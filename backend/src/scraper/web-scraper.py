from playwright.sync_api import sync_playwright


def scrape_website(url):
    with sync_playwright() as p:
        config = {
            "accept_downloads": False,  # do not download stuff
            "locale": "en-US",  # emulate us english language settings
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

        page.goto(url)

        # Example: Extract all the text from the page
        content = page.content()
        print(content)

        page.close()
        context.close()


if __name__ == "__main__":
    url = "https://de.linkedin.com/school/ruhrunibochum/people?facetCurrentFunction=4"
    scrape_website(url)
