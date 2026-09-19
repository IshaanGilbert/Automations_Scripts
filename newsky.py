from playwright.sync_api import sync_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page()
    try:
        page.goto("https://example.com", timeout=120000)
        logging.info("Page loaded successfully")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        browser.close()