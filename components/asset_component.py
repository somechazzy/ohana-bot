import json
from io import BytesIO

from PIL import Image
import aiofiles
from components import BaseComponent


class AssetComponent(BaseComponent):
    """
    Component for reading and managing static assets, as well as any files within the project.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_asset(self, defined_asset: str) -> bytes:
        """
        Returns the bytes object of the asset with the given name.
        Args:
            defined_asset (str): The defined asset path.

        Returns:
            bytes: The bytes object of the asset.
        """
        self.logger.debug(f"Reading asset \"{defined_asset}\"")
        async with aiofiles.open(defined_asset, mode='rb') as asset_file:
            return await asset_file.read()

    async def get_json_asset(self, defined_asset: str) -> dict:
        """
        Returns the JSON object of the asset with the given name.
        Args:
            defined_asset (str): The defined asset path.

        Returns:
            dict: The JSON object of the asset.
        """
        return json.loads((await self.get_asset(defined_asset)).decode('utf-8'))

    async def get_image_asset(self, defined_asset: str) -> Image.Image:
        """
        Returns the image object of the asset with the given name.
        Args:
            defined_asset (str): The defined asset path.
        Returns:
            Image.Image: The image object of the asset.
        """
        return Image.open(BytesIO(await self.get_asset(defined_asset)))
