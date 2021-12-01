import logging
from enum import Enum
from typing import Optional, Union, List

from sched_slack_bot.model.slack_body import SlackState

logger = logging.getLogger(__name__)


class _SlackValueContainerType(Enum):
    value: str
    plain_text_input = "value"
    multi_users_select = "selected_users"
    conversations_select = "selected_conversation"
    static_select = "selected_option"
    datepicker = "selected_date"


def find_block_value(state: SlackState, block_id: str) -> Optional[Union[str, List[str]]]:
    block_state = state["values"][block_id]
    sub_blocks = list(block_state.keys())

    value_container = block_state[sub_blocks[0]]

    value_container_type = _SlackValueContainerType[value_container["type"]]
    value_key = value_container_type.value

    logger.debug(value_container)
    logger.debug(value_key)

    # type ignores are necessary since the name of the field in the container is dynamic,
    # typing it isn't easily possible
    if value_container_type == _SlackValueContainerType.static_select:
        # extra level of dictionary in this case
        value = value_container[value_key]["value"]  # type: ignore
    else:
        value = value_container[value_key]  # type: ignore

    return value  # type: ignore
