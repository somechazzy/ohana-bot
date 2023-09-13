from typing import Iterable

from discord import SelectOption, ButtonStyle
from discord.ui import View, Select as SelectView, Button as ButtonView, RoleSelect, ChannelSelect, UserSelect

from globals_ import shared_memory
from globals_.clients import discord_client
from globals_.constants import NUMBER_EMOJI_MAP, RoleMenuType, RoleMenuMode, PLAYER_ACTION_CUSTOM_EMOJI_MAP, \
    PlayerAction, GeneralButtonEmoji
from . import shorten_text_if_above_x_characters as shorten


def get_pagination_views(page, page_count, interactions_handler, add_close_button=True, add_back_button=False):
    view = View(timeout=300)
    if page != 1:
        previous_button = ButtonView(label="Previous", style=ButtonStyle.blurple, custom_id="previous",
                                     emoji=discord_client.get_emoji(GeneralButtonEmoji.PREVIOUS))
        previous_button.callback = interactions_handler.handle_previous
        view.add_item(previous_button)
    if page < page_count:
        next_button = ButtonView(label="Next", style=ButtonStyle.blurple, custom_id="next",
                                 emoji=discord_client.get_emoji(GeneralButtonEmoji.NEXT))
        next_button.callback = interactions_handler.handle_next
        view.add_item(next_button)
    if add_close_button:
        close_button = ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close")
        close_button.callback = interactions_handler.handle_cancel
        view.add_item(close_button)
    if add_back_button:
        back_button = ButtonView(label="Back", emoji=discord_client.get_emoji(GeneralButtonEmoji.GO_BACK),
                                 style=ButtonStyle.gray, custom_id="back")
        back_button.callback = interactions_handler.handle_go_back
        view.add_item(back_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_numbered_list_views(list_items, interactions_handler, add_close_button=True):
    view = View(timeout=300)
    options = [SelectOption(label=shorten(f"{i+1}. {item}", 90), value=str(i), emoji=NUMBER_EMOJI_MAP[i+1])
               for i, item in enumerate(list_items)]
    select_view = SelectView(options=options)
    select_view.callback = interactions_handler.handle_selection
    view.add_item(select_view)
    if add_close_button:
        close_button = ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close")
        close_button.callback = interactions_handler.handle_cancel
        view.add_item(close_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def make_mal_info_views(add_expand_button, interactions_handler):
    view = View(timeout=300)

    back_button = ButtonView(label="Back to search", style=ButtonStyle.gray, custom_id="back",
                             emoji=discord_client.get_emoji(GeneralButtonEmoji.GO_BACK))
    back_button.callback = interactions_handler.handle_back_to_search
    view.add_item(back_button)

    if add_expand_button:
        expand_button = ButtonView(label="Expand", emoji='📜', style=ButtonStyle.blurple, custom_id="expand")
        expand_button.callback = interactions_handler.handle_expand_synopsis
        view.add_item(expand_button)

    close_button = ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close")
    close_button.callback = interactions_handler.handle_cancel
    view.add_item(close_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_mal_profile_views(add_unlock, interactions_handler):
    view = View(timeout=300)

    anime_list_button = ButtonView(label="Anime", emoji='📺', style=ButtonStyle.blurple, custom_id="anime_list")
    anime_list_button.callback = interactions_handler.handle_anime_list
    view.add_item(anime_list_button)

    manga_list_button = ButtonView(label="Manga", emoji='📚', style=ButtonStyle.blurple, custom_id="manga_list")
    manga_list_button.callback = interactions_handler.handle_manga_list
    view.add_item(manga_list_button)

    favorites_button = ButtonView(label="Favs", emoji='⭐', style=ButtonStyle.blurple, custom_id="favorites")
    favorites_button.callback = interactions_handler.handle_favorites
    view.add_item(favorites_button)

    if add_unlock:
        unlock_button = ButtonView(label="Unlock", emoji='🔓', style=ButtonStyle.gray, custom_id="unlock", row=1)
        unlock_button.callback = interactions_handler.handle_unlock
        view.add_item(unlock_button)

    close_button = ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close", row=1)
    close_button.callback = interactions_handler.handle_cancel
    view.add_item(close_button)

    view.on_timeout = interactions_handler.on_timeout if interactions_handler else None
    return view


def get_al_profile_views(add_unlock, interactions_handler):
    view = View(timeout=300)

    anime_list_button = ButtonView(label="Anime", emoji='📺', style=ButtonStyle.blurple, custom_id="anime_list")
    anime_list_button.callback = interactions_handler.handle_anime_list
    view.add_item(anime_list_button)

    manga_list_button = ButtonView(label="Manga", emoji='📚', style=ButtonStyle.blurple, custom_id="manga_list")
    manga_list_button.callback = interactions_handler.handle_manga_list
    view.add_item(manga_list_button)

    favorites_button = ButtonView(label="Favs", emoji='⭐', style=ButtonStyle.blurple, custom_id="favorites")
    favorites_button.callback = interactions_handler.handle_favorites
    view.add_item(favorites_button)

    analysis_button = ButtonView(label="Analysis", emoji='🧮', style=ButtonStyle.green, custom_id="analysis", row=1)
    analysis_button.callback = interactions_handler.handle_analysis
    view.add_item(analysis_button)

    if add_unlock:
        unlock_button = ButtonView(label="Unlock", emoji='🔓', style=ButtonStyle.gray, custom_id="unlock", row=1)
        unlock_button.callback = interactions_handler.handle_unlock
        view.add_item(unlock_button)

    close_button = ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close", row=1)
    close_button.callback = interactions_handler.handle_cancel
    view.add_item(close_button)

    view.on_timeout = interactions_handler.on_timeout if interactions_handler else None
    return view


def get_back_view(interactions_handler, add_close_button=False):
    view = View(timeout=300)

    back_button = ButtonView(label="Back", emoji=discord_client.get_emoji(GeneralButtonEmoji.GO_BACK),
                             style=ButtonStyle.gray, custom_id="back")
    back_button.callback = interactions_handler.handle_go_back
    view.add_item(back_button)

    if add_close_button:
        close_button = ButtonView(label="Close", emoji='🗑', style=ButtonStyle.red, custom_id="close")
        close_button.callback = interactions_handler.handle_cancel
        view.add_item(close_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_music_library_views(page, page_count, playlists, interactions_handler):
    view = View(timeout=600)
    starting_index = (page - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(playlists)) \
        else len(playlists)
    if page != 1:
        previous_button = ButtonView(label="Previous Page", style=ButtonStyle.gray, custom_id="previous",
                                     emoji=discord_client.get_emoji(GeneralButtonEmoji.PREVIOUS))
        previous_button.callback = interactions_handler.handle_library_previous_page
        view.add_item(previous_button)
    if page < page_count:
        next_button = ButtonView(label="Next Page", style=ButtonStyle.gray, custom_id="next",
                                 emoji=discord_client.get_emoji(GeneralButtonEmoji.NEXT))
        next_button.callback = interactions_handler.handle_library_next_page
        view.add_item(next_button)
    create_button = ButtonView(label="Create Playlist", style=ButtonStyle.green, custom_id="create",
                               emoji=discord_client.get_emoji(GeneralButtonEmoji.ADD))
    create_button.callback = interactions_handler.handle_create_playlist
    view.add_item(create_button)

    options = [SelectOption(label=shorten(f"{i+(10*(page-1))}. {playlist.name}", 90), value=str(i+(10*(page-1))))
               for i, playlist in enumerate(playlists[starting_index:final_index], 1)]
    playlist_select_view = SelectView(options=options, placeholder="Select a playlist to manage")
    playlist_select_view.callback = interactions_handler.handle_library_playlist_select
    view.add_item(playlist_select_view)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_playlist_views(page, page_count, interactions_handler, add_back_button=False, show_more_button=True,
                       is_playlist_empty=False, track_index_title_map=None):
    view = View(timeout=600)

    if track_index_title_map:
        track_select_view = SelectView(options=[SelectOption(label=shorten(f"{i+1}. {track_title}", 90), value=str(i))
                                                for i, track_title in track_index_title_map.items()],
                                       placeholder="Select a track to queue")
        track_select_view.callback = interactions_handler.handle_playlist_track_select
        view.add_item(track_select_view)

    play_button = ButtonView(label="Play", style=ButtonStyle.green, custom_id="play",
                             emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.RESUME]))
    play_button.callback = interactions_handler.handle_playlist_play
    view.add_item(play_button)

    if page != 1:
        previous_page = ButtonView(
            label="Previous Page", style=ButtonStyle.gray, custom_id="previous",
            emoji=discord_client.get_emoji(GeneralButtonEmoji.PREVIOUS)
        )
        previous_page.callback = interactions_handler.handle_playlist_previous_page
        view.add_item(previous_page)

    if page < page_count:
        next_page = ButtonView(
            label="Next Page", style=ButtonStyle.gray, custom_id="next",
            emoji=discord_client.get_emoji(GeneralButtonEmoji.NEXT)
        )
        next_page.callback = interactions_handler.handle_playlist_next_page
        view.add_item(next_page)

    if add_back_button:
        back_button = ButtonView(label="Go back", emoji=discord_client.get_emoji(GeneralButtonEmoji.GO_BACK),
                                 style=ButtonStyle.gray, custom_id="back")
        back_button.callback = interactions_handler.handle_playlist_go_back
        view.add_item(back_button)

    add_track_button = ButtonView(label="Add Track", style=ButtonStyle.blurple, custom_id="add-track", row=2,
                                  emoji=discord_client.get_emoji(GeneralButtonEmoji.ADD))
    add_track_button.callback = interactions_handler.handle_playlist_add_track
    view.add_item(add_track_button)

    if show_more_button:
        more_button = ButtonView(label="•••", style=ButtonStyle.blurple, custom_id="more", row=2)
        more_button.callback = interactions_handler.handle_playlist_show_all_buttons
        view.add_item(more_button)

    else:
        if not is_playlist_empty:
            remove_track_button = ButtonView(
                label="Remove Track", style=ButtonStyle.grey, custom_id="remove-track", row=2,
                emoji=discord_client.get_emoji(GeneralButtonEmoji.REMOVE)
            )
            remove_track_button.callback = interactions_handler.handle_playlist_remove_track
            view.add_item(remove_track_button)

            move_track_button = ButtonView(
                label="Move Track", style=ButtonStyle.grey, custom_id="move-track", row=2,
                emoji=discord_client.get_emoji(GeneralButtonEmoji.MOVE)
            )
            move_track_button.callback = interactions_handler.handle_playlist_move_track
            view.add_item(move_track_button)

        rename_button = ButtonView(label="Rename Playlist", style=ButtonStyle.blurple, custom_id="rename", row=3,
                                   emoji=discord_client.get_emoji(GeneralButtonEmoji.RENAME))
        rename_button.callback = interactions_handler.handle_playlist_rename
        view.add_item(rename_button)

        clone_button = ButtonView(label="Clone Playlist", style=ButtonStyle.blurple, custom_id="clone", row=3,
                                  emoji=discord_client.get_emoji(GeneralButtonEmoji.COPY))
        clone_button.callback = interactions_handler.handle_playlist_clone
        view.add_item(clone_button)

        if not is_playlist_empty:
            clear_button = ButtonView(label="Clear Playlist", style=ButtonStyle.red, custom_id="clear", row=3,
                                      emoji=discord_client.get_emoji(GeneralButtonEmoji.CLEAR))
            clear_button.callback = interactions_handler.handle_playlist_clear
            view.add_item(clear_button)

        delete_button = ButtonView(label="Delete Playlist", style=ButtonStyle.red, custom_id="delete", row=3,
                                   emoji=discord_client.get_emoji(GeneralButtonEmoji.DELETE))
        delete_button.callback = interactions_handler.handle_playlist_delete
        view.add_item(delete_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_role_menu_setup_views(interactions_handler, roles_removable=False, is_restricted=False, image_added=False):
    view = View(timeout=900)

    basic_setup_button = ButtonView(label="Basic Setup", emoji='🪄', style=ButtonStyle.blurple, custom_id="basic_setup")
    basic_setup_button.callback = interactions_handler.handle_basic_setup

    add_role_button = ButtonView(label="Add Role", emoji='➕', style=ButtonStyle.green, custom_id="add_role")
    add_role_button.callback = interactions_handler.handle_add_role

    remove_role_button = ButtonView(label="Remove Role", emoji='➖', style=ButtonStyle.red, custom_id="remove_role")
    remove_role_button.callback = interactions_handler.handle_remove_role

    change_role_mode_button = ButtonView(label="Change Role Mode", emoji='🧩', style=ButtonStyle.gray,
                                         custom_id="change_role_mode", row=2)
    change_role_mode_button.callback = interactions_handler.handle_role_menu_mode

    change_menu_type_button = ButtonView(label="Change Menu Type", emoji='🧮', style=ButtonStyle.gray,
                                         custom_id="change_menu_type", row=2)
    change_menu_type_button.callback = interactions_handler.handle_role_menu_type

    restrict_menu_button = ButtonView(label="Restrict Menu" if not is_restricted else "Un-restrict Menu", emoji='⛓',
                                      style=ButtonStyle.green, custom_id="restrict_menu", row=3)
    restrict_menu_button.callback = interactions_handler.handle_restrict_menu

    add_image_button = ButtonView(label="Add Image" if not image_added else "Change Image", emoji='🖼️',
                                  style=ButtonStyle.green, custom_id="add_image", row=3)
    add_image_button.callback = interactions_handler.handle_add_image

    view.add_item(basic_setup_button)
    view.add_item(add_role_button)
    if roles_removable:
        view.add_item(remove_role_button)

    view.add_item(change_role_mode_button)
    view.add_item(change_menu_type_button)

    view.add_item(restrict_menu_button)
    view.add_item(add_image_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_role_menu_views(roles_map, role_menu_type, role_menu_mode):
    if not roles_map:
        return None
    view = View(timeout=None)
    ordered_role_tuples = [tuple()] * len(roles_map)
    for role_id, role_details in roles_map.items():
        role_option_name = role_details['alias']
        role_emoji = role_details['emoji']
        role_rank = role_details['rank']
        ordered_role_tuples[role_rank-1] = (role_id, role_option_name, role_emoji)
    if role_menu_type == RoleMenuType.SELECT:
        remove_role_label = "Remove role" if role_menu_mode == RoleMenuMode.SINGLE else "Remove all roles"
        options = [SelectOption(label=remove_role_label, value='0', emoji='❌')]
        options.extend([SelectOption(label=role_option_name, value=str(role_id), emoji=role_emoji or None)
                        for role_id, role_option_name, role_emoji in ordered_role_tuples])
        max_selections = len(roles_map) if role_menu_mode == RoleMenuMode.MULTIPLE else 1
        view.add_item(SelectView(options=options, max_values=max_selections))
    elif role_menu_type == RoleMenuType.BUTTON:
        i = 0
        for role_id, role_option_name, role_emoji in ordered_role_tuples:
            view.add_item(ButtonView(label=role_option_name, emoji=role_emoji or None,
                                     style=ButtonStyle.blurple, custom_id=str(role_id), row=(i//5)+1))
            i += 1

    return view


def get_player_message_views(is_paused=False, is_connected=False, display_previous=False, display_next=False,
                             track_queued=False, disable_refresh_button=False):
    view = View(timeout=None)
    if is_connected:
        if track_queued:
            if is_paused:
                view.add_item(ButtonView(
                    label="Resume", style=ButtonStyle.green, custom_id="resume",
                    emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.RESUME])
                ))
            else:
                view.add_item(ButtonView(
                    label="Pause", style=ButtonStyle.gray, custom_id="pause",
                    emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.PAUSE])
                ))
        if track_queued:
            view.add_item(ButtonView(
                label="Skip", style=ButtonStyle.grey, custom_id="skip",
                emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.SKIP])
            ))
        view.add_item(ButtonView(label="Disconnect", style=ButtonStyle.red, custom_id="disconnect"))
        if track_queued:
            view.add_item(ButtonView(
                label="Shuffle", style=ButtonStyle.grey, custom_id="shuffle", row=2,
                emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.SHUFFLE])
            ))
            view.add_item(ButtonView(
                label="Loop", style=ButtonStyle.grey, custom_id="loop", row=2,
                emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.LOOP])
            ))
        if track_queued and not is_paused:
            label = "Refresh" if not disable_refresh_button else "Refresh (disabled due to spam)"
            view.add_item(ButtonView(
                label=label, style=ButtonStyle.grey, custom_id="refresh", row=2,
                emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.REFRESH]),
                disabled=disable_refresh_button
            ))
        view.add_item(ButtonView(
            label="Add to Queue..", style=ButtonStyle.green, custom_id="add_track", row=3 if track_queued else 2,
            emoji=discord_client.get_emoji(GeneralButtonEmoji.ADD)
        ))
        if track_queued:
            view.add_item(ButtonView(
                label="Add to Favorites", style=ButtonStyle.blurple, custom_id="favorite", row=3,
                emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.FAVORITE])
            ))
        view.add_item(ButtonView(
            label="Report a problem..", style=ButtonStyle.grey, custom_id="report", row=3)
        )
        view.add_item(ButtonView(
            label="My Library", style=ButtonStyle.grey, custom_id="library", row=4,
            emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.LIBRARY])
        ))
        view.add_item(ButtonView(
            label="Playback History", style=ButtonStyle.grey, custom_id="history", row=4,
            emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.HISTORY])
        ))
        if display_previous:
            view.add_item(ButtonView(
                label="Previous Page", style=ButtonStyle.grey, custom_id="previous_page", row=4,
                emoji=discord_client.get_emoji(GeneralButtonEmoji.PREVIOUS)
            ))
        if display_next:
            view.add_item(ButtonView(
                label="Next Page", style=ButtonStyle.grey, custom_id="next_page", row=4,
                emoji=discord_client.get_emoji(GeneralButtonEmoji.NEXT)
            ))
        view.add_item(ButtonView(
            label="Switch to Radio", style=ButtonStyle.blurple, custom_id="switch_to_radio", row=4,
            emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.RADIO])
        ))
    else:
        view.add_item(ButtonView(label="Connect", style=ButtonStyle.green, custom_id="connect"))

    return view


def get_radio_message_views(currently_playing_supported, show_stop_button, streams: Iterable = None,
                            selected_stream_code=None):
    view = View(timeout=None)

    if not streams:
        streams = shared_memory.music_streams.values()

    view.add_item(
        SelectView(placeholder="Select Radio", min_values=1, max_values=1, custom_id="select_stream", row=0,
                   options=[SelectOption(label=stream.name,
                                         value=stream.code,
                                         description=stream.get_genres_string(),
                                         emoji=discord_client.get_emoji(stream.icon_emoji_id),
                                         default=stream.code == selected_stream_code)
                            for stream in streams])
    )

    if show_stop_button:
        view.add_item(ButtonView(
            label="Stop", style=ButtonStyle.grey, custom_id="stop",
            emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.LEAVE])
        ))
    view.add_item(ButtonView(label="Disconnect", style=ButtonStyle.red, custom_id="disconnect", row=1))
    view.add_item(ButtonView(label="Report a problem..", style=ButtonStyle.grey, custom_id="report", row=1))

    if currently_playing_supported:
        view.add_item(ButtonView(label="What's Playing?", style=ButtonStyle.green, custom_id="show_currently_playing",
                                 row=2))

    view.add_item(ButtonView(
        label="Switch to Player", style=ButtonStyle.blurple, custom_id="switch_to_player", row=2,
        emoji=discord_client.get_emoji(PLAYER_ACTION_CUSTOM_EMOJI_MAP[PlayerAction.PLAYER])
    ))
    return view


def get_history_embed_views(interactions_handler, show_previous, show_next, track_index_title_map):
    view = View(timeout=300)

    if show_previous:
        previous_button = ButtonView(label="Previous", style=ButtonStyle.blurple, custom_id="previous",
                                     emoji=discord_client.get_emoji(GeneralButtonEmoji.PREVIOUS))
        previous_button.callback = interactions_handler.handle_history_previous_page
        view.add_item(previous_button)

    if show_next:
        next_button = ButtonView(label="Next", style=ButtonStyle.blurple, custom_id="next",
                                 emoji=discord_client.get_emoji(GeneralButtonEmoji.NEXT))
        next_button.callback = interactions_handler.handle_history_next_page
        view.add_item(next_button)

    track_select_view = SelectView(options=[SelectOption(label=shorten(f"{i+1}. {track_title}", 90), value=str(i))
                                            for i, track_title in track_index_title_map.items()],
                                   placeholder="Select a track to queue")
    track_select_view.callback = interactions_handler.handle_history_track_select
    view.add_item(track_select_view)
    return view


def get_roles_management_views(interactions_handler, placeholder="Select a role to add or remove",
                               add_clear_button=False):
    view = View(timeout=300)
    select_role_view = RoleSelect(placeholder=placeholder, max_values=1)
    select_role_view.callback = interactions_handler.handle_role_select
    view.add_item(select_role_view)

    if add_clear_button:
        clear_button = ButtonView(label="Clear", style=ButtonStyle.red, custom_id="clear",
                                  emoji=discord_client.get_emoji(GeneralButtonEmoji.CLEAR))
        clear_button.callback = interactions_handler.handle_clear_roles
        view.add_item(clear_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_logging_channel_setup_views(interactions_handler):
    view = View(timeout=300)

    select_channel_view = ChannelSelect(placeholder="Select a channel to receive logs", max_values=1)
    select_channel_view.callback = interactions_handler.handle_channel_select
    view.add_item(select_channel_view)

    create_new_channel_button = ButtonView(label="Create New Channel", style=ButtonStyle.green, custom_id="create_new",
                                           row=2, emoji=discord_client.get_emoji(GeneralButtonEmoji.ADD))
    create_new_channel_button.callback = interactions_handler.handle_create_new_channel
    view.add_item(create_new_channel_button)

    unset_channel_button = ButtonView(label="Unset Channel", style=ButtonStyle.red, custom_id="unset", row=2,
                                      emoji=discord_client.get_emoji(GeneralButtonEmoji.CLEAR))
    unset_channel_button.callback = interactions_handler.handle_unset_channel
    view.add_item(unset_channel_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_channels_management_views(interactions_handler, placeholder="Select a channel to add or remove",
                                  add_clear_button=False):
    view = View(timeout=300)
    select_channel_view = ChannelSelect(placeholder=placeholder, max_values=1)
    select_channel_view.callback = interactions_handler.handle_channel_select
    view.add_item(select_channel_view)

    if add_clear_button:
        clear_button = ButtonView(label="Clear", style=ButtonStyle.red, custom_id="clear",
                                  emoji=discord_client.get_emoji(GeneralButtonEmoji.CLEAR))
        clear_button.callback = interactions_handler.handle_clear_channels
        view.add_item(clear_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def quick_button_views(button_callback_map: dict, styles, on_timeout, timeout=300):
    view = View(timeout=timeout)
    for i, (label, callback) in enumerate(button_callback_map.items()):
        button = ButtonView(label=label, style=styles[i])
        button.callback = callback
        view.add_item(button)

    view.on_timeout = on_timeout
    return view


def get_xp_settings_views(xp_gain_enabled, levelup_message_enabled, xp_decay_enabled, level_roles_added,
                          stack_level_roles_enabled, interactions_handler):
    view = View(timeout=600)

    if not xp_gain_enabled:
        xp_gain_button = ButtonView(label="Enable XP Gain", style=ButtonStyle.green, custom_id="enable_xp_gain",
                                    emoji=discord_client.get_emoji(GeneralButtonEmoji.SWITCH))
    else:
        xp_gain_button = ButtonView(label="Disable XP Gain", style=ButtonStyle.red, custom_id="disable_xp_gain",
                                    emoji=discord_client.get_emoji(GeneralButtonEmoji.SWITCH))
    xp_gain_button.callback = interactions_handler.handle_xp_gain_toggle
    view.add_item(xp_gain_button)

    if not xp_gain_enabled:
        return view

    if levelup_message_enabled:
        levelup_message_button = ButtonView(label="Disable Levelup Message", style=ButtonStyle.red,
                                            custom_id="disable_levelup_message",
                                            emoji=discord_client.get_emoji(GeneralButtonEmoji.SWITCH))
    else:
        levelup_message_button = ButtonView(label="Enable Levelup Message", style=ButtonStyle.green,
                                            custom_id="enable_levelup_message",
                                            emoji=discord_client.get_emoji(GeneralButtonEmoji.SWITCH))
    levelup_message_button.callback = interactions_handler.handle_levelup_message_toggle
    view.add_item(levelup_message_button)

    if xp_decay_enabled:
        xp_decay_button = ButtonView(label="Disable XP Decay", style=ButtonStyle.red, custom_id="disable_xp_decay",
                                     emoji=discord_client.get_emoji(GeneralButtonEmoji.SWITCH))
    else:
        xp_decay_button = ButtonView(label="Enable XP Decay", style=ButtonStyle.green, custom_id="enable_xp_decay",
                                     emoji=discord_client.get_emoji(GeneralButtonEmoji.SWITCH))
    xp_decay_button.callback = interactions_handler.handle_xp_decay_toggle
    view.add_item(xp_decay_button)

    xp_gain_settings_button = ButtonView(label="XP Gain Settings", style=ButtonStyle.blurple,
                                         custom_id="xp_gain_settings", row=1,
                                         emoji=discord_client.get_emoji(GeneralButtonEmoji.SETTINGS))
    xp_gain_settings_button.callback = interactions_handler.handle_xp_gain_settings
    view.add_item(xp_gain_settings_button)

    levelup_message_settings_button = ButtonView(label="Levelup Message Settings", style=ButtonStyle.blurple,
                                                 custom_id="levelup_message_settings", row=1,
                                                 emoji=discord_client.get_emoji(GeneralButtonEmoji.SETTINGS))
    levelup_message_settings_button.callback = interactions_handler.handle_levelup_message_settings
    view.add_item(levelup_message_settings_button)

    xp_decay_settings_button = ButtonView(label="XP Decay Settings", style=ButtonStyle.blurple,
                                          custom_id="xp_decay_settings", row=1,
                                          emoji=discord_client.get_emoji(GeneralButtonEmoji.SETTINGS))
    xp_decay_settings_button.callback = interactions_handler.handle_xp_decay_settings
    view.add_item(xp_decay_settings_button)

    if level_roles_added:
        if stack_level_roles_enabled:
            button_label = "Disable level role stacking"
        else:
            button_label = "Enable level role stacking"
        stack_level_roles_button = ButtonView(label=button_label, style=ButtonStyle.gray,
                                              custom_id="stack_roles_toggle", row=1)
        stack_level_roles_button.callback = interactions_handler.handle_stack_roles_toggle
        view.add_item(stack_level_roles_button)

    level_role_select = RoleSelect(placeholder="Select a level role to add or remove",
                                   max_values=1, row=2)
    level_role_select.callback = interactions_handler.handle_level_role_select
    view.add_item(level_role_select)

    ignored_channel_select = ChannelSelect(placeholder="Select an Ignored Channel to add or remove",
                                           max_values=1, row=3)
    ignored_channel_select.callback = interactions_handler.handle_ignored_channel_select
    view.add_item(ignored_channel_select)

    ignored_role_select = RoleSelect(placeholder="Select an Ignored Role to add or remove",
                                     max_values=1, row=4)
    ignored_role_select.callback = interactions_handler.handle_ignored_role_select
    view.add_item(ignored_role_select)

    view.on_timeout = interactions_handler.on_timeout
    return view


def quick_role_select_view(placeholder, callback, on_timeout, max_values=1, row=0):
    view = View(timeout=300)
    role_select = RoleSelect(placeholder=placeholder, max_values=max_values, row=row)
    role_select.callback = callback
    view.add_item(role_select)

    view.on_timeout = on_timeout
    return view


def quick_member_select_view(placeholder, callback, on_timeout, max_values=1, row=0,
                             add_user_id_button=False, user_id_button_callback=None):
    view = View(timeout=300)

    member_select = UserSelect(placeholder=placeholder, max_values=max_values, row=row)
    member_select.callback = callback
    view.add_item(member_select)

    if add_user_id_button:
        user_id_button = ButtonView(label="Select by user ID", style=ButtonStyle.blurple, custom_id="user_id",
                                    row=row+1)
        user_id_button.callback = user_id_button_callback
        view.add_item(user_id_button)

    view.on_timeout = on_timeout
    return view


def get_general_help_views(interactions_handler, add_close_button=True):
    view = View(timeout=300)

    general_help_button = ButtonView(label="User Commands", style=ButtonStyle.green)
    general_help_button.callback = interactions_handler.handle_user_menu
    view.add_item(general_help_button)

    xp_help_button = ButtonView(label="Music Commands", style=ButtonStyle.blurple)
    xp_help_button.callback = interactions_handler.handle_music_menu
    view.add_item(xp_help_button)

    moderation_help_button = ButtonView(label="Admin Commands", style=ButtonStyle.gray)
    moderation_help_button.callback = interactions_handler.handle_admin_menu
    view.add_item(moderation_help_button)

    if add_close_button:
        close_button = ButtonView(label="Close", style=ButtonStyle.red, emoji="🗑")
        close_button.callback = interactions_handler.handle_cancel
        view.add_item(close_button)

    view.on_timeout = interactions_handler.on_timeout
    return view


def get_reminder_views():
    view = View(timeout=None)

    options = [SelectOption(label="1 hour", value="60"),
               SelectOption(label="12 hours", value="720"),
               SelectOption(label="1 day", value="1440"),
               SelectOption(label="Custom...", value="custom")]
    view.add_item(SelectView(placeholder="Snooze for...", options=options, row=0, custom_id="snooze_reminder_select"))

    return view
