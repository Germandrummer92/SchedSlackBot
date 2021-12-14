import datetime
import uuid
from unittest import mock

import pytest
from slack_sdk import WebClient

from sched_slack_bot.model.reminder import Reminder
from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.reminder.slack_sender import SlackReminderSender
from sched_slack_bot.views.reminder_blocks import get_reminder_text, get_reminder_blocks, get_skip_text, get_skip_blocks


@pytest.fixture
def schedule() -> Schedule:
    return Schedule(id=str(uuid.uuid4()),
                    display_name="Rotation Schedule",
                    members=["U1", "U2"],
                    next_rotation=datetime.datetime.now(),
                    time_between_rotations=datetime.timedelta(hours=2),
                    channel_id_to_notify_in="C1",
                    created_by="creator")


@pytest.fixture
def reminder(schedule: Schedule) -> Reminder:
    return Reminder(schedule=schedule)


@pytest.fixture()
def client() -> mock.MagicMock:
    return mock.MagicMock(spec=WebClient)


@pytest.fixture
def slack_sender(client: mock.MagicMock) -> SlackReminderSender:
    return SlackReminderSender(client=client)


def test_send_reminder(slack_sender: SlackReminderSender,
                       client: mock.MagicMock, reminder: Reminder) -> None:
    slack_sender.send_reminder(reminder=reminder)

    client.chat_postMessage.assert_called_once_with(channel=reminder.channel_id_to_notify_in,
                                                    # used for screen readers, if blocks can't be rendered
                                                    text=get_reminder_text(reminder=reminder),
                                                    blocks=get_reminder_blocks(reminder=reminder))


def test_skip_reminder(slack_sender: SlackReminderSender,
                       client: mock.MagicMock, reminder: Reminder) -> None:
    slack_sender.send_skip_message(reminder=reminder)

    client.chat_postMessage.assert_called_once_with(channel=reminder.channel_id_to_notify_in,
                                                    # used for screen readers, if blocks can't be rendered
                                                    text=get_skip_text(reminder=reminder),
                                                    blocks=get_skip_blocks(reminder=reminder))
