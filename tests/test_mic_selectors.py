from __future__ import annotations

from scrapy import Request
from scrapy.http import HtmlResponse, TextResponse

from collectors.collector.spiders.mic_portal import MicPortalSpider, response_resource_id


def test_mic_listing_filters_by_tag():
    spider = MicPortalSpider(listing_url="https://opendata.mic.gov.vn/list", tag="internet")
    html = """
    <div class="dataset-item"><h3>Internet subscribers</h3><a href="detail.html">View</a></div>
    <div class="dataset-item"><h3>Other data</h3></div>
    """
    response = HtmlResponse(url="https://opendata.mic.gov.vn/list", body=html, encoding="utf-8")
    requests = list(spider.parse_listing(response))
    assert len(requests) == 1
    assert requests[0].url.endswith("detail.html")


def test_mic_resource_item_structure():
    spider = MicPortalSpider(listing_url="https://opendata.mic.gov.vn/list", tag="ict")
    request = Request(url="https://opendata.mic.gov.vn/data.json")
    request.meta.update({"dataset": "ICT", "source": "mic", "tag": "ict"})
    response = TextResponse(
        url="https://opendata.mic.gov.vn/data.json",
        body='[{"province":"Đà Nẵng","value":15}]',
        encoding="utf-8",
        request=request,
    )
    result = list(spider.parse_resource(response))
    assert result[0]["dataset"] == "ICT"
    assert result[0]["tags"] == ["ict"]
    assert response_resource_id("ICT", 0) == "ict-0"
