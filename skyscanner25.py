#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 17:34:15 2025

@author: user
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTIMATE Anti-Bot Detection Script
Maximum stealth mode - bypass ALL detection
"""

# import time
# import random
# import requests
# import json
# import math
# import base64
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- ULTIMATE CONFIG ----------
# TARGET_URL = "ishan-portfolio.com"
# TOKEN = "CHANGE_ME_TOKEN"

# # MAXIMUM STEALTH SETTINGS
# TOTAL_PROFILES = 1
# PRE_NAVIGATION_DELAY = (15, 25)  # Long delay before going to target site
# HUMAN_BEHAVIOR_TIME = (30, 60)   # Extended human behavior
# PAGE_LOAD_PATIENCE = (8, 15)     # Patient page loading

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     if len(parts) == 1:
#         proto = None
#         main = parts[0]
#     else:
#         proto = parts[0].lower()
#         main = parts[1]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto or "socks5", "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create the most stealthy profile possible"""
#     try:
#         gl = GoLogin({"token": TOKEN})
        
#         print(f"🥷 Creating ULTIMATE stealth profile: {profile_name}")
        
#         # Create profile with random OS selection for diversity
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac", "lin"]),  # Include Linux
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         # Set proxy with error handling
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
                
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         # Update user agent to latest
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with MAXIMUM stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
        
#         print(f"🚀 Starting MAXIMUM stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         # Longer wait for browser stability
#         wait_time = random.uniform(5, 10)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         chromium_version = gl.get_chromium_version()
#         service = Service(ChromeDriverManager(driver_version=chromium_version).install())
        
#         chrome_options = webdriver.ChromeOptions()
#         chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         # ULTIMATE stealth injection
#         inject_ultimate_stealth(driver)
        
#         return gl, driver
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None

# def inject_ultimate_stealth(driver):
#     """Inject ULTIMATE stealth scripts - most comprehensive"""
#     try:
#         print("🛡️ Injecting ULTIMATE stealth protection...")
        
#         # 1. Remove ALL webdriver traces
#         driver.execute_script("""
#             // Remove webdriver property
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined,
#             });
            
#             // Remove webdriver from window
#             delete window.webdriver;
            
#             // Remove automation flags
#             Object.defineProperty(navigator, 'automation', {
#                 get: () => undefined,
#             });
            
#             // Remove webdriver from document
#             delete document.webdriver;
#         """)
        
#         # 2. Mock Chrome runtime
#         driver.execute_script("""
#             // Mock chrome runtime
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 },
#                 storage: {
#                     local: {
#                         get: () => {},
#                         set: () => {},
#                     }
#                 }
#             };
#         """)
        
#         # 3. Advanced plugin mocking
#         driver.execute_script("""
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [
#                     {
#                         0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
#                         description: "Portable Document Format",
#                         filename: "internal-pdf-viewer",
#                         length: 1,
#                         name: "Chrome PDF Plugin"
#                     },
#                     {
#                         0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin},
#                         description: "",
#                         filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
#                         length: 1,
#                         name: "Chrome PDF Viewer"
#                     },
#                     {
#                         description: "Shockwave Flash",
#                         filename: "pepflashplayer.dll",
#                         name: "Shockwave Flash"
#                     }
#                 ]
#             });
#         """)
        
#         # 4. Mock languages and timezone
#         driver.execute_script("""
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN', 'hi'],
#             });
            
#             // Mock timezone
#             Date.prototype.getTimezoneOffset = function() {
#                 return -330; // IST timezone
#             };
#         """)
        
#         # 5. Advanced WebGL spoofing
#         driver.execute_script("""
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 // Mock real GPU signatures
#                 if (parameter === 37445) {
#                     return 'Intel Inc.';
#                 }
#                 if (parameter === 37446) {
#                     return 'Intel(R) UHD Graphics 630';
#                 }
#                 return getParameter.call(this, parameter);
#             };
#         """)
        
#         # 6. Mock screen properties realistically
#         driver.execute_script("""
#             Object.defineProperty(screen, 'availWidth', {
#                 get: () => 1920
#             });
#             Object.defineProperty(screen, 'availHeight', {
#                 get: () => 1040
#             });
#             Object.defineProperty(screen, 'width', {
#                 get: () => 1920
#             });
#             Object.defineProperty(screen, 'height', {
#                 get: () => 1080
#             });
#         """)
        
#         # 7. Mock permissions API
#         driver.execute_script("""
#             const originalQuery = window.navigator.permissions.query;
#             window.navigator.permissions.query = (parameters) => (
#                 parameters.name === 'notifications' ?
#                     Promise.resolve({ state: Notification.permission }) :
#                     originalQuery(parameters)
#             );
#         """)
        
#         # 8. Advanced mouse event mocking
#         driver.execute_script("""
#             // Mock mouse events
#             let mouseX = 0, mouseY = 0;
#             document.addEventListener('mousemove', (e) => {
#                 mouseX = e.clientX;
#                 mouseY = e.clientY;
#             });
            
#             // Mock realistic mouse behavior
#             Object.defineProperty(MouseEvent.prototype, 'isTrusted', {
#                 get: () => true
#             });
#         """)
        
#         print("✅ ULTIMATE stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def pre_navigation_warmup(driver):
#     """Warm up browser with innocent sites before target"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
        
#         innocent_sites = [
#             "https://www.google.co.in",
#             "https://www.wikipedia.org",
#             "https://www.github.com"
#         ]
        
#         for i, site in enumerate(innocent_sites):
#             print(f"🌐 Warming up {i+1}/{len(innocent_sites)}: {site}")
            
#             driver.get(site)
            
#             # Wait for page load
#             wait_time = random.uniform(3, 6)
#             time.sleep(wait_time)
            
#             # Light human behavior
#             perform_light_interaction(driver)
            
#             # Wait between sites
#             if i < len(innocent_sites) - 1:
#                 wait_time = random.uniform(4, 8)
#                 print(f"⏳ Cooling down: {wait_time:.1f}s")
#                 time.sleep(wait_time)
        
#         # Final warm-up delay
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
        
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")

# def perform_light_interaction(driver):
#     """Light human interactions during warmup"""
#     try:
#         # Small scroll
#         scroll_distance = random.randint(100, 400)
#         driver.execute_script(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(1, 3))
        
#         # Mouse movement to random element
#         try:
#             elements = driver.find_elements(By.CSS_SELECTOR, "a, button, input")
#             if elements:
#                 random_element = random.choice(elements[:5])
#                 if random_element.is_displayed():
#                     ActionChains(driver).move_to_element(random_element).perform()
#                     time.sleep(random.uniform(0.5, 2))
#         except:
#             pass
            
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def ultimate_human_browsing(driver):
#     """ULTIMATE human-like browsing behavior"""
#     try:
#         print("🎭 Starting ULTIMATE human behavior simulation...")
        
#         # Patient navigation to target
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         driver.get(TARGET_URL)
        
#         # Very patient page load wait
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         # Check for CAPTCHA or blocks
#         if detect_and_handle_challenges(driver):
#             return True
        
#         # Wait for page elements
#         try:
#             WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "body"))
#             )
#             print("📄 Page elements detected")
#         except TimeoutException:
#             print("⚠️ Page load timeout, continuing...")
        
#         # Extended human behavior
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice([
#                 'realistic_scroll', 'mouse_trail', 'reading_pause', 
#                 'element_hover', 'focus_simulation', 'typing_simulation'
#             ])
            
#             execute_human_action(driver, action)
#             time.sleep(random.uniform(1, 4))
        
#         print("✅ Ultimate human behavior complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False

# def detect_and_handle_challenges(driver):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = driver.current_url
#         page_source = driver.page_source.lower()
        
#         # Check for common challenge indicators
#         challenge_indicators = [
#             'captcha', 'robot', 'verify', 'challenge', 
#             'access denied', 'blocked', 'security check'
#         ]
        
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
            
#             # Try to handle different types of challenges
#             if 'captcha' in current_url.lower() or 'captcha' in page_source:
#                 print("🧩 CAPTCHA challenge detected")
#                 handle_captcha_page(driver)
            
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_captcha_page(driver):
#     """Handle CAPTCHA page with human-like behavior"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
        
#         # Look for buttons or interactive elements
#         button_selectors = [
#             "button",
#             "[role='button']",
#             ".button",
#             "input[type='button']",
#             "input[type='submit']",
#             "[onclick]"
#         ]
        
#         for selector in button_selectors:
#             try:
#                 elements = driver.find_elements(By.CSS_SELECTOR, selector)
#                 for element in elements:
#                     if element.is_displayed() and element.is_enabled():
#                         text = element.text.lower()
#                         if any(word in text for word in ['continue', 'proceed', 'verify', 'submit']):
#                             print(f"🔄 Found action button: {element.text}")
                            
#                             # Human-like click
#                             actions = ActionChains(driver)
#                             actions.move_to_element(element)
#                             actions.pause(random.uniform(2, 5))
#                             actions.click()
#                             actions.perform()
                            
#                             # Wait for response
#                             time.sleep(random.uniform(3, 8))
#                             return
#             except:
#                 continue
        
#         # If no buttons found, wait and see
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(10, 20))
        
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def execute_human_action(driver, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             # Natural scrolling patterns
#             for _ in range(random.randint(2, 5)):
#                 scroll_distance = random.randint(100, 300)
#                 driver.execute_script(f"""
#                     window.scrollBy({{
#                         top: {scroll_distance},
#                         left: 0,
#                         behavior: 'smooth'
#                     }});
#                 """)
#                 time.sleep(random.uniform(1.5, 3.5))
                
#         elif action == 'mouse_trail':
#             # Create realistic mouse movement trail
#             elements = driver.find_elements(By.CSS_SELECTOR, "div, span, p, h1, h2, a")[:10]
#             if elements:
#                 actions = ActionChains(driver)
#                 for element in random.sample(elements, min(3, len(elements))):
#                     if element.is_displayed():
#                         actions.move_to_element(element)
#                         actions.pause(random.uniform(0.8, 2.2))
#                 actions.perform()
                
#         elif action == 'reading_pause':
#             # Simulate reading with eye movement patterns
#             time.sleep(random.uniform(3, 8))
            
#         elif action == 'element_hover':
#             # Hover over interesting elements
#             try:
#                 links = driver.find_elements(By.TAG_NAME, "a")[:5]
#                 if links:
#                     random_link = random.choice(links)
#                     if random_link.is_displayed():
#                         ActionChains(driver).move_to_element(random_link).pause(2).perform()
#             except:
#                 pass
                
#         elif action == 'focus_simulation':
#             # Simulate window focus changes
#             driver.execute_script("window.blur();")
#             time.sleep(random.uniform(1, 3))
#             driver.execute_script("window.focus();")
            
#         elif action == 'typing_simulation':
#             # Simulate typing in search boxes (if any)
#             try:
#                 inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='search']")
#                 if inputs:
#                     random_input = random.choice(inputs[:2])
#                     if random_input.is_displayed() and random_input.is_enabled():
#                         # Human-like typing
#                         test_words = ["delhi", "mumbai", "bangalore", "flight"]
#                         word = random.choice(test_words)
                        
#                         random_input.click()
#                         time.sleep(random.uniform(0.5, 1.5))
                        
#                         for char in word:
#                             random_input.send_keys(char)
#                             time.sleep(random.uniform(0.1, 0.3))
                        
#                         time.sleep(random.uniform(1, 3))
#                         random_input.clear()
#             except:
#                 pass
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the ultimate stealth test"""
#     print("🎯 ULTIMATE STEALTH MODE ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"ultimate_stealth_{profile_num}_{random.randint(100000, 999999)}"
        
#         # Get proxy
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         # Create profile
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             # Extended wait before browser start
#             wait_time = random.uniform(8, 15)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             # Start browser
#             gl, driver = start_maximum_stealth_browser(profile_id)
            
#             if driver:
#                 try:
#                     # Pre-navigation warmup
#                     pre_navigation_warmup(driver)
                    
#                     # Ultimate human browsing
#                     success = ultimate_human_browsing(driver)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     # Extended session time
#                     session_time = random.uniform(60, 120)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, driver)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
    
#     # Final results
#     print(f"\n🏆 ULTIMATE STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl, driver):
#     """Clean up browser resources"""
#     try:
#         if driver:
#             driver.quit()
#         time.sleep(3)
#         if gl:
#             gl.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ ULTIMATE ANTI-BOT DETECTION BYPASS")
#     print("Maximum stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Ultimate stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in ultimate stealth test: {e}")





# import time
# import random
# import requests
# import json
# import math
# import base64
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager
# from fake_useragent import UserAgent

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- ENHANCED CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# TOKEN = "CHANGE_ME_TOKEN"

# # MAXIMUM STEALTH SETTINGS
# TOTAL_PROFILES = 1
# PRE_NAVIGATION_DELAY = (20, 35)  # Increased delay
# HUMAN_BEHAVIOR_TIME = (45, 90)   # Extended human behavior
# PAGE_LOAD_PATIENCE = (10, 20)    # More patient loading
# SESSION_DURATION = (120, 300)    # Longer session time

# # Enhanced proxy list with rotation
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
#     # Add more proxies for rotation
# ]

# # User agents for rotation
# ua = UserAgent()

# def parse_proxy_string(s: str):
#     """Parse proxy string with enhanced error handling"""
#     try:
#         s = s.strip()
#         parts = s.split()
#         if len(parts) == 1:
#             proto = None
#             main = parts[0]
#         else:
#             proto = parts[0].lower()
#             main = parts[1]
        
#         segs = main.split(":", 3)
#         if len(segs) == 4:
#             host, port, username, password = segs
#             return {"type": proto or "socks5", "host": host, "port": port, "username": username, "password": password}
#         return None
#     except Exception as e:
#         print(f"⚠️ Proxy parsing error: {e}")
#         return None

# def create_enhanced_stealth_profile(profile_name, proxy_config=None):
#     """Create enhanced stealth profile with better fingerprinting"""
#     try:
#         gl = GoLogin({"token": TOKEN})
        
#         print(f"🥷 Creating ENHANCED stealth profile: {profile_name}")
        
#         # Enhanced profile creation with more realistic settings
#         profile_settings = {
#             "os": random.choice(["win", "mac", "lin"]),
#             "name": profile_name,
#             # Add more realistic browser settings
#             "navigator": {
#                 "userAgent": ua.random,
#                 "resolution": random.choice(["1920x1080", "1366x768", "1536x864", "1440x900"]),
#                 "language": random.choice(["en-US", "en-GB", "hi-IN"]),
#             },
#             "fonts": {
#                 "families": ["Arial", "Times New Roman", "Helvetica", "Verdana"]
#             },
#             "audioContext": {
#                 "enable": True,
#                 "noiseValue": random.uniform(0.00001, 0.0001)
#             },
#             "canvas": {
#                 "mode": "noise",
#                 "noise": random.uniform(0.1, 0.5)
#             },
#             "webgl": {
#                 "noise": True,
#                 "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
#                 "renderer": "Intel(R) UHD Graphics 630"
#             }
#         }
        
#         profile = gl.createProfileRandomFingerprint(profile_settings)
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         # Enhanced proxy configuration
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', ''),
#                     "changeIpUrl": ""  # For IP rotation
#                 }
                
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Enhanced proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         # Update to latest browser version
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 Browser updated to latest version")
#         except Exception as e:
#             print(f"⚠️ Browser update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_enhanced_stealth_browser(profile_id):
#     """Start browser with ENHANCED stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
        
#         print(f"🚀 Starting ENHANCED stealth browser: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         # Extended browser stabilization
#         wait_time = random.uniform(8, 15)
#         print(f"⏳ Enhanced browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         chromium_version = gl.get_chromium_version()
#         service = Service(ChromeDriverManager(driver_version=chromium_version).install())
        
#         chrome_options = webdriver.ChromeOptions()
#         chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        
#         # Fixed stealth options - removing problematic excludeSwitches
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-plugins-discovery")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--disable-web-security")
#         chrome_options.add_argument("--allow-running-insecure-content")
#         chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
#         # Set user agent
#         chrome_options.add_argument(f"--user-agent={ua.random}")
        
#         try:
#             driver = webdriver.Chrome(service=service, options=chrome_options)
#         except Exception as chrome_error:
#             print(f"❌ Chrome options error: {chrome_error}")
#             # Fallback with minimal options
#             chrome_options_minimal = webdriver.ChromeOptions()
#             chrome_options_minimal.add_experimental_option("debuggerAddress", debugger_address)
#             driver = webdriver.Chrome(service=service, options=chrome_options_minimal)
        
#         # Enhanced stealth injection
#         inject_enhanced_stealth(driver)
        
#         # Set realistic viewport
#         driver.set_window_size(
#             random.choice([1920, 1366, 1536, 1440]),
#             random.choice([1080, 768, 864, 900])
#         )
        
#         return gl, driver
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None

# def inject_enhanced_stealth(driver):
#     """Inject ENHANCED stealth scripts with advanced techniques"""
#     try:
#         print("🛡️ Injecting ENHANCED stealth protection...")
        
#         # 1. Advanced webdriver detection removal
#         driver.execute_script("""
#             // Remove webdriver traces completely
#             const originalDescriptor = Object.getOwnPropertyDescriptor(Navigator.prototype, 'webdriver');
#             if (originalDescriptor) {
#                 delete Navigator.prototype.webdriver;
#             }
            
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined,
#                 configurable: true
#             });
            
#             // Remove from window and document
#             ['webdriver', 'automation', '__webdriver_evaluate', '__selenium_evaluate', 
#              '__webdriver_script_function', '__webdriver_script_func', '__webdriver_script_fn',
#              '__fxdriver_evaluate', '__driver_unwrapped', '__webdriver_unwrapped',
#              '__driver_evaluate', '__selenium_unwrapped', '__fxdriver_unwrapped'].forEach(prop => {
#                 delete window[prop];
#                 delete document[prop];
#             });
#         """)
        
#         # 2. Enhanced Chrome runtime mocking
#         driver.execute_script("""
#             // Mock chrome runtime with realistic properties
#             if (!window.chrome) {
#                 window.chrome = {};
#             }
            
#             window.chrome.runtime = {
#                 onConnect: { addListener: function() {}, hasListener: function() { return false; } },
#                 onMessage: { addListener: function() {}, hasListener: function() { return false; } },
#                 connect: function() { return { onMessage: { addListener: function() {} } }; }
#             };
            
#             window.chrome.storage = {
#                 local: { get: function() {}, set: function() {} }
#             };
            
#             window.chrome.app = { isInstalled: false };
#         """)
        
#         # 3. Advanced plugin and mime type spoofing
#         driver.execute_script("""
#             // Enhanced plugin array with realistic plugins
#             const plugins = [
#                 { name: "Chrome PDF Plugin", filename: "internal-pdf-viewer", description: "Portable Document Format" },
#                 { name: "Chrome PDF Viewer", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", description: "" },
#                 { name: "Native Client", filename: "internal-nacl-plugin", description: "Native Client" },
#                 { name: "Shockwave Flash", filename: "pepflashplayer.dll", description: "Shockwave Flash 32.0 r0" }
#             ];
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => plugins,
#                 configurable: true
#             });
            
#             // Enhanced mimeTypes
#             const mimeTypes = [
#                 { type: "application/pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: plugins[0] },
#                 { type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: plugins[0] }
#             ];
            
#             Object.defineProperty(navigator, 'mimeTypes', {
#                 get: () => mimeTypes,
#                 configurable: true
#             });
#         """)
        
#         # 4. Enhanced WebGL fingerprinting protection
#         driver.execute_script("""
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 const glParams = {
#                     37445: 'Intel Inc.',  // VENDOR
#                     37446: 'Intel(R) UHD Graphics 630',  // RENDERER  
#                     7936: 'Intel(R) UHD Graphics 630',   // VERSION
#                     35724: 'WebGL GLSL ES 1.0',          // SHADING_LANGUAGE_VERSION
#                 };
                
#                 if (parameter in glParams) {
#                     return glParams[parameter];
#                 }
#                 return getParameter.call(this, parameter);
#             };
            
#             // WebGL2 context protection
#             if (typeof WebGL2RenderingContext !== 'undefined') {
#                 const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
#                 WebGL2RenderingContext.prototype.getParameter = WebGLRenderingContext.prototype.getParameter;
#             }
#         """)
        
#         # 5. Canvas fingerprinting protection with noise
#         driver.execute_script("""
#             const toBlob = HTMLCanvasElement.prototype.toBlob;
#             const toDataURL = HTMLCanvasElement.prototype.toDataURL;
#             const getImageData = CanvasRenderingContext2D.prototype.getImageData;
            
#             // Add subtle noise to canvas operations
#             const noisify = function(canvas, context) {
#                 const shift = {
#                     'r': Math.floor(Math.random() * 10) - 5,
#                     'g': Math.floor(Math.random() * 10) - 5,
#                     'b': Math.floor(Math.random() * 10) - 5,
#                     'a': Math.floor(Math.random() * 10) - 5
#                 };
                
#                 const width = canvas.width;
#                 const height = canvas.height;
#                 const imageData = context.getImageData(0, 0, width, height);
                
#                 for (let i = 0; i < imageData.data.length; i += 4) {
#                     imageData.data[i] += shift.r;
#                     imageData.data[i + 1] += shift.g;
#                     imageData.data[i + 2] += shift.b;
#                     imageData.data[i + 3] += shift.a;
#                 }
                
#                 context.putImageData(imageData, 0, 0);
#             };
            
#             Object.defineProperty(HTMLCanvasElement.prototype, 'toBlob', {
#                 "value": function() {
#                     noisify(this, this.getContext('2d'));
#                     return toBlob.apply(this, arguments);
#                 }
#             });
            
#             Object.defineProperty(HTMLCanvasElement.prototype, 'toDataURL', {
#                 "value": function() {
#                     noisify(this, this.getContext('2d'));
#                     return toDataURL.apply(this, arguments);
#                 }
#             });
#         """)
        
#         # 6. Enhanced navigator properties
#         driver.execute_script("""
#             // Realistic navigator properties
#             Object.defineProperties(navigator, {
#                 languages: { get: () => ['en-US', 'en', 'hi'] },
#                 platform: { get: () => 'Win32' },
#                 hardwareConcurrency: { get: () => 8 },
#                 deviceMemory: { get: () => 8 },
#                 maxTouchPoints: { get: () => 0 },
#                 cookieEnabled: { get: () => true },
#                 doNotTrack: { get: () => null }
#             });
#         """)
        
#         # 7. Enhanced screen properties with realistic values
#         driver.execute_script("""
#             const screenProps = {
#                 width: 1920,
#                 height: 1080,
#                 availWidth: 1920,
#                 availHeight: 1040,
#                 colorDepth: 24,
#                 pixelDepth: 24,
#                 orientation: { angle: 0, type: 'landscape-primary' }
#             };
            
#             Object.defineProperties(screen, screenProps);
#         """)
        
#         # 8. Advanced event handling and mouse simulation
#         driver.execute_script("""
#             // Enhanced mouse event handling
#             let mouseHistory = [];
#             let mousePosition = { x: 0, y: 0 };
            
#             document.addEventListener('mousemove', function(e) {
#                 mousePosition = { x: e.clientX, y: e.clientY };
#                 mouseHistory.push({ x: e.clientX, y: e.clientY, time: Date.now() });
#                 if (mouseHistory.length > 100) mouseHistory.shift();
#             }, true);
            
#             // Mock trusted events
#             const originalIsTrusted = Object.getOwnPropertyDescriptor(Event.prototype, 'isTrusted');
#             Object.defineProperty(Event.prototype, 'isTrusted', {
#                 get: function() {
#                     return true;
#                 }
#             });
            
#             // Enhanced Date and timezone handling
#             const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
#             Date.prototype.getTimezoneOffset = function() {
#                 return -330; // IST timezone
#             };
#         """)
        
#         # 9. Permissions API enhancement
#         driver.execute_script("""
#             if (navigator.permissions && navigator.permissions.query) {
#                 const originalQuery = navigator.permissions.query;
#                 navigator.permissions.query = function(parameters) {
#                     const mockPermissions = {
#                         'geolocation': 'prompt',
#                         'notifications': 'default',
#                         'camera': 'prompt',
#                         'microphone': '9999999999'
#                     };
                    
#                     if (parameters.name in mockPermissions) {
#                         return Promise.resolve({ state: mockPermissions[parameters.name] });
#                     }
                    
#                     return originalQuery.apply(this, arguments);
#                 };
#             }
#         """)
        
#         # 10. Network timing API protection
#         driver.execute_script("""
#             if (window.performance && window.performance.getEntriesByType) {
#                 const originalGetEntriesByType = window.performance.getEntriesByType;
#                 window.performance.getEntriesByType = function(type) {
#                     const entries = originalGetEntriesByType.call(this, type);
#                     // Add realistic timing variations
#                     return entries.map(entry => ({
#                         ...entry,
#                         connectStart: entry.connectStart + Math.random() * 10,
#                         connectEnd: entry.connectEnd + Math.random() * 10
#                     }));
#                 };
#             }
#         """)
        
#         print("✅ ENHANCED stealth protection activated")
        
#     except Exception as e:
#         print(f"⚠️ Enhanced stealth injection warning: {e}")

# def enhanced_pre_navigation_warmup(driver):
#     """Enhanced warmup with more realistic browsing patterns"""
#     try:
#         print("🔥 Starting enhanced pre-navigation warmup...")
        
#         # More diverse warmup sites
#         warmup_sites = [
#             "https://www.google.co.in",
#             "https://stackoverflow.com",
#             "https://github.com",
#             "https://www.wikipedia.org",
#             "https://medium.com"
#         ]
        
#         selected_sites = random.sample(warmup_sites, random.randint(2, 4))
        
#         for i, site in enumerate(selected_sites):
#             print(f"🌐 Enhanced warmup {i+1}/{len(selected_sites)}: {site}")
            
#             try:
#                 driver.get(site)
                
#                 # Wait for page load with realistic patience
#                 WebDriverWait(driver, 15).until(
#                     EC.presence_of_element_located((By.TAG_NAME, "body"))
#                 )
                
#                 # Enhanced human behavior during warmup
#                 perform_enhanced_interaction(driver)
                
#                 # Realistic inter-site delay
#                 if i < len(selected_sites) - 1:
#                     wait_time = random.uniform(8, 15)
#                     print(f"⏳ Inter-site cooldown: {wait_time:.1f}s")
#                     time.sleep(wait_time)
                    
#             except Exception as e:
#                 print(f"⚠️ Warmup site error: {e}")
#                 continue
        
#         # Final preparation delay
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target")
#         time.sleep(final_delay)
        
#     except Exception as e:
#         print(f"⚠️ Enhanced warmup error: {e}")

# def perform_enhanced_interaction(driver):
#     """Enhanced human interactions with more realistic patterns"""
#     try:
#         # Scroll with realistic patterns
#         scroll_patterns = random.choice(['gradual', 'quick_scan', 'thorough_read'])
        
#         if scroll_patterns == 'gradual':
#             for _ in range(random.randint(3, 6)):
#                 scroll_distance = random.randint(200, 500)
#                 driver.execute_script(f"""
#                     window.scrollBy({{
#                         top: {scroll_distance},
#                         left: 0,
#                         behavior: 'smooth'
#                     }});
#                 """)
#                 time.sleep(random.uniform(2, 4))
                
#         elif scroll_patterns == 'quick_scan':
#             # Quick scroll to bottom, then back up
#             driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
#             time.sleep(random.uniform(2, 4))
#             driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
#             time.sleep(random.uniform(1, 3))
            
#         else:  # thorough_read
#             # Small incremental scrolls with reading pauses
#             for _ in range(random.randint(5, 10)):
#                 scroll_distance = random.randint(100, 200)
#                 driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
#                 time.sleep(random.uniform(3, 6))  # Reading time
        
#         # Enhanced mouse movements
#         try:
#             clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a, button, input, [onclick]")[:10]
#             if clickable_elements:
#                 actions = ActionChains(driver)
                
#                 # Move to multiple elements with realistic timing
#                 for element in random.sample(clickable_elements, min(3, len(clickable_elements))):
#                     if element.is_displayed():
#                         actions.move_to_element(element)
#                         actions.pause(random.uniform(1, 3))
                        
#                         # Sometimes move away from element
#                         if random.choice([True, False]):
#                             actions.move_by_offset(random.randint(-50, 50), random.randint(-50, 50))
#                             actions.pause(random.uniform(0.5, 1.5))
                
#                 actions.perform()
#         except Exception as e:
#             print(f"⚠️ Mouse interaction warning: {e}")
            
#         # Simulate focus changes
#         if random.choice([True, False]):
#             driver.execute_script("window.blur();")
#             time.sleep(random.uniform(1, 2))
#             driver.execute_script("window.focus();")
            
#     except Exception as e:
#         print(f"⚠️ Enhanced interaction error: {e}")

# def enhanced_human_browsing(driver):
#     """Enhanced human-like browsing with advanced behavior patterns"""
#     try:
#         print("🎭 Starting ENHANCED human behavior simulation...")
        
#         # Navigate to target with referrer
#         print(f"🎯 Navigating to target: {TARGET_URL}")
        
#         # Sometimes come from a search engine
#         if random.choice([True, False]):
#             print("🔍 Simulating search engine referral...")
#             driver.get("https://www.google.com/search?q=portfolio+website")
#             time.sleep(random.uniform(3, 6))
        
#         # Navigate to target
#         driver.get(TARGET_URL)
        
#         # Enhanced page load waiting
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Enhanced page loading patience: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         # Check for challenges/blocks
#         if detect_and_handle_challenges(driver):
#             return True
        
#         # Wait for critical elements
#         try:
#             WebDriverWait(driver, 25).until(
#                 lambda d: d.execute_script("return document.readyState") == "complete"
#             )
#             print("📄 Page fully loaded")
#         except TimeoutException:
#             print("⚠️ Page load timeout, continuing...")
        
#         # Extended realistic human behavior
#         behavior_duration = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Enhanced human behavior for {behavior_duration:.1f}s")
        
#         start_time = time.time()
#         interaction_count = 0
        
#         while time.time() - start_time < behavior_duration:
#             # More diverse actions
#             actions = [
#                 'realistic_scroll', 'mouse_trail', 'reading_pause', 
#                 'element_hover', 'focus_simulation', 'typing_simulation',
#                 'tab_interaction', 'context_menu', 'selection_behavior'
#             ]
            
#             action = random.choice(actions)
#             execute_enhanced_human_action(driver, action)
            
#             interaction_count += 1
            
#             # Variable delay between actions
#             delay = random.uniform(2, 8)
#             time.sleep(delay)
            
#             # Periodic longer pauses (like getting distracted)
#             if interaction_count % random.randint(5, 8) == 0:
#                 distraction_time = random.uniform(10, 20)
#                 print(f"💭 Simulating distraction: {distraction_time:.1f}s")
#                 time.sleep(distraction_time)
        
#         print("✅ Enhanced human behavior simulation complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Enhanced browsing error: {e}")
#         return False

# def execute_enhanced_human_action(driver, action):
#     """Execute enhanced human-like actions with more sophistication"""
#     try:
#         if action == 'realistic_scroll':
#             # More natural scrolling patterns
#             scroll_type = random.choice(['smooth_read', 'quick_scan', 'section_jump'])
            
#             if scroll_type == 'smooth_read':
#                 for _ in range(random.randint(3, 7)):
#                     scroll_distance = random.randint(150, 350)
#                     driver.execute_script(f"""
#                         window.scrollBy({{
#                             top: {scroll_distance},
#                             left: 0,
#                             behavior: 'smooth'
#                         }});
#                     """)
#                     time.sleep(random.uniform(2, 5))
                    
#             elif scroll_type == 'quick_scan':
#                 # Fast initial scroll, then slower
#                 driver.execute_script("window.scrollTo({top: document.body.scrollHeight/2, behavior: 'auto'});")
#                 time.sleep(random.uniform(1, 2))
#                 for _ in range(random.randint(2, 4)):
#                     scroll_distance = random.randint(100, 200)
#                     driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
#                     time.sleep(random.uniform(1, 3))
                    
#         elif action == 'mouse_trail':
#             # Create more realistic mouse movement patterns
#             try:
#                 elements = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, p, a, img, button")[:15]
#                 if elements:
#                     actions = ActionChains(driver)
                    
#                     # Move in a more natural pattern
#                     for element in random.sample(elements, min(5, len(elements))):
#                         if element.is_displayed():
#                             # Sometimes move to element directly, sometimes in an arc
#                             if random.choice([True, False]):
#                                 actions.move_to_element(element)
#                             else:
#                                 # Move in an arc
#                                 element_location = element.location
#                                 actions.move_by_offset(
#                                     element_location['x'] + random.randint(-100, 100),
#                                     element_location['y'] + random.randint(-50, 50)
#                                 )
#                                 time.sleep(random.uniform(0.3, 0.8))
#                                 actions.move_to_element(element)
                            
#                             actions.pause(random.uniform(1, 3))
                    
#                     actions.perform()
#             except Exception:
#                 pass
                
#         elif action == 'reading_pause':
#             # Simulate different reading patterns
#             reading_time = random.choice([
#                 random.uniform(3, 6),    # Quick scan
#                 random.uniform(8, 15),   # Normal read
#                 random.uniform(15, 25)   # Deep read
#             ])
#             time.sleep(reading_time)
            
#         elif action == 'tab_interaction':
#             # Simulate tab key usage for accessibility
#             try:
#                 active_element = driver.switch_to.active_element
#                 for _ in range(random.randint(1, 3)):
#                     active_element.send_keys(Keys.TAB)
#                     time.sleep(random.uniform(0.5, 1.5))
#             except:
#                 pass
                
#         elif action == 'context_menu':
#             # Sometimes right-click (but don't actually use context menu)
#             try:
#                 elements = driver.find_elements(By.CSS_SELECTOR, "p, div, img")[:5]
#                 if elements:
#                     element = random.choice(elements)
#                     if element.is_displayed():
#                         ActionChains(driver).context_click(element).perform()
#                         time.sleep(random.uniform(1, 2))
#                         # Click elsewhere to dismiss
#                         ActionChains(driver).click().perform()
#             except:
#                 pass
                
#         elif action == 'selection_behavior':
#             # Simulate text selection behavior
#             try:
#                 text_elements = driver.find_elements(By.CSS_SELECTOR, "p, span, div")[:10]
#                 if text_elements:
#                     element = random.choice([e for e in text_elements if e.text.strip()])
#                     if element and len(element.text) > 10:
#                         # Double-click to select word
#                         ActionChains(driver).double_click(element).perform()
#                         time.sleep(random.uniform(1, 3))
#                         # Click elsewhere to deselect
#                         ActionChains(driver).click().perform()
#             except:
#                 pass
                
#         else:
#             # Execute original actions for backward compatibility
#             if action in ['element_hover', 'focus_simulation', 'typing_simulation']:
#                 # Original implementation with minor enhancements
#                 if action == 'element_hover':
#                     try:
#                         hoverable_elements = driver.find_elements(By.CSS_SELECTOR, "a, button, [title], img")[:8]
#                         if hoverable_elements:
#                             element = random.choice(hoverable_elements)
#                             if element.is_displayed():
#                                 ActionChains(driver).move_to_element(element).pause(random.uniform(2, 4)).perform()
#                     except:
#                         pass
                        
#     except Exception as e:
#         print(f"⚠️ Enhanced action error: {e}")

# def detect_and_handle_challenges(driver):
#     """Enhanced challenge detection and handling"""
#     try:
#         current_url = driver.current_url
#         page_source = driver.page_source.lower()
#         page_title = driver.title.lower()
        
#         # Enhanced challenge indicators
#         challenge_indicators = [
#             'captcha', 'robot', 'verify', 'challenge', 'access denied', 'blocked', 
#             'security check', 'cloudflare', 'ddos protection', 'checking your browser',
#             'please wait', 'anti-bot', 'rate limit', 'too many requests', 'forbidden'
#         ]
        
#         is_challenge = any(indicator in current_url.lower() or 
#                           indicator in page_source or 
#                           indicator in page_title 
#                           for indicator in challenge_indicators)
        
#         # Check for common challenge page elements
#         challenge_selectors = [
#             '[class*="captcha"]', '[id*="captcha"]',
#             '[class*="challenge"]', '[id*="challenge"]',
#             '[class*="cloudflare"]', '[id*="cloudflare"]',
#             '.cf-browser-verification', '.cf-checking-browser'
#         ]
        
#         for selector in challenge_selectors:
#             try:
#                 if driver.find_elements(By.CSS_SELECTOR, selector):
#                     is_challenge = True
#                     break
#             except:
#                 continue
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             print(f"Title: {driver.title}")
            
#             # Handle different types of challenges
#             if any(term in page_source for term in ['cloudflare', 'checking your browser']):
#                 print("☁️ Cloudflare challenge detected")
#                 handle_cloudflare_challenge(driver)
#             elif 'captcha' in page_source:
#                 print("🧩 CAPTCHA challenge detected")
#                 handle_captcha_challenge(driver)
#             else:
#                 print("🛡️ Generic challenge detected")
#                 handle_generic_challenge(driver)
            
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_cloudflare_challenge(driver):
#     """Handle Cloudflare challenges with patience"""
#     try:
#         print("☁️ Handling Cloudflare challenge...")
        
#         # Wait for automatic verification
#         max_wait = 30
#         start_time = time.time()
        
#         while time.time() - start_time < max_wait:
#             current_url = driver.current_url
#             page_source = driver.page_source.lower()
            
#             # Check if challenge is resolved
#             if not any(term in page_source for term in ['checking your browser', 'cloudflare', 'ddos protection']):
#                 print("✅ Cloudflare challenge passed")
#                 return
            
#             # Look for "Continue" or verification buttons
#             button_selectors = [
#                 'input[type="submit"]', 'button[type="submit"]',
#                 '[value*="continue"]', '[value*="verify"]',
#                 'button:contains("Continue")', 'button:contains("Verify")'
#             ]
            
#             for selector in button_selectors:
#                 try:
#                     button = driver.find_element(By.CSS_SELECTOR, selector)
#                     if button.is_displayed() and button.is_enabled():
#                         print(f"🔄 Found verification button: {button.text or button.get_attribute('value')}")
                        
#                         # Human-like click with delay
#                         ActionChains(driver).move_to_element(button).pause(2).click().perform()
#                         time.sleep(random.uniform(3, 6))
#                         break
#                 except:
#                     continue
            
#             print("⏳ Waiting for Cloudflare verification...")
#             time.sleep(2)
        
#         print("⚠️ Cloudflare challenge timeout")
        
#     except Exception as e:
#         print(f"⚠️ Cloudflare handling error: {e}")

# def handle_captcha_challenge(driver):
#     """Handle CAPTCHA challenges"""
#     try:
#         print("🧩 Handling CAPTCHA challenge...")
        
#         # Look for different types of CAPTCHA elements
#         captcha_iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="captcha"], iframe[src*="recaptcha"]')
        
#         if captcha_iframes:
#             print("🔍 Found CAPTCHA iframe")
            
#             # Switch to iframe and look for checkbox
#             for iframe in captcha_iframes:
#                 try:
#                     driver.switch_to.frame(iframe)
                    
#                     # Look for reCAPTCHA checkbox
#                     checkbox_selectors = [
#                         '.recaptcha-checkbox-border',
#                         '#recaptcha-anchor',
#                         '[role="checkbox"]'
#                     ]
                    
#                     for selector in checkbox_selectors:
#                         try:
#                             checkbox = WebDriverWait(driver, 5).until(
#                                 EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
#                             )
                            
#                             print("☑️ Found CAPTCHA checkbox")
                            
#                             # Human-like click
#                             ActionChains(driver).move_to_element(checkbox).pause(2).click().perform()
#                             time.sleep(random.uniform(2, 4))
#                             break
#                         except:
#                             continue
                    
#                     driver.switch_to.default_content()
#                     break
#                 except:
#                     driver.switch_to.default_content()
#                     continue
        
#         # Wait for manual intervention or automatic resolution
#         print("⏳ Waiting for CAPTCHA resolution...")
#         time.sleep(random.uniform(10, 20))
        
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def handle_generic_challenge(driver):
#     """Handle generic challenges"""
#     try:
#         print("🛡️ Handling generic challenge...")
        
#         # Look for common action buttons
#         button_texts = ['continue', 'proceed', 'verify', 'submit', 'next', 'enter']
        
#         for text in button_texts:
#             buttons = driver.find_elements(By.XPATH, f"//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{text}')]")
#             buttons.extend(driver.find_elements(By.XPATH, f"//input[@value and contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{text}')]"))
            
#             for button in buttons:
#                 if button.is_displayed() and button.is_enabled():
#                     print(f"🔄 Found action button: {button.text or button.get_attribute('value')}")
                    
#                     # Human-like interaction
#                     ActionChains(driver).move_to_element(button).pause(3).click().perform()
#                     time.sleep(random.uniform(3, 8))
#                     return
        
#         # If no buttons found, wait and retry
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(15, 30))
        
#     except Exception as e:
#         print(f"⚠️ Generic challenge handling error: {e}")

# def run_enhanced_stealth_test():
#     """Run the enhanced stealth test with better error handling"""
#     print("🎯 ENHANCED STEALTH MODE ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
#     failed_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"enhanced_stealth_{profile_num}_{random.randint(100000, 999999)}"
#         gl = None
#         driver = None
        
#         try:
#             # Get proxy configuration
#             proxy_config = None
#             if PROXY_LIST:
#                 proxy_str = random.choice(PROXY_LIST)
#                 proxy_config = parse_proxy_string(proxy_str)
#                 if proxy_config:
#                     print(f"🌐 Using proxy: {proxy_config['host']}")
            
#             # Create enhanced profile
#             profile_id = create_enhanced_stealth_profile(profile_name, proxy_config)
            
#             if profile_id:
#                 # Extended preparation time
#                 prep_time = random.uniform(10, 20)
#                 print(f"⏳ Profile preparation: {prep_time:.1f}s")
#                 time.sleep(prep_time)
                
#                 # Start enhanced browser
#                 gl, driver = start_enhanced_stealth_browser(profile_id)
                
#                 if driver:
#                     try:
#                         # Enhanced pre-navigation warmup
#                         enhanced_pre_navigation_warmup(driver)
                        
#                         # Enhanced human browsing
#                         success = enhanced_human_browsing(driver)
                        
#                         if success:
#                             successful_runs += 1
#                             print(f"🎉 PROFILE {profile_num} - SUCCESS!")
                            
#                             # Extended successful session
#                             session_time = random.uniform(*SESSION_DURATION)
#                             print(f"🕐 Maintaining successful session: {session_time:.1f}s")
#                             time.sleep(session_time)
#                         else:
#                             failed_runs += 1
#                             print(f"❌ PROFILE {profile_num} - FAILED")
                            
#                     except Exception as session_error:
#                         failed_runs += 1
#                         print(f"❌ PROFILE {profile_num} - SESSION ERROR: {session_error}")
                        
#                 else:
#                     failed_runs += 1
#                     print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#             else:
#                 failed_runs += 1
#                 print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
                
#         except Exception as profile_error:
#             failed_runs += 1
#             print(f"❌ PROFILE {profile_num} - PROFILE ERROR: {profile_error}")
            
#         finally:
#             # Always cleanup
#             cleanup_enhanced_browser(gl, driver, profile_name)
            
#             # Inter-profile delay
#             if profile_num < TOTAL_PROFILES:
#                 inter_delay = random.uniform(15, 30)
#                 print(f"⏳ Inter-profile delay: {inter_delay:.1f}s")
#                 time.sleep(inter_delay)
    
#     # Final comprehensive results
#     print(f"\n🏆 ENHANCED STEALTH TEST COMPLETE!")
#     print(f"📊 Results Summary:")
#     print(f"   ✅ Successful: {successful_runs}")
#     print(f"   ❌ Failed: {failed_runs}")
#     print(f"   📈 Success Rate: {successful_runs/(successful_runs + failed_runs)*100:.1f}%")

# def cleanup_enhanced_browser(gl, driver, profile_name):
#     """Enhanced cleanup with better error handling"""
#     try:
#         print(f"🧹 Cleaning up profile: {profile_name}")
        
#         if driver:
#             try:
#                 # Clear browsing data before closing
#                 driver.execute_script("window.localStorage.clear();")
#                 driver.execute_script("window.sessionStorage.clear();")
#                 driver.delete_all_cookies()
#                 print("🗑️ Browsing data cleared")
#             except:
#                 pass
                
#             try:
#                 driver.quit()
#                 print("🔒 Driver closed")
#             except:
#                 pass
        
#         # Wait for driver cleanup
#         time.sleep(3)
        
#         if gl:
#             try:
#                 gl.stop()
#                 print("⏹️ GoLogin session stopped")
#             except:
#                 pass
        
#         print("✅ Cleanup completed")
        
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# def main():
#     """Main function with startup checks"""
#     print("🛡️ ENHANCED ANTI-BOT DETECTION BYPASS")
#     print("Enhanced stealth configuration for portfolio testing")
#     print("=" * 60)
    
#     # Verify dependencies
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin library not available!")
#         print("Install with: pip install gologin")
#         return
    
#     # Verify configuration
#     if not TOKEN:
#         print("❌ GoLogin token not configured!")
#         return
        
#     if not TARGET_URL:
#         print("❌ Target URL not configured!")
#         return
    
#     print(f"🎯 Target: {TARGET_URL}")
#     print(f"🔑 Token: {TOKEN[:20]}...")
#     print(f"📊 Profiles to test: {TOTAL_PROFILES}")
    
#     try:
#         # Test GoLogin connection
#         test_gl = GoLogin({"token": TOKEN})
#         print("✅ GoLogin connection verified")
        
#         # Start enhanced test
#         run_enhanced_stealth_test()
        
#     except KeyboardInterrupt:
#         print("\n🛑 Enhanced stealth test interrupted by user")
#     except Exception as e:
#         print(f"❌ Fatal error in enhanced stealth test: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     main()




# import time
# import random
# import requests
# import json
# import math
# import base64
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- ULTIMATE CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# TOKEN = "CHANGE_ME_TOKEN"

# # MAXIMUM STEALTH SETTINGS
# TOTAL_PROFILES = 1
# PRE_NAVIGATION_DELAY = (15, 25)  # Long delay before going to target site
# HUMAN_BEHAVIOR_TIME = (30, 60)   # Extended human behavior
# PAGE_LOAD_PATIENCE = (8, 15)     # Patient page loading

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     if len(parts) == 1:
#         proto = None
#         main = parts[0]
#     else:
#         proto = parts[0].lower()
#         main = parts[1]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto or "socks5", "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create the most stealthy profile possible"""
#     try:
#         gl = GoLogin({"token": TOKEN})
        
#         print(f"🥷 Creating ULTIMATE stealth profile: {profile_name}")
        
#         # Create profile with random OS selection for diversity
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac", "lin"]),  # Include Linux
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         # Set proxy with error handling
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
                
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         # Update user agent to latest
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with MAXIMUM stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
        
#         print(f"🚀 Starting MAXIMUM stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         # Longer wait for browser stability
#         wait_time = random.uniform(5, 10)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         # ULTIMATE stealth injection
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject ULTIMATE stealth scripts - most comprehensive"""
#     try:
#         print("🛡️ Injecting ULTIMATE stealth protection...")
        
#         # 1. Remove ALL webdriver traces
#         page.evaluate("""
#             // Remove webdriver property
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined,
#             });
            
#             // Remove webdriver from window
#             delete window.webdriver;
            
#             // Remove automation flags
#             Object.defineProperty(navigator, 'automation', {
#                 get: () => undefined,
#             });
            
#             // Remove webdriver from document
#             delete document.webdriver;
#         """)
        
#         # 2. Mock Chrome runtime
#         page.evaluate("""
#             // Mock chrome runtime
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 },
#                 storage: {
#                     local: {
#                         get: () => {},
#                         set: () => {},
#                     }
#                 }
#             };
#         """)
        
#         # 3. Advanced plugin mocking
#         page.evaluate("""
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [
#                     {
#                         0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
#                         description: "Portable Document Format",
#                         filename: "internal-pdf-viewer",
#                         length: 1,
#                         name: "Chrome PDF Plugin"
#                     },
#                     {
#                         0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin},
#                         description: "",
#                         filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
#                         length: 1,
#                         name: "Chrome PDF Viewer"
#                     },
#                     {
#                         description: "Shockwave Flash",
#                         filename: "pepflashplayer.dll",
#                         name: "Shockwave Flash"
#                     }
#                 ]
#             });
#         """)
        
#         # 4. Mock languages and timezone
#         page.evaluate("""
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN', 'hi'],
#             });
            
#             // Mock timezone
#             Date.prototype.getTimezoneOffset = function() {
#                 return -330; // IST timezone
#             };
#         """)
        
#         # 5. Advanced WebGL spoofing
#         page.evaluate("""
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 // Mock real GPU signatures
#                 if (parameter === 37445) {
#                     return 'Intel Inc.';
#                 }
#                 if (parameter === 37446) {
#                     return 'Intel(R) UHD Graphics 630';
#                 }
#                 return getParameter.call(this, parameter);
#             };
#         """)
        
#         # 6. Mock screen properties realistically
#         page.evaluate("""
#             Object.defineProperty(screen, 'availWidth', {
#                 get: () => 1920
#             });
#             Object.defineProperty(screen, 'availHeight', {
#                 get: () => 1040
#             });
#             Object.defineProperty(screen, 'width', {
#                 get: () => 1920
#             });
#             Object.defineProperty(screen, 'height', {
#                 get: () => 1080
#             });
#         """)
        
#         # 7. Mock permissions API
#         page.evaluate("""
#             const originalQuery = window.navigator.permissions.query;
#             window.navigator.permissions.query = (parameters) => (
#                 parameters.name === 'notifications' ?
#                     Promise.resolve({ state: Notification.permission }) :
#                     originalQuery(parameters)
#             );
#         """)
        
#         # 8. Advanced mouse event mocking
#         page.evaluate("""
#             // Mock mouse events
#             let mouseX = 0, mouseY = 0;
#             document.addEventListener('mousemove', (e) => {
#                 mouseX = e.clientX;
#                 mouseY = e.clientY;
#             });
            
#             // Mock realistic mouse behavior
#             Object.defineProperty(MouseEvent.prototype, 'isTrusted', {
#                 get: () => true
#             });
#         """)
        
#         print("✅ ULTIMATE stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with innocent sites before target"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
        
#         innocent_sites = [
#             "https://www.google.co.in",
#             "https://www.wikipedia.org",
#             "https://www.github.com"
#         ]
        
#         for i, site in enumerate(innocent_sites):
#             print(f"🌐 Warming up {i+1}/{len(innocent_sites)}: {site}")
            
#             page.goto(site)
            
#             # Wait for page load
#             wait_time = random.uniform(3, 6)
#             time.sleep(wait_time)
            
#             # Light human behavior
#             perform_light_interaction(page)
            
#             # Wait between sites
#             if i < len(innocent_sites) - 1:
#                 wait_time = random.uniform(4, 8)
#                 print(f"⏳ Cooling down: {wait_time:.1f}s")
#                 time.sleep(wait_time)
        
#         # Final warm-up delay
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
        
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions during warmup"""
#     try:
#         # Small scroll
#         scroll_distance = random.randint(100, 400)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(1, 3))
        
#         # Mouse movement to random element
#         try:
#             elements = page.locator("a, button, input").all()[:5]
#             if elements:
#                 random_element = random.choice(elements)
#                 if random_element.is_visible():
#                     random_element.hover()
#                     time.sleep(random.uniform(0.5, 2))
#         except:
#             pass
            
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def ultimate_human_browsing(page: Page):
#     """ULTIMATE human-like browsing behavior"""
#     try:
#         print("🎭 Starting ULTIMATE human behavior simulation...")
        
#         # Patient navigation to target
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         page.goto(TARGET_URL)
        
#         # Very patient page load wait
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         # Check for CAPTCHA or blocks
#         if detect_and_handle_challenges(page):
#             return True
        
#         # Wait for page elements
#         try:
#             page.wait_for_selector("body", timeout=20000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         # Extended human behavior
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice([
#                 'realistic_scroll', 'mouse_trail', 'reading_pause', 
#                 'element_hover', 'focus_simulation', 'typing_simulation'
#             ])
            
#             execute_human_action(page, action)
#             time.sleep(random.uniform(1, 4))
        
#         print("✅ Ultimate human behavior complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         # Check for common challenge indicators
#         challenge_indicators = [
#             'captcha', 'robot', 'verify', 'challenge', 
#             'access denied', 'blocked', 'security check'
#         ]
        
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
            
#             # Try to handle different types of challenges
#             if 'captcha' in current_url.lower() or 'captcha' in page_source:
#                 print("🧩 CAPTCHA challenge detected")
#                 handle_captcha_page(page)
            
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page with human-like behavior"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
        
#         # Look for buttons or interactive elements
#         button_selectors = [
#             "button",
#             "[role='button']",
#             ".button",
#             "input[type='button']",
#             "input[type='submit']",
#             "[onclick]"
#         ]
        
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible() and element.is_enabled():
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'proceed', 'verify', 'submit']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
                            
#                             # Human-like click
#                             element.hover()
#                             time.sleep(random.uniform(2, 5))
#                             element.click()
                            
#                             # Wait for response
#                             time.sleep(random.uniform(3, 8))
#                             return
#             except:
#                 continue
        
#         # If no buttons found, wait and see
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(10, 20))
        
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             # Natural scrolling patterns
#             for _ in range(random.randint(2, 5)):
#                 scroll_distance = random.randint(100, 300)
#                 page.evaluate(f"""
#                     window.scrollBy({{
#                         top: {scroll_distance},
#                         left: 0,
#                         behavior: 'smooth'
#                     }});
#                 """)
#                 time.sleep(random.uniform(1.5, 3.5))
                
#         elif action == 'mouse_trail':
#             # Create realistic mouse movement trail
#             elements = page.locator("div, span, p, h1, h2, a").all()[:10]
#             if elements:
#                 for element in random.sample(elements, min(3, len(elements))):
#                     if element.is_visible():
#                         element.hover()
#                         time.sleep(random.uniform(0.8, 2.2))
                
#         elif action == 'reading_pause':
#             # Simulate reading with eye movement patterns
#             time.sleep(random.uniform(3, 8))
            
#         elif action == 'element_hover':
#             # Hover over interesting elements
#             try:
#                 links = page.locator("a").all()[:5]
#                 if links:
#                     random_link = random.choice(links)
#                     if random_link.is_visible():
#                         random_link.hover()
#                         time.sleep(2)
#             except:
#                 pass
                
#         elif action == 'focus_simulation':
#             # Simulate window focus changes
#             page.evaluate("window.blur();")
#             time.sleep(random.uniform(1, 3))
#             page.evaluate("window.focus();")
            
#         elif action == 'typing_simulation':
#             # Simulate typing in search boxes (if any)
#             try:
#                 inputs = page.locator("input[type='text'], input[type='search']").all()
#                 if inputs:
#                     random_input = random.choice(inputs[:2])
#                     if random_input.is_visible() and random_input.is_enabled():
#                         # Human-like typing
#                         test_words = ["delhi", "mumbai", "bangalore", "flight"]
#                         word = random.choice(test_words)
                        
#                         random_input.click()
#                         time.sleep(random.uniform(0.5, 1.5))
                        
#                         for char in word:
#                             random_input.type(char, delay=random.uniform(0.1, 0.3) * 1000)
                        
#                         time.sleep(random.uniform(1, 3))
#                         random_input.clear()
#             except:
#                 pass
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the ultimate stealth test"""
#     print("🎯 ULTIMATE STEALTH MODE ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"ultimate_stealth_{profile_num}_{random.randint(100000, 999999)}"
        
#         # Get proxy
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         # Create profile
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             # Extended wait before browser start
#             wait_time = random.uniform(8, 15)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             # Start browser
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     # Pre-navigation warmup
#                     pre_navigation_warmup(page)
                    
#                     # Ultimate human browsing
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     # Extended session time
#                     session_time = random.uniform(60, 120)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
    
#     # Final results
#     print(f"\n🏆 ULTIMATE STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(3)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ ULTIMATE ANTI-BOT DETECTION BYPASS")
#     print("Maximum stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Ultimate stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in ultimate stealth test: {e}")






# import time
# import random
# import requests
# import json
# import math
# import base64
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- ULTIMATE CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# SEARCH_URL = "https://www.google.co.in/search?q=ishanprotfolio"
# PORTFOLIO_URL = "https://www.skyscanner.co.in/"
# TOKEN = "CHANGE_ME_TOKEN"

# # MAXIMUM STEALTH SETTINGS
# TOTAL_PROFILES = 1
# PRE_NAVIGATION_DELAY = (10, 20)  # Reduced for efficiency
# HUMAN_BEHAVIOR_TIME = (20, 40)   # Optimized human behavior duration
# PAGE_LOAD_PATIENCE = (5, 10)     # Faster page loading

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     if len(parts) == 1:
#         proto = None
#         main = parts[0]
#     else:
#         proto = parts[0].lower()
#         main = parts[1]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto or "socks5", "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile with optimized settings"""
#     try:
#         gl = GoLogin({"token": TOKEN})
        
#         print(f"🥷 Creating optimized stealth profile: {profile_name}")
        
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac"]),  # Simplified OS selection
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
                
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with optimized stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
        
#         print(f"🚀 Starting optimized stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 7)  # Reduced stabilization time
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject optimized stealth scripts"""
#     try:
#         print("🛡️ Injecting optimized stealth protection...")
        
#         page.evaluate("""
#             // Remove webdriver traces
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined,
#             });
#             delete window.webdriver;
            
#             // Mock chrome runtime
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             // Mock plugins
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [
#                     {
#                         description: "Portable Document Format",
#                         filename: "internal-pdf-viewer",
#                         name: "Chrome PDF Plugin"
#                     }
#                 ]
#             });
            
#             // Mock languages
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             // Mock timezone
#             Date.prototype.getTimezoneOffset = () => -330; // IST
            
#             // Mock screen properties
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
        
#         print("✅ Optimized stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with strategic navigation"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
        
#         # First tab: Google search
#         print(f"🌐 Navigating to Google search: {SEARCH_URL}")
#         page.goto(SEARCH_URL)
#         wait_time = random.uniform(3, 6)
#         time.sleep(wait_time)
#         perform_light_interaction(page)
        
#         # Open portfolio in new tab
#         context = page.context
#         portfolio_page = context.new_page()
#         print(f"🌐 Navigating to portfolio: {PORTFOLIO_URL}")
#         portfolio_page.goto(PORTFOLIO_URL)
#         wait_time = random.uniform(3, 6)
#         time.sleep(wait_time)
#         perform_light_interaction(portfolio_page)
        
#         # Close portfolio tab and return to main page
#         portfolio_page.close()
        
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
        
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions during warmup"""
#     try:
#         scroll_distance = random.randint(100, 300)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(1, 2))
        
#         elements = page.locator("a, button").all()[:3]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.5))
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def ultimate_human_browsing(page: Page):
#     """Optimized human-like browsing behavior"""
#     try:
#         print("🎭 Starting optimized human behavior simulation...")
        
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         page.goto(TARGET_URL)
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             return True
        
#         try:
#             page.wait_for_selector("body", timeout=15000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#             execute_human_action(page, action)
#             time.sleep(random.uniform(1, 3))
        
#         print("✅ Optimized human behavior complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         challenge_indicators = ['captcha', 'robot', 'verify', 'challenge']
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             handle_captcha_page(page)
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page with optimized behavior"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
        
#         button_selectors = ["button", "[role='button']", ".button"]
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible() and element.is_enabled():
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'verify']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
#                             element.hover()
#                             time.sleep(random.uniform(1, 3))
#                             element.click()
#                             time.sleep(random.uniform(2, 5))
#                             return
#             except:
#                 continue
        
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(5, 10))
        
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 200)
#             page.evaluate(f"""
#                 window.scrollBy({{
#                     top: {scroll_distance},
#                     left: 0,
#                     behavior: 'smooth'
#                 }});
#             """)
#             time.sleep(random.uniform(1, 2))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a").all()[:5]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible():
#                         element.hover()
#                         time.sleep(random.uniform(0.5, 1.5))
                
#         elif action == 'reading_pause':
#             time.sleep(random.uniform(2, 5))
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the optimized stealth test"""
#     print("🎯 OPTIMIZED STEALTH MODE ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"optimized_stealth_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(5, 10)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     pre_navigation_warmup(page)
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(30, 60)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
    
#     print(f"\n🏆 OPTIMIZED STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(2)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ OPTIMIZED ANTI-BOT DETECTION BYPASS")
#     print("Optimized stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Optimized stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in optimized stealth test: {e}")



# import time 
# import random
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)     

# # ---------- CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# SEARCH_TERM = "ishanprotfolio"
# PORTFOLIO_URL = "https://www.ishanprotpholio.co.in/"
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"

# # STEALTH SETTINGS
# TOTAL_PROFILES = 1
# PRE_NAVIGATION_DELAY = (8, 15)  # Delay before target site
# HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration
# PAGE_LOAD_PATIENCE = (4, 8)     # Page loading patience

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile"""
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"🥷 Creating stealth profile: {profile_name}")
        
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac"]),
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
        
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             Date.prototype.getTimezoneOffset = () => -330;
            
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
        
#         print("✅ Stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with Google searches and portfolio visit"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
        
#         # First tab: Google search for 'ishanprotfolio'
#         context = page.context
#         search_page = context.new_page()
#         search_url = f"{GOOGLE_SEARCH_BASE}{SEARCH_TERM}"
#         print(f"🌐 Tab 1: Google search: {search_url}")
#         search_page.goto(search_url)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(search_page)
        
#         # Second tab: Google search for portfolio URL and navigate to it
#         portfolio_search_page = context.new_page()
#         portfolio_search_url = f"{GOOGLE_SEARCH_BASE}{PORTFOLIO_URL}"
#         print(f"🌐 Tab 2: Google search: {portfolio_search_url}")
#         portfolio_search_page.goto(portfolio_search_url)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(portfolio_search_page)
        
#         # Click on portfolio link in search results
#         try:
#             portfolio_link = portfolio_search_page.locator(f"a[href*='{PORTFOLIO_URL}']").first
#             if portfolio_link.is_visible():
#                 print(f"🌐 Tab 2: Navigating to {PORTFOLIO_URL}")
#                 portfolio_link.click()
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#                 perform_light_interaction(portfolio_search_page)
#         except Exception as e:
#             print(f"⚠️ Portfolio link click error: {e}")
        
#         # Close tabs
#         search_page.close()
#         portfolio_search_page.close()
        
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
        
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")

# def ultimate_human_browsing(page: Page):
#     """Human-like browsing behavior with cookie clearing on each response"""
#     try:
#         print("🎭 Starting human behavior simulation...")

#         # Set up response listener to clear cookies on each response
#         def handle_response(response):
#             print(f"🌐 Response received: {response.url}")
#             page.context.clearCookies()
#             print("🧹 Cookies cleared after response")

#         page.on("response", handle_response)

#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         page.goto(TARGET_URL)
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             return True
        
#         try:
#             page.wait_for_selector("body", timeout=10000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#             execute_human_action(page, action)
#             perform_light_interaction(page)  # Random clicks
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False
#     finally:
#         # Remove response listener to prevent memory leaks
#         page.remove_listener("response", handle_response)

# def perform_light_interaction(page: Page):
#     """Light human interactions"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         elements = page.locator("a, button").all()[:3]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.2))
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def ultimate_human_browsing(page: Page):
#     """Human-like browsing behavior"""
#     try:
#         print("🎭 Starting human behavior simulation...")
        
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         page.goto(TARGET_URL)
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             return True
        
#         try:
#             page.wait_for_selector("body", timeout=10000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#             execute_human_action(page, action)
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         challenge_indicators = ['captcha', 'robot', 'verify', 'challenge']
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             handle_captcha_page(page)
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
        
#         button_selectors = ["button", "[role='button']", ".button"]
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible() and element.is_enabled():
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'verify']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
#                             element.hover()
#                             time.sleep(random.uniform(1, 2))
#                             element.click()
#                             time.sleep(random.uniform(2, 4))
#                             return
#             except:
#                 continue
        
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(4, 8))
        
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 200)
#             page.evaluate(f"""
#                 window.scrollBy({{
#                     top: {scroll_distance},
#                     left: 0,
#                     behavior: 'smooth'
#                 }});
#             """)
#             time.sleep(random.uniform(0.8, 1.5))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a").all()[:4]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible():
#                         element.hover()
#                         time.sleep(random.uniform(0.4, 1))
                
#         elif action == 'reading_pause':
#             time.sleep(random.uniform(1.5, 4))
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     pre_navigation_warmup(page)
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION")
#     print("Stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")



# import time
# import random
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"  # Target URL
# TOKEN = "CHANGE_ME_TOKEN"
# TOTAL_PROFILES = 1
# PAGE_LOAD_PATIENCE = (4, 8)  # Page loading patience
# HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile"""
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"🥷 Creating stealth profile: {profile_name}")
        
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac"]),
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         # Disable third-party cookies and clear initial cookies
#         context.set_extra_http_headers({"DNT": "1"})  # Do Not Track header
#         context.add_cookies([])  # अपडेट: set_cookies → add_cookies
#         context.clear_cookies()  # Clear any existing cookies for fresh start
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
        
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             Date.prototype.getTimezoneOffset = () => -330;
            
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
        
#         print("✅ Stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         elements = page.locator("a, button").all()[:3]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.2))
#                 random_element.click()
#                 print("🖱️ Performed random click")
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def ultimate_human_browsing(page: Page):
#     """Human-like browsing behavior with cookie clearing on each page load and response"""
#     try:
#         print("🎭 Starting human behavior simulation...")

#         # Clear cookies on every page load
#         def handle_page_load():
#             print("🌐 Page load detected")
#             page.context.clear_cookies()
#             print("🧹 Cookies cleared after page load")

#         # Clear cookies on every response
#         def handle_response(response):
#             print(f"🌐 Response received: {response.url}")
#             page.context.clear_cookies()
#             print("🧹 Cookies cleared after response")

#         # Attach event listeners
#         page.on("load", handle_page_load)
#         page.on("response", handle_response)

#         # Navigate to target URL with retry logic
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         for attempt in range(3):  # Retry up to 3 times
#             try:
#                 page.goto(TARGET_URL, timeout=60000)  # 60 seconds timeout
#                 break
#             except Exception as e:
#                 print(f"⚠️ Attempt {attempt + 1} failed for {TARGET_URL}: {e}")
#                 if attempt == 2:
#                     print(f"❌ Failed to load {TARGET_URL} after 3 attempts")
#                     return False
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         try:
#             page.wait_for_selector("body", timeout=10000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#             execute_human_action(page, action)
#             perform_light_interaction(page)  # Random clicks
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False
#     finally:
#         # Remove event listeners to prevent memory leaks
#         page.remove_listener("load", handle_page_load)
#         page.remove_listener("response", handle_response)

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 200)
#             page.evaluate(f"""
#                 window.scrollBy({{
#                     top: {scroll_distance},
#                     left: 0,
#                     behavior: 'smooth'
#                 }});
#             """)
#             time.sleep(random.uniform(0.8, 1.5))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a").all()[:4]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible():
#                         element.hover()
#                         time.sleep(random.uniform(0.4, 1))
                
#         elif action == 'reading_pause':
#             time.sleep(random.uniform(1.5, 4))
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION")
#     print("Stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")


# import time
# import random
# import uuid
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URLS = [
#     "https://www.skyscanner.co.in/",
#     "https://www.skyscanner.co.in/carhire",
#     "https://www.skyscanner.co.in/flights",
#     "https://www.skyscanner.co.in/hotels",
#     "https://www.skyscanner.co.in/transport/flights/in/knu/251002/251009/?adultsv2=1&cabinclass=economy&childrenv2=&ref=home&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false"
# ]
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"
# TOTAL_PROFILES = 1
# PAGE_LOAD_PATIENCE = (4, 8)  # Page loading patience
# HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile"""
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"🥷 Creating stealth profile: {profile_name}")
        
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac"]),
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         # Disable third-party cookies and clear initial cookies
#         context.set_extra_http_headers({"DNT": "1"})  # Do Not Track header
#         context.add_cookies([])  # Clear any initial cookies
#         context.clear_cookies()  # Ensure fresh state
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
        
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             Date.prototype.getTimezoneOffset = () => -330;
            
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
        
#         print("✅ Stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         elements = page.locator("a, button").all()[:3]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.2))
#                 random_element.click()
#                 print("🖱️ Performed random click")
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def inject_fake_cookies(context):
#     """Inject fake cookies to simulate a new user"""
#     fake_cookies = [
#         {
#             "name": "session_id",
#             "value": str(uuid.uuid4()),  # Random session ID
#             "domain": ".skyscanner.co.in",
#             "path": "/",
#             "expires": int(time.time()) + 3600,  # Expire in 1 hour
#             "httpOnly": False,
#             "secure": True
#         },
#         {
#             "name": "user_prefs",
#             "value": f"pref_{random.randint(1000, 9999)}",
#             "domain": ".skyscanner.co.in",
#             "path": "/",
#             "expires": int(time.time()) + 3600,
#             "httpOnly": False,
#             "secure": True
#         }
#     ]
#     context.add_cookies(fake_cookies)
#     print("🍪 Injected fake cookies")

# def ultimate_human_browsing(page: Page):
#     """Human-like browsing behavior with cookie clearing and fake cookie injection"""
#     try:
#         print("🎭 Starting human behavior simulation...")

#         # Clear cookies and inject fake cookies on every page load
#         def handle_page_load():
#             print("🌐 Page load detected")
#             page.context.clear_cookies()
#             print("🧹 Cookies cleared after page load")
#             inject_fake_cookies(page.context)

#         # Clear cookies and inject fake cookies on every response
#         def handle_response(response):
#             print(f"🌐 Response received: {response.url}")
#             page.context.clear_cookies()
#             print("🧹 Cookies cleared after response")
#             inject_fake_cookies(page.context)

#         # Attach event listeners
#         page.on("load", handle_page_load)
#         page.on("response", handle_response)

#         # Step 1: Type and search first URL
#         google_url = "https://www.google.co.in/"
#         print(f"🌐 Navigating to Google: {google_url}")
#         for attempt in range(3):
#             try:
#                 page.goto(google_url, timeout=60000)
#                 break
#             except Exception as e:
#                 print(f"⚠️ Attempt {attempt + 1} failed for {google_url}: {e}")
#                 if attempt == 2:
#                     print(f"❌ Failed to load {google_url} after 3 attempts")
#                     return False
        
#         # Type first URL in Google search
#         search_bar = page.locator("input[name='q']")
#         if search_bar.is_visible():
#             print(f"🔍 Typing target URL: {TARGET_URLS[0]}")
#             search_bar.type(TARGET_URLS[0], delay=random.uniform(100, 200))
#             search_bar.press("Enter")
#             wait_time = random.uniform(3, 5)
#             print(f"⏳ Waiting for search results: {wait_time:.1f}s")
#             time.sleep(wait_time)
        
#         # Click on the first URL in search results
#         try:
#             target_link = page.locator(f"a[href*='{TARGET_URLS[0]}']").first
#             if target_link.is_visible():
#                 print(f"🌐 Clicking target link: {TARGET_URLS[0]}")
#                 target_link.click()
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#             else:
#                 print(f"⚠️ Target link not found in search results, navigating directly")
#                 page.goto(TARGET_URLS[0], timeout=60000)
#         except Exception as e:
#             print(f"⚠️ Target link click error: {e}")
#             page.goto(TARGET_URLS[0], timeout=60000)

#         # Process each URL
#         for url in TARGET_URLS:
#             print(f"🎯 Navigating to: {url}")
#             for attempt in range(3):
#                 try:
#                     page.goto(url, timeout=60000)
#                     break
#                 except Exception as e:
#                     print(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
#                     if attempt == 2:
#                         print(f"❌ Failed to load {url} after 3 attempts")
#                         continue
            
#             page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#             print(f"⏳ Patient page loading: {page_wait:.1f}s")
#             time.sleep(page_wait)
            
#             try:
#                 page.wait_for_selector("body", timeout=10000)
#                 print("📄 Page elements detected")
#             except TimeoutError:
#                 print("⚠️ Page load timeout, continuing...")
            
#             # Scroll page randomly and fully
#             try:
#                 page_height = page.evaluate("document.body.scrollHeight")
#                 current_pos = 0
#                 while current_pos < page_height:
#                     scroll_distance = random.randint(10, 100)
#                     page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
#                     current_pos += scroll_distance
#                     time.sleep(random.uniform(0.5, 1.5))
#                 print("📜 Scrolled full page")
#             except Exception as e:
#                 print(f"⚠️ Scroll error: {e}")
            
#             # Perform human-like behavior
#             human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#             print(f"🤖 Performing human behavior for {human_time:.1f}s")
#             start_time = time.time()
#             while time.time() - start_time < human_time:
#                 action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#                 execute_human_action(page, action)
#                 perform_light_interaction(page)
#                 time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False
#     finally:
#         page.remove_listener("load", handle_page_load)
#         page.remove_listener("response", handle_response)

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(10, 100)
#             page.evaluate(f"""
#                 window.scrollBy({{
#                     top: {scroll_distance},
#                     left: 0,
#                     behavior: 'smooth'
#                 }});
#             """)
#             time.sleep(random.uniform(0.8, 1.5))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a").all()[:4]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible():
#                         element.hover()
#                         time.sleep(random.uniform(0.4, 1))
                
#         elif action == 'reading_pause':
#             time.sleep(random.uniform(1.5, 4))
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION")
#     print("Stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")



import time
import random
import uuid
from playwright.sync_api import sync_playwright, TimeoutError
from playwright.sync_api import Page, Browser, Playwright

try:
    from gologin import GoLogin
    GOLOGIN_AVAILABLE = True
except ImportError:
    print("Install GoLogin: pip install gologin")
    exit(1)

# ---------- CONFIG ----------
TARGET_URLS = [
    "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc",
    "https://www.skyscanner.co.in/carhire",
    "https://www.skyscanner.co.in/flights",
    "https://www.skyscanner.co.in/hotels",
]
GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
TOKEN = "CHANGE_ME_TOKEN"
TOTAL_PROFILES = 1
PAGE_LOAD_PATIENCE = (4, 8)  # Page loading patience
HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration

# Proxy list
PROXY_LIST = [
    "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
]

def parse_proxy_string(s: str):
    """Parse proxy string"""
    s = s.strip()
    parts = s.split()
    proto = parts[0].lower() if len(parts) > 1 else "socks5"
    main = parts[1] if len(parts) > 1 else parts[0]
    
    segs = main.split(":", 3)
    if len(segs) == 4:
        host, port, username, password = segs
        return {"type": proto, "host": host, "port": port, "username": username, "password": password}
    return None

def create_ultimate_stealth_profile(profile_name, proxy_config=None):
    """Create stealth profile with enhanced fingerprinting"""
    try:
        gl = GoLogin({"token": TOKEN})
        print(f"🥷 Creating stealth profile: {profile_name}")
        
        profile = gl.createProfileRandomFingerprint({
            "os": random.choice(["win", "mac"]),
            "name": profile_name,
            "webgl": {
                "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
                "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650/PCIe/SSE2", "Radeon RX 580"])
            },
            "audioContext": {
                "enable": True,
                "noise": random.uniform(0.0001, 0.0005)
            }
        })
        
        if not profile or 'id' not in profile:
            print(f"❌ Profile creation failed: {profile}")
            return None
            
        profile_id = profile['id']
        print(f"✅ Profile created: {profile_id}")
        
        if proxy_config:
            try:
                proxy_data = {
                    "mode": proxy_config['type'],
                    "host": proxy_config['host'],
                    "port": int(proxy_config['port']),
                    "username": proxy_config.get('username', ''),
                    "password": proxy_config.get('password', '')
                }
                gl.changeProfileProxy(profile_id, proxy_data)
                print(f"🔄 Proxy configured: {proxy_config['host']}")
            except Exception as e:
                print(f"⚠️ Proxy setup warning: {e}")
        
        try:
            gl.updateUserAgentToLatestBrowser([profile_id])
            print("🔄 User agent updated to latest")
        except Exception as e:
            print(f"⚠️ User agent update warning: {e}")
        
        return profile_id
        
    except Exception as e:
        print(f"❌ Profile creation error: {e}")
        return None

def start_maximum_stealth_browser(profile_id):
    """Start browser with stealth configuration"""
    try:
        gl = GoLogin({
            "token": TOKEN,
            "profile_id": profile_id
        })
        print(f"🚀 Starting stealth browser for: {profile_id}")
        debugger_address = gl.start()
        print(f"🔌 Browser endpoint: {debugger_address}")
        
        wait_time = random.uniform(3, 6)
        print(f"⏳ Browser stabilization: {wait_time:.1f}s")
        time.sleep(wait_time)
        
        pw = sync_playwright().start()
        cdp_url = f"http://{debugger_address}"
        browser = pw.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()
        
        # Disable third-party cookies and clear initial cookies
        context.set_extra_http_headers({
            "DNT": "1",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "User-Agent": context.pages[0].evaluate("() => navigator.userAgent")
        })
        context.add_cookies([])  # Clear any initial cookies
        context.clear_cookies()  # Ensure fresh state
        
        inject_ultimate_stealth(page)
        
        return gl, pw, browser, page
        
    except Exception as e:
        print(f"❌ Browser start error: {e}")
        return None, None, None, None

def inject_ultimate_stealth(page: Page):
    """Inject stealth scripts with enhanced fingerprinting"""
    try:
        print("🛡️ Injecting stealth protection...")
        
        page.evaluate("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            delete window.webdriver;
            
            window.chrome = {
                runtime: {
                    onConnect: {addListener: () => {}},
                    onMessage: {addListener: () => {}},
                }
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [{
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    name: "Chrome PDF Plugin"
                }]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'hi-IN'],
            });
            
            Date.prototype.getTimezoneOffset = () => -330;
            
            Object.defineProperty(screen, 'width', {get: () => 1920});
            Object.defineProperty(screen, 'height', {get: () => 1080});
            
            // Spoof WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37446) return 'Intel Inc.';
                if (parameter === 37447) return 'Intel Iris OpenGL Engine';
                return getParameter.apply(this, arguments);
            };
            
            // Spoof Canvas
            const getImageData = HTMLCanvasElement.prototype.getContext('2d').getImageData;
            HTMLCanvasElement.prototype.getContext('2d').getImageData = function() {
                const data = getImageData.apply(this, arguments);
                data.data[0] += Math.random() * 0.01; // Add noise
                return data;
            };
        """)
        
        print("✅ Stealth protection active")
        
    except Exception as e:
        print(f"⚠️ Stealth injection warning: {e}")

def perform_light_interaction(page: Page):
    """Light human interactions with enhanced mouse and keyboard events"""
    try:
        # Random scroll
        scroll_distance = random.randint(10, 100)
        page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
        time.sleep(random.uniform(0.8, 1.5))
        
        # Random mouse movement
        page.mouse.move(random.randint(100, 800), random.randint(100, 600))
        time.sleep(random.uniform(0.3, 0.7))
        
        # Random element interaction
        elements = page.locator("a, button, input").all()[:5]
        if elements:
            random_element = random.choice(elements)
            if random_element.is_visible():
                random_element.hover()
                time.sleep(random.uniform(0.5, 1.2))
                random_element.click()
                print("🖱️ Performed random click")
                # Simulate keyboard input if it's an input field
                if random_element.evaluate("el => el.tagName.toLowerCase() === 'input'"):
                    random_element.type(random.choice(["search", "flights", "hotels"]), delay=random.uniform(100, 200))
                    print("⌨️ Simulated keyboard input")
                
    except Exception as e:
        print(f"⚠️ Light interaction warning: {e}")

def inject_fake_cookies(context):
    """Inject dynamic fake cookies to simulate a new user"""
    fake_cookies = [
        {
            "name": random.choice(["session_id", "user_session", "track_id"]),
            "value": str(uuid.uuid4()),
            "domain": ".skyscanner.co.in",
            "path": "/",
            "expires": int(time.time()) + random.randint(1800, 7200),  # Random expiry (30 min to 2 hours)
            "httpOnly": random.choice([True, False]),
            "secure": True
        },
        {
            "name": random.choice(["user_prefs", "settings", "pref_id"]),
            "value": f"pref_{random.randint(1000, 9999)}",
            "domain": ".skyscanner.co.in",
            "path": "/",
            "expires": int(time.time()) + random.randint(1800, 7200),
            "httpOnly": random.choice([True, False]),
            "secure": True
        }
    ]
    context.add_cookies(fake_cookies)
    print("🍪 Injected dynamic fake cookies")

def ultimate_human_browsing(page: Page):
    """Human-like browsing behavior with cookie management and CAPTCHA bypass"""
    try:
        print("🎭 Starting human behavior simulation...")

        # Preserve PerimeterX cookies
        preserved_cookies = []

        def handle_page_load():
            print("🌐 Page load detected")
            current_cookies = page.context.cookies()
            # Preserve PerimeterX cookies
            for cookie in current_cookies:
                if cookie["name"].startswith("_px"):
                    preserved_cookies.append(cookie)
            page.context.clear_cookies()
            # Restore PerimeterX cookies
            if preserved_cookies:
                page.context.add_cookies(preserved_cookies)
                print("🍪 Restored PerimeterX cookies")
            inject_fake_cookies(page.context)

        def handle_response(response):
            print(f"🌐 Response received: {response.url}")
            if "captcha-v2" in response.url:
                print("🚨 CAPTCHA detected, attempting to handle...")
                # Simulate human interaction on CAPTCHA page
                try:
                    page.wait_for_selector("body", timeout=10000)
                    buttons = page.locator("button, [role='button']").all()
                    for button in buttons:
                        if button.is_visible() and "verify" in button.inner_text().lower():
                            button.hover()
                            time.sleep(random.uniform(1, 2))
                            button.click()
                            print("🖱️ Clicked CAPTCHA verify button")
                            break
                except Exception as e:
                    print(f"⚠️ CAPTCHA handling error: {e}")
            current_cookies = page.context.cookies()
            # Preserve PerimeterX cookies
            for cookie in current_cookies:
                if cookie["name"].startswith("_px"):
                    preserved_cookies.append(cookie)
            page.context.clear_cookies()
            if preserved_cookies:
                page.context.add_cookies(preserved_cookies)
                print("🍪 Restored PerimeterX cookies")
            inject_fake_cookies(page.context)

        # Attach event listeners
        page.on("load", handle_page_load)
        page.on("response", handle_response)

        # Step 1: Type and search first URL
        google_url = "https://www.google.co.in/"
        print(f"🌐 Navigating to Google: {google_url}")
        for attempt in range(3):
            try:
                page.goto(google_url, timeout=60000)
                page.wait_for_load_state("networkidle")
                break
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed for {google_url}: {e}")
                if attempt == 2:
                    print(f"❌ Failed to load {google_url} after 3 attempts")
                    return False
        
        # Type first URL in Google search
        search_bar = page.locator("input[name='q']")
        if search_bar.is_visible():
            print(f"🔍 Typing target URL: {TARGET_URLS[0]}")
            search_bar.type(TARGET_URLS[0], delay=random.uniform(100, 200))
            search_bar.press("Enter")
            wait_time = random.uniform(3, 5)
            print(f"⏳ Waiting for search results: {wait_time:.1f}s")
            time.sleep(wait_time)
        
        # Click on the first URL in search results
        try:
            target_link = page.locator(f"a[href*='{TARGET_URLS[0]}']").first
            if target_link.is_visible():
                print(f"🌐 Clicking target link: {TARGET_URLS[0]}")
                target_link.click()
                page.wait_for_load_state("networkidle")
                wait_time = random.uniform(4, 7)
                time.sleep(wait_time)
            else:
                print(f"⚠️ Target link not found in search results, navigating directly")
                page.goto(TARGET_URLS[0], timeout=60000)
                page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"⚠️ Target link click error: {e}")
            page.goto(TARGET_URLS[0], timeout=60000)
            page.wait_for_load_state("networkidle")

        # Process each URL
        for url in TARGET_URLS:
            print(f"🎯 Navigating to: {url}")
            for attempt in range(3):
                try:
                    page.goto(url, timeout=60000)
                    page.wait_for_load_state("networkidle")
                    break
                except Exception as e:
                    print(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt == 2:
                        print(f"❌ Failed to load {url} after 3 attempts")
                        continue
            
            page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
            print(f"⏳ Patient page loading: {page_wait:.1f}s")
            time.sleep(page_wait)
            
            try:
                page.wait_for_selector("body", timeout=10000)
                print("📄 Page elements detected")
            except TimeoutError:
                print("⚠️ Page load timeout, continuing...")
            
            # Scroll page randomly and fully
            try:
                page_height = page.evaluate("document.body.scrollHeight")
                current_pos = 0
                while current_pos < page_height:
                    scroll_distance = random.randint(10, 100)
                    page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
                    current_pos += scroll_distance
                    time.sleep(random.uniform(0.5, 1.5))
                print("📜 Scrolled full page")
            except Exception as e:
                print(f"⚠️ Scroll error: {e}")
            
            # Perform human-like behavior
            human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
            print(f"🤖 Performing human behavior for {human_time:.1f}s")
            start_time = time.time()
            while time.time() - start_time < human_time:
                action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
                execute_human_action(page, action)
                perform_light_interaction(page)
                time.sleep(random.uniform(0.8, 2.5))
        
        print("✅ Human behavior complete")
        return True
        
    except Exception as e:
        print(f"❌ Human browsing error: {e}")
        return False
    finally:
        page.remove_listener("load", handle_page_load)
        page.remove_listener("response", handle_response)

def execute_human_action(page: Page, action):
    """Execute specific human-like action"""
    try:
        if action == 'realistic_scroll':
            scroll_distance = random.randint(10, 100)
            page.evaluate(f"""
                window.scrollBy({{
                    top: {scroll_distance},
                    left: 0,
                    behavior: 'smooth'
                }});
            """)
            time.sleep(random.uniform(0.8, 1.5))
                
        elif action == 'mouse_trail':
            elements = page.locator("div, a").all()[:4]
            if elements:
                for element in random.sample(elements, min(2, len(elements))):
                    if element.is_visible():
                        element.hover()
                        time.sleep(random.uniform(0.4, 1))
                
        elif action == 'reading_pause':
            time.sleep(random.uniform(1.5, 4))
                
    except Exception as e:
        print(f"⚠️ Human action error: {e}")

def run_ultimate_stealth_test():
    """Run the stealth test"""
    print("🎯 STEALTH MODE WITH COOKIE CONFUSION ACTIVATED")
    print("=" * 60)
    
    successful_runs = 0
    
    for profile_num in range(1, TOTAL_PROFILES + 1):
        print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
        profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
        proxy_config = None
        if PROXY_LIST:
            proxy_str = random.choice(PROXY_LIST)
            proxy_config = parse_proxy_string(proxy_str)
        
        profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
        if profile_id:
            wait_time = random.uniform(4, 8)
            print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
            time.sleep(wait_time)
            
            gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
            if page:
                try:
                    success = ultimate_human_browsing(page)
                    
                    if success:
                        successful_runs += 1
                        print(f"🎉 PROFILE {profile_num} - SUCCESS!")
                    else:
                        print(f"❌ PROFILE {profile_num} - FAILED")
                    
                    session_time = random.uniform(20, 40)
                    print(f"🕐 Maintaining session: {session_time:.1f}s")
                    time.sleep(session_time)
                    
                finally:
                    cleanup_browser(gl, pw, browser)
            else:
                print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
        else:
            print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
    
    print(f"\n🏆 STEALTH TEST COMPLETE!")
    print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
    """Clean up browser resources"""
    try:
        if browser:
            browser.close()
        time.sleep(1)
        if gl:
            gl.stop()
        if pw:
            pw.stop()
        print("🧹 Browser session terminated")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

if __name__ == "__main__":
    print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION")
    print("Stealth configuration activated")
    print("=" * 60)
    
    if not GOLOGIN_AVAILABLE:
        print("❌ GoLogin not available!")
        exit(1)
    
    try:
        run_ultimate_stealth_test()
    except KeyboardInterrupt:
        print("\n🛑 Stealth test interrupted")
    except Exception as e:
        print(f"❌ Fatal error in stealth test: {e}")


# import time
# import random
# import uuid
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URLS = [
#     "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc",
#     "https://www.skyscanner.co.in/carhire",
#     "https://www.skyscanner.co.in/flights",
#     "https://www.skyscanner.co.in/hotels",
# ]
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"
# TOTAL_PROFILES = 100
# PAGE_LOAD_PATIENCE = (4, 8)  # Page loading patience
# HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile with enhanced fingerprinting"""
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"🥷 Creating stealth profile: {profile_name}")
        
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac"]),
#             "name": profile_name,
#             "webgl": {
#                 "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
#                 "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650/PCIe/SSE2", "Radeon RX 580"])
#             },
#             "audioContext": {
#                 "enable": True,
#                 "noise": random.uniform(0.0001, 0.0005)
#             }
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         # Disable third-party cookies and clear initial cookies
#         context.set_extra_http_headers({
#             "DNT": "1",
#             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
#             "User-Agent": context.pages[0].evaluate("() => navigator.userAgent")
#         })
#         context.add_cookies([])  # Clear any initial cookies
#         context.clear_cookies()  # Ensure fresh state
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts with enhanced fingerprinting"""
#     try:
#         print("🛡️ Injecting stealth protection...")
        
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             Date.prototype.getTimezoneOffset = () => -330;
            
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
            
#             // Spoof WebGL
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 if (parameter === 37446) return 'Intel Inc.';
#                 if (parameter === 37447) return 'Intel Iris OpenGL Engine';
#                 return getParameter.apply(this, arguments);
#             };
            
#             // Spoof Canvas
#             const getImageData = HTMLCanvasElement.prototype.getContext('2d').getImageData;
#             HTMLCanvasElement.prototype.getContext('2d').getImageData = function() {
#                 const data = getImageData.apply(this, arguments);
#                 data.data[0] += Math.random() * 0.01; // Add noise
#                 return data;
#             };
#         """)
        
#         print("✅ Stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions with enhanced mouse and keyboard events"""
#     try:
#         # Random scroll
#         scroll_distance = random.randint(10, 100)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         # Random mouse movement
#         page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#         time.sleep(random.uniform(0.3, 0.7))
        
#         # Random element interaction
#         elements = page.locator("a, button, input").all()[:5]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.2))
#                 random_element.click()
#                 print("🖱️ Performed random click")
#                 # Simulate keyboard input if it's an input field
#                 if random_element.evaluate("el => el.tagName.toLowerCase() === 'input'"):
#                     random_element.type(random.choice(["search", "flights", "hotels"]), delay=random.uniform(100, 200))
#                     print("⌨️ Simulated keyboard input")
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def inject_fake_cookies(context):
#     """Inject dynamic fake cookies to simulate a new user"""
#     fake_cookies = [
#         {
#             "name": random.choice(["session_id", "user_session", "track_id"]),
#             "value": str(uuid.uuid4()),
#             "domain": ".skyscanner.co.in",
#             "path": "/",
#             "expires": int(time.time()) + random.randint(1800, 7200),  # Random expiry (30 min to 2 hours)
#             "httpOnly": random.choice([True, False]),
#             "secure": True
#         },
#         {
#             "name": random.choice(["user_prefs", "settings", "pref_id"]),
#             "value": f"pref_{random.randint(1000, 9999)}",
#             "domain": ".skyscanner.co.in",
#             "path": "/",
#             "expires": int(time.time()) + random.randint(1800, 7200),
#             "httpOnly": random.choice([True, False]),
#             "secure": True
#         }
#     ]
#     context.add_cookies(fake_cookies)
#     print("🍪 Injected dynamic fake cookies")

# def ultimate_human_browsing(page: Page):
#     """Human-like browsing behavior with cookie management and CAPTCHA bypass"""
#     try:
#         print("🎭 Starting human behavior simulation...")

#         # Preserve PerimeterX cookies
#         preserved_cookies = []

#         def handle_page_load():
#             print("🌐 Page load detected")
#             current_cookies = page.context.cookies()
#             # Preserve PerimeterX cookies
#             for cookie in current_cookies:
#                 if cookie["name"].startswith("_px"):
#                     preserved_cookies.append(cookie)
#             page.context.clear_cookies()
#             # Restore PerimeterX cookies
#             if preserved_cookies:
#                 page.context.add_cookies(preserved_cookies)
#                 print("🍪 Restored PerimeterX cookies")
#             inject_fake_cookies(page.context)

#         def handle_response(response):
#             print(f"🌐 Response received: {response.url}")
#             if "captcha-v2" in response.url:
#                 print("🚨 CAPTCHA detected, attempting to handle...")
#                 # Simulate human interaction on CAPTCHA page
#                 try:
#                     page.wait_for_selector("body", timeout=10000)
#                     buttons = page.locator("button, [role='button']").all()
#                     for button in buttons:
#                         if button.is_visible() and "verify" in button.inner_text().lower():
#                             button.hover()
#                             time.sleep(random.uniform(1, 2))
#                             button.click()
#                             print("🖱️ Clicked CAPTCHA verify button")
#                             break
#                 except Exception as e:
#                     print(f"⚠️ CAPTCHA handling error: {e}")
#             current_cookies = page.context.cookies()
#             # Preserve PerimeterX cookies
#             for cookie in current_cookies:
#                 if cookie["name"].startswith("_px"):
#                     preserved_cookies.append(cookie)
#             page.context.clear_cookies()
#             if preserved_cookies:
#                 page.context.add_cookies(preserved_cookies)
#                 print("🍪 Restored PerimeterX cookies")
#             inject_fake_cookies(page.context)

#         # Attach event listeners
#         page.on("load", handle_page_load)
#         page.on("response", handle_response)

#         # Step 1: Type and search first URL
#         google_url = "https://www.google.co.in/"
#         print(f"🌐 Navigating to Google: {google_url}")
#         for attempt in range(3):
#             try:
#                 page.goto(google_url, timeout=60000)
#                 page.wait_for_load_state("networkidle")
#                 break
#             except Exception as e:
#                 print(f"⚠️ Attempt {attempt + 1} failed for {google_url}: {e}")
#                 if attempt == 2:
#                     print(f"❌ Failed to load {google_url} after 3 attempts")
#                     return False
        
#         # Type first URL in Google search
#         search_bar = page.locator("input[name='q']")
#         if search_bar.is_visible():
#             print(f"🔍 Typing target URL: {TARGET_URLS[0]}")
#             search_bar.type(TARGET_URLS[0], delay=random.uniform(100, 200))
#             search_bar.press("Enter")
#             wait_time = random.uniform(3, 5)
#             print(f"⏳ Waiting for search results: {wait_time:.1f}s")
#             time.sleep(wait_time)
        
#         # Click on the first URL in search results
#         try:
#             target_link = page.locator(f"a[href*='{TARGET_URLS[0]}']").first
#             if target_link.is_visible():
#                 print(f"🌐 Clicking target link: {TARGET_URLS[0]}")
#                 target_link.click()
#                 page.wait_for_load_state("networkidle")
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#             else:
#                 print(f"⚠️ Target link not found in search results, navigating directly")
#                 page.goto(TARGET_URLS[0], timeout=60000)
#                 page.wait_for_load_state("networkidle")
#         except Exception as e:
#             print(f"⚠️ Target link click error: {e}")
#             page.goto(TARGET_URLS[0], timeout=60000)
#             page.wait_for_load_state("networkidle")

#         # Process the first URL (already visited via Google, but perform behaviors)
#         url = TARGET_URLS[0]
#         print(f"🎯 Processing first URL: {url}")
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         try:
#             page.wait_for_selector("body", timeout=10000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         # Scroll page randomly and fully
#         try:
#             page_height = page.evaluate("document.body.scrollHeight")
#             current_pos = 0
#             while current_pos < page_height:
#                 scroll_distance = random.randint(10, 100)
#                 page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
#                 current_pos += scroll_distance
#                 time.sleep(random.uniform(0.5, 1.5))
#             print("📜 Scrolled full page")
#         except Exception as e:
#             print(f"⚠️ Scroll error: {e}")
        
#         # Perform human-like behavior on first URL
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s on first URL")
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#             execute_human_action(page, action)
#             perform_light_interaction(page)
#             time.sleep(random.uniform(0.8, 2.5))

#         # Now select and process one random URL from the remaining
#         remaining_urls = TARGET_URLS[1:]
#         if remaining_urls:
#             random_url = random.choice(remaining_urls)
#             print(f"🎯 Navigating to random URL: {random_url}")
#             for attempt in range(3):
#                 try:
#                     page.goto(random_url, timeout=60000)
#                     page.wait_for_load_state("networkidle")
#                     break
#                 except Exception as e:
#                     print(f"⚠️ Attempt {attempt + 1} failed for {random_url}: {e}")
#                     if attempt == 2:
#                         print(f"❌ Failed to load {random_url} after 3 attempts")
#                         continue
            
#             page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#             print(f"⏳ Patient page loading: {page_wait:.1f}s")
#             time.sleep(page_wait)
            
#             try:
#                 page.wait_for_selector("body", timeout=10000)
#                 print("📄 Page elements detected")
#             except TimeoutError:
#                 print("⚠️ Page load timeout, continuing...")
            
#             # Scroll page randomly and fully
#             try:
#                 page_height = page.evaluate("document.body.scrollHeight")
#                 current_pos = 0
#                 while current_pos < page_height:
#                     scroll_distance = random.randint(10, 100)
#                     page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
#                     current_pos += scroll_distance
#                     time.sleep(random.uniform(0.5, 1.5))
#                 print("📜 Scrolled full page")
#             except Exception as e:
#                 print(f"⚠️ Scroll error: {e}")
            
#             # Perform human-like behavior on random URL
#             human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#             print(f"🤖 Performing human behavior for {human_time:.1f}s on random URL")
#             start_time = time.time()
#             while time.time() - start_time < human_time:
#                 action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#                 execute_human_action(page, action)
#                 perform_light_interaction(page)
#                 time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False
#     finally:
#         page.remove_listener("load", handle_page_load)
#         page.remove_listener("response", handle_response)

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(10, 100)
#             page.evaluate(f"""
#                 window.scrollBy({{
#                     top: {scroll_distance},
#                     left: 0,
#                     behavior: 'smooth'
#                 }});
#             """)
#             time.sleep(random.uniform(0.8, 1.5))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a").all()[:4]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible():
#                         element.hover()
#                         time.sleep(random.uniform(0.4, 1))
                
#         elif action == 'reading_pause':
#             time.sleep(random.uniform(1.5, 4))
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION")
#     print("Stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")


# import time
# import random
# import uuid
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc"
# TOKEN = "CHANGE_ME_TOKEN"
# TOTAL_PROFILES = 100
# PAGE_LOAD_PATIENCE = (4, 8)  # Page loading patience
# HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def test_proxy_connection(page: Page):
#     """Test if proxy is working by checking IP"""
#     try:
#         print("🔍 Testing proxy connection...")
#         page.goto("https://httpbin.org/ip", timeout=15000, wait_until="domcontentloaded")
#         time.sleep(2)
#         ip_info = page.inner_text("body")
#         print(f"🌐 Current IP: {ip_info[:100]}...")
#         return True
#     except Exception as e:
#         print(f"⚠️ Proxy test failed: {e}")
#         return False

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile with enhanced fingerprinting and retry logic"""
#     max_retries = 3
#     retry_delay = 5
    
#     for attempt in range(max_retries):
#         try:
#             print(f"🥷 Creating stealth profile: {profile_name} (Attempt {attempt + 1}/{max_retries})")
            
#             gl = GoLogin({"token": TOKEN})
            
#             # Add delay between attempts
#             if attempt > 0:
#                 wait_time = retry_delay * attempt
#                 print(f"⏳ Waiting {wait_time}s before retry...")
#                 time.sleep(wait_time)
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name,
#                 "webgl": {
#                     "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
#                     "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650/PCIe/SSE2", "Radeon RX 580"])
#                 },
#                 "audioContext": {
#                     "enable": True,
#                     "noise": random.uniform(0.0001, 0.0005)
#                 }
#             })
            
#             if not profile or 'id' not in profile:
#                 print(f"❌ Profile creation returned invalid data: {profile}")
#                 if attempt < max_retries - 1:
#                     continue
#                 return None
                
#             profile_id = profile['id']
#             print(f"✅ Profile created successfully: {profile_id}")
            
#             # Configure proxy with retry
#             if proxy_config:
#                 try:
#                     proxy_data = {
#                         "mode": proxy_config['type'],
#                         "host": proxy_config['host'],
#                         "port": int(proxy_config['port']),
#                         "username": proxy_config.get('username', ''),
#                         "password": proxy_config.get('password', '')
#                     }
#                     gl.changeProfileProxy(profile_id, proxy_data)
#                     print(f"🔄 Proxy configured: {proxy_config['host']}")
#                 except Exception as proxy_error:
#                     print(f"⚠️ Proxy setup failed: {proxy_error}")
            
#             # Update user agent with retry
#             try:
#                 gl.updateUserAgentToLatestBrowser([profile_id])
#                 print("🔄 User agent updated to latest")
#             except Exception as ua_error:
#                 print(f"⚠️ User agent update failed: {ua_error}")
            
#             return profile_id
            
#         except Exception as e:
#             error_msg = str(e)
#             print(f"❌ Profile creation attempt {attempt + 1} failed: {error_msg}")
            
#             # Check for specific connection errors
#             if "Connection aborted" in error_msg or "ConnectionResetError" in error_msg or "RemoteDisconnected" in error_msg:
#                 print("🌐 Network connection issue detected")
#                 if attempt < max_retries - 1:
#                     print(f"🔄 Retrying in {retry_delay}s...")
#                     time.sleep(retry_delay)
#                     continue
#             elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
#                 print("⏰ Timeout issue detected")
#                 if attempt < max_retries - 1:
#                     print(f"🔄 Retrying with longer timeout in {retry_delay}s...")
#                     time.sleep(retry_delay)
#                     continue
#             else:
#                 print(f"💥 Unexpected error: {error_msg}")
#                 if attempt < max_retries - 1:
#                     print(f"🔄 Retrying anyway in {retry_delay}s...")
#                     time.sleep(retry_delay)
#                     continue
    
#     print(f"❌ All {max_retries} profile creation attempts failed")
#     return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration and retry logic"""
#     max_retries = 2
    
#     for attempt in range(max_retries):
#         try:
#             print(f"🚀 Starting stealth browser for: {profile_id} (Attempt {attempt + 1}/{max_retries})")
            
#             gl = GoLogin({
#                 "token": TOKEN,
#                 "profile_id": profile_id
#             })
            
#             debugger_address = gl.start()
#             print(f"🔌 Browser endpoint: {debugger_address}")
            
#             if not debugger_address:
#                 print("❌ No debugger address received")
#                 if attempt < max_retries - 1:
#                     continue
#                 return None, None, None, None
            
#             wait_time = random.uniform(3, 6)
#             print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             pw = sync_playwright().start()
#             cdp_url = f"http://{debugger_address}"
            
#             try:
#                 browser = pw.chromium.connect_over_cdp(cdp_url)
#             except Exception as connect_error:
#                 print(f"❌ Browser connection failed: {connect_error}")
#                 if attempt < max_retries - 1:
#                     print("🔄 Retrying browser connection...")
#                     gl.stop()
#                     pw.stop()
#                     time.sleep(3)
#                     continue
#                 return None, None, None, None
            
#             context = browser.contexts[0] if browser.contexts else browser.new_context()
            
#             if context.pages:
#                 page = context.pages[0]
#             else:
#                 page = context.new_page()
            
#             # Set headers with error handling
#             try:
#                 context.set_extra_http_headers({
#                     "DNT": "1",
#                     "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
#                 })
#             except Exception as header_error:
#                 print(f"⚠️ Header setup warning: {header_error}")
            
#             inject_ultimate_stealth(page)
            
#             return gl, pw, browser, page
            
#         except Exception as e:
#             print(f"❌ Browser start attempt {attempt + 1} failed: {e}")
#             if attempt < max_retries - 1:
#                 print("🔄 Retrying browser start...")
#                 time.sleep(3)
#                 continue
    
#     print(f"❌ All {max_retries} browser start attempts failed")
#     return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts with enhanced fingerprinting"""
#     try:
#         print("🛡️ Injecting stealth protection...")
        
#         page.add_init_script("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             // Spoof WebGL
#             const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 if (parameter === 37446) return 'Intel Inc.';
#                 if (parameter === 37447) return 'Intel Iris OpenGL Engine';
#                 return originalGetParameter.call(this, parameter);
#             };
            
#             // Add timezone
#             try {
#                 Date.prototype.getTimezoneOffset = () => -330;
#             } catch(e) {}
#         """)
        
#         print("✅ Stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions with enhanced mouse and keyboard events"""
#     try:
#         # Random scroll with error handling
#         try:
#             scroll_distance = random.randint(10, 100)
#             page.evaluate(f"window.scrollBy(0, {scroll_distance});")
#             time.sleep(random.uniform(0.8, 1.5))
#         except:
#             pass
        
#         # Random mouse movement with error handling
#         try:
#             page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#             time.sleep(random.uniform(0.3, 0.7))
#         except:
#             pass
        
#         # Try to interact with visible elements
#         try:
#             elements = page.locator("a, button").all()[:3]
#             if elements:
#                 random_element = random.choice(elements)
#                 if random_element.is_visible():
#                     random_element.hover()
#                     time.sleep(random.uniform(0.5, 1.2))
#                     print("🖱️ Performed hover interaction")
#         except:
#             pass
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def ultimate_human_browsing(page: Page):
#     """Human-like browsing behavior directly on target URL"""
#     try:
#         print("🎭 Starting human behavior simulation...")

#         # Navigate directly to target URL with multiple strategies
#         print(f"🌐 Navigating directly to target URL: {TARGET_URL}")
        
#         success = False
        
#         # Strategy 1: Try with networkidle
#         try:
#             print("📡 Attempt 1: Using networkidle strategy...")
#             page.goto(TARGET_URL, timeout=45000, wait_until="networkidle")
#             print("✅ Successfully loaded target URL with networkidle")
#             success = True
#         except Exception as e:
#             print(f"⚠️ Networkidle strategy failed: {e}")
        
#         # Strategy 2: Try with domcontentloaded
#         if not success:
#             try:
#                 print("📡 Attempt 2: Using domcontentloaded strategy...")
#                 page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
#                 print("✅ Successfully loaded target URL with domcontentloaded")
#                 success = True
#             except Exception as e:
#                 print(f"⚠️ Domcontentloaded strategy failed: {e}")
        
#         # Strategy 3: Try with load
#         if not success:
#             try:
#                 print("📡 Attempt 3: Using load strategy...")
#                 page.goto(TARGET_URL, timeout=90000, wait_until="load")
#                 print("✅ Successfully loaded target URL with load")
#                 success = True
#             except Exception as e:
#                 print(f"⚠️ Load strategy failed: {e}")
        
#         # Strategy 4: Try without wait condition
#         if not success:
#             try:
#                 print("📡 Attempt 4: Using no wait condition...")
#                 page.goto(TARGET_URL, timeout=120000)
#                 print("✅ Successfully loaded target URL without wait condition")
#                 success = True
#             except Exception as e:
#                 print(f"⚠️ No wait condition strategy failed: {e}")
        
#         if not success:
#             print("❌ All loading strategies failed")
#             return False
        
#         # Wait for page to stabilize
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Page stabilization: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         # Check if page loaded properly
#         try:
#             # Wait for basic page elements
#             page.wait_for_selector("body", timeout=15000)
#             print("📄 Page body detected")
            
#             # Try to get page title to confirm it loaded
#             try:
#                 title = page.title()
#                 print(f"📰 Page title: {title[:50]}...")
#             except:
#                 print("📰 No title detected")
                
#             # Check if we can get page URL
#             try:
#                 current_url = page.url
#                 print(f"🔗 Current URL: {current_url[:80]}...")
#             except:
#                 print("🔗 URL detection failed")
                
#         except TimeoutError:
#             print("⚠️ Body timeout, but continuing with available page...")
        
#         # Scroll page behavior with better error handling
#         try:
#             print("📜 Starting scroll behavior...")
#             # Get page height with fallback
#             try:
#                 page_height = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, window.innerHeight)")
#             except:
#                 page_height = page.evaluate("window.innerHeight") or 1000
                
#             print(f"📏 Page height: {page_height}px")
            
#             if page_height > 500:
#                 # Scroll in chunks
#                 scroll_positions = [0, page_height * 0.25, page_height * 0.5, page_height * 0.75, page_height * 0.9]
#                 for i, pos in enumerate(scroll_positions):
#                     try:
#                         page.evaluate(f"window.scrollTo({{top: {int(pos)}, behavior: 'smooth'}});")
#                         print(f"📜 Scroll position {i+1}/5: {int(pos)}px")
#                         time.sleep(random.uniform(1.5, 3))
#                     except Exception as scroll_error:
#                         print(f"⚠️ Scroll {i+1} error: {scroll_error}")
#                         continue
#                 print("📜 Completed page scrolling")
#             else:
#                 # Simple scroll for shorter pages
#                 try:
#                     page.evaluate("window.scrollBy({top: 200, behavior: 'smooth'});")
#                     time.sleep(1)
#                     print("📜 Simple scroll completed")
#                 except Exception as e:
#                     print(f"⚠️ Simple scroll error: {e}")
#         except Exception as e:
#             print(f"⚠️ Scroll setup error: {e}")
        
#         # Perform human-like behavior
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
#         start_time = time.time()
        
#         while time.time() - start_time < human_time:
#             action = random.choice(['scroll_small', 'mouse_move', 'pause'])
            
#             if action == 'scroll_small':
#                 scroll_distance = random.randint(50, 150)
#                 page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
#                 time.sleep(random.uniform(1, 2))
#             elif action == 'mouse_move':
#                 x = random.randint(100, 1200)
#                 y = random.randint(100, 800)
#                 page.mouse.move(x, y)
#                 time.sleep(random.uniform(0.5, 1))
#             elif action == 'pause':
#                 time.sleep(random.uniform(2, 4))
            
#             perform_light_interaction(page)
#             time.sleep(random.uniform(0.5, 1.5))
        
#         print("✅ Human behavior simulation complete")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False

# def run_ultimate_stealth_test():
#     """Run the stealth test with enhanced error handling"""
#     print("🎯 STEALTH MODE - DIRECT URL LOADING")
#     print("=" * 60)
    
#     successful_runs = 0
#     failed_profiles = 0
#     max_consecutive_failures = 5
#     consecutive_failures = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         # Check for too many consecutive failures
#         if consecutive_failures >= max_consecutive_failures:
#             print(f"⚠️ Too many consecutive failures ({consecutive_failures}). Taking a longer break...")
#             time.sleep(30)  # 30 second break
#             consecutive_failures = 0
        
#         profile_name = f"stealth_direct_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         # Create profile with retries
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(3, 5)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     # Test proxy first
#                     proxy_test = test_proxy_connection(page)
#                     if not proxy_test:
#                         print("⚠️ Proxy test failed, but continuing...")
                    
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         consecutive_failures = 0  # Reset failure counter
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         failed_profiles += 1
#                         consecutive_failures += 1
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(15, 25)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 failed_profiles += 1
#                 consecutive_failures += 1
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             failed_profiles += 1
#             consecutive_failures += 1
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
        
#         # Brief pause between profiles (longer if there were failures)
#         pause_time = random.uniform(3, 6) if consecutive_failures == 0 else random.uniform(8, 12)
#         time.sleep(pause_time)
        
#         # Show progress every 10 profiles
#         if profile_num % 10 == 0:
#             success_rate = (successful_runs / profile_num) * 100
#             print(f"\n📊 Progress Update - Completed: {profile_num}/{TOTAL_PROFILES}")
#             print(f"✅ Successful: {successful_runs} | ❌ Failed: {failed_profiles}")
#             print(f"📈 Current Success Rate: {success_rate:.1f}%")
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Final Results:")
#     print(f"✅ Successful: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")
#     print(f"❌ Failed: {failed_profiles}/{TOTAL_PROFILES} ({failed_profiles/TOTAL_PROFILES*100:.1f}%)")
    
#     if successful_runs > 0:
#         print(f"🎯 Target URL was successfully loaded {successful_runs} times!")
#     else:
#         print("😞 No successful runs. Consider checking network connection or GoLogin account.")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ DIRECT URL STEALTH LOADING")
#     print("Target URL: https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")


# import time
# import random
# import json
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc"
# TOKEN = "CHANGE_ME_TOKEN"
# TOTAL_PROFILES = 100
# PAGE_LOAD_PATIENCE = (4, 8)
# HUMAN_BEHAVIOR_TIME = (15, 30)

# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # ========== FINGERPRINT DETECTION FUNCTIONS ==========

# def extract_complete_fingerprint(page: Page):
#     """Extract complete browser fingerprint that websites use for detection"""
#     print("\n" + "="*70)
#     print("🔍 EXTRACTING COMPLETE FINGERPRINT")
#     print("="*70)
    
#     fingerprint = {}
    
#     try:
#         fingerprint_data = page.evaluate("""
#             () => {
#                 const fp = {};
                
#                 // ========== NAVIGATOR PROPERTIES ==========
#                 fp.navigator = {
#                     userAgent: navigator.userAgent,
#                     platform: navigator.platform,
#                     language: navigator.language,
#                     languages: navigator.languages,
#                     hardwareConcurrency: navigator.hardwareConcurrency,
#                     deviceMemory: navigator.deviceMemory || 'not available',
#                     maxTouchPoints: navigator.maxTouchPoints,
#                     vendor: navigator.vendor,
#                     vendorSub: navigator.vendorSub,
#                     productSub: navigator.productSub,
#                     appVersion: navigator.appVersion,
#                     appName: navigator.appName,
#                     appCodeName: navigator.appCodeName,
#                     cookieEnabled: navigator.cookieEnabled,
#                     doNotTrack: navigator.doNotTrack,
#                     onLine: navigator.onLine,
#                     webdriver: navigator.webdriver,
#                     pdfViewerEnabled: navigator.pdfViewerEnabled || false
#                 };
                
#                 // ========== WEBDRIVER DETECTION ==========
#                 fp.webdriverDetection = {
#                     navigatorWebdriver: navigator.webdriver,
#                     windowWebdriver: window.webdriver,
#                     documentWebdriver: document.webdriver,
#                     navigatorWebdriverType: typeof navigator.webdriver,
#                     domAutomation: window.domAutomation || 'not present',
#                     domAutomationController: window.domAutomationController || 'not present',
#                     callPhantom: window.callPhantom || 'not present',
#                     _phantom: window._phantom || 'not present',
#                     phantom: window.phantom || 'not present',
#                     __nightmare: window.__nightmare || 'not present',
#                     _selenium: window._selenium || 'not present',
#                     callSelenium: window.callSelenium || 'not present',
#                     _Selenium_IDE_Recorder: window._Selenium_IDE_Recorder || 'not present'
#                 };
                
#                 // ========== CHROME DETECTION ==========
#                 fp.chromeDetection = {
#                     chromeExists: !!window.chrome,
#                     chromeRuntime: window.chrome && window.chrome.runtime ? 'present' : 'not present',
#                     chromeLoadTimes: window.chrome && window.chrome.loadTimes ? 'present' : 'not present',
#                     chromeCsi: window.chrome && window.chrome.csi ? 'present' : 'not present',
#                     chromeApp: window.chrome && window.chrome.app ? 'present' : 'not present',
#                     chromeKeys: window.chrome ? Object.keys(window.chrome) : []
#                 };
                
#                 // ========== PERMISSIONS ==========
#                 fp.permissions = {
#                     notificationPermission: Notification.permission || 'not available'
#                 };
                
#                 // ========== PLUGINS & MIMETYPES ==========
#                 fp.plugins = {
#                     count: navigator.plugins.length,
#                     list: Array.from(navigator.plugins).map(p => ({
#                         name: p.name,
#                         description: p.description,
#                         filename: p.filename
#                     }))
#                 };
                
#                 fp.mimeTypes = {
#                     count: navigator.mimeTypes.length,
#                     list: Array.from(navigator.mimeTypes).map(m => m.type)
#                 };
                
#                 // ========== WEBGL FINGERPRINT ==========
#                 try {
#                     const canvas = document.createElement('canvas');
#                     const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
#                     if (gl) {
#                         const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
#                         fp.webgl = {
#                             vendor: gl.getParameter(gl.VENDOR),
#                             renderer: gl.getParameter(gl.RENDERER),
#                             version: gl.getParameter(gl.VERSION),
#                             shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
#                             unmaskedVendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'not available',
#                             unmaskedRenderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'not available'
#                         };
#                     } else {
#                         fp.webgl = { error: 'WebGL not available' };
#                     }
#                 } catch (e) {
#                     fp.webgl = { error: e.toString() };
#                 }
                
#                 // ========== CANVAS FINGERPRINT ==========
#                 try {
#                     const canvas = document.createElement('canvas');
#                     const ctx = canvas.getContext('2d');
#                     ctx.textBaseline = 'top';
#                     ctx.font = '14px Arial';
#                     ctx.textBaseline = 'alphabetic';
#                     ctx.fillStyle = '#f60';
#                     ctx.fillRect(125, 1, 62, 20);
#                     ctx.fillStyle = '#069';
#                     ctx.fillText('Canvas Fingerprint', 2, 15);
#                     ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
#                     ctx.fillText('Canvas Fingerprint', 4, 17);
#                     fp.canvasFingerprint = canvas.toDataURL().substring(0, 100) + '...';
#                 } catch (e) {
#                     fp.canvasFingerprint = { error: e.toString() };
#                 }
                
#                 // ========== AUDIO CONTEXT ==========
#                 try {
#                     const AudioContext = window.AudioContext || window.webkitAudioContext;
#                     if (AudioContext) {
#                         const context = new AudioContext();
#                         const oscillator = context.createOscillator();
#                         const analyser = context.createAnalyser();
#                         const gainNode = context.createGain();
#                         const scriptProcessor = context.createScriptProcessor(4096, 1, 1);
                        
#                         fp.audioContext = {
#                             state: context.state,
#                             sampleRate: context.sampleRate,
#                             maxChannelCount: context.destination.maxChannelCount,
#                             numberOfInputs: scriptProcessor.numberOfInputs,
#                             numberOfOutputs: scriptProcessor.numberOfOutputs,
#                             channelCount: analyser.channelCount
#                         };
                        
#                         context.close();
#                     } else {
#                         fp.audioContext = { error: 'AudioContext not available' };
#                     }
#                 } catch (e) {
#                     fp.audioContext = { error: e.toString() };
#                 }
                
#                 // ========== SCREEN PROPERTIES ==========
#                 fp.screen = {
#                     width: screen.width,
#                     height: screen.height,
#                     availWidth: screen.availWidth,
#                     availHeight: screen.availHeight,
#                     colorDepth: screen.colorDepth,
#                     pixelDepth: screen.pixelDepth,
#                     devicePixelRatio: window.devicePixelRatio,
#                     orientation: screen.orientation ? screen.orientation.type : 'not available'
#                 };
                
#                 // ========== WINDOW PROPERTIES ==========
#                 fp.window = {
#                     innerWidth: window.innerWidth,
#                     innerHeight: window.innerHeight,
#                     outerWidth: window.outerWidth,
#                     outerHeight: window.outerHeight,
#                     screenX: window.screenX,
#                     screenY: window.screenY
#                 };
                
#                 // ========== TIMEZONE & LOCALE ==========
#                 fp.timezone = {
#                     offset: new Date().getTimezoneOffset(),
#                     timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
#                     locale: Intl.DateTimeFormat().resolvedOptions().locale
#                 };
                
#                 // ========== CONNECTION INFO ==========
#                 if (navigator.connection) {
#                     fp.connection = {
#                         effectiveType: navigator.connection.effectiveType,
#                         downlink: navigator.connection.downlink,
#                         rtt: navigator.connection.rtt,
#                         saveData: navigator.connection.saveData
#                     };
#                 } else {
#                     fp.connection = { error: 'Connection API not available' };
#                 }
                
#                 // ========== AUTOMATION INDICATORS ==========
#                 fp.automationIndicators = {
#                     windowChrome: window.chrome !== undefined,
#                     chromeRuntimeId: window.chrome && window.chrome.runtime && window.chrome.runtime.id ? 'present' : 'absent',
#                     notificationPermissions: Notification.permission,
#                     documentHidden: document.hidden,
#                     documentVisibilityState: document.visibilityState
#                 };
                
#                 // ========== PROTOTYPE TAMPERING DETECTION ==========
#                 fp.prototypeTampering = {
#                     functionToStringModified: Function.prototype.toString.toString().includes('[native code]'),
#                     dateGetTimezoneOffset: Date.prototype.getTimezoneOffset.toString().includes('[native code]'),
#                     navigatorGetPropertyDescriptor: Object.getOwnPropertyDescriptor(Navigator.prototype, 'webdriver') !== undefined
#                 };
                
#                 // ========== PERFORMANCE TIMING ==========
#                 if (performance && performance.timing) {
#                     fp.performanceTiming = {
#                         navigationStart: performance.timing.navigationStart,
#                         loadEventEnd: performance.timing.loadEventEnd,
#                         domContentLoadedEventEnd: performance.timing.domContentLoadedEventEnd
#                     };
#                 }
                
#                 return fp;
#             }
#         """)
        
#         fingerprint = fingerprint_data
#         print_fingerprint_analysis(fingerprint)
#         return fingerprint
        
#     except Exception as e:
#         print(f"❌ Fingerprint extraction error: {e}")
#         return {}

# def print_fingerprint_analysis(fp):
#     """Print detailed analysis of fingerprint data"""
    
#     print("\n" + "🔴 CRITICAL BOT DETECTION SIGNALS".center(70, "="))
    
#     bot_signals = []
    
#     # Webdriver detection
#     if fp.get('webdriverDetection', {}).get('navigatorWebdriver') == True:
#         bot_signals.append("⚠️ navigator.webdriver = TRUE (MAJOR RED FLAG)")
    
#     if fp.get('webdriverDetection', {}).get('navigatorWebdriver') is not None:
#         bot_signals.append(f"⚠️ navigator.webdriver exists: {fp['webdriverDetection']['navigatorWebdriver']}")
    
#     # Chrome object detection
#     chrome_keys = fp.get('chromeDetection', {}).get('chromeKeys', [])
#     if not chrome_keys or len(chrome_keys) < 3:
#         bot_signals.append(f"⚠️ Incomplete chrome object (only {len(chrome_keys)} keys)")
    
#     # Plugin detection
#     plugin_count = fp.get('plugins', {}).get('count', 0)
#     if plugin_count == 0:
#         bot_signals.append("⚠️ NO PLUGINS detected (suspicious)")
    
#     # Permissions
#     notif_perm = fp.get('permissions', {}).get('notificationPermission')
#     if notif_perm == 'denied':
#         bot_signals.append("⚠️ Notification permission DENIED (automation indicator)")
    
#     # Display bot signals
#     if bot_signals:
#         print("\n🚨 BOT DETECTION SIGNALS FOUND:")
#         for signal in bot_signals:
#             print(f"  {signal}")
#     else:
#         print("\n✅ No obvious bot signals detected")
    
#     # Navigator details
#     print("\n" + "📱 NAVIGATOR PROPERTIES".center(70, "="))
#     nav = fp.get('navigator', {})
#     print(f"User Agent: {nav.get('userAgent', 'N/A')[:80]}...")
#     print(f"Platform: {nav.get('platform')}")
#     print(f"Languages: {nav.get('languages')}")
#     print(f"Hardware Concurrency: {nav.get('hardwareConcurrency')}")
#     print(f"Device Memory: {nav.get('deviceMemory')}")
#     print(f"Vendor: {nav.get('vendor')}")
#     print(f"Webdriver: {nav.get('webdriver')}")
#     print(f"PDF Viewer Enabled: {nav.get('pdfViewerEnabled')}")
    
#     # Webdriver detection
#     print("\n" + "🤖 WEBDRIVER DETECTION".center(70, "="))
#     wd = fp.get('webdriverDetection', {})
#     for key, value in wd.items():
#         status = "❌ DETECTED" if value not in [None, 'not present', False] else "✅ OK"
#         print(f"{status} | {key}: {value}")
    
#     # Chrome detection
#     print("\n" + "🌐 CHROME OBJECT ANALYSIS".center(70, "="))
#     chrome = fp.get('chromeDetection', {})
#     print(f"Chrome exists: {chrome.get('chromeExists')}")
#     print(f"Chrome runtime: {chrome.get('chromeRuntime')}")
#     print(f"Chrome keys: {chrome.get('chromeKeys')}")
    
#     # Plugins
#     print("\n" + "🔌 PLUGINS & MIMETYPES".center(70, "="))
#     plugins = fp.get('plugins', {})
#     print(f"Plugin count: {plugins.get('count')}")
#     if plugins.get('list'):
#         for p in plugins.get('list', [])[:3]:
#             print(f"  - {p.get('name')} ({p.get('filename')})")
    
#     # WebGL
#     print("\n" + "🎨 WEBGL FINGERPRINT".center(70, "="))
#     webgl = fp.get('webgl', {})
#     if 'error' not in webgl:
#         print(f"Vendor: {webgl.get('vendor')}")
#         print(f"Renderer: {webgl.get('renderer')}")
#         print(f"Unmasked Vendor: {webgl.get('unmaskedVendor')}")
#         print(f"Unmasked Renderer: {webgl.get('unmaskedRenderer')}")
#     else:
#         print(f"Error: {webgl.get('error')}")
    
#     # Screen
#     print("\n" + "📺 SCREEN PROPERTIES".center(70, "="))
#     screen = fp.get('screen', {})
#     print(f"Resolution: {screen.get('width')}x{screen.get('height')}")
#     print(f"Color Depth: {screen.get('colorDepth')}")
#     print(f"Device Pixel Ratio: {screen.get('devicePixelRatio')}")
    
#     # Timezone
#     print("\n" + "🌍 TIMEZONE & LOCALE".center(70, "="))
#     tz = fp.get('timezone', {})
#     print(f"Timezone: {tz.get('timezone')}")
#     print(f"Offset: {tz.get('offset')} minutes")
#     print(f"Locale: {tz.get('locale')}")
    
#     # Prototype tampering
#     print("\n" + "⚙️ PROTOTYPE TAMPERING DETECTION".center(70, "="))
#     proto = fp.get('prototypeTampering', {})
#     for key, value in proto.items():
#         status = "✅ OK" if value else "⚠️ MODIFIED"
#         print(f"{status} | {key}: {value}")
    
#     print("\n" + "="*70)

# def detect_skyscanner_specific_checks(page: Page):
#     """Detect Skyscanner-specific anti-bot checks"""
#     print("\n" + "🎯 SKYSCANNER-SPECIFIC DETECTION".center(70, "="))
    
#     try:
#         skyscanner_checks = page.evaluate("""
#             () => {
#                 const checks = {};
                
#                 // Check for common anti-bot scripts
#                 checks.scripts = Array.from(document.scripts).map(s => ({
#                     src: s.src,
#                     id: s.id,
#                     type: s.type
#                 })).filter(s => 
#                     s.src.includes('recaptcha') || 
#                     s.src.includes('captcha') || 
#                     s.src.includes('bot') ||
#                     s.src.includes('challenge') ||
#                     s.src.includes('px') ||
#                     s.src.includes('perimeterx') ||
#                     s.src.includes('datadome')
#                 );
                
#                 // Check for iframes (captcha, challenges)
#                 checks.iframes = Array.from(document.querySelectorAll('iframe')).map(i => ({
#                     src: i.src,
#                     title: i.title,
#                     id: i.id
#                 }));
                
#                 // Check for common anti-bot elements
#                 checks.suspiciousElements = {
#                     captcha: document.querySelector('[class*="captcha"]') !== null,
#                     challenge: document.querySelector('[class*="challenge"]') !== null,
#                     blocked: document.querySelector('[class*="blocked"]') !== null,
#                     robot: document.querySelector('[class*="robot"]') !== null
#                 };
                
#                 // Check cookies
#                 checks.cookies = document.cookie.split(';').map(c => c.trim().split('=')[0]);
                
#                 // Check localStorage
#                 checks.localStorage = Object.keys(localStorage);
                
#                 // Check sessionStorage
#                 checks.sessionStorage = Object.keys(sessionStorage);
                
#                 return checks;
#             }
#         """)
        
#         print("\n📜 LOADED SCRIPTS:")
#         if skyscanner_checks.get('scripts'):
#             for script in skyscanner_checks['scripts']:
#                 print(f"  ⚠️ Anti-bot script: {script['src']}")
#         else:
#             print("  ✅ No obvious anti-bot scripts detected")
        
#         print("\n🖼️ IFRAMES:")
#         if skyscanner_checks.get('iframes'):
#             for iframe in skyscanner_checks['iframes'][:5]:
#                 print(f"  - {iframe.get('title') or iframe.get('src', 'No source')[:50]}")
#         else:
#             print("  ✅ No iframes detected")
        
#         print("\n🚫 SUSPICIOUS ELEMENTS:")
#         for key, value in skyscanner_checks.get('suspiciousElements', {}).items():
#             status = "❌ DETECTED" if value else "✅ Not found"
#             print(f"  {status} | {key}")
        
#         print("\n🍪 COOKIES:")
#         cookies = skyscanner_checks.get('cookies', [])
#         print(f"  Total cookies: {len(cookies)}")
#         for cookie in cookies[:10]:
#             print(f"  - {cookie}")
        
#         return skyscanner_checks
        
#     except Exception as e:
#         print(f"❌ Skyscanner detection error: {e}")
#         return {}

# def save_fingerprint_to_file(fingerprint, skyscanner_checks):
#     """Save fingerprint data to JSON file"""
#     try:
#         timestamp = time.strftime("%Y%m%d_%H%M%S")
#         filename = f"fingerprint_analysis_{timestamp}.json"
        
#         data = {
#             "timestamp": timestamp,
#             "target_url": TARGET_URL,
#             "fingerprint": fingerprint,
#             "skyscanner_checks": skyscanner_checks
#         }
        
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(data, f, indent=2, ensure_ascii=False)
        
#         print(f"\n💾 Fingerprint saved to: {filename}")
        
#     except Exception as e:
#         print(f"⚠️ Could not save fingerprint: {e}")

# # ========== ORIGINAL FUNCTIONS ==========

# def parse_proxy_string(s: str):
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def test_proxy_connection(page: Page):
#     try:
#         print("🔍 Testing proxy connection...")
#         page.goto("https://httpbin.org/ip", timeout=15000, wait_until="domcontentloaded")
#         time.sleep(2)
#         ip_info = page.inner_text("body")
#         print(f"🌐 Current IP: {ip_info[:100]}...")
#         return True
#     except Exception as e:
#         print(f"⚠️ Proxy test failed: {e}")
#         return False

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     max_retries = 3
#     retry_delay = 5
    
#     for attempt in range(max_retries):
#         try:
#             print(f"🥷 Creating stealth profile: {profile_name} (Attempt {attempt + 1}/{max_retries})")
            
#             gl = GoLogin({"token": TOKEN})
            
#             if attempt > 0:
#                 wait_time = retry_delay * attempt
#                 print(f"⏳ Waiting {wait_time}s before retry...")
#                 time.sleep(wait_time)
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name,
#                 "webgl": {
#                     "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
#                     "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650/PCIe/SSE2", "Radeon RX 580"])
#                 },
#                 "audioContext": {
#                     "enable": True,
#                     "noise": random.uniform(0.0001, 0.0005)
#                 }
#             })
            
#             if not profile or 'id' not in profile:
#                 print(f"❌ Profile creation returned invalid data: {profile}")
#                 if attempt < max_retries - 1:
#                     continue
#                 return None
                
#             profile_id = profile['id']
#             print(f"✅ Profile created successfully: {profile_id}")
            
#             if proxy_config:
#                 try:
#                     proxy_data = {
#                         "mode": proxy_config['type'],
#                         "host": proxy_config['host'],
#                         "port": int(proxy_config['port']),
#                         "username": proxy_config.get('username', ''),
#                         "password": proxy_config.get('password', '')
#                     }
#                     gl.changeProfileProxy(profile_id, proxy_data)
#                     print(f"🔄 Proxy configured: {proxy_config['host']}")
#                 except Exception as proxy_error:
#                     print(f"⚠️ Proxy setup failed: {proxy_error}")
            
#             try:
#                 gl.updateUserAgentToLatestBrowser([profile_id])
#                 print("🔄 User agent updated to latest")
#             except Exception as ua_error:
#                 print(f"⚠️ User agent update failed: {ua_error}")
            
#             return profile_id
            
#         except Exception as e:
#             error_msg = str(e)
#             print(f"❌ Profile creation attempt {attempt + 1} failed: {error_msg}")
            
#             if "Connection aborted" in error_msg or "ConnectionResetError" in error_msg or "RemoteDisconnected" in error_msg:
#                 print("🌐 Network connection issue detected")
#                 if attempt < max_retries - 1:
#                     print(f"🔄 Retrying in {retry_delay}s...")
#                     time.sleep(retry_delay)
#                     continue
#             elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
#                 print("⏰ Timeout issue detected")
#                 if attempt < max_retries - 1:
#                     print(f"🔄 Retrying with longer timeout in {retry_delay}s...")
#                     time.sleep(retry_delay)
#                     continue
#             else:
#                 print(f"💥 Unexpected error: {error_msg}")
#                 if attempt < max_retries - 1:
#                     print(f"🔄 Retrying anyway in {retry_delay}s...")
#                     time.sleep(retry_delay)
#                     continue
    
#     print(f"❌ All {max_retries} profile creation attempts failed")
#     return None

# def start_maximum_stealth_browser(profile_id):
#     max_retries = 2
    
#     for attempt in range(max_retries):
#         try:
#             print(f"🚀 Starting stealth browser for: {profile_id} (Attempt {attempt + 1}/{max_retries})")
            
#             gl = GoLogin({
#                 "token": TOKEN,
#                 "profile_id": profile_id
#             })
            
#             debugger_address = gl.start()
#             print(f"🔌 Browser endpoint: {debugger_address}")
            
#             if not debugger_address:
#                 print("❌ No debugger address received")
#                 if attempt < max_retries - 1:
#                     continue
#                 return None, None, None, None
            
#             wait_time = random.uniform(3, 6)
#             print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             pw = sync_playwright().start()
#             cdp_url = f"http://{debugger_address}"
            
#             try:
#                 browser = pw.chromium.connect_over_cdp(cdp_url)
#             except Exception as connect_error:
#                 print(f"❌ Browser connection failed: {connect_error}")
#                 if attempt < max_retries - 1:
#                     print("🔄 Retrying browser connection...")
#                     gl.stop()
#                     pw.stop()
#                     time.sleep(3)
#                     continue
#                 return None, None, None, None
            
#             context = browser.contexts[0] if browser.contexts else browser.new_context()
            
#             if context.pages:
#                 page = context.pages[0]
#             else:
#                 page = context.new_page()
            
#             try:
#                 context.set_extra_http_headers({
#                     "DNT": "1",
#                     "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
#                 })
#             except Exception as header_error:
#                 print(f"⚠️ Header setup warning: {header_error}")
            
#             inject_ultimate_stealth(page)
            
#             return gl, pw, browser, page
            
#         except Exception as e:
#             print(f"❌ Browser start attempt {attempt + 1} failed: {e}")
#             if attempt < max_retries - 1:
#                 print("🔄 Retrying browser start...")
#                 time.sleep(3)
#                 continue
    
#     print(f"❌ All {max_retries} browser start attempts failed")
#     return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     try:
#         print("🛡️ Injecting stealth protection...")
        
#         page.add_init_script("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 if (parameter === 37446) return 'Intel Inc.';
#                 if (parameter === 37447) return 'Intel Iris OpenGL Engine';
#                 return originalGetParameter.call(this, parameter);
#             };
            
#             try {
#                 Date.prototype.getTimezoneOffset = () => -330;
#             } catch(e) {}
#         """)
        
#         print("✅ Stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def perform_light_interaction(page: Page):
#     try:
#         try:
#             scroll_distance = random.randint(10, 100)
#             page.evaluate(f"window.scrollBy(0, {scroll_distance});")
#             time.sleep(random.uniform(0.8, 1.5))
#         except:
#             pass
        
#         try:
#             page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#             time.sleep(random.uniform(0.3, 0.7))
#         except:
#             pass
        
#         try:
#             elements = page.locator("a, button").all()[:3]
#             if elements:
#                 random_element = random.choice(elements)
#                 if random_element.is_visible():
#                     random_element.hover()
#                     time.sleep(random.uniform(0.5, 1.2))
#                     print("🖱️ Performed hover interaction")
#         except:
#             pass
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def ultimate_human_browsing_with_fingerprint(page: Page):
#     """Human-like browsing with comprehensive fingerprint extraction"""
#     try:
#         print("🎭 Starting human behavior simulation with fingerprint analysis...")

#         # Navigate to target URL
#         print(f"🌐 Navigating to target URL: {TARGET_URL}")
        
#         success = False
        
#         # Try multiple loading strategies
#         strategies = [
#             ("networkidle", 45000),
#             ("domcontentloaded", 60000),
#             ("load", 90000),
#             (None, 120000)
#         ]
        
#         for i, (wait_strategy, timeout) in enumerate(strategies, 1):
#             try:
#                 if wait_strategy:
#                     print(f"📡 Attempt {i}: Using {wait_strategy} strategy...")
#                     page.goto(TARGET_URL, timeout=timeout, wait_until=wait_strategy)
#                 else:
#                     print(f"📡 Attempt {i}: No wait condition...")
#                     page.goto(TARGET_URL, timeout=timeout)
#                 print(f"✅ Successfully loaded target URL")
#                 success = True
#                 break
#             except Exception as e:
#                 print(f"⚠️ Strategy {i} failed: {e}")
        
#         if not success:
#             print("❌ All loading strategies failed")
#             return False
        
#         # Wait for page stabilization
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Page stabilization: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         # ========== EXTRACT COMPLETE FINGERPRINT ==========
#         fingerprint = extract_complete_fingerprint(page)
        
#         # ========== DETECT SKYSCANNER-SPECIFIC CHECKS ==========
#         skyscanner_checks = detect_skyscanner_specific_checks(page)
        
#         # Check page basics
#         try:
#             page.wait_for_selector("body", timeout=15000)
#             print("📄 Page body detected")
            
#             try:
#                 title = page.title()
#                 print(f"📰 Page title: {title[:50]}...")
#             except:
#                 print("📰 No title detected")
                
#             try:
#                 current_url = page.url
#                 print(f"🔗 Current URL: {current_url[:80]}...")
#             except:
#                 print("🔗 URL detection failed")
                
#         except TimeoutError:
#             print("⚠️ Body timeout, but continuing...")
        
#         # Scroll behavior
#         try:
#             print("📜 Starting scroll behavior...")
#             try:
#                 page_height = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight, window.innerHeight)")
#             except:
#                 page_height = page.evaluate("window.innerHeight") or 1000
                
#             print(f"📏 Page height: {page_height}px")
            
#             if page_height > 500:
#                 scroll_positions = [0, page_height * 0.25, page_height * 0.5, page_height * 0.75, page_height * 0.9]
#                 for i, pos in enumerate(scroll_positions):
#                     try:
#                         page.evaluate(f"window.scrollTo({{top: {int(pos)}, behavior: 'smooth'}});")
#                         print(f"📜 Scroll position {i+1}/5: {int(pos)}px")
#                         time.sleep(random.uniform(1.5, 3))
#                     except Exception as scroll_error:
#                         print(f"⚠️ Scroll {i+1} error: {scroll_error}")
#                         continue
#                 print("📜 Completed page scrolling")
#             else:
#                 try:
#                     page.evaluate("window.scrollBy({top: 200, behavior: 'smooth'});")
#                     time.sleep(1)
#                     print("📜 Simple scroll completed")
#                 except Exception as e:
#                     print(f"⚠️ Simple scroll error: {e}")
#         except Exception as e:
#             print(f"⚠️ Scroll setup error: {e}")
        
#         # Human-like behavior
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
#         start_time = time.time()
        
#         while time.time() - start_time < human_time:
#             action = random.choice(['scroll_small', 'mouse_move', 'pause'])
            
#             if action == 'scroll_small':
#                 scroll_distance = random.randint(50, 150)
#                 page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
#                 time.sleep(random.uniform(1, 2))
#             elif action == 'mouse_move':
#                 x = random.randint(100, 1200)
#                 y = random.randint(100, 800)
#                 page.mouse.move(x, y)
#                 time.sleep(random.uniform(0.5, 1))
#             elif action == 'pause':
#                 time.sleep(random.uniform(2, 4))
            
#             perform_light_interaction(page)
#             time.sleep(random.uniform(0.5, 1.5))
        
#         # ========== FINAL FINGERPRINT CHECK ==========
#         print("\n" + "🔍 FINAL FINGERPRINT CHECK AFTER INTERACTION".center(70, "="))
#         final_fingerprint = extract_complete_fingerprint(page)
        
#         # Save fingerprint to file
#         save_fingerprint_to_file(fingerprint, skyscanner_checks)
        
#         print("✅ Human behavior simulation complete with fingerprint analysis")
#         return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False

# def run_ultimate_stealth_test():
#     """Run the stealth test with fingerprint analysis"""
#     print("🎯 STEALTH MODE WITH FINGERPRINT ANALYSIS")
#     print("=" * 60)
    
#     successful_runs = 0
#     failed_profiles = 0
#     max_consecutive_failures = 5
#     consecutive_failures = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         if consecutive_failures >= max_consecutive_failures:
#             print(f"⚠️ Too many consecutive failures ({consecutive_failures}). Taking a longer break...")
#             time.sleep(30)
#             consecutive_failures = 0
        
#         profile_name = f"stealth_fp_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(3, 5)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     proxy_test = test_proxy_connection(page)
#                     if not proxy_test:
#                         print("⚠️ Proxy test failed, but continuing...")
                    
#                     # Use new function with fingerprint extraction
#                     success = ultimate_human_browsing_with_fingerprint(page)
                    
#                     if success:
#                         successful_runs += 1
#                         consecutive_failures = 0
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         failed_profiles += 1
#                         consecutive_failures += 1
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(15, 25)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 failed_profiles += 1
#                 consecutive_failures += 1
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             failed_profiles += 1
#             consecutive_failures += 1
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
        
#         pause_time = random.uniform(3, 6) if consecutive_failures == 0 else random.uniform(8, 12)
#         time.sleep(pause_time)
        
#         if profile_num % 10 == 0:
#             success_rate = (successful_runs / profile_num) * 100
#             print(f"\n📊 Progress Update - Completed: {profile_num}/{TOTAL_PROFILES}")
#             print(f"✅ Successful: {successful_runs} | ❌ Failed: {failed_profiles}")
#             print(f"📈 Current Success Rate: {success_rate:.1f}%")
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Final Results:")
#     print(f"✅ Successful: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")
#     print(f"❌ Failed: {failed_profiles}/{TOTAL_PROFILES} ({failed_profiles/TOTAL_PROFILES*100:.1f}%)")
    
#     if successful_runs > 0:
#         print(f"🎯 Target URL was successfully loaded {successful_runs} times!")
#         print(f"📁 Check fingerprint_analysis_*.json files for detailed analysis")
#     else:
#         print("😞 No successful runs. Check fingerprint files to identify issues.")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ FINGERPRINT ANALYSIS & DETECTION SCRIPT")
#     print("Target URL: https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc")
#     print("=" * 60)
#     print("\n📋 This script will:")
#     print("  1. Extract complete browser fingerprint")
#     print("  2. Detect bot signals (webdriver, chrome object, plugins, etc.)")
#     print("  3. Identify Skyscanner-specific anti-bot checks")
#     print("  4. Save detailed analysis to JSON files")
#     print("  5. Show exactly what websites see about your browser")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")



# import time
# import random
# import json
# import math
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc"
# TOKEN = "CHANGE_ME_TOKEN"
# TOTAL_PROFILES = 100
# PAGE_LOAD_PATIENCE = (8, 15)  # Increased for PerimeterX
# HUMAN_BEHAVIOR_TIME = (30, 60)  # Increased significantly

# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # ========== ADVANCED STEALTH INJECTION ==========

# def inject_ultimate_stealth_v2(page: Page):
#     """Advanced stealth injection - fixes all detection issues"""
#     try:
#         print("🛡️ Injecting ADVANCED stealth protection (v2)...")
        
#         page.add_init_script("""
#             // ========== FIX 1: COMPLETE CHROME OBJECT ==========
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: function() {}},
#                     onMessage: {addListener: function() {}},
#                     connect: function() {},
#                     sendMessage: function() {},
#                     PlatformOs: {
#                         MAC: "mac",
#                         WIN: "win",
#                         ANDROID: "android",
#                         CROS: "cros",
#                         LINUX: "linux",
#                         OPENBSD: "openbsd"
#                     },
#                     PlatformArch: {
#                         ARM: "arm",
#                         X86_32: "x86-32",
#                         X86_64: "x86-64"
#                     },
#                     PlatformNaclArch: {
#                         ARM: "arm",
#                         X86_32: "x86-32",
#                         X86_64: "x86-64"
#                     }
#                 },
#                 loadTimes: function() {
#                     return {
#                         requestTime: Date.now() / 1000 - Math.random() * 2,
#                         startLoadTime: Date.now() / 1000 - Math.random() * 1.5,
#                         commitLoadTime: Date.now() / 1000 - Math.random() * 1,
#                         finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 0.5,
#                         finishLoadTime: Date.now() / 1000 - Math.random() * 0.3,
#                         firstPaintTime: Date.now() / 1000 - Math.random() * 0.2,
#                         firstPaintAfterLoadTime: 0,
#                         navigationType: "Other",
#                         wasFetchedViaSpdy: false,
#                         wasNpnNegotiated: true,
#                         npnNegotiatedProtocol: "h2",
#                         wasAlternateProtocolAvailable: false,
#                         connectionInfo: "h2"
#                     };
#                 },
#                 csi: function() {
#                     return {
#                         startE: Date.now() - Math.random() * 3000,
#                         onloadT: Date.now() - Math.random() * 1000,
#                         pageT: Math.random() * 2000,
#                         tran: 15
#                     };
#                 },
#                 app: {
#                     isInstalled: false,
#                     InstallState: {
#                         DISABLED: 'disabled',
#                         INSTALLED: 'installed',
#                         NOT_INSTALLED: 'not_installed'
#                     },
#                     RunningState: {
#                         CANNOT_RUN: 'cannot_run',
#                         READY_TO_RUN: 'ready_to_run',
#                         RUNNING: 'running'
#                     },
#                     getDetails: function() {},
#                     getIsInstalled: function() {},
#                     installState: function() {},
#                     runningState: function() {}
#                 }
#             };
            
#             // ========== FIX 2: MULTIPLE PLUGINS ==========
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => {
#                     const plugins = [
#                         {
#                             description: "Portable Document Format",
#                             filename: "internal-pdf-viewer",
#                             name: "Chrome PDF Plugin",
#                             length: 2,
#                             item: function(index) { return this[index]; },
#                             namedItem: function(name) { return this[name]; }
#                         },
#                         {
#                             description: "Chromium PDF Plugin",
#                             filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
#                             name: "Chrome PDF Viewer",
#                             length: 1,
#                             item: function(index) { return this[index]; },
#                             namedItem: function(name) { return this[name]; }
#                         },
#                         {
#                             description: "Native Client",
#                             filename: "internal-nacl-plugin",
#                             name: "Native Client",
#                             length: 2,
#                             item: function(index) { return this[index]; },
#                             namedItem: function(name) { return this[name]; }
#                         }
#                     ];
                    
#                     plugins.item = function(index) { return this[index]; };
#                     plugins.namedItem = function(name) { 
#                         return this.find(p => p.name === name); 
#                     };
#                     plugins.refresh = function() {};
                    
#                     return plugins;
#                 }
#             });
            
#             // ========== FIX 3: REMOVE WEBDRIVER ==========
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined
#             });
#             delete window.webdriver;
#             delete navigator.webdriver;
            
#             // ========== FIX 4: REALISTIC LANGUAGES ==========
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en']
#             });
            
#             Object.defineProperty(navigator, 'language', {
#                 get: () => 'en-US'
#             });
            
#             // ========== FIX 5: PERMISSIONS API ==========
#             const originalQuery = window.navigator.permissions.query;
#             window.navigator.permissions.query = (parameters) => (
#                 parameters.name === 'notifications' ?
#                     Promise.resolve({ state: Notification.permission }) :
#                     originalQuery(parameters)
#             );
            
#             // ========== FIX 6: WEBGL - NO TAMPERING, USE NATURAL ==========
#             // Remove WebGL tampering to avoid detection
            
#             // ========== FIX 7: REMOVE PROTOTYPE TAMPERING ==========
#             // DO NOT modify Date.prototype.getTimezoneOffset
#             // Let GoLogin handle timezone naturally
            
#             // ========== FIX 8: IFRAME CONTENT WINDOW ==========
#             Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
#                 get: function() {
#                     return window;
#                 }
#             });
            
#             // ========== FIX 9: MEDIA DEVICES ==========
#             if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
#                 const originalEnumerate = navigator.mediaDevices.enumerateDevices;
#                 navigator.mediaDevices.enumerateDevices = function() {
#                     return originalEnumerate.call(this).then(devices => {
#                         return devices.map(device => ({
#                             deviceId: device.deviceId,
#                             kind: device.kind,
#                             label: device.label,
#                             groupId: device.groupId,
#                             toJSON: function() { return this; }
#                         }));
#                     });
#                 };
#             }
            
#             // ========== FIX 10: BATTERY API ==========
#             if (navigator.getBattery) {
#                 const originalGetBattery = navigator.getBattery;
#                 navigator.getBattery = function() {
#                     return originalGetBattery.call(this).then(battery => {
#                         Object.defineProperty(battery, 'charging', { value: true });
#                         Object.defineProperty(battery, 'chargingTime', { value: 0 });
#                         Object.defineProperty(battery, 'dischargingTime', { value: Infinity });
#                         Object.defineProperty(battery, 'level', { value: 1 });
#                         return battery;
#                     });
#                 };
#             }
            
#             // ========== FIX 11: CONNECTION API ==========
#             if (navigator.connection) {
#                 Object.defineProperty(navigator.connection, 'rtt', {
#                     get: () => Math.floor(Math.random() * 50) + 50
#                 });
#             }
            
#             // ========== FIX 12: NOTIFICATION PERMISSIONS ==========
#             const originalNotificationPermission = Notification.permission;
#             Object.defineProperty(Notification, 'permission', {
#                 get: () => 'default'
#             });
            
#             // ========== FIX 13: SCREEN CONSISTENCY ==========
#             Object.defineProperty(screen, 'availTop', { value: 0 });
#             Object.defineProperty(screen, 'availLeft', { value: 0 });
            
#             // ========== FIX 14: MOUSE EVENTS - Add realistic properties ==========
#             const originalMouseEvent = window.MouseEvent;
#             window.MouseEvent = function(type, eventInitDict) {
#                 const event = new originalMouseEvent(type, eventInitDict);
#                 if (eventInitDict && typeof eventInitDict.pageX === 'undefined') {
#                     Object.defineProperty(event, 'pageX', { value: eventInitDict.clientX || 0 });
#                     Object.defineProperty(event, 'pageY', { value: eventInitDict.clientY || 0 });
#                 }
#                 return event;
#             };
            
#             console.log('🛡️ Advanced Stealth Protection Active - All fixes applied');
#         """)
        
#         print("✅ Advanced stealth v2 protection active - All 14 fixes applied!")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# # ========== ADVANCED HUMAN BEHAVIOR ==========

# def advanced_mouse_movement(page: Page, duration: float = 2.0):
#     """Realistic mouse movement using bezier curves"""
#     try:
#         # Get current viewport
#         viewport = page.viewport_size
#         max_x = viewport['width'] if viewport else 1200
#         max_y = viewport['height'] if viewport else 800
        
#         # Random start and end points
#         start_x = random.randint(100, max_x - 100)
#         start_y = random.randint(100, max_y - 100)
#         end_x = random.randint(100, max_x - 100)
#         end_y = random.randint(100, max_y - 100)
        
#         # Bezier curve control points
#         cp1_x = random.randint(min(start_x, end_x), max(start_x, end_x))
#         cp1_y = random.randint(min(start_y, end_y), max(start_y, end_y))
#         cp2_x = random.randint(min(start_x, end_x), max(start_x, end_x))
#         cp2_y = random.randint(min(start_y, end_y), max(start_y, end_y))
        
#         steps = random.randint(25, 40)
        
#         for i in range(steps):
#             t = i / steps
#             # Cubic bezier curve formula
#             x = (1-t)**3 * start_x + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * end_x
#             y = (1-t)**3 * start_y + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * end_y
            
#             page.mouse.move(x, y)
#             time.sleep(duration / steps + random.uniform(0, 0.01))
        
#         print(f"🖱️ Bezier curve mouse movement completed")
        
#     except Exception as e:
#         print(f"⚠️ Mouse movement error: {e}")

# def realistic_scroll_pattern(page: Page):
#     """Realistic scrolling with pauses and variations"""
#     try:
#         # Get page height
#         try:
#             page_height = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
#         except:
#             page_height = 2000
        
#         current_position = 0
        
#         while current_position < page_height * 0.8:
#             # Random scroll distance
#             scroll_amount = random.randint(80, 250)
            
#             # Scroll with easing
#             page.evaluate(f"""
#                 window.scrollTo({{
#                     top: window.scrollY + {scroll_amount},
#                     behavior: 'smooth'
#                 }});
#             """)
            
#             current_position += scroll_amount
            
#             # Random pause (reading time)
#             pause = random.uniform(1.5, 4.5)
#             time.sleep(pause)
            
#             # Sometimes scroll back up a bit (natural behavior)
#             if random.random() < 0.2:
#                 back_scroll = random.randint(30, 80)
#                 page.evaluate(f"""
#                     window.scrollTo({{
#                         top: window.scrollY - {back_scroll},
#                         behavior: 'smooth'
#                     }});
#                 """)
#                 time.sleep(random.uniform(0.5, 1.5))
#                 current_position -= back_scroll
        
#         print("📜 Realistic scroll pattern completed")
        
#     except Exception as e:
#         print(f"⚠️ Scroll pattern error: {e}")

# def random_interactions(page: Page):
#     """Random realistic interactions"""
#     try:
#         actions = [
#             'hover_element',
#             'click_safe',
#             'double_move',
#             'pause_reading'
#         ]
        
#         action = random.choice(actions)
        
#         if action == 'hover_element':
#             try:
#                 elements = page.locator("a, button, div[role='button']").all()[:5]
#                 if elements:
#                     elem = random.choice(elements)
#                     if elem.is_visible():
#                         # Move mouse to element with curve
#                         box = elem.bounding_box()
#                         if box:
#                             target_x = box['x'] + box['width'] / 2
#                             target_y = box['y'] + box['height'] / 2
#                             page.mouse.move(target_x, target_y)
#                             time.sleep(random.uniform(0.5, 1.5))
#                             print("🖱️ Hovered over element")
#             except:
#                 pass
        
#         elif action == 'click_safe':
#             # Click on empty space (safe click)
#             try:
#                 viewport = page.viewport_size
#                 safe_x = random.randint(50, (viewport['width'] if viewport else 800) - 50)
#                 safe_y = random.randint(50, (viewport['height'] if viewport else 600) - 50)
#                 page.mouse.click(safe_x, safe_y)
#                 time.sleep(random.uniform(0.3, 0.8))
#                 print("🖱️ Safe click performed")
#             except:
#                 pass
        
#         elif action == 'double_move':
#             advanced_mouse_movement(page, duration=random.uniform(1.5, 3.0))
        
#         elif action == 'pause_reading':
#             # Simulate reading
#             time.sleep(random.uniform(3, 7))
#             print("📖 Reading pause")
        
#     except Exception as e:
#         print(f"⚠️ Interaction error: {e}")

# # ========== FINGERPRINT DETECTION ==========

# def extract_complete_fingerprint(page: Page):
#     """Extract complete browser fingerprint"""
#     print("\n" + "="*70)
#     print("🔍 EXTRACTING COMPLETE FINGERPRINT")
#     print("="*70)
    
#     fingerprint = {}
    
#     try:
#         fingerprint_data = page.evaluate("""
#             () => {
#                 const fp = {};
                
#                 fp.navigator = {
#                     userAgent: navigator.userAgent,
#                     platform: navigator.platform,
#                     language: navigator.language,
#                     languages: navigator.languages,
#                     hardwareConcurrency: navigator.hardwareConcurrency,
#                     deviceMemory: navigator.deviceMemory || 'not available',
#                     maxTouchPoints: navigator.maxTouchPoints,
#                     vendor: navigator.vendor,
#                     webdriver: navigator.webdriver,
#                     pdfViewerEnabled: navigator.pdfViewerEnabled || false
#                 };
                
#                 fp.webdriverDetection = {
#                     navigatorWebdriver: navigator.webdriver,
#                     windowWebdriver: window.webdriver,
#                     navigatorWebdriverType: typeof navigator.webdriver
#                 };
                
#                 fp.chromeDetection = {
#                     chromeExists: !!window.chrome,
#                     chromeRuntime: window.chrome && window.chrome.runtime ? 'present' : 'not present',
#                     chromeKeys: window.chrome ? Object.keys(window.chrome) : []
#                 };
                
#                 fp.permissions = {
#                     notificationPermission: Notification.permission || 'not available'
#                 };
                
#                 fp.plugins = {
#                     count: navigator.plugins.length,
#                     list: Array.from(navigator.plugins).map(p => ({
#                         name: p.name,
#                         description: p.description,
#                         filename: p.filename
#                     }))
#                 };
                
#                 fp.mimeTypes = {
#                     count: navigator.mimeTypes.length,
#                     list: Array.from(navigator.mimeTypes).map(m => m.type)
#                 };
                
#                 try {
#                     const canvas = document.createElement('canvas');
#                     const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
#                     if (gl) {
#                         const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
#                         fp.webgl = {
#                             vendor: gl.getParameter(gl.VENDOR),
#                             renderer: gl.getParameter(gl.RENDERER),
#                             unmaskedVendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'not available',
#                             unmaskedRenderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'not available'
#                         };
#                     } else {
#                         fp.webgl = { error: 'WebGL not available' };
#                     }
#                 } catch (e) {
#                     fp.webgl = { error: e.toString() };
#                 }
                
#                 fp.screen = {
#                     width: screen.width,
#                     height: screen.height,
#                     colorDepth: screen.colorDepth,
#                     devicePixelRatio: window.devicePixelRatio
#                 };
                
#                 fp.timezone = {
#                     offset: new Date().getTimezoneOffset(),
#                     timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
#                 };
                
#                 fp.prototypeTampering = {
#                     dateGetTimezoneOffset: Date.prototype.getTimezoneOffset.toString().includes('[native code]')
#                 };
                
#                 return fp;
#             }
#         """)
        
#         fingerprint = fingerprint_data
#         print_fingerprint_analysis(fingerprint)
#         return fingerprint
        
#     except Exception as e:
#         print(f"❌ Fingerprint extraction error: {e}")
#         return {}

# def print_fingerprint_analysis(fp):
#     """Print analysis"""
#     print("\n" + "🔴 CRITICAL BOT DETECTION SIGNALS".center(70, "="))
    
#     bot_signals = []
    
#     if fp.get('webdriverDetection', {}).get('navigatorWebdriver') is not None:
#         if fp['webdriverDetection']['navigatorWebdriver'] == True:
#             bot_signals.append("⚠️ navigator.webdriver = TRUE (MAJOR RED FLAG)")
#         else:
#             bot_signals.append(f"⚠️ navigator.webdriver exists: {fp['webdriverDetection']['navigatorWebdriver']}")
    
#     chrome_keys = fp.get('chromeDetection', {}).get('chromeKeys', [])
#     if len(chrome_keys) < 3:
#         bot_signals.append(f"⚠️ Incomplete chrome object ({len(chrome_keys)} keys)")
    
#     plugin_count = fp.get('plugins', {}).get('count', 0)
#     if plugin_count < 2:
#         bot_signals.append(f"⚠️ Insufficient plugins ({plugin_count})")
    
#     if not fp.get('prototypeTampering', {}).get('dateGetTimezoneOffset', True):
#         bot_signals.append("⚠️ Date prototype TAMPERED")
    
#     if bot_signals:
#         print("\n🚨 BOT DETECTION SIGNALS FOUND:")
#         for signal in bot_signals:
#             print(f"  {signal}")
#     else:
#         print("\n✅ No obvious bot signals detected")
    
#     print("\n" + "📱 NAVIGATOR".center(70, "="))
#     nav = fp.get('navigator', {})
#     print(f"Webdriver: {nav.get('webdriver')}")
#     print(f"Languages: {nav.get('languages')}")
    
#     print("\n" + "🌐 CHROME OBJECT".center(70, "="))
#     chrome = fp.get('chromeDetection', {})
#     print(f"Chrome keys ({len(chrome.get('chromeKeys', []))}): {chrome.get('chromeKeys')}")
    
#     print("\n" + "🔌 PLUGINS".center(70, "="))
#     plugins = fp.get('plugins', {})
#     print(f"Plugin count: {plugins.get('count')}")
    
#     print("\n" + "⚙️ PROTOTYPE".center(70, "="))
#     proto = fp.get('prototypeTampering', {})
#     print(f"Date.getTimezoneOffset native: {proto.get('dateGetTimezoneOffset')}")
    
#     print("\n" + "="*70)

# def detect_skyscanner_checks(page: Page):
#     """Detect Skyscanner anti-bot"""
#     print("\n" + "🎯 SKYSCANNER DETECTION".center(70, "="))
    
#     try:
#         checks = page.evaluate("""
#             () => {
#                 const c = {};
#                 c.scripts = Array.from(document.scripts)
#                     .map(s => s.src)
#                     .filter(s => s.includes('captcha') || s.includes('px') || s.includes('perimeterx'));
#                 c.isCaptchaPage = window.location.href.includes('captcha');
#                 c.currentUrl = window.location.href;
#                 return c;
#             }
#         """)
        
#         if checks.get('isCaptchaPage'):
#             print("  ❌ CAPTCHA PAGE DETECTED!")
#         else:
#             print("  ✅ Not on captcha page")
        
#         if checks.get('scripts'):
#             print(f"  ⚠️ Anti-bot scripts found: {len(checks['scripts'])}")
#         else:
#             print("  ✅ No anti-bot scripts detected")
        
#         print(f"  🔗 URL: {checks.get('currentUrl', 'N/A')[:80]}...")
        
#         return checks
        
#     except Exception as e:
#         print(f"❌ Detection error: {e}")
#         return {}

# def save_fingerprint_to_file(fingerprint, checks):
#     """Save to JSON"""
#     try:
#         timestamp = time.strftime("%Y%m%d_%H%M%S")
#         filename = f"fingerprint_{timestamp}.json"
        
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump({
#                 "timestamp": timestamp,
#                 "fingerprint": fingerprint,
#                 "checks": checks
#             }, f, indent=2)
        
#         print(f"\n💾 Saved: {filename}")
#     except Exception as e:
#         print(f"⚠️ Save error: {e}")

# # ========== CORE FUNCTIONS ==========

# def parse_proxy_string(s: str):
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def test_proxy_connection(page: Page):
#     try:
#         print("🔍 Testing proxy...")
#         page.goto("https://httpbin.org/ip", timeout=15000, wait_until="domcontentloaded")
#         time.sleep(2)
#         ip_info = page.inner_text("body")
#         print(f"🌐 IP: {ip_info[:50]}...")
#         return True
#     except Exception as e:
#         print(f"⚠️ Proxy test failed: {e}")
#         return False

# def create_stealth_profile(profile_name, proxy_config=None):
#     max_retries = 3
    
#     for attempt in range(max_retries):
#         try:
#             print(f"🥷 Creating profile: {profile_name} (Attempt {attempt + 1})")
            
#             gl = GoLogin({"token": TOKEN})
            
#             if attempt > 0:
#                 time.sleep(5 * attempt)
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name,
#                 "webgl": {
#                     "mode": "noise",
#                     "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation"]),
#                     "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650"])
#                 },
#                 "audioContext": {
#                     "mode": "noise",
#                     "noise": random.uniform(0.0001, 0.0005)
#                 },
#                 "canvas": {
#                     "mode": "noise"
#                 },
#                 "timezone": {
#                     "enabled": True,
#                     "fillBasedOnIp": True
#                 }
#             })
            
#             if not profile or 'id' not in profile:
#                 if attempt < max_retries - 1:
#                     continue
#                 return None
                
#             profile_id = profile['id']
#             print(f"✅ Profile created: {profile_id}")
            
#             if proxy_config:
#                 try:
#                     gl.changeProfileProxy(profile_id, {
#                         "mode": proxy_config['type'],
#                         "host": proxy_config['host'],
#                         "port": int(proxy_config['port']),
#                         "username": proxy_config.get('username', ''),
#                         "password": proxy_config.get('password', '')
#                     })
#                     print(f"🔄 Proxy configured")
#                 except Exception as e:
#                     print(f"⚠️ Proxy setup failed: {e}")
            
#             try:
#                 gl.updateUserAgentToLatestBrowser([profile_id])
#                 print("🔄 User agent updated")
#             except:
#                 pass
            
#             return profile_id
            
#         except Exception as e:
#             print(f"❌ Attempt {attempt + 1} failed: {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(5)
    
#     return None

# def start_stealth_browser(profile_id):
#     max_retries = 2
    
#     for attempt in range(max_retries):
#         try:
#             print(f"🚀 Starting browser (Attempt {attempt + 1})")
            
#             gl = GoLogin({"token": TOKEN, "profile_id": profile_id})
#             debugger_address = gl.start()
            
#             if not debugger_address:
#                 if attempt < max_retries - 1:
#                     continue
#                 return None, None, None, None
            
#             print(f"🔌 Browser endpoint: {debugger_address}")
#             time.sleep(random.uniform(4, 7))
            
#             pw = sync_playwright().start()
#             browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
            
#             context = browser.contexts[0] if browser.contexts else browser.new_context()
#             page = context.pages[0] if context.pages else context.new_page()
            
#             context.set_extra_http_headers({
#                 "DNT": "1",
#                 "Accept-Language": "en-US,en;q=0.9",
#                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#                 "Sec-Fetch-Dest": "document",
#                 "Sec-Fetch-Mode": "navigate",
#                 "Sec-Fetch-Site": "none",
#                 "Upgrade-Insecure-Requests": "1"
#             })
            
#             inject_ultimate_stealth_v2(page)
            
#             return gl, pw, browser, page
            
#         except Exception as e:
#             print(f"❌ Browser start failed: {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(3)
    
#     return None, None, None, None

# def ultimate_human_browsing(page: Page):
#     """Advanced human browsing with PerimeterX bypass techniques"""
#     try:
#         print("🎭 Starting ADVANCED human behavior simulation...")

#         # Navigate to target
#         print(f"🌐 Navigating to: {TARGET_URL}")
        
#         success = False
#         strategies = [
#             ("domcontentloaded", 90000),
#             ("load", 120000),
#             (None, 150000)
#         ]
        
#         for i, (wait_strategy, timeout) in enumerate(strategies, 1):
#             try:
#                 print(f"📡 Loading strategy {i}...")
#                 if wait_strategy:
#                     page.goto(TARGET_URL, timeout=timeout, wait_until=wait_strategy)
#                 else:
#                     page.goto(TARGET_URL, timeout=timeout)
#                 print(f"✅ Page loaded successfully")
#                 success = True
#                 break
#             except Exception as e:
#                 print(f"⚠️ Strategy {i} failed: {str(e)[:80]}")
        
#         if not success:
#             print("❌ All loading strategies failed")
#             return False
        
#         # CRITICAL: Long stabilization for PerimeterX analysis
#         stabilization = random.uniform(10, 15)
#         print(f"⏳ Page stabilization (PerimeterX analysis): {stabilization:.1f}s")
#         time.sleep(stabilization)
        
#         # Extract fingerprint
#         fingerprint = extract_complete_fingerprint(page)
        
#         # Detect Skyscanner checks
#         checks = detect_skyscanner_checks(page)
        
#         # Check if we're on captcha page
#         try:
#             current_url = page.url
#             if 'captcha' in current_url.lower():
#                 print("⚠️ WARNING: Redirected to CAPTCHA page!")
#                 print(f"   URL: {current_url}")
#             else:
#                 print(f"✅ On target page: {current_url[:60]}...")
#         except:
#             pass
        
#         # Page basics
#         try:
#             page.wait_for_selector("body", timeout=15000)
#             title = page.title()
#             print(f"📰 Title: {title[:50]}...")
#         except:
#             print("⚠️ Could not get page title")
        
#         # PHASE 1: Initial observation (simulate user reading)
#         print("\n📖 PHASE 1: Initial page observation")
#         observation_time = random.uniform(8, 15)
#         print(f"   Reading page for {observation_time:.1f}s...")
        
#         # Subtle mouse movements during reading
#         for _ in range(3):
#             advanced_mouse_movement(page, duration=random.uniform(2, 4))
#             time.sleep(random.uniform(2, 4))
        
#         # PHASE 2: Realistic scrolling
#         print("\n📜 PHASE 2: Realistic scroll pattern")
#         realistic_scroll_pattern(page)
        
#         # PHASE 3: Interactive exploration
#         print("\n🖱️ PHASE 3: Interactive exploration")
#         interaction_time = random.uniform(20, 40)
#         start_time = time.time()
        
#         interaction_count = 0
#         while time.time() - start_time < interaction_time:
#             # Random realistic actions
#             action_choice = random.random()
            
#             if action_choice < 0.3:
#                 # Advanced mouse movement
#                 advanced_mouse_movement(page, duration=random.uniform(1.5, 3.5))
#                 interaction_count += 1
#             elif action_choice < 0.5:
#                 # Scroll a bit
#                 scroll_amount = random.randint(100, 300)
#                 direction = random.choice(['down', 'up'])
#                 if direction == 'down':
#                     page.evaluate(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}})")
#                 else:
#                     page.evaluate(f"window.scrollBy({{top: -{scroll_amount}, behavior: 'smooth'}})")
#                 time.sleep(random.uniform(1.5, 3))
#                 interaction_count += 1
#             elif action_choice < 0.7:
#                 # Random interactions
#                 random_interactions(page)
#                 interaction_count += 1
#             else:
#                 # Reading pause
#                 pause = random.uniform(3, 6)
#                 print(f"   📖 Reading pause: {pause:.1f}s")
#                 time.sleep(pause)
            
#             # Small random delay between actions
#             time.sleep(random.uniform(0.5, 2))
        
#         print(f"   ✅ Completed {interaction_count} interactions")
        
#         # PHASE 4: Final scroll to bottom
#         print("\n📜 PHASE 4: Final exploration")
#         try:
#             page_height = page.evaluate("document.body.scrollHeight")
#             page.evaluate(f"window.scrollTo({{top: {page_height * 0.9}, behavior: 'smooth'}})")
#             time.sleep(random.uniform(3, 5))
#             print("   ✅ Scrolled to bottom")
#         except:
#             pass
        
#         # Final fingerprint check
#         print("\n🔍 FINAL FINGERPRINT CHECK")
#         final_fp = extract_complete_fingerprint(page)
        
#         # Final Skyscanner check
#         final_checks = detect_skyscanner_checks(page)
        
#         # Save data
#         save_fingerprint_to_file(fingerprint, checks)
        
#         print("\n✅ Advanced human behavior simulation COMPLETE")
        
#         # Check if we ended on captcha
#         try:
#             final_url = page.url
#             if 'captcha' in final_url.lower():
#                 print("❌ RESULT: Still on CAPTCHA page - Detection occurred")
#                 return False
#             else:
#                 print("✅ RESULT: Successfully bypassed detection!")
#                 return True
#         except:
#             return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False

# def run_stealth_test():
#     """Main test runner"""
#     print("🎯 ULTIMATE STEALTH TEST - PERIMETERX BYPASS")
#     print("=" * 70)
    
#     successful_runs = 0
#     failed_profiles = 0
#     captcha_hits = 0
#     max_consecutive_failures = 5
#     consecutive_failures = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n{'='*70}")
#         print(f"🚀 PROFILE {profile_num}/{TOTAL_PROFILES}")
#         print(f"{'='*70}")
        
#         if consecutive_failures >= max_consecutive_failures:
#             print(f"⚠️ Too many failures. Taking 30s break...")
#             time.sleep(30)
#             consecutive_failures = 0
        
#         profile_name = f"stealth_v2_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             time.sleep(random.uniform(3, 6))
            
#             gl, pw, browser, page = start_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     # Test proxy
#                     test_proxy_connection(page)
                    
#                     # Run advanced behavior
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         consecutive_failures = 0
#                         print(f"\n🎉 ✅ PROFILE {profile_num} - SUCCESS!")
#                     else:
#                         failed_profiles += 1
#                         captcha_hits += 1
#                         consecutive_failures += 1
#                         print(f"\n❌ PROFILE {profile_num} - FAILED (Captcha)")
                    
#                     # Extra session time
#                     session_time = random.uniform(10, 20)
#                     print(f"🕐 Session cooldown: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 failed_profiles += 1
#                 consecutive_failures += 1
#                 print(f"❌ PROFILE {profile_num} - BROWSER FAILED")
#         else:
#             failed_profiles += 1
#             consecutive_failures += 1
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
        
#         # Pause between profiles
#         pause = random.uniform(5, 10) if consecutive_failures == 0 else random.uniform(10, 15)
#         print(f"⏸️ Pause before next profile: {pause:.1f}s")
#         time.sleep(pause)
        
#         # Progress report every 5 profiles
#         if profile_num % 5 == 0:
#             success_rate = (successful_runs / profile_num) * 100
#             print(f"\n{'='*70}")
#             print(f"📊 PROGRESS REPORT - {profile_num}/{TOTAL_PROFILES}")
#             print(f"{'='*70}")
#             print(f"✅ Successful: {successful_runs}")
#             print(f"❌ Failed: {failed_profiles}")
#             print(f"🚫 Captcha hits: {captcha_hits}")
#             print(f"📈 Success rate: {success_rate:.1f}%")
#             print(f"{'='*70}\n")
    
#     # Final results
#     print(f"\n{'='*70}")
#     print(f"🏆 FINAL RESULTS")
#     print(f"{'='*70}")
#     print(f"✅ Successful: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")
#     print(f"❌ Failed: {failed_profiles}/{TOTAL_PROFILES} ({failed_profiles/TOTAL_PROFILES*100:.1f}%)")
#     print(f"🚫 Captcha hits: {captcha_hits}")
#     print(f"{'='*70}")
    
#     if successful_runs > 0:
#         print(f"\n🎯 Successfully bypassed PerimeterX {successful_runs} times!")
#         print(f"📁 Check fingerprint_*.json files for analysis")
#     else:
#         print("\n😞 No successful bypasses. Review fingerprint files.")
    
#     print(f"\n💡 Tips for improvement:")
#     print(f"   - Use residential proxies from target country")
#     print(f"   - Increase HUMAN_BEHAVIOR_TIME to 60-120s")
#     print(f"   - Add more realistic mouse patterns")
#     print(f"   - Use real device fingerprints")

# def cleanup_browser(gl, pw, browser):
#     """Cleanup resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser cleaned up")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("\n" + "="*70)
#     print("🛡️ ULTIMATE STEALTH SCRIPT v2.0 - PERIMETERX BYPASS")
#     print("="*70)
#     print(f"\n📋 Configuration:")
#     print(f"   Target: {TARGET_URL}")
#     print(f"   Profiles: {TOTAL_PROFILES}")
#     print(f"   Behavior time: {HUMAN_BEHAVIOR_TIME[0]}-{HUMAN_BEHAVIOR_TIME[1]}s")
#     print(f"   Proxy: {'Enabled' if PROXY_LIST else 'Disabled'}")
#     print("\n🔧 Features:")
#     print("   ✅ Complete Chrome object (4+ keys)")
#     print("   ✅ Multiple plugins (3)")
#     print("   ✅ No prototype tampering")
#     print("   ✅ Realistic mouse movements (Bezier curves)")
#     print("   ✅ Advanced scroll patterns")
#     print("   ✅ Interactive exploration")
#     print("   ✅ PerimeterX bypass techniques")
#     print("   ✅ Fingerprint analysis & export")
#     print("="*70 + "\n")
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_stealth_test()
#     except KeyboardInterrupt:
#         print("\n\n🛑 Test interrupted by user")
#     except Exception as e:
#         print(f"\n❌ Fatal error: {e}")
#         import traceback
#         traceback.print_exc()



# import time
# import random
# import json
# import math
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc"
# TOKEN = "CHANGE_ME_TOKEN"
# TOTAL_PROFILES = 100
# PAGE_LOAD_PATIENCE = (15, 30)  # Increased for better handling
# HUMAN_BEHAVIOR_TIME = (30, 60)  # Kept as is

# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
#     "socks5 us.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-us:another-uuid-here",  # Added fallback proxy
# ]

# # ========== ADVANCED STEALTH INJECTION ==========

# def inject_ultimate_stealth_v2(page: Page):
#     """Advanced stealth injection - fixes all detection issues"""
#     try:
#         print("🛡️ Injecting ADVANCED stealth protection (v2)...")
        
#         page.add_init_script("""
#             // ========== FIX 1: COMPLETE CHROME OBJECT ==========
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: function() {}},
#                     onMessage: {addListener: function() {}},
#                     connect: function() {},
#                     sendMessage: function() {},
#                     PlatformOs: { MAC: "mac", WIN: "win", ANDROID: "android", CROS: "cros", LINUX: "linux", OPENBSD: "openbsd" },
#                     PlatformArch: { ARM: "arm", X86_32: "x86-32", X86_64: "x86-64" },
#                     PlatformNaclArch: { ARM: "arm", X86_32: "x86-32", X86_64: "x86-64" }
#                 },
#                 loadTimes: function() { return { requestTime: Date.now() / 1000 - Math.random() * 2, startLoadTime: Date.now() / 1000 - Math.random() * 1.5, commitLoadTime: Date.now() / 1000 - Math.random() * 1, finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 0.5, finishLoadTime: Date.now() / 1000 - Math.random() * 0.3, firstPaintTime: Date.now() / 1000 - Math.random() * 0.2, firstPaintAfterLoadTime: 0, navigationType: "Other", wasFetchedViaSpdy: false, wasNpnNegotiated: true, npnNegotiatedProtocol: "h2", wasAlternateProtocolAvailable: false, connectionInfo: "h2" }; },
#                 csi: function() { return { startE: Date.now() - Math.random() * 3000, onloadT: Date.now() - Math.random() * 1000, pageT: Math.random() * 2000, tran: 15 }; },
#                 app: { isInstalled: false, InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' }, RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }, getDetails: function() {}, getIsInstalled: function() {}, installState: function() {}, runningState: function() {} }
#             };
            
#             // ========== FIX 2: MULTIPLE PLUGINS ==========
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format", filename: "internal-pdf-viewer", name: "Chrome PDF Plugin", length: 2, item: function(index) { return this[index]; }, namedItem: function(name) { return this[name]; }
#                 }, {
#                     description: "Chromium PDF Plugin", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", name: "Chrome PDF Viewer", length: 1, item: function(index) { return this[index]; }, namedItem: function(name) { return this[name]; }
#                 }, {
#                     description: "Native Client", filename: "internal-nacl-plugin", name: "Native Client", length: 2, item: function(index) { return this[index]; }, namedItem: function(name) { return this[name]; }
#                 }]
#             });
            
#             // ========== FIX 3: REMOVE WEBDRIVER ==========
#             Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
#             delete window.webdriver;
#             delete navigator.webdriver;
            
#             // ========== FIX 4: REALISTIC LANGUAGES ==========
#             Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
#             Object.defineProperty(navigator, 'language', { get: () => 'en-US' });
            
#             // ========== FIX 5: PERMISSIONS API ==========
#             const originalQuery = window.navigator.permissions.query;
#             window.navigator.permissions.query = (parameters) => (parameters.name === 'notifications' ? Promise.resolve({ state: Notification.permission }) : originalQuery(parameters));
            
#             // ========== FIX 6: WEBGL - NO TAMPERING, USE NATURAL ==========
            
#             // ========== FIX 7: REMOVE PROTOTYPE TAMPERING ==========
            
#             // ========== FIX 8: IFRAME CONTENT WINDOW ==========
#             Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', { get: function() { return window; } });
            
#             // ========== FIX 9: MEDIA DEVICES ==========
#             if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
#                 const originalEnumerate = navigator.mediaDevices.enumerateDevices;
#                 navigator.mediaDevices.enumerateDevices = function() { return originalEnumerate.call(this).then(devices => devices.map(device => ({ deviceId: device.deviceId, kind: device.kind, label: device.label, groupId: device.groupId, toJSON: function() { return this; } }))); };
#             }
            
#             // ========== FIX 10: BATTERY API ==========
#             if (navigator.getBattery) {
#                 const originalGetBattery = navigator.getBattery;
#                 navigator.getBattery = function() { return originalGetBattery.call(this).then(battery => { Object.defineProperty(battery, 'charging', { value: true }); Object.defineProperty(battery, 'chargingTime', { value: 0 }); Object.defineProperty(battery, 'dischargingTime', { value: Infinity }); Object.defineProperty(battery, 'level', { value: 1 }); return battery; }); };
#             }
            
#             // ========== FIX 11: CONNECTION API ==========
#             if (navigator.connection) {
#                 Object.defineProperty(navigator.connection, 'rtt', { get: () => Math.floor(Math.random() * 50) + 50 });
#             }
            
#             // ========== FIX 12: NOTIFICATION PERMISSIONS ==========
#             const originalNotificationPermission = Notification.permission;
#             Object.defineProperty(Notification, 'permission', { get: () => 'default' });
            
#             // ========== FIX 13: SCREEN CONSISTENCY ==========
#             Object.defineProperty(screen, 'availTop', { value: 0 });
#             Object.defineProperty(screen, 'availLeft', { value: 0 });
            
#             // ========== FIX 14: MOUSE EVENTS - Add realistic properties ==========
#             const originalMouseEvent = window.MouseEvent;
#             window.MouseEvent = function(type, eventInitDict) { const event = new originalMouseEvent(type, eventInitDict); if (eventInitDict && typeof eventInitDict.pageX === 'undefined') { Object.defineProperty(event, 'pageX', { value: eventInitDict.clientX || 0 }); Object.defineProperty(event, 'pageY', { value: eventInitDict.clientY || 0 }); } return event; };
            
#             console.log('🛡️ Advanced Stealth Protection Active - All fixes applied');
#         """)
        
#         print("✅ Advanced stealth v2 protection active - All 14 fixes applied!")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# # ========== ADVANCED HUMAN BEHAVIOR ==========

# def advanced_mouse_movement(page: Page, duration: float = 2.0):
#     """Realistic mouse movement using bezier curves"""
#     try:
#         viewport = page.viewport_size
#         max_x = viewport['width'] if viewport else 1200
#         max_y = viewport['height'] if viewport else 800
        
#         start_x = random.randint(100, max_x - 100)
#         start_y = random.randint(100, max_y - 100)
#         end_x = random.randint(100, max_x - 100)
#         end_y = random.randint(100, max_y - 100)
        
#         cp1_x = random.randint(min(start_x, end_x), max(start_x, end_x))
#         cp1_y = random.randint(min(start_y, end_y), max(start_y, end_y))
#         cp2_x = random.randint(min(start_x, end_x), max(start_x, end_x))
#         cp2_y = random.randint(min(start_y, end_y), max(start_y, end_y))
        
#         steps = random.randint(25, 40)
        
#         for i in range(steps):
#             t = i / steps
#             x = (1-t)**3 * start_x + 3*(1-t)**2*t * cp1_x + 3*(1-t)*t**2 * cp2_x + t**3 * end_x
#             y = (1-t)**3 * start_y + 3*(1-t)**2*t * cp1_y + 3*(1-t)*t**2 * cp2_y + t**3 * end_y
            
#             page.mouse.move(x, y)
#             time.sleep(duration / steps + random.uniform(0, 0.01))
        
#         print(f"🖱️ Bezier curve mouse movement completed")
        
#     except Exception as e:
#         print(f"⚠️ Mouse movement error: {e}")

# def realistic_scroll_pattern(page: Page):
#     """Realistic scrolling with pauses and variations"""
#     try:
#         page_height = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
#         current_position = 0
        
#         while current_position < page_height * 0.8:
#             scroll_amount = random.randint(80, 250)
#             page.evaluate(f"""
#                 window.scrollTo({{ top: window.scrollY + {scroll_amount}, behavior: 'smooth' }});
#             """)
#             current_position += scroll_amount
#             pause = random.uniform(1.5, 4.5)
#             time.sleep(pause)
            
#             if random.random() < 0.2:
#                 back_scroll = random.randint(30, 80)
#                 page.evaluate(f"""
#                     window.scrollTo({{ top: window.scrollY - {back_scroll}, behavior: 'smooth' }});
#                 """)
#                 time.sleep(random.uniform(0.5, 1.5))
#                 current_position -= back_scroll
        
#         print("📜 Realistic scroll pattern completed")
        
#     except Exception as e:
#         print(f"⚠️ Scroll pattern error: {e}")

# def random_interactions(page: Page):
#     """Random realistic interactions"""
#     try:
#         actions = ['hover_element', 'click_safe', 'double_move', 'pause_reading']
#         action = random.choice(actions)
        
#         if action == 'hover_element':
#             elements = page.locator("a, button, div[role='button']").all()[:5]
#             if elements:
#                 elem = random.choice(elements)
#                 if elem.is_visible():
#                     box = elem.bounding_box()
#                     if box:
#                         target_x = box['x'] + box['width'] / 2
#                         target_y = box['y'] + box['height'] / 2
#                         page.mouse.move(target_x, target_y)
#                         time.sleep(random.uniform(0.5, 1.5))
#                         print("🖱️ Hovered over element")
        
#         elif action == 'click_safe':
#             viewport = page.viewport_size
#             safe_x = random.randint(50, (viewport['width'] if viewport else 800) - 50)
#             safe_y = random.randint(50, (viewport['height'] if viewport else 600) - 50)
#             page.mouse.click(safe_x, safe_y)
#             time.sleep(random.uniform(0.3, 0.8))
#             print("🖱️ Safe click performed")
        
#         elif action == 'double_move':
#             advanced_mouse_movement(page, duration=random.uniform(1.5, 3.0))
        
#         elif action == 'pause_reading':
#             time.sleep(random.uniform(3, 7))
#             print("📖 Reading pause")
        
#     except Exception as e:
#         print(f"⚠️ Interaction error: {e}")

# # ========== FINGERPRINT DETECTION ==========

# def extract_complete_fingerprint(page: Page):
#     """Extract complete browser fingerprint"""
#     print("\n" + "="*70)
#     print("🔍 EXTRACTING COMPLETE FINGERPRINT")
#     print("="*70)
    
#     fingerprint = {}
    
#     try:
#         fingerprint_data = page.evaluate("""
#             () => {
#                 const fp = {};
#                 fp.navigator = { userAgent: navigator.userAgent, platform: navigator.platform, language: navigator.language, languages: navigator.languages, hardwareConcurrency: navigator.hardwareConcurrency, deviceMemory: navigator.deviceMemory || 'not available', maxTouchPoints: navigator.maxTouchPoints, vendor: navigator.vendor, webdriver: navigator.webdriver, pdfViewerEnabled: navigator.pdfViewerEnabled || false };
#                 fp.webdriverDetection = { navigatorWebdriver: navigator.webdriver, windowWebdriver: window.webdriver, navigatorWebdriverType: typeof navigator.webdriver };
#                 fp.chromeDetection = { chromeExists: !!window.chrome, chromeRuntime: window.chrome && window.chrome.runtime ? 'present' : 'not present', chromeKeys: window.chrome ? Object.keys(window.chrome) : [] };
#                 fp.permissions = { notificationPermission: Notification.permission || 'not available' };
#                 fp.plugins = { count: navigator.plugins.length, list: Array.from(navigator.plugins).map(p => ({ name: p.name, description: p.description, filename: p.filename })) };
#                 fp.mimeTypes = { count: navigator.mimeTypes.length, list: Array.from(navigator.mimeTypes).map(m => m.type) };
#                 try { const canvas = document.createElement('canvas'); const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl'); if (gl) { const debugInfo = gl.getExtension('WEBGL_debug_renderer_info'); fp.webgl = { vendor: gl.getParameter(gl.VENDOR), renderer: gl.getParameter(gl.RENDERER), unmaskedVendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'not available', unmaskedRenderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'not available' }; } else { fp.webgl = { error: 'WebGL not available' }; } } catch (e) { fp.webgl = { error: e.toString() }; }
#                 fp.screen = { width: screen.width, height: screen.height, colorDepth: screen.colorDepth, devicePixelRatio: window.devicePixelRatio };
#                 fp.timezone = { offset: new Date().getTimezoneOffset(), timezone: Intl.DateTimeFormat().resolvedOptions().timeZone };
#                 fp.prototypeTampering = { dateGetTimezoneOffset: Date.prototype.getTimezoneOffset.toString().includes('[native code]') };
#                 return fp;
#             }
#         """)
        
#         fingerprint = fingerprint_data
#         print_fingerprint_analysis(fingerprint)
#         return fingerprint
        
#     except Exception as e:
#         print(f"❌ Fingerprint extraction error: {e}")
#         return {}

# def print_fingerprint_analysis(fp):
#     """Print analysis"""
#     print("\n" + "🔴 CRITICAL BOT DETECTION SIGNALS".center(70, "="))
#     bot_signals = []
#     if fp.get('webdriverDetection', {}).get('navigatorWebdriver') is not None and fp['webdriverDetection']['navigatorWebdriver'] == True:
#         bot_signals.append("⚠️ navigator.webdriver = TRUE (MAJOR RED FLAG)")
#     elif fp.get('webdriverDetection', {}).get('navigatorWebdriver') is not None:
#         bot_signals.append(f"⚠️ navigator.webdriver exists: {fp['webdriverDetection']['navigatorWebdriver']}")
#     if len(fp.get('chromeDetection', {}).get('chromeKeys', [])) < 3:
#         bot_signals.append(f"⚠️ Incomplete chrome object ({len(fp.get('chromeDetection', {}).get('chromeKeys', []))} keys)")
#     if fp.get('plugins', {}).get('count', 0) < 2:
#         bot_signals.append(f"⚠️ Insufficient plugins ({fp.get('plugins', {}).get('count', 0)})")
#     if not fp.get('prototypeTampering', {}).get('dateGetTimezoneOffset', True):
#         bot_signals.append("⚠️ Date prototype TAMPERED")
#     if bot_signals:
#         print("\n🚨 BOT DETECTION SIGNALS FOUND:")
#         for signal in bot_signals:
#             print(f"  {signal}")
#     else:
#         print("\n✅ No obvious bot signals detected")
    
#     print("\n" + "📱 NAVIGATOR".center(70, "="))
#     nav = fp.get('navigator', {})
#     print(f"Webdriver: {nav.get('webdriver')}")
#     print(f"Languages: {nav.get('languages')}")
    
#     print("\n" + "🌐 CHROME OBJECT".center(70, "="))
#     chrome = fp.get('chromeDetection', {})
#     print(f"Chrome keys ({len(chrome.get('chromeKeys', []))}): {chrome.get('chromeKeys')}")
    
#     print("\n" + "🔌 PLUGINS".center(70, "="))
#     plugins = fp.get('plugins', {})
#     print(f"Plugin count: {plugins.get('count')}")
    
#     print("\n" + "⚙️ PROTOTYPE".center(70, "="))
#     proto = fp.get('prototypeTampering', {})
#     print(f"Date.getTimezoneOffset native: {proto.get('dateGetTimezoneOffset')}")

# def detect_skyscanner_checks(page: Page):
#     """Detect Skyscanner anti-bot"""
#     print("\n" + "🎯 SKYSCANNER DETECTION".center(70, "="))
    
#     try:
#         checks = page.evaluate("""
#             () => {
#                 const c = {};
#                 c.scripts = Array.from(document.scripts)
#                     .map(s => s.src)
#                     .filter(s => s.includes('captcha') || s.includes('px') || s.includes('perimeterx'));
#                 c.isCaptchaPage = window.location.href.includes('captcha');
#                 c.currentUrl = window.location.href;
#                 return c;
#             }
#         """)
        
#         if checks.get('isCaptchaPage'):
#             print("  ❌ CAPTCHA PAGE DETECTED!")
#         else:
#             print("  ✅ Not on captcha page")
        
#         if checks.get('scripts'):
#             print(f"  ⚠️ Anti-bot scripts found: {len(checks['scripts'])}")
#         else:
#             print("  ✅ No anti-bot scripts detected")
        
#         print(f"  🔗 URL: {checks.get('currentUrl', 'N/A')[:80]}...")
        
#         return checks
        
#     except Exception as e:
#         print(f"❌ Detection error: {e}")
#         return {}

# def save_fingerprint_to_file(fingerprint, checks):
#     """Save to JSON"""
#     try:
#         timestamp = time.strftime("%Y%m%d_%H%M%S")
#         filename = f"fingerprint_{timestamp}.json"
        
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump({
#                 "timestamp": timestamp,
#                 "fingerprint": fingerprint,
#                 "checks": checks
#             }, f, indent=2)
        
#         print(f"\n💾 Saved: {filename}")
#     except Exception as e:
#         print(f"⚠️ Save error: {e}")

# # ========== CORE FUNCTIONS ==========

# def parse_proxy_string(s: str):
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def test_proxy_connection(page: Page):
#     try:
#         print("🔍 Testing proxy...")
#         page.goto("https://httpbin.org/ip", timeout=20000, wait_until="domcontentloaded")
#         time.sleep(2)
#         ip_info = page.inner_text("body")
#         print(f"🌐 IP: {ip_info[:50]}...")
#         return True
#     except Exception as e:
#         print(f"⚠️ Proxy test failed: {e}")
#         return False

# def create_stealth_profile(profile_name, proxy_config=None):
#     max_retries = 3
    
#     for attempt in range(max_retries):
#         try:
#             print(f"🥷 Creating profile: {profile_name} (Attempt {attempt + 1})")
            
#             gl = GoLogin({"token": TOKEN})
            
#             if attempt > 0:
#                 time.sleep(5 * attempt)
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name,
#                 "webgl": { "mode": "noise", "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation"]), "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650"]) },
#                 "audioContext": { "mode": "noise", "noise": random.uniform(0.0001, 0.0005) },
#                 "canvas": { "mode": "noise" },
#                 "timezone": { "enabled": True, "fillBasedOnIp": True }
#             })
            
#             if not profile or 'id' not in profile:
#                 if attempt < max_retries - 1:
#                     continue
#                 return None
                
#             profile_id = profile['id']
#             print(f"✅ Profile created: {profile_id}")
            
#             if proxy_config:
#                 try:
#                     gl.changeProfileProxy(profile_id, {
#                         "mode": proxy_config['type'],
#                         "host": proxy_config['host'],
#                         "port": int(proxy_config['port']),
#                         "username": proxy_config.get('username', ''),
#                         "password": proxy_config.get('password', '')
#                     })
#                     print(f"🔄 Proxy configured")
#                 except Exception as e:
#                     print(f"⚠️ Proxy setup failed: {e}")
            
#             try:
#                 gl.updateUserAgentToLatestBrowser([profile_id])
#                 print("🔄 User agent updated")
#             except:
#                 pass
            
#             return profile_id
            
#         except Exception as e:
#             print(f"❌ Attempt {attempt + 1} failed: {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(5)
    
#     return None

# def start_stealth_browser(profile_id):
#     max_retries = 2
    
#     for attempt in range(max_retries):
#         try:
#             print(f"🚀 Starting browser (Attempt {attempt + 1})")
            
#             gl = GoLogin({"token": TOKEN, "profile_id": profile_id})
#             debugger_address = gl.start()
            
#             if not debugger_address:
#                 if attempt < max_retries - 1:
#                     continue
#                 return None, None, None, None
            
#             print(f"🔌 Browser endpoint: {debugger_address}")
#             time.sleep(random.uniform(4, 7))
            
#             pw = sync_playwright().start()
#             browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
            
#             context = browser.contexts[0] if browser.contexts else browser.new_context()
#             page = context.pages[0] if context.pages else context.new_page()
            
#             context.set_extra_http_headers({
#                 "DNT": "1",
#                 "Accept-Language": "en-US,en;q=0.9",
#                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#                 "Sec-Fetch-Dest": "document",
#                 "Sec-Fetch-Mode": "navigate",
#                 "Sec-Fetch-Site": "none",
#                 "Upgrade-Insecure-Requests": "1"
#             })
            
#             inject_ultimate_stealth_v2(page)
            
#             return gl, pw, browser, page
            
#         except Exception as e:
#             print(f"❌ Browser start failed: {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(3)
    
#     return None, None, None, None

# def ultimate_human_browsing(page: Page):
#     """Advanced human browsing with PerimeterX bypass techniques"""
#     try:
#         print("🎭 Starting ADVANCED human behavior simulation...")

#         # Navigate to target with enhanced retry
#         print(f"🌐 Navigating to: {TARGET_URL}")
#         success = False
#         strategies = [
#             ("domcontentloaded", 120000),
#             ("load", 180000),
#             (None, 240000)
#         ]
        
#         for i, (wait_strategy, timeout) in enumerate(strategies, 1):
#             try:
#                 print(f"📡 Loading strategy {i}...")
#                 if wait_strategy:
#                     page.goto(TARGET_URL, timeout=timeout, wait_until=wait_strategy)
#                 else:
#                     page.goto(TARGET_URL, timeout=timeout)
#                 print(f"✅ Page loaded successfully")
#                 success = True
#                 break
#             except TimeoutError as te:
#                 print(f"⚠️ Strategy {i} timed out: {str(te)[:80]}")
#             except Exception as e:
#                 print(f"⚠️ Strategy {i} failed: {str(e)[:80]}")
        
#         if not success:
#             print("❌ All loading strategies failed - Possible network or server issue")
#             return False
        
#         # Wait for dynamic content
#         try:
#             page.wait_for_load_state("networkidle", timeout=30000)
#             print("✅ Dynamic content loaded")
#         except TimeoutError:
#             print("⚠️ Dynamic content load timed out, proceeding with partial load")
        
#         # CRITICAL: Long stabilization for PerimeterX analysis
#         stabilization = random.uniform(15, 25)  # Increased stabilization
#         print(f"⏳ Page stabilization (PerimeterX analysis): {stabilization:.1f}s")
#         time.sleep(stabilization)
        
#         # Extract fingerprint
#         fingerprint = extract_complete_fingerprint(page)
        
#         # Detect Skyscanner checks
#         checks = detect_skyscanner_checks(page)
        
#         # Check if we're on captcha page
#         try:
#             current_url = page.url
#             if 'captcha' in current_url.lower():
#                 print("⚠️ WARNING: Redirected to CAPTCHA page!")
#                 print(f"   URL: {current_url}")
#             else:
#                 print(f"✅ On target page: {current_url[:60]}...")
#         except:
#             print("⚠️ Could not verify URL")
        
#         # Page basics
#         try:
#             page.wait_for_selector("body", timeout=15000)
#             title = page.title()
#             print(f"📰 Title: {title[:50]}...")
#         except:
#             print("⚠️ Could not get page title")
        
#         # PHASE 1: Initial observation
#         print("\n📖 PHASE 1: Initial page observation")
#         observation_time = random.uniform(10, 20)  # Increased observation time
#         print(f"   Reading page for {observation_time:.1f}s...")
#         for _ in range(3):
#             advanced_mouse_movement(page, duration=random.uniform(2, 4))
#             time.sleep(random.uniform(2, 4))
        
#         # PHASE 2: Realistic scrolling
#         print("\n📜 PHASE 2: Realistic scroll pattern")
#         realistic_scroll_pattern(page)
        
#         # PHASE 3: Interactive exploration
#         print("\n🖱️ PHASE 3: Interactive exploration")
#         interaction_time = random.uniform(25, 50)  # Increased interaction time
#         start_time = time.time()
#         interaction_count = 0
#         while time.time() - start_time < interaction_time:
#             action_choice = random.random()
#             if action_choice < 0.3:
#                 advanced_mouse_movement(page, duration=random.uniform(1.5, 3.5))
#                 interaction_count += 1
#             elif action_choice < 0.5:
#                 scroll_amount = random.randint(100, 300)
#                 direction = random.choice(['down', 'up'])
#                 if direction == 'down':
#                     page.evaluate(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}})")
#                 else:
#                     page.evaluate(f"window.scrollBy({{top: -{scroll_amount}, behavior: 'smooth'}})")
#                 time.sleep(random.uniform(1.5, 3))
#                 interaction_count += 1
#             elif action_choice < 0.7:
#                 random_interactions(page)
#                 interaction_count += 1
#             else:
#                 pause = random.uniform(3, 6)
#                 print(f"   📖 Reading pause: {pause:.1f}s")
#                 time.sleep(pause)
#             time.sleep(random.uniform(0.5, 2))
        
#         print(f"   ✅ Completed {interaction_count} interactions")
        
#         # PHASE 4: Final scroll to bottom
#         print("\n📜 PHASE 4: Final exploration")
#         try:
#             page_height = page.evaluate("document.body.scrollHeight")
#             page.evaluate(f"window.scrollTo({{top: {page_height * 0.9}, behavior: 'smooth'}})")
#             time.sleep(random.uniform(3, 5))
#             print("   ✅ Scrolled to bottom")
#         except:
#             pass
        
#         # Final fingerprint check
#         print("\n🔍 FINAL FINGERPRINT CHECK")
#         final_fp = extract_complete_fingerprint(page)
        
#         # Final Skyscanner check
#         final_checks = detect_skyscanner_checks(page)
        
#         # Save data
#         save_fingerprint_to_file(fingerprint, checks)
        
#         print("\n✅ Advanced human behavior simulation COMPLETE")
        
#         try:
#             final_url = page.url
#             if 'captcha' in final_url.lower():
#                 print("❌ RESULT: Still on CAPTCHA page - Detection occurred")
#                 return False
#             else:
#                 print("✅ RESULT: Successfully bypassed detection!")
#                 return True
#         except:
#             return True
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         return False

# def run_stealth_test():
#     """Main test runner"""
#     print("🎯 ULTIMATE STEALTH TEST - PERIMETERX BYPASS")
#     print("=" * 70)
    
#     successful_runs = 0
#     failed_profiles = 0
#     captcha_hits = 0
#     max_consecutive_failures = 5
#     consecutive_failures = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n{'='*70}")
#         print(f"🚀 PROFILE {profile_num}/{TOTAL_PROFILES}")
#         print(f"{'='*70}")
        
#         if consecutive_failures >= max_consecutive_failures:
#             print(f"⚠️ Too many failures. Taking 30s break...")
#             time.sleep(30)
#             consecutive_failures = 0
        
#         profile_name = f"stealth_v2_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
#             if not proxy_config and len(PROXY_LIST) > 1:
#                 proxy_str = PROXY_LIST[(PROXY_LIST.index(proxy_str) + 1) % len(PROXY_LIST)]
#                 proxy_config = parse_proxy_string(proxy_str)
#                 print(f"🔄 Switched to backup proxy: {proxy_str}")
        
#         profile_id = create_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             time.sleep(random.uniform(3, 6))
            
#             gl, pw, browser, page = start_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     if test_proxy_connection(page):
#                         success = ultimate_human_browsing(page)
#                         if success:
#                             successful_runs += 1
#                             consecutive_failures = 0
#                             print(f"\n🎉 ✅ PROFILE {profile_num} - SUCCESS!")
#                         else:
#                             failed_profiles += 1
#                             captcha_hits += 1
#                             consecutive_failures += 1
#                             print(f"\n❌ PROFILE {profile_num} - FAILED (Captcha)")
#                     else:
#                         print("❌ Proxy test failed, skipping profile")
#                         failed_profiles += 1
#                         consecutive_failures += 1
                    
#                     session_time = random.uniform(10, 20)
#                     print(f"🕐 Session cooldown: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 failed_profiles += 1
#                 consecutive_failures += 1
#                 print(f"❌ PROFILE {profile_num} - BROWSER FAILED")
#         else:
#             failed_profiles += 1
#             consecutive_failures += 1
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
        
#         pause = random.uniform(5, 10) if consecutive_failures == 0 else random.uniform(10, 15)
#         print(f"⏸️ Pause before next profile: {pause:.1f}s")
#         time.sleep(pause)
        
#         if profile_num % 5 == 0:
#             success_rate = (successful_runs / profile_num) * 100
#             print(f"\n{'='*70}")
#             print(f"📊 PROGRESS REPORT - {profile_num}/{TOTAL_PROFILES}")
#             print(f"{'='*70}")
#             print(f"✅ Successful: {successful_runs}")
#             print(f"❌ Failed: {failed_profiles}")
#             print(f"🚫 Captcha hits: {captcha_hits}")
#             print(f"📈 Success rate: {success_rate:.1f}%")
#             print(f"{'='*70}\n")
    
#     print(f"\n{'='*70}")
#     print(f"🏆 FINAL RESULTS")
#     print(f"{'='*70}")
#     print(f"✅ Successful: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")
#     print(f"❌ Failed: {failed_profiles}/{TOTAL_PROFILES} ({failed_profiles/TOTAL_PROFILES*100:.1f}%)")
#     print(f"🚫 Captcha hits: {captcha_hits}")
#     print(f"{'='*70}")
    
#     if successful_runs > 0:
#         print(f"\n🎯 Successfully bypassed PerimeterX {successful_runs} times!")
#         print(f"📁 Check fingerprint_*.json files for analysis")
#     else:
#         print("\n😞 No successful bypasses. Review fingerprint files.")
    
#     print(f"\n💡 Tips for improvement:")
#     print(f"   - Use residential proxies from target country")
#     print(f"   - Increase HUMAN_BEHAVIOR_TIME to 60-120s")
#     print(f"   - Add more realistic mouse patterns")
#     print(f"   - Use real device fingerprints")

# def cleanup_browser(gl, pw, browser):
#     """Cleanup resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser cleaned up")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("\n" + "="*70)
#     print("🛡️ ULTIMATE STEALTH SCRIPT v2.0 - PERIMETERX BYPASS")
#     print("="*70)
#     print(f"\n📋 Configuration:")
#     print(f"   Target: {TARGET_URL}")
#     print(f"   Profiles: {TOTAL_PROFILES}")
#     print(f"   Behavior time: {HUMAN_BEHAVIOR_TIME[0]}-{HUMAN_BEHAVIOR_TIME[1]}s")
#     print(f"   Proxy: {'Enabled' if PROXY_LIST else 'Disabled'}")
#     print("\n🔧 Features:")
#     print("   ✅ Complete Chrome object (4+ keys)")
#     print("   ✅ Multiple plugins (3)")
#     print("   ✅ No prototype tampering")
#     print("   ✅ Realistic mouse movements (Bezier curves)")
#     print("   ✅ Advanced scroll patterns")
#     print("   ✅ Interactive exploration")
#     print("   ✅ PerimeterX bypass techniques")
#     print("   ✅ Fingerprint analysis & export")
#     print("="*70 + "\n")
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_stealth_test()
#     except KeyboardInterrupt:
#         print("\n\n🛑 Test interrupted by user")
#     except Exception as e:
#         print(f"\n❌ Fatal error: {e}")
#         import traceback
#         traceback.print_exc()

# done


# import time
# import random
# import logging
# from datetime import datetime
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# SEARCH_TERM = "ishanprotfolio"
# PORTFOLIO_URL = "https://www.ishanprotpholio.co.in/"
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"

# # STEALTH SETTINGS
# TOTAL_PROFILES = 1000  # Run 1000 times
# PRE_NAVIGATION_DELAY = (8, 15)  # Delay before target site
# HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration
# PAGE_LOAD_PATIENCE = (4, 8)     # Page loading patience
# INTER_VISIT_DELAY = (10, 30)    # Random delay between visits

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # Navigation links for random click
# NAV_LINKS = [
#     {"selector": "a[aria-label='Car hire']", "name": "Car hire"},
#     {"selector": "a[aria-label='Hotels']", "name": "Hotels"},
#     {"selector": "a[aria-label='Explore everywhere']", "name": "Explore everywhere"}
# ]

# # Setup logging
# logging.basicConfig(
#     filename='stealth_browser_log.txt',
#     level=logging.INFO,
#     format='%(asctime)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile"""
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"🥷 Creating stealth profile: {profile_name}")
        
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac"]),
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
        
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             Date.prototype.getTimezoneOffset = () => -330;
            
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
        
#         print("✅ Stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with Google searches and portfolio visit"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
        
#         # First tab: Google search for 'ishanprotfolio'
#         context = page.context
#         search_page = context.new_page()
#         search_url = f"{GOOGLE_SEARCH_BASE}{SEARCH_TERM}"
#         print(f"🌐 Tab 1: Google search: {search_url}")
#         search_page.goto(search_url)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(search_page)
        
#         # Second tab: Google search for portfolio URL and navigate to it
#         portfolio_search_page = context.new_page()
#         portfolio_search_url = f"{GOOGLE_SEARCH_BASE}{PORTFOLIO_URL}"
#         print(f"🌐 Tab 2: Google search: {portfolio_search_url}")
#         portfolio_search_page.goto(portfolio_search_url)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(portfolio_search_page)
        
#         # Click on portfolio link in search results
#         try:
#             portfolio_link = portfolio_search_page.locator(f"a[href*='{PORTFOLIO_URL}']").first
#             if portfolio_link.is_visible():
#                 print(f"🌐 Tab 2: Navigating to {PORTFOLIO_URL}")
#                 portfolio_link.click()
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#                 perform_light_interaction(portfolio_search_page)
#         except Exception as e:
#             print(f"⚠️ Portfolio link click error: {e}")
        
#         # Close tabs
#         search_page.close()
#         portfolio_search_page.close()
        
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
        
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         elements = page.locator("a, button").all()[:3]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.2))
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def perform_random_nav_click(page: Page):
#     """Perform a random click on one of the navigation links"""
#     try:
#         selected_link = random.choice(NAV_LINKS)
#         link_selector = selected_link["selector"]
#         link_name = selected_link["name"]
#         print(f"🖱️ Attempting to click navigation link: {link_name}")
        
#         link = page.locator(link_selector).first
#         if link.is_visible() and link.is_enabled():
#             link.hover()
#             time.sleep(random.uniform(0.5, 1.5))
#             link.click()
#             print(f"✅ Clicked {link_name}")
#             time.sleep(random.uniform(2, 5))  # Wait after click
#             return link_name
#         else:
#             print(f"⚠️ Link {link_name} not visible or enabled")
#             return None
#     except Exception as e:
#         print(f"⚠️ Navigation click error: {e}")
#         return None

# def ultimate_human_browsing(page: Page, profile_name: str):
#     """Human-like browsing behavior with random navigation click"""
#     try:
#         print("🎭 Starting human behavior simulation...")
        
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         page.goto(TARGET_URL)
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             return True, None
        
#         try:
#             page.wait_for_selector("body", timeout=10000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         # Perform random navigation click
#         clicked_link = perform_random_nav_click(page)
        
#         # Log the profile and click details
#         logging.info(f"Profile: {profile_name}, Clicked Link: {clicked_link or 'None'}")
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#             execute_human_action(page, action)
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True, clicked_link
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         logging.info(f"Profile: {profile_name}, Error: {str(e)}")
#         return False, None

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         challenge_indicators = ['captcha', 'robot', 'verify', 'challenge']
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             handle_captcha_page(page)
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
        
#         button_selectors = ["button", "[role='button']", ".button"]
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible() and element.is_enabled():
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'verify']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
#                             element.hover()
#                             time.sleep(random.uniform(1, 2))
#                             element.click()
#                             time.sleep(random.uniform(2, 4))
#                             return
#             except:
#                 continue
        
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(4, 8))
        
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 200)
#             page.evaluate(f"""
#                 window.scrollBy({{
#                     top: {scroll_distance},
#                     left: 0,
#                     behavior: 'smooth'
#                 }});
#             """)
#             time.sleep(random.uniform(0.8, 1.5))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a").all()[:4]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible():
#                         element.hover()
#                         time.sleep(random.uniform(0.4, 1))
                
#         elif action == 'reading_pause':
#             time.sleep(random.uniform(1.5, 4))
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION AND RANDOM CLICKS ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     pre_navigation_warmup(page)
#                     success, clicked_link = ultimate_human_browsing(page, profile_name)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS! Clicked: {clicked_link or 'None'}")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#                 logging.info(f"Profile: {profile_name}, Error: Browser start failed")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
#             logging.info(f"Profile: {profile_name}, Error: Profile creation failed")
        
#         # Random delay between visits
#         inter_visit_delay = random.uniform(*INTER_VISIT_DELAY)
#         print(f"⏳ Inter-visit delay: {inter_visit_delay:.1f}s")
#         time.sleep(inter_visit_delay)
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION AND RANDOM CLICKS")
#     print("Stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")




# import time
# import random
# import logging
# from datetime import datetime
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# SEARCH_TERM = "ishanprotfolio"
# PORTFOLIO_URL = "https://www.ishanprotpholio.co.in/"
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"

# # STEALTH SETTINGS
# TOTAL_PROFILES = 1000  # Run 1000 times
# PRE_NAVIGATION_DELAY = (8, 15)  # Delay before target site
# HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration
# PAGE_LOAD_PATIENCE = (4, 8)     # Page loading patience
# INTER_VISIT_DELAY = (10, 30)    # Random delay between visits
# CLICK_PAGE_DURATION = (5, 10)   # Duration to stay on clicked page
# NAVIGATION_TIMEOUT = 60000      # Increased timeout for page.goto

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # Navigation links for random click on TARGET_URL only
# NAV_LINKS = [
#     {"selector": "a[aria-label='Car hire']", "name": "Car hire", "href": "https://www.skyscanner.co.in/carhire"},
#     {"selector": "a[aria-label='Hotels']", "name": "Hotels", "href": "https://www.skyscanner.co.in/hotels"}
# ]

# # Setup logging
# logging.basicConfig(
#     filename='stealth_browser_log.txt',
#     level=logging.INFO,
#     format='%(asctime)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
#     filemode='a'  # Append mode to ensure file creation
# )
# logger = logging.getLogger()

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile"""
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"🥷 Creating stealth profile: {profile_name}")
#         logger.info(f"Creating profile: {profile_name}")
        
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac"]),
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             logger.info(f"Profile: {profile_name}, Status: Profile creation failed")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
#         logger.info(f"Profile: {profile_name}, Status: Profile created - {profile_id}")
        
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#                 logger.info(f"Profile: {profile_name}, Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
#                 logger.info(f"Profile: {profile_name}, Proxy setup error: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#             logger.info(f"Profile: {profile_name}, User agent updated")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
#             logger.info(f"Profile: {profile_name}, User agent update error: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         logger.info(f"Profile: {profile_name}, Status: Profile creation error - {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
#         logger.info(f"Profile ID: {profile_id}, Browser started at endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         logger.info(f"Profile ID: {profile_id}, Status: Browser start error - {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             Date.prototype.getTimezoneOffset = () => -330;
            
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
#         print("✅ Stealth protection active")
#         logger.info("Stealth protection injected")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")
#         logger.info(f"Stealth injection error: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with Google searches and portfolio visit"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
#         logger.info("Starting pre-navigation warmup")
        
#         # First tab: Google search for 'ishanprotfolio'
#         context = page.context
#         search_page = context.new_page()
#         search_url = f"{GOOGLE_SEARCH_BASE}{SEARCH_TERM}"
#         print(f"🌐 Tab 1: Google search: {search_url}")
#         logger.info(f"Tab 1: Navigating to Google search: {search_url}")
#         search_page.goto(search_url, timeout=NAVIGATION_TIMEOUT)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(search_page)
        
#         # Second tab: Google search for portfolio URL and navigate to it
#         portfolio_search_page = context.new_page()
#         portfolio_search_url = f"{GOOGLE_SEARCH_BASE}{PORTFOLIO_URL}"
#         print(f"🌐 Tab 2: Google search: {portfolio_search_url}")
#         logger.info(f"Tab 2: Navigating to Google search: {portfolio_search_url}")
#         portfolio_search_page.goto(portfolio_search_url, timeout=NAVIGATION_TIMEOUT)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(portfolio_search_page)
        
#         # Click on portfolio link in search results
#         try:
#             portfolio_link = portfolio_search_page.locator(f"a[href*='{PORTFOLIO_URL}']").first
#             if portfolio_link.is_visible():
#                 print(f"🌐 Tab 2: Navigating to {PORTFOLIO_URL}")
#                 logger.info(f"Tab 2: Navigating to {PORTFOLIO_URL}")
#                 portfolio_link.click(timeout=10000)
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#                 perform_light_interaction(portfolio_search_page)
#         except Exception as e:
#             print(f"⚠️ Portfolio link click error: {e}")
#             logger.info(f"Portfolio link click error: {e}")
        
#         # Close tabs
#         search_page.close()
#         portfolio_search_page.close()
        
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         logger.info(f"Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
        
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")
#         logger.info(f"Warmup error: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         # Select safe elements, avoiding problematic Google navigation elements
#         elements = page.locator("a:not([jsname]), button:not([jsname])").all()[:3]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.scroll_into_view_if_needed()
#                 random_element.hover(timeout=3000)  # Reduced timeout
#                 time.sleep(random.uniform(0.5, 1.2))
#                 logger.info("Light interaction performed: hover")
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")
#         logger.info(f"Light interaction error: {e}")

# def perform_random_nav_click(page: Page):
#     """Perform a random click on one of the navigation links on TARGET_URL only"""
#     try:
#         # Verify we are on the target URL
#         if page.url != TARGET_URL:
#             print(f"⚠️ Not on target URL ({page.url}), skipping navigation click")
#             logger.info(f"Not on target URL ({page.url}), skipping navigation click")
#             return None, 0
        
#         selected_link = random.choice(NAV_LINKS)
#         link_selector = selected_link["selector"]
#         link_name = selected_link["name"]
#         print(f"🖱️ Attempting to click navigation link: {link_name} on {TARGET_URL}")
#         logger.info(f"Attempting to click navigation link: {link_name} on {TARGET_URL}")
        
#         # Wait for the link to be visible with retries
#         for attempt in range(3):
#             try:
#                 link = page.locator(link_selector).first
#                 page.wait_for_selector(link_selector, state="visible", timeout=15000)  # Increased timeout
#                 if link.is_visible() and link.is_enabled():
#                     link.scroll_into_view_if_needed()
#                     link.hover(timeout=5000)
#                     time.sleep(random.uniform(0.5, 1.5))
#                     click_start_time = time.time()
#                     link.click(timeout=10000)
#                     page.wait_for_load_state("domcontentloaded", timeout=15000)
#                     click_duration = random.uniform(*CLICK_PAGE_DURATION)  # Random duration on clicked page
#                     time.sleep(click_duration)
#                     print(f"✅ Clicked {link_name} (stayed {click_duration:.1f}s)")
#                     logger.info(f"Clicked {link_name} (stayed {click_duration:.1f}s)")
#                     return link_name, click_duration
#                 else:
#                     print(f"⚠️ Link {link_name} not visible or enabled on attempt {attempt + 1}")
#                     logger.info(f"Link {link_name} not visible or enabled on attempt {attempt + 1}")
#             except Exception as e:
#                 print(f"⚠️ Attempt {attempt + 1} failed for {link_name}: {e}")
#                 logger.info(f"Attempt {attempt + 1} failed for {link_name}: {e}")
#                 time.sleep(random.uniform(1, 3))
        
#         print(f"❌ Failed to click {link_name} after retries")
#         logger.info(f"Failed to click {link_name} after retries")
#         return None, 0
#     except Exception as e:
#         print(f"⚠️ Navigation click error: {e}")
#         logger.info(f"Navigation click error: {e}")
#         return None, 0

# def ultimate_human_browsing(page: Page, profile_name: str):
#     """Human-like browsing behavior with random navigation click on TARGET_URL"""
#     try:
#         print("🎭 Starting human behavior simulation...")
#         logger.info(f"Profile: {profile_name}, Starting human behavior simulation")
        
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         logger.info(f"Profile: {profile_name}, Navigating to target: {TARGET_URL}")
        
#         # Retry navigation up to 2 times
#         for attempt in range(2):
#             try:
#                 page.goto(TARGET_URL, timeout=NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
#                 break
#             except TimeoutError as e:
#                 print(f"⚠️ Navigation attempt {attempt + 1} failed: {e}")
#                 logger.info(f"Profile: {profile_name}, Navigation attempt {attempt + 1} failed: {e}")
#                 if attempt == 1:
#                     raise Exception("Failed to navigate to target URL after retries")
#                 time.sleep(random.uniform(5, 10))
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         logger.info(f"Profile: {profile_name}, Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             logger.info(f"Profile: {profile_name}, Status: Challenge detected, Clicked Link: None, Duration: 0s")
#             return True, None, 0
        
#         try:
#             page.wait_for_selector("body", timeout=15000)
#             print("📄 Page elements detected")
#             logger.info(f"Profile: {profile_name}, Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
#             logger.info(f"Profile: {profile_name}, Page load timeout")
        
#         # Perform random navigation click only on TARGET_URL
#         clicked_link, click_duration = perform_random_nav_click(page)
        
#         # Log the profile and click details
#         logger.info(f"Profile: {profile_name}, Clicked Link: {clicked_link or 'None'}, Duration: {click_duration:.1f}s")
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
#         logger.info(f"Profile: {profile_name}, Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#             execute_human_action(page, action)
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         logger.info(f"Profile: {profile_name}, Human behavior complete")
#         return True, clicked_link, click_duration
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         logger.info(f"Profile: {profile_name}, Status: Error - {e}, Clicked Link: None, Duration: 0s")
#         return False, None, 0

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         challenge_indicators = ['captcha', 'robot', 'verify', 'challenge']
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             logger.info(f"Challenge detected at URL: {current_url}")
#             handle_captcha_page(page)
#             return True
#         else:
#             print("✅ No challenges detected")
#             logger.info("No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         logger.info(f"Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
#         logger.info("Attempting to handle CAPTCHA page")
        
#         button_selectors = ["button", "[role='button']", ".button"]
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible() and element.is_enabled():
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'verify']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
#                             logger.info(f"Found action button: {element.inner_text()}")
#                             element.scroll_into_view_if_needed()
#                             element.hover(timeout=5000)
#                             time.sleep(random.uniform(1, 2))
#                             element.click(timeout=10000)
#                             time.sleep(random.uniform(2, 4))
#                             return
#             except:
#                 continue
        
#         print("⏳ No action buttons found, waiting...")
#         logger.info("No action buttons found, waiting")
#         time.sleep(random.uniform(4, 8))
        
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")
#         logger.info(f"CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 200)
#             page.evaluate(f"""
#                 window.scrollBy({{
#                     top: {scroll_distance},
#                     left: 0,
#                     behavior: 'smooth'
#                 }});
#             """)
#             time.sleep(random.uniform(0.8, 1.5))
#             logger.info("Human action: realistic_scroll")
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a").all()[:4]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible():
#                         element.scroll_into_view_if_needed()
#                         element.hover(timeout=5000)
#                         time.sleep(random.uniform(0.4, 1))
#                 logger.info("Human action: mouse_trail")
                
#         elif action == 'reading_pause':
#             time.sleep(random.uniform(1.5, 4))
#             logger.info("Human action: reading_pause")
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")
#         logger.info(f"Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION AND TARGETED CLICKS ACTIVATED")
#     print("=" * 60)
#     logger.info("STEALTH MODE WITH COOKIE CONFUSION AND TARGETED CLICKS ACTIVATED")
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
#         logger.info(f"Starting PROFILE {profile_num}/{TOTAL_PROFILES}")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             logger.info(f"Profile: {profile_name}, Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     pre_navigation_warmup(page)
#                     success, clicked_link, click_duration = ultimate_human_browsing(page, profile_name)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS! Clicked: {clicked_link or 'None'} ({click_duration:.1f}s)")
#                         logger.info(f"Profile: {profile_name}, Status: Success, Clicked Link: {clicked_link or 'None'}, Duration: {click_duration:.1f}s")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
#                         logger.info(f"Profile: {profile_name}, Status: Failed")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     logger.info(f"Profile: {profile_name}, Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#                 logger.info(f"Profile: {profile_name}, Status: Browser start failed")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
#             logger.info(f"Profile: {profile_name}, Status: Profile creation failed")
        
#         # Random delay between visits
#         inter_visit_delay = random.uniform(*INTER_VISIT_DELAY)
#         print(f"⏳ Inter-visit delay: {inter_visit_delay:.1f}s")
#         logger.info(f"Inter-visit delay: {inter_visit_delay:.1f}s")
#         time.sleep(inter_visit_delay)
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")
#     logger.info(f"STEALTH TEST COMPLETE! Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#         logger.info("Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")
#         logger.info(f"Cleanup error: {e}")

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION AND TARGETED CLICKS")
#     print("Stealth configuration activated")
#     print("=" * 60)
#     logger.info("ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION AND TARGETED CLICKS STARTED")
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         logger.info("GoLogin not available")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#         logger.info("Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")
#         logger.info(f"Fatal error in stealth test: {e}")





# import time
# import random
# import logging
# from datetime import datetime
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# SEARCH_TERM = "ishanprotfolio"
# PORTFOLIO_URL = "https://www.ishanprotpholio.co.in/"
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"

# # STEALTH SETTINGS
# TOTAL_PROFILES = 1000  # Run 1000 times
# PRE_NAVIGATION_DELAY = (8, 15)  # Delay before target site
# HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration
# PAGE_LOAD_PATIENCE = (4, 8)     # Page loading patience
# INTER_VISIT_DELAY = (10, 30)    # Random delay between visits
# CLICK_PAGE_DURATION = (5, 10)   # Duration to stay on clicked page
# NAVIGATION_TIMEOUT = 60000      # Timeout for page.goto
# SELECTOR_TIMEOUT = 20000        # Timeout for finding elements

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # Navigation links for random click on TARGET_URL only
# NAV_LINKS = [
#     {"selector": "a[aria-label='Car hire'][href*='carhire']", "name": "Car hire", "href": "https://www.skyscanner.co.in/carhire"},
#     {"selector": "a[aria-label='Hotels'][href*='hotels']", "name": "Hotels", "href": "https://www.skyscanner.co.in/hotels"}
# ]

# # Setup logging
# logging.basicConfig(
#     filename='stealth_browser_log.txt',
#     level=logging.INFO,
#     format='%(asctime)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
#     filemode='a'  # Append mode to ensure file creation
# )
# logger = logging.getLogger()

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile"""
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"🥷 Creating stealth profile: {profile_name}")
#         logger.info(f"Creating profile: {profile_name}")
        
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac"]),
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             logger.info(f"Profile: {profile_name}, Status: Profile creation failed")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
#         logger.info(f"Profile: {profile_name}, Status: Profile created - {profile_id}")
        
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#                 logger.info(f"Profile: {profile_name}, Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
#                 logger.info(f"Profile: {profile_name}, Proxy setup error: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#             logger.info(f"Profile: {profile_name}, User agent updated")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
#             logger.info(f"Profile: {profile_name}, User agent update error: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         logger.info(f"Profile: {profile_name}, Status: Profile creation error - {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration, with proxy retry"""
#     for attempt in range(3):
#         try:
#             gl = GoLogin({
#                 "token": TOKEN,
#                 "profile_id": profile_id
#             })
#             print(f"🚀 Starting stealth browser for: {profile_id} (Attempt {attempt + 1})")
#             logger.info(f"Profile ID: {profile_id}, Starting browser (Attempt {attempt + 1})")
#             debugger_address = gl.start()
#             print(f"🔌 Browser endpoint: {debugger_address}")
#             logger.info(f"Profile ID: {profile_id}, Browser started at endpoint: {debugger_address}")
            
#             wait_time = random.uniform(3, 6)
#             print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             pw = sync_playwright().start()
#             cdp_url = f"http://{debugger_address}"
#             browser = pw.chromium.connect_over_cdp(cdp_url)
#             context = browser.contexts[0]
#             if context.pages:
#                 page = context.pages[0]
#             else:
#                 page = context.new_page()
            
#             inject_ultimate_stealth(page)
#             return gl, pw, browser, page
            
#         except Exception as e:
#             print(f"❌ Browser start error (Attempt {attempt + 1}): {e}")
#             logger.info(f"Profile ID: {profile_id}, Browser start error (Attempt {attempt + 1}): {e}")
#             if attempt == 2:
#                 print("❌ All browser start attempts failed")
#                 logger.info(f"Profile ID: {profile_id}, Status: All browser start attempts failed")
#                 return None, None, None, None
#             time.sleep(random.uniform(5, 10))
    
#     return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             Date.prototype.getTimezoneOffset = () => -330;
            
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
#         print("✅ Stealth protection active")
#         logger.info("Stealth protection injected")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")
#         logger.info(f"Stealth injection error: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with Google searches and portfolio visit"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
#         logger.info("Starting pre-navigation warmup")
        
#         # First tab: Google search for 'ishanprotfolio'
#         context = page.context
#         search_page = context.new_page()
#         search_url = f"{GOOGLE_SEARCH_BASE}{SEARCH_TERM}"
#         print(f"🌐 Tab 1: Google search: {search_url}")
#         logger.info(f"Tab 1: Navigating to Google search: {search_url}")
#         search_page.goto(search_url, timeout=NAVIGATION_TIMEOUT)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(search_page)
        
#         # Second tab: Google search for portfolio URL and navigate to it
#         portfolio_search_page = context.new_page()
#         portfolio_search_url = f"{GOOGLE_SEARCH_BASE}{PORTFOLIO_URL}"
#         print(f"🌐 Tab 2: Google search: {portfolio_search_url}")
#         logger.info(f"Tab 2: Navigating to Google search: {portfolio_search_url}")
#         portfolio_search_page.goto(portfolio_search_url, timeout=NAVIGATION_TIMEOUT)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(portfolio_search_page)
        
#         # Click on portfolio link in search results
#         try:
#             portfolio_link = portfolio_search_page.locator(f"a[href='{PORTFOLIO_URL}']").first  # Exact match
#             if portfolio_link.is_visible(timeout=SELECTOR_TIMEOUT):
#                 print(f"🌐 Tab 2: Navigating to {PORTFOLIO_URL}")
#                 logger.info(f"Tab 2: Navigating to {PORTFOLIO_URL}")
#                 portfolio_link.scroll_into_view_if_needed()
#                 portfolio_link.click(timeout=10000)
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#                 perform_light_interaction(portfolio_search_page)
#         except Exception as e:
#             print(f"⚠️ Portfolio link click error: {e}")
#             logger.info(f"Portfolio link click error: {e}")
        
#         # Close tabs
#         search_page.close()
#         portfolio_search_page.close()
        
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         logger.info(f"Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
        
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")
#         logger.info(f"Warmup error: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         # Select safe elements, avoiding problematic Google elements
#         elements = page.locator("a:not([jsname]):not([href*='accounts.google.com']), button:not([jsname])").all()[:3]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible(timeout=SELECTOR_TIMEOUT):
#                 random_element.scroll_into_view_if_needed()
#                 random_element.hover(timeout=3000)
#                 time.sleep(random.uniform(0.5, 1.2))
#                 logger.info("Light interaction performed: hover")
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")
#         logger.info(f"Light interaction error: {e}")

# def perform_random_nav_click(page: Page):
#     """Perform a random click on 'Car hire' or 'Hotels' on TARGET_URL, with fallback to random element"""
#     try:
#         # Verify we are on the target URL
#         if page.url != TARGET_URL:
#             print(f"⚠️ Not on target URL ({page.url}), skipping navigation click")
#             logger.info(f"Not on target URL ({page.url}), skipping navigation click")
#             return None, 0
        
#         # Refresh page to ensure elements load
#         print("🔄 Refreshing page to ensure elements load")
#         logger.info("Refreshing page to ensure elements load")
#         page.reload(timeout=NAVIGATION_TIMEOUT)
#         time.sleep(random.uniform(2, 5))
        
#         print(f"🖱️ Attempting to find navigation links on {TARGET_URL}")
#         logger.info(f"Attempting to find navigation links on {TARGET_URL}")
        
#         # Try to find and click "Car hire" or "Hotels"
#         selected_link = random.choice(NAV_LINKS)
#         link_selector = selected_link["selector"]
#         link_name = selected_link["name"]
#         print(f"🖱️ Attempting to click navigation link: {link_name}")
#         logger.info(f"Attempting to click navigation link: {link_name}")
        
#         for attempt in range(3):
#             try:
#                 link = page.locator(link_selector).first
#                 page.wait_for_selector(link_selector, state="visible", timeout=SELECTOR_TIMEOUT)
#                 if link.is_visible() and link.is_enabled():
#                     link.scroll_into_view_if_needed()
#                     link.hover(timeout=5000)
#                     time.sleep(random.uniform(0.5, 1.5))
#                     click_start_time = time.time()
#                     link.click(timeout=10000)
#                     page.wait_for_load_state("domcontentloaded", timeout=15000)
#                     click_duration = random.uniform(*CLICK_PAGE_DURATION)
#                     time.sleep(click_duration)
#                     print(f"✅ Clicked {link_name} (stayed {click_duration:.1f}s)")
#                     logger.info(f"Clicked {link_name} (stayed {click_duration:.1f}s)")
#                     return link_name, click_duration
#                 else:
#                     print(f"⚠️ Link {link_name} not visible or enabled on attempt {attempt + 1}")
#                     logger.info(f"Link {link_name} not visible or enabled on attempt {attempt + 1}")
#             except Exception as e:
#                 print(f"⚠️ Attempt {attempt + 1} failed for {link_name}: {e}")
#                 logger.info(f"Attempt {attempt + 1} failed for {link_name}: {e}")
#                 time.sleep(random.uniform(1, 3))
        
#         print(f"❌ Failed to click {link_name}, attempting random click")
#         logger.info(f"Failed to click {link_name}, attempting random click")
        
#         # Fallback: Click a random visible <a> or <button>
#         elements = page.locator("a, button").all()[:5]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible(timeout=SELECTOR_TIMEOUT):
#                 random_element.scroll_into_view_if_needed()
#                 random_element.hover(timeout=5000)
#                 time.sleep(random.uniform(0.5, 1.5))
#                 click_start_time = time.time()
#                 random_element.click(timeout=10000)
#                 page.wait_for_load_state("domcontentloaded", timeout=15000)
#                 click_duration = random.uniform(*CLICK_PAGE_DURATION)
#                 time.sleep(click_duration)
#                 print(f"✅ Random click performed (stayed {click_duration:.1f}s)")
#                 logger.info(f"Random click performed (stayed {click_duration:.1f}s)")
#                 return "Random", click_duration
        
#         print("❌ No clickable elements found")
#         logger.info("No clickable elements found")
#         return None, 0
#     except Exception as e:
#         print(f"⚠️ Navigation click error: {e}")
#         logger.info(f"Navigation click error: {e}")
#         return None, 0

# def ultimate_human_browsing(page: Page, profile_name: str):
#     """Human-like browsing behavior with random navigation click on TARGET_URL"""
#     try:
#         print("🎭 Starting human behavior simulation...")
#         logger.info(f"Profile: {profile_name}, Starting human behavior simulation")
        
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         logger.info(f"Profile: {profile_name}, Navigating to target: {TARGET_URL}")
        
#         # Retry navigation up to 2 times
#         for attempt in range(2):
#             try:
#                 page.goto(TARGET_URL, timeout=NAVIGATION_TIMEOUT, wait_until="domcontentloaded")
#                 break
#             except TimeoutError as e:
#                 print(f"⚠️ Navigation attempt {attempt + 1} failed: {e}")
#                 logger.info(f"Profile: {profile_name}, Navigation attempt {attempt + 1} failed: {e}")
#                 if attempt == 1:
#                     logger.info(f"Profile: {profile_name}, Status: Failed navigation to target URL")
#                     return False, None, 0
#                 time.sleep(random.uniform(5, 10))
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         logger.info(f"Profile: {profile_name}, Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             logger.info(f"Profile: {profile_name}, Status: Challenge detected, Clicked Link: None, Duration: 0s")
#             return True, None, 0
        
#         try:
#             page.wait_for_selector("body", timeout=SELECTOR_TIMEOUT)
#             print("📄 Page elements detected")
#             logger.info(f"Profile: {profile_name}, Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
#             logger.info(f"Profile: {profile_name}, Page load timeout")
        
#         # Perform random navigation click
#         clicked_link, click_duration = perform_random_nav_click(page)
        
#         # Log the profile and click details
#         logger.info(f"Profile: {profile_name}, Clicked Link: {clicked_link or 'None'}, Duration: {click_duration:.1f}s")
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
#         logger.info(f"Profile: {profile_name}, Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#             execute_human_action(page, action)
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         logger.info(f"Profile: {profile_name}, Human behavior complete")
#         return True, clicked_link, click_duration
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         logger.info(f"Profile: {profile_name}, Status: Error - {e}, Clicked Link: None, Duration: 0s")
#         return False, None, 0

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         challenge_indicators = ['captcha', 'robot', 'verify', 'challenge']
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             logger.info(f"Challenge detected at URL: {current_url}")
#             handle_captcha_page(page)
#             return True
#         else:
#             print("✅ No challenges detected")
#             logger.info("No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         logger.info(f"Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
#         logger.info("Attempting to handle CAPTCHA page")
        
#         button_selectors = ["button", "[role='button']", ".button"]
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible() and element.is_enabled():
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'verify']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
#                             logger.info(f"Found action button: {element.inner_text()}")
#                             element.scroll_into_view_if_needed()
#                             element.hover(timeout=5000)
#                             time.sleep(random.uniform(1, 2))
#                             element.click(timeout=10000)
#                             time.sleep(random.uniform(2, 4))
#                             return
#             except:
#                 continue
        
#         print("⏳ No action buttons found, waiting...")
#         logger.info("No action buttons found, waiting")
#         time.sleep(random.uniform(4, 8))
        
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")
#         logger.info(f"CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 200)
#             page.evaluate(f"""
#                 window.scrollBy({{
#                     top: {scroll_distance},
#                     left: 0,
#                     behavior: 'smooth'
#                 }});
#             """)
#             time.sleep(random.uniform(0.8, 1.5))
#             logger.info("Human action: realistic_scroll")
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a").all()[:4]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible():
#                         element.scroll_into_view_if_needed()
#                         element.hover(timeout=5000)
#                         time.sleep(random.uniform(0.4, 1))
#                 logger.info("Human action: mouse_trail")
                
#         elif action == 'reading_pause':
#             time.sleep(random.uniform(1.5, 4))
#             logger.info("Human action: reading_pause")
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")
#         logger.info(f"Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION AND TARGETED CLICKS ACTIVATED")
#     print("=" * 60)
#     logger.info("STEALTH MODE WITH COOKIE CONFUSION AND TARGETED CLICKS ACTIVATED")
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
#         logger.info(f"Starting PROFILE {profile_num}/{TOTAL_PROFILES}")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             logger.info(f"Profile: {profile_name}, Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     pre_navigation_warmup(page)
#                     success, clicked_link, click_duration = ultimate_human_browsing(page, profile_name)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS! Clicked: {clicked_link or 'None'} ({click_duration:.1f}s)")
#                         logger.info(f"Profile: {profile_name}, Status: Success, Clicked Link: {clicked_link or 'None'}, Duration: {click_duration:.1f}s")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
#                         logger.info(f"Profile: {profile_name}, Status: Failed")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     logger.info(f"Profile: {profile_name}, Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#                 logger.info(f"Profile: {profile_name}, Status: Browser start failed")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
#             logger.info(f"Profile: {profile_name}, Status: Profile creation failed")
        
#         # Random delay between visits
#         inter_visit_delay = random.uniform(*INTER_VISIT_DELAY)
#         print(f"⏳ Inter-visit delay: {inter_visit_delay:.1f}s")
#         logger.info(f"Inter-visit delay: {inter_visit_delay:.1f}s")
#         time.sleep(inter_visit_delay)
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")
#     logger.info(f"STEALTH TEST COMPLETE! Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#         logger.info("Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")
#         logger.info(f"Cleanup error: {e}")

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION AND TARGETED CLICKS")
#     print("Stealth configuration activated")
#     print("=" * 60)
#     logger.info("ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION AND TARGETED CLICKS STARTED")
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         logger.info("GoLogin not available")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#         logger.info("Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")
#         logger.info(f"Fatal error in stealth test: {e}")



# import time
# import random
# import logging
# from datetime import datetime
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# SEARCH_TERM = "ishanprotfolio"
# PORTFOLIO_URL = "https://www.ishanprotpholio.co.in/"
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"

# # STEALTH SETTINGS
# TOTAL_PROFILES = 1000  # Run 1000 times
# PRE_NAVIGATION_DELAY = (8, 15)  # Delay before target site
# HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration
# PAGE_LOAD_PATIENCE = (4, 8)     # Page loading patience
# INTER_VISIT_DELAY = (10, 30)    # Random delay between visits

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # Navigation links for random click
# NAV_LINKS = [
#     {"selector": "a[aria-label='Car hire']", "name": "Car hire"},
#     {"selector": "a[aria-label='Hotels']", "name": "Hotels"},
#     {"selector": "a[aria-label='Explore everywhere']", "name": "Explore everywhere"}
# ]

# # Setup logging for profile visits
# logging.basicConfig(
#     filename='profile_visits.log',
#     level=logging.INFO,
#     format='%(asctime)s - Profile: %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     """Create stealth profile"""
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"🥷 Creating stealth profile: {profile_name}")
        
#         profile = gl.createProfileRandomFingerprint({
#             "os": random.choice(["win", "mac"]),
#             "name": profile_name
#         })
        
#         if not profile or 'id' not in profile:
#             print(f"❌ Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"✅ Profile created: {profile_id}")
        
#         if proxy_config:
#             try:
#                 proxy_data = {
#                     "mode": proxy_config['type'],
#                     "host": proxy_config['host'],
#                     "port": int(proxy_config['port']),
#                     "username": proxy_config.get('username', ''),
#                     "password": proxy_config.get('password', '')
#                 }
#                 gl.changeProfileProxy(profile_id, proxy_data)
#                 print(f"🔄 Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"⚠️ Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("🔄 User agent updated to latest")
#         except Exception as e:
#             print(f"⚠️ User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"❌ Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
        
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
            
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
            
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
            
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
            
#             Date.prototype.getTimezoneOffset = () => -330;
            
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
        
#         print("✅ Stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with Google searches and portfolio visit"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
        
#         # First tab: Google search for 'ishanprotfolio'
#         context = page.context
#         search_page = context.new_page()
#         search_url = f"{GOOGLE_SEARCH_BASE}{SEARCH_TERM}"
#         print(f"🌐 Tab 1: Google search: {search_url}")
#         search_page.goto(search_url)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(search_page)
        
#         # Second tab: Google search for portfolio URL and navigate to it
#         portfolio_search_page = context.new_page()
#         portfolio_search_url = f"{GOOGLE_SEARCH_BASE}{PORTFOLIO_URL}"
#         print(f"🌐 Tab 2: Google search: {portfolio_search_url}")
#         portfolio_search_page.goto(portfolio_search_url)
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(portfolio_search_page)
        
#         # Click on portfolio link in search results
#         try:
#             portfolio_link = portfolio_search_page.locator(f"a[href*='{PORTFOLIO_URL}']").first
#             if portfolio_link.is_visible():
#                 print(f"🌐 Tab 2: Navigating to {PORTFOLIO_URL}")
#                 portfolio_link.click()
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#                 perform_light_interaction(portfolio_search_page)
#         except Exception as e:
#             print(f"⚠️ Portfolio link click error: {e}")
        
#         # Close tabs
#         search_page.close()
#         portfolio_search_page.close()
        
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
        
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         elements = page.locator("a, button").all()[:3]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.2))
                
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def perform_random_page_click(page: Page):
#     """Perform a random click on visible elements after page load"""
#     try:
#         print("🖱️ Attempting random click on page...")
        
#         # Wait for page to fully load
#         page.wait_for_load_state("networkidle", timeout=10000)
        
#         # Get all clickable elements (links, buttons, etc.)
#         clickable_elements = page.locator("a, button, [role='button'], input[type='button'], input[type='submit']").all()
#         visible_elements = [el for el in clickable_elements if el.is_visible() and el.is_enabled()]
        
#         if visible_elements:
#             random_element = random.choice(visible_elements)
#             try:
#                 element_text = random_element.inner_text()[:50] or "Unknown element"
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.5))
#                 random_element.click()
#                 print(f"✅ Randomly clicked: {element_text}")
#                 time.sleep(random.uniform(2, 5))  # Wait after click
#                 return element_text
#             except Exception as e:
#                 print(f"⚠️ Random click error: {e}")
#                 return None
#         else:
#             print("⚠️ No visible clickable elements found")
#             return None
            
#     except Exception as e:
#         print(f"⚠️ Random page click error: {e}")
#         return None

# def ultimate_human_browsing(page: Page, profile_name: str):
#     """Human-like browsing behavior with random page click"""
#     try:
#         print("🎭 Starting human behavior simulation...")
        
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         page.goto(TARGET_URL)
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             return True, None
        
#         try:
#             page.wait_for_selector("body", timeout=10000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         # Perform random click on page
#         clicked_element = perform_random_page_click(page)
        
#         # Log the profile and click details
#         logging.info(f"{profile_name}, Clicked Element: {clicked_element or 'None'}")
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         while time.time() - start_time < human_time:
#             action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#             execute_human_action(page, action)
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True, clicked_element
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         logging.info(f"{profile_name}, Error: {str(e)}")
#         return False, None

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         challenge_indicators = ['captcha', 'robot', 'verify', 'challenge']
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             handle_captcha_page(page)
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
        
#         button_selectors = ["button", "[role='button']", ".button"]
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible() and element.is_enabled():
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'verify']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
#                             element.hover()
#                             time.sleep(random.uniform(1, 2))
#                             element.click()
#                             time.sleep(random.uniform(2, 4))
#                             return
#             except:
#                 continue
        
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(4, 8))
        
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 200)
#             page.evaluate(f"""
#                 window.scrollBy({{
#                     top: {scroll_distance},
#                     left: 0,
#                     behavior: 'smooth'
#                 }});
#             """)
#             time.sleep(random.uniform(0.8, 1.5))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a").all()[:4]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible():
#                         element.hover()
#                         time.sleep(random.uniform(0.4, 1))
                
#         elif action == 'reading_pause':
#             time.sleep(random.uniform(1.5, 4))
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION AND RANDOM CLICKS ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     pre_navigation_warmup(page)
#                     success, clicked_element = ultimate_human_browsing(page, profile_name)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS! Clicked: {clicked_element or 'None'}")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#                 logging.info(f"{profile_name}, Error: Browser start failed")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
#             logging.info(f"{profile_name}, Error: Profile creation failed")
        
#         # Random delay between visits
#         inter_visit_delay = random.uniform(*INTER_VISIT_DELAY)
#         print(f"⏳ Inter-visit delay: {inter_visit_delay:.1f}s")
#         time.sleep(inter_visit_delay)
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION AND RANDOM CLICKS")
#     print("Stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")


# import time
# import random
# import logging
# import os
# from datetime import datetime
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# SEARCH_TERM = "ishanprotfolio"
# PORTFOLIO_URL = "https://www.ishanprotpholio.co.in/"
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"

# # STEALTH SETTINGS
# TOTAL_PROFILES = 10  # Reduced for testing
# PRE_NAVIGATION_DELAY = (8, 15)
# HUMAN_BEHAVIOR_TIME = (15, 30)
# PAGE_LOAD_PATIENCE = (4, 8)
# INTER_VISIT_DELAY = (20, 40)

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # Setup logging
# LOG_FILE = os.path.join(r"D:\streakads", "profile_visits.log")
# try:
#     # Ensure log directory is writable
#     os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
#     logging.basicConfig(
#         filename=LOG_FILE,
#         level=logging.INFO,
#         format='%(asctime)s - Profile: %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S'
#     )
#     # Test log entry to confirm file creation
#     logging.info("Script started")
# except PermissionError as e:
#     print(f"❌ Cannot create log file at {LOG_FILE}: {e}")
#     exit(1)

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None, max_retries=3):
#     """Create stealth profile with retry mechanism"""
#     for attempt in range(1, max_retries + 1):
#         try:
#             gl = GoLogin({"token": TOKEN})
#             print(f"🥷 Creating stealth profile: {profile_name} (Attempt {attempt}/{max_retries})")
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name
#             })
            
#             if not profile or 'id' not in profile:
#                 print(f"❌ Profile creation failed: Invalid response - {profile}")
#                 logging.info(f"{profile_name}, Error: Invalid profile response - {profile}")
#                 if attempt < max_retries:
#                     time.sleep(random.uniform(2, 5))
#                     continue
#                 return None
                
#             profile_id = profile['id']
#             print(f"✅ Profile created: {profile_id}")
            
#             if proxy_config:
#                 try:
#                     proxy_data = {
#                         "mode": proxy_config['type'],
#                         "host": proxy_config['host'],
#                         "port": int(proxy_config['port']),
#                         "username": proxy_config.get('username', ''),
#                         "password": proxy_config.get('password', '')
#                     }
#                     gl.changeProfileProxy(profile_id, proxy_data)
#                     print(f"🔄 Proxy configured: {proxy_config['host']}")
#                 except Exception as e:
#                     print(f"⚠️ Proxy setup warning: {e}. Continuing without proxy.")
#                     logging.info(f"{profile_name}, Warning: Proxy setup failed - {e}")
            
#             try:
#                 gl.updateUserAgentToLatestBrowser([profile_id])
#                 print("🔄 User agent updated to latest")
#             except Exception as e:
#                 print(f"⚠️ User agent update warning: {e}")
            
#             return profile_id
            
#         except Exception as e:
#             print(f"❌ Profile creation error: {e}")
#             logging.info(f"{profile_name}, Error: Profile creation failed - {e}")
#             if attempt < max_retries:
#                 time.sleep(random.uniform(2, 5))
#                 continue
#             return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         logging.info(f"Profile ID: {profile_id}, Error: Browser start failed - {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
#             Date.prototype.getTimezoneOffset = () => -330;
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
#         print("✅ Stealth protection active")
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with Google searches and portfolio visit"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
#         context = page.context
#         search_page = context.new_page()
#         search_url = f"{GOOGLE_SEARCH_BASE}{SEARCH_TERM}"
#         print(f"🌐 Tab 1: Google search: {search_url}")
#         search_page.goto(search_url, wait_until="domcontentloaded")
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(search_page)
        
#         portfolio_search_page = context.new_page()
#         portfolio_search_url = f"{GOOGLE_SEARCH_BASE}{PORTFOLIO_URL}"
#         print(f"🌐 Tab 2: Google search: {portfolio_search_url}")
#         portfolio_search_page.goto(portfolio_search_url, wait_until="domcontentloaded")
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(portfolio_search_page)
        
#         try:
#             portfolio_link = portfolio_search_page.locator(f"a[href*='{PORTFOLIO_URL}']").first
#             if portfolio_link.is_visible(timeout=5000):
#                 print(f"🌐 Tab 2: Navigating to {PORTFOLIO_URL}")
#                 portfolio_link.click()
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#                 perform_light_interaction(portfolio_search_page)
#         except Exception as e:
#             print(f"⚠️ Portfolio link click error: {e}")
        
#         search_page.close()
#         portfolio_search_page.close()
        
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions with retry"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         elements = page.locator("a, button").all()[:5]
#         if elements:
#             for _ in range(3):  # Retry up to 3 times
#                 random_element = random.choice(elements)
#                 if random_element.is_visible(timeout=5000):
#                     try:
#                         random_element.scroll_into_view_if_needed(timeout=5000)
#                         random_element.hover(timeout=5000)
#                         time.sleep(random.uniform(0.5, 1.2))
#                         break
#                     except Exception as e:
#                         print(f"⚠️ Hover attempt failed: {e}")
#                         continue
#                 else:
#                     print("⚠️ Element not visible, trying another")
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def perform_random_page_click(page: Page):
#     """Perform a random click anywhere on the page with human-like behavior"""
#     try:
#         print("🖱️ Attempting random click on page...")
        
#         # Wait for page to load content
#         page.wait_for_load_state("domcontentloaded", timeout=15000)
        
#         # Try clicking a visible element first
#         clickable_elements = page.locator("a, button, [role='button'], input, div[onclick]").all()
#         visible_elements = [el for el in clickable_elements if el.is_visible(timeout=5000) and el.is_enabled(timeout=5000)]
        
#         if visible_elements and random.random() < 0.7:  # 70% chance to click an element
#             random_element = random.choice(visible_elements)
#             try:
#                 element_text = random_element.inner_text()[:50] or "Unknown element"
#                 random_element.scroll_into_view_if_needed(timeout=5000)
#                 random_element.hover(timeout=5000)
#                 time.sleep(random.uniform(0.5, 1.5))
#                 random_element.click(timeout=5000)
#                 print(f"✅ Randomly clicked element: {element_text}")
#                 return element_text
#             except Exception as e:
#                 print(f"⚠️ Element click error: {e}")
        
#         # Fallback: Click at random coordinates
#         try:
#             viewport = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
#             x = random.randint(50, viewport['width'] - 50)  # Avoid edges
#             y = random.randint(50, viewport['height'] - 50)
#             print(f"🖱️ Clicking at random coordinates: ({x}, {y})")
#             page.mouse.move(x, y, steps=10)  # Smooth mouse movement
#             time.sleep(random.uniform(0.3, 0.8))
#             page.mouse.click(x, y)
#             print("✅ Random coordinate click performed")
#             return f"Coordinates ({x}, {y})"
#         except Exception as e:
#             print(f"⚠️ Random coordinate click error: {e}")
#             return None
            
#     except Exception as e:
#         print(f"⚠️ Random page click error: {e}")
#         return None

# def ultimate_human_browsing(page: Page, profile_name: str):
#     """Human-like browsing behavior with random actions"""
#     try:
#         print("🎭 Starting human behavior simulation...")
        
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         page.goto(TARGET_URL, wait_until="domcontentloaded")
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             return True, None
        
#         try:
#             page.wait_for_selector("body", timeout=10000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         clicked_element = perform_random_page_click(page)
        
#         logging.info(f"{profile_name}, Clicked Element: {clicked_element or 'None'}")
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         actions = ['realistic_scroll', 'mouse_trail', 'reading_pause', 'random_hover']
#         while time.time() - start_time < human_time:
#             action = random.choice(actions)
#             execute_human_action(page, action)
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True, clicked_element
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         logging.info(f"{profile_name}, Error: {str(e)}")
#         return False, None

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         challenge_indicators = ['captcha', 'robot', 'verify', 'challenge']
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             handle_captcha_page(page)
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
#         button_selectors = ["button", "[role='button']", ".button"]
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible(timeout=5000) and element.is_enabled(timeout=5000):
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'verify']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
#                             element.scroll_into_view_if_needed(timeout=5000)
#                             element.hover(timeout=5000)
#                             time.sleep(random.uniform(1, 2))
#                             element.click(timeout=5000)
#                             time.sleep(random.uniform(2, 4))
#                             return
#             except:
#                 continue
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(4, 8))
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 400)
#             direction = random.choice(['down', 'up'])
#             scroll_top = f"window.scrollBy({{top: {'-' if direction == 'up' else ''}{scroll_distance}, behavior: 'smooth'}});"
#             page.evaluate(scroll_top)
#             print(f"🖱️ Scrolled {direction} by {scroll_distance}px")
#             time.sleep(random.uniform(0.8, 1.5))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div, a, button, span").all()[:5]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible(timeout=5000):
#                         element.scroll_into_view_if_needed(timeout=5000)
#                         element.hover(timeout=5000)
#                         print("🖱️ Hovered over element")
#                         time.sleep(random.uniform(0.4, 1))
                
#         elif action == 'random_hover':
#             viewport = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
#             x = random.randint(50, viewport['width'] - 50)
#             y = random.randint(50, viewport['height'] - 50)
#             page.mouse.move(x, y, steps=10)
#             print(f"🖱️ Moved mouse to ({x}, {y})")
#             time.sleep(random.uniform(0.3, 0.8))
                
#         elif action == 'reading_pause':
#             pause_time = random.uniform(1.5, 4)
#             print(f"⏳ Paused for {pause_time:.1f}s")
#             time.sleep(pause_time)
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION AND RANDOM CLICKS ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     pre_navigation_warmup(page)
#                     success, clicked_element = ultimate_human_browsing(page, profile_name)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS! Clicked: {clicked_element or 'None'}")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#                 logging.info(f"{profile_name}, Error: Browser start failed")
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
#             logging.info(f"{profile_name}, Error: Profile creation failed")
        
#         inter_visit_delay = random.uniform(*INTER_VISIT_DELAY)
#         print(f"⏳ Inter-visit delay: {inter_visit_delay:.1f}s")
#         time.sleep(inter_visit_delay)
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION AND RANDOM CLICKS")
#     print("Stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#         logging.info("Main, Error: Script interrupted by user")
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")
#         logging.info(f"Main, Error: Fatal error in stealth test - {e}")






# import time
# import random
# import logging
# import os
# import sys
# from datetime import datetime
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://www.skyscanner.co.in/"
# SEARCH_TERM = "ishanprotfolio"
# PORTFOLIO_URL = "https://www.ishanprotpholio.co.in/"
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"

# # STEALTH SETTINGS
# TOTAL_PROFILES = 1000  # Reduced for testing
# PRE_NAVIGATION_DELAY = (8, 15)
# HUMAN_BEHAVIOR_TIME = (15, 30)
# PAGE_LOAD_PATIENCE = (4, 8)
# INTER_VISIT_DELAY = (20, 40)

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # Setup logging in the script's directory
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# LOG_FILE = os.path.join(SCRIPT_DIR, "profile_visits.log")
# try:
#     logging.basicConfig(
#         filename=LOG_FILE,
#         level=logging.INFO,
#         format='%(asctime)s - Profile: %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S',
#         force=True
#     )
#     # Test log entry to confirm file creation
#     logging.info("Script started")
#     logging.getLogger().handlers[0].flush()  # Ensure initial log is written
#     print(f"📝 Log file created at: {LOG_FILE}")
# except PermissionError as e:
#     print(f"❌ Cannot create log file at {LOG_FILE}: {e}")
#     exit(1)

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None, max_retries=3):
#     """Create stealth profile with retry mechanism"""
#     for attempt in range(1, max_retries + 1):
#         try:
#             gl = GoLogin({"token": TOKEN})
#             print(f"🥷 Creating stealth profile: {profile_name} (Attempt {attempt}/{max_retries})")
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name
#             })
            
#             if not profile or 'id' not in profile:
#                 print(f"❌ Profile creation failed: Invalid response - {profile}")
#                 logging.info(f"{profile_name}, Error: Invalid profile response - {profile}")
#                 logging.getLogger().handlers[0].flush()
#                 if attempt < max_retries:
#                     time.sleep(random.uniform(2, 5))
#                     continue
#                 return None
                
#             profile_id = profile['id']
#             print(f"✅ Profile created: {profile_id}")
            
#             if proxy_config:
#                 try:
#                     proxy_data = {
#                         "mode": proxy_config['type'],
#                         "host": proxy_config['host'],
#                         "port": int(proxy_config['port']),
#                         "username": proxy_config.get('username', ''),
#                         "password": proxy_config.get('password', '')
#                     }
#                     gl.changeProfileProxy(profile_id, proxy_data)
#                     print(f"🔄 Proxy configured: {proxy_config['host']}")
#                 except Exception as e:
#                     print(f"⚠️ Proxy setup warning: {e}. Continuing without proxy.")
#                     logging.info(f"{profile_name}, Warning: Proxy setup failed - {e}")
#                     logging.getLogger().handlers[0].flush()
            
#             try:
#                 gl.updateUserAgentToLatestBrowser([profile_id])
#                 print("🔄 User agent updated to latest")
#             except Exception as e:
#                 print(f"⚠️ User agent update warning: {e}")
            
#             return profile_id
            
#         except Exception as e:
#             print(f"❌ Profile creation error: {e}")
#             logging.info(f"{profile_name}, Error: Profile creation failed - {e}")
#             logging.getLogger().handlers[0].flush()
#             if attempt < max_retries:
#                 time.sleep(random.uniform(2, 5))
#                 continue
#             return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         logging.info(f"Profile ID: {profile_id}, Error: Browser start failed - {e}")
#         logging.getLogger().handlers[0].flush()
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
#             Date.prototype.getTimezoneOffset = () => -330;
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
#         print("✅ Stealth protection active")
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with Google searches and portfolio visit"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
#         context = page.context
#         search_page = context.new_page()
#         search_url = f"{GOOGLE_SEARCH_BASE}{SEARCH_TERM}"
#         print(f"🌐 Tab 1: Google search: {search_url}")
#         search_page.goto(search_url, wait_until="domcontentloaded")
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(search_page)
        
#         portfolio_search_page = context.new_page()
#         portfolio_search_url = f"{GOOGLE_SEARCH_BASE}{PORTFOLIO_URL}"
#         print(f"🌐 Tab 2: Google search: {portfolio_search_url}")
#         portfolio_search_page.goto(portfolio_search_url, wait_until="domcontentloaded")
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(portfolio_search_page)
        
#         try:
#             portfolio_link = portfolio_search_page.locator(f"a[href*='{PORTFOLIO_URL}']").first
#             if portfolio_link.is_visible(timeout=5000):
#                 print(f"🌐 Tab 2: Navigating to {PORTFOLIO_URL}")
#                 portfolio_link.click(timeout=5000)
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#                 perform_light_interaction(portfolio_search_page)
#         except Exception as e:
#             print(f"⚠️ Portfolio link click error: {e}")
        
#         search_page.close()
#         portfolio_search_page.close()
        
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions with retry"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         # Broader selector to avoid overlays
#         elements = page.locator("a:not([role='navigation']), button:not([role='navigation'])").all()[:5]
#         if elements:
#             for _ in range(3):
#                 random_element = random.choice(elements)
#                 try:
#                     if random_element.is_visible(timeout=5000):
#                         random_element.scroll_into_view_if_needed(timeout=5000)
#                         random_element.hover(timeout=5000)
#                         print("🖱️ Hovered over element")
#                         time.sleep(random.uniform(0.5, 1.2))
#                         break
#                 except Exception as e:
#                     print(f"⚠️ Hover attempt failed: {e}")
#                     continue
#         else:
#             print("⚠️ No suitable elements for interaction")
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def perform_random_page_click(page: Page):
#     """Perform a random click anywhere on the page with human-like behavior"""
#     try:
#         print("🖱️ Attempting random click on page...")
        
#         # Wait for page to load content
#         page.wait_for_load_state("domcontentloaded", timeout=15000)
        
#         # Try clicking a visible element first
#         clickable_elements = page.locator("a, button, [role='button'], input, div[onclick], span[onclick]").all()
#         visible_elements = [el for el in clickable_elements if el.is_visible(timeout=5000)]
        
#         if visible_elements and random.random() < 0.7:
#             for _ in range(3):  # Retry up to 3 times
#                 random_element = random.choice(visible_elements)
#                 try:
#                     element_text = random_element.inner_text()[:50] or "Unknown element"
#                     random_element.scroll_into_view_if_needed(timeout=5000)
#                     random_element.hover(timeout=5000)
#                     time.sleep(random.uniform(0.5, 1.5))
#                     random_element.click(timeout=5000, force=True)  # Force click to bypass restrictions
#                     print(f"✅ Randomly clicked element: {element_text}")
#                     return element_text
#                 except Exception as e:
#                     print(f"⚠️ Element click error: {e}")
#                     continue
        
#         # Fallback: Click at random coordinates
#         try:
#             viewport = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
#             x = random.randint(50, viewport['width'] - 50)
#             y = random.randint(50, viewport['height'] - 50)
#             print(f"🖱️ Clicking at random coordinates: ({x}, {y})")
#             page.mouse.move(x, y, steps=10)
#             time.sleep(random.uniform(0.3, 0.8))
#             page.mouse.click(x, y)
#             print("✅ Random coordinate click performed")
#             return f"Coordinates ({x}, {y})"
#         except Exception as e:
#             print(f"⚠️ Random coordinate click error: {e}")
#             return None
            
#     except Exception as e:
#         print(f"⚠️ Random page click error: {e}")
#         return None

# def ultimate_human_browsing(page: Page, profile_name: str):
#     """Human-like browsing behavior with random actions"""
#     try:
#         print("🎭 Starting human behavior simulation...")
        
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         page.goto(TARGET_URL, wait_until="domcontentloaded")
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             return True, None
        
#         try:
#             page.wait_for_selector("body", timeout=10000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         clicked_element = perform_random_page_click(page)
        
#         logging.info(f"{profile_name}, Clicked Element: {clicked_element or 'None'}")
#         logging.getLogger().handlers[0].flush()
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         actions = ['realistic_scroll', 'mouse_trail', 'random_hover', 'reading_pause', 'random_drag']
#         while time.time() - start_time < human_time:
#             action = random.choice(actions)
#             execute_human_action(page, action)
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True, clicked_element
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         logging.info(f"{profile_name}, Error: {str(e)}")
#         logging.getLogger().handlers[0].flush()
#         return False, None

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         challenge_indicators = ['captcha', 'robot', 'verify', 'challenge']
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             handle_captcha_page(page)
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
#         button_selectors = ["button", "[role='button']", ".button"]
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible(timeout=5000) and element.is_enabled(timeout=5000):
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'verify']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
#                             element.scroll_into_view_if_needed(timeout=5000)
#                             element.hover(timeout=5000)
#                             time.sleep(random.uniform(1, 2))
#                             element.click(timeout=5000, force=True)
#                             time.sleep(random.uniform(2, 4))
#                             return
#             except:
#                 continue
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(4, 8))
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 400)
#             direction = random.choice(['down', 'up'])
#             scroll_top = f"window.scrollBy({{top: {'-' if direction == 'up' else ''}{scroll_distance}, behavior: 'smooth'}});"
#             page.evaluate(scroll_top)
#             print(f"🖱️ Scrolled {direction} by {scroll_distance}px")
#             time.sleep(random.uniform(0.8, 1.5))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div:not([role='navigation']), a:not([role='navigation']), button, span").all()[:5]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible(timeout=5000):
#                         element.scroll_into_view_if_needed(timeout=5000)
#                         element.hover(timeout=5000)
#                         print("🖱️ Hovered over element")
#                         time.sleep(random.uniform(0.4, 1))
                
#         elif action == 'random_hover':
#             viewport = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
#             x = random.randint(50, viewport['width'] - 50)
#             y = random.randint(50, viewport['height'] - 50)
#             page.mouse.move(x, y, steps=10)
#             print(f"🖱️ Moved mouse to ({x}, {y})")
#             time.sleep(random.uniform(0.3, 0.8))
                
#         elif action == 'random_drag':
#             viewport = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
#             x1 = random.randint(50, viewport['width'] - 50)
#             y1 = random.randint(50, viewport['height'] - 50)
#             x2 = x1 + random.randint(-100, 100)
#             y2 = y1 + random.randint(-100, 100)
#             page.mouse.move(x1, y1, steps=10)
#             page.mouse.down()
#             page.mouse.move(x2, y2, steps=10)
#             page.mouse.up()
#             print(f"🖱️ Dragged mouse from ({x1}, {y1}) to ({x2}, {y2})")
#             time.sleep(random.uniform(0.5, 1.2))
                
#         elif action == 'reading_pause':
#             pause_time = random.uniform(1.5, 4)
#             print(f"⏳ Paused for {pause_time:.1f}s")
#             time.sleep(pause_time)
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION AND RANDOM CLICKS ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     pre_navigation_warmup(page)
#                     success, clicked_element = ultimate_human_browsing(page, profile_name)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS! Clicked: {clicked_element or 'None'}")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#                 logging.info(f"{profile_name}, Error: Browser start failed")
#                 logging.getLogger().handlers[0].flush()
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
#             logging.info(f"{profile_name}, Error: Profile creation failed")
#             logging.getLogger().handlers[0].flush()
        
#         inter_visit_delay = random.uniform(*INTER_VISIT_DELAY)
#         print(f"⏳ Inter-visit delay: {inter_visit_delay:.1f}s")
#         time.sleep(inter_visit_delay)
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")
#     finally:
#         logging.getLogger().handlers[0].flush()

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION AND RANDOM CLICKS")
#     print("Stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         logging.info("Main, Error: GoLogin not available")
#         logging.getLogger().handlers[0].flush()
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#         logging.info("Main, Error: Script interrupted by user")
#         logging.getLogger().handlers[0].flush()
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")
#         logging.info(f"Main, Error: Fatal error in stealth test - {e}")
#         logging.getLogger().handlers[0].flush()




# import time
# import random
# import logging
# import os
# import sys
# from datetime import datetime
# from playwright.sync_api import sync_playwright, TimeoutError
# from playwright.sync_api import Page, Browser, Playwright

# try:
#     from gologin import GoLogin
#     GOLOGIN_AVAILABLE = True
# except ImportError:
#     print("Install GoLogin: pip install gologin")
#     exit(1)

# # ---------- CONFIG ----------
# TARGET_URL = "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc"
# SEARCH_TERM = "ishanprotfolio"
# PORTFOLIO_URL = "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc"
# GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# TOKEN = "CHANGE_ME_TOKEN"

# # STEALTH SETTINGS
# TOTAL_PROFILES = 1000  # Reduced for testing
# PRE_NAVIGATION_DELAY = (8, 15)
# HUMAN_BEHAVIOR_TIME = (15, 30)
# PAGE_LOAD_PATIENCE = (4, 8)
# INTER_VISIT_DELAY = (20, 40)

# # Proxy list
# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # Setup logging in the executable's directory
# EXE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
# LOG_FILE = os.path.join(EXE_DIR, "profile_visits.log")
# try:
#     logging.basicConfig(
#         filename=LOG_FILE,
#         level=logging.INFO,
#         format='%(asctime)s - Profile: %(message)s',
#         datefmt='%Y-%m-%d %H:%M:%S',
#         force=True
#     )
#     # Test log entry to confirm file creation
#     logging.info("Script started")
#     logging.getLogger().handlers[0].flush()  # Ensure initial log is written
#     print(f"📝 Log file created at: {LOG_FILE}")
# except PermissionError as e:
#     print(f"❌ Cannot create log file at {LOG_FILE}: {e}")
#     exit(1)

# def parse_proxy_string(s: str):
#     """Parse proxy string"""
#     s = s.strip()
#     parts = s.split()
#     proto = parts[0].lower() if len(parts) > 1 else "socks5"
#     main = parts[1] if len(parts) > 1 else parts[0]
    
#     segs = main.split(":", 3)
#     if len(segs) == 4:
#         host, port, username, password = segs
#         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
#     return None

# def create_ultimate_stealth_profile(profile_name, proxy_config=None, max_retries=3):
#     """Create stealth profile with retry mechanism"""
#     for attempt in range(1, max_retries + 1):
#         try:
#             gl = GoLogin({"token": TOKEN})
#             print(f"🥷 Creating stealth profile: {profile_name} (Attempt {attempt}/{max_retries})")
            
#             profile = gl.createProfileRandomFingerprint({
#                 "os": random.choice(["win", "mac"]),
#                 "name": profile_name
#             })
            
#             if not profile or 'id' not in profile:
#                 print(f"❌ Profile creation failed: Invalid response - {profile}")
#                 logging.info(f"{profile_name}, Error: Invalid profile response - {profile}")
#                 logging.getLogger().handlers[0].flush()
#                 if attempt < max_retries:
#                     time.sleep(random.uniform(2, 5))
#                     continue
#                 return None
                
#             profile_id = profile['id']
#             print(f"✅ Profile created: {profile_id}")
            
#             if proxy_config:
#                 try:
#                     proxy_data = {
#                         "mode": proxy_config['type'],
#                         "host": proxy_config['host'],
#                         "port": int(proxy_config['port']),
#                         "username": proxy_config.get('username', ''),
#                         "password": proxy_config.get('password', '')
#                     }
#                     gl.changeProfileProxy(profile_id, proxy_data)
#                     print(f"🔄 Proxy configured: {proxy_config['host']}")
#                 except Exception as e:
#                     print(f"⚠️ Proxy setup warning: {e}. Continuing without proxy.")
#                     logging.info(f"{profile_name}, Warning: Proxy setup failed - {e}")
#                     logging.getLogger().handlers[0].flush()
            
#             try:
#                 gl.updateUserAgentToLatestBrowser([profile_id])
#                 print("🔄 User agent updated to latest")
#             except Exception as e:
#                 print(f"⚠️ User agent update warning: {e}")
            
#             return profile_id
            
#         except Exception as e:
#             print(f"❌ Profile creation error: {e}")
#             logging.info(f"{profile_name}, Error: Profile creation failed - {e}")
#             logging.getLogger().handlers[0].flush()
#             if attempt < max_retries:
#                 time.sleep(random.uniform(2, 5))
#                 continue
#             return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"🚀 Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"🔌 Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"❌ Browser start error: {e}")
#         logging.info(f"Profile ID: {profile_id}, Error: Browser start failed - {e}")
#         logging.getLogger().handlers[0].flush()
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts"""
#     try:
#         print("🛡️ Injecting stealth protection...")
#         page.evaluate("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             delete window.webdriver;
#             window.chrome = {
#                 runtime: {
#                     onConnect: {addListener: () => {}},
#                     onMessage: {addListener: () => {}},
#                 }
#             };
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [{
#                     description: "Portable Document Format",
#                     filename: "internal-pdf-viewer",
#                     name: "Chrome PDF Plugin"
#                 }]
#             });
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en', 'hi-IN'],
#             });
#             Date.prototype.getTimezoneOffset = () => -330;
#             Object.defineProperty(screen, 'width', {get: () => 1920});
#             Object.defineProperty(screen, 'height', {get: () => 1080});
#         """)
#         print("✅ Stealth protection active")
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def pre_navigation_warmup(page: Page):
#     """Warm up browser with Google searches and portfolio visit"""
#     try:
#         print("🔥 Starting pre-navigation warmup...")
#         context = page.context
#         search_page = context.new_page()
#         search_url = f"{GOOGLE_SEARCH_BASE}{SEARCH_TERM}"
#         print(f"🌐 Tab 1: Google search: {search_url}")
#         search_page.goto(search_url, wait_until="domcontentloaded")
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(search_page)
        
#         portfolio_search_page = context.new_page()
#         portfolio_search_url = f"{GOOGLE_SEARCH_BASE}{PORTFOLIO_URL}"
#         print(f"🌐 Tab 2: Google search: {portfolio_search_url}")
#         portfolio_search_page.goto(portfolio_search_url, wait_until="domcontentloaded")
#         wait_time = random.uniform(3, 5)
#         time.sleep(wait_time)
#         perform_light_interaction(portfolio_search_page)
        
#         try:
#             portfolio_link = portfolio_search_page.locator(f"a[href*='{PORTFOLIO_URL}']").first
#             if portfolio_link.is_visible(timeout=5000):
#                 print(f"🌐 Tab 2: Navigating to {PORTFOLIO_URL}")
#                 portfolio_link.click(timeout=5000)
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#                 perform_light_interaction(portfolio_search_page)
#         except Exception as e:
#             print(f"⚠️ Portfolio link click error: {e}")
        
#         search_page.close()
#         portfolio_search_page.close()
        
#         final_delay = random.uniform(*PRE_NAVIGATION_DELAY)
#         print(f"🎯 Final preparation: {final_delay:.1f}s before target site")
#         time.sleep(final_delay)
#     except Exception as e:
#         print(f"⚠️ Warmup warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions with retry"""
#     try:
#         scroll_distance = random.randint(100, 250)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         # Broader selector to avoid overlays
#         elements = page.locator("a:not([role='navigation']), button:not([role='navigation'])").all()[:5]
#         if elements:
#             for _ in range(3):
#                 random_element = random.choice(elements)
#                 try:
#                     if random_element.is_visible(timeout=5000):
#                         random_element.scroll_into_view_if_needed(timeout=5000)
#                         random_element.hover(timeout=5000)
#                         print("🖱️ Hovered over element")
#                         time.sleep(random.uniform(0.5, 1.2))
#                         break
#                 except Exception as e:
#                     print(f"⚠️ Hover attempt failed: {e}")
#                     continue
#         else:
#             print("⚠️ No suitable elements for interaction")
#     except Exception as e:
#         print(f"⚠️ Light interaction warning: {e}")

# def perform_random_page_click(page: Page):
#     """Perform a random click anywhere on the page with human-like behavior"""
#     try:
#         print("🖱️ Attempting random click on page...")
        
#         # Wait for page to load content
#         page.wait_for_load_state("domcontentloaded", timeout=15000)
        
#         # Try clicking a visible element first
#         clickable_elements = page.locator("a, button, [role='button'], input, div[onclick], span[onclick]").all()
#         visible_elements = [el for el in clickable_elements if el.is_visible(timeout=5000)]
        
#         if visible_elements and random.random() < 0.7:
#             for _ in range(3):  # Retry up to 3 times
#                 random_element = random.choice(visible_elements)
#                 try:
#                     element_text = random_element.inner_text()[:50] or "Unknown element"
#                     random_element.scroll_into_view_if_needed(timeout=5000)
#                     random_element.hover(timeout=5000)
#                     time.sleep(random.uniform(0.5, 1.5))
#                     random_element.click(timeout=5000, force=True)  # Force click to bypass restrictions
#                     print(f"✅ Randomly clicked element: {element_text}")
#                     return element_text
#                 except Exception as e:
#                     print(f"⚠️ Element click error: {e}")
#                     continue
        
#         # Fallback: Click at random coordinates
#         try:
#             viewport = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
#             x = random.randint(50, viewport['width'] - 50)
#             y = random.randint(50, viewport['height'] - 50)
#             print(f"🖱️ Clicking at random coordinates: ({x}, {y})")
#             page.mouse.move(x, y, steps=10)
#             time.sleep(random.uniform(0.3, 0.8))
#             page.mouse.click(x, y)
#             print("✅ Random coordinate click performed")
#             return f"Coordinates ({x}, {y})"
#         except Exception as e:
#             print(f"⚠️ Random coordinate click error: {e}")
#             return None
            
#     except Exception as e:
#         print(f"⚠️ Random page click error: {e}")
#         return None

# def ultimate_human_browsing(page: Page, profile_name: str):
#     """Human-like browsing behavior with random actions"""
#     try:
#         print("🎭 Starting human behavior simulation...")
        
#         print(f"🎯 Navigating to target: {TARGET_URL}")
#         page.goto(TARGET_URL, wait_until="domcontentloaded")
        
#         page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#         print(f"⏳ Patient page loading: {page_wait:.1f}s")
#         time.sleep(page_wait)
        
#         if detect_and_handle_challenges(page):
#             return True, None
        
#         try:
#             page.wait_for_selector("body", timeout=10000)
#             print("📄 Page elements detected")
#         except TimeoutError:
#             print("⚠️ Page load timeout, continuing...")
        
#         clicked_element = perform_random_page_click(page)
        
#         logging.info(f"{profile_name}, Clicked Element: {clicked_element or 'None'}")
#         logging.getLogger().handlers[0].flush()
        
#         human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#         print(f"🤖 Performing human behavior for {human_time:.1f}s")
        
#         start_time = time.time()
#         actions = ['realistic_scroll', 'mouse_trail', 'random_hover', 'reading_pause', 'random_drag']
#         while time.time() - start_time < human_time:
#             action = random.choice(actions)
#             execute_human_action(page, action)
#             time.sleep(random.uniform(0.8, 2.5))
        
#         print("✅ Human behavior complete")
#         return True, clicked_element
        
#     except Exception as e:
#         print(f"❌ Human browsing error: {e}")
#         logging.info(f"{profile_name}, Error: {str(e)}")
#         logging.getLogger().handlers[0].flush()
#         return False, None

# def detect_and_handle_challenges(page: Page):
#     """Detect and handle CAPTCHA/challenges"""
#     try:
#         current_url = page.url
#         page_source = page.content().lower()
        
#         challenge_indicators = ['captcha', 'robot', 'verify', 'challenge']
#         is_challenge = any(indicator in current_url.lower() or indicator in page_source 
#                           for indicator in challenge_indicators)
        
#         if is_challenge:
#             print("🚨 Challenge detected!")
#             print(f"URL: {current_url}")
#             handle_captcha_page(page)
#             return True
#         else:
#             print("✅ No challenges detected")
#             return False
            
#     except Exception as e:
#         print(f"⚠️ Challenge detection error: {e}")
#         return False

# def handle_captcha_page(page: Page):
#     """Handle CAPTCHA page"""
#     try:
#         print("🧩 Attempting to handle CAPTCHA page...")
#         button_selectors = ["button", "[role='button']", ".button"]
#         for selector in button_selectors:
#             try:
#                 elements = page.locator(selector).all()
#                 for element in elements:
#                     if element.is_visible(timeout=5000) and element.is_enabled(timeout=5000):
#                         text = element.inner_text().lower()
#                         if any(word in text for word in ['continue', 'verify']):
#                             print(f"🔄 Found action button: {element.inner_text()}")
#                             element.scroll_into_view_if_needed(timeout=5000)
#                             element.hover(timeout=5000)
#                             time.sleep(random.uniform(1, 2))
#                             element.click(timeout=5000, force=True)
#                             time.sleep(random.uniform(2, 4))
#                             return
#             except:
#                 continue
#         print("⏳ No action buttons found, waiting...")
#         time.sleep(random.uniform(4, 8))
#     except Exception as e:
#         print(f"⚠️ CAPTCHA handling error: {e}")

# def execute_human_action(page: Page, action):
#     """Execute specific human-like action"""
#     try:
#         if action == 'realistic_scroll':
#             scroll_distance = random.randint(100, 400)
#             direction = random.choice(['down', 'up'])
#             scroll_top = f"window.scrollBy({{top: {'-' if direction == 'up' else ''}{scroll_distance}, behavior: 'smooth'}});"
#             page.evaluate(scroll_top)
#             print(f"🖱️ Scrolled {direction} by {scroll_distance}px")
#             time.sleep(random.uniform(0.8, 1.5))
                
#         elif action == 'mouse_trail':
#             elements = page.locator("div:not([role='navigation']), a:not([role='navigation']), button, span").all()[:5]
#             if elements:
#                 for element in random.sample(elements, min(2, len(elements))):
#                     if element.is_visible(timeout=5000):
#                         element.scroll_into_view_if_needed(timeout=5000)
#                         element.hover(timeout=5000)
#                         print("🖱️ Hovered over element")
#                         time.sleep(random.uniform(0.4, 1))
                
#         elif action == 'random_hover':
#             viewport = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
#             x = random.randint(50, viewport['width'] - 50)
#             y = random.randint(50, viewport['height'] - 50)
#             page.mouse.move(x, y, steps=10)
#             print(f"🖱️ Moved mouse to ({x}, {y})")
#             time.sleep(random.uniform(0.3, 0.8))
                
#         elif action == 'random_drag':
#             viewport = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
#             x1 = random.randint(50, viewport['width'] - 50)
#             y1 = random.randint(50, viewport['height'] - 50)
#             x2 = x1 + random.randint(-100, 100)
#             y2 = y1 + random.randint(-100, 100)
#             page.mouse.move(x1, y1, steps=10)
#             page.mouse.down()
#             page.mouse.move(x2, y2, steps=10)
#             page.mouse.up()
#             print(f"🖱️ Dragged mouse from ({x1}, {y1}) to ({x2}, {y2})")
#             time.sleep(random.uniform(0.5, 1.2))
                
#         elif action == 'reading_pause':
#             pause_time = random.uniform(1.5, 4)
#             print(f"⏳ Paused for {pause_time:.1f}s")
#             time.sleep(pause_time)
                
#     except Exception as e:
#         print(f"⚠️ Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     print("🎯 STEALTH MODE WITH COOKIE CONFUSION AND RANDOM CLICKS ACTIVATED")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     pre_navigation_warmup(page)
#                     success, clicked_element = ultimate_human_browsing(page, profile_name)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"🎉 PROFILE {profile_num} - SUCCESS! Clicked: {clicked_element or 'None'}")
#                     else:
#                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(20, 40)
#                     print(f"🕐 Maintaining session: {session_time:.1f}s")
#                     time.sleep(session_time)
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
#                 logging.info(f"{profile_name}, Error: Browser start failed")
#                 logging.getLogger().handlers[0].flush()
#         else:
#             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
#             logging.info(f"{profile_name}, Error: Profile creation failed")
#             logging.getLogger().handlers[0].flush()
        
#         inter_visit_delay = random.uniform(*INTER_VISIT_DELAY)
#         print(f"⏳ Inter-visit delay: {inter_visit_delay:.1f}s")
#         time.sleep(inter_visit_delay)
    
#     print(f"\n🏆 STEALTH TEST COMPLETE!")
#     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     """Clean up browser resources"""
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("🧹 Browser session terminated")
#     except Exception as e:
#         print(f"⚠️ Cleanup warning: {e}")
#     finally:
#         logging.getLogger().handlers[0].flush()

# if __name__ == "__main__":
#     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION AND RANDOM CLICKS")
#     print("Stealth configuration activated")
#     print("=" * 60)
    
#     if not GOLOGIN_AVAILABLE:
#         print("❌ GoLogin not available!")
#         logging.info("Main, Error: GoLogin not available")
#         logging.getLogger().handlers[0].flush()
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\n🛑 Stealth test interrupted")
#         logging.info("Main, Error: Script interrupted by user")
#         logging.getLogger().handlers[0].flush()
#     except Exception as e:
#         print(f"❌ Fatal error in stealth test: {e}")
#         logging.info(f"Main, Error: Fatal error in stealth test - {e}")
#         logging.getLogger().handlers[0].flush()