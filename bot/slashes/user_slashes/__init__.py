from clients import emojis
from constants import CommandContext
from bot.slashes import BaseSlashes


class UserSlashes(BaseSlashes):

    def __init__(self, interaction):
        super().__init__(interaction=interaction)
        self.loading_emoji = '⌛'
        if self.context in [CommandContext.DM, CommandContext.SELF_INSTALL] or \
                (self.context == CommandContext.GUILD and
                 self.channel.permissions_for(self.guild.me).use_external_emojis):
            self.loading_emoji = emojis.loading.get_random()

    async def preprocess_and_validate(self, **kwargs):
        await super().preprocess_and_validate(**kwargs)
