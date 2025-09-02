from typing import TYPE_CHECKING

import discord
from discord.ui import View, RoleSelect, Button, Select, ChannelSelect
from discord import ButtonStyle, SelectOption

from clients import emojis
from models.dto.cachables import CachedGuildSettings
from utils.helpers.text_manipulation_helpers import shorten_text

if TYPE_CHECKING:
    from bot.interaction_handlers.admin_interaction_handlers.manage_autoroles_interaction_handler import \
        ManageAutorolesInteractionHandler
    from bot.interaction_handlers.admin_interaction_handlers.manage_auto_responses_interaction_handler import \
        ManageAutoResponsesInteractionHandler
    from bot.interaction_handlers.admin_interaction_handlers.manage_gallery_channels_interaction_handler import \
        ManageGalleryChannelsInteractionHandler
    from bot.interaction_handlers.admin_interaction_handlers.\
        manage_limited_messages_channels_interaction_handler import ManageLimitedMessagesChannelsInteractionHandler


def get_autorole_setup_view(interaction_handler: "ManageAutorolesInteractionHandler",
                            add_clear_button: bool) -> View:
    """
    Creates a View for managing autoroles.
    Args:
        interaction_handler (ManageAutorolesInteractionHandler): The interaction handler to use for the view.
        add_clear_button (bool): Whether to add a button to clear all autoroles.

    Returns:
        View: The created View.
    """
    view = View(timeout=600)

    role_select_view = RoleSelect(max_values=1,
                                  placeholder="Select a role to add/remove as an autorole")
    role_select_view.callback = interaction_handler.on_role_select
    view.add_item(role_select_view)

    if add_clear_button:
        clear_button = Button(label="Clear all roles", style=ButtonStyle.red, emoji=emojis.action.clear)
        clear_button.callback = interaction_handler.clear_roles
        view.add_item(clear_button)

    view.on_timeout = interaction_handler.on_timeout
    return view


def get_auto_responses_setup_view(interaction_handler: "ManageAutoResponsesInteractionHandler",
                                  auto_responses: list[CachedGuildSettings.Autoresponse],
                                  page: int,
                                  page_count: int,
                                  page_size: int) -> View:
    """
    Creates a View for managing auto-responses.
    Args:
        interaction_handler (ManageAutoResponsesInteractionHandler): The interaction handler to use for the view.
        auto_responses (list[CachedGuildSettings.Autoresponse]): The list of auto-responses to display.
        page (int): The current page number.
        page_count (int): The total number of pages.
        page_size (int): The number of auto-responses per page.
    Returns:
        View: The created View.
    """
    view = View(timeout=600)

    if auto_responses:
        auto_response_select = Select(
            placeholder="Select an auto-response to edit or delete",
            min_values=1, max_values=1,
            custom_id="auto-response-select",
            row=0,
            options=[SelectOption(label=shorten_text(auto_response.trigger, 95),
                                  description=shorten_text(auto_response.response, 95),
                                  value=str(auto_response.guild_auto_response_id))
                     for auto_response in auto_responses[(page - 1) * page_size: page * page_size]]
        )
        auto_response_select.callback = interaction_handler.on_auto_response_select
        view.add_item(auto_response_select)

    add_button = Button(label="Add new auto-response", style=ButtonStyle.green, emoji=emojis.action.add, row=1)
    add_button.callback = interaction_handler.on_add_auto_response
    view.add_item(add_button)

    if auto_responses:
        clear_button = Button(label="Delete all auto-responses", style=ButtonStyle.red,
                              emoji=emojis.action.clear, row=1)
        clear_button.callback = interaction_handler.clear_auto_responses
        view.add_item(clear_button)

    if page and page_count:
        if page > 1:
            previous_button = Button(style=ButtonStyle.blurple, label="Previous",
                                     custom_id="navigation_previous", emoji=emojis.navigation.previous, row=2)
            previous_button.callback = interaction_handler.previous_page
            view.add_item(previous_button)
        if page < page_count:
            next_button = Button(style=ButtonStyle.blurple, label="Next",
                                 custom_id="navigation_next", emoji=emojis.navigation.next, row=2)
            next_button.callback = interaction_handler.next_page
            view.add_item(next_button)

    view.on_timeout = interaction_handler.on_timeout
    return view


def get_gallery_channels_setup_view(interaction_handler: "ManageGalleryChannelsInteractionHandler") -> View:
    """
    Creates a View for managing gallery channels.
    Args:
        interaction_handler (ManageGalleryChannelsInteractionHandler): The interaction handler to use for the view.

    Returns:
        View: The created View.
    """
    view = View(timeout=600)

    channel_select = ChannelSelect(max_values=1,
                                   placeholder="Select a channel to add/remove as a gallery channel",
                                   channel_types=[discord.ChannelType.text])
    channel_select.callback = interaction_handler.on_channel_select
    view.add_item(channel_select)

    view.on_timeout = interaction_handler.on_timeout
    return view


def get_limited_messages_channels_setup_view(
        interaction_handler: "ManageLimitedMessagesChannelsInteractionHandler"
) -> View:
    """
    Creates a View for managing limited-messages channels.
    Args:
        interaction_handler (ManageLimitedMessagesChannelsInteractionHandler):
            The interaction handler to use for the view.
    Returns:
        View: The created View.
    """
    view = View(timeout=600)

    channel_select = ChannelSelect(max_values=1,
                                   placeholder="Select a channel to add/remove as a limited-messages channel",
                                   channel_types=[discord.ChannelType.text])
    channel_select.callback = interaction_handler.on_channel_select
    view.add_item(channel_select)

    view.on_timeout = interaction_handler.on_timeout
    return view
