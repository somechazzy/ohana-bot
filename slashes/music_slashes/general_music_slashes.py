import traceback

from components.music_components.base_music_component import MusicComponent
from user_interactions.music_interactions.music_logs_interactions_handler import MusicLogsInteractionsHandler
from utils.embed_factory import quick_embed, make_dj_role_management_embed
from globals_.constants import Colour
from utils.helpers import get_roles_management_views
from utils.decorators import slash_command
from slashes.music_slashes.base_music_slashes import MusicSlashes
from user_interactions.music_interactions.music_dj_interactions_handler import MusicDJInteractionsHandler


class GeneralMusicSlashes(MusicSlashes):

    @slash_command
    async def dj(self):
        """
        /music dj
        Manage the DJ role(s)
        """
        if not await self.preprocess_and_validate():
            return

        handler = MusicDJInteractionsHandler(source_interaction=self.interaction, guild=self.guild)
        embed = make_dj_role_management_embed(guild=self.guild, dj_role_ids=self.guild_prefs.dj_roles)
        views = get_roles_management_views(interactions_handler=handler,
                                           add_clear_button=bool(self.guild_prefs.dj_roles))
        await self.interaction.response.send_message(embed=embed, view=views, ephemeral=True)

    @slash_command
    async def channel_create(self):
        """
        /music channel-create
        Create Music channel
        """
        if not await self.preprocess_and_validate(guild_only=True):
            return

        if self.guild_prefs.music_channel and self.guild.get_channel(self.guild_prefs.music_channel):
            return await self.interaction.response.send_message(
                embed=quick_embed(f"Player channel <#{self.guild_prefs.music_channel}> "
                                  f"already exists.", self.channel, emoji='❌', color=Colour.RED),
                ephemeral=True
            )
        await self.interaction.response.send_message(
            embed=quick_embed(f"Creating player channel...", self.channel),
            ephemeral=True
        )
        try:
            music_channel = await MusicComponent().setup_player_channel(guild=self.guild)
        except Exception as e:
            await self.interaction.edit_original_response(
                embed=quick_embed("Failed at creating player channel. "
                                  "Please make sure I have the necessary permissions.",
                                  self.channel, emoji='❌', color=Colour.RED)
            )
            self.error_logger.log(f"Failed at creating player channel in guild `{self.guild} ({self.guild.id})`.\n"
                                  f"Error: {e}\nTraceback: {traceback.format_exc()}")
            return
        if self.music_service:
            self.music_service.music_channel = self.music_service.text_channel = music_channel
            self.music_service.player_message_id = self.guild_prefs.music_player_message
        await self.interaction.edit_original_response(
            embed=quick_embed(f"Player channel {music_channel.mention} created!\n"
                              f"Feel free to move the channel and to rename it.",
                              self.channel, emoji='', color=Colour.GREEN)
        )

    @slash_command
    async def logs(self):
        """
        /music logs
        Get audit log of members actions related to music
        """
        if not await self.preprocess_and_validate(guild_only=True):
            return

        music_logs_list = await self.music_logger_component.get_guild_music_logs_readable_and_stylized(
            guild_id=self.guild.id
        )

        if not music_logs_list:
            return await self.interaction.response.send_message("No music logs for this server yet.",
                                                                ephemeral=True)
        music_logs_list.reverse()
        interactions_handler = MusicLogsInteractionsHandler(
            source_interaction=self.interaction,
            logs_list=music_logs_list
        )
        embed, views = interactions_handler.get_embed_and_views()
        await self.interaction.response.send_message(content=None, embed=embed, view=views, ephemeral=True)
