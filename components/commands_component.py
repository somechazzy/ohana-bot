import itertools

from bot.utils.helpers.command_helpers import get_commands_info_under_category
from components import BaseComponent
from constants import CommandQueryType


class CommandsComponent(BaseComponent):
    """
    Component to manage and provide information about bot commands.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_commands_info(self, category: str) -> list[dict]:
        """
        Retrieves information about commands based on the specified category.
        Args:
            category (str): The category of commands to retrieve. Use CommandQueryType.ALL to get all commands.

        Returns:
            list[dict]: A list of dictionaries containing command information.
        """
        if category == CommandQueryType.ALL:
            return list(itertools.chain.from_iterable(
                self.get_commands_info(cat) for cat in CommandQueryType.as_list() if cat != CommandQueryType.ALL
            ))

        commands_info = get_commands_info_under_category(category)
        return [
            command_info.to_dict() for command_info in commands_info
        ]
