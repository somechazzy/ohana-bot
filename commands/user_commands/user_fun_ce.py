import random
import re

from auto_moderation.auto_moderator import get_banned_words_for
from commands.user_command_executor import UserCommandExecutor
from globals_ import variables
from globals_.constants import UserCommandSection
from actions import delete_message_from_guild, send_embed, send_message
from helpers import get_uwufied_text
from embed_factory import make_snipe_embed


class FunUserCommandExecutor(UserCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)

    async def check_for_section_enabled(self):
        if self.is_dm:
            return True
        if not self.guild_prefs.fun_commands_enabled:
            if int(self.guild_prefs.spam_channel) == self.message.channel.id:
                return True
            await send_embed(f"Sorry, but an admin has disabled {UserCommandSection.FUN} commands.",
                             self.message.channel,
                             emoji='💔', color=0xFF522D, reply_to=self.message)
            return False
        return True

    async def handle_command_uwufy(self, delete=False):
        if await self.routine_checks_fail():
            return

        if delete:
            await delete_message_from_guild(self.message, "used \'uwufydel\' command")
        if not self.command_options_and_arguments:
            await self.handle_incorrect_use(feedback="Tell me what to uwufy ʕ￫ᴥ￩ʔ")
            return

        content = str(self.message.clean_content).split(' ', 1)[1]
        uwufied_text = get_uwufied_text(content)
        await send_message(uwufied_text, self.channel, reply_to=self.message)

    async def handle_command_uwufydel(self):
        return await self.handle_command_uwufy(delete=True)

    async def handle_command_snipe(self):
        if await self.routine_checks_fail():
            return
        sniped_message = variables.channel_id_sniped_message_map.get(self.channel.id)
        if not sniped_message or self.is_dm:
            return await send_embed("Nothing to snipe.", self.channel)
        member = self.guild.get_member(sniped_message.get('author_id'))
        if not member or self.has_banned_word(sniped_message.get('content')):
            return await send_embed("Nothing to snipe.", self.channel)
        embed = make_snipe_embed(sniped_message, member)
        await send_message(message="", embed=embed, channel=self.channel, reply_to=self.message)
        variables.channel_id_sniped_message_map[self.channel.id] = None
        if random.Random().randint(1, 7) == 4:
            await send_embed(message=f"Tip: you can disable sniping using"
                                     f" `{self.admin_prefix}disable fun`", channel=self.channel)

    def has_banned_word(self, content):
        content = str(content).lower()
        content_no_spaces = content.replace(" ", "")
        banned_words_full, banned_words_partial, banned_words_regex = get_banned_words_for(self.guild_prefs)
        words_used = []

        def remove_word(_word):
            while _word in words_used:
                words_used.remove(_word)

        for word in banned_words_partial:
            if word in content_no_spaces:
                words_used.append(word)

        content_list = re.split("[^A-Za-z]", content)
        for word in content_list:
            if word in banned_words_full:
                words_used.append(word)

        for regex in banned_words_regex:
            words_used_regex = re.finditer(regex, content, re.IGNORECASE)
            for word in words_used_regex:
                words_used.append(word.group())

        if len(words_used) > 0:
            for command_name in variables.commands_names:
                remove_word(command_name)

        return words_used
