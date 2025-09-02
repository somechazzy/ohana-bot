import discord
from discord.ui import Label, TextInput, Select

from bot.utils.modal_factory import BaseModal
from constants import AutoResponseMatchType


class AddAutoResponseModal(BaseModal, title="Add auto-response"):
    trigger_label = Label(
        text='Prompt/Trigger',
        description='The text that will trigger the auto-response',
        component=TextInput(
            max_length=1024,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )
    response_label = Label(
        text='Response',
        description="The response message I'll send",
        component=TextInput(
            max_length=1024,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )
    match_type_label = Label(
        text='Match type',
        description='Match type against the trigger text',
        component=Select(
            min_values=1,
            max_values=1,
            required=True
        ),
    )
    delete_original_label = Label(
        text='Delete prompt message?',
        description='Should I delete the message that triggered the auto-response?',
        component=Select(
            min_values=1,
            max_values=1,
            required=True
        ),
    )

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self._set_select_options_for_label(label=self.match_type_label,
                                           ohana_enum=AutoResponseMatchType)
        self._set_select_options_for_bool_label(label=self.delete_original_label)

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_auto_response_modal_submit(
            interaction=interaction,
            auto_response_id=None,
            trigger_text=self.trigger_label.component.value,
            response_text=self.response_label.component.value,
            match_type=self.match_type_label.component.values[0],
            delete_original=self._get_bool_from_label_select(self.delete_original_label),
            delete_auto_response=False
        )


class EditAutoResponseModal(AddAutoResponseModal, title="Edit auto-response"):
    delete_auto_response_label = Label(
        text='Delete auto-response?',
        description="Type 'delete' in the box below to delete this auto-response",
        component=TextInput(
            max_length=6,
            min_length=6,
            required=False,
            style=discord.TextStyle.short
        )
    )

    def __init__(self,
                 interactions_handler,
                 auto_response_id: int,
                 trigger_text: str,
                 response_text: str,
                 match_type: str,
                 delete_original: bool,
                 **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.auto_response_id = auto_response_id
        self.trigger_label.component.default = trigger_text
        self.response_label.component.default = response_text
        self._set_select_options_for_label(label=self.match_type_label,
                                           ohana_enum=AutoResponseMatchType,
                                           default_value=match_type)
        self._set_select_options_for_bool_label(label=self.delete_original_label,
                                                default_value=delete_original)

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_auto_response_modal_submit(
            interaction=interaction,
            auto_response_id=self.auto_response_id,
            trigger_text=self.trigger_label.component.value.strip(),
            response_text=self.response_label.component.value.strip(),
            match_type=self.match_type_label.component.values[0],
            delete_original=self._get_bool_from_label_select(self.delete_original_label),
            delete_auto_response=((self.delete_auto_response_label.component.value or "").lower() == 'delete')
        )


class AddLimitedMessagesChannelRoleNameModal(BaseModal, title="Enter role name"):
    role_name_label = Label(
        text="Role name",
        description="Enter the name of the role I'll create",
        component=TextInput(
            max_length=30,
            min_length=1,
            required=True,
            style=discord.TextStyle.short,
            placeholder="Example: 'Limited Messages Role'"
        )
    )

    def __init__(self, interactions_handler, channel_id: int, **kwargs):
        super().__init__(interactions_handler, **kwargs)
        self.interactions_handler = interactions_handler
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_limited_messages_channel_role_name_modal_submit(
            interaction=interaction,
            channel_id=self.channel_id,
            role_name=self.role_name_label.component.value.strip()
        )
