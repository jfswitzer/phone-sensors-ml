"""BirdNet audio analysis functions."""

import logging
from functools import partial
from uuid import UUID

from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from pydantic import FilePath
from redis import Redis
from rq import Callback, Queue
from rq.job import Job
from sqlmodel import Session

from phone_sensors.schemas import BirdNetDetection, Detection, SensorMetadata
from phone_sensors.settings import get_settings

logger = logging.getLogger(__name__)


def analyze_audio(
    file_path: FilePath, sensor_metadata: SensorMetadata, min_conf: float
) -> list[BirdNetDetection]:
    """Analyze audio file and return list of bird species."""
    logger.info("Analyzing audio file %s...", file_path)
    logger.debug("Sensor metadata: %s", sensor_metadata.model_dump_json(indent=2))
    recording = Recording(
        analyzer=Analyzer(),
        path=file_path,
        lat=sensor_metadata.lat,
        lon=sensor_metadata.lon,
        min_conf=min_conf,
    )
    recording.analyze()
    return recording.detections


def on_analyze_audio_job_success(
    job: Job,
    connection: Redis,
    result: list[BirdNetDetection],
    *args,
    session: Session,
    sensor_metadata: SensorMetadata,
    **kwargs
):  # pylint: disable=unused-argument # type: ignore
    """Callback for analyze_audio job success."""
    session.add_all(Detection.from_birdnet_detections(result, sensor_metadata))
    session.commit()


def submit_analyze_audio_job(
    session: Session, connection: Redis, file_path: FilePath, sensor_metadata: SensorMetadata
) -> UUID:
    """Analyze audio file and return list of bird species."""
    job = Queue(connection=connection).enqueue(
        analyze_audio,
        file_path=file_path,
        sensor_metadata=sensor_metadata,
        min_conf=get_settings().birdnet_min_confidence,
        on_success=Callback(
            partial(on_analyze_audio_job_success, sensor_metadata=sensor_metadata, session=session)
        ),
    )
    return job.id
