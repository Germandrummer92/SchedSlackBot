from sched_slack_bot.model.schedule import Schedule


class Reminder:
    def __init__(self, schedule: Schedule):
        self._schedule = schedule

    @property
    def channel_id_to_notify_in(self) -> str:
        return self._schedule.channel_id_to_notify_in

    @property
    def user_id_to_notify(self) -> str:
        return self._schedule.members[self._schedule.current_index]

    @property
    def display_name(self) -> str:
        return self._schedule.display_name

    @property
    def next_next_rotation_date(self) -> str:
        return self._schedule.next_next_rotation_date.strftime("%Y-%m-%d-%H-%M")

    @property
    def next_rotation_user(self) -> str:
        return self._schedule.members[self._schedule.next_index]

    @property
    def next_schedule(self) -> Schedule:
        return self._schedule.next_schedule
