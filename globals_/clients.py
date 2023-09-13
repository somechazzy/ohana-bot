from services.third_party.discord import DiscordClient
from services.background.xp_service import XPService
from services.third_party.firebase import FirebaseService
from services.background.reminder_service import ReminderService
from services.third_party.spotify import SpotifyService
from workers.worker_manager import WorkerManagerService

discord_client = DiscordClient().get_client()
firebase_client = FirebaseService()
reminder_service = ReminderService()
xp_service = XPService()
spotify_service = SpotifyService()
worker_manager_service = WorkerManagerService()
