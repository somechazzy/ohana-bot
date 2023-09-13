
class GuildPerks:
    GUILD_ID = None

    def handle_automod(self, message):
        raise NotImplementedError

    @staticmethod
    def get_perks_class_by_guild_id(guild_id):
        from auto_moderation.guild_specific_perks.inn_perks import InnPerks
        if guild_id == InnPerks.GUILD_ID:
            return InnPerks
