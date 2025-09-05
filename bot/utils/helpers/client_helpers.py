import asyncio

import discord

from clients import discord_client
from common.app_logger import AppLogger
from common.exceptions import UserInputException
from constants import AppLogCategory


async def force_fetch_member(user_id: int, guild: discord.Guild) -> discord.Member:
    """
    Get a member from a guild, forcing a fetch if the guild is not chunked.
    Args:
        user_id (int): The ID of the user to fetch.
        guild (discord.Guild): The guild to fetch the member from.
    Returns:
        discord.Member: The member object.
    Raises:
        UserInputException: If the member is not found in the guild.
    """
    try:
        member = guild.get_member(user_id)
        if not member and not guild.chunked:
            member = await guild.fetch_member(user_id)
        if not member:
            raise discord.NotFound
    except discord.NotFound:
        raise UserInputException("Member not found in this server")
    return member


async def lazy_chunk_guilds():
    """
    Lazy chunk all guilds the bot is in.
    """
    for guild in discord_client.guilds:
        if not guild.chunked:
            await guild.chunk(cache=True)
            await asyncio.sleep(1)
    AppLogger('lazy_chunk_guilds').info("Finished lazy chunking guilds",
                                        category=AppLogCategory.BOT_GENERAL)


async def sync_commands_on_discord(guild_id: int | None = None):
    """
    Sync commands on Discord.
    Args:
        guild_id (int | None): The ID of the guild to sync commands to. If None, syncs globally.
    """
    if guild_id:
        guild = discord_client.get_guild(guild_id)
        if not guild:
            raise UserInputException("Guild not found")
        AppLogger('sync_commands_on_discord').info(f"Syncing commands on Discord for guild {guild.name} ({guild.id})",
                                                   category=AppLogCategory.BOT_GENERAL)
    else:
        guild = None
        AppLogger('sync_commands_on_discord').info("Syncing commands on Discord globally",
                                                   category=AppLogCategory.BOT_GENERAL)
    await discord_client.tree.sync(guild=guild)
