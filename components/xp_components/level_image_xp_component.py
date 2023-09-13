import io
import re

from components.xp_components.base_xp_component import XPComponent

import discord
from PIL import Image, ImageDraw, ImageFont
from globals_.constants import CachingType, XP_LEVEL_MAP, XPSettingsKey, LEVEL_XP_MAP, AVATAR_PLACEHOLDER
from utils.helpers import data_size_human_format, build_path
from internal.requests_manager import request
from models.member import MemberXP


class LevelImageXPComponent(XPComponent):

    def __init__(self, avatar_size=(240, 240), tag_max_font_size=70, **kwargs):
        super().__init__(**kwargs)
        self.avatar_size = avatar_size
        self.tag_max_font_size = tag_max_font_size

    async def get_level_image(self, member: discord.Member, all_members_xp: dict, guild_xp_settings: dict):
        tag, avatar_url, xp_max, xp_progress, level, rank, total_xp, xp_for_next_role, next_role_level = \
            self.get_level_necessary_data(member, guild_xp_settings, all_members_xp)

        image = Image.open(build_path(["media", "level_template.jpg"]))

        d = ImageDraw.Draw(image)
        tag, tag_font_size, tag_removed, tag_ending_xy = self._get_tag_string_and_font_size(tag=tag, im=image)

        # Discord tag
        font_for_name = ImageFont.truetype(build_path(["media", "calibri_italic.ttf"]), tag_font_size)
        x = ((392 - tag_ending_xy[0]) / 2)
        y = ((640 - tag_ending_xy[1]) / 2)
        d.multiline_text((x, y), tag, font=font_for_name, fill=(0xFF, 0xEA, 0x9E), align='center')
        # fill=(65, 58, 32)

        # Discord avatar
        avatar_im = await self._get_circular_avatar(avatar_url)
        avatar_offset = (77, 14)
        image.paste(avatar_im, avatar_offset, avatar_im)

        # XP progress bar
        progress = xp_progress / xp_max
        w, h = 710, 48
        shape = (450, 110, 450 + w * progress, 110 + h)
        d.rectangle(shape, fill=(0xDE, 0xC4, 0xA7))

        # XP progress text
        progress_text = f"XP: {data_size_human_format(xp_progress)}/{data_size_human_format(xp_max)}"

        font_for_progress_text = ImageFont.truetype(build_path(["media", "calibri.ttf"]), 40)
        progress_text_draw_xy = ImageDraw.Draw(image).textsize(progress_text, font=font_for_progress_text)
        d.text((1159 - progress_text_draw_xy[0], 180),
               progress_text, font=font_for_progress_text, fill=(0xFF, 0xEA, 0x9E))

        # XP level text
        level_text = f"Level {level}"
        font_for_level_and_rank = ImageFont.truetype(build_path(["media", "calibri_italic.ttf"]), 60)
        d.text((450, 33), level_text, font=font_for_level_and_rank, fill=(0xFF, 0xEA, 0x9E))

        # Rank text
        rank_text = f"Rank {rank}"
        rank_text_draw_xy = ImageDraw.Draw(image).textsize(rank_text, font=font_for_level_and_rank)
        d.text((1159 - rank_text_draw_xy[0], 33),
               rank_text, font=font_for_level_and_rank, fill=(0xFF, 0xEA, 0x9E))

        # Total XP text
        total_xp_title = f"Total XP: "
        total_xp_value = f"{data_size_human_format(total_xp)}"
        font_for_total_xp = ImageFont.truetype(build_path(["media", "calibri_italic.ttf"]), 50)
        total_xp_title_draw_xy = ImageDraw.Draw(image).textsize(total_xp_title, font=font_for_total_xp)
        d.text((465, 240), total_xp_title, font=font_for_total_xp, fill=(0xDD, 0xDD, 0xDD))
        d.text((465 + total_xp_title_draw_xy[0], 240), total_xp_value,
               font=font_for_total_xp, fill=(0xDE, 0xC5, 0xA7))

        # XP til next level text
        xp_til_next_level_title = f"XP needed for next role: "
        if xp_for_next_role:
            xp_til_next_level_value = f"{data_size_human_format(xp_for_next_role)} (level {next_role_level})"
        else:
            xp_til_next_level_value = "—"
        font_xp_til_next_level = ImageFont.truetype(build_path(["media", "calibri_italic.ttf"]), 40)
        xp_til_next_level_title_draw_xy = ImageDraw.Draw(image).textsize(xp_til_next_level_title,
                                                                         font=font_xp_til_next_level)
        d.text((465, 320), xp_til_next_level_title, font=font_xp_til_next_level, fill=(0xDD, 0xDD, 0xDD))
        d.text((465 + xp_til_next_level_title_draw_xy[0], 320), xp_til_next_level_value,
               font=font_xp_til_next_level, fill=(0xDE, 0xC5, 0xA7))

        return image

    @staticmethod
    def get_level_necessary_data(member: discord.Member, guild_xp_settings, all_members_xp):
        tag = member.global_name or str(member)
        avatar_asset = member.guild_avatar if hasattr(member, 'guild_avatar') and member.guild_avatar else member.avatar
        avatar = str(avatar_asset.with_size(256).url) if avatar_asset else AVATAR_PLACEHOLDER
    
        if re.findall("https://cdn.discordapp.com/embed/avatars/[0-9]+\\.png", avatar):
            avatar = AVATAR_PLACEHOLDER
    
        member_xp: MemberXP = all_members_xp.get(member.id, None)
        if not member_xp:
            all_members_xp[member.id] = MemberXP(member.id)
            member_xp = all_members_xp[member.id]
        total_xp = member_xp.xp
        level = 0
        for xp_requirement in XP_LEVEL_MAP.keys():
            if total_xp >= xp_requirement:
                level = XP_LEVEL_MAP[xp_requirement]
            else:
                break
        if level == 400:
            level = 399
            total_xp = LEVEL_XP_MAP[400] - 1
        xp_max = LEVEL_XP_MAP[level + 1] - LEVEL_XP_MAP[level]
        xp_progress = total_xp - LEVEL_XP_MAP[level]
    
        members_ids_xp_total_map = {mid: mxp.xp for mid, mxp in all_members_xp.items()}
        members_ids_sorted = {k: v for k, v in sorted(members_ids_xp_total_map.items(),
                                                      key=lambda item: item[1], reverse=True)}
    
        rank = list(members_ids_sorted.keys()).index(member.id) + 1
    
        level_roles = guild_xp_settings[XPSettingsKey.LEVEL_ROLES]
        next_role_level = None
        for level_role_level in level_roles.keys():
            if level_role_level > level:
                next_role_level = level_role_level
                break
        if next_role_level:
            xp_for_next_role = LEVEL_XP_MAP[next_role_level] - total_xp
        else:
            xp_for_next_role = None
    
        return tag, avatar, xp_max, xp_progress, level, rank, total_xp, xp_for_next_role, next_role_level

    async def _get_circular_avatar(self, url):
        res = await request("GET", url.replace('.gif', '.webp'), type_of_request=CachingType.DISCORD_AVATAR)
        im = Image.open(io.BytesIO(res.content))
        while im.size[0] < 240 or im.size[1] < 240:
            im = im.resize((im.size[0] * 2, im.size[1] * 2))
        big_size = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', big_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + big_size, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        im.putalpha(mask)
        im.thumbnail(self.avatar_size, Image.ANTIALIAS)

        return im

    def _get_tag_string_and_font_size(self, tag: str, im, max_width=370):
        font_size = self.tag_max_font_size
        original_font_size = font_size
        tag_removed = False
        num_of_loops = 0
        ending_xy = ()
        while num_of_loops < 100:
            while font_size > 24 * 2:
                fnt = ImageFont.truetype(build_path(["media", "calibri.ttf"]), font_size)
                ending_xy = ImageDraw.Draw(im).multiline_textsize(tag, font=fnt)
                if ending_xy[0] < max_width:
                    return tag, font_size, tag_removed, ending_xy
                font_size = font_size - 1
            if ' ' in tag and '\n' not in tag:
                half_length = int(len(tag) / 2)
                first_half_space_index = tag[:half_length].rindex(' ') if ' ' in tag[:half_length] else 1000
                second_half_space_index = tag[half_length:].index(' ') if ' ' in tag[half_length:] else 1000
                if abs(half_length - first_half_space_index) <= abs(half_length - second_half_space_index):
                    tag = tag[:half_length][::-1].replace(' ', '\n', 1)[::-1] + tag[half_length:]
                else:
                    tag = tag[:half_length] + tag[half_length:].replace(' ', '\n', 1)
            elif '\n' not in tag:
                tag = tag[:int(len(tag) / 2)] + '\n' + tag[int(len(tag) / 2):]
            elif not tag_removed:
                tag = tag[:tag.rindex("#")]
                tag_removed = True
            else:
                tag = tag[:-5] + '...'
            font_size = original_font_size

        return tag[:5] + '...', font_size, tag_removed, ending_xy
        # resorts to this only if no amount of reduction could get the desired result after 100 iterations
