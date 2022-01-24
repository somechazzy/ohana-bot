import disnake as discord


def bot_has_permission_to_send_text_in_channel(channel):
    if isinstance(channel, discord.channel.DMChannel):
        return True
    bot_member = channel.guild.me
    permissions = channel.permissions_for(bot_member)
    return permissions.send_messages


def bot_has_permission_to_send_embed_in_channel(channel):
    if isinstance(channel, discord.channel.DMChannel):
        return True
    bot_member = channel.guild.me
    permissions: discord.Permissions = channel.permissions_for(bot_member)
    return permissions.embed_links


def can_moderate_target_member(requesting_member, target_member, check_bot_hierarchy=True):
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
