# -*- coding: utf-8 -*-
"""
UC Chrome runner with mobile fingerprinting and SOCKS5 proxy (authenticated)
Continuous profile launching, old browsers close after 5–10 min
No profile folders saved
@author: yoges
"""

import time
import random
from seleniumwire import webdriver as wire_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ---------- CONFIG ----------
TARGET_URL = "https://bigbillionwall.com"
START_BUTTON_SELECTOR = "a.btn-main"
HEADLESS = False

# Browser lifespan in seconds (5–10 min)
BROWSER_LIFESPAN = (300, 600)

# Interval between launching new browsers
NEW_BROWSER_INTERVAL = (1, 15)  # every 5–15 seconds

# Total number of profiles to create
TOTAL_PROFILES = 5000

# List of SOCKS5 proxies with auth
PROXY_LIST = [
    "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
]
# ----------------------------------

def parse_proxy_string(s: str):
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

def generate_fingerprinting():
    """Generate realistic mobile device fingerprints"""
    # Comprehensive mobile user agents
    user_agents = [
        # Android Chrome - Latest versions
        "Mozilla/5.0 (Linux; Android {0}.{1}; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{2}.0.{3}.{4} Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}; Pixel {5}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{2}.0.{3}.{4} Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{2}.0.{3}.{4} Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}; OnePlus {5}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{2}.0.{3}.{4} Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}; Mi {5}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{2}.0.{3}.{4} Mobile Safari/537.36",
        
        # iPhone Safari
        "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{0}.{1} Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone{5}; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{0}.{1} Mobile/15E148 Safari/604.1",
        
        # iPhone Chrome
        "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{2}.0.{3}.{4} Mobile/15E148 Safari/604.1",
        
        # iPad
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{0}.{1} Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{2}.0.{3}.{4} Mobile/15E148 Safari/604.1"
    ]
    
    # Version ranges
    android_version = random.randint(10, 14)
    ios_version = random.randint(15, 17)
    version_minor = random.randint(0, 5)
    chrome_version = random.randint(115, 120)
    chrome_build = random.randint(5000, 6500)
    chrome_patch = random.randint(100, 250)
    device_model = random.randint(6, 12)
    
    ua_template = random.choice(user_agents)
    
    # Format user agent based on type
    if "Android" in ua_template:
        ua = ua_template.format(android_version, version_minor, chrome_version, chrome_build, chrome_patch, device_model)
        platform = "Android"
    else:  # iOS
        iphone_model = f" {device_model}" if "{5}" in ua_template else ""
        ua = ua_template.format(ios_version, version_minor, chrome_version, chrome_build, chrome_patch, iphone_model)
        platform = "iOS"
    
    # Realistic mobile screen resolutions with proper aspect ratios
    mobile_screens = {
        "small_phones": [(320, 568), (360, 640), (375, 667)],
        "medium_phones": [(375, 812), (390, 844), (393, 851), (412, 869), (412, 915)],
        "large_phones": [(414, 896), (428, 926), (430, 932)],
        "tablets": [(768, 1024), (810, 1080), (820, 1180), (834, 1194), (1024, 1366)]
    }
    
    # Choose screen category based on device type
    if "iPad" in ua:
        screen_category = "tablets"
    elif platform == "Android":
        screen_category = random.choices(
            ["small_phones", "medium_phones", "large_phones", "tablets"],
            weights=[10, 50, 30, 10]
        )[0]
    else:  # iPhone
        screen_category = random.choices(
            ["small_phones", "medium_phones", "large_phones"],
            weights=[15, 60, 25]
        )[0]
    
    screen_width, screen_height = random.choice(mobile_screens[screen_category])
    
    # Device pixel ratio based on screen size
    if screen_category == "tablets":
        pixel_ratio = random.uniform(1.5, 2.5)
    elif screen_category == "small_phones":
        pixel_ratio = random.uniform(2.0, 2.5)
    else:
        pixel_ratio = random.uniform(2.5, 3.5)
    
    return {
        "user_agent": ua,
        "screen_width": screen_width,
        "screen_height": screen_height,
        "pixel_ratio": pixel_ratio,
        "platform": platform
    }

def build_uc_options(fp: dict):
    options = wire_webdriver.ChromeOptions()
    options.add_argument(f"--window-size={fp['screen_width']},{fp['screen_height']}")
    options.add_argument(f"--user-agent={fp['user_agent']}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    if HEADLESS:
        options.add_argument("--headless=new")
    return options

# def start_browser(fp: dict, proxy: dict):
#     options = build_uc_options(fp)
#     seleniumwire_options = {
#         'proxy': {
#             'http': f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}",
#             'https': f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}",
#             'no_proxy': 'localhost,127.0.0.1'
#         },
#         'ca_cert': 'ca.crt'
#     }
#     driver = wire_webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
#     return driver

def start_browser(fp: dict, proxy: dict):
    options = build_uc_options(fp)
    seleniumwire_options = {
        'proxy': {
            'http': f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}",
            'https': f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}",
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    driver = wire_webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
    return driver

def click_start(driver):
    try:
        el = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, START_BUTTON_SELECTOR))
        )
        time.sleep(random.uniform(0.5, 1.5))
        el.click()
        return True
    except TimeoutException:
        return False

def main():
    idx = 1
    active_browsers = []

    while idx <= TOTAL_PROFILES or active_browsers:
        # Launch new browser if we haven't reached TOTAL_PROFILES
        if idx <= TOTAL_PROFILES:
            fp = generate_fingerprinting()
            proxy_str = random.choice(PROXY_LIST)
            proxy = parse_proxy_string(proxy_str)

            try:
                driver = start_browser(fp, proxy)
                driver.get(TARGET_URL)
                time.sleep(random.uniform(1, 2))
                click_start(driver)
                # Store driver with its closing timestamp
                close_time = time.time() + random.uniform(*BROWSER_LIFESPAN)
                active_browsers.append({"driver": driver, "close_time": close_time})
                print(f"Profile {idx} opened, will close around {int(close_time)}")
            except Exception as e:
                print(f"Profile {idx} failed to open: {e}")

            idx += 1
            time.sleep(random.uniform(*NEW_BROWSER_INTERVAL))

        # Close browsers whose lifespan ended
        for item in active_browsers[:]:
            if time.time() >= item["close_time"]:
                try:
                    item["driver"].quit()
                    print("Closed a browser")
                except:
                    pass
                active_browsers.remove(item)

if __name__ == "__main__":
    main()