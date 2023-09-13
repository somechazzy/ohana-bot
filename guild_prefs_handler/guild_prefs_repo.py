from globals_.clients import firebase_client
from utils.helpers import get_encrypted_string


class GuildPrefsRepo:

    def __init__(self):
        self.firebase_client = firebase_client

    async def get_guild(self, guild_id):
        path = ('guilds', guild_id)
        return await self.firebase_client.get(path=path)

    async def add_guild(self, guild_prefs):
        path = ('guilds', guild_prefs.guild_id)
        guild_prefs_dict = guild_prefs.__dict__
        return await self.firebase_client.set(path=path, data=guild_prefs_dict)

    async def get_all_guilds_prefs(self):
        return await self.firebase_client.get_all_guilds_prefs()

    async def update_guild_attribute(self, guild_id, attribute_name, attribute_value):

        attribute_name = get_encrypted_string(str(attribute_name))

        if (isinstance(attribute_value, int) or isinstance(attribute_value, float))\
                and not isinstance(attribute_value, bool):
            attribute_value = str(attribute_value)

        path = ("guilds", guild_id, attribute_name)
        await self.firebase_client.set(path=path, data=attribute_value)

    async def update_second_level_guild_attribute(self, guild_id, attribute_name,
                                                  second_level_attribute_name, attribute_value):

        attribute_name = get_encrypted_string(str(attribute_name))
        second_level_attribute_name = get_encrypted_string(str(second_level_attribute_name))

        if isinstance(attribute_value, int) or isinstance(attribute_value, float):
            attribute_value = str(attribute_value)

        path = ("guilds", guild_id, attribute_name, second_level_attribute_name)
        await self.firebase_client.set(path=path, data=attribute_value)

    async def update_third_level_guild_attribute(self, guild_id, attribute_name,
                                                 second_level_attribute_name, third_level_attribute_name,
                                                 attribute_value):

        attribute_name = get_encrypted_string(str(attribute_name))
        second_level_attribute_name = get_encrypted_string(str(second_level_attribute_name))
        third_level_attribute_name = get_encrypted_string(str(third_level_attribute_name))

        if isinstance(attribute_value, int) or isinstance(attribute_value, float):
            attribute_value = str(attribute_value)

        path = ("guilds", guild_id, attribute_name, second_level_attribute_name, third_level_attribute_name)
        await self.firebase_client.set(path=path, data=attribute_value)

    async def update_fourth_level_guild_attribute(self, guild_id, attribute_name,
                                                  second_level_attribute_name, third_level_attribute_name,
                                                  fourth_level_attribute_name, attribute_value):

        attribute_name = get_encrypted_string(str(attribute_name))
        second_level_attribute_name = get_encrypted_string(str(second_level_attribute_name))
        third_level_attribute_name = get_encrypted_string(str(third_level_attribute_name))
        fourth_level_attribute_name = get_encrypted_string(str(fourth_level_attribute_name))

        if isinstance(attribute_value, int) or isinstance(attribute_value, float):
            attribute_value = str(attribute_value)

        path = ("guilds", guild_id, attribute_name, second_level_attribute_name,
                third_level_attribute_name, fourth_level_attribute_name)
        await self.firebase_client.set(path=path, data=attribute_value)
