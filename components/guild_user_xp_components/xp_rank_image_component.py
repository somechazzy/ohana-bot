from io import BytesIO

import aiohttp
from PIL import Image, ImageDraw, ImageFont

from components.asset_component import AssetComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from components.guild_user_xp_components import BaseGuildUserXPComponent
import cache
from components.guild_user_xp_components.guild_user_xp_component import GuildUserXPComponent
from constants import DefinedAsset
from models.dto.cachables import CachedGuildXP, CachedGuildSettings
from utils.helpers.text_manipulation_helpers import shorten_text, get_shortened_human_readable_number


class XPRankImageComponent(BaseGuildUserXPComponent):
    MAX_USERNAME_FONT_SIZE = 70
    MIN_USERNAME_FONT_SIZE = 40
    MAX_USERNAME_WIDTH = 370

    USERNAME_ENDING_X = 392
    USERNAME_STARTING_Y = 294
    USERNAME_FILL_COLOR = (0xFF, 0xEA, 0x9E)

    AVATAR_SIZE = (240, 240)
    AVATAR_BOX_STARTING_XY = (77, 14)

    PROGRESS_BAR_STARTING_XY = (450, 110)
    PROGRESS_BAR_SIZE = (710, 48)
    PROGRESS_BAR_FILL_COLOR = (0xDE, 0xC4, 0xA7)
    PROGRESS_TEXT_ENDING_X = 1159
    PROGRESS_TEXT_STARTING_Y = 180
    PROGRESS_TEXT_FONT_SIZE = 40
    PROGRESS_TEXT_FILL_COLOR = (0xFF, 0xEA, 0x9E)

    LEVEL_STARTING_XY = (450, 33)
    RANK_ENDING_X = 1159
    RANK_STARTING_Y = 33
    LEVEL_AND_RANK_FONT_SIZE = 60
    LEVEL_AND_RANK_FILL_COLOR = (0xFF, 0xEA, 0x9E)

    TOTAL_XP_STARTING_XY = (450, 240)
    TOTAL_XP_FONT_SIZE = 50
    TOTAL_XP_LABEL_FILL_COLOR = (0xDD, 0xDD, 0xDD)
    TOTAL_XP_VALUE_FILL_COLOR = (0xDE, 0xC5, 0xA7)

    XP_TO_NEXT_ROLE_STARTING_XY = (450, 320)
    XP_TO_NEXT_ROLE_FONT_SIZE = 40
    XP_TO_NEXT_ROLE_LABEL_FILL_COLOR = (0xDD, 0xDD, 0xDD)
    XP_TO_NEXT_ROLE_VALUE_FILL_COLOR = (0xDE, 0xC5, 0xA7)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_member_rank_image(self,
                                    user_id: int,
                                    display_username: str,
                                    user_username: str,
                                    user_avatar: str | None,
                                    guild_id: int) -> Image:
        """
        Build the member rank/level image for the given user.
        Args:
            user_id (int): The ID of the user to build the rank image for.
            display_username (str): The display name of the user to show in the rank image.
            user_username (str): The user username required to initiate member XP, if needed.
            user_avatar (str | None): The avatar URL of the user, if available.
            guild_id (int): The ID of the guild the user belongs to.

        Returns:
            Image: The rank image for the member.
        """
        guild_xp = await GuildUserXPComponent().get_guild_xp(guild_id=guild_id)
        if not (member_xp := guild_xp.get_xp_for(user_id)):
            member_xp = guild_xp.initiate_member_xp(user_id=user_id,
                                                    user_username=user_username)
        xp_settings = (await GuildSettingsComponent().get_guild_settings(guild_id=guild_id)).xp_settings

        progress_to_next_level, xp_required_for_next_level = self._get_progress_to_next_level(member_xp=member_xp,
                                                                                              xp_settings=xp_settings)
        rank = guild_xp.get_rank_for(member_id=user_id)
        next_level_role, xp_to_next_level_role = self._get_next_role_level_and_xp_required(member_xp=member_xp,
                                                                                           xp_settings=xp_settings)

        rank_image = await AssetComponent().get_image_asset(defined_asset=DefinedAsset.XPAssets.XP_RANK_TEMPLATE)

        canvas = ImageDraw.Draw(rank_image)

        await self._draw_username(canvas=canvas, username=display_username)
        await self._draw_avatar(image=rank_image, avatar_url=user_avatar)
        await self._draw_progress(canvas=canvas,
                                  progress=progress_to_next_level,
                                  progress_max=xp_required_for_next_level)
        await self._draw_level_and_rank(canvas=canvas, level=member_xp.level, rank=rank)
        await self._draw_total_xp(canvas=canvas, total_xp=member_xp.xp)
        await self._draw_xp_to_next_role(canvas=canvas,
                                         next_role_level=next_level_role,
                                         xp_to_next_role=xp_to_next_level_role)

        return rank_image

    @staticmethod
    def _get_progress_to_next_level(member_xp: CachedGuildXP.MemberXP,
                                    xp_settings: CachedGuildSettings.XPSettings) -> tuple[int, int]:
        """
        Calculate the progress to the next level based on the member's
        current XP, level, and the next level XP requirement.
        Args:
            member_xp (MemberXP): The MemberXP object containing the user's XP data.
            xp_settings (XPSettings): The XPSettings object containing the guild's XP settings.
        Returns:
            tuple[int, int]: A tuple containing the current XP progress and the XP required for the next level.
        """
        if member_xp.level >= xp_settings.max_level:
            overflow_xp = member_xp.xp - cache.LEVEL_XP_MAP[member_xp.level]
            if overflow_xp < 0:  # just in case
                overflow_xp = 0
            return overflow_xp, 0
        xp_max = cache.LEVEL_XP_MAP[member_xp.level + 1] - cache.LEVEL_XP_MAP[member_xp.level]
        xp_progress = member_xp.xp - cache.LEVEL_XP_MAP[member_xp.level]
        return xp_progress, xp_max

    @staticmethod
    def _get_next_role_level_and_xp_required(member_xp: CachedGuildXP.MemberXP,
                                             xp_settings: CachedGuildSettings.XPSettings) -> tuple[int | None, int]:

        """
        Determine the next level role level and the XP required to reach it.
        Args:
            member_xp (MemberXP): Cached MemberXP object.
            xp_settings (XPSettings): Cached XPSettings object.

        Returns:
            tuple[int | None, int]: A tuple containing the next level role level (or None if there isn't one)
                                    and the XP required to reach that level (0 if none).
        """
        level_role_levels = xp_settings.level_role_ids_map.keys()
        next_role_level = None
        for level_role_level in level_role_levels:
            if level_role_level > member_xp.level:
                next_role_level = level_role_level
                break
        xp_to_next_role = (cache.LEVEL_XP_MAP[next_role_level] - member_xp.xp) if next_role_level else 0

        return next_role_level, xp_to_next_role

    async def _draw_username(self, canvas: ImageDraw.Draw, username: str):
        """
        Draw the username on the rank image.
        Args:
            canvas (ImageDraw.Draw): The drawing context for the rank image.
            username (str): The username to draw.
        """
        current_font_size = self.MAX_USERNAME_FONT_SIZE
        username = shorten_text(username, 20)
        while current_font_size >= self.MIN_USERNAME_FONT_SIZE:
            if current_font_size not in cache.RANK_IMAGE_ITALIC_FONT_CACHE:
                cache.RANK_IMAGE_ITALIC_FONT_CACHE[current_font_size] = \
                    ImageFont.truetype(font=BytesIO(await AssetComponent().get_asset(DefinedAsset.Font.CALIBRI_ITALIC)),
                                       size=current_font_size)
            font = cache.RANK_IMAGE_ITALIC_FONT_CACHE[current_font_size]
            expected_width = canvas.textlength(text=username, font=font)
            if expected_width <= self.MAX_USERNAME_WIDTH:
                canvas.text(xy=((self.USERNAME_ENDING_X - expected_width) / 2,
                                self.USERNAME_STARTING_Y),
                            text=username,
                            font=font,
                            fill=self.USERNAME_FILL_COLOR,
                            align='center')
                return
            current_font_size -= 2
        # fallback
        font = cache.RANK_IMAGE_ITALIC_FONT_CACHE[self.MAX_USERNAME_FONT_SIZE]
        expected_width = canvas.textlength(text='...', font=font)
        canvas.text(xy=((self.USERNAME_ENDING_X - expected_width) / 2,
                        self.USERNAME_STARTING_Y),
                    text='...',
                    font=font,
                    fill=self.USERNAME_FILL_COLOR,
                    align='center')

    async def _draw_avatar(self, image: Image, avatar_url: str | None):
        """
        Draw the user's avatar on the rank image.
        Args:
            image (Image): The rank image to draw the avatar on.
            avatar_url (str | None): The URL of the user's avatar. If not available, a default avatar is used.
        """
        avatar_image = None
        if avatar_url:
            async with aiohttp.ClientSession() as session:
                response = await session.get(avatar_url.replace('.gif', '.webp'))
                if response.status == 200:
                    avatar_bytes = BytesIO(await response.read())
                    avatar_image = Image.open(avatar_bytes).convert("RGBA")
        if not avatar_image:
            avatar_image = await AssetComponent().get_image_asset(defined_asset=DefinedAsset.XPAssets.DEFAULT_AVATAR)

        if avatar_image.height < 240 or avatar_image.width < 240:
            avatar_image = avatar_image.resize((240, 240))
        oversized_mask_size = (avatar_image.size[0] * 3, avatar_image.size[1] * 3)
        circle_mask = Image.new(mode="L", size=oversized_mask_size, color=0)
        mask_draw = ImageDraw.Draw(circle_mask)
        mask_draw.ellipse(xy=(0, 0) + oversized_mask_size, fill=255)
        circle_mask = circle_mask.resize(size=avatar_image.size, resample=Image.Resampling.LANCZOS)
        avatar_image.putalpha(circle_mask)

        avatar_image.thumbnail(size=self.AVATAR_SIZE, resample=Image.Resampling.LANCZOS)
        image.paste(im=avatar_image, box=self.AVATAR_BOX_STARTING_XY, mask=avatar_image)

    async def _draw_progress(self, canvas: ImageDraw.Draw, progress: int, progress_max: int):
        """
        Draw the XP progress bar and text on the rank image.
        Args:
            canvas (ImageDraw.Draw): The drawing context for the rank image.
            progress (int): The current XP progress.
            progress_max (int): The XP required for the next level.
        """
        # XP progress bar
        progress_percentage = (progress / progress_max) if progress_max > 0 else 1
        progress_bar_fill = (self.PROGRESS_BAR_STARTING_XY[0],
                             self.PROGRESS_BAR_STARTING_XY[1],
                             self.PROGRESS_BAR_STARTING_XY[0] + self.PROGRESS_BAR_SIZE[0] * progress_percentage,
                             self.PROGRESS_BAR_STARTING_XY[1] + self.PROGRESS_BAR_SIZE[1])
        canvas.rectangle(xy=progress_bar_fill, fill=self.PROGRESS_BAR_FILL_COLOR)

        # XP progress text
        progress_text = (f"XP: {get_shortened_human_readable_number(progress)}/"
                         f"{get_shortened_human_readable_number(progress_max) if progress_max else '-'}")

        if not (font := cache.RANK_IMAGE_FONT_CACHE.get(self.PROGRESS_TEXT_FONT_SIZE)):
            cache.RANK_IMAGE_FONT_CACHE[self.PROGRESS_TEXT_FONT_SIZE] = \
                ImageFont.truetype(font=BytesIO(await AssetComponent().get_asset(DefinedAsset.Font.CALIBRI)),
                                   size=self.PROGRESS_TEXT_FONT_SIZE)
            font = cache.RANK_IMAGE_FONT_CACHE[self.PROGRESS_TEXT_FONT_SIZE]
        expected_text_width = canvas.textlength(text=progress_text, font=font)
        canvas.text(xy=(self.PROGRESS_TEXT_ENDING_X - expected_text_width,
                        self.PROGRESS_TEXT_STARTING_Y),
                    text=progress_text,
                    font=font,
                    fill=self.PROGRESS_TEXT_FILL_COLOR)

    async def _draw_level_and_rank(self, canvas: ImageDraw.Draw, level: int, rank: int):
        """
        Draw the user's level and rank on the rank image.
        Args:
            canvas (ImageDraw.Draw): The drawing context for the rank image.
            level (int): The user's current level.
            rank (int): The user's current rank in the guild.
        """
        if not (font := cache.RANK_IMAGE_ITALIC_FONT_CACHE.get(self.LEVEL_AND_RANK_FONT_SIZE)):
            cache.RANK_IMAGE_ITALIC_FONT_CACHE[self.LEVEL_AND_RANK_FONT_SIZE] = \
                ImageFont.truetype(font=BytesIO(await AssetComponent().get_asset(DefinedAsset.Font.CALIBRI_ITALIC)),
                                   size=self.LEVEL_AND_RANK_FONT_SIZE)
            font = cache.RANK_IMAGE_ITALIC_FONT_CACHE[self.LEVEL_AND_RANK_FONT_SIZE]

        level_text = f"Level {level}"
        canvas.text(xy=self.LEVEL_STARTING_XY,
                    text=level_text,
                    font=font,
                    fill=self.LEVEL_AND_RANK_FILL_COLOR)
        rank_text = f"Rank {rank}"
        expected_rank_text_width = canvas.textlength(text=f"Rank: {rank}", font=font)
        canvas.text(xy=(self.RANK_ENDING_X - expected_rank_text_width,
                        self.RANK_STARTING_Y),
                    text=rank_text,
                    font=font,
                    fill=self.LEVEL_AND_RANK_FILL_COLOR)

    async def _draw_total_xp(self, canvas: ImageDraw.Draw, total_xp: int):
        """
        Draw the user's total XP on the rank image.
        Args:
            canvas (ImageDraw.Draw): The drawing context for the rank image.
            total_xp (int): The user's total accumulated XP.
        """
        if not (font := cache.RANK_IMAGE_ITALIC_FONT_CACHE.get(self.TOTAL_XP_FONT_SIZE)):
            cache.RANK_IMAGE_ITALIC_FONT_CACHE[self.TOTAL_XP_FONT_SIZE] = \
                ImageFont.truetype(font=BytesIO(await AssetComponent().get_asset(DefinedAsset.Font.CALIBRI_ITALIC)),
                                   size=self.TOTAL_XP_FONT_SIZE)
            font = cache.RANK_IMAGE_ITALIC_FONT_CACHE[self.TOTAL_XP_FONT_SIZE]

        total_xp_label = f"Total XP: "
        total_xp_value = get_shortened_human_readable_number(total_xp)
        expected_label_width = canvas.textlength(text=total_xp_label, font=font)
        canvas.text(xy=self.TOTAL_XP_STARTING_XY,
                    text=total_xp_label,
                    font=font,
                    fill=self.TOTAL_XP_LABEL_FILL_COLOR)
        canvas.text(xy=(self.TOTAL_XP_STARTING_XY[0] + expected_label_width,
                        self.TOTAL_XP_STARTING_XY[1]),
                    text=total_xp_value,
                    font=font,
                    fill=self.TOTAL_XP_VALUE_FILL_COLOR)

    async def _draw_xp_to_next_role(self, canvas, next_role_level, xp_to_next_role):
        """
        Draw the XP required to reach the next level role on the rank image.
        Args:
            canvas (ImageDraw.Draw): The drawing context for the rank image.
            next_role_level (int | None): The level of the next role, or None if there isn't one.
            xp_to_next_role (int): The XP required to reach the next role level.
        """
        if not (font := cache.RANK_IMAGE_ITALIC_FONT_CACHE.get(self.XP_TO_NEXT_ROLE_FONT_SIZE)):
            cache.RANK_IMAGE_ITALIC_FONT_CACHE[self.XP_TO_NEXT_ROLE_FONT_SIZE] = \
                ImageFont.truetype(font=BytesIO(await AssetComponent().get_asset(DefinedAsset.Font.CALIBRI_ITALIC)),
                                   size=self.XP_TO_NEXT_ROLE_FONT_SIZE)
            font = cache.RANK_IMAGE_ITALIC_FONT_CACHE[self.XP_TO_NEXT_ROLE_FONT_SIZE]

        xp_to_next_role_label = "XP needed for next role: "
        xp_to_next_role_value = f"{get_shortened_human_readable_number(xp_to_next_role)} (level {next_role_level})" \
            if next_role_level else "-"
        expected_label_width = canvas.textlength(text=xp_to_next_role_label, font=font)
        canvas.text(xy=self.XP_TO_NEXT_ROLE_STARTING_XY,
                    text=xp_to_next_role_label,
                    font=font,
                    fill=self.XP_TO_NEXT_ROLE_LABEL_FILL_COLOR)
        canvas.text(xy=(self.XP_TO_NEXT_ROLE_STARTING_XY[0] + expected_label_width,
                        self.XP_TO_NEXT_ROLE_STARTING_XY[1]),
                    text=xp_to_next_role_value,
                    font=font,
                    fill=self.XP_TO_NEXT_ROLE_VALUE_FILL_COLOR)
