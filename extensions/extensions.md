
# Quick guide to extensions

* Extensions can be structured in any way in this directory as long as it's outside `templates` directory.
* All extensions must be in the form of a class that inherits a particular event's template class.
* Each of these classes must implement `check` and `handle_event` methods. 
  * Your extension's event handler will be called if `check` returns `True`.
  * Your check method should be as lightweight as possible.
* Example usage:

```python
import discord

from constants import Colour
from extensions.templates.events.guild_events import BaseOnGuildJoinEventHandler
from settings import BOT_OWNER_ID


class WelcomeMessageOnGuildJoin(BaseOnGuildJoinEventHandler):
    async def check(self) -> bool:
        return self.guild.owner_id == BOT_OWNER_ID

    async def handle_event(self):
        for channel in self.guild.text_channels:
            permissions = channel.permissions_for(self.guild.me)
            if permissions.send_messages and permissions.embed_links:
                await channel.send(embed=discord.Embed(colour=Colour.PRIMARY_ACCENT,
                                                       description="Thanks for adding me to your server! "
                                                                   "Use `/help` to get started."))
                break
```