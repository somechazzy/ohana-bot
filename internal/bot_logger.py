import asyncio
import io
import logging
from datetime import datetime
from pathlib import Path

import discord
import pytz
from globals_.constants import BotLogLevel, DISCORD_LOGGING_CHANNEL_ID, BOT_OWNER_ID, PING_WORTHY_LOG_LEVELS
from globals_.settings import settings


class BotLogger:

    def __init__(self, component=None, log_to_console_default=True, log_to_file_default=True,
                 log_to_discord_default=False, **kwargs):
        Path(settings.logging_directory).mkdir(parents=True, exist_ok=True)
        self.component = component or "Unknown"
        self.log_to_console_default = log_to_console_default
        self.log_to_file_default = log_to_file_default
        self.log_to_discord_default = log_to_discord_default
        self.default_level = BotLogLevel.GENERAL
        self.logger_ = logging.getLogger("bot")
        self._print_buffer = ""

    def log(self, message: str, level=None, user_id=None, guild_id=None, extras: dict = None,
            log_to_console: bool = None, log_to_file: bool = None, log_to_discord: bool = None):
        if log_to_console is None:
            log_to_console = self.log_to_console_default
        if log_to_file is None:
            log_to_file = self.log_to_file_default
        if log_to_discord is None:
            log_to_discord = self.log_to_discord_default
        if level in [BotLogLevel.BOT_INFO, BotLogLevel.ERROR, BotLogLevel.WARNING, BotLogLevel.MINOR_WARNING,
                     BotLogLevel.GUILD_JOIN, BotLogLevel.GUILD_LEAVE]:
            log_to_discord = True
        if not level:
            level = self.default_level
        if not extras:
            extras = {}
        extras['component'] = self.component

        asyncio.get_event_loop().create_task(self._log(message=message, level=level, user_id=user_id, guild_id=guild_id,
                                                       extras=extras, log_to_console=log_to_console,
                                                       log_to_file=log_to_file, log_to_discord=log_to_discord))

    async def _log(self, message, level, user_id, guild_id, extras, log_to_console, log_to_file, log_to_discord):
        if log_to_console:
            await asyncio.get_event_loop().run_in_executor(None, self._log_to_console, message,
                                                           level, user_id, guild_id, extras.copy())
        if log_to_file and not settings.no_log:
            await asyncio.get_event_loop().run_in_executor(None, self._log_to_file, message,
                                                           level, user_id, guild_id, extras.copy())
        if log_to_discord and not settings.no_log:
            await self._log_to_discord(message, level, user_id, guild_id, extras.copy())

    def _log_to_console(self, message, level, user_id, guild_id, extras):
        if not extras:
            extras = {}
        if user_id:
            extras['user_id'] = user_id
        if guild_id:
            extras['guild_id'] = guild_id
        extras_str = ' '.join([f'[{key}={value}]' for key, value in extras.items()])
        print(f"{ConsoleColors.FG.blue if not level == BotLogLevel.ERROR else ConsoleColors.FG.red}"
              f"{self._get_time_string()}{ConsoleColors.reset}"
              f" - {level} - {message}\nExtras: {extras_str}")

    def _log_to_file(self, message, level, user_id, guild_id, extras):
        try:
            extras = extras or {}
            if user_id:
                extras['user_id'] = user_id
            if guild_id:
                extras['guild_id'] = guild_id
            extras_str = ' '.join([f'[{key}={value}]' for key, value in extras.items()])
            with open(self._get_logging_file_path(), 'a+', encoding='utf-8') as logging_file:
                logging_file.write(
                    f"{self._get_time_string()} - {level} - {message} {extras_str}\n"
                )
        except Exception as exc:
            self._log_to_console(f"Error while logging to file: {exc}", BotLogLevel.ERROR, None, None, None)

    async def _log_to_discord(self, message, level, user_id, guild_id, extras):
        from globals_.clients import discord_client
        from utils.embed_factory import make_bot_log_embed
        log_channel = discord_client.get_channel(DISCORD_LOGGING_CHANNEL_ID)
        if len(message) > 4000:
            buf = io.BytesIO(str.encode(f"{self._get_time_string()} - {level}:\n{message}"))
            await log_channel.send(f"<@{BOT_OWNER_ID}>" if level in PING_WORTHY_LOG_LEVELS else "Log text:",
                                   files=[discord.File(buf, filename='log_message.txt'), ])
        else:
            extras = extras or {}
            if user_id:
                extras['user_id'] = user_id
            if guild_id:
                extras['guild_id'] = guild_id
            if 'component' in extras and level not in [BotLogLevel.ERROR, BotLogLevel.WARNING,
                                                       BotLogLevel.MINOR_WARNING]:
                del extras['component']
            embed = make_bot_log_embed(message=message, level=level, extras=extras)
            await log_channel.send(content=f"<@{BOT_OWNER_ID}>" if level in PING_WORTHY_LOG_LEVELS else "",
                                   embed=embed)

    @staticmethod
    def _get_time_string():
        return datetime.now(pytz.timezone('Asia/Jerusalem')).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _get_date_numeral_string():
        return datetime.now(pytz.timezone('Asia/Jerusalem')).strftime("%Y%m%d")

    def _get_logging_file_path(self):
        from utils.helpers import build_path
        return build_path([settings.logging_directory, f'{self._get_date_numeral_string()}.txt'],
                          append_main_path=False)


class InfoLogger(BotLogger):

    def __init__(self, component=None, log_to_console_default=True, log_to_file_default=True,
                 log_to_discord_default=False, default_level=BotLogLevel.GENERAL, **kwargs):
        super().__init__(component, log_to_console_default, log_to_file_default, log_to_discord_default, **kwargs)
        self.default_level = default_level


class ErrorLogger(BotLogger):
    def __init__(self, component=None, log_to_console_default=True, log_to_file_default=True,
                 log_to_discord_default=True, default_level=BotLogLevel.ERROR, **kwargs):
        super().__init__(component, log_to_console_default, log_to_file_default, log_to_discord_default, **kwargs)
        self.default_level = default_level


class DMLogger(BotLogger):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_level = BotLogLevel.RECEIVED_DM
        self.log_to_discord_default = True

    def log_dm(self, message: discord.Message):
        media_list = ""
        if message.attachments:
            media_list += "**Attachments**:\n"
            for attachment in message.attachments:
                media_list += f"[{attachment.content_type}] ({attachment.filename}) {attachment.url}\n"
        if message.stickers:
            media_list += "**Stickers**:\n"
            for sticker in message.stickers:
                media_list += f"[sticker] ({sticker.name}) {sticker.url}"
        message_content = "> " + message.content.strip().replace("\n", "\n> ")
        self.log(message=f"Received message on DMs from {message.author}\n"
                         f"{message_content}\n{media_list}", user_id=message.author.id)


class ConsoleColors:
    """ConsoleColors class:
    **copied from some stackoverflow answer**
    Reset all colors with reset
    Two subclasses fg for foreground and bg for background.
    Use as colors.subclass.color_name.
    i.e. colors.fg.red or colors.bg.green
    Also, the generic bold, disable, underline, reverse, strikethrough,
    and invisible work with the main class
    i.e. colors.bold
    """
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'

    class FG:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        lightgrey = '\033[37m'
        darkgrey = '\033[90m'
        light_red = '\033[91m'
        lightgreen = '\033[92m'
        yellow = '\033[93m'
        lightblue = '\033[94m'
        pink = '\033[95m'
        lightcyan = '\033[96m'

    class BG:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        lightgrey = '\033[47m'
