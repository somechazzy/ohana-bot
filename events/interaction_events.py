from auto_moderation.role_management import handle_role_menu_interaction
from globals_ import shared_memory
from globals_.clients import discord_client
from globals_.constants import SUPPORTED_PLAYER_ACTION_IDS, SUPPORTED_RADIO_ACTION_IDS
import discord

from user_interactions.music_interactions.music_player_interactions_handler import MusicPlayerInteractionsHandler
from user_interactions.music_interactions.music_radio_interactions_handler import MusicRadioInteractionsHandler
from user_interactions.user_interactions.reminder_interactions_handler import ReminderInteractionsHandler

client = discord_client


@client.event
async def on_interaction(interaction: discord.Interaction):
    if not interaction.message or interaction.message.author.id != client.user.id:
        return

    await handle_music_interaction(interaction=interaction)
    await handle_main_interaction(interaction=interaction)


async def handle_music_interaction(interaction):
    if not interaction.guild:
        return
    music_player_message_id = shared_memory.guilds_prefs[interaction.guild.id].music_player_message
    if interaction.message.id == music_player_message_id and 'custom_id' in interaction.data:
        if interaction.data['custom_id'] in SUPPORTED_PLAYER_ACTION_IDS:
            await MusicPlayerInteractionsHandler(source_interaction=interaction) \
                .handle_action(action=interaction.data["custom_id"])
        elif interaction.data['custom_id'] in SUPPORTED_RADIO_ACTION_IDS:
            await MusicRadioInteractionsHandler(source_interaction=interaction) \
                .handle_action(action=interaction.data["custom_id"])


async def handle_main_interaction(interaction):
    await handle_role_menu_interaction(interaction=interaction)
    if "custom_id" in interaction.data and interaction.data["custom_id"] == "snooze_reminder_select":
        await ReminderInteractionsHandler(source_interaction=interaction).handle_snooze()
