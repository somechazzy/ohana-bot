from discord import app_commands
from globals_.clients import discord_client
from .role_menu_admin_blueprints import RoleMenuAdminBlueprints
from .general_admin_blueprints import GeneralAdminBlueprints
from .xp_admin_blueprints import XPAdminBlueprints


@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
class AdminSlashesGroupCog(RoleMenuAdminBlueprints, GeneralAdminBlueprints, XPAdminBlueprints,
                           name='manage'):
    pass


cog = AdminSlashesGroupCog()


async def add_cogs():
    await discord_client.add_cog(cog)
