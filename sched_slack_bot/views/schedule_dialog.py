from __future__ import annotations

from enum import StrEnum
from typing import Optional, Dict

from slack_sdk.models.blocks import (
    HeaderBlock,
    PlainTextObject,
    DividerBlock,
    PlainTextInputElement,
    ConversationSelectElement,
    UserMultiSelectElement,
)
from slack_sdk.models.views import View

from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.views.datetime_selector import get_datetime_selector
from sched_slack_bot.views.input_block_with_block_id import InputBlockWithBlockId
from sched_slack_bot.views.schedule_dialog_block_ids import (
    DISPLAY_NAME_BLOCK_ID,
    CHANNEL_INPUT_BLOCK_ID,
    USERS_INPUT_BLOCK_ID,
    FIRST_ROTATION_LABEL,
    SECOND_ROTATION_LABEL,
    DatetimeSelectorType,
    CREATE_NEW_SCHEDULE_VIEW_ID,
)

CREATION_CHANNEL_PLACEHOLDER = "#channel"

CREATE_NEW_SCHEDULE_DISPLAY_NAME = "New Rotating Schedule"

EDIT_MODAL_TYPE = "Edit"
CREATE_MODAL_TYPE = "Create"


def get_users_input(schedule: Optional[Schedule] = None) -> InputBlockWithBlockId:
    initial_users = None if schedule is None else schedule.members
    return InputBlockWithBlockId(
        label="Users to use in Rotation",
        element=UserMultiSelectElement(initial_users=initial_users),
        hint=PlainTextObject(text="The Users that should be part of the rotation"),
        block_id=USERS_INPUT_BLOCK_ID,
    )


def get_channel_input(schedule: Optional[Schedule] = None) -> InputBlockWithBlockId:
    placeholder = CREATION_CHANNEL_PLACEHOLDER if schedule is None else None
    initial_conversation = None if schedule is None else schedule.channel_id_to_notify_in
    return InputBlockWithBlockId(
        label="Channel To Notify",
        element=ConversationSelectElement(placeholder=placeholder, initial_conversation=initial_conversation),
        hint=PlainTextObject(text="The channel to notify automatically"),
        block_id=CHANNEL_INPUT_BLOCK_ID,
    )


def get_display_name_input(schedule: Optional[Schedule] = None) -> InputBlockWithBlockId:
    initial_value = CREATE_NEW_SCHEDULE_DISPLAY_NAME if schedule is None else schedule.display_name
    return InputBlockWithBlockId(
        label="Display Name",
        hint=PlainTextObject(text="Name for your rotating schedule"),
        element=PlainTextInputElement(initial_value=initial_value),
        block_id=DISPLAY_NAME_BLOCK_ID,
    )


def get_first_rotation_block(schedule: Optional[Schedule] = None) -> Dict[DatetimeSelectorType, InputBlockWithBlockId]:
    schedule_date = schedule.next_rotation if schedule is not None else None
    return get_datetime_selector(label=FIRST_ROTATION_LABEL, schedule_date=schedule_date)


def get_second_rotation_block(schedule: Optional[Schedule] = None) -> Dict[DatetimeSelectorType, InputBlockWithBlockId]:
    schedule_date = schedule.next_rotation + schedule.time_between_rotations if schedule is not None else None
    return get_datetime_selector(label=SECOND_ROTATION_LABEL, schedule_date=schedule_date)


class ScheduleDialogCallback(StrEnum):
    CREATE_DIALOG = "SCHED_SLACK_BOT_NEW_SCHEDULE_SUBMIT_ID"
    EDIT_DIALOG = "SCHED_SLACK_BOT_EDIT_SCHEDULE_SUBMIT_ID"


def get_edit_schedule_block(
    schedule: Optional[Schedule] = None, callback: ScheduleDialogCallback = ScheduleDialogCallback.CREATE_DIALOG
) -> View:
    modal_type = CREATE_MODAL_TYPE if schedule is None else EDIT_MODAL_TYPE
    external_id = schedule.id if schedule is not None else CREATE_NEW_SCHEDULE_VIEW_ID
    return View(
        type="modal",
        external_id=external_id,
        blocks=[
            HeaderBlock(text=PlainTextObject(text=f"{modal_type} an existing :calendar: Rotating Schedule")),
            DividerBlock(),
            get_display_name_input(schedule=schedule),
            get_channel_input(schedule=schedule),
            get_users_input(schedule=schedule),
            *get_first_rotation_block(schedule=schedule).values(),
            *get_second_rotation_block(schedule=schedule).values(),
        ],
        title="Rotating Schedule",
        submit=modal_type,
        callback_id=callback,
    )
