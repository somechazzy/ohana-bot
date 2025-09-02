import discord
from discord.ui import TextInput, Label

from bot.utils.modal_factory import BaseModal
from constants import Links


class ReminderSnoozeDurationModal(BaseModal, title="Reminder Snooze"):
    duration_label = Label(
        text="When should I remind you again?",
        description="Examples: 15m, 6h 30m, 1d 12h, 3w, etc..",
        component=TextInput(
            max_length=50,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_snooze_modal_submit(
            interaction=interaction,
            duration_text=self.duration_label.component.value
        )


class ReminderEditWhatModal(BaseModal, title="Reminder Edit: What to remind?"):
    text_label = Label(
        text="What should I remind you about?",
        component=TextInput(
            max_length=3000,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self, interactions_handler, current_what, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.text_label.component.default = current_what

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_edit_what_modal_submit(
            interaction=interaction,
            what_text=self.text_label.component.value
        )


class ReminderEditWhenModal(BaseModal, title="Reminder Edit: When to remind?"):
    text_label = Label(
        text="When should I remind you about this?",
        description="Examples: 15m, 6h 30m, 1d 12h, 3w, etc..",
        component=TextInput(
            max_length=50,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_edit_when_modal_submit(
            interaction=interaction,
            when_text=self.text_label.component.value
        )


class ReminderBasicRecurrenceInputModal(BaseModal, title="Reminder Recurrence"):
    recurrence_label = Label(
        text="Remind me every x {unit}(s)",
        description="Every how many {unit}s should I remind you?",
        component=TextInput(
            placeholder="x",
            max_length=5,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self, interactions_handler, days: bool, hours: bool, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        if days:
            self.recurrence_label.text = self.recurrence_label.text.format(unit="day")
            self.recurrence_label.description = self.recurrence_label.description.format(unit="day")
        elif hours:
            self.recurrence_label.text = self.recurrence_label.text.format(unit="hour")
            self.recurrence_label.description = self.recurrence_label.description.format(unit="hour")
        else:
            raise ValueError("At least one of days or hours should be True.")

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_basic_recurrence_input_modal_submit(
            interaction=interaction,
            recurrence_input=self.recurrence_label.component.value
        )


class ReminderConditionedRecurrenceInputModal(BaseModal, title="Reminder Recurrence"):
    recurrence_label = Label(
        text="Which days of the month should I remind you?",
        description="Enter the days of the month as numbers separated by commas. Example: 1, 15, 30",
        component=TextInput(
            placeholder="Example: 1, 15, 30",
            max_length=50,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_conditioned_recurrence_input_modal_submit(
            interaction=interaction,
            recurrence_input=self.recurrence_label.component.value
        )


class TimezoneSelectionModal(BaseModal, title="Timezone Setup"):
    timezone_label = Label(
        text="Enter your timezone",
        description=f"Copy your timezone from {Links.APPS_TIMEZONE}",
        component=TextInput(
            placeholder="Enter the timezone you copied from the website",
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_timezone_modal_submit(
            interaction=interaction,
            timezone=self.timezone_label.component.value
        )


class ReminderSetWhenModal(BaseModal, title="Reminder: When to remind?"):
    text_label = Label(
        text="When should I remind you about this?",
        description="Examples: 15m, 6h 30m, 1d 12h, 3w, etc..",
        component=TextInput(
            max_length=50,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_set_when_modal_submit(
            interaction=interaction,
            when_text=self.text_label.component.value
        )
