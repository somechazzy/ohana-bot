
class PlaylistDuplicateNameException(Exception):
    pass


class PlaylistAddParsingException(Exception):
    pass


class PlaylistNotFoundException(Exception):
    pass


class PlaylistPlayException(Exception):
    pass


class MusicVoiceConnectionException(Exception):
    pass


class MyAnimeListException(Exception):
    pass


class MyAnimeListNotFoundException(MyAnimeListException):
    pass


class MyAnimeListInternalErrorException(MyAnimeListException):
    pass


class MyAnimeListParseException(MyAnimeListException):
    pass


class AnilistException(Exception):
    pass


class AnilistNotFoundException(AnilistException):
    pass


class AnilistInternalErrorException(AnilistException):
    pass


class AnilistParseException(AnilistException):
    pass


class ModerationHierarchyError(Exception):
    pass


class StreamStatusCheckException(Exception):
    pass
