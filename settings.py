"""
Name of your bot
"""
BOT_NAME = "Ohana"

"""
Default prefixes for your bot. Change as you deem necessary but make sure each one is unique from the other.
"""
DEFAULT_PREFIX = "."
DEFAULT_MUSIC_PREFIX = "-"
DEFAULT_ADMIN_PREFIX = "="

"""
Replace this with your discord ID
"""
BOT_OWNER_ID = 218515152327278603

"""
Replace this with the channel ID where you want your bot to send its logs (info, errors, warnings etc..)
(make sure your bot can send messages and embed links in that channel) 
"""
DISCORD_LOGGING_CHANNEL_ID = 877525128194428929

"""
Replace this with your timezone from https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
This is used for showing logs in your timezone in case you're running your bot from a remote server.
"""
MY_TIMEZONE = 'Asia/Jerusalem'

"""
Replace this with the invite link for your bot. This can be obtained from https://discord.com/developers/applications
Go to the link above > Choose your bot > OAuth2 > URL Generator >
 Scopes: "bot" and "applications.commands" > Select permissions your bot needs > Copy link and paste below.
 You can just choose Administrator permission if you're not sure which permissions you bot might need.
"""
BOT_INVITE = "https://discord.com/api/oauth2/authorize?client_id=867836138689396826&permissions=8&scope=bot%20applications.commands"

"""
Image to use in help embeds. Leave string empty if you dont want one.
"""
HELP_EMBED_THUMBNAIL = "https://cdn.discordapp.com/attachments/345970006967844864/779776654444068894/ezgif-7-2ab56dfb17d41.gif"

"""
Bot color. This color is used in a lot of embeds, so try to pick something that goes well with the avatar of your bot.
"""
BOT_COLOR = 0xDEC5A7

"""
XP Default settings
"""
DEFAULT_LEVELUP_MESSAGE = "{member_mention} You have levelled up! You are now level {level}."
DEFAULT_LEVEL_ROLE_EARN_MESSAGE = "You now have the **{role_name}** role."
DEFAULT_TIMEFRAME_FOR_XP = 60
DEFAULT_MIN_XP_GIVEN = 20
DEFAULT_MAX_XP_GIVEN = 40
DEFAULT_XP_DECAY_PERCENTAGE = 1.0
DEFAULT_XP_DECAY_DAYS = 7  # aka grace period

"""
Music settings
"""
DEFAULT_PLAYER_CHANNEL_EMBED_MESSAGE_CONTENT = "Send a URL or type a song name below to queue something."
PLAYER_HEADER_IMAGE = "https://cdn.discordapp.com/attachments/794891724345442316/917935019681513552/player_header.png"
PLAYER_IDLE_IMAGE = "https://cdn.discordapp.com/attachments/794891724345442316/916657976641720360/player_idle.gif"

"""
Music Player control emojis as seen in player channels.
You can leave them empty if you want your bot to use default emojis, otherwise replace the values with emoji IDs that 
 your bot can see; that is: make sure your bot is in the server where these emojis are uploaded to.
Each control must have a unique emoji from the other controls (e.g. join can't have the same emoji as resume/pause etc.)
"""
PLAYER_JOIN_EMOJI_ID = 916704053642293298
PLAYER_RESUME_PAUSE_EMOJI_ID = 916704131287248936
PLAYER_REFRESH_EMOJI_ID = 916704131455025205
PLAYER_LEAVE_EMOJI_ID = 916704130544857108
PLAYER_SKIP_EMOJI_ID = 916704132478431282
PLAYER_SHUFFLE_EMOJI_ID = 916704132230946836
PLAYER_LOOP_EMOJI_ID = 916704130800713738
PLAYER_FAVORITE_EMOJI_ID = 916704130263830598
PLAYER_PREVIOUS_EMOJI_ID = 916704131463401492
PLAYER_NEXT_EMOJI_ID = 916704131023011880

"""
Rate-limiting settings below are important to make sure your bot isn't abused by requesting 
 too many commands/auto-responses within a short period of time. You can leave them as is if you're not sure.

AR_LIMIT_SECONDS: cooldown for auto-response. Setting below means a user can trigger one auto-response every 1 second.
COMMAND_LIMIT_X_SECONDS is the timespan in which COMMAND_LIMIT_PER_X_SECONDS are allowed.
Settings below mean that someone is allowed to use only 3 commands each 10 seconds
"""
AR_LIMIT_SECONDS = 1
COMMAND_LIMIT_X_SECONDS = 10
COMMAND_LIMIT_PER_X_SECONDS = 3

"""
Following settings are self-explanatory. If you don't understand what they do then you should probably leave them as is.
"""
CACHE_CLEANUP_FREQUENCY_SECONDS = 60
GUILDS_XP_SYNC_FREQUENCY_SECONDS = 45
