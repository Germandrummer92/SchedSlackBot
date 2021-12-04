import logging
import os

from sched_slack_bot.app import app, start_all_schedules

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    port = int(os.environ.get("PORT", 3000))
    logger.info(f"Starting SchedSlackBot on Port {port}")
    start_all_schedules()
    app.start(port=port)
