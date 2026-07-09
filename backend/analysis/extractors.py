import re

from backend.models.menu import MenuItem

COFFEE_KEYWORDS = (
    "Cappuccino",
    "Capuccino",
    "Cappucino",
    "Capucino",
    "Capuchino",
    "Cappuchino",
    "Capucchino",
    "Cappucchino",
)
COFFEE_KEYWORD_PATTERNS = tuple(
    (
        keyword,
        re.compile(r"(?<![\w-])" + re.escape(keyword).replace(r"\ ", r"\s+") + r"\d*(?!\w)", re.I),
    )
    for keyword in sorted(COFFEE_KEYWORDS, key=len, reverse=True)
)

PRICE_RE = re.compile(
    r"(?P<name>.*?)(?:[\s\.\-]+)(?:€|eur)?\s*(?P<price>\d{1,2}(?:[,.]\d{1,2})?)(?:\s*(?:€|eur))?(?!\s*[,.]\s*\d)",
    re.I,
)
PRICE_ONLY_RE = re.compile(
    r"^(?:€|eur)?\s*(?P<price>\d{1,2}(?:[,.]\d{1,2})?)\s*(?:€|eur)?[^\w]*$", 
    re.I
)
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")


def is_coffee_text(text: str) -> bool:
    return matched_coffee_keyword(text) is not None


def matched_coffee_keyword(text: str) -> str | None:
    for keyword, pattern in COFFEE_KEYWORD_PATTERNS:
        if pattern.search(text):
            return keyword
    return None


def extract_menu_items_from_text(text: str) -> list[MenuItem]:
    items: list[MenuItem] = []
    seen: set[tuple[str, float]] = set()
    pending_name = ""

    normalized_text = TAG_RE.sub("\n", text)
    for line in normalized_text.splitlines():
        line = " ".join(line.split()).strip(" -:|")
        if not line:
            continue
        price_match = PRICE_ONLY_RE.search(line)
        if price_match is not None:
            if pending_name:
                name = matched_coffee_keyword(pending_name)
                price = float(price_match.group("price").replace(",", "."))
                if name and 2 <= price <= 7:
                    raw_name = pending_name.strip(" -.,|")
                    key = (raw_name.lower(), price)
                    if key not in seen:
                        seen.add(key)
                        items.append(MenuItem(name=raw_name, price=price))
            pending_name = ""
            continue

        matches = list(PRICE_RE.finditer(line))

        if not matches:
            if is_coffee_text(line):
                pending_name = line
            continue
        for match in matches:
            raw_name = match.group("name").strip(" -.,|")
            name = matched_coffee_keyword(raw_name)
            if name:
                extra_text = match.group("name").lower().replace(name.lower(), "")
                clean_words = re.sub(r"[^\w\s]", "", extra_text).split()

                words_only = [w for w in clean_words if not w.isdigit()]
                
                if len(words_only) > 1:
                    pending_name = name
                    continue
                    
            if not name and pending_name:
                words_only = [w for w in re.sub(r"[^\w\s]", "", raw_name).split() if not w.isdigit()]
                if len(words_only) > 1:
                    pending_name = ""
                    continue
                    
                raw_name = f"{pending_name} {raw_name}".strip() if raw_name else pending_name
                name = matched_coffee_keyword(pending_name)
                

            raw_price = match.group("price")
            has_euro = "€" in match.group(0) or "eur" in match.group(0).lower()
            
            if not has_euro and not raw_price.endswith(("0", "5")):
                if name:
                    pending_name = raw_name
                continue

            price = float(raw_price.replace(",", "."))

            if not name or not 2 <= price <= 7:
                continue

            key = (raw_name.lower(), price) 
            if key in seen:
                continue

            seen.add(key)
            items.append(MenuItem(name=raw_name, price=price))
            pending_name = ""
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
