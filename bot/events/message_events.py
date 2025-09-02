"""
This module contains event handlers for message-related events.
"""
import discord

from bot.utils.bot_actions.automod_actions import perform_message_automoderation
from bot.utils.bot_actions.basic_actions import delete_message
from bot.utils.decorators import extensible_event
from bot.utils.helpers.message_helpers import log_dm
from clients import discord_client, xp_service
from common.decorators import require_db_session
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from settings import OWNER_COMMAND_PREFIX, BOT_OWNER_ID
from strings.general_strings import GeneralStrings
from system.owner_commands import OwnerCommandsHandler

from common.app_logger import AppLogger
logger: AppLogger = AppLogger('message_events')


@discord_client.event
@require_db_session
@extensible_event(group='message')
async def on_message(message: discord.Message):
    """
    Event handler for new messages.
    Args:
        message (discord.Message): The message object.
    """
    if discord_client.user.id == message.author.id:
        return

    if message.author.id == BOT_OWNER_ID and message.content.startswith(OWNER_COMMAND_PREFIX):
        await OwnerCommandsHandler(message=message).handle()
        return

    if message.channel.type == discord.ChannelType.private:
        await message.channel.send(GeneralStrings.DM_RESPONSE)
        log_dm(message=message)
        return

    guild_settings = await GuildSettingsComponent().get_guild_settings(message.guild.id)
    if message.channel.id == guild_settings.music_channel_id:
        await delete_message(message, reason="Music channel")

    if message.author.bot:
        return

    await perform_message_automoderation(message)

    await xp_service.add_message_to_queue(message)


@discord_client.event
@extensible_event(group='message')
async def on_message_edit(*_):
    pass


@discord_client.event
@require_db_session
@extensible_event(group='message')
async def on_message_delete(*_):
    pass


@discord_client.event
@extensible_event(group='message')
async def on_bulk_message_delete(*_):
    pass


@discord_client.event
@extensible_event(group='message')
async def on_raw_message_edit(*_):
    pass


@discord_client.event
@extensible_event(group='message')
async def on_raw_message_delete(*_):
    pass


@discord_client.event
@extensible_event(group='message')
async def on_raw_bulk_message_delete(*_):
    pass
