from components.integration_component import AnimangaProviderComponent
from services.urban_dictionary_service import UrbanDictionaryService

from models.dto.dictionary import UrbanDictionaryDefinition


class UrbanDictionaryComponent(AnimangaProviderComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ud_service = UrbanDictionaryService()

    async def get_definitions(self, term: str) -> list[UrbanDictionaryDefinition]:
        """
        Get definitions for a given term from Urban Dictionary.
        Args:
            term (str): The term to search for in Urban Dictionary.

        Returns:
            list[UrbanDictionaryDefinition]: A list of definitions for the term.
        """
        definitions = await self.ud_service.get_definitions(term)
        return UrbanDictionaryDefinition.from_many(data=definitions)
