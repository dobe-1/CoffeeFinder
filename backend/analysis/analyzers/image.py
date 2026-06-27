from io import BytesIO

import pytesseract
from PIL import Image

from backend.analysis.extractors import deduplicate_menu_items, extract_menu_items_from_text
from backend.analysis.models import DocumentAnalysis
from backend.models.menu import Menu

from .base import BaseAnalyzer


class ImageAnalyzer(BaseAnalyzer):
    def analyze(
        self,
        data: bytes,
        content_type: str,
        source_url: str | None = None,
    ) -> DocumentAnalysis:
        warnings: list[str] = []
        text = ""

        try:
            with Image.open(BytesIO(data)) as image:
                text = pytesseract.image_to_string(image, lang="deu+eng", config="--psm 6")
        except Exception as exc:
            warnings.append(f"OCR failed for {source_url or 'unknown source'}: {exc}")

        return DocumentAnalysis(
            source_url=source_url,
            content_type=content_type,
            extracted_text=text or None,
            menu=Menu(
                items=deduplicate_menu_items(extract_menu_items_from_text(text)) if text else [],
                currency="EUR",
            ),
            warnings=warnings,
        )
