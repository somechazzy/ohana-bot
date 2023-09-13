import asyncio
import discord
from discord import ButtonStyle

from actions import create_role
from auto_moderation.role_management import scan_and_assign_role_for_single_message_channel
from utils.embed_factory import make_single_message_channels_management_embed, quick_embed
from utils.helpers import get_channels_management_views, quick_button_views
from user_interactions.admin_interactions.base_admin_interactions_handler import AdminInteractionsHandler
from utils.decorators import interaction_handler
from user_interactions.modals.admin_general_modals import SingleMessageChannelsRoleNameModal


class ManageSingleMessageChannelsInteractionsHandler(AdminInteractionsHandler):

    def __init__(self, source_interaction, guild):
        super().__init__(source_interaction=source_interaction, guild=guild)
        self.chosen_channel_id = None
        self.role_id = None

    @interaction_handler
    async def handle_channel_select(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        channel_id = int(inter.data["values"][0])
        removed = channel_id in self.guild_prefs.single_message_channels

        await inter.response.defer()
        channel = self.guild.get_channel(channel_id)

        if removed:
            await self.guild_prefs_component.remove_guild_single_message_channel(guild=self.guild,
                                                                                 channel_id=channel_id)

            await self.refresh_setup_message(feedback_message=f"Channel {channel.mention} removed")

            await self.log_action_to_server(event=f"Changed single-message channels (removed channel)",
                                            field_value_map={"Channel": f"{channel.mention}"})
            return

        if not channel or not channel.type == discord.ChannelType.text:
            return await self.refresh_setup_message(feedback_message="I can't see that channel.")
        if not channel.permissions_for(self.guild.me).manage_messages:
            return await self.refresh_setup_message(feedback_message="I don't have the permission"
                                                                     "to delete messages there "
                                                                     "(**Manage Messages** permission missing).")

        embed, views = self.get_role_name_prompt_embed_and_views()
        self.chosen_channel_id = channel_id
        await self.source_interaction.edit_original_response(embed=embed, view=views)

    async def handle_role_name_prompt_proceed(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        modal = SingleMessageChannelsRoleNameModal(interactions_handler=self)
        await inter.response.send_modal(modal)

    async def handle_role_name_prompt_cancel(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        await inter.response.defer()
        await self.refresh_setup_message()

    async def handle_role_name_modal_submit(self, inter: discord.Interaction, role_name):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return
        await inter.response.defer()
        try:
            created_role = await create_role(self.guild, role_name, reason=f"for single-text mode in"
                                                                           f" <#{self.chosen_channel_id}>")
        except Exception:
            return await self.refresh_setup_message(feedback_message="There was an issue creating the role, "
                                                                     "please make sure I have the **Manage Roles** "
                                                                     "permission and that the role name is valid.")
        self.role_id = created_role.id
        embed, views = self.get_retroactive_assignment_embed_and_views()
        await self.source_interaction.edit_original_response(embed=embed, view=views)

    async def handle_retroactive_assignment_yes(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        await inter.response.send_message(f"Scanning messages in <#{self.chosen_channel_id}> and assigning role,"
                                          f"This will take a while, please wait...",
                                          ephemeral=True)

        channel_id = self.chosen_channel_id
        await self.guild_prefs_component.add_guild_single_message_channel(guild=self.guild,
                                                                          channel_id=channel_id,
                                                                          role_id=self.role_id,
                                                                          mode='delete')
        await self.refresh_setup_message(feedback_message="Channel added and roles are being assigned")
        asyncio.get_event_loop().create_task(scan_and_assign_role_for_single_message_channel(
            channel=self.guild.get_channel(channel_id),
            created_role=self.guild.get_role(self.role_id),
            interaction_to_edit_upon_completion=inter,
        ))
        await self.log_action_to_server(event=f"Changed single-message channels "
                                              f"(added channel with retroactive role assignment)",
                                        field_value_map={"Channel": f"<#{channel_id}>",
                                                         "Role": f"<@&{self.role_id}>"})

    async def handle_retroactive_assignment_no(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        await inter.response.defer()
        channel_id = self.chosen_channel_id
        await self.guild_prefs_component.add_guild_single_message_channel(guild=self.guild,
                                                                          channel_id=channel_id,
                                                                          role_id=self.role_id,
                                                                          mode='delete')
        await self.log_action_to_server(event=f"Changed single-message channels (added channel)",
                                        field_value_map={"Channel": f"<#{channel_id}>",
                                                         "Role": f"<@&{self.role_id}>"})

    @interaction_handler
    async def handle_clear_channels(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            await inter.response.defer()
            return

        await inter.response.defer()

        existing_single_message_channels = self.guild_prefs.single_message_channels.copy()

        await self.guild_prefs_component.clear_guild_single_message_channels(guild=self.guild)
        await self.refresh_setup_message(feedback_message="All single-message channels removed")

        await self.log_action_to_server(
            event=f"Cleared all single-message channels",
            field_value_map={"Channels": ", ".join([f"<#{channel}>" for channel in existing_single_message_channels])}
        )

    async def refresh_setup_message(self, feedback_message=None):
        self.chosen_channel_id = None
        embed, views = self.get_embed_and_views(feedback_message=feedback_message)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        await asyncio.sleep(0.5)
        await self.source_interaction.edit_original_response(embed=embed, view=views)

    def get_embed_and_views(self, feedback_message=None):
        embed = make_single_message_channels_management_embed(
            guild=self.guild,
            single_message_channels_data=self.guild_prefs.single_message_channels,
            feedback_message=feedback_message
        )
        views = get_channels_management_views(interactions_handler=self,
                                              add_clear_button=bool(self.guild_prefs.single_message_channels))

        return embed, views

    def get_role_name_prompt_embed_and_views(self):
        embed = quick_embed(
            title="Single-Message Channel - Role Name",
            text="In order to track people who have sent a message in this channel, we need to give them a role."
                 " What would you like to call this role?",
            emoji="",
            bold=False
        )
        views = quick_button_views(
            button_callback_map={
                "Set role name": self.handle_role_name_prompt_proceed,
                "Cancel": self.handle_role_name_prompt_cancel
            },
            styles=[ButtonStyle.green, ButtonStyle.red],
            on_timeout=self.on_timeout
        )
        return embed, views

    def get_retroactive_assignment_embed_and_views(self):
        embed = quick_embed(
            title="Single-Message Channel - Retroactive Assignment",
            text="Would you like to retroactively assign the role to"
                 " people who have already sent a message in this channel?\n"
                 "If yes: I will go over the last 300 messages in the channel.",
            emoji="",
            bold=False,
            fields_values={
                "Role": f"<@&{self.role_id}>",
                "Channel": f"<#{self.chosen_channel_id}>"
            }
        )
        views = quick_button_views(
            button_callback_map={
                "Yes please": self.handle_retroactive_assignment_yes,
                "No thanks": self.handle_retroactive_assignment_no
            },
            styles=[ButtonStyle.green, ButtonStyle.grey],
            on_timeout=self.on_timeout
        )
        return embed, views
