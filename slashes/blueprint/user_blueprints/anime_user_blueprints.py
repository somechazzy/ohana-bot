from typing import Union

import discord
from discord import app_commands
from discord.ext.commands import Cog

from slashes.user_slashes.anime_user_slashes import AnimeUserSlashes


class AnimeUserBlueprints(Cog):
    LINK_MYANIMELIST = app_commands.command(name="link-myanimelist",
                                            description="Link your MyAnimeList username for stats & profile")
    LINK_ANILIST = app_commands.command(name="link-anilist",
                                        description="Link your AniList username for stats & profile")
    MYANIMELIST = app_commands.command(name="myanimelist",
                                       description="Get your MyAnimeList profile or someone else's")
    ANILIST = app_commands.command(name="anilist",
                                   description="Get your AniList profile or someone else's")
    MAL = app_commands.command(name="mal",
                               description="Get your MyAnimeList profile or someone else's",
                               extras={"is_alias": True, "alias_for": "myanimelist"})
    AL = app_commands.command(name="al",
                              description="Get your AniList profile or someone else's",
                              extras={"is_alias": True, "alias_for": "anilist"})
    ANIME = app_commands.command(name="anime",
                                 description="Get anime info with your stats")
    MANGA = app_commands.command(name="manga",
                                 description="Get manga info with your stats")

    @LINK_MYANIMELIST
    async def link_myanimelist(self, inter, username: str):
        """Link your MyAnimeList username for stats & profile

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        username: str
            Your MyAnimeList username
        """

        await AnimeUserSlashes(interaction=inter).link_myanimelist(username=username)

    @LINK_ANILIST
    async def link_anilist(self, inter, username: str):
        """Link your Anilist username for stats & profile

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        username: str
            Your AniList username
        """

        await AnimeUserSlashes(interaction=inter).link_anilist(username=username)

    @MYANIMELIST
    async def myanimelist(self, inter, username: str = None, member: discord.Member = None, unlock: bool = True):
        """Get your MyAnimeList profile or someone else's

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        username: str
            MyAnimeList username if you want to get someone else's profile
        member: discord.Member
            Or get someone else's profile by selecting them
        unlock: bool
            Unlock for others to navigate through the profile (default: True)
        """

        await AnimeUserSlashes(interaction=inter).myanimelist(username=username, member=member, unlock=unlock)

    @MAL
    async def mal(self, inter, username: str = None, member: Union[discord.Member, discord.User] = None,
                  unlock: bool = True):
        """Get your MyAnimeList profile (alias for /myanimelist)

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        username: str
            MyAnimeList username if you want to get someone else's profile
        member: discord.Member
            Or get someone else's profile by selecting them
        unlock: bool
            Unlock for others to navigate through the profile (default: True)
        """

        await AnimeUserSlashes(interaction=inter).myanimelist(username=username, member=member, unlock=unlock)

    @ANILIST
    async def anilist(self, inter, username: str = None, member: Union[discord.Member, discord.User] = None,
                      unlock: bool = True):
        """Get your AniList profile

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        username: str
            Anilist username if you want to get someone else's profile
        member: discord.Member
            Or get someone else's profile by selecting them
        unlock: bool
            Unlock for others to navigate through the profile (default: True)
        """

        await AnimeUserSlashes(interaction=inter).anilist(username=username, member=member, unlock=unlock)

    @AL
    async def al(self, inter, username: str = None, member: discord.Member = None, unlock: bool = True):
        """Get your AniList profile (alias for /anilist)

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        username: str
            Anilist username if you want to get someone else's profile
        member: discord.Member
            Or get someone else's profile by selecting them
        unlock: bool
            Unlock for others to navigate through the profile (default: True)
        """

        await AnimeUserSlashes(interaction=inter).anilist(username=username, member=member, unlock=unlock)

    @ANIME
    async def anime(self, inter, anime: str):
        """Get anime info with your stats

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        anime: str
            Anime name
        """

        await AnimeUserSlashes(interaction=inter).anime(anime=anime)

    @MANGA
    async def manga(self, inter, manga: str):
        """Get manga info with your stats

        Parameters
        -----------
        inter: Interaction
            Interaction to handle
        manga: str
            Manga name
        """

        await AnimeUserSlashes(interaction=inter).manga(manga=manga)
