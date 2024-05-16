"""BirdNet audio analysis functions."""

import logging
from uuid import UUID

from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from pydantic import FilePath
from redis import Redis
from rq import Callback, Queue
from rq.job import Job
from sqlmodel import select

from phone_sensors.schemas import BirdNetDetection, Detection, SensorStatus
from phone_sensors.settings import get_db_session, get_settings

logger = logging.getLogger(__name__)


def analyze_audio(
    file_path: FilePath, sensor_status: SensorStatus, min_conf: float
) -> tuple[list[BirdNetDetection], SensorStatus]:
    """Analyze audio file and return list of bird species."""
    logger.info("Analyzing audio file %s...", file_path)
    logger.debug("Sensor metadata: %s", sensor_status.model_dump_json(indent=2))
    recording = Recording(
        analyzer=Analyzer(),
        path=file_path,
        lat=sensor_status.lat,
        lon=sensor_status.lon,
        min_conf=min_conf,
    )
    recording.analyze()
    detections = [BirdNetDetection.model_validate(d) for d in recording.detections]
    return detections, sensor_status


def on_analyze_audio_job_success(
    job: Job,  # pylint: disable=unused-argument # type: ignore
    connection: Redis,  # pylint: disable=unused-argument # type: ignore
    result: tuple[list[BirdNetDetection], SensorStatus],
    *args,
    **kwargs
) -> None:  # pylint: disable=unused-argument # type: ignore
    """Callback for analyze_audio job success."""
    detections, sensor_status = result
    print("Processing result:", result)
    # update sensor status if exists, otherwise create new
    sensor_status.add_coordinates()
    session = next(get_db_session())
    curr_status = session.exec(
        select(SensorStatus).where(SensorStatus.sensor_id == sensor_status.sensor_id)
    ).one_or_none()
    if curr_status:
        curr_status.timestamp = sensor_status.timestamp
        curr_status.lat = sensor_status.lat
        curr_status.lon = sensor_status.lon
        curr_status.accuracy = sensor_status.accuracy
        curr_status.battery = sensor_status.battery
        curr_status.temperature = sensor_status.temperature
        curr_status.coordinates = sensor_status.coordinates
    else:
        session.add(sensor_status)
    session.commit()

    session.add_all(Detection.from_birdnet_detections(detections, sensor_status))
    session.commit()


def submit_analyze_audio_job(
    connection: Redis, file_path: FilePath, sensor_status: SensorStatus
) -> UUID:
    """Analyze audio file and return list of bird species."""
    job = Queue(connection=connection).enqueue(
        analyze_audio,
        file_path=file_path,
        sensor_status=sensor_status,
        min_conf=get_settings().birdnet_min_confidence,
        on_success=Callback(on_analyze_audio_job_success),
    )
    return job.id
