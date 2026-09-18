#!/usr/bin/env python3
"""make_accounts_wf.py -- account banao WATERFOX se, Geonode proxy ke saath.

Kyun alag script: `make_accounts.py` Chrome (Playwright) se account banati hai,
jabki order `place_order.py` Waterfox se lagti hai. Chrome me bani session ka
login Waterfox me restore nahi hota -- `_shopify_essential` (Shopify ka asli
session cookie) wahan tik hi nahi paata. Isliye ab account bhi usi browser aur
usi IP se banaya jaata hai jisse aage order lagega. Ek hi browser, ek hi IP,
ek hi profile -- transfer ka sawal hi nahi.

Rasta wahi hai jo make_accounts.py ka tha (naap kar mila hua):
    /account/login  ->  Shiprocket ka popup (iframe) me 10 ank ka mobile
    OTP ke khaane   ->  provider se SMS OTP  ->  bhar do
    "Enter your email" -> apna pata -> Continue
    login -> session file

CHALANA
    python make_accounts_wf.py                 # 1 account
    python make_accounts_wf.py --count 3
    python make_accounts_wf.py --no-proxy      # bina proxy (sirf jaanch ke liye)
"""
import os
import re
import csv
import sys
import json
import time
import random
import argparse

import otpd
import place_order as po      # Waterfox launcher + Scope/frames/el_* wahin se
import sheet_log              # Google Sheet me row-by-row likhne wala

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Sab kuch place_order se -- exe me __file__ temp folder hota hai, isliye wahi
# frozen-aware HERE dono jagah chalta hai (sessions/CSV exe ke bagal me).
HERE = po.HERE
OUT = po.OUT
SESSIONS = po.SESSIONS
LEDGER = os.path.join(HERE, "accounts.csv")

URL = "https://estuaryworld.com/account/login?return_url=%2Faccount"
ACCOUNT_URL = "https://estuaryworld.com/account"
POPUP = "shiprocketLogin"

MOBILE = "9999999999"
LOGIN_BTN = "span.Login_inputAddonRight__ptvZb"
OTP_BOX = "input[autocomplete='one-time-code']"
EMAIL_BOX = ("input#email, input[name='email'], input[type='email'], "
             "input[placeholder*='mail']")
CONTINUE = ("button.loginPopupPrimaryButton, button:has-text('Continue'), "
            "button[type='submit']")
NAME_BOX = "input#name, input[name='name'], input[placeholder*='name']"

EMAIL_DOMAIN = "test@example.com"
FIRST = ["aarav", "ishan", "rohit", "nikhil", "sahil", "varun", "kabir", "arjun",
         "manish", "rahul", "vikas", "priya", "neha", "swati", "megha", "pooja",
         "anjali", "kiran", "deepak", "amit", "suresh", "ritu", "sneha", "karan"]
LAST = ["sharma", "verma", "gupta", "singh", "yadav", "mehta", "joshi", "pandey",
        "tiwari", "chauhan", "kumar", "mishra", "shukla", "dubey", "rathore"]

for _d in (OUT, SESSIONS):
    os.makedirs(_d, exist_ok=True)

log = po.log


def new_email():
    sep = random.choice([".", "_", ""])
    local = sep.join([random.choice(FIRST), random.choice(LAST)]) + str(
        random.randint(100, 99999))
    return "%s@%s" % (re.sub(r"[^a-z0-9._]", "", local), EMAIL_DOMAIN)


# ---------------------------------------------------------------- popup
def popup_frame(page, secs=30):
    """Shiprocket ka login popup -- apne iframe me chalta hai, panne par nahi.

    Har kadam par frame naya ban sakta hai, isliye har baar taaza dhoondha
    jaata hai; purana pakad kar rakhna galti hai.
    """
    end = time.time() + secs
    while time.time() < end:
        for f in po.frames(page):
            u = f.url or ""
            if POPUP in u or "fastrr-boost-ui.pickrr.com" in u:
                try:
                    if f.count(MOBILE):
                        return f
                except Exception:
                    continue
        page.wait_for_timeout(1000)
    return None


def live_popup(page):
    for f in po.frames(page):
        if POPUP in (f.url or ""):
            return f
    return None


def boxes_gone(f):
    try:
        return f.count(OTP_BOX) == 0
    except Exception:
        return True          # frame hi chala gaya = aage badh gaya


def fill_otp(f, page, code):
    """OTP ke khaane. Aakhri ank padte hi popup KHUD submit karta hai aur khaane
    hata deta hai -- isliye "khaane gayab" ko kaamyaabi maana jaata hai."""
    try:
        n = f.count(OTP_BOX)
    except Exception:
        n = 0
    if not n:
        return False

    els = f.query(OTP_BOX)
    f.use()
    try:
        els[0].click()
    except Exception:
        pass
    # ek ek ank -- khaane khud aage badhte hain
    from selenium.webdriver.common.action_chains import ActionChains
    for ch in code:
        ActionChains(f.d).send_keys(ch).perform()
        time.sleep(0.15)
    page.wait_for_timeout(3000)
    if boxes_gone(f):
        return True

    # na chala to har khaane me alag alag
    try:
        els = f.query(OTP_BOX)
        for i, ch in enumerate(code[:len(els)]):
            po.el_fill(f, els[i], ch)
            page.wait_for_timeout(300)
    except Exception:
        pass
    page.wait_for_timeout(3000)
    return boxes_gone(f)


def do_email(page, email, secs=30):
    """OTP ke baad ka "Enter your email" -- popup me bhi ho sakta hai, panne par bhi."""
    end = time.time() + secs
    while time.time() < end:
        for scope in (live_popup(page), page):
            if scope is None:
                continue
            el = scope.visible_first(EMAIL_BOX)
            if el is None:
                continue
            log("      email ka khaana mila")
            po.el_fill(scope, el, "")
            po.el_type(scope, el, email, delay=60)
            page.wait_for_timeout(900)

            nm_el = scope.visible_first(NAME_BOX)
            if nm_el is not None:
                nm = email.split("@")[0].split(".")[0].split("_")[0].capitalize()
                po.el_fill(scope, nm_el, nm)
                page.wait_for_timeout(400)

            btn = scope.visible_first(CONTINUE)
            if btn is not None:
                # Continue tab tak bujha rehta hai jab tak email theek na ho --
                # bujhe button par click chup-chaap kuch nahi karta.
                for _ in range(10):
                    try:
                        if btn.is_enabled():
                            break
                    except Exception:
                        break
                    page.wait_for_timeout(500)
                po.scroll_click(scope, btn)
            else:
                from selenium.webdriver.common.keys import Keys
                scope.use()
                el.send_keys(Keys.ENTER)
            page.wait_for_timeout(7000)
            return True
        page.wait_for_timeout(1000)
    return False


def logged_in(page):
    """Login hua ya nahi. Shopify khud batata hai -- customerId. Wahi sabse
    pakka saboot hai; shabd dhoondhna dhila tareeka tha."""
    try:
        cid = page.evaluate(
            "return (window.__st && __st.cid) || (window.ShopifyAnalytics &&"
            " ShopifyAnalytics.meta && ShopifyAnalytics.meta.page &&"
            " ShopifyAnalytics.meta.page.customerId) || null;")
    except Exception:
        cid = None
    if cid:
        return True, str(cid)
    try:
        url = page.url or ""
        txt = (page.body_text() or "").lower()
    except Exception:
        url, txt = "", ""
    if "/account" in url and "login" not in url:
        return True, ""
    if any(w in txt for w in ("logout", "log out", "my orders")):
        return True, ""
    return False, ""


# ---------------------------------------------------------------- ek account
def one_account(h, email, proxy_port, tag, log=log):
    """(ok, note, session_file, sms_aaya, customer_id)"""
    got_sms = False
    ok, note, sfile, cid = False, "", "", ""
    driver = None
    try:
        driver = po.launch_waterfox(proxy_port=proxy_port)
        page = po.Scope(driver, driver.current_window_handle)

        page.goto(URL, timeout=120)
        page.wait_for_timeout(6000)

        f = popup_frame(page)
        if not f:
            note = "login ka popup nahi aaya"
            page.screenshot(os.path.join(OUT, "%s_fail_popup.png" % tag))
            return ok, note, sfile, got_sms, cid

        log("      number: %s" % h["phone"])
        el = f.first(MOBILE)
        po.el_fill(f, el, "")
        po.el_type(f, el, h["phone"], delay=90)
        page.wait_for_timeout(1200)

        # das ank bharte hi popup khud aage badh jaata hai; na badhe to Login dabao
        end = time.time() + 10
        while time.time() < end and boxes_gone(f):
            page.wait_for_timeout(1000)
        if boxes_gone(f):
            b = f.visible_first(LOGIN_BTN)
            if b is not None:
                po.scroll_click(f, b)
            end = time.time() + 40
            while time.time() < end and boxes_gone(f):
                page.wait_for_timeout(1000)
        if boxes_gone(f):
            note = "OTP ka panna nahi aaya"
            page.screenshot(os.path.join(OUT, "%s_fail_otpscreen.png" % tag))
            return ok, note, sfile, got_sms, cid

        code = otpd.get_otp(h, log=lambda m: log("      " + m))
        if not code:
            note = "SMS OTP nahi aaya"
            page.screenshot(os.path.join(OUT, "%s_fail_nootp.png" % tag))
            return ok, note, sfile, got_sms, cid
        got_sms = True
        log("      SMS OTP: %s" % code)

        if not fill_otp(f, page, code):
            note = "OTP khaanon me baitha nahi"
            page.screenshot(os.path.join(OUT, "%s_fail_otpfill.png" % tag))
            return ok, note, sfile, got_sms, cid
        page.wait_for_timeout(5000)

        log("      email: %s" % email)
        if not do_email(page, email):
            note = "email ka khaana nahi aaya"
        page.wait_for_timeout(4000)

        ok, cid = logged_in(page)
        if not ok:
            page.goto(ACCOUNT_URL, timeout=90)
            page.wait_for_timeout(5000)
            ok, cid = logged_in(page)
        log("      login: %s%s" % ("HAAN" if ok else "NAHI",
                                   ("  customerId=%s" % cid) if cid else ""))
        page.screenshot(os.path.join(OUT, "%s_done.png" % tag))
        if not ok and not note:
            note = "login sabit nahi hua"
    except Exception as e:
        note = "gadbad: %s" % str(e)[:140]
    finally:
        # SESSION SIRF KAAMYAB ACCOUNT KI BACHTI HAI.
        # Pehle har haal me bachti thi -- fail hui koshishon ki aadhi session
        # bhi. Un se koi kaam nahi nikalta (login hai hi nahi) aur wo
        # sessions/ me bhar kar `newest_session()` ko dhokha deti thi: order
        # wali script sabse nayi file uthati hai, aur wo ek nakaam session hoti.
        if driver is not None:
            if ok:
                try:
                    nm = "estuary_%s_%s.json" % (h["phone"], int(time.time()))
                    d = {"phone": h["phone"], "email": email,
                         "when": time.strftime("%Y-%m-%d %H:%M:%S"),
                         "logged_in": True, "customer_id": cid,
                         "browser": "waterfox", "proxy": bool(proxy_port),
                         "url": "", "state": {"cookies": [], "origins": []}}
                    if po.save_session(driver, d, os.path.join(SESSIONS, nm)):
                        sfile = nm
                    else:
                        ok = False
                        note = (note + " | session save nahi hui").strip(" |")
                except Exception as e:
                    ok = False
                    note = (note + " | session save nahi hui: %s"
                            % str(e)[:60]).strip(" |")
            else:
                log("      (fail -- session save nahi ki)")
            try:
                driver.quit()
            except Exception:
                pass
    return ok, note, sfile, got_sms, cid


def write_row(row):
    new = not os.path.exists(LEDGER)
    with open(LEDGER, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["created_at", "phone", "email", "logged_in",
                        "session_file", "note"])
        w.writerow(row)


def make_one(proxy_port, tries, n, sheet_on=True, sheet_id=None, sheet_tab=None,
             log=log, should_stop=None):
    """Ek account -- number badal kar `tries` baar tak. True/False.

    Sheet aur session SIRF kaamyaabi par. Fail koshish ka nishaan sirf
    accounts.csv me rehta hai (wo local bahi-khata hai, usme sab kuch rehna
    chahiye -- kya fail hua aur kyun, ye baad me kaam aata hai).
    """
    email = new_email()
    for t in range(1, tries + 1):
        if should_stop is not None and should_stop():
            log("   (rok diya gaya)")
            return False
        log("   koshish %d/%d" % (t, tries))
        h = otpd.buy()
        if not h:
            log("      koi number nahi mila")
            time.sleep(10)
            continue
        tag = "wf_acct%02d_try%d" % (n, t)
        ok, note, sfile, got_sms, cid = one_account(h, email, proxy_port, tag,
                                                    log=log)
        if not got_sms:
            # SMS aaya hi nahi -> number wapas, poora paisa wapas.
            otpd.cancel(h, log=lambda m: log("      " + m))

        banaya = time.strftime("%Y-%m-%d %H:%M:%S")
        write_row([banaya, h["phone"], email, "yes" if ok else "no", sfile,
                   (note + (" | customerId=%s" % cid if cid else "")).strip(" |")])

        if ok:
            # Sheet me sirf bane hue account jaate hain.
            if sheet_on:
                sheet_log.add_account(
                    h["phone"], email, sfile, created_at=banaya,
                    status="created", customer_id=cid, browser="waterfox",
                    proxy=bool(proxy_port), note="",
                    sheet_id=sheet_id, tab=sheet_tab, log=log)
            log("   BAN GAYA: %s / %s  (customerId=%s)"
                % (h["phone"], email, cid or "-"))
            return True

        log("   nahi bana: %s" % (note or "wajah darj nahi"))
        # agli koshish naye email se -- purana pata site par darj ho chuka
        # ho sakta hai, aur usi se dobara jaana nayi rukawat khadi karta hai
        email = new_email()
    return False


def run_batch(count, proxy_port=None, tries=3, sheet_on=True, sheet_id=None,
              sheet_tab=None, gap=(25, 55), log=log, should_stop=None,
              on_progress=None, max_rounds=None, max_lagataar_fail=10):
    """Jab tak `count` account BAN na jayen, chalte raho.

    Purana tareeka "count baar koshish karo" tha -- 10 maange to 10 koshish,
    aur 6 hi bante the. Ab ginti KAAMYAAB accounts ki hoti hai, koshishon ki
    nahi.

    Rukne ki teen wajah (warna paise yun hi jalte rahenge):
      * user ne Stop daba diya            -> should_stop()
      * lagataar itni koshish nakaam      -> max_lagataar_fail
      * itne round ho gaye                -> max_rounds (default: count * 4)
    """
    if max_rounds is None:
        max_rounds = max(count * 4, count + 5)

    bane = 0
    round_no = 0
    lagataar_fail = 0

    while bane < count:
        if should_stop is not None and should_stop():
            log("\n[STOP] user ne rok diya.")
            break
        if round_no >= max_rounds:
            log("\n[STOP] %d round ho gaye par %d/%d hi bane -- ruk rahe hain."
                % (round_no, bane, count))
            break
        if lagataar_fail >= max_lagataar_fail:
            log("\n[STOP] lagataar %d koshish nakaam -- ruk rahe hain. "
                "(number/site/proxy me dikkat ho sakti hai)" % lagataar_fail)
            break

        round_no += 1
        log("\n===== account %d/%d  (koshish round %d) ====="
            % (bane + 1, count, round_no))

        if make_one(proxy_port, tries, round_no, sheet_on=sheet_on,
                    sheet_id=sheet_id, sheet_tab=sheet_tab, log=log,
                    should_stop=should_stop):
            bane += 1
            lagataar_fail = 0
        else:
            lagataar_fail += 1

        if on_progress is not None:
            on_progress(bane, count, round_no)

        if bane < count and not (should_stop is not None and should_stop()):
            w = random.randint(*gap)
            log("   %ds ruk kar agla" % w)
            # ek saath sona theek nahi -- Stop dabane par turant ruke
            for _ in range(w):
                if should_stop is not None and should_stop():
                    break
                time.sleep(1)

    return bane, round_no


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--tries", type=int, default=2)
    ap.add_argument("--no-proxy", action="store_true",
                    help="bina proxy (default: Geonode India)")
    ap.add_argument("--proxy-country", default=po.GEONODE_COUNTRY)
    ap.add_argument("--gap", type=int, nargs=2, default=[25, 55])
    # ---- Google Sheet ----
    ap.add_argument("--no-sheet", action="store_true",
                    help="Sheet me row mat likho")
    ap.add_argument("--sheet-id", default=sheet_log.SHEET_ID)
    ap.add_argument("--sheet-tab", default=sheet_log.TAB)
    a = ap.parse_args()

    log("otpdoctor balance: %s" % otpd.balance())

    sheet_on = not a.no_sheet
    if sheet_on:
        ws, kahani = sheet_log.open_tab(a.sheet_id, a.sheet_tab)
        log("sheet : %s | tab '%s' -> %s" % (a.sheet_id[:22] + "...",
                                             a.sheet_tab, kahani))
        if ws is None:
            log("sheet : row nahi likhi jayengi (account phir bhi banenge)")
            sheet_on = False
    else:
        log("sheet : OFF")

    stop_bridge = None
    port = None
    if not a.no_proxy:
        user = po.geonode_username(a.proxy_country, sticky=False)
        log("proxy : Geonode country=%s | user=%s" % (a.proxy_country, user))
        port, stop_bridge = po.start_geonode_bridge(user)
        log("proxy : local bridge 127.0.0.1:%d" % port)
    else:
        log("proxy : OFF")

    bane, rounds = 0, 0
    try:
        bane, rounds = run_batch(a.count, proxy_port=port, tries=a.tries,
                                 sheet_on=sheet_on, sheet_id=a.sheet_id,
                                 sheet_tab=a.sheet_tab, gap=tuple(a.gap))
    finally:
        if stop_bridge is not None:
            stop_bridge.set()

    log("\n================ hisaab ================")
    log("   maange gaye : %d" % a.count)
    log("   ban gaye    : %d" % bane)
    log("   round lage  : %d" % rounds)
    log("   browser     : Waterfox%s" % ("" if a.no_proxy else " + Geonode proxy"))
    log("   balance ab  : %s" % otpd.balance())
    return 0 if bane >= a.count else 1


if __name__ == "__main__":
    sys.exit(main())
