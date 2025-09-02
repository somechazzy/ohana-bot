from sqlalchemy import delete, update

from models.guild_settings_models import GuildAutoResponse
from repositories import BaseRepo


class GuildAutoResponseRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_auto_response(self,
                                         guild_settings_id: int,
                                         trigger_text: str,
                                         response_text: str,
                                         match_type: str,
                                         delete_original: bool) -> GuildAutoResponse:
        """
        Create an auto response for a guild.
        """
        new_auto_response = GuildAutoResponse(
            guild_settings_id=guild_settings_id,
            trigger_text=trigger_text,
            response_text=response_text,
            match_type=match_type,
            delete_original=delete_original
        )
        self._session.add(new_auto_response)
        await self._session.flush()
        return new_auto_response

    async def update_guild_auto_response(self,
                                         guild_auto_response_id: int,
                                         **update_data):
        """
        Update an existing auto response by its ID.
        """
        await self._session.execute(
            update(GuildAutoResponse).where(
                GuildAutoResponse.id == guild_auto_response_id
            ).values(**update_data)
        )

    async def delete_guild_auto_response(self, guild_auto_response_id: int) -> None:
        """
        Delete an auto response by its ID.
        """
        await self._session.execute(
            delete(GuildAutoResponse).where(
                GuildAutoResponse.id == guild_auto_response_id
            )
        )

    async def delete_guild_auto_responses(self, guild_settings_id: int) -> None:
        """
        Delete all auto responses for a specific guild settings ID.
        """
        await self._session.execute(
            delete(GuildAutoResponse).where(
                GuildAutoResponse.guild_settings_id == guild_settings_id
            )
        )
