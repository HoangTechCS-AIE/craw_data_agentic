"""Project wide Scrapy settings."""
import os
from datetime import datetime

BOT_NAME = "openlinkedhub"

SPIDER_MODULES = ["collector.spiders"]
NEWSPIDER_MODULE = "collector.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 0.5
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_BACKOFF_BASE = 2
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "OpenLinkedHubCollector/1.0 (+https://openlinkedhub.org)",
    "Accept-Language": "en",
}

FEED_EXPORT_ENCODING = "utf-8"
_timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
FEEDS = {
    f"exports/%(name)s/{_timestamp}.jsonl": {
        "format": "jsonlines",
        "encoding": "utf-8",
        "overwrite": False,
    },
    f"exports/%(name)s/{_timestamp}.csv": {
        "format": "csv",
        "encoding": "utf-8",
        "overwrite": False,
    },
}

ITEM_PIPELINES = {
    "collector.pipelines.ValidationPipeline": 100,
    "collector.pipelines.DatabasePipeline": 200,
    "collector.pipelines.ExportPipeline": 400,
}

LOG_LEVEL = os.environ.get("SCRAPY_LOG_LEVEL", "INFO")

JOBDIR = "jobdir"
