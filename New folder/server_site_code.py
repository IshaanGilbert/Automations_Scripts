# import time
# import random
# import json
# import multiprocessing
# import os 
# import sys
# import logging
# from gologin import GoLogin
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By


# def setup_logging():
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     log_path = os.path.join(base_dir, 'error_log.txt')
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler(log_path, mode='a', encoding='utf-8'),
#             logging.StreamHandler(sys.stdout)
#         ]
#     )

# setup_logging()

# # === Path helper for PyInstaller or normal run ===
# def resource_path(relative_path):
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)

# # === Read tokens from tokens.txt ===
# def load_tokens():
#     tokens_path = resource_path("tokens.txt")
#     if not os.path.exists(tokens_path):
#         logging.error("tokens.txt file not found!")
#         return []
#     with open(tokens_path, "r") as f:
#         tokens = [line.strip() for line in f if line.strip()]
#     logging.info(f"Loaded {len(tokens)} tokens.")
#     return tokens

# TOKENS = load_tokens()
# if not TOKENS:
#     logging.error("No tokens loaded. Exiting.")
#     sys.exit(1)

# CHROMEDRIVER_PATH = resource_path("chromedriver")  # Use linux chromedriver binary path

# PROXY_TEMPLATE = {
#     "mode": "socks5",
#     "host": "92.204.164.15",
#     "port": 11001,
#     "username": "geonode_xvmYN44Bvz",
#     "password": "CHANGE_ME_PASSWORD"
# }

# URLS = [
#     "https://marcadeo.com/",
#     "https://unfilteredgadgets.com/",
#     "https://marcadeo.in/"
# ]

# total_runs = 300
# concurrent_processes = 30

# def run_profile(run_index, token):
#     logging.info(f"Starting profile #{run_index + 1}")
#     gl = GoLogin({
#         "token": token,
#         "executablePath": "orbita-browser/chrome",
#         "extra_params": [
#         "--disable-gpu",
#         "--disable-software-rasterizer",
#         "--disable-features=Vulkan",
#         "--disable-dev-shm-usage",
#         "--no-sandbox",
#         "--headless=new"
#         ],
#         "verbose": True  # Enable verbose logging for debugging
#     })
#     try:
#         profile_id = gl.createProfileWithCustomParams({
#             "name": f"auto-profile-{run_index + 1}",
#             "os": "lin",
#  #           "chromeVersion": "134",
#             "navigator": {
#                 "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
#                 "resolution": "1920x1080",
#                 "language": "en-US",
#                 "platform": "Linux x86_64"
#             },
#             "proxyEnabled": True,
#             "proxy": PROXY_TEMPLATE
#         })
#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()

#         service = Service(CHROMEDRIVER_PATH)
#         chrome_options = webdriver.ChromeOptions()
#         chrome_options.add_experimental_option("debuggerAddress", debugger_address)
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--headless=new")  # Headless for Selenium
#         chrome_options.add_argument("--disable-gpu")   # Disable GPU
#         chrome_options.add_argument("--window-size=1920,1080")  # Set window size
#         driver = webdriver.Chrome(service=service, options=chrome_options)

#         # Rest of the code remains the same
#         for _ in range(2):
#             driver.execute_script("window.open('');")
#             driver.switch_to.window(driver.window_handles[-1])
#             target_url = random.choice(URLS)
#             print(f"Profile #{run_index + 1} visiting URL: {target_url}")
#             driver.get(target_url)

#             time.sleep(5)
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(3)

#             buttons = driver.find_elements(By.XPATH, "//div[@class='hmvrCard']//a[contains(text(), 'Apply Now')]")
#             if buttons:
#                 chosen_button = random.choice(buttons)
#                 driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", chosen_button)
#                 time.sleep(2)
#                 ActionChains(driver).move_to_element(chosen_button).perform()
#                 time.sleep(2)
#                 chosen_button.click()
#                 print(f"Clicked a random Apply Now button for profile #{run_index + 1}")
#             else:
#                 print(f"No 'Apply Now' buttons found for profile #{run_index + 1}")

#             time.sleep(5)

#         driver.quit()

#     except Exception as e:
#         logging.error(f"[ERROR #{run_index + 1}]: {e}", exc_info=True)
#     finally:
#         try:
#             gl.stop()
#         except Exception as e:
#             logging.error(f"Error stopping profile #{run_index + 1}: {e}")
#         logging.info(f"Stopped profile #{run_index + 1}")

# def run_all_profiles():
#     pool = multiprocessing.Pool(processes=concurrent_processes)
#     tasks = []

#     for i in range(total_runs):
#         token_index = i // 1000 % len(TOKENS)
#         token = TOKENS[token_index]
#         tasks.append(pool.apply_async(run_profile, args=(i, token)))

#     pool.close()
#     pool.join()

# if __name__ == '__main__':
#     multiprocessing.freeze_support()
#     logging.info("=== Script Started ===")
#     run_all_profiles()
#     logging.info("✅ All profile runs completed.")


# import time
# import random
# import json
# import multiprocessing
# import os 
# import sys
# import logging
# from gologin import GoLogin
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By


# def setup_logging():
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     log_path = os.path.join(base_dir, 'error_log.txt')
#     visited_urls_path = os.path.join(base_dir, 'visited_urls.txt')  # New file for visited URLs
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler(log_path, mode='a', encoding='utf-8'),
#             logging.StreamHandler(sys.stdout)
#         ]
#     )
#     # Setup separate logger for visited URLs
#     visited_urls_logger = logging.getLogger('visited_urls')
#     visited_urls_logger.setLevel(logging.INFO)
#     visited_urls_handler = logging.FileHandler(visited_urls_path, mode='a', encoding='utf-8')
#     visited_urls_handler.setFormatter(logging.Formatter('%(asctime)s - Profile #%(profile_id)s - Visited URL: %(message)s'))
#     visited_urls_logger.addHandler(visited_urls_handler)
#     return visited_urls_logger

# visited_urls_logger = setup_logging()

# # === Path helper for PyInstaller or normal run ===
# def resource_path(relative_path):
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)

# # === Read tokens from tokens.txt ===
# def load_tokens():
#     tokens_path = resource_path("tokens.txt")
#     if not os.path.exists(tokens_path):
#         logging.error("tokens.txt file not found!")
#         return []
#     with open(tokens_path, "r") as f:
#         tokens = [line.strip() for line in f if line.strip()]
#     logging.info(f"Loaded {len(tokens)} tokens.")
#     return tokens

# TOKENS = load_tokens()
# if not TOKENS:
#     logging.error("No tokens loaded. Exiting.")
#     sys.exit(1)

# CHROMEDRIVER_PATH = resource_path("Chromedriver/chromedriver.exe")  # ChromeDriver in project folder
# CHROME_BINARY_PATH = resource_path("Chrome/chrome.exe")  # Chrome binary in project folder's 'chrome' subfolder
# logging.info(f"ChromeDriver path: {CHROMEDRIVER_PATH}")
# logging.info(f"Chrome binary path: {CHROME_BINARY_PATH}")

# PROXY_TEMPLATE = {
#     "mode": "socks5",
#     "host": "92.204.164.15",
#     "port": 11001,
#     "username": "geonode_xvmYN44Bvz",
#     "password": "CHANGE_ME_PASSWORD"
# }

# URLS = [
#     "https://marcadeo.com/",
#     "https://unfilteredgadgets.com/",
#     "https://marcadeo.in/"
# ]

# total_runs = 10
# concurrent_processes = 5

# def run_profile(run_index, token):
#     logging.info(f"Starting profile #{run_index + 1}")
#     gl = GoLogin({
#         "token": token,
#         "executablePath": "/home/ubuntu/ishan/orbita-browser/chromium-browser",  # Corrected path
#         "extra_params": [
#             "--disable-gpu",
#             "--disable-software-rasterizer",
#             "--disable-features=Vulkan",
#             "--disable-dev-shm-usage",
#             "--no-sandbox",
#             "--headless=new"
#         ],
#         "verbose": True
#     })
#     try:
#         profile_id = gl.createProfileWithCustomParams({
#             "name": f"auto-profile-{run_index + 1}",
#             "os": "win",
#             "navigator": {
#                 "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
#                 "resolution": "1920x1080",
#                 "language": "en-US",
#                 "platform": "Win32"
#             },
#             "proxyEnabled": True,
#             "proxy": PROXY_TEMPLATE
#         })
#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()

#         # service = Service(CHROMEDRIVER_PATH)
#         # chrome_options = webdriver.ChromeOptions()
#         # chrome_options.add_experimental_option("debuggerAddress", debugger_address)
#         # chrome_options.add_argument("--no-sandbox")
#         # chrome_options.add_argument("--disable-dev-shm-usage")
#         # chrome_options.add_argument("--headless=new")
#         # chrome_options.add_argument("--disable-gpu")
#         # chrome_options.add_argument("--window-size=1920,1080")
#         # driver = webdriver.Chrome(service=service, options=chrome_options)
#         service = Service(CHROMEDRIVER_PATH)
#         chrome_options = webdriver.ChromeOptions()
#         chrome_options.binary_location = CHROME_BINARY_PATH  # Specify Chrome binary location
#         chrome_options.add_experimental_option("debuggerAddress", debugger_address)
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         driver = webdriver.Chrome(service=service, options=chrome_options)

#         # Visit all URLs in separate tabs
#         for i, target_url in enumerate(URLS):
#             if i == 0:
#                 driver.get(target_url)  # Use first tab for first URL
#             else:
#                 driver.execute_script("window.open('');")
#                 driver.switch_to.window(driver.window_handles[-1])
#                 driver.get(target_url)
            
#             print(f"Profile #{run_index + 1} visiting URL: {target_url}")
#             visited_urls_logger.info(target_url, extra={'profile_id': run_index + 1})

#             time.sleep(5)
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(3)

#             buttons = driver.find_elements(By.XPATH, "//div[@class='hmvrCard']//a[contains(text(), 'Apply Now')]")
#             if buttons:
#                 chosen_button = random.choice(buttons)
#                 driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", chosen_button)
#                 time.sleep(2)
#                 ActionChains(driver).move_to_element(chosen_button).perform()
#                 time.sleep(2)
#                 chosen_button.click()
#                 print(f"Clicked a random Apply Now button for profile #{run_index + 1}")
#             else:
#                 print(f"No 'Apply Now' buttons found for profile #{run_index + 1}")

#             time.sleep(5)

#         driver.quit()

#     except Exception as e:
#         logging.error(f"[ERROR #{run_index + 1}]: {e}", exc_info=True)
#     finally:
#         try:
#             gl.stop()
#         except Exception as e:
#             logging.error(f"Error stopping profile #{run_index + 1}: {e}")
#         logging.info(f"Stopped profile #{run_index + 1}")

# def run_all_profiles():
#     pool = multiprocessing.Pool(processes=concurrent_processes)
#     tasks = []

#     for i in range(total_runs):
#         token_index = i // 1000 % len(TOKENS)
#         token = TOKENS[token_index]
#         tasks.append(pool.apply_async(run_profile, args=(i, token)))

#     pool.close()
#     pool.join()

# if __name__ == '__main__':
#     multiprocessing.freeze_support()
#     logging.info("=== Script Started ===")
#     run_all_profiles()
#     logging.info("✅ All profile runs completed.")



import time
import random
import json
import multiprocessing
import os
import sys
import logging
from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import psutil
import shutil

# Logging Setup
def setup_logging():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(base_dir, 'error_log.txt')
    visited_urls_path = os.path.join(base_dir, 'visited_urls.txt')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    visited_urls_logger = logging.getLogger('visited_urls')
    visited_urls_logger.setLevel(logging.INFO)
    visited_handler = logging.FileHandler(visited_urls_path, mode='a', encoding='utf-8')
    visited_handler.setFormatter(logging.Formatter('%(asctime)s - Profile #%(profile_id)s - Visited URL: %(message)s'))
    visited_urls_logger.addHandler(visited_handler)
    
    return visited_urls_logger

visited_urls_logger = setup_logging()

# Path Helper
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load Tokens
def load_tokens():
    tokens_path = resource_path("tokens.txt")
    if not os.path.exists(tokens_path):
        logging.error("tokens.txt file not found!")
        return []
    with open(tokens_path, "r") as f:
        tokens = [line.strip() for line in f if line.strip()]
    logging.info(f"Loaded {len(tokens)} tokens.")
    return tokens

TOKENS = load_tokens()
if not TOKENS:
    logging.error("No tokens loaded. Exiting.")
    sys.exit(1)

CHROMEDRIVER_PATH = resource_path("Chromedriver/chromedriver.exe")
BROWSER_PATH = resource_path("Chrome/chrome.exe")

PROXY_TEMPLATE = {
    "mode": "socks5",
    "host": "92.204.164.15",
    "port": 11001,
    "username": "geonode_xvmYN44Bvz",
    "password": "CHANGE_ME_PASSWORD"
}

URLS = [
    "https://marcadeo.com/",
    "https://unfilteredgadgets.com/",
    "https://marcadeo.in/"
]

total_runs = 10
MAX_CONCURRENT = min(5, os.cpu_count() * 2)  # Reduced for Windows stability

# Dynamic Concurrency
def get_dynamic_concurrent():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    if cpu_usage > 80 or memory_usage > 80:
        return max(1, MAX_CONCURRENT // 2)
    return MAX_CONCURRENT

# Run Profile Logic
def run_profile(run_index, token):
    logging.info(f"Starting profile #{run_index + 1}")
    temp_profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"gologin_temp_{run_index}")
    
    gl = GoLogin({
        "token": token,
        "executablePath": BROWSER_PATH,
        "profilePath": temp_profile_dir,
        "extra_params": [
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-features=Vulkan",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--headless=new",
            "--disable-background-networking",
            "--disable-client-side-phishing-detection",
            "--disable-sync"
        ],
        "verbose": False
    })

    try:
        # Verify paths
        if not os.path.exists(BROWSER_PATH):
            logging.error(f"Browser executable not found at {BROWSER_PATH}")
            return
        if not os.path.exists(CHROMEDRIVER_PATH):
            logging.error(f"Chromedriver not found at {CHROMEDRIVER_PATH}")
            return
        logging.info(f"ChromeDriver path: {CHROMEDRIVER_PATH}")
        logging.info(f"Chrome binary path: {BROWSER_PATH}")

        profile_id = gl.createProfileWithCustomParams({
            "name": f"auto-profile-{run_index + 1}",
            "os": "win",
            "navigator": {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "resolution": "1920x1080",
                "language": "en-US",
                "platform": "Win32"
            },
            "proxyEnabled": True,
            "proxy": PROXY_TEMPLATE
        })
        gl.setProfileId(profile_id)
        debugger_address = gl.start()

        service = Service(CHROMEDRIVER_PATH)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-client-side-phishing-detection")

        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15)

        # Visit all URLs with retry logic
        max_attempts = 3
        for i, target_url in enumerate(URLS):
            for attempt in range(max_attempts):
                try:
                    if i == 0:
                        driver.get(target_url)
                    else:
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.get(target_url)
                    
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    visited_urls_logger.info(target_url, extra={'profile_id': run_index + 1})
                    print(f"Profile #{run_index + 1} visiting URL: {target_url}")

                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    # Try multiple XPaths for buttons
                    xpaths = [
                        "//div[@class='hmvrCard']//a[contains(text(), 'Apply Now')]",
                        "//a[contains(text(), 'Apply')]",
                        "//button[contains(text(), 'Apply Now')]",
                        "//a[contains(text(), 'Shop')]"  # Added for testing
                    ]
                    button_found = False
                    for xpath in xpaths:
                        buttons = driver.find_elements(By.XPATH, xpath)
                        if buttons:
                            button_found = True
                            chosen_button = random.choice(buttons)
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", chosen_button)
                            wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            ActionChains(driver).move_to_element(chosen_button).click().perform()
                            print(f"Profile #{run_index + 1} clicked a button with XPath: {xpath}")
                            break
                    if not button_found:
                        print(f"Profile #{run_index + 1} found no clickable buttons for URL: {target_url}")
                    
                    break
                except Exception as e:
                    logging.error(f"Attempt {attempt + 1} failed for URL {target_url} in profile #{run_index + 1}: {e}")
                    if attempt == max_attempts - 1:
                        logging.error(f"Max attempts reached for URL {target_url} in profile #{run_index + 1}")
                    time.sleep(2)
            time.sleep(1)

        driver.quit()

    except Exception as e:
        logging.error(f"[ERROR #{run_index + 1}]: {e}", exc_info=True)
    finally:
        try:
            gl.stop()
            if os.path.exists(temp_profile_dir):
                shutil.rmtree(temp_profile_dir, ignore_errors=True)
        except Exception as e:
            logging.error(f"Error stopping profile #{run_index + 1}: {e}")
        logging.info(f"Stopped profile #{run_index + 1}")

# Run in Batches
def run_in_batches():
    batch_size = get_dynamic_concurrent()
    total_batches = (total_runs + batch_size - 1) // batch_size

    for batch_index in range(total_batches):
        logging.info(f"Starting batch {batch_index + 1}/{total_batches}")
        start = batch_index * batch_size
        end = min(start + batch_size, total_runs)
        tasks = []

        current_concurrent = get_dynamic_concurrent()
        with ThreadPoolExecutor(max_workers=current_concurrent) as executor:
            for i in range(start, end):
                token_index = i % len(TOKENS)
                token = TOKENS[token_index]
                tasks.append(executor.submit(run_profile, i, token))
        
        logging.info(f"Finished batch {batch_index + 1}/{total_batches}")
        time.sleep(1)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    logging.info("=== Script Started ===")
    run_in_batches()
    logging.info("✅ All profile runs completed.")