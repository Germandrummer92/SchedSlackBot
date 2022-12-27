import datetime
from typing import Generator
from unittest import mock

import pytest

from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.utils.fix_schedule_from_the_past import fix_schedule_from_the_past


@pytest.fixture()
def datetime_now() -> datetime.datetime:
    return datetime.datetime(year=2000, month=1, day=1, hour=1, minute=0, second=0)


@pytest.fixture
def schedule_in_the_past(datetime_now: datetime.datetime) -> Schedule:
    return Schedule(
        id="id",
        display_name="display",
        members=[],
        next_rotation=datetime_now - datetime.timedelta(hours=1),
        time_between_rotations=datetime.timedelta(days=14),
        channel_id_to_notify_in="channelId",
        created_by="creator",
        current_index=0,
    )


@pytest.fixture
def schedule_in_the_future(datetime_now: datetime.datetime) -> Schedule:
    return Schedule(
        id="id",
        display_name="display",
        members=[],
        next_rotation=datetime_now + datetime.timedelta(hours=1),
        time_between_rotations=datetime.timedelta(days=14),
        channel_id_to_notify_in="channelId",
        created_by="creator",
        current_index=0,
    )


@pytest.fixture(autouse=True)
def mocked_datetime_now(datetime_now: datetime.datetime) -> Generator[mock.MagicMock, None, None]:
    with mock.patch("sched_slack_bot.utils.fix_schedule_from_the_past.datetime.datetime") as mocked_datetime:
        mocked_datetime.now.return_value = datetime_now
        mocked_datetime.side_effect = lambda *args, **kw: datetime.datetime(*args, **kw)
        yield mocked_datetime


def test_it_correctly_fixes_schedule_in_the_past(schedule_in_the_past: Schedule, datetime_now: datetime.datetime) -> None:
    fixed_schedule = fix_schedule_from_the_past(schedule=schedule_in_the_past)
    expected_date = schedule_in_the_past.next_rotation + schedule_in_the_past.time_between_rotations

    assert fixed_schedule.next_rotation == expected_date
    assert fixed_schedule.id == schedule_in_the_past.id
    assert fixed_schedule.display_name == schedule_in_the_past.display_name
    assert fixed_schedule.time_between_rotations == schedule_in_the_past.time_between_rotations
    assert fixed_schedule.current_index == schedule_in_the_past.current_index
    assert fixed_schedule.created_by == schedule_in_the_past.created_by
    assert fixed_schedule.channel_id_to_notify_in == schedule_in_the_past.channel_id_to_notify_in
    assert fixed_schedule.members == schedule_in_the_past.members


def test_it_doesnt_change_schedule_in_the_future(schedule_in_the_future: Schedule) -> None:
    assert fix_schedule_from_the_past(schedule=schedule_in_the_future) == schedule_in_the_future
