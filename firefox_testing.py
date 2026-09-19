import os
import json
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("selenium_proxy.log"),
        logging.StreamHandler()
    ]
)

# Geonode credentials
GEONODE_USERNAME = "geonode_xvmYN44Bvz-type-residential-country-in"
GEONODE_PASSWORD = "CHANGE_ME_PASSWORD"
GEONODE_PROXY_SERVER = "sg.proxy.geonode.io:11000"

# Target URLs
BASE_URLS = [
    "https://example.com",
    "https://example.org"
]

def verify_proxy_connection():
    """Test if the proxy is working before launching browser"""
    import requests
    from urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter

    print("Verifying proxy connection...")
    proxy_host, proxy_port = GEONODE_PROXY_SERVER.split(":")
    proxies = {
        'http': f'socks5h://{GEONODE_USERNAME}:CHANGE_ME_PASSWORD@{proxy_host}:{proxy_port}',
        'https': f'socks5h://{GEONODE_USERNAME}:CHANGE_ME_PASSWORD@{proxy_host}:{proxy_port}'
    }

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1)
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get('https://api.ipify.org?format=json', proxies=proxies, timeout=15)
        if response.status_code == 200:
            ip_data = response.json()
            print(f"Proxy connection successful. IP: {ip_data['ip']}")
            logging.info(f"Proxy connection successful. IP: {ip_data['ip']}")
            return True, ip_data['ip']
        else:
            print(f"Proxy verification failed: HTTP {response.status_code}")
            logging.error(f"Proxy verification failed: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        print(f"Proxy verification failed: {str(e)}")
        logging.error(f"Proxy verification failed: {str(e)}")
        return False, None

def init_selenium_firefox():
    """Initialize Selenium with Firefox and SOCKS5 proxy"""
    print("Initializing Selenium Firefox...")
    proxy_host, proxy_port = GEONODE_PROXY_SERVER.split(":")
    print(f"Proxy host: {proxy_host}, port: {proxy_port}")

    try:
        # Create a Firefox profile for proxy settings
        firefox_profile = FirefoxProfile()
        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("network.proxy.socks", proxy_host)
        firefox_profile.set_preference("network.proxy.socks_port", int(proxy_port))
        firefox_profile.set_preference("network.proxy.socks_version", 5)
        firefox_profile.set_preference("network.proxy.socks_remote_dns", True)
        firefox_profile.set_preference("network.proxy.no_proxies_on", "localhost, 127.0.0.1")
        # Set user agent
        firefox_profile.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0"
        )
        # Set geolocation
        firefox_profile.set_preference(
            "geo.provider.network.url",
            'data:application/json,{"location": {"lat": 20.5937, "lng": 78.9629}}'
        )
        firefox_profile.set_preference("geo.enabled", True)
        # Disable WebDriver detection
        firefox_profile.set_preference("dom.webdriver.enabled", False)
        firefox_profile.set_preference("useAutomationExtension", False)

        # Configure Firefox options
        firefox_options = Options()
        firefox_options.headless = False  # Set to True for headless mode
        firefox_options.profile = firefox_profile
        firefox_options.add_argument("--disable-gpu")
        firefox_options.add_argument("--no-sandbox")

        print("Launching Firefox browser...")
        driver = webdriver.Firefox(options=firefox_options)
        driver.set_window_size(1366, 768)

        print("Navigating to IP check...")
        driver.get('https://api.ipify.org?format=json')
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            ip_data = json.loads(driver.find_element(By.TAG_NAME, "body").text)
            print(f"Browser is using IP: {ip_data['ip']}")
            logging.info(f"Browser is using IP: {ip_data['ip']}")
        except Exception as e:
            print(f"IP check failed: {str(e)}")
            logging.error(f"IP check failed: {str(e)}")
            raise
        return driver
    except Exception as e:
        print(f"Failed to initialize Selenium Firefox: {str(e)}")
        logging.error(f"Failed to initialize Selenium Firefox: {str(e)}")
        raise

def random_behavior(driver):
    """Simulate human-like random behavior"""
    try:
        actions = ActionChains(driver)
        scroll_options = [
            (0, random.randint(300, 800)),
            (0, random.randint(800, 1500)),
            (0, random.randint(1500, 2500)),
            (random.randint(100, 500), 0),
            (random.randint(500, 1000), 0)
        ]
        scroll_x, scroll_y = random.choice(scroll_options)
        driver.execute_script(f"window.scrollBy({scroll_x}, {scroll_y});")
        time.sleep(random.uniform(0.5, 2.5))

        for _ in range(random.randint(2, 5)):
            x = random.randint(0, 1000)
            y = random.randint(0, 700)
            actions.move_by_offset(x, y).perform()
            time.sleep(random.uniform(0.1, 0.7))
        actions.move_by_offset(-x, -y).perform()  # Reset mouse position
    except Exception as e:
        print(f"Random behavior simulation failed: {str(e)}")
        logging.warning(f"Random behavior simulation failed: {str(e)}")

def visit_url(driver, url):
    """Visit a URL and perform actions"""
    try:
        print(f"Visiting URL: {url}")
        logging.info(f"Visiting URL: {url}")
        driver.get(url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(random.uniform(3, 8))
        random_behavior(driver)

        clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a, button, input[type='button'], input[type='submit']")
        if clickable_elements:
            element = random.choice(clickable_elements)
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(random.uniform(0.5, 1.5))
                element.click()
                print(f"Clicked on element at {url}")
                logging.info(f"Clicked on element at {url}")
                time.sleep(random.uniform(2, 5))
                if random.random() > 0.5:
                    driver.back()
                    time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"Failed to click element: {str(e)}")
                logging.warning(f"Failed to click element: {str(e)}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"screenshots/{url.split('//')[1].split('/')[0]}_{timestamp}.png"
        os.makedirs("screenshots", exist_ok=True)
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        return True
    except Exception as e:
        print(f"Error visiting {url}: {str(e)}")
        logging.error(f"Error visiting {url}: {str(e)}")
        return False

def main():
    print("Starting main function...")
    proxy_ok, proxy_ip = verify_proxy_connection()
    print(f"Proxy verification result: {proxy_ok}, IP: {proxy_ip}")
    if not proxy_ok:
        print("Proxy connection verification failed. Exiting.")
        logging.error("Proxy connection verification failed. Exiting.")
        return

    driver = None
    try:
        driver = init_selenium_firefox()
        print("Selenium initialized successfully")
        random.shuffle(BASE_URLS)
        for url in BASE_URLS:
            success = visit_url(driver, url)
            if not success:
                print(f"Failed to visit {url}")
                logging.warning(f"Skipping remaining URLs due to failure on {url}")
                break
            delay = random.randint(15, 45)
            print(f"Waiting for {delay} seconds before next visit...")
            logging.info(f"Waiting for {delay} seconds before next visit...")
            time.sleep(delay)
        print("Closing browser...")
        driver.quit()
        print("Browser session completed successfully.")
        logging.info("Browser session completed successfully.")
    except Exception as e:
        print(f"Main execution failed: {str(e)}")
        logging.error(f"Main execution failed: {str(e)}")
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    print("hii")
    main()