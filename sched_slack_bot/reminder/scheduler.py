import datetime
import logging
import threading
from typing import Dict, Mapping, cast, List

from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.reminder.reminder import Reminder
from sched_slack_bot.reminder.sender import ReminderSender

logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(self) -> None:
        self._scheduled_jobs: Dict[int, threading.Timer] = dict()
        self._scheduled_jobs_lock = threading.RLock()

    def schedule_all_reminders(self, schedules: List[Schedule], reminder_sender: ReminderSender) -> None:
        for schedule in schedules:
            self.schedule_reminder(schedule=schedule, reminder_sender=reminder_sender)

    @property
    def scheduled_jobs(self) -> Mapping[int, threading.Timer]:
        with self._scheduled_jobs_lock:
            return self._scheduled_jobs

    def _add_timer(self, timer: threading.Timer) -> None:
        timer.start()
        with self._scheduled_jobs_lock:
            # timer is started above so the identifier is always defined
            self._scheduled_jobs[timer.ident] = timer  # type: ignore

    def _remove_timer(self, thread_ident: int) -> None:
        with self._scheduled_jobs_lock:
            self._scheduled_jobs.pop(thread_ident)

    def schedule_reminder(self, schedule: Schedule, reminder_sender: ReminderSender) -> None:
        now = datetime.datetime.now()
        if schedule.next_rotation < now:
            raise ValueError("The provided schedule was scheduled in the past!")

        interval = (schedule.next_rotation - now).total_seconds()
        reminder = Reminder(schedule=schedule)
        logger.info(f"Scheduling Reminder at {interval}s from now")
        timer = threading.Timer(interval=interval, function=self.execute_reminder,
                                kwargs={"reminder": reminder, "reminder_sender": reminder_sender})
        self._add_timer(timer=timer)

    def execute_reminder(self, reminder: Reminder, reminder_sender: ReminderSender) -> None:
        logger.info(f"Executing reminder {reminder.display_name}")

        current_thread = threading.current_thread()
        thread_ident = cast(int, current_thread.ident)
        self._remove_timer(thread_ident=thread_ident)

        reminder_sender.send_reminder(reminder=reminder)

        self.schedule_reminder(schedule=reminder.next_schedule,
                               reminder_sender=reminder_sender)


REMINDER_SCHEDULER = ReminderScheduler()
