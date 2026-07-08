import re

from backend.models.menu import MenuItem

COFFEE_KEYWORDS = (
    "americano",
    "cafe crema",
    "caffe crema",
    "cappuccino",
    "coffee",
    "espresso",
    "flat white",
    "kaffee",
    "latte",
    "macchiato",
    "milchkaffee",
    "mocha",
)
COFFEE_KEYWORD_PATTERNS = tuple(
    re.compile(r"(?<!\w)" + re.escape(keyword).replace(r"\ ", r"\s+") + r"(?!\w)", re.I)
    for keyword in COFFEE_KEYWORDS
)

PRICE_RE = re.compile(
    r"(?P<name>.+?)\s+(?:€|eur)?\s*(?P<price>\d{1,2}(?:[,.]\d{1,2})?)\s*(?:€|eur)?(?=\s|$)",
    re.I,
)
PRICE_ONLY_RE = re.compile(r"^(?:€|eur)?\s*(?P<price>\d{1,2}(?:[,.]\d{1,2})?)\s*(?:€|eur)?$", re.I)
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
NAME_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def is_coffee_text(text: str) -> bool:
    return any(pattern.search(text) for pattern in COFFEE_KEYWORD_PATTERNS)


def normalize_menu_item_name(name: str) -> str:
    cleaned = " ".join(name.split()).strip(" -:|")
    return NAME_WORD_RE.sub(lambda match: match.group(0).capitalize(), cleaned)


def extract_menu_items_from_text(text: str) -> list[MenuItem]:
    items: list[MenuItem] = []
    seen: set[tuple[str, float]] = set()
    pending_name = ""

    normalized_text = TAG_RE.sub("\n", text)
    for line in normalized_text.splitlines():
        line = " ".join(line.split()).strip(" -:|")
        if not line or not is_coffee_text(line):
            price_match = PRICE_ONLY_RE.search(line)
            if price_match is not None and pending_name:
                name = normalize_menu_item_name(pending_name)
                price = float(price_match.group("price").replace(",", "."))
                if name and 0.5 <= price <= 30:
                    key = (name.lower(), price)
                    if key not in seen:
                        seen.add(key)
                        items.append(MenuItem(name=name, price=price))
                pending_name = ""
            continue

        match = PRICE_RE.search(line)
        if match is None:
            pending_name = line
            continue

        name = normalize_menu_item_name(match.group("name"))
        price = float(match.group("price").replace(",", "."))
        if not name or not 0.5 <= price <= 30:
            continue

        key = (name.lower(), price)
        if key in seen:
            continue

        seen.add(key)
        items.append(MenuItem(name=name, price=price))

    return items


def deduplicate_menu_items(items: list[MenuItem]) -> list[MenuItem]:
    seen: set[tuple[str, float]] = set()
    result: list[MenuItem] = []
    for item in items:
        key = (item.name.lower(), item.price)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
