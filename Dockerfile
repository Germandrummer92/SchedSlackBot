FROM python:3.13@sha256:884da97271696864c2eca77c6362b1c501196d6377115c81bb9dd8d538033ec3 as base

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
