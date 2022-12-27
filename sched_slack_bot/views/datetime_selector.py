import datetime
from typing import Optional

from slack_sdk.models.blocks import PlainTextObject, DatePickerElement, StaticSelectElement, OptionGroup, Option

from sched_slack_bot.views.input_block_with_block_id import InputBlockWithBlockId
from sched_slack_bot.views.schedule_dialog_block_ids import get_datetime_block_ids, DatetimeSelectorType

DateTimeSelectorBlocks = dict[DatetimeSelectorType, InputBlockWithBlockId]


def _get_options_for_range(option_range: range, label: str) -> OptionGroup:
    return OptionGroup(
        options=[Option(value=str(hour), label=str(hour)) for hour in option_range], label=PlainTextObject(text=label)
    )


def get_datetime_selector(label: str, schedule_date: Optional[datetime.datetime] = None) -> DateTimeSelectorBlocks:
    blocks = dict()
    block_ids = get_datetime_block_ids(label=label)
    option_group_hours = _get_options_for_range(option_range=range(0, 24), label="Hour")
    option_group_minute = _get_options_for_range(option_range=range(0, 60), label="Minute")

    # format needs to match the format defined in DatePickerElement
    initial_date = None if schedule_date is None else schedule_date.date().isoformat()

    initial_hour: Optional[Option] = None
    if schedule_date is not None:
        hour_options = option_group_hours.options or []
        initial_hour = [o for o in hour_options if o.value == str(schedule_date.hour)][0]

    initial_minute: Optional[Option] = None
    if schedule_date is not None:
        minute_options = option_group_minute.options or []
        initial_minute = [o for o in minute_options if o.value == str(schedule_date.minute)][0]

    blocks[DatetimeSelectorType.DATE] = InputBlockWithBlockId(
        label=block_ids[DatetimeSelectorType.DATE],
        hint=PlainTextObject(text="The date of the first Rotation/Reminder"),
        element=DatePickerElement(initial_date=initial_date),
        block_id=block_ids[DatetimeSelectorType.DATE],
    )

    blocks[DatetimeSelectorType.HOUR] = InputBlockWithBlockId(
        label=block_ids[DatetimeSelectorType.HOUR],
        hint=PlainTextObject(
            text=f"The Hour of the first Rotation/Reminder (in {datetime.datetime.now().astimezone().tzname()})"
        ),
        element=StaticSelectElement(initial_option=initial_hour, option_groups=[option_group_hours]),
        block_id=block_ids[DatetimeSelectorType.HOUR],
    )

    blocks[DatetimeSelectorType.MINUTE] = InputBlockWithBlockId(
        label=block_ids[DatetimeSelectorType.MINUTE],
        hint=PlainTextObject(text="The Minute of the first Rotation/Reminder"),
        element=StaticSelectElement(initial_option=initial_minute, option_groups=[option_group_minute]),
        block_id=block_ids[DatetimeSelectorType.MINUTE],
    )

    return blocks
