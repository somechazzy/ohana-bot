import asyncio
from datetime import datetime
from types import coroutine

from constants import PERIODIC_WORKER_FREQUENCY, AppLogCategory, WORKER_RETRY_ON_ERROR_DELAY
from common.app_logger import AppLogger
from utils.helpers.context_helpers import create_isolated_task


class WorkerManagerService:
    """
    This class will be responsible for knowing when each periodic or scheduled task should run using an
    asyncio.PriorityQueue.

    Workers can be of two types: periodic or scheduled.

    Periodic workers will have a predefined interval/frequency at which they should run (countdown to next run will
    start after the previous run is finished).

    Scheduled workers however are self-scheduling, meaning they will specify how long they should wait before running
    again by returning a wait time (in seconds).
    """
    def __init__(self):
        self._worker_queue: asyncio.PriorityQueue = None  # type: ignore
        self._is_running: bool = False
        self.logger = AppLogger(component=self.__class__.__name__)

    async def run(self):
        self.logger.debug("WorkerManagerService is running...")
        self._is_running = True
        while True:
            last_handled_worker_item = None
            while (worker_item := await self._worker_queue.get()).next_run <= datetime.now().timestamp():
                create_isolated_task(self.start_worker(worker_item=worker_item))
                self._worker_queue.task_done()
                last_handled_worker_item = worker_item
            if worker_item and worker_item != last_handled_worker_item:
                await self._worker_queue.put(worker_item)
            await asyncio.sleep(0.1)

    async def add_worker(self,
                         worker_callable: coroutine,
                         worker_name: str,
                         next_run: float = datetime.now().timestamp(),
                         **kwargs):
        """
        Add a worker to the queue.
        Args:
            worker_callable (coroutine): The coroutine function that represents the worker to be added.
            worker_name (str): The name of the worker.
            next_run (float): The timestamp (in seconds) when the worker should run next.
        """
        if not next_run:
            self.logger.info(f"Worker {worker_name} will not be added to "
                             f"the queue as it is not scheduled to run again.",
                             category=AppLogCategory.APP_GENERAL)
            return
        await self._worker_queue.put(WorkerItem(next_run=next_run,
                                                worker_callable=worker_callable,
                                                worker_name=worker_name,
                                                **kwargs))

    async def start_worker(self, worker_item: 'WorkerItem'):
        """
        Start a worker by executing its callback and rescheduling it based on its return value or predefined frequency.
        Args:
            worker_item (WorkerItem): The worker item containing the callback and scheduling information.
        """
        try:
            wait_time = await worker_item.worker_callable(**worker_item.kwargs)
        except Exception as e:
            wait_time = WORKER_RETRY_ON_ERROR_DELAY.get(worker_item.worker_name, 300)
            self.logger.error(f"Error while running worker {worker_item.worker_name}.\n"
                              f"Retrying in {wait_time} seconds: {e}\n")
        else:
            if worker_item.worker_name in PERIODIC_WORKER_FREQUENCY:
                wait_time = PERIODIC_WORKER_FREQUENCY[worker_item.worker_name]

        if wait_time:
            next_run = datetime.now().timestamp() + wait_time
        else:
            next_run = None

        await self.add_worker(worker_callable=worker_item.worker_callable,
                              worker_name=worker_item.worker_name,
                              next_run=next_run,
                              **worker_item.kwargs)

    async def register_workers(self):
        """
        This method will be called on startup to register all workers with worker decorators.
        """
        self._worker_queue = asyncio.PriorityQueue()
        from .app_workers import AppWorkers
        from clients import reminder_service, xp_service

        worker_callables = []
        app_workers = AppWorkers()

        worker_callables.append(app_workers.cache_cleanup)
        worker_callables.append(app_workers.log_ingestion)

        worker_callables.append(reminder_service.reminder_producer)
        worker_callables.append(reminder_service.reminder_consumer)

        worker_callables.append(xp_service.message_consumer)
        worker_callables.append(xp_service.xp_action_consumer)
        worker_callables.append(xp_service.decay_producer)
        worker_callables.append(xp_service.decay_consumer)
        worker_callables.append(xp_service.xp_sync_to_database)

        for worker_callable in worker_callables:
            await self.add_worker(
                worker_callable=worker_callable,
                worker_name=worker_callable.worker_data['name'],
                next_run=datetime.now().timestamp() + worker_callable.worker_data['initial_delay'],
                **worker_callable.worker_data['kwargs']
            )
        worker_list_str = "\n• ".join([worker_callable.worker_data['name'] for worker_callable in worker_callables])
        self.logger.info(f"Registered workers:\n• {worker_list_str}", category=AppLogCategory.APP_GENERAL,
                         log_to_discord=True)


class WorkerItem:
    def __init__(self, next_run, worker_callable, worker_name, **kwargs):
        self.next_run: float = next_run
        self.worker_callable: coroutine = worker_callable
        self.worker_name: str = worker_name
        self.kwargs: dict = kwargs or {}

    def __lt__(self, other):
        return self.next_run < other.next_run

    def __gt__(self, other):
        return self.next_run > other.next_run
