from bot.interaction_handlers import BaseInteractionHandler
from bot.utils.embed_factory.general_embeds import get_info_embed
from bot.utils.guild_logger import GuildLogEventField, GuildLogger
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import GuildLogEvent


class AdminInteractionHandler(BaseInteractionHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild_settings_component: GuildSettingsComponent = GuildSettingsComponent()
        self.interactions_restricted = True

    def __new__(cls, *args, **kwargs):
        if cls is AdminInteractionHandler:
            raise TypeError("AdminInteractionHandler cannot be instantiated directly. "
                            "Please use a subclass instead.")
        return super().__new__(cls)

    async def preprocess_and_validate(self, *args, **kwargs):
        await super().preprocess_and_validate(*args, **kwargs)

    async def log_setting_change(self, event_text: str, fields: list[GuildLogEventField] | None = None):
        """
        Quick-access method to log a setting change event to the guild's logging channel.
        Args:
            event_text (str): Description of the event.
            fields (list[GuildLogEventField] | None): Additional fields to include in the log embed.
        """
        await GuildLogger(guild=self.guild).log_event(event=GuildLogEvent.SETTING_CHANGE,
                                                      actor=self.source_interaction.user,
                                                      event_message=event_text,
                                                      fields=fields)

    async def on_timeout(self):
        await self.source_interaction.edit_original_response(embed=get_info_embed("Timed out! "
                                                                                  "Please recall the command."),
                                                             view=None)
