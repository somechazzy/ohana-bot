"""
Blueprint for reminder user slash commands. All commands here are prefixed with `/remind`.
"""
import discord
from discord import app_commands
from discord.app_commands import allowed_installs, allowed_contexts
from discord.ext.commands import GroupCog

from bot.slashes.user_slashes.reminder_user_slashes import RemindUserSlashes
from constants import CommandGroup
from strings.commands_strings import UserSlashCommandsStrings


@allowed_installs(users=True, guilds=True)
@allowed_contexts(guilds=True, dms=True, private_channels=True)
class RemindUserBlueprint(GroupCog, group_name="remind"):
    ME = app_commands.command(name="me",
                              description=UserSlashCommandsStrings.REMIND_ME_DESCRIPTION,
                              extras={"group": CommandGroup.REMINDER,
                                      "listing_priority": 1})
    SOMEONE = app_commands.command(name="someone",
                                   description=UserSlashCommandsStrings.REMIND_SOMEONE_DESCRIPTION,
                                   extras={"group": CommandGroup.REMINDER,
                                           "listing_priority": 2})
    LIST = app_commands.command(name="list",
                                description=UserSlashCommandsStrings.REMIND_LIST_DESCRIPTION,
                                extras={"group": CommandGroup.REMINDER,
                                        "listing_priority": 3})

    @ME
    async def me(self, interaction: discord.Interaction, when: str, what: str):
        """Remind me of something at a specific time

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        when: str
            When to remind you (Ex: 12h, 1d6h, 1h30m, 1w3d)
        what: str
            What to remind you of
        """

        await RemindUserSlashes(interaction=interaction).me(when=when, what=what)

    @SOMEONE
    @app_commands.checks.cooldown(1, 30, key=lambda i: i.user.id)
    async def someone(self,
                      interaction: discord.Interaction,
                      who: discord.Member | discord.User,
                      when: str,
                      what: str):
        """Remind someone of something at a specific time

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        who: discord.Member | discord.User
            Member to remind (you can enter a user ID)
        when: str
            When to remind them (Ex: 12h, 1d6h, 1h30m, 1w3d)
        what: str
            What to remind them of
        """

        await RemindUserSlashes(interaction=interaction).someone(who=who, when=when, what=what)

    @LIST
    async def list(self, interaction: discord.Interaction):
        """List & manage all of your reminders

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        """

        await RemindUserSlashes(interaction=interaction).list()

    @someone.error
    async def on_someone_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)
        else:
            raise error
