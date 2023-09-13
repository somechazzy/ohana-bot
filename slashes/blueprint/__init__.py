from . import admin_blueprints
from . import music_blueprints
from . import user_blueprints


async def add_cogs():
    await admin_blueprints.add_cogs()
    await music_blueprints.add_cogs()
    await user_blueprints.add_cogs()
