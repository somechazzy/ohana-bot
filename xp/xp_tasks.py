import asyncio
import copy
import time
import traceback
from datetime import datetime

from globals_ import variables
from globals_.clients import firebase_client, discord_client
from globals_.constants import GUILDS_XP_SYNC_FREQUENCY_SECONDS, BotLogType, XPSettingsKey
from internal.bot_logging import log
from models.guild import GuildXP
from xp.xp import modify_member_level_roles


async def periodic_guilds_xp_sync():
    next_sync = int(datetime.utcnow().timestamp()) + GUILDS_XP_SYNC_FREQUENCY_SECONDS
    errors_occurred = []
    while True:
        sleep_duration = next_sync - int(datetime.utcnow().timestamp())
        next_sync = int(datetime.utcnow().timestamp()) + GUILDS_XP_SYNC_FREQUENCY_SECONDS
        await asyncio.sleep(sleep_duration if sleep_duration > 0 else 1)
        iterations = 0
        for guild_id, guild_xp in variables.guilds_xp.items():
            guild_xp: GuildXP = copy.deepcopy(guild_xp)
            if not guild_xp.synced:
                try:
                    data = {}
                    for member_id, member_xp in guild_xp.members_xp.items():
                        if not member_xp.is_synced:
                            data[str(member_id)] = member_xp.stringify_values().__dict__
                            variables.guilds_xp[guild_id].members_xp[member_id].is_synced = True
                    await firebase_client.update_guild_xp(guild_id, data)
                    variables.guilds_xp[guild_id].set_synced(True)
                except Exception as e:
                    error_text = f"Error while syncing guilds XP: {e}\n{traceback.format_exc()}"
                    errors_occurred.append(error_text)
                    print(error_text)
                    if len(errors_occurred) > 5:
                        await log(f"Encountered >5 errors for guild XP syncing. Latest:\n{error_text}",
                                  level=BotLogType.BOT_ERROR, ping_me=True)
                finally:
                    iterations += 1
                    # sleep for a second after each 2 iterations to avoid rate-limiting
                    if not iterations % 2:
                        await asyncio.sleep(1)


async def queue_members_for_xp_decay():
    while True:
        list_of_queued_member_guild_ids = [f"{i['member_id']}_{i['guild_id']}" for i in variables.member_decay_queue]

        for guild_prefs in variables.guilds_prefs.values():
            if guild_prefs.xp_settings[XPSettingsKey.XP_DECAY_ENABLED]:
                guild = discord_client.get_guild(guild_prefs.guild_id)
                if not guild:
                    continue
                safe_period_seconds = guild_prefs.xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY] * 24 * 60 * 60
                if not safe_period_seconds >= 1:
                    continue

                current_time = int(time.time()) - time.altzone
                for member_id, member_xp in variables.guilds_xp[guild_prefs.guild_id].members_xp.items():
                    if guild_prefs.xp_settings[XPSettingsKey.IGNORED_ROLES]:
                        member = guild.get_member(member_id)
                        no_xp_user = False
                        if member:
                            for role in member.roles:
                                if role.id in guild_prefs.xp_settings[XPSettingsKey.IGNORED_ROLES]:
                                    no_xp_user = True
                                    break
                        if no_xp_user:
                            continue
                    if member_xp.last_message_ts > 0 and (current_time-member_xp.last_message_ts) > safe_period_seconds:

                        already_exists = f"{member_id}_{guild_prefs.guild_id}" in list_of_queued_member_guild_ids
                        if not already_exists:
                            variables.member_decay_queue.append({
                                "member_id": member_id,
                                "guild_id": guild_prefs.guild_id,
                                "next_decay_ts": member_xp.ts_of_last_decay + (24 * 60 * 60)
                            })

        variables.member_decay_queue.sort(key=lambda k: k['next_decay_ts'])
        await asyncio.sleep(60*60)


async def initiate_periodic_xp_decay():
    while True:
        if variables.member_decay_queue:
            variables.member_decay_queue.sort(key=lambda k: k['next_decay_ts'])
            current_time = int(time.time()) - time.altzone
            if variables.member_decay_queue[0]['next_decay_ts'] > current_time:
                to_sleep = variables.member_decay_queue[0]['next_decay_ts'] - current_time
                if to_sleep < 10*60:
                    await asyncio.sleep(to_sleep+1)
                else:
                    await asyncio.sleep(10*60)
                    continue

            member_id = variables.member_decay_queue[0]['member_id']
            guild_id = variables.member_decay_queue[0]['guild_id']

            xp_settings = variables.guilds_prefs[guild_id].xp_settings
            safe_period_secs = xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY] * 24 * 60 * 60
            latest_decay_ts = variables.guilds_xp[guild_id].members_xp[member_id].ts_of_last_decay

            if (current_time - variables.guilds_xp[guild_id].members_xp[member_id].last_message_ts) > safe_period_secs \
                    and current_time - latest_decay_ts > 24 * 60 * 60:
                decay_percentage = xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]
                current_xp = variables.guilds_xp[guild_id].members_xp[member_id].xp
                to_decay = int(current_xp * (decay_percentage/100))
                variables.guilds_xp[guild_id].members_xp[member_id].decay_xp(xp=to_decay)
                variables.guilds_xp[guild_id].members_xp[member_id].set_ts_of_last_decay(current_time)
                await readjust_level_and_roles_after_decay(member_id, guild_id, xp_settings)
                variables.guilds_xp[guild_id].set_synced(False)
            variables.member_decay_queue.pop(0)
        else:
            await asyncio.sleep(60)


async def readjust_level_and_roles_after_decay(member_id, guild_id, xp_settings):
    current_xp = variables.guilds_xp[guild_id].members_xp[member_id].xp
    level_before = variables.guilds_xp[guild_id].members_xp[member_id].level
    level = 0
    for xp_requirement in variables.xp_level_map.keys():
        if current_xp >= xp_requirement:
            level = variables.xp_level_map[xp_requirement]
        else:
            break
    variables.guilds_xp[guild_id].members_xp[member_id].set_level(level)

    if level != level_before:
        guild = discord_client.get_guild(guild_id)
        if guild:
            member = guild.get_member(member_id)
            if member:
                await modify_member_level_roles(member=member, member_level=level, xp_settings=xp_settings,
                                                reason="Level roles readjustment (after decaying)")
