from globals_.constants import XPSettingsKey, ENCRYPTED_CHARACTERS, DEFAULT_LEVELUP_MESSAGE, \
    DEFAULT_LEVEL_ROLE_EARN_MESSAGE, DEFAULT_MIN_XP_GIVEN, DEFAULT_TIMEFRAME_FOR_XP, DEFAULT_MAX_XP_GIVEN, \
    DEFAULT_XP_DECAY_PERCENTAGE, DEFAULT_XP_DECAY_DAYS, MessageCountMode
from .member import MemberXP


class GuildPrefs:
    def __init__(self, guild_id: int, guild_name: str):

        self._guild_id = guild_id
        self._guild_name = guild_name

        self._autoroles = []
        self._dj_roles = []

        self._logs_channel = 0
        self._music_channel = 0
        self._music_header_message = 0
        self._music_player_message = 0
        self._music_player_message_timestamp = 0

        self._role_persistence_enabled = False
        self._default_banned_words_enabled = False
        self._single_message_channels = {}
        self._gallery_channels = []
        self._role_menus = {}

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
    def autoroles(self):
        return self._autoroles

    def set_autoroles(self, autoroles):
        if isinstance(autoroles, type(None)):
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
    def dj_roles(self):
        return self._dj_roles

    def set_dj_roles(self, dj_roles):
        if isinstance(dj_roles, type(None)):
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
    def logs_channel(self):
        return self._logs_channel

    def set_logs_channel(self, logs_channel: int):
        if isinstance(logs_channel, type(None)):
            logs_channel = 0
        self._logs_channel = int(logs_channel)

    @property
    def music_channel(self):
        return self._music_channel

    def set_music_channel(self, music_channel: int):
        if isinstance(music_channel, type(None)):
            music_channel = 0
        self._music_channel = int(music_channel)

    @property
    def music_header_message(self):
        return self._music_header_message

    def set_music_header_message(self, music_header_message: int):
        if isinstance(music_header_message, type(None)):
            music_header_message = 0
        self._music_header_message = int(music_header_message)

    @property
    def music_player_message(self):
        return self._music_player_message

    def set_music_player_message(self, music_player_message: int):
        if isinstance(music_player_message, type(None)):
            music_player_message = 0
        self._music_player_message = int(music_player_message)

    @property
    def music_player_message_timestamp(self):
        return self._music_player_message_timestamp

    def set_music_player_message_timestamp(self, music_player_message_timestamp):
        if isinstance(music_player_message_timestamp, type(None)):
            music_player_message_timestamp = 0
        self._music_player_message_timestamp = int(music_player_message_timestamp)

    @property
    def default_banned_words_enabled(self):
        return self._default_banned_words_enabled

    def set_default_banned_words_enabled(self, default_banned_words_enabled: bool):
        if isinstance(default_banned_words_enabled, type(None)):
            default_banned_words_enabled = False
        self._default_banned_words_enabled = default_banned_words_enabled

    @property
    def role_persistence_enabled(self):
        return self._role_persistence_enabled

    def set_role_persistence_enabled(self, role_persistence_enabled: bool):
        if isinstance(role_persistence_enabled, type(None)):
            role_persistence_enabled = False
        self._role_persistence_enabled = role_persistence_enabled

    @property
    def single_message_channels(self):
        return self._single_message_channels

    def set_single_message_channels(self, single_message_channels):
        if isinstance(single_message_channels, type(None)):
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

    def set_gallery_channels(self, gallery_channels):
        if isinstance(gallery_channels, type(None)):
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
    def role_menus(self):
        return self._role_menus

    def set_role_menus(self, role_menus):
        if not role_menus:
            role_menus = {}
        for message_id, role_menu_details in role_menus.items():
            self._role_menus[int(message_id)] = {
                "restricted_to_roles": {int(role_id) for role_id in role_menu_details.get("restricted_to_roles", [])},
                "mode": role_menu_details["mode"],
                "type": role_menu_details["type"],
                "restricted_description": role_menu_details.get("restricted_description", "")
            }

    def add_role_menu(self, message_id, role_menu_type, role_menu_mode, restricted_to_roles, restricted_description):
        self._role_menus[int(message_id)] = {
            "type": role_menu_type,
            "mode": role_menu_mode,
            "restricted_to_roles": set(restricted_to_roles),
            "restricted_description": restricted_description
        }

    def remove_role_menu(self, message_id):
        if message_id in self._role_menus:
            del self._role_menus[message_id]

    @property
    def xp_settings(self):
        return self._xp_settings

    def set_xp_settings(self, xp_settings):
        if isinstance(xp_settings, type(None)):
            return
        for key, value in xp_settings.items():
            self._xp_settings[key] = value

    def stringify_values(self):
        self._guild_id = str(self._guild_id)

        str_autoroles = []
        for autorole in self._autoroles:
            str_autoroles.append(str(autorole))
        self._autoroles = str_autoroles

        self._logs_channel = str(self._logs_channel)
        self._music_channel = str(self._music_channel)
        self._music_header_message = str(self._music_header_message)
        self._music_player_message = str(self._music_player_message)

        str_gallery = []
        for gallery_channel in self._gallery_channels:
            str_gallery.append(str(gallery_channel))
        self._gallery_channels = str_gallery

        for key in self._single_message_channels.keys():
            self._single_message_channels[key]['channel_id'] =\
                str(self._single_message_channels[key].get('channel_id', 0))
            self._single_message_channels[key]['role_id'] = str(self._single_message_channels[key].get('role_id', 0))

        self._xp_settings = self.stringify_xp_settings_values(self._xp_settings)

        return self

    def destringify_values(self):
        self._guild_id = int(self._guild_id)

        int_autoroles = []
        for autorole in self._autoroles:
            int_autoroles.append(int(autorole))
        self._autoroles = int_autoroles

        self._logs_channel = int(self._logs_channel)
        self._music_channel = int(self._music_channel)
        self._music_header_message = int(self._music_header_message)
        self._music_player_message = int(self._music_player_message)

        int_gallery = []
        for gallery_channel in self._gallery_channels:
            int_gallery.append(int(gallery_channel))
        self._gallery_channels = int_gallery

        for key in self._single_message_channels.keys():
            self._single_message_channels[key]['channel_id'] = \
                int(self._single_message_channels[key].get('channel_id', 0))
            self._single_message_channels[key]['role_id'] = int(self._single_message_channels[key].get('role_id', 0))

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
        if isinstance(xp_settings[XPSettingsKey.LEVEL_ROLES], list):
            for i in range(len(xp_settings[XPSettingsKey.LEVEL_ROLES])):
                if xp_settings[XPSettingsKey.LEVEL_ROLES][i]:
                    new_level_roles_dict[i] = int(xp_settings[XPSettingsKey.LEVEL_ROLES][i])
        else:
            for key, value in xp_settings[XPSettingsKey.LEVEL_ROLES].items():
                new_level_roles_dict[int(key)] = int(value)
        xp_settings[XPSettingsKey.LEVEL_ROLES] = new_level_roles_dict

        return xp_settings


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
