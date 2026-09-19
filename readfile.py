import asyncio
import random
import logging
import argparse
import time
import json
import os
import socket
import struct
import threading
import gspread
from datetime import datetime

os.environ["TZ"] = "Asia/Calcutta"          # IST timestamps/logs
try: time.tzset()
except Exception: pass

from google.oauth2.service_account import Credentials
from playwright.async_api import async_playwright

# ====================== ARGUMENTS ======================
parser = argparse.ArgumentParser()
parser.add_argument('--instance', type=int, default=5)
parser.add_argument('--total-instances', type=int, default=5)
args = parser.parse_args()

INSTANCE_ID = args.instance
TOTAL_INSTANCES = args.total_instances

# ====================== LOGGING SETUP ======================
log_filename = f"read_i{INSTANCE_ID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ====================== CONFIG & CREDENTIALS ======================
CONFIG_FILE  = "config.json"

# 6 service accounts me load baant-te hain (Google ki 60-read/min/account limit todne ke liye).
# Instance number se round-robin: 1->creds1, 2->creds2 ... 6->creds6, 7->creds1 ...
NUM_ACCOUNTS = 6
_acct_num = ((INSTANCE_ID - 1) % NUM_ACCOUNTS) + 1
CREDENTIALS_FILE = f"creds{_acct_num}.json"
if not os.path.exists(CREDENTIALS_FILE):
    CREDENTIALS_FILE = "google_credentials.json"   # fallback (agar creds file na mile)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.loads(f.read().strip())
    return {}

config = load_config()

# Google credentials
with open(CREDENTIALS_FILE, 'r') as _cf:
    GOOGLE_CREDENTIALS = json.load(_cf)
logger.info(f"[Creds] Instance {INSTANCE_ID} -> {CREDENTIALS_FILE}")

# Sheet ID from config
import re as _re
_sheet_url = config.get("GOOGLE_SHEET_URL_OR_ID", "")
_sheet_match = _re.search(r'/d/([a-zA-Z0-9\-_]+)', _sheet_url)
SPREADSHEET_ID = _sheet_match.group(1) if _sheet_match else _sheet_url

SHEET_NAME = config.get("TASKS_SHEET", "readfile")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ====================== GOOGLE SHEET HELPERS ======================
def _api(fn, *a, **k):
    """Sheet API call ko 429 (rate limit) pe retry/backoff ke saath chalata hai - crash nahi hota."""
    delay = 5
    last = None
    for attempt in range(6):
        try:
            return fn(*a, **k)
        except gspread.exceptions.APIError as e:
            last = e
            if "429" in str(e) or "Quota exceeded" in str(e) or "RATE_LIMIT" in str(e):
                wait = delay + random.uniform(0, 4)
                logger.warning(f"[RateLimit] 429 - {wait:.0f}s wait (retry {attempt+1}/6)")
                time.sleep(wait)
                delay = min(delay * 2, 90)
                continue
            raise
    raise last

def get_sheet():
    creds  = Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet  = _api(lambda: client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME))
    return sheet

CLAIM_STALE_SECONDS = 1200
_fail_attempts = {}   # row_index -> kitni baar fail hua (3 ke baad FAILED mark)

def _claimable(val):
    val = (val or "").strip()
    if not val:
        return True
    if val.startswith("CLAIM:"):
        parts = val.split(":")
        try:
            return (time.time() - int(parts[2])) > CLAIM_STALE_SECONDS
        except Exception:
            return True
    return False

def fetch_pending_rows(sheet):
    all_values = _api(sheet.get_all_values)
    if not all_values:
        return []
    headers = all_values[0]
    if "Transaction_ID" not in headers:
        logger.error(f"[Sheet] '{SHEET_NAME}' has no 'Transaction_ID' column — cannot proceed.")
        return []

    txn_col     = headers.index("Transaction_ID") + 1
    is_read_col = headers.index("Is_Read") + 1 if "Is_Read" in headers else None
    dur_col     = headers.index("Duration_Sec") + 1 if "Duration_Sec" in headers else None
    date_col    = headers.index("Date") + 1 if "Date" in headers else None
    reason_col  = headers.index("Reason") + 1 if "Reason" in headers else None   # <-- NEW
    claim_col   = is_read_col or txn_col

    pending = []
    for i, row in enumerate(all_values[1:]):
        row_index = i + 2
        # ---- WORK PARTITION ----
        # Har instance sirf apni rows uthaye -> takrav/skip/duplicate khatam, full speed.
        # Instance 1 -> rows 1,61,121...  Instance 2 -> 2,62,122...  (row % total)
        if TOTAL_INSTANCES > 1 and (row_index % TOTAL_INSTANCES) != (INSTANCE_ID % TOTAL_INSTANCES):
            continue
        record    = dict(zip(headers, row))
        email_val = str(record.get("Email", "")).strip()
        txn_val   = str(record.get("Transaction_ID", "")).strip()
        claim_val = record.get("Is_Read", "") if is_read_col else record.get("Transaction_ID", "")

        if email_val and not txn_val and _claimable(claim_val):
            pending.append({
                "row_index"   : row_index,
                "email"       : email_val,
                "password"    : str(record.get("Password", "")).strip(),
                "name"        : str(record.get("Name_Used", "")).strip(),
                "txn_col"     : txn_col,
                "is_read_col" : is_read_col,
                "dur_col"     : dur_col,
                "date_col"    : date_col,
                "reason_col"  : reason_col,          # <-- NEW
                "claim_col"   : claim_col,
            })
    return pending

def update_reason(sheet, row_index, reason_col, reason_text):
    if reason_col:
        try:
            _api(sheet.update_cell, row_index, reason_col, reason_text)
            logger.info(f"[Sheet] Reason updated at row {row_index}: {reason_text}")
        except Exception as e:
            logger.warning(f"[Sheet] Failed to update Reason: {e}")

def claim_row(sheet, row_index, claim_col):
    token = f"CLAIM:{INSTANCE_ID}:{int(time.time())}"
    try:
        _api(sheet.update_cell, row_index, claim_col, token)
        time.sleep(0.7)
        current = str(_api(sheet.cell, row_index, claim_col).value or "").strip()
        if current == token:
            return True
        logger.info(f"[Claim] row {row_index} taken by another reader — skipping.")
        return False
    except Exception as e:
        logger.warning(f"[Claim] row {row_index} failed: {e}")
        return False

def update_transaction_id(sheet, row_index, txn_col, transaction_id):
    _api(sheet.update_cell, row_index, txn_col, transaction_id)
    logger.info(f"[Sheet] Transaction ID updated at row {row_index}: {transaction_id}")

def update_date(sheet, row_index, date_col, date_val):
    if date_col and date_val:
        try:
            _api(sheet.update_cell, row_index, date_col, date_val)
            logger.info(f"[Sheet] Date updated at row {row_index}: {date_val}")
        except Exception as e:
            logger.warning(f"[Sheet] Date update failed: {e}")

def mark_read_done(sheet, row_data, duration=None):
    try:
        if row_data.get("is_read_col"):
            _api(sheet.update_cell, row_data["row_index"], row_data["is_read_col"], "YES")
        if row_data.get("dur_col") and duration is not None:
            _api(sheet.update_cell, row_data["row_index"], row_data["dur_col"], str(round(duration, 1)))
        logger.info(f"[Sheet] row {row_data['row_index']} marked Is_Read=YES")
    except Exception as e:
        logger.warning(f"[Sheet] mark done failed: {e}")

# ====================== POPUP DISMISS ======================
async def dismiss_popups(page):
    close_selectors = [
        '#tooltipOkBtnD',
        'button.tooltip-ok',
        'button.jsx-a5473e9fc229b582.close-btn',
    ]
    for selector in close_selectors:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible():
                await btn.click()
                logger.info(f"[Popup] Dismissed: {selector}")
                await page.wait_for_timeout(300)
        except:
            pass

async def auto_dismiss_loop(page, stop_event):
    while not stop_event.is_set():
        try:
            await dismiss_popups(page)
            await asyncio.sleep(1)
        except:
            if stop_event.is_set():
                break
            await asyncio.sleep(1)

POPUP_KILL_JS = """
(function(){
  try {
    Object.defineProperty(window, 'clevertap', {
      configurable:true,
      get:function(){ return this.__ct; },
      set:function(nv){
        try { if (nv) { nv.notifications = nv.notifications || {}; nv.notifications.push = function(){}; } } catch(e){}
        this.__ct = nv;
      }
    });
  } catch(e){}
  try { if (window.Notification) { Notification.requestPermission = function(cb){ if(cb) cb('denied'); return Promise.resolve('denied'); }; } } catch(e){}
  function rm(){
    try { document.querySelectorAll('.wzrk-alert,.wzrk-overlay,.wzrk-backdrop,[id^="wzrk"],[class*="wzrk"]').forEach(function(el){ el.remove(); }); } catch(e){}
  }
  try { new MutationObserver(rm).observe(document.documentElement||document,{childList:true,subtree:true}); } catch(e){}
  document.addEventListener('DOMContentLoaded', rm);
  setInterval(rm, 800);
})();
"""

# ====================== BROWSER FACTORY ======================
async def create_browser(playwright):
    browser = await playwright.chromium.launch(
        headless=True,
        args=['--start-maximized', '--disable-blink-features=AutomationControlled']
    )
    context = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    )
    await context.add_init_script(POPUP_KILL_JS)
    return browser, context

# ====================== PROCESS ONE ACCOUNT ======================
async def process_account(playwright, row_data, sheet):
    email     = row_data["email"]
    password  = row_data["password"]
    name      = row_data["name"]
    row_index = row_data["row_index"]
    txn_col   = row_data["txn_col"]
    date_col  = row_data["date_col"]
    reason_col = row_data.get("reason_col")   # <-- NEW

    logger.info(f"\n{'='*60}")
    logger.info(f"[Account] Processing: {email}")
    logger.info(f"{'='*60}")

    t_start = time.time()
    browser, context = await create_browser(playwright)
    orders_page = None
    reader_tasks = []

    try:
        logger.info("[Step 1] Opening Magzter login page...")
        page = await context.new_page()
        await page.goto("https://www.magzter.com/login/email", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        async def _fill_first(selectors, value, label):
            for sel in selectors:
                try:
                    loc = page.locator(sel).first
                    if await loc.count() and await loc.is_visible():
                        await loc.fill(value)
                        return True
                except Exception:
                    pass
            logger.warning(f"[Login] {label} field not found")
            return False

        async def _click_first(selectors, label):
            for sel in selectors:
                try:
                    loc = page.locator(sel).first
                    if await loc.count() and await loc.is_visible() and await loc.is_enabled():
                        await loc.click()
                        return True
                except Exception:
                    pass
            logger.warning(f"[Login] {label} button not found")
            return False

        CONTINUE_BTNS = ['#continue_btn', 'button:has-text("Continue")',
                         'button[type="submit"].max-width', 'button[type="submit"]']

        await _fill_first(['#user-email-inp', 'input[name="mail"]', '#user-email',
                           'input[type="email"]'], email, "email")
        logger.info(f"[Step 2] Email filled: {email}")
        await _click_first(CONTINUE_BTNS, "email-continue")
        await page.wait_for_timeout(3500)
        await dismiss_popups(page)

        try:
            await page.wait_for_selector('#user-pass, input[name="pass"], input[type="password"]',
                                         state="visible", timeout=15000)
        except Exception:
            logger.warning("[Step 3] Password field did not appear after email Continue")

        await _fill_first(['#inp_box'], name, "name")
        filled_pw = await _fill_first(['#user-pass', 'input[name="pass"]',
                                       'input[name="password"]', 'input[type="password"]'],
                                      password, "password")
        if filled_pw:
            logger.info("[Step 3] Password filled")

        await _click_first(CONTINUE_BTNS, "password-continue")
        logger.info("[Step 4] Login submitted")
        await page.wait_for_timeout(6000)   # Wait for response

        # ==================== INVALID PASSWORD CHECK ====================
        invalid_selectors = [
            'text=incorrect password',
            'text=invalid password',
            'text=wrong password',
            '[class*="error"]',
            '.alert-danger',
            'div[role="alert"]',
            '#error-message',
            'text=Invalid credentials'
        ]

        is_invalid = False
        for sel in invalid_selectors:
            try:
                if await page.locator(sel).first.is_visible(timeout=3000):
                    is_invalid = True
                    break
            except:
                continue

        if is_invalid:
            logger.warning(f"[Login] Invalid Password for {email}")
            update_reason(sheet, row_index, reason_col, "invalid password")
            # Browser close kar ke next row pe jaayenge
            raise Exception("Invalid Password - Skipping further processing")

        # Agar password sahi hai to aage badho
        orders_page = await context.new_page()
        await orders_page.goto("https://www.magzter.com/dashboard/my_orders", wait_until="domcontentloaded", timeout=60000)
        await orders_page.wait_for_timeout(3000)

        # ===== Transaction ID + Date fetch =====
        transaction_id = "NOT_FOUND"
        transaction_date = ""
        try:
            await orders_page.wait_for_selector('td[data-title="Transaction ID"]', timeout=10000)
            transaction_id = (await orders_page.inner_text('td[data-title="Transaction ID"]')).strip()
            logger.info(f"[Step 8] Transaction ID: {transaction_id}")
        except Exception as e:
            logger.warning(f"[Step 8] Transaction ID not found: {e}")

        try:
            transaction_date = (await orders_page.inner_text('td[data-title="Date"]')).strip()
            logger.info(f"[Step 8] Transaction Date: {transaction_date}")
        except Exception as e:
            logger.warning(f"[Step 8] Transaction Date not found: {e}")

        update_transaction_id(sheet, row_index, txn_col, transaction_id)
        update_date(sheet, row_index, date_col, transaction_date)

        # ... (Baaki pura code same hai jaise pehle tha - books reading tak)

        await orders_page.goto("https://www.magzter.com/dashboard/purchase/gold", wait_until="domcontentloaded", timeout=60000)
        await orders_page.wait_for_timeout(3000)

        await orders_page.evaluate("window.scrollBy(0, 400)")
        await orders_page.wait_for_timeout(1000)

        try:
            explore_buttons = await orders_page.locator('a[href="/magztergold/publications"] button.blue_transparent_btn').all()
            if explore_buttons:
                await random.choice(explore_buttons).click()
            else:
                await orders_page.click('a[href="/magztergold/publications"] button.blue_transparent_btn')
            logger.info("[Step 11] Explore Now clicked")
        except Exception as e:
            logger.warning(f"[Step 11] Explore Now error: {e}")

        await orders_page.wait_for_timeout(4000)

        num_books = random.randint(2, 5)
        logger.info(f"[Updated] Will read {num_books} random books (3-4 pages each with pagination)")

        current_page = 1

        for book_num in range(1, num_books + 1):
            try:
                logger.info(f"[Book {book_num}/{num_books}] Selecting random magazine...")

                if book_num > 1 and random.random() < 0.65:
                    try:
                        next_btn = orders_page.locator('a.pagination-previous.svelte-1rpew09[aria-label="Next"], a[aria-label="Next"]')
                        if await next_btn.count() > 0 and await next_btn.first.is_visible():
                            await next_btn.click()
                            await orders_page.wait_for_timeout(5000)
                            current_page += 1
                    except:
                        pass

                await orders_page.wait_for_selector('li.magazines-list a.magazines-anchor', timeout=12000)
                magazines = await orders_page.locator('li.magazines-list a.magazines-anchor').all()

                if magazines:
                    random_mag = random.choice(magazines)
                    mag_name = await random_mag.get_attribute('data-magname')
                    logger.info(f"[Book {book_num}] Magazine selected: {mag_name}")
                    await random_mag.scroll_into_view_if_needed()
                    await orders_page.wait_for_timeout(800)
                    await random_mag.click()
                    await orders_page.wait_for_timeout(4000)
                else:
                    continue

                logger.info(f"[Book {book_num}] Clicking Read Now...")
                await orders_page.wait_for_selector('#reader', timeout=10000)
                await orders_page.click('#reader')
                await orders_page.wait_for_timeout(4000)

                reader_page = None
                for p_obj in context.pages:
                    if "reader.magzter.com" in p_obj.url:
                        reader_page = p_obj
                        break
                if not reader_page:
                    reader_page = orders_page

                reader_stop = asyncio.Event()
                reader_task = asyncio.create_task(auto_dismiss_loop(reader_page, reader_stop))
                reader_tasks.append((reader_task, reader_stop))

                pages_to_read = random.randint(3, 4)

                next_selectors = [
                    'div.pagination-previous-icon.svelte-1rpew09',
                    'div.right img[alt="next page"]',
                    'img[alt="next page"]',
                ]

                next_selector = None
                for sel in next_selectors:
                    try:
                        await reader_page.wait_for_selector(sel, timeout=5000)
                        next_selector = sel
                        break
                    except:
                        continue

                if next_selector:
                    for i in range(pages_to_read):
                        await dismiss_popups(reader_page)
                        try:
                            await reader_page.click(next_selector, timeout=8000)
                            wait_sec = random.randint(5, 15)
                            await reader_page.wait_for_timeout(wait_sec * 1000)
                        except:
                            break

                reader_stop.set()
                try:
                    await asyncio.wait_for(reader_task, timeout=5)
                except:
                    pass

            except Exception as book_error:
                logger.warning(f"[Book {book_num}] Failed: {book_error}")
                continue

            if book_num < num_books:
                try:
                    await reader_page.goto("https://www.magzter.com/magztergold/publications", wait_until="domcontentloaded", timeout=60000)
                    await reader_page.wait_for_timeout(4000)
                except:
                    pass

        mark_read_done(sheet, row_data, time.time() - t_start)
        logger.info(f"[Done] Account processed successfully: {email}")

    except Exception as e:
        err = str(e)
        logger.error(f"[Critical Error] Account {email} failed: {err}")
        import traceback
        traceback.print_exc()
        # ---- ROW ATAKNE SE BACHAO ----
        # Fail hone par claim release karo (turant retry ho) ya permanent-fail ko FAILED mark karo.
        try:
            rc = row_data.get("claim_col")
            ri = row_data["row_index"]
            if rc:
                if "Invalid Password" in err:
                    _api(sheet.update_cell, ri, rc, "FAILED")   # permanent - retry mat karo
                    logger.info(f"[Recover] row {ri} -> FAILED (invalid password)")
                else:
                    _fail_attempts[ri] = _fail_attempts.get(ri, 0) + 1
                    if _fail_attempts[ri] >= 3:
                        _api(sheet.update_cell, ri, rc, "FAILED")   # 3 baar fail -> chhodo
                        logger.info(f"[Recover] row {ri} -> FAILED (3 attempts)")
                    else:
                        _api(sheet.update_cell, ri, rc, "")          # claim release -> phir se pending
                        logger.info(f"[Recover] row {ri} claim released (retry {_fail_attempts[ri]}/3)")
        except Exception as ee:
            logger.warning(f"[Recover] cleanup failed: {ee}")
    finally:
        for task, stop_event in reader_tasks:
            stop_event.set()
            if not task.done():
                try:
                    await asyncio.wait_for(task, timeout=3)
                except:
                    pass

        logger.info(f"[Session] Closing browser for: {email}")
        await browser.close()
        logger.info(f"[Session] Browser closed for: {email}")

# ====================== MAIN ======================
async def main():
    logger.info(f"[Start] Reader instance {INSTANCE_ID} — connecting to Google Sheet...")
    sheet = get_sheet()

    PARALLEL_SESSIONS = 1

    async with async_playwright() as playwright:
        while True:
            pending = fetch_pending_rows(sheet)
            if not pending:
                logger.info(f"[Info] No pending rows left.")
                break

            claimed_rows = []
            for cand in pending:
                if len(claimed_rows) >= PARALLEL_SESSIONS:
                    break
                if claim_row(sheet, cand["row_index"], cand["claim_col"]):
                    claimed_rows.append(cand)
                    logger.info(f"[Info] Claimed row {cand['row_index']} ({cand['email']})")

            if not claimed_rows:
                logger.info(f"[Info] All visible rows claimed by others — done.")
                break

            logger.info(f"[Info] Starting {len(claimed_rows)} parallel sessions...")

            await asyncio.gather(
                *[process_account(playwright, row_data, sheet) for row_data in claimed_rows]
            )

            await asyncio.sleep(3)

    logger.info(f"[Complete] All sessions done.")
    logger.info(f"[Log] Full log saved to: {log_filename}")

asyncio.run(main())