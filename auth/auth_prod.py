

class ProdAuth:
    # todo
    """
    Get your bot token from https://discord.com/developers/applications
    Choose your bot > Bot > copy token shown under "Token"
    """
    BOT_TOKEN = ''

    """
    This one is a bit tricky. 
    If you know what to do here, then go ahead. Otherwise follow step 3 in this guide 
     https://github.com/somechazzy/ohana-bot/blob/master/README.md
    """
    FIREBASE_CONFIG = {}

    """
    [Optional]
    Rapid API is used for urban dictionary, while Merriam API is used for Merriam dictionary
    • Get your Rapid API key by signing up here https://rapidapi.com then going here https://rapidapi.com/developer/security
      Create an app (fill boxes with anything) then go to your app > Security > Show the key and copy it here
    • Get your Merriam API key by signing up here https://dictionaryapi.com 
       > Your Keys > copy the key under "Key (Dictionary)"
    """
    RAPID_API_KEY = ""
    MERRIAM_API_KEY = ""

    """
    Get your spotify client details by signing in/up here https://developer.spotify.com/dashboard/applications
    Create an app (name/description can be anything) then you'll be able to see your Client ID and Client Secret
    """
    SPOTIFY_CLIENT_ID = ""
    SPOTIFY_CLIENT_SECRET = ""

    """
    Get your token by going here https://genius.com/api-clients > sign up or sign in 
     > New API Client  (fill with anything, leave redirect URL empty) > Generate Access Token > copy token
    """
    GENIUS_ACCESS_TOKEN = ""

    """
    Get your MAL client ID by logging into your MAL account and then by going here https://myanimelist.net/apiconfig 
     > Create ID > Fill the data as you wish > Submit (sample form here: https://files.catbox.moe/hm3ung.png)
     After you submit, you'll be able to see your client ID under the App Name
    """
    MYANIMELIST_CLIENT_ID = ""
