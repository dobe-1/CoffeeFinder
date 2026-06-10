import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from backend.models import CoffeeShop
from backend.scraper.overpassAPI import get_coffee_shops_in_city
from backend.scraper.web_scraper import extract_menu_url_from_coffee_shop


def get_coffee_shops(city: str) -> list[CoffeeShop]:
    # Check if we have a cached version of the coffee shops for the city
    cache_file = Path(f"cache/{city.replace(', ', '_')}.json")
    if not cache_file.exists():
        # If we don't have a valid cache, fetch the coffee shops from the API
        coffee_shops = get_coffee_shops_in_city(city)
    else:
        # If we have a valid cache, load the coffee shops from the cache file
        with cache_file.open() as f:
            coffee_shops = [CoffeeShop.model_validate(coffee_shop) for coffee_shop in json.load(f)]

    # Check if the coffee shops have price information
    for coffee_shop in coffee_shops:
        if (
            coffee_shop.website.url
            and coffee_shop.website.accessible != False
            and not coffee_shop.menu.extracted_at
            or (
                coffee_shop.menu.extracted_at
                and coffee_shop.menu.extracted_at <= datetime.now(tz=UTC) - timedelta(days=30)
            )
        ):
            extract_menu_url_from_coffee_shop(coffee_shop)

    data = json.dumps(
        [coffee_shop.model_dump(mode="json") for coffee_shop in coffee_shops],
        indent=2,
        ensure_ascii=False,
    )

    cache_file.parent.mkdir(exist_ok=True)
    with cache_file.open("w") as f:
        f.write(data)
    return coffee_shops
