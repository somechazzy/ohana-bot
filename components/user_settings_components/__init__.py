from components import BaseComponent


class BaseUserSettingsComponent(BaseComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if cls is BaseUserSettingsComponent:
            raise TypeError("BaseUserSettingsComponent is an abstract class and cannot be instantiated directly.")
        return super().__new__(cls)
