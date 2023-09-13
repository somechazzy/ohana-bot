from internal.bot_logger import InfoLogger, ErrorLogger


class BaseComponent:

    def __init__(self, *args, **kwargs):
        self.component_name = self.__class__.__name__
        self.info_logger = InfoLogger()
        self.error_logger = ErrorLogger()
