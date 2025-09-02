from typing import TYPE_CHECKING

from discord import ButtonStyle
from discord.ui import View, Button

from clients import emojis

if TYPE_CHECKING:
    from bot.interaction_handlers.user_interaction_handlers.animanga_profile_interaction_handler import \
        AnimangaProfileInteractionHandler
    from bot.interaction_handlers.user_interaction_handlers.anime_info_interaction_handler import \
        AnimeInfoInteractionHandler
    from bot.interaction_handlers.user_interaction_handlers.manga_info_interaction_handler import \
        MangaInfoInteractionHandler


def get_animanga_profile_view(interaction_handler: 'AnimangaProfileInteractionHandler',
                              add_analysis_button: bool) -> View:
    """
    Creates a view for the anime/manga profile navigation.
    Args:
        interaction_handler (AnimangaProfileInteractionHandler): The interaction handler for the view.
        add_analysis_button (bool): Whether to add the analysis button.

    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    anime_list_button = Button(label="Anime", emoji=emojis.general.tv, style=ButtonStyle.blurple,
                               custom_id="anime_list", row=0)
    anime_list_button.callback = interaction_handler.go_to_anime_list
    view.add_item(anime_list_button)

    manga_list_button = Button(label="Manga", emoji=emojis.general.book, style=ButtonStyle.blurple,
                               custom_id="manga_list", row=0)
    manga_list_button.callback = interaction_handler.go_to_manga_list
    view.add_item(manga_list_button)

    favorites_button = Button(label="Favorites", emoji=emojis.general.favorite, style=ButtonStyle.blurple,
                              custom_id="animanga-favorites", row=1 if add_analysis_button else 0)
    favorites_button.callback = interaction_handler.go_to_favorites
    view.add_item(favorites_button)

    if add_analysis_button:
        analysis_button = Button(label="Analysis", emoji=emojis.general.pie_chart, style=ButtonStyle.green,
                                 custom_id="animanga-analysis", row=1)
        analysis_button.callback = interaction_handler.go_to_analysis
        view.add_item(analysis_button)

    if interaction_handler.interactions_restricted:
        edit_button = Button(label="Unlock", emoji=emojis.action.unlock, style=ButtonStyle.grey,
                             custom_id="animanga-profile-unlock", row=2)
        edit_button.callback = interaction_handler.unlock
        view.add_item(edit_button)

    close_button = Button(label="Close", emoji=emojis.action.delete, style=ButtonStyle.red,
                          custom_id="close-embed", row=2)
    close_button.callback = interaction_handler.close_embed
    view.add_item(close_button)

    view.on_timeout = interaction_handler.on_timeout
    return view


def get_animanga_info_view(interaction_handler: 'AnimeInfoInteractionHandler | MangaInfoInteractionHandler') -> View:
    """
    Creates a view for the anime/manga info navigation.
    Args:
        interaction_handler (AnimeInfoInteractionHandler | MangaInfoInteractionHandler):
            The interaction handler for the view.

    Returns:
        View: The created view.
    """
    view = View(timeout=300)

    back_button = Button(label="Back to search", style=ButtonStyle.gray,
                         custom_id="back-to-search", emoji=emojis.navigation.back)
    back_button.callback = interaction_handler.go_to_search
    view.add_item(back_button)

    if interaction_handler.synopsis_expandable():
        expand_button = Button(label="Expand", emoji=emojis.action.scroll_down,
                               style=ButtonStyle.blurple, custom_id="expand-synopsis")
        expand_button.callback = interaction_handler.expand_synopsis
        view.add_item(expand_button)

    close_button = Button(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close")
    close_button.callback = interaction_handler.close_embed
    view.add_item(close_button)

    view.on_timeout = interaction_handler.on_timeout
    return view
