from typing import Iterable

from sqlalchemy import select, update
from sqlalchemy.orm import load_only, joinedload

from constants import AnimangaProvider
from models.user_settings_models import UserSettings
from repositories import BaseRepo


class UserSettingsRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_user_settings(self,
                                   user_id: int,
                                   timezone: str | None = None,
                                   relayed_reminders_disabled: bool = False,
                                   blocked_from_relaying_reminders: bool = False,
                                   preferred_animanga_provider: str = AnimangaProvider.MAL) -> UserSettings:
        """
        Create settings for a user.
        """
        user_settings = UserSettings(
            user_id=user_id,
            timezone=timezone,
            relayed_reminders_disabled=relayed_reminders_disabled,
            blocked_from_relaying_reminders=blocked_from_relaying_reminders,
            preferred_animanga_provider=preferred_animanga_provider
        )
        self._session.add(user_settings)
        await self._session.flush()
        return user_settings

    async def get_user_settings_by_user_id(self,
                                           user_id: int,
                                           load_reminders: bool = False,
                                           load_usernames: bool = False,
                                           only: Iterable | None = None) -> UserSettings | None:
        """
        Get user settings by user ID.
        """
        load_options = []
        if load_reminders:
            load_options.append(UserSettings.owned_reminders)
            load_options.append(UserSettings.received_reminders)
        if load_usernames:
            load_options.append(UserSettings.usernames)

        query = select(UserSettings) \
            .where(UserSettings.user_id == user_id)
        if load_options:
            query = query.options(joinedload(*load_options))
        if only:
            query = query.options(load_only(*only))

        return (await self._session.execute(query)).unique().scalar_one_or_none()

    async def update_user_settings(self,
                                   user_settings_id: int | None = None,
                                   user_id: int | None = None,
                                   user_settings: UserSettings | None = None,
                                   **kwargs) -> None:
        """
        Update user settings. Must provide either user_settings_id, user_id or user_settings.
        """
        if not any((user_settings_id, user_id, user_settings)):
            raise ValueError("Must provide either user_settings_id, user_id or user_settings.")
        if user_settings_id:
            await self._session.execute(
                update(UserSettings).where(UserSettings.id == user_settings_id).values(**kwargs)
            )
            await self._session.flush()
        elif user_id:
            await self._session.execute(
                update(UserSettings).where(UserSettings.user_id == user_id).values(**kwargs)
            )
            await self._session.flush()
        elif user_settings:
            for key, value in kwargs.items():
                setattr(user_settings, key, value)
            self._session.add(user_settings)
            await self._session.flush()
