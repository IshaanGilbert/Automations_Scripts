import os
import time
import random
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------- CONFIG ----------
TARGET_URL = "https://bigbillionwall.com"
START_BUTTON_SELECTOR = "a.btn-main"
BASE_PROFILE_DIR = Path("./chrome_profiles_uc_runs")
HEADLESS = False
MAX_CONCURRENT_PROFILES = 2  # max browsers open at a time
WAIT_AFTER_CLICK = (60, 180)  # wait 1-3 min after clicking Start Searching
TOTAL_RUNS = 10  # total profiles/runs

# Geonode credentials for proxy
USERNAME = "geonode_xvmYN44Bvz-type-residential-country-in"
PASSWORD = "CHANGE_ME_PASSWORD"
GEONODE_DNS = "sg.proxy.geonode.io:9000"
proxy_url = f"http://{USERNAME}:CHANGE_ME_PASSWORD@{GEONODE_DNS}"
IP_CHECK_URL = "https://api.ipify.org?format=json"
# ----------------------------------

def generate_fingerprinting():
    # Mobile devices with user agents and resolutions
    mobile_devices = [
        {
            "user_agent": "Mozilla/5.0 (Linux; Android 12; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
            "device_name": "Galaxy S10",
            "width": 360,
            "height": 760,
            "pixel_ratio": 3.0
        },
        {
            "user_agent": "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
            "device_name": "Pixel 6",
            "width": 412,
            "height": 732,
            "pixel_ratio": 2.0
        },
        {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.6478.54 Mobile/15E148 Safari/604.1",
            "device_name": "iPhone 13",
            "width": 390,
            "height": 844,
            "pixel_ratio": 3.0
        },
        {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
            "device_name": "iPhone SE",
            "width": 375,
            "height": 667,
            "pixel_ratio": 2.0
        }
    ]
    
    device = random.choice(mobile_devices)
    accept_languages = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.8",
        "hi-IN,en;q=0.9,hi;q=0.7"
    ]
    return {
        "user_agent": device["user_agent"],
        "device_name": device["device_name"],
        "screen_width": device["width"],
        "screen_height": device["height"],
        "pixel_ratio": device["pixel_ratio"],
        "accept_language": random.choice(accept_languages)
    }

def build_uc_options(fp: dict, profile_dir: str, headless: bool = False):
    options = uc.ChromeOptions()
    Path(profile_dir).mkdir(parents=True, exist_ok=True)
    options.add_argument(f"--user-data-dir={str(Path(profile_dir).resolve())}")
    options.add_argument(f"--window-size={fp['screen_width']},{fp['screen_height']}")
    options.add_argument(f"--user-agent={fp['user_agent']}")
    options.add_argument(f"--lang={fp['accept_language']}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")  # remove 'Chrome is being controlled'
    options.add_argument("--disable-extensions")
    if headless:
        options.add_argument("--headless=new")
    
    # Add Proxy Settings
    options.add_argument(f"--proxy-server={proxy_url}")
    
    return options

def start_browser_uc(fp: dict, profile_dir: str, headless: bool = False):
    options = build_uc_options(fp, profile_dir, headless=headless)
    driver = uc.Chrome(options=options)
    return driver

def wait_and_click_start(driver, selector_css: str):
    wait = WebDriverWait(driver, 20)
    try:
        el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector_css)))
        time.sleep(random.uniform(1.5, 2))
        el.click()
        return True
    except TimeoutException:
        logging.warning("Start Searching button not found.")
        return False

def check_ip_using_proxy():
    try:
        response = requests.get(IP_CHECK_URL, proxies={"http": proxy_url, "https": proxy_url})
        ip_data = response.json()
        logging.info(f"Current IP address through proxy: {ip_data['ip']}")
        return ip_data
    except requests.RequestException as e:
        logging.error(f"Error checking IP with proxy: {e}")
        return None

def run_one_iteration(idx: int):
    timestamp = int(time.time())
    profile_dir = BASE_PROFILE_DIR.joinpath(f"profile_{timestamp}_{idx}")
    fp = generate_fingerprinting()
    logging.info(f"Run {idx} - profile_dir={profile_dir} UA={fp['user_agent']}")
    driver = None
    try:
        driver = start_browser_uc(fp, str(profile_dir), headless=HEADLESS)
        driver.set_page_load_timeout(30)
        driver.get(TARGET_URL)
        time.sleep(random.uniform(1.0, 3.0))
        clicked = wait_and_click_start(driver, START_BUTTON_SELECTOR)
        logging.info(f"Run {idx} - clicked start: {clicked}")
        # Random wait 1-3 minutes after clicking start
        wait_sec = random.uniform(*WAIT_AFTER_CLICK)
        logging.info(f"Run {idx} - keeping browser open for {wait_sec:.1f} seconds")
        time.sleep(wait_sec)
    except Exception as e:
        logging.exception(f"Run {idx} - error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def main():
    # Check the proxy IP first
    check_ip_using_proxy()

    BASE_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_PROFILES) as executor:
        futures = {executor.submit(run_one_iteration, i): i for i in range(1, TOTAL_RUNS + 1)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                future.result()
                logging.info(f"Run {idx} completed and browser closed.")
            except Exception as e:
                logging.error(f"Run {idx} failed: {e}")
    logging.info("All runs completed.")

if __name__ == "__main__":
    main()
