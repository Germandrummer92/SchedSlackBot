import logging
import os

from sched_slack_bot.app import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    port = int(os.environ.get("PORT", 3000))
    logger.info(f"Starting SchedSlackBot on Port {port}")
    app.start(port=port)
