import copy
import dataclasses
import datetime
import uuid
from typing import Dict

import pytest

from sched_slack_bot.model.schedule import Schedule, SERIALIZATION_DATE_FORMAT
from sched_slack_bot.utils.find_block_value import SlackValueContainerType
from sched_slack_bot.utils.slack_typing_stubs import SlackState, SlackView, SlackBody, SlackBodyUser, \
    SlackInputBlockState
from sched_slack_bot.views.datetime_selector import DatetimeSelectorType
from sched_slack_bot.views.input_block_with_block_id import InputBlockWithBlockId
from sched_slack_bot.views.schedule_dialog import CHANNEL_INPUT, DISPLAY_NAME_INPUT, USERS_INPUT, \
    FIRST_ROTATION_INPUT, SECOND_ROTATION_INPUT


@pytest.fixture()
def next_rotation_date() -> datetime.datetime:
    return datetime.datetime(year=2500, month=12, day=1, hour=12, minute=0, second=0)


@pytest.fixture
def schedule(next_rotation_date: datetime.datetime) -> Schedule:
    return Schedule(id=str(uuid.uuid4()),
                    display_name="Rotation Schedule",
                    members=["U1", "U2"],
                    next_rotation=next_rotation_date,
                    time_between_rotations=datetime.timedelta(hours=2),
                    channel_id_to_notify_in="C1",
                    created_by="creator")


@pytest.fixture()
def minimum_slack_body() -> SlackBody:
    return SlackBody(
        view=SlackView(state=SlackState(values={}),
                       id="someView"),
        actions=[],
        user=SlackBodyUser(id="userId", username="username",
                           name="name", team_id="team"),
        trigger_id="triggerId"
    )


def _add_valid_datetime_values(datetime_value: datetime.datetime, slack_body: SlackBody,
                               date_input: Dict[DatetimeSelectorType, InputBlockWithBlockId]) -> None:
    slack_body["view"]["state"]["values"][date_input[DatetimeSelectorType.DATE].block_id] = {
        "subBlock": SlackInputBlockState(
            **{SlackValueContainerType.datepicker.value: datetime_value.date().isoformat(),  # type: ignore
               "type": SlackValueContainerType.datepicker.name})}
    slack_body["view"]["state"]["values"][date_input[DatetimeSelectorType.HOUR].block_id] = {
        "subBlock": SlackInputBlockState(
            **{SlackValueContainerType.static_select.value: {"value": str(datetime_value.hour)},  # type: ignore
               "type": SlackValueContainerType.static_select.name})}
    slack_body["view"]["state"]["values"][date_input[DatetimeSelectorType.MINUTE].block_id] = {
        "subBlock": SlackInputBlockState(
            **{SlackValueContainerType.static_select.value: {"value": str(datetime_value.minute)},  # type: ignore
               "type": SlackValueContainerType.static_select.name})}


@pytest.fixture()
def valid_slack_body(minimum_slack_body: SlackBody, schedule: Schedule) -> SlackBody:
    valid_slack_body = copy.deepcopy(minimum_slack_body)

    # mypy cant deal with dynamic typed dicts
    valid_slack_body["view"]["state"]["values"][DISPLAY_NAME_INPUT.block_id] = {
        "subBlock": SlackInputBlockState(**{SlackValueContainerType.static_select.value: {  # type: ignore
            "value": schedule.display_name, },
            "type": SlackValueContainerType.static_select.name})}

    valid_slack_body["view"]["state"]["values"][USERS_INPUT.block_id] = {
        "subBlock": SlackInputBlockState(
            **{SlackValueContainerType.multi_users_select.value: schedule.members,  # type: ignore
               "type": SlackValueContainerType.multi_users_select.name})}

    valid_slack_body["view"]["state"]["values"][CHANNEL_INPUT.block_id] = {
        "subBlock": SlackInputBlockState(
            **{SlackValueContainerType.conversations_select.value: schedule.channel_id_to_notify_in,  # type: ignore
               "type": SlackValueContainerType.conversations_select.name})}

    schedule_first_date = schedule.next_rotation
    schedule_second_date = schedule.next_rotation + schedule.time_between_rotations

    _add_valid_datetime_values(datetime_value=schedule_first_date, slack_body=valid_slack_body,
                               date_input=FIRST_ROTATION_INPUT)
    _add_valid_datetime_values(datetime_value=schedule_second_date, slack_body=valid_slack_body,
                               date_input=SECOND_ROTATION_INPUT)

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
        "current_index": schedule.current_index
    }


def test_schedule_can_be_deserialized(schedule: Schedule) -> None:
    json_schedule = schedule.as_json()

    assert Schedule.from_json(json=json_schedule) == schedule


def test_schedule_from_modal_submission_raises_with_no_values(schedule: Schedule,
                                                              minimum_slack_body: SlackBody) -> None:
    with pytest.raises(ValueError):
        Schedule.from_modal_submission(submission_body=minimum_slack_body)


@pytest.mark.parametrize("missing_block_id", [CHANNEL_INPUT.block_id, USERS_INPUT.block_id,
                                              DISPLAY_NAME_INPUT.block_id,
                                              *[FIRST_ROTATION_INPUT[k].block_id for k in FIRST_ROTATION_INPUT.keys()],
                                              *[SECOND_ROTATION_INPUT[k].block_id for k in
                                                SECOND_ROTATION_INPUT.keys()],
                                              ])
def test_schedule_from_modal_submission_raises_with_missing_values(schedule: Schedule,
                                                                   valid_slack_body: SlackBody,
                                                                   missing_block_id: str) -> None:
    del valid_slack_body["view"]["state"]["values"][missing_block_id]
    with pytest.raises(ValueError):
        Schedule.from_modal_submission(submission_body=valid_slack_body)


def test_schedule_from_modal_submission_works(schedule: Schedule,
                                              valid_slack_body: SlackBody) -> None:
    from_modal = Schedule.from_modal_submission(submission_body=valid_slack_body)

    assert from_modal.display_name == schedule.display_name
    assert from_modal.members == schedule.members
    assert from_modal.channel_id_to_notify_in == schedule.channel_id_to_notify_in
    assert from_modal.next_rotation == schedule.next_rotation
    assert from_modal.current_index == schedule.current_index
    assert from_modal.time_between_rotations == schedule.time_between_rotations
