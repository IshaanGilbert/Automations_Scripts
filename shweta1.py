# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 14:48:18 2025

@author: yoges
"""

# -*- coding: utf-8 -*-
"""
multi_uc_mobile_runner.py
Run multiple UC Chrome profiles with mobile fingerprinting, proxy, and click 'Start Searching'.
"""
import os
import time
import random
import logging
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# optional selenium-wire for proxy auth
try:
    from seleniumwire import webdriver as wire_webdriver
    SELENIUM_WIRE_AVAILABLE = True
except Exception:
    wire_webdriver = None
    SELENIUM_WIRE_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------- USER CONFIG ----------
TARGET_URL = "https://bigbillionwall.com"
START_BUTTON_SELECTOR = "a.btn-main"
BASE_PROFILE_DIR = Path("./chrome_profiles_uc_runs")
HEADLESS = False
MAX_CONCURRENT_PROFILES = 7    # max browsers open at the same time
DELAY_BETWEEN_RUNS = (2.0, 6.0)
WAIT_BEFORE_CLOSE = (60, 180)    # 1-3 min wait after clicking start
PROXY_STRING = "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff"
# ----------------------------------

def generate_fingerprinting():
    user_agents = [
        "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
    ]
    version_main = random.randint(8, 14)
    version_minor = random.randint(0, 3)
    webkit_version = random.randint(500, 600)
    chrome_version = random.randint(90, 120)
    build_version = random.randint(1000, 5000)
    ua_template = random.choice(user_agents)
    ua = ua_template.format(version_main, version_minor, webkit_version, chrome_version, build_version)
    widths = [360, 375, 412, 768]
    heights = [640, 667, 800, 812, 915]
    return {
        "user_agent": ua,
        "screen_width": random.choice(widths),
        "screen_height": random.choice(heights),
        "accept_language": random.choice(["en-US,en;q=0.9","en-GB,en;q=0.8","hi-IN,en;q=0.9"])
    }

def parse_proxy_string(s: str):
    if not s:
        return None
    s = s.strip()
    parts = s.split()
    if len(parts) == 1:
        proto = None
        main = parts[0]
    else:
        proto = parts[0].lower()
        main = parts[1]
    segs = main.split(":", 3)
    if len(segs) == 2:
        host, port = segs
        return {"type": proto or "socks5", "host": host, "port": port}
    elif len(segs) == 3:
        host, port, username = segs
        return {"type": proto or "socks5", "host": host, "port": port, "username": username}
    else:
        host, port, username, password = segs
        return {"type": proto or "socks5", "host": host, "port": port, "username": username, "password": password}

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
    options.add_argument("--disable-infobars")  # removes 'Chrome is being controlled'
    options.add_argument("--disable-extensions")
    if headless:
        options.add_argument("--headless=new")
    return options

def start_browser_uc(fp: dict, profile_dir: str, proxy_string: str = None, headless: bool = False):
    proxy_info = parse_proxy_string(proxy_string) if proxy_string else None

    options = build_uc_options(fp, profile_dir, headless=headless)

    # selenium-wire with proxy auth
    if proxy_info and proxy_info.get("username") and proxy_info.get("password"):
        if not SELENIUM_WIRE_AVAILABLE:
            raise RuntimeError("Proxy requires auth but selenium-wire not installed.")
        seleniumwire_options = {
            "proxy": {
                "http": f"{proxy_info['type']}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}",
                "https": f"{proxy_info['type']}://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}",
                "no_proxy": "localhost,127.0.0.1"
            }
        }
        driver = wire_webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
        return driver

    # normal UC Chrome
    driver = uc.Chrome(options=options)
    return driver

def wait_and_click_start(driver, selector_css: str, timeout: int = 20):
    wait = WebDriverWait(driver, timeout)
    try:
        el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector_css)))
        time.sleep(random.uniform(0.5, 1.5))
        el.click()
        return True
    except TimeoutException:
        # fallback to span child or text
        try:
            el2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"{selector_css} .btn-text")))
            time.sleep(random.uniform(0.5, 1.5))
            el2.click()
            return True
        except TimeoutException:
            try:
                el3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[normalize-space()="Start Searching" or .//span[normalize-space()="Start Searching"]]')))
                time.sleep(random.uniform(0.5, 1.5))
                el3.click()
                return True
            except TimeoutException:
                logging.warning("Start Searching button not found.")
                return False

def run_one_iteration(idx: int, proxy_string: str):
    timestamp = int(time.time())
    profile_dir = BASE_PROFILE_DIR.joinpath(f"profile_{timestamp}_{idx}")
    fp = generate_fingerprinting()
    logging.info(f"Run {idx} - profile_dir={profile_dir} UA={fp['user_agent']}")
    driver = None
    try:
        driver = start_browser_uc(fp, str(profile_dir), proxy_string=proxy_string, headless=HEADLESS)
        driver.set_page_load_timeout(30)
        driver.get(TARGET_URL)
        time.sleep(random.uniform(1.0, 3.0))
        clicked = wait_and_click_start(driver, START_BUTTON_SELECTOR, timeout=25)
        logging.info(f"Run {idx} - clicked start: {clicked}")
        # wait 1-3 min before closing
        wait_sec = random.uniform(*WAIT_BEFORE_CLOSE)
        logging.info(f"Run {idx} - keeping browser open for {wait_sec:.1f} seconds")
        time.sleep(wait_sec)
    except Exception as e:
        logging.exception(f"Run {idx} - error: {e}")
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass

def main(total_runs: int):
    BASE_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_PROFILES) as executor:
        futures = []
        for i in range(1, total_runs + 1):
            futures.append(executor.submit(run_one_iteration, i, PROXY_STRING))
            time.sleep(random.uniform(*DELAY_BETWEEN_RUNS))
        # wait all
        for f in futures:
            f.result()
    logging.info("All runs completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run UC Chrome mobile profiles clicking Start Searching.")
    parser.add_argument("--runs", type=int, default=5000, help="Total number of profiles/runs")
    args = parser.parse_args()
    main(args.runs)