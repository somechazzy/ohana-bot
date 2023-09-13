import asyncio
import uuid

from pyrebase import pyrebase
from auth import auth


class FirebaseService:

    def __init__(self):
        self._firebase_reference = None

    def _get_fb_ref(self):
        if not self._firebase_reference:
            self.initialize_fb()
        return self._firebase_reference

    def initialize_fb(self):
        if self._firebase_reference is not None:
            pass
        else:
            self._firebase_reference = pyrebase.initialize_app(auth.FIREBASE_CONFIG)

    def get_db_ref(self):
        return self._get_fb_ref().database()

    async def get(self, path):
        node = self.get_db_ref()
        for child in path:
            node = node.child(child)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, node.get)

    async def set(self, path, data):
        node = self.get_db_ref()
        for child in path:
            node = node.child(child)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, node.set, data)

    async def update(self, path, data):
        node = self.get_db_ref()
        for child in path:
            node = node.child(child)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, node.update, data)

    async def remove(self, path):
        node = self.get_db_ref()
        for child in path:
            node = node.child(child)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, node.remove)

    async def get_mal_usernames(self):
        path = ('mal_usernames',)
        return (await self.get(path=path)).pyres or []

    async def get_al_usernames(self):
        path = ('al_usernames',)
        return (await self.get(path=path)).pyres or []

    async def put_mal_username(self, discord_id, username_mapping):
        path = ('mal_usernames', discord_id)
        return await self.set(path=path, data=username_mapping)

    async def put_al_username(self, discord_id, username_mapping):
        path = ('al_usernames', discord_id)
        return await self.set(path=path, data=username_mapping)

    async def remove_mal_username(self, discord_id):
        path = ('mal_usernames', discord_id)
        return await self.remove(path=path)

    async def remove_al_username(self, discord_id):
        path = ('al_usernames', discord_id)
        return await self.remove(path=path)

    async def save_user_roles_for_guild(self, member_id, roles, guild_id):
        path = ('guilds_data', "role_persistence", str(guild_id), str(member_id))
        return await self.set(path=path, data=roles)

    async def get_user_roles_for_guild(self, member_id, guild_id):
        path = ('guilds_data', "role_persistence", str(guild_id), str(member_id))
        return await self.get(path=path)

    async def add_reminder(self, timestamp, reason, user_id):
        reminder = {
            "timestamp": timestamp,
            "reason": reason,
            "user_id": user_id
        }
        key = str(uuid.uuid4().hex)
        path = ('reminders', key,)
        await self.set(path=path, data=reminder)
        return key

    async def remove_reminder(self, key):
        path = ('reminders', key)
        return await self.remove(path=path)

    async def get_all_reminders(self):
        path = ('reminders',)
        return (await self.get(path=path)).pyres or []

    async def get_all_guilds_prefs(self):
        path = ('guilds',)
        return (await self.get(path=path)).pyres or []

    async def get_all_guilds_xp(self):
        path = ('guilds_data', 'xp')
        return (await self.get(path=path)).pyres or []

    async def update_guilds_xp(self, data):
        path = ('guilds_data', "xp")
        return await self.update(path=path, data=data)

    async def set_gms(self, data):
        path = ('gms',)
        return await self.set(path=path, data=data)

    async def get_gms(self):
        path = ('gms',)
        return await self.get(path=path)

    async def reset_gms(self):
        path = ('gms',)
        return await self.remove(path=path)

    async def save_user_music_library(self, music_library):
        path = ('music_library', f"{music_library.user_id}")
        return await self.set(path=path, data=music_library.to_dict())

    async def get_user_music_library(self, user_id):
        path = ('music_library', f"{user_id}")
        return await self.get(path=path)

    async def save_rewatch(self, mal_id, rewatch_data):
        path = ('rewatch', f"{mal_id}")
        return await self.set(path=path, data=rewatch_data)

    async def get_rewatches(self):
        path = ('rewatch',)
        return await self.get(path=path)

    async def delete_rewatch(self, mal_id):
        path = ('rewatch', f"{mal_id}")
        return await self.remove(path=path)

    async def get_rewatch(self, mal_id):
        path = ('rewatch', f"{mal_id}")
        return await self.get(path=path)

    async def get_guilds_with_disabled_players_refresh_button(self):
        path = ('guilds_with_disabled_players_refresh_button',)
        return (await self.get(path=path)).pyres or []

    async def add_guild_with_disabled_players_refresh_button(self, guild_id, user_ids):
        path = ('guilds_with_disabled_players_refresh_button', str(guild_id))
        return await self.set(path=path, data=[str(user_id) for user_id in user_ids])

    async def remove_guild_with_disabled_players_refresh_button(self, guild_id):
        path = ('guilds_with_disabled_players_refresh_button', str(guild_id))
        return await self.remove(path=path)

    async def set_giveaway(self, message_id, data):
        path = ('custom_data', 'giveaway_data', str(message_id))
        return await self.set(path=path, data=data)

    async def set_guild_music_logs(self, guild_id, music_logs):
        path = ('guilds_data', 'music_logs', str(guild_id))
        return await self.set(path=path, data=music_logs)

    async def get_guild_music_logs(self, guild_id):
        path = ('guilds_data', 'music_logs', str(guild_id))
        return (await self.get(path=path)).val()
