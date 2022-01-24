import re
from actions import send_message, send_embed
from commands.music_command_executor import MusicCommandExecutor
from globals_.constants import MusicVCLoopMode
from helpers import get_pagination_views
from embed_factory import make_music_queue_embed
from user_interactions import handle_music_queue


class QueueMusicCommandExecutor(MusicCommandExecutor):

    async def handle_command_queue(self):
        if self.using_music_channel:
            return await send_embed("Use queue above and navigate using arrows, "
                                    "or use this command in a different channel.", self.channel,
                                    delete_after=self.delete_after_long)
        if await self.routine_checks_fail():
            return

        if not self.music_service:
            return await send_embed(f"Nothing queued.", self.channel,
                                    emoji='❕', reply_to=self.message)
        if not self.music_service.queue:
            return await send_embed(f"Queue empty.", self.channel,
                                    emoji='❕', reply_to=self.message)

        page = self.command_options_and_arguments_fixed.split(" ")[0] \
            if self.command_options_and_arguments_fixed else '1'
        page = int(page) if page.isdigit() else 1
        page_count = len(self.music_service.queue)
        if page > page_count or page < 1:
            page = 1
        embed = make_music_queue_embed(guild=self.guild, queue=self.music_service.queue, page=page,
                                       currently_playing_index=self.music_service.currently_played_track_index)
        view = get_pagination_views(page, page_count)
        sent_message = await send_message(message=None, channel=self.channel,
                                          embed=embed, reply_to=self.message, view=view)

        await handle_music_queue(sent_message=sent_message, page=page, requested_by=self.author)

    async def handle_command_clear(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self.hold_vote("Clear queue?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                     delete_after=self.delete_after)
                return
        if not self.music_service:
            return
        if not self.music_service.queue:
            return await send_embed(f"Queue empty.", self.channel,
                                    emoji='❕', reply_to=self.reply_to, delete_after=self.delete_after)
        await self.music_service.clear_queue()
        await send_embed(f"Queue cleared.", self.channel, reply_to=self.reply_to,
                         delete_after=self.delete_after)

    async def handle_command_move(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self.hold_vote("Move track?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.message,
                                     delete_after=self.delete_after)
                return
        if not self.music_service:
            return
        elif not self.music_service.queue or len(self.music_service.queue) < 3:
            return await send_embed("Nothing to move.", self.channel, reply_to=self.message,
                                    delete_after=self.delete_after)

        indices_string = re.split("[^0-9]", self.command_options_and_arguments_fixed)
        indices = [int(index) - 1 for index in indices_string if index.isdigit()]
        if len(indices) != 2:
            return await send_embed("Please provide me with 2 numbers.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.message,
                                    delete_after=self.delete_after)
        for index in indices:
            if any([index < 0, index >= len(self.music_service.queue)]):
                return await send_embed("Track number not on the queue!", self.channel,
                                        emoji='❌', color=0xFF522D, reply_to=self.message,
                                        delete_after=self.delete_after)
            if index == self.music_service.currently_played_track_index:
                return await send_embed("Can't move the currently playing track.", self.channel,
                                        emoji='❌', color=0xFF522D, reply_to=self.message,
                                        delete_after=self.delete_after)

        if indices[0] == indices[1]:
            return await send_embed("Provide me with different numbers.", self.channel,
                                    emoji='🙄', reply_to=self.message, delete_after=self.delete_after)
        track_title = await self.music_service.move_track(track_index=indices[0], target_index=indices[1])
        return await send_embed(f"Moved `{track_title}` to position {indices[1] + 1}.", self.channel,
                                delete_after=self.delete_after)

    async def handle_command_skip(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True, check_for_music_channel=True):
            return
        if not self.music_service:
            return
        elif not self.music_service.queue:
            await send_embed("Nothing to skip.", self.channel, reply_to=self.message)
        if not self.author_is_dj_or_is_alone_in_vc():
            track_before_vote = self.music_service.current_track
            vote_passed, send_feedback = await self.hold_vote("Skip current track?")
            track_after_vote = self.music_service.current_track
            if not vote_passed or not track_before_vote == track_after_vote:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.message)
                return
        self.music_service.skip_current_track()
        return await send_embed("Skipped track.", self.channel)

    async def handle_command_loop(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True, check_for_music_channel=True):
            return
        await self.subcommand_checks_fail(send_feedback_message=False)
        if not self.music_service:
            return
        elif not self.music_service.queue:
            await send_embed("Nothing to loop.", self.channel, reply_to=self.message)
        if not self.author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self.hold_vote("Change loop mode?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.message)
                return

        next_mode = self.music_service.change_loop_mode(next_mode=self.used_sub_command)
        feedback_message = "All tracks will be looped" if next_mode == MusicVCLoopMode.ALL \
            else "Current track will be looped" if next_mode == MusicVCLoopMode.ONE \
            else "Nothing will be looped"
        return await send_embed(f"Loop mode changed to `{next_mode}`. {feedback_message}.", self.channel)

    async def handle_command_shuffle(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True, check_for_music_channel=True):
            return
        if not self.music_service or not self.music_service.queue or len(self.music_service.queue) < 2:
            return await send_embed("Nothing to shuffle.", self.channel,
                                    emoji='❕', reply_to=self.message)
        if not self.author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self.hold_vote("Shuffle queue?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.message)
                return

        self.music_service.shuffle_queue()
        return await send_embed("Queue shuffled.", self.channel)

    async def handle_command_remove(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.music_service:
            return
        elif not self.music_service.queue or len(self.music_service.queue) < 2:
            return await send_embed("Nothing to remove.", self.channel, reply_to=self.reply_to,
                                    delete_after=self.delete_after)
        index = self.command_options_and_arguments_fixed.split(' ')[0]
        if not index.isdigit():
            return await send_embed("Please provide me with the track number to remove.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                    delete_after=self.delete_after)
        index = int(index) - 1
        if not self.author_is_dj_or_is_alone_in_vc() \
                and not self.author.id == self.music_service.queue[index]['added_by']:
            vote_passed, send_feedback = await self.hold_vote("Remove track?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                     delete_after=self.delete_after)
                return
        if any([index < 0, index >= len(self.music_service.queue)]):
            return await send_embed("Track number not on the queue!", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.reply_to,
                                    delete_after=self.delete_after)
        removed_title = await self.music_service.remove_track(index=index)
        return await send_embed(f"Removed `{removed_title}`.", self.channel, reply_to=self.reply_to,
                                delete_after=self.delete_after)

    async def handle_command_skipto(self):
        if await self.routine_checks_fail(check_if_author_in_bot_voice_channel=True):
            return
        if not self.author_is_dj_or_is_alone_in_vc():
            vote_passed, send_feedback = await self.hold_vote("Skip track(s)?")
            if not vote_passed:
                if send_feedback:
                    await send_embed("You need DJ role for this.", self.channel,
                                     emoji='❌', color=0xFF522D, reply_to=self.message,
                                     delete_after=self.delete_after)
                return
        if not self.music_service or not self.music_service.queue or len(self.music_service.queue) < 2:
            return await send_embed("Nothing to skip to.", self.channel, reply_to=self.message,
                                    delete_after=self.delete_after)
        index = self.command_options_and_arguments_fixed.split(' ')[0]
        if not index.isdigit():
            return await send_embed("Please provide me with the track number to skip to.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.message,
                                    delete_after=self.delete_after)
        index = int(index) - 1
        if any([index < 0, index >= len(self.music_service.queue)]):
            return await send_embed("Track number not on the queue!", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.message,
                                    delete_after=self.delete_after)
        if index == self.music_service.currently_played_track_index:
            return await send_embed("Can't skip to the currently playing track.", self.channel,
                                    emoji='❌', color=0xFF522D, reply_to=self.message,
                                    delete_after=self.delete_after)
        track_info = self.music_service.skip_to_track(index=index)
        return await send_embed(f"Skipped to `{track_info['title']}`.", self.channel,
                                delete_after=self.delete_after)
