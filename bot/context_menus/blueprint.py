"""
Blueprint to define context menu app commands.
Any new commands must be added to `__init__.py`'s register_commands function.
"""
import discord
from discord import app_commands
from discord.app_commands import allowed_installs, allowed_contexts

from bot.context_menus.user_context_menus import UserContextMenus
from strings.commands_strings import ContextCommandsStrings

REMIND_ME = app_commands.context_menu(name=ContextCommandsStrings.REMIND_ME)
AVATAR = app_commands.context_menu(name=ContextCommandsStrings.AVATAR)
BANNER = app_commands.context_menu(name=ContextCommandsStrings.BANNER)
LEVEL = app_commands.context_menu(name=ContextCommandsStrings.LEVEL)
EMOJI = app_commands.context_menu(name=ContextCommandsStrings.EMOJI)
STICKER = app_commands.context_menu(name=ContextCommandsStrings.STICKER)


@REMIND_ME
@allowed_installs(users=True, guilds=True)
@allowed_contexts(guilds=True, dms=True, private_channels=True)
async def remind_me(interaction:  discord.Interaction, message: discord.Message):
    """Remind me of this message at a specific time

    Parameters
    -----------
    interaction: discord.Interaction
        Interaction to handle
    message: discord.Message
        Message to remind you of
    """

    await UserContextMenus(interaction=interaction, target=message).remind_me()


@AVATAR
@allowed_installs(users=True, guilds=True)
@allowed_contexts(guilds=True, dms=True, private_channels=True)
async def get_avatar(interaction: discord.Interaction, user: discord.User | discord.Member):
    """Get user's avatar

    Parameters
    -----------
    interaction: discord.Interaction
        Interaction
    user: discord.Member | discord.User
        User to get avatar of
    """

    await UserContextMenus(interaction=interaction, target=user).get_avatar()


@BANNER
@allowed_installs(users=True, guilds=True)
@allowed_contexts(guilds=True, dms=True, private_channels=True)
async def get_banner(interaction: discord.Interaction, user: discord.User | discord.Member):
    """Get user's banner

    Parameters
    -----------
    interaction: discord.Interaction
        Interaction
    user: discord.Member | discord.User
        User to get banner of
    """

    await UserContextMenus(interaction=interaction, target=user).get_banner()


@LEVEL
@allowed_installs(users=False, guilds=True)
@allowed_contexts(guilds=True, dms=False, private_channels=False)
async def get_level(interaction: discord.Interaction, user: discord.Member):
    """Get user's level/rank

    Parameters
    -----------
    interaction: discord.Interaction
        Interaction
    user: discord.Member
        User to get level of
    """

    await UserContextMenus(interaction=interaction, target=user).get_level()


@EMOJI
@allowed_installs(users=True, guilds=True)
@allowed_contexts(guilds=True, dms=True, private_channels=True)
async def get_emoji(interaction: discord.Interaction, message: discord.Message):
    """Get message's emoji

    Parameters
    -----------
    interaction: discord.Interaction
        Interaction
    message: discord.Message
        Message to get emoji of
    """

    await UserContextMenus(interaction=interaction, target=message).get_emoji()


@STICKER
@allowed_installs(users=True, guilds=True)
@allowed_contexts(guilds=True, dms=True, private_channels=True)
async def get_sticker(interaction: discord.Interaction, message: discord.Message):
    """Get message's sticker

    Parameters
    -----------
    interaction: discord.Interaction
        Interaction
    message: discord.Message
        Message to get sticker of
    """

    await UserContextMenus(interaction=interaction, target=message).get_sticker()
