from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from scraper.overpassAPI import filter_cafes_with_website, get_cafes_in_city


def build_cafe_payload(city_name: str) -> dict:
    cafes = get_cafes_in_city(city_name)
    cafes_with_website = filter_cafes_with_website(cafes)

    result = {"cafes": []}
    for _, cafe in cafes_with_website.iterrows():
        name = cafe.get("name")
        geometry = cafe.get("geometry")
        if pd.isna(name) or geometry is None:
            continue

        # OSM cafes can be mapped as points or polygons; use the centroid for area geometries.
        point = geometry if hasattr(geometry, "x") and hasattr(geometry, "y") else geometry.centroid

        website_url = None
        for key in ("website", "contact:website"):
            value = cafe.get(key)
            if pd.notna(value):
                website_url = str(value).strip()
                break

        menu_url = None
        menu_value = cafe.get("website:menu")
        if pd.notna(menu_value):
            menu_url = str(menu_value).strip()

        result["cafes"].append(
            {
                "name": str(name),
                "coordinates": [float(point.y), float(point.x)],
                "category": "Cafe",
                "website_url": website_url,
                "menu_url": menu_url,
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Export cafes with websites to JSON.")
    parser.add_argument("--city", required=True, help='City name, e.g. "Bochum, Germany"')
    parser.add_argument("--output", help="Optional output file. If omitted, JSON is printed.")
    args = parser.parse_args()

    payload = build_cafe_payload(args.city)
    output = json.dumps(payload, indent=2, ensure_ascii=False)

    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output)
        print(f"saved {destination}")
        return

    print(output)


if __name__ == "__main__":
    main()
