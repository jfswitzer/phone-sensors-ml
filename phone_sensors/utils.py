"""Utility functions"""

from geoalchemy2 import WKBElement
from geoalchemy2.shape import from_shape, to_shape
from shapely import Point


def to_coordinates(lat: float, lon: float) -> WKBElement:
    """Return a Shapely Point from latitude and longitude."""
    return from_shape(Point(lon, lat))


def from_coordinates(coords: WKBElement) -> tuple[float, float]:
    """Return lon, lat tuple from coordinates WKBElement"""
    point: Point = to_shape(coords)
    return point.x, point.y
