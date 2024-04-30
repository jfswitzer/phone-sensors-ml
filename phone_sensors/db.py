"""Database initialization"""

from sqlalchemy import Engine
from sqlmodel import SQLModel


def init_db(engine: Engine) -> None:
    """Initialize the database"""
    SQLModel.metadata.create_all(engine)
