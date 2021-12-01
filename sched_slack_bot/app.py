import logging
import os
from typing import Callable, Any

from slack_bolt import App
from slack_bolt.request.payload_utils import is_view_submission
from slack_sdk import WebClient

from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.model.slack_body import SlackBody
from sched_slack_bot.model.slack_event import SlackEvent
from sched_slack_bot.views.app_home import get_app_home_view, CREATE_BUTTON_ACTION_ID
from sched_slack_bot.views.schedule_dialog import SCHEDULE_NEW_DIALOG_CALL_BACK_ID, \
    SCHEDULE_NEW_DIALOG

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
logger = logging.getLogger(__name__)

app = App(
    name="sched_slack_bot",
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
    logger=logger
)


@app.event("app_home_opened")
def update_home_tab(client: WebClient, event: SlackEvent) -> None:
    user = event["user"]

    logger.info(f"{user=} clicked on App.Home")
    client.views_publish(
        user_id=user,
        view=get_app_home_view(schedules=[])
    )


@app.action(CREATE_BUTTON_ACTION_ID)
def clicked_create_schedule(ack: Callable[[], None], body: SlackBody, client: WebClient) -> None:
    ack()

    trigger_id = body["trigger_id"]

    client.views_open(trigger_id=trigger_id,
                      view=SCHEDULE_NEW_DIALOG
                      )


@app.view(SCHEDULE_NEW_DIALOG_CALL_BACK_ID, matchers=[is_view_submission])
def submitted_create_schedule(ack: Callable[[], None], body: SlackBody, *_: Any, **__: dict[str, Any]) -> None:
    ack()

    logger.info(f"Creating Schedule from {body['user']}")

    schedule = Schedule.from_modal_submission(submission_body=body)

    logger.info(f"Created Schedule {schedule}")


