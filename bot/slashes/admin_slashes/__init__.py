from bot.slashes import BaseSlashes
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent


class AdminSlashes(BaseSlashes):

    def __init__(self, interaction):
        super().__init__(interaction=interaction)
        self.guild_settings_component: GuildSettingsComponent = GuildSettingsComponent()

    async def preprocess_and_validate(self, **kwargs):
        await super().preprocess_and_validate(**kwargs | dict(guild_only=True))
