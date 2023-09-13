import asyncio
from datetime import datetime

import discord

from globals_.constants import BotLogLevel, BackgroundWorker
from internal.bot_logger import InfoLogger, ErrorLogger
from models.reminder import Reminder
from utils.decorators import periodic_worker


class ReminderService:

    def __init__(self):
        from globals_.clients import firebase_client, discord_client
        self.queue = asyncio.PriorityQueue()
        self.firebase_client = firebase_client
        self.discord_client = discord_client

        self.info_logger = InfoLogger(component=self.__class__.__name__)
        self.error_logger = ErrorLogger(component=self.__class__.__name__)

    async def add_reminder(self, timestamp, reason, user_id, db_key=None):
        if not db_key:
            db_key = await self.firebase_client.add_reminder(timestamp=timestamp, user_id=user_id, reason=reason)
        reminder = Reminder(timestamp=timestamp, reason=reason, user_id=user_id, db_key=db_key)
        await self.queue.put(reminder)

    @periodic_worker(name=BackgroundWorker.REMINDER_SERVICE)
    async def run(self):
        reminder = None
        if not self.queue.empty() and (reminder := await self.queue.get()).timestamp <= datetime.utcnow().timestamp():
            asyncio.create_task(self.send_reminder(reminder))
            asyncio.create_task(self.firebase_client.remove_reminder(key=reminder.db_key))
            self.queue.task_done()
        elif reminder:
            await self.queue.put(reminder)

    async def send_reminder(self, reminder):
        try:
            user = await self.discord_client.fetch_user(reminder.user_id)
        except discord.NotFound:
            self.error_logger.log(f"Sending reminder to {reminder.user_id} failed due to not finding the user.",
                                  level=BotLogLevel.MINOR_WARNING)
            return

        minutes_late = int((datetime.utcnow().timestamp() - reminder.timestamp) / 60)
        embed, views = self.get_reminder_embed_and_views(reason=reminder.reason, minutes_late=minutes_late)

        await user.send(embed=embed, view=views)

        self.info_logger.log(f"Sent reminder to {user} ({user.id}) within "
                             f"{round(datetime.utcnow().timestamp() - reminder.timestamp, 2)} seconds.",
                             level=BotLogLevel.MESSAGE_SENT)

    async def restore_reminders(self):
        reminders = await self.firebase_client.get_all_reminders()
        for reminder in reminders:
            reminder_dict = reminder.val()
            db_key = reminder.key()
            timestamp = reminder_dict.get("timestamp",
                                          reminder_dict.get("time_of_duration_end_seconds"))
            reason = reminder_dict.get("reason")
            user_id = reminder_dict.get("user_id")

            await self.add_reminder(timestamp=timestamp, reason=reason, user_id=user_id, db_key=db_key)
        self.info_logger.log(f"Recovered {len(reminders)} reminders.",
                             level=BotLogLevel.BOT_INFO)

    @staticmethod
    def get_reminder_embed_and_views(reason, minutes_late):
        from utils.embed_factory import make_reminder_embed
        from utils.helpers import get_reminder_views
        embed = make_reminder_embed(reason=reason, minutes_late=minutes_late)
        views = get_reminder_views()
        return embed, views
