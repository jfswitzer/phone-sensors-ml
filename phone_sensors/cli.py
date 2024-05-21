"""Main entry point for the application."""

from multiprocessing import Process

import rich
import uvicorn
from rq.worker_pool import WorkerPool
from sqlalchemy import create_engine

from phone_sensors.api import app
from phone_sensors.db import init_db
from phone_sensors.settings import get_redis_connection, get_settings


def main():
    """CLI entry point."""
    settings = get_settings()
    rich.print(settings)
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
