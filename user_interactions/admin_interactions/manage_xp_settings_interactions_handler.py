import asyncio
import re
import discord
from discord import ButtonStyle
from utils.embed_factory import make_xp_overview_embed
from globals_.constants import XPSettingsKey
from utils.helpers import get_xp_settings_views, quick_button_views, get_curly_bracketed_parameters_from_text
from utils.decorators import interaction_handler
from user_interactions.admin_interactions.base_admin_interactions_handler import AdminInteractionsHandler
from user_interactions.modals.admin_xp_modals import XPGainSettingsModal, XPDecaySettingsModal, \
    LevelUpMessageSettingsModal, AddLevelRoleModal


class ManageXPSettingsInteractionsHandler(AdminInteractionsHandler):

    def __init__(self, source_interaction, guild):
        super().__init__(source_interaction=source_interaction, guild=guild)

    @interaction_handler
    async def handle_xp_gain_toggle(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.defer()
        disabled = self.guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_ENABLED]

        await self.guild_prefs_component.set_xp_setting(guild=self.guild, setting=XPSettingsKey.XP_GAIN_ENABLED,
                                                        value=not disabled)
        await self.log_action_to_server(event=f"{'Disabled' if disabled else 'Enabled'} XP gain on this server.")

        await self.refresh_setup_message(feedback_message=f"XP gain has been {'disabled' if disabled else 'enabled'}")

    @interaction_handler
    async def handle_levelup_message_toggle(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.defer()
        disabled = self.guild_prefs.xp_settings[XPSettingsKey.LEVELUP_ENABLED]

        await self.guild_prefs_component.set_xp_setting(guild=self.guild, setting=XPSettingsKey.LEVELUP_ENABLED,
                                                        value=not disabled)
        await self.log_action_to_server(event=f"{'Disabled' if disabled else 'Enabled'}"
                                              f" levelup messages on this server.")

        await self.refresh_setup_message(feedback_message=f"Levelup messages have been "
                                                          f"{'disabled' if disabled else 'enabled'}")

    @interaction_handler
    async def handle_xp_decay_toggle(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.defer()
        disabled = self.guild_prefs.xp_settings[XPSettingsKey.XP_DECAY_ENABLED]

        await self.guild_prefs_component.set_xp_setting(guild=self.guild, setting=XPSettingsKey.XP_DECAY_ENABLED,
                                                        value=not disabled)
        await self.log_action_to_server(event=f"{'Disabled' if disabled else 'Enabled'} XP decay on this server.")

        await self.refresh_setup_message(feedback_message=f"XP decay has been {'disabled' if disabled else 'enabled'}")

    @interaction_handler
    async def handle_xp_gain_settings(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(XPGainSettingsModal(
            interactions_handler=self,
            current_max_xp_gain=self.guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_MAX],
            current_min_xp_gain=self.guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_MIN],
            current_xp_gain_timeframe=self.guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME],
            current_booster_bonus=self.guild_prefs.xp_settings[XPSettingsKey.BOOST_EXTRA_GAIN]
        ))

    async def handle_xp_gain_settings_modal_submit(self, inter: discord.Interaction, max_xp_gain, min_xp_gain,
                                                   xp_gain_timeframe, booster_bonus):
        await inter.response.defer()

        if not max_xp_gain.isdigit() or not min_xp_gain.isdigit() \
                or not xp_gain_timeframe.isdigit():
            return await self.refresh_setup_message(feedback_message="⚠️ Max Gain , Min Gain and Timeframe"
                                                                     " must be numbers (integers).")

        if not re.match(r"^\d+\.\d+$", booster_bonus) and not booster_bonus.isdigit():
            return await self.refresh_setup_message(feedback_message="⚠️ Booster Bonus must be a number.")

        max_xp_gain = int(max_xp_gain)
        min_xp_gain = int(min_xp_gain)
        xp_gain_timeframe = int(xp_gain_timeframe)
        booster_bonus = float(booster_bonus)

        if max_xp_gain < min_xp_gain:
            return await self.refresh_setup_message(feedback_message="⚠️ Max XP gain cannot be less than min XP gain.")
        if max_xp_gain < 1 or min_xp_gain < 1:
            return await self.refresh_setup_message(feedback_message="⚠️ Max and min XP gain must be at least 1.")
        if max_xp_gain > 10000 or min_xp_gain > 10000:
            return await self.refresh_setup_message(feedback_message="⚠️ Max and min XP gain must be at most 10,000.")
        if not xp_gain_timeframe >= 10 or not xp_gain_timeframe <= 86400:
            return await self.refresh_setup_message(feedback_message="⚠️ Timeframe must be between 10 "
                                                                     "seconds and 1 day.")
        if not booster_bonus >= 0 or not booster_bonus <= 1000:
            return await self.refresh_setup_message(feedback_message="⚠️ Booster bonus must be between 0% and 1000%.")

        xp_settings = self.guild_prefs.xp_settings
        old_max = xp_settings[XPSettingsKey.XP_GAIN_MAX]
        old_min = xp_settings[XPSettingsKey.XP_GAIN_MIN]
        old_timeframe = xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME]
        old_booster_bonus = xp_settings[XPSettingsKey.BOOST_EXTRA_GAIN]
        changes_map = {}
        if old_max != max_xp_gain:
            changes_map["Max XP gain"] = f"{old_max} -> {max_xp_gain}"
            xp_settings[XPSettingsKey.XP_GAIN_MAX] = max_xp_gain
        if old_min != min_xp_gain:
            changes_map["Min XP gain"] = f"{old_min} -> {min_xp_gain}"
            xp_settings[XPSettingsKey.XP_GAIN_MIN] = min_xp_gain
        if old_timeframe != xp_gain_timeframe:
            changes_map["Timeframe"] = f"{old_timeframe} -> {xp_gain_timeframe}"
            xp_settings[XPSettingsKey.XP_GAIN_TIMEFRAME] = xp_gain_timeframe
        if old_booster_bonus != booster_bonus:
            changes_map["Booster bonus"] = f"{old_booster_bonus} -> {booster_bonus}"
            xp_settings[XPSettingsKey.BOOST_EXTRA_GAIN] = booster_bonus

        if not changes_map:
            return await self.refresh_setup_message(feedback_message="No changes were made.")

        xp_settings[XPSettingsKey.XP_GAIN_MIN] = min_xp_gain
        xp_settings[XPSettingsKey.BOOST_EXTRA_GAIN] = booster_bonus
        await self.guild_prefs_component.set_xp_settings(guild=self.guild, settings=xp_settings)
        await self.refresh_setup_message(feedback_message="XP gain settings have been updated.")

        await self.log_action_to_server(event="Updated XP gain settings",
                                        field_value_map=changes_map)

    @interaction_handler
    async def handle_levelup_message_settings(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(LevelUpMessageSettingsModal(
            interactions_handler=self,
            current_levelup_message=self.guild_prefs.xp_settings[XPSettingsKey.LEVELUP_MESSAGE],
            current_levelup_channel_id=self.guild_prefs.xp_settings[XPSettingsKey.LEVELUP_CHANNEL],
            current_max_level=self.guild_prefs.xp_settings[XPSettingsKey.LEVEL_MAX]
        ))

    async def handle_levelup_message_settings_modal_submit(self, inter: discord.Interaction, levelup_message,
                                                           levelup_channel_id, max_level):
        await inter.response.defer()

        max_level = max_level or '400'
        if not max_level.isdigit():
            return await self.refresh_setup_message(feedback_message="⚠️ Max Level must be a number (integer).")
        max_level = int(max_level)
        if max_level > 400 or max_level < 0:
            return await self.refresh_setup_message(feedback_message="⚠️ Max Level must be at most 400 (that's the "
                                                                     "furthest I can go anyway).")

        levelup_channel_id = levelup_channel_id or 0

        if levelup_channel_id and not levelup_channel_id.isdigit():
            return await self.refresh_setup_message(feedback_message="⚠️ LevelUp channel ID must be a number or empty.")

        if levelup_channel_id:
            levelup_channel_id = int(levelup_channel_id)
            if not self.guild.get_channel(levelup_channel_id):
                return await self.refresh_setup_message(feedback_message="⚠️ Cannot find a channel with that ID.")

        # people do be dumb sometimes
        if '{mention}' in levelup_message:
            levelup_message = levelup_message.replace('{mention}', '{member_mention}')
        if '{tag}' in levelup_message:
            levelup_message = levelup_message.replace('{tag}', '{member_tag}')
        if '{member}' in levelup_message:
            levelup_message = levelup_message.replace('{member}', '{member_mention}')
        if '{user}' in levelup_message:
            levelup_message = levelup_message.replace('{user}', '{member_mention}')
        curly_bracketed_parameters = get_curly_bracketed_parameters_from_text(levelup_message)
        if any(param not in ['{member_mention}', '{member_tag}', '{level}'] for param in curly_bracketed_parameters):
            return await self.refresh_setup_message(feedback_message="⚠️ Invalid parameter in LevelUp message. "
                                                                     "Valid parameters are: **{member_mention}**, "
                                                                     "**{member_tag}** and **{level}**.")

        xp_settings = self.guild_prefs.xp_settings
        old_levelup_message = xp_settings[XPSettingsKey.LEVELUP_MESSAGE]
        old_levelup_channel_id = xp_settings[XPSettingsKey.LEVELUP_CHANNEL]
        old_max_level = xp_settings[XPSettingsKey.LEVEL_MAX]
        changes_map = {}

        if old_levelup_message != levelup_message:
            changes_map["LevelUp message"] = f"{levelup_message}"
            xp_settings[XPSettingsKey.LEVELUP_MESSAGE] = levelup_message
        if old_levelup_channel_id != levelup_channel_id:
            old_channel = self.guild.get_channel(old_levelup_channel_id) if old_levelup_channel_id else "None"
            new_channel = self.guild.get_channel(levelup_channel_id) if levelup_channel_id else "None"
            changes_map["LevelUp channel"] = f"{old_channel} -> {new_channel}"
            xp_settings[XPSettingsKey.LEVELUP_CHANNEL] = levelup_channel_id
        if old_max_level != max_level:
            changes_map["Max Level"] = f"{old_max_level} -> {max_level}"
            xp_settings[XPSettingsKey.LEVEL_MAX] = max_level

        if not changes_map:
            return await self.refresh_setup_message(feedback_message="No changes were made.")

        await self.guild_prefs_component.set_xp_settings(guild=self.guild, settings=xp_settings)
        await self.refresh_setup_message(feedback_message="LevelUp Message settings have been updated.")

        await self.log_action_to_server(event="Updated LevelUp Message settings",
                                        field_value_map=changes_map)

    @interaction_handler
    async def handle_xp_decay_settings(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(XPDecaySettingsModal(
            interactions_handler=self,
            current_decay_percentage=self.guild_prefs.xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY],
            current_decay_grace_period=self.guild_prefs.xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY],
        ))

    async def handle_xp_decay_settings_modal_submit(self, inter: discord.Interaction, decay_percentage,
                                                    decay_grace_period):
        await inter.response.defer()

        if not decay_grace_period.isdigit():
            return await self.refresh_setup_message(feedback_message="⚠️ XP Decay grace period must be"
                                                                     " a number (integer).")
        decay_grace_period = int(decay_grace_period)

        if decay_grace_period < 1:
            return await self.refresh_setup_message(feedback_message="⚠️ XP Decay grace period must be at least 1 day.")

        if not re.match(r"^\d+\.\d+$", decay_percentage) and not decay_percentage.isdigit():
            return await self.refresh_setup_message(feedback_message="⚠️ XP Decay percentage must be a number "
                                                                     "(decimal).")
        decay_percentage = float(decay_percentage)

        if decay_percentage > 100 or decay_percentage < 0:
            return await self.refresh_setup_message(feedback_message="⚠️ XP Decay percentage must be at most 100%.")

        xp_settings = self.guild_prefs.xp_settings
        old_decay_percentage = xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY]
        old_decay_grace_period = xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY]
        changes_map = {}

        if old_decay_percentage != decay_percentage:
            changes_map["XP Decay percentage"] = f"{old_decay_percentage}% -> {decay_percentage}%"
            xp_settings[XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY] = decay_percentage
        if old_decay_grace_period != decay_grace_period:
            changes_map["XP Decay grace period"] = f"{old_decay_grace_period} -> {decay_grace_period}"
            xp_settings[XPSettingsKey.DAYS_BEFORE_XP_DECAY] = decay_grace_period

        if not changes_map:
            return await self.refresh_setup_message(feedback_message="No changes were made.")

        await self.guild_prefs_component.set_xp_settings(guild=self.guild, settings=xp_settings)
        await self.refresh_setup_message(feedback_message="XP Decay settings have been updated.")

        await self.log_action_to_server(event="Updated XP Decay settings",
                                        field_value_map=changes_map)

    @interaction_handler
    async def handle_stack_roles_toggle(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.defer()
        disabled = self.guild_prefs.xp_settings[XPSettingsKey.STACK_ROLES]

        await self.guild_prefs_component.set_xp_setting(guild=self.guild, setting=XPSettingsKey.STACK_ROLES,
                                                        value=not disabled)
        await self.log_action_to_server(event=f"{'Disabled' if disabled else 'Enabled'} "
                                              f"level role stacking on this server.")

        await self.refresh_setup_message(feedback_message=f"Level role stacking has been "
                                                          f"{'disabled' if disabled else 'enabled'}")

    @interaction_handler
    async def handle_level_role_select(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        role_id = int(inter.data["values"][0])

        role = self.guild.get_role(role_id)
        if not self.is_role_assignable(role):
            await inter.response.defer()
            return await self.refresh_setup_message(feedback_message="⚠️ The role you selected is not assignable.")

        level_role_map = self.guild_prefs.xp_settings[XPSettingsKey.LEVEL_ROLES]
        role_level_map = {v: k for k, v in level_role_map.items()}

        if role_id in role_level_map:
            await inter.response.defer()
            level_role_map.pop(role_level_map[role_id])
            await self.guild_prefs_component.set_xp_setting(guild=self.guild,
                                                            setting=XPSettingsKey.LEVEL_ROLES,
                                                            value=level_role_map)
            await self.refresh_setup_message(feedback_message=f"Removed level role for level {role_level_map[role_id]}")
            await self.log_action_to_server(event="Removed level role",
                                            field_value_map={"Level": role_level_map[role_id]})
            return

        await inter.response.send_modal(AddLevelRoleModal(
            interactions_handler=self,
            role_id=role_id,
        ))

    async def handle_add_level_role_modal_submit(self, inter: discord.Interaction, level, role_id):
        await inter.response.defer()

        if not level.isdigit():
            return await self.refresh_setup_message(feedback_message="⚠️ Level must be a number (integer).")
        level = int(level)

        level_role_map = self.guild_prefs.xp_settings[XPSettingsKey.LEVEL_ROLES]

        if level in level_role_map:
            return await self.refresh_setup_message(feedback_message="⚠️ There is already a role set for this level.")

        if level < 1 or level > 400:
            return await self.refresh_setup_message(feedback_message="⚠️ Level must be between 1 and 400.")

        role = self.guild.get_role(role_id)

        level_role_map[level] = role_id
        sorted_level_roles = dict(sorted(level_role_map.items()))
        await self.guild_prefs_component.set_xp_setting(guild=self.guild,
                                                        setting=XPSettingsKey.LEVEL_ROLES,
                                                        value=sorted_level_roles)
        await self.refresh_setup_message(feedback_message=f"Added level role for level {level} ({role.mention})")
        await self.log_action_to_server(event="Added level role",
                                        field_value_map={"Level": level,
                                                         "Role": role.mention})

    @interaction_handler
    async def handle_ignored_channel_select(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()

        channel_id = int(inter.data["values"][0])
        channel = self.guild.get_channel(channel_id)

        if channel.type == discord.ChannelType.category:
            return await self.refresh_setup_message(feedback_message="⚠️ Please select a text channel.")

        ignored_channels = self.guild_prefs.xp_settings[XPSettingsKey.IGNORED_CHANNELS]

        if channel_id in ignored_channels:
            ignored_channels.remove(channel_id)
            await self.guild_prefs_component.set_xp_setting(guild=self.guild,
                                                            setting=XPSettingsKey.IGNORED_CHANNELS,
                                                            value=ignored_channels)
            await self.refresh_setup_message(feedback_message=f"Removed {channel.mention} from the list of ignored "
                                                              f"channels.")
            await self.log_action_to_server(event="Removed ignored channel for XP Gain",
                                            field_value_map={"Channel": channel.mention})
            return

        ignored_channels.append(channel_id)
        await self.guild_prefs_component.set_xp_setting(guild=self.guild,
                                                        setting=XPSettingsKey.IGNORED_CHANNELS,
                                                        value=ignored_channels)
        await self.refresh_setup_message(feedback_message=f"Added {channel.mention} to the list of ignored channels.")
        await self.log_action_to_server(event="Added ignored channel for XP Gain",
                                        field_value_map={"Channel": channel.mention})

    @interaction_handler
    async def handle_ignored_role_select(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()

        role_id = int(inter.data["values"][0])
        role = self.guild.get_role(role_id)

        ignored_roles = self.guild_prefs.xp_settings[XPSettingsKey.IGNORED_ROLES]

        if role_id in ignored_roles:
            ignored_roles.remove(role_id)
            await self.guild_prefs_component.set_xp_setting(guild=self.guild,
                                                            setting=XPSettingsKey.IGNORED_ROLES,
                                                            value=ignored_roles)
            await self.refresh_setup_message(feedback_message=f"Removed {role.mention} from the list of ignored roles.")
            await self.log_action_to_server(event="Removed ignored role for XP Gain",
                                            field_value_map={"Role": role.mention})
            return

        ignored_roles.append(role_id)
        await self.guild_prefs_component.set_xp_setting(guild=self.guild,
                                                        setting=XPSettingsKey.IGNORED_ROLES,
                                                        value=ignored_roles)
        await self.refresh_setup_message(feedback_message=f"Added {role.mention} to the list of ignored roles.")
        await self.log_action_to_server(event="Added ignored role for XP Gain",
                                        field_value_map={"Role": role.mention})

    @interaction_handler
    async def switch_to_edit_mode(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.defer()
        await self.refresh_setup_message(is_overview=False)

    def get_embed_and_views(self, is_overview=False, feedback_message=None):
        embed = make_xp_overview_embed(xp_settings=self.guild_prefs.xp_settings,
                                       requested_by=self.member,
                                       feedback_message=feedback_message)
        if is_overview:
            return embed, quick_button_views(button_callback_map={"Edit Settings": self.switch_to_edit_mode},
                                             styles=[ButtonStyle.green],
                                             on_timeout=self.on_timeout)
        views = get_xp_settings_views(
            xp_gain_enabled=self.guild_prefs.xp_settings[XPSettingsKey.XP_GAIN_ENABLED],
            levelup_message_enabled=self.guild_prefs.xp_settings[XPSettingsKey.LEVELUP_ENABLED],
            xp_decay_enabled=self.guild_prefs.xp_settings[XPSettingsKey.XP_DECAY_ENABLED],
            level_roles_added=bool(self.guild_prefs.xp_settings[XPSettingsKey.LEVEL_ROLES]),
            stack_level_roles_enabled=self.guild_prefs.xp_settings[XPSettingsKey.STACK_ROLES],
            interactions_handler=self
        )
        return embed, views

    async def refresh_setup_message(self, is_overview=False, feedback_message=None):
        embed, views = self.get_embed_and_views(is_overview=is_overview, feedback_message=feedback_message)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        await asyncio.sleep(0.5)
        await self.source_interaction.edit_original_response(embed=embed, view=views)
