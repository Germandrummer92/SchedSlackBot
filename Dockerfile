FROM python:3.10 as base

WORKDIR /app

COPY sched_slack_bot .
COPY bin .
COPY poetry.lock .
COPY pyproject.toml .
COPY setup.py .

RUN apt-get -y install curl
RUN curl -sSL https://install.python-poetry.org/install-poetry.py | python -

RUN poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT python bin/app.py
