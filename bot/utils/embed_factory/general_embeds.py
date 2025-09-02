import discord

from clients import emojis
from constants import Colour


def get_generic_embed(description: str,
                      title: str | None = None,
                      color: int = Colour.PRIMARY_ACCENT,
                      field_value_map: dict | None = None) -> discord.Embed:
    """
    Create a generic embed with a title and description and a specified color.

    Args:
        description (str): The description/message of the embed.
        title (str | None): The title of the embed.
        color (int): The color of the embed. Defaults to the primary accent.
        field_value_map (dict | None): A dictionary of field names/values to add to the embed.

    Returns:
        discord.Embed: The created embed.
    """
    embed = discord.Embed(title=title, description=description, color=color)
    if field_value_map:
        for field_name, field_value in field_value_map.items():
            embed.add_field(name=field_name, value=field_value, inline=True)
    return embed


def get_error_embed(message: str, title: str | None = None) -> discord.Embed:
    """
    Create a user-facing error embed with a title and message.
    Args:
        message (str): The error message to display in the embed.
        title (str | None): The title of the embed.

    Returns:
        discord.Embed: The created embed.
    """
    if not message.startswith("❌"):
        message = f"❌ {message}"
    return get_generic_embed(title=title, description=message, color=Colour.ERROR)


def get_info_embed(message: str, title: str | None = None) -> discord.Embed:
    """
    Create a user-facing info embed with a title and message.
    Args:
        message (str): The info message to display in the embed.
        title (str | None): The title of the embed.

    Returns:
        discord.Embed: The created embed.
    """
    if not message.startswith(str(emojis.general.info)):
        message = f"{emojis.general.info} ‎ {message}"
    return get_generic_embed(title=title, description=message, color=Colour.INFO)


def get_success_embed(message: str, title: str | None = None) -> discord.Embed:
    """
    Create a user-facing success embed with a title and message.
    Args:
        message (str): The success message to display in the embed.
        title (str | None): The title of the embed.

    Returns:
        discord.Embed: The created embed.
    """
    if not message.startswith("✅"):
        message = f"✅ {message}"
    return get_generic_embed(title=title, description=message, color=Colour.SUCCESS)
