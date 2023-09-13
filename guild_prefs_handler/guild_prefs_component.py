import asyncio
import copy
from globals_.clients import discord_client
from internal.bot_logger import InfoLogger
from models.guild import GuildPrefs
from globals_ import shared_memory
from globals_.constants import XPSettingsKey, DEFAULT_TIMEFRAME_FOR_XP, DEFAULT_MIN_XP_GIVEN, \
    DEFAULT_MAX_XP_GIVEN, DEFAULT_XP_DECAY_DAYS, DEFAULT_XP_DECAY_PERCENTAGE, BotLogLevel
from utils.helpers import dict_to_guild_prefs_object, encrypt_guild_prefs_keys, stringify_xp_settings_values
from .guild_prefs_repo import GuildPrefsRepo


class GuildPrefsComponent:

    def __init__(self):
        self.repo = GuildPrefsRepo()
        self.info_logger = InfoLogger(component=self.__class__.__name__)

    async def get_guild_prefs(self, guild) -> GuildPrefs:
        guild_prefs = shared_memory.guilds_prefs.get(int(guild.id))
        if not guild_prefs:
            await self.make_default_guild_prefs(guild)
            guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        return guild_prefs

    async def make_default_guild_prefs(self, guild):
        guild_prefs = GuildPrefs(guild.id, guild.name)
        if guild.id not in shared_memory.guilds_prefs.keys():
            success = await self.ensure_if_guild_prefs_exist(guild.id)
            if success:
                return False  # Guild prefs already exist
            shared_memory.guilds_prefs[guild.id] = guild_prefs
            await self.update_guild_in_db(guild)
            return True  # Guild prefs were created
        return False  # Guild prefs already exist

    async def ensure_if_guild_prefs_exist(self, guild_id):
        res = (await self.repo.get_guild(guild_id)).val()
        if res is None:
            return False
        gp_object = dict_to_guild_prefs_object(res)
        shared_memory.guilds_prefs[guild_id] = gp_object.destringify_values()
        return True

    async def set_guild_name(self, guild, new_name):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.set_guild_name(new_name)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_name', new_name)

    async def set_guild_logs_channel(self, guild, channel_id):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.set_logs_channel(channel_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_logs_channel', str(channel_id))

    async def set_guild_music_channel(self, guild, channel_id):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.set_music_channel(channel_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_music_channel', str(channel_id))

    async def set_guild_music_header_message(self, guild, message_id):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.set_music_header_message(message_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_music_header_message', str(message_id))

    async def set_guild_music_player_message(self, guild, message_id):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.set_music_player_message(message_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_music_player_message', str(message_id))

    async def set_guild_music_player_message_timestamp(self, guild, timestamp):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.set_music_player_message_timestamp(timestamp)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_music_player_message_timestamp', str(timestamp))

    async def add_guild_autorole(self, guild, role_id):
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.add_autorole(role_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        autoroles = list(map(str, guild_prefs.autoroles.copy()))
        await self.repo.update_guild_attribute(guild.id, '_autoroles', autoroles)

    async def remove_guild_autorole(self, guild, role_id):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.remove_autorole(role_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        autoroles = list(map(str, guild_prefs.autoroles.copy()))
        await self.repo.update_guild_attribute(guild.id, '_autoroles', autoroles)

    async def clear_guild_autoroles(self, guild):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.autoroles.clear()
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        autoroles = list(map(str, guild_prefs.autoroles.copy()))
        await self.repo.update_guild_attribute(guild.id, '_autoroles', autoroles)

    async def add_guild_dj_role(self, guild, role_id):
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.add_dj_role(role_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        dj_roles = list(map(str, guild_prefs.dj_roles.copy()))
        await self.repo.update_guild_attribute(guild.id, '_dj_roles', dj_roles)

    async def remove_guild_dj_role(self, guild, role_id):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.remove_dj_role(role_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        dj_roles = list(map(str, guild_prefs.dj_roles.copy()))
        await self.repo.update_guild_attribute(guild.id, '_dj_roles', dj_roles)

    async def clear_guild_dj_roles(self, guild):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.dj_roles.clear()
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        dj_roles = list(map(str, guild_prefs.dj_roles.copy()))
        await self.repo.update_guild_attribute(guild.id, '_dj_roles', dj_roles)

    async def add_guild_single_message_channel(self, guild, channel_id, role_id, mode):
        single_message_channel_dict = {
            "channel_id": int(channel_id),
            "role_id": int(role_id),
            "mode": str(mode)
        }
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.add_single_message_channel(channel_id, single_message_channel_dict)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        single_message_channel_dict = {
            "channel_id": str(channel_id),
            "role_id": str(role_id),
            "mode": str(mode)
        }
        await self.repo.update_second_level_guild_attribute(guild.id, '_single_message_channels',
                                                            channel_id, single_message_channel_dict)

    async def remove_guild_single_message_channel(self, guild, channel_id):
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.remove_single_message_channel(channel_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_second_level_guild_attribute(guild.id, '_single_message_channels',
                                                            channel_id, {})

    async def clear_guild_single_message_channels(self, guild):
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.single_message_channels.clear()
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_single_message_channels', {})

    async def add_guild_gallery_channel(self, guild, channel_id):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.add_gallery_channel(str(channel_id))
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        gallery_channels = list(map(str, guild_prefs.gallery_channels.copy()))
        await self.repo.update_guild_attribute(guild.id, '_gallery_channels', gallery_channels)

    async def remove_guild_gallery_channel(self, guild, channel_id):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.remove_gallery_channel(channel_id)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        gallery_channels = list(map(str, guild_prefs.gallery_channels.copy()))
        await self.repo.update_guild_attribute(guild.id, '_gallery_channels', gallery_channels)

    async def clear_guild_gallery_channels(self, guild):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.gallery_channels.clear()
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        gallery_channels = list(map(str, guild_prefs.gallery_channels.copy()))
        await self.repo.update_guild_attribute(guild.id, '_gallery_channels', gallery_channels)

    async def set_role_persistence_enabled_state(self, guild, state: bool):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.set_role_persistence_enabled(state)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_role_persistence_enabled', state)

    async def set_xp_setting(self, guild, setting, value, guild_id=None):
        if guild is not None:
            guild_id = guild.id
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild_id)

        if setting in [XPSettingsKey.XP_GAIN_TIMEFRAME, XPSettingsKey.XP_GAIN_MIN, XPSettingsKey.XP_GAIN_MAX]:
            guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_ENABLED] = True
        if setting in [XPSettingsKey.LEVELUP_MESSAGE, XPSettingsKey.LEVELUP_CHANNEL,
                       XPSettingsKey.LEVEL_ROLES, XPSettingsKey.LEVEL_ROLE_EARN_MESSAGE]:
            guild_prefs.xp_settings[XPSettingsKey.LEVELUP_ENABLED] = True
        if setting in [XPSettingsKey.DAYS_BEFORE_XP_DECAY, XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]:
            guild_prefs.xp_settings[XPSettingsKey.XP_DECAY_ENABLED] = True

        guild_prefs.xp_settings[setting] = value

        shared_memory.guilds_prefs[guild_id] = guild_prefs
        stringified_xp_settings = stringify_xp_settings_values(copy.deepcopy(guild_prefs.xp_settings))
        await self.repo.update_guild_attribute(guild_id, '_xp_settings', stringified_xp_settings)

    async def set_xp_settings(self, guild, settings):
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.set_xp_settings(settings)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        stringified_xp_settings = stringify_xp_settings_values(copy.deepcopy(guild_prefs.xp_settings))
        await self.repo.update_guild_attribute(guild.id, '_xp_settings', stringified_xp_settings)

    async def reset_xp_gain_settings(self, guild):
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_ENABLED] = True
        guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME] = DEFAULT_TIMEFRAME_FOR_XP
        guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_MIN] = DEFAULT_MIN_XP_GIVEN
        guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_MAX] = DEFAULT_MAX_XP_GIVEN
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        stringified_xp_settings = stringify_xp_settings_values(copy.deepcopy(guild_prefs.xp_settings))
        await self.repo.update_guild_attribute(guild.id, '_xp_settings', stringified_xp_settings)

    async def reset_xp_decay_settings(self, guild):
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY] = DEFAULT_XP_DECAY_PERCENTAGE
        guild_prefs.xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY] = DEFAULT_XP_DECAY_DAYS
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        stringified_xp_settings = stringify_xp_settings_values(copy.deepcopy(guild_prefs.xp_settings))
        await self.repo.update_guild_attribute(guild.id, '_xp_settings', stringified_xp_settings)

    async def update_role_menu_config(self, guild, message_id, role_menu_type, role_menu_mode, restricted_to_roles,
                                      restricted_description):
        guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs.add_role_menu(message_id, role_menu_type, role_menu_mode, restricted_to_roles,
                                  restricted_description)
        shared_memory.guilds_prefs[guild.id] = guild_prefs
        role_menu_data = copy.deepcopy(guild_prefs.role_menus[message_id])
        role_menu_data['restricted_to_roles'] = [str(role_id) for role_id in role_menu_data['restricted_to_roles']]
        await self.repo.update_second_level_guild_attribute(guild.id, '_role_menus', message_id, role_menu_data)

    async def refresh_guilds_info(self):
        client = discord_client

        for guild in client.guilds:  # for adding guilds that were joined while offline
            if guild.id not in shared_memory.guilds_prefs.keys():
                is_new = await self.make_default_guild_prefs(guild)
                if is_new:
                    self.info_logger.log(f"ADDED NEW GUILD ON LAUNCH DURING REFRESH: ID={guild.id}. NAME='{guild}'",
                                         level=BotLogLevel.GUILD_JOIN, guild_id=guild.id)

        for guild_prefs in shared_memory.guilds_prefs.values():  # for refreshing guilds names
            if guild := client.get_guild(guild_prefs.guild_id):
                if guild_prefs.guild_name != guild.name:
                    asyncio.get_event_loop().create_task(self.set_guild_name(guild=guild, new_name=guild.name))

    async def update_guild_in_db(self, guild):
        guild_prefs = shared_memory.guilds_prefs.get(guild.id)
        guild_prefs_enc_keys = encrypt_guild_prefs_keys(copy.deepcopy(guild_prefs))
        guild_prefs_stringified_values = guild_prefs_enc_keys.stringify_values()
        await self.repo.add_guild(guild_prefs_stringified_values)
