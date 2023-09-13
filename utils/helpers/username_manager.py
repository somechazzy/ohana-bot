from globals_.constants import CachingType
from globals_.shared_memory import user_id_mal_username_map, user_id_anilist_username_map
from internal.requests_manager import request
from models.username_mapping import UsernameMapping


async def link_mal_username(user, username: str):
    """
        :param user: user whose username is to be linked
        :param username: username meant to be set and linked

        :returns bool: whether a change has happened or not
        :returns string: feedback text
    """
    if user.id in user_id_mal_username_map:
        username_mapping: UsernameMapping = user_id_mal_username_map.get(user.id)
        if username.strip().__eq__(username_mapping.username):
            return False, f"Your MAL username is already set to **{username}**. Try using `/mal` command."

        else:
            old_username = username_mapping.username
            username_mapping.set_username(username)
            user_id_mal_username_map[user.id] = username_mapping
            await update_mal_username_in_db(user.id)
            return True, f"Your MAL username has been changed from **{old_username}** to **{username}**. " \
                         f"Try using `/mal` command."
    else:
        username_mapping = UsernameMapping(user.id, username)
        user_id_mal_username_map[user.id] = username_mapping
        await update_mal_username_in_db(user.id)
        return True, f"Your MAL username has been set to **{username}**! Try using `/mal` command."


async def link_al_username(user, username):
    """
        :param user: member whose username is to be linked
        :param username: username meant to be set and linked

        :returns bool: whether a change has happened or not
        :returns string: feedback text
    """
    if user.id in user_id_anilist_username_map:
        username_mapping: UsernameMapping = user_id_anilist_username_map.get(user.id)
        if username.strip().__eq__(username_mapping.username):
            return False, f"Your Anilist username is already set to **{username}**. Try using `/al` command."

        else:
            old_username = username_mapping.username
            username_mapping.set_username(username)
            user_id_anilist_username_map[user.id] = username_mapping
            await update_al_username_in_db(user.id)
            return True, f"Your Anilist username has been changed from **{old_username}** to **{username}**. " \
                         f"Try using `/al` command."
    else:
        username_mapping = UsernameMapping(user.id, username)
        user_id_anilist_username_map[user.id] = username_mapping
        await update_al_username_in_db(user.id)
        return True, f"Your Anilist username has been set to **{username}**! Try using `/al` command."


def get_mal_username(user_id):
    """
        :param user_id: discord_id whose username is to be retrieved

        :returns username: if username exists, else returns None
    """
    user_id = int(user_id)
    if user_id in user_id_mal_username_map:
        return user_id_mal_username_map.get(user_id).username
    return None


def get_anilist_username(user_id):
    """
        :param user_id: discord_id whose username is to be retrieved

        :returns username: if username exists, else returns None
    """
    user_id = int(user_id)
    if user_id in user_id_anilist_username_map:
        return user_id_anilist_username_map.get(user_id).username
    return None


async def update_mal_username_in_db(user_id):
    from globals_.clients import firebase_client
    user_id = int(user_id)
    if user_id in user_id_mal_username_map:
        username_mapping_object = user_id_mal_username_map.get(user_id)
        username_mapping = {
            "username": username_mapping_object.username
        }
        await firebase_client.put_mal_username(user_id, username_mapping)
    else:
        pass


async def update_al_username_in_db(user_id):
    from globals_.clients import firebase_client
    user_id = int(user_id)
    if user_id in user_id_anilist_username_map:
        username_mapping_object = user_id_anilist_username_map.get(user_id)
        username_mapping = {
            "username": username_mapping_object.username
        }
        await firebase_client.put_al_username(user_id, username_mapping)
    else:
        pass


async def unlink_mal_username(user_id):
    from globals_.clients import firebase_client
    user_id_mal_username_map.pop(user_id)
    await firebase_client.remove_mal_username(user_id)


async def unlink_anilist_username(user_id):
    from globals_.clients import firebase_client
    user_id_anilist_username_map.pop(user_id)
    await firebase_client.remove_al_username(user_id)


async def mal_profile_exists(username):
    url = f"https://myanimelist.net/profile/{username}"
    response = await request("GET", url, CachingType.MAL_PROFILE)
    return response.status


async def anilist_profile_exists(username):
    query = """
    query ($name: String) {

         User (name: $name) {
             id
             name
         }
    }
    """
    var = {
        'name': username
    }
    url = 'https://graphql.anilist.co'
    response = await request("post", url, CachingType.AL_PROFILE, json_={'query': query, 'variables': var})
    return response.status
