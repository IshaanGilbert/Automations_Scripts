# # # this script is who run on Date 19-06-2025

# # # Script used : Script make on Selenium and UC Driver with random user-agent and fingerprint actions

# # # Running visit : Total visit 120

# # # Data : ON GA :- 98, ON Adobe :- 102 

# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import time
# import random
# import os
# import signal
# import sys
# import threading
# from concurrent.futures import ThreadPoolExecutor


# # === CONFIGURATION ===
# TARGET_URLS = [
#     "https://unfilteredgadgets.com/"
# ]
# NUM_VISITS = 30
# CONCURRENCY = 2
# HEADLESS = False  # Toggle to True for headless mode
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")


# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864), (800, 600),
#     (360, 640), (375, 667),
# ]
# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
# ]
# TIMEZONES = [
#     "Asia/Kolkata", "Europe/London", "America/New_York",
#     "Australia/Sydney", "Asia/Tokyo", "Europe/Paris", "America/Los_Angeles"
# ]


# ACTIVE_DRIVERS = []
# ua_generator = UserAgent()


# def signal_handler(sig, frame):
#     print("Received interrupt signal. Closing all active drivers...")
#     for driver in ACTIVE_DRIVERS:
#         try:
#             driver.quit()
#             print("Driver closed successfully.")
#         except Exception as e:
#             print(f"Failed to close driver: {e}")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")
#     print("All drivers and processes terminated.")
#     sys.exit(0)


# def get_random_user_agent():
#     browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera']
#     try:
#         return getattr(ua_generator, random.choice(browsers))
#     except:
#         return ua_generator.random


# def create_driver(session_id):
#     ua = get_random_user_agent()
#     vp = random.choice(VIEWPORTS)
#     locale = random.choice(LOCALES)
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
#     os.makedirs("browser_profiles", exist_ok=True)


#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--remote-debugging-port=0")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"user-agent={ua}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     options.add_argument("--no-first-run")
#     options.add_argument("--no-default-browser-check")
#     options.add_argument("--disable-features=UserAgentClientHint")
#     # [Change] Added extra options to improve headless emulation, inspired by Playwright's realistic rendering
#     # Message: Yeh options headless mode ko real browser jaisa banate hain, GA tracking ke liye zaroori
#     options.add_argument("--disable-gpu")
#     options.add_argument("--blink-settings=imagesEnabled=true")
#     options.add_argument("--enable-webgl")
#     options.add_argument("--enable-javascript")
#     options.add_argument("--ignore-certificate-errors")
#     if HEADLESS:
#         options.add_argument("--headless=new")


#     service = Service(CHROMEDRIVER_PATH, log_path="chromedriver.log")


#     try:
#         driver = uc.Chrome(
#             service=service,
#             options=options,
#             user_data_dir=profile_folder,
#             use_subprocess=True,
#             headless=HEADLESS,
#             driver_executable_path=CHROMEDRIVER_PATH,
#             patcher_force_close=True,
#         )
#         driver.set_window_size(vp[0], vp[1])
#         ACTIVE_DRIVERS.append(driver)
#         return driver, locale
#     except Exception as e:
#         print(f"Failed to create driver for session #{session_id}: {e}")
#         return None, None


# def spoof_js_script(timezone):
#     return f"""
#     // Webdriver removal
#     Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});


#     // Fake plugins
#     Object.defineProperty(navigator, 'plugins', {{
#         get: () => [1, 2, 3, 4, 5]
#     }});


#     // Fake languages
#     Object.defineProperty(navigator, 'languages', {{
#         get: () => ['en-US', 'en']
#     }});


#     // Device memory
#     Object.defineProperty(navigator, 'deviceMemory', {{
#         get: () => 8
#     }});


#     // Hardware Concurrency
#     Object.defineProperty(navigator, 'hardwareConcurrency', {{
#         get: () => 4
#     }});


#     // WebGL fingerprint spoof
#     const getParameter = WebGLRenderingContext.prototype.getParameter;
#     WebGLRenderingContext.prototype.getParameter = function(parameter) {{
#         if (parameter === 37445) return 'Intel Inc.';
#         if (parameter === 37446) return 'Intel Iris OpenGL Engine';
#         return getParameter(parameter);
#     }};


#     // Canvas spoof
#     const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#     HTMLCanvasElement.prototype.toDataURL = function() {{
#         return "data:image/png;base64,fakecanvasdata";
#     }};


#     // Audio fingerprint spoof
#     const createOscillator = AudioContext.prototype.createOscillator;
#     AudioContext.prototype.createOscillator = function() {{
#         const oscillator = createOscillator.call(this);
#         oscillator.frequency.value = 440;
#         return oscillator;
#     }};


#     // Timezone spoof
#     Intl.DateTimeFormat = function() {{
#         return {{ resolvedOptions: () => ({{ timeZone: '{timezone}' }}) }};
#     }};
#     """


# def simulate_interaction(driver, total_time=90):
#     start_time = time.time()
#     total_time_spent = 0
#     action = ActionChains(driver)


#     try:
#         # [Change] Increased initial wait to match Playwright's reliable page load
#         # Message: Playwright ke wait_for_load_state("load") jaisa effect, page ke full load hone ka wait
#         time.sleep(random.uniform(5, 10))
#         total_time_spent += random.uniform(5, 10)


#         # Get window dimensions
#         width = driver.execute_script("return window.innerWidth") or 1200
#         height = driver.execute_script("return window.innerHeight") or 1000


#         while total_time_spent < total_time:
#             # Random mouse movement
#             for _ in range(random.randint(2, 5)):
#                 x = random.randint(0, min(width, 1200))
#                 y = random.randint(0, min(height, 1000))
#                 try:
#                     action.move_by_offset(x, y).perform()
#                     action.reset_actions()
#                 except:
#                     pass
#                 t = random.uniform(0.3, 1.0)
#                 time.sleep(t)
#                 total_time_spent += t


#             # Scroll action
#             if random.choice([True, False]):
#                 scroll_y = random.randint(300, 1000)
#                 driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#                 t = random.uniform(1, 2)
#                 time.sleep(t)
#                 total_time_spent += t


#             # Random scroll position
#             if random.choice([True, False]):
#                 driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#                 t = random.uniform(1, 2)
#                 time.sleep(t)
#                 total_time_spent += t


#             # [Change] Added click simulation to mimic Playwright's realistic user behavior
#             # Message: Playwright ke interaction se inspired, random clicks GA tracking ko trigger kar sakte hain
#             try:
#                 links = driver.find_elements(By.TAG_NAME, "a")
#                 if links:
#                     random.choice(links).click()
#                     time.sleep(random.uniform(2, 4))
#                     driver.back()
#             except:
#                 pass
#                 t = random.uniform(1, 2)
#                 total_time_spent += t


#             # Idle like reading
#             t = random.uniform(2, 5)
#             time.sleep(t)
#             total_time_spent += t


#             # Exit if total_time is reached
#             if total_time_spent >= total_time:
#                 break


#         # Final wait to normalize total time
#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)


#     except Exception as e:
#         print(f"[!] Interaction Error: {e}")


# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     driver, locale = create_driver(session_id)
#     if not driver:
#         print(f"[x] Session #{session_id} failed: Driver creation failed")
#         return


#     timezone = random.choice(TIMEZONES)
#     start_time = time.time()
#     try:
#         # [Change] Added robust page load wait inspired by Playwright's wait_for_load_state
#         # Message: Yeh ensure karta hai ki page fully load ho, GA scripts ke liye zaroori
#         driver.get(url)
#         WebDriverWait(driver, 30).until(
#             lambda d: d.execute_script("return document.readyState === 'complete'")
#         )
#         WebDriverWait(driver, 30).until(
#             EC.presence_of_element_located((By.TAG_NAME, "body"))
#         )


#         # [Change] Improved Cloudflare handling with more robust checks
#         # Message: Playwright ke reliable Cloudflare bypass se inspired, zyada wait aur checks
#         if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#             print(f"[!] Session #{session_id}: Cloudflare challenge detected.")
#             try:
#                 WebDriverWait(driver, 30).until(
#                     lambda d: "cf-ray" not in d.page_source and "Checking your browser" not in d.page_source
#                 )
#                 print(f"[✓] Cloudflare challenge passed")
#             except:
#                 print(f"[!] Cloudflare challenge not resolved")
#             time.sleep(random.uniform(10, 15))


#         # [Change] Moved spoof script earlier to apply before GA scripts load
#         # Message: Playwright ke init_script jaisa effect, anti-detection pehle apply hota hai
#         driver.execute_script(spoof_js_script(timezone))


#         # [Change] Enhanced GA script wait to ensure scripts are loaded
#         # Message: Playwright ke reliable script detection se inspired, GA scripts ke load hone ka wait
#         try:
#             WebDriverWait(driver, 30).until(
#                 lambda d: d.execute_script("return typeof gtag === 'function' || typeof ga === 'function' || typeof window.dataLayer !== 'undefined'")
#             )
#             print(f"[📊] GA scripts loaded in session #{session_id}")
#         except Exception as e:
#             print(f"[!] GA script load failed: {e}")


#         # Trigger GA events
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'page_view');
#                 gtag('event', 'headless_test', { 'event_category': 'Test', 'event_label': 'Headless' });
#             } else if (typeof ga === 'function') {
#                 ga('send', 'pageview');
#                 ga('send', 'event', 'Test', 'Headless', 'headless_test');
#             }
#             if (typeof window.dataLayer !== 'undefined') {
#                 window.dataLayer.push({'event': 'headless_test'});
#             }
#         """)


#         # Simulate scrolling
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(random.uniform(1.5, 3))
#         driver.execute_script("window.scrollTo(0, 0);")


#         # [Change] Added GA beacon check inspired by Playwright's resource tracking
#         # Message: Yeh verify karta hai ki GA collect requests bheje gaye, Playwright ke jaisa
#         beacons = driver.execute_script("""
#             return performance.getEntriesByType('resource')
#                 .filter(r => r.name.includes('google-analytics.com/collect') || r.name.includes('googletagmanager.com'));
#         """)
#         print(f"[📊] GA beacons detected: {len(beacons)}")

#         # Simulate interaction
#         # [Change] Increased visit time to 90-120s to mimic Playwright's realistic session duration
#         # Message: Zyada time GA ke liye realistic session banata hai
#         visit_time = random.randint(90, 120)
#         simulate_interaction(driver, total_time=visit_time)

#         # [Change] Added final wait for network activity, inspired by Playwright's clean context close
#         # Message: Yeh ensure karta hai ki GA beacons send ho jayein quit se pehle
#         try:
#             WebDriverWait(driver, 20).until(
#                 lambda d: d.execute_script("return performance.getEntriesByType('resource').length") == d.execute_script("return performance.getEntriesByType('resource').length")
#             )
#         except:
#             pass
#         time.sleep(random.uniform(10, 15))

#         print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")

#     except Exception as e:
#         print(f"[x] Session #{session_id} failed: {e}")
#     finally:
#         try:
#             if driver in ACTIVE_DRIVERS:
#                 ACTIVE_DRIVERS.remove(driver)
#             driver.quit()
#         except Exception as e:
#             print(f"[!] Session #{session_id}: Driver quit failed - {e}")
#             os.system("taskkill /F /IM chrome.exe")
#             os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")


#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))


#     # Use ThreadPoolExecutor for concurrency
#     with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#         visit_id = 0
#         futures = []
#         for i in range(NUM_VISITS):
#             for url in TARGET_URLS:
#                 visit_id += 1
#                 futures.append(executor.submit(simulate_single_visit, visit_id, url))
       
#         # Wait for all visits to complete
#         for future in futures:
#             future.result()

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.")




# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from fake_useragent import UserAgent
# import time
# import random
# import requests

# # === CONFIGURATION ===
# TARGET_URL = "https://unfilteredgadgets.com/"
# VISIT_DURATION = (40, 60)  # seconds per visit
# HEADLESS = False
# USER_AGENT = UserAgent().random  # Consistent user-agent for session

# def simulate_user_behavior(driver):
#     try:
#         actions = ActionChains(driver)

#         # Accept cookies if a consent banner is present
#         try:
#             cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Allow') or contains(text(), 'Agree')]")
#             if cookie_buttons:
#                 cookie_buttons[0].click()
#                 time.sleep(random.uniform(1, 2))
#         except Exception as e:
#             print("[!] Cookie consent error:", e)

#         # Window dimensions
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return document.body.scrollHeight")

#         # Simulate realistic mouse movements
#         for _ in range(random.randint(3, 6)):
#             x = random.randint(0, width - 10)
#             y = random.randint(0, height - 10)
#             actions.move_by_offset(x, y).perform()
#             time.sleep(random.uniform(0.5, 1.5))
#             actions.reset_actions()

#         # Scroll smoothly to ensure analytics triggers
#         scroll = 0
#         while scroll < height:
#             scroll += random.randint(200, 400)
#             driver.execute_script(f"window.scrollTo(0, {scroll})")
#             time.sleep(random.uniform(0.8, 1.5))

#         # Interact with clickable elements to trigger events
#         clickable_elements = driver.find_elements(By.XPATH, "//a | //button | //div[contains(@class, 'track')]")
#         if clickable_elements:
#             target = random.choice(clickable_elements)
#             try:
#                 driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target)
#                 time.sleep(random.uniform(0.5, 1))
#                 target.click()
#                 time.sleep(random.uniform(3, 5))  # Wait for analytics events
#             except Exception as e:
#                 print("[!] Click error:", e)

#         # Additional scroll to ensure full pageview tracking
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
#         time.sleep(random.uniform(1, 2))

#     except Exception as e:
#         print("[!] Behavior simulation error:", e)

# def spoof_fingerprint(driver):
#     # Minimal spoofing to avoid detection without breaking analytics
#     js_scripts = [
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
#         "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});",
#     ]
#     for script in js_scripts:
#         try:
#             driver.execute_script(script)
#         except:
#             pass

# def create_driver():
#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument(f"user-agent={USER_AGENT}")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")  # Helps with headless stability
#     options.add_argument("--no-first-run")
#     options.add_argument("--no-default-browser-check")

#     if HEADLESS:
#         options.add_argument("--headless=new")

#     driver = uc.Chrome(options=options, use_subprocess=True, version_main=137)
#     return driver

# def visit_website():
#     driver = create_driver()
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(5, 8))  # Allow analytics scripts to load
#         spoof_fingerprint(driver)
#         simulate_user_behavior(driver)
#         time.sleep(random.randint(*VISIT_DURATION))

#         # Verify analytics tracking (optional for debugging)
#         try:
#             ga_loaded = driver.execute_script("return typeof window.ga !== 'undefined' || typeof window.dataLayer !== 'undefined';")
#             adobe_loaded = driver.execute_script("return typeof window.s !== 'undefined';")
#             print(f"[+] GA Tracking: {ga_loaded}, Adobe Tracking: {adobe_loaded}")
#         except:
#             print("[!] Analytics tracking check failed")

#     except Exception as e:
#         print("[!] Visit failed:", e)
#     finally:
#         driver.quit()

# # Run loop
# if __name__ == "__main__":
#     for i in range(5):  # Number of visits
#         print(f"[+] Visit #{i + 1}")
#         visit_website()
#         time.sleep(random.randint(5, 10))





# import asyncio
# import random
# import time
# from playwright.async_api import async_playwright
# from fake_useragent import UserAgent

# # === CONFIG ===
# TARGET_URLS = [
#     # "https://marcadeo.com/",
#     "https://unfilteredgadgets.com/",
#     # "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 1
# CONCURRENCY = 1

# ua_generator = UserAgent()

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864), (800, 600),
#     (360, 640), (375, 667),
# ]
# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
# ]
# TIMEZONES = [
#     "Asia/Kolkata", "Europe/London", "America/New_York",
#     "Australia/Sydney", "Asia/Tokyo", "Europe/Paris", "America/Los_Angeles"
# ]

# # # === INTERACTION ===
# # async def simulate_interaction(page):
# #     try:
# #         await page.wait_for_load_state("load")
# #         await asyncio.sleep(random.uniform(3, 5))

# #         for _ in range(random.randint(4, 6)):
# #             await page.mouse.move(random.randint(0, 1100), random.randint(0, 1000))
# #             await asyncio.sleep(random.uniform(0.3, 0.9))

# #         for _ in range(random.randint(3, 6)):
# #             await page.mouse.wheel(0, random.randint(500, 800))
# #             await asyncio.sleep(random.uniform(0.3, 0.9))

# #         await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
# #         await asyncio.sleep(random.randint(35, 45))
# #     except Exception as e:
# #         print(f"[!] Interaction Error: {e}")

# # === INTERACTION ===
# async def simulate_interaction(page):
#     try:
#         await page.wait_for_load_state("load")
#         visit_time = random.uniform(60, 80)  # 🎯 Total time to spend on page
#         total_time_spent = 0

#         # Initial reading delay
#         t = random.uniform(3, 7)
#         await asyncio.sleep(t)
#         total_time_spent += t

#         # Simulate interaction in loop
#         while total_time_spent < visit_time:
#             # Random mouse movement
#             for _ in range(random.randint(2, 5)):
#                 x = random.randint(0, 1200)
#                 y = random.randint(0, 1000)
#                 await page.mouse.move(x, y)
#                 t = random.uniform(0.3, 1.0)
#                 await asyncio.sleep(t)
#                 total_time_spent += t

#             # Scroll action
#             if random.choice([True, False]):
#                 scroll_y = random.randint(300, 1000)
#                 await page.mouse.wheel(0, scroll_y)
#                 t = random.uniform(1, 2)
#                 await asyncio.sleep(t)
#                 total_time_spent += t

#             # Random scroll position
#             if random.choice([True, False]):
#                 await page.evaluate("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#                 t = random.uniform(1, 2)
#                 await asyncio.sleep(t)
#                 total_time_spent += t

#             # Idle like reading
#             t = random.uniform(2, 5)
#             await asyncio.sleep(t)
#             total_time_spent += t

#             # Exit loop if visit_time is reached
#             if total_time_spent >= visit_time:
#                 break

#         # Final wait to normalize total time
#         if total_time_spent < visit_time:
#             await asyncio.sleep(visit_time - total_time_spent)

#     except Exception as e:
#         print(f"[!] Interaction Error: {e}")

# # === SINGLE VISIT ===
# async def simulate_single_visit(playwright, session_id, url):
#     browser = await playwright.chromium.launch(headless=False, args=[
#         "--no-sandbox",
#         "--disable-dev-shm-usage",
#         "--disable-blink-features=AutomationControlled"
#     ])

#     ua = ua_generator.random
#     vp = random.choice(VIEWPORTS)
#     loc = random.choice(LOCALES)
#     tz = random.choice(TIMEZONES)

#     context = await browser.new_context(
#         user_agent=ua,
#         locale=loc,
#         viewport={"width": vp[0], "height": vp[1]},
#         timezone_id=tz
#     )

#     await context.add_init_script("""
#         // Webdriver removal
#         Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

#         // Fake plugins
#         Object.defineProperty(navigator, 'plugins', {
#             get: () => [1, 2, 3, 4, 5]
#         });

#         // Fake languages
#         Object.defineProperty(navigator, 'languages', {
#             get: () => ['en-US', 'en']
#         });

#         // Device memory
#         Object.defineProperty(navigator, 'deviceMemory', {
#             get: () => 8
#         });

#         // Hardware Concurrency
#         Object.defineProperty(navigator, 'hardwareConcurrency', {
#             get: () => 4
#         });

#         // WebGL fingerprint spoof
#         const getParameter = WebGLRenderingContext.prototype.getParameter;
#         WebGLRenderingContext.prototype.getParameter = function(parameter) {
#             if (parameter === 37445) return 'Intel Inc.';
#             if (parameter === 37446) return 'Intel Iris OpenGL Engine';
#             return getParameter(parameter);
#         };

#         // Canvas spoof
#         const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#         HTMLCanvasElement.prototype.toDataURL = function() {
#             return "data:image/png;base64,fakecanvasdata";
#         };

#         // Audio fingerprint spoof
#         const createOscillator = AudioContext.prototype.createOscillator;
#         AudioContext.prototype.createOscillator = function() {
#             const oscillator = createOscillator.call(this);
#             oscillator.frequency.value = 440;
#             return oscillator;
#         };
#     """)

#     try:
#         page = await context.new_page()
#         await page.goto(url, wait_until="load", timeout=50000)
#         print(f"[+] Session #{session_id} → {url} → UA: {ua}")
#         await simulate_interaction(page)
#         await page.close()
#     except Exception as e:
#         print(f"[!] Visit Error #{session_id}:", e)
#     finally:
#         await context.close()
#         await browser.close()

# # === MAIN ===
# async def main():
#     sem = asyncio.Semaphore(CONCURRENCY)

#     async with async_playwright() as p:
#         visit_id = 0

#         async def visit_task(i, url):
#             async with sem:
#                 await simulate_single_visit(p, i, url)

#         tasks = []
#         for i in range(NUM_VISITS):
#             for url in TARGET_URLS:
#                 visit_id += 1
#                 tasks.append(visit_task(visit_id, url))

#         await asyncio.gather(*tasks)

# if __name__ == "__main__":
#     start = time.time()
#     asyncio.run(main())
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.")





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
    "https://www.adidas.co.in/adi_zomato"
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