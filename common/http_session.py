import aiohttp
import requests
from datetime import datetime, timedelta, UTC

_async_http_sessions: dict[str, tuple[aiohttp.ClientSession, datetime]] = {
    # name: (session, expiry datetime)
}

_sync_http_sessions: dict[str, tuple[requests.Session, datetime]] = {
    # name: (session, expiry datetime)
}


async def get_async_http_session(name: str):
    """
    Get or create an asynchronous HTTP session
    Args:
        name (str): The identifier of the session.
    Returns:
        aiohttp.ClientSession: The asynchronous HTTP session.
    """
    if name in _async_http_sessions:
        session, expiry = _async_http_sessions[name]
        if not session.closed:
            if expiry < datetime.now(UTC):
                await session.close()
            else:
                return session
    session = aiohttp.ClientSession()
    expiry = datetime.now(UTC) + timedelta(minutes=30)
    _async_http_sessions[name] = (session, expiry)
    return session


def get_sync_http_session(name: str):
    """
    Get or create a synchronous HTTP session
    Args:
        name (str): The identifier of the session.
    Returns:
        requests.Session: The synchronous HTTP session.
    """
    if name in _sync_http_sessions:
        session, expiry = _sync_http_sessions[name]
        if expiry > datetime.now(UTC):
            return session
        session.close()
    session = requests.Session()
    expiry = datetime.now(UTC) + timedelta(minutes=30)
    _sync_http_sessions[name] = (session, expiry)
    return session
