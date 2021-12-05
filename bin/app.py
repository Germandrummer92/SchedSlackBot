import logging

from sched_slack_bot.controller import AppController

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    controller = AppController()

    controller.start()
