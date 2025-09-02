"""
Module containing the base modal class and other generic modals.
"""
from types import coroutine
from typing import Type

import discord
from discord import SelectOption
from discord.ui import Modal, TextInput, Label

from constants import OhanaEnum


class BaseModal(Modal, title="Form"):

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(**kwargs)
        self.interactions_handler = interactions_handler
        self.modal_name = self.__class__.__name__

    async def interaction_check(self, interaction: discord.Interaction):
        return self.interactions_handler.source_interaction.user.id == interaction.user.id

    async def on_submit(self, interaction: discord.Interaction):
        raise NotImplementedError

    @staticmethod
    def _set_select_options_for_label(label: Label,
                                      ohana_enum: Type[OhanaEnum],
                                      default_value: str | None = None):
        label.component.options = [
            SelectOption(label=value.replace('_', ' ').title(),
                         value=value,
                         default=default_value and value == default_value)
            for value in ohana_enum.as_list()
        ]

    @staticmethod
    def _set_select_options_for_bool_label(label: Label,
                                           default_value: bool | None = None):
        label.component.options = [
            SelectOption(label="Yes", value="true", default=default_value is True),
            SelectOption(label="No", value="false", default=default_value is False)
        ]

    @staticmethod
    def _get_bool_from_label_select(label: Label) -> bool | None:
        if label.component.values:
            return label.component.values[0].lower() == "true"
        return None


class ConfirmationModal(Modal, title="Confirm"):
    confirm_input = TextInput(
        label="This action cannot be reverted.",
        max_length=100,
        min_length=1,
        required=True,
        placeholder="Type \"CONFIRM\" to confirm.",
        style=discord.TextStyle.short
    )

    def __init__(self,
                 callback: coroutine,
                 callback_params: dict | None = None,
                 custom_label: str | None = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.callback_params = callback_params or {}
        if custom_label:
            self.confirm_input.label = custom_label

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirm_input.value.lower() != "confirm":
            return await interaction.response.send_message("Action not confirmed.", ephemeral=True)
        await self.callback(interaction, **self.callback_params)
