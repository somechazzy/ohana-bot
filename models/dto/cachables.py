"""
DTOs to be used for frequently accessed DB data.
"""
from datetime import datetime, UTC

from common import NOT_SET_
from constants import ReminderRecurrenceType, ReminderRecurrenceConditionedType, REMINDER_YEAR_DAY_FORMAT, \
    DiscordTimestamp
from models.guild_settings_models import GuildSettings, GuildChannelSettings, GuildAutorole, GuildAutoResponse, \
    GuildRoleMenu, GuildXPSettings, GuildMusicSettings
from models.guild_settings_models import GuildUserXP
from models.user_settings_models import UserReminder, UserReminderRecurrence
from utils.helpers.text_manipulation_helpers import get_days_of_week_from_numbers, get_numbers_with_suffix

NOT_SET = NOT_SET_()


class CachedGuildSettings:
    
    class Autoresponse:
        def __init__(self,
                     guild_auto_response_id: int, trigger: str, response: str,
                     match_type: str, delete_original: bool):
            self.guild_auto_response_id: int = guild_auto_response_id
            self.trigger: str = trigger
            self.response: str = response
            self.match_type: str = match_type  # AutoResponseMatchType
            self.delete_original: bool = delete_original

    class RoleMenu:
        def __init__(self, guild_role_menu_id: int, channel_id: int, message_id: int, menu_type: str, menu_mode: str,
                     role_restriction_description: str | None, restricted_role_ids: set[int]):
            self.guild_role_menu_id: int = guild_role_menu_id
            self.channel_id: int = channel_id
            self.message_id: int = message_id
            self.menu_type: str = menu_type  # RoleMenuType
            self.menu_mode: str = menu_mode  # RoleMenuMode
            self.role_restriction_description: str | None = role_restriction_description
            self.restricted_role_ids: set[int] = restricted_role_ids
            
    class XPSettings:
        def __init__(self, guild_xp_settings_id: int, xp_gain_enabled: bool, xp_gain_timeframe: int,
                     xp_gain_minimum: int, xp_gain_maximum: int, message_count_mode: str, xp_decay_enabled: bool,
                     xp_decay_per_day_percentage: float, xp_decay_grace_period_days: int,
                     booster_xp_gain_multiplier: float, level_up_message_enabled: bool,
                     level_up_message_channel_id: int | None, level_up_message_text: str | None,
                     level_up_message_minimum_level: int, max_level: int | None, stack_level_roles: bool,
                     level_role_earn_message_text: str | None, level_role_ids_map: dict[int, set[int]],
                     ignored_channel_ids: set[int], ignored_role_ids: set[int]):
            self.guild_xp_settings_id: int = guild_xp_settings_id
            self.xp_gain_enabled: bool = xp_gain_enabled
            self.xp_gain_timeframe: int = xp_gain_timeframe
            self.xp_gain_minimum: int = xp_gain_minimum
            self.xp_gain_maximum: int = xp_gain_maximum
            self.message_count_mode: str = message_count_mode  # XPSettingsMessageCountMode
            self.xp_decay_enabled: bool = xp_decay_enabled
            self.xp_decay_per_day_percentage: float = xp_decay_per_day_percentage
            self.xp_decay_grace_period_days: int = xp_decay_grace_period_days
            self.booster_xp_gain_multiplier: float = booster_xp_gain_multiplier
            self.level_up_message_enabled: bool = level_up_message_enabled
            self.level_up_message_channel_id: int | None = level_up_message_channel_id
            self.level_up_message_text: str | None = level_up_message_text
            self.level_up_message_minimum_level: int = level_up_message_minimum_level
            self.max_level: int | None = max_level
            self.stack_level_roles: bool = stack_level_roles
            self.level_role_earn_message_text: str | None = level_role_earn_message_text
            self.level_role_ids_map: dict[int, set[int]] = level_role_ids_map
            self.ignored_channel_ids: set[int] = ignored_channel_ids
            self.ignored_role_ids: set[int] = ignored_role_ids

    def __init__(self, guild_id: int, guild_settings_id: int):
        self.guild_id: int = guild_id
        self.guild_settings_id: int = guild_settings_id
        self.logging_channel_id: int | None = None
        self.music_channel_id: int | None = None
        self.music_header_message_id: int | None = None
        self.music_player_message_id: int | None = None
        self.role_persistence_enabled: bool = False
        self.channel_id_message_limiting_role_id: dict[int, int] = {}
        self.channel_id_is_gallery_channel: dict[int, bool] = {}
        self.autoroles_ids: list[int] = []
        self.auto_responses: list[CachedGuildSettings.Autoresponse] = []
        self.role_menus: list[CachedGuildSettings.RoleMenu] = []
        self._message_id_role_menu_map: dict[int, CachedGuildSettings.RoleMenu] = {}
        self.xp_settings: CachedGuildSettings.XPSettings = ...

        self._cached_at = datetime.now(UTC)
        self._is_stale = False

    @classmethod
    def from_orm_object(cls, guild_settings: GuildSettings) -> 'CachedGuildSettings':
        """
        To be called only when all relations are loaded.
        """
        instance = cls(guild_id=guild_settings.guild_id, guild_settings_id=guild_settings.id)
        instance.set_attributes(
            guild_settings=guild_settings,
            guild_channel_settings=guild_settings.channels_settings,
            guild_autoroles=guild_settings.autoroles,
            guild_auto_responses=guild_settings.auto_responses,
            guild_role_menus=guild_settings.role_menus,
            guild_xp_settings=guild_settings.xp_settings,
            guild_music_settings=guild_settings.music_settings
        )
        return instance

    def set_attributes(self,
                       guild_settings: GuildSettings | NOT_SET_ = NOT_SET,
                       guild_channel_settings: list[GuildChannelSettings] | NOT_SET_ = NOT_SET,
                       guild_autoroles: list[GuildAutorole] | NOT_SET_ = NOT_SET,
                       guild_auto_responses: list[GuildAutoResponse] | NOT_SET_ = NOT_SET,
                       guild_role_menus: list[GuildRoleMenu] | NOT_SET_ = NOT_SET,
                       guild_xp_settings: GuildXPSettings | NOT_SET_ = NOT_SET,
                       guild_music_settings: GuildMusicSettings | NOT_SET_ = NOT_SET) -> 'CachedGuildSettings':
        """
        To be used for updating values directly from ORM objects.
        """
        if guild_settings is not NOT_SET:
            self.logging_channel_id = guild_settings.logging_channel_id
            self.role_persistence_enabled = guild_settings.role_persistence_enabled
        if guild_channel_settings is not NOT_SET:
            self.channel_id_message_limiting_role_id = {}
            self.channel_id_is_gallery_channel = {}
            for channel_setting in guild_channel_settings:
                if channel_setting.message_limiting_role_id:
                    self.channel_id_message_limiting_role_id[channel_setting.channel_id] =\
                        channel_setting.message_limiting_role_id
                if channel_setting.is_gallery_channel:
                    self.channel_id_is_gallery_channel[channel_setting.channel_id] = True
        if guild_autoroles is not NOT_SET:
            self.autoroles_ids = [autorole.role_id for autorole in guild_autoroles]
        if guild_auto_responses is not NOT_SET:
            self.auto_responses = [
                CachedGuildSettings.Autoresponse(
                    guild_auto_response_id=autoresponse.id,
                    trigger=autoresponse.trigger_text,
                    response=autoresponse.response_text,
                    match_type=autoresponse.match_type,
                    delete_original=autoresponse.delete_original
                ) for autoresponse in guild_auto_responses
            ]
        if guild_role_menus is not NOT_SET:
            self.role_menus = [
                CachedGuildSettings.RoleMenu(
                    guild_role_menu_id=role_menu.id,
                    channel_id=role_menu.channel_id,
                    message_id=role_menu.message_id,
                    menu_type=role_menu.menu_type,
                    menu_mode=role_menu.menu_mode,
                    role_restriction_description=role_menu.role_restriction_description,
                    restricted_role_ids={role_menu_role.role_id for role_menu_role in role_menu.restricted_roles}
                ) for role_menu in guild_role_menus
            ]
            self._message_id_role_menu_map = {
                role_menu.message_id: role_menu for role_menu in self.role_menus
            }
        if guild_xp_settings is not NOT_SET:
            level_role_ids_map = dict()
            for level_role in guild_xp_settings.level_roles:
                if level_role.level not in level_role_ids_map:
                    level_role_ids_map[level_role.level] = set()
                level_role_ids_map[level_role.level].add(level_role.role_id)
            self.xp_settings = CachedGuildSettings.XPSettings(
                guild_xp_settings_id=guild_xp_settings.id,
                xp_gain_enabled=guild_xp_settings.xp_gain_enabled,
                xp_gain_timeframe=guild_xp_settings.xp_gain_timeframe,
                xp_gain_minimum=guild_xp_settings.xp_gain_minimum,
                xp_gain_maximum=guild_xp_settings.xp_gain_maximum,
                message_count_mode=guild_xp_settings.message_count_mode,
                xp_decay_enabled=guild_xp_settings.xp_decay_enabled,
                xp_decay_per_day_percentage=guild_xp_settings.xp_decay_per_day_percentage,
                xp_decay_grace_period_days=guild_xp_settings.xp_decay_grace_period_days,
                booster_xp_gain_multiplier=guild_xp_settings.booster_xp_gain_multiplier,
                level_up_message_enabled=guild_xp_settings.level_up_message_enabled,
                level_up_message_channel_id=guild_xp_settings.level_up_message_channel_id,
                level_up_message_text=guild_xp_settings.level_up_message_text,
                level_up_message_minimum_level=guild_xp_settings.level_up_message_minimum_level,
                max_level=guild_xp_settings.max_level,
                stack_level_roles=guild_xp_settings.stack_level_roles,
                level_role_earn_message_text=guild_xp_settings.level_role_earn_message_text,
                level_role_ids_map=level_role_ids_map,
                ignored_channel_ids={channel.channel_id for channel in guild_xp_settings.ignored_channels},
                ignored_role_ids={role.role_id for role in guild_xp_settings.ignored_roles}
            )
        if guild_music_settings is not NOT_SET:
            self.music_channel_id = guild_music_settings.music_channel_id
            self.music_header_message_id = guild_music_settings.music_header_message_id
            self.music_player_message_id = guild_music_settings.music_player_message_id
        return self

    def add_auto_response(self, guild_auto_response_id: int, trigger: str, response: str,
                          match_type: str, delete_original: bool) -> None:
        """
        Adds a new auto-response to the cached settings.
        """
        self.auto_responses.append(
            CachedGuildSettings.Autoresponse(
                guild_auto_response_id=guild_auto_response_id,
                trigger=trigger,
                response=response,
                match_type=match_type,
                delete_original=delete_original
            )
        )

    def remove_auto_response(self, guild_auto_response_id: int):
        """
        Removes an auto-response from the cached settings by its ID.
        """
        self.auto_responses = [
            autoresponse for autoresponse in self.auto_responses
            if autoresponse.guild_auto_response_id != guild_auto_response_id
        ]

    def get_auto_response(self,
                          guild_auto_response_id: int | None = None,
                          trigger: str | None = None) -> 'CachedGuildSettings.Autoresponse | None':
        """
        Retrieves an auto-response by its ID or trigger.
        """
        if guild_auto_response_id is None and trigger is None:
            raise ValueError("Either guild_auto_response_id or trigger must be provided.")
        for autoresponse in self.auto_responses:
            if autoresponse.guild_auto_response_id == guild_auto_response_id or autoresponse.trigger == trigger:
                return autoresponse
        return None

    def add_role_menu(self,
                      guild_role_menu_id: int,
                      channel_id: int,
                      message_id: int,
                      menu_type: str,  # RoleMenuType
                      menu_mode: str,  # RoleMenuMode
                      role_restriction_description: str | None = None,
                      restricted_role_ids: set[int] = None) -> None:
        """
        Adds a new role menu to the cached settings.
        """
        role_menu = CachedGuildSettings.RoleMenu(
            guild_role_menu_id=guild_role_menu_id,
            channel_id=channel_id,
            message_id=message_id,
            menu_type=menu_type,
            menu_mode=menu_mode,
            role_restriction_description=role_restriction_description,
            restricted_role_ids=restricted_role_ids or set()
        )
        self.role_menus.append(role_menu)
        self._message_id_role_menu_map[message_id] = role_menu

    def get_role_menu(self,
                      guild_role_menu_id: int | None = None,
                      message_id: int | None = None) -> 'CachedGuildSettings.RoleMenu | None':
        """
        Retrieves a role menu by its ID or message ID.
        """
        if guild_role_menu_id is None and message_id is None:
            raise ValueError("Either guild_role_menu_id or message_id must be provided.")
        if message_id is not None:
            return self._message_id_role_menu_map.get(message_id)
        for role_menu in self.role_menus:
            if role_menu.guild_role_menu_id == guild_role_menu_id:
                return role_menu
        return None

    @property
    def is_stale(self) -> bool:
        return self._is_stale or \
            (datetime.now(UTC) - self._cached_at).total_seconds() > 60 * 60  # 60 minutes


class CachedReminder:

    class RecurrenceSettings:
        def __init__(self,
                     status: str,  # ReminderRecurrenceStatus.ACTIVE
                     recurrence_type: str,  # ReminderRecurrenceType
                     basic_interval: int | None,
                     basic_interval_unit: str | None,
                     conditioned_type: str | None,  # ReminderRecurrenceConditionedType
                     conditioned_days: list[int],  # 0-31 for days of month, 0-6 for days of week
                     conditioned_year_day: str | None,  # formatted as %B %d (e.g., "January 01")
                     ends_at: datetime | None):  # Optional end date for the recurrence
            self.status: str = status
            self.recurrence_type: str = recurrence_type  # ReminderRecurrenceType
            self.basic_interval: int | None = basic_interval
            self.basic_interval_unit: str | None = basic_interval_unit
            self.conditioned_type: str | None = conditioned_type
            self.conditioned_days: list[int] = conditioned_days
            self.conditioned_year_day: str | None = conditioned_year_day
            self.ends_at: datetime | None = ends_at

        @property
        def is_conditioned(self):
            return self.recurrence_type == ReminderRecurrenceType.CONDITIONED

        @property
        def is_basic(self):
            return self.recurrence_type == ReminderRecurrenceType.BASIC

        def __str__(self) -> str:
            str_ = "Every "
            if self.is_basic:
                str_ += f"{self.basic_interval} {self.basic_interval_unit.lower()}(s)"
            else:
                if self.conditioned_type == ReminderRecurrenceConditionedType.DAYS_OF_WEEK:
                    days = get_days_of_week_from_numbers(self.conditioned_days)
                    if len(days) > 2:
                        str_ += f"{', '.join(days[:-1])} and {days[-1]}"
                    else:
                        str_ += f"{' and '.join(days)}"
                elif self.conditioned_type == ReminderRecurrenceConditionedType.DAYS_OF_MONTH:
                    days = get_numbers_with_suffix(self.conditioned_days)
                    if len(days) > 2:
                        str_ += f"{', '.join(days[:-1])} and {days[-1]} of the month"
                    else:
                        str_ += f"{' and '.join(days)} of the month"
                elif self.conditioned_type == ReminderRecurrenceConditionedType.DAY_OF_YEAR:
                    formatted_date = datetime.strptime(self.conditioned_year_day,
                                                       REMINDER_YEAR_DAY_FORMAT).strftime("%B %d")
                    str_ += f"{formatted_date} of the year"

            if self.ends_at:
                str_ += f" until {DiscordTimestamp.SHORT_DATE_TIME.format(timestamp=int(self.ends_at.timestamp()))}."

            return str_ + "."

        @staticmethod
        def get_recurrence_descriptor_from_orm_object(recurrence: UserReminderRecurrence | None) -> str:
            if not recurrence:
                return "Not set"
            recurrence_settings = CachedReminder.RecurrenceSettings(
                status=recurrence.status,
                recurrence_type=recurrence.recurrence_type,
                basic_interval=recurrence.basic_interval,
                basic_interval_unit=recurrence.basic_unit,
                conditioned_type=recurrence.conditioned_type,
                conditioned_days=recurrence.conditioned_days,
                conditioned_year_day=recurrence.conditioned_year_day,
                ends_at=recurrence.ends_at
            )
            return str(recurrence_settings)

    def __init__(self,
                 user_reminder_id: int,
                 owner_user_id: int,
                 recipient_user_id: int,
                 reminder_text: str,
                 reminder_time: datetime,
                 was_snoozed: bool,
                 recurrence: RecurrenceSettings | None):
        self.user_reminder_id: int = user_reminder_id
        self.owner_user_id: int = owner_user_id
        self.recipient_user_id: int = recipient_user_id
        self.reminder_text: str = reminder_text
        self.reminder_time: datetime = reminder_time
        self.was_snoozed: bool = was_snoozed
        self.recurrence: CachedReminder.RecurrenceSettings | None = recurrence

    @classmethod
    def from_orm_object(cls, reminder: UserReminder) -> 'CachedReminder':
        recurrence = cls.RecurrenceSettings(
            status=reminder.recurrence.status,
            recurrence_type=reminder.recurrence.recurrence_type,
            basic_interval=reminder.recurrence.basic_interval,
            basic_interval_unit=reminder.recurrence.basic_unit,
            conditioned_type=reminder.recurrence.conditioned_type,
            conditioned_days=reminder.recurrence.conditioned_days,
            conditioned_year_day=reminder.recurrence.conditioned_year_day,
            ends_at=reminder.recurrence.ends_at if reminder.recurrence else None
        ) if reminder.recurrence else None
        return cls(
            user_reminder_id=reminder.id,
            owner_user_id=reminder.owner.user_id,
            recipient_user_id=reminder.recipient.user_id,
            reminder_text=reminder.reminder_text,
            reminder_time=reminder.reminder_time,
            was_snoozed=reminder.is_snoozed,
            recurrence=recurrence
        )

    def __lt__(self, other: 'CachedReminder'):
        return self.reminder_time < other.reminder_time

    def __gt__(self, other: 'CachedReminder'):
        return self.reminder_time > other.reminder_time

    def __eq__(self, other):
        return self.user_reminder_id == other.user_reminder_id

    def __hash__(self):
        return hash(self.user_reminder_id)

    @property
    def is_relayed(self) -> bool:
        return self.owner_user_id != self.recipient_user_id

    @property
    def clean_reminder_text(self) -> str:
        """
        Returns the reminder text without any accents (`).
        """
        return self.reminder_text.replace('`', '\'').strip()

    def update_from_orm_object(self, reminder: UserReminder) -> None:
        self.user_reminder_id = reminder.id
        self.owner_user_id = reminder.owner.user_id
        self.recipient_user_id = reminder.recipient.user_id
        self.reminder_text = reminder.reminder_text
        self.reminder_time = reminder.reminder_time
        self.was_snoozed = reminder.is_snoozed
        self.recurrence = self.RecurrenceSettings(
            status=reminder.recurrence.status,
            recurrence_type=reminder.recurrence.recurrence_type,
            basic_interval=reminder.recurrence.basic_interval,
            basic_interval_unit=reminder.recurrence.basic_unit,
            conditioned_type=reminder.recurrence.conditioned_type,
            conditioned_days=reminder.recurrence.conditioned_days,
            conditioned_year_day=reminder.recurrence.conditioned_year_day,
            ends_at=reminder.recurrence.ends_at if reminder.recurrence else None
        ) if reminder.recurrence else None


class CachedGuildXP:

    class MemberXP:
        def __init__(self, guild_xp: 'CachedGuildXP', user_id: int, user_username: str, xp: int, level: int,
                     message_count: int, latest_gain_time: datetime, latest_level_up_message_time: datetime | None,
                     decayed_xp: int, latest_decay_time: datetime | None, latest_message_time: datetime):
            self.guild_xp: 'CachedGuildXP' = guild_xp  # backref just in case
            self.user_id: int = user_id
            self.user_username: str = user_username
            self.xp: int = xp
            self.level: int = level
            self.message_count: int = message_count
            self.latest_gain_time: datetime = latest_gain_time
            self.latest_level_up_message_time: datetime | None = latest_level_up_message_time
            self.decayed_xp: int = decayed_xp
            self.latest_decay_time: datetime | None = latest_decay_time
            self.latest_message_time: datetime = latest_message_time

            self._is_synced: bool = True

        @property
        def is_synced(self) -> bool:
            return self._is_synced

        @is_synced.setter
        def is_synced(self, value: bool):
            self._is_synced = value
            if self.guild_xp.is_synced and not self._is_synced:
                self.guild_xp.is_synced = False

        def set_sync_status(self, is_synced: bool) -> None:
            """
            Callable setter needed for some logic.
            """
            self.is_synced = is_synced

        def decay_xp(self, amount: int, new_level: int | None = None):
            self.decayed_xp += amount
            self.latest_decay_time = datetime.now(UTC)
            self.xp -= amount
            if new_level is not None:
                self.level = new_level
            if self.xp < 0:
                self.xp = 0
            self.is_synced = False

        def gain_xp(self, amount: int, new_level: int | None = None):
            self.xp += amount
            if new_level is not None:
                self.level = new_level
            self.latest_gain_time = datetime.now(UTC)
            self.is_synced = False

        def register_message(self, message_time: datetime | None = None):
            self.message_count += 1
            self.latest_message_time = message_time or datetime.now(UTC)
            self.is_synced = False

        def offset_xp(self, amount: int, new_level: int | None = None):
            self.xp += amount
            if new_level is not None:
                self.level = new_level
            if self.xp < 0:
                self.xp = 0
            self.is_synced = False

        def register_level_up_message(self):
            self.latest_level_up_message_time = datetime.now(UTC)
            self.is_synced = False

        @classmethod
        def from_orm_object(cls, guild_xp: 'CachedGuildXP',
                            guild_user_xp: GuildUserXP) -> 'CachedGuildXP.MemberXP':
            return cls(
                guild_xp=guild_xp,
                user_id=guild_user_xp.user_id,
                user_username=guild_user_xp.user_username,
                xp=guild_user_xp.xp,
                level=guild_user_xp.level,
                message_count=guild_user_xp.message_count,
                latest_gain_time=guild_user_xp.latest_gain_time,
                latest_level_up_message_time=guild_user_xp.latest_level_up_message_time,
                decayed_xp=guild_user_xp.decayed_xp,
                latest_decay_time=guild_user_xp.latest_decay_time,
                latest_message_time=guild_user_xp.latest_message_time
            )

    def __init__(self, guild_id: int, guild_settings_id: int):
        self.guild_id: int = guild_id
        self.guild_settings_id: int = guild_settings_id
        self._member_xps: list[CachedGuildXP.MemberXP] = None  # noqa: to be set later
        self._member_id_member_xp_map: dict[int, CachedGuildXP.MemberXP] = {}

        self._is_synced: bool = True

    @property
    def is_synced(self) -> bool:
        return self._is_synced

    @is_synced.setter
    def is_synced(self, value: bool):
        self._is_synced = value

    @property
    def member_count(self) -> int:
        """
        Returns the total number of members with XP in the guild.
        """
        return len(self._member_xps)

    def get_xp_for(self, user_id: int) -> 'CachedGuildXP.MemberXP':
        return self._member_id_member_xp_map.get(user_id)

    def initiate_member_xp(self, user_id: int, user_username: str) -> 'CachedGuildXP.MemberXP':
        """
        Initiates a new member XP entry for the given user.
        """
        if user_id in self._member_id_member_xp_map:
            raise ValueError(f"Member XP for user {user_id} already exists.")
        if not user_username:
            raise ValueError("user_username must be provided.")

        member_xp = CachedGuildXP.MemberXP(
            guild_xp=self,
            user_id=user_id,
            user_username=user_username,
            xp=0,
            level=0,
            message_count=0,
            latest_gain_time=datetime.now(UTC),
            latest_level_up_message_time=None,
            decayed_xp=0,
            latest_decay_time=None,
            latest_message_time=datetime.now(UTC)
        )
        self._member_xps.append(member_xp)
        self._member_id_member_xp_map[user_id] = member_xp
        member_xp.is_synced = False
        return member_xp

    def get_unsynced_xps(self) -> list['CachedGuildXP.MemberXP']:
        """
        Returns a list of member XPs that are not synced with the database.
        """
        if self.is_synced:
            return []
        return [member_xp for member_xp in self._member_xps if not member_xp.is_synced]

    def get_xps_with_last_message_time_before(self, time: datetime) -> list['CachedGuildXP.MemberXP']:
        """
        Returns a list of member XPs that have their last message time before the given time.
        """
        return [member_xp for member_xp in self._member_xps if member_xp.latest_message_time < time]

    def resort_members_by_xp(self):
        """
        Resorts the member XP list by XP in descending order.
        """
        self._member_xps.sort(key=lambda member_xp: member_xp.xp, reverse=True)

    def get_members_xp_page(self, page: int, page_size: int = 10) -> list['CachedGuildXP.MemberXP']:
        """
        Returns a paginated list of member XPs sorted by XP in descending order.
        """
        self.resort_members_by_xp()
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        return self._member_xps[start_index:end_index]

    def get_rank_for(self, member_id: int, resort_members: bool = True) -> int:
        """
        Returns the rank of the member in the guild based on their XP.
        """
        if member_id not in self._member_id_member_xp_map:
            return len(self._member_xps) + 1
        if resort_members:
            self._member_xps.sort(key=lambda member_xp: member_xp.xp, reverse=True)
        sorted_member_ids = [member_xp.user_id for member_xp in self._member_xps]
        return sorted_member_ids.index(member_id) + 1

    @classmethod
    def from_orm_objects(cls, guild_id, guild_settings_id, guild_user_xps: list[GuildUserXP]) -> 'CachedGuildXP':
        """
        Creates a CachedGuildXP instance from ORM objects.
        """
        instance = cls(guild_id=guild_id, guild_settings_id=guild_settings_id)
        instance._member_xps = [
            CachedGuildXP.MemberXP.from_orm_object(guild_xp=instance, guild_user_xp=guild_user_xp)
            for guild_user_xp in guild_user_xps
        ]
        instance._member_id_member_xp_map = {member_xp.user_id: member_xp for member_xp in instance._member_xps}
        return instance
