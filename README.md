# SchedSlackBot 
[![CI](https://github.com/Germandrummer92/SchedSlackBot/actions/workflows/ci.yml/badge.svg)](https://github.com/Germandrummer92/SchedSlackBot/actions/workflows/ci.yml)

![Image of a Calendar](https://github.com/Germandrummer92/SchedSlackBot/raw/main/assets/calendar.jpg "Rotational Scheduling")

A Kubernetes self-hosted Slack bot able to setup rotating schedules for Reminders.

Your One-Stop-Shop for setting up rotating :calendar: schedules.

* Setting up a Meeting and want to have the meeting moderation rotate between members? SchedSlackBot can help you.
* Have a meeting that a representative of your team should join? (e.g. Scrum of Scrums, Weekly etc.)
SchedSlackBot can help balance the load fairly between Team Members

# Setup Slack Bot

# Development

* Follow the [#Setup Slack Bot](#setup-slack-bot) guide to setup a test bot in your own workspace
* Set the `SLACK_SIGNING_SECRET` and `SLACK_BOT_TOKEN`env variables
* Setup a mongo database and set the corresponding url in env variable `MONGO_URL`
* Setup a reverse proxy (e.g [ngrok](https://ngrok.io))
* Update the url in your slack bot to the ngrok url
* Start `python bin/app.py`


### Image Attribution

[Banner vector created by makyzz - www.freepik.com](https://www.freepik.com/vectors/banner)
