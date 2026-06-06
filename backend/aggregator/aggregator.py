import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from backend.models import CoffeeShop
from backend.scraper.overpassAPI import get_coffee_shops_in_city
from backend.scraper.web_scraper import (
    extract_menu_url_from_coffee_shop,
    get_menu_urls_from_website,
)

# TODO function for comparing execution with test set
#   - load test set from file (coffee shops from city with correct menu links)
#   - execute get_coffe_shops
#   - check for each coffee shop: is correct menu from test in return list from get_coffe_shops
#   - return ratio

# TODO function to create test set
#   - specify city
#   - execute get_coffe_shops
#   - store to file
#


def get_menu_for_url(url: str) -> list:
    return get_menu_urls_from_website(url)


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
    # TODO fix logic to correctly extract menu if not cached
    for coffee_shop in coffee_shops:
        if (
            coffee_shop.website.url
            and coffee_shop.website.accessible
            and (
                not coffee_shop.menu.extracted_at
                or coffee_shop.menu.extracted_at <= datetime.now(tz=UTC) - timedelta(days=30)
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
