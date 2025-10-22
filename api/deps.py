"""Dependency helpers for FastAPI."""
from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from .models import Base, create_engine_and_session

_engine, SessionLocal = create_engine_and_session()
Base.metadata.create_all(_engine)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
