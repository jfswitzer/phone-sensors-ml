"""API endpoints for the phone sensors project."""

import datetime
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from pydub import AudioSegment
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}") from e


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
    status = SensorStatus(
        sensor_id=sensor_id,
        timestamp=timestamp,
        lat=lat,
        lon=lon,
        accuracy=accuracy,
        battery=battery,
        temperature=temperature,
    )
    status.add_coordinates()
    audio_data = await audio_file.read()
    file_name = audio_file.filename
    if file_name is None:
        raise HTTPException(
            status_code=400, detail="Missing file name, unable to determine file type."
        )

    file_path = Path(tempfile.gettempdir()) / file_name
    wav_file_path = file_path.with_suffix(".wav")
    file_path.write_bytes(audio_data)
    try:
        audio: AudioSegment = AudioSegment.from_file(file_path)
        audio.export(wav_file_path, format="wav")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error converting file to wav: {e}") from e

    file_path.unlink()
    return submit_analyze_audio_job(redis_conn, wav_file_path, status)
