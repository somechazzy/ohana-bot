
class CommandInfo:
    """
    A DTO for command information.
    """

    def __init__(self, name: str, category: str, listing_priority: int, aliases: list[str], group: str | None,
                 guild_only: bool, description: str, parameters: list['CommandParameterInfo']):
        self.name: str = name
        self.category: str = category
        self.listing_priority: int = listing_priority
        self.aliases: list[str] = aliases
        self.group: str | None = group
        self.guild_only: bool = guild_only
        self.description: str = description
        self.parameters: list['CommandParameterInfo'] = parameters

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "aliases": self.aliases,
            "group": self.group[4:] if self.group else self.group,
            "guild_only": self.guild_only,
            "description": self.description,
            "parameters": [param.to_dict() for param in self.parameters]
        }

    # for sorting, use group, then listing_priority, then name
    def __lt__(self, other: 'CommandInfo') -> bool:
        if self.group == other.group:
            if self.listing_priority == other.listing_priority:
                return self.name < other.name
            return self.listing_priority < other.listing_priority
        if self.group is None:
            return False
        if other.group is None:
            return True
        return self.group < other.group


class CommandParameterInfo:
    """
    A DTO for command parameter information.
    """

    def __init__(self, name: str, description: str, required: bool):
        self.name: str = name
        self.description: str = description
        self.required: bool = required

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "required": self.required
        }
