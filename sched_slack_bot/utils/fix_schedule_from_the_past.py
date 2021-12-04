import datetime

from sched_slack_bot.model.schedule import Schedule


def fix_schedule_from_the_past(schedule: Schedule) -> Schedule:
    now = datetime.datetime.now()
    next_rotation = schedule.next_rotation
    while now >= next_rotation:
        next_rotation += schedule.time_between_rotations

    return Schedule(
        id=schedule.id,
        display_name=schedule.display_name,
        members=schedule.members,
        next_rotation=next_rotation,
        time_between_rotations=schedule.time_between_rotations,
        channel_id_to_notify_in=schedule.channel_id_to_notify_in,
        created_by=schedule.created_by,
        current_index=schedule.current_index
    )
