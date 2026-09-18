#!/usr/bin/env python3
"""sheet_emails.py -- 'Account_emails' tab: input padho, nateeja likho.

Is tab me pehle se chaar column hain jo HAATH SE bhare gaye hain:

    A First_Name | B Last_Name | C Email Addess | D Password

Script inhe sirf PADHTI hai. Uske aage paanch column apne aap jud jaate hain
aur wahin nateeja jaata hai:

    E Status | F Session_file | G Customer_ID | H Created_At | I Note

Ek row ek hi baar kaam aati hai. Niyam saaf hai: **Status khaali = row abhi
baaki hai**. Isliye kaam shuru karte hi row par "RUNNING" likh diya jaata hai
(claim), aur kaam khatam hone par "complete" ya "failed". Ye claim isliye
zaroori hai -- agar beech me bijli chali jaye ya script mar jaye, to row
"RUNNING" par ruki reh jaati hai aur dobara nahi uthti. Wahi chahiye: ho sakta
hai us email par account ban chuka ho aur hume pata na chala ho. Aise row
haath se dekh kar khaali kar dena, tab wo phir se list me aa jayegi.
"""
import os
import sys
import time

import sheet_log

TAB = os.environ.get("ESTUARY_EMAIL_TAB") or "Account_emails"

# jo pehle se hain (sirf padhne ke liye)
IN_COLS = ["First_Name", "Last_Name", "Email Addess", "Password"]
# jo script jodti hai
OUT_COLS = ["Status", "Session_file", "Customer_ID", "Created_At", "Note"]

STATUS_COL = 5          # E
FIRST_OUT_COL = "John"
LAST_OUT_COL = "Doe"

DONE = "complete"
FAIL = "failed"
BUSY = "RUNNING"


def open_tab(sheet_id=None, tab=None):
    """(worksheet, kahani). Na khule to (None, wajah)."""
    sheet_id = sheet_id or sheet_log.SHEET_ID
    tab = tab or TAB
    creds, _src = sheet_log._creds()
    if not creds:
        return None, "credentials nahi mile"
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
        return None, "tab '%s' nahi mila" % tab

    # header: pehle chaar column HAATH ke hain, unhe chhedna nahi. Sirf E-I
    # tab jodo jab wahan kuch likha hi na ho.
    try:
        first = ws.row_values(1)
        if len(first) < 4:
            return ws, ("CHETAVNI: tab me sirf %d column hain -- "
                        "First_Name/Last_Name/Email/Password chahiye" % len(first))
        aage = [c.strip() for c in first[4:9]]
        if not any(aage):
            ws.update([OUT_COLS], "%s1:%s1" % (FIRST_OUT_COL, LAST_OUT_COL),
                      value_input_option="RAW")
            return ws, "ok (Status..Note ke column jod diye)"
        if aage[:1] and aage[0].lower() != "status":
            return ws, "CHETAVNI: E1 me 'Status' nahi, '%s' likha hai" % aage[0]
    except Exception as e:
        return ws, "ok, par header dekh nahi paye (%s)" % str(e)[:80]
    return ws, "ok"


def pending(ws, limit=None):
    """Wo rows jinka Status khaali hai. [{row, first, last, email, password}]"""
    vals = ws.get_all_values()
    out = []
    for i, r in enumerate(vals[1:], start=2):       # row 1 header hai
        first = (r[0] if len(r) > 0 else "").strip()
        last = (r[1] if len(r) > 1 else "").strip()
        email = (r[2] if len(r) > 2 else "").strip()
        pw = (r[3] if len(r) > 3 else "").strip()
        status = (r[4] if len(r) > 4 else "").strip()
        if status:                                   # pehle hi use ho chuki
            continue
        if not (email and pw):                       # aadhi bhari row chhod do
            continue
        out.append({"row": i, "first": first, "last": last,
                    "email": email, "password": pw})
        if limit and len(out) >= limit:
            break
    return out


def _write(ws, row, values):
    rng = "%s%d:%s%d" % (FIRST_OUT_COL, row, LAST_OUT_COL, row)
    ws.update([values], rng, value_input_option="RAW")


def still_free(ws, row):
    """Ab bhi khaali hai? (kaam shuru karne se THEEK pehle poochho)

    `pending()` ek baar list bana leta hai, aur us list par kaam karte-karte
    kai minute nikal jaate hain. Us beech koi doosri script (ya doosre system
    par chalti wahi exe) usi row ko utha sakti hai -- tab ek hi email par do
    baar account banane ki koshish hoti hai, aur doosri baar sheet ki row
    bekaar me kharch ho jaati hai. Isliye uthane se pehle sirf wo ek khaana
    dobara padh lete hain; poori sheet dobara padhne ki zaroorat nahi.

    Padha hi na jaye (network) to `True` -- shak me kaam rokna theek nahi.
    """
    try:
        got = ws.acell("%s%d" % (FIRST_OUT_COL, row)).value
    except Exception as e:
        print("   [sheet] row %d ka Status dobara padha nahi gaya: %s"
              % (row, str(e)[:80]))
        return True
    return not (got or "").strip()


def claim(ws, row):
    """Row ko 'RUNNING' kar do taaki koi doosri run ise na uthaye."""
    try:
        _write(ws, row, [BUSY, "", "", time.strftime("%Y-%m-%d %H:%M:%S"), ""])
        return True
    except Exception as e:
        print("   [sheet] row %d claim nahi hui: %s" % (row, str(e)[:90]))
        return False


def mark(ws, row, status, session_file="", customer_id="", note=""):
    try:
        _write(ws, row, [status, session_file, str(customer_id or ""),
                         time.strftime("%Y-%m-%d %H:%M:%S"), note[:200]])
        return True
    except Exception as e:
        print("   [sheet] row %d likhi nahi gayi: %s" % (row, str(e)[:90]))
        return False


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Account_emails tab ka haal")
    ap.add_argument("--tab", default=TAB)
    ap.add_argument("--show", type=int, default=5)
    a = ap.parse_args()

    ws, kahani = open_tab(tab=a.tab)
    print("tab '%s' -> %s" % (a.tab, kahani))
    if ws is None:
        return 1
    vals = ws.get_all_values()
    print("kul rows   :", len(vals) - 1)
    baaki = pending(ws)
    print("baaki (khaali Status):", len(baaki))
    for r in baaki[:a.show]:
        print("   row %-4d %s %s  %s" % (r["row"], r["first"], r["last"], r["email"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
