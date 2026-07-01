import json
import os
import shutil
from pathlib import Path

import pytest

from backend.analysis import Analyzer
from backend.models import CoffeeShop, Menu, Website

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "analyzer"
MANIFEST_PATH = FIXTURES_DIR / "manifest.json"
DEBUG_OUTPUT_ENABLED = os.getenv("ANALYZER_DEBUG_JSON", "").lower() in {"1", "true", "yes", "on"}


def load_manifest_cases() -> list[dict]:
    return json.loads(MANIFEST_PATH.read_text())["cases"]


def load_expected(case: dict) -> dict:
    return json.loads((FIXTURES_DIR / case["expected_fixture"]).read_text())


def coffee_shop_from_case(case: dict, expected: dict) -> CoffeeShop:
    cafe = case["cafe"]
    return CoffeeShop(
        name=cafe["name"],
        coordinates=tuple(cafe["coordinates"]),
        category=cafe["category"],
        website=Website(url=cafe.get("website_url")),
        menu=Menu(menu_url=cafe.get("menu_url") or expected["menu"]["source_url"]),
    )


@pytest.mark.parametrize("case", load_manifest_cases(), ids=lambda case: case["id"])
def test_component_updates_coffee_shop_model(case: dict) -> None:
    expected = load_expected(case)
    coffee_shop = coffee_shop_from_case(case, expected)
    fixture_name = case["document_fixture"]
    content_type = case["content_type"]

    if Path(fixture_name).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        pytest.importorskip("PIL")
        pytest.importorskip("pytesseract")
        if shutil.which("tesseract") is None:
            pytest.skip("Native tesseract binary is not installed.")

    data = (FIXTURES_DIR / fixture_name).read_bytes()
    result = Analyzer().analyze(coffee_shop, data=data, content_type=content_type)

    if DEBUG_OUTPUT_ENABLED:
        print(result.model_dump_json(indent=2))

    assert result is coffee_shop
    assert coffee_shop.name == expected["name"]
    assert list(coffee_shop.coordinates) == expected["coordinates"]
    assert coffee_shop.category == expected["category"]
    assert coffee_shop.website.url == expected["website_url"]
    assert coffee_shop.menu.currency == expected["menu"]["currency"]
    assert coffee_shop.menu.extracted_at is not None
    
    items = {(item.name, item.price) for item in coffee_shop.menu.items}
    if DEBUG_OUTPUT_ENABLED:
        print(coffee_shop.menu.items)
    for expected_offer in expected["menu"]["offers"]:
        assert (expected_offer["name"], expected_offer["price"]) in items
