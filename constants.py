"""
Module for project-wide constants
"""
from enum import Enum
from sqlalchemy import Enum as ORMEnum

REMINDER_YEAR_DAY_FORMAT = "%B %d"


class OhanaEnum:
    @classmethod
    def as_list(cls):
        return [value for key, value in cls.__dict__.items() if not key.startswith('_') and not key.endswith('__')]

    @classmethod
    def values_as_enum(cls):
        return Enum(cls.__name__, {value: value for value in cls.as_list()})

    @classmethod
    def as_map(cls):
        return {key: value for key, value in cls.__dict__.items() if not key.startswith('_') and not key.endswith('__')}


class Links:
    class Media:
        HELP_EMBED_THUMBNAIL = "https://assets.ohanabot.xyz/images/help_embed.gif"
        CONTEXT_MENU_USE_CASE = "https://assets.ohanabot.xyz/images/context_menu_command_use_case.jpg"
        URBAN_DICTIONARY_LOGO = "https://assets.ohanabot.xyz/images/logos/urban_dictionary.jpg"
        MERRIAM_WEBSTER_LOGO = "https://assets.ohanabot.xyz/images/logos/merriam_webster.png"
        MAL_LOGO = "https://assets.ohanabot.xyz/images/logos/mal.png"
        ANILIST_LOGO = "https://assets.ohanabot.xyz/images/logos/anilist.png"

    OHANA_WEBSITE = "https://www.ohanabot.xyz/"
    OHANA_WEBSITE_COMMANDS = "https://www.ohanabot.xyz/commands"
    OHANA_INVITE = "http://invite.ohanabot.xyz"
    OHANA_APPS = "https://apps.ohanabot.xyz/"
    APPS_TIMEZONE = "https://apps.ohanabot.xyz/timezone"

    SUPPORT_SERVER_INVITE = "https://discord.gg/syArWFWCeg"
    SUPPORT_ME = "https://ko-fi.com/somechazzy"

    MAL_BASE_URL = "https://myanimelist.net"
    MAL_ANIME_SEARCH_URL = "https://myanimelist.net/anime.php?q={query}&cat=anime"
    MAL_MANGA_SEARCH_URL = "https://myanimelist.net/manga.php?q={query}&cat=manga"
    MAL_ANIME_URL = "https://myanimelist.net/anime/{anime_id}"
    MAL_MANGA_URL = "https://myanimelist.net/manga/{manga_id}"
    MAL_PROFILE_URL = "https://myanimelist.net/profile/{username}"
    MAL_ANIME_LIST_URL = "https://myanimelist.net/animelist/{username}"
    MAL_MANGA_LIST_URL = "https://myanimelist.net/mangalist/{username}"

    ANILIST_BASE_URL = "https://anilist.co"
    ANILIST_ANIME_SEARCH_URL = "https://anilist.co/search/anime?search={query}"
    ANILIST_MANGA_SEARCH_URL = "https://anilist.co/search/manga?search={query}"
    ANILIST_ANIME_URL = "https://anilist.co/anime/{anime_id}"
    ANILIST_MANGA_URL = "https://anilist.co/manga/{manga_id}"
    ANILIST_PROFILE_URL = "https://anilist.co/user/{username}"
    ANILIST_ANIME_LIST_URL = "https://anilist.co/user/{username}/animelist"
    ANILIST_MANGA_LIST_URL = "https://anilist.co/user/{username}/mangalist"

    DISCORD_STICKER_URL = "https://media.discordapp.net/stickers/{sticker_id}.{extension}"
    DISCORD_EMOJI_URL = "https://cdn.discordapp.com/emojis/{emoji_id}.{extension}"

    MERRIAM_WEBSTER_DEFINITION_URL = "https://www.merriam-webster.com/dictionary/{term}"


class Colour(OhanaEnum):
    PRIMARY_ACCENT = 0xE4CAA0  # accent from pfp
    SECONDARY_ACCENT = 0xFFEA9D  # brighter
    MUSIC_ACCENT = 0xDEC5A7  # legacy primary

    RED = 0xB94D35
    GREEN = 0x8ADE87
    BLACK = 0x000000
    BROWN = 0xAC7731
    WARM_GOLD = 0xFFBF52
    HOT_ORANGE = 0xD6581A
    SILVER = 0xA8A8A8
    DEEP_BLUE = 0x364B92
    SKY_BLUE = 0x6AC8FD
    CLOUDY_PURPLE = 0x2B2D42
    BLURPLE = 0x5539CC
    WHITE = 0xFFFFFF

    # ALIASES
    LEGACY = MUSIC_ACCENT
    OHANA = PRIMARY_ACCENT
    OHANA_DARKER = SECONDARY_ACCENT

    ERROR = RED
    SUCCESS = GREEN
    SYSTEM = BLACK
    WARNING = BROWN
    INFO = SECONDARY_ACCENT
    UNFORTUNATE = HOT_ORANGE
    NOTICE_ME = BROWN
    NEUTRAL = SILVER

    EXT_STEAM = DEEP_BLUE
    EXT_MAL = DEEP_BLUE
    EXT_ANILIST = CLOUDY_PURPLE
    EXT_URBAN = SKY_BLUE
    EXT_MERRIAM = SKY_BLUE


####### DB Enums ########


class DBEnum(OhanaEnum):

    @classmethod
    def as_orm_enum(cls):
        return ORMEnum(*cls.as_list(), name=cls.__name__)


class GuildEventType(DBEnum):
    JOIN = "JOIN"
    LEAVE = "LEAVE"


class AutoResponseMatchType(DBEnum):
    EXACT = "EXACT"
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"


class RoleMenuType(DBEnum):
    SELECT = "SELECT"
    BUTTON = "BUTTON"


class RoleMenuMode(DBEnum):
    SINGLE = "SINGLE"
    MULTI = "MULTI"


class XPSettingsMessageCountMode(DBEnum):
    PER_MESSAGE = "PER_MESSAGE"
    PER_TIMEFRAME = "PER_TIMEFRAME"


class AnimangaProvider(DBEnum):
    MAL = "MAL"
    ANILIST = "ANILIST"


class UserUsernameProvider(DBEnum):
    MAL = "MAL"
    ANILIST = "ANILIST"


class ReminderStatus(DBEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class ReminderRecurrenceStatus(DBEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ReminderRecurrenceType(DBEnum):
    BASIC = "BASIC"
    CONDITIONED = "CONDITIONED"


class ReminderRecurrenceBasicUnit(DBEnum):
    HOUR = "HOUR"
    DAY = "DAY"


class ReminderRecurrenceConditionedType(DBEnum):
    DAYS_OF_WEEK = "DAYS_OF_WEEK"
    DAYS_OF_MONTH = "DAYS_OF_MONTH"
    DAY_OF_YEAR = "DAY_OF_YEAR"


####### DB Enums End ########


class ChunkGuildsSetting(OhanaEnum):
    AT_STARTUP = 'AT_STARTUP'
    LAZY = 'LAZY'
    ON_DEMAND = 'ON_DEMAND'


class XPDefaults:
    LEVEL_UP_MESSAGE = "{member_mention} You have levelled up! You are now level {level}."
    LEVEL_UP_MESSAGE_MINIMUM_LEVEL = 3
    LEVEL_ROLE_EARN_MESSAGE = "You now have the **{role_name}** role."
    TIMEFRAME_FOR_XP = 60
    MIN_XP_GIVEN = 20
    MAX_XP_GIVEN = 40
    DECAY_XP_PERCENTAGE = 1.0
    DECAY_DAYS_GRACE = 7
    BOOSTER_GAIN_MULTIPLIER = 0.0
    MAX_LEVEL = 400


class MusicDefaults:
    DEFAULT_PLAYER_MESSAGE_CONTENT = "Choose a radio station from the dropdown below."
    PLAYER_HEADER_IMAGE = "https://assets.ohanabot.xyz/images/player_header_v4.png"
    PLAYER_IDLE_IMAGE = "https://assets.ohanabot.xyz/images/player_idle.gif"
    DEFAULT_STREAM_IMAGE = "https://assets.ohanabot.xyz/images/radio_default.jpg"


class RoleMenuDefaults:
    NAME = "General Role Menu"
    DESCRIPTION = "Use this menu to select your role(s)"
    EMBED_COLOUR = Colour.PRIMARY_ACCENT
    MENU_TYPE = RoleMenuType.SELECT
    MENU_MODE = RoleMenuMode.SINGLE


class DefinedAsset:

    class Font:
        CALIBRI = r"assets/fonts/calibri.ttf"
        CALIBRI_ITALIC = r"assets/fonts/calibri_italic.ttf"

    class XPAssets:
        XP_RANK_TEMPLATE = r"assets/xp/rank_template.jpg"
        DEFAULT_AVATAR = r"assets/xp/default_avatar.png"
        XP_REQUIREMENTS_MODEL = r"assets/data/xp_requirement_ohana_model.json"

    class MediaAssets:
        MAL_LOGO = r"assets/media/mal_logo.png"
        ANILIST_LOGO = r"assets/media/anilist_logo.png"
        URBAN_LOGO = r"assets/media/urban_logo.png"

    RADIO_STREAMS = r"assets/data/radio_streams.json"
    EMOJIS_BASE_DIR = r"assets/media/emojis"


class Environment(OhanaEnum):
    DEV = 'dev'
    PROD = 'prod'


class CommandGroup(OhanaEnum):
    # Prefixes are priorities for /commands API sorting purposes
    ANIMANGA = 'P01-Animanga'
    XP = 'P02-XP'
    REMINDER = 'P03-Reminder'
    UTILITY = 'P04-Utility'
    MODERATION = 'P05-Moderation'
    GENERAL = 'P06-General'

    GENERAL_MANAGEMENT = 'P10-General Management'
    MUSIC = 'P11-Music'
    ROLE_MENU_MANAGEMENT = 'P12-Role Menu Management'
    XP_MANAGEMENT = 'P13-XP Management'
    ROLE_MANAGEMENT = 'P14-Role Management'
    CHANNEL_MANAGEMENT = 'P15-Channel Management'
    AUTOMOD = 'P16-Automod'


COMMAND_GROUP_DESCRIPTION_MAP = {
    CommandGroup.GENERAL: "General",
    CommandGroup.ANIMANGA: "Anime & Manga",
    CommandGroup.XP: "XP & Levels",
    CommandGroup.REMINDER: "Reminders",
    CommandGroup.UTILITY: "Utility",
    CommandGroup.MODERATION: "Moderation",

    CommandGroup.GENERAL_MANAGEMENT: "General Management",
    CommandGroup.MUSIC: "Music",
    CommandGroup.ROLE_MENU_MANAGEMENT: "Role Menu Management",
    CommandGroup.XP_MANAGEMENT: "XP Management",
    CommandGroup.ROLE_MANAGEMENT: "Role Management",
    CommandGroup.CHANNEL_MANAGEMENT: "Channel Management",
    CommandGroup.AUTOMOD: "Automod"
}


class CommandQueryType(OhanaEnum):
    USER = 'USER'
    ADMIN = 'ADMIN'
    ALL = 'ALL'


class CommandCategory(OhanaEnum):
    USER = 'USER'
    ADMIN = 'ADMIN'


class CommandContext(OhanaEnum):
    GUILD = "guild"
    DM = "dm"
    SELF_INSTALL = "self_install"


class AppLogLevel(OhanaEnum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

    @classmethod
    def to_numeric(cls, level: str) -> int:
        return {
            cls.DEBUG: 10,
            cls.INFO: 20,
            cls.WARNING: 30,
            cls.ERROR: 40,
            cls.CRITICAL: 50
        }.get(level, 20)


class AppLogCategory(OhanaEnum):
    BOT_GENERAL = 'BOT_GENERAL'
    APP_GENERAL = 'APP_GENERAL'

    BOT_SLASH_COMMAND_CALLED = 'BOT_SLASH_COMMAND_CALLED'
    BOT_CONTEXT_MENU_COMMAND_CALLED = 'BOT_CONTEXT_MENU_COMMAND_CALLED'
    BOT_INTERACTION_CALLED = 'BOT_INTERACTION_CALLED'

    BOT_MESSAGE_SENT = 'BOT_MESSAGE_SENT'
    BOT_MESSAGE_EDITED = 'BOT_MESSAGE_EDITED'
    BOT_MESSAGE_DELETED = 'BOT_MESSAGE_DELETED'

    BOT_DM_RECEIVED = 'BOT_DM_RECEIVED'
    BOT_GUILD_JOINED = 'BOT_GUILD_JOINED'
    BOT_GUILD_LEFT = 'BOT_GUILD_LEFT'

    API_REQUEST_RECEIVED = 'API_REQUEST_RECEIVED'

    BOT_DPY = 'BOT_DPY'


class BackgroundWorker(OhanaEnum):
    # PERIODIC WORKERS (run every specified interval)

    # worker for refreshing cached/queued reminders
    REMINDER_QUEUE_PRODUCER = "Reminder Queue Producer"
    # worker for sending reminders
    REMINDER_QUEUE_CONSUMER = "Reminder Queue Consumer"
    # worker for cleaning cache (web requests, yt info)
    CACHE_CLEANUP = "Cache Cleanup"
    # worker for log ingestion (logs are kept in async queue and processed here)
    LOG_INGESTION = "Log Ingestion"
    # worker for syncing xp with the database
    XP_DB_SYNC = "XP Database Sync"
    # worker for processing messages for xp gain
    XP_MESSAGE_QUEUE_CONSUMER = "XP Message Queue Consumer"
    # worker for processing XP actions adjusting member XP - from commands
    XP_ACTION_QUEUE_CONSUMER = "XP Action Queue Consumer"
    # worker for enqueuing members pending xp decay
    XP_DECAY_QUEUE_PRODUCER = "XP Decay Queue Producer"
    # worker for decaying members XP
    XP_DECAY_QUEUE_CONSUMER = "XP Decay Queue Consumer"

    # SELF-SCHEDULING WORKERS (worker decides when to run again)


PERIODIC_WORKER_FREQUENCY = {
    BackgroundWorker.REMINDER_QUEUE_PRODUCER: 30,
    BackgroundWorker.REMINDER_QUEUE_CONSUMER: 5,
    BackgroundWorker.CACHE_CLEANUP: 30,
    BackgroundWorker.XP_DB_SYNC: 30,
    BackgroundWorker.XP_MESSAGE_QUEUE_CONSUMER: 0.1,
    BackgroundWorker.XP_ACTION_QUEUE_CONSUMER: 3,
    BackgroundWorker.XP_DECAY_QUEUE_PRODUCER: 3600,
    BackgroundWorker.XP_DECAY_QUEUE_CONSUMER: 300,
    BackgroundWorker.LOG_INGESTION: 1,
}

WORKER_RETRY_ON_ERROR_DELAY = {
    BackgroundWorker.REMINDER_QUEUE_PRODUCER: 10,
    BackgroundWorker.REMINDER_QUEUE_CONSUMER: 5,
    BackgroundWorker.CACHE_CLEANUP: 60,
    BackgroundWorker.XP_DB_SYNC: 30,
    BackgroundWorker.XP_MESSAGE_QUEUE_CONSUMER: 0.1,
    BackgroundWorker.XP_ACTION_QUEUE_CONSUMER: 3,
    BackgroundWorker.XP_DECAY_QUEUE_PRODUCER: 7200,
    BackgroundWorker.XP_DECAY_QUEUE_CONSUMER: 600,
    BackgroundWorker.LOG_INGESTION: 1,
}


class CachingPolicyPresetName:
    NO_CACHE = 0

    MAL_PROFILE = 1
    MAL_SEARCH = 2
    MAL_LIST = 3
    MAL_INFO = 4

    ANILIST_PROFILE = 5
    ANILIST_SEARCH = 6
    ANILIST_LIST = 7
    ANILIST_INFO = 8

    URBAN_DEFINITION = 9
    MERRIAM_DEFINITION = 10


CACHING_POLICY_PRESET = {
    # : duration in seconds to keep cached
    CachingPolicyPresetName.NO_CACHE: 0,
    CachingPolicyPresetName.MAL_PROFILE: 60 * 15,  # 15 minutes
    CachingPolicyPresetName.MAL_SEARCH: 60 * 60 * 2,   # 2 hours
    CachingPolicyPresetName.MAL_LIST: 60 * 15,  # 15 minutes
    CachingPolicyPresetName.MAL_INFO: 60 * 60 * 12,  # 12 hours
    CachingPolicyPresetName.ANILIST_PROFILE: 60 * 15,  # 15 minutes
    CachingPolicyPresetName.ANILIST_SEARCH: 60 * 60 * 2,  # 2 hours
    CachingPolicyPresetName.ANILIST_LIST: 60 * 15,  # 15 minutes
    CachingPolicyPresetName.ANILIST_INFO: 60 * 60 * 12,  # 12 hours
    CachingPolicyPresetName.URBAN_DEFINITION: 60 * 60,  # 1 hour
    CachingPolicyPresetName.MERRIAM_DEFINITION: 60 * 60 * 24,  # 24 hours
}


###### Anime/Manga, MAL/AniList ######


class UserAnimangaListScoringSystem:
    ZERO_TO_HUNDRED = "0-100"
    ZERO_TO_TEN = "0-10"
    ZERO_TO_TEN_DECIMAL = "0-10"
    ZERO_TO_FIVE = "0-5"
    ZERO_TO_THREE = "0-3"
    OTHER = "Other"


ANILIST_SCORING_SYSTEM_MAPPING = {
    "POINT_100": UserAnimangaListScoringSystem.ZERO_TO_HUNDRED,
    "POINT_10_DECIMAL": UserAnimangaListScoringSystem.ZERO_TO_TEN_DECIMAL,
    "POINT_10": UserAnimangaListScoringSystem.ZERO_TO_TEN,
    "POINT_5": UserAnimangaListScoringSystem.ZERO_TO_FIVE,
    "POINT_3": UserAnimangaListScoringSystem.ZERO_TO_THREE,
    "-": UserAnimangaListScoringSystem.OTHER
}


class UserAnimeStatus:
    WATCHING = "Watching"
    COMPLETED = "Completed"
    ON_HOLD = "On-Hold"
    DROPPED = "Dropped"
    PLAN_TO_WATCH = "Plan to Watch"
    REWATCHING = "Rewatching"
    NOT_ON_LIST = "Not on List"


MAL_USER_ANIME_STATUS_MAPPING = {
    1: UserAnimeStatus.WATCHING,
    2: UserAnimeStatus.COMPLETED,
    3: UserAnimeStatus.ON_HOLD,
    4: UserAnimeStatus.DROPPED,
    6: UserAnimeStatus.PLAN_TO_WATCH
}

ANILIST_USER_ANIME_STATUS_MAPPING = {
    "CURRENT": UserAnimeStatus.WATCHING,
    "COMPLETED": UserAnimeStatus.COMPLETED,
    "PAUSED": UserAnimeStatus.ON_HOLD,
    "DROPPED": UserAnimeStatus.DROPPED,
    "PLANNING": UserAnimeStatus.PLAN_TO_WATCH,
    "REPEATING": UserAnimeStatus.REWATCHING
}


class UserMangaStatus:
    READING = "Reading"
    COMPLETED = "Completed"
    ON_HOLD = "On-Hold"
    DROPPED = "Dropped"
    PLAN_TO_READ = "Plan to Read"
    REREADING = "Re-reading"
    NOT_ON_LIST = "Not on List"


MAL_USER_MANGA_STATUS_MAPPING = {
    1: UserMangaStatus.READING,
    2: UserMangaStatus.COMPLETED,
    3: UserMangaStatus.ON_HOLD,
    4: UserMangaStatus.DROPPED,
    6: UserMangaStatus.PLAN_TO_READ
}

ANILIST_USER_MANGA_STATUS_MAPPING = {
    "CURRENT": UserMangaStatus.READING,
    "COMPLETED": UserMangaStatus.COMPLETED,
    "PAUSED": UserMangaStatus.ON_HOLD,
    "DROPPED": UserMangaStatus.DROPPED,
    "PLANNING": UserMangaStatus.PLAN_TO_READ,
    "REPEATING": UserMangaStatus.REREADING
}


class AnimeMediaType:
    TV = "TV"
    MOVIE = "Movie"
    ONA = "ONA"
    OVA = "OVA"
    MUSIC = "Music"
    SPECIAL = "Special"
    TV_SHORT = "TV Short"
    PV = "PV"
    CM = "CM"


MAL_ANIME_MEDIA_TYPE_MAPPING = {
    "tv": AnimeMediaType.TV,
    "movie": AnimeMediaType.MOVIE,
    "ona": AnimeMediaType.ONA,
    "ova": AnimeMediaType.OVA,
    "music": AnimeMediaType.MUSIC,
    "special": AnimeMediaType.SPECIAL,
    "tv_special": AnimeMediaType.SPECIAL,
    "tv special": AnimeMediaType.SPECIAL,
    "tv_short": AnimeMediaType.TV_SHORT,
    "tv short": AnimeMediaType.TV_SHORT,
    "pv": AnimeMediaType.PV,
    "cm": AnimeMediaType.CM
}

ANILIST_ANIME_MEDIA_TYPE_MAPPING = {
    "tv": AnimeMediaType.TV,
    "tv_short": AnimeMediaType.TV_SHORT,
    "movie": AnimeMediaType.MOVIE,
    "special": AnimeMediaType.SPECIAL,
    "ova": AnimeMediaType.OVA,
    "ona": AnimeMediaType.ONA,
    "music": AnimeMediaType.MUSIC
}


class MangaMediaType:
    MANGA = "Manga"
    NOVEL = "Novel"
    ONE_SHOT = "One-shot"
    MANHUA = "Manhua"
    MANHWA = "Manhwa"
    LIGHT_NOVEL = "Light Novel"
    DOUJINSHI = "Doujinshi"


MAL_MANGA_MEDIA_TYPE_MAPPING = {
    "manga": MangaMediaType.MANGA,
    "novel": MangaMediaType.NOVEL,
    "one_shot": MangaMediaType.ONE_SHOT,
    "one shot": MangaMediaType.ONE_SHOT,
    "manhua": MangaMediaType.MANHUA,
    "manhwa": MangaMediaType.MANHWA,
    "light_novel": MangaMediaType.LIGHT_NOVEL,
    "light novel": MangaMediaType.LIGHT_NOVEL,
    "doujinshi": MangaMediaType.DOUJINSHI,
    "doujin": MangaMediaType.DOUJINSHI
}

ANILIST_MANGA_MEDIA_TYPE_MAPPING = {
    "MANGA": MangaMediaType.MANGA,
    "NOVEL": MangaMediaType.NOVEL,
    "ONE_SHOT": MangaMediaType.ONE_SHOT,
}


class AnimeAiringStatus:
    CURRENTLY_AIRING = "Currently Airing"
    UPCOMING = "Upcoming"
    FINISHED = "Finished"


MAL_ANIME_AIRING_STATUS_MAPPING = {
    "currently_airing": AnimeAiringStatus.CURRENTLY_AIRING,
    "not_yet_aired": AnimeAiringStatus.UPCOMING,
    "finished_airing": AnimeAiringStatus.FINISHED
}

ANILIST_ANIME_AIRING_STATUS_MAPPING = {
    "RELEASING": AnimeAiringStatus.CURRENTLY_AIRING,
    "NOT_YET_RELEASED": AnimeAiringStatus.UPCOMING,
    "FINISHED": AnimeAiringStatus.FINISHED
}


class AnimeSeason:
    WINTER = "Winter"
    SPRING = "Spring"
    SUMMER = "Summer"
    FALL = "Fall"


MAL_ANIME_SEASON_MAPPING = {
    "winter": AnimeSeason.WINTER,
    "spring": AnimeSeason.SPRING,
    "summer": AnimeSeason.SUMMER,
    "fall": AnimeSeason.FALL
}

ANILIST_ANIME_SEASON_MAPPING = {
    "WINTER": AnimeSeason.WINTER,
    "SPRING": AnimeSeason.SPRING,
    "SUMMER": AnimeSeason.SUMMER,
    "FALL": AnimeSeason.FALL
}


class AnimeMediaSource:
    ORIGINAL = "Original"
    MANGA = "Manga"
    FOUR_KOMA = "4-Koma"
    WEB_MANGA = "Web Manga"
    DIGITAL_MANGA = "Digital Manga"
    NOVEL = "Novel"
    LIGHT_NOVEL = "Light Novel"
    VISUAL_NOVEL = "Visual Novel"
    VIDEO_GAME = "Video Game"
    CARD_GAME = "Card Game"
    BOOK = "Book"
    PICTURE_BOOK = "Picture Book"
    RADIO = "Radio"
    MUSIC = "Music"
    DOUJINSHI = "Doujinshi"
    ANIME = "Anime"
    WEB_NOVEL = "Web Novel"
    LIVE_ACTION = "Live Action"
    COMIC = "Comic"
    MULTIMEDIA_PROJECT = "Multimedia Project"
    OTHER = "Other"


MAL_ANIME_MEDIA_SOURCE_MAPPING = {
    "original": AnimeMediaSource.ORIGINAL,
    "manga": AnimeMediaSource.MANGA,
    "4_koma_manga": AnimeMediaSource.FOUR_KOMA,
    "web_manga": AnimeMediaSource.WEB_MANGA,
    "digital_manga": AnimeMediaSource.DIGITAL_MANGA,
    "novel": AnimeMediaSource.NOVEL,
    "light_novel": AnimeMediaSource.LIGHT_NOVEL,
    "visual_novel": AnimeMediaSource.VISUAL_NOVEL,
    "game": AnimeMediaSource.VIDEO_GAME,
    "card_game": AnimeMediaSource.CARD_GAME,
    "book": AnimeMediaSource.BOOK,
    "picture_book": AnimeMediaSource.PICTURE_BOOK,
    "radio": AnimeMediaSource.RADIO,
    "music": AnimeMediaSource.MUSIC,
    "other": AnimeMediaSource.OTHER,
    "-": AnimeMediaSource.OTHER
}

ANILIST_ANIME_MEDIA_SOURCE_MAPPING = {
    "ORIGINAL": AnimeMediaSource.ORIGINAL,
    "MANGA": AnimeMediaSource.MANGA,
    "LIGHT_NOVEL": AnimeMediaSource.LIGHT_NOVEL,
    "VISUAL_NOVEL": AnimeMediaSource.VISUAL_NOVEL,
    "VIDEO_GAME": AnimeMediaSource.VIDEO_GAME,
    "OTHER": AnimeMediaSource.OTHER,
    "NOVEL": AnimeMediaSource.NOVEL,
    "DOUJINSHI": AnimeMediaSource.DOUJINSHI,
    "ANIME": AnimeMediaSource.ANIME,
    "WEB_NOVEL": AnimeMediaSource.WEB_NOVEL,
    "LIVE_ACTION": AnimeMediaSource.LIVE_ACTION,
    "GAME": AnimeMediaSource.CARD_GAME,
    "COMIC": AnimeMediaSource.COMIC,
    "MULTIMEDIA_PROJECT": AnimeMediaSource.MULTIMEDIA_PROJECT,
    "PICTURE_BOOK": AnimeMediaSource.PICTURE_BOOK
}


class MangaPublishingStatus:
    PUBLISHING = "Publishing"
    UPCOMING = "Upcoming"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    HIATUS = "On hiatus"


MAL_MANGA_PUBLISHING_STATUS_MAPPING = {
    "publishing": MangaPublishingStatus.PUBLISHING,
    "currently_publishing": MangaPublishingStatus.PUBLISHING,
    "not_yet_published": MangaPublishingStatus.UPCOMING,
    "finished": MangaPublishingStatus.COMPLETED
}

ANILIST_MANGA_PUBLISHING_STATUS_MAPPING = {
    "RELEASING": MangaPublishingStatus.PUBLISHING,
    "NOT_YET_RELEASED": MangaPublishingStatus.UPCOMING,
    "FINISHED": MangaPublishingStatus.COMPLETED,
    "CANCELLED": MangaPublishingStatus.CANCELLED,
    "HIATUS": MangaPublishingStatus.HIATUS
}


class AnimangaListLoadingStatus:
    PENDING = "Pending"
    LOADING = "Loading"
    LOADED = "Loaded"
    PARTIAL_FAILURE = "Partial Failure"
    FAILED = "Failed"


####### Anime/Manga, MAL/AniList End ######


class DiscordTimestamp(OhanaEnum):
    SHORT_TIME = "<t:{timestamp}:t>"
    LONG_TIME = "<t:{timestamp}:T>"
    SHORT_DATE = "<t:{timestamp}:d>"
    LONG_DATE = "<t:{timestamp}:D>"
    SHORT_DATE_TIME = "<t:{timestamp}:f>"
    LONG_DATE_TIME = "<t:{timestamp}:F>"
    RELATIVE_TIME = "<t:{timestamp}:R>"
    DEFAULT = "<t:{timestamp}>"


class GuildLogEvent(OhanaEnum):
    ASSIGNED_ROLES = "Assigned Roles"
    UNASSIGNED_ROLES = "Unassigned Roles"
    EDITED_ROLES = "Edited Roles"
    CREATED_ROLE = "Created Role"
    CREATED_CHANNEL = "Created Channel"
    KICKED_MEMBER = "Kicked Member"
    BANNED_MEMBER = "Banned Member"
    UNBANNED_MEMBER = "Unbanned Member"
    MUTED_MEMBER = "Muted Member"
    UNMUTED_MEMBER = "Unmuted Member"
    DELETED_MESSAGE = "Deleted Message"
    SENT_MESSAGE = "Sent Message"

    PERM_ERROR = "Permission Error"
    ACTION_ERROR = "Action Error"

    SETTING_CHANGE = "Ohana Setting Change"
    GENERAL = "General"


DAY_OF_WEEK_NUMBER_NAME_MAP = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

OFFENSIVE_WORDS_LIST = ("Y3VudCxkeWtlLCBmYWcgLGZhZ2dvdCxuaWdnZXIsbmlnZ2Esc"
                        "2x1dCx3aG9yZSxjaGluayx0cmFubnksdHJhbm5pZSxraWtl")


class MusicPlayerAction(OhanaEnum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    SELECT_STREAM = "select-stream"
    STOP = "stop"
    REPORT_ISSUE = "report-issue"
    FIX_PLAYER = "fix-player"
    SHOW_CURRENTLY_PLAYING = "show-currently-playing"

    @classmethod
    def qualifier(cls):
        return "music"

    @classmethod
    def subselect_qualifier(cls):
        return "category"


class ReminderDeliveryAction(OhanaEnum):
    SNOOZE_60 = "snooze-60"
    SNOOZE_720 = "snooze-720"
    SNOOZE_1440 = "snooze-1440"
    SNOOZE_CUSTOM = "snooze-custom"
    EDIT = "edit"
    SETUP = "setup"
    BLOCK_ALL = "block-all"
    BLOCK_AUTHOR = "block-author"

    @classmethod
    def snooze_actions(cls):
        return [cls.SNOOZE_60, cls.SNOOZE_720, cls.SNOOZE_1440, cls.SNOOZE_CUSTOM]

    @classmethod
    def qualifier(cls):
        return "delivered-reminder"


class RoleMenuImagePlacement(OhanaEnum):
    IMAGE = "image"
    THUMBNAIL = "thumbnail"


class XPLevelUpMessageSubstitutable(OhanaEnum):
    MEMBER_MENTION = "member_mention"
    MEMBER_NAME = "member_name"
    LEVEL = "level"

    @classmethod
    def as_placeholders(cls):
        return {f"{{{value}}}" for value in cls.as_list()}


class XPActionEnums:

    class MainAction(OhanaEnum):
        AWARD_XP = "Award XP"
        TAKE_AWAY_XP = "Take away XP"
        TRANSFER_XP = "Transfer XP"
        RESET_XP = "Reset XP"

    class ActionTargetType(OhanaEnum):
        MEMBER = "Member"
        ROLE = "Role"
        EVERYONE = "Everyone"


GUILD_FEATURE_MEMBER_VERIFICATION_GATE_ENABLED = "MEMBER_VERIFICATION_GATE_ENABLED"


class RadioStreamCategory(OhanaEnum):
    DEFAULT = "DEFAULT"
    ROCK = "ROCK"
    HIPHOP = "HIPHOP"
    CLASSIC = "CLASSIC"
    JAPANESE = "JAPANESE"
    KOREAN = "KOREAN"
    POP = "POP"
    ARABIC = "ARABIC"


RADIO_CATEGORY_LABEL_MAP = {
    RadioStreamCategory.DEFAULT: "Default stations",
    RadioStreamCategory.ROCK: "Rock music stations",
    RadioStreamCategory.HIPHOP: "Hip-Hop & R&B stations",
    RadioStreamCategory.CLASSIC: "Jazz, Classics & Oldies",
    RadioStreamCategory.JAPANESE: "J-Rock, J-Pop, Anime",
    RadioStreamCategory.KOREAN: "K-Pop, K-Hip-Hop",
    RadioStreamCategory.POP: "Pop music stations",
    RadioStreamCategory.ARABIC: "Arabic music stations",
}
