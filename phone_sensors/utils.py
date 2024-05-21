"""Utility functions"""

from geoalchemy2 import WKBElement
from geoalchemy2.shape import from_shape, to_shape
from pydantic import FilePath
from pydub import AudioSegment
from shapely import Point


def to_coordinates(lat: float, lon: float) -> WKBElement:
    """Return a Shapely Point from latitude and longitude."""
    return from_shape(Point(lon, lat))


def from_coordinates(coords: WKBElement) -> tuple[float, float]:
    """Return lon, lat tuple from coordinates WKBElement"""
    point: Point = to_shape(coords)
    return point.x, point.y


def convert_to_wav(src_path: FilePath, dest_path: FilePath | None = None) -> FilePath:
    """Convert audio file to wav format."""
    audio = AudioSegment.from_file(src_path)
    if dest_path is None:
        dest_path = src_path.with_suffix(".wav")
    audio.export(dest_path, format="wav")
    return dest_path
