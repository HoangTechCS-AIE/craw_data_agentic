"""Spider for World Bank indicators."""
from __future__ import annotations

import json

import scrapy

from collector.items import RecordItem


class WorldbankSpider(scrapy.Spider):
    name = "worldbank"

    def __init__(self, tag: str, indicators: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag = tag
        self.indicators = [code.strip() for code in indicators.split(",") if code.strip()]

    def start_requests(self):
        for code in self.indicators:
            url = f"https://api.worldbank.org/v2/country/VNM/indicator/{code}?format=json&per_page=20000"
            yield scrapy.Request(url, callback=self.parse_indicator, meta={"indicator_code": code})

    def parse_indicator(self, response: scrapy.http.Response):
        data = json.loads(response.text)
        if not isinstance(data, list) or len(data) < 2:
            return
        records = data[1] or []
        for entry in records:
            if entry.get("value") is None:
                continue
            yield RecordItem(
                id=f"worldbank:{entry.get('indicator', {}).get('id')}:{entry.get('date')}",
                source="https://api.worldbank.org",
                dataset=entry.get("indicator", {}).get("value"),
                resource_id=entry.get("indicator", {}).get("id"),
                tags=[self.tag],
                indicator=self.tag,
                province=None,
                year=entry.get("date"),
                value=entry.get("value"),
                raw=entry,
            )
