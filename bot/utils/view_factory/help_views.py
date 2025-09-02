from typing import TYPE_CHECKING

from discord.ui import View, Button
from discord import ButtonStyle

from clients import emojis
from constants import Links

if TYPE_CHECKING:
    from bot.interaction_handlers.user_interaction_handlers.help_menu_interaction_handler import \
        HelpMenuInteractionHandler


def get_main_help_view(interaction_handler: 'HelpMenuInteractionHandler') -> View:
    """
    Creates the main help menu view with buttons for user menu, admin menu, and a link to the full commands list.
    Args:
        interaction_handler (HelpMenuInteractionHandler): The handler for button interactions.
    Returns:
        View: The constructed view.
    """
    view = View(timeout=600)

    user_menu_button = Button(label="User menu", style=ButtonStyle.green, custom_id="user-menu")
    user_menu_button.callback = interaction_handler.go_to_user_menu
    view.add_item(user_menu_button)

    admin_menu_button = Button(label="Admin Menu", style=ButtonStyle.blurple, custom_id="admin-menu")
    admin_menu_button.callback = interaction_handler.go_to_admin_menu
    view.add_item(admin_menu_button)

    commands_link_button = Button(label="Full commands list", style=ButtonStyle.link,
                                  url=Links.OHANA_WEBSITE_COMMANDS)
    view.add_item(commands_link_button)

    view.on_timeout = interaction_handler.on_timeout
    return view


def get_commands_menu_view(interaction_handler: 'HelpMenuInteractionHandler') -> View:
    """
    Creates a view for the specific commands menu with a "Go Back" button and a link to the full commands list.
    Args:
        interaction_handler (HelpMenuInteractionHandler): The handler for button interactions.
    Returns:
        View: The constructed view.
    """
    view = View(timeout=600)

    go_back_button = Button(label="Go Back", style=ButtonStyle.gray, custom_id="go-back", emoji=emojis.navigation.back)
    go_back_button.callback = interaction_handler.go_back
    view.add_item(go_back_button)

    commands_link_button = Button(label="Full List", style=ButtonStyle.link, url=Links.OHANA_WEBSITE_COMMANDS)
    view.add_item(commands_link_button)

    view.on_timeout = interaction_handler.on_timeout
    return view

