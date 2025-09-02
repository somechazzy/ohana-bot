from aiohttp import web

from utils.helpers.context_helpers import get_context_id


def api_response(body: dict | str, status: int = 200, headers: dict | None = None) -> web.Response:
    """
    Create a JSON response for the API.

    Args:
        body (dict | str): The body of the response, typically a dictionary.
        status (int): The HTTP status code for the response, default is 200.
        headers (dict): Optional headers to include in the response.

    Returns:
        web.Response: An aiohttp web.Response object with the specified body, status, and headers.
    """
    if headers is None:
        headers = {}
    if isinstance(body, str):
        body = {
            "message": body
        }
    headers['Content-Type'] = 'application/json'
    headers['X-Request-ID'] = get_context_id()
    return web.json_response(body, status=status)
