import pytest

from sched_slack_bot.model.slack_body import SlackState, SlackInputBlockState
from sched_slack_bot.utils.find_block_value import find_block_value, SlackValueContainerType


@pytest.mark.parametrize("value_container_type", list(SlackValueContainerType))
def test_it_finds_block_value(value_container_type: SlackValueContainerType) -> None:
    block_id = "block"
    expected_value = "value"

    value_kwargs = {value_container_type.value: expected_value}

    if value_container_type == SlackValueContainerType.static_select:
        value_kwargs = {value_container_type.value: {"value": expected_value}}
    # noinspection PyArgumentList
    block_value = find_block_value(state=SlackState(values={
        block_id: {
            "some_value_key": SlackInputBlockState(type=value_container_type.name,
                                                   **value_kwargs)
        }
    }), block_id=block_id)

    assert block_value == expected_value


def test_it_returns_none_if_no_matching_block() -> None:
    block_value = find_block_value(state=SlackState(values={}), block_id="non_existant")

    assert block_value is None


def test_it_returns_none_if_no_sub_blocks_in_matching_block() -> None:
    block_id = "block"
    block_value = find_block_value(state=SlackState(values={
        block_id: {}
    }), block_id=block_id)

    assert block_value is None
