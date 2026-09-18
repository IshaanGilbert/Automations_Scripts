#!/usr/bin/env python3
"""
Card generation (MasterCard smartdata portal) — fully dashboard-driven.

All inputs come from settings.json -> "card_generation" section (pushed by the
controller). No interactive input(): the OTP is
delivered by the dashboard, which writes BASE/card_otp.txt (POST /api/card_otp on
the node_agent). Runs under the slot's Xvfb display so an operator can also watch
via the Live (VNC) view.

Exit code: 0 on success, 1 on fatal error (so node_agent shows crashed vs done).
"""

import asyncio
import os
import sys
import json
import re
import threading
import time as _time
from datetime import datetime, timedelta
os.environ["TZ"] = "Asia/Calcutta"          # IST timestamps/logs
try: _time.tzset()
except Exception: pass
from playwright.async_api import async_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
OTP_FILE = os.path.join(BASE, "card_otp.txt")
# Dropped while the bot is waiting for the portal OTP; the node agent reports it so the
# dashboard / OTP app / WhatsApp alert know EXACTLY when an OTP is needed. Removed the
# moment the OTP arrives or the wait times out.
OTP_WANTED_FILE = os.path.join(BASE, "card_otp_wanted.txt")

# Prefer the shared loader; if settings_util.py wasn't copied to this server,
# fall back to reading the JSON files directly so the script still runs.
import db

try:
    from settings_util import load_settings
except Exception:
    def _ld(name):
        try:
            with open(os.path.join(BASE, name)) as f:
                return json.loads(f.read().strip())
        except Exception:
            return {}
    def load_settings(section):
        d = _ld("settings.json")
        s = d.get(section, {}) if isinstance(d, dict) else {}
        return s if isinstance(s, dict) else {}

# node_agent launches this with no_args=True (node_agent.py:90), so there is no
# instance number on argv. cards.ran_by only needs to identify the owner well enough
# for the stale-reset to spot an abandoned claim, so the PID serves — and unlike a
# fixed constant it stays distinct if two agents ever run at once.
INSTANCE_ID = os.getpid()

# ---- settings (dashboard-pushed) with safe fallbacks --------------------------
S = load_settings("card_generation")

LOG_FILE       = S.get("log_file") or "mastercard_card_logs.json"

# How many slots to claim per run. This is a BATCH SIZE, not the target — the target
# is the cards quota, which pre-provisioned the slots in the DB. The agent fills
# whatever it can claim and exits; node_agent relaunches it (run_once + singleton).
# How many slots to claim/fill in ONE login session. Default (0/unset) = DRAIN: fill EVERY
# waiting slot in one run, not just one card. (Regression: the old default of 1 generated a
# single card and, since card_generation is run-once, the agent never relaunched it — so the
# rest of the requested pool was never filled.)
BATCH_SIZE       = int(S.get("total_cards", 0) or 0) or 9999
MAX_AMOUNT       = int(S.get("max_amount", 5000) or 5000)
MIN_AMOUNT       = int(S.get("min_amount", 1) or 1)
MAX_TRANSACTIONS = int(S.get("max_transactions", 1) or 1)
# The MasterCard portal OTP stays valid ~15 min, so wait that long by default
# instead of abandoning the login after 3 min (settings can still override).
OTP_WAIT_SECONDS = int(S.get("otp_wait_seconds", 900) or 900)

# ── STALL WATCHDOG (buyer parity) ─────────────────────────────────────────────
# The buyer kills a hung instance so it can be auto-restarted; card-gen now does the
# same. `_progress` is refreshed at every real step (OTP poll, login, each card). If
# NOTHING advances for CARD_STALL_SECONDS the agent is hung — exit(2) so node_agent
# relaunches it AND reset_stale_card_slots frees the claimed slots for another run,
# instead of ~2000 cards sitting stuck in 'generating' forever.
CARD_STALL_SECONDS = int(S.get("card_stall_seconds", 300) or 300)
_progress = _time.time()

def _touch():
    global _progress
    _progress = _time.time()

def _stall_watchdog():
    while True:
        _time.sleep(10)
        if _time.time() - _progress > CARD_STALL_SECONDS:
            print(f"⛔ card-gen stalled >{CARD_STALL_SECONDS}s (hung) — exiting for "
                  f"auto-restart; claimed slots will be freed by stale-reset.", flush=True)
            os._exit(2)

# Login URL — matches the proven shweta_card (incl. the hostName param).
LOGIN_URL      = S.get("login_url") or ("https://smartdata.mastercard.co.in/static/public-portal-ui/"
                                        "login-signin-component?cobrandHost=mastercard"
                                        "&hostName=null%20(81587de2-b7ea-4621-65ee-f758)")
PORTAL_USER    = S.get("portal_username", "")
PORTAL_PASS    = S.get("portal_password", "")
# Cardholder details — taken from Settings (dashboard). NOTE: if any of these are
# left blank in Settings, the portal will not render the card panel (#cardNumberLabel
# stays hidden) and extraction fails — so keep them filled in Settings → Card generation.
CH_FIRST       = S.get("cardholder_first", "")
CH_LAST        = S.get("cardholder_last", "")
CH_EMAIL       = S.get("cardholder_email", "")
CH_PHONE       = S.get("cardholder_phone", "")
COUNTRY_CODE   = S.get("country_code", "India +91")
CARD_BIN       = S.get("card_bin", "")
CARD_NETWORK   = S.get("card_network", "")


def _expiry_dates():
    """Return (start, end) as dd/mm/yyyy from explicit overrides or offsets."""
    start = S.get("expiry_start_date", "").strip()
    end = S.get("expiry_end_date", "").strip()
    if start and end:
        return start, end
    today = datetime.now()
    s = today + timedelta(days=int(S.get("expiry_start_offset_days", 0) or 0))
    e = s + timedelta(days=int(S.get("expiry_days", 365) or 365))
    return s.strftime("%d/%m/%Y"), e.strftime("%d/%m/%Y")


# ====================== SAVE: DATABASE ======================
# Cards used to be append_row'd to a 'Carddetails' Google Sheet, which meant the
# card pool had no status, no idempotency, and a "count" you got by counting rows.
# The quota pre-provisions SLOTS in the DB; this agent fills them.
def save_card_to_db(card_id, card_data):
    """Put a real card number into the slot we claimed. Returns True on success."""
    ok = db.fill_card(
        card_id,
        card_data["card_number"],
        card_data["expiry_date"],
        card_data["cvc"],
        card_data.get("max_amount"),
    )
    if ok:
        masked = card_data["card_number"][:4] + "···" + card_data["card_number"][-4:]
        print(f"💾 Slot #{card_id} filled: {masked} | ₹{card_data['max_amount']}", flush=True)
    return ok


# ====================== LOGGING ======================
def save_to_log(card_data=None, error=None, status="success"):
    log_entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status": status}
    if card_data:
        log_entry.update({"card_number": card_data.get("card_number"),
                          "action": "Card Created Successfully"})
    if error:
        log_entry.update({"error": str(error), "action": "Error Occurred"})
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except Exception:
            logs = []
    else:
        logs = []
    logs.append(log_entry)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)
    print(f"📝 Log Saved: {status}")


# ====================== DATA CLEANING ======================
def clean_card_data(card_info, max_amount):
    if not card_info:
        return None
    card_number = re.sub(r'\D', '', card_info.get("card_number", ""))
    expiry_date = card_info.get("expiry_date", "").split(',')[0].strip()
    cvc = str(card_info.get("cvc", "")).strip()
    cleaned = {"card_number": card_number, "expiry_date": expiry_date,
               "cvc": cvc, "max_amount": max_amount}
    print(f"🧹 Cleaned -> Card: {card_number} | Expiry: {expiry_date} | CVC: {cvc} | Max: {max_amount}")
    return cleaned


# ====================== OTP (dashboard-delivered) ======================
async def wait_for_otp(timeout_s):
    """Poll BASE/card_otp.txt (written by the dashboard) for a 6-digit OTP."""
    try: os.remove(OTP_FILE)          # clear any stale OTP first
    except Exception: pass
    try:                              # signal "OTP needed" for the dashboard/app/WhatsApp
        with open(OTP_WANTED_FILE, "w") as f:
            f.write("waiting")
    except Exception: pass
    print(f"⏳ Waiting up to {timeout_s}s for OTP — dashboard se bhejo "
          f"(writes {os.path.basename(OTP_FILE)})...", flush=True)
    waited = 0
    try:
        while waited < timeout_s:
            try:
                if os.path.exists(OTP_FILE):
                    with open(OTP_FILE) as f:
                        val = re.sub(r'\D', '', f.read())
                    try: os.remove(OTP_FILE)
                    except Exception: pass
                    if len(val) >= 6:
                        print(f"✅ OTP received: {val[:6]}", flush=True)
                        return val[:6]
            except Exception:
                pass
            await asyncio.sleep(2)
            waited += 2
            _touch()          # waiting for the OTP is legitimate progress — don't let the
                              # stall-watchdog kill a bot that's correctly holding for the OTP
        return None
    finally:
        try: os.remove(OTP_WANTED_FILE)   # stop signalling once done/timed out
        except Exception: pass


# ====================== SURVEY BANNER DISMISS ======================
async def dismiss_survey_banner(page):
    try:
        await page.evaluate("""
            () => {
                const banners = document.querySelectorAll('.QSIInfoBar, [class*="QSIInfoBar"], [class*="SI_5hGHbb"]');
                banners.forEach(el => el.remove());
                document.querySelectorAll('div, section, aside').forEach(el => {
                    const style = window.getComputedStyle(el);
                    if ((style.position === 'fixed' || style.position === 'sticky') && parseInt(style.zIndex) > 100) {
                        el.remove();
                    }
                });
            }
        """)
        print("✅ Survey Banner Dismissed!")
    except Exception as e:
        print(f"⚠️ Banner dismiss warning: {e}")


# ====================== COUNTRY CODE FILL ======================
async def fill_country_code(page, code):
    try:
        country_input = page.locator('input[role="combobox"]').nth(2)
        await country_input.wait_for(state="visible", timeout=10000)
        await country_input.click()
        await page.wait_for_timeout(400)
        await country_input.press('Control+a')
        await page.wait_for_timeout(200)
        await country_input.press('Backspace')
        await page.wait_for_timeout(300)
        await country_input.type(code, delay=120)
        await page.wait_for_timeout(800)
        await country_input.press('Tab')
        await page.wait_for_timeout(500)
        value = await country_input.input_value()
        print(f"✅ Country Code Set: {value}")
        return True
    except Exception as e:
        print(f"❌ Country Code Fill Failed: {e}")
        return False


# ====================== EXTRACT CARD INFO ======================
async def extract_card_info(page):
    try:
        await page.wait_for_selector('#cardNumberLabel', timeout=15000)
        await page.wait_for_timeout(2000)
        card_number  = await page.input_value('#cardNumberLabel')
        expiry_date  = await page.input_value('#expireDateLabel')
        cvc          = await page.input_value('#cvcLabel')
        billing_name = await page.input_value('#billingNameLabel')
        print(f"\n💳 Raw Extracted: {card_number} | {expiry_date} | {cvc}")
        return {"card_number": card_number, "expiry_date": expiry_date,
                "cvc": cvc, "billing_name": billing_name}
    except Exception as e:
        print(f"❌ Card Info Extract Failed: {e}")
        return None


async def capture_failure(page, tag):
    """When the card panel never renders, save a screenshot + dump any visible
    portal error/validation text so we can see WHY the card was not created
    (can't inspect the live portal otherwise)."""
    try:
        path = os.path.join(BASE, f"cardfail_{tag}.png")
        await page.screenshot(path=path, full_page=True)
        print(f"   📸 failure screenshot: {path}", flush=True)
    except Exception as e:
        print(f"   (screenshot failed: {e})", flush=True)
    try:
        msgs = await page.evaluate("""() => {
            const out = [];
            document.querySelectorAll('[role=alert], .error, .gwt-Label, [class*=rror], [class*=alidation], [class*=warn], [class*=Warn]').forEach(e => {
                const t = (e.innerText || '').trim();
                if (t && t.length < 200) out.push(t);
            });
            return Array.from(new Set(out)).slice(0, 10);
        }""")
        if msgs:
            print("   ⚠️ portal messages: " + " | ".join(msgs), flush=True)
        else:
            print("   (no visible error text found — card likely just didn't submit)", flush=True)
    except Exception:
        pass


async def main():
    # Portal creds are decided AFTER claiming: a corp-tagged batch uses THAT corporate's
    # login (Corporates page); an untagged batch uses the global Settings login. So we do
    # not hard-fail here on missing global creds.

    # Buyer-style stall watchdog: if the agent hangs (e.g. the portal wedges after login),
    # exit so node_agent relaunches it and stale-reset frees the claimed slots — instead of
    # sitting stuck holding the whole batch in 'generating'.
    _touch()
    threading.Thread(target=_stall_watchdog, daemon=True).start()

    # Claim the slots BEFORE opening a browser. The cards quota decides how many cards
    # exist; this agent only fills slots that already exist. If none are waiting, there
    # is nothing to generate — exit without burning a portal login (each one costs an OTP).
    try:
        db.assert_db_ready()                 # reachable AND migrated (matches the buyers)
        db.reset_stale_card_slots()          # a previous crash may still hold slots
        claim = db.claim_card_slots(INSTANCE_ID, BATCH_SIZE)
    except Exception as e:
        print(f"❌ DB not reachable: {e}", flush=True)
        return 1

    SLOTS = claim.get("ids") or []
    CORP  = claim.get("corp_id")
    _login = claim.get("login") or {}
    # per-corp login wins; fall back to the global Settings login for untagged slots.
    USER = (_login.get("username") or PORTAL_USER or "").strip()
    PASS = (_login.get("password") or PORTAL_PASS or "").strip()

    if not SLOTS:
        print("💤 No card slots awaiting generation. Set a cards quota in the dashboard "
              "(Quotas → Cards) to pre-provision more.", flush=True)
        return 0

    if not USER or not PASS:
        where = f"Corporates → {CORP}" if CORP else "Settings → Card generation"
        print(f"❌ Portal login missing for {('corp ' + CORP) if CORP else 'untagged slots'} — "
              f"set it in {where}. Releasing the {len(SLOTS)} claimed slot(s).", flush=True)
        try: db.release_card_slots(SLOTS)
        except Exception: pass
        return 1

    print(f"🚀 {len(SLOTS)} slot(s) claimed{(' for corp ' + CORP) if CORP else ''}: {SLOTS} | "
          f"Max ₹{MAX_AMOUNT} | Max txns {MAX_TRANSACTIONS}", flush=True)
    start_date, end_date = _expiry_dates()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,                         # visible under Xvfb (Live view for OTP)
            args=['--start-maximized', '--disable-blink-features=AutomationControlled',
                  '--ignore-certificate-errors', '--ignore-certificate-errors-spki-list',
                  '--disable-web-security']
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            ignore_https_errors=True)
        page = await context.new_page()
        rc = 0
        try:
            print("🌐 Opening Login Page...")
            await page.goto(LOGIN_URL, timeout=90000, wait_until="domcontentloaded")

            try:
                await page.click('button[id*="onetrust-accept"]', timeout=5000)
            except Exception:
                await page.evaluate("""() => {
                    document.querySelectorAll('button').forEach(btn => {
                        if(btn.innerText && (btn.innerText.includes('Accept') || btn.innerText.includes('Allow'))) btn.click();
                    });
                }""")
            await page.wait_for_timeout(4000)

            await page.fill('input#loginUserID', USER)
            await page.fill('input#passwordControl', PASS)
            await page.click('button.primary', timeout=10000)

            print("⏳ Waiting for OTP Page...")
            await page.wait_for_timeout(7000)
            otp = await wait_for_otp(OTP_WAIT_SECONDS)
            if not otp or len(otp) != 6 or not otp.isdigit():
                print("❌ No valid OTP received in time.", flush=True)
                # Release the claimed slots immediately instead of leaving them stuck
                # in 'generating' until the 30-min stale-reset. The login OTP failed,
                # so NONE of this batch got filled yet.
                for _cid in SLOTS:
                    try: db.fail_card_slot(_cid, "login OTP timeout")
                    except Exception: pass
                return 1
            for i in range(6):
                await page.fill(f'#otp-input-{i}', otp[i])
                await page.wait_for_timeout(250)
            await page.click('button.primary', timeout=10000)
            print("✅ Login Successful!")
            _touch()

            # Post-login navigation — matches the PROVEN standalone flow (shweta_card).
            # The SSO redirect chain (loginactions.view -> webseal/login.do -> home)
            # can take 20-30s, so wait for the header iframe to actually EXIST before
            # clicking the menu, then use 15s clicks and wait for the form to appear.
            # (The old code clicked after a fixed ~11s and raced the redirect ->
            # "Payment Control" timeout -> crash -> relaunch = the login loop.)
            print("🔍 Waiting for portal home / header iframe...")
            await page.wait_for_timeout(6000)
            await page.wait_for_selector('iframe#smart-data-header-ui-iframe', timeout=30000)
            iframe = page.frame_locator('iframe#smart-data-header-ui-iframe')

            async def reach_form(tries=3):
                """Navigate to a fresh Create Single Request form, WITH RETRIES. Returns
                True on success, False after `tries` failures. Buyer-style resilience: a
                flaky SSO redirect / transient portal hiccup is RETRIED instead of crashing
                the session and stranding the whole claimed batch in 'generating'."""
                for _ in range(tries):
                    try:
                        _touch()
                        await dismiss_survey_banner(page)
                        await page.wait_for_timeout(800)
                        await iframe.locator('a:has-text("Payment Control")').click(timeout=15000, force=True)
                        await page.wait_for_timeout(1500)
                        await iframe.locator('a:has-text("Purchase Requests")').click(timeout=15000, force=True)
                        await page.wait_for_timeout(1500)
                        await iframe.locator('a:has-text("Create Single Request")').click(timeout=15000, force=True)
                        await page.wait_for_selector('#minimum-transaction-amount', timeout=20000)
                        return True
                    except Exception as e:
                        print(f"   ⚠️ form-nav attempt failed: {str(e)[:60]} — retrying…", flush=True)
                        try: await page.wait_for_timeout(2000)
                        except Exception: pass
                return False

            # INITIAL navigation to the form — WITH RETRIES (was a one-shot that raced the
            # SSO redirect → timeout → whole session crashed → batch stranded in 'generating').
            # Now, after a manual OTP login, the flow RETRIES its way to the form and carries
            # on; only if it truly can't reach the form do we release the batch for retry.
            if not await reach_form(tries=4):
                print("❌ Could not reach the request form after login — releasing this "
                      "batch back to the pool for retry.", flush=True)
                for _cid in SLOTS:
                    try: db.fail_card_slot(_cid, "form not reachable after login")
                    except Exception: pass
                return 1
            print("✅ Reached Create Single Request Form!")
            await page.wait_for_timeout(6000)

            made = 0
            for idx, card_id in enumerate(SLOTS, 1):
                print(f"\n{'='*50}\n🔄 Slot #{card_id}  ({idx} of {len(SLOTS)})\n{'='*50}")
                _touch()          # each card is forward progress — keeps the watchdog happy

                # Each card is isolated: one card's failure must NOT close the whole
                # session — release just that slot and carry on to the next.
                try:
                    await page.fill('#minimum-transaction-amount', str(MIN_AMOUNT))
                    await page.fill('#maximum-transaction-amount', str(MAX_AMOUNT))
                    await page.fill('#start-date', start_date)
                    await page.fill('#end-date', end_date)
                    await page.fill('#cumulativeColumnIdVCW', str(MAX_AMOUNT))
                    await page.fill('#maximumNumberOfTransactionIdVCW', str(MAX_TRANSACTIONS))
                    print("✅ Amount & Date Fields Filled!")

                    await page.fill('#userDetailsFirstNameTextBox', CH_FIRST)
                    await page.fill('#userDetailsLastNameTextBox', CH_LAST)
                    await page.evaluate("""(email) => {
                        const el = document.getElementById('userDetailsEmailAddressTextBox');
                        if (el) {
                            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            setter.call(el, email);
                            el.dispatchEvent(new Event('input',  { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }""", CH_EMAIL)
                    await fill_country_code(page, COUNTRY_CODE)
                    await page.fill('#userDetailsPhoneNumberTextBox', CH_PHONE)

                    if CARD_BIN or CARD_NETWORK:
                        print(f"ℹ️ BIN/network requested (bin={CARD_BIN!r}, network={CARD_NETWORK!r}).", flush=True)

                    print("🔘 Clicking Submit...")
                    await page.click('button#submitBtn1', timeout=15000)
                    await page.wait_for_timeout(4000)

                    card_info = await extract_card_info(page)
                    cleaned = clean_card_data(card_info, MAX_AMOUNT) if card_info else None
                    if cleaned and cleaned.get("card_number"):
                        # H4: a REAL card was created — if the slot is no longer ours (a stale-
                        # reset re-claimed it), fill_card returns False and the number would be
                        # LOST (and the slot could regenerate → a second charge). Never lose it:
                        # persist to the slot if we still own it, else to an orphan sink.
                        if save_card_to_db(card_id, cleaned):
                            save_to_log(card_data=cleaned, status="success")
                            made += 1
                            print(f"✅ Slot #{card_id} complete.")
                        else:
                            try:
                                with open(f"{BASE}/orphan_cards.jsonl", "a") as _of:
                                    _of.write(json.dumps(cleaned) + "\n")
                            except Exception:
                                pass
                            save_to_log(card_data=cleaned, status="orphan_saved")
                            print(f"⚠️ Slot #{card_id}: slot no longer 'generating' — real card "
                                  f"saved to orphan_cards.jsonl (not lost).", flush=True)
                    else:
                        await capture_failure(page, card_id)   # why did the panel stay hidden?
                        db.fail_card_slot(card_id, "portal returned no card details (card panel stayed hidden)")
                        print(f"⚠️ Slot #{card_id} released back to the pool.", flush=True)
                except Exception as e:
                    print(f"⚠️ Slot #{card_id} errored: {str(e)[:90]} — releasing, continuing.", flush=True)
                    try: db.fail_card_slot(card_id, f"card error: {str(e)[:120]}")
                    except Exception: pass

                # Re-reach the form for the NEXT card. If it can't recover, end the
                # session gracefully (release the rest for a later run) — don't crash.
                if idx < len(SLOTS):
                    if not await reach_form():
                        print("⚠️ Could not re-reach the form — ending this session; "
                              "remaining slots released for retry on the next run.", flush=True)
                        for cid in SLOTS[idx:]:
                            try: db.fail_card_slot(cid, "form navigation lost mid-batch")
                            except Exception: pass
                        break

            print(f"\n🎉 Batch done: {made}/{len(SLOTS)} card(s) created. Logs: {LOG_FILE}")

        except Exception as e:
            print(f"❌ Error: {e}")
            for _cid in SLOTS:
                try: db.fail_card_slot(_cid, f"agent crashed: {e}")
                except Exception: pass
            save_to_log(error=e, status="error")
            import traceback
            traceback.print_exc()
            rc = 1
        finally:
            await browser.close()
        return rc


if __name__ == "__main__":
    sys.exit(asyncio.run(main()) or 0)
