import discord

import cache
from bot.utils.guild_logger import GuildLogger, GuildLogEventField
from bot.utils.helpers.moderation_helpers import bot_can_assign_role
from clients import discord_client
from common.app_logger import AppLogger
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import GuildLogEvent, XPLevelUpMessageSubstitutable

logger = AppLogger(__name__)


async def handle_roles_and_level_up_message_on_level_update(guild_id: int,
                                                            user_id: int,
                                                            level_change_reason: str,
                                                            channel_id: int | None = None):
    """
    Handles the level role assignment and level-up message sending when a user's level is updated.
    Args:
        guild_id (int): Guild ID the user belongs to.
        user_id (int): User ID whose level is updated.
        level_change_reason (str): Reason for the level change, used in logging and role edit audit.
        channel_id (int | None): channel ID that triggered the level update, if any.
            If passed, a level-up message will be sent.
    """
    guild = discord_client.get_guild(guild_id)
    if not guild:
        return
    if guild.chunked:
        member = guild.get_member(user_id)
    else:
        try:
            member = await guild.fetch_member(user_id)
        except (discord.NotFound, discord.Forbidden):
            member = None
    if not member:
        return
    xp_settings = (await GuildSettingsComponent().get_guild_settings(guild_id)).xp_settings
    member_xp = cache.CACHED_GUILD_XP[guild_id].get_xp_for(member.id)

    level_roles_map_member_is_eligible_for = {
        level_role_level: role_ids for level_role_level, role_ids
        in xp_settings.level_role_ids_map.items() if level_role_level <= member_xp.level
    }
    new_member_level_roles = set()
    if level_roles_map_member_is_eligible_for:
        if xp_settings.stack_level_roles:
            for level_role_level, role_ids in level_roles_map_member_is_eligible_for.items():
                new_member_level_roles.update(
                    {guild.get_role(role_id) for role_id in role_ids if guild.get_role(role_id) and
                     bot_can_assign_role(guild.get_role(role_id))}
                )
        else:
            highest_level_role_level = max(level_roles_map_member_is_eligible_for.keys())
            new_member_level_roles.update(
                {guild.get_role(role_id) for role_id in level_roles_map_member_is_eligible_for[highest_level_role_level]
                 if guild.get_role(role_id) and bot_can_assign_role(guild.get_role(role_id))}
            )

    existing_member_roles = set(member.roles)
    new_member_roles = set(member.roles) | set(new_member_level_roles)

    added_roles = set()
    if existing_member_roles != (existing_member_roles | new_member_level_roles):
        added_roles = new_member_roles - existing_member_roles
        removed_roles = existing_member_roles - new_member_roles

        member = await member.edit(roles=new_member_roles, reason=level_change_reason)
        await GuildLogger(guild).log_event(event=GuildLogEvent.EDITED_ROLES,
                                           roles_deltas=(added_roles, removed_roles),
                                           member=member,
                                           reason=level_change_reason,
                                           fields=[GuildLogEventField(name='New Level',
                                                                      value=str(member_xp.level))])
    if channel_id \
            and xp_settings.level_up_message_enabled \
            and member_xp.level >= xp_settings.level_up_message_minimum_level:
        if not xp_settings.level_up_message_channel_id \
                or not (channel := guild.get_channel(xp_settings.level_up_message_channel_id)):
            channel = guild.get_channel(channel_id)
        level_up_message_substitutions = {
            XPLevelUpMessageSubstitutable.LEVEL: str(member_xp.level),
            XPLevelUpMessageSubstitutable.MEMBER_MENTION: member.mention,
            XPLevelUpMessageSubstitutable.MEMBER_NAME: member.display_name,
        }
        level_up_message_text = xp_settings.level_up_message_text.format(**level_up_message_substitutions)
        if added_roles:
            highest_role = max(added_roles, key=lambda r: r.position)
            if highest_role.id in xp_settings.level_role_ids_map.get(member_xp.level, []):
                level_up_message_text += "\n" + \
                                         xp_settings.level_role_earn_message_text.format(role_name=highest_role.name)
        await channel.send(level_up_message_text)
        logger.info(f"Sent level-up message in guild {guild} for user {member_xp.user_username}"
                    f" on reaching level {member_xp.level}")
