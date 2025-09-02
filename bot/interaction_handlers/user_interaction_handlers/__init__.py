from bot.interaction_handlers import BaseInteractionHandler


class UserInteractionHandler(BaseInteractionHandler):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if cls is UserInteractionHandler:
            raise TypeError("UserInteractionHandler cannot be instantiated directly. "
                            "Please use a subclass instead.")
        return super().__new__(cls)

    async def preprocess_and_validate(self, *args, **kwargs):
        await super().preprocess_and_validate(*args, **kwargs)
