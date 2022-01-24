import asyncio

from disnake import MessageInteraction

from globals_.constants import CommandType, UserCommandSection, AdminCommandSection, MusicCommandSection
from globals_.clients import discord_client
from actions import edit_message
from helpers import get_section_help_views, get_main_help_views
from embed_factory import make_section_help_embed, make_section_admin_help_embed, make_section_music_help_embed


async def help_navigation(received_message, sent_message, main_embed, guild_prefs):
    return await help_navigation_for(received_message, sent_message, main_embed, guild_prefs, CommandType.USER)


async def music_help_navigation(received_message, sent_message, main_embed, guild_prefs):
    return await help_navigation_for(received_message, sent_message, main_embed, guild_prefs, CommandType.MUSIC)


async def admin_help_navigation(received_message, sent_message, main_embed, guild_prefs):
    return await help_navigation_for(received_message, sent_message, main_embed, guild_prefs, CommandType.ADMIN)


async def help_navigation_for(received_message, sent_message, main_embed, guild_prefs, command_type):
    command_type_section = UserCommandSection if command_type == CommandType.USER \
        else AdminCommandSection if command_type == CommandType.ADMIN \
        else MusicCommandSection if CommandType.MUSIC \
        else None
    while True:

        def check_help_interactions(interaction_: MessageInteraction):
            if interaction_.message.id != sent_message.id:
                return False
            if interaction_.user.id != received_message.author.id:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            return True

        try:
            interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                        check=check_help_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, None, embed=main_embed, view=None)
            return

        if interaction.data.custom_id == 'close':
            await interaction.response.defer()
            await interaction.edit_original_message(content="Help menu closed.", embed=None, view=None)
            return

        if interaction.data.values and\
                interaction.data.values[0] in [section for section in command_type_section.as_list()]:
            command_section = interaction.data.values[0]
        else:
            continue
        if command_type == CommandType.USER:
            section_embed = make_section_help_embed(command_section, guild_prefs)
        elif command_type == CommandType.ADMIN:
            section_embed = make_section_admin_help_embed(command_section, guild_prefs)
        elif command_type == CommandType.MUSIC:
            section_embed = make_section_music_help_embed(command_section, guild_prefs)
        else:
            return

        await interaction.response.defer()
        await interaction.edit_original_message(content=None, embed=section_embed, view=get_section_help_views())

        try:
            interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                        check=check_help_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, None, embed=section_embed, view=None)
            return

        if interaction.data.custom_id == 'back':
            await interaction.response.defer()
            await interaction.edit_original_message(content=None, embed=main_embed,
                                                    view=get_main_help_views(command_type_section))
