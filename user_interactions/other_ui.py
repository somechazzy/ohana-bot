import asyncio
from actions import edit_message
from globals_.clients import discord_client
from helpers import get_pagination_views
from embed_factory import make_urban_embed


async def urban_navigation(sent_message, definition_list: list):
    total_pages = len(definition_list)
    i = 1
    embed = make_urban_embed(definition_list[i - 1], i, total_pages)
    while True:
        def check_urban_interactions(interaction_):
            if interaction_.message.id != sent_message.id:
                return False
            return True

        try:
            interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                        check=check_urban_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, None, embed=embed, view=None)
            return

        if interaction.data.custom_id == 'next':
            if i < total_pages:
                i += 1
        elif interaction.data.custom_id == 'previous':
            if i > 1:
                i -= 1

        embed = make_urban_embed(definition_list[i - 1], i, total_pages)
        view = get_pagination_views(i, total_pages, add_close_button=False)
        await interaction.response.defer()
        await interaction.edit_original_message(content=None, embed=embed, view=view)


async def handle_general_close_embed(sent_message, requested_by):
    def check_interactions(interaction_):
        if interaction_.message.id != sent_message.id:
            return False
        if interaction_.user.id != requested_by.id:
            asyncio.get_event_loop().create_task(interaction_.response.defer())
            return False
        return True

    try:
        interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                    check=check_interactions,
                                                    timeout=300)
    except asyncio.TimeoutError:
        return False

    if interaction.data.custom_id == 'close':
        await interaction.response.defer()
        return True
