import os
import time
import random
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("run_log.txt"),
        logging.StreamHandler()
    ]
)

# ---------- CONFIG ----------
TARGET_URL = "https://bigbillionwall.com"
START_BUTTON_SELECTOR = "a.btn-main"
START_BUTTON_XPATH = "//*[contains(@class, 'btn-main') or contains(text(), 'Start Searching') or contains(text(), 'start searching')]"
BASE_PROFILE_DIR = Path("./chrome_profiles_uc_runs")
HEADLESS = False  # Keep False to visually verify mobile view
MAX_CONCURRENT_PROFILES = 1  # Reduced to 1 for 13-inch laptop
WAIT_AFTER_CLICK = (30, 60)  # Reduced wait for testing
TOTAL_RUNS = 5  # Small for testing
# ----------------------------------

def generate_fingerprinting():
    # Mobile devices with precise user agents and metrics
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
    options.add_argument(f"--user-agent={fp['user_agent']}")
    options.add_argument(f"--lang={fp['accept_language']}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")  # Added for stability on some systems
    if headless:
        options.add_argument("--headless=new")
    
    # Enforce mobile view with device emulation
    mobile_emulation = {
        "deviceMetrics": {
            "width": fp["screen_width"],
            "height": fp["screen_height"],
            "pixelRatio": fp["pixel_ratio"]
        },
        "userAgent": fp["user_agent"]
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    return options

def start_browser_uc(fp: dict, profile_dir: str, headless: bool = False):
    try:
        options = build_uc_options(fp, profile_dir, headless=headless)
        driver = uc.Chrome(options=options, version_main=126)
        return driver
    except WebDriverException as e:
        logging.error(f"Failed to start browser: {e}")
        return None

def wait_and_click_start(driver, selector_css: str, selector_xpath: str, idx: int):
    wait = WebDriverWait(driver, 30)  # Increased timeout
    try:
        # Scroll down to ensure button is in view
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # Wait for scroll
        # Try CSS selector first
        el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector_css)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", el)
        time.sleep(random.uniform(1.5, 2))
        try:
            el.click()
            logging.info("Clicked button using CSS selector (normal click)")
        except:
            driver.execute_script("arguments[0].click();", el)
            logging.info("Clicked button using CSS selector (JS click)")
        return True
    except TimeoutException:
        logging.warning("Button not found with CSS selector, trying XPath")
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            el = wait.until(EC.element_to_be_clickable((By.XPATH, selector_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", el)
            time.sleep(random.uniform(1.5, 2))
            try:
                el.click()
                logging.info("Clicked button using XPath (normal click)")
            except:
                driver.execute_script("arguments[0].click();", el)
                logging.info("Clicked button using XPath (JS click)")
            return True
        except TimeoutException:
            logging.warning("Button not found with XPath either")
            # Save screenshot for debugging
            driver.save_screenshot(f"screenshot_{idx}.png")
            logging.info(f"Screenshot saved: screenshot_{idx}.png")
            return False

def run_one_iteration(idx: int):
    timestamp = int(time.time())
    profile_dir = BASE_PROFILE_DIR.joinpath(f"profile_{timestamp}_{idx}")
    fp = generate_fingerprinting()
    logging.info(f"Run {idx} - profile_dir={profile_dir} Device={fp['device_name']} UA={fp['user_agent']} Resolution={fp['screen_width']}x{fp['screen_height']}")
    driver = None
    try:
        driver = start_browser_uc(fp, str(profile_dir), headless=HEADLESS)
        if not driver:
            raise Exception("Failed to initialize browser")
        driver.set_page_load_timeout(30)
        driver.get(TARGET_URL)
        time.sleep(random.uniform(2.0, 4.0))  # Increased wait for page load
        clicked = wait_and_click_start(driver, START_BUTTON_SELECTOR, START_BUTTON_XPATH, idx)
        logging.info(f"Run {idx} - clicked start: {clicked}")
        if clicked:
            wait_sec = random.uniform(*WAIT_AFTER_CLICK)
            logging.info(f"Run {idx} - keeping browser open for {wait_sec:.1f} seconds")
            time.sleep(wait_sec)
        else:
            logging.warning(f"Run {idx} - skipping wait due to click failure")
    except Exception as e:
        logging.exception(f"Run {idx} - error: {e}")
        if driver:
            driver.save_screenshot(f"error_screenshot_{idx}.png")
            logging.info(f"Error screenshot saved: error_screenshot_{idx}.png")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
            logging.info(f"Run {idx} - browser closed.")

def main():
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
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script stopped by user.")