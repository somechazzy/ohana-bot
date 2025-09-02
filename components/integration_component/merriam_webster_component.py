from components.integration_component import AnimangaProviderComponent
from services.merriam_webster_service import MerriamWebsterService

from models.dto.dictionary import MerriamWebsterDefinition


class MerriamWebsterComponent(AnimangaProviderComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mw_service = MerriamWebsterService()

    async def get_definition(self, term: str) -> MerriamWebsterDefinition:
        """
        Get definition for a given term from
        Args:
            term (str): The term to search for in merriam-webster dictionary.

        Returns:
            MerriamWebsterDefinition: A definition for the term.
        """
        definitions = await self.mw_service.get_definitions(term)
        return MerriamWebsterDefinition.from_dict(data=definitions[0]) if definitions else None
