from discord import Interaction, app_commands
from discord.ext.commands import Cog

from slashes.admin_slashes.gerenal_admin_slashes import GeneralAdminSlashes


class GeneralAdminBlueprints(Cog):
    LOGGING_CHANNEL = app_commands.command(name="logging-channel",
                                           description="Set/unset the logging channel for this server")

    ROLE_PERSISTENCE = app_commands.command(name="role-persistence",
                                            description="Enable/disable role persistence for this server")

    AUTOROLES = app_commands.command(name="autoroles",
                                     description="Manage autoroles for this server")

    GALLERY_CHANNELS = app_commands.command(name="gallery-channels",
                                            description="Manage gallery channels for this server")

    SINGLE_MESSAGE_CHANNELS = app_commands.command(name="single-message-channels",
                                                   description="Manage single-message channels for this server")

    SETTINGS_OVERVIEW = app_commands.command(name="settings-overview",
                                             description="View a summary of all settings for this server")

    @LOGGING_CHANNEL
    @app_commands.guild_only()
    async def logging_channel(self, inter: Interaction):
        """Set/unset the logging channel for this server

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await GeneralAdminSlashes(interaction=inter).logging_channel()

    @ROLE_PERSISTENCE
    @app_commands.guild_only()
    async def role_persistence(self, inter: Interaction, enable: bool):
        """Enable/disable role persistence for this server

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        enable: bool
            Whether to enable role persistence
        """

        await GeneralAdminSlashes(interaction=inter).role_persistence(enable=enable)

    @AUTOROLES
    @app_commands.guild_only()
    async def autoroles(self, inter: Interaction):
        """Manage autoroles for this server

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await GeneralAdminSlashes(interaction=inter).autoroles()

    @GALLERY_CHANNELS
    @app_commands.guild_only()
    async def gallery_channels(self, inter: Interaction):
        """Manage gallery channels for this server

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await GeneralAdminSlashes(interaction=inter).gallery_channels()

    @SINGLE_MESSAGE_CHANNELS
    @app_commands.guild_only()
    async def single_message_channels(self, inter: Interaction):
        """Manage single-message channels for this server

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await GeneralAdminSlashes(interaction=inter).single_message_channels()

    @SETTINGS_OVERVIEW
    @app_commands.guild_only()
    @app_commands.rename(make_visible="make-visible")
    async def settings_overview(self, inter: Interaction, make_visible: bool = False):
        """View a summary of all settings for this server

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        make_visible: bool
            Whether to make the message visible to everyone
        """

        await GeneralAdminSlashes(interaction=inter).settings_overview(make_visible=make_visible)
