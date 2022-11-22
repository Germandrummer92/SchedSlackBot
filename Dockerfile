FROM python:3.10 as base

WORKDIR /app

RUN apt-get -y install curl
RUN curl -sSL https://install.python-poetry.org/install-poetry.py | python -
ENV PATH=/root/.local/bin:$PATH
RUN poetry config virtualenvs.create false

COPY poetry.lock .
COPY pyproject.toml .
COPY setup.py .
RUN poetry install --only main --no-interaction --no-ansi

COPY sched_slack_bot sched_slack_bot
COPY bin/app.py app.py

ENTRYPOINT uvicorn app:api
