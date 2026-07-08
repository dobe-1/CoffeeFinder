from datetime import UTC, datetime

from backend.analysis.analyzers.base import BaseAnalyzer
from backend.analysis.analyzers.image import ImageAnalyzer
from backend.analysis.analyzers.pdf import PdfAnalyzer
from backend.analysis.analyzers.text import TextAnalyzer
from backend.models import CoffeeShop


class Analyzer:
    def __init__(self) -> None:
        self.text_analyzer = TextAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.pdf_analyzer = PdfAnalyzer()
        self.base_analyzer = BaseAnalyzer()

    def analyze(self, coffee_shop: CoffeeShop, data: bytes, content_type: str) -> CoffeeShop:
        analyzer = self._analyzer_for_content_type(content_type)
        analysis = analyzer.analyze(
            data=data,
            content_type=content_type,
            source_url=coffee_shop.menu.menu_url,
        )
        coffee_shop.menu.items = analysis.menu.items
        coffee_shop.menu.currency = analysis.menu.currency or "EUR"
        coffee_shop.menu.extracted_at = datetime.now(tz=UTC)
        return coffee_shop

    def _analyzer_for_content_type(self, content_type: str) -> BaseAnalyzer:
        normalized = content_type.lower().split(";", 1)[0].strip()
        if normalized.startswith("image/"):
            return self.image_analyzer

        analyzers: dict[str, BaseAnalyzer] = {
            "application/pdf": self.pdf_analyzer,
            "application/xhtml+xml": self.text_analyzer,
            "application/json": self.text_analyzer,
            "application/xml": self.text_analyzer,
            "text/html": self.text_analyzer,
            "text/plain": self.text_analyzer,
            "text/xml": self.text_analyzer,
        }
        return analyzers.get(normalized, self.base_analyzer)
