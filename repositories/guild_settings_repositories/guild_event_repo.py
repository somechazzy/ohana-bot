from datetime import datetime

from sqlalchemy import select

from models.guild_settings_models import GuildEvent, GuildSettings
from repositories import BaseRepo


class GuildEventRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_event(self,
                                 guild_settings_id: int,
                                 event_type: str,
                                 event_time: datetime,
                                 event_metadata: dict | str | None = None) -> GuildEvent:
        """
        Create a new guild event.
        """
        guild_event = GuildEvent(
            guild_settings_id=guild_settings_id,
            event_type=event_type,
            event_time=event_time,
            event_metadata=event_metadata
        )
        self._session.add(guild_event)
        return guild_event

    async def get_guild_events_by_guild_settings_id(self,
                                                    guild_settings_id: int,
                                                    event_type: str | None = None) -> list[GuildEvent]:
        """
        Get all guild events for a specific guild settings ID.
        """
        conditions = [GuildEvent.guild_settings_id == guild_settings_id]
        if event_type:
            conditions.append(GuildEvent.event_type == event_type)
        return (await self._session.execute(
            select(GuildEvent).where(*conditions)
        )).scalars().all()

    async def get_guild_events_by_guild_id(self,
                                           guild_id: int,
                                           event_type: str | None = None) -> list[GuildEvent]:
        """
        Get all guild events for a specific guild ID.
        """
        conditions = [GuildSettings.guild_id == guild_id]
        if event_type:
            conditions.append(GuildEvent.event_type == event_type)
        return (await self._session.execute(
            select(GuildEvent).join(GuildEvent.guild_settings).where(*conditions)
        )).scalars().all()
