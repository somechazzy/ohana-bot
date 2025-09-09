from common.db import get_session
from components.user_settings_components import BaseUserSettingsComponent
from constants import AnimangaProvider
from models.user_settings_models import UserSettings
from repositories.user_settings_repositories.user_settings_repo import UserSettingsRepo


class UserSettingsComponent(BaseUserSettingsComponent):

    async def create_default_user_settings(self,
                                           user_id: int,
                                           preferred_animanga_provider: str = AnimangaProvider.MAL) -> UserSettings:
        """
        Creates default user settings for a new user.
        Args:
            user_id (int): user Discord ID.
            preferred_animanga_provider (str): The preferred animanga provider for the user.

        Returns:
            UserSettings: The newly created user settings.
        """
        self.logger.debug(f"Creating default user settings for user_id={user_id}")

        user_settings_repo = UserSettingsRepo(session=get_session())
        return await user_settings_repo.create_user_settings(user_id=user_id,
                                                             preferred_animanga_provider=preferred_animanga_provider)

    async def get_user_settings(self, user_id: int,
                                load_usernames: bool = False) -> UserSettings | None:
        """
        Fetches the user settings for a given user ID. Creates default settings if none exist.
        Args:
            user_id (int): user Discord ID.
            load_usernames (bool): Whether to load associated usernames.

        Returns:
            UserSettings: The settings for the specified user.
        """
        self.logger.debug(f"Getting user settings for user_id={user_id}")

        user_settings_repo = UserSettingsRepo(session=get_session())
        if not (user_settings := await user_settings_repo.get_user_settings_by_user_id(user_id=user_id,
                                                                                       load_usernames=load_usernames)):
            self.logger.debug(f"No existing settings found for user_id={user_id}, creating default settings.")
            user_settings = await self.create_default_user_settings(user_id=user_id)
        return user_settings

    async def update_user_settings(self,
                                   user_id: int | None = None,
                                   user_settings: UserSettings | None = None,
                                   timezone: str | None = None,
                                   relayed_reminders_disabled: bool | None = None,
                                   blocked_from_relaying_reminders: bool | None = None,
                                   preferred_animanga_provider: str | None = None) -> None:
        """
        Updates user settings based on the provided parameters. Must provide either user_id or user_settings.
        Args:
            user_id (int | None):
                The Discord ID of the user whose settings are to be updated.
            user_settings (UserSettings | None):
                The user settings object to update.
            timezone (str | None):
                The timezone to set for the user. None to leave unchanged.
            relayed_reminders_disabled (bool | None):
                Whether relayed reminders are disabled. None to leave unchanged.
            blocked_from_relaying_reminders (bool | None):
                Whether the user is blocked from relaying reminders. None to leave unchanged.
            preferred_animanga_provider (str | None):
                The preferred animanga provider. None to leave unchanged.
        Returns:
            None
        """
        if user_id is None and user_settings is None:
            raise ValueError("Must provide either user_id or user_settings")
        self.logger.debug(f"Updating user settings for user_id={user_id or user_settings.id}, "
                          f"relayed_reminders_disabled={relayed_reminders_disabled}, "
                          f"blocked_from_relaying_reminders={blocked_from_relaying_reminders}, "
                          f"preferred_animanga_provider={preferred_animanga_provider}")

        update_data = {}
        if timezone is not None:
            update_data["timezone"] = timezone
        if relayed_reminders_disabled is not None:
            update_data['relayed_reminders_disabled'] = relayed_reminders_disabled
        if blocked_from_relaying_reminders is not None:
            update_data['blocked_from_relaying_reminders'] = blocked_from_relaying_reminders
        if preferred_animanga_provider is not None:
            update_data['preferred_animanga_provider'] = preferred_animanga_provider

        if not update_data:
            self.logger.debug("No update data provided, skipping update.")
            return

        user_settings_repo = UserSettingsRepo(session=get_session())
        await user_settings_repo.update_user_settings(
            user_id=user_id,
            user_settings=user_settings,
            **update_data
        )
