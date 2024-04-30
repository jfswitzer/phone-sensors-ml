"""Main entry point for the application."""

from multiprocessing import Process

import rich
import uvicorn
from rq.worker_pool import WorkerPool

from phone_sensors.api import app
from phone_sensors.settings import get_redis_connection, get_settings

if __name__ == "__main__":
    rich.print(get_settings())
    api_process = Process(target=uvicorn.run, args=(app,), kwargs={"host": "0.0.0.0", "port": 8000})
    worker_pool_process = Process(
        target=WorkerPool(
            ["default", "high", "low"], num_workers=3, connection=next(get_redis_connection())
        ).start
    )
    api_process.start()
    worker_pool_process.start()
