# import cloudscraper
# scraper = cloudscraper.create_scraper()
# response = scraper.get("https://www.adidas.co.in/adi_zomato")
# print(response.text)

# import cloudscraper
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# import random
# import time
# import fake_useragent
# import requests
# import json

# # Initialize cloudscraper
# scraper = cloudscraper.create_scraper()

# # FlareSolverr API endpoint
# FLARESOLVERR_URL = "http://localhost:8191/v1"

# # List of user agents for rotation
# ua = fake_useragent.UserAgent()
# user_agents = [
#     ua.chrome,
#     ua.firefox,
#     ua.safari,
#     ua.random
# ]

# # Function to try FlareSolverr
# def try_flaresolverr(url):
#     try:
#         print("Trying FlareSolverr...")
#         headers = {"Content-Type": "application/json"}
#         payload = {
#             "cmd": "request.get",
#             "url": url,
#             "maxTimeout": 60000
#         }
#         response = requests.post(FLARESOLVERR_URL, headers=headers, json=payload)
#         if response.status_code == 200:
#             data = response.json()
#             if data.get("status") == "ok":
#                 print("FlareSolverr succeeded!")
#                 return data["solution"]["response"]
#             else:
#                 print(f"FlareSolverr failed: {data.get('message')}")
#                 return None
#         else:
#             print(f"FlareSolverr API error: Status {response.status_code}")
#             return None
#     except Exception as e:
#         print(f"FlareSolverr error: {e}")
#         return None

# # Function to simulate human-like mouse movements
# def simulate_mouse_movements(driver):
#     try:
#         action = ActionChains(driver)
#         window_size = driver.get_window_size()
#         width, height = window_size['width'], window_size['height']
#         print(f"Window size: {width}x{height}")

#         # Start from a safe position (center of the window)
#         body = driver.find_element("tag name", "body")
#         action.move_to_element_with_offset(body, 0, 0).perform()
#         time.sleep(random.uniform(0.2, 0.5))

#         # Perform random mouse movements within safe bounds
#         for _ in range(random.randint(3, 7)):
#             x_offset = random.randint(-width // 10, width // 10)  # Even smaller range
#             y_offset = random.randint(-height // 10, height // 10)
#             print(f"Moving mouse by offset: ({x_offset}, {y_offset})")
#             action.move_by_offset(x_offset, y_offset).pause(random.uniform(0.1, 0.5)).perform()
#             action.reset_actions()
#             time.sleep(random.uniform(0.2, 0.8))
#     except Exception as e:
#         print(f"Error in mouse movements: {e}")

# # Function to simulate human-like scrolling
# def simulate_scrolling(driver):
#     try:
#         for _ in range(random.randint(2, 5)):
#             scroll_amount = random.randint(100, 500)
#             print(f"Scrolling by: {scroll_amount}px")
#             driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
#             time.sleep(random.uniform(0.3, 1.0))
#         # Scroll back up sometimes
#         if random.choice([True, False]):
#             print("Scrolling back to top")
#             driver.execute_script("window.scrollTo(0, 0);")
#             time.sleep(random.uniform(0.5, 1.2))
#     except Exception as e:
#         print(f"Error in scrolling: {e}")

# # Main function to bypass Cloudflare
# def bypass_cloudflare(url):
#     try:
#         # Try FlareSolverr first
#         result = try_flaresolverr(url)
#         if result:
#             return result

#         # Try cloudscraper as fallback
#         headers = {"User-Agent": random.choice(user_agents)}
#         print(f"Trying cloudscraper with User-Agent: {headers['User-Agent']}")
#         response = scraper.get(url, headers=headers)
#         if response.status_code == 200:
#             print("Successfully accessed using cloudscraper!")
#             return response.text
#         else:
#             print(f"Cloudscraper failed with status code: {response.status_code}, switching to Selenium...")

#         # Set up Selenium with non-headless Chrome
#         chrome_options = Options()
#         chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")

#         # Initialize WebDriver
#         print("Initializing Chrome WebDriver...")
#         driver = webdriver.Chrome(options=chrome_options)
        
#         # Navigate to the URL
#         print(f"Navigating to {url}")
#         driver.get(url)
#         time.sleep(random.uniform(2, 5))  # Wait for page to load
#         print("Page loaded, starting human-like interactions...")

#         # Simulate human-like interactions
#         simulate_mouse_movements(driver)
#         simulate_scrolling(driver)

#         # Additional human-like interactions (e.g., random clicks or key presses)
#         try:
#             print("Simulating spacebar press...")
#             ActionChains(driver).send_keys(Keys.SPACE).perform()
#             time.sleep(random.uniform(0.5, 1.5))
#         except Exception as e:
#             print(f"Error during key press: {e}")

#         # Get page content
#         page_source = driver.page_source
#         print("Successfully accessed using Selenium!")
        
#         # Clean up
#         driver.quit()
#         return page_source

#     except Exception as e:
#         print(f"Error occurred: {e}")
#         return None

# # Example usage
# if __name__ == "__main__":
#     target_url = "https://www.adidas.co.in/adi_zomato"  # Target URL
#     result = bypass_cloudflare(target_url)
#     if result:
#         print("Page content retrieved successfully!")
#         # Save the result to a file
#         with open("output.html", "w", encoding="utf-8") as f:
#             f.write(result)
#     else:
#         print("Failed to bypass Cloudflare.")





# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# import time
# import random

# def simulate_real_user(driver):
#     actions = ActionChains(driver)

#     # Move mouse randomly
#     for _ in range(random.randint(5, 10)):
#         x = random.randint(100, 400)
#         y = random.randint(100, 500)
#         actions.move_by_offset(x, y).perform()
#         time.sleep(random.uniform(0.2, 0.6))
#         actions.reset_actions()

#     # Scroll
#     scroll_depth = random.randint(300, 1000)
#     driver.execute_script(f"window.scrollTo(0, {scroll_depth});")
#     time.sleep(random.uniform(2, 5))

#     # Stay on page long enough
#     time.sleep(random.uniform(15, 30))

# def visit_site(url):
#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     # options.add_argument("--headless=new")  # comment out for visible window

#     driver = uc.Chrome(options=options, use_subprocess=True, version_main=137)

#     try:
#         driver.get(url)
#         time.sleep(5)  # wait for GA to load
#         simulate_real_user(driver)
#     except Exception as e:
#         print("Visit failed:", e)
#     finally:
#         driver.quit()

# # === MAIN LOOP ===
# if __name__ == "__main__":
#     for i in range(5):
#         print(f"\n[+] Visit #{i+1}")
#         visit_site("https://marcadeo.com/")
#         time.sleep(random.randint(10, 15))




# import undetected_chromedriver as uc
# from selenium.webdriver.common.action_chains import ActionChains
# import time
# import random

# def simulate_real_user(driver):
#     actions = ActionChains(driver)

#     for _ in range(random.randint(3, 6)):
#         x = random.randint(0, 500)
#         y = random.randint(0, 500)
#         actions.move_by_offset(x, y).perform()
#         time.sleep(random.uniform(0.5, 1.0))
#         actions.reset_actions()

#     scroll_times = random.randint(2, 4)
#     for i in range(scroll_times):
#         scroll_y = random.randint(200, 800)
#         driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#         time.sleep(random.uniform(1.0, 2.5))

#     time.sleep(random.uniform(15, 25))  # Very important for GA tracking

# def visit_site(url):
#     options = uc.ChromeOptions()
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--start-maximized")
#     # Don't use headless mode

#     driver = uc.Chrome(options=options, version_main=137)

#     try:
#         print(f"[+] Visiting {url}")
#         driver.get(url)
#         time.sleep(5)  # Allow gtag.js or analytics.js to load
#         simulate_real_user(driver)
#         print("[✓] Visit complete")
#     except Exception as e:
#         print("[!] Visit error:", e)
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     for i in range(3):
#         print(f"\n==== Visit #{i+1} ====")
#         visit_site("https://marcadeo.com/")  # or marcadeo.com
#         time.sleep(random.randint(10, 20))








import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import time
import random
import os
import signal
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

# === CONFIGURATION ===
TARGET_URLS = [
    "https://marcadeo.com/"
]
NUM_VISITS = 30
CONCURRENCY = 1
HEADLESS = False  # Toggle to True for headless mode
CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")

VIEWPORTS = [
    (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
    (1024, 768), (1600, 900), (1536, 864), (800, 600),
    (360, 640), (375, 667),
]
LOCALES = [
    "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
]
TIMEZONES = [
    "Asia/Kolkata", "Europe/London", "America/New_York",
    "Australia/Sydney", "Asia/Tokyo", "Europe/Paris", "America/Los_Angeles"
]

ACTIVE_DRIVERS = []
ua_generator = UserAgent()

def signal_handler(sig, frame):
    print("Received interrupt signal. Closing all active drivers...")
    for driver in ACTIVE_DRIVERS:
        try:
            driver.quit()
            print("Driver closed successfully.")
        except Exception as e:
            print(f"Failed to close driver: {e}")
    os.system("taskkill /F /IM chrome.exe")
    os.system("taskkill /F /IM chromedriver.exe")
    print("All drivers and processes terminated.")
    sys.exit(0)

def get_random_user_agent():
    browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera']
    try:
        return getattr(ua_generator, random.choice(browsers))
    except:
        return ua_generator.random

def create_driver(session_id):
    ua = get_random_user_agent()
    vp = random.choice(VIEWPORTS)
    locale = random.choice(LOCALES)
    profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
    os.makedirs("browser_profiles", exist_ok=True)

    options = uc.ChromeOptions()
    options.binary_location = CHROME_BINARY
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument(f"--lang={locale}")
    options.add_argument(f"user-agent={ua}")
    options.add_argument(f"--user-data-dir={profile_folder}")
    options.add_argument(f"--window-size={vp[0]},{vp[1]}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-features=UserAgentClientHint")
    # [Change] Added extra options to improve headless emulation, inspired by Playwright's realistic rendering
    # Message: Yeh options headless mode ko real browser jaisa banate hain, GA tracking ke liye zaroori
    options.add_argument("--disable-gpu")
    options.add_argument("--blink-settings=imagesEnabled=true")
    options.add_argument("--enable-webgl")
    options.add_argument("--enable-javascript")
    options.add_argument("--ignore-certificate-errors")
    if HEADLESS:
        options.add_argument("--headless=new")

    service = Service(CHROMEDRIVER_PATH, log_path="chromedriver.log")

    try:
        driver = uc.Chrome(
            service=service,
            options=options,
            user_data_dir=profile_folder,
            use_subprocess=True,
            headless=HEADLESS,
            driver_executable_path=CHROMEDRIVER_PATH,
            patcher_force_close=True,
        )
        driver.set_window_size(vp[0], vp[1])
        ACTIVE_DRIVERS.append(driver)
        return driver, locale
    except Exception as e:
        print(f"Failed to create driver for session #{session_id}: {e}")
        return None, None

def spoof_js_script(timezone):
    return f"""
    // Webdriver removal
    Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});

    // Fake plugins
    Object.defineProperty(navigator, 'plugins', {{
        get: () => [1, 2, 3, 4, 5]
    }});

    // Fake languages
    Object.defineProperty(navigator, 'languages', {{
        get: () => ['en-US', 'en']
    }});

    // Device memory
    Object.defineProperty(navigator, 'deviceMemory', {{
        get: () => 8
    }});

    // Hardware Concurrency
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => 4
    }});

    // WebGL fingerprint spoof
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter(parameter);
    }};

    // Canvas spoof
    const toDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function() {{
        return "data:image/png;base64,fakecanvasdata";
    }};

    // Audio fingerprint spoof
    const createOscillator = AudioContext.prototype.createOscillator;
    AudioContext.prototype.createOscillator = function() {{
        const oscillator = createOscillator.call(this);
        oscillator.frequency.value = 440;
        return oscillator;
    }};

    // Timezone spoof
    Intl.DateTimeFormat = function() {{
        return {{ resolvedOptions: () => ({{ timeZone: '{timezone}' }}) }};
    }};
    """

def simulate_interaction(driver, total_time=90):
    start_time = time.time()
    total_time_spent = 0
    action = ActionChains(driver)

    try:
        # [Change] Increased initial wait to match Playwright's reliable page load
        # Message: Playwright ke wait_for_load_state("load") jaisa effect, page ke full load hone ka wait
        time.sleep(random.uniform(5, 10))
        total_time_spent += random.uniform(5, 10)

        # Get window dimensions
        width = driver.execute_script("return window.innerWidth") or 1200
        height = driver.execute_script("return window.innerHeight") or 1000

        while total_time_spent < total_time:
            # Random mouse movement
            for _ in range(random.randint(2, 5)):
                x = random.randint(0, min(width, 1200))
                y = random.randint(0, min(height, 1000))
                try:
                    action.move_by_offset(x, y).perform()
                    action.reset_actions()
                except:
                    pass
                t = random.uniform(0.3, 1.0)
                time.sleep(t)
                total_time_spent += t

            # Scroll action
            if random.choice([True, False]):
                scroll_y = random.randint(300, 1000)
                driver.execute_script(f"window.scrollBy(0, {scroll_y});")
                t = random.uniform(1, 2)
                time.sleep(t)
                total_time_spent += t

            # Random scroll position
            if random.choice([True, False]):
                driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
                t = random.uniform(1, 2)
                time.sleep(t)
                total_time_spent += t

            # [Change] Added click simulation to mimic Playwright's realistic user behavior
            # Message: Playwright ke interaction se inspired, random clicks GA tracking ko trigger kar sakte hain
            try:
                links = driver.find_elements(By.TAG_NAME, "a")
                if links:
                    random.choice(links).click()
                    time.sleep(random.uniform(2, 4))
                    driver.back()
            except:
                pass
                t = random.uniform(1, 2)
                total_time_spent += t

            # Idle like reading
            t = random.uniform(2, 5)
            time.sleep(t)
            total_time_spent += t

            # Exit if total_time is reached
            if total_time_spent >= total_time:
                break

        # Final wait to normalize total time
        if total_time_spent < total_time:
            time.sleep(total_time - total_time_spent)

    except Exception as e:
        print(f"[!] Interaction Error: {e}")

def simulate_single_visit(session_id, url):
    print(f"[*] Starting session #{session_id} → {url}")
    driver, locale = create_driver(session_id)
    if not driver:
        print(f"[x] Session #{session_id} failed: Driver creation failed")
        return

    timezone = random.choice(TIMEZONES)
    start_time = time.time()
    try:
        # [Change] Added robust page load wait inspired by Playwright's wait_for_load_state
        # Message: Yeh ensure karta hai ki page fully load ho, GA scripts ke liye zaroori
        driver.get(url)
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState === 'complete'")
        )
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # [Change] Improved Cloudflare handling with more robust checks
        # Message: Playwright ke reliable Cloudflare bypass se inspired, zyada wait aur checks
        if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
            print(f"[!] Session #{session_id}: Cloudflare challenge detected.")
            try:
                WebDriverWait(driver, 30).until(
                    lambda d: "cf-ray" not in d.page_source and "Checking your browser" not in d.page_source
                )
                print(f"[✓] Cloudflare challenge passed")
            except:
                print(f"[!] Cloudflare challenge not resolved")
            time.sleep(random.uniform(10, 15))

        # [Change] Moved spoof script earlier to apply before GA scripts load
        # Message: Playwright ke init_script jaisa effect, anti-detection pehle apply hota hai
        driver.execute_script(spoof_js_script(timezone))

        # [Change] Enhanced GA script wait to ensure scripts are loaded
        # Message: Playwright ke reliable script detection se inspired, GA scripts ke load hone ka wait
        try:
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return typeof gtag === 'function' || typeof ga === 'function' || typeof window.dataLayer !== 'undefined'")
            )
            print(f"[📊] GA scripts loaded in session #{session_id}")
        except Exception as e:
            print(f"[!] GA script load failed: {e}")

        # Trigger GA events
        driver.execute_script("""
            if (typeof gtag === 'function') {
                gtag('event', 'page_view');
                gtag('event', 'headless_test', { 'event_category': 'Test', 'event_label': 'Headless' });
            } else if (typeof ga === 'function') {
                ga('send', 'pageview');
                ga('send', 'event', 'Test', 'Headless', 'headless_test');
            }
            if (typeof window.dataLayer !== 'undefined') {
                window.dataLayer.push({'event': 'headless_test'});
            }
        """)

        # Simulate scrolling
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1.5, 3))
        driver.execute_script("window.scrollTo(0, 0);")

        # [Change] Added GA beacon check inspired by Playwright's resource tracking
        # Message: Yeh verify karta hai ki GA collect requests bheje gaye, Playwright ke jaisa
        beacons = driver.execute_script("""
            return performance.getEntriesByType('resource')
                .filter(r => r.name.includes('google-analytics.com/collect') || r.name.includes('googletagmanager.com'));
        """)
        print(f"[📊] GA beacons detected: {len(beacons)}")

        # Simulate interaction
        # [Change] Increased visit time to 90-120s to mimic Playwright's realistic session duration
        # Message: Zyada time GA ke liye realistic session banata hai
        visit_time = random.randint(90, 120)
        simulate_interaction(driver, total_time=visit_time)

        # [Change] Added final wait for network activity, inspired by Playwright's clean context close
        # Message: Yeh ensure karta hai ki GA beacons send ho jayein quit se pehle
        try:
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script("return performance.getEntriesByType('resource').length") == d.execute_script("return performance.getEntriesByType('resource').length")
            )
        except:
            pass
        time.sleep(random.uniform(10, 15))

        print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")

    except Exception as e:
        print(f"[x] Session #{session_id} failed: {e}")
    finally:
        try:
            if driver in ACTIVE_DRIVERS:
                ACTIVE_DRIVERS.remove(driver)
            driver.quit()
        except Exception as e:
            print(f"[!] Session #{session_id}: Driver quit failed - {e}")
            os.system("taskkill /F /IM chrome.exe")
            os.system("taskkill /F /IM chromedriver.exe")

def main():
    signal.signal(signal.SIGINT, signal_handler)

    print("Cleaning up existing Chrome processes...")
    os.system("taskkill /F /IM chrome.exe")
    os.system("taskkill /F /IM chromedriver.exe")

    print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
    print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

    # Use ThreadPoolExecutor for concurrency
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        visit_id = 0
        futures = []
        for i in range(NUM_VISITS):
            for url in TARGET_URLS:
                visit_id += 1
                futures.append(executor.submit(simulate_single_visit, visit_id, url))
        
        # Wait for all visits to complete
        for future in futures:
            future.result()

if __name__ == "__main__":
    start = time.time()
    main()
    print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.")