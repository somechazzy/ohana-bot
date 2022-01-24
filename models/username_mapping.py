
class UsernameMapping:
    def __init__(self, discord_id: int, username: str):
        self._discord_id = discord_id
        self._username = username

    @property
    def username(self):
        return self._username

    def set_username(self, username: str):
        self._username = username

    @property
    def discord_id(self):
        return self._discord_id

    def set_discord_id(self, discord_id: str):
        self._discord_id = discord_id
