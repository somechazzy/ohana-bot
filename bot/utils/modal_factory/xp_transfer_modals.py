import discord
from discord.ui import TextInput, Label

from bot.utils.modal_factory import BaseModal


class EnterUserIDModal(BaseModal, title="Enter User ID"):
    user_id_label = Label(
        text="Please enter the User ID.",
        component=TextInput(
            max_length=35,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_enter_user_id_modal_submit(interaction=interaction,
                                                                      user_id=self.user_id_label.component.value)


class EnterXPAmountModal(BaseModal, title="Enter XP Amount"):
    xp_amount_label = Label(
        text="Please enter the XP amount.",
        component=TextInput(
            max_length=10,
            min_length=1,
            required=True,
            style=discord.TextStyle.short
        )
    )

    async def on_submit(self, interaction: discord.Interaction):
        await self.interactions_handler.on_enter_xp_amount_modal_submit(interaction=interaction,
                                                                        amount=self.xp_amount_label.component.value)
