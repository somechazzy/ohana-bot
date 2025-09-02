from components import BaseComponent


class BaseGuildSettingsComponent(BaseComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if cls is BaseGuildSettingsComponent:
            raise TypeError("BaseGuildSettingsComponent is an abstract class and cannot be instantiated directly.")
        return super().__new__(cls)
