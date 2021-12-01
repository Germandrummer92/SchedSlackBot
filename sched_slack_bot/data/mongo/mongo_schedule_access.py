import logging
from typing import List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection

from sched_slack_bot.data.schedule_access import ScheduleAccess
from sched_slack_bot.model.schedule import Schedule

logger = logging.getLogger(__name__)


class MongoScheduleAccess(ScheduleAccess):
    def __init__(self, mongo_url: str, port: Optional[str] = None, db_name: str = "sched-slack-bot",
                 collection_name: str = "schedules"):
        self._client = MongoClient(host=mongo_url,
                                   port=port)
        self._db_name = db_name
        self._collection_name = collection_name

    @property
    def _collection(self) -> Collection:
        return self._client.get_database(name=self._db_name).get_collection(name=self._collection_name)

    def get_available_schedules(self) -> List[Schedule]:
        return [Schedule.from_json(json=s) for s in self._collection.find({})]

    def save_schedule(self, schedule: Schedule) -> None:
        logger.info(f"Saving schedule with id {schedule.id}")
        self._collection.insert_one(schedule.as_json())

    def delete_schedule(self, schedule: Schedule) -> None:
        logger.info(f"Deleting schedule with id {schedule.id}")
        self._collection.delete_one({"id": schedule.id})
