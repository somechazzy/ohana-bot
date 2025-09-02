"""
This module contains event handlers for interaction-related events.
"""
import discord

from bot.interaction_handlers.user_interaction_handlers.radio_interaction_handler import RadioInteractionHandler
from bot.interaction_handlers.user_interaction_handlers.reminder_delivery_interaction_handler import \
    ReminderDeliveryInteractionHandler
from bot.interaction_handlers.user_interaction_handlers.role_menu_interaction_handler import RoleMenuInteractionHandler
from bot.utils.bot_actions.utility_actions import refresh_music_player_message
from bot.utils.decorators import extensible_event
from clients import discord_client
from common.decorators import require_db_session
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from constants import MusicPlayerAction, ReminderDeliveryAction, CommandContext


@discord_client.event
@require_db_session
@extensible_event(group='interaction')
async def on_interaction(interaction: discord.Interaction):
    """
    Event handler for interactions.
    Args:
        interaction (discord.Interaction): The interaction object.
    """
    custom_id = interaction.data.get('custom_id') if interaction.data else None
    if not interaction.message or interaction.message.author.id != discord_client.user.id or not custom_id:
        return
    guild_settings = await GuildSettingsComponent().get_guild_settings(interaction.guild_id) \
        if interaction.guild_id else None
    message_id = interaction.message.id
    channel_id = interaction.channel.id

    ### Radio player actions ###
    if guild_settings \
            and channel_id == guild_settings.music_channel_id \
            and custom_id.startswith(MusicPlayerAction.qualifier()):
        if guild_settings.music_player_message_id == message_id:
            radio_interaction_handler = RadioInteractionHandler(
                source_interaction=interaction,
                context=CommandContext.GUILD,
                guild_settings=guild_settings,
            )
            await radio_interaction_handler.handle_action(
                action=custom_id.split(MusicPlayerAction.qualifier() + '-', 1)[-1]
            )
        elif custom_id.startswith(MusicPlayerAction.qualifier() + "-" + MusicPlayerAction.subselect_qualifier()):
            radio_interaction_handler = RadioInteractionHandler(
                source_interaction=interaction,
                context=CommandContext.GUILD,
                guild_settings=guild_settings,
            )
            await radio_interaction_handler.handle_action(
                action=custom_id.split(MusicPlayerAction.qualifier() +
                                       '-' + MusicPlayerAction.subselect_qualifier() + '-', 1)[-1]
            )
        else:  # old player message, delete it and resend if necessary
            try:
                await interaction.message.delete()
            except:
                pass
            await refresh_music_player_message(guild=interaction.guild)
    ### Reminder delivery actions ###
    elif not guild_settings and custom_id.startswith(ReminderDeliveryAction.qualifier()):
        reminder_delivery_interaction_handler = ReminderDeliveryInteractionHandler(
            source_interaction=interaction,
            context=CommandContext.DM,
            guild_settings=None,
            reminder_id=custom_id.split(ReminderDeliveryAction.qualifier() + '-', 1)[-1]
        )
        await reminder_delivery_interaction_handler.handle_action(action=interaction.data["values"][0])
    ### Role menu actions ###
    elif guild_settings and (role_menu := guild_settings.get_role_menu(message_id=message_id)):
        role_menu_interaction_handler = RoleMenuInteractionHandler(source_interaction=interaction,
                                                                   guild_settings=guild_settings,
                                                                   context=CommandContext.GUILD,
                                                                   role_menu=role_menu)
        await role_menu_interaction_handler.handle_action()
