import datetime
import logging
import os
from typing import Callable

from slack_bolt import App
from slack_bolt.request.payload_utils import is_view_submission
from slack_sdk import WebClient

from sched_slack_bot.data.mongo.mongo_schedule_access import MongoScheduleAccess
from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.model.slack_body import SlackBody
from sched_slack_bot.model.slack_event import SlackEvent
from sched_slack_bot.reminder.scheduler import REMINDER_SCHEDULER
from sched_slack_bot.reminder.slack_sender import SlackReminderSender
from sched_slack_bot.utils.fix_schedule_from_the_past import fix_schedule_from_the_past
from sched_slack_bot.views.app_home import get_app_home_view, CREATE_BUTTON_ACTION_ID
from sched_slack_bot.views.schedule_dialog import SCHEDULE_NEW_DIALOG_CALL_BACK_ID, \
    SCHEDULE_NEW_DIALOG

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
MONGO_URL = os.environ["MONGO_URL"]
logger = logging.getLogger(__name__)

app = App(
    name="sched_slack_bot",
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    logger=logger,
)

data_access = MongoScheduleAccess(mongo_url=MONGO_URL)
slack_client = WebClient(token=SLACK_BOT_TOKEN)
reminder_sender = SlackReminderSender(client=slack_client)


def start_all_schedules() -> None:
    saved_schedules = data_access.get_available_schedules()

    schedules_to_start = list(map(fix_schedule_from_the_past, saved_schedules))

    REMINDER_SCHEDULER.schedule_all_reminders(schedules=schedules_to_start, reminder_sender=reminder_sender)


@app.event("app_home_opened")
def update_home_tab(client: WebClient, event: SlackEvent) -> None:
    user = event["user"]

    logger.info(f"{user=} clicked on App.Home")
    client.views_publish(
        user_id=user,
        view=get_app_home_view(schedules=data_access.get_available_schedules())
    )


@app.action(CREATE_BUTTON_ACTION_ID)
def clicked_create_schedule(ack: Callable[[], None], body: SlackBody) -> None:
    ack()

    trigger_id = body["trigger_id"]

    slack_client.views_open(trigger_id=trigger_id,
                            view=SCHEDULE_NEW_DIALOG,
                            )


@app.view(SCHEDULE_NEW_DIALOG_CALL_BACK_ID, matchers=[is_view_submission])
def submitted_create_schedule(ack: Callable[[], None], body: SlackBody) -> None:
    ack()

    logger.info(f"Creating Schedule from {body['user']}")

    schedule = Schedule.from_modal_submission(submission_body=body)

    REMINDER_SCHEDULER.schedule_reminder(schedule=schedule, reminder_sender=reminder_sender)
    data_access.save_schedule(schedule=schedule)

    logger.info(f"Created Schedule {schedule}")
    slack_client.views_publish(
        view=get_app_home_view(schedules=data_access.get_available_schedules()),
        user_id=body["user"]["id"]
    )
