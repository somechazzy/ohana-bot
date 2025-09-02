import re
from datetime import datetime


class UrbanDictionaryDefinition:
    def __init__(self,
                 term: str,
                 definition: str,
                 permalink: str,
                 author: str,
                 example: str | None,
                 thumbs_up: int,
                 thumbs_down: int,
                 created_on: datetime):
        self.term: str = term
        self.definition: str = definition
        self.permalink: str = permalink
        self.author: str = author
        self.example: str | None = example
        self.thumbs_up: int = thumbs_up
        self.thumbs_down: int = thumbs_down
        self.created_on: datetime = created_on

    @classmethod
    def from_dict(cls, data: dict) -> 'UrbanDictionaryDefinition':
        return cls(
            term=data['word'],
            definition=data['definition'],
            permalink=data['permalink'],
            author=data['author'],
            example=data.get('example'),
            thumbs_up=data['thumbs_up'],
            thumbs_down=data['thumbs_down'],
            created_on=datetime.fromisoformat(data['written_on'])
        )

    @classmethod
    def from_many(cls, data: list[dict]) -> list['UrbanDictionaryDefinition']:
        return [cls.from_dict(item) for item in data]


class MerriamWebsterDefinition:
    def __init__(self, is_offensive: bool, definitions: list[str], part_of_speech: str, dated_to: str):
        self.is_offensive: bool = is_offensive
        self.definitions: list[str] = definitions
        self.part_of_speech: str = part_of_speech
        self.dated_to: str = dated_to

    @classmethod
    def from_dict(cls, data: dict) -> 'MerriamWebsterDefinition':
        return cls(
            is_offensive=data.get('meta', {}).get('offensive', False),
            definitions=data.get('shortdef', []),
            part_of_speech=data.get('fl', '?'),
            dated_to=re.sub(r'\{.*?}', '', data.get('date', ''))
        )
