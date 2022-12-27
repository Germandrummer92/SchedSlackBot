import dataclasses
import datetime
import os
import uuid
from typing import List
from unittest import mock

import pytest
from slack_bolt import App
from slack_sdk import WebClient

from sched_slack_bot.controller import AppController
from sched_slack_bot.data.schedule_access import ScheduleAccess
from sched_slack_bot.model.reminder import Reminder
from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.reminder.scheduler import ReminderScheduler
from sched_slack_bot.reminder.sender import ReminderSender
from sched_slack_bot.utils.slack_typing_stubs import SlackEvent, SlackBody, SlackBodyUser, SlackView, SlackState, SlackAction
from sched_slack_bot.views.app_home import get_app_home_view
from sched_slack_bot.views.schedule_dialog import get_edit_schedule_block


@pytest.fixture
def controller() -> AppController:
    return AppController()


@pytest.fixture()
def mocked_reminder_sender() -> mock.MagicMock:
    return mock.MagicMock(spec=ReminderSender)


@pytest.fixture()
def mocked_app() -> mock.MagicMock:
    return mock.MagicMock(spec=App)


@pytest.fixture()
def mocked_schedule_access() -> mock.MagicMock:
    return mock.MagicMock(spec=ScheduleAccess)


@pytest.fixture()
def mocked_reminder_scheduler() -> mock.MagicMock:
    return mock.MagicMock(spec=ReminderScheduler)


@pytest.fixture()
def mocked_slack_client() -> mock.MagicMock:
    return mock.MagicMock(spec=WebClient)


@pytest.fixture()
def controller_with_mocks(
    controller: AppController,
    mocked_reminder_sender: mock.MagicMock,
    mocked_app: mock.MagicMock,
    mocked_schedule_access: mock.MagicMock,
    mocked_reminder_scheduler: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
) -> AppController:
    controller._reminder_sender = mocked_reminder_sender
    controller._app = mocked_app
    controller._reminder_scheduler = mocked_reminder_scheduler
    controller._slack_client = mocked_slack_client
    controller._schedule_access = mocked_schedule_access

    return controller


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


@pytest.fixture()
def slack_body() -> SlackBody:
    return SlackBody(
        trigger_id="trigger",
        user=SlackBodyUser(id="user", username="username", name="name", team_id="T123"),
        view=SlackView(state=SlackState(values={}), id="view"),
        actions=[],
    )


@pytest.mark.parametrize("required_missing_variable_name", ["MONGO_URL", "SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET"])
def test_controller_fails_without_required_environment_variables(
    controller: AppController, required_missing_variable_name: str
) -> None:
    os.environ.pop(required_missing_variable_name, None)
    with pytest.raises(RuntimeError):
        controller.start()


def test_handle_reminder_executed_saves_updated_schedule(
    controller_with_mocks: AppController, mocked_schedule_access: mock.MagicMock, schedule: Schedule
) -> None:
    controller_with_mocks.handle_reminder_executed(next_schedule=schedule)

    mocked_schedule_access.update_schedule.assert_called_once_with(schedule_id_to_update=schedule.id, new_schedule=schedule)


def test_app_home_opened_opens_app_home(
    controller_with_mocks: AppController,
    mocked_schedule_access: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
    schedule: Schedule,
) -> None:
    mocked_schedule_access.get_available_schedules.return_value = [schedule]
    user = "someUser"
    event = SlackEvent(user=user)

    controller_with_mocks.handle_app_home_opened(event=event)

    assert_published_home_view(mocked_slack_client=mocked_slack_client, schedules=[schedule], user=user)


def assert_published_home_view(mocked_slack_client: mock.MagicMock, schedules: List[Schedule], user: str) -> None:
    mocked_slack_client.views_publish.assert_called_once_with(user_id=user, view=get_app_home_view(schedules=schedules))


def test_handle_clicked_create_opens_schedule_dialog(
    controller_with_mocks: AppController,
    mocked_schedule_access: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
    slack_body: SlackBody,
    schedule: Schedule,
) -> None:
    mocked_schedule_access.get_available_schedules.return_value = [schedule]

    ack = mock.MagicMock()
    controller_with_mocks.handle_clicked_create_schedule(ack=ack, body=slack_body)

    ack.assert_called_once()
    mocked_slack_client.views_open.assert_called_once_with(trigger_id=slack_body["trigger_id"], view=get_edit_schedule_block())


def test_handle_submitted_create_schedule_creates_new_schedule(
    controller_with_mocks: AppController,
    mocked_schedule_access: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
    slack_body: SlackBody,
    mocked_reminder_scheduler: mock.MagicMock,
    mocked_reminder_sender: mock.MagicMock,
    schedule: Schedule,
) -> None:
    mocked_schedule_access.get_available_schedules.return_value = [schedule]
    ack = mock.MagicMock()
    with mock.patch("sched_slack_bot.controller.Schedule.from_modal_submission") as mocked_from_model_submission:
        mocked_from_model_submission.return_value = schedule
        controller_with_mocks.handle_submitted_create_schedule(ack=ack, body=slack_body)

    mocked_reminder_scheduler.schedule_reminder.assert_called_once_with(
        schedule=schedule, reminder_sender=mocked_reminder_sender
    )
    ack.assert_called_once()
    mocked_schedule_access.save_schedule.assert_called_once_with(schedule=schedule)
    assert_published_home_view(mocked_slack_client=mocked_slack_client, schedules=[schedule], user=slack_body["user"]["id"])


def test_handle_submitted_edit_schedule_updates_existing_schedule(
    controller_with_mocks: AppController,
    mocked_schedule_access: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
    slack_body: SlackBody,
    mocked_reminder_scheduler: mock.MagicMock,
    mocked_reminder_sender: mock.MagicMock,
    schedule: Schedule,
) -> None:
    mocked_schedule_access.get_available_schedules.return_value = [schedule]
    ack = mock.MagicMock()

    with mock.patch("sched_slack_bot.controller.Schedule.from_modal_submission") as mocked_from_model_submission:
        mocked_from_model_submission.return_value = schedule
        controller_with_mocks.handle_submitted_edit_schedule(ack=ack, body=slack_body)

    mocked_schedule_access.update_schedule.assert_called_once_with(schedule_id_to_update=schedule.id, new_schedule=schedule)
    mocked_reminder_scheduler.remove_reminder_for_schedule.assert_called_once_with(schedule_id=schedule.id)
    mocked_reminder_scheduler.schedule_reminder.assert_called_once_with(
        schedule=schedule, reminder_sender=mocked_reminder_sender
    )
    ack.assert_called_once()
    assert_published_home_view(mocked_slack_client=mocked_slack_client, schedules=[schedule], user=slack_body["user"]["id"])


def test_handle_delete_does_nothing_without_schedule(
    controller_with_mocks: AppController,
    mocked_schedule_access: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
    slack_body: SlackBody,
    mocked_reminder_scheduler: mock.MagicMock,
    schedule: Schedule,
) -> None:
    ack = mock.MagicMock()
    controller_with_mocks.handle_clicked_delete_button(ack=ack, body=slack_body)

    ack.assert_called_once()

    mocked_schedule_access.delete_schedule.assert_not_called()


def test_handle_delete_deletes_matching_schedule(
    controller_with_mocks: AppController,
    mocked_schedule_access: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
    slack_body: SlackBody,
    mocked_reminder_scheduler: mock.MagicMock,
    schedule: Schedule,
) -> None:
    slack_body["actions"] = [SlackAction(action_id="DELETE", block_id=schedule.id)]

    ack = mock.MagicMock()
    controller_with_mocks.handle_clicked_delete_button(ack=ack, body=slack_body)

    ack.assert_called_once()

    mocked_schedule_access.delete_schedule.assert_called_once_with(schedule_id=schedule.id)
    mocked_reminder_scheduler.remove_reminder_for_schedule.assert_called_once_with(schedule_id=schedule.id)
    assert_published_home_view(mocked_slack_client=mocked_slack_client, schedules=[], user=slack_body["user"]["id"])


def test_handle_skip_does_nothing_without_schedule(
    controller_with_mocks: AppController,
    mocked_schedule_access: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
    slack_body: SlackBody,
    mocked_reminder_scheduler: mock.MagicMock,
    schedule: Schedule,
) -> None:
    ack = mock.MagicMock()
    controller_with_mocks.handle_clicked_confirm_skip(ack=ack, body=slack_body)

    ack.assert_called_once()

    mocked_schedule_access.update_schedule.assert_not_called()


def test_handle_skip_does_nothing_without_matching_schedule(
    controller_with_mocks: AppController,
    mocked_schedule_access: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
    slack_body: SlackBody,
    mocked_reminder_scheduler: mock.MagicMock,
    schedule: Schedule,
) -> None:
    mocked_schedule_access.get_schedule.return_value = None
    slack_body["actions"] = [SlackAction(action_id="SKIP", block_id=schedule.id)]
    ack = mock.MagicMock()
    controller_with_mocks.handle_clicked_confirm_skip(ack=ack, body=slack_body)

    ack.assert_called_once()

    mocked_schedule_access.update_schedule.assert_not_called()


def test_handle_skip_skips_matching_schedule(
    controller_with_mocks: AppController,
    mocked_schedule_access: mock.MagicMock,
    mocked_slack_client: mock.MagicMock,
    slack_body: SlackBody,
    mocked_reminder_sender: mock.MagicMock,
    mocked_reminder_scheduler: mock.MagicMock,
    schedule: Schedule,
) -> None:
    schedule_with_skipped_index = dataclasses.replace(schedule, current_index=schedule.next_index)

    mocked_schedule_access.get_schedule.return_value = schedule
    slack_body["actions"] = [SlackAction(action_id="SKIP", block_id=schedule.id)]
    ack = mock.MagicMock()
    controller_with_mocks.handle_clicked_confirm_skip(ack=ack, body=slack_body)

    ack.assert_called_once()

    mocked_reminder_sender.send_skip_message.assert_called_once_with(reminder=Reminder(schedule))
    mocked_schedule_access.update_schedule.assert_called_once_with(
        schedule_id_to_update=schedule.id, new_schedule=schedule_with_skipped_index
    )
    mocked_reminder_scheduler.remove_reminder_for_schedule.assert_called_once_with(schedule_id=schedule.id)
    mocked_reminder_scheduler.schedule_reminder.assert_called_once_with(
        schedule=schedule_with_skipped_index, reminder_sender=mocked_reminder_sender
    )
