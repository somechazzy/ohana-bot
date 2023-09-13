import asyncio

import discord
from actions import delete_message_from_guild, send_message
from auto_moderation.guild_specific_perks.base import GuildPerks
from internal.guild_logging import log_to_server
from globals_ import constants
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from models.guild import GuildPrefs


async def automod(message: discord.Message, guild_prefs: GuildPrefs):
    # returns skip status on commands
    # (whether the bot shouldn't check commands in the text or should)

    if message.channel.id in guild_prefs.single_message_channels.keys():
        deleted = await handle_single_message_channel(message, guild_prefs)
        if deleted:
            return True

    if message.channel.id in guild_prefs.gallery_channels:
        deleted = await handle_gallery_channel(message)
        if deleted:
            return True

    await handle_custom_automod(message)

    return False


async def handle_single_message_channel(message, guild_prefs):
    if message.channel.permissions_for(message.author).administrator:
        return
    for single_message_channel_dict in guild_prefs.single_message_channels.values():
        if single_message_channel_dict.get("channel_id") == str(message.channel.id):
            role_id = int(single_message_channel_dict.get("role_id"))
            role = message.guild.get_role(role_id)
            if not role:
                await log_to_server(message.guild, constants.GuildLogType.ACTION_ERROR, message=message,
                                    event=f"Cannot find role with ID {role_id}, necessary for single-text channel "
                                          f"#{message.channel}.\nSingle-text mode "
                                          f"has been disabled for that channel.")
                await GuildPrefsComponent().remove_guild_single_message_channel(message.guild, str(message.channel.id))
                return False

            if role in message.author.roles:
                if single_message_channel_dict.get("mode") == 'delete':
                    await delete_message_from_guild(message, reason=f"Single-message channel: member "
                                                                    f"already has <@&{role_id}> role.")
                    return True
            else:
                await asyncio.sleep(5)
                try:
                    if not getattr(message.channel.permissions_for(message.guild.me), 'manage_roles', True):
                        return False
                    await message.author.add_roles(role, reason=f"single-message channel role (#{message.channel})")
                    await log_to_server(message.guild, constants.GuildLogType.ASSIGNED_ROLE, message=message,
                                        role=role, member=message.author,
                                        fields=["Reason"],
                                        values=[f"Single-message channel role (#{message.channel})"])
                    return True
                except discord.Forbidden:
                    return False


async def handle_gallery_channel(message):
    if message.channel.permissions_for(message.author).administrator:
        return False
    if len(message.attachments) == 0:
        await delete_message_from_guild(message, reason="text-only text in gallery channel")

        await send_message(f"Sorry, {message.author.mention}. Only images are allowed in this channel :(",
                           message.channel, delete_after=6)
        return True
    return False


async def handle_custom_automod(message):
    # for special features that are guild-specific
    perks_class = GuildPerks.get_perks_class_by_guild_id(message.guild.id)
    if perks_class:
        await perks_class().handle_automod(message)
