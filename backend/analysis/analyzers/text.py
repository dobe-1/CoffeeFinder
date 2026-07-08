from backend.analysis.extractors import deduplicate_menu_items, extract_menu_items_from_text
from backend.analysis.models import DocumentAnalysis
from backend.models.menu import Menu

from .base import BaseAnalyzer


class TextAnalyzer(BaseAnalyzer):
    def analyze(
        self,
        data: bytes,
        content_type: str,
        source_url: str | None = None,
    ) -> DocumentAnalysis:
        text = data.decode("utf-8", errors="replace")
        return DocumentAnalysis(
            source_url=source_url,
            content_type=content_type,
            extracted_text=text,
            menu=Menu(
                items=deduplicate_menu_items(extract_menu_items_from_text(text)),
                currency="EUR",
            ),
        )
