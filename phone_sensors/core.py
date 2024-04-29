"""Core functionality for phone_sensors package."""

import logging

from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from pydantic import FilePath

from phone_sensors.schemas import BirdNetDetection, SensorMetadata

logger = logging.getLogger(__name__)


def analyze_audio(file_path: FilePath, sensor_metadata: SensorMetadata) -> list[BirdNetDetection]:
    """Analyze audio file and return list of bird species."""
    logger.info("Analyzing audio file %s...", file_path)
    logger.debug("Sensor metadata: %s", sensor_metadata.model_dump_json(indent=2))
    recording = Recording(
        analyzer=Analyzer(),
        path=file_path,
        lat=sensor_metadata.lat,
        lon=sensor_metadata.lon,
        min_conf=0.25,
    )
    recording.analyze()
    return recording.detections
