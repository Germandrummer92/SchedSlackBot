FROM python:3.13@sha256:385ccb8304f6330738a6d9e6fa0bd7608e006da7e15bc52b33b0398e1ba4a15b as base

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
