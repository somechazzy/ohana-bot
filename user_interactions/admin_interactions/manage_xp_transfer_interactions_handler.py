import discord

from globals_.clients import xp_service
from utils.embed_factory import quick_embed
from globals_ import shared_memory
from globals_.constants import XPTransferActionTarget, XPTransferAction, GuildLogType
from utils.helpers import quick_role_select_view, quick_member_select_view
from user_interactions.admin_interactions.base_admin_interactions_handler import AdminInteractionsHandler
from utils.decorators import interaction_handler
from user_interactions.modals.admin_xp_modals import XPTransferAmountModal, XPTransferResetConfirmationModal, \
    XPTransferEnterUserIDModal


class ManageXPTransferInteractionsHandler(AdminInteractionsHandler):

    def __init__(self, source_interaction, guild, target, action):
        super().__init__(source_interaction=source_interaction, guild=guild)
        self.target = target
        self.action = action
        self.members_to_action = self.guild.members if target == XPTransferActionTarget.EVERYONE else []

    async def handle_xp_transfer_amount_modal_submit(self, inter: discord.Interaction, amount, selected_role=None):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        if not amount.isdigit():
            return await inter.response.send_message("Invalid amount, please enter a number", ephemeral=True)

        amount = int(amount)
        offset = amount if self.action == XPTransferAction.AWARD else -amount

        if self.target == XPTransferActionTarget.EVERYONE:
            await inter.response.send_message(
                embed=quick_embed("Adjusting XP and level roles, this might take a while.."),
            )
        else:
            await inter.response.defer()
            await self.source_interaction.edit_original_response(
                embed=quick_embed("Adjusting XP and level roles, this might take a while.."),
            )

        for member in self.members_to_action:
            if member.bot:
                continue
            await xp_service.add_xp_action(guild_id=self.guild.id, member_id=member.id, xp_offset=offset)

        if self.target == XPTransferActionTarget.EVERYONE:
            await self.log_action_to_server(event="Adjusted XP for all members",
                                            event_type=GuildLogType.GENERAL,
                                            field_value_map={"Amount": amount,
                                                             "Actor": self.source_interaction.user.mention})

        elif self.target == XPTransferActionTarget.ROLE:
            await self.log_action_to_server(event="Adjusted XP for all members in a role",
                                            event_type=GuildLogType.GENERAL,
                                            field_value_map={"Amount": amount,
                                                             "Role": selected_role.mention,
                                                             "Actor": self.source_interaction.user.mention})

        elif self.target == XPTransferActionTarget.MEMBER:
            await self.log_action_to_server(event="Adjusted XP for a member",
                                            event_type=GuildLogType.GENERAL,
                                            field_value_map={"Amount": amount,
                                                             "Member": self.members_to_action[0].mention,
                                                             "Actor": self.source_interaction.user.mention})

    async def handle_xp_transfer_reset_confirmation_modal_submit(self, inter: discord.Interaction, selected_role):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        if selected_role:
            await inter.response.defer()
            await self.source_interaction.edit_original_response(embed=quick_embed("Resetting XP for this role, "
                                                                                   "this might take a while..."),
                                                                 view=None)
        else:
            await inter.response.send_message(embed=quick_embed("Resetting XP for everyone, "
                                                                "this might take a while..."))

        for member in self.members_to_action:
            await xp_service.add_xp_action(guild_id=self.guild.id, member_id=member.id, reset=True)

        if selected_role:
            await self.log_action_to_server(event="Reset XP for all members in a role",
                                            event_type=GuildLogType.GENERAL,
                                            field_value_map={"Role": selected_role.mention,
                                                             "Actor": self.source_interaction.user.mention})
        else:
            await self.log_action_to_server(event="Reset XP for all members",
                                            event_type=GuildLogType.GENERAL,
                                            field_value_map={"Actor": self.source_interaction.user.mention})

    @interaction_handler
    async def handle_role_select(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        role = self.guild.get_role(int(inter.data["values"][0]))

        self.members_to_action = role.members

        if self.action in (XPTransferAction.AWARD, XPTransferAction.TAKE_AWAY):
            return await inter.response.send_modal(XPTransferAmountModal(interactions_handler=self,
                                                                         target=self.target,
                                                                         action=self.action,
                                                                         selected_role=role))

        await inter.response.send_modal(XPTransferResetConfirmationModal(interactions_handler=self,
                                                                         selected_role=role))

    @interaction_handler
    async def handle_member_select(self, inter: discord.Interaction, user_id=None):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        if not user_id:
            user_id = int(inter.data["values"][0])
        member = self.guild.get_member(user_id)

        if not member and not shared_memory.guilds_xp[self.guild.id].members_xp.get(user_id):
            return await inter.response.send_message(embed=quick_embed("Cannot find user."), ephemeral=True)
        if member and member.bot:
            return await inter.response.send_message(embed=quick_embed("Bots don't have XP."), ephemeral=True)

        self.members_to_action = [member]

        if self.action in (XPTransferAction.AWARD, XPTransferAction.TAKE_AWAY):
            return await inter.response.send_modal(XPTransferAmountModal(interactions_handler=self,
                                                                         target=self.target,
                                                                         action=self.action))
        await inter.response.defer()

        await xp_service.add_xp_action(guild_id=self.guild.id, member_id=member.id, reset=True)

        await self.source_interaction.edit_original_response(
            embed=quick_embed(f"Reset {member.mention if member else user_id}'s XP"),
            view=None
        )

        await self.log_action_to_server(event=f"Reset XP for someone",
                                        event_type=GuildLogType.GENERAL,
                                        field_value_map={"Member": member.mention if member else user_id,
                                                         "Actor": self.source_interaction.user.mention})

    @interaction_handler
    async def handle_user_id_select(self, inter: discord.Interaction):
        if not self.source_interaction.user.id == inter.user.id:
            return await inter.response.defer()

        await inter.response.send_modal(XPTransferEnterUserIDModal(interactions_handler=self))

    def get_embed_and_views(self):
        text = f"‎Select target from the list below"

        if self.target == XPTransferActionTarget.ROLE:
            views = quick_role_select_view(placeholder="Select targeted role",
                                           callback=self.handle_role_select,
                                           on_timeout=self.on_timeout)
        else:
            views = quick_member_select_view(placeholder="Select targeted member",
                                             callback=self.handle_member_select,
                                             add_user_id_button=True,
                                             user_id_button_callback=self.handle_user_id_select,
                                             on_timeout=self.on_timeout)
            text += "\nIf the user is no longer in the server, click \"Select by user ID\""

        embed = quick_embed(
            title=f"{self.action.value.capitalize()} XP for {self.target.value}",
            text=text,
            emoji='',
            bold=False,
        )
        return embed, views
