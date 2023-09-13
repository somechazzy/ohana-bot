from youtubesearchpython.__future__ import VideosSearch
from functools import partial
import asyncio
import yt_dlp

from globals_ import shared_memory
from globals_.constants import BotLogLevel
from internal.bot_logger import InfoLogger, ErrorLogger
from utils.helpers import build_path


class YoutubeService:

    def __init__(self):
        self._base_params = {'format': 'bestaudio'}
        self.info_logger = InfoLogger(component=self.__class__.__name__)
        self.error_logger = ErrorLogger(component=self.__class__.__name__)

    async def get_video_info(self, url_, process=True, download=False, file_name=None, is_mp3=False):
        params = {
            "quiet": True
        }
        if is_mp3:
            params['audio-format'] = 'mp3'
        if download:
            params['postprocessors'] = [{'key': 'FFmpegExtractAudio'}]
            if is_mp3:
                params['postprocessors'][0]['preferredcodec'] = 'mp3'
                params['postprocessors'].extend([{'key': 'FFmpegMetadata'},
                                                 {'key': 'FFmpegThumbnailsConvertor'}])
            params['outtmpl'] = build_path(relative_path_params=('media', 'music', file_name))
        try:
            ydl = yt_dlp.YoutubeDL(params=self._base_params | params)
            return await asyncio.get_event_loop().run_in_executor(None, partial(ydl.extract_info, **{
                'url': url_,
                'download': download,
                'process': process
            }))
        except (yt_dlp.utils.DownloadError, yt_dlp.utils.ExtractorError) as e:
            self.error_logger.log(f"Couldn't extract info from a video/playlist: {e} ({e.exc_info})",
                                  level=BotLogLevel.MINOR_WARNING)
            return None

    async def get_search_results(self, search_term, limit=5):
        search_term = search_term.lower()
        search_results = shared_memory.cached_youtube_search_results.get(search_term)
        if search_results and len(search_results) >= limit:
            search_results = shared_memory.cached_youtube_search_results[search_term]
        else:
            video_search = VideosSearch(search_term, limit=limit)
            result = await video_search.next()
            if not result:
                self.info_logger.log(f"Couldn't find any results for search term: {search_term}. Which is weird.")
                return []
            search_results = [
                {
                    "title": result_item['title'],
                    "url": result_item['link'],
                    "thumbnail_url": result_item['thumbnails'][0]['url'],
                    "duration": result_item['duration']
                }
                for result_item in result['result']
            ]
            shared_memory.cached_youtube_search_results[search_term] = search_results
        return search_results
