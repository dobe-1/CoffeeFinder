import re
from datetime import UTC, datetime
from urllib.parse import urlsplit, urlparse, urljoin

from playwright.sync_api import sync_playwright

from backend.models import CoffeeShop, Menu

MENU_PATTERN = re.compile(
    r"([a-z]*karte[n]?|[a-z]*men(?:ü|ue|u|%C3%BC)s?|essen|food|drink[s]|speisen|mittagstisch|fr(?:ü|ue|u|%C3%BC)hst(?:ü|ue|u|%C3%BC)ck|getr(?:ä|ae|a|%C3%A4)nke|drinks?|food)",
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


def is_menu_link_str(text: str | None) -> bool:
    if text and MENU_PATTERN.search(text):
        return True
    return False


def is_crawlable_page(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.lower()

    ignored_extensions = [
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".zip",
        ".tar",
        ".gz",
        ".mp4",
        ".mp3",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
    ]

    return not any(path.endswith(ext) for ext in ignored_extensions)


def get_menu_urls_from_website(url, max_depth=3, max_calls=20) -> list:

    base_domain = urlparse(url).netloc

    visited_urls = set()
    menu_urls = []
    call_count = 0
    current_depth = 0

    queue = [url]
    queue_next = set()

    with sync_playwright() as p:
        config = {
            "accept_downloads": False,  # do not download stuff
            "locale": "de-DE",  # emulate us english language settings
            "screen": {"width": 1920, "height": 1080},  # emulate full hd screen
            "viewport": {"width": 1920, "height": 1080},  # emulate full hd viewport
            "headless": True,  # set true to not show browser window (invisible); set false to show browser window (visible)
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
        while current_depth < max_depth:
            if current_depth > 0:
                print(f"search with depth {current_depth}")
            while queue and call_count < max_calls:
                current_url = queue.pop()
                # times.sleep(3) #maybe do this to not ddos the page
                # check for duplicates

                if current_url in visited_urls:
                    continue

                visited_urls.add(current_url)
                call_count += 1

                try:
                    page.goto(current_url, timeout=15000)
                except Exception as e:
                    print(f"Error navigating to {current_url}: {e}")
                    continue
                frame = page.frames[0]
                locators = frame.locator("a")

                for i in range(locators.count()):
                    locator = locators.nth(i)
                    href = locator.get_attribute("href")
                    if not href:
                        continue
                    # handle relative urls
                    href = urljoin(current_url, href)

                    try:
                        validated_url = validate_url(href)
                    except ValueError:
                        continue
                    if is_menu_link(locator.inner_text(), validated_url):
                        if validated_url not in menu_urls:
                            menu_urls.append(validated_url)
                            print(f"Found menu URL: {validated_url}")
                    else:
                        # append to queue (for next depth) if it is from same domain
                        if urlparse(validated_url).netloc == base_domain and is_crawlable_page(
                            validated_url
                        ):
                            queue_next.add(validated_url)

            if menu_urls:
                break
            else:
                current_depth += 1
                queue = queue_next
                queue_next = set()

        page.close()
        context.close()

        return menu_urls


def retrieve_menu_data(menu: Menu):
    if not menu.menu_url:
        print("No menu URL provided.")
        return

    with sync_playwright() as p:
        config = {
            "locale": "de-DE",  # emulate us english language settings
            "screen": {"width": 1920, "height": 1080},  # emulate full hd screen
            "viewport": {"width": 1920, "height": 1080},  # emulate full hd viewport
            "headless": True,  # set true to not show browser window (invisible); set false to show browser window (visible)
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
            page.goto(menu.menu_url)
        except Exception as e:
            print(f"Error navigating to {menu.menu_url}: {e}")
            context.close()
            menu.menu_url_accessible = False
            menu.menu_url_last_checked = datetime.now(tz=UTC)
            return

        menu.menu_url_accessible = True
        menu.menu_url_last_checked = datetime.now(tz=UTC)

        # TODO: implement actual menu data extraction logic here


# def _analyze_cafes(cafes: GeoDataFrame):
#     menu_url_found = 0
#
#     for index, cafe in cafes.iterrows():
#         menu_url = cafe.get("website:menu")
#         if pd.notna(menu_url):
#             menu_url_found += 1
#             print(f"Cafe: {cafe['name']}, Menu URL: {cafe['website:menu']}")
#             continue
#
#         cafe_website = cafe.get("website")
#         contact_website = cafe.get("contact:website")
#
#         if pd.notna(cafe_website):
#             cafe_website = cafe_website.strip()
#         elif pd.notna(contact_website):
#             cafe_website = contact_website.strip()
#         else:
#             print(f"No website found for cafe: {cafe['name']}")
#             continue
#
#         if cafe_website:
#             print(f"Analyzing website for cafe: {cafe['name']} at {cafe_website}")
#             menu_urls = get_menu_urls_from_website(cafe_website)
#             if menu_urls:
#                 print(f"Menu URLs found for cafe '{cafe['name']}': {menu_urls}")
#                 menu_url_found += 1
#                 continue
#             else:
#                 print(f"No menu URLs found for cafe '{cafe['name']}'.")
#
#     print(f"Total cafes analyzed: {len(cafes)}")
#     print(f"Total cafes with menu URL found: {menu_url_found}")
#     print(f"Percentage of cafes with menu URL found: {menu_url_found / len(cafes) * 100:.2f}%")


def extract_menu_url_from_coffee_shop(coffee_shop: CoffeeShop):
    if coffee_shop.website.url:
        if not coffee_shop.menu.menu_url:
            try:
                menu_urls = get_menu_urls_from_website(coffee_shop.website.url)
                coffee_shop.website.accessible = True
                coffee_shop.website.last_checked = datetime.now(tz=UTC)
            except Exception as e:
                coffee_shop.website.accessible = False
                coffee_shop.website.last_checked = datetime.now(tz=UTC)
                print(f"Error accessing website for {coffee_shop.name}: {e}")
                return
        else:
            menu_urls = [coffee_shop.menu.menu_url]

        if menu_urls:
            # TODO: implement logic to choose the best menu URL if there are multiple
            coffee_shop.menu.menu_url = menu_urls[0]
            retrieve_menu_data(coffee_shop.menu)


# if __name__ == "__main__":
#     # url = "https://51gradcafe.de/"
#    # essen 53.23% 62/ 33
#     cafes = get_cafes_in_city("Bochum, Germany")
#     cafes_with_website = filter_cafes_with_website(cafes)
#     _analyze_cafes(cafes_with_website)
