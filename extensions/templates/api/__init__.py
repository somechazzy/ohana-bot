from api.views.base_view import APIViewV1


class BaseExtendedAPIViewV1(APIViewV1):
    ROUTE = None
    AUTH_REQUIRED = True
    LOG_REQUEST = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if cls is APIViewV1:
            raise TypeError("BaseExtendedAPIViewV1 class cannot be instantiated.")
        if cls.ROUTE is None:
            raise ValueError(f"{cls.__name__} must define a ROUTE class variable.")
        return super().__new__(cls)
