import asyncio
import traceback
from math import ceil
import disnake as discord
from actions import send_embed, edit_embed, \
    delete_message_from_guild
from internal.bot_logging import log
from globals_.clients import discord_client
from globals_ import variables
from globals_.constants import BotLogType, \
    VOICE_PERMISSIONS, MusicVCState, CUSTOM_EMOJI_PLAYER_ACTION_MAP, DEFAULT_EMOJI_PLAYER_ACTION_MAP
from services.music_service import GuildMusicService


class MusicPlayerReactionHandler:
    def __init__(self, channel, message_id, emoji, member):
        self.channel = channel
        self.message_id = message_id
        self.emoji: discord.Emoji = emoji
        self.author: discord.Member = member
        self.guild: discord.Guild = channel.guild
        self.guild_prefs = variables.guilds_prefs[self.guild.id]
        self.music_service: GuildMusicService = variables.guild_music_services.get(self.guild.id)
        self.author_voice_channel = \
            self.author.voice.channel if self.author.voice and self.author.voice.channel else None
        self.bot_voice_channel = \
            self.guild.me.voice.channel if self.guild.me.voice and self.guild.me.voice.channel else None
        self.command_name = self.voice_client = None

    async def handle(self):
        action = ""
        if self.emoji.id and CUSTOM_EMOJI_PLAYER_ACTION_MAP.get(self.emoji.id):
            action = CUSTOM_EMOJI_PLAYER_ACTION_MAP.get(self.emoji.id)
        elif not self.emoji.id and DEFAULT_EMOJI_PLAYER_ACTION_MAP.get(str(self.emoji)):
            action = DEFAULT_EMOJI_PLAYER_ACTION_MAP.get(str(self.emoji))
        if action:
            if self.music_service and await self.music_service.are_reactions_on_cooldown():
                return
            action_handler = getattr(self, f"_handle_{action.lower()}")
            try:
                await action_handler()
            except Exception as e:
                await log(f"Error encountered while handling music react: {e}\n{traceback.format_exc()}",
                          level=BotLogType.BOT_ERROR)
        return await self._remove_member_react()

    async def _remove_member_react(self):
        try:
            player_message = self.channel.get_partial_message(self.message_id)
            await player_message.remove_reaction(emoji=self.emoji, member=self.author)
        except:
            await send_embed("Couldn't remove user's reaction from the player text. "
                             "Please make sure I have the Manage Messages permission in this channel!",
                             self.channel, delete_after=10, emoji='❌', color=0xFF522D)

    async def _handle_join(self):
        self.command_name = 'join'
        if await self._routine_checks_fail():
            return

        if not self.bot_voice_channel and self.guild.id in variables.guild_music_services:
            variables.guild_music_services[self.guild.id].voice_client = None
            del variables.guild_music_services[self.guild.id]
            await self._delete_guild_music_service()

        if not await self._attempt_joining_vc_channel_of_author():
            return
        if not self.music_service:
            self._initiate_guild_music_service()
        await self.music_service.refresh_player()

    async def _handle_leave(self):
        self.command_name = 'leave'
        if await self._routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return

        if not self.bot_voice_channel:
            return await send_embed("I'm not currently in any voice channel.", self.channel,
                                    emoji='❌', color=0xFF522D, delete_after=3)
        if not self._author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self._hold_vote("Leave VC?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, delete_after=3)
                return

        if self.guild.voice_client:
            await self.guild.voice_client.disconnect(force=True)
        else:
            channel = await self.author_voice_channel.connect()
            await channel.disconnect()

        await self._delete_guild_music_service()

    async def _handle_resume_pause(self):
        self.command_name = 'resume'
        if await self._routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.music_service:
            return await send_embed("Nothing to resume", self.channel, delete_after=3)
        action = 'resume' if self.music_service.voice_client.is_paused() else 'pause'
        if not self._author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self._hold_vote(f"{action.capitalize()} playback?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, delete_after=3)
                return
        if action == 'resume':
            self.music_service.resume_playback()
        else:
            self.music_service.pause_playback()
        await self.music_service.refresh_player()

    async def _handle_refresh(self):
        if not self.music_service:
            return
        await self.music_service.refresh_player()

    async def _handle_skip(self):
        self.command_name = 'skip'
        if await self._routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.music_service or not self.music_service.queue:
            return await send_embed("Nothing to skip", self.channel, delete_after=3)
        if not self._author_is_dj_or_is_alone_in_vc():
            track_before_vote = self.music_service.current_track
            vote_passed, send_feedback = await self._hold_vote("Skip current track?")
            track_after_vote = self.music_service.current_track
            if not vote_passed or not track_before_vote == track_after_vote:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, delete_after=3)
                return
        self.music_service.skip_current_track()

    async def _handle_shuffle(self):
        self.command_name = 'shuffle'
        if await self._routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.music_service or not self.music_service.queue:
            return await send_embed("Nothing to shuffle", self.channel, delete_after=3)
        if not self._author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self._hold_vote("Shuffle queue?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, delete_after=3)
                return

        self.music_service.shuffle_queue()
        await self.music_service.refresh_player()

    async def _handle_loop(self):
        self.command_name = 'shuffle'
        if await self._routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.music_service or not self.music_service.queue:
            return await send_embed("Nothing to loop.", self.channel, delete_after=3)

        if not self._author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self._hold_vote("Change loop mode?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, delete_after=3)
                return
        self.music_service.change_loop_mode(next_mode=None)
        await self.music_service.refresh_player()

    async def _handle_favorite(self):
        return await send_embed("Favorites feature coming soon!", self.channel, delete_after=3)

    async def _handle_previous(self):
        if not self.music_service or not self.music_service.queue:
            return
        await self.music_service.refresh_player(page_adjustment=-1)

    async def _handle_next(self):
        if not self.music_service or not self.music_service.queue:
            return
        await self.music_service.refresh_player(page_adjustment=+1)

    async def _attempt_joining_vc_channel_of_author(self, send_already_joined_feedback=True):
        if not self.author_voice_channel:
            await send_embed("You must join a voice channel first.", self.channel,
                             emoji='❌', color=0xFF522D, delete_after=3)
            return False
        if self.bot_voice_channel:
            if self.bot_voice_channel.id == self.author_voice_channel.id:
                if send_already_joined_feedback:
                    await send_embed("I'm already in your voice channel.", self.channel, delete_after=3)
                return True
            elif len(self.bot_voice_channel.members) > 1:
                await send_embed("I'm already in a different voice channel.", self.channel, delete_after=3)
                return False
        missing_permission = self._bot_can_connect_and_speak_in_vc(self.author_voice_channel)
        if missing_permission:
            await send_embed(f"I need the `{missing_permission}` permission "
                             f"on the voice channel for this command.", self.channel,
                             emoji='❌', color=0xFF522D, delete_after=3)
            return False
        self.voice_client = self.guild.voice_client or await self.author.voice.channel.connect()
        return True

    def _initiate_guild_music_service(self):
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

    def _bot_can_connect_and_speak_in_vc(self, voice_channel=None):
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

    def _author_is_dj_or_is_alone_in_vc(self):
        return self._author_is_dj() or self._author_is_alone_in_vc()

    def _author_is_dj(self):
        if self.guild.owner_id == self.author.id:
            return True
        for role in self.author.roles:
            if role.id in self.guild_prefs.dj_roles:
                return True
        return False

    def _author_is_alone_in_vc(self):
        return len([member for member in self.author_voice_channel.members if member.id != self.guild.me.id]) < 3

    async def _hold_vote(self, vote_question):
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
        delete_after = votes_needed * 15 if votes_needed < 7 else 90
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
                                                     timeout=15)
            except asyncio.TimeoutError:
                sent_message = await self.channel.fetch_message(sent_message.id)
                await delete_message_from_guild(message=sent_message)
                return False, False
            sent_message = await self.channel.fetch_message(sent_message.id)
            reactions_count = [reaction.count for reaction in sent_message.reactions if str(reaction.emoji) == "✅"]
            new_votes = reactions_count[0] if reactions_count else votes
            if votes != new_votes:
                votes = new_votes
                await edit_embed(original_message=sent_message,
                                 message=f"{vote_question} ({votes}/{votes_needed})")
        await delete_message_from_guild(message=sent_message)
        return True, False

    async def _delete_guild_music_service(self):
        if self.guild.id in variables.guild_music_services:
            await self.music_service.refresh_player()
            variables.guild_music_services.pop(self.guild.id)
        self.music_service = None

    async def _routine_checks_fail(self, check_if_author_in_bot_voice_channel=False):
        voice_channel = self.author_voice_channel
        has_perms, missing_perm, who = \
            await self._has_needed_permissions_for_command(voice_channel=voice_channel)
        if not has_perms:
            pronoun = "I" if who.lower().__eq__("bot") else "You"
            await send_embed(f"{pronoun} need the {missing_perm} permission for this action :(", self.channel,
                             emoji='❌', color=0xFF522D, delete_after=3)
            return True
        if check_if_author_in_bot_voice_channel and self.bot_voice_channel \
                and self.author not in self.bot_voice_channel.members:
            await send_embed("Join my voice channel first.", self.channel, delete_after=3)
            return True
        return False

    async def _has_needed_permissions_for_command(self, voice_channel=None):
        member_has_perm, member_missing_perm = await self._member_has_needed_permissions_for_command()
        if not member_has_perm:
            return False, member_missing_perm, "member"
        bot_has_perm, bot_missing_perm = await self._bot_has_needed_permissions_for_command(voice_channel=voice_channel)
        if not bot_has_perm:
            return False, bot_missing_perm, "bot"
        return True, "None", "None"

    async def _bot_has_needed_permissions_for_command(self, voice_channel=None):
        bot_member = self.channel.guild.me
        bot_permissions = self.channel.permissions_for(bot_member)
        bot_permissions_in_voice = voice_channel.permissions_for(bot_member) if voice_channel else None
        command = variables.music_commands_dict.get(self.command_name)
        if not command.bot_perms:
            return True, "None"
        if not command:
            await log(f"Command can't be recognized. Command: {self.command_name}",
                      level=BotLogType.BOT_ERROR)
            return False, "Unknown"
        if bot_permissions.administrator:
            return True, "None"
        for perm in command.bot_perms:
            if perm in VOICE_PERMISSIONS:
                if not voice_channel:
                    continue
                if hasattr(bot_permissions_in_voice, perm):
                    if not getattr(bot_permissions_in_voice, perm):
                        return False, perm
                else:
                    await log(f"Command requires a permission that can't be recognized. Permission: {perm}",
                              level=BotLogType.BOT_ERROR)
                    return True, "None"
            else:
                if hasattr(bot_permissions, perm):
                    if not getattr(bot_permissions, perm):
                        return False, perm
                else:
                    await log(f"Command requires a permission that can't be recognized. Permission: {perm}",
                              level=BotLogType.BOT_ERROR)
                    return True, "None"
        return True, "None"

    async def _member_has_needed_permissions_for_command(self):
        member_permissions = self.channel.permissions_for(self.author)
        command = variables.music_commands_dict.get(self.command_name)
        if not command.member_perms:
            return True, "None"
        if not command:
            await log(f"Command can't be recognized. Command: {self.command_name}", level=BotLogType.BOT_ERROR)
            return False, "Unknown"
        if member_permissions.administrator:
            return True, "None"
        for perm in command.member_perms:
            if hasattr(member_permissions, perm):
                if not getattr(member_permissions, perm):
                    return False, perm
            else:
                await log(f"Command requires a permission that can't be recognized. Permission: {perm}",
                          level=BotLogType.BOT_ERROR)
                return True, "None"
        return True, "None"
