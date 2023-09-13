import json

from models.guild import GuildPrefs, GuildXP
from models.member import MemberXP
from models.music_stream import MusicStream
from models.username_mapping import UsernameMapping
from globals_ import shared_memory, constants
from .string_manipulation import build_path


def load_commands_permissions():
    user_commands_file = open(build_path(["globals_", "data", "commands_permissions", "user_commands.json"]),
                              'r', encoding="utf8")
    music_commands_file = open(build_path(["globals_", "data", "commands_permissions", "music_commands.json"]),
                               'r', encoding="utf8")
    admin_commands_file = open(build_path(["globals_", "data", "commands_permissions", "admin_commands.json"]),
                               'r', encoding="utf8")

    shared_memory.user_commands_permissions = json.loads(user_commands_file.read())
    shared_memory.music_commands_permissions = json.loads(music_commands_file.read())
    shared_memory.admin_commands_permissions = json.loads(admin_commands_file.read())


def load_level_requirement_models():
    model_file = open(build_path(["globals_", "data", "xp_requirement_ohana_model.json"]), "r", encoding="utf8")
    model_json = model_file.readlines()
    model_json = ''.join(model_json)
    model_dict = json.loads(model_json)

    for key, value in model_dict.items():
        constants.LEVEL_XP_MAP[int(key)] = int(value)
        constants.XP_LEVEL_MAP[int(value)] = int(key)

    model_file.close()


async def load_mal_usernames():
    from globals_.clients import firebase_client
    usernames_entries = await firebase_client.get_mal_usernames()
    for username_node in usernames_entries:
        discord_id = int(username_node.key())
        username = username_node.val()["username"]
        shared_memory.user_id_mal_username_map[discord_id] = UsernameMapping(discord_id, username)


async def load_al_usernames():
    from globals_.clients import firebase_client
    usernames_entries = await firebase_client.get_al_usernames()
    for username_node in usernames_entries:
        discord_id = int(username_node.key())
        username = username_node.val()["username"]
        shared_memory.user_id_anilist_username_map[discord_id] = UsernameMapping(discord_id, username)


async def load_guilds_prefs():
    from globals_.clients import firebase_client
    guilds_prefs_nodes = await firebase_client.get_all_guilds_prefs()
    for guild_pref_node in guilds_prefs_nodes:
        guild_id = int(guild_pref_node.key())
        guild_pref_node = guild_pref_node.val()
        guild_prefs = dict_to_guild_prefs_object(guild_pref_node)
        shared_memory.guilds_prefs[guild_id] = guild_prefs.destringify_values()


async def load_guilds_xp():
    from globals_.clients import firebase_client
    guilds_xp_nodes = await firebase_client.get_all_guilds_xp()
    for guild_xp_node in guilds_xp_nodes:
        guild_id = int(guild_xp_node.key())
        guild_xp_object = db_node_to_guild_xp_object(guild_xp_node)
        shared_memory.guilds_xp[guild_id] = guild_xp_object


def dict_to_guild_prefs_object(guild_pref_node):
    guild_name = guild_pref_node.get("_guild_name")
    guild_id = int(guild_pref_node.get("_guild_id"))
    guild_prefs = GuildPrefs(guild_id, guild_name)
    guild_prefs.set_autoroles(guild_pref_node.get("_autoroles"))
    guild_prefs.set_dj_roles(guild_pref_node.get("_dj_roles"))
    guild_prefs.set_logs_channel(guild_pref_node.get("_logs_channel"))
    guild_prefs.set_music_channel(guild_pref_node.get("_music_channel"))
    guild_prefs.set_music_player_message(guild_pref_node.get("_music_player_message"))
    guild_prefs.set_music_player_message_timestamp(guild_pref_node.get("_music_player_message_timestamp"))
    guild_prefs.set_music_header_message(guild_pref_node.get("_music_header_message"))
    guild_prefs.set_default_banned_words_enabled(guild_pref_node.get("_default_banned_words_enabled"))
    guild_prefs.set_role_persistence_enabled(guild_pref_node.get("_role_persistence_enabled"))
    guild_prefs.set_single_message_channels(guild_pref_node.get("_single_message_channels"))
    guild_prefs.set_gallery_channels(guild_pref_node.get("_gallery_channels"))
    guild_prefs.set_xp_settings(guild_pref_node.get("_xp_settings"))
    guild_prefs.set_role_menus(guild_pref_node.get("_role_menus"))
    return guild_prefs


def db_node_to_guild_xp_object(guild_xp_node):
    guild_xp = GuildXP(int(guild_xp_node.key()))
    guild_xp_dict = guild_xp_node.val()
    members_xp = {}
    for member_id, member_xp_dict in guild_xp_dict.items():
        member_xp = MemberXP(member_id=int(member_id))
        member_xp.set_member_tag(member_xp_dict.get('_member_tag', f"({member_id})"))
        member_xp.set_messages(member_xp_dict.get('_messages'))

        member_xp.set_xp(member_xp_dict.get('_xp'))
        member_xp.set_timeframe_ts(member_xp_dict.get('_timeframe_ts'))

        member_xp.set_xp_decayed(member_xp_dict.get('_xp_decayed'))
        member_xp.set_last_message_ts(member_xp_dict.get('_last_message_ts'))
        member_xp.set_ts_of_last_decay(member_xp_dict.get('_ts_of_last_decay'))

        member_xp.set_level(member_xp_dict.get('_level'))
        member_xp.set_last_sent_level(member_xp_dict.get('_last_sent_level'))

        member_xp.is_synced = True
        members_xp[int(member_id)] = member_xp.destringify_values()

    guild_xp.set_members_xp(members_xp)

    return guild_xp


async def load_guilds_with_disabled_players_refresh_button():
    from globals_.clients import firebase_client
    guilds_nodes = await firebase_client.get_guilds_with_disabled_players_refresh_button()
    for guild_node in guilds_nodes:
        guild_id = int(guild_node.key())
        shared_memory.GUILDS_WITH_PLAYER_REFRESH_DISABLED.add(guild_id)


def load_music_streams():
    with open(build_path(["globals_", "data", "streams.json"]), "r", encoding="utf8") as f:
        streams = json.load(f)
        for stream in streams:
            shared_memory.music_streams[stream['code']] = MusicStream(info_dict=stream)
