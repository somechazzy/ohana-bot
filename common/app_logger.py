import asyncio
import traceback
import sys
import aiofiles
import io
import logging
from logging import Handler, LogRecord
from pathlib import Path
from datetime import datetime, UTC

from discord import Webhook, File as DiscordFile

from common.decorators import suppress_and_log
from common.http_session import get_async_http_session
from utils.helpers.context_helpers import get_context_id
from settings import BOT_OWNER_ID, DEBUG_ENABLED, DEBUG_EXTERNALLY, \
    LOGGING_CHANNEL_WEBHOOK_URL, LOGTAIL_TOKEN, LOGGING_DIRECTORY, REDIRECT_STDOUT_TO_LOGGER
from constants import AppLogCategory, AppLogLevel
from utils.helpers.text_manipulation_helpers import shorten_text


async_log_queue = asyncio.PriorityQueue()


class AppLogger:
    def __init__(self,
                 component: str = None,
                 log_to_console_default: bool = True,
                 log_to_file_default: bool = True,
                 log_externally_default: bool = True,
                 log_to_discord_default: bool = False):

        self.component = component or "AppLogger"
        self.log_to_console_default = log_to_console_default
        self.log_to_file_default = log_to_file_default
        self.log_externally_default = log_externally_default
        self.log_to_discord_default = log_to_discord_default

    @suppress_and_log(log=False)
    def _log(self,
             message: str,
             *,
             category: str = AppLogCategory.APP_GENERAL,
             level: str = AppLogLevel.INFO,
             component: str = "Unknown",
             log_to_console: bool = None,
             log_to_file: bool = None,
             log_externally: bool = None,
             log_to_discord: bool = None,
             extras: dict | None = None):
        extras = extras or {}
        original_category = category
        category = (category or AppLogCategory.APP_GENERAL).replace('_', ' ').title().replace(' ', '/', 1)
        level = level or AppLogLevel.INFO
        component = component or self.component
        extras.update({"component": component,
                       "category": category,
                       "context_id": get_context_id()})

        log_to_console = log_to_console if log_to_console is not None else self.log_to_console_default
        log_to_file = (log_to_file if log_to_file is not None else self.log_to_file_default) \
            and LOGGING_DIRECTORY
        log_externally = (log_externally if log_externally is not None else self.log_externally_default) \
            and LOGTAIL_TOKEN
        log_to_discord = (log_to_discord if log_to_discord is not None else self.log_to_discord_default) \
            and LOGGING_CHANNEL_WEBHOOK_URL

        record = console_logger.makeRecord(
            name=category,
            level=AppLogLevel.to_numeric(level=level),
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
            extra=extras,
        )

        if log_to_console:
            console_logger.handle(record)

        log_record_data = LogRecordData(
            message=message,
            level=level,
            category=category,
            original_category=original_category,
            component=component,
            log_time=datetime.now(UTC),
            context_id=get_context_id(),
            extras=extras,
            log_to_file=log_to_file,
            log_to_discord=log_to_discord,
            log_externally=log_externally,
        )
        async_log_queue.put_nowait(log_record_data)

    # quick access methods
    def debug(self, message: str,
              *,
              category: str = None,
              component: str = None,
              log_to_console: bool = True,
              log_to_file: bool = True,
              log_externally: bool = DEBUG_EXTERNALLY,
              log_to_discord: bool = False,
              extras: dict | None = None):
        if not DEBUG_ENABLED:
            return
        self._log(
            message=message,
            category=category,
            component=component or self.component,
            log_to_console=log_to_console,
            log_to_file=log_to_file,
            log_externally=log_externally,
            log_to_discord=log_to_discord,
            level=AppLogLevel.DEBUG,
            extras=extras,
        )

    def info(self, message: str,
             *,
             category: str = None,
             component: str = None,
             log_to_console: bool = True,
             log_to_file: bool = True,
             log_externally: bool = True,
             log_to_discord: bool = False,
             extras: dict | None = None):
        self._log(
            message=message,
            category=category,
            component=component or self.component,
            log_to_console=log_to_console,
            log_to_file=log_to_file,
            log_externally=log_externally,
            log_to_discord=log_to_discord,
            level=AppLogLevel.INFO,
            extras=extras
        )

    def warning(self, message: str,
                *,
                category: str = None,
                component: str = None,
                log_to_console: bool = True,
                log_to_file: bool = True,
                log_externally: bool = True,
                log_to_discord: bool = True,
                extras: dict | None = None):
        self._log(
            message=message,
            category=category,
            component=component or self.component,
            log_to_console=log_to_console,
            log_to_file=log_to_file,
            log_externally=log_externally,
            log_to_discord=log_to_discord,
            level=AppLogLevel.WARNING,
            extras=extras,
        )

    def error(self, message: str,
              *,
              category: str = None,
              component: str = None,
              log_to_console: bool = True,
              log_to_file: bool = True,
              log_externally: bool = True,
              log_to_discord: bool = True,
              extras: dict | None = None):
        self._log(
            message=message,
            category=category,
            component=component or self.component,
            log_to_console=log_to_console,
            log_to_file=log_to_file,
            log_externally=log_externally,
            log_to_discord=log_to_discord,
            level=AppLogLevel.ERROR,
            extras=(extras or {}) | {"traceback": traceback.format_exc()},
        )

    def critical(self, message: str,
                 *,
                 category: str = None,
                 component: str = None,
                 log_to_console: bool = True,
                 log_to_file: bool = True,
                 log_externally: bool = True,
                 log_to_discord: bool = True,
                 extras: dict | None = None):
        self._log(
            message=message,
            category=category,
            component=component or self.component,
            log_to_console=log_to_console,
            log_to_file=log_to_file,
            log_externally=log_externally,
            log_to_discord=log_to_discord,
            level=AppLogLevel.CRITICAL,
            extras=extras
        )


class AsyncFileLogHandler:
    def __init__(self):
        self.path = Path(LOGGING_DIRECTORY) / f"{datetime.now(UTC).strftime("%Y.%m.%d")}.txt"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def log(self, log_record_data: 'LogRecordData'):
        line = (f"\n{log_record_data.log_time.strftime("%Y-%m-%d %H:%M:%S")}"
                f" [{log_record_data.level}]"
                f" {log_record_data.category}"
                f" - {log_record_data.message} \n"
                + " ".join(f"[{k}={v}]" for k, v in log_record_data.extras.items()))
        async with aiofiles.open(self.path, mode='a', encoding='utf-8') as f:
            await f.write(line)


class DiscordLogHandler:
    def __init__(self):
        self.webhook_url = LOGGING_CHANNEL_WEBHOOK_URL

    async def log(self, log_record_data: 'LogRecordData'):
        if not self.webhook_url:
            return
        message = log_record_data.message
        level = log_record_data.level
        extras = {}
        for extra_key, extra_val in log_record_data.extras.items():
            if extra_key in ["category"]:
                continue
            if extra_key == "traceback":
                extra_val = f"```py\n{shorten_text(extra_val, 980)}\n```"
            extras[extra_key.replace('_', ' ').title()] = extra_val
        from bot.utils.embed_factory.log_embeds import get_bot_log_embed
        content = f"<@{BOT_OWNER_ID}>" if (
                level == AppLogLevel.ERROR or log_record_data.original_category in [AppLogCategory.BOT_DM_RECEIVED,
                                                                                    AppLogCategory.BOT_GUILD_JOINED,
                                                                                    AppLogCategory.BOT_GUILD_LEFT]
        ) else None
        session = await get_async_http_session(name=self.__class__.__name__)
        webhook = Webhook.from_url(self.webhook_url, session=session)
        if len(message) > 4000:
            log_file = DiscordFile(io.BytesIO(f"[{log_record_data.log_time.strftime("%Y-%m-%d %H:%M:%S")}]\n"
                                              f"<{level}>\n"
                                              f"{message}".encode()),
                                   filename=f"log_message_"
                                            f"{log_record_data.log_time.strftime("%Y-%m-%d_%H.%M.%S")}.txt")
            embed = get_bot_log_embed(message=shorten_text(message, 300),
                                      category=log_record_data.original_category,
                                      level=level,
                                      log_time=log_record_data.log_time,
                                      extras=extras)
            await webhook.send(content=content, embed=embed,
                               files=[log_file])
        else:
            embed = get_bot_log_embed(message=message,
                                      category=log_record_data.original_category,
                                      level=level,
                                      log_time=log_record_data.log_time,
                                      extras=extras)
            await webhook.send(content=content, embed=embed)


class ExternalLogHandler:
    def __init__(self):
        from services.logtail_service import LogtailService
        self.logtail_service: LogtailService = LogtailService(token=LOGTAIL_TOKEN)

    async def log(self, log_records_data: list['LogRecordData']):
        logtail_data = [
            {
                "message": log_record_data.message,
                "dt": log_record_data.log_time.timestamp(),
                "level": log_record_data.level,
                "category": log_record_data.category,
                "component": log_record_data.component,
                "context_id": log_record_data.context_id,
                **log_record_data.extras,
            } for log_record_data in log_records_data
        ]
        if not logtail_data:
            return
        await self.logtail_service.log(log_records=logtail_data)


class LogRecordData:
    def __init__(self, message: str, level: str, category: str, original_category: str, component: str,
                 log_time: datetime, context_id: str, extras: dict, log_to_file: bool,
                 log_to_discord: bool, log_externally: bool):
        self.message = message
        self.level = level
        self.category = category
        self.original_category = original_category
        self.component = component
        self.log_time = log_time
        self.context_id = context_id
        self.extras = extras or {}
        self.log_to_file = log_to_file
        self.log_to_discord = log_to_discord
        self.log_externally = log_externally

    def __lt__(self, other):
        return self.log_time < other.log_time

    def __gt__(self, other):
        return self.log_time > other.log_time


class ConsoleLoggingHandler(Handler):
    COLORS = {
        "DEBUG": "\033[90m",      # reset / no color
        "INFO": "\033[92m",      # green
        "WARNING": "\033[93m",   # yellow/orange
        "ERROR": "\033[91m",     # red
        "CRITICAL": "\033[95m",  # magenta
    }
    RESET = "\033[0m"

    def emit(self, record: LogRecord):
        try:
            msg = self.format(record)
            stream = sys.__stderr__ if record.levelno > logging.WARNING else sys.__stdout__
            if not msg.endswith("\n"):
                msg += "\n"
            stream.write(msg)
            if traceback_ := getattr(record, "traceback", None):
                stream.write(f"Traceback:\n{traceback_}\n")
            stream.flush()
        except Exception:
            self.handleError(record)

    def format(self, record: logging.LogRecord) -> str:
        level_name = record.levelname
        color = self.COLORS.get(level_name, self.RESET)
        record.levelname = f"{color}{level_name}{self.RESET}"
        return super().format(record)


class DpyLoggingHandler(Handler):
    def __init__(self):
        super().__init__()
        self.app_logger = AppLogger("discord.py")

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        match record.levelname.upper():
            case "DEBUG":
                self.app_logger.debug(msg, category=AppLogCategory.BOT_DPY)
            case "INFO":
                self.app_logger.info(msg, category=AppLogCategory.BOT_DPY)
            case "WARNING":
                self.app_logger.warning(msg, category=AppLogCategory.BOT_DPY, log_to_discord=False)
            case "ERROR":
                self.app_logger.error(msg, category=AppLogCategory.BOT_DPY, log_to_discord=False)
            case "CRITICAL":
                self.app_logger.critical(msg, category=AppLogCategory.BOT_DPY)
            case _:
                self.app_logger.info(msg, category=AppLogCategory.BOT_DPY)


class StdoutRedirect:
    def __init__(self, logger: AppLogger, component: str, original_logger: io.TextIOWrapper):
        self.logger = logger
        self.component = component
        self.original_logger = original_logger
        self._buffer = ""

    def write(self, buf):
        self.original_logger.write(buf)
        self.original_logger.flush()

        total = self._buffer + buf
        lines = total.splitlines(True)

        if not total.endswith("\n"):
            self._buffer = lines.pop()
        else:
            self._buffer = ""

        if lines:
            self.log("".join(lines).strip(), category=AppLogCategory.APP_GENERAL, component=self.component)

    def flush(self):
        self.original_logger.flush()

        if self._buffer:
            self.log(self._buffer.strip(), category=AppLogCategory.APP_GENERAL, component=self.component)
            self._buffer = ''

    def log(self, message: str, category: str, component: str):
        if self.component == "stdout":
            self.logger.info(message, category=category, component=component)
        else:
            self.logger.error(message, category=category, component=component)


if REDIRECT_STDOUT_TO_LOGGER:
    sys.stdout = StdoutRedirect(
        logger=AppLogger(component="stdout", log_to_console_default=False),
        component="stdout",
        original_logger=sys.__stdout__
    )
    sys.stderr = StdoutRedirect(
        logger=AppLogger(component="stderr", log_to_console_default=False),
        component="stderr",
        original_logger=sys.__stderr__
    )

console_handler = ConsoleLoggingHandler()
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
))
console_logger = logging.getLogger("ohana")
console_logger.setLevel(logging.INFO)
console_logger.addHandler(console_handler)
