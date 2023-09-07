from __future__ import annotations

from enum import Enum

DISPLAY_NAME_BLOCK_ID = "NEW_SCHEDULE_DISPLAY_NAME_INPUT"
CHANNEL_INPUT_BLOCK_ID = "NEW_SCHEDULE_CHANNEL_INPUT"
USERS_INPUT_BLOCK_ID = "NEW_SCHEDULE_USERS_INPUT"

FIRST_ROTATION_LABEL = "First Rotation Reminder/Rotation"
SECOND_ROTATION_LABEL = "Second Rotation Reminder/Rotation"

CREATE_NEW_SCHEDULE_VIEW_ID_PREFIX = "NEW_DIALOG"

SCHEDULE_VIEW_ID_SCHEDULE_ID_DELIMITER = "::"


class DatetimeSelectorType(Enum):
    DATE = "DATE"
    HOUR = "HOUR"
    MINUTE = "MINUTE"


def get_datetime_block_ids(label: str) -> dict[DatetimeSelectorType, str]:
    return {
        DatetimeSelectorType.DATE: f"{label} Date",
        DatetimeSelectorType.HOUR: f"{label} Hour",
        DatetimeSelectorType.MINUTE: f"{label} Minute",
    }
