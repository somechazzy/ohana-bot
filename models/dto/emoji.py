import discord
import random

from common.app_logger import AppLogger

logger = AppLogger(component="EmojiWarehouse")


class EmojiWarehouse:
    _instance = None
    """
    For storing bot's emojis in a centralized manner.
    """
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EmojiWarehouse, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.action = ActionEmojis()
        self.general = GeneralEmojis()
        self.loading = LoadingEmojis()
        self.navigation = NavigationEmojis()
        self.player = PlayerEmojis()
        self.weekday = WeekdayEmojis()
        self.numbers = NumberEmojis()
        self.logos = LogoEmojis()
        self.misc = MiscEmojis()

    def set_emojis(self, emojis: list[discord.Emoji]) -> None:
        """
        Sets warehouse emojis based on their prefixes.
        Args:
            emojis (list[discord.Emoji]): List of emojis to set.

        Returns:
            None
        """
        for emoji in emojis:
            if emoji.name.startswith(self.action.PREFIX):
                setattr(self.action, emoji.name.split('_', 1)[1], emoji)
            elif emoji.name.startswith(self.general.PREFIX):
                setattr(self.general, emoji.name.split('_', 1)[1], emoji)
            elif emoji.name.startswith(self.loading.PREFIX):
                self.loading.list_.append(emoji)
            elif emoji.name.startswith(self.navigation.PREFIX):
                setattr(self.navigation, emoji.name.split('_', 1)[1], emoji)
            elif emoji.name.startswith(self.player.PREFIX):
                if '_station_category_' in emoji.name:
                    self.player.station_category_emojis.append(emoji)
                elif '_station_' in emoji.name:
                    self.player.station_emojis.append(emoji)
                else:
                    setattr(self.player, emoji.name.split('_', 1)[1], emoji)
            elif emoji.name.startswith(self.weekday.PREFIX):
                setattr(self.weekday, emoji.name.split('_', 1)[1], emoji)
            elif emoji.name.startswith(self.numbers.PREFIX):
                if emoji.name.endswith('_r'):
                    self.numbers.digits_boxed_right[int(emoji.name.split('_')[1])] = emoji
                elif emoji.name.endswith('_l'):
                    self.numbers.digits_boxed_left[int(emoji.name.split('_')[1])] = emoji
                elif emoji.name.endswith('_c'):
                    self.numbers.digits_boxed_center[int(emoji.name.split('_')[1])] = emoji
                elif emoji.name.endswith('_rc'):
                    self.numbers.digits_boxed_right_center[int(emoji.name.split('_')[1])] = emoji
                elif emoji.name.endswith('_lc'):
                    self.numbers.digits_boxed_left_center[int(emoji.name.split('_')[1])] = emoji
                else:
                    self.numbers.digits_boxed[int(emoji.name.split('_')[1])] = emoji
            elif emoji.name.startswith(self.logos.PREFIX):
                setattr(self.logos, emoji.name.split('_', 1)[1], emoji)
            elif emoji.name.startswith(self.misc.PREFIX):
                setattr(self.misc, emoji.name.split('_', 1)[1], emoji)
            else:
                logger.warning(f"Application emoji {emoji.name} has no defined destination.")
                setattr(self, emoji.name, emoji)


class ActionEmojis:
    PREFIX = "action"

    add: discord.Emoji
    clear: discord.Emoji
    copy: discord.Emoji
    delete: discord.Emoji
    merge: discord.Emoji
    move: discord.Emoji
    refresh: discord.Emoji
    remove: discord.Emoji
    rename: discord.Emoji
    switch: discord.Emoji
    scroll_down: discord.Emoji
    scroll_up: discord.Emoji
    edit: discord.Emoji
    select: discord.Emoji
    unlock: discord.Emoji


class GeneralEmojis:
    PREFIX = "general"

    clock: discord.Emoji
    favorite: discord.Emoji
    history: discord.Emoji
    settings: discord.Emoji
    info: discord.Emoji
    bug: discord.Emoji
    wand: discord.Emoji
    image: discord.Emoji
    chain: discord.Emoji
    orientation: discord.Emoji
    tv: discord.Emoji
    book: discord.Emoji
    books: discord.Emoji
    pie_chart: discord.Emoji


class LoadingEmojis:
    PREFIX = "loading"

    list_: list[discord.Emoji] = []

    def get_random(self) -> discord.Emoji:
        return random.choice(self.list_) if self.list_ else '⌛'


class NavigationEmojis:
    PREFIX = "navigation"

    back: discord.Emoji
    next: discord.Emoji
    previous: discord.Emoji


class PlayerEmojis:
    PREFIX = "player"

    play: discord.Emoji
    stop: discord.Emoji
    library: discord.Emoji
    loop: discord.Emoji
    music: discord.Emoji
    pause: discord.Emoji
    pause_resume: discord.Emoji
    radio: discord.Emoji
    resume: discord.Emoji
    shuffle: discord.Emoji
    skip: discord.Emoji
    connect: discord.Emoji
    disconnect: discord.Emoji
    station_emojis: list[discord.Emoji] = []
    station_category_emojis: list[discord.Emoji] = []

    def get_station_emoji(self, code: str) -> discord.Emoji | None:
        for emoji in self.station_emojis:
            if emoji.name == f"{self.PREFIX}_station_{code.lower()}":
                return emoji
        logger.warning(f"Station emoji not found for code: {code}")
        return self.radio

    def get_station_category_emoji(self, category: str) -> discord.Emoji | None:
        for emoji in self.station_category_emojis:
            if emoji.name == f"{self.PREFIX}_station_category_{category.lower()}":
                return emoji
        logger.warning(f"Category emoji not found for category: {category}")
        return self.radio


class WeekdayEmojis:
    PREFIX = "weekday"

    monday: discord.Emoji
    tuesday: discord.Emoji
    wednesday: discord.Emoji
    thursday: discord.Emoji
    friday: discord.Emoji
    saturday: discord.Emoji
    sunday: discord.Emoji

    def __getitem__(self, key: int) -> discord.Emoji:
        return [self.monday, self.tuesday, self.wednesday, self.thursday,
                self.friday, self.saturday, self.sunday][key % 7]


class NumberEmojis:
    PREFIX = "number"

    digits_boxed: list[discord.Emoji] = [None] * 10
    digits_boxed_left: list[discord.Emoji] = [None] * 10
    digits_boxed_right: list[discord.Emoji] = [None] * 10
    digits_boxed_center: list[discord.Emoji] = [None] * 10
    digits_boxed_left_center: list[discord.Emoji] = [None] * 10
    digits_boxed_right_center: list[discord.Emoji] = [None] * 10

    def __getitem__(self, key) -> str:
        if isinstance(key, str) and key.isdigit():
            key = int(key)
        elif not isinstance(key, int) or key < 0:
            raise IndexError("Key must be a non-negative integer.")

        if key < 10:
            return f"{self.digits_boxed[key]}"
        else:
            key = str(key)
            if len(key) < 4:
                left = self.digits_boxed_left_center[int(key[0])]
                center = [str(self.digits_boxed_center[int(digit)]) for digit in key[1:-1]]
                right = self.digits_boxed_right_center[int(key[-1])]
                return f"{left}{''.join(center)}{right}"
            else:
                left = self.digits_boxed_left[int(key[0])]
                right = self.digits_boxed_right[int(key[-1])]
                centers = [str(self.digits_boxed_center[int(digit)]) for digit in key[1:-1]]
                return f"{left}{''.join(centers)}{right}" if centers else f"{left}{right}"


class LogoEmojis:
    PREFIX = "logo"

    mal: discord.Emoji
    anilist: discord.Emoji


class MiscEmojis:
    PREFIX = "misc"

    yay: discord.Emoji
