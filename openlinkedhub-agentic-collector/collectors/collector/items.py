"""Scrapy items for normalized records."""
from __future__ import annotations

import datetime as dt
from typing import List, Optional

import scrapy


class RecordItem(scrapy.Item):
    id = scrapy.Field()
    source = scrapy.Field()
    dataset = scrapy.Field()
    resource_id = scrapy.Field()
    tags = scrapy.Field()
    indicator = scrapy.Field()
    province = scrapy.Field()
    province_code = scrapy.Field()
    year = scrapy.Field()
    date = scrapy.Field()
    value = scrapy.Field()
    raw = scrapy.Field()
    fetched_at = scrapy.Field(serializer=lambda v: v or dt.datetime.utcnow().isoformat())


__all__ = ["RecordItem"]
