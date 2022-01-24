import json
from globals_.clients import firebase_client
from models.command import Command
from models.guild import GuildPrefs, GuildXP
from models.member import MemberXP
from models.username_mapping import UsernameMapping
from globals_ import variables
from .string_manipulation import build_path


def import_command_list():
    import_command_list_for("normal")
    import_command_list_for("music")
    import_command_list_for("admin")
    populate_command_names()


def populate_command_names():
    for command in variables.commands_dict.keys():
        variables.normal_commands_names.append(command)
        variables.normal_commands_names += [i for i in variables.commands_dict[command].aliases]
    for command in variables.admin_commands_dict.keys():
        variables.admin_commands_names.append(command)
        variables.admin_commands_names += [i for i in variables.admin_commands_dict[command].aliases]
    for command in variables.music_commands_dict.keys():
        variables.music_commands_names.append(command)
        variables.music_commands_names += [i for i in variables.music_commands_dict[command].aliases]
    variables.commands_names = \
        variables.normal_commands_names + variables.admin_commands_names + variables.music_commands_names


def import_command_list_for(commands_level: str):
    if commands_level.lower().strip() == "normal":
        commands_json_file = open(build_path(["globals_", "data", "commands_info", "user_commands_info.json"]),
                                  "r", encoding="utf8")
    elif commands_level.lower().strip() == "music":
        commands_json_file = open(build_path(["globals_", "data", "commands_info", "music_commands_info.json"]),
                                  "r", encoding="utf8")
    elif commands_level.lower().strip() == "admin":
        commands_json_file = open(build_path(["globals_", "data", "commands_info", "admin_commands_info.json"]),
                                  "r", encoding="utf8")
    else:
        return

    commands_json = commands_json_file.readlines()
    commands_json = ''.join(commands_json)
    commands_dict = json.loads(commands_json)
    for command_dict in commands_dict:
        command = Command(command_dict['name'])
        command.set_aliases(command_dict['aliases'])
        command.set_sub_commands(command_dict['sub_commands'])
        if commands_level.lower().strip() == "normal":
            command.set_section(command_dict['section'])
        elif commands_level.lower().strip() == "music":
            command.set_section(command_dict['section'])
        else:
            command.set_section(command_dict['section'])
        command.set_description(command_dict['description'])
        command.set_short_description(command_dict['short_description'])
        command.set_further_details(command_dict['further_details'])
        command.set_usage_examples(command_dict['usage_examples'])
        command.set_show_on_listing(command_dict['show_on_listing'])
        command.set_bot_perms(command_dict['bot_perms'])
        command.set_member_perms(command_dict['member_perms'])
        if commands_level.lower().strip() == "normal":
            variables.commands_dict[command_dict['name']] = command
        elif commands_level.lower().strip() == "music":
            variables.music_commands_dict[command_dict['name']] = command
        else:
            variables.admin_commands_dict[command_dict['name']] = command

    commands_json_file.close()


def import_level_requirement_models():
    model_file = open(build_path(["globals_", "data", "xp_requirement_ohana_model.json"]), "r", encoding="utf8")
    model_json = model_file.readlines()
    model_json = ''.join(model_json)
    model_dict = json.loads(model_json)

    for key, value in model_dict.items():
        variables.level_xp_map[int(key)] = int(value)
        variables.xp_level_map[int(value)] = int(key)

    model_file.close()


async def import_mal_usernames():
    usernames_entries = await firebase_client.get_mal_usernames()
    try:
        for username_entry in usernames_entries:
            discord_id = int(username_entry.key())
            username_dict = username_entry.val()
            username = username_dict["username"]
            variables.mal_usernames[discord_id] = UsernameMapping(discord_id, username)
    except:
        pass


async def import_al_usernames():
    usernames_entries = await firebase_client.get_al_usernames()
    try:
        for username_entry in usernames_entries:
            discord_id = int(username_entry.key())
            username_dict = username_entry.val()
            username = username_dict["username"]
            variables.al_usernames[discord_id] = UsernameMapping(discord_id, username)
    except:
        pass


async def import_guilds_prefs():
    guilds_prefs_nodes = await firebase_client.get_all_guilds_prefs()
    try:
        for _ in guilds_prefs_nodes:
            break
    except:
        return
    for guild_pref_node in guilds_prefs_nodes:
        guild_pref_node = guild_pref_node.val()
        guild_id = int(guild_pref_node.get("_guild_id"))
        guild_prefs = dict_to_guild_prefs_object(guild_pref_node)
        variables.guilds_prefs[guild_id] = guild_prefs.destringify_values()


async def import_guilds_xp():
    guilds_xp_nodes = await firebase_client.get_all_guilds_data(xp_only=True)
    try:
        for _ in guilds_xp_nodes:
            pass
    except:
        return
    for guild_xp_node in guilds_xp_nodes:
        guild_id = int(guild_xp_node.key())
        guild_xp_object = db_node_to_guild_xp_object(guild_xp_node)
        variables.guilds_xp[guild_id] = guild_xp_object


def dict_to_guild_prefs_object(guild_pref_node):
    guild_name = guild_pref_node.get("_guild_name")
    guild_id = int(guild_pref_node.get("_guild_id"))
    guild_prefs = GuildPrefs(guild_id, guild_name)
    guild_prefs.set_currently_in_guild(guild_pref_node.get("_currently_in_guild"))
    guild_prefs.set_prefix(guild_pref_node.get("_prefix"))
    guild_prefs.set_admin_prefix(guild_pref_node.get("_admin_prefix"))
    guild_prefs.set_music_prefix(guild_pref_node.get("_music_prefix"))
    guild_prefs.set_autoroles(guild_pref_node.get("_autoroles"))
    guild_prefs.set_dj_roles(guild_pref_node.get("_dj_roles"))
    guild_prefs.set_spam_channel(guild_pref_node.get("_spam_channel"))
    guild_prefs.set_logs_channel(guild_pref_node.get("_logs_channel"))
    guild_prefs.set_music_channel(guild_pref_node.get("_music_channel"))
    guild_prefs.set_music_player_message(guild_pref_node.get("_music_player_message"))
    guild_prefs.set_music_header_message(guild_pref_node.get("_music_header_message"))
    guild_prefs.set_fun_commands_enabled(guild_pref_node.get("_fun_commands_enabled"))
    guild_prefs.set_utility_commands_enabled(guild_pref_node.get("_utility_commands_enabled"))
    guild_prefs.set_mal_al_commands_enabled(guild_pref_node.get("_mal_al_commands_enabled"))
    guild_prefs.set_xp_commands_enabled(guild_pref_node.get("_xp_commands_enabled"))
    guild_prefs.set_moderation_commands_enabled(guild_pref_node.get("_moderation_commands_enabled"))
    guild_prefs.set_default_banned_words_enabled(guild_pref_node.get("_default_banned_words_enabled"))
    guild_prefs.set_role_persistence_enabled(guild_pref_node.get("_role_persistence_enabled"))
    guild_prefs.set_banned_words(guild_pref_node.get("_banned_words"))
    guild_prefs.set_single_message_channels(guild_pref_node.get("_single_message_channels"))
    guild_prefs.set_react_roles(guild_pref_node.get("_react_roles"))
    guild_prefs.set_gallery_channels(guild_pref_node.get("_gallery_channels"))
    guild_prefs.set_anime_channels(guild_pref_node.get("_anime_channels"))
    guild_prefs.set_auto_responses(guild_pref_node.get("_auto_responses"))
    guild_prefs.set_whitelisted_role(guild_pref_node.get("_whitelisted_role"))
    guild_prefs.set_xp_settings(guild_pref_node.get("_xp_settings"))
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
