from disnake import SelectOption, ButtonStyle
from disnake.ui import View, Select as SelectView, Button as ButtonView

from globals_.constants import UserCommandSection, LETTER_EMOTES_COMMANDS, AdminCommandSection, \
    LETTER_EMOTES_ADMIN_COMMANDS, MusicCommandSection, LETTER_EMOTES_MUSIC_COMMANDS, EMOJI_NUMBER_MAP


def get_main_help_views(command_type_section):
    view = View(timeout=300)
    letter_emotes = LETTER_EMOTES_COMMANDS if command_type_section == UserCommandSection else \
        LETTER_EMOTES_ADMIN_COMMANDS if command_type_section == AdminCommandSection else \
        LETTER_EMOTES_MUSIC_COMMANDS if command_type_section == MusicCommandSection else {}
    options = [SelectOption(label=section, value=section, emoji=letter_emotes.get(section[0].lower()))
               for section in command_type_section.as_list()]
    view.add_item(SelectView(options=options))
    view.add_item(ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close"))
    return view


def get_section_help_views():
    view = View(timeout=300)
    view.add_item(ButtonView(label="Go back", emoji='⬅', style=ButtonStyle.gray, custom_id="back"))
    return view


def get_close_embed_view():
    view = View(timeout=300)
    view.add_item(ButtonView(label="Close embed", emoji='🗑', style=ButtonStyle.gray, custom_id="close"))
    return view


def get_pagination_views(page, page_count, add_close_button=True, add_back_button=False):
    view = View(timeout=300)
    if page != 1:
        view.add_item(ButtonView(label="Previous", emoji='⬅', style=ButtonStyle.blurple, custom_id="previous"))
    if page < page_count:
        view.add_item(ButtonView(label="Next", emoji='➡', style=ButtonStyle.blurple, custom_id="next"))
    if add_close_button:
        view.add_item(ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close"))
    if add_back_button:
        view.add_item(ButtonView(label="Back", emoji='❌', style=ButtonStyle.gray, custom_id="back"))
    return view


def get_numbered_list_views(list_items, add_close_button=True):
    view = View(timeout=300)
    options = [SelectOption(label=item, value=str(i), emoji=list(EMOJI_NUMBER_MAP.keys())[i])
               for i, item in enumerate(list_items)]
    view.add_item(SelectView(options=options))
    if add_close_button:
        view.add_item(ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close"))
    return view


def get_mal_info_views(add_expand_button, add_back_button=False):
    view = View(timeout=300)
    if add_back_button:
        view.add_item(ButtonView(label="Back to search", emoji='⬅', style=ButtonStyle.gray, custom_id="back"))
    if add_expand_button:
        view.add_item(ButtonView(label="Expand", emoji='📜', style=ButtonStyle.blurple, custom_id="expand"))
    view.add_item(ButtonView(label="Close", emoji='🗑', style=ButtonStyle.red, custom_id="close"))
    return view


def get_mal_al_profile_views(add_unlock):
    view = View(timeout=300)
    view.add_item(ButtonView(label="Anime", emoji='📺', style=ButtonStyle.blurple, custom_id="anime_list"))
    view.add_item(ButtonView(label="Manga", emoji='📚', style=ButtonStyle.blurple, custom_id="manga_list"))
    view.add_item(ButtonView(label="Favs", emoji='⭐', style=ButtonStyle.blurple, custom_id="favorites"))
    if add_unlock:
        view.add_item(ButtonView(label="Unlock", emoji='🔓', style=ButtonStyle.gray, custom_id="unlock", row=2))
    view.add_item(ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close", row=2))
    return view


def get_al_profile_views(add_unlock):
    view = View(timeout=300)
    view.add_item(ButtonView(label="Anime", emoji='📺', style=ButtonStyle.blurple, custom_id="anime_list"))
    view.add_item(ButtonView(label="Manga", emoji='📚', style=ButtonStyle.blurple, custom_id="manga_list"))
    view.add_item(ButtonView(label="Favs", emoji='⭐', style=ButtonStyle.blurple, custom_id="favorites"))
    view.add_item(ButtonView(label="Analysis", emoji='🧮', style=ButtonStyle.green, custom_id="analysis", row=2))
    if add_unlock:
        view.add_item(ButtonView(label="Unlock", emoji='🔓', style=ButtonStyle.gray, custom_id="unlock", row=2))
    view.add_item(ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close", row=2))
    return view


def get_back_view():
    view = View(timeout=300)
    view.add_item(ButtonView(label="Back", emoji='❌', style=ButtonStyle.gray, custom_id="back"))
    return view


def get_history_embed_views(page, page_count, list_items):
    view = View(timeout=300)
    if page != 1:
        view.add_item(ButtonView(label="Previous", emoji='⬅', style=ButtonStyle.blurple, custom_id="previous"))
    if page < page_count:
        view.add_item(ButtonView(label="Next", emoji='➡', style=ButtonStyle.blurple, custom_id="next"))
    view.add_item(ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close"))
    options = [SelectOption(label=item['title'], value=str(i)) for i, item in enumerate(list_items)]
    view.add_item(SelectView(options=options))
    return view


def get_menu_confirmation_view(label):
    view = View(timeout=300)
    options = [SelectOption(label=label, value="confirm"), ]
    view.add_item(SelectView(options=options))
    return view
