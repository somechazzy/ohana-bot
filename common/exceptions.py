"""
This module contains custom exceptions. All exceptions should inherit from OhanaException or its children.
"""
from aiohttp.web_exceptions import HTTPException


# noinspection PyArgumentList
class OhanaException(Exception):
    def __init__(self, message: str, **kwargs):
        super().__init__(message)
        self.message: str = message
        self.debugging_info: dict | str | None = kwargs.get("debugging_info")


class UserReadableException(OhanaException):
    def __init__(self, user_message: str | None = None, message: str | None = None, **kwargs):
        super().__init__(message=message or user_message, **kwargs)
        self.user_message: str = user_message

    def __str__(self):
        return f"{self.message} | User Message: {self.user_message}"


class UserInputException(UserReadableException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, user_message=message, **kwargs)


class ExternalServiceException(UserReadableException):
    def __init__(self, message: str,
                 status_code: int,
                 debugging_info: dict | str | None = None,
                 user_message: str | None = None,
                 alert_worthy: bool = False,
                 **kwargs):
        super().__init__(message=message,
                         debugging_info=debugging_info,
                         user_message=user_message,
                         **kwargs)
        self.status_code: int = status_code
        self.alert_worthy: bool = alert_worthy

    def __str__(self):
        return (f"{self.message} | Status Code: {self.status_code} | "
                f"Debugging Info: {self.debugging_info} | User Message: {self.user_message} | "
                f"Alert Worthy: {self.alert_worthy}")


class InvalidCommandUsageException(UserReadableException):
    def __init__(self, user_message: str | None = None, **kwargs):
        super().__init__(user_message, **kwargs)
        self.user_message: str = user_message

    def __str__(self):
        return f"User Message: {self.user_message}"


class InvalidInteractionException(UserReadableException):
    def __init__(self, user_message: str | None = None, **kwargs):
        super().__init__(user_message, **kwargs)
        self.user_message: str = user_message

    def __str__(self):
        return f"User Message: {self.user_message}"


class ModerationHierarchyError(InvalidCommandUsageException):
    def __init__(self, user_message: str | None = None, **kwargs):
        super().__init__(user_message, **kwargs)
        self.user_message: str = user_message


### API Exceptions


class APIException(HTTPException):
    status = 500

    def __new__(cls, **kwargs):
        if cls is APIException:
            raise TypeError("APIException class cannot be instantiated directly.")
        return super().__new__(cls, **kwargs)

    def __init__(self, message: str, **kwargs):
        super().__init__(text=message, **kwargs)
        self.message: str = message

    def response_body(self):
        return {
            "error": self.message
        }

    def __str__(self):
        return f"APIException: {self.message} | Status: {self.status}"


class APIBadRequestException(APIException):
    status = 400

    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, **kwargs)


class APIUnauthorizedException(APIException):
    status = 401

    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, **kwargs)
