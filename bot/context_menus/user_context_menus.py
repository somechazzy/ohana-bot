from io import BytesIO

import discord

from bot.utils.helpers.xp_helpers import get_user_username_for_xp
from bot.utils.modal_factory.reminder_modals import ReminderSetWhenModal
from bot.interaction_handlers.user_interaction_handlers.reminder_context_menu_interaction_handler import \
    ReminderContextMenuInteractionHandler
from bot.utils.embed_factory.general_embeds import get_generic_embed
from bot.utils.embed_factory.user_embeds import get_utility_image_embed
from bot.utils.view_factory.general_views import get_external_url_view
from clients import discord_client
from common.app_logger import AppLogger
from bot.utils.decorators import context_menu_command
from common.exceptions import InvalidCommandUsageException, UserInputException
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from components.guild_user_xp_components.xp_rank_image_component import XPRankImageComponent
from constants import AppLogCategory, CommandContext, Links
from models.dto.cachables import CachedGuildSettings
from strings.commands_strings import ContextCommandsStrings
from utils.helpers.text_manipulation_helpers import get_discord_emoji_string
from utils.helpers.text_parsing_helpers import extract_emojis_from_discord_message


class UserContextMenus:
    """
    Handler for user context menu commands. All handlers must be decorated with `@context_menu_command`.
    """

    def __init__(self,
                 interaction: discord.Interaction,
                 target: discord.Member | discord.User | discord.Message):
        if interaction.context.guild:
            if interaction.guild.name:
                self.context = CommandContext.GUILD
            else:
                self.context = CommandContext.SELF_INSTALL
        else:
            self.context = CommandContext.DM
        self.target: discord.Member | discord.User | discord.Message = target
        self.user: discord.User | discord.Member = interaction.user
        self.member: discord.Member | None
        if isinstance(self.user, discord.Member) and self.context == CommandContext.GUILD:
            self.member = interaction.user
        elif self.context == CommandContext.GUILD:
            self.member = interaction.guild.get_member(interaction.user.id)
        else:
            self.member = None
        self.channel: discord.TextChannel | discord.VoiceChannel | None = interaction.channel
        self.guild: discord.Guild = interaction.guild
        self.guild_settings: CachedGuildSettings | None = None
        self.interaction: discord.Interaction = interaction
        self.logger = AppLogger(component=self.__class__.__name__)

    @context_menu_command()
    async def remind_me(self):
        self.target: discord.Message = self.target
        interaction_handler = ReminderContextMenuInteractionHandler(
            source_interaction=self.interaction,
            context=self.context,
            guild_settings=None,
            target_message=self.target,
        )
        await self.interaction.response.send_modal(ReminderSetWhenModal(interactions_handler=interaction_handler))

    @context_menu_command()
    async def get_avatar(self):
        self.target: discord.User | discord.Member = self.target
        if isinstance(self.target, discord.Member):
            avatar = self.target.display_avatar
        else:
            avatar = (await discord_client.fetch_user(self.target.id)).avatar

        if not avatar:
            raise UserInputException(ContextCommandsStrings.AVATAR_NOT_FOUND)

        await self.interaction.response.send_message(
            embed=get_utility_image_embed(
                image_url=avatar.url,
                title=ContextCommandsStrings.AVATAR_TITLE.format(username=self.target.display_name)
            ),
            view=get_external_url_view(external_url=avatar.url),
            ephemeral=True
        )

    @context_menu_command()
    async def get_banner(self):
        self.target: discord.User | discord.Member = self.target
        if isinstance(self.target, discord.Member) \
                and self.context == CommandContext.GUILD \
                and (member := await self.guild.fetch_member(self.target.id)) \
                and member.guild_banner:
            banner = member.guild_banner
        else:
            user = await discord_client.fetch_user(self.target.id)
            banner = user.banner

        if not banner:
            raise UserInputException(ContextCommandsStrings.BANNER_NOT_FOUND)

        await self.interaction.response.send_message(
            embed=get_utility_image_embed(
                image_url=banner.url,
                title=ContextCommandsStrings.BANNER_TITLE.format(username=self.target.display_name)
            ),
            view=get_external_url_view(external_url=banner.url),
            ephemeral=True
        )

    @context_menu_command(guild_only=True)
    async def get_level(self):
        self.target: discord.User | discord.Member = self.target
        await self.interaction.response.defer(thinking=True)

        image = await XPRankImageComponent().get_member_rank_image(
            user_id=self.target.id,
            display_username=self.target.display_name,
            user_username=get_user_username_for_xp(self.target),
            user_avatar=self.target.display_avatar.with_size(256).url if self.target.display_avatar else None,
            guild_id=self.guild.id
        )

        with BytesIO() as image_binary:
            image.save(image_binary, 'JPEG')
            image_binary.seek(0)
            await self.interaction.followup.send(files=[discord.File(fp=image_binary, filename='level.jpg'), ])

    @context_menu_command()
    async def get_emoji(self):
        self.target: discord.Message = self.target
        emojis_details = extract_emojis_from_discord_message(message=self.target.content or '')[:15]

        if not emojis_details:
            raise UserInputException(ContextCommandsStrings.EMOJIS_NOT_FOUND)

        emoji_id_name_map = {}
        emoji_id_is_animated_map = {}
        emoji_id_url_map = {}
        for is_animated, name, emoji_id in emojis_details:
            emoji_url = Links.DISCORD_EMOJI_URL.format(emoji_id=emoji_id,
                                                       extension="png" if not is_animated else "gif")
            emoji_id_name_map[emoji_id] = name
            emoji_id_is_animated_map[emoji_id] = is_animated
            emoji_id_url_map[emoji_id] = emoji_url

        message = "\n".join(
            get_discord_emoji_string(emoji_name=emoji_name,
                                     emoji_id=emoji_id,
                                     is_animated=emoji_id_is_animated_map[emoji_id]) + f": {emoji_id_url_map[emoji_id]}"
            for emoji_id, emoji_name in emoji_id_name_map.items()
        )

        await self.interaction.response.send_message(
            embed=get_generic_embed(title=ContextCommandsStrings.EMOJIS_TITLE, description=message),
            ephemeral=True
        )

    @context_menu_command()
    async def get_sticker(self):
        self.target: discord.Message = self.target

        if not self.target.stickers:
            raise UserInputException(ContextCommandsStrings.STICKER_NOT_FOUND)

        sticker_url = Links.DISCORD_STICKER_URL.format(sticker_id=self.target.stickers[0].id,
                                                       extension=self.target.stickers[0].format.file_extension)
        await self.interaction.response.send_message(
            embed=get_utility_image_embed(image_url=sticker_url,
                                          title=ContextCommandsStrings.STICKER_TITLE),
            view=get_external_url_view(external_url=sticker_url),
            ephemeral=True
        )

    async def preprocess_and_validate(self, guild_only: bool = False):
        if guild_only and not self.context == CommandContext.GUILD:
            raise InvalidCommandUsageException(ContextCommandsStrings.GUILD_ONLY_ERROR)
        if self.context == CommandContext.GUILD:
            self.guild_settings = await GuildSettingsComponent().get_guild_settings(self.guild.id)
        else:
            self.guild_settings = None
        self.logger.info(f"Context menu command `{self.interaction.command.name}` "
                         f"called by user: {self.interaction.user} ({self.interaction.user.id})."
                         + (f" Guild: {self.guild.name}" if self.guild else "") +
                         f" Channel: {f'#{self.channel}' if self.channel else 'DM'}",
                         extras={
                             "interaction_data": self.interaction.data,
                             "guild_id": self.guild.id if self.guild else None,
                             "channel_id": self.channel.id if self.channel else None,
                             "user_id": self.user.id
                         },
                         category=AppLogCategory.BOT_CONTEXT_MENU_COMMAND_CALLED)
