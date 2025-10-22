"""Spider for MIC open data portal."""
from __future__ import annotations

import csv
import io
import json
from urllib.parse import urljoin

import scrapy

from collector.items import RecordItem


class MicPortalSpider(scrapy.Spider):
    name = "mic_portal"
    custom_settings = {"DOWNLOAD_DELAY": 1}

    def __init__(self, listing_url: str, tag: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listing_url = listing_url
        self.tag = tag.lower()

    def start_requests(self):
        yield scrapy.Request(self.listing_url, callback=self.parse_listing)

    def parse_listing(self, response: scrapy.http.Response):
        cards = response.css(".dataset-item")
        for card in cards:
            title = " ".join(card.css("*::text").getall()).strip()
            if self.tag in title.lower():
                link = card.css("a::attr(href)").get()
                if link:
                    yield response.follow(link, callback=self.parse_dataset, meta={"title": title})
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_listing)

    def parse_dataset(self, response: scrapy.http.Response):
        title = response.meta.get("title")
        links = response.css("a[href$='.csv']::attr(href), a[href$='.json']::attr(href)").getall()
        for link in links:
            absolute = urljoin(response.url, link)
            yield scrapy.Request(absolute, callback=self.parse_resource, meta={"dataset": title, "source": "https://opendata.mic.gov.vn", "tag": self.tag})

    def parse_resource(self, response: scrapy.http.Response):
        body = response.text
        if response.url.endswith(".json") or "json" in response.headers.get("Content-Type", b"").decode().lower():
            data = json.loads(body)
            rows = data if isinstance(data, list) else data.get("data") or data.get("records") or []
            for index, row in enumerate(rows):
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
            id=f"mic:{index}:{row.get('id', '')}",
            source=meta.get("source"),
            dataset=meta.get("dataset"),
            resource_id=response_resource_id(meta.get("dataset"), index),
            tags=[meta.get("tag", self.tag)],
            indicator=meta.get("tag", self.tag),
            province=province,
            year=year,
            value=value,
            raw=row,
        )


def response_resource_id(dataset: str | None, index: int) -> str:
    slug = (dataset or "mic").lower().replace(" ", "-")
    return f"{slug}-{index}"
