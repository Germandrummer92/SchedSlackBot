import datetime
import uuid
from typing import Generator, List
from unittest import mock

import pytest
from pymongo.collection import Collection

from sched_slack_bot.data.mongo.mongo_schedule_access import MongoScheduleAccess
from sched_slack_bot.model.schedule import Schedule


@pytest.fixture()
def mocked_collection() -> mock.MagicMock:
    return mock.MagicMock(spec=Collection)


@pytest.fixture(autouse=True)
def mocked_mongo_client(mocked_collection: mock.MagicMock) -> Generator[mock.MagicMock, None, None]:
    with mock.patch("sched_slack_bot.data.mongo.mongo_schedule_access.MongoClient") as mocked_client:
        mocked_client.return_value.get_database.return_value.get_collection.return_value = mocked_collection
        yield mocked_client


@pytest.fixture()
def mongo_schedule_access() -> MongoScheduleAccess:
    return MongoScheduleAccess(mongo_url="mongodb://someUrl")


@pytest.fixture()
def schedules() -> List[Schedule]:
    return [Schedule(id=str(uuid.uuid4()),
                     display_name="Rotation Schedule",
                     members=["U1", "U2"],
                     next_rotation=datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(seconds=100),
                     time_between_rotations=datetime.timedelta(hours=2),
                     channel_id_to_notify_in="C1",
                     created_by="creator"),
            Schedule(id=str(uuid.uuid4()),
                     display_name="Rotation Schedule 2",
                     members=["U3", "U4"],
                     next_rotation=datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(seconds=200),
                     time_between_rotations=datetime.timedelta(hours=4),
                     channel_id_to_notify_in="C2",
                     created_by="creator2")
            ]


def test_get_available_schedules(mocked_collection: mock.MagicMock, mongo_schedule_access: MongoScheduleAccess,
                                 schedules: List[Schedule]) -> None:
    mocked_collection.find.return_value = [s.as_json() for s in schedules]
    assert mongo_schedule_access.get_available_schedules() == schedules


def test_get_schedule(mocked_collection: mock.MagicMock, mongo_schedule_access: MongoScheduleAccess,
                      schedules: List[Schedule]) -> None:
    mocked_collection.find_one.return_value = schedules[0].as_json()
    assert mongo_schedule_access.get_schedule(schedule_id=schedules[0].id) == schedules[0]


def test_get_schedule_none(mocked_collection: mock.MagicMock, mongo_schedule_access: MongoScheduleAccess,
                           schedules: List[Schedule]) -> None:
    mocked_collection.find_one.return_value = None
    assert mongo_schedule_access.get_schedule(schedule_id=schedules[0].id) is None


def test_update_schedule(mocked_collection: mock.MagicMock, mongo_schedule_access: MongoScheduleAccess,
                         schedules: List[Schedule]) -> None:
    mongo_schedule_access.update_schedule(schedule_id_to_update=schedules[0].id,
                                          new_schedule=schedules[0])

    mocked_collection.replace_one.assert_called_once_with(filter={"id": schedules[0].id},
                                                          replacement=schedules[0].as_json())


def test_delete_schedule(mocked_collection: mock.MagicMock, mongo_schedule_access: MongoScheduleAccess,
                         schedules: List[Schedule]) -> None:
    mongo_schedule_access.delete_schedule(schedule_id=schedules[0].id)

    mocked_collection.delete_one.assert_called_once_with({"id": schedules[0].id})


def test_save_schedule(mocked_collection: mock.MagicMock,
                       mongo_schedule_access: MongoScheduleAccess,
                       schedules: List[Schedule]) -> None:
    mongo_schedule_access.save_schedule(schedule=schedules[0])

    mocked_collection.insert_one.assert_called_once_with(schedules[0].as_json())
