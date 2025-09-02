

class GeneralIntegrationStrings:
    """
    Base class for integration strings.
    To be inherited by all integration strings classes to provide easy access per integration to shared strings.
    """
    CONNECTION_ERROR_MESSAGE = "Sorries. There was an error while connecting to the service. Please try again later."
    USERNAME_BEING_CHECKED = "Checking username {loading_emoji}"

    ANIME_LOADING = "Getting anime info {loading_emoji}"
    MANGA_LOADING = "Getting manga info {loading_emoji}"
    ANIME_NOT_FOUND = "No anime found for `{title}`."
    MANGA_NOT_FOUND = "No manga found for `{title}`."


class MALStrings(GeneralIntegrationStrings):
    """
    Strings for MAL/MyAnimeList integration.
    """
    USERNAME_LINKED = "You **MyAnimeList username** has been successfully linked as `{username}`."
    USERNAME_UPDATED = "Your **MyAnimeList username** has been updated from `{old_username}` to `{username}`."
    USERNAME_NOT_FOUND = "MyAnimeList username `{username}` not found."
    USERNAME_NOT_SET = ("Your MyAnimeList username isn't linked."
                        " Use `/link-myanimelist` to use this command or provide a username.")
    OTHER_USERNAME_NOT_SET = ("User's MyAnimeList username isn't linked."
                              " You can directly provide their username instead.")
    USERNAME_UNSET = "Unlinked your MAL account.\nIf this was a mistake you can relink it using the same command."

    LINK_INSTRUCTION = "You can link your MyAnimeList account by using the `/link-myanimelist` command."

    PROFILE_LOADING = "Loading MyAnimeList profile {loading_emoji}"

    CONNECTION_ERROR_MESSAGE = "Error while connecting to MyAnimeList. Please try again later."
    NOT_FOUND_MESSAGE = "MyAnimeList returned 404 :("
    SERVICE_DOWN_MESSAGE = "MyAnimeList is currently down. Please try again later."

    INTEGRATION_DISABLED = "MyAnimeList integration isn't available (yet)."


class AnilistStrings(GeneralIntegrationStrings):
    """
    Strings for AniList integration.
    """
    USERNAME_LINKED = "You **AniList username** has been successfully linked as `{username}`."
    USERNAME_UPDATED = "Your **AniList username** has been updated from `{old_username}` to `{username}`."
    USERNAME_NOT_FOUND = "AniList username `{username}` doesn't exist or is a private profile."
    USERNAME_NOT_SET = ("Your AniList username isn't linked."
                        " Use `/link-anilist` to use this command or provide a username.")
    OTHER_USERNAME_NOT_SET = "User's AniList username isn't linked."
    USERNAME_UNSET = "Unlinked your AniList account.\nIf this was a mistake you can relink it using the same command."

    LINK_INSTRUCTION = "You can link your AniList account by using the `/link-anilist` command."

    PROFILE_LOADING = "Loading AniList profile {loading_emoji}"

    CONNECTION_ERROR_MESSAGE = "Error while connecting to AniList. Please try again later."
    NOT_FOUND_MESSAGE = "AniList returned 404 :("
    SERVICE_DOWN_MESSAGE = "AniList is currently down. Please try again later."

    ANALYSIS_ANIME_DAYS_100P = "Needs to get a life, seriously (spent **{completed_days}** days watching anime)."
    ANALYSIS_ANIME_DAYS_60P = "Has watched way too much anime (**{completed_days}** days)."
    ANALYSIS_ANIME_DAYS_30P = "Has watched a considerable amount of anime (**{completed_days}** days)."
    ANALYSIS_ANIME_DAYS_P0 = "Hasn't watched much anime *yet* (**{completed_days}** days)."
    ANALYSIS_ANIME_DAYS_0 = "Hasn't watched anime at all. Weird, I know."

    ANALYSIS_ANIME_SCORE_85P = "Is very generous with scoring (~**{mean_score}** mean score)"
    ANALYSIS_ANIME_SCORE_70P = "Is fair enough when rating (~**{mean_score}** mean score)"
    ANALYSIS_ANIME_SCORE_0P = "Has high standards (~**{mean_score}** mean score)"

    ANALYSIS_ANIME_PLANNING_MAX = "Needs to start checking their planning list (**{planned_percentage}%** planned)."
    ANALYSIS_ANIME_PLANNING_MIN = "Actually watches things they plan to watch (**{planned_percentage}%** planned)."
    ANALYSIS_ANIME_PLANNING_BALANCED = ("Keeps a healthy amount of anime in their planning list "
                                        "(**{planned_percentage}%** planned anime).")
    ANALYSIS_ANIME_PLANNING_NEW = "Seems to be just getting into anime."
    ANALYSIS_ANIME_CURRENT_MAX = "Is taking on too many shows at once (currently watching **{current_count}**)"
    ANALYSIS_ANIME_CURRENT_0 = "Isn't watching anything at the moment. Maybe they need some recommendations?"
    ANALYSIS_ANIME_DROPPED_MAX = ("Might be picky but at least willing to give things a chance"
                                  " (**{dropped_count}** dropped).")
    ANALYSIS_ANIME_DROPPED_0 = "Fully commits to finishing any show they start (no dropped or paused anime)."
    ANALYSIS_ANIME_PAUSED_MAX = "Has commitment issues (**{paused_count}** paused)."

    ANALYSIS_ANIME_LENGTH_1 = "Really loves anime movies."
    ANALYSIS_ANIME_LENGTH_2_TO_6 = "Prefers short anime (2-6 episodes long)."
    ANALYSIS_ANIME_LENGTH_7_TO_28 = "Mostly can only handle 1-cour or 2-cour anime."
    ANALYSIS_ANIME_LENGTH_29_TO_100 = "Watches a lot of long-running anime (30-100 episodes)."
    ANALYSIS_ANIME_LENGTH_101P = "Anything less than 100 episodes isn't even worth watching..."

    ANALYSIS_ANIME_RELEASE_YEARS_ALL = "Their list keeps a great balance across all generations of anime."
    ANALYSIS_ANIME_RELEASE_YEARS_2000P = "Prefers things released after the year 2000."
    ANALYSIS_ANIME_RELEASE_YEARS_OLD_NEW = "Likes new and old anime just the same."
    ANALYSIS_ANIME_RELEASE_YEARS_OLD = "Not the biggest fan of newer releases."
    ANALYSIS_ANIME_RELEASE_YEARS_2010P = "Likes newer anime (2010+) more than anything."
    ANALYSIS_ANIME_RELEASE_YEARS_2000_TO_2010 = "Prefers anime from 2000-2010 more than anything."
    ANALYSIS_ANIME_RELEASE_YEARS_PRE_2000 = "Big fan of old-school anime (pre-2000)."

    ANALYSIS_ANIME_GENRES_3P = ("Watches a lot of **{genre_1}**, **{genre_2}**, and **{genre_3}**."
                                " But especially enjoys **{highest_rated_genre}** anime.")
    ANALYSIS_ANIME_GENRES_TWO = ("Watches a lot of **{genre_1}** and **{genre_2}**."
                                 " But especially enjoys **{highest_rated_genre}** anime.")
    ANALYSIS_ANIME_GENRES_ONE = "Watches a lot of **{genre}**."

    ANALYSIS_ANIME_TAGS_3P = ("Most of what they watch is themed around **{tag_1}**, **{tag_2}**, and **{tag_3}**,"
                              " and more than anything is fond of **{highest_rated_tag}**.")
    ANALYSIS_ANIME_TAGS_TWO = ("Most of what they watch is themed around **{tag_1}** and **{tag_2}**,"
                               " and more than anything is fond of **{highest_rated_tag}**.")
    ANALYSIS_ANIME_TAGS_ONE = "Most of what they watch is themed around **{tag}**."

    ANALYSIS_ANIME_VA = "Would recognize [{va_name}]({va_url})'s voice in a heartbeat."
    ANALYSIS_ANIME_STUDIO = "Is secretly a fan of whatever [{studio_name}]({studio_url}) puts out."

    ANALYSIS_MANGA_CHAPTERS_5KP = "Really, really likes manga (has read **{completed_chapters}** chapters)."
    ANALYSIS_MANGA_CHAPTERS_3KP = "Reads a lot of manga (**{completed_chapters}** completed chapters)."
    ANALYSIS_MANGA_CHAPTERS_1KP = "Reads manga occasionally (**{completed_chapters}** completed chapters)."
    ANALYSIS_MANGA_CHAPTERS_MIN = ("Doesn't read manga that often, or is just getting started "
                                   "(**{completed_chapters}** completed chapters).")
    ANALYSIS_MANGA_CHAPTERS_0P_ANIME = "Prefers anime over manga."
    ANALYSIS_MANGA_CHAPTERS_0_ANIME = "Prefers anime over manga. Has never completed a chapter in fact."
    ANALYSIS_MANGA_CHAPTERS_0P = "Never read a chapter."
    ANALYSIS_MANGA_CHAPTERS_0 = "Never read a chapter and has yet to discover a thing called manga."

    ANALYSIS_MANGA_SCORE_85P = "Likes what they read (~**{mean_score}** mean score)"
    ANALYSIS_MANGA_SCORE_70P = "Finds most of what they read to be good enough (~**{mean_score}** mean score)"
    ANALYSIS_MANGA_SCORE_0P = "Very critical of what they read (~**{mean_score}** mean score)"

    ANALYSIS_MANGA_PLANNING_MAX = "Their planning list just keeps growing (**{planned_percentage}%** planned)."
    ANALYSIS_MANGA_PLANNING_MIN = ("Likely starts a manga immediately after discovering"
                                   " it rather than sending it to planning list.")
    ANALYSIS_MANGA_PLANNING_MOST_WITH_COMPLETED = "Keeps adding manga to their planning list but barely reads any."
    ANALYSIS_MANGA_PLANNING_MOST_WITHOUT_COMPLETED = "Keeps adding manga to their planning list but never reads any."

    ANALYSIS_MANGA_CURRENT_50P = "Somehow keeping up with **{current_count}** manga. Honestly, how?"
    ANALYSIS_MANGA_CURRENT_15P = ("Too busy keeping up with all the manga they"
                                  " read (currently reading **{current_count}**)")
    ANALYSIS_MANGA_CURRENT_1P = ("Doing their best to keep up with their favorite manga"
                                 " (currently reading **{current_count}**)")
    ANALYSIS_MANGA_CURRENT_0 = "Isn't reading any manga at the moment. Maybe they need some recommendations?"

    ANALYSIS_MANGA_PAUSED_DROPPED = ("Constantly sad that their favorite titles keep"
                                     " going on hiatus (or worse - discontinued).")

    ANALYSIS_MANGA_GENRES_3P = ("Reads a lot of  **{genre_1}**, **{genre_2}**, and **{genre_3}**,"
                                " and their favorite is **{highest_rated_genre}** manga.")
    ANALYSIS_MANGA_GENRES_TWO = ("Watches a lot of **{genre_1}** and **{genre_2}**,"
                                 " and their favorite is **{highest_rated_genre}** manga.")
    ANALYSIS_MANGA_GENRES_ONE = "Reads a lot of **{genre}**."

    ANALYSIS_MANGA_TAGS_3P = ("Most of what they read is themed around **{tag_1}**, **{tag_2}**, and **{tag_3}**,"
                              " but likes **{highest_rated_tag}** the most.")
    ANALYSIS_MANGA_TAGS_TWO = ("Most of what they read is themed around **{tag_1}** and **{tag_2}**,"
                               " but likes **{highest_rated_tag}** the most.")
    ANALYSIS_MANGA_TAGS_ONE = "Most of what they read is themed around **{tag}**."

    ANALYSIS_MANGA_STAFF = "Has read multiple titles by [{staff_name}]({staff_url})."


class UrbanStrings(GeneralIntegrationStrings):
    """
    Strings for Urban Dictionary integration.
    """
    DEFINITION_LOADING = "Getting definition {loading_emoji}"

    SERVICE_DOWN_MESSAGE = "Looks like Urban Dictionary is down."

    INTEGRATION_DISABLED = "Urban Dictionary integration isn't available (yet)."


class MerriamWebsterStrings(GeneralIntegrationStrings):
    """
    Strings for Merriam-Webster Dictionary integration.
    """
    NO_DEFINITION_FOUND = "No definition found for this term."
    SERVICE_DOWN_MESSAGE = "Looks like Merriam-Webster Dictionary is down."

    INTEGRATION_DISABLED = "Merriam-Webster Dictionary integration isn't available (yet)."
