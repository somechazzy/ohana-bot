from typing import TYPE_CHECKING

from discord import SelectOption, ButtonStyle
from discord.ui import View, Select, Button

from clients import emojis
from constants import AnimangaProvider

if TYPE_CHECKING:
    from bot.interaction_handlers.user_interaction_handlers.user_settings_interaction_handler import \
        UserSettingsInteractionHandler
    from bot.interaction_handlers.user_interaction_handlers.reminder_setup_interaction_handler import \
        ReminderSetupInteractionHandler


def get_user_settings_view(interaction_handler: 'UserSettingsInteractionHandler',
                           preferred_animanga_provider: str,
                           relayed_reminders_disabled: bool) -> View:
    """
    Creates a view for user settings, including timezone setting, preferred anime/manga provider selection,
    and relayed reminders enablement.
    Args:
        interaction_handler (UserSettingsInteractionHandler): The interaction handler for the view.
        preferred_animanga_provider (str): The user's current preferred anime/manga provider.
        relayed_reminders_disabled (bool): Whether relayed reminders are disabled.
    Returns:
        View: The created view.
    """
    view = View(timeout=600)

    timezone_button = Button(label="Set timezone", style=ButtonStyle.blurple, emoji=emojis.general.clock)
    timezone_button.callback = interaction_handler.set_timezone
    view.add_item(timezone_button)

    animanga_provider_select_view = Select(
        options=[
            SelectOption(label=f"Preferred Anime/Manga Provider: MyAnimeList",
                         value=AnimangaProvider.MAL,
                         default=preferred_animanga_provider == AnimangaProvider.MAL,
                         emoji=emojis.logos.mal),
            SelectOption(label=f"Preferred Anime/Manga Provider: AniList",
                         value=AnimangaProvider.ANILIST,
                         default=preferred_animanga_provider == AnimangaProvider.ANILIST,
                         emoji=emojis.logos.anilist),
        ]
    )
    animanga_provider_select_view.callback = interaction_handler.set_preferred_animanga_provider
    view.add_item(animanga_provider_select_view)

    relayed_reminders_select_view = Select(
        options=[
            SelectOption(label="Relayed Reminders: Enabled",
                         value="enabled",
                         default=not relayed_reminders_disabled,
                         emoji='✅'),
            SelectOption(label="Relayed Reminders: Disabled",
                         value="disabled",
                         default=relayed_reminders_disabled,
                         emoji='❌'),
        ]
    )
    relayed_reminders_select_view.callback = interaction_handler.set_relayed_reminders_enablement
    view.add_item(relayed_reminders_select_view)

    view.on_timeout = interaction_handler.on_timeout  # type: ignore
    return view


def get_timezone_prompt_view(interactions_handler: 'ReminderSetupInteractionHandler') -> View:
    """
    Creates a view prompting the user to set their timezone or cancel the setup.
    Args:
        interactions_handler: The interaction handler for the view.
    Returns:
        View: The created view.
    """
    view = View(timeout=300)

    set_timezone_button = Button(label="Set Timezone", style=ButtonStyle.green, custom_id="set-timezone",
                                 emoji=emojis.general.settings, row=0)
    set_timezone_button.callback = interactions_handler.go_to_set_timezone
    view.add_item(set_timezone_button)

    cancel_button = Button(label="Cancel", style=ButtonStyle.gray, custom_id="cancel-timezone",
                           emoji=emojis.navigation.back, row=0)
    cancel_button.callback = interactions_handler.on_cancel_setup
    view.add_item(cancel_button)

    view.on_timeout = interactions_handler.on_timeout
    return view
