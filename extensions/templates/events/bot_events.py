"""
Templates for custom extensions handling bot-related events.
"""
from . import _BaseEventHandler


class BaseOnReadyEventHandler(_BaseEventHandler):
    """
    Base template for on-ready event handlers.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaseOnConnectEventHandler(_BaseEventHandler):
    """
    Base template for on-connect event handlers.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaseOnErrorEventHandler(_BaseEventHandler):
    """
    Base template for on-error event handlers.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
