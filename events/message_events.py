import asyncio
import re
import discord
import traceback
from actions import send_embed, delete_message_from_guild
from auto_moderation.auto_moderator import automod
from components.music_components.message_enqueue_music_component import MessageEnqueueMusicComponent
from globals_.constants import BOT_OWNER_ID, OWNER_COMMAND_PREFIX
from internal.bot_logger import DMLogger, ErrorLogger
from globals_.clients import discord_client, xp_service
from internal.system import execute_owner_code_snippet
from internal.owner_commands import OwnerCommandsHandler
from globals_ import shared_memory
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent


client = discord_client


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.author.id == BOT_OWNER_ID and message.content.startswith(OWNER_COMMAND_PREFIX):
        return await (OwnerCommandsHandler(message)).handle()

    if isinstance(message.channel, discord.DMChannel):
        clean_message_content = re.sub("[^a-z] ", '', message.content.lower()).strip()
        if clean_message_content.startswith('help') or clean_message_content.startswith('h ') \
                or clean_message_content == 'h':
            return await message.reply("My help menu can be found using `/help`")
        await send_embed("Sorry, I've been told not to speak with strangers on DMs.\n"
                         "You can check my commands though. Type `/` to see what I have.", message.channel,
                         emoji="👉👈")
        return DMLogger().log_dm(message=message)

    if message.author.id == BOT_OWNER_ID and message.content.lower().startswith("execute"):
        return await execute_owner_code_snippet(message)

    guild_prefs = await GuildPrefsComponent().get_guild_prefs(message.guild)

    asyncio.get_event_loop().create_task(xp_service.add_message_to_handle(message=message))

    skip_commands = await automod(message, guild_prefs)
    if skip_commands:
        return

    if message.channel.id == guild_prefs.music_channel and message.content:
        try:
            await MessageEnqueueMusicComponent(message=message, guild_prefs=guild_prefs).handle_message()
        except Exception as e:
            ErrorLogger().log(f"Error encountered while handling enqueue: {e}"
                              f"\nChannel: {message.channel}/{message.guild} ({message.channel.id}/{message.guild.id})"
                              f"\nMessage: {message.content}"
                              f"\nTraceback: {traceback.format_exc()}", guild_id=message.guild.id)
        finally:
            try:
                await delete_message_from_guild(message=message, reason="Music channel")
            except Exception:
                pass


@client.event
async def on_message_delete(message: discord.Message):
    if message.author.bot or not message.content:
        return
    shared_memory.channel_id_sniped_message_map[message.channel.id] = {
        'content': message.content,
        'author_id': message.author.id,
        'created_at': message.created_at
    }
