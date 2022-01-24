import asyncio

from actions import add_roles, remove_role, add_role
from globals_.clients import firebase_client
from globals_ import variables
from models.guild import GuildPrefs


async def save_roles_for(member):
    roles_ids = []
    for role in member.roles:
        if str(role) in ["everyone", "@everyone"] or role.id == member.guild.id:
            continue
        roles_ids.append(str(role.id))
    await firebase_client.save_user_roles_for_guild(member.id, roles_ids, member.guild.id)


async def reinstate_roles_for(member):
    await asyncio.sleep(3)
    roles_ids = (await firebase_client.get_user_roles_for_guild(member.id, member.guild.id)).val()
    if roles_ids is not None and len(roles_ids) > 0:
        if len(roles_ids) == 1 and roles_ids[0] == member.guild.id:
            return False
        await add_roles(member, roles_ids, reason="Role persistence")
        return True
    return False


async def handle_react_role_add(guild, channel_id, message_id, member, emoji):
    guild_prefs: GuildPrefs = variables.guilds_prefs[guild.id]
    role_id = guild_prefs.react_roles.get(channel_id, {}).get(message_id, {}).get(emoji.id, None)
    if not role_id:
        return
    role = guild.get_role(role_id)
    if role:
        await add_role(member, role_id, reason="React role")


async def handle_react_role_remove(guild, channel_id, message_id, member, emoji):
    guild_prefs: GuildPrefs = variables.guilds_prefs[guild.id]
    role_id = guild_prefs.react_roles.get(channel_id, {}).get(message_id, {}).get(emoji.id, None)
    if not role_id:
        return
    role = guild.get_role(role_id)
    if role:
        await remove_role(member, role_id, reason="React role - unreacted")
