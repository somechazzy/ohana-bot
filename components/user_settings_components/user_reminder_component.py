from datetime import datetime, timedelta, UTC

from common.db import get_session
from common.exceptions import UserReadableException
from components.user_settings_components import BaseUserSettingsComponent
from components.user_settings_components.user_settings_component import UserSettingsComponent
from constants import REMINDER_YEAR_DAY_FORMAT, ReminderRecurrenceConditionedType, ReminderStatus, \
    ReminderRecurrenceType, ReminderRecurrenceBasicUnit
from models.user_settings_models import UserReminder, UserReminderRecurrence, UserReminderBlockedUser
from repositories.user_settings_repositories.user_reminder_repo import UserReminderRepo
from repositories.user_settings_repositories.user_settings_repo import UserSettingsRepo
from utils.helpers.datetime_helpers import from_timestamp, get_next_year_day, get_next_weekday, get_next_month_day


class UserReminderComponent(BaseUserSettingsComponent):

    async def create_reminder(self,
                              reminder_text: str,
                              reminder_time: datetime,
                              owner_user_id: int,
                              recipient_user_id: int,
                              is_snoozed: bool = False,
                              snoozed_from_reminder_id: int | None = None) -> UserReminder:
        """
        Create a new reminder for a user.
        Args:
            reminder_text (str): The text of the reminder ('what').
            reminder_time (datetime): Delivery time of the reminder ('when').
            owner_user_id (int): ID of the user who created the reminder.
            recipient_user_id (int): ID of the user who will receive the reminder ('who').
            is_snoozed (bool): Whether the reminder is snoozed.
            snoozed_from_reminder_id (int | None): ID of the reminder from which the snooze was initiated, if any.

        Returns:
            UserReminder: The created reminder object.
        """
        self.logger.debug(f"Creating reminder for user {owner_user_id} "
                          f"to be delivered to {recipient_user_id} at {reminder_time}.")
        user_settings_repo = UserSettingsRepo(session=get_session())
        user_reminder_repo = UserReminderRepo(session=get_session())
        if not (owner_user_settings := await user_settings_repo.get_user_settings_by_user_id(user_id=owner_user_id)):
            owner_user_settings = await UserSettingsComponent().create_default_user_settings(user_id=owner_user_id)
            self.logger.debug(f"Created default user settings for reminder owner {owner_user_id}.")
        if not (recipient_user_settings := await user_settings_repo.get_user_settings_by_user_id(
                user_id=recipient_user_id
        )):
            recipient_user_settings = await UserSettingsComponent().create_default_user_settings(
                user_id=recipient_user_id
            )
            self.logger.debug(f"Created default user settings for reminder recipient {recipient_user_id}.")
        return await user_reminder_repo.create_reminder(owner_user_settings_id=owner_user_settings.id,
                                                        recipient_user_settings_id=recipient_user_settings.id,
                                                        reminder_text=reminder_text,
                                                        reminder_time=reminder_time,
                                                        is_snoozed=is_snoozed,
                                                        snoozed_from_reminder_id=snoozed_from_reminder_id)

    async def get_user_reminders(self, user_id: int) -> list[UserReminder]:
        """
        Get all reminders for a user.
        Args:
            user_id (int): ID of the user whose reminders are to be fetched.

        Returns:
            list[UserReminder]: List of reminders for the user.
        """
        self.logger.debug(f"Fetching reminders for user {user_id}.")
        user_reminder_repo = UserReminderRepo(session=get_session())
        return await user_reminder_repo.get_user_reminders(user_id=user_id,
                                                           load_user_settings=True,
                                                           load_recurrence_settings=True)

    async def delete_reminder(self, reminder_id: int):
        """
        Delete a reminder by its ID.
        Args:
            reminder_id (int): ID of the reminder to be deleted.
        """
        self.logger.debug(f"Deleting reminder with ID {reminder_id}.")
        user_reminder_repo = UserReminderRepo(session=get_session())
        await user_reminder_repo.delete_reminder(reminder_id=reminder_id)

    async def update_reminder(self,
                              reminder_id: int | None = None,
                              reminder: UserReminder | None = None,
                              reminder_text: str | None = None,
                              reminder_time: datetime | None = None,
                              is_snoozed: bool | None = None,
                              status: bool | None = None):
        """
        Update a reminder's details. Either `reminder_id` or `reminder` must be provided.
        Args:
            reminder_id (int | None): ID of the reminder to update.
            reminder (UserReminder | None): The reminder object to update.
            reminder_text (str | None): New text for the reminder.
            reminder_time (datetime | None): New delivery time for the reminder.
            is_snoozed (bool | None): Whether the reminder is snoozed or not.
            status (bool | None): New status for the reminder - ReminderStatus.
        """
        self.logger.debug(f"Updating reminder with ID {reminder_id or reminder.id}.")
        if not reminder_id and not reminder:
            raise ValueError("Either 'reminder_id' or 'reminder' must be provided.")
        user_reminder_repo = UserReminderRepo(session=get_session())
        update_data = {}
        if reminder_text is not None:
            update_data['reminder_text'] = reminder_text
        if reminder_time is not None:
            update_data['reminder_time'] = reminder_time
        if is_snoozed is not None:
            update_data['is_snoozed'] = is_snoozed
        if status is not None:
            update_data['status'] = status

        await user_reminder_repo.update_reminder(reminder_id=reminder_id, reminder=reminder, **update_data)

    async def set_reminder_recurrence(self,
                                      recurrence_type: str | None,
                                      reminder: UserReminder,
                                      ends_at: datetime | None = None,
                                      basic_interval: int | None = None,
                                      basic_unit: str | None = None,
                                      conditioned_type: str | None = None,
                                      conditioned_days: list[int] | None = None) -> UserReminderRecurrence | None:
        """
        Set the recurrence settings for a reminder.
        Args:
            recurrence_type (str | None): Type of recurrence - ReminderRecurrenceType. Pass none to delete recurrence.
            reminder (UserReminder): The reminder object to set recurrence for.
            ends_at (datetime | None): The end time for the recurrence.
            basic_interval (int | None): The basic interval for the recurrence.
            basic_unit (str | None): The unit of the basic interval - ReminderRecurrenceBasicUnit.
            conditioned_type (str | None): Type of conditioned recurrence - ReminderRecurrenceConditionedType.
            conditioned_days (list[int] | None): List of days for conditioned recurrence (0-6 weekdays, 1-31 monthdays).

        Returns:
            UserReminderRecurrence | None: The created/updated recurrence settings for the reminder. None if deleted.
        """
        self.logger.debug(f"Setting recurrence for reminder {reminder.id} wih recurrence type {recurrence_type}.")
        year_day = None
        repo = UserReminderRepo(session=get_session())
        if recurrence_type == ReminderRecurrenceType.BASIC:
            if not basic_interval or not basic_unit:
                raise ValueError("For BASIC recurrence type, basic_interval and basic_unit must be provided.")
        elif recurrence_type == ReminderRecurrenceType.CONDITIONED:
            if not conditioned_type:
                raise ValueError("For CONDITIONED recurrence type, conditioned_type must be provided.")
            if conditioned_type == ReminderRecurrenceConditionedType.DAY_OF_YEAR:
                year_day = from_timestamp(utc_timestamp=reminder.reminder_time.timestamp(),
                                          timezone=reminder.owner.timezone).strftime(REMINDER_YEAR_DAY_FORMAT)
            elif not conditioned_days:
                raise ValueError("For CONDITIONED recurrence type other than DAY_OF_YEAR, "
                                 "conditioned_days must be provided.")
        else:
            self.logger.debug(f"Removing recurrence for reminder {reminder.id}.")
            await repo.delete_reminder_recurrence(reminder_recurrence_id=reminder.recurrence.id)
            reminder.recurrence = None
            return
        if reminder.recurrence:
            await self._update_reminder_recurrence(
                reminder_recurrence=reminder.recurrence,
                recurrence_type=recurrence_type,
                ends_at=ends_at,
                basic_interval=basic_interval,
                basic_unit=basic_unit,
                conditioned_type=conditioned_type,
                conditioned_days=conditioned_days,
                conditioned_year_day=year_day
            )
            return reminder.recurrence
        recurrence = await repo.create_reminder_recurrence(
            user_reminder_id=reminder.id,
            recurrence_type=recurrence_type,
            ends_at=ends_at,
            basic_interval=basic_interval,
            basic_unit=basic_unit,
            conditioned_type=conditioned_type,
            conditioned_days=conditioned_days,
            conditioned_year_day=year_day
        )
        reminder.recurrence = recurrence
        if reminder.status == ReminderStatus.ARCHIVED:
            await repo.update_reminder(reminder_id=reminder.id, status=ReminderStatus.ACTIVE)
        if reminder.reminder_time <= datetime.now(UTC):
            await self.handle_reminder_post_delivery(reminder_id=reminder.id)
        return recurrence

    async def _update_reminder_recurrence(self,
                                          reminder_recurrence: UserReminderRecurrence,
                                          recurrence_type: str,
                                          ends_at: datetime | None = None,
                                          basic_interval: int | None = None,
                                          basic_unit: str | None = None,
                                          conditioned_type: str | None = None,
                                          conditioned_days: list[int] | None = None,
                                          conditioned_year_day: str | None = None):
        """
        Set the recurrence settings for a reminder.
        Args:
            reminder_recurrence (UserReminderRecurrence): The recurrence object to update.
            recurrence_type (str): Type of recurrence - ReminderRecurrenceType.
            ends_at (datetime | None): The end time for the recurrence.
            basic_interval (int | None): The basic interval for the recurrence.
            basic_unit (str | None): The unit of the basic interval - ReminderRecurrenceBasicUnit.
            conditioned_type (str | None): Type of conditioned recurrence - ReminderRecurrenceConditionedType.
            conditioned_days (list[int] | None): List of days for conditioned recurrence (0-6 weekdays, 1-31 monthdays).
            conditioned_year_day (str | None): Year day for DAY_OF_YEAR conditioned recurrence.
        """
        self.logger.debug(f"Updating recurrence for reminder {reminder_recurrence.user_reminder_id}.")
        repo = UserReminderRepo(session=get_session())
        await repo.update_reminder_recurrence(
            reminder_recurrence=reminder_recurrence,
            recurrence_type=recurrence_type,
            ends_at=ends_at,
            basic_interval=basic_interval,
            basic_unit=basic_unit,
            conditioned_type=conditioned_type,
            conditioned_days=sorted(conditioned_days) if conditioned_days else conditioned_days,
            conditioned_year_day=conditioned_year_day,
        )

    async def get_reminders_before_time(self,
                                        before_datetime: datetime,
                                        load_users: bool = True,
                                        load_recurrence: bool = True) -> list[UserReminder]:
        """
        Get all reminders that are scheduled to be delivered before a specific datetime.
        Args:
            before_datetime (datetime): The datetime before which reminders' reminder_time should be.
            load_users (bool): Whether to load owner and recipient user settings.
            load_recurrence (bool): Whether to load recurrence settings for the reminders.

        Returns:
            list[UserReminder]: List of reminders that match the criteria.
        """
        self.logger.debug(f"Getting reminders scheduled to deliver before {before_datetime}.")
        user_reminder_repo = UserReminderRepo(session=get_session())
        return await user_reminder_repo.get_all_reminders_before(before_time=before_datetime,
                                                                 load_user_settings=load_users,
                                                                 load_recurrence_settings=load_recurrence)

    async def validate_relayed_reminder_deliverability(self, reminder_id: int):
        """ 
        Checks if the owner can relay reminders in general and specifically to this recipient.
        Also checks if the recipient accepts relayed reminders.
        Args:
            reminder_id (int): ID of the reminder to check.

        Raises:
            UserReadableException: if the reminder cannot be relayed.
        """
        self.logger.debug(f"Validating deliverability of relayed reminder with ID {reminder_id}.")
        repo = UserReminderRepo(session=get_session())
        reminder = await self.get_reminder(reminder_id=reminder_id, load_user_settings=True)
        if not reminder:
            raise ValueError(f"Reminder with ID {reminder_id} not found.")
        if reminder.owner.blocked_from_relaying_reminders:
            raise UserReadableException("You have been blocked from relaying reminders to other users.")
        if reminder.recipient.relayed_reminders_disabled:
            raise UserReadableException("The recipient has disabled receiving relayed reminders.")
        reminder_blocked_user = await repo.get_user_reminder_blocked_user(user_settings_id=reminder.recipient.id,
                                                                          blocked_user_settings_id=reminder.owner.id,
                                                                          only=(UserReminderBlockedUser.id, ))
        if reminder_blocked_user:
            raise UserReadableException("You have been blocked by the recipient from relaying reminders to them.")

    async def handle_reminder_post_delivery(self, reminder_id: int):
        """
        Handle post-delivery actions for a reminder, such as updating its status and next delivery time if recurring.
        Args:
            reminder_id (int): ID of the reminder.
        """
        self.logger.debug(f"Handling post-delivery for reminder with ID {reminder_id}.")
        repo = UserReminderRepo(session=get_session())
        reminder = await self.get_reminder(reminder_id=reminder_id,
                                           load_user_settings=True,
                                           load_recurrence_settings=True)
        if not reminder.recurrence:
            await repo.update_reminder(reminder_id=reminder_id, status=ReminderStatus.ARCHIVED)
            return

        next_delivery_at = reminder.reminder_time
        # while loop is necessary for the case of app downtime, to avoid repeating reminders that are already due
        while next_delivery_at <= datetime.now(UTC):
            if reminder.recurrence.recurrence_type == ReminderRecurrenceType.BASIC:
                next_delivery_at = self._get_basic_next_delivery_at(reminder=reminder)
            elif reminder.recurrence.recurrence_type == ReminderRecurrenceType.CONDITIONED:
                try:
                    next_delivery_at = self._get_conditioned_next_delivery_at(reminder=reminder)
                except Exception as e:
                    self.logger.error(f"Error while trying to get next_delivery_at for reminder"
                                      f" {reminder.id}. Setting reminder to archived and awaiting manual action. "
                                      f"Error: {e}")
                    await repo.update_reminder(reminder_id=reminder.id, status=ReminderStatus.ARCHIVED)
                    return
            else:
                raise ValueError("Reminder recurrence settings must have either basic or conditioned details.")
            reminder.reminder_time = next_delivery_at
            self.logger.debug(f"Next delivery time for reminder {reminder_id} is {next_delivery_at}.")

        if reminder.recurrence.ends_at and next_delivery_at > reminder.recurrence.ends_at:
            self.logger.debug(f"Next delivery time {next_delivery_at} is after the recurrence ends at "
                              f"{reminder.recurrence.ends_at}. Archiving reminder {reminder_id}.")
            await repo.update_reminder(reminder_id=reminder_id, status=ReminderStatus.ARCHIVED)
            return

        await repo.update_reminder(reminder_id=reminder_id,
                                   reminder_time=next_delivery_at)

    def _get_basic_next_delivery_at(self, reminder: UserReminder) -> datetime:
        """
        Calculate the next delivery time for a reminder with basic recurrence settings.
        Args:
            reminder (UserReminder): The reminder object with basic recurrence settings.

        Returns:
            datetime: The next delivery time for the reminder.
        """
        self.logger.debug(f"Calculating next delivery time for reminder {reminder.id} with basic recurrence settings.")
        match reminder.recurrence.basic_unit:
            case ReminderRecurrenceBasicUnit.HOUR:
                return reminder.reminder_time + timedelta(hours=reminder.recurrence.basic_interval)
            case ReminderRecurrenceBasicUnit.DAY:
                return reminder.reminder_time + timedelta(days=reminder.recurrence.basic_interval)
            case _:
                raise ValueError(f"Unsupported basic interval unit {reminder.recurrence.basic_unit}.")

    def _get_conditioned_next_delivery_at(self, reminder: UserReminder, recursive_limit=5,
                                          recursion_resolving_reference=None) -> datetime:
        """
        Calculate the next delivery time for a reminder with conditioned recurrence settings.
        Args:
            reminder (UserReminder): The reminder object with conditioned recurrence settings.

        Returns:
            datetime: The next delivery time for the reminder.
        """
        self.logger.debug(f"Calculating next delivery time for reminder "
                          f"{reminder.id} with conditioned recurrence settings.")
        localized_deliver_at = from_timestamp(utc_timestamp=int(reminder.reminder_time.timestamp()),
                                              timezone=reminder.owner.timezone)
        recursion_resolving_reference = recursion_resolving_reference or {}
        if reminder.recurrence.conditioned_type == ReminderRecurrenceConditionedType.DAY_OF_YEAR:
            next_delivery_at = get_next_year_day(
                from_datetime=localized_deliver_at,
                year_day=reminder.recurrence.conditioned_year_day
            )
        elif reminder.recurrence.conditioned_type == ReminderRecurrenceConditionedType.DAYS_OF_WEEK:
            condition_days = sorted(reminder.recurrence.conditioned_days)
            if len(condition_days) == 1 or condition_days[-1] <= localized_deliver_at.weekday():
                next_weekday = condition_days[0]
            else:
                next_weekday = condition_days[i := 0]
                while next_weekday <= localized_deliver_at.weekday():
                    next_weekday = condition_days[i := i + 1]
            next_delivery_at = get_next_weekday(from_datetime=localized_deliver_at,
                                                weekday=next_weekday)
        elif reminder.recurrence.conditioned_type == ReminderRecurrenceConditionedType.DAYS_OF_MONTH:
            days_to_skip = recursion_resolving_reference.get("days_to_skip", set())
            condition_days = sorted(reminder.recurrence.conditioned_days)
            for day_to_skip in days_to_skip:
                condition_days.remove(day_to_skip) if day_to_skip in condition_days else None
            if not condition_days:  # ideally should never happen
                self.logger.error(f"It happened... reminder {reminder.id}")
                next_month_day = reminder.recurrence.conditioned_days[0]
            else:
                if len(condition_days) == 1 or condition_days[-1] <= localized_deliver_at.day:
                    next_month_day = condition_days[0]
                else:
                    next_month_day = condition_days[i := 0]
                    while next_month_day <= localized_deliver_at.day:
                        next_month_day = condition_days[i := i + 1]
            next_delivery_at = get_next_month_day(from_datetime=localized_deliver_at,
                                                  month_day=next_month_day)
            recursion_resolving_reference["days_to_skip"] = ({next_month_day}
                                                             | recursion_resolving_reference.get("days_to_skip", set()))
            next_delivery_at = from_timestamp(utc_timestamp=int(next_delivery_at.timestamp()))
        else:
            raise ValueError(f"Unsupported reminder condition type {reminder.recurrence.conditioned_type}.")

        if next_delivery_at == reminder.reminder_time:
            # purpose of recursion logic: example: if there are days set to 28, 29, 30, 31, and it's a non-leap feb,
            # the reminder will send 4 times at once, need to check if new delivery_at is the same and skip accordingly
            if recursive_limit == 0:
                raise RecursionError("Recursion limit reached.")
            next_delivery_at = self._get_conditioned_next_delivery_at(
                reminder=reminder,
                recursive_limit=recursive_limit - 1,
                recursion_resolving_reference=recursion_resolving_reference
            )

        return from_timestamp(next_delivery_at.timestamp())  # return as UTC for DB storage

    async def block_user_from_relaying_reminders(self, user_id: int, blocked_user_id: int):
        """
        Block a user from relaying reminders to another user.
        Args:
            user_id (int): ID of the user who is blocking.
            blocked_user_id (int): ID of the user to be blocked from relaying reminders.
        """
        self.logger.debug(f"Blocking user {blocked_user_id} from relaying reminders to user {user_id}.")
        user_settings_component = UserSettingsComponent()
        repo = UserReminderRepo(session=get_session())
        if not (user_settings := await user_settings_component.get_user_settings(user_id=user_id)):
            raise ValueError(f"User with ID {user_id} not found.")
        elif not (blocked_user_settings := await user_settings_component.get_user_settings(
                user_id=blocked_user_id)):
            raise ValueError(f"Blocked user with ID {blocked_user_id} not found.")
        if not await repo.get_user_reminder_blocked_user(user_settings_id=user_settings.id,
                                                         blocked_user_settings_id=blocked_user_settings.id):
            await repo.create_user_reminder_blocked_user(user_settings_id=user_settings.id,
                                                         blocked_user_settings_id=blocked_user_settings.id)
            self.logger.debug(f"User {blocked_user_id} has been blocked from relaying reminders to user {user_id}.")

    async def get_reminder(self,
                           reminder_id: int,
                           load_user_settings: bool = False,
                           load_recurrence_settings: bool = False) -> UserReminder:
        """
        Get a reminder by its ID, optionally loading user and recurrence settings.
        Args:
            reminder_id (int): ID of the reminder to fetch.
            load_user_settings (bool): Whether to load user settings for the reminder owner and recipient.
            load_recurrence_settings (bool): Whether to load recurrence settings for the reminder.

        Returns:
            UserReminder: The reminder object.
        """
        self.logger.debug(f"Fetching reminder with ID {reminder_id}.")
        user_reminder_repo = UserReminderRepo(session=get_session())
        return await user_reminder_repo.get_reminder_by_id(reminder_id=reminder_id,
                                                           load_user_settings=load_user_settings,
                                                           load_recurrence_settings=load_recurrence_settings)
