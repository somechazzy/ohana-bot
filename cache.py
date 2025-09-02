"""
This module is meant to be used as cache and more generally as shared memory throughout the application.
"""
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PIL.ImageFont import FreeTypeFont
    from models.dto.cachables import CachedGuildSettings, CachedGuildXP
    from services import StandardResponse
    from bot.guild_music_service import GuildMusicService
    from models.dto.radio_stream import RadioStream

LEVEL_XP_MAP: dict[int, int] = {}  # level -> xp required to reach that level
XP_LEVEL_MAP: dict[int, int] = {}  # xp -> level
RANK_IMAGE_FONT_CACHE: dict[int, 'FreeTypeFont'] = {}  # font_size -> ImageFont
RANK_IMAGE_ITALIC_FONT_CACHE: dict[int, 'FreeTypeFont'] = {}  # font_size -> ImageFont

CACHED_WEB_RESPONSES: dict[str, 'StandardResponse'] = {}  # url -> StandardResponse

CACHED_GUILD_SETTINGS: dict[int, 'CachedGuildSettings'] = {}  # guild_id -> CachedGuildSettings
CACHED_GUILD_XP: dict[int, 'CachedGuildXP'] = {}

MUSIC_SERVICES: dict[int, 'GuildMusicService'] = {}  # guild_id -> GuildMusicService
RADIO_STREAMS: dict[str, 'RadioStream'] = {}  # stream_code -> RadioStream
RADIO_STREAMS_BY_CATEGORY: dict[str, list['RadioStream']] = {}  # category_code -> list of RadioStreams

CUSTOM: dict[str, Any] = {}  # custom use for extensions, ensure key is specific enough
