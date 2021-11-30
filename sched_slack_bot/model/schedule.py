from __future__ import annotations

import datetime
import logging
import uuid
from dataclasses import dataclass
from typing import List, Optional, Union, TypeGuard, Dict

from slack_sdk.models.blocks import InputBlock

from sched_slack_bot.model.slack_body import SlackBody, SlackState
from sched_slack_bot.utils.find_block_value import find_block_value
from sched_slack_bot.views.datetime_selector import DatetimeSelectorType
from sched_slack_bot.views.schedule_dialog import DISPLAY_NAME_INPUT, USERS_INPUT, CHANNEL_INPUT, FIRST_ROTATION_INPUT, \
    SECOND_ROTATION_INPUT


logger = logging.getLogger(__name__)


def raise_if_not_present(value: Optional[Union[str, List[str]]], name: str) -> TypeGuard[Union[str, List[str]]]:
    if value is None:
        raise ValueError(f"Value {name} must be present but isn't")

    return value


def get_datetime_state(state: SlackState, date_input: Dict[DatetimeSelectorType, InputBlock]) -> datetime.datetime:
    date_string = find_block_value(state=state, block_id=date_input[DatetimeSelectorType.DATE].block_id)
    raise_if_not_present(value=date_string, name="date")
    hour = find_block_value(state=state, block_id=date_input[DatetimeSelectorType.HOUR].block_id)
    raise_if_not_present(value=hour, name="hour")
    minute = find_block_value(state=state, block_id=date_input[DatetimeSelectorType.MINUTE].block_id)
    raise_if_not_present(value=minute, name="minute")

    date = datetime.date.fromisoformat(date_string)
    logger.debug(f"{date=}, {hour=}, {minute=}")

    return datetime.datetime(day=date.day,
                             month=date.month,
                             year=date.year,
                             hour=int(hour),
                             minute=int(minute))


@dataclass
class Schedule:
    id: str
    display_name: str
    members: List[str]
    next_rotation: datetime.datetime
    time_between_rotations: datetime.timedelta
    channel_id_to_notify_in: str
    created_by: str
    current_index: int = 0

    @classmethod
    def from_modal_submission(cls, submission_body: SlackBody) -> Schedule:
        state = submission_body["view"]["state"]

        display_name = find_block_value(state=state,
                                        block_id=DISPLAY_NAME_INPUT.block_id)
        raise_if_not_present(value=display_name, name="display_name")

        members = find_block_value(state=state,
                                   block_id=USERS_INPUT.block_id)
        raise_if_not_present(value=members, name="members")

        channel_id_to_notify_in = find_block_value(state=state,
                                                   block_id=CHANNEL_INPUT.block_id)
        raise_if_not_present(value=channel_id_to_notify_in, name="channel_id_to_notify_in")

        next_rotation = get_datetime_state(state=state, date_input=FIRST_ROTATION_INPUT)
        second_rotation = get_datetime_state(state=state, date_input=SECOND_ROTATION_INPUT)

        time_between_rotations = second_rotation - next_rotation

        return Schedule(id=str(uuid.uuid4()),
                        display_name=display_name,
                        members=members,
                        next_rotation=next_rotation,
                        time_between_rotations=time_between_rotations,
                        channel_id_to_notify_in=channel_id_to_notify_in,
                        created_by=submission_body["user"]["name"],
                        current_index=0
                        )
