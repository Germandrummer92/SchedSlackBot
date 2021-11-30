from slack_sdk.models.blocks import HeaderBlock, PlainTextObject, DividerBlock, InputBlock, PlainTextInputElement, \
    ConversationSelectElement, UserMultiSelectElement
from slack_sdk.models.views import View

from sched_slack_bot.views.datetime_selector import get_datetime_selector

USERS_INPUT = InputBlock(label="Users to use in Rotation", element=UserMultiSelectElement(),
                         hint=PlainTextObject(text="The Users that should be part of the rotation"),
                         block_id="NEW_SCHEDULE_USERS_INPUT")

CHANNEL_INPUT = InputBlock(label="Channel To Notify", element=ConversationSelectElement(placeholder="#channel"),
                           hint=PlainTextObject(text="The channel to notify automatically"),
                           block_id="NEW_SCHEDULE_CHANNEL_INPUT")

DISPLAY_NAME_INPUT = InputBlock(label="Display Name", hint=PlainTextObject(text="Name for your rotating schedule"),
                                element=PlainTextInputElement(initial_value="New Rotating Schedule"),
                                block_id="NEW_SCHEDULE_DISPLAY_NAME_INPUT")

FIRST_ROTATION_INPUT = get_datetime_selector(label="First Rotation Reminder/Rotation")
SECOND_ROTATION_INPUT = get_datetime_selector(label="Second Rotation Reminder/Rotation")

SCHEDULE_NEW_DIALOG_CALL_BACK_ID = "SCHED_SLACK_BOT_NEW_SCHEDULE_SUBMIT_ID"

SCHEDULE_NEW_DIALOG = View(type="modal",
                           blocks=[
                               HeaderBlock(
                                   text=PlainTextObject(text="Create a new :calendar: Rotating Schedule")),
                               DividerBlock(),
                               DISPLAY_NAME_INPUT,
                               CHANNEL_INPUT,
                               USERS_INPUT,
                               *FIRST_ROTATION_INPUT.values(),
                               *SECOND_ROTATION_INPUT.values()

                           ],
                           title="Rotating Schedule",
                           submit="Create",
                           callback_id=SCHEDULE_NEW_DIALOG_CALL_BACK_ID)
