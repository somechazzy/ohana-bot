from typing import TYPE_CHECKING

from discord import ButtonStyle
from discord.ui import View, Button, RoleSelect, ChannelSelect, UserSelect

from clients import emojis

if TYPE_CHECKING:
    from bot.interaction_handlers.admin_interaction_handlers.manage_xp_settings_interaction_handler import \
        ManageXPSettingsInteractionHandler
    from bot.interaction_handlers.admin_interaction_handlers.manage_xp_transfer_interaction_handler import \
        ManageXPTransferInteractionHandler


def get_xp_setup_view(interactions_handler: 'ManageXPSettingsInteractionHandler',
                      xp_gain_enabled: bool,
                      level_up_message_enabled: bool,
                      xp_decay_enabled: bool,
                      level_roles_added: bool,
                      level_role_stacking_enabled: bool) -> View:
    """
    Creates a view for managing XP settings in a Discord server.
    Args:
        interactions_handler (ManageXPSettingsInteractionHandler): The interaction handler for the view.
        xp_gain_enabled (bool): Whether XP gain is enabled.
        level_up_message_enabled (bool): Whether level-up messages are enabled.
        xp_decay_enabled (bool): Whether XP decay is enabled.
        level_roles_added (bool): Whether any level roles have been added.
        level_role_stacking_enabled (bool): Whether level role stacking is enabled.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    if not xp_gain_enabled:
        xp_gain_button = Button(label="Enable XP Gain", style=ButtonStyle.green, row=0,
                                custom_id="enable_xp_gain", emoji=emojis.action.switch)
    else:
        xp_gain_button = Button(label="Disable XP Gain", style=ButtonStyle.red, row=0,
                                custom_id="disable_xp_gain", emoji=emojis.action.switch)
    xp_gain_button.callback = interactions_handler.toggle_xp_gain
    view.add_item(xp_gain_button)

    if not xp_gain_enabled:
        return view

    if level_up_message_enabled:
        level_up_message_button = Button(label="Disable Level-up Message", style=ButtonStyle.red, row=0,
                                         custom_id="disable_level_up_message", emoji=emojis.action.switch)
    else:
        level_up_message_button = Button(label="Enable Level-up Message", style=ButtonStyle.green, row=0,
                                         custom_id="enable_level_up_message", emoji=emojis.action.switch)
    level_up_message_button.callback = interactions_handler.toggle_level_up_message
    view.add_item(level_up_message_button)

    if xp_decay_enabled:
        xp_decay_button = Button(label="Disable XP Decay", style=ButtonStyle.red, row=0,
                                 custom_id="disable_xp_decay", emoji=emojis.action.switch)
    else:
        xp_decay_button = Button(label="Enable XP Decay", style=ButtonStyle.green, row=0,
                                 custom_id="enable_xp_decay", emoji=emojis.action.switch)
    xp_decay_button.callback = interactions_handler.toggle_xp_decay
    view.add_item(xp_decay_button)

    xp_gain_settings_button = Button(label="XP Gain Settings", style=ButtonStyle.blurple, row=1,
                                     custom_id="xp_gain_settings", emoji=emojis.general.settings,
                                     disabled=not xp_gain_enabled)
    xp_gain_settings_button.callback = interactions_handler.go_to_xp_gain_settings
    view.add_item(xp_gain_settings_button)

    level_up_message_settings_button = Button(label="Level-up Message Settings", style=ButtonStyle.blurple, row=1,
                                              custom_id="level_up_message_settings", emoji=emojis.general.settings,
                                              disabled=not level_up_message_enabled)
    level_up_message_settings_button.callback = interactions_handler.go_to_level_up_message_settings
    view.add_item(level_up_message_settings_button)

    xp_decay_settings_button = Button(label="XP Decay Settings", style=ButtonStyle.blurple, row=1,
                                      custom_id="xp_decay_settings", emoji=emojis.general.settings,
                                      disabled=not xp_decay_enabled)
    xp_decay_settings_button.callback = interactions_handler.go_to_xp_decay_settings
    view.add_item(xp_decay_settings_button)

    if level_roles_added:
        if level_role_stacking_enabled:
            button_label = "Disable level role stacking"
        else:
            button_label = "Enable level role stacking"
        stack_level_roles_button = Button(label=button_label, style=ButtonStyle.gray,
                                          custom_id="stack_roles_toggle", row=1)
        stack_level_roles_button.callback = interactions_handler.toggle_level_role_stacking
        view.add_item(stack_level_roles_button)

    level_role_select = RoleSelect(placeholder="Select a level role to add or remove",
                                   max_values=1, row=2)
    level_role_select.callback = interactions_handler.on_level_role_select
    view.add_item(level_role_select)

    ignored_channel_select = ChannelSelect(placeholder="Select an Ignored Channel to add or remove",
                                           max_values=1, row=3)
    ignored_channel_select.callback = interactions_handler.on_ignored_channel_select
    view.add_item(ignored_channel_select)

    ignored_role_select = RoleSelect(placeholder="Select an Ignored Role to add or remove",
                                     max_values=1, row=4)
    ignored_role_select.callback = interactions_handler.on_ignored_role_select
    view.add_item(ignored_role_select)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_transfer_xp_from_member_view(interaction_handler: 'ManageXPTransferInteractionHandler') -> View:
    """
    Creates a view for transferring XP from one member to another.
    Args:
        interaction_handler (ManageXPTransferInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    user_id_button = Button(label="Enter user ID instead",
                            style=ButtonStyle.gray)
    user_id_button.callback = interaction_handler.enter_user_id
    view.add_item(user_id_button)

    user_select = UserSelect(placeholder="Select user to transfer XP from",
                             min_values=1, max_values=1)
    user_select.callback = interaction_handler.on_target_member_select
    view.add_item(user_select)

    return view


def get_transfer_xp_to_member_view(interaction_handler: 'ManageXPTransferInteractionHandler') -> View:
    """
    Creates a view for transferring XP to another member.
    Args:
        interaction_handler (ManageXPTransferInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    user_select = UserSelect(placeholder="Select user to transfer XP to",
                             min_values=1, max_values=1)
    user_select.callback = interaction_handler.on_other_target_member_select
    view.add_item(user_select)

    return view


def get_award_xp_to_member_view(interaction_handler: 'ManageXPTransferInteractionHandler') -> View:
    """
    Creates a view for awarding XP to a member.
    Args:
        interaction_handler (ManageXPTransferInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    user_select = UserSelect(placeholder="Select user to award XP to",
                             min_values=1, max_values=1)
    user_select.callback = interaction_handler.on_target_member_select
    view.add_item(user_select)

    return view


def get_take_away_xp_from_member_view(interaction_handler: 'ManageXPTransferInteractionHandler') -> View:
    """
    Creates a view for taking away XP from a member.
    Args:
        interaction_handler (ManageXPTransferInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    user_id_button = Button(label="Enter user ID instead",
                            style=ButtonStyle.gray)
    user_id_button.callback = interaction_handler.enter_user_id
    view.add_item(user_id_button)

    user_select = UserSelect(placeholder="Select user to take XP from",
                             min_values=1, max_values=1)
    user_select.callback = interaction_handler.on_target_member_select
    view.add_item(user_select)

    return view


def get_reset_xp_for_member_view(interaction_handler: 'ManageXPTransferInteractionHandler') -> View:
    """
    Creates a view for resetting XP for a member.
    Args:
        interaction_handler (ManageXPTransferInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    user_id_button = Button(label="Enter user ID instead",
                            style=ButtonStyle.gray)
    user_id_button.callback = interaction_handler.enter_user_id
    view.add_item(user_id_button)

    user_select = UserSelect(placeholder="Select user to reset XP for",
                             min_values=1, max_values=1)
    user_select.callback = interaction_handler.on_target_member_select
    view.add_item(user_select)

    return view


def get_award_xp_to_role_view(interaction_handler: 'ManageXPTransferInteractionHandler') -> View:
    """
    Creates a view for awarding XP to a role.
    Args:
        interaction_handler (ManageXPTransferInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    role_select = RoleSelect(placeholder="Select role to award XP to",
                             min_values=1, max_values=1)
    role_select.callback = interaction_handler.on_target_role_select
    view.add_item(role_select)

    return view


def get_take_away_xp_from_role_view(interaction_handler: 'ManageXPTransferInteractionHandler') -> View:
    """
    Creates a view for taking away XP from a role.
    Args:
        interaction_handler (ManageXPTransferInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    role_select = RoleSelect(placeholder="Select role to take XP from",
                             min_values=1, max_values=1)
    role_select.callback = interaction_handler.on_target_role_select
    view.add_item(role_select)

    return view


def get_reset_xp_for_role_view(interaction_handler: 'ManageXPTransferInteractionHandler') -> View:
    """
    Creates a view for resetting XP for a role.
    Args:
        interaction_handler (ManageXPTransferInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    role_select = RoleSelect(placeholder="Select role to reset XP for",
                             min_values=1, max_values=1)
    role_select.callback = interaction_handler.on_target_role_select
    view.add_item(role_select)

    return view
