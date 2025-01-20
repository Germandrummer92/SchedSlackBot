FROM python:3.13@sha256:d57ec66c94b9497b9f3c66f6cdddc1e4e0bad4c584397e0b57a721baef0e6fdc as base

WORKDIR /app

RUN apt-get -y install curl
RUN curl -sSL https://install.python-poetry.org/install-poetry.py | python -
ENV PATH=/root/.local/bin:$PATH
RUN poetry config virtualenvs.create false

COPY sched_slack_bot sched_slack_bot
COPY bin/app.py app.py
COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install --only main --no-interaction --no-ansi

ENTRYPOINT uvicorn app:api
