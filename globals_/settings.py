import os
import sys


class Settings:
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'prod')
    if ENVIRONMENT not in ['prod']:  # you can use this to add more environments
        raise Exception(f"Invalid environment: {ENVIRONMENT}")

    @property
    def no_log(self):  # limits logging to prints only
        return os.environ.get('NOLOG', 'false').lower() == 'true'

    @property
    def main_path(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def os_type(self):
        from globals_.constants import OSType
        return OSType.LINUX if sys.platform.lower() == 'linux' \
            else OSType.WINDOWS if sys.platform.lower() == 'win32' \
            else OSType.OTHER

    @property
    def logging_directory(self):
        inner_directory = f"logs_{self.ENVIRONMENT}"
        return self._build_path(['logs', inner_directory], append_main_path=True)

    @staticmethod
    def _build_path(relative_path_params: [], append_main_path=True):
        # copied here from helpers to avoid circular imports
        from globals_.constants import OSType
        if settings.os_type == OSType.WINDOWS:
            relative_path = '\\' + '\\'.join(relative_path_params)
        else:
            relative_path = '/' if (append_main_path and not settings.main_path.endswith('/')) else ''
            relative_path += '/'.join(relative_path_params)
        path = (settings.main_path + relative_path) if append_main_path else relative_path
        if path.startswith("\\C:\\"):
            path = path.replace("\\C:\\", "C:\\", 1)
        return path


settings = Settings()
