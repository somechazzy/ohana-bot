import base64
import datetime
import json

from auth import auth
from globals_.constants import CachingType
from internal.requests_manager import request
from services.third_party.base import ThirdPartyService


class SpotifyService(ThirdPartyService):

    def __init__(self):
        super().__init__()
        self.client_id = auth.SPOTIFY_CLIENT_ID
        self.client_secret = auth.SPOTIFY_CLIENT_SECRET
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
        r = await request(method="POST", url=token_url, type_of_request=CachingType.NO_CACHE, headers=token_headers,
                          data=token_data)
        if r.status not in range(200, 299):
            self.error_logger.log(f"Error while authorizing Spotify client. Details: {r.content}")
        data = json.loads(r.content)
        now = datetime.datetime.utcnow()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires

    def is_access_token_expired(self):
        now = datetime.datetime.utcnow()
        return True if not self.access_token else self.access_token_expires < now

    async def get_access_token(self):
        if self.is_access_token_expired():
            await self.perform_auth()
            return await self.get_access_token()
        elif not self.access_token:
            await self.perform_auth()
            return await self.get_access_token()
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
        r = await request(method="GET", url=endpoint, type_of_request=type_of_request, headers=headers, params=params)
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
