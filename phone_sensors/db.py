"""Database initialization"""

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel

from phone_sensors.schemas import Detection


def init_db(engine: Engine) -> None:
    """Initialize the database"""
    SQLModel.metadata.create_all(engine)


def insert_detections(engine: Engine, detections: list[Detection]) -> None:
    """Insert a prediction into the database"""
    with Session(engine) as session:
        for detection in detections:
            session.add(detection)
        session.commit()
