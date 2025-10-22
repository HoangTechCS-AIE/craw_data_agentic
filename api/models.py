"""Database models for collector records."""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

from sqlalchemy import JSON, Column, Date, DateTime, Float, MetaData, String, create_engine
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


class Record(Base):  # type: ignore[misc]
    __tablename__ = "records"

    id = Column(String(255), primary_key=True)
    source = Column(String(255), nullable=False)
    dataset = Column(String(255), nullable=False)
    resource_id = Column(String(255), nullable=False)
    tags = Column(JSON().with_variant(SQLITE_JSON(), "sqlite"), nullable=False)
    indicator = Column(String(255), nullable=False)
    province = Column(String(255))
    province_code = Column(String(32))
    year = Column(String(32))
    date = Column(Date)
    value = Column(Float)
    raw = Column(JSON().with_variant(SQLITE_JSON(), "sqlite"), nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def from_item(cls, item: Dict[str, Any]) -> "Record":
        fetched_at = item.get("fetched_at")
        if isinstance(fetched_at, str):
            try:
                fetched_at_dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
            except ValueError:
                fetched_at_dt = datetime.utcnow()
        else:
            fetched_at_dt = fetched_at or datetime.utcnow()
        return cls(
            id=item.get("id"),
            source=item.get("source"),
            dataset=item.get("dataset"),
            resource_id=item.get("resource_id"),
            tags=item.get("tags") or [],
            indicator=item.get("indicator"),
            province=item.get("province"),
            province_code=item.get("province_code"),
            year=str(item.get("year")) if item.get("year") else None,
            date=item.get("date"),
            value=float(item.get("value")) if item.get("value") not in (None, "") else None,
            raw=item.get("raw"),
            fetched_at=fetched_at_dt,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "dataset": self.dataset,
            "resource_id": self.resource_id,
            "tags": self.tags,
            "indicator": self.indicator,
            "province": self.province,
            "province_code": self.province_code,
            "year": self.year,
            "date": self.date.isoformat() if self.date else None,
            "value": self.value,
            "raw": self.raw,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "sqlite:///data/collector.db")


def create_engine_and_session(database_url: str | None = None):
    url = database_url or get_database_url()
    if url.startswith("sqlite:///"):
        db_path = Path(url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url, future=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return engine, SessionLocal
