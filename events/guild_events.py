from internal.bot_logging import log
from globals_.clients import discord_client
from globals_ import constants, variables
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from datetime import datetime
from embed_factory import make_initial_player_message_embed


@discord_client.event
async def on_guild_join(guild):
    member_count = guild.member_count
    human_count = len([member for member in guild.members if not member.bot])
    bot_count = len([member for member in guild.members if member.bot])
    owner_other_guild_count = \
        len([guild_ for guild_ in discord_client.guilds if guild_.owner.id == guild.owner.id and guild_.id != guild.id])
    await log(f"{guild} ({guild.id}): {member_count} members.\n"
              f"Owned by {guild.owner} ({guild.owner.id}).\n" +
              (f"**Bot is in** {owner_other_guild_count} other guilds they own.\n" if owner_other_guild_count else "") +
              f"Created at <t:{int(datetime.timestamp(guild.created_at))}:f>.\n"
              f"Human count = {human_count}.\n"
              f"Bot count = {bot_count}.\n"
              f"Bot Percentage = {round(bot_count/member_count, 2)}.\n"
              f"Bot admin status: {guild.me.guild_permissions.administrator}.",
              level=constants.BotLogType.GUILD_JOIN, ping_me=True, guild_id=guild.id)
    if guild.id not in variables.guilds_prefs.keys():
        await GuildPrefsComponent().make_default_guild_prefs(guild)
    else:
        await GuildPrefsComponent().set_currently_in_guild(guild, True)


@discord_client.event
async def on_guild_remove(guild):
    if guild:
        await log(f"{guild} ({guild.id}): {guild.member_count} members.\nOwned by {guild.owner} ({guild.owner.id}).\n"
                  f"Created at <t:{int(datetime.timestamp(guild.created_at))}:f>.",
                  level=constants.BotLogType.GUILD_LEAVE, ping_me=True, guild_id=guild.id)
        await GuildPrefsComponent().set_currently_in_guild(guild, False)


@discord_client.event
async def on_voice_state_update(member, _, after):
    if member.id == discord_client.user.id:
        if not after.channel:
            guild_prefs = variables.guilds_prefs[member.guild.id]
            music_channel = discord_client.get_channel(guild_prefs.music_channel)
            if music_channel:
                player_message = music_channel.get_partial_message(guild_prefs.music_player_message)
                if player_message:
                    embed = make_initial_player_message_embed(guild=member.guild)
                    await player_message.edit(embed=embed)
