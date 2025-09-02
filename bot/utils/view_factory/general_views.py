"""
Module containing generic views.
"""
from types import coroutine
from typing import TYPE_CHECKING

from discord import ButtonStyle, SelectOption
from discord.ui import View, Button, Select

from clients import emojis
from utils.helpers.text_manipulation_helpers import shorten_text

if TYPE_CHECKING:
    from bot.interaction_handlers import NavigationInteractionHandler, NumberedListInteractionHandler


def get_navigation_view(interaction_handler: 'NavigationInteractionHandler',
                        page: int | None = None,
                        page_count: int | None = None,
                        add_back_button: bool = False,
                        add_close_button: bool = False) -> View:
    """
    Creates a navigation view with optional back, close, previous, and next buttons.
    Args:
        interaction_handler (NavigationInteractionHandler): The interaction handler for the view.
        page (int | None): The current page number.
        page_count (int | None): The total number of pages.
        add_back_button (bool): Whether to add a back button.
        add_close_button (bool): Whether to add a close button.
    Returns:
        View: The created navigation view.
    """
    view = View(timeout=600)

    if add_back_button:
        back_button = Button(style=ButtonStyle.secondary, label="Back",
                             custom_id="navigation_back", emoji=emojis.navigation.back)
        back_button.callback = interaction_handler.go_back
        view.add_item(back_button)

    if add_close_button:
        close_button = Button(label="Close", emoji=emojis.action.delete,
                              style=ButtonStyle.gray, custom_id="close-embed")
        close_button.callback = interaction_handler.close_embed  # type: ignore (close_embed is defined in the base IH)
        view.add_item(close_button)

    if page and page_count:
        if page > 1:
            previous_button = Button(style=ButtonStyle.blurple, label="Previous",
                                     custom_id="navigation_previous", emoji=emojis.navigation.previous)
            previous_button.callback = interaction_handler.previous_page
            view.add_item(previous_button)
        if page < page_count:
            next_button = Button(style=ButtonStyle.blurple, label="Next",
                                 custom_id="navigation_next", emoji=emojis.navigation.next)
            next_button.callback = interaction_handler.next_page
            view.add_item(next_button)

    view.on_timeout = interaction_handler.on_timeout  # type: ignore
    return view


def get_numbered_list_view(interaction_handler: 'NumberedListInteractionHandler',
                           label_description_list: list[tuple[str, str]],
                           add_close_button: bool = False) -> View:
    """
    Creates a numbered list view with a select menu and optional close button.
    Args:
        interaction_handler (NumberedListInteractionHandler): The interaction handler for the view.
        label_description_list (list[tuple[str, str]]): A list of tuples containing options' labels and descriptions.
        add_close_button (bool): Whether to add a close button.
    Returns:
        View: The created numbered list view.
    """
    view = View(timeout=600)

    select_view = Select(options=[SelectOption(label=shorten_text(label, max_length=90),
                                               description=shorten_text(label, max_length=90),
                                               value=str(i),
                                               emoji=emojis.numbers[i + 1])
                                  for i, (label, description) in enumerate(label_description_list)])
    select_view.callback = interaction_handler.select_item
    view.add_item(select_view)

    if add_close_button:
        close_button = Button(label="Close", emoji=emojis.action.delete,
                              style=ButtonStyle.gray, custom_id="close-embed")
        close_button.callback = interaction_handler.close_embed  # type: ignore
        view.add_item(close_button)

    view.on_timeout = interaction_handler.on_timeout  # type: ignore
    return view


def get_external_url_view(external_url: str) -> View:
    """
    Creates a view with a button that opens an external URL.
    Args:
        external_url (str): The URL to open.
    Returns:
        View: The created view.
    """
    view = View()

    view.add_item(Button(label="Open URL", style=ButtonStyle.link, url=external_url))

    return view


def get_yes_no_view(interaction_handler, yes_callback: coroutine, no_callback: coroutine) -> View:
    """
    Creates a view with Yes and No buttons.
    Args:
        interaction_handler: The interaction handler for the view.
        yes_callback (coroutine): The callback function for the Yes button.
        no_callback (coroutine): The callback function for the No button.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    yes_button = Button(style=ButtonStyle.success, label="Yes", custom_id="yes_button")
    yes_button.callback = yes_callback
    view.add_item(yes_button)

    no_button = Button(style=ButtonStyle.danger, label="No", custom_id="no_button")
    no_button.callback = no_callback
    view.add_item(no_button)

    view.on_timeout = interaction_handler.on_timeout
    return view
