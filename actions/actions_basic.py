import traceback
import disnake as discord

from globals_.constants import BOT_COLOR
from internal.bot_logging import log, log_to_server
from globals_ import constants
from helpers import bot_has_permission_to_send_text_in_channel, shorten_text_if_above_x_characters,\
    bot_has_permission_to_send_embed_in_channel, make_message_send_log_string


# This function got way too messy over time and I'm too lazy to rewrite it - but it works
async def send_message(message, channel, embed=None, files=None, log_message=True, embed_feedback_message=False,
                       reply_to=None, force_send_without_embed=False, delete_after=None, view=None):
    """
    Function to use for sending messages either on DMs or on servers.
    :param (str or None) message: message content to send
    :param (discord.TextChannel or discord.DMChannel) channel: target channel
    :param (discord.Embed or None) embed: embed to go with the message
    :param (list of discord.File or None) files: list of files to send with the message
    :param (bool) log_message: whether to log the message or not
    :param (bool) embed_feedback_message: whether this message is a feedback message (not really important)
    :param (discord.Message or None) reply_to: parent message to reply to
    :param (bool) force_send_without_embed: whether to force send the message as text in case the bot can't embed
    :param (int or None) delete_after: seconds to wait before deleting the sent message
    :param (discord.ui.View or None) view: discord UI views to go with the message
    :return: (discord.Message or None) sent message
    """
    if message is None:
        message = ""
    if isinstance(channel, discord.Member) or isinstance(channel, discord.User):
        channel = await get_dm_channel(user=channel)
    is_dm = True if isinstance(channel, discord.DMChannel) else False
    guild_id = channel.guild.id if getattr(channel, 'guild', None) else None

    if not is_dm and not bot_has_permission_to_send_text_in_channel(channel):
        message = make_message_send_log_string(message, embed, embed_feedback_message)
        await log(f"Denied permission to send text: '{message}'. Channel: {channel}/{channel.guild}.",
                  level=constants.BotLogType.PERM_ERROR, guild_id=guild_id)
        return None
    if embed is not None:
        if not is_dm and not bot_has_permission_to_send_embed_in_channel(channel):
            if embed_feedback_message:
                if reply_to:
                    try:
                        ret_message = await reply_to.reply(str(embed.description), mention_author=False,
                                                           delete_after=delete_after)
                    except:
                        ret_message = await channel.send(str(embed.description), files=files,
                                                         delete_after=delete_after, view=view)
                else:
                    ret_message = await channel.send(str(embed.description), files=files,
                                                     delete_after=delete_after, view=view)
                if log_message:
                    await log(f"'{message}'. Channel: {channel}/{channel.guild}.",
                              level=constants.BotLogType.REPLY_SENT if reply_to
                              else constants.BotLogType.MESSAGE_SENT, log_to_db=False,
                              log_to_discord=False, guild_id=guild_id)
                return ret_message
            else:
                if message and force_send_without_embed:
                    if reply_to:
                        try:
                            ret_message = await reply_to.reply(message, mention_author=False,
                                                               delete_after=delete_after, view=view)
                        except:
                            ret_message = await channel.send(message, files=files, delete_after=delete_after, view=view)
                    else:
                        ret_message = await channel.send(message, files=files, delete_after=delete_after, view=view)
                    return ret_message
                if reply_to:
                    try:
                        ret_message = await reply_to.reply("Unfortunately, I don't have the permission to send "
                                                           "an embed in this channel :(", mention_author=False)
                    except:
                        ret_message = await channel.send("Unfortunately, I don't have the permission"
                                                         " to send an embed in this channel :(")
                else:
                    ret_message = await channel.send("Unfortunately, I don't have the permission"
                                                     " to send an embed in this channel :(")
                if log_message:
                    await log(f"Denied permission to send embed. Channel: {channel}/{channel.guild}.",
                              level=constants.BotLogType.PERM_ERROR, guild_id=guild_id)
                return ret_message
        else:
            if reply_to:
                try:
                    ret_message = await reply_to.reply(message, embed=embed, mention_author=False,
                                                       delete_after=delete_after, view=view)
                except:
                    ret_message = await channel.send(message, embed=embed, files=files,
                                                     delete_after=delete_after, view=view)
            else:
                ret_message = await channel.send(message, embed=embed, files=files,
                                                 delete_after=delete_after, view=view)
            if log_message:
                message = make_message_send_log_string(message, embed, embed_feedback_message)
                await log(
                    f"Embed with details: '{message}'. Channel: {channel}/{channel.guild if not is_dm else None}.",
                    level=constants.BotLogType.REPLY_SENT if reply_to
                    else constants.BotLogType.MESSAGE_SENT, log_to_db=False, log_to_discord=False,
                    guild_id=guild_id)
    else:
        if reply_to:
            try:
                ret_message = await reply_to.reply(message, mention_author=False, delete_after=delete_after, view=view)
            except:
                ret_message = await channel.send(message, files=files, delete_after=delete_after, view=view)
        else:
            ret_message = await channel.send(message, files=files, delete_after=delete_after, view=view)
        if log_message:
            await log(f"'{message}'. Channel: {channel}/{channel.guild if hasattr(channel, 'guild') else None}.",
                      level=constants.BotLogType.REPLY_SENT if reply_to
                      else constants.BotLogType.MESSAGE_SENT, log_to_db=False,
                      log_to_discord=False, guild_id=guild_id)
    return ret_message


async def send_embed(message, channel, emoji='💬', color=BOT_COLOR, logging=True, reply_to=None,
                     bold=True, thumbnail_url=None, fields_values=None, delete_after=None, view=None):
    """
    Function used to quickly send simple embeds.
    :param (str) message: text to quick-embed
    :param (discord.TextChannel or discord.DMChannel) channel: target channel
    :param (str) emoji: text emoji to add at the start of the quick-embed
    :param (int) color: color of the embed, you can pass this in hex format 0xFFFFFF
    :param (bool) logging: whether to log the message or not
    :param (discord.Message or None) reply_to: parent message to reply to
    :param (bool) bold: whether to apply bold formatting to the message
    :param (str or None) thumbnail_url: URL of a thumbnail to add to the embed
    :param (dict or None) fields_values: mapping of field-value to add to the embed
    :param (int or None) delete_after: seconds to wait before deleting the sent message
    :param (discord.ui.View or None) view: discord UI views to go with the message
    :return: (discord.Message or None) sent message
    """
    asterisks = '**' if bold else ''
    if emoji is None:
        description = f"{asterisks}{message}{asterisks}"
    else:
        description = f"{emoji}  {asterisks}{message}{asterisks}‎‎‎"
    embed = discord.Embed(colour=discord.Colour(color),
                          description=description)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if fields_values:
        for field, value in fields_values.items():
            embed.add_field(name=field, value=value)
    return await send_message(message=None, channel=channel, embed=embed, log_message=logging,
                              embed_feedback_message=True, reply_to=reply_to, delete_after=delete_after, view=view)


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


async def delete_message_from_guild(message, reason="Not provided."):
    if not message.guild:
        return
    content = message.content if message.content else "-"
    if not message.channel.permissions_for(message.guild.me).manage_messages and not message.author == message.guild.me:
        await log_to_server(message.guild, constants.GuildLogType.PERM_ERROR, message=message,
                            event=f"Failed at deleting text by {message.author} "
                                  f"due to lacking the `Manage Messages` permission.",
                            fields=["Message", "Reason"],
                            values=[shorten_text_if_above_x_characters(content, 250), reason])
        return
    try:
        await message.delete()
        await log(f"'{content}' by {message.author}/{message.author.id}. Reason: {reason}. "
                  f"Channel: {message.channel}/{message.guild}.", level=constants.BotLogType.MESSAGE_DELETED,
                  log_to_db=False, log_to_discord=False, guild_id=message.guild.id if message.guild else None)
        if not message.author == message.guild.me:
            await log_to_server(message.guild, constants.GuildLogType.DELETED_MESSAGE, message=message,
                                fields=["Message", "Reason"],
                                values=[shorten_text_if_above_x_characters(content, 250), reason])
        return True
    except:
        return False


async def edit_message(message, content, embed=None, reason="not provided",
                       log_enable=True, embed_feedback_message=False, view=None):
    contains_embed = embed is not None
    is_dm = True if isinstance(message.channel, discord.DMChannel) else False
    if not is_dm and not bot_has_permission_to_send_embed_in_channel(message.channel) and contains_embed:
        if embed_feedback_message:
            if log_enable:
                content = str(embed.description)
                await log(f"To '{content}'. Embed status: {contains_embed}. Reason: {reason}. "
                          f"Channel: {message.channel}/{message.guild}.",
                          level=constants.BotLogType.MESSAGE_EDITED, log_to_db=False, log_to_discord=False,
                          guild_id=message.guild.id if message.guild else None)
            return await message.edit(content=content, view=view)
        await message.edit(content="Unfortunately, I don't have the permission to send an embed in this channel :(",
                           view=None)
        if log_enable:
            await log(f"Denied permission to edit to embed. Channel: {message.channel}/{message.guild}.",
                      level=constants.BotLogType.PERM_ERROR, guild_id=message.guild.id if message.guild else None)
            return None
    try:
        message = await message.edit(content=content, embed=embed, view=view)
        if log_enable:
            await log(f"To '{content}'. Embed status: {contains_embed}. Reason: {reason}. "
                      f"Channel: {message.channel}/{message.guild}.",
                      level=constants.BotLogType.MESSAGE_EDITED, log_to_db=False, log_to_discord=False,
                      guild_id=message.guild.id if message.guild else None)
        return message
    except Exception as e:
        await log(f"Could not edit text from To '{content}'. Embed status from to {contains_embed}. Reason: {reason}. "
                  f"Channel: {message.channel}/{message.guild}. Error: {e}.",
                  level=constants.BotLogType.BOT_WARNING, guild_id=message.guild.id if message.guild else None)
        return None


async def edit_embed(message, original_message, emoji='💬', color=BOT_COLOR,
                     reason="not provided", logging=True, bold=True):
    asterisks = '**' if bold else ''
    if emoji is None:
        description = f"{asterisks}{message}{asterisks}"
    else:
        description = f"{emoji}  {asterisks}{message}{asterisks}"
    embed = discord.Embed(colour=discord.Colour(color),
                          description=description)
    return await edit_message(original_message, "", embed=embed, reason=reason,
                              log_enable=logging, embed_feedback_message=True)


async def send_perm_error_message(permission: str, bot_or_member: str, channel, reply_to=None, delete_after=None):
    pronoun = "I" if bot_or_member.lower() == "bot" else "You"
    await send_embed(f"{pronoun} need the {permission} permission for that command :(", channel,
                     emoji='❌', color=0xFF522D, reply_to=reply_to, delete_after=delete_after)


async def send_hierarchy_error_message(bot_or_member: str, channel, reply_to=None):
    pronoun = "I" if bot_or_member.lower() == "bot" else "You"
    await send_embed(f"{pronoun} can't do that to a member on the same level "
                     f"of the hierarchy or higher 🙄", channel,
                     emoji='❌', color=0xFF522D, reply_to=reply_to)


async def add_role(member, role_id, reason="Not provided"):
    role: discord.Role = member.guild.get_role(role_id)
    if role in member.roles:
        return
    if role.is_default() or str(role) == "@everyone":
        return
    if not role:
        await log(f"Could not get role with ID={role_id}.", level=constants.BotLogType.BOT_ERROR,
                  guild_id=member.guild.id)
        return
    bot_highest_role = member.guild.me.roles[-1]
    if role >= bot_highest_role:
        await log(f"Role `{role}` ({role_id}) in Guild `{member.guild}` ({member.guild.id}) is higher than my highest"
                  f" role so I cannot assign it to member `{member}`.", level=constants.BotLogType.BOT_WARNING_IGNORE,
                  guild_id=member.guild.id)
        await log_to_server(member.guild, constants.GuildLogType.ACTION_ERROR,
                            event=f"Role `{role}` is higher than my highest so I could not assign it to {member}.")
        return
    try:
        await member.add_roles(role, reason=reason)
        await log(f"Added role \"{role}\" to {member}. Guild: {member.guild}.", level=constants.BotLogType.MEMBER_INFO,
                  guild_id=member.guild.id, log_to_discord=False)
        await log_to_server(member.guild, constants.GuildLogType.ASSIGNED_ROLE, role=role, member=member,
                            fields=["Reason"],
                            values=[reason])
    except Exception as e:
        await log(f"Could not add role \"{role}\" to {member}. Exception: {e}: {traceback.format_exc()}",
                  level=constants.BotLogType.BOT_WARNING, guild_id=member.guild.id)


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
        await log(f"Role `{role}` ({role_id}) in Guild `{member.guild}` ({member.guild.id}) is higher than my highest"
                  f" role so I cannot remove it from member `{member}`.", level=constants.BotLogType.BOT_WARNING_IGNORE,
                  guild_id=member.guild.id)
        await log_to_server(member.guild, constants.GuildLogType.ACTION_ERROR,
                            event=f"Role `{role}` is higher than my highest so I could not remove it from {member}.")
        return
    try:
        await member.remove_roles(role, reason=reason)
        await log(f"Removed role \"{role}\" from {member}. Guild: {member.guild}.",
                  level=constants.BotLogType.MEMBER_INFO, guild_id=member.guild.id, log_to_discord=False)
        await log_to_server(member.guild, constants.GuildLogType.UNASSIGNED_ROLE, role=role, member=member,
                            fields=["Reason"],
                            values=[reason])
    except Exception as e:
        await log(f"Could not remove role \"{role}\" from {member}. Exception: {e}",
                  level=constants.BotLogType.BOT_WARNING, guild_id=member.guild.id)


async def add_roles(member: discord.Member, roles_ids, reason="Not provided"):
    bot_highest_role = member.guild.me.roles[-1]
    roles = []
    roles_higher_in_hierarchy = []
    for role_id in roles_ids:
        role = member.guild.get_role(int(role_id))
        if str(role) == "@everyone":
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
        await log(f"Added roles {roles_names_and_ids} to {member}. Guild: {member.guild}.",
                  level=constants.BotLogType.MEMBER_INFO, guild_id=member.guild.id, log_to_discord=False)
        await log_to_server(member.guild, constants.GuildLogType.ASSIGNED_ROLES, roles=roles, member=member,
                            fields=["Reason"],
                            values=[reason])
        if roles_higher_in_hierarchy:
            await log_to_server(member.guild, constants.GuildLogType.ACTION_ERROR,
                                event=f"Roles `{roles_names_and_ids_higher_in_hierarchy}` are higher than my highest"
                                      f" role so I could not assign them to {member}.")

        return True
    except Exception as e:
        await log(f"Could not add roles \"{roles_names_and_ids}\" to {member}. Exception: {e}",
                  level=constants.BotLogType.BOT_WARNING, guild_id=member.guild.id)
        return False


def _role_cannot_be_added(role, bot_highest_role):
    if role.is_bot_managed() or role.is_premium_subscriber() or role.is_integration() \
            or role.is_default() or str(role) in ["@everyone", "@@everyone"] or role >= bot_highest_role:
        return True


async def edit_roles(member, roles_ids, reason="not provided"):
    existing_member_role_ids = [role.id for role in member.roles]
    if not member.guild.me.guild_permissions.manage_roles:
        await log_to_server(member.guild, constants.GuildLogType.PERM_ERROR,
                            event="Couldn't modify member roles because"
                                  " I do not have the necessary permissions (Manage Roles)",
                            fields=["Reason for attempt"],
                            values=[reason])
        return
    bot_highest_role = member.guild.me.roles[-1]
    roles = []
    for role_id in roles_ids:
        role = member.guild.get_role(int(role_id))
        if not role:
            continue
        if _role_cannot_be_added(role, bot_highest_role):
            if role.id not in existing_member_role_ids:
                continue
        roles.append(role)
    if not roles or roles == member.roles:
        return
    roles_added = [role for role in roles if not (role.id in existing_member_role_ids or role.id == member.guild.id)]
    roles_removed = [role for role in member.roles if role not in roles]
    roles = list(set(roles))
    member = await member.edit(roles=roles, reason=reason)

    await log((f"Added roles {[f'`{role}/{role.id}`' for role in roles_added]}. " if roles_added else "") +
              (f"Removed roles {[f'`{role}/{role.id}`' for role in roles_removed]}. " if roles_removed else " ") +
              f"for {member}. Guild: {member.guild}. Reason: {reason}",
              level=constants.BotLogType.MEMBER_INFO, guild_id=member.guild.id, log_to_discord=False)
    await log_to_server(member.guild, constants.GuildLogType.EDITED_ROLES,
                        roles=roles_added,
                        roles_removed=roles_removed,
                        member=member,
                        fields=["Reason"],
                        values=[reason])


async def create_role(guild, name, reason="Not provided"):
    try:
        created_role = await guild.create_role(name=name, reason=reason)
    except:
        await log(f"{(traceback.format_exc())}", level=constants.BotLogType.BOT_WARNING, print_to_console=False,
                  guild_id=guild.id)
        return None
    if not created_role:
        return None
    await log_to_server(guild, constants.GuildLogType.CREATED_ROLE, role=created_role,
                        fields=["Reason"],
                        values=[reason])
    return created_role


async def remove_reactions(message: discord.Message):
    try:
        await message.clear_reactions()
    except:
        if isinstance(message.channel, discord.DMChannel):
            bot_member = message.channel.me
        else:
            bot_member = message.guild.me
        for reaction in message.reactions:
            try:
                await message.remove_reaction(reaction, bot_member)
            except:
                pass
