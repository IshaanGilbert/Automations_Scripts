# import asyncio
# import random
# import string
# from playwright.async_api import async_playwright

# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "hotmail.com"]
#     return f"{name}{num}@{random.choice(domains)}"

# def generate_name():
#     first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun"]
#     last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
#     return random.choice(first), random.choice(last)

# async def main():
#     url = "https://app.adstracking.io/click?pid=3030&offer_id=20655"

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=False,
#             args=['--start-maximized', '--disable-blink-features=AutomationControlled']
#         )

#         context = await browser.new_context(
#             viewport={"width": 1440, "height": 900},
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
#         )

#         page = await context.new_page()

#         try:
#             print("🌐 Opening Magzter Gold Offer Page...")
#             await page.goto(url, timeout=90000, wait_until="domcontentloaded")
#             print("✅ Page Loaded!")

#             await page.wait_for_timeout(4000)

#             # Claim Now
#             print("🔘 Clicking 'Claim Now'...")
#             await page.click('button:has-text("Claim Now")', timeout=15000)
#             await page.wait_for_timeout(5000)

#             # Email
#             email = generate_random_email()
#             print(f"📧 Filling Email: {email}")
#             await page.fill('input[type="email"]', email)
#             await page.wait_for_timeout(2000)

#             # Continue after Email
#             print("🔄 Clicking Continue...")
#             await page.click('button:has-text("Continue")', timeout=10000)
#             await page.wait_for_timeout(6000)

#             # Name + Zip Code
#             first_name, last_name = generate_name()
#             print(f"👤 Filling Name: {first_name} {last_name}")

#             await page.fill('input[name="firstName"], input[placeholder*="First Name"]', first_name)
#             await page.fill('input[name="lastName"], input[placeholder*="Last Name"]', last_name)
#             await page.fill('input[name="zipCode"], input[placeholder*="Zip Code"]', "000000")

#             await page.wait_for_timeout(3000)

#             # Continue after Details
#             print("🔄 Clicking Continue after Name & Zip...")
#             # Stronger selector for submit button
#             await page.click('button#submitBtn, button.svelte-xdpg18', timeout=12000)
#             print("✅ Continue Clicked!")
#             await page.wait_for_timeout(8000)

#             # Card Number
#             print("💳 Filling Card Number...")
#             await page.fill('input#cardNumber, input[name="cardNumber"]', "0000000000000000")
#             await page.wait_for_timeout(4000)

#             print("\n🎉 Script Completed Up to Card Details!")
#             print("Browser abhi khula hai...")

#             await asyncio.sleep(300)   # 5 minutes tak khula rahega

#         except Exception as e:
#             print(f"❌ Error: {e}")
#         finally:
#             # await browser.close()
#             pass

# asyncio.run(main())






# import asyncio
# import random
# import string
# import json
# import os
# from datetime import datetime
# from playwright.async_api import async_playwright

# # ================= CONFIG =================
# HEADLESS = False
# TOTAL_RUNS = 10          # Kitni baar script chalani hai
# LOG_FILE = "magzter_logs.json"

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

# async def run_one_cycle(run_number):
#     url = "https://www.magzter.com/magztergold/1year-subscription-offer?utm_source=affle-cps&pub_id=3030_&click_id=6a29c10562fcda00014a6b12"

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=HEADLESS,
#             args=['--start-maximized', '--disable-blink-features=AutomationControlled']
#         )

#         context = await browser.new_context(
#             viewport={"width": 1440, "height": 900},
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
#         )

#         page = await context.new_page()
#         status = "failed"
#         email = "test@example.com"

#         try:
#             print(f"\n🚀 === Run #{run_number} Started ===")
#             await page.goto(url, timeout=90000, wait_until="domcontentloaded")
#             await page.wait_for_timeout(4000)

#             # Claim Now
#             await page.click('button:has-text("Claim Now")', timeout=15000)
#             await page.wait_for_timeout(5000)

#             # Email
#             email = generate_random_email()
#             print(f"📧 Email: {email}")
#             await page.fill('input[type="email"]', email)
#             await page.wait_for_timeout(2000)
#             await page.click('button:has-text("Continue")', timeout=10000)
#             await page.wait_for_timeout(6000)

#             # Name + Zip
#             first_name, last_name = generate_name()
#             await page.fill('input[placeholder*="First Name"]', first_name)
#             await page.fill('input[placeholder*="Last Name"]', last_name)
#             await page.fill('input[placeholder*="Zip Code"]', "000000")
#             await page.wait_for_timeout(3000)

#             # Continue
#             await page.click('button#submitBtn, button.svelte-xdpg18', timeout=12000)
#             await page.wait_for_timeout(8000)

#             # Payment Details
#             print("💳 Filling Card Details...")
#             await page.fill('input#cardNumber', "0000000000000000")
#             await page.fill('input#cardExpiry', "0312")          # MMYY
#             await page.fill('input#cardCvc', "123")
#             await page.fill('input#billingName', "john doe")
#             await page.wait_for_timeout(3000)

#             print(f"✅ Run #{run_number} Completed Successfully!")
#             status = "success"

#         except Exception as e:
#             print(f"❌ Run #{run_number} Failed: {e}")
#             status = "failed"
#         finally:
#             log_data = {
#                 "run_number": run_number,
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "email": email,
#                 "status": status,
#                 "error": str(e)[:200] if 'e' in locals() else None
#             }
#             save_log(log_data)
#             await browser.close()

# # ================= MULTIPLE RUNS =================
# async def main():
#     print("=== Magzter Gold Auto Subscription Script ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         await run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             wait_time = random.uniform(15, 30)
#             print(f"⏳ Waiting {wait_time:.1f} seconds before next run...")
#             await asyncio.sleep(wait_time)

#     print("\n🎉 All Runs Completed!")

# asyncio.run(main())






# import asyncio
# import random
# import string
# import json
# import os
# from datetime import datetime
# from playwright.async_api import async_playwright

# # ================= CONFIG =================
# HEADLESS = False
# TOTAL_RUNS = 10          # Kitni baar script chalani hai
# LOG_FILE = "magzter_logs.json"

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

# async def run_one_cycle(run_number):
#     url = "https://app.adstracking.io/click?pid=3030&offer_id=20655"

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=HEADLESS,
#             args=['--start-maximized', '--disable-blink-features=AutomationControlled']
#         )

#         context = await browser.new_context(
#             viewport={"width": 1440, "height": 900},
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
#         )

#         page = await context.new_page()
#         status = "failed"
#         email = "test@example.com"

#         try:
#             print(f"\n🚀 === Run #{run_number} Started ===")
#             await page.goto(url, timeout=90000, wait_until="domcontentloaded")
#             await page.wait_for_timeout(4000)

#             # Claim Now
#             await page.click('button:has-text("Claim Now")', timeout=15000)
#             await page.wait_for_timeout(5000)

#             # Email
#             email = generate_random_email()
#             print(f"📧 Email: {email}")
#             await page.fill('input[type="email"]', email)
#             await page.wait_for_timeout(2000)
#             await page.click('button:has-text("Continue")', timeout=10000)
#             await page.wait_for_timeout(6000)

#             # Name + Zip
#             first_name, last_name = generate_name()
#             await page.fill('input[placeholder*="First Name"]', first_name)
#             await page.fill('input[placeholder*="Last Name"]', last_name)
#             await page.fill('input[placeholder*="Zip Code"]', "000000")
#             await page.wait_for_timeout(3000)

#             # Continue (after name+zip)
#             await page.click('button#submitBtn, button.svelte-xdpg18', timeout=15000)
#             await page.wait_for_timeout(8000)

#             # Payment Details
#             print("💳 Filling Card Details...")
#             await page.fill('input#cardNumber', "0000000000000000")
#             await page.fill('input#cardExpiry', "06/28")          # MMYY
#             await page.fill('input#cardCvc', "172")
#             await page.fill('input#billingName', "rajat dalal")
#             await page.wait_for_timeout(4000)

#             # ================= NEW PART START =================
#             print("🔘 Clicking Submit Button with Spinner...")
#             await page.click('div.SubmitButton-IconContainer', timeout=15000)
#             await page.wait_for_timeout(8000)   # form open hone ka wait

#             # Corporate ID & Employee ID
#             print("🏢 Filling Corporate & Employee ID...")
#             await page.fill('input#corporateId', "YOUR_CORPORATE_ID")      # ← Yahan apna daalo
#             await page.fill('input#employeeId', "YOUR_EMPLOYEE_ID")        # ← Yahan apna daalo
#             await page.wait_for_timeout(3000)

#             # Submit Corporate Form
#             await page.click('a.btn.primary__btn:has-text("Submit"), a.btn.primary__btn', timeout=12000)
#             await page.wait_for_timeout(7000)

#             # OTP Form
#             print("🔐 OTP Form aaya - OTP daalo")
#             # Manual OTP ke liye pause (sabse safe)
#             print("⚠️  Browser mein OTP daal do aur yahan Enter press karo...")
#             input("Press Enter after entering OTP...")

#             # OTP Submit
#             await page.click('button#submitBtn, button.submit:has-text("SUBMIT")', timeout=12000)
#             await page.wait_for_timeout(8000)

#             print(f"✅ Run #{run_number} Completed Successfully!")
#             status = "success"

#         except Exception as e:
#             print(f"❌ Run #{run_number} Failed: {e}")
#             status = "failed"
#         finally:
#             log_data = {
#                 "run_number": run_number,
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "email": email,
#                 "status": status,
#                 "error": str(e)[:300] if 'e' in locals() else None
#             }
#             save_log(log_data)
#             await browser.close()

# # ================= MULTIPLE RUNS =================
# async def main():
#     print("=== Magzter Gold Auto Subscription Script ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         await run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             wait_time = random.uniform(15, 30)
#             print(f"⏳ Waiting {wait_time:.1f} seconds before next run...")
#             await asyncio.sleep(wait_time)

#     print("\n🎉 All Runs Completed!")

# asyncio.run(main())





# import asyncio
# import random
# import string
# import json
# import os
# import tempfile
# from datetime import datetime
# from playwright.async_api import async_playwright

# # ================= GEONODE CONFIG =================
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS      = "CHANGE_ME_SECRET"
# GEONODE_HOST      = "sg.proxy.geonode.io"
# GEONODE_PORT      = "11000"

# COUNTRIES = ["IT", "GR", "CH", "AT"]

# # ================= CONFIG =================
# HEADLESS = False
# TOTAL_RUNS = 10
# LOG_FILE = "magzter_logs.json"

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

# def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass):
#     manifest_json = {
#         "version": "1.0.0",
#         "manifest_version": 2,
#         "name": "Proxy Auth",
#         "permissions": ["proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"],
#         "background": {"scripts": ["background.js"]},
#         "minimum_chrome_version": "22.0.0"
#     }

#     background_js = f"""
#     var config = {{
#         mode: "fixed_servers",
#         rules: {{
#             singleProxy: {{
#                 scheme: "socks5",
#                 host: "{proxy_host}",
#                 port: parseInt({proxy_port})
#             }},
#             bypassList: ["localhost"]
#         }}
#     }};
#     chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
#     function callbackFn(details) {{
#         return {{
#             authCredentials: {{ username: "{proxy_user}", password: "CHANGE_ME_PASSWORD" }}
#         }};
#     }}
#     chrome.webRequest.onAuthRequired.addListener(callbackFn, {{urls: ["<all_urls>"]}}, ['blocking']);
#     """

#     tmp_dir = tempfile.mkdtemp()
#     ext_dir = os.path.join(tmp_dir, "proxy_auth")
#     os.makedirs(ext_dir, exist_ok=True)

#     with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
#         json.dump(manifest_json, f, indent=2)
#     with open(os.path.join(ext_dir, "background.js"), "w") as f:
#         f.write(background_js)

#     return ext_dir

# async def run_one_cycle(run_number):
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
   
#     print(f"\n🚀 === Run #{run_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy: {username}@{GEONODE_HOST}:{GEONODE_PORT}")

#     url = "https://app.adstracking.io/click?pid=3030&offer_id=20655"

#     async with async_playwright() as p:
#         extension_path = create_proxy_auth_extension(GEONODE_HOST, GEONODE_PORT, username, GEONODE_PASS)

#         browser = await p.chromium.launch(
#             headless=HEADLESS,
#             args=[
#                 '--start-maximized',
#                 '--disable-blink-features=AutomationControlled',
#                 '--no-sandbox',
#                 '--disable-dev-shm-usage',
#                 '--disable-blink-features=AutomationControlled',
#                 '--disable-features=IsolateOrigins,site-per-process',
#                 f'--load-extension={extension_path}',
#                 '--disable-extensions-except=' + extension_path
#             ]
#         )

#         # ================= IMPROVED FINGERPRINTING =================
#         context = await browser.new_context(
#             viewport={"width": random.randint(1366, 1920), "height": random.randint(768, 1080)},
#             user_agent=random.choice([
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
#             ]),
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#             permissions=["geolocation"],
#             geolocation={"latitude": 28.6139, "longitude": 77.2090},  # Delhi approx
#             has_touch=random.choice([True, False]),
#             is_mobile=random.choice([True, False]),
#             bypass_csp=True,
#             ignore_https_errors=True,
#             # Extra anti-detection
#             extra_http_headers={
#                 "Accept-Language": "en-US,en;q=0.9",
#                 "Sec-Fetch-Site": "none",
#                 "Sec-Fetch-Mode": "navigate"
#             }
#         )

#         # Hide automation flags
#         await context.add_init_script("""
#             Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#             Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
#             Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
#             window.chrome = { runtime: {} };
#         """)

#         page = await context.new_page()
#         status = "failed"
#         email = "test@example.com"

#         try:
#             print(f"\n🚀 === Run #{run_number} Started ===")
#             await page.goto(url, timeout=90000, wait_until="domcontentloaded")
#             await page.wait_for_timeout(random.randint(3000, 6000))

#             # Human-like random movement
#             await page.mouse.move(random.randint(100, 600), random.randint(100, 400))
#             await page.wait_for_timeout(800)

#             # Claim Now
#             await page.click('button:has-text("Claim Now")', timeout=20000)
#             await page.wait_for_timeout(random.randint(4000, 7000))

#             # Email
#             email = generate_random_email()
#             print(f"📧 Email: {email}")
#             await page.fill('input[type="email"]', email)
#             await page.wait_for_timeout(random.randint(1500, 3000))
#             await page.click('button:has-text("Continue")', timeout=20000)
#             await page.wait_for_timeout(random.randint(5000, 8000))

#             # Name + Zip
#             first_name, last_name = generate_name()
#             await page.fill('input[placeholder*="First Name"]', first_name)
#             await page.fill('input[placeholder*="Last Name"]', last_name)
#             await page.fill('input[placeholder*="Zip Code"]', "000000")
#             await page.wait_for_timeout(random.randint(2000, 4000))

#             # Continue
#             await page.click('button#submitBtn, button.svelte-xdpg18', timeout=25000)
#             await page.wait_for_timeout(random.randint(6000, 9000))

#             # Payment Details
#             print("💳 Filling Card Details...")
#             await page.fill('input#cardNumber', "0000000000000000")
#             await page.fill('input#cardExpiry', "06/28")
#             await page.fill('input#cardCvc', "172")
#             await page.fill('input#billingName', "rajat dalal")
#             await page.wait_for_timeout(random.randint(3000, 5000))

#             # Corporate Form
#             print("🔘 Clicking Submit Button...")
#             await page.click('div.SubmitButton-IconContainer', timeout=20000)
#             await page.wait_for_timeout(random.randint(6000, 9000))

#             await page.fill('input#corporateId', "YOUR_CORPORATE_ID")
#             await page.fill('input#employeeId', "YOUR_EMPLOYEE_ID")
#             await page.wait_for_timeout(random.randint(2000, 4000))

#             await page.click('a.btn.primary__btn:has-text("Submit"), a.btn.primary__btn', timeout=15000)
#             await page.wait_for_timeout(random.randint(5000, 8000))

#             # OTP
#             print("🔐 OTP Form aaya - OTP daalo")
#             print("⚠️ Browser mein OTP daal do aur yahan Enter press karo...")
#             input("Press Enter after entering OTP...")

#             await page.click('button#submitBtn, button.submit:has-text("SUBMIT")', timeout=15000)
#             await page.wait_for_timeout(8000)

#             print(f"✅ Run #{run_number} Completed Successfully!")
#             status = "success"

#         except Exception as e:
#             print(f"❌ Run #{run_number} Failed: {e}")
#             status = "failed"
#         finally:
#             log_data = {
#                 "run_number": run_number,
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "email": email,
#                 "country": country_code,
#                 "status": status,
#                 "error": str(e)[:300] if 'e' in locals() else None
#             }
#             save_log(log_data)
#             await browser.close()

# # ================= MULTIPLE RUNS =================
# async def main():
#     print("=== Magzter Gold Auto Subscription Script with Geonode + Anti-Bot ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         await run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             wait_time = random.uniform(20, 45)
#             print(f"⏳ Waiting {wait_time:.1f} seconds before next run...")
#             await asyncio.sleep(wait_time)

#     print("\n🎉 All Runs Completed!")

# asyncio.run(main())






# import asyncio
# import random
# import string
# import json
# import os
# import tempfile
# from datetime import datetime
# from playwright.async_api import async_playwright

# # ================= GEONODE CONFIG =================
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS      = "CHANGE_ME_SECRET"
# GEONODE_HOST      = "sg.proxy.geonode.io"
# GEONODE_PORT      = "11000"

# COUNTRIES = ["IT", "GR", "CH", "AT"]

# # ================= CONFIG =================
# HEADLESS = False
# TOTAL_RUNS = 10
# LOG_FILE = "magzter_logs.json"

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

# def create_proxy_auth_extension_v3(proxy_host, proxy_port, proxy_user, proxy_pass):
#     """Manifest V3 Compatible Proxy Extension"""
#     manifest_json = {
#         "version": "1.0.0",
#         "manifest_version": 3,
#         "name": "Proxy Auth",
#         "permissions": [
#             "proxy",
#             "webRequest",
#             "webRequestAuthProvider",
#             "storage",
#             "unlimitedStorage"
#         ],
#         "host_permissions": ["<all_urls>"],
#         "background": {
#             "service_worker": "background.js"
#         },
#         "minimum_chrome_version": "110.0.0"
#     }

#     background_js = f"""
#     chrome.proxy.settings.set({{
#         value: {{
#             mode: "fixed_servers",
#             rules: {{
#                 singleProxy: {{
#                     scheme: "socks5",
#                     host: "{proxy_host}",
#                     port: parseInt({proxy_port})
#                 }},
#                 bypassList: ["localhost"]
#             }}
#         }},
#         scope: "regular"
#     }}, () => {{}});

#     chrome.webRequest.onAuthRequired.addListener(
#         (details) => {{
#             return {{
#                 authCredentials: {{
#                     username: "{proxy_user}",
#                     password: "CHANGE_ME_PASSWORD"
#                 }}
#             }};
#         }},
#         {{ urls: ["<all_urls>"] }},
#         ["asyncBlocking"]
#     );
#     """

#     tmp_dir = tempfile.mkdtemp()
#     ext_dir = os.path.join(tmp_dir, "proxy_auth_v3")
#     os.makedirs(ext_dir, exist_ok=True)

#     with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
#         json.dump(manifest_json, f, indent=2)
#     with open(os.path.join(ext_dir, "background.js"), "w") as f:
#         f.write(background_js)

#     return ext_dir

# async def run_one_cycle(run_number):
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
   
#     print(f"\n🚀 === Run #{run_number} | Country: {country_code} ===")
#     print(f"🔗 Proxy: {username}@{GEONODE_HOST}:{GEONODE_PORT}")

#     url = "https://app.adstracking.io/click?pid=3030&offer_id=20655"

#     async with async_playwright() as p:
#         extension_path = create_proxy_auth_extension_v3(GEONODE_HOST, GEONODE_PORT, username, GEONODE_PASS)

#         browser = await p.chromium.launch(
#             headless=HEADLESS,
#             args=[
#                 '--start-maximized',
#                 '--disable-blink-features=AutomationControlled',
#                 '--no-sandbox',
#                 '--disable-dev-shm-usage',
#                 '--disable-features=IsolateOrigins,site-per-process',
#                 f'--load-extension={extension_path}',
#                 '--disable-extensions-except=' + extension_path
#             ]
#         )

#         # ================= STRONG FINGERPRINTING =================
#         context = await browser.new_context(
#             viewport={"width": random.randint(1366, 1920), "height": random.randint(768, 1080)},
#             user_agent=random.choice([
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
#             ]),
#             locale="en-US",
#             timezone_id="Asia/Kolkata",
#             geolocation={"latitude": 28.6139, "longitude": 77.2090},
#             permissions=["geolocation"],
#             has_touch=False,
#             is_mobile=False,
#             bypass_csp=True,
#             ignore_https_errors=True,
#             extra_http_headers={
#                 "Accept-Language": "en-US,en;q=0.9",
#                 "Sec-Ch-Ua": '"Chromium";v="134", "Not;A=Brand";v="99"',
#                 "Sec-Ch-Ua-Mobile": "9999999999",
#                 "Sec-Ch-Ua-Platform": '"Windows"'
#             }
#         )

#         # Advanced Anti-Detection
#         await context.add_init_script("""
#             () => {
#                 Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#                 Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
#                 Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
#                 window.chrome = { runtime: {}, app: {}, webstore: {} };
                
#                 // Canvas & WebGL Fingerprint Randomization
#                 const originalGetContext = HTMLCanvasElement.prototype.getContext;
#                 HTMLCanvasElement.prototype.getContext = function(type, ...args) {
#                     if (type === '2d') {
#                         const ctx = originalGetContext.call(this, type, ...args);
#                         const originalFillText = ctx.fillText;
#                         ctx.fillText = function(text, x, y, ...rest) {
#                             return originalFillText.call(this, text + Math.random().toString(36).slice(2,5), x, y, ...rest);
#                         };
#                         return ctx;
#                     }
#                     return originalGetContext.call(this, type, ...args);
#                 };
#             }
#         """)

#         page = await context.new_page()
#         status = "failed"
#         email = "test@example.com"

#         try:
#             print(f"\n🚀 === Run #{run_number} Started ===")
#             await page.goto(url, timeout=90000, wait_until="domcontentloaded")
#             await page.wait_for_timeout(random.randint(4000, 7000))

#             # Human-like mouse movement
#             await page.mouse.move(random.randint(200, 800), random.randint(100, 500), steps=25)
#             await page.wait_for_timeout(1200)

#             # Claim Now
#             await page.click('button:has-text("Claim Now")', timeout=20000)
#             await page.wait_for_timeout(random.randint(4000, 7000))

#             # Email + Continue
#             email = generate_random_email()
#             print(f"📧 Email: {email}")
#             await page.fill('input[type="email"]', email)
#             await page.wait_for_timeout(random.randint(1500, 3000))
#             await page.click('button:has-text("Continue")', timeout=20000)
#             await page.wait_for_timeout(random.randint(5000, 8000))

#             # Name + Zip
#             first_name, last_name = generate_name()
#             await page.fill('input[placeholder*="First Name"]', first_name)
#             await page.fill('input[placeholder*="Last Name"]', last_name)
#             await page.fill('input[placeholder*="Zip Code"]', "000000")
#             await page.wait_for_timeout(random.randint(2500, 4500))

#             # Continue
#             await page.click('button#submitBtn, button.svelte-xdpg18', timeout=25000)
#             await page.wait_for_timeout(random.randint(7000, 10000))

#             # Payment Details
#             print("💳 Filling Card Details...")
#             await page.fill('input#cardNumber', "0000000000000000")
#             await page.fill('input#cardExpiry', "06/28")
#             await page.fill('input#cardCvc', "172")
#             await page.fill('input#billingName', "rajat dalal")
#             await page.wait_for_timeout(random.randint(3000, 5000))

#             # Corporate Part
#             print("🔘 Clicking Submit Button...")
#             await page.click('div.SubmitButton-IconContainer', timeout=20000)
#             await page.wait_for_timeout(random.randint(6000, 9000))

#             await page.fill('input#corporateId', "streakads")
#             await page.fill('input#employeeId', "streakads1")
#             await page.wait_for_timeout(random.randint(2500, 4000))

#             await page.click('a.btn.primary__btn:has-text("Submit"), a.btn.primary__btn', timeout=15000)
#             await page.wait_for_timeout(random.randint(5000, 8000))

#             # OTP
#             print("🔐 OTP Form aaya - OTP daalo")
#             print("⚠️  Browser mein OTP daal do aur yahan Enter press karo...")
#             input("Press Enter after entering OTP...")

#             await page.click('button#submitBtn, button.submit:has-text("SUBMIT")', timeout=15000)
#             await page.wait_for_timeout(8000)

#             print(f"✅ Run #{run_number} Completed Successfully!")
#             status = "success"

#         except Exception as e:
#             print(f"❌ Run #{run_number} Failed: {e}")
#             status = "failed"
#         finally:
#             log_data = {
#                 "run_number": run_number,
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "email": email,
#                 "country": country_code,
#                 "status": status,
#                 "error": str(e)[:300] if 'e' in locals() else None
#             }
#             save_log(log_data)
#             await browser.close()

# # ================= MULTIPLE RUNS =================
# async def main():
#     print("=== Magzter Gold Script with Geonode + Strong Anti-Bot ===\n")
#     print(f"Total Runs: {TOTAL_RUNS}\n")

#     for i in range(1, TOTAL_RUNS + 1):
#         await run_one_cycle(i)
#         if i < TOTAL_RUNS:
#             wait_time = random.uniform(25, 50)
#             print(f"⏳ Waiting {wait_time:.1f} seconds before next run...")
#             await asyncio.sleep(wait_time)

#     print("\n🎉 All Runs Completed!")

# asyncio.run(main())







import asyncio
import random
import string
import json
import os
import tempfile
from datetime import datetime
from playwright.async_api import async_playwright

# ================= GEONODE CONFIG =================
GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
GEONODE_PASS      = "CHANGE_ME_SECRET"
GEONODE_HOST      = "sg.proxy.geonode.io"
GEONODE_PORT      = "11000"

COUNTRIES = ["IN"]

# ================= CONFIG =================
HEADLESS = False
TOTAL_RUNS = 10
LOG_FILE = "magzter_logs.json"

def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase, k=8))
    num = random.randint(100, 999)
    domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"]
    return f"{name}{num}@{random.choice(domains)}"

def generate_name():
    first = ["Amit", "Rahul", "Priya", "Sneha", "Vikas", "Neha", "Rohan", "Pooja", "Arjun", "Kiran"]
    last = ["Sharma", "Singh", "Kumar", "Verma", "Gupta", "Yadav", "Patel", "Jain"]
    return random.choice(first), random.choice(last)

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
    print(f"📝 Log Saved | Run #{data['run_number']}")

def create_proxy_auth_extension_v3(proxy_host, proxy_port, proxy_user, proxy_pass):
    manifest_json = {
        "version": "1.0.0",
        "manifest_version": 3,
        "name": "Proxy Auth",
        "permissions": ["proxy", "webRequest", "webRequestAuthProvider", "storage", "unlimitedStorage"],
        "host_permissions": ["<all_urls>"],
        "background": {"service_worker": "background.js"},
        "minimum_chrome_version": "110.0.0"
    }

    background_js = f"""
    chrome.proxy.settings.set({{ value: {{ mode: "fixed_servers", rules: {{ singleProxy: {{ scheme: "socks5", host: "{proxy_host}", port: parseInt({proxy_port}) }}, bypassList: ["localhost"] }} }}, scope: "regular" }}, () => {{}});
    chrome.webRequest.onAuthRequired.addListener((details) => {{ return {{ authCredentials: {{ username: "{proxy_user}", password: "CHANGE_ME_PASSWORD" }} }}; }}, {{ urls: ["<all_urls>"] }}, ["asyncBlocking"]);
    """

    tmp_dir = tempfile.mkdtemp()
    ext_dir = os.path.join(tmp_dir, "proxy_auth_v3")
    os.makedirs(ext_dir, exist_ok=True)

    with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
        json.dump(manifest_json, f, indent=2)
    with open(os.path.join(ext_dir, "background.js"), "w") as f:
        f.write(background_js)

    return ext_dir

async def run_one_cycle(run_number):
    country_code = random.choice(COUNTRIES)
    username = GEONODE_USER_BASE.format(country_code.lower())
   
    print(f"\n🚀 === Run #{run_number} | Country: {country_code} ===")
    print(f"🔗 Proxy: {username}@{GEONODE_HOST}:{GEONODE_PORT}")

    url = "https://app.adstracking.io/click?pid=3030&offer_id=20655"

    async with async_playwright() as p:
        extension_path = create_proxy_auth_extension_v3(GEONODE_HOST, GEONODE_PORT, username, GEONODE_PASS)

        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-features=IsolateOrigins,site-per-process,AutoExpandDetails',
                f'--load-extension={extension_path}',
                '--disable-extensions-except=' + extension_path
            ]
        )

        context = await browser.new_context(
            viewport={"width": random.randint(1366, 1920), "height": random.randint(768, 1080)},
            user_agent=random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
            ]),
            locale="en-US",
            timezone_id="Asia/Kolkata",
            geolocation={"latitude": 28.6139 + random.uniform(-0.5, 0.5), "longitude": 77.2090 + random.uniform(-0.5, 0.5)},
            permissions=["geolocation"],
            has_touch=False,
            is_mobile=False,
            bypass_csp=True,
            ignore_https_errors=True,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Ch-Ua": '"Not;A=Brand";v="99", "Chromium";v="134"',
                "Sec-Ch-Ua-Mobile": "9999999999",
                "Sec-Ch-Ua-Platform": '"Windows"'
            }
        )

        # === VERY STRONG ANTI-DETECTION ===
        await context.add_init_script("""
            () => {
                delete navigator.__proto__.webdriver;
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                
                window.chrome = { runtime: {}, app: {}, webstore: {} };
                Object.defineProperty(window, 'navigator', {value: navigator, configurable: true});
                
                // Canvas Fingerprint Spoof
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type) {
                    const ctx = originalGetContext.call(this, type);
                    if (type === '2d') {
                        const originalFillText = ctx.fillText;
                        ctx.fillText = function(text, x, y) {
                            originalFillText.call(this, text + Math.random().toString(36).substr(2, 4), x + Math.random(), y + Math.random());
                        };
                    }
                    return ctx;
                };
                
                // Randomize WebGL
                const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(param) {
                    if (param === 37445) return "Intel Inc.";
                    if (param === 37446) return "Intel(R) UHD Graphics";
                    return originalGetParameter.call(this, param);
                };
            }
        """)

        page = await context.new_page()

        # Extra stealth
        await page.add_init_script("""
            Object.defineProperty(document, 'visibilityState', {get: () => 'visible'});
            Object.defineProperty(document, 'hidden', {get: () => false});
        """)

        status = "failed"
        email = "test@example.com"

        try:
            print(f"\n🚀 === Run #{run_number} Started ===")
            
            await page.goto(url, timeout=90000, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(5000, 8000))

            # Heavy Human Simulation
            for _ in range(3):
                await page.mouse.move(random.randint(100, 1200), random.randint(100, 700), steps=random.randint(20, 35))
                await page.wait_for_timeout(random.randint(800, 1500))

            # Claim Now
            await page.click('button:has-text("Claim Now")', timeout=25000)
            await page.wait_for_timeout(random.randint(5000, 9000))

            email = generate_random_email()
            print(f"📧 Email: {email}")
            await page.fill('input[type="email"]', email)
            await page.wait_for_timeout(random.randint(2000, 4000))
            await page.click('button:has-text("Continue")', timeout=25000)
            await page.wait_for_timeout(random.randint(6000, 10000))

            # Name + Zip
            first_name, last_name = generate_name()
            await page.fill('input[placeholder*="First Name"]', first_name)
            await page.fill('input[placeholder*="Last Name"]', last_name)
            await page.fill('input[placeholder*="Zip Code"]', "000000")
            await page.wait_for_timeout(random.randint(3000, 5000))

            await page.click('button#submitBtn, button.svelte-xdpg18', timeout=30000)
            await page.wait_for_timeout(random.randint(7000, 12000))

            # Payment Details
            print("💳 Filling Card Details...")
            await page.fill('input#cardNumber', "0000000000000000 ")
            await page.fill('input#cardExpiry', "06/28")
            await page.fill('input#cardCvc', "164")
            await page.fill('input#billingName', "john doe")
            await page.wait_for_timeout(random.randint(4000, 6000))

            # Corporate
            print("🔘 Corporate Form...")
            await page.click('div.SubmitButton-IconContainer', timeout=25000)
            await page.wait_for_timeout(random.randint(6000, 10000))

            await page.fill('input#corporateId', "streakads")
            await page.fill('input#employeeId', "streakads1")
            await page.wait_for_timeout(random.randint(3000, 5000))

            await page.click('a.btn.primary__btn:has-text("Submit"), a.btn.primary__btn', timeout=20000)
            await page.wait_for_timeout(random.randint(6000, 9000))

            # OTP
            print("🔐 OTP Form aaya - OTP daalo")
            print("⚠️ Browser mein OTP daal do aur yahan Enter press karo...")
            input("Press Enter after entering OTP...")

            await page.click('button#submitBtn, button.submit:has-text("SUBMIT")', timeout=20000)
            await page.wait_for_timeout(8000)

            print(f"✅ Run #{run_number} Completed Successfully!")
            status = "success"

        except Exception as e:
            print(f"❌ Run #{run_number} Failed: {e}")
            status = "failed"
        finally:
            log_data = {
                "run_number": run_number,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "email": email,
                "country": country_code,
                "status": status,
                "error": str(e)[:300] if 'e' in locals() else None
            }
            save_log(log_data)
            await browser.close()

async def main():
    print("=== Magzter Gold Script - Max Stealth + Geonode ===\n")
    print(f"Total Runs: {TOTAL_RUNS}\n")

    for i in range(1, TOTAL_RUNS + 1):
        await run_one_cycle(i)
        if i < TOTAL_RUNS:
            wait_time = random.uniform(30, 60)
            print(f"⏳ Waiting {wait_time:.1f} seconds before next run...")
            await asyncio.sleep(wait_time)

    print("\n🎉 All Runs Completed!")

asyncio.run(main())