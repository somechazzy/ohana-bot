import asyncio

import discord

from bot.interaction_handlers.admin_interaction_handlers import AdminInteractionHandler
from bot.utils.modal_factory.automod_management_modals import AddLimitedMessagesChannelRoleNameModal
from bot.utils.bot_actions.moderation_actions import scan_for_messages_and_assign_role
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.automod_management_embeds import get_limited_messages_channels_setup_embed
from bot.utils.embed_factory.general_embeds import get_info_embed
from bot.utils.guild_logger import GuildLogEventField, GuildLogger
from bot.utils.view_factory.automod_management_views import get_limited_messages_channels_setup_view
from common.exceptions import UserInputException
from components.guild_settings_components.guild_channel_settings_component import GuildChannelSettingsComponent
from constants import GuildLogEvent
from utils.helpers.context_helpers import create_task


class ManageLimitedMessagesChannelsInteractionHandler(AdminInteractionHandler):
    VIEW_NAME = "Limited-messages channels management"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interactions_restricted = True
        self.guild_channel_settings_component = GuildChannelSettingsComponent()

    @interaction_handler()
    async def on_channel_select(self, interaction: discord.Interaction):
        selected_channel_id = int(interaction.data["values"][0])
        channel = self.guild.get_channel(selected_channel_id)
        removed = self.guild_settings.channel_id_message_limiting_role_id.get(selected_channel_id)

        if not removed:
            if not channel:
                raise UserInputException("I can't see that channel.")
            elif channel.type != discord.ChannelType.text:
                raise UserInputException("Please choose a text channel.")
            elif not channel.permissions_for(self.guild.me).manage_messages:
                raise UserInputException("I can't delete messages in that channel.")
            elif not self.guild.me.guild_permissions.manage_roles:
                raise UserInputException("I need the 'Manage Roles' permission to do that.")
            await interaction.response.send_modal(AddLimitedMessagesChannelRoleNameModal(
                interactions_handler=self, channel_id=selected_channel_id
            ))
            return

        await interaction.response.defer()
        await self.guild_channel_settings_component.set_guild_channel_settings(
            guild_id=self.guild.id,
            guild_settings_id=self.guild_settings.guild_settings_id,
            channel_id=selected_channel_id,
            message_limiting_role_id=None
        )

        await self.refresh_message(feedback=f"Channel <#{selected_channel_id}> removed.")
        await self.log_setting_change(event_text=f"Removed limited-messages channel",
                                      fields=[GuildLogEventField(name="Channel", value=f"<#{selected_channel_id}>")])

    @interaction_handler()
    async def on_limited_messages_channel_role_name_modal_submit(self,
                                                                 interaction: discord.Interaction,
                                                                 channel_id: int,
                                                                 role_name: str):
        channel = self.guild.get_channel(channel_id)
        await interaction.response.send_message(embed=get_info_embed(f"Creating role `{role_name}` ..."),
                                                ephemeral=True)
        role = await self.guild.create_role(name=role_name, reason=f"for single-text mode in {channel.mention}")
        await self.guild_channel_settings_component.set_guild_channel_settings(
            guild_id=self.guild.id,
            guild_settings_id=self.guild_settings.guild_settings_id,
            channel_id=channel_id,
            message_limiting_role_id=role.id
        )
        await GuildLogger(guild=self.guild).log_event(event=GuildLogEvent.CREATED_ROLE,
                                                      roles=[role],
                                                      actor=interaction.user,
                                                      reason="Automatically created for limited-messages channel",)
        await interaction.edit_original_response(embed=get_info_embed(f"Role `{role_name}` created: {role.mention}\n"
                                                                      f"Scanning {channel.mention} for messages"
                                                                      f" (this will take some time)..."))
        create_task(scan_for_messages_and_assign_role(
            channel=channel,
            role=role,
            update_callback=interaction.edit_original_response
        ))
        await self.refresh_message(feedback=f"Channel <#{channel_id}> added.")
        await self.log_setting_change(event_text=f"Added limited-messages channel",
                                      fields=[GuildLogEventField(name="Channel", value=f"<#{channel_id}>")])

    async def refresh_message(self, no_view: bool = False, feedback: str | None = None, *args, **kwargs):
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        if not no_view and view is not None:
            await asyncio.sleep(0.5)
            await self.source_interaction.edit_original_response(embed=embed, view=view)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        embed = get_limited_messages_channels_setup_embed(
            selected_channel_ids=[channel_id for channel_id, limit
                                  in self.guild_settings.channel_id_message_limiting_role_id.items()],
            guild=self.guild,
            feedback_message=feedback
        )
        view = get_limited_messages_channels_setup_view(interaction_handler=self)
        return embed, view

    async def fetch_and_cleanup_limited_messages_channels(self):
        invalid_channel_ids = []
        for channel_id, role_id in self.guild_settings.channel_id_message_limiting_role_id.items():
            channel = self.guild.get_channel(channel_id)
            role = self.guild.get_role(role_id)
            if not channel or not role:
                invalid_channel_ids.append(channel_id)
        for channel_id in invalid_channel_ids:
            await self.guild_channel_settings_component.set_guild_channel_settings(
                guild_id=self.guild.id,
                guild_settings_id=self.guild_settings.guild_settings_id,
                channel_id=channel_id,
                message_limiting_role_id=None
            )
