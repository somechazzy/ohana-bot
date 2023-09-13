import discord

from globals_ import shared_memory
from globals_.constants import GuildLogType
from internal.guild_logging import log_to_server
from models.guild import GuildPrefs
from user_interactions.base_interactions_handler import BaseInteractionsHandler


class AdminInteractionsHandler(BaseInteractionsHandler):

    def __init__(self, source_interaction, guild=None):
        super().__init__(source_interaction=source_interaction)
        if self.__class__ == AdminInteractionsHandler:
            raise NotImplementedError("AdminInteractionsHandler is an abstract class and cannot be instantiated")
        self.guild = guild or source_interaction.guild
        self.guild_prefs: GuildPrefs = shared_memory.guilds_prefs.get(self.guild.id)
        self.member = self.guild.get_member(self.source_interaction.user.id)

    async def on_timeout(self):
        try:
            await self.source_interaction.edit_original_response(content="Timed-out. "
                                                                         "Please call the command again if needed.",
                                                                 embed=None,
                                                                 view=None)
        except discord.NotFound:
            pass

    def is_role_assignable(self, role=None, role_id=None, check_against_user=False):
        if not role and not role_id:
            raise
        if not role:
            role = self.guild.get_role(role_id)
        if self.guild.me.roles[-1] <= role or role.is_bot_managed() or role.is_premium_subscriber() \
                or role.is_integration() or role.is_default():
            return False
        if check_against_user and self.guild.get_member(self.source_interaction.user.id).roles[-1] <= role:
            return False
        return True

    async def log_action_to_server(self, event, event_type=GuildLogType.SETTING_CHANGE, field_value_map=None):
        if field_value_map is None:
            field_value_map = {}
        fields = []
        values = []
        for field, value in field_value_map.items():
            fields.append(field)
            values.append(value)
        await log_to_server(guild=self.guild,
                            event_type=event_type,
                            member=self.member,
                            event=event,
                            fields=fields,
                            values=values)
