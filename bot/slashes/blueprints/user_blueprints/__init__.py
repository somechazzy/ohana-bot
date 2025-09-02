from clients import discord_client
from .animanga_user_blueprint import AnimangaUserBlueprint
from .general_user_blueprint import GeneralUserBlueprint
from .moderation_user_blueprint import ModerationUserBlueprint
from .reminder_user_blueprint import RemindUserBlueprint
from .utility_user_blueprint import UtilityUserBlueprint
from .xp_user_blueprint import XPUserBlueprint


class UserSlashesCog(AnimangaUserBlueprint, GeneralUserBlueprint, UtilityUserBlueprint,
                     ModerationUserBlueprint, XPUserBlueprint):
    pass


cog = UserSlashesCog()
reminder_user_cog = RemindUserBlueprint()


async def register_cogs():
    await discord_client.add_cog(cog)
    await discord_client.add_cog(reminder_user_cog)
