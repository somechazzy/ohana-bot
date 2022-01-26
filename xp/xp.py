import random
import time
import disnake as discord

from actions import send_message, edit_roles
from globals_.constants import XPSettingsKey as XPKeys, MessageCountMode
from models.guild import GuildPrefs
from globals_ import variables
from models.member import MemberXP
from models.guild import GuildXP


async def handle_xp(message: discord.Message, guilds_prefs: GuildPrefs):
    """
    Handles XP for each message sent in any channel the bot can see, as long as they have XP gain enabled
    :param (discord.Message) message:
    :param (GuildPrefs) guilds_prefs:
    :return:
    """
    xp_settings = guilds_prefs.xp_settings
    member = message.author
    guild = message.guild

    if xp_settings[XPKeys.XP_GAIN_ENABLED]:

        initiate_guild_or_member_data_if_not_exist(guild=guild, member=member)

        current_time = int(time.time()) - time.altzone
        variables.guilds_xp[guild.id].members_xp[member.id].set_last_message_ts(current_time)

        if is_ignored_channel_or_role(message, xp_settings):
            return

        if xp_settings[XPKeys.MESSAGE_COUNT_MODE] is MessageCountMode.PER_MESSAGE:
            variables.guilds_xp[guild.id].members_xp[member.id].increment_messages()

        xp_updated = update_xp_and_timeframe(message, xp_settings)

        if xp_updated:
            if xp_settings[XPKeys.MESSAGE_COUNT_MODE] is MessageCountMode.PER_TIMEFRAME:
                variables.guilds_xp[guild.id].members_xp[member.id].increment_messages()
            level_updated = update_level(member)
            if level_updated:
                awarded_role = None
                if xp_settings[XPKeys.LEVEL_ROLES]:
                    awarded_role = await award_role(member, xp_settings)
                if xp_settings[XPKeys.LEVELUP_ENABLED]:
                    await send_levelup_message(message, xp_settings, awarded_role)

        variables.guilds_xp[guild.id].set_synced(False)


async def edit_member_xp(member, guilds_prefs: GuildPrefs, offset: int = 0, reset=False):
    if (offset and reset) or (not offset and not reset):
        raise Exception(f"Edit member XP must receive either offset or reset, not neither nor both. "
                        f"Offset=`{offset}` Reset=`{reset}`.")
    initiate_guild_or_member_data_if_not_exist(guild=member.guild, member=member)
    xp_settings = guilds_prefs.xp_settings
    existing_xp_amount = int(variables.guilds_xp[member.guild.id].members_xp[member.id].xp)
    if offset:
        if existing_xp_amount + offset < 0:
            offset = existing_xp_amount
        variables.guilds_xp[member.guild.id].members_xp[member.id].add_xp(offset)
    elif reset:
        variables.guilds_xp[member.guild.id].members_xp[member.id].set_xp(0)
    variables.guilds_xp[member.guild.id].members_xp[member.id].is_synced = False
    variables.guilds_xp[member.guild.id].set_synced(False)

    level_updated = update_level(member=member)
    if level_updated and xp_settings[XPKeys.LEVEL_ROLES]:
        await modify_member_level_roles(member=member,
                                        member_level=variables.guilds_xp[member.guild.id].members_xp[member.id].level,
                                        xp_settings=xp_settings,
                                        reason="Adjustment after member XP action")
    return existing_xp_amount


def edit_user_xp(user_id, guilds_prefs, offset: int = 0, reset=False):
    """
    Used for editing XP of a user who no longer exists in a guild
    """
    guild_id = guilds_prefs.guild_id
    if (offset and reset) or (not offset and not reset):
        raise Exception(f"Edit user XP must receive either offset or reset, not neither nor both. "
                        f"Offset=`{offset}` Reset=`{reset}`.")
    if not variables.guilds_xp[guild_id].members_xp.get(user_id):
        return

    existing_xp_amount = int(variables.guilds_xp[guild_id].members_xp[user_id].xp)
    if offset:
        if existing_xp_amount + offset < 0:
            offset = existing_xp_amount
        variables.guilds_xp[guild_id].members_xp[user_id].add_xp(offset)
    elif reset:
        variables.guilds_xp[guild_id].members_xp[user_id].set_xp(0)
    variables.guilds_xp[guild_id].members_xp[user_id].is_synced = False
    variables.guilds_xp[guild_id].set_synced(False)

    return existing_xp_amount


def is_ignored_channel_or_role(message, xp_settings):
    if message.channel.id in xp_settings[XPKeys.IGNORED_CHANNELS]:
        return True
    if xp_settings[XPKeys.IGNORED_ROLES]:
        for role in message.author.roles:
            if role.id in xp_settings[XPKeys.IGNORED_ROLES]:
                return True
    return False


def initiate_guild_or_member_data_if_not_exist(guild, member):
    if guild.id not in variables.guilds_xp:
        variables.guilds_xp[guild.id] = GuildXP(guild.id)
    if member.id not in variables.guilds_xp[guild.id].members_xp:
        variables.guilds_xp[guild.id].members_xp[member.id] = MemberXP(member.id)
        variables.guilds_xp[guild.id].members_xp[member.id].set_member_tag(str(member))


def update_xp_and_timeframe(message, xp_settings):
    member_xp: MemberXP = variables.guilds_xp[message.guild.id].members_xp[message.author.id]

    is_booster = message.author in message.guild.premium_subscribers
    timeframe = xp_settings[XPKeys.XP_GAIN_TIMEFRAME]
    current_time = int(time.time()) - time.altzone

    if member_xp.timeframe_ts > 0 and (current_time - member_xp.timeframe_ts) > timeframe:
        rand_multiplier = xp_settings[XPKeys.XP_GAIN_MAX] - xp_settings[XPKeys.XP_GAIN_MIN] + 1
        if not rand_multiplier < 1:
            xp_gain = xp_settings[XPKeys.XP_GAIN_MIN] + int(random.random() * rand_multiplier)
        else:
            xp_gain = xp_settings[XPKeys.XP_GAIN_MIN]
        if is_booster:
            xp_gain += int(xp_gain * float(xp_settings[XPKeys.BOOST_EXTRA_GAIN]/100))
        variables.guilds_xp[message.guild.id].members_xp[message.author.id].add_xp(xp_gain)
        variables.guilds_xp[message.guild.id].members_xp[message.author.id].set_timeframe_ts(current_time)
        variables.guilds_xp[message.guild.id].members_xp[message.author.id].set_member_tag(str(message.author))
        return True
    elif member_xp.timeframe_ts < 0:
        variables.guilds_xp[message.guild.id].members_xp[message.author.id].set_timeframe_ts(current_time)

    return False


def update_level(member):
    current_xp = variables.guilds_xp[member.guild.id].members_xp[member.id].xp

    level = 0
    for xp_requirement in variables.xp_level_map.keys():
        if current_xp >= xp_requirement:
            level = variables.xp_level_map[xp_requirement]
        else:
            break
    if level != variables.guilds_xp[member.guild.id].members_xp[member.id].level:
        variables.guilds_xp[member.guild.id].members_xp[member.id].set_level(level)
        return True
    return False


async def award_role(member, xp_settings):
    member_level = variables.guilds_xp[member.guild.id].members_xp[member.id].level
    role_id = xp_settings[XPKeys.LEVEL_ROLES].get(member_level, None)
    role = member.guild.get_role(role_id)
    reason = f"Level roles adjustment" if not role else f"Role <@&{role_id}> awarded at level {member_level}"
    await modify_member_level_roles(member=member, member_level=member_level, xp_settings=xp_settings,
                                    reason=reason)
    return role


async def modify_member_level_roles(member, member_level, xp_settings, reason):
    level_roles = xp_settings[XPKeys.LEVEL_ROLES]
    if not level_roles:
        return
    member_roles_ids = [role.id for role in member.roles]
    new_roles_ids = [role_id for role_id in member_roles_ids if role_id not in level_roles.values()]
    level_roles_member_is_eligible_for = {
        level: role_id for level, role_id in level_roles.items() if level <= member_level
    }

    if xp_settings[XPKeys.STACK_ROLES]:
        new_roles_ids.extend(level_roles_member_is_eligible_for.values())
    else:
        new_roles_ids.append(level_roles[max(list(level_roles_member_is_eligible_for.keys()))])

    if new_roles_ids == member_roles_ids:
        return
    await edit_roles(member=member, roles_ids=new_roles_ids, reason=reason)


async def send_levelup_message(message, xp_settings, awarded_role):
    level = variables.guilds_xp[message.guild.id].members_xp[message.author.id].level
    channel = message.channel
    custom_channel = message.guild.get_channel(xp_settings[XPKeys.LEVELUP_CHANNEL])
    if custom_channel:
        channel = custom_channel

    message_template = xp_settings[XPKeys.LEVELUP_MESSAGE]
    message_to_send = message_template. \
        format(member_mention=message.author.mention,
               member_tag=str(message.author),
               level=level)

    if awarded_role:
        message_to_send += f"\n{xp_settings[XPKeys.LEVEL_ROLE_EARN_MESSAGE].format(role_name=str(awarded_role))}"

    await send_message(message_to_send, channel)
