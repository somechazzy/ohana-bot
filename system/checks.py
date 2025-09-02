import inspect
import os
import re
import socket
import time

import requests
# noinspection PyPackageRequirements
import pymysql


def validate_discord_bot_token(discord_bot_token: str):
    try:
        response = requests.get(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": f"Bot {discord_bot_token}"}
        )
        if response.status_code not in range(200, 300):
            return f"Invalid DISCORD_BOT_TOKEN: status={response.status_code}."
    except Exception as e:
        return f"Error validating DISCORD_BOT_TOKEN: {e}"
    return None


def validate_logtail_token(logtail_token: str):
    try:
        response = requests.post("https://in.logs.betterstack.com",
                                 headers={"Authorization": f"Bearer {logtail_token}"},
                                 json=[])
        if response.status_code in range(400, 500):
            return f"Invalid LOGTAIL_TOKEN: status={response.status_code}."
    except Exception as e:
        return f"Error validating LOGTAIL_TOKEN: {e}"
    return None


def validate_myanimelist_client_id(myanimelist_client_id: str):
    try:
        response = requests.get("https://api.myanimelist.net/v2/anime/1",
                                headers={"X-MAL-CLIENT-ID": myanimelist_client_id})
        if response.status_code in range(400, 500):
            return f"Invalid MYANIMELIST_CLIENT_ID: status={response.status_code}."
    except Exception as e:
        return f"Error validating MYANIMELIST_CLIENT_ID: {e}"
    return None


def validate_rapid_api_key(rapid_api_key: str):
    try:
        response = requests.get("https://mashape-community-urban-dictionary.p.rapidapi.com/define?term=ohana",
                                headers={'x-rapidapi-key': rapid_api_key,
                                         'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com"})
        if response.status_code in range(400, 500):
            return f"Invalid RAPID_API_KEY: status={response.status_code}."
    except Exception as e:
        return f"Error validating RAPID_API_KEY: {e}"
    return None


def validate_merriam_api_key(merriam_api_key: str):
    try:
        response = requests.get("https://dictionaryapi.com/api/v3/references/collegiate/json/{term}",
                                headers={"key": merriam_api_key})
        if response.status_code in range(400, 500):
            return f"Invalid MERRIAM_API_KEY: status={response.status_code}."
    except Exception as e:
        return f"Error validating MERRIAM_API_KEY: {e}"
    return None


def wait_and_validate_mysql_connection(user: str, password: str, host: str, port: int, db: str, retries: int = 5):
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db,
            port=port,
            connect_timeout=5,
        )
        conn.close()
    except Exception as e:
        if retries > 0:
            time.sleep(5)
            retries -= 1
            print(f"Retrying MySQL connection ({5 - retries}/5)...")
            return wait_and_validate_mysql_connection(user, password, host, port, db, retries - 1)
        return f"Error while connecting to MySQL: {e}"
    return None


def validate_logging_channel_webhook_url(logging_channel_webhook_url):
    match = re.search(r'discord(?:app)?\.com/api/webhooks/(?P<id>[0-9]{17,})/(?P<token>[A-Za-z0-9.\-_]{60,})',
                      logging_channel_webhook_url)
    if match is None:
        return 'Invalid webhook URL given.'
    match = match.groupdict()
    webook_id, webhook_token = match['id'], match['token']
    try:
        response = requests.get(f"https://discord.com/api/v10/webhooks/{webook_id}/{webhook_token}")
        if response.status_code in range(400, 500):
            return f"Invalid LOGGING_CHANNEL_WEBHOOK_URL: status={response.status_code}."
    except Exception as e:
        return f"Error validating LOGGING_CHANNEL_WEBHOOK_URL: {e}"
    return None


def validate_api_service_port(api_service_port: str):
    if not api_service_port.isdigit() or not (1 <= int(api_service_port) <= 65535):
        return "API_SERVICE_PORT must be a number between 1 and 65535."
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', int(api_service_port)))
            if result == 0:
                return f"Port {api_service_port} is already in use. Please choose a different port."
    except Exception as e:
        return f"Error checking API_SERVICE_PORT: {e}"
    return None


def run_pre_startup_checks():
    if os.getenv("SKIP_PRE_STARTUP_CHECKS", "false").lower() == "true":
        print("Skipping pre-startup checks: SKIP_PRE_STARTUP_CHECKS is set to true.\n")
        return
    print("Running pre-startup checks...")
    errors = []

    # Database connection
    db_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
    missing_db_vars = [var for var in db_vars if not os.environ.get(var)]
    for var in missing_db_vars:
        errors.append(f"{var} environment variable is not set.")
    db_port = os.environ.get('DB_PORT')
    if db_port and not db_port.isdigit():
        errors.append("DB_PORT must be a numeric string.")
    if not missing_db_vars and db_port and db_port.isdigit():
        err = wait_and_validate_mysql_connection(
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=int(db_port),
            db=os.environ.get('DB_NAME')
        )
        if err:
            errors.append(err)

    if not (bot_owner_id := os.environ.get("BOT_OWNER_ID")):
        errors.append("BOT_OWNER_ID environment variable is not set.")
    elif not bot_owner_id.isdigit():
        errors.append("BOT_OWNER_ID must be a numeric string.")

    # Auth tokens and API keys
    discord_bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    if not discord_bot_token:
        errors.append("DISCORD_BOT_TOKEN environment variable is not set.")
    else:
        err = validate_discord_bot_token(discord_bot_token)
        if err:
            errors.append(err)
    if not os.environ.get('API_AUTH_TOKEN'):
        errors.append("API_AUTH_TOKEN environment variable is not set.")
    logtail_token = os.environ.get('LOGTAIL_TOKEN')
    if logtail_token:
        err = validate_logtail_token(logtail_token)
        if err:
            errors.append(err)
    if os.getenv("SKIP_INTEGRATIONS_CHECKS", "false").lower() != "true":
        myanimelist_client_id = os.environ.get('MYANIMELIST_CLIENT_ID')
        if myanimelist_client_id:
            err = validate_myanimelist_client_id(myanimelist_client_id)
            if err:
                errors.append(err)
        rapid_api_key = os.environ.get('RAPID_API_KEY')
        if rapid_api_key:
            err = validate_rapid_api_key(rapid_api_key)
            if err:
                errors.append(err)
        merriam_api_key = os.environ.get('MERRIAM_API_KEY')
        if merriam_api_key:
            err = validate_merriam_api_key(merriam_api_key)
            if err:
                errors.append(err)

    # Logging and debugging
    if os.environ.get('EXTERNAL_LOGGING_ENABLED', 'true').lower() not in ['true', 'false']:
        errors.append("EXTERNAL_LOGGING_ENABLED must be 'true' or 'false'.")
    if os.environ.get('DEBUG_EXTERNALLY', 'false').lower() not in ['true', 'false']:
        errors.append("DEBUG_EXTERNALLY must be 'true' or 'false'.")
    if os.environ.get('DEBUG_ENABLED', 'false').lower() not in ['true', 'false']:
        errors.append("DEBUG_ENABLED must be 'true' or 'false'.")
    if os.environ.get('SQL_ECHO', 'false').lower() not in ['true', 'false']:
        errors.append("SQL_ECHO must be 'true' or 'false'.")
    logging_channel_webhook_url = os.environ.get('LOGGING_CHANNEL_WEBHOOK_URL')
    if logging_channel_webhook_url:
        err = validate_logging_channel_webhook_url(logging_channel_webhook_url)
        if err:
            errors.append(err)
    logging_directory = os.environ.get('LOGGING_DIRECTORY')
    if logging_directory:
        try:
            os.makedirs(logging_directory, exist_ok=True)
            test_file_path = os.path.join(logging_directory, 'test_write_permissions.tmp')
            with open(test_file_path, 'w') as test_file:
                test_file.write('test')
            os.remove(test_file_path)
        except Exception as e:
            errors.append(f"Logging directory '{logging_directory}' is not writable: {e}")

    # App configs
    if os.environ.get('SYNC_COMMANDS_ON_STARTUP', 'true').lower() not in ['true', 'false']:
        errors.append("SYNC_COMMANDS_ON_STARTUP must be 'true' or 'false'.")
    if os.environ.get('SYNC_EMOJIS_ON_STARTUP', 'true').lower() not in ['true', 'false']:
        errors.append("SYNC_EMOJIS_ON_STARTUP must be 'true' or 'false'.")
    if os.environ.get('ENABLE_API_SERVICE', 'true').lower() not in ['true', 'false']:
        errors.append("ENABLE_API_SERVICE must be 'true' or 'false'.")
    api_service_port = os.environ.get('API_SERVICE_PORT')
    if api_service_port:
        err = validate_api_service_port(api_service_port)
        if err:
            errors.append(err)
    owner_command_prefix = os.environ.get('OWNER_COMMAND_PREFIX')
    if owner_command_prefix is not None and owner_command_prefix.strip() == "":
        errors.append("OWNER_COMMAND_PREFIX cannot be an empty string.")
    chunk_guilds_setting = os.environ.get('CHUNK_GUILDS_SETTING')
    if chunk_guilds_setting and chunk_guilds_setting not in ['AT_STARTUP', 'LAZY', 'ON_DEMAND']:
        errors.append("CHUNK_GUILDS_SETTING must be one of 'AT_STARTUP', 'LAZY', or 'ON_DEMAND'.")
    if os.environ.get('REDIRECT_STDOUT_TO_LOGGER', 'true').lower() not in ['true', 'false']:
        errors.append("REDIRECT_STDOUT_TO_LOGGER must be 'true' or 'false'.")

    if errors:
        print("Pre-startup checks failed with the following errors:")
        for error in errors:
            print(f"- {error}")
        exit(1)
    else:
        print("All pre-startup checks passed.")


def verify_slashes_decorators():
    from bot.slashes.user_slashes.animanga_user_slashes import AnimangaUserSlashes
    from bot.slashes.user_slashes.general_user_slashes import GeneralUserSlashes
    from bot.slashes.user_slashes.moderation_user_slashes import ModerationUserSlashes
    from bot.slashes.user_slashes.reminder_user_slashes import RemindUserSlashes
    from bot.slashes.user_slashes.utility_user_slashes import UtilityUserSlashes
    from bot.slashes.user_slashes.xp_user_slashes import XPUserSlashes
    for cls in [AnimangaUserSlashes, GeneralUserSlashes, ModerationUserSlashes,
                RemindUserSlashes, UtilityUserSlashes, XPUserSlashes]:
        for name, member in cls.__dict__.items():
            if inspect.isfunction(member) and not name.startswith('_'):
                if not inspect.iscoroutinefunction(member):
                    raise RuntimeError(f"The method {name} in class {cls.__name__} is not a coroutine function.")
                if not hasattr(member, "__is_slash_command__"):
                    raise RuntimeError(f"The method {name} in class {cls.__name__} is missing the "
                                       f"@slash_command() decorator.")
