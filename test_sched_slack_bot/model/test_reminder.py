import datetime
import uuid

import pytest

from sched_slack_bot.model.reminder import Reminder
from sched_slack_bot.model.schedule import Schedule


@pytest.fixture()
def next_rotation_date() -> datetime.datetime:
    return datetime.datetime(year=2500, month=12, day=1, hour=12, minute=0, second=0)


@pytest.fixture
def schedule(next_rotation_date: datetime.datetime) -> Schedule:
    return Schedule(
        id=str(uuid.uuid4()),
        display_name="Rotation Schedule",
        members=["U1", "U2"],
        next_rotation=next_rotation_date,
        time_between_rotations=datetime.timedelta(seconds=2),
        channel_id_to_notify_in="C1",
        created_by="creator",
    )


@pytest.fixture()
def reminder(schedule: Schedule) -> Reminder:
    return Reminder(schedule=schedule)


class TestReminder:
    def test_next_next_rotation_date_is_formatted_correctly(
        self, reminder: Reminder, next_rotation_date: datetime.datetime
    ) -> None:
        assert reminder.next_next_rotation_date == "2500-12-01-12:00:00"

    def test_user_to_notify_is_correct(self, reminder: Reminder, schedule: Schedule) -> None:
        assert reminder.user_id_to_notify == schedule.members[schedule.current_index]

    def test_next_schedule_is_correct(self, reminder: Reminder, schedule: Schedule) -> None:
        assert reminder.next_schedule == schedule.next_schedule

    def test_next_user_is_correct(self, reminder: Reminder, schedule: Schedule) -> None:
        assert reminder.next_rotation_user == schedule.members[schedule.next_index]
