from typing import Union

import discord
from discord import app_commands
from discord.ext.commands import Cog

from slashes.user_slashes.utility_user_slashes import UtilityUserSlashes


class UtilityUserBlueprints(Cog):
    STICKER = app_commands.command(name="sticker",
                                   description="Get link to a sticker")
    AVATAR = app_commands.command(name="avatar",
                                  description="Get link to your or someone else's avatar")
    BANNER = app_commands.command(name="banner",
                                  description="Get link to your or someone else's banner")
    SERVER_INFO = app_commands.command(name="server-info",
                                       description="Get information about the server")
    USER_INFO = app_commands.command(name="user-info",
                                     description="Get information about your or a user")
    REMIND_ME = app_commands.command(name="remind-me",
                                     description="Set a reminder for yourself")
    URBAN = app_commands.command(name="urban",
                                 description="Get a definition from Urban Dictionary")
    DEFINE = app_commands.command(name="define",
                                  description="Get a definition from Merriam-Webster Dictionary")
    SNIPE = app_commands.command(name="snipe",
                                 description="Get the latest deleted message",
                                 extras={"unlisted": True})

    @STICKER
    @app_commands.rename(sticker_message_id="message-id-with-sticker")
    async def sticker(self, inter, sticker_message_id: str = None):
        """Get link to a sticker

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        sticker_message_id: str
            ID of the message that contains the sticker
        """

        await UtilityUserSlashes(interaction=inter).sticker(sticker_message_id=sticker_message_id)

    @AVATAR
    @app_commands.rename(use_server_profile="use-server-profile")
    async def avatar(self, inter, user: Union[discord.Member, discord.User] = None, use_server_profile: bool = False):
        """Get link to your or someone else's avatar

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        user: Union[discord.Member, discord.User]
            Get someone else's avatar (you can enter a user ID)
        use_server_profile: bool
            Use the server-specific avatar instead of the global avatar
        """

        await UtilityUserSlashes(interaction=inter).avatar(user=user, use_server_profile=use_server_profile)

    @BANNER
    async def banner(self, inter, user: Union[discord.Member, discord.User] = None):
        """Get link to your or someone else's banner

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        user: Union[discord.Member, discord.User]
            Get someone else's banner (you can enter a user ID)
        """

        await UtilityUserSlashes(interaction=inter).banner(user=user)

    @SERVER_INFO
    @app_commands.guild_only()
    @app_commands.rename(make_visible="make-visible")
    async def server_info(self, inter, make_visible: bool = False):
        """Get information about the server

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        make_visible: bool
            Make the embed visible to everyone
        """

        await UtilityUserSlashes(interaction=inter).server_info(make_visible=make_visible)

    @USER_INFO
    @app_commands.guild_only()
    @app_commands.rename(make_visible="make-visible")
    async def user_info(self, inter, user: Union[discord.Member, discord.User] = None, make_visible: bool = False):
        """Get information about your or a user

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        user: Union[discord.Member, discord.User]
            Get information about someone else (you can enter a user ID)
        make_visible: bool
            Make the embed visible to everyone
        """

        await UtilityUserSlashes(interaction=inter).user_info(user=user, make_visible=make_visible)

    @REMIND_ME
    async def remind_me(self, inter, when: str, what: str):
        """Set a reminder for yourself

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        when: str
            When to remind you (Ex: 12h, 1d6h, 1h30m, 1w3d)
        what: str
            What to remind you of
        """

        await UtilityUserSlashes(interaction=inter).remind_me(when=when, what=what)

    @URBAN
    async def urban(self, inter, term: str):
        """Get a definition from Urban Dictionary

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        term: str
            Word or phrase to define
        """

        await UtilityUserSlashes(interaction=inter).urban(term=term)

    @DEFINE
    async def define(self, inter, term: str):
        """Get a definition from Merriam-Webster Dictionary

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        term: str
            Word or phrase to define
        """

        await UtilityUserSlashes(interaction=inter).define(term=term)

    @SNIPE
    @app_commands.guild_only()
    async def snipe(self, inter):
        """Get the last deleted message

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await UtilityUserSlashes(interaction=inter).snipe()
