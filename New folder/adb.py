# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import time, random, uuid, os, logging, subprocess, requests

# # — CONFIGURATION —
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# VISIT_COUNT = 50
# VISIT_DURATION = (40, 60)
# HEADLESS = False
# PROXY_LIST = []

# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# def get_random_proxy():
#     return random.choice(PROXY_LIST) if PROXY_LIST else None

# def toggle_airplane_mode_once():
#     try:
#         subprocess.run([
#             'adb', 'shell', 'su', '-c',
#             'settings put global airplane_mode_on 1 && am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true'
#         ], timeout=5)
#         time.sleep(random.randint(3, 5))
#         subprocess.run([
#             'adb', 'shell', 'su', '-c',
#             'settings put global airplane_mode_on 0 && am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false'
#         ], timeout=5)
#         time.sleep(5)
#     except Exception as e:
#         logging.error(f"Airplane toggle failed: {e}")

# def rotate_ip_before_visit():
#     logging.info("🔄 Toggling airplane mode twice before visit...")
#     for i in range(2):
#         logging.info(f"🛫 Toggle cycle {i+1}/2 starting")
#         toggle_airplane_mode_once()
#     return fetch_current_ip()

# def fetch_current_ip():
#     try:
#         ip = requests.get("https://api.ipify.org", timeout=5).text.strip()
#         logging.info(f"🌐 Current public IP: {ip}")
#         return ip
#     except:
#         logging.warning("❌ Could not fetch current IP.")
#         return "Unknown"

# def create_driver(proxy=None):
#     ua = UserAgent().random
#     profile_id = uuid.uuid4()
#     options = uc.ChromeOptions()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     logging.info(f"🧭 Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def simulate_user_behavior(driver):
#     actions = ActionChains(driver)
#     wait = WebDriverWait(driver, 10)
#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")

#     for _ in range(random.randint(3, 7)):
#         actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
#         time.sleep(random.uniform(0.2, 0.6))
#         actions.reset_actions()

#     total_h = driver.execute_script("return document.body.scrollHeight")
#     pos = 0
#     for _ in range(random.randint(3, 5)):
#         pos += random.randint(200, 600)
#         driver.execute_script(f"window.scrollTo(0, {pos});")
#         time.sleep(random.uniform(1, 2))
#         if random.random() < 0.3:
#             pos = max(0, pos - random.randint(100, 300))
#             driver.execute_script(f"window.scrollTo(0, {pos});")
#             time.sleep(random.uniform(0.5, 1.2))

#     elems = driver.find_elements(By.XPATH, "//a|//button")
#     visible = [e for e in elems if e.is_displayed()]
#     if visible and random.random() < 0.7:
#         tgt = random.choice(visible)
#         driver.execute_script("arguments[0].scrollIntoView();", tgt)
#         wait.until(EC.element_to_be_clickable(tgt))
#         tgt.click()
#         logging.info("🖱️ Clicked an element")
#         time.sleep(random.uniform(4, 10))

#     try:
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'page_view', {
#                   page_title: document.title,
#                   page_location: window.location.href
#                 });
#             }
#         """)
#     except:
#         pass

#     time.sleep(random.uniform(*VISIT_DURATION))

# def visit_once():
#     ip = rotate_ip_before_visit()
#     logging.info(f"🚀 Starting visit with IP: {ip}")
#     proxy = get_random_proxy()
#     driver = create_driver(proxy)
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(5)
#         simulate_user_behavior(driver)
#         logging.info("✅ Visit complete — browser closed")
#     except Exception as e:
#         logging.error(f"❌ Error during visit: {e}")
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     for i in range(VISIT_COUNT):
#         logging.info(f"\n=== 🚦 Visit {i+1} of {VISIT_COUNT} ===")
#         visit_once()
#         time.sleep(random.randint(10, 20))


# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time, random, uuid, os, logging, requests
# import subprocess

# # ===================== CONFIGURATION =====================
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# VISIT_COUNT = 1
# VISIT_DURATION = (40, 60)
# HEADLESS = False

# STATIC_USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
#     "Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
# ]

# # ============== LOGGING SETUP ==============
# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# # ============== ADB AIRPLANE TOGGLE ==============
# def toggle_airplane_mode():
#     for cycle in range(2):
#         print(f"\n🔄 Cycle {cycle + 1}:")
#         print("📴 Turning ON Airplane Mode...")
#         subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '1'])
#         subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'true'])
#         time.sleep(random.randint(5, 10))

#         print("📶 Turning OFF Airplane Mode...")
#         subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '0'])
#         subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'false'])
#         time.sleep(random.randint(5, 8))

#         ip = get_ip()
#         print(f"🌐 Public IP after toggle {cycle + 1}: {ip}")
#         logging.info(f"🌐 IP after airplane toggle {cycle + 1}: {ip}")

# def get_ip():
#     try:
#         response = requests.get("https://api.ipify.org", timeout=5)
#         return response.text.strip()
#     except:
#         return "❌ Could not fetch IP"

# # ============== BROWSER SETUP ==============
# def create_driver(proxy=None):
#     ua = random.choice(STATIC_USER_AGENTS)
#     profile_id = uuid.uuid4()
#     options = uc.ChromeOptions()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     logging.info(f"🧭 Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def simulate_user_behavior(driver):
#     actions = ActionChains(driver)
#     wait = WebDriverWait(driver, 10)

#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")

#     for _ in range(random.randint(3, 7)):
#         actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
#         time.sleep(random.uniform(0.2, 0.6))
#         actions.reset_actions()

#     total_h = driver.execute_script("return document.body.scrollHeight")
#     pos = 0
#     for _ in range(random.randint(3, 5)):
#         pos += random.randint(200, 600)
#         driver.execute_script(f"window.scrollTo(0, {pos});")
#         time.sleep(random.uniform(1, 2))
#         if random.random() < 0.3:
#             pos = max(0, pos - random.randint(100, 300))
#             driver.execute_script(f"window.scrollTo(0, {pos});")
#             time.sleep(random.uniform(0.5, 1.2))

#     elems = driver.find_elements(By.XPATH, "//a|//button")
#     visible = [e for e in elems if e.is_displayed()]
#     if visible and random.random() < 0.7:
#         tgt = random.choice(visible)
#         driver.execute_script("arguments[0].scrollIntoView();", tgt)
#         wait.until(EC.element_to_be_clickable(tgt))
#         tgt.click()
#         logging.info("🖱️ Clicked element")
#         time.sleep(random.uniform(4, 10))

#     try:
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'page_view', {
#                   page_title: document.title,
#                   page_location: window.location.href
#                 });
#             }
#         """)
#     except:
#         pass

#     time.sleep(random.uniform(*VISIT_DURATION))

# # ============== MAIN VISIT FUNCTION ==============
# def visit_once():
#     driver = create_driver()
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(5)
#         simulate_user_behavior(driver)
#         logging.info("✅ Visit complete")
#     except Exception as e:
#         logging.error(f"❌ Error during visit: {e}")
#     finally:
#         driver.quit()

# # ============== ENTRY POINT ==============
# if __name__ == "__main__":
#     toggle_airplane_mode()  # First toggle device
#     for i in range(VISIT_COUNT):
#         print(f"\n🚀 Starting visit {i + 1} of {VISIT_COUNT}")
#         logging.info(f"=== Starting visit {i+1} ===")
#         visit_once()
#         time.sleep(random.randint(10, 20))




# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time, random, uuid, os, logging, requests
# import subprocess

# # ===================== CONFIGURATION =====================
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# VISIT_COUNT = 3
# VISIT_DURATION = (40, 60)
# HEADLESS = False

# STATIC_USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
#     "Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
# ]

# # ============== LOGGING SETUP ==============
# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# # ============== ADB AIRPLANE TOGGLE ==============
# def toggle_airplane_mode():
#     try:
#         print("\n🔄 Starting airplane mode toggle sequence:")
#         # First ON (5-10 seconds)
#         print("📴 Turning ON Airplane Mode (1st time)...")
#         subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '1'])
#         subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'true'])
#         on_duration = random.randint(5, 10)
#         time.sleep(on_duration)
#         print(f"Waited {on_duration} seconds.")

#         # First OFF (3-5 seconds)
#         print("📶 Turning OFF Airplane Mode (1st time)...")
#         subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '0'])
#         subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'false'])
#         off_duration = random.randint(3, 5)
#         time.sleep(off_duration)
#         print(f"Waited {off_duration} seconds.")

#         # Second ON (5-10 seconds)
#         print("📴 Turning ON Airplane Mode (2nd time)...")
#         subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '1'])
#         subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'true'])
#         on_duration = random.randint(5, 10)
#         time.sleep(on_duration)
#         print(f"Waited {on_duration} seconds.")

#         # Second OFF 
#         print("📶 Turning OFF Airplane Mode (2nd time)...")
#         subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '0'])
#         subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'false'])
#         time.sleep(5)  # Fixed 5 seconds to ensure network reconnects
#         ip = get_ip()
#         print(f"🌐 Public IP after toggle sequence: {ip}")
#         logging.info(f"🌐 IP after airplane toggle sequence: {ip}")
#         return True
#     except Exception as e:
#         logging.error(f"❌ Error toggling airplane mode: {e}")
#         print(f"❌ Error toggling airplane mode: {e}")
#         return False

# def get_ip():
#     try:
#         response = requests.get("https://api.ipify.org", timeout=5)
#         return response.text.strip()
#     except:
#         return "❌ Could not fetch IP"

# # ============== BROWSER SETUP ==============
# def create_driver(proxy=None):
#     ua = random.choice(STATIC_USER_AGENTS)
#     profile_id = uuid.uuid4()
#     options = uc.ChromeOptions()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     logging.info(f"🧭 Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def simulate_user_behavior(driver):
#     actions = ActionChains(driver)
#     wait = WebDriverWait(driver, 10)

#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")

#     for _ in range(random.randint(3, 7)):
#         actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
#         time.sleep(random.uniform(0.2, 0.6))
#         actions.reset_actions()

#     total_h = driver.execute_script("return document.body.scrollHeight")
#     pos = 0
#     for _ in range(random.randint(3, 5)):
#         pos += random.randint(200, 600)
#         driver.execute_script(f"window.scrollTo(0, {pos});")
#         time.sleep(random.uniform(1, 2))
#         if random.random() < 0.3:
#             pos = max(0, pos - random.randint(100, 300))
#             driver.execute_script(f"window.scrollTo(0, {pos});")
#             time.sleep(random.uniform(0.5, 1.2))

#     elems = driver.find_elements(By.XPATH, "//a|//button")
#     visible = [e for e in elems if e.is_displayed()]
#     if visible and random.random() < 0.7:
#         tgt = random.choice(visible)
#         driver.execute_script("arguments[0].scrollIntoView();", tgt)
#         wait.until(EC.element_to_be_clickable(tgt))
#         tgt.click()
#         logging.info("🖱️ Clicked element")
#         time.sleep(random.uniform(4, 10))

#     try:
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'page_view', {
#                   page_title: document.title,
#                   page_location: window.location.href
#                 });
#             }
#         """)
#     except:
#         pass

#     time.sleep(random.uniform(*VISIT_DURATION))

# # ============== MAIN VISIT FUNCTION ==============
# def visit_once():
#     # Toggle airplane mode before visit
#     if not toggle_airplane_mode():
#         logging.error("Failed to toggle airplane mode. Skipping visit.")
#         print("❌ Failed to toggle airplane mode. Skipping visit.")
#         return
#     driver = create_driver()
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(5)
#         simulate_user_behavior(driver)
#         logging.info("✅ Visit complete")
#     except Exception as e:
#         logging.error(f"❌ Error during visit: {e}")
#     finally:
#         driver.quit()

# # ============== ENTRY POINT ==============
# if __name__ == "__main__":
#     for i in range(VISIT_COUNT):
#         print(f"\n🚀 Starting visit {i + 1} of {VISIT_COUNT}")
#         logging.info(f"=== Starting visit {i+1} ===")
#         visit_once()
#         time.sleep(random.randint(10, 20))







import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random, uuid, os, logging, requests, subprocess, tempfile
import subprocess

# ===================== CONFIGURATION =====================
TARGET_URL = "https://www.adidas.co.in/adi_zomato"
VISIT_COUNT = 100
VISIT_DURATION = (20, 40)  # Reduced from (40, 60) for faster visits
HEADLESS = True

STATIC_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 Chrome/91.0.4472.124 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 Chrome/87.0.4280.141 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 Chrome/88.0.4324.182 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 Chrome/92.0.4515.107 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 Chrome/91.0.4472.77 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 9; Redmi Note 8) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/77.0.3865.75 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 Chrome/81.0.4044.117 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 Chrome/75.0.3770.142 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 Safari/601.7.7",
    "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-G950F) AppleWebKit/537.36 Chrome/78.0.3904.108 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Mozilla/5.0 (iPad; CPU OS 12_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 10; Redmi Note 9 Pro) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.4.8 Safari/602.4.8",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Gecko/20100101 Firefox/74.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; Nexus 6P Build/NBD91L) AppleWebKit/537.36 Chrome/64.0.3282.137 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) Gecko/20100101 Firefox/60.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 Chrome/65.0.3325.181 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 8.1.0; Infinix X608) AppleWebKit/537.36 Chrome/71.0.3578.99 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; ARM; Surface Duo) AppleWebKit/537.36 Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.34",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 Chrome/63.0.3239.132 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; SM-J500F) AppleWebKit/537.36 Chrome/79.0.3945.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1; rv:52.0) Gecko/20100101 Firefox/52.0",
    "Mozilla/5.0 (iPad; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 Mobile/13G36",
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 Chrome/76.0.3809.132 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Mozilla/5.0 (Linux; Android 7.1.1; Moto G (5S)) AppleWebKit/537.36 Chrome/81.0.4044.138 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 Chrome/77.0.3865.90 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2 like Mac OS X) AppleWebKit/604.4.7 Mobile/15C114",
    "Mozilla/5.0 (X11; Linux i686; rv:65.0) Gecko/20100101 Firefox/65.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0",
    "Mozilla/5.0 (Linux; Android 10; SM-M315F) AppleWebKit/537.36 Chrome/85.0.4183.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 Chrome/80.0.3987.87 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; LG-H870) AppleWebKit/537.36 Chrome/72.0.3626.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 Mobile/13F69",
    "Mozilla/5.0 (Windows NT 10.0; x64) AppleWebKit/537.36 Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62",
    "Mozilla/5.0 (Linux; Android 8.1.0; vivo 1803) AppleWebKit/537.36 Chrome/76.0.3809.111 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/69.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 Chrome/49.0.2623.112 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; Nokia 6.1) AppleWebKit/537.36 Chrome/72.0.3626.121 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
    "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 Mobile/15A5341f",
    "Mozilla/5.0 (Linux; Android 6.0.1; Moto G4) AppleWebKit/537.36 Chrome/73.0.3683.90 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 Chrome/72.0.3626.96 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Mozilla/5.0 (Linux; Android 10; SM-A107F) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 Chrome/73.0.3683.75 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 7.0; SM-J730GM) AppleWebKit/537.36 Chrome/80.0.3987.132 Mobile Safari/537.36",
]

# ============== LOGGING SETUP ==============
logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# ============== ADB AIRPLANE TOGGLE ==============
def toggle_airplane_mode():
    try:
        print("\n🔄 Starting airplane mode toggle sequence:")
        # First ON (3-5 seconds)
        print("📴 Turning ON Airplane Mode (1st time)...")
        subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '1'], check=True)
        subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'true'], check=True)
        on_duration = random.uniform(3, 5)
        time.sleep(on_duration)
        print(f"Waited {on_duration:.2f} seconds.")

        # First OFF (2-3 seconds)
        print("📶 Turning OFF Airplane Mode (1st time)...")
        subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '0'], check=True)
        subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'false'], check=True)
        off_duration = random.uniform(2, 3)
        time.sleep(off_duration)
        print(f"Waited {off_duration:.2f} seconds.")

        # Second ON (3-5 seconds)
        print("📴 Turning ON Airplane Mode (2nd time)...")
        subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '1'], check=True)
        subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'true'], check=True)
        on_duration = random.uniform(3, 5)
        time.sleep(on_duration)
        print(f"Waited {on_duration:.2f} seconds.")

        # Second OFF
        print("📶 Turning OFF Airplane Mode (2nd time)...")
        subprocess.run(['adb', 'shell', 'settings', 'put', 'global', 'airplane_mode_on', '0'], check=True)
        subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'false'], check=True)
        time.sleep(3)  # Reduced from 5s to 3s for faster network reconnection
        ip = get_ip()
        print(f"🌐 Public IP after toggle sequence: {ip}")
        logging.info(f"🌐 IP after airplane toggle sequence: {ip}")
        return ip != "❌ Could not fetch IP"
    except Exception as e:
        logging.error(f"❌ Error toggling airplane mode: {e}")
        print(f"❌ Error toggling airplane mode: {e}")
        return False

def get_ip(max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get("https://api.ipify.org", timeout=3)  # Reduced timeout from 5s to 3s
            ip = response.text.strip()
            return ip
        except:
            print(f"IP fetch attempt {attempt + 1} failed.")
            time.sleep(1)
    return "❌ Could not fetch IP"

# ============== BROWSER SETUP ==============
def create_driver(proxy=None):
    ua = random.choice(STATIC_USER_AGENTS)
    profile_id = uuid.uuid4()
    options = uc.ChromeOptions()
    options.add_argument(f"--user-agent={ua}")
    options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    if proxy:
        options.add_argument(f"--proxy-server=http://{proxy}")
    if HEADLESS:
        options.add_argument("--headless=new")

    logging.info(f"🧭 Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
    return uc.Chrome(options=options, use_subprocess=True, version_main=137, driver_executable_path="C:/Users/lenovo/appdata/roaming/undetected_chromedriver/chromedriver.exe")
# def create_driver(proxy=None):
#     ua = random.choice(STATIC_USER_AGENTS)
#     temp_dir = tempfile.mkdtemp()  # ✅ Dynamic temporary directory
#     options = uc.ChromeOptions()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--user-data-dir={temp_dir}")  # ✅ Replaced hardcoded path
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     logging.info(f"🧭 Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
    
#     # ✅ Set driver_executable_path to local chromedriver.exe
#     return uc.Chrome(
#         options=options,
#         use_subprocess=True,
#         version_main=137,
#         driver_executable_path="./chromedriver.exe"  # Local to script folder
#     )

def simulate_user_behavior(driver):
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 5)  # Reduced timeout from 10s to 5s

    width = driver.execute_script("return window.innerWidth")
    height = driver.execute_script("return window.innerHeight")

    for _ in range(random.randint(2, 5)):  # Reduced from 3-7 to 2-5
        actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
        time.sleep(random.uniform(0.1, 0.3))  # Reduced from 0.2-0.6
        actions.reset_actions()

    total_h = driver.execute_script("return document.body.scrollHeight")
    pos = 0
    for _ in range(random.randint(2, 4)):  # Reduced from 3-5 to 2-4
        pos += random.randint(200, 400)  # Reduced max scroll distance
        driver.execute_script(f"window.scrollTo(0, {pos});")
        time.sleep(random.uniform(0.5, 1))  # Reduced from 1-2
        if random.random() < 0.3:
            pos = max(0, pos - random.randint(100, 200))  # Reduced backtrack distance
            driver.execute_script(f"window.scrollTo(0, {pos});")
            time.sleep(random.uniform(0.3, 0.7))  # Reduced from 0.5-1.2

    elems = driver.find_elements(By.XPATH, "//a|//button")
    visible = [e for e in elems if e.is_displayed()]
    if visible and random.random() < 0.7:
        tgt = random.choice(visible)
        driver.execute_script("arguments[0].scrollIntoView();", tgt)
        wait.until(EC.element_to_be_clickable(tgt))
        tgt.click()
        logging.info("🖱️ Clicked element")
        time.sleep(random.uniform(2, 5))  # Reduced from 4-10

    # Skip GA triggering unless confirmed necessary for target site
    try:
        driver.execute_script("""
            if (typeof gtag === 'function') {
                gtag('event', 'page_view', {
                  page_title: document.title,
                  page_location: window.location.href
                });
            }
        """)
    except:
        pass

    time.sleep(random.uniform(*VISIT_DURATION))

# ============== MAIN VISIT FUNCTION ==============
def visit_once():
    # Toggle airplane mode before visit
    if not toggle_airplane_mode():
        logging.error("Failed to toggle airplane mode. Skipping visit.")
        print("❌ Failed to toggle airplane mode. Skipping visit.")
        return
    driver = create_driver()
    try:
        driver.get(TARGET_URL)
        time.sleep(3)  # Reduced from 5s
        simulate_user_behavior(driver)
        logging.info("✅ Visit complete")
    except Exception as e:
        logging.error(f"❌ Error during visit: {e}")
    finally:
        driver.quit()

# ============== ENTRY POINT ==============
if __name__ == "__main__": 
    for i in range(VISIT_COUNT):
        print(f"\n🚀 Starting visit {i + 1} of {VISIT_COUNT}")
        logging.info(f"=== Starting visit {i+1} ===")
        visit_once()
        time.sleep(random.randint(5, 10))  # Reduced from 10-20  