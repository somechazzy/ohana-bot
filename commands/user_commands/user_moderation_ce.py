from commands.user_command_executor import UserCommandExecutor
from actions import mute_member, unmute_member, \
    kick_member, ban_member, send_hierarchy_error_message, send_embed
from helpers import can_moderate_target_member, get_id_from_text_if_exists_otherwise_get_author_id, \
    get_duration_and_reason_if_exist


class ModerationUserCommandExecutor(UserCommandExecutor):
    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)
        self.victim = None

    async def check_for_section_enabled(self):
        if self.is_dm:
            await send_embed(f"Moderation commands are only available on servers.", self.channel)
            return False
        if not self.guild_prefs.moderation_commands_enabled:
            await send_embed(f"Sorry, but Moderation commands were disabled by an admin.", self.channel,
                             emoji='💔', color=0xFF522D, reply_to=self.message)
            return False
        return True

    async def handle_command_mute(self):
        if await self.routine_checks_fail():
            return

        if await self.routine_moderation_checks_fail(check_bot_hierarchy=False):
            return

        message_list = self.command_options_and_arguments_fixed.split(" ", maxsplit=1)
        optional_arguments_text = message_list[1] if len(message_list) > 1 else ""

        duration_minutes, reason = get_duration_and_reason_if_exist(optional_arguments_text)
        if duration_minutes > 40320:
            return await send_embed("Duration can be 28 days at most.", self.channel, emoji='❌',
                                    color=0xFF522D)
        await mute_member(self.victim, self.guild, duration_minutes, send_on_channel=True,
                          channel=self.channel, reason=reason, moderator=self.author)

    async def handle_command_unmute(self):
        if await self.routine_checks_fail():
            return

        if await self.routine_moderation_checks_fail(check_bot_hierarchy=False):
            return

        await unmute_member(self.victim, self.guild, send_on_channel=True,
                            channel=self.channel, moderator=self.author)

    async def handle_command_kick(self):
        if await self.routine_checks_fail():
            return

        if await self.routine_moderation_checks_fail():
            return

        message_list = self.command_options_and_arguments_fixed.split(" ", maxsplit=1)
        reason = message_list[1] if len(message_list) > 1 else "Not provided"

        await kick_member(self.victim, self.guild, reason=reason, moderator=self.author)
        await send_embed(f"User {self.victim} has been kicked.", self.channel, emoji='✅', color=0x0AAC00,
                         reply_to=self.message)

    async def handle_command_ban(self, delete_messages=False):
        if await self.routine_checks_fail():
            return

        if await self.routine_moderation_checks_fail():
            return

        message_list = self.command_options_and_arguments_fixed.split(" ", maxsplit=1)
        reason = message_list[1] if len(message_list) > 1 else "Not provided"

        await ban_member(self.victim, self.guild, reason=reason, delete_messages=delete_messages, moderator=self.author)
        await send_embed(f"User {self.victim} has been banned.", self.channel, emoji='✅', color=0x0AAC00,
                         reply_to=self.message)

    async def handle_command_bandel(self):
        return await self.handle_command_ban(delete_messages=True)

    async def routine_moderation_checks_fail(self, check_victim=True, check_bot_hierarchy=True):
        if not self.command_options_and_arguments:
            await self.handle_incorrect_use(feedback="You need to provide a mention or an ID.")
            return True

        text = self.command_options_and_arguments_fixed.split(' ')[0]
        discord_id, not_author = \
            get_id_from_text_if_exists_otherwise_get_author_id(text, self.author)
        if not not_author:
            await self.handle_incorrect_use(feedback="You need to provide a mention or an ID.")
            return True
        if check_victim:
            if int(discord_id) == self.author.id:
                await send_embed(f"You can't do that to yourself.", self.channel, emoji='❌',
                                 color=0xFF522D,
                                 reply_to=self.message)
                return True
            self.victim = self.guild.get_member(int(discord_id))
            if not self.victim:
                await send_embed(f"Can't find member.", self.channel, emoji='❌',
                                 color=0xFF522D,
                                 reply_to=self.message)
                return True
            can, who = can_moderate_target_member(self.author, self.victim, check_bot_hierarchy=check_bot_hierarchy)
            if not can:
                await send_hierarchy_error_message(who, self.channel, reply_to=self.message)
                return True
        return False
