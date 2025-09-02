import discord
import pytz

from bot.utils.modal_factory.reminder_modals import TimezoneSelectionModal
from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.embed_factory.user_embeds import get_user_settings_embed
from bot.utils.view_factory.user_views import get_user_settings_view
from bot.utils.decorators import interaction_handler
from common.exceptions import UserInputException
from components.user_settings_components.user_settings_component import UserSettingsComponent
from constants import AnimangaProvider, Links
from models.user_settings_models import UserSettings


class UserSettingsInteractionHandler(UserInteractionHandler):
    VIEW_NAME = "User settings"

    def __init__(self, user_settings: UserSettings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interactions_restricted = True
        self._is_closed = False
        self.user_settings: UserSettings = user_settings
        self.user_settings_component = UserSettingsComponent()

    async def preprocess_and_validate(self, *args, **kwargs):
        await super().preprocess_and_validate(*args, **kwargs)
        self.user_settings = await self.user_settings_component.get_user_settings(
            user_id=self.original_user.id,
            load_usernames=True
        )

    @interaction_handler()
    async def set_preferred_animanga_provider(self, interaction: discord.Interaction):
        new_provider = interaction.data["values"][0]
        if new_provider not in AnimangaProvider.as_list():
            raise ValueError(f"Invalid provider: {new_provider}")
        await interaction.response.defer()
        await self.user_settings_component.update_user_settings(user_settings=self.user_settings,
                                                                preferred_animanga_provider=new_provider)
        await self.refresh_message(feedback="✅ Preferred provider updated.")

    @interaction_handler()
    async def set_relayed_reminders_enablement(self, interaction: discord.Interaction):
        new_value = interaction.data["values"][0] != "enabled"
        await interaction.response.defer()
        await self.user_settings_component.update_user_settings(user_settings=self.user_settings,
                                                                relayed_reminders_disabled=new_value)
        await self.refresh_message(feedback="✅ Relayed reminders disablement updated.")

    @interaction_handler()
    async def set_timezone(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TimezoneSelectionModal(
            interactions_handler=self
        ))
        return

    @interaction_handler()
    async def on_timezone_modal_submit(self, interaction: discord.Interaction, timezone: str):
        await interaction.response.defer()
        if not timezone or timezone not in pytz.all_timezones:
            raise UserInputException(f"Invalid timezone. Get your timezone here: {Links.APPS_TIMEZONE}")
        await self.user_settings_component.update_user_settings(user_settings=self.user_settings,
                                                                timezone=timezone)
        await self.refresh_message(feedback="✅ Timezone updated.")

    async def refresh_message(self, feedback: str | None = None, *args, **kwargs) -> None:
        embed, view = self.get_embed_and_view(feedback=feedback)
        await self.source_interaction.edit_original_response(embed=embed, view=view)

    def get_embed_and_view(self, feedback: str | None = None, *args, **kwargs) -> tuple[discord.Embed, discord.ui.View]:
        embed = get_user_settings_embed(timezone=self.user_settings.timezone,
                                        preferred_animanga_provider=self.user_settings.preferred_animanga_provider,
                                        relayed_reminders_disabled=self.user_settings.relayed_reminders_disabled,
                                        usernames_map=self._get_usernames_map(),
                                        user=self.original_user,
                                        feedback=feedback)
        view = get_user_settings_view(interaction_handler=self,
                                      preferred_animanga_provider=self.user_settings.preferred_animanga_provider,
                                      relayed_reminders_disabled=self.user_settings.relayed_reminders_disabled)
        return embed, view

    def _get_usernames_map(self) -> dict[str, str]:
        return {
            username.provider: username.username for username in self.user_settings.usernames
        }
