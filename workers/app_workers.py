import gc
import traceback
from datetime import datetime, UTC

import cache
from clients import discord_client
from common.decorators import periodic_worker, require_db_session
from settings import EXTERNAL_LOGGING_ENABLED
from constants import BackgroundWorker, AppLogCategory
from common.http_session import _async_http_sessions, _sync_http_sessions  # noqa


class AppWorkers:
    """
    Miscellaneous background workers for the application.
    """

    def __init__(self):
        self._cache_cleanup_tracker = 0
        self._last_database_backup = 0

        from common.app_logger import AsyncFileLogHandler, DiscordLogHandler, ExternalLogHandler
        self.file_log_handler = AsyncFileLogHandler()
        self.discord_log_handler = DiscordLogHandler()
        self.external_log_handler = ExternalLogHandler()

    @require_db_session
    @periodic_worker(name=BackgroundWorker.CACHE_CLEANUP, initial_delay=30)
    async def cache_cleanup(self):
        """
        Periodically cleans up obsolete cached web responses, idle music services, and other expired resources.
        """
        obsolete_async_session_names = []
        obsolete_sync_session_names = []
        for session_name, (session, expiry) in _async_http_sessions.items():
            if expiry < datetime.now(UTC):
                obsolete_async_session_names.append(session_name)
                await session.close()
        for session_name in obsolete_async_session_names:
            _async_http_sessions.pop(session_name, None)
        for session_name, (session, expiry) in _sync_http_sessions.items():
            if expiry < datetime.now(UTC):
                obsolete_sync_session_names.append(session_name)
                session.close()
        for session_name in obsolete_sync_session_names:
            _sync_http_sessions.pop(session_name, None)

        obsolete_web_responses_keys = []
        for cache_key, cached_response in cache.CACHED_WEB_RESPONSES.items():
            if cached_response.cache_expiry < datetime.now():
                obsolete_web_responses_keys.append(cache_key)
        for cache_key in obsolete_web_responses_keys:
            cache.CACHED_WEB_RESPONSES.pop(cache_key, None)

        guild_music_services_to_kill = set()
        for guild_id, guild_music_service in cache.MUSIC_SERVICES.items():
            if not discord_client.get_guild(guild_id).voice_client:
                guild_music_services_to_kill.add(guild_id)
            cache.MUSIC_SERVICES[guild_id].check_and_update_idle_status()
            if guild_music_service.idle_since \
                    and (datetime.now(UTC) - guild_music_service.idle_since).total_seconds() >= 300:
                guild_music_services_to_kill.add(guild_id)
            else:
                guild_music_service.check_and_update_idle_status()
        for guild_id in guild_music_services_to_kill:
            await cache.MUSIC_SERVICES[guild_id].kill()

        gc.collect()

    @periodic_worker(name=BackgroundWorker.LOG_INGESTION)
    async def log_ingestion(self):
        """
        Periodically ingests log records from the async log queue and processes them for external logging.
        """
        from common.app_logger import async_log_queue, AppLogger, LogRecordData
        logger = AppLogger("AppWorkers.log_ingestion")
        log_records_for_external_logger = []
        while not async_log_queue.empty():
            log_record_data: LogRecordData = await async_log_queue.get()
            log_records_for_external_logger.append(log_record_data)
            async_log_queue.task_done()

            if log_record_data.log_to_file:
                try:
                    await self.file_log_handler.log(log_record_data=log_record_data)
                except Exception as e:
                    logger.critical(F"Failed to log to file: {e}", category=AppLogCategory.APP_GENERAL,
                                    log_to_file=False)

            if log_record_data.log_to_discord and EXTERNAL_LOGGING_ENABLED:
                try:
                    await self.discord_log_handler.log(log_record_data=log_record_data)
                except Exception as e:
                    logger.critical(F"Failed to log to Discord: {e}", category=AppLogCategory.APP_GENERAL,
                                    log_to_discord=False, log_externally=False)

        if log_records_for_external_logger and EXTERNAL_LOGGING_ENABLED:
            try:
                await self.external_log_handler.log(log_records_data=[
                    log_record_data for log_record_data in log_records_for_external_logger
                    if log_record_data.log_externally
                ])
            except Exception as e:
                logger.critical(F"Failed to log externally: {e}\n{traceback.format_exc()}",
                                category=AppLogCategory.APP_GENERAL,
                                log_to_discord=False, log_externally=False)
