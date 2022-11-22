import logging

from fastapi import FastAPI, Request, Response

from slack_bolt.adapter.fastapi import SlackRequestHandler
from sched_slack_bot.controller import AppController

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

controller = AppController()

app_handler = SlackRequestHandler(controller.app)
api = FastAPI()


@api.post("/slack/events")
async def endpoint(req: Request) -> Response:
    return await app_handler.handle(req)


@api.get("/health")
async def health(req: Request) -> Response:
    return Response(status_code=200)
