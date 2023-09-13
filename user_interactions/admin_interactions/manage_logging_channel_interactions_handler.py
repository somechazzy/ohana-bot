import asyncio

import discord

from utils.embed_factory import quick_embed
from utils.helpers import get_logging_channel_setup_views
from utils.decorators import interaction_handler
from user_interactions.admin_interactions.base_admin_interactions_handler import AdminInteractionsHandler


class ManageLoggingChannelInteractionsHandler(AdminInteractionsHandler):

    def __init__(self, source_interaction, guild):
        super().__init__(source_interaction=source_interaction, guild=guild)

    @interaction_handler
    async def handle_channel_select(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.defer()
        selected_channel_id = int(inter.data["values"][0])

        if selected_channel_id == self.guild_prefs.logs_channel:
            return await self.refresh_setup_message(feedback_message="This channel is already "
                                                                     "set as the logging channel.")

        channel = self.guild.get_channel(selected_channel_id)
        if not channel:
            return await self.refresh_setup_message(feedback_message="I can't see that channel.")

        if channel.type != discord.ChannelType.text:
            return await self.refresh_setup_message(feedback_message="Please choose a text channel.")

        if not channel.permissions_for(self.guild.me).send_messages:
            return await self.refresh_setup_message(feedback_message="I can't send messages in that channel.")

        if not channel.permissions_for(self.guild.me).embed_links:
            return await self.refresh_setup_message(feedback_message="I need the **Embed Links** "
                                                                     "permission in that channel.")

        await self.guild_prefs_component.set_guild_logs_channel(guild=self.guild, channel_id=selected_channel_id)

        await self.refresh_setup_message(feedback_message="Set new logging channel.")

        await self.log_action_to_server(event="Set logs channel for logging bot related events.",
                                        field_value_map={"Channel": f"{channel.mention}"})

    @interaction_handler
    async def handle_create_new_channel(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.defer()
        if not self.guild.me.guild_permissions.manage_channels:
            return await self.refresh_setup_message(feedback_message="I need the **Manage Channels** "
                                                                     "permission to do that.")

        logging_channel = await self.guild.create_text_channel(
            name="📃-logs",
            topic="Logs",
            reason="Logging channel",
            position=0,
            overwrites={
                self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                self.guild.me: discord.PermissionOverwrite(read_messages=True,
                                                           send_messages=True,
                                                           embed_links=True),
                self.guild.get_member(self.source_interaction.user.id): discord.PermissionOverwrite(read_messages=True)
            }
        )

        await self.guild_prefs_component.set_guild_logs_channel(guild=self.guild, channel_id=logging_channel.id)
        await self.refresh_setup_message(feedback_message=f"Created new logging channel {logging_channel.mention}.")

        await self.log_action_to_server(event="Created & set logs channel for logging bot related events.",
                                        field_value_map={"Channel": f"{logging_channel.mention}"})

    @interaction_handler
    async def handle_unset_channel(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.defer()
        await self.refresh_setup_message(feedback_message="Unset logging channel.")
        await self.log_action_to_server(event="Unset logs channel (this will be my last log).")
        await self.guild_prefs_component.set_guild_logs_channel(guild=self.guild, channel_id=0)

    async def refresh_setup_message(self, feedback_message=None):
        embed, views = self.get_embed_and_views(feedback_message=feedback_message)
        await self.source_interaction.edit_original_response(embed=embed, view=None)
        await asyncio.sleep(0.5)
        await self.source_interaction.edit_original_response(embed=embed, view=views)

    def get_embed_and_views(self, feedback_message=None):
        logging_channel = self.guild.get_channel(self.guild_prefs.logs_channel)
        fields_values = {"Current logging channel": logging_channel.mention if logging_channel else "None"}
        if feedback_message:
            fields_values["Note"] = feedback_message
        embed = quick_embed(title="Logging Channel Setup",
                            text="I will log bot-related logs (like admin actions etc..) to this channel.",
                            emoji='',
                            bold=False,
                            fields_values=fields_values,
                            fields_values_inline=False)
        views = get_logging_channel_setup_views(interactions_handler=self)

        return embed, views
