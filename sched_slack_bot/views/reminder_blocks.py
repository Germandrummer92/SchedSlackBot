from typing import List

from slack_sdk.models.blocks import ConfirmObject, Block, SectionBlock, \
    MarkdownTextObject, ButtonElement

from sched_slack_bot.model.reminder import Reminder

SKIP_CURRENT_MEMBER_ACTION_ID = "SCHED_SLACK_BOT_SKIP_ACTION_ID"


def _get_confirm_object_for_skip(reminder: Reminder) -> ConfirmObject:
    return ConfirmObject(
        text=MarkdownTextObject(text=f"Are you sure you"
                                     f" want to skip <@{reminder.user_id_to_notify}>?\n\n\n\n"
                                     f" Next responsible person will be <@{reminder.next_rotation_user}>"),
        confirm="Skip",
        deny="Cancel",
        title=f"Skip {reminder.display_name}")


def get_reminder_blocks(reminder: Reminder) -> List[Block]:
    return [SectionBlock(text=MarkdownTextObject(text=get_reminder_text(reminder)),
                         block_id=reminder.schedule_id,
                         accessory=ButtonElement(action_id=SKIP_CURRENT_MEMBER_ACTION_ID,
                                                 text="Skip",
                                                 confirm=_get_confirm_object_for_skip(reminder=reminder)))]


def get_skip_blocks(reminder: Reminder) -> List[Block]:
    return [SectionBlock(text=MarkdownTextObject(text=get_skip_text(reminder)),
                         block_id=reminder.schedule_id,
                         accessory=ButtonElement(action_id=SKIP_CURRENT_MEMBER_ACTION_ID,
                                                 text="Skip",
                                                 confirm=_get_confirm_object_for_skip(reminder=reminder)))]


def get_reminder_text(reminder: Reminder) -> str:
    text = f"Hey <@{reminder.user_id_to_notify}>, you are responsible for" + \
           f" *{reminder.display_name}*!" + \
           f" Next Rotation is on _{reminder.next_next_rotation_date}_," + \
           f" next user is <@{reminder.next_rotation_user}>"

    return text


def get_skip_text(reminder: Reminder) -> str:
    text = f"Skipped to <@{reminder.user_id_to_notify}>: you are responsible for" + \
           f" *{reminder.display_name}* today!" + \
           f" Next Rotation is on _{reminder.next_next_rotation_date}_," + \
           f" next user is <@{reminder.next_rotation_user}>"

    return text
