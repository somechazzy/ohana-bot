from discord import app_commands

from bot.slashes.blueprints.admin_blueprints.automod_admin_blueprint import AutomodAdminBlueprints
from bot.slashes.blueprints.admin_blueprints.general_admin_blueprint import GeneralAdminBlueprints
from bot.slashes.blueprints.admin_blueprints.music_admin_blueprint import MusicAdminBlueprints
from bot.slashes.blueprints.admin_blueprints.role_menu_admin_blueprint import RoleMenuAdminBlueprints
from bot.slashes.blueprints.admin_blueprints.xp_admin_blueprint import XPAdminBlueprints
from clients import discord_client


@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
class AdminSlashesGroupCog(AutomodAdminBlueprints, GeneralAdminBlueprints, MusicAdminBlueprints,
                           RoleMenuAdminBlueprints, XPAdminBlueprints, name='manage'):
    pass


cog = AdminSlashesGroupCog()


async def register_cogs():
    await discord_client.add_cog(cog)
