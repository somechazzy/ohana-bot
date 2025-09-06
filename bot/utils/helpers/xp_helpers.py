import discord


def get_user_username_for_xp(user: discord.Member | discord.User) -> str:
    """
    Get a string representation of the user's username storage and leaderboard display.
    Args:
        user (discord.Member | discord.User): The user or member object.
    Returns:
        str: The string representation of the user's username.
    """
    if isinstance(user, discord.Member):
        if user.nick and user.nick != user.name:
            user_username = f"{user.nick} ({user.name})"
        elif user.global_name and user.global_name != user.name:
            user_username = f"{user.global_name} ({user.name})"
        else:
            user_username = user.name
    else:
        if user.global_name and user.global_name != user.name:
            user_username = f"{user.global_name} ({user.name})"
        else:
            user_username = user.name
    return user_username
