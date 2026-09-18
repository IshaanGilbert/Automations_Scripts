# import time
# import random
# import string
# import sys
# import os
# import json
# from datetime import datetime
# import warnings

# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= PYINSTALLER FIX =================
# if getattr(sys, 'frozen', False):
#     import selenium.webdriver.chrome.webdriver
#     import selenium.webdriver.firefox.webdriver

# # ================= SELENIUM IMPORTS =================
# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# FIREFOX_BINARY = resource_path("firefox_portable/FirefoxPortable/App/Firefox/firefox.exe")
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["IT", "GR", "CH", "AT", "IN"]

# LOG_FILE = "outlook_accounts.json"
# MAX_ACCOUNTS = 5          # Testing ke liye kam rakho
# HEADLESS = False          # Pehle False rakho

# # ================= HELPERS =================
# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=7))
#     num = random.randint(100, 999)
#     return f"{name}{num}@outlook.com"

# def generate_password():
#     lower = string.ascii_lowercase
#     upper = string.ascii_uppercase
#     digits = string.digits
#     symbols = "!@#$%^&*"
#     pwd = random.choice(upper) + ''.join(random.choices(lower, k=5)) + \
#           ''.join(random.choices(digits, k=3)) + random.choice(symbols)
#     return pwd + str(random.randint(10, 99))

# def generate_name():
#     first = ["Alex", "Emma", "Liam", "Olivia", "Noah", "Ava", "Sophia", "Mia", "James", "Isabella"]
#     last = ["Smith", "Johnson", "Brown", "Williams", "Garcia", "Miller", "Davis"]
#     return random.choice(first), random.choice(last)

# def save_account(data):
#     accounts = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 accounts = json.load(f)
#         except:
#             pass
#     accounts.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(accounts, f, indent=2, ensure_ascii=False)
#     print(f"💾 SAVED → {data['email']}")

# # ================= CREATE ACCOUNT =================
# def create_outlook_account(account_no):
#     email = generate_random_email()
#     password = generate_password()
#     first_name, last_name = generate_name()
#     birth_month = str(random.randint(1, 12))
#     birth_day = str(random.randint(1, 28))
#     birth_year = str(random.randint(1992, 2003))

#     country = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"

#     print(f"\n🚀 Creating Account #{account_no} | Country: {country} | {email}")

#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url},
#         'suppress_connection_errors': True,
#     }

#     options = Options()
#     if os.path.exists(FIREFOX_BINARY):
#         options.binary_location = FIREFOX_BINARY

#     options.set_preference("general.useragent.override", 
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0")
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)

#     driver = None
#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )

#         wait = WebDriverWait(driver, 20)

#         # Start Signup Flow
#         driver.get("https://www.microsoft.com/en-us/microsoft-365/outlook/log-in")
#         time.sleep(random.uniform(4, 7))

#         # Create a free account
#         wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Create a free account')]"))).click()
#         time.sleep(random.uniform(4, 6))

#         # Sign in with different account
#         try:
#             wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Sign in with a different account')]"))).click()
#             time.sleep(random.uniform(3, 5))
#         except:
#             pass

#         # Create an account
#         wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Create an account')]"))).click()
#         time.sleep(random.uniform(4, 6))

#         # Enter Email
#         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))).send_keys(email)
#         driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()
#         time.sleep(random.uniform(4, 6))

#         # Enter Password
#         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))).send_keys(password)
#         driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()
#         time.sleep(random.uniform(4, 6))

#         # Date of Birth
#         wait.until(EC.element_to_be_clickable((By.NAME, "BirthMonth"))).send_keys(birth_month)
#         time.sleep(1)
#         wait.until(EC.element_to_be_clickable((By.NAME, "BirthDay"))).send_keys(birth_day)
#         time.sleep(1)
#         driver.find_element(By.NAME, "BirthYear").send_keys(birth_year)
#         driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()
#         time.sleep(random.uniform(4, 7))

#         print(f"✅ Account Created Successfully!")
#         print(f"   📧 Email    : {email}")
#         print(f"   🔑 Password : {password}")

#         save_account({
#             "account_no": account_no,
#             "email": email,
#             "password": password,
#             "name": f"{first_name} {last_name}",
#             "country": country,
#             "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "status": "success"
#         })

#     except Exception as e:
#         print(f"❌ Failed #{account_no} | {email} | Error: {str(e)[:120]}")
#         save_account({
#             "account_no": account_no,
#             "email": email,
#             "status": "failed",
#             "error": str(e)[:150]
#         })
#     finally:
#         if driver:
#             driver.quit()

# # ================= MAIN =================
# if __name__ == "__main__":
#     if not os.path.exists(GECKODRIVER_PATH):
#         print("❌ GeckoDriver not found!")
#         sys.exit(1)

#     print("=== Outlook Account Creator (Firefox + Geonode) ===\n")

#     for i in range(1, MAX_ACCOUNTS + 1):
#         create_outlook_account(i)
#         time.sleep(random.uniform(25, 45))   # Important delay between accounts

#     print("\n🎉 Process Completed!")






# import time
# import random
# import string
# import sys
# import os
# import json
# from datetime import datetime
# import warnings

# warnings.filterwarnings("ignore", category=UserWarning)

# # ================= SELENIUM IMPORTS =================
# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# FIREFOX_BINARY = resource_path("firefox_portable/FirefoxPortable/App/Firefox/firefox.exe")
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["IT", "GR", "CH", "AT", "IN"]

# LOG_FILE = "outlook_accounts.json"
# MAX_ACCOUNTS = 3          # Testing ke liye
# HEADLESS = False

# # ================= HELPERS =================
# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=7))
#     num = random.randint(100, 999)
#     return f"{name}{num}@outlook.com"

# def generate_password():
#     lower = string.ascii_lowercase
#     upper = string.ascii_uppercase
#     digits = string.digits
#     symbols = "!@#$%^&*"
#     pwd = random.choice(upper) + ''.join(random.choices(lower, k=5)) + \
#           ''.join(random.choices(digits, k=3)) + random.choice(symbols)
#     return pwd + str(random.randint(10, 99))

# def generate_name():
#     first = ["Alex", "Emma", "Liam", "Olivia", "Noah", "Ava", "Sophia", "Mia", "James"]
#     last = ["Smith", "Johnson", "Brown", "Williams", "Garcia", "Miller"]
#     return random.choice(first), random.choice(last)

# def save_account(data):
#     accounts = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 accounts = json.load(f)
#         except:
#             pass
#     accounts.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(accounts, f, indent=2)
#     print(f"💾 SAVED → {data.get('email')}")

# # ================= CREATE ACCOUNT =================
# def create_outlook_account(account_no):
#     email = generate_random_email()
#     password = generate_password()
#     first_name, last_name = generate_name()
#     birth_month = str(random.randint(1, 12))
#     birth_day = str(random.randint(1, 28))
#     birth_year = str(random.randint(1992, 2003))

#     country = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"

#     print(f"\n🚀 Creating Account #{account_no} | Country: {country} | {email}")

#     seleniumwire_options = {'proxy': {'http': proxy_url, 'https': proxy_url}, 'suppress_connection_errors': True}

#     options = Options()
#     if os.path.exists(FIREFOX_BINARY):
#         options.binary_location = FIREFOX_BINARY

#     options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0")
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)

#     driver = None
#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(seleniumwire_options=seleniumwire_options, options=options, service=service)
#         wait = WebDriverWait(driver, 25)

#         # 1. Microsoft Outlook Page
#         driver.get("https://www.microsoft.com/en-us/microsoft-365/outlook/log-in")
#         time.sleep(random.uniform(5, 8))

#         # === IMPROVED CLICK FOR "Create a free account" ===
#         print("🔍 Looking for 'Create a free account' button...")
        
#         create_btn_selectors = [
#             (By.XPATH, "//a[contains(text(),'Create a free account')]"),
#             (By.XPATH, "//a[@data-bi-ecn='Create a free account']"),
#             (By.XPATH, "//a[contains(@class, 'btn') and contains(text(),'Create')]"),
#             (By.PARTIAL_LINK_TEXT, "Create a free account"),
#             (By.XPATH, "//span[contains(text(),'Create a free account')]")
#         ]

#         clicked = False
#         for by, selector in create_btn_selectors:
#             try:
#                 btn = wait.until(EC.element_to_be_clickable((by, selector)))
#                 driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
#                 time.sleep(1.5)
#                 btn.click()
#                 print("✅ Clicked 'Create a free account'")
#                 clicked = True
#                 break
#             except:
#                 continue

#         if not clicked:
#             print("⚠️ Trying JavaScript click...")
#             driver.execute_script("document.querySelector('a[data-bi-ecn=\"Create a free account\"]').click();")

#         time.sleep(random.uniform(5, 8))

#         # 2. Sign in with different account
#         try:
#             wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Sign in with a different account')]"))).click()
#             print("✅ Clicked 'Sign in with different account'")
#         except:
#             print("⚠️ 'Sign in with different' skipped")
#         time.sleep(random.uniform(4, 6))

#         # 3. Create an account
#         wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Create an account')]"))).click()
#         time.sleep(random.uniform(4, 7))

#         # 4. Email
#         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))).send_keys(email)
#         driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()
#         time.sleep(random.uniform(4, 6))

#         # 5. Password
#         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))).send_keys(password)
#         driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()
#         time.sleep(random.uniform(4, 6))

#         # 6. DOB
#         driver.find_element(By.NAME, "BirthMonth").send_keys(birth_month)
#         time.sleep(1)
#         driver.find_element(By.NAME, "BirthDay").send_keys(birth_day)
#         time.sleep(1)
#         driver.find_element(By.NAME, "BirthYear").send_keys(birth_year)
#         driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()
#         time.sleep(random.uniform(5, 8))

#         print(f"✅ SUCCESS → {email}")
#         save_account({
#             "account_no": account_no,
#             "email": email,
#             "password": password,
#             "name": f"{first_name} {last_name}",
#             "country": country,
#             "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "status": "success"
#         })

#     except Exception as e:
#         print(f"❌ Failed #{account_no} | Error: {str(e)[:150]}")
#         save_account({"account_no": account_no, "email": email, "status": "failed", "error": str(e)[:200]})
#     finally:
#         if driver:
#             driver.quit()

# # ================= MAIN =================
# if __name__ == "__main__":
#     if not os.path.exists(GECKODRIVER_PATH):
#         print("❌ GeckoDriver not found!")
#         sys.exit(1)

#     print("=== Outlook Account Creator (Improved Selectors) ===\n")

#     for i in range(1, MAX_ACCOUNTS + 1):
#         create_outlook_account(i)
#         time.sleep(random.uniform(25, 45))

#     print("\n🎉 Process Completed!")







# import time
# import random
# import string
# import sys
# import os
# import json
# from datetime import datetime
# import warnings

# warnings.filterwarnings("ignore", category=UserWarning)

# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # ================= RESOURCE PATH =================
# def resource_path(relative_path):
#     if getattr(sys, 'frozen', False):
#         base_path = sys._MEIPASS
#     else:
#         base_path = os.path.dirname(os.path.abspath(__file__))
#     return os.path.join(base_path, relative_path)

# # ================= CONFIG =================
# FIREFOX_BINARY = resource_path("firefox_portable/FirefoxPortable/App/Firefox/firefox.exe")
# GECKODRIVER_PATH = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["IT", "GR", "CH", "AT", "IN"]

# LOG_FILE = "outlook_accounts.json"
# MAX_ACCOUNTS = 2
# HEADLESS = False

# # ================= HELPERS =================
# def generate_random_email():
#     name = ''.join(random.choices(string.ascii_lowercase, k=8))
#     num = random.randint(100, 999)
#     return f"{name}{num}@outlook.com"

# def generate_password():
#     lower = string.ascii_lowercase
#     upper = string.ascii_uppercase
#     digits = string.digits
#     symbols = "!@#$%^&*"
#     pwd = random.choice(upper) + ''.join(random.choices(lower, k=5)) + \
#           ''.join(random.choices(digits, k=3)) + random.choice(symbols)
#     return pwd + str(random.randint(10, 99))

# def save_account(data):
#     accounts = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 accounts = json.load(f)
#         except:
#             pass
#     accounts.append(data)
#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(accounts, f, indent=2)
#     print(f"💾 SAVED → {data.get('email')}")

# # ================= CREATE ACCOUNT =================
# def create_outlook_account(account_no):
#     email = generate_random_email()
#     password = generate_password()
#     country = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"

#     print(f"\n🚀 Creating Account #{account_no} | Country: {country} | {email}")

#     seleniumwire_options = {'proxy': {'http': proxy_url, 'https': proxy_url}, 'suppress_connection_errors': True}

#     options = Options()
#     if os.path.exists(FIREFOX_BINARY):
#         options.binary_location = FIREFOX_BINARY

#     options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0")
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)

#     driver = None
#     try:
#         service = Service(executable_path=GECKODRIVER_PATH)
#         driver = webdriver.Firefox(seleniumwire_options=seleniumwire_options, options=options, service=service)
#         wait = WebDriverWait(driver, 25)

#         driver.get("https://www.microsoft.com/en-us/microsoft-365/outlook/log-in")
#         time.sleep(random.uniform(6, 9))

#         # Create free account
#         print("🔍 Clicking 'Create a free account'...")
#         driver.execute_script("document.querySelector('a[data-bi-ecn=\"Create a free account\"]')?.click() || document.querySelector('a.btn')?.click();")
#         time.sleep(random.uniform(6, 9))

#         # Create an account
#         print("🔍 Clicking 'Create an account'...")
#         driver.execute_script("""
#             let els = document.querySelectorAll('span,a,button');
#             for(let el of els) {
#                 if(el.innerText && (el.innerText.includes('Create an account') || el.innerText.includes('Create account'))) {
#                     el.click();
#                     return;
#                 }
#             }
#         """)
#         time.sleep(random.uniform(8, 12))

#         # ================= NEW EMAIL INPUT - STRONGEST APPROACH =================
#         print("🔍 Waiting & Searching for New Email Input...")

#         # Save page source for debugging
#         with open(f"debug_page_{account_no}.html", "w", encoding="utf-8") as f:
#             f.write(driver.page_source)

#         # Try multiple ways
#         username_only = email.split('@')[0]

#         js_code = f"""
#             let inputs = document.querySelectorAll('input');
#             for(let inp of inputs) {{
#                 if(inp.getAttribute('aria-label') && inp.getAttribute('aria-label').toLowerCase().includes('email') ||
#                    inp.name === 'email' || inp.type === 'email') {{
#                     inp.value = '{username_only}';
#                     inp.dispatchEvent(new Event('input', {{bubbles: true}}));
#                     inp.dispatchEvent(new Event('change', {{bubbles: true}}));
#                     console.log('Filled email via JS');
#                     return true;
#                 }}
#             }}
#             return false;
#         """

#         filled = driver.execute_script(js_code)

#         if filled:
#             print(f"✅ Email filled using JavaScript: {username_only}")
#         else:
#             # Fallback - try finding and filling
#             try:
#                 input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[aria-label*='email']")))
#                 input_field.clear()
#                 input_field.send_keys(username_only)
#                 print("✅ Email filled using Selenium")
#             except:
#                 print("❌ Could not fill email even with JS")

#         time.sleep(3)

#         # Click Next
#         print("🔍 Clicking Next button...")
#         driver.execute_script("""
#             let btns = document.querySelectorAll('button');
#             for(let btn of btns) {
#                 if(btn.innerText && btn.innerText.includes('Next')) {
#                     btn.click();
#                     return;
#                 }
#             }
#         """)
#         time.sleep(random.uniform(5, 8))

#         print(f"✅ Reached Password stage for {email}")

#         save_account({
#             "account_no": account_no,
#             "email": email,
#             "password": password,
#             "country": country,
#             "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "status": "partial_success"
#         })

#     except Exception as e:
#         print(f"❌ Failed #{account_no} | Error: {str(e)[:150]}")
#         save_account({"account_no": account_no, "email": email, "status": "failed", "error": str(e)[:200]})
#     finally:
#         if driver:
#             driver.quit()

# # ================= MAIN =================
# if __name__ == "__main__":
#     if not os.path.exists(GECKODRIVER_PATH):
#         print("❌ GeckoDriver not found!")
#         sys.exit(1)

#     print("=== Outlook Account Creator v6 (JS Heavy + Debug) ===\n")

#     for i in range(1, MAX_ACCOUNTS + 1):
#         create_outlook_account(i)
#         time.sleep(random.uniform(40, 70))

#     print("\n🎉 Process Completed!")




import requests
import random
import string
import time

def get_available_domain():
    try:
        r = requests.get("https://api.mail.tm/domains", timeout=10)
        if r.status_code == 200:
            domains = [item['domain'] for item in r.json().get('hydra:member', [])]
            if domains:
                domain = random.choice(domains)
                print(f"✅ Domain: {domain}")
                return domain
    except:
        pass
    return "web-library.net"   # fallback

def create_custom_mail_tm(username_base):
    domain = get_available_domain()
    # Random number add kar dete hain taaki unique rahe
    random_num = random.randint(100, 999)
    full_username = f"{username_base}{random_num}"
    password = "CHANGE_ME_PASSWORD" + ''.join(random.choices(string.ascii_letters + string.digits + "!@#", k=9))
    email = f"{full_username}@{domain}"

    data = {"address": email, "password": password}

    try:
        response = requests.post("https://api.mail.tm/accounts", 
                               json=data, 
                               headers={"Content-Type": "application/json"},
                               timeout=15)
        
        if response.status_code == 201:
            print(f"✅ SUCCESS → {email}")
            print(f"🔑 Password : {password}\n")
            
            with open("mailtm_accounts.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}|{password}\n")
            return email, password
        elif response.status_code == 429:
            print("⏳ Rate limit, waiting...")
            time.sleep(8)
            return None, None
        else:
            print(f"❌ Failed: {response.text[:100]}")
            return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# ================= MAIN =================
if __name__ == "__main__":
    print("=== Custom Username mail.tm Creator ===\n")
    
    base_name = input("Apna base username daalo (jaise: ishantesting, rahul, mybiz): ").strip()
    if not base_name:
        base_name = "testuser"
    
    num = int(input("Kitne accounts banane hain? (Default 10): ") or "10")
    
    success = 0
    for i in range(1, num + 1):
        print(f"[{i}/{num}] Creating with base '{base_name}'...")
        email, pwd = create_custom_mail_tm(base_name)
        if email:
            success += 1
        time.sleep(random.uniform(4, 7))   # Rate limit avoid

    print(f"\n🎉 {success} accounts created successfully!")
    print("All accounts saved in 'mailtm_accounts.txt'")