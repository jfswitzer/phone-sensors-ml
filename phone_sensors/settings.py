"""This module manages the settings for the backend services."""

from typing import Generator

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from redis import Redis
from sqlmodel import Session, create_engine


class Settings(BaseSettings):
    """Settings for phone_sensors package."""

    redis_dsn: RedisDsn = Field("redis://redis:6379/0")
    postgres_dsn: PostgresDsn = Field("postgresql://postgres:phonesensors@db/sensor_data")
    birdnet_min_confidence: float = Field(0.25)


def get_settings() -> Settings:
    """Get server settings"""
    return Settings()  # type: ignore


def get_redis_connection() -> Generator[Redis, None, None]:
    """Return a generator of Redis connection"""
    with Redis.from_url(str(get_settings().redis_dsn)) as connection:
        yield connection


def get_db_session() -> Generator[Session, None, None]:
    """Returna generator of SQLAlchemy session"""
    with Session(create_engine(str(get_settings().postgres_dsn))) as session:
        yield session
