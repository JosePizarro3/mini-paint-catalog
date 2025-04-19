import os
import requests
from playwright.sync_api import sync_playwright
import cairosvg
from PIL import Image
from io import BytesIO

from minipaintcatalog.datamodel import Paint


url = "https://www.warhammer.com/en-WW/paint"

FOLDER_IMG = "./data/citadel/"


with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800},
    )
    page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)  # let JS finish
    # page.wait_for_load_state("networkidle")
    # time.sleep(10)

    product_cards = page.query_selector_all('[data-test="product-card"]')
    paints = []
    for i, card in enumerate(product_cards):
        name_el = card.query_selector('[data-testid="product-card-name"]')
        name = name_el.inner_text() if name_el else "Unknown"

        price_el = card.query_selector('[data-testid="product-card-current-price"]')
        price = price_el.inner_text() if price_el else "N/A"

        tag_els = card.query_selector_all('[data-testid="product-card-tags"] li')
        tags = [tag.inner_text() for tag in tag_els] if tag_els else []

        img_el = card.query_selector('img')
        img_src = img_el.get_attribute("src") if img_el else None
        img_url = f"https://www.warhammer.com{img_src}" if img_src else None

        paint = Paint(
            name=name.strip(),
            price=price.strip(),
            tags=tags,
            image_url=img_url,
        )
        print(f"Paint {i} located: {name.strip()}")

        if img_url:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
            }
            response = requests.get(img_url, headers=headers)
            response.raise_for_status()
            if response.headers.get("Content-Type") == 'image/svg+xml':
                png_data = cairosvg.svg2png(bytestring=response.content)
                img = Image.open(BytesIO(png_data)).convert("RGB")
                # Get center pixel
                width, height = img.size
                center_pixel = img.getpixel((width // 2, height // 2))
                rgb_code = center_pixel
                hex_code = '#%02x%02x%02x' % center_pixel

                paint.rgb_color = rgb_code
                paint.hex_color = hex_code


        paints.append(paint)

    browser.close()
    print(paints)