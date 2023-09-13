from actions import send_message
from user_interactions.user_interactions.help_menu_interactions_handler import HelpMenuInteractionsHandler
from utils.embed_factory import quick_embed
from globals_.clients import discord_client
from globals_.constants import Colour, BOT_OWNER_ID, SUPPORT_SERVER_INVITE
from utils.decorators import slash_command
from slashes.user_slashes.base_user_slashes import UserSlashes


class OtherUserSlashes(UserSlashes):

    @slash_command
    async def feedback(self, feedback: str):
        """
        /feedback
        Send feedback to the bot owner
        """

        if not await self.preprocess_and_validate():
            return

        await self.interaction.response.send_message(
            embed=quick_embed("Thank you for the feedback 💘. "
                              "If this is a bug report or a suggestion,"
                              " we will send you a message once we fix or implement it.",
                              emoji='',
                              color=Colour.SUCCESS,
                              bold=False),
            ephemeral=True
        )

        await send_message(f"Received general feedback",
                           embed=quick_embed(feedback, bold=False, emoji=None,
                                             fields_values={
                                                 "User": f"**{self.user}** ({self.user.id})"
                                             }),
                           channel=discord_client.get_user(BOT_OWNER_ID))

    @slash_command
    async def support(self):
        """
        /support
        Get the support server invite link
        """

        if not await self.preprocess_and_validate():
            return

        await self.interaction.response.send_message(
            embed=quick_embed(f"[Click here]({SUPPORT_SERVER_INVITE}) to join the support server.",
                              emoji='',
                              color=Colour.SUCCESS,
                              bold=False),
            ephemeral=True
        )

    @slash_command
    async def help(self, menu: str = None, make_visible: bool = False):
        """
        /help
        Show the help menu
        """

        if not await self.preprocess_and_validate():
            return

        interactions_handler = HelpMenuInteractionsHandler(interaction=self.interaction,
                                                           selected_menu=menu)

        embed, views = interactions_handler.get_embed_and_views()

        await self.interaction.response.send_message(embed=embed,
                                                     view=views,
                                                     ephemeral=self.send_as_ephemeral(make_visible=make_visible))
