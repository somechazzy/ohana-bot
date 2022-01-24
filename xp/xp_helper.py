import io
import re

import disnake as discord
from PIL import Image, ImageDraw, ImageFont
from globals_.constants import CachingType, XPSettingsKey
from globals_ import variables
from helpers import human_format, build_path
from internal.web_handler import request
from models.member import MemberXP


async def get_level_image(member, xp_settings, all_members_xp, member_tag=None, member_id=None):
    tag, avatar_url, xp_max, xp_progress, level, rank, total_xp, xp_for_next_role, next_role_level =\
        get_level_necessary_data(member, xp_settings, all_members_xp, member_tag=member_tag, member_id=member_id)

    im = Image.open(build_path(["media", "level_template.jpg"]))

    d = ImageDraw.Draw(im)
    tag, tag_font_size, tag_removed, tag_ending_xy = get_tag_string_and_font_size(tag, im)

    # Discord tag
    font_for_name = ImageFont.truetype(build_path(["media", "calibri_italic.ttf"]), tag_font_size)
    x = ((392-tag_ending_xy[0])/2)
    y = ((640-tag_ending_xy[1])/2)
    d.multiline_text((x, y), tag, font=font_for_name, fill=(0xFF, 0xEA, 0x9E), align='center')
    # fill=(65, 58, 32)

    # Discord avatar
    avatar_im = await get_circular_avatar(avatar_url, size=(240, 240))
    avatar_offset = (77, 14)
    im.paste(avatar_im, avatar_offset, avatar_im)

    # XP progress bar
    progress = xp_progress / xp_max
    w, h = 710, 48
    shape = (450, 110,  450+w*progress, 110+h)
    d.rectangle(shape, fill=(0xDE, 0xC4, 0xA7))

    # XP progress text
    progress_text = f"XP: {human_format(xp_progress)}/{human_format(xp_max)}"

    font_for_progress_text = ImageFont.truetype(build_path(["media", "calibri.ttf"]), 40)
    progress_text_draw_xy = ImageDraw.Draw(im).textsize(progress_text, font=font_for_progress_text)
    d.text((1159-progress_text_draw_xy[0], 180),
           progress_text, font=font_for_progress_text, fill=(0xFF, 0xEA, 0x9E))

    # XP level text
    level_text = f"Level {level}"
    font_for_level_and_rank = ImageFont.truetype(build_path(["media", "calibri_italic.ttf"]), 60)
    d.text((450, 33), level_text, font=font_for_level_and_rank, fill=(0xFF, 0xEA, 0x9E))

    # Rank text
    rank_text = f"Rank {rank}"
    rank_text_draw_xy = ImageDraw.Draw(im).textsize(rank_text, font=font_for_level_and_rank)
    d.text((1159-rank_text_draw_xy[0], 33),
           rank_text, font=font_for_level_and_rank, fill=(0xFF, 0xEA, 0x9E))

    # Total xp text
    total_xp_title = f"Total XP: "
    total_xp_value = f"{human_format(total_xp)}"
    font_for_total_xp = ImageFont.truetype(build_path(["media", "calibri_italic.ttf"]), 50)
    total_xp_title_draw_xy = ImageDraw.Draw(im).textsize(total_xp_title, font=font_for_total_xp)
    d.text((465, 240), total_xp_title, font=font_for_total_xp, fill=(0xDD, 0xDD, 0xDD))
    d.text((465+total_xp_title_draw_xy[0], 240), total_xp_value,
           font=font_for_total_xp, fill=(0xDE, 0xC5, 0xA7))

    # XP til next level text
    xp_til_next_level_title = f"XP needed for next role: "
    if xp_for_next_role:
        xp_til_next_level_value = f"{human_format(xp_for_next_role)} (level {next_role_level})"
    else:
        xp_til_next_level_value = "—"
    font_xp_til_next_level = ImageFont.truetype(build_path(["media", "calibri_italic.ttf"]), 40)
    xp_til_next_level_title_draw_xy = ImageDraw.Draw(im).textsize(xp_til_next_level_title,
                                                                  font=font_xp_til_next_level)
    d.text((465, 320), xp_til_next_level_title, font=font_xp_til_next_level, fill=(0xDD, 0xDD, 0xDD))
    d.text((465+xp_til_next_level_title_draw_xy[0], 320), xp_til_next_level_value,
           font=font_xp_til_next_level, fill=(0xDE, 0xC5, 0xA7))

    return im


def get_tag_string_and_font_size(tag: str, im, font_size=70, max_width=370):
    original_font_size = font_size
    tag_removed = False
    num_of_loops = 0
    ending_xy = ()
    while num_of_loops < 100:
        while font_size > 24*2:
            fnt = ImageFont.truetype(build_path(["media", "calibri.ttf"]), font_size)
            ending_xy = ImageDraw.Draw(im).multiline_textsize(tag, font=fnt)
            if ending_xy[0] < max_width:
                return tag, font_size, tag_removed, ending_xy
            font_size = font_size - 1
        if ' ' in tag and '\n' not in tag:
            half_length = int(len(tag)/2)
            first_half_space_index = tag[:half_length].rindex(' ') if ' ' in tag[:half_length] else 1000
            second_half_space_index = tag[half_length:].index(' ') if ' ' in tag[half_length:] else 1000
            if abs(half_length - first_half_space_index) <= abs(half_length - second_half_space_index):
                tag = tag[:half_length][::-1].replace(' ', '\n', 1)[::-1] + tag[half_length:]
            else:
                tag = tag[:half_length] + tag[half_length:].replace(' ', '\n', 1)
        elif '\n' not in tag:
            tag = tag[:int(len(tag)/2)] + '\n' + tag[int(len(tag)/2):]
        elif not tag_removed:
            tag = tag[:tag.rindex("#")]
            tag_removed = True
        else:
            tag = tag[:-5] + '...'
        font_size = original_font_size

    return tag[:5]+'...', font_size, tag_removed, ending_xy   # resorts to this only if no amount
                                                    # of reduction could get the desired result after 100 iterations,
                                                    # which tbh is a lot but whatever


async def get_circular_avatar(url, size=(240, 240)):
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
    im.thumbnail(size, Image.ANTIALIAS)

    return im


def get_level_necessary_data(member: discord.Member, xp_settings, all_members_xp, member_tag=None, member_id=None):
    if member:
        tag = str(member)
        avatar_asset = member.guild_avatar if hasattr(member, 'guild_avatar') and member.guild_avatar else member.avatar
        if avatar_asset:
            avatar = str(avatar_asset.with_size(256).url)
        else:
            avatar = "https://media.discordapp.net/attachments/794891724345442316/851614472333426728/unknown.png"
    else:
        tag = member_tag
        avatar = "https://media.discordapp.net/attachments/794891724345442316/851614472333426728/unknown.png"
    if re.findall("https://cdn.discordapp.com/embed/avatars/[0-9]+\\.png", avatar):
        avatar = "https://media.discordapp.net/attachments/794891724345442316/851614472333426728/unknown.png"

    member_xp: MemberXP = all_members_xp.get(member_id, None)
    if not member_xp:
        all_members_xp[member_id] = MemberXP(member_id)
        member_xp = all_members_xp[member_id]
    total_xp = member_xp.xp
    level = 0
    for xp_requirement in variables.xp_level_map.keys():
        if total_xp >= xp_requirement:
            level = variables.xp_level_map[xp_requirement]
        else:
            break
    if level == 400:
        level = 399
        total_xp = variables.level_xp_map[400] - 1
    xp_max = variables.level_xp_map[level+1] - variables.level_xp_map[level]
    xp_progress = total_xp - variables.level_xp_map[level]

    members_ids_xp_total_map = {mid: mxp.xp for mid, mxp in all_members_xp.items()}
    members_ids_sorted = {k: v for k, v in sorted(members_ids_xp_total_map.items(),
                                                  key=lambda item: item[1], reverse=True)}

    rank = list(members_ids_sorted.keys()).index(member_id) + 1

    level_roles = xp_settings[XPSettingsKey.LEVEL_ROLES]
    next_role_level = None
    for level_role_level in level_roles.keys():
        if level_role_level > level:
            next_role_level = level_role_level
            break
    if next_role_level:
        xp_for_next_role = variables.level_xp_map[next_role_level] - total_xp
    else:
        xp_for_next_role = None

    return tag, avatar, xp_max, xp_progress, level, rank, total_xp, xp_for_next_role, next_role_level
