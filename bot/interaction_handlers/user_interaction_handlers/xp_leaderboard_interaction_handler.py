import discord

from bot.interaction_handlers import NavigationInteractionHandler
from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.decorators import interaction_handler
from bot.utils.embed_factory.xp_user_embeds import get_xp_leaderboard_embed
from bot.utils.view_factory.general_views import get_navigation_view
from models.dto.cachables import CachedGuildXP


class XPLeaderboardInteractionHandler(UserInteractionHandler, NavigationInteractionHandler):
    VIEW_NAME = "XP leaderboard"
    PAGE_SIZE = 10

    def __init__(self, guild_xp: CachedGuildXP, page: int = 1, show_decays: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.guild_xp: CachedGuildXP = guild_xp
        self._page: int = page
        self._show_decays: bool = show_decays

    @interaction_handler()
    async def next_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.offset_page(1)
        await self.refresh_message()

    @interaction_handler()
    async def previous_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.offset_page(-1)
        await self.refresh_message()

    def offset_page(self, offset: int) -> None:
        self._page += offset
        if self._page < 1:
            self._page = self.page_count
        elif self._page > self.page_count:
            self._page = 1

    async def refresh_message(self, no_view: bool = False, *args, **kwargs) -> None:
        embed, view = self.get_embed_and_view()
        await self.source_interaction.edit_original_response(embed=embed, view=view if not no_view else None)

    def get_embed_and_view(self, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        embed = get_xp_leaderboard_embed(guild=self.guild,
                                         author=self.source_interaction.user,
                                         guild_xp=self.guild_xp,
                                         page=self._page,
                                         page_count=self.page_count,
                                         page_size=self.PAGE_SIZE,
                                         show_decays=self._show_decays)
        view = get_navigation_view(interaction_handler=self,
                                   page=self._page,
                                   page_count=self.page_count,
                                   add_close_button=True)
        return embed, view

    async def on_timeout(self):
        self._page = 1
        await super().on_timeout()

    @property
    def page_count(self) -> int:
        return ((self.guild_xp.member_count - 1) // self.PAGE_SIZE + 1) or 1
