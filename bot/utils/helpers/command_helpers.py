import discord

from constants import CommandCategory
from models.dto.command_info import CommandInfo, CommandParameterInfo


def get_commands_under_category(category: str) -> list[discord.app_commands.Command]:
    """
    Get all commands under a specific category.
    Args:
        category (str): The category of commands to retrieve. Should be one of the values in CommandCategory.
    Returns:
        list[discord.app_commands.Command]: A list of Command objects under the specified category.
    """
    if category == CommandCategory.USER:
        from bot.slashes.blueprints.user_blueprints import cog, reminder_user_cog
        commands = list(cog.walk_app_commands())
        commands += list(reminder_user_cog.walk_app_commands())
    elif category == CommandCategory.ADMIN:
        from bot.slashes.blueprints.admin_blueprints import cog
        commands = list(cog.walk_app_commands())
    else:
        raise ValueError(f"Invalid menu category: {category}")

    return commands


def get_commands_info_under_category(category: str) -> list[CommandInfo]:
    """
    Get detailed information about all commands under a specific category.
    Args:
        category (str): The category of commands to retrieve. Should be one of the values in CommandCategory.
    Returns:
        list[CommandInfo]: A list of CommandInfo objects containing detailed information about each command.
    """
    commands = get_commands_under_category(category=category)

    command_list = []
    for command in commands:
        if command.extras.get('unlisted', False) or command.extras.get('is_alias', False) \
                or isinstance(command, discord.app_commands.Group):
            continue
        parameters = [CommandParameterInfo(name=param.display_name,
                                           description=param.description,
                                           required=param.required)
                      for param in command.parameters]
        command_list.append(
            CommandInfo(name=command.qualified_name,
                        category=category,
                        listing_priority=command.extras.get('listing_priority', 1),
                        aliases=command.extras.get('aliases', []),
                        group=command.extras.get('group', None),
                        guild_only=command.guild_only,
                        description=command.description,
                        parameters=parameters)
        )

    return sorted(command_list)
