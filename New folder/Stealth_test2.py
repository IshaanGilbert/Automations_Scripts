import os
import sys
import time
import random
import logging
import multiprocessing
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth

# Setup logging
def setup_logging():
    log_path = os.path.join(os.path.abspath("."), "error_log_playwright.txt")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logging()

# === Target URLs ===
URLS = [
    "https://marcadeo.com/",
    "https://unfilteredgadgets.com/",
    "https://marcadeo.in/"
]

# === Proxy pool ===
PROXY_LIST = [
    {
        "server": "socks5://92.204.164.15:11001",
        "username": "geonode_xvmYN44Bvz",
        "password": "CHANGE_ME_PASSWORD"
    },
    # Add more proxies here
]

# === Config ===
TOTAL_VISITS = 10
CONCURRENT_PROCESSES = 8  # Set according to CPU

def visit_target(index):
    proxy = random.choice(PROXY_LIST)
    target_url = random.choice(URLS)
    logging.info(f"[{index}] Visiting: {target_url} via {proxy['server']}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )
            context = browser.new_context(
                proxy={
                    "server": proxy["server"],
                    "username": proxy["username"],
                    "password": proxy["password"]
                },
                viewport={"width": 1920, "height": 1080},
                user_agent=f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120,140)}.0.0.0 Safari/537.36",
                locale="en-US"
            )
            page = context.new_page()
            stealth(page)  # Stealth enabled

            page.goto(target_url, timeout=60000)
            time.sleep(random.randint(5, 8))

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.randint(3, 5))

            try:
                buttons = page.locator("//div[@class='hmvrCard']//a[contains(text(), 'Apply Now')]")
                count = buttons.count()
                if count > 0:
                    buttons.nth(random.randint(0, count - 1)).click()
                    logging.info(f"[{index}] Clicked 'Apply Now'")
                else:
                    logging.info(f"[{index}] No 'Apply Now' buttons found")
            except Exception as click_error:
                logging.warning(f"[{index}] Click error: {click_error}")

            page.close()
            context.close()
            browser.close()

    except Exception as e:
        logging.error(f"[{index}] Error: {e}", exc_info=True)

def run_all_visits():
    with multiprocessing.Pool(processes=CONCURRENT_PROCESSES) as pool:
        pool.map(visit_target, range(TOTAL_VISITS))

if __name__ == '__main__':
    multiprocessing.freeze_support()
    logging.info("🚀 Starting visits with stealth Playwright")
    run_all_visits()
    logging.info("✅ All visits completed.")
