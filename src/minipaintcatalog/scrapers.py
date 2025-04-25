import json
import os
from abc import ABC, abstractmethod
from io import BytesIO

import cairosvg
import requests
from PIL import Image
from playwright.sync_api import Browser, Page, sync_playwright

from minipaintcatalog.datamodel import Paint  # assuming this is your model

DATA_FOLDER = "./data"


class Scraper(ABC):
    """
    Abstract base class for all paint scrappers.
    Subclasses must implement the `parse` method to return the list of `Paint`.
    """

    def __init__(self):
        pass

    @abstractmethod
    def load_page(self) -> Page:
        """
        Loads the page using Playwright and returns a `Page` object. The class must store
        the browser instance in `self.browser` for later use.
        """
        pass

    @abstractmethod
    def parse(self) -> list[Paint]:
        """
        Parses the URL information and returns a list of `Paint` containing the metadata
        for each paint.
        """
        pass


class CitadelScraper(Scraper):
    def __init__(self, *args, **kwargs):
        super().__init__()

        # initializing self properties
        self.url = "https://www.warhammer.com/en-WW/paint"
        self.data_folder = os.path.join(DATA_FOLDER, "citadel")

        # opening browser for scraping
        playwright = sync_playwright().start()
        self.browser: Browser = playwright.firefox.launch(headless=False)

    def load_page(self) -> Page:
        page = self.browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
        page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)  # let JS finish

        # apply filters to extract categories for paints
        filter = page.query_selector_all(
            '[data-testid="search-results-filter-button"]'
        )[0].query_selector("button")
        if not filter or filter.is_disabled():
            print("Filter button not found or disabled.")
        else:
            filter.click()
            page.wait_for_timeout(5000)  # let new paints load

        # Click "Show more" until it disappears or is disabled
        while True:
            try:
                show_more = page.query_selector_all('[data-testid="load-more-widget"]')[
                    0
                ].query_selector("button")
                if not show_more or show_more.is_disabled():
                    break
                show_more.click()
                page.wait_for_timeout(5000)  # let new paints load
            except Exception as e:
                print(f"Stopped loading more paints: {e}")
                break
        return page

    def parse(self) -> list[Paint]:
        page = self.load_page()
        product_cards = page.query_selector_all('[data-test="product-card"]')
        paints = []
        for i, card in enumerate(product_cards):
            name_el = card.query_selector('[data-testid="product-card-name"]')
            name = name_el.inner_text() if name_el else "Unknown"

            price_el = card.query_selector('[data-testid="product-card-current-price"]')
            price = price_el.inner_text() if price_el else "N/A"

            img_el = card.query_selector("img")
            img_src = img_el.get_attribute("src") if img_el else None
            img_url = f"https://www.warhammer.com{img_src}" if img_src else None

            paint = Paint(
                manufacturer="Citadel",
                name=name.strip(),
                price=price.strip(),
                image_url=img_url,
            )
            print(f"Paint {i} located: {name.strip()}")

            if img_url:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
                }
                response = requests.get(img_url, headers=headers)
                response.raise_for_status()
                if response.headers.get("Content-Type") == "image/svg+xml":
                    png_data = cairosvg.svg2png(bytestring=response.content)
                    img = Image.open(BytesIO(png_data)).convert("RGB")
                    # Get center pixel
                    width, height = img.size
                    center_pixel = img.getpixel((width // 2, height // 2))
                    rgb_code = center_pixel
                    hex_code = f"#{center_pixel[0]:02x}{center_pixel[1]:02x}{center_pixel[2]:02x}"

                    paint.rgb_color = rgb_code
                    paint.hex_color = hex_code
            paints.append(paint)

        # don't forget to close the browser before returning `paints`
        self.browser.close()
        return paints

    def save_to_json(
        self, paints: list[Paint] = [], filename: str = "citadel_paints.json"
    ):
        if not paints:
            paints = self.parse()

        # creating directory in data/
        os.makedirs(self.data_folder, exist_ok=True)
        json_path = os.path.join(self.data_folder, filename)

        # Convert all Paint objects to dicts
        data = [paint.model_dump() for paint in paints]

        # Write to JSON file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(paints)} paints to {json_path}")
