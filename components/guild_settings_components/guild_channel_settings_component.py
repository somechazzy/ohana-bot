from common import NOT_SET_
from common.db import get_session
from components.guild_settings_components import BaseGuildSettingsComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from models.guild_settings_models import GuildChannelSettings
from repositories.guild_settings_repositories.guild_channel_settings_repo import GuildChannelSettingsRepo

NOT_SET = NOT_SET_()


class GuildChannelSettingsComponent(BaseGuildSettingsComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def set_guild_channel_settings(self,
                                         guild_id: int,
                                         guild_settings_id: int,
                                         channel_id: int,
                                         message_limiting_role_id: int | NOT_SET_ | None = NOT_SET,
                                         is_gallery_channel: bool | NOT_SET_ = NOT_SET) -> GuildChannelSettings:
        """
        Set a setting for a guild channel by updating its record or creating it.
        Args:
            guild_id (int): The ID of the guild.
            guild_settings_id (int): The GuildSettings ID related.
            channel_id (int): The ID of the channel to set the settings for.
            message_limiting_role_id (int | NOT_SET_): The role ID enforcing the limited messaging.
            is_gallery_channel (bool | NOT_SET_): Whether the channel is a gallery channel.

        Returns:
            GuildChannelSettings: The updated or created GuildChannelSettings instance.
        """
        self.logger.debug(f"Setting guild channel settings for guild_id: {guild_id}")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        guild_channel_settings_repo = GuildChannelSettingsRepo(session=get_session())

        update_data = {}
        if message_limiting_role_id is not NOT_SET:
            update_data['message_limiting_role_id'] = message_limiting_role_id
            if not message_limiting_role_id:
                guild_settings.channel_id_message_limiting_role_id.pop(channel_id, None)
            else:
                guild_settings.channel_id_message_limiting_role_id[channel_id] = message_limiting_role_id
        if is_gallery_channel is not NOT_SET:
            update_data['is_gallery_channel'] = is_gallery_channel
            if is_gallery_channel:
                guild_settings.channel_id_is_gallery_channel[channel_id] = is_gallery_channel
            else:
                guild_settings.channel_id_is_gallery_channel.pop(channel_id, None)

        if not (channel_settings := await guild_channel_settings_repo.get_guild_channel_settings(
            guild_settings_id=guild_settings_id,
            channel_id=channel_id
        )):
            channel_settings = await guild_channel_settings_repo.create_guild_channel_settings(
                guild_settings_id=guild_settings_id,
                channel_id=channel_id,
                is_gallery_channel=is_gallery_channel if is_gallery_channel is not NOT_SET else False,
                message_limiting_role_id=message_limiting_role_id
                if message_limiting_role_id is not NOT_SET else None
            )
        else:
            await guild_channel_settings_repo.update_guild_channel_settings(
                guild_settings_id=guild_settings_id,
                channel_id=channel_id,
                **update_data
            )

        return channel_settings
