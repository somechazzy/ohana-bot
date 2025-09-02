from common.db import get_session
from components.integration_component.anilist_component import AnilistComponent
from components.integration_component.mal_component import MALComponent
from components.user_settings_components import BaseUserSettingsComponent
from components.user_settings_components.user_settings_component import UserSettingsComponent
from constants import UserUsernameProvider, AnimangaProvider
from strings.integrations_strings import MALStrings
from repositories.user_settings_repositories.user_settings_repo import UserSettingsRepo
from repositories.user_settings_repositories.user_username_repo import UserUsernameRepo


class UserUsernameComponent(BaseUserSettingsComponent):

    async def set_user_username(self,
                                user_id: int,
                                new_username: str,
                                provider: str,
                                validate_with_provider: bool = True) -> str:
        """
        Set or update a provider username for a user. Returns status of the operation.
        Args:
            user_id (int): Discord user ID
            new_username (str): username to set/update to
            provider (str): UserUsernameProvider
            validate_with_provider (bool): If True, validates the username with the provider's service.

        Returns:
            str: user-facing status message

        Raises:
            UserInputException: If the username is invalid for the specified provider.
            ExternalServiceException: If the the specified provider's service is unavailable.
        """
        self.logger.debug(f"Setting new username for `{new_username}`. User ID: {user_id}, Provider: {provider}")
        if validate_with_provider:
            match provider:
                case UserUsernameProvider.MAL:
                    await MALComponent().validate_username(username=new_username)
                case UserUsernameProvider.ANILIST:
                    await AnilistComponent().validate_username(username=new_username)
        newly_created_user_settings = False

        user_settings_repo = UserSettingsRepo(session=get_session())
        user_username_repo = UserUsernameRepo(session=get_session())
        if not (user_settings := await user_settings_repo.get_user_settings_by_user_id(user_id=user_id,
                                                                                       load_usernames=True)):
            preferred_animanga_provider = UserUsernameProvider.MAL if provider == AnimangaProvider.MAL \
                else UserUsernameProvider.ANILIST if provider == AnimangaProvider.ANILIST \
                else None
            user_settings = await UserSettingsComponent().create_default_user_settings(
                user_id=user_id, preferred_animanga_provider=preferred_animanga_provider
            )
            newly_created_user_settings = True
        if newly_created_user_settings or not user_settings.usernames or not any(
                username.provider == provider for username in user_settings.usernames
        ):
            await user_username_repo.create_user_username(
                user_settings_id=user_settings.id, provider=provider, username=new_username
            )
            await user_settings_repo.update_user_settings(
                user_settings=user_settings,
                provider=UserUsernameProvider.MAL if provider == AnimangaProvider.MAL
                else UserUsernameProvider.ANILIST if provider == AnimangaProvider.ANILIST
                else None
            )
            feedback_message = MALStrings.USERNAME_LINKED.format(username=new_username)
        else:  # Update existing username
            existing_user_username = next(
                (username for username in user_settings.usernames if username.provider == provider), None
            )
            await user_username_repo.update_user_username(
                user_settings_id=user_settings.id, provider=provider, new_username=new_username
            )
            feedback_message = MALStrings.USERNAME_UPDATED.format(username=new_username,
                                                                  old_username=existing_user_username.username)

        return feedback_message

    async def unset_user_username(self, user_id: int, provider: str) -> str:
        """
        Unset a provider username for a user. Returns status of the operation.
        Args:
            user_id (int): Discord user ID
            provider (str): UserUsernameProvider

        Returns:
            str: user-facing status message
        """
        self.logger.debug(f"Unsetting username for User ID: {user_id}, Provider: {provider}")

        user_settings_repo = UserSettingsRepo(session=get_session())
        user_username_repo = UserUsernameRepo(session=get_session())
        if not (user_settings := await user_settings_repo.get_user_settings_by_user_id(user_id=user_id,
                                                                                       load_usernames=True)):
            return MALStrings.USERNAME_NOT_SET.format(provider=provider)

        if not any(username.provider == provider for username in user_settings.usernames):
            return MALStrings.USERNAME_NOT_SET.format(provider=provider)

        await user_username_repo.delete_user_username(user_settings_id=user_settings.id, provider=provider)

        return MALStrings.USERNAME_UNSET.format(provider=provider)

    async def get_user_username(self, user_id: int, provider: str) -> str | None:
        """
        Get a provider username for a user.
        Args:
            user_id (int): Discord user ID
            provider (str): UserUsernameProvider

        Returns:
            str | None: Username if set, otherwise None
        """
        self.logger.debug(f"Getting username for User ID: {user_id}, Provider: {provider}")

        user_username_repo = UserUsernameRepo(session=get_session())
        user_username = await user_username_repo.get_user_username_by_user_id(
            user_id=user_id, provider=provider
        )
        if user_username:
            return user_username.username
        return None
