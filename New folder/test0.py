#Done
# import undetected_chromedriver as uc 
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from fake_useragent import UserAgent
# import time
# import random
# import requests

# # === CONFIGURATION ===
# # TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# TARGET_URL = "https://marcadeo.com/"
# PROXY_LIST_URL = ""  # Optional
# VISIT_DURATION = (30, 60)  # seconds per visit
# SCROLL_PAUSE = 2 
# HEADLESS = False

# def get_random_proxy():
#     try:
#         proxy_list = requests.get(PROXY_LIST_URL).text.splitlines()
#         return random.choice(proxy_list).strip()
#     except:
#         return None

# def realistic_scroll(driver):
#     scroll_height = driver.execute_script("return document.body.scrollHeight")
#     current_position = 0
#     while current_position < scroll_height:
#         step = random.randint(200, 500)
#         driver.execute_script(f"window.scrollBy(0, {step});")
#         current_position += step
#         time.sleep(random.uniform(0.5, 1.5))

# def simulate_mouse_movements(driver):
#     try:
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")
#         actions = ActionChains(driver)
#         for _ in range(random.randint(5, 15)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             actions.move_by_offset(x, y).perform()
#             time.sleep(random.uniform(0.2, 0.8))
#             actions.reset_actions()
#     except Exception:
#         pass

# def create_driver(proxy=None):
#     ua = UserAgent().random
#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument(f"user-agent={ua}")

#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")

#     if HEADLESS:
#         options.add_argument("--headless=new")

#     driver = uc.Chrome(options=options, use_subprocess=True)
#     return driver

# def visit_website():
#     proxy = get_random_proxy()
#     driver = create_driver(proxy)
#     driver.get(TARGET_URL)

#     # Allow JS to render
#     time.sleep(random.uniform(3, 5))

#     # === Fingerprint Evasion ===
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#     driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
#     driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})")
#     driver.execute_script("Object.defineProperty(navigator, 'platform', {get: () => 'Win32'})")

#     # === Interaction ===
#     simulate_mouse_movements(driver)
#     realistic_scroll(driver)

#     # Stay on page
#     time.sleep(random.randint(*VISIT_DURATION))
#     driver.quit()

# # === Run multiple visits ===
# if __name__ == "__main__":
#     for i in range(10):  # Number of visits
#         print(f"[+] Visit #{i + 1}")
#         visit_website()
#         time.sleep(random.randint(5, 10))  # Random delay between visits


# Done
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from fake_useragent import UserAgent
# import time
# import random
# import requests

# # === CONFIGURATION ===
# # TARGET_URL = "https://marcadeo.com/"
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# PROXY_LIST_URL = ""  # Optional
# VISIT_DURATION = (40, 60)  # seconds per visit
# HEADLESS = False
 
# def get_random_proxy():
#     if not PROXY_LIST_URL:
#         return None
#     try:
#         proxy_list = requests.get(PROXY_LIST_URL).text.splitlines()
#         return random.choice(proxy_list).strip()
#     except:
#         return None

# def simulate_user_behavior(driver):
#     try:
#         actions = ActionChains(driver)

#         # Window dimensions
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")

#         # Mouse hover/move
#         for _ in range(random.randint(5, 10)):
#             x = random.randint(0, width - 10)
#             y = random.randint(0, height - 10)
#             actions.move_by_offset(x, y).perform()
#             time.sleep(random.uniform(0.3, 0.9))
#             actions.reset_actions()

#         # Scroll down slowly
#         total_height = driver.execute_script("return document.body.scrollHeight")
#         scroll = 0
#         while scroll < total_height:
#             scroll += random.randint(300, 500)
#             driver.execute_script(f"window.scrollTo(0, {scroll})")
#             time.sleep(random.uniform(1.0, 2.0))

#         # Random click
#         clickable_elements = driver.find_elements(By.XPATH, "//a | //button")
#         if clickable_elements:
#             target = random.choice(clickable_elements)
#             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target)
#             time.sleep(random.uniform(1, 2))
#             target.click()
#             time.sleep(random.uniform(5, 10))  # wait after click

#         # Scroll again after click
#         total_height = driver.execute_script("return document.body.scrollHeight")
#         scroll = 0
#         while scroll < total_height:
#             scroll += random.randint(300, 600)
#             driver.execute_script(f"window.scrollTo(0, {scroll})")
#             time.sleep(random.uniform(1.2, 2.5))

#     except Exception as e:
#         print("[!] Behavior simulation error:", e)

# def spoof_fingerprint(driver):
#     js_scripts = [
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
#         "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});",
#         "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});",
#         "Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});",
#         "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});",
#         "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});",
#         "Object.defineProperty(navigator, 'connection', {get: () => ({downlink: 10, effectiveType: '4g'})});"
#     ]
#     for script in js_scripts:
#         try:
#             driver.execute_script(script)
#         except:
#             pass

# def create_driver(proxy=None):
#     ua = UserAgent().random
#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument(f"user-agent={ua}")

#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")

#     if HEADLESS:
#         options.add_argument("--headless=new")

#     driver = uc.Chrome(options=options, use_subprocess=True,version_main=137)
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



import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
import time
import random
import requests
from multiprocessing import Pool

# === CONFIGURATION ===
TARGET_URL = "https://www.adidas.co.in/adi_zomato"
PROXY_LIST_URL = ""  # Optional
VISIT_DURATION = (30, 60)
SCROLL_PAUSE = 2
HEADLESS = False
CONCURRENT_BOTS = 1  # Concurrent browsers
TOTAL_VISITS = 4

def get_random_proxy(): 
    try:
        proxy_list = requests.get(PROXY_LIST_URL).text.splitlines()
        return random.choice(proxy_list).strip()
    except:
        return None

def realistic_scroll(driver):
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    while current_position < scroll_height:
        step = random.randint(200, 500)
        driver.execute_script(f"window.scrollBy(0, {step});")
        current_position += step
        time.sleep(random.uniform(0.5, 1.5))

def simulate_mouse_movements(driver):
    try:
        width = driver.execute_script("return window.innerWidth")
        height = driver.execute_script("return window.innerHeight")
        actions = ActionChains(driver)
        for _ in range(random.randint(5, 10)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            actions.move_by_offset(x, y).perform()
            time.sleep(random.uniform(0.3, 0.8))
            actions.reset_actions()
    except Exception:
        pass

def create_driver(proxy=None):
    ua = UserAgent().random
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("window-size=1920,1080")
    options.add_argument(f"user-agent={ua}")

    if proxy:
        options.add_argument(f"--proxy-server=http://{proxy}")

    if HEADLESS:
        options.add_argument("--headless=new")

    driver = uc.Chrome(options=options, use_subprocess=True)
    return driver

def visit_website(visit_id):
    proxy = get_random_proxy()
    driver = create_driver(proxy)
    try:
        driver.get(TARGET_URL)

        # Let GA/Adobe scripts load
        time.sleep(random.uniform(3, 5))

        # Fingerprint evasion
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})")
        driver.execute_script("Object.defineProperty(navigator, 'platform', {get: () => 'Win32'})")

        simulate_mouse_movements(driver)
        realistic_scroll(driver)

        # Add click to trigger GA
        try:
            elements = driver.find_elements(By.XPATH, "//*")
            random.choice(elements).click()
        except:
            pass

        time.sleep(random.randint(*VISIT_DURATION))
        print(f"[✓] Visit #{visit_id} completed")
    except Exception as e:
        print(f"[x] Visit #{visit_id} failed:", e)
    finally:
        driver.quit()

# === Concurrency Handler ===
if __name__ == "__main__":
    with Pool(CONCURRENT_BOTS) as p:
        p.map(visit_website, list(range(1, TOTAL_VISITS + 1)))




#Done
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from fake_useragent import UserAgent
# import time
# import random
# import requests
# from multiprocessing import Pool 
# from tempfile import mkdtemp

# # === CONFIGURATION ===
# # https://www.adidas.co.in/adi_zomato
# TARGET_URL = "https://marcadeo.com/"
# # TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# VISIT_DURATION = (30, 60)  # Visit time in seconds
# SCROLL_PAUSE = 2
# HEADLESS = False
# CONCURRENT_BOTS = 2
# TOTAL_VISITS = 4
# CHROME_VERSION = 137

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864), (800, 600),
#     (360, 640), (375, 667),
# ]

# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
# ]

# # === Realistic User Actions ===
# def simulate_user_behavior(driver, total_time=70):
#     start = time.time()
#     actions = ActionChains(driver)
#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")

#     while time.time() - start < total_time:
#         # Move mouse
#         for _ in range(random.randint(2, 4)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             try:
#                 actions.move_by_offset(x, y).perform()
#                 actions.reset_actions()
#             except:
#                 pass
#             time.sleep(random.uniform(0.3, 1.0))

#         # Scroll
#         if random.choice([True, False]):
#             scroll_y = random.randint(300, 1000)
#             driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#             time.sleep(random.uniform(1, 2))

#         # Jump scroll
#         if random.choice([True, False]):
#             driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#             time.sleep(random.uniform(1, 2))

#         time.sleep(random.uniform(2, 5))

# # === Chrome Driver Setup ===
# def create_driver():
#     ua = UserAgent().random
#     vp = random.choice(VIEWPORTS)
#     locale = random.choice(LOCALES)
#     tmp_profile = mkdtemp()

#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"user-agent={ua}")
#     options.add_argument("window-size={},{}".format(vp[0], vp[1]))
#     if HEADLESS:
#         options.add_argument("--headless=new")
#         options.add_argument("--disable-gpu")
#         options.add_argument("--disable-dev-shm-usage")

#     driver = uc.Chrome(
#         version_main=137,
#         options=options,
#         user_data_dir=tmp_profile,
#         use_subprocess=True
#     )
#     return driver

# # === Visit Function ===
# def visit_website(visit_id):
#     driver = create_driver()
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 6))  # Wait for GA to load

#         # Inject stealth/fingerprint overrides
#         driver.execute_script("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
#             Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
#             Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
#             Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});
#             Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});

#             // Canvas spoof
#             const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#             HTMLCanvasElement.prototype.toDataURL = function() {
#                 return "data:image/png;base64,fakecanvasdata";
#             };

#             // WebGL spoof
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(param) {
#                 if (param === 37445) return 'Intel Inc.';
#                 if (param === 37446) return 'Intel Iris OpenGL Engine';
#                 return getParameter.call(this, param);
#             };
#         """)

#         # Trigger some interaction for analytics
#         simulate_user_behavior(driver, total_time=random.randint(*VISIT_DURATION))

#         # Random click
#         elements = driver.find_elements(By.XPATH, "//*")
#         if elements:
#             random.choice(elements).click()

#         print(f"[✓] Visit #{visit_id} completed")
#     except Exception as e:
#         print(f"[x] Visit #{visit_id} failed:", e)
#     finally:
#         driver.quit()

# # === Main Execution ===
# if __name__ == "__main__":
#     print("[✓] ChromeDriver preloaded")
#     with Pool(CONCURRENT_BOTS) as p:
#         p.map(visit_website, list(range(1, TOTAL_VISITS + 1)))




# Done 
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from fake_useragent import UserAgent
# import time
# import random 
# from tempfile import mkdtemp
# from multiprocessing import get_context

# # === CONFIGURATION ===
# TARGET_URL = "https://marcadeo.com/"
# VISIT_DURATION = (10, 30)
# SCROLL_PAUSE = 2
# HEADLESS = True
# CONCURRENT_BOTS = 1
# TOTAL_VISITS = 10
# CHROME_VERSION = 137

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864), (800, 600),
#     (360, 640), (375, 667),
# ]

# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
# ]

# # === Realistic User Actions ===
# def simulate_user_behavior(driver, total_time=70):
#     start = time.time()
#     actions = ActionChains(driver)
#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")

#     while time.time() - start < total_time:
#         for _ in range(random.randint(2, 4)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             try:
#                 actions.move_by_offset(x, y).perform()
#                 actions.reset_actions()
#             except:
#                 pass
#             time.sleep(random.uniform(0.3, 1.0))

#         if random.choice([True, False]):
#             scroll_y = random.randint(300, 1000)
#             driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#             time.sleep(random.uniform(1, 2))

#         if random.choice([True, False]):
#             driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#             time.sleep(random.uniform(1, 2))

#         time.sleep(random.uniform(2, 5))

# # === Chrome Driver Setup ===
# def create_driver():
#     ua = UserAgent().random
#     vp = random.choice(VIEWPORTS)
#     locale = random.choice(LOCALES)
#     tmp_profile = mkdtemp()

#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"user-agent={ua}")
#     options.add_argument("window-size={},{}".format(vp[0], vp[1]))
#     if HEADLESS:
#         options.add_argument("--headless=new")
#         options.add_argument("--disable-gpu")
#         options.add_argument("--disable-dev-shm-usage")

#     driver = uc.Chrome(
#         version_main=CHROME_VERSION,
#         options=options,
#         user_data_dir=tmp_profile,
#         use_subprocess=True
#     )
#     return driver

# # === Visit Function ===
# def visit_website(visit_id):
#     driver = create_driver()
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 6))

#         driver.execute_script("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
#             Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
#             Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
#             Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});
#             Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
#             const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#             HTMLCanvasElement.prototype.toDataURL = function() {
#                 return "data:image/png;base64,fakecanvasdata";
#             };
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(param) {
#                 if (param === 37445) return 'Intel Inc.';
#                 if (param === 37446) return 'Intel Iris OpenGL Engine';
#                 return getParameter.call(this, param);
#             };
#         """)

#         simulate_user_behavior(driver, total_time=random.randint(*VISIT_DURATION))

#         elements = driver.find_elements(By.XPATH, "//*")
#         if elements:
#             random.choice(elements).click()

#         print(f"[✓] Visit #{visit_id} completed")
#     except Exception as e:
#         print(f"[x] Visit #{visit_id} failed:", e)
#     finally:
#         driver.quit()

# # === Main Execution ===
# if __name__ == "__main__":
#     print("[✓] ChromeDriver preloaded")
#     ctx = get_context("spawn")
#     with ctx.Pool(CONCURRENT_BOTS) as p:
#         p.map(visit_website, list(range(1, TOTAL_VISITS + 1)))


# Done
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from fake_useragent import UserAgent
# import time
# import random 
# from tempfile import mkdtemp
# from multiprocessing import get_context

# # === CONFIGURATION ===
# TARGET_URL = "https://marcadeo.com/"
# VISIT_DURATION = (10, 30)
# SCROLL_PAUSE = 2
# HEADLESS = False
# CONCURRENT_BOTS = 1
# TOTAL_VISITS = 10
# CHROME_VERSION = 137

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864), (800, 600),
#     (360, 640), (375, 667),
# ]

# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
# ]

# # === Realistic User Actions ===
# def simulate_user_behavior(driver, total_time=70):
#     start = time.time()
#     actions = ActionChains(driver)
#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")

#     while time.time() - start < total_time:
#         for _ in range(random.randint(2, 4)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             try:
#                 actions.move_by_offset(x, y).perform()
#                 actions.reset_actions()
#             except:
#                 pass
#             time.sleep(random.uniform(0.3, 1.0))

#         if random.choice([True, False]):
#             scroll_y = random.randint(300, 1000)
#             driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#             time.sleep(random.uniform(1, 2))

#         if random.choice([True, False]):
#             driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#             time.sleep(random.uniform(1, 2))

#         time.sleep(random.uniform(2, 5))

# # === Chrome Driver Setup ===
# def create_driver():
#     ua = UserAgent().random
#     vp = random.choice(VIEWPORTS)
#     locale = random.choice(LOCALES)
#     tmp_profile = mkdtemp()

#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"user-agent={ua}")
#     options.add_argument("window-size={},{}".format(vp[0], vp[1]))
#     if HEADLESS:
#         options.add_argument("--headless=new")
#         options.add_argument("--disable-gpu")
#         options.add_argument("--disable-dev-shm-usage")

#     driver = uc.Chrome(
#         version_main=CHROME_VERSION,
#         options=options,
#         user_data_dir=tmp_profile,
#         use_subprocess=True
#     )
#     return driver

# # === Visit Function ===
# def visit_website(visit_id):
#     driver = create_driver()
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 6))

#         driver.execute_script("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
#             Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
#             Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
#             Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});
#             Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
#             const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#             HTMLCanvasElement.prototype.toDataURL = function() {
#                 return "data:image/png;base64,fakecanvasdata";
#             };
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(param) {
#                 if (param === 37445) return 'Intel Inc.';
#                 if (param === 37446) return 'Intel Iris OpenGL Engine';
#                 return getParameter.call(this, param);
#             };
#         """)

#         simulate_user_behavior(driver, total_time=random.randint(*VISIT_DURATION))

#         try:
#             elements = driver.find_elements(By.XPATH, "//*")
#             if elements:
#                 random.choice(elements).click()
#         except Exception as click_err:
#             print(f"[!] Visit #{visit_id}: Click failed but continuing -", click_err)

#         print(f"[✓] Visit #{visit_id} completed")
#     except Exception as e:
#         print(f"[x] Visit #{visit_id} failed:", e)
#     finally:
#         driver.quit()

# # === Main Execution ===
# if __name__ == "__main__":
#     print("[✓] ChromeDriver preloaded")
#     ctx = get_context("spawn")
#     with ctx.Pool(CONCURRENT_BOTS) as p:
#         p.map(visit_website, list(range(1, TOTAL_VISITS + 1))) 




# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import os

# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")

# options = Options()
# options.binary_location = CHROME_BINARY

# service = Service(CHROMEDRIVER_PATH)
# driver = webdriver.Chrome(service=service, options=options)

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import undetected_chromedriver as uc
# import os

# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")

# # Create UC options
# options = uc.ChromeOptions()
# options.binary_location = CHROME_BINARY

# # Headless + additional anti-detection options
# options.add_argument("--headless=new")  # Use `--headless=new` for Chrome 109+
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-gpu")
# options.add_argument("--disable-dev-shm-usage")

# driver = uc.Chrome(
#     driver_executable_path=CHROMEDRIVER_PATH,
#     options=options,
#     version_main=137,  # Match your Chrome version
#     headless=True
# )

# # Test if it works
# driver.get("https://www.google.com")
# print("Page title:", driver.title)
# driver.quit()



# import os
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# import undetected_chromedriver as uc

# # Paths
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")

# # Verify paths
# print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
# print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

# # Clean up previous processes
# os.system("taskkill /F /IM chrome.exe")
# os.system("taskkill /F /IM chromedriver.exe")

# # Create UC options
# options = uc.ChromeOptions()
# options.binary_location = CHROME_BINARY
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--no-sandbox")
# options.add_argument("--remote-debugging-port=9222")  # Avoid port conflicts

# # Initialize driver
# service = Service(CHROMEDRIVER_PATH, log_path="chromedriver.log")
# try:
#     driver = uc.Chrome(
#         service=service,
#         options=options,
#         headless=False  # Test without headless first
#     )
#     # Test navigation
#     driver.get("https://www.google.com")
#     print("Page title:", driver.title)
# finally:
#     driver.quit()



# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from fake_useragent import UserAgent
# import time
# import random
# from tempfile import mkdtemp
# import os
# import signal
# import sys

# # === CONFIGURATION ===
# TARGET_URL = "https://marcadeo.com/"
# VISIT_DURATION = (10, 30)
# SCROLL_PAUSE = 2
# HEADLESS = False
# CONCURRENT_BOTS = 1
# TOTAL_VISITS = 10

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

# # Track active drivers
# ACTIVE_DRIVERS = []

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

# def simulate_user_behavior(driver, total_time=70):
#     start = time.time()
#     actions = ActionChains(driver)
#     try:
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")
#     except Exception as e:
#         print(f"Failed to get window dimensions: {e}")
#         return

#     while time.time() - start < total_time:
#         for _ in range(random.randint(2, 4)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             try:
#                 actions.move_by_offset(x, y).perform()
#                 actions.reset_actions()
#             except:
#                 pass
#             time.sleep(random.uniform(0.3, 1.0))

#         if random.choice([True, False]):
#             scroll_y = random.randint(300, 1000)
#             driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#             time.sleep(random.uniform(1, 2))

#         if random.choice([True, False]):
#             driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#             time.sleep(random.uniform(1, 2))

#         time.sleep(random.uniform(2, 5))

# def create_driver():
#     ua = UserAgent().random
#     vp = random.choice(VIEWPORTS)
#     locale = random.choice(LOCALES)
#     tmp_profile = mkdtemp()

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--remote-debugging-port=0")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     service = Service(CHROMEDRIVER_PATH, log_path="chromedriver.log")
#     try:
#         driver = uc.Chrome(
#             service=service,
#             options=options,
#             user_data_dir=tmp_profile,
#             use_subprocess=True,
#             headless=HEADLESS,
#         )
#         ACTIVE_DRIVERS.append(driver)
#         return driver
#     except Exception as e:
#         print(f"Failed to create driver: {e}")
#         return None

# def visit_website(visit_id):
#     print(f"[*] Starting visit #{visit_id}")
#     driver = create_driver()
#     if not driver:
#         print(f"[x] Visit #{visit_id} failed: Driver creation failed")
#         return

#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 6))

#         driver.execute_script("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
#             Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
#             Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
#             Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});
#             Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
#             const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#             HTMLCanvasElement.prototype.toDataURL = function() {
#                 return "data:image/png;base64,fakecanvasdata";
#             };
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(param) {
#                 if (param === 37445) return 'Intel Inc.';
#                 if (param === 37446) return 'Intel Iris OpenGL Engine';
#                 return getParameter.call(this, param);
#             };
#         """)

#         simulate_user_behavior(driver, total_time=random.randint(*VISIT_DURATION))

#         try:
#             elements = driver.find_elements(By.XPATH, "//*")
#             if elements:
#                 random.choice(elements).click()
#         except Exception as click_err:
#             print(f"[!] Visit #{visit_id}: Click failed but continuing - {click_err}")

#         print(f"[✓] Visit #{visit_id} completed")
#     except Exception as e:
#         print(f"[x] Visit #{visit_id} failed: {e}")
#     finally:
#         try:
#             if driver in ACTIVE_DRIVERS:
#                 ACTIVE_DRIVERS.remove(driver)
#             driver.quit()
#         except Exception as e:
#             print(f"[!] Visit #{visit_id}: Driver quit failed - {e}")
#             os.system("taskkill /F /IM chrome.exe")
#             os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)
    
#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

#     for i in range(1, TOTAL_VISITS + 1):
#         visit_website(i)
#         time.sleep(random.uniform(5, 10))  # Increased delay

# if __name__ == "__main__":
#     main()





# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from fake_useragent import UserAgent
# import time
# import random
# from tempfile import mkdtemp
# import os
# import signal
# import sys

# # === CONFIGURATION ===
# TARGET_URL = "https://marcadeo.com/"
# VISIT_DURATION = (10, 30)
# SCROLL_PAUSE = 2
# HEADLESS = True
# CONCURRENT_BOTS = 1
# TOTAL_VISITS = 10

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

# ACTIVE_DRIVERS = []

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
#     ua = UserAgent()
#     browsers = ['chrome', 'firefox', 'safari', 'edge']
#     try:
#         return getattr(ua, random.choice(browsers))
#     except:
#         return ua.random

# def create_driver():
#     ua_string = get_random_user_agent()
#     vp = random.choice(VIEWPORTS)
#     locale = random.choice(LOCALES)
#     tmp_profile = mkdtemp()
#     profile_folder = os.path.join("browser_profiles", f"profile_{random.randint(1, 999999)}")
#     os.makedirs("browser_profiles", exist_ok=True)

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--remote-debugging-port=0")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"user-agent={ua_string}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     if random.choice([True, False]):
#         mobile_emulation = {
#             "deviceMetrics": {"width": vp[0], "height": vp[1], "pixelRatio": random.choice([2.0, 3.0])},
#             "userAgent": ua_string
#         }
#         options.add_experimental_option("mobileEmulation", mobile_emulation)

#     service = Service(CHROMEDRIVER_PATH, log_path="chromedriver.log")

#     try:
#         driver = uc.Chrome(
#             service=service,
#             options=options,
#             user_data_dir=tmp_profile,
#             use_subprocess=True,
#             headless=HEADLESS,
#         )
#         driver.set_window_size(vp[0], vp[1])
#         ACTIVE_DRIVERS.append(driver)
#         return driver, locale
#     except Exception as e:
#         print(f"Failed to create driver: {e}")
#         return None, None

# def simulate_user_behavior(driver, total_time=70):
#     start = time.time()
#     actions = ActionChains(driver)
#     try:
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")
#     except Exception as e:
#         print(f"Failed to get window dimensions: {e}")
#         return

#     while time.time() - start < total_time:
#         for _ in range(random.randint(2, 4)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             try:
#                 actions.move_by_offset(x, y).perform()
#                 actions.reset_actions()
#             except:
#                 pass
#             time.sleep(random.uniform(0.3, 1.0))

#         if random.choice([True, False]):
#             scroll_y = random.randint(300, 1000)
#             driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#             time.sleep(random.uniform(1, 2))

#         if random.choice([True, False]):
#             driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#             time.sleep(random.uniform(1, 2))

#         time.sleep(random.uniform(2, 5))

# def visit_website(visit_id):
#     print(f"[*] Starting visit #{visit_id}")
#     driver, locale = create_driver()
#     if not driver:
#         print(f"[x] Visit #{visit_id} failed: Driver creation failed")
#         return

#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 6))

#         driver.execute_script(f"""
#             Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
#             Object.defineProperty(navigator, 'plugins', {{get: () => [1, 2, 3, 4, 5]}});
#             Object.defineProperty(navigator, 'languages', {{get: () => ['{locale}', 'en']}});

#             Object.defineProperty(navigator, 'deviceMemory', {{get: () => {random.choice([4, 8, 12, 16])}}});
#             Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {random.choice([2, 4, 6, 8])}}});
#             Object.defineProperty(navigator, 'platform', {{get: () => '{random.choice(['Win32', 'Linux x86_64', 'MacIntel'])}'}});

#             Intl.DateTimeFormat.prototype.resolvedOptions = function () {{
#                 return {{ timeZone: '{random.choice(['Asia/Kolkata', 'America/New_York', 'Europe/Berlin'])}' }};
#             }};

#             const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#             HTMLCanvasElement.prototype.toDataURL = function() {{
#                 return "data:image/png;base64,fakecanvasdata" + Math.random();
#             }};

#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(param) {{
#                 if (param === 37445) return 'Intel Inc.';
#                 if (param === 37446) return 'Intel Iris OpenGL Engine';
#                 return getParameter.call(this, param);
#             }};

#             Object.defineProperty(navigator, 'maxTouchPoints', {{get: () => {random.choice([1, 2, 5])}}});
#         """)

#         simulate_user_behavior(driver, total_time=random.randint(*VISIT_DURATION))

#         try:
#             elements = driver.find_elements(By.XPATH, "//*")
#             if elements:
#                 random.choice(elements).click()
#         except Exception as click_err:
#             print(f"[!] Visit #{visit_id}: Click failed but continuing - {click_err}")

#         print(f"[✓] Visit #{visit_id} completed")
#     except Exception as e:
#         print(f"[x] Visit #{visit_id} failed: {e}")
#     finally:
#         try:
#             if driver in ACTIVE_DRIVERS:
#                 ACTIVE_DRIVERS.remove(driver)
#             driver.quit()
#         except Exception as e:
#             print(f"[!] Visit #{visit_id}: Driver quit failed - {e}")
#             os.system("taskkill /F /IM chrome.exe")
#             os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

#     for i in range(1, TOTAL_VISITS + 1):
#         visit_website(i)
#         time.sleep(random.uniform(5, 10))

# if __name__ == "__main__":
#     main()






# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from fake_useragent import UserAgent
# import time
# import random
# from tempfile import mkdtemp
# import os
# import signal
# import sys

# # === CONFIGURATION ===
# TARGET_URL = "https://marcadeo.com/"
# VISIT_DURATION = (10, 30)
# SCROLL_PAUSE = 2
# HEADLESS = False
# CONCURRENT_BOTS = 1
# TOTAL_VISITS = 4

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

# ACTIVE_DRIVERS = []

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
#     ua = UserAgent()
#     browsers = ['chrome', 'firefox', 'safari', 'edge']
#     try:
#         return getattr(ua, random.choice(browsers))
#     except:
#         return ua.random

# def create_driver():
#     ua_string = get_random_user_agent()
#     vp = random.choice(VIEWPORTS)
#     locale = random.choice(LOCALES)
#     tmp_profile = mkdtemp()
#     profile_folder = os.path.join("browser_profiles", f"profile_{random.randint(1, 999999)}")
#     os.makedirs("browser_profiles", exist_ok=True)

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--remote-debugging-port=0")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"user-agent={ua_string}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     # ❌ Removed mobileEmulation block here

#     service = Service(CHROMEDRIVER_PATH, log_path="chromedriver.log")

#     try:
#         driver = uc.Chrome(
#             service=service,
#             options=options,
#             user_data_dir=tmp_profile,
#             use_subprocess=True,
#             headless=HEADLESS,
#         )
#         driver.set_window_size(vp[0], vp[1])
#         ACTIVE_DRIVERS.append(driver)
#         return driver, locale
#     except Exception as e:
#         print(f"Failed to create driver: {e}")
#         return None, None


# def simulate_user_behavior(driver, total_time=70):
#     start = time.time()
#     actions = ActionChains(driver)
#     try:
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")
#     except Exception as e:
#         print(f"Failed to get window dimensions: {e}")
#         return

#     while time.time() - start < total_time:
#         for _ in range(random.randint(2, 4)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             try:
#                 actions.move_by_offset(x, y).perform()
#                 actions.reset_actions()
#             except:
#                 pass
#             time.sleep(random.uniform(0.3, 1.0))

#         if random.choice([True, False]):
#             scroll_y = random.randint(300, 1000)
#             driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#             time.sleep(random.uniform(1, 2))

#         if random.choice([True, False]):
#             driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#             time.sleep(random.uniform(1, 2))
#         time.sleep(random.uniform(2, 5))

# def visit_website(visit_id):
#     print(f"[*] Starting visit #{visit_id}")
#     driver, locale = create_driver()
#     if not driver:
#         print(f"[x] Visit #{visit_id} failed: Driver creation failed")
#         return

#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 6))

#         spoof_script = f"""
#             Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
#             Object.defineProperty(navigator, 'plugins', {{get: () => [1, 2, 3, 4, 5]}});
#             Object.defineProperty(navigator, 'languages', {{get: () => ['{locale}', 'en']}});
#             Object.defineProperty(navigator, 'deviceMemory', {{get: () => {random.choice([4, 8, 12, 16])}}});
#             Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {random.choice([2, 4, 6, 8])}}});
#             Object.defineProperty(navigator, 'platform', {{get: () => '{random.choice(['Win32', 'Linux x86_64', 'MacIntel'])}'}});

#             Object.defineProperty(navigator, 'connection', {{
#                 get: () => {{
#                     return {{
#                         downlink: 10,
#                         effectiveType: '4g',
#                         rtt: 50,
#                         saveData: false
#                     }};
#                 }}
#             }});

#             Object.defineProperty(document, 'visibilityState', {{get: () => 'visible'}});

#             window.performance.timing = {{
#                 navigationStart: Date.now() - 1000,
#                 loadEventEnd: Date.now()
#             }};

#             Intl.DateTimeFormat.prototype.resolvedOptions = function () {{
#                 return {{ timeZone: '{random.choice(['Asia/Kolkata', 'America/New_York', 'Europe/Berlin'])}' }};
#             }};

#             const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#             HTMLCanvasElement.prototype.toDataURL = function() {{
#                 return "data:image/png;base64,fakecanvasdata" + Math.random();
#             }};

#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(param) {{
#                 if (param === 37445) return 'Intel Inc.';
#                 if (param === 37446) return 'Intel Iris OpenGL Engine';
#                 return getParameter.call(this, param);
#             }};

#             Object.defineProperty(navigator, 'maxTouchPoints', {{get: () => {random.choice([1, 2, 5])}}});

#             const link = document.createElement('link');
#             link.href = 'https://fonts.googleapis.com/css2?family=Roboto';
#             link.rel = 'stylesheet';
#             document.head.appendChild(link);

#             const script = document.createElement('script');
#             script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js';
#             document.head.appendChild(script);
#         """

#         driver.execute_script(spoof_script)

#         simulate_user_behavior(driver, total_time=random.randint(*VISIT_DURATION))

#         try:
#             elements = driver.find_elements(By.XPATH, "//*")
#             if elements:
#                 random.choice(elements).click()
#         except Exception as click_err:
#             print(f"[!] Visit #{visit_id}: Click failed but continuing - {click_err}")

#         print(f"[✓] Visit #{visit_id} completed")
#     except Exception as e:
#         print(f"[x] Visit #{visit_id} failed: {e}")
#     finally:
#         try:
#             if driver in ACTIVE_DRIVERS:
#                 ACTIVE_DRIVERS.remove(driver)
#             driver.quit()
#         except Exception as e:
#             print(f"[!] Visit #{visit_id}: Driver quit failed - {e}")
#             os.system("taskkill /F /IM chrome.exe")
#             os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

#     for i in range(1, TOTAL_VISITS + 1):
#         visit_website(i)
#         time.sleep(random.uniform(5, 10))

# if __name__ == "__main__":
#     main()



# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from fake_useragent import UserAgent
# import time
# import random
# import os
# import signal
# import sys
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from tempfile import mkdtemp
# import shutil

# # === CONFIGURATION ===
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# VISIT_DURATION = (10, 30)
# SCROLL_PAUSE = 2
# HEADLESS = False
# CONCURRENT_BOTS = 1  # Number of concurrent browser sessions
# TOTAL_VISITS = 100    # Total number of visits 

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

# ACTIVE_DRIVERS = []

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
#     ua = UserAgent()
#     browsers = ['chrome', 'firefox', 'safari', 'edge']
#     try:
#         return getattr(ua, random.choice(browsers))
#     except:
#         return ua.random

# def create_driver(session_id):
#     ua_string = get_random_user_agent()
#     vp = random.choice(VIEWPORTS)
#     locale = random.choice(LOCALES)
#     tmp_profile = mkdtemp()
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}_{random.randint(1, 999999)}")
#     os.makedirs("browser_profiles", exist_ok=True)

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--remote-debugging-port=0")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"user-agent={ua_string}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     service = Service(CHROMEDRIVER_PATH, log_path="chromedriver.log")
#     try:
#         driver = uc.Chrome(
#             service=service,
#             options=options,
#             user_data_dir=tmp_profile,
#             use_subprocess=True,
#             headless=HEADLESS,
#         )
#         driver.set_window_size(vp[0], vp[1])
#         ACTIVE_DRIVERS.append(driver)
#         print(f"Session {session_id} created with user-agent: {ua_string}, viewport: {vp}, locale: {locale}")
#         return driver, tmp_profile, locale
#     except Exception as e:
#         print(f"Failed to create driver for Session {session_id}: {e}")
#         return None, tmp_profile, None

# def simulate_user_behavior(driver, total_time=70):
#     start = time.time()
#     actions = ActionChains(driver)
#     try:
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")
#     except Exception as e:
#         print(f"Failed to get window dimensions: {e}")
#         return

#     while time.time() - start < total_time:
#         for _ in range(random.randint(2, 4)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             try:
#                 actions.move_by_offset(x, y).perform()
#                 actions.reset_actions()
#             except:
#                 pass
#             time.sleep(random.uniform(0.3, 1.0))

#         if random.choice([True, False]):
#             scroll_y = random.randint(300, 1000)
#             driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#             time.sleep(random.uniform(1, 2))

#         if random.choice([True, False]):
#             driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#             time.sleep(random.uniform(1, 2))
#         time.sleep(random.uniform(2, 5))

# def visit_website(session_id, visit_id):
#     print(f"[*] Session {session_id} - Starting visit #{visit_id}")
#     driver, tmp_profile, locale = create_driver(session_id)
#     if not driver:
#         print(f"[x] Session {session_id} - Visit #{visit_id} failed: Driver creation failed")
#         if os.path.exists(tmp_profile):
#             shutil.rmtree(tmp_profile, ignore_errors=True)
#         return

#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 6))

#         spoof_script = f"""
#             Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
#             Object.defineProperty(navigator, 'plugins', {{get: () => [1, 2, 3, 4, 5]}});
#             Object.defineProperty(navigator, 'languages', {{get: () => ['{locale}', 'en']}});
#             Object.defineProperty(navigator, 'deviceMemory', {{get: () => {random.choice([4, 8, 12, 16])}}});
#             Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {random.choice([2, 4, 6, 8])}}});
#             Object.defineProperty(navigator, 'platform', {{get: () => '{random.choice(['Win32', 'Linux x86_64', 'MacIntel'])}'}});

#             Object.defineProperty(navigator, 'connection', {{
#                 get: () => {{
#                     return {{
#                         downlink: 10,
#                         effectiveType: '4g',
#                         rtt: 50,
#                         saveData: false
#                     }};
#                 }}
#             }});

#             Object.defineProperty(document, 'visibilityState', {{get: () => 'visible'}});

#             window.performance.timing = {{
#                 navigationStart: Date.now() - 1000,
#                 loadEventEnd: Date.now()
#             }};

#             Intl.DateTimeFormat.prototype.resolvedOptions = function () {{
#                 return {{ timeZone: '{random.choice(['Asia/Kolkata', 'America/New_York', 'Europe/Berlin'])}' }};
#             }};

#             const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#             HTMLCanvasElement.prototype.toDataURL = function() {{
#                 return "data:image/png;base64,fakecanvasdata" + Math.random();
#             }};

#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(param) {{
#                 if (param === 37445) return 'Intel Inc.';
#                 if (param === 37446) return 'Intel Iris OpenGL Engine';
#                 return getParameter.call(this, param);
#             }};

#             Object.defineProperty(navigator, 'maxTouchPoints', {{get: () => {random.choice([1, 2, 5])}}});

#             const link = document.createElement('link');
#             link.href = 'https://fonts.googleapis.com/css2?family=Roboto';
#             link.rel = 'stylesheet';
#             document.head.appendChild(link);

#             const script = document.createElement('script');
#             script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js';
#             document.head.appendChild(script);
#         """

#         driver.execute_script(spoof_script)

#         simulate_user_behavior(driver, total_time=random.randint(*VISIT_DURATION))

#         try:
#             elements = driver.find_elements(By.XPATH, "//*")
#             if elements:
#                 random.choice(elements).click()
#         except Exception as click_err:
#             print(f"[!] Session {session_id} - Visit #{visit_id}: Click failed but continuing - {click_err}")

#         print(f"[✓] Session {session_id} - Visit #{visit_id} completed")
#     except Exception as e:
#         print(f"[x] Session {session_id} - Visit #{visit_id} failed: {e}")
#     finally:
#         try:
#             if driver in ACTIVE_DRIVERS:
#                 ACTIVE_DRIVERS.remove(driver)
#             driver.quit()
#         except Exception as e:
#             print(f"[!] Session {session_id} - Visit #{visit_id}: Driver quit failed - {e}")
#             os.system("taskkill /F /IM chrome.exe")
#             os.system("taskkill /F /IM chromedriver.exe")
#         if os.path.exists(tmp_profile):
#             shutil.rmtree(tmp_profile, ignore_errors=True)

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

#     with ThreadPoolExecutor(max_workers=CONCURRENT_BOTS) as executor:
#         futures = []
#         for visit_id in range(1, TOTAL_VISITS + 1):
#             session_id = (visit_id - 1) % CONCURRENT_BOTS  # Distribute visits across 2 sessions
#             futures.append(executor.submit(visit_website, session_id, visit_id))

#         for future in as_completed(futures):
#             try:
#                 future.result()
#             except Exception as e:
#                 print(f"Error in future execution: {e}")

#     print(f"Total visits completed: {TOTAL_VISITS}")

# if __name__ == "__main__":
#     main()




# ***************************************************************************************
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from fake_useragent import UserAgent
# import time
# import random
# from tempfile import mkdtemp
# import os
# import signal
# import sys

# # === CONFIGURATION ===
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# # TARGET_URL = "https://marcadeo.com/"
# VISIT_DURATION = (20, 40)  # Updated for scroll + behavior 
# SCROLL_PAUSE = 2
# HEADLESS = False
# CONCURRENT_BOTS = 1
# TOTAL_VISITS = 5

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

# ACTIVE_DRIVERS = []

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
#     ua = UserAgent()
#     browsers = ['chrome', 'firefox', 'safari', 'edge','opera', 'ie', 'google', 'msie', 'netscape', 'mozilla']
#     try:
#         return getattr(ua, random.choice(browsers))
#     except:
#         return ua.random

# def create_driver():
#     ua_string = get_random_user_agent()
#     vp = random.choice(VIEWPORTS)
#     locale = random.choice(LOCALES)
#     tmp_profile = mkdtemp()
#     profile_folder = os.path.join("browser_profiles", f"profile_{random.randint(1, 999999)}")
#     os.makedirs("browser_profiles", exist_ok=True)

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--remote-debugging-port=0")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"user-agent={ua_string}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     service = Service(CHROMEDRIVER_PATH, log_path="chromedriver.log")

#     try:
#         driver = uc.Chrome(
#             service=service,
#             options=options,
#             user_data_dir=tmp_profile,
#             use_subprocess=True,
#             headless=HEADLESS,
#         )
#         driver.set_window_size(vp[0], vp[1])
#         ACTIVE_DRIVERS.append(driver)
#         return driver, locale
#     except Exception as e:
#         print(f"Failed to create driver: {e}")
#         return None, None
    
# def spoof_js_script():
#     return """
# // === Anti-bot spoofing script ===
# Object.defineProperty(navigator, 'webdriver', {get: () => false});
# window.chrome = { runtime: {} };
# Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
# Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
# Object.defineProperty(screen, 'width', { get: () => 1920 });
# Object.defineProperty(screen, 'height', { get: () => 1080 });
# Intl.DateTimeFormat = function() {
#   return { resolvedOptions: () => ({ timeZone: 'Asia/Kolkata' }) };
# };
# """

# def simulate_user_behavior(driver, total_time=50):
#     start = time.time()
#     actions = ActionChains(driver)
#     try:
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")
#     except Exception as e:
#         print(f"Failed to get window dimensions: {e}")
#         return

#     while time.time() - start < total_time:
#         for _ in range(random.randint(2, 4)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             try:
#                 actions.move_by_offset(x, y).perform()
#                 actions.reset_actions()
#             except:
#                 pass
#             time.sleep(random.uniform(0.3, 1.0))

#         if random.choice([True, False]):
#             scroll_y = random.randint(300, 1000)
#             driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#             time.sleep(random.uniform(1, 2))

#         if random.choice([True, False]):
#             driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#             time.sleep(random.uniform(1, 2))
#         time.sleep(random.uniform(2, 5))

# def visit_website(visit_id):
#     print(f"[*] Starting visit #{visit_id}")
#     driver, locale = create_driver()
#     if not driver:
#         print(f"[x] Visit #{visit_id} failed: Driver creation failed")
#         return

#     start_time = time.time()
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 6))  # Page load wait

#         spoof_script = f"""/* spoofing script here (unchanged for brevity) */"""
#         driver.execute_script(spoof_js_script())

#         # Step 1: scroll & user behavior
#         simulate_user_behavior(driver, total_time=random.randint(*VISIT_DURATION))

#         # Step 2: random click
#         try:
#             elements = driver.find_elements(By.XPATH, "//*")
#             if elements:
#                 random.choice(elements).click()
#                 print(f"[i] Visit #{visit_id}: Random element clicked.")
#                 time.sleep(random.uniform(2, 5))
#         except Exception as click_err:
#             print(f"[!] Visit #{visit_id}: Click failed - {click_err}")

#         # Step 3: scroll to bottom
#         try:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             print("[i] Visit #{visit_id}: Scrolled to bottom")
#             time.sleep(random.uniform(2, 4))
#         except:
#             pass

#         # Step 4: wait until 60–80 sec total engagement
#         elapsed = time.time() - start_time
#         required_total = random.randint(60, 80)
#         remaining = required_total - elapsed
#         if remaining > 0:
#             print(f"[i] Padding wait time: {round(remaining, 2)} sec")
#             time.sleep(remaining)

#         print(f"[✓] Visit #{visit_id} completed in {round(time.time() - start_time)} seconds")
#     except Exception as e:
#         print(f"[x] Visit #{visit_id} failed: {e}")
#     finally:
#         try:
#             if driver in ACTIVE_DRIVERS:
#                 ACTIVE_DRIVERS.remove(driver)
#             driver.quit()
#         except Exception as e:
#             print(f"[!] Visit #{visit_id}: Driver quit failed - {e}")
#             os.system("taskkill /F /IM chrome.exe")
#             os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

#     for i in range(1, TOTAL_VISITS + 1):
#         visit_website(i)
#         time.sleep(random.uniform(5, 10))

# if __name__ == "__main__":
#     main()



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
#     "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 5
# CONCURRENCY = 1
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

# def simulate_interaction(driver, total_time=60):
#     start_time = time.time()
#     total_time_spent = 0
#     action = ActionChains(driver)

#     try:
#         # Wait for page to load
#         time.sleep(random.uniform(3, 7))
#         total_time_spent += random.uniform(3, 7)

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

# # def simulate_single_visit(session_id, url):
# #     print(f"[*] Starting session #{session_id} → {url}")
# #     driver, locale = create_driver(session_id)
# #     if not driver:
# #         print(f"[x] Session #{session_id} failed: Driver creation failed")
# #         return

# #     timezone = random.choice(TIMEZONES)
# #     start_time = time.time()
# #     try:
# #         driver.get(url)
# #         time.sleep(random.uniform(5, 10))  # Wait for potential challenges

# #         # Check for anti-bot page (e.g., Cloudflare)
# #         if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
# #             print(f"[!] Session #{session_id}: Cloudflare challenge detected, waiting...")
# #             time.sleep(random.uniform(10, 15))

# #         # Apply spoofing
# #         driver.execute_script(spoof_js_script(timezone))

# #         # Simulate user interaction
# #         visit_time = random.randint(60, 80)
# #         simulate_interaction(driver, total_time=visit_time)

# #         print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
# #     except Exception as e:
# #         print(f"[x] Session #{session_id} failed: {e}")
# #     finally:
# #         try:
# #             if driver in ACTIVE_DRIVERS:
# #                 ACTIVE_DRIVERS.remove(driver)
# #             driver.quit()
# #         except Exception as e:
# #             print(f"[!] Session #{session_id}: Driver quit failed - {e}")
# #             os.system("taskkill /F /IM chrome.exe")
# #             os.system("taskkill /F /IM chromedriver.exe")

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     driver, locale = create_driver(session_id)
#     if not driver:
#         print(f"[x] Session #{session_id} failed: Driver creation failed")
#         return

#     timezone = random.choice(TIMEZONES)
#     start_time = time.time()
#     try:
#         driver.get(url)
#         time.sleep(random.uniform(5, 10))  # Wait for initial loads

#         # Check for anti-bot challenge
#         if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#             print(f"[!] Session #{session_id}: Cloudflare challenge detected.")
#             time.sleep(random.uniform(10, 15))

#         # Wait for analytics scripts to load
#         WebDriverWait(driver, 20).until(
#             lambda d: "gtag" in d.page_source or "analytics.js" in d.page_source or
#                       d.execute_script("return typeof gtag === 'function' || typeof ga === 'function'")
#         )

#         # Force GA page view
#         try:
#             driver.execute_script("""
#                 if (typeof gtag === 'function') {
#                     gtag('event', 'page_view');
#                 } else if (typeof ga === 'function') {
#                     ga('send', 'pageview');
#                 }
#             """)
#         except Exception as e:
#             print(f"[!] GA event trigger error in session #{session_id}: {e}")

#         # Simulate scrolling to bottom to trigger analytics
#         try:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(random.uniform(1.5, 3))
#             driver.execute_script("window.scrollTo(0, 0);")
#         except:
#             pass

#         # Log GA beacon check
#         try:
#             ga_beacon = driver.execute_script("""
#                 return performance.getEntriesByType('resource')
#                     .some(r => r.name.includes('collect') || r.name.includes('google-analytics'));
#             """)
#             print(f"[📊] GA beacon sent: {ga_beacon}")
#         except Exception as e:
#             print(f"[!] GA beacon check failed: {e}")

#         # Inject spoof script
#         driver.execute_script(spoof_js_script(timezone))

#         # Simulate interaction
#         visit_time = random.randint(60, 80)
#         simulate_interaction(driver, total_time=visit_time)

#         # Ensure all scripts and beacons fire
#         time.sleep(random.randint(8, 12))

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
#     # "https://marcadeo.com/"
#     "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 5
# CONCURRENCY = 1
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
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     service = Service(CHROMEDRIVER_PATH, log_path="chromedriver.log")

#     try:
#         driver = uc.Chrome(
#             service=service,
#             options=options,
#             user_data_dir=profile_folder,
#             use_subprocess=True,
#             # headless=HEADLESS,
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

# def simulate_interaction(driver, total_time=60):
#     start_time = time.time()
#     total_time_spent = 0
#     action = ActionChains(driver)

#     try:
#         # Wait for page to load
#         time.sleep(random.uniform(3, 7))
#         total_time_spent += random.uniform(3, 7)

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

# # def simulate_single_visit(session_id, url):
# #     print(f"[*] Starting session #{session_id} → {url}")
# #     driver, locale = create_driver(session_id)
# #     if not driver:
# #         print(f"[x] Session #{session_id} failed: Driver creation failed")
# #         return

# #     timezone = random.choice(TIMEZONES)
# #     start_time = time.time()
# #     try:
# #         driver.get(url)
# #         time.sleep(random.uniform(5, 10))  # Wait for potential challenges

# #         # Check for anti-bot page (e.g., Cloudflare)
# #         if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
# #             print(f"[!] Session #{session_id}: Cloudflare challenge detected, waiting...")
# #             time.sleep(random.uniform(10, 15))

# #         # Apply spoofing
# #         driver.execute_script(spoof_js_script(timezone))

# #         # Simulate user interaction
# #         visit_time = random.randint(60, 80)
# #         simulate_interaction(driver, total_time=visit_time)

# #         print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
# #     except Exception as e:
# #         print(f"[x] Session #{session_id} failed: {e}")
# #     finally:
# #         try:
# #             if driver in ACTIVE_DRIVERS:
# #                 ACTIVE_DRIVERS.remove(driver)
# #             driver.quit()
# #         except Exception as e:
# #             print(f"[!] Session #{session_id}: Driver quit failed - {e}")
# #             os.system("taskkill /F /IM chrome.exe")
# #             os.system("taskkill /F /IM chromedriver.exe")

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     driver, locale = create_driver(session_id)
#     if not driver:
#         print(f"[x] Session #{session_id} failed: Driver creation failed")
#         return

#     timezone = random.choice(TIMEZONES)
#     start_time = time.time()
#     try:
#         driver.get(url)
#         time.sleep(random.uniform(5, 10))  # Wait for initial loads

#         # Check for anti-bot challenge
#         if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#             print(f"[!] Session #{session_id}: Cloudflare challenge detected.")
#             time.sleep(random.uniform(10, 15))

#         # Wait for analytics scripts to load
#         WebDriverWait(driver, 20).until(
#             lambda d: "gtag" in d.page_source or "analytics.js" in d.page_source or
#                       d.execute_script("return typeof gtag === 'function' || typeof ga === 'function'")
#         )

#         # Force GA page view
#         try:
#             driver.execute_script("""
#                 if (typeof gtag === 'function') {
#                     gtag('event', 'page_view');
#                 } else if (typeof ga === 'function') {
#                     ga('send', 'pageview');
#                 }
#             """)
#         except Exception as e:
#             print(f"[!] GA event trigger error in session #{session_id}: {e}")

#         # Simulate scrolling to bottom to trigger analytics
#         try:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(random.uniform(1.5, 3))
#             driver.execute_script("window.scrollTo(0, 0);")
#         except:
#             pass

#         # Log GA beacon check
#         try:
#             ga_beacon = driver.execute_script("""
#                 return performance.getEntriesByType('resource')
#                     .some(r => r.name.includes('collect') || r.name.includes('google-analytics'));
#             """)
#             print(f"[📊] GA beacon sent: {ga_beacon}")
#         except Exception as e:
#             print(f"[!] GA beacon check failed: {e}")

#         # Inject spoof script
#         driver.execute_script(spoof_js_script(timezone))

#         # Simulate interaction
#         visit_time = random.randint(60, 80)
#         simulate_interaction(driver, total_time=visit_time)

#         # Ensure all scripts and beacons fire
#         time.sleep(random.randint(8, 12))

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
#     # "https://marcadeo.com/"
#     "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 10
# CONCURRENCY = 1
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
#     options.add_argument("--enable-gpu")
#     options.add_argument("--blink-settings=imagesEnabled=true")
#     options.add_argument("--enable-webgl")
#     options.add_argument("--enable-javascript")
#     options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
#     options.add_argument("--ignore-certificate-errors")
#     options.add_argument("--autoplay-policy=no-user-gesture-required")
#     if HEADLESS:
#         options.add_argument("--headless=chrome")

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

#         driver.execute_script("window.dispatchEvent(new Event('focus'));")
#         driver.execute_script("document.dispatchEvent(new Event('visibilitychange'));")

#         # Trigger GA events
#         # driver.execute_script("""
#         #     if (typeof gtag === 'function') {
#         #         gtag('event', 'page_view');
#         #         gtag('event', 'headless_test', { 'event_category': 'Test', 'event_label': 'Headless' });
#         #     } else if (typeof ga === 'function') {
#         #         ga('send', 'pageview');
#         #         ga('send', 'event', 'Test', 'Headless', 'headless_test');
#         #     }
#         #     if (typeof window.dataLayer !== 'undefined') {
#         #         window.dataLayer.push({'event': 'headless_test'});
#         #     }
#         # """)
#         driver.execute_script("""
#         (function() {
#             console.log('[GA Test] Injecting GA events...');
            
#             if (typeof gtag === 'function') {
#                 console.log('[GA Test] Using gtag');
#                 gtag('config', 'YOUR_TRACKING_ID', { 'send_page_view': true });
#                 gtag('event', 'headless_test', {
#                     'event_category': 'Test',
#                     'event_label': 'Headless Browser Visit',
#                     'non_interaction': false
#                 });
#             } else if (typeof ga === 'function') {
#                 console.log('[GA Test] Using ga');
#                 ga('create', 'YOUR_TRACKING_ID', 'auto');
#                 ga('send', 'pageview');
#                 ga('send', 'event', 'Test', 'Headless Visit', 'headless_test');
#             }

#             if (typeof window.dataLayer !== 'undefined') {
#                 console.log('[GA Test] Pushing to dataLayer');
#                 window.dataLayer.push({
#                     'event': 'headless_test',
#                     'eventCategory': 'Test',
#                     'eventAction': 'Headless',
#                     'eventLabel': 'HeadlessBotTrigger'
#                 });
#             }

#             // Fallback: Use sendBeacon for guaranteed delivery
#             try {
#                 var cid = Math.random().toString(36).substring(2);
#                 var payload = new URLSearchParams({
#                     v: '1',
#                     tid: 'YOUR_TRACKING_ID',
#                     cid: cid,
#                     t: 'event',
#                     ec: 'Test',
#                     ea: 'HeadlessBotVisit',
#                     el: 'HeadlessJS',
#                     dp: '/headless-visit'
#                 });
#                 navigator.sendBeacon('https://www.google-analytics.com/collect', payload);
#                 console.log('[GA Test] sendBeacon triggered');
#             } catch (e) {
#                 console.log('[GA Test] sendBeacon failed', e);
#             }
#         })();
#         """)
#         time.sleep(random.uniform(2, 4)) 
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
#     "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 10
# CONCURRENCY = 1
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
#     options.add_argument("--enable-gpu")
#     options.add_argument("--blink-settings=imagesEnabled=true")
#     options.add_argument("--enable-webgl")
#     options.add_argument("--enable-javascript")
#     options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
#     options.add_argument("--ignore-certificate-errors")
#     if HEADLESS:
#         options.add_argument("--headless=chrome")

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