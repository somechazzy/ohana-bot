from . import user_blueprints
from . import admin_blueprints


async def register_cogs():
    await user_blueprints.register_cogs()
    await admin_blueprints.register_cogs()
