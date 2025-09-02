import discord

from common.app_logger import AppLogger
from common.decorators import suppress_and_log
from constants import AppLogCategory


@suppress_and_log()
def log_dm(message: discord.Message):
    """
    Log a DM message to the bot owner.
    Args:
        message (discord.Message): The DM message to log.
    """
    media_list = []
    for attachment in message.attachments:
        media_list.append(f"[{attachment.content_type}] ({attachment.filename}) {attachment.url}")
    for sticker in message.stickers:
        media_list.append(f"[sticker] ({sticker.name}) {sticker.url}")

    msg_content = "> " + message.content.strip().replace("\n", "\n> ")
    body = f"Received DM from {message.author}\n{msg_content}\n{'\n'.join(media_list)}"

    AppLogger('DMLogger').info(
        message=body,
        category=AppLogCategory.BOT_DM_RECEIVED,
        log_to_discord=True,
        extras={"user_id": message.author.id}
    )
