import random
from datetime import datetime, UTC, timedelta

from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from components.guild_user_xp_components import BaseGuildUserXPComponent
import cache
from components.guild_user_xp_components.guild_user_xp_component import GuildUserXPComponent
from constants import XPSettingsMessageCountMode
from models.dto.cachables import CachedGuildXP, CachedGuildSettings
from models.dto.xp import XPAction, XPDecayItem


class XPProcessingComponent(BaseGuildUserXPComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_user_message(self,
                              user_id: int,
                              guild_id: int,
                              message_time: datetime,
                              user_username: str,
                              is_booster: bool) -> bool:
        """
        Handle all changes related to user XP upon user message.
        Args:
            user_id (int): user ID that sent the message.
            guild_id (int): guild ID the message was sent to.
            message_time (datetime): time the message was sent.
            user_username (str): username of the user who sent the message.
            is_booster (bool): whether the user is eligible for the booster gain multiplier.

        Returns:
            bool: whether the user's level was updated during this flow.
        """
        self.logger.debug("Processing user message for XP gain.")
        level_updated = False
        member_xp = await self._get_member_xp(guild_id=guild_id, user_id=user_id, user_username=user_username)
        member_xp.user_username = user_username  # passively keep username updated

        xp_settings = (await GuildSettingsComponent().get_guild_settings(guild_id)).xp_settings

        if not member_xp.message_count:
            # case: first message from user, new XP record (latest_gain_time set to ~now), to bypass subtract timeframe
            member_xp.latest_gain_time -= timedelta(seconds=xp_settings.xp_gain_timeframe)

        if xp_settings.message_count_mode == XPSettingsMessageCountMode.PER_MESSAGE:
            member_xp.register_message(message_time=message_time)

        if (datetime.now(UTC) - member_xp.latest_gain_time).seconds >= xp_settings.xp_gain_timeframe:
            if xp_settings.message_count_mode == XPSettingsMessageCountMode.PER_TIMEFRAME:
                member_xp.register_message(message_time=message_time)
            xp_gain = xp_settings.xp_gain_minimum + int(random.random() *
                                                        (xp_settings.xp_gain_maximum - xp_settings.xp_gain_minimum + 1))
            if is_booster:
                xp_gain += int(xp_gain * (xp_settings.booster_xp_gain_multiplier / 100))

            new_level = self.get_level_at_xp(xp=member_xp.xp + xp_gain, xp_settings=xp_settings)
            level_updated = new_level != member_xp.level
            member_xp.gain_xp(amount=xp_gain, new_level=new_level)

        return level_updated

    async def on_user_xp_action(self, xp_action: XPAction) -> bool:
        """
        Handle direct XP action and its changes.
        Args:
            xp_action (XPAction): action to handle.

        Returns:
            bool: whether the user's level was updated during this flow.
        """
        self.logger.debug("Processing user XP action.")
        member_xp = await self._get_member_xp(guild_id=xp_action.guild_id, user_id=xp_action.member_id,
                                              user_username=xp_action.username)
        xp_settings = (await GuildSettingsComponent().get_guild_settings(xp_action.guild_id)).xp_settings

        xp_offset = -member_xp.xp if xp_action.reset else xp_action.xp_offset
        level = self.get_level_at_xp(xp=member_xp.xp + xp_offset, xp_settings=xp_settings)
        level_before_action = member_xp.level
        member_xp.offset_xp(amount=xp_offset, new_level=level)

        return level != level_before_action

    async def process_user_xp_decay(self, decay_item: XPDecayItem) -> bool:
        """
        Process user XP decay.
        Args:
            decay_item (XPDecayItem): DTO containing decay details.

        Returns:
            bool: whether the user's level was updated during this flow.
        """
        self.logger.debug("Processing user XP decay.")
        member_xp = await self._get_member_xp(guild_id=decay_item.guild_id, user_id=decay_item.member_id,
                                              user_username=decay_item.username)
        xp_settings = (await GuildSettingsComponent().get_guild_settings(decay_item.guild_id)).xp_settings

        decay_grace_days = xp_settings.xp_decay_grace_period_days
        decay_cutoff = datetime.now(UTC) - timedelta(days=decay_grace_days)
        if member_xp.latest_message_time and member_xp.latest_message_time > decay_cutoff:
            return False  # no need to decay anymore

        decay_amount = int(member_xp.xp * (xp_settings.xp_decay_per_day_percentage / 100))
        level = self.get_level_at_xp(xp=member_xp.xp - decay_amount, xp_settings=xp_settings)
        level_before_action = member_xp.level
        member_xp.decay_xp(amount=decay_amount, new_level=level)

        return level != level_before_action

    # noinspection PyMethodMayBeStatic
    async def _get_member_xp(self, guild_id: int, user_id: int, user_username: str) -> CachedGuildXP.MemberXP:
        """
        Get (and fetch or create if needed) member XP.
        Args:
            guild_id (int): guild ID.
            user_id (int): user ID.
            user_username (str): user username in case creation is needed for this member's XP.

        Returns:
            CachedGuildXP.MemberXP: member XP object.
        """
        if guild_id not in cache.CACHED_GUILD_XP:
            await GuildUserXPComponent().fetch_guild_xp(guild_id=guild_id)
        guild_xp = cache.CACHED_GUILD_XP[guild_id]
        if not guild_xp.get_xp_for(user_id):
            guild_xp.initiate_member_xp(user_id=user_id, user_username=user_username)
        return guild_xp.get_xp_for(user_id)

    # noinspection PyMethodMayBeStatic
    def get_level_at_xp(self, xp: int, xp_settings: CachedGuildSettings.XPSettings) -> int:
        """
        Checks the XP/level model to see which level this XP falls under.
        Args:
            xp (int): XP.
            xp_settings (CachedGuildSettings.XPSettings): XP settings to use.

        Returns:
            int: level.
        """
        level = 0
        for xp_requirement, xp_level in cache.XP_LEVEL_MAP.items():
            if xp >= xp_requirement:
                level = xp_level
            else:
                break
        if level > xp_settings.max_level:
            level = xp_settings.max_level
        return level
