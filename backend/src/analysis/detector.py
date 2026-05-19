from __future__ import annotations

from pathlib import PurePosixPath

from .models import DocumentKind, DownloadedDocument

try:
    import magic
except ImportError:  # pragma: no cover
    magic = None


def detect_kind(document: DownloadedDocument) -> DocumentKind:
    content_type = (document.content_type or document.headers.get("content-type", "")).lower()
    url_path = PurePosixPath((document.final_url or document.url).split("?", 1)[0]).suffix.lower()

    if "html" in content_type or url_path in {".html", ".htm"}:
        return DocumentKind.HTML
    if "pdf" in content_type or url_path == ".pdf":
        return DocumentKind.PDF
    if content_type.startswith("image/") or url_path in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return DocumentKind.IMAGE
    if "json" in content_type or url_path == ".json":
        return DocumentKind.JSON
    if "xml" in content_type or url_path in {".xml", ".svg"}:
        return DocumentKind.XML
    if content_type.startswith("text/") or url_path in {".txt", ".csv"}:
        return DocumentKind.TEXT

    if magic is not None:
        mime_type = magic.from_buffer(document.content[:4096], mime=True)
        if mime_type == "application/pdf":
            return DocumentKind.PDF
        if mime_type.startswith("image/"):
            return DocumentKind.IMAGE
        if mime_type.startswith("text/html"):
            return DocumentKind.HTML
        if mime_type.startswith("text/"):
            return DocumentKind.TEXT

    if document.content.lstrip().startswith(b"<html"):
        return DocumentKind.HTML
    return DocumentKind.BINARY
