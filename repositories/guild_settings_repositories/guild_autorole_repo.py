from sqlalchemy import delete

from models.guild_settings_models import GuildAutorole
from repositories import BaseRepo


class GuildAutoroleRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_autorole(self, guild_settings_id: int, role_id: int) -> GuildAutorole:
        """
        Create an autorole for a guild.
        """
        new_autorole = GuildAutorole(
            guild_settings_id=guild_settings_id,
            role_id=role_id
        )
        self._session.add(new_autorole)
        await self._session.flush()
        return new_autorole

    async def delete_guild_autorole(self, guild_settings_id: int, role_id: int) -> None:
        """
        Delete an autorole for a guild.
        """
        await self._session.execute(
            delete(GuildAutorole).where(
                GuildAutorole.guild_settings_id == guild_settings_id,
                GuildAutorole.role_id == role_id
            )
        )

    async def delete_guild_autoroles(self, guild_settings_id: int,) -> None:
        """
        Delete all autoroles for a guild.
        """
        await self._session.execute(
            delete(GuildAutorole).where(
                GuildAutorole.guild_settings_id == guild_settings_id
            )
        )
