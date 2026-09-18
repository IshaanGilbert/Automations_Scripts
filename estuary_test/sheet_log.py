#!/usr/bin/env python3
"""sheet_log.py -- bane hue account Google Sheet me row-by-row likho.

Kyun alag file: account banane wali script ka kaam browser chalana hai, sheet
ka nahi. Sheet kabhi na khule (net gaya, credentials badle) to account BANANA
nahi rukna chahiye -- isliye yahan har gadbad pakdi jaati hai aur sirf False
lautaya jaata hai, exception upar nahi jaata.

Credentials wahin se aate hain jahan pehle se rakhe hain:
    magzter-v3-server/config.json  ->  GOOGLE_CREDENTIALS
Sheet id neeche default hai, ya --sheet-id / ESTUARY_SHEET_ID se badal lo.

CHALANA (sirf jaanch)
    python sheet_log.py --check                 # judav aur tab ki jaanch
    python sheet_log.py --test-row              # ek nakli row daal kar dekho
"""
import os
import sys
import json
import time
import argparse

# exe me __file__ temp folder hota hai -- isliye exe ke bagal wali jagah aur
# exe ke andar bandhi hui copy, dono dekhi jaati hain.
FROZEN = bool(getattr(sys, "frozen", False))
HERE = (os.path.dirname(sys.executable) if FROZEN
        else os.path.dirname(os.path.abspath(__file__)))
BUNDLE = getattr(sys, "_MEIPASS", HERE)

# jahan se credentials milte hain (config me poora service-account darj hai)
CREDS_FILES = [
    os.environ.get("GOOGLE_CREDS_FILE") or "",
    os.path.join(HERE, "google_creds.json"),          # exe ke bagal me
    os.path.join(BUNDLE, "google_creds.json"),        # exe ke andar bandhi
    os.path.join(HERE, "config.json"),
    os.path.join(os.path.dirname(HERE), "magzter-v3-server", "config.json"),
    r"D:\streakads\magzter-v3-server\config.json",
]

# Estuary ki apni sheet. (Pehle yahan galti se MagzterAUG ki id thi -- rows
# wahan chali gayi thin.)
SHEET_ID = (os.environ.get("ESTUARY_SHEET_ID")
            or "12ZfV-1NktXOj-ISKkqDuZ2eEp08POjSnLfyfekUl5cc")
TAB = os.environ.get("ESTUARY_SHEET_TAB") or "Account_Data"

# Pehle chaar wahi hain jo tumne kahe. Baaki isliye ki baad me sawal na uthe --
# kaun sa browser tha, proxy chala tha ya nahi, aur Shopify ne kya id di.
HEADER = ["Mobile", "Email", "Session_file", "Created_At",
          "Status", "Customer_ID", "Browser", "Proxy", "Note"]


def _creds():
    """Service-account dict -- jo pehli file me mile."""
    for p in CREDS_FILES:
        if not p or not os.path.isfile(p):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        # config.json ke andar GOOGLE_CREDENTIALS, ya seedha service-account file
        got = d.get("GOOGLE_CREDENTIALS") if isinstance(d, dict) else None
        if not got and isinstance(d, dict) and d.get("type") == "service_account":
            got = d
        if got and got.get("private_key"):
            return got, p
    return None, ""


def open_tab(sheet_id=None, tab=None, make=True):
    """(worksheet, kahani). Na khule to (None, wajah)."""
    sheet_id = sheet_id or SHEET_ID
    tab = tab or TAB
    creds, src = _creds()
    if not creds:
        return None, "credentials nahi mile (dekhi: %s)" % ", ".join(
            p for p in CREDS_FILES if p)
    try:
        import gspread
    except ImportError:
        return None, "gspread nahi hai -- pip install gspread"

    try:
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_key(sheet_id)
    except Exception as e:
        return None, "sheet nahi khuli: %s" % str(e)[:160]

    try:
        ws = sh.worksheet(tab)
    except Exception:
        if not make:
            return None, "tab '%s' nahi mila" % tab
        try:
            ws = sh.add_worksheet(title=tab, rows=1000, cols=len(HEADER))
            ws.append_row(HEADER, value_input_option="RAW")
        except Exception as e:
            return None, "tab '%s' bana nahi paye: %s" % (tab, str(e)[:120])

    # Header ka milaan. Teen haal ho sakte hain:
    #   khaali tab      -> poora header daal do
    #   pehle 4 sahi    -> baaki column (Status, Customer_ID...) jod do
    #   pehle 4 alag    -> haath mat lagao, sirf chetavni -- kisi aur ke tab me
    #                      likhna shuru kar dena isse bura kuch nahi
    try:
        first = ws.row_values(1)
        if not first:
            ws.append_row(HEADER, value_input_option="RAW")
        elif [c.strip().lower() for c in first[:4]] != [h.lower() for h in HEADER[:4]]:
            return ws, ("CHETAVNI: tab ke column alag hain -- mile: %s"
                        % ", ".join(first[:6]))
        elif len(first) < len(HEADER):
            try:
                ws.update([HEADER], "A1:%s1" % chr(ord("A") + len(HEADER) - 1),
                          value_input_option="RAW")
            except Exception as e:
                return ws, ("ok, par baaki column nahi jud paye (%s)"
                            % str(e)[:60])
    except Exception:
        pass
    return ws, "ok (credentials: %s)" % os.path.basename(src)


def add_account(mobile, email, session_file, created_at=None, status="created",
                customer_id="", browser="waterfox", proxy=True, note="",
                sheet_id=None, tab=None, log=print):
    """Ek account ki row sheet me jodo. True/False.

    Sheet ki koi bhi gadbad account banane ko nahi rokegi -- isliye yahan sab
    kuch pakda jaata hai.
    """
    row = [str(mobile or ""), str(email or ""), str(session_file or ""),
           created_at or time.strftime("%Y-%m-%d %H:%M:%S"),
           status, str(customer_id or ""), browser,
           "haan" if proxy else "nahi", (note or "")[:300]]
    try:
        ws, kahani = open_tab(sheet_id, tab)
        if ws is None:
            log("   [sheet] %s" % kahani)
            return False
        if kahani.startswith("CHETAVNI"):
            log("   [sheet] %s" % kahani)
        ws.append_row(row, value_input_option="RAW")
        log("   [sheet] row jud gayi: %s | %s" % (mobile, email))
        return True
    except Exception as e:
        log("   [sheet] row nahi judi: %s" % str(e)[:140])
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet-id", default=SHEET_ID)
    ap.add_argument("--tab", default=TAB)
    ap.add_argument("--check", action="store_true", help="judav ki jaanch")
    ap.add_argument("--test-row", action="store_true", help="ek nakli row daalo")
    a = ap.parse_args()

    creds, src = _creds()
    print("credentials :", (creds or {}).get("client_email") or "NAHI MILE",
          "(%s)" % os.path.basename(src) if src else "")
    print("sheet id    :", a.sheet_id)
    print("tab         :", a.tab)

    ws, kahani = open_tab(a.sheet_id, a.tab)
    print("judav       :", kahani)
    if ws is None:
        return 1

    try:
        vals = ws.get_all_values()
        print("tab me rows :", len(vals))
        if vals:
            print("header      :", vals[0])
            for r in vals[-3:][1:] if len(vals) > 1 else []:
                print("   aakhri   :", r)
    except Exception as e:
        print("padha nahi gaya:", str(e)[:120])

    if a.test_row:
        ok = add_account("0000000000", "test@example.com", "TEST.json",
                         status="TEST -- hata dena", note="sheet_log.py --test-row",
                         sheet_id=a.sheet_id, tab=a.tab)
        print("test row    :", "gayi" if ok else "nahi gayi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
