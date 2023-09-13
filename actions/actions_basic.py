import asyncio
import traceback
import discord

from globals_.constants import Colour, BotLogLevel, GuildLogType
from internal.bot_logger import ErrorLogger, InfoLogger
from internal.guild_logging import log_to_server
from utils.helpers import bot_has_permission_to_send_text_in_channel, shorten_text_if_above_x_characters,\
    bot_has_permission_to_send_embed_in_channel
from utils.embed_factory import make_welcoming_embed, quick_embed

info_logger = InfoLogger(component="BasicAction")
error_logger = ErrorLogger(component="BasicAction")


async def send_message(message, channel, embed=None, files=None, logging=True, embed_feedback_message=False,
                       reply_to=None, force_send_without_embed=False, delete_after=None, view=None):
    if not message and not embed and not files:
        return None
    if message is None:
        message = ""
    if isinstance(channel, discord.Member) or isinstance(channel, discord.User):
        channel = await get_dm_channel(user=channel)
    is_dm = True if isinstance(channel, discord.DMChannel) else False
    guild_id = channel.guild.id if getattr(channel, 'guild', None) else None

    if not is_dm and not bot_has_permission_to_send_text_in_channel(channel):
        return None
    if embed is not None:
        if not is_dm and not bot_has_permission_to_send_embed_in_channel(channel):
            if embed_feedback_message:
                if reply_to:
                    try:
                        ret_message = await reply_to.reply(embed.description, mention_author=False,
                                                           delete_after=delete_after)
                    except (discord.Forbidden, discord.NotFound):
                        ret_message = await channel.send(embed.description, files=files,
                                                         delete_after=delete_after, view=view)
                else:
                    ret_message = await channel.send(embed.description, files=files,
                                                     delete_after=delete_after, view=view)
                if logging:
                    info_logger.log(f"'{message}'. Channel: {channel}/{channel.guild}.",
                                    level=BotLogLevel.REPLY_SENT if reply_to
                                    else BotLogLevel.MESSAGE_SENT, guild_id=guild_id)
                return ret_message
            else:
                if message and force_send_without_embed:
                    if reply_to:
                        try:
                            ret_message = await reply_to.reply(message, mention_author=False,
                                                               delete_after=delete_after, view=view)
                        except (discord.Forbidden, discord.NotFound):
                            ret_message = await channel.send(message, files=files, delete_after=delete_after, view=view)
                    else:
                        ret_message = await channel.send(message, files=files, delete_after=delete_after, view=view)
                    return ret_message
                if reply_to:
                    try:
                        ret_message = await reply_to.reply("Unfortunately, I don't have the permission to send "
                                                           "an embed in this channel :(", mention_author=False)
                    except (discord.Forbidden, discord.NotFound):
                        ret_message = await channel.send("Unfortunately, I don't have the permission"
                                                         " to send an embed in this channel :(")
                else:
                    ret_message = await channel.send("Unfortunately, I don't have the permission"
                                                     " to send an embed in this channel :(")
                return ret_message
        else:
            if reply_to:
                try:
                    ret_message = await reply_to.reply(message, embed=embed, mention_author=False,
                                                       delete_after=delete_after, view=view)
                except (discord.Forbidden, discord.NotFound):
                    ret_message = await channel.send(message, embed=embed, files=files,
                                                     delete_after=delete_after, view=view)
            else:
                ret_message = await channel.send(message, embed=embed, files=files,
                                                 delete_after=delete_after, view=view)
            if logging:
                info_logger.log(f"Embed with text: '{message or embed.title or embed.description}'. "
                                f"Channel: {channel}/{channel.guild if not is_dm else None}.",
                                level=BotLogLevel.REPLY_SENT if reply_to
                                else BotLogLevel.MESSAGE_SENT, guild_id=guild_id)
    else:
        if reply_to:
            try:
                ret_message = await reply_to.reply(message, mention_author=False, delete_after=delete_after, view=view)
            except (discord.Forbidden, discord.NotFound):
                ret_message = await channel.send(message, files=files, delete_after=delete_after, view=view)
        else:
            ret_message = await channel.send(message, files=files, delete_after=delete_after, view=view)
        if logging:
            info_logger.log(f"'{message}'. Channel: {channel}/{channel.guild if hasattr(channel, 'guild') else None}.",
                            level=BotLogLevel.REPLY_SENT if reply_to else BotLogLevel.MESSAGE_SENT,
                            guild_id=guild_id)
    return ret_message


async def get_dm_channel(user):
    """
    Gets DM channel with a user, and creates one if it didn't exist
    :param (discord.Member or discord.User) user: user to get DM channel for
    :return: (discord.DMChannel)
    """
    dm_channel = user.dm_channel
    if not dm_channel:
        dm_channel = await user.create_dm()
    return dm_channel


async def send_embed(message, channel, emoji='💬', color=Colour.PRIMARY_ACCENT, logging=True, reply_to=None,
                     bold=True, thumbnail_url=None, fields_values=None, delete_after=None, view=None, title=None):
    embed = quick_embed(message, bold=bold, color=color, thumbnail_url=thumbnail_url, fields_values=fields_values,
                        emoji=emoji, title=title)
    return await send_message(message=None, channel=channel, embed=embed, logging=logging, view=view,
                              embed_feedback_message=True, reply_to=reply_to, delete_after=delete_after)


async def delete_message_from_guild(message: discord.Message, reason="Not provided."):
    if not message.guild:
        return
    content = message.content if not isinstance(message.content, type(None)) else "No-content-in-text-found"
    if not message.channel.permissions_for(message.guild.me).manage_messages and not message.author == message.guild.me:
        await log_to_server(message.guild, GuildLogType.PERM_ERROR, message=message,
                            event=f"Failed at deleting text by {message.author} "
                                  f"due to lacking the `Manage Messages` permission.",
                            fields=["Message", "Reason"],
                            values=[shorten_text_if_above_x_characters(content, 250), reason])
        return
    try:
        await message.delete()
        info_logger.log(f"'{content}' by {message.author}/{message.author.id}. Reason: {reason}. "
                        f"Channel: {message.channel}/{message.guild}.", level=BotLogLevel.MESSAGE_DELETED,
                        guild_id=message.guild.id if message.guild else None)
        if not message.author == message.guild.me:
            await log_to_server(message.guild, GuildLogType.DELETED_MESSAGE, message=message,
                                fields=["Message", "Reason"],
                                values=[shorten_text_if_above_x_characters(content, 250), reason])
        return True
    except (discord.Forbidden, discord.NotFound):
        return False


async def edit_message(message: discord.Message, content, embed=None, reason="not provided",
                       log_enable=True, embed_feedback_message=False, view=None):
    contains_embed = embed is not None
    is_dm = True if isinstance(message.channel, discord.DMChannel) else False
    if not is_dm and not bot_has_permission_to_send_embed_in_channel(message.channel) and contains_embed:
        if embed_feedback_message:
            if log_enable:
                content = embed.description
                info_logger.log(f"To '{content}'. Embed status: {contains_embed}. Reason: {reason}. "
                                f"Channel: {message.channel}/{message.guild}.",
                                level=BotLogLevel.MESSAGE_EDITED,
                                guild_id=message.guild.id if message.guild else None)
            return await message.edit(content=content, view=view)
        await message.edit(content="Unfortunately, I don't have the permission to send an embed in this channel :(",
                           view=None)
    try:
        message = await message.edit(content=content, embed=embed, view=view)
        if log_enable:
            info_logger.log(f"To '{content}'. Embed status: {contains_embed}. Reason: {reason}. "
                            f"Channel: {message.channel}/{message.guild}.",
                            level=BotLogLevel.MESSAGE_EDITED,
                            guild_id=message.guild.id if message.guild else None)
        return message
    except (discord.Forbidden, discord.NotFound):
        return None


async def edit_embed(message, original_message, emoji='💬', color=Colour.PRIMARY_ACCENT,
                     reason="not provided", logging=True, bold=True):
    asterisks = '**' if bold else ''
    if emoji is None:
        description = f"{asterisks}{message}{asterisks}"
    else:
        description = f"{emoji}  {asterisks}{message}{asterisks}"
    embed = discord.Embed(colour=color,
                          description=description)
    return await edit_message(original_message, "", embed=embed, reason=reason,
                              log_enable=logging, embed_feedback_message=True)


async def add_role(member, role_id, reason="Not provided"):
    role: discord.Role = member.guild.get_role(role_id)
    if role in member.roles:
        return
    if role.is_default() or str(role) == "@everyone":
        return
    if not role:
        raise Exception(f"Role with ID {role_id} not found in guild {member.guild}")
    bot_highest_role = member.guild.me.roles[-1]
    if role >= bot_highest_role:
        error_logger.log(f"Role `{role}` ({role_id}) in Guild `{member.guild}` ({member.guild.id}) "
                         f"is higher than my highest  role so I cannot assign it to member `{member}`.",
                         level=BotLogLevel.MINOR_WARNING,
                         guild_id=member.guild.id, user_id=member.id)
        await log_to_server(member.guild, GuildLogType.ACTION_ERROR,
                            event=f"Role `{role}` is higher than my highest so I could not assign it to {member}.")
        return
    try:
        await member.add_roles(role, reason=reason)
        info_logger.log(f"Added role \"{role}\" to {member}. Guild: {member.guild}.", level=BotLogLevel.MEMBER_INFO,
                        guild_id=member.guild.id, user_id=member.id)
        await log_to_server(member.guild, GuildLogType.ASSIGNED_ROLE, role=role, member=member,
                            fields=["Reason"],
                            values=[reason])
    except Exception as e:
        error_logger.log(f"Could not add role \"{role}\" to {member}. Exception: {e}: {traceback.format_exc()}",
                         level=BotLogLevel.WARNING, guild_id=member.guild.id, user_id=member.id)


async def remove_role(member, role_id, reason="Not provided"):
    role: discord.Role = member.guild.get_role(role_id)
    if not role:
        return
    if role not in member.roles:
        return
    if role.is_default() or str(role) == "@everyone":
        return
    bot_highest_role = member.guild.me.roles[-1]
    if role >= bot_highest_role:
        await log_to_server(member.guild, GuildLogType.ACTION_ERROR,
                            event=f"Role `{role}` is higher than my highest so I could not remove it from {member}.")
        return
    try:
        await member.remove_roles(role, reason=reason)
        info_logger.log(f"Removed role \"{role}\" from {member}. Guild: {member.guild}.",
                        level=BotLogLevel.MEMBER_INFO, guild_id=member.guild.id, user_id=member.id)
        await log_to_server(member.guild, GuildLogType.UNASSIGNED_ROLE, role=role, member=member,
                            fields=["Reason"],
                            values=[reason])
    except discord.Forbidden:
        return


async def add_roles(member: discord.Member, roles_ids, reason="Not provided"):
    bot_highest_role = member.guild.me.roles[-1]
    roles = []
    roles_higher_in_hierarchy = []
    for role_id in roles_ids:
        role = member.guild.get_role(int(role_id))
        if str(role).__eq__("@everyone"):
            continue
        if not role:
            continue
        if role.is_bot_managed() or role.is_premium_subscriber() or role.is_integration() \
                or role.is_default():
            continue
        if role in member.roles:
            continue
        if role >= bot_highest_role:
            roles_higher_in_hierarchy.append(role)
            continue
        roles.append(role)

    if len(roles) == 0:
        return True
    roles_names_and_ids = []
    roles_names_and_ids_higher_in_hierarchy = ""
    for role in roles:
        roles_names_and_ids.append(f"{role}/{role.id}")
    if roles_higher_in_hierarchy:
        for role_higher_in_hierarchy in roles_higher_in_hierarchy:
            roles_names_and_ids_higher_in_hierarchy += f"{role_higher_in_hierarchy}/{role_higher_in_hierarchy.id}, "
    roles_names_and_ids_higher_in_hierarchy = \
        shorten_text_if_above_x_characters(roles_names_and_ids_higher_in_hierarchy.strip(), 800)
    try:
        roles_to_add = roles.copy()
        for role in member.roles:
            if role not in roles_to_add:
                roles_to_add.append(role)
        roles_to_add = list(set(roles_to_add))
        member = await member.edit(roles=roles_to_add, reason=reason)
        info_logger.log(f"Added roles {roles_names_and_ids} to {member}. Guild: {member.guild}.",
                        level=BotLogLevel.MEMBER_INFO, guild_id=member.guild.id, user_id=member.id)
        await log_to_server(member.guild, GuildLogType.ASSIGNED_ROLES, roles=roles, member=member,
                            fields=["Reason"],
                            values=[reason])
        if roles_higher_in_hierarchy:
            await log_to_server(member.guild, GuildLogType.ACTION_ERROR,
                                event=f"Roles `{roles_names_and_ids_higher_in_hierarchy}` are higher than my highest"
                                      f" role so I could not assign them to {member}.")

        return True
    except discord.Forbidden:
        return False


def _role_cannot_be_added(role, bot_highest_role):
    if role.is_bot_managed() or role.is_premium_subscriber() or role.is_integration() \
            or role.is_default() or str(role) in ["@everyone", "@@everyone"] or role >= bot_highest_role:
        return True


async def edit_roles(member, roles_ids=None, roles=None, reason="not provided"):
    if roles_ids is None and roles is None:
        raise ValueError("roles_ids and roles cannot both be None")
    if roles is None:
        roles = []
        for role_id in set(roles_ids):
            role = member.guild.get_role(int(role_id))
            if role:
                roles.append(role)
    existing_member_role_ids = {role.id for role in member.roles}
    if not member.guild.me.guild_permissions.manage_roles:
        await log_to_server(member.guild, GuildLogType.PERM_ERROR,
                            event="Couldn't modify member roles because"
                                  " I do not have the necessary permissions (Manage Roles)",
                            fields=["Reason for attempt"],
                            values=[reason])
        return
    bot_highest_role = member.guild.me.roles[-1]
    new_roles = []
    for role in roles:
        if not role:
            continue
        if _role_cannot_be_added(role, bot_highest_role):
            if role.id not in existing_member_role_ids:
                continue
        new_roles.append(role)
    if not new_roles or new_roles == member.roles:
        return
    roles_added = [role for role in new_roles
                   if not (role.id in existing_member_role_ids or role.id == member.guild.id)]
    roles_removed = [role for role in member.roles if role not in new_roles]
    if not roles_added and not roles_removed:
        return

    member = await member.edit(roles=new_roles, reason=reason)

    info_logger.log((f"Added roles {[f'`{role}/{role.id}`' for role in roles_added]}. " if roles_added else "") +
                    (f"Removed roles {[f'`{role}/{role.id}`' for role in roles_removed]}. " if roles_removed else " ") +
                    f"for {member}. Guild: {member.guild}. Reason: {reason}",
                    level=BotLogLevel.MEMBER_INFO, guild_id=member.guild.id, user_id=member.id)
    await log_to_server(member.guild, GuildLogType.EDITED_ROLES,
                        roles=roles_added,
                        roles_removed=roles_removed,
                        member=member,
                        fields=["Reason"],
                        values=[reason])


async def create_role(guild, name, reason="Not provided"):
    try:
        created_role = await guild.create_role(name=name, reason=reason)
    except discord.Forbidden:
        return None
    if not created_role:
        return None
    await log_to_server(guild, GuildLogType.CREATED_ROLE, role=created_role,
                        fields=["Reason"],
                        values=[reason])
    return created_role


async def send_welcoming_message(guild: discord.Guild, recurse=True):
    for channel in guild.text_channels:
        permissions = channel.permissions_for(guild.me)
        if permissions.send_messages and permissions.embed_links:
            embed = make_welcoming_embed(guild)
            await send_message(message="", embed=embed, channel=channel)
            return
    await asyncio.sleep(60)
    if recurse:
        await send_welcoming_message(guild, recurse=False)
