"""
This module is meant to contain various singletons (clients, services, etc...) used throughout the application.
"""
from discord.ext import commands
from models.dto.emoji import EmojiWarehouse
from bot.discord_service import DiscordService
from workers.reminder_workers import ReminderService
from workers.worker_manager import WorkerManagerService
from workers.xp_workers import XPService

discord_client: commands.Bot = DiscordService.get_client()
emojis: EmojiWarehouse = EmojiWarehouse()
worker_manager_service: WorkerManagerService = WorkerManagerService()
reminder_service: ReminderService = ReminderService()
xp_service: XPService = XPService()
