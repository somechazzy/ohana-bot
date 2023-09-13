from auto_moderation.guild_specific_perks.base import GuildPerks
from globals_.constants import SUPPORT_SERVER_ID


class InnPerks(GuildPerks):
    GUILD_ID = SUPPORT_SERVER_ID

    async def handle_automod(self, message):
        pass
