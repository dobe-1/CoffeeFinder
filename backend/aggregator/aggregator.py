import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from backend.models import CoffeeShop
from backend.scraper.overpassAPI import get_coffee_shops_in_city
from backend.scraper.web_scraper import (
    extract_menu_url_from_coffee_shop,
    get_menu_urls_from_website,
)


# run get_coffee_shops() for acity and save results to file for test set creation
def create_test_set(city: str) -> Path:
    coffee_shops = get_coffee_shops(city)
    test_file = Path("test_sets") / f"{city.replace(', ', '_')}.json"
    test_file.parent.mkdir(exist_ok=True)

    data = json.dumps(
        [shop.model_dump(mode="json") for shop in coffee_shops],
        indent=2,
        ensure_ascii=False,
    )
    with test_file.open("w") as f:
        f.write(data)
    return test_file


def evaluate_test_set(city: str) -> dict:
    # read test set
    test_file = Path("test_sets") / f"{city.replace(', ', '_')}.json"
    if not test_file.exists():
        raise FileNotFoundError(f"No test set found for {city}.")

    with test_file.open() as f:
        test_set_shops = [CoffeeShop.model_validate(shop) for shop in json.load(f)]

    # on urls of test set:
    # keep track of hits and misses
    correct = 0
    wrong = 0
    for shop in test_set_shops:
        actual_menu_url = shop.menu.menu_url
        # check if actual menu url in set
        if actual_menu_url:
            # run get_menu_urls_from_website for every menu (where a correct menu url exists)
            scraped_menu_urls = get_menu_urls_from_website(shop.website.url)
            if actual_menu_url in scraped_menu_urls:
                correct += 1
            else:
                wrong += 1

    ratio = correct / (correct + wrong) if (correct + wrong) > 0 else 0.0
    return {"total": (correct + wrong), "matched": correct, "missed": wrong, "ratio": ratio}


def get_menu_for_url(url: str) -> list:
    return get_menu_urls_from_website(url)


def extract_menu_for_shop(city: str, website_url: str) -> CoffeeShop:
    """Trigger menu-url extraction for a single cached coffee shop.

    The shop is identified by its (unique) website url within the city's cache.
    The extracted result is written back to the cache so it stays persistent.
    """
    cache_file = Path(f"store/{city.replace(', ', '_')}.json")
    if not cache_file.exists():
        raise FileNotFoundError(f"No cached coffee shops found for {city}.")

    with cache_file.open() as f:
        coffee_shops = [CoffeeShop.model_validate(shop) for shop in json.load(f)]

    target = next((shop for shop in coffee_shops if shop.website.url == website_url), None)
    if target is None:
        raise ValueError(f"No coffee shop with website {website_url} found in {city}.")

    extract_menu_url_from_coffee_shop(target)

    data = json.dumps(
        [shop.model_dump(mode="json") for shop in coffee_shops],
        indent=2,
        ensure_ascii=False,
    )
    cache_file.parent.mkdir(exist_ok=True)
    with cache_file.open("w") as f:
        f.write(data)

    return target


def get_available_cities() -> list[str]:
    # List cities for which we have cached coffee shops in the store directory
    store_dir = Path("store")
    if not store_dir.exists():
        return []

    cities = [path.stem.replace("_", ", ") for path in store_dir.glob("*.json")]
    return sorted(cities)


def get_coffee_shops(city: str) -> list[CoffeeShop]:
    # Check if we have a cached version of the coffee shops for the city
    cache_file = Path(f"store/{city.replace(', ', '_')}.json")
    if not cache_file.exists():
        # If we don't have a valid cache, fetch the coffee shops from the API
        coffee_shops = get_coffee_shops_in_city(city)
    else:
        # If we have a valid cache, load the coffee shops from the cache file
        with cache_file.open() as f:
            coffee_shops = [CoffeeShop.model_validate(coffee_shop) for coffee_shop in json.load(f)]

        return coffee_shops

    # Extract menu for shops that have a website and were not recently cached
    start_time = datetime.now(tz=UTC)
    for i, coffee_shop in enumerate(coffee_shops):
        if i % 10 == 0:
            print("------------------------------------------------")
            print(f"{i + 1}/{len(coffee_shops)} coffee shops processed.")
            time_in_progress = datetime.now(tz=UTC) - start_time
            print(f"Time in progress: {time_in_progress}")
            print(f"Average time per coffee shop: {time_in_progress / (i + 1)}")
            print(
                f"Estimated time remaining: {(time_in_progress * (len(coffee_shops) - i - 1)) / (i + 1)}"
            )
            print("------------------------------------------------")

        if (
            coffee_shop.website.url
            and coffee_shop.website.accessible is not False
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
