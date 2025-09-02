import discord

from constants import Colour
from models.dto.cachables import CachedGuildSettings


def get_logging_channel_setup_embed(logging_channel_id: int, guild: discord.Guild, feedback_message: str | None = None):
    """
    Creates an embed for setting up the logging channel.
    Args:
        logging_channel_id (int): The ID of the current logging channel, or None if not set.
        guild (discord.Guild): The guild where the logging channel is being set up.
        feedback_message (str | None): Optional feedback message to include in the embed.
    Returns:
        discord.Embed: The embed object for logging channel setup.
    """
    embed = discord.Embed(
        title="Logging Channel Setup",
        description="Select a channel to be used for logging Ohana related events.",
        color=Colour.PRIMARY_ACCENT
    )

    if logging_channel_id:
        channel = guild.get_channel(logging_channel_id)
        embed.add_field(name="Current Logging Channel", value=channel.mention, inline=False)
    else:
        embed.add_field(name="Current Logging Channel", value="None", inline=False)

    if feedback_message:
        embed.add_field(name="Feedback", value=feedback_message, inline=False)

    return embed


def get_guild_settings_embed(guild: discord.Guild, guild_settings: CachedGuildSettings) -> discord.Embed:
    """
    Creates an embed displaying and overview of the current guild settings.
    Args:
        guild (discord.Guild): The guild for which the settings are being displayed.
        guild_settings (CachedGuildSettings): The current settings of the guild.
    Returns:
        discord.Embed: The embed object containing the guild settings overview.
    """
    embed = discord.Embed(colour=Colour.INFO,
                          description=f"Server settings overview. "
                                      f"These settings can be changed using admin `/manage ...` commands.")

    embed.set_author(name=f"{guild.name} - Settings Overview",
                     icon_url=guild.icon.with_size(128).url if guild.icon else None)
    embed.set_footer(text=f"Ohana Settings", icon_url=guild.me.display_avatar.with_size(128).url)

    embed.add_field(name="Logging Channel",
                    value=(f"{f'<#{guild_settings.logging_channel_id}>' 
                           if guild_settings.logging_channel_id else 'Not set.'}\n") +
                    f"⚙ **Change logging channel** using `/manage logging-channel`\n",
                    inline=False)
    embed.add_field(name="XP Settings",
                    value=f"XP Gain {'Enabled' if guild_settings.xp_settings.xp_gain_enabled else 'Disabled'}\n" +
                          f"⚙ **To manage XP settings**: use `/manage xp settings`.",
                    inline=False)
    embed.add_field(name="Autoroles",
                    value=(f"{' • '.join([f'<@&{role_id}>' for role_id in guild_settings.autoroles_ids]) 
                           if guild_settings.autoroles_ids else 'No autoroles set.'}\n") +
                    f"⚙ **To manage autoroles**: use `/manage autoroles`.",
                    inline=False)
    embed.add_field(name="Auto-responses",
                    value=f"You have **{len(guild_settings.auto_responses)}** auto-responses set.\n" +
                    f"⚙ **To manage auto-responses**: use `/manage auto-responses`.",
                    inline=False)
    embed.add_field(name="Channel Settings",
                    value=f"You have {sum(guild_settings.channel_id_is_gallery_channel.values())} "
                          f"gallery channels.\n"
                          f"You have {sum(guild_settings.channel_id_message_limiting_role_id.values())} "
                          f"limited-messages channels.\n" +
                    f"⚙ **To manage Gallery channels settings**: "
                    f"use `/manage gallery-channels settings`.\n"
                    f"⚙ **To manage Limited Message channels settings**: "
                    f"use `/manage limited-messages-channels settings`.",
                    inline=False)
    embed.add_field(name="Role Menus",
                    value=f"You have **{len(guild_settings.role_menus)}** role menus.",
                    inline=False)
    music_channel = guild.get_channel(guild_settings.music_channel_id) if guild_settings.music_channel_id else None
    embed.add_field(name="Music Channel",
                    value=f"{f'<#{guild_settings.music_channel_id}>' if music_channel else 'Not created.'}\n" +
                    (f"⚙ **To create the Music Channel**: use `/manage music-create-channel`."
                     if not music_channel else ""),
                    inline=False)

    return embed
