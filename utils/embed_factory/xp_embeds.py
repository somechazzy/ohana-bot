from math import ceil
import discord
from globals_.clients import discord_client
from globals_.constants import Colour
from models.member import MemberXP
from utils.helpers import data_size_human_format


def make_leaderboard_embed(members_xp, requested_by, page=1):
    guild = requested_by.guild
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None
    author_icon_small = requested_by.avatar.with_size(128).url if requested_by.avatar else None

    members_ids_xp_total_map = {mid: mxp.xp for mid, mxp in members_xp.items()}
    members_dicts_sorted = {k: v for k, v in sorted(members_ids_xp_total_map.items(),
                                                    key=lambda item: item[1], reverse=True)}

    ids_sorted = list(members_dicts_sorted.keys())
    requested_by_rank = ids_sorted.index(requested_by.id) + 1 if requested_by.id in ids_sorted else '-'

    page_count = ceil(len(ids_sorted) / 10)
    if not (0 <= page <= page_count):
        page = 1

    starting_index = (page - 1) * 10
    final_index = (starting_index + 10) if (starting_index + 10 <= len(ids_sorted)) else len(ids_sorted)

    members_text = ""
    for i in range(starting_index, final_index):
        member = guild.get_member(ids_sorted[i])
        if member:
            if member.nick and member.nick != str(member):
                name = f"{member.nick} ({member})"
            elif member.global_name and member.global_name != str(member):
                name = f"{member.global_name} ({member})"
            elif not member.global_name and member.name != str(member):
                name = f"{member.name} ({member})"
            else:
                name = member.display_name
        elif user := discord_client.get_user(ids_sorted[i]):
            name = user.display_name
        else:
            name = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).member_tag
        level = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).level
        xp = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).xp
        messages = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).messages
        decayed = members_xp.get(ids_sorted[i], MemberXP(ids_sorted[i])).xp_decayed
        decayed_text = f" ({data_size_human_format(decayed)} decay)" if decayed > 0 else ""
        members_text += f"**{i + 1} • {name}**\n" \
                        f"‎ ‎ ‎ ‎ ‎ ‎" \
                        f"`Level: {level} |" \
                        f" XP: {data_size_human_format(xp)}{decayed_text} |" \
                        f" Messages: {data_size_human_format(messages)}`\n"

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"Navigate using reactions or jump to a page by"
                                      f" adding the page number to the leaderboard command.\n"
                                      f" React with 🗑 to close the embed.\n")

    embed.set_author(name=f"{guild} Leaderboard", icon_url=guild_icon_small or None)
    embed.set_footer(text=f"{requested_by}'s rank: #{requested_by_rank}",
                     icon_url=author_icon_small or None)

    embed.add_field(name="‎",
                    value=f"{members_text}", inline=False)
    embed.add_field(name="‎",
                    value=f"Showing page {page}/{page_count}", inline=False)

    return embed


def make_level_roles_embed(guild, level_roles):
    guild_icon_small = guild.icon.with_size(128).url if guild.icon else None

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"You can earn these roles by chatting and leveling up.\n‎")

    embed.set_author(name=f"{guild} Level Roles", icon_url=guild_icon_small or None)

    for level, role_id in level_roles.items():
        embed.add_field(name=f"Level {level}",
                        value=f"<@&{role_id}>", inline=False)

    return embed
