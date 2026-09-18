# import asyncio
# import random
# import logging
# import gspread
# from datetime import datetime
# from google.oauth2.service_account import Credentials
# from playwright.async_api import async_playwright

# # ====================== LOGGING SETUP ======================
# log_filename = f"magzter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     handlers=[
#         logging.FileHandler(log_filename, encoding="utf-8"),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # ====================== GOOGLE SHEETS CONFIG ======================
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
# SHEET_NAME     = "readfile"

# SCOPES = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive"
# ]

# # ====================== GOOGLE SHEET HELPERS ======================
# def get_sheet():
#     creds  = Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=SCOPES)
#     client = gspread.authorize(creds)
#     sheet  = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
#     return sheet

# def fetch_pending_rows(sheet):
#     records = sheet.get_all_records()
#     headers = sheet.row_values(1)
#     txn_col = headers.index("Transaction_ID") + 1

#     pending = []
#     for i, record in enumerate(records):
#         row_index = i + 2
#         txn_val   = str(record.get("Transaction_ID", "")).strip()
#         email_val = str(record.get("Email", "")).strip()
#         if email_val and not txn_val:
#             pending.append({
#                 "row_index" : row_index,
#                 "email"     : email_val,
#                 "password"  : str(record.get("Password", "")).strip(),
#                 "name"      : str(record.get("Name_Used", "")).strip(),
#                 "txn_col"   : txn_col
#             })
#     return pending

# def update_transaction_id(sheet, row_index, txn_col, transaction_id):
#     sheet.update_cell(row_index, txn_col, transaction_id)
#     logger.info(f"[Sheet] Transaction ID updated at row {row_index}: {transaction_id}")

# # ====================== POPUP DISMISS ======================
# async def dismiss_popups(page):
#     close_selectors = [
#         'button.close-btn',
#         'button.jsx-a5473e9fc229b582.close-btn',
#         'img[alt="Close"]',
#         '#tooltipOkBtnD',
#         'button.tooltip-ok',
#         '[aria-label="Close"]',
#         '[aria-label="close"]',
#         'button:has-text("Okay")',
#         'button:has-text("OK")',
#     ]
#     for selector in close_selectors:
#         try:
#             btn = page.locator(selector).first
#             if await btn.is_visible():
#                 await btn.click()
#                 logger.info(f"[Popup] Dismissed: {selector}")
#                 await page.wait_for_timeout(300)
#         except:
#             pass

# async def auto_dismiss_loop(page, stop_event):
#     while not stop_event.is_set():
#         try:
#             await dismiss_popups(page)
#             await asyncio.sleep(1)
#         except:
#             if stop_event.is_set():
#                 break
#             await asyncio.sleep(1)

# # ====================== BROWSER FACTORY ======================
# async def create_browser(playwright):
#     browser = await playwright.chromium.launch(
#         headless=False,
#         args=['--start-maximized', '--disable-blink-features=AutomationControlled']
#     )
#     context = await browser.new_context(
#         viewport={"width": 1440, "height": 900},
#         user_agent=(
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/120.0.0.0 Safari/537.36"
#         )
#     )
#     return browser, context

# # ====================== PROCESS ONE ACCOUNT ======================
# async def process_account(playwright, row_data, sheet):
#     email     = row_data["email"]
#     password  = row_data["password"]
#     name      = row_data["name"]
#     row_index = row_data["row_index"]
#     txn_col   = row_data["txn_col"]

#     logger.info(f"\n{'='*60}")
#     logger.info(f"[Account] Processing: {email}")
#     logger.info(f"{'='*60}")

#     browser, context = await create_browser(playwright)
#     orders_page = None
#     reader_tasks = []

#     try:
#         # ===== Step 1: Open Login Page =====
#         logger.info("[Step 1] Opening Magzter login page...")
#         page = await context.new_page()
#         await page.goto("https://www.magzter.com/login/email", wait_until="domcontentloaded", timeout=60000)
#         await page.wait_for_timeout(2000)

#         # ===== Step 2-6: Account Creation =====
#         await page.fill('#user-email', email)
#         logger.info(f"[Step 2] Email filled: {email}")
#         await page.click('#continue_btn')
#         await page.wait_for_timeout(3000)

#         await page.fill('#inp_box', name)
#         await page.fill('input[name="password"]', password)
#         await page.click('button[type="submit"].max-width')
#         logger.info("[Step 6] Account creation submitted")
#         await page.wait_for_timeout(5000)

#         # ===== Step 7: Orders Page =====
#         orders_page = await context.new_page()
#         await orders_page.goto("https://www.magzter.com/dashboard/my_orders", wait_until="domcontentloaded", timeout=60000)
#         await orders_page.wait_for_timeout(3000)

#         # ===== Step 8-9: Transaction ID =====
#         transaction_id = "NOT_FOUND"
#         try:
#             await orders_page.wait_for_selector('td[data-title="Transaction ID"]', timeout=10000)
#             transaction_id = (await orders_page.inner_text('td[data-title="Transaction ID"]')).strip()
#             logger.info(f"[Step 8] Transaction ID: {transaction_id}")
#         except Exception as e:
#             logger.warning(f"[Step 8] Transaction ID not found: {e}")

#         update_transaction_id(sheet, row_index, txn_col, transaction_id)

#         # ===== Step 10: Gold Purchase Page =====
#         await orders_page.goto("https://www.magzter.com/dashboard/purchase/gold", wait_until="domcontentloaded", timeout=60000)
#         await orders_page.wait_for_timeout(3000)

#         # ===== Step 11: Explore Now =====
#         await orders_page.evaluate("window.scrollBy(0, 400)")
#         await orders_page.wait_for_timeout(1000)
#         try:
#             explore_buttons = await orders_page.locator('a[href="/magztergold/publications"] button.blue_transparent_btn').all()
#             if explore_buttons:
#                 await random.choice(explore_buttons).click()
#             else:
#                 await orders_page.click('a[href="/magztergold/publications"] button.blue_transparent_btn')
#             logger.info("[Step 11] Explore Now clicked")
#         except Exception as e:
#             logger.warning(f"[Step 11] Explore Now error: {e}")

#         await orders_page.wait_for_timeout(4000)

#         # ====================== UPDATED: 2 TO 5 RANDOM BOOKS + PAGINATION ======================
#         num_books = random.randint(2, 5)
#         logger.info(f"[Updated] Will read {num_books} random books (3-4 pages each with pagination)")

#         current_page = 1

#         for book_num in range(1, num_books + 1):
#             logger.info(f"[Book {book_num}/{num_books}] Selecting random magazine...")

#             # Pagination Logic - Har 1-2 books ke baad Next page try karo
#             if book_num > 1 and random.random() < 0.6:  # 60% chance to go next page
#                 try:
#                     logger.info(f"[Pagination] Trying to go to next page...")
#                     next_btn = orders_page.locator('a.pagination-previous.svelte-1rpew09[aria-label="Next"], a[aria-label="Next"]')
#                     if await next_btn.count() > 0 and await next_btn.is_visible():
#                         await next_btn.click()
#                         await orders_page.wait_for_timeout(5000)
#                         current_page += 1
#                         logger.info(f"[Pagination] Moved to page {current_page}")
#                     else:
#                         logger.info("[Pagination] Next button not found or not visible")
#                 except Exception as e:
#                     logger.warning(f"[Pagination] Error: {e}")

#             # Select Random Magazine
#             try:
#                 await orders_page.wait_for_selector('li.magazines-list a.magazines-anchor', timeout=10000)
#                 magazines = await orders_page.locator('li.magazines-list a.magazines-anchor').all()
#                 if not magazines:
#                     logger.warning("No magazines found, trying pagination...")
#                     await orders_page.locator('a.pagination-previous.svelte-1rpew09[aria-label="Next"]').click()
#                     await orders_page.wait_for_timeout(4000)
#                     magazines = await orders_page.locator('li.magazines-list a.magazines-anchor').all()

#                 random_mag = random.choice(magazines)
#                 mag_name = await random_mag.get_attribute('data-magname')
#                 logger.info(f"[Book {book_num}] Magazine selected: {mag_name}")
#                 await random_mag.scroll_into_view_if_needed()
#                 await orders_page.wait_for_timeout(800)
#                 await random_mag.click()
#                 await orders_page.wait_for_timeout(4000)
#             except Exception as e:
#                 logger.warning(f"[Book {book_num}] Magazine select error: {e}")
#                 continue

#             # Click Read Now
#             logger.info(f"[Book {book_num}] Clicking Read Now...")
#             try:
#                 await orders_page.wait_for_selector('#reader', timeout=10000)
#                 await orders_page.click('#reader')
#                 logger.info(f"[Book {book_num}] Read Now clicked")
#             except Exception as e:
#                 logger.warning(f"[Book {book_num}] Read Now error: {e}")
#                 continue

#             await orders_page.wait_for_timeout(4000)

#             # Find Reader Page
#             reader_page = None
#             for p_obj in context.pages:
#                 if "reader.magzter.com" in p_obj.url:
#                     reader_page = p_obj
#                     break
#             if not reader_page:
#                 reader_page = orders_page

#             # Auto dismiss task
#             reader_stop = asyncio.Event()
#             reader_task = asyncio.create_task(auto_dismiss_loop(reader_page, reader_stop))
#             reader_tasks.append((reader_task, reader_stop))

#             # Dismiss Okay popup
#             try:
#                 await reader_page.wait_for_selector('button:has-text("Okay"), .tooltip-ok, #tooltipOkBtnD', timeout=8000)
#                 okay_btn = reader_page.locator('button:has-text("Okay"), .tooltip-ok, #tooltipOkBtnD').first
#                 if await okay_btn.is_visible():
#                     await okay_btn.click()
#                 await reader_page.wait_for_timeout(1000)
#             except:
#                 pass

#             # Read 3-4 pages
#             pages_to_read = random.randint(3, 4)
#             logger.info(f"[Book {book_num}] Reading {pages_to_read} pages (5-15s wait)")

#             next_selectors = [
#                 'div.pagination-previous-icon.svelte-1rpew09',
#                 'div.right img[alt="next page"]',
#                 '.right img[alt="next page"]',
#                 'img[alt="next page"]',
#             ]

#             next_selector = None
#             for sel in next_selectors:
#                 try:
#                     await reader_page.wait_for_selector(sel, timeout=5000)
#                     next_selector = sel
#                     logger.info(f"[Book {book_num}] Using next selector: {sel}")
#                     break
#                 except:
#                     continue

#             if next_selector:
#                 consecutive_failures = 0
#                 for i in range(pages_to_read):
#                     await dismiss_popups(reader_page)
#                     try:
#                         await reader_page.click(next_selector, timeout=8000)
#                         consecutive_failures = 0
#                         wait_sec = random.randint(5, 15)
#                         logger.info(f"[Book {book_num}] Page {i + 1}/{pages_to_read} turned | Waiting {wait_sec}s...")
#                         await reader_page.wait_for_timeout(wait_sec * 1000)
#                     except Exception as e:
#                         consecutive_failures += 1
#                         logger.warning(f"[Book {book_num}] Page turn failed: {e}")
#                         if consecutive_failures >= 3:
#                             break
#                         await reader_page.wait_for_timeout(5000)
#             else:
#                 logger.warning(f"[Book {book_num}] Next button not found")

#             # Clean up reader task
#             reader_stop.set()
#             try:
#                 await asyncio.wait_for(reader_task, timeout=5)
#             except:
#                 pass

#             # Go back to publications list
#             if book_num < num_books:
#                 try:
#                     await reader_page.goto("https://www.magzter.com/magztergold/publications",
#                                          wait_until="domcontentloaded", timeout=60000)
#                     await reader_page.wait_for_timeout(4000)
#                 except:
#                     pass

#         logger.info(f"[Done] Account processed successfully: {email}")

#     except Exception as e:
#         logger.error(f"[Error] Account {email} failed: {e}")
#         import traceback
#         traceback.print_exc()
#     finally:
#         for task, stop_event in reader_tasks:
#             stop_event.set()
#             if not task.done():
#                 try:
#                     await asyncio.wait_for(task, timeout=3)
#                 except:
#                     pass

#         logger.info(f"[Session] Closing browser for: {email}")
#         await browser.close()
#         logger.info(f"[Session] Browser closed for: {email}")

# # ====================== MAIN ======================
# async def main():
#     logger.info("[Start] Connecting to Google Sheet...")
#     sheet   = get_sheet()
#     pending = fetch_pending_rows(sheet)

#     if not pending:
#         logger.info("[Info] No pending rows found in sheet.")
#         return

#     logger.info(f"[Info] {len(pending)} pending account(s) found. Starting automation...")

#     async with async_playwright() as playwright:
#         for row_data in pending:
#             await process_account(playwright, row_data, sheet)
#             remaining = fetch_pending_rows(sheet)
#             logger.info(f"[Info] {len(remaining)} account(s) remaining\n")
#             await asyncio.sleep(3)

#     logger.info("[Complete] All accounts processed successfully.")
#     logger.info(f"[Log] Full log saved to: {log_filename}")

# asyncio.run(main())


import asyncio
import random
import logging
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from playwright.async_api import async_playwright

# ====================== LOGGING SETUP ======================
log_filename = f"magzter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ====================== GOOGLE SHEETS CONFIG ======================
GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "gmblinks",
    "private_key_id": "CHANGE_ME_KEY_ID",
    "private_key": "-----BEGIN PRIVATE KEY-----
CHANGE_ME_ROTATE_THIS_KEY
-----END PRIVATE KEY-----\n",
    "client_email": "test@example.com",
    "client_id": "0000000000",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "CHANGE_ME_TOKEN",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/marcadeo-tech%40gmblinks.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

SPREADSHEET_ID = "1usY7UmsiGCIHcDAJoBuHNJWtScSzNhMVhr6nqnpegUU"
SHEET_NAME     = "readfile"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ====================== GOOGLE SHEET HELPERS ======================
def get_sheet():
    creds  = Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet  = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    return sheet

def fetch_pending_rows(sheet):
    records = sheet.get_all_records()
    headers = sheet.row_values(1)
    txn_col = headers.index("Transaction_ID") + 1

    pending = []
    for i, record in enumerate(records):
        row_index = i + 2
        txn_val   = str(record.get("Transaction_ID", "")).strip()
        email_val = str(record.get("Email", "")).strip()
        if email_val and not txn_val:
            pending.append({
                "row_index" : row_index,
                "email"     : email_val,
                "password"  : str(record.get("Password", "")).strip(),
                "name"      : str(record.get("Name_Used", "")).strip(),
                "txn_col"   : txn_col
            })
    return pending

def update_transaction_id(sheet, row_index, txn_col, transaction_id):
    sheet.update_cell(row_index, txn_col, transaction_id)
    logger.info(f"[Sheet] Transaction ID updated at row {row_index}: {transaction_id}")

# ====================== POPUP DISMISS ======================
async def dismiss_popups(page):
    close_selectors = [
        'button.close-btn',
        'button.jsx-a5473e9fc229b582.close-btn',
        'img[alt="Close"]',
        '#tooltipOkBtnD',
        'button.tooltip-ok',
        '[aria-label="Close"]',
        '[aria-label="close"]',
        'button:has-text("Okay")',
        'button:has-text("OK")',
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

# ====================== BROWSER FACTORY ======================
async def create_browser(playwright):
    browser = await playwright.chromium.launch(
        headless=False,
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
    return browser, context

# ====================== PROCESS ONE ACCOUNT ======================
async def process_account(playwright, row_data, sheet):
    email     = row_data["email"]
    password  = row_data["password"]
    name      = row_data["name"]
    row_index = row_data["row_index"]
    txn_col   = row_data["txn_col"]

    logger.info(f"\n{'='*60}")
    logger.info(f"[Account] Processing: {email}")
    logger.info(f"{'='*60}")

    browser, context = await create_browser(playwright)
    orders_page = None
    reader_tasks = []

    try:
        # ===== Step 1: Open Login Page =====
        logger.info("[Step 1] Opening Magzter login page...")
        page = await context.new_page()
        await page.goto("https://www.magzter.com/login/email", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        # ===== Step 2-6: Account Creation =====
        await page.fill('#user-email', email)
        logger.info(f"[Step 2] Email filled: {email}")
        await page.click('#continue_btn')
        await page.wait_for_timeout(3000)

        await page.fill('#inp_box', name)
        await page.fill('input[name="password"]', password)
        await page.click('button[type="submit"].max-width')
        logger.info("[Step 6] Account creation submitted")
        await page.wait_for_timeout(5000)

        # ===== Step 7: Orders Page =====
        orders_page = await context.new_page()
        await orders_page.goto("https://www.magzter.com/dashboard/my_orders", wait_until="domcontentloaded", timeout=60000)
        await orders_page.wait_for_timeout(3000)

        # ===== Step 8-9: Transaction ID =====
        transaction_id = "NOT_FOUND"
        try:
            await orders_page.wait_for_selector('td[data-title="Transaction ID"]', timeout=10000)
            transaction_id = (await orders_page.inner_text('td[data-title="Transaction ID"]')).strip()
            logger.info(f"[Step 8] Transaction ID: {transaction_id}")
        except Exception as e:
            logger.warning(f"[Step 8] Transaction ID not found: {e}")

        update_transaction_id(sheet, row_index, txn_col, transaction_id)

        # ===== Step 10: Gold Purchase Page =====
        await orders_page.goto("https://www.magzter.com/dashboard/purchase/gold", wait_until="domcontentloaded", timeout=60000)
        await orders_page.wait_for_timeout(3000)

        # ===== Step 11: Explore Now =====
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

        # ====================== 2 TO 5 RANDOM BOOKS + PAGINATION ======================
        num_books = random.randint(2, 5)
        logger.info(f"[Updated] Will read {num_books} random books (3-4 pages each with pagination)")

        current_page = 1

        for book_num in range(1, num_books + 1):
            try:   # ← Book level try-except for resilience
                logger.info(f"[Book {book_num}/{num_books}] Selecting random magazine...")

                # Pagination Logic
                if book_num > 1 and random.random() < 0.65:
                    try:
                        logger.info(f"[Pagination] Trying to go to next page...")
                        next_btn = orders_page.locator('a.pagination-previous.svelte-1rpew09[aria-label="Next"], a[aria-label="Next"]')
                        if await next_btn.count() > 0 and await next_btn.is_visible(timeout=3000):
                            await next_btn.click()
                            await orders_page.wait_for_timeout(5000)
                            current_page += 1
                            logger.info(f"[Pagination] Moved to page {current_page}")
                    except Exception as e:
                        logger.warning(f"[Pagination] Could not move to next page: {e}")

                # Select Random Magazine
                await orders_page.wait_for_selector('li.magazines-list a.magazines-anchor', timeout=12000)
                magazines = await orders_page.locator('li.magazines-list a.magazines-anchor').all()
                
                if not magazines:
                    logger.warning("No magazines found, trying pagination...")
                    try:
                        await orders_page.locator('a.pagination-previous.svelte-1rpew09[aria-label="Next"]').click()
                        await orders_page.wait_for_timeout(5000)
                        magazines = await orders_page.locator('li.magazines-list a.magazines-anchor').all()
                    except:
                        pass

                if magazines:
                    random_mag = random.choice(magazines)
                    mag_name = await random_mag.get_attribute('data-magname')
                    logger.info(f"[Book {book_num}] Magazine selected: {mag_name}")
                    await random_mag.scroll_into_view_if_needed()
                    await orders_page.wait_for_timeout(800)
                    await random_mag.click()
                    await orders_page.wait_for_timeout(4000)
                else:
                    logger.warning(f"[Book {book_num}] No magazines available, skipping book")
                    continue

                # Click Read Now
                logger.info(f"[Book {book_num}] Clicking Read Now...")
                await orders_page.wait_for_selector('#reader', timeout=10000)
                await orders_page.click('#reader')
                logger.info(f"[Book {book_num}] Read Now clicked")
                await orders_page.wait_for_timeout(4000)

                # Find Reader Page
                reader_page = None
                for p_obj in context.pages:
                    if "reader.magzter.com" in p_obj.url:
                        reader_page = p_obj
                        break
                if not reader_page:
                    reader_page = orders_page

                # Auto dismiss task
                reader_stop = asyncio.Event()
                reader_task = asyncio.create_task(auto_dismiss_loop(reader_page, reader_stop))
                reader_tasks.append((reader_task, reader_stop))

                # Dismiss Okay popup
                try:
                    await reader_page.wait_for_selector('button:has-text("Okay"), .tooltip-ok, #tooltipOkBtnD', timeout=8000)
                    okay_btn = reader_page.locator('button:has-text("Okay"), .tooltip-ok, #tooltipOkBtnD').first
                    if await okay_btn.is_visible():
                        await okay_btn.click()
                    await reader_page.wait_for_timeout(1000)
                except:
                    pass

                # Read 3-4 pages
                pages_to_read = random.randint(3, 4)
                logger.info(f"[Book {book_num}] Reading {pages_to_read} pages (5-15s wait)")

                next_selectors = [
                    'div.pagination-previous-icon.svelte-1rpew09',
                    'div.right img[alt="next page"]',
                    '.right img[alt="next page"]',
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
                    consecutive_failures = 0
                    for i in range(pages_to_read):
                        await dismiss_popups(reader_page)
                        try:
                            await reader_page.click(next_selector, timeout=8000)
                            consecutive_failures = 0
                            wait_sec = random.randint(5, 15)
                            logger.info(f"[Book {book_num}] Page {i + 1}/{pages_to_read} turned | Waiting {wait_sec}s...")
                            await reader_page.wait_for_timeout(wait_sec * 1000)
                        except Exception as e:
                            consecutive_failures += 1
                            logger.warning(f"[Book {book_num}] Page turn failed: {e}")
                            if consecutive_failures >= 3:
                                logger.warning(f"[Book {book_num}] Too many failures, skipping remaining pages")
                                break
                            await reader_page.wait_for_timeout(5000)
                else:
                    logger.warning(f"[Book {book_num}] Next button not found")

                # Clean up reader task
                reader_stop.set()
                try:
                    await asyncio.wait_for(reader_task, timeout=5)
                except:
                    pass

            except Exception as book_error:
                logger.warning(f"[Book {book_num}] Failed due to error: {book_error}. Moving to next book or account.")
                continue   # Move to next book instead of failing whole account

            # Go back to publications list for next book
            if book_num < num_books:
                try:
                    await reader_page.goto("https://www.magzter.com/magztergold/publications",
                                         wait_until="domcontentloaded", timeout=60000)
                    await reader_page.wait_for_timeout(4000)
                except:
                    pass

        logger.info(f"[Done] Account processed successfully: {email}")

    except Exception as e:
        logger.error(f"[Critical Error] Account {email} failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup all reader tasks
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
    logger.info("[Start] Connecting to Google Sheet...")
    sheet   = get_sheet()
    pending = fetch_pending_rows(sheet)

    if not pending:
        logger.info("[Info] No pending rows found in sheet.")
        return

    logger.info(f"[Info] {len(pending)} pending account(s) found. Starting automation...")

    async with async_playwright() as playwright:
        for row_data in pending:
            await process_account(playwright, row_data, sheet)
            remaining = fetch_pending_rows(sheet)
            logger.info(f"[Info] {len(remaining)} account(s) remaining\n")
            await asyncio.sleep(3)

    logger.info("[Complete] All accounts processed successfully.")
    logger.info(f"[Log] Full log saved to: {log_filename}")

asyncio.run(main())