from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass
from typing import List, Optional, Union

from slack_sdk.scim import Group

from sched_slack_bot.model.slack_body import SlackBody
from sched_slack_bot.utils.find_block import find_block_value
from sched_slack_bot.views.schedule_dialog import DISPLAY_NAME_INPUT, USERS_INPUT, CHANNEL_INPUT


def raise_if_not_present(value: Optional[Union[str, List[str]]], name: str) -> Union[str, List[str]]:
    if value is None:
        raise ValueError(f"Value {name} must be present but isn't")

    return value


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

        # next_rotation = find_block_value(state=state,
        #                                  blo)

        return Schedule(id=str(uuid.uuid4()),
                        display_name=display_name,
                        members=members,
                        next_rotation=datetime.datetime.now(),
                        time_between_rotations=datetime.timedelta(seconds=10),
                        channel_id_to_notify_in=channel_id_to_notify_in,
                        created_by=submission_body["user"]["name"],
                        current_index=0
                        )
