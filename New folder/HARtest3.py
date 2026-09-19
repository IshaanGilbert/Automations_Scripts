# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import time
# import random
# import requests
# import json

# # === CONFIGURATION ===
# TARGET_URL = "https://marcadeo.com/"
# PROXY_API_URL = ""  # Optional: Use a proxy service API (e.g., Bright Data)
# VISIT_DURATION = (45, 90)  # seconds per visit
# HEADLESS = True
# SCREEN_SIZES = [(1920, 1080), (1366, 768), (375, 667), (1440, 900)]  # Desktop, laptop, mobile, etc.

# def get_random_proxy():
#     if not PROXY_API_URL:
#         return None
#     try:
#         # Replace with actual proxy service API call
#         proxy_list = requests.get(PROXY_API_URL).json().get('proxies', [])
#         return random.choice(proxy_list).strip()
#     except:
#         return None

# def handle_consent_banner(driver):
#     try:
#         consent_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(text(), 'OK')]")
#         if consent_buttons:
#             consent_buttons[0].click()
#             time.sleep(random.uniform(1, 2))
#             print("[+] Consent banner accepted")
#     except Exception as e:
#         print("[!] Consent banner handling error:", e)

# def wait_for_analytics(driver):
#     try:
#         # Wait for common analytics scripts (Google Analytics, Adobe Analytics, etc.)
#         WebDriverWait(driver, 10).until(
#             lambda d: d.execute_script("return typeof window.ga !== 'undefined' || typeof window._satellite !== 'undefined' || typeof window.gtag !== 'undefined'")
#         )
#         print("[+] Analytics scripts loaded")
#     except Exception as e:
#         print("[!] Analytics script wait error:", e)

# def simulate_user_behavior(driver):
#     try:
#         actions = ActionChains(driver)
#         width, height = driver.execute_script("return [window.innerWidth, window.innerHeight]")

#         handle_consent_banner(driver)
#         wait_for_analytics(driver)

#         # Trigger page view
#         driver.execute_script("gtag('config', 'G-XXXXXX', {'page_path': window.location.pathname});")

#         # Mouse and scroll behavior (existing code)
#         for _ in range(random.randint(5, 10)):
#             x = random.randint(0, width - 10)
#             y = random.randint(0, height - 10)
#             actions.move_by_offset(x, y).perform()
#             time.sleep(random.uniform(0.3, 0.9))
#             actions.reset_actions()

#         total_height = driver.execute_script("return document.body.scrollHeight")
#         scroll = 0
#         while scroll < total_height:
#             scroll += random.randint(300, 500)
#             driver.execute_script(f"window.scrollTo(0, {scroll})")
#             time.sleep(random.uniform(1.0, 2.0))

#         # Retry click logic
#         clickable_elements = driver.find_elements(By.XPATH, "//a | //button")
#         if clickable_elements:
#             target = random.choice(clickable_elements)
#             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target)
#             time.sleep(random.uniform(1, 2))
#             for attempt in range(3):
#                 try:
#                     target.click()
#                     time.sleep(random.uniform(5, 10))
#                     break
#                 except Exception as e:
#                     time.sleep(random.uniform(1, 2))
#                     if attempt == 2:
#                         print(f"[!] Failed to click: {e}")

#     except Exception as e:
#         print("[!] Behavior simulation error:", e)

# def handle_consent_banner(driver):
#     try:
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree')]"))).click()
#         time.sleep(random.uniform(1, 2))
#         print("[+] Consent banner accepted")
#     except:
#         print("[!] No consent banner found or failed to accept")

# def spoof_fingerprint(driver):
#     js_scripts = [
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
#         "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});",
#         "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});",
#         "Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});",
#         "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});",
#         "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});",
#         "Object.defineProperty(navigator, 'connection', {get: () => ({downlink: 10, effectiveType: '4g'})});",
#         "Object.defineProperty(window, 'chrome', {get: () => ({})});",
#         "Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})",
#         "Object.defineProperty(window, 'screen', {get: () => ({width: arguments[0], height: arguments[1]})})",
#     ]
#     screen_size = random.choice(SCREEN_SIZES)
#     for script in js_scripts:
#         try:
#             driver.execute_script(script, screen_size[0], screen_size[1])
#         except:
#             pass

#     # Set localStorage for analytics
#     try:
#         driver.execute_script("window.localStorage.setItem('analytics_id', 'user_' + Math.random().toString(36).substr(2, 9));")
#     except:
#         pass

# def create_driver(proxy=None):
#     ua = UserAgent().random
#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument(f"user-agent={ua}")
#     options.add_argument("--disable-popup-blocking")

#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")

#     if HEADLESS:
#         options.add_argument("--headless=new")

#     # Set random screen size
#     screen_size = random.choice(SCREEN_SIZES)
#     options.add_argument(f"--window-size={screen_size[0]},{screen_size[1]}")

#     driver = uc.Chrome(options=options, use_subprocess=True)
#     return driver

# def visit_website():
#     proxy = get_random_proxy()
#     driver = create_driver(proxy)
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 5))
#         spoof_fingerprint(driver)
#         simulate_user_behavior(driver)
#         time.sleep(random.randint(*VISIT_DURATION))
#         print("[+] Visit completed successfully")
#     except Exception as e:
#         print("[!] Visit failed:", e)
#     finally:
#         driver.quit()

# # Run loop
# if __name__ == "__main__":
#     for i in range(5):  # Number of visits
#         print(f"[+] Visit #{i + 1}")
#         visit_website()
#         time.sleep(random.randint(5, 15))  # Increased variability in delay



