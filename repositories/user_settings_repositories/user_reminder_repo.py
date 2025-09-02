from datetime import datetime
from typing import Iterable, Any

from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload, contains_eager, load_only

from constants import ReminderRecurrenceStatus, ReminderStatus
from models.user_settings_models import UserSettings, UserReminder, UserReminderRecurrence, UserReminderBlockedUser
from repositories import BaseRepo


class UserReminderRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_reminder(self,
                              owner_user_settings_id: int,
                              recipient_user_settings_id: int,
                              reminder_text: str,
                              reminder_time: datetime,
                              is_snoozed: bool = False,
                              snoozed_from_reminder_id: int | None = None,
                              status: str = ReminderStatus.ACTIVE) -> UserReminder:
        """
        Create reminder for a user.
        """
        user_settings = UserReminder(
            owner_user_settings_id=owner_user_settings_id,
            recipient_user_settings_id=recipient_user_settings_id,
            reminder_text=reminder_text,
            reminder_time=reminder_time,
            is_snoozed=is_snoozed,
            snoozed_from_reminder_id=snoozed_from_reminder_id,
            status=status,
            recurrence=None
        )
        self._session.add(user_settings)
        await self._session.flush()
        return user_settings

    async def get_user_reminders(self,
                                 user_id: int | None,
                                 user_settings_id: int | None = None,
                                 load_recurrence_settings: bool = False,
                                 load_user_settings: bool = False,
                                 status: str | None = ReminderStatus.ACTIVE) -> list[UserReminder]:
        """
        Get all reminders owned by the specified user.
        """
        if not user_id and not user_settings_id:
            raise ValueError("Either user_id or user_settings_id must be provided.")
        query = select(UserReminder)
        if load_recurrence_settings:
            query = query.options(joinedload(UserReminder.recurrence))
        if load_user_settings:
            if not user_id:
                query = query.options(joinedload(UserReminder.owner))
            else:
                query = query.join(UserSettings, UserReminder.owner_user_settings_id == UserSettings.id) \
                    .options(contains_eager(UserReminder.owner))
            query = query.options(joinedload(UserReminder.recipient))
        if user_id:
            query = query.where(UserSettings.user_id == user_id)
        elif user_settings_id:
            query = query.where(UserReminder.owner_user_settings_id == user_settings_id)
        if status:
            query = query.where(UserReminder.status == status)
        query = query.order_by(UserReminder.reminder_time.asc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_all_reminders_before(self, before_time: datetime,
                                       load_recurrence_settings: bool = False,
                                       load_user_settings: bool = False,
                                       status: str | None = ReminderStatus.ACTIVE) -> list[UserReminder]:
        """
        Get all reminders that are due before the specified time.
        """
        query = select(UserReminder).where(UserReminder.reminder_time < before_time)
        if load_recurrence_settings:
            query = query.options(joinedload(UserReminder.recurrence))
        if load_user_settings:
            query = query.options(joinedload(UserReminder.owner),
                                  joinedload(UserReminder.recipient))
        if status:
            query = query.where(UserReminder.status == status)
        query = query.order_by(UserReminder.reminder_time.asc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def update_reminder(self,
                              reminder_id: int | None = None,
                              reminder: UserReminder | None = None,
                              **update_data) -> None:
        """
        Update a reminder with the given ID using the provided update data.
        """
        if reminder_id:
            await self._session.execute(
                update(UserReminder).where(UserReminder.id == reminder_id).values(**update_data)
            )
            await self._session.flush()
        elif reminder:
            for key, value in update_data.items():
                setattr(reminder, key, value)
            self._session.add(reminder)
            await self._session.flush()
        else:
            raise ValueError("Either reminder_id or reminder must be provided.")

    # noinspection PyTypeChecker
    async def create_reminder_recurrence(self,
                                         user_reminder_id: int,
                                         ends_at: datetime | None,
                                         recurrence_type: str,
                                         basic_interval: bool | None = None,
                                         basic_unit: str | None = None,
                                         status: str = ReminderRecurrenceStatus.ACTIVE,
                                         conditioned_type: str | None = None,
                                         conditioned_days: list[int] | None = None,
                                         conditioned_year_day: str | None = None) -> UserReminderRecurrence:
        """
        Create a recurrence for a user reminder.
        """
        recurrence = UserReminderRecurrence(
            user_reminder_id=user_reminder_id,
            status=status,
            ends_at=ends_at,
            recurrence_type=recurrence_type,
            basic_interval=basic_interval,
            basic_unit=basic_unit,
            conditioned_type=conditioned_type,
            conditioned_days=conditioned_days,
            conditioned_year_day=conditioned_year_day
        )
        self._session.add(recurrence)
        await self._session.flush()
        return recurrence

    async def update_reminder_recurrence(self,
                                         recurrence_id: int | None = None,
                                         reminder_recurrence: UserReminderRecurrence | None = None,
                                         **update_data) -> None:
        """
        Update a reminder recurrence with the given ID using the provided update data.
        """
        if recurrence_id:
            await self._session.execute(
                update(UserReminderRecurrence).where(UserReminderRecurrence.id == recurrence_id).values(**update_data)
            )
            await self._session.flush()
        elif reminder_recurrence:
            for key, value in update_data.items():
                setattr(reminder_recurrence, key, value)
            self._session.add(reminder_recurrence)
            await self._session.flush()
        else:
            raise ValueError("Either recurrence_id or reminder_recurrence must be provided.")

    async def delete_reminder(self, reminder_id: int) -> None:
        """
        Delete a reminder by its ID.
        """
        await self._session.execute(
            select(UserReminder).where(UserReminder.id == reminder_id)
        )
        await self._session.flush()

    async def get_reminder_by_id(self,
                                 reminder_id: int,
                                 load_user_settings: bool = False,
                                 load_recurrence_settings: bool = False) -> UserReminder | None:
        """
        Get a reminder by its ID.
        """
        query = select(UserReminder).where(UserReminder.id == reminder_id)
        if load_user_settings:
            query = query.options(joinedload(UserReminder.owner),
                                  joinedload(UserReminder.recipient))
        if load_recurrence_settings:
            query = query.options(joinedload(UserReminder.recurrence))
        result = await self._session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_user_reminder_blocked_user(self,
                                             user_settings_id: int,
                                             blocked_user_settings_id: int,
                                             only: Iterable[Any] | None = None) -> UserReminderBlockedUser | None:
        """
        Get the record - if exists - of the "blocked user" being blocked by the "user" from relaying reminders.
        """
        query = select(UserReminderBlockedUser).where(
            UserReminderBlockedUser.user_settings_id == user_settings_id,
            UserReminderBlockedUser.blocked_user_settings_id == blocked_user_settings_id
        )
        if only:
            query = query.options(load_only(*only))
        result = await self._session.execute(query)
        return result.unique().scalar_one_or_none()

    # noinspection PyTypeChecker
    async def create_user_reminder_blocked_user(self,
                                                user_settings_id: int,
                                                blocked_user_settings_id: int) -> UserReminderBlockedUser:
        """
        Create a record of the "blocked user" being blocked by the "user" from relaying reminders.
        """
        blocked_user = UserReminderBlockedUser(
            user_settings_id=user_settings_id,
            blocked_user_settings_id=blocked_user_settings_id
        )
        self._session.add(blocked_user)
        await self._session.flush()
        return blocked_user

    async def delete_reminder_recurrence(self, reminder_recurrence_id: int):
        """
        Delete a reminder recurrence by its ID.
        """
        await self._session.execute(
            delete(UserReminderRecurrence).where(UserReminderRecurrence.id == reminder_recurrence_id)
        )
        await self._session.flush()
