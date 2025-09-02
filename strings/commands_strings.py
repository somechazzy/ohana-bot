class GeneralCommandsStrings:
    """
    Strings used across multiple command handlers
    """
    SERVER_ONLY_COMMAND_ERROR_MESSAGE = "This command can only be used in a server."
    COMMAND_PERMISSIONS_BASE_ERROR_MESSAGE = "Please ensure that:"
    COMMAND_PERMISSIONS_USER_ERROR_MESSAGE = "You have the following permissions:"
    COMMAND_PERMISSIONS_BOT_ERROR_MESSAGE = "I have the following permissions:"
    GENERIC_PERMISSIONS_ERROR_MESSAGE = ("It seems I am missing some permissions to run this command. "
                                         "Please check my role permissions & role hierarchy in "
                                         "the server settings and try again.")

    AVATAR_NOT_FOUND = "No avatar found..."
    AVATAR_TITLE = "{username}'s avatar"

    BANNER_NOT_FOUND = "No banner found..."
    BANNER_TITLE = "{username}'s banner"

    EMOJIS_NOT_FOUND = "No emojis found..."
    EMOJIS_TITLE = "Emojis in message"

    STICKER_NOT_FOUND = "No sticker found..."
    STICKER_TITLE = "Sticker in message"

    GUILD_ONLY_ERROR = "This command can only be used in a server I'm in."

    INVALID_DURATION_ERROR_MESSAGE = ("Invalid duration format. Valid examples:\n"
                                      "• **1d12h** means 1 day and 12 hours\n"
                                      "• **1h30m** means 1 hour and 30 minutes\n"
                                      "• **3d4h15m** means 3 days, 4 hours and 15 minutes")


class ContextCommandsStrings(GeneralCommandsStrings):
    """
    Strings for context menu commands
    """
    REMIND_ME = "Remind me about this.."
    AVATAR = "Get avatar link"
    BANNER = "Get banner link"
    LEVEL = "Get member level/rank"
    EMOJI = "Get emoji link(s)"
    STICKER = "Get sticker link"


class UserSlashCommandsStrings(GeneralCommandsStrings):
    """
    Strings for user slash commands
    """
    # Commands descriptions
    LINK_MYANIMELIST_DESCRIPTION = "Link your MyAnimeList username for stats & profile"
    LINK_ANILIST_DESCRIPTION = "Link your Anilist username for stats & profile"
    MYANIMELIST_DESCRIPTION = "Get your MyAnimeList profile or someone else's"
    ANILIST_DESCRIPTION = "Get your Anilist profile or someone else's"
    ANIME_DESCRIPTION = "Get anime info with your stats"
    MANGA_DESCRIPTION = "Get manga info with your stats"

    USER_SETTINGS_DESCRIPTION = "View or change your settings"
    FEEDBACK_DESCRIPTION = "Send feedback, report bugs or suggest features"
    HELP_DESCRIPTION = "Show the help menu"
    MUSIC_FIX_DESCRIPTION = "Fix Ohana player/radio by force resetting everything."

    MUTE_DESCRIPTION = "Mute a member"
    UNMUTE_DESCRIPTION = "Unmute a member"
    KICK_DESCRIPTION = "Kick a member"
    BAN_DESCRIPTION = "Ban a member"
    UNBAN_DESCRIPTION = "Unban a member"

    REMIND_ME_DESCRIPTION = "Remind me of something at a specific time"
    REMIND_SOMEONE_DESCRIPTION = "Remind someone of something at a specific time"
    REMIND_LIST_DESCRIPTION = "List & manage all of your reminders"

    STICKER_DESCRIPTION = "Get link to a sticker"
    AVATAR_DESCRIPTION = "Get link to your or someone else's avatar"
    BANNER_DESCRIPTION = "Get link to your or someone else's banner"
    SERVER_INFO_DESCRIPTION = "Get info about the server"
    USER_INFO_DESCRIPTION = "Get information about yourself or someone else"
    URBAN_DESCRIPTION = "Get a definition from Urban Dictionary"
    DEFINE_DESCRIPTION = "Get a definition from Merriam-Webster Dictionary"
    FLIP_DESCRIPTION = "Flip a coin"

    LEVEL_DESCRIPTION = "Get your current level and rank - or someone else's"
    LEADERBOARD_DESCRIPTION = "Get the server XP leaderboard"
    LEVEL_ROLES_DESCRIPTION = "Show what level roles the server offers"

    # General commands
    FEEDBACK_REPLY = ("Thank you for the feedback 💞. If this is a bug report or a suggestion, "
                      "we might send you a message once we fix or implement it.")

    # Moderation Commands
    MUTE_DURATION_INVALID_ERROR_MESSAGE = "Maximum mute duration must be less than 28 days."
    MUTE_SUCCESS_FEEDBACK = "{member} has been muted for {duration}."
    UNMUTE_NON_MUTED_ERROR_MESSAGE = "{member} is not muted."
    UNMUTE_SUCCESS_FEEDBACK = "{member} has been unmuted."
    KICK_SUCCESS_FEEDBACK = "{member} has been kicked."
    BAN_DELETE_DURATION_INVALID_ERROR_MESSAGE = "Delete duration must be between 0 and 24 hours."
    BAN_SUCCESS_FEEDBACK = "{member} has been banned."
    UNBAN_SUCCESS_FEEDBACK = "User {user} ({user_id}) has been unbanned."

    # Reminder Commands
    REMIND_EXCEEDS_MAX_ERROR_MESSAGE = "Maximum reminder time is 1 year."
    GENERIC_REMINDER_CREATION_ERROR_MESSAGE = ("😔 Failed at setting up your reminder. "
                                               "We're already looking into it.")
    REMIND_OTHER_SUCCESS_FEEDBACK = ("Okie. I'll remind {member_name} ({member_mention}) "
                                     "about that in {duration} ({timestamp}).")

    # Utility Commands
    STICKER_INVALID_MESSAGE_ID_ERROR_MESSAGE = "Invalid message ID"
    STICKER_MESSAGE_NOT_FOUND_ERROR_MESSAGE = "Message not found"
    STICKER_CONTEXT_MENU_COMMAND_UPSELL = "You can also right click the message -> Apps -> Get sticker link"
    AVATAR_CONTEXT_MENU_COMMAND_UPSELL = "You can right click the user -> Apps -> Get avatar link"
    BANNER_CONTEXT_MENU_COMMAND_UPSELL = "You can right click the user -> Apps -> Get banner link"
    USER_INFO_USER_NOT_FOUND_ERROR_MESSAGE = "Please select someone in the server."
    FLIP_FLIPPING = "Flipping {loading_emoji}..."
    FLIP_FLIPPED_RESULT = "Flipped **{result}** {emoji}"
    FLIP_HEADS = "Heads"
    FLIP_TAILS = "Tails"

    # XP commands
    LEVEL_USER_NOT_FOUND_ERROR_MESSAGE = "Member not found in this server."


class AdminSlashCommandsStrings(GeneralCommandsStrings):
    """
    Strings for admin slash commands
    """
    # Commands descriptions
    ROLE_PERSISTENCE_DESCRIPTION = "Automatically reassign roles to members who leave and rejoin"
    AUTOROLES_DESCRIPTION = "Manage autoroles for this server"
    AUTO_RESPONSES_DESCRIPTION = "Manage auto-responses for this server"
    GALLERY_CHANNELS_DESCRIPTION = "Manage gallery channels for this server"
    LIMITED_MESSAGES_CHANNELS_DESCRIPTION = "Manage limited-messages channels for this server"

    LOGGING_CHANNEL_DESCRIPTION = "Set/unset the logging channel for this server"
    GENERAL_SETTINGS_DESCRIPTION = "View a summary and manage all the settings for this server"

    MUSIC_CREATE_CHANNEL_DESCRIPTION = "Create the #ohana-player channel."

    ROLE_MENU_CREATE_DESCRIPTION = "Create a new role menu"
    ROLE_MENU_EDIT_DESCRIPTION = "Edit an existing role menu (also use to refresh roles)"

    XP_GROUP_DESCRIPTION = "XP and levels system settings"
    XP_SETTINGS_DESCRIPTION = "Manage XP and levels settings for this server"
    XP_TRANSFER_DESCRIPTION = "Award, remove, or transfer XP from/to users"

    # Automod commands
    ROLE_PERSISTENCE_TITLE = "Role persistence"
    ROLE_PERSISTENCE_ALREADY_SET_ERROR_MESSAGE = "Role persistence is already {state}."
    ROLE_PERSISTENCE_SET_SUCCESS_MESSAGE = "Role persistence is now **{state}**."

    # Music commands
    MUSIC_CREATE_CHANNEL_ALREADY_EXISTS_ERROR_MESSAGE = "The music channel already exists: {channel_mention}"
    MUSIC_CREATE_CHANNEL_NO_MANAGE_CHANNELS_PERMISSION_ERROR_MESSAGE = ("I need the **Manage Channels** "
                                                                        "permission to create the music channel.")
    MUSIC_CREATE_CHANNEL_STARTING_MESSAGE = "Creating Ohana Player channel..."
    MUSIC_CREATE_CHANNEL_CHANNEL_DESCRIPTION = ("Ohana Player. If the player is stuck or the player message is missing,"
                                                " you can use /music-fix")
    MUSIC_CREATE_CHANNEL_SUCCESS_MESSAGE = ("Created Ohana Player channel: {channel_mention}\n"
                                            "Feel free to move the channel and to rename it.")

    # Role menu commands
    ROLE_MENU_CREATE_PERMISSION_ERROR_MESSAGE = ("I need the permission to **send messages**, "
                                                 "**embed links** and **read message history** in this channel.")
    ROLE_MENU_EDIT_INVALID_MESSAGE_ID_ERROR_MESSAGE = "Invalid message ID"
    ROLE_MENU_EDIT_PERMISSION_ERROR_MESSAGE = "I don't have permission to access that message"
    ROLE_MENU_EDIT_MESSAGE_NOT_FOUND_ERROR_MESSAGE = "Message not found"
