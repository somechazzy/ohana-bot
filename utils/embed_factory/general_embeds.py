import datetime
import time

import discord
from discord.app_commands import Group
from globals_.clients import discord_client
from globals_.constants import BotLogLevel, MerriamDictionaryResponseType, SUPPORT_SERVER_INVITE, \
    Colour, HelpMenuType, HELP_EMBED_THUMBNAIL
from ..helpers import convert_minutes_to_time_string


def make_general_help_embed():
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description="I have listed my most popular commands below. "
                                      "Click on each section to see the full commands list.\n‎")
    embed.set_thumbnail(url=HELP_EMBED_THUMBNAIL)
    embed.set_author(name="Help")

    embed.add_field(name="User commands", value=f"• **/myanimelist** • **/anilist** • **/anime** • **/manga**\n"
                                                f"• **/level** • **/leaderboard**\n"
                                                f"• **/remind-me**\n‎",
                    inline=False)

    embed.add_field(name="Music commands",
                    value=f"Most of my music commands have been migrated to the new music player. "
                          f"If you don't have a music channel yet, use this to create it: **/music channel-create**\n‎",
                    inline=False)

    embed.add_field(name="Admin commands",
                    value=f"To configure my XP & Levels system, use **/manage xp settings**.\n"
                          f"You can also see an overview of all admin settings "
                          f"using this command **/manage settings-overview**.\n‎",
                    inline=False)

    embed.add_field(name="Join the support server", value=f"{SUPPORT_SERVER_INVITE}\n", inline=False)

    embed.set_footer(text="General Help Menu",
                     icon_url=discord_client.user.avatar.with_size(128).url)

    return embed


def make_help_embed_for_menu(menu_type):
    if menu_type == HelpMenuType.USER:
        from slashes.blueprint.user_blueprints import cog
    elif menu_type == HelpMenuType.ADMIN:
        from slashes.blueprint.admin_blueprints import cog
    elif menu_type == HelpMenuType.MUSIC:
        from slashes.blueprint.music_blueprints import cog
    else:
        raise Exception(f"Invalid menu type: {menu_type}")

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=f"Full list of {menu_type} commands.\n‎")
    embed.set_thumbnail(url=HELP_EMBED_THUMBNAIL)
    embed.set_author(name=f"My {menu_type} Commands")

    for command in list(cog.walk_app_commands()):
        if isinstance(cog, Group):
            continue
        if not command.extras.get('unlisted') and not command.extras.get('is_alias'):
            embed.add_field(name=f"{command.qualified_name}", value=f"{command.description}", inline=True)
        if len(embed.fields) == 25:
            break

    embed.set_footer(text="Note that some of these are server-only commands",
                     icon_url=discord_client.user.avatar.with_size(128).url)

    return embed


def make_log_embed(event, event_type, author_name, author_icon,
                   guild_avatar, color_hex, footer_text=None, fields=None, values=None):
    if values is None:
        values = []
    if fields is None:
        fields = []
    footer_text = event_type + ((" | " + footer_text) if footer_text is not None else "")
    embed = discord.Embed(colour=color_hex, description=f"{event}",
                          timestamp=datetime.datetime.utcfromtimestamp(int(time.time())))

    embed.set_author(name=f"{author_name}", icon_url=author_icon or None)
    embed.set_footer(text=f"{footer_text}", icon_url=guild_avatar or None)
    for i in range(0, len(fields)):
        if len(values) == i:
            break
        embed.add_field(name=f"{fields[i]}", value=f"{values[i]}", inline=False)

    return embed


def make_urban_embed(definition_dict: dict, index, total):
    term = definition_dict.get("word")
    permalink = definition_dict.get("permalink")
    thumbs_up = definition_dict.get("thumbs_up")
    thumbs_down = definition_dict.get("thumbs_down")
    author = definition_dict.get("author")
    definition = definition_dict.get("definition")
    example = definition_dict.get("example")

    embed = discord.Embed(colour=Colour.EXT_URBAN, description=f"{definition}")

    embed.set_author(name=f"{term}", url=f"{permalink}",
                     icon_url="https://is4-ssl.mzstatic.com/image/thumb/Purple111/"
                              "v4/7e/49/85/7e498571-a905-d7dc-26c5-33dcc0dc04a8/source/512x512bb.jpg")
    embed.set_footer(text=f"Definition by {author} | Page {index}/{total}")

    if example:
        embed.add_field(name="Example", value=f"{example}\n", inline=False)
    embed.add_field(name="‎‎‎", value=f"{thumbs_up} 👍 | 👎 {thumbs_down}", inline=False)

    return embed


def make_merriam_embed(term, data, response_type):
    url = f"https://www.merriam-webster.com/dictionary/{term}"
    embed = discord.Embed(colour=Colour.EXT_MERRIAM)
    embed.set_author(name=f"{term}", url=f"{url.replace(' ', '%20')}",
                     icon_url="https://merriam-webster.com/assets/mw/static/social-media-share/mw-logo-245x245@1x.png")

    if response_type == MerriamDictionaryResponseType.SUCCESS and data:
        data = data[:3]
        for entry in data:
            embed.add_field(name=entry['pos'], value='.\n'.join(entry['definitions'][:3]) + '.\n', inline=False)
    elif response_type == MerriamDictionaryResponseType.NOT_FOUND:
        embed.description = "Couldn't find a definition for the provided term. See suggestions below."
        embed.add_field(name="Suggested", value=', '.join(data[0]['suggestions']) + '\n', inline=False)
    elif len(data) == 0:
        embed.description = "No definitions found."
    else:
        embed.description = data[0]['error'] + f"\nTry checking the definition through [this link]({url})."

    return embed


def make_bot_log_embed(message, level, extras=None):
    bot_avatar = discord_client.user.avatar.with_size(128).url if discord_client.user.avatar else None
    if level == BotLogLevel.ERROR:
        color_hex = Colour.RED
    elif level in [BotLogLevel.WARNING, BotLogLevel.MINOR_WARNING, BotLogLevel.GUILD_LEAVE]:
        color_hex = Colour.HOT_ORANGE
    elif level in [BotLogLevel.RECEIVED_DM, BotLogLevel.GUILD_JOIN]:
        color_hex = Colour.GREEN
    else:
        color_hex = Colour.PRIMARY_ACCENT

    embed = discord.Embed(colour=color_hex, description=f"{message}",
                          timestamp=datetime.datetime.utcfromtimestamp(int(time.time())))

    embed.set_author(name=level)
    embed.set_footer(text="", icon_url=bot_avatar)
    if extras:
        for field_name, value in extras.items():
            embed.add_field(name=f"{field_name}",
                            value=f"{value}",
                            inline=False)
    return embed


def make_server_info_embed(guild: discord.Guild):
    if not guild:
        return discord.Embed(colour=Colour.RED, description="What server")
    name = guild.name
    icon = guild.icon.with_size(128).url if guild.icon else None
    banner = guild.banner.url if guild.banner else None
    owner = guild.owner
    category_count = len(guild.categories)
    text_channel_count = len(guild.text_channels)
    voice_channel_count = len(guild.voice_channels)
    stage_channel_count = len(guild.stage_channels)
    created_at = guild.created_at
    description = guild.description if guild.description else None
    emoji_count = len(guild.emojis)
    sticker_count = len(guild.stickers)
    member_count = guild.member_count
    booster_count = guild.premium_subscription_count
    boost_level = guild.premium_tier
    role_count = len(guild.roles) - 1

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT,
                          description=description if description else None)
    embed.set_author(name=f"{name}", icon_url=icon if icon else None)
    if icon:
        embed.set_thumbnail(url=icon)
    if banner:
        embed.set_image(url=banner)
    embed.add_field(name="Owner", value=owner.mention, inline=False)
    embed.add_field(name="Creation time", value=f"<t:{int(created_at.timestamp())}:F>", inline=False)
    embed.add_field(name="Server in Numbers",
                    value=f"• Members: {member_count}\n"
                          + (f"• Roles: {role_count}\n" if role_count else "")
                          + (f"• Categories: {category_count}\n" if category_count else "")
                          + (f"• Text Channels: {text_channel_count}\n" if text_channel_count else "")
                          + (f"• Voice Channels: {voice_channel_count}\n" if voice_channel_count else "")
                          + (f"• Stage Channels: {stage_channel_count}\n" if stage_channel_count else "")
                          + (f"• Emojis: {emoji_count}\n" if emoji_count else "")
                          + (f"• Stickers: {sticker_count}\n" if sticker_count else ""),
                    inline=False)
    embed.add_field(name="Boosts",
                    value=f"• Number of boosts: {booster_count}\n"
                          f"• Boost level: {boost_level}",
                    inline=False)
    return embed


def make_member_info_embed(member: discord.Member, user: discord.User):
    name = str(member)
    nick = member.nick
    avatar_asset = member.guild_avatar if member.guild_avatar else member.avatar
    avatar = avatar_asset.with_size(256).url if avatar_asset else None
    banner = user.banner.url if user.banner else None
    color = user.accent_color
    is_bot = member.bot
    created_at = member.created_at
    joined_at = member.joined_at
    booster_since = member.premium_since
    role_count = len(member.roles) - 1

    description = f"{'`BOT` • ' if is_bot else ''} " + (f"`AKA` {nick}" if nick else "")
    roles_value = f"-" if role_count == 0 \
        else " ".join(role.mention for role in member.roles if role.name != "@everyone")
    embed = discord.Embed(colour=color or Colour.PRIMARY_ACCENT,
                          description=description if description.strip() else None)
    embed.set_author(name=f"{name}", icon_url=avatar if avatar else None)
    if avatar:
        embed.set_thumbnail(url=avatar)
    if banner:
        embed.set_image(url=banner)
    embed.add_field(name="Account created", value=f"<t:{int(created_at.timestamp())}:F>", inline=False)
    embed.add_field(name="Member joined", value=f"<t:{int(joined_at.timestamp())}:F>", inline=False)
    embed.add_field(name=f"Roles ({role_count} roles)", value=roles_value, inline=False)
    if booster_since:
        embed.add_field(name="Boosting since",
                        value=f"<t:{int(booster_since.timestamp())}:F>",
                        inline=False)
    return embed


def make_snipe_embed(sniped_message, member):
    author_icon = member.avatar.with_size(128).url if member.avatar else None
    author_name = str(member)
    message_content = sniped_message.get('content')
    message_timestamp = sniped_message.get('created_at')
    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT, description=message_content, timestamp=message_timestamp)
    embed.set_author(name=author_name, icon_url=author_icon or None)
    return embed


def make_welcoming_embed(guild: discord.Guild):
    description = f"Thank you for adding me to {guild.name}! I'll be at your service. " \
                  f"I have a lot to offer but here are my **top features**:\n‎\n"

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT, description=description)
    embed.set_author(name="Getting Started", icon_url=guild.me.avatar.with_size(64).url)
    embed.set_thumbnail(url=guild.icon.with_size(256).url if guild.icon else None)
    embed.set_footer(text="If you need help, you can join the support server using /support")

    embed.add_field(name="Music",
                    value="This is probably why you added me in the first place. "
                          "Get started by using `/music channel-create`.\n"
                          "Besides the controls in the player channel, type `/music` to see all the commands.\n‎",
                    inline=False)

    embed.add_field(name="XP & Levels system",
                    value="I have a unique and powerful XP & Levels system which "
                          "you (as an admin) can view and customize using `/manage xp overview`.\n"
                          "I also have many auto-moderation features which you can explore using"
                          " `/manage settings-overview`\n‎",
                    inline=False)

    embed.add_field(name="Anime/Manga",
                    value="I was originally made for this purpose.\n"
                          "You can link your MyAnimeList (`/link-myanimelist`) "
                          "and Anilist (`/link-anilist`) accounts for a start.\n"
                          "You can also view anime and manga information using `/anime` and `/manga`.\n‎",
                    inline=False)

    embed.add_field(name="Utility",
                    value="I have a lot of utility commands to offer.\n"
                          "Have a look for yourself by sending `/help`.\n‎",
                    inline=False)

    return embed


def quick_embed(text, bold=False, color=Colour.PRIMARY_ACCENT, thumbnail_url=None, fields_values=None, emoji='💬',
                title=None, fields_values_inline=True, footer=None):
    asterisks = '**' if bold else ''
    if emoji is None:
        description = f"{asterisks}{text}{asterisks}"
    else:
        description = f"{emoji}  {asterisks}{text}{asterisks}‎‎‎"
    embed = discord.Embed(colour=color,
                          description=description)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if fields_values:
        for field, value in fields_values.items():
            embed.add_field(name=field, value=value, inline=fields_values_inline)
    if title:
        embed.set_author(name=title)
    if footer:
        embed.set_footer(text=footer)
    return embed


def make_reminder_embed(reason, minutes_late):
    title = "⏱ Reminder" if minutes_late < 5 else f"⏱ Belated Reminder"

    embed = discord.Embed(colour=Colour.PRIMARY_ACCENT, title=title,
                          description=f"{reason}")

    if minutes_late > 5:
        embed.set_footer(text=f"Sorry! I was offline {convert_minutes_to_time_string(minutes=minutes_late)}"
                              f" ago so I missed the reminder.")

    return embed
