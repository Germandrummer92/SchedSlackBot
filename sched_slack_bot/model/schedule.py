from __future__ import annotations

import datetime
import logging
import uuid
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any

from sched_slack_bot.utils.find_block_value import find_block_value
from sched_slack_bot.utils.slack_typing_stubs import SlackState, SlackBody
from sched_slack_bot.views.schedule_dialog_block_ids import (
    DISPLAY_NAME_BLOCK_ID,
    SCHEDULE_VIEW_ID_SCHEDULE_ID_DELIMITER,
    USERS_INPUT_BLOCK_ID,
    CHANNEL_INPUT_BLOCK_ID,
    DatetimeSelectorType,
    get_datetime_block_ids,
    FIRST_ROTATION_LABEL,
    SECOND_ROTATION_LABEL,
    CREATE_NEW_SCHEDULE_VIEW_ID_PREFIX,
)

logger = logging.getLogger(__name__)

SERIALIZATION_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"


def _raise_if_not_string(value: Optional[Union[str, List[str]]], name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Value {name} must be a string but isn't, actual value: {value}")

    return value


def _raise_if_not_list(value: Optional[Union[str, List[str]]], name: str) -> List[str]:
    if not isinstance(value, list):
        raise ValueError(f"Value {name} must be a list but isn't, actual value: {value}")

    return value


def _get_datetime_from_modal_submission(
    state: SlackState, date_input_block_ids: Dict[DatetimeSelectorType, str]
) -> datetime.datetime:
    date_string = find_block_value(state=state, block_id=date_input_block_ids[DatetimeSelectorType.DATE])
    date_string = _raise_if_not_string(value=date_string, name="date")
    hour = find_block_value(state=state, block_id=date_input_block_ids[DatetimeSelectorType.HOUR])
    hour = _raise_if_not_string(value=hour, name="hour")
    minute = find_block_value(state=state, block_id=date_input_block_ids[DatetimeSelectorType.MINUTE])
    minute = _raise_if_not_string(value=minute, name="minute")

    # no kwarg supported
    date = datetime.date.fromisoformat(date_string)

    logger.debug(f"{date=}, {hour=}, {minute=}")

    return datetime.datetime(day=date.day, month=date.month, year=date.year, hour=int(hour), minute=int(minute))


@dataclass(frozen=True)
class Schedule:
    id: str
    display_name: str
    members: List[str]
    next_rotation: datetime.datetime
    time_between_rotations: datetime.timedelta
    channel_id_to_notify_in: str
    created_by: str
    current_index: int = 0

    def __post_init__(self) -> None:
        if self.time_between_rotations.total_seconds() == 0:
            raise ValueError("A schedule with 0 time between rotations cannot be handled!")

        if len(self.members) == 0:
            raise ValueError("A schedule with 0 members cannot be handled!")

    @property
    def next_index(self) -> int:
        return (self.current_index + 1) % len(self.members)

    @property
    def next_next_rotation_date(self) -> datetime.datetime:
        return self.next_rotation + self.time_between_rotations

    @property
    def next_schedule(self) -> Schedule:
        return Schedule(
            id=self.id,
            display_name=self.display_name,
            members=self.members,
            next_rotation=self.next_next_rotation_date,
            time_between_rotations=self.time_between_rotations,
            channel_id_to_notify_in=self.channel_id_to_notify_in,
            current_index=self.next_index,
            created_by=self.created_by,
        )

    @property
    def current_user_to_notify(self) -> str:
        return self.members[self.current_index]

    def as_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "members": self.members,
            "next_rotation": self.next_rotation.strftime(SERIALIZATION_DATE_FORMAT),
            "time_between_rotations": self.time_between_rotations.total_seconds(),
            "channel_id_to_notify_in": self.channel_id_to_notify_in,
            "created_by": self.created_by,
            "current_index": self.current_index,
        }

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> Schedule:
        return Schedule(
            id=json["id"],
            display_name=json["display_name"],
            members=json["members"],
            next_rotation=datetime.datetime.strptime(json["next_rotation"], SERIALIZATION_DATE_FORMAT),
            time_between_rotations=datetime.timedelta(seconds=json["time_between_rotations"]),
            channel_id_to_notify_in=json["channel_id_to_notify_in"],
            created_by=json["created_by"],
            current_index=json["current_index"],
        )

    @classmethod
    def from_modal_submission(cls, submission_body: SlackBody) -> Schedule:
        state = submission_body["view"]["state"]

        display_name = find_block_value(state=state, block_id=DISPLAY_NAME_BLOCK_ID)
        display_name = _raise_if_not_string(value=display_name, name="display_name")

        members = find_block_value(state=state, block_id=USERS_INPUT_BLOCK_ID)
        members = _raise_if_not_list(value=members, name="members")

        channel_id_to_notify_in = find_block_value(state=state, block_id=CHANNEL_INPUT_BLOCK_ID)
        channel_id_to_notify_in = _raise_if_not_string(value=channel_id_to_notify_in, name="channel_id_to_notify_in")

        next_rotation = _get_datetime_from_modal_submission(
            state=state, date_input_block_ids=get_datetime_block_ids(label=FIRST_ROTATION_LABEL)
        )
        second_rotation = _get_datetime_from_modal_submission(
            state=state, date_input_block_ids=get_datetime_block_ids(label=SECOND_ROTATION_LABEL)
        )

        time_between_rotations = abs(second_rotation - next_rotation)

        schedule_id = submission_body["view"]["external_id"]

        if schedule_id.startswith(CREATE_NEW_SCHEDULE_VIEW_ID_PREFIX):
            schedule_id = str(uuid.uuid4())
        elif SCHEDULE_VIEW_ID_SCHEDULE_ID_DELIMITER in schedule_id:
            schedule_id = schedule_id.split(SCHEDULE_VIEW_ID_SCHEDULE_ID_DELIMITER)[0]
        else:
            raise ValueError(f"external id of schedule doesn't contain delimiter '{SCHEDULE_VIEW_ID_SCHEDULE_ID_DELIMITER}'"
                             f"nor prefix '{CREATE_NEW_SCHEDULE_VIEW_ID_PREFIX}', received instead: '{schedule_id}'")

        return Schedule(
            id=schedule_id,
            display_name=display_name,
            members=members,
            next_rotation=next_rotation,
            time_between_rotations=time_between_rotations,
            channel_id_to_notify_in=channel_id_to_notify_in,
            created_by=submission_body["user"]["name"],
            current_index=0,
        )
