import discord

from clients import discord_client, emojis
from constants import Colour, AnimangaProvider, DiscordTimestamp, Links, UserUsernameProvider


def get_user_settings_embed(timezone: str | None,
                            preferred_animanga_provider: str,
                            relayed_reminders_disabled: bool,
                            usernames_map: dict[str, str],
                            user: discord.User,
                            feedback: str | None = None) -> discord.Embed:
    """
    Embed for displaying user settings.
    Args:
        timezone (str | None): The user's timezone.
        preferred_animanga_provider (str): The user's preferred anime/manga provider.
        relayed_reminders_disabled (bool): Whether the user has disabled relayed reminders.
        usernames_map (dict[str, str]): A map of the user's linked usernames, provider -> username.
        user (discord.User): The user whose settings are being displayed.
        feedback (str | None): Optional feedback message to include in the embed.
    Returns:
        discord.Embed: The embed containing the user's settings.
    """
    embed = discord.Embed(
        colour=Colour.PRIMARY_ACCENT,
        title=f"{user.name}",
        description=f"Settings related to you.\n"
                    f"In order to set your timezone, go to [this link]({Links.APPS_TIMEZONE})"
                    f" and click copy before clicking "
                    f"on the button below.\n‎"
    )

    embed.set_thumbnail(url=user.display_avatar.with_size(128).url)

    embed.set_author(name="User settings",
                     icon_url=discord_client.user.display_avatar.with_size(32).url)

    embed.add_field(name="Timezone", value=f"{emojis.general.clock} {timezone or 'Not set'}", inline=False)

    embed.add_field(name="Preferred Anime/Manga Provider",
                    value=f"{emojis.logos.mal} MyAnimeList" if preferred_animanga_provider == AnimangaProvider.MAL
                    else f"{emojis.logos.anilist} AniList" if preferred_animanga_provider == AnimangaProvider.ANILIST
                    else "None",
                    inline=False)

    usernames_text = ""
    if UserUsernameProvider.MAL in usernames_map:
        usernames_text += (f"{emojis.logos.mal} MyAnimeList: `{usernames_map[UserUsernameProvider.MAL]}`"
                           f" (change or unset using `/link-myanimelist`)\n")
    else:
        usernames_text += (f"{emojis.logos.mal} MyAnimeList: not linked yet."
                           f" Link using `/link-myanimelist`.\n")
    if UserUsernameProvider.ANILIST in usernames_map:
        usernames_text += (f"{emojis.logos.anilist} AniList: `{usernames_map[UserUsernameProvider.ANILIST]}`"
                           f" (change or unset using `/link-anilist`)\n")
    else:
        usernames_text += (f"{emojis.logos.anilist} AniList: not linked yet."
                           f" Link using `/link-anilist`.\n")

    embed.add_field(name="Linked Usernames", value=usernames_text, inline=False)

    embed.add_field(name="Allow other users to relay you reminders",
                    value="No" if relayed_reminders_disabled else "Yes",
                    inline=False)

    if feedback:
        embed.add_field(name="Info",
                        value=feedback,
                        inline=False)

    return embed


def get_utility_image_embed(image_url: str,
                            title: str,
                            context_menu_command_instructions: str | None = None) -> discord.Embed:
    """
    Embed for displaying an image within it. For commands such as `/avatar`, `/banner`, `/sticker`, etc.
    Args:
        image_url (str): The URL of the image to display.
        title (str): The title of the embed.
        context_menu_command_instructions (str | None): Optional instructions to include in the footer.
    Returns:
        discord.Embed: The embed containing the image.
    """
    embed = discord.Embed(
        colour=Colour.PRIMARY_ACCENT,
        title=title
    )

    embed.set_image(url=image_url)

    if context_menu_command_instructions:
        embed.set_footer(text=context_menu_command_instructions)

    return embed


def get_server_info_embed(guild: discord.Guild) -> discord.Embed:
    """
    Embed for displaying server information.
    Args:
        guild (discord.Guild): The guild whose information is being displayed.
    Returns:
        discord.Embed: The embed containing the server's information.
    """
    if not guild:
        return discord.Embed(colour=Colour.RED, description="What server")
    icon = guild.icon.with_size(128).url if guild.icon else None
    created_at_timestamp = int(guild.created_at.timestamp())

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=guild.description)
    embed.set_author(name=f"{guild.name}", icon_url=icon)
    if icon:
        embed.set_thumbnail(url=icon)
    if guild.banner and guild.banner.url:
        embed.set_image(url=guild.banner.url)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
    embed.add_field(name="Creation time",
                    value=f"{DiscordTimestamp.LONG_DATE_TIME.format(timestamp=created_at_timestamp)} "
                          f"({DiscordTimestamp.RELATIVE_TIME.format(timestamp=created_at_timestamp)})",
                    inline=False)
    embed.add_field(name="Server in Numbers",
                    value=f"• Members: {guild.member_count}\n"
                          f"• Roles: {len(guild.roles) - 1}\n"
                          f"• Channel categories: {len(guild.categories)}\n"
                          f"• Text Channels: {len(guild.text_channels)}\n"
                          f"• Voice Channels: {len(guild.voice_channels)}\n"
                          f"• Stage Channels: {len(guild.stage_channels)}\n"
                          f"• Emojis: {len(guild.emojis)}\n"
                          f"• Stickers: {len(guild.stickers)}\n",
                    inline=False)
    embed.add_field(name="Boosts",
                    value=f"• Number of boosts: {guild.premium_subscription_count}\n"
                          f"• Boost level: {guild.premium_tier}",
                    inline=False)
    if guild.vanity_url:
        embed.add_field(name="Vanity URL",
                        value=guild.vanity_url,
                        inline=False)
    return embed


def get_member_info_embed(member: discord.Member, user: discord.User) -> discord.Embed:
    """
    Embed for displaying a server member's information.
    Args:
        member (discord.Member): The member whose information is being displayed.
        user (discord.User): The user object corresponding to the member.
    Returns:
        discord.Embed: The embed containing the member's information.
    """
    nick = member.nick
    role_count = len(member.roles) - 1

    created_at_timestamp = int(user.created_at.timestamp())
    joined_at_timestamp = int(member.joined_at.timestamp())
    booster_since_timestamp = int(member.premium_since.timestamp()) if member.premium_since else None
    description = f"{'`BOT` • ' if member.bot else ''} " + (f"`AKA` {nick}" if nick else "")
    roles_value = f"-" if role_count == 0 \
        else " ".join(role.mention for role in member.roles if role.name != "@everyone")

    embed = discord.Embed(colour=user.accent_color or Colour.PRIMARY_ACCENT,
                          description=description if description.strip() else None)

    avatar_url = user.display_avatar.with_size(128).url
    embed.set_thumbnail(url=avatar_url)
    embed.set_author(name=f"{member}", icon_url=avatar_url)

    if member.guild_banner:
        embed.set_image(url=member.banner.url)
    elif user.banner:
        embed.set_image(url=user.banner.url)

    embed.add_field(name="Account created",
                    value=f"{DiscordTimestamp.LONG_DATE_TIME.format(timestamp=created_at_timestamp)} "
                          f"({DiscordTimestamp.RELATIVE_TIME.format(timestamp=created_at_timestamp)})",
                    inline=False)
    embed.add_field(name="Member joined",
                    value=f"{DiscordTimestamp.LONG_DATE_TIME.format(timestamp=joined_at_timestamp)} "
                          f"({DiscordTimestamp.RELATIVE_TIME.format(timestamp=joined_at_timestamp)})",
                    inline=False)
    embed.add_field(name=f"Roles ({role_count} roles)", value=roles_value, inline=False)

    if booster_since_timestamp:
        embed.add_field(name="Boosting since",
                        value=f"{DiscordTimestamp.LONG_DATE_TIME.format(timestamp=booster_since_timestamp)} "
                              f"({DiscordTimestamp.RELATIVE_TIME.format(timestamp=booster_since_timestamp)})",
                        inline=False)

    return embed


def get_timezone_prompt_embed(first_time: bool = False) -> discord.Embed:
    """
    Embed for prompting the user to set their timezone.
    Args:
        first_time (bool): Whether this is the first time the user is setting their timezone.
    Returns:
        discord.Embed: The embed prompting the user to set their timezone.
    """
    embed = discord.Embed(
        title="Timezone Setup",
        description="Enter your timezone."
                    + (" This is a one-time thing required for setting recurring reminders." if first_time else ""),
        color=Colour.PRIMARY_ACCENT
    )

    embed.add_field(name="Instructions",
                    value=f"1. Go to {Links.APPS_TIMEZONE}\n"
                          "2. Click \"Copy Timezone Info\"\n"
                          "3. Click \"Set timezone\" button below\n"
                          "4. Paste the timezone",
                    inline=False)

    return embed
