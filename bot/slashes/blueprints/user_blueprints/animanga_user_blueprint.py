"""
Blueprint for anime/manga or MAL/AniList user slash commands.
"""
import discord
from discord import app_commands
from discord.app_commands import allowed_installs, allowed_contexts
from discord.ext.commands import Cog

from constants import CommandGroup
from bot.slashes.user_slashes.animanga_user_slashes import AnimangaUserSlashes
from strings.commands_strings import UserSlashCommandsStrings


class AnimangaUserBlueprint(Cog):
    LINK_MYANIMELIST = app_commands.command(name="link-myanimelist",
                                            description=UserSlashCommandsStrings.LINK_MYANIMELIST_DESCRIPTION,
                                            extras={"group": CommandGroup.ANIMANGA,
                                                    "listing_priority": 4})
    LINK_ANILIST = app_commands.command(name="link-anilist",
                                        description=UserSlashCommandsStrings.LINK_ANILIST_DESCRIPTION,
                                        extras={"group": CommandGroup.ANIMANGA,
                                                "listing_priority": 6})
    MYANIMELIST = app_commands.command(name="myanimelist",
                                       description=UserSlashCommandsStrings.MYANIMELIST_DESCRIPTION,
                                       extras={"group": CommandGroup.ANIMANGA,
                                               "listing_priority": 3,
                                               "aliases": ["mal"]})
    ANILIST = app_commands.command(name="anilist",
                                   description=UserSlashCommandsStrings.ANILIST_DESCRIPTION,
                                   extras={"group": CommandGroup.ANIMANGA,
                                           "listing_priority": 5,
                                           "aliases": ["al"]})
    MAL = app_commands.command(name="mal",
                               description=UserSlashCommandsStrings.MYANIMELIST_DESCRIPTION,
                               extras={"is_alias": True,
                                       "alias_for": "myanimelist",
                                       "group": CommandGroup.ANIMANGA,
                                       "listing_priority": 12})
    AL = app_commands.command(name="al",
                              description=UserSlashCommandsStrings.ANILIST_DESCRIPTION,
                              extras={"is_alias": True,
                                      "alias_for": "anilist",
                                      "group": CommandGroup.ANIMANGA,
                                      "listing_priority": 11})
    ANIME = app_commands.command(name="anime",
                                 description=UserSlashCommandsStrings.ANIME_DESCRIPTION,
                                 extras={"group": CommandGroup.ANIMANGA,
                                         "listing_priority": 1})
    MANGA = app_commands.command(name="manga",
                                 description=UserSlashCommandsStrings.MANGA_DESCRIPTION,
                                 extras={"group": CommandGroup.ANIMANGA,
                                         "listing_priority": 2})

    @LINK_MYANIMELIST
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def link_myanimelist(self, interaction: discord.Interaction, username: str):
        """Link your MyAnimeList username for stats & profile

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        username: str
            Your MyAnimeList username
        """

        await AnimangaUserSlashes(interaction=interaction).link_myanimelist(username=username)

    @LINK_ANILIST
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def link_anilist(self, interaction: discord.Interaction, username: str):
        """Link your Anilist username for stats & profile

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        username: str
            Your AniList username
        """

        await AnimangaUserSlashes(interaction=interaction).link_anilist(username=username)

    @MYANIMELIST
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def myanimelist(self,
                          interaction: discord.Interaction,
                          username: str = None,
                          member: discord.Member = None):
        """Get your MyAnimeList profile or someone else's

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        username: str
            MyAnimeList username if you want to get someone else's profile
        member: discord.Member
            Or get someone else's profile by selecting them
        """

        await AnimangaUserSlashes(interaction=interaction).myanimelist(username=username, member=member)

    @MAL
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mal(self,
                  interaction: discord.Interaction,
                  username: str = None,
                  member: discord.Member | discord.User = None):
        """Get your MyAnimeList profile (alias for /myanimelist)

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        username: str
            MyAnimeList username if you want to get someone else's profile
        member: discord.Member
            Or get someone else's profile by selecting them
        """

        await AnimangaUserSlashes(interaction=interaction).myanimelist(username=username, member=member)

    @ANILIST
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def anilist(self,
                      interaction: discord.Interaction,
                      username: str = None,
                      member: discord.Member | discord.User = None):
        """Get your AniList profile

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        username: str
            Anilist username if you want to get someone else's profile
        member: discord.Member
            Or get someone else's profile by selecting them
        """

        await AnimangaUserSlashes(interaction=interaction).anilist(username=username, member=member)

    @AL
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def al(self,
                 interaction: discord.Interaction,
                 username: str = None,
                 member: discord.Member = None):
        """Get your AniList profile (alias for /anilist)

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        username: str
            Anilist username if you want to get someone else's profile
        member: discord.Member
            Or get someone else's profile by selecting them
        """

        await AnimangaUserSlashes(interaction=interaction).anilist(username=username, member=member)

    @ANIME
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def anime(self, interaction: discord.Interaction, anime: str):
        """Get anime info with your stats

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        anime: str
            Anime name
        """

        await AnimangaUserSlashes(interaction=interaction).anime(anime=anime)

    @MANGA
    @allowed_installs(users=True, guilds=True)
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def manga(self, interaction: discord.Interaction, manga: str):
        """Get manga info with your stats

        Parameters
        -----------
        interaction: discord.Interaction
            Interaction to handle
        manga: str
            Manga name
        """

        await AnimangaUserSlashes(interaction=interaction).manga(manga=manga)
