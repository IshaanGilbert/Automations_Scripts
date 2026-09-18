


# import os
# import json
# import time
# import random
# import hashlib
# import datetime
# import logging
# import requests
# import threading
# import subprocess
# import tkinter as tk
# from queue import Queue
# from tkinter import messagebox
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import (
#     WebDriverException,
#     TimeoutException,
#     NoSuchElementException,
#     ElementClickInterceptedException,
#     ElementNotInteractableException,
#     StaleElementReferenceException,
#     JavascriptException,
#     UnexpectedAlertPresentException,
#     NoSuchWindowException,
#     SessionNotCreatedException
# )
# from selenium.webdriver.common.action_chains import ActionChains
# import undetected_chromedriver as uc
# import string
# import requests.exceptions
# import socket

# # Logging configuration
# logging.basicConfig(
#     filename="error_log.txt",
#     level=logging.ERROR,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )

# # Geonode credentials for proxy
# USERNAME = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD = "CHANGE_ME_PASSWORD"
# GEONODE_DNS = "sg.proxy.geonode.io:11000"
# TEST_URL = "http://ip-api.com/json"
# IP_CHECK_URL = "https://api.ipify.org?format=json"

# # Load base URLs from config
# with open("config.json") as f:
#     config = json.load(f)
# BASE_URLS = config.get("base_urls", [])

# visits = 0
# app_start_time = time.time()
# task_queue = Queue()
# allow_task_run = False
# task_lock = threading.Lock()
# visit_times = []

# def scheduler(start_times, end_times):
#     global allow_task_run
#     while True:
#         now = datetime.datetime.now().time()
#         with task_lock:
#             allow_task_run = any(start <= now < end for start, end in zip(start_times, end_times))
#         time.sleep(5)

# class WebTaskGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Web Task Automation")
#         self.root.geometry("500x400")
#         padding = {'padx': 10, 'pady': 5}

#         self.start_times = []
#         self.end_times = []

#         for i in range(3):
#             start_label = tk.Label(root, text=f"Start Time {i+1} (HH:MM):")
#             start_label.grid(row=i, column=0, sticky="w", **padding)
#             start_entry = tk.Entry(root, width=10)
#             start_entry.grid(row=i, column=1, **padding)
#             self.start_times.append(start_entry)

#             end_label = tk.Label(root, text=f"End Time {i+1} (HH:MM):")
#             end_label.grid(row=i, column=2, sticky="w", **padding)
#             end_entry = tk.Entry(root, width=10)
#             end_entry.grid(row=i, column=3, **padding)
#             self.end_times.append(end_entry)

#         self.min_delay_label = tk.Label(root, text="Min Delay (seconds):")
#         self.min_delay_label.grid(row=6, column=0, sticky="w", **padding)
#         self.min_delay_entry = tk.Entry(root, width=10)
#         self.min_delay_entry.grid(row=6, column=1, **padding)
#         self.min_delay_entry.insert(0, "30")

#         self.max_delay_label = tk.Label(root, text="Max Delay (seconds):")
#         self.max_delay_label.grid(row=6, column=2, sticky="w", **padding)
#         self.max_delay_entry = tk.Entry(root, width=10)
#         self.max_delay_entry.grid(row=6, column=3, **padding)
#         self.max_delay_entry.insert(0, "50")

#         self.num_browsers_label = tk.Label(root, text="Number of Browsers:")
#         self.num_browsers_label.grid(row=7, column=0, sticky="w", **padding)
#         self.num_browsers_entry = tk.Entry(root, width=10)
#         self.num_browsers_entry.grid(row=7, column=1, **padding)
#         self.num_browsers_entry.insert(0, "1")

#         self.status_label = tk.Label(root, text="Status: Ready", fg="blue")
#         self.status_label.grid(row=10, columnspan=4, pady=5)

#         self.run_button = tk.Button(root, text="Run Task", command=self.run_task)
#         self.run_button.grid(row=11, columnspan=4, pady=10)

#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")

#     def update_task_count(self, visit_count):
#         self.status_label.config(text=f"Visit Count: {visit_count}")

#     def run_task(self):
#         try:
#             start_times = []
#             end_times = []
#             for i in range(3):
#                 start_time_str = self.start_times[i].get()
#                 end_time_str = self.end_times[i].get()
#                 if start_time_str and end_time_str:
#                     start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
#                     end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
#                     start_times.append(start_time)
#                     end_times.append(end_time)
#                 elif not start_time_str and not end_time_str:
#                     continue
#                 else:
#                     raise ValueError("Both start and end times must be provided or left empty.")

#             if not start_times or not end_times:
#                 raise ValueError("At least one set of start and end times must be provided.")

#             min_delay = int(self.min_delay_entry.get()) if self.min_delay_entry.get() else 45
#             max_delay = int(self.max_delay_entry.get()) if self.max_delay_entry.get() else 60
#             if min_delay <= 0 or max_delay <= 0:
#                 raise ValueError("Delay values must be greater than zero.")
#             if min_delay > max_delay:
#                 raise ValueError("Max Delay value must be greater than Min Delay.")

#             num_browsers = int(self.num_browsers_entry.get())
#             if num_browsers <= 0:
#                 raise ValueError("Number of browsers must be at least 1.")

#             scheduler_thread = threading.Thread(target=scheduler, args=(start_times, end_times), daemon=True)
#             scheduler_thread.start()

#             def web_task_thread(browser_id):
#                 global allow_task_run
#                 while True:
#                     if allow_task_run:
#                         self.update_status(f"Running browser {browser_id}...")
#                         proxy_url, proxy_ip = generate_indian_proxy()
#                         if proxy_url:
#                             driver = init_browser(proxy_url)
#                             if driver:
#                                 # Verify the browser's IP
#                                 actual_ip = verify_browser_ip(driver)
#                                 if actual_ip and actual_ip != proxy_ip:
#                                     logging.error(f"Browser using IP {actual_ip} instead of proxy IP {proxy_ip}")
#                                     print(f"Warning: Browser using IP {actual_ip} instead of proxy IP {proxy_ip}")
#                                 navigate_and_click(driver, task_queue, proxy_ip)
#                                 driver.quit()
#                             else:
#                                 self.update_status(f"Failed to initialize browser {browser_id}. Retrying...")
#                                 time.sleep(5)
#                         else:
#                             self.update_status(f"Failed to generate proxy for browser {browser_id}. Retrying...")
#                             time.sleep(5)
#                     else:
#                         self.update_status(f"Paused browser {browser_id}...")
#                     time.sleep(5)

#             threads = []
#             for i in range(num_browsers):
#                 t = threading.Thread(target=web_task_thread, args=(i + 1,), daemon=True)
#                 threads.append(t)
#                 t.start()

#         except ValueError as e:
#             messagebox.showerror("Input Error", f"Invalid input values: {str(e)}")
# def test_proxy(proxy_url):
#     """Test if a SOCKS5 proxy is working and returns Indian IP"""
#     try:
#         proxy_host, proxy_port = GEONODE_DNS.split(":")
#         proxy_dict = {
#             "proxyType": "MANUAL",
#             "socksProxy": f"{proxy_host}:{proxy_port}",
#             "socksVersion": 5,
#             "httpProxy": None,
#             "sslProxy": None,
#             "username": USERNAME,
#             "password": PASSWORD
#         }
        
#         # Use requests with pysocks for SOCKS5
#         proxies = {
#             "http": f"socks5h://{USERNAME}:CHANGE_ME_PASSWORD@{proxy_host}:{proxy_port}",
#             "https": f"socks5h://{USERNAME}:CHANGE_ME_PASSWORD@{proxy_host}:{proxy_port}"
#         }
#         response = requests.get(TEST_URL, proxies=proxies, timeout=15)
#         logging.debug(f"Proxy test response: {response.status_code}, {response.text}")
#         if response.status_code == 200:
#             data = response.json()
#             if data.get("status") == "success" and data.get("countryCode") == "IN":
#                 return True, data.get("query")
#         return False, None
#     except Exception as e:
#         logging.error(f"Proxy test failed for {proxy_url}: {str(e)}")
#         return False, str(e)

# def generate_indian_proxy():
#     """Generate a single working Indian proxy"""
#     max_attempts = 5
#     attempt = 0
#     while attempt < max_attempts:
#         proxy_url = f"socks5://{USERNAME}:CHANGE_ME_PASSWORD@{GEONODE_DNS}"
#         logging.debug(f"Attempting to test proxy: {proxy_url}")
#         is_working, ip = test_proxy(proxy_url)
#         if is_working:
#             print(f"Generated working Indian proxy: {ip}")
#             logging.info(f"Generated working Indian proxy: {ip}")
#             return proxy_url, ip
#         attempt += 1
#         time.sleep(2)  # Increased delay to respect rate limits
#     logging.error("Failed to generate a working Indian proxy after max attempts")
#     return None, None

# def init_browser(proxy_url=None):
#     try:
#         options = uc.ChromeOptions()
#         fingerprinting = generate_fingerprinting()

#         if not fingerprinting:
#             print("Fingerprinting data is missing or invalid.")
#             logging.error("Fingerprinting data is missing or invalid.")
#             return None

#         # User Agent
#         options.add_argument(f"--user-agent={fingerprinting['user_agent']}")

#         # Proxy settings for SOCKS5
#         if proxy_url:
#             proxy_host, proxy_port = GEONODE_DNS.split(":")
#             options.add_argument(f"--proxy-server=socks5://{proxy_host}:{proxy_port}")
#             options.add_argument("--ignore-certificate-errors")
#             options.add_argument("--allow-insecure-localhost")
#             # Avoid using --proxy-auth as it may not work reliably with SOCKS5
#             logging.debug(f"Setting SOCKS5 proxy: socks5://{proxy_host}:{proxy_port}")

#         # General options
#         options.add_argument("--disable-gpu")
#         options.add_argument("--disable-software-rasterizer")
#         options.add_argument("--enable-unsafe-webgl")
#         options.add_argument("--use-gl=swiftshader")
#         options.add_argument("--enable-webgl")
#         options.add_argument("--log-level=3")
#         options.add_argument("--disable-logging")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-popup-blocking")
#         options.add_argument("--disable-extensions")
#         options.add_argument("--disable-infobars")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_argument("--force-timezone=Asia/Kolkata")

#         # Set binary and driver paths
#         project_dir = os.getcwd()
#         chrome_binary_path = os.path.join(project_dir, "Chrome", "chrome.exe")
#         driver_path = os.path.join(project_dir, "chromedriver", "chromedriver.exe")

#         if not os.path.exists(chrome_binary_path):
#             print(f"Chrome binary not found at {chrome_binary_path}. Check the path!")
#             logging.error(f"Chrome binary not found at {chrome_binary_path}")
#             return None

#         if not os.path.exists(driver_path):
#             print(f"ChromeDriver not found at {driver_path}. Check the path!")
#             logging.error(f"ChromeDriver not found at {driver_path}")
#             return None

#         options.binary_location = chrome_binary_path

#         driver = uc.Chrome(
#             driver_executable_path=driver_path,
#             options=options,
#             version_main=120,
#             headless=False
#         )

#         # Set proxy authentication via CDP (Chrome DevTools Protocol)
#         if proxy_url:
#             driver.execute_cdp_cmd("Network.setUserAgentOverride", {
#                 "userAgent": fingerprinting["user_agent"]
#             })
#             driver.execute_cdp_cmd("Network.setBypassServiceWorker", {"bypass": True})
#             # Inject proxy authentication
#             driver.execute_cdp_cmd("Network.setProxy", {
#                 "proxyType": "manual",
#                 "socksProxy": f"{proxy_host}:{proxy_port}",
#                 "socksVersion": 5,
#                 "username": USERNAME,
#                 "password": PASSWORD
#             })
#             logging.debug(f"Applied proxy authentication via CDP for {proxy_host}:{proxy_port}")

#         # Set custom resolution
#         device_type = fingerprinting['device_type']
#         device_resolutions = {
#             "android_phone": (360, 640),
#             "iphone": (360, 640),
#             "tablet": (768, 1024),
#             "ipad": (768, 1024),
#             "android_tablet": (768, 1024),
#             "smart_tv": (1920, 1080),
#             "car_browser": (1280, 720),
#         }
#         driver.set_window_size(*device_resolutions.get(device_type, (1366, 768)))

#         # Inject anti-detection JS
#         js_script = f"""
#         Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#         Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
#         Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});

#         const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
#         WebGLRenderingContext.prototype.getParameter = function(param) {{
#             if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#             if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#             return getParameterProxy.call(this, param);
#         }};

#         const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
#         HTMLCanvasElement.prototype.toDataURL = function() {{
#             return "data:image/png;base64," + btoa("fakecanvasdata");
#         }};

#         const audioContext = window.AudioContext || window.webkitAudioContext;
#         if (audioContext) {{
#             const originalCreateOscillator = audioContext.prototype.createOscillator;
#             audioContext.prototype.createOscillator = function() {{
#                 const oscillator = originalCreateOscillator.call(this);
#                 oscillator.frequency.value = 1000;
#                 return oscillator;
#             }};
#         }}

#         Object.defineProperty(navigator, 'mediaDevices', {{
#             get: () => undefined
#         }});

#         Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#             return {{ timeZone: '{fingerprinting["timezone"]}' }};
#         }};
#         """

#         driver.execute_script(js_script)
#         logging.info("Browser initialized successfully with SOCKS5 proxy")
#         return driver

#     except Exception as e:
#         print(f"Failed to initialize browser: {e}")
#         logging.error(f"Failed to initialize browser: {e}")
#         return None
    
# def verify_browser_ip(driver):
#     """Verify the IP address used by the browser"""
#     try:
#         driver.get(IP_CHECK_URL)
#         ip_data = json.loads(driver.find_element(By.TAG_NAME, "body").text)
#         return ip_data.get("ip")
#     except Exception as e:
#         logging.error(f"Failed to verify browser IP: {e}")
#         return None

# def generate_fingerprinting():
#     device_os_mapping = {
#         "desktop": ["Windows", "macOS", "Linux", "Fedora"],
#         "laptop": ["Windows", "macOS", "Linux", "ChromeOS", "Fedora"],
#         "ultrabook": ["Windows", "macOS", "Linux", "Fedora"],
#         "macbook": ["macOS"],
#         "chromebook": ["ChromeOS"],
#         "smartphone": ["Windows", "Android", "iOS"],
#         "android_phone": ["Android"],
#         "iphone": ["iOS"],
#         "tablet": ["Android", "iOS"],
#         "ipad": ["iPadOS"],
#         "android_tablet": ["Android"],
#         "smart_tv": ["Android TV", "Tizen", "WebOS"],
#     }

#     user_agents = {
#         "Windows": [
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Midori/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Falkon/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Opera/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Safari/{3}.0.0.0",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36"
#         ],
#         "Fedora": [
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/76.0.4017.154 Safari/537.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.26.74 Safari/537.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Vivaldi/4.2.2406.44 Safari/537.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Konqueror/5.0.97 Safari/537.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Epiphany/40.1 Safari/537.36"
#         ],
#         "iPadOS": [
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Opera/73.0.3856.257 Safari/537.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Vivaldi/4.2.2406.44 Safari/537.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.31.87 Safari/537.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) UC Browser/13.4.0.1307 Safari/537.36"
#         ],
#         "macOS": [
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Safari/{3}.0.0.0",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Microsoft Edge/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36"
#         ],
#         "Linux": [
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Falkon/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Midori/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Arch Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Manjaro Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36"
#         ],
#         "Android": [
#             "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) EdgA/{3}.0.{4}.0 Mobile Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Mobile Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Mobile Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) DuckDuckGo/{3}.0.{4}.0 Mobile Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Mobile Safari/{2}.36"
#         ],
#         "iOS": [
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) EdgiOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) DuckDuckGo/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) EdgiOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36"
#         ],
#         "ChromeOS": [
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS armv7l {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; Google Pixelbook) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; ASUS Chromebook) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; Acer Chromebook Spin) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; Samsung Chromebook) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36"
#         ],
#         "Tizen": [
#             "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (SMART-TV; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}; Samsung SmartTV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}; Samsung 4K UHD) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "Android TV": [
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Nexus Player) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; MiTV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; SHIELD Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Sony BRAVIA 4K GB) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Samsung SmartTV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.0.0 Safari/{2}.36"
#         ],
#         "WebOS": [
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Firefox/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.1 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) WebView/{3}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Opera/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Midori/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Falkon/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0 Safari/{2}.36",
#         ],
#     }

#     device_type = random.choice(list(device_os_mapping.keys()))
#     os = random.choice(device_os_mapping[device_type])
#     version_main = random.randint(8, 14)
#     version_minor = random.randint(0, 3)
#     webkit_version = random.randint(500, 600)
#     chrome_version = random.randint(90, 120)
#     firefox_version = random.randint(10, 90)
#     build_version = random.randint(1000, 5000)
#     user_agent = random.choice(user_agents[os]).format(
#         version_main, version_minor, webkit_version, chrome_version, firefox_version, build_version
#     )
#     screen_widths = [1024, 1366, 1920, 2560, 3840]
#     screen_heights = [768, 800, 1080, 1200, 1600]
#     device_pixel_ratio = [1, 1.25, 1.5, 2, 2.5, 3]
#     webgl_renderer = ["ANGLE (NVIDIA)", "Intel(R) UHD Graphics", "AMD Radeon RX"]
#     webgl_vendor = ["Google Inc.", "Intel Inc.", "NVIDIA Corporation"]
#     timezone = ["UTC", "America/New_York", "Europe/Berlin", "Asia/Tokyo"]
#     plugin_list = [
#         ["Chrome PDF Viewer", "Widevine Content Decryption Module"],
#         ["PDF.js", "Shockwave Flash"],
#         ["Java", "Silverlight"]
#     ]
#     installed_fonts = [
#         ["Arial", "Verdana", "Times New Roman"],
#         ["Roboto", "Lato", "Montserrat"],
#         ["Comic Sans MS", "Courier New"]
#     ]
#     accept_language = [
#         "en-US,en;q=0.9", "fr-FR,fr;q=0.8", "de-DE,de;q=0.9", "es-ES,es;q=0.8"
#     ]
#     navigator_platform = ["Win32", "Linux x86_64", "MacIntel"]
#     speech_synthesis_voices = [
#         ["Google UK English Male", "Microsoft Zira"],
#         ["Google Deutsch", "Apple Samantha"],
#         ["Google Español", "Microsoft David"]
#     ]

#     def generate_random_webgl():
#         random_string = "".join(random.choices("abcdef0123456789", k=32))
#         return hashlib.sha256(random_string.encode()).hexdigest()[:32]

#     def generate_random_canvas():
#         random_string = "".join(random.choices("abcdef0123456789", k=32))
#         return hashlib.sha256(random_string.encode()).hexdigest()[:32]

#     return {
#         "device_type": device_type,
#         "os": os,
#         "user_agent": user_agent,
#         "screen_width": random.choice(screen_widths),
#         "screen_height": random.choice(screen_heights),
#         "device_pixel_ratio": random.choice(device_pixel_ratio),
#         "webgl_disabled": random.choice([True, False]),
#         "webgl_renderer": random.choice(webgl_renderer),
#         "webgl_vendor": random.choice(webgl_vendor),
#         "peer_connection_disabled": random.choice([True, False]),
#         "resist_fingerprinting": random.choice([True, False]),
#         "language": random.choice(["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-PT", "ru-RU", "zh-CN", "ja-JP", "ko-KR", "ar-SA"]),
#         "timezone_offset": random.choice([0, -180, -240, 180, 360]),
#         "timezone": random.choice(timezone),
#         "plugins": random.choice([True, False]),
#         "plugin_list": random.choice(plugin_list),
#         "fonts": random.choice([True, False]),
#         "installed_fonts": random.choice(installed_fonts),
#         "hardware_concurrency": random.choice([2, 4, 8, 12, 16]),
#         "device_memory": random.choice([2, 4, 8, 16, 32]),
#         "screen_orientation": random.choice(["portrait", "landscape"]),
#         "accept_language": random.choice(accept_language),
#         "audio_fingerprint": random.choice(["audio1", "audio2", "audio3"]),
#         "gpu_fingerprint": random.choice(["gpu1", "gpu2", "gpu3"]),
#         "navigator_platform": random.choice(navigator_platform),
#         "do_not_track": random.choice(["1", "0", None]),
#         "math_tan_pi": random.choice([3.14159265358979, 3.0000000000000000]),
#         "speech_synthesis_voices": random.choice(speech_synthesis_voices),
#         "canvas": generate_random_canvas(),
#         "networkType": random.choice(["4g", "5g", "wifi"]),
#         "cookieEnabled": random.choice([True, False]),
#         "display": f"{random.randint(20, 50)}|{random.randint(300, 600)}|{random.randint(400, 800)}|{random.randint(300, 600)}|{random.randint(400, 800)}",
#         "platform": random.choice(["MacIntel", "Win32", "Linux x86_64"]),
#         "java": random.choice(["true", "false"]),
#         "webgl": generate_random_webgl(),
#         "silverlight": "NA",
#         "touchSupport": random.choice([True, False]),
#         "errorProperty": "${flash,http-accept-headers,audio}"
#     }


# def init_browser(proxy_url=None):
#     try:
#         options = uc.ChromeOptions()
#         fingerprinting = generate_fingerprinting()

#         if not fingerprinting:
#             print("Fingerprinting data is missing or invalid.")
#             return None

#         # User Agent
#         options.add_argument(f"--user-agent={fingerprinting['user_agent']}")

#         # Proxy settings for SOCKS5
#         if proxy_url:
#             proxy_host = GEONODE_DNS.split(":")[0]
#             proxy_port = GEONODE_DNS.split(":")[1]
#             options.add_argument(f"--proxy-server=socks5://{proxy_host}:{proxy_port}")
#             options.add_argument("--ignore-certificate-errors")
#             options.add_argument("--allow-insecure-localhost")
            
#             # Set proxy authentication using Chrome DevTools Protocol
#             options.add_argument(f"--proxy-auth={USERNAME}:{PASSWORD}")

#         # General options
#         options.add_argument("--disable-gpu")
#         options.add_argument("--disable-software-rasterizer")
#         options.add_argument("--enable-unsafe-webgl")
#         options.add_argument("--use-gl=swiftshader")
#         options.add_argument("--enable-webgl")
#         options.add_argument("--log-level=3")
#         options.add_argument("--disable-logging")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-popup-blocking")
#         options.add_argument("--disable-extensions")
#         options.add_argument("--disable-infobars")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_argument("--force-timezone=Asia/Kolkata")

#         # Set binary and driver paths
#         project_dir = os.getcwd()
#         chrome_binary_path = os.path.join(project_dir, "Chrome", "chrome.exe")
#         driver_path = os.path.join(project_dir, "chromedriver", "chromedriver.exe")

#         if not os.path.exists(chrome_binary_path):
#             print(f"Chrome binary not found at {chrome_binary_path}. Check the path!")
#             return None

#         if not os.path.exists(driver_path):
#             print(f"ChromeDriver not found at {driver_path}. Check the path!")
#             return None

#         options.binary_location = chrome_binary_path

#         driver = uc.Chrome(
#             driver_executable_path=driver_path,
#             options=options,
#             version_main=120,
#             headless=False
#         )

#         # Set proxy authentication via CDP (Chrome DevTools Protocol)
#         if proxy_url:
#             driver.execute_cdp_cmd("Network.setUserAgentOverride", {
#                 "userAgent": fingerprinting["user_agent"]
#             })
#             driver.execute_cdp_cmd("Network.setBypassServiceWorker", {"bypass": True})

#         # Set custom resolution
#         device_type = fingerprinting['device_type']
#         device_resolutions = {
#             "android_phone": (360, 640),
#             "iphone": (360, 640),
#             "tablet": (768, 1024),
#             "ipad": (768, 1024),
#             "android_tablet": (768, 1024),
#             "smart_tv": (1920, 1080),
#             "car_browser": (1280, 720),
#         }
#         driver.set_window_size(*device_resolutions.get(device_type, (1366, 768)))

#         # Inject anti-detection JS
#         js_script = f"""
#         Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#         Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
#         Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});

#         const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
#         WebGLRenderingContext.prototype.getParameter = function(param) {{
#             if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#             if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#             return getParameterProxy.call(this, param);
#         }};

#         const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
#         HTMLCanvasElement.prototype.toDataURL = function() {{
#             return "data:image/png;base64," + btoa("fakecanvasdata");
#         }};

#         const audioContext = window.AudioContext || window.webkitAudioContext;
#         if (audioContext) {{
#             const originalCreateOscillator = audioContext.prototype.createOscillator;
#             audioContext.prototype.createOscillator = function() {{
#                 const oscillator = originalCreateOscillator.call(this);
#                 oscillator.frequency.value = 1000;
#                 return oscillator;
#             }};
#         }}

#         Object.defineProperty(navigator, 'mediaDevices', {{
#             get: () => undefined
#         }});

#         Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#             return {{ timeZone: '{fingerprinting["timezone"]}' }};
#         }};
#         """

#         driver.execute_script(js_script)

#         return driver

#     except Exception as e:
#         print(f"Failed to initialize browser: {e}")
#         logging.error(f"Failed to initialize browser: {e}")
#         return None

# def random_delay(min_delay, max_delay):
#     delay = random.randint(min_delay, max_delay)
#     return delay

# def clear_cookies(driver):
#     try:
#         print("Clearing all cookies...")
#         driver.delete_all_cookies()
#         print("All cookies cleared.")
#     except Exception as e:
#         error_message = f"Failed to clear cookie: {e}"
#         print("Failed to clear cookies")
#         logging.error(error_message)
#         return

# def write_to_file(file_path, visit_data):
#     try:
#         with open(file_path, 'r') as file:
#             data = json.load(file)
#             if not isinstance(data, list):
#                 data = []
#         data.append(visit_data)
#         with open(file_path, 'w') as file:
#             json.dump(data, file, indent=4)
#         print(f"Visit data successfully written to {file_path}")
#     except (FileNotFoundError, json.JSONDecodeError):
#         with open(file_path, 'w') as file:
#             json.dump([visit_data], file, indent=4)
#         print(f"New visit data file created: {file_path}")
#     except Exception as e:
#         error_message = f"Error writing file: {e}"
#         print("Error writing file")
#         logging.error(error_message)
#         return

# def navigate_and_click(driver, task_queue, proxy_ip):
#     global visits
#     visits += 1
#     print("Visit:", visits)
#     gui.update_task_count(visits)
#     clear_cookies(driver)

#     tabs = []
#     clickids = []
#     shuffled_urls = BASE_URLS[:]
#     random.shuffle(shuffled_urls)
#     for base_url in shuffled_urls:
#         success = False
#         attempts = 0

#         while not success and attempts < 10:
#             try:
#                 attempts += 1
#                 print(f"Attempt {attempts} for URL: {base_url}")

#                 driver.execute_script("window.open('');")
#                 driver.switch_to.window(driver.window_handles[-1])
#                 driver.get(base_url)
#                 tabs.append(driver.current_window_handle)

#                 # Wait for page to load and check for sign-in prompt
#                 try:
#                     WebDriverWait(driver, 10).until(
#                         EC.presence_of_element_located((By.TAG_NAME, "body"))
#                     )
#                     # Check for sign-in prompt
#                     sign_in_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign In') or contains(text(), 'Login')]")
#                     if sign_in_elements:
#                         print("Sign-in prompt detected. This may be due to website security or proxy detection.")
#                         logging.warning(f"Sign-in prompt detected on {base_url} with proxy IP {proxy_ip}")
#                         driver.close()
#                         driver.switch_to.window(driver.window_handles[0])
#                         return
#                 except TimeoutException:
#                     print("Page load timed out.")
#                     logging.error(f"Page load timed out for {base_url}")

#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(2)

#                 # Broader XPath for buttons
#                 buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Apply Now') or contains(text(), 'Buy Now') or contains(text(), 'Shop Now') or contains(@class, 'btn') or contains(@class, 'button')]")
#                 if buttons:
#                     chosen_button = random.choice(buttons)
#                     ActionChains(driver).move_to_element(chosen_button).perform()
#                     time.sleep(1)
#                     chosen_button.click()
#                     print("Clicked a random button.")
#                     clickids.append((
#                         f"click_{random.randint(1000, 9999)}",
#                         driver.current_url
#                     ))
#                 else:
#                     print("No actionable buttons found on this page.")
#                     logging.warning(f"No buttons found on {base_url} with proxy IP {proxy_ip}")

#                 success = True

#             except (
#                 WebDriverException,
#                 TimeoutException,
#                 NoSuchElementException,
#                 ElementClickInterceptedException,
#                 ElementNotInteractableException,
#                 StaleElementReferenceException,
#                 JavascriptException,
#                 UnexpectedAlertPresentException,
#                 NoSuchWindowException,
#                 SessionNotCreatedException,
#                 requests.exceptions.RequestException,
#                 socket.gaierror,
#                 socket.timeout,
#                 ConnectionResetError,
#                 ConnectionAbortedError,
#                 ConnectionRefusedError
#             ) as e:
#                 logging.error(f"Error on attempt {attempts} for {base_url}: {e}")
#                 time.sleep(2)

#                 if len(driver.window_handles) > 1:
#                     driver.close()
#                     driver.switch_to.window(driver.window_handles[0])

#         if not success:
#             logging.error(f"Failed to process {base_url} after 10 attempts.")

#     try:
#         min_delay = int(gui.min_delay_entry.get()) if gui.min_delay_entry.get() else 30
#         max_delay = int(gui.max_delay_entry.get()) if gui.max_delay_entry.get() else 45
#     except ValueError:
#         min_delay, max_delay = 30, 45

#     delay_time = random.randint(min_delay, max_delay)
#     print(f"Waiting for {delay_time} seconds...")
#     time.sleep(delay_time)

#     for clickid, full_url in clickids:
#         visit_data = {
#             "visit_number": visits,
#             "clickid": clickid,
#             "url": full_url,
#             "proxy_ip": proxy_ip,
#             "timestamp": datetime.datetime.now().isoformat()
#         }
#         write_to_file("visit_log.json", visit_data)

#     task_queue.put(visits)

# if __name__ == "__main__":
#     root = tk.Tk()
#     gui = WebTaskGUI(root)
#     root.mainloop()






# import requests

# # Your GeoNode Credentials
# PROXY_HOST = "sg.proxy.geonode.io"
# PROXY_PORT = "11000"
# PROXY_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PROXY_PASS = "CHANGE_ME_SECRET"

# proxies = {
#     "http": f"socks5://{PROXY_USER}:CHANGE_ME_PASSWORD@{PROXY_HOST}:{PROXY_PORT}",
#     "https": f"socks5://{PROXY_USER}:CHANGE_ME_PASSWORD@{PROXY_HOST}:{PROXY_PORT}"
# }

# print("🔄 Testing GeoNode Proxy...")

# try:
#     r = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=10)
#     print("\n✅ Proxy Active!")
#     print("Your Proxy IP:", r.json())
# except Exception as e:
#     print("\n❌ Proxy Not Working!")
#     print("Error:", e)




# import requests
# import time
# import random
# import string

# # Your GeoNode Credentials
# PROXY_HOST = "sg.proxy.geonode.io"
# PROXY_PORT = "11000"
# PROXY_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PROXY_PASS = "CHANGE_ME_SECRET"

# # Rotating Proxy Format
# def get_proxy():
#     return {
#         "http": f"socks5://{PROXY_USER}:CHANGE_ME_PASSWORD@{PROXY_HOST}:{PROXY_PORT}",
#         "https": f"socks5://{PROXY_USER}:CHANGE_ME_PASSWORD@{PROXY_HOST}:{PROXY_PORT}"
#     }

# # Random ID generator
# def random_id(length=10):
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# print("🔄 Starting 10 Proxy Visits...\n")

# for i in range(1, 11):
#     try:
#         print(f"🌐 Visit {i}: Changing IP & Calling URL...")

#         proxy = get_proxy()

#         # Generate random clickid and sourceid
#         clickid = random_id()
#         sourceid = random_id()

#         # Final URL with actual values
#         visit_url = f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2={clickid}&sub1={sourceid}"

#         # Step 1: Check Current Proxy IP
#         ip_res = requests.get("https://api.ipify.org?format=json", proxies=proxy, timeout=10)
#         print("🔹 Current Proxy IP:", ip_res.json())

#         # Step 2: Visit Offer URL
#         response = requests.get(visit_url, proxies=proxy, timeout=10)
#         print("✅ URL Visited | Status Code:", response.status_code)
#         print("🔗 URL:", visit_url)

#     except Exception as e:
#         print("❌ Error on Visit:", i)
#         print("Error:", e)

#     print("-----")
#     time.sleep(2)  # delay between visits



# import lorem

# print(lorem.sentence())
# print(lorem.paragraph())
# print(lorem.text())


# from faker import Faker
# fake = Faker()

# print(fake.text())          # random paragraph
# print(fake.sentence())      # random sentence
# print(fake.name())          # random name
# print(fake.address())       # random address


# from textgenrnn import textgenrnn

# textgen = textgenrnn.TextgenRnn()
# textgen.generate(n=3)


# from keytotext import pipeline

# # Model load karo (3 models available: k2t-base, k2t-small, k2t-tiny)
# nlp = pipeline("k2t-base")  # 850 MB download hoga

# # Keywords dedo, sentences mil jayengi
# keywords = ['India', 'cricket', 'world cup']
# result = nlp(keywords)
# print(result)
# # Output: "India won the cricket world cup after a great performance."



# import os
# from groq import Groq
# import httpx

# # API Key set (testing ke liye – production mein env use karo)
# os.environ["GROQ_API_KEY"] = "CHANGE_ME_SECRET"

# # Proxy setup (GeoNode residential)
# def get_proxy_transport():
#     proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#     return httpx.HTTPTransport(proxy=proxy_url)

# # Client init with proxy
# client = Groq(
#     api_key=os.environ["GROQ_API_KEY"],
#     http_client=httpx.Client(transport=get_proxy_transport())
# )

# def generate():
#     try:
#         response = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",  # ← YE UPDATE KIA! Purane ki jagah yeh use karo
#             messages=[{"role": "user", "content": "Ek random desi joke sunao"}],
#             temperature=1.0,  # High for uniqueness
#             max_tokens=200
#         )
#         print("Fresh Content →", response.choices[0].message.content)
#         print("IP badla hoga har baar 🔥")
#     except Exception as e:
#         print(f"Error: {str(e)} – Model check karo ya key renew karo!")

# # 3 baar chala ke dekh lo (har baar fresh + unique)
# generate()
# generate() 
# generate()





# TATA_1LAKH_GROQ_GUI_OPTIMIZED.py ← FINAL BANDWIDTH SAVER EDITION
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from groq import Groq
import httpx
import random
import time
import json
import os
import threading
from datetime import datetime
import sys

# ================== GLOBAL VARIABLES ==================
PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
TARGET_URL = ""
GROQ_API_KEY = "CHANGE_ME_API_KEY"
groq_client = None
is_running = False
total_conversions = 0

# ================== 50 PATRIOTIC PROMPTS ==================
PROMPTS = [
    "As a devoted citizen of this sacred nation, I affirm that",
    "With deep respect for Bharat Mata, I take this vow that",
    "Standing under the glory of our tricolor, I promise that",
    "With the spirit of true patriotism, I commit myself to",
    "As a proud youth of this ancient yet modern nation, I declare that",
    "With my mind awakened and soul inspired by my country, I pledge that",
    "Being a child of this timeless civilization, I promise that",
    "With responsibility towards future generations, I solemnly commit to",
    "As a torchbearer of India's legacy, I take this sacred oath that",
    "With gratitude for my heroes and freedom fighters, I declare that",
    "Being blessed to be born in India, I vow to",
    "With unwavering faith in my country's greatness, I promise that",
    "As a humble servant of this great motherland, I dedicate myself to",
    "With the strength of unity and diversity, I take this pledge that",
    "Today, with courage and determination, I promise that",
    "Inspired by the sacrifices of our brave hearts, I commit to",
    "With integrity in my actions and India in my soul, I vow to",
    "As a nationalist by heart and Indian by birth, I pledge that",
    "With devotion to our culture and constitution, I promise that",
    "As a responsible youth of this land, I dedicate my efforts to",
    "With every beat of my heart supporting India, I declare that",
    "As a citizen shaped by Indian values, I commit that",
    "With hope, pride, and responsibility, I take this vow that",
    "As a guardian of India's future, I promise that",
    "With unity in thought and nation in mind, I pledge that",
    "As a believer in India's destiny, I solemnly declare that",
    "With the blessings of my ancestors, I promise that",
    "As a protector of peace and progress, I commit to",
    "With the dream of a powerful India in sight, I vow to",
    "As a carrier of Indian civilization's light, I pledge that",
    "With devotion to India's growth and harmony, I promise that",
    "As one among 1.4 billion dreamers, I declare that",
    "With courage inspired by our army and martyrs, I commit that",
    "As a citizen who values freedom and responsibility, I promise that",
    "With love and loyalty to my nation, I vow to",
    "As a proud Indian determined to make a difference, I pledge that",
    "With full confidence in my nation's rise, I declare that",
    "As a believer in progress and equality, I promise that",
    "With the goal of a united and prosperous India, I commit to",
    "As a carrier of young India's dreams, I solemnly vow that",
    "With honesty as my guide and patriotism as my strength, I pledge that",
    "As a guardian of justice and democracy, I promise that",
    "With India's honor above everything, I take this oath that",
    "As a citizen devoted to the welfare of my nation, I commit that",
    "With every step guided by India's values, I vow to",
    "As a proud Indian shaping tomorrow, I promise that",
    "With respect for every Indian and love for my country, I declare that",
    "As a believer in India's bright future, I pledge that",
    "With complete dedication to my nation's progress, I commit myself to",
    "As an Indian who values unity, peace and strength, I promise that"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]

RESOLUTIONS = ["1920,1080", "1366,768", "1536,864", "1440,900", "360,800", "414,896", "390,844", "375,812"]
LOG_FILE = "tata_optimized_log.json"

# ================== GROQ CLIENT ==================
def setup_groq_client(api_key):
    global groq_client
    try:
        proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
        transport = httpx.HTTPTransport(proxy=proxy_url)
        client = httpx.Client(transport=transport)
        groq_client = Groq(api_key=api_key, http_client=client)
        return True
    except Exception as e:
        print(f"Groq setup error: {e}")
        return False

# ================== GENERATE PLEDGE ==================
def generate_pledge():
    global groq_client
    starter = random.choice(PROMPTS)
    prompt = f"""
    Complete this pledge in powerful, emotional, and patriotic English (18-28 sentences).
    Start exactly with: "{starter}"
    Make it sound like a real Indian student wrote it — natural, heartfelt, and inspiring.
    Include personal stories, dreams for India, respect for soldiers, farmers, women, etc.
    End with 'Jai Hind', 'Bharat Mata Ki Jai' or 'Vande Mataram'.
    No repetition, no robotic tone.
    """
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.05,
            max_tokens=700,
            top_p=0.95
        )
        pledge = response.choices[0].message.content.strip()
        if not any(end in pledge.lower() for end in ["jai hind", "bharat mata", "vande mataram"]):
            pledge += " Jai Hind! Bharat Mata Ki Jai!"
        return pledge
    except Exception as e:
        print(f"[GROQ ERROR] Using fallback → {e}")
        return f"{starter} I will always stand for unity, progress, and pride of India. I will work hard, respect every Indian, and contribute to making Bharat a global leader. This is my promise to my motherland. Jai Hind! Bharat Mata Ki Jai!"

def generate_mobile():
    return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

def log(data):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []
    logs.append(data)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

# ================== OPTIMIZED WORKER (70% BANDWIDTH SAVE) ==================
def worker(tid, log_callback, status_callback):
    global is_running, total_conversions, TARGET_URL
    
    log_callback(f"[THREAD {tid}] Beast Activated – BANDWIDTH SAVER MODE ON")
    
    while is_running:
        ua = random.choice(USER_AGENTS)
        res = random.choice(RESOLUTIONS)
        
        # === ULTRA BANDWIDTH SAVING OPTIONS ===
        options = Options()
        options.add_argument(f"--user-agent={ua}")
        options.add_argument(f"--window-size={res}")
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-images")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-javascript")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-features=TranslateUI,AudioService")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values": {
                "images": 2, "javascript": 2, "plugins": 2, "popups": 2, "notifications": 2
            }
        })

        # === BLOCK ALL WASTE REQUESTS (IMAGES, CSS, ADS, ANALYTICS) ===
        seleniumwire_options = {
            'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
            'disable_encoding': True,
            'suppress_connection_errors': True,
            'request_interceptors': [(
                lambda request: request.abort() if any(
                    ext in request.url.lower() for ext in 
                    ['.jpg','.jpeg','.png','.gif','.webp','.svg','.css','.woff','.ttf',
                     'analytics','track','pixel','ads','beacon','doubleclick','gtag','facebook']
                ) else None
            )]
        }

        driver = None
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options,
                seleniumwire_options=seleniumwire_options
            )

            driver.get("https://api.ipify.org")
            time.sleep(2)
            ip = driver.find_element(By.TAG_NAME, "body").text.strip()

            driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
            time.sleep(random.randint(10, 16))

            essay = generate_pledge()
            mobile = generate_mobile()

            driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
            driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
            driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            total_conversions += 1
            log_callback(f"[THREAD {tid}] SUCCESS | Words: {len(essay.split())} | IP: {ip} | TOTAL: {total_conversions}")
            status_callback(f"Total Conversions: {total_conversions} | Data Saved: ~70%")

            log({"thread": tid, "no": total_conversions, "time": datetime.now().strftime("%H:%M:%S"), "ip": ip})

            time.sleep(random.randint(10, 18))

        except Exception as e:
            log_callback(f"[THREAD {tid}] ERROR → {str(e)[:100]}")
            time.sleep(12)
        finally:
            if driver:
                driver.quit()

    log_callback(f"[THREAD {tid}] Stopped.")

# ================== GUI CLASS (SAME AS BEFORE) ==================
class TataGroqGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TATA 1 LAKH GROQ BEAST - BANDWIDTH SAVER EDITION")
        self.root.geometry("900x700")
        self.root.configure(bg="#0f0f1e")
        self.root.resizable(True, True)
        self.threads = []
        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="TATA 1 LAKH GROQ BEAST", font=("Arial", 26, "bold"), fg="#ff4757", bg="#0f0f1e")
        title.pack(pady=15)
        subtitle = tk.Label(self.root, text="70%+ Bandwidth Saved | 100% Unique Pledges | Residential Proxy", font=("Arial", 11), fg="#70a1ff", bg="#0f0f1e")
        subtitle.pack()

        # Input Frame
        frame = tk.Frame(self.root, bg="#1e1e2e", padx=30, pady=20)
        frame.pack(pady=10, fill="x")

        tk.Label(frame, text="Target URL:", font=("Arial", 12, "bold"), fg="white", bg="#1e1e2e").grid(row=0, column=0, sticky="w", pady=8)
        self.url_entry = tk.Entry(frame, font=("Arial", 11), width=70, bg="#2f3542", fg="#ffffff", insertbackground="white")
        self.url_entry.grid(row=0, column=1, padx=10, pady=8)
        self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")

        tk.Label(frame, text="Groq API Key:", font=("Arial", 12, "bold"), fg="white", bg="#1e1e2e").grid(row=1, column=0, sticky="w", pady=8)
        self.key_entry = tk.Entry(frame, font=("Arial", 11), width=70, bg="#2f3542", fg="#ffffff", show="*", insertbackground="white")
        self.key_entry.grid(row=1, column=1, padx=10, pady=8)

        tk.Label(frame, text="Threads:", font=("Arial", 12, "bold"), fg="white", bg="#1e1e2e").grid(row=2, column=0, sticky="w", pady=8)
        self.thread_spin = ttk.Spinbox(frame, from_=1, to=15, width=10)
        self.thread_spin.set(8)
        self.thread_spin.grid(row=2, column=1, sticky="w", padx=10, pady=8)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#0f0f1e")
        btn_frame.pack(pady=20)
        self.start_btn = tk.Button(btn_frame, text="START BEAST MODE", font=("Arial", 14, "bold"), bg="#2ed573", fg="black", width=20, height=2, command=self.start_script)
        self.start_btn.pack(side="left", padx=15)
        self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#ff4757", fg="white", width=15, height=2, command=self.stop_script, state="disabled")
        self.stop_btn.pack(side="left", padx=15)

        # Status
        self.status_label = tk.Label(self.root, text="Status: Ready", font=("Arial", 12, "bold"), fg="#70a1ff", bg="#0f0f1e")
        self.status_label.pack(pady=5)

        # Log Box
        log_frame = tk.Frame(self.root, bg="#0f0f1e")
        log_frame.pack(pady=10, padx=30, fill="both", expand=True)
        self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#1e1e2e", fg="#7bed9f", height=18)
        self.log_text.pack(fill="both", expand=True)

        footer = tk.Label(self.root, text="Made with ❤️ for Bharat | Jai Hind!", font=("Arial", 9), fg="#57606f", bg="#0f0f1e")
        footer.pack(pady=10)

    def log_message(self, msg):
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")

    def start_script(self):
        global TARGET_URL, GROQ_API_KEY, is_running
        TARGET_URL = self.url_entry.get().strip()
        GROQ_API_KEY = self.key_entry.get().strip()

        if not TARGET_URL or not GROQ_API_KEY:
            messagebox.showerror("Error", "URL aur API Key daal bhai!")
            return

        if not setup_groq_client(GROQ_API_KEY):
            messagebox.showerror("Error", "Groq API connect nahi hua!")
            return

        is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        threads = int(self.thread_spin.get())
        self.log_message("BEAST MODE ACTIVATED! | BANDWIDTH SAVER ON")
        self.log_message(f"Threads: {threads} | Target: {TARGET_URL[:60]}...")
        self.update_status("Running...")

        for i in range(1, threads + 1):
            t = threading.Thread(target=worker, args=(i, self.log_message, self.update_status), daemon=True)
            t.start()
            self.threads.append(t)
            time.sleep(1.5)

    def stop_script(self):
        global is_running
        is_running = False
        self.log_message("STOPPING ALL THREADS...")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status("Stopped")
        self.threads = []

# ================== MAIN ==================
if __name__ == "__main__":
    root = tk.Tk()
    app = TataGroqGUI(root)
    root.mainloop()

# import random
# import phonenumbers
# from phonenumbers import carrier

# # Indian operators ke REAL prefixes (2025 updated)
# JIO_PREFIXES = [f"7{str(i).zfill(2)}" for i in range(1,100)] + [f"60{str(i).zfill(1)}" for i in range(0,10)] + \
#                ["701","702","703","704","705","706","707","708","709","721","722","723","724","725","726","727","728","729",
#                 "741","742","743","744","745","746","747","748","749","761","762","763","764","765","766","767","768","769",
#                 "781","782","783","784","785","786","787","788","789","791","792","793","794","795","796","797","798","799"]

# AIRTEL_PREFIXES = ["801","802","803","804","805","806","807","808","809","821","822","823","824","825","826","827","828","829",
#                    "831","832","833","834","835","836","837","838","839","851","852","853","854","855","856","857","858","859",
#                    "861","862","863","864","865","866","867","868","869","871","872","873","874","875","876","877","878","879",
#                    "881","882","883","884","885","886","887","888","889","891","892","893","894","895","896","897","898","899"]

# VI_PREFIXES = [f"9{str(i).zfill(2)}" for i in range(0,100)] + \
#               ["900","901","902","903","904","905","906","907","908","909","911","912","913","914","915","916","917","918","919",
#                "920","921","922","923","924","925","926","927","928","929","931","932","933","934","935","936","937","938","939",
#                "941","942","943","944","945","946","947","948","949","950","951","952","953","954","955","956","957","958","959",
#                "961","962","963","964","965","966","967","968","969","971","972","973","974","975","976","977","978","979",
#                "981","982","983","984","985","986","987","988","989","991","992","993","994","995","996","997","998"]

# BSNL_PREFIXES = ["841","842","843","844","845","846","847","848","849","940"]

# ALL_PREFIXES = JIO_PREFIXES + AIRTEL_PREFIXES + VI_PREFIXES + BSNL_PREFIXES

# def is_natural_number(num_str):
#     """Check karta hai ki number fake pattern wala to nahi"""
#     # No 4+ repeated digits
#     if any(char * 4 in num_str for char in "0123456789"):
#         return False
#     # No 5+ sequential digits (12345 ya 98765)
#     seq = "0123456789999999999"
#     if any(seq[i:i+5] in num_str for i in range(len(seq)-4)):
#         return False
#     # No too many same digits (max 3 allowed)
#     if max(num_str.count(c) for c in "0123456789") > 3:
#         return False
#     return True

# def generate_real_indian_mobile():
#     while True:
#         prefix = random.choice(ALL_PREFIXES)
#         suffix = ''.join(random.choices("0123456789", k=7))
#         number = prefix + suffix
        
#         # Final 10-digit number
#         full = "9" + number[-9:] if len(number) > 9 else number
        
#         # Natural feel check
#         if not is_natural_number(full):
#             continue
            
#         # Final validation using phonenumbers library
#         try:
#             parsed = phonenumbers.parse("+91" + full, None)
#             if phonenumbers.is_valid_number(parsed) and phonenumbers.is_possible_number(parsed):
#                 return full
#         except:
#             continue

# # TEST KAR (10 numbers dekh)
# if __name__ == "__main__":
#     print("Real Indian Mobile Numbers (Zero Fake Feel):")
#     for _ in range(15):
#         num = generate_real_indian_mobile()
#         carrier_name = carrier.name_for_number(phonenumbers.parse("+91"+num, "IN"), "en")
#         print(f"{num} → {carrier_name or 'Valid Indian Number'}")