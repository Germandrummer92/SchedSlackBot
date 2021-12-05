from typing import List

from slack_sdk.models.blocks import Block, SectionBlock, MarkdownTextObject, DividerBlock, ActionsBlock, \
    ButtonElement, PlainTextObject, ConfirmObject

from sched_slack_bot.model.schedule import Schedule

DELETE_SCHEDULE_ACTION_ID = "SCHED_SLACK_BOT_DELETE_SCHEDULE"


def create_delete_schedule_block(schedule: Schedule) -> ActionsBlock:
    return ActionsBlock(elements=[
        ButtonElement(text=PlainTextObject(text="Delete"), action_id=DELETE_SCHEDULE_ACTION_ID,
                      style="danger",
                      confirm=ConfirmObject(text=f"Are you sure you want to delete {schedule.display_name}?",
                                            title=f"Delete {schedule.display_name}?",
                                            confirm="Delete", deny="Cancel", style="danger")
                      )],
        block_id=schedule.id)


def blocks_for_schedule(schedule: Schedule) -> List[Block]:
    return [
        SectionBlock(text=MarkdownTextObject(
            text=f":calendar: Schedule *{schedule.display_name}*: Next-Rotation: _{schedule.next_rotation}_"
                 f" channel: <#{schedule.channel_id_to_notify_in}>")),
        SectionBlock(text=MarkdownTextObject(
            text=f"Next Responsible person: <@{schedule.current_user_to_notify}>, "
                 f"all users: {[f'<@{user}>' for user in schedule.members]}"
        )),
        create_delete_schedule_block(schedule=schedule),
        DividerBlock()
    ]


def get_blocks_for_schedules(schedules: List[Schedule]) -> List[Block]:
    blocks = list()
    for schedule in schedules:
        blocks.extend(blocks_for_schedule(schedule=schedule))

    return blocks
