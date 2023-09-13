import asyncio
import lyricsgenius
from auth import auth


class GeniusService:
    def __init__(self):
        self.client = lyricsgenius.Genius(access_token=auth.GENIUS_ACCESS_TOKEN,
                                          skip_non_songs=True,
                                          retries=1)

    async def search_song(self, title):
        if not auth.GENIUS_ACCESS_TOKEN:
            raise NotImplementedError("Genius API key not set.")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.client.search_song, title)
        return result
