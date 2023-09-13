import discord

from utils.decorators import interaction_handler
from user_interactions.modals.base_modal import BaseModal


class MusicLibraryCreatePlaylistModal(BaseModal, title="Create Playlist"):
    playlist_name_input = discord.ui.TextInput(
        label="Give your playlist a name (must be unique)",
        max_length=300,
        min_length=1,
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(playlist_view=False)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_create_playlist_modal_submit(
            inter=interaction,
            playlist_name=self.playlist_name_input.value
        )


class MusicLibraryPlaylistAddTrackModal(BaseModal, title="Add to Playlist"):
    track_input = discord.ui.TextInput(
        label="Enter a playlist/track name or URL",
        max_length=300,
        min_length=1,
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(playlist_view=True)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_playlist_add_track_modal_submit(
            inter=interaction,
            track_input=self.track_input.value
        )


class MusicLibraryPlaylistRemoveTrackModal(BaseModal, title="Remove from Playlist"):
    track_input = discord.ui.TextInput(
        label="Enter a track number",
        max_length=300,
        min_length=1,
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(playlist_view=True)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_playlist_remove_track_modal_submit(
            inter=interaction,
            track_input=self.track_input.value
        )


class MusicLibraryPlaylistRenameModal(BaseModal, title="Rename Playlist"):
    playlist_name_input = discord.ui.TextInput(
        label="Enter a new name for your playlist",
        max_length=300,
        min_length=1,
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(playlist_view=True)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_playlist_rename_modal_submit(
            inter=interaction,
            playlist_name=self.playlist_name_input.value
        )


class MusicLibraryPlaylistCloneModal(BaseModal, title="Clone Playlist"):
    playlist_name_input = discord.ui.TextInput(
        label="Enter a name for the cloned playlist",
        max_length=300,
        min_length=1,
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(playlist_view=True)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_playlist_clone_modal_submit(
            inter=interaction,
            playlist_name=self.playlist_name_input.value
        )


class MusicLibraryPlaylistMoveTrackModal(BaseModal, title="Move Track"):
    target_track_index_input = discord.ui.TextInput(
        label="Track number you want to move",
        max_length=10,
        min_length=1,
        required=True,
        style=discord.TextStyle.short
    )
    destination_track_index_input = discord.ui.TextInput(
        label="To which position do you want to move it?",
        max_length=10,
        min_length=1,
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await super().on_error(interaction, error)
        await self.interactions_handler.refresh_embeds(playlist_view=True)

    @interaction_handler
    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.handle_playlist_move_track_modal_submit(
            inter=interaction,
            target_track_index=self.target_track_index_input.value,
            destination_track_index=self.destination_track_index_input.value
        )
