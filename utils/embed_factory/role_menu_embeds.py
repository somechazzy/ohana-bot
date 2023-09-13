import discord

from globals_.constants import RoleMenuType, RoleMenuMode, Colour


def make_role_menu_embed(role_menu_name, guild, title, color=Colour.PRIMARY_ACCENT, thumbnail=None, image=None,
                         footer_note=None, role_menu_type=RoleMenuType.SELECT, role_menu_mode=RoleMenuMode.SINGLE,
                         is_restricted=False, restricted_description=None):
    guild_avatar = guild.icon.with_size(256).url if guild.icon else None
    embed = discord.Embed(title=title, color=color)
    embed.set_author(name=role_menu_name, icon_url=guild_avatar)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if footer_note:
        embed.set_footer(text=footer_note)
    description = ""
    if is_restricted and restricted_description:
        description += f"**{restricted_description.strip()}**\n"
    description += f"{'Click on the buttons' if role_menu_type == RoleMenuType.BUTTON else 'Select from the list'}" \
                   f" below to get your roles."
    if role_menu_mode == RoleMenuMode.SINGLE:
        description += " You can select only one role at a time."
    else:
        description += " You can select multiple roles at a time."
    embed.description = description
    return embed


def make_role_menu_setup_embed(guild, added_roles_map, role_menu_type, role_menu_mode, restricted_to_roles, info=None):
    bot_avatar = guild.me.avatar.with_size(256).url if guild.me.avatar else None
    guild_avatar = guild.icon.with_size(256).url if guild.icon else None
    description = f"Use the buttons below to customize your role menu. " \
                  f"Changes will reflect on the role menu I just sent to this channel."
    embed = discord.Embed(title="Role Menu Creation", color=Colour.PRIMARY_ACCENT, description=description)

    if role_menu_mode == RoleMenuMode.SINGLE:
        role_mode_value = "Single Role (user can have only one role at a time from this menu)."
    else:
        role_mode_value = "Multiple Roles (user can have multiple roles at a time from this menu)."

    roles_field_value = ""
    ordered_role_tuples = [tuple()] * len(added_roles_map)
    for role_id, role_details in added_roles_map.items():
        role_option_name = role_details['alias']
        role_emoji = role_details['emoji']
        role_rank = role_details['rank']
        ordered_role_tuples[role_rank - 1] = (role_id, role_option_name, role_emoji)
    for role_id, role_option_name, role_emoji in ordered_role_tuples:
        emoji_str = (str(role_emoji) + ' ') if role_emoji else ""
        roles_field_value += f"• {emoji_str}{role_option_name} (<@&{role_id}>)\n"
    if not roles_field_value:
        roles_field_value = "*No roles added yet.*"
    embed.add_field(name="Added Roles", value=roles_field_value, inline=False)

    embed.add_field(name="Selection Mode", value=role_mode_value, inline=False)
    embed.add_field(name="Menu Type", value="Buttons" if role_menu_type == RoleMenuType.BUTTON else "Dropdown Select",
                    inline=False)
    if restricted_to_roles:
        restriction_value = "This role menu is restricted to people with **any** of the following roles: "
        restriction_value += ", ".join([f"<@&{role_id}>" for role_id in restricted_to_roles])
    else:
        restriction_value = "This role menu is open to everyone, click on `Restrict Menu` below to change that."
    embed.add_field(name="Restriction", value=restriction_value, inline=False)
    embed.set_author(name=guild.name, icon_url=guild_avatar)
    embed.set_footer(text="Delete/dismiss this message once you're finished with setting up!", icon_url=bot_avatar)

    if info:
        embed.add_field(name="Info", value=info, inline=False)

    return embed
