import asyncio
import inspect
import traceback
from datetime import datetime

from globals_.constants import PERIODIC_WORKER_FREQUENCY, BotLogLevel, WORKER_RETRY_ON_ERROR_DELAY
from globals_.settings import settings
from internal.bot_logger import InfoLogger, ErrorLogger


class WorkerManagerService:
    """
    My solution to avoid having a forever-running async thread(?) for each worker.

    This class (which is treated as a singleton) will be responsible for knowing when each periodic or scheduled task
        should run using an asyncio.PriorityQueue.

    Workers can be of two types: periodic or scheduled, often referred to here as "keep_running" and "wait_and_rerun",
        respectively.
    Periodic workers will have a predefined interval/frequency at which they should run (countdown to next run will
        start after the previous run is finished).
    Scheduled workers on the other hand are self-scheduling - meaning they will specify how long they should wait
        before running again by returning a wait time (in seconds).
    """
    def __init__(self):
        self._worker_queue = None
        self._is_running = False
        self.info_logger = InfoLogger(component=self.__class__.__name__)
        self.error_logger = ErrorLogger(component=self.__class__.__name__)

    async def run(self):
        print("WorkerManagerService is running...")
        self._is_running = True
        # ironically this is a periodic worker - can it queue itself...
        while True:
            last_handled_worker_item = None
            while (worker_item := await self._worker_queue.get()).next_run <= datetime.utcnow().timestamp():
                asyncio.get_event_loop().create_task(self.start_worker(worker_item=worker_item))
                self._worker_queue.task_done()
                last_handled_worker_item = worker_item
            if worker_item and worker_item != last_handled_worker_item:
                await self._worker_queue.put(worker_item)
            await asyncio.sleep(0.1)

    async def add_worker(self, worker_callback, worker_name, next_run=datetime.utcnow().timestamp(),
                         **kwargs):
        if not next_run:
            self.info_logger.log(f"Worker {worker_name} will not be added to "
                                 f"the queue as it is not scheduled to run again.",
                                 level=BotLogLevel.BOT_INFO)
            return
        await self._worker_queue.put(WorkerItem(next_run=next_run,
                                                worker_callback=worker_callback,
                                                worker_name=worker_name,
                                                **kwargs))

    async def start_worker(self, worker_item):
        try:
            if inspect.iscoroutinefunction(worker_item.worker_callback):
                wait_time = await worker_item.worker_callback(**worker_item.kwargs)
            else:
                wait_time = worker_item.worker_callback(**worker_item.kwargs)
        except Exception as e:
            wait_time = WORKER_RETRY_ON_ERROR_DELAY.get(worker_item.worker_name, 300)
            self.error_logger.log(f"Error while running worker {worker_item.worker_name}.\n"
                                  f"Retrying in {wait_time} seconds: {e}\n"
                                  f"{traceback.format_exc()}")
        else:
            if worker_item.worker_name in PERIODIC_WORKER_FREQUENCY:
                wait_time = PERIODIC_WORKER_FREQUENCY[worker_item.worker_name]

        if wait_time:
            next_run = datetime.utcnow().timestamp() + wait_time
        else:
            next_run = None

        await self.add_worker(worker_callback=worker_item.worker_callback,
                              worker_name=worker_item.worker_name,
                              next_run=next_run,
                              **worker_item.kwargs)

    async def register_workers(self):
        """
        This function will be called on startup to register all workers with worker decorators.
        """
        self._worker_queue = asyncio.PriorityQueue()
        # ugly imports here to avoid circular imports
        from .custom_tasks import CustomTasks
        from components.music_components.youtube_music_component import YoutubeMusicComponent
        from globals_.clients import reminder_service, xp_service
        custom_tasks = CustomTasks()

        worker_callbacks = [YoutubeMusicComponent().music_download_worker,
                            xp_service.xp_gain,
                            xp_service.xp_adjustment,
                            xp_service.queue_members_for_xp_decay,
                            xp_service.xp_decay,
                            xp_service.xp_sync,
                            reminder_service.run,
                            custom_tasks.cache_cleanup]

        for worker_callback in worker_callbacks:
            await self.add_worker(worker_callback=worker_callback,
                                  worker_name=worker_callback.worker_data['name'],
                                  next_run=datetime.utcnow().timestamp() + worker_callback.worker_data['initial_delay'],
                                  **worker_callback.worker_data['kwargs'])
        worker_list_str = "\n• ".join([worker_callback.worker_data['name'] for worker_callback in worker_callbacks])
        self.info_logger.log(f"Registered workers:\n• {worker_list_str}",
                             level=BotLogLevel.BOT_INFO)


class WorkerItem:
    def __init__(self, next_run, worker_callback, worker_name, **kwargs):
        self.next_run = next_run
        self.worker_callback = worker_callback
        self.worker_name = worker_name
        self.kwargs = kwargs or {}

    def __lt__(self, other):
        return self.next_run < other.next_run

    def __gt__(self, other):
        return self.next_run > other.next_run
