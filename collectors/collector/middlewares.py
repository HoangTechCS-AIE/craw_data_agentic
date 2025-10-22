"""Placeholders for optional Scrapy middlewares."""
from __future__ import annotations

from scrapy import signals


class CollectorSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):  # pragma: no cover - Scrapy integration
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):  # pragma: no cover - Scrapy integration
        spider.logger.info("Spider opened: %s", spider.name)


class CollectorDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):  # pragma: no cover - Scrapy integration
        return cls()
