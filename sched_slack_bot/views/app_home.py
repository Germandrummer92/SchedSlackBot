import uuid
from typing import List

from slack_sdk.models.blocks import SectionBlock, TextObject, DividerBlock, ActionsBlock, ButtonElement, \
    MarkdownTextObject, PlainTextObject, HeaderBlock
from slack_sdk.models.views import View

from sched_slack_bot.model.schedule import Schedule

NO_SCHEDULES_BLOCK = SectionBlock(text=TextObject(
    type="mrkdwn",
    text="No Schedules configured yet :cry:, create one below to get started!"
))

CREATE_BUTTON_ACTION_ID = "SCHED_SLACK_BOT_CREATE"


def get_app_home_view(schedules: List[Schedule]) -> View:
    schedules_block = NO_SCHEDULES_BLOCK if len(schedules) == 0 else DividerBlock()

    return View(type="home",
                callback_id="home_view",
                blocks=[
                    HeaderBlock(text=PlainTextObject(
                        text="Welcome to the SchedSlack Bot :tada:"
                    )),
                    SectionBlock(text=MarkdownTextObject(
                        text="Your *One-Stop-Shop* for setting up rotating :calendar: schedules.")),
                    DividerBlock(),
                    schedules_block,
                    DividerBlock(),
                    SectionBlock(text=MarkdownTextObject(
                        text="Create a new Schedule"
                    )),
                    ActionsBlock(elements=[
                        ButtonElement(text=PlainTextObject(text="Create"), action_id=CREATE_BUTTON_ACTION_ID)])

                ])
