import argparse
import json
from pathlib import Path

from backend.scraper.overpassAPI import get_coffee_shops_in_city
from backend.scraper.web_scraper import extract_menu_url_from_coffee_shop


def main() -> None:
    parser = argparse.ArgumentParser(description="Export cafes with websites to JSON.")
    parser.add_argument("--city", required=True, help='City name, e.g. "Bochum, Germany"')
    parser.add_argument("--output", help="Optional output file. If omitted, JSON is printed.")
    args = parser.parse_args()

    coffee_shops = get_coffee_shops_in_city(args.city)

    for coffee_shop in coffee_shops:
        extract_menu_url_from_coffee_shop(coffee_shop)

    output = json.dumps(
        [coffee_shop.model_dump(mode="json") for coffee_shop in coffee_shops],
        indent=2,
        ensure_ascii=False,
    )

    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output)
        print(f"saved {destination}")
        return

    print(output)


if __name__ == "__main__":
    main()
