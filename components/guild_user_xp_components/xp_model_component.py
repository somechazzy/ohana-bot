from components.asset_component import AssetComponent
from components.guild_user_xp_components import BaseGuildUserXPComponent
from constants import DefinedAsset
import cache


class XPModelComponent(BaseGuildUserXPComponent):

    async def load_xp_model(self):
        """
        Load XP model for levels requirement from config files into cache.
        Returns:
            None
        """
        self.logger.debug("Loading XP model into cache")
        asset_component = AssetComponent()
        xp_model = await asset_component.get_json_asset(
            DefinedAsset.XPAssets.XP_REQUIREMENTS_MODEL
        )
        for key, value in xp_model.items():
            cache.LEVEL_XP_MAP[int(key)] = int(value)
            cache.XP_LEVEL_MAP[int(value)] = int(key)
