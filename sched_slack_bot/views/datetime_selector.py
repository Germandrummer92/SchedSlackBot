import uuid
from enum import Enum
from typing import Dict, List

from slack_sdk.models.blocks import InputBlock, PlainTextObject, DatePickerElement, StaticSelectElement, OptionGroup, \
    Option


class DatetimeSelectorType(Enum):
    DATE = "DATE"
    HOUR = "HOUR"
    MINUTE = "MINUTE"


def get_options_for_range(option_range: range, label: str) -> List[OptionGroup]:
    return [OptionGroup(options=[Option(value=str(hour), label=str(hour)) for hour in option_range],
                        label=PlainTextObject(text=label))]


def get_datetime_selector(label: str) -> Dict[DatetimeSelectorType, InputBlock]:
    blocks = dict()
    blocks[DatetimeSelectorType.DATE] = InputBlock(label=f"{label} Date",
                                                   hint=PlainTextObject(text="The date of the first Rotation/Reminder"),
                                                   element=DatePickerElement(),
                                                   block_id=f"{label} Date")
    blocks[DatetimeSelectorType.HOUR] = InputBlock(label=f"{label} Hour",
                                                   hint=PlainTextObject(text="The Hour of the first Rotation/Reminder"),
                                                   element=StaticSelectElement(
                                                       option_groups=get_options_for_range(option_range=range(0, 24),
                                                                                           label="Hour")),
                                                   block_id=f"{label} Hour")

    blocks[DatetimeSelectorType.MINUTE] = InputBlock(label=f"{label} Minute",
                                                     hint=PlainTextObject(
                                                         text="The Minute of the first Rotation/Reminder"),
                                                     element=StaticSelectElement(
                                                         option_groups=get_options_for_range(option_range=range(0, 60),
                                                                                             label="Minute")),
                                                     block_id=f"{label} Minute")

    return blocks
