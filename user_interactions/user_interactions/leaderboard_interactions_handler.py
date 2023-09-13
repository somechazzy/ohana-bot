import discord

from utils.embed_factory import quick_embed, make_leaderboard_embed
from utils.helpers import get_pagination_views
from globals_.constants import Colour
from utils.decorators import interaction_handler
from user_interactions.user_interactions.base_users_interactions import UserInteractionsHandler


class LeaderboardInteractionsHandler(UserInteractionsHandler):

    def __init__(self, source_interaction, members_xp, page=1):
        super().__init__(source_interaction=source_interaction)
        self._members_xp = members_xp
        self._page = page

    @interaction_handler
    async def handle_cancel(self, inter: discord.Interaction):
        if self.source_interaction.user.id != inter.user.id:
            return await inter.response.defer()
        await inter.response.defer()
        await self.source_interaction.edit_original_response(embed=quick_embed("Leaderboard closed.",
                                                                               color=Colour.PRIMARY_ACCENT,
                                                                               bold=False),
                                                             view=None)

    @interaction_handler
    async def handle_next(self, inter: discord.Interaction):
        await inter.response.defer()

        if self._page < len(self._members_xp) // 10 + 1:
            self._page += 1
        else:
            self._page = 1

        await self.refresh_message()

    @interaction_handler
    async def handle_previous(self, inter: discord.Interaction):
        await inter.response.defer()

        if self._page > 1:
            self._page -= 1
        else:
            self._page = len(self._members_xp) // 10 + 1

        await self.refresh_message()

    async def refresh_message(self, no_views=False):
        embed, views = self.get_embed_and_views()
        await self.source_interaction.edit_original_response(embed=embed, view=views if not no_views else None)

    def get_embed_and_views(self):
        embed = make_leaderboard_embed(members_xp=self._members_xp,
                                       requested_by=self.source_interaction.user,
                                       page=self._page)
        views = get_pagination_views(page=self._page,
                                     page_count=len(self._members_xp) // 10 + 1,
                                     interactions_handler=self,
                                     add_close_button=True)

        return embed, views

    async def on_timeout(self):
        await self.refresh_message(no_views=True)
