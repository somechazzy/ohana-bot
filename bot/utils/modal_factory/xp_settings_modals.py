import discord
from discord.ui import TextInput, Label

from bot.utils.modal_factory import BaseModal
from constants import XPDefaults


class XPGainSettingsModal(BaseModal, title="XP Gain Settings"):
    min_xp_gain_label = Label(
        text="Minimum XP Gain",
        description=f"Minimum XP a user can gain per timeframe",
        component=TextInput(
            min_length=1,
            required=True,
            placeholder=f"Default: {XPDefaults.MIN_XP_GIVEN}",
            style=discord.TextStyle.short
        )
    )
    max_xp_gain_label = Label(
        text="Maximum XP Gain",
        description=f"Maximum XP a user can gain per timeframe",
        component=TextInput(
            min_length=1,
            required=True,
            placeholder=f"Default: {XPDefaults.MAX_XP_GIVEN}",
            style=discord.TextStyle.short
        )
    )
    xp_gain_timeframe_label = Label(
        text="XP Gain Timeframe (in seconds)",
        description=f"A user will gain XP only once per timeframe, no matter how many messages they send",
        component=TextInput(
            min_length=1,
            required=True,
            placeholder=f"Default: {XPDefaults.TIMEFRAME_FOR_XP}",
            style=discord.TextStyle.short
        )
    )
    booster_bonus_label = Label(
        text="Booster Bonus (in %)",
        description="Grant extra XP to server boosters",
        component=TextInput(
            min_length=1,
            required=True,
            placeholder=f"Default: {XPDefaults.BOOSTER_GAIN_MULTIPLIER}",
            style=discord.TextStyle.short
        )
    )

    def __init__(self, interactions_handler,
                 xp_gain_minimum: str,
                 xp_gain_maximum: str,
                 xp_gain_timeframe: str,
                 booster_xp_gain_multiplier: str,
                 **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.min_xp_gain_label.component.default = xp_gain_minimum
        self.max_xp_gain_label.component.default = xp_gain_maximum
        self.xp_gain_timeframe_label.component.default = xp_gain_timeframe
        self.booster_bonus_label.component.default = booster_xp_gain_multiplier

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_xp_gain_settings_modal_submit(
            interaction=interaction,
            xp_gain_minimum=self.min_xp_gain_label.component.value,
            xp_gain_maximum=self.max_xp_gain_label.component.value,
            xp_gain_timeframe=self.xp_gain_timeframe_label.component.value,
            booster_xp_gain_multiplier=self.booster_bonus_label.component.value
        )


class LevelUpMessageSettingsModal(BaseModal, title="Level-up Message Settings"):
    level_up_message_label = Label(
        text="Level-up message",
        description="You can use {member_mention}, {member_name}, and {level} as placeholders in the message.",
        component=TextInput(
            min_length=1,
            max_length=1000,
            required=True,
            style=discord.TextStyle.long,
            placeholder="Enter the message here"
        )
    )
    level_up_message_minimum_level_label = Label(
        text="Minimum level for the level-up message",
        description=f"Recommended: at least {XPDefaults.LEVEL_UP_MESSAGE_MINIMUM_LEVEL} to avoid spam.",
        component=TextInput(
            min_length=1,
            placeholder="Enter the minimum level here",
            required=True,
            style=discord.TextStyle.short
        )
    )
    level_up_channel_label = Label(
        text="Level-up channel",
        description="This is where level-up messages are sent."
                    " If empty, they'll be sent wherever the user is chatting.",
        component=TextInput(
            placeholder="Enter the channel ID here or leave empty",
            required=False,
            style=discord.TextStyle.short
        )
    )
    max_level_label = Label(
        text="Maximum level",
        description=f"Set the maximum level a user can reach. Maximum allowed is {XPDefaults.MAX_LEVEL}.",
        component=TextInput(
            min_length=1,
            placeholder="Enter the maximum level here",
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self,
                 interactions_handler,
                 level_up_message: str,
                 level_up_message_minimum_level: str,
                 level_up_message_channel_id: str,
                 max_level: str,
                 **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.level_up_message_label.component.default = level_up_message
        self.level_up_message_minimum_level_label.component.default = level_up_message_minimum_level
        self.level_up_channel_label.component.default = level_up_message_channel_id
        self.max_level_label.component.default = max_level

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_level_up_message_settings_modal_submit(
            interaction=interaction,
            level_up_message=self.level_up_message_label.component.value,
            level_up_message_minimum_level=self.level_up_message_minimum_level_label.component.value,
            level_up_message_channel_id=self.level_up_channel_label.component.value,
            max_level=self.max_level_label.component.value
        )


class XPDecaySettingsModal(BaseModal, title="XP Decay Settings"):
    decay_percentage_label = Label(
        text="Decay Percentage Per Day",
        description="% of user XP to be decayed per day after the grace period.",
        component=TextInput(
            min_length=1,
            placeholder=f"Recommended: {XPDefaults.DECAY_XP_PERCENTAGE}% or less.",
            required=True,
            style=discord.TextStyle.short
        )
    )
    decay_grace_period_label = Label(
        text="Decay Grace Period (in days)",
        description="Number of days a user must be inactive before decay starts.",
        component=TextInput(
            min_length=1,
            placeholder=f"Recommended: at least {XPDefaults.DECAY_DAYS_GRACE} days.",
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self,
                 interactions_handler,
                 xp_decay_per_day_percentage: str,
                 xp_decay_grace_period_days: str,
                 **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.decay_percentage_label.component.default = xp_decay_per_day_percentage
        self.decay_grace_period_label.component.default = xp_decay_grace_period_days

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_xp_decay_settings_modal_submit(
            interaction=interaction,
            xp_decay_per_day_percentage=self.decay_percentage_label.component.value,
            xp_decay_grace_period_days=self.decay_grace_period_label.component.value
        )


class AddXPLevelRoleModal(BaseModal, title="Set XP Level Role level"):
    level_label = Label(
        text="Level to award role",
        description="At what level should the role be awarded?",
        component=TextInput(
            placeholder="Enter the level here",
            max_length=3,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self, interactions_handler, role_id: int, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.role_id = role_id

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_level_role_add_modal_submit(
            interaction=interaction,
            role_id=self.role_id,
            level=self.level_label.component.value
        )
