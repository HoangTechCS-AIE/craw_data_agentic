"""Spider for CKAN portals (data.gov.vn and local portals)."""
from __future__ import annotations

import csv
import io
import json
from typing import Iterable

import scrapy

from collector.items import RecordItem


class CkanPortalSpider(scrapy.Spider):
    name = "ckan_portal"

    def __init__(self, base_url: str, tag: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.tag = tag
        self.api_base = f"{self.base_url}/api/3/action"

    def start_requests(self):
        url = f"{self.api_base}/package_search?fq=tags:\"{self.tag}\"&rows=100"
        yield scrapy.Request(url, callback=self.parse_search, meta={"start": 0})

    def parse_search(self, response: scrapy.http.Response):
        payload = json.loads(response.text)
        results = payload.get("result", {})
        for package in results.get("results", []):
            dataset_name = package.get("name")
            dataset_title = package.get("title", dataset_name)
            for resource in package.get("resources", []):
                resource_id = resource.get("id")
                if not resource_id:
                    continue
                meta = {
                    "dataset": dataset_title,
                    "resource_id": resource_id,
                    "source": self.base_url,
                }
                if resource.get("datastore_active"):
                    datastore_url = f"{self.api_base}/datastore_search?resource_id={resource_id}&limit=5000"
                    yield scrapy.Request(datastore_url, callback=self.parse_datastore, meta=meta)
                else:
                    url = resource.get("url")
                    if not url:
                        continue
                    yield scrapy.Request(url, callback=self.parse_resource_file, meta=meta)
        start = response.meta.get("start", 0)
        count = results.get("count", 0)
        if start + 100 < count:
            next_start = start + 100
            next_url = f"{self.api_base}/package_search?fq=tags:\"{self.tag}\"&rows=100&start={next_start}"
            yield scrapy.Request(next_url, callback=self.parse_search, meta={"start": next_start})

    def parse_datastore(self, response: scrapy.http.Response):
        payload = json.loads(response.text)
        result = payload.get("result", {})
        records = result.get("records", [])
        for index, row in enumerate(records):
            yield self._build_item(row, response.meta, index)

    def parse_resource_file(self, response: scrapy.http.Response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        body = response.text
        if "json" in content_type or body.strip().startswith("{"):
            data = json.loads(body)
            rows = data.get("records") if isinstance(data, dict) else data
            for index, row in enumerate(rows or []):
                yield self._build_item(row, response.meta, index)
        else:
            reader = csv.DictReader(io.StringIO(body))
            for index, row in enumerate(reader):
                yield self._build_item(row, response.meta, index)

    def _build_item(self, row: dict, meta: dict, index: int) -> RecordItem:
        province = row.get("province") or row.get("tinh")
        year = row.get("year") or row.get("nam")
        value = row.get("value") or row.get("giatri")
        return RecordItem(
            id=f"{meta['resource_id']}:{row.get('_id', index)}",
            source=meta.get("source"),
            dataset=meta.get("dataset"),
            resource_id=meta.get("resource_id"),
            tags=[self.tag],
            indicator=self.tag,
            province=province,
            year=year,
            value=value,
            raw=row,
        )
