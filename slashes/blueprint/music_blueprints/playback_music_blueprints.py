from discord import app_commands
from discord.ext.commands import Cog

from slashes.music_slashes.playback_music_slashes import PlaybackMusicSlashes


class PlaybackMusicBlueprints(Cog):
    PLAY = app_commands.command(name="play",
                                description="Queue a track/playlist to be played")
    SEARCH = app_commands.command(name="search",
                                  description="Search for a track on YouTube to play")
    PLAY_NOW = app_commands.command(name="play-now",
                                    description="Play a track immediately")
    SEEK = app_commands.command(name="seek",
                                description="Seek to a position in the current track")
    REPLAY = app_commands.command(name="replay",
                                  description="Replay the current track")
    CLEAR = app_commands.command(name="clear",
                                 description="Clear the queue")
    MOVE = app_commands.command(name="move",
                                description="Move a track in the queue")
    REMOVE = app_commands.command(name="remove",
                                  description="Remove a track from the queue")
    SKIP_TO = app_commands.command(name="skip-to",
                                   description="Skip to a track in the queue")
    LYRICS = app_commands.command(name="lyrics",
                                  description="Get the lyrics of the current track")
    HISTORY = app_commands.command(name="history",
                                   description="History of tracks played on this server")

    @PLAY
    @app_commands.rename(user_input="track-or-playlist")
    @app_commands.guild_only()
    async def play(self, inter, user_input: str):
        """List and manage all of your playlists

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        user_input: str
            Track name or link, or playlist link
        """

        await PlaybackMusicSlashes(interaction=inter).play(user_input=user_input)

    @SEARCH
    @app_commands.rename(search_term="track-name")
    @app_commands.guild_only()
    async def search(self, inter, search_term: str):
        """Search for a track on YouTube to play

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        search_term: str
            Track name
        """

        await PlaybackMusicSlashes(interaction=inter).search(search_term=search_term)

    @PLAY_NOW
    @app_commands.rename(user_input="track")
    @app_commands.guild_only()
    async def play_now(self, inter, user_input: str):
        """Play a track immediately

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        user_input: str
            Track name or link
        """

        await PlaybackMusicSlashes(interaction=inter).play_now(user_input=user_input)

    @SEEK
    @app_commands.rename(position="position")
    @app_commands.guild_only()
    async def seek(self, inter, position: str):
        """Seek to a position in the current track

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        position: str
            Position to seek to (ex: 1:25)
        """

        await PlaybackMusicSlashes(interaction=inter).seek(position=position)

    @REPLAY
    @app_commands.guild_only()
    async def replay(self, inter):
        """Replay the current track

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await PlaybackMusicSlashes(interaction=inter).replay()

    @CLEAR
    @app_commands.guild_only()
    async def clear(self, inter):
        """Clear the queue

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await PlaybackMusicSlashes(interaction=inter).clear()

    @MOVE
    @app_commands.rename(from_position="from_position", to_position="to_position")
    @app_commands.guild_only()
    async def move(self, inter, from_position: int, to_position: int):
        """Move a track in the queue

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        from_position: int
            Position of the track to move
        to_position: int
            Position to move the track to
        """

        await PlaybackMusicSlashes(interaction=inter).move(from_position=from_position,
                                                           to_position=to_position)

    @REMOVE
    @app_commands.rename(position="position")
    @app_commands.guild_only()
    async def remove(self, inter, position: int):
        """Remove a track from the queue

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        position: int
            Position of the track to remove
        """

        await PlaybackMusicSlashes(interaction=inter).remove(position=position)

    @SKIP_TO
    @app_commands.rename(position="position")
    @app_commands.guild_only()
    async def skip_to(self, inter, position: int):
        """Skip to a track in the queue

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        position: int
            Position of the track to skip to
        """

        await PlaybackMusicSlashes(interaction=inter).skip_to(position=position)

    @LYRICS
    @app_commands.guild_only()
    async def lyrics(self, inter):
        """Get the lyrics of the currently playing track

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await PlaybackMusicSlashes(interaction=inter).lyrics()

    @HISTORY
    @app_commands.guild_only()
    async def history(self, inter):
        """Get the history of the currently playing track

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await PlaybackMusicSlashes(interaction=inter).history()
