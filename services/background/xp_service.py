import asyncio
import traceback
from collections import defaultdict
from datetime import datetime

import discord

from globals_ import shared_memory
from globals_.constants import BackgroundWorker, XPSettingsKey
from internal.bot_logger import ErrorLogger
from utils.decorators import periodic_worker

member_lock = asyncio.Lock()
sync_status_lock = asyncio.Lock()
member_decay_lock = asyncio.Lock()


class XPService:
    """
    This service is responsible for handling XP changes/actions for members - with DB synchronization.
    5 workers:
    1. XP Gain from messages
    2. XP Adjustment from admin commands
    3+4. XP Decay enqueue & consume
    5. XP Sync to DB

    We use locks to prevent workers from operating on the same member at the same time.
    We could also use locks to prevent conflicting role handling but really what are the chances + roles
        will resolve themselves on the next level role check.
    """

    def __init__(self):
        from globals_.clients import firebase_client, discord_client
        from components.xp_components.xp_handler_component import XPHandlerComponent
        self.xp_handler_component = XPHandlerComponent()
        self.firebase_client = firebase_client
        self.discord_client = discord_client
        self._error_logger = ErrorLogger(component=self.__class__.__name__)

        self._guild_id_member_id_out_of_sync_map = defaultdict(dict)
        self._guild_id_member_id_pending_xp_update_count_map = defaultdict(int)

        self._xp_message_queue = asyncio.Queue()

        self._xp_action_queue = asyncio.Queue()

        self._xp_decay_queue = asyncio.PriorityQueue()
        self._guild_members_pending_decay = set()

    async def _set_out_of_sync(self, guild_id: int, member_id: int):
        async with sync_status_lock:
            self._guild_id_member_id_out_of_sync_map[guild_id][member_id] = True

    async def _get_and_clear_out_of_sync_map(self):
        async with sync_status_lock:
            guild_id_member_id_out_of_sync_map = self._guild_id_member_id_out_of_sync_map.copy()
            self._guild_id_member_id_out_of_sync_map = defaultdict(dict)
            return guild_id_member_id_out_of_sync_map

    def _is_member_pending_xp_update(self, guild_id, user_id):
        return (guild_id, user_id) in self._guild_id_member_id_pending_xp_update_count_map and \
            self._guild_id_member_id_pending_xp_update_count_map[(guild_id, user_id)] > 0

    async def _lock_member_for_xp_update(self, guild_id, user_id):
        async with member_lock:
            self._guild_id_member_id_pending_xp_update_count_map[(guild_id, user_id)] += 1

    async def _unlock_member_for_xp_update(self, guild_id, user_id):
        async with member_lock:
            self._guild_id_member_id_pending_xp_update_count_map[(guild_id, user_id)] -= 1
            if self._guild_id_member_id_pending_xp_update_count_map[(guild_id, user_id)] <= 0:
                self._guild_id_member_id_pending_xp_update_count_map.pop((guild_id, user_id))

    # message handling
    async def add_message_to_handle(self, message: discord.Message):
        """
        Adds a message to the queue to be handled by the XP Gain worker.
        :param message: The message to handle.
        """
        await self._xp_message_queue.put(message)

    @periodic_worker(name=BackgroundWorker.XP_GAIN)
    async def xp_gain(self):
        while not self._xp_message_queue.empty():
            message = await self._xp_message_queue.get()

            if self._is_member_pending_xp_update(guild_id=message.guild.id, user_id=message.author.id):
                self._xp_message_queue.task_done()
                await self._xp_message_queue.put(message)
                continue

            await self._lock_member_for_xp_update(guild_id=message.guild.id, user_id=message.author.id)

            try:
                xp_updated = await self.xp_handler_component.handle_xp_gain(message=message)
                if xp_updated:
                    await self._set_out_of_sync(guild_id=message.guild.id, member_id=message.author.id)
            except Exception as e:
                self._error_logger.log(f"Error handling XP gain for message from user {message.author.id} in guild "
                                       f"{message.guild.id}: {e}, {traceback.format_exc()}", extras=self._debug_extras)
            await self._unlock_member_for_xp_update(guild_id=message.guild.id, user_id=message.author.id)

            self._xp_message_queue.task_done()

    # xp action handling
    async def add_xp_action(self, guild_id: int, member_id: int, xp_offset: int = None, reset: bool = False):
        """
        Adds an XP action to the queue.
        :param guild_id: The ID of the guild the action took place in.
        :param member_id: The ID of the member the action took place on.
        :param xp_offset: The XP change (positive or negative offset).
        :param reset: Whether to reset the XP to 0.
        """
        if not xp_offset and not reset:
            return

        xp_action = XPAction(guild_id=guild_id, member_id=member_id, xp_offset=xp_offset, reset=reset)
        await self._xp_action_queue.put(xp_action)

    @periodic_worker(name=BackgroundWorker.XP_ADJUSTMENT)
    async def xp_adjustment(self):
        while not self._xp_action_queue.empty():
            xp_action = await self._xp_action_queue.get()
            await self.perform_xp_action(xp_action=xp_action)

    async def perform_xp_action(self, xp_action):
        while self._is_member_pending_xp_update(guild_id=xp_action.guild_id, user_id=xp_action.member_id):
            await asyncio.sleep(0.1)

        await self._lock_member_for_xp_update(guild_id=xp_action.guild_id, user_id=xp_action.member_id)

        try:
            member = self.discord_client.get_guild(xp_action.guild_id).get_member(xp_action.member_id)
            if member:
                self.xp_handler_component.edit_member_xp(member=member, offset=xp_action.xp_offset,
                                                         reset=xp_action.reset)
            else:
                self.xp_handler_component.edit_user_xp(user_id=xp_action.member_id, guild_id=xp_action.guild_id,
                                                       offset=xp_action.xp_offset, reset=xp_action.reset)

            await self._set_out_of_sync(guild_id=xp_action.guild_id, member_id=xp_action.member_id)
        except Exception as e:
            self._error_logger.log(f"Error handling XP action for user {xp_action.member_id} in guild "
                                   f"{xp_action.guild_id}: {e}, {traceback.format_exc()}",
                                   extras=self._debug_extras | locals())

        await self._unlock_member_for_xp_update(guild_id=xp_action.guild_id, user_id=xp_action.member_id)

    # decay handling
    async def set_guild_member_as_pending_decay(self, guild_id: int, member_id: int):
        async with member_decay_lock:
            self._guild_members_pending_decay.add((guild_id, member_id))

    async def unset_guild_member_as_pending_decay(self, guild_id: int, member_id: int):
        async with member_decay_lock:
            self._guild_members_pending_decay.remove((guild_id, member_id))

    @periodic_worker(name=BackgroundWorker.XP_DECAY_ENQUEUE)
    async def queue_members_for_xp_decay(self):
        for guild_prefs in shared_memory.guilds_prefs.values():

            if not guild_prefs.xp_settings[XPSettingsKey.XP_DECAY_ENABLED]:
                continue
            guild = self.discord_client.get_guild(guild_prefs.guild_id)
            if not guild:
                continue
            grace_period_seconds = guild_prefs.xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY] * 24 * 60 * 60
            if not grace_period_seconds >= 1:
                continue
            ignored_roles = guild_prefs.xp_settings[XPSettingsKey.IGNORED_ROLES]

            for member_id, member_xp in shared_memory.guilds_xp[guild_prefs.guild_id].members_xp.items():
                member = guild.get_member(member_id)
                if member and any(guild.get_role(role_id) in member.roles for role_id in ignored_roles):
                    continue
                if (guild.id, member_id) in self._guild_members_pending_decay:
                    continue

                if member_xp.last_message_ts > 0 and \
                        datetime.utcnow().timestamp() - member_xp.last_message_ts > grace_period_seconds:
                    await self._xp_decay_queue.put(
                        XPDecayItem(guild_id=guild.id,
                                    member_id=member_id,
                                    next_decay_ts=member_xp.ts_of_last_decay + (24 * 60 * 60))
                    )
                    await self.set_guild_member_as_pending_decay(guild_id=guild.id, member_id=member_id)

    @periodic_worker(name=BackgroundWorker.XP_DECAY)
    async def xp_decay(self):
        while not self._xp_decay_queue.empty():
            if (decay_item := await self._xp_decay_queue.get()).next_decay_ts <= datetime.utcnow().timestamp():
                await self.perform_xp_decay(decay_item=decay_item)
                self._xp_decay_queue.task_done()
            else:
                await self._xp_decay_queue.put(decay_item)
                break

    async def perform_xp_decay(self, decay_item):
        while self._is_member_pending_xp_update(guild_id=decay_item.guild_id, user_id=decay_item.member_id):
            await asyncio.sleep(1)

        await self._lock_member_for_xp_update(guild_id=decay_item.guild_id, user_id=decay_item.member_id)

        try:
            member_xp = shared_memory.guilds_xp[decay_item.guild_id].members_xp[decay_item.member_id]
            xp_settings = shared_memory.guilds_prefs[decay_item.guild_id].xp_settings

            grace_period_secs = xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY] * 24 * 60 * 60
            current_timestamp = datetime.utcnow().timestamp()

            if (current_timestamp - member_xp.last_message_ts) > grace_period_secs \
                    and (current_timestamp - member_xp.ts_of_last_decay) >= 24 * 60 * 60:
                decay_percentage = xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]
                current_xp = member_xp.xp
                to_decay = int(current_xp * (decay_percentage / 100))
                member_xp.decay_xp(xp=to_decay)
                member_xp.set_ts_of_last_decay(current_timestamp)
                asyncio.get_event_loop().create_task(
                    self.xp_handler_component.readjust_level_and_roles_after_decay(guild_id=decay_item.guild_id,
                                                                                   member_id=decay_item.member_id)
                )
                await self._set_out_of_sync(guild_id=decay_item.guild_id, member_id=decay_item.member_id)

        except Exception as e:
            self._error_logger.log(f"Error performing XP decay for user {decay_item.member_id} in guild "
                                   f"{decay_item.guild_id}: {e}, {traceback.format_exc()}",
                                   extras=self._debug_extras | locals())

        await self.unset_guild_member_as_pending_decay(guild_id=decay_item.guild_id, member_id=decay_item.member_id)
        await self._unlock_member_for_xp_update(guild_id=decay_item.guild_id, user_id=decay_item.member_id)

    @periodic_worker(name=BackgroundWorker.XP_SYNC)
    async def xp_sync(self):
        guild_id_member_id_out_of_sync_map = await self._get_and_clear_out_of_sync_map()
        if not guild_id_member_id_out_of_sync_map:
            return
        update_data = {}

        for guild_id, member_id_out_of_sync_map in guild_id_member_id_out_of_sync_map.items():
            for member_id, _ in member_id_out_of_sync_map.items():
                member_xp = shared_memory.guilds_xp[guild_id].members_xp[member_id]
                update_data[f"{guild_id}/{member_id}"] = member_xp.stringify_values().__dict__

        try:
            await self.firebase_client.update_guilds_xp(data=update_data)
        except Exception as e:
            self._error_logger.log(f"Error syncing XP: {e}, {traceback.format_exc()}",
                                   extras=self._debug_extras | locals())
            for guild_id, member_id_out_of_sync_map in guild_id_member_id_out_of_sync_map.items():
                for member_id, _ in member_id_out_of_sync_map.items():
                    await self._set_out_of_sync(guild_id=guild_id, member_id=member_id)

    @property
    def _debug_extras(self) -> dict:
        return {
            "_xp_message_queue_len": self._xp_message_queue.qsize(),
            "_xp_decay_queue_len": self._xp_decay_queue.qsize(),
            "_xp_action_queue_len": self._xp_action_queue.qsize(),
            "member_lock_status": bool(member_lock.locked()),
            "member_decay_lock_status": bool(member_decay_lock.locked()),
            "sync_status_lock_status": bool(sync_status_lock.locked()),
        }


class XPAction:
    
    def __init__(self, guild_id: int = None, member_id: int = None, xp_offset: int = None, reset: bool = False):
        self.guild_id = guild_id
        self.member_id = member_id
        self.xp_offset = xp_offset
        self.reset = reset

    def __str__(self):
        return f"XPAction(guild_id={self.guild_id}, member_id={self.member_id}, xp_offset={self.xp_offset})"


class XPDecayItem:
    def __init__(self, guild_id: int = None, member_id: int = None, next_decay_ts: int = None):
        self.guild_id = guild_id
        self.member_id = member_id
        self.next_decay_ts = next_decay_ts

    def __lt__(self, other):
        return self.next_decay_ts < other.next_decay_ts

    def __gt__(self, other):
        return self.next_decay_ts > other.next_decay_ts

    def __str__(self):
        return f"XPDecayItem(guild_id={self.guild_id}, member_id={self.member_id}, next_decay_ts={self.next_decay_ts})"
