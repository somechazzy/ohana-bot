# Ohana Discord Bot

---

* [Introduction & features](#introduction)
* [Installation](#installation)
  * [Docker](#docker)
  * [Manual installation](#manual-installation)
* [Configuration & extensions](#configuration--extensions)
* [Commands](#commands)
* [Owner management commands & API](#owner-commands-and-apis)
* [Contributing](#contributing)
* [License](#license)

---

Note: As of v3.1, the main Ohana bot runs directly on this repo. Music streaming from YT has been removed along with user libraries and playlists.

## Introduction

Ohana started as a bot to supplement other bots, but over the years it has grown into its own thing with its feature set being a little all over the place. Built using [discord.py](https://discordpy.readthedocs.io/en/stable/), with clear docstrings and type hinting all over. The bot's functionality is also easily extensible (see [Configuration & extensions](#configuration--extensions)).

It's difficult to narrow down the bot into one or two categories, so here's a list of its features instead:

* **Radio streaming**: a robust and simple VC session management system that supports ~30 radio stations, which is designed to be easily expandable. Adding a new station takes only a few minutes (and you don't even need to restart the bot for it to take effect!). You can find more details about this in the [Configuration](#configuration--extensions) section.
* **MyAnimeList & AniList integration**: search for anime and manga easily, and display all the relevant information in a clean embed. You can also link your MAL/AniList account to show off your & others' profiles, lists and stats in a navigable embed.
* **XP System**: a complex, configurable and reliable XP system with a number of standard features plus original ones:
  * Level roles
  * Customisable level-up messages
  * Leaderboards
  * Customisable XP gain rates
  * Ability to disable XP gain for chosen channels and roles
  * XP decay (an original feature, at the time of its first implementation at least), with configurable decay rate and grace period
* **Reminders**: super reliable one-time and recurring reminders, with the ability to list and edit. You can even remind others (as long as they don't block you).
* **Auto-Moderation features**: mostly standard:
  * Autoroles
  * Role menus
  * Role persistence
  * Auto-responses
  * Gallery channels & limited-messages channels
  * Moderation commands (kick, ban, mute, etc.)
  * Mod logs for any action taken by the bot or any setting changes
* **Various utility commands**
* **User and message context menu commands**

---

## Installation

You can get your own Ohana up and running in a few minutes. You can either download this repo directly, add the necessary env vars and run `main.py` (requires a MariaDB-compatible database running), or use the docker compose provided below.

> [!IMPORTANT]
> **Prerequisite**: a Discord bot application with both "Guild Members" and "Message Content" intents enabled.

### Docker
You can use the following docker-compose to get Ohana up and running quickly. Make sure to carefully read the environment section of both `ohana` and `ohana_db` services, and to set the environment variables with your own values as necessary (look for `# SET ME` comments).

> [!NOTE]
> First run might take a minute or two to set up the database and upload the bot's emojis. 

```yaml
services:
  ohana:
    image: ghcr.io/somechazzy/ohana-bot:latest
    restart: unless-stopped
    container_name: ohana
    environment:
      # ↓ Required ↓
        BOT_OWNER_ID: # SET ME  # Your Discord user ID (https://support.discord.com/hc/en-us/articles/206346498)
        DISCORD_BOT_TOKEN: # SET ME  # Discord bot token from the Discord Developer Portal (https://discord.com/developers/applications)
        API_AUTH_TOKEN: # SET ME  # Random string to serve as an auth token for internal management API (https://it-tools.tech/token-generator)
        DB_USER: ohana_app  # Must be the same as MYSQL_USER in ohana_db service
        DB_PASSWORD: # SET ME  # Must be the same as MYSQL_PASSWORD in ohana_db service
        DB_HOST: ohana_db  # Must be the same as the ohana_db service name
        DB_PORT: 3306  # Must be the same as the port exposed by the ohana_db service
        DB_NAME: ohana  # Must be the same as MYSQL_DATABASE in ohana_db service
      # ↓ Recommended for full functionality ↓
        LOGTAIL_TOKEN: # SET ME OR REMOVE ME  # Token from Logtail/BetterStack for external logging (https://betterstack.com/docs/logs/api/getting-started/#get-an-telemetry-api-token)
        LOGGING_CHANNEL_WEBHOOK_URL: # SET ME OR REMOVE ME  # For logging important things to a Discord channel (https://support.discord.com/hc/en-us/articles/228383668)
        MYANIMELIST_CLIENT_ID: # SET ME OR REMOVE ME  # For MyAnimeList integration (/mal, /anime, /manga) (https://help.myanimelist.net/hc/en-us/articles/900003108823-API)
        RAPID_API_KEY: # SET ME OR REMOVE ME  # For UrbanDictionary integration (/urban) (https://it-tools.tech/token-generator)
        MERRIAM_API_KEY: # SET ME OR REMOVE ME  # For dictionary integration (/define) (https://dictionaryapi.com/register/index - Intermediate Dictionary)
      # ↓ Logging config ↓
        EXTERNAL_LOGGING_ENABLED: true  # Set to "true" to enable external logging, has no effect if neither LOGTAIL_TOKEN nor LOGGING_CHANNEL_WEBHOOK_URL is set
        DEBUG_ENABLED: false  # Set to "true" to enable debug logging, by default only to console and log files
        DEBUG_EXTERNALLY: false  # Set to "true" to send debug logs to LOGTAIL (very spammy). Only has effect if DEBUG_ENABLED is also true
        SQL_ECHO: false  # Set to "true" to log all SQL queries to console (also spammy but doesn't log externally)
      # ↓ App config ↓
        SYNC_COMMANDS_ON_STARTUP: true  # Set to "true" to sync Discord slash commands on startup, otherwise you will need to use the owner command or API to sync
        SYNC_EMOJIS_ON_STARTUP: true  # Set to "true" to sync custom emojis on startup, otherwise you will need to use the API to sync. Either way, emojis must be synced at least once before the bot is usable
        ENABLE_API_SERVICE: true  # Set to "true" to enable the internal management API service
        OWNER_COMMAND_PREFIX: ..  # Prefix for owner-only commands
        CHUNK_GUILDS_SETTING: LAZY  # Options: Can be one of 1. AT_STARTUP: Chunk all guild members at startup (delays bot startup by one minute per 100 guilds) 2. LAZY: Chunk members over time after starting (recommended) 3. ON_DEMAND: Only chunk members per guild when needed (e.g. certain commands)
    depends_on:
      - ohana_db
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs

  ohana_db:
    image: mariadb:12.0
    container_name: ohana_db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: # SET ME  # Enter a secure DB password here for the root user
      MYSQL_DATABASE: ohana
      MYSQL_USER: ohana_app
      MYSQL_PASSWORD: # SET ME  # Enter a secure DB password here for the ohana_app user, must match DB_PASSWORD in ohana service
    # ports:  # Uncomment to expose the database outside the container, if manual DB management is needed
    #   - "3306:3306"
    volumes:
      - ./db_data:/var/lib/mysql

volumes:
  db_data:
```

### Manual installation

1. Clone this repo or download it.
2. Set up a Python 3.13 venv and install the `requirements.txt` file.
3. Set up a MariaDB-compatible database (recommended: MariaDB 12.0) and create a database and user for the bot.
4. Set the following environment variables:
    <details>
    <summary>Environment Variables</summary>
   
      #### Required

    * `BOT_OWNER_ID`: Your [Discord user ID](https://support.discord.com/hc/en-us/articles/206346498).
    * `DISCORD_BOT_TOKEN`: Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications).
    * `API_AUTH_TOKEN`: [Random string](https://it-tools.tech/token-generator) to serve as an auth token for internal management API.
    * `DB_USER`: Database user created for the bot.
    * `DB_PASSWORD`: Password for the database user.
    * `DB_HOST`: Hostname of the database (e.g. `localhost` or an IP address).
    * `DB_PORT`: Port of the database (default is usually `3306`).
    * `DB_NAME`: Name of the database created for the bot.

    #### Recommended for full functionality

    * `LOGTAIL_TOKEN`: Token from [Logtail/BetterStack](https://betterstack.com/docs/logs/api/getting-started/#get-an-telemetry-api-token) for external logging.
    * `LOGGING_CHANNEL_WEBHOOK_URL`: [Webhook URL](https://support.discord.com/hc/en-us/articles/228383668) for logging important things to a Discord channel.
    * `MYANIMELIST_CLIENT_ID`: [Client ID](https://help.myanimelist.net/hc/en-us/articles/900003108823-API) for MyAnimeList integration (/mal, /anime, /manga).
    * `RAPID_API_KEY`: [Rapid API key](https://it-tools.tech/token-generator) for UrbanDictionary integration (/urban).
    * `MERRIAM_API_KEY`: [Intermedia Dictionary-capable](https://dictionaryapi.com/register/index) API key For dictionary integration (/define).
   
    #### Optional app and logging config

    * `EXTERNAL_LOGGING_ENABLED`: Default is `true`. Set to `true` to enable external logging, has no effect if neither `LOGTAIL_TOKEN` nor `LOGGING_CHANNEL_WEBHOOK_URL` is set.
    * `DEBUG_ENABLED`: Default is `false`. Set to `true` to enable debug logging, by default only to console and log files.
    * `DEBUG_EXTERNALLY`: Default is `false`. Set to `true` to send debug logs to LOGTAIL (very spammy). Only has effect if DEBUG_ENABLED is also `true`.
    * `SQL_ECHO`: Default is `false`. Set to `true` to log all SQL queries to console (also spammy but doesn't log externally).
    * `SYNC_COMMANDS_ON_STARTUP`: Default is `true`. Set to `true` to sync Discord slash commands on startup, otherwise you will need to use the owner command or API to sync.
    * `SYNC_EMOJIS_ON_STARTUP`: Default is `true`. Set to `true` to sync custom emojis on startup, otherwise you will need to use the API to sync. Either way, emojis must be synced at least once before the bot is usable.
    * `ENABLE_API_SERVICE`: Default is `true`. Set to `true` to enable the internal management API service.
    * `OWNER_COMMAND_PREFIX`: Default is `..`. Prefix for owner-only commands.
    * `CHUNK_GUILDS_SETTING`: Default is `LAZY`. Can be one of
      1. `AT_STARTUP`: Chunk all guild members at startup (delays bot startup by one minute per 100 guilds).
      2. `LAZY`: Chunk members over time after starting (recommended).
      3. `ON_DEMAND`: Only chunk members per guild when needed (e.g. certain commands).

    </details>
5. Run `main.py`. On first run, the bot will automatically set up the database tables and upload its custom emojis. This might take a minute or two.

---

## Configuration & extensions

You can clone or fork this repo to configure and extend the bot as you see fit. Here I'll explain the easier configurable parts.

### Radio stations

Your entry point here is [the radio streams json file](assets/data/radio_streams.json). There isn't currently any JSON schema file to validate against, but you can deduce the structure by looking at the existing entries.

### Event extensions

Any extensions placed within the `extensions` directory will be automatically loaded on bot startup. You can create your own extensions by inheriting from any of the base classes in the [templates directory](extensions/templates). See [here](extensions/extensions.md) for a quick guide to extensions.

If you decide to use the docker solution, you can load your extensions by mounting a volume to the `/app/extensions/my_extensions` directory in the container. Example:

```yaml
services:
  ohana:
    #...
    volumes:
      - /home/user/my_ohana_extensions:/app/extensions/my_extensions:ro
```

Adjust the host path (`/home/user/my_ohana_extensions`) as necessary.

### Owner Commands

Add your owners commands to [this file](system/owner_commands.py) with a simple if statement and a method to handle the command. Use existing commands as reference.

### Management API

Create a new API by inheriting the APIView class and registering it in the API service [module](api/api_service.py). See [this API](api/views/v1/commands_view.py) as an example.

---

## Commands

See a full list of slash commands [here](https://www.ohanabot.xyz/commands) (fun fact: this uses the `/api/v1/commands` API to pull the latest set of commands).

---

## Owner commands and APIs

### Owner commands

The following commands can be used by the bot owner, based on the `BOT_OWNER_ID` env var. The prefix can be changed using the `OWNER_COMMAND_PREFIX` env var. The following list assumes the default prefix of `..`.

* `..help` - Get a list of all owner commands.
* `..stats` - Get bot statistics.
* `..ping` - Check bot latency.
* `..sync slashes` - Sync slash commands.
* `..guild leave <guild_id>` - Make the bot leave a guild by its ID.
* `..guild info <guild_id>` - Get information about a guild by its ID.
* `..music streams reload` - Reload radio streams from the JSON file.
* `..extensions reload` - Reload all extensions.

### Management API

The bot also has an internal management API that can be enabled or disabled using the `ENABLE_API_SERVICE` env var. The API runs on port 8000 by default and requires an `API_AUTH_TOKEN` env var to be set for authentication.

More endpoints will be added over time.

* `GET /api/v1/healthcheck` - Basic healthcheck endpoint.
* `POST /api/v1/commands/sync` - Sync slash commands. Takes an optional JSON body with a `guild_id` field to sync commands to a specific guild only.
* `POST /api/v1/emojis/sync` - Sync custom emojis from the assets directory into Discord, and refetch emojis into the cache.
* `POST /api/v1/invalidate_guild_cache` - Invalidate the guild cache if available, forcing a refetch of guild settings and XP data from the database. Takes an optional `guild_id` field in the JSON body to invalidate a specific guild only.
---

## Contributing

Feel free to open issues or PRs if you find any bugs or want to suggest new features (or radio stations). If you want to contribute code, please make sure to follow the existing code style and add type hints and docstrings where necessary. See [To-do](#to-do) for some ideas on what to work on.

---

## To-do

- [ ] Move all the remaining string literals to the `strings` directory.
- [ ] Add more radio streams, diversify the genre list. Add more static images per stream.
- [ ] Add more management API endpoints.
- [ ] User auth for MyAnimeList and AniList.

---

## License

This project is licensed under the [MIT License](LICENSE).
