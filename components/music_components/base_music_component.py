import discord

from actions import send_message
from components.base_component import BaseComponent
from globals_.constants import Colour, PLAYER_HEADER_IMAGE, DEFAULT_PLAYER_MESSAGE_CONTENT
from utils.helpers import get_player_message_views
from utils.embed_factory import make_initial_player_message_embed
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent


class MusicComponent(BaseComponent):

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_player_channel(self, guild, music_channel=None, send_header=True, player_embed=None,
                                   player_views=None,
                                   player_message_content=DEFAULT_PLAYER_MESSAGE_CONTENT):
        if not music_channel:
            music_channel = await guild.create_text_channel(name="🎸-player",
                                                            topic="Music Player",
                                                            reason="Player channel",
                                                            position=0)
            self.info_logger.log(f"Created music channel for guild {guild.name} ({guild.id})",
                                 guild_id=guild.id)

        if send_header:
            header_embed = discord.Embed(color=Colour.PRIMARY_ACCENT)
            header_embed.set_image(url=PLAYER_HEADER_IMAGE)
            header_message = await send_message(message="",
                                                embed=header_embed,
                                                channel=music_channel)
            header_message_id = header_message.id
        else:
            header_message_id = (await GuildPrefsComponent().get_guild_prefs(guild=guild)).music_header_message
        if not player_embed:
            player_embed = make_initial_player_message_embed(guild)
        if not player_views:
            player_views = get_player_message_views()
        player_message = await send_message(message=player_message_content,
                                            embed=player_embed,
                                            channel=music_channel,
                                            view=player_views)

        await GuildPrefsComponent().set_guild_music_channel(guild=guild, channel_id=music_channel.id)
        await GuildPrefsComponent().set_guild_music_header_message(guild=guild, message_id=header_message_id)
        await GuildPrefsComponent().set_guild_music_player_message(guild=guild, message_id=player_message.id)
        await GuildPrefsComponent().set_guild_music_player_message_timestamp(
            guild=guild, timestamp=int(player_message.created_at.timestamp())
        )
        return music_channel
