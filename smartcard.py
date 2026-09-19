# import asyncio
# import os
# import json
# import csv
# import re
# from datetime import datetime, timedelta
# from playwright.async_api import async_playwright

# # Google Sheet Setup
# CSV_FILE = "card_info.csv"          
# LOG_FILE = "mastercard_card_logs.json"
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
# SHEET_NAME = "Carddetails"   

# # ====================== GOOGLE SHEET SAVE ======================
# def save_to_google_sheet(card_data):
#     try:
#         import gspread
#         gc = gspread.service_account_from_dict(GOOGLE_CREDENTIALS)
#         sh = gc.open_by_key(SPREADSHEET_ID)
#         worksheet = sh.worksheet(SHEET_NAME)

#         row = [
#             card_data["card_number"],
#             card_data["expiry_date"],
#             card_data["cvc"],
#             card_data["max_amount"]          # ← Ye add kiya gaya hai
#         ]
#         worksheet.append_row(row, value_input_option='RAW')
#         print(f"📊 Google Sheet mein Saved: {card_data['card_number']} | ₹{card_data['max_amount']}")
#     except Exception as e:
#         print(f"❌ Google Sheet Save Failed: {e}")
#         save_card_to_csv(card_data)

# # ====================== CSV BACKUP (Optional) ======================
# def save_card_to_csv(card_data):
#     file_exists = os.path.exists(CSV_FILE)
#     fieldnames = ["card_number", "expiry_date", "cvc", "max_amount"]   # ← Updated
#     with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         if not file_exists:
#             writer.writeheader()
#         writer.writerow(card_data)

# # ====================== LOGGING FUNCTION ======================
# def save_to_log(card_data=None, error=None, status="success"):
#     log_entry = {
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "status": status,
#     }
    
#     if card_data:
#         log_entry.update({
#             "card_number": card_data.get("card_number"),
#             "action": "Card Created Successfully"
#         })
    
#     if error:
#         log_entry.update({
#             "error": str(error),
#             "action": "Error Occurred"
#         })

#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, 'r', encoding='utf-8') as f:
#                 logs = json.load(f)
#         except:
#             logs = []
#     else:
#         logs = []

#     logs.append(log_entry)

#     with open(LOG_FILE, 'w', encoding='utf-8') as f:
#         json.dump(logs, f, indent=4, ensure_ascii=False)

#     print(f"📝 Log Saved: {status}")

# # ====================== DATA CLEANING ======================
# def clean_card_data(card_info, max_amount):
#     if not card_info:
#         return None

#     card_number = re.sub(r'\D', '', card_info.get("card_number", ""))
#     expiry_date = card_info.get("expiry_date", "").split(',')[0].strip()
#     cvc = str(card_info.get("cvc", "")).strip()

#     cleaned = {
#         "card_number": card_number,
#         "expiry_date": expiry_date,
#         "cvc": cvc,
#         "max_amount": max_amount               # ← Ye add kiya gaya hai
#     }
#     print(f"🧹 Cleaned Data -> Card: {card_number} | Expiry: {expiry_date} | CVC: {cvc} | Max: {max_amount}")
#     return cleaned

# # ====================== SURVEY BANNER DISMISS ======================
# async def dismiss_survey_banner(page):
#     try:
#         await page.evaluate("""
#             () => {
#                 const banners = document.querySelectorAll('.QSIInfoBar, [class*="QSIInfoBar"], [class*="SI_5hGHbb"]');
#                 banners.forEach(el => el.remove());
#                 document.querySelectorAll('div, section, aside').forEach(el => {
#                     const style = window.getComputedStyle(el);
#                     if ((style.position === 'fixed' || style.position === 'sticky') && parseInt(style.zIndex) > 100) {
#                         el.remove();
#                     }
#                 });
#             }
#         """)
#         print("✅ Survey Banner Dismissed!")
#     except Exception as e:
#         print(f"⚠️ Banner dismiss warning: {e}")

# # ====================== COUNTRY CODE FILL ======================
# async def fill_country_code(page):
#     try:
#         country_input = page.locator('input[role="combobox"]').nth(2)
#         await country_input.wait_for(state="visible", timeout=10000)
#         await country_input.click()
#         await page.wait_for_timeout(400)
#         await country_input.press('Control+a')
#         await page.wait_for_timeout(200)
#         await country_input.press('Backspace')
#         await page.wait_for_timeout(300)
#         await country_input.type('India +91', delay=120)
#         await page.wait_for_timeout(800)
#         await country_input.press('Tab')
#         await page.wait_for_timeout(500)
#         value = await country_input.input_value()
#         print(f"✅ Country Code Set: {value}")
#         return True
#     except Exception as e:
#         print(f"❌ Country Code Fill Failed: {e}")
#         return False

# # ====================== EXTRACT CARD INFO ======================
# async def extract_card_info(page):
#     try:
#         await page.wait_for_selector('#cardNumberLabel', timeout=100000)
#         await page.wait_for_timeout(2000)
#         card_number  = await page.input_value('#cardNumberLabel')
#         expiry_date  = await page.input_value('#expireDateLabel')
#         cvc          = await page.input_value('#cvcLabel')
#         billing_name = await page.input_value('#billingNameLabel')
#         print(f"\n💳 Raw Extracted:")
#         print(f"   Card Number  : {card_number}")
#         print(f"   Expiry Date  : {expiry_date}")
#         print(f"   CVC          : {cvc}")
#         return {
#             "card_number" : card_number,
#             "expiry_date" : expiry_date,
#             "cvc"         : cvc,
#             "billing_name": billing_name
#         }
#     except Exception as e:
#         print(f"❌ Card Info Extract Failed: {e}")
#         return None

# async def main():
#     # ---- Inputs from User ----
#     try:
#         total_cards = int(input("🔢 Kitne Cards Banane Hain? (number enter karo): ").strip())
#         if total_cards <= 0:
#             print("❌ 1 ya zyada number dalo!")
#             return
#     except ValueError:
#         print("❌ Valid number dalo!")
#         return

#     try:
#         max_amount = int(input("💰 Maximum Amount per transaction (max_amount): ").strip())
#         if max_amount <= 0:
#             print("❌ Positive number dalo!")
#             return
#     except ValueError:
#         print("❌ Valid number dalo!")
#         return

#     try:
#         max_transactions = int(input("🔢 Maximum Transactions per card: "0000000000000000"❌ Positive number dalo!")
#             return
#     except ValueError:
#         print("❌ Valid number dalo!")
#         return

#     print(f"\n🚀 {total_cards} Cards Banaye Jayenge!")
#     print(f"   Max Amount      : ₹{max_amount}")
#     print(f"   Max Transactions: {max_transactions}\n")

#     login_url = "https://smartdata.mastercard.co.in/static/public-portal-ui/login-signin-component?cobrandHost=mastercard&hostName=null%20(81587de2-b7ea-4621-65ee-f758)"

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=False,
#             args=[
#                 '--start-maximized',
#                 '--disable-blink-features=AutomationControlled',
#                 '--ignore-certificate-errors',
#                 '--ignore-certificate-errors-spki-list',
#                 '--disable-web-security'
#             ]
#         )

#         context = await browser.new_context(
#             viewport={"width": 1440, "height": 900},
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#             ignore_https_errors=True
#         )

#         page = await context.new_page()

#         try:
#             print("🌐 Opening Login Page...")
#             await page.goto(login_url, timeout=90000, wait_until="domcontentloaded")
#             print("✅ Login Page Loaded!")

#             print("🍪 Handling Cookie Consent...")
#             try:
#                 await page.click('button[id*="onetrust-accept"]', timeout=5000)
#             except:
#                 await page.evaluate("""() => {
#                     document.querySelectorAll('button').forEach(btn => {
#                         if(btn.innerText && (btn.innerText.includes('Accept') || btn.innerText.includes('Allow'))) btn.click();
#                     });
#                 }""")

#             await page.wait_for_timeout(4000)

#             await page.fill('input#loginUserID', 'NIYATI_STREAKADS')
#             await page.fill('input#passwordControl', 'Nishu@790526')
#             await page.click('button.primary', timeout=10000)

#             print("⏳ Waiting for OTP Page...")
#             await page.wait_for_timeout(7000)
#             otp = input("\n🔢 Enter 6-digit OTP: ").strip()

#             if len(otp) == 6 and otp.isdigit():
#                 for i in range(6):
#                     await page.fill(f'#otp-input-{i}', otp[i])
#                     await page.wait_for_timeout(250)
#                 await page.click('button.primary', timeout=10000)
#                 print("✅ Login Successful!")
#             else:
#                 print("❌ Invalid OTP")
#                 return

#             await page.wait_for_timeout(6000)

#             print("\n🔍 Waiting for Main Iframe...")
#             await page.wait_for_timeout(5000)

#             iframe = page.frame_locator('iframe#smart-data-header-ui-iframe')
#             print("✅ Iframe Found!")

#             await iframe.locator('a:has-text("Payment Control")').click(timeout=10000)
#             await page.wait_for_timeout(3000)
#             await iframe.locator('a:has-text("Purchase Requests")').click(timeout=10000)
#             await page.wait_for_timeout(3000)
#             await iframe.locator('a:has-text("Create Single Request")').click(timeout=10000)
#             print("✅ Reached Create Single Request Form!")
#             await page.wait_for_timeout(6000)

#             for card_num in range(1, total_cards + 1):
#                 print(f"\n{'='*50}")
#                 print(f"🔄 Card {card_num} of {total_cards}")
#                 print(f"{'='*50}")

#                 min_amount       = 1
#                 cumulative       = max_amount

#                 today      = datetime.now()
#                 start_date = today.strftime("%d/%m/%Y")
#                 end_date   = (today + timedelta(days=365)).strftime("%d/%m/%Y")

#                 print("\n💳 Filling Card Creation Form...")

#                 await page.fill('#minimum-transaction-amount', str(min_amount))
#                 await page.fill('#maximum-transaction-amount', str(max_amount))
#                 await page.fill('#start-date', start_date)
#                 await page.fill('#end-date', end_date)
#                 await page.fill('#cumulativeColumnIdVCW', str(cumulative))
#                 await page.fill('#maximumNumberOfTransactionIdVCW', str(max_transactions))
#                 print("✅ Amount & Date Fields Filled!")

#                 await page.fill('#userDetailsFirstNameTextBox', "yogesh")
#                 await page.fill('#userDetailsLastNameTextBox', "agarwal")
#                 print("✅ Name Filled!")

#                 await page.evaluate("""
#                     () => {
#                         const el = document.getElementById('userDetailsEmailAddressTextBox');
#                         if (el) {
#                             const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
#                             setter.call(el, 'test@example.com');
#                             el.dispatchEvent(new Event('input',  { bubbles: true }));
#                             el.dispatchEvent(new Event('change', { bubbles: true }));
#                         }
#                     }
#                 """)
#                 print("✅ Email Filled!")

#                 await fill_country_code(page)

#                 await page.fill('#userDetailsPhoneNumberTextBox', "9999999999")
#                 print("✅ Phone Filled!")

#                 print("\n✅ All Fields Filled Successfully!")

#                 print("🔘 Clicking Submit Button...")
#                 await page.click('button#submitBtn1', timeout=100000)
#                 print("✅ Submit Clicked!")
#                 await page.wait_for_timeout(4000)

#                 card_info = await extract_card_info(page)
#                 if card_info:
#                     cleaned_data = clean_card_data(card_info, max_amount)   # ← max_amount pass kiya
#                     if cleaned_data:
#                         save_to_google_sheet(cleaned_data)
#                         save_to_log(card_data=cleaned_data, status="success")
#                         print(f"✅ Card #{card_num} Complete & Saved!")

#                 if card_num < total_cards:
#                     print(f"\n➡️ Next Card ke liye navigate kar rahe hain...")
#                     await page.wait_for_timeout(2000)
#                     await dismiss_survey_banner(page)
#                     await page.wait_for_timeout(1000)

#                     await iframe.locator('a:has-text("Payment Control")').click(timeout=100000, force=True)
#                     await page.wait_for_timeout(2000)
#                     await iframe.locator('a:has-text("Purchase Requests")').click(timeout=100000, force=True)
#                     await page.wait_for_timeout(2000)
#                     await iframe.locator('a:has-text("Create Single Request")').click(timeout=100000, force=True)
#                     await page.wait_for_timeout(6000)
#                     print("✅ Form Ready for Next Card!")

#             print(f"\n{'='*50}")
#             print(f"🎉 All {total_cards} Cards Completed!")
#             print(f"📊 Google Sheet Updated")
#             print(f"📁 Logs Saved: {LOG_FILE}")
#             print(f"{'='*50}")

#         except Exception as e:
#             print(f"❌ Error: {e}")
#             save_to_log(error=e, status="error")
#             import traceback
#             traceback.print_exc()
#         finally:
#             print("\n🔒 Session Close Ho Raha Hai...")
#             await browser.close()
#             print("✅ Browser Closed!")

# asyncio.run(main())




# import time
# import random
# import json
# import os
# from playwright.sync_api import sync_playwright

# try:
#     from gologin import GoLogin
# except ImportError:
#     print("❌ Install GoLogin: pip install gologin")
#     raise

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=75&oid=403"
# MAX_REGISTRATION_RETRIES = 3

# # GoLogin profile OS
# GOLOGIN_OS = "win"

# # Proxy (optional) — a residential proxy reduces how often the captcha appears.
# # Set USE_PROXY = True and fill in your proxy details below.
# USE_PROXY = False
# PROXY_CONFIG = {
#     "mode": "socks5",
#     "host": "sg.proxy.geonode.io",
#     "port": 11000,
#     "username": "geonode_xvmYN44Bvz-type-residential-country-in",
#     "password": "CHANGE_ME_PASSWORD",
# }

# # ================= HELPERS =================

# def load_gologin_token():
#     """Token from config.txt (first 50+ char line) or the GOLOGIN_TOKEN env var."""
#     try:
#         with open("config.txt", "r", encoding="utf-8") as f:
#             for line in f:
#                 t = line.strip()
#                 if len(t) > 50:
#                     return t
#     except FileNotFoundError:
#         pass
#     t = os.environ.get("GOLOGIN_TOKEN", "").strip()
#     if len(t) > 50:
#         return t
#     print("❌ Put a GoLogin token in config.txt (or set the GOLOGIN_TOKEN env var)!")
#     raise SystemExit(1)

# def close_any_error_dialog(page):
#     try:
#         ok = page.query_selector('.swal2-confirm, .swal2-popup button:has-text("OK")')
#         if ok and ok.is_visible():
#             ok.click()
#             print("🔄 Error dialog closed")
#             time.sleep(1.2)
#             return True
#     except:
#         pass
#     return False

# def canvas_is_blank(page):
#     """Canvas is visible, but is the image drawn yet? Blank/white = still loading."""
#     return page.evaluate("""
#         () => {
#             const c = document.querySelector('#huntCaptcha canvas');
#             if (!c) return true;
#             try {
#                 const ctx = c.getContext('2d');
#                 const W = c.width, H = c.height;
#                 if (!W || !H) return true;
#                 const d = ctx.getImageData(0, 0, W, H).data;
#                 // Count non-white / non-transparent pixels — too few means blank
#                 let drawn = 0;
#                 for (let i = 0; i < d.length; i += 4) {
#                     const r = d[i], g = d[i+1], b = d[i+2], a = d[i+3];
#                     if (a < 50) continue;                 // transparent
#                     if (r > 245 && g > 245 && b > 245) continue;  // white background
#                     drawn++;
#                 }
#                 // A rendered image has thousands of colored pixels
#                 return drawn < 800;
#             } catch (e) {
#                 return true;  // cross-origin / not ready
#             }
#         }
#     """)

# def wait_for_captcha(page, timeout=30):
#     """
#     Wait for the captcha popup to appear, THEN wait for the canvas image to render.
#     The image renders 5-10s later — detecting on a blank canvas will fail.
#     """
#     print("⏳ Waiting for the captcha canvas...")
#     deadline = time.time() + timeout

#     # Step 1: wait for the canvas element to become visible
#     canvas_visible = False
#     while time.time() < deadline:
#         try:
#             el = page.query_selector('#huntCaptcha canvas')
#             if el and el.is_visible():
#                 canvas_visible = True
#                 print("✅ Captcha canvas visible — now waiting for the image to render...")
#                 break
#         except:
#             pass
#         time.sleep(0.4)

#     if not canvas_visible:
#         print("❌ Captcha canvas timeout (never became visible)")
#         return False

#     # Step 2: wait for the actual image (ball + target) to be drawn — not blank
#     while time.time() < deadline:
#         try:
#             if not canvas_is_blank(page):
#                 print("✅ Captcha image rendered!")
#                 time.sleep(1.0)  # let it settle a bit
#                 return True
#         except:
#             pass
#         print("   ...image still blank/loading, waiting...")
#         time.sleep(0.6)

#     print("⚠️ Captcha image render timeout — trying anyway")
#     return True

# def debug_captcha_dom(page):
#     """Dump the full captcha DOM to locate the slider."""
#     info = page.evaluate("""
#         () => {
#             const results = [];

#             // Find all interactive elements on the page - full document
#             const tags = ['button', 'div', 'span', 'input', 'canvas'];
#             for (const tag of tags) {
#                 const els = document.querySelectorAll(tag);
#                 for (const el of els) {
#                     const r = el.getBoundingClientRect();
#                     if (r.width < 5 || r.height < 5) continue;
#                     const cls = (el.className || '').toString().toLowerCase();
#                     const id  = (el.id || '').toLowerCase();

#                     // Slider/drag related keywords
#                     if (cls.includes('drag') || cls.includes('slide') || cls.includes('handle') ||
#                         cls.includes('control') || cls.includes('track') || cls.includes('thumb') ||
#                         cls.includes('knob') || cls.includes('scrubber') ||
#                         id.includes('drag') || id.includes('slide') || id.includes('handle') ||
#                         el.getAttribute('draggable') === 'true' ||
#                         el.getAttribute('role') === 'slider') {
#                         results.push({
#                             tag: tag,
#                             id: el.id,
#                             class: el.className.toString().substring(0, 80),
#                             left: Math.round(r.left),
#                             top: Math.round(r.top),
#                             width: Math.round(r.width),
#                             height: Math.round(r.height),
#                             draggable: el.getAttribute('draggable'),
#                             role: el.getAttribute('role')
#                         });
#                     }
#                 }
#             }

#             // Also check every element inside the swal2 popup
#             const swal = document.querySelector('.swal2-popup');
#             if (swal) {
#                 const allInSwal = swal.querySelectorAll('*');
#                 for (const el of allInSwal) {
#                     const r = el.getBoundingClientRect();
#                     if (r.width < 5 || r.height < 5) continue;
#                     const cls = (el.className || '').toString();
#                     const id  = (el.id || '');
#                     // Not already in results and not canvas
#                     if (el.tagName !== 'CANVAS' && (r.width > 20 || r.height > 20)) {
#                         results.push({
#                             tag: el.tagName,
#                             id: id,
#                             class: cls.substring(0, 80),
#                             left: Math.round(r.left),
#                             top: Math.round(r.top),
#                             width: Math.round(r.width),
#                             height: Math.round(r.height),
#                             draggable: el.getAttribute('draggable'),
#                             role: el.getAttribute('role'),
#                             source: 'swal2'
#                         });
#                     }
#                 }
#             }

#             return results;
#         }
#     """)
#     print(f"\n🔍 DOM ELEMENTS FOUND ({len(info)}):")
#     for el in info:
#         print(f"   [{el['tag']}] id='{el.get('id','')}' class='{el.get('class','')}' "
#               f"pos=({el['left']},{el['top']}) size={el['width']}x{el['height']} "
#               f"draggable={el.get('draggable')} role={el.get('role')} src={el.get('source','')}")
#     return info

# def get_positions(page):
#     return page.evaluate("""
#         () => {
#             const canvas = document.querySelector('#huntCaptcha canvas');
#             if (!canvas) return {error: 'no canvas'};
#             const ctx = canvas.getContext('2d');
#             const W = canvas.width, H = canvas.height;
#             const d = ctx.getImageData(0, 0, W, H).data;

#             let ballXs = [], ballYs = [], circleXs = [];

#             for (let y = 0; y < H; y++) {
#                 for (let x = 0; x < W; x++) {
#                     const i = (y * W + x) * 4;
#                     const r = d[i], g = d[i+1], b = d[i+2], a = d[i+3];
#                     if (a < 100) continue;

#                     // Target circle: gray metallic ring, upper area
#                     if (y < H * 0.65) {
#                         const avg = (r+g+b)/3;
#                         const mx = Math.max(Math.abs(r-g), Math.abs(g-b), Math.abs(r-b));
#                         if (avg > 140 && avg < 215 && mx < 22) circleXs.push(x);
#                     }

#                     // Ball / slider handle: white pixels, lower area
#                     if (y > H * 0.55 && r > 210 && g > 210 && b > 210) {
#                         ballXs.push(x);
#                         ballYs.push(y);
#                     }
#                 }
#             }

#             const center = arr => {
#                 if (arr.length < 10) return null;
#                 arr.sort((a,b) => a-b);
#                 const t = Math.floor(arr.length * 0.2);
#                 const s = arr.slice(t, arr.length - t);
#                 return (Math.min(...s) + Math.max(...s)) / 2;
#             };
#             const mean = arr => arr.length ? arr.reduce((a,b)=>a+b,0)/arr.length : null;

#             return {
#                 canvasW: W, canvasH: H,
#                 ballX: center(ballXs),
#                 ballY: mean(ballYs),
#                 circleX: center(circleXs),
#                 ballPx: ballXs.length,
#                 circlePx: circleXs.length
#             };
#         }
#     """)

# def find_slider_element(page, canvas_box):
#     """
#     Find the slider element across the whole document — inside and outside swal2.
#     From the captcha HTML: there is a drag bar with an arrow button below the canvas.
#     """

#     # Method 1: first visible interactive element below the canvas
#     box = page.evaluate("""
#         (canvasBottom) => {
#             // Check every element below the canvas
#             const all = document.querySelectorAll('*');
#             let candidates = [];

#             for (const el of all) {
#                 const r = el.getBoundingClientRect();
#                 // Must be below the canvas, visible, reasonable size
#                 if (r.top > canvasBottom - 5 && r.top < canvasBottom + 150 &&
#                     r.width > 20 && r.height > 10 && r.height < 100) {

#                     const tag = el.tagName.toLowerCase();
#                     const cls = (el.className || '').toString().toLowerCase();
#                     const style = window.getComputedStyle(el);

#                     // Skip hidden/transparent
#                     if (style.display === 'none' || style.visibility === 'hidden' ||
#                         parseFloat(style.opacity) < 0.1) continue;

#                     // Skip canvas itself
#                     if (tag === 'canvas') continue;

#                     candidates.push({
#                         tag: tag,
#                         id: el.id || '',
#                         cls: cls.substring(0, 60),
#                         left: r.left, top: r.top,
#                         width: r.width, height: r.height,
#                         cursor: style.cursor,
#                         isButton: tag === 'button',
#                         hasPointer: style.cursor === 'pointer' || style.cursor === 'grab' || style.cursor === 'ew-resize'
#                     });
#                 }
#             }

#             // Sort by top (closest to canvas first)
#             candidates.sort((a, b) => a.top - b.top);
#             return candidates;
#         }
#     """, canvas_box['top'] + canvas_box['height'])

#     print(f"\n🔍 Below-canvas candidates ({len(box)}):")
#     for c in box[:8]:
#         print(f"   [{c['tag']}] cls='{c['cls']}' pos=({c['left']:.0f},{c['top']:.0f}) "
#               f"size={c['width']:.0f}x{c['height']:.0f} cursor={c['cursor']} btn={c['isButton']}")

#     if box:
#         # Prefer button or element with pointer/grab cursor
#         for c in box:
#             if c['isButton'] or c['hasPointer']:
#                 print(f"✅ Slider chosen: [{c['tag']}] cls='{c['cls']}'")
#                 return {'left': c['left'], 'top': c['top'], 'width': c['width'], 'height': c['height']}

#         # Fallback: first candidate
#         c = box[0]
#         print(f"⚠️ Slider fallback first candidate: [{c['tag']}] cls='{c['cls']}'")
#         return {'left': c['left'], 'top': c['top'], 'width': c['width'], 'height': c['height']}

#     # Method 2: pure position estimate from the image
#     # Slider bar ~50px below the canvas, arrow button in the center
#     print("⚠️ No candidates found, using hard estimate")
#     return {
#         'left':   canvas_box['left'] + canvas_box['width'] / 2 - 25,
#         'top':    canvas_box['top'] + canvas_box['height'] + 50,
#         'width':  50,
#         'height': 40
#     }

# def get_canvas_box(page):
#     return page.evaluate("""
#         () => {
#             const c = document.querySelector('#huntCaptcha canvas');
#             if (!c) return null;
#             const r = c.getBoundingClientRect();
#             return {left: r.left, top: r.top, width: r.width, height: r.height};
#         }
#     """)

# def analyze_captcha(page):
#     """
#     Read the canvas and find three things:
#       - blueX/blueY : the BLUE slider button (handle) on the track below — drag from here
#       - ballX       : the soccer ball (white + nearby black pixels) — distinct from the player's plain white shirt
#       - ringX       : the target ring (medium gray, low-saturation, middle band)
#     All in canvas-internal pixels.
#     """
#     return page.evaluate("""
#         () => {
#             const c = document.querySelector('#huntCaptcha canvas');
#             if (!c) return {error: 'no canvas'};
#             const ctx = c.getContext('2d');
#             const W = c.width, H = c.height;
#             const d = ctx.getImageData(0, 0, W, H).data;
#             const at = (x, y) => { const i = (y*W+x)*4; return [d[i], d[i+1], d[i+2], d[i+3]]; };
#             const trackTop = Math.floor(H * 0.80);   // bottom 20% = slider track

#             let blueXs = [], blueYs = [];
#             let ballPts = [];   // {x,y} soccer ball (pure black <-> pure white tight mix)
#             let grayPts = [];   // {x,y} ring candidates (gray, low-saturation)

#             for (let y = 0; y < H; y++) {
#                 for (let x = 0; x < W; x++) {
#                     const i = (y * W + x) * 4;
#                     const r = d[i], g = d[i+1], b = d[i+2], a = d[i+3];
#                     if (a < 80) continue;

#                     if (y >= trackTop) {
#                         // BLUE slider button
#                         if (b > 105 && (b - r) > 28 && (b - g) > 8) {
#                             blueXs.push(x); blueYs.push(y);
#                         }
#                         continue;
#                     }
#                     if (y <= H * 0.12) continue;   // skip top sky/header

#                     // ---- SOCCER BALL ----
#                     // A PURE BLACK pixel with a PURE WHITE pixel within 9px (the ball's pentagons).
#                     // The ring's outline is GRAY (not pure black), so it stays separate.
#                     if (r < 45 && g < 45 && b < 45) {
#                         let white = false;
#                         for (let dx = -9; dx <= 9 && !white; dx++) {
#                             for (let dy = -9; dy <= 9; dy++) {
#                                 const xx = x+dx, yy = y+dy;
#                                 if (xx<0||xx>=W||yy<0||yy>=H) continue;
#                                 const j = (yy*W+xx)*4;
#                                 if (d[j] > 225 && d[j+1] > 225 && d[j+2] > 225) { white = true; break; }
#                             }
#                         }
#                         if (white) ballPts.push({x, y});
#                     }

#                     // ---- RING (target) ----
#                     // Gray, low-saturation, medium brightness. Upper-middle band.
#                     if (y > H * 0.22 && y < H * 0.70) {
#                         const avg = (r + g + b) / 3;
#                         const mx = Math.max(Math.abs(r-g), Math.abs(g-b), Math.abs(r-b));
#                         if (avg > 120 && avg < 210 && mx < 18) grayPts.push({x, y});
#                     }
#                 }
#             }

#             const mean = a => a.length ? a.reduce((s,v)=>s+v,0)/a.length : null;
#             const centerX = (pts) => {
#                 if (pts.length < 8) return null;
#                 const xs = pts.map(p => p.x).sort((a,b)=>a-b);
#                 const t = Math.floor(xs.length * 0.12);
#                 const s = xs.slice(t, xs.length - t);
#                 return (s[0] + s[s.length-1]) / 2;
#             };

#             const ballX = centerX(ballPts);
#             const ballY = ballPts.length ? mean(ballPts.map(p=>p.y)) : null;

#             // Ring: drop gray pixels near the ball (±22px) so we don't catch the ball's shine
#             let ringPts = grayPts;
#             if (ballX !== null) ringPts = grayPts.filter(p => Math.abs(p.x - ballX) > 22);
#             const ringX = centerX(ringPts);
#             const ringY = ringPts.length ? mean(ringPts.map(p=>p.y)) : null;

#             return {
#                 canvasW: W, canvasH: H,
#                 blueX: blueXs.length >= 8 ? mean(blueXs) : null,
#                 blueY: blueYs.length >= 8 ? mean(blueYs) : null,
#                 blueN: blueXs.length,
#                 ballX: ballX, ballY: ballY ? Math.round(ballY) : null, ballN: ballPts.length,
#                 ringX: ringX, ringY: ringY ? Math.round(ringY) : null, ringN: ringPts.length
#             };
#         }
#     """)

# def check_solved(page):
#     """Result after a drag: 'solved' | 'wrong' | 'error' | 'unclear'"""
#     if page.evaluate("() => !document.querySelector('#huntCaptcha canvas')"):
#         return 'solved'
#     val_err = page.evaluate("""
#         () => {
#             const v = document.querySelector('#swal2-validation-message');
#             return !!(v && v.style.display !== 'none' && v.textContent.trim().length > 0);
#         }
#     """)
#     if val_err:
#         return 'wrong'
#     server_err = page.evaluate("""
#         () => {
#             const t = document.querySelector('.swal2-title');
#             return !!(t && t.textContent.toLowerCase().includes('error'));
#         }
#     """)
#     if server_err:
#         return 'error'
#     return 'unclear'

# def drag_slider_to(page, canvas_box, scale_x, scale_y, btn_x_canvas, btn_y_canvas, target_x_canvas):
#     """Grab the blue button (canvas-px) and drag it along the track to target_x (canvas-px)."""
#     sx = canvas_box['left'] + btn_x_canvas * scale_x
#     sy = canvas_box['top']  + btn_y_canvas * scale_y
#     tx = canvas_box['left'] + target_x_canvas * scale_x
#     dist = tx - sx

#     print(f"🖱️ Drag handle: ({sx:.0f},{sy:.0f}) → x={tx:.0f}  ({dist:+.0f}px)")

#     page.mouse.move(sx, sy, steps=8)
#     time.sleep(random.uniform(0.2, 0.35))
#     page.mouse.down()
#     time.sleep(random.uniform(0.20, 0.35))

#     steps = random.randint(26, 40)
#     for i in range(steps + 1):
#         t = i / steps
#         eased = 1 - (1 - t) ** 3                 # ease-out cubic
#         cx = sx + dist * eased + random.uniform(-0.5, 0.5)
#         cy = sy + random.uniform(-1.5, 1.5)      # stay on the track
#         page.mouse.move(cx, cy)
#         time.sleep(random.uniform(0.006, 0.018))

#     time.sleep(random.uniform(0.25, 0.45))
#     page.mouse.up()

# def disable_hint_overlay(page):
#     """
#     #hintWrapper is an invisible (opacity:0) layer with pointer-events:auto —
#     it intercepts our mouse events on the canvas slider.
#     Disable it so the drag reaches the canvas directly.
#     """
#     try:
#         removed = page.evaluate("""
#             () => {
#                 let n = 0;
#                 document.querySelectorAll('#huntCaptcha #hintWrapper, #huntCaptcha [id*="hint"]').forEach(el => {
#                     el.style.pointerEvents = 'none';
#                     el.style.display = 'none';
#                     n++;
#                 });
#                 return n;
#             }
#         """)
#         if removed:
#             print(f"🧹 Disabled hintWrapper overlay (count={removed})")
#     except Exception as e:
#         print(f"⚠️ hintWrapper disable warning: {e}")

# def _nudge_and_measure(page, sx, sy, nudge_screen, ball0, btn_x):
#     """Press @ (sx,sy), nudge +nudge_screen px right, re-analyze live. Returns (ball_delta, blue_delta, mid)."""
#     page.mouse.move(sx, sy, steps=5)
#     time.sleep(random.uniform(0.12, 0.20))
#     page.mouse.down()
#     time.sleep(random.uniform(0.25, 0.35))
#     for i in range(1, 15):
#         page.mouse.move(sx + nudge_screen * (i / 14), sy + random.uniform(-1, 1))
#         time.sleep(0.012)
#     time.sleep(0.30)
#     mid = analyze_captcha(page)
#     mid_ball = mid.get('ballX')
#     mid_blue = mid.get('blueX')
#     ball_delta = (mid_ball - ball0) if (mid_ball is not None and ball0 is not None) else 0
#     blue_delta = (mid_blue - btn_x) if (mid_blue is not None and btn_x is not None) else 0
#     return ball_delta, blue_delta, mid

# def drag_calibrated(page, canvas_box, scale_x, scale_y, info):
#     """
#     CLOSED-LOOP drag:
#       1. Find the working-y (the y where pressing actually moves the slider).
#       2. HOLD the slider (mouse down) and drive the ball to the ring using live feedback —
#          re-analyze after each step and adjust the mouse based on the error. The ratio is
#          learned internally (self-correcting), so the exact mapping doesn't need to be known.
#       3. RELEASE as soon as the ball is near the ring (<=5px).
#     Return: 'moved' or 'static'
#     """
#     btn_x = info['blueX']
#     base_y = info['blueY']
#     ball0 = info.get('ballX')

#     sx = canvas_box['left'] + btn_x * scale_x
#     left_lim  = canvas_box['left'] + canvas_box['width'] * 0.04
#     right_lim = canvas_box['left'] + canvas_box['width'] * 0.96

#     print(f"🖱️ Grab search @ x={sx:.0f}  Ball0={ball0}  Ring={info.get('ringX')}")

#     # ---- Step 1: find the working-y (where the slider responds) ----
#     working_sy = None
#     cur_x = sx
#     for dy in [16, 30, 0, 44, 58, -14, 72]:
#         cand_y = base_y + dy
#         if cand_y > 300 or cand_y < 200:
#             continue
#         sy = canvas_box['top'] + cand_y * scale_y
#         ball_delta, blue_delta, _ = _nudge_and_measure(page, sx, sy, 45, ball0, btn_x)
#         print(f"   dy={dy:+d} (y={sy:.0f}) → ballΔ={ball_delta:.1f} blueΔ={blue_delta:.1f}")
#         if abs(ball_delta) > 2 or abs(blue_delta) > 2:
#             working_sy = sy
#             cur_x = sx + 45        # mouse is here after the nudge (still down)
#             print(f"   ✅ Slider responsive at y={sy:.0f} — starting closed-loop")
#             break
#         page.mouse.up()
#         time.sleep(0.25)

#     if working_sy is None:
#         print("   ⚠️ Slider did not move at any y (static)")
#         return 'static'

#     # ---- Step 2: closed-loop — drive the ball to the ring (mouse stays DOWN) ----
#     sy = working_sy
#     gain = None              # ball canvas-px per mouse canvas-px (sign + magnitude)
#     prev_ball = None
#     prev_x = None
#     best_err = 1e9
#     for it in range(34):
#         cur = analyze_captcha(page)
#         ballX = cur.get('ballX')
#         ringX = cur.get('ringX')
#         if ballX is None or ringX is None:
#             # no feedback — nudge a bit and look again
#             cur_x = max(left_lim, min(right_lim, cur_x + 12))
#             page.mouse.move(cur_x, sy + random.uniform(-1, 1), steps=3)
#             time.sleep(0.18)
#             continue

#         err = ringX - ballX                       # canvas-px the ball still needs to move
#         best_err = min(best_err, abs(err))
#         # learn the gain (from the previous move)
#         if prev_ball is not None and prev_x is not None and abs(cur_x - prev_x) > 1:
#             db = ballX - prev_ball
#             dm = (cur_x - prev_x) / scale_x        # mouse move in canvas-px
#             if abs(db) > 0.6 and abs(dm) > 0.6:
#                 g = db / dm
#                 gain = g if gain is None else (0.5 * gain + 0.5 * g)

#         print(f"   it{it}: ball={ballX:.0f} ring={ringX:.0f} err={err:+.0f} gain={gain}")
#         if abs(err) <= 5:
#             print("   🎯 Ball aligned with the ring!")
#             break

#         prev_ball = ballX
#         prev_x = cur_x
#         if gain is None or abs(gain) < 0.03:
#             # gain unknown yet — small probe step (assume +mouse → +ball)
#             step = 18 if err > 0 else -18
#         else:
#             step = (err / gain) * scale_x          # mouse screen-px needed
#             step = max(-45, min(45, step))         # cap per step
#         cur_x = max(left_lim, min(right_lim, cur_x + step))
#         page.mouse.move(cur_x, sy + random.uniform(-1, 1), steps=4)
#         time.sleep(0.20)

#     time.sleep(0.25)
#     page.mouse.up()
#     print(f"   release (best_err={best_err:.0f})")
#     return 'moved'

# def drag_via_pointer_events(page):
#     """
#     Fallback: if Playwright's trusted mouse doesn't move the slider, dispatch
#     pointer+mouse+touch events directly on the canvas via JS (bypasses overlay/hit-test).
#     Tries the ring plus a few sweep positions.
#     """
#     info = analyze_captcha(page)
#     if info.get('blueX') is None:
#         return False
#     W = info.get('canvasW', 315)

#     js = """
#         ({bx, by, tx}) => {
#             const c = document.querySelector('#huntCaptcha canvas');
#             if (!c) return false;
#             const r = c.getBoundingClientRect();
#             const sx = r.left + bx, sy = r.top + by;
#             const ex = r.left + tx;
#             const fire = (kind, x, y, buttons) => {
#                 const o = {bubbles:true, cancelable:true, composed:true,
#                            clientX:x, clientY:y, screenX:x, screenY:y,
#                            button:0, buttons:buttons, pointerId:1, pointerType:'mouse',
#                            isPrimary:true, view:window};
#                 try { c.dispatchEvent(new PointerEvent('pointer'+kind, o)); } catch(e){}
#                 try { document.dispatchEvent(new PointerEvent('pointer'+kind, o)); } catch(e){}
#                 const m = kind==='down'?'mousedown':kind==='up'?'mouseup':'mousemove';
#                 try { c.dispatchEvent(new MouseEvent(m, o)); } catch(e){}
#                 try { document.dispatchEvent(new MouseEvent(m, o)); } catch(e){}
#             };
#             fire('down', sx, sy, 1);
#             const N = 24;
#             for (let i = 1; i <= N; i++) {
#                 const x = sx + (ex - sx) * (i / N);
#                 fire('move', x, sy, 1);
#             }
#             fire('move', ex, sy, 1);
#             fire('up', ex, sy, 0);
#             return true;
#         }
#     """

#     targets = []
#     if info.get('ringX') is not None:
#         targets.append(info['ringX'])
#     targets += [W*0.5, W*0.3, W*0.7, W*0.2, W*0.8, W*0.15, W*0.85]

#     for tx in targets:
#         cur = analyze_captcha(page)
#         if cur.get('blueX') is None:
#             break
#         bx = cur['blueX']
#         by = cur['blueY']
#         print(f"   📤 pointer-dispatch: x={bx:.0f}→{tx:.0f} y={by:.0f}")
#         try:
#             page.evaluate(js, {"bx": bx, "by": by, "tx": tx})
#         except Exception as e:
#             print(f"   ⚠️ dispatch error: {e}")
#         time.sleep(1.8)
#         if check_solved(page) == 'solved':
#             return True
#     return False

# def retry_captcha(page, max_retries=12):
#     if not wait_for_captcha(page, timeout=25):
#         return True

#     canvas_box = get_canvas_box(page)
#     if not canvas_box:
#         return True
#     print(f"📐 Canvas: left={canvas_box['left']:.0f} top={canvas_box['top']:.0f} "
#           f"w={canvas_box['width']:.0f} h={canvas_box['height']:.0f}")

#     # Disable the invisible hintWrapper overlay — otherwise it intercepts the drag
#     disable_hint_overlay(page)

#     static_streak = 0
#     for attempt in range(1, max_retries + 1):
#         print(f"\n🔄 Captcha Attempt {attempt}/{max_retries}")

#         if not page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')"):
#             print("✅ Canvas gone — solved!")
#             return True

#         # Don't detect on a blank canvas
#         blank_deadline = time.time() + 10
#         while time.time() < blank_deadline and canvas_is_blank(page):
#             print("   ⏳ Canvas blank, waiting for render...")
#             time.sleep(0.6)

#         disable_hint_overlay(page)   # every time (the popup may re-render)

#         info = analyze_captcha(page)
#         print(f"📊 {json.dumps(info)}")

#         W = info.get('canvasW', 315)
#         H = info.get('canvasH', 300)
#         scale_x = canvas_box['width']  / W
#         scale_y = canvas_box['height'] / H

#         if info.get('blueX') is None:
#             print("⚠️ Blue button not detected — trying from center")
#             info['blueX'] = W / 2
#             info['blueY'] = H * 0.86

#         outcome = drag_calibrated(page, canvas_box, scale_x, scale_y, info)
#         time.sleep(2.5)

#         result = check_solved(page)
#         print(f"   → drag={outcome}  result={result}")
#         if result == 'solved':
#             time.sleep(1.0)
#             if not page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')"):
#                 print("✅ Confirmed solved!")
#                 return True

#         # If the slider stays 'static' at every y, the mouse-drag mechanism simply
#         # isn't working — retrying is pointless. After 3 statics, try the pointer-event fallback.
#         if outcome == 'static':
#             static_streak += 1
#             if static_streak == 3:
#                 print("\n⚠️ Mouse-drag isn't moving the slider — trying POINTER-EVENT drag...")
#                 if drag_via_pointer_events(page):
#                     time.sleep(2.5)
#                     if check_solved(page) == 'solved':
#                         print("✅ Solved via pointer-event drag!")
#                         return True
#             if static_streak >= 5:
#                 print("❌ Slider won't respond by any method — aborting.")
#                 return False
#         else:
#             static_streak = 0

#         close_any_error_dialog(page)
#         time.sleep(1.0)
#         wait_for_captcha(page, timeout=8)

#     return False

# # ================= REGISTER =================

# def click_register_and_handle(page):
#     for attempt in range(1, MAX_REGISTRATION_RETRIES + 1):
#         print(f"\n📤 Register attempt {attempt}/{MAX_REGISTRATION_RETRIES}")

#         reg_selectors = [
#             'button:has-text("REGISTER")',
#             'button.ui-button:has-text("REGISTER")',
#             'span:has-text("Register")',
#             'button[type="submit"]',
#         ]
#         clicked = False
#         for sel in reg_selectors:
#             try:
#                 el = page.wait_for_selector(sel, timeout=5000)
#                 if el and el.is_visible():
#                     el.click()
#                     clicked = True
#                     print(f"✅ REGISTER clicked: {sel}")
#                     break
#             except:
#                 continue

#         if not clicked:
#             print("❌ REGISTER button not found!")
#             return False

#         time.sleep(random.uniform(2, 3))

#         # === IMPORTANT ===
#         # The captcha popup appears 5-10s AFTER clicking REGISTER.
#         # Checking only once would wrongly assume "no captcha" before the popup shows.
#         # So poll for up to 15s until the canvas appears.
#         print("⏳ Waiting for the captcha popup (up to 15s)...")
#         captcha_appeared = False
#         appear_deadline = time.time() + 15
#         while time.time() < appear_deadline:
#             try:
#                 if page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')"):
#                     captcha_appeared = True
#                     break
#             except:
#                 pass
#             time.sleep(0.5)

#         if captcha_appeared:
#             print("🎮 Captcha appeared — solving...")
#             solved = retry_captcha(page, max_retries=12)
#             if not solved:
#                 print("❌ Captcha not solved — retrying registration")
#                 close_any_error_dialog(page)
#                 time.sleep(2)
#                 continue
#             # Confirm the solve: did the canvas actually disappear?
#             time.sleep(2)
#             still_there = page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')")
#             if still_there:
#                 print("❌ Captcha still on screen — retrying")
#                 close_any_error_dialog(page)
#                 time.sleep(2)
#                 continue
#             print("✅ Captcha solved successfully!")
#         else:
#             print("ℹ️ No captcha popup within 15s — assuming direct registration")

#         server_error = page.evaluate("""
#             () => {
#                 const t = document.querySelector('.swal2-title, .swal2-popup h2');
#                 if (t && t.textContent.toLowerCase().includes('error')) return true;
#                 const c = document.querySelector('#swal2-content, .swal2-html-container');
#                 if (c && c.textContent.toLowerCase().includes('server error')) return true;
#                 return false;
#             }
#         """)
#         if server_error:
#             print(f"❌ Server error on attempt {attempt}")
#             close_any_error_dialog(page)
#             time.sleep(random.uniform(4, 8))
#             continue

#         print("✅ Registration done!")
#         return True

#     return False

# # ================= MAIN =================

# def run():
#     print("=== StreakAds Registration Bot (GoLogin) ===\n")

#     token = load_gologin_token()
#     gl = GoLogin({"token": token})

#     profile_id = None
#     pw = None
#     browser = None
#     page = None

#     try:
#         # ---- Create a GoLogin profile (random anti-detect fingerprint) ----
#         profile = gl.createProfileRandomFingerprint({
#             "name": f"streakads-{random.randint(1000, 9999)}",
#             "os": GOLOGIN_OS,
#         })
#         profile_id = profile["id"]
#         print(f"✅ Profile created: {profile_id}")

#         if USE_PROXY:
#             gl.changeProfileProxy(profile_id, PROXY_CONFIG)
#             print("✅ Proxy configured")

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()
#         print(f"✅ GoLogin browser started: {debugger_address}")

#         # ---- Connect Playwright to the GoLogin browser over CDP ----
#         pw = sync_playwright().start()
#         browser = pw.chromium.connect_over_cdp(f"http://{debugger_address}")
#         context = browser.contexts[0]
#         page = context.pages[0] if context.pages else context.new_page()
#         try:
#             page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); }")
#         except Exception:
#             pass

#         print(f"🌐 Opening: {TARGET_URL}")
#         page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
#         time.sleep(random.uniform(3, 5))
#         print(f"📄 URL: {page.url}")

#         print("\n🔍 Looking for 'One-click'...")
#         el = page.wait_for_selector('span.registration-tabs__caption:has-text("One-click")', timeout=100000)
#         el.hover()
#         time.sleep(random.uniform(0.4, 0.7))
#         el.click()
#         print("✅ 'One-click' clicked!")
#         time.sleep(random.uniform(3, 5))
#         print(f"📄 URL: {page.url}")

#         try:
#             page.wait_for_url("**/registration**", timeout=12000)
#         except:
#             print(f"⚠️ URL: {page.url}")
#         time.sleep(random.uniform(2, 3))

#         success = click_register_and_handle(page)

#         if success:
#             # Captcha solved (or never appeared) and no server error.
#             print("\n🎉 Registration complete!")
#             page.screenshot(path="final_state.png", full_page=False)
#             print("📸 Screenshot: final_state.png")
#             wait_sec = random.uniform(5, 10)
#             print(f"⏳ Success! Waiting {wait_sec:.0f}s, then closing the browser...")
#             time.sleep(wait_sec)
#             print("✅ Goal complete.")
#         else:
#             print("\n❌ Registration failed.")
#             try:
#                 page.screenshot(path="failed_state.png", full_page=False)
#                 print("📸 Screenshot: failed_state.png")
#             except Exception:
#                 pass
#             time.sleep(3)

#     except Exception as e:
#         print(f"❌ Error: {e}")
#         import traceback
#         traceback.print_exc()
#         try:
#             if page:
#                 page.screenshot(path="error_state.png")
#         except Exception:
#             pass
#     finally:
#         # ---- Cleanup: close the browser + GoLogin ----
#         try:
#             if browser:
#                 browser.close()
#             if pw:
#                 pw.stop()
#         except Exception:
#             pass
#         try:
#             gl.stop()
#         except Exception:
#             pass
#         print("✅ Browser closed.")

# if __name__ == "__main__":
#     run()



# import time
# import random
# import json
# import os
# import sys
# import asyncio
# import threading
# import datetime
# from playwright.sync_api import sync_playwright

# try:
#     import pproxy
# except ImportError:
#     print("❌ Install pproxy: pip install pproxy")
#     raise

# # ================= GEONODE (proxy upstream) =================
# # This Geonode endpoint is SOCKS5-with-auth. Chromium/Playwright cannot use
# # authenticated SOCKS5 directly, so we run an in-process pproxy bridge:
# #   Playwright -> http://127.0.0.1:<port>  ->  SOCKS5 (auth) Geonode
# # The bridge runs in a background thread (works the same in script and .exe).
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS      = "CHANGE_ME_SECRET"
# GEONODE_HOST      = "sg.proxy.geonode.io"
# GEONODE_PORT      = 11000
# LOCAL_BRIDGE_HOST = "127.0.0.1"

# # Registration retries within a single visit
# MAX_REGISTRATION_RETRIES = 3

# # ================= CONFIG (config.json) =================
# # Everything the user may want to tweak lives in config.json next to the script/exe.
# DEFAULT_CONFIG = {
#     "target_url": "https://partners.streakads.com/click?aid=75&oid=403",
#     "proxy_locations": ["IN"],          # e.g. ["IN"] = India only, or ["IN","US"]
#     "total_visits": 5,                  # how many times to run the whole flow
#     "post_success_wait_seconds": 30,    # stay on the page this long after success
#     "delay_between_visits_min": 10,     # random gap between visits (seconds)
#     "delay_between_visits_max": 30,
#     "headless": False,
#     "log_file": "smartcard.log"
# }

# def app_dir():
#     """Folder of the script (or the .exe when frozen) — config.json/log live here."""
#     if getattr(sys, "frozen", False):
#         return os.path.dirname(sys.executable)
#     return os.path.dirname(os.path.abspath(__file__))

# def load_config():
#     """Load config.json from app_dir; create it with defaults if missing."""
#     path = os.path.join(app_dir(), "config.json")
#     if not os.path.exists(path):
#         with open(path, "w", encoding="utf-8") as f:
#             json.dump(DEFAULT_CONFIG, f, indent=2)
#         print(f"📝 Created default config.json at {path}")
#         return dict(DEFAULT_CONFIG)
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             cfg = json.load(f) or {}
#         merged = dict(DEFAULT_CONFIG)
#         merged.update(cfg)
#         return merged
#     except Exception as e:
#         print(f"⚠️ config.json read error ({e}) — using defaults")
#         return dict(DEFAULT_CONFIG)

# # ---- logging: tee all console output to a timestamped .log file ----
# class _LogFile:
#     def __init__(self, path):
#         self.f = open(path, "a", encoding="utf-8", buffering=1)
#         self._nl = True
#     def write(self, data):
#         for line in data.splitlines(keepends=True):
#             if self._nl and line.strip():
#                 ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 self.f.write(f"[{ts}] ")
#             self.f.write(line)
#             self._nl = line.endswith("\n")
#         return len(data)
#     def flush(self):
#         try: self.f.flush()
#         except Exception: pass

# class _Tee:
#     def __init__(self, *streams): self.streams = streams
#     def write(self, data):
#         for s in self.streams:
#             try: s.write(data); s.flush()
#             except Exception: pass
#         return len(data)
#     def flush(self):
#         for s in self.streams:
#             try: s.flush()
#             except Exception: pass

# def setup_logging(log_file):
#     # Make the console UTF-8 so emojis don't crash on cp1252 terminals / in the .exe.
#     for stream in (sys.__stdout__, sys.__stderr__):
#         try:
#             stream.reconfigure(encoding="utf-8", errors="replace")
#         except Exception:
#             pass
#     path = os.path.join(app_dir(), log_file)
#     lf = _LogFile(path)
#     sys.stdout = _Tee(sys.__stdout__, lf)
#     sys.stderr = _Tee(sys.__stderr__, lf)
#     print(f"📒 Logging to {path}")

# # ---- in-process HTTP->SOCKS5 proxy bridge (works in script AND .exe) ----
# class ProxyBridge:
#     def __init__(self, country, port):
#         self.country = str(country).lower()
#         self.port = port
#         self._loop = None
#         self._thread = None

#     def start(self):
#         # Fresh random sessid each visit -> a new exit IP per visit (Geonode rotates).
#         sessid = "".join(random.choice("0123456789abcdef") for _ in range(8))
#         user = GEONODE_USER_BASE.format(self.country) + f"-sessid-{sessid}"
#         remote_url = f"socks5://{GEONODE_HOST}:{GEONODE_PORT}#{user}:{GEONODE_PASS}"
#         listen_url = self.server_url
#         ready = threading.Event()

#         def _run():
#             self._loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(self._loop)
#             server = pproxy.Server(listen_url)
#             remote = pproxy.Connection(remote_url)
#             args = dict(rserver=[remote], verbose=lambda *a, **k: None)
#             self._loop.run_until_complete(server.start_server(args))
#             ready.set()
#             try:
#                 self._loop.run_forever()
#             finally:
#                 # Cancel pending tasks before closing — avoids noisy
#                 # "Task was destroyed but it is pending!" warnings.
#                 try:
#                     pending = asyncio.all_tasks(self._loop)
#                     for t in pending:
#                         t.cancel()
#                     self._loop.run_until_complete(
#                         asyncio.gather(*pending, return_exceptions=True))
#                 except Exception:
#                     pass
#                 self._loop.close()

#         self._thread = threading.Thread(target=_run, daemon=True)
#         self._thread.start()
#         ready.wait(timeout=10)
#         time.sleep(1.0)
#         print(f"✅ Proxy bridge up: {listen_url} -> SOCKS5 {GEONODE_HOST}:{GEONODE_PORT} (country={self.country.upper()})")

#     def stop(self):
#         try:
#             if self._loop:
#                 self._loop.call_soon_threadsafe(self._loop.stop)
#         except Exception:
#             pass

#     @property
#     def server_url(self):
#         return f"http://{LOCAL_BRIDGE_HOST}:{self.port}"

# # ================= HELPERS =================

# def close_any_error_dialog(page):
#     try:
#         ok = page.query_selector('.swal2-confirm, .swal2-popup button:has-text("OK")')
#         if ok and ok.is_visible():
#             ok.click()
#             print("🔄 Error dialog closed")
#             time.sleep(1.2)
#             return True
#     except:
#         pass
#     return False

# def canvas_is_blank(page):
#     return page.evaluate("""
#         () => {
#             const c = document.querySelector('#huntCaptcha canvas');
#             if (!c) return true;
#             try {
#                 const ctx = c.getContext('2d');
#                 const W = c.width, H = c.height;
#                 if (!W || !H) return true;
#                 const d = ctx.getImageData(0, 0, W, H).data;
#                 let drawn = 0;
#                 for (let i = 0; i < d.length; i += 4) {
#                     const r = d[i], g = d[i+1], b = d[i+2], a = d[i+3];
#                     if (a < 50) continue;
#                     if (r > 245 && g > 245 && b > 245) continue;
#                     drawn++;
#                 }
#                 return drawn < 800;
#             } catch (e) {
#                 return true;
#             }
#         }
#     """)

# def wait_for_captcha(page, timeout=100000):
#     print("⏳ Waiting for the captcha canvas...")
#     deadline = time.time() + timeout

#     canvas_visible = False
#     while time.time() < deadline:
#         try:
#             el = page.query_selector('#huntCaptcha canvas')
#             if el and el.is_visible():
#                 canvas_visible = True
#                 print("✅ Captcha canvas visible — now waiting for image to render...")
#                 break
#         except:
#             pass
#         time.sleep(0.4)

#     if not canvas_visible:
#         print("❌ Captcha canvas timeout")
#         return False

#     while time.time() < deadline:
#         try:
#             if not canvas_is_blank(page):
#                 print("✅ Captcha image rendered!")
#                 time.sleep(1.0)
#                 return True
#         except:
#             pass
#         time.sleep(0.6)

#     print("⚠️ Captcha image render timeout — trying anyway")
#     return True

# def get_canvas_box(page):
#     return page.evaluate("""
#         () => {
#             const c = document.querySelector('#huntCaptcha canvas');
#             if (!c) return null;
#             const r = c.getBoundingClientRect();
#             return {left: r.left, top: r.top, width: r.width, height: r.height};
#         }
#     """)

# def analyze_captcha(page):
#     return page.evaluate("""
#         () => {
#             const c = document.querySelector('#huntCaptcha canvas');
#             if (!c) return {error: 'no canvas'};
#             const ctx = c.getContext('2d');
#             const W = c.width, H = c.height;
#             const d = ctx.getImageData(0, 0, W, H).data;
#             const at = (x, y) => { const i = (y*W+x)*4; return [d[i], d[i+1], d[i+2], d[i+3]]; };
#             const trackTop = Math.floor(H * 0.80);

#             let blueXs = [], blueYs = [];
#             let ballPts = [];
#             let grayPts = [];

#             for (let y = 0; y < H; y++) {
#                 for (let x = 0; x < W; x++) {
#                     const i = (y * W + x) * 4;
#                     const r = d[i], g = d[i+1], b = d[i+2], a = d[i+3];
#                     if (a < 80) continue;

#                     if (y >= trackTop) {
#                         if (b > 105 && (b - r) > 28 && (b - g) > 8) {
#                             blueXs.push(x); blueYs.push(y);
#                         }
#                         continue;
#                     }
#                     if (y <= H * 0.12) continue;

#                     if (r < 45 && g < 45 && b < 45) {
#                         let white = false;
#                         for (let dx = -9; dx <= 9 && !white; dx++) {
#                             for (let dy = -9; dy <= 9 && !white; dy++) {
#                                 const xx = x+dx, yy = y+dy;
#                                 if (xx<0||xx>=W||yy<0||yy>=H) continue;
#                                 const j = (yy*W+xx)*4;
#                                 if (d[j] > 225 && d[j+1] > 225 && d[j+2] > 225) { white = true; break; }
#                             }
#                         }
#                         if (white) ballPts.push({x, y});
#                     }

#                     if (y > H * 0.22 && y < H * 0.70) {
#                         const avg = (r + g + b) / 3;
#                         const mx = Math.max(Math.abs(r-g), Math.abs(g-b), Math.abs(r-b));
#                         // Ring is a light, low-saturation silver/gray circle — loosened range
#                         if (avg > 115 && avg < 240 && mx < 24) grayPts.push({x, y});
#                     }
#                 }
#             }

#             const mean = a => a.length ? a.reduce((s,v)=>s+v,0)/a.length : null;
#             const centerX = (pts) => {
#                 if (pts.length < 8) return null;
#                 const xs = pts.map(p => p.x).sort((a,b)=>a-b);
#                 const t = Math.floor(xs.length * 0.12);
#                 const s = xs.slice(t, xs.length - t);
#                 return (s[0] + s[s.length-1]) / 2;
#             };

#             const ballX = centerX(ballPts);
#             const ballY = ballPts.length ? mean(ballPts.map(p=>p.y)) : null;
#             let ringPts = grayPts;
#             if (ballX !== null) ringPts = grayPts.filter(p => Math.abs(p.x - ballX) > 22);
#             const ringX = centerX(ringPts);

#             return {
#                 canvasW: W, canvasH: H,
#                 blueX: blueXs.length >= 8 ? mean(blueXs) : null,
#                 blueY: blueYs.length >= 8 ? mean(blueYs) : null,
#                 ballX: ballX, ballY: ballY ? Math.round(ballY) : null,
#                 ringX: ringX, ringN: ringPts.length
#             };
#         }
#     """)

# def check_solved(page):
#     """Result after a drag: 'solved' | 'wrong' | 'error' | 'unclear'"""
#     if page.evaluate("() => !document.querySelector('#huntCaptcha canvas')"):
#         return 'solved'
#     val_err = page.evaluate("""
#         () => {
#             const v = document.querySelector('#swal2-validation-message');
#             return !!(v && v.style.display !== 'none' && v.textContent.trim().length > 0);
#         }
#     """)
#     if val_err:
#         return 'wrong'
#     server_err = page.evaluate("""
#         () => {
#             const t = document.querySelector('.swal2-title');
#             return !!(t && t.textContent.toLowerCase().includes('error'));
#         }
#     """)
#     if server_err:
#         return 'error'
#     return 'unclear'

# def disable_hint_overlay(page):
#     """
#     #hintWrapper is an invisible (opacity:0) layer with pointer-events:auto that
#     intercepts mouse events on the canvas slider. Disable it so the drag reaches the canvas.
#     """
#     try:
#         removed = page.evaluate("""
#             () => {
#                 let n = 0;
#                 document.querySelectorAll('#huntCaptcha #hintWrapper, #huntCaptcha [id*="hint"]').forEach(el => {
#                     el.style.pointerEvents = 'none';
#                     el.style.display = 'none';
#                     n++;
#                 });
#                 return n;
#             }
#         """)
#         if removed:
#             print(f"🧹 Disabled hintWrapper overlay (count={removed})")
#     except Exception as e:
#         print(f"⚠️ hintWrapper disable warning: {e}")

# def _nudge_and_measure(page, sx, sy, nudge_screen, ball0, btn_x):
#     """Press @ (sx,sy), nudge +nudge_screen px right, re-analyze live. Returns (ball_delta, blue_delta, mid)."""
#     page.mouse.move(sx, sy, steps=5)
#     time.sleep(random.uniform(0.12, 0.20))
#     page.mouse.down()
#     time.sleep(random.uniform(0.25, 0.35))
#     for i in range(1, 15):
#         page.mouse.move(sx + nudge_screen * (i / 14), sy + random.uniform(-1, 1))
#         time.sleep(0.012)
#     time.sleep(0.30)
#     mid = analyze_captcha(page)
#     mid_ball = mid.get('ballX')
#     mid_blue = mid.get('blueX')
#     ball_delta = (mid_ball - ball0) if (mid_ball is not None and ball0 is not None) else 0
#     blue_delta = (mid_blue - btn_x) if (mid_blue is not None and btn_x is not None) else 0
#     return ball_delta, blue_delta, mid

# def drag_calibrated(page, canvas_box, scale_x, scale_y, info):
#     """
#     CLOSED-LOOP drag:
#       1. Find the working-y (the y where pressing actually moves the slider).
#       2. HOLD the slider (mouse down) and drive the ball to the ring using live feedback —
#          re-analyze after each step and adjust the mouse from the error. The ratio is
#          learned internally (self-correcting), so the exact mapping isn't needed.
#       3. RELEASE once the ball is near the ring (<=5px).
#     Return: 'moved' or 'static'
#     """
#     btn_x = info['blueX']
#     ball0 = info.get('ballX')
#     # LOCK the ring — it is STATIC. Re-detecting it each frame was noisy (50->13->50).
#     ring_target = info.get('ringX')
#     H = info.get('canvasH', 300)

#     if ball0 is None or ring_target is None:
#         print(f"   ⚠️ ball/ring missing (ball={ball0} ring={ring_target}) — skip")
#         return 'nodetect'

#     sx = canvas_box['left'] + btn_x * scale_x
#     left_lim  = canvas_box['left'] + canvas_box['width'] * 0.04
#     right_lim = canvas_box['left'] + canvas_box['width'] * 0.96

#     print(f"🖱️ Grab @ x={sx:.0f}  ball={ball0:.0f}  RING(locked)={ring_target:.0f}")

#     # ---- Step 1: grab where the BALL actually moves ----
#     # The blue button sits LOW on the track (canvas y ~283-300). blueY detection is
#     # flaky, so probe fixed low rows and REQUIRE real ball movement (not just blueΔ,
#     # which can be chevron animation).
#     working_sy = None
#     cur_x = sx
#     for cy in [H - 10, H - 4, H - 18, H + 2, H - 26]:
#         if cy < 200 or cy > H + 5:
#             continue
#         sy = canvas_box['top'] + cy * scale_y
#         ball_delta, blue_delta, _ = _nudge_and_measure(page, sx, sy, 55, ball0, btn_x)
#         print(f"   try cy={cy} (y={sy:.0f}) → ballΔ={ball_delta:.1f} blueΔ={blue_delta:.1f}")
#         if abs(ball_delta) > 2:
#             working_sy = sy
#             cur_x = sx + 55        # mouse is here after the nudge (still down)
#             print(f"   ✅ Ball responds at y={sy:.0f} — starting closed-loop")
#             break
#         page.mouse.up()
#         time.sleep(0.25)

#     if working_sy is None:
#         print("   ⚠️ Ball never moved (slider not engaging)")
#         return 'static'

#     # ---- Step 2: closed-loop — drive the ball to the LOCKED ring (mouse stays DOWN) ----
#     sy = working_sy
#     gain = None              # ball canvas-px per mouse canvas-px (sign + magnitude)
#     prev_ball = None
#     prev_x = None
#     best_err = 1e9
#     for it in range(30):
#         cur = analyze_captcha(page)
#         ballX = cur.get('ballX')
#         if ballX is None:
#             cur_x = max(left_lim, min(right_lim, cur_x + 15))
#             page.mouse.move(cur_x, sy + random.uniform(-1, 1), steps=3)
#             time.sleep(0.16)
#             continue

#         err = ring_target - ballX                 # target is LOCKED (stable)
#         best_err = min(best_err, abs(err))
#         if prev_ball is not None and prev_x is not None and abs(cur_x - prev_x) > 1:
#             db = ballX - prev_ball
#             dm = (cur_x - prev_x) / scale_x        # mouse move in canvas-px
#             if abs(db) > 0.8 and abs(dm) > 0.8:
#                 g = db / dm
#                 gain = g if gain is None else (0.5 * gain + 0.5 * g)

#         print(f"   it{it}: ball={ballX:.0f} ring={ring_target:.0f} err={err:+.0f} gain={gain}")
#         if abs(err) <= 5:
#             print("   🎯 Ball aligned with the ring!")
#             break

#         prev_ball = ballX
#         prev_x = cur_x
#         if gain is None or abs(gain) < 0.1:
#             step = 22 if err > 0 else -22          # gain unknown/too small — fixed probe step
#         else:
#             step = (err / gain) * scale_x
#             step = max(-55, min(55, step))         # cap per step
#         cur_x = max(left_lim, min(right_lim, cur_x + step))
#         page.mouse.move(cur_x, sy + random.uniform(-1, 1), steps=3)
#         time.sleep(0.18)

#     time.sleep(0.25)
#     page.mouse.up()
#     print(f"   release (best_err={best_err:.0f})")
#     return 'moved'

# def drag_via_pointer_events(page):
#     """
#     Fallback: if Playwright's trusted mouse can't move the slider, dispatch
#     pointer+mouse events directly on the canvas via JS (bypasses overlay/hit-test).
#     """
#     info = analyze_captcha(page)
#     if info.get('blueX') is None:
#         return False
#     W = info.get('canvasW', 315)

#     js = """
#         ({bx, by, tx}) => {
#             const c = document.querySelector('#huntCaptcha canvas');
#             if (!c) return false;
#             const r = c.getBoundingClientRect();
#             const sx = r.left + bx, sy = r.top + by;
#             const ex = r.left + tx;
#             const fire = (kind, x, y, buttons) => {
#                 const o = {bubbles:true, cancelable:true, composed:true,
#                            clientX:x, clientY:y, screenX:x, screenY:y,
#                            button:0, buttons:buttons, pointerId:1, pointerType:'mouse',
#                            isPrimary:true, view:window};
#                 try { c.dispatchEvent(new PointerEvent('pointer'+kind, o)); } catch(e){}
#                 try { document.dispatchEvent(new PointerEvent('pointer'+kind, o)); } catch(e){}
#                 const m = kind==='down'?'mousedown':kind==='up'?'mouseup':'mousemove';
#                 try { c.dispatchEvent(new MouseEvent(m, o)); } catch(e){}
#                 try { document.dispatchEvent(new MouseEvent(m, o)); } catch(e){}
#             };
#             fire('down', sx, sy, 1);
#             const N = 24;
#             for (let i = 1; i <= N; i++) fire('move', sx + (ex - sx) * (i / N), sy, 1);
#             fire('move', ex, sy, 1);
#             fire('up', ex, sy, 0);
#             return true;
#         }
#     """

#     targets = []
#     if info.get('ringX') is not None:
#         targets.append(info['ringX'])
#     targets += [W*0.5, W*0.3, W*0.7, W*0.2, W*0.8, W*0.15, W*0.85]

#     for tx in targets:
#         cur = analyze_captcha(page)
#         if cur.get('blueX') is None:
#             break
#         bx = cur['blueX']
#         by = cur['blueY']
#         print(f"   📤 pointer-dispatch: x={bx:.0f}→{tx:.0f} y={by:.0f}")
#         try:
#             page.evaluate(js, {"bx": bx, "by": by, "tx": tx})
#         except Exception as e:
#             print(f"   ⚠️ dispatch error: {e}")
#         time.sleep(1.8)
#         if check_solved(page) == 'solved':
#             return True
#     return False

# def retry_captcha(page, max_retries=12):
#     if not wait_for_captcha(page, timeout=100000):
#         return True

#     canvas_box = get_canvas_box(page)
#     if not canvas_box:
#         return True
#     print(f"📐 Canvas: left={canvas_box['left']:.0f} top={canvas_box['top']:.0f} "
#           f"w={canvas_box['width']:.0f} h={canvas_box['height']:.0f}")

#     # Disable the invisible hintWrapper overlay — otherwise it intercepts the drag
#     disable_hint_overlay(page)

#     static_streak = 0
#     for attempt in range(1, max_retries + 1):
#         print(f"\n🔄 Captcha Attempt {attempt}/{max_retries}")

#         if not page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')"):
#             print("✅ Canvas gone — solved!")
#             return True

#         # Don't detect on a blank canvas
#         blank_deadline = time.time() + 10
#         while time.time() < blank_deadline and canvas_is_blank(page):
#             print("   ⏳ Canvas blank, waiting for render...")
#             time.sleep(0.6)

#         disable_hint_overlay(page)   # every time (the popup may re-render)

#         info = analyze_captcha(page)
#         print(f"📊 {json.dumps(info)}")

#         if info.get('blueX') is None:
#             print("⚠️ Blue button not detected — trying from center")
#             info['blueX'] = info.get('canvasW', 315) / 2
#             info['blueY'] = info.get('canvasH', 300) * 0.86

#         scale_x = canvas_box['width'] / info['canvasW']
#         scale_y = canvas_box['height'] / info['canvasH']

#         outcome = drag_calibrated(page, canvas_box, scale_x, scale_y, info)
#         time.sleep(2.5)

#         result = check_solved(page)
#         print(f"   → drag={outcome}  result={result}")
#         if result == 'solved':
#             time.sleep(1.0)
#             if not page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')"):
#                 print("✅ Confirmed solved!")
#                 return True

#         # If the slider stays 'static' at every y, mouse-drag isn't working.
#         # After 3 statics, try the pointer-event fallback; give up after 5.
#         if outcome == 'static':
#             static_streak += 1
#             if static_streak == 3:
#                 print("\n⚠️ Mouse-drag isn't moving the slider — trying POINTER-EVENT drag...")
#                 if drag_via_pointer_events(page):
#                     time.sleep(2.5)
#                     if check_solved(page) == 'solved':
#                         print("✅ Solved via pointer-event drag!")
#                         return True
#             if static_streak >= 5:
#                 print("❌ Slider won't respond by any method — aborting.")
#                 return False
#         else:
#             static_streak = 0

#         close_any_error_dialog(page)
#         time.sleep(1.0)
#         wait_for_captcha(page, timeout=3000)

#     return False

# # ================= REGISTER =================

# def click_register_and_handle(page):
#     for attempt in range(1, MAX_REGISTRATION_RETRIES + 1):
#         print(f"\n📤 Register attempt {attempt}/{MAX_REGISTRATION_RETRIES}")

#         reg_selectors = [
#             'button:has-text("REGISTER")',
#             'button.ui-button:has-text("REGISTER")',
#             'button[type="submit"]',
#         ]
#         clicked = False
#         for sel in reg_selectors:
#             try:
#                 el = page.wait_for_selector(sel, timeout=100000)
#                 if el and el.is_visible():
#                     el.click()
#                     clicked = True
#                     print(f"✅ REGISTER clicked")
#                     break
#             except:
#                 continue

#         if not clicked:
#             print("❌ REGISTER button not found!")
#             return False

#         time.sleep(random.uniform(2, 4))

#         # The captcha popup appears a few seconds AFTER clicking REGISTER. Over a
#         # residential proxy this can be slow, so poll generously (up to 45s) and also
#         # accept the swal2 popup as a sign the captcha is on its way.
#         print("⏳ Waiting for captcha popup (up to 45s)...")
#         captcha_appeared = False
#         appear_deadline = time.time() + 45
#         while time.time() < appear_deadline:
#             try:
#                 has_canvas = page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')")
#                 has_popup  = page.evaluate("() => !!document.querySelector('#huntCaptcha, .s-swal2-captcha-popup')")
#             except Exception:
#                 has_canvas, has_popup = False, False
#             if has_canvas:
#                 captcha_appeared = True
#                 break
#             if has_popup:
#                 print("   …captcha popup detected, waiting for canvas to render…")
#             remaining = int(appear_deadline - time.time())
#             if remaining % 5 == 0:
#                 print(f"   …still waiting ({remaining}s left)…")
#             time.sleep(1.0)

#         if captcha_appeared:
#             print("🎮 Captcha appeared — solving...")
#             solved = retry_captcha(page, max_retries=12)
#             if not solved:
#                 print("❌ Captcha solve failed — retrying registration")
#                 close_any_error_dialog(page)
#                 time.sleep(2)
#                 continue
#         else:
#             print("ℹ️ No captcha appeared within 45s — assuming direct registration")

#         print("✅ Registration done!")
#         return True

#     return False

# # ================= MAIN =================

# def do_one_visit(config, proxy_port, visit_num):
#     """One full visit: fresh proxy IP -> browser -> navigate -> register -> wait -> close."""
#     country = random.choice(config["proxy_locations"])
#     bridge = ProxyBridge(country, proxy_port)
#     bridge.start()
#     proxy = {"server": bridge.server_url}
#     target = config["target_url"]
#     headless = bool(config.get("headless", False))
#     success = False

#     try:
#       with sync_playwright() as pw:
#         browser = pw.chromium.launch(
#             headless=headless,
#             proxy=proxy,
#             args=[
#                 '--start-maximized',
#                 '--disable-blink-features=AutomationControlled',
#                 # Force HTTP/1.1 — proxied HTTP/2 can cause ERR_RESPONSE_HEADERS_TRUNCATED.
#                 '--disable-http2',
#                 '--disable-quic',
#             ]
#         )
#         context = browser.new_context(
#             viewport={"width": 1440, "height": 900},
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#         )
#         page = context.new_page()

#         try:
#             # Residential proxies are flaky on the first hit — retry the navigation a few times.
#             print(f"🌐 Opening: {target}")
#             last_err = None
#             for nav_try in range(1, 5):
#                 try:
#                     page.goto(target, timeout=100000, wait_until="commit")
#                     page.wait_for_load_state("domcontentloaded", timeout=100000)
#                     last_err = None
#                     break
#                 except Exception as e:
#                     last_err = e
#                     print(f"⚠️ Navigation attempt {nav_try}/4 failed: {str(e).splitlines()[0]}")
#                     time.sleep(random.uniform(3, 6))
#             if last_err:
#                 raise last_err
#             time.sleep(random.uniform(3, 6))

#             print("🔍 Looking for 'One-click'...")
#             el = page.wait_for_selector('span.registration-tabs__caption:has-text("One-click")', timeout=100000)
#             el.click()
#             print("✅ 'One-click' clicked!")
#             time.sleep(random.uniform(3, 5))

#             success = click_register_and_handle(page)

#             if success:
#                 print("\n🎉 Registration complete!")
#                 try:
#                     page.screenshot(path=os.path.join(app_dir(), f"success_visit{visit_num}.png"))
#                 except Exception:
#                     pass
#                 # Stay on the page for the configured time before closing.
#                 wait_sec = float(config.get("post_success_wait_seconds", 30))
#                 print(f"⏳ Staying on page for {wait_sec:.0f}s before closing...")
#                 time.sleep(wait_sec)
#                 print("✅ Goal complete.")
#             else:
#                 print("\n❌ Registration failed.")
#                 try:
#                     page.screenshot(path=os.path.join(app_dir(), f"failed_visit{visit_num}.png"))
#                 except Exception:
#                     pass
#                 time.sleep(3)

#         except Exception as e:
#             print(f"❌ Error: {e}")
#             import traceback
#             traceback.print_exc()
#             try:
#                 page.screenshot(path=os.path.join(app_dir(), f"error_visit{visit_num}.png"))
#             except Exception:
#                 pass
#         finally:
#             browser.close()
#             print("✅ Browser closed.")
#     finally:
#         bridge.stop()
#         print("🧹 Proxy bridge stopped.")

#     return success

# # ================= MAIN =================

# def run():
#     config = load_config()
#     setup_logging(config.get("log_file", "smartcard.log"))

#     # Validate / normalize config
#     locations = config.get("proxy_locations") or ["IN"]
#     config["proxy_locations"] = [str(c) for c in locations]
#     total = max(1, int(config.get("total_visits", 1)))

#     print("=== StreakAds Registration Bot ===")
#     print(f"   target_url  : {config['target_url']}")
#     print(f"   locations   : {config['proxy_locations']}")
#     print(f"   total_visits: {total}\n")

#     ok = 0
#     for visit in range(1, total + 1):
#         print(f"\n========== VISIT {visit}/{total} ==========")
#         port = 8089 + (visit % 50)   # vary the local bridge port to avoid bind races
#         try:
#             if do_one_visit(config, port, visit):
#                 ok += 1
#         except Exception as e:
#             print(f"❌ Visit {visit} crashed: {e}")
#         print(f"📈 Successful so far: {ok}/{visit}")

#         if visit < total:
#             dmin = float(config.get("delay_between_visits_min", 10))
#             dmax = float(config.get("delay_between_visits_max", 30))
#             delay = random.uniform(min(dmin, dmax), max(dmin, dmax))
#             print(f"⏳ Waiting {delay:.0f}s before the next visit...")
#             time.sleep(delay)

#     print(f"\n🏁 All visits done. Success: {ok}/{total}")

# if __name__ == "__main__":
#     run()







import time
import random
import json
import sys
import os
import asyncio
import threading
from playwright.sync_api import sync_playwright

try:
    import pproxy
except ImportError:
    print("❌ Install pproxy: pip install pproxy")
    raise

# When frozen as a PyInstaller .exe, load the Playwright browser bundled inside the app.
if getattr(sys, "frozen", False):
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")

# ================= GEONODE CONFIG =================
# This Geonode endpoint is SOCKS5-with-auth. Chromium/Playwright cannot use
# authenticated SOCKS5 directly, so we run an in-process pproxy bridge (thread) so
# it also works inside the .exe (a subprocess of `python -m pproxy` would not).
#   Playwright -> http://127.0.0.1:LOCAL_BRIDGE_PORT  ->  SOCKS5 (auth) Geonode
GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
GEONODE_PASS      = "CHANGE_ME_SECRET"
GEONODE_HOST      = "sg.proxy.geonode.io"
GEONODE_PORT      = 11000

# Local HTTP bridge (pproxy) that Playwright connects to
LOCAL_BRIDGE_HOST = "127.0.0.1"
LOCAL_BRIDGE_PORT = 8089

# ================= CONFIG =================
TARGET_URL = "https://partners.streakads.com/click?aid=75&oid=403"
MAX_REGISTRATION_RETRIES = 3

# Country code (change if needed)
COUNTRY_CODE = "in"   # India

# ---- How many total visits/registrations to perform (change this number) ----
TOTAL_VISITS = 10

# Log file: records how many visits succeeded (captcha solved) and how many failed
LOG_FILE = "registration_results.log"

# ================= HELPERS =================

class _ProxyBridge:
    """Handle for the in-process bridge; .terminate() stops the background loop."""
    def __init__(self):
        self._loop = None
        self._thread = None
    def terminate(self):
        try:
            if self._loop:
                self._loop.call_soon_threadsafe(self._loop.stop)
        except Exception:
            pass

def start_proxy_bridge():
    """
    Start an in-process pproxy HTTP->SOCKS5 bridge (background thread) so Playwright
    can use the authenticated Geonode SOCKS5 proxy. Runs the same in script and .exe.
    Requires: pip install pproxy
    Returns a handle with .terminate().
    """
    remote_url = (f"socks5://{GEONODE_HOST}:{GEONODE_PORT}"
                  f"#{GEONODE_USER_BASE.format(COUNTRY_CODE)}:{GEONODE_PASS}")
    listen_url = f"http://{LOCAL_BRIDGE_HOST}:{LOCAL_BRIDGE_PORT}"
    h = _ProxyBridge()
    ready = threading.Event()

    def _ignore_reset(loop, context):
        # SOCKS upstream connections get reset constantly (WinError 10054) — harmless noise.
        exc = context.get("exception")
        if isinstance(exc, (ConnectionResetError, ConnectionAbortedError, OSError)):
            return
        loop.default_exception_handler(context)

    def _run():
        h._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(h._loop)
        h._loop.set_exception_handler(_ignore_reset)
        server = pproxy.Server(listen_url)
        remote = pproxy.Connection(remote_url)
        args = dict(rserver=[remote], verbose=lambda *a, **k: None)
        h._loop.run_until_complete(server.start_server(args))
        ready.set()
        try:
            h._loop.run_forever()
        finally:
            try:
                pending = asyncio.all_tasks(h._loop)
                for t in pending:
                    t.cancel()
                h._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass
            h._loop.close()

    h._thread = threading.Thread(target=_run, daemon=True)
    h._thread.start()
    ready.wait(timeout=10)
    time.sleep(1.0)
    print(f"✅ Proxy bridge up: {listen_url} -> SOCKS5 {GEONODE_HOST}:{GEONODE_PORT} (country={COUNTRY_CODE})")
    return h

def close_any_error_dialog(page):
    try:
        ok = page.query_selector('.swal2-confirm, .swal2-popup button:has-text("OK")')
        if ok and ok.is_visible():
            ok.click()
            print("🔄 Error dialog closed")
            time.sleep(1.2)
            return True
    except:
        pass
    return False

def registration_succeeded(page):
    """
    True if the 'THANKS FOR THE REGISTRATION!' success popup is visible.
    This is the REAL proof the captcha was solved — it appears a few seconds
    after a correct solve (showing the new username/password).
    """
    try:
        return page.evaluate("""
            () => {
                const t = (document.body.innerText || '');
                return /THANKS FOR THE REGISTRATION/i.test(t) ||
                       /do not forget to save your username and password/i.test(t);
            }
        """)
    except Exception:
        return False

def close_server_error(page):
    """
    Dismiss the 'Server error. Please try again later.' popup (click Ok, or the X)
    so a fresh captcha can appear. Returns True if a server-error popup was closed.
    """
    try:
        is_err = page.evaluate("""
            () => {
                const txt = (document.body.innerText || '');
                return /server error/i.test(txt) ||
                       !!document.querySelector('.ui-status-icon--status-error');
            }
        """)
        if not is_err:
            return False
        # Prefer the Ok submit button, fall back to the close (X) button.
        for sel in ['.ui-popup__submit', '.ui-popup__close',
                    'button:has-text("Ok")', 'button:has-text("OK")']:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    btn.click()
                    print("🔄 Server-error popup closed — will wait for a fresh captcha")
                    time.sleep(1.2)
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False

def canvas_is_blank(page):
    return page.evaluate("""
        () => {
            const c = document.querySelector('#huntCaptcha canvas');
            if (!c) return true;
            try {
                const ctx = c.getContext('2d');
                const W = c.width, H = c.height;
                if (!W || !H) return true;
                const d = ctx.getImageData(0, 0, W, H).data;
                let drawn = 0;
                for (let i = 0; i < d.length; i += 4) {
                    const r = d[i], g = d[i+1], b = d[i+2], a = d[i+3];
                    if (a < 50) continue;
                    if (r > 245 && g > 245 && b > 245) continue;
                    drawn++;
                }
                return drawn < 800;
            } catch (e) {
                return true;
            }
        }
    """)

def wait_for_captcha(page, timeout=100000):
    print("⏳ Waiting for the captcha canvas...")
    deadline = time.time() + timeout

    canvas_visible = False
    while time.time() < deadline:
        try:
            el = page.query_selector('#huntCaptcha canvas')
            if el and el.is_visible():
                canvas_visible = True
                print("✅ Captcha canvas visible — now waiting for image to render...")
                break
        except:
            pass
        time.sleep(0.4)

    if not canvas_visible:
        print("❌ Captcha canvas timeout")
        return False

    while time.time() < deadline:
        try:
            if not canvas_is_blank(page):
                print("✅ Captcha image rendered!")
                time.sleep(1.0)
                return True
        except:
            pass
        time.sleep(0.6)

    print("⚠️ Captcha image render timeout — trying anyway")
    return True

def get_canvas_box(page):
    return page.evaluate("""
        () => {
            const c = document.querySelector('#huntCaptcha canvas');
            if (!c) return null;
            const r = c.getBoundingClientRect();
            return {left: r.left, top: r.top, width: r.width, height: r.height};
        }
    """)

def analyze_captcha(page):
    return page.evaluate("""
        () => {
            const c = document.querySelector('#huntCaptcha canvas');
            if (!c) return {error: 'no canvas'};
            const ctx = c.getContext('2d');
            const W = c.width, H = c.height;
            const d = ctx.getImageData(0, 0, W, H).data;
            const at = (x, y) => { const i = (y*W+x)*4; return [d[i], d[i+1], d[i+2], d[i+3]]; };
            const trackTop = Math.floor(H * 0.80);
            // Skin tone (goalkeeper face/hands/legs) — used to reject the keeper from ball/ring.
            const isSkin = (R,G,B) => (R>115 && G>75 && B>55 && (R-B)>22 && R>=(G-15) && B<195 && G<210);

            let blueXs = [], blueYs = [];
            let ballPts = [];
            let grayPts = [];

            for (let y = 0; y < H; y++) {
                for (let x = 0; x < W; x++) {
                    const i = (y * W + x) * 4;
                    const r = d[i], g = d[i+1], b = d[i+2], a = d[i+3];
                    if (a < 80) continue;

                    if (y >= trackTop) {
                        if (b > 105 && (b - r) > 28 && (b - g) > 8) {
                            blueXs.push(x); blueYs.push(y);
                        }
                        continue;
                    }
                    if (y <= H * 0.12) continue;

                    // ---- SOCCER BALL ----
                    // PURE BLACK with PURE WHITE within 9px, AND no skin within 13px.
                    // The skin check rejects the GOALKEEPER (white shirt + black shorts + skin),
                    // which previously got mis-detected as the ball (giving a static ballX).
                    if (r < 45 && g < 45 && b < 45) {
                        let white = false, skin = false;
                        for (let dy = -9; dy <= 9 && !white; dy++) {
                            for (let dx = -9; dx <= 9; dx++) {
                                const xx = x+dx, yy = y+dy;
                                if (xx<0||xx>=W||yy<0||yy>=H) continue;
                                const j = (yy*W+xx)*4;
                                if (d[j] > 225 && d[j+1] > 225 && d[j+2] > 225) { white = true; break; }
                            }
                        }
                        for (let dy = -13; dy <= 13 && !skin; dy++) {
                            for (let dx = -13; dx <= 13; dx++) {
                                const xx = x+dx, yy = y+dy;
                                if (xx<0||xx>=W||yy<0||yy>=H) continue;
                                const j = (yy*W+xx)*4;
                                if (isSkin(d[j], d[j+1], d[j+2])) { skin = true; break; }
                            }
                        }
                        if (white && !skin) ballPts.push({x, y});
                    }

                    // ---- RING (target) ----
                    // Light low-saturation gray circle. Exclude bright white (posts/net/shirt)
                    // and skin (keeper). The ball region is removed afterwards.
                    if (y > H * 0.22 && y < H * 0.68) {
                        const avg = (r + g + b) / 3;
                        const mx = Math.max(Math.abs(r-g), Math.abs(g-b), Math.abs(r-b));
                        if (avg > 128 && avg < 224 && mx < 20 && !isSkin(r, g, b)) {
                            grayPts.push({x, y});
                        }
                    }
                }
            }

            const mean = a => a.length ? a.reduce((s,v)=>s+v,0)/a.length : null;
            const centerX = (pts) => {
                if (pts.length < 8) return null;
                const xs = pts.map(p => p.x).sort((a,b)=>a-b);
                const t = Math.floor(xs.length * 0.12);
                const s = xs.slice(t, xs.length - t);
                return (s[0] + s[s.length-1]) / 2;
            };

            const ballX = centerX(ballPts);
            const ballY = ballPts.length ? mean(ballPts.map(p=>p.y)) : null;
            let ringPts = grayPts;
            if (ballX !== null) ringPts = grayPts.filter(p => Math.abs(p.x - ballX) > 25);
            const ringX = centerX(ringPts);

            return {
                canvasW: W, canvasH: H,
                blueX: blueXs.length >= 8 ? mean(blueXs) : null,
                blueY: blueYs.length >= 8 ? mean(blueYs) : null,
                ballX: ballX, ballY: ballY ? Math.round(ballY) : null, ballN: ballPts.length,
                ringX: ringX, ringN: ringPts.length
            };
        }
    """)

def check_solved(page):
    """Result after a drag: 'solved' | 'wrong' | 'error' | 'unclear'"""
    if page.evaluate("() => !document.querySelector('#huntCaptcha canvas')"):
        return 'solved'
    val_err = page.evaluate("""
        () => {
            const v = document.querySelector('#swal2-validation-message');
            return !!(v && v.style.display !== 'none' && v.textContent.trim().length > 0);
        }
    """)
    if val_err:
        return 'wrong'
    server_err = page.evaluate("""
        () => {
            const t = document.querySelector('.swal2-title');
            return !!(t && t.textContent.toLowerCase().includes('error'));
        }
    """)
    if server_err:
        return 'error'
    return 'unclear'

def disable_hint_overlay(page):
    """
    #hintWrapper is an invisible (opacity:0) layer with pointer-events:auto that
    intercepts mouse events on the canvas slider. Disable it so the drag reaches the canvas.
    """
    try:
        removed = page.evaluate("""
            () => {
                let n = 0;
                document.querySelectorAll('#huntCaptcha #hintWrapper, #huntCaptcha [id*="hint"]').forEach(el => {
                    el.style.pointerEvents = 'none';
                    el.style.display = 'none';
                    n++;
                });
                return n;
            }
        """)
        if removed:
            print(f"🧹 Disabled hintWrapper overlay (count={removed})")
    except Exception as e:
        print(f"⚠️ hintWrapper disable warning: {e}")

def _nudge_and_measure(page, sx, sy, nudge_screen, ball0, btn_x):
    """Press @ (sx,sy), nudge +nudge_screen px right, re-analyze live. Returns (ball_delta, blue_delta, mid)."""
    page.mouse.move(sx, sy, steps=5)
    time.sleep(random.uniform(0.12, 0.20))
    page.mouse.down()
    time.sleep(random.uniform(0.25, 0.35))
    for i in range(1, 15):
        page.mouse.move(sx + nudge_screen * (i / 14), sy + random.uniform(-1, 1))
        time.sleep(0.012)
    time.sleep(0.30)
    mid = analyze_captcha(page)
    mid_ball = mid.get('ballX')
    mid_blue = mid.get('blueX')
    ball_delta = (mid_ball - ball0) if (mid_ball is not None and ball0 is not None) else 0
    blue_delta = (mid_blue - btn_x) if (mid_blue is not None and btn_x is not None) else 0
    return ball_delta, blue_delta, mid

def drag_calibrated(page, canvas_box, scale_x, scale_y, info):
    """
    CLOSED-LOOP drag:
      1. Find the working-y (the y where pressing actually moves the slider).
      2. HOLD the slider (mouse down) and drive the ball to the ring using live feedback —
         re-analyze after each step and adjust the mouse from the error. The ratio is
         learned internally (self-correcting), so the exact mapping isn't needed.
      3. RELEASE once the ball is near the ring (<=5px).
    Return: 'moved' or 'static'
    """
    btn_x = info['blueX']
    ball0 = info.get('ballX')
    # LOCK the ring — it is STATIC. Re-detecting it each frame was noisy (50->13->50).
    ring_target = info.get('ringX')
    H = info.get('canvasH', 300)

    if ball0 is None or ring_target is None:
        print(f"   ⚠️ ball/ring missing (ball={ball0} ring={ring_target}) — skip")
        return 'nodetect', 1e9

    sx = canvas_box['left'] + btn_x * scale_x
    left_lim  = canvas_box['left'] + canvas_box['width'] * 0.04
    right_lim = canvas_box['left'] + canvas_box['width'] * 0.96

    print(f"🖱️ Grab @ x={sx:.0f}  ball={ball0:.0f}  RING(locked)={ring_target:.0f}")

    # ---- Step 1: grab where the BALL actually moves ----
    # The blue button sits LOW on the track (canvas y ~283-300). blueY detection is
    # flaky, so probe fixed low rows and REQUIRE real ball movement (not just blueΔ,
    # which can be chevron animation).
    working_sy = None
    cur_x = sx
    seed_gain = None
    for cy in [H - 10, H - 4, H - 18, H + 2, H - 26]:
        if cy < 200 or cy > H + 5:
            continue
        sy = canvas_box['top'] + cy * scale_y
        ball_delta, blue_delta, _ = _nudge_and_measure(page, sx, sy, 55, ball0, btn_x)
        print(f"   try cy={cy} (y={sy:.0f}) → ballΔ={ball_delta:.1f} blueΔ={blue_delta:.1f}")
        if abs(ball_delta) > 2:
            working_sy = sy
            cur_x = sx + 55                  # mouse is here after the nudge (still down)
            seed_gain = ball_delta / 55.0    # ball canvas-px per mouse screen-px (with SIGN)
            print(f"   ✅ Ball responds at y={sy:.0f} (seed gain={seed_gain:.3f}) — closed-loop")
            break
        page.mouse.up()
        time.sleep(0.25)

    if working_sy is None:
        print("   ⚠️ Ball never moved (slider not engaging)")
        return 'static', 1e9

    # ---- Step 2: closed-loop — drive the ball to the LOCKED ring (mouse stays DOWN) ----
    sy = working_sy
    gain = seed_gain          # seed from the grab nudge -> correct direction from the start
    prev_ball = None
    prev_x = None
    best_err = 1e9
    stuck = 0
    for it in range(30):
        cur = analyze_captcha(page)
        ballX = cur.get('ballX')
        if ballX is None:
            cur_x = max(left_lim, min(right_lim, cur_x + 15))
            page.mouse.move(cur_x, sy + random.uniform(-1, 1), steps=3)
            time.sleep(0.16)
            continue

        err = ring_target - ballX                 # target is LOCKED (stable)
        best_err = min(best_err, abs(err))
        if prev_ball is not None and prev_x is not None and abs(cur_x - prev_x) > 1:
            db = ballX - prev_ball
            dm = (cur_x - prev_x) / scale_x        # mouse move in canvas-px
            if abs(db) > 0.8 and abs(dm) > 0.8:
                g = db / dm
                gain = g if gain is None else (0.5 * gain + 0.5 * g)
                stuck = 0
            else:
                stuck += 1                          # ball didn't move this step

        print(f"   it{it}: ball={ballX:.0f} ring={ring_target:.0f} err={err:+.0f} gain={gain}")
        if abs(err) <= 5:
            print("   🎯 Ball aligned with the ring!")
            break
        if stuck >= 6:
            print("   ⚠️ Ball stopped responding — giving up this attempt")
            break

        prev_ball = ballX
        prev_x = cur_x
        if gain is None or abs(gain) < 0.05:
            step = 25 if err > 0 else -25          # gain unknown — fixed probe step
        else:
            step = (err / gain) * scale_x
            step = max(-60, min(60, step))         # cap per step
        cur_x = max(left_lim, min(right_lim, cur_x + step))
        page.mouse.move(cur_x, sy + random.uniform(-1, 1), steps=3)
        time.sleep(0.18)

    time.sleep(0.25)
    page.mouse.up()
    print(f"   release (best_err={best_err:.0f})")
    return 'moved', best_err

def drag_via_pointer_events(page):
    """
    Fallback: if Playwright's trusted mouse can't move the slider, dispatch
    pointer+mouse events directly on the canvas via JS (bypasses overlay/hit-test).
    """
    info = analyze_captcha(page)
    if info.get('blueX') is None:
        return False
    W = info.get('canvasW', 315)

    js = """
        ({bx, by, tx}) => {
            const c = document.querySelector('#huntCaptcha canvas');
            if (!c) return false;
            const r = c.getBoundingClientRect();
            const sx = r.left + bx, sy = r.top + by;
            const ex = r.left + tx;
            const fire = (kind, x, y, buttons) => {
                const o = {bubbles:true, cancelable:true, composed:true,
                           clientX:x, clientY:y, screenX:x, screenY:y,
                           button:0, buttons:buttons, pointerId:1, pointerType:'mouse',
                           isPrimary:true, view:window};
                try { c.dispatchEvent(new PointerEvent('pointer'+kind, o)); } catch(e){}
                try { document.dispatchEvent(new PointerEvent('pointer'+kind, o)); } catch(e){}
                const m = kind==='down'?'mousedown':kind==='up'?'mouseup':'mousemove';
                try { c.dispatchEvent(new MouseEvent(m, o)); } catch(e){}
                try { document.dispatchEvent(new MouseEvent(m, o)); } catch(e){}
            };
            fire('down', sx, sy, 1);
            const N = 24;
            for (let i = 1; i <= N; i++) fire('move', sx + (ex - sx) * (i / N), sy, 1);
            fire('move', ex, sy, 1);
            fire('up', ex, sy, 0);
            return true;
        }
    """

    targets = []
    if info.get('ringX') is not None:
        targets.append(info['ringX'])
    targets += [W*0.5, W*0.3, W*0.7, W*0.2, W*0.8, W*0.15, W*0.85]

    for tx in targets:
        cur = analyze_captcha(page)
        if cur.get('blueX') is None:
            break
        bx = cur['blueX']
        by = cur['blueY']
        print(f"   📤 pointer-dispatch: x={bx:.0f}→{tx:.0f} y={by:.0f}")
        try:
            page.evaluate(js, {"bx": bx, "by": by, "tx": tx})
        except Exception as e:
            print(f"   ⚠️ dispatch error: {e}")
        time.sleep(1.8)
        if check_solved(page) == 'solved':
            return True
    return False

def retry_captcha(page, max_retries=12):
    if not wait_for_captcha(page, timeout=100000):
        return True

    canvas_box = get_canvas_box(page)
    if not canvas_box:
        return True
    print(f"📐 Canvas: left={canvas_box['left']:.0f} top={canvas_box['top']:.0f} "
          f"w={canvas_box['width']:.0f} h={canvas_box['height']:.0f}")

    # Disable the invisible hintWrapper overlay — otherwise it intercepts the drag
    disable_hint_overlay(page)

    ALIGN_OK = 8   # ball must land within this many px of the ring to count as a real solve

    static_streak = 0
    for attempt in range(1, max_retries + 1):
        print(f"\n🔄 Captcha Attempt {attempt}/{max_retries}")

        # If the success popup is already up, the captcha was solved -> done.
        if registration_succeeded(page):
            print("✅ Registration success popup detected — captcha solved!")
            return True

        # If a 'Server error' popup is up, close it and wait for a fresh captcha.
        if close_server_error(page):
            time.sleep(1.0)
            if not wait_for_captcha(page, timeout=20):
                print("❌ No fresh captcha appeared after server error — failing")
                return False
            continue

        if not page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')"):
            # Canvas vanished BEFORE we did anything this attempt.
            if attempt == 1:
                print("ℹ️ No captcha canvas — nothing to solve")
                return True
            # On later attempts this means the popup closed/timed out WITHOUT us
            # actually solving it — that is NOT a success.
            print("⚠️ Captcha popup closed without an aligned solve — NOT solved")
            return False

        # Don't detect on a blank canvas
        blank_deadline = time.time() + 10
        while time.time() < blank_deadline and canvas_is_blank(page):
            print("   ⏳ Canvas blank, waiting for render...")
            time.sleep(0.6)

        disable_hint_overlay(page)   # every time (the popup may re-render)

        info = analyze_captcha(page)
        print(f"📊 {json.dumps(info)}")

        if info.get('blueX') is None:
            print("⚠️ Blue button not detected — trying from center")
            info['blueX'] = info.get('canvasW', 315) / 2
            info['blueY'] = info.get('canvasH', 300) * 0.86

        scale_x = canvas_box['width'] / info['canvasW']
        scale_y = canvas_box['height'] / info['canvasH']

        outcome, best_err = drag_calibrated(page, canvas_box, scale_x, scale_y, info)
        time.sleep(2.0)

        canvas_present = page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')")
        result = check_solved(page)
        print(f"   → drag={outcome}  result={result}  best_err={best_err:.0f}  canvas={'yes' if canvas_present else 'no'}")

        # The success popup ("THANKS FOR THE REGISTRATION!") appears 5-10s AFTER a
        # correct solve. After a clean drag (ball aligned + canvas gone) poll for it.
        if (not canvas_present) and best_err <= ALIGN_OK:
            print("✅ Ball aligned + canvas gone — waiting for the success popup...")
            for _ in range(12):
                if registration_succeeded(page):
                    print("✅ Confirmed solved (registration success popup)!")
                    return True
                if close_server_error(page):
                    break   # server error instead -> fall through to fresh captcha
                time.sleep(1.0)
            else:
                # No popup and no error within the wait window — the aligned solve
                # (canvas gone) still counts as success.
                print("✅ Confirmed solved (ball was aligned)!")
                return True
            # Broke out due to a server error -> wait for a fresh captcha.
            time.sleep(1.0)
            if not wait_for_captcha(page, timeout=20):
                print("❌ No fresh captcha appeared after server error — failing")
                return False
            continue

        # Canvas gone but we did NOT align -> success popup, server error, or timeout.
        # Wait for a fresh captcha and keep trying.
        if not canvas_present:
            # A correct solve may still have produced the success popup.
            for _ in range(8):
                if registration_succeeded(page):
                    print("✅ Confirmed solved (registration success popup)!")
                    return True
                time.sleep(1.0)
            print("⚠️ Canvas gone but ball was NOT aligned — popup closed, waiting for a fresh one...")
            close_server_error(page)
            close_any_error_dialog(page)
            time.sleep(1.0)
            if not wait_for_captcha(page, timeout=15):
                print("❌ No fresh captcha appeared — failing this registration attempt")
                return False
            continue

        # Slider not engaging at all -> after 3 statics try the pointer-event fallback.
        if outcome == 'static':
            static_streak += 1
            if static_streak == 3:
                print("\n⚠️ Mouse-drag isn't moving the slider — trying POINTER-EVENT drag...")
                if drag_via_pointer_events(page):
                    time.sleep(2.5)
                    if not page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')"):
                        print("✅ Solved via pointer-event drag!")
                        return True
            if static_streak >= 5:
                print("❌ Slider won't respond by any method — aborting.")
                return False
        else:
            static_streak = 0

        close_server_error(page)
        close_any_error_dialog(page)
        time.sleep(1.0)
        wait_for_captcha(page, timeout=15)

    return False

# ================= REGISTER =================

def click_register_and_handle(page):
    for attempt in range(1, MAX_REGISTRATION_RETRIES + 1):
        print(f"\n📤 Register attempt {attempt}/{MAX_REGISTRATION_RETRIES}")

        reg_selectors = [
            'button:has-text("REGISTER")',
            'button.ui-button:has-text("REGISTER")',
            'button[type="submit"]',
        ]
        clicked = False
        for sel in reg_selectors:
            try:
                el = page.wait_for_selector(sel, timeout=100000)
                if el and el.is_visible():
                    el.click()
                    clicked = True
                    print(f"✅ REGISTER clicked")
                    break
            except:
                continue

        if not clicked:
            print("❌ REGISTER button not found!")
            return False

        time.sleep(random.uniform(2, 4))

        # The captcha popup appears a few seconds AFTER clicking REGISTER. Over a
        # residential proxy this can be slow, so poll generously (up to 45s) and also
        # accept the swal2 popup as a sign the captcha is on its way.
        print("⏳ Waiting for captcha popup (up to 45s)...")
        captcha_appeared = False
        appear_deadline = time.time() + 45
        while time.time() < appear_deadline:
            try:
                has_canvas = page.evaluate("() => !!document.querySelector('#huntCaptcha canvas')")
                has_popup  = page.evaluate("() => !!document.querySelector('#huntCaptcha, .s-swal2-captcha-popup')")
            except Exception:
                has_canvas, has_popup = False, False
            if has_canvas:
                captcha_appeared = True
                break
            if has_popup:
                print("   …captcha popup detected, waiting for canvas to render…")
            remaining = int(appear_deadline - time.time())
            if remaining % 5 == 0:
                print(f"   …still waiting ({remaining}s left)…")
            time.sleep(1.0)

        if captcha_appeared:
            print("🎮 Captcha appeared — solving...")
            solved = retry_captcha(page, max_retries=12)
            if not solved:
                print("❌ Captcha solve failed — retrying registration")
                close_any_error_dialog(page)
                time.sleep(2)
                continue
        else:
            print("ℹ️ No captcha appeared within 45s — assuming direct registration")

        print("✅ Registration done!")
        return True

    return False

# ================= MAIN =================

def run(visit_no=None):
    print("=== StreakAds Registration Bot (Geonode SOCKS5 via local bridge) ===\n")

    # Start the local HTTP->SOCKS5 bridge; Playwright connects to the local HTTP side.
    bridge = start_proxy_bridge()
    proxy = {"server": f"http://{LOCAL_BRIDGE_HOST}:{LOCAL_BRIDGE_PORT}"}

    success = False
    success_shot = None
    try:
      with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=False,
            proxy=proxy,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                # Force HTTP/1.1 — proxied HTTP/2 can cause ERR_RESPONSE_HEADERS_TRUNCATED.
                '--disable-http2',
                '--disable-quic',
            ]
        )

        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        try:
            # Residential proxies are flaky on the first hit — retry the navigation a few times.
            print(f"🌐 Opening: {TARGET_URL}")
            last_err = None
            for nav_try in range(1, 5):
                try:
                    page.goto(TARGET_URL, timeout=100000, wait_until="commit")
                    page.wait_for_load_state("domcontentloaded", timeout=100000)
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    print(f"⚠️ Navigation attempt {nav_try}/4 failed: {str(e).splitlines()[0]}")
                    time.sleep(random.uniform(3, 6))
            if last_err:
                raise last_err
            time.sleep(random.uniform(3, 6))

            print("🔍 Looking for 'One-click'...")
            el = page.wait_for_selector('span.registration-tabs__caption:has-text("One-click")', timeout=100000)
            el.click()
            print("✅ 'One-click' clicked!")
            time.sleep(random.uniform(3, 5))

            success = click_register_and_handle(page)

            if success:
                print("\n🎉 Registration complete!")
                # The "THANKS FOR THE REGISTRATION!" popup shows 5-10s after a solve.
                # Wait for it, then screenshot it and remember the file path for the log.
                for _ in range(12):
                    if registration_succeeded(page):
                        break
                    time.sleep(1.0)
                shot = f"success_visit_{visit_no}.png" if visit_no else "success.png"
                try:
                    page.screenshot(path=shot)
                    success_shot = os.path.abspath(shot)
                    print(f"📸 Saved success screenshot: {success_shot}")
                except Exception:
                    success_shot = None
            else:
                print("\n❌ Registration failed.")
                page.screenshot(path="failed.png")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            try:
                page.screenshot(path="error.png")
            except:
                pass
        finally:
            browser.close()
            print("✅ Browser closed.")
    finally:
        # Stop the local proxy bridge
        try:
            bridge.terminate()
            print("🧹 Proxy bridge stopped.")
        except Exception:
            pass

    return success, success_shot

def run_campaign():
    """Run `run()` TOTAL_VISITS times, count solved vs failed, and write a .log summary."""
    import datetime

    def _log(msg):
        line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
        print(line)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    solved = 0
    failed = 0
    _log(f"===== Campaign start: {TOTAL_VISITS} visit(s) =====")
    for visit in range(1, TOTAL_VISITS + 1):
        _log(f"----- Visit {visit}/{TOTAL_VISITS} -----")
        shot = None
        try:
            ok, shot = run(visit)
        except Exception as e:
            ok = False
            _log(f"Visit {visit} crashed: {e}")
        if ok:
            solved += 1
            _log(f"Visit {visit}: SUCCESS (captcha solved) | screenshot: {shot or 'N/A'}")
        else:
            failed += 1
            _log(f"Visit {visit}: FAILED (captcha not solved)")
        _log(f"Running total -> success: {solved}, failed: {failed}")

    _log(f"===== Campaign done: {solved} success / {failed} failed out of {TOTAL_VISITS} =====")

if __name__ == "__main__":
    run_campaign()