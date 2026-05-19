from __future__ import annotations

from analysis.aggregate import aggregate_shop
from analysis.detector import detect_kind
from analysis.models import AnalysisRequest, CoffeeShopIdentity, CoffeeShopRecord, DownloadedDocument
from analysis.registry import AnalyzerRegistry


class AnalyzerService:
    def __init__(self, registry: AnalyzerRegistry | None = None) -> None:
        self.registry = registry or AnalyzerRegistry()

    def analyze(self, request: AnalysisRequest) -> CoffeeShopRecord:
        analyses = []
        for document in request.documents:
            kind = detect_kind(document)
            analyzer = self.registry.get(kind)
            analyses.append(analyzer.analyze(document))
        return aggregate_shop(request.shop, analyses)

    def analyze_downloaded_documents(
        self,
        identity: CoffeeShopIdentity,
        documents: list[DownloadedDocument],
    ) -> CoffeeShopRecord:
        return self.analyze(AnalysisRequest(shop=identity, documents=documents))
