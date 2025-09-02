"""
This module contains event handlers for guild-related events.
"""
import discord

from bot.utils.decorators import extensible_event
from clients import discord_client
from common.decorators import require_db_session
from components.guild_settings_components.guild_event_component import GuildEventComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import GuildEventType, AppLogCategory

from common.app_logger import AppLogger
logger: AppLogger = AppLogger('guild_logger')


@discord_client.event
@require_db_session
@extensible_event(group='guild')
async def on_guild_join(guild: discord.Guild):
    """
    Event handler for when the bot joins a new guild.
    Args:
        guild (discord.Guild): The guild that the bot has joined.
    """
    member_count = human_count = bot_count = 0
    text_channel_count = voice_channel_count = category_count = 0
    if not guild.chunked:
        await guild.chunk()
    for member in guild.members:
        member_count += 1
        if member.bot:
            bot_count += 1
        else:
            human_count += 1
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            text_channel_count += 1
        elif isinstance(channel, discord.VoiceChannel):
            voice_channel_count += 1
        elif isinstance(channel, discord.CategoryChannel):
            category_count += 1

    join_event_metadata = {"owner_id": guild.owner_id,
                           "created_at": guild.created_at.isoformat(sep=" "),
                           "member_count": member_count,
                           "human_count": human_count,
                           "bot_count": bot_count,
                           "text_channel_count": text_channel_count,
                           "voice_channel_count": voice_channel_count,
                           "category_count": category_count,
                           "bot_admin_status": guild.me.guild_permissions.administrator}

    guild_settings_component = GuildSettingsComponent()
    if await guild_settings_component.fetch_guild_settings(guild_id=guild.id):
        guild_settings = await guild_settings_component.get_guild_settings(guild_id=guild.id)
        await GuildEventComponent().create_guild_event(guild_id=guild.id,
                                                       guild_settings_id=guild_settings.guild_settings_id,
                                                       event=GuildEventType.JOIN,
                                                       event_time=guild.me.joined_at,
                                                       event_metadata=join_event_metadata)
        await GuildSettingsComponent().update_guild_settings(guild_id=guild.id,
                                                             guild_name=guild.name,
                                                             currently_in_guild=True)
    else:
        await GuildSettingsComponent().create_initial_guild_settings(guild_id=guild.id,
                                                                     guild_name=guild.name,
                                                                     joined_at=guild.me.joined_at,
                                                                     guild_data=join_event_metadata)
    logger.info(f"Joined guild: **{guild.name}** (ID: {guild.id})\n"
                f"Owner: {guild.owner} (ID: {guild.owner_id})\n"
                f"Member Count: {member_count}\n"
                f"Human Count: {human_count}\n"
                f"Bot Count: {bot_count}\n"
                f"Ohana admin status: {guild.me.guild_permissions.administrator}",
                category=AppLogCategory.BOT_GUILD_JOINED,
                log_to_discord=True,
                extras={"guild_id": guild.id,
                        "user_id": guild.owner_id})


@discord_client.event
@require_db_session
@extensible_event(group='guild')
async def on_guild_remove(guild: discord.Guild):
    """
    Event handler for when the bot is removed from a guild.
    Args:
        guild (discord.Guild): The guild that the bot has been removed from.
    """
    guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=guild.id)
    await GuildEventComponent().create_guild_event(guild_id=guild.id,
                                                   guild_settings_id=guild_settings.guild_settings_id,
                                                   event=GuildEventType.LEAVE,
                                                   event_time=guild.me.joined_at,
                                                   event_metadata={"owner_id": guild.owner_id,
                                                                   "member_count": guild.member_count})
    await GuildSettingsComponent().update_guild_settings(guild_id=guild.id,
                                                         currently_in_guild=False)
    logger.info(f"Left guild: **{guild.name}** (ID: {guild.id})\n"
                f"Owner: {guild.owner} (ID: {guild.owner_id})\n"
                f"Member Count: {guild.member_count}",
                category=AppLogCategory.BOT_GUILD_LEFT,
                log_to_discord=True,
                extras={"guild_id": guild.id,
                        "user_id": guild.owner_id})


@discord_client.event
@extensible_event(group='guild')
async def on_guild_update(*_):
    pass


@discord_client.event
@extensible_event(group='guild')
async def on_guild_emojis_update(*_):
    pass


@discord_client.event
@extensible_event(group='guild')
async def on_guild_stickers_update(*_):
    pass


@discord_client.event
@extensible_event(group='guild')
async def on_audit_log_entry_create(*_):
    pass


@discord_client.event
@extensible_event(group='guild')
async def on_invite_create(*_):
    pass


@discord_client.event
@extensible_event(group='guild')
async def on_invite_delete(*_):
    pass
