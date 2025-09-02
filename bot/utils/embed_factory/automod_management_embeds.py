import discord

from clients import emojis
from constants import Colour
from models.dto.cachables import CachedGuildSettings


def get_autoroles_setup_embed(selected_role_ids: list[int],
                              guild: discord.Guild,
                              feedback_message: str | None = None) -> discord.Embed:
    """
    Generate an embed for the autoroles setup.
    Args:
        selected_role_ids (list[int]): List of role IDs that are set as autoroles.
        guild (discord.Guild): The guild related.
        feedback_message (str | None): Optional feedback message to include in the embed.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(
        title="Autoroles Setup",
        description="Select roles to be automatically assigned to new members.",
        color=Colour.PRIMARY_ACCENT
    )

    roles = [guild.get_role(role_id) for role_id in selected_role_ids]
    role_mentions = "\n".join(role.mention for role in roles if role)
    embed.add_field(name="Selected autoroles", value=role_mentions or "None", inline=False)

    embed.set_footer(text="Use \"/manage settings\" to see an overview of your server settings.",
                     icon_url=guild.icon.with_size(128).url if guild.icon else None)

    if feedback_message:
        embed.add_field(name="Info", value=feedback_message, inline=False)

    return embed


def get_auto_responses_setup_embed(auto_responses: list[CachedGuildSettings.Autoresponse],
                                   guild: discord.Guild,
                                   page: int,
                                   page_count: int,
                                   page_size: int,
                                   feedback_message: str | None = None) -> discord.Embed:
    """
    Generate an embed for the auto-responses setup.
    Args:
        auto_responses (list[CachedGuildSettings.Autoresponse]): List of auto-responses.
        guild (discord.Guild): The guild related.
        page (int): Current page number.
        page_count (int): Total number of pages.
        page_size (int): Number of items per page.
        feedback_message (str | None): Optional feedback message to include in the embed.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(
        title="Auto-responses Setup",
        description="Auto-responses are triggered by specific keywords or phrases in messages.",
        color=Colour.PRIMARY_ACCENT
    )

    for idx, auto_response in enumerate(auto_responses[(page - 1) * page_size: page * page_size], 1):
        embed.add_field(
            name=emojis.numbers[idx],
            value=f"**Trigger**: \"{auto_response.trigger}\"\n"
                  f"**Response**: \"{auto_response.response}\"\n"
                  f"**Match Type**: {auto_response.match_type.replace('_', ' ').title()}\n"
                  f"**Delete Original**: {'Yes' if auto_response.delete_original else 'No'}",
            inline=False
        )
    if not auto_responses:
        embed.add_field(name="No auto-responses", value="You have no auto-responses set up.", inline=False)

    if feedback_message:
        embed.add_field(name="Feedback", value=feedback_message, inline=False)

    embed.set_footer(text=f"Showing page {page}/{page_count}. Total of {len(auto_responses)} auto-responses.",
                     icon_url=guild.icon.with_size(128).url if guild.icon else None)

    return embed


def get_gallery_channels_setup_embed(selected_channel_ids: list[int],
                                     guild: discord.Guild,
                                     feedback_message: str | None = None) -> discord.Embed:
    """
    Generate an embed for the gallery channels setup.
    Args:
        selected_channel_ids (list[int]): List of channel IDs that are set as gallery channels.
        guild (discord.Guild): The guild related.
        feedback_message (str | None): Optional feedback message to include in the embed.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(
        title="Gallery channels Setup",
        description="Select channels to be used as gallery channels, where non-media messages are deleted.",
        color=Colour.PRIMARY_ACCENT
    )

    if feedback_message:
        embed.add_field(name="Feedback", value=feedback_message, inline=False)

    channels = [guild.get_channel(channel_id) for channel_id in selected_channel_ids]
    channel_mentions = "\n".join(channel.mention for channel in channels if channel)
    embed.add_field(name="Selected gallery channels", value=channel_mentions or "None", inline=False)

    embed.set_footer(text="Use \"/manage settings\" to see an overview of your server settings.",
                     icon_url=guild.icon.with_size(128).url if guild.icon else None)

    return embed


def get_limited_messages_channels_setup_embed(selected_channel_ids: list[int],
                                              guild: discord.Guild,
                                              feedback_message: str | None = None) -> discord.Embed:
    """
    Generate an embed for the limited-messages channels setup.
    Args:
        selected_channel_ids (list[int]): List of channel IDs that are set as limited-messages channels.
        guild (discord.Guild): The guild related.
        feedback_message (str | None): Optional feedback message to include in the embed.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(
        title="Limited-Messages Channels Setup",
        description="Choose channels where members can send **only one message**. "
                    "Useful for things like introduction channels.\n‎\n"
                    "Upon selecting a channel, you will be asked to enter a role name which will be assigned to users "
                    "who send a message in that channel. From here, you can either:\n"
                    "1. Manually change that role's Send Messages permission in the channel to *deny*, or\n"
                    "2. Leave it to me to delete any any new messages from members with that role.\n‎\n"
                    "I will scan the most recent **~300 messages** in the channel "
                    "initially and assign this role retroactively.",
        color=Colour.PRIMARY_ACCENT
    )

    if feedback_message:
        embed.add_field(name="Feedback", value=feedback_message, inline=False)

    channels = [guild.get_channel(channel_id) for channel_id in selected_channel_ids]
    channel_mentions = "\n".join(channel.mention for channel in channels if channel)
    embed.add_field(name="Selected Limited-messages channels", value=channel_mentions or "None", inline=False)

    embed.set_footer(text="Use \"/manage settings\" to see an overview of your server settings.",
                     icon_url=guild.icon.with_size(128).url if guild.icon else None)

    return embed
