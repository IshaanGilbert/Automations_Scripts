# import os
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# import math
# import traceback
# import json
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import psutil

# # === CONFIGURATION ===
# TARGET_URLS = ["https://www.adidas.co.in/adi_zomato"]
# # TARGET_URLS = ["https://marcadeo.com/"]
# NUM_VISITS = 100 
# CONCURRENCY = 2  # Set to 2 for your test case
# HEADLESS = False
# CHROME_BINARY = os.path.abspath("C:\\traffic_bots\\Chrome\\chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("C:\\traffic_bots\\chromedriver-win64\\chromedriver.exe")
# PROXIES = []
# VIEWPORTS = [(1280, 720), (1366, 768), (1440, 900), (1920, 1080), (1024, 768), (1600, 900)]
# LOCALES = ["en-US", "en-GB", "hi-IN", "es-ES", "fr-FR", "de-DE", "ja-JP", "zh-CN"]
# TIMEZONES = ["Asia/Kolkata", "Europe/London", "America/New_York", "Asia/Tokyo", "Europe/Paris", "Australia/Sydney"]

# ACTIVE_DRIVERS = []
# driver_lock = threading.Lock()  # Add lock for thread safety

# # Setup logging (unchanged)
# log_dir = os.path.dirname(os.path.abspath(__file__))
# os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
# error_log = os.path.join(log_dir, "logs", "error_log.txt")
# info_log = os.path.join(log_dir, "logs", "info_log.txt")
# visit_json = os.path.join(log_dir, "logs", "visit_data.json")
# logging.basicConfig(filename=error_log, level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
# info_logger = logging.getLogger("info")
# info_handler = logging.FileHandler(info_log)
# info_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
# info_logger.addHandler(info_handler)
# info_logger.setLevel(logging.INFO)

# def generate_fingerprinting(session_id):
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

#     viewport = random.choice(VIEWPORTS)  # Reuse VIEWPORTS from config
#     # Generate unique cookie per session
#     cookie_value = hashlib.sha256(f"{session_id}{random.randint(0, 1000000)}".encode()).hexdigest()[:16]
#     return {
#         "session_id": session_id,
#         "device_type": device_type,
#         "os": os,
#         "user_agent": user_agent,
#         "viewport": viewport,
#         "webgl_vendor": random.choice(webgl_vendor),
#         "webgl_renderer": random.choice(webgl_renderer),
#         "language": random.choice(LOCALES),  # Reuse LOCALES from config
#         "timezone": random.choice(timezone),
#         "plugin_list": random.choice(plugin_list),
#         "installed_fonts": random.choice(installed_fonts),
#         "hardware_concurrency": random.choice([4, 8, 12]),
#         "device_memory": random.choice([4, 8]),
#         "canvas_hash": hashlib.sha256(f"{session_id}{random.randint(0, 1000000)}".encode()).hexdigest()[:16],
#         "webgl_hash": hashlib.sha256(f"{session_id}{random.randint(0, 1000000)}".encode()).hexdigest()[:16],
#         "navigator_platform": random.choice(navigator_platform),
#         "do_not_track": random.choice(["1", "0", None]),
#         "screen_width": random.choice(screen_widths),
#         "screen_height": random.choice(screen_heights),
#         "device_pixel_ratio": random.choice(device_pixel_ratio),
#         "accept_language": random.choice(accept_language),
#         "speech_synthesis_voices": random.choice(speech_synthesis_voices),
#         "cookie_value": cookie_value,
#         "app_version": f"{random.randint(90, 120)}.0.0.0",
#         "product_sub": f"2023{random.randint(0, 99)}"
#     }

# def save_visit_data(session_id, user_agent, viewport, fingerprinting, interaction, url, status):
#     visit_data = {
#         "session_id": session_id,
#         "user_agent": user_agent,
#         "viewport": viewport,
#         "fingerprint": fingerprinting,
#         "interaction": interaction,
#         "url": url,
#         "status": status,
#         "timestamp": time.ctime()
#     }
#     with open(visit_json, 'a') as f:
#         f.write(json.dumps(visit_data) + "\n")

# def signal_handler(sig, frame):
#     print("Interrupt received. Closing drivers...")
#     info_logger.info("Interrupt received. Closing all drivers.")
#     for driver in ACTIVE_DRIVERS:
#         try:
#             driver.quit()
#             info_logger.info("Driver closed successfully.")
#         except Exception as e:
#             logging.error(f"Failed to close driver: {e}")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")
#     print("All drivers terminated.")
#     sys.exit(0)

# def spoof_js_script(fingerprinting):
#     voices = [f"{fingerprinting['language'].split('-')[0]} Voice {i}" for i in range(1, random.randint(2, 5))]
#     voices_js_array = "[" + ",".join([f'{{name: "{voice.replace('"', '\\"')}", lang: "{fingerprinting["language"].replace('"', '\\"')}", default: {i == 1}}}' for i, voice in enumerate(voices, 1)]) + "]"
#     return f"""
#     Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#     Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"] or ''}' }});
#     Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
#     Object.defineProperty(navigator, 'plugins', {{ get: () => {json.dumps(fingerprinting["plugin_list"] or [])} }});
#     Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'] }});
#     Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]} }});
#     Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]} }});
#     Object.defineProperty(navigator, 'appVersion', {{ get: () => '{fingerprinting["app_version"]}' }});
#     Object.defineProperty(navigator, 'productSub', {{ get: () => '{fingerprinting["product_sub"]}' }});
#     const getParameter = WebGLRenderingContext.prototype.getParameter;
#     WebGLRenderingContext.prototype.getParameter = function(param) {{
#         if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#         if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#         return getParameter.call(this, param);
#     }};
#     HTMLCanvasElement.prototype.toDataURL = function() {{
#         return 'data:image/png;base64,{fingerprinting["canvas_hash"]}';
#     }};
#     Object.defineProperty(window, 'speechSynthesis', {{
#         get: () => ({{ getVoices: () => JSON.parse('{voices_js_array}') }})
#     }});
#     Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#         return {{ timeZone: '{fingerprinting["timezone"]}' }};
#     }};
#     """

# def human_mouse_move(driver, action, x_start, y_start, x_end, y_end, steps=15):
#     points = []
#     for t in range(steps + 1):
#         t = t / steps
#         x = x_start + (x_end - x_start) * t + random.randint(-30, 30) * math.sin(t * math.pi)
#         y = y_start + (y_end - y_start) * t + random.randint(-30, 30) * math.cos(t * math.pi)
#         points.append((int(x), int(y)))
#     for x, y in points:
#         try:
#             action.move_by_offset(x - action.x, y - action.y).perform()
#             action.x, action.y = x, y
#             time.sleep(random.uniform(0.05, 0.2))
#         except:
#             action.reset_actions()
#     action.reset_actions()

# def simulate_interaction(driver, session_id, fingerprinting, url):
#     action = ActionChains(driver)
#     total_time_spent = 0
#     width = driver.execute_script("return window.innerWidth") or 1200
#     height = driver.execute_script("return window.innerHeight") or 1000
#     action.x, action.y = random.randint(0, width // 2), random.randint(0, height // 2)
#     interaction_log = []

#     try:
#         # Initial delay to simulate page load
#         initial_delay = random.uniform(2, 5)
#         time.sleep(initial_delay)
#         total_time_spent += initial_delay
#         info_logger.info(f"Session #{session_id}: Initial page load delay")
#         interaction_log.append(f"Initial delay: {initial_delay} seconds")

#         # Handle consent if present
#         try:
#             consent_button = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(@class, 'consent')]"))
#             )
#             action.move_to_element(consent_button).pause(random.uniform(0.5, 1)).click().perform()
#             info_logger.info(f"Session #{session_id}: Clicked consent button")
#             print(f"[*] Session #{session_id}: Clicked consent button")
#             time.sleep(random.uniform(1, 2))
#             total_time_spent += random.uniform(1, 2)
#             interaction_log.append("Clicked consent button")
#         except:
#             info_logger.info(f"Session #{session_id}: No consent button found")
#             interaction_log.append("No consent button found")

#         # Fixed 1-2 minute target duration
#         target_duration = random.uniform(60, 120)
#         max_actions = 5  # Limit actions to ensure time fit
#         actions_performed = 0

#         while total_time_spent < target_duration and actions_performed < max_actions:
#             remaining_time = target_duration - total_time_spent
#             if remaining_time < 5:  # Minimum time for next action
#                 break

#             action_type = random.choices(
#                 ["scroll", "click", "hover", "type", "navigate"],
#                 weights=[0.4, 0.3, 0.15, 0.1, 0.05]
#             )[0]

#             if action_type == "scroll":
#                 scroll_type = random.choice(["smooth", "jump"])
#                 if scroll_type == "smooth":
#                     scroll_y = random.randint(200, 600)
#                     driver.execute_script(f"window.scrollBy({{ top: {scroll_y}, behavior: 'smooth' }});")
#                     info_logger.info(f"Session #{session_id}: Smooth scrolled by {scroll_y}px")
#                     print(f"[*] Session #{session_id}: Smooth scrolled by {scroll_y}px")
#                     time.sleep(random.uniform(1, 2))
#                     total_time_spent += random.uniform(1, 2)
#                     interaction_log.append(f"Smooth scroll by {scroll_y}px")
#                 else:
#                     scroll_pos = random.randint(0, int(driver.execute_script("return document.body.scrollHeight") or height))
#                     driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
#                     info_logger.info(f"Session #{session_id}: Jumped to {scroll_pos}px")
#                     print(f"[*] Session #{session_id}: Jumped to {scroll_pos}px")
#                     time.sleep(random.uniform(2, 3))
#                     total_time_spent += random.uniform(2, 3)
#                     interaction_log.append(f"Jumped to {scroll_pos}px")

#             elif action_type == "click":
#                 try:
#                     elements = driver.find_elements(By.XPATH, "//a | //button | //input | //div[not(@role='presentation')]")
#                     if elements:
#                         element = random.choice(elements)
#                         if element.is_displayed() and element.is_enabled():
#                             action.move_to_element(element).pause(random.uniform(0.5, 1)).click().perform()
#                             info_logger.info(f"Session #{session_id}: Clicked {element.tag_name}")
#                             print(f"[*] Session #{session_id}: Clicked {element.tag_name}")
#                             time.sleep(random.uniform(2, 3))
#                             total_time_spent += random.uniform(2, 3)
#                             interaction_log.append(f"Clicked {element.tag_name}")
#                             if random.random() < 0.3:
#                                 driver.back()
#                                 time.sleep(random.uniform(1, 2))
#                                 total_time_spent += random.uniform(1, 2)
#                                 interaction_log.append("Navigated back")
#                 except Exception as e:
#                     logging.error(f"Session #{session_id}: Click error: {e}")

#             elif action_type == "hover":
#                 try:
#                     elements = driver.find_elements(By.XPATH, "//a | //button | //div")
#                     if elements:
#                         element = random.choice(elements)
#                         action.move_to_element(element).pause(random.uniform(1, 2)).perform()
#                         info_logger.info(f"Session #{session_id}: Hovered over {element.tag_name}")
#                         print(f"[*] Session #{session_id}: Hovered over {element.tag_name}")
#                         time.sleep(random.uniform(1, 2))
#                         total_time_spent += random.uniform(1, 2)
#                         interaction_log.append(f"Hovered over {element.tag_name}")
#                 except Exception as e:
#                     logging.error(f"Session #{session_id}: Hover error: {e}")

#             elif action_type == "type":
#                 try:
#                     inputs = driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea | //input[@type='search']")
#                     if inputs:
#                         input_field = random.choice(inputs)
#                         if input_field.is_displayed():
#                             action.move_to_element(input_field).click().perform()
#                             fake_text = "".join(random.choices("abcdefghijklmnopqrstuvwxyz ", k=random.randint(3, 8)))
#                             for char in fake_text:
#                                 input_field.send_keys(char)
#                                 time.sleep(random.uniform(0.1, 0.2))
#                             if random.random() < 0.5:
#                                 input_field.send_keys(Keys.ENTER)
#                             info_logger.info(f"Session #{session_id}: Typed '{fake_text}'")
#                             print(f"[*] Session #{session_id}: Typed '{fake_text}'")
#                             time.sleep(random.uniform(2, 3))
#                             total_time_spent += random.uniform(2, 3)
#                             interaction_log.append(f"Typed '{fake_text}'")
#                 except Exception as e:
#                     logging.error(f"Session #{session_id}: Typing error: {e}")

#             elif action_type == "navigate":
#                 if random.random() < 0.2:
#                     try:
#                         links = driver.find_elements(By.TAG_NAME, "a")
#                         if links:
#                             link = random.choice(links)
#                             if link.is_displayed():
#                                 action.move_to_element(link).pause(random.uniform(0.5, 1)).click().perform()
#                                 info_logger.info(f"Session #{session_id}: Navigated to new page")
#                                 print(f"[*] Session #{session_id}: Navigated to new page")
#                                 time.sleep(random.uniform(3, 4))
#                                 total_time_spent += random.uniform(3, 4)
#                                 interaction_log.append("Navigated to new page")
#                                 if random.random() < 0.5:
#                                     driver.back()
#                                     time.sleep(random.uniform(1, 2))
#                                     total_time_spent += random.uniform(1, 2)
#                                     interaction_log.append("Navigated back")
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Navigation error: {e}")

#             # Bot detection bypass with limited retries
#             if "cf-ray" in driver.page_source or "Akamai" in driver.page_source or "CAPTCHA" in driver.page_source:
#                 retry_count = 0
#                 max_retries = 2
#                 while retry_count < max_retries and ("CAPTCHA" in driver.page_source or "cf-ray" in driver.page_source):
#                     print(f"[!] Session #{session_id}: Bot detection triggered, retry {retry_count + 1}/{max_retries}")
#                     info_logger.info(f"Session #{session_id}: Bot detection triggered, retry {retry_count + 1}")
#                     time.sleep(random.uniform(5, 10))
#                     driver.execute_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
#                     driver.refresh()
#                     time.sleep(random.uniform(3, 5))
#                     total_time_spent += random.uniform(3, 5)
#                     interaction_log.append(f"Bot detection retry {retry_count + 1}")
#                     retry_count += 1
#                     if "CAPTCHA" in driver.page_source:
#                         print(f"[!] Session #{session_id}: CAPTCHA detected after retries, skipping visit")
#                         info_logger.info(f"Session #{session_id}: CAPTCHA detected after retries, visit skipped")
#                         save_visit_data(session_id, fingerprinting["user_agent"], fingerprinting["viewport"], fingerprinting, interaction_log, url, "Bot detected")
#                         return

#             # Ensure minimum think time and enforce exact duration
#             think_time = min(random.uniform(1, 2), target_duration - total_time_spent)
#             time.sleep(think_time)
#             total_time_spent += think_time
#             interaction_log.append(f"Think time: {think_time} seconds")
#             actions_performed += 1

#         # Force exact 60-120 second duration
#         if total_time_spent < target_duration:
#             time.sleep(target_duration - total_time_spent)
#         total_time_spent = target_duration  # Ensure exact match
#         save_visit_data(session_id, fingerprinting["user_agent"], fingerprinting["viewport"], fingerprinting, interaction_log, url, "Loaded successfully")

#     except Exception as e:
#         logging.error(f"Session #{session_id}: Interaction error: {e}")
#         print(f"[!] Session #{session_id}: Interaction error: {e}")
#         logging.error(f"Traceback: {traceback.format_exc()}")
#         save_visit_data(session_id, fingerprinting["user_agent"], fingerprinting["viewport"], fingerprinting, interaction_log, url, "Error")

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     info_logger.info(f"Session #{session_id}: Starting visit to {url}")
#     fingerprinting = generate_fingerprinting(session_id)
#     vp = fingerprinting["viewport"]
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
#     os.makedirs("browser_profiles", exist_ok=True)

#     # Improved cleanup with lock and retry
#     max_cleanup_attempts = 2
#     for attempt in range(max_cleanup_attempts):
#         with driver_lock:
#             os.system("taskkill /F /IM chrome.exe 2>nul")
#             os.system("taskkill /F /IM chromedriver.exe 2>nul")
#             time.sleep(2)
#             if not any("chrome.exe" in p.name() for p in psutil.process_iter() if "chrome" in p.name().lower()):
#                 break
#         if attempt < max_cleanup_attempts - 1:
#             time.sleep(2)

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument(f"--user-agent={fingerprinting['user_agent']}")
#     options.add_argument(f"--lang={fingerprinting['language']}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--no-first-run")
#     options.add_argument("--disable-popup-blocking")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--enable-webgl")
#     options.add_argument("--enable-javascript")
#     options.add_argument("--ignore-certificate-errors")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-notifications")
#     if PROXIES:
#         options.add_argument(f"--proxy-server={random.choice(PROXIES)}")

#     if HEADLESS:
#         options.add_argument("--headless=new")
#         options.add_argument("--disable-gpu")

#     service = Service(CHROMEDRIVER_PATH, log_path=os.path.join(log_dir, "logs", f"chromedriver_{session_id}.log"))

#     try:
#         driver = None
#         max_driver_attempts = 3
#         for attempt in range(max_driver_attempts):
#             try:
#                 with driver_lock:
#                     driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=HEADLESS, version_main=137)
#                 driver.set_window_size(vp[0], vp[1])
#                 driver.execute_script(f"window.resizeTo({vp[0]}, {vp[1]});")
#                 ACTIVE_DRIVERS.append(driver)
#                 info_logger.info(f"Session #{session_id}: Driver created with UA: {fingerprinting['user_agent']}, Viewport: {vp}")
#                 print(f"[*] Session #{session_id}: Created driver with viewport {vp}")
#                 break
#             except Exception as e:
#                 logging.error(f"Session #{session_id}: Driver creation attempt {attempt + 1} failed: {e}")
#                 print(f"[!] Session #{session_id}: Driver creation attempt {attempt + 1} failed: {e}")
#                 if attempt < max_driver_attempts - 1:
#                     time.sleep(5)
#                 else:
#                     raise

#         start_time = time.time()
#         attempts = 0
#         max_attempts = 3
#         success = False

#         while not success and attempts < max_attempts:
#             attempts += 1
#             print(f"[*] Session #{session_id}: Attempt {attempts}/{max_attempts}")
#             try:
#                 driver.get(url)
#                 WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#                 info_logger.info(f"Session #{session_id}: Page loaded successfully")
#                 print(f"[*] Session #{session_id}: Page loaded")

#                 try:
#                     cookie_domain = '.' + url.split('/')[2]
#                     if not cookie_domain.startswith('.'):
#                         cookie_domain = f".{cookie_domain}"
#                     driver.add_cookie({
#                         "name": "session_id",
#                         "value": fingerprinting["cookie_value"],
#                         "domain": cookie_domain,
#                         "path": "/"
#                     })
#                     info_logger.info(f"Session #{session_id}: Cookie set successfully")
#                     print(f"[*] Session #{session_id}: Cookie set")
#                 except Exception as e:
#                     logging.error(f"Session #{session_id}: Failed to set cookie: {e}")
#                     print(f"[!] Session #{session_id}: Failed to set cookie: {e}")

#                 try:
#                     driver.execute_script(spoof_js_script(fingerprinting))
#                     info_logger.info(f"Session #{session_id}: Fingerprint spoofing applied")
#                     print(f"[*] Session #{session_id}: Fingerprint spoofing applied")
#                 except Exception as e:
#                     logging.error(f"Session #{session_id}: Fingerprint spoofing failed: {e}")
#                     print(f"[!] Session #{session_id}: Fingerprint spoofing failed: {e}")

#                 if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#                     print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts})")
#                     info_logger.info(f"Session #{session_id}: Cloudflare challenge detected")
#                     time.sleep(random.uniform(5, 10))
#                     continue

#                 simulate_interaction(driver, session_id, fingerprinting, url)
#                 time.sleep(random.uniform(1, 2))  # Short buffer
#                 print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#                 info_logger.info(f"Session #{session_id}: Completed in {round(time.time() - start_time)} seconds")
#                 success = True

#             except Exception as e:
#                 logging.error(f"Session #{session_id}: Attempt {attempts} failed: {e}")
#                 print(f"[!] Session #{session_id}: Attempt {attempts} failed: {e}")
#                 logging.error(f"Traceback: {traceback.format_exc()}")
#                 if attempts < max_attempts:
#                     driver.quit()
#                     with driver_lock:
#                         driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=HEADLESS, version_main=137)
#                     time.sleep(random.uniform(5, 10))
#                 else:
#                     raise

#         if not success:
#             print(f"[x] Session #{session_id}: Failed after {max_attempts} attempts")
#             info_logger.info(f"Session #{session_id}: Failed after {max_attempts} attempts")

#         if driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#         driver.quit()
#         info_logger.info(f"Session #{session_id}: Driver closed")
#         print(f"[*] Session #{session_id}: Driver closed")

#     except Exception as e:
#         if driver and driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#             driver.quit()
#         logging.error(f"Session #{session_id}: Overall failure: {e}")
#         print(f"[x] Session #{session_id}: Overall failure: {e}")
#         logging.error(f"Traceback: {traceback.format_exc()}")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)
#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe 2>nul")
#     os.system("taskkill /F /IM chromedriver.exe 2>nul")
#     time.sleep(2)  # Wait for cleanup
#     print("Chrome binary:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver:", os.path.exists(CHROMEDRIVER_PATH))

#     # Resource check for scalability
#     def check_resources():
#         cpu_usage = psutil.cpu_percent()
#         memory_usage = psutil.virtual_memory().percent
#         return cpu_usage < 80 and memory_usage < 90

#     start_time = time.time()
#     total_visits = NUM_VISITS
#     completed_visits = 0
#     max_concurrency = min(CONCURRENCY, 6)  # Cap concurrency for stability

#     while completed_visits < total_visits:
#         if not check_resources():
#             print("[!] System resources overloaded, waiting...")
#             time.sleep(30)
#             continue

#         batch_size = min(max_concurrency, total_visits - completed_visits)
#         print(f"[*] Starting batch with {batch_size} visits (Total completed: {completed_visits}/{total_visits})")
#         with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
#             futures = []
#             for _ in range(batch_size):
#                 visit_id = completed_visits + 1
#                 for url in TARGET_URLS:
#                     futures.append(executor.submit(simulate_single_visit, visit_id, url))
#                 completed_visits += 1
            
#             for future in futures:
#                 try:
#                     future.result()
#                 except Exception as e:
#                     print(f"[!] Error in future execution: {e}")
#                     logging.error(f"Future execution failed: {e}")
#                     logging.error(f"Traceback: {traceback.format_exc()}")

#         if completed_visits < total_visits:
#             print(f"[*] Completed {completed_visits}/{total_visits} visits. Pausing before next batch...")
#             time.sleep(random.uniform(5, 10))

#     print(f"[✅] All visits completed in {round(time.time() - start_time, 2)} seconds.")

# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print(f"[x] Main execution failed: {e}")
#         logging.error(f"Main execution failed: {e}")
#         logging.error(f"Traceback: {traceback.format_exc()}")
















# *** server wali
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from fake_useragent import UserAgent
# import time
# import random
# import requests

# # === CONFIGURATION ===
# # TARGET_URL = "https://marcadeo.com/"
# TARGET_URL = "https://www.nike.com/"
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
#     for i in range(100):  # Number of visits
#         print(f"[+] Visit #{i + 1}")
#         visit_website()
#         time.sleep(random.randint(5, 10))


# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from fake_useragent import UserAgent
# import time
# import random
# import requests
# from datetime import datetime

# # === CONFIGURATION ===
# TARGET_URL = "https://www.nike.com/"
# PROXY_LIST_URL = ""  # Optional
# VISIT_DURATION = (40, 60)  # seconds per visit
# HEADLESS = False
# LOG_FILE = "visit_log.txt"  # [LOG]

# def log_visit(data):  # [LOG]
#     with open(LOG_FILE, "a") as f:
#         f.write(f"{datetime.now()} | Visit #{data['visit']} | Proxy: {data['proxy'] or 'None'} | UA: {data['ua']}\n")
#         f.write(f"Status: {data['status']}\n")
#         f.write(f"Details: {data['details']}\n")
#         f.write("-" * 60 + "\n")

# def get_random_proxy():
#     if not PROXY_LIST_URL:
#         return None
#     try:
#         proxy_list = requests.get(PROXY_LIST_URL).text.splitlines()
#         return random.choice(proxy_list).strip()
#     except:
#         return None

# def simulate_user_behavior(driver, actions_log):  # [LOG]
#     try:
#         actions = ActionChains(driver)

#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")

#         for _ in range(random.randint(5, 10)):
#             x = random.randint(0, width - 10)
#             y = random.randint(0, height - 10)
#             actions.move_by_offset(x, y).perform()
#             time.sleep(random.uniform(0.3, 0.9))
#             actions.reset_actions()
#         actions_log.append("Mouse movements")

#         total_height = driver.execute_script("return document.body.scrollHeight")
#         scroll = 0
#         while scroll < total_height:
#             scroll += random.randint(300, 500)
#             driver.execute_script(f"window.scrollTo(0, {scroll})")
#             time.sleep(random.uniform(1.0, 2.0))
#         actions_log.append("Scrolled")

#         clickable_elements = driver.find_elements(By.XPATH, "//a | //button")
#         if clickable_elements:
#             target = random.choice(clickable_elements)
#             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target)
#             time.sleep(random.uniform(1, 2))
#             target.click()
#             actions_log.append("Clicked")
#             time.sleep(random.uniform(5, 10))

#             total_height = driver.execute_script("return document.body.scrollHeight")
#             scroll = 0
#             while scroll < total_height:
#                 scroll += random.randint(300, 600)
#                 driver.execute_script(f"window.scrollTo(0, {scroll})")
#                 time.sleep(random.uniform(1.2, 2.5))
#             actions_log.append("Post-click scroll")

#     except Exception as e:
#         actions_log.append(f"[!] Behavior error: {e}")

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

#     driver = uc.Chrome(options=options, use_subprocess=True, version_main=137)
#     return driver, ua

# def visit_website(visit_num):
#     proxy = get_random_proxy()
#     driver, ua = create_driver(proxy)
#     actions_log = []
#     status = "Success"
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(3, 5))
#         if "403" in driver.title or "Access Denied" in driver.page_source:
#             status = "Bot Detected (403)"
#         spoof_fingerprint(driver)
#         simulate_user_behavior(driver, actions_log)
#         time.sleep(random.randint(*VISIT_DURATION))
#     except Exception as e:
#         status = f"Error: {e}"
#     finally:
#         log_visit({
#             "visit": visit_num,
#             "proxy": proxy,
#             "ua": ua,
#             "status": status,
#             "details": ", ".join(actions_log) if actions_log else "No actions"
#         })  # [LOG]
#         driver.quit()

# # Run loop
# if __name__ == "__main__":
#     for i in range(100):  # Number of visits
#         print(f"[+] Visit #{i + 1}")
#         visit_website(i + 1)
#         time.sleep(random.randint(5, 10))





# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import time, random, uuid, os, logging, requests

# # — CONFIGURATION —
# # TARGET_URL = "https://marcadeo.com/"  # Your target URL
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# VISIT_COUNT = 50                       # Total visits to simulate
# VISIT_DURATION = (40, 60)             # Seconds spent on page per visit
# HEADLESS = True                       

# # Setup logging
# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# # Optional proxy list (one per line): "ip:port"
# PROXY_LIST = []  # Fill with proxies if available

# def get_random_proxy():
#     if not PROXY_LIST:
#         return None
#     return random.choice(PROXY_LIST)

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

#     logging.info(f"Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def simulate_user_behavior(driver):
#     actions = ActionChains(driver)
#     wait = WebDriverWait(driver, 10)

#     # Random mouse movements
#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")
#     for _ in range(random.randint(3, 7)):
#         actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
#         time.sleep(random.uniform(0.2, 0.6))
#         actions.reset_actions()

#     # Scroll and backtrack
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

#     # Click a visible element
#     elems = driver.find_elements(By.XPATH, "//a|//button")
#     visible = [e for e in elems if e.is_displayed()]
#     if visible and random.random() < 0.7:
#         tgt = random.choice(visible)
#         driver.execute_script("arguments[0].scrollIntoView();", tgt)
#         wait.until(EC.element_to_be_clickable(tgt))
#         tgt.click()
#         logging.info("Clicked element")
#         time.sleep(random.uniform(4, 10))

#     # Trigger GA manually
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

#     # dwell time
#     time.sleep(random.uniform(*VISIT_DURATION))

# def visit_once():
#     proxy = get_random_proxy()
#     driver = create_driver(proxy)
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(5)  # Let GA load
#         simulate_user_behavior(driver)
#         logging.info("Visit done — closing browser")
#     except Exception as e:
#         logging.error(f"Error during visit: {e}")
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     for i in range(VISIT_COUNT):
#         logging.info(f"=== Starting visit {i+1} of {VISIT_COUNT} ===")
#         visit_once()
#         time.sleep(random.randint(10, 20))




# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import time, random, uuid, os, logging, requests

# # === CONFIGURATION ===
# # TARGET_URL = "https://marcadeo.com/" 
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# VISIT_COUNT = 30
# VISIT_DURATION = (40, 60)
# HEADLESS = False  # Headless OFF ensures better tracking
# PROXY_LIST = []  # Optional proxy list

# # Logging setup
# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# def get_random_proxy():
#     if not PROXY_LIST:
#         return None
#     return random.choice(PROXY_LIST)

# def spoof_fingerprint(driver):
#     js_scripts = [
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
#         "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});",
#         "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4]});",
#         "Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});",
#         "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});",
#         "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});"
#     ]
#     for script in js_scripts:
#         try:
#             driver.execute_script(script)
#         except:
#             pass

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
    
#     logging.info(f"Starting browser — UA: {ua[:50]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def simulate_user_behavior(driver):
#     actions = ActionChains(driver)
#     wait = WebDriverWait(driver, 10)

#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")

#     # Random mouse movement
#     for _ in range(random.randint(4, 7)):
#         x = random.randint(0, width - 1)
#         y = random.randint(0, height - 1)
#         actions.move_by_offset(x, y).perform()
#         time.sleep(random.uniform(0.3, 0.8))
#         actions.reset_actions()

#     # Scroll with some backtrack (Adobe friendly)
#     scroll_pos = 0
#     total_height = driver.execute_script("return document.body.scrollHeight")
#     for _ in range(random.randint(3, 5)):
#         scroll_pos += random.randint(300, 500)
#         driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
#         time.sleep(random.uniform(1.2, 2.2))
#         if random.random() < 0.3:
#             scroll_pos = max(0, scroll_pos - random.randint(100, 300))
#             driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
#             time.sleep(random.uniform(0.7, 1.2))

#     # Click a visible element (Adobe + GA trigger)
#     try:
#         elements = driver.find_elements(By.XPATH, "//a | //button")
#         visible = [el for el in elements if el.is_displayed()]
#         if visible and random.random() < 0.7:
#             target = random.choice(visible)
#             driver.execute_script("arguments[0].scrollIntoView();", target)
#             wait.until(EC.element_to_be_clickable(target))
#             target.click()
#             logging.info("Clicked a button or link.")
#             time.sleep(random.uniform(4, 8))
#     except Exception as e:
#         logging.warning(f"[!] Click failed: {e}")

#     # Trigger GA manually (like in 2nd script)
#     try:
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'page_view', {
#                     page_title: document.title,
#                     page_location: window.location.href
#                 });
#             }
#         """)
#         logging.info("GA event triggered manually")
#     except:
#         pass

#     # Final scroll after click (helps Adobe)
#     try:
#         scroll_pos = 0
#         total_height = driver.execute_script("return document.body.scrollHeight")
#         while scroll_pos < total_height:
#             scroll_pos += random.randint(200, 400)
#             driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
#             time.sleep(random.uniform(0.8, 1.4))
#     except:
#         pass

#     # Wait total visit duration
#     time.sleep(random.uniform(*VISIT_DURATION))

# def visit_once():
#     proxy = get_random_proxy()
#     driver = create_driver(proxy)
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(4, 6))  # wait for analytics to load
#         spoof_fingerprint(driver)
#         simulate_user_behavior(driver)
#         logging.info("Visit completed.")
#     except Exception as e:  
#         logging.error(f"[!] Visit failed: {e}")
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     for i in range(VISIT_COUNT):
#         logging.info(f"\n=== Visit {i + 1} / {VISIT_COUNT} ===")
#         visit_once()
#         time.sleep(random.randint(10, 20))







# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import time, random, uuid, os, logging, requests

# # === CONFIGURATION ===
# VISIT_COUNT = 30
# VISIT_DURATION = (40, 60)
# HEADLESS = False
# PROXY_LIST = []  # Optional proxy list

# # Logging setup
# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# # === UTM DYNAMIC GENERATOR ===
# def get_target_url():
#     base_url = "https://marcadeo.com/"
#     utm_sources = ['bot', 'user_sim', 'agent_01']
#     utm_mediums = ['automation', 'simulator']
#     utm_campaigns = ['testvisit', 'utm_boosted', 'tracking_demo']

#     source = random.choice(utm_sources)
#     medium = random.choice(utm_mediums)
#     campaign = random.choice(utm_campaigns)

#     utm_url = f"{base_url}?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}"
#     logging.info(f"Using URL: {utm_url}")
#     return utm_url

# def get_random_proxy():
#     if not PROXY_LIST:
#         return None
#     return random.choice(PROXY_LIST)

# def spoof_fingerprint(driver):
#     js_scripts = [
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
#         "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});",
#         "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4]});",
#         "Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});",
#         "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});",
#         "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});"
#     ]
#     for script in js_scripts:
#         try:
#             driver.execute_script(script)
#         except:
#             pass

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

#     logging.info(f"Launching browser with UA: {ua[:50]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def simulate_user_behavior(driver):
#     actions = ActionChains(driver)
#     wait = WebDriverWait(driver, 10)

#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")

#     # Mouse movements
#     for _ in range(random.randint(4, 7)):
#         x = random.randint(0, width - 1)
#         y = random.randint(0, height - 1)
#         actions.move_by_offset(x, y).perform()
#         time.sleep(random.uniform(0.3, 0.8))
#         actions.reset_actions()

#     # Scroll and backtrack
#     scroll_pos = 0
#     total_height = driver.execute_script("return document.body.scrollHeight")
#     for _ in range(random.randint(3, 5)):
#         scroll_pos += random.randint(300, 500)
#         driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
#         time.sleep(random.uniform(1.0, 2.0))
#         if random.random() < 0.3:
#             scroll_pos = max(0, scroll_pos - random.randint(100, 300))
#             driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
#             time.sleep(random.uniform(0.7, 1.2))

#     # Random click
#     try:
#         elements = driver.find_elements(By.XPATH, "//a | //button")
#         visible = [el for el in elements if el.is_displayed()]
#         if visible and random.random() < 0.7:
#             target = random.choice(visible)
#             driver.execute_script("arguments[0].scrollIntoView();", target)
#             wait.until(EC.element_to_be_clickable(target))
#             target.click()
#             logging.info("Clicked an element.")
#             time.sleep(random.uniform(4, 8))
#     except Exception as e:
#         logging.warning(f"[!] Click failed: {e}")

#     # Trigger GA event
#     try:
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'page_view', {
#                     page_title: document.title,
#                     page_location: window.location.href
#                 });
#             }
#         """)
#         logging.info("Triggered GA manual event.")
#     except:
#         pass

#     # Final scroll
#     try:
#         scroll_pos = 0
#         total_height = driver.execute_script("return document.body.scrollHeight")
#         while scroll_pos < total_height:
#             scroll_pos += random.randint(200, 400)
#             driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
#             time.sleep(random.uniform(0.8, 1.4))
#     except:
#         pass

#     time.sleep(random.uniform(*VISIT_DURATION))

# def visit_once():
#     proxy = get_random_proxy()
#     driver = create_driver(proxy)
#     try:
#         url = get_target_url()
#         driver.get(url)
#         time.sleep(random.uniform(4, 6))
#         spoof_fingerprint(driver)
#         simulate_user_behavior(driver)
#         logging.info("Visit completed successfully.")
#     except Exception as e:
#         logging.error(f"[!] Visit failed: {e}")
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     for i in range(VISIT_COUNT):
#         logging.info(f"\n=== Visit {i + 1} / {VISIT_COUNT} ===")
#         visit_once()
#         time.sleep(random.randint(10, 20))






# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from fake_useragent import UserAgent
# import time
# import random
# import requests

# # === CONFIGURATION ===
# BASE_URL = "https://www.adidas.co.in/adi_zomato"
# PROXY_LIST_URL = ""  # Optional
# VISIT_DURATION = (40, 60)  # seconds per visit
# HEADLESS = False

# # Generate URL with UTM tags for GA tracking
# def get_target_url():
#     sources = ["bot", "testscript", "sim"]
#     mediums = ["automation", "visit"]
#     campaigns = ["utm_test", "ga_push"]
#     return f"{BASE_URL}?utm_source={random.choice(sources)}&utm_medium={random.choice(mediums)}&utm_campaign={random.choice(campaigns)}"

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

#         # === GA Trigger (manually send page_view)
#         try:
#             driver.execute_script("""
#                 if (typeof gtag === 'function') {
#                     gtag('event', 'page_view', {
#                         page_title: document.title,
#                         page_location: window.location.href
#                     });
#                 }
#             """)
#         except Exception as e:
#             print("[!] GA event injection error:", e)

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

#     driver = uc.Chrome(options=options, use_subprocess=True, version_main=137)
#     return driver

# def visit_website():
#     proxy = get_random_proxy()
#     driver = create_driver(proxy)
#     try:
#         TARGET_URL = get_target_url()  # <- dynamically built
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
#     for i in range(50):  # Number of visits
#         print(f"[+] Visit #{i + 1}")
#         visit_website()
#         time.sleep(random.randint(5, 10)) 






# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait 
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import time, random, uuid, os, logging, requests 

# # — CONFIGURATION —
# # TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# TARGET_URL = "https://unfilteredgadgets.com/"
# VISIT_COUNT = 50                       # Total visits to simulate
# VISIT_DURATION = (40, 60)             # Seconds spent on page per visit 
# HEADLESS = False 
# REFERRERS = [
#     "https://www.google.com/",
#     "https://www.bing.com/",
#     "https://t.co/",
#     None  # Direct traffic
# ]

# # Setup logging
# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# # Optional proxy list (one per line): "ip:port"
# PROXY_LIST = []  # Fill with proxies if available

# def get_random_proxy():
#     if not PROXY_LIST:
#         return None
#     return random.choice(PROXY_LIST)

# def create_driver(proxy=None):
#     ua = UserAgent().random
#     profile_id = uuid.uuid4()
#     options = uc.ChromeOptions()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")
#     if HEADLESS:
#         options.add_argument("--headless=new")
    
#     # Simulate realistic browser settings
#     options.add_argument("--disable-infobars")
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-notifications")

#     logging.info(f"Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def simulate_user_behavior(driver):
#     actions = ActionChains(driver)
#     wait = WebDriverWait(driver, 15)

#     # Random mouse movements
#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")
#     for _ in range(random.randint(4, 8)):
#         actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
#         time.sleep(random.uniform(0.3, 0.7))
#         actions.reset_actions()

#     # Scroll with realistic behavior
#     total_h = driver.execute_script("return document.body.scrollHeight")
#     pos = 0 
#     for _ in range(random.randint(3, 6)):
#         pos += random.randint(200, 800)
#         pos = min(pos, total_h)
#         driver.execute_script(f"window.scrollTo(0, {pos});")
#         time.sleep(random.uniform(1.5, 2.5))
#         if random.random() < 0.4:
#             pos = max(0, pos - random.randint(100, 400))
#             driver.execute_script(f"window.scrollTo(0, {pos});")
#             time.sleep(random.uniform(0.7, 1.5))

#     # Interact with elements (links, buttons, or inputs)
#     try:
#         interactable = driver.find_elements(By.XPATH, "//a|//button|//input[@type='text']")
#         visible = [e for e in interactable if e.is_displayed() and e.is_enabled()]
#         if visible and random.random() < 0.8:
#             tgt = random.choice(visible)
#             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tgt)
#             wait.until(EC.element_to_be_clickable(tgt))
#             if tgt.tag_name == "input":
#                 tgt.send_keys("sample search " + str(random.randint(1, 1000)))
#                 logging.info("Entered text in input field")
#             else:
#                 tgt.click()
#                 logging.info("Clicked element")
#             time.sleep(random.uniform(3, 8))
#     except Exception as e:
#         logging.warning(f"Interaction error: {e}")

#     # Trigger GA events
#     try:
#         driver.execute_script("""
#             window.dataLayer = window.dataLayer || [];
#             function gtag(){dataLayer.push(arguments);}
#             gtag('js', new Date());
#             gtag('config', 'G-XXXXXXXXXX'); // Replace with actual GA tracking ID if known
#             gtag('event', 'page_view', {
#                 page_title: document.title,
#                 page_location: window.location.href,
#                 page_path: window.location.pathname
#             });
#         """)
#         logging.info("Triggered GA page_view event")
#     except Exception as e:
#         logging.error(f"GA trigger error: {e}")

#     # Simulate additional events for GA
#     try:
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'user_engagement', {
#                     engagement_time_msec: Math.floor(Math.random() * 1000) + 500
#                 });
#             }
#         """)
#         logging.info("Triggered GA user_engagement event")
#     except Exception as e:
#         logging.error(f"GA engagement event error: {e}")

#     # Dwell time
#     time.sleep(random.uniform(*VISIT_DURATION))

# def visit_once():
#     proxy = get_random_proxy()
#     driver = None
#     try:
#         driver = create_driver(proxy)
#         # Set random referrer
#         referrer = random.choice(REFERRERS)
#         if referrer:
#             driver.execute_script(f"Object.defineProperty(document, 'referrer', {{get: function(){{return '{referrer}';}}}});")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(8, 12))  # Extended wait for GA to load
#         simulate_user_behavior(driver)
#         logging.info("Visit completed successfully")
#     except Exception as e:
#         logging.error(f"Error during visit: {e}")
#         if proxy:
#             logging.info("Retrying without proxy...")
#             driver.quit()
#             driver = create_driver()  # Retry without proxy
#             driver.get(TARGET_URL)
#             time.sleep(random.uniform(8, 12))
#             simulate_user_behavior(driver)
#     finally:
#         if driver:
#             driver.quit()

# if __name__ == "__main__":
#     for i in range(VISIT_COUNT):
#         logging.info(f"=== Starting visit {i+1} of {VISIT_COUNT} ===")
#         visit_once()
#         time.sleep(random.randint(15, 25))  # Increased delay between visits  






# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait 
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import time, random, uuid, os, logging, requests
# import threading

# # — CONFIGURATION —
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# VISIT_COUNT = 10                   # Total visits
# VISIT_DURATION = (80, 90)             # Increased to 80-90 seconds
# HEADLESS = False
# MAX_THREADS = 2                       # Run 8 browsers at a time
# REFERRERS = [
#     "https://www.google.com/",
#     "https://www.bing.com/",
#     "https://t.co/",
#     "https://www.facebook.com/",
#     "https://www.instagram.com/",
#     "https://www.duckduckgo.com/",
#     "https://www.yahoo.com/",
#     None
# ]

# # Setup logging
# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# # Proxy list
# PROXY_LIST = []  # Add proxies here

# def get_random_proxy():
#     if not PROXY_LIST:
#         return None
#     return random.choice(PROXY_LIST)

# def create_driver(proxy=None):
#     ua = UserAgent().random
#     profile_id = uuid.uuid4()
#     options = uc.ChromeOptions()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")
#     if HEADLESS:
#         options.add_argument("--headless=new")
    
#     options.add_argument("--disable-infobars")
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-notifications")

#     logging.info(f"Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def simulate_user_behavior(driver):
#     actions = ActionChains(driver)
#     wait = WebDriverWait(driver, 15)

#     # Random mouse movements
#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")
#     for _ in range(random.randint(6, 10)):
#         actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
#         time.sleep(random.uniform(0.5, 1.0))
#         actions.reset_actions()

#     # Scroll with realistic behavior
#     total_h = driver.execute_script("return document.body.scrollHeight")
#     pos = 0
#     for _ in range(random.randint(8, 12)):
#         pos += random.randint(200, 800)
#         pos = min(pos, total_h)
#         driver.execute_script(f"window.scrollTo(0, {pos});")
#         time.sleep(random.uniform(2, 4))
#         if random.random() < 0.4:
#             pos = max(0, pos - random.randint(100, 400))
#             driver.execute_script(f"window.scrollTo(0, {pos});")
#             time.sleep(random.uniform(1, 2))

#     # Interact with multiple elements
#     try:
#         interactable = driver.find_elements(By.XPATH, "//a|//button|//input[@type='text']")
#         visible = [e for e in interactable if e.is_displayed() and e.is_enabled()]
#         for _ in range(random.randint(1, 3)):
#             if visible:
#                 tgt = random.choice(visible)
#                 driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tgt)
#                 wait.until(EC.element_to_be_clickable(tgt))
#                 if tgt.tag_name == "input":
#                     tgt.send_keys("sample search " + str(random.randint(1, 1000)))
#                     logging.info("Entered text in input field")
#                 else:
#                     tgt.click()
#                     logging.info("Clicked element")
#                 time.sleep(random.uniform(5, 10))
#                 visible.remove(tgt)
#     except Exception as e:
#         logging.warning(f"Interaction error: {e}")

#     # Simulate page navigation
#     try:
#         links = driver.find_elements(By.XPATH, "//a[@href]")
#         internal_links = [link for link in links if TARGET_URL in link.get_attribute("href")]
#         if internal_links and random.random() < 0.5:
#             link = random.choice(internal_links)
#             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
#             link.click()
#             logging.info("Navigated to internal page")
#             time.sleep(random.uniform(5, 10))
#     except Exception as e:
#         logging.warning(f"Navigation error: {e}")

#     # Trigger GA events
#     try:
#         driver.execute_script("""
#             window.dataLayer = window.dataLayer || [];
#             function gtag(){dataLayer.push(arguments);}
#             gtag('js', new Date());
#             gtag('config', 'G-XXXXXXXXXX');
#             gtag('event', 'page_view', {
#                 page_title: document.title,
#                 page_location: window.location.href,
#                 page_path: window.location.pathname
#             });
#             gtag('event', 'scroll', {
#                 scroll_depth: '50%'
#             });
#         """)
#         logging.info("Triggered GA page_view and scroll events")
#     except Exception as e:
#         logging.error(f"GA trigger error: {e}")

#     # Simulate engagement time
#     try:
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'user_engagement', {
#                     engagement_time_msec: Math.floor(Math.random() * 10000) + 80000  // 80-90s
#                 });
#             }
#         """)
#         logging.info("Triggered GA user_engagement event")
#     except Exception as e:
#         logging.error(f"GA engagement event error: {e}")

#     # Dwell time
#     time.sleep(random.uniform(*VISIT_DURATION))

# def visit_once():
#     proxy = get_random_proxy()
#     driver = None
#     try:
#         driver = create_driver(proxy)
#         referrer = random.choice(REFERRERS)
#         if referrer:
#             driver.execute_script(f"Object.defineProperty(document, 'referrer', {{get: function(){{return '{referrer}';}}}});")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(8, 12))
#         simulate_user_behavior(driver)
#         logging.info("Visit completed successfully")
#     except Exception as e:
#         logging.error(f"Error during visit: {e}")
#         if proxy:
#             logging.info("Retrying without proxy...")
#             driver.quit()
#             driver = create_driver()
#             driver.get(TARGET_URL)
#             time.sleep(random.uniform(8, 12))
#             simulate_user_behavior(driver)
#     finally:
#         if driver:
#             driver.quit()

# def run_visits_in_thread(visit_count):
#     for i in range(visit_count):
#         logging.info(f"=== Starting visit {i+1} ===")
#         visit_once()
#         time.sleep(random.randint(5, 10))  # Reduced delay for 15-20 hours

# if __name__ == "__main__":
#     threads = []
#     visits_per_thread = VISIT_COUNT // MAX_THREADS
#     for _ in range(MAX_THREADS):
#         thread = threading.Thread(target=run_visits_in_thread, args=(visits_per_thread,))
#         threads.append(thread)
#         thread.start()
    
#     for thread in threads:
#         thread.join()

#     # Handle remaining visits
#     remaining_visits = VISIT_COUNT % MAX_THREADS
#     if remaining_visits:
#         run_visits_in_thread(remaining_visits)







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
# NUM_VISITS = 30
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





# ye wo script h jo server pr run ki thi 4 bot 10000 wale 
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent 
# import time, random, uuid, os, logging, requests

# # — CONFIGURATION —
# # TARGET_URL = "https://marcadeo.com/"  # Your target URL 
# TARGET_URL = "https://www.adidas.co.in/adi_zomato" 
# VISIT_COUNT = 50                       # Total visits to simulate
# VISIT_DURATION = (40, 60)             # Seconds spent on page per visit
# HEADLESS = False                      

# # Setup logging
# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# # Optional proxy list (one per line): "ip:port"
# PROXY_LIST = []  # Fill with proxies if available

# def get_random_proxy():
#     if not PROXY_LIST:
#         return None
#     return random.choice(PROXY_LIST)

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

#     logging.info(f"Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def simulate_user_behavior(driver):
#     actions = ActionChains(driver)
#     wait = WebDriverWait(driver, 10)

#     # Random mouse movements
#     width = driver.execute_script("return window.innerWidth")
#     height = driver.execute_script("return window.innerHeight")
#     for _ in range(random.randint(3, 7)):
#         actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
#         time.sleep(random.uniform(0.2, 0.6))
#         actions.reset_actions()

#     # Scroll and backtrack
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

#     # Click a visible element
#     elems = driver.find_elements(By.XPATH, "//a|//button")
#     visible = [e for e in elems if e.is_displayed()]
#     if visible and random.random() < 0.7:
#         tgt = random.choice(visible)
#         driver.execute_script("arguments[0].scrollIntoView();", tgt)
#         wait.until(EC.element_to_be_clickable(tgt))
#         tgt.click()
#         logging.info("Clicked element")
#         time.sleep(random.uniform(4, 10))

#     # Trigger GA manually
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

#     # dwell time
#     time.sleep(random.uniform(*VISIT_DURATION))

# def visit_once():
#     proxy = get_random_proxy()
#     driver = create_driver(proxy)
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(5)  # Let GA load
#         simulate_user_behavior(driver)
#         logging.info("Visit done — closing browser")
#     except Exception as e:
#         logging.error(f"Error during visit: {e}")
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     for i in range(VISIT_COUNT):
#         logging.info(f"=== Starting visit {i+1} of {VISIT_COUNT} ===")
#         visit_once()
#         time.sleep(random.randint(10, 20))



# jo bad me non headless exe bana kr run ki thi jisse 117 or ga pr 114 aay the wo yhi thi shyd
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time, random, uuid, os, logging

# # --- CONFIGURATION ---
# TARGET_URL = "https://www.adidas.co.in/adi_zomato"
# VISIT_COUNT = 10000
# VISIT_DURATION = (40, 60)
# HEADLESS = True

# # --- SETUP LOGGING ---
# logging.basicConfig(filename="/home/ubuntu/ishan/bot_project/logs/visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# # --- STATIC USER-AGENTS LIST (merged user_agents + more_user_agents) ---
# user_agents = [
#     # First 20-30 (already given above)...
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/85.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 Chrome/80.0.3987.149 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/77.0.3865.75 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/85.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 Chrome/80.0.3987.149 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/77.0.3865.75 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 Chrome/81.0.4044.117 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 Chrome/75.0.3770.142 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 Safari/601.7.7",
#     "Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-G950F) AppleWebKit/537.36 Chrome/78.0.3904.108 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0",
#     "Mozilla/5.0 (iPad; CPU OS 12_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
#     "Mozilla/5.0 (Linux; Android 10; Redmi Note 9 Pro) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.4.8 Safari/602.4.8",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Gecko/20100101 Firefox/74.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/70.0.3538.77 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 7.0; Nexus 6P Build/NBD91L) AppleWebKit/537.36 Chrome/64.0.3282.137 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.3; Win64; x64) Gecko/20100101 Firefox/60.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 Chrome/65.0.3325.181 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 Mobile/15E148",
#     "Mozilla/5.0 (Linux; Android 8.1.0; Infinix X608) AppleWebKit/537.36 Chrome/71.0.3578.99 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; ARM; Surface Duo) AppleWebKit/537.36 Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.34",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 Chrome/63.0.3239.132 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 6.0.1; SM-J500F) AppleWebKit/537.36 Chrome/79.0.3945.93 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 5.1; rv:52.0) Gecko/20100101 Firefox/52.0",
#     "Mozilla/5.0 (iPad; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 Mobile/13G36",
#     "Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 Chrome/76.0.3809.132 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/78.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0",
#     "Mozilla/5.0 (Linux; Android 7.1.1; Moto G (5S)) AppleWebKit/537.36 Chrome/81.0.4044.138 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 Chrome/77.0.3865.90 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2 like Mac OS X) AppleWebKit/604.4.7 Mobile/15C114",
#     "Mozilla/5.0 (X11; Linux i686; rv:65.0) Gecko/20100101 Firefox/65.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0",
#     "Mozilla/5.0 (Linux; Android 10; SM-M315F) AppleWebKit/537.36 Chrome/85.0.4183.101 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 Chrome/80.0.3987.87 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 7.0; LG-H870) AppleWebKit/537.36 Chrome/72.0.3626.121 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 Chrome/60.0.3112.113 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 Mobile/13F69",
#     "Mozilla/5.0 (Windows NT 10.0; x64) AppleWebKit/537.36 Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62",
#     "Mozilla/5.0 (Linux; Android 8.1.0; vivo 1803) AppleWebKit/537.36 Chrome/76.0.3809.111 Mobile Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/69.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 Chrome/49.0.2623.112 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 9; Nokia 6.1) AppleWebKit/537.36 Chrome/72.0.3626.121 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
#     "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 Mobile/15A5341f",
#     "Mozilla/5.0 (Linux; Android 6.0.1; Moto G4) AppleWebKit/537.36 Chrome/73.0.3683.90 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 Chrome/72.0.3626.96 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:70.0) Gecko/20100101 Firefox/70.0",
#     "Mozilla/5.0 (Linux; Android 10; SM-A107F) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 Chrome/73.0.3683.75 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
#     "Mozilla/5.0 (Linux; Android 7.0; SM-J730GM) AppleWebKit/537.36 Chrome/80.0.3987.132 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/113.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 Chrome/89.0.4389.82 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/92.0.4515.131 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 Chrome/87.0.4280.88 Safari/537.36",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Gecko/20100101 Firefox/89.0",
#     "Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 Chrome/91.0.4472.124 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 Chrome/87.0.4280.141 Safari/537.36",
#     "Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/93.0.4577.82 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 Chrome/88.0.4324.182 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 Chrome/92.0.4515.107 Mobile Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/94.0",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 Chrome/91.0.4472.77 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 Safari/605.1.15",
#     "Mozilla/5.0 (Linux; Android 9; Redmi Note 8) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36",
# ]

# # --- PROXY LIST (OPTIONAL) ---
# PROXY_LIST = []  # Fill if needed

# def get_random_proxy():
#     return random.choice(PROXY_LIST) if PROXY_LIST else None

# # def create_driver(proxy=None):
# #     ua = random.choice(user_agents)
# #     profile_id = uuid.uuid4()
# #     options = uc.ChromeOptions()
# #     options.add_argument(f"--user-agent={ua}")
# #     options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
# #     options.add_argument("--disable-blink-features=AutomationControlled")
# #     options.add_argument("--no-sandbox")
# #     if proxy:
# #         options.add_argument(f"--proxy-server=http://{proxy}")
# #     if HEADLESS:
# #         options.add_argument("--headless=new")
# #     logging.info(f"Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
# #     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def create_driver(proxy=None):
#     ua = random.choice(user_agents)
#     profile_id = uuid.uuid4()
#     options = uc.ChromeOptions()
#     options.add_argument(f"--user-agent={ua}")
#     if not HEADLESS:
#         options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--start-maximized")
#     options.add_argument("--window-size=1920,1080")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--use-fake-ui-for-media-stream")
#     options.add_argument("--use-fake-device-for-media-stream")
#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")
#     if HEADLESS:
#         options.add_argument("--headless=chrome")
#     logging.info(f"Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)


# # def simulate_user_behavior(driver):
# #     actions = ActionChains(driver)
# #     wait = WebDriverWait(driver, 10)

# #     # Mouse move
# #     width = driver.execute_script("return window.innerWidth")
# #     height = driver.execute_script("return window.innerHeight")
# #     for _ in range(random.randint(3, 7)):
# #         actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
# #         time.sleep(random.uniform(0.2, 0.6))
# #         actions.reset_actions()

# #     # Scroll
# #     total_h = driver.execute_script("return document.body.scrollHeight")
# #     pos = 0
# #     for _ in range(random.randint(3, 5)):
# #         pos += random.randint(200, 600)
# #         driver.execute_script(f"window.scrollTo(0, {pos});")
# #         time.sleep(random.uniform(1, 2))
# #         if random.random() < 0.3:
# #             pos = max(0, pos - random.randint(100, 300))
# #             driver.execute_script(f"window.scrollTo(0, {pos});")
# #             time.sleep(random.uniform(0.5, 1.2))

# #     # Click
# #     elems = driver.find_elements(By.XPATH, "//a|//button")
# #     visible = [e for e in elems if e.is_displayed()]
# #     if visible and random.random() < 0.7:
# #         tgt = random.choice(visible)
# #         driver.execute_script("arguments[0].scrollIntoView();", tgt)
# #         wait.until(EC.element_to_be_clickable(tgt))
# #         tgt.click()
# #         logging.info("Clicked element")
# #         time.sleep(random.uniform(4, 10))

# #     # Simulate GA
# #     try:
# #         driver.execute_script("""
# #             if (typeof gtag === 'function') {
# #                 gtag('event', 'page_view', {
# #                   page_title: document.title,
# #                   page_location: window.location.href
# #                 });
# #             }
# #         """)
# #     except:
# #         pass

# #     time.sleep(random.uniform(*VISIT_DURATION))

# def simulate_user_behavior(driver):
#     wait = WebDriverWait(driver, 10)
#     actions = ActionChains(driver)

#     # Patch common headless detection methods
#     driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#         "source": """
#             Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
#             Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4] });
#             Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
#             window.chrome = { runtime: {} };
#             const originalQuery = window.navigator.permissions.query;
#             window.navigator.permissions.query = (parameters) =>
#                 parameters.name === 'notifications'
#                     ? Promise.resolve({ state: Notification.permission })
#                     : originalQuery(parameters);
#         """
#     })

#     time.sleep(random.uniform(3, 6))  # Let JS analytics load

#     # Mouse move simulation
#     try:
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")
#         for _ in range(random.randint(3, 7)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             actions.move_by_offset(x, y).perform()
#             time.sleep(random.uniform(0.3, 0.7))
#             actions.reset_actions()
#     except Exception as e:
#         logging.warning(f"Mouse move failed: {e}")

#     # Scroll simulation
#     try:
#         total_h = driver.execute_script("return document.body.scrollHeight")
#         pos = 0
#         for _ in range(random.randint(4, 6)):
#             pos += random.randint(200, 500)
#             driver.execute_script(f"window.scrollTo(0, {pos});")
#             time.sleep(random.uniform(1.0, 2.5))
#             if random.random() < 0.3:
#                 pos = max(0, pos - random.randint(100, 300))
#                 driver.execute_script(f"window.scrollTo(0, {pos});")
#                 time.sleep(random.uniform(0.5, 1.2))
#     except Exception as e:
#         logging.warning(f"Scroll failed: {e}")

#     # Click a visible element (optional interaction)
#     try:
#         elems = driver.find_elements(By.XPATH, "//a|//button")
#         visible = [e for e in elems if e.is_displayed() and e.size['height'] > 0]
#         if visible and random.random() < 0.7:
#             tgt = random.choice(visible)
#             driver.execute_script("arguments[0].scrollIntoView();", tgt)
#             wait.until(EC.element_to_be_clickable(tgt))
#             tgt.click()
#             logging.info("Clicked a visible element")
#             time.sleep(random.uniform(5, 10))
#     except Exception as e:
#         logging.warning(f"Click failed: {e}")

#     # Simulate Google Analytics call
#     try:
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'page_view', {
#                   page_title: document.title,
#                   page_location: window.location.href
#                 });
#             }
#         """)
#     except Exception as e:
#         logging.warning(f"GA tracking simulation failed: {e}")

#     time.sleep(random.uniform(*VISIT_DURATION))

# def visit_once():
#     proxy = get_random_proxy()
#     driver = create_driver(proxy)
#     try:
#         driver.get(TARGET_URL)
#         time.sleep(5)  # Let GA load
#         simulate_user_behavior(driver)
#         logging.info("Visit done — closing browser")
#     except Exception as e:
#         logging.error(f"Error during visit: {e}")
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     for i in range(VISIT_COUNT):
#         logging.info(f"=== Starting visit {i+1} of {VISIT_COUNT} ===")
#         visit_once()
#         time.sleep(random.randint(10, 20))


#  tail -f /home/ubuntu/ishan/bot_project/logs/visit_log.txt 





# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC 
# from fake_useragent import UserAgent
# import time, random, uuid, os, logging, requests

# # — CONFIGURATION —
# TARGET_URL = "https://marcadeo.com/"
# VISIT_COUNT = 10000                       # Total visits to simulate
# VISIT_DURATION = (40, 60)             # Seconds spent on page per visit
# HEADLESS = False
# REFERRERS = [
#     "https://www.google.com/",
#     "https://www.bing.com/",
#     "https://t.co/",
#     None  # Direct traffic
# ]

# # Setup logging
# logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# # Optional proxy list (one per line): "ip:port"
# PROXY_LIST = []  # Fill with proxies if available

# def get_random_proxy():
#     if not PROXY_LIST:
#         return None
#     return random.choice(PROXY_LIST)

# # def create_driver(proxy=None):
# #     ua = UserAgent().random
# #     profile_id = uuid.uuid4()
# #     options = uc.ChromeOptions()
# #     options.add_argument(f"--user-agent={ua}")
# #     options.add_argument(f"--user-data-dir=/tmp/chrome_profile_{profile_id}")
# #     options.add_argument("--disable-blink-features=AutomationControlled")
# #     options.add_argument("--no-sandbox")
# #     options.add_argument("--disable-dev-shm-usage")
# #     if proxy:
# #         options.add_argument(f"--proxy-server=http://{proxy}")
# #     if HEADLESS:
# #         options.add_argument("--headless=new")

# #     # Simulate realistic browser settings
# #     options.add_argument("--disable-infobars")
# #     options.add_argument("--start-maximized")
# #     options.add_argument("--disable-notifications")

# #     logging.info(f"Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
# #     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# def create_driver(proxy=None):
#     ua = UserAgent().random  # ✅ Correct usage
#     profile_id = uuid.uuid4()
#     options = uc.ChromeOptions()
#     options.add_argument(f"--user-agent={ua}")
#     if not HEADLESS:
#         options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--start-maximized")
#     options.add_argument("--window-size=1920,1080")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--use-fake-ui-for-media-stream")
#     options.add_argument("--use-fake-device-for-media-stream")
#     if proxy:
#         options.add_argument(f"--proxy-server=http://{proxy}")
#     if HEADLESS:
#         options.add_argument("--headless=chrome")
#     logging.info(f"Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
#     return uc.Chrome(options=options, use_subprocess=True, version_main=137)

# # def simulate_user_behavior(driver):
# #     actions = ActionChains(driver)
# #     wait = WebDriverWait(driver, 15)

# #     # Random mouse movements
# #     width = driver.execute_script("return window.innerWidth")
# #     height = driver.execute_script("return window.innerHeight")
# #     for _ in range(random.randint(4, 8)):
# #         actions.move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
# #         time.sleep(random.uniform(0.3, 0.7))
# #         actions.reset_actions()

# #     # Scroll with realistic behavior
# #     total_h = driver.execute_script("return document.body.scrollHeight")
# #     pos = 0
# #     for _ in range(random.randint(3, 6)):
# #         pos += random.randint(200, 800)
# #         pos = min(pos, total_h)
# #         driver.execute_script(f"window.scrollTo(0, {pos});")
# #         time.sleep(random.uniform(1.5, 2.5))
# #         if random.random() < 0.4:
# #             pos = max(0, pos - random.randint(100, 400))
# #             driver.execute_script(f"window.scrollTo(0, {pos});")
# #             time.sleep(random.uniform(0.7, 1.5))

# #     # Interact with elements (links, buttons, or inputs)
# #     try:
# #         interactable = driver.find_elements(By.XPATH, "//a|//button|//input[@type='text']")
# #         visible = [e for e in interactable if e.is_displayed() and e.is_enabled()]
# #         if visible and random.random() < 0.8:
# #             tgt = random.choice(visible)
# #             driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tgt)
# #             wait.until(EC.element_to_be_clickable(tgt))
# #             if tgt.tag_name == "input":
# #                 tgt.send_keys("sample search " + str(random.randint(1, 1000)))
# #                 logging.info("Entered text in input field")
# #             else:
# #                 tgt.click()
# #                 logging.info("Clicked element")
# #             time.sleep(random.uniform(3, 8))
# #     except Exception as e:
# #         logging.warning(f"Interaction error: {e}")

# #     # Trigger GA events
# #     try:
# #         driver.execute_script("""
# #             window.dataLayer = window.dataLayer || [];
# #             function gtag(){dataLayer.push(arguments);}
# #             gtag('js', new Date());
# #             gtag('config', 'G-XXXXXXXXXX'); // Replace with actual GA tracking ID if known
# #             gtag('event', 'page_view', {
# #                 page_title: document.title,
# #                 page_location: window.location.href,
# #                 page_path: window.location.pathname
# #             });
# #         """)
# #         logging.info("Triggered GA page_view event")
# #     except Exception as e:
# #         logging.error(f"GA trigger error: {e}")

# #     # Simulate additional events for GA
# #     try:
# #         driver.execute_script("""
# #             if (typeof gtag === 'function') {
# #                 gtag('event', 'user_engagement', {
# #                     engagement_time_msec: Math.floor(Math.random() * 1000) + 500
# #                 });
# #             }
# #         """)
# #         logging.info("Triggered GA user_engagement event")
# #     except Exception as e:
# #         logging.error(f"GA engagement event error: {e}")

# #     # Dwell time
# #     time.sleep(random.uniform(*VISIT_DURATION))

# def simulate_user_behavior(driver):
#     wait = WebDriverWait(driver, 10)
#     actions = ActionChains(driver)

#     # Patch common headless detection methods
#     driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#         "source": """
#             Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
#             Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4] });
#             Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
#             window.chrome = { runtime: {} };
#             const originalQuery = window.navigator.permissions.query;
#             window.navigator.permissions.query = (parameters) =>
#                 parameters.name === 'notifications'
#                     ? Promise.resolve({ state: Notification.permission })
#                     : originalQuery(parameters);
#         """
#     })

#     time.sleep(random.uniform(3, 6))  # Let JS analytics load

#     # Mouse move simulation
#     try:
#         width = driver.execute_script("return window.innerWidth")
#         height = driver.execute_script("return window.innerHeight")
#         for _ in range(random.randint(3, 7)):
#             x = random.randint(0, width)
#             y = random.randint(0, height)
#             actions.move_by_offset(x, y).perform()
#             time.sleep(random.uniform(0.3, 0.7))
#             actions.reset_actions()
#     except Exception as e:
#         logging.warning(f"Mouse move failed: {e}")

#     # Scroll simulation
#     try:
#         total_h = driver.execute_script("return document.body.scrollHeight")
#         pos = 0
#         for _ in range(random.randint(4, 6)):
#             pos += random.randint(200, 500)
#             driver.execute_script(f"window.scrollTo(0, {pos});")
#             time.sleep(random.uniform(1.0, 2.5))
#             if random.random() < 0.3:
#                 pos = max(0, pos - random.randint(100, 300))
#                 driver.execute_script(f"window.scrollTo(0, {pos});")
#                 time.sleep(random.uniform(0.5, 1.2))
#     except Exception as e:
#         logging.warning(f"Scroll failed: {e}")

#     # Click a visible element (optional interaction)
#     try:
#         elems = driver.find_elements(By.XPATH, "//a|//button")
#         visible = [e for e in elems if e.is_displayed() and e.size['height'] > 0]
#         if visible and random.random() < 0.7:
#             tgt = random.choice(visible)
#             driver.execute_script("arguments[0].scrollIntoView();", tgt)
#             wait.until(EC.element_to_be_clickable(tgt))
#             tgt.click()
#             logging.info("Clicked a visible element")
#             time.sleep(random.uniform(5, 10))
#     except Exception as e:
#         logging.warning(f"Click failed: {e}")

#     # Simulate Google Analytics call
#     try:
#         driver.execute_script("""
#             if (typeof gtag === 'function') {
#                 gtag('event', 'page_view', {
#                   page_title: document.title,
#                   page_location: window.location.href
#                 });
#             }
#         """)
#     except Exception as e:
#         logging.warning(f"GA tracking simulation failed: {e}")

#     time.sleep(random.uniform(*VISIT_DURATION))

# def visit_once():
#     proxy = get_random_proxy()
#     driver = None
#     try:
#         driver = create_driver(proxy)
#         # Set random referrer
#         referrer = random.choice(REFERRERS)
#         if referrer:
#             driver.execute_script(f"Object.defineProperty(document, 'referrer', {{get: function(){{return '{referrer}';}}}});")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(8, 12))  # Extended wait for GA to load
#         simulate_user_behavior(driver)
#         logging.info("Visit completed successfully")
#     except Exception as e:
#         logging.error(f"Error during visit: {e}")
#         if proxy:
#             logging.info("Retrying without proxy...")
#             driver.quit()
#             driver = create_driver()  # Retry without proxy
#             driver.get(TARGET_URL)
#             time.sleep(random.uniform(8, 12))
#             simulate_user_behavior(driver)
#     finally:
#         if driver:
#             driver.quit()

# if __name__ == "__main__":
#     for i in range(VISIT_COUNT):
#         logging.info(f"=== Starting visit {i+1} of {VISIT_COUNT} ===")
#         visit_once()
#         time.sleep(random.randint(15, 25))  # Increased delay between visits




import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import time, random, uuid, os, logging

# — CONFIGURATION —
TARGET_URL = "https://www.adidas.co.in/adi_zomato"
VISIT_COUNT = 10000
VISIT_DURATION = (40, 60)
HEADLESS = False
REFERRERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://t.co/",
    None
]

# Setup logging
logging.basicConfig(filename="visit_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Optional proxy list
PROXY_LIST = []  # Fill with proxies if needed

def get_random_proxy():
    if not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)

def create_driver(proxy=None):
    try:
        ua = UserAgent().random
    except:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

    profile_id = uuid.uuid4()
    options = uc.ChromeOptions()
    options.add_argument(f"--user-agent={ua}")
    if not HEADLESS:
        options.add_argument(f"--user-data-dir=C:/temp/chrome_profile_{profile_id}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--use-fake-device-for-media-stream")
    if proxy:
        options.add_argument(f"--proxy-server=http://{proxy}")
    if HEADLESS:
        options.add_argument("--headless=chrome")

    logging.info(f"Creating browser — UA: {ua[:40]}..., Proxy: {proxy}")
    return uc.Chrome(options=options, use_subprocess=True, version_main=137)

def simulate_user_behavior(driver):
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    # Patch common headless detection techniques
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) =>
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : originalQuery(parameters);
        """
    })

    time.sleep(random.uniform(3, 6))  # Let analytics load

    # Simulate mouse movement
    try:
        width = driver.execute_script("return window.innerWidth")
        height = driver.execute_script("return window.innerHeight")
        for _ in range(random.randint(3, 7)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            actions.move_by_offset(x, y).perform()
            time.sleep(random.uniform(0.3, 0.7))
            actions.reset_actions()
    except Exception as e:
        logging.warning(f"Mouse move failed: {e}")

    # Simulate scrolling
    try:
        total_h = driver.execute_script("return document.body.scrollHeight")
        pos = 0
        for _ in range(random.randint(4, 6)):
            pos += random.randint(200, 500)
            driver.execute_script(f"window.scrollTo(0, {pos});")
            time.sleep(random.uniform(1.0, 2.5))
            if random.random() < 0.3:
                pos = max(0, pos - random.randint(100, 300))
                driver.execute_script(f"window.scrollTo(0, {pos});")
                time.sleep(random.uniform(0.5, 1.2))
    except Exception as e:
        logging.warning(f"Scroll failed: {e}")

    # Click a visible element
    try:
        elems = driver.find_elements(By.XPATH, "//a|//button")
        visible = [e for e in elems if e.is_displayed() and e.size['height'] > 0]
        if visible and random.random() < 0.7:
            tgt = random.choice(visible)
            driver.execute_script("arguments[0].scrollIntoView();", tgt)
            wait.until(EC.element_to_be_clickable(tgt))
            tgt.click()
            logging.info("Clicked a visible element")
            time.sleep(random.uniform(5, 10))
    except Exception as e:
        logging.warning(f"Click failed: {e}")

    # Simulate GA tracking
    try:
        driver.execute_script("""
            if (typeof gtag === 'function') {
                gtag('event', 'page_view', {
                    page_title: document.title,
                    page_location: window.location.href
                });
            }
        """)
    except Exception as e:
        logging.warning(f"GA tracking simulation failed: {e}")

    # Stay on page
    time.sleep(random.uniform(*VISIT_DURATION))

def visit_once():
    proxy = get_random_proxy()
    driver = None
    try:
        driver = create_driver(proxy)
        referrer = random.choice(REFERRERS)
        if referrer:
            driver.execute_script(f"""
                Object.defineProperty(document, 'referrer', {{
                    get: function() {{ return '{referrer}'; }}
                }});
            """)
        driver.get(TARGET_URL)
        time.sleep(random.uniform(8, 12))
        simulate_user_behavior(driver)
        logging.info("Visit completed successfully")
    except Exception as e:
        logging.error(f"Error during visit: {e}")
        if proxy:
            logging.info("Retrying without proxy...")
            driver.quit()
            driver = create_driver()
            driver.get(TARGET_URL)
            time.sleep(random.uniform(8, 12))
            simulate_user_behavior(driver)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    for i in range(VISIT_COUNT):
        logging.info(f"=== Starting visit {i + 1} of {VISIT_COUNT} ===")
        visit_once()
        time.sleep(random.randint(15, 25))