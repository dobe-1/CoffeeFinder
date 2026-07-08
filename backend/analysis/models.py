from pydantic import BaseModel, Field

from backend.models.menu import Menu


class DocumentAnalysis(BaseModel):
    source_url: str | None = None
    content_type: str | None = None
    extracted_text: str | None = None
    menu: Menu = Field(default_factory=Menu)
    warnings: list[str] = Field(default_factory=list)
