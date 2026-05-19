from __future__ import annotations

from analysis.analyzers.base import BaseAnalyzer
from analysis.extractors import deduplicate_offers, extract_offers_from_text, extract_price_evidence
from analysis.models import DocumentAnalysis, DocumentKind, DocumentMetadata, DownloadedDocument

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None


class PdfAnalyzer(BaseAnalyzer):
    def analyze(self, document: DownloadedDocument) -> DocumentAnalysis:
        warnings: list[str] = []
        if fitz is None:
            warnings.append("PyMuPDF is not installed; PDF analysis skipped.")
            return DocumentAnalysis(
                source_url=document.url,
                final_url=document.final_url,
                kind=DocumentKind.PDF,
                metadata=DocumentMetadata(
                    content_type=document.content_type,
                    status_code=document.status_code,
                    headers=document.headers,
                ),
                warnings=warnings,
            )

        pdf = fitz.open(stream=document.content, filetype="pdf")
        text_parts: list[str] = []
        image_count = 0
        for page in pdf:
            text_parts.append(page.get_text("text"))
            image_count += len(page.get_images(full=True))
        pdf.close()

        extracted_text = "\n".join(text_parts).strip()
        offers = deduplicate_offers(extract_offers_from_text(extracted_text, document.url, confidence=0.8))
        prices = extract_price_evidence(extracted_text, document.url, confidence=0.7)

        return DocumentAnalysis(
            source_url=document.url,
            final_url=document.final_url,
            kind=DocumentKind.PDF,
            metadata=DocumentMetadata(
                content_type=document.content_type,
                status_code=document.status_code,
                headers=document.headers,
            ),
            extracted_text=extracted_text,
            offers=offers,
            detected_prices=prices,
            raw_signals={
                "page_count": len(text_parts),
                "embedded_image_count": image_count,
            },
            warnings=warnings,
        )
