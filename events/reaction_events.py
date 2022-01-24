import disnake as discord
from auto_moderation.role_management import handle_react_role_remove, handle_react_role_add
from globals_.clients import discord_client
from commands.music_commands.music_reactions_handler import MusicPlayerReactionHandler
from globals_ import variables


@discord_client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == discord_client.user.id:
        return
    channel_id = payload.channel_id
    channel = discord_client.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        return
    message_id = payload.message_id
    emoji = payload.emoji
    guild: discord.Guild = channel.guild
    member: discord.Member = guild.get_member(payload.user_id)
    guild_prefs = variables.guilds_prefs[guild.id]
    if message_id == guild_prefs.music_player_message:
        return await MusicPlayerReactionHandler(channel=channel, message_id=message_id,
                                                emoji=emoji, member=member).handle()

    await handle_react_role_add(guild, channel_id, message_id, member, emoji)


@discord_client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.user_id == discord_client.user.id:
        return
    channel_id = payload.channel_id
    channel = discord_client.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        return
    message_id = payload.message_id
    emoji = payload.emoji
    guild: discord.Guild = channel.guild
    member: discord.Member = guild.get_member(payload.user_id)

    await handle_react_role_remove(guild, channel_id, message_id, member, emoji)
