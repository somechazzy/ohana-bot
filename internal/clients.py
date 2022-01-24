import asyncio
import json
import random
import lyricsgenius
import pyrebase
from disnake.ext import commands
import disnake as discord
import base64
import datetime
from globals_.constants import CachingType
from .web_handler import request
import auth


class DiscordClient:
    client = None

    @staticmethod
    def get_client():
        if DiscordClient.client is None:
            intents = discord.Intents.all()
            DiscordClient.client = commands.Bot(intents=intents, sync_commands_debug=True)
        return DiscordClient.client

    @staticmethod
    def run_client():
        DiscordClient.get_client().run(auth.BOT_TOKEN)


class FirebaseClient:
    
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
            config = auth.FIREBASE_CONFIG
            self._firebase_reference = pyrebase.initialize_app(config)

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

    async def log_to_db(self, log_details, time_now, timestamp_numeral, guild_id=None):
        if not guild_id:
            path = ('logs', time_now.strftime("%Y%m%d"), 'not_guild_related', timestamp_numeral)
        else:
            path = ('logs', time_now.strftime("%Y%m%d"), str(guild_id), timestamp_numeral)
        return await self.set(path=path, data=log_details)

    async def get_mal_usernames(self):
        path = ('mal_usernames', )
        return await self.get(path=path)

    async def get_al_usernames(self):
        path = ('al_usernames', )
        return await self.get(path=path)

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

    async def add_countdown(self, message, countdown_params):
        path = ('countdown', f"{message.channel.id}_{message.id}",)
        return await self.set(path=path, data=countdown_params)

    async def remove_countdown(self, message):
        path = ('countdown', f"{message.channel.id}_{message.id}")
        return await self.remove(path=path)

    async def get_all_countdowns(self):
        path = ('countdown', )
        return await self.get(path=path)

    async def add_reminder(self, time_of_duration_end_seconds, reason, user_id):
        reminder = {
            "time_of_duration_end_seconds": time_of_duration_end_seconds,
            "reason": reason,
            "user_id": user_id
        }
        key = f"{user_id}_{time_of_duration_end_seconds}_{random.randint(0, 1000)}"
        path = ('reminders', key,)
        await self.set(path=path, data=reminder)
        return key

    async def remove_reminder(self, key):
        path = ('reminders', key)
        return await self.remove(path=path)

    async def get_all_reminders(self):
        path = ('reminders', )
        return await self.get(path=path)

    async def get_all_guilds_prefs(self):
        path = ('guilds', )
        return await self.get(path=path)

    async def get_all_guilds_data(self, xp_only=True):
        if not xp_only:
            path = ('guilds_data', )
        else:
            path = ('guilds_data', 'xp')
        return await self.get(path=path)

    async def update_guild_xp(self, guild_id, data):
        path = ('guilds_data', "xp", guild_id,)
        return await self.set(path=path, data=data)

    async def get_logs_for_server(self, guild_id, day_yyyymmdd):
        path = ('logs', day_yyyymmdd, str(guild_id))
        return await self.get(path=path)

    async def set_gms(self, data):
        path = ('gms', )
        return await self.set(path=path, data=data)

    async def get_gms(self):
        path = ('gms', )
        return await self.get(path=path)

    async def reset_gms(self):
        path = ('gms', )
        return await self.remove(path=path)


class SpotifyClient:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://accounts.spotify.com/api/token"
        self.token_data = {"grant_type": "client_credentials"}
        self.access_token, self.access_token_expires = None, None

    def _get_client_credentials(self):
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def _get_token_headers(self):
        client_creds_b64 = self._get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    async def perform_auth(self):
        token_url = self.token_url
        token_data = self.token_data
        token_headers = self._get_token_headers()
        r = await request(method="POST", url=token_url, data=token_data,
                          headers=token_headers, type_of_request=CachingType.SPOTIFY_INFO, no_caching=True)
        if r.status not in range(200, 299):
            raise Exception(f"Error while initiating Spotify client. Received {r.status} response while authenticating")
        data = json.loads(r.content)
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires

    def is_access_token_expired(self):
        now = datetime.datetime.now()
        return self.access_token_expires < now

    async def get_access_token(self):
        if self.is_access_token_expired():
            await self.perform_auth()
            return self.get_access_token()
        elif not self.access_token:
            await self.perform_auth()
            return self.get_access_token()
        return self.access_token

    async def _get_resource_header(self):
        access_token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    async def _get_resource(self, lookup_id, resource_type='tracks', version='v1',
                            no_recurse=False, offset=None, limit=None, end_point_append=""):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}{end_point_append}"
        headers = await self._get_resource_header()
        params = {"offset": offset, "limit": limit} if (offset is not None and limit is not None) else None
        type_of_request = CachingType.SPOTIFY_PLAYLIST if resource_type == 'playlists' else CachingType.SPOTIFY_INFO
        r = await request(method="GET", url=endpoint, headers=headers,
                          type_of_request=type_of_request, params=params)
        if r.status not in range(200, 299):
            if r.status == 401 and not no_recurse:
                await self.perform_auth()
                return await self._get_resource(lookup_id, resource_type, version, no_recurse=True)
            return {}
        return json.loads(r.content)

    async def get_album_tracks(self, _id, offset=0, limit=50):
        return await self._get_resource(_id, resource_type='albums', offset=offset,
                                        limit=limit, end_point_append="/tracks")

    async def get_artist(self, _id):
        return await self._get_resource(_id, resource_type='artists')

    async def get_track(self, _id):
        return await self._get_resource(_id, resource_type='tracks')

    async def get_playlist_tracks(self, _id, offset=0, limit=50):
        return await self._get_resource(_id, resource_type='playlists', offset=offset,
                                        limit=limit, end_point_append="/tracks")


class GeniusClient:
    client = None

    @staticmethod
    def get_genius_client():
        if GeniusClient.client is None or not GeniusClient.client:
            GeniusClient.client = lyricsgenius.Genius(access_token=auth.GENIUS_ACCESS_TOKEN,
                                                      skip_non_songs=True,
                                                      retries=1)
        return GeniusClient.client
