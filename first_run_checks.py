"""
First run checks: just to make sure you've set up everything correctly.
"""

from globals_ import constants
from auth import auth


def perform_checks():
    failed_config_checks = []
    failed_constants_checks = []
    failed_auth_checks = []
    if not constants.BOT_OWNER_ID:
        failed_config_checks.append("BOT_OWNER_ID")
    if not constants.DISCORD_LOGGING_CHANNEL_ID:
        failed_config_checks.append("DISCORD_LOGGING_CHANNEL_ID")
    if not constants.SUPPORT_SERVER_ID:
        failed_config_checks.append("SUPPORT_SERVER_ID")
    if not constants.OWNER_COMMAND_PREFIX or len(constants.OWNER_COMMAND_PREFIX) != 2:
        failed_config_checks.append("OWNER_COMMAND_PREFIX")

    if any(not emoji_id for emoji_id in constants.PLAYER_ACTION_CUSTOM_EMOJI_MAP.values()):
        failed_constants_checks.append("PLAYER_ACTION_CUSTOM_EMOJI_MAP")
    if any(not value for key, value
           in constants.GeneralButtonEmoji.__dict__.items()
           if not key.startswith('_') and not key.endswith('__')):
        failed_constants_checks.append("GeneralButtonEmoji")

    if not auth.BOT_TOKEN:
        failed_auth_checks.append("BOT_TOKEN")
    if not auth.FIREBASE_CONFIG or not auth.FIREBASE_CONFIG.get("apiKey") or not auth.FIREBASE_CONFIG.get("databaseURL") \
            or not auth.FIREBASE_CONFIG.get("serviceAccount") or any(key not in auth.FIREBASE_CONFIG for key in
                                                                     ["authDomain", "storageBucket", "apiKey"]):
        failed_auth_checks.append("FIREBASE_CONFIG")
    if not auth.SPOTIFY_CLIENT_ID or not auth.SPOTIFY_CLIENT_SECRET:
        failed_auth_checks.append("SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET")
    if not auth.MYANIMELIST_CLIENT_ID:
        failed_auth_checks.append("MYANIMELIST_CLIENT_ID")

    if failed_constants_checks or failed_auth_checks or failed_config_checks:
        print("You have the following issues:")
        if failed_constants_checks:
            print("\tFile: globals_/constants.py")
            for failed_constant in failed_constants_checks:
                print(f"\t\t{failed_constant}")
        if failed_auth_checks:
            print("\tFile: auth/auth_prod.py")
            for failed_auth in failed_auth_checks:
                print(f"\t\t{failed_auth}")
        if failed_config_checks:
            print("\tFile: globals_/_config/prod.py")
            for failed_config in failed_config_checks:
                print(f"\t\t{failed_config}")
        print("Make sure you've set them right then run the bot again.")
        exit()
