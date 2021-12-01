from typing import List

from slack_sdk.models.blocks import Block, SectionBlock, MarkdownTextObject, DividerBlock

from sched_slack_bot.model.schedule import Schedule


def blocks_for_schedule(schedule: Schedule) -> List[Block]:
    return [
        SectionBlock(text=MarkdownTextObject(
            text=f":calendar: Schedule *{schedule.display_name}*: Next-Rotation: _{schedule.next_rotation}_")),
        SectionBlock(text=MarkdownTextObject(
            text=f"Next Responsible person: <@{schedule.current_user_to_notify}>, all users: {[f'<@{user}>' for user in schedule.members]}"
        )),
        DividerBlock()
    ]


def get_blocks_for_schedules(schedules: List[Schedule]) -> List[Block]:
    blocks = list()
    for schedule in schedules:
        blocks.extend(blocks_for_schedule(schedule=schedule))

    return blocks
