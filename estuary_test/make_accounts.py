#!/usr/bin/env python3
"""make_accounts.py -- estuaryworld.com par account banao. Ek hi script, bas.

CHALANA
-------
    python make_accounts.py                 # 1 account
    python make_accounts.py --count 10      # 10 account
    python make_accounts.py --count 10 --headless
    python make_accounts.py --count 5 --tries 4 --gap 40 70

Har account ka nateeja `accounts.csv` me likha jaata hai aur uski session
(cookies) `sessions/` me. Script kabhi bhi rok kar dobara chalayi ja sakti hai
-- ginti wahin se aage badhti hai, kyunki har account apni line khud likhta
hai.


RASTA (wahi jo aadmi haath se karta hai)
---------------------------------------
    /account/login  ->  popup me 10 ank ka mobile
    OTP ka panna (4 khaane)  ->  provider se SMS OTP  ->  bhar do
    "Enter your email"  ->  apna @buzzaro.in wala pata  ->  Continue
    login ho gaya  ->  session file me


CHAAR BAATEIN JO NAAP KAR MILI (andaze se nahi)
-----------------------------------------------
1. Login ka popup PANNE PAR NAHI hai. Wo Shiprocket ka widget hai jo apne
   iframe me chalta hai (`fastrr-boost-ui.pickrr.com`). Panne par `#mobile`
   dhoondhne par 0 mila, frame ke andar 1. Isliye har selector frame me.
2. Das ank bharte hi popup KHUD aage badh jaata hai -- "OTP sent to +91 ..."
   aa jaata hai aur Login wala button gayab ho jaata hai. Isliye pehle DEKHA
   jaata hai, phir click -- warna wo button dhoondhte hue run toot jaati hai.
3. Aakhri ank padte hi popup KHUD submit karta hai aur OTP ke khaane hata deta
   hai. Isliye "khaane gayab" ko kaamyaabi maana jaata hai; unhe wapas padhne
   jaana hi wo galti thi jisse pehli run tooti.
4. Jo number is waqt mil rahe hain wo "ALL (60 Seconds)" server ke hain -- SMS
   60 second me na aaye to provider KHUD number cancel kar deta hai (aur paisa
   wapas kar deta hai). Isliye ek account par kai number tak koshish hoti hai;
   ek number par ruk jaana matlab kismat par chhod dena.


PAISE KA KHYAAL
---------------
Har number Rs 11-14 ka hai. Do niyam isi liye hain:
  * Number tabhi wapas kiya jaata hai jab SMS aaya hi na ho. Aa gaya to paisa
    lag chuka -- cancel ka koi matlab nahi.
  * Cancel ek baar bhejna kaafi nahi: pehle ~2 minute provider `WAIT_CANCEL`
    lautata hai. `otpd.cancel` intezaar karke dobara bhejta hai.
"""
import os
import re
import csv
import sys
import json
import time
import random
import argparse
import urllib.parse
import urllib.request

import otpd
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SESSIONS = os.path.join(HERE, "sessions")
LEDGER = os.path.join(HERE, "accounts.csv")

URL = "https://estuaryworld.com/account/login?return_url=%2Faccount"
ACCOUNT_URL = "https://estuaryworld.com/account"
POPUP = "shiprocketLogin"

# ---- popup ke andar ke selector (sab naap kar liye gaye) ----
MOBILE = "9999999999"
LOGIN_BTN = "span.Login_inputAddonRight__ptvZb"
OTP_BOX = "input[autocomplete='one-time-code']"
EMAIL_BOX = ["input#email", "input[name='email']", "input[type='email']",
             "input[placeholder*='mail' i]"]
CONTINUE = ["button.loginPopupPrimaryButton", "button:has-text('Continue')",
            "button[type='submit']"]
NAME_BOX = ["input#name", "input[name='name']", "input[placeholder*='name' i]"]

# ---- email: wahi rasta jo pehle se chal raha hai ----
# Koi bhi `@buzzaro.in` pata chalta hai (catch-all), aur us par aaya code is
# worker se padha jaata hai. Isliye yahan naya kuch banane ki zaroorat nahi.
EMAIL_DOMAIN = "test@example.com"
WORKER = "https://nykaa-otp.buzzaro-otp.workers.dev/otp"
FIRST = ["aarav", "ishan", "rohit", "nikhil", "sahil", "varun", "kabir", "arjun",
         "manish", "rahul", "vikas", "priya", "neha", "swati", "megha", "pooja",
         "anjali", "kiran", "deepak", "amit", "suresh", "ritu", "sneha", "karan"]
LAST = ["sharma", "verma", "gupta", "singh", "yadav", "mehta", "joshi", "pandey",
        "tiwari", "chauhan", "kumar", "mishra", "shukla", "dubey", "rathore"]

for d in (OUT, SESSIONS):
    os.makedirs(d, exist_ok=True)


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- pehchaan
def new_email():
    sep = random.choice([".", "_", ""])
    local = sep.join([random.choice(FIRST), random.choice(LAST)]) + str(
        random.randint(100, 99999))
    return "%s@%s" % (re.sub(r"[^a-z0-9._]", "", local), EMAIL_DOMAIN)


def email_otp(email, tries=18, every=10):
    """Us email par aaya code -- Cloudflare worker se.

    Ye tabhi chalta hai jab site email par bhi OTP maange. Abhi tak ke test me
    nahi maanga, par maangne par kaam ruk na jaye isliye rasta yahan hai.
    """
    for i in range(1, tries + 1):
        time.sleep(every)
        try:
            req = urllib.request.Request(
                WORKER + "?email="test@example.com"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode("utf-8", "ignore") or "{}")
            if d.get("otp"):
                code = re.sub(r"\D", "", str(d["otp"]))
                log("      [mail] OTP mila: %s" % code)
                return code
        except Exception as e:
            log("      [mail] (worker: %s)" % str(e)[:60])
        log("      [mail] wait %d/%d" % (i, tries))
    return None


# ---------------------------------------------------------------- browser
def shot(page, name):
    try:
        page.screenshot(path=os.path.join(OUT, name + ".png"), full_page=False)
    except Exception:
        pass


def live_frame(page):
    """Popup ka frame ABHI. Har kadam par naya ban sakta hai, isliye purana
    pakad kar rakhna galat hai."""
    for fr in page.frames:
        if POPUP in (fr.url or ""):
            return fr
    return None


def wait_frame(page, secs=25):
    for _ in range(secs):
        fr = live_frame(page)
        try:
            if fr and fr.locator(MOBILE).count():
                return fr
        except Exception:
            pass
        page.wait_for_timeout(1000)
    return None


def find(scope, sels):
    for s in sels:
        try:
            if scope.locator(s).count() and scope.locator(s).first.is_visible():
                return s
        except Exception:
            continue
    return None


def words(scope, n=10):
    try:
        txt = scope.locator("body").inner_text() or ""
    except Exception:
        return ""
    return " | ".join([l.strip() for l in txt.splitlines() if l.strip()][:n])[:200]


def boxes_gone(f):
    try:
        return f.locator(OTP_BOX).count() == 0
    except Exception:
        return True          # frame hi chala gaya = aage badh gaya


def fill_otp(f, page, code):
    try:
        n = f.locator(OTP_BOX).count()
    except Exception:
        n = 0
    if not n:
        return False
    f.locator(OTP_BOX).first.click()
    page.keyboard.type(code, delay=150)
    page.wait_for_timeout(3000)
    if boxes_gone(f):
        return True
    try:
        for i, ch in enumerate(code[:n]):
            f.locator(OTP_BOX).nth(i).fill(ch)
            page.wait_for_timeout(300)
    except Exception:
        pass
    page.wait_for_timeout(3000)
    return boxes_gone(f)


def do_email(page, email, secs=30):
    """OTP ke baad ka "Enter your email" wala khaana.

    Popup me dekha jaata hai aur panne par bhi -- widget kabhi apne andar
    poochta hai aur kabhi site apne panne par le jaati hai.
    """
    for _ in range(secs):
        for scope in (live_frame(page), page):
            if scope is None:
                continue
            sel = find(scope, EMAIL_BOX)
            if not sel:
                continue
            log("      email ka khaana mila (%s)" % sel)
            scope.locator(sel).click()
            scope.locator(sel).fill("")
            scope.locator(sel).type(email, delay=60)
            page.wait_for_timeout(900)

            nsel = find(scope, NAME_BOX)
            if nsel:
                nm = email.split("@")[0].split(".")[0].split("_")[0].capitalize()
                scope.locator(nsel).fill(nm)
                page.wait_for_timeout(400)

            b = find(scope, CONTINUE)
            if b:
                # Continue tab tak bujha rehta hai jab tak email theek na ho.
                # Isliye click se pehle uske jagne ka intezaar -- bujhe button
                # par click chup-chaap kuch nahi karta.
                for _ in range(10):
                    try:
                        if scope.locator(b).first.is_enabled():
                            break
                    except Exception:
                        break
                    page.wait_for_timeout(500)
                scope.locator(b).first.click()
            else:
                page.keyboard.press("Enter")
            page.wait_for_timeout(7000)
            return True
        page.wait_for_timeout(1000)
    return False


def logged_in(page):
    """Login hua ya nahi -- panne ke apne shabdon se, andaze se nahi."""
    try:
        txt = (page.inner_text("body") or "").lower()
    except Exception:
        txt = ""
    if "/account" in page.url and "login" not in page.url:
        return True
    return any(w in txt for w in ("logout", "log out", "my orders", "my account"))


# ---------------------------------------------------------------- ek account
def one_account(h, email, headless, tag):
    """(ok, note, session_file). `h` = khareeda hua number."""
    got_sms = {"yes": False}
    with sync_playwright() as p:
        b = p.chromium.launch(
            headless=headless,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(
            viewport=None, locale="en-IN",
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/140.0.0.0 Safari/537.36"))
        page = ctx.new_page()
        ok, note, sfile = False, "", ""
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(6000)

            f = wait_frame(page)
            if not f:
                shot(page, "%s_fail_popup" % tag)
                return False, "login ka popup nahi aaya", "", got_sms["yes"]

            log("      number: %s" % h["phone"])
            f.locator(MOBILE).click()
            f.locator(MOBILE).fill("")
            f.locator(MOBILE).type(h["phone"], delay=90)
            page.wait_for_timeout(800)

            # Popup khud aage badh jaata hai; na badhe to Login dabao.
            try:
                f.wait_for_selector(OTP_BOX, timeout=9000)
            except Exception:
                if f.locator(LOGIN_BTN).count():
                    f.locator(LOGIN_BTN).click()
                try:
                    f.wait_for_selector(OTP_BOX, timeout=40000)
                except Exception:
                    shot(page, "%s_fail_otpscreen" % tag)
                    return False, "OTP ka panna nahi aaya", "", got_sms["yes"]

            code = otpd.get_otp(h, log=lambda m: log("      " + m))
            if not code:
                shot(page, "%s_fail_nootp" % tag)
                return False, "SMS OTP nahi aaya", "", got_sms["yes"]
            got_sms["yes"] = True
            log("      SMS OTP: %s" % code)

            if not fill_otp(f, page, code):
                shot(page, "%s_fail_otpfill" % tag)
                return False, "OTP khaanon me baitha nahi", "", got_sms["yes"]
            page.wait_for_timeout(5000)

            log("      email: %s" % email)
            if do_email(page, email):
                shot(page, "%s_email" % tag)
                # Email par bhi OTP maanga jaye to wo bhi bhar do.
                sc = live_frame(page) or page
                if find(sc, [OTP_BOX]):
                    log("      email wala OTP bhi maanga gaya")
                    ec = email_otp(email)
                    if ec:
                        fill_otp(sc, page, ec)
                        page.wait_for_timeout(6000)
            else:
                note = "email ka khaana nahi aaya"

            if not logged_in(page):
                page.goto(ACCOUNT_URL, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(5000)
            ok = logged_in(page)
            shot(page, "%s_done" % tag)
            if not ok and not note:
                note = "login sabit nahi hua (%s)" % words(page, 4)
        except Exception as e:
            note = "gadbad: %s" % str(e)[:120]
        finally:
            # SESSION HAR HAAL ME BACHTI HAI -- yahi is kaam ka nateeja hai.
            try:
                nm = "estuary_%s_%s.json" % (h["phone"], int(time.time()))
                st = ctx.storage_state()
                json.dump({"phone": h["phone"], "email": email,
                           "when": time.strftime("%Y-%m-%d %H:%M:%S"),
                           "logged_in": ok, "url": page.url, "state": st},
                          open(os.path.join(SESSIONS, nm), "w", encoding="utf-8"),
                          ensure_ascii=False, indent=1)
                sfile = nm
                log("      session: sessions/%s (cookies: %d)"
                    % (nm, len(st.get("cookies", []))))
            except Exception as e:
                note = (note + " | session save nahi hui: %s" % str(e)[:60]).strip(" |")
            try:
                b.close()
            except Exception:
                pass
    return ok, note, sfile, got_sms["yes"]


def write_row(row):
    new = not os.path.exists(LEDGER)
    with open(LEDGER, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["created_at", "phone", "email", "logged_in",
                        "session_file", "note"])
        w.writerow(row)


# ---------------------------------------------------------------- runner
def make_one(headless, tries, n):
    """Ek account -- number badal kar `tries` baar tak."""
    email = new_email()
    for t in range(1, tries + 1):
        log("   koshish %d/%d" % (t, tries))
        h = otpd.buy()
        if not h:
            log("      koi number nahi mila")
            time.sleep(10)
            continue
        tag = "acct%02d_try%d" % (n, t)
        ok, note, sfile, got_sms = one_account(h, email, headless, tag)
        if not got_sms:
            # SMS aaya hi nahi -> number wapas, poora paisa wapas.
            otpd.cancel(h, log=lambda m: log("      " + m))
        if ok:
            write_row([time.strftime("%Y-%m-%d %H:%M:%S"), h["phone"], email,
                       "yes", sfile, note])
            log("   BAN GAYA: %s / %s" % (h["phone"], email))
            return True
        log("   nahi bana: %s" % (note or "wajah darj nahi"))
        write_row([time.strftime("%Y-%m-%d %H:%M:%S"), h["phone"], email,
                   "no", sfile, note])
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1, help="kitne account banane hain")
    ap.add_argument("--tries", type=int, default=3, help="ek account par kitne number tak")
    # Headless band -- login ka popup Shiprocket ke iframe me chalta hai aur
    # bina window ke aksar aata hi nahi. Flag rakha hai taaki purane command na
    # tooten; ye ab kuch karta nahi.
    ap.add_argument("--headless", action="store_true",
                    help="(band kar diya gaya -- browser hamesha window ke saath)")
    ap.add_argument("--gap", type=int, nargs=2, default=[25, 55],
                    metavar=("KAM", "ZYADA"),
                    help="do account ke beech kitne second (kam zyada)")
    a = ap.parse_args()

    if a.headless:
        log("(--headless ab kaam nahi karta -- browser window ke saath hi chalega)")
    a.headless = False          # har haal me headed

    log("otpdoctor balance: %s" % otpd.balance())
    bane = 0
    for i in range(1, a.count + 1):
        log("\n===== account %d/%d =====" % (i, a.count))
        if make_one(a.headless, a.tries, i):
            bane += 1
        if i < a.count:
            w = random.randint(*a.gap)
            log("   %ds ruk kar agla" % w)
            time.sleep(w)

    log("\n================ hisaab ================")
    log("   maange gaye : %d" % a.count)
    log("   ban gaye    : %d" % bane)
    log("   nahi bane   : %d" % (a.count - bane))
    log("   ledger      : accounts.csv")
    log("   session     : sessions/")
    log("   balance ab  : %s" % otpd.balance())
    return 0 if bane else 1


if __name__ == "__main__":
    sys.exit(main())
