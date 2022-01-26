import disnake as discord


def bot_has_permission_to_send_text_in_channel(channel):
    """
    Simple function that returns whether or not you bot can send a message in a channel
    :param (discord.TextChannel or discord.DMChannel) channel: 
    :return: bool
    """
    if isinstance(channel, discord.DMChannel):
        return True
    bot_member = channel.guild.me
    permissions = channel.permissions_for(bot_member)
    return permissions.send_messages


def bot_has_permission_to_send_embed_in_channel(channel):
    if isinstance(channel, discord.DMChannel):
        return True
    bot_member = channel.guild.me
    permissions: discord.Permissions = channel.permissions_for(bot_member)
    return permissions.embed_links


def can_moderate_target_member(requesting_member, target_member, check_bot_hierarchy=True):
    """
    Checks whether or not a particular member can have a moderation action taken against them
    by the requesting user and by the bot.
    :param (discord.Member) requesting_member:
    :param (discord.Member) target_member:
    :param (bool) check_bot_hierarchy:
    :return: bool
    """
    if requesting_member_can_moderate_target_member(requesting_member, target_member):
        if bot_can_moderate_target_member(target_member) or not check_bot_hierarchy:
            return True, "None"
        else:
            return False, "bot"
    return False, "member"


def bot_can_moderate_target_member(target_member):
    if target_member == target_member.guild.owner:
        return False
    bot_roles = target_member.guild.me.roles
    bot_roles.reverse()
    bot_highest_role = bot_roles[0]
    target_roles = target_member.roles
    target_roles.reverse()
    target_highest_role = target_roles[0]
    return bot_highest_role > target_highest_role


def requesting_member_can_moderate_target_member(requesting_member, target_member):
    if target_member == target_member.guild.owner:
        return False
    if requesting_member == target_member.guild.owner:
        return True
    requesting_roles = requesting_member.roles
    requesting_roles.reverse()
    requesting_highest_role = requesting_roles[0]
    target_roles = target_member.roles
    target_roles.reverse()
    target_highest_role = target_roles[0]
    return requesting_highest_role > target_highest_role
