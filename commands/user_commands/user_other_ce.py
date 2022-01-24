from actions import send_message, send_embed
from globals_.clients import discord_client
from commands.user_command_executor import UserCommandExecutor
from globals_.constants import BOT_OWNER_ID, BOT_NAME, BOT_INVITE


class OtherUserCommandExecutor(UserCommandExecutor):

    def __init__(self, message, command_name, guild_prefs=None):
        super().__init__(message=message, command_name=command_name, guild_prefs=guild_prefs)

    async def check_for_section_enabled(self):
        return True

    async def handle_command_feedback(self):
        if await self.routine_checks_fail():
            return

        if not self.command_options_and_arguments:
            await self.handle_incorrect_use(feedback="Type the feedback you'd like to send!.")
            return
        owner = discord_client.get_user(BOT_OWNER_ID)
        await send_message(f"Received feedback from **{self.author}** ({self.author.id}) "
                           f"in **{self.channel}**/**{self.guild}** "
                           f"({self.guild.id if self.guild else None}).\n\n"
                           f"```\n{self.command_options_and_arguments}\n```", owner)
        try:
            await self.message.add_reaction('👌')
        except:
            pass

    async def handle_command_invite(self):
        if await self.routine_checks_fail():
            return

        invite_message = f"Follow this link to invite {BOT_NAME} to your server {BOT_INVITE}"
        sent_message = await send_embed(invite_message, self.channel, reply_to=self.message, bold=False)
        if sent_message is None:
            await send_message(invite_message, self.author)
