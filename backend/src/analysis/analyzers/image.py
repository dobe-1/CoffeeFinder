from __future__ import annotations

from io import BytesIO

from analysis.analyzers.base import BaseAnalyzer
from analysis.extractors import deduplicate_offers, extract_offers_from_text, extract_price_evidence
from analysis.models import (
    DocumentAnalysis,
    DocumentKind,
    DocumentMetadata,
    DownloadedDocument,
    ImageInfo,
)

try:
    import pytesseract
except ImportError:  # pragma: no cover
    pytesseract = None

try:
    from PIL import ExifTags, Image
except ImportError:  # pragma: no cover
    ExifTags = None
    Image = None


class ImageAnalyzer(BaseAnalyzer):
    def analyze(self, document: DownloadedDocument) -> DocumentAnalysis:
        warnings: list[str] = []
        images: list[ImageInfo] = []
        extracted_text = None

        if Image is None:
            warnings.append("Pillow is not installed; image metadata extraction skipped.")
            return DocumentAnalysis(
                source_url=document.url,
                final_url=document.final_url,
                kind=DocumentKind.IMAGE,
                metadata=DocumentMetadata(
                    content_type=document.content_type,
                    status_code=document.status_code,
                    headers=document.headers,
                ),
                warnings=warnings,
            )

        with Image.open(BytesIO(document.content)) as image:
            exif: dict[str, str] = {}
            if hasattr(image, "getexif"):
                raw_exif = image.getexif()
                for tag_id, value in raw_exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id)) if ExifTags else str(tag_id)
                    exif[tag_name] = str(value)

            if pytesseract is None:
                warnings.append("pytesseract is not installed; OCR skipped.")
            else:
                try:
                    # Menu images are usually column-like layouts, so psm 4 tends to preserve
                    # the item/price structure better than the default text-block mode.
                    extracted_text = pytesseract.image_to_string(
                        image,
                        lang="deu+eng",
                        config="--psm 4",
                    )
                except Exception as exc:  # pragma: no cover
                    warnings.append(f"OCR failed: {exc}")

            images.append(
                ImageInfo(
                    url=document.url,
                    width=image.width,
                    height=image.height,
                    format=image.format,
                    exif=exif,
                    ocr_text=extracted_text,
                )
            )

        offers = (
            deduplicate_offers(
                extract_offers_from_text(extracted_text, document.url, confidence=0.65)
            )
            if extracted_text
            else []
        )
        prices = (
            extract_price_evidence(extracted_text, document.url, confidence=0.55)
            if extracted_text
            else []
        )

        return DocumentAnalysis(
            source_url=document.url,
            final_url=document.final_url,
            kind=DocumentKind.IMAGE,
            metadata=DocumentMetadata(
                content_type=document.content_type,
                status_code=document.status_code,
                headers=document.headers,
            ),
            extracted_text=extracted_text,
            images=images,
            offers=offers,
            detected_prices=prices,
            warnings=warnings,
        )
