from collections import defaultdict

import discord
from discord.app_commands import Command, Group

from clients import discord_client
from constants import Colour, Links, COMMAND_GROUP_DESCRIPTION_MAP


def get_main_help_embed() -> discord.Embed:
    """
    Creates the main help menu embed.
    Returns:
        discord.Embed: The main help menu embed.
    """
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT, url=Links.OHANA_WEBSITE,
                          description="I have listed my most popular commands below. "
                                      "Click on each section to see the full commands list.\n‎")
    embed.set_thumbnail(url=Links.Media.HELP_EMBED_THUMBNAIL)
    embed.set_author(name="Ohana", url=Links.OHANA_WEBSITE)

    embed.add_field(name="User commands", value=f"• **/myanimelist** • **/anilist** • **/anime** • **/manga** • ...\n"
                                                f"• **/level** • **/leaderboard** • ...\n"
                                                f"• **/remind me** • ...\n‎",
                    inline=False)

    embed.add_field(name="Admin commands",
                    value=f"To configure my XP & Levels system, use **/manage xp settings**.\n"
                          f"You can also see an overview of all admin settings "
                          f"using **/manage settings**.\n‎",
                    inline=False)

    embed.add_field(name="Detailed command list", value=f"{Links.OHANA_WEBSITE_COMMANDS}",
                    inline=False)

    embed.add_field(name="Join Ohana's support server", value=f"{Links.SUPPORT_SERVER_INVITE}\n", inline=False)
    embed.add_field(name="Support the project <3", value=f"{Links.SUPPORT_ME}\n", inline=False)

    embed.set_footer(text="General Help Menu",
                     icon_url=discord_client.user.display_avatar.with_size(128).url)

    return embed


def get_commands_menu_embed(category: str, command_list: list[Command]) -> discord.Embed:
    """
    Creates a commands menu embed for a specific category.
    Args:
        category (str): The category of commands.
        command_list (list[Command]): The list of commands in the category.
    Returns:
        discord.Embed: The commands menu embed.
    """
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT, url=Links.OHANA_WEBSITE,
                          description=f"Full list of {category} commands.\n‎")
    embed.set_thumbnail(url=Links.Media.HELP_EMBED_THUMBNAIL)
    embed.set_author(name=f"Ohana's {category} Commands", url=Links.OHANA_WEBSITE)

    command_group_commands_map = defaultdict(list)
    for command in command_list:
        if isinstance(command, Group):
            continue
        if command.extras.get('unlisted') or command.extras.get('is_alias'):
            continue
        group = command.extras.get('group')
        command_group_commands_map[group].append(command)

    command_groups_sorted = sorted(command_group_commands_map.keys())
    for group in command_groups_sorted:
        commands_sorted = sorted(command_group_commands_map[group], key=lambda x: x.extras.get('listing_priority', 100))
        field_name = COMMAND_GROUP_DESCRIPTION_MAP.get(group, group[4:])
        field_value = "‎\n".join([f"• **`/{command.qualified_name}`**: {command.description}"
                                  for command in commands_sorted])
        embed.add_field(name=field_name, value=field_value + "\n‎", inline=False)

    embed.set_footer(text="Note that some of these are server-only commands",
                     icon_url=discord_client.user.display_avatar.with_size(128).url)

    return embed
