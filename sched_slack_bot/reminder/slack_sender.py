from slack_sdk import WebClient

from sched_slack_bot.reminder.reminder import Reminder
from sched_slack_bot.reminder.sender import ReminderSender


class SlackReminderSender(ReminderSender):
    def __init__(self, client: WebClient):
        self._client = client

    def send_reminder(self, reminder: Reminder) -> None:
        self._client.chat_postMessage(channel=reminder.channel_id_to_notify_in,
                                      text=f"Hey <@{reminder.user_id_to_notify}>, you are responsible for"
                                           f" *{reminder.display_name}*!"
                                           f" Next Rotation is on {reminder.next_next_rotation_date},"
                                           f" next user is <@{reminder.next_rotation_user}>",
                                      )
