import discord


def bot_has_permission_to_send_text_in_channel(channel):
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
