from typing import TYPE_CHECKING

from discord import SelectOption, ButtonStyle
from discord.ui import View, Select, Button

from bot.utils.view_factory.general_views import get_navigation_view
from clients import emojis
from constants import DAY_OF_WEEK_NUMBER_NAME_MAP, ReminderDeliveryAction
from models.dto.cachables import CachedReminder
from models.user_settings_models import UserReminder
from utils.helpers.text_manipulation_helpers import shorten_text

if TYPE_CHECKING:
    from bot.interaction_handlers.user_interaction_handlers.reminder_setup_interaction_handler import \
        ReminderSetupInteractionHandler
    from bot.interaction_handlers.user_interaction_handlers.reminder_list_interaction_handler import \
        ReminderListInteractionHandler


def get_reminder_delivery_view(reminder: CachedReminder) -> View:
    """
    View for the delivery message of a reminder to the user.
    Args:
        reminder (CachedReminder): The reminder to create the view for.
    Returns:
        View: The created view.
    """
    view = View(timeout=300)

    options = [SelectOption(label="Snooze 1 hour",
                            value=f"{ReminderDeliveryAction.SNOOZE_60}"),
               SelectOption(label="Snooze 12 hours",
                            value=f"{ReminderDeliveryAction.SNOOZE_720}"),
               SelectOption(label="Snooze 1 day",
                            value=f"{ReminderDeliveryAction.SNOOZE_1440}"),
               SelectOption(label="Snooze custom...",
                            value=f"{ReminderDeliveryAction.SNOOZE_CUSTOM}")]
    if not reminder.was_snoozed:
        is_recurring = bool(reminder.recurrence)
        if not reminder.is_relayed:
            if is_recurring:
                options.append(SelectOption(
                    label="Edit recurrence",
                    value=f"{ReminderDeliveryAction.EDIT}"
                ))
            else:
                options.append(SelectOption(
                    label="Setup as recurring",
                    value=f"{ReminderDeliveryAction.SETUP}"
                ))
        else:
            options.append(SelectOption(
                label="Report/Block relayed reminders from this user",
                value=f"{ReminderDeliveryAction.BLOCK_AUTHOR}"
            ))
            options.append(SelectOption(
                label="Block all relayed reminders from Ohana",
                value=f"{ReminderDeliveryAction.BLOCK_ALL}"
            ))

    select_view = Select(placeholder="Actions...",
                         options=options,
                         min_values=1,
                         max_values=1,
                         custom_id=f"{ReminderDeliveryAction.qualifier()}-{reminder.user_reminder_id}")
    view.add_item(select_view)

    return view


def get_reminder_confirmation_view(interactions_handler: 'ReminderSetupInteractionHandler',
                                   add_back_button: bool = False) -> View:
    """
    View for confirming the creation of a reminder.
    Args:
        interactions_handler (ReminderSetupInteractionHandler): The interaction handler for the view.
        add_back_button (bool): Whether to add a back button to the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=300)

    if add_back_button:
        back_button = Button(label="Go back",
                             emoji=emojis.navigation.back,
                             style=ButtonStyle.gray,
                             custom_id="back")
        back_button.callback = interactions_handler.go_back
        view.add_item(back_button)

    setup_button = Button(label="Edit/Setup Recurrence",
                          style=ButtonStyle.blurple,
                          custom_id="edit-reminder",
                          emoji=emojis.general.settings)
    setup_button.callback = interactions_handler.go_to_setup
    view.add_item(setup_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_reminder_setup_view(interactions_handler: 'ReminderSetupInteractionHandler',
                            timezone_set: bool,
                            add_back_button: bool = False,
                            show_recurrence: bool = True) -> View:
    """
    View for setting up a reminder.
    Args:
        interactions_handler (ReminderSetupInteractionHandler): The interaction handler for the view.
        timezone_set (bool): Whether the user's timezone is set.
        add_back_button (bool): Whether to add a back button to the view.
        show_recurrence (bool): Whether to show the recurrence options.
    Returns:
        View: The created view.
    """
    reminder = interactions_handler.reminder
    view = View(timeout=300)

    if add_back_button:
        back_button = Button(label="Go back", emoji=emojis.navigation.back,
                             style=ButtonStyle.gray, custom_id="back")
        back_button.callback = interactions_handler.go_back
        view.add_item(back_button)

    edit_what_button = Button(label="Edit What", style=ButtonStyle.blurple, custom_id="edit-reminder-what",
                              emoji=emojis.action.rename, row=0)
    edit_what_button.callback = interactions_handler.go_to_edit_what
    view.add_item(edit_what_button)

    edit_when_button = Button(label="Edit When", style=ButtonStyle.blurple, custom_id="edit-reminder-when",
                              emoji=emojis.general.clock, row=0)
    edit_when_button.callback = interactions_handler.go_to_edit_when
    view.add_item(edit_when_button)

    delete_button = Button(label="Delete", style=ButtonStyle.red, custom_id="delete-reminder",
                           emoji=emojis.action.delete, row=0)
    delete_button.callback = interactions_handler.go_to_delete
    view.add_item(delete_button)

    if show_recurrence:
        recurrence_select = Select(
            placeholder="Repeat.." if not reminder.is_relayed else "Edit Recurrence",
            min_values=1, max_values=1,
            custom_id="reminder-recurrence-setup", row=1,
            options=[SelectOption(label="Every x hours",
                                  value=interactions_handler.RecurrenceSelectValue.HOURS),
                     SelectOption(label="Every x days",
                                  value=interactions_handler.RecurrenceSelectValue.DAYS),
                     SelectOption(label="On the same day every week",
                                  value=interactions_handler.RecurrenceSelectValue.WEEKLY),
                     SelectOption(label="On the same day every month",
                                  value=interactions_handler.RecurrenceSelectValue.MONTHLY,
                                  description="You'll be asked to enter your timezone" if not timezone_set else None),
                     SelectOption(label="On the same day every year",
                                  value=interactions_handler.RecurrenceSelectValue.YEARLY,
                                  description="You'll be asked to enter your timezone" if not timezone_set else None),
                     SelectOption(label="On certain days of the week",
                                  value=interactions_handler.RecurrenceSelectValue.WEEKLY_DAYS,
                                  description="You'll be asked to enter your timezone" if not timezone_set else None),
                     SelectOption(label="On certain days of the month",
                                  value=interactions_handler.RecurrenceSelectValue.MONTHLY_DAYS,
                                  description="You'll be asked to enter your timezone" if not timezone_set else None)]
        )
        if reminder.recurrence:
            recurrence_select.options.insert(0,
                                             SelectOption(label="Remove recurrence",
                                                          value=interactions_handler.RecurrenceSelectValue.DELETE,
                                                          emoji=emojis.action.delete))
        recurrence_select.callback = interactions_handler.go_to_recurrence_setup
        view.add_item(recurrence_select)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_delete_confirmation_view(interactions_handler: 'ReminderSetupInteractionHandler') -> View:
    """
    View for confirming the deletion of a reminder.
    Args:
        interactions_handler (ReminderSetupInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=300)

    cancel_button = Button(label="Cancel", style=ButtonStyle.gray, custom_id="cancel-delete",
                           emoji=emojis.navigation.back, row=0)
    cancel_button.callback = interactions_handler.on_delete_cancel
    view.add_item(cancel_button)

    confirm_button = Button(label="Yes, delete", style=ButtonStyle.red, custom_id="confirm-delete",
                            emoji=emojis.action.delete, row=0)
    confirm_button.callback = interactions_handler.on_delete_confirmation
    view.add_item(confirm_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_weekdays_selection_view(interactions_handler: 'ReminderSetupInteractionHandler') -> View:
    """
    View for selecting weekdays for a weekly recurring reminder.
    Args:
        interactions_handler (ReminderSetupInteractionHandler): The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=300)

    options = [SelectOption(label=name, value=number, emoji=emojis.weekday[number])
               for number, name in DAY_OF_WEEK_NUMBER_NAME_MAP.items()]
    select_view = Select(placeholder="Select the weekdays", options=options, row=0, max_values=7, min_values=1)
    select_view.callback = interactions_handler.go_to_weekdays_selection
    view.add_item(select_view)

    cancel_button = Button(label="Cancel", style=ButtonStyle.gray, custom_id="cancel-timezone",
                           emoji=emojis.navigation.back, row=1)
    cancel_button.callback = interactions_handler.on_cancel_setup
    view.add_item(cancel_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_reminder_list_view(interactions_handler: 'ReminderListInteractionHandler',
                           reminders: list[UserReminder],
                           page: int,
                           page_count: int,
                           page_size: int) -> View:
    """
    View for listing reminders with pagination and selection.
    Args:
        interactions_handler (ReminderListInteractionHandler): The interaction handler for the view.
        reminders (list[UserReminder]): The list of reminders to display.
        page (int): The current page number.
        page_count (int): The total number of pages.
        page_size (int): The number of reminders per page.
    Returns:
        View: The created view.
    """
    view = get_navigation_view(interaction_handler=interactions_handler,
                               page=page,
                               page_count=page_count,
                               add_back_button=False)

    if reminders:
        options = []
        offset = (page - 1) * page_size
        for idx, reminder in enumerate(reminders[offset: offset + page_size], offset + 1):
            options.append(SelectOption(
                label=f"[{idx}]",
                value=str(reminder.id),
                description=f"\"{shorten_text(reminder.reminder_text, 40)}\""
            ))
        select_view = Select(placeholder="Select to manage...", options=options, row=1, min_values=1, max_values=1)
        select_view.callback = interactions_handler.on_reminder_select
        view.add_item(select_view)

    view.on_timeout = interactions_handler.on_timeout
    return view
