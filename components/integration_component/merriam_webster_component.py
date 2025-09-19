from common.exceptions import ExternalServiceException, UserInputException
from components.integration_component import AnimangaProviderComponent
from services.merriam_webster_service import MerriamWebsterService

from models.dto.dictionary import MerriamWebsterDefinition


class MerriamWebsterComponent(AnimangaProviderComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mw_service = MerriamWebsterService()

    async def get_definition(self, term: str) -> MerriamWebsterDefinition | None:
        """
        Get definition for a given term from
        Args:
            term (str): The term to search for in merriam-webster dictionary.

        Returns:
            MerriamWebsterDefinition | None: A definition for the term, or None if not found.
        Raises:
            UserInputException: If no definitions are found for the term.
            ExternalServiceException: If there is an error with the external service,
                or the response format is unexpected.
        """
        definitions = await self.mw_service.get_definitions(term)
        if not definitions:
            return None
        if isinstance(definitions[0], str):  # invalid term, suggestions received instead
            raise UserInputException(f"No definitions found for '{term}'.\n"
                                     f"Suggestions: `{'`, `'.join(definitions[:5])}`")
        elif not isinstance(definitions[0], dict):
            raise ExternalServiceException(message="Unexpected response format from Merriam-Webster API",
                                           user_message="There was an error getting the definition"
                                                        " from Merriam-Webster Dictionary.",
                                           status_code=200,
                                           debugging_info={"response": definitions},
                                           alert_worthy=True)
        return MerriamWebsterDefinition.from_dict(data=definitions[0])
