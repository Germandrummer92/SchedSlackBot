FROM python:3.11@sha256:b337e1fd27dbacda505219f713789bf82766694095876769ea10c2d34b4f470b as base

WORKDIR /app

RUN apt-get -y install curl
RUN curl -sSL https://install.python-poetry.org/install-poetry.py | python -
ENV PATH=/root/.local/bin:$PATH
RUN poetry config virtualenvs.create false

COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install --only main --no-interaction --no-ansi

COPY sched_slack_bot sched_slack_bot
COPY bin/app.py app.py

ENTRYPOINT uvicorn app:api
