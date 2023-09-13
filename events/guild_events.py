import asyncio

from discord import NotFound

from components.music_components.base_music_component import MusicComponent
from globals_.constants import BotLogLevel, DEFAULT_PLAYER_MESSAGE_CONTENT
from internal.bot_logger import InfoLogger
from utils.helpers import get_player_message_views
from globals_.clients import discord_client
from globals_ import shared_memory
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from datetime import datetime
from actions import send_welcoming_message
from utils.embed_factory import make_initial_player_message_embed

client = discord_client


info_logger = InfoLogger("GuildEvents")


@client.event
async def on_guild_join(guild):
    member_count = guild.member_count
    human_count = len([member for member in guild.members if not member.bot])
    bot_count = len([member for member in guild.members if member.bot])
    owner_other_guild_count = \
        len([guild_ for guild_ in client.guilds if guild_.owner.id == guild.owner.id and guild_.id != guild.id])
    info_logger.log(f"{guild} ({guild.id}): {member_count} members.\n"
                    f"Owned by {guild.owner} ({guild.owner.id}).\n" +
                    (f"**This bot is in** {owner_other_guild_count} other guilds they own.\n"
                     if owner_other_guild_count else "") +
                    f"Created at <t:{int(datetime.timestamp(guild.created_at))}:f>.\n"
                    f"Human count = {human_count}.\n"
                    f"Bot count = {bot_count}.\n"
                    f"Bot Percentage = {round(bot_count / member_count, 2)}.\n"
                    f"Bot admin status: {guild.me.guild_permissions.administrator}.",
                    level=BotLogLevel.GUILD_JOIN, guild_id=guild.id)
    _ = await GuildPrefsComponent().get_guild_prefs(guild)  # get or create
    await send_welcoming_message(guild)


@client.event
async def on_guild_remove(guild):
    if guild:
        info_logger.log(f"{guild} ({guild.id}): {guild.member_count} members.\n"
                        f"Owned by {guild.owner} ({guild.owner.id}).\n"
                        f"Created at <t:{int(datetime.timestamp(guild.created_at))}:f>.",
                        level=BotLogLevel.GUILD_LEAVE, guild_id=guild.id)


@client.event
async def on_voice_state_update(member, _, after):
    if member.id == client.user.id:
        if not after.channel:
            guild_prefs = shared_memory.guilds_prefs[member.guild.id]
            music_channel = discord_client.get_channel(guild_prefs.music_channel)
            if music_channel:
                player_message = music_channel.get_partial_message(guild_prefs.music_player_message)
                content = DEFAULT_PLAYER_MESSAGE_CONTENT
                embed = make_initial_player_message_embed(guild=member.guild)
                views = get_player_message_views()
                try:
                    await player_message.edit(content=content, embed=embed, view=views)
                except NotFound:
                    pass
                except Exception as e:
                    if "rate limited" in str(e) or '429' in str(e):
                        await MusicComponent().setup_player_channel(guild=member.guild, send_header=False)
                    else:
                        raise e

        gms = shared_memory.guild_music_services.pop(member.guild.id, None)

        if gms:  # fallback for this weird case where discord tells you you're disconnected when you're not
            await asyncio.sleep(3)
            if member.guild.voice_client and member.guild.voice_client.is_connected() \
                    and member.guild.voice_client.is_playing():
                gms.voice_client = member.guild.voice_client
                shared_memory.guild_music_services[member.guild.id] = gms
                await gms.refresh_player()
