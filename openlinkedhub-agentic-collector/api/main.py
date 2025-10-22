"""FastAPI service exposing collected records."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import yaml
from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .deps import get_session
from .models import Record

app = FastAPI(title="OpenLinkedHub Agentic Collector", version="1.0.0")


class RecordResponse(BaseModel):
    id: str
    source: str
    dataset: str
    resource_id: str
    tags: List[str]
    indicator: str
    province: Optional[str]
    province_code: Optional[str]
    year: Optional[str]
    date: Optional[str]
    value: Optional[float]
    raw: dict
    fetched_at: Optional[str]

    @classmethod
    def from_orm_record(cls, record: Record) -> "RecordResponse":
        data = record.to_dict()
        return cls(**data)


class PaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[RecordResponse]


@app.get("/api/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/api/meta/tags")
def meta_tags() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "agent" / "config" / "tags.yaml"
    tags = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return tags


@app.get("/api/records", response_model=PaginatedResponse)
def list_records(
    source: Optional[str] = None,
    province: Optional[str] = None,
    indicator: Optional[str] = None,
    year: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
):
    query = session.query(Record)
    if source:
        query = query.filter(Record.source == source)
    if province:
        query = query.filter(Record.province == province)
    if indicator:
        query = query.filter(Record.indicator == indicator)
    if year:
        query = query.filter(Record.year == year)
    if tag:
        query = query.filter(Record.tags.contains([tag]))
    total = query.count()
    results = query.offset(offset).limit(limit).all()
    items = [RecordResponse.from_orm_record(record) for record in results]
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=items)


@app.get("/")
def root() -> dict:
    return {"message": "OpenLinkedHub Agentic Collector API"}
