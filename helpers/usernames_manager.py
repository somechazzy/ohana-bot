from globals_.clients import firebase_client
from globals_.variables import mal_usernames, al_usernames
from models.username_mapping import UsernameMapping


async def link_mal_username(member, username: str):
    """
        :param member: member whose username is to be linked
        :param username: username meant to be set and linked

        :returns bool: whether a change has happened or not
        :returns string: feedback text
    """
    if member.id in mal_usernames:
        username_mapping: UsernameMapping = mal_usernames.get(member.id)
        if username.strip() == username_mapping.username:
            return False, f"Your MAL username is already set to {username}."

        else:
            old_username = username_mapping.username
            username_mapping.set_username(username)
            mal_usernames[member.id] = username_mapping
            await update_mal_username_in_db(member.id)
            return True, f"Your MAL username has been changed from {old_username} to {username}."
    else:
        username_mapping = UsernameMapping(member.id, username)
        mal_usernames[member.id] = username_mapping
        await update_mal_username_in_db(member.id)
        return True, f"Your MAL username has been set to `{username}`! Try using `mal` command."


async def link_al_username(member, username):
    """
        :param member: member whose username is to be linked
        :param username: username meant to be set and linked

        :returns bool: whether a change has happened or not
        :returns string: feedback text
    """
    if member.id in al_usernames:
        username_mapping: UsernameMapping = al_usernames.get(member.id)
        if username.strip() == username_mapping.username:
            return False, f"Your AL username is already set to {username}."

        else:
            old_username = username_mapping.username
            username_mapping.set_username(username)
            al_usernames[member.id] = username_mapping
            await update_al_username_in_db(member.id)
            return True, f"Your AL username has been changed from {old_username} to {username}."
    else:
        username_mapping = UsernameMapping(member.id, username)
        al_usernames[member.id] = username_mapping
        await update_al_username_in_db(member.id)
        return True, f"Your AL username has been set to `{username}`! Try using `al` command."


def get_mal_username(discord_id):
    """
        :param discord_id: discord_id whose username is to be retrieved

        :returns username: if username exists, else returns None
        :returns string: feedback text
    """
    discord_id = int(discord_id)
    if discord_id in mal_usernames:
        username_mapping = mal_usernames.get(discord_id)
        return username_mapping.username, "-"
    else:
        return None, "You haven't linked your MAL yet. Use `[prefix]linkmal [your MAL username]`."


def get_al_username(discord_id):
    """
        :param discord_id: discord_id whose username is to be retrieved

        :returns username: if username exists, else returns None
        :returns string: feedback text
    """
    discord_id = int(discord_id)
    if discord_id in al_usernames:
        username_mapping = al_usernames.get(discord_id)
        return username_mapping.username, "-"
    else:
        return None, "You haven't linked your AL yet. Use `[prefix]linkal [your AL username]`."


def get_mal_username_mapping(discord_id):
    discord_id = int(discord_id)
    return mal_usernames.get(discord_id)


def get_al_username_mapping(discord_id):
    discord_id = int(discord_id)
    return al_usernames.get(discord_id)


async def update_mal_username_in_db(discord_id):
    discord_id = int(discord_id)
    if discord_id in mal_usernames:
        username_mapping_object = mal_usernames.get(discord_id)
        username_mapping = {
            "username": username_mapping_object.username
        }
        await firebase_client.put_mal_username(discord_id, username_mapping)
    else:
        pass


async def update_al_username_in_db(discord_id):
    discord_id = int(discord_id)
    if discord_id in al_usernames:
        username_mapping_object = al_usernames.get(discord_id)
        username_mapping = {
            "username": username_mapping_object.username
        }
        await firebase_client.put_al_username(discord_id, username_mapping)
    else:
        pass


def mal_username_exists_for_user(discord_id):
    discord_id = int(discord_id)
    return discord_id in mal_usernames


def al_username_exists_for_user(discord_id):
    discord_id = int(discord_id)
    return discord_id in al_usernames


async def unlink_mal_username(discord_id):
    if mal_username_exists_for_user(discord_id):
        mal_usernames.pop(discord_id)
        await firebase_client.remove_mal_username(discord_id)
        return True, f"Your MAL username has been unlinked."
    else:
        return False, f"You don't have your MAL linked."


async def unlink_al_username(discord_id):
    if al_username_exists_for_user(discord_id):
        al_usernames.pop(discord_id)
        await firebase_client.remove_al_username(discord_id)
        return True, f"Your Anilist username has been unlinked."
    else:
        return False, f"You don't have your Anilist linked."
