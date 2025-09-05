from datetime import UTC, datetime, timedelta

import aiohttp
import discord

import cache
from bot.utils.embed_factory.general_embeds import get_error_embed
from bot.utils.bot_actions.basic_actions import send_message
from bot.utils.embed_factory.music_embeds import get_music_header_embed, get_music_player_embed
from bot.utils.embed_factory.reminder_embeds import get_reminder_delivery_embed
from bot.utils.view_factory.music_views import get_music_player_view
from bot.utils.view_factory.reminder_views import get_reminder_delivery_view
from clients import discord_client
from common.app_logger import AppLogger
from common.decorators import with_retry, suppress_and_log
from common.exceptions import UserReadableException
from components.guild_settings_components.guild_music_settings_component import GuildMusicSettingsComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import MusicDefaults, AppLogCategory
from models.dto.cachables import CachedReminder

logger = AppLogger(component=__name__)


@with_retry(count=3, delay=1)
async def send_reminder_to_user(reminder: CachedReminder):
    """
    Send a reminder to a user.
    Args:
        reminder (CachedReminder): Cacheable reminder object containing the reminder details.
    """
    embed = get_reminder_delivery_embed(reminder=reminder)
    view = get_reminder_delivery_view(reminder=reminder)

    recipient = await discord_client.fetch_user(reminder.recipient_user_id)
    await send_message(channel=recipient, embed=embed, view=view)
    seconds_to_send = (datetime.now(UTC) - reminder.reminder_time).seconds
    logger.info(f"Sent reminder to user {recipient.display_name} within {seconds_to_send} seconds.",
                extras={"user_id": reminder.recipient_user_id}, category=AppLogCategory.BOT_GENERAL)
    if seconds_to_send > 60:
        logger.warning(f"Reminder delivery took more than 60 seconds ({seconds_to_send} seconds)"
                       f" for reminder {reminder.user_reminder_id}.",
                       extras={"user_id": reminder.recipient_user_id})


async def handle_reminder_delivery_failure(reminder: CachedReminder, error: Exception):
    """
    Handle the failure of sending a reminder to a user.
    Args:
        reminder (CachedReminder): Cacheable reminder object containing the reminder details.
        error (Exception): The exception that occurred during the delivery attempt.
    """
    if reminder.is_relayed:
        reminder_owner = await discord_client.fetch_user(reminder.owner_user_id)
        error_message = error.user_message if isinstance(error, UserReadableException) else None
        await send_message(channel=reminder_owner,
                           embed=get_error_embed(f"Failed to deliver reminder to <@!{reminder.recipient_user_id}>.\n"
                                                 f"**Reminder**: `{reminder.clean_reminder_text}`\n"
                                                 + (f"**Reason**: {error_message}" if error_message else "")),
                           raise_on_error=False)


async def refresh_music_header_message(guild: discord.Guild):
    """
    Sends or refreshes the music header message in the specified guild's music channel.
    Args:
        guild (discord.Guild): The guild where the music header message should be sent.
    """
    guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=guild.id)
    if not guild_settings.music_channel_id:
        return
    channel = discord_client.get_partial_messageable(guild_settings.music_channel_id, guild_id=guild.id)
    if guild_settings.music_header_message_id:
        try:
            music_header_message = await channel.fetch_message(guild_settings.music_header_message_id)
            if music_header_message:
                await music_header_message.edit(embed=get_music_header_embed())
                return
        except discord.NotFound:
            pass
    message = await channel.send(embed=get_music_header_embed())
    await GuildMusicSettingsComponent().update_guild_music_settings(guild_id=guild.id,
                                                                    guild_settings_id=guild_settings.guild_settings_id,
                                                                    music_header_message_id=message.id)


@suppress_and_log(ignore_exceptions=(discord.Forbidden, discord.HTTPException,
                                     aiohttp.client_exceptions.ServerDisconnectedError))
async def refresh_music_player_message(guild: discord.Guild) -> bool:
    """
    Sends or refreshes the music player message in the specified guild's music channel.
    Args:
        guild (discord.Guild): The guild where the music player message should be sent.
    Returns:
        bool: True if the message was successfully sent or refreshed, False otherwise.
    """
    guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=guild.id)
    if not guild_settings.music_channel_id:
        return False
    music_service = cache.MUSIC_SERVICES.get(guild.id)
    if not (channel := guild.get_channel(guild_settings.music_channel_id)):
        return False
    if guild_settings.music_player_message_id:
        try:
            music_player_message = channel.get_partial_message(guild_settings.music_player_message_id)
            if music_player_message.created_at < (datetime.now(UTC) - timedelta(hours=1)):
                try:
                    await music_player_message.delete()
                except Exception as e:
                    logger.debug(f"Failed to delete old music player message in guild {guild.id}: {e}")
            else:
                await music_player_message.edit(content=MusicDefaults.DEFAULT_PLAYER_MESSAGE_CONTENT,
                                                embed=get_music_player_embed(guild=guild,
                                                                             music_service=music_service),
                                                view=get_music_player_view(music_service=music_service))
                return True
        except discord.NotFound:
            pass
    message = await channel.send(content=MusicDefaults.DEFAULT_PLAYER_MESSAGE_CONTENT,
                                 embed=get_music_player_embed(guild=guild, music_service=music_service),
                                 view=get_music_player_view(music_service=music_service))
    await GuildMusicSettingsComponent().update_guild_music_settings(guild_id=guild.id,
                                                                    guild_settings_id=guild_settings.guild_settings_id,
                                                                    music_player_message_id=message.id)
    return True
