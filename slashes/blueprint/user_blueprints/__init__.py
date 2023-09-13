from globals_.clients import discord_client
from .anime_user_blueprints import AnimeUserBlueprints
from .moderation_user_blueprints import ModerationUserBlueprints
from .other_user_blueprints import OtherUserBlueprints
from .utility_user_blueprints import UtilityUserBlueprints
from .xp_user_blueprints import XPUserBlueprints


class UserSlashesCog(AnimeUserBlueprints, ModerationUserBlueprints, OtherUserBlueprints,
                     UtilityUserBlueprints, XPUserBlueprints):
    pass


cog = UserSlashesCog()


async def add_cogs():
    await discord_client.add_cog(cog)
