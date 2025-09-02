from clients import discord_client


async def register_commands():
    from .blueprint import remind_me, get_avatar, get_banner, get_level, get_emoji, get_sticker
    discord_client.tree.add_command(remind_me)
    discord_client.tree.add_command(get_avatar)
    discord_client.tree.add_command(get_banner)
    discord_client.tree.add_command(get_level)
    discord_client.tree.add_command(get_emoji)
    discord_client.tree.add_command(get_sticker)
