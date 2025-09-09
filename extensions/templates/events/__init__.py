
class _BaseEventHandler:
    """
    Base class for event handlers. Do not inherit from this class directly.
    """
    _event_group = None
    _event_name = None

    def __init__(self, **kwargs):
        from common.app_logger import AppLogger
        self._kwargs = kwargs
        self.logger = AppLogger(self.__class__.__name__)

    async def check(self) -> bool:
        """
        Check if the event handler should process the event.
        Override this method in subclasses to implement custom checks.

        Returns:
            bool: True if the handler should process the event, False otherwise.
        """
        raise NotImplementedError()

    async def handle_event(self):
        """
        Handler for the event.
        Override this method in subclasses to implement the event handling logic.
        """
        raise NotImplementedError()

    @classmethod
    def event_group(cls) -> str:
        if not cls._event_group:
            raise NotImplementedError("Event group not set.")
        return cls._event_group

    @classmethod
    def event_name(cls) -> str:
        if not cls._event_name:
            raise NotImplementedError("Event name not set.")
        return cls._event_name
