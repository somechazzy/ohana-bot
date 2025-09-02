from api.views.base_view import APIViewV1
from bot.utils.helpers.application_emojis_helper import sync_up_application_emojis
from utils.helpers.api_helpers import api_response


class EmojisSyncView(APIViewV1):
    route = '/emojis/sync'
    AUTH_REQUIRED = True

    async def post(self):
        """
        Sync up application emojis with Discord and sync them back to the cache.
        """
        await sync_up_application_emojis(refetch_and_set=True)
        return api_response({"message": "Emojis sync done."}, status=200)
