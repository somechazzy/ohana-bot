import discord

from constants import RoleMenuDefaults, RoleMenuType, RoleMenuMode, Colour
from models.dto.role_menu import RoleMenuRole


def get_role_menu_embed(guild: discord.Guild,
                        role_menu_name: str = RoleMenuDefaults.NAME,
                        role_menu_description: str = RoleMenuDefaults.DESCRIPTION,
                        embed_color: hex = RoleMenuDefaults.EMBED_COLOUR,
                        thumbnail: str | None = None,
                        image: str | None = None,
                        footer_note: str | None = None,
                        role_menu_type: str = RoleMenuDefaults.MENU_TYPE,
                        role_menu_mode: str = RoleMenuDefaults.MENU_MODE,
                        is_restricted: bool = False,
                        restricted_description: str | None = None) -> discord.Embed:
    """
    Creates a role menu embed for displaying role selection options.
    Args:
        guild (discord.Guild): The guild where the role menu will be displayed.
        role_menu_name (str): The name of the role menu.
        role_menu_description (str): The description of the role menu.
        embed_color (hex): The color of the embed.
        thumbnail (str | None): The URL of the thumbnail image.
        image (str | None): The URL of the main image.
        footer_note (str | None): The footer note text.
        role_menu_type (str): The type of the role menu (button or select).
        role_menu_mode (str): The mode of the role menu (single or multiple).
        is_restricted (bool): Whether the role menu is restricted to certain roles.
        restricted_description (str | None): The description for the restriction, if any.
    Returns:
        discord.Embed: The created role menu embed.
    """
    guild_avatar = guild.icon.with_size(256).url if guild.icon else None
    embed = discord.Embed(title=role_menu_description, color=embed_color)
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


def get_role_menu_setup_embed(guild: discord.Guild,
                              role_menu_roles: list[RoleMenuRole],
                              role_menu_type: str,
                              role_menu_mode: str,
                              restricted_to_roles: list[discord.Role],
                              feedback_message: str | None = None) -> discord.Embed:
    """
    Creates an embed for setting up a role menu.
    Args:
        guild (discord.Guild): The guild where the role menu will be displayed.
        role_menu_roles (list[RoleMenuRole]): The list of roles added to the role menu.
        role_menu_type (str): The type of the role menu (button or select).
        role_menu_mode (str): The mode of the role menu (single or multiple).
        restricted_to_roles (list[discord.Role]): The list of roles that can use this role menu.
        feedback_message (str | None): Any feedback message to display in the embed.
    Returns:
        discord.Embed: The created role menu setup embed.
    """
    role_menu_roles.sort()
    added_roles_text = '\n'.join(f"• {str(role.emoji) + ' ' if role.emoji else ''}{role.alias} (<@&{role.role_id}>)"
                                 for role in role_menu_roles) if role_menu_roles else "*No roles added yet.*"
    embed = discord.Embed(title="Role Menu Creation",
                          color=Colour.PRIMARY_ACCENT,
                          description=f"Use the buttons below to customize your role menu. " 
                                      f"Changes will reflect on the role menu I just sent to this channel.\n‎\n"
                                      f"Added Roles:\n{added_roles_text}")

    embed.set_author(name=guild.name,
                     icon_url=guild.me.display_avatar.with_size(256).url)
    embed.set_footer(text="Delete/dismiss this message once you're finished with setting up!",
                     icon_url=guild.icon.with_size(256).url if guild.icon else None)

    embed.add_field(name="Selection Mode",
                    value="Single Role (user can have only one role at a time from this menu)."
                    if role_menu_mode == RoleMenuMode.SINGLE
                    else "Multiple Roles (user can have multiple roles at a time from this menu).",
                    inline=False)
    embed.add_field(name="Menu Type",
                    value="Buttons" if role_menu_type == RoleMenuType.BUTTON else "Dropdown Select",
                    inline=False)

    if restricted_to_roles:
        restriction_value = "This role menu is restricted to people with **any** of the following roles: "
        restriction_value += ", ".join([f"{role_.mention}" for role_ in restricted_to_roles])
    else:
        restriction_value = "This role menu is open to everyone, click on `Restrict Menu` below to change that."
    embed.add_field(name="Restriction", value=restriction_value, inline=False)

    if feedback_message:
        embed.add_field(name="Info", value=feedback_message, inline=False)

    embed.set_footer(text="Dismiss this message once you're finished with setting up!",
                     icon_url=guild.me.display_avatar.with_size(256).url)

    return embed


def get_role_menu_restriction_setup_embed(guild: discord.Guild,
                                          restricted_to_roles: list[discord.Role],
                                          restriction_description: str,
                                          feedback_message: str | None) -> discord.Embed:
    """
    Creates an embed for setting up role menu restrictions.
    Args:
        guild (discord.Guild): The guild where the role menu will be displayed.
        restricted_to_roles (list[discord.Role]): The list of roles that can use this role menu.
        restriction_description (str): The description for the restriction.
        feedback_message (str | None): Any feedback message to display in the embed.
    Returns:
        discord.Embed: The created role menu restriction setup embed.
    """
    embed = discord.Embed(title="Role Menu Restriction Setup",
                          color=Colour.PRIMARY_ACCENT,
                          description="Select the roles that can use this role menu. "
                                      "If none are selected then this role menu will remain open to everyone.\n"
                                      "Restriction description will be shown in the role menu embed.")

    embed.set_author(name=guild.name,
                     icon_url=guild.me.display_avatar.with_size(256).url)

    if restricted_to_roles:
        roles = [role.mention for role in restricted_to_roles]
        embed.add_field(name="Selected Roles", value=' • '.join(roles), inline=False)
    else:
        embed.add_field(name="Selected Roles", value="*No roles selected yet.*", inline=False)

    embed.add_field(name="Restriction Description",
                    value=restriction_description,
                    inline=False)

    if feedback_message:
        embed.add_field(name="Info", value=feedback_message, inline=False)

    return embed


def get_role_menu_image_setup_embed(guild: discord.Guild,
                                    image_url: str | None,
                                    image_placement: str) -> discord.Embed:
    """
    Creates an embed for setting up the role menu image.
    Args:
        guild (discord.Guild): The guild where the role menu will be displayed.
        image_url (str | None): The URL of the image to set.
        image_placement (str): The placement of the image (thumbnail or image).
    Returns:
        discord.Embed: The created role menu image setup embed.
    """
    embed = discord.Embed(title="Role Menu Image Setup",
                          color=Colour.PRIMARY_ACCENT,
                          description="Set the image or thumbnail for your role menu.\n"
                                      "Image placement can be \"Thumbnail\" (small, shown at the top of the embed) "
                                      "or \"Image\" (large, shown at the bottom of the embed).\n")
    embed.set_author(name=guild.name,
                     icon_url=guild.me.display_avatar.with_size(256).url)

    if image_url:
        embed.set_thumbnail(url=image_url)

    embed.add_field(name="Current Image",
                    value=f"Image URL: {f'`{image_url}`' if image_url else '*No image set.*'}\n"
                          f"Image Placement: {image_placement}.",
                    inline=False)

    return embed
