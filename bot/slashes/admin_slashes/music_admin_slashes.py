import discord

from bot.slashes.admin_slashes import AdminSlashes
from bot.utils.bot_actions.utility_actions import refresh_music_header_message, refresh_music_player_message
from bot.utils.decorators import slash_command
from bot.utils.embed_factory.general_embeds import get_info_embed, get_success_embed
from components.guild_settings_components.guild_music_settings_component import GuildMusicSettingsComponent
from strings.commands_strings import AdminSlashCommandsStrings


class MusicAdminSlashes(AdminSlashes):

    @slash_command(guild_only=True,
                   user_permissions=["manage_guild"],
                   bot_permissions=["manage_channels", "send_messages", "embed_links", "manage_messages",
                                    "read_message_history", "connect", "speak"])
    async def music_create_channel(self):
        """
        /manage music-create-channel
        Create the #ohana-player channel
        """
        if self.guild_settings.music_channel_id and \
                (music_channel := self.guild.get_channel(self.guild_settings.music_channel_id)):
            return await self.interaction.response.send_message(
                embed=get_info_embed(AdminSlashCommandsStrings.MUSIC_CREATE_CHANNEL_ALREADY_EXISTS_ERROR_MESSAGE.format(
                    channel_mention=music_channel.mention
                )),
                ephemeral=True
            )
        if not self.guild.me.guild_permissions.manage_channels:
            return await self.interaction.response.send_message(
                embed=get_info_embed(
                    AdminSlashCommandsStrings.MUSIC_CREATE_CHANNEL_NO_MANAGE_CHANNELS_PERMISSION_ERROR_MESSAGE
                ),
                ephemeral=True
            )
        await self.interaction.response.send_message(
            embed=get_info_embed(AdminSlashCommandsStrings.MUSIC_CREATE_CHANNEL_STARTING_MESSAGE),
            ephemeral=True
        )
        music_channel = await self.guild.create_text_channel(
            name="🎵-ohana-player",
            topic=AdminSlashCommandsStrings.MUSIC_CREATE_CHANNEL_CHANNEL_DESCRIPTION,
            reason="Ohana music channel",
            overwrites={
                self.guild.me: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    read_message_history=True,
                    embed_links=True,
                    manage_messages=True
                ),
                self.guild.default_role: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=False,
                    read_message_history=True
                ),
            }
        )
        await GuildMusicSettingsComponent().update_guild_music_settings(
            guild_id=self.guild.id,
            guild_settings_id=self.guild_settings.guild_settings_id,
            music_channel_id=music_channel.id
        )
        await refresh_music_header_message(guild=self.guild)
        if not await refresh_music_player_message(guild=self.guild):
            self.logger.error(f"Failed to send music player message in guild {self.guild.name} ({self.guild.id})")

        await self.interaction.edit_original_response(
            embed=get_success_embed(AdminSlashCommandsStrings.MUSIC_CREATE_CHANNEL_SUCCESS_MESSAGE.format(
                channel_mention=music_channel.mention
            )),
        )
