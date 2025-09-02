from typing import TYPE_CHECKING
import inspect
from functools import wraps

import discord

from bot.utils.embed_factory.general_embeds import get_error_embed
from common.db import session_context, get_session, execute_post_commit_actions, execute_post_rollback_actions
from common.exceptions import OhanaException, ExternalServiceException, UserReadableException
from constants import AppLogCategory
from strings.commands_strings import GeneralCommandsStrings
from strings.general_strings import GeneralStrings
from system.extensions_management import propagate_to_extensions
from utils.helpers.context_helpers import set_context_id, reset_context_id
if TYPE_CHECKING:
    from bot.context_menus.user_context_menus import UserContextMenus
    from bot.interaction_handlers import BaseInteractionHandler
    from bot.slashes import BaseSlashes


def slash_command(guild_only: bool = False,
                  bot_permissions: list[str] | None = None,
                  user_permissions: list[str] | None = None):
    """
    Decorator to mark a coroutine function as a slash command with pre-processing and error handling.
    Args:
        guild_only (bool): Whether the command can only be used in guilds.
        bot_permissions (list[str] | None): List of permissions the bot requires to execute the command.
        user_permissions (list[str] | None): List of permissions the user requires to execute the command.
    """
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Slash command must be a coroutine function.")
        func.__is_slash_command__ = True

        @wraps(func)
        async def wrapper(slashes_handler: 'BaseSlashes', *args, **kwargs):
            async with session_context():
                from common.app_logger import AppLogger
                logger = AppLogger("SlashCommandHandler")
                context_token = set_context_id()
                interaction: discord.Interaction = slashes_handler.interaction

                command_failed = False
                try:
                    await slashes_handler.preprocess_and_validate(guild_only=guild_only,
                                                                  bot_permissions=bot_permissions,
                                                                  user_permissions=user_permissions)
                    await func(slashes_handler, *args, **kwargs)
                except Exception as e:
                    command_failed = True
                    if isinstance(e, discord.Forbidden):
                        error_message = GeneralCommandsStrings.GENERIC_PERMISSIONS_ERROR_MESSAGE
                    elif isinstance(e, OhanaException):
                        error_message = getattr(e, "user_message", GeneralStrings.GENERIC_ERROR_MESSAGE)
                    else:
                        error_message = GeneralStrings.GENERIC_ERROR_MESSAGE
                    if (not isinstance(e, UserReadableException)
                            and not (isinstance(e, ExternalServiceException) and not e.alert_worthy)):
                        logger.error(f"Slash handler `{func.__qualname__}` failed.\nError: `{e}`",
                                     category=AppLogCategory.BOT_GENERAL,
                                     extras={
                                         "interaction_data": interaction.data,
                                         "user_id": interaction.user.id,
                                         "guild_id": interaction.guild.id if interaction.guild else None,
                                     })

                    error_embed = get_error_embed(message=error_message)

                    try:
                        if not interaction.response.is_done():
                            await interaction.response.send_message(embed=error_embed,
                                                                    ephemeral=True,
                                                                    delete_after=10)
                        else:
                            await interaction.followup.send(embed=error_embed,
                                                            ephemeral=True)
                    except discord.NotFound:
                        try:
                            await interaction.followup.send(embed=error_embed,
                                                            ephemeral=True)
                        except Exception:
                            pass

                    await get_session().rollback()
                    await execute_post_rollback_actions()
                finally:
                    await get_session().commit()
                    await execute_post_commit_actions()
                    if not interaction.response.is_done() and not command_failed:
                        logger.warning(f"Slash Handler {func.__qualname__} did not respond to interaction.")
                    reset_context_id(context_token)

        return wrapper
    return decorator


def interaction_handler():
    """
    Decorator to mark a coroutine function as an interaction handler with pre-processing and error handling.
    """
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Interaction handler must be a coroutine function.")
        func.__is_interaction_handler__ = True

        @wraps(func)
        async def wrapper(interaction_handler_object: 'BaseInteractionHandler', *args, **kwargs):
            async with session_context():
                from common.app_logger import AppLogger
                logger = AppLogger("InteractionHandler")
                context_token = set_context_id()
                interaction: discord.Interaction = args[0] if args else kwargs.get('interaction')

                command_failed = False
                try:
                    await interaction_handler_object.preprocess_and_validate(
                        interaction=interaction,
                        handler=func
                    )
                    await func(interaction_handler_object, *args, **kwargs)
                except Exception as e:
                    command_failed = True
                    if isinstance(e, discord.Forbidden):
                        error_message = GeneralCommandsStrings.GENERIC_PERMISSIONS_ERROR_MESSAGE
                    elif isinstance(e, OhanaException):
                        error_message = getattr(e, "user_message", GeneralStrings.GENERIC_ERROR_MESSAGE)
                    else:
                        error_message = GeneralStrings.GENERIC_ERROR_MESSAGE
                    if (not isinstance(e, UserReadableException)
                            and not (isinstance(e, ExternalServiceException) and not e.alert_worthy)):
                        logger.error(f"Interaction handler `{func.__qualname__}` failed.\nError: `{e}`",
                                     category=AppLogCategory.BOT_GENERAL,
                                     extras={
                                         "interaction_data": interaction.data,
                                         "user_id": interaction.user.id,
                                         "guild_id": interaction.guild.id if interaction.guild else None,
                                     })

                    error_embed = get_error_embed(message=error_message)

                    try:
                        if not interaction.response.is_done():
                            await interaction.response.send_message(embed=error_embed,
                                                                    ephemeral=True,
                                                                    delete_after=10)
                        else:
                            await interaction.followup.send(embed=error_embed,
                                                            ephemeral=True)
                    except discord.NotFound:
                        try:
                            await interaction.followup.send(embed=error_embed,
                                                            ephemeral=True)
                        except Exception:
                            pass

                    await get_session().rollback()
                    await execute_post_rollback_actions()
                finally:
                    await get_session().commit()
                    await execute_post_commit_actions()
                    if not interaction.response.is_done() and not command_failed:
                        logger.warning(f"Interaction Handler {func.__qualname__} did not respond to interaction.")
                    reset_context_id(context_token)

        return wrapper
    return decorator


def context_menu_command(guild_only: bool = False):
    """
    Decorator to mark a coroutine function as a context menu command with pre-processing and error handling.
    Args:
        guild_only (bool): Whether the command can only be used in guilds.
    """
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Context menu command must be a coroutine function.")
        func.__is_context_menu_command__ = True

        @wraps(func)
        async def wrapper(context_menu_command_handler: 'UserContextMenus', *args, **kwargs):
            async with session_context():
                from common.app_logger import AppLogger
                logger = AppLogger("ContextMenuCommandHandler")
                context_token = set_context_id()
                interaction: discord.Interaction = context_menu_command_handler.interaction

                command_failed = False
                try:
                    await context_menu_command_handler.preprocess_and_validate(guild_only=guild_only)
                    await func(context_menu_command_handler, *args, **kwargs)
                except Exception as e:
                    command_failed = True
                    if isinstance(e, discord.Forbidden):
                        error_message = GeneralCommandsStrings.GENERIC_PERMISSIONS_ERROR_MESSAGE
                    elif isinstance(e, OhanaException):
                        error_message = getattr(e, "user_message", GeneralStrings.GENERIC_ERROR_MESSAGE)
                    else:
                        error_message = GeneralStrings.GENERIC_ERROR_MESSAGE
                    if (not isinstance(e, UserReadableException)
                            and not (isinstance(e, ExternalServiceException) and not e.alert_worthy)):
                        logger.error(f"Context menu command `{func.__qualname__}` failed.\nError: `{e}`",
                                     category=AppLogCategory.BOT_GENERAL,
                                     extras={
                                         "interaction_data": interaction.data,
                                         "user_id": interaction.user.id,
                                         "guild_id": interaction.guild.id if interaction.guild else None,
                                     })

                    error_embed = get_error_embed(message=error_message)

                    try:
                        if not interaction.response.is_done():
                            await interaction.response.send_message(embed=error_embed,
                                                                    ephemeral=True,
                                                                    delete_after=10)
                        else:
                            await interaction.followup.send(embed=error_embed,
                                                            ephemeral=True)
                    except discord.NotFound:
                        try:
                            await interaction.followup.send(embed=error_embed,
                                                            ephemeral=True)
                        except Exception:
                            pass

                    await get_session().rollback()
                    await execute_post_rollback_actions()
                finally:
                    await get_session().commit()
                    await execute_post_commit_actions()
                    if not interaction.response.is_done() and not command_failed:
                        logger.warning(f"Context menu command {func.__qualname__} did not respond to interaction.")
                    reset_context_id(context_token)

        return wrapper
    return decorator


def extensible_event(group: str):
    """
    Decorator to mark an event handler as an extensible event that propagates to extensions after execution.
    Args:
        group (str): The group name of the event (bot, guild, member, etc...).
    """
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Extensible event must be a coroutine function.")

        @wraps(func)
        async def wrapper(*args, **kwargs):
            from common.app_logger import AppLogger
            logger = AppLogger("ExtensibleEvent")
            context_token = set_context_id()
            event_name = func.__qualname__.split('.')[-1]
            try:
                logger.debug(f"Processing event `{event_name}`")
                await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Extensible event `{event_name}` in group `{group}` failed.\nError: `{e}`",
                             category=AppLogCategory.BOT_GENERAL)
            await propagate_to_extensions(*args,
                                          event_group=group,
                                          event=event_name)

            reset_context_id(context_token)

        return wrapper
    return decorator
