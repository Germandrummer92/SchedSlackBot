# SchedSlackBot

[![CI](https://github.com/Germandrummer92/SchedSlackBot/actions/workflows/ci.yml/badge.svg)](https://github.com/Germandrummer92/SchedSlackBot/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/Germandrummer92/SchedSlackBot/badge.svg?branch=main)](https://coveralls.io/github/Germandrummer92/SchedSlackBot?branch=main)
![Image of a Calendar](https://github.com/Germandrummer92/SchedSlackBot/raw/main/assets/calendar.jpg "Rotational Scheduling")

A Kubernetes self-hosted Slack bot able to setup rotating schedules for Reminders.

Your One-Stop-Shop for setting up rotating :calendar: schedules.

* Setting up a Meeting and want to have the meeting moderation rotate between members? SchedSlackBot can help you.
* Have a meeting that a representative of your team should join? (e.g. Scrum of Scrums, Weekly etc.)
  SchedSlackBot can help balance the load fairly between Team Members

## Features

* Overview of current rotating schedules
![Image of overview](https://github.com/Germandrummer92/SchedSlackBot/raw/main/assets/overview.png "Overview")

* Creating new Schedules
![Image of creating a new schedule](https://github.com/Germandrummer92/SchedSlackBot/raw/main/assets/create.png "Create")

* Schedule Reminders with ability to skip to next person in line
![Image of a reminder](https://github.com/Germandrummer92/SchedSlackBot/raw/main/assets/reminder.png "Reminder")

* Ability to delete existing reminders
![Image of a deletion](https://github.com/Germandrummer92/SchedSlackBot/raw/main/assets/delete.png "Delete")


## Setting up a new Slack bot

* Open [Slack Apps](https://api.slack.com/apps)
* Create New App
* Copy & paste app_manifest.yml
![Image of creating a slack app](https://github.com/Germandrummer92/SchedSlackBot/raw/main/assets/slack_bot_creation.png "Creating a Slack bot")
* Adjust the request url to something valid (either ngrok or already final k8s deployment url) (you can change it later)
* Install to your workspace
![Image of installing the slack bot](https://github.com/Germandrummer92/SchedSlackBot/raw/main/assets/install.png "Installing the Slack bot")
* Copy the Slack_Bot_Token and Slack_Signing_Secret for local development or deployment


## Deployment

* Create the necessary kubernetes secret:
`kubectl create secret generic sched-slack-bot-secret \
  --from-literal=mongo_url="mongodb://yourMongoDbUrl+Password+Port" \
  --from-literal=slack_signing_secret="YourSlackSigningSecret" \
  --from-literal=slack_bot_token="xoxb-YourSlackBotToken"`

* Adjust the "CLUSTER_DOMAIN" in the deployment.yml to match your specific k8s cluster
* Adjust the "TLS_SUFFIX" to match your specific k8s tls suffix

* Deploy the file:
  `kubectl apply -f deployment.yml`

## Development

* Install python3.10 `sudo apt-get -y python3.10`
* Install poetry `curl -sSL https://install.python-poetry.org/install-poetry.py | python3.10 -`
* Install dependencies with poetry `poetry install`
* Setup pre-commit hook: `pre-commit install`
* Follow the [#Setup Slack Bot](#Setting up a new Slack bot) guide to setup a test bot in your own workspace
* Set the `SLACK_SIGNING_SECRET` and `SLACK_BOT_TOKEN` env variables
* Setup a running mongo database instance and set the corresponding url in env variable `MONGO_URL`
* Setup a reverse proxy (e.g [ngrok](https://ngrok.io))
* Update the url in your slack bot to the ngrok url
* Start `python bin/app.py`

### Image Attribution

[Banner vector created by makyzz - www.freepik.com](https://www.freepik.com/vectors/banner)
