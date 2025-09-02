import asyncio
from collections import defaultdict
from datetime import datetime, UTC, timedelta

from common.app_logger import AppLogger
from common.decorators import periodic_worker, require_db_session
from common.exceptions import UserReadableException
from components.user_settings_components.user_reminder_component import UserReminderComponent
from constants import BackgroundWorker
from models.dto.cachables import CachedReminder


class ReminderService:
    """
    Service to host the reminder workers.
    """
    _instance: 'ReminderService' = None
    lock = asyncio.Lock()

    def __init__(self):
        super().__init__()
        self.reminder_component = UserReminderComponent()
        self._queue: asyncio.PriorityQueue['CachedReminder'] = asyncio.PriorityQueue()
        self._user_id_reminder_map: dict[int, set[CachedReminder]] = defaultdict(set)
        self._reminder_id_reminder_map: dict[int, CachedReminder] = {}
        self.logger = AppLogger(self.__class__.__name__)

    def __new__(cls, *args, **kwargs) -> 'ReminderService':
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @require_db_session
    @periodic_worker(name=BackgroundWorker.REMINDER_QUEUE_PRODUCER)
    async def reminder_producer(self):
        """
        Refresh queued reminders from the database.
        """
        reminders = await self.reminder_component.get_reminders_before_time(
            before_datetime=datetime.now(UTC) + timedelta(hours=1), load_users=True, load_recurrence=True
        )
        reminder_id_reminder_map = {reminder.id: reminder for reminder in reminders}
        newly_added_reminder_count = 0
        removed_reminder_count = 0
        async with self.lock:
            queued_reminders: list[CachedReminder] = []
            while not self._queue.empty():
                queued_reminders.append(await self._queue.get())
                self._queue.task_done()
            for queued_reminder in queued_reminders:
                if queued_reminder.user_reminder_id not in reminder_id_reminder_map:
                    queued_reminders.remove(queued_reminder)
                    self._user_id_reminder_map[queued_reminder.owner_user_id].discard(queued_reminder)
                    self._reminder_id_reminder_map.pop(queued_reminder.user_reminder_id, None)
                    removed_reminder_count += 1
            for reminder in reminders:
                if reminder.id not in self._reminder_id_reminder_map:
                    cached_reminder = CachedReminder.from_orm_object(reminder)
                    self._reminder_id_reminder_map[reminder.id] = cached_reminder
                    self._user_id_reminder_map[reminder.owner.user_id].add(cached_reminder)
                    await self._queue.put(cached_reminder)
                    newly_added_reminder_count += 1
                else:
                    cached_reminder = self._reminder_id_reminder_map[reminder.id]
                    cached_reminder.update_from_orm_object(reminder)
                    await self._queue.put(cached_reminder)
        if newly_added_reminder_count or removed_reminder_count:
            self.logger.info(
                f"Refreshed reminders: {newly_added_reminder_count} added, {removed_reminder_count} removed."
            )
        else:
            self.logger.debug("No reminders to refresh.")

    @require_db_session
    @periodic_worker(name=BackgroundWorker.REMINDER_QUEUE_CONSUMER, initial_delay=5)
    async def reminder_consumer(self):
        """
        Consume due reminders from the queue and send them.
        """
        reminders_to_send = set()
        async with self.lock:
            while not self._queue.empty():
                if (reminder := await self._queue.get()).reminder_time <= datetime.now(UTC):
                    reminders_to_send.add(reminder)
                    self._queue.task_done()
                else:
                    await self._queue.put(reminder)
                    self._queue.task_done()
                    break
            for reminder in reminders_to_send:
                await self._send_reminder(reminder)

    async def _send_reminder(self, reminder: CachedReminder):
        """
        Send a reminder to the user.
        Args:
            reminder: The reminder to send.
        """
        from bot.utils.bot_actions.utility_actions import send_reminder_to_user, handle_reminder_delivery_failure
        try:
            if reminder.is_relayed:
                await self.reminder_component.validate_relayed_reminder_deliverability(
                    reminder_id=reminder.user_reminder_id
                )
            await send_reminder_to_user(reminder=reminder)
        except Exception as e:
            if not isinstance(e, UserReadableException):
                self.logger.warning(f"Failed to send reminder {reminder.user_reminder_id} "
                                    f"to user {reminder.recipient_user_id}: {e}",
                                    extras={"user_id": reminder.recipient_user_id})
            if reminder.is_relayed:
                await handle_reminder_delivery_failure(reminder=reminder,
                                                       error=e)
        await self.reminder_component.handle_reminder_post_delivery(reminder_id=reminder.user_reminder_id)
