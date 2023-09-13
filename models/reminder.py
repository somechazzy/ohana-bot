
class Reminder:
    def __init__(self, timestamp, reason, user_id, db_key):
        self.timestamp = timestamp
        self.reason = reason
        self.user_id = int(user_id)
        self.db_key = db_key

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __gt__(self, other):
        return self.timestamp > other.timestamp
