import re

import pandas as pd
from geopandas import GeoDataFrame
from overpassAPI import filter_cafes_with_website, get_cafes_in_city
from playwright.sync_api import sync_playwright

MENU_PATTERN = re.compile(
    r"(speisekarten?|men(?:ü|ue|u)s?|essen|getr(?:ä|ae|a)nke|drinks?|food)",
    re.IGNORECASE,
)


def validate_url(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://") and not url.startswith("/"):
        raise ValueError(
            "URL must start with http:// or https:// or be a relative path starting with /"
        )
    return url


def is_menu_link(text: str | None, href: str | None) -> bool:
    if text and MENU_PATTERN.search(text):
        return True
    if href and MENU_PATTERN.search(href):
        return True
    return False


def get_menu_urls_from_website(url) -> list:
    with sync_playwright() as p:
        config = {
            "accept_downloads": False,  # do not download stuff
            "locale": "de-DE",  # emulate us english language settings
            "screen": {"width": 1920, "height": 1080},  # emulate full hd screen
            "viewport": {"width": 1920, "height": 1080},  # emulate full hd viewport
            "headless": True,  # set true to not show browser window (invisible); set false to show browser window (visible)
            # TODO: set navigator.webdriver to false to bypass bot detection
        }
        browser = p.chromium
        context = browser.launch_persistent_context("", **config)

        page = context.new_page()
        page.add_init_script("""
        navigator.webdriver = false
        Object.defineProperty(navigator, 'webdriver', {
        get: () => false
        })
        """)

        try:
            page.goto(url)
        except Exception as e:
            print(f"Error navigating to {url}: {e}")
            context.close()
            return []
        frame = page.frames[0]
        locators = frame.locator("a")

        menu_urls = []

        for i in range(locators.count()):
            locator = locators.nth(i)
            href = locator.get_attribute("href")
            if not href:
                continue

            if is_menu_link(locator.inner_text(), href):
                try:
                    validated_url = validate_url(href)
                    if validated_url not in menu_urls:
                        menu_urls.append(validated_url)
                        print(f"Found menu URL: {validated_url}")

                except ValueError:
                    continue

        page.close()
        context.close()
        return menu_urls


def analyze_cafes(cafes: GeoDataFrame):
    menu_url_found = 0

    for index, cafe in cafes.iterrows():
        menu_url = cafe.get("website:menu")
        if pd.notna(menu_url):
            menu_url_found += 1
            print(f"Cafe: {cafe['name']}, Menu URL: {cafe['website:menu']}")
            continue

        cafe_website = cafe.get("website")
        contact_website = cafe.get("contact:website")

        if pd.notna(cafe_website):
            cafe_website = cafe_website.strip()
        elif pd.notna(contact_website):
            cafe_website = contact_website.strip()
        else:
            print(f"No website found for cafe: {cafe['name']}")
            continue

        if cafe_website:
            print(f"Analyzing website for cafe: {cafe['name']} at {cafe_website}")
            menu_urls = get_menu_urls_from_website(cafe_website)
            if menu_urls:
                print(f"Menu URLs found for cafe '{cafe['name']}': {menu_urls}")
                menu_url_found += 1
                continue
            else:
                print(f"No menu URLs found for cafe '{cafe['name']}'.")

    print(f"Total cafes analyzed: {len(cafes)}")
    print(f"Total cafes with menu URL found: {menu_url_found}")
    print(f"Percentage of cafes with menu URL found: {menu_url_found / len(cafes) * 100:.2f}%")


if __name__ == "__main__":
    # url = "https://51gradcafe.de/"

    cafes = get_cafes_in_city("Bochum, Germany")
    cafes_with_website = filter_cafes_with_website(cafes)
    analyze_cafes(cafes_with_website)
