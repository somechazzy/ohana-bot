"""
Templates for custom extensions handling bot-related events.
"""
from . import _BaseEventHandler


class BaseOnReadyEventHandler(_BaseEventHandler):
    """
    Base template for on-ready event handlers.
    """
    _event_group = "bot"
    _event_name = "on_ready"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaseOnConnectEventHandler(_BaseEventHandler):
    """
    Base template for on-connect event handlers.
    """
    _event_group = "bot"
    _event_name = "on_connect"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaseOnErrorEventHandler(_BaseEventHandler):
    """
    Base template for on-error event handlers.
    """
    _event_group = "bot"
    _event_name = "on_error"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
