from discord import app_commands
from discord.ext.commands import Cog

from globals_.constants import HelpMenuType
from slashes.user_slashes.other_user_slashes import OtherUserSlashes


class OtherUserBlueprints(Cog):
    FEEDBACK = app_commands.command(name="feedback",
                                    description="Send feedback to the bot owner")
    SUPPORT = app_commands.command(name="support",
                                   description="Get the support server invite link",
                                   extras={"unlisted": True})
    HELP = app_commands.command(name="help",
                                description="Show the help menu",
                                extras={"unlisted": True})

    @FEEDBACK
    async def feedback(self, inter, feedback: str):
        """Send feedback to the bot owner

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        feedback: str
            Feedback to send
        """

        await OtherUserSlashes(interaction=inter).feedback(feedback=feedback)

    @SUPPORT
    async def support(self, inter):
        """Get the support server invite link

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        """

        await OtherUserSlashes(interaction=inter).support()

    @HELP
    @app_commands.rename(make_visible="make-visible")
    async def help(self, inter, menu: HelpMenuType.values_as_enum() = None, make_visible: bool = False):
        """Show the help menu

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        menu: HelpMenuType.values_as_enum()
           Jump to a specific menu
        make_visible: bool
            Make the menu visible to everyone (can be spammy...)
        """

        await OtherUserSlashes(interaction=inter).help(menu=menu, make_visible=make_visible)
