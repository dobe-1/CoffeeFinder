import csv
import json
from pathlib import Path
from statistics import fmean

from backend.models.aggregation import AggregationResult
from backend.models.coffee_shop import CoffeeShop

CITY_LIST_PATH = Path("cities_in_germany.txt")
STORE_DIR = Path("store")
OUTPUT_PATH = STORE_DIR / "aggregates.json"
CORRELATION_DATA_PATH = Path("Grossstädte-Korrelation.csv")

INCOME_COLUMN = "Verfügbares Einkommen pro Person in Euro"
OVERNIGHT_STAYS_COLUMN = "Übernachtungen je EW"

MIN_PLAUSIBLE_PRICE = 2
MAX_PLAUSIBLE_PRICE = 6.5


def read_city_list(path: Path) -> list[dict[str, str | float | None]]:
    cities = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        parts = [part.strip() for part in line.split(",")]
        lat = None
        lon = None
        if len(parts) >= 4:
            lat = float(parts[2])
            lon = float(parts[3])

        cities.append(
            {
                "city": parts[0],
                "country": parts[1] if len(parts) > 1 else "",
                "lat": lat,
                "lon": lon,
            }
        )
    return cities


def parse_number(value: str) -> float | None:
    # CSV uses German formatting: thousands separated by spaces, decimal comma.
    cleaned = value.strip().replace(" ", "").replace(",", ".")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_city_name(city: str) -> str:
    # Strip any parenthetical suffix, e.g. "Frankfurt (Main)" -> "Frankfurt".
    return city.split(" (", 1)[0].strip()


def load_correlation_data() -> dict[str, dict[str, float | None]]:
    if not CORRELATION_DATA_PATH.exists():
        print(f"Warning: {CORRELATION_DATA_PATH} not found, skipping correlation data.")
        return {}

    with CORRELATION_DATA_PATH.open(encoding="utf-8", newline="") as file:
        return {
            normalize_city_name(row["Stadt"]): {
                "disposable_income_per_person": parse_number(row.get(INCOME_COLUMN, "")),
                "overnight_stays_per_inhabitant": parse_number(row.get(OVERNIGHT_STAYS_COLUMN, "")),
            }
            for row in csv.DictReader(file)
        }


def city_name_from_data_file(path: Path) -> str:
    return path.stem.removesuffix("_Germany").replace("_", " ")


def city_data_files() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for path in STORE_DIR.glob("*_Germany.json"):
        paths[city_name_from_data_file(path)] = path
    return paths


def is_cappuccino_item(name: object) -> bool:
    if not isinstance(name, str):
        return False
    return name.strip().casefold() in CAPPUCCINO_NAMES


def is_plausible_price(price: object) -> bool:
    return (
        isinstance(price, int | float)
        and MIN_PLAUSIBLE_PRICE <= float(price) <= MAX_PLAUSIBLE_PRICE
    )


def shop_cappuccino_price(shop: CoffeeShop) -> float | None:
    price_sum = 0
    item_count = 0
    for item in shop.menu.items:
        price = item.price
        if not is_plausible_price(price):
            continue
        item_count += 1
        price_sum += float(price)
    return price_sum / item_count if item_count > 0 else None


def city_cappuccino_prices() -> dict[str, list[float]]:
    prices_by_city: dict[str, list[float]] = {}

    for city, path in city_data_files().items():
        shops = [
            CoffeeShop.model_validate(shop) for shop in json.loads(path.read_text(encoding="utf-8"))
        ]
        shop_prices = [
            price for shop in shops if (price := shop_cappuccino_price(shop)) is not None
        ]
        prices_by_city[city] = shop_prices

    return prices_by_city


def extract_city_metadata():
    total_shops = 0
    shops_with_website = 0
    shops_with_menu = 0

    city_metadata = {}
    for city, path in city_data_files().items():
        shops = [
            CoffeeShop.model_validate(shop) for shop in json.loads(path.read_text(encoding="utf-8"))
        ]
        city_metadata[city] = {
            "total_shops": len(shops),
            "shops_with_website": sum(1 for shop in shops if shop.website.url),
            "shops_with_possible_menu": sum(
                1 for shop in shops if shop.menu.menu_url and shop.menu.menu_url_accessible
            ),
        }
        total_shops += city_metadata[city]["total_shops"]
        shops_with_website += city_metadata[city]["shops_with_website"]
        shops_with_menu += city_metadata[city]["shops_with_possible_menu"]

    print(f"Total shops: {total_shops}")
    print(
        f"Shops with website: {shops_with_website} ({(shops_with_website / total_shops * 100):.2f}%)"
    )
    print(
        f"Shops with possible menu: {shops_with_menu} ({(shops_with_menu / total_shops * 100):.2f}%)"
    )

    return city_metadata


def build_aggregates() -> dict[str, AggregationResult]:
    prices_by_city = city_cappuccino_prices()
    city_metadata = extract_city_metadata()
    correlation_data = load_correlation_data()
    aggregates = {}

    for city_info in read_city_list(CITY_LIST_PATH):
        city = str(city_info["city"])
        shop_prices = prices_by_city.get(city, [])
        correlation = correlation_data.get(normalize_city_name(city), {})
        aggregates[city] = AggregationResult(
            coordinates=(city_info["lat"], city_info["lon"]),
            sample_size=len(shop_prices),
            aggregated_value=round(fmean(shop_prices), 2) if shop_prices else None,
            total_shops=city_metadata.get(city, {}).get("total_shops", 0),
            shops_with_website=city_metadata.get(city, {}).get("shops_with_website", 0),
            shops_with_possible_menu=city_metadata.get(city, {}).get("shops_with_possible_menu", 0),
            disposable_income_per_person=correlation.get("disposable_income_per_person"),
            overnight_stays_per_inhabitant=correlation.get("overnight_stays_per_inhabitant"),
        )

    return aggregates


def main() -> None:
    aggregates = build_aggregates()
    serializable = {city: result.model_dump() for city, result in aggregates.items()}
    OUTPUT_PATH.write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    cities_with_prices = sum(
        1 for result in aggregates.values() if result.aggregated_value is not None
    )
    total_samples = sum(result.sample_size for result in aggregates.values())
    print(f"Wrote aggregates for {len(aggregates)} cities to {OUTPUT_PATH}.")
    print(f"Cities with extracted cappuccino prices: {cities_with_prices}")
    print(f"Coffee-shop samples used: {total_samples}")


if __name__ == "__main__":
    main()
