import io
import pdfplumber
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
        warnings: list[str] = []
        text = ""
        try:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                extracted_pages = []

                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_pages.append(page_text)

                text = "\n".join(extracted_pages)

        except Exception as exc:
            warnings.append(f"PDF text extraction failed for {source_url or 'unknown source'}: {exc}")

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
