import asyncio
# noinspection PyPackageRequirements
import contextvars
import uuid
from typing import Coroutine

_context_id_var = contextvars.ContextVar('context_id', default="default-context")


def get_context_id() -> str:
    return _context_id_var.get()


def set_context_id(context_id: str | None = None) -> contextvars.Token:
    return _context_id_var.set(context_id or uuid.uuid4().hex)


def reset_context_id(token: contextvars.Token):
    _context_id_var.reset(token)


def create_isolated_task(coro: Coroutine) -> asyncio.Task:
    """
    Create an isolated task with its own context.
    Args:
        coro (Coroutine): The coroutine to run as a task.
    Returns:
        asyncio.Task: The created task.
    """
    def runner():
        async def wrapper():
            token = set_context_id()
            try:
                await coro
            except Exception as e:
                from common.app_logger import AppLogger
                AppLogger(str(coro)).error(f"Error while executing isolated task {coro.__qualname__}: {e}")
            finally:
                reset_context_id(token)
        return asyncio.create_task(wrapper())

    return contextvars.copy_context().run(runner)


def create_task(coro: Coroutine) -> asyncio.Task:
    """
    Create a task with the current context.
    Args:
        coro (Coroutine): The coroutine to run as a task.
    Returns:
        asyncio.Task: The created task.
    """
    async def wrapper():
        try:
            await coro
        except Exception as e:
            from common.app_logger import AppLogger
            AppLogger(str(coro)).error(f"Error while executing task {coro.__qualname__}: {e}")

    return asyncio.get_running_loop().create_task(wrapper())
