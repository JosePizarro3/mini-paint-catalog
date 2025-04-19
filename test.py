import urllib.request

import requests
from bs4 import BeautifulSoup

url = "https://www.warhammer.com/en-WW/paint"

import time

from playwright.sync_api import sync_playwright

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
    print(page)
