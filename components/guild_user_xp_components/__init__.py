from components import BaseComponent


class BaseGuildUserXPComponent(BaseComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if cls is BaseGuildUserXPComponent:
            raise TypeError("BaseGuildUserXPComponent is an abstract class and cannot be instantiated directly.")
        return super().__new__(cls)
