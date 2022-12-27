import abc
from typing import List, Optional

from sched_slack_bot.model.schedule import Schedule


class ScheduleAccess(abc.ABC):
    @abc.abstractmethod
    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        raise NotImplementedError("Not Implemented")

    @abc.abstractmethod
    def get_available_schedules(self) -> List[Schedule]:
        raise NotImplementedError("Not Implemented")

    @abc.abstractmethod
    def save_schedule(self, schedule: Schedule) -> None:
        raise NotImplementedError("Not Implemented")

    @abc.abstractmethod
    def update_schedule(self, schedule_id_to_update: str, new_schedule: Schedule) -> None:
        raise NotImplementedError("Not Implemented")

    @abc.abstractmethod
    def delete_schedule(self, schedule_id: str) -> None:
        raise NotImplementedError("Not Implemented")
