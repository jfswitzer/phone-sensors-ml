"""Data formats and database schema for the phone sensors project."""

import datetime
from typing import Any, Self
from uuid import UUID

from geoalchemy2 import Geometry, shape
from pydantic import BaseModel, field_serializer
from shapely import Point
from sqlmodel import Column, Field, SQLModel


class SensorStatus(SQLModel, table=True):
    """Schema for the SensorMetadata format."""

    __tablename__ = "sensor_status"  # type: ignore
    sensor_id: UUID = Field(primary_key=True)
    timestamp: datetime.datetime
    lat: float
    lon: float
    accuracy: float
    battery: float
    temperature: float
    coordinates: Any | None = Field(
        sa_column=Column(Geometry(geometry_type="POINT", srid=4326)), default=None
    )

    @field_serializer("sensor_id")
    def serialize_sensor_id(self, sensor_id: UUID) -> str:
        """Serialize sensor ID to a string."""
        return str(sensor_id)

    @field_serializer("coordinates")
    def serialize_coordinates(self, coords: Any) -> str | None:
        """Serialize coordinates to a tuple."""
        if coords is None:
            return None
        coords = shape.to_shape(coords)
        return f"POINT({coords.x}, {coords.y})"

    def add_coordinates(self) -> Self:
        """Generate coordinates from lat and lon."""
        self.coordinates = shape.from_shape(Point(self.lon, self.lat))
        return self


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

    __tablename__ = "detection"  # type: ignore
    detection_id: int = Field(default=None, primary_key=True)
    sensor_id: UUID = Field(foreign_key="sensor_status.sensor_id")
    timestamp: datetime.datetime
    duration: float
    lat: float
    lon: float
    coordinates: Any | None = Field(
        sa_column=Column(Geometry(geometry_type="POINT", srid=4326)), default=None
    )
    accuracy: float
    scientific_name: str
    common_name: str
    label: str
    confidence: float

    @classmethod
    def from_birdnet_detections(
        cls, birdnet_detections: list[BirdNetDetection], sensor_metadata: SensorStatus
    ) -> list["Detection"]:
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
                    scientific_name=detection.scientific_name,
                    common_name=detection.common_name,
                    label=detection.label,
                    confidence=detection.confidence,
                )
            )
        return detections

    @field_serializer("coordinates")
    def serialize_coordinates(self, coords: Any) -> tuple[float, float]:
        """Serialize coordinates to a tuple."""
        coords = shape.to_shape(coords)
        return coords.x, coords.y
