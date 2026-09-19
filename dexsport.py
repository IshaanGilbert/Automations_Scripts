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
# from selenium.webdriver.common.by import By

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
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
# ]

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

# # ================= RANDOM CLICK FUNCTION =================
# def perform_random_click(driver):
#     try:
#         # Clickable elements selectors
#         selectors = [
#             "a", "button", "input[type='button']", "input[type='submit']",
#             "div[onclick]", "span[onclick]", "[role='button']"
#         ]
        
#         all_elements = []
#         for selector in selectors:
#             elements = driver.find_elements(By.CSS_SELECTOR, selector)
#             all_elements.extend(elements)
        
#         # Filter visible and enabled elements
#         clickable = []
#         for el in all_elements:
#             try:
#                 if el.is_displayed() and el.is_enabled():
#                     clickable.append(el)
#             except:
#                 continue
        
#         if clickable:
#             element = random.choice(clickable)
#             # Scroll to element smoothly
#             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
#             time.sleep(random.uniform(0.8, 1.5))
            
#             # Random click
#             ActionChains(driver).move_to_element(element).pause(random.uniform(0.3, 0.8)).click().perform()
#             print(f"   ➤ Random click performed on element")
#             return True
#         else:
#             print("   ➤ No clickable element found")
#             return False
#     except Exception as e:
#         print(f"   ➤ Click error: {e}")
#         return False

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
      
#         print("🚀 Firefox opened with proxy...")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(5, 9))   # Initial wait after load
      
#         current_url = driver.current_url
#         print(f"📍 Landed on : {current_url[:90]}...")
      
#         # Perform Random Click
#         print("🖱️ Looking for clickable element...")
#         perform_random_click(driver)
      
#         # Human-like behavior (Stay Time)
#         stay_time = random.uniform(28, 52)
#         print(f"⏳ Staying {stay_time:.1f} seconds on page...")
#         start_time = time.time()
        
#         while time.time() - start_time < stay_time and not stop_flag:
#             if random.random() < 0.60:
#                 try:
#                     driver.execute_script(f"window.scrollBy(0, {random.randint(200, 700)});")
#                 except:
#                     pass
#                 time.sleep(random.uniform(1.2, 3.5))
          
#             if random.random() < 0.40:
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-120, 120), random.randint(-70, 70)).perform()
#                 except:
#                     pass
#                 time.sleep(random.uniform(0.6, 2.0))
            
#             time.sleep(0.7)
      
#         print(f"✅ Visit #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s\n")
      
#         visit_data = {
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "ip": "Unknown",
#             "landed_url": current_url[:150],
#             "stay_duration": round(stay_time, 1),
#             "random_click": True
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
#             print(f"🔒 Firefox closed for Visit #{visit_number}\n")

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
#         print("Please place 'geckodriver-v0.36.0-win64' folder correctly.")
#         sys.exit(1)
  
#     print("=== Geonode + Firefox + Random Click ===\n")
#     print(f"Target Visits : {TARGET_VISITS} | Max Concurrent : {MAX_CONCURRENT_SESSIONS}\n")
    
#     stop_flag = False
    
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

# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.common.by import By

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# TARGET_URL        = "https://partners.trackopia.com/click?aid=4&oid=311"
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS      = "CHANGE_ME_SECRET"
# GEONODE_HOST      = "sg.proxy.geonode.io"
# GEONODE_PORT      = "11000"

# COUNTRIES = ["IN", "IT", "FR"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
# ]

# LOG_FILE         = "visit_log.json"
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# # ================= USER SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 4
# TARGET_VISITS           = 2000

# # ================= GLOBAL =================
# stop_flag = False
# log_lock  = threading.Lock()

# # ================= LOGGING — Real-time JSON save =================
# def save_log(visit_data):
#     """Har visit ke baad turant JSON file mein save karta hai"""
#     with log_lock:
#         logs = []
#         # Existing logs load karo
#         if os.path.exists(LOG_FILE):
#             try:
#                 with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                     logs = json.load(f)
#             except Exception:
#                 logs = []

#         logs.append(visit_data)

#         # Turant write karo
#         try:
#             with open(LOG_FILE, 'w', encoding='utf-8') as f:
#                 json.dump(logs, f, indent=2, ensure_ascii=False)
#         except Exception as e:
#             print(f"⚠️ Log save failed: {e}")

# def get_total_logged():
#     """Abhi tak kitne log saved hain"""
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return len(json.load(f))
#         except:
#             return 0
#     return 0

# # ================= RANDOM CLICK =================
# def perform_random_click(driver):
#     try:
#         selectors = [
#             "a", "button", "input[type='button']", "input[type='submit']",
#             "div[onclick]", "span[onclick]", "[role='button']"
#         ]
#         all_elements = []
#         for selector in selectors:
#             try:
#                 all_elements.extend(driver.find_elements(By.CSS_SELECTOR, selector))
#             except:
#                 pass

#         clickable = []
#         for el in all_elements:
#             try:
#                 if el.is_displayed() and el.is_enabled():
#                     clickable.append(el)
#             except:
#                 continue

#         if clickable:
#             element = random.choice(clickable)
#             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
#             time.sleep(random.uniform(0.8, 1.5))
#             ActionChains(driver).move_to_element(element).pause(
#                 random.uniform(0.3, 0.8)
#             ).click().perform()
#             print("   ➤ Random click performed on element")
#             return True
#         else:
#             print("   ➤ No clickable element found")
#             return False
#     except Exception as e:
#         print(f"   ➤ Click error: {str(e)[:60]}")
#         return False

# # ================= SINGLE VISIT =================
# def open_with_proxy(visit_number):
#     global stop_flag
#     if stop_flag:
#         return

#     country_code = random.choice(COUNTRIES)
#     username     = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url    = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"

#     print(f"\n=== Visit #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy : {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {
#             'http':     proxy_url,
#             'https':    proxy_url,
#             'no_proxy': 'localhost,127.0.0.1'
#         },
#         # ✅ Internal seleniumwire proxy requests ko suppress karta hai
#         'request_storage':          'memory',
#         'suppress_connection_errors': True,
#         'disable_encoding':           True,
#         'connection_timeout':         45,
#         # Internal 0.0.x.x requests ko intercept mat karo
#         'ignore_http_methods':        [],
#         'exclude_hosts':              ['0.0.0.0', '127.0.0.1', 'localhost'],
#     }

#     options = Options()
#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
#     options.set_preference("dom.webdriver.enabled",      False)
#     options.set_preference("useAutomationExtension",     False)
#     options.set_preference("privacy.resistFingerprinting", False)

#     # ✅ Firefox binary path — agar default location pe nahi hai to yahan set karo
#     # options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

#     width  = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver     = None
#     click_done = False
#     landed_url = ""

#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver  = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )

#         print("🚀 Firefox opened with proxy...")

#         # Page load timeout set karo — hang nahi karega
#         driver.set_page_load_timeout(60)

#         try:
#             driver.get(TARGET_URL)
#         except Exception as load_err:
#             # Timeout pe bhi continue — page partial load ho sakta hai
#             print(f"⚠️ Page load note: {str(load_err)[:80]}")

#         time.sleep(random.uniform(5, 9))

#         landed_url = driver.current_url
#         print(f"📍 Landed on : {landed_url[:90]}")

#         # Random Click
#         print("🖱️ Looking for clickable element...")
#         click_done = perform_random_click(driver)

#         # Human-like stay
#         stay_time  = random.uniform(28, 52)
#         print(f"⏳ Staying {stay_time:.1f} seconds on page...")
#         start_time = time.time()

#         while time.time() - start_time < stay_time and not stop_flag:
#             action = random.random()

#             if action < 0.45:
#                 try:
#                     driver.execute_script(
#                         f"window.scrollBy(0, {random.randint(200, 700)});"
#                     )
#                 except:
#                     pass
#                 time.sleep(random.uniform(1.2, 3.5))

#             elif action < 0.70:
#                 try:
#                     ActionChains(driver).move_by_offset(
#                         random.randint(-120, 120),
#                         random.randint(-70, 70)
#                     ).perform()
#                 except:
#                     pass
#                 time.sleep(random.uniform(0.6, 2.0))

#             else:
#                 time.sleep(random.uniform(1.0, 2.5))

#         print(f"✅ Visit #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s")

#         # ✅ Real-time log save — visit complete hote hi
#         save_log({
#             "visit_number":  visit_number,
#             "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country":       country_code,
#             "landed_url":    landed_url[:150],
#             "stay_duration": round(stay_time, 1),
#             "random_click":  click_done,
#             "status":        "success",
#         })
#         print(f"💾 Logged visit #{visit_number} → {LOG_FILE}")

#     except Exception as e:
#         err_msg = str(e)[:200]
#         print(f"❌ Error in Visit #{visit_number}: {err_msg}")

#         # ✅ Failed visits bhi log hoti hain
#         save_log({
#             "visit_number": visit_number,
#             "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country":      country_code,
#             "landed_url":   landed_url[:150] if landed_url else "",
#             "stay_duration": 0,
#             "random_click": False,
#             "status":       "error",
#             "error":        err_msg,
#         })

#     finally:
#         if driver:
#             time.sleep(random.uniform(1, 3))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Firefox closed for Visit #{visit_number}")

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
#             saved = get_total_logged()
#             print(f"📊 Completed: {completed_count[0]}/{TARGET_VISITS} | Saved in JSON: {saved}")

#         time.sleep(random.uniform(0.8, 2.2))

# # ================= MAIN =================
# if __name__ == "__main__":
#     if not os.path.exists(GECKODRIVER_PATH):
#         print(f"❌ GeckoDriver not found at:\n{GECKODRIVER_PATH}")
#         print("Please place 'geckodriver-v0.36.0-win64' folder in script directory.")
#         sys.exit(1)

#     print("=== Geonode + Firefox + Random Click ===\n")
#     print(f"Target Visits : {TARGET_VISITS} | Max Concurrent : {MAX_CONCURRENT_SESSIONS}")
#     print(f"Log File      : {os.path.abspath(LOG_FILE)}\n")

#     stop_flag = False

#     visit_queue = Queue()
#     for i in range(1, TARGET_VISITS + 1):
#         visit_queue.put(i)

#     lock            = threading.Lock()
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

#     total_saved = get_total_logged()
#     print(f"\n🎉 Script execution finished!")
#     print(f"Total Visits Completed : {completed_count[0]}/{TARGET_VISITS}")
#     print(f"Total Logs Saved       : {total_saved} → {os.path.abspath(LOG_FILE)}")





# import time
# import random
# import sys
# import os
# import json
# from datetime import datetime
# import warnings
# import threading
# from queue import Queue, Empty

# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER + SELENIUMWIRE FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver
#     import selenium.webdriver.edge.webdriver

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.common.by import By

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= FIREFOX PORTABLE PATH =================
# FIREFOX_BINARY = resource_path("FirefoxPortable/App/Firefox/firefox.exe")

# # ================= CONFIG =================
# TARGET_URL        = "https://partners.trackopia.com/click?aid=4&oid=311"   # ← Apna original URL
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS      = "CHANGE_ME_SECRET"
# GEONODE_HOST      = "sg.proxy.geonode.io"
# GEONODE_PORT      = "11000"

# COUNTRIES = ["IN", "IT", "FR"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
# ]

# LOG_FILE         = "visit_log.json"
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# # ================= USER SETTINGS =================
# MAX_CONCURRENT_SESSIONS = 3      # Thoda kam kiya stability ke liye
# TARGET_VISITS           = 2000

# # ================= GLOBAL =================
# stop_flag = False
# log_lock  = threading.Lock()

# # ================= LOGGING =================
# def save_log(visit_data):
#     with log_lock:
#         logs = []
#         if os.path.exists(LOG_FILE):
#             try:
#                 with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                     logs = json.load(f)
#             except Exception:
#                 logs = []
#         logs.append(visit_data)
#         try:
#             with open(LOG_FILE, 'w', encoding='utf-8') as f:
#                 json.dump(logs, f, indent=2, ensure_ascii=False)
#         except Exception as e:
#             print(f"⚠️ Log save failed: {e}")

# def get_total_logged():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 return len(json.load(f))
#         except:
#             return 0
#     return 0

# # ================= RANDOM CLICK =================
# def perform_random_click(driver):
#     try:
#         selectors = ["a", "button", "input[type='button']", "input[type='submit']",
#                      "div[onclick]", "span[onclick]", "[role='button']"]
#         all_elements = []
#         for selector in selectors:
#             try:
#                 all_elements.extend(driver.find_elements(By.CSS_SELECTOR, selector))
#             except:
#                 pass

#         clickable = [el for el in all_elements if el.is_displayed() and el.is_enabled()]
        
#         if clickable:
#             element = random.choice(clickable)
#             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
#             time.sleep(random.uniform(0.8, 1.5))
#             ActionChains(driver).move_to_element(element).pause(random.uniform(0.3, 0.8)).click().perform()
#             print("   ➤ Random click performed")
#             return True
#         return False
#     except Exception as e:
#         print(f"   ➤ Click error: {str(e)[:60]}")
#         return False

# # ================= SINGLE VISIT =================
# def open_with_proxy(visit_number):
#     global stop_flag
#     if stop_flag:
#         return

#     country_code = random.choice(COUNTRIES)
#     username     = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url    = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"

#     print(f"\n=== Visit #{visit_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy : {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
#         'request_storage': 'memory',
#         'suppress_connection_errors': True,
#         'connection_timeout': 45,
#         'exclude_hosts': ['0.0.0.0', '127.0.0.1', 'localhost'],
#     }

#     options = Options()
    
#     # 🔥 PORTABLE FIREFOX FIX (Sabse Important)
#     if os.path.exists(FIREFOX_BINARY):
#         options.binary_location = FIREFOX_BINARY
#         print(f"✅ Bundled Firefox Loaded: {FIREFOX_BINARY}")
#     else:
#         print(f"⚠️ Firefox binary not found at: {FIREFOX_BINARY}")

#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)

#     width  = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver = None
#     click_done = False
#     landed_url = ""

#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )

#         print("🚀 Firefox opened with proxy...")
#         driver.set_page_load_timeout(60)

#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(5, 9))

#         landed_url = driver.current_url
#         print(f"📍 Landed on : {landed_url[:90]}")

#         click_done = perform_random_click(driver)

#         stay_time = random.uniform(28, 52)
#         print(f"⏳ Staying {stay_time:.1f} seconds...")
#         start_time = time.time()

#         while time.time() - start_time < stay_time and not stop_flag:
#             action = random.random()
#             if action < 0.45:
#                 driver.execute_script(f"window.scrollBy(0, {random.randint(200, 700)});")
#             elif action < 0.70:
#                 ActionChains(driver).move_by_offset(random.randint(-120, 120), random.randint(-70, 70)).perform()
#             time.sleep(random.uniform(1.0, 3.5))

#         print(f"✅ Visit #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s")

#         save_log({
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "landed_url": landed_url[:150],
#             "stay_duration": round(stay_time, 1),
#             "random_click": click_done,
#             "status": "success",
#         })

#     except Exception as e:
#         err_msg = str(e)[:200]
#         print(f"❌ Error in Visit #{visit_number}: {err_msg}")
#         save_log({
#             "visit_number": visit_number,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "country": country_code,
#             "landed_url": landed_url[:150] if landed_url else "",
#             "stay_duration": 0,
#             "random_click": False,
#             "status": "error",
#             "error": err_msg,
#         })

#     finally:
#         if driver:
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print(f"🔒 Firefox closed for Visit #{visit_number}")

# # ================= WORKER & MAIN (Same as before) =================
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
#             saved = get_total_logged()
#             print(f"📊 Completed: {completed_count[0]}/{TARGET_VISITS} | Saved: {saved}")

#         time.sleep(random.uniform(0.8, 2.2))

# if __name__ == "__main__":
#     if not os.path.exists(GECKODRIVER_PATH):
#         print(f"❌ GeckoDriver not found at:\n{GECKODRIVER_PATH}")
#         sys.exit(1)

#     print("=== Geonode + Portable Firefox + Random Click ===\n")
#     print(f"Target Visits : {TARGET_VISITS} | Max Concurrent : {MAX_CONCURRENT_SESSIONS}\n")

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
#         time.sleep(random.uniform(1.0, 2.5))

#     try:
#         while completed_count[0] < TARGET_VISITS and not stop_flag:
#             time.sleep(3)
#     except KeyboardInterrupt:
#         print("\n🛑 Stopping...")
#         stop_flag = True

#     for t in threads:
#         if t.is_alive():
#             t.join(timeout=20)

#     print(f"\n🎉 Finished! Total Logs Saved: {get_total_logged()}")





import time
import random
import sys
import os
import json
from datetime import datetime
import warnings
import threading
from queue import Queue, Empty

warnings.filterwarnings("ignore", category=UserWarning)

# ================= PYINSTALLER FIX - Hidden Imports =================
if getattr(sys, 'frozen', False):
    import selenium.webdriver.chrome.webdriver
    import selenium.webdriver.firefox.webdriver
    import selenium.webdriver.edge.webdriver
    import selenium.webdriver.safari.webdriver
    import selenium.webdriver.remote.webdriver

# ================= SELENIUM IMPORTS =================
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

# ================= RESOURCE PATH =================
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ================= FIREFOX PORTABLE PATH =================
FIREFOX_BINARY = resource_path("firefox_portable/FirefoxPortable/App/Firefox/firefox.exe")

# ================= CONFIG =================
TARGET_URL        = ""
GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
GEONODE_PASS      = "CHANGE_ME_SECRET"
GEONODE_HOST      = "sg.proxy.geonode.io"
GEONODE_PORT      = "11000"

COUNTRIES = ["IT", "CH", "AT", "IN", "FR", "AU"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
]

LOG_FILE         = "visit_log.json"
GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# ================= USER SETTINGS =================
MAX_CONCURRENT_SESSIONS = 3
TARGET_VISITS           = 500

# ================= GLOBAL =================
stop_flag = False
log_lock  = threading.Lock()

# ================= LOGGING =================
def save_log(visit_data):
    with log_lock:
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(visit_data)
        try:
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Log save failed: {e}")

def get_total_logged():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return len(json.load(f))
        except:
            return 0
    return 0

# ================= RANDOM CLICK =================
def perform_random_click(driver):
    try:
        selectors = ["a", "button", "input[type='button']", "input[type='submit']",
                     "div[onclick]", "span[onclick]", "[role='button']"]
        all_elements = []
        for selector in selectors:
            try:
                all_elements.extend(driver.find_elements(By.CSS_SELECTOR, selector))
            except:
                pass

        clickable = [el for el in all_elements if el.is_displayed() and el.is_enabled()]
        
        if clickable:
            element = random.choice(clickable)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(random.uniform(0.8, 1.5))
            ActionChains(driver).move_to_element(element).pause(random.uniform(0.3, 0.8)).click().perform()
            print("   ➤ Random click performed")
            return True
        return False
    except Exception as e:
        print(f"   ➤ Click error: {str(e)[:60]}")
        return False

# ================= SINGLE VISIT =================
def open_with_proxy(visit_number):
    global stop_flag
    if stop_flag:
        return

    country_code = random.choice(COUNTRIES)
    username     = GEONODE_USER_BASE.format(country_code.lower())
    proxy_url    = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"

    print(f"\n=== Visit #{visit_number} | Country: {country_code} ===")
    print(f"🔗 Proxy : {proxy_url[:75]}...")

    seleniumwire_options = {
        'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'},
        'request_storage': 'memory',
        'suppress_connection_errors': True,
        'connection_timeout': 45,
        'exclude_hosts': ['0.0.0.0', '127.0.0.1', 'localhost'],
    }

    options = Options()
    
    # 🔥 PORTABLE FIREFOX
    if os.path.exists(FIREFOX_BINARY):
        options.binary_location = FIREFOX_BINARY
        print(f"✅ Portable Firefox Loaded Successfully!")
    else:
        print(f"❌ Firefox NOT found at: {FIREFOX_BINARY}")

    options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    options.set_preference("privacy.resistFingerprinting", False)

    width  = random.choice([1366, 1440, 1536, 1920])
    height = random.choice([768, 900, 1080])
    options.add_argument(f"--width={width}")
    options.add_argument(f"--height={height}")

    driver = None
    click_done = False
    landed_url = ""

    try:
        service = Service(executable_path=GECKODRIVER_PATH)
        driver = webdriver.Firefox(
            seleniumwire_options=seleniumwire_options,
            options=options,
            service=service
        )

        print("🚀 Firefox opened with proxy...")
        driver.set_page_load_timeout(60)

        driver.get(TARGET_URL)
        time.sleep(random.uniform(5, 9))

        landed_url = driver.current_url
        print(f"📍 Landed on : {landed_url[:90]}")

        click_done = perform_random_click(driver)

        stay_time = random.uniform(28, 52)
        print(f"⏳ Staying {stay_time:.1f} seconds...")
        start_time = time.time()

        while time.time() - start_time < stay_time and not stop_flag:
            action = random.random()
            if action < 0.45:
                driver.execute_script(f"window.scrollBy(0, {random.randint(200, 700)});")
            elif action < 0.70:
                ActionChains(driver).move_by_offset(random.randint(-120, 120), random.randint(-70, 70)).perform()
            time.sleep(random.uniform(1.0, 3.5))

        print(f"✅ Visit #{visit_number} completed | {country_code} | Stayed {stay_time:.1f}s")

        save_log({
            "visit_number": visit_number,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "country": country_code,
            "landed_url": landed_url[:150],
            "stay_duration": round(stay_time, 1),
            "random_click": click_done,
            "status": "success",
        })

    except Exception as e:
        err_msg = str(e)[:200]
        print(f"❌ Error in Visit #{visit_number}: {err_msg}")
        save_log({
            "visit_number": visit_number,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "country": country_code,
            "landed_url": landed_url[:150] if landed_url else "",
            "stay_duration": 0,
            "random_click": False,
            "status": "error",
            "error": err_msg,
        })

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
            print(f"🔒 Firefox closed for Visit #{visit_number}")

# ================= WORKER =================
def worker(visit_queue, completed_count, lock):
    global stop_flag
    while not stop_flag:
        try:
            visit_number = visit_queue.get_nowait()
        except Empty:
            break

        open_with_proxy(visit_number)

        with lock:
            completed_count[0] += 1
            saved = get_total_logged()
            print(f"📊 Completed: {completed_count[0]}/{TARGET_VISITS} | Saved: {saved}")

        time.sleep(random.uniform(0.8, 2.2))

# ================= MAIN =================
if __name__ == "__main__":
    if not os.path.exists(GECKODRIVER_PATH):
        print(f"❌ GeckoDriver not found at:\n{GECKODRIVER_PATH}")
        sys.exit(1)

    print("=== Geonode + Portable Firefox + Random Click ===\n")
    print(f"Target Visits : {TARGET_VISITS} | Max Concurrent : {MAX_CONCURRENT_SESSIONS}\n")

    visit_queue = Queue()
    for i in range(1, TARGET_VISITS + 1):
        visit_queue.put(i)

    lock = threading.Lock()
    completed_count = [0]
    threads = []

    for _ in range(MAX_CONCURRENT_SESSIONS):
        t = threading.Thread(target=worker, args=(visit_queue, completed_count, lock), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(random.uniform(1.0, 2.5))

    try:
        while completed_count[0] < TARGET_VISITS and not stop_flag:
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        stop_flag = True

    for t in threads:
        if t.is_alive():
            t.join(timeout=20)

    print(f"\n🎉 Script Finished! Total Logs Saved: {get_total_logged()}")
    
    if getattr(sys, 'frozen', False):
        print("\nPress any key to exit...")
        try:
            input()
        except:
            pass