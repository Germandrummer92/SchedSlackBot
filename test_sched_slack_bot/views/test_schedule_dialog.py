import datetime
import uuid

import pytest
from slack_sdk.models.blocks import HeaderBlock, PlainTextInputElement, ConversationSelectElement, UserMultiSelectElement

from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.views.datetime_selector import get_datetime_selector
from sched_slack_bot.views.schedule_dialog import (
    get_edit_schedule_block,
    get_display_name_input,
    EDIT_MODAL_TYPE,
    CREATE_MODAL_TYPE,
    CREATE_NEW_SCHEDULE_DISPLAY_NAME,
    get_channel_input,
    CREATION_CHANNEL_PLACEHOLDER,
    get_users_input,
    get_first_rotation_block,
    get_second_rotation_block,
)
from sched_slack_bot.views.schedule_dialog_block_ids import (
    CREATE_NEW_SCHEDULE_VIEW_ID_PREFIX,
    FIRST_ROTATION_LABEL,
    SECOND_ROTATION_LABEL,
)


@pytest.fixture
def schedule() -> Schedule:
    return Schedule(
        id=str(uuid.uuid4()),
        display_name="Rotation Schedule",
        members=["U1", "U2"],
        next_rotation=datetime.datetime.now() + datetime.timedelta(milliseconds=100),
        time_between_rotations=datetime.timedelta(hours=2),
        channel_id_to_notify_in="C1",
        created_by="creator",
    )


def test_get_create_schedule_dialog() -> None:
    create_block = get_edit_schedule_block()

    assert create_block.submit is not None
    assert create_block.submit.text == CREATE_MODAL_TYPE
    assert isinstance(create_block.blocks[0], HeaderBlock)
    assert create_block.blocks[0].text is not None
    assert CREATE_MODAL_TYPE in create_block.blocks[0].text.text

    assert create_block.external_id is not None
    assert create_block.external_id.startswith(CREATE_NEW_SCHEDULE_VIEW_ID_PREFIX)


def test_get_edit_schedule_dialog(schedule: Schedule) -> None:
    create_block = get_edit_schedule_block(schedule=schedule)

    assert create_block.submit is not None
    assert create_block.submit.text == EDIT_MODAL_TYPE
    assert isinstance(create_block.blocks[0], HeaderBlock)
    assert create_block.blocks[0].text is not None
    assert EDIT_MODAL_TYPE in create_block.blocks[0].text.text

    assert create_block.external_id is not None
    assert create_block.external_id.startswith(schedule.id)


def test_get_display_name_input_creation() -> None:
    display_name_input = get_display_name_input()

    assert isinstance(display_name_input.element, PlainTextInputElement)
    assert display_name_input.element.initial_value == CREATE_NEW_SCHEDULE_DISPLAY_NAME


def test_get_display_name_input_edit(schedule: Schedule) -> None:
    display_name_input = get_display_name_input(schedule=schedule)

    assert isinstance(display_name_input.element, PlainTextInputElement)
    assert display_name_input.element.initial_value == schedule.display_name


def test_get_channel_input_creation() -> None:
    channel_input = get_channel_input()

    assert isinstance(channel_input.element, ConversationSelectElement)
    assert channel_input.element.placeholder is not None
    assert channel_input.element.placeholder.text == CREATION_CHANNEL_PLACEHOLDER
    assert channel_input.element.initial_conversation is None


def test_get_channel_input_edit(schedule: Schedule) -> None:
    channel_input = get_channel_input(schedule=schedule)

    assert isinstance(channel_input.element, ConversationSelectElement)
    assert channel_input.element.placeholder is None
    assert channel_input.element.initial_conversation == schedule.channel_id_to_notify_in


def test_get_user_input_creation() -> None:
    users_input = get_users_input()

    assert isinstance(users_input.element, UserMultiSelectElement)
    assert users_input.element.initial_users is None


def test_get_user_input_edit(schedule: Schedule) -> None:
    users_input = get_users_input(schedule=schedule)

    assert isinstance(users_input.element, UserMultiSelectElement)
    assert users_input.element.initial_users == schedule.members


def test_get_first_rotation_block_creation() -> None:
    rotation_block = get_first_rotation_block()

    assert rotation_block == get_datetime_selector(label=FIRST_ROTATION_LABEL, schedule_date=None)


def test_get_first_rotation_block_edit(schedule: Schedule) -> None:
    rotation_block = get_first_rotation_block(schedule=schedule)

    assert rotation_block == get_datetime_selector(label=FIRST_ROTATION_LABEL, schedule_date=schedule.next_rotation)


def test_get_second_rotation_block_creation() -> None:
    rotation_block = get_second_rotation_block()

    assert rotation_block == get_datetime_selector(label=SECOND_ROTATION_LABEL, schedule_date=None)


def test_get_second_rotation_block_edit(schedule: Schedule) -> None:
    rotation_block = get_second_rotation_block(schedule=schedule)

    assert rotation_block == get_datetime_selector(
        label=SECOND_ROTATION_LABEL, schedule_date=schedule.next_rotation + schedule.time_between_rotations
    )
