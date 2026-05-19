from __future__ import annotations

from abc import ABC, abstractmethod

from analysis.models import DocumentAnalysis, DownloadedDocument


class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, document: DownloadedDocument) -> DocumentAnalysis:
        raise NotImplementedError
