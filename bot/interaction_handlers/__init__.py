"""
Base class and mixins for handling view-based/component interactions.
"""
from types import coroutine

import discord

from bot.utils.embed_factory.general_embeds import get_generic_embed
from common.app_logger import AppLogger
from bot.utils.decorators import interaction_handler
from common.exceptions import InvalidInteractionException
from constants import AppLogCategory, Colour, CommandContext
from models.dto.cachables import CachedGuildSettings


class BaseInteractionHandler:
    VIEW_NAME = "View"  # should be overridden in subclasses

    def __init__(self, source_interaction: discord.Interaction, context: str,
                 guild_settings: 'None | GuildSettings' = None):
        self.source_interaction: discord.Interaction = source_interaction
        self.guild: discord.Guild | None = source_interaction.guild if context == CommandContext.GUILD else None
        self.channel: discord.TextChannel | discord.DMChannel = source_interaction.channel
        self.original_user: discord.User = source_interaction.user
        self.original_member: discord.Member | None = self.original_user \
            if context == CommandContext.GUILD and self.guild else None
        self.interactions_restricted = False  # should be overridden when needed
        self._is_closed = False
        self._embed_color: hex = Colour.PRIMARY_ACCENT
        self.context: str = context  # CommandContext
        self.guild_settings: CachedGuildSettings = guild_settings
        self.logger = AppLogger(component=self.__class__.__name__)

    def __new__(cls, *args, **kwargs):
        if cls is BaseInteractionHandler:
            raise TypeError("BaseInteractionHandler cannot be instantiated directly. "
                            "Please use a subclass instead.")
        return super().__new__(cls)

    async def preprocess_and_validate(self,
                                      interaction: discord.Interaction,
                                      handler: coroutine):
        """
        Preprocesses and validates the interaction before passing it to the actual handler.
        Args:
            interaction (discord.Interaction): The interaction to preprocess and validate.
            handler (coroutine): The actual handler expected to be called after validation.
        """
        if self.interactions_restricted and interaction.user.id != self.original_user.id:
            raise InvalidInteractionException("Only the original user can interact with this view.")

        await self.log_interaction(handler=handler)

    async def log_interaction(self, handler: coroutine):
        """
        Logs the interaction details.
        Args:
            handler (coroutine): The actual handler being called. Needed to log the handler name.
        """
        self.logger.info(f"Interaction handler `{handler.__qualname__}` "
                         f"called by user: {self.original_user} ({self.original_user.id})."
                         + (f" Guild: {self.guild.name}" if self.guild else "") +
                         f" Channel: {f'#{self.channel}' if self.channel else 'DM'}",
                         extras={
                             "interaction_data": self.source_interaction.data,
                             "guild_id": self.guild.id if self.guild else None,
                             "channel_id": self.channel.id if self.channel else None,
                             "user_id": self.original_user.id
                         },
                         category=AppLogCategory.BOT_INTERACTION_CALLED)

    async def on_timeout(self):
        """
        Handles the timeout of the view. All views using an interaction handler are expected to have their callback
        for timeout set to this method or an overridden version of this method.
        """
        try:
            await self.refresh_message(no_view=True)
        except:
            pass

    @interaction_handler()
    async def close_embed(self, interaction: discord.Interaction):
        """
        Generic handler for a close embed button.
        Args:
            interaction (discord.Interaction): The received interaction.
        """
        await interaction.response.defer()
        await self._close_embed()

    async def _close_embed(self) -> None:
        await self.source_interaction.edit_original_response(
            embed=get_generic_embed(description=f"{self.VIEW_NAME} closed",
                                    color=self._embed_color),
            view=None
        )
        self._is_closed = True

    @interaction_handler()
    async def delete_original_response(self, interaction: discord.Interaction):
        """
        Generic handler for any view that needs to delete the original response message.
        Args:
            interaction (discord.Interaction): The received interaction.
        """
        await interaction.response.defer()
        try:
            await interaction.delete_original_response()
        except:
            pass

    async def refresh_message(self, feedback: str | None = None, no_view: bool = False, *args, **kwargs) -> None:
        raise NotImplementedError

    def get_embed_and_view(self, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        raise NotImplementedError


class NumberedListInteractionHandler:

    @interaction_handler()
    async def select_item(self, interaction: discord.Interaction):
        raise NotImplementedError


class NavigationInteractionHandler:

    @interaction_handler()
    async def next_page(self, interaction: discord.Interaction):
        raise NotImplementedError

    @interaction_handler()
    async def previous_page(self, interaction: discord.Interaction):
        raise NotImplementedError

    @interaction_handler()
    async def go_back(self, interaction: discord.Interaction):
        raise NotImplementedError

    def offset_page(self, offset: int) -> None:
        raise NotImplementedError

    @property
    def page_count(self) -> int:
        raise NotImplementedError
