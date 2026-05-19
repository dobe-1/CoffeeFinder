from __future__ import annotations

from analysis.analyzers.base import BaseAnalyzer
from analysis.analyzers.generic import GenericAnalyzer
from analysis.analyzers.html import HtmlAnalyzer
from analysis.analyzers.image import ImageAnalyzer
from analysis.analyzers.pdf import PdfAnalyzer
from analysis.analyzers.text import TextAnalyzer
from analysis.models import DocumentKind


class AnalyzerRegistry:
    def __init__(self) -> None:
        self._analyzers: dict[DocumentKind, BaseAnalyzer] = {
            DocumentKind.HTML: HtmlAnalyzer(),
            DocumentKind.PDF: PdfAnalyzer(),
            DocumentKind.IMAGE: ImageAnalyzer(),
            DocumentKind.TEXT: TextAnalyzer(),
            DocumentKind.JSON: TextAnalyzer(),
            DocumentKind.XML: TextAnalyzer(),
            DocumentKind.BINARY: GenericAnalyzer(),
            DocumentKind.UNKNOWN: GenericAnalyzer(),
        }

    def get(self, kind: DocumentKind) -> BaseAnalyzer:
        return self._analyzers.get(kind, self._analyzers[DocumentKind.UNKNOWN])
