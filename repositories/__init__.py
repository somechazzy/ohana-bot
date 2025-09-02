from common.db import AsyncSessionLocal


class BaseRepo:
    """
    Base repository class that defines the interface for all repositories.
    """
    def __new__(cls, *args, **kwargs):
        if cls is BaseRepo:
            raise TypeError("BaseRepo is an abstract class and cannot be instantiated directly.")
        return super().__new__(cls)

    def __init__(self, session: AsyncSessionLocal):
        self._session: AsyncSessionLocal = session
