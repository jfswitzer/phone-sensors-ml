"""API endpoints for the phone sensors project."""

import datetime
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, Form, UploadFile
from fastapi.responses import RedirectResponse
from redis import Redis

from phone_sensors.birdnet import submit_analyze_audio_job
from phone_sensors.schemas import SensorStatus
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


@app.post("/upload")
async def upload(
    *,
    redis_conn: Redis = Depends(get_redis_connection),
    sensor_id: UUID = Form(...),
    timestamp: datetime.datetime = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    accuracy: float = Form(...),
    battery: float = Form(...),
    temperature: float = Form(...),
    audio_file: UploadFile,
) -> UUID:
    """
    This endpoint accepts metadata and audio file in wav format as form data.
    Data will be queued to be processed by the server.
    Returns a job ID in 128-bit UUID format.
    """
    metadata = SensorStatus(
        sensor_id=sensor_id,
        timestamp=timestamp,
        lat=lat,
        lon=lon,
        accuracy=accuracy,
        battery=battery,
        temperature=temperature,
    )
    file_path = Path(tempfile.mktemp(suffix=".wav"))
    file_path.write_bytes(await audio_file.read())
    job_id = submit_analyze_audio_job(redis_conn, file_path, sensor_status=metadata)
    return job_id
