from typing import TYPE_CHECKING

import discord
from discord.ui import View, ChannelSelect, Button
from discord import ButtonStyle

from clients import emojis

if TYPE_CHECKING:
    from bot.interaction_handlers.admin_interaction_handlers.manage_logging_channel_interaction_handler import \
        ManageLoggingChannelInteractionHandler


def get_logging_channel_setup_view(interaction_handler: 'ManageLoggingChannelInteractionHandler',
                                   current_logging_channel: discord.TextChannel) -> View:
    """
    Creates a view for setting up or unsetting a logging channel.
    Args:
        interaction_handler (ManageLoggingChannelInteractionHandler): The interaction handler to use for the view.
        current_logging_channel (discord.TextChannel): The currently set logging channel, if any.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    channel_select = ChannelSelect(max_values=1,
                                   placeholder="Select a channel to set as the logging channel",
                                   channel_types=[discord.ChannelType.text],
                                   default_values=[current_logging_channel] if current_logging_channel else None)
    channel_select.callback = interaction_handler.on_channel_select
    view.add_item(channel_select)

    if current_logging_channel:
        clear_button = Button(label="Unset logging channel", style=ButtonStyle.red, emoji=emojis.action.delete)
        clear_button.callback = interaction_handler.unset_channel
        view.add_item(clear_button)
    else:
        create_button = Button(label="Create new logging channel", style=ButtonStyle.green, emoji=emojis.action.add)
        create_button.callback = interaction_handler.create_new_channel
        view.add_item(create_button)

    view.on_timeout = interaction_handler.on_timeout
    return view
