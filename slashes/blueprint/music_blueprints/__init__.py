from globals_.clients import discord_client
from .playlist_music_blueprints import PlaylistMusicBlueprints
from .library_music_blueprints import LibraryMusicBlueprints
from .playback_music_blueprints import PlaybackMusicBlueprints
from .general_music_blueprints import GeneralMusicBlueprints


class MusicSlashesGroupCog(PlaylistMusicBlueprints, LibraryMusicBlueprints,
                           PlaybackMusicBlueprints, GeneralMusicBlueprints,
                           name='music'):
    pass


cog = MusicSlashesGroupCog()


async def add_cogs():
    await discord_client.add_cog(cog)
