from globals_.constants import UserCommandSection, HelpListingVisibility


class Command:
    def __init__(self, name: str, aliases: [] = None):
        if aliases is None:
            aliases = []
        self._name = name
        self._aliases = aliases
        self._sub_commands = []
        self._section = UserCommandSection.OTHER
        self._description = "No description available"
        self._short_description = ""
        self._further_details = ""
        self._usage_examples = ["No usage examples available"]
        self._show_on_listing = HelpListingVisibility.SHOW
        self._bot_perms = ['read_messages']
        self._member_perms = ['send_messages']

    @property
    def name(self):
        return self._name

    def set_name(self, name: str):
        self._name = name

    @property
    def aliases(self):
        return self._aliases

    def set_aliases(self, aliases: []):
        self._aliases = aliases

    def add_alias(self, alias: str):
        self._aliases.append(alias)

    def add_aliases(self, aliases: []):
        self._aliases = self._aliases.extend(aliases)

    @property
    def sub_commands(self):
        return self._sub_commands

    def set_sub_commands(self, sub_commands: []):
        self._sub_commands = sub_commands

    def add_sub_command(self, sub_command: str):
        self._sub_commands.append(sub_command)

    def add_sub_commands(self, sub_commands: []):
        self._sub_commands = self._sub_commands.extend(sub_commands)

    @property
    def section(self):
        return self._section

    def set_section(self, section: UserCommandSection):
        self._section = section

    @property
    def description(self):
        return self._description

    def set_description(self, description: str):
        self._description = description

    @property
    def short_description(self):
        return self._short_description

    def set_short_description(self, short_description: str):
        self._short_description = short_description

    @property
    def further_details(self):
        return self._further_details

    def set_further_details(self, further_details: str):
        self._further_details = further_details

    @property
    def usage_examples(self):
        return self._usage_examples

    def set_usage_examples(self, usage_examples: []):
        self._usage_examples = usage_examples

    def add_usage_example(self, usage_example: str):
        self._usage_examples.append(usage_example)

    def add_usage_examples(self, usage_examples: []):
        self._usage_examples = self._usage_examples.extend(usage_examples)

    @property
    def show_on_listing(self):
        return self._show_on_listing

    def set_show_on_listing(self, show_on_listing: HelpListingVisibility):
        self._show_on_listing = show_on_listing

    @property
    def bot_perms(self):
        return self._bot_perms

    def set_bot_perms(self, bot_perms: []):
        self._bot_perms = bot_perms

    def add_bot_perm(self, bot_perm: str):
        self._bot_perms.append(bot_perm)

    def add_bot_perms(self, bot_perms: []):
        self._bot_perms = self._bot_perms.extend(bot_perms)

    @property
    def member_perms(self):
        return self._member_perms

    def set_member_perms(self, member_perms: []):
        self._member_perms = member_perms

    def add_member_perm(self, member_perm: str):
        self._member_perms.append(member_perm)

    def add_member_perms(self, member_perms: []):
        self._member_perms = self._member_perms.extend(member_perms)
