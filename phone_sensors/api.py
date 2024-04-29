"""API endpoints for the phone sensors project."""

import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile
from fastapi.responses import RedirectResponse
from sqlmodel import create_engine

from phone_sensors.core import analyze_audio
from phone_sensors.db import insert_detections
from phone_sensors.schemas import Detection, SensorMetadata

app = FastAPI()
engine = create_engine("postgresql://postgres:phonesensors@db/sensor_data")


@app.get("/")
def read_root() -> RedirectResponse:
    """Redirects to the API documentation page."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/sensor_upload")
async def sensor_upload(metadata: SensorMetadata, file: UploadFile) -> list[Detection]:
    """Sensor data upload endpoint."""
    file_path = Path(tempfile.mktemp(suffix=".wav"))
    file_path.write_bytes(await file.read())
    birdnet_detections = analyze_audio(file_path, metadata)
    detections = Detection.from_birdnet_detections(birdnet_detections, metadata)
    insert_detections(engine, detections)
    return detections


@app.post("/register_sensor")
def register_sensor() -> dict:
    """Sensor registration endpoint."""
    raise NotImplementedError("Not implemented yet")
