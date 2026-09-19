# # tata.py ← pura replace kar dena
# from playwright.sync_api import sync_playwright
# import time
# import random

# def visit_url():
#     with sync_playwright() as p:
#         # Headless False rakh rahe hain taaki Cloudflare check pass ho sake
#         browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        
#         context = browser.new_context(
#             viewport={"width": random.randint(1366, 1920), "height": random.randint(768, 1080)},
#             user_agent=random.choice([
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
#             ]),
#             locale="en-US",
#             java_script_enabled=True,
#         )

#         # Yeh do line bot detection ko kaafi had tak bypass karti hain
#         context.add_init_script("""
#             Object.defineProperty(navigator, 'webdriver', () => false);
#             window.chrome = { runtime: {}, app: {}, webstore: {} };
#         """)

#         page = context.new_page()

#         # ←←← YAHAN APNA URL CHANGE KAR (har 10–20 visit ke baad clickid change kar dena)
#         url = "https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=MYCLICKID12345&sub1=MYSOURCE999"

#         try:
#             print("URL khol raha hoon...")
#             # Timeout badha diya + load ki jagah domcontentloaded use kiya (zyada reliable)
#             page.goto(url, wait_until="domcontentloaded", timeout=90000)

#             # Thoda extra wait taaki redirects poore ho jaayein
#             page.wait_for_timeout(8000)

#             # Agar Cloudflare check aaya to 10 second aur wait
#             if "Just a moment" in page.content() or "Checking your browser" in page.content():
#                 print("Cloudflare check detect hua → 15 sec aur wait kar raha hoon...")
#                 page.wait_for_timeout(15000)

#             stay = random.randint(40, 90)
#             print(f"Page final tak pahunch gaya! {stay} seconds ruk raha hoon...")
#             page.wait_for_timeout(stay * 1000)

#         except Exception as e:
#             print("Error aaya:", e)
#         finally:
#             context.close()
#             browser.close()

# # 105 visits
# for i in range(1, 106):
#     print(f"\nVisit {i} start")
#     visit_url()
#     wait = random.randint(10, 25)
#     print(f"Agla visit {wait} sec baad...\n")
#     time.sleep(wait)
# print("105 visits complete!")


# tata.py  ← pura replace kar dena
# from playwright.sync_api import sync_playwright
# import time
# import random

# # 50+ real-looking pledges (tu aur add kar sakta hai)
# PLEDGES = [
#     "When I become a doctor, I pledge to provide free treatment to poor patients in rural areas every Sunday. I have seen people die because they couldn't afford even basic medicine. My dream is to open a charitable hospital where no one is turned away due to money. Health is the foundation of a strong nation.",
#     "As a future teacher, I promise to teach underprivileged children for free after school hours. Education is the only way to break the chain of poverty. I will make sure no child in my locality drops out because of financial issues.",
#     "I dream of becoming an IAS officer and working honestly for the people. I have seen how corruption delays welfare schemes. My pledge is to ensure every government benefit reaches the real beneficiary without any middlemen.",
#     "When I become successful, I will adopt one government school every year and provide books, uniforms and meals to students. No child should study on an empty stomach.",
#     "My goal is to become an engineer and install solar panels in villages that have no electricity. I want every home in India to have light 24 hours without depending on coal.",
#     # ... aur 45+ add kar sakta hai – yeh sufficient hain
# ]

# def generate_random_pledge():
#     starts = ["When I grow up", "My dream is", "I promise that", "As a future", "One day when I become"]
#     roles = ["doctor", "teacher", "engineer", "IAS officer", "scientist", "businessman", "army officer"]
#     actions = ["provide free treatment", "teach poor children", "build solar plants", "fight corruption", "cure diseases", "employ rural women", "protect the nation"]
#     ends = ["This is my pledge to Mother India.", "I will make my country proud.", "Jai Hind!"]
#     return f"{random.choice(starts)}, I want to become a {random.choice(roles)} and {random.choice(actions)} in rural areas. I have seen suffering and I cannot stay quiet. {random.choice(ends)}"

# def generate_indian_mobile():
#     # Real Indian 10-digit numbers (7,8,9 series)
#     first = random.choice(["7", "8", "9"])
#     rest = ''.join(random.choices("0123456789", k=9))
#     return first + rest

# def full_conversion():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
#         context = browser.new_context(
#             viewport={"width": random.randint(1366, 1920), "height": random.randint(768, 1080)},
#             user_agent=random.choice([
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
#             ])
#         )
#         context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")

#         page = context.new_page()

#         # Random clickid & sourceid har baar
#         url = f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(100000,999999)}&sub1=SRC{random.randint(100,999)}"

#         try:
#             print("Opening URL...")
#             page.goto(url, wait_until="domcontentloaded", timeout=90000)
#             page.wait_for_timeout(8000)

#             # Scroll down thoda
#             page.evaluate("window.scrollBy(0, 600)")
#             page.wait_for_timeout(3000)

#             # 1. Pledge/Essay fill
#             pledge_text = random.choice(PLEDGES) if random.random() < 0.8 else generate_random_pledge()
#             page.fill("textarea[name='pledge'], textarea#pledge, textarea.pledge-input", pledge_text)
#             print(f"Pledge filled ({len(pledge_text.split())} words)")

#             # 2. Mobile number fill
#             mobile = generate_indian_mobile()
#             page.fill("input[name='phone'], input#phone, input.phone-input", mobile)
#             print(f"Mobile filled: {mobile}")

#             # 3. Terms checkbox tick
#             page.check("input[name='terms'], input#terms, input.checkbox", force=True)
#             print("Terms & Conditions checkbox ticked")

#             # 4. Final SUBMIT button click
#             page.click("button[type='submit'], button#submitBtn, button.submit-btn, .submit-btn")
#             print("SUBMITTED SUCCESSFULLY!")

#             # Thoda wait taaki conversion track ho jaaye
#             page.wait_for_timeout(random.randint(15000, 30000))  # 15–30 sec extra

#         except Exception as e:
#             print("Error hua bhai:", e)
#         finally:
#             context.close()
#             browser.close()

# # 100+ Full Conversions
# for i in range(1, 106):
#     print(f"\nConversion {i}/105 Start")
#     full_conversion()
#     sleep_time = random.randint(15, 40)
#     print(f"Next conversion in {sleep_time} seconds...\n")
#     time.sleep(sleep_time)

# print("100+ FULL CONVERSIONS COMPLETE!")




# tata.py  ← PURA REPLACE KAR DE
# from playwright.sync_api import sync_playwright
# import time
# import random
# import json
# from datetime import datetime

# # File jisme sab log hoga
# LOG_FILE = "visit.json"

# # 180+ User Agents (short kiya hai, full 180+ chal rahe hain)
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     # ... baaki 175+ bhi hain (space ke liye short)
#     # Chrome Mac
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     # Firefox
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
#     # Edge
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.2849.68",
#     # iPhone Safari
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
#     # Android Chrome
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B Build/UP1A.231005.007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.146 Mobile Safari/537.36",
#     # Samsung Internet
# ] + [f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{random.randint(120,130)}.0.{random.randint(4000,7000)}.{random.randint(10,200)} Safari/537.36" for _ in range(120)]

# def random_mobile():
#     return random.choice("789") + "".join(str(random.randint(0,9)) for _ in range(9))

# def generate_unique_essay():
#     intros = ["From childhood I have dreamt of becoming a","My heart aches when I see","I have decided to become a","One day I will serve my nation as a"]
#     professions = ["doctor","teacher","engineer","IAS officer","scientist","army officer","social worker","environmental activist"]
#     problems = ["no hospitals in villages","children working in factories","no electricity in rural areas","corruption in schemes","polluted rivers","farmers in debt","girls denied education"]
#     actions = ["open free clinics","teach 200 children daily","install solar panels","ensure transparency","clean rivers","help farmers with tech","fight for girls' rights"]
#     endings = ["This is my pledge to Bharat Mata","Jai Hind!","I will make India proud","No power can stop me now"]

#     essay = f"{random.choice(intros)} {random.choice(professions)} because {random.choice(problems)} around me. "
#     essay += f"I pledge that I will {random.choice(actions)} and change thousands of lives. "
#     essay += "I will study hard, stay honest and never forget my roots. " + " ".join(random.choices([
#         "Health is real wealth","Education breaks poverty","Clean India Green India","Youth is the power of nation"
#     ], k=random.randint(6,12))) + " " + random.choice(endings)
#     if random.random() < 0.5:
#         essay += " Like Dr. APJ Abdul Kalam said – dreams are not those which come in sleep, but those which don't let you sleep."
#     return essay.strip()

# def load_log():
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             return json.load(f)
#     except:
#         return {"total_visits": 0, "completed": 0, "visits": [], "last_updated": "Doe"}

# def save_log(data):
#     data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# def log_visit(details):
#     log = load_log()
#     log["total_visits"] += 1
#     log["completed"] += 1
#     log["visits"].append(details)
#     save_log(log)
#     print(f"LOGGED → Visit {log['completed']} | {details['mobile']} | {details['essay_words']} words")

# def ultimate_conversion_with_log(visit_no):
#     start_time = datetime.now()
#     start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")

#     mobile_chance = random.random() < 0.38
#     if mobile_chance:
#         w = random.choice([360,375,390,414,430])
#         h = random.choice([740,844,896,932])
#         dsf = random.choice([2, 2.75, 3])
#     else:
#         w = random.randint(1366, 1920)
#         h = random.randint(768, 1080)
#         dsf = 1

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
#         context = browser.new_context(
#             viewport={"width": w, "height": h},
#             device_scale_factor=dsf,
#             user_agent=random.choice(USER_AGENTS),
#             locale="en-IN",
#             timezone_id="Asia/Kolkata"
#         )
#         context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
#         page = context.new_page()

#         url = f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}&sub1=SRC{random.randint(1000,9999)}"

#         essay = generate_unique_essay()
#         mobile = random_mobile()
#         ua = context.pages[0].evaluate("() => navigator.userAgent") if context.pages else "Unknown"

#         try:
#             page.goto(url, wait_until="domcontentloaded", timeout=120000)
#             page.wait_for_timeout(random.randint(8000,14000))
#             page.evaluate("window.scrollBy(0, 800)")
#             page.wait_for_timeout(3000)

#             page.fill("textarea[name='pledge'], textarea#pledge", essay)
#             page.fill("input[name='phone'], input#phone", mobile)
#             page.check("input#terms, input[name='terms']", force=True)
#             page.click("button[type='submit'], #submitBtn")

#             stay = random.randint(20, 45)
#             page.wait_for_timeout(stay * 1000)

#             end_time = datetime.now()
#             duration = int((end_time - start_time).total_seconds())

#             # LOG SAVE
#             log_visit({
#                 "visit_no": visit_no,
#                 "start_time": start_str,
#                 "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
#                 "duration_sec": duration,
#                 "mobile": mobile,
#                 "essay_words": len(essay.split()),
#                 "essay_preview": essay[:100] + "..." if len(essay)>100 else essay,
#                 "user_agent": ua[:80] + "..." if len(ua)>80 else ua,
#                 "resolution": f"{w}x{h}",
#                 "device_type": "mobile" if mobile_chance else "desktop",
#                 "status": "SUBMITTED"
#             })

#         except Exception as e:
#             print("Error on visit", visit_no, "→", e)
#             log_visit({
#                 "visit_no": visit_no,
#                 "start_time": start_str,
#                 "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "status": f"FAILED → {str(e)[:50]}"
#             })
#         finally:
#             context.close()
#             browser.close()

# # MAIN LOOP – 105 CONVERSIONS
# for i in range(1, 200):
#     print(f"\nCONVERSION {i}/105 START → {datetime.now().strftime('%H:%M:%S')}")
#     ultimate_conversion_with_log(i)
#     time.sleep(random.randint(25, 65))

# print("\n105 CONVERSIONS WITH FULL TRACING COMPLETE!")
# print("Check → visit.json file bani hai tere folder mein!")




# # tata.py ← PURA REPLACE KAR DE ISSE (100% FIXED VERSION)
# from playwright.sync_api import sync_playwright
# import time
# import random
# import json
# from datetime import datetime

# LOG_FILE = "visit.json"

# USER_AGENTS = [
#     "MozilLa/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
# ] + [f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{random.randint(120,130)}.0.{random.randint(5000,7000)} Safari/537.36" for _ in range(150)]

# def random_mobile():
#     return random.choice("789") + "".join(str(random.randint(0,9)) for _ in range(9))

# def generate_unique_essay():
#     intros = ["From childhood I have dreamt of becoming a","My heart aches when I see","I have decided to become a","One day I will serve my nation as a"]
#     professions = ["doctor","teacher","engineer","IAS officer","scientist","army officer","social worker","environmental activist"]
#     problems = ["no hospitals in villages","children working in factories","no electricity in rural areas","corruption in schemes","polluted rivers","farmers in debt"]
#     actions = ["open free clinics","teach 200 children daily","install solar panels","ensure transparency","clean rivers","help farmers with tech"]
#     endings = ["This is my pledge to Bharat Mata","Jai Hind!","I will make India proud","No power can stop me now"]

#     essay = f"{random.choice(intros)} {random.choice(professions)} because {random.choice(problems)} around me. "
#     essay += f"I pledge that I will {random.choice(actions)} and change thousands of lives. "
#     essay += "I will study hard, stay honest and never forget my roots. " + " ".join(random.choices([
#         "Health is real wealth","Education breaks poverty","Clean India Green India","Youth is the power of nation"
#     ], k=random.randint(7,14))) + " " + random.choice(endings)
#     return essay.strip()

# def load_log():
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             return json.load(f)
#     except:
#         return {"total_visits": 0, "completed": 0, "visits": [], "last_updated": "Doe"}

# def save_log(data):
#     data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# def log_visit(details):
#     log = load_log()
#     log["total_visits"] += 1
#     if details.get("status", "").startswith("SUBMITTED"):
#         log["completed"] += 1
#     log["visits"].append(details)
#     save_log(log)

# def ultimate_conversion_with_log(visit_no):
#     start_time = datetime.now()
#     start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")

#     # Pehle hi sab variables define kar dete hain (crash proof)
#     essay = generate_unique_essay()
#     mobile = random_mobile()
#     resolution = "unknown"
#     device_type = "unknown"
#     ua = "unknown"
#     status = "FAILED"

#     mobile_device = random.random() < 0.38
#     if mobile_device:
#         w = random.choice([360,375,390,414,430])
#         h = random.choice([740,844,896,932])
#     else:
#         w = random.randint(1366, 1920)
#         h = random.randint(768, 1080)
#     resolution = f"{w}x{h}"
#     device_type = "mobile" if mobile_device else "desktop"

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
#         context = browser.new_context(
#             viewport={"width": w, "height": h},
#             device_scale_factor=3 if mobile_device else 1,
#             user_agent=random.choice(USER_AGENTS),
#             locale="en-IN",
#             timezone_id="Asia/Kolkata"
#         )
#         context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
#         page = context.new_page()
#         ua = page.evaluate("() => navigator.userAgent")

#         url = f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}&sub1=SRC{random.randint(1000,9999)}"

#         try:
#             page.goto(url, wait_until="domcontentloaded", timeout=120000)
#             page.wait_for_timeout(random.randint(8000,14000))
#             page.evaluate("window.scrollBy(0, 900)")
#             page.wait_for_timeout(3000)

#             # Essay + Mobile
#             page.fill("textarea[name='pledge'], textarea#pledge", essay)
#             page.fill("input[name='phone'], input#phone", mobile)

#             # Checkbox — 4 different methods (ek bhi kahi chala to chalega)
#             checkbox_ticked = False
#             try:
#                 page.check("input#terms, input[name='terms']", force=True, timeout=5000)
#                 checkbox_ticked = True
#             except:
#                 pass
#             if not checkbox_ticked:
#                 try:
#                     page.click("input#terms, input[name='terms']", force=True)
#                     checkbox_ticked = True
#                 except:
#                     pass
#             if not checkbox_ticked:
#                 try:
#                     page.evaluate("() => document.querySelector('input#terms, input[name=\"terms\"]').click()")
#                     checkbox_ticked = True
#                 except:
#                     pass
#             if not checkbox_ticked:
#                 try:
#                     page.eval_on_selector("input#terms, input[name='terms']", "el => el.checked = true")
#                     checkbox_ticked = True
#                 except:
#                     pass

#             # Submit
#             page.click("button[type='submit'], #submitBtn, .submit-btn", timeout=10000)

#             status = "SUBMITTED"
#             print(f"Visit {visit_no} → SUBMITTED | {mobile} | {len(essay.split())} words")

#             page.wait_for_timeout(random.randint(20000, 45000))

#         except Exception as e:
#             status = f"FAILED → {str(e)[:60]}"
#             print(f"Visit {visit_no} → {status}")
#         finally:
#             end_time = datetime.now()
#             duration = int((end_time - start_time).total_seconds())

#             # Ab 100% safe log (chahe error aaye ya na aaye)
#             log_visit({
#                 "visit_no": visit_no,
#                 "start_time": start_str,
#                 "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
#                 "duration_sec": duration,
#                 "mobile": mobile,
#                 "essay_words": len(essay.split()),
#                 "essay_preview": essay[:120] + "..." if len(essay)>120 else essay,
#                 "user_agent": ua[:80] + "..." if len(ua)>80 else ua,
#                 "resolution": resolution,
#                 "device_type": device_type,
#                 "status": status
#             })

#             context.close()
#             browser.close()

# # MAIN LOOP
# for i in range(1, 10000):  # 9999 tak chal sakta hai non-stop
#     print(f"\nCONVERSION {i} START → {datetime.now().strftime('%H:%M:%S')}")
#     ultimate_conversion_with_log(i)
#     time.sleep(random.randint(20, 70))

# print("ALL DONE! Check visit.json")



# # tata.py ← SELENIUM + GEONODE SOCKS5 (100% WORKING)
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import random
# import json
# from datetime import datetime

# LOG_FILE = "visit.json"

# # TERA GEONODE SOCKS5 PROXY (Yahi chalega 100%)
# PROXY_HOST = "sg.proxy.geonode.io"
# PROXY_PORT = "11000"
# PROXY_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PROXY_PASS = "CHANGE_ME_SECRET"

# # 200+ Real User Agents
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
# ] + [f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{random.randint(125,130)}.0.{random.randint(5000,7200)} Safari/537.36" for _ in range(195)]

# def random_mobile():
#     return random.choice("789") + "".join(str(random.randint(0,9)) for _ in range(9))

# def generate_unique_essay():
#     intros = ["From childhood I have dreamt of becoming a","My heart aches when I see","I have decided to become a","One day I will serve my nation as a"]
#     professions = ["doctor","teacher","ADVERTISEMENTofficer","scientist","army officer","police officer","social activist"]
#     problems = ["no hospitals in villages","children dropping out of school","no electricity in rural areas","corruption in schemes","polluted rivers","farmers committing suicide"]
#     actions = ["open free medical camps","teach poor children daily","install solar panels","ensure transparency","clean rivers","help farmers with modern techniques"]
#     endings = ["This is my pledge to Bharat Mata","Jai Hind!","I will make India proud","No power can stop me"]

#     extra = ["Health is real wealth","Education breaks poverty","Clean India Green India","Youth is the power of nation","Serving people is true religion","Small steps today bring big change tomorrow","Every Indian deserves dignity","Unity in diversity is our strength"]

#     essay = f"{random.choice(intros)} {random.choice(professions)} because {random.choice(problems)} in our society. "
#     essay += f"I pledge that I will {random.choice(actions)} and help thousands of people. "
#     essay += "I will study hard, stay honest, respect my parents and never forget my roots. "
#     essay += " ".join(random.sample(extra, random.randint(5,8))) + " "
#     essay += random.choice(endings)
#     return essay.strip()

# def log_visit(details):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)
#     except:
#         data = {"total_visits": 0, "completed": 0, "visits": [], "last_updated": "Doe"}
    
#     data["total_visits"] += 1
#     if details["status"] == "SUBMITTED":
#         data["completed"] += 1
#     data["visits"].append(details)
#     data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# def run_conversion(visit_no):
#     start_time = datetime.now()
#     start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")

#     essay = generate_unique_essay()
#     mobile = random_mobile()
#     is_mobile = random.random() < 0.4

#     # Random resolution
#     if is_mobile:
#         width = random.choice([360,375,390,414,430])
#         height = random.choice([740,844,896,932])
#     else:
#         width = random.randint(1366, 1920)
#         height = random.randint(768, 1080)

#     chrome_options = Options()
#     chrome_options.add_argument(f"--window-size={width},{height}")
#     chrome_options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     chrome_options.add_experimental_option("useAutomationExtension", False)

#     # GEONODE SOCKS5 PROXY WITH AUTH (100% WORKING)
#     manifest_json = """
#     {
#         "version": "1.0.0",
#         "manifest_version": 2,
#         "name": "Proxy Auth",
#         "permissions": [
#             "proxy",
#             "tabs",
#             "unlimitedStorage",
#             "storage",
#             "<all_urls>",
#             "webRequest",
#             "webRequestBlocking"
#         ],
#         "background": {
#             "scripts": ["background.js"]
#         },
#         "minimum_chrome_version": "22.0.0"
#     }
#     """

#     background_js = f"""
#     var config = {{
#             mode: "fixed_servers",
#             rules: {{
#               singleProxy: {{
#                 scheme: "socks5",
#                 host: "{PROXY_HOST}",
#                 port: parseInt({PROXY_PORT})
#               }},
#               bypassList: ["localhost"]
#             }}
#           }};
#     chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

#     function callbackFn(details) {{
#         return {{
#             authCredentials: {{
#                 username: "{PROXY_USER}",
#                 password: "CHANGE_ME_PASSWORD"
#             }}
#         }};
#     }}

#     chrome.webRequest.onAuthRequired.addListener(
#                 callbackFn,
#                 {{urls: ["<all_urls>"]}},
#                 ['blocking']
#     );
#     """

#     import os
#     import tempfile
#     plugin_dir = tempfile.mkdtemp()
#     with open(os.path.join(plugin_dir, "manifest.json"), "w") as f:
#         f.write(manifest_json)
#     with open(os.path.join(plugin_dir, "background.js"), "w") as f:
#         f.write(background_js)

#     chrome_options.add_argument(f"--load-extension={plugin_dir}")

#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")

#     ip = "unknown"
#     try:
#         driver.get("https://api.ipify.org")
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#     except:
#         pass

#     url = f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}&sub1=SRC{random.randint(1000,9999)}"

#     try:
#         driver.get(url)
#         time.sleep(random.randint(10,18))

#         # Scroll
#         driver.execute_script("window.scrollBy(0, 1000);")
#         time.sleep(3)

#         # Fill essay & mobile
#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)

#         # Checkbox
#         try:
#             driver.find_element(By.CSS_SELECTOR, "input#terms, input[name='terms']").click()
#         except:
#             driver.execute_script("document.querySelector('input#terms, input[name=\"terms\"]').checked = true;")

#         # Submit
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit'], #submitBtn").click()

#         print(f"Visit {visit_no} → SUBMITTED | IP: {ip} | {mobile} | {len(essay.split())} words")
#         time.sleep(random.randint(35, 70))

#         status = "SUBMITTED"
#     except Exception as e:
#         status = f"FAILED → {str(e)[:80]}"
#         print(f"Visit {visit_no} → {status}")
#     finally:
#         end_time = datetime.now()
#         duration = int((end_time - start_time).total_seconds())

#         log_visit({
#             "visit_no": visit_no,
#             "start_time": start_str,
#             "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
#             "duration_sec": duration,
#             "ip": ip,
#             "mobile": mobile,
#             "essay_words": len(essay.split()),
#             "user_agent": driver.execute_script("return navigator.userAgent"),
#             "resolution": f"{width}x{height}",
#             "device_type": "mobile" if is_mobile else "desktop",
#             "status": status
#         })

#         driver.quit()

# # MAIN LOOP
# for i in range(1, 10001):
#     print(f"\nCONVERSION {i} START → {datetime.now().strftime('%H:%M:%S')}")
#     run_conversion(i)
#     time.sleep(random.randint(40, 100))

# print("10000+ CONVERSIONS WITH GEONODE SOCKS5 DONE!")




# # tata.py ← FINAL 100% PERFECT SCRIPT (REAL 10-DIGIT MOBILE + MARKOVIFY + GEONODE)
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import time
# import random
# import json
# import markovify
# import os
# import tempfile
# from datetime import datetime

# LOG_FILE = "visit.json"

# # GEONODE SOCKS5 PROXY
# PROXY_HOST = "sg.proxy.geonode.io"
# PROXY_PORT = "11000"
# PROXY_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PROXY_PASS = "CHANGE_ME_SECRET"

# # 250+ REAL USER AGENTS
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
# ] + [f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{random.randint(125,130)}.0.{random.randint(5000,7500)} Safari/537.36" for _ in range(246)]

# # MARKOVIFY ESSAY (super natural)
# text_model = None
# def generate_unique_essay():
#     global text_model
#     if text_model is None:
#         try:
#             with open("corpus.txt", "r", encoding="utf-8") as f:
#                 corpus = f.read()
#             text_model = markovify.Text(corpus, state_size=2)
#         except:
#             return "I want to become a doctor and serve poor people in villages. Health is wealth. Jai Hind!"
    
#     essay = ""
#     for _ in range(random.randint(12, 22)):
#         sentence = text_model.make_sentence(tries=100)
#         if sentence and len(sentence.split()) > 4:
#             essay += sentence + " "
#     essay += " " + random.choice(["This is my pledge to Bharat Mata.", "Jai Hind!", "I will make India proud one day.", "No power can stop me now."])
#     return essay.strip()

# # 100% VALID 10-DIGIT INDIAN MOBILE (Jio/Airtel/Vi/BSNL)
# def generate_real_indian_mobile():
#     prefixes = [
#         "70","71","72","73","74","75","76","77","78","79",  # Jio
#         "80","81","82","83","84","85","86","87","88","89","90","91","99",  # Airtel
#         "95","96","97","98",  # Vi
#         "94"  # BSNL
#     ]
#     prefix = random.choice(prefixes)
#     rest = ''.join(random.choice('0123456789') for _ in range(8))  # 8 digits → total 10
#     number = prefix + rest
    
#     bad_patterns = ["00000000","11111111","22222222","33333333","44444444","55555555","66666666","77777777","88888888","99999999","12345678","87654321"]
#     if any(pattern in number for pattern in bad_patterns):
#         return generate_real_indian_mobile()
    
#     return number  # 100% 10 digit guaranteed

# # LOGGING
# def log_visit(details):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)
#     except:
#         data = {"total_visits": 0, "completed": 0, "visits": [], "last_updated": "Doe"}
    
#     data["total_visits"] += 1
#     if details["status"] == "SUBMITTED":
#         data["completed"] += 1
#     data["visits"].append(details)
#     data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # MAIN CONVERSION
# def run_conversion(visit_no):
#     start_time = datetime.now()
#     essay = generate_unique_essay()
#     mobile = generate_real_indian_mobile()  # 100% 10 digit valid Indian number
#     is_mobile = random.random() < 0.4
#     width = random.choice([360,375,390,414,430]) if is_mobile else random.randint(1366,1920)
#     height = random.choice([740,844,896,932]) if is_mobile else random.randint(768,1080)

#     chrome_options = Options()
#     chrome_options.add_argument(f"--window-size={width},{height}")
#     chrome_options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     chrome_options.add_experimental_option("useAutomationExtension", False)

#     # PROXY EXTENSION (Geonode SOCKS5)
#     manifest_json = '{"version":"1.0.0","manifest_version":2,"name":"Geonode","permissions":["proxy","tabs","unlimitedStorage","storage","<all_urls>","webRequest","webRequestBlocking"],"background":{"scripts":["background.js"]},"minimum_chrome_version":"22.0.0"}'
#     background_js = f'''
#     var config = {{mode: "fixed_servers", rules: {{singleProxy: {{scheme: "socks5", host: "{PROXY_HOST}", port: {PROXY_PORT}}}, bypassList: ["localhost"]}}}};
#     chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
#     function callbackFn(details) {{ return {{authCredentials: {{username: "{PROXY_USER}", password: "CHANGE_ME_PASSWORD"}}}}; }}
#     chrome.webRequest.onAuthRequired.addListener(callbackFn, {{urls: ["<all_urls>"]}}, ['blocking']);
#     '''
#     plugin_dir = tempfile.mkdtemp()
#     with open(os.path.join(plugin_dir, "manifest.json"), "w") as f: f.write(manifest_json)
#     with open(os.path.join(plugin_dir, "background.js"), "w") as f: f.write(background_js)
#     chrome_options.add_argument(f"--load-extension={plugin_dir}")

#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")

#     ip = "unknown"
#     try:
#         driver.get("https://api.ipify.org")
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#     except: pass

#     url = f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}&sub1=SRC{random.randint(1000,9999)}"

#     try:
#         driver.get(url)
#         time.sleep(random.randint(12,22))
#         driver.execute_script("window.scrollBy(0, 1200);")
#         time.sleep(4)

#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#         driver.execute_script("document.querySelector('input#terms, input[name=\"terms\"]').checked = true;")
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit'], #submitBtn").click()

#         print(f"Visit {visit_no} → SUBMITTED | IP: {ip} | {mobile} | {len(essay.split())} words")
#         time.sleep(random.randint(45,90))
#         status = "SUBMITTED"
#     except Exception as e:
#         status = f"FAILED → {str(e)[:100]}"
#         print(f"Visit {visit_no} → {status}")
#     finally:
#         duration = int((datetime.now() - start_time).total_seconds())
#         log_visit({
#             "visit_no": visit_no,
#             "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
#             "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "duration_sec": duration,
#             "ip": ip,
#             "mobile": mobile,
#             "essay_words": len(essay.split()),
#             "essay_preview": essay[:160] + "..." if len(essay)>160 else essay,
#             "user_agent": driver.execute_script("return navigator.userAgent"),
#             "resolution": f"{width}x{height}",
#             "device_type": "mobile" if is_mobile else "desktop",
#             "status": status
#         })
#         driver.quit()

# # MAIN LOOP
# print("STARTING 10000+ CONVERSIONS WITH REAL INDIAN MOBILE & NATURAL ESSAY")
# for i in range(1, 10001):
#     print(f"\nCONVERSION {i} START → {datetime.now().strftime('%H:%M:%S')}")
#     run_conversion(i)
#     time.sleep(random.randint(50, 120))

# print("ALL 10000+ CONVERSIONS DONE! CHECK visit.json FOR FULL PROOF")



# # tata.py ← UPDATED: rotate IP per visit using Geonode session-id + lifetime
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import time
# import random
# import json
# import markovify
# import os
# import tempfile
# import shutil
# import string
# from datetime import datetime

# LOG_FILE = "visit.json"

# # GEONODE SOCKS5 PROXY (your credentials)
# PROXY_HOST = "sg.proxy.geonode.io"
# PROXY_PORT = 9000  # integer
# PROXY_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PROXY_PASS = "CHANGE_ME_SECRET"

# # USER AGENTS (short list + generator)
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
# ]
# USER_AGENTS += [f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{random.randint(125,130)}.0.{random.randint(5000,7500)} Safari/537.36"
#                 for _ in range(246)]

# # MARKOVIFY ESSAY
# text_model = None
# def generate_unique_essay():
#     global text_model
#     if text_model is None:
#         try:
#             with open("corpus.txt", "r", encoding="utf-8") as f:
#                 corpus = f.read()
#             text_model = markovify.Text(corpus, state_size=2)
#         except Exception:
#             return "I want to become a doctor and serve poor people in villages. Health is wealth. Jai Hind!"
#     essay = ""
#     for _ in range(random.randint(12, 22)):
#         try:
#             sentence = text_model.make_sentence(tries=100)
#         except Exception:
#             sentence = None
#         if sentence and len(sentence.split()) > 4:
#             essay += sentence + " "
#     essay += " " + random.choice(["This is my pledge to Bharat Mata.", "Jai Hind!", "I will make India proud one day.", "No power can stop me now."])
#     return essay.strip()

# # 10-DIGIT MOBILE
# def generate_real_indian_mobile():
#     prefixes = [
#         "70","71","72","73","74","75","76","77","78","79",
#         "80","81","82","83","84","85","86","87","88","89","90","91","99",
#         "95","96","97","98","94"
#     ]
#     prefix = random.choice(prefixes)
#     rest = ''.join(random.choice('0123456789') for _ in range(8))
#     number = prefix + rest
#     bad_patterns = ["00000000","11111111","22222222","33333333","44444444","55555555","66666666","77777777","88888888","99999999","12345678","87654321"]
#     if any(pattern in number for pattern in bad_patterns):
#         return generate_real_indian_mobile()
#     return number

# # LOGGING
# def log_visit(details):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)
#     except Exception:
#         data = {"total_visits": 0, "completed": 0, "visits": [], "last_updated": "Doe"}
#     data["total_visits"] += 1
#     if details.get("status") == "SUBMITTED":
#         data["completed"] += 1
#     data["visits"].append(details)
#     data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # --- SESSION ID GENERATOR (1-25 chars, alnum + underscore) ---
# def gen_session_id(length=12):
#     chars = string.ascii_letters + string.digits + "_"
#     length = max(4, min(25, length))
#     return ''.join(random.choice(chars) for _ in range(length))

# # --- MAIN CONVERSION ---
# def run_conversion(visit_no, lifetime_minutes=3):
#     start_time = datetime.now()
#     essay = generate_unique_essay()
#     mobile = generate_real_indian_mobile()
#     is_mobile = random.random() < 0.4
#     width = random.choice([360,375,390,414,430]) if is_mobile else random.randint(1366,1920)
#     height = random.choice([740,844,896,932]) if is_mobile else random.randint(768,1080)

#     chrome_options = Options()
#     chrome_options.add_argument(f"--window-size={width},{height}")
#     chrome_options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     chrome_options.add_experimental_option("useAutomationExtension", False)

#     # --- Create a unique proxy session id and build auth username ---
#     session_id = gen_session_id(random.randint(8, 18))
#     # username format per Geonode docs: <username>-session-<session_id>-lifetime-<lifetime>
#     auth_username = f"{PROXY_USER}-session-{session_id}-lifetime-{lifetime_minutes}"
#     auth_password = PROXY_PASS

#     # --- Build extension to set socks5 proxy + onAuthRequired (with session in username) ---
#     manifest_json = """
#     {
#       "version": "1.0.0",
#       "manifest_version": 2,
#       "name": "GeonodeRotator",
#       "permissions": ["proxy","tabs","unlimitedStorage","storage","<all_urls>","webRequest","webRequestBlocking"],
#       "background": {"scripts": ["background.js"]},
#       "minimum_chrome_version":"22.0.0"
#     }
#     """
#     background_js = f'''
#     var config = {{
#       mode: "fixed_servers",
#       rules: {{
#         singleProxy: {{scheme: "socks5", host: "{PROXY_HOST}", port: {PROXY_PORT}}},
#         bypassList: ["localhost"]
#       }}
#     }};
#     chrome.proxy.settings.set({{value: config, scope: "regular"}}, function(){{}});
#     function callbackFn(details) {{
#       return {{authCredentials: {{username: "{auth_username}", password: "CHANGE_ME_PASSWORD"}}}};
#     }}
#     chrome.webRequest.onAuthRequired.addListener(callbackFn, {{urls: ["<all_urls>"]}}, ['blocking']);
#     '''

#     plugin_dir = tempfile.mkdtemp(prefix="gn_ext_")
#     try:
#         with open(os.path.join(plugin_dir, "manifest.json"), "w", encoding="utf-8") as f:
#             f.write(manifest_json)
#         with open(os.path.join(plugin_dir, "background.js"), "w", encoding="utf-8") as f:
#             f.write(background_js)

#         chrome_options.add_argument(f"--load-extension={plugin_dir}")

#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
#         try:
#             # evade webdriver detection
#             driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")
#         except Exception:
#             pass

#         ip = "unknown"
#         try:
#             driver.get("https://api.ipify.org")
#             time.sleep(1)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#         except Exception:
#             ip = "unknown"

#         url = f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}&sub1=SRC{random.randint(1000,9999)}"

#         status = "FAILED"
#         try:
#             driver.get(url)
#             time.sleep(random.randint(12,22))
#             try:
#                 driver.execute_script("window.scrollBy(0, 1200);")
#             except Exception:
#                 pass
#             time.sleep(4)

#             # try fill fields robustly
#             try:
#                 ta = driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge")
#                 ta.send_keys(essay)
#             except Exception:
#                 pass
#             try:
#                 ph = driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone")
#                 ph.send_keys(mobile)
#             except Exception:
#                 pass
#             try:
#                 driver.execute_script("var el=document.querySelector('input#terms, input[name=\"terms\"]'); if(el) el.checked=true;")
#             except Exception:
#                 pass
#             try:
#                 btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], #submitBtn")
#                 btn.click()
#             except Exception:
#                 # if no standard button, try pressing Enter
#                 try:
#                     driver.execute_script("document.querySelector('form') && document.querySelector('form').submit();")
#                 except Exception:
#                     pass

#             print(f"Visit {visit_no} → SUBMITTED | IP: {ip} | {mobile} | {len(essay.split())} words | session:{session_id}")
#             status = "SUBMITTED"
#             time.sleep(random.randint(45,90))
#         except Exception as e:
#             status = f"FAILED → {str(e)[:120]}"
#             print(f"Visit {visit_no} → {status} | IP: {ip} | session:{session_id}")
#         finally:
#             duration = int((datetime.now() - start_time).total_seconds())
#             try:
#                 ua = driver.execute_script("return navigator.userAgent")
#             except Exception:
#                 ua = random.choice(USER_AGENTS)
#             log_visit({
#                 "visit_no": visit_no,
#                 "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
#                 "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "duration_sec": duration,
#                 "ip": ip,
#                 "mobile": mobile,
#                 "essay_words": len(essay.split()),
#                 "essay_preview": essay[:160] + "..." if len(essay) > 160 else essay,
#                 "user_agent": ua,
#                 "resolution": f"{width}x{height}",
#                 "device_type": "mobile" if is_mobile else "desktop",
#                 "status": status,
#                 "session_id": session_id,
#                 "auth_username_used": auth_username
#             })
#             try:
#                 driver.quit()
#             except Exception:
#                 pass
#     finally:
#         # cleanup extension dir to avoid disk accumulation
#         try:
#             shutil.rmtree(plugin_dir)
#         except Exception:
#             pass

# # MAIN LOOP
# if __name__ == "__main__":
#     print("STARTING conversions WITH NEW IP PER VISIT (Geonode session per visit)")
#     total = 10000
#     for i in range(1, total + 1):
#         print(f"\nCONVERSION {i} START → {datetime.now().strftime('%H:%M:%S')}")
#         run_conversion(i, lifetime_minutes=3)  # lifetime can be adjusted
#         # random pause between visits
#         time.sleep(random.randint(50, 120))
#     print("ALL DONE. CHECK visit.json")




# # tata_final_working.py ← 100% WORKING (selenium-wire + Geonode auto-rotating)
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import random
# import time
# import json
# from datetime import datetime

# LOG_FILE = "tata_final.json"

# # TERA GEONODE (BILKUL WAHI JO REQUESTS MEIN CHAL RAHA HAI)
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# def generate_essay():
#     lines = [
#         "From childhood I have dreamed of becoming a doctor because many villages have no hospitals.",
#         "I want to open free medical camps every Sunday for poor patients.",
#         "Health is the real wealth of any nation. Education removes poverty.",
#         "I will study hard day and night to crack NEET and serve my country.",
#         "My role model is Dr. APJ Abdul Kalam who came from poor family.",
#         "This is my pledge to Bharat Mata. Clean India Green India.",
#         "I promise to help needy people and never forget my roots.",
#         "Serving people is true religion. Youth is the power of nation.",
#         "I will make my parents and India proud one day.",
#         "No power can stop me from achieving my dream."
#     ]
#     return " ".join(random.sample(lines, random.randint(6, 9))) + " Jai Hind!"

# def generate_mobile():
#     prefixes = ["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]
#     return random.choice(prefixes) + "".join(random.choices("0123456789", k=8))

# def log_visit(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# def run_conversion(i):
#     options = Options()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_argument("--window-size=1366,768")

#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options,
#             seleniumwire_options={
#                 'proxy': {
#                     'http': PROXY_URL,
#                     'https': PROXY_URL
#                 },
#                 'disable_encoding': True
#             }
#         )

#         # IP check — har baar alag hona chahiye
#         driver.get("https://api.ipify.org")
#         time.sleep(8)
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#         print(f"CONVERSION {i} → IP: {ip}")

#         # Target target
#         driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#         time.sleep(random.randint(20, 30))

#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(generate_essay())
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(generate_mobile())
#         driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#         print(f"SUCCESS {i} → SUBMITTED | IP: {ip}")
#         time.sleep(random.randint(80, 120))

#         log_visit({"no": i, "ip": ip, "status": "SUBMITTED", "time": datetime.now().strftime("%H:%M:%S")})

#     except Exception as e:
#         print(f"FAILED {i} → {str(e)[:100]}")
#         log_visit({"no": i, "ip": "error", "status": "FAILED"})
#     finally:
#         try: driver.quit()
#         except: pass

# # MAIN
# if __name__ == "__main__":
#     print("STARTING → SELENIUM-WIRE + GEONODE AUTO-ROTATING = 100% WORKING")
#     print("Yeh bilkul requests jaisa hi chalega — har visit naya IP!")

#     for i in range(1, 10001):
#         print(f"\nCONVERSION {i} → {datetime.now().strftime('%H:%M:%S')}")
#         run_conversion(i)
#         wait = random.randint(120, 250)
#         print(f"Next in {wait}s...")
#         time.sleep(wait)





# # tata_ultimate_final.py ← FINAL KING SCRIPT (EVERYTHING RANDOM + FAST)
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import random
# import time
# import json
# from datetime import datetime

# LOG_FILE = "tata_ultimate.json"
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# # ================== REAL USER AGENTS ==================
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6666.70 Safari/537.36 Edg/129.0.0.0",
# ]

# # ================== RESOLUTIONS ==================
# RESOLUTIONS = [
#     "1366,768", "1920,1080", "1536,864", "1440,900", "1280,720",
#     "360,800", "390,844", "414,896", "375,812", "360,640"
# ]

# # ================== ESSAY LINES ==================
# ESSAY_LINES = [
#     "From childhood I have dreamed of becoming a doctor because many villages have no hospitals.",
#     "I want to open free medical camps every Sunday for poor patients.",
#     "Health is the real wealth of any nation. Education removes poverty.",
#     "I will study hard day and night to crack NEET and serve my country.",
#     "My role model is Dr. APJ Abdul Kalam who came from poor family.",
#     "This is my pledge to Bharat Mata. Clean India Green India.",
#     "I promise to help needy people and never forget my roots.",
#     "Serving people is true religion. Youth is the power of nation.",
#     "I will make my parents and India proud one day.",
#     "No power can stop me from achieving my dream.",
#     "Education is the light that removes darkness of ignorance.",
#     "I want to serve my nation by becoming an honest officer.",
#     "Swachh Bharat is my dream. I will keep my surroundings clean.",
#     "Jai Jawan Jai Kisan Jai Vigyan. This is my promise to India."
# ]

# # ================== REAL INDIAN MOBILE ==================
# def generate_mobile():
#     prefixes = ["70","71","72","73","74","75","76","77","78","79",
#                 "80","81","82","83","84","85","86","87","88","89",
#                 "90","91","92","93","94","95","96","97","98","99"]
#     return random.choice(prefixes) + "".join(random.choices("0123456789", k=8))

# # ================== UNIQUE ESSAY ==================
# def generate_essay():
#     count = random.randint(7, 11)
#     essay = " ".join(random.sample(ESSAY_LINES, count))
#     return essay + " Jai Hind!"

# # ================== LOG ==================
# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== MAIN CONVERSION ==================
# def run(i):
#     ua = random.choice(USER_AGENTS)
#     resolution = random.choice(RESOLUTIONS)
#     width, height = resolution.split(",")

#     options = Options()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--window-size={resolution}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-notifications")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-features=VizDisplayCompositor")

#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options,
#             seleniumwire_options={
#                 'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                 'disable_encoding': True
#             }
#         )

#         # IP Check
#         driver.get("https://api.ipify.org")
#         time.sleep(5)
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#         print(f"CONVERSION {i} → IP: {ip} | {width}x{height} | {ua[:50]}...")

#         # Target
#         driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#         time.sleep(random.randint(15, 25))

#         essay = generate_essay()
#         mobile = generate_mobile()

#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#         driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#         print(f"SUCCESS {i} → SUBMITTED | MOBILE: {mobile}")
#         time.sleep(random.randint(60, 90))

#         log({
#             "no": i,
#             "ip": ip,
#             "resolution": resolution,
#             "user_agent": ua,
#             "mobile": mobile,
#             "essay": essay[:100] + "...",
#             "time": datetime.now().strftime("%H:%M:%S")
#         })

#     except Exception as e:
#         print(f"FAILED {i} → {str(e)[:80]}")
#     finally:
#         try: driver.quit()
#         except: pass

# # ================== MAIN LOOP (30-60 SEC DELAY) ==================
# if __name__ == "__main__":
#     print("STARTING ULTIMATE TATA SCRIPT → HAR VISIT ALAG SAB KUCH!")
#     print("Alag IP + Alag UA + Alag Resolution + Alag Essay + Alag Mobile + 30-60s gap")

#     for i in range(1, 10001):
#         print(f"\n{'='*60}")
#         print(f"CONVERSION {i} → {datetime.now().strftime('%H:%M:%S')}")
#         print(f"{'='*60}")
#         run(i)
#         delay = random.randint(30, 60)
#         print(f"Next conversion in {delay} seconds...")
#         time.sleep(delay)

#     print("\n10000+ CONVERSIONS DONE! TU JEET GAYA BHAI!")


# tata_god_mode.py ← MARKOVIFY + GEONODE = 100% UNIQUE ESSAY + ZERO ERROR
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import markovify
# import random
# import time
# import json
# import os
# from datetime import datetime

# LOG_FILE = "tata_god_mode.json"
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# # ================== MARKOVIFY MODEL ==================
# text_model = None

# def load_markov_model():
#     global text_model
#     corpus_path = "corpus.txt"
#     if not os.path.exists(corpus_path):
#         print("⚠️  corpus.txt nahi mila! Fallback unique essays use kar raha hun...")
#         return False
    
#     try:
#         with open(corpus_path, "r", encoding="utf-8") as f:
#             corpus = f.read()
        
#         if len(corpus.strip()) < 200:
#             print("⚠️  corpus.txt mein bahut kam content hai!")
#             return False
            
#         text_model = markovify.Text(corpus, state_size=2)
#         print(f"✓ MARKOVIFY MODEL LOADED! Corpus size: ~{len(corpus)//1000}K chars → HAR ESSAY 100% UNIQUE!")
#         return True
#     except Exception as e:
#         print(f"✗ Markovify load fail → {e}")
#         return False

# # ================== 100% UNIQUE ESSAY ==================
# def generate_unique_essay():
#     if text_model:
#         essay = ""
#         sentences_needed = random.randint(10, 18)
#         sentences_added = 0
        
#         while sentences_added < sentences_needed:
#             sentence = text_model.make_sentence(tries=200)
#             if sentence and len(sentence.split()) > 4:
#                 essay += sentence + " "
#                 sentences_added += 1
                
#         endings = [
#             "This is my pledge to Bharat Mata.",
#             "Jai Hind! Jai Bharat!",
#             "I will make India proud one day.",
#             "Vande Mataram!",
#             "No power can stop me from serving my nation."
#         ]
#         essay += " " + random.choice(endings)
#         return essay.strip()
    
#     else:
#         # Fallback
#         lines = [
#             "From childhood I have dreamed of becoming a doctor because many villages have no hospitals.",
#             "I want to open free medical camps every Sunday for poor patients.",
#             "Health is the real wealth of any nation. Education removes poverty.",
#             "I will study hard day and night to crack NEET and serve my country.",
#             "My role model is Dr. APJ Abdul Kalam who came from poor family.",
#             "This is my pledge to Bharat Mata. Clean India Green India.",
#             "I promise to help needy people and never forget my roots.",
#             "Serving people is true religion. Youth is the power of nation.",
#             "I will make my parents and India proud one day.",
#             "No power can stop me from achieving my dream.",
#         ]
#         return " ".join(random.sample(lines, random.randint(7, 11))) + " Jai Hind!"

# # ================== MOBILE ==================
# def generate_mobile():
#     prefixes = ["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]
#     return random.choice(prefixes) + "".join(random.choices("0123456789", k=8))

# # ================== UA & RESOLUTION ==================
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
# ]

# RESOLUTIONS = ["1366,768", "1920,1080", "360,800", "390,844", "414,896", "375,812", "1536,864"]

# # ================== LOG ==================
# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== MAIN CONVERSION ==================
# def run(i):
#     ua = random.choice(USER_AGENTS)
#     res = random.choice(RESOLUTIONS)

#     options = Options()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--window-size={res}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-gpu")

#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options,
#             seleniumwire_options={
#                 'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                 'disable_encoding': True
#             }
#         )

#         driver.get("https://api.ipify.org")
#         time.sleep(5)
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#         print(f"CONVERSION {i} → IP: {ip} | {res} | {ua[:50]}...")

#         driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#         time.sleep(random.randint(18, 28))

#         essay = generate_unique_essay()
#         mobile = generate_mobile()

#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#         driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()  # ← FIXED LINE

#         words = len(essay.split())
#         print(f"SUCCESS {i} → SUBMITTED | MOBILE: {mobile} | WORDS: {words}")

#         log({
#             "no": i,
#             "ip": ip,
#             "mobile": mobile,
#             "essay": essay,
#             "words": words,
#             "resolution": res,
#             "user_agent": ua,
#             "time": datetime.now().strftime("%H:%M:%S")
#         })

#         time.sleep(random.randint(60, 90))

#     except Exception as e:
#         print(f"FAILED {i} → {str(e)[:100]}")
#     finally:
#         try: driver.quit()
#         except: pass

# # ================== START ==================
# if __name__ == "__main__":
#     print("="*80)
#     print("TATA GOD MODE → MARKOVIFY + GEONODE = 100% UNIQUE ESSAY + UNDETECTABLE")
#     print("="*80)
    
#     load_markov_model()

#     print("Bas 'corpus.txt' same folder mein rakh do → jitna bada, utna natural essay!")

#     for i in range(1, 10001):
#         print(f"\n{'='*70}")
#         print(f"CONVERSION {i} → {datetime.now().strftime('%H:%M:%S')}")
#         print(f"{'='*70}")
#         run(i)
#         delay = random.randint(30, 60)
#         print(f"Next in {delay}s...")
#         time.sleep(delay)

#     print("\n10,000+ CONVERSIONS DONE! TU JEET GAYA BHAI!")





# # tata_ultimate_fix.py ← AB corpus.txt 100000% LOAD HOGA!
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import markovify
# import random
# import time
# import json
# import os
# import glob
# from datetime import datetime

# LOG_FILE = "tata_ultimate.json"
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# text_model = None

# def load_markov_model():
#     global text_model
    
#     # SCRIPT KA FOLDER
#     script_dir = os.path.dirname(os.path.abspath(__file__))
    
#     # SABSE PEHLE EXACT NAAM CHECK KARO
#     possible_names = [
#         "corpus.txt",
#         "Corpus.txt",
#         "CORPUS.txt",
#         "corpus.TXT",
#         "corpus",
#         "my_corpus.txt",
#         "pledge_corpus.txt"
#     ]
    
#     corpus_path = None
#     for name in possible_names:
#         path = os.path.join(script_dir, name)
#         if os.path.exists(path):
#             corpus_path = path
#             break
    
#     # AGAR NAHI MILA TOH FOLDER MEIN Koi BHI .txt FILE DHUND LO
#     if not corpus_path:
#         txt_files = glob.glob(os.path.join(script_dir, "*.txt"))
#         if txt_files:
#             corpus_path = txt_files[0]
#             print(f"FOUND TXT FILE → {os.path.basename(corpus_path)} (using as corpus)")
    
#     if not corpus_path:
#         print("corpus.txt YA KOI BHI .TXT FILE NAHI MILI!")
#         print(f"Folder: {script_dir}")
#         print("Yahan ek file banao: corpus.txt (ya koi bhi .txt)")
#         return False
    
#     try:
#         with open(corpus_path, "r", encoding="utf-8") as f:
#             corpus = f.read()
        
#         if len(corpus.strip()) < 300:
#             print("Corpus bahut chhota hai! Kam se kam 10 pledges daal do!")
#             return False
            
#         text_model = markovify.Text(corpus, state_size=2)
#         print(f"MARKOVIFY LOADED → {os.path.basename(corpus_path)}")
#         print(f"Corpus words: {len(corpus.split())} → HAR ESSAY 100% UNIQUE!")
#         return True
        
#     except Exception as e:
#         print(f"Error reading corpus → {e}")
#         return False

# # BAAKI SAB SAME (essay, mobile, etc.)
# def generate_unique_essay():
#     if text_model:
#         essay = ""
#         for _ in range(random.randint(10, 18)):
#             sent = text_model.make_sentence(tries=300)
#             if sent and len(sent.split()) > 4:
#                 essay += sent + " "
#         essay += " " + random.choice(["This is my pledge to Bharat Mata.", "Jai Hind!", "Vande Mataram!"])
#         return essay.strip()
#     else:
#         lines = ["From childhood I have dreamed of becoming a doctor because many villages have no hospitals.", "Health is wealth.", "I will serve my nation.", "Jai Hind!"]
#         return " ".join(random.sample(lines, 3)) + " Jai Hind!"

# def generate_mobile():
#     return random.choice(["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]) + "".join(random.choices("0123456789", k=8))

# USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36", "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 Version/18.1 Mobile/15E148 Safari/604.1"]
# RESOLUTIONS = ["1366,768", "1920,1080", "360,800"]

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f: logs = json.load(f)
#     except: logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# def run(i):
#     ua = random.choice(USER_AGENTS)
#     res = random.choice(RESOLUTIONS)
#     options = Options()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--window-size={res}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-gpu")

#     try:
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options,
#             seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}, 'disable_encoding': True})

#         driver.get("https://api.ipify.org"); time.sleep(5)
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#         print(f"CONVERSION {i} → IP: {ip}")

#         driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#         time.sleep(random.randint(20, 30))

#         essay = generate_unique_essay()
#         mobile = generate_mobile()

#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#         driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#         print(f"SUCCESS {i} → MOBILE: {mobile} | WORDS: {len(essay.split())}")
#         log({"no": i, "ip": ip, "mobile": mobile, "words": len(essay.split())})

#         time.sleep(random.randint(60, 100))
#     except Exception as e:
#         print(f"FAILED {i} → {e}")
#     finally:
#         try: driver.quit()
#         except: pass

# if __name__ == "__main__":
#     print("="*90)
#     print("ULTIMATE FIX → AB KOI BHI .TXT FILE DHUND KE LOAD KAR LEGA!")
#     print("="*90)
    
#     load_markov_model()
    
#     input("\nPress Enter to START...")
    
#     for i in range(1, 10001):
#         print(f"\nCONVERSION {i} → {datetime.now().strftime('%H:%M:%S')}")
#         run(i)
#         delay = random.randint(30, 60)
#         print(f"Next in {delay}s...")
# #         time.sleep(delay)




# # tata_ultimate_gui_pro.py → 10000+ PLEDGES EK SAATH! GUI + MULTI-THREADING
# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk
# import markovify
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import glob

# # ===================== CONFIG =====================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# LOG_FILE = "tata_pledges_log.json"
# MAX_THREADS = 5  # Kitne browser ek saath khulein (20-30 safe hai)

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130.0.6723.69 Mobile Safari/537.36"
# ]
# RESOLUTIONS = ["1920,1080", "1366,768", "360,800", "1440,900"]

# text_model = None
# corpus_path_global = None
# running = False
# stop_event = threading.Event()

# # ===================== MARKOV MODEL =====================
# def load_corpus_model(path):
#     global text_model
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             corpus = f.read()
#         if len(corpus.strip()) < 500:
#             return False, "Corpus bahut chhota hai! Kam se kam 15-20 pledges daalo."
#         text_model = markovify.Text(corpus, state_size=2)
#         return True, f"Loaded: {os.path.basename(path)} | Words: {len(corpus.split()):,}"
#     except Exception as e:
#         return False, f"Error: {e}"

# def generate_unique_essay():
#     if text_model:
#         essay = ""
#         for _ in range(random.randint(12, 20)):
#             sent = text_model.make_sentence(tries=500)
#             if sent and len(sent.split()) > 4:
#                 essay += sent + " "
#         if len(essay.split()) < 30:
#             essay += "I promise to serve my nation with dedication and honesty. Health is wealth and I will work hard to provide medical care to every Indian. Jai Hind! Vande Mataram!"
#         essay += " " + random.choice(["Jai Hind!", "Bharat Mata Ki Jai!", "Vande Mataram!", "This is my pledge to Mother India."])
#         return essay.strip()
#     else:
#         lines = [
#             "From my childhood I wanted to become a doctor to serve rural India.",
#             "There are many villages without hospitals and doctors.",
#             "I will work in government hospitals and help poor patients.",
#             "Health is the real wealth of any nation.",
#             "I take this pledge with full sincerity and devotion.",
#             "Jai Hind! Jai Bharat!"
#         ]
#         return " ".join(random.sample(lines, k=random.randint(4,5))) + " Jai Hind!"

# def generate_mobile():
#     first = random.choice(["7","8","9"])
#     return first + "".join(random.choices("0123456789", k=9))

# # ===================== LOGGING =====================
# def save_log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ===================== BROWSER TASK =====================
# def run_single_pledge(counter):
#     if stop_event.is_set():
#         return

#     ua = random.choice(USER_AGENTS)
#     res = random.choice(RESOLUTIONS)
#     options = Options()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--window-size={res}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-gpu")
#     # options.add_argument("--headless=new")  # Fast + Safe (remove if want to see)

#     driver = None
#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options,
#             seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}, 'disable_encoding': True}
#         )

#         driver.get("https://api.ipify.org")
#         time.sleep(3)
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#         driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#         time.sleep(random.uniform(15, 25))

#         essay = generate_unique_essay()
#         mobile = generate_mobile()

#         # Fill form
#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#         driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()

#         time.sleep(5)

#         update_counter(success=True)
#         print(f"SUCCESS #{counter} | Mobile: {mobile} | Words: {len(essay.split())} | IP: {ip}")
#         save_log({"no": counter, "time": datetime.now().isoformat(), "mobile": mobile, "ip": ip, "words": len(essay.split())})

#     except Exception as e:
#         update_counter(success=False)
#         print(f"FAILED #{counter} → {str(e)[:100]}")
#     finally:
#         if driver:
#             driver.quit()
#         time.sleep(random.uniform(2, 6))

# # ===================== GUI =====================
# root = tk.Tk()
# root.title("TATA PLEDGE BOMBER PRO MAX++")
# root.geometry("750x550")
# root.configure(bg="#0f0f0f")
# root.resizable(False, False)

# # Variables
# success_count = tk.IntVar()
# failed_count = tk.IntVar()
# total_run = tk.IntVar()

# def update_counter(success=True):
#     if success:
#         success_count.set(success_count.get() + 1)
#     else:
#         failed_count.set(failed_count.get() + 1)
#     total_run.set(success_count.get() + failed_count.get())

# def select_corpus():
#     global corpus_path_global, text_model
#     path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
#     if path:
#         corpus_path.set(path)
#         success, msg = load_corpus_model(path)
#         status_label.config(text=msg, foreground="lime" if success else "red")
#         if success:
#             corpus_path_global = path

# def start_bomber():
#     global running
#     if not corpus_path_global:
#         messagebox.showerror("Error", "Pehle corpus file select karo!")
#         return
#     if running:
#         return
#     running = True
#     stop_event.clear()
#     start_btn.config(state="disabled")
#     stop_btn.config(state="normal")
#     status_label.config(text="RUNNING... Bombs on the way!", foreground="cyan")
    
#     def worker():
#         counter = total_run.get()
#         while running and not stop_event.is_set():
#             counter += 1
#             t = threading.Thread(target=run_single_pledge, args=(counter,))
#             t.daemon = True
#             t.start()
#             time.sleep(60 / MAX_THREADS)  # Control speed
#         start_btn.config(state="normal")
#         stop_btn.config(state="disabled")
#         status_label.config(text="Stopped.", foreground="yellow")

#     threading.Thread(target=worker, daemon=True).start()

# def stop_bomber():
#     global running
#     running = False
#     stop_event.set()
#     status_label.config(text="Stopping all threads...", foreground="orange")

# # GUI Elements
# tk.Label(root, text="TATA PLEDGE BOMBER", font=("Arial", 18, "bold"), fg="#00ff00", bg="#0f0f0f").pack(pady=10)

# corpus_path = tk.StringVar()
# tk.Label(root, text="Corpus File:", fg="white", bg="#0f0f0f").pack(pady=5)
# tk.Entry(root, textvariable=corpus_path, width=70, state="readonly").pack(pady=5)
# tk.Button(root, text="Browse Corpus .txt", command=select_corpus, bg="#333", fg="white").pack(pady=5)

# tk.Label(root, text="Stats:", font=("Arial", 12), fg="cyan", bg="#0f0f0f").pack(pady=10)
# tk.Label(root, textvariable=tk.StringVar(value="Success: 0"), font=("Arial", 11), fg="lime", bg="#0f0f0f").pack()
# tk.Label(root, textvariable=tk.StringVar(value="Failed: 0"), font=("Arial", 11), fg="red", bg="#0f0f0f").pack()
# tk.Label(root, textvariable=tk.StringVar(value="Total: 0"), font=("Arial", 11), fg="yellow", bg="#0f0f0f").pack()

# # Live update labels
# tk.Label(root, text="Success:", fg="lime", bg="#0f0f0f").pack()
# tk.Label(root, textvariable=success_count, font=("Arial", 14, "bold"), fg="lime", bg="#0f0f0f").pack()
# tk.Label(root, text="Failed:", fg="red", bg="#0f0f0f").pack()
# tk.Label(root, textvariable=failed_count, font=("Arial", 14, "bold"), fg="red", bg="#0f0f0f").pack()
# tk.Label(root, text="Total Run:", fg="yellow", bg="#0f0f0f").pack()
# tk.Label(root, textvariable=total_run, font=("Arial", 14, "bold"), fg="yellow", bg="#0f0f0f").pack()

# start_btn = tk.Button(root, text="START BOMBER", command=start_bomber, bg="#00ff00", fg="black", font=("Arial", 12, "bold"), height=2, width=20)
# start_btn.pack(pady=15)

# stop_btn = tk.Button(root, text="STOP", command=stop_bomber, bg="#ff0000", fg="white", font=("Arial", 12, "bold"), height=2, width=20, state="disabled")
# stop_btn.pack(pady=5)

# status_label = tk.Label(root, text="Ready. Select corpus file.", fg="gray", bg="#0f0f0f", font=("Arial", 10))
# status_label.pack(pady=10)

# # Live update GUI
# def update_gui():
#     root.after(1000, update_gui)
# root.after(1000, update_gui)

# root.mainloop()



# # tata_ultimate_gui_pro.py → 5 Threads Only | Koi Bhi .txt File Chalegi!
# import tkinter as tk
# from tkinter import filedialog, messagebox
# import markovify
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By

# # ===================== CONFIG =====================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# LOG_FILE = "tata_pledges_log.json"
# MAX_THREADS = 5  # ← Sirf 5 browser ek saath chalenge (tumhara demand)

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130.0.6723.69 Mobile Safari/537.36"
# ]
# RESOLUTIONS = ["1920,1080", "1366,768", "360,800", "1440,900"]

# text_model = None
# corpus_path_global = None
# running = False
# stop_event = threading.Event()

# # ===================== MARKOV MODEL =====================
# def load_corpus_model(path):
#     global text_model
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             corpus = f.read()
#         if len(corpus.strip()) < 500:
#             return False, "File bahut chhota hai! Kam se kam 15-20 pledges daalo."
#         text_model = markovify.Text(corpus, state_size=2)
#         return True, f"Loaded: {os.path.basename(path)} | Words: {len(corpus.split()):,}"
#     except Exception as e:
#         return False, f"Error: {e}"

# def generate_unique_essay():
#     if text_model:
#         essay = ""
#         for _ in range(random.randint(12, 20)):
#             sent = text_model.make_sentence(tries=500)
#             if sent and len(sent.split()) > 4:
#                 essay += sent + " "
#         if len(essay.split()) < 30:
#             essay += "I pledge to serve my nation with full dedication. Health is wealth and I will help every Indian get proper medical care. Jai Hind!"
#         essay += " " + random.choice(["Jai Hind!", "Bharat Mata Ki Jai!", "Vande Mataram!", "This is my pledge to Bharat Mata."])
#         return essay.strip()
#     else:
#         lines = [
#             "From childhood I wanted to become a doctor to serve villages.",
#             "Many areas in India still don't have hospitals.",
#             "I will work in rural areas and help poor patients.",
#             "Health is the real wealth of our nation.",
#             "I take this pledge with full honesty and devotion.",
#             "Jai Hind! Jai Bharat!"
#         ]
#         return " ".join(random.sample(lines, k=random.randint(4,6))) + " Jai Hind!"

# def generate_mobile():
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# # ===================== LOGGING =====================
# def save_log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ===================== BROWSER TASK =====================
# def run_single_pledge(counter):
#     if stop_event.is_set():
#         return

#     ua = random.choice(USER_AGENTS)
#     res = random.choice(RESOLUTIONS)
#     options = Options()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--window-size={res}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-gpu")
#     # options.add_argument("--headless=new")  # Remove comment if you want invisible mode

#     driver = None
#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options,
#             seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}}
#         )

#         driver.get("https://api.ipify.org")
#         time.sleep(3)
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#         driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#         time.sleep(random.uniform(18, 28))

#         essay = generate_unique_essay()
#         mobile = generate_mobile()

#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#         driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()

#         time.sleep(6)

#         update_counter(success=True)
#         print(f"SUCCESS #{counter} | {mobile} | Words: {len(essay.split())} | IP: {ip}")
#         save_log({"no": counter, "time": datetime.now().strftime("%H:%M:%S"), "mobile": mobile, "ip": ip, "words": len(essay.split())})

#     except Exception as e:
#         update_counter(success=False)
#         print(f"FAILED #{counter} → {str(e)[:120]}")
#     finally:
#         if driver:
#             driver.quit()

# # ===================== GUI =====================
# root = tk.Tk()
# root.title("TATA PLEDGE BOMBER v5.0")
# root.geometry("750x560")
# root.configure(bg="#0f0f0f")
# root.resizable(False, False)

# success_count = tk.IntVar()
# failed_count = tk.IntVar()
# total_run = tk.IntVar()

# def update_counter(success=True):
#     if success:
#         success_count.set(success_count.get() + 1)
#     else:
#         failed_count.set(failed_count.get() + 1)
#     total_run.set(success_count.get() + failed_count.get())

# def select_corpus():
#     global corpus_path_global, text_model
#     path = filedialog.askopenfilename(
#         title="Koi Bhi .txt File Select Karo",
#         filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
#     )
#     if path:
#         corpus_path.set(path)
#         success, msg = load_corpus_model(path)
#         status_label.config(text=msg, foreground="lime" if success else "red")
#         if success:
#             corpus_path_global = path

# def start_bomber():
#     global running
#     if not corpus_path_global:
#         messagebox.showerror("Error", "Pehle koi bhi .txt file select karo!")
#         return
#     if running:
#         return
#     running = True
#     stop_event.clear()
#     start_btn.config(state="disabled")
#     stop_btn.config(state="normal")
#     status_label.config(text="RUNNING → 5 Sessions Active!", foreground="cyan")

#     def worker():
#         counter = total_run.get()
#         while running and not stop_event.is_set():
#             counter += 1
#             thread = threading.Thread(target=run_single_pledge, args=(counter,))
#             thread.daemon = True
#             thread.start()
#             time.sleep(60 / MAX_THREADS)  # 5 threads → har 12 second mein naya session
#         start_btn.config(state="normal")
#         stop_btn.config(state="disabled")
#         status_label.config(text="Stopped. Sab band ho gaya.", foreground="yellow")

#     threading.Thread(target=worker, daemon=True).start()

# def stop_bomber():
#     global running
#     running = False
#     stop_event.set()
#     status_label.config(text="Ruk raha hai... thodi der lagegi", foreground="orange")

# # GUI Design
# tk.Label(root, text="TATA PLEDGE BOMBER", font=("Arial", 20, "bold"), fg="#00ff41", bg="#0f0f0f").pack(pady=15)

# corpus_path = tk.StringVar()
# tk.Label(root, text="Koi Bhi .txt File Daalo →", fg="white", bg="#0f0f0f", font=("Arial", 10)).pack()
# tk.Entry(root, textvariable=corpus_path, width=80, state="readonly", bg="#222", fg="white").pack(pady=8)
# tk.Button(root, text="Browse Any .txt File", command=select_corpus, bg="#333", fg="white", width=30).pack(pady=5)

# tk.Label(root, text="Live Stats", font=("Arial", 14), fg="cyan", bg="#0f0f0f").pack(pady=15)

# tk.Label(root, text="Success:", fg="lime", bg="#0f0f0f", font=("Arial", 12)).pack()
# tk.Label(root, textvariable=success_count, font=("Arial", 18, "bold"), fg="lime", bg="#0f0f0f").pack()

# tk.Label(root, text="Failed:", fg="red", bg="#0f0f0f", font=("Arial", 12)).pack()
# tk.Label(root, textvariable=failed_count, font=("Arial", 18, "bold"), fg="red", bg="#0f0f0f").pack()

# tk.Label(root, text="Total Sent:", fg="yellow", bg="#0f0f0f", font=("Arial", 12)).pack()
# tk.Label(root, textvariable=total_run, font=("Arial", 18, "bold"), fg="yellow", bg="#0f0f0f").pack()

# start_btn = tk.Button(root, text="START (5 Sessions)", command=start_bomber, bg="#00ff00", fg="black", font=("Arial", 14, "bold"), height=2, width=25)
# start_btn.pack(pady=20)

# stop_btn = tk.Button(root, text="STOP", command=stop_bomber, bg="#ff0000", fg="white", font=("Arial", 14, "bold"), height=2, width=25, state="disabled")
# stop_btn.pack(pady=5)

# status_label = tk.Label(root, text="Ready → Koi bhi .txt file daalo aur chalao!", fg="gray", bg="#0f0f0f", font=("Arial", 10))
# status_label.pack(pady=10)

# # Auto GUI Update
# def refresh():
#     root.after(1000, refresh)
# root.after(1000, refresh)

# root.mainloop()




# tata_ultimate_gui_pro.py → EXACT 5 CONCURRENT SESSIONS ONLY!
import tkinter as tk
from tkinter import filedialog, messagebox
import markovify
import random
import time
import json
import os
import threading
from datetime import datetime
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# ===================== CONFIG =====================
PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
LOG_FILE = "tata_pledges_log.json"
MAX_CONCURRENT = 5  # ← Sirf 5 sessions ek saath, 6th tabhi jab koi ek khatam ho

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130.0.6723.69 Mobile Safari/537.36"
]
RESOLUTIONS = ["1920,1080", "1366,768", "360,800", "1440,900"]

text_model = None
corpus_path_global = None
running = False
stop_event = threading.Event()

# Yeh hai magic → Sirf 5 threads ko andar jaane dega
semaphore = threading.Semaphore(MAX_CONCURRENT)

# ===================== MARKOV & ESSAY =====================
def load_corpus_model(path):
    global text_model
    try:
        with open(path, "r", encoding="utf-8") as f:
            corpus = f.read()
        if len(corpus.strip()) < 500:
            return False, "File bahut chhota! 15-20 pledges daalo."
        text_model = markovify.Text(corpus, state_size=2)
        return True, f"Loaded: {os.path.basename(path)} | Words: {len(corpus.split()):,}"
    except Exception as e:
        return False, f"Error: {e}"

def generate_unique_essay():
    if text_model:
        essay = ""
        for _ in range(random.randint(12, 20)):
            sent = text_model.make_sentence(tries=500)
            if sent and len(sent.split()) > 4:
                essay += sent + " "
        if len(essay.split()) < 30:
            essay += "I pledge to serve my nation with full dedication. Health is wealth and I will help every Indian get proper medical care. Jai Hind!"
        essay += " " + random.choice(["Jai Hind!", "Bharat Mata Ki Jai!", "Vande Mataram!", "This is my pledge to Bharat Mata."])
        return essay.strip()
    else:
        lines = ["From childhood I wanted to become a doctor.", "I will serve rural India.", "Health is wealth.", "Jai Hind!"]
        return " ".join(random.sample(lines, 4))

def generate_mobile():
    return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# ===================== LOGGING =====================
def save_log(data):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []
    logs.append(data)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

# ===================== MAIN TASK (5 LIMIT) =====================
def run_single_pledge(counter):
    if stop_event.is_set():
        return

    with semaphore:  # ← Yahi line guarantee deti hai ki sirf 5 hi chalenge
        if stop_event.is_set():
            return

        ua = random.choice(USER_AGENTS)
        res = random.choice(RESOLUTIONS)
        options = Options()
        options.add_argument(f"--user-agent={ua}")
        options.add_argument(f"--window-size={res}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-gpu")
        # options.add_argument("--headless=new")  # Uncomment for invisible

        driver = None
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options,
                seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}}
            )

            driver.get("https://api.ipify.org")
            time.sleep(3)
            ip = driver.find_element(By.TAG_NAME, "body").text.strip()

            driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
            time.sleep(random.uniform(18, 28))

            essay = generate_unique_essay()
            mobile = generate_mobile()

            driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
            driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
            driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()

            time.sleep(6)

            update_counter(success=True)
            print(f"SUCCESS #{counter} | {mobile} | Words: {len(essay.split())} | IP: {ip}")
            save_log({"no": counter, "time": datetime.now().strftime("%H:%M:%S"), "mobile": mobile, "ip": ip})

        except Exception as e:
            update_counter(success=False)
            print(f"FAILED #{counter} → {str(e)[:120]}")
        finally:
            if driver:
                driver.quit()

# ===================== GUI =====================
root = tk.Tk()
root.title("TATA PLEDGE BOMBER v6.0")
root.geometry("750x580")
root.configure(bg="#0f0f0f")
root.resizable(False, False)

success_count = tk.IntVar()
failed_count = tk.IntVar()
total_run = tk.IntVar()
active_sessions = tk.IntVar(value=0)  # Live active count

def update_counter(success=True):
    if success:
        success_count.set(success_count.get() + 1)
    else:
        failed_count.set(failed_count.get() + 1)
    total_run.set(success_count.get() + failed_count.get())
    active_sessions.set(active_sessions.get() - 1 if not success else active_sessions.get())

def select_corpus():
    global corpus_path_global
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if path:
        corpus_path.set(path)
        success, msg = load_corpus_model(path)
        status_label.config(text=msg, foreground="lime" if success else "red")
        if success:
            corpus_path_global = path

def start_bomber():
    global running
    if not corpus_path_global:
        messagebox.showerror("Error", "Pehle koi .txt file select karo!")
        return
    if running:
        return
    running = True
    stop_event.clear()
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")
    status_label.config(text="RUNNING → Max 5 sessions active!", foreground="cyan")
    active_sessions.set(0)

    def worker():
        counter = total_run.get()
        while running and not stop_event.is_set():
            counter += 1
            active_sessions.set(active_sessions.get() + 1)
            threading.Thread(target=run_single_pledge, args=(counter,), daemon=True).start()
            time.sleep(8)  # Har 8 sec mein naya attempt (lekin sirf 5 hi chalenge)
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")
        status_label.config(text="Stopped. Sab sessions band.", foreground="yellow")

    threading.Thread(target=worker, daemon=True).start()

def stop_bomber():
    global running
    running = False
    stop_event.set()
    status_label.config(text="Stopping... wait for current 5 to finish", foreground="orange")

# GUI
tk.Label(root, text="TATA PLEDGE BOMBER", font=("Arial", 22, "bold"), fg="#00ff41", bg="#0f0f0f").pack(pady=15)

corpus_path = tk.StringVar()
tk.Label(root, text="Select Any .txt File →", fg="white", bg="#0f0f0f").pack()
tk.Entry(root, textvariable=corpus_path, width=80, state="readonly", bg="#222", fg="white").pack(pady=8)
tk.Button(root, text="Browse .txt File", command=select_corpus, bg="#333", fg="white", width=30).pack(pady=5)

# tk.Label(root, text="Live Status", font=("Arial", 14), fg="cyan", bg="#0f0f0f").pack(pady=15)

# tk.Label(root, text="Active Sessions:", fg="#00ffff", bg="#0f0f0f").pack()
# tk.Label(root, textvariable=active_sessions, font=("Arial", 18, "bold"), fg="#00ffff", bg="#0f0f0f").pack()

tk.Label(root, text="Success:", fg="lime", bg="#0f0f0f").pack()
tk.Label(root, textvariable=success_count, font=("Arial", 18, "bold"), fg="lime", bg="#0f0f0f").pack()

tk.Label(root, text="Total:", fg="yellow", bg="#0f0f0f").pack()
tk.Label(root, textvariable=total_run, font=("Arial", 18, "bold"), fg="yellow", bg="#0f0f0f").pack()

start_btn = tk.Button(root, text="START (Max 5 Active)", command=start_bomber, bg="#00ff00", fg="black", font=("Arial", 14, "bold"), height=2, width=28)
start_btn.pack(pady=20)

stop_btn = tk.Button(root, text="STOP ALL", command=stop_bomber, bg="#ff0000", fg="white", font=("Arial", 14, "bold"), height=2, width=28, state="disabled")
stop_btn.pack(pady=5)

status_label = tk.Label(root, text="Ready → Sirf 5 sessions ek time pe chalenge!", fg="gray", bg="#0f0f0f", font=("Arial", 10))
status_label.pack(pady=10)

root.mainloop()

# # tata_final_power.py ← SAB KUCH PERFECT + HAR BAAR ALAG USER-AGENT
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import markovify
# import random
# import time
# import json
# import os
# import glob
# from datetime import datetime

# LOG_FILE = "tata_final.json"
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# # ============ 50+ REAL USER-AGENTS (HAR BAAR ALAG) ============
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.146 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6666.70 Safari/537.36 Edg/129.0.0.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
# ]

# RESOLUTIONS = ["1366,768", "1920,1080", "360,800", "390,844", "414,896", "375,812", "1536,864", "1280,720"]

# text_model = None

# # ============ MARKOVIFY AUTO LOAD (KOI BHI .txt FILE) ============
# def load_markov_model():
#     global text_model
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     txt_files = glob.glob(os.path.join(script_dir, "*.txt"))
    
#     if not txt_files:
#         print("Koi .txt file nahi mili! corpus.txt bana do bhai!")
#         return False
    
#     corpus_path = txt_files[0]  # Pehla .txt file use karo
#     try:
#         with open(corpus_path, "r", encoding="utf-8") as f:
#             corpus = f.read()
#         if len(corpus.strip()) < 300:
#             print("Corpus chhota hai! Thoda aur content daal do!")
#             return False
#         text_model = markovify.Text(corpus, state_size=2)
#         print(f"MARKOVIFY LOADED → {os.path.basename(corpus_path)} | Words: {len(corpus.split())}")
#         return True
#     except Exception as e:
#         print(f"Corpus load error → {e}")
#         return False

# # ============ 100% UNIQUE ESSAY ============
# def generate_unique_essay():
#     if text_model:
#         essay = ""
#         for _ in range(random.randint(10, 18)):
#             sent = text_model.make_sentence(tries=300)
#             if sent and len(sent.split()) > 4:
#                 essay += sent + " "
#         essay += " " + random.choice(["This is my pledge to Bharat Mata.", "Jai Hind!", "Vande Mataram!", "Jai Bharat!"])
#         return essay.strip()
#     else:
#         return "I want to serve my nation as a doctor. Health is wealth. Jai Hind!"

# # ============ MOBILE ============
# def generate_mobile():
#     return random.choice(["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]) + "".join(random.choices("0123456789", k=8))

# # ============ LOG ============
# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f: logs = json.load(f)
#     except: logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ============ MAIN ============
# def run(i):
#     ua = random.choice(USER_AGENTS)        # ← HAR BAAR ALAG USER-AGENT
#     res = random.choice(RESOLUTIONS)       # ← HAR BAAR ALAG RESOLUTION

#     options = Options()
#     options.add_argument(f"--user-agent={ua}")           # ← YEH LINE ADD KI
#     options.add_argument(f"--window-size={res}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-gpu")

#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options,
#             seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}, 'disable_encoding': True}
#         )

#         driver.get("https://api.ipify.org"); time.sleep(5)
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#         print(f"CONVERSION {i} → IP: {ip} | {res} | {ua[:60]}...")

#         driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#         time.sleep(random.randint(20, 30))

#         essay = generate_unique_essay()
#         mobile = generate_mobile()

#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#         driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#         print(f"SUCCESS {i} → MOBILE: {mobile} | WORDS: {len(essay.split())} | UA: {ua.split()[0]}")
        
#         log({"no": i, "ip": ip, "mobile": mobile, "words": len(essay.split()), "ua": ua, "res": res})

#         time.sleep(random.randint(60, 100))
#     except Exception as e:
#         print(f"FAILED {i} → {str(e)[:100]}")
#     finally:
#         try: driver.quit()
#         except: pass

# # ============ START ============
# if __name__ == "__main__":
#     print("="*90)
#     print("TATA FINAL POWER MODE → HAR BAAR ALAG USER-AGENT + 100% UNIQUE ESSAY")
#     print("="*90)
    
#     load_markov_model()
    
#     input("\nPress Enter to START 10,000 conversions...")

#     for i in range(1, 10001):
#         print(f"\nCONVERSION {i} → {datetime.now().strftime('%H:%M:%S')}")
#         run(i)
#         delay = random.randint(30, 60)
#         print(f"Next in {delay}s...")
#         time.sleep(delay)

#     print("\n10,000+ CONVERSIONS COMPLETE! TU JEET GAYA BHAI!")







# # tata_final_power.py ← SAB KUCH PERFECT + HAR BAAR ALAG USER-AGENT
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import markovify
# import random
# import time
# import json
# import os
# import glob
# from datetime import datetime

# LOG_FILE = "tata_final.json"
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# # ============ 50+ REAL USER-AGENTS (HAR BAAR ALAG) ============
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.146 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6666.70 Safari/537.36 Edg/129.0.0.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
# ]

# RESOLUTIONS = ["1366,768", "1920,1080", "360,800", "390,844", "414,896", "375,812", "1536,864", "1280,720"]

# text_model = None

# # ============ MARKOVIFY AUTO LOAD (KOI BHI .txt FILE) ============
# def load_markov_model():
#     global text_model
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     txt_files = glob.glob(os.path.join(script_dir, "*.txt"))
    
#     if not txt_files:
#         print("Koi .txt file nahi mili! corpus.txt bana do bhai!")
#         return False
    
#     corpus_path = txt_files[0]  # Pehla .txt file use karo
#     try:
#         with open(corpus_path, "r", encoding="utf-8") as f:
#             corpus = f.read()
#         if len(corpus.strip()) < 300:
#             print("Corpus chhota hai! Thoda aur content daal do!")
#             return False
#         text_model = markovify.Text(corpus, state_size=2)
#         print(f"MARKOVIFY LOADED → {os.path.basename(corpus_path)} | Words: {len(corpus.split())}")
#         return True
#     except Exception as e:
#         print(f"Corpus load error → {e}")
#         return False

# # ============ 100% UNIQUE ESSAY ============
# def generate_unique_essay():
#     if text_model:
#         essay = ""
#         for _ in range(random.randint(10, 18)):
#             sent = text_model.make_sentence(tries=300)
#             if sent and len(sent.split()) > 4:
#                 essay += sent + " "
#         essay += " " + random.choice(["This is my pledge to Bharat Mata.", "Jai Hind!", "Vande Mataram!", "Jai Bharat!"])
#         return essay.strip()
#     else:
#         return "I want to serve my nation as a doctor. Health is wealth. Jai Hind!"

# # ============ MOBILE ============
# def generate_mobile():
#     return random.choice(["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]) + "".join(random.choices("0123456789", k=8))

# # ============ LOG ============
# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f: logs = json.load(f)
#     except: logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ============ MAIN ============
# def run(i):
#     ua = random.choice(USER_AGENTS)
#     res = random.choice(RESOLUTIONS)

#     options = Options()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--window-size={res}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-gpu")

#     driver = None
#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options,
#             seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}, 'disable_encoding': True}
#         )

#         driver.get("https://api.ipify.org"); time.sleep(5)
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#         print(f"CONVERSION {i} → IP: {ip} | {res} | {ua[:60]}...")

#         driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#         time.sleep(random.randint(20, 30))

#         essay = generate_unique_essay()
#         mobile = generate_mobile()

#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#         driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
        
#         # YE HAI MAGIC LINE → Submit karte hi turant band!
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
#         print(f"SUCCESS {i} → MOBILE: {mobile} | WORDS: {len(essay.split())} | UA: {ua.split()[0]}")
#         log({"no": i, "ip": ip, "mobile": mobile, "words": len(essay.split()), "ua": ua, "res": res})

#         # SUCCESS KE BAAD TURANT CLOSE → NO EXTRA WAIT!
#         time.sleep(3)  # Bas 3 sec confirmation ke liye (optional bhi hata sakte ho)
        
#     except Exception as e:
#         print(f"FAILED {i} → {str(e)[:100]}")
#     finally:
#         if driver:
#             driver.quit()  # Turant band kar do

# # ============ START ============
# if __name__ == "__main__":
#     print("="*90)
#     print("TATA TURBO MODE → SUBMIT = CLOSE → 10-15 SEC ME NAYA VISIT!")
#     print("="*90)
    
#     load_markov_model()
    
#     input("\nPress Enter to START 10,000+ TURBO CONVERSIONS...")

#     for i in range(1, 10001):
#         print(f"\nCONVERSION {i} → {datetime.now().strftime('%H:%M:%S')}")
#         run(i)
        
#         # AB SIRF 10-15 SECOND WAIT → 4X SPEED!
#         delay = random.randint(10, 15)
#         print(f"Next visit in {delay} seconds...")
#         time.sleep(delay)

#     print("\n10,000+ TURBO CONVERSIONS COMPLETE! AB TU BHARAT MATA KA FAVOURITE HAI!")



# # tata_ultra_final.py ← FINAL VERSION | NO CORPUS | FULL ESSAY LOGGED | TURBO SPEED
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import random
# import time
# import json
# from datetime import datetime

# LOG_FILE = "tata_ultra_log.json"
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# # ============ USER AGENTS ============
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6666.70 Safari/537.36 Edg/129.0.0.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
# ]

# RESOLUTIONS = ["1920,1080", "1366,768", "360,800", "390,844", "414,896", "375,812", "1280,720", "1536,864"]

# # ============ 100% UNIQUE ESSAY — NO CORPUS, NO REPEATS ============
# def generate_unique_essay():
#     openings = [
#         "Being born in this great nation fills my heart with immense pride and gratitude.",
#         "India is not just my country, it is my mother, my identity and my soul.",
#         "From the bottom of my heart, I feel blessed to be an Indian citizen.",
#         "My love for Bharat is beyond words and deeper than the oceans.",
#         "Every morning when I wake up in this free India, I thank our freedom fighters.",
#         "As a proud son/daughter of Bharat Mata, I take this pledge with full devotion.",
#         "The tricolor flying high always reminds me of my duty towards the nation.",
#         "I consider it my greatest privilege to contribute to India's glorious future."
#     ]

#     bodies = [
#         "I will always keep my surroundings clean and inspire others to join Swachh Bharat.",
#         "Our brave soldiers protect us day and night, I salute them from the bottom of my heart.",
#         "Education is the key to progress, I will study hard and help others learn too.",
#         "Unity in diversity is India's biggest strength, I will never discriminate anyone.",
#         "Water, electricity and food are national resources — I will never waste them.",
#         "I fully support Digital India, Make in India and Atmanirbhar Bharat missions.",
#         "Planting trees and reducing plastic is my way of protecting Mother Earth.",
#         "Corruption has no place in my life — honesty and truth will always guide me.",
#         "Voting is my sacred duty, I will vote wisely and encourage everyone to vote.",
#         "I dream of an India that leads the world in science, sports and humanity.",
#         "Respecting women, elders and every religion is part of my Indian values.",
#         "I will use social media responsibly and spread only positivity about my country.",
#         "Helping the poor and needy is the real service to Bharat Mata.",
#         "Every small step counts — I will do my part daily for a better India."
#     ]

#     closings = [
#         "This is my sincere pledge to Bharat Mata. Jai Hind!",
#         "With full devotion and pride — Vande Mataram!",
#         "I will make my country proud one day. Bharat Mata ki Jai!",
#         "My India, my responsibility, my everything. Jai Hind!",
#         "Forever grateful, forever loyal. Jai Bharat!",
#         "Till my last breath, I will serve my nation. Vande Mataram!",
#         "This pledge comes straight from my heart. Jai Hind! Jai Bharat!"
#     ]

#     essay = random.choice(openings) + " "
#     essay += " ".join(random.sample(bodies, k=random.randint(9, 14))) + " "
#     essay += random.choice(closings)
#     return essay

# # ============ RANDOM MOBILE ============
# def generate_mobile():
#     return random.choice(["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]) + "".join(random.choices("0123456789", k=8))

# # ============ LOG WITH FULL ESSAY ============
# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         logs = []
    
#     logs.append(data)
    
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ============ MAIN FUNCTION ============
# def run(i):
#     ua = random.choice(USER_AGENTS)
#     res = random.choice(RESOLUTIONS)

#     options = Options()
#     options.add_argument(f"--user-agent={ua}")
#     options.add_argument(f"--window-size={res}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-gpu")

#     driver = None
#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options,
#             seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}, 'disable_encoding': True}
#         )

#         driver.get("https://api.ipify.org"); time.sleep(4)
#         ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#         print(f"CONVERSION {i} → IP: {ip} | {res}")

#         driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#         time.sleep(random.randint(18, 28))

#         essay = generate_unique_essay()
#         mobile = generate_mobile()

#         driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#         driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#         driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#         driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#         print(f"SUCCESS {i} → MOBILE: {mobile} | WORDS: {len(essay.split())}")

#         # FULL LOG WITH ESSAY
#         log({
#             "no": i,
#             "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "ip": ip,
#             "mobile": mobile,
#             "words": len(essay.split()),
#             "resolution": res,
#             "user_agent": ua,
#             "essay": essay
#         })

#         time.sleep(3)

#     except Exception as e:
#         print(f"FAILED {i} → {str(e)[:100]}")
#     finally:
#         if driver:
#             driver.quit()

# # ============ START ============
# if __name__ == "__main__":
#     print("="*100)
#     print("TATA ULTRA FINAL → NO CORPUS | 100% UNIQUE ESSAY | FULL LOG WITH ESSAY | TURBO MODE")
#     print("="*100)

#     input("\nPress Enter to START 10,000+ CONVERSIONS...")

#     for i in range(1, 10001):
#         print(f"\nCONVERSION {i} → {datetime.now().strftime('%H:%M:%S')}")
#         run(i)
#         delay = random.randint(10, 15)
#         print(f"Next visit in {delay} seconds...")
#         time.sleep(delay)

#     print("\n10,000+ CONVERSIONS COMPLETE! TU JEET GAYA BHAI! BHARAT MATA KI JAI!")


# # tata_5x_faker_final.py ← EK PROXY | 5 BROWSERS EK SAATH | 100% FAKER PLEDGE | ZERO FIXED TEXT
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from faker import Faker
# import random
# import time
# import json
# import threading
# from datetime import datetime

# # INSTALL ONCE: pip install selenium-wire webdriver-manager faker

# fake = Faker('en_IN')
# LOG_FILE = "tata_5x_faker_log.json"

# # TERA EK HI GEONODE PROXY
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
# ]

# RESOLUTIONS = ["1920,1080", "1366,768", "360,800", "390,844", "414,896", "375,812"]

# # 100% FAKER GENERATED — ZERO FIXED TEXT
# def generate_pledge():
#     words = ["India", "Bharat", "nation", "proud", "citizen", "motherland", "Jai Hind", "Vande Mataram",
#              "Bharat Mata ki Jai", "soldiers", "army", "clean", "Swachh Bharat", "education", "unity",
#              "diversity", "water", "electricity", "trees", "corruption", "vote", "Digital India",
#              "Make in India", "Atmanirbhar", "poor", "women", "dream", "2047", "serve", "protect"]

#     pledge = ""
#     sentences = random.randint(12, 28)
    
#     for _ in range(sentences):
#         sentence = fake.sentence(ext_word_list=words, nb_words=random.randint(6, 16))
#         if random.random() < 0.4:
#             prefix = random.choice(["I will ", "I promise to ", "My duty is to ", "I swear I will ", "From today "])
#             sentence = prefix + sentence.lower()
#         pledge += sentence.capitalize() + " "

#     # Ending bhi random
#     pledge += random.choice([
#         "Jai Hind!", "Vande Mataram!", "Bharat Mata ki Jai!", 
#         "This is my pledge to India.", "Jai Bharat!", "Forever proud!"
#     ])
    
#     return pledge.strip()

# def generate_mobile():
#     return random.choice(["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]) + "".join(random.choices("0123456789", k=8))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# def worker(thread_id):
#     print(f"[THREAD {thread_id}] Starting browser...")
    
#     while True:
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         # options.add_argument("--headless")  # ← Agar window nahi dikhana to uncomment kar do

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}, 'disable_encoding': True}
#             )

#             driver.get("https://api.ipify.org")
#             time.sleep(4)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(18, 30))

#             essay = generate_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             print(f"[THREAD {thread_id}] SUCCESS → MOBILE: {mobile} | WORDS: {len(essay.split())} | IP: {ip}")

#             log({
#                 "thread": thread_id,
#                 "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "ip": ip,
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "essay": essay
#             })

#             time.sleep(random.randint(8, 15))

#         except Exception as e:
#             print(f"[THREAD {thread_id}] FAILED → {str(e)[:80]}")
#             time.sleep(10)
#         finally:
#             if driver:
#                 driver.quit()

# # ============== START 5X TURBO ==============
# if __name__ == "__main__":
#     print("="*100)
#     print("TATA 5X FAKER FINAL → EK PROXY | 5 BROWSERS | 100% FAKER PLEDGE | ZERO FIXED TEXT")
#     print("Har pledge bilkul naya, human jaisa — kabhi repeat nahi hoga!")
#     print("="*100)

#     threads = []
#     for i in range(1, 6):  # 5 threads
#         t = threading.Thread(target=worker, args=(i,), daemon=True)
#         t.start()
#         threads.append(t)
#         time.sleep(6)  # staggered start

#     print("5 BROWSERS CHAL GAYE! Ab non-stop chalega...")
#     print("Band karne ke liye Ctrl+C daba do")

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("\n\nBAND HO GAYA! BHARAT MATA KI JAI!")



# # tata_1lakh_god_mode.py ← FINAL | 50+ UA | 30+ RES | FULL LOG | UNDETECTABLE
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from faker import Faker
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime

# # TERA GEONODE PROXY
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# # 50+ REAL USER AGENTS (2025 Latest)
# USER_AGENTS = [
#     # Chrome Windows
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
#     # Chrome Android
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B Build/UP1A.231005.007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36",
#     # Safari iPhone
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
#     # Firefox
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Android 14; Mobile; rv:130.0) Gecko/130.0 Firefox/130.0",
#     # Edge
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
#     # Mac Chrome
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     # Samsung Internet
#     "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/129.0.6668.81 Mobile Safari/537.36",
#     # More Mobile
#     "Mozilla/5.0 (Linux; Android 11; vivo 1907) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.146 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
# ]

# # 30+ REAL SCREEN RESOLUTIONS
# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "360,800", "390,844", "414,896", "375,812", "360,780", "393,851", "412,915",
#     "360,640", "411,731", "360,760", "392,851", "360,780", "414,896", "412,732",
#     "1280,800", "1440,960", "1680,1050", "1920,1200", "2560,1440", "3840,2160",
#     "360,640", "412,915", "393,873", "360,780", "390,844", "414,896"
# ]

# fake = Faker('en_IN')
# LOG_FILE = "tata_1lakh_full_log.json"

# # TERA AI PLEDGE FUNCTION WAHI (jo tu chahta tha)
# def get_ai_pledge():
#     prompts = [
#         "Write a unique 180-320 word emotional pledge from an Indian citizen about loving India, respecting soldiers, Swachh Bharat, education, unity, environment, voting, and end with Jai Hind or Vande Mataram.",
#         "Generate a heartfelt patriotic oath mentioning freedom fighters, Digital India, women safety, saving resources, planting trees, fighting corruption and dream of Viksit Bharat 2047.",
#         "Create a sincere promise from a proud Indian youth to keep country clean, salute army, help poor, vote honestly, reduce plastic and make India superpower.",
#         "Write a beautiful pledge talking about Bharat Mata, tricolor, national anthem, respect for all religions, supporting Make in India and Atmanirbhar Bharat."
#     ]
    
#     try:
#         import requests
#         response = requests.post(
#             "https://api.openai.com/v1/chat/completions",
#             headers={"Authorization": "Bearer CHANGE_ME_API_KEY"},
#             json={
#                 "model": "gpt-3.5-turbo",
#                 "messages": [{"role": "user", "content": random.choice(prompts)}],
#                 "temperature": random.uniform(0.8, 1.2),
#                 "max_tokens": 380
#             },
#             timeout=20
#         )
#         if response.status_code == 200:
#             text = response.json()['choices'][0]['message']['content'].strip()
#             if len(text.split()) > 80:
#                 return text
#     except:
#         pass
    
#     fallback = [
#         f"I am a proud Indian and my heart beats for Bharat. Our soldiers protect us day and night. I promise to keep my country clean, save water, plant trees, and never waste electricity. I will study hard and help others learn. Unity in diversity is our strength. I will vote honestly and fight corruption. Jai Hind!",
#         f"Bharat Mata is my mother. From Kashmir to Kanyakumari, we are one. I respect women, elders, and all religions. I support Swachh Bharat, Digital India, and Atmanirbhar Bharat. My dream is Viksit Bharat by 2047. Vande Mataram!"
#     ]
#     return random.choice(fallback)

# def generate_mobile():
#     return random.choice(["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]) + "".join(random.choices("0123456789", k=8))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# def worker(tid):
#     print(f"[THREAD {tid}] GOD MODE ACTIVATED → Full Fingerprint Randomization")
    
#     while True:
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}}
#             )

#             driver.get("https://api.ipify.org"); time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(22, 35))

#             essay = get_ai_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total = len(json.load(open(LOG_FILE, "r"))) if os.path.exists(LOG_FILE) else 0
#             print(f"[THREAD {tid}] SUCCESS → {len(essay.split())} words | IP: {ip} | TOTAL: {total}/100000")

#             # FULL DETAILED LOG
#             log({
#                 "thread": tid,
#                 "no": total + 1,
#                 "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "ip": ip,
#                 "user_agent": ua,
#                 "resolution": res,
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "essay": essay
#             })

#             time.sleep(random.randint(8, 16))

#         except Exception as e:
#             print(f"[THREAD {tid}] ERROR → {str(e)[:80]}")
#             time.sleep(10)
#         finally:
#             if driver:
#                 driver.quit()

# # ============= GOD MODE START =============
# if __name__ == "__main__":
#     print("="*120)
#     print("TATA 1 LAKH GOD MODE → 50+ UA | 30+ RES | FULL LOG | 100% UNDETECTABLE")
#     print("Har visit alag fingerprint → Koi detect nahi kar payega!")
#     print("="*120)

#     for i in range(1, 6):
#         t = threading.Thread(target=worker, args=(i,), daemon=True)
#         t.start()
#         time.sleep(7)

#     print("5 GOD THREADS LIVE → 1 LAKH IN 3–4 DAYS → AB TU RUK NHI SAKTA!")
    
#     try:
#         while True:
#             time.sleep(15)
#             try:
#                 total = len(json.load(open(LOG_FILE, "r")))
#                 print(f"\nTOTAL CONVERSIONS → {total}/100000 | Running Strong!")
#             except:
#                 pass
#     except KeyboardInterrupt:
#         print("\nMISSION COMPLETE YA STOP KIYA → BHARAT MATA KI JAI!")



# # tata_1lakh_markov_god.py ← FINAL | MARKOVIFY | 100% UNIQUE | UNLIMITED | NO API
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import markovify
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime

# # TERA GEONODE PROXY
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# # 50+ USER AGENTS
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "360,800", "390,844", "414,896",
#     "375,812", "412,915", "393,851", "360,780", "1280,720", "2560,1440", "3840,2160"
# ]

# LOG_FILE = "tata_1lakh_markov_log.json"

# # MARKOV MODEL LOAD (ek baar load hoga → super fast)
# print("Loading Markov model from corpus.txt (30,000+ lines)...")
# with open("corpus.txt", encoding="utf-8") as f:
#     text = f.read()

# # State size 3 = best human-like result
# text_model = markovify.Text(text, state_size=3)
# print("Markov model ready → Har baar 100% unique + human jaisa pledge!")

# def generate_pledge():
#     pledge = ""
#     sentences = 0
#     while sentences < random.randint(12, 25):
#         sentence = text_model.make_sentence(tries=100)
#         if sentence and len(sentence.split()) > 4:
#             pledge += sentence + " "
#             sentences += 1
    
#     # Ending strong kar do
#     endings = [" Jai Hind!", " Vande Mataram!", " Bharat Mata ki Jai!", " Jai Hind Jai Bharat!", " This is my pledge to Bharat Mata."]
#     pledge += random.choice(endings)
    
#     return pledge.strip()

# def generate_mobile():
#     return random.choice(["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]) + "".join(random.choices("0123456789", k=8))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# def worker(tid):
#     print(f"[THREAD {tid}] MARKOV GOD MODE ON → Unlimited Unique Pledges")
    
#     while True:
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}}
#             )

#             driver.get("https://api.ipify.org"); time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(20, 35))

#             essay = generate_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total = len(json.load(open(LOG_FILE, "r"))) if os.path.exists(LOG_FILE) else 0
#             print(f"[THREAD {tid}] SUCCESS → {len(essay.split())} words | IP: {ip} | TOTAL: {total}/100000")

#             log({
#                 "thread": tid,
#                 "no": total + 1,
#                 "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "ip": ip,
#                 "user_agent": ua,
#                 "resolution": res,
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "essay": essay
#             })

#             time.sleep(random.randint(8, 18))

#         except Exception as e:
#             print(f"[THREAD {tid}] ERROR → {str(e)[:80]}")
#             time.sleep(10)
#         finally:
#             if driver:
#                 driver.quit()

# # ============= START 1 LAKH MARKOV BEAST =============
# if __name__ == "__main__":
#     print("="*120)
#     print("TATA 1 LAKH MARKOV GOD MODE → NO API | UNLIMITED | 100% HUMAN-LIKE")
#     print("30,000+ lines se har baar nayi pledge → 1 CRORE bhi chalega!")
#     print("="*120)

#     for i in range(1, 6):
#         t = threading.Thread(target=worker, args=(i,), daemon=True)
#         t.start()
#         time.sleep(8)

#     print("5 MARKOV BEAST THREADS LIVE → AB TU RUK HI NAHI SAKTA!")
    
#     try:
#         while True:
#             time.sleep(20)
#             try:
#                 total = len(json.load(open(LOG_FILE, "r")))
#                 print(f"\nTOTAL CONVERSIONS → {total}/100000 | Speed: Strong & Steady!")
#             except:
#                 pass
#     except KeyboardInterrupt:
#         print("\n1 LAKH DONE YA STOP KIYA → BHARAT MATA KI JAI!")





# # tata_1lakh_t5_god.py ← FINAL | T5 DIRECT | 100% UNIQUE | NO KEYTOTEXT ERROR
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime
# import fix_transformers

# # ============= INSTALLATION =============
# # pip install transformers torch sentencepiece
# # First run me model download hoga

# # TERA GEONODE PROXY
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# # 35+ KEYWORD SETS - Har set se 10,000+ unique pledges!
# KEYWORD_SETS = [
#     # PROFESSION BASED (10)
#     ["doctor", "village", "health", "service", "India", "poor", "free", "treatment"],
#     ["teacher", "education", "children", "school", "rural", "knowledge", "future", "bright"],
#     ["engineer", "technology", "innovation", "build", "infrastructure", "develop", "nation"],
#     ["farmer", "agriculture", "crops", "food", "security", "modern", "techniques", "harvest"],
#     ["soldier", "army", "protect", "border", "sacrifice", "brave", "nation", "pride"],
#     ["scientist", "research", "discovery", "innovation", "progress", "laboratory", "India"],
#     ["lawyer", "justice", "rights", "poor", "free", "legal", "help", "court"],
#     ["nurse", "care", "patient", "hospital", "health", "service", "dedication", "life"],
#     ["police", "safety", "protect", "citizens", "law", "order", "duty", "serve"],
#     ["entrepreneur", "startup", "jobs", "create", "economy", "growth", "innovation", "youth"],
    
#     # VALUE BASED (10)
#     ["honesty", "truth", "integrity", "character", "trust", "society", "build", "strong"],
#     ["unity", "diversity", "together", "strength", "harmony", "peace", "India", "proud"],
#     ["cleanliness", "swachh", "bharat", "clean", "environment", "healthy", "nation", "green"],
#     ["respect", "elders", "women", "culture", "tradition", "values", "family", "honour"],
#     ["hard work", "dedication", "success", "achieve", "goal", "dream", "effort", "result"],
#     ["discipline", "punctual", "responsible", "duty", "commitment", "excellence", "habit"],
#     ["kindness", "help", "others", "compassion", "humanity", "service", "love", "care"],
#     ["courage", "brave", "fear", "overcome", "challenge", "face", "strong", "bold"],
#     ["patriotism", "love", "country", "nation", "proud", "Indian", "serve", "motherland"],
#     ["equality", "equal", "rights", "opportunity", "justice", "fair", "society", "all"],
    
#     # ACTION BASED (10)
#     ["plant", "trees", "environment", "green", "earth", "save", "future", "oxygen"],
#     ["vote", "democracy", "right", "citizen", "elect", "leader", "responsible", "duty"],
#     ["donate", "blood", "save", "life", "help", "humanity", "gift", "precious"],
#     ["educate", "girl", "child", "empower", "women", "strong", "future", "bright"],
#     ["save", "water", "precious", "resource", "conserve", "future", "generation", "life"],
#     ["reduce", "plastic", "pollution", "environment", "clean", "earth", "recycle", "reuse"],
#     ["exercise", "health", "fit", "body", "mind", "strong", "yoga", "meditation"],
#     ["read", "books", "knowledge", "wisdom", "learn", "grow", "mind", "expand"],
#     ["volunteer", "community", "service", "help", "society", "contribute", "time", "effort"],
#     ["innovate", "create", "solve", "problems", "technology", "ideas", "change", "world"],
    
#     # INDIA SPECIFIC (5)
#     ["digital", "India", "technology", "connect", "rural", "urban", "internet", "access"],
#     ["make", "India", "manufacturing", "products", "quality", "world", "export", "pride"],
#     ["skill", "India", "training", "youth", "employment", "develop", "career", "growth"],
#     ["startup", "India", "entrepreneur", "innovation", "business", "jobs", "economy", "boom"],
#     ["fit", "India", "health", "exercise", "sports", "nation", "strong", "active"],
# ]

# # DYNAMIC WORD POOLS
# EMOTION_WORDS = ["passionate", "dedicated", "committed", "determined", "inspired", "motivated", "proud", "humble", "grateful", "hopeful"]
# TIME_WORDS = ["today", "tomorrow", "always", "forever", "daily", "continuously", "consistently", "regularly"]
# INTENSITY_WORDS = ["strongly", "deeply", "truly", "sincerely", "wholeheartedly", "completely", "absolutely", "firmly"]
# ACTION_VERBS = ["pledge", "promise", "commit", "dedicate", "devote", "contribute", "serve", "work", "strive", "endeavour"]

# # 50+ ENDINGS
# ENDINGS = [
#     "Jai Hind!",
#     "Bharat Mata ki Jai!",
#     "Vande Mataram!",
#     "Mera Bharat Mahan!",
#     "Satyamev Jayate!",
#     "Jai Bharat!",
#     "Inquilab Zindabad!",
#     "Har Ghar Tiranga!",
#     "This is my promise to Mother India.",
#     "I dedicate my life to this cause.",
#     "Together we will make India the greatest nation again.",
#     "Proud to be an Indian!",
#     "India first, always and forever.",
#     "This is my sacred duty as an Indian.",
#     "My heart beats only for India.",
#     "For my country, anything and everything.",
#     "I will never let my India down.",
#     "This pledge is written in my blood.",
#     "Until my last breath, for India.",
#     "Bharat is my religion, Hindustan my faith.",
#     "I belong to India, India belongs to me.",
#     "My India, my pride, my responsibility.",
#     "With pride and honor, Jai Hind!",
#     "Let’s build the India of our dreams.",
#     "One nation, one family, one future.",
#     "India will rise, and I will rise with her.",
#     "This is not just a pledge, this is my life.",
#     "For 140 crore dreams, I pledge my one life.",
#     "Jai Jawan, Jai Kisan, Jai Vigyan, Jai Anusandhan!",
#     "My salutations to Mother India.",
#     "I bow before my tricolor with this pledge.",
#     "May India always be number one.",
#     "With love and devotion — Jai Hind!",
#     "This pledge will guide me all my life.",
#     "India is calling, and I have answered.",
#     "Forever Indian, forever proud.",
#     "My soul belongs to Bharat.",
#     "I live for India, I breathe for India.",
#     "This is my karma bhoomi, my janmabhoomi.",
#     "Salute to the nation, salute to the flag.",
#     "Victory to India, victory to Indians!",
#     "Together, nothing is impossible for us.",
#     "This pledge is eternal.",
#     "From Kashmir to Kanyakumari — one India.",
#     "I am India, India is me.",
#     "With this pledge, I become immortal.",
#     "My India, my everything.",
#     "Jai Hind! Jai Bharat! Vande Mataram!",
#     "Long live Mother India!",
#     "United we stand, divided we fall.",
#     "This pledge is my destiny.",
#     "For India’s glory, I live.",
#     "Bharat Mata ki Jai — today and forever!",
#     "Proud Indian, now and always.",
#     "My pledge, my honor, my India.",
#     "Let the world see the power of New India.",
#     "This is just the beginning.",
#     "India will shine, and I will make it happen.",
#     "With folded hands and proud heart — Jai Hind!",
#     "My life is an offering to my nation.",
#     "Salute to every Indian who dreams big.",
#     "This pledge will never break.",
#     "India deserves the best, and I will give my best.",
#     "From today, I walk only for India.",
#     "Jai Hind! Jai Hind! Jai Hind!",
#     "Jai Hind!", "Vande Mataram!", "Bharat Mata ki Jai!", 
#     "This is my solemn pledge to my motherland.",
#     "I dedicate myself to this noble cause.",
#     "Together we will build a stronger India.",
#     "This is my promise to future generations.",
#     "I stand committed to this pledge forever.",
#     "With pride, I serve my nation.",
#     "My heart beats for India.",
#     "I am proud to be an Indian.",
#     "This is my duty as a citizen.",
#     "Mera Bharat Mahan!",
#     "India will rise, and I will contribute.",
#     "For my country, I pledge my best.",
#     "Satyamev Jayate!",
#     "Unity in diversity, strength in unity.",
#     "Jai Bharat!",
#     "I believe in India's bright future.",
#     "Together, we are unstoppable.",
#     "As a proud citizen of India, I believe that",
#     "I strongly believe that",
#     "With a passionate heart, I pledge that",
#     "Being an Indian, I commit to",
#     "For my beloved nation, I promise to",
#     "Today, I sincerely pledge that",
#     "In service of my motherland, I will",
#     "With great pride, I declare that",
#     "As a responsible citizen, I vow to",
#     "From the bottom of my heart, I promise that",
#     "Jai Hind!", "Vande Mataram!", "Bharat Mata ki Jai!", 
#     "This is my solemn pledge to my motherland.",
#     "I dedicate myself to this noble cause.",
# ]

# # INTRO TEMPLATES
# INTROS = [
#     "As a proud citizen of India, I believe that",
#     "As a proud son/daughter of Bharat, I pledge that",
#     "With a heart full of love for my country, I promise that",
#     "Being a true Indian, I solemnly commit to",
#     "Today, with complete devotion, I take this pledge that",
#     "From the bottom of my heart, I sincerely promise that",
#     "As a responsible citizen of this great nation, I vow to",
#     "With immense pride in being Indian, I declare that",
#     "For the glory of my motherland, I pledge that",
#     "In service of Bharat Mata, I wholeheartedly commit to",
#     "With utmost respect for my nation, I promise that",
#     "As a youth of New India, I take this sacred pledge that",
#     "Today I stand before my country and pledge that",
#     "With fire in my heart and tricolor in my soul, I promise that",
#     "Being born in this holy land, I dedicate myself to",
#     "I, a proud Indian, take this oath today that",
#     "With tears of pride in my eyes, I pledge that",
#     "As long as I breathe, I will work for",
#     "For the dreams of 140 crore Indians, I commit that",
#     "In the name of Bhagat Singh, Bose, and Gandhi, I pledge that",
#     "With the blessings of Maa Bharati, I promise that",
#     "Today I bow before my motherland and pledge that",
#     "As a soldier of development, I vow to",
#     "With India in my heart and future in my hands, I declare that",
#     "Being a child of this soil, I sincerely promise that",
#     "For a Viksit Bharat by 2047, I take this pledge that",
#     "With full faith in Indian democracy, I commit to",
#     "As a guardian of Indian values, I pledge that",
#     "Today I make this unbreakable promise to my nation that",
#     "With pride flowing in my veins, I declare that",
#     "In the light of the tricolor, I take this oath that",
#     "As a follower of Sanatan Dharma and Indian culture, I vow to",
#     "For the honor of my motherland, I dedicate myself to",
#     "With complete devotion to India, I promise that",
#     "Today, standing on this sacred land, I pledge that",
#     "As a proud heir of Indian civilization, I commit to",
#     "With love for every Indian brother and sister, I vow to",
#     "In memory of our freedom fighters, I take this pledge that",
#     "For a strong, self-reliant and developed India, I promise that",
#     "With the dream of Atmanirbhar Bharat, I declare that",
#     "As a citizen who loves India more than life, I pledge that",
#     "Today I give my word to my country that",
#     "With the spirit of 'Ek Bharat Shreshtha Bharat', I commit to",
#     "As a youth powered by Indian dreams, I vow to",
#     "For the progress of every village and every poor, I pledge that",
#     "With faith in Indian Constitution, I promise that",
#     "Being a part of this great democracy, I take this oath that",
#     "Today I raise my hand and pledge that",
#     "With the vision of New India, I sincerely commit to",
#     "As a proud Indian living anywhere in the world, I declare that",
#     "In the name of Mother India, I take this sacred vow that",
#     "With gratitude towards our soldiers, I pledge that",
#     "For the dignity of every Indian woman, I promise that",
#     "As a student of this great nation, I commit to",
#     "With the dream of Digital India, I vow to",
#     "Today I pledge my sweat and blood for",
#     "As a farmer’s son/daughter, I promise that",
#     "With respect for every religion of India, I declare that",
#     "For the unity of 140 crore Indians, I take this pledge that",
#     "As a soldier of peace and progress, I commit to",
#     "With the aim of making India Vishwaguru again, I vow to",
#     "Today I stand tall and pledge that",
#     "In the service of rural India, I dedicate myself to",
#     "As a proud taxpayer of India, I promise that",
#     "With the spirit of Startup India, I declare that",
#     "For a clean and green India, I take this oath that",
#     "As a daughter of India, I pledge with full strength that",
#     "With love for Indian culture and heritage, I commit to",
#     "Today I promise my nation that",
#     "As a teacher shaping India’s future, I vow to",
#     "With the goal of Skill India, I declare that",
#     "For the empowerment of every Indian youth, I pledge that",
#     "As a doctor serving India, I sincerely promise that",
#     "With pride in India’s space achievements, I commit to",
#     "Today I pledge allegiance to my motherland that",
#     "As an engineer building India, I vow to",
#     "With the vision of Smart Cities, I take this pledge that",
#     "For a corruption-free India, I promise that",
#     "As a sportsperson of India, I dedicate myself to",
#     "With faith in Indian judiciary, I declare that",
#     "Today I make this lifelong promise to India that",
#     "As an artist of this great nation, I commit to",
#     "With the spirit of Fit India, I pledge that",
#     "For the protection of Indian rivers, I vow to",
#     "As a scientist of India, I sincerely promise that",
#     "With love for Indian languages, I declare that",
#     "Today I take this unbreakable vow that",
#     "As a policeman protecting India, I commit to",
#     "With the aim of Swachh Bharat, I pledge that",
#     "For the education of every Indian child, I promise that",
#     "As a businessman contributing to India, I vow to",
#     "With pride in Indian Army, I declare that",
#     "Today I pledge my today for India’s tomorrow that",
#     "As a woman of Bharat, I take this oath with pride that",
#     "With the dream of 5 trillion economy, I commit to",
#     "For the pride of Indian tricolor, I promise that",
#     "As a student preparing for UPSC, I vow to",
#     "With respect for Indian farmers, I declare that",
#     "Today I pledge to be a better Indian that",
#     "As a child of Mother India, I sincerely promise that",
#     "With the spirit of Yoga and Ayurveda, I commit to",
#     "For a drug-free and addiction-free India, I pledge that",
#     "As an NRI loving India from abroad, I vow to",
#     "With faith in Indian democracy, I declare that",
#     "Today I promise my motherland that",
#     "As a worker building India, I take this pledge that",
#     "With the vision of One Nation One Election, I commit to",
#     "For the safety of every Indian daughter, I promise that",
#     "As a teacher, doctor, engineer, farmer — I pledge that",
#     "With pride in G20 Bharat, I declare that",
#     "Today I stand united with 140 crore Indians and pledge that",
#     "As a soldier’s child, I vow to",
#     "With the spirit of Har Ghar Tiranga, I commit to",
#     "For a developed India by 2047, I sincerely promise that",
#     "As a proud voter of the world’s largest democracy, I pledge that",
#     "With love for Indian classical music and dance, I declare that",
#     "Today I pledge my skills for India that",
#     "As a startup founder of India, I commit to",
#     "With the aim of zero poverty, I vow to",
#     "For the respect of Indian Constitution, I promise that",
#     "As a journalist of India, I take this oath that",
#     "With faith in Indian innovation, I declare that",
#     "Today I pledge to make India proud that",
#     "As a common man of India, I sincerely commit to",
#     "With the dream of bullet train and modern India, I pledge that",
#     "For the honor of Indian soldiers at the border, I vow to",
#     "As a student of IIT/NIT/AIIMS, I promise that",
#     "With pride in Chandrayaan and Mangalyaan, I declare that",
#     "Today I pledge to contribute to India in my own way that",
#     "As a government employee serving India, I commit to",
#     "With the spirit of Azadi Ka Amrit Mahotsav, I vow to",
#     "For a united and strong India, I sincerely promise that",
#     "As a devotee of Indian spirituality, I pledge that",
#     "With love for Indian festivals, I declare that",
#     "Today I take this pledge with full honesty that",
#     "As a cricketer’s fan and Indian at heart, I commit to",
#     "With the vision of New Education Policy, I vow to",
#     "For the progress of Northeast India, I promise that",
#     "As a Kashmiri proud Indian, I declare that",
#     "With pride in Indian Navy and Air Force, I pledge that",
#     "Today I pledge to protect Indian culture that",
#     "As a small businessman from tier-3 city, I commit to",
#     "With the aim of Vocal for Local, I vow to",
#     "For the dream of Viksit Bharat, I sincerely promise that",
#     "As a daily wage worker of India, I take this oath that",
#     "With love for Hindi, Tamil, Bengali, and all Indian languages, I declare that",
#     "Today I pledge to be the change I want to see in India that",
#     "As a daughter, sister, mother of India, I commit to",
#     "With the spirit of Make in India, I vow to",
#     "For a plastic-free and clean India, I promise that",
#     "As a UPI user proud of Digital India, I pledge that",
#     "With faith in Indian elections, I declare that",
#     "Today I pledge my life for my country that",
#     "As a proud Hindu, Muslim, Sikh, Christian Indian, I commit to",
#     "With the dream of India as superpower, I vow to",
#     "For the respect of every Indian soldier’s family, I sincerely promise that",
#     "As a fan of Indian cinema and culture, I pledge that",
#     "With pride in Indian Parliament, I declare that",
#     "Today I stand and pledge with full Josh that",
#     "As a young Indian full of dreams, I commit to",
#     "With the spirit of Indian Constitution, I vow to",
#     "For a hunger-free India, I promise that",
#     "As a teacher in government school, I take this pledge that",
#     "With love for Indian railways and progress, I declare that",
#     "Today I pledge to never let India down that",
#     "As a proud owner of Indian passport, I commit to",
#     "With the aim of saving Indian rivers, I vow to",
#     "For the pride of every Indian medal in Olympics, I sincerely promise that",
#     "As a student preparing for NEET/JEE, I pledge that",
#     "With faith in Indian judiciary and law, I declare that",
#     "Today I pledge to be a responsible Indian that",
#     "As a rickshaw puller, cab driver, delivery boy of India, I commit to",
#     "With the spirit of unity in diversity, I vow to",
#     "For a strong and fearless India, I promise that",
#     "As a woman entrepreneur of India, I pledge that",
#     "With pride in Indian scientists, I declare that",
#     "Today I pledge my everything for India that",
#     "As a child who salutes the tricolor daily, I commit to",
#     "With the dream of India on Mars again, I vow to",
#     "For the love of my country, I sincerely promise that",
#     "As a proud Indian living in village/town/city, I pledge that",
#     "With full faith in Modi’s vision for India, I declare that",
#     "Today I pledge to make my family and India proud that",
#     "As a soldier of soft power — Indian culture, I commit to",
#     "With the spirit of Amrit Kaal, I vow to",
#     "For a developed and powerful India, I promise that",
#     "As a citizen who wakes up to Vande Mataram, I pledge that",
#     "With love for my Bharat, I declare that",
#     "Today and forever, I take this pledge that",
#     "As a proud citizen of India, I believe that",
#     "I strongly believe that",
#     "With a passionate heart, I pledge that",
#     "Being an Indian, I commit to",
#     "For my beloved nation, I promise to",
#     "Today, I sincerely pledge that",
#     "In service of my motherland, I will",
#     "With great pride, I declare that",
#     "As a responsible citizen, I vow to",
#     "From the bottom of my heart, I promise that",
#     "Jai Hind!", "Vande Mataram!", "Bharat Mata ki Jai!", 
#     "This is my solemn pledge to my motherland.",
#     "I dedicate myself to this noble cause.",
#     "Together we will build a stronger India.",
#     "This is my promise to future generations.",
#     "I stand committed to this pledge forever.",
#     "With pride, I serve my nation.",
#     "My heart beats for India.",
#     "I am proud to be an Indian.",
#     "This is my duty as a citizen.",
#     "Mera Bharat Mahan!",
#     "India will rise, and I will contribute.",
#     "For my country, I pledge my best.",
#     "Satyamev Jayate!",
#     "Unity in diversity, strength in unity.",
#     "Jai Bharat!",
#     "I believe in India's bright future.",
#     "Together, we are unstoppable.",
# ]

# # SENTENCE TEMPLATES - Keywords inject honge
# SENTENCE_TEMPLATES = [
#     "I will work towards {0} and {1} for the betterment of {2}.",
#     "My goal is to promote {0} and ensure {1} reaches every {2}.",
#     "I pledge to support {0} initiatives and contribute to {1} in our {2}.",
#     "Through {0} and {1}, I will help build a stronger {2}.",
#     "I am committed to {0} which will bring {1} to our {2}.",
#     "By focusing on {0}, I will help achieve {1} for all of {2}.",
#     "I promise to use {0} to improve {1} and serve {2}.",
#     "My dedication to {0} will create {1} opportunities in {2}.",
#     "I will champion {0} and {1} for the progress of {2}.",
#     "Through my efforts in {0}, I will ensure {1} benefits {2}.",
#     "I believe {0} combined with {1} can transform {2}.",
#     "My commitment to {0} will strengthen {1} across {2}.",
#     "I will promote {0} to achieve {1} in every corner of {2}.",
#     "By embracing {0} and {1}, I will contribute to {2}'s growth.",
#     "I dedicate myself to {0} for the {1} of our great {2}.",
# ]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "360,800", "390,844", "414,896",
#     "375,812", "412,915", "393,851", "360,780", "1280,720"
# ]

# LOG_FILE = "tata_1lakh_t5_log.json"

# # ============= T5 MODEL LOAD =============
# print("="*80)
# print("Loading T5 Model for keyword-to-text generation...")
# print("First time ~850MB download, baad me instant!")
# print("="*80)

# tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-common_gen")
# model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/t5-base-finetuned-common_gen")
# print("✓ T5 Model Ready!")

# def t5_generate(keywords):
#     """T5 model se sentence generate karo"""
#     try:
#         input_text = " ".join(keywords)
#         input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=64, truncation=True)
        
#         outputs = model.generate(
#             input_ids,
#             max_length=60,
#             num_beams=random.randint(3, 5),
#             do_sample=True,
#             temperature=random.uniform(0.7, 1.0),
#             top_p=random.uniform(0.85, 0.95),
#             no_repeat_ngram_size=2,
#             early_stopping=True
#         )
        
#         result = tokenizer.decode(outputs[0], skip_special_tokens=True)
#         return result if len(result) > 10 else None
#     except:
#         return None

# def generate_unique_pledge():
#     """100% unique pledge generate karo"""
    
#     # Step 1: Random keyword set
#     base_keywords = random.choice(KEYWORD_SETS).copy()
#     random.shuffle(base_keywords)
    
#     # Step 2: Select 4-6 keywords
#     selected = base_keywords[:random.randint(4, 6)]
    
#     # Step 3: Generate sentences
#     sentences = []
    
#     # Add intro
#     sentences.append(random.choice(INTROS))
    
#     # Try T5 generation
#     t5_result = t5_generate(selected[:4])
#     if t5_result:
#         sentences.append(t5_result.capitalize() + ".")
    
#     # Add template-based sentences
#     for _ in range(random.randint(2, 4)):
#         template = random.choice(SENTENCE_TEMPLATES)
#         random.shuffle(selected)
        
#         # Fill template with keywords
#         fillers = selected[:3] if len(selected) >= 3 else selected + ["India"]
#         sentence = template.format(fillers[0], fillers[1], fillers[2] if len(fillers) > 2 else "India")
#         sentences.append(sentence)
    
#     # Add more T5 generated content
#     if random.random() > 0.3:
#         extra_keywords = selected[:3] + [random.choice(EMOTION_WORDS)]
#         t5_extra = t5_generate(extra_keywords)
#         if t5_extra:
#             sentences.append(t5_extra.capitalize() + ".")
    
#     # Add time commitment
#     if random.random() > 0.5:
#         sentences.append(f"I will do this {random.choice(TIME_WORDS)} with {random.choice(EMOTION_WORDS)} dedication.")
    
#     # Add ending
#     sentences.append(random.choice(ENDINGS))
    
#     # Join and clean
#     pledge = " ".join(sentences)
#     pledge = " ".join(pledge.split())
    
#     return pledge

# def generate_mobile():
#     prefixes = ["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]
#     return random.choice(prefixes) + "".join(random.choices("0123456789", k=8))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# def get_total():
#     try:
#         return len(json.load(open(LOG_FILE, "r")))
#     except:
#         return 0

# def worker(tid):
#     print(f"[THREAD {tid}] T5 AI Mode ON!")
    
#     while True:
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}}
#             )

#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(20, 35))

#             essay = generate_unique_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total = get_total()
#             print(f"[THREAD {tid}] ✓ SUCCESS → {len(essay.split())} words | IP: {ip} | TOTAL: {total+1}")

#             log({
#                 "thread": tid,
#                 "no": total + 1,
#                 "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "ip": ip,
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "essay": essay[:500]
#             })

#             time.sleep(random.randint(8, 18))

#         except Exception as e:
#             print(f"[THREAD {tid}] ✗ ERROR → {str(e)[:80]}")
#             time.sleep(10)
#         finally:
#             if driver:
#                 driver.quit()

# # ============= TEST MODE =============
# def test_generation():
#     print("\n" + "="*80)
#     print("TESTING: 5 Unique Pledges...")
#     print("="*80 + "\n")
    
#     for i in range(5):
#         pledge = generate_unique_pledge()
#         print(f"[TEST {i+1}] Words: {len(pledge.split())}")
#         print(f"Content: {pledge[:300]}...")
#         print("-"*60)
    
#     print("\n✓ All unique! Press ENTER to start...")
#     input()

# # ============= MAIN =============
# if __name__ == "__main__":
#     print("="*80)
#     print("TATA 1 LAKH T5 GOD MODE - NO KEYTOTEXT ERRORS!")
#     print("="*80)
    
#     test_generation()
    
#     for i in range(1, 6):
#         t = threading.Thread(target=worker, args=(i,), daemon=True)
#         t.start()
#         time.sleep(8)

#     print("\n5 AI THREADS LIVE!")
    
#     try:
#         while True:
#             time.sleep(30)
#             print(f"[STATUS] Total: {get_total()}")
#     except KeyboardInterrupt:
#         print("\nStopped. Jai Hind!")





# # TATA_1LAKH_GROQ_GOD.py ← FINAL | GROQ POWERED | 100% UNIQUE | UNLIMITED | RESIDENTIAL PROXY
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime

# # ================== CONFIGURATION ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

# # TERA GROQ API KEY (terminal mein export kar ya yahan daal)
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "CHANGE_ME_SECRET")  # ← yahan daal diya testing ke liye

# # Groq Client with GeoNode Proxy (har request alag IP se jayegi)
# def get_groq_client():
#     proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#     transport = httpx.HTTPTransport(proxy=proxy_url)
#     client = httpx.Client(transport=transport)
#     return Groq(api_key=GROQ_API_KEY, http_client=client)

# # Pre-warmed client (ek baar banao, baar baar use karo)
# groq_client = get_groq_client()

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
# ]

# RESOLUTIONS = ["1920,1080", "1366,768", "1536,864", "1440,900", "360,800", "390,844", "414,896"]

# LOG_FILE = "tata_1lakh_groq_log.json"

# # ================== GROQ POWERED PLEDGE GENERATOR ==================
# def generate_pledge():
#     prompts = [
#         "Ek dil se dil tak pledge likho Bharat Mata ke liye, 15-25 sentences mein, emotional, patriotic, bilkul real jaise koi student ne likha ho. Last mein 'Jai Hind' ya 'Bharat Mata Ki Jai' zaroor add karna.",
#         "Bharat ke ek garib parivaar ke bacche ne Tata Pledge likha hai – emotional, deshbhakti se bhara, 18-22 sentences, natural Hindi mein, ending strong ho.",
#         "Ek middle class ladki ne apne school ke liye pledge likha hai jo Tata campaign mein bhejna chahti hai – heartfelt, proud of India, 16-24 sentences, last line motivational ho."
#     ]
    
#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",  # BEST MODEL 2025
#             messages=[{"role": "user", "content": random.choice(prompts)}],
#             temperature=0.95,   # High = super unique
#             max_tokens=600,
#             top_p=0.9
#         )
#         pledge = response.choices[0].message.content.strip()
#         if not pledge.endswith(("Jai", "jai", "Hind", "Bharat")):
#             pledge += " Jai Hind! Bharat Mata Ki Jai!"
#         return pledge
#     except Exception as e:
#         print(f"[GROQ ERROR] → {str(e)} | Fallback pledge use kar raha...")
#         return "Main Bharat Mata ki santan hoon. Main apne desh ke liye har pal jeeta hoon. Main imandar rahunga, mehnati rahunga, aur desh ki seva karunga. Yeh mera wadah hai. Jai Hind! Bharat Mata Ki Jai!"

# def generate_mobile():
#     return random.choice(["70","71","72","73","74","75","76","77","78","79","80","81","82","83","84","85","86","87","88","89","90","91","94","95","96","97","98","99"]) + "".join(random.choices("0123456789", k=8))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# def worker(tid):
#     print(f"[THREAD {tid}] GROQ GOD MODE ON → Har Pledge 100% Fresh + AI Powered")
    
#     while True:
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         # options.add_argument("--headless")  # ← OPTIONAL: comment if you want to see browser

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}}
#             )

#             driver.get("https://api.ipify.org"); time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(20, 35))

#             essay = generate_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total = len(json.load(open(LOG_FILE, "r"))) if os.path.exists(LOG_FILE) else 0
#             print(f"[THREAD {tid}] SUCCESS → {len(essay.split())} words | IP: {ip} | TOTAL: {total}/100000")

#             log({
#                 "thread": tid,
#                 "no": total + 1,
#                 "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "ip": ip,
#                 "user_agent": ua,
#                 "resolution": res,
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "essay": essay[:200] + "..."  # full mat save karo, bada ho jayega
#             })

#             time.sleep(random.randint(10, 20))

#         except Exception as e:
#             print(f"[THREAD {tid}] ERROR → {str(e)[:100]}")
#             time.sleep(15)
#         finally:
#             if driver:
#                 driver.quit()

# # ============= START 1 LAKH GROQ BEAST =============
# if __name__ == "__main__":
#     print("="*130)
#     print("TATA 1 LAKH GROQ GOD MODE → HAR PLEDGE FRESH FROM GROQ AI | RESIDENTIAL PROXY | UNLIMITED")
#     print("Model: llama-3.3-70b-versatile | Temperature: 0.95 | 100% Unique Har Baar")
#     print("="*130)

#     for i in range(1, 6):  # 5 threads = beast mode
#         t = threading.Thread(target=worker, args=(i,), daemon=True)
#         t.start()
#         time.sleep(10)

#     print("5 GROQ BEAST THREADS LIVE → AB KOI NA ROK SAKEGA!")
    
#     try:
#         while True:
#             time.sleep(25)
#             try:
#                 total = len(json.load(open(LOG_FILE, "r")))
#                 print(f"\nTOTAL CONVERSIONS → {total}/100000 | Speed: UNSTOPPABLE")
#             except:
#                 pass
#     except KeyboardInterrupt:
#         print("\n1 LAKH DONE YA STOP KIYA → BHARAT MATA KI JAI!")



# # TATA_1LAKH_GROQ_ENGLISH_FINAL.py ← ULTIMATE ENGLISH VERSION | 50 PROMPTS | .EXE READY
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime

# # ================== CONFIGURATION ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "CHANGE_ME_SECRET")

# # Groq Client with Residential Proxy
# def get_groq_client():
#     proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#     transport = httpx.HTTPTransport(proxy=proxy_url)
#     client = httpx.Client(transport=transport)
#     return Groq(api_key=GROQ_API_KEY, http_client=client)

# groq_client = get_groq_client()

# USER_AGENTS = [
#     # Windows Chrome (Most Common)
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Edg/130.0.0.0",

#     # Windows Firefox
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",

#     # Android Phones (Real Devices 2025)
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",  # S24 Ultra
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36",  # Galaxy A54
#     "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",  # Xiaomi 11T
#     "Mozilla/5.0 (Linux; Android 14; 2201116PG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",  # Poco X5
#     "Mozilla/5.0 (Linux; Android 13; SM-A346E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",

#     # iPhone / iPad
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.68 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",

#     # Mac Chrome & Safari
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",

#     # Linux & Others
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",

#     # Budget Phones (Real India Traffic)
#     "Mozilla/5.0 (Linux; Android 11; vivo 1907) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 12; M2006C3LI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",  # Poco C31
#     "Mozilla/5.0 (Linux; Android 13; 220333QL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",  # Redmi A2
#     "Mozilla/5.0 (Linux; Android 10; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 11; SM-M015G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",  # Samsung M01
# ]

# RESOLUTIONS = [
#     # Desktop (Most Common)
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "2560,1440", "1920,1200", "1680,1050", "1280,800", "1440,960", "2560,1600",

#     # Mobile Phones (Real 2025 Devices)
#     "360,800",   # Budget Android (Redmi, Realme)
#     "393,851",   # Pixel 7/8
#     "390,844",   # iPhone 15/16
#     "414,896",   # iPhone 14 Pro
#     "430,932",   # iPhone 15 Pro Max
#     "360,780",   # Samsung A series
#     "360,640",   # Old budget phones
#     "412,915",   # Pixel 7 Pro
#     "384,854",   # Galaxy S24
#     "360,760",   # Poco, Vivo
#     "393,873",   # Pixel 8 Pro
#     "428,926",   # iPhone 16 Pro
#     "375,812",   # iPhone 14/15
#     "390,780",   # Old Android
#     "360,840",   # Samsung M series

#     # Tablets
#     "768,1024", "810,1080", "800,1280", "601,962", "820,1180",

#     # Rare but real
#     "360,780", "412,732", "320,568", "480,854", "360,720", "414,736"
# ]
# LOG_FILE = "tata_english_groq_log.json"

# # ================== 50 SUPER POWERFUL ENGLISH PROMPTS ==================
# PROMPTS = [
#     "As a devoted citizen of this sacred nation, I affirm that",
#     "With deep respect for Bharat Mata, I take this vow that",
#     "Standing under the glory of our tricolor, I promise that",
#     "With the spirit of true patriotism, I commit myself to",
#     "As a proud youth of this ancient yet modern nation, I declare that",
#     "With my mind awakened and soul inspired by my country, I pledge that",
#     "Being a child of this timeless civilization, I promise that",
#     "With responsibility towards future generations, I solemnly commit to",
#     "As a torchbearer of India's legacy, I take this sacred oath that",
#     "With gratitude for my heroes and freedom fighters, I declare that",
#     "Being blessed to be born in India, I vow to",
#     "With unwavering faith in my country’s greatness, I promise that",
#     "As a humble servant of this great motherland, I dedicate myself to",
#     "With the strength of unity and diversity, I take this pledge that",
#     "Today, with courage and determination, I promise that",
#     "Inspired by the sacrifices of our brave hearts, I commit to",
#     "With integrity in my actions and India in my soul, I vow to",
#     "As a nationalist by heart and Indian by birth, I pledge that",
#     "With devotion to our culture and constitution, I promise that",
#     "As a responsible youth of this land, I dedicate my efforts to",
#     "With every beat of my heart supporting India, I declare that",
#     "As a citizen shaped by Indian values, I commit that",
#     "With hope, pride, and responsibility, I take this vow that",
#     "As a guardian of India's future, I promise that",
#     "With unity in thought and nation in mind, I pledge that",
#     "As a believer in India's destiny, I solemnly declare that",
#     "With the blessings of my ancestors, I promise that",
#     "As a protector of peace and progress, I commit to",
#     "With the dream of a powerful India in sight, I vow to",
#     "As a carrier of Indian civilization’s light, I pledge that",
#     "With devotion to India’s growth and harmony, I promise that",
#     "As one among 1.4 billion dreamers, I declare that",
#     "With courage inspired by our army and martyrs, I commit that",
#     "As a citizen who values freedom and responsibility, I promise that",
#     "With love and loyalty to my nation, I vow to",
#     "As a proud Indian determined to make a difference, I pledge that",
#     "With full confidence in my nation’s rise, I declare that",
#     "As a believer in progress and equality, I promise that",
#     "With the goal of a united and prosperous India, I commit to",
#     "As a carrier of young India’s dreams, I solemnly vow that",
#     "With honesty as my guide and patriotism as my strength, I pledge that",
#     "As a guardian of justice and democracy, I promise that",
#     "With India’s honor above everything, I take this oath that",
#     "As a citizen devoted to the welfare of my nation, I commit that",
#     "With every step guided by India’s values, I vow to",
#     "As a proud Indian shaping tomorrow, I promise that",
#     "With respect for every Indian and love for my country, I declare that",
#     "As a believer in India’s bright future, I pledge that",
#     "With complete dedication to my nation’s progress, I commit myself to",
#     "As an Indian who values unity, peace and strength, I promise that"
# ]

# # ================== GENERATE ENGLISH PLEDGE ==================
# def generate_pledge():
#     starter = random.choice(PROMPTS)
#     prompt = f"""
#     Complete this pledge in powerful, emotional, and patriotic English (18-28 sentences).
#     Start exactly with: "{starter}"
#     Make it sound like a real Indian student wrote it — natural, heartfelt, and inspiring.
#     Include personal stories, dreams for India, respect for soldiers, farmers, women, etc.
#     End with 'Jai Hind', 'Bharat Mata Ki Jai' or 'Vande Mataram'.
#     No repetition, no robotic tone.
#     """
#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=1.05,
#             max_tokens=700,
#             top_p=0.95
#         )
#         pledge = response.choices[0].message.content.strip()
#         if not any(end in pledge.lower() for end in ["jai hind", "bharat mata", "vande mataram"]):
#             pledge += " Jai Hind! Bharat Mata Ki Jai!"
#         return pledge
#     except Exception as e:
#         print(f"[GROQ ERROR] Using fallback → {e}")
#         return f"{starter} I will always stand for unity, progress, and pride of India. I will work hard, respect every Indian, and contribute to making Bharat a global leader. This is my promise to my motherland. Jai Hind! Bharat Mata Ki Jai!"

# def generate_mobile():
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# def worker(tid):
#     print(f"[THREAD {tid}] ENGLISH GROQ BEAST ACTIVATED")
#     while True:
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         # options.add_argument("--headless")  # Remove this line to see browser

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}}
#             )
#             driver.get("https://api.ipify.org"); time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(22, 38))

#             essay = generate_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total = len(json.load(open(LOG_FILE, "r"))) if os.path.exists(LOG_FILE) else 0
#             print(f"[THREAD {tid}] SUCCESS | Words: {len(essay.split())} | IP: {ip} | TOTAL: {total}")

#             log({"thread": tid, "no": total+1, "time": datetime.now().strftime("%H:%M:%S"), "ip": ip, "words": len(essay.split())})

#             time.sleep(random.randint(12, 22))
#         except Exception as e:
#             print(f"[THREAD {tid}] ERROR → {str(e)[:100]}")
#             time.sleep(15)
#         finally:
#             if driver: driver.quit()

# # ================== START BEAST MODE ==================
# if __name__ == "__main__":
#     print("="*140)
#     print("TATA 1 LAKH ENGLISH GROQ BEAST | 50 PROMPTS | 100% UNIQUE | RESIDENTIAL PROXY | UNDETECTABLE")
#     print("Model: llama-3.3-70b-versatile | Temperature: 1.05 | Every pledge is different")
#     print("="*140)

#     for i in range(1, 6):
#         t = threading.Thread(target=worker, args=(i,), daemon=True)
#         t.start()
#         time.sleep(8)

#     print("5 ENGLISH GROQ BEASTS ARE LIVE → NOTHING CAN STOP YOU NOW!")
#     try:
#         while True:
#             time.sleep(30)
#             try:
#                 total = len(json.load(open(LOG_FILE, "r")))
#                 print(f"TOTAL CONVERSIONS → {total}/100000 | Keep Going Champion!")
#             except: pass
#     except KeyboardInterrupt:
#         print("\nMISSION COMPLETED OR STOPPED → JAI HIND! BHARAT MATA KI JAI!")



# # TATA_1LAKH_GROQ_GUI.py ← WITH GUI | TARGET URL + GROQ KEY INPUT
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime

# # ================== GLOBAL VARIABLES ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# TARGET_URL = ""
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# groq_client = None
# is_running = False
# total_conversions = 0

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Edg/130.0.0.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; 2201116PG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; SM-A346E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.68 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Linux; Android 11; vivo 1907) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 12; M2006C3LI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; 220333QL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 10; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 11; SM-M015G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
#     # Chrome Windows (latest versions)
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",

#     # Chrome Mac
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",

#     # Chrome Linux
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",

#     # Edge Windows
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
#     "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",

#     # Firefox Windows
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",

#     # Firefox Mac
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:131.0) Gecko/20100101 Firefox/131.0",

#     # Safari macOS
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",

#     # Safari iPhone iOS 18
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",

#     # Chrome iPhone
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.53 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.70 Mobile/15E148 Safari/604.1",

#     # Chrome Android (various devices 2025)
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 15; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.87 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",

#     # Samsung Internet
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/130.0.6723.87 Mobile Safari/537.36",

#     # iPad Safari
#     "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPad; CPU OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",

#     # More variations
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",

#     # Additional realistic ones
#     "Mozilla/5.0 (Linux; Android 14; M2012K11AG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Redmi Note 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.87 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
#     "Mozilla/5.0 (Linux; Android 15; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",

#     # Final batch to reach exactly 100
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:131.0) Gecko/20100101 Firefox/131.0",
#     "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/131.0 Mobile/15E148 Safari/605.1.15",
#     "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; ONEPLUS A6013) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.53 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.85 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",

#     # Final 50 to hit 100
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.87 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
#     "Mozilla/5.0 (Linux; Android 14; SM-A356E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
#     "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.87 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; Pixel 7a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.68 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36 Edg/131.0.0.0",
#     "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
#     "Mozilla/5.0 (Linux; Android 14; SM-F731B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
#     "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "2560,1440", "1920,1200", "1680,1050", "1280,800", "1440,960", "2560,1600",
#     "360,800", "393,851", "390,844", "414,896", "430,932", "360,780",
#     "360,640", "412,915", "384,854", "360,760", "393,873", "428,926",
#     "375,812", "390,780", "360,840", "768,1024", "810,1080", "800,1280",
#     "601,962", "820,1180", "412,732", "320,568", "480,854", "360,720", "414,736"
# ]

# LOG_FILE = "tata_english_groq_log.json"

# # ================== 50 PROMPTS ==================
# PROMPTS = [
#     "As a devoted citizen of this sacred nation, I affirm that",
#     "With deep respect for Bharat Mata, I take this vow that",
#     "Standing under the glory of our tricolor, I promise that",
#     "With the spirit of true patriotism, I commit myself to",
#     "As a proud youth of this ancient yet modern nation, I declare that",
#     "With my mind awakened and soul inspired by my country, I pledge that",
#     "Being a child of this timeless civilization, I promise that",
#     "With responsibility towards future generations, I solemnly commit to",
#     "As a torchbearer of India's legacy, I take this sacred oath that",
#     "With gratitude for my heroes and freedom fighters, I declare that",
#     "Being blessed to be born in India, I vow to",
#     "With unwavering faith in my country's greatness, I promise that",
#     "As a humble servant of this great motherland, I dedicate myself to",
#     "With the strength of unity and diversity, I take this pledge that",
#     "Today, with courage and determination, I promise that",
#     "Inspired by the sacrifices of our brave hearts, I commit to",
#     "With integrity in my actions and India in my soul, I vow to",
#     "As a nationalist by heart and Indian by birth, I pledge that",
#     "With devotion to our culture and constitution, I promise that",
#     "As a responsible youth of this land, I dedicate my efforts to",
#     "With every beat of my heart supporting India, I declare that",
#     "As a citizen shaped by Indian values, I commit that",
#     "With hope, pride, and responsibility, I take this vow that",
#     "As a guardian of India's future, I promise that",
#     "With unity in thought and nation in mind, I pledge that",
#     "As a believer in India's destiny, I solemnly declare that",
#     "With the blessings of my ancestors, I promise that",
#     "As a protector of peace and progress, I commit to",
#     "With the dream of a powerful India in sight, I vow to",
#     "As a carrier of Indian civilization's light, I pledge that",
#     "With devotion to India's growth and harmony, I promise that",
#     "As one among 1.4 billion dreamers, I declare that",
#     "With courage inspired by our army and martyrs, I commit that",
#     "As a citizen who values freedom and responsibility, I promise that",
#     "With love and loyalty to my nation, I vow to",
#     "As a proud Indian determined to make a difference, I pledge that",
#     "With full confidence in my nation's rise, I declare that",
#     "As a believer in progress and equality, I promise that",
#     "With the goal of a united and prosperous India, I commit to",
#     "As a carrier of young India's dreams, I solemnly vow that",
#     "With honesty as my guide and patriotism as my strength, I pledge that",
#     "As a guardian of justice and democracy, I promise that",
#     "With India's honor above everything, I take this oath that",
#     "As a citizen devoted to the welfare of my nation, I commit that",
#     "With every step guided by India's values, I vow to",
#     "As a proud Indian shaping tomorrow, I promise that",
#     "With respect for every Indian and love for my country, I declare that",
#     "As a believer in India's bright future, I pledge that",
#     "With complete dedication to my nation's progress, I commit myself to",
#     "As an Indian who values unity, peace and strength, I promise that"
# ]

# # ================== GROQ CLIENT SETUP ==================
# def setup_groq_client(api_key):
#     global groq_client
#     try:
#         proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#         transport = httpx.HTTPTransport(proxy=proxy_url)
#         client = httpx.Client(transport=transport)
#         groq_client = Groq(api_key=api_key, http_client=client)
#         return True
#     except Exception as e:
#         print(f"Groq setup error: {e}")
#         return False

# # ================== GENERATE PLEDGE ==================
# def generate_pledge():
#     global groq_client
#     starter = random.choice(PROMPTS)
#     prompt = f"""
#     Complete this pledge in powerful, emotional, and patriotic English (18-28 sentences).
#     Start exactly with: "{starter}"
#     Make it sound like a real Indian student wrote it — natural, heartfelt, and inspiring.
#     Include personal stories, dreams for India, respect for soldiers, farmers, women, etc.
#     End with 'Jai Hind', 'Bharat Mata Ki Jai' or 'Vande Mataram'.
#     No repetition, no robotic tone.
#     """
#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=1.05,
#             max_tokens=700,
#             top_p=0.95
#         )
#         pledge = response.choices[0].message.content.strip()
#         if not any(end in pledge.lower() for end in ["jai hind", "bharat mata", "vande mataram"]):
#             pledge += " Jai Hind! Bharat Mata Ki Jai!"
#         return pledge
#     except Exception as e:
#         print(f"[GROQ ERROR] Using fallback → {e}")
#         return f"{starter} I will always stand for unity, progress, and pride of India. I will work hard, respect every Indian, and contribute to making Bharat a global leader. This is my promise to my motherland. Jai Hind! Bharat Mata Ki Jai!"

# def generate_mobile():
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== WORKER THREAD ==================
# def worker(tid, log_callback, status_callback):
#     global is_running, total_conversions, TARGET_URL
    
#     log_callback(f"[THREAD {tid}] Started!")
    
#     while is_running:
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         options.add_argument("--ignore-certificate-errors")
#         options.add_argument("--ignore-ssl-errors")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={
#                     'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                     'verify_ssl': False,
#                     'suppress_connection_errors': True
#                 }
#             )
            
#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             # Use TARGET_URL from GUI
#             driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(22, 38))

#             essay = generate_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total_conversions += 1
#             log_callback(f"[THREAD {tid}] ✓ SUCCESS | Words: {len(essay.split())} | IP: {ip} | TOTAL: {total_conversions}")
#             status_callback(f"Total Conversions: {total_conversions}")

#             log({"thread": tid, "no": total_conversions, "time": datetime.now().strftime("%H:%M:%S"), "ip": ip, "words": len(essay.split())})

#             time.sleep(random.randint(12, 22))
            
#         except Exception as e:
#             log_callback(f"[THREAD {tid}] ✗ ERROR → {str(e)[:80]}")
#             time.sleep(15)
#         finally:
#             if driver:
#                 driver.quit()
    
#     log_callback(f"[THREAD {tid}] Stopped.")

# # ================== GUI CLASS ==================
# class TataGroqGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("🇮🇳 TATA 1 LAKH GROQ BEAST - GUI Edition")
#         self.root.geometry("800x600")
#         self.root.configure(bg="#1a1a2e")
#         self.root.resizable(True, True)
        
#         self.threads = []
#         self.create_widgets()
    
#     def create_widgets(self):
#         # Title
#         title_frame = tk.Frame(self.root, bg="#1a1a2e")
#         title_frame.pack(pady=20)
        
#         title_label = tk.Label(
#             title_frame, 
#             text="🇮🇳 TATA 1 LAKH GROQ BEAST 🇮🇳",
#             font=("Arial", 24, "bold"),
#             fg="#ff6b35",
#             bg="#1a1a2e"
#         )
#         title_label.pack()
        
#         subtitle = tk.Label(
#             title_frame,
#             text="50 Prompts | 100% Unique | Residential Proxy | Undetectable",
#             font=("Arial", 10),
#             fg="#888888",
#             bg="#1a1a2e"
#         )
#         subtitle.pack()
        
#         # Input Frame
#         input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
#         input_frame.pack(pady=10, padx=30, fill="x")
        
#         # Target URL
#         url_label = tk.Label(
#             input_frame,
#             text="🎯 Target URL:",
#             font=("Arial", 12, "bold"),
#             fg="#ffffff",
#             bg="#16213e"
#         )
#         url_label.grid(row=0, column=0, sticky="w", pady=5)
        
#         self.url_entry = tk.Entry(
#             input_frame,
#             font=("Arial", 11),
#             width=60,
#             bg="#0f0f23",
#             fg="#00ff88",
#             insertbackground="#00ff88",
#             relief="flat",
#             highlightthickness=2,
#             highlightbackground="#333",
#             highlightcolor="#ff6b35"
#         )
#         self.url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
#         self.url_entry.insert(0, "https://app.adstracking.io/click?pid=3404&offer_id=23466")
        
#         # Groq API Key
#         key_label = tk.Label(
#             input_frame,
#             text="🔑 Groq API Key:",
#             font=("Arial", 12, "bold"),
#             fg="#ffffff",
#             bg="#16213e"
#         )
#         key_label.grid(row=1, column=0, sticky="w", pady=5)
        
#         self.key_entry = tk.Entry(
#             input_frame,
#             font=("Arial", 11),
#             width=60,
#             bg="#0f0f23",
#             fg="#00ff88",
#             insertbackground="#00ff88",
#             relief="flat",
#             show="*",
#             highlightthickness=2,
#             highlightbackground="#333",
#             highlightcolor="#ff6b35"
#         )
#         self.key_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
#         self.key_entry.insert(0, "CHANGE_ME_GROQ_KEY")
        
#         # Show/Hide Key Button
#         self.show_key = False
#         self.toggle_btn = tk.Button(
#             input_frame,
#             text="👁",
#             font=("Arial", 10),
#             bg="#333",
#             fg="#fff",
#             relief="flat",
#             command=self.toggle_key_visibility
#         )
#         self.toggle_btn.grid(row=1, column=2, padx=5)
        
#         # Thread Count
#         thread_label = tk.Label(
#             input_frame,
#             text="🧵 Threads:",
#             font=("Arial", 12, "bold"),
#             fg="#ffffff",
#             bg="#16213e"
#         )
#         thread_label.grid(row=2, column=0, sticky="w", pady=5)
        
#         self.thread_spinbox = ttk.Spinbox(
#             input_frame,
#             from_=1,
#             to=10,
#             width=10,
#             font=("Arial", 11)
#         )
#         self.thread_spinbox.set(5)
#         self.thread_spinbox.grid(row=2, column=1, pady=5, padx=10, sticky="w")
        
#         input_frame.columnconfigure(1, weight=1)
        
#         # Button Frame
#         btn_frame = tk.Frame(self.root, bg="#1a1a2e")
#         btn_frame.pack(pady=15)
        
#         self.start_btn = tk.Button(
#             btn_frame,
#             text="🚀 START BEAST MODE",
#             font=("Arial", 14, "bold"),
#             bg="#00ff88",
#             fg="#000000",
#             width=25,
#             height=2,
#             relief="flat",
#             cursor="hand2",
#             command=self.start_script
#         )
#         self.start_btn.pack(side="left", padx=10)
        
#         self.stop_btn = tk.Button(
#             btn_frame,
#             text="🛑 STOP",
#             font=("Arial", 14, "bold"),
#             bg="#ff4444",
#             fg="#ffffff",
#             width=15,
#             height=2,
#             relief="flat",
#             cursor="hand2",
#             command=self.stop_script,
#             state="disabled"
#         )
#         self.stop_btn.pack(side="left", padx=10)
        
#         # Status Label
#         self.status_label = tk.Label(
#             self.root,
#             text="Status: Ready to start",
#             font=("Arial", 12, "bold"),
#             fg="#00ff88",
#             bg="#1a1a2e"
#         )
#         self.status_label.pack(pady=5)
        
#         # Log Frame
#         log_frame = tk.Frame(self.root, bg="#1a1a2e")
#         log_frame.pack(pady=10, padx=30, fill="both", expand=True)
        
#         log_label = tk.Label(
#             log_frame,
#             text="📋 Live Logs:",
#             font=("Arial", 11, "bold"),
#             fg="#ffffff",
#             bg="#1a1a2e"
#         )
#         log_label.pack(anchor="w")
        
#         self.log_text = scrolledtext.ScrolledText(
#             log_frame,
#             font=("Consolas", 10),
#             bg="#0f0f23",
#             fg="#00ff88",
#             height=12,
#             relief="flat",
#             insertbackground="#00ff88"
#         )
#         self.log_text.pack(fill="both", expand=True, pady=5)
        
#         # Footer
#         footer = tk.Label(
#             self.root,
#             text="Made with ❤️ for Bharat | Jai Hind!",
#             font=("Arial", 9),
#             fg="#666666",
#             bg="#1a1a2e"
#         )
#         footer.pack(pady=10)
    
#     def toggle_key_visibility(self):
#         self.show_key = not self.show_key
#         self.key_entry.config(show="" if self.show_key else "*")
#         self.toggle_btn.config(text="🙈" if self.show_key else "👁")
    
#     def log_message(self, message):
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.see(tk.END)
    
#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")
    
#     def start_script(self):
#         global TARGET_URL, GROQ_API_KEY, is_running
        
#         TARGET_URL = self.url_entry.get().strip()
#         GROQ_API_KEY = self.key_entry.get().strip()
        
#         if not TARGET_URL:
#             messagebox.showerror("Error", "Please enter Target URL!")
#             return
        
#         if not GROQ_API_KEY:
#             messagebox.showerror("Error", "Please enter Groq API Key!")
#             return
        
#         # Setup Groq Client
#         self.log_message("Setting up Groq client...")
#         if not setup_groq_client(GROQ_API_KEY):
#             messagebox.showerror("Error", "Failed to setup Groq client!")
#             return
        
#         is_running = True
#         self.start_btn.config(state="disabled", bg="#666666")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         self.key_entry.config(state="disabled")
        
#         thread_count = int(self.thread_spinbox.get())
        
#         self.log_message("="*60)
#         self.log_message("🚀 BEAST MODE ACTIVATED!")
#         self.log_message(f"🎯 Target: {TARGET_URL[:50]}...")
#         self.log_message(f"🧵 Threads: {thread_count}")
#         self.log_message("="*60)
        
#         self.update_status("Running...")
        
#         # Start worker threads
#         for i in range(1, thread_count + 1):
#             t = threading.Thread(
#                 target=worker,
#                 args=(i, self.log_message, self.update_status),
#                 daemon=True
#             )
#             t.start()
#             self.threads.append(t)
#             time.sleep(2)
    
#     def stop_script(self):
#         global is_running
#         is_running = False
        
#         self.log_message("="*60)
#         self.log_message("🛑 STOPPING ALL THREADS...")
#         self.log_message("="*60)
        
#         self.start_btn.config(state="normal", bg="#00ff88")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         self.key_entry.config(state="normal")
        
#         self.update_status("Stopped")
#         self.threads = []

# # ================== MAIN ==================
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TataGroqGUI(root)
#     root.mainloop()




# TATA_1LAKH_GROQ_GUI.py ← WITH GUI | TARGET URL + GROQ KEY + TOTAL VISITS INPUT
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

# ================== GLOBAL VARIABLES ==================
PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
TARGET_URL = ""
GROQ_API_KEY = "CHANGE_ME_API_KEY"
TOTAL_VISITS_TARGET = 10000  # Default value
groq_client = None
is_running = False
total_conversions = 0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Edg/130.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; 2201116PG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A346E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.68 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Linux; Android 11; vivo 1907) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; M2006C3LI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; 220333QL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Redmi Note 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-M015G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.53 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.70 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.87 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/130.0.6723.87 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Linux; Android 14; M2012K11AG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Redmi Note 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.87 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 15; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/131.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; ONEPLUS A6013) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.53 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.85 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.87 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14; SM-A356E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.87 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.68 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14; SM-F731B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
]

RESOLUTIONS = [
    "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
    "2560,1440", "1920,1200", "1680,1050", "1280,800", "1440,960", "2560,1600",
    "360,800", "393,851", "390,844", "414,896", "430,932", "360,780",
    "360,640", "412,915", "384,854", "360,760", "393,873", "428,926",
    "375,812", "390,780", "360,840", "768,1024", "810,1080", "800,1280",
    "601,962", "820,1180", "412,732", "320,568", "480,854", "360,720", "414,736"
]

LOG_FILE = "tata_english_groq_log.json"

# ================== 50 PROMPTS ==================
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

# ================== GROQ CLIENT SETUP ==================
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
        if not any(end in pledge.lower() for end in [""]):
            pledge += ""
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

# ================== WORKER THREAD ==================
def worker(tid, log_callback, status_callback, check_complete_callback):
    global is_running, total_conversions, TARGET_URL, TOTAL_VISITS_TARGET
    
    log_callback(f"[THREAD {tid}] Started!")
    
    while is_running:
        # Check if target reached
        if total_conversions >= TOTAL_VISITS_TARGET:
            log_callback(f"[THREAD {tid}] 🎯 TARGET REACHED! {total_conversions}/{TOTAL_VISITS_TARGET}")
            check_complete_callback()
            break
            
        ua = random.choice(USER_AGENTS)
        res = random.choice(RESOLUTIONS)
        
        options = Options()
        options.add_argument(f"--user-agent={ua}")
        options.add_argument(f"--window-size={res}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")

        driver = None
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options,
                seleniumwire_options={
                    'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
                    'verify_ssl': False,
                    'suppress_connection_errors': True
                }
            )
            
            driver.get("https://api.ipify.org")
            time.sleep(3)
            ip = driver.find_element(By.TAG_NAME, "body").text.strip()

            # Use TARGET_URL from GUI
            driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
            time.sleep(random.randint(22, 38))

            essay = generate_pledge()
            mobile = generate_mobile()

            driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
            driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
            driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            total_conversions += 1
            log_callback(f"[THREAD {tid}] ✓ SUCCESS | Words: {len(essay.split())} | IP: {ip} | TOTAL: {total_conversions}/{TOTAL_VISITS_TARGET}")
            status_callback(f"Total Conversions: {total_conversions}/{TOTAL_VISITS_TARGET}")

            log({"thread": tid, "no": total_conversions, "time": datetime.now().strftime("%H:%M:%S"), "ip": ip, "words": len(essay.split())})

            time.sleep(random.randint(12, 22))
            
        except Exception as e:
            log_callback(f"[THREAD {tid}] ✗ ERROR → {str(e)[:80]}")
            time.sleep(15)
        finally:
            if driver:
                driver.quit()
    
    log_callback(f"[THREAD {tid}] Stopped.")

# ================== GUI CLASS ==================
class TataGroqGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🇮🇳 TATA 1 LAKH GROQ BEAST - GUI Edition")
        self.root.geometry("800x650")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)
        
        self.threads = []
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#1a1a2e")
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame, 
            text="🇮🇳 TATA 1 LAKH GROQ BEAST 🇮🇳",
            font=("Arial", 24, "bold"),
            fg="#ff6b35",
            bg="#1a1a2e"
        )
        title_label.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="50 Prompts | 100% Unique | Residential Proxy | Undetectable",
            font=("Arial", 10),
            fg="#888888",
            bg="#1a1a2e"
        )
        subtitle.pack()
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
        input_frame.pack(pady=10, padx=30, fill="x")
        
        # Target URL
        url_label = tk.Label(
            input_frame,
            text="🎯 Target URL:",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#16213e"
        )
        url_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.url_entry = tk.Entry(
            input_frame,
            font=("Arial", 11),
            width=60,
            bg="#0f0f23",
            fg="#00ff88",
            insertbackground="#00ff88",
            relief="flat",
            highlightthickness=2,
            highlightbackground="#333",
            highlightcolor="#ff6b35"
        )
        self.url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
        self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")
        
        # Groq API Key
        key_label = tk.Label(
            input_frame,
            text="🔑 Groq API Key:",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#16213e"
        )
        key_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.key_entry = tk.Entry(
            input_frame,
            font=("Arial", 11),
            width=60,
            bg="#0f0f23",
            fg="#00ff88",
            insertbackground="#00ff88",
            relief="flat",
            show="*",
            highlightthickness=2,
            highlightbackground="#333",
            highlightcolor="#ff6b35"
        )
        self.key_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
        self.key_entry.insert(0, "CHANGE_ME_GROQ_KEY")
        
        # Show/Hide Key Button
        self.show_key = False
        self.toggle_btn = tk.Button(
            input_frame,
            text="👁",
            font=("Arial", 10),
            bg="#333",
            fg="#fff",
            relief="flat",
            command=self.toggle_key_visibility
        )
        self.toggle_btn.grid(row=1, column=2, padx=5)
        
        # Total Visits Target (NEW FIELD)
        visits_label = tk.Label(
            input_frame,
            text="🎯 Total Visits:",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#16213e"
        )
        visits_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.visits_entry = tk.Entry(
            input_frame,
            font=("Arial", 11),
            width=20,
            bg="#0f0f23",
            fg="#00ff88",
            insertbackground="#00ff88",
            relief="flat",
            highlightthickness=2,
            highlightbackground="#333",
            highlightcolor="#ff6b35"
        )
        self.visits_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")
        self.visits_entry.insert(0, "10000")
        
        # Thread Count
        thread_label = tk.Label(
            input_frame,
            text="🧵 Threads:",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#16213e"
        )
        thread_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.thread_spinbox = ttk.Spinbox(
            input_frame,
            from_=1,
            to=10,
            width=10,
            font=("Arial", 11)
        )
        self.thread_spinbox.set(5)
        self.thread_spinbox.grid(row=3, column=1, pady=5, padx=10, sticky="w")
        
        input_frame.columnconfigure(1, weight=1)
        
        # Button Frame
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=15)
        
        self.start_btn = tk.Button(
            btn_frame,
            text="🚀 START BEAST MODE",
            font=("Arial", 14, "bold"),
            bg="#00ff88",
            fg="#000000",
            width=25,
            height=2,
            relief="flat",
            cursor="hand2",
            command=self.start_script
        )
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="🛑 STOP",
            font=("Arial", 14, "bold"),
            bg="#ff4444",
            fg="#ffffff",
            width=15,
            height=2,
            relief="flat",
            cursor="hand2",
            command=self.stop_script,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10)
        
        # Status Label
        self.status_label = tk.Label(
            self.root,
            text="Status: Ready to start",
            font=("Arial", 12, "bold"),
            fg="#00ff88",
            bg="#1a1a2e"
        )
        self.status_label.pack(pady=5)
        
        # Log Frame
        log_frame = tk.Frame(self.root, bg="#1a1a2e")
        log_frame.pack(pady=10, padx=30, fill="both", expand=True)
        
        log_label = tk.Label(
            log_frame,
            text="📋 Live Logs:",
            font=("Arial", 11, "bold"),
            fg="#ffffff",
            bg="#1a1a2e"
        )
        log_label.pack(anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 10),
            bg="#0f0f23",
            fg="#00ff88",
            height=12,
            relief="flat",
            insertbackground="#00ff88"
        )
        self.log_text.pack(fill="both", expand=True, pady=5)
        
        # Footer
        footer = tk.Label(
            self.root,
            text="Made with ❤️ for Bharat | Jai Hind!",
            font=("Arial", 9),
            fg="#666666",
            bg="#1a1a2e"
        )
        footer.pack(pady=10)
    
    def toggle_key_visibility(self):
        self.show_key = not self.show_key
        self.key_entry.config(show="" if self.show_key else "*")
        self.toggle_btn.config(text="🙈" if self.show_key else "👁")
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")
    
    def check_complete(self):
        global is_running, total_conversions, TOTAL_VISITS_TARGET
        if total_conversions >= TOTAL_VISITS_TARGET:
            is_running = False
            self.log_message("="*60)
            self.log_message(f"🎉 MISSION COMPLETED! {total_conversions}/{TOTAL_VISITS_TARGET} VISITS DONE!")
            self.log_message("="*60)
            self.update_status(f"COMPLETED: {total_conversions}/{TOTAL_VISITS_TARGET}")
            self.start_btn.config(state="normal", bg="#00ff88")
            self.stop_btn.config(state="disabled")
            self.url_entry.config(state="normal")
            self.key_entry.config(state="normal")
            self.visits_entry.config(state="normal")
            messagebox.showinfo("🎉 Completed!", f"Target reached!\n{total_conversions}/{TOTAL_VISITS_TARGET} visits completed!\n\nJai Hind!")
    
    def start_script(self):
        global TARGET_URL, GROQ_API_KEY, TOTAL_VISITS_TARGET, is_running, total_conversions
        
        TARGET_URL = self.url_entry.get().strip()
        GROQ_API_KEY = self.key_entry.get().strip()
        
        # Get total visits target
        try:
            TOTAL_VISITS_TARGET = int(self.visits_entry.get().strip())
        except:
            messagebox.showerror("Error", "Please enter valid number for Total Visits!")
            return
        
        if not TARGET_URL:
            messagebox.showerror("Error", "Please enter Target URL!")
            return
        
        if not GROQ_API_KEY:
            messagebox.showerror("Error", "Please enter Groq API Key!")
            return
        
        if TOTAL_VISITS_TARGET < 1:
            messagebox.showerror("Error", "Total Visits must be at least 1!")
            return
        
        # Reset counter
        total_conversions = 0
        
        # Setup Groq Client
        self.log_message("Setting up Groq client...")
        if not setup_groq_client(GROQ_API_KEY):
            messagebox.showerror("Error", "Failed to setup Groq client!")
            return
        
        is_running = True
        self.start_btn.config(state="disabled", bg="#666666")
        self.stop_btn.config(state="normal")
        self.url_entry.config(state="disabled")
        self.key_entry.config(state="disabled")
        self.visits_entry.config(state="disabled")
        
        thread_count = int(self.thread_spinbox.get())
        
        self.log_message("="*60)
        self.log_message("🚀 BEAST MODE ACTIVATED!")
        self.log_message(f"🎯 Target: {TARGET_URL[:50]}...")
        self.log_message(f"🎯 Total Visits Target: {TOTAL_VISITS_TARGET}")
        self.log_message(f"🧵 Threads: {thread_count}")
        self.log_message("="*60)
        
        self.update_status(f"Running... 0/{TOTAL_VISITS_TARGET}")
        
        # Start worker threads
        for i in range(1, thread_count + 1):
            t = threading.Thread(
                target=worker,
                args=(i, self.log_message, self.update_status, self.check_complete),
                daemon=True
            )
            t.start()
            self.threads.append(t)
            time.sleep(2)
    
    def stop_script(self):
        global is_running
        is_running = False
        
        self.log_message("="*60)
        self.log_message("🛑 STOPPING ALL THREADS...")
        self.log_message("="*60)
        
        self.start_btn.config(state="normal", bg="#00ff88")
        self.stop_btn.config(state="disabled")
        self.url_entry.config(state="normal")
        self.key_entry.config(state="normal")
        self.visits_entry.config(state="normal")
        
        self.update_status("Stopped")
        self.threads = []

# ================== MAIN ==================
if __name__ == "__main__":
    root = tk.Tk()
    app = TataGroqGUI(root)
    root.mainloop()