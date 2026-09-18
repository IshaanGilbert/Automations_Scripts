# # import time
# # import random
# # import uuid
# # from playwright.sync_api import sync_playwright, TimeoutError
# # from playwright.sync_api import Page, Browser, Playwright

# # try:
# #     from gologin import GoLogin
# #     GOLOGIN_AVAILABLE = True
# # except ImportError:
# #     print("Install GoLogin: pip install gologin")
# #     exit(1)

# # # ---------- CONFIG ----------
# # TARGET_URLS = [
# #     "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc",
# #     "https://www.skyscanner.co.in/carhire",
# #     "https://www.skyscanner.co.in/flights",
# #     "https://www.skyscanner.co.in/hotels",
# # ]
# # GOOGLE_SEARCH_BASE = "https://www.google.co.in/search?q="
# # TOKEN = "CHANGE_ME_TOKEN"
# # TOTAL_PROFILES = 1
# # PAGE_LOAD_PATIENCE = (4, 8)  # Page loading patience
# # HUMAN_BEHAVIOR_TIME = (15, 30)  # Human behavior duration

# # # Proxy list
# # PROXY_LIST = [
# #     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# # ]

# # def parse_proxy_string(s: str):
# #     """Parse proxy string"""
# #     s = s.strip()
# #     parts = s.split()
# #     proto = parts[0].lower() if len(parts) > 1 else "socks5"
# #     main = parts[1] if len(parts) > 1 else parts[0]
    
# #     segs = main.split(":", 3)
# #     if len(segs) == 4:
# #         host, port, username, password = segs
# #         return {"type": proto, "host": host, "port": port, "username": username, "password": password}
# #     return None

# # def create_ultimate_stealth_profile(profile_name, proxy_config=None):
# #     """Create stealth profile with enhanced fingerprinting"""
# #     try:
# #         gl = GoLogin({"token": TOKEN})
# #         print(f"🥷 Creating stealth profile: {profile_name}")
        
# #         profile = gl.createProfileRandomFingerprint({
# #             "os": random.choice(["win", "mac"]),
# #             "name": profile_name,
# #             "webgl": {
# #                 "vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
# #                 "renderer": random.choice(["Intel Iris OpenGL Engine", "GeForce GTX 1650/PCIe/SSE2", "Radeon RX 580"])
# #             },
# #             "audioContext": {
# #                 "enable": True,
# #                 "noise": random.uniform(0.0001, 0.0005)
# #             }
# #         })
        
# #         if not profile or 'id' not in profile:
# #             print(f"❌ Profile creation failed: {profile}")
# #             return None
            
# #         profile_id = profile['id']
# #         print(f"✅ Profile created: {profile_id}")
        
# #         if proxy_config:
# #             try:
# #                 proxy_data = {
# #                     "mode": proxy_config['type'],
# #                     "host": proxy_config['host'],
# #                     "port": int(proxy_config['port']),
# #                     "username": proxy_config.get('username', ''),
# #                     "password": proxy_config.get('password', '')
# #                 }
# #                 gl.changeProfileProxy(profile_id, proxy_data)
# #                 print(f"🔄 Proxy configured: {proxy_config['host']}")
# #             except Exception as e:
# #                 print(f"⚠️ Proxy setup warning: {e}")
        
# #         try:
# #             gl.updateUserAgentToLatestBrowser([profile_id])
# #             print("🔄 User agent updated to latest")
# #         except Exception as e:
# #             print(f"⚠️ User agent update warning: {e}")
        
# #         return profile_id
        
# #     except Exception as e:
# #         print(f"❌ Profile creation error: {e}")
# #         return None

# # def start_maximum_stealth_browser(profile_id):
# #     """Start browser with stealth configuration"""
# #     try:
# #         gl = GoLogin({
# #             "token": TOKEN,
# #             "profile_id": profile_id
# #         })
# #         print(f"🚀 Starting stealth browser for: {profile_id}")
# #         debugger_address = gl.start()
# #         print(f"🔌 Browser endpoint: {debugger_address}")
        
# #         wait_time = random.uniform(3, 6)
# #         print(f"⏳ Browser stabilization: {wait_time:.1f}s")
# #         time.sleep(wait_time)
        
# #         pw = sync_playwright().start()
# #         cdp_url = f"http://{debugger_address}"
# #         browser = pw.chromium.connect_over_cdp(cdp_url)
# #         context = browser.contexts[0]
# #         if context.pages:
# #             page = context.pages[0]
# #         else:
# #             page = context.new_page()
        
# #         # Disable third-party cookies and clear initial cookies
# #         context.set_extra_http_headers({
# #             "DNT": "1",
# #             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
# #             "User-Agent": context.pages[0].evaluate("() => navigator.userAgent")
# #         })
# #         context.add_cookies([])  # Clear any initial cookies
# #         context.clear_cookies()  # Ensure fresh state
        
# #         inject_ultimate_stealth(page)
        
# #         return gl, pw, browser, page
        
# #     except Exception as e:
# #         print(f"❌ Browser start error: {e}")
# #         return None, None, None, None

# # def inject_ultimate_stealth(page: Page):
# #     """Inject stealth scripts with enhanced fingerprinting"""
# #     try:
# #         print("🛡️ Injecting stealth protection...")
        
# #         page.evaluate("""
# #             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
# #             delete window.webdriver;
            
# #             window.chrome = {
# #                 runtime: {
# #                     onConnect: {addListener: () => {}},
# #                     onMessage: {addListener: () => {}},
# #                 }
# #             };
            
# #             Object.defineProperty(navigator, 'plugins', {
# #                 get: () => [{
# #                     description: "Portable Document Format",
# #                     filename: "internal-pdf-viewer",
# #                     name: "Chrome PDF Plugin"
# #                 }]
# #             });
            
# #             Object.defineProperty(navigator, 'languages', {
# #                 get: () => ['en-US', 'en', 'hi-IN'],
# #             });
            
# #             Date.prototype.getTimezoneOffset = () => -330;
            
# #             Object.defineProperty(screen, 'width', {get: () => 1920});
# #             Object.defineProperty(screen, 'height', {get: () => 1080});
            
# #             // Spoof WebGL
# #             const getParameter = WebGLRenderingContext.prototype.getParameter;
# #             WebGLRenderingContext.prototype.getParameter = function(parameter) {
# #                 if (parameter === 37446) return 'Intel Inc.';
# #                 if (parameter === 37447) return 'Intel Iris OpenGL Engine';
# #                 return getParameter.apply(this, arguments);
# #             };
            
# #             // Spoof Canvas
# #             const getImageData = HTMLCanvasElement.prototype.getContext('2d').getImageData;
# #             HTMLCanvasElement.prototype.getContext('2d').getImageData = function() {
# #                 const data = getImageData.apply(this, arguments);
# #                 data.data[0] += Math.random() * 0.01; // Add noise
# #                 return data;
# #             };
# #         """)
        
# #         print("✅ Stealth protection active")
        
# #     except Exception as e:
# #         print(f"⚠️ Stealth injection warning: {e}")

# # def perform_light_interaction(page: Page):
# #     """Light human interactions with enhanced mouse and keyboard events"""
# #     try:
# #         # Random scroll
# #         scroll_distance = random.randint(10, 100)
# #         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
# #         time.sleep(random.uniform(0.8, 1.5))
        
# #         # Random mouse movement
# #         page.mouse.move(random.randint(100, 800), random.randint(100, 600))
# #         time.sleep(random.uniform(0.3, 0.7))
        
# #         # Random element interaction
# #         elements = page.locator("a, button, input").all()[:5]
# #         if elements:
# #             random_element = random.choice(elements)
# #             if random_element.is_visible():
# #                 random_element.hover()
# #                 time.sleep(random.uniform(0.5, 1.2))
# #                 random_element.click()
# #                 print("🖱️ Performed random click")
# #                 # Simulate keyboard input if it's an input field
# #                 if random_element.evaluate("el => el.tagName.toLowerCase() === 'input'"):
# #                     random_element.type(random.choice(["search", "flights", "hotels"]), delay=random.uniform(100, 200))
# #                     print("⌨️ Simulated keyboard input")
                
# #     except Exception as e:
# #         print(f"⚠️ Light interaction warning: {e}")

# # def inject_fake_cookies(context):
# #     """Inject dynamic fake cookies to simulate a new user"""
# #     fake_cookies = [
# #         {
# #             "name": random.choice(["session_id", "user_session", "track_id"]),
# #             "value": str(uuid.uuid4()),
# #             "domain": ".skyscanner.co.in",
# #             "path": "/",
# #             "expires": int(time.time()) + random.randint(1800, 7200),  # Random expiry (30 min to 2 hours)
# #             "httpOnly": random.choice([True, False]),
# #             "secure": True
# #         },
# #         {
# #             "name": random.choice(["user_prefs", "settings", "pref_id"]),
# #             "value": f"pref_{random.randint(1000, 9999)}",
# #             "domain": ".skyscanner.co.in",
# #             "path": "/",
# #             "expires": int(time.time()) + random.randint(1800, 7200),
# #             "httpOnly": random.choice([True, False]),
# #             "secure": True
# #         }
# #     ]
# #     context.add_cookies(fake_cookies)
# #     print("🍪 Injected dynamic fake cookies")

# # def ultimate_human_browsing(page: Page):
# #     """Human-like browsing behavior with cookie management and CAPTCHA bypass"""
# #     try:
# #         print("🎭 Starting human behavior simulation...")

# #         # Preserve PerimeterX cookies
# #         preserved_cookies = []

# #         def handle_page_load():
# #             print("🌐 Page load detected")
# #             current_cookies = page.context.cookies()
# #             # Preserve PerimeterX cookies
# #             for cookie in current_cookies:
# #                 if cookie["name"].startswith("_px"):
# #                     preserved_cookies.append(cookie)
# #             page.context.clear_cookies()
# #             # Restore PerimeterX cookies
# #             if preserved_cookies:
# #                 page.context.add_cookies(preserved_cookies)
# #                 print("🍪 Restored PerimeterX cookies")
# #             inject_fake_cookies(page.context)

# #         def handle_response(response):
# #             print(f"🌐 Response received: {response.url}")
# #             if "captcha-v2" in response.url:
# #                 print("🚨 CAPTCHA detected, attempting to handle...")
# #                 try:
# #                     # Wait for the page to fully load
# #                     page.wait_for_selector("body", timeout=10000)
# #                     # Locate the "Press & Hold" button
# #                     press_hold_button = page.locator('p#GsnwQzyXVaaqaGt.RENrWaJpuDbbWBy')
# #                     if press_hold_button.is_visible():
# #                         print("🖱️ Found 'Press & Hold' button, initiating press and hold...")
# #                         # Simulate mouse down to start holding
# #                         press_hold_button.hover()
# #                         page.mouse.down()
# #                         print("🖱️ Holding button...")
# #                         # Monitor for navigation to the target URL
# #                         try:
# #                             # Wait for navigation to any of the target URLs
# #                             page.wait_for_url(lambda url: any(target_url in url for target_url in TARGET_URLS), timeout=30000)
# #                             print("🌐 Redirected back to target URL")
# #                             # Release the mouse
# #                             page.mouse.up()
# #                             print("🖱️ Released button")
# #                         except TimeoutError:
# #                             print("⚠️ Timeout waiting for redirect, releasing button")
# #                             page.mouse.up()
# #                     else:
# #                         print("⚠️ 'Press & Hold' button not found")
# #                 except Exception as e:
# #                     print(f"⚠️ CAPTCHA handling error: {e}")
# #             current_cookies = page.context.cookies()
# #             # Preserve PerimeterX cookies
# #             for cookie in current_cookies:
# #                 if cookie["name"].startswith("_px"):
# #                     preserved_cookies.append(cookie)
# #             page.context.clear_cookies()
# #             if preserved_cookies:
# #                 page.context.add_cookies(preserved_cookies)
# #                 print("🍪 Restored PerimeterX cookies")
# #             inject_fake_cookies(page.context)

# #         # Attach event listeners
# #         page.on("load", handle_page_load)
# #         page.on("response", handle_response)

# #         # Step 1: Type and search first URL
# #         google_url = "https://www.google.co.in/"
# #         print(f"🌐 Navigating to Google: {google_url}")
# #         for attempt in range(3):
# #             try:
# #                 page.goto(google_url, timeout=60000)
# #                 page.wait_for_load_state("networkidle")
# #                 break
# #             except Exception as e:
# #                 print(f"⚠️ Attempt {attempt + 1} failed for {google_url}: {e}")
# #                 if attempt == 2:
# #                     print(f"❌ Failed to load {google_url} after 3 attempts")
# #                     return False
        
# #         # Type first URL in Google search
# #         search_bar = page.locator("input[name='q']")
# #         if search_bar.is_visible():
# #             print(f"🔍 Typing target URL: {TARGET_URLS[0]}")
# #             search_bar.type(TARGET_URLS[0], delay=random.uniform(100, 200))
# #             search_bar.press("Enter")
# #             wait_time = random.uniform(3, 5)
# #             print(f"⏳ Waiting for search results: {wait_time:.1f}s")
# #             time.sleep(wait_time)
        
# #         # Click on the first URL in search results
# #         try:
# #             target_link = page.locator(f"a[href*='{TARGET_URLS[0]}']").first
# #             if target_link.is_visible():
# #                 print(f"🌐 Clicking target link: {TARGET_URLS[0]}")
# #                 target_link.click()
# #                 page.wait_for_load_state("networkidle")
# #                 wait_time = random.uniform(4, 7)
# #                 time.sleep(wait_time)
# #             else:
# #                 print(f"⚠️ Target link not found in search results, navigating directly")
# #                 page.goto(TARGET_URLS[0], timeout=60000)
# #                 page.wait_for_load_state("networkidle")
# #         except Exception as e:
# #             print(f"⚠️ Target link click error: {e}")
# #             page.goto(TARGET_URLS[0], timeout=60000)
# #             page.wait_for_load_state("networkidle")

# #         # Process each URL
# #         for url in TARGET_URLS:
# #             print(f"🎯 Navigating to: {url}")
# #             for attempt in range(3):
# #                 try:
# #                     page.goto(url, timeout=60000)
# #                     page.wait_for_load_state("networkidle")
# #                     break
# #                 except Exception as e:
# #                     print(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
# #                     if attempt == 2:
# #                         print(f"❌ Failed to load {url} after 3 attempts")
# #                         continue
            
# #             page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
# #             print(f"⏳ Patient page loading: {page_wait:.1f}s")
# #             time.sleep(page_wait)
            
# #             try:
# #                 page.wait_for_selector("body", timeout=10000)
# #                 print("📄 Page elements detected")
# #             except TimeoutError:
# #                 print("⚠️ Page load timeout, continuing...")
            
# #             # Scroll page randomly and fully
# #             try:
# #                 page_height = page.evaluate("document.body.scrollHeight")
# #                 current_pos = 0
# #                 while current_pos < page_height:
# #                     scroll_distance = random.randint(10, 100)
# #                     page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
# #                     current_pos += scroll_distance
# #                     time.sleep(random.uniform(0.5, 1.5))
# #                 print("📜 Scrolled full page")
# #             except Exception as e:
# #                 print(f"⚠️ Scroll error: {e}")
            
# #             # Perform human-like behavior
# #             human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
# #             print(f"🤖 Performing human behavior for {human_time:.1f}s")
# #             start_time = time.time()
# #             while time.time() - start_time < human_time:
# #                 action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
# #                 execute_human_action(page, action)
# #                 perform_light_interaction(page)
# #                 time.sleep(random.uniform(0.8, 2.5))
        
# #         print("✅ Human behavior complete")
# #         return True
        
# #     except Exception as e:
# #         print(f"❌ Human browsing error: {e}")
# #         return False
# #     finally:
# #         page.remove_listener("load", handle_page_load)
# #         page.remove_listener("response", handle_response)

# # def execute_human_action(page: Page, action):
# #     """Execute specific human-like action"""
# #     try:
# #         if action == 'realistic_scroll':
# #             scroll_distance = random.randint(10, 100)
# #             page.evaluate(f"""
# #                 window.scrollBy({{
# #                     top: {scroll_distance},
# #                     left: 0,
# #                     behavior: 'smooth'
# #                 }});
# #             """)
# #             time.sleep(random.uniform(0.8, 1.5))
                
# #         elif action == 'mouse_trail':
# #             elements = page.locator("div, a").all()[:4]
# #             if elements:
# #                 for element in random.sample(elements, min(2, len(elements))):
# #                     if element.is_visible():
# #                         element.hover()
# #                         time.sleep(random.uniform(0.4, 1))
                
# #         elif action == 'reading_pause':
# #             time.sleep(random.uniform(1.5, 4))
                
# #     except Exception as e:
# #         print(f"⚠️ Human action error: {e}")

# # def run_ultimate_stealth_test():
# #     """Run the stealth test"""
# #     print("🎯 STEALTH MODE WITH COOKIE CONFUSION ACTIVATED")
# #     print("=" * 60)
    
# #     successful_runs = 0
    
# #     for profile_num in range(1, TOTAL_PROFILES + 1):
# #         print(f"\n🚀 === PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
# #         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
# #         proxy_config = None
# #         if PROXY_LIST:
# #             proxy_str = random.choice(PROXY_LIST)
# #             proxy_config = parse_proxy_string(proxy_str)
        
# #         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
# #         if profile_id:
# #             wait_time = random.uniform(4, 8)
# #             print(f"⏳ Pre-start preparation: {wait_time:.1f}s")
# #             time.sleep(wait_time)
            
# #             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
# #             if page:
# #                 try:
# #                     success = ultimate_human_browsing(page)
                    
# #                     if success:
# #                         successful_runs += 1
# #                         print(f"🎉 PROFILE {profile_num} - SUCCESS!")
# #                     else:
# #                         print(f"❌ PROFILE {profile_num} - FAILED")
                    
# #                     session_time = random.uniform(20, 40)
# #                     print(f"🕐 Maintaining session: {session_time:.1f}s")
# #                     time.sleep(session_time)
                    
# #                 finally:
# #                     cleanup_browser(gl, pw, browser)
# #             else:
# #                 print(f"❌ PROFILE {profile_num} - BROWSER START FAILED")
# #         else:
# #             print(f"❌ PROFILE {profile_num} - PROFILE CREATION FAILED")
    
# #     print(f"\n🏆 STEALTH TEST COMPLETE!")
# #     print(f"📊 Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

# # def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
# #     """Clean up browser resources"""
# #     try:
# #         if browser:
# #             browser.close()
# #         time.sleep(1)
# #         if gl:
# #             gl.stop()
# #         if pw:
# #             pw.stop()
# #         print("🧹 Browser session terminated")
# #     except Exception as e:
# #         print(f"⚠️ Cleanup warning: {e}")

# # if __name__ == "__main__":
# #     print("🛡️ ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION")
# #     print("Stealth configuration activated")
# #     print("=" * 60)
    
# #     if not GOLOGIN_AVAILABLE:
# #         print("❌ GoLogin not available!")
# #         exit(1)
    
# #     try:
# #         run_ultimate_stealth_test()
# #     except KeyboardInterrupt:
# #         print("\n🛑 Stealth test interrupted")
# #     except Exception as e:
# #         print(f"❌ Fatal error in stealth test: {e}")


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
# TOTAL_PROFILES = 1
# PAGE_LOAD_PATIENCE = (4, 8)
# HUMAN_BEHAVIOR_TIME = (15, 30)

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
        
#         context.set_extra_http_headers({
#             "DNT": "1",
#             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
#             "User-Agent": context.pages[0].evaluate("() => navigator.userAgent")
#         })
#         context.add_cookies([])
#         context.clear_cookies()
        
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
            
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 if (parameter === 37446) return 'Intel Inc.';
#                 if (parameter === 37447) return 'Intel Iris OpenGL Engine';
#                 return getParameter.apply(this, arguments);
#             };
            
#             const getImageData = HTMLCanvasElement.prototype.getContext('2d').getImageData;
#             HTMLCanvasElement.prototype.getContext('2d').getImageData = function() {
#                 const data = getImageData.apply(this, arguments);
#                 data.data[0] += Math.random() * 0.01;
#                 return data;
#             };
#         """)
        
#         print("✅ Stealth protection active")
        
#     except Exception as e:
#         print(f"⚠️ Stealth injection warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions with enhanced mouse and keyboard events"""
#     try:
#         scroll_distance = random.randint(10, 100)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#         time.sleep(random.uniform(0.3, 0.7))
        
#         elements = page.locator("a, button, input").all()[:5]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.2))
#                 random_element.click()
#                 print("🖱️ Performed random click")
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
#             "expires": int(time.time()) + random.randint(1800, 7200),
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

# def handle_captcha_challenge(page: Page):
#     """Enhanced CAPTCHA handler with Press & Hold detection"""
#     try:
#         print("🚨 CAPTCHA detected, analyzing page...")
        
#         # Check if we're on captcha page
#         current_url = page.url
#         if "captcha-v2" not in current_url:
#             print("⚠️ Not on captcha page")
#             return False
        
#         # Wait for page to fully load
#         page.wait_for_selector("body", timeout=10000)
#         time.sleep(2)
        
#         # Multiple selector strategies for Press & Hold button
#         press_hold_selectors = [
#             'p#GsnwQzyXVaaqaGt.RENrWaJpuDbbWBy',
#             'p.YqItzObUEmtmcxq',
#             'p:has-text("Press & Hold")',
#             'p:has-text("Press &")',
#             '#hLHJUFOdBkOMCdP p',
#         ]
        
#         press_hold_button = None
#         for selector in press_hold_selectors:
#             try:
#                 btn = page.locator(selector).first
#                 if btn.is_visible(timeout=2000):
#                     press_hold_button = btn
#                     print(f"✅ Found Press & Hold button with selector: {selector}")
#                     break
#             except:
#                 continue
        
#         if not press_hold_button:
#             print("⚠️ Press & Hold button not found, trying parent container")
#             try:
#                 container = page.locator('#hLHJUFOdBkOMCdP').first
#                 if container.is_visible():
#                     press_hold_button = container
#                     print("✅ Using container element")
#             except:
#                 print("❌ Could not find CAPTCHA button")
#                 return False
        
#         # Get button position and start holding
#         bbox = press_hold_button.bounding_box()
#         if bbox:
#             x = bbox['x'] + bbox['width'] / 2
#             y = bbox['y'] + bbox['height'] / 2
            
#             print(f"🖱️ Moving to button position: ({x:.0f}, {y:.0f})")
#             page.mouse.move(x, y)
#             time.sleep(0.5)
            
#             print("🖱️ Pressing and holding button...")
#             page.mouse.down()
            
#             # Monitor width change of progress bar
#             max_wait_time = 45
#             start_time = time.time()
#             last_width = 0
            
#             while time.time() - start_time < max_wait_time:
#                 try:
#                     # Check progress bar width
#                     width = page.evaluate("""
#                         () => {
#                             const progressBar = document.querySelector('#TcJKXNyREfcrRxS');
#                             if (progressBar) {
#                                 const style = progressBar.style.width;
#                                 return parseInt(style) || 0;
#                             }
#                             return 0;
#                         }
#                     """)
                    
#                     if width > last_width:
#                         print(f"📊 Progress: {width}px / 259px")
#                         last_width = width
                    
#                     # Check if completed (width reaches ~259px)
#                     if width >= 250:
#                         print("✅ Progress bar completed!")
#                         time.sleep(1)
#                         break
                    
#                     # Check if page is redirecting
#                     if "captcha-v2" not in page.url:
#                         print("🌐 Page redirected, CAPTCHA passed!")
#                         break
                    
#                     time.sleep(0.5)
                    
#                 except Exception as e:
#                     print(f"⚠️ Progress check error: {e}")
#                     time.sleep(0.5)
            
#             # Release mouse
#             page.mouse.up()
#             print("🖱️ Released button")
            
#             # Wait for redirect
#             time.sleep(3)
            
#             # Check if we successfully bypassed
#             if "captcha-v2" not in page.url:
#                 print("🎉 CAPTCHA bypassed successfully!")
#                 return True
#             else:
#                 print("⚠️ Still on CAPTCHA page, may need retry")
#                 return False
#         else:
#             print("❌ Could not get button position")
#             return False
            
#     except Exception as e:
#         print(f"❌ CAPTCHA handling error: {e}")
#         return False

# def ultimate_human_browsing(page: Page):
#     """Human-like browsing behavior with cookie management and CAPTCHA bypass"""
#     try:
#         print("🎭 Starting human behavior simulation...")

#         preserved_cookies = []

#         def handle_page_load():
#             print("🌐 Page load detected")
#             current_cookies = page.context.cookies()
#             for cookie in current_cookies:
#                 if cookie["name"].startswith("_px"):
#                     preserved_cookies.append(cookie)
#             page.context.clear_cookies()
#             if preserved_cookies:
#                 page.context.add_cookies(preserved_cookies)
#                 print("🍪 Restored PerimeterX cookies")
#             inject_fake_cookies(page.context)

#         def handle_response(response):
#             url = response.url
#             # Check for CAPTCHA in URL or page
#             if "captcha-v2" in url or "captcha" in url.lower():
#                 print(f"🚨 CAPTCHA URL detected: {url}")
#                 time.sleep(2)
#                 # Attempt to handle CAPTCHA
#                 captcha_handled = handle_captcha_challenge(page)
#                 if captcha_handled:
#                     print("✅ CAPTCHA successfully handled")
#                 else:
#                     print("⚠️ CAPTCHA handling incomplete, retrying...")
#                     time.sleep(3)
#                     handle_captcha_challenge(page)
            
#             # Cookie management
#             current_cookies = page.context.cookies()
#             for cookie in current_cookies:
#                 if cookie["name"].startswith("_px"):
#                     if cookie not in preserved_cookies:
#                         preserved_cookies.append(cookie)
#             page.context.clear_cookies()
#             if preserved_cookies:
#                 page.context.add_cookies(preserved_cookies)
#             inject_fake_cookies(page.context)

#         page.on("load", handle_page_load)
#         page.on("response", handle_response)

#         # Step 1: Google search and first URL
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
        
#         search_bar = page.locator("input[name='q']")
#         if search_bar.is_visible():
#             print(f"🔍 Typing target URL: {TARGET_URLS[0]}")
#             search_bar.type(TARGET_URLS[0], delay=random.uniform(100, 200))
#             search_bar.press("Enter")
#             wait_time = random.uniform(3, 5)
#             print(f"⏳ Waiting for search results: {wait_time:.1f}s")
#             time.sleep(wait_time)
        
#         try:
#             target_link = page.locator(f"a[href*='{TARGET_URLS[0]}']").first
#             if target_link.is_visible():
#                 print(f"🌐 Clicking target link: {TARGET_URLS[0]}")
#                 target_link.click()
#                 page.wait_for_load_state("networkidle")
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#             else:
#                 print(f"⚠️ Target link not found, navigating directly")
#                 page.goto(TARGET_URLS[0], timeout=60000)
#                 page.wait_for_load_state("networkidle")
#         except Exception as e:
#             print(f"⚠️ Target link click error: {e}")
#             page.goto(TARGET_URLS[0], timeout=60000)
#             page.wait_for_load_state("networkidle")
        
#         # Check for CAPTCHA after first navigation
#         time.sleep(2)
#         if "captcha-v2" in page.url:
#             print("🚨 CAPTCHA detected after first URL")
#             handle_captcha_challenge(page)

#         # Process each URL
#         for url in TARGET_URLS:
#             print(f"🎯 Navigating to: {url}")
#             for attempt in range(3):
#                 try:
#                     page.goto(url, timeout=60000)
#                     page.wait_for_load_state("networkidle")
#                     break
#                 except Exception as e:
#                     print(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
#                     if attempt == 2:
#                         print(f"❌ Failed to load {url} after 3 attempts")
#                         continue
            
#             # Check for CAPTCHA
#             time.sleep(2)
#             if "captcha-v2" in page.url:
#                 print(f"🚨 CAPTCHA detected on {url}")
#                 captcha_success = handle_captcha_challenge(page)
#                 if not captcha_success:
#                     print("⚠️ CAPTCHA not resolved, retrying...")
#                     time.sleep(3)
#                     handle_captcha_challenge(page)
            
#             page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#             print(f"⏳ Patient page loading: {page_wait:.1f}s")
#             time.sleep(page_wait)
            
#             try:
#                 page.wait_for_selector("body", timeout=10000)
#                 print("📄 Page elements detected")
#             except TimeoutError:
#                 print("⚠️ Page load timeout, continuing...")
            
#             # Scroll page
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
            
#             # Human behavior
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






# import time
# import random
# import uuid
# import logging
# import os
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
# TOKEN = "CHANGE_ME_TOKEN"  # Replace with your actual GoLogin token
# TOTAL_PROFILES = 100  # Run 100 visits
# PAGE_LOAD_PATIENCE = (4, 8)
# HUMAN_BEHAVIOR_TIME = (60, 80)  # Each visit lasts 60-80 seconds
# MAX_CAPTCHA_RETRIES = 2  # Retry CAPTCHA 1-2 times

# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

# # Configure logging
# log_file = "stealth_script.log"
# try:
#     # Ensure the log file is writable
#     with open(log_file, "a") as f:
#         pass
# except PermissionError:
#     print(f"Permission denied for {log_file}. Trying alternative path...")
#     log_file = os.path.join(os.path.expanduser("~"), "stealth_script.log")
#     print(f"Logging to {log_file} instead.")

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.FileHandler(log_file),
#         logging.StreamHandler()  # Keep terminal output for debugging
#     ]
# )

# # Suppress Playwright and pyee tracebacks
# logging.getLogger("asyncio").setLevel(logging.CRITICAL)
# logging.getLogger("pyee").setLevel(logging.CRITICAL)

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
#         logging.info(f"Creating stealth profile: {profile_name}")
        
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
#             logging.error(f"Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         logging.info(f"Profile created: {profile_id}")
        
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
#                 logging.info(f"Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 logging.warning(f"Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             logging.info("User agent updated to latest")
#         except Exception as e:
#             logging.warning(f"User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         logging.error(f"Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     """Start browser with stealth configuration"""
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         logging.info(f"Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         logging.info(f"Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         logging.info(f"Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         context.set_extra_http_headers({
#             "DNT": "1",
#             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
#             "User-Agent": context.pages[0].evaluate("() => navigator.userAgent")
#         })
#         context.add_cookies([])
#         context.clear_cookies()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         logging.error(f"Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     """Inject stealth scripts with enhanced fingerprinting"""
#     try:
#         logging.info("Injecting stealth protection...")
        
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
            
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 if (parameter === 37446) return 'Intel Inc.';
#                 if (parameter === 37447) return 'Intel Iris OpenGL Engine';
#                 return getParameter.apply(this, arguments);
#             };
            
#             const getImageData = HTMLCanvasElement.prototype.getContext('2d').getImageData;
#             HTMLCanvasElement.prototype.getContext('2d').getImageData = function() {
#                 const data = getImageData.apply(this, arguments);
#                 data.data[0] += Math.random() * 0.01;
#                 return data;
#             };
#         """)
        
#         logging.info("Stealth protection active")
        
#     except Exception as e:
#         logging.warning(f"Stealth injection warning: {e}")

# def perform_light_interaction(page: Page):
#     """Light human interactions with enhanced mouse and keyboard events"""
#     try:
#         scroll_distance = random.randint(10, 100)
#         page.evaluate(f"window.scrollTo({{top: {scroll_distance}, behavior: 'smooth'}});")
#         time.sleep(random.uniform(0.8, 1.5))
        
#         page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#         time.sleep(random.uniform(0.3, 0.7))
        
#         elements = page.locator("a, button, input").all()[:5]
#         if elements:
#             random_element = random.choice(elements)
#             if random_element.is_visible():
#                 random_element.hover()
#                 time.sleep(random.uniform(0.5, 1.2))
#                 random_element.click(timeout=10000)
#                 logging.info("Performed random click")
#                 if random_element.evaluate("el => el.tagName.toLowerCase() === 'input'"):
#                     random_element.type(random.choice(["search", "flights", "hotels"]), delay=random.uniform(100, 200))
#                     logging.info("Simulated keyboard input")
                
#     except Exception as e:
#         logging.warning(f"Light interaction warning: {e}")

# def inject_fake_cookies(context):
#     """Inject dynamic fake cookies to simulate a new user"""
#     fake_cookies = [
#         {
#             "name": random.choice(["session_id", "user_session", "track_id"]),
#             "value": str(uuid.uuid4()),
#             "domain": ".skyscanner.co.in",
#             "path": "/",
#             "expires": int(time.time()) + random.randint(1800, 7200),
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
#     logging.info("Injected dynamic fake cookies")

# def handle_captcha_challenge(page: Page, retries=MAX_CAPTCHA_RETRIES):
#     """Enhanced CAPTCHA handler with Press & Hold detection and limited retries"""
#     for attempt in range(retries):
#         try:
#             logging.info(f"CAPTCHA detected, attempt {attempt + 1}/{retries}")
            
#             # Check if we're on CAPTCHA page
#             current_url = page.url
#             if "captcha-v2" not in current_url and not page.locator('[id*="captcha"]').is_visible(timeout=5000):
#                 logging.warning("Not on CAPTCHA page")
#                 return False
            
#             # Wait for page to fully load
#             page.wait_for_selector("body", timeout=20000)
#             time.sleep(2)
            
#             # Updated selectors for Press & Hold button
#             press_hold_selectors = [
#                 'p:has-text("Press & Hold")',
#                 'p:has-text("Press &")',
#                 'button:has-text("Press & Hold")',
#                 '[id*="captcha"] button',
#                 '[id*="captcha"] p',
#                 'div[id*="captcha"] p',
#                 'p[id*="GsnwQzyXVaaqaGt"]',
#                 'p[id*="YqItzObUEmtmcxq"]',
#                 '#hLHJUFOdBkOMCdP p',
#             ]
            
#             press_hold_button = None
#             for selector in press_hold_selectors:
#                 try:
#                     btn = page.locator(selector).first
#                     if btn.is_visible(timeout=5000):
#                         press_hold_button = btn
#                         logging.info(f"Found Press & Hold button with selector: {selector}")
#                         break
#                 except:
#                     continue
            
#             if not press_hold_button:
#                 logging.warning("Press & Hold button not found, trying parent container")
#                 try:
#                     container = page.locator('[id*="captcha"]').first
#                     if container.is_visible(timeout=5000):
#                         press_hold_button = container
#                         logging.info("Using container element")
#                 except:
#                     logging.warning("Could not find CAPTCHA button")
#                     return False
            
#             # Get button position and start holding
#             bbox = press_hold_button.bounding_box()
#             if bbox:
#                 x = bbox['x'] + bbox['width'] / 2
#                 y = bbox['y'] + bbox['height'] / 2
                
#                 logging.info(f"Moving to button position: ({x:.0f}, {y:.0f})")
#                 page.mouse.move(x, y)
#                 time.sleep(0.5)
                
#                 logging.info("Pressing and holding button...")
#                 page.mouse.down()
                
#                 # Monitor progress bar
#                 max_wait_time = 45
#                 start_time = time.time()
#                 last_width = 0
                
#                 while time.time() - start_time < max_wait_time:
#                     try:
#                         width = page.evaluate("""
#                             () => {
#                                 const progressBar = document.querySelector('[id*="progress"]') || document.querySelector('#TcJKXNyREfcrRxS');
#                                 if (progressBar) {
#                                     const style = window.getComputedStyle(progressBar).width;
#                                     return parseInt(style) || 0;
#                                 }
#                                 return 0;
#                             }
#                         """)
                        
#                         if width > last_width:
#                             logging.info(f"Progress: {width}px / 259px")
#                             last_width = width
                        
#                         if width >= 250:
#                             logging.info("Progress bar completed!")
#                             time.sleep(1)
#                             break
                        
#                         if "captcha-v2" not in page.url:
#                             logging.info("Page redirected, CAPTCHA passed!")
#                             break
                        
#                         time.sleep(0.5)
                        
#                     except Exception as e:
#                         logging.warning(f"Progress check error: {e}")
#                         time.sleep(0.5)
                
#                 page.mouse.up()
#                 logging.info("Released button")
                
#                 time.sleep(3)
                
#                 if "captcha-v2" not in page.url:
#                     logging.info("CAPTCHA bypassed successfully!")
#                     return True
#                 else:
#                     logging.warning("Still on CAPTCHA page, retrying...")
#                     return False
#             else:
#                 logging.warning("Could not get button position")
#                 return False
                
#         except Exception as e:
#             logging.error(f"CAPTCHA handling error: {e}")
#             return False
#     logging.error(f"Failed to handle CAPTCHA after {retries} attempts")
#     return False

# def ultimate_human_browsing(page: Page):
#     """Human-like browsing behavior with cookie management and CAPTCHA bypass"""
#     start_time = time.time()
#     try:
#         logging.info("Starting human behavior simulation...")
#         preserved_cookies = []
#         captcha_detected = False

#         def handle_page_load():
#             logging.info("Page load detected")
#             current_cookies = page.context.cookies()
#             for cookie in current_cookies:
#                 if cookie["name"].startswith("_px"):
#                     preserved_cookies.append(cookie)
#             page.context.clear_cookies()
#             if preserved_cookies:
#                 page.context.add_cookies(preserved_cookies)
#                 logging.info("Restored PerimeterX cookies")
#             inject_fake_cookies(page.context)

#         def handle_response(response):
#             nonlocal captcha_detected
#             url = response.url
#             if "captcha-v2" in url or "captcha" in url.lower():
#                 if not captcha_detected:
#                     logging.info(f"CAPTCHA URL detected: {url}")
#                     captcha_detected = True
#                     captcha_handled = handle_captcha_challenge(page)
#                     if captcha_handled:
#                         logging.info("CAPTCHA successfully handled")
#                     else:
#                         logging.warning("CAPTCHA handling failed")
#                         raise Exception("CAPTCHA not resolved")

#         page.on("load", handle_page_load)
#         page.on("response", handle_response)

#         # Navigate to Google
#         google_url = "https://www.google.co.in/"
#         logging.info(f"Navigating to Google: {google_url}")
#         for attempt in range(3):
#             try:
#                 page.goto(google_url, timeout=60000)
#                 page.wait_for_load_state("networkidle")
#                 break
#             except Exception as e:
#                 logging.warning(f"Attempt {attempt + 1} failed for {google_url}: {e}")
#                 if attempt == 2:
#                     logging.error(f"Failed to load {google_url} after 3 attempts")
#                     return False
        
#         search_bar = page.locator("input[name='q']")
#         if search_bar.is_visible():
#             logging.info(f"Typing target URL: {TARGET_URLS[0]}")
#             search_bar.type(TARGET_URLS[0], delay=random.uniform(100, 200))
#             search_bar.press("Enter")
#             wait_time = random.uniform(3, 5)
#             logging.info(f"Waiting for search results: {wait_time:.1f}s")
#             time.sleep(wait_time)
        
#         try:
#             target_link = page.locator(f"a[href*='{TARGET_URLS[0]}']").first
#             if target_link.is_visible():
#                 logging.info(f"Clicking target link: {TARGET_URLS[0]}")
#                 target_link.click()
#                 page.wait_for_load_state("networkidle")
#                 wait_time = random.uniform(4, 7)
#                 time.sleep(wait_time)
#             else:
#                 logging.warning(f"Target link not found, navigating directly")
#                 page.goto(TARGET_URLS[0], timeout=60000)
#                 page.wait_for_load_state("networkidle")
#         except Exception as e:
#             logging.warning(f"Target link click error: {e}")
#             page.goto(TARGET_URLS[0], timeout=60000)
#             page.wait_for_load_state("networkidle")
        
#         if "captcha-v2" in page.url or page.locator('[id*="captcha"]').is_visible(timeout=5000):
#             logging.info("CAPTCHA detected after first URL")
#             if not handle_captcha_challenge(page):
#                 logging.error("Failed to resolve CAPTCHA after first URL")
#                 return False

#         # Process each URL
#         for url in TARGET_URLS:
#             logging.info(f"Navigating to: {url}")
#             for attempt in range(3):
#                 try:
#                     page.goto(url, timeout=60000)
#                     page.wait_for_load_state("networkidle")
#                     break
#                 except Exception as e:
#                     logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
#                     if attempt == 2:
#                         logging.error(f"Failed to load {url} after 3 attempts")
#                         continue
            
#             if "captcha-v2" in page.url or page.locator('[id*="captcha"]').is_visible(timeout=5000):
#                 logging.info(f"CAPTCHA detected on {url}")
#                 if not handle_captcha_challenge(page):
#                     logging.error(f"Failed to resolve CAPTCHA for {url}")
#                     return False
            
#             page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#             logging.info(f"Patient page loading: {page_wait:.1f}s")
#             time.sleep(page_wait)
            
#             try:
#                 page.wait_for_selector("body", timeout=20000)
#                 logging.info("Page elements detected")
#             except TimeoutError:
#                 logging.warning("Page load timeout, continuing...")
            
#             try:
#                 page_height = page.evaluate("document.body.scrollHeight")
#                 current_pos = 0
#                 while current_pos < page_height:
#                     scroll_distance = random.randint(10, 100)
#                     page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
#                     current_pos += scroll_distance
#                     time.sleep(random.uniform(0.5, 1.5))
#                 logging.info("Scrolled full page")
#             except Exception as e:
#                 logging.warning(f"Scroll error: {e}")
            
#             human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#             logging.info(f"Performing human behavior for {human_time:.1f}s")
#             behavior_start = time.time()
#             while time.time() - behavior_start < human_time:
#                 action = random.choice(['realistic_scroll', 'mouse_trail', 'reading_pause'])
#                 execute_human_action(page, action)
#                 perform_light_interaction(page)
#                 time.sleep(random.uniform(0.8, 2.5))
        
#         duration = time.time() - start_time
#         logging.info(f"Human behavior complete, visit duration: {duration:.1f}s")
#         return True
        
#     except Exception as e:
#         logging.error(f"Human browsing error: {e}")
#         return False
#     finally:
#         duration = time.time() - start_time
#         logging.info(f"Visit ended, total duration: {duration:.1f}s")
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
#         logging.warning(f"Human action error: {e}")

# def run_ultimate_stealth_test():
#     """Run the stealth test"""
#     logging.info("STEALTH MODE WITH COOKIE CONFUSION ACTIVATED")
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         logging.info(f"\n=== PROFILE {profile_num}/{TOTAL_PROFILES} ===")
#         start_time = time.time()
#         profile_name = f"stealth_cookie_confusion_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             logging.info(f"Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     success = ultimate_human_browsing(page)
#                     duration = time.time() - start_time
#                     if success:
#                         successful_runs += 1
#                         logging.info(f"PROFILE {profile_num} - SUCCESS! Duration: {duration:.1f}s")
#                     else:
#                         logging.error(f"PROFILE {profile_num} - FAILED. Duration: {duration:.1f}s")
                    
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 logging.error(f"PROFILE {profile_num} - BROWSER START FAILED. Duration: {time.time() - start_time:.1f}s")
#         else:
#             logging.error(f"PROFILE {profile_num} - PROFILE CREATION FAILED. Duration: {time.time() - start_time:.1f}s")

#     logging.info(f"\nSTEALTH TEST COMPLETE! Success Rate: {successful_runs}/{TOTAL_PROFILES} ({successful_runs/TOTAL_PROFILES*100:.1f}%)")

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
#         logging.info("Browser session terminated")
#     except Exception as e:
#         logging.warning(f"Cleanup warning: {e}")

# if __name__ == "__main__":
#     logging.info("ANTI-BOT DETECTION BYPASS WITH COOKIE CONFUSION")
#     logging.info("Stealth configuration activated")
    
#     if not GOLOGIN_AVAILABLE:
#         logging.error("GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         logging.info("Stealth test interrupted")
#     except Exception as e:
#         logging.error(f"Fatal error in stealth test: {e}")



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
# TOKEN = "CHANGE_ME_TOKEN"
# TOTAL_PROFILES = 1
# PAGE_LOAD_PATIENCE = (4, 8)
# HUMAN_BEHAVIOR_TIME = (15, 30)

# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

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

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"Creating stealth profile: {profile_name}")
        
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
#             print(f"Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"Profile created: {profile_id}")
        
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
#                 print(f"Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("User agent updated to latest")
#         except Exception as e:
#             print(f"User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         context.set_extra_http_headers({
#             "DNT": "1",
#             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
#             "User-Agent": context.pages[0].evaluate("() => navigator.userAgent")
#         })
#         context.add_cookies([])
#         context.clear_cookies()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     try:
#         print("Injecting stealth protection...")
        
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
            
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 if (parameter === 37446) return 'Intel Inc.';
#                 if (parameter === 37447) return 'Intel Iris OpenGL Engine';
#                 return getParameter.apply(this, arguments);
#             };
#         """)
        
#         print("Stealth protection active")
        
#     except Exception as e:
#         print(f"Stealth injection warning: {e}")

# def inject_fake_cookies(context):
#     try:
#         fake_cookies = [
#             {
#                 "name": random.choice(["session_id", "user_session", "track_id"]),
#                 "value": str(uuid.uuid4()),
#                 "domain": ".skyscanner.co.in",
#                 "path": "/",
#                 "expires": int(time.time()) + random.randint(1800, 7200),
#                 "httpOnly": random.choice([True, False]),
#                 "secure": True
#             }
#         ]
#         context.add_cookies(fake_cookies)
#     except:
#         pass

# def handle_captcha_challenge(page: Page, max_retries=3):
#     """Enhanced CAPTCHA handler with iframe detection and proper mouse interaction"""
    
#     for attempt in range(max_retries):
#         try:
#             print(f"\nCAPTCHA Handler - Attempt {attempt + 1}/{max_retries}")
            
#             current_url = page.url
#             print(f"Current URL: {current_url[:100]}...")
            
#             if "captcha" not in current_url.lower():
#                 print("Not on CAPTCHA page")
#                 return False
            
#             print("Waiting for CAPTCHA page to load...")
#             page.wait_for_load_state("load", timeout=20000)
#             print("Page loaded")
            
#             time.sleep(3)
            
#             # STRATEGY 1: Check main page first
#             print("\n[Strategy 1] Searching main page...")
#             button_found = False
#             target_frame = page
            
#             button_info = page.evaluate("""
#                 () => {
#                     const allElements = document.querySelectorAll('*');
#                     for (let elem of allElements) {
#                         const text = (elem.textContent || elem.innerText || '').toUpperCase();
#                         if (text.includes('PRESS') && text.includes('HOLD')) {
#                             const rect = elem.getBoundingClientRect();
#                             if (rect.width > 50 && rect.height > 30 && 
#                                 rect.top >= 0 && rect.left >= 0 &&
#                                 rect.top < window.innerHeight && rect.left < window.innerWidth) {
#                                 return {
#                                     x: rect.x + rect.width / 2,
#                                     y: rect.y + rect.height / 2,
#                                     width: rect.width,
#                                     height: rect.height,
#                                     text: elem.textContent.trim()
#                                 };
#                             }
#                         }
#                     }
#                     return null;
#                 }
#             """)
            
#             # STRATEGY 2: Search in iframes if not found
#             if not button_info:
#                 print("[Strategy 1] Not found in main page")
#                 print("\n[Strategy 2] Searching iframes...")
                
#                 frames = page.frames
#                 print(f"Found {len(frames)} frames total")
                
#                 for idx, frame in enumerate(frames):
#                     try:
#                         frame_url = frame.url
#                         print(f"  Frame {idx}: {frame_url[:60]}...")
                        
#                         # Wait for frame to be ready
#                         time.sleep(1)
                        
#                         # Search this frame
#                         button_info = frame.evaluate("""
#                             () => {
#                                 const allElements = document.querySelectorAll('*');
#                                 console.log('Scanning elements in iframe:', allElements.length);
                                
#                                 for (let elem of allElements) {
#                                     const text = (elem.textContent || elem.innerText || '').toUpperCase();
                                    
#                                     if (text.includes('PRESS') && text.includes('HOLD')) {
#                                         console.log('Found PRESS & HOLD element:', elem.tagName, text.substring(0, 50));
#                                         const rect = elem.getBoundingClientRect();
                                        
#                                         // Check if visible and reasonable size
#                                         if (rect.width > 50 && rect.height > 30 && 
#                                             rect.top >= 0 && rect.left >= 0) {
                                            
#                                             console.log('Element is visible and clickable');
#                                             return {
#                                                 x: rect.x + rect.width / 2,
#                                                 y: rect.y + rect.height / 2,
#                                                 width: rect.width,
#                                                 height: rect.height,
#                                                 text: elem.textContent.trim(),
#                                                 tag: elem.tagName
#                                             };
#                                         }
#                                     }
#                                 }
#                                 return null;
#                             }
#                         """)
                        
#                         if button_info:
#                             print(f"  SUCCESS! Button found in frame {idx}")
#                             print(f"    Tag: {button_info.get('tag')}")
#                             print(f"    Text: {button_info['text'][:50]}")
#                             target_frame = frame
#                             button_found = True
#                             break
                            
#                     except Exception as e:
#                         print(f"  Frame {idx} error: {str(e)[:50]}")
#                         continue
#             else:
#                 print("[Strategy 1] Button found in main page!")
#                 button_found = True
            
#             if not button_info:
#                 print("\nButton not found in any frame")
                
#                 # Save debug screenshot
#                 try:
#                     timestamp = int(time.time())
#                     page.screenshot(path=f"debug_{timestamp}.png", full_page=True)
#                     print(f"Screenshot saved: debug_{timestamp}.png")
#                 except:
#                     pass
                
#                 if attempt < max_retries - 1:
#                     print("Retrying in 5 seconds...")
#                     time.sleep(5)
#                 continue
            
#             # INTERACT WITH BUTTON
#             print(f"\nButton located!")
#             print(f"  Position: ({button_info['x']:.1f}, {button_info['y']:.1f})")
#             print(f"  Size: {button_info['width']:.1f} x {button_info['height']:.1f}")
            
#             center_x = button_info['x']
#             center_y = button_info['y']
            
#             # If button is in an iframe, adjust coordinates
#             if target_frame != page:
#                 # Get iframe's position in the main page
#                 iframe_element = target_frame.frame_element()
#                 iframe_rect = page.evaluate("""
#                     (element) => {
#                         const rect = element.getBoundingClientRect();
#                         return {
#                             x: rect.x,
#                             y: rect.y
#                         };
#                     }
#                 """, iframe_element)
                
#                 # Adjust coordinates to main page's coordinate system
#                 center_x += iframe_rect['x']
#                 center_y += iframe_rect['y']
#                 print(f"  Adjusted coordinates for iframe: ({center_x:.1f}, {center_y:.1f})")
            
#             # Move to button using page.mouse
#             print("\nMoving to button...")
#             page.mouse.move(center_x, center_y, steps=25)
#             time.sleep(random.uniform(0.3, 0.6))
            
#             print("Pressing button...")
#             page.mouse.down()
            
#             # Hold and monitor
#             hold_duration = 60
#             start_time = time.time()
            
#             print(f"Holding for up to {hold_duration} seconds...")
#             print("(Will auto-release if CAPTCHA is solved)")
            
#             while time.time() - start_time < hold_duration:
#                 elapsed = time.time() - start_time
                
#                 # Print progress every 3 seconds
#                 if int(elapsed) % 3 == 0 and elapsed % 1 < 0.5:
#                     print(f"  Holding... {int(elapsed)}s")
                
#                 # Check if we've been redirected (CAPTCHA solved)
#                 try:
#                     current = page.url
#                     if "captcha" not in current.lower():
#                         print(f"\nCAPTCHA SOLVED! Redirected after {elapsed:.1f}s")
#                         page.mouse.up()
#                         return True
#                 except:
#                     pass
                
#                 time.sleep(0.5)
            
#             # Release after timeout
#             page.mouse.up()
#             print("\nReleased button after full duration")
            
#             time.sleep(3)
            
#             # Final check
#             if "captcha" not in page.url.lower():
#                 print("CAPTCHA bypassed successfully!")
#                 return True
#             else:
#                 print("Still on CAPTCHA page")
#                 if attempt < max_retries - 1:
#                     print("Retrying...")
#                     time.sleep(5)
                
#         except Exception as e:
#             print(f"Error in attempt {attempt + 1}: {e}")
#             import traceback
#             traceback.print_exc()
#             if attempt < max_retries - 1:
#                 time.sleep(5)
    
#     print("\nAll attempts exhausted")
#     return False

# def ultimate_human_browsing(page: Page):
#     try:
#         print("Starting human behavior simulation...")

#         preserved_cookies = []

#         def handle_page_load():
#             print("Page load detected")
#             if "captcha" in page.url.lower():
#                 print("CAPTCHA page detected")
#             else:
#                 current_cookies = page.context.cookies()
#                 for cookie in current_cookies:
#                     if cookie["name"].startswith("_px"):
#                         if cookie not in preserved_cookies:
#                             preserved_cookies.append(cookie)
#                 page.context.clear_cookies()
#                 if preserved_cookies:
#                     page.context.add_cookies(preserved_cookies)
#                 inject_fake_cookies(page.context)

#         def handle_response(response):
#             url = response.url
#             if "captcha-v2/index.html" in url:
#                 print(f"Main CAPTCHA page detected: {url[:80]}...")

#         page.on("load", handle_page_load)
#         page.on("response", handle_response)

#         google_url = "https://www.google.co.in/"
#         print(f"\nNavigating to Google: {google_url}")
        
#         for attempt in range(3):
#             try:
#                 page.goto(google_url, timeout=60000, wait_until="networkidle")
#                 break
#             except Exception as e:
#                 print(f"Attempt {attempt + 1} failed: {e}")
#                 if attempt == 2:
#                     return False
        
#         time.sleep(3)
#         if "captcha" in page.url.lower():
#             print("\nCAPTCHA detected after Google")
#             if not handle_captcha_challenge(page):
#                 print("Failed to bypass CAPTCHA")
#                 return False

#         for url in TARGET_URLS:
#             print(f"\n{'='*60}")
#             print(f"Navigating to: {url}")
#             print(f"{'='*60}")
            
#             for attempt in range(3):
#                 try:
#                     page.goto(url, timeout=60000, wait_until="networkidle")
#                     break
#                 except Exception as e:
#                     print(f"Navigation attempt {attempt + 1} failed: {e}")
#                     if attempt == 2:
#                         print(f"Failed to load {url}")
#                         continue
            
#             time.sleep(3)
            
#             if "captcha" in page.url.lower():
#                 print(f"\nCAPTCHA detected on {url}")
#                 if not handle_captcha_challenge(page):
#                     print("Failed to bypass CAPTCHA, skipping this URL")
#                     continue
            
#             page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#             print(f"Page loaded, waiting {page_wait:.1f}s")
#             time.sleep(page_wait)
            
#             try:
#                 page_height = page.evaluate("document.body.scrollHeight")
#                 scroll_steps = random.randint(3, 6)
#                 for _ in range(scroll_steps):
#                     scroll_distance = random.randint(200, 500)
#                     page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
#                     time.sleep(random.uniform(1, 2))
#                 print("Page scrolled")
#             except Exception as e:
#                 print(f"Scroll error: {e}")
            
#             human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#             print(f"Simulating human behavior for {human_time:.1f}s")
#             start_time = time.time()
            
#             while time.time() - start_time < human_time:
#                 action = random.choice(['scroll', 'mouse_move', 'pause'])
                
#                 if action == 'scroll':
#                     page.evaluate(f"window.scrollBy({{top: {random.randint(50, 150)}, behavior: 'smooth'}});")
#                 elif action == 'mouse_move':
#                     page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#                 else:
#                     time.sleep(random.uniform(1, 3))
                
#                 time.sleep(random.uniform(1, 2))
        
#         print("\nHuman behavior simulation complete")
#         return True
        
#     except Exception as e:
#         print(f"Human browsing error: {e}")
#         import traceback
#         traceback.print_exc()
#         return False
#     finally:
#         try:
#             page.remove_listener("load", handle_page_load)
#             page.remove_listener("response", handle_response)
#         except:
#             pass

# def run_ultimate_stealth_test():
#     print("STEALTH MODE WITH TEXT-BASED CAPTCHA BYPASS")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n=== PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_text_bypass_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"\nPROFILE {profile_num} - SUCCESS!")
#                     else:
#                         print(f"\nPROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(10, 20)
#                     print(f"Session cleanup in {session_time:.1f}s")
#                     time.sleep(session_time)
                  
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             print(f"PROFILE {profile_num} - PROFILE CREATION FAILED")

#     print(f"\n{'='*60}")
#     print(f"TEST COMPLETE!")
#     print(f"Success Rate: {successful_runs}/{TOTAL_PROFILES}")
#     print(f"{'='*60}")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("Browser session terminated")
#     except Exception as e:
#         print(f"Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("ANTI-BOT DETECTION BYPASS WITH TEXT-BASED CAPTCHA SOLVER")
#     print("=" * 60)

#     if not GOLOGIN_AVAILABLE:
#         print("GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\nTest interrupted by user")
#     except Exception as e:
#         print(f"Fatal error: {e}")                            # done
#         import traceback
#         traceback.print_exc()




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
# TOKEN = "CHANGE_ME_TOKEN"
# TOTAL_PROFILES = 1
# PAGE_LOAD_PATIENCE = (4, 8)
# HUMAN_BEHAVIOR_TIME = (15, 30)

# PROXY_LIST = [
#     "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
# ]

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

# def create_ultimate_stealth_profile(profile_name, proxy_config=None):
#     try:
#         gl = GoLogin({"token": TOKEN})
#         print(f"Creating stealth profile: {profile_name}")
        
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
#             print(f"Profile creation failed: {profile}")
#             return None
            
#         profile_id = profile['id']
#         print(f"Profile created: {profile_id}")
        
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
#                 print(f"Proxy configured: {proxy_config['host']}")
#             except Exception as e:
#                 print(f"Proxy setup warning: {e}")
        
#         try:
#             gl.updateUserAgentToLatestBrowser([profile_id])
#             print("User agent updated to latest")
#         except Exception as e:
#             print(f"User agent update warning: {e}")
        
#         return profile_id
        
#     except Exception as e:
#         print(f"Profile creation error: {e}")
#         return None

# def start_maximum_stealth_browser(profile_id):
#     try:
#         gl = GoLogin({
#             "token": TOKEN,
#             "profile_id": profile_id
#         })
#         print(f"Starting stealth browser for: {profile_id}")
#         debugger_address = gl.start()
#         print(f"Browser endpoint: {debugger_address}")
        
#         wait_time = random.uniform(3, 6)
#         print(f"Browser stabilization: {wait_time:.1f}s")
#         time.sleep(wait_time)
        
#         pw = sync_playwright().start()
#         cdp_url = f"http://{debugger_address}"
#         browser = pw.chromium.connect_over_cdp(cdp_url)
#         context = browser.contexts[0]
#         if context.pages:
#             page = context.pages[0]
#         else:
#             page = context.new_page()
        
#         context.set_extra_http_headers({
#             "DNT": "1",
#             "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
#             "User-Agent": context.pages[0].evaluate("() => navigator.userAgent")
#         })
#         context.add_cookies([])
#         context.clear_cookies()
        
#         inject_ultimate_stealth(page)
        
#         return gl, pw, browser, page
        
#     except Exception as e:
#         print(f"Browser start error: {e}")
#         return None, None, None, None

# def inject_ultimate_stealth(page: Page):
#     try:
#         print("Injecting stealth protection...")
        
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
            
#             const getParameter = WebGLRenderingContext.prototype.getParameter;
#             WebGLRenderingContext.prototype.getParameter = function(parameter) {
#                 if (parameter === 37446) return 'Intel Inc.';
#                 if (parameter === 37447) return 'Intel Iris OpenGL Engine';
#                 return getParameter.apply(this, arguments);
#             };
#         """)
        
#         print("Stealth protection active")
        
#     except Exception as e:
#         print(f"Stealth injection warning: {e}")

# def inject_fake_cookies(context):
#     try:
#         fake_cookies = [
#             {
#                 "name": random.choice(["session_id", "user_session", "track_id"]),
#                 "value": str(uuid.uuid4()),
#                 "domain": ".skyscanner.co.in",
#                 "path": "/",
#                 "expires": int(time.time()) + random.randint(1800, 7200),
#                 "httpOnly": random.choice([True, False]),
#                 "secure": True
#             }
#         ]
#         context.add_cookies(fake_cookies)
#     except:
#         pass

# def handle_captcha_challenge(page: Page, max_retries=3):
#     """Simplified CAPTCHA handler: Find button, hold, check page change"""
    
#     for attempt in range(max_retries):
#         try:
#             print(f"\nCAPTCHA Handler - Attempt {attempt + 1}/{max_retries}")
            
#             current_url = page.url
#             print(f"Current URL: {current_url[:100]}...")
            
#             if "captcha" not in current_url.lower():
#                 print("Not on CAPTCHA page")
#                 return False
            
#             print("Waiting for CAPTCHA page to load...")
#             page.wait_for_load_state("load", timeout=30000)
#             print("Page loaded")
            
#             time.sleep(3)
            
#             # STRATEGY 1: Check main page first
#             print("\n[Strategy 1] Searching main page...")
#             button_found = False
#             target_frame = page
#             button_element = None
            
#             # Search for button in main page
#             button_element = page.locator("text=/PRESS.*HOLD/i").first  # Case-insensitive regex for "PRESS & HOLD"
#             if button_element.is_visible():
#                 print("[Strategy 1] Button found in main page!")
#                 button_found = True
            
#             # STRATEGY 2: Search in iframes if not found
#             if not button_found:
#                 print("[Strategy 1] Not found in main page")
#                 print("\n[Strategy 2] Searching iframes...")
                
#                 frames = page.frames
#                 print(f"Found {len(frames)} frames total")
                
#                 for idx, frame in enumerate(frames):
#                     try:
#                         frame_url = frame.url
#                         print(f"  Frame {idx}: {frame_url[:60]}...")
                        
#                         # Log frame content for debugging
#                         try:
#                             frame_content = frame.content()
#                             print(f"  Frame {idx} content (first 200 chars): {frame_content[:200]}...")
#                         except Exception as e:
#                             print(f"  Frame {idx} content error: {str(e)[:50]}")
                        
#                         # Search for button in frame
#                         button_element = frame.locator("text=/PRESS.*HOLD/i").first
#                         if button_element.is_visible():
#                             print(f"  SUCCESS! Button found in frame {idx}")
#                             target_frame = frame
#                             button_found = True
#                             break
                            
#                     except Exception as e:
#                         print(f"  Frame {idx} error: {str(e)[:50]}")
#                         continue
            
#             if not button_found:
#                 print("\nButton not found in any frame")
#                 try:
#                     timestamp = int(time.time())
#                     page.screenshot(path=f"debug_no_button_{timestamp}.png", full_page=True)
#                     print(f"Screenshot saved: debug_no_button_{timestamp}.png")
#                 except Exception as e:
#                     print(f"Screenshot error: {e}")
#                 if attempt < max_retries - 1:
#                     print("Retrying in 5 seconds...")
#                     time.sleep(5)
#                 continue
            
#             # INTERACT WITH BUTTON
#             print("\nButton found! Getting position...")
#             try:
#                 bounding_box = button_element.bounding_box()
#                 if bounding_box:
#                     center_x = bounding_box['x'] + bounding_box['width'] / 2
#                     center_y = bounding_box['y'] + bounding_box['height'] / 2
#                     print(f"  Button position (page coordinates): ({center_x:.1f}, {center_y:.1f})")
#                     print(f"  Size: {bounding_box['width']:.1f} x {bounding_box['height']:.1f}")
#                 else:
#                     print("  Bounding box not available, skipping interaction")
#                     continue
#             except Exception as e:
#                 print(f"  Error getting button position: {e}")
#                 continue
            
#             print("\nMoving to button...")
#             page.mouse.move(center_x, center_y, steps=25)
#             time.sleep(random.uniform(0.3, 0.6))
            
#             print("Pressing button...")
#             page.mouse.down()
            
#             try:
#                 timestamp = int(time.time())
#                 page.screenshot(path=f"debug_button_press_{timestamp}.png", full_page=True)
#                 print(f"Screenshot saved: debug_button_press_{timestamp}.png")
#             except Exception as e:
#                 print(f"Screenshot error: {e}")
            
#             # Hold and monitor page change
#             hold_duration = 90
#             start_time = time.time()
#             print(f"Holding for up to {hold_duration} seconds...")
#             print("(Will auto-release if CAPTCHA page changes)")
            
#             while time.time() - start_time < hold_duration:
#                 elapsed = time.time() - start_time
                
#                 # Check if CAPTCHA is solved (page reloaded, no 'captcha' in URL)
#                 try:
#                     current = page.url
#                     if "captcha" not in current.lower():
#                         print(f"\nCAPTCHA SOLVED! Redirected after {elapsed:.1f}s")
#                         page.mouse.up()
#                         return True
#                 except:
#                     pass
                
#                 if int(elapsed) % 3 == 0 and elapsed % 1 < 0.5:
#                     print(f"  Holding... {int(elapsed)}s")
#                 time.sleep(0.5)
            
#             # Release after timeout
#             page.mouse.up()
#             print("\nReleased button after full duration")
            
#             try:
#                 timestamp = int(time.time())
#                 page.screenshot(path=f"debug_button_release_{timestamp}.png", full_page=True)
#                 print(f"Screenshot saved: debug_button_release_{timestamp}.png")
#             except Exception as e:
#                 print(f"Screenshot error: {e}")
            
#             time.sleep(3)
            
#             # Final check
#             if "captcha" not in page.url.lower():
#                 print("CAPTCHA bypassed successfully!")
#                 return True
#             else:
#                 print("Still on CAPTCHA page")
#                 if attempt < max_retries - 1:
#                     print("Retrying...")
#                     time.sleep(5)
                
#         except Exception as e:
#             print(f"Error in attempt {attempt + 1}: {e}")
#             import traceback
#             traceback.print_exc()
#             if attempt < max_retries - 1:
#                 time.sleep(5)
    
#     print("\nAll attempts exhausted")
#     return False

# def ultimate_human_browsing(page: Page):
#     try:
#         print("Starting human behavior simulation...")

#         preserved_cookies = []

#         def handle_page_load():
#             print("Page load detected")
#             if "captcha" in page.url.lower():
#                 print("CAPTCHA page detected")
#             else:
#                 current_cookies = page.context.cookies()
#                 for cookie in current_cookies:
#                     if cookie["name"].startswith("_px"):
#                         if cookie not in preserved_cookies:
#                             preserved_cookies.append(cookie)
#                 page.context.clear_cookies()
#                 if preserved_cookies:
#                     page.context.add_cookies(preserved_cookies)
#                 inject_fake_cookies(page.context)

#         def handle_response(response):
#             url = response.url
#             if "captcha-v2/index.html" in url:
#                 print(f"Main CAPTCHA page detected: {url[:80]}...")

#         page.on("load", handle_page_load)
#         page.on("response", handle_response)

#         google_url = "https://www.google.co.in/"
#         print(f"\nNavigating to Google: {google_url}")
        
#         for attempt in range(3):
#             try:
#                 page.goto(google_url, timeout=60000, wait_until="networkidle")
#                 break
#             except Exception as e:
#                 print(f"Attempt {attempt + 1} failed: {e}")
#                 if attempt == 2:
#                     return False
        
#         time.sleep(3)
#         if "captcha" in page.url.lower():
#             print("\nCAPTCHA detected after Google")
#             if not handle_captcha_challenge(page):
#                 print("Failed to bypass CAPTCHA")
#                 return False

#         for url in TARGET_URLS:
#             print(f"\n{'='*60}")
#             print(f"Navigating to: {url}")
#             print(f"{'='*60}")
            
#             for attempt in range(3):
#                 try:
#                     page.goto(url, timeout=60000, wait_until="networkidle")
#                     break
#                 except Exception as e:
#                     print(f"Navigation attempt {attempt + 1} failed: {e}")
#                     if attempt == 2:
#                         print(f"Failed to load {url}")
#                         continue
            
#             time.sleep(3)
            
#             if "captcha" in page.url.lower():
#                 print(f"\nCAPTCHA detected on {url}")
#                 if not handle_captcha_challenge(page):
#                     print("Failed to bypass CAPTCHA, skipping this URL")
#                     continue
            
#             page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
#             print(f"Page loaded, waiting {page_wait:.1f}s")
#             time.sleep(page_wait)
            
#             try:
#                 page_height = page.evaluate("document.body.scrollHeight")
#                 scroll_steps = random.randint(3, 6)
#                 for _ in range(scroll_steps):
#                     scroll_distance = random.randint(200, 500)
#                     page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
#                     time.sleep(random.uniform(1, 2))
#                 print("Page scrolled")
#             except Exception as e:
#                 print(f"Scroll error: {e}")
            
#             human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
#             print(f"Simulating human behavior for {human_time:.1f}s")
#             start_time = time.time()
            
#             while time.time() - start_time < human_time:
#                 action = random.choice(['scroll', 'mouse_move', 'pause'])
                
#                 if action == 'scroll':
#                     page.evaluate(f"window.scrollBy({{top: {random.randint(50, 150)}, behavior: 'smooth'}});")
#                 elif action == 'mouse_move':
#                     page.mouse.move(random.randint(100, 800), random.randint(100, 600))
#                 else:
#                     time.sleep(random.uniform(1, 3))
                
#                 time.sleep(random.uniform(1, 2))
        
#         print("\nHuman behavior simulation complete")
#         return True
        
#     except Exception as e:
#         print(f"Human browsing error: {e}")
#         import traceback
#         traceback.print_exc()
#         return False
#     finally:
#         try:
#             page.remove_listener("load", handle_page_load)
#             page.remove_listener("response", handle_response)
#         except:
#             pass

# def run_ultimate_stealth_test():
#     print("STEALTH MODE WITH IFRAME-AWARE CAPTCHA BYPASS")
#     print("=" * 60)
    
#     successful_runs = 0
    
#     for profile_num in range(1, TOTAL_PROFILES + 1):
#         print(f"\n=== PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
#         profile_name = f"stealth_iframe_bypass_{profile_num}_{random.randint(100000, 999999)}"
        
#         proxy_config = None
#         if PROXY_LIST:
#             proxy_str = random.choice(PROXY_LIST)
#             proxy_config = parse_proxy_string(proxy_str)
        
#         profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
#         if profile_id:
#             wait_time = random.uniform(4, 8)
#             print(f"Pre-start preparation: {wait_time:.1f}s")
#             time.sleep(wait_time)
            
#             gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
#             if page:
#                 try:
#                     success = ultimate_human_browsing(page)
                    
#                     if success:
#                         successful_runs += 1
#                         print(f"\nPROFILE {profile_num} - SUCCESS!")
#                     else:
#                         print(f"\nPROFILE {profile_num} - FAILED")
                    
#                     session_time = random.uniform(10, 20)
#                     print(f"Session cleanup in {session_time:.1f}s")
#                     time.sleep(session_time)
                  
#                 finally:
#                     cleanup_browser(gl, pw, browser)
#             else:
#                 print(f"PROFILE {profile_num} - BROWSER START FAILED")
#         else:
#             print(f"PROFILE {profile_num} - PROFILE CREATION FAILED")

#     print(f"\n{'='*60}")
#     print(f"TEST COMPLETE!")
#     print(f"Success Rate: {successful_runs}/{TOTAL_PROFILES}")
#     print(f"{'='*60}")

# def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
#     try:
#         if browser:
#             browser.close()
#         time.sleep(1)
#         if gl:
#             gl.stop()
#         if pw:
#             pw.stop()
#         print("Browser session terminated")
#     except Exception as e:
#         print(f"Cleanup warning: {e}")

# if __name__ == "__main__":
#     print("ANTI-BOT DETECTION BYPASS WITH IFRAME-AWARE CAPTCHA SOLVER")
#     print("=" * 60)

#     if not GOLOGIN_AVAILABLE:
#         print("GoLogin not available!")
#         exit(1)
    
#     try:
#         run_ultimate_stealth_test()
#     except KeyboardInterrupt:
#         print("\nTest interrupted by user")
#     except Exception as e:
#         print(f"Fatal error: {e}")
#         import traceback
#         traceback.print_exc()






import time
import random
import uuid
import datetime
import re
import random
import datetime
import random
from playwright.sync_api import expect
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
]
TOKEN = "CHANGE_ME_TOKEN"
TOTAL_PROFILES = 1
PAGE_LOAD_PATIENCE = (4, 8)
HUMAN_BEHAVIOR_TIME = (15, 30)

PROXY_LIST = [
    "socks5 sg.proxy.geonode.io:11000:geonode_xvmYN44Bvz-type-residential-country-in:a8a841f4-46ad-4059-bf25-c9d8170908ff",
]

# Airport codes with full names
AIRPORT_CODES = {
    "BLR": "Bengaluru (BLR)",
    "BOM": "Mumbai (BOM)",
    "DEL": "Delhi (DEL)",
    "CCU": "Kolkata (CCU)",
    "MAA": "Chennai (MAA)",
    "HYD": "Hyderabad (HYD)",
    "AMD": "Ahmedabad (AMD)",
    "PNQ": "Pune (PNQ)",
    "LHR": "London (LHR)",
    "JFK": "New York (JFK)",
    "DXB": "Dubai (DXB)"
}

def parse_proxy_string(s: str):
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
    try:
        gl = GoLogin({"token": TOKEN})
        print(f"Creating stealth profile: {profile_name}")
        
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
            print(f"Profile creation failed: {profile}")
            return None
            
        profile_id = profile['id']
        print(f"Profile created: {profile_id}")
        
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
                print(f"Proxy configured: {proxy_config['host']}")
            except Exception as e:
                print(f"Proxy setup warning: {e}")
        
        try:
            gl.updateUserAgentToLatestBrowser([profile_id])
            print("User agent updated to latest")
        except Exception as e:
            print(f"User agent update warning: {e}")
        
        return profile_id
        
    except Exception as e:
        print(f"Profile creation error: {e}")
        return None

def start_maximum_stealth_browser(profile_id):
    try:
        gl = GoLogin({
            "token": TOKEN,
            "profile_id": profile_id
        })
        print(f"Starting stealth browser for: {profile_id}")
        debugger_address = gl.start()
        print(f"Browser endpoint: {debugger_address}")
        
        wait_time = random.uniform(3, 6)
        print(f"Browser stabilization: {wait_time:.1f}s")
        time.sleep(wait_time)
        
        pw = sync_playwright().start()
        cdp_url = f"http://{debugger_address}"
        browser = pw.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()
        
        context.set_extra_http_headers({
            "DNT": "1",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "User-Agent": context.pages[0].evaluate("() => navigator.userAgent")
        })
        context.add_cookies([])
        context.clear_cookies()
        
        inject_ultimate_stealth(page)
        
        return gl, pw, browser, page
        
    except Exception as e:
        print(f"Browser start error: {e}")
        return None, None, None, None

def inject_ultimate_stealth(page: Page):
    try:
        print("Injecting stealth protection...")
        
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
            
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37446) return 'Intel Inc.';
                if (parameter === 37447) return 'Intel Iris OpenGL Engine';
                return getParameter.apply(this, arguments);
            };
        """)
        
        print("Stealth protection active")
        
    except Exception as e:
        print(f"Stealth injection warning: {e}")

def inject_fake_cookies(context):
    try:
        fake_cookies = [
            {
                "name": random.choice(["session_id", "user_session", "track_id"]),
                "value": str(uuid.uuid4()),
                "domain": ".skyscanner.co.in",
                "path": "/",
                "expires": int(time.time()) + random.randint(1800, 7200),
                "httpOnly": random.choice([True, False]),
                "secure": True
            }
        ]
        context.add_cookies(fake_cookies)
    except:
        pass

def handle_captcha_challenge(page: Page, max_retries=3):
    """Simplified CAPTCHA handler: Find button, hold, check page change"""
    
    for attempt in range(max_retries):
        try:
            print(f"\nCAPTCHA Handler - Attempt {attempt + 1}/{max_retries}")
            
            current_url = page.url
            print(f"Current URL: {current_url[:100]}...")
            
            if "captcha" not in current_url.lower():
                print("Not on CAPTCHA page")
                return False
            
            print("Waiting for CAPTCHA page to load...")
            page.wait_for_load_state("load", timeout=30000)
            print("Page loaded")
            
            time.sleep(3)
            
            # STRATEGY 1: Check main page first
            print("\n[Strategy 1] Searching main page...")
            button_found = False
            target_frame = page
            button_element = None
            
            # Search for button in main page
            button_element = page.locator("text=/PRESS.*HOLD/i").first  # Case-insensitive regex for "PRESS & HOLD"
            if button_element.is_visible():
                print("[Strategy 1] Button found in main page!")
                button_found = True
            
            # STRATEGY 2: Search in iframes if not found
            if not button_found:
                print("[Strategy 1] Not found in main page")
                print("\n[Strategy 2] Searching iframes...")
                
                frames = page.frames
                print(f"Found {len(frames)} frames total")
                
                for idx, frame in enumerate(frames):
                    try:
                        frame_url = frame.url
                        print(f"  Frame {idx}: {frame_url[:60]}...")
                        
                        # Log frame content for debugging
                        try:
                            frame_content = frame.content()
                            print(f"  Frame {idx} content (first 200 chars): {frame_content[:200]}...")
                        except Exception as e:
                            print(f"  Frame {idx} content error: {str(e)[:50]}")
                        
                        # Search for button in frame
                        button_element = frame.locator("text=/PRESS.*HOLD/i").first
                        if button_element.is_visible():
                            print(f"  SUCCESS! Button found in frame {idx}")
                            target_frame = frame
                            button_found = True
                            break
                            
                    except Exception as e:
                        print(f"  Frame {idx} error: {str(e)[:50]}")
                        continue
            
            if not button_found:
                print("\nButton not found in any frame")
                try:
                    timestamp = int(time.time())
                    page.screenshot(path=f"debug_no_button_{timestamp}.png", full_page=True)
                    print(f"Screenshot saved: debug_no_button_{timestamp}.png")
                except Exception as e:
                    print(f"Screenshot error: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                continue
            
            # INTERACT WITH BUTTON
            print("\nButton found! Getting position...")
            try:
                bounding_box = button_element.bounding_box()
                if bounding_box:
                    center_x = bounding_box['x'] + bounding_box['width'] / 2
                    center_y = bounding_box['y'] + bounding_box['height'] / 2
                    print(f"  Button position (page coordinates): ({center_x:.1f}, {center_y:.1f})")
                    print(f"  Size: {bounding_box['width']:.1f} x {bounding_box['height']:.1f}")
                else:
                    print("  Bounding box not available, skipping interaction")
                    continue
            except Exception as e:
                print(f"  Error getting button position: {e}")
                continue
            
            print("\nMoving to button...")
            page.mouse.move(center_x, center_y, steps=25)
            time.sleep(random.uniform(0.3, 0.6))
            
            print("Pressing button...")
            page.mouse.down()
            
            try:
                timestamp = int(time.time())
                page.screenshot(path=f"debug_button_press_{timestamp}.png", full_page=True)
                print(f"Screenshot saved: debug_button_press_{timestamp}.png")
            except Exception as e:
                print(f"Screenshot error: {e}")
            
            # Hold and monitor page change
            hold_duration = 90
            start_time = time.time()
            print(f"Holding for up to {hold_duration} seconds...")
            print("(Will auto-release if CAPTCHA page changes)")
            
            while time.time() - start_time < hold_duration:
                elapsed = time.time() - start_time
                
                # Check if CAPTCHA is solved (page reloaded, no 'captcha' in URL)
                try:
                    current = page.url
                    if "captcha" not in current.lower():
                        print(f"\nCAPTCHA SOLVED! Redirected after {elapsed:.1f}s")
                        page.mouse.up()
                        return True
                except:
                    pass
                
                if int(elapsed) % 3 == 0 and elapsed % 1 < 0.5:
                    print(f"  Holding... {int(elapsed)}s")
                time.sleep(0.5)
            
            # Release after timeout
            page.mouse.up()
            print("\nReleased button after full duration")
            
            try:
                timestamp = int(time.time())
                page.screenshot(path=f"debug_button_release_{timestamp}.png", full_page=True)
                print(f"Screenshot saved: debug_button_release_{timestamp}.png")
            except Exception as e:
                print(f"Screenshot error: {e}")
            
            time.sleep(3)
            
            # Final check
            if "captcha" not in page.url.lower():
                print("CAPTCHA bypassed successfully!")
                return True
            else:
                print("Still on CAPTCHA page")
                if attempt < max_retries - 1:
                    print("Retrying...")
                    time.sleep(5)
                
        except Exception as e:
            print(f"Error in attempt {attempt + 1}: {e}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries - 1:
                time.sleep(5)
    
    print("\nAll attempts exhausted")
    return False

def ultimate_human_browsing(page: Page):
    try:
        print("Starting human behavior simulation...")

        preserved_cookies = []

        def handle_page_load():
            print("Page load detected")
            if "captcha" in page.url.lower():
                print("CAPTCHA page detected")
            else:
                current_cookies = page.context.cookies()
                for cookie in current_cookies:
                    if cookie["name"].startswith("_px"):
                        if cookie not in preserved_cookies:
                            preserved_cookies.append(cookie)
                page.context.clear_cookies()
                if preserved_cookies:
                    page.context.add_cookies(preserved_cookies)
                inject_fake_cookies(page.context)

        def handle_response(response):
            url = response.url
            if "captcha-v2/index.html" in url:
                print(f"Main CAPTCHA page detected: {url[:80]}...")

        page.on("load", handle_page_load)
        page.on("response", handle_response)

        google_url = "https://www.google.co.in/"
        print(f"\nNavigating to Google: {google_url}")
        
        for attempt in range(3):
            try:
                page.goto(google_url, timeout=60000, wait_until="networkidle")
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    return False
        
        time.sleep(3)
        if "captcha" in page.url.lower():
            print("\nCAPTCHA detected after Google")
            if not handle_captcha_challenge(page):
                print("Failed to bypass CAPTCHA")
                return False

        for url in TARGET_URLS:
            print(f"\n{'='*60}")
            print(f"Navigating to: {url}")
            print(f"{'='*60}")
            
            for attempt in range(3):
                try:
                    page.goto(url, timeout=60000, wait_until="networkidle")
                    break
                except Exception as e:
                    print(f"Navigation attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        print(f"Failed to load {url}")
                        continue
            
            time.sleep(5)  # Wait for page to render
            
            if "captcha" in page.url.lower():
                print(f"\nCAPTCHA detected on {url}")
                if not handle_captcha_challenge(page):
                    print("Failed to bypass CAPTCHA, skipping this URL")
                    continue
            
            # Fill form fields
            if url == "https://skyscanner.pxf.io/c/5989167/1027991/13416?SharedId=Marc":
                print("Filling form fields...")
                # Origin input
                origin_input = page.locator("#originInput-input")
                if origin_input.is_visible():
                    origin_code = random.choice(list(AIRPORT_CODES.keys()))
                    origin_input.fill(AIRPORT_CODES[origin_code])
                    print(f"Set origin to: {AIRPORT_CODES[origin_code]}")
                
                # Destination input
                dest_input = page.locator("#destinationInput-input")
                if dest_input.is_visible():
                    dest_code = random.choice([code for code in AIRPORT_CODES.keys() if code != origin_code])
                    dest_input.fill(AIRPORT_CODES[dest_code])
                    print(f"Set destination to: {AIRPORT_CODES[dest_code]}")
                
                # Find and click departure button in main or frames
                departure_found = False
                departure_element = page.locator("button.DatePickerInputButton_DepartDateButton__NmViO")
                if departure_element.is_visible():
                    departure_found = True
                    departure_element.click()
                    print("Clicked departure button in main page to open date picker")
                else:
                    frames = page.frames
                    print(f"Searching {len(frames)} frames for departure button...")
                    for idx, frame in enumerate(frames):
                        try:
                            departure_element = frame.locator("button.DatePickerInputButton_DepartDateButton__NmViO")
                            if departure_element.is_visible():
                                departure_found = True
                                departure_element.click()
                                print(f"Clicked departure button in frame {idx} to open date picker")
                                break
                        except Exception as e:
                            print(f"  Frame {idx} error for departure button: {str(e)[:50]}")
                
                if not departure_found:
                    print("Warning: Departure button not found")
                else:
                    time.sleep(2)  # Wait for calendar to load
                    
                    # Select a random date from the visible calendar in main or frames
                    date_buttons_found = False
                    date_buttons = page.locator("button.BpkCalendarDate_bpk-calendar-date__ZmE2M")
                    if date_buttons.count() > 0:
                        date_buttons_found = True
                        random_button = date_buttons.nth(random.randint(0, date_buttons.count() - 1))
                        aria_label = random_button.get_attribute("aria-label")
                        random_button.click()
                        print(f"Selected random departure date in main page: {aria_label}")
                    else:
                        frames = page.frames
                        print(f"Searching {len(frames)} frames for date buttons...")
                        for idx, frame in enumerate(frames):
                            try:
                                date_buttons = frame.locator("button.BpkCalendarDate_bpk-calendar-date__ZmE2M")
                                if date_buttons.count() > 0:
                                    date_buttons_found = True
                                    random_button = date_buttons.nth(random.randint(0, date_buttons.count() - 1))
                                    aria_label = random_button.get_attribute("aria-label")
                                    random_button.click()
                                    print(f"Selected random departure date in frame {idx}: {aria_label}")
                                    break
                            except Exception as e:
                                print(f"  Frame {idx} error for date buttons: {str(e)[:50]}")
                    
                    if not date_buttons_found:
                        print("Warning: No date buttons found in calendar.")
                
                # Click search button
                search_button = page.locator("button[data-testid='mobile-cta']")
                if search_button.is_visible():
                    search_button.click()
                    print("Clicked Search button")
                    time.sleep(random.uniform(2, 5))
            
            page_wait = random.uniform(*PAGE_LOAD_PATIENCE)
            print(f"Page loaded, waiting {page_wait:.1f}s")
            time.sleep(page_wait)
            
            try:
                page_height = page.evaluate("document.body.scrollHeight")
                scroll_steps = random.randint(3, 6)
                for _ in range(scroll_steps):
                    scroll_distance = random.randint(200, 500)
                    page.evaluate(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
                    time.sleep(random.uniform(1, 2))
                print("Page scrolled")
            except Exception as e:
                print(f"Scroll error: {e}")
            
            human_time = random.uniform(*HUMAN_BEHAVIOR_TIME)
            print(f"Simulating human behavior for {human_time:.1f}s")
            start_time = time.time()
            
            while time.time() - start_time < human_time:
                action = random.choice(['scroll', 'mouse_move', 'pause'])
                
                if action == 'scroll':
                    page.evaluate(f"window.scrollBy({{top: {random.randint(50, 150)}, behavior: 'smooth'}});")
                elif action == 'mouse_move':
                    page.mouse.move(random.randint(100, 800), random.randint(100, 600))
                else:
                    time.sleep(random.uniform(1, 3))
                
                time.sleep(random.uniform(1, 2))
        
        print("\nHuman behavior simulation complete")
        return True
        
    except Exception as e:
        print(f"Human browsing error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            page.remove_listener("load", handle_page_load)
            page.remove_listener("response", handle_response)
        except:
            pass

def run_ultimate_stealth_test():
    print("STEALTH MODE WITH IFRAME-AWARE CAPTCHA BYPASS")
    print("=" * 60)
    
    successful_runs = 0
    
    for profile_num in range(1, TOTAL_PROFILES + 1):
        print(f"\n=== PROFILE {profile_num}/{TOTAL_PROFILES} ===")
        
        profile_name = f"stealth_iframe_bypass_{profile_num}_{random.randint(100000, 999999)}"
        
        proxy_config = None
        if PROXY_LIST:
            proxy_str = random.choice(PROXY_LIST)
            proxy_config = parse_proxy_string(proxy_str)
        
        profile_id = create_ultimate_stealth_profile(profile_name, proxy_config)
        
        if profile_id:
            wait_time = random.uniform(4, 8)
            print(f"Pre-start preparation: {wait_time:.1f}s")
            time.sleep(wait_time)
            
            gl, pw, browser, page = start_maximum_stealth_browser(profile_id)
            
            if page:
                try:
                    success = ultimate_human_browsing(page)
                    
                    if success:
                        successful_runs += 1
                        print(f"\nPROFILE {profile_num} - SUCCESS!")
                    else:
                        print(f"\nPROFILE {profile_num} - FAILED")
                    
                    session_time = random.uniform(10, 20)
                    print(f"Session cleanup in {session_time:.1f}s")
                    time.sleep(session_time)
                  
                finally:
                    cleanup_browser(gl, pw, browser)
            else:
                print(f"PROFILE {profile_num} - BROWSER START FAILED")
        else:
            print(f"PROFILE {profile_num} - PROFILE CREATION FAILED")

    print(f"\n{'='*60}")
    print(f"TEST COMPLETE!")
    print(f"Success Rate: {successful_runs}/{TOTAL_PROFILES}")
    print(f"{'='*60}")

def cleanup_browser(gl: GoLogin, pw: Playwright, browser: Browser):
    try:
        if browser:
            browser.close()
        time.sleep(1)
        if gl:
            gl.stop()
        if pw:
            pw.stop()
        print("Browser session terminated")
    except Exception as e:
        print(f"Cleanup warning: {e}")

if __name__ == "__main__":
    print("ANTI-BOT DETECTION BYPASS WITH IFRAME-AWARE CAPTCHA SOLVER")
    print("=" * 60)

    if not GOLOGIN_AVAILABLE:
        print("GoLogin not available!")
        exit(1)
    
    try:
        run_ultimate_stealth_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()