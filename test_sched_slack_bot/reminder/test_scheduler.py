import datetime
import time
import uuid
from typing import Any
from unittest import mock

import pytest

from sched_slack_bot.model.reminder import Reminder
from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.reminder.scheduler import ReminderScheduler
from sched_slack_bot.reminder.sender import ReminderSender


@pytest.fixture(params=[mock.MagicMock(), None])
def scheduler(request: Any) -> ReminderScheduler:
    if isinstance(request.param, mock.MagicMock):
        request.param.reset_mock()
    return ReminderScheduler(reminder_executed_callback=request.param)


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


@pytest.fixture
def reminder(schedule: Schedule) -> Reminder:
    return Reminder(schedule=schedule)


@pytest.fixture()
def reminder_sender() -> mock.MagicMock:
    return mock.MagicMock(spec=ReminderSender)


def test_execute_unscheduled_reminder(
    scheduler: ReminderScheduler, reminder: Reminder, reminder_sender: mock.MagicMock
) -> None:
    # do not schedule next reminder
    scheduler.schedule_reminder = mock.MagicMock()  # type: ignore
    scheduler.execute_reminder(reminder=reminder, reminder_sender=reminder_sender)

    reminder_sender.send_reminder.assert_called_once_with(reminder=reminder)
    scheduler.schedule_reminder.assert_called_once_with(schedule=reminder.next_schedule, reminder_sender=reminder_sender)

    if isinstance(scheduler._reminder_executed_callback, mock.MagicMock):
        scheduler._reminder_executed_callback.assert_called_once_with(reminder.next_schedule)


def test_schedule_all_reminders(
    scheduler: ReminderScheduler, reminder: Reminder, schedule: Schedule, reminder_sender: mock.MagicMock
) -> None:
    scheduler.schedule_all_reminders(schedules=[schedule, schedule], reminder_sender=reminder_sender)
    # override schedule reminder now to not continuously schedule
    scheduler.schedule_reminder = mock.MagicMock()  # type: ignore

    while reminder_sender.send_reminder.call_count == 0:
        # no idle waiting
        time.sleep(0.1)

    assert reminder_sender.send_reminder.call_count == 2
    scheduler.schedule_reminder.assert_called_with(schedule=reminder.next_schedule, reminder_sender=reminder_sender)
    if isinstance(scheduler._reminder_executed_callback, mock.MagicMock):
        scheduler._reminder_executed_callback.assert_called_with(reminder.next_schedule)


def test_schedule_reminder(
    scheduler: ReminderScheduler, reminder: Reminder, schedule: Schedule, reminder_sender: mock.MagicMock
) -> None:
    scheduler.schedule_reminder(schedule=schedule, reminder_sender=reminder_sender)
    # override schedule reminder now to not continuously schedule
    scheduler.schedule_reminder = mock.MagicMock()  # type: ignore

    while reminder_sender.send_reminder.call_count == 0:
        # no idle waiting
        time.sleep(0.1)

    reminder_sender.send_reminder.assert_called_once()
    scheduler.schedule_reminder.assert_called_once_with(schedule=reminder.next_schedule, reminder_sender=reminder_sender)
    if isinstance(scheduler._reminder_executed_callback, mock.MagicMock):
        scheduler._reminder_executed_callback.assert_called_once_with(reminder.next_schedule)


def test_stop_reminder(
    scheduler: ReminderScheduler, reminder: Reminder, schedule: Schedule, reminder_sender: mock.MagicMock
) -> None:
    scheduler.schedule_reminder(schedule=schedule, reminder_sender=reminder_sender)
    scheduler.remove_reminder_for_schedule(schedule_id=schedule.id)

    now = datetime.datetime.now()
    while now < schedule.next_rotation:
        # no idle waiting
        time.sleep(0.1)
        now = datetime.datetime.now()

    reminder_sender.assert_not_called()


@mock.patch("sched_slack_bot.reminder.scheduler.threading.Timer")
def test_schedule_reminder_starts_daemon_threads(
    mocked_timer: mock.MagicMock,
    scheduler: ReminderScheduler,
    reminder: Reminder,
    schedule: Schedule,
    reminder_sender: mock.MagicMock,
) -> None:
    scheduler.schedule_reminder(schedule=schedule, reminder_sender=reminder_sender)

    # need to explicitly assert on true value, MagicMock is truthy otherwise
    assert mocked_timer.return_value.daemon is True
