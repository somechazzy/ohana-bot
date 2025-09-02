import discord

from bot.interaction_handlers.user_interaction_handlers import UserInteractionHandler
from bot.utils.guild_logger import GuildLogger
from bot.utils.helpers.moderation_helpers import bot_can_assign_role
from constants import RoleMenuType, RoleMenuMode, GuildLogEvent
from models.dto.cachables import CachedGuildSettings


class RoleMenuInteractionHandler(UserInteractionHandler):
    VIEW_NAME = "Role menu"

    def __init__(self, role_menu: CachedGuildSettings.RoleMenu, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_menu = role_menu

    async def handle_action(self):
        member = self.original_member
        if self.role_menu.restricted_role_ids and not any(
                role.id in self.role_menu.restricted_role_ids for role in member.roles
        ):
            await self.source_interaction.response.send_message(
                "You don't have any of the required roles to use this menu: \n"
                f"{', '.join([f'<@&{role_id}>' for role_id in self.role_menu.restricted_role_ids])}",
                ephemeral=True
            )
            return

        if self.role_menu.menu_type == RoleMenuType.SELECT:
            selected_role_ids = set(map(int, self.source_interaction.data["values"]))
            available_role_ids = {
                int(option.value) for select_menu in self.source_interaction.message.components[0].children
                for option in select_menu.options
            }
        else:
            selected_role_ids = {int(self.source_interaction.data["custom_id"])}
            available_role_ids = {
                int(button.custom_id) for component in self.source_interaction.message.components
                for button in component.children
            }
        available_role_ids.discard(0)
        existing_user_role_ids = {role.id for role in member.roles}

        roles_to_add, roles_to_remove = self._determine_role_changes(
            selected_role_ids=selected_role_ids,
            available_role_ids=available_role_ids,
            existing_user_role_ids=existing_user_role_ids
        )

        new_member_roles = (set(member.roles) | set(roles_to_add)) - roles_to_remove
        await member.edit(roles=new_member_roles, reason="Role menu")

        feedback_message = "Roles updated:"
        if roles_to_add:
            feedback_message += f"\nAdded roles: {', '.join([role.mention for role in roles_to_add])}"
        if roles_to_remove:
            feedback_message += f"\nRemoved roles: {', '.join([role.mention for role in roles_to_remove])}"
        if not roles_to_add and not roles_to_remove:
            feedback_message += "\nNothing changed.."
        await self.source_interaction.response.send_message(feedback_message, ephemeral=True)

        await GuildLogger(guild=self.guild).log_event(event=GuildLogEvent.EDITED_ROLES,
                                                      roles_deltas=(roles_to_add, roles_to_remove),
                                                      member=member,
                                                      reason="Role menu interaction")

    def _determine_role_changes(self,
                                selected_role_ids: set[int],
                                available_role_ids: set[int],
                                existing_user_role_ids: set[int]) -> tuple[set[discord.Role], set[discord.Role]]:
        roles_ids_to_add, role_ids_to_remove = set(), set()

        if 0 in selected_role_ids:
            role_ids_to_remove.update(existing_user_role_ids & available_role_ids)
        elif self.role_menu.menu_mode == RoleMenuMode.SINGLE:
            selected_role_id = selected_role_ids.pop()
            if selected_role_id in existing_user_role_ids:
                role_ids_to_remove.add(selected_role_id)
            else:
                roles_ids_to_add.add(selected_role_id)
                role_ids_to_remove.update(existing_user_role_ids & available_role_ids)
                role_ids_to_remove.discard(selected_role_id)
        else:
            if selected_role_ids.issubset(existing_user_role_ids):
                role_ids_to_remove.update(selected_role_ids)
            elif not selected_role_ids & existing_user_role_ids:
                roles_ids_to_add.update(selected_role_ids)
            else:
                roles_ids_to_add.update(selected_role_ids - existing_user_role_ids)
                role_ids_to_remove.update(existing_user_role_ids & (available_role_ids - selected_role_ids))

        roles_to_add = {self.guild.get_role(role_id) for role_id in roles_ids_to_add
                        if self.guild.get_role(role_id) and (bot_can_assign_role(self.guild.get_role(role_id)))}
        roles_to_remove = {self.guild.get_role(role_id) for role_id in role_ids_to_remove
                           if self.guild.get_role(role_id) and bot_can_assign_role(self.guild.get_role(role_id))}

        return roles_to_add, roles_to_remove
