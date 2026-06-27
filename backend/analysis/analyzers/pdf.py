from backend.analysis.extractors import deduplicate_menu_items, extract_menu_items_from_text
from backend.analysis.models import DocumentAnalysis
from backend.models.menu import Menu

from .base import BaseAnalyzer


class PdfAnalyzer(BaseAnalyzer):
    def analyze(
        self,
        data: bytes,
        content_type: str,
        source_url: str | None = None,
    ) -> DocumentAnalysis:
        return DocumentAnalysis(
            source_url=source_url,
            content_type=content_type,
            warnings=[
                f"PDF analysis missing for {source_url or 'unknown source'}. TODO(nick): add your extraction logic here,"
                " adapting to the existing interface. See image.py for example. Basically you only need to add text"
                " extraction and give it to extract_menu_items_from_text and deduplicate_menu_items."
            ],
        )
