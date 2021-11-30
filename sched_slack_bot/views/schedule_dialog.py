from typing import List

from slack_sdk.models.blocks import HeaderBlock, PlainTextObject, DividerBlock, InputBlock, PlainTextInputElement, \
    ConversationSelectElement, DatePickerElement, StaticSelectElement, OptionGroup, Option, UserMultiSelectElement
from slack_sdk.models.views import View

USERS_INPUT = InputBlock(label="Users to use in Rotation", element=UserMultiSelectElement(),
                         hint=PlainTextObject(text="The Users that should be part of the rotation"),
                         block_id="NEW_SCHEDULE_USERS_INPUT")

CHANNEL_INPUT = InputBlock(label="Channel To Notify", element=ConversationSelectElement(placeholder="#channel"),
                           hint=PlainTextObject(text="The channel to notify automatically"),
                           block_id="NEW_SCHEDULE_CHANNEL_INPUT")

DISPLAY_NAME_INPUT = InputBlock(label="Display Name", hint=PlainTextObject(text="Name for your rotating schedule"),
                                element=PlainTextInputElement(initial_value="New Rotating Schedule"),
                                block_id="NEW_SCHEDULE_DISPLAY_NAME_INPUT")


def get_options_for_range(option_range: range, label: str) -> List[OptionGroup]:
    return [OptionGroup(options=[Option(value=str(hour), label=str(hour)) for hour in option_range],
                        label=PlainTextObject(text=label))]


def get_datetime_selector(label: str) -> List[InputBlock]:
    blocks = list()
    blocks.append(InputBlock(label=f"{label} Date",
                             hint=PlainTextObject(text="The date of the first Rotation/Reminder"),
                             element=DatePickerElement()))
    blocks.append(InputBlock(label=f"{label} Hour",
                             hint=PlainTextObject(text="The Hour of the first Rotation/Reminder"),
                             element=StaticSelectElement(
                                 option_groups=get_options_for_range(option_range=range(0, 24),
                                                                     label="Hour"))))
    blocks.append(InputBlock(label=f"{label} Minute",
                             hint=PlainTextObject(text="The Minute of the first Rotation/Reminder"),
                             element=StaticSelectElement(
                                 option_groups=get_options_for_range(option_range=range(0, 60),
                                                                     label="Minute"))))

    return blocks


SCHEDULE_NEW_DIALOG_CALL_BACK_ID = "SCHED_SLACK_BOT_NEW_SCHEDULE_SUBMIT_ID"

SCHEDULE_NEW_DIALOG = View(type="modal",
                           blocks=[
                               HeaderBlock(
                                   text=PlainTextObject(text="Create a new :calendar: Rotating Schedule")),
                               DividerBlock(),
                               DISPLAY_NAME_INPUT,
                               CHANNEL_INPUT,
                               USERS_INPUT,
                               *get_datetime_selector(label="First Rotation Reminder/Rotation"),
                               *get_datetime_selector(label="Second Rotation Reminder/Rotation"),

                           ],
                           title="Rotating Schedule",
                           submit="Create",
                           callback_id=SCHEDULE_NEW_DIALOG_CALL_BACK_ID)
