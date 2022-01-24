import asyncio
import re
from difflib import SequenceMatcher
from math import ceil

import disnake as discord
from actions import send_message, send_perm_error_message, send_embed, remove_reactions, \
    edit_message, edit_embed, delete_message_from_guild
from internal.bot_logging import log
from globals_.clients import discord_client
from commands.command_executor import CommandExecutor
from globals_ import variables
from globals_.constants import BotLogType, CommandType, MusicVCState, MusicVCLoopMode, HelpListingVisibility
from helpers import convert_seconds_to_numeric_time
from models.command import Command
from models.guild import GuildPrefs
from services.music_service import GuildMusicService


class MusicCommandExecutor(CommandExecutor):
    def __init__(self, message: discord.Message, command_name, guild_prefs: GuildPrefs = None):
        super().__init__(message, command_name, guild_prefs)
        self.author_voice_channel = None
        self.bot_voice_channel = None
        self.set_author_and_bot_voice_channels()
        self.command_object: Command = variables.music_commands_dict.get(command_name, Command(''))
        self.sub_commands: [] = self.command_object.sub_commands
        self.command_options, self.used_sub_command = None, None
        self.voice_client = None
        self.music_service: GuildMusicService = \
            variables.guild_music_services.get(self.guild.id) if self.guild else None
        self.player_channel = self.guild_prefs.music_channel if self.guild_prefs else None
        self.player_message = self.guild_prefs.music_player_message if self.guild_prefs else None
        self.using_music_channel = message.channel.id == guild_prefs.music_channel
        self.delete_after = 3 if self.using_music_channel else None
        self.delete_after_long = 5 if self.using_music_channel else None
        self.delete_after_longest = 15 if self.using_music_channel else None
        self.reply_to = None if self.using_music_channel else self.message
        asyncio.get_event_loop().create_task(self.log_command())

    async def log_command(self, level=BotLogType.MUSIC_COMMAND_RECEIVED):
        assumed_command = self.message_string_lowered.split(' ')[0][len(self.music_prefix):]
        assumed_command = \
            self.command_name if self.command_name else assumed_command if len(assumed_command) > 2 else None
        if not assumed_command:
            return
        channel_text = f"{self.channel}/{self.guild}" if self.guild else f"{self.author}"
        await log(
            f"'{assumed_command}' from {self.author}/{self.author.id}. Message: '{self.message_content}'."
            f" Channel: {channel_text}.", log_to_discord=False,
            level=level if self.command_name else BotLogType.UNRECOGNIZED_COMMAND_RECEIVED,
            guild_id=self.guild.id if self.guild else None)

    async def handle_incorrect_use(self, feedback="Incorrect use of command."):
        feedback += f"\nSee `{self.music_prefix}help {self.command_name}`."
        return await send_message(feedback, self.channel, reply_to=self.message,
                                  force_send_without_embed=True, delete_after=self.delete_after)

    async def routine_checks_fail(self, check_if_author_in_bot_voice_channel=False, check_for_music_channel=False):
        voice_channel = self.author_voice_channel
        has_perms, missing_perm, who = \
            await self.has_needed_permissions_for_command(command_type=CommandType.MUSIC,
                                                          voice_channel=voice_channel)
        if not has_perms:
            await send_perm_error_message(missing_perm, who, self.channel, reply_to=self.message,
                                          delete_after=self.delete_after)
            return True
        if check_if_author_in_bot_voice_channel and self.bot_voice_channel \
                and self.author not in self.bot_voice_channel.members:
            await send_embed("Join my voice channel first.", self.channel, delete_after=self.delete_after)
            return True
        if self.guild_prefs.music_channel and \
                self.guild.get_channel(self.guild_prefs.music_channel) and check_for_music_channel:
            if self.using_music_channel:
                await send_embed(f"Please use reactions above.", self.channel,
                                 delete_after=self.delete_after)
            else:
                await send_embed(f"Please use <#{self.guild_prefs.music_channel}>.", self.channel,
                                 delete_after=self.delete_after)
            return True
        return False

    async def handle_command_unrecognized(self):
        assumed_command = self.message_content.lower().split(' ')[0][len(self.prefix):].strip()
        closest_command = get_closest_command_if_exists(assumed_command)
        if not closest_command:
            return
        await log(f"Unrecognized command '{assumed_command}'. Suggested '{closest_command}'.", log_to_discord=False,
                  guild_id=self.guild.id)
        await send_embed(f"Hmm, did you mean `{self.music_prefix}{closest_command}`?"
                         f" Use `{self.music_prefix}help` to see all available commands.",
                         self.channel, reply_to=self.message, delete_after=self.delete_after)

    def set_author_and_bot_voice_channels(self):
        self.author_voice_channel = \
            self.author.voice.channel if self.guild and self.author.voice and self.author.voice.channel else None
        self.bot_voice_channel = \
            self.guild.me.voice.channel if self.guild and self.guild.me.voice \
            and self.guild.me.voice.channel and self.guild else None

    async def attempt_joining_vc_channel_of_author(self, send_already_joined_feedback=True):
        self.set_author_and_bot_voice_channels()
        if not self.author_voice_channel:
            await send_embed("You must join a voice channel first.", self.channel,
                             emoji='❌', color=0xFF522D, reply_to=self.message, delete_after=self.delete_after)
            return False
        if self.bot_voice_channel:
            if self.bot_voice_channel.id == self.author_voice_channel.id:
                if send_already_joined_feedback:
                    await send_embed("I'm already in your voice channel.", self.channel,
                                     delete_after=self.delete_after)
                return True
            elif len(self.bot_voice_channel.members) > 1:
                await send_embed("I'm already in a different voice channel.", self.channel,
                                 delete_after=self.delete_after)
                return False
        missing_permission = self.bot_can_connect_and_speak_in_vc(self.author_voice_channel)
        if missing_permission:
            await send_embed(f"I need the `{missing_permission}` permission "
                             f"on the voice channel for this command.", self.channel,
                             emoji='❌', color=0xFF522D, reply_to=self.message, delete_after=self.delete_after)
            return False
        self.voice_client = self.guild.voice_client or await self.author.voice.channel.connect()

        return True

    def bot_can_connect_and_speak_in_vc(self, voice_channel=None):
        if not voice_channel:
            voice_channel = self.author_voice_channel
        bot_member = self.channel.guild.me
        bot_permissions = voice_channel.permissions_for(bot_member)
        if bot_permissions.administrator:
            return
        if not bot_permissions.connect:
            return 'connect'
        if not bot_permissions.speak:
            return 'speak'
        if not bot_permissions.use_voice_activation:
            return 'use_voice_activation'

    def author_is_dj_or_is_alone_in_vc(self):
        return self.author_is_dj() or self.author_is_alone_in_vc()

    def author_is_dj(self):
        if self.guild.owner_id == self.author.id:
            return True
        for role in self.author.roles:
            if role.id in self.guild_prefs.dj_roles:
                return True
        return False

    def author_is_alone_in_vc(self):
        # not actually alone, can be only 2 people but you get the point
        return len([member for member in self.author_voice_channel.members if member.id != self.guild.me.id]) < 3

    async def subcommand_checks_fail(self, send_feedback_message=True):
        if not self.command_options_and_arguments:
            if send_feedback_message:
                # noinspection PyTypeChecker
                sub_commands_text = '`' + '` | `'.join(self.sub_commands) + '`'
                await self.handle_incorrect_use(feedback=f"You must use a sub-command"
                                                         f" with this command: {sub_commands_text}.")
            return True

        self.command_options = self.command_options_and_arguments_fixed.split(' ')
        self.used_sub_command = re.sub("[^A-Za-z]", "", self.command_options[0]).lower()

        if self.used_sub_command not in self.sub_commands:
            if send_feedback_message:
                sub_commands_text = '`' + '` | `'.join(self.sub_commands) + '`'
                await self.handle_incorrect_use(feedback=f"You must use a sub-command"
                                                         f" with this command: {sub_commands_text}.")
            return True

        return False

    def initiate_guild_music_service(self):
        if not self.voice_client:
            self.voice_client = self.guild.voice_client
        variables.guild_music_services[self.guild.id] = GuildMusicService(guild_id=self.guild.id,
                                                                          voice_channel_id=self.author_voice_channel.id,
                                                                          voice_client=self.voice_client,
                                                                          text_channel=self.channel)
        variables.guild_music_services[self.guild.id].state = MusicVCState.CONNECTED
        self.music_service: GuildMusicService = variables.guild_music_services[self.guild.id]
        asyncio.get_event_loop().create_task(self.music_service.initiate_dc_countdown())
        return variables.guild_music_services[self.guild.id]

    def delete_guild_music_service(self):
        if self.guild.id in variables.guild_music_services:
            variables.guild_music_services.pop(self.guild.id)
        self.music_service = None

    async def hold_vote(self, vote_question):
        """
        :param vote_question:
        :return: vote_passed, send_feedback
        """
        if not self.channel.permissions_for(self.guild.me).add_reactions:
            return False, True
        count_of_potential_voters = len([member for member in self.author_voice_channel.members
                                         if member.id != self.guild.me.id])
        votes_needed = ceil(count_of_potential_voters / 2)
        votes = 1
        delete_after = votes_needed * 15 if votes_needed < 7 else 90 if self.using_music_channel else None
        sent_message = await send_embed(f"{vote_question} ({votes}/{votes_needed})", self.channel,
                                        delete_after=delete_after)
        await sent_message.add_reaction('✅')
        while votes < votes_needed:
            def check_react(reaction, user):
                if user.id in [sent_message.author.id, self.author.id]:
                    return False
                if user.id not in [member.id for member in self.bot_voice_channel.members]:
                    return False
                if reaction.message.id != sent_message.id:
                    return False
                if str(reaction.emoji) == "✅":
                    return True
                return False

            try:
                _, _ = await discord_client.wait_for("REACTION_ADD",
                                                     check=check_react,
                                                     timeout=15 if self.using_music_channel else 300)
            except asyncio.TimeoutError:
                sent_message = await self.channel.fetch_message(sent_message.id)
                if sent_message:
                    if self.using_music_channel:
                        await delete_message_from_guild(message=sent_message)
                    else:
                        await remove_reactions(sent_message)
                        await edit_message(sent_message, content="Not enough votes :(")
                return False, False
            sent_message = await self.channel.fetch_message(sent_message.id)
            reactions_count = [reaction.count for reaction in sent_message.reactions if str(reaction.emoji) == "✅"]
            new_votes = reactions_count[0] if reactions_count else votes
            if votes != new_votes:
                votes = new_votes
                await edit_embed(original_message=sent_message,
                                 message=f"{vote_question} ({votes}/{votes_needed})")
        if self.using_music_channel:
            await delete_message_from_guild(message=sent_message)
        else:
            await remove_reactions(sent_message)
        return True, False

    async def _send_final_feedback_message_for_track_add(self, track_info):
        if not track_info:
            return await send_embed(f"Couldn't play this track.", self.channel,
                                    emoji='❕', reply_to=self.reply_to, delete_after=self.delete_after)
        time_left = self.music_service.calculate_time_to_queue_end() - track_info['duration']
        fields_values = {"Duration": track_info['duration_text']}
        if self.music_service.loop_mode != MusicVCLoopMode.ONE and \
                self.music_service.current_track != track_info:
            fields_values["Wait time"] = convert_seconds_to_numeric_time(time_left)
        await send_embed(f"Added `{track_info['title']}` to queue.",
                         self.channel, reply_to=self.reply_to, delete_after=self.delete_after,
                         thumbnail_url=track_info['tiny_thumbnail_url'], fields_values=fields_values)


def get_closest_command_if_exists(assumed_command):
    for command in variables.music_commands_names:
        if len(command) > 2:
            if SequenceMatcher(None, assumed_command, command).ratio() >= 0.75 and \
                    variables.music_commands_dict.get(command,
                                                      Command('')).show_on_listing != HelpListingVisibility.HIDE:
                return command
    return None
