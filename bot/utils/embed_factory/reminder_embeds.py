from datetime import datetime, UTC

import discord

from clients import emojis
from constants import Colour, DiscordTimestamp
from models.dto.cachables import CachedReminder
from models.user_settings_models import UserReminder
from utils.helpers.text_manipulation_helpers import get_human_readable_time, shorten_text


def get_reminder_delivery_embed(reminder: CachedReminder) -> discord.Embed:
    """
    Embed for delivering a reminder to the user.
    Args:
        reminder (CachedReminder): The reminder to deliver.
    Returns:
        discord.Embed: The embed to send.
    """
    minutes_late = (datetime.now(UTC) - reminder.reminder_time).total_seconds() // 60
    is_recurring = bool(reminder.recurrence)

    embed = discord.Embed(
        description=f"{reminder.reminder_text}",
        color=Colour.GREEN
    )

    title = "Reminder"
    if reminder.is_relayed:
        title = f"Relayed {title}"
    if reminder.was_snoozed:
        title = f"Snoozed {title}"
    if minutes_late > 5:
        title = f"Belated {title}"
        embed.add_field(name="Delay", value=f"I was offline {get_human_readable_time(minutes=minutes_late)} "
                                            f"ago so I missed the reminder. Sorry!", inline=False)

    embed.title = f"⏱ {title}"

    if reminder.is_relayed:
        embed.add_field(name="Relayed by", value=f"<@!{reminder.owner_user_id}> ({reminder.owner_user_id})\n",
                        inline=False)
        embed.set_footer(text="You can take actions (report, block, etc..) using the menu below")
    elif is_recurring:
        embed.set_footer(text=f"This reminder repeats: {reminder.recurrence}")

    return embed


def get_reminder_confirmation_embed(reminder: UserReminder, feedback_message: str | None = None) -> discord.Embed:
    """
    Embed for confirming a reminder creation.
    Args:
        reminder (UserReminder): The reminder to confirm.
        feedback_message (str | None): Optional feedback message to include in the embed.
    Returns:
        discord.Embed: The embed to send.
    """
    embed = discord.Embed(
        title="✅ Reminder Set!",
        color=Colour.GREEN
    )

    embed.add_field(name="What",
                    value=f"> {shorten_text(reminder.reminder_text, 990)}",
                    inline=False)
    embed.add_field(
        name="When",
        value=f"{DiscordTimestamp.LONG_DATE_TIME.format(timestamp=int(reminder.reminder_time.timestamp()))} "
              f"({DiscordTimestamp.RELATIVE_TIME.format(timestamp=int(reminder.reminder_time.timestamp()))})",
        inline=True
    )

    if reminder.is_relayed:
        embed.add_field(name="Who", value=f"<@!{reminder.recipient.user_id}>",
                        inline=False)

    if reminder.recurrence:
        embed.add_field(
            name="Recurrence",
            value=f"{CachedReminder.RecurrenceSettings.get_recurrence_descriptor_from_orm_object(reminder.recurrence)}",
            inline=False
        )

    if feedback_message:
        embed.add_field(name="Note", value=feedback_message, inline=False)

    embed.set_footer(text="View and manage your reminders using /remind list")

    return embed


def get_reminder_setup_embed(reminder: UserReminder, feedback_message: str | None = None) -> discord.Embed:
    """
    Embed for configuring a reminder.
    Args:
        reminder (UserReminder): The reminder to configure.
        feedback_message (str | None): Optional feedback message to include in the embed.
    Returns:
        discord.Embed: The created embed.
    """
    embed = discord.Embed(
        title="⚙️ Reminder Setup",
        description="Configure your reminder settings",
        color=Colour.PRIMARY_ACCENT
    )

    embed.add_field(name="What", value=f"> {reminder.reminder_text}",
                    inline=False)
    embed.add_field(
        name="When",
        value=f"{DiscordTimestamp.LONG_DATE_TIME.format(timestamp=int(reminder.reminder_time.timestamp()))} "
              f"({DiscordTimestamp.RELATIVE_TIME.format(timestamp=int(reminder.reminder_time.timestamp()))})",
        inline=True
    )

    if reminder.is_relayed:
        embed.add_field(name="Who", value=f"<@!{reminder.recipient.user_id}>",
                        inline=False)

    if reminder.recurrence:
        embed.add_field(
            name="Recurrence",
            value=f"{CachedReminder.RecurrenceSettings.get_recurrence_descriptor_from_orm_object(reminder.recurrence)}",
            inline=False
        )

    if feedback_message:
        embed.add_field(name="Note", value=feedback_message, inline=False)

    embed.set_footer(text=f"Reminder ref: {reminder.id}")

    return embed


def get_reminder_delete_confirmation_embed() -> discord.Embed:
    """
    Embed for confirming the deletion of a reminder.
    Returns:
        discord.Embed: The embed to send.
    """
    embed = discord.Embed(
        title="⚠️ Delete Confirmation",
        description="Are you sure you want to delete this reminder?",
        color=Colour.RED
    )

    return embed


def get_reminder_weekdays_selection_embed() -> discord.Embed:
    """
    Embed for selecting the weekdays for a recurring reminder.
    Returns:
        discord.Embed: The embed to send.
    """
    embed = discord.Embed(
        title="📅 Reminder Recurrence",
        description="On which days of the week should I remind you? Use the selection menu below.",
        color=Colour.PRIMARY_ACCENT,
    )

    return embed


def get_reminder_list_embed(reminders: list[UserReminder],
                            page: int,
                            page_count: int,
                            page_size: int = 5,
                            feedback_message: str | None = None) -> discord.Embed:
    """
    Embed for listing reminders.
    Args:
        reminders (list[UserReminder]): The list of reminders to display.
        page (int): The current page number.
        page_count (int): The total number of pages.
        page_size (int): The number of reminders per page.
        feedback_message (str | None): Optional feedback message to include in the embed.
    Returns:
        discord.Embed: The created embed.
    """
    embed = discord.Embed(
        title="Reminders",
        description=f"Select a reminder to view and manage it.\n‎",
        color=Colour.PRIMARY_ACCENT
    )

    if reminders:
        offset = (page - 1) * page_size
        for idx, reminder in enumerate(reminders[offset: offset + page_size], offset + 1):
            what = shorten_text(reminder.clean_reminder_text, 50)
            when = DiscordTimestamp.LONG_DATE_TIME.format(timestamp=int(reminder.reminder_time.timestamp())) \
                + f" ({DiscordTimestamp.RELATIVE_TIME.format(timestamp=int(reminder.reminder_time.timestamp()))})"
            field_value = f"**What**: `{what}`\n" \
                          f"**When**: {when}"
            if not reminder.is_relayed:
                recurrence_descriptor = CachedReminder.RecurrenceSettings.get_recurrence_descriptor_from_orm_object(
                    reminder.recurrence
                )
                field_value += f"\n**Recurrence**: {recurrence_descriptor}"
            else:
                field_value += f"\n**Recipient**: <@!{reminder.recipient.user_id}>"
            field_value += "\n‎"
            embed.add_field(
                name=emojis.numbers[idx],
                value=field_value,
                inline=False
            )
    else:
        embed.add_field(name="No reminders", value="You don't have any reminders yet. Use `/remind me` to add one!\n‎",
                        inline=False)

    if feedback_message:
        embed.add_field(name="Note", value=feedback_message, inline=False)

    embed.set_footer(text=f"Page {page}/{page_count}")

    return embed
