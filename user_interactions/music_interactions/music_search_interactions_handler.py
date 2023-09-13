import discord

from globals_.constants import MusicServiceMode, MusicLogAction
from utils.exceptions import MusicVoiceConnectionException
from user_interactions.base_interactions_handler import NumberedListInteractions
from utils.decorators import interaction_handler
from user_interactions.music_interactions.base_music_interactions_handler import MusicInteractionsHandler


class MusicSearchInteractionsHandler(MusicInteractionsHandler, NumberedListInteractions):

    def __init__(self, source_interaction: discord.Interaction, guild_id, index_track_info_map):
        super().__init__(source_interaction=source_interaction)
        self.guild_id = guild_id
        self.index_track_info_map = index_track_info_map

    @interaction_handler
    async def handle_selection(self, interaction: discord.Interaction):
        selected_index = int(interaction.data["values"][0])
        track_info = self.index_track_info_map[selected_index]
        try:
            voice_client = await self.check_playablity_and_connect(raise_=True)
            music_service = self.get_or_initiate_guild_music_service(voice_channel_id=voice_client.channel.id,
                                                                     voice_client=voice_client)

            if music_service.service_mode != MusicServiceMode.PLAYER:
                return await self.ask_to_switch_to_player_mode(interaction=interaction)

            track_info = await self.handle_play_track_from_view(track_url=track_info["url"], voice_client=voice_client)
        except MusicVoiceConnectionException as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return
        await interaction.response.send_message(f"Added {track_info['title']} to queue", ephemeral=True)

        await self.music_logger_component.log_music_action(action=MusicLogAction.ADDED_TRACK)
        del self

    @interaction_handler
    async def handle_cancel(self, interaction: discord.Interaction):
        # delete the message
        await interaction.message.delete()
        del self
