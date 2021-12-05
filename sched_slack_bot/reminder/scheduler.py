import datetime
import logging
import threading
from typing import Dict, cast, List, Optional, Callable

from sched_slack_bot.model.schedule import Schedule
from sched_slack_bot.reminder.reminder import Reminder
from sched_slack_bot.reminder.sender import ReminderSender

logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(self, reminder_executed_callback: Optional[Callable[[Schedule], None]] = None) -> None:
        self._scheduled_jobs: Dict[int, threading.Timer] = dict()
        self._timer_by_schedule_id: Dict[str, threading.Timer] = dict()
        self._scheduled_jobs_lock = threading.RLock()
        self._reminder_executed_callback: Optional[Callable[[Schedule], None]] = reminder_executed_callback

    def _get_thread_ident_for_schedule(self, schedule_id: str) -> int:
        with self._scheduled_jobs_lock:
            # this timer has to be started
            return self._timer_by_schedule_id[schedule_id].ident  # type: ignore

    def remove_reminder_for_schedule(self, schedule_id: str):
        logger.info(f"Removing scheduled reminder for schedule id {schedule_id}")
        ident_to_remove = self._get_thread_ident_for_schedule(schedule_id=schedule_id)

        self._remove_timer(thread_ident=ident_to_remove, schedule_id=schedule_id, cancel=True)

    def schedule_all_reminders(self, schedules: List[Schedule], reminder_sender: ReminderSender) -> None:
        for schedule in schedules:
            self.schedule_reminder(schedule=schedule, reminder_sender=reminder_sender)

    def _add_timer(self, timer: threading.Timer, schedule_id: str) -> None:
        timer.start()
        with self._scheduled_jobs_lock:
            # timer is started above so the identifier is always defined
            self._scheduled_jobs[timer.ident] = timer  # type: ignore
            self._timer_by_schedule_id[schedule_id] = timer

    def _remove_timer(self, thread_ident: int, schedule_id: str, cancel: bool = False) -> None:
        with self._scheduled_jobs_lock:
            if thread_ident in self._scheduled_jobs:
                timer_to_cancel = self._scheduled_jobs.pop(thread_ident)
                if cancel:
                    timer_to_cancel.cancel()
            if schedule_id in self._timer_by_schedule_id:
                self._timer_by_schedule_id.pop(schedule_id)

    def schedule_reminder(self, schedule: Schedule, reminder_sender: ReminderSender) -> None:
        now = datetime.datetime.now()
        if schedule.next_rotation < now:
            raise ValueError("The provided schedule was scheduled in the past!")

        interval = (schedule.next_rotation - now).total_seconds()
        reminder = Reminder(schedule=schedule)
        logger.info(f"Scheduling Reminder at {interval}s from now")
        timer = threading.Timer(interval=interval, function=self.execute_reminder,
                                kwargs={"reminder": reminder, "reminder_sender": reminder_sender})
        self._add_timer(timer=timer, schedule_id=schedule.id)

    def execute_reminder(self, reminder: Reminder, reminder_sender: ReminderSender) -> None:
        logger.info(f"Executing reminder {reminder.display_name}")

        current_thread = threading.current_thread()
        thread_ident = cast(int, current_thread.ident)

        reminder_sender.send_reminder(reminder=reminder)
        self._remove_timer(thread_ident=thread_ident, schedule_id=reminder.schedule_id)

        next_schedule = reminder.next_schedule
        self.schedule_reminder(schedule=next_schedule,
                               reminder_sender=reminder_sender)

        if self._reminder_executed_callback is not None:
            self._reminder_executed_callback(next_schedule)
