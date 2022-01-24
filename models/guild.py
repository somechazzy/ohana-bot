from globals_.constants import XPSettingsKey, DEFAULT_PREFIX, DEFAULT_ADMIN_PREFIX, \
    ENCRYPTED_CHARACTERS, DEFAULT_LEVELUP_MESSAGE, DEFAULT_LEVEL_ROLE_EARN_MESSAGE, DEFAULT_MIN_XP_GIVEN, \
    DEFAULT_TIMEFRAME_FOR_XP, DEFAULT_MAX_XP_GIVEN, DEFAULT_XP_DECAY_PERCENTAGE, DEFAULT_XP_DECAY_DAYS, \
    MessageCountMode, DEFAULT_MUSIC_PREFIX
from .member import MemberXP


class GuildPrefs:
    def __init__(self, guild_id: int, guild_name: str):

        self._guild_id = guild_id
        self._guild_name = guild_name
        self._currently_in_guild = True

        self._prefix = DEFAULT_PREFIX
        self._admin_prefix = DEFAULT_ADMIN_PREFIX
        self._music_prefix = DEFAULT_MUSIC_PREFIX
        self._autoroles = []
        self._auto_responses = {}
        self._dj_roles = []

        self._spam_channel = 0
        self._logs_channel = 0
        self._music_channel = 0
        self._music_header_message = 0
        self._music_player_message = 0

        self._fun_commands_enabled = True
        self._utility_commands_enabled = True
        self._mal_al_commands_enabled = True
        self._xp_commands_enabled = True
        self._moderation_commands_enabled = True

        self._role_persistence_enabled = False
        self._default_banned_words_enabled = False
        self._whitelisted_role = 0
        self._banned_words = {}
        self._single_message_channels = {}
        self._gallery_channels = []
        self._react_roles = {}
        self._anime_channels = []

        self._xp_settings = {
            XPSettingsKey.XP_GAIN_ENABLED: True,
            XPSettingsKey.XP_GAIN_TIMEFRAME: DEFAULT_TIMEFRAME_FOR_XP,
            XPSettingsKey.XP_GAIN_MIN: DEFAULT_MIN_XP_GIVEN,
            XPSettingsKey.XP_GAIN_MAX: DEFAULT_MAX_XP_GIVEN,
            XPSettingsKey.MESSAGE_COUNT_MODE: MessageCountMode.PER_MESSAGE,
            XPSettingsKey.LEVELUP_ENABLED: False,
            XPSettingsKey.LEVELUP_CHANNEL: 0,
            XPSettingsKey.LEVELUP_MESSAGE: DEFAULT_LEVELUP_MESSAGE,
            XPSettingsKey.LEVEL_MAX: 0,
            XPSettingsKey.XP_DECAY_ENABLED: False,
            XPSettingsKey.PERCENTAGE_OF_XP_DECAY_PER_DAY: DEFAULT_XP_DECAY_PERCENTAGE,
            XPSettingsKey.DAYS_BEFORE_XP_DECAY: DEFAULT_XP_DECAY_DAYS,
            XPSettingsKey.LEVEL_ROLES: {},
            XPSettingsKey.LEVEL_ROLE_EARN_MESSAGE: DEFAULT_LEVEL_ROLE_EARN_MESSAGE,
            XPSettingsKey.STACK_ROLES: True,
            XPSettingsKey.BOOST_EXTRA_GAIN: 0.0,
            XPSettingsKey.IGNORED_CHANNELS: [],
            XPSettingsKey.IGNORED_ROLES: [],
        }

    @property
    def guild_id(self):
        return self._guild_id

    def set_guild_id(self, guild_id):
        self._guild_id = int(guild_id)

    @property
    def guild_name(self):
        return self._guild_name

    def set_guild_name(self, guild_name: str):
        if not guild_name:
            guild_name = "NO_GUILD_NAME"
        self._guild_name = guild_name

    @property
    def currently_in_guild(self):
        return self._currently_in_guild

    def set_currently_in_guild(self, currently_in_guild: bool):
        if not currently_in_guild:
            currently_in_guild = False
        self._currently_in_guild = currently_in_guild

    @property
    def prefix(self):
        return self._prefix

    def set_prefix(self, prefix: str):
        if not prefix:
            prefix = DEFAULT_PREFIX
        self._prefix = prefix

    @property
    def admin_prefix(self):
        return self._admin_prefix

    def set_admin_prefix(self, admin_prefix: str):
        if not admin_prefix:
            admin_prefix = DEFAULT_ADMIN_PREFIX
        self._admin_prefix = admin_prefix

    @property
    def music_prefix(self):
        return self._music_prefix

    def set_music_prefix(self, music_prefix: str):
        if not music_prefix:
            music_prefix = DEFAULT_MUSIC_PREFIX
        self._music_prefix = music_prefix

    @property
    def autoroles(self):
        return self._autoroles

    def set_autoroles(self, autoroles: []):
        if not autoroles:
            autoroles = []
        for autorole in autoroles:
            self._autoroles.append(int(autorole))

    def add_autorole(self, autorole: int):
        if autorole in self._autoroles:
            return
        self._autoroles.append(autorole)

    def remove_autorole(self, autorole: int):
        while autorole in self._autoroles:
            self._autoroles.remove(autorole)

    @property
    def auto_responses(self):
        return self._auto_responses

    def set_auto_responses(self, auto_responses: dict):
        if not auto_responses:
            auto_responses = {}
        for key in auto_responses.keys():
            self._auto_responses[get_decrypted_string(key)] = auto_responses[key]

    def add_auto_response(self, trigger: str, auto_response: dict):
        if trigger in self._auto_responses.keys():
            return
        self._auto_responses[trigger] = auto_response

    def remove_auto_response(self, trigger: str):
        while trigger in self._auto_responses.keys():
            self._auto_responses.pop(trigger)

    @property
    def dj_roles(self):
        return self._dj_roles

    def set_dj_roles(self, dj_roles: []):
        if not dj_roles:
            dj_roles = []
        for dj_role in dj_roles:
            self._dj_roles.append(int(dj_role))

    def add_dj_role(self, dj_role: int):
        if dj_role in self._dj_roles:
            return
        self._dj_roles.append(dj_role)

    def remove_dj_role(self, dj_role: int):
        while dj_role in self._dj_roles:
            self._dj_roles.remove(dj_role)

    @property
    def spam_channel(self):
        return self._spam_channel

    def set_spam_channel(self, spam_channel: int):
        if not spam_channel:
            spam_channel = 0
        self._spam_channel = int(spam_channel)

    @property
    def logs_channel(self):
        return self._logs_channel

    def set_logs_channel(self, logs_channel: int):
        if not logs_channel:
            logs_channel = 0
        self._logs_channel = int(logs_channel)

    @property
    def music_channel(self):
        return self._music_channel

    def set_music_channel(self, music_channel: int):
        if not music_channel:
            music_channel = 0
        self._music_channel = int(music_channel)

    @property
    def music_header_message(self):
        return self._music_header_message

    def set_music_header_message(self, music_header_message: int):
        if not music_header_message:
            music_header_message = 0
        self._music_header_message = int(music_header_message)

    @property
    def music_player_message(self):
        return self._music_player_message

    def set_music_player_message(self, music_player_message: int):
        if not music_player_message:
            music_player_message = 0
        self._music_player_message = int(music_player_message)

    @property
    def fun_commands_enabled(self):
        return self._fun_commands_enabled

    def set_fun_commands_enabled(self, fun_commands_enabled: bool):
        if fun_commands_enabled is None:
            fun_commands_enabled = True
        self._fun_commands_enabled = fun_commands_enabled

    @property
    def utility_commands_enabled(self):
        return self._utility_commands_enabled

    def set_utility_commands_enabled(self, utility_commands_enabled: bool):
        if utility_commands_enabled is None:
            utility_commands_enabled = True
        self._utility_commands_enabled = utility_commands_enabled

    @property
    def mal_al_commands_enabled(self):
        return self._mal_al_commands_enabled

    def set_mal_al_commands_enabled(self, mal_al_commands_enabled: bool):
        if mal_al_commands_enabled is None:
            mal_al_commands_enabled = True
        self._mal_al_commands_enabled = mal_al_commands_enabled

    @property
    def xp_commands_enabled(self):
        return self._xp_commands_enabled

    def set_xp_commands_enabled(self, xp_commands_enabled: bool):
        if xp_commands_enabled is None:
            xp_commands_enabled = True
        self._xp_commands_enabled = xp_commands_enabled

    @property
    def moderation_commands_enabled(self):
        return self._moderation_commands_enabled

    def set_moderation_commands_enabled(self, moderation_commands_enabled: bool):
        if moderation_commands_enabled is None:
            moderation_commands_enabled = True
        self._moderation_commands_enabled = moderation_commands_enabled

    @property
    def default_banned_words_enabled(self):
        return self._default_banned_words_enabled

    def set_default_banned_words_enabled(self, default_banned_words_enabled: bool):
        if default_banned_words_enabled is None:
            default_banned_words_enabled = False
        self._default_banned_words_enabled = default_banned_words_enabled

    @property
    def role_persistence_enabled(self):
        return self._role_persistence_enabled

    def set_role_persistence_enabled(self, role_persistence_enabled: bool):
        if role_persistence_enabled is None:
            role_persistence_enabled = False
        self._role_persistence_enabled = role_persistence_enabled

    @property
    def banned_words(self):
        return self._banned_words

    def set_banned_words(self, banned_words: {}):
        if not banned_words:
            banned_words = {}
        for key in banned_words.keys():
            self._banned_words[get_decrypted_string(key)] = banned_words[key]

    def add_banned_word(self, banned_word: str, banned_word_dict: dict):
        if banned_word in self.banned_words.keys():
            return
        self._banned_words[banned_word] = banned_word_dict

    def remove_banned_word(self, banned_word: str):
        while banned_word in self.banned_words.keys():
            self._banned_words.pop(banned_word)

    @property
    def single_message_channels(self):
        return self._single_message_channels

    def set_single_message_channels(self, single_message_channels: {}):
        if not single_message_channels:
            single_message_channels = {}
        for key in single_message_channels.keys():
            self._single_message_channels[int(get_decrypted_string(key))] = single_message_channels[key]

    def add_single_message_channel(self, single_message_channel: int, single_message_channel_dict: dict):
        if single_message_channel in self.single_message_channels.keys():
            return
        self._single_message_channels[int(single_message_channel)] = single_message_channel_dict

    def remove_single_message_channel(self, single_message_channel: int):
        while single_message_channel in self.single_message_channels.keys():
            self._single_message_channels.pop(int(single_message_channel))

    @property
    def gallery_channels(self):
        return self._gallery_channels

    def set_gallery_channels(self, gallery_channels: []):
        if not gallery_channels:
            gallery_channels = []
        for channel in gallery_channels:
            self._gallery_channels.append(int(channel))

    def add_gallery_channel(self, gallery_channel: int):
        if gallery_channel in self.gallery_channels:
            return
        self._gallery_channels.append(int(gallery_channel))

    def remove_gallery_channel(self, gallery_channel: int):
        while gallery_channel in self.gallery_channels:
            self._gallery_channels.remove(gallery_channel)

    @property
    def react_roles(self):
        return self._react_roles

    def set_react_roles(self, react_roles: {}):
        if not react_roles:
            react_roles = {}
        self._integerify_react_roles_data(react_roles)

    def add_react_role(self, channel_id: int, message_id: int, emoji_id: int, role_id: int):
        if channel_id not in self._react_roles:
            self._react_roles[channel_id] = {}
        if message_id not in self._react_roles[channel_id]:
            self._react_roles[channel_id][message_id] = {}
        if emoji_id not in self._react_roles[channel_id][message_id]:
            self._react_roles[channel_id][message_id][emoji_id] = role_id

    def remove_react_role(self, channel_id: int, message_id: int, emoji_id: int, ):
        if self._react_roles.get(channel_id, {}).get(message_id, {}).get(emoji_id, None):
            del self._react_roles[channel_id][message_id][emoji_id]

    @property
    def whitelisted_role(self):
        return self._whitelisted_role

    def set_whitelisted_role(self, whitelisted_role: int):
        if not whitelisted_role:
            whitelisted_role = 0
        self._whitelisted_role = int(whitelisted_role)

    @property
    def anime_channels(self):
        return self._anime_channels

    def set_anime_channels(self, anime_channels: []):
        if not anime_channels:
            anime_channels = []
        for channel in anime_channels:
            self._anime_channels.append(int(channel))

    def add_anime_channel(self, anime_channel: int):
        if anime_channel in self.anime_channels:
            return
        self._anime_channels.append(int(anime_channel))

    def remove_anime_channel(self, anime_channel: int):
        while anime_channel in self.anime_channels:
            self._anime_channels.remove(anime_channel)

    @property
    def xp_settings(self):
        return self._xp_settings

    def set_xp_settings(self, xp_settings: {}):
        if not xp_settings:
            return
        for key, value in xp_settings.items():
            self._xp_settings[key] = value

    def stringify_values(self):
        self._guild_id = str(self._guild_id)

        str_autoroles = []
        for autorole in self._autoroles:
            str_autoroles.append(str(autorole))
        self._autoroles = str_autoroles

        self._spam_channel = str(self._spam_channel)
        self._logs_channel = str(self._logs_channel)
        self._music_channel = str(self._music_channel)
        self._music_header_message = str(self._music_header_message)
        self._music_player_message = str(self._music_player_message)
        self._whitelisted_role = str(self._whitelisted_role)

        str_gallery = []
        for gallery_channel in self._gallery_channels:
            str_gallery.append(str(gallery_channel))
        self._gallery_channels = str_gallery

        for key in self._single_message_channels.keys():
            self._single_message_channels[key]['channel_id'] =\
                str(self._single_message_channels[key].get('channel_id', 0))
            self._single_message_channels[key]['role_id'] = str(self._single_message_channels[key].get('role_id', 0))

        str_anime = []
        for anime_channel in self._anime_channels:
            str_anime.append(str(anime_channel))
        self._anime_channels = str_anime

        self._xp_settings = self.stringify_xp_settings_values(self._xp_settings)

        return self

    def destringify_values(self):
        self._guild_id = int(self._guild_id)

        int_autoroles = []
        for autorole in self._autoroles:
            int_autoroles.append(int(autorole))
        self._autoroles = int_autoroles

        self._spam_channel = int(self._spam_channel)
        self._logs_channel = int(self._logs_channel)
        self._music_channel = int(self._music_channel)
        self._music_header_message = int(self._music_header_message)
        self._music_player_message = int(self._music_player_message)
        self._whitelisted_role = int(self._whitelisted_role)

        int_gallery = []
        for gallery_channel in self._gallery_channels:
            int_gallery.append(int(gallery_channel))
        self._gallery_channels = int_gallery

        for key in self._single_message_channels.keys():
            self._single_message_channels[key]['channel_id'] = \
                int(self._single_message_channels[key].get('channel_id', 0))
            self._single_message_channels[key]['role_id'] = int(self._single_message_channels[key].get('role_id', 0))

        int_anime = []
        for anime_channel in self._anime_channels:
            int_anime.append(int(anime_channel))
        self._anime_channels = int_anime

        self._xp_settings = self.destringify_xp_settings_values(self._xp_settings)

        return self

    @staticmethod
    def stringify_xp_settings_values(xp_settings: dict):
        xp_settings[XPSettingsKey.LEVELUP_CHANNEL] = str(xp_settings[XPSettingsKey.LEVELUP_CHANNEL])

        str_ignored_channels = [str(i) for i in xp_settings[XPSettingsKey.IGNORED_CHANNELS]]
        xp_settings[XPSettingsKey.IGNORED_CHANNELS] = str_ignored_channels

        str_ignored_roles = [str(i) for i in xp_settings[XPSettingsKey.IGNORED_ROLES]]
        xp_settings[XPSettingsKey.IGNORED_ROLES] = str_ignored_roles

        for key, value in xp_settings[XPSettingsKey.LEVEL_ROLES].items():
            xp_settings[XPSettingsKey.LEVEL_ROLES][key] = str(value)

        return xp_settings

    @staticmethod
    def destringify_xp_settings_values(xp_settings: dict):
        xp_settings[XPSettingsKey.LEVELUP_CHANNEL] = int(xp_settings[XPSettingsKey.LEVELUP_CHANNEL])

        str_ignored_channels = [int(i) for i in xp_settings[XPSettingsKey.IGNORED_CHANNELS]]
        xp_settings[XPSettingsKey.IGNORED_CHANNELS] = str_ignored_channels

        str_ignored_roles = [int(i) for i in xp_settings[XPSettingsKey.IGNORED_ROLES]]
        xp_settings[XPSettingsKey.IGNORED_ROLES] = str_ignored_roles

        new_level_roles_dict = {}
        for key, value in xp_settings[XPSettingsKey.LEVEL_ROLES].items():
            new_level_roles_dict[int(key)] = int(value)
        xp_settings[XPSettingsKey.LEVEL_ROLES] = new_level_roles_dict

        return xp_settings

    def _integerify_react_roles_data(self, react_roles):
        if not react_roles:
            return {}
        for channel_id_str, message_dicts in react_roles.items():
            self._react_roles[int(channel_id_str)] = {}
            for message_id_str, emoji_role_dict in message_dicts.items():
                self._react_roles[int(channel_id_str)][int(message_id_str)] = {}
                for emoji_id_str, role_id in emoji_role_dict.items():
                    self._react_roles[int(channel_id_str)][int(message_id_str)][int(emoji_id_str)] = int(role_id)


class GuildXP:
    def __init__(self, guild_id: int):

        self._guild_id = guild_id
        self._synced = True
        self._members_xp = {
            0: MemberXP(0)
        }

    @property
    def guild_id(self):
        return self._guild_id

    def set_guild_id(self, guild_id):
        self._guild_id = int(guild_id)

    @property
    def synced(self):
        return self._synced

    def set_synced(self, synced):
        self._synced = synced

    @property
    def members_xp(self):
        return self._members_xp

    def set_members_xp(self, members_xp):
        self._members_xp = members_xp.copy()


def get_decrypted_string(text: str):
    for symbol in ENCRYPTED_CHARACTERS.keys():
        text = text.replace(ENCRYPTED_CHARACTERS[symbol], symbol)
    return text
