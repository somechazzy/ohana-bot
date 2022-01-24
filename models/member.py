import time


class MemberXP:

    def __init__(self, member_id: int):
        self._member_id = int(member_id)
        self._member_tag = f"({member_id})"
        self._messages = 0

        self._xp = 0
        self._timeframe_ts = -1

        self._xp_decayed = 0
        self._last_message_ts = int(time.time()) - time.altzone
        self._ts_of_last_decay = -1

        self._level = 0
        self._last_sent_level = -1
        self.is_synced = True

    @property
    def member_id(self):
        return self._member_id

    @property
    def member_tag(self):
        return self._member_tag

    def set_member_tag(self, member_tag):
        self._member_tag = member_tag
        self.is_synced = False

    @property
    def messages(self):
        return self._messages

    def set_messages(self, messages):
        self._messages = int(messages)
        self.is_synced = False

    def increment_messages(self):
        self._messages += 1
        self.is_synced = False

    @property
    def xp(self):
        return self._xp

    def set_xp(self, xp):
        self._xp = int(float(xp))
        self.is_synced = False

    def add_xp(self, xp):
        self._xp += xp
        self.is_synced = False

    @property
    def timeframe_ts(self):
        return self._timeframe_ts

    def set_timeframe_ts(self, timeframe_ts):
        self._timeframe_ts = int(timeframe_ts)
        self.is_synced = False
        
    @property
    def xp_decayed(self):
        return self._xp_decayed

    def set_xp_decayed(self, xp_decayed):
        self._xp_decayed = int(xp_decayed)
        self.is_synced = False

    def decay_xp(self, xp, only_add_to_decayed_variable=False):
        if not only_add_to_decayed_variable:
            self._xp -= xp
        self._xp_decayed += xp
        self.is_synced = False
        
    @property
    def last_message_ts(self):
        return self._last_message_ts

    def set_last_message_ts(self, last_message_ts):
        if int(last_message_ts) == -1:
            last_message_ts = int(time.time()) - time.altzone - 24*60*60
        self._last_message_ts = int(last_message_ts)
        self.is_synced = False
        
    @property
    def ts_of_last_decay(self):
        return self._ts_of_last_decay

    def set_ts_of_last_decay(self, ts_of_last_decay):
        self._ts_of_last_decay = int(ts_of_last_decay)
        self.is_synced = False
        
    @property
    def level(self):
        return self._level

    def set_level(self, level):
        self._level = int(level)
        self.is_synced = False
        
    @property
    def last_sent_level(self):
        return self._last_sent_level

    def set_last_sent_level(self, last_sent_level):
        self._last_sent_level = int(last_sent_level)
        self.is_synced = False

    def stringify_values(self):
        self._member_id = str(self._member_id)
        self._messages = str(self._messages)
        self._xp = str(self._xp)
        self._timeframe_ts = str(self._timeframe_ts)
        self._xp_decayed = str(self._xp_decayed)
        self._last_message_ts = str(self._last_message_ts)
        self._ts_of_last_decay = str(self._ts_of_last_decay)
        self._level = str(self._level)
        self._last_sent_level = str(self._last_sent_level)
        return self

    def destringify_values(self):
        self._member_id = int(self._member_id)
        self._messages = int(self._messages)
        self._xp = int(self._xp)
        self._timeframe_ts = int(self._timeframe_ts)
        self._xp_decayed = int(self._xp_decayed)
        self._last_message_ts = int(self._last_message_ts)
        self._ts_of_last_decay = int(self._ts_of_last_decay)
        self._level = int(self._level)
        self._last_sent_level = int(self._last_sent_level)
        return self
