"""
Blueprint for utility user slash commands.
"""
import discord
from discord import app_commands
from discord.app_commands import allowed_installs, allowed_contexts
from discord.ext.commands import Cog

from bot.slashes.user_slashes.utility_user_slashes import UtilityUserSlashes
from constants import CommandGroup
from strings.commands_strings import UserSlashCommandsStrings


class UtilityUserBlueprint(Cog):
    STICKER = app_commands.command(name="sticker",
                                   description=UserSlashCommandsStrings.STICKER_DESCRIPTION,
                                   extras={"group": CommandGroup.UTILITY,
                                           "listing_priority": 6})
    AVATAR = app_commands.command(name="avatar",
                                  description=UserSlashCommandsStrings.AVATAR_DESCRIPTION,
                                  extras={"group": CommandGroup.UTILITY,
                                          "listing_priority": 4})
    BANNER = app_commands.command(name="banner",
                                  description=UserSlashCommandsStrings.BANNER_DESCRIPTION,
                                  extras={"group": CommandGroup.UTILITY,
                                          "listing_priority": 5})
    SERVER_INFO = app_commands.command(name="server-info",
                                       description=UserSlashCommandsStrings.SERVER_INFO_DESCRIPTION,
                                       extras={"group": CommandGroup.UTILITY,
                                               "listing_priority": 3,
                                               "aliases": ["serverinfo"]})
    SERVERINFO = app_commands.command(name="serverinfo",
                                      description=UserSlashCommandsStrings.SERVER_INFO_DESCRIPTION,
                                      extras={"is_alias": True,
                                              "alias_for": "server-info",
                                              "group": CommandGroup.UTILITY,
                                              "listing_priority": 3})
    USER_INFO = app_commands.command(name="user-info",
                                     description=UserSlashCommandsStrings.USER_INFO_DESCRIPTION,
                                     extras={"group": CommandGroup.UTILITY,
                                             "listing_priority": 2,
                                             "aliases": ["userinfo"]})
    USERINFO = app_commands.command(name="userinfo",
                                    description=UserSlashCommandsStrings.USER_INFO_DESCRIPTION,
                                    extras={"is_alias": True,
                                            "alias_for": "user-info",
                                            "group": CommandGroup.UTILITY,
                                            "listing_priority": 2})
    URBAN = app_commands.command(name="urban",
                                 description=UserSlashCommandsStrings.URBAN_DESCRIPTION,
                                 extras={"group": CommandGroup.UTILITY,
                                         "listing_priority": 8})
    DEFINE = app_commands.command(name="define",
                                  description=UserSlashCommandsStrings.DEFINE_DESCRIPTION,
                                  extras={"group": CommandGroup.UTILITY,
                                          "listing_priority": 7})
    FLIP = app_commands.command(name="flip",
                                description=UserSlashCommandsStrings.FLIP_DESCRIPTION,
                                extras={"group": CommandGroup.UTILITY,
                                        "listing_priority": 9})

    @STICKER
    @app_commands.rename(sticker_message_id="sticker-message-id")
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def sticker(self, interaction: discord.Interaction, sticker_message_id: str):
        """Get link to a sticker

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        sticker_message_id: str
            ID or link of the message that contains the sticker
        """

        await UtilityUserSlashes(interaction=interaction).sticker(sticker_message_id=sticker_message_id)

    @AVATAR
    @app_commands.rename(use_server_profile="use-server-profile")
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def avatar(self,
                     interaction: discord.Interaction,
                     user: discord.Member | discord.User = None,
                     use_server_profile: bool = False):
        """Get link to your or someone else's avatar

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        user: discord.Member | discord.User
            Get someone else's avatar (you can enter a user ID)
        use_server_profile: bool
            Get from the server profile instead of the global one
        """

        await UtilityUserSlashes(interaction=interaction).avatar(user=user, use_server_profile=use_server_profile)

    @BANNER
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def banner(self,
                     interaction: discord.Interaction,
                     user: discord.Member | discord.User = None,
                     use_server_profile: bool = False):
        """Get link to your or someone else's banner

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        user: discord.Member | discord.User
            Get someone else's banner (you can enter a user ID)
        use_server_profile: bool
            Get from the server profile instead of the global one
        """

        await UtilityUserSlashes(interaction=interaction).banner(user=user, use_server_profile=use_server_profile)

    @SERVER_INFO
    @app_commands.guild_only()
    @app_commands.rename(make_visible="make-visible")
    async def server_info(self, interaction: discord.Interaction, make_visible: bool = True):
        """Get information about the server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        make_visible: bool
            Make the embed visible to everyone
        """

        await UtilityUserSlashes(interaction=interaction).server_info(make_visible=make_visible)

    @SERVERINFO
    @app_commands.guild_only()
    @app_commands.rename(make_visible="make-visible")
    async def serverinfo(self, interaction: discord.Interaction, make_visible: bool = True):
        """Get information about the server

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        make_visible: bool
            Make the embed visible to everyone
        """

        await UtilityUserSlashes(interaction=interaction).server_info(make_visible=make_visible)

    @USER_INFO
    @app_commands.guild_only()
    @app_commands.rename(make_visible="make-visible")
    async def user_info(self,
                        interaction: discord.Interaction,
                        user: discord.Member | discord.User = None,
                        make_visible: bool = True):
        """Get information about your or a user

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        user: discord.Member | discord.User
            Get information about someone else (you can enter a user ID)
        make_visible: bool
            Make the embed visible to everyone
        """

        await UtilityUserSlashes(interaction=interaction).user_info(user=user, make_visible=make_visible)

    @USERINFO
    @app_commands.guild_only()
    @app_commands.rename(make_visible="make-visible")
    async def userinfo(self,
                       interaction: discord.Interaction,
                       user: discord.Member | discord.User = None,
                       make_visible: bool = True):
        """Get information about your or a user

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        user: discord.Member | discord.User
            Get information about someone else (you can enter a user ID)
        make_visible: bool
            Make the embed visible to everyone
        """

        await UtilityUserSlashes(interaction=interaction).user_info(user=user, make_visible=make_visible)

    @URBAN
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def urban(self, interaction: discord.Interaction, term: str):
        """Get a definition from Urban Dictionary

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        term: str
            Word or phrase to define
        """

        await UtilityUserSlashes(interaction=interaction).urban(term=term)

    @DEFINE
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def define(self, interaction: discord.Interaction, term: str):
        """Get a definition from Merriam-Webster Dictionary

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        term: str
            Word or phrase to define
        """

        await UtilityUserSlashes(interaction=interaction).define(term=term)

    @FLIP
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def flip(self, interaction: discord.Interaction):
        """Flip a coin

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await UtilityUserSlashes(interaction=interaction).flip()
