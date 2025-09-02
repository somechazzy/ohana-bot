"""
Shared classes and functions for components.
"""
from common.app_logger import AppLogger


class BaseComponent:
    """
    Base class for all components.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = AppLogger(component=self.__class__.__name__)

    def __new__(cls, *args, **kwargs):
        if cls is BaseComponent:
            raise TypeError("BaseComponent is an abstract class and cannot be instantiated directly.")
        return super().__new__(cls, *args, **kwargs)
