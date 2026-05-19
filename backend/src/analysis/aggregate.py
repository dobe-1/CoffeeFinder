from __future__ import annotations

from collections import Counter

from .extractors import deduplicate_offers
from .models import CoffeeShopIdentity, CoffeeShopRecord, DocumentAnalysis, SourceSummary


def aggregate_shop(identity: CoffeeShopIdentity, analyses: list[DocumentAnalysis]) -> CoffeeShopRecord:
    offers = deduplicate_offers([offer for analysis in analyses for offer in analysis.offers])
    media = [image for analysis in analyses for image in analysis.images]
    sources = [
        SourceSummary(
            url=analysis.source_url,
            final_url=analysis.final_url,
            kind=analysis.kind,
            content_type=analysis.metadata.content_type,
            title=analysis.metadata.title,
            offers_found=len(analysis.offers),
            images_found=len(analysis.images),
            warnings=analysis.warnings,
        )
        for analysis in analyses
    ]

    offer_counter = Counter(offer.name.lower() for offer in offers)
    return CoffeeShopRecord(
        identity=identity,
        offers=offers,
        media=media,
        sources=sources,
        source_analyses=analyses,
        signals={
            "offer_count": len(offers),
            "media_count": len(media),
            "source_count": len(sources),
            "top_offer_names": [name for name, _count in offer_counter.most_common(10)],
        },
    )
