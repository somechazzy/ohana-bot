import discord
from globals_.constants import BotLogLevel, GuildLogType, Colour
from internal.bot_logger import ErrorLogger
from models.guild import GuildPrefs
from globals_ import shared_memory
from utils.embed_factory import make_log_embed


async def log_to_server(guild: discord.Guild, event_type: GuildLogType, event=None, member=None,
                        message=None, role=None, roles=None, roles_removed=None, fields=None, values=None):
    if guild.id not in shared_memory.guilds_prefs:
        return
    guilds_prefs: GuildPrefs = shared_memory.guilds_prefs[guild.id]
    logs_channel: discord.TextChannel = guild.get_channel(int(guilds_prefs.logs_channel))
    if isinstance(logs_channel, type(None)):
        return
    if not logs_channel.permissions_for(guild.me).embed_links or \
            not logs_channel.permissions_for(guild.me).send_messages:
        return
    if values is None:
        values = []
    if fields is None:
        fields = []
    guild_avatar = guild.icon.with_size(128).url if guild.icon else None

    if event_type is GuildLogType.GENERAL:
        author_name = f"{guild.me}" if member is None else f"{member}"
        author_icon = f"{guild.me.avatar.with_size(128).url}" if member is None\
            else f"{member.avatar.with_size(128).url}" if member.avatar\
            else None
        color_hex = Colour.SILVER
        footer_text = f"ID: {member.id}" if member is not None else None
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.MEMBER_JOINED:
        event = ("Member" if not member.bot else "Bot") + " has joined the server."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.GREEN
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.MEMBER_LEFT:
        event = "Member has left the server."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.RED
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type in [GuildLogType.ASSIGNED_ROLE, GuildLogType.UNASSIGNED_ROLE]:
        action = 'given' if event_type is GuildLogType.ASSIGNED_ROLE else 'removed from'
        event = f"{member.mention} was {action} the {role.mention} role."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.ROLE_CHANGE
        footer_text = f"UID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.ASSIGNED_ROLES:
        roles_mentions = []
        for role in roles:
            roles_mentions.append(str(role.mention))
        roles_mentions_string = ", ".join(roles_mentions)
        event = f"{member.mention} was given the following roles: {roles_mentions_string}"
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.ROLE_CHANGE
        footer_text = f"UID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.UNASSIGNED_ROLES:
        roles_mentions = []
        for role in roles:
            roles_mentions.append(str(role.mention))
        roles_mentions_string = ", ".join(roles_mentions)
        event = f"{member.mention} was removed from the following roles: {roles_mentions_string}"
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.ROLE_CHANGE
        footer_text = f"UID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.EDITED_ROLES:
        roles_string_list = [str(role.mention) for role in roles]
        roles_string = ", ".join(roles_string_list)
        roles_removed_string_list = [str(role.mention) for role in roles_removed]
        roles_removed_string = ", ".join(roles_removed_string_list)
        event = f"{member.mention} was:" + \
                (f"\nGiven the following roles: {roles_string}. " if roles else "") +\
                (f"\nRemoved from the following roles: {roles_removed_string}. " if roles_removed else "")
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.ROLE_CHANGE
        footer_text = f"UID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.CREATED_ROLE:
        event = f"Role `{role}` was created."
        author_name = f"{role}"
        author_icon = guild_avatar
        color_hex = Colour.ROLE_CHANGE
        footer_text = f"ID: {role.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.KICKED_MEMBER:
        event = f"Member `{member}` was kicked."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.RED
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.BANNED_MEMBER:
        event = f"Member `{member}` was banned."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.RED
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.UNBANNED_MEMBER:
        event = f"User `{member}` was unbanned."
        author_name = f"{member}"
        author_icon = None
        color_hex = Colour.WARM_GOLD
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.MUTED_MEMBER:
        event = f"Member `{member}` was muted - on timeout."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.HOT_ORANGE
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.UNMUTED_MEMBER:
        event = f"Member `{member}` was unmuted - timeout lifted."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.BROWN
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.WARNED_MEMBER:
        event = f"Member `{member}` was warned."
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.BROWN
        footer_text = f"ID: {member.id}"
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.DELETED_MESSAGE:
        event = f"Message by `{message.author}` was deleted."
        author_name = f"{message.author}"
        author_icon = f"{message.author.avatar.with_size(128).url}" if message.author.avatar else None
        color_hex = Colour.BROWN
        footer_text = f"UID: {message.author.id}"
        fields.append("Channel")
        values.append(f"<#{message.channel.id}>")
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               footer_text=footer_text, fields=fields, values=values)

    elif event_type is GuildLogType.PERM_ERROR:
        author_name = f"Permission Error"
        author_icon = f"{guild.me.avatar.with_size(128).url}"
        color_hex = Colour.RED
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               fields=fields, values=values)

    elif event_type is GuildLogType.ACTION_ERROR:
        author_name = f"Action Failed"
        author_icon = f"{guild.me.avatar.with_size(128).url}"
        color_hex = Colour.RED
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               fields=fields, values=values)

    elif event_type is GuildLogType.SETTING_CHANGE:
        author_name = f"{member}"
        author_icon = f"{member.avatar.with_size(128).url}" if member.avatar else None
        color_hex = Colour.SILVER
        embed = make_log_embed(event, event_type, author_name, author_icon, guild_avatar, color_hex,
                               fields=fields, values=values)

    else:
        ErrorLogger("guild_logging").log(f"Failed at recognizing event log type '{event_type}'.",
                                         level=BotLogLevel.ERROR,
                                         guild_id=guild.id)
        return

    await logs_channel.send(" ", embed=embed)
