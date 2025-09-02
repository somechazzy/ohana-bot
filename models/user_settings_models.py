from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from constants import (AnimangaProvider, UserUsernameProvider, ReminderRecurrenceStatus,
                       ReminderRecurrenceType, ReminderRecurrenceBasicUnit, ReminderRecurrenceConditionedType,
                       ReminderStatus)
from models import BaseModel, BaseModelMixin, SnowflakeID, Json, AwareDateTime


class UserSettings(BaseModel, BaseModelMixin):
    __tablename__ = 'user_settings'

    user_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]
    timezone: Mapped[str] = mapped_column(nullable=True)
    relayed_reminders_disabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    blocked_from_relaying_reminders: Mapped[bool] = mapped_column(default=False, nullable=False)
    preferred_animanga_provider: Mapped[str] = mapped_column(AnimangaProvider.as_orm_enum(),
                                                             default=AnimangaProvider.MAL,
                                                             nullable=False)

    usernames: Mapped[list['UserUsername']] = relationship('UserUsername',
                                                           back_populates='user_settings',
                                                           uselist=True)
    owned_reminders: Mapped[list['UserReminder']] = relationship('UserReminder',
                                                                 back_populates='owner',
                                                                 foreign_keys='UserReminder.owner_user_settings_id',
                                                                 uselist=True)
    received_reminders: Mapped[list['UserReminder']] = relationship(
        'UserReminder',
        back_populates='recipient',
        foreign_keys='UserReminder.recipient_user_settings_id',
        uselist=True
    )


class UserUsername(BaseModel, BaseModelMixin):
    __tablename__ = 'user_username'

    user_settings_id: Mapped[int] = mapped_column(ForeignKey('user_settings.id'),  # type: ignore[arg-type]
                                                  nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    provider: Mapped[str] = mapped_column(UserUsernameProvider.as_orm_enum(), nullable=False)

    user_settings: Mapped['UserSettings'] = relationship('UserSettings',
                                                         back_populates='usernames',
                                                         uselist=True)


class UserReminder(BaseModel, BaseModelMixin):
    __tablename__ = 'user_reminder'

    owner_user_settings_id: Mapped[int] = mapped_column(ForeignKey('user_settings.id'),  # type: ignore[arg-type]
                                                        nullable=False)
    recipient_user_settings_id: Mapped[int] = mapped_column(ForeignKey('user_settings.id'),  # type: ignore[arg-type]
                                                            nullable=False)
    reminder_text: Mapped[str] = mapped_column(nullable=False)
    reminder_time: Mapped[datetime] = mapped_column(AwareDateTime(),  # type: ignore[arg-type]
                                                    nullable=False)
    is_snoozed: Mapped[bool] = mapped_column(default=False, nullable=False)
    snoozed_from_reminder_id: Mapped[int | None] = mapped_column(ForeignKey('user_reminder.id'),  # type: ignore
                                                                 nullable=True)
    status: Mapped[str] = mapped_column(ReminderStatus.as_orm_enum(),
                                        default=ReminderStatus.ACTIVE,
                                        nullable=False)

    owner: Mapped['UserSettings'] = relationship('UserSettings',
                                                 back_populates='owned_reminders',
                                                 foreign_keys=[owner_user_settings_id],
                                                 uselist=False)
    recipient: Mapped['UserSettings'] = relationship('UserSettings',
                                                     back_populates='received_reminders',
                                                     foreign_keys=[recipient_user_settings_id],
                                                     uselist=False)
    recurrence: Mapped['UserReminderRecurrence'] = relationship('UserReminderRecurrence',
                                                                back_populates='reminder',
                                                                uselist=False)
    original_reminder: Mapped['UserReminder'] = relationship('UserReminder',
                                                             foreign_keys=[snoozed_from_reminder_id],
                                                             uselist=False)

    @property
    def is_relayed(self) -> bool:
        return self.owner_user_settings_id != self.recipient_user_settings_id

    @property
    def clean_reminder_text(self) -> str:
        """
        Returns the reminder text without any accents (`).
        """
        return self.reminder_text.replace('`', '\'').strip()


class UserReminderRecurrence(BaseModel, BaseModelMixin):
    __tablename__ = 'user_reminder_recurrence'

    user_reminder_id: Mapped[int] = mapped_column(ForeignKey('user_reminder.id'),  # type: ignore[arg-type]
                                                  nullable=False)
    status: Mapped[str] = mapped_column(ReminderRecurrenceStatus.as_orm_enum(),
                                        default=ReminderRecurrenceStatus.ACTIVE,
                                        nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(AwareDateTime(),  # type: ignore[arg-type]
                                                     nullable=True)
    recurrence_type: Mapped[str] = mapped_column(ReminderRecurrenceType.as_orm_enum(), nullable=False)
    basic_interval: Mapped[int | None] = mapped_column(nullable=True)
    basic_unit: Mapped[str | None] = mapped_column(ReminderRecurrenceBasicUnit.as_orm_enum(), nullable=True)
    conditioned_type: Mapped[str] = mapped_column(ReminderRecurrenceConditionedType.as_orm_enum(), nullable=False)
    conditioned_days: Mapped[list | None] = mapped_column(Json(), nullable=True)  # type: ignore[arg-type]
    conditioned_year_day: Mapped[str | None] = mapped_column(nullable=True)

    reminder: Mapped['UserReminder'] = relationship('UserReminder',
                                                    back_populates='recurrence',
                                                    uselist=False)


class UserReminderBlockedUser(BaseModel, BaseModelMixin):
    __tablename__ = 'user_reminder_blocked_user'

    user_settings_id: Mapped[int] = mapped_column(ForeignKey('user_settings.id'),  # type: ignore[arg-type]
                                                  nullable=False)
    blocked_user_settings_id: Mapped[int] = mapped_column(ForeignKey('user_settings.id'),  # type: ignore[arg-type]
                                                          nullable=False)
    reference_reminder_id: Mapped[int | None] = mapped_column(ForeignKey('user_reminder.id'),  # type: ignore[arg-type]
                                                              nullable=True)
