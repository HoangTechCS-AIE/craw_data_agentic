from __future__ import annotations

import json

from scrapy.http import TextResponse

from collectors.collector.spiders.ckan_portal import CkanPortalSpider


def test_ckan_parse_search_generates_requests():
    spider = CkanPortalSpider(base_url="https://data.gov.vn", tag="internet")
    body = json.dumps(
        {
            "result": {
                "count": 1,
                "results": [
                    {
                        "name": "internet-usage",
                        "title": "Internet usage",
                        "resources": [
                            {
                                "id": "resource-1",
                                "datastore_active": True,
                            }
                        ],
                    }
                ],
            }
        }
    )
    response = TextResponse(url="https://data.gov.vn/api/3/action/package_search", body=body, encoding="utf-8")
    results = list(spider.parse_search(response))
    assert results, "Spider should yield datastore request"
    request = results[0]
    assert "datastore_search" in request.url
    assert request.meta["resource_id"] == "resource-1"


def test_ckan_build_item_normalizes_fields():
    spider = CkanPortalSpider(base_url="https://data.gov.vn", tag="ict")
    item = spider._build_item(
        {"province": "Hà Nội", "year": "2023", "value": "10", "_id": 1},
        {"dataset": "ICT stats", "resource_id": "abc", "source": "https://data.gov.vn"},
        0,
    )
    assert item["province"] == "Hà Nội"
    assert item["tags"] == ["ict"]
    assert item["indicator"] == "ict"
