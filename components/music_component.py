import cache
from components import BaseComponent
from components.asset_component import AssetComponent
from constants import DefinedAsset
from models.dto.radio_stream import RadioStream


class MusicComponent(BaseComponent):
    """
    Component to manage some music-and-radio-related functionalities.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def load_radio_streams(self):
        """
        Load radio streams from asset files into cache.
        """
        self.logger.debug("Loading radio streams from config files into cache.")
        asset_component = AssetComponent()
        radio_streams_data = await asset_component.get_json_asset(DefinedAsset.RADIO_STREAMS)
        for radio_stream_data in radio_streams_data:
            radio_stream = RadioStream.from_dict(radio_stream_data)
            cache.RADIO_STREAMS[radio_stream.code] = radio_stream
            if radio_stream.category not in cache.RADIO_STREAMS_BY_CATEGORY:
                cache.RADIO_STREAMS_BY_CATEGORY[radio_stream.category] = []
            cache.RADIO_STREAMS_BY_CATEGORY[radio_stream.category].append(radio_stream)
        self.logger.info(f"Loaded {len(cache.RADIO_STREAMS)} radio streams.")
