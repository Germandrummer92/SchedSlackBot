from slack_sdk import WebClient

from sched_slack_bot.model.reminder import Reminder
from sched_slack_bot.reminder.sender import ReminderSender
from sched_slack_bot.views.reminder_blocks import get_reminder_blocks, get_reminder_text, get_skip_text, get_skip_blocks


class SlackReminderSender(ReminderSender):
    def __init__(self, client: WebClient):
        self._client = client

    def send_reminder(self, reminder: Reminder) -> None:
        self._client.chat_postMessage(channel=reminder.channel_id_to_notify_in,
                                      # used for screen readers, if blocks can't be rendered
                                      text=get_reminder_text(reminder=reminder),
                                      blocks=get_reminder_blocks(reminder=reminder)
                                      )

    def send_skip_message(self, reminder: Reminder) -> None:
        self._client.chat_postMessage(channel=reminder.channel_id_to_notify_in,
                                      # used for screen readers, if blocks can't be rendered
                                      text=get_skip_text(reminder=reminder),
                                      blocks=get_skip_blocks(reminder=reminder)
                                      )
