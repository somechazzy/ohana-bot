

async def register_cogs():
    from .slashes.blueprints import register_cogs as register_slashes_cogs
    from .context_menus import register_commands as register_context_menus_commands
    await register_slashes_cogs()
    await register_context_menus_commands()
