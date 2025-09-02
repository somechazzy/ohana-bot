import discord

from constants import Colour, Links
from models.dto.dictionary import UrbanDictionaryDefinition, MerriamWebsterDefinition


def get_urban_dictionary_definition_embed(definitions: list[UrbanDictionaryDefinition],
                                          page: int,
                                          page_count: int) -> discord.Embed:
    """
    Create an embed for an Urban Dictionary definition.
    Args:
        definitions (list[UrbanDictionaryDefinition]): List of definitions to choose from.
        page (int): Current page number (1-indexed).
        page_count (int): Total number of pages.
    Returns:
        discord.Embed: The created embed.
    """
    definition = definitions[page - 1]
    embed = discord.Embed(colour=Colour.EXT_URBAN, description=f"{definition.definition}",
                          timestamp=definition.created_on)

    embed.set_author(name=definition.term, url=definition.permalink,
                     icon_url=Links.Media.URBAN_DICTIONARY_LOGO)
    embed.set_footer(text=f"Definition by {definition.author} | Page {page}/{page_count}")

    if definition.example:
        embed.add_field(name="Example", value=f"{definition.example}\n", inline=False)
    embed.add_field(name="‎‎‎", value=f"{definition.thumbs_up} 👍 | 👎 {definition.thumbs_down}", inline=False)

    return embed


def get_merriam_webster_definition_embed(term: str, definition: MerriamWebsterDefinition) -> discord.Embed:
    """
    Create an embed for a Merriam-Webster definition.
    Args:
        term (str): The term being defined.
        definition (MerriamWebsterDefinition): The definition object.
    Returns:
        discord.Embed: The created embed.
    """
    description = f"***{definition.part_of_speech}***\n"
    definition_text = '\n'.join(definition.definitions)
    if definition.is_offensive:
        definition_text = f"**[Potentially offensive]** ||{definition_text}||"
    description += definition_text
    embed = discord.Embed(colour=Colour.EXT_URBAN, description=description)

    embed.set_author(name=term, url=Links.MERRIAM_WEBSTER_DEFINITION_URL.format(term=term),
                     icon_url=Links.Media.MERRIAM_WEBSTER_LOGO)

    embed.set_footer(text=f"Dated: {definition.dated_to}")

    return embed
