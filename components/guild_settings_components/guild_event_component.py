from datetime import datetime

from common.db import get_session
from components.guild_settings_components import BaseGuildSettingsComponent
from models.guild_settings_models import GuildEvent
from repositories.guild_settings_repositories.guild_event_repo import GuildEventRepo


class GuildEventComponent(BaseGuildSettingsComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create_guild_event(self,
                                 guild_id: int,
                                 guild_settings_id: int,
                                 event: str,
                                 event_time: datetime,
                                 event_metadata: dict | None) -> GuildEvent:
        """
        Create a guild event.
        Args:
            guild_id (int): The ID of the guild.
            guild_settings_id (int): guild settings ID to associate the event with.
            event (str): The event to create - GuildEventType
            event_time (datetime): The time of the event.
            event_metadata (dict | None): Metadata for the event, if any.

        Returns:
            GuildEvent: The created guild event.
        """
        self.logger.debug(f"Creating guild event '{event}' for guild {guild_id}")
        return await GuildEventRepo(get_session()).create_guild_event(
            guild_settings_id=guild_settings_id,
            event_type=event,
            event_time=event_time,
            event_metadata=event_metadata,
        )
