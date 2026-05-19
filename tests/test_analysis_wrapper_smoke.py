from __future__ import annotations

import json
import mimetypes
import os
from pathlib import Path
import shutil

from analysis.component import AnalyzerComponent, default_document_downloader
from analysis.models import DownloadedDocument
import pytest
import requests


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "analyzer"
MANIFEST_PATH = FIXTURES_DIR / "manifest.json"
DEBUG_OUTPUT_ENABLED = os.getenv("ANALYZER_DEBUG_JSON", "").lower() in {"1", "true", "yes", "on"}


def load_manifest_cases() -> list[dict]:
    manifest = json.loads(MANIFEST_PATH.read_text())
    return manifest["cases"]


def load_expected(case: dict) -> dict:
    return json.loads((FIXTURES_DIR / case["expected_fixture"]).read_text())


def fixture_downloader_factory(case: dict):
    cafe = case["cafe"]
    expected = load_expected(case)
    fixture_url = cafe["menu_url"] or expected["menu"]["source_url"]
    fixture_name = case.get("document_fixture")

    if not fixture_name:
        return default_document_downloader

    def fixture_downloader(url: str) -> DownloadedDocument:
        if url != fixture_url:
            raise KeyError(url)

        fixture_path = FIXTURES_DIR / fixture_name
        content = fixture_path.read_bytes()
        content_type, _encoding = mimetypes.guess_type(fixture_path.name)
        return DownloadedDocument(
            url=url,
            final_url=url,
            content_type=content_type or "application/octet-stream",
            content=content,
        )

    return fixture_downloader


@pytest.mark.parametrize("case", load_manifest_cases(), ids=lambda case: case["id"])
def test_component_enriches_manifest_cafe_object(case: dict) -> None:
    component = AnalyzerComponent(downloader=fixture_downloader_factory(case))
    expected = load_expected(case)
    cafe = case["cafe"]
    analysis_url = cafe["menu_url"] or expected["menu"]["source_url"]


    try:
        enriched = component.analyze_cafe(cafe, menu_url_override=analysis_url)
    except requests.RequestException as exc:
        pytest.skip(f"Live download unavailable for {analysis_url}: {exc}")

    if DEBUG_OUTPUT_ENABLED:
        print(json.dumps(enriched, indent=2, ensure_ascii=False))

    assert enriched["name"] == expected["name"]
    assert enriched["coordinates"] == expected["coordinates"]
    assert enriched["category"] == expected["category"]
    assert enriched["website_url"] == expected["website_url"]
    assert enriched["menu_url"] == expected["menu_url"]
    assert enriched["menu"]["currency"] == expected["menu"]["currency"]
    assert expected["menu"]["source_url"] in enriched["menu"]["source_urls"]

    offers = {(offer["name"], offer["price"]) for offer in enriched["menu"]["offers"]}
    for expected_offer in expected["menu"]["offers"]:
        assert (expected_offer["name"], expected_offer["price"]) in offers
