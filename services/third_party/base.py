from internal.bot_logger import InfoLogger, ErrorLogger


class ThirdPartyService:

    def __init__(self):
        self.info_logger = InfoLogger(self.__class__.__name__)
        self.error_logger = ErrorLogger(self.__class__.__name__)
