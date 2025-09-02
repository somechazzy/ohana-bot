"""
Templates for custom extensions handling interaction-related events.
"""
import discord

from . import _BaseEventHandler


class BaseOnInteractionEventHandler(_BaseEventHandler):
    """
    Base template for on-interaction event handlers.

    Attributes:
        interaction (discord.Interaction): The interaction that triggered the event.
    """
    def __init__(self, interaction: discord.Interaction, **kwargs):
        super().__init__(**kwargs)
        self.interaction: discord.Interaction = interaction
