from common.db import get_session
from components.guild_settings_components import BaseGuildSettingsComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from repositories.guild_settings_repositories.guild_autorole_repo import GuildAutoroleRepo


class GuildAutoroleComponent(BaseGuildSettingsComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add_autorole(self, guild_id: int, role_id: int):
        """
        Adds a role to the autoroles of a guild.
        Args:
            guild_id (int): The ID of the guild.
            role_id (int): The ID of the role to be added as an autorole.
        """
        self.logger.debug(f"Adding autorole {role_id} to guild {guild_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        if role_id in guild_settings.autoroles_ids:
            return
        guild_settings.autoroles_ids.append(role_id)
        guild_autoroles_repo = GuildAutoroleRepo(session=get_session())
        await guild_autoroles_repo.create_guild_autorole(
            guild_settings_id=guild_settings.guild_settings_id,
            role_id=role_id
        )

    async def remove_autorole(self, guild_id: int, role_id: int):
        """
        Removes a role from the autoroles of a guild.
        Args:
            guild_id (int): The ID of the guild.
            role_id (int): The ID of the role to be removed from autoroles.
        """
        self.logger.debug(f"Removing autorole {role_id} from guild {guild_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        if role_id not in guild_settings.autoroles_ids:
            return
        guild_settings.autoroles_ids.remove(role_id)
        guild_autoroles_repo = GuildAutoroleRepo(session=get_session())
        await guild_autoroles_repo.delete_guild_autorole(
            guild_settings_id=guild_settings.guild_settings_id,
            role_id=role_id
        )

    async def clear_autoroles(self, guild_id: int):
        """
        Clears all autoroles for a guild.
        Args:
            guild_id (int): The ID of the guild.
        """
        self.logger.debug(f"Clearing all autoroles for guild {guild_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        if not guild_settings.autoroles_ids:
            return
        guild_settings.autoroles_ids.clear()
        guild_autoroles_repo = GuildAutoroleRepo(session=get_session())
        await guild_autoroles_repo.delete_guild_autoroles(guild_settings.guild_settings_id)
