import asyncio
import os
from datetime import datetime
# import psutil
from actions import send_embed
from components.music_components.base_music_component import MusicComponent
from globals_.clients import discord_client, firebase_client
from globals_ import shared_memory
from globals_.constants import CustomEnum, PLAYER_HEADER_IMAGE, Colour
from utils.helpers import get_id_from_text, get_ids_from_text, backup_music_services
import discord


"""
Note: psutil might be difficult to install due to its OS dependencies. 
I've commented out its usage here but if you manage to install it,
 you uncomment its related code below (`usage` command)
"""


class OwnerCommandsHandler:
    class OwnerCommand(CustomEnum):
        HELP = "help"
        # USAGE = 'usage'
        GUILD_LEAVE = 'guild leave'
        GUILDS_LEAVE = 'guilds leave'
        GUILD_INFO = 'guild info'
        GUILD_LIST = 'guild list'
        STATS = 'stats'
        MUSIC_BACKUP = 'music backup'
        MUSIC_CLEANUP = 'music cleanup'
        MUSIC_REFRESH_BLOCK = 'music refresh block'
        MUSIC_REFRESH_UNBLOCK = 'music refresh unblock'
        MUSIC_STREAMS_SYNC = 'music streams sync'
        
        # MIGRATIONS
        SYNC_SLASHES = 'sync slashes'
        REFRESH_MUSIC_MESSAGES = 'refresh music messages'

    def __init__(self, message):
        self.message = message
        self.message_content_lowered = message.content.lower()[2:]
        self.channel = message.channel
        self.client = discord_client

    async def handle(self):
        if self.message_content_lowered == self.OwnerCommand.HELP:
            return await self.handle_command_help()
        # elif self.message_content_lowered == self.OwnerCommand.USAGE:
        #     return await self.handle_command_usage()
        elif self.message_content_lowered.startswith(self.OwnerCommand.GUILD_LEAVE):
            return await self.handle_command_guild_leave()
        elif self.message_content_lowered.startswith(self.OwnerCommand.GUILDS_LEAVE):
            return await self.handle_command_guilds_leave()
        elif self.message_content_lowered.startswith(self.OwnerCommand.GUILD_INFO):
            return await self.handle_command_guild_info()
        elif self.message_content_lowered.startswith(self.OwnerCommand.GUILD_LIST):
            return await self.handle_command_guild_list()
        elif self.message_content_lowered == self.OwnerCommand.STATS:
            return await self.handle_command_stats()
        elif self.message_content_lowered == self.OwnerCommand.MUSIC_BACKUP:
            return await self.handle_command_music_backup()
        elif self.message_content_lowered == self.OwnerCommand.MUSIC_CLEANUP:
            return await self.handle_command_music_cleanup()
        elif self.message_content_lowered.startswith(self.OwnerCommand.SYNC_SLASHES):
            return await self.handle_command_sync_slashes()
        elif self.message_content_lowered.startswith(self.OwnerCommand.REFRESH_MUSIC_MESSAGES):
            return await self.handle_command_refresh_music_messages()
        elif self.message_content_lowered.startswith(self.OwnerCommand.MUSIC_REFRESH_BLOCK):
            return await self.handle_command_music_refresh_block()
        elif self.message_content_lowered.startswith(self.OwnerCommand.MUSIC_REFRESH_UNBLOCK):
            return await self.handle_command_music_refresh_unblock()
        elif self.message_content_lowered.startswith(self.OwnerCommand.MUSIC_STREAMS_SYNC):
            return await self.handle_command_sync_music_streams()

    async def handle_command_help(self):
        commands_list = '**' + '**\n**'.join(self.OwnerCommand.as_list()) + '**'
        return await send_embed(f"Owner commands:\n{commands_list}", self.channel)

    # async def handle_command_usage(self):
    #     memory_amount_usage = round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, 2)
    #     memory_percent_usage = round(psutil.virtual_memory().percent, 2)
    #     memory_usage = f"Memory usage = {memory_amount_usage} MB ({memory_percent_usage}%)"
    #
    #     disk_amount_usage = round(psutil.disk_usage(os.sep).used / 1024 ** 2, 2)
    #     disk_percent_usage = round(psutil.disk_usage(os.sep).percent, 2)
    #     disk_usage = f"Disk usage = {disk_amount_usage} MB ({disk_percent_usage}%)"
    #
    #     cpu_usage = f"CPU usage = {round(psutil.cpu_percent(), 2)}%"
    #
    #     await send_embed(f"{memory_usage}\n{disk_usage}\n{cpu_usage}", self.channel, emoji="🚀",
    #                      color=Colour.SYSTEM, logging=False, title="Usage")

    async def handle_command_guild_leave(self):
        guild_id = get_id_from_text(str(self.message.content))
        if not guild_id:
            await send_embed("Enter proper ID.", self.channel)
            return
        guild = discord_client.get_guild(guild_id)
        if not guild:
            await send_embed("Guild not found.", self.channel)
            return
        await guild.leave()
        await send_embed("Left guild.", self.channel)

    async def handle_command_guilds_leave(self):
        guild_ids = get_ids_from_text(str(self.message.content))
        if not guild_ids:
            await send_embed("Enter some IDs.", self.channel)
            return
        guilds = [discord_client.get_guild(guild_id) for guild_id in guild_ids]
        if not guilds or not all(guilds):
            await send_embed("Not all guilds were found.", self.channel)
            return
        for guild in guilds:
            await guild.leave()
            await send_embed(f"Left guild {guild} ({guild.id}).", self.channel)

    async def handle_command_guild_info(self):
        option_value_pairs = self._get_option_value_pairs()
        days = option_value_pairs.get('d', 3)
        guild_id = get_id_from_text(self.message_content_lowered)
        if not guild_id:
            await send_embed("Enter proper ID.", self.channel)
            return
        guild = discord_client.get_guild(guild_id)
        if not guild:
            await send_embed("Guild not found.", self.channel)
            return
        client = self.client
        member_count = guild.member_count
        human_count = len([member for member in guild.members if not member.bot])
        bot_count = len([member for member in guild.members if member.bot])
        owner_other_guild_count = \
            len([guild_ for guild_ in client.guilds if guild_.owner.id == guild.owner.id and guild_.id != guild.id])

        await send_embed(
            f"**{guild}** ({guild.id})\n\n"
            f"**Member count**: {member_count}.\n"
            f"**Owned by** {guild.owner} ({guild.owner.id}).\n" +
            (f"**This bot is in** {owner_other_guild_count} other guilds they own.\n" if owner_other_guild_count else "") +
            f"**Created at** <t:{int(datetime.timestamp(guild.created_at))}:f>.\n"
            f"**Joined at** <t:{int(datetime.timestamp(guild.me.joined_at))}:f>.\n"
            f"**Human count** = {human_count}.\n"
            f"**Bot count** = {bot_count}.\n"
            f"**Bot Percentage** = {round(bot_count * 100 / member_count, 2)}%\n"
            f"**Bot admin status**: {guild.me.guild_permissions.administrator}.\n",
            self.channel, bold=False)

    async def handle_command_guild_list(self):
        option_value_pairs = self._get_option_value_pairs()
        include_ids = option_value_pairs.get('id', False) or option_value_pairs.get('ids', False)
        guilds_dict = {}
        for guild in self.client.guilds:
            bot_count = len([member for member in guild.members if member.bot])
            bot_percentage = round(bot_count * 100 / guild.member_count, 2)
            bolded_percentage = "**" if bot_percentage > 50 else ""
            bolded_member_count = "**" if guild.member_count < 11 else ""
            guilds_dict[f"{guild.name} ({guild.id})" if include_ids else guild.name] = \
                f"Total count = {bolded_member_count}{guild.member_count}{bolded_member_count}, " \
                f"Bots = {bolded_percentage}{bot_percentage}{bolded_percentage}%."
        list_of_message_contents_to_send = []
        message_content = ""
        for guild_key, guild_stats in guilds_dict.items():
            message_extension = f"**{guild_key}**: {guild_stats}\n"
            if len(message_content) + len(message_extension) > 1500:
                list_of_message_contents_to_send.append(f"{message_content}")
                message_content = ""
            message_content += message_extension
        list_of_message_contents_to_send.append(f"{message_content}")
        number_of_messages = len(list_of_message_contents_to_send)
        for i, message_content_to_send in enumerate(list_of_message_contents_to_send, 1):
            await send_embed(f"**Guilds** ({i}/{number_of_messages})\n\n" + message_content_to_send.strip(),
                             self.channel, bold=False)

    async def handle_command_stats(self):
        member_ids = []
        bot_ids = []
        channel_count = 0
        for guild in self.client.guilds:
            for user in guild.members:
                member_ids.append(user.id)
                if user.bot:
                    bot_ids.append(user.id)
            channel_count += len(guild.channels)
        total_member_count = len(member_ids)
        total_bot_count = len(bot_ids)
        unique_user_count = len(set(member_ids))
        unique_bot_count = len(set(bot_ids))
        total_human_percentage = round((total_member_count - total_bot_count) * 100 / total_member_count, 2)
        total_bot_percentage = round(100 - total_human_percentage, 2)
        unique_human_percentage = round((unique_user_count - unique_bot_count) * 100 / unique_user_count, 2)
        unique_bot_percentage = round(100 - unique_human_percentage, 2)
        await send_embed(f"**Bot Stats**\n"
                         f"**Guild count** = {len(self.client.guilds)}\n"
                         f"**Total channel count** = {channel_count}\n"
                         f"**Total member count** = {total_member_count}\n"
                         f"  **-of which are bots** = {total_bot_count}\n"
                         f"**Unique user count** = {unique_user_count}\n"
                         f"  **-of which are bots** = {unique_bot_count}\n"
                         f"**Total human/bot ratio** = {total_human_percentage}% humans,"
                         f" {total_bot_percentage}% bots\n"
                         f"**Unique user/bot ratio** = {unique_human_percentage}% humans,"
                         f" {unique_bot_percentage}% bots",
                         self.channel, bold=False)

    async def handle_command_music_backup(self):
        if self._get_option_value_pairs().get('notify', False):
            await send_embed("Informing current users...", self.channel)
            for gms in shared_memory.guild_music_services.values():
                if gms.voice_client and gms.voice_client.is_playing() \
                        and gms.text_channel and gms.music_channel != gms.text_channel:
                    await send_embed("This bot is restarting soon. Don't worry, your queue "
                                     "will be restored within few seconds...", gms.text_channel)
                    await asyncio.sleep(1)
            await send_embed("Everyone informed", self.channel)
        ms_count = await backup_music_services()
        await send_embed(f"Backup complete ({ms_count} services)", self.channel)

    async def handle_command_music_cleanup(self):
        from internal.system import MusicCleanup
        await MusicCleanup().handle_cleanup(self.message)

    def _get_option_value_pairs(self, keep_digits_as_str: list = None):
        if keep_digits_as_str is None:
            keep_digits_as_str = []
        pairs = {}
        idx = 0
        while idx < len(self.message_content_lowered):
            if self.message_content_lowered[idx] != '-':
                idx += 1
                continue
            elif (idx + 1) < len(self.message_content_lowered) and self.message_content_lowered[idx + 1] != ' ':
                idx += 1
                option_name = ''
                while idx < len(self.message_content_lowered) and self.message_content_lowered[idx] != ' ':
                    option_name += self.message_content_lowered[idx]
                    idx += 1
                while self.message_content_lowered[idx] == ' ' and idx < len(self.message_content_lowered):
                    idx += 1
                option_value = ''
                while idx < len(self.message_content_lowered) and self.message_content_lowered[idx] not in ['-', ' ']:
                    option_value += self.message_content_lowered[idx]
                    idx += 1
                if option_value.isdigit() and option_name not in keep_digits_as_str:
                    option_value = int(option_value)
                if option_value == '':
                    option_value = True
                pairs[option_name] = option_value

        return pairs

    async def handle_command_sync_slashes(self):
        if 'guild' in self.message_content_lowered:
            await discord_client.tree.sync(guild=self.channel.guild)
        else:
            await discord_client.tree.sync()
        await send_embed("Slashes sync requested", self.channel)

    async def handle_command_refresh_music_messages(self):
        guild_prefs = shared_memory.guilds_prefs
        guild_id_music_channel_id_map = {}
        guild_id_header_message_id_map = {}
        guild_id_player_message_id_map = {}
        for guild_id, guild_pref in guild_prefs.items():
            if not guild_pref.music_channel \
                    or not guild_pref.music_header_message \
                    or not guild_pref.music_player_message:
                continue
            guild_id_music_channel_id_map[guild_id] = guild_pref.music_channel
            guild_id_header_message_id_map[guild_id] = guild_pref.music_header_message
            guild_id_player_message_id_map[guild_id] = guild_pref.music_player_message

        player_update_failed = []
        music_channel_missing = []
        successful_updates = []
        idx = 0
        for guild_id, music_channel_id in guild_id_music_channel_id_map.items():
            idx += 1
            await send_embed(f"Refreshing music messages for guild {idx}/{len(guild_id_music_channel_id_map)}",
                             self.channel)
            music_channel = discord_client.get_channel(music_channel_id)
            if not music_channel:
                music_channel_missing.append(guild_id)
                continue

            # delete all messages in music channel that aren't the header or player message
            async for message in music_channel.history(limit=300):
                if message.id not in [guild_id_header_message_id_map[guild_id],
                                      guild_id_player_message_id_map[guild_id]]:
                    await message.delete()

            # update header, resend player messages

            try:
                header_message = await music_channel.fetch_message(guild_id_header_message_id_map[guild_id])
            except discord.errors.NotFound:
                header_message = None
            if header_message:
                embeds = header_message.embeds
                if embeds:
                    embed = embeds[0]
                    embed.set_image(url=PLAYER_HEADER_IMAGE)
                    await header_message.edit(embed=embed)
                else:
                    await header_message.delete()
                    header_message = None

            try:
                player_message = await music_channel.fetch_message(guild_id_player_message_id_map[guild_id])
            except discord.errors.NotFound:
                player_message = None
            if player_message:
                await player_message.delete()

            music_component = MusicComponent()
            await music_component.setup_player_channel(guild=music_channel.guild, music_channel=music_channel,
                                                       send_header=not header_message)
            if guild_id in shared_memory.guild_music_services:
                await shared_memory.guild_music_services[guild_id].refresh_player()

            successful_updates.append(guild_id)

        await send_embed(f"Refreshed music messages for {len(successful_updates)} guilds,"
                         f" {len(player_update_failed)} player updates failed. \n"
                         f"{len(music_channel_missing)} music channels missing.",
                         self.channel)

    async def handle_command_music_refresh_block(self):
        ids = get_ids_from_text(self.message_content_lowered)
        if not len(ids) >= 2:
            return await send_embed("Invalid input. Expected guild ID followed by user ID(s)", self.channel)
        guild_id = ids[0]
        user_ids = ids[1:]

        if not discord_client.get_guild(guild_id):
            return await send_embed("Invalid guild ID", self.channel)
        for user_id in user_ids:
            if not discord_client.get_user(user_id):
                return await send_embed("Invalid user ID", self.channel)

        shared_memory.GUILDS_WITH_PLAYER_REFRESH_DISABLED.add(guild_id)

        await firebase_client.add_guild_with_disabled_players_refresh_button(guild_id=guild_id, user_ids=user_ids)

    async def handle_command_music_refresh_unblock(self):
        ids = get_ids_from_text(self.message_content_lowered)
        if not ids:
            return await send_embed("Invalid input. Expected guild ID", self.channel)
        guild_id = ids[0]

        if guild_id not in shared_memory.GUILDS_WITH_PLAYER_REFRESH_DISABLED:
            return await send_embed("Guild not added to block list", self.channel)

        shared_memory.GUILDS_WITH_PLAYER_REFRESH_DISABLED.remove(guild_id)

        await firebase_client.remove_guild_with_disabled_players_refresh_button(guild_id=guild_id)
        
    async def handle_command_sync_music_streams(self):
        from utils.helpers import load_music_streams
        await load_music_streams()
