import discord

from bot.interaction_handlers.admin_interaction_handlers import AdminInteractionHandler
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.xp_management_embeds import get_transfer_xp_from_member_embed, \
    get_award_xp_to_member_embed, get_award_xp_to_role_embed, get_take_away_xp_from_member_embed, \
    get_take_away_xp_from_role_embed, get_reset_xp_for_role_embed, get_reset_xp_for_member_embed, \
    get_transfer_xp_to_member_embed
from bot.utils.guild_logger import GuildLogger
from bot.utils.layout_factory.xp_management_layouts import XPTransferLayout, XPTransferSummaryLayout
from bot.utils.modal_factory import ConfirmationModal
from bot.utils.modal_factory.xp_transfer_modals import EnterXPAmountModal, EnterUserIDModal
from bot.utils.view_factory.xp_management_views import get_transfer_xp_from_member_view, get_award_xp_to_member_view, \
    get_award_xp_to_role_view, get_take_away_xp_from_role_view, get_reset_xp_for_member_view, \
    get_reset_xp_for_role_view, get_transfer_xp_to_member_view, get_take_away_xp_from_member_view
from clients import xp_service
from common.exceptions import UserInputException
from components.guild_user_xp_components.guild_user_xp_component import GuildUserXPComponent
from models.dto.xp import XPAction
from constants import XPActionEnums, GuildLogEvent


class ManageXPTransferInteractionHandler(AdminInteractionHandler):
    VIEW_NAME = "XP management"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_action: str | None = None  # XPActionEnums.MainAction
        self.selected_target_type: str | None = None  # XPActionEnums.ActionTargetType
        self.selected_member: discord.Member | None = None
        self.selected_user_id: int | None = None
        self.selected_other_member: discord.Member | None = None
        self.selected_role: discord.Role | None = None
        self.xp_amount: int = 0

        self.guild_user_xp_component = GuildUserXPComponent()

    @interaction_handler()
    async def on_action_select(self, interaction: discord.Interaction):
        self.selected_action = interaction.data["custom_id"]
        self.selected_target_type = None
        self.selected_member = None
        self.selected_user_id = None
        self.selected_other_member = None
        self.selected_role = None
        if self.selected_action == XPActionEnums.MainAction.TRANSFER_XP:
            embed = get_transfer_xp_from_member_embed()
            view = get_transfer_xp_from_member_view(interaction_handler=self)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            await self.refresh_message(feedback="Awaiting member selection...")
        else:
            await interaction.response.defer()
            await self.refresh_message()

    @interaction_handler()
    async def on_target_type_select(self, interaction: discord.Interaction):
        self.selected_target_type = interaction.data["custom_id"]
        self.selected_member = None
        self.selected_user_id = None
        self.selected_other_member = None
        self.selected_role = None
        if self.selected_action == XPActionEnums.MainAction.AWARD_XP:
            if self.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
                embed = get_award_xp_to_member_embed()
                view = get_award_xp_to_member_view(interaction_handler=self)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                await self.refresh_message(feedback="Awaiting member selection...")
            elif self.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
                embed = get_award_xp_to_role_embed()
                view = get_award_xp_to_role_view(interaction_handler=self)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                await self.refresh_message(feedback="Awaiting role selection...")
            else:
                await interaction.response.defer()
                await self.refresh_message()
        elif self.selected_action == XPActionEnums.MainAction.TAKE_AWAY_XP:
            if self.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
                embed = get_take_away_xp_from_member_embed()
                view = get_take_away_xp_from_member_view(interaction_handler=self)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                await self.refresh_message(feedback="Awaiting member selection...")
            elif self.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
                embed = get_take_away_xp_from_role_embed()
                view = get_take_away_xp_from_role_view(interaction_handler=self)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                await self.refresh_message(feedback="Awaiting role selection...")
            else:
                await interaction.response.defer()
                await self.refresh_message()
        elif self.selected_action == XPActionEnums.MainAction.RESET_XP:
            if self.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
                embed = get_reset_xp_for_member_embed()
                view = get_reset_xp_for_member_view(interaction_handler=self)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                await self.refresh_message(feedback="Awaiting member selection...")
            elif self.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
                embed = get_reset_xp_for_role_embed()
                view = get_reset_xp_for_role_view(interaction_handler=self)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                await self.refresh_message(feedback="Awaiting role selection...")
            else:
                await interaction.response.defer()
                await self.refresh_message()
        else:
            await interaction.response.defer()
            await self.refresh_message()

    @interaction_handler()
    async def on_target_member_select(self, interaction: discord.Interaction):
        member = await self.guild.fetch_member(int(interaction.data["values"][0]))
        if member.bot:
            raise UserInputException("You cannot select a bot member for this action.")
        if self.selected_member or self.selected_user_id:
            self.selected_other_member = member
        else:
            self.selected_member = member
            self.selected_other_member = None
            self.selected_user_id = None
        self.selected_role = None
        if self.selected_action == XPActionEnums.MainAction.TRANSFER_XP and not self.selected_other_member:
            embed = get_transfer_xp_to_member_embed()
            view = get_transfer_xp_to_member_view(interaction_handler=self)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            await self.refresh_message(feedback="Awaiting other member selection...")
        else:
            await interaction.response.defer()
            await self.refresh_message()
            try:
                await interaction.delete_original_response()
            except Exception as e:
                self.logger.debug(f"Failed to delete target member selection message: {e}")

    @interaction_handler()
    async def enter_user_id(self, interaction: discord.Interaction):
        await interaction.response.send_message(EnterUserIDModal(interactions_handler=self))

    @interaction_handler()
    async def on_enter_user_id_modal_submit(self, interaction: discord.Interaction, user_id: str):
        if not user_id.isdigit():
            raise UserInputException("Invalid user ID. Please enter a valid numeric user ID.")
        self.selected_user_id = int(user_id)
        self.selected_member = None
        self.selected_other_member = None
        self.selected_role = None
        if self.selected_action == XPActionEnums.MainAction.TRANSFER_XP:
            embed = get_transfer_xp_to_member_embed()
            view = get_transfer_xp_to_member_view(interaction_handler=self)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            await self.refresh_message(feedback="Awaiting other member selection...")
        else:
            await interaction.response.defer()
            await self.refresh_message()
            try:
                await interaction.delete_original_response()
            except Exception as e:
                self.logger.debug(f"Failed to delete target member selection message: {e}")

    @interaction_handler()
    async def on_target_role_select(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_member = None
        self.selected_user_id = None
        self.selected_other_member = None
        self.selected_role = self.guild.get_role(int(interaction.data["values"][0]))
        await self.refresh_message()
        try:
            await interaction.delete_original_response()
        except Exception as e:
            self.logger.debug(f"Failed to delete target member selection message: {e}")

    @interaction_handler()
    async def on_other_target_member_select(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_other_member = await self.guild.fetch_member(int(interaction.data["values"][0]))
        self.selected_role = None
        await self.refresh_message()

    @interaction_handler()
    async def on_restart(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.selected_action = None
        self.selected_target_type = None
        self.selected_member = None
        self.selected_user_id = None
        self.selected_other_member = None
        self.selected_role = None
        self.xp_amount = 0
        embed, view = self.get_embed_and_view()
        await interaction.edit_original_response(embed=embed, view=view)
        await self.refresh_message()

    @interaction_handler()
    async def on_submit(self, interaction: discord.Interaction):
        if self.selected_action in [XPActionEnums.MainAction.AWARD_XP,
                                    XPActionEnums.MainAction.TAKE_AWAY_XP]:
            await interaction.response.send_modal(EnterXPAmountModal(interactions_handler=self))
        else:
            await self._get_confirmation_and_commit_xp_actions(interaction=interaction)

    @interaction_handler()
    async def on_enter_xp_amount_modal_submit(self, interaction: discord.Interaction, amount: str):
        if not amount.isdigit():
            raise UserInputException("Invalid XP amount. Please enter a valid numeric value.")
        self.xp_amount = int(amount)
        await self._get_confirmation_and_commit_xp_actions(interaction=interaction)

    async def _get_confirmation_and_commit_xp_actions(self, interaction: discord.Interaction):
        if self.selected_action == XPActionEnums.MainAction.RESET_XP:
            await interaction.response.send_modal(ConfirmationModal(callback=self.on_action_confirmation_modal_submit,
                                                                    custom_label="This action could be irreversible"))
        else:
            await self._construct_and_add_xp_actions(interaction=interaction)

    @interaction_handler()
    async def on_action_confirmation_modal_submit(self, interaction: discord.Interaction):
        await self._construct_and_add_xp_actions(interaction=interaction)

    async def _construct_and_add_xp_actions(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self._refresh_message_and_log_summary()
        guild_xp = await self.guild_user_xp_component.get_guild_xp(guild_id=self.guild.id)
        if self.selected_target_type in [XPActionEnums.ActionTargetType.ROLE,
                                         XPActionEnums.ActionTargetType.EVERYONE]:
            if not self.guild.chunked:
                await self.guild.chunk()
        xp_actions = []
        if self.selected_action == XPActionEnums.MainAction.AWARD_XP:
            if self.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
                xp_actions.append(XPAction(guild_id=self.guild.id,
                                           member_id=self.selected_user_id or self.selected_member.id,
                                           username=f"{self.selected_user_id or self.selected_member}",
                                           xp_offset=self.xp_amount))
            elif self.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
                for member in self.selected_role.members:
                    if not member.bot:
                        xp_actions.append(XPAction(guild_id=self.guild.id,
                                                   member_id=member.id,
                                                   username=str(member),
                                                   xp_offset=self.xp_amount))
            elif self.selected_target_type == XPActionEnums.ActionTargetType.EVERYONE:
                for member in self.guild.members:
                    if not member.bot:
                        xp_actions.append(XPAction(guild_id=self.guild.id,
                                                   member_id=member.id,
                                                   username=str(member),
                                                   xp_offset=self.xp_amount))
        elif self.selected_action == XPActionEnums.MainAction.TAKE_AWAY_XP:
            if self.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
                xp_actions.append(XPAction(guild_id=self.guild.id,
                                           member_id=self.selected_user_id or self.selected_member.id,
                                           username=f"{self.selected_user_id or self.selected_member}",
                                           xp_offset=-self.xp_amount))
            elif self.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
                for member in self.selected_role.members:
                    if not member.bot:
                        xp_actions.append(XPAction(guild_id=self.guild.id,
                                                   member_id=member.id,
                                                   username=str(member),
                                                   xp_offset=-self.xp_amount))
            elif self.selected_target_type == XPActionEnums.ActionTargetType.EVERYONE:
                for member in self.guild.members:
                    if not member.bot:
                        xp_actions.append(XPAction(guild_id=self.guild.id,
                                                   member_id=member.id,
                                                   username=str(member),
                                                   xp_offset=-self.xp_amount))
        elif self.selected_action == XPActionEnums.MainAction.TRANSFER_XP:
            if not (member_xp := guild_xp.get_xp_for(self.selected_user_id or self.selected_member.id)):
                member_xp = guild_xp.initiate_member_xp(user_id=self.selected_user_id or self.selected_member.id,
                                                        user_username=f"{self.selected_member
                                                                         or f'({self.selected_user_id})'}")
            xp_actions.append(XPAction(guild_id=self.guild.id,
                                       member_id=self.selected_user_id or self.selected_member.id,
                                       username=f"{self.selected_user_id or self.selected_member}",
                                       xp_offset=-member_xp.xp))  # noqa
            xp_actions.append(XPAction(guild_id=self.guild.id,
                                       member_id=self.selected_other_member.id,
                                       username=str(self.selected_other_member),
                                       xp_offset=member_xp.xp))
        elif self.selected_action == XPActionEnums.MainAction.RESET_XP:
            if self.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
                xp_actions.append(XPAction(guild_id=self.guild.id,
                                           member_id=self.selected_user_id or self.selected_member.id,
                                           username=f"{self.selected_user_id or self.selected_member}",
                                           reset=True))
            elif self.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
                for member in self.selected_role.members:
                    if not member.bot:
                        xp_actions.append(XPAction(guild_id=self.guild.id,
                                                   member_id=member.id,
                                                   username=str(member),
                                                   reset=True))
            elif self.selected_target_type == XPActionEnums.ActionTargetType.EVERYONE:
                for member in self.guild.members:
                    if not member.bot:
                        xp_actions.append(XPAction(guild_id=self.guild.id,
                                                   member_id=member.id,
                                                   username=str(member),
                                                   reset=True))
        else:
            raise ValueError(f"Action not recognized: {self.selected_action}")
        for xp_action in xp_actions:
            await xp_service.add_xp_action(guild_id=xp_action.guild_id,
                                           user_id=xp_action.member_id,
                                           user_username=xp_action.username,
                                           xp_offset=xp_action.xp_offset,
                                           reset=xp_action.reset)

    async def _refresh_message_and_log_summary(self):
        summary_text = self._generate_action_summary_text()
        view = XPTransferSummaryLayout(interactions_handler=self, summary_text=summary_text)
        await GuildLogger(guild=self.guild).log_event(event=GuildLogEvent.GENERAL,
                                                      event_message=f"XP Transfer action performing:\n{summary_text}",
                                                      member=self.original_user)
        await self.source_interaction.edit_original_response(view=view)

    async def refresh_message(self, feedback: str | None = None, *args, **kwargs):
        _, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=None, view=view)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[None, discord.ui.LayoutView]:
        view = XPTransferLayout(interactions_handler=self, feedback_message=feedback)
        return None, view

    def _generate_action_summary_text(self) -> str:
        if self.selected_target_type == XPActionEnums.ActionTargetType.EVERYONE:
            target = 'everyone'
        elif self.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
            target = self.selected_role.mention
        elif self.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
            target = self.selected_member.mention \
                if self.selected_member else \
                self.selected_user_id
        elif not self.selected_action == XPActionEnums.MainAction.TRANSFER_XP:
            raise ValueError(f"Target type not recognized: {self.selected_target_type}")
        else:
            target = None

        if self.selected_action == XPActionEnums.MainAction.AWARD_XP:
            summary_text = (f"### - Action: Award XP\n"
                            f"### - Target: {target}\n"
                            f"### - Amount: {self.xp_amount}")
        elif self.selected_action == XPActionEnums.MainAction.TAKE_AWAY_XP:
            summary_text = (f"### - Action: Take away XP\n"
                            f"### - Target: {target}\n"
                            f"### - Amount: {self.xp_amount}")
        elif self.selected_action == XPActionEnums.MainAction.TRANSFER_XP:
            summary_text = (f"### - Action: Transfer XP\n"
                            f"### - From: {self.selected_member.mention
                                           if self.selected_member else
                                           self.selected_user_id}\n"
                            f"### - To: {self.selected_other_member.mention}\n")
        elif self.selected_action == XPActionEnums.MainAction.RESET_XP:
            summary_text = (f"### - Action: Reset XP\n"
                            f"### - Target: {target}")
        else:
            raise ValueError(f"Action not recognized: {self.selected_action}")

        return summary_text
