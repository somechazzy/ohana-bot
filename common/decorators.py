import asyncio
import inspect
import time
import traceback
from functools import wraps
from types import coroutine

from common.db import execute_post_commit_actions, execute_post_rollback_actions


def periodic_worker(name: str, initial_delay: int = 0, **kwargs_):
    """
    Decorator to mark a coroutine function as a periodic worker.
    Args:
        name (str): The name of the worker.
        initial_delay (int): Initial delay before the first run in seconds.
        **kwargs_: Additional keyword arguments to be passed to the worker manager.
    """
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Periodic worker must be a coroutine function.")
        func.worker_data = {
            "name": name,
            "initial_delay": initial_delay,
            "kwargs": kwargs_
        }

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def self_scheduling_worker(name: str, initial_delay: int = 0, **kwargs_):
    """
    Decorator to mark a coroutine function as a self-scheduling worker.
    Args:
        name (str): The name of the worker.
        initial_delay (int): Initial delay before the first run in seconds.
        **kwargs_: Additional keyword arguments to be passed to the worker manager.
    """
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Self-scheduling worker must be a coroutine function.")
        func.worker_data = {
            "name": name,
            "initial_delay": initial_delay,
            "kwargs": kwargs_
        }

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def suppress_and_log(log: bool = True, ignore_exceptions: tuple = ()):
    """
    Decorator to catch any exceptions and log them instead of raising.
    Args:
        log: Whether to log the exception.
        ignore_exceptions: Tuple of exception types to ignore and not log.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            from common.app_logger import AppLogger
            logger = AppLogger(component=func.__module__)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log and not isinstance(e, ignore_exceptions):
                    logger.warning(f"Suppress-and-log coroutine {func.__name__} raised an exception: {e}\n"
                                   f"{traceback.format_exc()}")

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            from common.app_logger import AppLogger
            logger = AppLogger(component=func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log and not isinstance(e, ignore_exceptions):
                    logger.warning(f"Suppress-and-log function {func.__name__} raised an exception: {e}\n"
                                   f"{traceback.format_exc()}")

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator


def with_retry(count: int, delay: int = 1):
    """
    Decorator to retry a function or coroutine a specified number of times with a delay between attempts.
    Args:
        count (int): Number of retry attempts.
        delay (int): Delay in seconds between attempts.
    """
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                for i in range(count):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if i == count - 1:
                            raise e
                        await asyncio.sleep(delay)
                return None
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                for i in range(count):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if i == count - 1:
                            raise e
                        time.sleep(delay)
                return None
        return wrapper
    return decorator


def rate_limit(timeframe: float, limit: int, args_key: callable):
    """
    Decorator to rate limit a function or coroutine based on the provided timeframe and limit.
    Args:
        timeframe (float): Timeframe in seconds.
        limit (int): Maximum number of calls allowed within the timeframe.
        args_key (callable): Function or lambda to generate a key based on the function's arguments.
    """
    def decorator(func):
        calls = {}
        func._rate_limit_data = calls

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = args_key(args)
                now = time.time()

                timestamps = calls.setdefault(key, [])
                timestamps[:] = [t for t in timestamps if now - t < timeframe]

                if len(timestamps) >= limit:
                    wait_time = timeframe - (now - timestamps[0])
                    await asyncio.sleep(wait_time)
                    now = time.time()
                    timestamps[:] = [t for t in timestamps if now - t < timeframe]

                timestamps.append(time.time())
                return await func(*args, **kwargs)

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                key = args_key(args)
                now = time.time()

                timestamps = calls.setdefault(key, [])
                timestamps[:] = [t for t in timestamps if now - t < timeframe]

                if len(timestamps) >= limit:
                    wait_time = timeframe - (now - timestamps[0])
                    time.sleep(wait_time)
                    now = time.time()
                    timestamps[:] = [t for t in timestamps if now - t < timeframe]

                timestamps.append(time.time())
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator


def require_db_session(coro: coroutine):
    """
    Decorator to ensure that a coroutine function runs within a database session context.
    It handles committing the session if the coroutine completes successfully,
    or rolling back the session if an exception occurs.
    Args:
        coro: The coroutine function to be decorated.
    """
    @wraps(coro)
    async def wrapper(*args, **kwargs):
        from common.db import session_context, get_session
        async with session_context():
            try:
                return await coro(*args, **kwargs)
            except Exception as e:
                await get_session().rollback()
                await execute_post_rollback_actions()
                raise e
            finally:
                await get_session().commit()
                await execute_post_commit_actions()

    return wrapper
