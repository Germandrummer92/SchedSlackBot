import dataclasses
import logging
import os
from typing import Optional

from slack_bolt import App, Ack
from slack_bolt.request.payload_utils import is_view_submission
from slack_sdk import WebClient

from sched_slack_bot.data.mongo.mongo_schedule_access import MongoScheduleAccess
from sched_slack_bot.data.schedule_access import ScheduleAccess
from sched_slack_bot.model.reminder import Reminder
from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.reminder.scheduler import ReminderScheduler
from sched_slack_bot.reminder.slack_sender import SlackReminderSender
from sched_slack_bot.utils.fix_schedule_from_the_past import fix_schedule_from_the_past
from sched_slack_bot.utils.slack_typing_stubs import SlackBody, SlackEvent
from sched_slack_bot.views.app_home import get_app_home_view, CREATE_BUTTON_ACTION_ID
from sched_slack_bot.views.reminder_blocks import SKIP_CURRENT_MEMBER_ACTION_ID
from sched_slack_bot.views.schedule_blocks import DELETE_SCHEDULE_ACTION_ID
from sched_slack_bot.views.schedule_dialog import SCHEDULE_NEW_DIALOG, SCHEDULE_NEW_DIALOG_CALL_BACK_ID

logger = logging.getLogger(__name__)


class UnstartedControllerException(Exception):
    pass


class AppController:
    def __init__(self) -> None:
        self._schedule_access: Optional[ScheduleAccess] = None
        self._slack_client: Optional[WebClient] = None
        self._reminder_scheduler: Optional[ReminderScheduler] = None
        self._reminder_sender: Optional[SlackReminderSender] = None
        self._app: Optional[App] = None

    @property
    def schedule_access(self) -> ScheduleAccess:
        if self._schedule_access is None:
            raise UnstartedControllerException("Controller not yet started, please call start before!")

        return self._schedule_access

    @property
    def slack_client(self) -> WebClient:
        if self._slack_client is None:
            raise UnstartedControllerException("Controller not yet started, please call start before!")

        return self._slack_client

    @property
    def reminder_scheduler(self) -> ReminderScheduler:
        if self._reminder_scheduler is None:
            raise UnstartedControllerException("Controller not yet started, please call start before!")

        return self._reminder_scheduler

    @property
    def reminder_sender(self) -> SlackReminderSender:
        if self._reminder_sender is None:
            raise UnstartedControllerException("Controller not yet started, please call start before!")

        return self._reminder_sender

    @property
    def app(self) -> App:
        if self._app is None:
            raise UnstartedControllerException("Controller unstarted, please call start before!")

        return self._app

    def start(self) -> None:
        mongo_url = os.environ.get("MONGO_URL")
        slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
        slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
        port = int(os.environ.get("PORT", 3000))

        if mongo_url is None or slack_bot_token is None or slack_signing_secret is None:
            raise RuntimeError("Environment variables 'MONGO_URL', "
                               "'SLACK_BOT_TOKEN' and 'SLACK_SIGNING_SECRET' are required")

        self._schedule_access = MongoScheduleAccess(mongo_url=mongo_url)
        self._slack_client = WebClient(token=slack_bot_token)
        self._reminder_sender = SlackReminderSender(client=self._slack_client)
        self._reminder_scheduler = ReminderScheduler(reminder_executed_callback=self.handle_reminder_executed)
        self._app = App(name="sched_slack_bot",
                        token=slack_bot_token,
                        signing_secret=slack_signing_secret,
                        logger=logger)

        self._start_all_saved_schedules()
        self._register_listeners()
        self._app.start(port=port)

    def _start_all_saved_schedules(self) -> None:
        saved_schedules = self.schedule_access.get_available_schedules()

        logger.info(f"Found {len(saved_schedules)} schedules to start reminders for!")

        schedules_to_start = list(map(fix_schedule_from_the_past, saved_schedules))
        self.reminder_scheduler.schedule_all_reminders(schedules=schedules_to_start,
                                                       reminder_sender=self.reminder_sender)

        logger.info(f"Started {len(schedules_to_start)} reminders!")

    def _register_listeners(self) -> None:
        self.app.event(event="app_home_opened")(self.handle_app_home_opened)
        self.app.block_action(constraints=DELETE_SCHEDULE_ACTION_ID)(self.handle_clicked_delete_button)
        self.app.block_action(constraints=CREATE_BUTTON_ACTION_ID)(self.handle_clicked_create_schedule)
        self.app.action(constraints=SKIP_CURRENT_MEMBER_ACTION_ID)(self.handle_clicked_confirm_skip)
        self.app.view(constraints=SCHEDULE_NEW_DIALOG_CALL_BACK_ID, matchers=[is_view_submission])(
            self.handle_submitted_create_schedule)

    def handle_reminder_executed(self, next_schedule: Schedule) -> None:
        self.schedule_access.update_schedule(schedule_id_to_update=next_schedule.id,
                                             new_schedule=next_schedule)

    def handle_app_home_opened(self, event: SlackEvent) -> None:
        user = event["user"]

        logger.info(f"{user=} clicked on App.Home")
        self._update_app_home(user_id=user)

    def handle_clicked_delete_button(self, ack: Ack, body: SlackBody) -> None:
        ack()
        actions = body["actions"]

        if len(actions) != 1:
            logger.error(f"Got an unexpected list of actions for the delete button: {actions}")
            return

        schedule_id = actions[0]["block_id"]
        logger.info(f"Confirmed Deletion of schedule {schedule_id}")

        self.reminder_scheduler.remove_reminder_for_schedule(schedule_id=schedule_id)
        self.schedule_access.delete_schedule(schedule_id=schedule_id)
        self._update_app_home(user_id=body["user"]["id"])

    def _update_app_home(self, user_id: str) -> None:
        self.slack_client.views_publish(
            user_id=user_id,
            view=get_app_home_view(schedules=self.schedule_access.get_available_schedules())
        )

    def handle_clicked_create_schedule(self, ack: Ack, body: SlackBody) -> None:
        ack()
        logger.info(f"User {body['user']} clicked the create button")

        trigger_id = body["trigger_id"]

        self.slack_client.views_open(trigger_id=trigger_id,
                                     view=SCHEDULE_NEW_DIALOG)

    def handle_submitted_create_schedule(self, ack: Ack, body: SlackBody) -> None:
        ack()

        logger.info(f"Creating Schedule from {body['user']}")

        schedule = Schedule.from_modal_submission(submission_body=body)

        self.reminder_scheduler.schedule_reminder(schedule=schedule, reminder_sender=self.reminder_sender)
        self.schedule_access.save_schedule(schedule=schedule)

        logger.info(f"Created Schedule {schedule}")
        self._update_app_home(user_id=body["user"]["id"])

    def handle_clicked_confirm_skip(self, ack: Ack, body: SlackBody) -> None:
        ack()

        actions = body["actions"]

        if len(actions) != 1:
            logger.error(f"Got an unexpected list of actions for the skip button: {actions}")
            return

        schedule_id = actions[0]["block_id"]

        logger.info(f"Clicked Skip current Schedule user from {body['user']} for schedule {schedule_id}")

        schedule = self.schedule_access.get_schedule(schedule_id=schedule_id)
        if schedule is None:
            logger.error(f"Error when skipping for schedule with id {schedule_id}, already deleted!")
            return

        self.reminder_sender.send_skip_message(reminder=Reminder(schedule=schedule))

        schedule_with_skipped_index = dataclasses.replace(schedule, current_index=schedule.next_index)

        self.schedule_access.update_schedule(schedule_id_to_update=schedule_id,
                                             new_schedule=schedule_with_skipped_index)
        self.reminder_scheduler.remove_reminder_for_schedule(schedule_id=schedule_id)
        self.reminder_scheduler.schedule_reminder(schedule=schedule_with_skipped_index,
                                                  reminder_sender=self.reminder_sender)

        logger.info(f"Successfully skipped current schedule user from {body['user']} for schedule {schedule_id}")
