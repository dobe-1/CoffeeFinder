from __future__ import annotations

import re

from .models import ExtractedOffer, PriceEvidence

COFFEE_KEYWORDS = {
    "coffee",
    "kaffee",
    "espresso",
    "cappuccino",
    "latte",
    "americano",
    "flat white",
    "milchkaffee",
    "filterkaffee",
    "filter coffee",
    "cafe crema",
    "caffe crema",
    "macchiato",
    "mocha",
}

PRICE_RE = re.compile(
    r"(?:(?P<prefix>€|\$)\s?)?(?P<amount>\d{1,4}(?:[.,]\d{1,2})?)(?:\s?(?P<suffix>€|eur|usd))?",
    re.IGNORECASE,
)
LINE_SPLIT_RE = re.compile(r"[\r\n]+")


def normalize_price(value: str) -> float:
    return float(value.replace(",", "."))


def is_plausible_price(value: float) -> bool:
    return 0.5 <= value <= 100.0


def line_has_price_context(line: str) -> bool:
    return any(token in line.lower() for token in ("€", "$", "eur", "usd"))


def is_likely_coffee_item(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in COFFEE_KEYWORDS)


def is_likely_coffee_section(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in ("coffee", "kaffee", "espresso", "cappuccino", "latte"))


def build_price_evidence(
    amount: float,
    source_text: str,
    source_url: str,
    confidence: float,
    label: str | None = None,
) -> PriceEvidence:
    return PriceEvidence(
        label=label,
        price_eur=amount,
        source_text=source_text,
        source_url=source_url,
        confidence=confidence,
    )


def extract_offers_from_text(text: str, source_url: str, confidence: float) -> list[ExtractedOffer]:
    offers: list[ExtractedOffer] = []
    for raw_line in LINE_SPLIT_RE.split(text):
        line = " ".join(raw_line.split())
        if not line:
            continue

        if not is_likely_coffee_item(line):
            continue

        matches = list(PRICE_RE.finditer(line))
        if not matches:
            continue

        for match in matches:
            amount = normalize_price(match.group("amount"))
            if not is_plausible_price(amount):
                continue
            if not line_has_price_context(line) and "." not in match.group("amount") and "," not in match.group(
                "amount"
            ):
                continue
            name = raw_line[: match.start()].strip(" -:|") or raw_line.strip()
            evidence = build_price_evidence(
                amount=amount,
                source_text=line,
                source_url=source_url,
                confidence=confidence,
                label=name or None,
            )
            offers.append(
                ExtractedOffer(
                    name=name or raw_line.strip(),
                    price_eur=amount,
                    evidence=[evidence],
                    confidence=confidence,
                )
            )
    return deduplicate_offers(offers)


def extract_price_evidence(text: str, source_url: str, confidence: float) -> list[PriceEvidence]:
    evidence: list[PriceEvidence] = []
    for raw_line in LINE_SPLIT_RE.split(text):
        line = " ".join(raw_line.split())
        if not line:
            continue
        for match in PRICE_RE.finditer(line):
            amount = normalize_price(match.group("amount"))
            if not is_plausible_price(amount):
                continue
            evidence.append(
                build_price_evidence(
                    amount=amount,
                    source_text=line,
                    source_url=source_url,
                    confidence=confidence,
                )
            )
    return evidence


def extract_structured_offer(
    name: str,
    price_text: str,
    source_url: str,
    confidence: float,
    menu_context: str | None = None,
) -> ExtractedOffer | None:
    match = PRICE_RE.search(price_text)
    if match is None:
        return None

    amount = normalize_price(match.group("amount"))
    if not is_plausible_price(amount):
        return None

    clean_name = " ".join(name.split()).strip(" -:|")
    if not clean_name:
        return None
    if not is_likely_coffee_item(clean_name) and not (
        menu_context and is_likely_coffee_section(menu_context)
    ):
        return None

    evidence = build_price_evidence(
        amount=amount,
        source_text=f"{clean_name} {price_text}".strip(),
        source_url=source_url,
        confidence=confidence,
        label=clean_name,
    )
    return ExtractedOffer(
        name=clean_name,
        price_eur=amount,
        evidence=[evidence],
        confidence=confidence,
    )


def extract_multiple_structured_offers(
    name: str,
    price_text: str,
    source_url: str,
    confidence: float,
    menu_context: str | None = None,
) -> list[ExtractedOffer]:
    clean_name = " ".join(name.split()).strip(" -:|")
    if not clean_name:
        return []
    if not is_likely_coffee_item(clean_name) and not (
        menu_context and is_likely_coffee_section(menu_context)
    ):
        return []

    offers: list[ExtractedOffer] = []
    for match in PRICE_RE.finditer(price_text):
        amount = normalize_price(match.group("amount"))
        if not is_plausible_price(amount):
            continue
        evidence = build_price_evidence(
            amount=amount,
            source_text=f"{clean_name} {price_text}".strip(),
            source_url=source_url,
            confidence=confidence,
            label=clean_name,
        )
        offers.append(
            ExtractedOffer(
                name=clean_name,
                price_eur=amount,
                evidence=[evidence],
                confidence=confidence,
            )
        )
    return deduplicate_offers(offers)


def deduplicate_offers(offers: list[ExtractedOffer]) -> list[ExtractedOffer]:
    seen: set[tuple[str, float | None]] = set()
    deduplicated: list[ExtractedOffer] = []
    for offer in offers:
        key = (offer.name.lower(), offer.price_eur)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(offer)
    return deduplicated
