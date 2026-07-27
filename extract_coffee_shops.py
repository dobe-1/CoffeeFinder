import argparse

from backend.aggregator import aggregator


def main():
    parser = argparse.ArgumentParser(description="Extract coffee shops from a given city")
    parser.add_argument(
        "--file", type=str, help="Path to a text file containing city names (one per line)"
    )
    args = parser.parse_args()

    with open(args.file) as f:
        print(f"Reading cities from file: {args.file}")
        cities = [line.strip() for line in f if line.strip()]

    for city in cities:
        print(f"Extracting coffee shops for city: {city}")
        aggregator.get_coffee_shops(
            city
        )  # This should create a new file in the store directory for each city


if __name__ == "__main__":
    main()
