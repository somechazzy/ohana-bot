import asyncio
import traceback

from components.xp_components.base_xp_component import XPComponent

import random
from datetime import datetime

import discord
from globals_.clients import discord_client
from globals_.constants import XPSettingsKey as XPKeys, XP_LEVEL_MAP, MessageCountMode
from globals_ import shared_memory
from models.member import MemberXP
from models.guild import GuildXP


class XPHandlerComponent(XPComponent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def handle_xp_gain(self, message: discord.Message):
        xp_settings = shared_memory.guilds_prefs[message.guild.id].xp_settings
        member = message.author
        guild = message.guild

        if xp_settings[XPKeys.XP_GAIN_ENABLED]:

            self.initiate_guild_or_member_data_if_not_exist(guild=guild, member=member)

            current_time = int(datetime.utcnow().timestamp())
            shared_memory.guilds_xp[guild.id].members_xp[member.id].set_last_message_ts(current_time)

            if self.is_ignored_channel_or_role(message, xp_settings):
                return

            if xp_settings[XPKeys.MESSAGE_COUNT_MODE] is MessageCountMode.PER_MESSAGE:
                shared_memory.guilds_xp[guild.id].members_xp[member.id].increment_messages()

            xp_updated = self.update_xp_and_timeframe(message, xp_settings)

            if xp_updated:
                if xp_settings[XPKeys.MESSAGE_COUNT_MODE] is MessageCountMode.PER_TIMEFRAME:
                    shared_memory.guilds_xp[guild.id].members_xp[member.id].increment_messages()
                level_updated = self.update_level(member)
                awarded_role = None
                if level_updated and xp_settings[XPKeys.LEVEL_ROLES]:
                    awarded_role = self.award_role(message, xp_settings)
                if level_updated and xp_settings[XPKeys.LEVELUP_ENABLED]:
                    asyncio.get_event_loop().create_task(self.send_levelup_message(message, xp_settings, awarded_role))
            return True
        return False

    @staticmethod
    def is_ignored_channel_or_role(message, xp_settings):
        if message.channel.id in xp_settings[XPKeys.IGNORED_CHANNELS]:
            return True
        if xp_settings[XPKeys.IGNORED_ROLES]:
            for role in message.author.roles:
                if role.id in xp_settings[XPKeys.IGNORED_ROLES]:
                    return True
        return False

    @staticmethod
    def initiate_guild_or_member_data_if_not_exist(guild, member):
        if guild.id not in shared_memory.guilds_xp:
            shared_memory.guilds_xp[guild.id] = GuildXP(guild.id)
        if member.id not in shared_memory.guilds_xp[guild.id].members_xp:
            shared_memory.guilds_xp[guild.id].members_xp[member.id] = MemberXP(member.id)
            shared_memory.guilds_xp[guild.id].members_xp[member.id].set_member_tag(str(member))

    @staticmethod
    def update_xp_and_timeframe(message, xp_settings):
        member_xp: MemberXP = shared_memory.guilds_xp[message.guild.id].members_xp[message.author.id]

        is_booster = message.author in message.guild.premium_subscribers
        timeframe = xp_settings[XPKeys.XP_GAIN_TIMEFRAME]
        current_time = int(datetime.utcnow().timestamp())

        if member_xp.timeframe_ts > 0 and (current_time - member_xp.timeframe_ts) > timeframe:
            rand_multiplier = xp_settings[XPKeys.XP_GAIN_MAX] - xp_settings[XPKeys.XP_GAIN_MIN] + 1
            if not rand_multiplier < 1:
                xp_gain = xp_settings[XPKeys.XP_GAIN_MIN] + int(random.random() * rand_multiplier)
            else:
                xp_gain = xp_settings[XPKeys.XP_GAIN_MIN]
            if is_booster:
                xp_gain += int(xp_gain * float(xp_settings[XPKeys.BOOST_EXTRA_GAIN] / 100))
            shared_memory.guilds_xp[message.guild.id].members_xp[message.author.id].add_xp(xp_gain)
            shared_memory.guilds_xp[message.guild.id].members_xp[message.author.id].set_timeframe_ts(current_time)
            shared_memory.guilds_xp[message.guild.id].members_xp[message.author.id].set_member_tag(str(message.author))
            return True
        elif member_xp.timeframe_ts < 0:
            shared_memory.guilds_xp[message.guild.id].members_xp[message.author.id].set_timeframe_ts(current_time)

        return False

    @staticmethod
    def update_level(member):
        current_xp = shared_memory.guilds_xp[member.guild.id].members_xp[member.id].xp

        level = 0
        for xp_requirement in XP_LEVEL_MAP.keys():
            if current_xp >= xp_requirement:
                level = XP_LEVEL_MAP[xp_requirement]
            else:
                break
        if level != shared_memory.guilds_xp[member.guild.id].members_xp[member.id].level:
            shared_memory.guilds_xp[member.guild.id].members_xp[member.id].set_level(level)
            return True
        return False

    def award_role(self, message, xp_settings):
        member = message.author
        member_level = shared_memory.guilds_xp[member.guild.id].members_xp[member.id].level
        role_id = xp_settings[XPKeys.LEVEL_ROLES].get(member_level, None)
        role = member.guild.get_role(role_id)
        reason = f"Level roles adjustment" if not role else f"Role <@&{role_id}> awarded at level {member_level}"
        self.modify_member_level_roles(member=member, member_level=member_level, xp_settings=xp_settings,
                                       reason=reason)
        return role

    def modify_member_level_roles(self, member, member_level, xp_settings, reason):
        from actions import edit_roles
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

        try:
            asyncio.get_event_loop().create_task(edit_roles(member=member, roles_ids=new_roles_ids, reason=reason))
        except Exception as e:
            self.error_logger.log(f"Error while modifying member level roles {e}:\n {traceback.format_exc()}",
                                  guild_id=member.guild.id, user_id=member.id)

    @staticmethod
    async def send_levelup_message(message, xp_settings, awarded_role):
        from actions import send_message
        level = shared_memory.guilds_xp[message.guild.id].members_xp[message.author.id].level
        channel = message.channel
        custom_channel = message.guild.get_channel(xp_settings[XPKeys.LEVELUP_CHANNEL])
        if not isinstance(custom_channel, type(None)):
            channel = custom_channel

        message_template = xp_settings[XPKeys.LEVELUP_MESSAGE]
        message_to_send = message_template. \
            format(member_mention=message.author.mention,
                   member_tag=str(message.author),
                   level=level)

        if awarded_role:
            message_to_send += f"\n{xp_settings[XPKeys.LEVEL_ROLE_EARN_MESSAGE].format(role_name=str(awarded_role))}"

        await send_message(message_to_send, channel)

    def edit_member_xp(self, member, offset: int = 0, reset=False):
        if (offset and reset) or (not offset and not reset):
            self.error_logger.log(f"Edit member XP must receive either offset or reset, not neither nor both. "
                                  f"Offset=`{offset}` Reset=`{reset}`.")
        self.initiate_guild_or_member_data_if_not_exist(guild=member.guild, member=member)
        xp_settings = shared_memory.guilds_prefs[member.guild.id].xp_settings
        existing_xp_amount = int(shared_memory.guilds_xp[member.guild.id].members_xp[member.id].xp)
        if offset:
            if existing_xp_amount + offset < 0:
                offset = existing_xp_amount
            shared_memory.guilds_xp[member.guild.id].members_xp[member.id].add_xp(offset)
        elif reset:
            shared_memory.guilds_xp[member.guild.id].members_xp[member.id].set_xp(0)

        level_updated = self.update_level(member=member)
        if level_updated and xp_settings[XPKeys.LEVEL_ROLES]:
            self.modify_member_level_roles(
                member=member,
                member_level=shared_memory.guilds_xp[member.guild.id].members_xp[member.id].level,
                xp_settings=xp_settings,
                reason="Adjustment after member XP action"
            )

    def edit_user_xp(self, user_id, guild_id, offset: int = 0, reset=False):
        """
        Used for editing XP of a user who no longer exists in a guild
        """
        if (offset and reset) or (not offset and not reset):
            self.error_logger.log(f"Edit user XP must receive either offset or reset, not neither nor both. "
                                  f"Offset=`{offset}` Reset=`{reset}`.")
        if not shared_memory.guilds_xp[guild_id].members_xp.get(user_id):
            return

        existing_xp_amount = int(shared_memory.guilds_xp[guild_id].members_xp[user_id].xp)
        if offset:
            if existing_xp_amount + offset < 0:
                offset = existing_xp_amount
            shared_memory.guilds_xp[guild_id].members_xp[user_id].add_xp(offset)
        elif reset:
            shared_memory.guilds_xp[guild_id].members_xp[user_id].set_xp(0)

        return existing_xp_amount

    async def readjust_level_and_roles_after_decay(self, member_id, guild_id):
        xp_settings = shared_memory.guilds_prefs[guild_id].xp_settings
        current_xp = shared_memory.guilds_xp[guild_id].members_xp[member_id].xp
        level_before = shared_memory.guilds_xp[guild_id].members_xp[member_id].level
        level = 0
        for xp_requirement in XP_LEVEL_MAP.keys():
            if current_xp >= xp_requirement:
                level = XP_LEVEL_MAP[xp_requirement]
            else:
                break
        shared_memory.guilds_xp[guild_id].members_xp[member_id].set_level(level)

        if level != level_before:
            guild = discord_client.get_guild(guild_id)
            if guild:
                member = guild.get_member(member_id)
                if member:
                    self.modify_member_level_roles(member=member, member_level=level, xp_settings=xp_settings,
                                                   reason="Level roles readjustment (after decaying)")
