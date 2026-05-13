import time

import osmnx as ox
import pandas as pd
import pycountry
import requests
from geopandas import GeoDataFrame

#########################################################################
####### City retrieval logic ############################################
#########################################################################


def get_country_iso_code(country_name) -> str | None:
    try:
        country = pycountry.countries.get(name=country_name)
        if country:
            return country.alpha_2
        else:
            raise ValueError(f"Country '{country_name}' not found.")
    except Exception as e:
        print(f"Error: {e}")
        return None


def parse_population(population_str) -> int:
    try:
        population_str = population_str.replace(",", "")
        population_str = population_str.replace(".", "")
        return int(population_str)
    except ValueError:
        return 0


def get_cities_in_country(country_name="Germany") -> list:

    country_code = get_country_iso_code(country_name)
    if not country_code:
        return []

    query = f"""
    [out:json][timeout:90];
    area["ISO3166-1"="{country_code}"][admin_level=2]->.a;
    node
    ["place"~"city|town"]
    ["population"]
    (area.a);
    out tags;
    """

    response = requests.get(
        "https://overpass.kumi.systems/api/interpreter",
        data=query,
        headers={"User-Agent": "python-requests/2.31.0"},
    )
    data = response.json()

    cities = sorted(
        set(
            f"{element['tags']['name']}, {country_name}"
            for element in data["elements"]
            if (
                "name" in element["tags"]
                and "population" in element["tags"]
                and parse_population(element["tags"]["population"]) > 100000
            )
        )
    )
    return cities


##############################################################################
####### Cafe retrieval and filtering logic ###################################
##############################################################################


def get_cafes_in_city(city_name) -> GeoDataFrame:
    tags = {"amenity": "cafe"}
    cafes = ox.features_from_place(city_name, tags)
    return cafes


def safe_col(df: GeoDataFrame, col: str) -> pd.Series:
    return df.get(col, pd.Series(index=df.index, dtype="object"))


def has_any(df: GeoDataFrame, cols: list[str]) -> pd.Series:
    return pd.concat([safe_col(df, col).notnull() for col in cols], axis=1).any(axis=1)


def has_none(df: GeoDataFrame, cols: list[str]) -> pd.Series:
    return pd.concat([safe_col(df, col).isnull() for col in cols], axis=1).all(axis=1)


def filter_cafes_with_website(cafes: GeoDataFrame) -> GeoDataFrame:
    return cafes[
        has_any(
            cafes,
            [
                "website",
                "website:menu",
                "contact:website",
            ],
        )
    ]


def filter_cafes_without_website(cafes: GeoDataFrame) -> GeoDataFrame:
    return cafes[
        has_none(
            cafes,
            [
                "website",
                "website:menu",
                "contact:website",
            ],
        )
    ]


def filter_cafes_with_menu(cafes: GeoDataFrame) -> GeoDataFrame:
    return cafes[
        has_any(
            cafes,
            [
                "website:menu",
            ],
        )
    ]


def filter_cafes_without_website_with_social_media(
    cafes: GeoDataFrame,
) -> GeoDataFrame:
    cafes_without_website = filter_cafes_without_website(cafes)
    return cafes_without_website[
        has_any(
            cafes_without_website,
            [
                "contact:facebook",
                "contact:instagram",
            ],
        )
    ]


def filter_cafes_with_facebook(cafes: GeoDataFrame) -> GeoDataFrame:
    return cafes[
        has_any(
            cafes,
            [
                "contact:facebook",
            ],
        )
    ]


def filter_cafes_with_instagram(cafes: GeoDataFrame) -> GeoDataFrame:
    return cafes[
        has_any(
            cafes,
            [
                "contact:instagram",
            ],
        )
    ]


def get_information_about_cafes(city_name):
    cafes = get_cafes_in_city(city_name)
    cafes_with_website = filter_cafes_with_website(cafes)
    cafes_without_website = filter_cafes_without_website(cafes)
    cafes_with_menu = filter_cafes_with_menu(cafes)
    cafes_without_website_with_social_media = filter_cafes_without_website_with_social_media(
        cafes_without_website
    )
    cafes_without_website_with_facebook = filter_cafes_with_facebook(cafes_without_website)
    cafes_without_website_with_instagram = filter_cafes_with_instagram(cafes_without_website)

    print(f"Total cafes in {city_name}: {len(cafes)}")
    print(f"Cafes with website: {len(cafes_with_website)}")
    print(f"Cafes with menu: {len(cafes_with_menu)}")
    print(
        f"Cafes without website but with social media: {len(cafes_without_website_with_social_media)}"
    )
    print(f"Cafes without website but with Facebook: {len(cafes_without_website_with_facebook)}")
    print(f"Cafes without website but with Instagram: {len(cafes_without_website_with_instagram)}")

    return {
        "total": len(cafes),
        "with_website": len(cafes_with_website),
        "with_menu": len(cafes_with_menu),
        "without_website_with_social_media": len(cafes_without_website_with_social_media),
        "without_website_with_facebook": len(cafes_without_website_with_facebook),
        "without_website_with_instagram": len(cafes_without_website_with_instagram),
    }


def analyze_cafes():
    with open("cities_in_germany.txt") as f:
        cities = [line.strip() for line in f.readlines()]

    total_cafes = 0
    cafes_with_websites = 0
    cafes_with_menus = 0
    cafes_without_websites_with_social_media = 0
    cafes_without_websites_with_facebook = 0
    cafes_without_websites_with_instagram = 0
    for city in cities:
        print(f"Analyzing cafes in {city}...")
        info = get_information_about_cafes(city)
        total_cafes += info["total"]
        cafes_with_websites += info["with_website"]
        cafes_with_menus += info["with_menu"]
        cafes_without_websites_with_social_media += info["without_website_with_social_media"]
        cafes_without_websites_with_facebook += info["without_website_with_facebook"]
        cafes_without_websites_with_instagram += info["without_website_with_instagram"]
        time.sleep(1)  # To avoid overwhelming the API

    print(f"{cafes_with_websites / total_cafes:.2%} of cafes have websites.")
    print(f"{cafes_with_menus / total_cafes:.2%} of cafes have menus online.")
    print(
        f"{cafes_without_websites_with_social_media / total_cafes:.2%} of cafes without websites have social media presence."
    )


def save_cafes_to_csv(cafes: GeoDataFrame, filename) -> None:
    cafes.to_csv(
        filename,
        columns=[
            "name",
            "website",
            "website:menu",
            "contact:website",
            "contact:facebook",
            "contact:instagram",
            "contact:email",
        ],
        index=False,
    )


if __name__ == "__main__":
    # citites = get_cities_in_country("Germany")
    # with open("cities_in_germany.txt", "w") as f:
    #     for city in citites:
    #         f.write(f"{city}\n")

    city_name = "Bochum, Germany"
    cafes = get_cafes_in_city(city_name)
    cafes_with_website = filter_cafes_with_website(cafes)
    print(cafes_with_website[["name", "website"]])
    # get_information_about_cafes(city_name)
    # analyze_cafes()

    # save_cafes_to_csv(cafes_with_website, "cafes_with_websites.csv")
