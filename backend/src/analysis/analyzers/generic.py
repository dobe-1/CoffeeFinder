from __future__ import annotations

from analysis.analyzers.base import BaseAnalyzer
from analysis.models import DocumentAnalysis, DocumentKind, DocumentMetadata, DownloadedDocument


class GenericAnalyzer(BaseAnalyzer):
    def analyze(self, document: DownloadedDocument) -> DocumentAnalysis:
        return DocumentAnalysis(
            source_url=document.url,
            final_url=document.final_url,
            kind=DocumentKind.BINARY,
            metadata=DocumentMetadata(
                content_type=document.content_type,
                status_code=document.status_code,
                headers=document.headers,
            ),
            warnings=["No specialized analyzer available for this document type yet."],
        )
