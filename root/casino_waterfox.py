# import time
# import random
# import sys
# import os
# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service
# from webdriver_manager.firefox import GeckoDriverManager

# # ================= RESOURCE PATH FOR EXE BUNDLE =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")

# # ================= MAIN FUNCTION =================
# def open_with_proxy():
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
    
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
    
#     print(f"🌍 Country : {country_code}")
#     print(f"🔗 Proxy   : {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'}
#     }

#     options = Options()
#     options.binary_location = WATERFOX_PATH
    
#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.set_preference("webdriver.assume_untrusted", False)
    
#     options.add_argument("--start-maximized")

#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver = None
#     try:
#         # GeckoDriver (webdriver_manager)
#         service = Service(GeckoDriverManager().install())
        
#         driver = webdriver.Firefox(          # ← Yeh sahi hai (Chrome nahi)
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
        
#         print("🚀 Waterfox opened with proxy...")

#         driver.get("https://api.ipify.org?format=json")
#         time.sleep(random.uniform(4, 7))
#         try:
#             ip_text = driver.find_element(By.TAG_NAME, "body").text.strip()
#             print(f"🌐 Real Exit IP : {ip_text}")
#         except:
#             print("🌐 Real Exit IP : (fetched)")

#         print(f"🔗 Opening rotator URL...")
#         driver.get(TARGET_URL)
        
#         time.sleep(random.uniform(5, 10))

#         print(f"📍 Landed on    : {driver.current_url[:90]}...")

#         print("📜 Human-like interaction...")
#         for _ in range(random.randint(2, 5)):
#             scroll_amount = random.randint(400, 900)
#             driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
#             time.sleep(random.uniform(1.8, 4.2))
            
#             try:
#                 actions = ActionChains(driver)
#                 actions.move_by_offset(random.randint(-100, 100), random.randint(-60, 60)).perform()
#                 time.sleep(random.uniform(0.8, 2.3))
#             except:
#                 pass

#         final_wait = random.uniform(8, 18)
#         print(f"⏳ Staying {final_wait:.1f} seconds on page...")
#         time.sleep(final_wait)

#         print(f"✅ Visit done for {country_code}\n")

#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(3, 7))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print("🔒 Waterfox closed\n")

# if __name__ == "__main__":
#     print("=== Geonode + Waterfox + Human-like Traffic ===\n")
#     open_with_proxy()


# import time
# import random
# import sys
# import os

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# # Force import all webdriver modules that seleniumwire tries to load
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service
# from webdriver_manager.firefox import GeckoDriverManager

# # ================= RESOURCE PATH FOR EXE =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")

# # ================= MAIN FUNCTION =================
# def open_with_proxy():
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
    
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
    
#     print(f"🌍 Country : {country_code}")
#     print(f"🔗 Proxy   : {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'}
#     }

#     options = Options()
#     options.binary_location = WATERFOX_PATH
    
#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.set_preference("webdriver.assume_untrusted", False)
    
#     options.add_argument("--start-maximized")

#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver = None
#     try:
#         service = Service(GeckoDriverManager().install())
        
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
        
#         print("🚀 Waterfox opened with proxy...")

#         driver.get("https://api.ipify.org?format=json")
#         time.sleep(random.uniform(4, 7))
#         try:
#             ip_text = driver.find_element(By.TAG_NAME, "body").text.strip()
#             print(f"🌐 Real Exit IP : {ip_text}")
#         except:
#             print("🌐 Real Exit IP : (fetched)")

#         print(f"🔗 Opening rotator URL...")
#         driver.get(TARGET_URL)
        
#         time.sleep(random.uniform(5, 10))
#         print(f"📍 Landed on    : {driver.current_url[:90]}...")

#         print("📜 Human-like interaction...")
#         for _ in range(random.randint(2, 5)):
#             scroll_amount = random.randint(400, 900)
#             driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
#             time.sleep(random.uniform(1.8, 4.2))
            
#             try:
#                 actions = ActionChains(driver)
#                 actions.move_by_offset(random.randint(-100, 100), random.randint(-60, 60)).perform()
#                 time.sleep(random.uniform(0.8, 2.3))
#             except:
#                 pass

#         final_wait = random.uniform(8, 18)
#         print(f"⏳ Staying {final_wait:.1f} seconds on page...")
#         time.sleep(final_wait)

#         print(f"✅ Visit done for {country_code}\n")

#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(3, 7))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print("🔒 Waterfox closed\n")

# if __name__ == "__main__":
#     print("=== Geonode + Waterfox + Human-like Traffic ===\n")
#     open_with_proxy()




# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime

# # Suppress RequestsDependencyWarning
# import warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service
# from webdriver_manager.firefox import GeckoDriverManager

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")

# LOG_FILE = "visit_log.json"

# # Load existing logs or create new
# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_log(visit_data):
#     logs = load_logs()
#     logs.append(visit_data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================= MAIN FUNCTION =================
# def open_with_proxy(visit_number=1):
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
    
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
    
#     print(f"\n=== Visit #{visit_number} ===")
#     print(f"🌍 Country : {country_code}")
#     print(f"🔗 Proxy   : {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'}
#     }

#     options = Options()
#     options.binary_location = WATERFOX_PATH
#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.set_preference("webdriver.assume_untrusted", False)
#     options.add_argument("--start-maximized")

#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver = None
#     try:
#         service = Service(GeckoDriverManager().install())
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
        
#         print("🚀 Waterfox opened with proxy...")

#         # Fast IP Check
#         driver.get("https://api.ipify.org?format=json")
#         time.sleep(random.uniform(3, 5))
#         ip_text = "Unknown"
#         try:
#             ip_text = driver.find_element(By.TAG_NAME, "body").text.strip()
#             print(f"🌐 Real Exit IP : {ip_text}")
#         except:
#             print("🌐 Real Exit IP : (fetched)")

#         # Direct Target URL (Fast Visit)
#         print(f"🔗 Opening Target URL...")
#         driver.get(TARGET_URL)
        
#         time.sleep(random.uniform(4, 7))   # thoda wait redirect ke liye

#         current_url = driver.current_url
#         print(f"📍 Landed on    : {current_url[:90]}...")

#         # ================= MAIN STAY ON LANDED PAGE =================
#         stay_time = random.uniform(30, 50)   # Minimum 30 seconds
#         print(f"⏳ Staying {stay_time:.1f} seconds on main page (Visit Count Page)...")

#         start_time = time.time()
#         while time.time() - start_time < stay_time:
#             # Random Human Behavior
#             if random.random() < 0.6:
#                 scroll_amount = random.randint(300, 800)
#                 driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
#                 time.sleep(random.uniform(1.2, 3.5))
            
#             if random.random() < 0.4:
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-120, 120), random.randint(-70, 70)).perform()
#                     time.sleep(random.uniform(0.6, 2.1))
#                 except:
#                     pass

#             time.sleep(0.5)  # small delay between actions

#         print(f"✅ Visit #{visit_number} completed for {country_code} | Stayed {stay_time:.1f}s\n")

#         # Save Log
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "ip": ip_text,
#             "landed_url": current_url[:150],
#             "stay_duration": round(stay_time, 1)
#         }
#         save_log(visit_data)

#     except Exception as e:
#         print(f"❌ Error in Visit #{visit_number}: {e}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 4))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print("🔒 Waterfox closed\n")


# if __name__ == "__main__":
#     print("=== Geonode + Waterfox + Fast Human-like Traffic ===\n")
#     visit_count = 1
    
#     while True:   # Infinite loop for long running
#         open_with_proxy(visit_count)
#         visit_count += 1
        
#         # Random delay between visits (15 to 45 seconds)
#         sleep_between = random.uniform(15, 45)
#         print(f"⏳ Waiting {sleep_between:.1f} seconds before next visit...\n")
#         time.sleep(sleep_between)



# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime
# import warnings
# import threading
# from concurrent.futures import ThreadPoolExecutor, as_completed

# # Suppress Warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")
# LOG_FILE = "visit_log.json"

# # ================= LOCAL GECKODRIVER PATH (Aapka Path) =================
# GECKODRIVER_PATH = r"D:\streakads\geckodriver-v0.36.0-win64\geckodriver.exe"

# # ================= USER SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 5      # 5 sessions ek saath (agar RAM zyada lage to 4 kar sakte ho)
# TARGET_VISITS = 10000

# # Thread-safe logging
# log_lock = threading.Lock()

# # ================= LOGGING =================
# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_log(visit_data):
#     with log_lock:
#         logs = load_logs()
#         logs.append(visit_data)
#         with open(LOG_FILE, 'w', encoding='utf-8') as f:
#             json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================= SINGLE VISIT FUNCTION =================
# def open_with_proxy(visit_number):
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
   
#     print(f"\n=== Visit #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy : {proxy_url[:75]}...")
   
#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
#         'request_storage': 'memory',
#         'connection_timeout': 45
#     }
   
#     options = Options()
#     options.binary_location = WATERFOX_PATH
#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.add_argument("--start-maximized")
   
#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")
   
#     driver = None
   
#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
       
#         print("🚀 Waterfox opened with proxy...")
       
#         print(f"🔗 Opening Target URL...")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(4, 8))
       
#         current_url = driver.current_url
#         print(f"📍 Landed on : {current_url[:90]}...")
       
#         # Human-like behavior
#         stay_time = random.uniform(32, 55)
#         print(f"⏳ Staying {stay_time:.1f} seconds on page...")
#         start_time = time.time()
#         while time.time() - start_time < stay_time:
#             if random.random() < 0.65:
#                 driver.execute_script(f"window.scrollBy(0, {random.randint(250, 750)});")
#                 time.sleep(random.uniform(1.0, 3.8))
           
#             if random.random() < 0.45:
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-150, 150), random.randint(-80, 80)).perform()
#                     time.sleep(random.uniform(0.5, 2.3))
#                 except:
#                     pass
#             time.sleep(0.6)
       
#         print(f"✅ Visit #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s\n")
       
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "ip": "Unknown",
#             "landed_url": current_url[:150],
#             "stay_duration": round(stay_time, 1)
#         }
#         save_log(visit_data)
       
#     except Exception as e:
#         print(f"❌ Error in Visit #{visit_number}: {str(e)[:150]}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 5))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Waterfox closed for Visit #{visit_number}\n")

# # ================= MAIN EXECUTION =================
# if __name__ == "__main__":
#     # Check if geckodriver exists
#     if not os.path.exists(GECKODRIVER_PATH):
#         print(f"❌ GeckoDriver not found at:\n{GECKODRIVER_PATH}")
#         print("Please check the path and make sure geckodriver.exe is inside the folder.")
#         sys.exit(1)
   
#     print("=== Geonode + Waterfox + Concurrent Sessions (Local GeckoDriver) ===\n")
#     print(f"Target Visits : {TARGET_VISITS} | Max Concurrent Sessions : {MAX_CONCURRENT_SESSIONS}\n")
   
#     completed_visits = 0
#     visit_number = 1
   
#     with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SESSIONS) as executor:
#         futures = []
       
#         # Initial sessions with delay between them
#         for i in range(MAX_CONCURRENT_SESSIONS):
#             if completed_visits >= TARGET_VISITS:
#                 break
#             future = executor.submit(open_with_proxy, visit_number)
#             futures.append(future)
#             visit_number += 1
#             if i < MAX_CONCURRENT_SESSIONS - 1:
#                 time.sleep(random.uniform(1.8, 3.8))   # Natural delay between opening sessions
       
#         # Continue launching new sessions as old ones complete
#         while completed_visits < TARGET_VISITS:
#             for future in as_completed(futures):
#                 try:
#                     future.result()
#                 except:
#                     pass
               
#                 completed_visits += 1
#                 print(f"📊 Total Completed: {completed_visits}/{TARGET_VISITS}")
               
#                 if completed_visits >= TARGET_VISITS:
#                     break
               
#                 # Small delay before starting next new session
#                 time.sleep(random.uniform(1.2, 3.2))
#                 future = executor.submit(open_with_proxy, visit_number)
#                 futures.append(future)
#                 visit_number += 1
           
#             futures = [f for f in futures if not f.done()]
   
#     print("\n🎉 All target visits completed successfully!")
#     print(f"Total Visits Done: {completed_visits}")
#     print("Script band ho raha hai...\n")


# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime
# import warnings
# import threading
# from concurrent.futures import ThreadPoolExecutor, as_completed

# # Suppress Warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     """ PyInstaller EXE ke liye sahi path deta hai """
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")
# LOG_FILE = "visit_log.json"

# # ================= LOCAL GECKODRIVER PATH (PyInstaller ke liye) =================
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# # ================= USER SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 4      # 4 ya 3 kar sakte ho agar RAM zyada lage
# TARGET_VISITS = 2000            # Aapne 10000 set kiya tha

# # Thread-safe logging
# log_lock = threading.Lock()

# # ================= LOGGING =================
# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_log(visit_data):
#     with log_lock:
#         logs = load_logs()
#         logs.append(visit_data)
#         with open(LOG_FILE, 'w', encoding='utf-8') as f:
#             json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================= SINGLE VISIT FUNCTION =================
# def open_with_proxy(visit_number):
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
   
#     print(f"\n=== Visit #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy : {proxy_url[:75]}...")
   
#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
#         'request_storage': 'memory',
#         'connection_timeout': 45
#     }
   
#     options = Options()
#     options.binary_location = WATERFOX_PATH
#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.add_argument("--start-maximized")
   
#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")
   
#     driver = None
   
#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
       
#         print("🚀 Waterfox opened with proxy...")
       
#         print(f"🔗 Opening Target URL...")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(4, 8))
       
#         current_url = driver.current_url
#         print(f"📍 Landed on : {current_url[:90]}...")
       
#         # Human-like behavior
#         stay_time = random.uniform(32, 55)
#         print(f"⏳ Staying {stay_time:.1f} seconds on page...")
#         start_time = time.time()
#         while time.time() - start_time < stay_time:
#             if random.random() < 0.65:
#                 driver.execute_script(f"window.scrollBy(0, {random.randint(250, 750)});")
#                 time.sleep(random.uniform(1.0, 3.8))
           
#             if random.random() < 0.45:
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-150, 150), random.randint(-80, 80)).perform()
#                     time.sleep(random.uniform(0.5, 2.3))
#                 except:
#                     pass
#             time.sleep(0.6)
       
#         print(f"✅ Visit #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s\n")
       
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "ip": "Unknown",
#             "landed_url": current_url[:150],
#             "stay_duration": round(stay_time, 1)
#         }
#         save_log(visit_data)
       
#     except Exception as e:
#         print(f"❌ Error in Visit #{visit_number}: {str(e)[:150]}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 5))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Waterfox closed for Visit #{visit_number}\n")

# # ================= MAIN EXECUTION =================
# if __name__ == "__main__":
#     # Check if geckodriver exists
#     if not os.path.exists(GECKODRIVER_PATH):
#         print(f"❌ GeckoDriver not found at:\n{GECKODRIVER_PATH}")
#         print("Make sure you have placed 'geckodriver-v0.36.0-win64' folder in the same directory as the script/EXE.")
#         print("Folder structure should be: geckodriver-v0.36.0-win64/geckodriver.exe")
#         sys.exit(1)
   
#     print("=== Geonode + Waterfox + Concurrent Sessions (EXE Ready) ===\n")
#     print(f"Target Visits : {TARGET_VISITS} | Max Concurrent Sessions : {MAX_CONCURRENT_SESSIONS}\n")
   
#     completed_visits = 0
#     visit_number = 1
   
#     with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SESSIONS) as executor:
#         futures = []
       
#         # Initial sessions with delay
#         for i in range(MAX_CONCURRENT_SESSIONS):
#             if completed_visits >= TARGET_VISITS:
#                 break
#             future = executor.submit(open_with_proxy, visit_number)
#             futures.append(future)
#             visit_number += 1
#             if i < MAX_CONCURRENT_SESSIONS - 1:
#                 time.sleep(random.uniform(1.8, 3.8))
       
#         # Keep launching new sessions as old ones finish
#         while completed_visits < TARGET_VISITS:
#             for future in as_completed(futures):
#                 try:
#                     future.result()
#                 except:
#                     pass
               
#                 completed_visits += 1
#                 print(f"📊 Total Completed: {completed_visits}/{TARGET_VISITS}")
               
#                 if completed_visits >= TARGET_VISITS:
#                     break
               
#                 time.sleep(random.uniform(1.2, 3.2))
#                 future = executor.submit(open_with_proxy, visit_number)
#                 futures.append(future)
#                 visit_number += 1
           
#             futures = [f for f in futures if not f.done()]
   
#     print("\n🎉 All target visits completed successfully!")
#     print(f"Total Visits Done: {completed_visits}")
#     print("Script band ho raha hai...\n")




# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime
# import warnings
# import threading
# from concurrent.futures import ThreadPoolExecutor, as_completed

# # Suppress Warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     """ PyInstaller EXE ke liye sahi path deta hai """
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")
# LOG_FILE = "visit_log.json"

# # ================= LOCAL GECKODRIVER PATH (PyInstaller ke liye) =================
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# # ================= USER SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 4      # 4 ya 3 kar sakte ho agar RAM zyada lage
# TARGET_VISITS = 2000

# # Thread-safe logging
# log_lock = threading.Lock()

# # ================= LOGGING =================
# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_log(visit_data):
#     with log_lock:
#         logs = load_logs()
#         logs.append(visit_data)
#         with open(LOG_FILE, 'w', encoding='utf-8') as f:
#             json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================= SINGLE VISIT FUNCTION =================
# def open_with_proxy(visit_number):
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
   
#     print(f"\n=== Visit #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy : {proxy_url[:75]}...")
   
#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
#         'request_storage': 'memory',
#         'connection_timeout': 45
#     }
   
#     options = Options()
#     options.binary_location = WATERFOX_PATH
#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.add_argument("--start-maximized")
   
#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")
   
#     driver = None
   
#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
       
#         print("🚀 Waterfox opened with proxy...")
       
#         print(f"🔗 Opening Target URL...")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(4, 8))
       
#         current_url = driver.current_url
#         print(f"📍 Landed on : {current_url[:90]}...")
       
#         # Human-like behavior
#         stay_time = random.uniform(32, 55)
#         print(f"⏳ Staying {stay_time:.1f} seconds on page...")
#         start_time = time.time()
#         while time.time() - start_time < stay_time:
#             if random.random() < 0.65:
#                 driver.execute_script(f"window.scrollBy(0, {random.randint(250, 750)});")
#                 time.sleep(random.uniform(1.0, 3.8))
           
#             if random.random() < 0.45:
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-150, 150), random.randint(-80, 80)).perform()
#                     time.sleep(random.uniform(0.5, 2.3))
#                 except:
#                     pass
#             time.sleep(0.6)
       
#         print(f"✅ Visit #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s\n")
       
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "ip": "Unknown",
#             "landed_url": current_url[:150],
#             "stay_duration": round(stay_time, 1)
#         }
#         save_log(visit_data)
       
#     except Exception as e:
#         print(f"❌ Error in Visit #{visit_number}: {str(e)[:150]}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 5))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Waterfox closed for Visit #{visit_number}\n")

# # ================= MAIN EXECUTION (Fixed Concurrency Logic) =================
# if __name__ == "__main__":
#     # Check if geckodriver exists
#     if not os.path.exists(GECKODRIVER_PATH):
#         print(f"❌ GeckoDriver not found at:\n{GECKODRIVER_PATH}")
#         print("Make sure you have placed 'geckodriver-v0.36.0-win64' folder in the same directory as the script/EXE.")
#         print("Folder structure should be: geckodriver-v0.36.0-win64/geckodriver.exe")
#         sys.exit(1)
   
#     print("=== Geonode + Waterfox + Concurrent Sessions (EXE Ready) ===\n")
#     print(f"Target Visits : {TARGET_VISITS} | Max Concurrent Sessions : {MAX_CONCURRENT_SESSIONS}\n")
   
#     completed_visits = 0
#     visit_number = 1
   
#     with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SESSIONS) as executor:
#         active_futures = []
       
#         # Initial batch launch with delay
#         for i in range(MAX_CONCURRENT_SESSIONS):
#             if completed_visits >= TARGET_VISITS:
#                 break
#             future = executor.submit(open_with_proxy, visit_number)
#             active_futures.append(future)
#             visit_number += 1
#             if i < MAX_CONCURRENT_SESSIONS - 1:
#                 time.sleep(random.uniform(1.5, 3.5))
       
#         # Main loop - Ensure MAX_CONCURRENT_SESSIONS always running
#         while completed_visits < TARGET_VISITS:
#             # Wait for at least one future to complete
#             for future in as_completed(active_futures):
#                 try:
#                     future.result()
#                 except:
#                     pass
                
#                 completed_visits += 1
#                 print(f"📊 Total Completed: {completed_visits}/{TARGET_VISITS}")
                
#                 if completed_visits >= TARGET_VISITS:
#                     break
                
#                 # Immediately start a new session to maintain concurrency
#                 if completed_visits < TARGET_VISITS:
#                     time.sleep(random.uniform(1.0, 2.8))   # Natural small delay
#                     new_future = executor.submit(open_with_proxy, visit_number)
#                     active_futures.append(new_future)
#                     visit_number += 1
            
#             # Clean up completed futures (important fix)
#             active_futures = [f for f in active_futures if not f.done()]
   
#     print("\n🎉 All target visits completed successfully!")
#     print(f"Total Visits Done: {completed_visits}")
#     print("Script band ho raha hai...\n")



# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime
# import warnings
# import threading
# from queue import Queue, Empty

# # Suppress Warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     """ PyInstaller EXE ke liye sahi path deta hai """
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# TARGET_URL = "https://partners.trackopia.com/click?aid=4&oid=311"
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["IN", "IT", "FR"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")
# LOG_FILE = "visit_log.json"
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# # ================= USER SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 4
# TARGET_VISITS = 2000

# # ================= GLOBAL VARIABLES =================
# stop_flag = False
# log_lock = threading.Lock()

# # ================= LOGGING =================
# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except Exception:
#             return []
#     return []

# def save_log(visit_data):
#     with log_lock:
#         logs = load_logs()
#         logs.append(visit_data)
#         try:
#             with open(LOG_FILE, 'w', encoding='utf-8') as f:
#                 json.dump(logs, f, indent=2, ensure_ascii=False)
#         except Exception as e:
#             print(f"⚠️ Log save failed: {e}")

# # ================= SINGLE VISIT FUNCTION =================
# def open_with_proxy(visit_number):
#     global stop_flag
#     if stop_flag:
#         return

#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
  
#     print(f"\n=== Visit #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy : {proxy_url[:75]}...")
  
#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
#         'request_storage': 'memory',
#         'connection_timeout': 45
#     }
  
#     options = Options()
#     options.binary_location = WATERFOX_PATH
#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.add_argument("--start-maximized")
  
#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")
  
#     driver = None
  
#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
      
#         print("🚀 Waterfox opened with proxy...")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(4, 8))
      
#         current_url = driver.current_url
#         print(f"📍 Landed on : {current_url[:90]}...")
      
#         # Human-like behavior
#         stay_time = random.uniform(32, 55)
#         print(f"⏳ Staying {stay_time:.1f} seconds on page...")
#         start_time = time.time()
        
#         while time.time() - start_time < stay_time and not stop_flag:
#             if random.random() < 0.65:
#                 try:
#                     driver.execute_script(f"window.scrollBy(0, {random.randint(250, 750)});")
#                 except:
#                     pass
#                 time.sleep(random.uniform(1.0, 3.8))
          
#             if random.random() < 0.45:
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-150, 150), random.randint(-80, 80)).perform()
#                 except:
#                     pass
#                 time.sleep(random.uniform(0.5, 2.3))
            
#             time.sleep(0.6)
      
#         print(f"✅ Visit #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s\n")
      
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "ip": "Unknown",
#             "landed_url": current_url[:150],
#             "stay_duration": round(stay_time, 1)
#         }
#         save_log(visit_data)
      
#     except Exception as e:
#         print(f"❌ Error in Visit #{visit_number}: {str(e)[:180]}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 5))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Waterfox closed for Visit #{visit_number}\n")

# # ================= WORKER FUNCTION =================
# def worker(visit_queue, completed_count, lock):
#     global stop_flag
#     while not stop_flag:
#         try:
#             visit_number = visit_queue.get_nowait()
#         except Empty:
#             break
        
#         open_with_proxy(visit_number)
        
#         with lock:
#             completed_count[0] += 1
#             print(f"📊 Total Completed: {completed_count[0]}/{TARGET_VISITS}")
        
#         time.sleep(random.uniform(0.8, 2.2))

# # ================= MAIN EXECUTION =================
# if __name__ == "__main__":
#     # Check geckodriver
#     if not os.path.exists(GECKODRIVER_PATH):
#         print(f"❌ GeckoDriver not found at:\n{GECKODRIVER_PATH}")
#         print("Please place 'geckodriver-v0.36.0-win64' folder correctly.")
#         sys.exit(1)
  
#     print("=== Geonode + Waterfox + Stable Concurrent Sessions ===\n")
#     print(f"Target Visits : {TARGET_VISITS} | Max Concurrent : {MAX_CONCURRENT_SESSIONS}\n")
    
#     # Reset stop_flag
#     stop_flag = False
    
#     # Create visit queue
#     visit_queue = Queue()
#     for i in range(1, TARGET_VISITS + 1):
#         visit_queue.put(i)
    
#     lock = threading.Lock()
#     completed_count = [0]
    
#     # Start threads
#     threads = []
#     for _ in range(MAX_CONCURRENT_SESSIONS):
#         t = threading.Thread(
#             target=worker,
#             args=(visit_queue, completed_count, lock),
#             daemon=True
#         )
#         t.start()
#         threads.append(t)
#         time.sleep(random.uniform(1.0, 2.5))   # Staggered start
    
#     # Monitor loop
#     try:
#         while completed_count[0] < TARGET_VISITS and not stop_flag:
#             time.sleep(3)
#             if visit_queue.empty() and all(not t.is_alive() for t in threads):
#                 break
#     except KeyboardInterrupt:
#         print("\n\n🛑 Stopping by user request...")
#         stop_flag = True
    
#     # Graceful shutdown
#     print("\nWaiting for remaining sessions to complete...")
#     for t in threads:
#         if t.is_alive():
#             t.join(timeout=20)
    
#     print("\n🎉 Script execution finished!")
#     print(f"Total Visits Completed: {completed_count[0]}/{TARGET_VISITS}")
#     print("Thank you for using the script.\n")






# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime
# import warnings
# import threading
# from queue import Queue, Empty

# # Suppress Warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     """ PyInstaller EXE ke liye sahi path deta hai """
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= GEONODE + WATERFOX CONFIG =================
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS      = "CHANGE_ME_SECRET"
# GEONODE_HOST      = "sg.proxy.geonode.io"
# GEONODE_PORT      = "11000"

# COUNTRIES = ["IT", "GR", "CH", "AT", "US", "CA"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0 Waterfox/132.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")
# LOG_FILE = "magzter_logs.json"
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# # ================= USER SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 3
# TARGET_VISITS = 2000

# # ================= GLOBAL VARIABLES =================
# stop_flag = False
# log_lock = threading.Lock()

# # ================= LOGGING =================
# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except Exception:
#             return []
#     return []

# def save_log(visit_data):
#     with log_lock:
#         logs = load_logs()
#         logs.append(visit_data)
#         try:
#             with open(LOG_FILE, 'w', encoding='utf-8') as f:
#                 json.dump(logs, f, indent=2, ensure_ascii=False)
#         except Exception as e:
#             print(f"⚠️ Log save failed: {e}")

# # ================= SINGLE VISIT FUNCTION (Fingerprinting Updated) =================
# def open_with_proxy(visit_number):
#     global stop_flag
#     if stop_flag:
#         return

#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
  
#     print(f"\n=== Run #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy : {proxy_url[:75]}...")
  
#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
#         'request_storage': 'memory',
#         'connection_timeout': 60
#     }
  
#     options = Options()
#     options.binary_location = WATERFOX_PATH
    
#     # ================= STRONG FINGERPRINTING =================
#     ua = random.choice(USER_AGENTS)
#     options.set_preference("general.useragent.override", ua)
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.set_preference("privacy.trackingprotection.enabled", True)
#     options.set_preference("media.eme.enabled", False)
#     options.set_preference("intl.accept_languages", "en-US,en")
#     options.set_preference("general.platform.override", "Win32")
    
#     # Extra anti-detection preferences
#     options.set_preference("webgl.disabled", False)
#     options.set_preference("canvas.capturestream.enabled", True)
#     options.set_preference("gfx.canvas.azure.backends", "direct2d1.1,skia")
    
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-blink-features=AutomationControlled")
    
#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver = None
  
#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
      
#         print("🚀 Waterfox opened with Geonode Proxy + Strong Fingerprinting...")
#         driver.get("https://app.adstracking.io/click?pid=3030&offer_id=20655")
#         time.sleep(random.uniform(4, 8))
      
#         current_url = driver.current_url
#         print(f"📍 Landed on : {current_url[:90]}...")
      
#         # Human-like behavior (same as before)
#         stay_time = random.uniform(32, 55)
#         print(f"⏳ Staying {stay_time:.1f} seconds on page...")
#         start_time = time.time()
        
#         while time.time() - start_time < stay_time and not stop_flag:
#             if random.random() < 0.65:
#                 try:
#                     driver.execute_script(f"window.scrollBy(0, {random.randint(250, 750)});")
#                 except:
#                     pass
#                 time.sleep(random.uniform(1.0, 3.8))
          
#             if random.random() < 0.45:
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-150, 150), random.randint(-80, 80)).perform()
#                 except:
#                     pass
#                 time.sleep(random.uniform(0.5, 2.3))
            
#             time.sleep(0.6)
      
#         print(f"✅ Run #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s\n")
      
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "status": "success",
#             "landed_url": current_url[:150],
#             "stay_duration": round(stay_time, 1)
#         }
#         save_log(visit_data)
      
#     except Exception as e:
#         print(f"❌ Error in Run #{visit_number}: {str(e)[:180]}")
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "status": "failed",
#             "error": str(e)[:200]
#         }
#         save_log(visit_data)
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 5))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Waterfox closed for Run #{visit_number}\n")

# # ================= WORKER FUNCTION (Same) =================
# def worker(visit_queue, completed_count, lock):
#     global stop_flag
#     while not stop_flag:
#         try:
#             visit_number = visit_queue.get_nowait()
#         except Empty:
#             break
        
#         open_with_proxy(visit_number)
        
#         with lock:
#             completed_count[0] += 1
#             print(f"📊 Total Completed: {completed_count[0]}/{TARGET_VISITS}")
        
#         time.sleep(random.uniform(0.8, 2.2))

# # ================= MAIN EXECUTION (Same) =================
# if __name__ == "__main__":
#     if not os.path.exists(GECKODRIVER_PATH):
#         print(f"❌ GeckoDriver not found at:\n{GECKODRIVER_PATH}")
#         sys.exit(1)
#     if not os.path.exists(WATERFOX_PATH):
#         print(f"❌ Waterfox not found at:\n{WATERFOX_PATH}")
#         sys.exit(1)
  
#     print("=== Magzter Script - Waterfox + Improved Geonode Fingerprinting ===\n")
#     print(f"Target Runs : {TARGET_VISITS} | Max Concurrent : {MAX_CONCURRENT_SESSIONS}\n")
    
#     stop_flag = False
    
#     visit_queue = Queue()
#     for i in range(1, TARGET_VISITS + 1):
#         visit_queue.put(i)
    
#     lock = threading.Lock()
#     completed_count = [0]
    
#     threads = []
#     for _ in range(MAX_CONCURRENT_SESSIONS):
#         t = threading.Thread(
#             target=worker,
#             args=(visit_queue, completed_count, lock),
#             daemon=True
#         )
#         t.start()
#         threads.append(t)
#         time.sleep(random.uniform(1.0, 2.5))
    
#     try:
#         while completed_count[0] < TARGET_VISITS and not stop_flag:
#             time.sleep(3)
#             if visit_queue.empty() and all(not t.is_alive() for t in threads):
#                 break
#     except KeyboardInterrupt:
#         print("\n\n🛑 Stopping by user request...")
#         stop_flag = True
    
#     print("\nWaiting for remaining sessions to complete...")
#     for t in threads:
#         if t.is_alive():
#             t.join(timeout=20)
    
#     print("\n🎉 Script execution finished!")
#     print(f"Total Runs Completed: {completed_count[0]}/{TARGET_VISITS}")




# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime
# import warnings
# import threading
# from queue import Queue, Empty

# # Suppress Warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     """ PyInstaller EXE ke liye sahi path deta hai """
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= GEONODE + WATERFOX CONFIG =================
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS      = "CHANGE_ME_SECRET"
# GEONODE_HOST      = "sg.proxy.geonode.io"
# GEONODE_PORT      = "11000"

# COUNTRIES = ["IT", "GR", "CH", "AT", "US", "CA"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0 Waterfox/132.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")
# LOG_FILE = "magzter_logs.json"
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# # ================= USER SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 3
# TARGET_VISITS = 2000

# # ================= GLOBAL VARIABLES =================
# stop_flag = False
# log_lock = threading.Lock()

# # ================= LOGGING =================
# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except Exception:
#             return []
#     return []

# def save_log(visit_data):
#     with log_lock:
#         logs = load_logs()
#         logs.append(visit_data)
#         try:
#             with open(LOG_FILE, 'w', encoding='utf-8') as f:
#                 json.dump(logs, f, indent=2, ensure_ascii=False)
#         except Exception as e:
#             print(f"⚠️ Log save failed: {e}")

# # ================= SINGLE VISIT FUNCTION =================
# def open_with_proxy(visit_number):
#     global stop_flag
#     if stop_flag:
#         return

#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
  
#     print(f"\n=== Run #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy : {proxy_url[:75]}...")
  
#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
#         'request_storage': 'memory',
#         'connection_timeout': 60
#     }
  
#     options = Options()
#     options.binary_location = WATERFOX_PATH
    
#     # ================= STRONG FINGERPRINTING =================
#     ua = random.choice(USER_AGENTS)
#     options.set_preference("general.useragent.override", ua)
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.set_preference("privacy.trackingprotection.enabled", True)
#     options.set_preference("media.eme.enabled", False)
#     options.set_preference("intl.accept_languages", "en-US,en")
#     options.set_preference("general.platform.override", "Win32")
    
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-blink-features=AutomationControlled")
    
#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver = None
  
#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
      
#         print("🚀 Waterfox opened with Geonode Proxy + Strong Fingerprinting...")
#         driver.get("https://app.adstracking.io/click?pid=3030&offer_id=20655")
        
#         # ================= NEW: CLICK "CLAIM NOW" BUTTON =================
#         print("⏳ Waiting for 'Claim Now' button...")
#         try:
#             wait = WebDriverWait(driver, 20)  # 20 seconds max wait
#             claim_button = wait.until(
#                 EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.m-0.yellow_btn.subscribe.svelte-1dkwios'))
#             )
#             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", claim_button)
#             time.sleep(random.uniform(0.8, 1.5))
            
#             claim_button.click()
#             print("✅ Claim Now button clicked successfully!")
#             time.sleep(random.uniform(4, 7))  # Wait after click for next page/load
            
#         except Exception as click_err:
#             print(f"⚠️ Could not click Claim Now button: {click_err}")
#             # Fallback: Try by text
#             try:
#                 claim_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Claim Now')]")
#                 claim_button.click()
#                 print("✅ Claim Now clicked using fallback XPath")
#                 time.sleep(random.uniform(3, 6))
#             except:
#                 print("❌ Both selectors failed for Claim Now")
        
#         # ================= Human-like behavior =================
#         stay_time = random.uniform(35, 60)
#         print(f"⏳ Staying {stay_time:.1f} seconds on page...")
#         start_time = time.time()
        
#         while time.time() - start_time < stay_time and not stop_flag:
#             if random.random() < 0.65:
#                 try:
#                     driver.execute_script(f"window.scrollBy(0, {random.randint(250, 750)});")
#                 except:
#                     pass
#                 time.sleep(random.uniform(1.0, 3.8))
          
#             if random.random() < 0.45:
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-150, 150), random.randint(-80, 80)).perform()
#                 except:
#                     pass
#                 time.sleep(random.uniform(0.5, 2.3))
            
#             time.sleep(0.7)
      
#         print(f"✅ Run #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s\n")
      
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "status": "success",
#             "landed_url": driver.current_url[:150],
#             "stay_duration": round(stay_time, 1)
#         }
#         save_log(visit_data)
      
#     except Exception as e:
#         print(f"❌ Error in Run #{visit_number}: {str(e)[:180]}")
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "status": "failed",
#             "error": str(e)[:200]
#         }
#         save_log(visit_data)
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 5))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Waterfox closed for Run #{visit_number}\n")

# # ================= WORKER FUNCTION =================
# def worker(visit_queue, completed_count, lock):
#     global stop_flag
#     while not stop_flag:
#         try:
#             visit_number = visit_queue.get_nowait()
#         except Empty:
#             break
        
#         open_with_proxy(visit_number)
        
#         with lock:
#             completed_count[0] += 1
#             print(f"📊 Total Completed: {completed_count[0]}/{TARGET_VISITS}")
        
#         time.sleep(random.uniform(0.8, 2.2))

# # ================= MAIN EXECUTION =================
# if __name__ == "__main__":
#     if not os.path.exists(GECKODRIVER_PATH):
#         print(f"❌ GeckoDriver not found at:\n{GECKODRIVER_PATH}")
#         sys.exit(1)
#     if not os.path.exists(WATERFOX_PATH):
#         print(f"❌ Waterfox not found at:\n{WATERFOX_PATH}")
#         sys.exit(1)
  
#     print("=== Magzter Script - Waterfox + Improved Geonode + Claim Now Click ===\n")
#     print(f"Target Runs : {TARGET_VISITS} | Max Concurrent : {MAX_CONCURRENT_SESSIONS}\n")
    
#     stop_flag = False
    
#     visit_queue = Queue()
#     for i in range(1, TARGET_VISITS + 1):
#         visit_queue.put(i)
    
#     lock = threading.Lock()
#     completed_count = [0]
    
#     threads = []
#     for _ in range(MAX_CONCURRENT_SESSIONS):
#         t = threading.Thread(
#             target=worker,
#             args=(visit_queue, completed_count, lock),
#             daemon=True
#         )
#         t.start()
#         threads.append(t)
#         time.sleep(random.uniform(1.0, 2.5))
    
#     try:
#         while completed_count[0] < TARGET_VISITS and not stop_flag:
#             time.sleep(3)
#             if visit_queue.empty() and all(not t.is_alive() for t in threads):
#                 break
#     except KeyboardInterrupt:
#         print("\n\n🛑 Stopping by user request...")
#         stop_flag = True
    
#     print("\nWaiting for remaining sessions to complete...")
#     for t in threads:
#         if t.is_alive():
#             t.join(timeout=20)
    
#     print("\n🎉 Script execution finished!")
#     print(f"Total Runs Completed: {completed_count[0]}/{TARGET_VISITS}") 





# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime
# import warnings
# import threading
# from queue import Queue, Empty

# # Suppress Warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= GEONODE + WATERFOX CONFIG =================
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS      = "CHANGE_ME_SECRET"
# GEONODE_HOST      = "sg.proxy.geonode.io"
# GEONODE_PORT      = "11000"

# COUNTRIES = ["IN"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")
# LOG_FILE = "magzter_logs.json"
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# # ================= SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 1      # OTP ke wajah se kam rakho
# TARGET_VISITS = 5              # Apne hisab se badal sakte ho

# # ================= GLOBAL =================
# stop_flag = False
# log_lock = threading.Lock()

# # ================= LOGGING =================
# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_log(visit_data):
#     with log_lock:
#         logs = load_logs()
#         logs.append(visit_data)
#         try:
#             with open(LOG_FILE, 'w', encoding='utf-8') as f:
#                 json.dump(logs, f, indent=2, ensure_ascii=False)
#         except Exception as e:
#             print(f"Log save failed: {e}")

# def generate_random_email():
#     name = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# # ================= MAIN FUNCTION =================
# def open_with_proxy(visit_number):
#     global stop_flag
#     if stop_flag:
#         return

#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"

#     print(f"\n=== Run #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy: {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
#         'request_storage': 'memory'
#     }

#     options = Options()
#     options.binary_location = WATERFOX_PATH
#     ua = random.choice(USER_AGENTS)
#     options.set_preference("general.useragent.override", ua)
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-blink-features=AutomationControlled")

#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )

#         wait = WebDriverWait(driver, 25)

#         print("🚀 Opening URL...")
#         driver.get("https://app.adstracking.io/click?pid=3030&offer_id=20655")
#         time.sleep(random.uniform(4, 7))

#         # ================= STEP 1: Claim Now =================
#         print("🔘 Clicking Claim Now...")
#         try:
#             claim_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.m-0.yellow_btn.subscribe.svelte-1dkwios')))
#             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", claim_btn)
#             time.sleep(random.uniform(1, 2))
#             claim_btn.click()
#         except:
#             driver.find_element(By.XPATH, "//button[contains(text(),'Claim Now')]").click()
#         time.sleep(random.uniform(5, 8))

#         # ================= STEP 2: Email =================
#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
#         email_field.clear()
#         email_field.send_keys(email)
#         time.sleep(random.uniform(2, 4))

#         # Continue
#         wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Continue')]"))).click()
#         time.sleep(random.uniform(5, 9))

#         # ================= STEP 3: Name + Zip =================
#         first_name, last_name = generate_name()
#         wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'First Name')]"))).send_keys(first_name)
#         wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Last Name')]"))).send_keys(last_name)
#         wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Zip Code')]"))).send_keys("000000")
#         time.sleep(random.uniform(3, 5))

#         # Submit
#         driver.find_element(By.CSS_SELECTOR, "button#submitBtn, button.svelte-xdpg18").click()
#         time.sleep(random.uniform(6, 10))

#         # ================= STEP 4: Card Details =================
#         print("💳 Filling Card Details...")
#         wait.until(EC.presence_of_element_located((By.ID, "cardNumber"))).send_keys("0000000000000000")
#         wait.until(EC.presence_of_element_located((By.ID, "cardExpiry"))).send_keys("06/28")
#         wait.until(EC.presence_of_element_located((By.ID, "cardCvc"))).send_keys("172")
#         wait.until(EC.presence_of_element_located((By.ID, "billingName"))).send_keys("rajat dalal")
#         time.sleep(random.uniform(4, 7))

#         # ================= STEP 5: Corporate =================
#         print("🏢 Corporate Form...")
#         try:
#             driver.find_element(By.CSS_SELECTOR, "div.SubmitButton-IconContainer").click()
#         except:
#             driver.find_element(By.XPATH, "//div[contains(@class,'SubmitButton')]").click()
#         time.sleep(random.uniform(5, 8))

#         driver.find_element(By.ID, "corporateId").send_keys("streakads")
#         driver.find_element(By.ID, "employeeId").send_keys("streakads1")
#         time.sleep(random.uniform(3, 5))

#         # Submit
#         driver.find_element(By.XPATH, "//a[contains(@class,'btn') and contains(text(),'Submit')]").click()
#         time.sleep(random.uniform(6, 10))

#         # ================= STEP 6: OTP =================
#         print("\n🔐 OTP Screen aaya hai!")
#         print("Browser mein OTP daal do aur neeche Enter press karo...\n")
#         input("Press Enter after entering OTP...")

#         # Final Submit
#         try:
#             final_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#submitBtn, button.submit")))
#             final_btn.click()
#             print("✅ Final Submit clicked")
#         except:
#             print("⚠️ Could not find final submit button")

#         time.sleep(8)
#         status = "success"
#         print(f"✅ Run #{visit_number} Completed Successfully!")

#     except Exception as e:
#         print(f"❌ Run #{visit_number} Failed: {str(e)[:150]}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "country": country_code,
#             "status": status
#         }
#         save_log(log_data)

#         if driver:
#             time.sleep(random.uniform(3, 6))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Browser closed for Run #{visit_number}\n")


# # ================= WORKER =================
# def worker(visit_queue, completed_count, lock):
#     global stop_flag
#     while not stop_flag:
#         try:
#             visit_number = visit_queue.get_nowait()
#         except Empty:
#             break
#         open_with_proxy(visit_number)
        
#         with lock:
#             completed_count[0] += 1
#             print(f"📊 Total Completed: {completed_count[0]}/{TARGET_VISITS}")

# # ================= MAIN =================
# if __name__ == "__main__":
#     if not os.path.exists(GECKODRIVER_PATH) or not os.path.exists(WATERFOX_PATH):
#         print("❌ GeckoDriver ya Waterfox nahi mila!")
#         sys.exit(1)

#     print("=== Magzter Full Flow - Waterfox + Selenium ===\n")
#     print(f"Target Runs : {TARGET_VISITS} | Max Concurrent : {MAX_CONCURRENT_SESSIONS}\n")

#     visit_queue = Queue()
#     for i in range(1, TARGET_VISITS + 1):
#         visit_queue.put(i)

#     lock = threading.Lock()
#     completed_count = [0]
#     threads = []

#     for _ in range(MAX_CONCURRENT_SESSIONS):
#         t = threading.Thread(target=worker, args=(visit_queue, completed_count, lock), daemon=True)
#         t.start()
#         threads.append(t)
#         time.sleep(random.uniform(1.5, 4))

#     try:
#         while completed_count[0] < TARGET_VISITS and not stop_flag:
#             time.sleep(5)
#     except KeyboardInterrupt:
#         stop_flag = True
#         print("\n🛑 Stopping...")

#     for t in threads:
#         if t.is_alive():
#             t.join(timeout=30)

#     print("\n🎉 Script Finished!")







# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime
# import warnings
# import threading
# from queue import Queue, Empty

# # Suppress Warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver
#     import selenium.webdriver.safari.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= GEONODE + WATERFOX CONFIG =================
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS      = "CHANGE_ME_SECRET"
# GEONODE_HOST      = "sg.proxy.geonode.io"
# GEONODE_PORT      = "11000"

# COUNTRIES = ["IN"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
# ]

# WATERFOX_PATH = resource_path("Waterfox/waterfox.exe")
# LOG_FILE = "magzter_logs.json"
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# # ================= SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 1     
# TARGET_VISITS = 5               

# # ================= GLOBAL =================
# stop_flag = False
# log_lock = threading.Lock()

# # ================= LOGGING =================
# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_log(visit_data):
#     with log_lock:
#         logs = load_logs()
#         logs.append(visit_data)
#         try:
#             with open(LOG_FILE, 'w', encoding='utf-8') as f:
#                 json.dump(logs, f, indent=2, ensure_ascii=False)
#         except Exception as e:
#             print(f"Log save failed: {e}")

# def generate_random_email():
#     name = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# # ================= MAIN FUNCTION =================
# def open_with_proxy(visit_number):
#     global stop_flag
#     if stop_flag:
#         return

#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"

#     print(f"\n=== Run #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy: {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
#         'request_storage': 'memory'
#     }

#     options = Options()
#     options.binary_location = WATERFOX_PATH
#     ua = random.choice(USER_AGENTS)
#     options.set_preference("general.useragent.override", ua)
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.set_preference("browser.download.folderList", 2)
#     options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )

#         wait = WebDriverWait(driver, 35)   # Increased timeout

#         print("🚀 Opening URL...")
#         driver.get("https://app.adstracking.io/click?pid=3030&offer_id=20655")
#         time.sleep(random.uniform(7, 12))

#         # ================= STEP 1: Claim Now =================
#         print("🔘 Clicking Claim Now...")
#         try:
#             claim_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.m-0.yellow_btn.subscribe.svelte-1dkwios')))
#             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", claim_btn)
#             time.sleep(random.uniform(1.5, 2.5))
#             claim_btn.click()
#         except:
#             driver.find_element(By.XPATH, "//button[contains(text(),'Claim Now')]").click()
#         time.sleep(random.uniform(7, 12))

#         # ================= STEP 2: Email =================
#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
#         email_field.clear()
#         email_field.send_keys(email)
#         time.sleep(random.uniform(2.5, 4.5))

#         wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Continue')]"))).click()
#         time.sleep(random.uniform(7, 11))

#         # ================= STEP 3: Name + Zip =================
#         first_name, last_name = generate_name()
#         wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'First Name')]"))).send_keys(first_name)
#         wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Last Name')]"))).send_keys(last_name)
#         wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Zip Code')]"))).send_keys("000000")
#         time.sleep(random.uniform(4, 7))

#         driver.find_element(By.CSS_SELECTOR, "button#submitBtn, button.svelte-xdpg18").click()
#         time.sleep(random.uniform(8, 13))

#         # ================= STEP 4: Card Details =================
#         print("💳 Waiting for Card Details Page...")
#         time.sleep(random.uniform(6, 10))
        
#         wait.until(EC.presence_of_element_located((By.ID, "cardNumber")))
#         print("💳 Filling Card Details...")
        
#         driver.find_element(By.ID, "cardNumber").send_keys("0000000000000000")
#         time.sleep(1.2)
#         driver.find_element(By.ID, "cardExpiry").send_keys("06/28")
#         time.sleep(1.2)
#         driver.find_element(By.ID, "cardCvc").send_keys("172")
#         time.sleep(1.2)
#         driver.find_element(By.ID, "billingName").send_keys("rajat dalal")
#         time.sleep(random.uniform(5, 8))

#         # ================= STEP 5: Corporate =================
#         print("🏢 Corporate Form...")
#         try:
#             corp_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.SubmitButton-IconContainer")))
#             corp_btn.click()
#         except:
#             try:
#                 driver.find_element(By.XPATH, "//div[contains(@class,'SubmitButton')]").click()
#             except:
#                 pass
#         time.sleep(random.uniform(6, 10))

#         driver.find_element(By.ID, "corporateId").send_keys("streakads")
#         driver.find_element(By.ID, "employeeId").send_keys("streakads1")
#         time.sleep(random.uniform(4, 7))

#         driver.find_element(By.XPATH, "//a[contains(@class,'btn') and contains(text(),'Submit')]").click()
#         time.sleep(random.uniform(8, 12))

#         # ================= STEP 6: OTP =================
#         print("\n🔐 OTP Screen aaya hai!")
#         print("Browser mein OTP daal do aur neeche Enter press karo...\n")
#         input("Press Enter after entering OTP...")

#         try:
#             final_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#submitBtn, button.submit")))
#             final_btn.click()
#             print("✅ Final Submit clicked")
#         except:
#             print("⚠️ Could not find final submit button")

#         time.sleep(8)
#         status = "success"
#         print(f"✅ Run #{visit_number} Completed Successfully!")

#     except WebDriverException as wd_err:
#         print(f"❌ WebDriver Error in Run #{visit_number}: {str(wd_err)[:120]}")
#         status = "failed"
#     except Exception as e:
#         print(f"❌ Run #{visit_number} Failed: {str(e)[:150]}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "country": country_code,
#             "status": status
#         }
#         save_log(log_data)

#         if driver:
#             time.sleep(random.uniform(3, 6))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Browser closed for Run #{visit_number}\n")


# # ================= WORKER =================
# def worker(visit_queue, completed_count, lock):
#     global stop_flag
#     while not stop_flag:
#         try:
#             visit_number = visit_queue.get_nowait()
#         except Empty:
#             break
#         open_with_proxy(visit_number)
        
#         with lock:
#             completed_count[0] += 1
#             print(f"📊 Total Completed: {completed_count[0]}/{TARGET_VISITS}")

# # ================= MAIN =================
# if __name__ == "__main__":
#     if not os.path.exists(GECKODRIVER_PATH) or not os.path.exists(WATERFOX_PATH):
#         print("❌ GeckoDriver ya Waterfox nahi mila!")
#         sys.exit(1)

#     print("=== Magzter Full Flow - Waterfox + Fixed WebDriver ===\n")
#     print(f"Target Runs : {TARGET_VISITS} | Max Concurrent : {MAX_CONCURRENT_SESSIONS}\n")

#     visit_queue = Queue()
#     for i in range(1, TARGET_VISITS + 1):
#         visit_queue.put(i)

#     lock = threading.Lock()
#     completed_count = [0]
#     threads = []

#     for _ in range(MAX_CONCURRENT_SESSIONS):
#         t = threading.Thread(target=worker, args=(visit_queue, completed_count, lock), daemon=True)
#         t.start()
#         threads.append(t)
#         time.sleep(random.uniform(2, 5))

#     try:
#         while completed_count[0] < TARGET_VISITS and not stop_flag:
#             time.sleep(6)
#     except KeyboardInterrupt:
#         stop_flag = True
#         print("\n🛑 Stopping...")

#     for t in threads:
#         if t.is_alive():
#             t.join(timeout=40)

#     print("\n🎉 Script Finished!")




# import time
# import random
# import string
# import json
# import os
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# GOLOGIN_TOKEN = None

# def load_token():
#     global GOLOGIN_TOKEN
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             GOLOGIN_TOKEN = f.read().strip()
#             if len(GOLOGIN_TOKEN) > 50:
#                 print("✅ GoLogin Token Loaded")
#                 return
#     except:
#         pass
#     print("❌ config.txt mein apna GoLogin token daal do!")
#     exit(1)

# load_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     return f"{name}{num}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta"]
#     return random.choice(first), random.choice(last)

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE RUN =================
# def run_one_cycle(run_number):
#     print(f"\n=== Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         # GoLogin Profile Creation (Exact same as your big script)
#         gl = GoLogin({"token": GOLOGIN_TOKEN})
#         profile_name = f"magzter-run-{run_number}-{random.randint(1000,9999)}"

#         profile = gl.createProfileRandomFingerprint({
#             "name": profile_name,
#             "os": "win",
#             "timezone": "Asia/Kolkata"
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         # Proxy Setup
#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         # Playwright Connect
#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         # Stealth
#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= MAGZTER FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=60000)
#         time.sleep(random.uniform(5, 8))

#         # Claim Now
#         page.click('button:has-text("Claim Now")', timeout=20000)
#         time.sleep(random.uniform(5, 8))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(2)
#         page.click('button:has-text("Continue")', timeout=20000)
#         time.sleep(random.uniform(6, 10))

#         # Name + Zip
#         first, last = generate_name()
#         page.fill('input[placeholder*="First Name"]', first)
#         page.fill('input[placeholder*="Last Name"]', last)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(3)
#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=25000)
#         time.sleep(random.uniform(7, 12))

#         # Card Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "172")
#         page.fill('input#billingName', "rajat dalal")
#         time.sleep(random.uniform(5, 8))

#         # Corporate
#         print("🏢 Corporate Form...")
#         page.click('div.SubmitButton-IconContainer', timeout=20000)
#         time.sleep(4)
#         page.fill('input#corporateId', "streakads")
#         page.fill('input#employeeId', "streakads1")
#         time.sleep(3)
#         page.click('a.btn.primary__btn:has-text("Submit")', timeout=20000)
#         time.sleep(random.uniform(6, 10))

#         print("\n🔐 Browser mein OTP daal do aur yahan Enter press karo...")
#         input("Press Enter after entering OTP...")

#         status = "success"
#         print(f"✅ Run #{run_number} Completed Successfully!")

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter GoLogin + Playwright (Stable) ===\n")
#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(20, 40))

#     print("\n🎉 All Runs Completed!")






# import time
# import random
# import string
# import json
# import os
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",           # ← Force English
#             "languages": ["en-US", "en"]   # ← Extra force
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         # Proxy Setup
#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         # Playwright Connect
#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         # Extra English Force
#         context.set_extra_http_headers({
#             "Accept-Language": "en-US,en;q=0.9"
#         })

#         # Strong Stealth
#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
#         }""")

#         # ================= ORIGINAL FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=90000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         # Human Simulation
#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         # Claim Now
#         print("🔘 Clicking Claim Now...")
#         page.click('button:has-text("Claim Now")', timeout=50000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=25000)
#         time.sleep(random.uniform(6, 10))

#         # Name + Zip
#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=50000)
#         time.sleep(random.uniform(7, 12))

#         # Card Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "172")
#         page.fill('input#billingName', "rajat dalal")
#         time.sleep(random.uniform(4, 7))

#         # Corporate
#         print("🏢 Corporate Form...")
#         page.click('div.SubmitButton-IconContainer', timeout=25000)
#         time.sleep(random.uniform(6, 10))

#         page.fill('input#corporateId', "streakads")
#         page.fill('input#employeeId', "streakads1")
#         time.sleep(random.uniform(3, 5))

#         page.click('a.btn.primary__btn:has-text("Submit"), a.btn.primary__btn', timeout=25000)
#         time.sleep(random.uniform(6, 10))

#         # OTP
#         print("\n🔐 OTP Form aaya - Browser mein OTP daal do")
#         print("⚠️ Enter press karo yahan...")
#         input("Press Enter after entering OTP...")

#         page.click('button#submitBtn, button.submit:has-text("SUBMIT")', timeout=20000)
#         time.sleep(8)

#         print(f"✅ Run #{run_number} Completed Successfully!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow with GoLogin + Force English ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")




# import time
# import random
# import string
# import json
# import os
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         # Proxy Setup
#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         # Playwright Connect
#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         # Force English
#         context.set_extra_http_headers({
#             "Accept-Language": "en-US,en;q=0.9"
#         })

#         # Stealth
#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
#         }""")

#         # ================= ORIGINAL FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=90000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         # Human Simulation
#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         # Claim Now
#         print("🔘 Clicking Claim Now...")
#         page.click('button:has-text("Claim Now")', timeout=50000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=25000)
#         time.sleep(random.uniform(6, 10))

#         # Name + Zip
#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=50000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "172")
#         page.fill('input#billingName', "rajat dalal")
#         time.sleep(random.uniform(4, 7))

#         # ================= CORPORATE STEP (Fixed) =================
#         print("🏢 Corporate Form...")
#         try:
#             # Click on Corporate Icon
#             page.click('div.SubmitButton-IconContainer', timeout=25000)
#             time.sleep(random.uniform(4, 7))
            
#             # Fill Corporate ID and Employee ID
#             page.fill('input#corporateId', "streakads")
#             time.sleep(1.5)
#             page.fill('input#employeeId', "streakads1")
#             time.sleep(random.uniform(3, 5))
            
#             # Submit Corporate Form
#             page.click('a.btn.primary__btn:has-text("Submit"), a.btn.primary__btn', timeout=25000)
#             time.sleep(random.uniform(6, 10))
#             print("✅ Corporate Form Submitted")
#         except Exception as corp_err:
#             print(f"⚠️ Corporate step warning: {corp_err}")

#         # OTP
#         print("\n🔐 OTP Form aaya - Browser mein OTP daal do")
#         print("⚠️ Enter press karo yahan...")
#         input("Press Enter after entering OTP...")

#         page.click('button#submitBtn, button.submit:has-text("SUBMIT")', timeout=20000)
#         time.sleep(8)

#         print(f"✅ Run #{run_number} Completed Successfully!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow with GoLogin + Corporate Fixed ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")





# import time
# import random
# import string
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# # Corporate Config
# CORPORATE_ID = "streakads"
# EMPLOYEE_ID = "CHANGE_ME_EMP_ID"
# API_EMPLOYEE_ID = "CHANGE_ME_EMP_ID"

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def get_latest_otp(max_attempts=30, delay=4):
#     url = f"https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp"
#     print(f"🔍 Waiting for OTP from API...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=90000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=50000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=25000)
#         time.sleep(random.uniform(6, 10))

#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=50000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "172")
#         page.fill('input#billingName', "rajat dalal")
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=50000)
#         time.sleep(random.uniform(7, 10))

#         # ================= CORPORATE FORM (INSIDE IFRAME) =================
#         print("🏢 Handling Corporate Form inside Iframe...")
#         try:
#             # Wait for iframe to load
#             page.wait_for_timeout(6000)
            
#             iframe = page.frame_locator("iframe#challengeFrame, iframe.ThreeDS2-challenge, iframe[name='stripe-challenge-frame']")
            
#             if iframe:
#                 print("✅ Iframe detected, switching to iframe context")
                
#                 # Fill Corporate ID inside iframe
#                 iframe.locator('input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]').first.fill(CORPORATE_ID)
#                 time.sleep(1.5)
                
#                 # Fill Employee ID inside iframe
#                 iframe.locator('input[placeholder*="Employee"], input#employeeId, input[name*="employee"]').first.fill(EMPLOYEE_ID)
#                 time.sleep(2)
                
#                 # Click Submit inside iframe
#                 iframe.locator('button:has-text("SUBMIT"), button[type="submit"], button:visible').first.click(timeout=15000)
#                 print("✅ Corporate Form Submitted (Inside Iframe)")
#                 time.sleep(random.uniform(6, 9))
#             else:
#                 print("⚠️ Iframe not found, trying main page")
#                 # Fallback (old method)
#                 page.fill('input#corporateId, input[placeholder*="Corporate"]', CORPORATE_ID)
#                 time.sleep(1.5)
#                 page.fill('input#employeeId, input[placeholder*="Employee"]', EMPLOYEE_ID)
#                 page.click('button:has-text("SUBMIT")')
#                 time.sleep(6)

#         except Exception as corp_err:
#             print(f"⚠️ Corporate Iframe Error: {corp_err}")
#             # Final fallback
#             try:
#                 page.keyboard.type(CORPORATE_ID)
#                 page.keyboard.press("Tab")
#                 page.keyboard.type(EMPLOYEE_ID)
#                 page.keyboard.press("Enter")
#             except:
#                 pass

#         # ================= AUTO OTP =================
#         print("\n🔐 Fetching OTP from API...")
#         otp = get_latest_otp(max_attempts=30, delay=4)
        
#         if otp:
#             try:
#                 otp_selectors = [
#                     'input[autocomplete="one-time-code"]',
#                     'input[name="otp"]',
#                     'input[placeholder*="OTP" i]',
#                     'input#otp',
#                     'input[type="text"][maxlength="6"]'
#                 ]
                
#                 for selector in otp_selectors:
#                     try:
#                         page.wait_for_selector(selector, timeout=12000)
#                         page.fill(selector, otp)
#                         print(f"✅ OTP filled with: {selector}")
#                         break
#                     except:
#                         continue
                
#                 time.sleep(2.5)
#                 page.click('button#submitBtn, button:has-text("SUBMIT"), button:has-text("Verify"), button[type="submit"]', timeout=20000)
#                 time.sleep(8)
                
#             except Exception as otp_err:
#                 print(f"⚠️ OTP Error: {otp_err}")
#         else:
#             print("❌ OTP fetch failed")

#         print(f"✅ Run #{run_number} Completed!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow - IFRAME Corporate Fix + Auto OTP ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")



# import time
# import random
# import string
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# # Corporate Config
# CORPORATE_ID = "streakads"
# EMPLOYEE_ID = "CHANGE_ME_EMP_ID"
# API_EMPLOYEE_ID = "CHANGE_ME_EMP_ID"

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def get_latest_otp(max_attempts=30, delay=4):
#     url = f"https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp"
#     print(f"🔍 Waiting for OTP from API...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=90000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "164")
#         page.fill('input#billingName', "john doe")
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=200000)
#         time.sleep(random.uniform(7, 10))

#         # ================= CORPORATE FORM (INSIDE IFRAME) - IMPROVED =================
#         print("🏢 Handling Corporate Form inside Iframe...")
#         try:
#             page.wait_for_timeout(8000)  # Extra wait for iframe to fully load
            
#             # Get iframe
#             iframe_locator = page.frame_locator("iframe#challengeFrame, iframe.ThreeDS2-challenge, iframe[name='stripe-challenge-frame']")
            
#             # Check if iframe exists
#             if iframe_locator.count() > 0:
#                 print("✅ Iframe detected")
#                 iframe = iframe_locator.first
                
#                 # Wait for form to be visible inside iframe
#                 iframe.wait_for_selector('input', timeout=200000)
#                 print("✅ Form fields visible inside iframe")
                
#                 # Fill Corporate ID
#                 corp_selector = 'input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]'
#                 iframe.locator(corp_selector).first.fill(CORPORATE_ID)
#                 print(f"✅ Corporate ID filled: {CORPORATE_ID}")
#                 time.sleep(2)
                
#                 # Fill Employee ID (with more wait and fallback)
#                 emp_selector = 'CHANGE_ME_EMP_ID"Employee"], input#employeeId, input[name*="employee"]'
#                 try:
#                     iframe.locator(emp_selector).first.fill(EMPLOYEE_ID)
#                     print(f"✅ Employee ID filled: {EMPLOYEE_ID}")
#                 except Exception as emp_err:
#                     print(f"⚠️ Direct Employee fill failed, trying keyboard: {emp_err}")
#                     iframe.locator('input').nth(1).fill(EMPLOYEE_ID)  # Second input field
                
#                 time.sleep(2.5)
                
#                 # Click Submit
#                 submit_btn = iframe.locator('button:has-text("SUBMIT"), button[type="submit"], button:visible:has-text("SUBMIT")')
#                 submit_btn.first.click(timeout=15000)
#                 print("✅ Corporate Submit clicked inside iframe")
#                 time.sleep(random.uniform(6, 10))
                
#             else:
#                 print("⚠️ Iframe not found - trying main page fallback")
#                 page.fill('input#corporateId, input[placeholder*="Corporate"]', CORPORATE_ID)
#                 time.sleep(1.5)
#                 page.fill('input#employeeId, input[placeholder*="Employee"]', EMPLOYEE_ID)
#                 page.click('button:has-text("SUBMIT")')
#                 time.sleep(6)

#         except Exception as corp_err:
#             print(f"⚠️ Corporate Iframe Error: {corp_err}")
#             # Keyboard fallback
#             try:
#                 print("🔄 Using keyboard fallback")
#                 page.keyboard.type(CORPORATE_ID)
#                 page.keyboard.press("Tab")
#                 time.sleep(1)
#                 page.keyboard.type(EMPLOYEE_ID)
#                 page.keyboard.press("Enter")
#             except:
#                 pass

#         # ================= AUTO OTP =================
#         print("\n🔐 Fetching OTP from API...")
#         otp = get_latest_otp(max_attempts=30, delay=4)
        
#         if otp:
#             try:
#                 otp_selectors = [
#                     'input[autocomplete="one-time-code"]',
#                     'input[name="otp"]',
#                     'input[placeholder*="OTP" i]',
#                     'input#otp',
#                     'input[type="text"][maxlength="6"]'
#                 ]
                
#                 for selector in otp_selectors:
#                     try:
#                         page.wait_for_selector(selector, timeout=15000)
#                         page.fill(selector, otp)
#                         print(f"✅ OTP filled with: {selector}")
#                         break
#                     except:
#                         continue
                
#                 time.sleep(3)
#                 page.click('button#submitBtn, button:has-text("SUBMIT"), button:has-text("Verify"), button[type="submit"]', timeout=20000)
#                 time.sleep(8)
                
#             except Exception as otp_err:
#                 print(f"⚠️ OTP Error: {otp_err}")
#         else:
#             print("❌ OTP fetch failed")

#         print(f"✅ Run #{run_number} Completed!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow - Improved Iframe Corporate Fix ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")







# import time
# import random
# import string
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# # Corporate Config
# CORPORATE_ID = "streakads"
# EMPLOYEE_ID = "CHANGE_ME_EMP_ID"
# API_EMPLOYEE_ID = "CHANGE_ME_EMP_ID"

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def get_latest_otp(max_attempts=30, delay=4):
#     url = f"https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp"
#     print(f"🔍 Waiting for OTP from API...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=90000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "164")
#         page.fill('input#billingName', "john doe")
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=200000)
#         time.sleep(random.uniform(7, 10))

#         # ================= CORPORATE FORM (INSIDE IFRAME) - STRONG FIX =================
#         print("🏢 Handling Corporate Form inside Iframe...")
#         try:
#             page.wait_for_timeout(8000)
            
#             iframe_locator = page.frame_locator("iframe#challengeFrame, iframe.ThreeDS2-challenge, iframe[name='stripe-challenge-frame']")
            
#             if iframe_locator.count() > 0:
#                 print("✅ Iframe detected")
#                 iframe = iframe_locator.first
                
#                 # Strong wait for form
#                 iframe.wait_for_selector("input", timeout=200000)
#                 print("✅ Inputs visible inside iframe")
                
#                 time.sleep(2)
                
#                 # Fill Corporate ID (First Input)
#                 try:
#                     iframe.locator("input").nth(0).fill(CORPORATE_ID)
#                     print(f"✅ Corporate ID filled: {CORPORATE_ID}")
#                 except:
#                     iframe.locator('input[placeholder*="Corporate"], input#corporateId').first.fill(CORPORATE_ID)
#                     print(f"✅ Corporate ID filled (fallback)")
                
#                 time.sleep(2)
                
#                 # Fill Employee ID (Second Input)
#                 try:
#                     iframe.locator("input").nth(1).fill(EMPLOYEE_ID)
#                     print(f"✅ Employee ID filled: {EMPLOYEE_ID}")
#                 except Exception as e:
#                     print(f"⚠️ Trying alternative for Employee ID: {e}")
#                     iframe.locator('input[placeholder*="Employee"], input#employeeId').first.fill(EMPLOYEE_ID)
                
#                 time.sleep(2.5)
                
#                 # Click Submit Button
#                 try:
#                     iframe.locator('button:has-text("SUBMIT"), button[type="submit"]').first.click(timeout=20000)
#                     print("✅ Corporate Submit clicked inside iframe")
#                 except:
#                     iframe.locator("button").filter(has_text="SUBMIT").first.click(timeout=15000)
#                     print("✅ Corporate Submit clicked (text filter)")
                
#                 time.sleep(random.uniform(6, 10))
                
#             else:
#                 print("⚠️ Iframe not found, trying fallback")
#                 page.fill('input#corporateId, input[placeholder*="Corporate"]', CORPORATE_ID)
#                 time.sleep(1.5)
#                 page.fill('input#employeeId, input[placeholder*="Employee"]', EMPLOYEE_ID)
#                 page.click('button:has-text("SUBMIT")')
#                 time.sleep(6)

#         except Exception as corp_err:
#             print(f"⚠️ Corporate Iframe Error: {corp_err}")
#             # Ultimate Keyboard Fallback
#             try:
#                 print("🔄 Using Keyboard Fallback")
#                 page.keyboard.type(CORPORATE_ID)
#                 page.keyboard.press("Tab")
#                 time.sleep(1.5)
#                 page.keyboard.type(EMPLOYEE_ID)
#                 page.keyboard.press("Enter")
#             except:
#                 pass

#         # ================= AUTO OTP =================
#         print("\n🔐 Fetching OTP from API...")
#         otp = get_latest_otp(max_attempts=30, delay=4)
        
#         if otp:
#             try:
#                 otp_selectors = [
#                     'input[autocomplete="one-time-code"]',
#                     'input[name="otp"]',
#                     'input[placeholder*="OTP" i]',
#                     'input#otp',
#                     'input[type="text"][maxlength="6"]'
#                 ]
                
#                 for selector in otp_selectors:
#                     try:
#                         page.wait_for_selector(selector, timeout=15000)
#                         page.fill(selector, otp)
#                         print(f"✅ OTP filled with: {selector}")
#                         break
#                     except:
#                         continue
                
#                 time.sleep(3)
#                 page.click('button#submitBtn, button:has-text("SUBMIT"), button:has-text("Verify"), button[type="submit"]', timeout=20000)
#                 time.sleep(8)
                
#             except Exception as otp_err:
#                 print(f"⚠️ OTP Error: {otp_err}")
#         else:
#             print("❌ OTP fetch failed")

#         print(f"✅ Run #{run_number} Completed!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow - Final Iframe Corporate Fix ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")






# import time
# import random
# import string
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# # Corporate Config
# CORPORATE_ID = "streakads"
# EMPLOYEE_ID = "CHANGE_ME_EMP_ID"
# API_EMPLOYEE_ID = "CHANGE_ME_EMP_ID"

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def get_latest_otp(max_attempts=30, delay=4):
#     url = f"https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp"
#     print(f"🔍 Waiting for OTP from API...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=90000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "164")
#         page.fill('input#billingName', "john doe")
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=200000)
#         time.sleep(random.uniform(7, 10))

#         # ================= CORPORATE FORM (IFRAME) - FULLY FIXED =================
#         print("🏢 Handling Corporate Form inside Iframe...")
#         time.sleep(8)

#         # Debug: saare frames dekho
#         print("📋 Frames available:")
#         for i, frame in enumerate(page.frames):
#             print(f"  [{i}] name='{frame.name}' | url='{frame.url}'")

#         # Iframe detect karo
#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             name_match = any(x in frame.name.lower() for x in ["challenge", "stripe", "3ds", "threeds"])
#             url_match  = any(x in frame.url.lower()  for x in ["challenge", "3ds", "acs", "authenticate", "capitalone"])
#             if name_match or url_match:
#                 iframe = frame
#                 print(f"✅ Iframe Found: name='{frame.name}'")
#                 break

#         # Fallback: pehla non-main frame lo
#         if not iframe:
#             non_main = [f for f in page.frames if f != page.main_frame]
#             if non_main:
#                 iframe = non_main[0]
#                 print(f"⚠️ Fallback iframe: name='{iframe.name}' url='{iframe.url}'")

#         if iframe:
#             iframe.wait_for_selector('input', timeout=200000)
#             time.sleep(2)

#             # Corporate ID
#             try:
#                 iframe.fill('#corporateId', CORPORATE_ID)
#                 print(f"✅ Corporate ID: {CORPORATE_ID}")
#             except:
#                 iframe.locator('input').nth(0).fill(CORPORATE_ID)
#                 print(f"✅ Corporate ID (nth 0): {CORPORATE_ID}")

#             time.sleep(2)

#             # Employee ID
#             try:
#                 iframe.fill('#employeeId', EMPLOYEE_ID)
#                 print(f"✅ Employee ID: {EMPLOYEE_ID}")
#             except:
#                 iframe.locator('input').nth(1).fill(EMPLOYEE_ID)
#                 print(f"✅ Employee ID (nth 1): {EMPLOYEE_ID}")

#             time.sleep(2)

#             # Submit - <a> tag hai!
#             try:
#                 iframe.click('a.primary__btn', timeout=200000)
#                 print("✅ Submit Clicked")
#             except:
#                 try:
#                     iframe.click('a:has-text("Submit")', timeout=200000)
#                 except:
#                     iframe.evaluate("""() => {
#                         const btn = document.querySelector('a.primary__btn')
#                                  || document.querySelector('a[onclick*="submit"]')
#                                  || Array.from(document.querySelectorAll('a'))
#                                     .find(a => /submit/i.test(a.textContent));
#                         if(btn) btn.click();
#                     }""")
#                 print("✅ Submit via fallback")
#         else:
#             print("❌ No iframe found at all - check frame debug output above") 

#         time.sleep(8)

#         # ================= AUTO OTP =================
#         print("\n🔐 Fetching OTP from API...")
#         otp = get_latest_otp(max_attempts=30, delay=4)
        
#         if otp:
#             try:
#                 otp_selectors = [
#                     'input[autocomplete="one-time-code"]',
#                     'input[name="otp"]',
#                     'input[placeholder*="OTP" i]',
#                     'input#otp',
#                     'input[type="text"][maxlength="6"]'
#                 ]
                
#                 for selector in otp_selectors:
#                     try:
#                         page.wait_for_selector(selector, timeout=15000)
#                         page.fill(selector, otp)
#                         print(f"✅ OTP filled with: {selector}")
#                         break
#                     except:
#                         continue
                
#                 time.sleep(3)
#                 page.click('button#submitBtn, button:has-text("SUBMIT"), button:has-text("Verify")', timeout=20000)
#                 time.sleep(8)
#             except Exception as otp_err:
#                 print(f"⚠️ OTP Error: {otp_err}")
#         else:
#             print("❌ OTP fetch failed")

#         print(f"✅ Run #{run_number} Completed!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow - Fixed Iframe Corporate Form ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")






# import time
# import random
# import string
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# # Corporate Config
# CORPORATE_ID = "streakads"
# EMPLOYEE_ID = "CHANGE_ME_EMP_ID"
# API_EMPLOYEE_ID = "CHANGE_ME_EMP_ID"

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def get_latest_otp(max_attempts=30, delay=4):
#     url = f"https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp"
#     print(f"🔍 Waiting for OTP from API...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=90000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "164")
#         page.fill('input#billingName', "john doe")
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=200000)
#         time.sleep(random.uniform(8, 12))

#         # ================= CORPORATE FORM DETECTION =================
#         print("🏢 Waiting for Corporate Form...")
#         time.sleep(10)

#         # Wait for Stripe checkout page + Corporate text
#         try:
#             page.wait_for_load_state("networkidle", timeout=200000)
#         except:
#             pass

#         corporate_text = page.get_by_text("Corporate ID", timeout=200000)
#         if corporate_text.count() > 0 or page.get_by_text("Employee ID").count() > 0:
#             print("✅ Corporate Form Detected by Text")
#         else:
#             print("⚠️ Corporate text not immediately visible, continuing...")

#         print("📋 All Frames:")
#         for i, frame in enumerate(page.frames):
#             print(f"  [{i}] name='{frame.name}' | url='{frame.url[:120]}...'")

#         # Smart Iframe Detection
#         iframe = None
#         corporate_keywords = ["corporate", "employee", "challenge", "3ds", "authenticate", "stripe-origin"]

#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             name_lower = (frame.name or "").lower()
#             url_lower = (frame.url or "").lower()
            
#             if any(k in name_lower for k in corporate_keywords) or any(k in url_lower for k in corporate_keywords):
#                 iframe = frame
#                 print(f"✅ Matched Iframe: name='{frame.name}'")
#                 break

#         # Fallback: Find frame containing corporate text
#         if not iframe:
#             non_main = [f for f in page.frames if f != page.main_frame]
#             for f in non_main:
#                 try:
#                     if f.get_by_text("Corporate ID").count() > 0 or f.get_by_text("Employee ID").count() > 0:
#                         iframe = f
#                         print("✅ Iframe Found via Text Content")
#                         break
#                 except:
#                     continue

#         # Ultimate fallback - first frame with inputs
#         if not iframe and non_main:
#             for f in non_main:
#                 try:
#                     if f.locator('input').count() >= 1:
#                         iframe = f
#                         print("✅ Fallback: First frame with input fields")
#                         break
#                 except:
#                     continue

#         if iframe:
#             print("🔍 Filling Corporate Form...")
#             try:
#                 iframe.wait_for_selector('input', timeout=200000)
#                 time.sleep(3)
#             except:
#                 print("⚠️ Wait for input timed out, trying anyway")

#             # Fill fields
#             try:
#                 iframe.fill('input#corporateId, input[placeholder*="Corporate"], input[name*="corporate"]', CORPORATE_ID)
#                 print(f"✅ Corporate ID: {CORPORATE_ID}")
#             except:
#                 try:
#                     iframe.locator('input').nth(0).fill(CORPORATE_ID)
#                     print("✅ Corporate ID (nth 0)")
#                 except:
#                     pass

#             time.sleep(2)

#             try:
#                 iframe.fill('input#employeeId, input[placeholder*="Employee"], input[name*="employee"]', EMPLOYEE_ID)
#                 print(f"✅ Employee ID: {EMPLOYEE_ID}")
#             except:
#                 try:
#                     iframe.locator('input').nth(1).fill(EMPLOYEE_ID)
#                     print("✅ Employee ID (nth 1)")
#                 except:
#                     pass

#             time.sleep(2)

#             # Submit
#             try:
#                 iframe.click('a.primary__btn, button:has-text("Submit"), a:has-text("Submit")', timeout=200000)
#                 print("✅ Submit Clicked")
#             except:
#                 try:
#                     iframe.click('a:has-text("Submit"), button:has-text("SUBMIT")', timeout=200000)
#                 except:
#                     iframe.evaluate("""() => {
#                         const els = document.querySelectorAll('a, button');
#                         for (let el of els) {
#                             if (/submit|continue|pay/i.test((el.textContent || '').toLowerCase())) {
#                                 el.click();
#                                 return;
#                             }
#                         }
#                     }""")
#                     print("✅ Submit via JS")
#         else:
#             print("❌ No iframe found. Trying main page fallback...")
#             try:
#                 page.fill('input[placeholder*="Corporate"]', CORPORATE_ID)
#                 page.fill('input[placeholder*="Employee"]', EMPLOYEE_ID)
#                 page.click('a:has-text("Submit"), button:has-text("Submit")')
#             except:
#                 print("⚠️ Main page fallback failed")

#         time.sleep(10)

#         # ================= AUTO OTP =================
#         print("\n🔐 Fetching OTP from API...")
#         otp = get_latest_otp(max_attempts=30, delay=4)
        
#         if otp:
#             try:
#                 otp_selectors = [
#                     'input[autocomplete="one-time-code"]',
#                     'input[name="otp"]',
#                     'input[placeholder*="OTP" i]',
#                     'input#otp',
#                     'input[type="text"][maxlength="6"]'
#                 ]
                
#                 for selector in otp_selectors:
#                     try:
#                         page.wait_for_selector(selector, timeout=200000)
#                         page.fill(selector, otp)
#                         print(f"✅ OTP filled with: {selector}")
#                         break
#                     except:
#                         continue
                
#                 time.sleep(3)
#                 page.click('button#submitBtn, button:has-text("SUBMIT"), button:has-text("Verify")', timeout=200000)
#                 time.sleep(8)
#             except Exception as otp_err:
#                 print(f"⚠️ OTP Error: {otp_err}")
#         else:
#             print("❌ OTP fetch failed")

#         print(f"✅ Run #{run_number} Completed!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow - Text + Iframe Corporate Detection ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")






# import time
# import random
# import string
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# # Corporate Config
# CORPORATE_ID = "streakads"
# EMPLOYEE_ID = "CHANGE_ME_EMP_ID"
# API_EMPLOYEE_ID = "CHANGE_ME_EMP_ID"

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def get_latest_otp(max_attempts=30, delay=4):
#     url = f"https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp"
#     print(f"🔍 Waiting for OTP from API...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=200000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "164")
#         page.fill('input#billingName', "john doe")
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=200000)
#         time.sleep(random.uniform(8, 12))

#         # ================= CORPORATE FORM DETECTION (FIXED) =================
#         print("🏢 Waiting for Corporate Form...")
#         time.sleep(10)

#         try:
#             page.wait_for_load_state("networkidle", timeout=200000)
#         except:
#             pass

#         # Check for Corporate Form using text
#         corporate_detected = False
#         try:
#             if page.get_by_text("Corporate ID").count() > 0 or page.get_by_text("Employee ID").count() > 0:
#                 print("✅ Corporate Form Detected by Text on Main Page")
#                 corporate_detected = True
#         except:
#             pass

#         print("📋 All Frames:")
#         for i, frame in enumerate(page.frames):
#             print(f"  [{i}] name='{frame.name}' | url='{frame.url[:120]}...'")

#         # Smart Iframe Detection
#         iframe = None
#         corporate_keywords = ["corporate", "employee", "challenge", "3ds", "authenticate", "stripe-origin"]

#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             name_lower = (frame.name or "").lower()
#             url_lower = (frame.url or "").lower()
            
#             if any(k in name_lower for k in corporate_keywords) or any(k in url_lower for k in corporate_keywords):
#                 iframe = frame
#                 print(f"✅ Matched Iframe: name='{frame.name}'")
#                 break

#         # Fallback: Find frame containing corporate text
#         if not iframe:
#             non_main = [f for f in page.frames if f != page.main_frame]
#             for f in non_main:
#                 try:
#                     if (f.get_by_text("Corporate ID").count() > 0 or 
#                         f.get_by_text("Employee ID").count() > 0):
#                         iframe = f
#                         print("✅ Iframe Found via Text Content")
#                         corporate_detected = True
#                         break
#                 except:
#                     continue

#         # Ultimate fallback - first frame with inputs
#         if not iframe:
#             non_main = [f for f in page.frames if f != page.main_frame]
#             for f in non_main:
#                 try:
#                     if f.locator('input').count() >= 1:
#                         iframe = f
#                         print("✅ Fallback: First frame with input fields")
#                         break
#                 except:
#                     continue

#         if iframe:
#             print("🔍 Filling Corporate Form in Iframe...")
#             try:
#                 iframe.wait_for_selector('input', timeout=200000)
#                 time.sleep(3)
#             except:
#                 print("⚠️ Input wait timed out, proceeding...")

#             # Fill Corporate ID
#             try:
#                 iframe.fill('input#corporateId, input[placeholder*="Corporate"], input[name*="corporate"]', CORPORATE_ID)
#                 print(f"✅ Corporate ID: {CORPORATE_ID}")
#             except:
#                 try:
#                     iframe.locator('input').nth(0).fill(CORPORATE_ID)
#                     print("✅ Corporate ID (nth 0)")
#                 except:
#                     pass

#             time.sleep(2)

#             # Fill Employee ID
#             try:
#                 iframe.fill('input#employeeId, input[placeholder*="Employee"], input[name*="employee"]', EMPLOYEE_ID)
#                 print(f"✅ Employee ID: {EMPLOYEE_ID}")
#             except:
#                 try:
#                     iframe.locator('input').nth(1).fill(EMPLOYEE_ID)
#                     print("✅ Employee ID (nth 1)")
#                 except:
#                     pass

#             time.sleep(2)

#             # Submit Button
#             try:
#                 iframe.click('a.primary__btn, a:has-text("Submit"), button:has-text("Submit")', timeout=200000)
#                 print("✅ Submit Clicked")
#             except:
#                 try:
#                     iframe.click('a:has-text("Submit"), button:has-text("SUBMIT")', timeout=200000)
#                 except:
#                     iframe.evaluate("""() => {
#                         const els = document.querySelectorAll('a, button');
#                         for (let el of els) {
#                             if (/submit|continue|pay/i.test((el.textContent || '').toLowerCase())) {
#                                 el.click();
#                                 return;
#                             }
#                         }
#                     }""")
#                     print("✅ Submit via JS fallback")
#         else:
#             print("❌ No iframe found. Trying main page fallback...")
#             try:
#                 page.fill('input[placeholder*="Corporate"], input[name*="corporate"]', CORPORATE_ID)
#                 page.fill('input[placeholder*="Employee"], input[name*="employee"]', EMPLOYEE_ID)
#                 page.click('a:has-text("Submit"), button:has-text("Submit")', timeout=200000)
#             except:
#                 print("⚠️ Main page fallback failed")

#         time.sleep(10)

#         # ================= AUTO OTP =================
#         print("\n🔐 Fetching OTP from API...")
#         otp = get_latest_otp(max_attempts=30, delay=4)
        
#         if otp:
#             try:
#                 otp_selectors = [
#                     'input[autocomplete="one-time-code"]',
#                     'input[name="otp"]',
#                     'input[placeholder*="OTP" i]',
#                     'input#otp',
#                     'input[type="text"][maxlength="6"]'
#                 ]
                
#                 for selector in otp_selectors:
#                     try:
#                         page.wait_for_selector(selector, timeout=200000)
#                         page.fill(selector, otp)
#                         print(f"✅ OTP filled with: {selector}")
#                         break
#                     except:
#                         continue
                
#                 time.sleep(3)
#                 page.click('button#submitBtn, button:has-text("SUBMIT"), button:has-text("Verify")', timeout=200000)
#                 time.sleep(8)
#             except Exception as otp_err:
#                 print(f"⚠️ OTP Error: {otp_err}")
#         else:
#             print("❌ OTP fetch failed")

#         print(f"✅ Run #{run_number} Completed!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow - Fixed Corporate Detection ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")




# import time
# import random
# import string
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# # Corporate Config
# CORPORATE_ID = "streakads"
# EMPLOYEE_ID = "CHANGE_ME_EMP_ID"
# API_EMPLOYEE_ID = "CHANGE_ME_EMP_ID"

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def get_latest_otp(max_attempts=30, delay=4):
#     url = f"https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp"
#     print(f"🔍 Waiting for OTP from API...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=200000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "164")
#         page.fill('input#billingName', "john doe")
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=200000)
#         time.sleep(random.uniform(10, 15))   # Extra wait for bank challenge

#         # ================= CORPORATE FORM (ICICI BANK) =================
#         print("🏢 Waiting for ICICI Corporate Form...")
#         time.sleep(12)

#         try:
#             page.wait_for_load_state("networkidle", timeout=200000)
#         except:
#             pass

#         print("📋 All Frames Debug:")
#         for i, frame in enumerate(page.frames):
#             print(f"  [{i}] name='{frame.name}' | url='{frame.url[:150]}...'")

#         # Find the correct iframe (Corporate Form)
#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 # Check by text inside frame
#                 if (frame.get_by_text("Corporate ID").count() > 0 or 
#                     frame.get_by_text("Employee ID").count() > 0):
#                     iframe = frame
#                     print(f"✅ Corporate Form Iframe Found by Text!")
#                     break
#             except:
#                 continue

#         # Fallback by keywords
#         if not iframe:
#             for frame in page.frames:
#                 if frame == page.main_frame:
#                     continue
#                 name_lower = (frame.name or "").lower()
#                 url_lower = (frame.url or "").lower()
#                 if any(k in name_lower + url_lower for k in ["challenge", "3ds", "icici", "corporate", "employee"]):
#                     iframe = frame
#                     print(f"✅ Iframe Found by Keyword: {frame.name}")
#                     break

#         if iframe:
#             print("🔍 Filling Corporate Form...")
#             iframe.wait_for_selector('input', timeout=200000)
#             time.sleep(4)

#             # Fill Corporate ID (first input)
#             try:
#                 iframe.fill('input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]', CORPORATE_ID)
#                 print(f"✅ Corporate ID Filled")
#             except:
#                 iframe.locator('input').nth(0).fill(CORPORATE_ID)
#                 print("✅ Corporate ID (Position 1)")

#             time.sleep(2)

#             # Fill Employee ID (second input)
#             try:
#                 iframe.fill('input[placeholder*="Employee"], input#employeeId, input[name*="employee"]', EMPLOYEE_ID)
#                 print(f"✅ Employee ID Filled")
#             except:
#                 iframe.locator('input').nth(1).fill(EMPLOYEE_ID)
#                 print("✅ Employee ID (Position 2)")

#             time.sleep(2)

#             # Click SUBMIT button (blue button as per screenshot)
#             try:
#                 iframe.click('button:has-text("SUBMIT"), button[type="submit"], a:has-text("SUBMIT")', timeout=200000)
#                 print("✅ SUBMIT Clicked")
#             except:
#                 try:
#                     iframe.locator('button').filter(has_text="SUBMIT").click(timeout=200000)
#                 except:
#                     iframe.evaluate("""() => {
#                         const btns = document.querySelectorAll('button, a');
#                         for (let b of btns) {
#                             if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) {
#                                 b.click();
#                                 return;
#                             }
#                         }
#                     }""")
#                     print("✅ SUBMIT via JS")
#         else:
#             print("❌ Iframe not found - trying main page")
#             try:
#                 page.fill('input[placeholder*="Corporate"]', CORPORATE_ID)
#                 page.fill('input[placeholder*="Employee"]', EMPLOYEE_ID)
#                 page.click('button:has-text("SUBMIT")')
#             except:
#                 print("⚠️ Main page fallback failed")

#         time.sleep(10)

#         # ================= AUTO OTP =================
#         print("\n🔐 Fetching OTP from API...")
#         otp = get_latest_otp(max_attempts=30, delay=4)
        
#         if otp:
#             try:
#                 otp_selectors = [
#                     'input[autocomplete="one-time-code"]',
#                     'input[name="otp"]',
#                     'input[placeholder*="OTP" i]',
#                     'input#otp',
#                     'input[type="text"][maxlength="6"]'
#                 ]
                
#                 for selector in otp_selectors:
#                     try:
#                         page.wait_for_selector(selector, timeout=200000)
#                         page.fill(selector, otp)
#                         print(f"✅ OTP filled with: {selector}")
#                         break
#                     except:
#                         continue
                
#                 time.sleep(3)
#                 page.click('button#submitBtn, button:has-text("SUBMIT"), button:has-text("Verify")', timeout=200000)
#                 time.sleep(8)
#             except Exception as otp_err:
#                 print(f"⚠️ OTP Error: {otp_err}")
#         else:
#             print("❌ OTP fetch failed")

#         print(f"✅ Run #{run_number} Completed!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow - ICICI Corporate Form Fixed ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")





# import time
# import random
# import string
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False

# # Corporate Config
# CORPORATE_ID = "streakads"
# EMPLOYEE_ID = "CHANGE_ME_EMP_ID"
# API_EMPLOYEE_ID = "CHANGE_ME_EMP_ID"

# def load_gologin_token():
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             token = f.read().strip()
#             if len(token) > 50:
#                 print("✅ GoLogin Token Loaded Successfully")
#                 return token
#     except:
#         pass
#     print("❌ config.txt mein apna real GoLogin token daal do!")
#     exit(1)

# GOLOGIN_TOKEN = load_gologin_token()

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# def get_latest_otp(max_attempts=30, delay=4):
#     url = f"https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp"
#     print(f"🔍 Waiting for OTP from API...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=500)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     try:
#         gl = GoLogin({"token": GOLOGIN_TOKEN})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=200000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         email = generate_random_email()
#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         first_name, last_name = generate_name()
#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', "000000")
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', "0000000000000000")
#         page.fill('input#cardExpiry', "06/28")
#         page.fill('input#cardCvc', "164")
#         page.fill('input#billingName', "john doe")
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=200000)
#         time.sleep(random.uniform(10, 15))

#         # ================= CORPORATE FORM (ICICI BANK) =================
#         print("🏢 Waiting for ICICI Corporate Form...")
#         time.sleep(12)

#         try:
#             page.wait_for_load_state("networkidle", timeout=200000)
#         except:
#             pass

#         print("📋 All Frames Debug:")
#         for i, frame in enumerate(page.frames):
#             print(f"  [{i}] name='{frame.name}' | url='{frame.url[:150]}...'")

#         # Find the correct iframe
#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if (frame.get_by_text("Corporate ID").count() > 0 or 
#                     frame.get_by_text("Employee ID").count() > 0):
#                     iframe = frame
#                     print(f"✅ Corporate Form Iframe Found by Text!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             for frame in page.frames:
#                 if frame == page.main_frame:
#                     continue
#                 name_lower = (frame.name or "").lower()
#                 url_lower = (frame.url or "").lower()
#                 if any(k in name_lower + url_lower for k in ["challenge", "3ds", "icici", "corporate", "employee"]):
#                     iframe = frame
#                     print(f"✅ Iframe Found by Keyword: {frame.name}")
#                     break

#         if iframe:
#             print("🔍 Filling Corporate Form...")
#             iframe.wait_for_selector('input', timeout=200000)
#             time.sleep(4)

#             try:
#                 iframe.fill('input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]', CORPORATE_ID)
#                 print(f"✅ Corporate ID Filled")
#             except:
#                 iframe.locator('input').nth(0).fill(CORPORATE_ID)
#                 print("✅ Corporate ID (Position 1)")

#             time.sleep(2)

#             try:
#                 iframe.fill('input[placeholder*="Employee"], input#employeeId, input[name*="employee"]', EMPLOYEE_ID)
#                 print(f"✅ Employee ID Filled")
#             except:
#                 iframe.locator('input').nth(1).fill(EMPLOYEE_ID)
#                 print("✅ Employee ID (Position 2)")

#             time.sleep(2)

#             try:
#                 iframe.click('button:has-text("SUBMIT"), button[type="submit"]', timeout=200000)
#                 print("✅ Corporate SUBMIT Clicked")
#             except:
#                 iframe.evaluate("""() => {
#                     const btns = document.querySelectorAll('button, a');
#                     for (let b of btns) {
#                         if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) {
#                             b.click();
#                             return;
#                         }
#                     }
#                 }""")
#                 print("✅ Corporate SUBMIT via JS")
#         else:
#             print("❌ Iframe not found - trying main page")
#             try:
#                 page.fill('input[placeholder*="Corporate"]', CORPORATE_ID)
#                 page.fill('input[placeholder*="Employee"]', EMPLOYEE_ID)
#                 page.click('button:has-text("SUBMIT")')
#             except:
#                 print("⚠️ Main page fallback failed")

#         # ================= OTP FORM (Same Iframe) =================
#         print("\n🔐 Waiting for OTP Form...")
#         time.sleep(20)

#         # Re-detect iframe for OTP screen
#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if frame.get_by_text("Enter OTP").count() > 0 or frame.get_by_text("Cardholder authentication").count() > 0:
#                     iframe = frame
#                     print("✅ OTP Form Iframe Found by Text!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             # Fallback to previous iframe or first non-main
#             non_main = [f for f in page.frames if f != page.main_frame]
#             if non_main:
#                 iframe = non_main[0]
#                 print("⚠️ Using fallback iframe for OTP")

#         if iframe:
#             print("🔍 Filling OTP...")
#             try:
#                 iframe.wait_for_selector('input', timeout=200000)
#                 time.sleep(3)
#             except:
#                 print("⚠️ Input wait timeout, trying anyway")

#             otp = get_latest_otp(max_attempts=35, delay=5)

#             if otp:
#                 try:
#                     # OTP input as per your HTML
#                     iframe.fill('input[name="otpValue"], input.input-field, input[type="password"][maxlength="6"]', otp)
#                     print(f"✅ OTP Filled: {otp}")
#                 except:
#                     try:
#                         iframe.locator('input').nth(0).fill(otp)
#                         print("✅ OTP Filled (nth 0)")
#                     except:
#                         print("❌ Could not fill OTP")

#                 time.sleep(2)

#                 # Click Submit
#                 try:
#                     iframe.click('button#submitBtn, button:has-text("SUBMIT")', timeout=200000)
#                     print("✅ OTP SUBMIT Clicked")
#                 except:
#                     try:
#                         iframe.locator('button').filter(has_text="SUBMIT").click(timeout=200000)
#                     except:
#                         iframe.evaluate("""() => {
#                             const btns = document.querySelectorAll('button');
#                             for (let b of btns) {
#                                 if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) {
#                                     b.click();
#                                     return;
#                                 }
#                             }
#                         }""")
#                         print("✅ OTP SUBMIT via JS")
#             else:
#                 print("❌ OTP not received from API")
#         else:
#             print("❌ OTP Iframe not found")

#         time.sleep(8)

#         print(f"✅ Run #{run_number} Completed!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow - Corporate + OTP Fixed ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")



# import time
# import random
# import string
# import json
# import os
# import requests
# import csv
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# TOTAL_RUNS = 5
# HEADLESS = False
# DETAILS_CSV = "details.csv"

# # Corporate Config
# CORPORATE_ID = "streakads"
# EMPLOYEE_ID = "CHANGE_ME_EMP_ID"
# API_EMPLOYEE_ID = "CHANGE_ME_EMP_ID"

# def load_gologin_tokens():
#     tokens = []
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             for line in f:
#                 token = line.strip()
#                 if len(token) > 50:
#                     tokens.append(token)
#     except:
#         pass
#     if tokens:
#         print(f"✅ {len(tokens)} GoLogin Token(s) Loaded")
#         return tokens
#     print("❌ config.txt mein GoLogin token(s) daal do!")
#     exit(1)

# GOLOGIN_TOKENS = load_gologin_tokens()

# def load_details():
#     details = []
#     try:
#         with open(DETAILS_CSV, 'r', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 details.append(row)
#         print(f"✅ Loaded {len(details)} records from {DETAILS_CSV}")
#         return details
#     except Exception as e:
#         print(f"❌ Could not load {DETAILS_CSV}: {e}")
#         exit(1)

# DETAILS_LIST = load_details()

# def get_random_detail():
#     if not DETAILS_LIST:
#         return None
#     return random.choice(DETAILS_LIST)

# def generate_email_from_name(first_name):
#     first = first_name.lower().strip()
#     num = random.randint(10, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
#     return f"{first}{num}@{random.choice(domains)}"

# def get_latest_otp(max_attempts=30, delay=4):
#     url = f"https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp"
#     print(f"🔍 Waiting for OTP from API...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=500)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Run #{data['run_number']}")

# # ================= SINGLE CYCLE =================
# def run_one_cycle(run_number):
#     print(f"\n🚀 === Run #{run_number} Starting ===")
#     gl = None
#     pw = None
#     browser = None
#     page = None
#     email = "test@example.com"
#     status = "failed"

#     # Get random details from CSV
#     detail = get_random_detail()
#     if not detail:
#         print("❌ No data in details.csv")
#         return

#     first_name = detail.get("First Name", "Rahul")
#     last_name = detail.get("Last Name", "Sharma")
#     zip_code = detail.get("Zip Code", "000000")
#     card_number = detail.get("Card Number", "0000000000000000")
#     card_expiry = detail.get("Card Expiry", "06/28")
#     card_cvc = detail.get("Card CVC", "164")
#     billing_name = detail.get("Billing Name", "john doe")

#     email = generate_email_from_name(first_name)

#     try:
#         # Try tokens one by one if previous fails
#         current_token = GOLOGIN_TOKENS[(run_number - 1) % len(GOLOGIN_TOKENS)]
#         gl = GoLogin({"token": current_token})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })

#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id} | Token: {current_token[:15]}...")

#         proxy_data = {
#             "mode": "socks5",
#             "host": "sg.proxy.geonode.io",
#             "port": 11000,
#             "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#             "password": "CHANGE_ME_PASSWORD"
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})

#         page.evaluate("""() => {
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#         }""")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=200000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', zip_code)
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', card_number)
#         page.fill('input#cardExpiry', card_expiry)
#         page.fill('input#cardCvc', card_cvc)
#         page.fill('input#billingName', billing_name)
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=200000)
#         time.sleep(random.uniform(10, 15))

#         # ================= CORPORATE FORM (ICICI BANK) =================
#         print("🏢 Waiting for ICICI Corporate Form...")
#         time.sleep(12)

#         try:
#             page.wait_for_load_state("networkidle", timeout=200000)
#         except:
#             pass

#         print("📋 All Frames Debug:")
#         for i, frame in enumerate(page.frames):
#             print(f"  [{i}] name='{frame.name}' | url='{frame.url[:150]}...'")

#         # Find the correct iframe
#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if (frame.get_by_text("Corporate ID").count() > 0 or
#                     frame.get_by_text("Employee ID").count() > 0):
#                     iframe = frame
#                     print(f"✅ Corporate Form Iframe Found by Text!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             for frame in page.frames:
#                 if frame == page.main_frame:
#                     continue
#                 name_lower = (frame.name or "").lower()
#                 url_lower = (frame.url or "").lower()
#                 if any(k in name_lower + url_lower for k in ["challenge", "3ds", "icici", "corporate", "employee"]):
#                     iframe = frame
#                     print(f"✅ Iframe Found by Keyword: {frame.name}")
#                     break

#         if iframe:
#             print("🔍 Filling Corporate Form...")
#             iframe.wait_for_selector('input', timeout=200000)
#             time.sleep(4)

#             try:
#                 iframe.fill('input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]', CORPORATE_ID)
#                 print(f"✅ Corporate ID Filled")
#             except:
#                 iframe.locator('input').nth(0).fill(CORPORATE_ID)
#                 print("✅ Corporate ID (Position 1)")

#             time.sleep(2)

#             try:
#                 iframe.fill('input[placeholder*="Employee"], input#employeeId, input[name*="employee"]', EMPLOYEE_ID)
#                 print(f"✅ Employee ID Filled")
#             except:
#                 iframe.locator('input').nth(1).fill(EMPLOYEE_ID)
#                 print("✅ Employee ID (Position 2)")

#             time.sleep(2)

#             try:
#                 iframe.click('button:has-text("SUBMIT"), button[type="submit"]', timeout=200000)
#                 print("✅ Corporate SUBMIT Clicked")
#             except:
#                 iframe.evaluate("""() => {
#                     const btns = document.querySelectorAll('button, a');
#                     for (let b of btns) {
#                         if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) {
#                             b.click();
#                             return;
#                         }
#                     }
#                 }""")
#                 print("✅ Corporate SUBMIT via JS")
#         else:
#             print("❌ Iframe not found - trying main page")
#             try:
#                 page.fill('input[placeholder*="Corporate"]', CORPORATE_ID)
#                 page.fill('input[placeholder*="Employee"]', EMPLOYEE_ID)
#                 page.click('button:has-text("SUBMIT")')
#             except:
#                 print("⚠️ Main page fallback failed")

#         # ================= OTP FORM (Same Iframe) =================
#         print("\n🔐 Waiting for OTP Form...")
#         time.sleep(20)

#         # Re-detect iframe for OTP screen
#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if frame.get_by_text("Enter OTP").count() > 0 or frame.get_by_text("Cardholder authentication").count() > 0:
#                     iframe = frame
#                     print("✅ OTP Form Iframe Found by Text!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             non_main = [f for f in page.frames if f != page.main_frame]
#             if non_main:
#                 iframe = non_main[0]
#                 print("⚠️ Using fallback iframe for OTP")

#         if iframe:
#             print("🔍 Filling OTP...")
#             try:
#                 iframe.wait_for_selector('input', timeout=200000)
#                 time.sleep(3)
#             except:
#                 print("⚠️ Input wait timeout, trying anyway")

#             otp = get_latest_otp(max_attempts=35, delay=5)

#             if otp:
#                 try:
#                     iframe.fill('input[name="otpValue"], input.input-field, input[type="password"][maxlength="6"]', otp)
#                     print(f"✅ OTP Filled: {otp}")
#                 except:
#                     try:
#                         iframe.locator('input').nth(0).fill(otp)
#                         print("✅ OTP Filled (nth 0)")
#                     except:
#                         print("❌ Could not fill OTP")

#                 time.sleep(2)

#                 try:
#                     iframe.click('button#submitBtn, button:has-text("SUBMIT")', timeout=200000)
#                     print("✅ OTP SUBMIT Clicked")
#                 except:
#                     try:
#                         iframe.locator('button').filter(has_text="SUBMIT").click(timeout=200000)
#                     except:
#                         iframe.evaluate("""() => {
#                             const btns = document.querySelectorAll('button');
#                             for (let b of btns) {
#                                 if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) {
#                                     b.click();
#                                     return;
#                                 }
#                             }
#                         }""")
#                         print("✅ OTP SUBMIT via JS")
#             else:
#                 print("❌ OTP not received from API")
#         else:
#             print("❌ OTP Iframe not found")

#         time.sleep(8)
#         print(f"✅ Run #{run_number} Completed!")
#         status = "success"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#     finally:
#         log_data = {
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status
#         }
#         save_log(log_data)

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================
# if __name__ == "__main__":
#     print("=== Magzter Full Flow - CSV + Multi Token + Name Email ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             time.sleep(random.uniform(25, 45))

#     print("\n🎉 All Runs Completed!")




# import time
# import random
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# try:
#     import gspread
# except ImportError:
#     print("❌ Install gspread: pip install gspread")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# HEADLESS = False

# GOOGLE_CREDENTIALS = {
#     "type": "service_account",
#     "project_id": "gmblinks",
#     "private_key_id": "CHANGE_ME_KEY_ID",
#     "private_key": "-----BEGIN PRIVATE KEY-----
CHANGE_ME_ROTATE_THIS_KEY
-----END PRIVATE KEY-----\n",
#     "client_email": "test@example.com",
#     "client_id": "0000000000",
#     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#     "token_uri": "CHANGE_ME_TOKEN",
#     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/marcadeo-tech%40gmblinks.iam.gserviceaccount.com",
#     "universe_domain": "googleapis.com"
# }

# SPREADSHEET_ID = "1usY7UmsiGCIHcDAJoBuHNJWtScSzNhMVhr6nqnpegUU"
# TASKS_SHEET = "Gologin_Test"

# # Expected columns in Tasks sheet (order must match sheet headers exactly)
# # Card_No | Month | CVV | Email | Password | Corp_ID | Emp_ID | Zip_Code | First_Name | Last_Name | Status | Name_Used | Proxy_IP | Duration_Sec | ErrorTimestamp

# COL_CARD_NO      = "0000000000000000"
# COL_MONTH        = "Month"
# COL_CVV          = "000"
# COL_EMAIL        = "test@example.com"
# COL_PASSWORD     = "CHANGE_ME_PASSWORD"
# COL_CORP_ID      = "Corp_ID"
# COL_EMP_ID       = "CHANGE_ME_EMP_ID"
# COL_ZIP_CODE     = "Zip_Code"
# COL_FIRST_NAME   = "John"
# COL_LAST_NAME    = "Doe"
# COL_STATUS       = "Status"
# COL_NAME_USED    = "Name_Used"
# COL_PROXY_IP     = "Proxy_IP"
# COL_DURATION_SEC = "Duration_Sec"
# COL_ERROR_TS     = "Error"

# # ================= GOOGLE SHEET HELPERS =================

# def get_sheet():
#     gc = gspread.service_account_from_dict(GOOGLE_CREDENTIALS)
#     sh = gc.open_by_key(SPREADSHEET_ID)
#     return sh.worksheet(TASKS_SHEET)

# def load_pending_rows():
#     """Load all rows from Tasks sheet where Status is empty or 'pending'."""
#     ws = get_sheet()
#     records = ws.get_all_records()
#     pending = []
#     for idx, row in enumerate(records, start=2):  # row 1 = header, data starts at 2
#         status = str(row.get(COL_STATUS, "")).strip().lower()
#         if status in ("", "pending"):
#             pending.append((idx, row))
#     print(f"✅ {len(pending)} pending rows loaded from '{TASKS_SHEET}'")
#     return pending

# def update_row_status(row_index, ws, headers, updates: dict):
#     """Write multiple cell updates to a specific row using column names."""
#     for col_name, value in updates.items():
#         try:
#             col_idx = headers.index(col_name) + 1  # gspread is 1-indexed
#             ws.update_cell(row_index, col_idx, value)
#         except ValueError:
#             print(f"⚠️ Column '{col_name}' not found in sheet headers — skipping")
#         except Exception as e:
#             print(f"⚠️ Could not update '{col_name}': {e}")

# # ================= GOLOGIN =================

# def load_gologin_tokens():
#     tokens = []
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             for line in f:
#                 token = line.strip()
#                 if len(token) > 50:
#                     tokens.append(token)
#     except:
#         pass
#     if tokens:
#         print(f"✅ {len(tokens)} GoLogin Token(s) Loaded")
#         return tokens
#     print("❌ config.txt mein GoLogin token(s) daal do!")
#     exit(1)

# GOLOGIN_TOKENS = load_gologin_tokens()

# # ================= OTP =================

# def get_latest_otp(emp_id, max_attempts=30, delay=4):
#     api_emp_id = emp_id.upper()
#     url = f"https://test.trackopia.in/api/employees/{api_emp_id}/latest-otp"
#     print(f"🔍 Waiting for OTP from API (emp: {api_emp_id})...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=500)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# # ================= LOGGING =================

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Row #{data['sheet_row']}")

# # ================= SINGLE CYCLE =================

# def run_one_cycle(run_number, sheet_row_index, row_data, ws, headers):
#     print(f"\n🚀 === Run #{run_number} | Sheet Row {sheet_row_index} ===")

#     # --- Read inputs from sheet row ---
#     card_number  = str(row_data.get(COL_CARD_NO, "")).strip()
#     card_expiry  = str(row_data.get(COL_MONTH, "")).strip()   # e.g. "06/28"
#     card_cvc     = str(row_data.get(COL_CVV, "")).strip()
#     email        = str(row_data.get(COL_EMAIL, "")).strip()
#     password     = str(row_data.get(COL_PASSWORD, "")).strip()
#     corp_id      = str(row_data.get(COL_CORP_ID, "")).strip()
#     emp_id       = str(row_data.get(COL_EMP_ID, "")).strip()
#     zip_code     = str(row_data.get(COL_ZIP_CODE, "")).strip()
#     first_name   = str(row_data.get(COL_FIRST_NAME, "")).strip()
#     last_name    = str(row_data.get(COL_LAST_NAME, "")).strip()

#     billing_name = f"{first_name} {last_name}".strip()

#     # Proxy config (static residential — update if needed)
#     proxy_host = "sg.proxy.geonode.io"
#     proxy_port = 11000
#     proxy_user = "geonode_xvmYN44Bvz-type-residential-country-in"
#     proxy_pass = "CHANGE_ME_SECRET"
#     proxy_ip_label = f"{proxy_host}:{proxy_port}"

#     status = "failed"
#     error_ts = ""
#     duration_sec = ""
#     start_time = time.time()

#     gl = None
#     pw = None
#     browser = None
#     page = None

#     try:
#         # Mark row as "running" immediately
#         update_row_status(sheet_row_index, ws, headers, {COL_STATUS: "running"})

#         current_token = GOLOGIN_TOKENS[(run_number - 1) % len(GOLOGIN_TOKENS)]
#         gl = GoLogin({"token": current_token})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })
#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": proxy_host,
#             "port": proxy_port,
#             "username": proxy_user,
#             "password": proxy_pass
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
#         page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); }")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=200000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', zip_code)
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', card_number)
#         page.fill('input#cardExpiry', card_expiry)
#         page.fill('input#cardCvc', card_cvc)
#         page.fill('input#billingName', billing_name)
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=2000000)
#         time.sleep(random.uniform(10, 15))

#         # ================= CORPORATE FORM =================
#         print("🏢 Waiting for Corporate Form...")
#         time.sleep(12)

#         try:
#             page.wait_for_load_state("networkidle", timeout=200000)
#         except:
#             pass

#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if (frame.get_by_text("Corporate ID").count() > 0 or
#                         frame.get_by_text("Employee ID").count() > 0):
#                     iframe = frame
#                     print("✅ Corporate Iframe Found by Text!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             for frame in page.frames:
#                 if frame == page.main_frame:
#                     continue
#                 name_lower = (frame.name or "").lower()
#                 url_lower = (frame.url or "").lower()
#                 if any(k in name_lower + url_lower for k in ["challenge", "3ds", "icici", "corporate", "employee"]):
#                     iframe = frame
#                     print(f"✅ Iframe Found by Keyword: {frame.name}")
#                     break

#         if iframe:
#             iframe.wait_for_selector('input', timeout=200000)
#             time.sleep(4)
#             try:
#                 iframe.fill('input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]', corp_id)
#                 print(f"✅ Corporate ID Filled: {corp_id}")
#             except:
#                 iframe.locator('input').nth(0).fill(corp_id)

#             time.sleep(2)

#             try:
#                 iframe.fill('input[placeholder*="Employee"], input#employeeId, input[name*="employee"]', emp_id)
#                 print(f"✅ Employee ID Filled: {emp_id}")
#             except:
#                 iframe.locator('input').nth(1).fill(emp_id)

#             time.sleep(2)

#             try:
#                 iframe.click('button:has-text("SUBMIT"), button[type="submit"]', timeout=200000)
#                 print("✅ Corporate SUBMIT Clicked")
#             except:
#                 iframe.evaluate("""() => {
#                     const btns = document.querySelectorAll('button, a');
#                     for (let b of btns) {
#                         if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
#                     }
#                 }""")
#         else:
#             print("❌ Corporate Iframe not found — trying main page")
#             try:
#                 page.fill('input[placeholder*="Corporate"]', corp_id)
#                 page.fill('input[placeholder*="Employee"]', emp_id)
#                 page.click('button:has-text("SUBMIT")')
#             except:
#                 print("⚠️ Main page fallback failed")

#         # ================= OTP FORM =================
#         print("\n🔐 Waiting for OTP Form...")
#         time.sleep(20)

#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if frame.get_by_text("Enter OTP").count() > 0 or frame.get_by_text("Cardholder authentication").count() > 0:
#                     iframe = frame
#                     print("✅ OTP Iframe Found!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             non_main = [f for f in page.frames if f != page.main_frame]
#             if non_main:
#                 iframe = non_main[0]
#                 print("⚠️ Using fallback iframe for OTP")

#         if iframe:
#             try:
#                 iframe.wait_for_selector('input', timeout=200000)
#                 time.sleep(3)
#             except:
#                 pass

#             otp = get_latest_otp(emp_id, max_attempts=35, delay=5)

#             if otp:
#                 try:
#                     iframe.fill('input[name="otpValue"], input.input-field, input[type="password"][maxlength="6"]', otp)
#                     print(f"✅ OTP Filled: {otp}")
#                 except:
#                     try:
#                         iframe.locator('input').nth(0).fill(otp)
#                     except:
#                         print("❌ Could not fill OTP")

#                 time.sleep(2)

#                 try:
#                     iframe.click('button#submitBtn, button:has-text("SUBMIT")', timeout=200000)
#                     print("✅ OTP SUBMIT Clicked")
#                 except:
#                     iframe.evaluate("""() => {
#                         const btns = document.querySelectorAll('button');
#                         for (let b of btns) {
#                             if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
#                         }
#                     }""")
#             else:
#                 print("❌ OTP not received from API")
#         else:
#             print("❌ OTP Iframe not found")

#         time.sleep(8)
#         print(f"✅ Run #{run_number} Completed!")
#         status = "complete"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#         error_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     finally:
#         duration_sec = round(time.time() - start_time, 1)

#         # Update sheet row with results
#         sheet_updates = {
#             COL_STATUS:       status,
#             COL_NAME_USED:    billing_name,
#             COL_PROXY_IP:     proxy_ip_label,
#             COL_DURATION_SEC: duration_sec,
#             COL_ERROR_TS:     error_ts,
#         }
#         try:
#             update_row_status(sheet_row_index, ws, headers, sheet_updates)
#             print(f"📊 Sheet Row {sheet_row_index} Updated → Status: {status} | Duration: {duration_sec}s")
#         except Exception as e:
#             print(f"❌ Sheet update failed: {e}")

#         save_log({
#             "sheet_row": sheet_row_index,
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status,
#             "duration_sec": duration_sec,
#             "proxy": proxy_ip_label,
#             "error_timestamp": error_ts,
#         })

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

# # ================= MAIN =================

# if __name__ == "__main__":
#     print("=== Magzter Full Flow — Google Sheet Tasks Mode ===\n")

#     # Load sheet + headers once
#     ws = get_sheet()
#     all_values = ws.get_all_values()
#     if not all_values:
#         print("❌ Sheet is empty!")
#         exit(1)
#     headers = all_values[0]  # first row = column names
#     print(f"📋 Sheet headers: {headers}")

#     # Load pending rows
#     pending = load_pending_rows()
#     if not pending:
#         print("✅ No pending rows found. All done!")
#         exit(0)

#     print(f"\n🚀 Processing {len(pending)} pending rows...\n")

#     for run_number, (row_index, row_data) in enumerate(pending, start=1):
#         run_one_cycle(run_number, row_index, row_data, ws, headers)
#         if run_number < len(pending):
#             wait = random.uniform(25, 45)
#             print(f"\n⏳ Waiting {wait:.0f}s before next run...")
#             time.sleep(wait)

#     print("\n🎉 All Pending Rows Processed!")





# import time
# import random
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# try:
#     import gspread
# except ImportError:
#     print("❌ Install gspread: pip install gspread")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# HEADLESS = False

# GOOGLE_CREDENTIALS = {
#     "type": "service_account",
#     "project_id": "gmblinks",
#     "private_key_id": "CHANGE_ME_KEY_ID",
#     "private_key": "-----BEGIN PRIVATE KEY-----
CHANGE_ME_ROTATE_THIS_KEY
-----END PRIVATE KEY-----\n",
#     "client_email": "test@example.com",
#     "client_id": "0000000000",
#     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#     "token_uri": "CHANGE_ME_TOKEN",
#     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/marcadeo-tech%40gmblinks.iam.gserviceaccount.com",
#     "universe_domain": "googleapis.com"
# }

# SPREADSHEET_ID = "1usY7UmsiGCIHcDAJoBuHNJWtScSzNhMVhr6nqnpegUU"
# TASKS_SHEET = "Gologin_Test"

# # Expected columns in Tasks sheet (order must match sheet headers exactly)
# # Card_No | Month | CVV | Email | Password | Corp_ID | Emp_ID | Zip_Code | First_Name | Last_Name | Status | Name_Used | Proxy_IP | Duration_Sec | ErrorTimestamp

# COL_CARD_NO      = "0000000000000000"
# COL_MONTH        = "Month"
# COL_CVV          = "000"
# COL_EMAIL        = "test@example.com"
# COL_PASSWORD     = "CHANGE_ME_PASSWORD"
# COL_CORP_ID      = "Corp_ID"
# COL_EMP_ID       = "CHANGE_ME_EMP_ID"
# COL_ZIP_CODE     = "Zip_Code"
# COL_FIRST_NAME   = "John"
# COL_LAST_NAME    = "Doe"
# COL_STATUS       = "Status"
# COL_NAME_USED    = "Name_Used"
# COL_PROXY_IP     = "Proxy_IP"
# COL_DURATION_SEC = "Duration_Sec"
# COL_ERROR_TS     = "Error"

# # ================= GOOGLE SHEET HELPERS =================

# def get_sheet():
#     gc = gspread.service_account_from_dict(GOOGLE_CREDENTIALS)
#     sh = gc.open_by_key(SPREADSHEET_ID)
#     return sh.worksheet(TASKS_SHEET)

# def load_pending_rows():
#     """Load all rows from Tasks sheet where Status is empty or 'pending'."""
#     ws = get_sheet()
#     records = ws.get_all_records()
#     pending = []
#     for idx, row in enumerate(records, start=2):  # row 1 = header, data starts at 2
#         status = str(row.get(COL_STATUS, "")).strip().lower()
#         if status in ("", "pending"):
#             pending.append((idx, row))
#     print(f"✅ {len(pending)} pending rows loaded from '{TASKS_SHEET}'")
#     return pending

# def update_row_status(row_index, ws, headers, updates: dict):
#     """Write multiple cell updates to a specific row using column names."""
#     for col_name, value in updates.items():
#         try:
#             col_idx = headers.index(col_name) + 1  # gspread is 1-indexed
#             ws.update_cell(row_index, col_idx, value)
#         except ValueError:
#             print(f"⚠️ Column '{col_name}' not found in sheet headers — skipping")
#         except Exception as e:
#             print(f"⚠️ Could not update '{col_name}': {e}")

# # ================= GOLOGIN =================

# def load_gologin_tokens():
#     tokens = []
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             for line in f:
#                 token = line.strip()
#                 if len(token) > 50:
#                     tokens.append(token)
#     except:
#         pass
#     if tokens:
#         print(f"✅ {len(tokens)} GoLogin Token(s) Loaded")
#         return tokens
#     print("❌ config.txt mein GoLogin token(s) daal do!")
#     exit(1)

# GOLOGIN_TOKENS = load_gologin_tokens()

# # ================= OTP =================

# def get_latest_otp(emp_id, max_attempts=30, delay=4):
#     api_emp_id = emp_id.upper()
#     url = f"https://test.trackopia.in/api/employees/{api_emp_id}/latest-otp"
#     print(f"🔍 Waiting for OTP from API (emp: {api_emp_id})...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=500)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# # ================= LOGGING =================

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Row #{data['sheet_row']}")

# # ================= SINGLE CYCLE =================

# def run_one_cycle(run_number, sheet_row_index, row_data, ws, headers):
#     print(f"\n🚀 === Run #{run_number} | Sheet Row {sheet_row_index} ===")

#     # --- Read inputs from sheet row ---
#     card_number  = str(row_data.get(COL_CARD_NO, "")).strip()
#     card_expiry  = str(row_data.get(COL_MONTH, "")).strip()   # e.g. "06/28"
#     card_cvc     = str(row_data.get(COL_CVV, "")).strip()
#     email        = str(row_data.get(COL_EMAIL, "")).strip()
#     password     = str(row_data.get(COL_PASSWORD, "")).strip()
#     corp_id      = str(row_data.get(COL_CORP_ID, "")).strip()
#     emp_id       = str(row_data.get(COL_EMP_ID, "")).strip()
#     zip_code     = str(row_data.get(COL_ZIP_CODE, "")).strip()
#     first_name   = str(row_data.get(COL_FIRST_NAME, "")).strip()
#     last_name    = str(row_data.get(COL_LAST_NAME, "")).strip()

#     billing_name = f"{first_name} {last_name}".strip()

#     # Proxy config (static residential — update if needed)
#     proxy_host = "sg.proxy.geonode.io"
#     proxy_port = 11000
#     proxy_user = "geonode_xvmYN44Bvz-type-residential-country-in"
#     proxy_pass = "CHANGE_ME_SECRET"
#     proxy_ip_label = f"{proxy_host}:{proxy_port}"

#     status = "failed"
#     error_ts = ""
#     duration_sec = ""
#     start_time = time.time()

#     gl = None
#     pw = None
#     browser = None
#     page = None
#     profile_id = None

#     try:
#         # Mark row as "running" immediately
#         update_row_status(sheet_row_index, ws, headers, {COL_STATUS: "running"})

#         current_token = GOLOGIN_TOKENS[(run_number - 1) % len(GOLOGIN_TOKENS)]
#         gl = GoLogin({"token": current_token})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })
#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": proxy_host,
#             "port": proxy_port,
#             "username": proxy_user,
#             "password": proxy_pass
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
#         page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); }")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=200000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', zip_code)
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', card_number)
#         page.fill('input#cardExpiry', card_expiry)
#         page.fill('input#cardCvc', card_cvc)
#         page.fill('input#billingName', billing_name)
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=2000000)
#         time.sleep(random.uniform(10, 15))

#         # ================= CORPORATE FORM =================
#         print("🏢 Waiting for Corporate Form...")
#         time.sleep(12)

#         try:
#             page.wait_for_load_state("networkidle", timeout=200000)
#         except:
#             pass

#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if (frame.get_by_text("Corporate ID").count() > 0 or
#                         frame.get_by_text("Employee ID").count() > 0):
#                     iframe = frame
#                     print("✅ Corporate Iframe Found by Text!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             for frame in page.frames:
#                 if frame == page.main_frame:
#                     continue
#                 name_lower = (frame.name or "").lower()
#                 url_lower = (frame.url or "").lower()
#                 if any(k in name_lower + url_lower for k in ["challenge", "3ds", "icici", "corporate", "employee"]):
#                     iframe = frame
#                     print(f"✅ Iframe Found by Keyword: {frame.name}")
#                     break

#         if iframe:
#             iframe.wait_for_selector('input', timeout=200000)
#             time.sleep(4)
#             try:
#                 iframe.fill('input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]', corp_id)
#                 print(f"✅ Corporate ID Filled: {corp_id}")
#             except:
#                 iframe.locator('input').nth(0).fill(corp_id)

#             time.sleep(2)

#             try:
#                 iframe.fill('input[placeholder*="Employee"], input#employeeId, input[name*="employee"]', emp_id)
#                 print(f"✅ Employee ID Filled: {emp_id}")
#             except:
#                 iframe.locator('input').nth(1).fill(emp_id)

#             time.sleep(2)

#             try:
#                 iframe.click('button:has-text("SUBMIT"), button[type="submit"]', timeout=200000)
#                 print("✅ Corporate SUBMIT Clicked")
#             except:
#                 iframe.evaluate("""() => {
#                     const btns = document.querySelectorAll('button, a');
#                     for (let b of btns) {
#                         if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
#                     }
#                 }""")
#         else:
#             print("❌ Corporate Iframe not found — trying main page")
#             try:
#                 page.fill('input[placeholder*="Corporate"]', corp_id)
#                 page.fill('input[placeholder*="Employee"]', emp_id)
#                 page.click('button:has-text("SUBMIT")')
#             except:
#                 print("⚠️ Main page fallback failed")

#         # ================= OTP FORM =================
#         print("\n🔐 Waiting for OTP Form...")
#         time.sleep(20)

#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if frame.get_by_text("Enter OTP").count() > 0 or frame.get_by_text("Cardholder authentication").count() > 0:
#                     iframe = frame
#                     print("✅ OTP Iframe Found!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             non_main = [f for f in page.frames if f != page.main_frame]
#             if non_main:
#                 iframe = non_main[0]
#                 print("⚠️ Using fallback iframe for OTP")

#         if iframe:
#             try:
#                 iframe.wait_for_selector('input', timeout=200000)
#                 time.sleep(3)
#             except:
#                 pass

#             otp = get_latest_otp(emp_id, max_attempts=35, delay=5)

#             if otp:
#                 try:
#                     iframe.fill('input[name="otpValue"], input.input-field, input[type="password"][maxlength="6"]', otp)
#                     print(f"✅ OTP Filled: {otp}")
#                 except:
#                     try:
#                         iframe.locator('input').nth(0).fill(otp)
#                     except:
#                         print("❌ Could not fill OTP")

#                 time.sleep(2)

#                 try:
#                     iframe.click('button#submitBtn, button:has-text("SUBMIT")', timeout=200000)
#                     print("✅ OTP SUBMIT Clicked")
#                 except:
#                     iframe.evaluate("""() => {
#                         const btns = document.querySelectorAll('button');
#                         for (let b of btns) {
#                             if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
#                         }
#                     }""")
#             else:
#                 print("❌ OTP not received from API")
#         else:
#             print("❌ OTP Iframe not found")

#         time.sleep(8)
#         print(f"✅ Run #{run_number} Completed!")
#         status = "complete"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#         error_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     finally:
#         duration_sec = round(time.time() - start_time, 1)

#         # Update sheet row with results
#         sheet_updates = {
#             COL_STATUS:       status,
#             COL_NAME_USED:    billing_name,
#             COL_PROXY_IP:     proxy_ip_label,
#             COL_DURATION_SEC: duration_sec,
#             COL_ERROR_TS:     error_ts,
#         }
#         try:
#             update_row_status(sheet_row_index, ws, headers, sheet_updates)
#             print(f"📊 Sheet Row {sheet_row_index} Updated → Status: {status} | Duration: {duration_sec}s")
#         except Exception as e:
#             print(f"❌ Sheet update failed: {e}")

#         save_log({
#             "sheet_row": sheet_row_index,
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status,
#             "duration_sec": duration_sec,
#             "proxy": proxy_ip_label,
#             "error_timestamp": error_ts,
#         })

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

#         # === UPDATED: Delete profile in ALL cases (success or failed) ===
#         if gl and profile_id:
#             try:
#                 gl.delete(profile_id)
#                 print(f"🗑️ Profile deleted: {profile_id} (Status: {status})")
#             except Exception as del_e:
#                 print(f"⚠️ Failed to delete profile {profile_id}: {del_e}")

# # ================= MAIN =================

# if __name__ == "__main__":
#     print("=== Magzter Full Flow — Google Sheet Tasks Mode ===\n")

#     # Load sheet + headers once
#     ws = get_sheet()
#     all_values = ws.get_all_values()
#     if not all_values:
#         print("❌ Sheet is empty!")
#         exit(1)
#     headers = all_values[0]  # first row = column names
#     print(f"📋 Sheet headers: {headers}")

#     # Load pending rows
#     pending = load_pending_rows()
#     if not pending:
#         print("✅ No pending rows found. All done!")
#         exit(0)

#     print(f"\n🚀 Processing {len(pending)} pending rows...\n")

#     for run_number, (row_index, row_data) in enumerate(pending, start=1):
#         run_one_cycle(run_number, row_index, row_data, ws, headers)
#         if run_number < len(pending):
#             wait = random.uniform(25, 45)
#             print(f"\n⏳ Waiting {wait:.0f}s before next run...")
#             time.sleep(wait)

#     print("\n🎉 All Pending Rows Processed!")




# import time
# import random
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# try:
#     import gspread
# except ImportError:
#     print("❌ Install gspread: pip install gspread")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# HEADLESS = False

# GOOGLE_CREDENTIALS = {
#     "type": "service_account",
#     "project_id": "gmblinks",
#     "private_key_id": "CHANGE_ME_KEY_ID",
#     "private_key": "-----BEGIN PRIVATE KEY-----
CHANGE_ME_ROTATE_THIS_KEY
-----END PRIVATE KEY-----\n",
#     "client_email": "test@example.com",
#     "client_id": "0000000000",
#     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#     "token_uri": "CHANGE_ME_TOKEN",
#     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/marcadeo-tech%40gmblinks.iam.gserviceaccount.com",
#     "universe_domain": "googleapis.com"
# }

# SPREADSHEET_ID = "1usY7UmsiGCIHcDAJoBuHNJWtScSzNhMVhr6nqnpegUU"
# TASKS_SHEET = "Gologin_Test"

# # Expected columns in Tasks sheet (order must match sheet headers exactly)
# # Card_No | Month | CVV | Email | Password | Corp_ID | Emp_ID | Zip_Code | First_Name | Last_Name | Status | Name_Used | Proxy_IP | Duration_Sec | ErrorTimestamp

# COL_CARD_NO      = "0000000000000000"
# COL_MONTH        = "Month"
# COL_CVV          = "000"
# COL_EMAIL        = "test@example.com"
# COL_PASSWORD     = "CHANGE_ME_PASSWORD"
# COL_CORP_ID      = "Corp_ID"
# COL_EMP_ID       = "CHANGE_ME_EMP_ID"
# COL_ZIP_CODE     = "Zip_Code"
# COL_FIRST_NAME   = "John"
# COL_LAST_NAME    = "Doe"
# COL_STATUS       = "Status"
# COL_NAME_USED    = "Name_Used"
# COL_PROXY_IP     = "Proxy_IP"
# COL_DURATION_SEC = "Duration_Sec"
# COL_ERROR_TS     = "Error"

# # ================= GOOGLE SHEET HELPERS =================

# def get_sheet():
#     gc = gspread.service_account_from_dict(GOOGLE_CREDENTIALS)
#     sh = gc.open_by_key(SPREADSHEET_ID)
#     return sh.worksheet(TASKS_SHEET)

# def load_pending_rows():
#     """Load all rows from Tasks sheet where Status is empty or 'pending'."""
#     ws = get_sheet()
#     records = ws.get_all_records()
#     pending = []
#     for idx, row in enumerate(records, start=2):  # row 1 = header, data starts at 2
#         status = str(row.get(COL_STATUS, "")).strip().lower()
#         if status in ("", "pending"):
#             pending.append((idx, row))
#     print(f"✅ {len(pending)} pending rows loaded from '{TASKS_SHEET}'")
#     return pending

# def update_row_status(row_index, ws, headers, updates: dict):
#     """Write multiple cell updates to a specific row using column names."""
#     for col_name, value in updates.items():
#         try:
#             col_idx = headers.index(col_name) + 1  # gspread is 1-indexed
#             ws.update_cell(row_index, col_idx, value)
#         except ValueError:
#             print(f"⚠️ Column '{col_name}' not found in sheet headers — skipping")
#         except Exception as e:
#             print(f"⚠️ Could not update '{col_name}': {e}")

# # ================= GOLOGIN =================

# def load_gologin_tokens():
#     tokens = []
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             for line in f:
#                 token = line.strip()
#                 if len(token) > 50:
#                     tokens.append(token)
#     except:
#         pass
#     if tokens:
#         print(f"✅ {len(tokens)} GoLogin Token(s) Loaded")
#         return tokens
#     print("❌ config.txt mein GoLogin token(s) daal do!")
#     exit(1)

# GOLOGIN_TOKENS = load_gologin_tokens()

# # ================= OTP =================

# def get_latest_otp(emp_id, max_attempts=30, delay=4):
#     api_emp_id = emp_id.upper()
#     url = f"https://test.trackopia.in/api/employees/{api_emp_id}/latest-otp"
#     print(f"🔍 Waiting for OTP from API (emp: {api_emp_id})...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=500)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# # ================= LOGGING =================

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Row #{data['sheet_row']}")

# # ================= SINGLE CYCLE =================

# def run_one_cycle(run_number, sheet_row_index, row_data, ws, headers):
#     print(f"\n🚀 === Run #{run_number} | Sheet Row {sheet_row_index} ===")

#     # --- Read inputs from sheet row ---
#     card_number  = str(row_data.get(COL_CARD_NO, "")).strip()
#     card_expiry  = str(row_data.get(COL_MONTH, "")).strip()   # e.g. "06/28"
#     card_cvc     = str(row_data.get(COL_CVV, "")).strip()
#     email        = str(row_data.get(COL_EMAIL, "")).strip()
#     password     = str(row_data.get(COL_PASSWORD, "")).strip()
#     corp_id      = str(row_data.get(COL_CORP_ID, "")).strip()
#     emp_id       = str(row_data.get(COL_EMP_ID, "")).strip()
#     zip_code     = str(row_data.get(COL_ZIP_CODE, "")).strip()
#     first_name   = str(row_data.get(COL_FIRST_NAME, "")).strip()
#     last_name    = str(row_data.get(COL_LAST_NAME, "")).strip()

#     billing_name = f"{first_name} {last_name}".strip()

#     # Proxy config (static residential — update if needed)
#     proxy_host = "sg.proxy.geonode.io"
#     proxy_port = 11000
#     proxy_user = "geonode_xvmYN44Bvz-type-residential-country-in"
#     proxy_pass = "CHANGE_ME_SECRET"
#     proxy_ip_label = f"{proxy_host}:{proxy_port}"

#     status = "failed"
#     error_ts = ""
#     duration_sec = ""
#     start_time = time.time()

#     gl = None
#     pw = None
#     browser = None
#     page = None
#     profile_id = None

#     try:
#         # Mark row as "running" immediately
#         update_row_status(sheet_row_index, ws, headers, {COL_STATUS: "running"})

#         current_token = GOLOGIN_TOKENS[(run_number - 1) % len(GOLOGIN_TOKENS)]
#         gl = GoLogin({"token": current_token})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })
#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": proxy_host,
#             "port": proxy_port,
#             "username": proxy_user,
#             "password": proxy_pass
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
#         page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); }")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=200000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=200000)
#         time.sleep(random.uniform(5, 9))

#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=200000)
#         time.sleep(random.uniform(6, 10))

#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         page.fill('input[placeholder*="Zip Code"]', zip_code)
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=200000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', card_number)
#         page.fill('input#cardExpiry', card_expiry)
#         page.fill('input#cardCvc', card_cvc)
#         page.fill('input#billingName', billing_name)
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=2000000)
#         time.sleep(random.uniform(10, 15))

#         # ================= CORPORATE FORM =================
#         print("🏢 Waiting for Corporate Form...")
#         time.sleep(12)

#         try:
#             page.wait_for_load_state("networkidle", timeout=200000)
#         except:
#             pass

#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if (frame.get_by_text("Corporate ID").count() > 0 or
#                         frame.get_by_text("Employee ID").count() > 0):
#                     iframe = frame
#                     print("✅ Corporate Iframe Found by Text!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             for frame in page.frames:
#                 if frame == page.main_frame:
#                     continue
#                 name_lower = (frame.name or "").lower()
#                 url_lower = (frame.url or "").lower()
#                 if any(k in name_lower + url_lower for k in ["challenge", "3ds", "icici", "corporate", "employee"]):
#                     iframe = frame
#                     print(f"✅ Iframe Found by Keyword: {frame.name}")
#                     break

#         if iframe:
#             iframe.wait_for_selector('input', timeout=200000)
#             time.sleep(4)
#             try:
#                 iframe.fill('input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]', corp_id)
#                 print(f"✅ Corporate ID Filled: {corp_id}")
#             except:
#                 iframe.locator('input').nth(0).fill(corp_id)

#             time.sleep(2)

#             try:
#                 iframe.fill('input[placeholder*="Employee"], input#employeeId, input[name*="employee"]', emp_id)
#                 print(f"✅ Employee ID Filled: {emp_id}")
#             except:
#                 iframe.locator('input').nth(1).fill(emp_id)

#             time.sleep(2)

#             try:
#                 iframe.click('button:has-text("SUBMIT"), button[type="submit"]', timeout=200000)
#                 print("✅ Corporate SUBMIT Clicked")
#             except:
#                 iframe.evaluate("""() => {
#                     const btns = document.querySelectorAll('button, a');
#                     for (let b of btns) {
#                         if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
#                     }
#                 }""")
#         else:
#             print("❌ Corporate Iframe not found — trying main page")
#             try:
#                 page.fill('input[placeholder*="Corporate"]', corp_id)
#                 page.fill('input[placeholder*="Employee"]', emp_id)
#                 page.click('button:has-text("SUBMIT")')
#             except:
#                 print("⚠️ Main page fallback failed")

#         # ================= OTP FORM =================
#         print("\n🔐 Waiting for OTP Form...")
#         time.sleep(20)

#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if frame.get_by_text("Enter OTP").count() > 0 or frame.get_by_text("Cardholder authentication").count() > 0:
#                     iframe = frame
#                     print("✅ OTP Iframe Found!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             non_main = [f for f in page.frames if f != page.main_frame]
#             if non_main:
#                 iframe = non_main[0]
#                 print("⚠️ Using fallback iframe for OTP")

#         if iframe:
#             try:
#                 iframe.wait_for_selector('input', timeout=200000)
#                 time.sleep(3)
#             except:
#                 pass

#             otp = get_latest_otp(emp_id, max_attempts=35, delay=5)

#             if otp:
#                 try:
#                     iframe.fill('input[name="otpValue"], input.input-field, input[type="password"][maxlength="6"]', otp)
#                     print(f"✅ OTP Filled: {otp}")
#                 except:
#                     try:
#                         iframe.locator('input').nth(0).fill(otp)
#                     except:
#                         print("❌ Could not fill OTP")

#                 time.sleep(2)

#                 try:
#                     iframe.click('button#submitBtn, button:has-text("SUBMIT")', timeout=200000)
#                     print("✅ OTP SUBMIT Clicked")
#                 except:
#                     iframe.evaluate("""() => {
#                         const btns = document.querySelectorAll('button');
#                         for (let b of btns) {
#                             if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
#                         }
#                     }""")
#             else:
#                 print("❌ OTP not received from API")
#         else:
#             print("❌ OTP Iframe not found")

#         time.sleep(8)
#         print(f"✅ Run #{run_number} Completed!")
#         status = "complete"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#         error_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     finally:
#         duration_sec = round(time.time() - start_time, 1)

#         # Update sheet row with results
#         sheet_updates = {
#             COL_STATUS:       status,
#             COL_NAME_USED:    billing_name,
#             COL_PROXY_IP:     proxy_ip_label,
#             COL_DURATION_SEC: duration_sec,
#             COL_ERROR_TS:     error_ts,
#         }
#         try:
#             update_row_status(sheet_row_index, ws, headers, sheet_updates)
#             print(f"📊 Sheet Row {sheet_row_index} Updated → Status: {status} | Duration: {duration_sec}s")
#         except Exception as e:
#             print(f"❌ Sheet update failed: {e}")

#         save_log({
#             "sheet_row": sheet_row_index,
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status,
#             "duration_sec": duration_sec,
#             "proxy": proxy_ip_label,
#             "error_timestamp": error_ts,
#         })

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

#         # === UPDATED: Delete profile in ALL cases (success or failed) ===
#         if gl and profile_id:
#             try:
#                 gl.delete(profile_id)
#                 print(f"🗑️ Profile deleted: {profile_id} (Status: {status})")
#             except Exception as del_e:
#                 print(f"⚠️ Failed to delete profile {profile_id}: {del_e}")

# # ================= MAIN =================

# if __name__ == "__main__":
#     print("=== Magzter Full Flow — Google Sheet Tasks Mode ===\n")

#     # Load sheet + headers once
#     ws = get_sheet()
#     all_values = ws.get_all_values()
#     if not all_values:
#         print("❌ Sheet is empty!")
#         exit(1)
#     headers = all_values[0]  # first row = column names
#     print(f"📋 Sheet headers: {headers}")

#     # Load pending rows
#     pending = load_pending_rows()
#     if not pending:
#         print("✅ No pending rows found. All done!")
#         exit(0)

#     print(f"\n🚀 Processing {len(pending)} pending rows...\n")

#     for run_number, (row_index, row_data) in enumerate(pending, start=1):
#         run_one_cycle(run_number, row_index, row_data, ws, headers)
#         if run_number < len(pending):
#             wait = random.uniform(25, 45)
#             print(f"\n⏳ Waiting {wait:.0f}s before next run...")
#             time.sleep(wait)

#     print("\n🎉 All Pending Rows Processed!")








# import time
# import random
# import json
# import os
# import requests
# from datetime import datetime
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     exit(1)

# try:
#     import gspread
# except ImportError:
#     print("❌ Install gspread: pip install gspread")
#     exit(1)

# # ================= CONFIG =================
# LOG_FILE = "magzter_logs.json"
# HEADLESS = False

# GOOGLE_CREDENTIALS = {
#     "type": "service_account",
#     "project_id": "gmblinks",
#     "private_key_id": "CHANGE_ME_KEY_ID",
#     "private_key": "-----BEGIN PRIVATE KEY-----
CHANGE_ME_ROTATE_THIS_KEY
-----END PRIVATE KEY-----\n",
#     "client_email": "test@example.com",
#     "client_id": "0000000000",
#     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#     "token_uri": "CHANGE_ME_TOKEN",
#     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/marcadeo-tech%40gmblinks.iam.gserviceaccount.com",
#     "universe_domain": "googleapis.com"
# }

# SPREADSHEET_ID = "1usY7UmsiGCIHcDAJoBuHNJWtScSzNhMVhr6nqnpegUU"
# TASKS_SHEET = "Gologin_Test"

# # Expected columns in Tasks sheet (order must match sheet headers exactly)
# # Card_No | Month | CVV | Email | Password | Corp_ID | Emp_ID | Zip_Code | First_Name | Last_Name | Status | Name_Used | Proxy_IP | Duration_Sec | ErrorTimestamp

# COL_CARD_NO      = "0000000000000000"
# COL_MONTH        = "Month"
# COL_CVV          = "000"
# COL_EMAIL        = "test@example.com"
# COL_PASSWORD     = "CHANGE_ME_PASSWORD"
# COL_CORP_ID      = "Corp_ID"
# COL_EMP_ID       = "CHANGE_ME_EMP_ID"
# COL_ZIP_CODE     = "Zip_Code"
# COL_FIRST_NAME   = "John"
# COL_LAST_NAME    = "Doe"
# COL_STATUS       = "Status"
# COL_NAME_USED    = "Name_Used"
# COL_PROXY_IP     = "Proxy_IP"
# COL_DURATION_SEC = "Duration_Sec"
# COL_ERROR_TS     = "Error"

# # ================= GOOGLE SHEET HELPERS =================

# def get_sheet():
#     gc = gspread.service_account_from_dict(GOOGLE_CREDENTIALS)
#     sh = gc.open_by_key(SPREADSHEET_ID)
#     return sh.worksheet(TASKS_SHEET)

# def load_pending_rows():
#     """Load all rows from Tasks sheet where Status is empty or 'pending'."""
#     ws = get_sheet()
#     records = ws.get_all_records()
#     pending = []
#     for idx, row in enumerate(records, start=2):  # row 1 = header, data starts at 2
#         status = str(row.get(COL_STATUS, "")).strip().lower()
#         if status in ("", "pending"):
#             pending.append((idx, row))
#     print(f"✅ {len(pending)} pending rows loaded from '{TASKS_SHEET}'")
#     return pending

# def update_row_status(row_index, ws, headers, updates: dict):
#     """Write multiple cell updates to a specific row using column names."""
#     for col_name, value in updates.items():
#         try:
#             col_idx = headers.index(col_name) + 1  # gspread is 1-indexed
#             ws.update_cell(row_index, col_idx, value)
#         except ValueError:
#             print(f"⚠️ Column '{col_name}' not found in sheet headers — skipping")
#         except Exception as e:
#             print(f"⚠️ Could not update '{col_name}': {e}")

# # ================= GOLOGIN =================

# def load_gologin_tokens():
#     tokens = []
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             for line in f:
#                 token = line.strip()
#                 if len(token) > 50:
#                     tokens.append(token)
#     except:
#         pass
#     if tokens:
#         print(f"✅ {len(tokens)} GoLogin Token(s) Loaded")
#         return tokens
#     print("❌ config.txt mein GoLogin token(s) daal do!")
#     exit(1)

# GOLOGIN_TOKENS = load_gologin_tokens()

# # ================= OTP =================

# def get_latest_otp(emp_id, max_attempts=30, delay=4):
#     api_emp_id = emp_id.upper()
#     url = f"https://test.trackopia.in/api/employees/{api_emp_id}/latest-otp"
#     print(f"🔍 Waiting for OTP from API (emp: {api_emp_id})...")
#     for attempt in range(1, max_attempts + 1):
#         try:
#             response = requests.get(url, timeout=500)
#             if response.status_code == 200:
#                 data = response.json()
#                 otp = data.get("otp")
#                 if otp and len(str(otp)) == 6:
#                     print(f"✅ OTP Received: {otp}")
#                     return str(otp)
#             print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
#         except Exception as e:
#             print(f"⚠️ API Error: {e}")
#         time.sleep(delay)
#     print("❌ Could not fetch OTP")
#     return None

# # ================= LOGGING =================

# def save_log(data):
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     logs.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)
#     print(f"📝 Log Saved | Row #{data['sheet_row']}")

# # ================= SINGLE CYCLE =================

# def run_one_cycle(run_number, sheet_row_index, row_data, ws, headers):
#     print(f"\n🚀 === Run #{run_number} | Sheet Row {sheet_row_index} ===")

#     # --- Read inputs from sheet row ---
#     card_number  = str(row_data.get(COL_CARD_NO, "")).strip()
#     card_expiry  = str(row_data.get(COL_MONTH, "")).strip()   # e.g. "06/28"
#     card_cvc     = str(row_data.get(COL_CVV, "")).strip()
#     email        = str(row_data.get(COL_EMAIL, "")).strip()
#     password     = str(row_data.get(COL_PASSWORD, "")).strip()
#     corp_id      = str(row_data.get(COL_CORP_ID, "")).strip()
#     emp_id       = str(row_data.get(COL_EMP_ID, "")).strip()
#     zip_code     = str(row_data.get(COL_ZIP_CODE, "")).strip()
#     first_name   = str(row_data.get(COL_FIRST_NAME, "")).strip()
#     last_name    = str(row_data.get(COL_LAST_NAME, "")).strip()

#     billing_name = f"{first_name} {last_name}".strip()

#     # Proxy config (static residential — update if needed)
#     proxy_host = "sg.proxy.geonode.io"
#     proxy_port = 11000
#     proxy_user = "geonode_xvmYN44Bvz-type-residential-country-in"
#     proxy_pass = "CHANGE_ME_SECRET"
#     proxy_ip_label = f"{proxy_host}:{proxy_port}"

#     status = "failed"
#     error_ts = ""
#     duration_sec = ""
#     start_time = time.time()

#     gl = None
#     pw = None
#     browser = None
#     page = None
#     profile_id = None

#     try:
#         # Mark row as "running" immediately
#         update_row_status(sheet_row_index, ws, headers, {COL_STATUS: "running"})

#         current_token = GOLOGIN_TOKENS[(run_number - 1) % len(GOLOGIN_TOKENS)]
#         gl = GoLogin({"token": current_token})

#         profile = gl.createProfileRandomFingerprint({
#             "name": f"magzter-{run_number}",
#             "os": "win",
#             "timezone": "Asia/Kolkata",
#             "language": "en-US",
#             "languages": ["en-US", "en"]
#         })
#         profile_id = profile['id']
#         print(f"✅ Profile Created: {profile_id}")

#         proxy_data = {
#             "mode": "socks5",
#             "host": proxy_host,
#             "port": proxy_port,
#             "username": proxy_user,
#             "password": proxy_pass
#         }
#         gl.changeProfileProxy(profile_id, proxy_data)
#         print("✅ Proxy Configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ Browser Started: {debugger_address}")

#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()

#         context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
#         page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); }")

#         # ================= FULL FLOW =================
#         page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=100000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(5, 8))

#         for _ in range(3):
#             page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
#             time.sleep(random.uniform(0.8, 1.5))

#         page.click('button:has-text("Claim Now")', timeout=100000)
#         time.sleep(random.uniform(5, 9))

#         print(f"📧 Email: {email}")
#         page.fill('input[type="email"]', email)
#         time.sleep(random.uniform(2, 4))
#         page.click('button:has-text("Continue")', timeout=100000)
#         time.sleep(random.uniform(6, 10))

#         page.fill('input[placeholder*="First Name"]', first_name)
#         page.fill('input[placeholder*="Last Name"]', last_name)
#         # Zip code field removed from website - skipping
#         # page.fill('input[placeholder*="Zip Code"]', zip_code)
#         time.sleep(random.uniform(3, 5))

#         page.click('button#submitBtn, button.svelte-xdpg18', timeout=100000)
#         time.sleep(random.uniform(7, 12))

#         # Payment Details
#         print("💳 Filling Card Details...")
#         page.fill('input#cardNumber', card_number)
#         page.fill('input#cardExpiry', card_expiry)
#         page.fill('input#cardCvc', card_cvc)
#         page.fill('input#billingName', billing_name)
#         time.sleep(random.uniform(4, 7))

#         print("💳 Submitting Card...")
#         page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=100000)
#         time.sleep(random.uniform(10, 15))

#         # ================= CORPORATE FORM =================
#         print("🏢 Waiting for Corporate Form...")
#         time.sleep(12)

#         try:
#             page.wait_for_load_state("networkidle", timeout=100000)
#         except:
#             pass

#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if (frame.get_by_text("Corporate ID").count() > 0 or
#                         frame.get_by_text("Employee ID").count() > 0):
#                     iframe = frame
#                     print("✅ Corporate Iframe Found by Text!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             for frame in page.frames:
#                 if frame == page.main_frame:
#                     continue
#                 name_lower = (frame.name or "").lower()
#                 url_lower = (frame.url or "").lower()
#                 if any(k in name_lower + url_lower for k in ["challenge", "3ds", "icici", "corporate", "employee"]):
#                     iframe = frame
#                     print(f"✅ Iframe Found by Keyword: {frame.name}")
#                     break

#         if iframe:
#             iframe.wait_for_selector('input', timeout=100000)
#             time.sleep(4)
#             try:
#                 iframe.fill('input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]', corp_id)
#                 print(f"✅ Corporate ID Filled: {corp_id}")
#             except:
#                 iframe.locator('input').nth(0).fill(corp_id)

#             time.sleep(2)

#             try:
#                 iframe.fill('input[placeholder*="Employee"], input#employeeId, input[name*="employee"]', emp_id)
#                 print(f"✅ Employee ID Filled: {emp_id}")
#             except:
#                 iframe.locator('input').nth(1).fill(emp_id)

#             time.sleep(2)

#             try:
#                 iframe.click('button:has-text("SUBMIT"), button[type="submit"]', timeout=100000)
#                 print("✅ Corporate SUBMIT Clicked")
#             except:
#                 iframe.evaluate("""() => {
#                     const btns = document.querySelectorAll('button, a');
#                     for (let b of btns) {
#                         if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
#                     }
#                 }""")
#         else:
#             print("❌ Corporate Iframe not found — trying main page")
#             try:
#                 page.fill('input[placeholder*="Corporate"]', corp_id)
#                 page.fill('input[placeholder*="Employee"]', emp_id)
#                 page.click('button:has-text("SUBMIT")')
#             except:
#                 print("⚠️ Main page fallback failed")

#         # ================= OTP FORM =================
#         print("\n🔐 Waiting for OTP Form...")
#         time.sleep(20)

#         iframe = None
#         for frame in page.frames:
#             if frame == page.main_frame:
#                 continue
#             try:
#                 if frame.get_by_text("Enter OTP").count() > 0 or frame.get_by_text("Cardholder authentication").count() > 0:
#                     iframe = frame
#                     print("✅ OTP Iframe Found!")
#                     break
#             except:
#                 continue

#         if not iframe:
#             non_main = [f for f in page.frames if f != page.main_frame]
#             if non_main:
#                 iframe = non_main[0]
#                 print("⚠️ Using fallback iframe for OTP")

#         if iframe:
#             try:
#                 iframe.wait_for_selector('input', timeout=100000)
#                 time.sleep(3)
#             except:
#                 pass

#             otp = get_latest_otp(emp_id, max_attempts=35, delay=5)

#             if otp:
#                 try:
#                     iframe.fill('input[name="otpValue"], input.input-field, input[type="password"][maxlength="6"]', otp)
#                     print(f"✅ OTP Filled: {otp}")
#                 except:
#                     try:
#                         iframe.locator('input').nth(0).fill(otp)
#                     except:
#                         print("❌ Could not fill OTP")

#                 time.sleep(2)

#                 try:
#                     iframe.click('button#submitBtn, button:has-text("SUBMIT")', timeout=100000)
#                     print("✅ OTP SUBMIT Clicked")
#                 except:
#                     iframe.evaluate("""() => {
#                         const btns = document.querySelectorAll('button');
#                         for (let b of btns) {
#                             if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
#                         }
#                     }""")
#             else:
#                 print("❌ OTP not received from API")
#         else:
#             print("❌ OTP Iframe not found")

#         time.sleep(8)
#         print(f"✅ Run #{run_number} Completed!")
#         status = "complete"

#     except Exception as e:
#         print(f"❌ Run #{run_number} Failed: {e}")
#         status = "failed"
#         error_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     finally:
#         duration_sec = round(time.time() - start_time, 1)

#         # Update sheet row with results
#         sheet_updates = {
#             COL_STATUS:       status,
#             COL_NAME_USED:    billing_name,
#             COL_PROXY_IP:     proxy_ip_label,
#             COL_DURATION_SEC: duration_sec,
#             COL_ERROR_TS:     error_ts,
#         }
#         try:
#             update_row_status(sheet_row_index, ws, headers, sheet_updates)
#             print(f"📊 Sheet Row {sheet_row_index} Updated → Status: {status} | Duration: {duration_sec}s")
#         except Exception as e:
#             print(f"❌ Sheet update failed: {e}")

#         save_log({
#             "sheet_row": sheet_row_index,
#             "run_number": run_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "email": email,
#             "status": status,
#             "duration_sec": duration_sec,
#             "proxy": proxy_ip_label,
#             "error_timestamp": error_ts,
#         })

#         try:
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
#         try:
#             if gl: gl.stop()
#         except: pass

#         # === UPDATED: Delete profile in ALL cases (success or failed) ===
#         if gl and profile_id:
#             try:
#                 gl.delete(profile_id)
#                 print(f"🗑️ Profile deleted: {profile_id} (Status: {status})")
#             except Exception as del_e:
#                 print(f"⚠️ Failed to delete profile {profile_id}: {del_e}")

# # ================= MAIN =================

# if __name__ == "__main__":
#     print("=== Magzter Full Flow — Google Sheet Tasks Mode ===\n")

#     # Load sheet + headers once
#     ws = get_sheet()
#     all_values = ws.get_all_values()
#     if not all_values:
#         print("❌ Sheet is empty!")
#         exit(1)
#     headers = all_values[0]  # first row = column names
#     print(f"📋 Sheet headers: {headers}")

#     # Load pending rows
#     pending = load_pending_rows()
#     if not pending:
#         print("✅ No pending rows found. All done!")
#         exit(0)

#     print(f"\n🚀 Processing {len(pending)} pending rows...\n")

#     for run_number, (row_index, row_data) in enumerate(pending, start=1):
#         run_one_cycle(run_number, row_index, row_data, ws, headers)
#         if run_number < len(pending):
#             wait = random.uniform(25, 45)
#             print(f"\n⏳ Waiting {wait:.0f}s before next run...")
#             time.sleep(wait)

#     print("\n🎉 All Pending Rows Processed!")


import time
import random
import json
import os
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

try:
    from gologin import GoLogin
except ImportError:
    print("❌ Install GoLogin: pip install gologin")
    exit(1)

try:
    import gspread
except ImportError:
    print("❌ Install gspread: pip install gspread")
    exit(1)

# ================= CONFIG =================
LOG_FILE = "magzter_logs.json"
HEADLESS = False

# 2Captcha API key — used to auto-solve captcha (reCAPTCHA / hCaptcha / Cloudflare Turnstile)
# that appears on the Stripe / payment step.
TWOCAPTCHA_API_KEY = "CHANGE_ME_API_KEY"

GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "gmblinks",
    "private_key_id": "CHANGE_ME_KEY_ID",
    "private_key": "-----BEGIN PRIVATE KEY-----
CHANGE_ME_ROTATE_THIS_KEY
-----END PRIVATE KEY-----\n",
    "client_email": "test@example.com",
    "client_id": "0000000000",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "CHANGE_ME_TOKEN",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/marcadeo-tech%40gmblinks.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

SPREADSHEET_ID = "1usY7UmsiGCIHcDAJoBuHNJWtScSzNhMVhr6nqnpegUU"
TASKS_SHEET = "Gologin_Test"

# Expected columns in Tasks sheet (order must match sheet headers exactly)
# Card_No | Month | CVV | Email | Password | Corp_ID | Emp_ID | Zip_Code | First_Name | Last_Name | Status | Name_Used | Proxy_IP | Duration_Sec | ErrorTimestamp

COL_CARD_NO      = "0000000000000000"
COL_MONTH        = "Month"
COL_CVV          = "000"
COL_EMAIL        = "test@example.com"
COL_PASSWORD     = "CHANGE_ME_PASSWORD"
COL_CORP_ID      = "Corp_ID"
COL_EMP_ID       = "CHANGE_ME_EMP_ID"
COL_ZIP_CODE     = "Zip_Code"
COL_FIRST_NAME   = "John"
COL_LAST_NAME    = "Doe"
COL_STATUS       = "Status"
COL_NAME_USED    = "Name_Used"
COL_PROXY_IP     = "Proxy_IP"
COL_DURATION_SEC = "Duration_Sec"
COL_ERROR_TS     = "Error"

# ================= GOOGLE SHEET HELPERS =================

def get_sheet():
    gc = gspread.service_account_from_dict(GOOGLE_CREDENTIALS)
    sh = gc.open_by_key(SPREADSHEET_ID)
    return sh.worksheet(TASKS_SHEET)

def load_pending_rows():
    """Load all rows from Tasks sheet where Status is empty or 'pending'."""
    ws = get_sheet()
    records = ws.get_all_records()
    pending = []
    for idx, row in enumerate(records, start=2):  # row 1 = header, data starts at 2
        status = str(row.get(COL_STATUS, "")).strip().lower()
        if status in ("", "pending"):
            pending.append((idx, row))
    print(f"✅ {len(pending)} pending rows loaded from '{TASKS_SHEET}'")
    return pending

def update_row_status(row_index, ws, headers, updates: dict):
    """Write multiple cell updates to a specific row using column names."""
    for col_name, value in updates.items():
        try:
            col_idx = headers.index(col_name) + 1  # gspread is 1-indexed
            ws.update_cell(row_index, col_idx, value)
        except ValueError:
            print(f"⚠️ Column '{col_name}' not found in sheet headers — skipping")
        except Exception as e:
            print(f"⚠️ Could not update '{col_name}': {e}")

# ================= GOLOGIN =================

def load_gologin_tokens():
    tokens = []
    try:
        with open("config.txt", "r", encoding="utf-8") as f:
            for line in f:
                token = line.strip()
                if len(token) > 50:
                    tokens.append(token)
    except:
        pass
    if tokens:
        print(f"✅ {len(tokens)} GoLogin Token(s) Loaded")
        return tokens
    print("❌ config.txt mein GoLogin token(s) daal do!")
    exit(1)

GOLOGIN_TOKENS = load_gologin_tokens()

# ================= OTP =================

def get_latest_otp(emp_id, max_attempts=30, delay=4):
    api_emp_id = emp_id.upper()
    url = f"https://test.trackopia.in/api/employees/{api_emp_id}/latest-otp"
    print(f"🔍 Waiting for OTP from API (emp: {api_emp_id})...")
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, timeout=500)
            if response.status_code == 200:
                data = response.json()
                otp = data.get("otp")
                if otp and len(str(otp)) == 6:
                    print(f"✅ OTP Received: {otp}")
                    return str(otp)
            print(f"⏳ OTP not ready (Attempt {attempt}/{max_attempts})")
        except Exception as e:
            print(f"⚠️ API Error: {e}")
        time.sleep(delay)
    print("❌ Could not fetch OTP")
    return None

# ================= CAPTCHA (2Captcha) =================

# This init-script is injected into EVERY page/frame BEFORE the site's own JS runs.
# It hooks the hCaptcha API so that whenever Stripe (or any site) renders/executes
# hCaptcha, we capture the sitekey, the enterprise `rqdata`, and — most importantly —
# the success `callback`. Stripe reads the token via this callback, NOT via a textarea,
# so capturing it is what lets us actually pass the challenge.
HCAPTCHA_HOOK_JS = r"""() => {
    try {
        if (window.__hc_hook_installed) return;
        window.__hc_hook_installed = true;
        window.__hc_data = window.__hc_data || {};
        const grab = (opts) => {
            try {
                if (!opts || typeof opts !== 'object') return;
                if (opts.sitekey) window.__hc_data.sitekey = opts.sitekey;
                if (opts.rqdata) window.__hc_data.rqdata = opts.rqdata;
                if (typeof opts.callback === 'function') window.__hc_data.callback = opts.callback;
                else if (typeof opts.callback === 'string' && typeof window[opts.callback] === 'function') window.__hc_data.callback = window[opts.callback];
            } catch (e) {}
        };
        let _hc;
        Object.defineProperty(window, 'hcaptcha', {
            configurable: true,
            get() { return _hc; },
            set(v) {
                _hc = v;
                try {
                    ['render', 'execute'].forEach((fn) => {
                        if (v && typeof v[fn] === 'function') {
                            const orig = v[fn].bind(v);
                            v[fn] = function (a, b) {
                                grab(typeof a === 'object' ? a : null);
                                grab(typeof b === 'object' ? b : null);
                                return orig(a, b);
                            };
                        }
                    });
                } catch (e) {}
            }
        });
    } catch (e) {}
}"""


def _twocaptcha_solve(method_params, max_wait=180, poll=5):
    """Submit a job to 2captcha and poll res.php until solved. Returns token or None."""
    try:
        in_params = {"key": TWOCAPTCHA_API_KEY, "json": 1}
        in_params.update(method_params)
        r = requests.post("https://2captcha.com/in.php", data=in_params, timeout=60)
        data = r.json()
        if data.get("status") != 1:
            print(f"⚠️ 2captcha submit error: {data.get('request')}")
            return None
        captcha_id = data["request"]
        print(f"🧩 2captcha job submitted (id={captcha_id}) — waiting for solution...")

        waited = 0
        while waited < max_wait:
            time.sleep(poll)
            waited += poll
            res = requests.get(
                "https://2captcha.com/res.php",
                params={"key": TWOCAPTCHA_API_KEY, "action": "get", "id": captcha_id, "json": 1},
                timeout=60,
            )
            res_data = res.json()
            if res_data.get("status") == 1:
                print("✅ Captcha solved by 2captcha")
                return res_data["request"]
            if res_data.get("request") != "CAPCHA_NOT_READY":
                print(f"⚠️ 2captcha solve error: {res_data.get('request')}")
                return None
            print(f"⏳ Captcha not ready ({waited}s/{max_wait}s)")
        print("❌ Captcha solve timed out")
        return None
    except Exception as e:
        print(f"⚠️ 2captcha request failed: {e}")
        return None


def _detect_captcha(page):
    """Scan the main page + all frames for a captcha widget.
    Combines the hCaptcha hook data (sitekey/rqdata captured at render time) with a
    DOM scan. Returns dict {type, sitekey, rqdata, frame} or None."""
    dom_js = r"""() => {
        const out = {};
        // hCaptcha hook data (captured before render) — most reliable for Stripe.
        try {
            if (window.__hc_data && window.__hc_data.sitekey) {
                out.type = 'hcaptcha';
                out.sitekey = window.__hc_data.sitekey;
                out.rqdata = window.__hc_data.rqdata || '';
                out.hasCallback = !!window.__hc_data.callback;
                return out;
            }
        } catch (e) {}

        // reCAPTCHA v2
        let iframeRc = document.querySelector('iframe[src*="recaptcha/api2"], iframe[src*="recaptcha/enterprise"]');
        if (iframeRc) { const m = iframeRc.src.match(/[?&]k=([^&]+)/); if (m) return {type: 'recaptcha', sitekey: decodeURIComponent(m[1])}; }
        let g = document.querySelector('.g-recaptcha[data-sitekey]');
        if (g) return {type: 'recaptcha', sitekey: g.getAttribute('data-sitekey')};

        // hCaptcha via DOM
        let h = document.querySelector('.h-captcha[data-sitekey], [data-hcaptcha-sitekey]');
        if (h) return {type: 'hcaptcha', sitekey: h.getAttribute('data-sitekey') || h.getAttribute('data-hcaptcha-sitekey'), rqdata: ''};
        let hIframe = document.querySelector('iframe[src*="hcaptcha.com"]');
        if (hIframe) { const m = hIframe.src.match(/[?&]sitekey=([^&]+)/); if (m) return {type: 'hcaptcha', sitekey: decodeURIComponent(m[1]), rqdata: ''}; }

        // Cloudflare Turnstile
        let t = document.querySelector('.cf-turnstile[data-sitekey], [data-sitekey][class*="turnstile"]');
        if (t) return {type: 'turnstile', sitekey: t.getAttribute('data-sitekey')};
        let tIframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
        if (tIframe) { const m = tIframe.src.match(/[?&]sitekey=([^&]+)/); if (m) return {type: 'turnstile', sitekey: decodeURIComponent(m[1])}; }
        return null;
    }"""

    frames = [page.main_frame] + [f for f in page.frames if f != page.main_frame]
    for frame in frames:
        try:
            found = frame.evaluate(dom_js)
            if found and found.get("sitekey"):
                found["frame"] = frame
                return found
        except Exception:
            continue
    return None


def _inject_captcha_token(frame, captcha_type, token):
    """Set the response textarea(s) AND invoke the captured/site callback in `frame`."""
    js = r"""(args) => {
        const {ctype, token} = args;
        const setVal = (sel) => {
            document.querySelectorAll(sel).forEach(t => {
                t.value = token;
                try { t.innerHTML = token; } catch (e) {}
                t.dispatchEvent(new Event('input', {bubbles: true}));
                t.dispatchEvent(new Event('change', {bubbles: true}));
            });
        };
        let firedCallback = false;
        if (ctype === 'hcaptcha') {
            setVal('textarea[name="h-captcha-response"]');
            setVal('textarea[name="g-recaptcha-response"]');
            setVal('textarea#h-captcha-response');
            setVal('textarea[name="hcaptcha-response"]');
            // The real success callback we captured at render time — this is what Stripe listens to.
            try {
                if (window.__hc_data && typeof window.__hc_data.callback === 'function') {
                    window.__hc_data.callback(token);
                    firedCallback = true;
                }
            } catch (e) {}
            // data-callback attribute fallback
            try {
                document.querySelectorAll('.h-captcha[data-callback]').forEach(el => {
                    const cbName = el.getAttribute('data-callback');
                    if (cbName && typeof window[cbName] === 'function') { window[cbName](token); firedCallback = true; }
                });
            } catch (e) {}
        } else if (ctype === 'recaptcha') {
            setVal('textarea#g-recaptcha-response');
            setVal('textarea[name="g-recaptcha-response"]');
            try {
                if (window.___grecaptcha_cfg && window.___grecaptcha_cfg.clients) {
                    const findCb = (obj, depth) => {
                        if (!obj || depth > 6) return null;
                        for (const k in obj) { try { const v = obj[k];
                            if (v && typeof v === 'object') { if (typeof v.callback === 'function') return v.callback; const r = findCb(v, depth + 1); if (r) return r; }
                        } catch (e) {} } return null;
                    };
                    for (const cid in window.___grecaptcha_cfg.clients) { const cb = findCb(window.___grecaptcha_cfg.clients[cid], 0); if (cb) { cb(token); firedCallback = true; } }
                }
            } catch (e) {}
        } else if (ctype === 'turnstile') {
            setVal('input[name="cf-turnstile-response"]');
            setVal('textarea[name="cf-turnstile-response"]');
        }
        return firedCallback;
    }"""
    args = {"ctype": captcha_type, "token": token}
    fired_any = False
    # Try the frame that has the hook data first, then all frames as fallback.
    targets = [frame] if frame else []
    try:
        targets += [f for f in frame.page.frames if f != frame]
    except Exception:
        pass
    for f in targets:
        try:
            if f.evaluate(js, args):
                fired_any = True
        except Exception:
            continue
    return fired_any


def solve_captcha_if_present(page, label=""):
    """Detect a captcha; if found, solve via 2captcha (enterprise rqdata aware) and
    inject the token + fire the callback. Returns True if solved, else False."""
    try:
        detected = _detect_captcha(page)
    except Exception as e:
        print(f"⚠️ Captcha detection error: {e}")
        detected = None

    if not detected:
        return False

    ctype = detected["type"]
    sitekey = detected["sitekey"]
    rqdata = detected.get("rqdata") or ""
    frame = detected.get("frame")
    page_url = page.url
    print(f"🧩 Captcha detected{(' ' + label) if label else ''}: type={ctype} sitekey={sitekey} enterprise={bool(rqdata)}")

    if ctype == "recaptcha":
        params = {"method": "userrecaptcha", "googlekey": sitekey, "pageurl": page_url}
    elif ctype == "hcaptcha":
        params = {"method": "hcaptcha", "sitekey": sitekey, "pageurl": page_url}
        if rqdata:
            # Stripe uses hCaptcha Enterprise — rqdata is mandatory for a valid token.
            params["data"] = rqdata
            params["enterprise"] = 1
    elif ctype == "turnstile":
        params = {"method": "turnstile", "sitekey": sitekey, "pageurl": page_url}
    else:
        print(f"⚠️ Unknown captcha type: {ctype}")
        return False

    token = _twocaptcha_solve(params)
    if not token:
        print("❌ Captcha could not be solved")
        return False

    fired = _inject_captcha_token(frame, ctype, token)
    print(f"✅ Captcha token injected (callback fired: {fired})")
    time.sleep(random.uniform(2, 4))
    return True


def wait_and_solve_captcha(page, timeout=60, label=""):
    """Poll for up to `timeout` seconds waiting for a captcha to appear, then solve it.
    Use this right after submitting the card, since the hCaptcha modal pops up a few
    seconds into 'Processing'. Returns True if a captcha was solved."""
    waited = 0
    interval = 3
    while waited < timeout:
        if solve_captcha_if_present(page, label=label):
            return True
        time.sleep(interval)
        waited += interval
    return False

# ================= LOGGING =================

def save_log(data):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    logs.append(data)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    print(f"📝 Log Saved | Row #{data['sheet_row']}")

# ================= SINGLE CYCLE =================

def run_one_cycle(run_number, sheet_row_index, row_data, ws, headers):
    print(f"\n🚀 === Run #{run_number} | Sheet Row {sheet_row_index} ===")

    # --- Read inputs from sheet row ---
    card_number  = str(row_data.get(COL_CARD_NO, "")).strip()
    card_expiry  = str(row_data.get(COL_MONTH, "")).strip()   # e.g. "06/28"
    card_cvc     = str(row_data.get(COL_CVV, "")).strip()
    email        = str(row_data.get(COL_EMAIL, "")).strip()
    password     = str(row_data.get(COL_PASSWORD, "")).strip()
    corp_id      = str(row_data.get(COL_CORP_ID, "")).strip()
    emp_id       = str(row_data.get(COL_EMP_ID, "")).strip()
    zip_code     = str(row_data.get(COL_ZIP_CODE, "")).strip()
    first_name   = str(row_data.get(COL_FIRST_NAME, "")).strip()
    last_name    = str(row_data.get(COL_LAST_NAME, "")).strip()

    billing_name = f"{first_name} {last_name}".strip()

    # Proxy config (static residential — update if needed)
    proxy_host = "sg.proxy.geonode.io"
    proxy_port = 11000
    proxy_user = "geonode_xvmYN44Bvz-type-residential-country-in"
    proxy_pass = "CHANGE_ME_SECRET"
    proxy_ip_label = f"{proxy_host}:{proxy_port}"

    status = "failed"
    error_ts = ""
    duration_sec = ""
    start_time = time.time()

    gl = None
    pw = None
    browser = None
    page = None
    profile_id = None

    try:
        # Mark row as "running" immediately
        update_row_status(sheet_row_index, ws, headers, {COL_STATUS: "running"})

        current_token = GOLOGIN_TOKENS[(run_number - 1) % len(GOLOGIN_TOKENS)]
        gl = GoLogin({"token": current_token})

        profile = gl.createProfileRandomFingerprint({
            "name": f"magzter-{run_number}",
            "os": "win",
            "timezone": "Asia/Kolkata",
            "language": "en-US",
            "languages": ["en-US", "en"]
        })
        profile_id = profile['id']
        print(f"✅ Profile Created: {profile_id}")

        proxy_data = {
            "mode": "socks5",
            "host": proxy_host,
            "port": proxy_port,
            "username": proxy_user,
            "password": proxy_pass
        }
        gl.changeProfileProxy(profile_id, proxy_data)
        print("✅ Proxy Configured")

        gl.setProfileId(profile_id)
        debugger_address = gl.start()
        print(f"✅ Browser Started: {debugger_address}")

        pw = sync_playwright().start()
        browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        # Install the hCaptcha hook into every future document/frame (incl. the Stripe page)
        # so we can capture the sitekey, enterprise rqdata, and success callback at render time.
        try:
            context.add_init_script(HCAPTCHA_HOOK_JS)
            print("✅ hCaptcha hook installed")
        except Exception as e:
            print(f"⚠️ Could not install hCaptcha hook: {e}")

        context.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
        page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); }")

        # ================= FULL FLOW =================
        page.goto("https://app.adstracking.io/click?pid=3030&offer_id=20655", timeout=100000, wait_until="domcontentloaded")
        time.sleep(random.uniform(5, 8))

        for _ in range(3):
            page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
            time.sleep(random.uniform(0.8, 1.5))

        page.click('button:has-text("Claim Now")', timeout=100000)
        time.sleep(random.uniform(5, 9))

        print(f"📧 Email: {email}")
        page.fill('input[type="email"]', email)
        time.sleep(random.uniform(2, 4))
        page.click('button:has-text("Continue")', timeout=100000)
        time.sleep(random.uniform(6, 10))

        page.fill('input[placeholder*="First Name"]', first_name)
        page.fill('input[placeholder*="Last Name"]', last_name)
        # Zip code field removed from website - skipping
        time.sleep(random.uniform(3, 5))

        page.click('button#submitBtn, button.svelte-xdpg18', timeout=100000)
        time.sleep(random.uniform(7, 12))

        # Payment Details
        print("💳 Filling Card Details...")

        # Captcha may appear when the Stripe/payment page loads — solve it before filling.
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except:
            pass
        solve_captcha_if_present(page, label="(payment page load)")

        page.fill('input#cardNumber', card_number, timeout=100000)
        page.fill('input#cardExpiry', card_expiry, timeout=100000)
        page.fill('input#cardCvc', card_cvc, timeout=100000)
        page.fill('input#billingName', billing_name, timeout=100000)
        time.sleep(random.uniform(4, 7))

        # Captcha may also appear right before/while submitting the card — solve if present.
        solve_captcha_if_present(page, label="(before card submit)")

        print("💳 Submitting Card...")
        page.click('button[type="submit"], button:has-text("Submit"), button:has-text("Pay")', timeout=100000)
        time.sleep(random.uniform(6, 9))

        # The "One more step before you're done" hCaptcha modal pops up a few seconds into
        # 'Processing'. Poll for up to 60s, solve it, then let Stripe continue.
        print("🧩 Watching for Stripe hCaptcha challenge...")
        if wait_and_solve_captcha(page, timeout=60, label="(stripe payment)"):
            print("✅ Stripe captcha handled — waiting for payment to continue...")
            time.sleep(random.uniform(8, 12))
            # Some flows need the Pay button pressed again after the captcha closes.
            try:
                if page.locator('button:has-text("Pay"), button[type="submit"]').count() > 0:
                    page.click('button[type="submit"], button:has-text("Pay")', timeout=15000)
                    print("💳 Re-submitted after captcha")
                    time.sleep(random.uniform(6, 10))
            except:
                pass
        else:
            print("ℹ️ No captcha appeared within wait window")

        # ================= CORPORATE FORM =================
        print("🏢 Waiting for Corporate Form...")
        time.sleep(12)

        try:
            page.wait_for_load_state("networkidle", timeout=100000)
        except:
            pass

        iframe = None
        for frame in page.frames:
            if frame == page.main_frame:
                continue
            try:
                if (frame.get_by_text("Corporate ID").count() > 0 or
                        frame.get_by_text("Employee ID").count() > 0):
                    iframe = frame
                    print("✅ Corporate Iframe Found by Text!")
                    break
            except:
                continue

        if not iframe:
            for frame in page.frames:
                if frame == page.main_frame:
                    continue
                name_lower = (frame.name or "").lower()
                url_lower = (frame.url or "").lower()
                if any(k in name_lower + url_lower for k in ["challenge", "3ds", "icici", "corporate", "employee"]):
                    iframe = frame
                    print(f"✅ Iframe Found by Keyword: {frame.name}")
                    break

        if iframe:
            iframe.wait_for_selector('input', timeout=100000)
            time.sleep(4)
            try:
                iframe.fill('input[placeholder*="Corporate"], input#corporateId, input[name*="corporate"]', corp_id, timeout=100000)
                print(f"✅ Corporate ID Filled: {corp_id}")
            except:
                iframe.locator('input').nth(0).fill(corp_id, timeout=100000)

            time.sleep(2)

            try:
                iframe.fill('input[placeholder*="Employee"], input#employeeId, input[name*="employee"]', emp_id, timeout=100000)
                print(f"✅ Employee ID Filled: {emp_id}")
            except:
                iframe.locator('input').nth(1).fill(emp_id, timeout=100000)

            time.sleep(2)

            try:
                iframe.click('button:has-text("SUBMIT"), button[type="submit"]', timeout=100000)
                print("✅ Corporate SUBMIT Clicked")
            except:
                iframe.evaluate("""() => {
                    const btns = document.querySelectorAll('button, a');
                    for (let b of btns) {
                        if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
                    }
                }""")
        else:
            print("❌ Corporate Iframe not found — trying main page")
            try:
                page.fill('input[placeholder*="Corporate"]', corp_id, timeout=100000)
                page.fill('input[placeholder*="Employee"]', emp_id, timeout=100000)
                page.click('button:has-text("SUBMIT")', timeout=100000)
            except:
                print("⚠️ Main page fallback failed")

        # ================= OTP FORM =================
        print("\n🔐 Waiting for OTP Form...")
        time.sleep(20)

        iframe = None
        for frame in page.frames:
            if frame == page.main_frame:
                continue
            try:
                if frame.get_by_text("Enter OTP").count() > 0 or frame.get_by_text("Cardholder authentication").count() > 0:
                    iframe = frame
                    print("✅ OTP Iframe Found!")
                    break
            except:
                continue

        if not iframe:
            non_main = [f for f in page.frames if f != page.main_frame]
            if non_main:
                iframe = non_main[0]
                print("⚠️ Using fallback iframe for OTP")

        if iframe:
            try:
                iframe.wait_for_selector('input', timeout=100000)
                time.sleep(3)
            except:
                pass

            otp = get_latest_otp(emp_id, max_attempts=35, delay=5)

            if otp:
                try:
                    iframe.fill('input[name="otpValue"], input.input-field, input[type="password"][maxlength="6"]', otp, timeout=100000)
                    print(f"✅ OTP Filled: {otp}")
                except:
                    try:
                        iframe.locator('input').nth(0).fill(otp, timeout=100000)
                    except:
                        print("❌ Could not fill OTP")

                time.sleep(2)

                try:
                    iframe.click('button#submitBtn, button:has-text("SUBMIT")', timeout=100000)
                    print("✅ OTP SUBMIT Clicked")
                except:
                    iframe.evaluate("""() => {
                        const btns = document.querySelectorAll('button');
                        for (let b of btns) {
                            if (b.textContent && b.textContent.trim().toUpperCase().includes('SUBMIT')) { b.click(); return; }
                        }
                    }""")
            else:
                print("❌ OTP not received from API")
        else:
            print("❌ OTP Iframe not found")

        time.sleep(8)
        print(f"✅ Run #{run_number} Completed!")
        status = "complete"

    except Exception as e:
        print(f"❌ Run #{run_number} Failed: {e}")
        status = "failed"
        error_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    finally:
        duration_sec = round(time.time() - start_time, 1)

        # Update sheet row with results
        sheet_updates = {
            COL_STATUS:       status,
            COL_NAME_USED:    billing_name,
            COL_PROXY_IP:     proxy_ip_label,
            COL_DURATION_SEC: duration_sec,
            COL_ERROR_TS:     error_ts,
        }
        try:
            update_row_status(sheet_row_index, ws, headers, sheet_updates)
            print(f"📊 Sheet Row {sheet_row_index} Updated → Status: {status} | Duration: {duration_sec}s")
        except Exception as e:
            print(f"❌ Sheet update failed: {e}")

        save_log({
            "sheet_row": sheet_row_index,
            "run_number": run_number,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "email": email,
            "status": status,
            "duration_sec": duration_sec,
            "proxy": proxy_ip_label,
            "error_timestamp": error_ts,
        })

        try:
            if browser: browser.close()
            if pw: pw.stop()
        except: pass
        try:
            if gl: gl.stop()
        except: pass

        # === UPDATED: Delete profile in ALL cases (success or failed) ===
        if gl and profile_id:
            try:
                gl.delete(profile_id)
                print(f"🗑️ Profile deleted: {profile_id} (Status: {status})")
            except Exception as del_e:
                print(f"⚠️ Failed to delete profile {profile_id}: {del_e}")

# ================= MAIN =================

if __name__ == "__main__":
    print("=== Magzter Full Flow — Google Sheet Tasks Mode ===\n")

    # Load sheet + headers once
    ws = get_sheet()
    all_values = ws.get_all_values()
    if not all_values:
        print("❌ Sheet is empty!")
        exit(1)
    headers = all_values[0]  # first row = column names
    print(f"📋 Sheet headers: {headers}")

    # Load pending rows
    pending = load_pending_rows()
    if not pending:
        print("✅ No pending rows found. All done!")
        exit(0)

    print(f"\n🚀 Processing {len(pending)} pending rows...\n")

    for run_number, (row_index, row_data) in enumerate(pending, start=1):
        run_one_cycle(run_number, row_index, row_data, ws, headers)
        if run_number < len(pending):
            wait = random.uniform(25, 45)
            print(f"\n⏳ Waiting {wait:.0f}s before next run...")
            time.sleep(wait)

    print("\n🎉 All Pending Rows Processed!")