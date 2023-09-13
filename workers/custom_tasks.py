import gc
from datetime import datetime
from globals_ import shared_memory
from globals_.constants import cache_timeout_minutes, BackgroundWorker
from utils.decorators import periodic_worker


class CustomTasks:

    def __init__(self):
        self._cache_cleanup_tracker = 0

    @periodic_worker(name=BackgroundWorker.CACHE_CLEANUP)
    async def cache_cleanup(self):
        current_time = int(datetime.utcnow().timestamp())
        to_remove = []
        for cached_page in shared_memory.cached_pages:
            cache_timestamp = shared_memory.cached_pages.get(cached_page).get("timestamp")
            cache_timeout = cache_timeout_minutes.get(shared_memory.cached_pages.get(cached_page).get("type")) * 60
            if current_time - cache_timestamp > cache_timeout:
                to_remove.append(cached_page)
        for item in to_remove:
            shared_memory.cached_pages.pop(item)
        self._cache_cleanup_tracker += 1
        if self._cache_cleanup_tracker % 360 == 0:
            shared_memory.cached_youtube_info = {}
            shared_memory.cached_youtube_search_results = {}
        gc.collect()
