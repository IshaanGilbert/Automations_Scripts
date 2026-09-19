# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Automation script for Skyscanner using GoLogin and GeoNode
# Creates unique browser profiles with GeoNode proxies
# """

# import time
# import random
# import os
# import tempfile
# import json
# import shutil
# import multiprocessing
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

# # Try to import GoLogin
# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     GOLOGIN_AVAILABLE = False
#     print("GoLogin not available. Please install with 'pip install gologin'.")

# # ---------- CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# HEADLESS = False

# # Browser lifespan in seconds (5–10 min)
# BROWSER_LIFESPAN = (300, 600)

# # Interval between launching new browsers
# NEW_BROWSER_INTERVAL = (5, 15)

# # Total number of profiles to create
# TOTAL_PROFILES = 100

# # Mode: Always "gologin" for this script
# AUTOMATION_MODE = "gologin"

# # GoLogin Configuration
# try:
#     with open("config.json") as f:
#         TOKENS = json.load(f)["tokens"]
# except Exception:
#     TOKENS = [
#         "CHANGE_ME_JWT_TOKEN"  # Replace with your GoLogin token
#     ]

# CHROMEDRIVER_PATH = "chromedriver.exe"

# # GeoNode Proxy Configuration
# GOLOGIN_PROXY_TEMPLATE = {
#     "mode": "socks5",
#     "host": "sg.proxy.geonode.io",
#     "port": 11000,
#     "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#     "password": "CHANGE_ME_PASSWORD"
# }

# # Batch processing for GoLogin
# BATCH_SIZE = 5
# # ----------------------------------

# def generate_mobile_fingerprint():
#     """Generate mobile device fingerprints"""
#     mobile_user_agents = [
#         "Mozilla/5.0 (Linux; Android {android_version}; {device_model}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.{build_version}.{patch_version} Mobile Safari/537.36",
#         "Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_version}.0 Mobile/15E148 Safari/604.1",
#     ]
    
#     mobile_devices = [
#         {"model": "iPhone12,1", "width": 414, "height": 896, "pixel_ratio": 2.0},
#         {"model": "SM-G991B", "width": 360, "height": 800, "pixel_ratio": 3.0},
#         {"model": "Pixel 6", "width": 412, "height": 915, "pixel_ratio": 2.625},
#     ]
    
#     device = random.choice(mobile_devices)
#     ua_template = random.choice(mobile_user_agents)
    
#     android_version = f"{random.randint(8, 13)}.{random.randint(0, 1)}"
#     ios_version = f"{random.randint(13, 16)}_{random.randint(0, 7)}"
#     chrome_version = random.randint(110, 120)
#     build_version = random.randint(5000, 6000)
#     patch_version = random.randint(100, 999)
#     safari_version = random.randint(15, 17)
    
#     ua = ua_template.format(
#         android_version=android_version,
#         ios_version=ios_version,
#         device_model=device["model"],
#         chrome_version=chrome_version,
#         build_version=build_version,
#         patch_version=patch_version,
#         safari_version=safari_version
#     )
    
#     return {
#         "user_agent": ua,
#         "screen_width": device["width"],
#         "screen_height": device["height"],
#         "pixel_ratio": device["pixel_ratio"],
#         "device_model": device["model"]
#     }

# def build_chrome_options(fp: dict):
#     """Build Chrome options with mobile emulation"""
#     options = webdriver.ChromeOptions()
    
#     options.add_argument(f"--window-size={fp['screen_width']},{fp['screen_height']}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-popup-blocking")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")
    
#     mobile_emulation = {
#         "deviceMetrics": {
#             "width": fp['screen_width'],
#             "height": fp['screen_height'],
#             "pixelRatio": fp['pixel_ratio']
#         },
#         "userAgent": fp['user_agent']
#     }
#     options.add_experimental_option("mobileEmulation", mobile_emulation)
#     options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
#     options.add_experimental_option('useAutomationExtension', False)
    
#     if HEADLESS:
#         options.add_argument("--headless=new")
    
#     return options

# def start_gologin_browser(run_index, token):
#     """Start browser using GoLogin with GeoNode proxy"""
#     if not GOLOGIN_AVAILABLE:
#         print("GoLogin not available!")
#         return None, None
    
#     print(f"\n--- Starting GoLogin profile #{run_index+1} ---")
#     gl = GoLogin({"token": token})
    
#     try:
#         fp = generate_mobile_fingerprint()
        
#         profile_id = gl.createProfileWithCustomParams({
#             "name": f"auto-skyscanner-{run_index+1}",
#             "os": "android",
#             "navigator": {
#                 "userAgent": fp['user_agent'],
#                 "resolution": f"{fp['screen_width']}x{fp['screen_height']}",
#                 "language": "en-US",
#                 "platform": "Linux armv8l"
#             },
#             "proxyEnabled": True,
#             "proxy": GOLOGIN_PROXY_TEMPLATE
#         })
        
#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
        
#         service = Service(CHROMEDRIVER_PATH)
#         chrome_options = build_chrome_options(fp)
#         chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         return driver, profile_id
        
#     except Exception as e:
#         print(f"[ERROR GoLogin #{run_index+1}]: {e}")
#         return None, None

# def interact_with_skyscanner(driver):
#     """Interact with Skyscanner website"""
#     try:
#         print("Loading Skyscanner...")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(5, 10))
        
#         WebDriverWait(driver, 20).until(
#             lambda d: d.execute_script("return document.readyState") == "complete"
#         )
        
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
#         time.sleep(random.uniform(2, 4))
        
#         search_selectors = [
#             "input[placeholder*='Where from']",
#             "input[placeholder*='Where to']",
#             "[data-testid*='searchbox']",
#         ]
        
#         for selector in search_selectors:
#             try:
#                 element = WebDriverWait(driver, 5).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, selector))
#                 )
#                 driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
#                 time.sleep(1)
#                 print(f"Found search element: {selector}")
#                 break
#             except TimeoutException:
#                 continue
        
#         for _ in range(3):
#             scroll_position = random.randint(0, 1000)
#             driver.execute_script(f"window.scrollTo(0, {scroll_position});")
#             time.sleep(random.uniform(1, 3))
        
#         print("Skyscanner interaction completed")
#         return True
        
#     except Exception as e:
#         print(f"Error interacting with Skyscanner: {e}")
#         return False

# def run_gologin_batch(batch_index):
#     """Run batch of GoLogin profiles"""
#     if not GOLOGIN_AVAILABLE:
#         print("GoLogin not available!")
#         return
    
#     processes = []
#     for i in range(BATCH_SIZE):
#         run_index = batch_index * BATCH_SIZE + i
#         if run_index >= TOTAL_PROFILES:
#             break
#         token_index = run_index // 1000 % len(TOKENS)
#         token = TOKENS[token_index]
#         p = multiprocessing.Process(target=run_single_profile, args=(run_index, token))
#         processes.append(p)
#         p.start()
    
#     for p in processes:
#         p.join()

# def run_single_profile(run_index, token):
#     """Run single GoLogin profile"""
#     driver, profile_id = start_gologin_browser(run_index, token)
#     if driver is None:
#         return
    
#     try:
#         if interact_with_skyscanner(driver):
#             lifespan = random.uniform(*BROWSER_LIFESPAN)
#             print(f"Keeping browser open for {lifespan:.0f} seconds")
#             time.sleep(lifespan)
#     finally:
#         driver.quit()
#         print(f"Stopped GoLogin profile #{run_index+1} (ID: {profile_id})")

# def main():
#     """Main execution function"""
#     print(f"Starting Skyscanner automation in {AUTOMATION_MODE.upper()} mode")
#     print(f"Target URL: {TARGET_URL}")
#     print(f"Total profiles: {TOTAL_PROFILES}")
    
#     if not GOLOGIN_AVAILABLE:
#         print("GoLogin not available! Please install the package.")
#         return
    
#     total_batches = (TOTAL_PROFILES + BATCH_SIZE - 1) // BATCH_SIZE
#     for batch_index in range(total_batches):
#         print(f"\n=== Running GoLogin Batch {batch_index+1}/{total_batches} ===")
#         run_gologin_batch(batch_index)
#     print("\n✅ All GoLogin profile runs completed.")

# if __name__ == "__main__":
#     main()



# import os
# import logging
# import time
# from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
# from webdriver_manager.firefox import GeckoDriverManager
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.proxy import Proxy, ProxyType

# # Logging setup
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('waterfox_geonode.log'),
#         logging.StreamHandler()
#     ]
# )

# # GeoNode Proxy Configuration
# GEONODE_PROXY_TEMPLATE = {
#     "mode": "socks5",
#     "host": "sg.proxy.geonode.io",
#     "port": 11000,
#     "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#     "password": "CHANGE_ME_PASSWORD"
# }

# # Target URL
# TARGET_URL = "https://www.skyscanner.co.in/"

# def setup_waterfox_with_geonode():
#     """Setup Waterfox browser with GeoNode proxy configuration"""
    
#     # Waterfox binary path (from your existing script)
#     waterfox_path = r"C:\Users\HP\Downloads\Scrap\Waterfox\waterfox.exe"
    
#     # Firefox options
#     options = Options()
    
#     # Check if Waterfox exists, otherwise fallback to Firefox
#     if not os.path.exists(waterfox_path):
#         logging.error(f"Waterfox binary not found at {waterfox_path}. Falling back to standard Firefox.")
#         options.binary_location = ""
#     else:
#         options.binary_location = waterfox_path
#         logging.info(f"Using Waterfox from: {waterfox_path}")
    
#     # Non-headless mode (browser window visible)
#     # options.add_argument('--headless')  # Commented out for non-headless mode
    
#     # Additional options for better proxy handling
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
    
#     # Setup proxy configuration
#     proxy = Proxy()
#     proxy.proxy_type = ProxyType.MANUAL
    
#     # Configure SOCKS5 proxy
#     proxy.socks_proxy = f"{GEONODE_PROXY_TEMPLATE['host']}:{GEONODE_PROXY_TEMPLATE['port']}"
#     proxy.socks_version = 5
    
#     # Set proxy username and password in preferences
#     options.set_preference("network.proxy.type", 1)  # Manual proxy
#     options.set_preference("network.proxy.socks", GEONODE_PROXY_TEMPLATE['host'])
#     options.set_preference("network.proxy.socks_port", GEONODE_PROXY_TEMPLATE['port'])
#     options.set_preference("network.proxy.socks_version", 5)
#     options.set_preference("network.proxy.socks_username", GEONODE_PROXY_TEMPLATE['username'])
#     options.set_preference("network.proxy.socks_password", GEONODE_PROXY_TEMPLATE['password'])
    
#     # Additional proxy settings
#     options.set_preference("network.proxy.socks_remote_dns", True)
#     options.set_preference("network.proxy.no_proxies_on", "")
    
#     # User agent (optional)
#     options.set_preference("general.useragent.override", 
#                           "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    
#     return options, proxy

# def init_driver_with_proxy():
#     """Initialize WebDriver with proxy configuration"""
#     try:
#         options, proxy = setup_waterfox_with_geonode()
        
#         # Create capabilities and add proxy
#         capabilities = webdriver.DesiredCapabilities.FIREFOX.copy()
#         proxy.add_to_capabilities(capabilities)
        
#         # Initialize driver
#         driver = webdriver.Firefox(
#             service=Service(GeckoDriverManager().install()),
#             options=options,
#             desired_capabilities=capabilities
#         )
        
#         logging.info("WebDriver initialized successfully with GeoNode proxy")
#         return driver
        
#     except Exception as e:
#         logging.error(f"WebDriver initialization failed: {str(e)}")
#         logging.info("Trying without proxy...")
        
#         # Fallback without proxy
#         options = Options()
#         if os.path.exists(r"C:\Users\HP\Downloads\Scrap\Waterfox\waterfox.exe"):
#             options.binary_location = r"C:\Users\HP\Downloads\Scrap\Waterfox\waterfox.exe"
        
#         driver = webdriver.Firefox(
#             service=Service(GeckoDriverManager().install()),
#             options=options
#         )
#         return driver

# def test_proxy_connection(driver):
#     """Test proxy connection by checking IP"""
#     try:
#         logging.info("Testing proxy connection...")
#         driver.get("https://httpbin.org/ip")
#         time.sleep(5)
        
#         # Get IP information
#         ip_info = driver.find_element("tag name", "body").text
#         logging.info(f"Current IP info: {ip_info}")
        
#         return True
#     except Exception as e:
#         logging.warning(f"Proxy test failed: {str(e)}")
#         return False

# def open_target_url(driver):
#     """Open the target URL"""
#     try:
#         logging.info(f"Opening target URL: {TARGET_URL}")
#         driver.get(TARGET_URL)
#         time.sleep(10)  # Wait for page to load
        
#         # Get page title
#         page_title = driver.title
#         logging.info(f"Page loaded successfully. Title: {page_title}")
        
#         return True
#     except Exception as e:
#         logging.error(f"Failed to open target URL: {str(e)}")
#         return False

# def main():
#     """Main function"""
#     driver = None
    
#     try:
#         # Initialize driver with proxy
#         driver = init_driver_with_proxy()
        
#         # Test proxy connection
#         proxy_working = test_proxy_connection(driver)
#         if proxy_working:
#             logging.info("Proxy connection successful!")
#         else:
#             logging.warning("Proxy connection test failed, but continuing...")
        
#         # Open target URL
#         success = open_target_url(driver)
        
#         if success:
#             logging.info("Script executed successfully!")
#             logging.info("Browser window will remain open. Press Ctrl+C to close.")
            
#             # Keep browser open until user interrupts
#             try:
#                 while True:
#                     time.sleep(10)
#             except KeyboardInterrupt:
#                 logging.info("User interrupted. Closing browser...")
        
#     except Exception as e:
#         logging.error(f"Script execution failed: {str(e)}")
    
#     finally:
#         # Clean up
#         if driver:
#             driver.quit()
#             logging.info("WebDriver closed.")

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         logging.info("Script interrupted by user.")
#     except Exception as e:
#         logging.error(f"Unexpected error: {str(e)}")



# from seleniumwire import webdriver
# from selenium.webdriver.chrome.options import Options
# import json

# # Geonode proxy details
# proxy_host = "sg.proxy.geonode.io"
# proxy_port = 11000
# proxy_username = "geonode_xvmYN44Bvz-type-residential-country-in"
# proxy_password = "CHANGE_ME_PASSWORD"

# # Target URL
# target_url = "https://www.skyscanner.co.in/"

# # Proxy settings for selenium-wire
# proxy_options = {
#     'proxy': {
#         'http': f'socks5://{proxy_username}:CHANGE_ME_PASSWORD@{proxy_host}:{proxy_port}',
#         'https': f'socks5://{proxy_username}:CHANGE_ME_PASSWORD@{proxy_host}:{proxy_port}',
#         'no_proxy': 'localhost,127.0.0.1'
#     }
# }

# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--log-level=3')
# chrome_options.add_argument('--disable-extensions')
# chrome_options.add_argument('--disable-sync')
# chrome_options.add_argument('--disable-notifications')

# # Initialize Chrome WebDriver with selenium-wire
# driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=proxy_options)

# try:
#     # Check IP address to confirm proxy
#     driver.get("https://httpbin.org/ip")
#     ip_element = driver.find_element_by_tag_name("pre")
#     ip_data = json.loads(ip_element.text)
#     print(f"IP Address via Proxy: {ip_data['origin']}")

#     # Navigate to the target URL
#     driver.get(target_url)
#     print(f"Successfully accessed {target_url}")
    
#     # Print page title to confirm
#     print("Page Title:", driver.title)
    
#     # Save a screenshot
#     driver.save_screenshot("skyscanner_screenshot.png")
#     print("Screenshot saved as skyscanner_screenshot.png")

# except Exception as e:
#     print(f"An error occurred: {e}")

# finally:
#     # Keep browser open for 10 seconds to observe
#     import time
#     time.sleep(10)
#     # Close the browser
#     driver.quit()


# from seleniumwire import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# import json

# # Geonode proxy details
# proxy_host = "sg.proxy.geonode.io"
# proxy_port = 11000
# proxy_username = "geonode_xvmYN44Bvz-type-residential-country-in"
# proxy_password = "CHANGE_ME_PASSWORD"

# # Target URL
# target_url = "https://www.skyscanner.co.in/"

# # Proxy settings for selenium-wire
# proxy_options = {
#     'proxy': {
#         'http': f'socks5://{proxy_username}:CHANGE_ME_PASSWORD@{proxy_host}:{proxy_port}',
#         'https': f'socks5://{proxy_username}:CHANGE_ME_PASSWORD@{proxy_host}:{proxy_port}',
#         'no_proxy': 'localhost,127.0.0.1'
#     }
# }

# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--log-level=3')
# chrome_options.add_argument('--disable-extensions')
# chrome_options.add_argument('--disable-sync')
# chrome_options.add_argument('--disable-notifications')

# # Initialize Chrome WebDriver with selenium-wire
# driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=proxy_options)

# try:
#     # Check IP address to confirm proxy
#     driver.get("https://httpbin.org/ip")
#     ip_element = driver.find_element(By.TAG_NAME, "pre")
#     ip_data = json.loads(ip_element.text)
#     print(f"Current Proxy IP: {ip_data['origin']} (via Geonode proxy)")

#     # Navigate to the target URL
#     driver.get(target_url)
#     print(f"Successfully accessed {target_url}")
    
#     # Print page title to confirm
#     print("Page Title:", driver.title)
    
#     # Save a screenshot
#     driver.save_screenshot("skyscanner_screenshot.png")
#     print("Screenshot saved as skyscanner_screenshot.png")

# except Exception as e:
#     print(f"An error occurred: {e}")

# finally:
#     # Keep browser open for 10 seconds to observe
#     import time
#     time.sleep(10)
#     # Close the browser
#     driver.quit()



# waterfox and geonode script running sucessfully
# import os
# import logging
# import time
# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service
# from webdriver_manager.firefox import GeckoDriverManager
# from selenium.webdriver.common.by import By
# import json

# # Logging setup
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('waterfox_geonode.log'),
#         logging.StreamHandler()
#     ]
# )

# # Geonode Proxy Configuration
# GEONODE_PROXY_TEMPLATE = {
#     "host": "sg.proxy.geonode.io",
#     "port": 11000,
#     "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#     "password": "CHANGE_ME_PASSWORD"
# }

# # Target URL
# TARGET_URL = "https://www.skyscanner.co.in/"

# def setup_waterfox_with_geonode():
#     """Setup Waterfox browser with GeoNode proxy configuration"""
#     # Waterfox binary path
#     waterfox_path = r"C:\Users\HP\Downloads\Scrap\Waterfox\waterfox.exe"
    
#     # Firefox options
#     options = Options()
    
#     # Check if Waterfox exists, otherwise fallback to Firefox
#     if not os.path.exists(waterfox_path):
#         logging.error(f"Waterfox binary not found at {waterfox_path}. Falling back to standard Firefox.")
#         options.binary_location = ""
#     else:
#         options.binary_location = waterfox_path
#         logging.info(f"Using Waterfox from: {waterfox_path}")
    
#     # Non-headless mode
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
    
#     # User agent (optional, matching your script)
#     options.set_preference("general.useragent.override", 
#                           "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    
#     # Proxy settings for selenium-wire
#     proxy_options = {
#         'proxy': {
#             'http': f'socks5://{GEONODE_PROXY_TEMPLATE["username"]}:{GEONODE_PROXY_TEMPLATE["password"]}@{GEONODE_PROXY_TEMPLATE["host"]}:{GEONODE_PROXY_TEMPLATE["port"]}',
#             'https': f'socks5://{GEONODE_PROXY_TEMPLATE["username"]}:{GEONODE_PROXY_TEMPLATE["password"]}@{GEONODE_PROXY_TEMPLATE["host"]}:{GEONODE_PROXY_TEMPLATE["port"]}',
#             'no_proxy': 'localhost,127.0.0.1'
#         }
#     }
    
#     return options, proxy_options

# def init_driver_with_proxy():
#     """Initialize WebDriver with proxy configuration"""
#     try:
#         options, proxy_options = setup_waterfox_with_geonode()
        
#         # Initialize driver with selenium-wire
#         driver = webdriver.Firefox(
#             service=Service(GeckoDriverManager().install()),
#             options=options,
#             seleniumwire_options=proxy_options
#         )
        
#         logging.info("WebDriver initialized successfully with GeoNode proxy")
#         return driver
        
#     except Exception as e:
#         logging.error(f"WebDriver initialization failed: {str(e)}")
#         logging.info("Trying without proxy...")
        
#         # Fallback without proxy
#         options = Options()
#         if os.path.exists(r"C:\Users\HP\Downloads\Scrap\Waterfox\waterfox.exe"):
#             options.binary_location = r"C:\Users\HP\Downloads\Scrap\Waterfox\waterfox.exe"
        
#         driver = webdriver.Firefox(
#             service=Service(GeckoDriverManager().install()),
#             options=options
#         )
#         return driver

# def test_proxy_connection(driver):
#     """Test proxy connection by checking IP"""
#     try:
#         logging.info("Testing proxy connection...")
#         driver.get("https://httpbin.org/ip")
#         time.sleep(5)
        
#         # Get IP information
#         ip_element = driver.find_element(By.TAG_NAME, "pre")
#         ip_data = json.loads(ip_element.text)
#         logging.info(f"Current Proxy IP: {ip_data['origin']} (via Geonode proxy)")
        
#         return True
#     except Exception as e:
#         logging.warning(f"Proxy test failed: {str(e)}")
#         return False

# def open_target_url(driver):
#     """Open the target URL"""
#     try:
#         logging.info(f"Opening target URL: {TARGET_URL}")
#         driver.get(TARGET_URL)
#         time.sleep(5)  # Wait for page to load
        
#         # Get page title
#         page_title = driver.title
#         logging.info(f"Page loaded successfully. Title: {page_title}")
        
#         # Save a screenshot
#         driver.save_screenshot("skyscanner_screenshot.png")
#         logging.info("Screenshot saved as skyscanner_screenshot.png")
        
#         return True
#     except Exception as e:
#         logging.error(f"Failed to open target URL: {str(e)}")
#         return False

# def main():
#     """Main function"""
#     driver = None
    
#     try:
#         # Initialize driver with proxy
#         driver = init_driver_with_proxy()
        
#         # Test proxy connection
#         proxy_working = test_proxy_connection(driver)
#         if proxy_working:
#             logging.info("Proxy connection successful!")
#         else:
#             logging.warning("Proxy connection test failed, but continuing...")
        
#         # Open target URL
#         success = open_target_url(driver)
        
#         if success:
#             logging.info("Script executed successfully!")
        
#     except Exception as e:
#         logging.error(f"Script execution failed: {str(e)}")
    
#     finally:
#         # Keep browser open for 10 seconds
#         if driver:
#             logging.info("Keeping browser open for 10 seconds...")
#             time.sleep(10)
#             driver.quit()
#             logging.info("WebDriver closed.")

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         logging.info("Script interrupted by user.")
#     except Exception as e:
#         logging.error(f"Unexpected error: {str(e)}")





from gologin import GoLogin

gl = GoLogin({
    "token": "CHANGE_ME_TOKEN",
    "profile_id": "68d62cb00c1a88ab4472c08e"
})

# Browser start karo
debugger_address = gl.start()
print("Browser started at:", debugger_address)

# Automation ke liye selenium ya playwright connect kar sakte ho
# Example: Selenium with Chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.debugger_address = debugger_address

driver = webdriver.Chrome(service=Service(gl.driver_path), options=chrome_options)
driver.get("https://httpbin.org/ip")  # test karo ki IP aur fingerprint alag h
print(driver.page_source)

# Jab kaam ho jaye
driver.quit()
gl.stop()
