import copy
from internal.bot_logging import log
from globals_.clients import discord_client
from models.guild import GuildPrefs
from globals_ import variables
from globals_.constants import XPSettingsKey, AdminSettingsAction, DEFAULT_TIMEFRAME_FOR_XP, DEFAULT_MIN_XP_GIVEN, \
    DEFAULT_MAX_XP_GIVEN, DEFAULT_XP_DECAY_DAYS, DEFAULT_XP_DECAY_PERCENTAGE
from helpers import dict_to_guild_prefs_object, encrypt_guild_prefs_keys, stringify_xp_settings_values
from .guild_prefs_repo import GuildPrefsRepo


class GuildPrefsComponent:
    """
    Component for handling any and all changes to a guild's GuildPrefs object.
    It is very important to use this in order to ensure that the changes are synced with the database.
    """

    def __init__(self):
        self.repo = GuildPrefsRepo()

    async def get_guild_prefs(self, guild):
        guild_prefs = variables.guilds_prefs.get(int(guild.id))
        if not guild_prefs:
            await self.make_default_guild_prefs(guild)
            guild_prefs = variables.guilds_prefs.get(guild.id)
        return guild_prefs

    async def make_default_guild_prefs(self, guild):
        guild_prefs = GuildPrefs(guild.id, guild.name)
        if guild.id not in variables.guilds_prefs.keys():
            exists = await self.ensure_that_guild_prefs_exist(guild.id)
            if exists:
                return variables.guilds_prefs[guild.id]
            variables.guilds_prefs[guild.id] = guild_prefs
            await self.update_guild_in_db(guild)

    async def ensure_that_guild_prefs_exist(self, guild_id):
        res = (await self.repo.get_guild(guild_id)).val()
        if res is None:
            return False
        gp_object = dict_to_guild_prefs_object(res)
        variables.guilds_prefs[guild_id] = gp_object.destringify_values()
        return True

    async def set_guild_prefix(self, guild, new_prefix):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_prefix(new_prefix)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_prefix', new_prefix)

    async def set_guild_admin_prefix(self, guild, new_prefix):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_admin_prefix(new_prefix)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_admin_prefix', new_prefix)

    async def set_guild_music_prefix(self, guild, new_prefix):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_music_prefix(new_prefix)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_music_prefix', new_prefix)

    async def set_currently_in_guild(self, guild, state: bool):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_currently_in_guild(state)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_currently_in_guild', state)

    async def set_guild_logs_channel(self, guild, channel_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_logs_channel(channel_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_logs_channel', channel_id)

    async def set_guild_spam_channel(self, guild, channel_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_spam_channel(channel_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_spam_channel', channel_id)

    async def set_guild_music_channel(self, guild, channel_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_music_channel(channel_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_music_channel', channel_id)

    async def set_guild_music_header_message(self, guild, message_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_music_header_message(message_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_music_header_message', message_id)

    async def set_guild_music_player_message(self, guild, message_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_music_player_message(message_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_music_player_message', message_id)

    async def add_guild_anime_channel(self, guild, channel_id):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.add_anime_channel(channel_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_anime_channels', guild_prefs.anime_channels)

    async def remove_guild_anime_channel(self, guild, channel_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.remove_anime_channel(channel_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_anime_channels', guild_prefs.anime_channels)

    async def clear_guild_anime_channels(self, guild):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.anime_channels.clear()
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_anime_channels', guild_prefs.anime_channels)

    async def set_guild_fun_section_enabled_state(self, guild, state: bool):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_fun_commands_enabled(state)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_fun_commands_enabled', state)

    async def set_guild_utility_section_enabled_state(self, guild, state: bool):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_utility_commands_enabled(state)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_utility_commands_enabled', state)

    async def set_guild_moderation_section_enabled_state(self, guild, state: bool):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_moderation_commands_enabled(state)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_moderation_commands_enabled', state)

    async def set_guild_anime_and_manga_section_enabled_state(self, guild, state: bool):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_mal_al_commands_enabled(state)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_mal_al_commands_enabled', state)

    async def set_guild_xp_section_enabled_state(self, guild, state: bool, guild_id=None):
        guild_prefs = variables.guilds_prefs.get(guild.id if not guild_id else guild_id)
        guild_prefs.set_xp_commands_enabled(state)
        variables.guilds_prefs[guild.id if not guild_id else guild_id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id if not guild_id else guild_id, '_xp_commands_enabled', state)

    async def add_guild_autorole(self, guild, role_id):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.add_autorole(role_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_autoroles', guild_prefs.autoroles)

    async def remove_guild_autorole(self, guild, role_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.remove_autorole(role_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_autoroles', guild_prefs.autoroles)

    async def clear_guild_autoroles(self, guild):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.autoroles.clear()
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_autoroles', guild_prefs.autoroles)

    async def add_guild_dj_role(self, guild, role_id):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.add_dj_role(role_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_dj_roles', guild_prefs.dj_roles)

    async def remove_guild_dj_role(self, guild, role_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.remove_dj_role(role_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_dj_roles', guild_prefs.dj_roles)

    async def clear_guild_dj_roles(self, guild):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.dj_roles.clear()
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_dj_roles', guild_prefs.dj_roles)

    async def add_guild_auto_response(self, guild, trigger, response, delete, match_type):
        if guild.id in variables.auto_responses_cache.keys():
            variables.auto_responses_cache[guild.id]["valid"] = False
        auto_response_dict = {
            "response": response,
            "match": match_type,
            "delete": delete
        }
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.add_auto_response(trigger, auto_response_dict)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_second_level_guild_attribute(guild.id, '_auto_responses', trigger, auto_response_dict)

    async def remove_guild_auto_response(self, guild, trigger):
        if guild.id in variables.auto_responses_cache.keys():
            variables.auto_responses_cache[guild.id]["valid"] = False
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.remove_auto_response(trigger)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_second_level_guild_attribute(guild.id, '_auto_responses', trigger, {})

    async def clear_guild_auto_responses(self, guild):
        if guild.id in variables.auto_responses_cache.keys():
            variables.auto_responses_cache[guild.id]["valid"] = False
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.auto_responses.clear()
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_auto_responses', {})

    async def add_guild_banned_word(self, guild, word, regex, warn, match_type):
        if guild.id in variables.banned_words_cache.keys():
            variables.banned_words_cache[guild.id]["valid"] = False
        banned_word_dict = {
            "regex": regex,
            "match": match_type,
            "warn": warn
        }
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.add_banned_word(word, banned_word_dict)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_second_level_guild_attribute(guild.id, '_banned_words', word, banned_word_dict)

    async def remove_guild_banned_word(self, guild, word):
        if guild.id in variables.banned_words_cache.keys():
            variables.banned_words_cache[guild.id]["valid"] = False
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.remove_banned_word(word)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_second_level_guild_attribute(guild.id, '_banned_words', word, {})

    async def clear_guild_banned_words(self, guild):
        if guild.id in variables.banned_words_cache.keys():
            variables.banned_words_cache[guild.id]["valid"] = False
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.banned_words.clear()
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_banned_words', {})

    async def add_guild_single_message_channel(self, guild, channel_id, role_id, mode):
        single_message_channel_dict = {
            "channel_id": int(channel_id),
            "role_id": int(role_id),
            "mode": str(mode)
        }
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.add_single_message_channel(channel_id, single_message_channel_dict)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_second_level_guild_attribute(guild.id, '_single_message_channels',
                                                            channel_id, single_message_channel_dict)

    async def remove_guild_single_message_channel(self, guild, channel_id):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.remove_single_message_channel(channel_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_second_level_guild_attribute(guild.id, '_single_message_channels',
                                                            channel_id, {})

    async def clear_guild_single_message_channels(self, guild):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.single_message_channels.clear()
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_single_message_channels', {})

    async def add_guild_react_role(self, guild, channel_id, message_id, emoji_id, role_id):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.add_react_role(channel_id, message_id, emoji_id, role_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_fourth_level_guild_attribute(guild.id, '_react_roles',
                                                            channel_id, message_id, emoji_id, role_id)

    async def remove_guild_react_role(self, guild, channel_id, message_id, emoji_id):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.remove_react_role(channel_id, message_id, emoji_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_fourth_level_guild_attribute(guild.id, '_react_roles',
                                                            channel_id, message_id, emoji_id, None)

    async def clear_guild_react_roles(self, guild):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.react_roles.clear()
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_react_roles', {})

    async def add_guild_gallery_channel(self, guild, channel_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.add_gallery_channel(str(channel_id))
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_gallery_channels', guild_prefs.gallery_channels)

    async def remove_guild_gallery_channel(self, guild, channel_id):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.remove_gallery_channel(channel_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_gallery_channels', guild_prefs.gallery_channels)

    async def clear_guild_gallery_channels(self, guild):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.gallery_channels.clear()
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_gallery_channels', guild_prefs.gallery_channels)

    async def set_whitelisted_role(self, guild, role_id):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_whitelisted_role(role_id)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_whitelisted_role', role_id)

    async def set_role_persistence_enabled_state(self, guild, state: bool):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.set_role_persistence_enabled(state)
        variables.guilds_prefs[guild.id] = guild_prefs
        await self.repo.update_guild_attribute(guild.id, '_role_persistence_enabled', state)

    async def set_xp_setting(self, guild, setting, value, action=None, guild_id=None):
        if guild is not None:
            guild_id = guild.id
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild_id)

        if setting in [XPSettingsKey.IGNORED_CHANNELS, XPSettingsKey.IGNORED_ROLES]:
            if action == AdminSettingsAction.ADD:
                guild_prefs.xp_settings[setting].append(value)
            elif action == AdminSettingsAction.REMOVE:
                while value in guild_prefs.xp_settings[setting]:
                    guild_prefs.xp_settings[setting].remove(value)
            elif action == AdminSettingsAction.CLEAR:
                guild_prefs.xp_settings[setting].clear()
        else:
            if setting in [XPSettingsKey.XP_GAIN_TIMEFRAME, XPSettingsKey.XP_GAIN_MIN, XPSettingsKey.XP_GAIN_MAX]:
                guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_ENABLED] = True
            if setting in [XPSettingsKey.LEVELUP_MESSAGE, XPSettingsKey.LEVELUP_CHANNEL,
                           XPSettingsKey.LEVEL_ROLES, XPSettingsKey.LEVEL_ROLE_EARN_MESSAGE]:
                guild_prefs.xp_settings[XPSettingsKey.LEVELUP_ENABLED] = True
            if setting in [XPSettingsKey.DAYS_BEFORE_XP_DECAY, XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]:
                guild_prefs.xp_settings[XPSettingsKey.XP_DECAY_ENABLED] = True
            guild_prefs.xp_settings[setting] = value

        variables.guilds_prefs[guild_id] = guild_prefs
        stringified_xp_settings = stringify_xp_settings_values(copy.deepcopy(guild_prefs.xp_settings))
        await self.repo.update_guild_attribute(guild_id, '_xp_settings', stringified_xp_settings)

    async def reset_xp_gain_settings(self, guild):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_ENABLED] = True
        guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME] = DEFAULT_TIMEFRAME_FOR_XP
        guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_MIN] = DEFAULT_MIN_XP_GIVEN
        guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_MAX] = DEFAULT_MAX_XP_GIVEN
        variables.guilds_prefs[guild.id] = guild_prefs
        stringified_xp_settings = stringify_xp_settings_values(copy.deepcopy(guild_prefs.xp_settings))
        await self.repo.update_guild_attribute(guild.id, '_xp_settings', stringified_xp_settings)

    async def reset_xp_decay_settings(self, guild):
        guild_prefs: GuildPrefs = variables.guilds_prefs.get(guild.id)
        guild_prefs.xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY] = DEFAULT_XP_DECAY_PERCENTAGE
        guild_prefs.xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY] = DEFAULT_XP_DECAY_DAYS
        variables.guilds_prefs[guild.id] = guild_prefs
        stringified_xp_settings = stringify_xp_settings_values(copy.deepcopy(guild_prefs.xp_settings))
        await self.repo.update_guild_attribute(guild.id, '_xp_settings', stringified_xp_settings)

    async def refresh_guilds_info(self):
        all_guilds_ids = []

        for guild in discord_client.guilds:  # for adding guilds that were joined while offline
            all_guilds_ids.append(guild.id)
            if guild.id not in variables.guilds_prefs.keys():
                await self.make_default_guild_prefs(guild)
                await log(f"ADDED NEW GUILD ON LAUNCH DURING REFRESH: ID={guild.id}. NAME='{guild}'",
                          ping_me=True, guild_id=guild.id)
        for guild_prefs in variables.guilds_prefs.values():  # for marking guilds that were left while offline
            if guild_prefs.guild_id not in all_guilds_ids:
                await guild_prefs.set_currently_in_guild(False)
                variables.guilds_prefs[guild_prefs.guild_id] = guild_prefs
                await self.repo.add_guild(guild_prefs)
        for guild_prefs in variables.guilds_prefs.values():  # for refreshing guilds names
            if guild_prefs.currently_in_guild and \
                    not guild_prefs.guild_name == discord_client.get_guild(guild_prefs.guild_id).name:
                guild_prefs.set_guild_name(discord_client.get_guild(guild_prefs.guild_id).name)
                variables.guilds_prefs[guild_prefs.guild_id] = guild_prefs
                await self.update_guild_in_db(discord_client.get_guild(guild_prefs.guild_id))

    async def update_guild_in_db(self, guild):
        guild_prefs = variables.guilds_prefs.get(guild.id)
        guild_prefs_enc_keys = encrypt_guild_prefs_keys(copy.deepcopy(guild_prefs))
        guild_prefs_stringified_values = guild_prefs_enc_keys.stringify_values()
        await self.repo.add_guild(guild_prefs_stringified_values)

    async def validate_autoroles_exist_and_remove_invalid_ones(self, guild_prefs: GuildPrefs, update_db=True):
        guild = discord_client.get_guild(guild_prefs.guild_id)
        roles_to_be_removed = []
        for role_id in guild_prefs.autoroles:
            if not guild.get_role(role_id):
                roles_to_be_removed.append(role_id)
        for role_id in roles_to_be_removed:
            guild_prefs.remove_autorole(role_id)

        if len(roles_to_be_removed) > 0 and update_db:
            variables.guilds_prefs[guild_prefs.guild_id] = guild_prefs
            await self.update_guild_in_db(guild)
        return guild_prefs

    async def validate_dj_roles_exist_and_remove_invalid_ones(self, guild_prefs: GuildPrefs, update_db=True):
        guild = discord_client.get_guild(guild_prefs.guild_id)
        roles_to_be_removed = []
        for role_id in guild_prefs.dj_roles:
            if not guild.get_role(role_id):
                roles_to_be_removed.append(role_id)
        for role_id in roles_to_be_removed:
            guild_prefs.remove_dj_role(role_id)

        if len(roles_to_be_removed) > 0 and update_db:
            variables.guilds_prefs[guild_prefs.guild_id] = guild_prefs
            await self.update_guild_in_db(guild)
        return guild_prefs
