"""
Base class for slash command handlers.
"""
import discord

from common.exceptions import InvalidCommandUsageException
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import AppLogCategory, CommandContext
from common.app_logger import AppLogger
from strings.commands_strings import GeneralCommandsStrings
from models.dto.cachables import CachedGuildSettings


class BaseSlashes:

    def __init__(self, interaction: discord.Interaction):
        if interaction.context.guild:
            if interaction.guild.name:
                self.context = CommandContext.GUILD
            else:
                self.context = CommandContext.SELF_INSTALL
        else:
            self.context = CommandContext.DM
        self.interaction: discord.Interaction = interaction
        self.guild: discord.Guild | None = interaction.guild if self.context == CommandContext.GUILD else None
        self.channel: discord.TextChannel | discord.DMChannel = interaction.channel
        self.user: discord.User | discord.Member = interaction.user
        if isinstance(self.user, discord.Member) and self.context == CommandContext.GUILD:
            self.member: discord.Member | None = interaction.user
        elif self.context == CommandContext.GUILD:
            self.member: discord.Member | None = interaction.guild.get_member(interaction.user.id)
        else:
            self.member: discord.Member | None = None
        self.is_dm = self.context == CommandContext.DM
        self.interaction_data = interaction.data
        self.guild_settings: CachedGuildSettings | None = ...
        self.command_name: str = interaction.command.qualified_name
        self.logger = AppLogger(component=self.__class__.__name__,)

    async def preprocess_and_validate(self,
                                      guild_only: bool = False,
                                      bot_permissions: list[str] | None = None,
                                      user_permissions: list[str] | None = None,
                                      **kwargs):
        """
        Preprocesses and validates the slash command before passing it to the actual handler.
        Args:
            guild_only (bool): Whether the command can only be used in a guild.
            bot_permissions (list[str] | None): List of permissions the bot needs to execute the command.
            user_permissions (list[str] | None): List of permissions the user needs to execute the command.
        """
        if guild_only and not self.guild:
            raise InvalidCommandUsageException(GeneralCommandsStrings.SERVER_ONLY_COMMAND_ERROR_MESSAGE)

        missing_user_perms, missing_bot_perms = await self.check_permissions(bot_permissions=bot_permissions,
                                                                             user_permissions=user_permissions)
        if missing_user_perms or missing_bot_perms:
            error_message = GeneralCommandsStrings.COMMAND_PERMISSIONS_BASE_ERROR_MESSAGE
            if missing_user_perms:
                user_perms = ', '.join(["**" + missing_user_perm.replace('_', ' ').title() + "**"
                                        for missing_user_perm in missing_user_perms])
                error_message += f"\n• {GeneralCommandsStrings.COMMAND_PERMISSIONS_USER_ERROR_MESSAGE}" \
                                 f" {user_perms}"
            if missing_bot_perms:
                bot_perms = ', '.join(["**" + missing_bot_perm.replace('_', ' ').title() + "**"
                                       for missing_bot_perm in missing_bot_perms])
                error_message += f"\n• {GeneralCommandsStrings.COMMAND_PERMISSIONS_BOT_ERROR_MESSAGE}" \
                                 f" {bot_perms}"
            raise InvalidCommandUsageException(error_message)

        if self.context == CommandContext.GUILD:
            self.guild_settings = await GuildSettingsComponent().get_guild_settings(self.guild.id)
        else:
            self.guild_settings = None

        await self.log_command()

    async def check_permissions(self,
                                bot_permissions: list[str] | None,
                                user_permissions: list[str] | None) -> tuple[list[str], list[str]]:
        """
        Checks if the bot and user have the required permissions to execute the command.
        Args:
            bot_permissions (list[str] | None): List of permissions the bot needs to execute the command.
            user_permissions (list[str] | None): List of permissions the user needs to execute the command.

        Returns:
            tuple[list[str], list[str]]: A tuple of missing user permissions and missing bot permissions.
        """
        missing_user_perms = []
        missing_bot_perms = []
        if self.context in [CommandContext.SELF_INSTALL, CommandContext.DM]:
            return missing_user_perms, missing_bot_perms
        if user_permissions:
            if not self.member:
                return missing_user_perms, missing_bot_perms
            for perm in user_permissions:
                if not getattr(self.member.guild_permissions, perm):
                    missing_user_perms.append(perm)
        if bot_permissions:
            for perm in bot_permissions:
                if not getattr(self.guild.me.guild_permissions, perm):
                    missing_bot_perms.append(perm)
        return missing_user_perms, missing_bot_perms

    async def log_command(self):
        """
        Logs the command usage.
        """
        handler_name = self.interaction.command.qualified_name
        self.logger.info(f"Slash command `{handler_name}` called by user: {self.user} ({self.user.id})."
                         + (f" Guild: {self.guild.name}" if self.guild else "") +
                         f" Channel: {f'#{self.channel}' if self.channel else 'DM'}",
                         extras={
                             "interaction_data": self.interaction_data,
                             "guild_id": self.guild.id if self.guild else None,
                             "channel_id": self.channel.id if self.channel else None,
                             "user_id": self.user.id
                         },
                         category=AppLogCategory.BOT_SLASH_COMMAND_CALLED)

    @property
    def is_using_music_channel(self) -> bool:
        """
        Checks if the command is being used in Ohana's music channel.
        """
        return self.guild_settings \
            and self.guild_settings.music_channel_id == self.channel.id

    def send_as_ephemeral(self, make_visible=True) -> bool:
        """
        Determines if the response should be sent as ephemeral (only visible to the user).
        Args:
            make_visible (bool): User's preference for visibility as passed in the command.
        Returns:
            bool: True if the response should be sent as ephemeral, False otherwise.
        """
        if self.context in [CommandContext.DM, CommandContext.SELF_INSTALL]:
            return False
        if self.is_using_music_channel:
            return True
        if not self.channel.permissions_for(self.guild.me).embed_links:
            return True
        return not make_visible
