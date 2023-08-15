import copy
import dataclasses
import datetime
import uuid
from typing import Dict

import pytest

from sched_slack_bot.model.schedule import Schedule, SERIALIZATION_DATE_FORMAT
from sched_slack_bot.utils.find_block_value import SlackValueContainerType
from sched_slack_bot.utils.slack_typing_stubs import SlackState, SlackView, SlackBody, SlackBodyUser, SlackInputBlockState
from sched_slack_bot.views.schedule_dialog_block_ids import (
    DISPLAY_NAME_BLOCK_ID,
    USERS_INPUT_BLOCK_ID,
    CHANNEL_INPUT_BLOCK_ID,
    DatetimeSelectorType,
    get_datetime_block_ids,
    FIRST_ROTATION_LABEL,
    SECOND_ROTATION_LABEL,
)


@pytest.fixture()
def next_rotation_date() -> datetime.datetime:
    return datetime.datetime(year=2500, month=11, day=1, hour=12, minute=0, second=0)


@pytest.fixture
def schedule(next_rotation_date: datetime.datetime) -> Schedule:
    return Schedule(
        id=str(uuid.uuid4()),
        display_name="Rotation Schedule",
        members=["U1", "U2"],
        next_rotation=next_rotation_date,
        time_between_rotations=datetime.timedelta(hours=2),
        channel_id_to_notify_in="C1",
        created_by="creator",
    )


@pytest.fixture()
def minimum_slack_body() -> SlackBody:
    return SlackBody(
        view=SlackView(state=SlackState(values={}), id="someView"),
        actions=[],
        user=SlackBodyUser(id="userId", username="username", name="name", team_id="team"),
        trigger_id="triggerId",
    )


def _add_valid_datetime_values(
    datetime_value: datetime.datetime, slack_body: SlackBody, date_input_block_ids: Dict[DatetimeSelectorType, str]
) -> None:
    slack_body["view"]["state"]["values"][date_input_block_ids[DatetimeSelectorType.DATE]] = {
        "subBlock": SlackInputBlockState(
            **{
                SlackValueContainerType.datepicker.value: datetime_value.date().isoformat(),
                "type": SlackValueContainerType.datepicker.name,
            }
        )
    }
    slack_body["view"]["state"]["values"][date_input_block_ids[DatetimeSelectorType.HOUR]] = {
        "subBlock": SlackInputBlockState(
            **{
                SlackValueContainerType.static_select.value: {"value": str(datetime_value.hour)},
                "type": SlackValueContainerType.static_select.name,
            }
        )
    }
    slack_body["view"]["state"]["values"][date_input_block_ids[DatetimeSelectorType.MINUTE]] = {
        "subBlock": SlackInputBlockState(
            **{
                SlackValueContainerType.static_select.value: {"value": str(datetime_value.minute)},
                "type": SlackValueContainerType.static_select.name,
            }
        )
    }


@pytest.fixture()
def valid_slack_body(minimum_slack_body: SlackBody, schedule: Schedule) -> SlackBody:
    valid_slack_body = copy.deepcopy(minimum_slack_body)

    valid_slack_body["view"]["external_id"] = schedule.id

    # mypy cant deal with dynamic typed dicts
    valid_slack_body["view"]["state"]["values"][DISPLAY_NAME_BLOCK_ID] = {
        "subBlock": SlackInputBlockState(
            **{
                SlackValueContainerType.static_select.value: {
                    "value": schedule.display_name,
                },
                "type": SlackValueContainerType.static_select.name,
            }
        )
    }

    valid_slack_body["view"]["state"]["values"][USERS_INPUT_BLOCK_ID] = {
        "subBlock": SlackInputBlockState(
            **{
                SlackValueContainerType.multi_users_select.value: schedule.members,
                "type": SlackValueContainerType.multi_users_select.name,
            }
        )
    }

    valid_slack_body["view"]["state"]["values"][CHANNEL_INPUT_BLOCK_ID] = {
        "subBlock": SlackInputBlockState(
            **{
                SlackValueContainerType.conversations_select.value: schedule.channel_id_to_notify_in,
                "type": SlackValueContainerType.conversations_select.name,
            }
        )
    }

    schedule_first_date = schedule.next_rotation
    schedule_second_date = schedule.next_rotation + schedule.time_between_rotations

    _add_valid_datetime_values(
        datetime_value=schedule_first_date,
        slack_body=valid_slack_body,
        date_input_block_ids=get_datetime_block_ids(label=FIRST_ROTATION_LABEL),
    )
    _add_valid_datetime_values(
        datetime_value=schedule_second_date,
        slack_body=valid_slack_body,
        date_input_block_ids=get_datetime_block_ids(label=SECOND_ROTATION_LABEL),
    )

    return valid_slack_body


def test_schedule_has_correct_next_next_date(schedule: Schedule) -> None:
    assert schedule.next_next_rotation_date == schedule.next_rotation + schedule.time_between_rotations


def test_next_schedule_has_correct_next_index(schedule: Schedule) -> None:
    assert schedule.next_index == 1

    schedule_at_end_of_rotation = dataclasses.replace(schedule, current_index=1)
    assert schedule_at_end_of_rotation.next_index == 0


def test_next_schedule_has_correct_next_schedule(schedule: Schedule) -> None:
    prev_schedule = schedule
    next_schedule = schedule.next_schedule
    for i in range(5):
        assert next_schedule.current_index == prev_schedule.next_index
        assert next_schedule.next_rotation == prev_schedule.next_next_rotation_date
        prev_schedule = next_schedule
        next_schedule = next_schedule.next_schedule


def test_next_schedule_has_correct_user_to_notify(schedule: Schedule) -> None:
    assert schedule.current_user_to_notify == "U1"


def test_schedule_to_json_is_correct(schedule: Schedule) -> None:
    assert schedule.as_json() == {
        "id": schedule.id,
        "display_name": schedule.display_name,
        "members": schedule.members,
        "next_rotation": schedule.next_rotation.strftime(SERIALIZATION_DATE_FORMAT),
        "time_between_rotations": schedule.time_between_rotations.total_seconds(),
        "channel_id_to_notify_in": schedule.channel_id_to_notify_in,
        "created_by": schedule.created_by,
        "current_index": schedule.current_index,
    }


def test_schedule_can_be_deserialized(schedule: Schedule) -> None:
    json_schedule = schedule.as_json()

    assert Schedule.from_json(json=json_schedule) == schedule


def test_schedule_without_time_between_rotations_raises() -> None:
    with pytest.raises(ValueError):
        Schedule(
            id="some_id",
            display_name="some name",
            members=["some_member"],
            next_rotation=datetime.datetime.now() + datetime.timedelta(seconds=5),
            time_between_rotations=datetime.timedelta(),
            channel_id_to_notify_in="some channel id",
            created_by="some user",
            current_index=0,
        )


def test_schedule_without_members_raises() -> None:
    with pytest.raises(ValueError):
        Schedule(
            id="some_id",
            display_name="some name",
            members=[],
            next_rotation=datetime.datetime.now() + datetime.timedelta(seconds=5),
            time_between_rotations=datetime.timedelta(seconds=100),
            channel_id_to_notify_in="some channel id",
            created_by="some user",
            current_index=0,
        )


def test_schedule_from_modal_submission_raises_with_no_values(schedule: Schedule, minimum_slack_body: SlackBody) -> None:
    with pytest.raises(ValueError):
        Schedule.from_modal_submission(submission_body=minimum_slack_body)


@pytest.mark.parametrize(
    "missing_block_id",
    [
        CHANNEL_INPUT_BLOCK_ID,
        USERS_INPUT_BLOCK_ID,
        DISPLAY_NAME_BLOCK_ID,
        *[
            get_datetime_block_ids(label=FIRST_ROTATION_LABEL)[k]
            for k in get_datetime_block_ids(label=FIRST_ROTATION_LABEL).keys()
        ],
        *[
            get_datetime_block_ids(label=SECOND_ROTATION_LABEL)[k]
            for k in get_datetime_block_ids(label=SECOND_ROTATION_LABEL).keys()
        ],
    ],
)
def test_schedule_from_modal_submission_raises_with_missing_values(
    schedule: Schedule, valid_slack_body: SlackBody, missing_block_id: str
) -> None:
    del valid_slack_body["view"]["state"]["values"][missing_block_id]
    with pytest.raises(ValueError):
        Schedule.from_modal_submission(submission_body=valid_slack_body)


def test_schedule_from_modal_submission_works(schedule: Schedule, valid_slack_body: SlackBody) -> None:
    from_modal = Schedule.from_modal_submission(submission_body=valid_slack_body)

    assert from_modal.display_name == schedule.display_name
    assert from_modal.members == schedule.members
    assert from_modal.channel_id_to_notify_in == schedule.channel_id_to_notify_in
    assert from_modal.next_rotation == schedule.next_rotation
    assert from_modal.current_index == schedule.current_index
    assert from_modal.time_between_rotations == schedule.time_between_rotations
    assert from_modal.id == schedule.id
