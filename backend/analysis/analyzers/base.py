from backend.analysis.models import DocumentAnalysis


class BaseAnalyzer:
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
                f"No analyzer available for {source_url or 'unknown source'} with content type {content_type}."
            ],
        )
