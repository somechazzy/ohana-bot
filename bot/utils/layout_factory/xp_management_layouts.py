from typing import TYPE_CHECKING, Coroutine

from discord import ButtonStyle
from discord.ui import TextDisplay, ActionRow, Button, Container, Separator

from bot.utils.layout_factory import BaseLayout
from clients import emojis
from constants import Colour, XPActionEnums

if TYPE_CHECKING:
    from bot.interaction_handlers.admin_interaction_handlers.manage_xp_transfer_interaction_handler import \
        ManageXPTransferInteractionHandler


class XPTransferLayout(BaseLayout):

    def __init__(self,
                 interactions_handler: 'ManageXPTransferInteractionHandler',
                 feedback_message: str | None,
                 **kwargs) -> None:
        super().__init__(interactions_handler=interactions_handler, **kwargs)
        container = Container(accent_color=Colour.PRIMARY_ACCENT)
        self.add_item(container)
        container.add_item(TextDisplay('# XP Transfer Wizard'))

        feedback_message = "## " + feedback_message if feedback_message else None

        container.add_item(Separator())
        container.add_item(TextDisplay('## What kind of action would you like to do?'))
        action_row = self._get_select_as_action_row(options=XPActionEnums.MainAction.as_list(),
                                                    callback=interactions_handler.on_action_select,
                                                    selected_option=interactions_handler.selected_action)
        container.add_item(action_row)

        if interactions_handler.selected_action == XPActionEnums.MainAction.AWARD_XP:
            container.add_item(Separator())
            container.add_item(TextDisplay('## Who are we awarding?'))
            action_row = self._get_select_as_action_row(options=XPActionEnums.ActionTargetType.as_list(),
                                                        callback=interactions_handler.on_target_type_select,
                                                        selected_option=interactions_handler.selected_target_type)
            container.add_item(action_row)
            if interactions_handler.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
                if interactions_handler.selected_member:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(f'You are awarding to '
                                                   f'{interactions_handler.selected_member.mention} '
                                                   f'({interactions_handler.selected_member.id})'))
                    submit_button = Button(label='Enter amount', style=ButtonStyle.green)
                    submit_button.callback = interactions_handler.on_submit
                    container.add_item(ActionRow(submit_button))
                elif feedback_message:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(feedback_message))
            elif interactions_handler.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
                if interactions_handler.selected_role:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(f'You are awarding to '
                                                   f'{interactions_handler.selected_role.mention}'))
                    submit_button = Button(label='Enter amount', style=ButtonStyle.green)
                    submit_button.callback = interactions_handler.on_submit
                    container.add_item(ActionRow(submit_button))
                elif feedback_message:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(feedback_message))
            elif interactions_handler.selected_target_type == XPActionEnums.ActionTargetType.EVERYONE:
                container.add_item(Separator())
                container.add_item(TextDisplay('You are awarding to everyone in the server.'))
                submit_button = Button(label='Enter amount', style=ButtonStyle.green)
                submit_button.callback = interactions_handler.on_submit
                container.add_item(ActionRow(submit_button))
        elif interactions_handler.selected_action == XPActionEnums.MainAction.TAKE_AWAY_XP:
            container.add_item(Separator())
            container.add_item(TextDisplay('## Who are we taking away XP from?'))
            action_row = self._get_select_as_action_row(options=XPActionEnums.ActionTargetType.as_list(),
                                                        callback=interactions_handler.on_target_type_select,
                                                        selected_option=interactions_handler.selected_target_type)
            container.add_item(action_row)
            if interactions_handler.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
                if interactions_handler.selected_member:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(f'You are taking away XP from '
                                                   f'{interactions_handler.selected_member.mention} '
                                                   f'({interactions_handler.selected_member.id})'))
                    submit_button = Button(label='Enter amount', style=ButtonStyle.green)
                    submit_button.callback = interactions_handler.on_submit
                    container.add_item(ActionRow(submit_button))
                elif interactions_handler.selected_user_id:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(f'You are taking away XP from user ID '
                                                   f'{interactions_handler.selected_user_id}'))
                    submit_button = Button(label='Enter amount', style=ButtonStyle.green)
                    submit_button.callback = interactions_handler.on_submit
                    container.add_item(ActionRow(submit_button))
                elif feedback_message:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(feedback_message))
            elif interactions_handler.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
                if interactions_handler.selected_role:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(f'You are taking away XP from '
                                                   f'{interactions_handler.selected_role.mention}'))
                    submit_button = Button(label='Enter amount', style=ButtonStyle.green)
                    submit_button.callback = interactions_handler.on_submit
                    container.add_item(ActionRow(submit_button))
                elif feedback_message:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(feedback_message))
            elif interactions_handler.selected_target_type == XPActionEnums.ActionTargetType.EVERYONE:
                container.add_item(Separator())
                container.add_item(TextDisplay('You are taking away XP from everyone in the server.'))
                submit_button = Button(label='Enter amount', style=ButtonStyle.green)
                submit_button.callback = interactions_handler.on_submit
                container.add_item(ActionRow(submit_button))
        elif interactions_handler.selected_action == XPActionEnums.MainAction.TRANSFER_XP:
            container.add_item(Separator())
            container.add_item(TextDisplay('## Choose the user you want to transfer XP from.'))
            if interactions_handler.selected_member:
                container.add_item(Separator())
                container.add_item(TextDisplay(f'You are transferring XP from '
                                               f'{interactions_handler.selected_member.mention} '
                                               f'({interactions_handler.selected_member.id})'))
            elif interactions_handler.selected_user_id:
                container.add_item(Separator())
                container.add_item(TextDisplay(f'You are transferring XP from user ID '
                                               f'{interactions_handler.selected_user_id}'))
            if interactions_handler.selected_other_member:
                container.add_item(TextDisplay(f'You are transferring XP to '
                                               f'{interactions_handler.selected_other_member.mention} '
                                               f'({interactions_handler.selected_other_member.id})'))
                submit_button = Button(label='Transfer XP', style=ButtonStyle.green)
                submit_button.callback = interactions_handler.on_submit
                container.add_item(ActionRow(submit_button))
            if feedback_message:
                container.add_item(Separator())
                container.add_item(TextDisplay(feedback_message))

        elif interactions_handler.selected_action == XPActionEnums.MainAction.RESET_XP:
            container.add_item(Separator())
            container.add_item(TextDisplay('## Who are we resetting XP for?'))
            action_row = self._get_select_as_action_row(options=XPActionEnums.ActionTargetType.as_list(),
                                                        callback=interactions_handler.on_target_type_select,
                                                        selected_option=interactions_handler.selected_target_type)
            container.add_item(action_row)
            if interactions_handler.selected_target_type == XPActionEnums.ActionTargetType.MEMBER:
                if interactions_handler.selected_member:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(f'You are resetting XP for '
                                                   f'{interactions_handler.selected_member.mention} '
                                                   f'({interactions_handler.selected_member.id})'))
                    submit_button = Button(label='Reset XP', style=ButtonStyle.red)
                    submit_button.callback = interactions_handler.on_submit
                    container.add_item(ActionRow(submit_button))
                elif interactions_handler.selected_user_id:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(f'You are resetting XP for user ID '
                                                   f'{interactions_handler.selected_user_id}'))
                    submit_button = Button(label='Reset XP', style=ButtonStyle.red)
                    submit_button.callback = interactions_handler.on_submit
                    container.add_item(ActionRow(submit_button))
                elif feedback_message:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(feedback_message))
            elif interactions_handler.selected_target_type == XPActionEnums.ActionTargetType.ROLE:
                if interactions_handler.selected_role:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(f'You are resetting XP for all members in '
                                                   f'{interactions_handler.selected_role.mention}'))
                    submit_button = Button(label='Reset XP', style=ButtonStyle.red)
                    submit_button.callback = interactions_handler.on_submit
                    container.add_item(ActionRow(submit_button))
                elif feedback_message:
                    container.add_item(Separator())
                    container.add_item(TextDisplay(feedback_message))
            elif interactions_handler.selected_target_type == XPActionEnums.ActionTargetType.EVERYONE:
                container.add_item(Separator())
                container.add_item(TextDisplay('You are resetting XP for everyone in the server.'))
                submit_button = Button(label='Reset XP', style=ButtonStyle.red)
                submit_button.callback = interactions_handler.on_submit
                container.add_item(ActionRow(submit_button))

        if interactions_handler.selected_action:
            container.add_item(Separator())
            restart_button = Button(label='Restart Wizard', style=ButtonStyle.grey, emoji=emojis.action.clear)
            restart_button.callback = interactions_handler.on_restart
            container.add_item(ActionRow(restart_button))

    # noinspection PyMethodMayBeStatic
    def _get_select_as_action_row(self,
                                  options: list[str],
                                  callback: type(Coroutine),
                                  selected_option: str | None) -> ActionRow:
        action_row = ActionRow()
        action_buttons = [
            Button(label=action, style=ButtonStyle.blurple,
                   custom_id=action, disabled=action == selected_option)
            for action in options
        ]
        for action_button in action_buttons:
            action_button.callback = callback
            action_row.add_item(action_button)

        return action_row


class XPTransferSummaryLayout(BaseLayout):

    def __init__(self, interactions_handler: 'ManageXPTransferInteractionHandler', summary_text: str, **kwargs) -> None:
        super().__init__(interactions_handler=interactions_handler, **kwargs)
        container = Container(accent_color=Colour.PRIMARY_ACCENT)

        container.add_item(TextDisplay('# Summary'))
        container.add_item(Separator())
        container.add_item(TextDisplay(summary_text))
        container.add_item(Separator())
        container.add_item(TextDisplay(f"This could take some time depending on the size of the action."
                                       f" Feel free to dismiss this message."))

        self.add_item(container)
