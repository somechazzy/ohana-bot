import asyncio
from collections import defaultdict
from datetime import datetime, UTC, timedelta

import discord

import cache
from bot.utils.helpers.xp_helpers import get_user_username_for_xp
from common.app_logger import AppLogger
from common.decorators import periodic_worker, require_db_session
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from components.guild_user_xp_components.guild_user_xp_component import GuildUserXPComponent
from components.guild_user_xp_components.xp_processing_component import XPProcessingComponent
from constants import BackgroundWorker
from models.dto.xp import XPAction, XPDecayItem


class XPService:
    """
    Service to host the XP workers and manage all XP processing.
    Any xp changes need to go through here to ensure proper locking.
    """
    _instance: 'XPService' = None

    def __init__(self):
        super().__init__()
        self.xp_processing_component = XPProcessingComponent()
        self.guild_user_xp_component = GuildUserXPComponent()
        self.guild_settings_component = GuildSettingsComponent()

        self._message_queue: asyncio.Queue[discord.Message] = asyncio.Queue()
        self._action_queue: asyncio.Queue = asyncio.Queue()
        self._decay_queue: asyncio.Queue = asyncio.PriorityQueue()

        self._guild_members_pending_decay: set[tuple[int, int]] = set()

        # Map of (guild_id, member_id) to asyncio.Lock to prevent concurrent XP processing for the same member
        self._member_lock_map: dict[tuple[int, int], asyncio.Lock] = defaultdict(asyncio.Lock)
        self._global_xp_lock = asyncio.Lock()

        self.logger = AppLogger(self.__class__.__name__)

    def __new__(cls, *args, **kwargs) -> 'XPService':
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def add_message_to_queue(self, message: discord.Message):
        """
        Add a message to the queue for processing.
        Args:
            message (discord.Message): The message to add to the queue.
        """
        await self._message_queue.put(message)

    async def add_xp_action(self,
                            guild_id: int,
                            user_id: int,
                            user_username: str,
                            xp_offset: int = 0,
                            reset: bool = False):
        """
        Add an XP action to the queue for processing.
        Args:
            guild_id (int): The guild ID related.
            user_id (int): The user ID to apply the XP action to.
            user_username (str): The user's username at the time of the action.
            xp_offset (int): The amount of XP to add or subtract.
            reset (bool): Whether to reset the user's XP. Overrides xp_offset if True.
        """
        xp_action = XPAction(
            guild_id=guild_id,
            member_id=user_id,
            username=user_username,
            xp_offset=xp_offset,
            reset=reset
        )
        await self._action_queue.put(xp_action)

    @require_db_session
    @periodic_worker(name=BackgroundWorker.XP_MESSAGE_QUEUE_CONSUMER)
    async def message_consumer(self):
        """
        Consume messages from the queue and process them for XP.
        """
        while not self._message_queue.empty():
            message = await self._message_queue.get()

            guild_settings = await self.guild_settings_component.get_guild_settings(message.guild.id)
            if not guild_settings.xp_settings.xp_gain_enabled or \
                    message.channel.id in guild_settings.xp_settings.ignored_channel_ids or \
                    guild_settings.xp_settings.ignored_role_ids.intersection({role.id for role
                                                                              in message.author.roles}):
                self._message_queue.task_done()
                continue

            if self._member_lock_map[(message.guild.id, message.author.id)].locked():
                self._message_queue.task_done()  # member being processed by another worker, get back to it later
                await self._message_queue.put(message)
                continue

            async with self._global_xp_lock:
                async with self._member_lock_map[(message.guild.id, message.author.id)]:
                    level_updated = await self.xp_processing_component.on_user_message(
                        user_id=message.author.id,
                        guild_id=message.guild.id,
                        message_time=message.created_at,
                        user_username=get_user_username_for_xp(message.author),
                        is_booster=message.author.premium_since is not None,
                    )
                    if level_updated:
                        await self.handle_roles_and_level_up_message_on_level_update(
                            guild_id=message.guild.id,
                            user_id=message.author.id,
                            level_change_reason="XP - level up from message",
                            channel_id=message.channel.id,
                        )

            self._message_queue.task_done()

    @require_db_session
    @periodic_worker(name=BackgroundWorker.XP_ACTION_QUEUE_CONSUMER)
    async def xp_action_consumer(self):
        """
        Consume XP actions from the queue and process them.
        """
        while not self._action_queue.empty():
            xp_action: XPAction = await self._action_queue.get()
            async with self._global_xp_lock:
                async with self._member_lock_map[(xp_action.guild_id, xp_action.member_id)]:
                    level_updated = await self.xp_processing_component.on_user_xp_action(xp_action=xp_action)
                    if level_updated:
                        await self.handle_roles_and_level_up_message_on_level_update(
                            guild_id=xp_action.guild_id,
                            user_id=xp_action.member_id,
                            level_change_reason="XP update from direct XP action",
                        )
            self._action_queue.task_done()

    @require_db_session
    @periodic_worker(name=BackgroundWorker.XP_DECAY_QUEUE_PRODUCER)
    async def decay_producer(self):
        """
        Produce XP decay items for members eligible for decay and add them to the decay queue.
        """
        await self.guild_user_xp_component.fetch_guild_xp_for_decay_eligible_guilds()

        guild_ids = list(cache.CACHED_GUILD_XP.keys())
        for guild_id in guild_ids:
            cached_guild_xp = cache.CACHED_GUILD_XP[guild_id]
            guild_settings = await self.guild_settings_component.get_guild_settings(guild_id)
            if guild_settings.xp_settings.xp_decay_enabled:
                decay_grace_days = guild_settings.xp_settings.xp_decay_grace_period_days
                decay_cutoff = datetime.now(UTC) - timedelta(days=decay_grace_days)
                for member_xp in cached_guild_xp.get_xps_with_last_message_time_before(decay_cutoff):
                    if (guild_id, member_xp.user_id) in self._guild_members_pending_decay:
                        continue
                    if member_xp.latest_decay_time:
                        next_decay = member_xp.latest_decay_time + timedelta(days=1)
                    else:
                        next_decay = member_xp.latest_message_time + timedelta(days=decay_grace_days)
                    self.logger.debug(f"Queuing user {member_xp.user_username} for XP decay in guild {guild_id}")
                    await self._decay_queue.put(XPDecayItem(
                        guild_id=guild_id,
                        member_id=member_xp.user_id,
                        username=member_xp.user_username,
                        next_decay=next_decay
                    ))
                    async with self._member_lock_map[(guild_id, member_xp.user_id)]:
                        self._guild_members_pending_decay.add((guild_id, member_xp.user_id))

    @require_db_session
    @periodic_worker(name=BackgroundWorker.XP_DECAY_QUEUE_CONSUMER, initial_delay=30)
    async def decay_consumer(self):
        """
        Consume XP decay items from the decay queue and process them.
        """
        while not self._decay_queue.empty():
            if (decay_item := await self._decay_queue.get()).next_decay <= datetime.now(UTC):
                self.logger.debug(f"Processing XP decay for user {decay_item.username} in guild {decay_item.guild_id}")
                async with self._global_xp_lock:
                    async with self._member_lock_map[(decay_item.guild_id, decay_item.member_id)]:
                        level_updated = await self.xp_processing_component.process_user_xp_decay(decay_item=decay_item)
                        if level_updated:
                            await self.handle_roles_and_level_up_message_on_level_update(
                                guild_id=decay_item.guild_id,
                                user_id=decay_item.member_id,
                                level_change_reason="Level adjustment from XP decay",
                            )
                self._decay_queue.task_done()
            else:
                self._decay_queue.task_done()
                await self._decay_queue.put(decay_item)
                break

    @require_db_session
    @periodic_worker(name=BackgroundWorker.XP_DB_SYNC)
    async def xp_sync_to_database(self):
        """
        Periodically sync the cached XP data back to the database.
        """
        async with self._global_xp_lock:
            await self.guild_user_xp_component.sync_up_guild_user_xp()

    @staticmethod
    async def handle_roles_and_level_up_message_on_level_update(guild_id: int, user_id: int,
                                                                level_change_reason: str, channel_id: int = None):
        """
        Handle roles and level up message on level update.
        Args:
            guild_id (int): The guild ID.
            user_id (int): The user ID.
            level_change_reason (str): The reason for the level change.
            channel_id (int | None): The channel ID to send the level up message to (from message events).
        """
        from bot.utils.bot_actions.xp_actions import handle_roles_and_level_up_message_on_level_update
        await handle_roles_and_level_up_message_on_level_update(
            guild_id=guild_id,
            user_id=user_id,
            level_change_reason=level_change_reason,
            channel_id=channel_id
        )
