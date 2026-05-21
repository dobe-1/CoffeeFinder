from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from hashlib import sha256
from typing import Any

from pydantic import BaseModel, Field, computed_field


class DocumentKind(str, Enum):
    HTML = "html"
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    BINARY = "binary"
    UNKNOWN = "unknown"


class PriceEvidence(BaseModel):
    label: str | None = None
    price_eur: float
    currency: str = "EUR"
    source_text: str
    source_url: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class ImageInfo(BaseModel):
    url: str
    alt_text: str | None = None
    width: int | None = None
    height: int | None = None
    format: str | None = None
    exif: dict[str, Any] = Field(default_factory=dict)
    ocr_text: str | None = None


class ExtractedOffer(BaseModel):
    category: str = "coffee"
    name: str
    price_eur: float | None = None
    currency: str = "EUR"
    size: str | None = None
    description: str | None = None
    evidence: list[PriceEvidence] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class DocumentMetadata(BaseModel):
    title: str | None = None
    description: str | None = None
    language: str | None = None
    content_type: str | None = None
    status_code: int | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    discovered_links: list[str] = Field(default_factory=list)


class DownloadedDocument(BaseModel):
    url: str
    final_url: str | None = None
    path_hint: str | None = None
    content_type: str | None = None
    status_code: int | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    content: bytes = Field(repr=False)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @computed_field
    @property
    def sha256(self) -> str:
        return sha256(self.content).hexdigest()

    @computed_field
    @property
    def size_bytes(self) -> int:
        return len(self.content)


class DocumentAnalysis(BaseModel):
    source_url: str
    final_url: str | None = None
    kind: DocumentKind = DocumentKind.UNKNOWN
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    extracted_text: str | None = None
    offers: list[ExtractedOffer] = Field(default_factory=list)
    images: list[ImageInfo] = Field(default_factory=list)
    detected_prices: list[PriceEvidence] = Field(default_factory=list)
    entities: dict[str, list[str]] = Field(default_factory=dict)
    raw_signals: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class CoffeeShopIdentity(BaseModel):
    source_id: str | None = None
    name: str
    city: str | None = None
    country: str | None = "DE"
    website: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class SourceSummary(BaseModel):
    url: str
    final_url: str | None = None
    kind: DocumentKind
    content_type: str | None = None
    title: str | None = None
    offers_found: int = 0
    images_found: int = 0
    warnings: list[str] = Field(default_factory=list)


class CoffeeShopRecord(BaseModel):
    identity: CoffeeShopIdentity
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    offers: list[ExtractedOffer] = Field(default_factory=list)
    media: list[ImageInfo] = Field(default_factory=list)
    sources: list[SourceSummary] = Field(default_factory=list)
    source_analyses: list[DocumentAnalysis] = Field(default_factory=list)
    signals: dict[str, Any] = Field(default_factory=dict)


class AnalysisRequest(BaseModel):
    shop: CoffeeShopIdentity
    documents: list[DownloadedDocument]
