import asyncio
from datetime import datetime

from components.music_components.base_music_component import MusicComponent
from globals_.clients import firebase_client
from globals_.constants import MusicLogAction, COUNTABLE_MUSIC_LOG_ACTIONS
from models.music_library import MusicLog

guild_id_lock_map = dict()


class MusicLoggerComponent(MusicComponent):

    def __init__(self, guild_id=None, actor_id=None, actor_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild_id = guild_id
        self.actor_id = actor_id
        self.actor_name = actor_name
        self.firebase_client = firebase_client

    async def log_music_action(self, action, context_count=1, context_value=None, timestamp=None):
        if not self.guild_id or not self.actor_id or not self.actor_name:
            raise Exception("Guild ID, actor ID and actor name must be provided in the constructor for logging.")
        if self.guild_id not in guild_id_lock_map:
            guild_id_lock_map[self.guild_id] = asyncio.Lock()
        async with guild_id_lock_map[self.guild_id]:
            logs = await self.get_guild_music_logs(guild_id=self.guild_id)
            if logs and logs[-1].actor_id == self.actor_id and logs[-1].action == action and \
                    action in COUNTABLE_MUSIC_LOG_ACTIONS:
                logs[-1].context_count += context_count
            else:
                music_log = MusicLog(actor_id=self.actor_id, actor_name=self.actor_name, action=action,
                                     context_count=context_count, context_value=context_value, timestamp=timestamp)
                logs.append(music_log)
            await self.firebase_client.set_guild_music_logs(guild_id=self.guild_id,
                                                            music_logs=MusicLog.to_json_list(logs[-50:]))

    async def get_guild_music_logs(self, guild_id):
        music_logs_json = await self.firebase_client.get_guild_music_logs(guild_id=guild_id)
        if not music_logs_json:
            return []
        return MusicLog.from_json_list(music_logs_json)

    async def get_guild_music_logs_readable_and_stylized(self, guild_id):
        music_logs = await self.get_guild_music_logs(guild_id=guild_id)
        if not music_logs:
            return []
        result = []
        for log in music_logs:
            if log.action == MusicLogAction.CONNECTED_BOT:
                log_text = f"**{log.actor_name}** connected **bot** to VC."
            elif log.action == MusicLogAction.SWITCHED_TO_RADIO:
                log_text = f"**{log.actor_name}** switched to **radio** mode."
            elif log.action == MusicLogAction.SWITCHED_TO_PLAYER:
                log_text = f"**{log.actor_name}** switched to **player** mode."
            elif log.action == MusicLogAction.DISCONNECTED_BOT:
                log_text = f"**{log.actor_name}** disconnected **bot** from VC."
            elif log.action == MusicLogAction.ADDED_TRACK:
                if log.context_count == 1:
                    log_text = f"**{log.actor_name}** added one track to the queue."
                else:
                    log_text = f"**{log.actor_name}** added {log.context_count} tracks to the queue."
            elif log.action == MusicLogAction.REMOVED_TRACK:
                if log.context_count == 1:
                    log_text = f"**{log.actor_name}** removed one track from the queue."
                else:
                    log_text = f"**{log.actor_name}** removed {log.context_count} tracks from the queue."
            elif log.action == MusicLogAction.SKIPPED_TRACK:
                if log.context_count == 1:
                    log_text = f"**{log.actor_name}** skipped one track."
                else:
                    log_text = f"**{log.actor_name}** skipped {log.context_count} tracks."
            elif log.action == MusicLogAction.MOVED_TRACK:
                if log.context_count == 1:
                    log_text = f"**{log.actor_name}** moved one track."
                else:
                    log_text = f"**{log.actor_name}** moved {log.context_count} tracks."
            elif log.action == MusicLogAction.TRACK_SEEK:
                log_text = f"**{log.actor_name}** seeked a track ({log.context_value})."
            elif log.action == MusicLogAction.REPLAYED_TRACK:
                if log.context_count == 1:
                    log_text = f"**{log.actor_name}** replayed one track."
                else:
                    log_text = f"**{log.actor_name}** replayed a track/tracks {log.context_count} times."
            elif log.action == MusicLogAction.CLEARED_QUEUE:
                log_text = f"**{log.actor_name}** cleared the queue with {log.context_value} tracks in it."
            elif log.action == MusicLogAction.CHANGED_LOOP_MODE:
                log_text = f"**{log.actor_name}** changed loop mode to **{log.context_value}**."
            elif log.action == MusicLogAction.SHUFFLED_QUEUE:
                if log.context_count == 1:
                    log_text = f"**{log.actor_name}** shuffled the queue."
                else:
                    log_text = f"**{log.actor_name}** shuffled the queue {log.context_count} times."
            elif log.action == MusicLogAction.CHANGED_RADIO_STREAM:
                log_text = f"**{log.actor_name}** changed radio stream to **{log.context_value}**."
            elif log.action == MusicLogAction.FORCE_PLAYED_TRACK:
                if log.context_count == 1:
                    log_text = f"**{log.actor_name}** force played one track."
                else:
                    log_text = f"**{log.actor_name}** force played a track/tracks {log.context_count} times."
            elif log.action == MusicLogAction.PAUSED_PLAYBACK:
                log_text = f"**{log.actor_name}** paused playback."
            elif log.action == MusicLogAction.RESUMED_PLAYBACK:
                log_text = f"**{log.actor_name}** resumed playback."
            else:
                raise Exception(f"Unknown action {log.action} in music log.")

            log_text += f" (<t:{int(log.timestamp)}:R>)"
            result.append(log_text)

        return result
