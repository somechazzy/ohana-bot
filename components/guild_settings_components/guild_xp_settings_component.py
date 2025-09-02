from common import NOT_SET_
from common.db import get_session
from components.guild_settings_components import BaseGuildSettingsComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from models.guild_settings_models import GuildXPIgnoredChannel, GuildXPIgnoredRole, GuildXPLevelRole, GuildXPSettings
from repositories.guild_settings_repositories.guild_xp_settings_repo import GuildXPSettingsRepo

NOT_SET = NOT_SET_()


class GuildXPSettingsComponent(BaseGuildSettingsComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create_guild_xp_settings(self, guild_id: int, guild_settings_id: int) -> GuildXPSettings:
        """
        Create XP settings for a guild.
        Args:
            guild_id (int): The ID of the guild.
            guild_settings_id (int): The GuildSettings ID related.

        Returns:
            GuildXPSettings: The created XP settings object.
        """
        self.logger.debug(f"Creating XP settings for guild_id: {guild_id}")
        return await GuildXPSettingsRepo(session=get_session()).create_guild_xp_settings(
            guild_settings_id=guild_settings_id
        )

    async def update_guild_xp_settings(self,
                                       guild_id: int,
                                       xp_gain_enabled: bool | NOT_SET_ = NOT_SET,
                                       xp_gain_timeframe: int | NOT_SET_ = NOT_SET,
                                       xp_gain_minimum: int | NOT_SET_ = NOT_SET,
                                       xp_gain_maximum: int | NOT_SET_ = NOT_SET,
                                       message_count_mode: str | NOT_SET_ = NOT_SET,  # XPSettingsMessageCountMode
                                       xp_decay_enabled: bool | NOT_SET_ = NOT_SET,
                                       xp_decay_per_day_percentage: float | NOT_SET_ = NOT_SET,
                                       xp_decay_grace_period_days: int | NOT_SET_ = NOT_SET,
                                       booster_xp_gain_multiplier: float | NOT_SET_ = NOT_SET,
                                       level_up_message_enabled: bool | NOT_SET_ = NOT_SET,
                                       level_up_message_channel_id: int | NOT_SET_ = NOT_SET,
                                       level_up_message_text: str | NOT_SET_ = NOT_SET,
                                       level_up_message_minimum_level: int | NOT_SET_ = NOT_SET,
                                       max_level: int | NOT_SET_ = NOT_SET,
                                       stack_level_roles: bool | NOT_SET_ = NOT_SET,
                                       level_role_earn_message_text: str | NOT_SET_ = NOT_SET):
        """
        Update the XP channel settings for a guild.
        Args:
            guild_id (int): The ID of the guild.
            xp_gain_enabled (bool | NOT_SET_): Whether XP gain is enabled.
            xp_gain_timeframe (int | NOT_SET_): The timeframe for XP gain in seconds.
            xp_gain_minimum (int | NOT_SET_): The minimum XP gain per message.
            xp_gain_maximum (int | NOT_SET_): The maximum XP gain per message.
            message_count_mode (str | NOT_SET_): The mode for counting messages for XP gain.
            xp_decay_enabled (bool | NOT_SET_): Whether XP decay is enabled.
            xp_decay_per_day_percentage (float | NOT_SET_): The percentage of XP to decay per day.
            xp_decay_grace_period_days (int | NOT_SET_): The number of days before XP decay starts.
            booster_xp_gain_multiplier (float | NOT_SET_): The multiplier for XP gain for boosters.
            level_up_message_enabled (bool | NOT_SET_): Whether level-up messages are enabled.
            level_up_message_channel_id (int | NOT_SET_): The channel ID for level-up messages.
            level_up_message_text (str | NOT_SET_): The text for level-up messages.
            level_up_message_minimum_level (int | NOT_SET_): The minimum level to send level-up messages.
            max_level (int | NOT_SET_): The maximum level a user can reach.
            stack_level_roles (bool | NOT_SET_): Whether to stack level roles.
            level_role_earn_message_text (str | NOT_SET_): The message to send when a user
        """
        self.logger.debug(f"Updating XP settings for guild_id: {guild_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_xp_settings_repo = GuildXPSettingsRepo(session=get_session())

        update_data = {}
        if xp_gain_enabled is not NOT_SET:
            update_data['xp_gain_enabled'] = xp_gain_enabled
            guild_settings.xp_settings.xp_gain_enabled = xp_gain_enabled
        if xp_gain_timeframe is not NOT_SET:
            update_data['xp_gain_timeframe'] = xp_gain_timeframe
            guild_settings.xp_settings.xp_gain_timeframe = xp_gain_timeframe
        if xp_gain_minimum is not NOT_SET:
            update_data['xp_gain_minimum'] = xp_gain_minimum
            guild_settings.xp_settings.xp_gain_minimum = xp_gain_minimum
        if xp_gain_maximum is not NOT_SET:
            update_data['xp_gain_maximum'] = xp_gain_maximum
            guild_settings.xp_settings.xp_gain_maximum = xp_gain_maximum
        if message_count_mode is not NOT_SET:
            update_data['message_count_mode'] = message_count_mode
            guild_settings.xp_settings.message_count_mode = message_count_mode
        if xp_decay_enabled is not NOT_SET:
            update_data['xp_decay_enabled'] = xp_decay_enabled
            guild_settings.xp_settings.xp_decay_enabled = xp_decay_enabled
        if xp_decay_per_day_percentage is not NOT_SET:
            update_data['xp_decay_per_day_percentage'] = xp_decay_per_day_percentage
            guild_settings.xp_settings.xp_decay_per_day_percentage = xp_decay_per_day_percentage
        if xp_decay_grace_period_days is not NOT_SET:
            update_data['xp_decay_grace_period_days'] = xp_decay_grace_period_days
            guild_settings.xp_settings.xp_decay_grace_period_days = xp_decay_grace_period_days
        if booster_xp_gain_multiplier is not NOT_SET:
            update_data['booster_xp_gain_multiplier'] = booster_xp_gain_multiplier
            guild_settings.xp_settings.booster_xp_gain_multiplier = booster_xp_gain_multiplier
        if level_up_message_enabled is not NOT_SET:
            update_data['level_up_message_enabled'] = level_up_message_enabled
            guild_settings.xp_settings.level_up_message_enabled = level_up_message_enabled
        if level_up_message_channel_id is not NOT_SET:
            update_data['level_up_message_channel_id'] = level_up_message_channel_id
            guild_settings.xp_settings.level_up_message_channel_id = level_up_message_channel_id
        if level_up_message_text is not NOT_SET:
            update_data['level_up_message_text'] = level_up_message_text
            guild_settings.xp_settings.level_up_message_text = level_up_message_text
        if level_up_message_minimum_level is not NOT_SET:
            update_data['level_up_message_minimum_level'] = level_up_message_minimum_level
            guild_settings.xp_settings.level_up_message_minimum_level = level_up_message_minimum_level
        if max_level is not NOT_SET:
            update_data['max_level'] = max_level
            guild_settings.xp_settings.max_level = max_level
        if stack_level_roles is not NOT_SET:
            update_data['stack_level_roles'] = stack_level_roles
            guild_settings.xp_settings.stack_level_roles = stack_level_roles
        if level_role_earn_message_text is not NOT_SET:
            update_data['level_role_earn_message_text'] = level_role_earn_message_text
            guild_settings.xp_settings.level_role_earn_message_text = level_role_earn_message_text

        await guild_xp_settings_repo.update_guild_xp_settings(
            guild_xp_settings_id=guild_settings.xp_settings.guild_xp_settings_id,
            **update_data
        )

    async def add_xp_level_role(self,
                                guild_id: int,
                                guild_xp_settings_id: int,
                                role_id: int,
                                level: int) -> GuildXPLevelRole:
        """
        Add a level role to the guild's XP settings.
        Args:
            guild_id (int): The ID of the guild.
            guild_xp_settings_id (int): The ID of the guild's XP settings.
            role_id (int): The ID of the role to add.
            level (int): The level associated with the role.

        Returns:
            GuildXPLevelRole: The created level role object.
        """
        self.logger.debug(f"Adding XP level role for guild_id: {guild_id}, role_id: {role_id}, level: {level}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        if level not in guild_settings.xp_settings.level_role_ids_map:
            guild_settings.xp_settings.level_role_ids_map[level] = set()
        guild_settings.xp_settings.level_role_ids_map[level].add(role_id)
        return await GuildXPSettingsRepo(session=get_session()).add_xp_level_role(
            guild_xp_settings_id=guild_xp_settings_id,
            role_id=role_id,
            level=level
        )

    async def update_xp_level_role(self, guild_id: int, role_id: int, level: int, old_level: int):
        """
        Update a level role in the guild's XP settings.
        Args:
            guild_id (int): The ID of the guild.
            role_id (int): The ID of the role to update.
            level (int): The new level associated with the role.
            old_level (int): The old level associated with the role.
        """
        self.logger.debug(f"Updating XP level role for guild_id: {guild_id}, role_id: {role_id}, level: {level}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        if old_level in guild_settings.xp_settings.level_role_ids_map:
            guild_settings.xp_settings.level_role_ids_map[old_level].discard(role_id)
        if level not in guild_settings.xp_settings.level_role_ids_map:
            guild_settings.xp_settings.level_role_ids_map[level] = set()
        guild_settings.xp_settings.level_role_ids_map[level].add(role_id)
        await GuildXPSettingsRepo(session=get_session()).update_level_role(
            role_id=role_id,
            level=level,
        )

    async def remove_xp_level_role(self, guild_id: int, role_id: int, level: int):
        """
        Remove a level role from the guild's XP settings.
        Args:
            guild_id (int): The ID of the guild.
            role_id (int): The ID of the role to remove.
            level (int): The level associated with the role.
        """
        self.logger.debug(f"Removing XP level role for guild_id: {guild_id}, role_id: {role_id}, level: {level}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        if level in guild_settings.xp_settings.level_role_ids_map:
            guild_settings.xp_settings.level_role_ids_map[level].discard(role_id)
            if not guild_settings.xp_settings.level_role_ids_map[level]:
                guild_settings.xp_settings.level_role_ids_map.pop(level, None)
        await GuildXPSettingsRepo(session=get_session()).remove_xp_level_role(
            role_id=role_id,
            level=level
        )

    async def add_ignored_channel(self,
                                  guild_id: int,
                                  guild_xp_settings_id: int,
                                  channel_id: int) -> GuildXPIgnoredChannel:
        """
        Add a channel to the list of ignored channels for XP gain.
        Args:
            guild_id (int): The ID of the guild.
            guild_xp_settings_id (int): The ID of the guild's XP settings.
            channel_id (int): The ID of the channel to ignore.

        Returns:
            GuildXPIgnoredChannel: The created ignored channel object.
        """
        self.logger.debug(f"Adding ignored channel for guild_id: {guild_id}, channel_id: {channel_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_settings.xp_settings.ignored_channel_ids.add(channel_id)
        return await GuildXPSettingsRepo(session=get_session()).add_xp_ignored_channel(
            guild_xp_settings_id=guild_xp_settings_id,
            channel_id=channel_id
        )

    async def remove_ignored_channel(self, guild_id: int, channel_id: int):
        """
        Remove a channel from the list of ignored channels for XP gain.
        Args:
            guild_id (int): The ID of the guild.
            channel_id (int): The ID of the channel to remove from ignored channels.
        """
        self.logger.debug(f"Removing ignored channel for guild_id: {guild_id}, channel_id: {channel_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_settings.xp_settings.ignored_channel_ids.discard(channel_id)
        return await GuildXPSettingsRepo(session=get_session()).remove_xp_ignored_channel(
            channel_id=channel_id
        )

    async def add_ignored_role(self, guild_id: int, guild_xp_settings_id: int, role_id: int) -> GuildXPIgnoredRole:
        """
        Add a role to the list of ignored roles for XP gain.
        Args:
            guild_id (int): The ID of the guild.
            guild_xp_settings_id (int): The ID of the guild's XP settings.
            role_id (int): The ID of the role to ignore.

        Returns:
            GuildXPIgnoredRole: The created ignored role object.
        """
        self.logger.debug(f"Adding ignored role for guild_id: {guild_id}, role_id: {role_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_settings.xp_settings.ignored_role_ids.add(role_id)
        return await GuildXPSettingsRepo(session=get_session()).add_xp_ignored_role(
            guild_xp_settings_id=guild_xp_settings_id,
            role_id=role_id
        )

    async def remove_ignored_role(self, guild_id: int, role_id: int):
        """
        Remove a role from the list of ignored roles for XP gain.
        Args:
            guild_id (int): The ID of the guild.
            role_id (int): The ID of the role to remove from ignored roles.
        """
        self.logger.debug(f"Removing ignored role for guild_id: {guild_id}, role_id: {role_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_settings.xp_settings.ignored_role_ids.discard(role_id)
        return await GuildXPSettingsRepo(session=get_session()).remove_xp_ignored_role(
            role_id=role_id
        )
