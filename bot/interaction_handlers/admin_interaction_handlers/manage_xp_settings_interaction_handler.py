import asyncio
import re

import discord

from bot.interaction_handlers.admin_interaction_handlers import AdminInteractionHandler
from bot.utils.modal_factory.xp_settings_modals import XPGainSettingsModal, LevelUpMessageSettingsModal, \
    XPDecaySettingsModal, AddXPLevelRoleModal
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.xp_management_embeds import get_xp_setup_embed
from bot.utils.guild_logger import GuildLogEventField
from bot.utils.helpers.moderation_helpers import bot_can_assign_role
from bot.utils.view_factory.xp_management_views import get_xp_setup_view
from common.exceptions import UserInputException
from components.guild_settings_components.guild_xp_settings_component import GuildXPSettingsComponent
from constants import XPLevelUpMessageSubstitutable


class ManageXPSettingsInteractionHandler(AdminInteractionHandler):
    VIEW_NAME = "XP management"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.xp_settings_component = GuildXPSettingsComponent()

    @interaction_handler()
    async def toggle_xp_gain(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.guild_settings.xp_settings.xp_gain_enabled:
            new_state = False
            feedback = "XP gain has been disabled."
        else:
            new_state = True
            feedback = "XP gain has been enabled."
        await self.xp_settings_component.update_guild_xp_settings(
            guild_id=self.guild.id,
            xp_gain_enabled=new_state
        )
        await self.refresh_message(feedback=f"✅ {feedback}")
        await self.log_setting_change(event_text=feedback)

    @interaction_handler()
    async def toggle_level_up_message(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.guild_settings.xp_settings.level_up_message_enabled:
            new_state = False
            feedback = "Level-up messages have been disabled."
        else:
            new_state = True
            feedback = "Level-up messages have been enabled."
        await self.xp_settings_component.update_guild_xp_settings(
            guild_id=self.guild.id,
            level_up_message_enabled=new_state
        )
        await self.refresh_message(feedback=f"✅ {feedback}")
        await self.log_setting_change(event_text=feedback)

    @interaction_handler()
    async def toggle_xp_decay(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.guild_settings.xp_settings.xp_decay_enabled:
            new_state = False
            feedback = "XP decay has been disabled."
        else:
            new_state = True
            feedback = "XP decay has been enabled."
        await self.xp_settings_component.update_guild_xp_settings(
            guild_id=self.guild.id,
            xp_decay_enabled=new_state
        )
        await self.refresh_message(feedback=f"✅ {feedback}")
        await self.log_setting_change(event_text=feedback)

    @interaction_handler()
    async def go_to_xp_gain_settings(self, interaction: discord.Interaction):
        await interaction.response.send_modal(XPGainSettingsModal(
            interactions_handler=self,
            xp_gain_minimum=str(self.guild_settings.xp_settings.xp_gain_minimum),
            xp_gain_maximum=str(self.guild_settings.xp_settings.xp_gain_maximum),
            xp_gain_timeframe=str(self.guild_settings.xp_settings.xp_gain_timeframe),
            booster_xp_gain_multiplier=str(round(self.guild_settings.xp_settings.booster_xp_gain_multiplier, 2))
        ))

    @interaction_handler()
    async def on_xp_gain_settings_modal_submit(self,
                                               interaction: discord.Interaction,
                                               xp_gain_minimum: str,
                                               xp_gain_maximum: str,
                                               xp_gain_timeframe: str,
                                               booster_xp_gain_multiplier: str):
        if not xp_gain_maximum.isdigit() or not xp_gain_minimum.isdigit() or not xp_gain_timeframe.isdigit():
            raise UserInputException("Invalid input. Please enter valid numbers.")
        try:
            booster_xp_gain_multiplier = float(booster_xp_gain_multiplier)
        except:
            raise UserInputException("Invalid input for booster XP gain multiplier. Please enter a valid number.")

        xp_gain_maximum, xp_gain_minimum, xp_gain_timeframe = \
            int(xp_gain_maximum), int(xp_gain_minimum), int(xp_gain_timeframe)

        if xp_gain_maximum < xp_gain_minimum:
            raise UserInputException("Max XP gain cannot be less than min XP gain.")
        if xp_gain_maximum < 1 or xp_gain_minimum < 1:
            raise UserInputException("Max and min XP gain must be at least 1.")
        if xp_gain_maximum > 10000 or xp_gain_minimum > 10000:
            raise UserInputException("Max and min XP gain must be at most 10,000.")
        if not 10 >= xp_gain_timeframe <= 86400:
            raise UserInputException("Timeframe must be between 10 seconds and 1 day.")
        if not 0 >= booster_xp_gain_multiplier <= 1000:
            raise UserInputException("Booster bonus must be between 0% and 1000%.")

        updated_settings = {}
        if xp_gain_maximum != self.guild_settings.xp_settings.xp_gain_maximum:
            updated_settings['XP gain maximum'] = (f"{self.guild_settings.xp_settings.xp_gain_maximum}"
                                                   f" → {xp_gain_maximum}")
        if xp_gain_minimum != self.guild_settings.xp_settings.xp_gain_minimum:
            updated_settings['XP gain minimum'] = (f"{self.guild_settings.xp_settings.xp_gain_minimum} "
                                                   f"→ {xp_gain_minimum}")
        if xp_gain_timeframe != self.guild_settings.xp_settings.xp_gain_timeframe:
            updated_settings['XP gain timeframe'] = (f"{self.guild_settings.xp_settings.xp_gain_timeframe} "
                                                     f"→ {xp_gain_timeframe} seconds")
        if booster_xp_gain_multiplier != self.guild_settings.xp_settings.booster_xp_gain_multiplier:
            updated_settings['Booster XP gain multiplier'] = (f"{self.guild_settings.xp_settings
                                                              .booster_xp_gain_multiplier} "
                                                              f"→ {booster_xp_gain_multiplier:.2f}")

        await interaction.response.defer()
        if not updated_settings:
            await self.refresh_message(feedback="No changes were made to the XP gain settings.")
            return
        await self.xp_settings_component.update_guild_xp_settings(guild_id=self.guild.id,
                                                                  xp_gain_maximum=xp_gain_maximum,
                                                                  xp_gain_minimum=xp_gain_minimum,
                                                                  xp_gain_timeframe=xp_gain_timeframe,
                                                                  booster_xp_gain_multiplier=booster_xp_gain_multiplier)
        await self.refresh_message(feedback="✅ XP gain settings have been updated successfully.")
        await self.log_setting_change(event_text=f"Updated XP gain settings.",
                                      fields=[GuildLogEventField(name=name,
                                                                 value=value)
                                              for name, value in updated_settings.items()])

    @interaction_handler()
    async def go_to_level_up_message_settings(self, interaction: discord.Interaction):
        await interaction.response.send_modal(LevelUpMessageSettingsModal(
            interactions_handler=self,
            level_up_message=self.guild_settings.xp_settings.level_up_message_text,
            level_up_message_minimum_level=str(self.guild_settings.xp_settings.level_up_message_minimum_level),
            level_up_message_channel_id=str(self.guild_settings.xp_settings.level_up_message_channel_id or '') or None,
            max_level=str(self.guild_settings.xp_settings.max_level),
        ))

    @interaction_handler()
    async def on_level_up_message_settings_modal_submit(self,
                                                        interaction: discord.Interaction,
                                                        level_up_message: str,
                                                        level_up_message_minimum_level: str,
                                                        level_up_message_channel_id: str,
                                                        max_level: str):
        if ((level_up_message_channel_id and not level_up_message_channel_id.isdigit())
                or not level_up_message_minimum_level.isdigit()
                or (max_level and not max_level.isdigit())):
            raise UserInputException("Invalid input. Please enter valid numbers.")

        max_level, level_up_message_channel_id, level_up_message_minimum_level = \
            (int(max_level) if max_level else None,
             int(level_up_message_channel_id) if level_up_message_channel_id else None,
             int(level_up_message_minimum_level))
        if max_level is not None and max_level > 400:
            raise UserInputException("Max level cannot exceed 400.")
        if level_up_message_channel_id and not self.guild.get_channel(level_up_message_channel_id):
            raise UserInputException("Invalid channel selected for level-up messages.")
        if level_up_message_minimum_level > (max_level or 400):
            raise UserInputException("Minimum level for level-up messages cannot exceed max level.")

        level_up_message = (level_up_message
                            .replace('{tag}', '{member_name}')
                            .replace('{name}', '{member_name}')
                            .replace('{mention}', '{member_mention}')
                            .replace('{member}', '{member_mention}')
                            .replace('{user}', '{member_mention}'))
        if not set(re.findall("[{][^{}]+[}]", level_up_message)) \
                .issubset(set(XPLevelUpMessageSubstitutable.as_placeholders())):
            raise UserInputException("Invalid placeholders in level-up message. "
                                     f"Allowed placeholders: "
                                     f"{', '.join(XPLevelUpMessageSubstitutable.as_placeholders())}")

        updated_settings = {}
        if level_up_message != self.guild_settings.xp_settings.level_up_message_text:
            updated_settings['Old level-up message'] = self.guild_settings.xp_settings.level_up_message_text
            updated_settings['New level-up message'] = level_up_message
        if level_up_message_channel_id != self.guild_settings.xp_settings.level_up_message_channel_id:
            new_channel_text = f"<#{level_up_message_channel_id}>" if level_up_message_channel_id \
                else "Wherever the user is chatting"
            old_channel_text = f"<#{self.guild_settings.xp_settings.level_up_message_channel_id}>" \
                if self.guild_settings.xp_settings.level_up_message_channel_id \
                else "Wherever the user is chatting"
            updated_settings['Level-up message channel'] = f"{old_channel_text} → {new_channel_text}"
        if max_level != self.guild_settings.xp_settings.max_level:
            updated_settings['Max level'] = f"{self.guild_settings.xp_settings.max_level} → {max_level}"
        if level_up_message_minimum_level != self.guild_settings.xp_settings.level_up_message_minimum_level:
            updated_settings['Level-up message minimum level'] = \
                f"{self.guild_settings.xp_settings.level_up_message_minimum_level} " \
                f"→ {level_up_message_minimum_level}"

        await interaction.response.defer()
        if not updated_settings:
            await self.refresh_message(feedback="No changes were made to the level-up message settings.")
            return
        await self.xp_settings_component.update_guild_xp_settings(
            guild_id=self.guild.id,
            level_up_message_text=level_up_message,
            level_up_message_minimum_level=level_up_message_minimum_level,
            level_up_message_channel_id=level_up_message_channel_id,
            max_level=max_level
        )
        await self.refresh_message(feedback="✅ Level-up message settings have been updated successfully.")
        await self.log_setting_change(event_text=f"Updated level-up message settings.",
                                      fields=[GuildLogEventField(name=name, value=value)
                                              for name, value in updated_settings.items()])

    @interaction_handler()
    async def go_to_xp_decay_settings(self, interaction: discord.Interaction):
        await interaction.response.send_modal(XPDecaySettingsModal(
            interactions_handler=self,
            xp_decay_per_day_percentage=str(self.guild_settings.xp_settings.xp_decay_per_day_percentage),
            xp_decay_grace_period_days=str(self.guild_settings.xp_settings.xp_decay_grace_period_days)
        ))

    @interaction_handler()
    async def on_xp_decay_settings_modal_submit(self,
                                                interaction: discord.Interaction,
                                                xp_decay_per_day_percentage: str,
                                                xp_decay_grace_period_days: str):
        if not xp_decay_grace_period_days.isdigit():
            raise UserInputException("Invalid input. Please enter a valid number for grace period.")
        xp_decay_grace_period_days = int(xp_decay_grace_period_days)
        try:
            xp_decay_per_day_percentage = float(xp_decay_per_day_percentage)
        except:
            raise UserInputException("Invalid input for XP decay percentage. Please enter a valid number.")
        if not (0 <= xp_decay_per_day_percentage <= 100):
            raise UserInputException("Invalid input. Please enter a percentage between 0 and 100.")
        if xp_decay_grace_period_days < 1:
            raise UserInputException("Invalid input. Grace period must be at least 1 day.")

        updated_settings = {}
        if xp_decay_per_day_percentage != self.guild_settings.xp_settings.xp_decay_per_day_percentage:
            updated_settings['XP decay percentage per day'] = \
                f"{self.guild_settings.xp_settings.xp_decay_per_day_percentage}% → {xp_decay_per_day_percentage}%"
        if xp_decay_grace_period_days != self.guild_settings.xp_settings.xp_decay_grace_period_days:
            updated_settings['XP decay grace period (days)'] = \
                f"{self.guild_settings.xp_settings.xp_decay_grace_period_days} → {xp_decay_grace_period_days} days"

        await interaction.response.defer()
        if not updated_settings:
            await self.refresh_message(feedback="No changes were made to the XP decay settings.")
            return
        await self.xp_settings_component.update_guild_xp_settings(
            guild_id=self.guild.id,
            xp_decay_per_day_percentage=xp_decay_per_day_percentage,
            xp_decay_grace_period_days=xp_decay_grace_period_days
        )
        await self.refresh_message(feedback="✅ XP decay settings have been updated successfully.")
        await self.log_setting_change(event_text=f"Updated XP decay settings.",
                                      fields=[GuildLogEventField(name=name, value=value)
                                              for name, value in updated_settings.items()])

    @interaction_handler()
    async def toggle_level_role_stacking(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.guild_settings.xp_settings.stack_level_roles:
            new_state = False
            feedback = "Level role stacking has been disabled."
        else:
            new_state = True
            feedback = "Level role stacking has been enabled."
        await self.xp_settings_component.update_guild_xp_settings(
            guild_id=self.guild.id,
            stack_level_roles=new_state
        )
        await self.refresh_message(feedback=f"✅ {feedback}")
        await self.log_setting_change(event_text=feedback)

    @interaction_handler()
    async def on_level_role_select(self, interaction: discord.Interaction):
        role_id = int(interaction.data['values'][0])
        for level, role_ids in self.guild_settings.xp_settings.level_role_ids_map.items():
            if role_id in role_ids:
                await interaction.response.defer()
                await self.xp_settings_component.remove_xp_level_role(guild_id=self.guild.id,
                                                                      role_id=role_id,
                                                                      level=level)
                await self.refresh_message(feedback=f"✅ Role has been removed from level {level}.")
                await self.log_setting_change(event_text="Removed level role",
                                              fields=[GuildLogEventField(name="Role",
                                                                         value=f"<@&{role_id}> (ID: {role_id})"),
                                                      GuildLogEventField(name="Level",
                                                                         value=str(level))])
                return
        role = self.guild.get_role(role_id)
        if not bot_can_assign_role(role=role):
            raise UserInputException("I cannot assign this role. This could be due to role hierarchy or permissions.")
        await interaction.response.send_modal(AddXPLevelRoleModal(
            interactions_handler=self,
            role_id=role_id,
        ))

    @interaction_handler()
    async def on_level_role_add_modal_submit(self,
                                             interaction: discord.Interaction,
                                             role_id: int,
                                             level: str):
        if not level.isdigit():
            await self.refresh_message()
            raise UserInputException("Invalid input. Please enter a valid level number.")
        await interaction.response.defer()
        await self.xp_settings_component.add_xp_level_role(
            guild_id=self.guild.id,
            guild_xp_settings_id=self.guild_settings.xp_settings.guild_xp_settings_id,
            role_id=role_id,
            level=int(level)
        )
        await self.refresh_message(feedback="✅ Level role has been added successfully.")
        await self.log_setting_change(event_text="Added level role",
                                      fields=[GuildLogEventField(name="Role",
                                                                 value=f"<@&{role_id}> (ID: {role_id})"),
                                              GuildLogEventField(name="Level",
                                                                 value=str(level))])

    @interaction_handler()
    async def on_ignored_channel_select(self, interaction: discord.Interaction):
        channel_id = int(interaction.data['values'][0])
        if channel_id in self.guild_settings.xp_settings.ignored_channel_ids:
            await interaction.response.defer()
            await self.xp_settings_component.remove_ignored_channel(guild_id=self.guild.id, channel_id=channel_id)
            await self.refresh_message(feedback="✅ Channel has been removed from the ignored channels list.")
            await self.log_setting_change(event_text="Removed ignored channel for XP gain",
                                          fields=[GuildLogEventField(name="Channel",
                                                                     value=f"<#{channel_id}> (ID: {channel_id})")])
            return
        channel = self.guild.get_channel(channel_id)
        if not channel:
            raise UserInputException("Invalid channel selected.")
        await interaction.response.defer()
        await self.xp_settings_component.add_ignored_channel(
            guild_xp_settings_id=self.guild_settings.xp_settings.guild_xp_settings_id,
            guild_id=self.guild.id,
            channel_id=channel_id
        )
        await self.refresh_message(feedback="✅ Channel has been added to the ignored channels list.")
        await self.log_setting_change(event_text="Added ignored channel for XP gain",
                                      fields=[GuildLogEventField(name="Channel",
                                                                 value=f"<#{channel_id}> (ID: {channel_id})")])

    @interaction_handler()
    async def on_ignored_role_select(self, interaction: discord.Interaction):
        role_id = int(interaction.data['values'][0])
        if role_id in self.guild_settings.xp_settings.ignored_role_ids:
            await interaction.response.defer()
            await self.xp_settings_component.remove_ignored_role(guild_id=self.guild.id, role_id=role_id)
            await self.refresh_message(feedback="✅ Role has been removed from the ignored roles list.")
            await self.log_setting_change(event_text="Removed ignored role for XP gain",
                                          fields=[GuildLogEventField(name="Role",
                                                                     value=f"<@&{role_id}> (ID: {role_id})")])
            return
        role = self.guild.get_role(role_id)
        if not role:
            raise UserInputException("Invalid role selected.")
        await interaction.response.defer()
        await self.xp_settings_component.add_ignored_role(
            guild_xp_settings_id=self.guild_settings.xp_settings.guild_xp_settings_id,
            guild_id=self.guild.id,
            role_id=role_id
        )
        await self.refresh_message(feedback="✅ Role has been added to the ignored roles list.")
        await self.log_setting_change(event_text="Added ignored role for XP gain",
                                      fields=[GuildLogEventField(name="Role",
                                                                 value=f"<@&{role_id}> (ID: {role_id})")])

    async def refresh_message(self, no_view: bool = False, feedback: str | None = None, *args, **kwargs):
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        if not no_view and view is not None:
            await asyncio.sleep(0.5)
            await self.source_interaction.edit_original_response(embed=embed, view=view)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        embed = get_xp_setup_embed(guild=self.guild,
                                   xp_settings=self.guild_settings.xp_settings,
                                   feedback_message=feedback)
        view = get_xp_setup_view(interactions_handler=self,
                                 xp_gain_enabled=self.guild_settings.xp_settings.xp_gain_enabled,
                                 level_up_message_enabled=self.guild_settings.xp_settings.level_up_message_enabled,
                                 xp_decay_enabled=self.guild_settings.xp_settings.xp_decay_enabled,
                                 level_roles_added=bool(self.guild_settings.xp_settings.level_role_ids_map),
                                 level_role_stacking_enabled=self.guild_settings.xp_settings.stack_level_roles)
        return embed, view

    async def fetch_and_cleanup_channels_and_roles(self):
        """
        Fetches the roles from the role menu message and cleans up any invalid roles.
        """
        invalid_role_ids = []
        invalid_channel_ids = []
        for role_id in self.guild_settings.xp_settings.ignored_role_ids:
            if not self.guild.get_role(role_id):
                invalid_role_ids.append(role_id)
        for channel_id in self.guild_settings.xp_settings.ignored_channel_ids:
            if not self.guild.get_channel(channel_id):
                invalid_channel_ids.append(channel_id)
        for role_id in invalid_role_ids:
            await self.xp_settings_component.remove_ignored_role(guild_id=self.guild.id,
                                                                 role_id=role_id)
        for channel_id in invalid_channel_ids:
            await self.xp_settings_component.remove_ignored_channel(guild_id=self.guild.id,
                                                                    channel_id=channel_id)
