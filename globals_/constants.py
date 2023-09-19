from enum import Enum
from globals_.settings import settings

if settings.ENVIRONMENT == 'prod':
    # noinspection PyProtectedMember
    from globals_._config.prod import *

OWNER_COMMAND_PREFIX = OWNER_COMMAND_PREFIX

BOT_OWNER_ID = BOT_OWNER_ID
SUPPORT_SERVER_ID = SUPPORT_SERVER_ID
DISCORD_LOGGING_CHANNEL_ID = DISCORD_LOGGING_CHANNEL_ID

SUPPORT_SERVER_INVITE = SUPPORT_SERVER_INVITE

DEFAULT_LEVELUP_MESSAGE = DEFAULT_LEVELUP_MESSAGE
DEFAULT_LEVEL_ROLE_EARN_MESSAGE = DEFAULT_LEVEL_ROLE_EARN_MESSAGE
DEFAULT_TIMEFRAME_FOR_XP = DEFAULT_TIMEFRAME_FOR_XP
DEFAULT_MIN_XP_GIVEN = DEFAULT_MIN_XP_GIVEN
DEFAULT_MAX_XP_GIVEN = DEFAULT_MAX_XP_GIVEN
DEFAULT_XP_DECAY_PERCENTAGE = DEFAULT_XP_DECAY_PERCENTAGE
DEFAULT_XP_DECAY_DAYS = DEFAULT_XP_DECAY_DAYS

DEFAULT_PLAYER_MESSAGE_CONTENT = DEFAULT_PLAYER_MESSAGE_CONTENT
PLAYER_HEADER_IMAGE = PLAYER_HEADER_IMAGE
PLAYER_IDLE_IMAGE = PLAYER_IDLE_IMAGE
DEFAULT_STREAM_IMAGE = DEFAULT_STREAM_IMAGE
DEFAULT_RADIO_MESSAGE_CONTENT = DEFAULT_RADIO_MESSAGE_CONTENT

AVATAR_PLACEHOLDER = AVATAR_PLACEHOLDER

HELP_EMBED_THUMBNAIL = HELP_EMBED_THUMBNAIL


class CustomEnum:
    @classmethod
    def as_list(cls):
        return [value for key, value in cls.__dict__.items() if not key.startswith('_') and not key.endswith('__')]

    @classmethod
    def values_as_enum(cls):
        return Enum(cls.__name__, {value: value for value in cls.as_list()})

    @classmethod
    def as_map(cls):
        return {key: value for key, value in cls.__dict__.items() if not key.startswith('_') and not key.endswith('__')}


class BotLogLevel(CustomEnum):
    BOT_INFO = "Info"
    GENERAL = "General"
    RECEIVED_DM = "Received DM"
    MEMBER_INFO = "Member Info"
    GUILD_JOIN = "Guild Join"
    GUILD_LEAVE = "Guild Leave"
    ERROR = "Error"
    WARNING = "Warning"
    MINOR_WARNING = "Minor Warning"
    MESSAGE_SENT = "Message Sent"
    REPLY_SENT = "Reply Sent"
    MESSAGE_DELETED = "Message Deleted"
    MESSAGE_EDITED = "Message Edited"
    LEGACY_MUSIC_ENQUEUE = "Legacy Music Enqueue"
    SLASH_COMMAND_RECEIVED = "Slash Command Received"
    INTERACTION_CALLBACK = "Interaction Callback"
    USER_SLASH_COMMAND_RECEIVED = "User Slash Command Received"
    MUSIC_SLASH_COMMAND_RECEIVED = "Music Slash Command Received"
    ADMIN_SLASH_COMMAND_RECEIVED = "Admin Slash Command Received"


class GuildLogType(CustomEnum):
    MEMBER_JOINED = "Member Joined"
    MEMBER_LEFT = "Member Left"
    ASSIGNED_ROLE = "Assigned Role"
    UNASSIGNED_ROLE = "Unassigned Role"
    ASSIGNED_ROLES = "Assigned Roles"
    UNASSIGNED_ROLES = "Assigned Roles"
    EDITED_ROLES = "Edited Roles"
    CREATED_ROLE = "Created Role"
    KICKED_MEMBER = "Kicked Member"
    BANNED_MEMBER = "Banned Member"
    UNBANNED_MEMBER = "Unbanned Member"
    WARNED_MEMBER = "Warned Member"
    MUTED_MEMBER = "Muted Member"
    UNMUTED_MEMBER = "Unmuted Member"
    DELETED_MESSAGE = "Deleted Message"
    PERM_ERROR = "Permission Error"
    ACTION_ERROR = "Action Error"
    SETTING_CHANGE = "Bot Setting Change"
    GENERAL = "General"


class CachingType(CustomEnum):
    MAL_INFO_ANIME = "mal_info_anime"
    MAL_INFO_MANGA = "mal_info_manga"
    MAL_SEARCH_ANIME = "mal_search_anime"
    MAL_SEARCH_MANGA = "mal_search_manga"
    MAL_PROFILE = "mal_profile"
    MAL_LIST_ANIME = "mal_list_anime"
    MAL_LIST_MANGA = "mal_list_manga"
    AL_PROFILE = "al_profile"
    AL_LISTS = "al_lists"
    URBAN_DICTIONARY = "urban_dictionary"
    MERRIAM_DICTIONARY = "merriam_dictionary"
    DISCORD_AVATAR = "discord_avatar"
    SPOTIFY_INFO = "spotify_info"
    SPOTIFY_PLAYLIST = "spotify_playlist"
    NO_CACHE = "no_cache"


cache_timeout_minutes = {
    CachingType.MAL_INFO_ANIME: 360,
    CachingType.MAL_INFO_MANGA: 360,
    CachingType.MAL_SEARCH_ANIME: 480,
    CachingType.MAL_SEARCH_MANGA: 480,
    CachingType.MAL_PROFILE: 15,
    CachingType.MAL_LIST_ANIME: 15,
    CachingType.MAL_LIST_MANGA: 15,
    CachingType.AL_PROFILE: 15,
    CachingType.AL_LISTS: 15,
    CachingType.URBAN_DICTIONARY: 600,
    CachingType.MERRIAM_DICTIONARY: 1440,
    CachingType.DISCORD_AVATAR: 20,
    CachingType.SPOTIFY_INFO: 1440,
    CachingType.SPOTIFY_PLAYLIST: 5,
    CachingType.NO_CACHE: 0
}


NUMBERS_EMOJI_CODES = [
    ":one:",
    ":two:",
    ":three:",
    ":four:",
    ":five:",
    ":six:",
    ":seven:",
    ":eight:",
    ":nine:",
    ":keycap_ten:"
]

NUMBER_EMOJI_MAP = {
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣",
    9: "9️⃣",
    10: "🔟"
}

MAL_ANIME_STATUS_MAPPING = {
    "1": "Watching",
    "2": "Completed",
    "3": "On-Hold",
    "4": "Dropped",
    "6": "Plan to"
}

MAL_MANGA_STATUS_MAPPING = {
    "1": "Reading",
    "2": "Completed",
    "3": "On-Hold",
    "4": "Dropped",
    "6": "Plan to"
}

ANILIST_SCORING_SYSTEM_MAP: dict[str, str] = {
    "POINT_100": "0-100",
    "POINT_10_DECIMAL": "0-10",
    "POINT_10": "0-10",
    "POINT_5": "0-5",
    "POINT_3": "0-3",
    "-": "unknown"
}

ENCRYPTED_CHARACTERS = {
    "$": "%dollar_sign%",
    "#": "%hash_sign%",
    "[": "%opening_square_bracket%",
    "]": "%closing_square_bracket%",
    ".": "%dot_sign%",
    "?": "%question_mark%"
}


class MerriamDictionaryResponseType(CustomEnum):
    SUCCESS = "Success"
    NOT_FOUND = "Not Found"
    OTHER = "Other"


class XPSettingsKey(CustomEnum):
    IGNORED_CHANNELS = "ignored_channels"
    IGNORED_ROLES = "ignored_roles"

    XP_GAIN_ENABLED = "xp_gain_enabled"
    XP_GAIN_TIMEFRAME = "xp_gain_time_frame"
    XP_GAIN_MIN = "xp_gain_min"
    XP_GAIN_MAX = "xp_gain_max"
    MESSAGE_COUNT_MODE = "message_count_mode"

    LEVELUP_ENABLED = "levelup_enabled"
    LEVELUP_CHANNEL = "levelup_channel"
    LEVELUP_MESSAGE = "levelup_message"
    LEVEL_ROLES = "level_roles"
    LEVEL_ROLE_EARN_MESSAGE = "level_role_earn_message"
    STACK_ROLES = "stack_roles"
    LEVEL_MAX = "level_max"

    XP_DECAY_ENABLED = "xp_decay_enabled"
    PERCENTAGE_OF_XP_DECAY_PER_DAY = "percentage_of_xp_decay_per_day"
    DAYS_BEFORE_XP_DECAY = "days_before_xp_decay"

    BOOST_EXTRA_GAIN = "boost_extra_gain"
    ROLES_EXTRA_GAIN = "roles_extra_gain"


LEVEL_XP_MAP = {}
XP_LEVEL_MAP = {}


class MessageCountMode(CustomEnum):
    PER_TIMEFRAME = 0
    PER_MESSAGE = 1


class OSType(CustomEnum):
    LINUX = 'Linux'
    WINDOWS = 'Windows'
    OTHER = 'Other'


class MusicVCState(CustomEnum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    PLAYING = "playing"


class MusicVCLoopMode(CustomEnum):
    NONE = "none"
    ALL = "all"
    ONE = "one"


next_music_vc_loop_mode = {
    MusicVCLoopMode.NONE: MusicVCLoopMode.ALL,
    MusicVCLoopMode.ALL: MusicVCLoopMode.ONE,
    MusicVCLoopMode.ONE: MusicVCLoopMode.NONE
}


VOICE_PERMISSIONS = [
    'speak',
    'connect',
    'deafen_members',
    'move_members',
    'priority_speaker',
    'request_to_speak',
    'stream',
    'use_voice_activation'
]


class MusicTrackSource(CustomEnum):
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"


generic_youtube_title_words = [
    'official lyric video',
    'official lyrics video',
    'lyric video',
    'lyrics video',
    'official music video',
    'music video',
    'official video',
    'official audio',
    'audio',
    'official',
    'with lyrics',
    'lyrics',
    'explicit'
]

generic_youtube_title_words_to_remove = [
    'official lyric video',
    'official lyrics video',
    'lyric video',
    'lyrics video',
    'official music video',
    'music video',
    'official video',
    'official audio',
    'with lyrics',
    'lyrics',
]


class PlayerAction(CustomEnum):
    JOIN = "JOIN"
    REFRESH = "REFRESH"
    LEAVE = "LEAVE"
    SKIP = "SKIP"
    SHUFFLE = "SHUFFLE"
    LOOP = "LOOP"
    FAVORITE = "FAVORITE"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    LIBRARY = "LIBRARY"
    HISTORY = "HISTORY"
    RADIO = "RADIO"
    PLAYER = "PLAYER"


# todo
"""
Upload images in this folder as emojis to your server (where your bot is)
https://drive.google.com/drive/folders/1mQgvzT45KcSR3Fcs6AQkcRgCotY79uO-?usp=sharing
"""
PLAYER_ACTION_CUSTOM_EMOJI_MAP = {
    PlayerAction.JOIN: 0,  # replace with the emoji ID related to Join.png
    PlayerAction.REFRESH: 0,  # replace with the emoji ID related to Refresh_v2.png
    PlayerAction.LEAVE: 0,  # replace with the emoji ID related to Leave.png
    PlayerAction.SKIP: 0,  # replace with the emoji ID related to Skip.png
    PlayerAction.SHUFFLE: 0,  # replace with the emoji ID related to Shuffle.png
    PlayerAction.LOOP: 0,  # replace with the emoji ID related to Loop.png
    PlayerAction.FAVORITE: 0,  # replace with the emoji ID related to Favorite.png
    PlayerAction.PAUSE: 0,  # replace with the emoji ID related to Pause.png
    PlayerAction.RESUME: 0,  # replace with the emoji ID related to Resume.png
    PlayerAction.LIBRARY: 0,  # replace with the emoji ID related to Library.png
    PlayerAction.HISTORY: 0,  # replace with the emoji ID related to History.png
    PlayerAction.RADIO: 0,  # replace with the emoji ID related to Radio.png
    PlayerAction.PLAYER: 0  # replace with the emoji ID related to Player.png
}


class AnilistStatus(CustomEnum):
    COMPLETED = "COMPLETED"
    CURRENT = "CURRENT"
    DROPPED = "DROPPED"
    PAUSED = "PAUSED"
    PLANNING = "PLANNING"


class RoleMenuType(CustomEnum):
    SELECT = "select"
    BUTTON = "button"


class RoleMenuMode(CustomEnum):
    SINGLE = "single"
    MULTIPLE = "multiple"


class EmojiType(CustomEnum):
    CUSTOM = "custom"
    DEFAULT = "default"


class RoleMenuImagePlacement:
    THUMBNAIL = "thumbnail"
    IMAGE = "image"


SUPPORTED_PLAYER_ACTION_IDS = {
    'resume', 'pause', 'skip',
    'disconnect', 'connect',
    'previous_page', 'next_page',
    'shuffle', 'loop', 'favorite',
    'add_track', 'refresh', 'report',
    'library', 'history', 'switch_to_radio'
}


SUPPORTED_RADIO_ACTION_IDS = {
    'disconnect', 'select_stream', 'switch_to_player', 'report', 'show_currently_playing', 'stop'
}


class Colour(CustomEnum):
    PRIMARY_ACCENT = 0xE4CAA0  # accent from pfp
    SECONDARY_ACCENT = 0xFFEA9D  # brighter

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
    ERROR = RED
    SUCCESS = GREEN
    SYSTEM = BLACK
    WARNING = BROWN
    INFO = SECONDARY_ACCENT
    UNFORTUNATE = HOT_ORANGE
    ROLE_CHANGE = BROWN

    EXT_STEAM = DEEP_BLUE
    EXT_MAL = DEEP_BLUE
    EXT_ANILIST = CLOUDY_PURPLE
    EXT_URBAN = SKY_BLUE
    EXT_MERRIAM = SKY_BLUE


class GenericColour(CustomEnum):
    RED = Colour.RED
    GREEN = Colour.GREEN
    BLACK = Colour.BLACK
    BROWN = Colour.BROWN
    WARM_GOLD = Colour.WARM_GOLD
    HOT_ORANGE = Colour.HOT_ORANGE
    SILVER = Colour.SILVER
    DEEP_BLUE = Colour.DEEP_BLUE
    SKY_BLUE = Colour.SKY_BLUE
    CLOUDY_PURPLE = Colour.CLOUDY_PURPLE
    BLURPLE = Colour.BLURPLE
    WHITE = Colour.WHITE


class XPTransferAction(Enum):
    AWARD = "award"
    TAKE_AWAY = "take away"
    RESET = "reset"


class XPTransferActionTarget(Enum):
    MEMBER = "member"
    ROLE = "role"
    EVERYONE = "everyone"


class HelpMenuType(CustomEnum):
    USER = "User"
    MUSIC = "Music"
    ADMIN = "Admin"


class GeneralButtonEmoji:
    # todo
    """
    Same as PLAYER_ACTION_CUSTOM_EMOJI_MAP - if you haven't uploaded images in this folder as emojis yet, do it now:
    https://drive.google.com/drive/folders/1mQgvzT45KcSR3Fcs6AQkcRgCotY79uO-?usp=sharing
    """
    GO_BACK = 0  # replace with the emoji ID related to Back.png
    RENAME = 0  # replace with the emoji ID related to Rename.png
    COPY = 0  # replace with the emoji ID related to Copy.png
    CLEAR = 0  # replace with the emoji ID related to Clear.png
    DELETE = 0  # replace with the emoji ID related to Delete.png
    MERGE = 0  # replace with the emoji ID related to Merge.png
    MOVE = 0  # replace with the emoji ID related to Move.png
    PREVIOUS = 0  # replace with the emoji ID related to Previous.png
    NEXT = 0  # replace with the emoji ID related to Next.png
    ADD = 0  # replace with the emoji ID related to Add.png
    REMOVE = 0  # replace with the emoji ID related to Remove.png
    SWITCH = 0  # replace with the emoji ID related to Switch.png
    SETTINGS = 0  # replace with the emoji ID related to Settings.png


PING_WORTHY_LOG_LEVELS = [
    BotLogLevel.ERROR,
    BotLogLevel.WARNING,
    BotLogLevel.GUILD_JOIN,
    BotLogLevel.GUILD_LEAVE,
    BotLogLevel.RECEIVED_DM
]


class BackgroundWorker(CustomEnum):
    # PERIODIC WORKERS (run every specified interval)
    # worker for sending reminders
    REMINDER_SERVICE = "Reminder Service"
    # worker for cleaning cache (web requests, yt info)
    CACHE_CLEANUP = "Cache Cleanup"
    # worker for syncing xp with the database
    XP_SYNC = "XP Sync"
    # worker for enqueuing members pending xp decay
    XP_DECAY_ENQUEUE = "XP Decay Enqueue"
    # worker for decaying members XP
    XP_DECAY = "XP Decay"
    # worker for processing messages for xp gain
    XP_GAIN = "XP Gain"
    # worker for adjusting members XP (e.g. for xp decay, commands)
    XP_ADJUSTMENT = "XP Adjustment"
    # worker for loading recently queued music locally
    MUSIC_DOWNLOADER = "Music Downloader"

    # SELF-SCHEDULING WORKERS (worker decides when to run again)
    # none yet


PERIODIC_WORKER_FREQUENCY = {
    BackgroundWorker.REMINDER_SERVICE: 5,
    BackgroundWorker.CACHE_CLEANUP: 60,
    BackgroundWorker.XP_SYNC: 45,
    BackgroundWorker.XP_DECAY_ENQUEUE: 3600,
    BackgroundWorker.XP_DECAY: 300,
    BackgroundWorker.MUSIC_DOWNLOADER: 5,
    BackgroundWorker.XP_ADJUSTMENT: 3,
    BackgroundWorker.XP_GAIN: 0.1,
}

WORKER_RETRY_ON_ERROR_DELAY = {
    BackgroundWorker.REMINDER_SERVICE: 5,
    BackgroundWorker.CACHE_CLEANUP: 60,
    BackgroundWorker.XP_SYNC: 45,
    BackgroundWorker.XP_DECAY_ENQUEUE: 7200,
    BackgroundWorker.XP_DECAY: 600,
    BackgroundWorker.MUSIC_DOWNLOADER: 30,
    BackgroundWorker.XP_ADJUSTMENT: 3,
    BackgroundWorker.XP_GAIN: 0.1,
}


class MusicServiceMode(CustomEnum):
    PLAYER = "player"
    RADIO = "radio"


class MusicLogAction(CustomEnum):
    CONNECTED_BOT = "connect_bot"
    SWITCHED_TO_RADIO = "switched_to_radio"
    SWITCHED_TO_PLAYER = "switched_to_player"
    DISCONNECTED_BOT = "disconnect_bot"
    ADDED_TRACK = "add_track"
    REMOVED_TRACK = "remove_track"
    SKIPPED_TRACK = "skipped_track"
    MOVED_TRACK = "moved_track"
    TRACK_SEEK = "track_seek"
    REPLAYED_TRACK = "replayed_track"
    CLEARED_QUEUE = "cleared_queue"
    CHANGED_LOOP_MODE = "changed_loop_mode"
    SHUFFLED_QUEUE = "shuffled_queue"
    CHANGED_RADIO_STREAM = "changed_radio_stream"
    FORCE_PLAYED_TRACK = "force_played_track"
    PAUSED_PLAYBACK = "paused_playback"
    RESUMED_PLAYBACK = "resumed_playback"


COUNTABLE_MUSIC_LOG_ACTIONS = [
    MusicLogAction.ADDED_TRACK,
    MusicLogAction.REMOVED_TRACK,
    MusicLogAction.SKIPPED_TRACK,
    MusicLogAction.MOVED_TRACK,
    MusicLogAction.REPLAYED_TRACK,
    MusicLogAction.SHUFFLED_QUEUE,
    MusicLogAction.FORCE_PLAYED_TRACK
]
