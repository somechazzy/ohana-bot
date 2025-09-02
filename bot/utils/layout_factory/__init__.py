"""
Base class for all layout views.
"""
from discord.ui import LayoutView


class BaseLayout(LayoutView):

    def __init__(self, interactions_handler, **kwargs):
        super().__init__(**kwargs)
        self.interactions_handler = interactions_handler
