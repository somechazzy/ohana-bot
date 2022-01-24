import asyncio
import json
import os
import traceback
from math import ceil
import disnake as discord
from actions import send_message, edit_message, send_embed, \
    delete_message_from_guild
from globals_.clients import discord_client
from internal.bot_logging import log_to_server, log
from commands.music_command_executor import MusicCommandExecutor
from globals_ import variables
from globals_.constants import DEFAULT_PLAYER_CHANNEL_EMBED_MESSAGE_CONTENT, PLAYER_HEADER_IMAGE, \
    CUSTOM_EMOJI_PLAYER_ACTION_MAP, DEFAULT_EMOJI_PLAYER_ACTION_MAP, MusicCommandSection, MusicVCState, GuildLogType, \
    BOT_COLOR
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from helpers import get_id_from_text, get_close_embed_view, get_main_help_views, build_path, get_history_embed_views
from embed_factory import make_initial_player_message_embed, make_main_music_help_embed, make_command_music_help_embed,\
    make_music_history_embed
from models.guild import GuildPrefs
from user_interactions import handle_general_close_embed, music_help_navigation, handle_history


class GeneralMusicCommandExecutor(MusicCommandExecutor):

    async def handle_command_help(self):
        if self.using_music_channel:
            return await self.handle_help_on_dms()
        if not self.command_options_and_arguments:
            view = get_main_help_views(MusicCommandSection)
            embed = make_main_music_help_embed(self.guild_prefs)
            sent_message = await send_message(None, self.channel, embed=embed,
                                              reply_to=self.reply_to, view=view)
            if sent_message is not None:
                await music_help_navigation(self.message, sent_message, embed, self.guild_prefs)
        else:
            embed = make_command_music_help_embed(self.message, self.guild_prefs)
            sent_message = await send_message(None, self.channel, embed=embed,
                                              reply_to=self.reply_to, view=get_close_embed_view())
            close_embed = await handle_general_close_embed(sent_message=sent_message, requested_by=self.author)
            if close_embed:
                await edit_message(sent_message, "Help embed closed.", reason=f"Closed help embed for some command",
                                   view=None)
                return

    async def handle_command_join(self):
        if await self.routine_checks_fail(check_for_music_channel=True):
            return

        if not self.bot_voice_channel and self.guild.id in variables.guild_music_services:
            variables.guild_music_services[self.guild.id].voice_client = None
            del variables.guild_music_services[self.guild.id]
            self.delete_guild_music_service()

        if not await self.attempt_joining_vc_channel_of_author():
            return
        if not self.music_service:
            self.initiate_guild_music_service()
        try:
            await self.message.add_reaction('✔')
        except:
            pass

    async def handle_command_leave(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True,
                                          check_for_music_channel=True):
            return
        if not self.bot_voice_channel:
            return await send_embed("I'm not currently in any voice channel.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.reply_to)
        if not self.author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self.hold_vote("Leave VC?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.reply_to)
                return

        if self.guild.voice_client:
            await self.guild.voice_client.disconnect(force=True)
        else:
            channel = await self.author_voice_channel.connect()
            await channel.disconnect()

        self.delete_guild_music_service()
        try:
            await self.message.add_reaction('✔')
        except:
            pass

    async def handle_command_dj(self):
        if await self.routine_checks_fail():
            return

        if await self.subcommand_checks_fail():
            return

        sub_command_options = self.command_options[1:]

        if self.used_sub_command == "add":
            self.guild_prefs = \
                await GuildPrefsComponent().validate_dj_roles_exist_and_remove_invalid_ones(self.guild_prefs)
            if len(self.guild_prefs.dj_roles) >= 10:
                await send_embed("Sorry! You already have the maximum of 10 DJ roles.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                 delete_after=self.delete_after)
                return
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a role ID to add.")
                return

            role_id = get_id_from_text(sub_command_options[0])
            if not role_id:
                await self.handle_incorrect_use(feedback="Provide me with a role ID to add.")
                return

            role = self.guild.get_role(int(role_id))

            if await self.role_checks_fail(role, check_if_assignable=False, delete_after=self.delete_after):
                return

            if int(role_id) in self.guild_prefs.dj_roles:
                await send_embed(f"`{role}` is already a DJ role.",
                                 self.channel, reply_to=self.reply_to, delete_after=self.delete_after)
                return
            await GuildPrefsComponent().add_guild_dj_role(self.guild, role_id)
            await send_embed(f"`{role}` has been added to list of DJ roles.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.reply_to,
                             delete_after=self.delete_after)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Added role to list of DJ roles.",
                                fields=["Role"],
                                values=[role])

        elif self.used_sub_command in ["remove", "delete"]:
            if not sub_command_options:
                await self.handle_incorrect_use(feedback="Provide me with a role ID to remove.")
                return

            role_id = get_id_from_text(sub_command_options[0])
            if int(role_id) not in self.guild_prefs.dj_roles:
                await send_embed("Role you entered is not a DJ role.",
                                 self.channel, emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                 delete_after=self.delete_after)
                return
            await GuildPrefsComponent().remove_guild_dj_role(self.guild, role_id)
            role = self.guild.get_role(int(role_id))
            if not role:
                role = "Unknown role"
            await send_embed(f"`{role}` has been removed from DJ roles.",
                             self.channel, emoji='✅', color=0x0AAC00, reply_to=self.reply_to,
                             delete_after=self.delete_after)
            await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                event="Removed role from list of DJ roles.",
                                fields=["Role"],
                                values=[role])

        elif self.used_sub_command == "show":
            if not self.guild_prefs.dj_roles:
                await send_embed(f"No DJ roles added yet.", self.channel, reply_to=self.reply_to,
                                 delete_after=self.delete_after)
                return

            roles_string = ", ".join([f"<@&{role_id}>" for role_id in self.guild_prefs.dj_roles
                                      if self.guild.get_role(int(role_id))])

            await send_embed(f"DJ roles:\n{roles_string}.", self.channel, reply_to=self.reply_to,
                             delete_after=self.delete_after_long)

        elif self.used_sub_command == "clear":
            if self.guild_prefs.dj_roles:
                await GuildPrefsComponent().clear_guild_dj_roles(self.guild)
                await send_embed(f"DJ role list cleared.",
                                 self.channel, emoji='✅', color=0x0AAC00, reply_to=self.reply_to,
                                 delete_after=self.delete_after)
                await log_to_server(self.guild, GuildLogType.SETTING_CHANGE, member=self.author,
                                    event="Cleared list of DJ roles.")
            else:
                await send_embed(f"No DJ roles added yet.", self.channel, reply_to=self.reply_to,
                                 delete_after=self.delete_after)

    async def handle_help_on_dms(self):
        if self.using_music_channel:
            await delete_message_from_guild(message=self.message, reason="Music channel text")
        if not self.command_options_and_arguments:
            view = get_main_help_views(MusicCommandSection)
            embed = make_main_music_help_embed(GuildPrefs(0, ''))
            sent_message = await send_message(None, self.author, embed=embed, view=view)
            if sent_message is not None:
                await music_help_navigation(self.message, sent_message, embed, GuildPrefs(0, ''))
        else:
            embed = make_command_music_help_embed(self.message, GuildPrefs(0, ''))
            await send_message(None, self.author, embed=embed)

    async def handle_command_notify(self):
        if self.player_channel:
            return await send_embed("Notifications aren't available due to player channel.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.reply_to)
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True,
                                          check_for_music_channel=True):
            return
        if not self.author_is_dj_or_is_alone_in_vc():
            return await send_embed("You need a DJ role for this action.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.reply_to)
        if not self.music_service:
            return await send_embed("Start a music session first!", self.channel)
        currently_enabled = self.music_service.change_notifications_enabled_state(text_channel=self.channel)
        if currently_enabled:
            return await send_embed(f"\"Now Playing...\" notifications enabled "
                                    f"to be sent in this channel.",
                                    self.channel, color=0x0AAC00, reply_to=self.reply_to)
        else:
            return await send_embed(f"\"Now Playing...\" notifications disabled in this channel. "
                                    f"You can use this command again to re-enable them in another channel.",
                                    self.channel, color=0x0AAC00, reply_to=self.reply_to)

    async def handle_command_history(self):
        if self.using_music_channel:
            return await send_embed("Please use this command in another channel.",
                                    self.channel, delete_after=3)
        guild_history_path = build_path(["media", "music", "history", f"{self.guild.id}.json"])
        history = {}
        if os.path.isfile(guild_history_path):
            with open(guild_history_path, 'r') as file:
                history = json.load(file)
        if not history:
            return await send_embed("No playback history for this server yet.", self.channel)
        history = list(history.values())
        history.reverse()
        page = 1
        embed = make_music_history_embed(guild=self.guild, history=history, page=page)
        view = get_history_embed_views(page=page, page_count=ceil(len(history) / 10), list_items=history[:10])
        sent_message = await send_message(message="", channel=self.channel, embed=embed, view=view)
        while True:
            chosen_index, page = await handle_history(sent_message=sent_message, requested_by=self.author,
                                                      original_embed=embed, history=history, page=page)
            if chosen_index is None:
                break

            self.delete_after = 3
            if not await self.attempt_joining_vc_channel_of_author(send_already_joined_feedback=False):
                continue
            self.delete_after = None

            if not self.bot_voice_channel and self.guild.id in variables.guild_music_services:
                variables.guild_music_services[self.guild.id].voice_client = None
                del variables.guild_music_services[self.guild.id]
                self.delete_guild_music_service()

            if not self.music_service:
                self.initiate_guild_music_service()

            url = history[(page - 1) * 10:(page - 1) * 10 + 10][chosen_index].get('url')
            track_info = await self.music_service.add_track_to_queue(url=url, added_by=self.author.id,
                                                                     refresh_player=True)
            if self.music_service.current_track != track_info:
                await self._send_final_feedback_message_for_track_add(track_info)
            await self.music_service.refresh_player()
            if self.music_service.state != MusicVCState.PLAYING:
                asyncio.get_event_loop().create_task(self.music_service.start_worker())
            sent_message = self.channel.get_partial_message(sent_message.id)
            embed = make_music_history_embed(guild=self.guild, history=history, page=page)
            view = get_history_embed_views(page=page, page_count=ceil(len(history) / 10), list_items=history[:10])
            await edit_message(sent_message, content="", embed=embed, view=view)

    async def handle_command_setup(self):
        if await self.routine_checks_fail():
            return
        if self.guild_prefs.music_channel and self.guild.get_channel(self.guild_prefs.music_channel):
            return await send_embed(f"Music player channel <#{self.guild_prefs.music_channel}> "
                                    f"already exists.",
                                    self.channel, reply_to=self.reply_to, delete_after=self.delete_after_long)
        try:
            music_channel = await self.setup_player_channel()
        except Exception as e:
            await send_embed("Failed at creating player channel. "
                             "Please make sure I have the necessary permissions.",
                             self.channel, emoji='❌', color=0xFF522D, reply_to=self.reply_to)
            await log(f"Failed at creating player channel in guild `{self.guild} ({self.guild.id})`.\n"
                      f"Error: {e}\nTraceback: {traceback.format_exc()}")
            return
        if self.music_service:
            self.music_service.music_channel = self.music_service.text_channel = music_channel
            self.music_service.player_message_id = self.guild_prefs.music_player_message
        return await send_embed(f"Music player channel {music_channel.mention} created!\n"
                                f"Feel free to move the channel and to rename it.", self.channel,
                                emoji='', color=0x0AAC00, reply_to=self.reply_to)

    async def setup_player_channel(self):
        music_channel = await self.guild.create_text_channel(name="🎸-player",
                                                             topic=f"Music Player - Not a Hydra ripoff",
                                                             reason="Music Player channel",
                                                             position=0)
        if not music_channel:
            raise
        header_embed = discord.Embed(color=BOT_COLOR)
        header_embed.set_image(url=PLAYER_HEADER_IMAGE)
        header_message = await send_message(message="",
                                            embed=header_embed,
                                            channel=music_channel)
        player_embed = make_initial_player_message_embed(self.guild)
        player_message = await send_message(message=DEFAULT_PLAYER_CHANNEL_EMBED_MESSAGE_CONTENT,
                                            embed=player_embed,
                                            channel=music_channel)
        if not header_message or not player_message:
            raise
        if music_channel.permissions_for(self.guild.me).use_external_emojis \
                and all(discord_client.get_emoji(emoji_id) for emoji_id in CUSTOM_EMOJI_PLAYER_ACTION_MAP.keys()):
            emoji_ids = CUSTOM_EMOJI_PLAYER_ACTION_MAP.keys()
            for emoji_id in emoji_ids:
                emoji = discord_client.get_emoji(emoji_id)
                await player_message.add_reaction(emoji)
        else:
            emojis = DEFAULT_EMOJI_PLAYER_ACTION_MAP.keys()
            for emoji in emojis:
                await player_message.add_reaction(emoji)
        await GuildPrefsComponent().set_guild_music_channel(guild=self.guild, channel_id=music_channel.id)
        await GuildPrefsComponent().set_guild_music_header_message(guild=self.guild, message_id=header_message.id)
        await GuildPrefsComponent().set_guild_music_player_message(guild=self.guild, message_id=player_message.id)
        return music_channel
