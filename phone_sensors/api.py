"""API endpoints for the phone sensors project."""

import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, UploadFile
from fastapi.responses import RedirectResponse
from redis import Redis
from sqlmodel import Session

from phone_sensors.birdnet import submit_analyze_audio_job
from phone_sensors.schemas import SensorMetadata
from phone_sensors.settings import get_db_session, get_redis_connection

app = FastAPI(title="Phone Sensors API", version="0.1.0")


@app.get("/")
def read_root() -> RedirectResponse:
    """Redirects to the API documentation page."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check() -> str:
    """Health check endpoint."""
    try:
        get_db_session()
        get_redis_connection()
        return "OK"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Error: {e}"


@app.post("/sensor_upload")
async def sensor_upload(
    *,
    session: Session = Depends(get_db_session),
    redis_conn: Redis = Depends(get_redis_connection),
    metadata: SensorMetadata,
    audio_file: UploadFile,
) -> UUID:
    """
    This endpoint accepts a metadata and audio file in wav format.
    Data will be queued to be processed by the server.
    Returns a job ID in 128-bit UUID format.
    """
    file_path = Path(tempfile.mktemp(suffix=".wav"))
    file_path.write_bytes(await audio_file.read())
    job_id = submit_analyze_audio_job(session, redis_conn, file_path, sensor_metadata=metadata)
    return job_id


@app.post("/register_sensor")
def register_sensor() -> dict:
    """Sensor registration endpoint."""
    raise NotImplementedError("Not implemented yet")
