from actions import send_embed
from globals_.constants import GuildLogType, BOT_NAME
from internal.bot_logging import log_to_server
from commands.admin_command_executor import AdminCommandExecutor
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from helpers import get_id_from_text


class ChannelsAdminCommandExecutor(AdminCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)

    async def handle_command_logschannel(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "set":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a channel "
                                                         "mention/ID to set as logs channel.")
                return
            channel_id = get_id_from_text(sub_command_options[0])
            if not channel_id:
                return await self.handle_incorrect_use(feedback="Provide me with a channel "
                                                                "mention/ID to set as logs channel.")
            channel = self.guild.get_channel(channel_id)
            if await self.channel_checks_fail(channel):
                return

            await GuildPrefsComponent().set_guild_logs_channel(self.guild, channel_id)
            await send_embed(f"Logs channel set to <#{channel_id}>. All {BOT_NAME}-related logs will be sent there.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event=f"Set logs channel for logging {BOT_NAME} related events.",
                                fields=["Channel"],
                                values=[f"this channel, duh"])

        elif self.used_sub_command == "show":
            if not self.guild_prefs.logs_channel:
                return await send_embed(f"No logs channel set yet.", self.channel,
                                        reply_to=self.message)
            await send_embed(f"Logs channel is <#{self.guild_prefs.logs_channel}>.", self.channel,
                             reply_to=self.message)

        elif self.used_sub_command == "unset":
            if self.guild_prefs.logs_channel:
                await send_embed(f"I will no longer log to <#{self.guild_prefs.logs_channel}>.",
                                 self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
                await GuildPrefsComponent().set_guild_logs_channel(self.guild, 0)
                await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                    event=f"Unset logs channel for logging {BOT_NAME} related events.")
            else:
                await send_embed(f"You haven't set a logs channel yet.",
                                 self.channel, reply_to=self.message)

    async def handle_command_spamchannel(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "set":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a channel "
                                                         "mention/ID to set as spam channel.")
                return
            channel_id = get_id_from_text(sub_command_options[0])
            if not channel_id:
                await self.handle_incorrect_use(feedback="Provide me with a channel "
                                                         "mention/ID to set as spam channel.")
                return
            channel = self.guild.get_channel(channel_id)
            if await self.channel_checks_fail(channel):
                return

            await GuildPrefsComponent().set_guild_spam_channel(self.guild, channel_id)
            await send_embed(f"Spam channel set to <#{channel_id}>. "
                             f"This channel will be an exception for any disabled commands.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Set spam channel - for allowing all sorts of commands.",
                                fields=["Channel"],
                                values=[f"<#{channel_id}>"])

        elif self.used_sub_command == "show":
            if not self.guild_prefs.spam_channel:
                await send_embed(f"No spam channel set yet.", self.channel,
                                 reply_to=self.message)
                return
            await send_embed(f"Spam channel is <#{self.guild_prefs.spam_channel}>.", self.channel,
                             reply_to=self.message)

        elif self.used_sub_command == "unset":
            if self.guild_prefs.spam_channel:
                await send_embed(f"<#{self.guild_prefs.spam_channel}> is no longer the spam channel.",
                                 self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
                await GuildPrefsComponent().set_guild_spam_channel(self.guild, 0)
                await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                    event="Unset spam channel.")
            else:
                await send_embed(f"You haven't set a spam channel yet.",
                                 self.channel, reply_to=self.message)

    async def handle_command_animechannels(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a channel "
                                                         "mention/ID to add as an anime/manga channel.")
                return
            channel_id = get_id_from_text(sub_command_options[0])
            if not channel_id:
                await self.handle_incorrect_use(feedback="Provide me with a channel "
                                                         "mention/ID to add as an anime/manga channel.")
                return
            channel = self.guild.get_channel(channel_id)
            if await self.channel_checks_fail(channel):
                return
            if int(channel_id) in self.guild_prefs.anime_channels:
                await send_embed(f"<#{channel_id}> is already an Anime/Manga channel.",
                                 self.channel, reply_to=self.message)
                return

            await GuildPrefsComponent().add_guild_anime_channel(self.guild, channel_id)
            await send_embed(
                f"<#{channel_id}> has been added to exception channels for Anime/Manga commands.",
                self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added an anime channel - for allowing all Anime & Manga commands.",
                                fields=["Channel"],
                                values=[f"<#{channel_id}>"])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a channel "
                                                         "mention/ID to remove from anime/manga channels.")
                return
            channel_id = get_id_from_text(sub_command_options[0])

            if int(channel_id) not in self.guild_prefs.anime_channels:
                await send_embed("Channel you entered isn't an Anime/Manga channel.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.message)
                return
            await GuildPrefsComponent().remove_guild_anime_channel(self.guild, channel_id)
            await send_embed(f"<#{channel_id}> has been unset as an Anime/Manga channel.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Removed a channel as an Anime & Manga channel.",
                                fields=["Channel"],
                                values=[f"<#{channel_id}>"])

        elif self.used_sub_command == "show":
            if not self.guild_prefs.anime_channels:
                await send_embed(f"No Anime/Manga channels added yet.", self.channel,
                                 reply_to=self.message)
                return

            channels_string = \
                ", ".join([f"<#{channel_id}> ({channel_id})" for channel_id in self.guild_prefs.anime_channels])

            await send_embed(f"Anime/Manga channels:\n{channels_string}.", self.channel,
                             reply_to=self.message)

        elif self.used_sub_command == "clear":
            if not self.guild_prefs.anime_channels:
                await send_embed(f"List of Anime/Manga channels already empty.", self.channel,
                                 reply_to=self.message)
                return
            await GuildPrefsComponent().clear_guild_anime_channels(self.guild)
            await send_embed(f"Anime/Manga channel list cleared.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.message)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Cleared list of Anime & Manga channels.")
