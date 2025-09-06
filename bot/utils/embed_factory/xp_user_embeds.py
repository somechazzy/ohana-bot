import discord

from bot.utils.helpers.xp_helpers import get_user_username_for_xp
from clients import emojis
from constants import Colour
from models.dto.cachables import CachedGuildXP
from utils.helpers.text_manipulation_helpers import get_shortened_human_readable_number


def get_xp_leaderboard_embed(guild: discord.Guild,
                             author: discord.User,
                             guild_xp: CachedGuildXP,
                             page: int,
                             page_count: int,
                             page_size: int,
                             show_decays: bool) -> discord.Embed:
    """
    Generate an embed for the XP leaderboard.
    Args:
        guild (discord.Guild): The guild for which the leaderboard is generated.
        author (discord.User): The user who requested the leaderboard.
        guild_xp (CachedGuildXP): The guild XP data.
        page (int): The current page number.
        page_count (int): The total number of pages.
        page_size (int): The number of entries per page.
        show_decays (bool): Whether to show decayed XP or not.
    Returns:
        discord.Embed: The generated embed.
    """
    author_rank = guild_xp.get_rank_for(author.id,
                                        resort_members=False)
    members_xp_page = guild_xp.get_members_xp_page(page,
                                                   page_size=10)

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"Navigate using buttons or jump to a page by"
                                      f" adding the page number to the leaderboard command.\n"
                                      f" React with {emojis.action.delete} to close the embed.\n‎\n")

    embed.set_author(name=f"{guild} Leaderboard",
                     icon_url=guild.icon.with_size(64).url if guild.icon else None)
    embed.set_footer(text=f"{author}'s rank: #{author_rank}",
                     icon_url=author.display_avatar.with_size(64).url)

    leaderboard_text = ""
    for idx, member_xp in enumerate(members_xp_page, page_size * (page - 1)):
        if member := guild.get_member(member_xp.user_id):
            username = get_user_username_for_xp(member)
        else:
            username = member_xp.user_username or f"({member_xp.user_id})"
        leaderboard_text += f"**{emojis.numbers[idx + 1]} ‎ {username}**\n" \
                            f"‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎" \
                            f"`Level: {member_xp.level} |" \
                            f" XP: {get_shortened_human_readable_number(member_xp.xp)}" + \
                            (f" ({get_shortened_human_readable_number(member_xp.decayed_xp)} decay)"
                             if show_decays and member_xp.decayed_xp else "") + \
                            f" | Messages: {get_shortened_human_readable_number(member_xp.message_count)}`\n"

    embed.description += leaderboard_text or "No one's on the leaderboard yet."

    embed.add_field(name="‎",
                    value=f"Showing page {page}/{page_count}", inline=False)

    return embed


def get_level_roles_embed(guild: discord.Guild, level_role_ids_map: dict[int, set[int]]) -> discord.Embed:
    """
    Generate an embed listing the level roles for the guild.
    Args:
        guild (discord.Guild): The guild for which the level roles are listed.
        level_role_ids_map (dict[int, set[int]]): A mapping of levels to role IDs.
    Returns:
        discord.Embed: The generated embed.
    """
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"You can earn these roles by chatting and leveling up.\n")
    embed.set_author(name=f"{guild} - Level Roles",
                     icon_url=guild.icon.with_size(64).url if guild.icon else None)

    if not level_role_ids_map:
        embed.description += "### There are no level roles set up for this server.\n" \
                             "If you're an admin, check `/manage xp settings`"
        return embed

    for level in sorted(level_role_ids_map.keys()):
        role_mentions = []
        for role_id in level_role_ids_map[level]:
            if role := guild.get_role(role_id):
                role_mentions.append(role.mention)
        embed.add_field(name=f"Level {level}",
                        value=" • ".join(role_mentions),
                        inline=False)

    embed.set_footer(text=f"Check your level using /level, and the XP leaderboard using /leaderboard")

    return embed
