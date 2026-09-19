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


def setup_logging():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(base_dir, 'error_log.txt')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logging()

# === Path helper for PyInstaller or normal run ===
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# === Read tokens from tokens.txt ===
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

CHROMEDRIVER_PATH = resource_path("chromedriver")  # Use linux chromedriver binary path

PROXY_TEMPLATE = {
    "mode": "socks5",
    "host": "92.204.164.15",
    "port": 11001,
    "username": "geonode_xvmYN44Bvz",
    "password": "CHANGE_ME_PASSWORD"
}

URLS = [
    "https://marcadeo.com/",
    "https://marcadeo.in/"
]

total_runs = 20
concurrent_processes =2

def run_profile(run_index, token):
    logging.info(f"Starting profile #{run_index + 1}")
    gl = GoLogin({
        "token": token,
        "executablePath": "orbita-browser/chrome",
        "extra_params": [
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-features=Vulkan",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--headless=new"
        ],
        "verbose": True  # Enable verbose logging for debugging
    })
    try:
        profile_id = gl.createProfileWithCustomParams({
            "name": f"auto-profile-{run_index + 1}",
            "os": "lin",
 #           "chromeVersion": "134",
            "navigator": {
                "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "resolution": "1920x1080",
                "language": "en-US",
                "platform": "Linux x86_64"
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
        chrome_options.add_argument("--headless=new")  # Headless for Selenium
        chrome_options.add_argument("--disable-gpu")   # Disable GPU
  #      chrome_options.add_argument("--window-size=1920,1080")  # Set window size
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Rest of the code remains the same
        for _ in range(2):
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            target_url = random.choice(URLS)
            print(f"Profile #{run_index + 1} visiting URL: {target_url}")
            driver.get(target_url)

            time.sleep(5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            buttons = driver.find_elements(By.XPATH, "//div[@class='hmvrCard']//a[contains(text(), 'Apply Now')]")
            if buttons:
                chosen_button = random.choice(buttons)
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", chosen_button)
                time.sleep(2)
                ActionChains(driver).move_to_element(chosen_button).perform()
                time.sleep(2)
                chosen_button.click()
                print(f"Clicked a random Apply Now button for profile #{run_index + 1}")
            else:
                print(f"No 'Apply Now' buttons found for profile #{run_index + 1}")

            time.sleep(5)

        driver.quit()

    except Exception as e:
        logging.error(f"[ERROR #{run_index + 1}]: {e}", exc_info=True)
    finally:
        try:
            gl.stop()
        except Exception as e:
            logging.error(f"Error stopping profile #{run_index + 1}: {e}")
        logging.info(f"Stopped profile #{run_index + 1}")

def run_all_profiles():
    pool = multiprocessing.Pool(processes=concurrent_processes)
    tasks = []

    for i in range(total_runs):
        token_index = i //500 % len(TOKENS)
        token = TOKENS[token_index]
        tasks.append(pool.apply_async(run_profile, args=(i, token)))

    pool.close()
    pool.join()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    logging.info("=== Script Started ===")
    run_all_profiles()
    logging.info("✅ All profile runs completed.")