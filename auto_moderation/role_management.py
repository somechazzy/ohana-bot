import asyncio

import discord

from actions import add_roles, edit_roles
from globals_.clients import firebase_client
from globals_.constants import RoleMenuType, RoleMenuMode
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent


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


async def handle_role_menu_interaction(interaction: discord.Interaction):
    if not interaction.guild:
        return

    guild_prefs = await GuildPrefsComponent().get_guild_prefs(guild=interaction.guild)
    if not guild_prefs:
        return
    role_menu_config = guild_prefs.role_menus.get(interaction.message.id)
    if not role_menu_config:
        return

    member = interaction.guild.get_member(interaction.user.id)
    restricted_to_roles = role_menu_config["restricted_to_roles"]
    if restricted_to_roles:
        if not any([role.id in restricted_to_roles for role in member.roles]):
            await interaction.response.send_message(
                "You don't have any of the required roles to use this menu:\n"
                f"{', '.join([interaction.guild.get_role(role_id).mention for role_id in restricted_to_roles])}",
                ephemeral=True
            )
            return

    available_role_ids = set()
    if role_menu_config["type"] == RoleMenuType.SELECT:
        selected_role_ids = set(map(int, interaction.data["values"]))
        for select_menu in interaction.message.components[0].children:
            available_role_ids |= {int(option.value) for option in select_menu.options}
    else:
        selected_role_ids = {int(interaction.data["custom_id"])}
        for component in interaction.message.components:
            available_role_ids |= {int(button.custom_id) for button in component.children}

    selected_role_ids = selected_role_ids & available_role_ids
    # 0 indicates selection of "remove role(s)" option
    available_role_ids.discard(0)

    if not selected_role_ids:
        return

    roles_ids_to_add, role_ids_to_remove = set(), set()
    existing_user_role_ids = {role.id for role in member.roles}

    if 0 in selected_role_ids:
        role_ids_to_remove.update(existing_user_role_ids & available_role_ids)
    elif role_menu_config["mode"] == RoleMenuMode.SINGLE:
        selected_role_id = selected_role_ids.pop()
        if selected_role_id in existing_user_role_ids:
            role_ids_to_remove.add(selected_role_id)
        else:
            roles_ids_to_add.add(selected_role_id)
            role_ids_to_remove.update(existing_user_role_ids & available_role_ids)
            role_ids_to_remove.discard(selected_role_id)
    else:
        if selected_role_ids.issubset(existing_user_role_ids):
            role_ids_to_remove.update(selected_role_ids)
        elif not selected_role_ids & existing_user_role_ids:
            roles_ids_to_add.update(selected_role_ids)
        else:
            roles_ids_to_add.update(selected_role_ids - existing_user_role_ids)
            role_ids_to_remove.update(existing_user_role_ids & (available_role_ids - selected_role_ids))

    roles_to_add = [interaction.guild.get_role(role_id) for role_id in roles_ids_to_add
                    if interaction.guild.get_role(role_id)]
    roles_to_remove = {interaction.guild.get_role(role_id) for role_id in role_ids_to_remove
                       if interaction.guild.get_role(role_id)}
    if roles_to_add or roles_to_remove:
        new_member_roles = [role for role in member.roles if role not in roles_to_remove] + roles_to_add
        await edit_roles(member=member, roles=new_member_roles, reason="Role menu")

    feedback_message = ""
    if roles_ids_to_add:
        feedback_message += \
            f"\nAdded roles: " \
            f"{', '.join([interaction.guild.get_role(role_id).mention for role_id in roles_ids_to_add])}"
    if role_ids_to_remove:
        feedback_message += \
            f"\nRemoved roles: " \
            f"{', '.join([interaction.guild.get_role(role_id).mention for role_id in role_ids_to_remove])}"
    if not roles_ids_to_add and not role_ids_to_remove:
        feedback_message = "Nothing changed.."
    await interaction.response.send_message(f"Roles updated:\n{feedback_message.strip()}", ephemeral=True)


async def scan_and_assign_role_for_single_message_channel(channel, created_role,
                                                          interaction_to_edit_upon_completion=None):
    counter = 0
    members = []

    async for message in channel.history(limit=300):
        if message.author not in members:
            members.append(message.author)
    for member in members:
        if member is channel.guild.me or member not in channel.guild.members:
            continue
        try:
            await member.add_roles(created_role, reason=f"single-text mode role for #{channel}")
        except Exception:
            await asyncio.sleep(1)
            continue
        counter += 1
        await asyncio.sleep(1)

    if interaction_to_edit_upon_completion:
        try:
            await interaction_to_edit_upon_completion.edit_original_response(content=f"Added role to {counter} members")
        except Exception:
            pass

    return counter


async def assign_autoroles(member, wait=3):
    autoroles = (await GuildPrefsComponent().get_guild_prefs(member.guild)).autoroles
    if wait:
        await asyncio.sleep(wait)
    await add_roles(member, autoroles, reason="Autorole")
