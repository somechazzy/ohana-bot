import discord

from common.exceptions import ModerationHierarchyError


def assert_hierarchy(actor: discord.Member, target: discord.Member):
    """
    Check if the actor can moderate the target member and if the bot can moderate the target member.
    Args:
        actor (discord.Member): The member performing the action.
        target (discord.Member): The member being acted upon.
    Raises:
        ModerationHierarchyError: If the actor or bot cannot moderate the target member.
    """
    if not actor_can_moderate_target_member(actor, target):
        raise ModerationHierarchyError("You do not have the necessary permission or role hierarchy order to do this.")
    if not bot_can_moderate_target_member(target):
        raise ModerationHierarchyError("I do not have the necessary permission or role hierarchy order to do this.")


def bot_can_moderate_target_member(target: discord.Member):
    """
    Check if the bot can moderate the target member.
    Args:
        target (discord.Member): The member being acted upon.
    Returns:
        bool: True if the bot can moderate the target member, False otherwise.
    """
    if target == target.guild.owner:
        return False
    return target.top_role > target.top_role


def actor_can_moderate_target_member(actor: discord.Member, target: discord.Member):
    """
    Check if the actor can moderate the target member.
    Args:
        actor (discord.Member): The member performing the action.
        target (discord.Member): The member being acted upon.
    Returns:
        bool: True if the actor can moderate the target member, False otherwise.
    """
    if target == target.guild.owner:
        return False
    if actor == actor.guild.owner:
        return True
    return actor.top_role > target.top_role


def bot_can_assign_role(role: discord.Role) -> bool:
    """
    Check if the bot can assign the given role.
    Args:
        role (discord.Role): The role to check.
    Returns:
        bool: True if the bot can assign the role, False otherwise.
    """
    if any([not role.guild.me.guild_permissions.manage_roles,
            role.guild.me.top_role <= role,
            role.is_bot_managed(),
            role.is_premium_subscriber(),
            role.is_integration(),
            role.is_default()]):
        return False
    return True


def actor_can_assign_role(actor: discord.Member, role: discord.Role) -> bool:
    """
    Check if the actor can assign the given role.
    Args:
        actor (discord.Member): The member performing the action.
        role (discord.Role): The role to check.
    Returns:
        bool: True if the actor can assign the role, False otherwise.
    """
    if any([not actor.guild_permissions.manage_roles,
            actor.top_role <= role,
            role.is_bot_managed(),
            role.is_premium_subscriber(),
            role.is_integration(),
            role.is_default()]):
        return False
    return True
