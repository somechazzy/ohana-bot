from pathlib import Path

import aiofiles

from clients import discord_client, emojis
from common.app_logger import AppLogger
from constants import DefinedAsset


def get_emoji_name_path_map() -> dict[str, str]:
    """
    Scans the emoji directory and creates a mapping of emoji names to their file paths.
    Returns:
        dict[str, str]: A dictionary mapping emoji names to their file paths.
    """
    emoji_dir = Path(DefinedAsset.EMOJIS_BASE_DIR)
    emoji_name_path_map = {}

    for file_path in emoji_dir.rglob("*"):
        if file_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif"}:
            continue

        relative = file_path.relative_to(emoji_dir)
        emoji_name = "_".join(relative.with_suffix("").parts)
        emoji_name_path_map[emoji_name] = str(file_path)

    return emoji_name_path_map


async def sync_up_application_emojis(refetch_and_set: bool = True):
    """
    Sync emojis from assets to the Discord application and update the local cache if refetch_and_set is True.
    Args:
        refetch_and_set (bool): If True, refetches the emojis from Discord and updates the local cache.
    """
    logger = AppLogger("sync_application_emojis")
    existing_emojis = await discord_client.fetch_application_emojis()
    emoji_name_path_map = get_emoji_name_path_map()

    existing_emoji_names = {emoji.name for emoji in existing_emojis}
    emojis_to_add = {name: path for name, path in emoji_name_path_map.items() if name not in existing_emoji_names}
    if not emojis_to_add:
        return
    logger.info(f"Found {len(emojis_to_add)} new emojis to add.")

    added_emojis = []
    for emoji_name, emoji_path in emojis_to_add.items():
        async with aiofiles.open(emoji_path, mode='rb') as emoji_file:
            try:
                await discord_client.create_application_emoji(name=emoji_name, image=await emoji_file.read())
                added_emojis.append(emoji_name)
            except Exception as e:
                logger.error(f"Failed to add emoji {emoji_name}: {e}")

    if added_emojis:
        logger.info(f"Added {len(added_emojis)} new emojis: {', '.join(added_emojis)}")
    if refetch_and_set:
        emojis.set_emojis(await discord_client.fetch_application_emojis())
    logger.info("Emoji sync completed.")
