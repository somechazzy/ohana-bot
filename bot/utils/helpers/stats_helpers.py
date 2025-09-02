import cache


def get_member_count_connected_to_vc_with_music_radio_stream(stream_code: str,
                                                             exclude_guild_id: int | None = None) -> int:
    """
    Returns the number of members connected to a voice channel where Ohana is playing a specific radio stream.
    Args:
        stream_code (str): The code of the radio stream to check for.
        exclude_guild_id (int | None): If provided, excludes the guild with this ID from the count.
    Returns:
        int: The number of members connected to voice channels with the specified radio stream.
    """
    total_count = 0
    for guild_id, music_service in cache.MUSIC_SERVICES.items():
        if music_service.current_stream \
                and music_service.current_stream.code == stream_code \
                and guild_id != exclude_guild_id:
            total_count += len(music_service.voice_client.channel.members) - 1  # exclude self
    return total_count
