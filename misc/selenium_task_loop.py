# import os 
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import json
# import shutil

# # === CONFIGURATION ===
# TARGET_URLS = [
#     "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 10000  # Changed to 10,000 visits
# CONCURRENCY = 2  # Increased concurrency for faster processing, but kept reasonable to avoid crashes
# BATCH_SIZE = 2  # Process visits in batches to manage resources
# BATCH_DELAY = 10  # Delay between batches to avoid overwhelming the system
# HEADLESS = False  # Changed to True for efficiency with high volume
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864), (800, 600),
#     (360, 640), (375, 667), (414, 896), (412, 915),  # Added more mobile viewports
# ]
# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR",
#     "ja-JP", "zh-CN", "ru-RU", "ar-SA"  # Expanded locale options
# ]
# TIMEZONES = [
#     "Asia/Kolkata", "Europe/London", "America/New_York", "Australia/Sydney",
#     "Asia/Tokyo", "Europe/Paris", "America/Los_Angeles", "Africa/Johannesburg",
#     "Asia/Dubai"  # Expanded timezone options
# ]

# ACTIVE_DRIVERS = []
# ua_generator = UserAgent()
# VISIT_STATS = {"successful": 0, "failed": 0}  # Added to track visit success/failure

# # Setup logging
# log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_log.txt")
# logging.basicConfig(
#     filename=log_path,
#     level=logging.DEBUG,  # Changed to DEBUG for detailed logging
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )

# def generate_fingerprinting(session_id):
#     # Enhanced fingerprinting to ensure uniqueness for each visit
#     device_os_mapping = {
#         "desktop": ["Windows", "macOS", "Linux", "Fedora"],
#         "laptop": ["Windows", "macOS", "Linux", "ChromeOS", "Fedora"],
#         "ultrabook": ["Windows", "macOS", "Linux", "Fedora"],
#         "macbook": ["macOS"],
#         "chromebook": ["ChromeOS"],
#         "smartphone": ["Android", "iOS"],
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
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64; rv:{3}.0) Gecko/20100101 Firefox/{3}.0",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "Fedora": [
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:{3}.0) Gecko/20100101 Firefox/{3}.0",
#         ],
#         "iPadOS": [
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.0 Safari/{2}.36",
#         ],
#         "macOS": [
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Safari/{3}.0",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}; rv:{3}.0) Gecko/20100101 Firefox/{3}.0",
#         ],
#         "Linux": [
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:{3}.0) Gecko/20100101 Firefox/{3}.0",
#         ],
#         "Android": [
#             "Mozilla/5.0 (Linux; Android {0}.{1}; SM-G950F Build/{5}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Pixel 4 Build/{5}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
#         ],
#         "iOS": [
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.0 Mobile/{4} Safari/{2}.36",
#         ],
#         "ChromeOS": [
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "Tizen": [
#             "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0 Safari/{2}.36",
#         ],
#         "Android TV": [
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#         ],
#         "WebOS": [
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.1 Safari/{2}.36",
#         ],
#     }

#     device_type = random.choice(list(device_os_mapping.keys()))
#     os = random.choice(device_os_mapping[device_type])
#     version_main = random.randint(10, 15)  # Updated for modern OS versions
#     version_minor = random.randint(0, 4)
#     webkit_version = random.randint(537, 605)
#     chrome_version = random.randint(100, 137) # Updated for recent Chrome versions
#     firefox_version = random.randint(90, 115)
#     build_version = random.randint(1000, 5000)
#     build_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))  # Added unique build ID for Android
#     user_agent = random.choice(user_agents[os]).format(
#         version_main, version_minor, webkit_version, chrome_version, firefox_version, build_id
#     )
#     screen_widths = [1024, 1366, 1440, 1920, 2560, 3840, 360, 412, 414, 390, 428]  # Added more mobile resolutions
#     screen_heights = [768, 800, 900, 1080, 1200, 1600, 640, 667, 896, 915, 720]
#     device_pixel_ratio = [1, 1.25, 1.5, 2, 2.25, 2.5, 3, 3.5]  # Added more pixel ratios
#     webgl_renderer = [
#         "ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)",
#         "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
#         "ANGLE (AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0)",
#     ]
#     webgl_vendor = ["Google Inc. (NVIDIA)", "Google Inc. (Intel)", "Google Inc. (AMD)"]
#     plugin_list = [
#         ["Chrome PDF Plugin", "Widevine Content Decryption Module", "Shockwave Flash"],
#         ["PDF Viewer", "Native Client"],
#         ["Java", "Silverlight", "QuickTime"],
#     ]
#     installed_fonts = [
#         ["Arial", "Helvetica", "Times New Roman", "Calibri"],
#         ["Roboto", "Open Sans", "Lato", "Montserrat"],
#         ["Georgia", "Courier New", "Verdana", "Trebuchet MS"],
#     ]
#     accept_language = [
#         "en-US,en;q=0.9", "fr-FR,fr;q=0.8", "de-DE,de;q=0.9",
#         "hi-IN,hi;q=0.8", "es-ES,es;q=0.9", "ja-JP,ja;q=0.8"
#     ]
#     navigator_platform = ["Win32", "Linux x86_64", "MacIntel", "iPhone", "iPad"]
#     speech_synthesis_voices = [
#         ["Google US English", "Microsoft David"],
#         ["Google UK English Male", "Microsoft Zira"],
#         ["Google Deutsch", "Apple Samantha"],
#         ["Google Hindi", "Microsoft Ravi"],
#     ]
#     connection_types = ["4g", "wifi", "5g", "3g"]
#     battery_levels = [0.7, 0.8, 0.9, 1.0, 0.5, 0.3]
#     vendors = ["Google Inc.", "Apple Computer, Inc.", ""]  # Added for navigator.vendor

#     def generate_random_webgl():
#         random_string = f"{session_id}{time.time()}"  # Use session_id for uniqueness
#         return hashlib.sha256(random_string.encode()).hexdigest()[:32]

#     def generate_random_canvas():
#         random_string = f"{session_id}{time.time()}"  # Use session_id for uniqueness
#         return hashlib.sha256(random_string.encode()).hexdigest()[:32]

#     return {
#         "device_type": device_type,
#         "os": os,
#         "user_agent": user_agent,
#         "screen_width": random.choice(screen_widths),
#         "screen_height": random.choice(screen_heights),
#         "avail_width": random.choice(screen_widths) - random.randint(0, 50),  # Added for realism
#         "avail_height": random.choice(screen_heights) - random.randint(0, 50),
#         "device_pixel_ratio": random.choice(device_pixel_ratio),
#         "webgl_disabled": random.choice([True, False]),
#         "webgl_renderer": random.choice(webgl_renderer),
#         "webgl_vendor": random.choice(webgl_vendor),
#         "peer_connection_disabled": random.choice([True, False]),
#         "resist_fingerprinting": random.choice([True, False]),
#         "language": random.choice(LOCALES),
#         "timezone_offset": random.choice([0, -60, -120, -180, -240, 60, 120, 180, 300]),
#         "timezone": random.choice(TIMEZONES),
#         "plugins": random.choice([True, False]),
#         "plugin_list": random.choice(plugin_list),
#         "fonts": random.choice([True, False]),
#         "installed_fonts": random.choice(installed_fonts),
#         "hardware_concurrency": random.choice([4, 8, 12, 16, 24]),
#         "device_memory": random.choice([4, 8, 16, 32]),
#         "screen_orientation": random.choice(["portrait", "landscape"]),
#         "accept_language": random.choice(accept_language),
#         "audio_fingerprint": generate_random_canvas(),
#         "gpu_fingerprint": generate_random_webgl(),
#         "navigator_platform": random.choice(navigator_platform),
#         "do_not_track": random.choice(["1", "0", None]),
#         "math_tan_pi": random.choice([3.0000000000000000, 3.14159265358979]),
#         "speech_synthesis_voices": random.choice(speech_synthesis_voices),
#         "canvas": generate_random_canvas(),
#         "networkType": random.choice(connection_types),
#         "cookieEnabled": True,  # Set to True for realistic GA tracking
#         "display": f"{random.randint(20, 50)}|{random.randint(300, 600)}|{random.randint(400, 800)}|{random.randint(300, 600)}|{random.randint(400, 800)}",
#         "platform": random.choice(["MacIntel", "Win32", "Linux x86_64", "iPhone", "iPad"]),
#         "java": random.choice(["true", "false"]),
#         "webgl": generate_random_webgl(),
#         "silverlight": "NA",
#         "touchSupport": random.choice([True, False]) if device_type in ["smartphone", "tablet", "ipad", "android_tablet"] else False,
#         "connection": random.choice(connection_types),
#         "battery_level": random.choice(battery_levels),
#         "vendor": random.choice(vendors),  # Added for navigator.vendor
#     }

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
#     print(f"[📊] Summary: {VISIT_STATS['successful']} successful visits, {VISIT_STATS['failed']} failed visits")
#     sys.exit(0)

# def spoof_js_script(fingerprinting):
#     # Enhanced spoofing with additional browser properties
#     voices_js_array = "[" + ",".join(
#         [f"{{name: '{name}', lang: '{fingerprinting['language']}', default: false}}" 
#          for name in fingerprinting["speech_synthesis_voices"]]
#     ) + "]"
    
#     return f"""
#     Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#     Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
#     Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
#     Object.defineProperty(navigator, 'plugins', {{ get: () => {fingerprinting["plugin_list"]} }});
#     Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'] }});
#     Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]} }});
#     Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]} }});
#     Object.defineProperty(navigator, 'vendor', {{ get: () => '{fingerprinting["vendor"]}' }});
#     Object.defineProperty(navigator, 'connection', {{ get: () => {{ downlink: {random.uniform(1, 10)}, effectiveType: '{fingerprinting["connection"]}', rtt: {random.randint(50, 200)} }} }});
#     Object.defineProperty(navigator, 'battery', {{ get: () => {{ level: {fingerprinting["battery_level"]}, charging: {random.choice(['true', 'false'])} }} }});
#     Object.defineProperty(screen, 'availWidth', {{ get: () => {fingerprinting["avail_width"]} }});
#     Object.defineProperty(screen, 'availHeight', {{ get: () => {fingerprinting["avail_height"]} }});
#     const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
#     WebGLRenderingContext.prototype.getParameter = function(param) {{
#         if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#         if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#         return getParameterProxy.call(this, param);
#     }};
#     const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
#     HTMLCanvasElement.prototype.toDataURL = function() {{
#         return "data:image/png;base64," + btoa("{fingerprinting['canvas']}");
#     }};
#     const audioContext = window.AudioContext || window.webkitAudioContext;
#     if (audioContext) {{
#         const originalCreateOscillator = audioContext.prototype.createOscillator;
#         audioContext.prototype.createOscillator = function() {{
#             const oscillator = originalCreateOscillator.call(this);
#             oscillator.frequency.setValueAtTime(1000, 0);
#             return oscillator;
#         }};
#     }}
#     Object.defineProperty(navigator, 'mediaDevices', {{ get: () => undefined }});
#     Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#         return {{ timeZone: '{fingerprinting["timezone"]}' }};
#     }};
#     Object.defineProperty(window, 'speechSynthesis', {{
#         get: () => ({{ getVoices: () => {voices_js_array} }})
#     }});
#     """

# def spoof_js_script(fingerprinting):
#     # Fixed JavaScript syntax to avoid 'Unexpected token ':' error
#     # Using proper string escaping and formatting for object properties
#     voices_js_array = "[" + ",".join(
#         [f"{{name: '{name}', lang: '{fingerprinting['language']}', default: false}}" 
#          for name in fingerprinting['speech_synthesis_voices']]
#     ) + "]"
    
#     # Ensured proper escaping of quotes and formatting
#     return f"""
#     (function() {{
#         try {{
#             Object.defineProperty(navigator, 'platform', {{ get: function() {{ return '{fingerprinting['navigator_platform']}'; }} }});
#             Object.defineProperty(navigator, 'doNotTrack', {{ get: function() {{ return '{fingerprinting['do_not_track'] or 'null'}'; }} }});
#             Object.defineProperty(navigator, 'webdriver', {{ get: function() {{ return false; }} }});
#             Object.defineProperty(navigator, 'plugins', {{ get: function() {{ return {json.dumps(fingerprinting['plugin_list'])}; }} }});
#             Object.defineProperty(navigator, 'languages', {{ get: function() {{ return ['{fingerprinting['language']}', 'en']; }} }});
#             Object.defineProperty(navigator, 'deviceMemory', {{ get: function() {{ return {fingerprinting['device_memory']}; }} }});
#             Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: function() {{ return {fingerprinting['hardware_concurrency']}; }} }});
#             Object.defineProperty(navigator, 'vendor', {{ get: function() {{ return '{fingerprinting['vendor']}'; }} }});
#             Object.defineProperty(navigator, 'connection', {{ 
#                 get: function() {{ 
#                     return {{ 
#                         downlink: {random.uniform(1, 10)}, 
#                         effectiveType: '{fingerprinting['connection']}', 
#                         rtt: {random.randint(50, 200)} 
#                     }}; 
#                 }} 
#             }});
#             Object.defineProperty(navigator, 'battery', {{ 
#                 get: function() {{ 
#                     return {{ 
#                         level: {fingerprinting['battery_level']}, 
#                         charging: {random.choice(['true', 'false'])} 
#                     }}; 
#                 }} 
#             }});
#             Object.defineProperty(screen, 'availWidth', {{ get: function() {{ return {fingerprinting['avail_width']}; }} }});
#             Object.defineProperty(screen, 'availHeight', {{ get: function() {{ return {fingerprinting['avail_height']}; }} }});
#             const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(param) {{
#                 if (param === 37445) return '{fingerprinting['webgl_vendor']}';
#                 if (param === 37446) return '{fingerprinting['webgl_renderer']}';
#                 return getParameterProxy.call(this, param);
#             }};
#             const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
#             HTMLCanvasElement.prototype.toDataURL = function() {{
#                 return 'data:image/png;base64,' + btoa('{fingerprinting['canvas']}');
#             }};
#             const audioContext = window.AudioContext || window.webkitAudioContext;
#             if (audioContext) {{
#                 const originalCreateOscillator = audioContext.prototype.createOscillator;
#                 audioContext.prototype.createOscillator = function() {{
#                     const oscillator = originalCreateOscillator.call(this);
#                     oscillator.frequency.setValueAtTime(1000, 0);
#                     return oscillator;
#                 }};
#             }}
#             Object.defineProperty(navigator, 'mediaDevices', {{ get: function() {{ return undefined; }} }});
#             Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#                 return {{ timeZone: '{fingerprinting['timezone']}' }};
#             }};
#             Object.defineProperty(window, 'speechSynthesis', {{
#                 get: function() {{ 
#                     return {{ getVoices: function() {{ return {voices_js_array}; }} }};
#                 }}
#             }});
#         }} catch (e) {{
#             console.error('Spoofing error:', e);
#         }}
#     }})();
#     """

# def create_driver(session_id):
#     # Pass session_id to generate_fingerprinting for unique fingerprints
#     fingerprinting = generate_fingerprinting(session_id)
#     vp = (fingerprinting["screen_width"], fingerprinting["screen_height"])
#     locale = fingerprinting["language"]
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}_{time.time()}")  # Unique profile folder per session
#     os.makedirs("browser_profiles", exist_ok=True)

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument(f"--user-agent={fingerprinting['user_agent']}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     options.add_argument("--no-first-run")
#     options.add_argument("--no-default-browser-check")
#     options.add_argument("--disable-features=UserAgentClientHint,OptimizationHints")
#     options.add_argument("--disable-popup-blocking")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--log-level=3")
#     options.add_argument("--enable-gpu")
#     options.add_argument("--blink-settings=imagesEnabled=true")
#     options.add_argument("--enable-webgl")
#     options.add_argument("--enable-javascript")
#     options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
#     options.add_argument("--ignore-certificate-errors")
#     options.add_argument("--disable-web-security")  # Added to bypass CSP issues
#     options.add_argument("--disable-background-timer-throttling")  # Added for realistic behavior
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
#             version_main=120,  # Ensure this matches your Chrome version
#         )
#         driver.set_window_size(vp[0], vp[1])
#         ACTIVE_DRIVERS.append(driver)
#         return driver, locale, fingerprinting
#     except Exception as e:
#         logging.error(f"Failed to create driver for session #{session_id}: {e}")
#         return None, None, None

# def simulate_interaction(driver, total_time=90, session_id=None):
#     # Enhanced interaction with varied actions for uniqueness
#     start_time = time.time()
#     total_time_spent = 0
#     action = ActionChains(driver)
#     interaction_log = []

#     try:
#         time.sleep(random.uniform(3, 8))  # Reduced initial delay for efficiency
#         total_time_spent += random.uniform(3, 8)
#         interaction_log.append("Initial page load delay")

#         width = driver.execute_script("return window.innerWidth") or 1200
#         height = driver.execute_script("return window.innerHeight") or 1000

#         # Define possible interaction sequences
#         interaction_types = [
#             "scroll", "mouse_move", "click_product", "click_category", "hover_item", "search"
#         ]
#         random.shuffle(interaction_types)  # Shuffle for unique sequence per visit

#         while total_time_spent < total_time:
#             for interaction in interaction_types[:random.randint(2, 4)]:  # Pick 2-4 interactions
#                 if interaction == "scroll":
#                     scroll_type = random.choice(["incremental", "random", "to_bottom"])
#                     if scroll_type == "incremental":
#                         scroll_y = random.randint(200, 800)
#                         driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#                         interaction_log.append(f"Scrolled incrementally by {scroll_y}px")
#                     elif scroll_type == "random":
#                         driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#                         interaction_log.append("Scrolled to random position")
#                     else:
#                         driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
#                         interaction_log.append("Scrolled to bottom")
#                     t = random.uniform(1, 3)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "mouse_move":
#                     for _ in range(random.randint(2, 5)):
#                         x = random.randint(0, min(width, 1200))
#                         y = random.randint(0, min(height, 1000))
#                         try:
#                             action.move_by_offset(x, y).perform()
#                             action.reset_actions()
#                             interaction_log.append(f"Moved mouse to ({x}, {y})")
#                         except:
#                             pass
#                         t = random.uniform(0.2, 0.8)
#                         time.sleep(t)
#                         total_time_spent += t

#                 elif interaction == "click_product":
#                     try:
#                         products = driver.find_elements(By.XPATH, "//a[contains(@href, '/products/') or contains(@class, 'product')]")
#                         if products:
#                             chosen_product = random.choice(products)
#                             action.move_to_element(chosen_product).perform()
#                             time.sleep(random.uniform(0.5, 1.5))
#                             chosen_product.click()
#                             interaction_log.append("Clicked product link")
#                             time.sleep(random.uniform(2, 5))
#                             driver.back()
#                     except Exception as e:
#                         interaction_log.append(f"Product click failed: {e}")
#                         pass
#                     t = random.uniform(1, 3)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "click_category":
#                     try:
#                         categories = driver.find_elements(By.XPATH, "//a[contains(@href, '/category/') or contains(text(), 'Men') or contains(text(), 'Women') or contains(text(), 'Kids')]")
#                         if categories:
#                             chosen_category = random.choice(categories)
#                             action.move_to_element(chosen_category).perform()
#                             time.sleep(random.uniform(0.5, 1.5))
#                             chosen_category.click()
#                             interaction_log.append("Clicked category link")
#                             time.sleep(random.uniform(2, 5))
#                             driver.back()
#                     except Exception as e:
#                         interaction_log.append(f"Category click failed: {e}")
#                         pass
#                     t = random.uniform(1, 3)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "hover_item":
#                     try:
#                         items = driver.find_elements(By.XPATH, "//div[contains(@class, 'product-card') or contains(@class, 'item')]")
#                         if items:
#                             chosen_item = random.choice(items)
#                             action.move_to_element(chosen_item).perform()
#                             interaction_log.append("Hovered over item")
#                             time.sleep(random.uniform(1, 3))
#                     except Exception as e:
#                         interaction_log.append(f"Hover failed: {e}")
#                         pass
#                     t = random.uniform(1, 2)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "search":
#                     try:
#                         search_box = driver.find_elements(By.XPATH, "//input[@type='search' or @name='q' or contains(@class, 'search')]")
#                         if search_box:
#                             search_terms = ["shoes", "sneakers", "running", "adidas originals"]
#                             search_box[0].send_keys(random.choice(search_terms))
#                             interaction_log.append(f"Entered search term: {search_terms}")
#                             time.sleep(random.uniform(0.5, 1.5))
#                             search_box[0].submit()
#                             time.sleep(random.uniform(2, 5))
#                             driver.back()
#                     except Exception as e:
#                         interaction_log.append(f"Search failed: {e}")
#                         pass
#                     t = random.uniform(1, 3)
#                     time.sleep(t)
#                     total_time_spent += t

#             t = random.uniform(2, 5)
#             time.sleep(t)
#             total_time_spent += t

#             if total_time_spent >= total_time:
#                 break

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#         logging.debug(f"Session #{session_id} interactions: {interaction_log}")

#     except Exception as e:
#         logging.error(f"Interaction Error in session #{session_id}: {e}")

# def log_network_requests(driver, session_id):
#     # Added to log all network requests for debugging
#     try:
#         requests = driver.execute_script("""
#             return performance.getEntriesByType('resource').map(r => ({
#                 name: r.name,
#                 initiatorType: r.initiatorType,
#                 duration: r.duration
#             }));
#         """)
#         with open(f"network_log_{session_id}.json", "w") as f:
#             json.dump(requests, f, indent=2)
#         logging.info(f"Session #{session_id}: Network requests logged to network_log_{session_id}.json")
#         return requests
#     except Exception as e:
#         logging.error(f"Session #{session_id}: Failed to log network requests: {e}")
#         return []

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     driver, locale, fingerprinting = create_driver(session_id)
#     if not driver:
#         print(f"[x] Session #{session_id} failed: Driver creation failed")
#         VISIT_STATS["failed"] += 1
#         return

#     start_time = time.time()
#     attempts = 0
#     max_attempts = 15  # Increased for better Cloudflare handling
#     success = False

#     while not success and attempts < max_attempts:
#         attempts += 1
#         try:
#             driver.get(url)
#             WebDriverWait(driver, 60).until(
#                 lambda d: d.execute_script("return document.readyState === 'complete'")
#             )
#             WebDriverWait(driver, 60).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "body"))
#             )

#             driver.execute_script(spoof_js_script(fingerprinting))

#             # Enhanced Cloudflare detection
#             if any(text in driver.page_source.lower() for text in ["cf-ray", "checking your browser", "just a moment"]):
#                 print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts}).")
#                 try:
#                     WebDriverWait(driver, 60).until(
#                         lambda d: all(text not in d.page_source.lower() for text in ["cf-ray", "checking your browser", "just a moment"])
#                     )
#                     print(f"[✓] Cloudflare challenge passed")
#                 except:
#                     print(f"[!] Cloudflare challenge not resolved")
#                     time.sleep(random.uniform(10, 20))
#                     continue

#             # Enhanced analytics detection
#             try:
#                 WebDriverWait(driver, 60).until(
#                     lambda d: d.execute_script(
#                         "return typeof gtag === 'function' || typeof ga === 'function' || "
#                         "typeof window.dataLayer !== 'undefined' || "
#                         "typeof _satellite !== 'undefined' || "
#                         "document.querySelector('script[src*=\"analytics\"]') !== null"
#                     )
#                 )
#                 print(f"[📊] Analytics scripts loaded in session #{session_id}")
#             except Exception as e:
#                 print(f"[!] Analytics script load failed: {e}")
#                 logging.error(f"Session #{session_id}: Analytics script load failed: {e}")
#                 with open(f"page_source_{session_id}.html", "w", encoding="utf-8") as f:
#                     f.write(driver.page_source)
#                 logging.info(f"Session #{session_id}: Page source saved to page_source_{session_id}.html")

#             # Enhanced GA event triggering
#             driver.execute_script("""
#                 if (typeof gtag === 'function') {
#                     gtag('event', 'page_view', {'page_path': window.location.pathname});
#                     gtag('event', 'view_item', { 'event_category': 'Ecommerce', 'event_label': 'Adidas Product' });
#                     gtag('event', 'headless_test', { 'event_category': 'Test', 'event_label': 'Headless' });
#                 } else if (typeof ga === 'function') {
#                     ga('send', 'pageview');
#                     ga('send', 'event', 'Ecommerce', 'View Item', 'Adidas Product');
#                     ga('send', 'event', 'Test', 'Headless', 'headless_test');
#                 }
#                 if (typeof window.dataLayer !== 'undefined') {
#                     window.dataLayer.push({
#                         'event': 'headless_test',
#                         'page': window.location.pathname,
#                         'ecommerce': {'impressions': [{'name': 'Adidas Product', 'category': 'Shoes'}]}
#                     });
#                 }
#             """)

#             # Log analytics beacons
#             beacons = driver.execute_script("""
#                 return performance.getEntriesByType('resource')
#                     .filter(r => r.name.includes('google-analytics.com') || 
#                                  r.name.includes('googletagmanager.com') || 
#                                  r.name.includes('adobe') || 
#                                  r.name.includes('collect'));
#             """)
#             print(f"[📊] Analytics beacons detected: {len(beacons)}")
#             if beacons:
#                 logging.info(f"Session #{session_id}: Beacons: {json.dumps(beacons, indent=2)}")
#             else:
#                 logging.warning(f"Session #{session_id}: No analytics beacons detected")

#             # Log all network requests
#             log_network_requests(driver, session_id)

#             visit_time = random.randint(60, 150)  # Varied visit time for realism
#             simulate_interaction(driver, total_time=visit_time, session_id=session_id)

#             # Wait for resource stabilization
#             try:
#                 WebDriverWait(driver, 20).until(
#                     lambda d: d.execute_script("return performance.getEntriesByType('resource').length") == 
#                               d.execute_script("return performance.getEntriesByType('resource').length")
#                 )
#             except:
#                 pass
#             time.sleep(random.uniform(5, 15))  # Reduced final delay
#             print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#             success = True
#             VISIT_STATS["successful"] += 1

#         except Exception as e:
#             logging.error(f"Session #{session_id}: Attempt {attempts} failed for {url}: {e}")
#             time.sleep(random.uniform(5, 10))

#     if not success:
#         print(f"[x] Session #{session_id} failed after {max_attempts} attempts")
#         VISIT_STATS["failed"] += 1

#     try:
#         if driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#         driver.quit()
#         # Clean up profile folder to save disk space
#         shutil.rmtree(os.path.join("browser_profiles", f"profile_{session_id}_{time.time()}"), ignore_errors=True)
#     except Exception as e:
#         print(f"[!] Session #{session_id}: Driver quit failed - {e}")
#         os.system("taskkill /F /IM chrome.exe")
#         os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

#     # Process visits in batches
#     for batch in range(0, NUM_VISITS, BATCH_SIZE):
#         print(f"[*] Starting batch {batch // BATCH_SIZE + 1} (Visits {batch + 1} to {min(batch + BATCH_SIZE, NUM_VISITS)})")
#         with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#             visit_id = batch
#             futures = []
#             for i in range(min(BATCH_SIZE, NUM_VISITS - batch)):
#                 for url in TARGET_URLS:
#                     visit_id += 1
#                     futures.append(executor.submit(simulate_single_visit, visit_id, url))
            
#             for future in futures:
#                 future.result()
        
#         print(f"[*] Batch {batch // BATCH_SIZE + 1} completed. Waiting {BATCH_DELAY} seconds before next batch...")
#         time.sleep(BATCH_DELAY)

#     print(f"[📊] Final Summary: {VISIT_STATS['successful']} successful visits, {VISIT_STATS['failed']} failed visits")

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.") 




# import os
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent
# import json
# import shutil

# # === CONFIGURATION ===
# TARGET_URLS = [
#     "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 10000  # Changed to 10,000 visits
# CONCURRENCY = 5  # Increased concurrency for faster processing, but kept reasonable to avoid crashes
# BATCH_SIZE = 100  # Process visits in batches to manage resources
# BATCH_DELAY = 10  # Delay between batches to avoid overwhelming the system
# HEADLESS = True  # Changed to True for efficiency with high volume
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864), (800, 600),
#     (360, 640), (375, 667), (414, 896), (412, 915),  # Added more mobile viewports
# ]
# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR",
#     "ja-JP", "zh-CN", "ru-RU", "ar-SA"  # Expanded locale options
# ]
# TIMEZONES = [
#     "Asia/Kolkata", "Europe/London", "America/New_York", "Australia/Sydney",
#     "Asia/Tokyo", "Europe/Paris", "America/Los_Angeles", "Africa/Johannesburg",
#     "Asia/Dubai"  # Expanded timezone options
# ]

# ACTIVE_DRIVERS = []
# ua_generator = UserAgent()
# VISIT_STATS = {"successful": 0, "failed": 0}  # Added to track visit success/failure

# # Setup logging
# log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_log.txt")
# logging.basicConfig(
#     filename=log_path,
#     level=logging.DEBUG,  # Changed to DEBUG for detailed logging
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )

# def generate_fingerprinting(session_id):
#     # Enhanced fingerprinting to ensure uniqueness for each visit
#     device_os_mapping = {
#         "desktop": ["Windows", "macOS", "Linux", "Fedora"],
#         "laptop": ["Windows", "macOS", "Linux", "ChromeOS", "Fedora"],
#         "ultrabook": ["Windows", "macOS", "Linux", "Fedora"],
#         "macbook": ["macOS"],
#         "chromebook": ["ChromeOS"],
#         "smartphone": ["Android", "iOS"],
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
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64; rv:{3}.0) Gecko/20100101 Firefox/{3}.0",
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "Fedora": [
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:{3}.0) Gecko/20100101 Firefox/{3}.0",
#         ],
#         "iPadOS": [
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.0 Safari/{2}.36",
#         ],
#         "macOS": [
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Safari/{3}.0",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}; rv:{3}.0) Gecko/20100101 Firefox/{3}.0",
#         ],
#         "Linux": [
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:{3}.0) Gecko/20100101 Firefox/{3}.0",
#         ],
#         "Android": [
#             "Mozilla/5.0 (Linux; Android {0}.{1}; SM-G950F Build/{5}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Pixel 4 Build/{5}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
#         ],
#         "iOS": [
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.0 Mobile/{4} Safari/{2}.36",
#         ],
#         "ChromeOS": [
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "Tizen": [
#             "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0 Safari/{2}.36",
#         ],
#         "Android TV": [
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#         ],
#         "WebOS": [
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.1 Safari/{2}.36",
#         ],
#     }

#     device_type = random.choice(list(device_os_mapping.keys()))
#     os = random.choice(device_os_mapping[device_type])
#     version_main = random.randint(10, 15)  # Updated for modern OS versions
#     version_minor = random.randint(0, 4)
#     webkit_version = random.randint(537, 605)
#     chrome_version = random.randint(100, 126)  # Updated for recent Chrome versions
#     firefox_version = random.randint(90, 115)
#     build_version = random.randint(1000, 5000)
#     build_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))  # Added unique build ID for Android
#     user_agent = random.choice(user_agents[os]).format(
#         version_main, version_minor, webkit_version, chrome_version, firefox_version, build_id
#     )
#     screen_widths = [1024, 1366, 1440, 1920, 2560, 3840, 360, 412, 414, 390, 428]  # Added more mobile resolutions
#     screen_heights = [768, 800, 900, 1080, 1200, 1600, 640, 667, 896, 915, 720]
#     device_pixel_ratio = [1, 1.25, 1.5, 2, 2.25, 2.5, 3, 3.5]  # Added more pixel ratios
#     webgl_renderer = [
#         "ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)",
#         "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
#         "ANGLE (AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0)",
#     ]
#     webgl_vendor = ["Google Inc. (NVIDIA)", "Google Inc. (Intel)", "Google Inc. (AMD)"]
#     plugin_list = [
#         ["Chrome PDF Plugin", "Widevine Content Decryption Module", "Shockwave Flash"],
#         ["PDF Viewer", "Native Client"],
#         ["Java", "Silverlight", "QuickTime"],
#     ]
#     installed_fonts = [
#         ["Arial", "Helvetica", "Times New Roman", "Calibri"],
#         ["Roboto", "Open Sans", "Lato", "Montserrat"],
#         ["Georgia", "Courier New", "Verdana", "Trebuchet MS"],
#     ]
#     accept_language = [
#         "en-US,en;q=0.9", "fr-FR,fr;q=0.8", "de-DE,de;q=0.9",
#         "hi-IN,hi;q=0.8", "es-ES,es;q=0.9", "ja-JP,ja;q=0.8"
#     ]
#     navigator_platform = ["Win32", "Linux x86_64", "MacIntel", "iPhone", "iPad"]
#     speech_synthesis_voices = [
#         ["Google US English", "Microsoft David"],
#         ["Google UK English Male", "Microsoft Zira"],
#         ["Google Deutsch", "Apple Samantha"],
#         ["Google Hindi", "Microsoft Ravi"],
#     ]
#     connection_types = ["4g", "wifi", "5g", "3g"]
#     battery_levels = [0.7, 0.8, 0.9, 1.0, 0.5, 0.3]
#     vendors = ["Google Inc.", "Apple Computer, Inc.", ""]  # Added for navigator.vendor

#     def generate_random_webgl():
#         random_string = f"{session_id}{time.time()}"  # Use session_id for uniqueness
#         return hashlib.sha256(random_string.encode()).hexdigest()[:32]

#     def generate_random_canvas():
#         random_string = f"{session_id}{time.time()}"  # Use session_id for uniqueness
#         return hashlib.sha256(random_string.encode()).hexdigest()[:32]

#     return {
#         "device_type": device_type,
#         "os": os,
#         "user_agent": user_agent,
#         "screen_width": random.choice(screen_widths),
#         "screen_height": random.choice(screen_heights),
#         "avail_width": random.choice(screen_widths) - random.randint(0, 50),  # Added for realism
#         "avail_height": random.choice(screen_heights) - random.randint(0, 50),
#         "device_pixel_ratio": random.choice(device_pixel_ratio),
#         "webgl_disabled": random.choice([True, False]),
#         "webgl_renderer": random.choice(webgl_renderer),
#         "webgl_vendor": random.choice(webgl_vendor),
#         "peer_connection_disabled": random.choice([True, False]),
#         "resist_fingerprinting": random.choice([True, False]),
#         "language": random.choice(LOCALES),
#         "timezone_offset": random.choice([0, -60, -120, -180, -240, 60, 120, 180, 300]),
#         "timezone": random.choice(TIMEZONES),
#         "plugins": random.choice([True, False]),
#         "plugin_list": random.choice(plugin_list),
#         "fonts": random.choice([True, False]),
#         "installed_fonts": random.choice(installed_fonts),
#         "hardware_concurrency": random.choice([4, 8, 12, 16, 24]),
#         "device_memory": random.choice([4, 8, 16, 32]),
#         "screen_orientation": random.choice(["portrait", "landscape"]),
#         "accept_language": random.choice(accept_language),
#         "audio_fingerprint": generate_random_canvas(),
#         "gpu_fingerprint": generate_random_webgl(),
#         "navigator_platform": random.choice(navigator_platform),
#         "do_not_track": random.choice(["1", "0", None]),
#         "math_tan_pi": random.choice([3.0000000000000000, 3.14159265358979]),
#         "speech_synthesis_voices": random.choice(speech_synthesis_voices),
#         "canvas": generate_random_canvas(),
#         "networkType": random.choice(connection_types),
#         "cookieEnabled": True,  # Set to True for realistic GA tracking
#         "display": f"{random.randint(20, 50)}|{random.randint(300, 600)}|{random.randint(400, 800)}|{random.randint(300, 600)}|{random.randint(400, 800)}",
#         "platform": random.choice(["MacIntel", "Win32", "Linux x86_64", "iPhone", "iPad"]),
#         "java": random.choice(["true", "false"]),
#         "webgl": generate_random_webgl(),
#         "silverlight": "NA",
#         "touchSupport": random.choice([True, False]) if device_type in ["smartphone", "tablet", "ipad", "android_tablet"] else False,
#         "connection": random.choice(connection_types),
#         "battery_level": random.choice(battery_levels),
#         "vendor": random.choice(vendors),  # Added for navigator.vendor
#     }

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
#     print(f"[📊] Summary: {VISIT_STATS['successful']} successful visits, {VISIT_STATS['failed']} failed visits")
#     sys.exit(0)

# def spoof_js_script(fingerprinting):
#     # Enhanced spoofing with additional browser properties
#     voices_js_array = "[" + ",".join(
#         [f"{{name: '{name}', lang: '{fingerprinting['language']}', default: false}}" 
#          for name in fingerprinting["speech_synthesis_voices"]]
#     ) + "]"
    
#     return f"""
#     Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#     Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
#     Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
#     Object.defineProperty(navigator, 'plugins', {{ get: () => {fingerprinting["plugin_list"]} }});
#     Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'] }});
#     Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]} }});
#     Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]} }});
#     Object.defineProperty(navigator, 'vendor', {{ get: () => '{fingerprinting["vendor"]}' }});
#     Object.defineProperty(navigator, 'connection', {{ get: () => {{ downlink: {random.uniform(1, 10)}, effectiveType: '{fingerprinting["connection"]}', rtt: {random.randint(50, 200)} }} }});
#     Object.defineProperty(navigator, 'battery', {{ get: () => {{ level: {fingerprinting["battery_level"]}, charging: {random.choice(['true', 'false'])} }} }});
#     Object.defineProperty(screen, 'availWidth', {{ get: () => {fingerprinting["avail_width"]} }});
#     Object.defineProperty(screen, 'availHeight', {{ get: () => {fingerprinting["avail_height"]} }});
#     const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
#     WebGLRenderingContext.prototype.getParameter = function(param) {{
#         if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#         if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#         return getParameterProxy.call(this, param);
#     }};
#     const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
#     HTMLCanvasElement.prototype.toDataURL = function() {{
#         return "data:image/png;base64," + btoa("{fingerprinting['canvas']}");
#     }};
#     const audioContext = window.AudioContext || window.webkitAudioContext;
#     if (audioContext) {{
#         const originalCreateOscillator = audioContext.prototype.createOscillator;
#         audioContext.prototype.createOscillator = function() {{
#             const oscillator = originalCreateOscillator.call(this);
#             oscillator.frequency.setValueAtTime(1000, 0);
#             return oscillator;
#         }};
#     }}
#     Object.defineProperty(navigator, 'mediaDevices', {{ get: () => undefined }});
#     Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#         return {{ timeZone: '{fingerprinting["timezone"]}' }};
#     }};
#     Object.defineProperty(window, 'speechSynthesis', {{
#         get: () => ({{ getVoices: () => {voices_js_array} }})
#     }});
#     """

# def create_driver(session_id):
#     # Pass session_id to generate_fingerprinting for unique fingerprints
#     fingerprinting = generate_fingerprinting(session_id)
#     vp = (fingerprinting["screen_width"], fingerprinting["screen_height"])
#     locale = fingerprinting["language"]
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}_{time.time()}")  # Unique profile folder per session
#     os.makedirs("browser_profiles", exist_ok=True)

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument(f"--user-agent={fingerprinting['user_agent']}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     options.add_argument("--no-first-run")
#     options.add_argument("--no-default-browser-check")
#     options.add_argument("--disable-features=UserAgentClientHint,OptimizationHints")
#     options.add_argument("--disable-popup-blocking")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--log-level=3")
#     options.add_argument("--enable-gpu")
#     options.add_argument("--blink-settings=imagesEnabled=true")
#     options.add_argument("--enable-webgl")
#     options.add_argument("--enable-javascript")
#     options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
#     options.add_argument("--ignore-certificate-errors")
#     options.add_argument("--disable-web-security")  # Added to bypass CSP issues
#     options.add_argument("--disable-background-timer-throttling")  # Added for realistic behavior
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
#             version_main=120,  # Ensure this matches your Chrome version
#         )
#         driver.set_window_size(vp[0], vp[1])
#         ACTIVE_DRIVERS.append(driver)
#         return driver, locale, fingerprinting
#     except Exception as e:
#         logging.error(f"Failed to create driver for session #{session_id}: {e}")
#         return None, None, None

# def simulate_interaction(driver, total_time=90, session_id=None):
#     # Enhanced interaction with varied actions for uniqueness
#     start_time = time.time()
#     total_time_spent = 0
#     action = ActionChains(driver)
#     interaction_log = []

#     try:
#         time.sleep(random.uniform(3, 8))  # Reduced initial delay for efficiency
#         total_time_spent += random.uniform(3, 8)
#         interaction_log.append("Initial page load delay")

#         width = driver.execute_script("return window.innerWidth") or 1200
#         height = driver.execute_script("return window.innerHeight") or 1000

#         # Define possible interaction sequences
#         interaction_types = [
#             "scroll", "mouse_move", "click_product", "click_category", "hover_item", "search"
#         ]
#         random.shuffle(interaction_types)  # Shuffle for unique sequence per visit

#         while total_time_spent < total_time:
#             for interaction in interaction_types[:random.randint(2, 4)]:  # Pick 2-4 interactions
#                 if interaction == "scroll":
#                     scroll_type = random.choice(["incremental", "random", "to_bottom"])
#                     if scroll_type == "incremental":
#                         scroll_y = random.randint(200, 800)
#                         driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#                         interaction_log.append(f"Scrolled incrementally by {scroll_y}px")
#                     elif scroll_type == "random":
#                         driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#                         interaction_log.append("Scrolled to random position")
#                     else:
#                         driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
#                         interaction_log.append("Scrolled to bottom")
#                     t = random.uniform(1, 3)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "mouse_move":
#                     for _ in range(random.randint(2, 5)):
#                         x = random.randint(0, min(width, 1200))
#                         y = random.randint(0, min(height, 1000))
#                         try:
#                             action.move_by_offset(x, y).perform()
#                             action.reset_actions()
#                             interaction_log.append(f"Moved mouse to ({x}, {y})")
#                         except:
#                             pass
#                         t = random.uniform(0.2, 0.8)
#                         time.sleep(t)
#                         total_time_spent += t

#                 elif interaction == "click_product":
#                     try:
#                         products = driver.find_elements(By.XPATH, "//a[contains(@href, '/products/') or contains(@class, 'product')]")
#                         if products:
#                             chosen_product = random.choice(products)
#                             action.move_to_element(chosen_product).perform()
#                             time.sleep(random.uniform(0.5, 1.5))
#                             chosen_product.click()
#                             interaction_log.append("Clicked product link")
#                             time.sleep(random.uniform(2, 5))
#                             driver.back()
#                     except Exception as e:
#                         interaction_log.append(f"Product click failed: {e}")
#                         pass
#                     t = random.uniform(1, 3)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "click_category":
#                     try:
#                         categories = driver.find_elements(By.XPATH, "//a[contains(@href, '/category/') or contains(text(), 'Men') or contains(text(), 'Women') or contains(text(), 'Kids')]")
#                         if categories:
#                             chosen_category = random.choice(categories)
#                             action.move_to_element(chosen_category).perform()
#                             time.sleep(random.uniform(0.5, 1.5))
#                             chosen_category.click()
#                             interaction_log.append("Clicked category link")
#                             time.sleep(random.uniform(2, 5))
#                             driver.back()
#                     except Exception as e:
#                         interaction_log.append(f"Category click failed: {e}")
#                         pass
#                     t = random.uniform(1, 3)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "hover_item":
#                     try:
#                         items = driver.find_elements(By.XPATH, "//div[contains(@class, 'product-card') or contains(@class, 'item')]")
#                         if items:
#                             chosen_item = random.choice(items)
#                             action.move_to_element(chosen_item).perform()
#                             interaction_log.append("Hovered over item")
#                             time.sleep(random.uniform(1, 3))
#                     except Exception as e:
#                         interaction_log.append(f"Hover failed: {e}")
#                         pass
#                     t = random.uniform(1, 2)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "search":
#                     try:
#                         search_box = driver.find_elements(By.XPATH, "//input[@type='search' or @name='q' or contains(@class, 'search')]")
#                         if search_box:
#                             search_terms = ["shoes", "sneakers", "running", "adidas originals"]
#                             search_box[0].send_keys(random.choice(search_terms))
#                             interaction_log.append(f"Entered search term: {search_terms}")
#                             time.sleep(random.uniform(0.5, 1.5))
#                             search_box[0].submit()
#                             time.sleep(random.uniform(2, 5))
#                             driver.back()
#                     except Exception as e:
#                         interaction_log.append(f"Search failed: {e}")
#                         pass
#                     t = random.uniform(1, 3)
#                     time.sleep(t)
#                     total_time_spent += t

#             t = random.uniform(2, 5)
#             time.sleep(t)
#             total_time_spent += t

#             if total_time_spent >= total_time:
#                 break

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#         logging.debug(f"Session #{session_id} interactions: {interaction_log}")

#     except Exception as e:
#         logging.error(f"Interaction Error in session #{session_id}: {e}")

# def log_network_requests(driver, session_id):
#     # Added to log all network requests for debugging
#     try:
#         requests = driver.execute_script("""
#             return performance.getEntriesByType('resource').map(r => ({
#                 name: r.name,
#                 initiatorType: r.initiatorType,
#                 duration: r.duration
#             }));
#         """)
#         with open(f"network_log_{session_id}.json", "w") as f:
#             json.dump(requests, f, indent=2)
#         logging.info(f"Session #{session_id}: Network requests logged to network_log_{session_id}.json")
#         return requests
#     except Exception as e:
#         logging.error(f"Session #{session_id}: Failed to log network requests: {e}")
#         return []

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     driver, locale, fingerprinting = create_driver(session_id)
#     if not driver:
#         print(f"[x] Session #{session_id} failed: Driver creation failed")
#         VISIT_STATS["failed"] += 1
#         return

#     start_time = time.time()
#     attempts = 0
#     max_attempts = 15  # Increased for better Cloudflare handling
#     success = False

#     while not success and attempts < max_attempts:
#         attempts += 1
#         try:
#             driver.get(url)
#             WebDriverWait(driver, 60).until(
#                 lambda d: d.execute_script("return document.readyState === 'complete'")
#             )
#             WebDriverWait(driver, 60).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "body"))
#             )

#             driver.execute_script(spoof_js_script(fingerprinting))

#             # Enhanced Cloudflare detection
#             if any(text in driver.page_source.lower() for text in ["cf-ray", "checking your browser", "just a moment"]):
#                 print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts}).")
#                 try:
#                     WebDriverWait(driver, 60).until(
#                         lambda d: all(text not in d.page_source.lower() for text in ["cf-ray", "checking your browser", "just a moment"])
#                     )
#                     print(f"[✓] Cloudflare challenge passed")
#                 except:
#                     print(f"[!] Cloudflare challenge not resolved")
#                     time.sleep(random.uniform(10, 20))
#                     continue

#             # Enhanced analytics detection
#             try:
#                 WebDriverWait(driver, 60).until(
#                     lambda d: d.execute_script(
#                         "return typeof gtag === 'function' || typeof ga === 'function' || "
#                         "typeof window.dataLayer !== 'undefined' || "
#                         "typeof _satellite !== 'undefined' || "
#                         "document.querySelector('script[src*=\"analytics\"]') !== null"
#                     )
#                 )
#                 print(f"[📊] Analytics scripts loaded in session #{session_id}")
#             except Exception as e:
#                 print(f"[!] Analytics script load failed: {e}")
#                 logging.error(f"Session #{session_id}: Analytics script load failed: {e}")
#                 with open(f"page_source_{session_id}.html", "w", encoding="utf-8") as f:
#                     f.write(driver.page_source)
#                 logging.info(f"Session #{session_id}: Page source saved to page_source_{session_id}.html")

#             # Enhanced GA event triggering
#             driver.execute_script("""
#                 if (typeof gtag === 'function') {
#                     gtag('event', 'page_view', {'page_path': window.location.pathname});
#                     gtag('event', 'view_item', { 'event_category': 'Ecommerce', 'event_label': 'Adidas Product' });
#                     gtag('event', 'headless_test', { 'event_category': 'Test', 'event_label': 'Headless' });
#                 } else if (typeof ga === 'function') {
#                     ga('send', 'pageview');
#                     ga('send', 'event', 'Ecommerce', 'View Item', 'Adidas Product');
#                     ga('send', 'event', 'Test', 'Headless', 'headless_test');
#                 }
#                 if (typeof window.dataLayer !== 'undefined') {
#                     window.dataLayer.push({
#                         'event': 'headless_test',
#                         'page': window.location.pathname,
#                         'ecommerce': {'impressions': [{'name': 'Adidas Product', 'category': 'Shoes'}]}
#                     });
#                 }
#             """)

#             # Log analytics beacons
#             beacons = driver.execute_script("""
#                 return performance.getEntriesByType('resource')
#                     .filter(r => r.name.includes('google-analytics.com') || 
#                                  r.name.includes('googletagmanager.com') || 
#                                  r.name.includes('adobe') || 
#                                  r.name.includes('collect'));
#             """)
#             print(f"[📊] Analytics beacons detected: {len(beacons)}")
#             if beacons:
#                 logging.info(f"Session #{session_id}: Beacons: {json.dumps(beacons, indent=2)}")
#             else:
#                 logging.warning(f"Session #{session_id}: No analytics beacons detected")

#             # Log all network requests
#             log_network_requests(driver, session_id)

#             visit_time = random.randint(60, 150)  # Varied visit time for realism
#             simulate_interaction(driver, total_time=visit_time, session_id=session_id)

#             # Wait for resource stabilization
#             try:
#                 WebDriverWait(driver, 20).until(
#                     lambda d: d.execute_script("return performance.getEntriesByType('resource').length") == 
#                               d.execute_script("return performance.getEntriesByType('resource').length")
#                 )
#             except:
#                 pass
#             time.sleep(random.uniform(5, 15))  # Reduced final delay

#             print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#             success = True
#             VISIT_STATS["successful"] += 1

#         except Exception as e:
#             logging.error(f"Session #{session_id}: Attempt {attempts} failed for {url}: {e}")
#             time.sleep(random.uniform(5, 10))

#     if not success:
#         print(f"[x] Session #{session_id} failed after {max_attempts} attempts")
#         VISIT_STATS["failed"] += 1

#     try:
#         if driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#         driver.quit()
#         # Clean up profile folder to save disk space
#         shutil.rmtree(os.path.join("browser_profiles", f"profile_{session_id}_{time.time()}"), ignore_errors=True)
#     except Exception as e:
#         print(f"[!] Session #{session_id}: Driver quit failed - {e}")
#         os.system("taskkill /F /IM chrome.exe")
#         os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

#     # Process visits in batches
#     for batch in range(0, NUM_VISITS, BATCH_SIZE):
#         print(f"[*] Starting batch {batch // BATCH_SIZE + 1} (Visits {batch + 1} to {min(batch + BATCH_SIZE, NUM_VISITS)})")
#         with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#             visit_id = batch
#             futures = []
#             for i in range(min(BATCH_SIZE, NUM_VISITS - batch)):
#                 for url in TARGET_URLS:
#                     visit_id += 1
#                     futures.append(executor.submit(simulate_single_visit, visit_id, url))
            
#             for future in futures:
#                 future.result()
        
#         print(f"[*] Batch {batch // BATCH_SIZE + 1} completed. Waiting {BATCH_DELAY} seconds before next batch...")
#         time.sleep(BATCH_DELAY)

#     print(f"[📊] Final Summary: {VISIT_STATS['successful']} successful visits, {VISIT_STATS['failed']} failed visits")

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.")



# import os
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC 
# from fake_useragent import UserAgent

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

# # Setup logging
# log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_log.txt")
# logging.basicConfig(
#     filename=log_path,
#     level=logging.ERROR,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )

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

# def spoof_js_script(fingerprinting):
#     # Pre-process the speech_synthesis_voices array to create a valid JavaScript array string
#     voices_js_array = "[" + ",".join(
#         [f"{{name: '{name}', lang: '{fingerprinting['language']}', default: false}}" 
#          for name in fingerprinting["speech_synthesis_voices"]]
#     ) + "]"
    
#     return f"""
#     Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#     Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
#     Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
#     Object.defineProperty(navigator, 'plugins', {{ get: () => {fingerprinting["plugin_list"]} }});
#     Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'] }});
#     Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]} }});
#     Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]} }});
#     const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
#     WebGLRenderingContext.prototype.getParameter = function(param) {{
#         if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#         if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#         return getParameterProxy.call(this, param);
#     }};
#     const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
#     HTMLCanvasElement.prototype.toDataURL = function() {{
#         return "data:image/png;base64," + btoa("fakecanvasdata");
#     }};
#     const audioContext = window.AudioContext || window.webkitAudioContext;
#     if (audioContext) {{
#         const originalCreateOscillator = audioContext.prototype.createOscillator;
#         audioContext.prototype.createOscillator = function() {{
#             const oscillator = originalCreateOscillator.call(this);
#             oscillator.frequency.value = 1000;
#             return oscillator;
#         }};
#     }}
#     Object.defineProperty(navigator, 'mediaDevices', {{ get: () => undefined }});
#     Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#         return {{ timeZone: '{fingerprinting["timezone"]}' }};
#     }};
#     Object.defineProperty(window, 'speechSynthesis', {{
#         get: () => ({{ getVoices: () => {voices_js_array} }})
#     }});
#     """

# def create_driver(session_id):
#     fingerprinting = generate_fingerprinting()
#     vp = (fingerprinting["screen_width"], fingerprinting["screen_height"])
#     locale = fingerprinting["language"]
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
#     os.makedirs("browser_profiles", exist_ok=True)

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument(f"--user-agent={fingerprinting['user_agent']}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--remote-debugging-port=0")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     options.add_argument("--no-first-run")
#     options.add_argument("--no-default-browser-check")
#     options.add_argument("--disable-features=UserAgentClientHint")
#     options.add_argument("--disable-popup-blocking")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--log-level=3")
#     options.add_argument("--disable-logging")
#     options.add_argument("--enable-gpu")
#     options.add_argument("--blink-settings=imagesEnabled=true")
#     options.add_argument("--enable-webgl")
#     options.add_argument("--enable-javascript")
#     options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
#     options.add_argument("--ignore-certificate-errors")
#     if HEADLESS:
#         options.add_argument("--headless=new")  # Use latest headless mode

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
#             version_main=120,  # Match your Chrome version
#         )
#         driver.set_window_size(vp[0], vp[1])
#         ACTIVE_DRIVERS.append(driver)
#         return driver, locale, fingerprinting
#     except Exception as e:
#         logging.error(f"Failed to create driver for session #{session_id}: {e}")
#         return None, None, None

# def simulate_interaction(driver, total_time=90):
#     start_time = time.time()
#     total_time_spent = 0
#     action = ActionChains(driver)

#     try:
#         time.sleep(random.uniform(5, 10))
#         total_time_spent += random.uniform(5, 10)

#         width = driver.execute_script("return window.innerWidth") or 1200
#         height = driver.execute_script("return window.innerHeight") or 1000

#         while total_time_spent < total_time:
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

#             if random.choice([True, False]):
#                 scroll_y = random.randint(300, 1000)
#                 driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#                 t = random.uniform(1, 2)
#                 time.sleep(t)
#                 total_time_spent += t

#             if random.choice([True, False]):
#                 driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#                 t = random.uniform(1, 2)
#                 time.sleep(t)
#                 total_time_spent += t

#             try:
#                 buttons = driver.find_elements(By.XPATH, "") # //a[@href='https://marcadeo.com/about']
#                 if buttons:
#                     chosen_button = random.choice(buttons)
#                     action.move_to_element(chosen_button).perform()
#                     time.sleep(random.uniform(0.5, 1.5))
#                     chosen_button.click()
#                     time.sleep(random.uniform(2, 4))
#                     driver.back()
#             except:
#                 pass
#                 t = random.uniform(1, 2)
#                 total_time_spent += t

#             t = random.uniform(2, 5)
#             time.sleep(t)
#             total_time_spent += t

#             if total_time_spent >= total_time:
#                 break

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#     except Exception as e:
#         logging.error(f"Interaction Error: {e}")

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     driver, locale, fingerprinting = create_driver(session_id)
#     if not driver:
#         print(f"[x] Session #{session_id} failed: Driver creation failed")
#         return

#     start_time = time.time()
#     attempts = 0
#     max_attempts = 10
#     success = False

#     while not success and attempts < max_attempts:
#         attempts += 1
#         try:
#             driver.get(url)
#             WebDriverWait(driver, 30).until(
#                 lambda d: d.execute_script("return document.readyState === 'complete'")
#             )
#             WebDriverWait(driver, 30).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "body"))
#             )

#             driver.execute_script(spoof_js_script(fingerprinting))

#             if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#                 print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts}).")
#                 try:
#                     WebDriverWait(driver, 30).until(
#                         lambda d: "cf-ray" not in d.page_source and "Checking your browser" not in d.page_source
#                     )
#                     print(f"[✓] Cloudflare challenge passed")
#                 except:
#                     print(f"[!] Cloudflare challenge not resolved")
#                     time.sleep(random.uniform(10, 15))
#                     continue

#             try:
#                 WebDriverWait(driver, 30).until(
#                     lambda d: d.execute_script("return typeof gtag === 'function' || typeof ga === 'function' || typeof window.dataLayer !== 'undefined'")
#                 )
#                 print(f"[📊] GA scripts loaded in session #{session_id}")
#             except Exception as e:
#                 print(f"[!] GA script load failed: {e}")

#             driver.execute_script("""
#                 if (typeof gtag === 'function') {
#                     gtag('event', 'page_view');
#                     gtag('event', 'headless_test', { 'event_category': 'Test', 'event_label': 'Headless' });
#                 } else if (typeof ga === 'function') {
#                     ga('send', 'pageview');
#                     ga('send', 'event', 'Test', 'Headless', 'headless_test');
#                 }
#                 if (typeof window.dataLayer !== 'undefined') {
#                     window.dataLayer.push({'event': 'headless_test'});
#                 }
#             """)

#             beacons = driver.execute_script("""
#                 return performance.getEntriesByType('resource')
#                     .filter(r => r.name.includes('google-analytics.com/collect') || r.name.includes('googletagmanager.com'));
#             """)
#             print(f"[📊] GA beacons detected: {len(beacons)}")

#             visit_time = random.randint(90, 120)
#             simulate_interaction(driver, total_time=visit_time)

#             try:
#                 WebDriverWait(driver, 20).until(
#                     lambda d: d.execute_script("return performance.getEntriesByType('resource').length") == d.execute_script("return performance.getEntriesByType('resource').length")
#                 )
#             except:
#                 pass
#             time.sleep(random.uniform(10, 15))

#             print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#             success = True

#         except Exception as e:
#             logging.error(f"Attempt {attempts} failed for {url}: {e}")
#             time.sleep(random.uniform(2, 5))

#     if not success:
#         print(f"[x] Session #{session_id} failed after {max_attempts} attempts")

#     try:
#         if driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#         driver.quit()
#     except Exception as e:
#         print(f"[!] Session #{session_id}: Driver quit failed - {e}")
#         os.system("taskkill /F /IM chrome.exe")
#         os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

#     with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#         visit_id = 0
#         futures = []
#         for i in range(NUM_VISITS):
#             for url in TARGET_URLS:
#                 visit_id += 1
#                 futures.append(executor.submit(simulate_single_visit, visit_id, url))
        
#         for future in futures:
#             future.result()

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.") 




# import os
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # === CONFIGURATION ===
# TARGET_URLS = [
#     "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 5
# CONCURRENCY = 5
# HEADLESS = False  # Toggle to True for headless mode
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")
# XPATHS = [
#     # "//a[@href='/about']",
#     # "//button[@class='btn btn-primary']",
#     # "//a[@href='/contact']",
#     # "//button[@id='submit']",
#     # "//a[@class='nav-link']",
# ]

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

# # Setup logging
# log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_log.txt")
# logging.basicConfig(
#     filename=log_path,
#     level=logging.ERROR,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )

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
#         ],
#         "Fedora": [
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "iPadOS": [
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
#         ],
#         "macOS": [
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Safari/{3}.0.0.0",
#         ],
#         "Linux": [
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "Android": [
#             "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile Safari/{2}.36",
#         ],
#         "iOS": [
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
#         ],
#         "ChromeOS": [
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "Tizen": [
#             "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (SMART-TV; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "Android TV": [
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; Android {0}.{1}; Nexus Player) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
#         ],
#         "WebOS": [
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#             "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Firefox/{3}.0.{4}.0 Safari/{2}.36",
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

# def spoof_js_script(fingerprinting):
#     voices_js_array = "[" + ",".join(
#         [f"{{name: '{name}', lang: '{fingerprinting['language']}', default: false}}"
#          for name in fingerprinting["speech_synthesis_voices"]]
#     ) + "]"
    
#     return f"""
#     Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#     Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
#     Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
#     Object.defineProperty(navigator, 'plugins', {{ get: () => {fingerprinting["plugin_list"]} }});
#     Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'] }});
#     Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]} }});
#     Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]} }});
#     const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
#     WebGLRenderingContext.prototype.getParameter = function(param) {{
#         if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#         if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#         return getParameterProxy.call(this, param);
#     }};
#     const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
#     HTMLCanvasElement.prototype.toDataURL = function() {{
#         return "data:image/png;base64," + btoa("fakecanvasdata");
#     }};
#     const audioContext = window.AudioContext || window.webkitAudioContext;
#     if (audioContext) {{
#         const originalCreateOscillator = audioContext.prototype.createOscillator;
#         audioContext.prototype.createOscillator = function() {{
#             const oscillator = originalCreateOscillator.call(this);
#             oscillator.frequency.value = 1000;
#             return oscillator;
#         }};
#     }}
#     Object.defineProperty(navigator, 'mediaDevices', {{ get: () => undefined }});
#     Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#         return {{ timeZone: '{fingerprinting["timezone"]}' }};
#     }};
#     Object.defineProperty(window, 'speechSynthesis', {{
#         get: () => ({{ getVoices: () => {voices_js_array} }})
#     }});
#     """

# def create_driver(session_id):
#     fingerprinting = generate_fingerprinting()
#     vp = (fingerprinting["screen_width"], fingerprinting["screen_height"])
#     locale = fingerprinting["language"]
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
#     os.makedirs("browser_profiles", exist_ok=True)

#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument(f"--user-agent={fingerprinting['user_agent']}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--remote-debugging-port=0")
#     options.add_argument(f"--lang={locale}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
#     options.add_argument("--no-first-run")
#     options.add_argument("--no-default-browser-check")
#     options.add_argument("--disable-features=UserAgentClientHint")
#     options.add_argument("--disable-popup-blocking")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--log-level=3")
#     options.add_argument("--disable-logging")
#     options.add_argument("--enable-gpu")
#     options.add_argument("--blink-settings=imagesEnabled=true")
#     options.add_argument("--enable-webgl")
#     options.add_argument("--enable-javascript")
#     options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
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
#             version_main=120,
#         )
#         driver.set_window_size(vp[0], vp[1])
#         ACTIVE_DRIVERS.append(driver)
#         return driver, locale, fingerprinting
#     except Exception as e:
#         logging.error(f"Failed to create driver for session #{session_id}: {e}")
#         return None, None, None

# def simulate_interaction(driver, session_id, total_time=90):
#     start_time = time.time()
#     total_time_spent = 0
#     action = ActionChains(driver)
#     interaction_types = ["mouse_move", "scroll", "xpath_click"]

#     try:
#         time.sleep(random.uniform(3, 8))
#         total_time_spent += random.uniform(3, 8)

#         width = driver.execute_script("return window.innerWidth") or 1200
#         height = driver.execute_script("return window.innerHeight") or 1000

#         # Dynamic interaction loop
#         while total_time_spent < total_time:
#             # Randomly select interaction type and number of actions
#             num_actions = random.randint(1, 4)
#             selected_interactions = random.sample(interaction_types, k=min(len(interaction_types), num_actions))

#             for interaction in selected_interactions:
#                 if interaction == "mouse_move":
#                     x = random.randint(0, min(width, 1200))
#                     y = random.randint(0, min(height, 1000))
#                     try:
#                         action.move_by_offset(x, y).perform()
#                         action.reset_actions()
#                         print(f"[*] Session #{session_id}: Mouse moved to ({x}, {y})")
#                     except Exception as e:
#                         logging.error(f"Mouse move error in session #{session_id}: {e}")
#                     t = random.uniform(0.2, 0.8)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "scroll":
#                     if random.choice([True, False]):
#                         scroll_y = random.randint(200, 800)
#                         driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#                         print(f"[*] Session #{session_id}: Scrolled by {scroll_y}px")
#                     else:
#                         driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#                         print(f"[*] Session #{session_id}: Scrolled to random position")
#                     t = random.uniform(0.5, 1.5)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "xpath_click" and XPATHS:
#                     # Randomly select a subset of XPaths for this interaction cycle
#                     num_xpaths_to_click = random.randint(1, len(XPATHS))
#                     selected_xpaths = random.sample(XPATHS, k=num_xpaths_to_click)
#                     for xpath in selected_xpaths:
#                         try:
#                             buttons = driver.find_elements(By.XPATH, xpath)
#                             if buttons:
#                                 chosen_button = random.choice(buttons)
#                                 action.move_to_element(chosen_button).perform()
#                                 time.sleep(random.uniform(0.3, 1.0))
#                                 chosen_button.click()
#                                 print(f"[*] Session #{session_id}: Clicked element at XPath {xpath}")
#                                 time.sleep(random.uniform(1, 3))
#                                 driver.back()
#                                 time.sleep(random.uniform(0.5, 1.5))
#                             else:
#                                 print(f"[*] Session #{session_id}: No elements found for XPath {xpath}")
#                         except Exception as e:
#                             logging.error(f"XPath click error in session #{session_id} for {xpath}: {e}")
#                         t = random.uniform(1, 2)
#                         total_time_spent += t

#                 if total_time_spent >= total_time:
#                     break

#             t = random.uniform(1, 3)
#             time.sleep(t)
#             total_time_spent += t

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#     except Exception as e:
#         logging.error(f"Interaction Error in session #{session_id}: {e}")

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     driver, locale, fingerprinting = create_driver(session_id)
#     if not driver:
#         print(f"[x] Session #{session_id} failed: Driver creation failed")
#         return

#     start_time = time.time()
#     attempts = 0
#     max_attempts = 10
#     success = False

#     while not success and attempts < max_attempts:
#         attempts += 1
#         try:
#             driver.get(url)
#             WebDriverWait(driver, 30).until(
#                 lambda d: d.execute_script("return document.readyState === 'complete'")
#             )
#             WebDriverWait(driver, 30).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "body"))
#             )

#             driver.execute_script(spoof_js_script(fingerprinting))

#             if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#                 print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts}).")
#                 try:
#                     WebDriverWait(driver, 30).until(
#                         lambda d: "cf-ray" not in d.page_source and "Checking your browser" not in d.page_source
#                     )
#                     print(f"[✓] Cloudflare challenge passed")
#                 except:
#                     print(f"[!] Cloudflare challenge not resolved")
#                     time.sleep(random.uniform(10, 15))
#                     continue

#             try:
#                 WebDriverWait(driver, 30).until(
#                     lambda d: d.execute_script("return typeof gtag === 'function' || typeof ga === 'function' || typeof window.dataLayer !== 'undefined'")
#                 )
#                 print(f"[📊] GA scripts loaded in session #{session_id}")
#             except Exception as e:
#                 print(f"[!] GA script load failed: {e}")

#             driver.execute_script("""
#                 if (typeof gtag === 'function') {
#                     gtag('event', 'page_view');
#                     gtag('event', 'headless_test', { 'event_category': 'Test', 'event_label': 'Headless' });
#                 } else if (typeof ga === 'function') {
#                     ga('send', 'pageview');
#                     ga('send', 'event', 'Test', 'Headless', 'headless_test');
#                 }
#                 if (typeof window.dataLayer !== 'undefined') {
#                     window.dataLayer.push({'event': 'headless_test'});
#                 }
#             """)

#             beacons = driver.execute_script("""
#                 return performance.getEntriesByType('resource')
#                     .filter(r => r.name.includes('google-analytics.com/collect') || r.name.includes('googletagmanager.com'));
#             """)
#             print(f"[📊] GA beacons detected: {len(beacons)}")

#             visit_time = random.randint(90, 120)
#             simulate_interaction(driver, session_id, total_time=visit_time)

#             try:
#                 WebDriverWait(driver, 20).until(
#                     lambda d: d.execute_script("return performance.getEntriesByType('resource').length") == d.execute_script("return performance.getEntriesByType('resource').length")
#                 )
#             except:
#                 pass
#             time.sleep(random.uniform(10, 15))

#             print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#             success = True

#         except Exception as e:
#             logging.error(f"Attempt {attempts} failed for {url}: {e}")
#             time.sleep(random.uniform(2, 5))

#     if not success:
#         print(f"[x] Session #{session_id} failed after {max_attempts} attempts")

#     try:
#         if driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#         driver.quit()
#     except Exception as e:
#         print(f"[!] Session #{session_id}: Driver quit failed - {e}")
#         os.system("taskkill /F /IM chrome.exe")
#         os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary exists:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver exists:", os.path.exists(CHROMEDRIVER_PATH))

#     with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#         visit_id = 0
#         futures = []
#         for i in range(NUM_VISITS):
#             for url in TARGET_URLS:
#                 visit_id += 1
#                 futures.append(executor.submit(simulate_single_visit, visit_id, url))
        
#         for future in futures:
#             future.result()

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.")





# import os
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# import math
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # === CONFIGURATION ===
# TARGET_URLS = [
#     "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 5
# CONCURRENCY = 3  # Reduced to avoid resource strain
# HEADLESS = False  # Keep False for debugging
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")
# XPATHS = [
#     "//a[contains(@href, 'about')]",
#     "//button[contains(@class, 'btn')]",
#     "//a[contains(@href, 'contact')]",
#     "//button[@type='submit']",
#     "//a[contains(@class, 'nav')]",
# ]
# REFERRERS = [
#     "https://www.google.com/",
#     "https://www.bing.com/",
#     "https://www.adidas.co.in/",
#     "",
# ]
# # Optional: Add proxy list if needed
# PROXIES = [
#     # "http://proxy1:port",
#     # "http://proxy2:port",
# ]

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864),
# ]
# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
# ]
# TIMEZONES = [
#     "Asia/Kolkata", "Europe/London", "America/New_York",
#     "Australia/Sydney", "Asia/Tokyo", "Europe/Paris"
# ]

# ACTIVE_DRIVERS = []

# # Setup logging
# log_dir = os.path.dirname(os.path.abspath(__file__))
# os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
# error_log = os.path.join(log_dir, "logs", "error_log.txt")
# info_log = os.path.join(log_dir, "logs", "info_log.txt")
# logging.basicConfig(
#     filename=error_log,
#     level=logging.ERROR,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )
# info_logger = logging.getLogger("info")
# info_handler = logging.FileHandler(info_log)
# info_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
# info_logger.addHandler(info_handler)
# info_logger.setLevel(logging.INFO)

# def generate_fingerprinting():
#     device_os_mapping = {
#         "desktop": ["Windows", "macOS", "Linux"],
#         "laptop": ["Windows", "macOS", "Linux", "ChromeOS"],
#         "smartphone": ["Android", "iOS"],
#         "tablet": ["Android", "iOS", "iPadOS"],
#     }

#     user_agents = {
#         "Windows": [
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Safari/537.36",
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/{}.0.{}.0 Safari/537.36",
#         ],
#         "macOS": [
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_{}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Safari/537.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_{}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{}.0 Safari/605.1.15",
#         ],
#         "Linux": [
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Safari/537.36",
#             "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/{}.0",
#         ],
#         "ChromeOS": [
#             "Mozilla/5.0 (X11; CrOS x86_64 {}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Safari/537.36",
#         ],
#         "Android": [
#             "Mozilla/5.0 (Linux; Android {}; SM-G{}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Mobile Safari/537.36",
#         ],
#         "iOS": [
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {}_{} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{}.0 Mobile/15E148 Safari/604.1",
#         ],
#         "iPadOS": [
#             "Mozilla/5.0 (iPad; CPU OS {}_{} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{}.0 Mobile/15E148 Safari/604.1",
#         ],
#     }

#     device_type = random.choice(list(device_os_mapping.keys()))
#     os = random.choice(device_os_mapping[device_type])
#     chrome_version = random.randint(110, 126)
#     build_version = random.randint(4000, 6000)
#     os_version = random.randint(0, 5)
#     safari_version = random.randint(15, 17)
#     firefox_version = random.randint(100, 115)
#     android_version = random.randint(10, 14)
#     ios_version = random.randint(15, 18)
#     cros_version = f"{random.randint(14000, 15000)}.{random.randint(0, 999)}.{random.randint(0, 99)}"
#     device_model = random.randint(950, 990)
#     user_agent = random.choice(user_agents[os]).format(
#         chrome_version, build_version, os_version, safari_version, firefox_version,
#         android_version, device_model, ios_version, cros_version
#     )
#     viewport = random.choice(VIEWPORTS)

#     fonts = [
#         ["Arial", "Helvetica", "Times New Roman", "Courier New"],
#         ["Roboto", "Open Sans", "Lato", "Montserrat"],
#         ["Georgia", "Verdana", "Trebuchet MS"],
#     ]
#     plugins = [
#         ["Chrome PDF Plugin", "Widevine Content Decryption Module"],
#         ["Shockwave Flash"],
#         [],
#     ]
#     return {
#         "device_type": device_type,
#         "os": os,
#         "user_agent": user_agent,
#         "viewport": viewport,
#         "webgl_vendor": random.choice(["Google Inc.", "Intel Inc.", "NVIDIA Corporation"]),
#         "webgl_renderer": random.choice(["ANGLE (Intel)", "ANGLE (NVIDIA)", "WebKit WebGL"]),
#         "language": random.choice(LOCALES),
#         "timezone": random.choice(TIMEZONES),
#         "plugin_list": random.choice(plugins),
#         "installed_fonts": random.choice(fonts),
#         "hardware_concurrency": random.choice([4, 8, 12, 16]),
#         "device_memory": random.choice([4, 8, 16]),
#         "canvas_hash": hashlib.sha256(str(random.randint(0, 1000000)).encode()).hexdigest()[:16],
#         "webgl_hash": hashlib.sha256(str(random.randint(0, 1000000)).encode()).hexdigest()[:16],
#         "navigator_platform": {"Windows": "Win32", "macOS": "MacIntel", "Linux": "Linux x86_64", "ChromeOS": "CrOS x86_64", "Android": "Linux armv8l", "iOS": "iPhone", "iPadOS": "iPad"}.get(os, "Win32"),
#         "do_not_track": random.choice(["1", "0", None]),
#     }

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
#     voices_js_array = "[" + ",".join(
#         [f"{{name: '{name}', lang: '{fingerprinting['language']}', default: false}}"
#          for name in fingerprinting["speech_synthesis_voices"]]
#     ) + "]"
    
#     return f"""
#     Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#     Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
#     Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
#     Object.defineProperty(navigator, 'plugins', {{ get: () => {fingerprinting["plugin_list"]} }});
#     Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'] }});
#     Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]} }});
#     Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]} }});
#     const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
#     WebGLRenderingContext.prototype.getParameter = function(param) {{
#         if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#         if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#         return getParameterProxy.call(this, param);
#     }};
#     const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
#     HTMLCanvasElement.prototype.toDataURL = function() {{
#         return "data:image/png;base64," + btoa("fakecanvasdata");
#     }};
#     const audioContext = window.AudioContext || window.webkitAudioContext;
#     if (audioContext) {{
#         const originalCreateOscillator = audioContext.prototype.createOscillator;
#         audioContext.prototype.createOscillator = function() {{
#             const oscillator = originalCreateOscillator.call(this);
#             oscillator.frequency.value = 1000;
#             return oscillator;
#         }};
#     }}
#     Object.defineProperty(navigator, 'mediaDevices', {{ get: () => undefined }});
#     Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#         return {{ timeZone: '{fingerprinting["timezone"]}' }};
#     }};
#     Object.defineProperty(window, 'speechSynthesis', {{
#         get: () => ({{ getVoices: () => {voices_js_array} }})
#     }});
#     """

# def create_driver(session_id):
#     fingerprinting = generate_fingerprinting()
#     vp = fingerprinting["viewport"]
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
#     os.makedirs("browser_profiles", exist_ok=True)

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
#     options.add_argument(f"--referer={random.choice(REFERRERS)}")
#     if PROXIES:
#         options.add_argument(f"--proxy-server={random.choice(PROXIES)}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     service = Service(CHROMEDRIVER_PATH, log_path=os.path.join(log_dir, "logs", "chromedriver.log"))

#     try:
#         driver = uc.Chrome(
#             service=service,
#             options=options,
#             user_data_dir=profile_folder,
#             headless=HEADLESS,
#             driver_executable_path=CHROMEDRIVER_PATH,
#             version_main=126,
#         )
#         driver.set_window_size(vp[0], vp[1])
#         driver.execute_script(f"window.resizeTo({vp[0]}, {vp[1]});")
#         ACTIVE_DRIVERS.append(driver)
#         info_logger.info(f"Session #{session_id}: Driver created with UA: {fingerprinting['user_agent']}, Viewport: {vp}")
#         print(f"[*] Session #{session_id}: Created driver with viewport {vp}")
#         return driver, fingerprinting
#     except Exception as e:
#         logging.error(f"Session #{session_id}: Failed to create driver: {e}")
#         print(f"[x] Session #{session_id}: Driver creation failed: {e}")
#         return None, None

# def human_mouse_move(driver, action, x_start, y_start, x_end, y_end, steps=10):
#     points = []
#     for t in range(steps + 1):
#         t = t / steps
#         x = x_start + (x_end - x_start) * t + random.randint(-20, 20) * math.sin(t * math.pi)
#         y = y_start + (y_end - y_start) * t + random.randint(-20, 20) * math.cos(t * math.pi)
#         points.append((int(x), int(y)))
#     for x, y in points:
#         try:
#             action.move_by_offset(x - action.x, y - action.y).perform()
#             action.x, action.y = x, y
#             time.sleep(random.uniform(0.01, 0.05))
#         except:
#             action.reset_actions()
#     action.reset_actions()

# def simulate_interaction(driver, session_id, total_time=60):
#     action = ActionChains(driver)
#     total_time_spent = 0
#     interaction_types = ["mouse_move", "scroll", "xpath_click", "random_click", "hover", "type"]
#     width = driver.execute_script("return window.innerWidth") or 1200
#     height = driver.execute_script("return window.innerHeight") or 1000
#     action.x, action.y = 0, 0

#     try:
#         time.sleep(random.uniform(1, 3))
#         total_time_spent += random.uniform(1, 3)
#         info_logger.info(f"Session #{session_id}: Starting interactions")

#         try:
#             consent_button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')] | //button[contains(text(), 'Agree')] | //button[contains(@class, 'consent')]"))
#             )
#             consent_button.click()
#             info_logger.info(f"Session #{session_id}: Clicked consent button")
#             print(f"[*] Session #{session_id}: Clicked consent button")
#             time.sleep(random.uniform(1, 2))
#             total_time_spent += random.uniform(1, 2)
#         except:
#             info_logger.info(f"Session #{session_id}: No consent button found")

#         while total_time_spent < total_time:
#             num_actions = random.randint(2, 5)
#             selected_interactions = random.sample(interaction_types, k=num_actions)

#             for interaction in selected_interactions:
#                 if interaction == "mouse_move":
#                     x_start = random.randint(0, width)
#                     y_start = random.randint(0, height)
#                     x_end = random.randint(0, width)
#                     y_end = random.randint(0, height)
#                     try:
#                         human_mouse_move(driver, action, x_start, y_start, x_end, y_end)
#                         info_logger.info(f"Session #{session_id}: Mouse moved from ({x_start}, {y_start}) to ({x_end}, {y_end})")
#                         print(f"[*] Session #{session_id}: Mouse moved to ({x_end}, {y_end})")
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Mouse move error: {e}")
#                     t = random.uniform(0.3, 1.0)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "scroll":
#                     if random.choice([True, False]):
#                         scroll_y = random.randint(200, 800)
#                         driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#                         info_logger.info(f"Session #{session_id}: Scrolled by {scroll_y}px")
#                         print(f"[*] Session #{session_id}: Scrolled by {scroll_y}px")
#                     else:
#                         driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#                         info_logger.info(f"Session #{session_id}: Scrolled to random position")
#                         print(f"[*] Session #{session_id}: Scrolled to random position")
#                     t = random.uniform(0.5, 1.2)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "xpath_click" and XPATHS:
#                     num_xpaths = random.randint(1, len(XPATHS))
#                     selected_xpaths = random.sample(XPATHS, k=num_xpaths)
#                     info_logger.info(f"Session #{session_id}: Attempting to click {num_xpaths} XPaths: {selected_xpaths}")
#                     print(f"[*] Session #{session_id}: Attempting XPaths: {selected_xpaths}")
#                     for xpath in selected_xpaths:
#                         try:
#                             buttons = WebDriverWait(driver, 3).until(
#                                 EC.presence_of_all_elements_located((By.XPATH, xpath))
#                             )
#                             if buttons:
#                                 button = random.choice(buttons)
#                                 action.move_to_element(button).perform()
#                                 time.sleep(random.uniform(0.2, 0.5))
#                                 button.click()
#                                 info_logger.info(f"Session #{session_id}: Clicked element at XPath {xpath}")
#                                 print(f"[*] Session #{session_id}: Clicked XPath {xpath}")
#                                 time.sleep(random.uniform(1, 2))
#                                 driver.back()
#                                 total_time_spent += random.uniform(1, 2)
#                             else:
#                                 info_logger.info(f"Session #{session_id}: No elements found for XPath {xpath}")
#                                 print(f"[*] Session #{session_id}: No elements for XPath {xpath}")
#                         except Exception as e:
#                             logging.error(f"Session #{session_id}: XPath click error for {xpath}: {e}")
#                             print(f"[!] Session #{session_id}: XPath click error for {xpath}: {e}")
#                         t = random.uniform(0.5, 1.0)
#                         total_time_spent += t

#                 elif interaction == "random_click":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //div[@clickable='true']")
#                         if elements:
#                             element = random.choice(elements)
#                             action.move_to_element(element).perform()
#                             time.sleep(random.uniform(0.2, 0.5))
#                             element.click()
#                             info_logger.info(f"Session #{session_id}: Random click on element")
#                             print(f"[*] Session #{session_id}: Random click")
#                             time.sleep(random.uniform(1, 2))
#                             driver.back()
#                             total_time_spent += random.uniform(1, 2)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Random click error: {e}")
#                     t = random.uniform(0.5, 1.0)
#                     total_time_spent += t

#                 elif interaction == "hover":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //div")
#                         if elements:
#                             element = random.choice(elements)
#                             action.move_to_element(element).perform()
#                             info_logger.info(f"Session #{session_id}: Hovered over element")
#                             print(f"[*] Session #{session_id}: Hovered over element")
#                             time.sleep(random.uniform(0.5, 1.5))
#                             total_time_spent += random.uniform(0.5, 1.5)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Hover error: {e}")

#                 elif interaction == "type":
#                     try:
#                         inputs = driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
#                         if inputs:
#                             input_field = random.choice(inputs)
#                             action.move_to_element(input_field).click().perform()
#                             fake_text = "".join(random.choices("abcdefghijklmnopqrstuvwxyz ", k=random.randint(5, 15)))
#                             for char in fake_text:
#                                 input_field.send_keys(char)
#                                 time.sleep(random.uniform(0.05, 0.15))
#                             input_field.send_keys(Keys.ENTER)
#                             info_logger.info(f"Session #{session_id}: Typed '{fake_text}' in input field")
#                             print(f"[*] Session #{session_id}: Typed '{fake_text}'")
#                             time.sleep(random.uniform(1, 2))
#                             total_time_spent += random.uniform(1, 2)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Typing error: {e}")
#                     t = random.uniform(0.5, 1.0)
#                     total_time_spent += t

#                 if total_time_spent >= total_time:
#                     break

#             t = random.uniform(0.5, 1.5)
#             time.sleep(t)
#             total_time_spent += t

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#     except Exception as e:
#         logging.error(f"Session #{session_id}: Interaction error: {e}")
#         print(f"[!] Session #{session_id}: Interaction error: {e}")

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     info_logger.info(f"Session #{session_id}: Starting visit to {url}")
#     driver, fingerprinting = create_driver(session_id)
#     if not driver:
#         return

#     start_time = time.time()
#     attempts = 0
#     max_attempts = 5
#     success = False

#     while not success and attempts < max_attempts:
#         attempts += 1
#         print(f"[*] Session #{session_id}: Attempt {attempts}/{max_attempts}")
#         try:
#             driver.get(url)
#             WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "body"))
#             )
#             info_logger.info(f"Session #{session_id}: Page loaded successfully")
#             print(f"[*] Session #{session_id}: Page loaded")

#             driver.execute_script(spoof_js_script(fingerprinting))

#             if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#                 print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts})")
#                 info_logger.info(f"Session #{session_id}: Cloudflare challenge detected")
#                 try:
#                     WebDriverWait(driver, 30).until(
#                         lambda d: "cf-ray" not in d.page_source and "Checking your browser" not in d.page_source
#                     )
#                     info_logger.info(f"Session #{session_id}: Cloudflare challenge passed")
#                     print(f"[*] Session #{session_id}: Cloudflare challenge passed")
#                 except:
#                     print(f"[!] Session #{session_id}: Cloudflare challenge not resolved")
#                     info_logger.info(f"Session #{session_id}: Cloudflare challenge not resolved")
#                     logging.error(f"Session #{session_id}: Page source: {driver.page_source[:500]}")
#                     time.sleep(random.uniform(5, 10))
#                     continue

#             try:
#                 WebDriverWait(driver, 10).until(
#                     lambda d: d.execute_script("return typeof gtag === 'function' || typeof ga === 'function' || typeof window.dataLayer !== 'undefined'")
#                 )
#                 info_logger.info(f"Session #{session_id}: GA scripts loaded")
#                 print(f"[*] Session #{session_id}: GA scripts loaded")
#                 driver.execute_script("""
#                     if (typeof gtag === 'function') {
#                         gtag('event', 'page_view');
#                         gtag('event', 'human_visit', { 'event_category': 'Visit', 'event_label': 'Simulated' });
#                     } else if (typeof ga === 'function') {
#                         ga('send', 'pageview');
#                         ga('send', 'event', 'Visit', 'Simulated', 'human_visit');
#                     }
#                     if (typeof window.dataLayer !== 'undefined') {
#                         window.dataLayer.push({'event': 'human_visit'});
#                     }
#                 """)
#                 beacons = driver.execute_script("""
#                     return performance.getEntriesByType('resource')
#                         .filter(r => r.name.includes('google-analytics.com') || r.name.includes('googletagmanager.com'));
#                 """)
#                 info_logger.info(f"Session #{session_id}: GA beacons detected: {len(beacons)}")
#                 print(f"[*] Session #{session_id}: GA beacons detected: {len(beacons)}")
#             except:
#                 info_logger.info(f"Session #{session_id}: GA script load failed")
#                 print(f"[!] Session #{session_id}: GA script load failed")

#             visit_time = random.randint(60, 90)
#             simulate_interaction(driver, session_id, total_time=visit_time)
#             time.sleep(random.uniform(5, 10))

#             print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#             info_logger.info(f"Session #{session_id}: Completed in {round(time.time() - start_time)} seconds")
#             success = True

#         except Exception as e:
#             logging.error(f"Session #{session_id}: Attempt {attempts} failed: {e}")
#             print(f"[!] Session #{session_id}: Attempt {attempts} failed: {e}")
#             logging.error(f"Session #{session_id}: Page source: {driver.page_source[:500]}")
#             time.sleep(random.uniform(2, 5))

#     if not success:
#         print(f"[x] Session #{session_id}: Failed after {max_attempts} attempts")
#         info_logger.info(f"Session #{session_id}: Failed after {max_attempts} attempts")

#     try:
#         if driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#         driver.quit()
#         info_logger.info(f"Session #{session_id}: Driver closed")
#         print(f"[*] Session #{session_id}: Driver closed")
#     except Exception as e:
#         logging.error(f"Session #{session_id}: Driver quit failed: {e}")
#         print(f"[!] Session #{session_id}: Driver quit failed: {e}")
#         os.system("taskkill /F /IM chrome.exe")
#         os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver:", os.path.exists(CHROMEDRIVER_PATH))

#     with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#         visit_id = 0
#         futures = []
#         for _ in range(NUM_VISITS):
#             for url in TARGET_URLS:
#                 visit_id += 1
#                 futures.append(executor.submit(simulate_single_visit, visit_id, url))
        
#         for future in futures:
#             future.result()

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.")






# import os
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# import math
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import traceback

# # === CONFIGURATION ===
# TARGET_URLS = [
#     "https://www.adidas.co.in/adi_zomato"
# ]
# NUM_VISITS = 5
# CONCURRENCY = 3  # Reduced to avoid resource strain
# HEADLESS = False  # Keep False for debugging
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")
# XPATHS = [
#     "//a[contains(@href, 'about')]",
#     "//button[contains(@class, 'btn')]",
#     "//a[contains(@href, 'contact')]",
#     "//button[@type='submit']",
#     "//a[contains(@class, 'nav')]",
# ]
# REFERRERS = [
#     "https://www.google.com/",
#     "https://www.bing.com/",
#     "https://www.adidas.co.in/",
#     "",
# ]
# # Optional: Add proxy list if needed
# PROXIES = [
#     # "http://proxy1:port",
#     # "http://proxy2:port",
# ]

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864),
# ]
# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
# ]
# TIMEZONES = [
#     "Asia/Kolkata", "Europe/London", "America/New_York",
#     "Australia/Sydney", "Asia/Tokyo", "Europe/Paris"
# ]

# ACTIVE_DRIVERS = []

# # Setup logging
# log_dir = os.path.dirname(os.path.abspath(__file__))
# os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
# error_log = os.path.join(log_dir, "logs", "error_log.txt")
# info_log = os.path.join(log_dir, "logs", "info_log.txt")
# logging.basicConfig(
#     filename=error_log,
#     level=logging.ERROR,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )
# info_logger = logging.getLogger("info")
# info_handler = logging.FileHandler(info_log)
# info_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
# info_logger.addHandler(info_handler)
# info_logger.setLevel(logging.INFO)

# def generate_fingerprinting():
#     device_os_mapping = {
#         "desktop": ["Windows", "macOS", "Linux"],
#         "laptop": ["Windows", "macOS", "Linux", "ChromeOS"],
#         "smartphone": ["Android", "iOS"],
#         "tablet": ["Android", "iOS", "iPadOS"],
#     }

#     user_agents = {
#         "Windows": [
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Safari/537.36",
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/{}.0.{}.0 Safari/537.36",
#         ],
#         "macOS": [
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_{}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Safari/537.36",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_{}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{}.0 Safari/605.1.15",
#         ],
#         "Linux": [
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Safari/537.36",
#             "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/{}.0",
#         ],
#         "ChromeOS": [
#             "Mozilla/5.0 (X11; CrOS x86_64 {}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Safari/537.36",
#         ],
#         "Android": [
#             "Mozilla/5.0 (Linux; Android {}; SM-G{}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.{}.0 Mobile Safari/537.36",
#         ],
#         "iOS": [
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {}_{} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{}.0 Mobile/15E148 Safari/604.1",
#         ],
#         "iPadOS": [
#             "Mozilla/5.0 (iPad; CPU OS {}_{} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{}.0 Mobile/15E148 Safari/604.1",
#         ],
#     }

#     device_type = random.choice(list(device_os_mapping.keys()))
#     os = random.choice(device_os_mapping[device_type])
#     chrome_version = random.randint(110, 126)
#     build_version = random.randint(4000, 6000)
#     os_version = random.randint(0, 5)
#     safari_version = random.randint(15, 17)
#     firefox_version = random.randint(100, 115)
#     android_version = random.randint(10, 14)
#     ios_version = random.randint(15, 18)
#     cros_version = f"{random.randint(14000, 15000)}.{random.randint(0, 999)}.{random.randint(0, 99)}"
#     device_model = random.randint(950, 990)
#     user_agent = random.choice(user_agents[os]).format(
#         chrome_version, build_version, os_version, safari_version, firefox_version,
#         android_version, device_model, ios_version, cros_version
#     )
#     viewport = random.choice(VIEWPORTS)

#     fonts = [
#         ["Arial", "Helvetica", "Times New Roman", "Courier New"],
#         ["Roboto", "Open Sans", "Lato", "Montserrat"],
#         ["Georgia", "Verdana", "Trebuchet MS"],
#     ]
#     plugins = [
#         ["Chrome PDF Plugin", "Widevine Content Decryption Module"],
#         ["Shockwave Flash"],
#         [],
#     ]
#     return {
#         "device_type": device_type,
#         "os": os,
#         "user_agent": user_agent,
#         "viewport": viewport,
#         "webgl_vendor": random.choice(["Google Inc.", "Intel Inc.", "NVIDIA Corporation"]),
#         "webgl_renderer": random.choice(["ANGLE (Intel)", "ANGLE (NVIDIA)", "WebKit WebGL"]),
#         "language": random.choice(LOCALES),
#         "timezone": random.choice(TIMEZONES),
#         "plugin_list": random.choice(plugins),
#         "installed_fonts": random.choice(fonts),
#         "hardware_concurrency": random.choice([4, 8, 12, 16]),
#         "device_memory": random.choice([4, 8, 16]),
#         "canvas_hash": hashlib.sha256(str(random.randint(0, 1000000)).encode()).hexdigest()[:16],
#         "webgl_hash": hashlib.sha256(str(random.randint(0, 1000000)).encode()).hexdigest()[:16],
#         "navigator_platform": {"Windows": "Win32", "macOS": "MacIntel", "Linux": "Linux x86_64", "ChromeOS": "CrOS x86_64", "Android": "Linux armv8l", "iOS": "iPhone", "iPadOS": "iPad"}.get(os, "Win32"),
#         "do_not_track": random.choice(["1", "0", None]),
#     }

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
#     voices_js_array = "[" + ",".join(
#         [f"{{name: '{name}', lang: '{fingerprinting['language']}', default: false}}"
#          for name in fingerprinting["speech_synthesis_voices"]]
#     ) + "]"
    
#     return f"""
#     Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#     Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
#     Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
#     Object.defineProperty(navigator, 'plugins', {{ get: () => {fingerprinting["plugin_list"]} }});
#     Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'] }});
#     Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]} }});
#     Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]} }});
#     const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
#     WebGLRenderingContext.prototype.getParameter = function(param) {{
#         if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#         if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#         return getParameterProxy.call(this, param);
#     }};
#     const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
#     HTMLCanvasElement.prototype.toDataURL = function() {{
#         return "data:image/png;base64," + btoa("fakecanvasdata");
#     }};
#     const audioContext = window.AudioContext || window.webkitAudioContext;
#     if (audioContext) {{
#         const originalCreateOscillator = audioContext.prototype.createOscillator;
#         audioContext.prototype.createOscillator = function() {{
#             const oscillator = originalCreateOscillator.call(this);
#             oscillator.frequency.value = 1000;
#             return oscillator;
#         }};
#     }}
#     Object.defineProperty(navigator, 'mediaDevices', {{ get: () => undefined }});
#     Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#         return {{ timeZone: '{fingerprinting["timezone"]}' }};
#     }};
#     Object.defineProperty(window, 'speechSynthesis', {{
#         get: () => ({{ getVoices: () => {voices_js_array} }})
#     }});
#     """

# def create_driver(session_id):
#     fingerprinting = generate_fingerprinting()
#     vp = fingerprinting["viewport"]
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
#     os.makedirs("browser_profiles", exist_ok=True)

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
#     options.add_argument(f"--referer={random.choice(REFERRERS)}")
#     if PROXIES:
#         options.add_argument(f"--proxy-server={random.choice(PROXIES)}")
#     if HEADLESS:
#         options.add_argument("--headless=new")

#     service = Service(CHROMEDRIVER_PATH, log_path=os.path.join(log_dir, "logs", "chromedriver.log"))

#     try:
#         driver = uc.Chrome(
#             service=service,
#             options=options,
#             user_data_dir=profile_folder,
#             headless=HEADLESS,
#             driver_executable_path=CHROMEDRIVER_PATH,
#             version_main=126,
#         )
#         driver.set_window_size(vp[0], vp[1])
#         driver.execute_script(f"window.resizeTo({vp[0]}, {vp[1]});")
#         ACTIVE_DRIVERS.append(driver)
#         info_logger.info(f"Session #{session_id}: Driver created with UA: {fingerprinting['user_agent']}, Viewport: {vp}")
#         print(f"[*] Session #{session_id}: Created driver with viewport {vp}")
#         return driver, fingerprinting
#     except Exception as e:
#         logging.error(f"Session #{session_id}: Failed to create driver: {e}")
#         print(f"[x] Session #{session_id}: Driver creation failed: {e}")
#         return None, None

# def human_mouse_move(driver, action, x_start, y_start, x_end, y_end, steps=10):
#     points = []
#     for t in range(steps + 1):
#         t = t / steps
#         x = x_start + (x_end - x_start) * t + random.randint(-20, 20) * math.sin(t * math.pi)
#         y = y_start + (y_end - y_start) * t + random.randint(-20, 20) * math.cos(t * math.pi)
#         points.append((int(x), int(y)))
#     for x, y in points:
#         try:
#             action.move_by_offset(x - action.x, y - action.y).perform()
#             action.x, action.y = x, y
#             time.sleep(random.uniform(0.01, 0.05))
#         except:
#             action.reset_actions()
#     action.reset_actions()

# def simulate_interaction(driver, session_id, total_time=60):
#     action = ActionChains(driver)
#     total_time_spent = 0
#     interaction_types = ["mouse_move", "scroll", "xpath_click", "random_click", "hover", "type"]
#     width = driver.execute_script("return window.innerWidth") or 1200
#     height = driver.execute_script("return window.innerHeight") or 1000
#     action.x, action.y = 0, 0

#     try:
#         time.sleep(random.uniform(1, 3))
#         total_time_spent += random.uniform(1, 3)
#         info_logger.info(f"Session #{session_id}: Starting interactions")

#         try:
#             consent_button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')] | //button[contains(text(), 'Agree')] | //button[contains(@class, 'consent')]"))
#             )
#             consent_button.click()
#             info_logger.info(f"Session #{session_id}: Clicked consent button")
#             print(f"[*] Session #{session_id}: Clicked consent button")
#             time.sleep(random.uniform(1, 2))
#             total_time_spent += random.uniform(1, 2)
#         except:
#             info_logger.info(f"Session #{session_id}: No consent button found")

#         while total_time_spent < total_time:
#             num_actions = random.randint(2, 5)
#             selected_interactions = random.sample(interaction_types, k=num_actions)

#             for interaction in selected_interactions:
#                 if interaction == "mouse_move":
#                     x_start = random.randint(0, width)
#                     y_start = random.randint(0, height)
#                     x_end = random.randint(0, width)
#                     y_end = random.randint(0, height)
#                     try:
#                         human_mouse_move(driver, action, x_start, y_start, x_end, y_end)
#                         info_logger.info(f"Session #{session_id}: Mouse moved from ({x_start}, {y_start}) to ({x_end}, {y_end})")
#                         print(f"[*] Session #{session_id}: Mouse moved to ({x_end}, {y_end})")
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Mouse move error: {e}")
#                     t = random.uniform(0.3, 1.0)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "scroll":
#                     if random.choice([True, False]):
#                         scroll_y = random.randint(200, 800)
#                         driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#                         info_logger.info(f"Session #{session_id}: Scrolled by {scroll_y}px")
#                         print(f"[*] Session #{session_id}: Scrolled by {scroll_y}px")
#                     else:
#                         driver.execute_script("window.scrollTo(0, Math.random() * document.body.scrollHeight)")
#                         info_logger.info(f"Session #{session_id}: Scrolled to random position")
#                         print(f"[*] Session #{session_id}: Scrolled to random position")
#                     t = random.uniform(0.5, 1.2)
#                     time.sleep(t)
#                     total_time_spent += t

#                 elif interaction == "xpath_click" and XPATHS:
#                     num_xpaths = random.randint(1, len(XPATHS))
#                     selected_xpaths = random.sample(XPATHS, k=num_xpaths)
#                     info_logger.info(f"Session #{session_id}: Attempting to click {num_xpaths} XPaths: {selected_xpaths}")
#                     print(f"[*] Session #{session_id}: Attempting XPaths: {selected_xpaths}")
#                     for xpath in selected_xpaths:
#                         try:
#                             buttons = WebDriverWait(driver, 3).until(
#                                 EC.presence_of_all_elements_located((By.XPATH, xpath))
#                             )
#                             if buttons:
#                                 button = random.choice(buttons)
#                                 action.move_to_element(button).perform()
#                                 time.sleep(random.uniform(0.2, 0.5))
#                                 button.click()
#                                 info_logger.info(f"Session #{session_id}: Clicked element at XPath {xpath}")
#                                 print(f"[*] Session #{session_id}: Clicked XPath {xpath}")
#                                 time.sleep(random.uniform(1, 2))
#                                 driver.back()
#                                 total_time_spent += random.uniform(1, 2)
#                             else:
#                                 info_logger.info(f"Session #{session_id}: No elements found for XPath {xpath}")
#                                 print(f"[*] Session #{session_id}: No elements for XPath {xpath}")
#                         except Exception as e:
#                             logging.error(f"Session #{session_id}: XPath click error for {xpath}: {e}")
#                             print(f"[!] Session #{session_id}: XPath click error for {xpath}: {e}")
#                         t = random.uniform(0.5, 1.0)
#                         total_time_spent += t

#                 elif interaction == "random_click":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //div[@clickable='true']")
#                         if elements:
#                             element = random.choice(elements)
#                             action.move_to_element(element).perform()
#                             time.sleep(random.uniform(0.2, 0.5))
#                             element.click()
#                             info_logger.info(f"Session #{session_id}: Random click on element")
#                             print(f"[*] Session #{session_id}: Random click")
#                             time.sleep(random.uniform(1, 2))
#                             driver.back()
#                             total_time_spent += random.uniform(1, 2)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Random click error: {e}")
#                     t = random.uniform(0.5, 1.0)
#                     total_time_spent += t

#                 elif interaction == "hover":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //div")
#                         if elements:
#                             element = random.choice(elements)
#                             action.move_to_element(element).perform()
#                             info_logger.info(f"Session #{session_id}: Hovered over element")
#                             print(f"[*] Session #{session_id}: Hovered over element")
#                             time.sleep(random.uniform(0.5, 1.5))
#                             total_time_spent += random.uniform(0.5, 1.5)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Hover error: {e}")

#                 elif interaction == "type":
#                     try:
#                         inputs = driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
#                         if inputs:
#                             input_field = random.choice(inputs)
#                             action.move_to_element(input_field).click().perform()
#                             fake_text = "".join(random.choices("abcdefghijklmnopqrstuvwxyz ", k=random.randint(5, 15)))
#                             for char in fake_text:
#                                 input_field.send_keys(char)
#                                 time.sleep(random.uniform(0.05, 0.15))
#                             input_field.send_keys(Keys.ENTER)
#                             info_logger.info(f"Session #{session_id}: Typed '{fake_text}' in input field")
#                             print(f"[*] Session #{session_id}: Typed '{fake_text}'")
#                             time.sleep(random.uniform(1, 2))
#                             total_time_spent += random.uniform(1, 2)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Typing error: {e}")
#                     t = random.uniform(0.5, 1.0)
#                     total_time_spent += t

#                 if total_time_spent >= total_time:
#                     break

#             t = random.uniform(0.5, 1.5)
#             time.sleep(t)
#             total_time_spent += t

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#     except Exception as e:
#         logging.error(f"Session #{session_id}: Interaction error: {e}")
#         print(f"[!] Session #{session_id}: Interaction error: {e}")
#         logging.error(f"Traceback: {traceback.format_exc()}")

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     info_logger.info(f"Session #{session_id}: Starting visit to {url}")
#     driver, fingerprinting = create_driver(session_id)
#     if not driver:
#         return

#     start_time = time.time()
#     attempts = 0
#     max_attempts = 5
#     success = False

#     while not success and attempts < max_attempts:
#         attempts += 1
#         print(f"[*] Session #{session_id}: Attempt {attempts}/{max_attempts}")
#         try:
#             driver.get(url)
#             WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "body"))
#             )
#             info_logger.info(f"Session #{session_id}: Page loaded successfully")
#             print(f"[*] Session #{session_id}: Page loaded")

#             # Try to execute spoofing script, but don't let it block success
#             try:
#                 driver.execute_script(spoof_js_script(fingerprinting))
#                 info_logger.info(f"Session #{session_id}: Fingerprint spoofing applied")
#                 print(f"[*] Session #{session_id}: Fingerprint spoofing applied")
#             except Exception as e:
#                 logging.error(f"Session #{session_id}: Fingerprint spoofing failed: {e}")
#                 print(f"[!] Session #{session_id}: Fingerprint spoofing failed: {e}")

#             if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#                 print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts})")
#                 info_logger.info(f"Session #{session_id}: Cloudflare challenge detected")
#                 try:
#                     WebDriverWait(driver, 30).until(
#                         lambda d: "cf-ray" not in d.page_source and "Checking your browser" not in d.page_source
#                     )
#                     info_logger.info(f"Session #{session_id}: Cloudflare challenge passed")
#                     print(f"[*] Session #{session_id}: Cloudflare challenge passed")
#                 except:
#                     print(f"[!] Session #{session_id}: Cloudflare challenge not resolved")
#                     info_logger.info(f"Session #{session_id}: Cloudflare challenge not resolved")
#                     logging.error(f"Session #{session_id}: Page source: {driver.page_source[:500]}")
#                     time.sleep(random.uniform(5, 10))
#                     continue

#             try:
#                 WebDriverWait(driver, 10).until(
#                     lambda d: d.execute_script("return typeof gtag === 'function' || typeof ga === 'function' || typeof window.dataLayer !== 'undefined'")
#                 )
#                 info_logger.info(f"Session #{session_id}: GA scripts loaded")
#                 print(f"[*] Session #{session_id}: GA scripts loaded")
#                 driver.execute_script("""
#                     if (typeof gtag === 'function') {
#                         gtag('event', 'page_view');
#                         gtag('event', 'human_visit', { 'event_category': 'Visit', 'event_label': 'Simulated' });
#                     } else if (typeof ga === 'function') {
#                         ga('send', 'pageview');
#                         ga('send', 'event', 'Visit', 'Simulated', 'human_visit');
#                     }
#                     if (typeof window.dataLayer !== 'undefined') {
#                         window.dataLayer.push({'event': 'human_visit'});
#                     }
#                 """)
#                 beacons = driver.execute_script("""
#                     return performance.getEntriesByType('resource')
#                         .filter(r => r.name.includes('google-analytics.com') || r.name.includes('googletagmanager.com'));
#                 """)
#                 info_logger.info(f"Session #{session_id}: GA beacons detected: {len(beacons)}")
#                 print(f"[*] Session #{session_id}: GA beacons detected: {len(beacons)}")
#             except:
#                 info_logger.info(f"Session #{session_id}: GA script load failed")
#                 print(f"[!] Session #{session_id}: GA script load failed")

#             visit_time = random.randint(60, 90)
#             simulate_interaction(driver, session_id, total_time=visit_time)
#             time.sleep(random.uniform(5, 10))

#             print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#             info_logger.info(f"Session #{session_id}: Completed in {round(time.time() - start_time)} seconds")
#             success = True

#         except Exception as e:
#             logging.error(f"Session #{session_id}: Attempt {attempts} failed: {e}")
#             print(f"[!] Session #{session_id}: Attempt {attempts} failed: {e}")
#             logging.error(f"Session #{session_id}: Page source: {driver.page_source[:500]}")
#             logging.error(f"Traceback: {traceback.format_exc()}")
#             time.sleep(random.uniform(2, 5))

#     if not success:
#         print(f"[x] Session #{session_id}: Failed after {max_attempts} attempts")
#         info_logger.info(f"Session #{session_id}: Failed after {max_attempts} attempts")

#     try:
#         if driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#         driver.quit()
#         info_logger.info(f"Session #{session_id}: Driver closed")
#         print(f"[*] Session #{session_id}: Driver closed")
#     except Exception as e:
#         logging.error(f"Session #{session_id}: Driver quit failed: {e}")
#         print(f"[!] Session #{session_id}: Driver quit failed: {e}")
#         os.system("taskkill /F /IM chrome.exe")
#         os.system("taskkill /F /IM chromedriver.exe")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)

#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")

#     print("Chrome binary:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver:", os.path.exists(CHROMEDRIVER_PATH))

#     with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#         visit_id = 0
#         futures = []
#         for _ in range(NUM_VISITS):
#             for url in TARGET_URLS:
#                 visit_id += 1
#                 futures.append(executor.submit(simulate_single_visit, visit_id, url))
        
#         for future in futures:
#             future.result()

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.") 






# import os
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# import math
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By 
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import traceback
# import json

# # === CONFIGURATION ===
# TARGET_URLS = ["https://www.adidas.co.in/adi_zomato"]
# NUM_VISITS = 3
# CONCURRENCY = 1  # Reduced to 1 for realism
# HEADLESS = False  # Keep False for debugging
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")
# PROXIES = []  # Add proxies e.g., ["http://user:CHANGE_ME_PASSWORD@proxy:port"]
# VIEWPORTS = [(1280, 720), (1366, 768), (1440, 900), (1920, 1080), (1024, 768), (1600, 900)]
# LOCALES = ["en-US", "en-GB", "hi-IN", "es-ES"]
# TIMEZONES = ["Asia/Kolkata", "Europe/London", "America/New_York", "Asia/Tokyo"]

# ACTIVE_DRIVERS = []

# # Setup logging
# log_dir = os.path.dirname(os.path.abspath(__file__))
# os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
# error_log = os.path.join(log_dir, "logs", "error_log.txt")
# info_log = os.path.join(log_dir, "logs", "info_log.txt")
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
#     }

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
#     voices_js_array = "[" + ",".join([f"{{name: '{voice}', lang: '{fingerprinting['language']}', default: {i == 1}}}" for i, voice in enumerate(voices, 1)]) + "]"
#     return f"""
#     Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
#     Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
#     Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
#     Object.defineProperty(navigator, 'plugins', {{ get: () => {json.dumps(fingerprinting["plugin_list"] or [])} }});
#     Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'] }});
#     Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]} }});
#     Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]} }});
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

# def simulate_interaction(driver, session_id, total_time=90):
#     action = ActionChains(driver)
#     total_time_spent = 0
#     width = driver.execute_script("return window.innerWidth") or 1200
#     height = driver.execute_script("return window.innerHeight") or 1000
#     action.x, action.y = random.randint(0, width), random.randint(0, height)

#     try:
#         time.sleep(random.uniform(2, 5))
#         total_time_spent += random.uniform(2, 5)
#         info_logger.info(f"Session #{session_id}: Starting interactions")

#         try:
#             consent_button = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(@class, 'consent')]"))
#             )
#             action.move_to_element(consent_button).pause(random.uniform(0.5, 1)).click().perform()
#             info_logger.info(f"Session #{session_id}: Clicked consent button")
#             print(f"[*] Session #{session_id}: Clicked consent button")
#             time.sleep(random.uniform(2, 5))
#             total_time_spent += random.uniform(2, 5)
#         except:
#             info_logger.info(f"Session #{session_id}: No consent button found")

#         interaction_types = ["mouse_move", "scroll", "click", "hover", "type"]
#         while total_time_spent < total_time:
#             num_actions = random.randint(1, 4)
#             selected_interactions = random.sample(interaction_types, k=num_actions)

#             for interaction in selected_interactions:
#                 if interaction == "mouse_move":
#                     x_start, y_start = action.x, action.y
#                     x_end, y_end = random.randint(0, width), random.randint(0, height)
#                     human_mouse_move(driver, action, x_start, y_start, x_end, y_end)
#                     info_logger.info(f"Session #{session_id}: Mouse moved from ({x_start}, {y_start}) to ({x_end}, {y_end})")
#                     print(f"[*] Session #{session_id}: Mouse moved to ({x_end}, {y_end})")
#                     time.sleep(random.uniform(1, 3))
#                     total_time_spent += random.uniform(1, 3)

#                 elif interaction == "scroll":
#                     if random.choice([True, False]):
#                         scroll_y = random.randint(200, 800)
#                         driver.execute_script(f"window.scrollBy(0, {scroll_y});")
#                         info_logger.info(f"Session #{session_id}: Scrolled by {scroll_y}px")
#                         print(f"[*] Session #{session_id}: Scrolled by {scroll_y}px")
#                     else:
#                         scroll_pos = random.randint(0, int(driver.execute_script("return document.body.scrollHeight") or height))
#                         driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
#                         info_logger.info(f"Session #{session_id}: Scrolled to {scroll_pos}px")
#                         print(f"[*] Session #{session_id}: Scrolled to {scroll_pos}px")
#                     time.sleep(random.uniform(2, 5))
#                     total_time_spent += random.uniform(2, 5)

#                 elif interaction == "click":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //input | //div[not(@role='presentation')]")
#                         if elements:
#                             element = random.choice(elements)
#                             if element.is_displayed() and element.is_enabled():
#                                 action.move_to_element(element).pause(random.uniform(0.5, 2)).click().perform()
#                                 info_logger.info(f"Session #{session_id}: Clicked element at {element.tag_name}")
#                                 print(f"[*] Session #{session_id}: Clicked {element.tag_name}")
#                                 time.sleep(random.uniform(3, 7))
#                                 total_time_spent += random.uniform(3, 7)
#                                 if random.choice([True, False]):
#                                     driver.back()
#                                     time.sleep(random.uniform(2, 5))
#                                     total_time_spent += random.uniform(2, 5)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Click error: {e}")
#                         print(f"[!] Session #{session_id}: Click error: {e}")

#                 elif interaction == "hover":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //div")
#                         if elements:
#                             element = random.choice(elements)
#                             action.move_to_element(element).pause(random.uniform(1, 3)).perform()
#                             info_logger.info(f"Session #{session_id}: Hovered over {element.tag_name}")
#                             print(f"[*] Session #{session_id}: Hovered over {element.tag_name}")
#                             time.sleep(random.uniform(1, 4))
#                             total_time_spent += random.uniform(1, 4)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Hover error: {e}")

#                 elif interaction == "type":
#                     try:
#                         inputs = driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
#                         if inputs:
#                             input_field = random.choice(inputs)
#                             if input_field.is_displayed():
#                                 action.move_to_element(input_field).click().perform()
#                                 fake_text = "".join(random.choices("abcdefghijklmnopqrstuvwxyz ", k=random.randint(5, 20)))
#                                 for char in fake_text:
#                                     input_field.send_keys(char)
#                                     time.sleep(random.uniform(0.1, 0.3))
#                                 if random.choice([True, False]):
#                                     input_field.send_keys(Keys.ENTER)
#                                 info_logger.info(f"Session #{session_id}: Typed '{fake_text}' in input")
#                                 print(f"[*] Session #{session_id}: Typed '{fake_text}'")
#                                 time.sleep(random.uniform(3, 6))
#                                 total_time_spent += random.uniform(3, 6)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Typing error: {e}")

#                 if total_time_spent >= total_time:
#                     break

#             time.sleep(random.uniform(2, 5))
#             total_time_spent += random.uniform(2, 5)

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#     except Exception as e:
#         logging.error(f"Session #{session_id}: Interaction error: {e}")
#         print(f"[!] Session #{session_id}: Interaction error: {e}")
#         logging.error(f"Traceback: {traceback.format_exc()}")

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     info_logger.info(f"Session #{session_id}: Starting visit to {url}")
#     fingerprinting = generate_fingerprinting(session_id)
#     vp = fingerprinting["viewport"]
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
#     os.makedirs("browser_profiles", exist_ok=True)

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
#     if PROXIES:
#         options.add_argument(f"--proxy-server={random.choice(PROXIES)}")

#     if HEADLESS:
#         options.add_argument("--headless=new")

#     service = Service(CHROMEDRIVER_PATH, log_path=os.path.join(log_dir, "logs", "chromedriver.log"))

#     try:
#         driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=HEADLESS)
#         driver.set_window_size(vp[0], vp[1])
#         driver.execute_script(f"window.resizeTo({vp[0]}, {vp[1]});")
#         ACTIVE_DRIVERS.append(driver)
#         info_logger.info(f"Session #{session_id}: Driver created with UA: {fingerprinting['user_agent']}, Viewport: {vp}")
#         print(f"[*] Session #{session_id}: Created driver with viewport {vp}")

#         start_time = time.time()
#         attempts = 0
#         max_attempts = 3  # Reduced attempts for efficiency
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
#                     driver.execute_script(spoof_js_script(fingerprinting))
#                     info_logger.info(f"Session #{session_id}: Fingerprint spoofing applied")
#                     print(f"[*] Session #{session_id}: Fingerprint spoofing applied")
#                 except Exception as e:
#                     logging.error(f"Session #{session_id}: Fingerprint spoofing failed: {e}")
#                     print(f"[!] Session #{session_id}: Fingerprint spoofing failed: {e}")

#                 if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#                     print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts})")
#                     info_logger.info(f"Session #{session_id}: Cloudflare challenge detected")
#                     time.sleep(random.uniform(10, 20))
#                     continue

#                 visit_time = random.randint(90, 120)
#                 simulate_interaction(driver, session_id, total_time=visit_time)
#                 time.sleep(random.uniform(5, 10))
#                 print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#                 info_logger.info(f"Session #{session_id}: Completed in {round(time.time() - start_time)} seconds")
#                 success = True

#             except Exception as e:
#                 logging.error(f"Session #{session_id}: Attempt {attempts} failed: {e}")
#                 print(f"[!] Session #{session_id}: Attempt {attempts} failed: {e}")
#                 logging.error(f"Traceback: {traceback.format_exc()}")
#                 time.sleep(random.uniform(5, 10))

#         if not success:
#             print(f"[x] Session #{session_id}: Failed after {max_attempts} attempts")
#             info_logger.info(f"Session #{session_id}: Failed after {max_attempts} attempts")

#         if driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#         driver.quit()
#         info_logger.info(f"Session #{session_id}: Driver closed")
#         print(f"[*] Session #{session_id}: Driver closed")

#     except Exception as e:
#         logging.error(f"Session #{session_id}: Driver creation failed: {e}")
#         print(f"[x] Session #{session_id}: Driver creation failed: {e}")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)
#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")
#     print("Chrome binary:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver:", os.path.exists(CHROMEDRIVER_PATH))

#     with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#         visit_id = 0
#         futures = []
#         for _ in range(NUM_VISITS):
#             for url in TARGET_URLS:
#                 visit_id += 1
#                 futures.append(executor.submit(simulate_single_visit, visit_id, url))
        
#         for future in futures:
#             future.result()

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.")




# import os
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# import math
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import traceback
# import json

# # === CONFIGURATION ===
# TARGET_URLS = ["https://www.adidas.co.in/adi_zomato"]
# NUM_VISITS = 5
# CONCURRENCY = 1  # Reduced to 1 for realism
# HEADLESS = False  # Toggle to True for headless mode
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")
# PROXIES = []  # Add proxies e.g., ["http://user:CHANGE_ME_PASSWORD@proxy:port"]
# VIEWPORTS = [(1280, 720), (1366, 768), (1440, 900), (1920, 1080), (1024, 768), (1600, 900)]
# LOCALES = ["en-US", "en-GB", "hi-IN", "es-ES"]
# TIMEZONES = ["Asia/Kolkata", "Europe/London", "America/New_York", "Asia/Tokyo"]

# ACTIVE_DRIVERS = []

# # Setup logging
# log_dir = os.path.dirname(os.path.abspath(__file__))
# os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
# error_log = os.path.join(log_dir, "logs", "error_log.txt")
# info_log = os.path.join(log_dir, "logs", "info_log.txt")
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

# def simulate_interaction(driver, session_id, total_time=90):
#     action = ActionChains(driver)
#     total_time_spent = 0
#     width = driver.execute_script("return window.innerWidth") or 1200
#     height = driver.execute_script("return window.innerHeight") or 1000
#     action.x, action.y = random.randint(0, width // 2), random.randint(0, height // 2)

#     try:
#         # Initial delay to simulate page load time
#         time.sleep(random.uniform(2, 5))
#         total_time_spent += random.uniform(2, 5)
#         info_logger.info(f"Session #{session_id}: Starting interactions")

#         # Handle consent if present
#         try:
#             consent_button = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(@class, 'consent')]"))
#             )
#             action.move_to_element(consent_button).pause(random.uniform(0.5, 1)).click().perform()
#             info_logger.info(f"Session #{session_id}: Clicked consent button")
#             print(f"[*] Session #{session_id}: Clicked consent button")
#             time.sleep(random.uniform(2, 5))
#             total_time_spent += random.uniform(2, 5)
#         except:
#             info_logger.info(f"Session #{session_id}: No consent button found")

#         interaction_types = ["mouse_move", "scroll", "click", "hover", "type", "navigate"]
#         while total_time_spent < total_time:
#             num_actions = random.randint(1, 5)  # Increased variety
#             selected_interactions = random.sample(interaction_types, k=min(num_actions, len(interaction_types)))

#             for interaction in selected_interactions:
#                 if interaction == "mouse_move":
#                     x_start, y_start = action.x, action.y
#                     x_end, y_end = random.randint(0, width), random.randint(0, height)
#                     human_mouse_move(driver, action, x_start, y_start, x_end, y_end)
#                     info_logger.info(f"Session #{session_id}: Mouse moved from ({x_start}, {y_start}) to ({x_end}, {y_end})")
#                     print(f"[*] Session #{session_id}: Mouse moved to ({x_end}, {y_end})")
#                     time.sleep(random.uniform(1, 3) * random.random())  # Random pause
#                     total_time_spent += random.uniform(1, 3)

#                 elif interaction == "scroll":
#                     scroll_type = random.choice(["smooth", "jump"])
#                     if scroll_type == "smooth":
#                         scroll_y = random.randint(200, 800)
#                         driver.execute_script(f"window.scrollBy({{ top: {scroll_y}, behavior: 'smooth' }});")
#                         info_logger.info(f"Session #{session_id}: Smooth scrolled by {scroll_y}px")
#                         print(f"[*] Session #{session_id}: Smooth scrolled by {scroll_y}px")
#                         time.sleep(random.uniform(2, 5) * random.random())  # Pause to read
#                         total_time_spent += random.uniform(2, 5)
#                     else:
#                         scroll_pos = random.randint(0, int(driver.execute_script("return document.body.scrollHeight") or height))
#                         driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
#                         info_logger.info(f"Session #{session_id}: Jumped to {scroll_pos}px")
#                         print(f"[*] Session #{session_id}: Jumped to {scroll_pos}px")
#                         time.sleep(random.uniform(3, 6) * random.random())  # Longer pause
#                         total_time_spent += random.uniform(3, 6)

#                 elif interaction == "click":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //input | //div[not(@role='presentation')]")
#                         if elements:
#                             element = random.choice(elements)
#                             if element.is_displayed() and element.is_enabled():
#                                 action.move_to_element(element).pause(random.uniform(0.5, 2)).click().perform()
#                                 info_logger.info(f"Session #{session_id}: Clicked {element.tag_name}")
#                                 print(f"[*] Session #{session_id}: Clicked {element.tag_name}")
#                                 time.sleep(random.uniform(3, 7) * random.random())  # Simulate reading
#                                 total_time_spent += random.uniform(3, 7)
#                                 if random.random() < 0.3:  # 30% chance to go back
#                                     driver.back()
#                                     time.sleep(random.uniform(2, 5))
#                                     total_time_spent += random.uniform(2, 5)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Click error: {e}")
#                         print(f"[!] Session #{session_id}: Click error: {e}")

#                 elif interaction == "hover":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //div")
#                         if elements:
#                             element = random.choice(elements)
#                             action.move_to_element(element).pause(random.uniform(1, 3)).perform()
#                             info_logger.info(f"Session #{session_id}: Hovered over {element.tag_name}")
#                             print(f"[*] Session #{session_id}: Hovered over {element.tag_name}")
#                             time.sleep(random.uniform(1, 4) * random.random())  # Simulate curiosity
#                             total_time_spent += random.uniform(1, 4)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Hover error: {e}")

#                 elif interaction == "type":
#                     try:
#                         inputs = driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea | //input[@type='search']")
#                         if inputs:
#                             input_field = random.choice(inputs)
#                             if input_field.is_displayed():
#                                 action.move_to_element(input_field).click().perform()
#                                 fake_text = "".join(random.choices("abcdefghijklmnopqrstuvwxyz ", k=random.randint(5, 20)))
#                                 for char in fake_text:
#                                     input_field.send_keys(char)
#                                     time.sleep(random.uniform(0.1, 0.3))  # Typing speed
#                                 if random.random() < 0.5:  # 50% chance to submit
#                                     input_field.send_keys(Keys.ENTER)
#                                 info_logger.info(f"Session #{session_id}: Typed '{fake_text}'")
#                                 print(f"[*] Session #{session_id}: Typed '{fake_text}'")
#                                 time.sleep(random.uniform(3, 6) * random.random())
#                                 total_time_spent += random.uniform(3, 6)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Typing error: {e}")

#                 elif interaction == "navigate":
#                     if random.random() < 0.2:  # 20% chance to navigate
#                         try:
#                             links = driver.find_elements(By.TAG_NAME, "a")
#                             if links:
#                                 link = random.choice(links)
#                                 if link.is_displayed():
#                                     action.move_to_element(link).pause(random.uniform(0.5, 1)).click().perform()
#                                     info_logger.info(f"Session #{session_id}: Navigated to new page")
#                                     print(f"[*] Session #{session_id}: Navigated to new page")
#                                     time.sleep(random.uniform(5, 10))
#                                     total_time_spent += random.uniform(5, 10)
#                                     if random.random() < 0.5:
#                                         driver.back()
#                                         time.sleep(random.uniform(2, 5))
#                                         total_time_spent += random.uniform(2, 5)
#                         except Exception as e:
#                             logging.error(f"Session #{session_id}: Navigation error: {e}")

#                 if total_time_spent >= total_time:
#                     break

#             time.sleep(random.uniform(2, 5) * random.random())  # Random breaks
#             total_time_spent += random.uniform(2, 5)

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#     except Exception as e:
#         logging.error(f"Session #{session_id}: Interaction error: {e}")
#         print(f"[!] Session #{session_id}: Interaction error: {e}")
#         logging.error(f"Traceback: {traceback.format_exc()}")

# def simulate_single_visit(session_id, url):
#     print(f"[*] Starting session #{session_id} → {url}")
#     info_logger.info(f"Session #{session_id}: Starting visit to {url}")
#     fingerprinting = generate_fingerprinting(session_id)
#     vp = fingerprinting["viewport"]
#     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
#     os.makedirs("browser_profiles", exist_ok=True)

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
#     if PROXIES:
#         options.add_argument(f"--proxy-server={random.choice(PROXIES)}")

#     if HEADLESS:
#         options.add_argument("--headless=new")
#         options.add_argument("--disable-gpu")

#     service = Service(CHROMEDRIVER_PATH, log_path=os.path.join(log_dir, "logs", "chromedriver.log"))

#     try:
#         driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=HEADLESS)
#         driver.set_window_size(vp[0], vp[1])
#         driver.execute_script(f"window.resizeTo({vp[0]}, {vp[1]});")
#         ACTIVE_DRIVERS.append(driver)
#         info_logger.info(f"Session #{session_id}: Driver created with UA: {fingerprinting['user_agent']}, Viewport: {vp}")
#         print(f"[*] Session #{session_id}: Created driver with viewport {vp}")

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

#                 # Set cookie after page load with valid domain
#                 try:
#                     cookie_domain = ".adidas.co.in"  # Adjust based on the target domain
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
#                     time.sleep(random.uniform(10, 20))
#                     continue

#                 visit_time = random.randint(90, 120)
#                 simulate_interaction(driver, session_id, total_time=visit_time)
#                 time.sleep(random.uniform(5, 10))
#                 print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#                 info_logger.info(f"Session #{session_id}: Completed in {round(time.time() - start_time)} seconds")
#                 success = True

#             except Exception as e:
#                 logging.error(f"Session #{session_id}: Attempt {attempts} failed: {e}")
#                 print(f"[!] Session #{session_id}: Attempt {attempts} failed: {e}")
#                 logging.error(f"Traceback: {traceback.format_exc()}")
#                 time.sleep(random.uniform(5, 10))

#         if not success:
#             print(f"[x] Session #{session_id}: Failed after {max_attempts} attempts")
#             info_logger.info(f"Session #{session_id}: Failed after {max_attempts} attempts")

#         if driver in ACTIVE_DRIVERS:
#             ACTIVE_DRIVERS.remove(driver)
#         driver.quit()
#         info_logger.info(f"Session #{session_id}: Driver closed")
#         print(f"[*] Session #{session_id}: Driver closed")

#     except Exception as e:
#         logging.error(f"Session #{session_id}: Driver creation failed: {e}")
#         print(f"[x] Session #{session_id}: Driver creation failed: {e}")

# def main():
#     signal.signal(signal.SIGINT, signal_handler)
#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe")
#     os.system("taskkill /F /IM chromedriver.exe")
#     print("Chrome binary:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver:", os.path.exists(CHROMEDRIVER_PATH))

#     with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#         visit_id = 0
#         futures = []
#         for _ in range(NUM_VISITS):
#             for url in TARGET_URLS:
#                 visit_id += 1
#                 futures.append(executor.submit(simulate_single_visit, visit_id, url))
        
#         for future in futures:
#             future.result()

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.")





# import os 
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# import math
# from concurrent.futures import ThreadPoolExecutor
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import traceback
# import json
# import psutil

# # === CONFIGURATION ===
# TARGET_URLS = ["https://www.adidas.co.in/adi_zomato"]
# NUM_VISITS = 5
# CONCURRENCY = 1  # Set to 3, 5, or 7 as desired
# HEADLESS = False 
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")
# PROXIES = []
# VIEWPORTS = [(1280, 720), (1366, 768), (1440, 900), (1920, 1080), (1024, 768), (1600, 900)]
# LOCALES = ["en-US", "en-GB", "hi-IN", "es-ES"]
# TIMEZONES = ["Asia/Kolkata", "Europe/London", "America/New_York", "Asia/Tokyo"]

# ACTIVE_DRIVERS = []
# driver_lock = threading.Lock()  # Add lock for thread safety

# # Setup logging (unchanged)
# log_dir = os.path.dirname(os.path.abspath(__file__))
# os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
# error_log = os.path.join(log_dir, "logs", "error_log.txt")
# info_log = os.path.join(log_dir, "logs", "info_log.txt")
# logging.basicConfig(filename=error_log, level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
# info_logger = logging.getLogger("info")
# info_handler = logging.FileHandler(info_log)
# info_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
# info_logger.addHandler(info_handler)
# info_logger.setLevel(logging.INFO)

# # [Rest of your functions like generate_fingerprinting, spoof_js_script, human_mouse_move, simulate_interaction remain unchanged]

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

# def simulate_interaction(driver, session_id, total_time=90):
#     action = ActionChains(driver)
#     total_time_spent = 0
#     width = driver.execute_script("return window.innerWidth") or 1200
#     height = driver.execute_script("return window.innerHeight") or 1000
#     action.x, action.y = random.randint(0, width // 2), random.randint(0, height // 2)

#     try:
#         # Initial delay to simulate page load time
#         time.sleep(random.uniform(2, 5))
#         total_time_spent += random.uniform(2, 5)
#         info_logger.info(f"Session #{session_id}: Starting interactions")

#         # Handle consent if present
#         try:
#             consent_button = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(@class, 'consent')]"))
#             )
#             action.move_to_element(consent_button).pause(random.uniform(0.5, 1)).click().perform()
#             info_logger.info(f"Session #{session_id}: Clicked consent button")
#             print(f"[*] Session #{session_id}: Clicked consent button")
#             time.sleep(random.uniform(2, 5))
#             total_time_spent += random.uniform(2, 5)
#         except:
#             info_logger.info(f"Session #{session_id}: No consent button found")

#         interaction_types = ["mouse_move", "scroll", "click", "hover", "type", "navigate"]
#         while total_time_spent < total_time:
#             num_actions = random.randint(1, 5)  # Increased variety
#             selected_interactions = random.sample(interaction_types, k=min(num_actions, len(interaction_types)))

#             for interaction in selected_interactions:
#                 if interaction == "mouse_move":
#                     x_start, y_start = action.x, action.y
#                     x_end, y_end = random.randint(0, width), random.randint(0, height)
#                     human_mouse_move(driver, action, x_start, y_start, x_end, y_end)
#                     info_logger.info(f"Session #{session_id}: Mouse moved from ({x_start}, {y_start}) to ({x_end}, {y_end})")
#                     print(f"[*] Session #{session_id}: Mouse moved to ({x_end}, {y_end})")
#                     time.sleep(random.uniform(1, 3) * random.random())  # Random pause
#                     total_time_spent += random.uniform(1, 3)

#                 elif interaction == "scroll":
#                     scroll_type = random.choice(["smooth", "jump"])
#                     if scroll_type == "smooth":
#                         scroll_y = random.randint(200, 800)
#                         driver.execute_script(f"window.scrollBy({{ top: {scroll_y}, behavior: 'smooth' }});")
#                         info_logger.info(f"Session #{session_id}: Smooth scrolled by {scroll_y}px")
#                         print(f"[*] Session #{session_id}: Smooth scrolled by {scroll_y}px")
#                         time.sleep(random.uniform(2, 5) * random.random())  # Pause to read
#                         total_time_spent += random.uniform(2, 5)
#                     else:
#                         scroll_pos = random.randint(0, int(driver.execute_script("return document.body.scrollHeight") or height))
#                         driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
#                         info_logger.info(f"Session #{session_id}: Jumped to {scroll_pos}px")
#                         print(f"[*] Session #{session_id}: Jumped to {scroll_pos}px")
#                         time.sleep(random.uniform(3, 6) * random.random())  # Longer pause
#                         total_time_spent += random.uniform(3, 6)

#                 elif interaction == "click":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //input | //div[not(@role='presentation')]")
#                         if elements:
#                             element = random.choice(elements)
#                             if element.is_displayed() and element.is_enabled():
#                                 action.move_to_element(element).pause(random.uniform(0.5, 2)).click().perform()
#                                 info_logger.info(f"Session #{session_id}: Clicked {element.tag_name}")
#                                 print(f"[*] Session #{session_id}: Clicked {element.tag_name}")
#                                 time.sleep(random.uniform(3, 7) * random.random())  # Simulate reading
#                                 total_time_spent += random.uniform(3, 7)
#                                 if random.random() < 0.3:  # 30% chance to go back
#                                     driver.back()
#                                     time.sleep(random.uniform(2, 5))
#                                     total_time_spent += random.uniform(2, 5)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Click error: {e}")
#                         print(f"[!] Session #{session_id}: Click error: {e}")

#                 elif interaction == "hover":
#                     try:
#                         elements = driver.find_elements(By.XPATH, "//a | //button | //div")
#                         if elements:
#                             element = random.choice(elements)
#                             action.move_to_element(element).pause(random.uniform(1, 3)).perform()
#                             info_logger.info(f"Session #{session_id}: Hovered over {element.tag_name}")
#                             print(f"[*] Session #{session_id}: Hovered over {element.tag_name}")
#                             time.sleep(random.uniform(1, 4) * random.random())  # Simulate curiosity
#                             total_time_spent += random.uniform(1, 4)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Hover error: {e}")

#                 elif interaction == "type":
#                     try:
#                         inputs = driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea | //input[@type='search']")
#                         if inputs:
#                             input_field = random.choice(inputs)
#                             if input_field.is_displayed():
#                                 action.move_to_element(input_field).click().perform()
#                                 fake_text = "".join(random.choices("abcdefghijklmnopqrstuvwxyz ", k=random.randint(5, 20)))
#                                 for char in fake_text:
#                                     input_field.send_keys(char)
#                                     time.sleep(random.uniform(0.1, 0.3))  # Typing speed
#                                 if random.random() < 0.5:  # 50% chance to submit
#                                     input_field.send_keys(Keys.ENTER)
#                                 info_logger.info(f"Session #{session_id}: Typed '{fake_text}'")
#                                 print(f"[*] Session #{session_id}: Typed '{fake_text}'")
#                                 time.sleep(random.uniform(3, 6) * random.random())
#                                 total_time_spent += random.uniform(3, 6)
#                     except Exception as e:
#                         logging.error(f"Session #{session_id}: Typing error: {e}")

#                 elif interaction == "navigate":
#                     if random.random() < 0.2:  # 20% chance to navigate
#                         try:
#                             links = driver.find_elements(By.TAG_NAME, "a")
#                             if links:
#                                 link = random.choice(links)
#                                 if link.is_displayed():
#                                     action.move_to_element(link).pause(random.uniform(0.5, 1)).click().perform()
#                                     info_logger.info(f"Session #{session_id}: Navigated to new page")
#                                     print(f"[*] Session #{session_id}: Navigated to new page")
#                                     time.sleep(random.uniform(5, 10))
#                                     total_time_spent += random.uniform(5, 10)
#                                     if random.random() < 0.5:
#                                         driver.back()
#                                         time.sleep(random.uniform(2, 5))
#                                         total_time_spent += random.uniform(2, 5)
#                         except Exception as e:
#                             logging.error(f"Session #{session_id}: Navigation error: {e}")

#                 if total_time_spent >= total_time:
#                     break

#             time.sleep(random.uniform(2, 5) * random.random())  # Random breaks
#             total_time_spent += random.uniform(2, 5)

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#     except Exception as e:
#         logging.error(f"Session #{session_id}: Interaction error: {e}")
#         print(f"[!] Session #{session_id}: Interaction error: {e}")
#         logging.error(f"Traceback: {traceback.format_exc()}")

# # def simulate_single_visit(session_id, url):
# #     print(f"[*] Starting session #{session_id} → {url}")
# #     info_logger.info(f"Session #{session_id}: Starting visit to {url}")
# #     fingerprinting = generate_fingerprinting(session_id)
# #     vp = fingerprinting["viewport"]
# #     profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
# #     os.makedirs("browser_profiles", exist_ok=True)

# #     # Improved cleanup with lock
# #     with driver_lock:
# #         os.system("taskkill /F /IM chrome.exe 2>nul")
# #         os.system("taskkill /F /IM chromedriver.exe 2>nul")
# #         time.sleep(2)  # Wait for file release

# #     options = uc.ChromeOptions()
# #     options.binary_location = CHROME_BINARY
# #     options.add_argument(f"--user-agent={fingerprinting['user_agent']}")
# #     options.add_argument(f"--lang={fingerprinting['language']}")
# #     options.add_argument(f"--user-data-dir={profile_folder}")
# #     options.add_argument(f"--window-size={vp[0]},{vp[1]}")
# #     options.add_argument("--no-sandbox")
# #     options.add_argument("--disable-blink-features=AutomationControlled")
# #     options.add_argument("--disable-dev-shm-usage")
# #     options.add_argument("--no-first-run")
# #     options.add_argument("--disable-popup-blocking")
# #     options.add_argument("--disable-infobars")
# #     options.add_argument("--enable-webgl")
# #     options.add_argument("--enable-javascript")
# #     options.add_argument("--ignore-certificate-errors")
# #     if PROXIES:
# #         options.add_argument(f"--proxy-server={random.choice(PROXIES)}")

# #     if HEADLESS:
# #         options.add_argument("--headless=new")
# #         options.add_argument("--disable-gpu")

# #     service = Service(CHROMEDRIVER_PATH, log_path=os.path.join(log_dir, "logs", "chromedriver.log"))

# #     try:
# #         with driver_lock:  # Lock during driver creation
# #             driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=HEADLESS)
# #         driver.set_window_size(vp[0], vp[1])
# #         driver.execute_script(f"window.resizeTo({vp[0]}, {vp[1]});")
# #         ACTIVE_DRIVERS.append(driver)
# #         info_logger.info(f"Session #{session_id}: Driver created with UA: {fingerprinting['user_agent']}, Viewport: {vp}")
# #         print(f"[*] Session #{session_id}: Created driver with viewport {vp}")

# #         start_time = time.time()
# #         attempts = 0
# #         max_attempts = 3
# #         success = False

# #         while not success and attempts < max_attempts:
# #             attempts += 1
# #             print(f"[*] Session #{session_id}: Attempt {attempts}/{max_attempts}")
# #             try:
# #                 driver.get(url)
# #                 WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
# #                 info_logger.info(f"Session #{session_id}: Page loaded successfully")
# #                 print(f"[*] Session #{session_id}: Page loaded")

# #                 # Dynamic cookie domain
# #                 try:
# #                     cookie_domain = '.' + url.split('/')[2]  # e.g., .marcadeo.com
# #                     driver.add_cookie({
# #                         "name": "session_id",
# #                         "value": fingerprinting["cookie_value"],
# #                         "domain": cookie_domain,
# #                         "path": "/"
# #                     })
# #                     info_logger.info(f"Session #{session_id}: Cookie set successfully")
# #                     print(f"[*] Session #{session_id}: Cookie set")
# #                 except Exception as e:
# #                     logging.error(f"Session #{session_id}: Failed to set cookie: {e}")
# #                     print(f"[!] Session #{session_id}: Failed to set cookie: {e}")

# #                 try:
# #                     driver.execute_script(spoof_js_script(fingerprinting))
# #                     info_logger.info(f"Session #{session_id}: Fingerprint spoofing applied")
# #                     print(f"[*] Session #{session_id}: Fingerprint spoofing applied")
# #                 except Exception as e:
# #                     logging.error(f"Session #{session_id}: Fingerprint spoofing failed: {e}")
# #                     print(f"[!] Session #{session_id}: Fingerprint spoofing failed: {e}")

# #                 if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
# #                     print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts})")
# #                     info_logger.info(f"Session #{session_id}: Cloudflare challenge detected")
# #                     time.sleep(random.uniform(10, 20))
# #                     continue

# #                 visit_time = random.randint(90, 120)
# #                 simulate_interaction(driver, session_id, total_time=visit_time)
# #                 time.sleep(random.uniform(5, 10))
# #                 print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
# #                 info_logger.info(f"Session #{session_id}: Completed in {round(time.time() - start_time)} seconds")
# #                 success = True

# #             except Exception as e:
# #                 logging.error(f"Session #{session_id}: Attempt {attempts} failed: {e}")
# #                 print(f"[!] Session #{session_id}: Attempt {attempts} failed: {e}")
# #                 logging.error(f"Traceback: {traceback.format_exc()}")
# #                 time.sleep(random.uniform(5, 10))

# #         if not success:
# #             print(f"[x] Session #{session_id}: Failed after {max_attempts} attempts")
# #             info_logger.info(f"Session #{session_id}: Failed after {max_attempts} attempts")

# #         if driver in ACTIVE_DRIVERS:
# #             ACTIVE_DRIVERS.remove(driver)
# #         driver.quit()
# #         info_logger.info(f"Session #{session_id}: Driver closed")
# #         print(f"[*] Session #{session_id}: Driver closed")

# #     except Exception as e:
# #         logging.error(f"Session #{session_id}: Driver creation failed: {e}")
# #         print(f"[x] Session #{session_id}: Driver creation failed: {e}")


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
#             time.sleep(2)  # Wait for file release
#             if not any("chrome.exe" in p.name() for p in psutil.process_iter() if "chrome" in p.name().lower()):
#                 break
#         if attempt < max_cleanup_attempts - 1:
#             time.sleep(2)  # Extra wait if cleanup fails

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
#     options.add_argument("--disable-extensions")  # Avoid extension conflicts
#     options.add_argument("--disable-notifications")  # Reduce interference
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
#                 with driver_lock:  # Lock during driver creation
#                     driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=HEADLESS)
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
#                     time.sleep(5)  # Wait before retry
#                 else:
#                     raise  # Raise exception if all attempts fail

#         start_time = time.time()
#         attempts = 0
#         max_attempts = 3
#         success = False

#         while not success and attempts < max_attempts:
#             attempts += 1
#             print(f"[*] Session #{session_id}: Attempt {attempts}/{max_attempts}")
#             try:
#                 driver.get(url)
#                 WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Fixed syntax
#                 info_logger.info(f"Session #{session_id}: Page loaded successfully")
#                 print(f"[*] Session #{session_id}: Page loaded")

#                 # Dynamic cookie domain with validation
#                 try:
#                     cookie_domain = '.' + url.split('/')[2]  # e.g., .adidas.co.in
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
#                     time.sleep(random.uniform(10, 20))
#                     continue

#                 visit_time = random.randint(90, 120)
#                 simulate_interaction(driver, session_id, total_time=visit_time)
#                 time.sleep(random.uniform(5, 10))
#                 print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#                 info_logger.info(f"Session #{session_id}: Completed in {round(time.time() - start_time)} seconds")
#                 success = True

#             except Exception as e:
#                 logging.error(f"Session #{session_id}: Attempt {attempts} failed: {e}")
#                 print(f"[!] Session #{session_id}: Attempt {attempts} failed: {e}")
#                 logging.error(f"Traceback: {traceback.format_exc()}")
#                 if attempts < max_attempts:
#                     driver.quit()  # Close and recreate driver
#                     with driver_lock:
#                         driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=HEADLESS)
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

# def main():
#     signal.signal(signal.SIGINT, signal_handler)
#     print("Cleaning up existing Chrome processes...")
#     os.system("taskkill /F /IM chrome.exe 2>nul")
#     os.system("taskkill /F /IM chromedriver.exe 2>nul")
#     time.sleep(2)  # Wait for cleanup
#     print("Chrome binary:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver:", os.path.exists(CHROMEDRIVER_PATH))

#     with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
#         visit_id = 0
#         futures = []
#         for _ in range(NUM_VISITS):
#             for url in TARGET_URLS:
#                 visit_id += 1
#                 futures.append(executor.submit(simulate_single_visit, visit_id, url))
        
#         for future in futures:
#             future.result()

# if __name__ == "__main__":
#     start = time.time()
#     main()
#     print(f"[✅] All visits completed in {round(time.time() - start, 2)} seconds.")







# import os
# import time
# import random
# import hashlib
# import logging
# import sys
# import signal
# import threading
# import math
# import asyncio
# import shutil
# import psutil
# import backoff
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import traceback
# import json
# import undetected_chromedriver as uc

# # === CONFIGURATION ===
# TARGET_URLS = ["https://www.adidas.co.in/adi_zomato"]
# NUM_VISITS = 6  # Set to 6 for testing; change to 10000 for production
# CONCURRENCY = 3
# BATCH_SIZE = 3  # Small batch for testing; change to 100 for production
# HEADLESS = False
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")
# PROXIES = []
# LOCALES = ["en-US", "en-GB", "hi-IN", "es-ES", "fr-FR", "de-DE", "ja-JP", "zh-CN"]
# TIMEZONES = ["Asia/Kolkata", "Europe/London", "America/New_York", "Asia/Tokyo", "Europe/Paris", "Australia/Sydney"]
# MAX_PROFILES = 50
# CPU_THRESHOLD = 85  # Adjusted slightly higher
# MEMORY_THRESHOLD = 85  # Adjusted slightly higher

# DEVICE_VIEWPORTS = {
#     "desktop": [(1920, 1080), (1366, 768), (1440, 900)],
#     "laptop": [(1366, 768), (1280, 800), (1440, 900)],
#     "smartphone": [(360, 640), (414, 896), (375, 812)],
#     "tablet": [(768, 1024), (810, 1080), (834, 1194)],
# }

# ACTIVE_DRIVERS = []
# driver_lock = threading.Lock()
# interaction_history = {}
# semaphore = asyncio.Semaphore(CONCURRENCY)

# # Setup logging
# log_dir = os.path.dirname(os.path.abspath(__file__))
# os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
# error_log = os.path.join(log_dir, "logs", "error_log.txt")
# info_log = os.path.join(log_dir, "logs", "info_log.txt")
# failed_log = os.path.join(log_dir, "logs", "failed_visits.log")
# logging.basicConfig(filename=error_log, level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
# info_logger = logging.getLogger("info")
# info_handler = logging.FileHandler(info_log)
# info_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
# info_logger.addHandler(info_handler)
# info_logger.setLevel(logging.INFO)
# failed_logger = logging.getLogger("failed")
# failed_handler = logging.FileHandler(failed_log)
# failed_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
# failed_logger.addHandler(failed_handler)
# failed_logger.setLevel(logging.INFO)

# def cleanup_processes():
#     max_cleanup_attempts = 7
#     for attempt in range(max_cleanup_attempts):
#         with driver_lock:
#             os.system("taskkill /F /IM chrome.exe 2>nul")
#             os.system("taskkill /F /IM chromedriver.exe 2>nul")
#             time.sleep(4)
#             if not any(p.name().lower() in ["chrome.exe", "chromedriver.exe"] for p in psutil.process_iter()):
#                 info_logger.info("All Chrome/Chromedriver processes cleaned up")
#                 return True
#         time.sleep(2)
#     logging.error("Failed to clean up all Chrome/Chromedriver processes after max attempts")
#     return False

# def check_resources():
#     cpu_percent = psutil.cpu_percent(interval=1)
#     memory_percent = psutil.virtual_memory().percent
#     if cpu_percent > CPU_THRESHOLD or memory_percent > MEMORY_THRESHOLD:
#         info_logger.info(f"Resource threshold exceeded: CPU {cpu_percent}%, Memory {memory_percent}%")
#         return False
#     return True

# def cleanup_profiles():
#     profile_dir = os.path.join(log_dir, "browser_profiles")
#     if os.path.exists(profile_dir):
#         profiles = [f for f in os.listdir(profile_dir) if f.startswith("profile_")]
#         if len(profiles) > MAX_PROFILES:
#             profiles.sort(key=lambda x: os.path.getmtime(os.path.join(profile_dir, x)))
#             for profile in profiles[:-MAX_PROFILES]:
#                 try:
#                     shutil.rmtree(os.path.join(profile_dir, profile))
#                     info_logger.info(f"Deleted old profile: {profile}")
#                 except Exception as e:
#                     logging.error(f"Failed to delete profile {profile}: {e}")

# def generate_fingerprinting(session_id):
#     device_os_mapping = {
#         "desktop": ["Windows", "macOS"],
#         "laptop": ["Windows", "macOS"],
#         "smartphone": ["Android", "iOS"],
#         "tablet": ["Android", "iOS"],
#     }

#     user_agents = {
#         "Windows": [
#             "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "macOS": [
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
#         ],
#         "Android": [
#             "Mozilla/5.0 (Linux; Android {0}.{1}; SM-G{5}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
#         ],
#         "iOS": [
#             "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.0 Mobile/{4} Safari/{2}.36",
#         ],
#     }

#     device_type = random.choice(list(device_os_mapping.keys()))
#     os = random.choice(device_os_mapping[device_type])
#     version_main = random.randint(10, 14)
#     version_minor = random.randint(0, 5)
#     webkit_version = random.randint(537, 605)
#     chrome_version = random.randint(110, 125)
#     build_version = random.randint(1000, 5000)
#     device_model = random.randint(900, 999)
#     user_agent = random.choice(user_agents[os]).format(
#         version_main, version_minor, webkit_version, chrome_version, build_version, device_model
#     )
#     viewport = random.choice(DEVICE_VIEWPORTS[device_type])
#     webgl_renderer = random.choice(["ANGLE (NVIDIA)", "Intel(R) UHD Graphics", "Mali-G72"])
#     webgl_vendor = random.choice(["Google Inc.", "Intel Inc.", "ARM"])
#     connection_types = ["4g", "wifi", "5g"]
#     battery_levels = [random.uniform(0.4, 1.0) for _ in range(3)]
#     cookie_value = hashlib.sha256(f"{session_id}{random.randint(0, 1000000)}".encode()).hexdigest()[:16]

#     fingerprint = {
#         "session_id": session_id,
#         "device_type": device_type,
#         "os": os,
#         "user_agent": user_agent,
#         "viewport": viewport,
#         "webgl_vendor": webgl_vendor,
#         "webgl_renderer": webgl_renderer,
#         "language": random.choice(LOCALES),
#         "timezone": random.choice(TIMEZONES),
#         "plugin_list": random.sample(["Chrome PDF Viewer", "Widevine"], k=1),
#         "hardware_concurrency": random.choice([4, 8]),
#         "device_memory": random.choice([4, 8]),
#         "canvas_hash": hashlib.sha256(f"{session_id}{random.randint(0, 1000000)}".encode()).hexdigest()[:16],
#         "webgl_hash": hashlib.sha256(f"{session_id}{random.randint(0, 1000000)}".encode()).hexdigest()[:16],
#         "navigator_platform": random.choice(["Win32", "MacIntel"]),
#         "do_not_track": random.choice(["1", "0"]),
#         "screen_width": viewport[0],
#         "screen_height": viewport[1],
#         "device_pixel_ratio": random.choice([1, 2, 2.5]),
#         "accept_language": f"{random.choice(LOCALES).lower()};q=0.{random.randint(7, 9)}",
#         "connection_type": random.choice(connection_types),
#         "battery_level": random.choice(battery_levels),
#         "cookie_value": cookie_value,
#         "app_version": f"{chrome_version}.0.{random.randint(0, 9)}.{random.randint(0, 9)}",
#         "product_sub": f"202{random.randint(3, 5)}0{random.randint(7, 9)}"
#     }
#     info_logger.info(f"Session #{session_id}: Fingerprint generated")
#     return fingerprint

# def signal_handler(sig, frame):
#     print("Interrupt received. Closing drivers...")
#     info_logger.info("Interrupt received. Closing all drivers.")
#     for driver in ACTIVE_DRIVERS:
#         try:
#             driver.quit()
#         except:
#             pass
#     cleanup_processes()
#     print("All drivers terminated.")
#     sys.exit(0)

# def spoof_js_script(fingerprinting):
#     voices = [f"{fingerprinting['language'].split('-')[0]} Voice {i}" for i in range(1, 3)]
#     voices_js_array = "[" + ",".join([f'{{name: "{voice.replace('"', '\\"')}", lang: "{fingerprinting["language"].replace('"', '\\"')}", default: {i == 1}}}' for i, voice in enumerate(voices, 1)]) + "]"
#     return f"""
#     try {{
#         Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}', configurable: true }});
#         Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}', configurable: true }});
#         Object.defineProperty(navigator, 'webdriver', {{ get: () => false, configurable: true }});
#         Object.defineProperty(navigator, 'plugins', {{ get: () => {json.dumps(fingerprinting["plugin_list"])}, configurable: true }});
#         Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'], configurable: true }});
#         Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]}, configurable: true }});
#         Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]}, configurable: true }});
#         Object.defineProperty(navigator, 'appVersion', {{ get: () => '{fingerprinting["app_version"]}', configurable: true }});
#         Object.defineProperty(navigator, 'productSub', {{ get: () => '{fingerprinting["product_sub"]}', configurable: true }});
#         Object.defineProperty(navigator, 'connection', {{ get: () => {{ return {{ effectiveType: '{fingerprinting["connection_type"]}' }}; }}, configurable: true }});
#         Object.defineProperty(navigator, 'battery', {{ get: () => {{ return {{ level: {fingerprinting["battery_level"]}, charging: {random.choice(['true', 'false'])} }}; }}, configurable: true }});
#         const getParameter = WebGLRenderingContext.prototype.getParameter;
#         WebGLRenderingContext.prototype.getParameter = function(param) {{
#             if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
#             if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
#             return getParameter.call(this, param);
#         }};
#         HTMLCanvasElement.prototype.toDataURL = function() {{
#             return 'data:image/png;base64,{fingerprinting["canvas_hash"]}';
#         }};
#         Object.defineProperty(window, 'speechSynthesis', {{
#             get: () => {{ return {{ getVoices: () => JSON.parse('{voices_js_array}') }}; }},
#             configurable: true
#         }});
#         Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
#             return {{ timeZone: '{fingerprinting["timezone"]}' }};
#         }};
#     }} catch (e) {{
#         console.warn('Spoofing error:', e);
#     }}
#     """

# def human_mouse_move(driver, action, x_start, y_start, x_end, y_end, steps=10):
#     points = []
#     for t in range(steps + 1):
#         t = t / steps
#         x = x_start + (x_end - x_start) * t + random.randint(-10, 10) * math.sin(t * math.pi)
#         y = y_start + (y_end - y_start) * t + random.randint(-10, 10) * math.cos(t * math.pi)
#         points.append((int(x), int(y)))
#     for x, y in points:
#         try:
#             action.move_by_offset(x - action.x, y - action.y).perform()
#             action.x, action.y = x, y
#             time.sleep(random.uniform(0.02, 0.08))
#         except:
#             action.reset_actions()
#     action.reset_actions()

# def micro_interaction(driver, action, width, height):
#     choice = random.choice(["wiggle", "mini_scroll", "tab_focus"])
#     if choice == "wiggle":
#         x_start, y_start = action.x, action.y
#         x_end = x_start + random.randint(-8, 8)
#         y_end = y_start + random.randint(-8, 8)
#         human_mouse_move(driver, action, x_start, y_start, x_end, y_end, steps=3)
#         info_logger.info(f"Micro-interaction: Mouse wiggled to ({x_end}, {y_end})")
#         return random.uniform(0.2, 0.6)
#     elif choice == "mini_scroll":
#         scroll_y = random.randint(30, 100)
#         driver.execute_script(f"window.scrollBy({{ top: {scroll_y}, behavior: 'smooth' }});")
#         info_logger.info(f"Micro-interaction: Mini scrolled by {scroll_y}px")
#         return random.uniform(0.4, 0.8)
#     else:
#         driver.execute_script("window.blur(); window.focus();")
#         info_logger.info("Micro-interaction: Simulated tab focus")
#         return random.uniform(0.2, 0.6)

# def simulate_interaction(driver, session_id, total_time=90):
#     action = ActionChains(driver)
#     total_time_spent = 0
#     width = driver.execute_script("return window.innerWidth") or 800
#     height = driver.execute_script("return window.innerHeight") or 600
#     action.x, action.y = random.randint(0, width // 2), random.randint(0, height // 2)
#     interaction_history[session_id] = []

#     interaction_weights = {
#         "mouse_move": 0.3,
#         "scroll": 0.25,
#         "click": 0.2,
#         "hover": 0.15,
#         "type": 0.05,
#         "navigate": 0.03,
#         "filter_click": 0.02
#     }

#     try:
#         time.sleep(random.uniform(5, 10))
#         total_time_spent += random.uniform(5, 10)

#         try:
#             consent_button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(@class, 'consent')]"))
#             )
#             action.move_to_element(consent_button).pause(random.uniform(0.4, 0.8)).click().perform()
#             time.sleep(random.uniform(0.5, 2))
#             total_time_spent += random.uniform(0.5, 2)
#         except:
#             pass

#         states = ["browsing", "engaging", "exploring"]
#         current_state = random.choice(states)
#         max_actions = random.randint(5, 10)

#         for _ in range(max_actions):
#             if total_time_spent >= total_time:
#                 break

#             if random.random() < 0.3:
#                 current_state = random.choice(states)

#             possible_interactions = (
#                 ["scroll", "mouse_move", "hover"] if current_state == "browsing" else
#                 ["click", "type", "navigate", "filter_click"] if current_state == "engaging" else
#                 ["mouse_move", "hover", "scroll", "click"]
#             )

#             recent_interactions = interaction_history[session_id][-1:]
#             available_interactions = [i for i in possible_interactions if i not in recent_interactions]
#             if not available_interactions:
#                 available_interactions = possible_interactions

#             interaction = random.choices(
#                 available_interactions,
#                 weights=[interaction_weights[i] for i in available_interactions],
#                 k=1
#             )[0]
#             interaction_history[session_id].append(interaction)

#             if random.random() < 0.3:
#                 pause = micro_interaction(driver, action, width, height)
#                 total_time_spent += pause

#             if interaction == "mouse_move":
#                 x_start, y_start = action.x, action.y
#                 x_end = random.randint(0, width)
#                 y_end = random.randint(0, height)
#                 human_mouse_move(driver, action, x_start, y_start, x_end, y_end)
#                 pause = random.uniform(0.3, 1.5)
#                 time.sleep(pause)
#                 total_time_spent += pause

#             elif interaction == "scroll":
#                 scroll_type = random.choice(["smooth", "jump"])
#                 scroll_distance = random.randint(100, 800)
#                 if scroll_type == "smooth":
#                     driver.execute_script(f"window.scrollBy({{ top: {scroll_distance}, behavior: 'smooth' }});")
#                     pause = random.uniform(1, 3)
#                 else:
#                     scroll_pos = random.randint(0, driver.execute_script("return document.body.scrollHeight") or height)
#                     driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
#                     pause = random.uniform(1, 4)
#                 time.sleep(pause)
#                 total_time_spent += pause

#             elif interaction == "click":
#                 try:
#                     elements = driver.find_elements(By.XPATH, "//a | //button | //div[contains(@class, 'product')]")
#                     if elements:
#                         element = random.choice(elements)
#                         if element.is_displayed() and element.is_enabled():
#                             action.move_to_element(element).pause(random.uniform(0.3, 1)).click().perform()
#                             pause = random.uniform(2, 5)
#                             time.sleep(pause)
#                             total_time_spent += pause
#                             if random.random() < 0.3:
#                                 driver.back()
#                                 time.sleep(random.uniform(0.5, 2))
#                                 total_time_spent += random.uniform(0.5, 2)
#                 except:
#                     pass

#             elif interaction == "hover":
#                 try:
#                     elements = driver.find_elements(By.XPATH, "//a | //button | //img | //div[contains(@class, 'product')]")
#                     if elements:
#                         element = random.choice(elements)
#                         action.move_to_element(element).pause(random.uniform(0.5, 2)).perform()
#                         pause = random.uniform(0.5, 2)
#                         time.sleep(pause)
#                         total_time_spent += pause
#                 except:
#                     pass

#             elif interaction == "type":
#                 try:
#                     inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='search']")
#                     if inputs:
#                         input_field = random.choice(inputs)
#                         if input_field.is_displayed():
#                             action.move_to_element(input_field).click().perform()
#                             fake_text = "".join(random.choices("abcdefghijklmnopqrstuvwxyz ", k=random.randint(5, 15)))
#                             for char in fake_text:
#                                 input_field.send_keys(char)
#                                 time.sleep(random.uniform(0.03, 0.1))
#                             if random.random() < 0.5:
#                                 input_field.send_keys(Keys.ENTER)
#                             pause = random.uniform(1, 4)
#                             time.sleep(pause)
#                             total_time_spent += pause
#                 except:
#                     pass

#             elif interaction == "navigate":
#                 try:
#                     links = driver.find_elements(By.XPATH, "//a[@href and not(contains(@href, 'javascript'))]")
#                     if links:
#                         link = random.choice(links)
#                         if link.is_displayed():
#                             action.move_to_element(link).pause(random.uniform(0.3, 1)).click().perform()
#                             pause = random.randint(3, 6)
#                             time.sleep(pause)
#                             total_time_spent += pause
#                             if random.random() < 0.4:
#                                 driver.back()
#                                 time.sleep(random.uniform(0.5, 2))
#                                 total_time_spent += random.uniform(0.5, 2)
#                 except:
#                     pass

#             elif interaction == "filter_click":
#                 try:
#                     filters = driver.find_elements(By.XPATH, "//div[contains(@class, 'filter') or contains(@class, 'sort')] | //button[contains(@class, 'filter')]")
#                     if filters:
#                         filter_element = random.choice(filters)
#                         if filter_element.is_displayed() and filter_element.is_enabled():
#                             action.move_to_element(filter_element).pause(random.uniform(0.3, 1)).click().perform()
#                             pause = random.uniform(2, 4)
#                             time.sleep(pause)
#                             total_time_spent += pause
#                 except:
#                     pass

#             time.sleep(random.uniform(0.2, 1))
#             total_time_spent += random.uniform(0.2, 1)

#         if total_time_spent < total_time:
#             time.sleep(total_time - total_time_spent)

#     except Exception as e:
#         failed_logger.error(f"Session #{session_id}: Interaction error: {e}")

# @backoff.on_exception(backoff.expo, Exception, max_tries=7, max_time=120)
# def create_driver(session_id, fingerprinting, profile_folder, headless):
#     time.sleep(random.uniform(0.5, 2))  # Stagger driver creation
#     options = uc.ChromeOptions()
#     options.binary_location = CHROME_BINARY
#     options.add_argument(f"--user-agent={fingerprinting['user_agent']}")
#     options.add_argument(f"--lang={fingerprinting['language']}")
#     options.add_argument(f"--user-data-dir={profile_folder}")
#     options.add_argument(f"--window-size={fingerprinting['viewport'][0]},{fingerprinting['viewport'][1]}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--no-first-run")
#     options.add_argument("--disable-popup-blocking")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--enable-javascript")
#     options.add_argument("--ignore-certificate-errors")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-notifications")
#     if PROXIES:
#         options.add_argument(f"--proxy-server={random.choice(PROXIES)}")
#     if headless:
#         options.add_argument("--headless=new")
#         options.add_argument("--disable-gpu")

#     service = Service(CHROMEDRIVER_PATH, log_path=os.path.join(log_dir, "logs", f"chromedriver_{session_id}.log"))

#     with driver_lock:
#         driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=headless)
#         driver.set_window_size(fingerprinting['viewport'][0], fingerprinting['viewport'][1])
#         driver.execute_script(f"window.resizeTo({fingerprinting['viewport'][0]}, {fingerprinting['viewport'][1]});")
#         ACTIVE_DRIVERS.append(driver)
#         info_logger.info(f"Session #{session_id}: Driver created with UA={fingerprinting['user_agent']}, Viewport={fingerprinting['viewport']}")
#         return driver

# async def simulate_single_visit(session_id, url):
#     async with semaphore:
#         print(f"[*] Session #{session_id}: Starting visit to {url}")
#         info_logger.info(f"Session #{session_id}: Starting visit")
#         fingerprinting = generate_fingerprinting(session_id)
#         profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
#         os.makedirs(profile_folder, exist_ok=True)

#         driver = None
#         try:
#             if not check_resources():
#                 print(f"[*] Session #{session_id}: Waiting for resources...")
#                 await asyncio.sleep(random.uniform(10, 30))
#             if not cleanup_processes():
#                 raise Exception("Process cleanup failed")

#             driver = create_driver(session_id, fingerprinting, profile_folder, HEADLESS)
#             start_time = time.time()
#             max_attempts = 3
#             success = False

#             for attempt in range(1, max_attempts + 1):
#                 print(f"[*] Session #{session_id}: Attempt {attempt}/{max_attempts}")
#                 try:
#                     driver.get(url)
#                     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#                     info_logger.info(f"Session #{session_id}: Page loaded successfully")
#                     print(f"[*] Session #{session_id}: Page loaded")

#                     try:
#                         cookie_domain = '.' + url.split('/')[2]
#                         driver.add_cookie({"name": "session_id", "value": fingerprinting['cookie_value'], "domain": cookie_domain, "path": "/"})
#                         info_logger.info(f"Session #{session_id}: Cookie set")
#                     except:
#                         pass

#                     try:
#                         driver.execute_script(spoof_js_script(fingerprinting))
#                         info_logger.info(f"Session #{session_id}: Fingerprint spoofing applied")
#                     except:
#                         pass

#                     if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
#                         print(f"[!] Session #{session_id}: Cloudflare detected (Attempt {attempt}/{max_attempts})")
#                         info_logger.info(f"Session #{session_id}: Cloudflare detected")
#                         await asyncio.sleep(random.uniform(10, 20))
#                         try:
#                             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#                         except:
#                             continue

#                     visit_time = random.randint(60, 100)
#                     simulate_interaction(driver, session_id, visit_time)
#                     await asyncio.sleep(random.uniform(3, 8))
#                     print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
#                     info_logger.info(f"Session #{session_id}: Completed in {round(time.time() - start_time)} seconds")
#                     success = True
#                     break

#                 except Exception as e:
#                     failed_logger.error(f"Session #{session_id}: Attempt {attempt} failed: {e}")
#                     print(f"[!] Session #{session_id}: Attempt {attempt} failed: {e}")
#                     if attempt < max_attempts:
#                         if driver:
#                             try:
#                                 driver.quit()
#                             except:
#                                 pass
#                         await asyncio.sleep(random.uniform(5, 10))
#                         driver = create_driver(session_id, fingerprinting, profile_folder, HEADLESS)
#                     else:
#                         raise

#             if not success:
#                 print(f"[x] Session #{session_id}: Failed after {max_attempts} attempts")
#                 failed_logger.info(f"Session #{session_id}: Failed after {max_attempts} attempts")

#         except Exception as e:
#             print(f"[x] Session #{session_id}: Overall failure: {e}")
#             failed_logger.error(f"Session #{session_id}: Overall failure: {e}")

#         finally:
#             if driver and driver in ACTIVE_DRIVERS:
#                 ACTIVE_DRIVERS.remove(driver)
#                 try:
#                     driver.quit()
#                     info_logger.info(f"Session #{session_id}: Driver closed")
#                 except:
#                     pass
#             try:
#                 shutil.rmtree(profile_folder)
#                 info_logger.info(f"Session #{session_id}: Profile deleted")
#             except:
#                 pass
#             cleanup_processes()

# async def main():
#     signal.signal(signal.SIGINT, signal_handler)
#     print("Cleaning up existing Chrome processes...")
#     cleanup_processes()

#     print("Chrome binary:", os.path.exists(CHROME_BINARY))
#     print("Chromedriver:", os.path.exists(CHROMEDRIVER_PATH))

#     total_visits = NUM_VISITS
#     completed_visits = 0

#     while completed_visits < total_visits:
#         batch_visits = min(BATCH_SIZE, total_visits - completed_visits)
#         tasks = []
#         for i in range(batch_visits):
#             visit_id = completed_visits + i + 1
#             for url in TARGET_URLS:
#                 tasks.append(simulate_single_visit(visit_id, url))

#         await asyncio.gather(*tasks, return_exceptions=True)
#         completed_visits += batch_visits
#         cleanup_profiles()

#         if completed_visits < total_visits:
#             print(f"[*] Completed {completed_visits}/{total_visits} visits. Pausing before next batch...")
#             await asyncio.sleep(random.uniform(10, 20))

# if __name__ == "__main__":
#     start_time = time.time()
#     asyncio.run(main())
#     print(f"[✅] All visits completed in {round(time.time() - start_time, 2)} seconds.")




# ****
import os
import time
import random
import hashlib
import logging
import sys
import signal
import threading
import math
import traceback
import json
from concurrent.futures import ThreadPoolExecutor
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psutil

# === CONFIGURATION ===
# TARGET_URLS = ["https://www.nike.com/"]
# TARGET_URLS = ["https://marcadeo.com/"]
TARGET_URLS = ["https://unfilteredgadgets.com/"]
NUM_VISITS = 10 
CONCURRENCY = 2  # Set to 2 for your test case
HEADLESS = False
CHROME_BINARY = os.path.abspath("C:\\traffic_bots\\Chrome\\chrome.exe")
CHROMEDRIVER_PATH = os.path.abspath("C:\\traffic_bots\\chromedriver-win64\\chromedriver.exe")
PROXIES = []
VIEWPORTS = [(1280, 720), (1366, 768), (1440, 900), (1920, 1080), (1024, 768), (1600, 900)]
LOCALES = ["en-US", "en-GB", "hi-IN", "es-ES", "fr-FR", "de-DE", "ja-JP", "zh-CN"]
TIMEZONES = ["Asia/Kolkata", "Europe/London", "America/New_York", "Asia/Tokyo", "Europe/Paris", "Australia/Sydney"]

ACTIVE_DRIVERS = []
driver_lock = threading.Lock()  # Add lock for thread safety

# Setup logging (unchanged)
log_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
error_log = os.path.join(log_dir, "logs", "error_log.txt")
info_log = os.path.join(log_dir, "logs", "info_log.txt")
logging.basicConfig(filename=error_log, level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
info_logger = logging.getLogger("info")
info_handler = logging.FileHandler(info_log)
info_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
info_logger.addHandler(info_handler)
info_logger.setLevel(logging.INFO)

def generate_fingerprinting(session_id):
    device_os_mapping = {
        "desktop": ["Windows", "macOS", "Linux", "Fedora"],
        "laptop": ["Windows", "macOS", "Linux", "ChromeOS", "Fedora"],
        "ultrabook": ["Windows", "macOS", "Linux", "Fedora"],
        "macbook": ["macOS"],
        "chromebook": ["ChromeOS"],
        "smartphone": ["Windows", "Android", "iOS"],
        "android_phone": ["Android"],
        "iphone": ["iOS"],
        "tablet": ["Android", "iOS"],
        "ipad": ["iPadOS"],
        "android_tablet": ["Android"],
        "smart_tv": ["Android TV", "Tizen", "WebOS"],
    }

    user_agents = {
        "Windows": [
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Midori/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Falkon/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Opera/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Safari/{3}.0.0.0",
            "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36"
        ],
        "Fedora": [
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/76.0.4017.154 Safari/537.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.26.74 Safari/537.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Vivaldi/4.2.2406.44 Safari/537.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Konqueror/5.0.97 Safari/537.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Epiphany/40.1 Safari/537.36"
        ],
        "iPadOS": [
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Opera/73.0.3856.257 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Vivaldi/4.2.2406.44 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.31.87 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) UC Browser/13.4.0.1307 Safari/537.36"
        ],
        "macOS": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Safari/{3}.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Microsoft Edge/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36"
        ],
        "Linux": [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Falkon/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Midori/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Arch Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; Manjaro Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36"
        ],
        "Android": [
            "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) EdgA/{3}.0.{4}.0 Mobile Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Mobile Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Mobile Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) DuckDuckGo/{3}.0.{4}.0 Mobile Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Mobile Safari/{2}.36"
        ],
        "iOS": [
            "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) EdgiOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) DuckDuckGo/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
            "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) EdgiOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36"
        ],
        "ChromeOS": [
            "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; CrOS armv7l {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; Google Pixelbook) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; ASUS Chromebook) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; Acer Chromebook Spin) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; Samsung Chromebook) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36"
        ],
        "Tizen": [
            "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (SMART-TV; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}; Samsung SmartTV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}; Samsung 4K UHD) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
        ],
        "Android TV": [
            "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}; Nexus Player) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}; MiTV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}; SHIELD Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}; Sony BRAVIA 4K GB) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}; Samsung SmartTV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.0.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.0.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.0.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.0.0 Safari/{2}.36"
        ],
        "WebOS": [
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Firefox/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.1 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) WebView/{3}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Opera/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Midori/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Falkon/{3}.0.{4}.0 Safari/{2}.36",
            "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0 Safari/{2}.36",
        ],
    }

    device_type = random.choice(list(device_os_mapping.keys()))
    os = random.choice(device_os_mapping[device_type])
    version_main = random.randint(8, 14)
    version_minor = random.randint(0, 3)
    webkit_version = random.randint(500, 600)
    chrome_version = random.randint(90, 120)
    firefox_version = random.randint(10, 90)
    build_version = random.randint(1000, 5000)
    user_agent = random.choice(user_agents[os]).format(
        version_main, version_minor, webkit_version, chrome_version, firefox_version, build_version
    )
    screen_widths = [1024, 1366, 1920, 2560, 3840]
    screen_heights = [768, 800, 1080, 1200, 1600]
    device_pixel_ratio = [1, 1.25, 1.5, 2, 2.5, 3]
    webgl_renderer = ["ANGLE (NVIDIA)", "Intel(R) UHD Graphics", "AMD Radeon RX"]
    webgl_vendor = ["Google Inc.", "Intel Inc.", "NVIDIA Corporation"]
    timezone = ["UTC", "America/New_York", "Europe/Berlin", "Asia/Tokyo"]
    plugin_list = [
        ["Chrome PDF Viewer", "Widevine Content Decryption Module"],
        ["PDF.js", "Shockwave Flash"],
        ["Java", "Silverlight"]
    ]
    installed_fonts = [
        ["Arial", "Verdana", "Times New Roman"],
        ["Roboto", "Lato", "Montserrat"],
        ["Comic Sans MS", "Courier New"]
    ]
    accept_language = [
        "en-US,en;q=0.9", "fr-FR,fr;q=0.8", "de-DE,de;q=0.9", "es-ES,es;q=0.8"
    ]
    navigator_platform = ["Win32", "Linux x86_64", "MacIntel"]
    speech_synthesis_voices = [
        ["Google UK English Male", "Microsoft Zira"],
        ["Google Deutsch", "Apple Samantha"],
        ["Google Español", "Microsoft David"]
    ]

    viewport = random.choice(VIEWPORTS)  # Reuse VIEWPORTS from config
    # Generate unique cookie per session
    cookie_value = hashlib.sha256(f"{session_id}{random.randint(0, 1000000)}".encode()).hexdigest()[:16]
    return {
        "session_id": session_id,
        "device_type": device_type,
        "os": os,
        "user_agent": user_agent,
        "viewport": viewport,
        "webgl_vendor": random.choice(webgl_vendor),
        "webgl_renderer": random.choice(webgl_renderer),
        "language": random.choice(LOCALES),  # Reuse LOCALES from config
        "timezone": random.choice(timezone),
        "plugin_list": random.choice(plugin_list),
        "installed_fonts": random.choice(installed_fonts),
        "hardware_concurrency": random.choice([4, 8, 12]),
        "device_memory": random.choice([4, 8]),
        "canvas_hash": hashlib.sha256(f"{session_id}{random.randint(0, 1000000)}".encode()).hexdigest()[:16],
        "webgl_hash": hashlib.sha256(f"{session_id}{random.randint(0, 1000000)}".encode()).hexdigest()[:16],
        "navigator_platform": random.choice(navigator_platform),
        "do_not_track": random.choice(["1", "0", None]),
        "screen_width": random.choice(screen_widths),
        "screen_height": random.choice(screen_heights),
        "device_pixel_ratio": random.choice(device_pixel_ratio),
        "accept_language": random.choice(accept_language),
        "speech_synthesis_voices": random.choice(speech_synthesis_voices),
        "cookie_value": cookie_value,
        "app_version": f"{random.randint(90, 120)}.0.0.0",
        "product_sub": f"2023{random.randint(0, 99)}"
    }

def signal_handler(sig, frame):
    print("Interrupt received. Closing drivers...")
    info_logger.info("Interrupt received. Closing all drivers.")
    for driver in ACTIVE_DRIVERS:
        try:
            driver.quit()
            info_logger.info("Driver closed successfully.")
        except Exception as e:
            logging.error(f"Failed to close driver: {e}")
    os.system("taskkill /F /IM chrome.exe")
    os.system("taskkill /F /IM chromedriver.exe")
    print("All drivers terminated.")
    sys.exit(0)

def spoof_js_script(fingerprinting):
    voices = [f"{fingerprinting['language'].split('-')[0]} Voice {i}" for i in range(1, random.randint(2, 5))]
    voices_js_array = "[" + ",".join([f'{{name: "{voice.replace('"', '\\"')}", lang: "{fingerprinting["language"].replace('"', '\\"')}", default: {i == 1}}}' for i, voice in enumerate(voices, 1)]) + "]"
    return f"""
    Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
    Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"] or ''}' }});
    Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});
    Object.defineProperty(navigator, 'plugins', {{ get: () => {json.dumps(fingerprinting["plugin_list"] or [])} }});
    Object.defineProperty(navigator, 'languages', {{ get: () => ['{fingerprinting["language"]}', 'en'] }});
    Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprinting["hardware_concurrency"]} }});
    Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprinting["device_memory"]} }});
    Object.defineProperty(navigator, 'appVersion', {{ get: () => '{fingerprinting["app_version"]}' }});
    Object.defineProperty(navigator, 'productSub', {{ get: () => '{fingerprinting["product_sub"]}' }});
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(param) {{
        if (param === 37445) return '{fingerprinting["webgl_vendor"]}';
        if (param === 37446) return '{fingerprinting["webgl_renderer"]}';
        return getParameter.call(this, param);
    }};
    HTMLCanvasElement.prototype.toDataURL = function() {{
        return 'data:image/png;base64,{fingerprinting["canvas_hash"]}';
    }};
    Object.defineProperty(window, 'speechSynthesis', {{
        get: () => ({{ getVoices: () => JSON.parse('{voices_js_array}') }})
    }});
    Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
        return {{ timeZone: '{fingerprinting["timezone"]}' }};
    }};
    """

def human_mouse_move(driver, action, x_start, y_start, x_end, y_end, steps=15):
    points = []
    for t in range(steps + 1):
        t = t / steps
        x = x_start + (x_end - x_start) * t + random.randint(-30, 30) * math.sin(t * math.pi)
        y = y_start + (y_end - y_start) * t + random.randint(-30, 30) * math.cos(t * math.pi)
        points.append((int(x), int(y)))
    for x, y in points:
        try:
            action.move_by_offset(x - action.x, y - action.y).perform()
            action.x, action.y = x, y
            time.sleep(random.uniform(0.05, 0.2))
        except:
            action.reset_actions()
    action.reset_actions()

def simulate_interaction(driver, session_id, total_time=90):
    action = ActionChains(driver)
    total_time_spent = 0
    width = driver.execute_script("return window.innerWidth") or 1200
    height = driver.execute_script("return window.innerHeight") or 1000
    action.x, action.y = random.randint(0, width // 2), random.randint(0, height // 2)

    try:
        # Initial delay to simulate page load
        initial_delay = random.uniform(2, 5)
        time.sleep(initial_delay)
        total_time_spent += initial_delay
        info_logger.info(f"Session #{session_id}: Initial page load delay")

        # Handle consent if present
        try:
            consent_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(@class, 'consent')]"))
            )
            action.move_to_element(consent_button).pause(random.uniform(0.5, 1)).click().perform()
            info_logger.info(f"Session #{session_id}: Clicked consent button")
            print(f"[*] Session #{session_id}: Clicked consent button")
            time.sleep(random.uniform(1, 2))
            total_time_spent += random.uniform(1, 2)
        except:
            info_logger.info(f"Session #{session_id}: No consent button found")

        # Fixed 1-2 minute target duration
        target_duration = random.uniform(60, 120)
        max_actions = 5  # Limit actions to ensure time fit
        actions_performed = 0

        while total_time_spent < target_duration and actions_performed < max_actions:
            remaining_time = target_duration - total_time_spent
            if remaining_time < 5:  # Minimum time for next action
                break

            action_type = random.choices(
                ["scroll", "click", "hover", "type", "navigate"],
                weights=[0.4, 0.3, 0.15, 0.1, 0.05]
            )[0]

            if action_type == "scroll":
                scroll_type = random.choice(["smooth", "jump"])
                if scroll_type == "smooth":
                    scroll_y = random.randint(200, 600)
                    driver.execute_script(f"window.scrollBy({{ top: {scroll_y}, behavior: 'smooth' }});")
                    info_logger.info(f"Session #{session_id}: Smooth scrolled by {scroll_y}px")
                    print(f"[*] Session #{session_id}: Smooth scrolled by {scroll_y}px")
                    time.sleep(random.uniform(1, 2))
                    total_time_spent += random.uniform(1, 2)
                else:
                    scroll_pos = random.randint(0, int(driver.execute_script("return document.body.scrollHeight") or height))
                    driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
                    info_logger.info(f"Session #{session_id}: Jumped to {scroll_pos}px")
                    print(f"[*] Session #{session_id}: Jumped to {scroll_pos}px")
                    time.sleep(random.uniform(2, 3))
                    total_time_spent += random.uniform(2, 3)

            elif action_type == "click":
                try:
                    elements = driver.find_elements(By.XPATH, "//a | //button | //input | //div[not(@role='presentation')]")
                    if elements:
                        element = random.choice(elements)
                        if element.is_displayed() and element.is_enabled():
                            action.move_to_element(element).pause(random.uniform(0.5, 1)).click().perform()
                            info_logger.info(f"Session #{session_id}: Clicked {element.tag_name}")
                            print(f"[*] Session #{session_id}: Clicked {element.tag_name}")
                            time.sleep(random.uniform(2, 3))
                            total_time_spent += random.uniform(2, 3)
                            if random.random() < 0.3:
                                driver.back()
                                time.sleep(random.uniform(1, 2))
                                total_time_spent += random.uniform(1, 2)
                except Exception as e:
                    logging.error(f"Session #{session_id}: Click error: {e}")

            elif action_type == "hover":
                try:
                    elements = driver.find_elements(By.XPATH, "//a | //button | //div")
                    if elements:
                        element = random.choice(elements)
                        action.move_to_element(element).pause(random.uniform(1, 2)).perform()
                        info_logger.info(f"Session #{session_id}: Hovered over {element.tag_name}")
                        print(f"[*] Session #{session_id}: Hovered over {element.tag_name}")
                        time.sleep(random.uniform(1, 2))
                        total_time_spent += random.uniform(1, 2)
                except Exception as e:
                    logging.error(f"Session #{session_id}: Hover error: {e}")

            elif action_type == "type":
                try:
                    inputs = driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea | //input[@type='search']")
                    if inputs:
                        input_field = random.choice(inputs)
                        if input_field.is_displayed():
                            action.move_to_element(input_field).click().perform()
                            fake_text = "".join(random.choices("abcdefghijklmnopqrstuvwxyz ", k=random.randint(3, 8)))
                            for char in fake_text:
                                input_field.send_keys(char)
                                time.sleep(random.uniform(0.1, 0.2))
                            if random.random() < 0.5:
                                input_field.send_keys(Keys.ENTER)
                            info_logger.info(f"Session #{session_id}: Typed '{fake_text}'")
                            print(f"[*] Session #{session_id}: Typed '{fake_text}'")
                            time.sleep(random.uniform(2, 3))
                            total_time_spent += random.uniform(2, 3)
                except Exception as e:
                    logging.error(f"Session #{session_id}: Typing error: {e}")

            elif action_type == "navigate":
                if random.random() < 0.2:
                    try:
                        links = driver.find_elements(By.TAG_NAME, "a")
                        if links:
                            link = random.choice(links)
                            if link.is_displayed():
                                action.move_to_element(link).pause(random.uniform(0.5, 1)).click().perform()
                                info_logger.info(f"Session #{session_id}: Navigated to new page")
                                print(f"[*] Session #{session_id}: Navigated to new page")
                                time.sleep(random.uniform(3, 4))
                                total_time_spent += random.uniform(3, 4)
                                if random.random() < 0.5:
                                    driver.back()
                                    time.sleep(random.uniform(1, 2))
                                    total_time_spent += random.uniform(1, 2)
                    except Exception as e:
                        logging.error(f"Session #{session_id}: Navigation error: {e}")

            # Bot detection bypass with limited retries
            if "cf-ray" in driver.page_source or "Akamai" in driver.page_source or "CAPTCHA" in driver.page_source:
                retry_count = 0
                max_retries = 2
                while retry_count < max_retries and ("CAPTCHA" in driver.page_source or "cf-ray" in driver.page_source):
                    print(f"[!] Session #{session_id}: Bot detection triggered, retry {retry_count + 1}/{max_retries}")
                    info_logger.info(f"Session #{session_id}: Bot detection triggered, retry {retry_count + 1}")
                    time.sleep(random.uniform(5, 10))
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
                    driver.refresh()
                    time.sleep(random.uniform(3, 5))
                    total_time_spent += random.uniform(3, 5)
                    retry_count += 1
                    if "CAPTCHA" in driver.page_source:
                        print(f"[!] Session #{session_id}: CAPTCHA detected after retries, skipping visit")
                        info_logger.info(f"Session #{session_id}: CAPTCHA detected after retries, visit skipped")
                        return

            # Ensure minimum think time and enforce exact duration
            think_time = min(random.uniform(1, 2), target_duration - total_time_spent)
            time.sleep(think_time)
            total_time_spent += think_time
            actions_performed += 1

        # Force exact 60-120 second duration
        if total_time_spent < target_duration:
            time.sleep(target_duration - total_time_spent)
        total_time_spent = target_duration  # Ensure exact match

    except Exception as e:
        logging.error(f"Session #{session_id}: Interaction error: {e}")
        print(f"[!] Session #{session_id}: Interaction error: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")

def simulate_single_visit(session_id, url):
    print(f"[*] Starting session #{session_id} → {url}")
    info_logger.info(f"Session #{session_id}: Starting visit to {url}")
    fingerprinting = generate_fingerprinting(session_id)
    vp = fingerprinting["viewport"]
    profile_folder = os.path.join("browser_profiles", f"profile_{session_id}")
    os.makedirs("browser_profiles", exist_ok=True)

    # Improved cleanup with lock and retry
    max_cleanup_attempts = 2
    for attempt in range(max_cleanup_attempts):
        with driver_lock:
            os.system("taskkill /F /IM chrome.exe 2>nul")
            os.system("taskkill /F /IM chromedriver.exe 2>nul")
            time.sleep(2)
            if not any("chrome.exe" in p.name() for p in psutil.process_iter() if "chrome" in p.name().lower()):
                break
        if attempt < max_cleanup_attempts - 1:
            time.sleep(2)

    options = uc.ChromeOptions()
    options.binary_location = CHROME_BINARY
    options.add_argument(f"--user-agent={fingerprinting['user_agent']}")
    options.add_argument(f"--lang={fingerprinting['language']}")
    options.add_argument(f"--user-data-dir={profile_folder}")
    options.add_argument(f"--window-size={vp[0]},{vp[1]}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--enable-webgl")
    options.add_argument("--enable-javascript")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    if PROXIES:
        options.add_argument(f"--proxy-server={random.choice(PROXIES)}")

    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    service = Service(CHROMEDRIVER_PATH, log_path=os.path.join(log_dir, "logs", f"chromedriver_{session_id}.log"))

    try:
        driver = None
        max_driver_attempts = 3
        for attempt in range(max_driver_attempts):
            try:
                with driver_lock:
                    driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=HEADLESS, version_main=137)
                driver.set_window_size(vp[0], vp[1])
                driver.execute_script(f"window.resizeTo({vp[0]}, {vp[1]});")
                ACTIVE_DRIVERS.append(driver)
                info_logger.info(f"Session #{session_id}: Driver created with UA: {fingerprinting['user_agent']}, Viewport: {vp}")
                print(f"[*] Session #{session_id}: Created driver with viewport {vp}")
                break
            except Exception as e:
                logging.error(f"Session #{session_id}: Driver creation attempt {attempt + 1} failed: {e}")
                print(f"[!] Session #{session_id}: Driver creation attempt {attempt + 1} failed: {e}")
                if attempt < max_driver_attempts - 1:
                    time.sleep(5)
                else:
                    raise

        start_time = time.time()
        attempts = 0
        max_attempts = 3
        success = False

        while not success and attempts < max_attempts:
            attempts += 1
            print(f"[*] Session #{session_id}: Attempt {attempts}/{max_attempts}")
            try:
                driver.get(url)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                info_logger.info(f"Session #{session_id}: Page loaded successfully")
                print(f"[*] Session #{session_id}: Page loaded")

                try:
                    cookie_domain = '.' + url.split('/')[2]
                    if not cookie_domain.startswith('.'):
                        cookie_domain = f".{cookie_domain}"
                    driver.add_cookie({
                        "name": "session_id",
                        "value": fingerprinting["cookie_value"],
                        "domain": cookie_domain,
                        "path": "/"
                    })
                    info_logger.info(f"Session #{session_id}: Cookie set successfully")
                    print(f"[*] Session #{session_id}: Cookie set")
                except Exception as e:
                    logging.error(f"Session #{session_id}: Failed to set cookie: {e}")
                    print(f"[!] Session #{session_id}: Failed to set cookie: {e}")

                try:
                    driver.execute_script(spoof_js_script(fingerprinting))
                    info_logger.info(f"Session #{session_id}: Fingerprint spoofing applied")
                    print(f"[*] Session #{session_id}: Fingerprint spoofing applied")
                except Exception as e:
                    logging.error(f"Session #{session_id}: Fingerprint spoofing failed: {e}")
                    print(f"[!] Session #{session_id}: Fingerprint spoofing failed: {e}")

                if "cf-ray" in driver.page_source or "Checking your browser" in driver.page_source:
                    print(f"[!] Session #{session_id}: Cloudflare challenge detected (Attempt {attempts}/{max_attempts})")
                    info_logger.info(f"Session #{session_id}: Cloudflare challenge detected")
                    time.sleep(random.uniform(5, 10))
                    continue

                simulate_interaction(driver, session_id)
                time.sleep(random.uniform(1, 2))  # Short buffer
                print(f"[✓] Session #{session_id} completed in {round(time.time() - start_time)} seconds")
                info_logger.info(f"Session #{session_id}: Completed in {round(time.time() - start_time)} seconds")
                success = True

            except Exception as e:
                logging.error(f"Session #{session_id}: Attempt {attempts} failed: {e}")
                print(f"[!] Session #{session_id}: Attempt {attempts} failed: {e}")
                logging.error(f"Traceback: {traceback.format_exc()}")
                if attempts < max_attempts:
                    driver.quit()
                    with driver_lock:
                        driver = uc.Chrome(service=service, options=options, user_data_dir=profile_folder, headless=HEADLESS, version_main=137)
                    time.sleep(random.uniform(5, 10))
                else:
                    raise

        if not success:
            print(f"[x] Session #{session_id}: Failed after {max_attempts} attempts")
            info_logger.info(f"Session #{session_id}: Failed after {max_attempts} attempts")

        if driver in ACTIVE_DRIVERS:
            ACTIVE_DRIVERS.remove(driver)
        driver.quit()
        info_logger.info(f"Session #{session_id}: Driver closed")
        print(f"[*] Session #{session_id}: Driver closed")

    except Exception as e:
        if driver and driver in ACTIVE_DRIVERS:
            ACTIVE_DRIVERS.remove(driver)
            driver.quit()
        logging.error(f"Session #{session_id}: Overall failure: {e}")
        print(f"[x] Session #{session_id}: Overall failure: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    print("Cleaning up existing Chrome processes...")
    os.system("taskkill /F /IM chrome.exe 2>nul")
    os.system("taskkill /F /IM chromedriver.exe 2>nul")
    time.sleep(2)  # Wait for cleanup
    print("Chrome binary:", os.path.exists(CHROME_BINARY))
    print("Chromedriver:", os.path.exists(CHROMEDRIVER_PATH))

    # Resource check for scalability
    def check_resources():
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        return cpu_usage < 80 and memory_usage < 90

    start_time = time.time()
    total_visits = NUM_VISITS
    completed_visits = 0
    max_concurrency = min(CONCURRENCY, 6)  # Cap concurrency for stability

    while completed_visits < total_visits:
        if not check_resources():
            print("[!] System resources overloaded, waiting...")
            time.sleep(30)
            continue

        batch_size = min(max_concurrency, total_visits - completed_visits)
        print(f"[*] Starting batch with {batch_size} visits (Total completed: {completed_visits}/{total_visits})")
        with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
            futures = []
            for _ in range(batch_size):
                visit_id = completed_visits + 1
                for url in TARGET_URLS:
                    futures.append(executor.submit(simulate_single_visit, visit_id, url))
                completed_visits += 1
            
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"[!] Error in future execution: {e}")
                    logging.error(f"Future execution failed: {e}")
                    logging.error(f"Traceback: {traceback.format_exc()}")

        if completed_visits < total_visits:
            print(f"[*] Completed {completed_visits}/{total_visits} visits. Pausing before next batch...")
            time.sleep(random.uniform(5, 10))

    print(f"[✅] All visits completed in {round(time.time() - start_time, 2)} seconds.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[x] Main execution failed: {e}")
        logging.error(f"Main execution failed: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")

# just uper wali 

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
# TARGET_URLS = ["https://marcadeo.com/"]
# NUM_VISITS = 1000 
# CONCURRENCY = 2  # Set to 2 for your test case
# HEADLESS = False
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")
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

# def simulate_interaction(driver, session_id, total_time=90):
#     action = ActionChains(driver)
#     total_time_spent = 0
#     width = driver.execute_script("return window.innerWidth") or 1200
#     height = driver.execute_script("return window.innerHeight") or 1000
#     action.x, action.y = random.randint(0, width // 2), random.randint(0, height // 2)

#     try:
#         # Initial delay to simulate page load
#         initial_delay = random.uniform(2, 5)
#         time.sleep(initial_delay)
#         total_time_spent += initial_delay
#         info_logger.info(f"Session #{session_id}: Initial page load delay")

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
#         except:
#             info_logger.info(f"Session #{session_id}: No consent button found")

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
#                 else:
#                     scroll_pos = random.randint(0, int(driver.execute_script("return document.body.scrollHeight") or height))
#                     driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
#                     info_logger.info(f"Session #{session_id}: Jumped to {scroll_pos}px")
#                     print(f"[*] Session #{session_id}: Jumped to {scroll_pos}px")
#                     time.sleep(random.uniform(2, 3))
#                     total_time_spent += random.uniform(2, 3)

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
#                             if random.random() < 0.3:
#                                 driver.back()
#                                 time.sleep(random.uniform(1, 2))
#                                 total_time_spent += random.uniform(1, 2)
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
#                                 if random.random() < 0.5:
#                                     driver.back()
#                                     time.sleep(random.uniform(1, 2))
#                                     total_time_spent += random.uniform(1, 2)
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
#                     retry_count += 1
#                     if "CAPTCHA" in driver.page_source:
#                         print(f"[!] Session #{session_id}: CAPTCHA detected after retries, skipping visit")
#                         info_logger.info(f"Session #{session_id}: CAPTCHA detected after retries, visit skipped")
#                         return

#             # Ensure minimum think time and enforce exact duration
#             think_time = min(random.uniform(1, 2), target_duration - total_time_spent)
#             time.sleep(think_time)
#             total_time_spent += think_time
#             actions_performed += 1

#         # Force exact 60-120 second duration
#         if total_time_spent < target_duration:
#             time.sleep(target_duration - total_time_spent)
#         total_time_spent = target_duration  # Ensure exact match

#     except Exception as e:
#         logging.error(f"Session #{session_id}: Interaction error: {e}")
#         print(f"[!] Session #{session_id}: Interaction error: {e}")
#         logging.error(f"Traceback: {traceback.format_exc()}")

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
#                 # Check HTTP status by inspecting page content
#                 status_code = "Unknown"
#                 page_source = driver.page_source.lower()
#                 if "403 forbidden" in page_source:
#                     status_code = "403"
#                 elif "404 not found" in page_source:
#                     status_code = "404"
#                 elif "500 internal server error" in page_source:
#                     status_code = "500"
#                 elif driver.execute_script("return document.readyState") == "complete":
#                     status_code = "200"  # Assume success if page loads completely
#                 info_logger.info(f"Session #{session_id}: Page loaded with status {status_code}")
#                 print(f"[*] Session #{session_id}: Page loaded with status {status_code}")

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

#                 simulate_interaction(driver, session_id)
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
# TARGET_URLS = ["https://marcadeo.com/"]
# # TARGET_URLS = ["https://www.adidas.co.in/adi_zomato"] 
# NUM_VISITS = 10
# CONCURRENCY = 2  # Set to 2 for your test case
# HEADLESS = False
# # CHROME_BINARY = os.path.abspath("C:\\traffic_bots\\Chrome\\chrome.exe")
# # CHROMEDRIVER_PATH = os.path.abspath("C:\\traffic_bots\\chromedriver-win64\\chromedriver.exe")
# CHROME_BINARY = os.path.abspath("Chrome/chrome.exe")
# CHROMEDRIVER_PATH = os.path.abspath("chromedriver-win64/chromedriver.exe")
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