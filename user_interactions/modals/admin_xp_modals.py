import discord
from utils.decorators import interaction_handler
from user_interactions.modals.base_modal import BaseModal


class XPGainSettingsModal(BaseModal, title="XP Gain Settings"):
    max_xp_gain_input = discord.ui.TextInput(label="Maximum XP Gain per timeframe",
                                             max_length=100,
                                             min_length=1,
                                             placeholder="Default: 40",
                                             required=True,
                                             style=discord.TextStyle.short)
    min_xp_gain_input = discord.ui.TextInput(label="Minimum XP Gain per timeframe",
                                             max_length=100,
                                             min_length=1,
                                             placeholder="Default: 20",
                                             required=True,
                                             style=discord.TextStyle.short)
    xp_gain_timeframe_input = discord.ui.TextInput(label="Timeframe for XP Gain (in seconds)",
                                                   max_length=100,
                                                   min_length=1,
                                                   placeholder="Default: 60",
                                                   required=True,
                                                   style=discord.TextStyle.short)
    booster_bonus_input = discord.ui.TextInput(label="Booster Bonus (in %)",
                                               max_length=100,
                                               min_length=1,
                                               placeholder="Default: 0%",
                                               required=True,
                                               style=discord.TextStyle.short)

    def __init__(self, interactions_handler, current_max_xp_gain, current_min_xp_gain, current_xp_gain_timeframe,
                 current_booster_bonus, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.max_xp_gain_input.default = current_max_xp_gain
        self.min_xp_gain_input.default = current_min_xp_gain
        self.xp_gain_timeframe_input.default = current_xp_gain_timeframe
        self.booster_bonus_input.default = str(current_booster_bonus)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_xp_gain_settings_modal_submit(
            inter=interaction,
            max_xp_gain=self.max_xp_gain_input.value,
            min_xp_gain=self.min_xp_gain_input.value,
            xp_gain_timeframe=self.xp_gain_timeframe_input.value,
            booster_bonus=self.booster_bonus_input.value
        )


class LevelUpMessageSettingsModal(BaseModal, title="LevelUp Message Settings"):
    levelup_message_input = discord.ui.TextInput(label="LevelUp message",
                                                 min_length=1,
                                                 max_length=1500,
                                                 placeholder="Enter the message here",
                                                 required=True,
                                                 style=discord.TextStyle.long)
    levelup_channel_input = discord.ui.TextInput(label="LevelUp channel",
                                                 placeholder="Enter the channel ID here or leave empty",
                                                 required=False,
                                                 style=discord.TextStyle.short)
    max_level_input = discord.ui.TextInput(label="Maximum level",
                                           min_length=1,
                                           placeholder="Enter the maximum level here",
                                           required=False,
                                           style=discord.TextStyle.short)

    def __init__(self, interactions_handler, current_levelup_message, current_levelup_channel_id,
                 current_max_level, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.levelup_message_input.default = current_levelup_message
        self.levelup_channel_input.default = current_levelup_channel_id
        self.max_level_input.default = current_max_level

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_levelup_message_settings_modal_submit(
            inter=interaction,
            levelup_message=self.levelup_message_input.value,
            levelup_channel_id=self.levelup_channel_input.value,
            max_level=self.max_level_input.value
        )


class XPDecaySettingsModal(BaseModal, title="XP Decay Settings"):
    decay_percentage_input = discord.ui.TextInput(label="Decay Percentage Per Day (in %)",
                                                  min_length=1,
                                                  placeholder="By default 1.0%",
                                                  required=True,
                                                  style=discord.TextStyle.short)
    decay_grace_period_input = discord.ui.TextInput(label="Decay Grace Period (in days)",
                                                    min_length=1,
                                                    placeholder="By default 7 days",
                                                    required=True,
                                                    style=discord.TextStyle.short)

    def __init__(self, interactions_handler, current_decay_percentage, current_decay_grace_period, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.decay_percentage_input.default = str(current_decay_percentage)
        self.decay_grace_period_input.default = current_decay_grace_period

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_xp_decay_settings_modal_submit(
            inter=interaction,
            decay_percentage=self.decay_percentage_input.value,
            decay_grace_period=self.decay_grace_period_input.value
        )


class AddLevelRoleModal(BaseModal, title="Add Level Role"):
    level_input = discord.ui.TextInput(label="At what level should the role be awarded?",
                                       min_length=1,
                                       placeholder="Enter the level here",
                                       required=True,
                                       style=discord.TextStyle.short)

    def __init__(self, interactions_handler, role_id, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.role_id = role_id

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_add_level_role_modal_submit(
            inter=interaction,
            level=self.level_input.value,
            role_id=self.role_id
        )


class XPTransferResetConfirmationModal(BaseModal, title="Reset XP Confirmation"):
    reset_input = discord.ui.TextInput(label="Type 'reset' to confirm",
                                       min_length=5,
                                       max_length=5,
                                       placeholder="This action cannot be undone!",
                                       required=True,
                                       style=discord.TextStyle.short)

    def __init__(self, interactions_handler, selected_role=None, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.selected_role = selected_role

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_xp_transfer_reset_confirmation_modal_submit(
            inter=interaction,
            selected_role=self.selected_role
        )


class XPTransferAmountModal(BaseModal, title="Transfer XP"):
    amount_input = discord.ui.TextInput(label="How much XP to {action} for {target}?",
                                        min_length=1,
                                        placeholder="Enter the amount here",
                                        required=True,
                                        style=discord.TextStyle.short)

    def __init__(self, interactions_handler, target, action, selected_role=None, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.amount_input.label = self.amount_input.label.format(action=action.value,
                                                                 target=target.value)
        self.selected_role = selected_role

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_xp_transfer_amount_modal_submit(
            inter=interaction,
            amount=self.amount_input.value,
            selected_role=self.selected_role
        )


class XPTransferEnterUserIDModal(BaseModal, title="XP Action on a User ID"):
    user_id_input = discord.ui.TextInput(label="Enter user ID",
                                         min_length=1,
                                         placeholder="Enter the ID here",
                                         required=True,
                                         style=discord.TextStyle.short)

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_member_select(
            interaction,
            user_id=self.user_id_input.value,
        )
