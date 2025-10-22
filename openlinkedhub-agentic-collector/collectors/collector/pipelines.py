"""Data pipelines for validation and persistence."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from agent.utils.normalize import map_tags, normalize_indicator, normalize_province, parse_numeric
from api.models import Base, Record, create_engine_and_session


class ValidationPipeline:
    required_fields = ("source", "dataset", "resource_id", "indicator")

    def process_item(self, item: Any, spider: Any):  # pragma: no cover - Scrapy integration
        for field in self.required_fields:
            if not item.get(field):
                raise ValueError(f"Missing required field {field} in item {item}")
        province, province_code = normalize_province(item.get("province"))
        item["province"], item["province_code"] = province, province_code
        item["indicator"] = normalize_indicator(item.get("tags", [item.get("indicator")])[0], item.get("indicator"))
        item["value"] = parse_numeric(item.get("value")) or item.get("value")
        item.setdefault("tags", [item.get("indicator")])
        item["tags"] = map_tags(item.get("tags", []), item.get("indicator"))
        item.setdefault("fetched_at", datetime.utcnow().isoformat())
        return item


class DatabasePipeline:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or os.environ.get("DATABASE_URL", "sqlite:///data/collector.db")
        self._session_factory = None
        self._engine = None

    def open_spider(self, spider: Any) -> None:  # pragma: no cover - Scrapy hook
        self._engine, self._session_factory = create_engine_and_session(self.database_url)
        Base.metadata.create_all(self._engine)

    def close_spider(self, spider: Any) -> None:  # pragma: no cover - Scrapy hook
        if self._engine:
            self._engine.dispose()

    def process_item(self, item: Any, spider: Any):  # pragma: no cover - Scrapy integration
        session: Session = self._session_factory()
        try:
            record = Record.from_item(item)
            session.merge(record)
            session.commit()
        finally:
            session.close()
        return item


class ExportPipeline:
    def __init__(self) -> None:
        base = Path(os.environ.get("EXPORT_BASE", Path(__file__).resolve().parents[2] / "exports"))
        base.mkdir(exist_ok=True, parents=True)
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        self.jsonl_path = base / f"records_{timestamp}.jsonl"

    def process_item(self, item: Any, spider: Any):  # pragma: no cover - Scrapy integration
        with self.jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(item), ensure_ascii=False) + "\n")
        return item
