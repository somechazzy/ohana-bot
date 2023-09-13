from math import ceil

import discord

from globals_.constants import MusicServiceMode, MusicLogAction
from utils.embed_factory import make_music_history_embed
from utils.helpers import get_history_embed_views
from utils.exceptions import MusicVoiceConnectionException
from utils.decorators import interaction_handler
from user_interactions.music_interactions.base_music_interactions_handler import MusicInteractionsHandler


class MusicHistoryInteractionsHandler(MusicInteractionsHandler):

    def __init__(self, source_interaction, history_list, page):
        super().__init__(source_interaction=source_interaction)
        self.history_list = history_list
        self.page = page
        self.page_count = ceil(len(self.history_list) / 10)

    @interaction_handler
    async def handle_history_previous_page(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        if self.page == 1:
            self.page = self.page_count
        else:
            self.page -= 1

        await inter.response.defer()
        await self.refresh_history_embed()

    @interaction_handler
    async def handle_history_next_page(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        if self.page == self.page_count:
            self.page = 1
        else:
            self.page += 1

        await inter.response.defer()
        await self.refresh_history_embed()

    @interaction_handler
    async def handle_history_track_select(self, inter: discord.Interaction):
        if not self.source_interaction_user.id == inter.user.id:
            return await inter.response.defer()
        track_index = int(inter.data["values"][0])
        track = self.history_list[track_index]

        if not await self.validate_music_channel(interaction=inter):
            return

        try:
            voice_client = await self.check_playablity_and_connect(raise_=True)
        except MusicVoiceConnectionException as e:
            return await inter.response.send_message(content=str(e), ephemeral=True)

        music_service = self.get_or_initiate_guild_music_service(voice_channel_id=voice_client.channel.id,
                                                                 voice_client=voice_client)

        if music_service.service_mode != MusicServiceMode.PLAYER:
            return await self.ask_to_switch_to_player_mode(interaction=inter)

        await inter.response.send_message(f"Adding track to queue: `{track['title']}`", ephemeral=True)
        await self.handle_play_track_from_view(track_url=track['url'], voice_client=voice_client)
        await self.refresh_history_embed()
        await self.music_logger_component.log_music_action(action=MusicLogAction.ADDED_TRACK)

    async def refresh_history_embed(self):
        first_index = (self.page - 1) * 10
        last_index = first_index + 10
        track_index_title_map = {index: track['title'] for index, track
                                 in enumerate(self.history_list[first_index:last_index], first_index)}
        view = get_history_embed_views(interactions_handler=self, show_previous=self.page > 1,
                                       show_next=self.page_count > self.page,
                                       track_index_title_map=track_index_title_map)
        embed = make_music_history_embed(guild=self.guild, history=self.history_list, page=self.page)
        await self.source_interaction.edit_original_response(embed=embed, view=view)
