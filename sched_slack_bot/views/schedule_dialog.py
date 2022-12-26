from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from slack_sdk.models.blocks import HeaderBlock, PlainTextObject, DividerBlock, PlainTextInputElement, \
    ConversationSelectElement, UserMultiSelectElement
from slack_sdk.models.views import View

from sched_slack_bot.views.schedule_dialog_constants import DISPLAY_NAME_BLOCK_ID, CHANNEL_INPUT_BLOCK_ID, \
    USERS_INPUT_BLOCK_ID

if TYPE_CHECKING:
    from sched_slack_bot.model.schedule import Schedule

from sched_slack_bot.views.datetime_selector import get_datetime_selector
from sched_slack_bot.views.input_block_with_block_id import InputBlockWithBlockId


def get_users_input(schedule: Optional[Schedule] = None) -> InputBlockWithBlockId:
    initial_users = None if schedule is None else schedule.members
    return InputBlockWithBlockId(label="Users to use in Rotation",
                                 element=UserMultiSelectElement(initial_users=initial_users),
                                 hint=PlainTextObject(text="The Users that should be part of the rotation"),
                                 block_id=USERS_INPUT_BLOCK_ID)


def get_channel_input(schedule: Optional[Schedule] = None) -> InputBlockWithBlockId:
    placeholder = "#channel" if schedule is None else None
    initial_conversation = None if schedule is None else schedule.channel_id_to_notify_in
    return InputBlockWithBlockId(label="Channel To Notify",
                                 element=ConversationSelectElement(placeholder=placeholder,
                                                                   initial_conversation=initial_conversation),
                                 hint=PlainTextObject(text="The channel to notify automatically"),
                                 block_id=CHANNEL_INPUT_BLOCK_ID)


def get_display_name_input(schedule: Optional[Schedule] = None) -> InputBlockWithBlockId:
    initial_value = "New Rotating Schedule" if schedule is None else schedule.display_name
    return InputBlockWithBlockId(label="Display Name",
                                 hint=PlainTextObject(text="Name for your rotating schedule"),
                                 element=PlainTextInputElement(initial_value=initial_value),
                                 block_id=DISPLAY_NAME_BLOCK_ID)


FIRST_ROTATION_INPUT = get_datetime_selector(label="First Rotation Reminder/Rotation")
SECOND_ROTATION_INPUT = get_datetime_selector(label="Second Rotation Reminder/Rotation")

SCHEDULE_NEW_DIALOG_CALL_BACK_ID = "SCHED_SLACK_BOT_NEW_SCHEDULE_SUBMIT_ID"
SCHEDULE_EDIT_DIALOG_CALL_BACK_ID = "SCHED_SLACK_BOT_EDIT_SCHEDULE_SUBMIT_ID"


def get_edit_schedule_block(schedule: Optional[Schedule] = None) -> View:
    modal_type = "Create" if schedule is None else "Edit"
    return View(type="modal",
                blocks=[
                    HeaderBlock(
                        text=PlainTextObject(text=f"{modal_type} an existing :calendar: Rotating Schedule")),
                    DividerBlock(),
                    get_display_name_input(schedule=schedule),
                    get_channel_input(schedule=schedule),
                    get_users_input(schedule=schedule),
                    *FIRST_ROTATION_INPUT.values(),
                    *SECOND_ROTATION_INPUT.values()

                ],
                title="Rotating Schedule",
                submit=modal_type,
                callback_id=SCHEDULE_NEW_DIALOG_CALL_BACK_ID)
