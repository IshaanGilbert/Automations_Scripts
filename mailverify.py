# import time, random, json, os, sys, re
# import threading
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor, as_completed

# import gspread
# from google.oauth2.service_account import Credentials
# from playwright.sync_api import sync_playwright

# CONFIG_FILE = "config.json"
# CREDENTIALS_FILE = "google_credentials.json"
# SCREENSHOT_DIR = "eligibility_screenshots"

# GLOBAL_TIMEOUT = 180000
# NAVIGATION_TIMEOUT = 300000
# ELEMENT_WAIT = 120000
# RETRY_COUNT = 5

# os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# BATCH_SIZE = 5
# BATCH_WAIT = 10  # Wait between batches

# def load_config():
#     if os.path.exists(CONFIG_FILE):
#         with open(CONFIG_FILE, 'r') as f:
#             return json.loads(f.read().strip())
#     return {}

# config = load_config()

# SHEET_ID = None
# sheet_url = config.get("GOOGLE_SHEET_URL_OR_ID", "")
# if sheet_url:
#     match = re.search(r'/d/([a-zA-Z0-9\-_]+)', sheet_url)
#     if match: SHEET_ID = match.group(1)

# TARGET_URL = config.get("TARGET_URL", "https://app.adstracking.io/click?pid=3030&offer_id=20655")

# ELIGIBILITY_MSGS = [
#     "not eligible", "you are not eligible for this offer", "ineligible",
#     "not valid for this offer", "already redeemed", "already subscribed",
#     "already been used", "already claimed", "offer has expired",
#     "offer expired", "limit reached", "not available in your",
#     "offer is no longer", "not qualify", "sorry", "unavailable"
# ]
# worksheet = None
# sheet_lock = threading.Lock()

# def update_sheet_status(row, status, error=""):
#     global worksheet
#     if not worksheet: return
#     with sheet_lock:
#         try:
#             worksheet.update(f'D{row}', [[status]], value_input_option='USER_ENTERED')
#             worksheet.update(f'E{row}', [[error[:200]]], value_input_option='USER_ENTERED')
#         except: pass

# def ensure_headers():
#     global worksheet
#     try:
#         headers = worksheet.row_values(1)
#         updates = []
#         if len(headers) < 4 or headers[3] != 'Status':
#             updates.append({'range': 'D1', 'values': [['Status']]})
#         if len(headers) < 5 or headers[4] != 'Error':
#             updates.append({'range': 'E1', 'values': [['Error']]})
#         if updates:
#             worksheet.batch_update(updates)
#     except: pass

# def check_page_text(page, phrases):
#     try:
#         text = page.locator('body').inner_text(timeout=60000).lower()
#         for p in phrases:
#             if p in text: return p
#     except: pass
#     return None

# def check_single_email(task_data):
#     """
#     Check ONE email with its OWN browser.
#     Each call creates its own Playwright + browser + context.
#     This avoids greenlet thread conflicts.
#     """
#     email = task_data['email']
#     first_name = task_data.get('first_name', '')
#     last_name = task_data.get('last_name', '')
#     row = task_data['row']
    
#     if not first_name:
#         first_name = random.choice(["Rahul","Amit","Priya","Sneha","Vikas"])
#     if not last_name:
#         last_name = random.choice(["Sharma","Kumar","Verma","Singh","Gupta"])
    
#     result = {'email': email, 'row': row, 'status': 'UNKNOWN', 'error': ''}
    
#     update_sheet_status(row, "🔄 Checking", "")
    
#     pw = browser = context = page = None
    
#     try:
#         # Each thread creates its OWN Playwright instance
#         pw = sync_playwright().start()
#         browser = pw.chromium.launch(
#             headless=True,
#             args=[
#                 '--no-sandbox',
#                 '--disable-dev-shm-usage',
#                 '--disable-gpu',
#                 '--window-size=1366,768',
#                 '--disable-blink-features=AutomationControlled',
#                 '--disable-infobars',
#                 '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
#             ]
#         )
#         context = browser.new_context(
#             viewport={'width':1366,'height':768},
#             ignore_https_errors=True,
#             locale="en-US"
#         )
#         page = context.new_page()
        
#         # 1. Navigate
#         page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
#         time.sleep(3)
        
#         # 2. Claim
#         try: page.click('button:has-text("Claim Now")', timeout=60000)
#         except:
#             try: page.click('a.subscribe_a button', timeout=60000)
#             except: pass
#         time.sleep(2)
        
#         # 3. Check
#         elig = check_page_text(page, ELIGIBILITY_MSGS)
#         if elig:
#             result['status'] = '🚫 Not Eligible'
#             result['error'] = f"Claim: {elig[:100]}"
#             update_sheet_status(row, "🚫 Not Eligible", result['error'])
#             return result
        
#         # 4. Email
#         try: page.fill('input[type="email"]', email)
#         except: page.fill('input[name="email"]', email)
#         page.click('button:has-text("Continue")')
#         time.sleep(3)
        
#         # 5. Check
#         elig = check_page_text(page, ELIGIBILITY_MSGS)
#         if elig:
#             result['status'] = '🚫 Not Eligible'
#             result['error'] = f"Email: {elig[:100]}"
#             update_sheet_status(row, "🚫 Not Eligible", result['error'])
#             return result
        
#         # 6. Name
#         t0=time.time()
#         fill_with_retry(page,['#firstName','input[placeholder*="First Name" i]'],first_name)
#         fill_with_retry(page,['#lastName','input[placeholder*="Last Name" i]'],last_name)
#         page.click('#submitBtn')
#         time.sleep(random.uniform(8,12))
        
#         # 7. Check
#         elig = check_page_text(page, ELIGIBILITY_MSGS)
#         if elig:
#             result['status'] = '🚫 Not Eligible'
#             result['error'] = f"Name: {elig[:100]}"
#             update_sheet_status(row, "🚫 Not Eligible", result['error'])
#             return result
        
#         # 8. Payment page?
#         payment_found = False
#         for sel in ['#cardNumber','input[name="cardNumber"]','[data-testid="hosted-payment-submit-button"]']:
#             try:
#                 page.wait_for_selector(sel, timeout=60000)
#                 payment_found = True
#                 break
#             except: pass
        
#         if payment_found:
#             result['status'] = '✅ Eligible'
#             result['error'] = 'Payment page reached'
#             update_sheet_status(row, "✅ Eligible", "Payment page reached")
#             page.screenshot(path=f"{SCREENSHOT_DIR}/yes_{row}.png")
#         else:
#             result['status'] = '⚠️ Unknown'
#             result['error'] = 'No payment page'
#             update_sheet_status(row, "⚠️ Unknown", "No payment page")
        
#     except Exception as e:
#         result['status'] = '❌ Error'
#         result['error'] = str(e)[:200]
#         update_sheet_status(row, "❌ Error", str(e)[:200])
    
#     finally:
#         try:
#             if context: context.close()
#             if browser: browser.close()
#             if pw: pw.stop()
#         except: pass
    
#     return result

# def fill_with_retry(page,selectors,value,timeout=ELEMENT_WAIT//1000):
#     if isinstance(selectors,str): selectors=[selectors]
#     per = max(5000, (timeout*1000)//RETRY_COUNT)
#     for a in range(1,RETRY_COUNT+1):
#         for sel in selectors:
#             try:
#                 page.wait_for_selector(sel,timeout=per,state="visible")
#                 page.fill(sel,value)
#                 return True
#             except: pass
#         print(f"   ⏳ [fill] round {a}/{RETRY_COUNT} waiting: {selectors}",flush=True)
#         time.sleep(3)
#     try:
#         page.keyboard.press("Tab");time.sleep(1)
#         page.keyboard.type(value,delay=100)
#         return True
#     except: return False

# def get_emails_from_sheet():
#     global worksheet
#     if not SHEET_ID: return []
    
#     try:
#         creds = Credentials.from_service_account_file(
#             CREDENTIALS_FILE,
#             scopes=['https://www.googleapis.com/auth/spreadsheets']
#         )
#         client = gspread.authorize(creds)
#         sheet = client.open_by_key(SHEET_ID)
        
#         try: worksheet = sheet.worksheet("EmailTesting")
#         except: return []
        
#         ensure_headers()
#         all_values = worksheet.get_all_values()
#         if not all_values: return []
        
#         emails = []
#         for i, row in enumerate(all_values[1:], start=2):
#             if len(row) >= 1:
#                 email = str(row[0]).strip() if len(row) > 0 else ''
#                 first = str(row[1]).strip() if len(row) > 1 else ''
#                 last = str(row[2]).strip() if len(row) > 2 else ''
#                 status = str(row[3]).strip() if len(row) > 3 else ''
                
#                 if status and status != '':
#                     continue
                
#                 if email and '@' in email:
#                     emails.append({
#                         'row': i, 'email': email,
#                         'first_name': first, 'last_name': last
#                     })
        
#         return emails
    
#     except Exception as e:
#         print(f"❌ Sheet error: {e}")
#         return []

# def main():

#     emails = get_emails_from_sheet()
    
#     if not emails:
#         print("❌ No pending emails!")
#         return
    
#     total_batches = (len(emails) + BATCH_SIZE - 1) // BATCH_SIZE
    
#     print(f"\n📋 {len(emails)} emails | 📦 {total_batches} batches | ⚡ {BATCH_SIZE} parallel\n")
    
#     all_eligible = []
#     all_not_eligible = []
#     total_processed = 0
    
#     for batch_num in range(total_batches):
#         start_idx = batch_num * BATCH_SIZE
#         end_idx = min(start_idx + BATCH_SIZE, len(emails))
#         batch = emails[start_idx:end_idx]
        
#         print(f"\n{'='*50}")
#         print(f"📦 Batch {batch_num+1}/{total_batches} ({len(batch)} emails)")
#         print(f"{'='*50}")
        
#         # Process batch in parallel
#         with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
#             futures = {executor.submit(check_single_email, e): e for e in batch}
            
#             for future in as_completed(futures):
#                 result = future.result()
#                 total_processed += 1
                
#                 if 'Eligible' in result['status']:
#                     all_eligible.append(result)
#                 elif 'Not Eligible' in result['status']:
#                     all_not_eligible.append(result)
                
#                 icon = "✅" if "Eligible" in result['status'] else "❌"
#                 print(f"   {icon} {result['email']}: {result['status']}")
        
#         print(f"\n📊 {total_processed}/{len(emails)} | ✅{len(all_eligible)} 🚫{len(all_not_eligible)}")
        
#         # Wait between batches
#         if batch_num < total_batches - 1:
#             print(f"⏰ Next batch in {BATCH_WAIT}s...")
#             time.sleep(BATCH_WAIT)


# if __name__ == "__main__":
#     main()




import time, random, json, os, sys, re
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import gspread
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright

CONFIG_FILE = "config.json"
CREDENTIALS_FILE = "google_credentials.json"
SCREENSHOT_DIR = "eligibility_screenshots"

GLOBAL_TIMEOUT = 180000
NAVIGATION_TIMEOUT = 300000
ELEMENT_WAIT = 120000
RETRY_COUNT = 5

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

BATCH_SIZE = 5
BATCH_WAIT = 10  # Wait between batches

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.loads(f.read().strip())
    return {}

config = load_config()

SHEET_ID = None
sheet_url = config.get("GOOGLE_SHEET_URL_OR_ID", "")
if sheet_url:
    match = re.search(r'/d/([a-zA-Z0-9\-_]+)', sheet_url)
    if match: SHEET_ID = match.group(1)

TARGET_URL = config.get("TARGET_URL", "https://app.adstracking.io/click?pid=3030&offer_id=20655")

ELIGIBILITY_MSGS = [
    "not eligible", "you are not eligible for this offer", "ineligible",
    "not valid for this offer", "already redeemed", "already subscribed",
    "already been used", "already claimed", "offer has expired",
    "offer expired", "limit reached", "not available in your",
    "offer is no longer", "not qualify", "sorry", "unavailable"
]
worksheet = None
sheet_lock = threading.Lock()

def update_sheet_status(row, status, error=""):
    global worksheet
    if not worksheet: return
    with sheet_lock:
        try:
            worksheet.update(f'D{row}', [[status]], value_input_option='USER_ENTERED')
            worksheet.update(f'E{row}', [[error[:200]]], value_input_option='USER_ENTERED')
        except: pass

def ensure_headers():
    global worksheet
    try:
        headers = worksheet.row_values(1)
        updates = []
        if len(headers) < 4 or headers[3] != 'Status':
            updates.append({'range': 'D1', 'values': [['Status']]})
        if len(headers) < 5 or headers[4] != 'Error':
            updates.append({'range': 'E1', 'values': [['Error']]})
        if updates:
            worksheet.batch_update(updates)
    except: pass

def check_page_text(page, phrases):
    try:
        text = page.locator('body').inner_text(timeout=60000).lower()
        for p in phrases:
            if p in text: return p
    except: pass
    return None

def check_single_email(task_data):
    """
    Check ONE email with its OWN browser.
    Each call creates its own Playwright + browser + context.
    This avoids greenlet thread conflicts.
    """
    email = task_data['email']
    first_name = task_data.get('first_name', '')
    last_name = task_data.get('last_name', '')
    row = task_data['row']
    
    if not first_name:
        first_name = random.choice(["Rahul","Amit","Priya","Sneha","Vikas"])
    if not last_name:
        last_name = random.choice(["Sharma","Kumar","Verma","Singh","Gupta"])
    
    result = {'email': email, 'row': row, 'status': 'UNKNOWN', 'error': ''}
    
    update_sheet_status(row, "🔄 Checking", "")
    
    pw = browser = context = page = None
    
    try:
        # Each thread creates its OWN Playwright instance
        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1366,768',
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
            ]
        )
        context = browser.new_context(
            viewport={'width':1366,'height':768},
            ignore_https_errors=True,
            locale="en-US"
        )
        page = context.new_page()
        
        # 1. Navigate
        page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
        time.sleep(3)
        
        # 2. Claim
        try: page.click('button:has-text("Claim Now")', timeout=60000)
        except:
            try: page.click('a.subscribe_a button', timeout=60000)
            except: pass
        time.sleep(2)
        
        # 3. Check
        elig = check_page_text(page, ELIGIBILITY_MSGS)
        if elig:
            result['status'] = '🚫 Not Eligible'
            result['error'] = f"Claim: {elig[:100]}"
            update_sheet_status(row, "🚫 Not Eligible", result['error'])
            return result
        
        # 4. Email
        try: page.fill('input[type="email"]', email)
        except: page.fill('input[name="email"]', email)
        page.click('button:has-text("Continue")')
        time.sleep(3)
        
        # 5. Check
        elig = check_page_text(page, ELIGIBILITY_MSGS)
        if elig:
            result['status'] = '🚫 Not Eligible'
            result['error'] = f"Email: {elig[:100]}"
            update_sheet_status(row, "🚫 Not Eligible", result['error'])
            return result
        
        # 6. Name
        t0=time.time()
        fill_with_retry(page,['#firstName','input[placeholder*="First Name" i]'],first_name)
        fill_with_retry(page,['#lastName','input[placeholder*="Last Name" i]'],last_name)
        page.click('#submitBtn')
        time.sleep(random.uniform(8,12))
        
        # 7. Check
        elig = check_page_text(page, ELIGIBILITY_MSGS)
        if elig:
            result['status'] = '🚫 Not Eligible'
            result['error'] = f"Name: {elig[:100]}"
            update_sheet_status(row, "🚫 Not Eligible", result['error'])
            return result
        
        # 8. Payment page?
        payment_found = False
        for sel in ['#cardNumber','input[name="cardNumber"]','[data-testid="hosted-payment-submit-button"]']:
            try:
                page.wait_for_selector(sel, timeout=60000)
                payment_found = True
                break
            except: pass
        
        if payment_found:
            result['status'] = '✅ Eligible'
            result['error'] = 'Payment page reached'
            update_sheet_status(row, "✅ Eligible", "Payment page reached")
            page.screenshot(path=f"{SCREENSHOT_DIR}/yes_{row}.png")
        else:
            result['status'] = '⚠️ Unknown'
            result['error'] = 'No payment page'
            update_sheet_status(row, "⚠️ Unknown", "No payment page")
        
    except Exception as e:
        result['status'] = '❌ Error'
        result['error'] = str(e)[:200]
        update_sheet_status(row, "❌ Error", str(e)[:200])
    
    finally:
        try:
            if context: context.close()
            if browser: browser.close()
            if pw: pw.stop()
        except: pass
    
    return result

def fill_with_retry(page,selectors,value,timeout=ELEMENT_WAIT//1000):
    if isinstance(selectors,str): selectors=[selectors]
    per = max(5000, (timeout*1000)//RETRY_COUNT)
    for a in range(1,RETRY_COUNT+1):
        for sel in selectors:
            try:
                page.wait_for_selector(sel,timeout=per,state="visible")
                page.fill(sel,value)
                return True
            except: pass
        print(f"   ⏳ [fill] round {a}/{RETRY_COUNT} waiting: {selectors}",flush=True)
        time.sleep(3)
    try:
        page.keyboard.press("Tab");time.sleep(1)
        page.keyboard.type(value,delay=100)
        return True
    except: return False

def get_emails_from_sheet():
    global worksheet
    if not SHEET_ID: return []
    
    try:
        creds = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID)
        
        # ✅ config.json ke TASKS_SHEET se tab naam lo (default: "EmailTesting")
        try: worksheet = sheet.worksheet(config.get("TASKS_SHEET", "EmailTesting"))
        except: return []
        
        ensure_headers()
        all_values = worksheet.get_all_values()
        if not all_values: return []
        
        emails = []
        for i, row in enumerate(all_values[1:], start=2):
            if len(row) >= 1:
                email = str(row[0]).strip() if len(row) > 0 else ''
                first = str(row[1]).strip() if len(row) > 1 else ''
                last = str(row[2]).strip() if len(row) > 2 else ''
                status = str(row[3]).strip() if len(row) > 3 else ''
                
                if status and status != '':
                    continue
                
                if email and '@' in email:
                    emails.append({
                        'row': i, 'email': email,
                        'first_name': first, 'last_name': last
                    })
        
        return emails
    
    except Exception as e:
        print(f"❌ Sheet error: {e}")
        return []

def main():

    emails = get_emails_from_sheet()
    
    if not emails:
        print("❌ No pending emails!")
        return
    
    total_batches = (len(emails) + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\n📋 {len(emails)} emails | 📦 {total_batches} batches | ⚡ {BATCH_SIZE} parallel\n")
    
    all_eligible = []
    all_not_eligible =[]
    total_processed = 0
    
    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(emails))
        batch = emails[start_idx:end_idx]
        
        print(f"\n{'='*50}")
        print(f"📦 Batch {batch_num+1}/{total_batches} ({len(batch)} emails)")
        print(f"{'='*50}")
        
        # Process batch in parallel
        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            futures = {executor.submit(check_single_email, e): e for e in batch}
            
            for future in as_completed(futures):
                result = future.result()
                total_processed += 1
                
                if 'Eligible' in result['status']:
                    all_eligible.append(result)
                elif 'Not Eligible' in result['status']:
                    all_not_eligible.append(result)
                
                icon = "✅" if "Eligible" in result['status'] else "❌"
                print(f"   {icon} {result['email']}: {result['status']}")
        
        print(f"\n📊 {total_processed}/{len(emails)} | ✅{len(all_eligible)} 🚫{len(all_not_eligible)}")
        
        # Wait between batches
        if batch_num < total_batches - 1:
            print(f"⏰ Next batch in {BATCH_WAIT}s...")
            time.sleep(BATCH_WAIT)


if __name__ == "__main__":
    main()