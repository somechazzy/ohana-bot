import os

from constants import ChunkGuildsSetting

BOT_OWNER_ID = int(os.environ["BOT_OWNER_ID"])

# Authentication and API Keys
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
API_AUTH_TOKEN = os.environ['API_AUTH_TOKEN']
LOGTAIL_TOKEN = os.environ.get('LOGTAIL_TOKEN')
MYANIMELIST_CLIENT_ID = os.environ.get('MYANIMELIST_CLIENT_ID')
RAPID_API_KEY = os.environ.get('RAPID_API_KEY')
MERRIAM_API_KEY = os.environ.get('MERRIAM_API_KEY')

# Logging and Debugging
EXTERNAL_LOGGING_ENABLED = os.environ.get('EXTERNAL_LOGGING_ENABLED', 'true').lower() == 'true'
DEBUG_EXTERNALLY = os.environ.get('DEBUG_EXTERNALLY', 'false').lower() == 'true'
DEBUG_ENABLED = os.environ.get('DEBUG_ENABLED', 'false').lower() == 'true'
SQL_ECHO = os.environ.get('SQL_ECHO', 'false').lower() == 'true'
LOGGING_CHANNEL_WEBHOOK_URL = os.environ.get('LOGGING_CHANNEL_WEBHOOK_URL')
LOGGING_DIRECTORY = os.environ.get('LOGGING_DIRECTORY', 'logs')
REDIRECT_STDOUT_TO_LOGGER = os.environ.get('REDIRECT_STDOUT_TO_LOGGER', 'false').lower() == 'true'

# Database Configuration
DB_CONFIG = {
    "driver": "mysql+aiomysql",
    "user": os.environ['DB_USER'],
    "password": os.environ['DB_PASSWORD'],
    "host": os.environ['DB_HOST'],
    "port": int(os.environ['DB_PORT']),
    "database": os.environ['DB_NAME'],
}

# App configs
SYNC_COMMANDS_ON_STARTUP = os.environ.get('SYNC_COMMANDS_ON_STARTUP', 'true').lower() == 'true'
SYNC_EMOJIS_ON_STARTUP = os.environ.get('SYNC_EMOJIS_ON_STARTUP', 'true').lower() == 'true'
ENABLE_API_SERVICE = os.environ.get('ENABLE_API_SERVICE', 'true').lower() == 'true'
API_SERVICE_PORT = int(os.environ.get('API_SERVICE_PORT', 8000))
OWNER_COMMAND_PREFIX = os.environ.get('OWNER_COMMAND_PREFIX', '..')
CHUNK_GUILDS_SETTING = os.environ.get('CHUNK_GUILDS_SETTING', ChunkGuildsSetting.LAZY)
