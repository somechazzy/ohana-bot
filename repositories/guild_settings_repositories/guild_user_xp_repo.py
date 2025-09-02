from datetime import datetime
from typing import Any

from sqlalchemy import or_, and_, select
from sqlalchemy.dialects.mysql import insert

from models.guild_settings_models import GuildUserXP
from repositories import BaseRepo


class GuildUserXPRepo(BaseRepo):

    # noinspection PyTypeChecker
    async def create_guild_user_xp(self,
                                   guild_settings_id: int,
                                   user_id: int,
                                   user_username: str,
                                   xp: int,
                                   level: int,
                                   message_count: int,
                                   latest_gain_time: datetime,
                                   latest_level_up_message_time: datetime,
                                   decayed_xp: int,
                                   latest_decay_time: datetime,
                                   latest_message_time: datetime) -> GuildUserXP:
        """
        Create guild user XP for a user.
        """
        new_settings = GuildUserXP(
            guild_settings_id=guild_settings_id,
            user_id=user_id,
            user_username=user_username,
            xp=xp,
            level=level,
            message_count=message_count,
            latest_gain_time=latest_gain_time,
            latest_level_up_message_time=latest_level_up_message_time,
            decayed_xp=decayed_xp,
            latest_decay_time=latest_decay_time,
            latest_message_time=latest_message_time
        )
        self._session.add(new_settings)
        await self._session.flush()
        return new_settings

    async def get_all_for_guild(self, guild_settings_id: int) -> list[GuildUserXP]:
        """
        Get all guild user XP records for a specific guild.
        """
        return (await self._session.execute(
            select(GuildUserXP).filter(GuildUserXP.guild_settings_id == guild_settings_id)
        )).scalars().all()

    async def bulk_upsert_guild_user_xp(self, upsert_data: dict[tuple[int, int], dict[str, Any]]):
        """
        Bulk upsert guild user XP records.
        Upsert data will be formatted as such:
            {(guild_settings_id, user_id): {
                'user_username': str,
                'xp': int,
                'level': int,
                'message_count': int,
                'latest_gain_time': datetime,
                'latest_level_up_message_time': datetime,
                'decayed_xp': int,
                'latest_decay_time': datetime,
                'latest_message_time': datetime
            }}
        if a record matching (guild_settings_id, user_id) key is found, then it will be updated with the provided data.
        """
        stmt = insert(GuildUserXP).values([
            {
                'guild_settings_id': guild_settings_id,
                'user_id': user_id,
                **data
            } for (guild_settings_id, user_id), data in upsert_data.items()
        ])

        stmt = stmt.on_duplicate_key_update(
            user_username=stmt.inserted.user_username,
            xp=stmt.inserted.xp,
            level=stmt.inserted.level,
            message_count=stmt.inserted.message_count,
            latest_gain_time=stmt.inserted.latest_gain_time,
            latest_level_up_message_time=stmt.inserted.latest_level_up_message_time,
            decayed_xp=stmt.inserted.decayed_xp,
            latest_decay_time=stmt.inserted.latest_decay_time,
            latest_message_time=stmt.inserted.latest_message_time,
        )

        await self._session.execute(stmt)
        await self._session.flush()

    async def get_guild_settings_ids_with_decay_eligible_members(
            self, guild_settings_id_last_message_time_pairs: list[tuple[int, datetime]]
    ) -> list[int]:
        """
        Get unique guild_setting_id values where any of the conditions are met for each pair in the given list:
            - guild_settings_id matches the given guild_settings_id.
            - latest_message_time is older than the current time.
        Args:
            guild_settings_id_last_message_time_pairs (list[tuple[int, datetime]]): List of tuples containing
                guild_settings_id and max latest_message_time to filter by.

        Returns:
            list[int]: List of unique guild_settings_id values that match the conditions.
        """
        if not guild_settings_id_last_message_time_pairs:
            return []

        or_conditions = [
            and_(GuildUserXP.guild_settings_id == guild_settings_id,
                 GuildUserXP.latest_message_time < last_message_time)
            for guild_settings_id, last_message_time in guild_settings_id_last_message_time_pairs
        ]

        query = select(GuildUserXP.guild_settings_id).filter(
            or_(*or_conditions)
        ).distinct()
        result = await self._session.execute(query)
        return [row[0] for row in result]

    async def get_all_for_guilds(self, guild_settings_ids: list[int]) -> list[GuildUserXP]:
        """
        Get all guild user XP records for a list of guilds.
        Args:
            guild_settings_ids (list[int]): List of guild settings IDs to filter by.

        Returns:
            list[GuildUserXP]: List of GuildUserXP records for the specified guilds.
        """
        if not guild_settings_ids:
            return []
        return (await self._session.execute(
            select(GuildUserXP).filter(GuildUserXP.guild_settings_id.in_(guild_settings_ids))
        )).scalars().all()
