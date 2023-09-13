from globals_.constants import AnilistStatus


class DummyAnilistProfile:

    def __init__(self, status):
        self._status = status

    @property
    def status(self):
        return self._status

    def set_status(self, status: int):
        self._status = status


class AnilistProfile:
    def __init__(self, data):
        self.status = 200
        self._data = data.get('data').get('User')
        self.id: int
        self.name: str
        self.avatar: str
        self.site_url: str
        self.banner: str
        self.created_at: int
        self.updated_at: int
        self._set_basic_info()
        self.favourites: FavouritesV2
        self._set_favourites()
        self.anime_stats: AnimeStats
        self.manga_stats: MangaStats
        self._set_stats()
        self.anilysis: Anilysis
        self.mangalysis: Mangalysis
        self._set_analyses()

    def _set_basic_info(self):
        self.id = self._data.get('id')
        self.name = self._data.get('name')
        self.avatar = self._data.get('avatar', {}).get('medium')
        self.site_url = self._data.get('siteUrl')
        self.banner = self._data.get('bannerImage')
        self.created_at = self._data.get('createdAt')
        self.updated_at = self._data.get('updatedAt')

    def _set_favourites(self):
        anime_favorites = [
            FavouriteV2(english_title=fav_node.get('title', {}).get('english'),
                        romaji_title=fav_node.get('title', {}).get('romaji'),
                        site_url=fav_node.get('siteUrl'))
            for fav_node in self._data.get('favourites', {}).get('anime', {}).get('nodes', [])
        ]
        manga_favorites = [
            FavouriteV2(english_title=fav_node.get('title', {}).get('english'),
                        romaji_title=fav_node.get('title', {}).get('romaji'),
                        site_url=fav_node.get('siteUrl'))
            for fav_node in self._data.get('favourites', {}).get('manga', {}).get('nodes', [])
        ]
        character_favorites = [
            FavouriteV2(english_title='',
                        romaji_title=fav_node.get('name', {}).get('full'),
                        site_url=fav_node.get('siteUrl'))
            for fav_node in self._data.get('favourites', {}).get('characters', {}).get('nodes', [])
        ]
        staff_favorites = [
            FavouriteV2(english_title='',
                        romaji_title=fav_node.get('name', {}).get('full'),
                        site_url=fav_node.get('siteUrl'))
            for fav_node in self._data.get('favourites', {}).get('staff', {}).get('nodes', [])
        ]
        studio_favorites = [
            FavouriteV2(english_title='',
                        romaji_title=fav_node.get('name'),
                        site_url=fav_node.get('siteUrl'))
            for fav_node in self._data.get('favourites', {}).get('studios', {}).get('nodes', [])
        ]
        self.favourites = FavouritesV2(anime=anime_favorites,
                                       manga=manga_favorites,
                                       characters=character_favorites,
                                       staff=staff_favorites,
                                       studios=studio_favorites)

    def _set_stats(self):
        self._set_anime_stats()
        self._set_manga_stats()

    def _set_anime_stats(self):
        anime_stats = self._data.get('statistics', {}).get('anime', {})
        anime_statuses = [
            StatusV2(count=statistic_type.get('count'),
                     status=statistic_type.get('status'),
                     amount=statistic_type.get('minutesWatched'))
            for statistic_type in anime_stats.get('statuses', [])
        ]
        anime_lengths = [
            Length(count=statistic_type.get('count'),
                   length=statistic_type.get('length'),
                   mean_score=statistic_type.get('meanScore'))
            for statistic_type in anime_stats.get('lengths', [])
        ]
        anime_release_years = [
            ReleaseYear(count=statistic_type.get('count'),
                        year=statistic_type.get('releaseYear'),
                        mean_score=statistic_type.get('meanScore'))
            for statistic_type in anime_stats.get('releaseYears', [])
        ]
        anime_genres = [
            Genre(count=statistic_type.get('count'),
                  genre=statistic_type.get('genre'),
                  mean_score=statistic_type.get('meanScore'))
            for statistic_type in anime_stats.get('genres', [])
        ]
        anime_tags = [
            Tag(count=statistic_type.get('count'),
                tag=statistic_type.get('tag', {}).get('name'),
                mean_score=statistic_type.get('meanScore'))
            for statistic_type in anime_stats.get('tags', [])
        ]
        anime_voice_actors = [
            VoiceActor(count=statistic_type.get('count'),
                       name=statistic_type.get('voiceActor', {}).get('name', {}).get('full'),
                       language=statistic_type.get('voiceActor', {}).get('languageV2'),
                       site_url=statistic_type.get('voiceActor', {}).get('siteUrl'),
                       mean_score=statistic_type.get('meanScore'))
            for statistic_type in anime_stats.get('voiceActors', [])
        ]
        anime_studios = [
            Studio(count=statistic_type.get('count'),
                   name=statistic_type.get('studio', {}).get('name'),
                   site_url=statistic_type.get('studio', {}).get('siteUrl'),
                   mean_score=statistic_type.get('meanScore'))
            for statistic_type in anime_stats.get('studios', [])
        ]

        self.anime_stats = AnimeStats(count=sum([status.count for status in anime_statuses]),
                                      mean_score=anime_stats.get('meanScore'),
                                      minutes_watched=sum([status.amount for status in anime_statuses
                                                          if status.status != AnilistStatus.PLANNING]),
                                      statuses=anime_statuses,
                                      lengths=anime_lengths,
                                      release_years=anime_release_years,
                                      genres=anime_genres,
                                      tags=anime_tags,
                                      voice_actors=anime_voice_actors,
                                      studios=anime_studios)

    def _set_manga_stats(self):
        manga_stats = self._data.get('statistics', {}).get('manga', {})
        manga_statuses = [
            StatusV2(count=statistic_type.get('count'),
                     status=statistic_type.get('status'),
                     amount=statistic_type.get('chaptersRead'))
            for statistic_type in manga_stats.get('statuses', [])
        ]
        manga_release_years = [
            ReleaseYear(count=statistic_type.get('count'),
                        year=statistic_type.get('releaseYear'),
                        mean_score=statistic_type.get('meanScore'))
            for statistic_type in manga_stats.get('releaseYears', [])
        ]
        manga_genres = [
            Genre(count=statistic_type.get('count'),
                  genre=statistic_type.get('genre'),
                  mean_score=statistic_type.get('meanScore'))
            for statistic_type in manga_stats.get('genres', [])
        ]
        manga_tags = [
            Tag(count=statistic_type.get('count'),
                tag=statistic_type.get('tag', {}).get('name'),
                mean_score=statistic_type.get('meanScore'))
            for statistic_type in manga_stats.get('tags', [])
        ]
        manga_staff = [
            Staff(count=statistic_type.get('count'),
                  name=statistic_type.get('staff', {}).get('name', {}).get('full'),
                  site_url=statistic_type.get('staff', {}).get('siteUrl'),
                  mean_score=statistic_type.get('meanScore'))
            for statistic_type in manga_stats.get('staff', [])
        ]

        self.manga_stats = MangaStats(count=sum([status.count for status in manga_statuses]),
                                      mean_score=manga_stats.get('meanScore'),
                                      chapters_read=sum([status.amount for status in manga_statuses
                                                         if status.status != AnilistStatus.PLANNING]),
                                      statuses=manga_statuses,
                                      release_years=manga_release_years,
                                      genres=manga_genres,
                                      tags=manga_tags,
                                      staff=manga_staff)

    def _set_analyses(self):
        anime_amount_analysis = anime_score_analysis = anime_planning_analysis = anime_current_analysis =\
            anime_dropped_analysis = anime_paused_analysis = manga_amount_analysis = manga_score_analysis = \
            manga_planning_analysis = manga_current_analysis = manga_paused_analysis = anime_length_analysis =\
            anime_release_years_analysis = anime_genres_analysis = anime_tags_analysis = anime_voice_actors_analysis =\
            anime_studios_analysis = manga_genres_analysis = manga_tags_analysis = manga_staff_analysis = None

        anime_planning_stats = self.anime_stats.get_status_stats(status=AnilistStatus.PLANNING)
        anime_current_stats = self.anime_stats.get_status_stats(status=AnilistStatus.CURRENT)
        anime_dropped_stats = self.anime_stats.get_status_stats(status=AnilistStatus.DROPPED)
        anime_paused_stats = self.anime_stats.get_status_stats(status=AnilistStatus.PAUSED)

        manga_planning_stats = self.manga_stats.get_status_stats(status=AnilistStatus.PLANNING)
        manga_current_stats = self.manga_stats.get_status_stats(status=AnilistStatus.CURRENT)
        manga_dropped_stats = self.manga_stats.get_status_stats(status=AnilistStatus.DROPPED)
        manga_paused_stats = self.manga_stats.get_status_stats(status=AnilistStatus.PAUSED)

        completed_days = round(self.anime_stats.minutes_watched / (60*24), 1)
        if completed_days >= 100:
            anime_amount_analysis = f"Needs to get a life, seriously " \
                                       f"(spent **{completed_days}** days watching anime)."
        elif completed_days >= 60:
            anime_amount_analysis = f"Has watched way too much anime (**{completed_days}** days)."
        elif completed_days >= 30:
            anime_amount_analysis = f"Has watched a considerable amount of anime (**{completed_days}** days)."
        elif completed_days > 0:
            anime_amount_analysis = f"Hasn't watched much anime *yet* (**{completed_days}** days)."
        else:
            anime_amount_analysis = "Hasn't watched anime at all. Weird, I know."

        if self.anime_stats.mean_score >= 85:
            anime_score_analysis = f"Is very generous with scoring " \
                                   f"(~**{round(self.anime_stats.mean_score, 2)}** mean score)"
        elif self.anime_stats.mean_score < 70 and self.anime_stats.count > 0:
            anime_score_analysis = f"Has high standards " \
                                   f"(~**{round(self.anime_stats.mean_score, 2)}** mean score)"
        elif self.anime_stats.count > 0:
            anime_score_analysis = f"Is fair enough when rating " \
                                   f"(~**{round(self.anime_stats.mean_score, 2)}** mean score)"

        anime_planned_percentage = round((anime_planning_stats.count / self.anime_stats.count)*100, 1) \
            if self.anime_stats.count else 0
        if anime_planned_percentage >= 15 and self.anime_stats.count > 60:
            anime_planning_analysis = f"Needs to start checking their planning list " \
                                      f"(**{anime_planned_percentage}%** planned)."
        elif anime_planned_percentage < 5 and self.anime_stats.count > 60:
            anime_planning_analysis = f"Actually watches things they plan to watch " \
                                      f"(**{anime_planned_percentage}%** planned)."
        elif self.anime_stats.count > 60:
            anime_planning_analysis = f"Keeps a good balance between planned and" \
                                      f" completed (**{anime_planned_percentage}%** planned)."
        elif self.anime_stats.count in range(30, 61) and anime_planned_percentage > 50:
            anime_planning_analysis = f"Seems to be just getting into anime."

        if anime_current_stats.count > 10:
            anime_current_analysis = f"Is taking on too many shows at once " \
                                     f"(currently watching **{anime_current_stats.count}**)"
        elif anime_current_stats.count == 0 and completed_days > 0:
            anime_current_analysis = f"Seems to be taking a break from anime right now."

        if anime_dropped_stats.count > 30:
            anime_dropped_analysis = f"Might be picky but at least willing to give things a chance " \
                                     f"(**{anime_dropped_stats.count}** dropped)."
        elif anime_dropped_stats.count + anime_paused_stats.count == 0 and completed_days:
            anime_dropped_analysis = f"Fully commits to finishing any show they start " \
                                     f"(no dropped or paused anime)."

        if anime_paused_stats.count > 15:
            anime_paused_analysis = f"Has commitment issues (**{anime_paused_stats.count}** paused)."

        completed_chapters = self.manga_stats.chapters_read
        if completed_chapters >= 5000:
            manga_amount_analysis = f"Really, really likes manga " \
                                    f"(has read **{completed_chapters}** chapters)."
        elif completed_chapters >= 3000:
            manga_amount_analysis = f"Reads a lot of manga (**{completed_chapters}** completed chapters)."
        elif completed_chapters >= 1000:
            manga_amount_analysis = f"Reads manga occasionally (**{completed_chapters}** completed chapters)."
        elif completed_chapters > 0:
            manga_amount_analysis = f"Doesn't read manga that often, or is just getting started" \
                                    f" (**{completed_chapters}** completed chapters)."
        elif completed_days > 30:
            manga_amount_analysis = "Prefers anime over manga."
            if self.manga_stats.count == 0:
                manga_amount_analysis += "  Has never completed a chapter in fact."
        else:
            manga_amount_analysis = "Never read a chapter"
            if self.manga_stats.count == 0:
                manga_amount_analysis += " and is yet to discovered a thing called manga"
            manga_amount_analysis += '.'

        if self.manga_stats.mean_score >= 85:
            manga_score_analysis = f"Likes what they read " \
                                   f"(~**{round(self.manga_stats.mean_score, 2)}** mean score)"
        elif self.manga_stats.mean_score <= 70 and self.manga_stats.count > 0:
            manga_score_analysis = f"Very critical of what they read " \
                                   f"(~**{round(self.manga_stats.mean_score, 2)}** mean score)"
        elif self.manga_stats.count > 0:
            manga_score_analysis = f"Finds most of what they read to be good enough " \
                                   f"(~**{round(self.manga_stats.mean_score, 2)}** mean score)"

        manga_planned_percentage = round((manga_planning_stats.count / self.manga_stats.count)*100, 1) \
            if self.manga_stats.count else 0
        if manga_planned_percentage >= 15 and self.manga_stats.count > 60:
            manga_planning_analysis = f"Their planning list just keeps growing " \
                                      f"(**{manga_planned_percentage}%** planned)."
        elif manga_planned_percentage < 5 and self.manga_stats.count > 60:
            manga_planning_analysis = f"Likely starts a manga immediately after discovering it" \
                                      f" rather than sending it to Planning list."
        elif self.manga_stats.count in range(30, 61) and manga_planned_percentage > 50:
            manga_planning_analysis = f"Keeps adding manga to their planning list but barely reads any."

        if manga_current_stats.count >= 50:
            manga_current_analysis = f"Somehow keeping up with **{manga_current_stats.count}** manga. Honestly, how?"
        elif manga_current_stats.count >= 15:
            manga_current_analysis = f"Too busy keeping up with all the manga they read " \
                                     f"(currently reading **{manga_current_stats.count}**)"
        elif manga_current_stats.count in range(1, 10):
            manga_current_analysis = f"Doing their best to keep up with a few manga " \
                                     f"(currently reading **{manga_current_stats.count}**)"
        elif manga_current_stats.count == 0 and completed_chapters > 0:
            manga_current_analysis = f"Taking a break from manga or just doesn't read anymore."

        if manga_paused_stats.count > manga_dropped_stats.count and manga_paused_stats.count > 3:
            manga_paused_analysis = f"Constantly sad that their favorite " \
                                    f"titles keep going on hiatus (or worse - discontinued)."

        if self.anime_stats.count > 30:
            if self.anime_stats.lengths[0].length == "1":
                anime_length_analysis = "Prefers movies or 1-episode titles over everything else."
            elif self.anime_stats.lengths[0].length == "2-6":
                anime_length_analysis = "Prefers short anime (2-6 episodes long)."
            elif self.anime_stats.lengths[0].length in ["7-16", "17-28"]:
                anime_length_analysis = "Mostly can only handle 1-cour or 2-cour anime" \
                                        + (" (probably just watches whatever is airing seasonally)."
                                           if anime_current_stats.count > 5 else ".")
            elif self.anime_stats.lengths[0].length in ["29-55", "56-100"]:
                anime_length_analysis = "Watches a lot of long-running anime (30-100 episodes)."
        elif self.anime_stats.lengths and self.anime_stats.lengths[0].length == "101+":
            anime_length_analysis = "Believes that if an anime doesn't run for over 100 " \
                                    "episodes then it's not worth watching."

        if self.anime_stats.count > 20:
            year_2000_minus = 0
            year_2001_2010 = 0
            year_2011_plus = 0
            for release_year, count in [(year_stat.year, year_stat.count)
                                        for year_stat in self.anime_stats.release_years]:
                if release_year <= 2000:
                    year_2000_minus += count
                elif release_year in range(2001, 2011):
                    year_2001_2010 += count
                else:
                    year_2011_plus += count
            max_period = max(year_2011_plus, year_2001_2010, year_2000_minus)
            close_range = range(0, int(self.anime_stats.count/8) + 2)
            if max_period == year_2011_plus \
                    and year_2011_plus - year_2001_2010 in close_range \
                    and year_2011_plus - year_2000_minus in close_range:
                anime_release_years_analysis = f"Their list keeps a great balance across all generations of anime."
            elif max_period == year_2011_plus and year_2011_plus - year_2001_2010 in close_range:
                anime_release_years_analysis = f"Prefers things released after the year 2000."
            elif max_period == year_2011_plus and year_2011_plus - year_2000_minus in close_range:
                anime_release_years_analysis = f"Likes new and old anime just the same."
            elif max_period == year_2001_2010 and year_2001_2010 - year_2000_minus in close_range:
                anime_release_years_analysis = f"Not the biggest fan of newer releases."
            elif max_period == year_2011_plus:
                anime_release_years_analysis = f"Likes newer anime (2010+) more than anything."
            elif max_period == year_2001_2010:
                anime_release_years_analysis = f"Prefers anime from 2000-2010 more than anything."
            elif max_period == year_2000_minus:
                anime_release_years_analysis = f"Big fan of old-school anime (pre-2000)."

            anime_genres_analysis = f"Watches a lot of " \
                                    f"**{'**, **'.join(g.genre for g in self.anime_stats.genres[:2])}** " \
                                    f"and **{self.anime_stats.genres[2].genre}** anime."

            tags_filtered = [tag for tag in self.anime_stats.tags if tag.tag not in ["Male Protagonist",
                                                                                     "Female Protagonist",
                                                                                     "Ensemble Cast",
                                                                                     "Primarily Female Cast",
                                                                                     "Primarily Male Cast"]]
            anime_tags_analysis = f"Most of what they watch is themed around " \
                                  f"**{'**, **'.join(t.tag for t in tags_filtered[:2])}** " \
                                  f"and **{tags_filtered[2].tag}**."

        if self.anime_stats.count > 100:
            voice_actors_filtered = [va for va in self.anime_stats.voice_actors if va.language == "Japanese"]
            anime_voice_actors_analysis = f"Would recognize [{voice_actors_filtered[0].name}]" \
                                          f"({voice_actors_filtered[0].site_url})'s voice in a heartbeat."

        if self.anime_stats.count > 50:
            anime_studios_analysis = f"Is secretly a fan of whatever **{self.anime_stats.studios[0].name}** puts out."

        if self.manga_stats.count > 20:
            manga_genres_analysis = f"Reads a lot of " \
                                    f"**{'**, **'.join(g.genre for g in self.manga_stats.genres[:2])}** " \
                                    f"and **{self.manga_stats.genres[2].genre}** manga."

            tags_filtered = [tag for tag in self.manga_stats.tags if tag.tag not in ["Male Protagonist",
                                                                                     "Female Protagonist",
                                                                                     "Ensemble Cast",
                                                                                     "Primarily Female Cast",
                                                                                     "Primarily Male Cast"]]
            manga_tags_analysis = f"Most of what they read is themed around " \
                                  f"**{'**, **'.join(t.tag for t in tags_filtered[:2])}** " \
                                  f"and **{tags_filtered[2].tag}**."

        if self.manga_stats.count > 50 and self.manga_stats.staff[0].count > 2:
            manga_staff_analysis = f"Has read multiple titles by [{self.manga_stats.staff[0].name}]" \
                                   f"({self.manga_stats.staff[0].site_url})."
            
        self.anilysis = Anilysis(anime_amount_analysis,
                                 anime_score_analysis,
                                 anime_planning_analysis, 
                                 anime_current_analysis,
                                 anime_dropped_analysis,
                                 anime_paused_analysis,
                                 anime_length_analysis,
                                 anime_release_years_analysis,
                                 anime_genres_analysis,
                                 anime_tags_analysis, 
                                 anime_voice_actors_analysis, 
                                 anime_studios_analysis)
        
        self.mangalysis = Mangalysis(manga_amount_analysis,
                                     manga_score_analysis,
                                     manga_planning_analysis,
                                     manga_current_analysis,
                                     manga_paused_analysis,
                                     manga_genres_analysis,
                                     manga_tags_analysis,
                                     manga_staff_analysis)


class FavouritesV2:
    def __init__(self, anime: list, manga: list, characters: list, staff: list, studios: list):
        self.anime = anime
        self.manga = manga
        self.characters = characters
        self.staff = staff
        self.studios = studios


class FavouriteV2:
    def __init__(self, english_title: str, romaji_title: str, site_url: str):
        self.english_title = english_title
        self.romaji_title = romaji_title
        self.site_url = site_url


class StatusV2:
    def __init__(self, count: int, status: str, amount: int):
        self.count = count
        self.status = status
        self.amount = amount


class Length:
    def __init__(self, count: int, length: str, mean_score: float):
        self.count = count
        self.length = length
        self.mean_score = mean_score


class ReleaseYear:
    def __init__(self, count: int, year: int, mean_score: float):
        self.count = count
        self.year = year
        self.mean_score = mean_score


class Genre:
    def __init__(self, count: int, genre: str, mean_score: float):
        self.count = count
        self.genre = genre
        self.mean_score = mean_score


class Tag:
    def __init__(self, count: int, tag: str, mean_score: float):
        self.count = count
        self.tag = tag
        self.mean_score = mean_score


class VoiceActor:
    def __init__(self, count: int, name: str, language: str, site_url: str, mean_score: float):
        self.count = count
        self.name = name
        self.language = language
        self.site_url = site_url
        self.mean_score = mean_score


class Studio:
    def __init__(self, count: int, name: str, site_url: str, mean_score: float):
        self.count = count
        self.name = name
        self.site_url = site_url
        self.mean_score = mean_score


class Staff:
    def __init__(self, count: int, name: str, site_url: str, mean_score: float):
        self.count = count
        self.name = name
        self.site_url = site_url
        self.mean_score = mean_score


class Anilysis:
    def __init__(self, amount_analysis, score_analysis, planning_analysis,  current_analysis,
                 dropped_analysis, paused_analysis, length_analysis, release_years_analysis,
                 genres_analysis, tags_analysis, voice_actors_analysis, studios_analysis):
        self.amount_analysis = amount_analysis
        self.score_analysis = score_analysis
        self.planning_analysis = planning_analysis
        self.current_analysis = current_analysis
        self.dropped_analysis = dropped_analysis
        self.paused_analysis = paused_analysis
        self.length_analysis = length_analysis
        self.release_years_analysis = release_years_analysis
        self.genres_analysis = genres_analysis
        self.tags_analysis = tags_analysis
        self.voice_actors_analysis = voice_actors_analysis
        self.studios_analysis = studios_analysis


class Mangalysis:
    def __init__(self, amount_analysis, score_analysis, planning_analysis,
                 current_analysis, paused_analysis, genres_analysis,
                 tags_analysis, staff_analysis):
        self.amount_analysis = amount_analysis
        self.score_analysis = score_analysis
        self.planning_analysis = planning_analysis
        self.current_analysis = current_analysis
        self.paused_analysis = paused_analysis
        self.genres_analysis = genres_analysis
        self.tags_analysis = tags_analysis
        self.staff_analysis = staff_analysis


class AnimeStats:
    def __init__(self, count: int, mean_score: float, minutes_watched: int, statuses: list, lengths: list,
                 release_years: list, genres: list, tags: list, voice_actors: list, studios: list):
        self.count = count
        self.mean_score = mean_score
        self.minutes_watched = minutes_watched
        self.statuses = statuses
        self.lengths = lengths
        self.release_years = release_years
        self.genres = genres
        self.tags = tags
        self.voice_actors = voice_actors
        self.studios = studios

    def get_status_stats(self, status: str) -> StatusV2:
        for status_ in self.statuses:
            if status_.status == status:
                return status_
        return StatusV2(0, status, 0)


class MangaStats:
    def __init__(self, count: int, mean_score: float, chapters_read: int, statuses: list,
                 release_years: list, genres: list, tags: list, staff: list):
        self.count = count
        self.mean_score = mean_score
        self.chapters_read = chapters_read
        self.statuses = statuses
        self.release_years = release_years
        self.genres = genres
        self.tags = tags
        self.staff = staff

    def get_status_stats(self, status: str) -> StatusV2:
        for status_ in self.statuses:
            if status_.status == status:
                return status_
        return StatusV2(0, status, 0)
