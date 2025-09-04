from datetime import datetime

import discord

import cache
from bot.utils.embed_factory.general_embeds import get_info_embed, get_error_embed, get_success_embed
from clients import discord_client
from components.music_component import MusicComponent
from settings import OWNER_COMMAND_PREFIX
from constants import OhanaEnum, DiscordTimestamp
from system.extensions_management import load_extensions


class OwnerCommandsHandler:
    class OwnerCommand(OhanaEnum):
        HELP = "help"
        GUILD_LEAVE = 'guild leave'
        GUILD_INFO = 'guild info'
        STATS = 'stats'
        MUSIC_STREAMS_RELOAD = 'music streams reload'
        EXTENSIONS_RELOAD = 'extensions reload'
        PING = 'ping'
        SYNC_SLASHES = 'sync slashes'
        SYNC_COMMANDS = 'sync commands'  # alias for sync slashes

    def __init__(self, message: discord.Message):
        self.message: discord.Message = message
        self.channel = message.channel

    async def handle(self):
        content = self.message.content.lstrip(OWNER_COMMAND_PREFIX)
        command = self._parse_command(content)
        if not command:
            command = 'help'
        try:
            await getattr(self, command)()
        except Exception as e:
            await self.channel.send(embed=get_error_embed(f"An error occurred while executing the command: {e}"))

    def _parse_command(self, content: str):
        for command in self.OwnerCommand.as_list():
            if content.startswith(command):
                return command.replace(' ', '_')
        return None

    async def help(self):
        help_text = (
            "Owner Commands:\n"
            f"`{OWNER_COMMAND_PREFIX}help` - Show this help message\n"
            f"`{OWNER_COMMAND_PREFIX}guild leave <guild_id>` - Make the bot leave the specified guild\n"
            f"`{OWNER_COMMAND_PREFIX}guild info <guild_id>` - Get information about the specified guild\n"
            f"`{OWNER_COMMAND_PREFIX}stats` - Show bot statistics\n"
            f"`{OWNER_COMMAND_PREFIX}music streams reload` - Reload music streams from json file\n"
            f"`{OWNER_COMMAND_PREFIX}extensions reload` - Reload all extensions\n"
            f"`{OWNER_COMMAND_PREFIX}ping` - Check bot latency\n"
            f"`{OWNER_COMMAND_PREFIX}sync slashes` - Sync slash commands with Discord\n"
            f"`{OWNER_COMMAND_PREFIX}sync commands` - Alias for sync slashes\n"
        )
        await self.channel.send(embed=get_info_embed(help_text))

    async def guild_leave(self):
        parts = self.message.content.split()
        if len(parts) < 3:
            await self.channel.send(embed=get_error_embed("Please provide a guild ID."))
            return
        guild_id = int(parts[2]) if parts[2].isdigit() else None
        if not guild_id:
            await self.channel.send(embed=get_error_embed("Please provide a valid guild ID."))
            return
        guild = discord_client.get_guild(guild_id)
        if guild:
            await guild.leave()
            await self.channel.send(embed=get_success_embed(f"Left guild: {guild.name} (ID: {guild.id})"))
        else:
            await self.channel.send(embed=get_error_embed("Guild not found or bot is not a member of it."))

    async def guild_info(self):
        parts = self.message.content.split()
        if len(parts) < 3:
            await self.channel.send("Please provide a guild ID.")
            return
        guild_id = int(parts[2]) if parts[2].isdigit() else None
        if not guild_id:
            await self.channel.send(embed=get_error_embed("Please provide a guild ID."))
            return
        guild = discord_client.get_guild(guild_id)
        if not guild:
            await self.channel.send(embed=get_error_embed("Guild not found or bot is not a member of it."))
            return
        if not guild.chunked:
            await guild.chunk(cache=True)
        member_count = guild.member_count
        human_count = len([member for member in guild.members if not member.bot])
        bot_count = len([member for member in guild.members if member.bot])
        guild_created_at = int(datetime.timestamp(guild.created_at))
        guild_joined_at = int(datetime.timestamp(guild.me.joined_at))
        await self.channel.send(embed=get_info_embed(
            f"**{guild}** ({guild.id})\n\n"
            f"**Member count**: {member_count}.\n"
            f"**Owned by** {guild.owner} ({guild.owner.id}).\n"
            f"**Created at** {DiscordTimestamp.SHORT_DATE_TIME.format(timestamp=guild_created_at)}.\n"
            f"**Joined at** {DiscordTimestamp.SHORT_DATE_TIME.format(timestamp=guild_joined_at)}.\n"
            f"**Human count** = {human_count}.\n"
            f"**Bot count** = {bot_count}.\n"
            f"**Bot Percentage** = {round(bot_count * 100 / member_count, 2)}%\n"
            f"**Ohana admin status**: {guild.me.guild_permissions.administrator}.\n"
        ))

    async def stats(self):
        total_guilds = len(discord_client.guilds)
        total_members = sum(guild.member_count for guild in discord_client.guilds)
        total_humans = 0
        total_bots = 0
        chunked_guilds = 0
        for guild in discord_client.guilds:
            if not guild.chunked:
                continue
            chunked_guilds += 1
            total_humans += len([member for member in guild.members if not member.bot])
            total_bots += len([member for member in guild.members if member.bot])
        human_percentage = round(total_humans * 100 / (total_humans + total_bots), 2) if total_members else 0
        bot_percentage = round(total_bots * 100 / (total_humans + total_bots), 2) if total_members else 0
        current_radio_connections = len(cache.MUSIC_SERVICES)
        await self.channel.send(embed=get_info_embed(
            f"**Ohana stats**\n\n"
            f"**Total Guilds**: {total_guilds}\n"
            f"**Total Members**: {total_members}\n"
            f"**Total Humans**: {total_humans} (as seen in {chunked_guilds} chunked guilds)\n"
            f"**Total Bots**: {total_bots} (as seen in {chunked_guilds} chunked guilds)\n"
            f"**Human Percentage**: {human_percentage}%\n"
            f"**Bot Percentage**: {bot_percentage}%\n"
            f"**Radio streaming** in {current_radio_connections} servers\n"
        ))

    async def music_streams_reload(self):
        await MusicComponent().load_radio_streams()
        await self.channel.send(embed=get_success_embed("Music streams reloaded successfully."))

    async def extensions_reload(self):
        message = await self.channel.send(embed=get_info_embed("Reloading extensions..."))
        load_extensions()
        await message.edit(content=None, embed=get_success_embed("Extensions reloaded. Check logs for any errors."))

    async def ping(self):
        latency = discord_client.latency * 1000
        await self.channel.send(embed=get_info_embed(f"Pong! Latency: {round(latency, 2)} ms"))

    async def sync_slashes(self):
        return await self.sync_commands()

    async def sync_commands(self):
        synced = await discord_client.tree.sync()
        await self.channel.send(embed=get_success_embed(f"Synced {len(synced)} commands successfully."))
