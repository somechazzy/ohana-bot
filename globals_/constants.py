import settings

BOT_NAME = settings.BOT_NAME

DEFAULT_PREFIX = settings.DEFAULT_PREFIX
DEFAULT_MUSIC_PREFIX = settings.DEFAULT_MUSIC_PREFIX
DEFAULT_ADMIN_PREFIX = settings.DEFAULT_ADMIN_PREFIX

BOT_OWNER_ID = settings.BOT_OWNER_ID
DISCORD_LOGGING_CHANNEL_ID = settings.DISCORD_LOGGING_CHANNEL_ID
MY_TIMEZONE = settings.MY_TIMEZONE

CACHE_CLEANUP_FREQUENCY_SECONDS = settings.CACHE_CLEANUP_FREQUENCY_SECONDS
GUILDS_XP_SYNC_FREQUENCY_SECONDS = settings.GUILDS_XP_SYNC_FREQUENCY_SECONDS

AR_LIMIT_SECONDS = settings.AR_LIMIT_SECONDS
COMMAND_LIMIT_X_SECONDS = settings.COMMAND_LIMIT_X_SECONDS
COMMAND_LIMIT_PER_X_SECONDS = settings.COMMAND_LIMIT_PER_X_SECONDS

BOT_INVITE = settings.BOT_INVITE

DEFAULT_LEVELUP_MESSAGE = settings.DEFAULT_LEVELUP_MESSAGE
DEFAULT_LEVEL_ROLE_EARN_MESSAGE = settings.DEFAULT_LEVEL_ROLE_EARN_MESSAGE
DEFAULT_TIMEFRAME_FOR_XP = settings.DEFAULT_TIMEFRAME_FOR_XP
DEFAULT_MIN_XP_GIVEN = settings.DEFAULT_MIN_XP_GIVEN
DEFAULT_MAX_XP_GIVEN = settings.DEFAULT_MAX_XP_GIVEN
DEFAULT_XP_DECAY_PERCENTAGE = settings.DEFAULT_XP_DECAY_PERCENTAGE
DEFAULT_XP_DECAY_DAYS = settings.DEFAULT_XP_DECAY_DAYS

DEFAULT_PLAYER_CHANNEL_EMBED_MESSAGE_CONTENT = settings.DEFAULT_PLAYER_CHANNEL_EMBED_MESSAGE_CONTENT
PLAYER_HEADER_IMAGE = settings.PLAYER_HEADER_IMAGE
PLAYER_IDLE_IMAGE = settings.PLAYER_IDLE_IMAGE

HELP_EMBED_THUMBNAIL = settings.HELP_EMBED_THUMBNAIL
BOT_COLOR = settings.BOT_COLOR


class OhanaEnum:
    @classmethod
    def as_list(cls):
        return [value for key, value in cls.__dict__.items() if not key.startswith('_')]

    @classmethod
    def __iter__(cls):
        return cls.as_list().__iter__()


class BotLogType(OhanaEnum):
    BOT_INFO = "Bot Info"
    RECEIVED_DM = "Received DM"
    MEMBER_INFO = "Member Info"
    GUILD_CHANGE = "Guild Change"
    GUILD_ERROR = "Guild Error"
    GUILD_JOIN = "Guild Join"
    GUILD_LEAVE = "Guild Leave"
    BOT_ERROR = "Bot Error"
    BOT_WARNING = "Bot Warning"
    BOT_WARNING_IGNORE = "Minor Bot Warning"
    MESSAGE_SENT = "Message Sent"
    REPLY_SENT = "Reply Sent"
    MESSAGE_DELETED = "Message Deleted"
    MESSAGE_EDITED = "Message Edited"
    AUTO_RESPOND = "Auto Respond"
    USER_COMMAND_RECEIVED = "User Command Received"
    MUSIC_COMMAND_RECEIVED = "Music Command Received"
    ADMIN_COMMAND_RECEIVED = "Admin Command Received"
    UNRECOGNIZED_COMMAND_RECEIVED = "Unrecognized Command Received"
    GENERAL = "General"
    PERM_ERROR = "Permission Error"


class GuildLogType(OhanaEnum):
    MEMBER_JOINED = "Member Joined"
    MEMBER_LEFT = "Member Left"
    ASSIGNED_ROLE = "Assigned Role"
    UNASSIGNED_ROLE = "Unassigned Role"
    ASSIGNED_ROLES = "Assigned Roles"
    EDITED_ROLES = "Edited Roles"
    CREATED_ROLE = "Created Role"
    KICKED_MEMBER = "Kicked Member"
    BANNED_MEMBER = "Banned Member"
    MUTED_MEMBER = "Muted Member"
    UNMUTED_MEMBER = "Unmuted Member"
    DELETED_MESSAGE = "Deleted Message"
    PERM_ERROR = "Permission Error"
    ACTION_ERROR = "Action Error"
    SETTING_CHANGE = f"{BOT_NAME} Setting Change"
    GENERAL = "General"


class CommandType(OhanaEnum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    MUSIC = 'MUSIC'


class UserCommandSection(OhanaEnum):
    FUN = "Fun"
    UTILITY = "Utility"
    ANIME_AND_MANGA = "Anime and Manga"
    XP = 'XP and Levels'
    MODERATION = "Moderation"
    OTHER = "Other"


class AdminCommandSection(OhanaEnum):
    GENERAL = "General"
    PREFIX = "Prefix"
    CHANNELS = "Channels"
    MODULES = "Modules"
    AUTOMOD = "Automod"
    XP = "XP and Levels"


class MusicCommandSection(OhanaEnum):
    GENERAL = "General"
    PLAYBACK = "Playback"
    QUEUE = "Queue"


class HelpListingVisibility(OhanaEnum):
    HIDE = "Hide"
    SHOW = "Show"
    PARTIAL = "Only section specific"


class CachingType(OhanaEnum):
    MAL_INFO_ANIME = "MAL_INFO_ANIME"
    MAL_INFO_MANGA = "MAL_INFO_MANGA"
    MAL_SEARCH_ANIME = "MAL_SEARCH_ANIME"
    MAL_SEARCH_MANGA = "MAL_SEARCH_MANGA"
    MAL_PROFILE = "MAL_PROFILE"
    MAL_LIST_ANIME = "MAL_LIST_ANIME"
    MAL_LIST_MANGA = "MAL_LIST_MANGA"
    AL_PROFILE = "AL_PROFILE"
    AL_LISTS = "AL_LISTS"
    URBAN_DICTIONARY = "URBAN_DICTIONARY"
    MERRIAM_DICTIONARY = "MERRIAM_DICTIONARY"
    STEAM_GAME_SEARCH = "STEAM_GAME_SEARCH"
    DISCORD_AVATAR = "DISCORD_AVATAR"
    SPOTIFY_INFO = "SPOTIFY_INFO"
    SPOTIFY_PLAYLIST = "SPOTIFY_PLAYLIST"


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
    CachingType.STEAM_GAME_SEARCH: 600,
    CachingType.DISCORD_AVATAR: 20,
    CachingType.SPOTIFY_INFO: 1440,
    CachingType.SPOTIFY_PLAYLIST: 5
}

LETTER_EMOTES_COMMANDS = {
    "f": "🎈",
    "u": "🧰",
    "a": "👀",
    "x": "🏅",
    "m": "🚓",
    "o": "📄",
}

LETTER_EMOTES_ADMIN_COMMANDS = {
    "g": "🤖",
    "p": "🚀",
    "c": "💬",
    "m": "🖇",
    "a": "👮",
    "x": "🏅"
}

LETTER_EMOTES_MUSIC_COMMANDS = {
    "g": "🤖",
    "p": "🎵",
    "q": "📜"
}

USER_COMMAND_SECTION_TOP_COMMANDS = {
    UserCommandSection.UTILITY: ["avatar", "remindMe", "serverInfo"],
    UserCommandSection.ANIME_AND_MANGA: ["anime", "manga", "mal", "anilist"],
    UserCommandSection.FUN: ["snipe", "uwufy"],
    UserCommandSection.XP: ["level", "leaderboard", "roles"],
    UserCommandSection.MODERATION: ["mute", "kick", "ban"],
    UserCommandSection.OTHER: ["invite", "feedback"],
}

ADMIN_COMMAND_SECTION_TOP_COMMANDS = {
    AdminCommandSection.GENERAL: ["overview", "help"],
    AdminCommandSection.PREFIX: ["prefix", "musicPrefix", "adminPrefix"],
    AdminCommandSection.AUTOMOD: ["autoroles", "rolePersistence", "autoResponses"],
    AdminCommandSection.CHANNELS: ["logsChannel", "spamChannel"],
    AdminCommandSection.MODULES: ["enable", "disable"],
    AdminCommandSection.XP: ["LevelUpMessage", "LevelUpRoles", "xpDecay"],
}

MUSIC_COMMAND_SECTION_TOP_COMMANDS = {
    MusicCommandSection.GENERAL: ["setup", "dj", "history", "leave"],
    MusicCommandSection.PLAYBACK: ["play", "search", "now", "pause", "seek", "lyrics"],
    MusicCommandSection.QUEUE: ["queue", "move", "shuffle", "loop", "skip", "skipTo", "remove"]
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

EMOJI_NUMBER_MAP = {
    "1️⃣": 0,
    "2️⃣": 1,
    "3️⃣": 2,
    "4️⃣": 3,
    "5️⃣": 4,
    "6️⃣": 5,
    "7️⃣": 6,
    "8️⃣": 7,
    "9️⃣": 8,
    "🔟": 9
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

# yeah sorry you're gonna have to fill these on your own
# partial means they can be a word on their own or part of a word, full means they must be a word on their own
BLACKLISTED_WORDS_PARTIAL = [
]

BLACKLISTED_WORDS_FULL = [
]

UWUFY_FACES = [
    '(*^ω^)',
    '(◕ᴥ◕)',
    'ʕ￫ᴥ￩ʔ',
    '>////<',
    'uwu',
    'UwU',
    '(*￣з￣)',
    '>w<',
    '^w^',
    '(つ✧ω✧)つ',
    '(/ =ω=)/',
    '(⁄ ⁄•⁄ω⁄•⁄ ⁄)'
]

ANILIST_SCORING_SYSTEM = {
    "POINT_100": "0-100",
    "POINT_10_DECIMAL": "0-10",
    "POINT_10": "0-10",
    "POINT_5": "0-5",
    "POINT_3": "0-3",
    "-": "Unknown"
}

ENCRYPTED_CHARACTERS = {
    "$": "%dollar_sign%",
    "#": "%hash_sign%",
    "[": "%opening_square_bracket%",
    "]": "%closing_square_bracket%",
    ".": "%dot_sign%"
}

IGNORED_UNRECOGNIZED_COMMANDS = [
    'claim',
    'daily',
    'eval',
    'meme',
    'mar',
    'fde',
    'he',
    'hourly',
    'lottery',
    'play',
    'queue',
    'shuffle',
    'next',
    'google',
    'music',
    'rep',
    'dice',
    'lootbox',
    'chop',
    'fish',
    'colisee',
    'remove',
    'boat',
    'skip',
    'crew',
    'profile',
    'battle',
    'chap',
    'train'
]


class MerriamDictionaryResponseType(OhanaEnum):
    SUCCESS = "Success"
    NOT_FOUND = "Not Found"
    OTHER = "Other"


class XPSettingsKey(OhanaEnum):
    IGNORED_CHANNELS = "IGNORED_CHANNELS"
    IGNORED_ROLES = "IGNORED_ROLES"

    XP_GAIN_ENABLED = "XP_GAIN_ENABLED"
    XP_GAIN_TIMEFRAME = "XP_GAIN_TIME_FRAME"
    XP_GAIN_MIN = "XP_GAIN_MIN"
    XP_GAIN_MAX = "XP_GAIN_MAX"
    MESSAGE_COUNT_MODE = "MESSAGE_COUNT_MODE"

    LEVELUP_ENABLED = "LEVELUP_ENABLED"
    LEVELUP_CHANNEL = "LEVELUP_CHANNEL"
    LEVELUP_MESSAGE = "LEVELUP_MESSAGE"
    LEVEL_ROLES = "LEVEL_ROLES"
    LEVEL_ROLE_EARN_MESSAGE = "LEVEL_ROLE_EARN_MESSAGE"
    STACK_ROLES = "STACK_ROLES"
    LEVEL_MAX = "LEVEL_MAX"

    XP_DECAY_ENABLED = "XP_DECAY_ENABLED"
    PERCENTAGE_OF_XP_DECAY_PER_DAY = "PERCENTAGE_OF_XP_DECAY_PER_DAY"
    DAYS_BEFORE_XP_DECAY = "DAYS_BEFORE_XP_DECAY"

    BOOST_EXTRA_GAIN = "BOOST_EXTRA_GAIN"
    ROLES_EXTRA_GAIN = "ROLES_EXTRA_GAIN"


class AdminSettingsAction(OhanaEnum):
    ADD = "add"
    REMOVE = "remove"
    CLEAR = "clear"


class MessageCountMode(OhanaEnum):
    PER_TIMEFRAME = 0
    PER_MESSAGE = 1


class OSType(OhanaEnum):
    LINUX = 'Linux'
    WINDOWS = 'Windows'
    OTHER = 'Other'


class MusicVCState(OhanaEnum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    PLAYING = "playing"


class MusicVCLoopMode(OhanaEnum):
    NONE = "none"
    ALL = "all"
    ONE = "one"


NEXT_MUSIC_VC_LOOP_MODE = {
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


class MusicTrackSource(OhanaEnum):
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"


GENERIC_YOUTUBE_TITLE_WORDS = [
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

GENERIC_YOUTUBE_TITLE_WORDS_TO_REMOVE = [
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


class PlayerAction(OhanaEnum):
    JOIN = "JOIN"
    RESUME_PAUSE = "RESUME_PAUSE"
    REFRESH = "REFRESH"
    LEAVE = "LEAVE"
    SKIP = "SKIP"
    SHUFFLE = "SHUFFLE"
    LOOP = "LOOP"
    FAVORITE = "FAVORITE"
    PREVIOUS = "PREVIOUS"
    NEXT = "NEXT"


CUSTOM_EMOJI_PLAYER_ACTION_MAP = {
    settings.PLAYER_JOIN_EMOJI_ID: PlayerAction.JOIN,
    settings.PLAYER_RESUME_PAUSE_EMOJI_ID: PlayerAction.RESUME_PAUSE,
    settings.PLAYER_REFRESH_EMOJI_ID: PlayerAction.REFRESH,
    settings.PLAYER_LEAVE_EMOJI_ID: PlayerAction.LEAVE,
    settings.PLAYER_SKIP_EMOJI_ID: PlayerAction.SKIP,
    settings.PLAYER_SHUFFLE_EMOJI_ID: PlayerAction.SHUFFLE,
    settings.PLAYER_LOOP_EMOJI_ID: PlayerAction.LOOP,
    settings.PLAYER_FAVORITE_EMOJI_ID: PlayerAction.FAVORITE,
    settings.PLAYER_PREVIOUS_EMOJI_ID: PlayerAction.PREVIOUS,
    settings.PLAYER_NEXT_EMOJI_ID: PlayerAction.NEXT
}

DEFAULT_EMOJI_PLAYER_ACTION_MAP = {
    "▶️": PlayerAction.JOIN,
    "⏯️": PlayerAction.RESUME_PAUSE,
    "♻️": PlayerAction.REFRESH,
    "⏹️": PlayerAction.LEAVE,
    "⏭️": PlayerAction.SKIP,
    "🔀": PlayerAction.SHUFFLE,
    "🔁": PlayerAction.LOOP,
    "🌟": PlayerAction.FAVORITE,
    "⬅️": PlayerAction.PREVIOUS,
    "➡️": PlayerAction.NEXT
}


class AnilistStatus(OhanaEnum):
    COMPLETED = "COMPLETED"
    CURRENT = "CURRENT"
    DROPPED = "DROPPED"
    PAUSED = "PAUSED"
    PLANNING = "PLANNING"
