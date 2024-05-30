"""Main entry point for the application."""

import logging
from multiprocessing import Process

import uvicorn
from rich.logging import RichHandler
from rq.worker_pool import WorkerPool
from sqlalchemy import create_engine

from phone_sensors.api import app
from phone_sensors.db import init_db
from phone_sensors.settings import get_redis_connection, get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)


def main():
    """CLI entry point."""
    settings = get_settings()
    logger.info(settings.model_dump())
    engine = create_engine(str(settings.postgres_dsn))
    init_db(engine)
    api_process = Process(
        target=uvicorn.run, args=(app,), kwargs={"host": settings.host, "port": settings.port}
    )
    worker_pool_process = Process(
        target=WorkerPool(
            ["default", "high", "low"], num_workers=3, connection=next(get_redis_connection())
        ).start
    )
    api_process.start()
    worker_pool_process.start()
