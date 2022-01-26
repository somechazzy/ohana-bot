import asyncio
import re
import disnake as discord
import traceback
from actions import send_embed, delete_message_from_guild
from auto_moderation.auto_moderator import automod
from internal.bot_logging import log
from globals_.clients import discord_client
from internal.green import execute_owner_code_snippet
from commands import UserCommandHandler, MusicCommandHandler, AdminCommandHandler
from globals_ import constants, variables
from globals_.constants import BotLogType
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from xp.xp import handle_xp


@discord_client.event
async def on_message(message):
    if message.author.bot:
        return True

    if isinstance(message.channel, discord.DMChannel):
        return await handle_dm(message)

    if message.author.id == constants.BOT_OWNER_ID and message.content.lower().startswith("execute"):
        await execute_owner_code_snippet(message)
        return

    guild_prefs = await GuildPrefsComponent().get_guild_prefs(message.guild)

    asyncio.get_event_loop().create_task(handle_xp(message, guild_prefs))

    skip_commands = await automod(message, guild_prefs)
    if skip_commands:
        return

    if message.channel.id == guild_prefs.music_channel:
        if not message.content.startswith(f'{guild_prefs.music_prefix}'):
            message.content = f"{guild_prefs.music_prefix}play {message.content}"

    handler = None

    if message.content.strip().lower() == f"{constants.DEFAULT_PREFIX}help":
        message.content = f"{guild_prefs.prefix}{message.content[len(constants.DEFAULT_PREFIX):]}"
        handler = UserCommandHandler

    if message.content.strip().lower() == f"{constants.DEFAULT_MUSIC_PREFIX}help":
        message.content = f"{guild_prefs.music_prefix}{message.content[len(constants.DEFAULT_MUSIC_PREFIX):]}"
        handler = MusicCommandHandler

    if message.content.lower().startswith(guild_prefs.prefix.lower()):
        handler = UserCommandHandler

    if message.content.lower().startswith(guild_prefs.music_prefix.lower()):
        handler = MusicCommandHandler

    if message.content.lower().startswith(guild_prefs.admin_prefix.lower()):
        handler = AdminCommandHandler

    if handler:
        try:
            if message.channel.id == guild_prefs.music_channel and handler != MusicCommandHandler:
                await send_embed("Please use a different channel for non-music commands.", message.channel,
                                 delete_after=3)
            else:
                await handler(message, guild_prefs).handle_command()
        except Exception as e:
            await log(f"Error encountered while handling command: {e}"
                      f"\nCommand handler: {handler.__name__}"
                      f"\nChannel: {message.channel}/{message.guild} ({message.channel.id}/{message.guild.id})"
                      f"\nMessage: {message.content}"
                      f"\nTraceback: {traceback.format_exc()}",
                      level=BotLogType.BOT_ERROR, guild_id=message.guild.id)
        finally:
            if message.channel.id == guild_prefs.music_channel:
                try:
                    await delete_message_from_guild(message=message, reason="Music channel")
                except:
                    pass
        return


async def handle_dm(message):
    literal_message_content = re.sub("[^a-z] ", '', str(message.content).lower()).strip()
    if str(message.content).lower().startswith(f'{constants.DEFAULT_PREFIX}h'):
        return await UserCommandHandler(message).handle_help_on_dms()
    elif str(message.content).lower().startswith(f'{constants.DEFAULT_ADMIN_PREFIX}h'):
        return await AdminCommandHandler(message).handle_help_on_dms()
    elif str(message.content).lower().startswith(f'{constants.DEFAULT_MUSIC_PREFIX}h'):
        return await MusicCommandHandler(message).handle_help_on_dms()
    if literal_message_content.startswith('help') or literal_message_content.startswith('h ') \
            or literal_message_content == 'h':
        return await UserCommandHandler(message).handle_help_on_dms()
    if any([message.content.strip().split(' ')[0].lower() in [cn.lower() for cn in variables.normal_commands_names],
            message.content.startswith(constants.DEFAULT_PREFIX)]):
        if not message.content.startswith(constants.DEFAULT_PREFIX):
            message.content = f"{constants.DEFAULT_PREFIX}{message.content}"
        return await UserCommandHandler(message=message).handle_command()
    await send_embed("Sorry, I've been told not to speak with strangers on DMs.", message.channel,
                     emoji="👉👈")
    await log(f"Received message on DMs from {message.author}/{message.author.id} with content: "
              f"\"{message.content}\".", level=constants.BotLogType.RECEIVED_DM,
              ping_me=message.author.id != 294551247384739840, guild_id=None)
    return


@discord_client.event
async def on_message_delete(message: discord.Message):
    # for snipe command
    if message.author.bot or not message.content:
        return
    variables.channel_id_sniped_message_map[message.channel.id] = {
        'content': message.content,
        'author_id': message.author.id,
        'created_at': message.created_at
    }
