#!/usr/bin/env python3
"""
Cron job script to run the job scraper once and exit.
This is designed to be run by a system scheduler like cron.
"""

import logging
from job_scraper import run_scraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cron_job.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cron_job")

if __name__ == "__main__":
    logger.info("Starting scheduled job scraper run")
    run_scraper()
    logger.info("Completed scheduled job scraper run")
