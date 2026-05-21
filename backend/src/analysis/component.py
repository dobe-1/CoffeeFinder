from __future__ import annotations

from collections.abc import Callable

import requests
from analysis.models import CoffeeShopIdentity, DownloadedDocument
from analysis.service import AnalyzerService


def default_document_downloader(url: str) -> DownloadedDocument:
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "CoffeeFinder/0.1"},
        allow_redirects=True,
    )
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    return DownloadedDocument(
        url=url,
        final_url=str(response.url),
        content_type=content_type or "text/html",
        status_code=response.status_code,
        headers={key.lower(): value for key, value in response.headers.items()},
        content=response.content,
    )


class AnalyzerComponent:
    def __init__(
        self,
        analyzer_service: AnalyzerService | None = None,
        downloader: Callable[[str], DownloadedDocument] | None = None,
    ) -> None:
        self.analyzer_service = analyzer_service or AnalyzerService()
        self.downloader = downloader or default_document_downloader

    def analyze_cafe(self, cafe: dict, menu_url_override: str | None = None) -> dict:
        menu_url = menu_url_override or cafe.get("menu_url")
        if not menu_url:
            enriched = dict(cafe)
            enriched["menu"] = {"currency": "EUR", "source_urls": [], "offers": []}
            return enriched

        document = self.downloader(menu_url)
        identity = CoffeeShopIdentity(
            name=cafe["name"],
            website=cafe.get("website_url"),
            latitude=cafe.get("coordinates", [None, None])[0],
            longitude=cafe.get("coordinates", [None, None])[1],
        )
        record = self.analyzer_service.analyze_downloaded_documents(identity, [document])
        return self._merge_with_cafe(cafe, record)

    def _merge_with_cafe(self, cafe: dict, record) -> dict:
        currency = next((offer.currency for offer in record.offers if offer.currency), "EUR")
        offers = [
            {"name": offer.name, "price": offer.price_eur}
            for offer in record.offers
            if offer.price_eur is not None
        ]

        enriched = dict(cafe)
        enriched["menu"] = {
            "currency": currency,
            "source_urls": [source.url for source in record.sources],
            "offers": offers,
        }
        return enriched
