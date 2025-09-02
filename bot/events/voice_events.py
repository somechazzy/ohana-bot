"""
This module contains event handlers for voice-related events.
"""
import discord

import cache
from bot.utils.decorators import extensible_event
from clients import discord_client
from common.decorators import require_db_session
from bot.guild_music_service import GuildMusicService
from utils.helpers.context_helpers import create_isolated_task


@discord_client.event
@require_db_session
@extensible_event(group='voice')
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """
    Event handler for voice state updates in a guild.
    Args:
        member (discord.Member): The member whose voice state has changed.
        before (discord.VoiceState): The previous voice state of the member.
        after (discord.VoiceState): The new voice state of the member.
    """
    if (gms := cache.MUSIC_SERVICES.get(member.guild.id)) and member.id == discord_client.user.id:
        if before.channel and not after.channel:
            await gms.kill(failure_ok=True)
        elif before.channel != after.channel:
            current_stream = gms.current_stream
            after_channel_id = after.channel.id
            await gms.kill()
            gms = await GuildMusicService.instantiate_with_connection(guild_id=member.guild.id,
                                                                      voice_channel_id=after_channel_id,
                                                                      reconnect_on_already_connected=True)
            if current_stream:
                gms.set_radio_stream(current_stream)
                create_isolated_task(gms.start())
    if gms:
        gms.check_and_update_idle_status()


@discord_client.event
@extensible_event(group='voice')
async def on_voice_channel_effect(*_):
    pass
