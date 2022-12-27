import abc

from sched_slack_bot.model.reminder import Reminder


class ReminderSender(abc.ABC):
    @abc.abstractmethod
    def send_reminder(self, reminder: Reminder) -> None:
        raise NotImplementedError("Not Implemented")

    @abc.abstractmethod
    def send_skip_message(self, reminder: Reminder) -> None:
        raise NotImplementedError("Not Implemented")
