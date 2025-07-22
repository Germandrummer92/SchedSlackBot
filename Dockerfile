FROM python:3.13@sha256:5f69d22a88dd4cc4ee1576def19aef48c8faa1b566054c44291183831cbad13b as base

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
