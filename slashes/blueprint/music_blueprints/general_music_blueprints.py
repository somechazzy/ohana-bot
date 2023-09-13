from discord import app_commands
from discord.ext.commands import Cog

from slashes.music_slashes.general_music_slashes import GeneralMusicSlashes


class GeneralMusicBlueprints(Cog):
    DJ = app_commands.command(name="dj",
                              description="Manage the DJ role(s)")
    CHANNEL_CREATE = app_commands.command(name="channel-create",
                                          description="Create Music channel")
    LOGS = app_commands.command(name="logs",
                                description="Get audit log of members actions related to music")

    @DJ
    @app_commands.guild_only()
    async def dj(self, inter):
        """Manage the DJ role(s)

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await GeneralMusicSlashes(interaction=inter).dj()

    @CHANNEL_CREATE
    @app_commands.guild_only()
    async def channel_create(self, inter):
        """Create Music channel

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await GeneralMusicSlashes(interaction=inter).channel_create()

    @LOGS
    @app_commands.guild_only()
    async def logs(self, inter):
        """Get audit log of members actions related to music

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await GeneralMusicSlashes(interaction=inter).logs()
