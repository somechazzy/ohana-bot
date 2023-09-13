import re
import traceback
import greenlet
from actions import send_embed
import asyncio
import json
import os
from datetime import datetime, timedelta
from actions import edit_message
from globals_.clients import discord_client
from utils.helpers import build_path
import discord
from discord import SelectOption, ButtonStyle, Interaction
from discord.ui import View, Select as SelectView, Button as ButtonView
from globals_.constants import BOT_OWNER_ID, Colour


class MusicCleanup:
    _path = ['media', 'music']
    _option_list = [
        "Cleanup tracks not used within 3 days",
        "Cleanup tracks not used within 7 days",
        "Cleanup tracks not used within 14 days",
        "Cleanup tracks not used within 30 days"
    ]

    async def handle_cleanup(self, received_message, ):
        _, opus_files, total_size, id_last_accessed_map = self._get_saved_music_stats()
        total_size_mb = self._convert_to_mb(total_size)
        current_time = datetime.utcnow()
        three_days_ago_ts = int((current_time - timedelta(days=3)).timestamp())
        seven_days_ago_ts = int((current_time - timedelta(days=7)).timestamp())
        fourteen_days_ago_ts = int((current_time - timedelta(days=14)).timestamp())
        thirty_days_ago_ts = int((current_time - timedelta(days=30)).timestamp())

        tracks_accessed_within_three_days = len(
            [0 for _, ts in id_last_accessed_map.items() if ts and ts >= three_days_ago_ts])
        tracks_accessed_within_seven_days = len(
            [0 for _, ts in id_last_accessed_map.items() if ts and ts >= seven_days_ago_ts])
        tracks_accessed_within_thirty_days = len(
            [0 for _, ts in id_last_accessed_map.items() if ts and ts >= thirty_days_ago_ts])
        tracks_accessed_within_fourteen_days = len(
            [0 for _, ts in id_last_accessed_map.items() if ts and ts >= fourteen_days_ago_ts])
        tracks_accessed_more_than_thirty_days_ago = len(
            [0 for _, ts in id_last_accessed_map.items() if ts and ts < thirty_days_ago_ts])

        embed = discord.Embed(title="Music Cleanup")
        embed.add_field(name="Stats",
                        value=f"Total audio files: {opus_files}\n"
                              f"Total size: {total_size_mb} MB\n")
        embed.add_field(name="Last accessed",
                        value=f"Within last 3 days: {tracks_accessed_within_three_days}\n"
                              f"Within last 7 days: {tracks_accessed_within_seven_days}\n"
                              f"Within last 14 days: {tracks_accessed_within_fourteen_days}\n"
                              f"Within last 30 days: {tracks_accessed_within_thirty_days}\n"
                              f"Not within last 30 days: {tracks_accessed_more_than_thirty_days_ago}\n",
                        inline=False)

        view = self._get_main_views()
        sent_message = await received_message.channel.send(embed=embed, view=view)
        action = await self._get_action(sent_message)
        if not action:
            return
        elif action == "Cleanup tracks not used within 3 days":
            estimation, tracks_to_remove = \
                self._get_tracks_not_used_within_last(days=3,
                                                      total_size=total_size,
                                                      id_last_accessed_map=id_last_accessed_map)
        elif action == "Cleanup tracks not used within 7 days":
            estimation, tracks_to_remove = \
                self._get_tracks_not_used_within_last(days=7,
                                                      total_size=total_size,
                                                      id_last_accessed_map=id_last_accessed_map)
        elif action == "Cleanup tracks not used within 14 days":
            estimation, tracks_to_remove = \
                self._get_tracks_not_used_within_last(days=14,
                                                      total_size=total_size,
                                                      id_last_accessed_map=id_last_accessed_map)
        elif action == "Cleanup tracks not used within 30 days":
            estimation, tracks_to_remove = \
                self._get_tracks_not_used_within_last(days=30,
                                                      total_size=total_size,
                                                      id_last_accessed_map=id_last_accessed_map)
        else:
            return

        embed = discord.Embed(description=f"**{action}**\n"
                                          f"Estimated size to free up: {estimation} MB\n"
                                          f"Tracks to be removed: {len(tracks_to_remove)}",
                              title="Music Cleanup")
        sent_message = received_message.channel.get_partial_message(sent_message.id)
        view = self._get_confirmation_views()
        await edit_message(sent_message, None, embed=embed, view=view)

        action = await self._get_final_action(sent_message)
        if not action:
            return
        elif action == 'confirm':
            self._erase_tracks(ids=tracks_to_remove)
            sent_message = received_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, "Done", view=None)

    def _get_saved_music_stats(self):
        total_size = 0
        total_files = 0
        opus_files = 0
        id_last_accessed_map = {}
        directory = build_path(self._path)
        for entry in os.scandir(directory):
            if entry.is_file():
                total_files += 1
                opus_files += 1 if entry.name.endswith(".opus") else 0
                if entry.name.endswith(".json"):
                    with open(entry.path, 'r') as file:
                        track_details = json.load(file)
                        id_last_accessed_map[entry.name[:-5]] = track_details.get('last_accessed')
                total_size += entry.stat().st_size
        return total_files, opus_files, total_size, id_last_accessed_map

    def _get_main_views(self):
        view = View(timeout=300)
        options = [SelectOption(label=option, value=option) for option in self._option_list]
        view.add_item(SelectView(options=options))
        view.add_item(ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close"))
        return view

    def _get_confirmation_views(self):
        view = View(timeout=300)
        view.add_item(ButtonView(label="Confirm", style=ButtonStyle.green, custom_id="confirm"))
        view.add_item(ButtonView(label="Close", emoji='🗑', style=ButtonStyle.gray, custom_id="close"))
        return view

    async def _get_action(self, sent_message):

        def check_help_interactions(interaction_: Interaction):
            if not interaction_.message or interaction_.message.id != sent_message.id:
                return False
            if interaction_.user.id != BOT_OWNER_ID:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            return True

        try:
            interaction = await discord_client.wait_for("INTERACTION",
                                                        check=check_help_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, "closed", embed=None, view=None)
            return

        await interaction.response.defer()
        if interaction.data.get('custom_id', None) == 'close':
            await interaction.edit_original_response(content="closed", embed=None, view=None)
            return None

        return interaction.data.get('values', [])[0] \
            if interaction.data.get('values', []) and interaction.data.get('values', [])[0] in self._option_list \
            else None

    def _convert_to_mb(self, size):
        return int(size / (1024 * 1024))

    def _get_tracks_not_used_within_last(self, days, total_size, id_last_accessed_map):
        total_tracks = len(id_last_accessed_map)
        if not days:
            ids = [id_ for id_, ts in id_last_accessed_map.items() if not ts]
            estimated_size = (len(ids) / total_tracks) * total_size
            return self._convert_to_mb(estimated_size), ids

        current_time = datetime.utcnow()
        days_ago_ts = int((current_time - timedelta(days=days)).timestamp())

        ids = [id_ for id_, ts in id_last_accessed_map.items() if ts and ts < days_ago_ts]
        estimated_size = (len(ids) / total_tracks) * total_size
        return self._convert_to_mb(estimated_size), ids

    async def _get_final_action(self, sent_message):

        def check_help_interactions(interaction_: Interaction):
            if not interaction_.message or interaction_.message.id != sent_message.id:
                return False
            if interaction_.user.id != BOT_OWNER_ID:
                asyncio.get_event_loop().create_task(interaction_.response.defer())
                return False
            return True

        try:
            interaction = await discord_client.wait_for("INTERACTION",
                                                        check=check_help_interactions,
                                                        timeout=300)
        except asyncio.TimeoutError:
            sent_message = sent_message.channel.get_partial_message(sent_message.id)
            await edit_message(sent_message, "closed", embed=None, view=None)
            return

        await interaction.response.defer()
        if interaction.data.get('custom_id', None) == 'close':
            await interaction.edit_original_response(content="closed", embed=None, view=None)
            return None
        return interaction.data.get('custom_id', None)

    def _erase_tracks(self, ids):
        for id_ in ids:
            json_file = build_path(self._path + [id_ + ".json"])
            opus_file = build_path(self._path + [id_ + ".opus"])

            if os.path.exists(json_file):
                os.remove(json_file)
            if os.path.exists(opus_file):
                os.remove(opus_file)


class GreenAwait:
    def __init__(self, child):
        self.current = greenlet.getcurrent()
        self.value = None
        self.child = child

    def __call__(self, future):
        self.value = future
        self.current.switch()

    def __iter__(self):
        while self.value is not None:
            yield self.value
            self.value = None
            self.child.switch()


def gexec(code):
    child = greenlet.greenlet(exec)
    gawait = GreenAwait(child)
    child.switch(code, {'gawait': gawait})
    yield from gawait


async def aexec(code, message):
    green = greenlet.greenlet(gexec)
    code_lines = '\t'.join(code.splitlines(keepends=True))
    final_code = f'''
from actions import send_embed, send_message
from globals_.clients import discord_client
from globals_.constants import Colour
async def code_to_execute():
\tthis_channel = discord_client.get_channel({message.channel.id})
\toutputs={{}}
\t{code_lines}
\tfeedback = f"Code executed; no output given." if len(outputs) == 0 else "Code executed\\n\\n"
\tfor output in outputs:
\t    feedback += f"{{output}}: {{outputs[output]}}\\n"
\tawait send_embed(feedback.strip(), this_channel, emoji="🚀", color=Colour.SYSTEM, logging=False)
gawait(code_to_execute())
    '''
    gen = green.switch(final_code)
    for future in gen:
        await future


async def execute_owner_code_snippet(message):
    code_matches = re.findall("```python[\n]?[\\s\\S]+[\n]?```", message.content)
    if len(code_matches) == 0:
        code_matches = re.findall("```[\n]?[\\s\\S]+[\n]?```", message.content)
        if len(code_matches) == 0:
            return
        code = code_matches[0][3:len(code_matches[0])-3]
    else:
        code = code_matches[0][9:len(code_matches[0])-3]
    outputs = {}
    try:
        await aexec(code.strip(), message)
    except Exception as e:
        outputs["error"] = f"{e.__doc__}\n{e.__str__()}\n{e.__traceback__}\n{e.__cause__}\n\n{(traceback.format_exc())}"
        feedback = "Code executed\n\n"
        for output in outputs:
            feedback += f"{output}: {outputs[output]}\n"
        await send_embed(feedback.strip(), message.channel, emoji="🚀", color=Colour.SYSTEM, logging=False)
