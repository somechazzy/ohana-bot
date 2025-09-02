"""
Actions related to automoderation.
"""
import discord

from bot.utils.bot_actions.basic_actions import delete_message, add_roles
from bot.utils.guild_logger import GuildLogger, GuildLogEventField
from bot.utils.helpers.moderation_helpers import bot_can_assign_role
from common.app_logger import AppLogger
from common.decorators import require_db_session
from components.guild_settings_components.guild_channel_settings_component import GuildChannelSettingsComponent
from components.guild_settings_components.guild_user_roles_component import GuildUserRolesComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import GuildLogEvent, AutoResponseMatchType

logger = AppLogger('automod_actions')


@require_db_session
async def initialize_role_persistence_on_guild(guild: discord.Guild):
    """
    Initialize role persistence for a guild by saving all members' roles to the database.
    Args:
        guild (discord.Guild): The guild to initialize role persistence for.
    """
    member_id_role_ids_map = {}
    if not guild.chunked:
        await guild.chunk()
    for member in guild.members:
        if not member.bot:
            member_id_role_ids_map[member.id] = [role.id for role in member.roles if role.id != guild.id]

    await GuildUserRolesComponent().bulk_create_guild_user_roles(guild_id=guild.id,
                                                                 user_id_role_ids_map=member_id_role_ids_map,
                                                                 delete_existing_guild_user_roles=True)


@require_db_session
async def apply_persistent_roles_to_member(member: discord.Member) -> bool:
    """
    Apply persistent roles to a member based on the database records.
    Args:
        member (discord.Member): The member to apply roles to.
    Returns:
        bool: True if roles were applied, False otherwise.
    """
    member_roles = await GuildUserRolesComponent().get_guild_user_roles_for_user(guild_id=member.guild.id,
                                                                                 user_id=member.id)
    if not member_roles or not (role_ids := member_roles.role_ids):
        return False

    guild_logger = GuildLogger(guild=member.guild)
    roles_to_add = [member.guild.get_role(role_id) for role_id in role_ids if member.guild.get_role(role_id)  # noqa
                    and bot_can_assign_role(role=member.guild.get_role(role_id))]  # noqa
    if roles_to_add:
        try:
            await member.edit(roles=roles_to_add, reason="Applying persistent roles.")
        except Exception as e:
            if isinstance(e, discord.Forbidden):
                event_message = f"Failed to apply persistent roles to member {member.mention} due to permission issues."
            else:
                event_message = (f"Failed to apply persistent roles to member {member.mention}"
                                 f" due to an unexpected error.")
                logger.info(f"Failed to apply role persistence to member {member.id} in guild {member.guild.id}: {e}",
                            extras={'guild_id': member.guild.id, 'user_id': member.id})
            await guild_logger.log_event(event=GuildLogEvent.ACTION_ERROR,
                                         event_message=event_message,
                                         reason="Role persistence", )
            return False

    await guild_logger.log_event(event=GuildLogEvent.ASSIGNED_ROLES,
                                 roles=roles_to_add,
                                 member=member,
                                 reason="Role persistence")
    logger.info(f"Applied persistent roles to member {member.display_name} ({member.id})"
                f" in guild {member.guild} ({member.guild.id})",
                extras={'guild_id': member.guild.id, 'user_id': member.id})

    return True


@require_db_session
async def assign_autoroles_to_member(member: discord.Member):
    """
    Assign autoroles to a member.
    Args:
        member (discord.Member): The member to assign roles to.
    """
    autoroles = [member.guild.get_role(role_id) for role_id in
                 (await GuildSettingsComponent().get_guild_settings(member.guild.id)).autoroles_ids
                 if member.guild.get_role(role_id) and bot_can_assign_role(member.guild.get_role(role_id))]
    await add_roles(member=member, roles=autoroles, reason="Autoroles")
    logger.info(f"Assign autoroles to member {member.display_name} ({member.id})"
                f" in guild {member.guild} ({member.guild.id})",
                extras={'guild_id': member.guild.id, 'user_id': member.id})


async def perform_message_automoderation(message: discord.Message) -> bool:
    """
    Perform automoderation actions on a message.
    Args:
        message (discord.Message): The message to perform automoderation on.
    Returns:
        bool: True if the message was deleted, False otherwise.
    """
    guild_settings = await GuildSettingsComponent().get_guild_settings(message.guild.id)

    message_deleted = False
    if role_id := guild_settings.channel_id_message_limiting_role_id.get(message.channel.id):
        if message.author.get_role(role_id):
            if await delete_message(message, reason=f"Message-limited channel, author has the <@&{role_id}> role."):
                message_deleted = True
        elif message.guild.get_role(role_id):
            await add_roles(member=message.author, roles=[message.guild.get_role(role_id)],
                            reason=f"Message-limited channel.")
        else:  # role does not exist anymore
            await GuildChannelSettingsComponent().set_guild_channel_settings(
                guild_id=message.guild.id,
                guild_settings_id=guild_settings.guild_settings_id,
                channel_id=message.channel.id,
                message_limiting_role_id=None
            )
    if not message_deleted and guild_settings.channel_id_is_gallery_channel.get(message.channel.id):
        if not message.attachments:
            if await delete_message(message, reason="Message in gallery channel without attachments."):
                message_deleted = True
    if not message_deleted and guild_settings.auto_responses:
        matching_auto_response = None
        for auto_response in guild_settings.auto_responses:
            if auto_response.match_type == AutoResponseMatchType.EXACT:
                if auto_response.trigger.lower().strip() == message.content.lower().strip():
                    matching_auto_response = auto_response
                    break
            elif auto_response.match_type == AutoResponseMatchType.CONTAINS:
                if auto_response.trigger.lower().strip() in message.content.lower().strip():
                    matching_auto_response = auto_response
                    break
            elif auto_response.match_type == AutoResponseMatchType.STARTS_WITH:
                if message.content.lower().strip().startswith(auto_response.trigger.lower().strip()):
                    matching_auto_response = auto_response
                    break
        if matching_auto_response:
            sent_message = await message.channel.send(matching_auto_response.response, reference=message)
            await GuildLogger(guild=message.guild).log_event(
                event=GuildLogEvent.SENT_MESSAGE,
                message=sent_message,
                reason=f"Auto response to trigger: `{matching_auto_response.trigger}`",
                fields=[GuildLogEventField(name="Message", value=f"[Jump to message]({message.jump_url})")]
            )
            logger.info(f"Auto responded to message {message.id} in guild {message.guild.id}."
                        f" Auto response: {matching_auto_response.guild_auto_response_id}")
            if matching_auto_response.delete_original:
                if await delete_message(message,
                                        reason=f"Auto response to trigger `{matching_auto_response.trigger}`."):
                    message_deleted = True

    return message_deleted
