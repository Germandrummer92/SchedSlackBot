import logging

from sched_slack_bot.controller import AppController

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

controller = AppController()
api = controller.start()
