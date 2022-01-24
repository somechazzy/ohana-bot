import asyncio
from math import ceil

from actions import edit_message
from globals_.clients import discord_client
from helpers import get_pagination_views
from embed_factory import make_leaderboard_embed


async def handle_leaderboard_navigation(sent_message, members_xp, requested_by, page):
    embed = make_leaderboard_embed(members_xp=members_xp, requested_by=requested_by, page=page)
    page_count = ceil(len(members_xp) / 10)
    if page > page_count:
        page = 1
    while True:
        def check_leaderboard_interactions(interaction_):
            if interaction_.message.id != sent_message.id:
                return False
            if interaction_.data.custom_id == 'close' and interaction_.user.id != requested_by.id:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            return True

        try:
            interaction = await discord_client.wait_for("MESSAGE_INTERACTION",
                                                        check=check_leaderboard_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, None, embed=embed, view=None)
            return

        if interaction.data.custom_id == 'close':
            await interaction.response.defer()
            await interaction.edit_original_message(content="Leaderboard closed.", embed=None, view=None)
            return
        elif interaction.data.custom_id == 'next':
            if page < page_count:
                page += 1
        elif interaction.data.custom_id == 'previous':
            if page > 1:
                page -= 1

        embed = make_leaderboard_embed(members_xp=members_xp, requested_by=requested_by, page=page)
        view = get_pagination_views(page, page_count)
        await interaction.response.defer()
        await interaction.edit_original_message(content=None, embed=embed, view=view)
