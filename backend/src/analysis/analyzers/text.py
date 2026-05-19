from __future__ import annotations

from analysis.analyzers.base import BaseAnalyzer
from analysis.extractors import deduplicate_offers, extract_offers_from_text, extract_price_evidence
from analysis.models import DocumentAnalysis, DocumentKind, DocumentMetadata, DownloadedDocument


class TextAnalyzer(BaseAnalyzer):
    def analyze(self, document: DownloadedDocument) -> DocumentAnalysis:
        text = document.content.decode("utf-8", errors="replace")
        offers = deduplicate_offers(extract_offers_from_text(text, document.url, confidence=0.7))
        prices = extract_price_evidence(text, document.url, confidence=0.55)
        return DocumentAnalysis(
            source_url=document.url,
            final_url=document.final_url,
            kind=DocumentKind.TEXT,
            metadata=DocumentMetadata(
                content_type=document.content_type,
                status_code=document.status_code,
                headers=document.headers,
            ),
            extracted_text=text,
            offers=offers,
            detected_prices=prices,
        )
