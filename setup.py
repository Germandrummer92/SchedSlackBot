from setuptools import find_packages, setup

setup(
        name="SchedSlackBot",
        version='1.0.0',
        author="Daniel Draper <Germandrummer92@gmail.com>",
        description="Setup and manage Rotating Schedules in Slack",
        packages=find_packages(include=["sched_slack_bot"]),
)
