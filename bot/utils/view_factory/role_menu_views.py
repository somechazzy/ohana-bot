from typing import TYPE_CHECKING

import discord
from discord import ButtonStyle, SelectOption
from discord.ui import View, Button, RoleSelect, Select

from clients import emojis
from constants import RoleMenuType, RoleMenuMode
from models.dto.role_menu import RoleMenuRole

if TYPE_CHECKING:
    from bot.interaction_handlers.admin_interaction_handlers.manage_role_menu_interaction_handler import \
        ManageRoleMenuInteractionHandler


def get_role_menu_view(role_menu_type: str, role_menu_mode: str, role_menu_roles: list[RoleMenuRole]) -> View:
    """
    Creates a view for a role menu message.
    Args:
        role_menu_type (str): The type of role menu (select or buttons) - RoleMenuType.
        role_menu_mode (str): The mode of role menu (single or multi) - RoleMenuMode.
        role_menu_roles (list[RoleMenuRole]): The list of roles to include in the role menu.

    Returns:
        View: The created view.
    """
    view = View(timeout=None)

    role_menu_roles.sort()
    if role_menu_type == RoleMenuType.SELECT:
        options = [SelectOption(label="Remove role" if role_menu_mode == RoleMenuMode.SINGLE else "Remove all roles",
                                value='0',
                                emoji='❌')] + [
            SelectOption(label=role.alias, value=str(role.role_id), emoji=role.emoji) for role in role_menu_roles
        ]
        max_selections = len(role_menu_roles) if role_menu_mode == RoleMenuMode.MULTI else 1
        view.add_item(Select(options=options, max_values=max_selections))
    else:
        for i, role in enumerate(role_menu_roles):
            button = Button(label=role.alias, style=ButtonStyle.blurple, custom_id=str(role.role_id),
                            emoji=role.emoji, row=(i//5))
            view.add_item(button)

    return view


def get_role_menu_setup_view(interactions_handler: 'ManageRoleMenuInteractionHandler',
                             roles_selected: bool = True,
                             is_restricted: bool = False,
                             image_added: bool = False) -> View:
    """
    Creates a view for setting up a role menu.
    Args:
        interactions_handler (ManageRoleMenuInteractionHandler): The interaction handler to use for the view.
        roles_selected (bool): Whether any roles have been selected for the role menu.
        is_restricted (bool): Whether the role menu is restricted to certain roles.
        image_added (bool): Whether an image has been added to the role menu.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    basic_setup_button = Button(label="Basic Setup", style=ButtonStyle.green, row=0,
                                custom_id="rm_basic_setup", emoji=emojis.general.wand)
    basic_setup_button.callback = interactions_handler.go_to_basic_setup
    view.add_item(basic_setup_button)

    menu_type_button = Button(label="Change Menu Type", style=ButtonStyle.blurple, row=0,
                              custom_id="rm_change_menu_type", emoji=emojis.general.orientation)
    menu_type_button.callback = interactions_handler.change_menu_type
    view.add_item(menu_type_button)

    menu_mode_button = Button(label="Change Role Mode", style=ButtonStyle.blurple, row=0,
                              custom_id="rm_change_menu_mode", emoji=emojis.action.select)
    menu_mode_button.callback = interactions_handler.change_menu_mode
    view.add_item(menu_mode_button)

    restrict_menu_button = Button(label="Restrict Menu" if not is_restricted else "Edit menu restriction", row=1,
                                  style=ButtonStyle.green, custom_id="restrict_menu", emoji=emojis.general.chain)
    restrict_menu_button.callback = interactions_handler.go_to_restriction_setup
    view.add_item(restrict_menu_button)

    add_image_button = Button(label="Add Image" if not image_added else "Edit Image", row=1,
                              style=ButtonStyle.green, custom_id="add_image", emoji=emojis.general.image)
    add_image_button.callback = interactions_handler.go_to_image_setup
    view.add_item(add_image_button)

    add_or_edit_role_select = RoleSelect(placeholder="Add Role", min_values=1, max_values=1,
                                         custom_id="add_role_select", row=2)
    add_or_edit_role_select.callback = interactions_handler.on_add_or_edit_role_select
    view.add_item(add_or_edit_role_select)

    if roles_selected:
        remove_role_select = RoleSelect(placeholder="Remove Role", min_values=1, max_values=1,
                                        custom_id="remove_role_select", row=3)
        remove_role_select.callback = interactions_handler.on_remove_role_select
        view.add_item(remove_role_select)

    view.on_timeout = interactions_handler.on_timeout

    return view


def get_role_menu_restriction_setup_view(interactions_handler: 'ManageRoleMenuInteractionHandler',
                                         existing_roles: list[discord.Role]) -> View:
    """
    Creates a view for setting up role restrictions for a role menu.
    Args:
        interactions_handler (ManageRoleMenuInteractionHandler): The interaction handler to use for the view.
        existing_roles (list[discord.Role]): The list of roles that are currently set as restrictions.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    go_back_button = Button(label="Go Back", style=ButtonStyle.grey, row=0,
                            custom_id="go_back_to_setup", emoji=emojis.navigation.back)
    go_back_button.callback = interactions_handler.go_back
    view.add_item(go_back_button)

    edit_restriction_description_button = Button(label="Edit Restriction Description",
                                                 style=ButtonStyle.blurple, row=0,
                                                 custom_id="edit_restriction_description",
                                                 emoji=emojis.action.edit)
    edit_restriction_description_button.callback = interactions_handler.edit_restriction_description
    view.add_item(edit_restriction_description_button)

    role_select = RoleSelect(placeholder="Select or unselect roles to restrict to", min_values=0, max_values=10,
                             custom_id="restrict_role_select", row=1, default_values=existing_roles)
    role_select.callback = interactions_handler.on_restricted_role_select
    view.add_item(role_select)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_role_menu_image_setup_view(interactions_handler: 'ManageRoleMenuInteractionHandler',
                                   image_added: bool) -> View:
    """
    Creates a view for setting up an image for a role menu.
    Args:
        interactions_handler (ManageRoleMenuInteractionHandler): The interaction handler to use for the view.
        image_added (bool): Whether an image has been added to the role menu.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    go_back_button = Button(label="Go Back", style=ButtonStyle.grey, row=0,
                            custom_id="go_back_to_setup", emoji=emojis.navigation.back)
    go_back_button.callback = interactions_handler.go_back
    view.add_item(go_back_button)

    image_url_input = Button(label="Set image", style=ButtonStyle.green, row=0,
                             custom_id="set_image_button", emoji=emojis.general.image)
    image_url_input.callback = interactions_handler.go_to_image_url_input
    view.add_item(image_url_input)

    if image_added:
        remove_image_button = Button(label="Remove Image", style=ButtonStyle.red, row=1,
                                     custom_id="remove_image_button", emoji=emojis.action.delete)
        remove_image_button.callback = interactions_handler.remove_image
        view.add_item(remove_image_button)

        image_placement_button = Button(label="Change Image Placement", style=ButtonStyle.blurple, row=1,
                                        custom_id="change_image_placement", emoji=emojis.action.switch)
        image_placement_button.callback = interactions_handler.change_image_placement
        view.add_item(image_placement_button)

    view.on_timeout = interactions_handler.on_timeout
    return view
