import os
import asyncio
import logging
from datetime import datetime
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "scheduler.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  
        logging.StreamHandler()         
    ],
)

# Initialize APScheduler with AsyncIO support
scheduler = AsyncIOScheduler(executors={"default": AsyncIOExecutor()})


# Disable APScheduler internal logging
logging.getLogger("apscheduler").setLevel(logging.WARNING)

# Define an asynchronous task that logs the timestamp
async def log_timestamp():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Async Cron Job Executed Successfully at {timestamp}")

    # Simulating an async non-blocking task (e.g., database update, API request)
    await asyncio.sleep(1)

scheduler.add_job(log_timestamp, "interval", hours=6)


def start_scheduler():
    scheduler.start()
    logging.info("Async APScheduler has started and logs will be saved in 'logs/scheduler.log'")
