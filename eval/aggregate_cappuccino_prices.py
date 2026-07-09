import json
from pathlib import Path
from statistics import fmean


BASE_DIR = Path(__file__).resolve().parents[1]
CITY_LIST_PATH = BASE_DIR / "cities_in_germany.txt"
STORE_DIR = BASE_DIR / "store"
OUTPUT_PATH = Path(__file__).with_name("cappuccino_price_aggregates.json")

CAPPUCCINO_NAMES = {"cappuccino"}
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


def shop_cappuccino_price(shop: dict) -> float | None:
    for item in shop.get("menu", {}).get("items", []):
        price = item.get("price")
        if is_cappuccino_item(item.get("name")) and is_plausible_price(price):
            return float(price)
    return None


def city_cappuccino_prices() -> dict[str, list[float]]:
    prices_by_city: dict[str, list[float]] = {}

    for city, path in city_data_files().items():
        shops = json.loads(path.read_text(encoding="utf-8"))
        shop_prices = [
            price
            for shop in shops
            if (price := shop_cappuccino_price(shop)) is not None
        ]
        prices_by_city[city] = shop_prices

    return prices_by_city


def build_aggregates() -> dict[str, dict[str, object]]:
    prices_by_city = city_cappuccino_prices()
    aggregates = {}

    for city_info in read_city_list(CITY_LIST_PATH):
        city = str(city_info["city"])
        shop_prices = prices_by_city.get(city, [])
        aggregates[city] = {
            "coordinates": [city_info["lat"], city_info["lon"]],
            "sample_size": len(shop_prices),
            "aggregated_value": round(fmean(shop_prices), 2) if shop_prices else None,
        }

    return aggregates


def main() -> None:
    aggregates = build_aggregates()
    OUTPUT_PATH.write_text(
        json.dumps(aggregates, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    cities_with_prices = sum(
        1 for city in aggregates.values() if city["aggregated_value"] is not None
    )
    total_samples = sum(int(city["sample_size"]) for city in aggregates.values())
    print(f"Wrote aggregates for {len(aggregates)} cities to {OUTPUT_PATH}.")
    print(f"Cities with extracted cappuccino prices: {cities_with_prices}")
    print(f"Coffee-shop samples used: {total_samples}")


if __name__ == "__main__":
    main()
