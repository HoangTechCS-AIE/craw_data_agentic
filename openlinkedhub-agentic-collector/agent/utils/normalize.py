"""Helpers to normalize datasets into the common schema."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from slugify import slugify

PROVINCE_PATH = Path(__file__).resolve().parent / "province_map_vi.json"


@lru_cache(maxsize=1)
def _province_map() -> Dict[str, Dict[str, Any]]:
    with PROVINCE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_province(raw: str | None) -> Tuple[Optional[str], Optional[str]]:
    if not raw:
        return None, None
    raw_clean = raw.strip()
    data = _province_map()
    for name, payload in data.items():
        if raw_clean.lower() == name.lower() or raw_clean in payload.get("aliases", []):
            return name, payload.get("code")
        for alias in payload.get("aliases", []):
            if raw_clean.lower() == alias.lower():
                return name, payload.get("code")
    return raw_clean, None


def normalize_indicator(tag: str, indicator: str | None = None) -> str:
    base = indicator or tag
    return slugify(base, separator="-")


def parse_numeric(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").strip()
        if cleaned == "":
            return None
        match = re.match(r"^-?\d+(\.\d+)?$", cleaned)
        if match:
            return float(cleaned)
    return None


def map_tags(source_tags: list[str], matched_tag: str) -> list[str]:
    tags = list(dict.fromkeys([matched_tag, *source_tags]))
    return tags
