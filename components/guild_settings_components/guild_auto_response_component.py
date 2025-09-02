from common import NOT_SET_
from common.db import get_session
from components.guild_settings_components import BaseGuildSettingsComponent
from components.guild_settings_components.guild_settings_component import GuildSettingsComponent
from models.guild_settings_models import GuildAutoResponse
from repositories.guild_settings_repositories.guild_auto_response_repo import GuildAutoResponseRepo

NOT_SET = NOT_SET_()


class GuildAutoResponseComponent(BaseGuildSettingsComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add_auto_response(self,
                                guild_id: int,
                                trigger_text: str,
                                response_text: str,
                                match_type: str,
                                delete_original: bool) -> GuildAutoResponse:
        """
        Adds an auto response to the guild.
        Args:
            guild_id (int): The ID of the guild.
            trigger_text (str): The text that triggers the auto response.
            response_text (str): The text that the bot will respond with.
            match_type (str): The type of match for the trigger text (AutoResponseMatchType)
            delete_original (bool): Whether to delete the original message that triggered the response.

        Returns:
            GuildAutoResponse: The created auto response object.
        """
        self.logger.debug(f"Adding auto response for guild {guild_id}.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id)
        if guild_settings.get_auto_response(trigger=trigger_text):
            raise ValueError(f"Trigger text '{trigger_text}' already exists in guild {guild_id} auto responses.")
        guild_auto_responses_repo = GuildAutoResponseRepo(session=get_session())
        auto_response = await guild_auto_responses_repo.create_guild_auto_response(
            guild_settings_id=guild_settings.guild_settings_id,
            trigger_text=trigger_text,
            response_text=response_text,
            match_type=match_type,
            delete_original=delete_original
        )
        guild_settings.add_auto_response(guild_auto_response_id=auto_response.id,
                                         trigger=trigger_text,
                                         response=response_text,
                                         match_type=match_type,
                                         delete_original=delete_original)
        return auto_response

    async def update_auto_response(self,
                                   guild_id: int,
                                   guild_auto_response_id: int,
                                   trigger_text: str | NOT_SET_ = NOT_SET,
                                   response_text: str | NOT_SET_ = NOT_SET,
                                   match_type: str | NOT_SET_ = NOT_SET,
                                   delete_original: bool = NOT_SET) -> None:
        """
        Updates an existing auto response.
        Args:
            guild_id (int): The ID of the guild.
            guild_auto_response_id (int): The ID of the auto response to update.
            trigger_text (str): The new trigger text.
            response_text (str): The new response text.
            match_type (str): The new match type.
            delete_original (bool): Whether to delete the original message that triggered the response.
        """
        self.logger.debug(f"Updating auto response {guild_auto_response_id}.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=guild_id)
        auto_response = guild_settings.get_auto_response(guild_auto_response_id=guild_auto_response_id)
        update_data = {}
        if trigger_text is not NOT_SET:
            if guild_settings.get_auto_response(trigger=trigger_text):
                raise ValueError(f"Trigger text '{trigger_text}' already exists in guild {guild_id} auto responses.")
            update_data['trigger_text'] = trigger_text
            auto_response.trigger = trigger_text
        if response_text is not NOT_SET:
            update_data['response_text'] = response_text
            auto_response.response = response_text
        if match_type is not NOT_SET:
            update_data['match_type'] = match_type
            auto_response.match_type = match_type
        if delete_original is not NOT_SET:
            update_data['delete_original'] = delete_original
            auto_response.delete_original = delete_original

        guild_auto_responses_repo = GuildAutoResponseRepo(session=get_session())
        await guild_auto_responses_repo.update_guild_auto_response(
            guild_auto_response_id=guild_auto_response_id,
            trigger_text=trigger_text,
            response_text=response_text,
            match_type=match_type,
            delete_original=delete_original
        )

    async def remove_auto_response(self,
                                   guild_id: int,
                                   guild_auto_response_id: int) -> None:
        """
        Removes an auto response from the guild.
        Args:
            guild_id (int): The ID of the guild.
            guild_auto_response_id (int): The ID of the auto response to remove.
        """
        self.logger.debug(f"Removing auto response {guild_auto_response_id} from guild {guild_id}.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=guild_id)
        auto_response = guild_settings.get_auto_response(guild_auto_response_id=guild_auto_response_id)
        if not auto_response:
            raise ValueError(f"Auto response with ID {guild_auto_response_id} does not exist in guild {guild_id}.")

        guild_auto_responses_repo = GuildAutoResponseRepo(session=get_session())
        await guild_auto_responses_repo.delete_guild_auto_response(guild_auto_response_id=guild_auto_response_id)
        guild_settings.remove_auto_response(guild_auto_response_id=guild_auto_response_id)

    async def clear_auto_responses(self, guild_id: int) -> None:
        """
        Clears all auto responses for the guild.
        Args:
            guild_id (int): The ID of the guild.
        """
        self.logger.debug(f"Clearing all auto responses for guild {guild_id}.")
        guild_settings = await GuildSettingsComponent().get_guild_settings(guild_id=guild_id)
        if not guild_settings.auto_responses:
            return
        guild_auto_responses_repo = GuildAutoResponseRepo(session=get_session())
        await guild_auto_responses_repo.delete_guild_auto_responses(guild_settings_id=guild_settings.guild_settings_id)
        guild_settings.auto_responses.clear()
