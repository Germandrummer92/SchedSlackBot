import abc

from sched_slack_bot.reminder.reminder import Reminder


class ReminderSender(abc.ABC):

    @abc.abstractmethod
    def send_reminder(self, reminder: Reminder) -> None:
        raise NotImplementedError("Not Implemented")
