import importlib.util
import inspect
import pathlib
import sys
import traceback

from extensions.templates.events.bot_events import *
from extensions.templates.events.channel_events import *
from extensions.templates.events.guild_events import *
from extensions.templates.events.interaction_events import *
from extensions.templates.events.member_events import *
from extensions.templates.events.message_events import *
from extensions.templates.events.reaction_events import *
from extensions.templates.events.role_events import *
from extensions.templates.events.voice_events import *
from utils.helpers.context_helpers import create_isolated_task

bot_on_ready_extensions = []
bot_on_connect_extensions = []
bot_on_error_extensions = []

channel_on_guild_channel_create_extensions = []
channel_on_guild_channel_delete_extensions = []
channel_on_guild_channel_update_extensions = []
channel_on_guild_channel_pins_update_extensions = []
channel_on_typing_extensions = []
channel_on_raw_typing_extensions = []

guild_on_guild_join_extensions = []
guild_on_guild_remove_extensions = []
guild_on_guild_update_extensions = []
guild_on_guild_emojis_update_extensions = []
guild_on_guild_stickers_update_extensions = []
guild_on_audit_log_entry_create_extensions = []
guild_on_invite_create_extensions = []
guild_on_invite_delete_extensions = []

interaction_on_interaction_extensions = []

member_on_member_join_extensions = []
member_on_member_remove_extensions = []
member_on_raw_member_remove_extensions = []
member_on_member_update_extensions = []
member_on_user_update_extensions = []
member_on_member_ban_extensions = []
member_on_member_unban_extensions = []
member_on_presence_update_extensions = []
member_on_raw_presence_update_extensions = []

message_on_message_extensions = []
message_on_message_edit_extensions = []
message_on_message_delete_extensions = []
message_on_bulk_message_delete_extensions = []
message_on_raw_message_edit_extensions = []
message_on_raw_message_delete_extensions = []
message_on_raw_bulk_message_delete_extensions = []

reaction_on_reaction_add_extensions = []
reaction_on_reaction_remove_extensions = []
reaction_on_reaction_clear_extensions = []
reaction_on_reaction_clear_emoji_extensions = []
reaction_on_raw_reaction_add_extensions = []
reaction_on_raw_reaction_remove_extensions = []
reaction_on_raw_reaction_clear_extensions = []
reaction_on_raw_reaction_clear_emoji_extensions = []

role_on_guild_role_create_extensions = []
role_on_guild_role_delete_extensions = []
role_on_guild_role_update_extensions = []

voice_on_voice_state_update_extensions = []
voice_on_voice_channel_effect_extensions = []


def load_extensions():
    from common.app_logger import AppLogger
    logger = AppLogger("extensions_management")
    base_path = pathlib.Path(r"extensions").resolve()
    loaded_extensions_count = 0
    for path in base_path.rglob("*.py"):
        if not path.is_file() or base_path.joinpath("templates") in path.parents:
            continue
        module_name = path.relative_to(base_path).with_suffix("").as_posix().replace("/", ".")
        full_module_name = f"{base_path}.{module_name}"

        try:
            spec = importlib.util.spec_from_file_location(full_module_name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[full_module_name] = module
            spec.loader.exec_module(module)
            loaded_extensions_count += 1
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if cls.__module__ != module.__name__:
                    continue
                try:
                    if issubclass(cls, BaseOnReadyEventHandler):
                        bot_on_ready_extensions.append(cls)
                    elif issubclass(cls, BaseOnConnectEventHandler):
                        bot_on_connect_extensions.append(cls)
                    elif issubclass(cls, BaseOnErrorEventHandler):
                        bot_on_error_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildChannelCreateEventHandler):
                        channel_on_guild_channel_create_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildChannelDeleteEventHandler):
                        channel_on_guild_channel_delete_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildChannelUpdateEventHandler):
                        channel_on_guild_channel_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildChannelPinsUpdateEventHandler):
                        channel_on_guild_channel_pins_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnTypingEventHandler):
                        channel_on_typing_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawTypingEventHandler):
                        channel_on_raw_typing_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildJoinEventHandler):
                        guild_on_guild_join_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildRemoveEventHandler):
                        guild_on_guild_remove_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildUpdateEventHandler):
                        guild_on_guild_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildEmojisUpdateEventHandler):
                        guild_on_guild_emojis_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildStickersUpdateEventHandler):
                        guild_on_guild_stickers_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnAuditLogEntryCreateEventHandler):
                        guild_on_audit_log_entry_create_extensions.append(cls)
                    elif issubclass(cls, BaseOnInviteCreateEventHandler):
                        guild_on_invite_create_extensions.append(cls)
                    elif issubclass(cls, BaseOnInviteDeleteEventHandler):
                        guild_on_invite_delete_extensions.append(cls)
                    elif issubclass(cls, BaseOnInteractionEventHandler):
                        interaction_on_interaction_extensions.append(cls)
                    elif issubclass(cls, BaseOnMemberJoinEventHandler):
                        member_on_member_join_extensions.append(cls)
                    elif issubclass(cls, BaseOnMemberRemoveEventHandler):
                        member_on_member_remove_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawMemberRemoveEventHandler):
                        member_on_raw_member_remove_extensions.append(cls)
                    elif issubclass(cls, BaseOnMemberUpdateEventHandler):
                        member_on_member_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnUserUpdateEventHandler):
                        member_on_user_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnMemberBanEventHandler):
                        member_on_member_ban_extensions.append(cls)
                    elif issubclass(cls, BaseOnMemberUnbanEventHandler):
                        member_on_member_unban_extensions.append(cls)
                    elif issubclass(cls, BaseOnPresenceUpdateEventHandler):
                        member_on_presence_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawPresenceUpdateEventHandler):
                        member_on_raw_presence_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnMessageEventHandler):
                        message_on_message_extensions.append(cls)
                    elif issubclass(cls, BaseOnMessageEditEventHandler):
                        message_on_message_edit_extensions.append(cls)
                    elif issubclass(cls, BaseOnMessageDeleteEventHandler):
                        message_on_message_delete_extensions.append(cls)
                    elif issubclass(cls, BaseOnBulkMessageDeleteEventHandler):
                        message_on_bulk_message_delete_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawMessageEditEventHandler):
                        message_on_raw_message_edit_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawMessageDeleteEventHandler):
                        message_on_raw_message_delete_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawBulkMessageDeleteEventHandler):
                        message_on_raw_bulk_message_delete_extensions.append(cls)
                    elif issubclass(cls, BaseOnReactionAddEventHandler):
                        reaction_on_reaction_add_extensions.append(cls)
                    elif issubclass(cls, BaseOnReactionRemoveEventHandler):
                        reaction_on_reaction_remove_extensions.append(cls)
                    elif issubclass(cls, BaseOnReactionClearEventHandler):
                        reaction_on_reaction_clear_extensions.append(cls)
                    elif issubclass(cls, BaseOnReactionClearEmojiEventHandler):
                        reaction_on_reaction_clear_emoji_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawReactionAddEventHandler):
                        reaction_on_raw_reaction_add_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawReactionRemoveEventHandler):
                        reaction_on_raw_reaction_remove_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawReactionClearEventHandler):
                        reaction_on_raw_reaction_clear_extensions.append(cls)
                    elif issubclass(cls, BaseOnRawReactionClearEmojiEventHandler):
                        reaction_on_raw_reaction_clear_emoji_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildRoleCreateEventHandler):
                        role_on_guild_role_create_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildRoleDeleteEventHandler):
                        role_on_guild_role_delete_extensions.append(cls)
                    elif issubclass(cls, BaseOnGuildRoleUpdateEventHandler):
                        role_on_guild_role_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnVoiceStateUpdateEventHandler):
                        voice_on_voice_state_update_extensions.append(cls)
                    elif issubclass(cls, BaseOnVoiceChannelEffectEventHandler):
                        voice_on_voice_channel_effect_extensions.append(cls)
                    else:
                        loaded_extensions_count -= 1
                except Exception as e:
                    logger.warning(f"Error loading extension {cls.__name__} from {module_name}: {e}",
                                   extras={"traceback": traceback.format_exc()})
                    loaded_extensions_count -= 1
        except Exception as e:
            logger.warning(f"Error loading module {module_name}: {e}",
                           extras={"traceback": traceback.format_exc()})

    logger.info(f"Loaded {loaded_extensions_count} extensions.")


async def propagate_to_extensions(*args, event_group: str, event: str):
    """
    Executes the appropriate extension handlers based on the event type.
    """
    from common.app_logger import AppLogger
    logger = AppLogger("extensions_management")
    extensions: list = globals().get(f"{event_group}_{event}_extensions", [])
    if not extensions:
        return
    logger.debug(f"Propagating event {event_group}.{event} to {len(extensions)} extensions")
    for extension_class in extensions:
        try:
            extension_handler = extension_class(*args)
            if await extension_handler.check():
                create_isolated_task(extension_handler.handle_event())
        except Exception as e:
            logger.error(f"Error in extension {extension_class.__name__} for event {event_group}.{event}: {e}")
