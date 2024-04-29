"""Data formats and database schema for the phone sensors project."""

import datetime
from typing import Any
from uuid import UUID

from geoalchemy2 import Geometry, shape
from pydantic import BaseModel
from shapely import Point
from sqlmodel import Column, Field, SQLModel


class SensorMetadata(BaseModel):
    """Schema for the SensorMetadata format."""

    sensor_id: UUID
    timestamp: datetime.datetime
    lat: float
    lon: float
    accuracy: float


class BirdNetDetection(BaseModel):
    """Schema for the BirdNet detection format."""

    common_name: str
    scientific_name: str
    start_time: float
    end_time: float
    confidence: float
    label: str


class Detection(SQLModel, table=True):
    """Schema for the Prediction table."""

    detection_id: int = Field(default=None, primary_key=True)
    sensor_id: UUID = Field(default=None, foreign_key="sensor.id")
    timestamp: datetime.datetime = Field(default=datetime.datetime.now)
    duration: float = Field(default=None)
    lat: float = Field(default=None)
    lon: float = Field(default=None)
    coordinates: Any = Field(
        sa_column=Column(Geometry(geometry_type="POINT", srid=4326)), default=None
    )
    accuracy: float = Field(default=None)
    label: str = Field(nullable=False)
    confidence: float = Field(default=0)

    @classmethod
    def from_birdnet_detections(cls, birdnet_detections, sensor_metadata) -> list["Detection"]:
        """Create a list of Detection instances from BirdNet detections."""
        detections = []
        for detection in birdnet_detections:
            detections.append(
                Detection(
                    sensor_id=sensor_metadata.sensor_id,
                    timestamp=sensor_metadata.timestamp
                    + datetime.timedelta(seconds=detection.start_time),
                    duration=detection.end_time - detection.start_time,
                    lat=sensor_metadata.lat,
                    lon=sensor_metadata.lon,
                    coordinates=shape.from_shape(Point(sensor_metadata.lon, sensor_metadata.lat)),
                    accuracy=sensor_metadata.accuracy,
                    label=detection.label,
                    confidence=detection.confidence,
                )
            )
        return detections
