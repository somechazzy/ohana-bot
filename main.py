"""
Application entry point
"""
from bot.events import register_event_handlers
from bot.discord_service import DiscordService
from system.db_migrations import apply_db_migrations
from system.extensions_management import load_extensions
from system.checks import run_pre_startup_checks

run_pre_startup_checks()
apply_db_migrations()
load_extensions()
register_event_handlers()

DiscordService.run_client()
