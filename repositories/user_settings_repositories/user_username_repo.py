from models.user_settings_models import UserUsername, UserSettings
from repositories import BaseRepo
from sqlalchemy import select, update, delete


class UserUsernameRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_user_username(self,
                                   user_settings_id: int,
                                   username: str,
                                   provider: str) -> UserUsername:
        """
        Create a username record of a certain provider for the user.
        """
        user_username = UserUsername(
            user_settings_id=user_settings_id,
            username=username,
            provider=provider
        )
        self._session.add(user_username)
        await self._session.flush()
        return user_username

    async def get_user_username(self,
                                user_settings_id: int,
                                provider: str) -> UserUsername | None:
        """
        Get a username record of a certain provider for the user.
        """
        return (await self._session.execute(
            select(UserUsername).where(UserUsername.user_settings_id == user_settings_id,
                                       UserUsername.provider == provider)
        )).scalar_one_or_none()

    async def get_user_usernames(self, user_settings_id: int) -> list[UserUsername]:
        """
        Get all username records for a specific user settings ID.
        """
        return (await self._session.execute(
            select(UserUsername).where(UserUsername.user_settings_id == user_settings_id)
        )).scalars().all()

    async def update_user_username(self,
                                   user_username_id: int | None = None,
                                   user_username: UserUsername | None = None, **kwargs) -> None:
        """
        Update username for a specific user settings ID. Must provide either user_username_id or user_username.
        """
        if user_username_id:
            await self._session.execute(
                update(UserUsername).where(UserUsername.id == user_username_id).values(**kwargs)
            )
            await self._session.flush()
        elif user_username:
            for key, value in kwargs.items():
                setattr(user_username, key, value)
            self._session.add(user_username)
            await self._session.flush()
        else:
            raise ValueError("Either user_username_id or user_username must be provided.")

    async def delete_user_username(self,
                                   user_settings_id: int,
                                   provider: str) -> None:
        """
        Delete a username record of a certain provider for the user.
        """
        await self._session.execute(
            delete(UserUsername).where(UserUsername.user_settings_id == user_settings_id,
                                       UserUsername.provider == provider)
        )

    async def get_user_username_by_user_id(self, user_id: int, provider: str) -> UserUsername | None:
        """
        Get a username record of a certain provider for the user by user ID.
        """
        return (await self._session.execute(
            select(UserUsername).join(UserUsername.user_settings).where(UserSettings.user_id == user_id,
                                                                        UserUsername.provider == provider)
        )).scalar_one_or_none()
