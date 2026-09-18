#!/usr/bin/env python3
"""order_plan.py -- ek order ki poori "yojna" banata hai.

Order lagane se pehle teen cheezein tay karni hoti hain, aur teeno alag jagah
se aati hain:

    1. CART   -- user ke diye product links se, itne variant/pack chuno ki kul
                 daam di hui range me aa jaye (jaise 3000-5000).
    2. PATA   -- 'Input_details' tab se, par har order par ALAG. Sheet me sirf
                 231 email, 5 naam, 26 pincode aur ek namoona pata hai; baaki
                 sab yahin gadha jaata hai.
    3. PAISA  -- 'payment_details' tab se ek row: card + corporate/employee id.
                 Ek row ek hi baar. Use karte hi uske aage 'complete'.

Ye file browser ko haath nahi lagati -- sirf faisla karti hai. Chalane ka kaam
place_order.py karta hai.
"""
import os
import re
import sys
import json
import time
import random

import requests

SHOP = "https://estuaryworld.com"

# ---------------------------------------------------------------- 1. CART


def handle_from_link(link):
    """Kisi bhi product link se uska handle nikalo.

    Link do tarah ke aate hain aur dono ek hi product ke hote hain:
        /products/johnnie-walker-luxe-blended-water
        /collections/diageo-brands/products/johnnie-walker-luxe-blended-water
    """
    link = (link or "").strip()
    if not link:
        return ""
    m = re.search(r"/products/([^/?#\s]+)", link)
    if m:
        return m.group(1)
    # sirf handle hi de diya ho to wahi
    if "/" not in link and " " not in link:
        return link
    return ""


def variants_from_links(links, log=print, timeout=25):
    """Har link ke saare variant (pack size) aur unka daam lao.

    Shopify khud ye JSON deta hai -- /products/<handle>.js -- isliye panna
    khol kar padhne ki zaroorat nahi. Isme daam aur stock dono sach-sach hote
    hain, jabki apne paas rakhi purani list (products_check.json) baasi ho
    sakti hai.
    """
    out = []
    for link in links:
        h = handle_from_link(link)
        if not h:
            log("   link samajh nahi aaya: %s" % str(link)[:70])
            continue
        url = "%s/products/%s.js" % (SHOP, h)
        try:
            r = requests.get(url, timeout=timeout,
                             headers={"Accept": "application/json",
                                      "User-Agent": "Mozilla/5.0"})
        except Exception as e:
            log("   %s -- nahi mila (%s)" % (h, str(e)[:60]))
            continue
        if r.status_code != 200:
            log("   %s -- HTTP %s" % (h, r.status_code))
            continue
        try:
            d = r.json()
        except ValueError:
            log("   %s -- jawaab JSON nahi tha" % h)
            continue

        mila = 0
        bahar = 0
        for v in d.get("variants", []):
            if not v.get("available"):
                bahar += 1
                continue
            out.append({
                "product": d.get("title") or h,
                "handle": h,
                "variant_id": v.get("id"),
                "variant_name": v.get("title") or "",
                "price": (v.get("price") or 0) / 100.0,
            })
            mila += 1
        if mila:
            log("   %-40s %d pack mile%s"
                % (d.get("title", h)[:40], mila,
                   (" (%d out of stock)" % bahar) if bahar else ""))
        else:
            log("   %-40s SAB out of stock -- ise chhod rahe hain"
                % (d.get("title", h)[:40]))
    return out


def pick_cart(variants, lo, hi, max_lines=6, max_qty=3, tries=4000, seed=None):
    """Aise variant chuno ki kul daam lo aur hi ke BEECH aa jaye.

    Seedha "sabse bada pehle" wala tareeka har baar ek jaisa cart banata hai,
    aur ek jaise order shak paida karte hain. Isliye har baar naye sire se
    random koshish hoti hai -- alag pack, alag ginti, alag mel.

    Lautata hai (items, kul). Na ban paye to ([], 0.0).
    """
    if not variants:
        return [], 0.0
    rnd = random.Random(seed)
    sasta = min(v["price"] for v in variants)

    # Kaun sa variant kis product ka hai
    dukan = {}
    for v in variants:
        dukan.setdefault(v["handle"], []).append(v)

    behtar, behtar_kul = [], 0.0
    for _ in range(tries):
        chune, kul = [], 0.0

        # Pehle HAR product se ek -- user ne kai link isiliye diye hain ki cart
        # me alag-alag cheezein jayen. Bina iske random chunav aksar ek hi
        # product ke teen pack utha leta tha, aur cart ek hi item ka ban jaata.
        handles = list(dukan)
        rnd.shuffle(handles)
        for h in handles:
            if len(chune) >= max_lines:
                break
            ho_sakte = [v for v in dukan[h] if v["price"] <= hi - kul]
            if not ho_sakte:
                continue
            v = rnd.choice(ho_sakte)
            chune.append(dict(v, quantity=1))
            kul += v["price"]

        # Ab range tak pahunchne ke liye upar se aur daalo
        bacha = list(variants)
        rnd.shuffle(bacha)
        for v in bacha:
            if len(chune) >= max_lines or kul >= lo:
                break
            # is variant ki kitni ginti bina hi ke paar gaye daali ja sakti hai
            jagah = hi - kul
            ho_sake = int(jagah // v["price"])
            if ho_sake < 1:
                continue
            n = rnd.randint(1, min(max_qty, ho_sake))
            # wahi variant pehle se cart me ho to uski ginti badha do,
            # nayi line na banao
            pehle = next((c for c in chune
                          if c["variant_id"] == v["variant_id"]), None)
            if pehle is not None:
                pehle["quantity"] += n
            else:
                chune.append(dict(v, quantity=n))
            kul += v["price"] * n

        if lo <= kul <= hi:
            return chune, round(kul, 2)
        # theek range me na aaye to jo sabse paas pahuncha wahi yaad rakho
        if kul <= hi and kul > behtar_kul:
            behtar, behtar_kul = chune, kul

    # range me kuch nahi bana. Jo sabse paas tha use lauta do -- par tabhi jab
    # wo lo ke kareeb ho (kam se kam ek sasta item ki doori par).
    if behtar and behtar_kul >= lo - sasta:
        return behtar, round(behtar_kul, 2)
    return [], 0.0


# ------------------------------------------------------------- 2. PATA
# Sheet me pincode 208001-000000 hain -- ye sab ASLI Kanpur ke hain. Inke saath
# city/state badalna theek nahi: pincode aur shehar ka mel na baithe to
# Shiprocket order hi nahi uthata. Isliye variety pincode ki apni girah se
# aati hai (26 alag), aur naam/address/apartment se -- jo yahan gadhe jaate
# hain. Pincode ke ANK khud se badalna jaan bujh kar nahi kiya jaata: badla
# hua pincode ya to hai hi nahi, ya kisi aur shehar ka nikal aata hai.

PIN_SHEHAR = {
    "208": ("Kanpur", "Uttar Pradesh"),
    "226": ("Lucknow", "Uttar Pradesh"),
    "201": ("Ghaziabad", "Uttar Pradesh"),
    "110": ("New Delhi", "Delhi"),
    "302": ("Jaipur", "Rajasthan"),
    "400": ("Mumbai", "Maharashtra"),
    "560": ("Bengaluru", "Karnataka"),
}
DEFAULT_SHEHAR = ("Kanpur", "Uttar Pradesh")

MOHALLA = [
    "Kalyanpur", "Shastri Nagar", "Kidwai Nagar", "Govind Nagar",
    "Swaroop Nagar", "Arya Nagar", "Civil Lines", "Barra", "Vikas Nagar",
    "Ratan Lal Nagar", "Harsh Nagar", "Rawatpur", "Kakadeo", "Nawabganj",
    "Fazalganj", "Yashoda Nagar", "Sarvodaya Nagar", "Panki", "Chakeri",
    "Shyam Nagar", "Naveen Market", "Gumti No 5",
]

GHAR_ROOP = ["LIG {a}", "MIG {a}", "H.No {a}/{b}", "{a}/{b}", "Plot {a}",
             "House No {a}", "{a}-{b}", "Flat {a}"]

NISHANI = [
    "Near {m} Market", "Opposite {m} Park", "Behind {m} Petrol Pump",
    "Near {m} Chauraha", "Above SBI Branch, {m}", "Next to {m} Police Station",
]

BHAWAN = ["Saket Apartment", "Ganga Residency", "Shanti Kunj", "Krishna Villa",
          "Sharma Complex", "Gokul Apartment", "Radhe Tower", "Anand Bhawan",
          "Yamuna Enclave", "Tulsi Residency"]

PEHLA_NAAM = ["Amit", "Rahul", "Aman", "Naina", "Rohit", "Sneha", "Vikas",
              "Priya", "Manish", "Kavita", "Sandeep", "Anjali", "Deepak",
              "Ritu", "Nitin", "Pooja", "Ashish", "Meena", "Gaurav", "Swati"]
DUSRA_NAAM = ["Sharma", "Raj", "Pal", "Singh", "Mathur", "Verma", "Gupta",
              "Yadav", "Mishra", "Tiwari", "Srivastava", "Dubey", "Awasthi",
              "Katiyar", "Dixit", "Pandey"]


def _shehar_from_pin(pin):
    return PIN_SHEHAR.get(str(pin)[:3], DEFAULT_SHEHAR)


INPUT_TAB = os.environ.get("ESTUARY_INPUT_TAB") or "Input_details"
# A-I haath ke hain. J me discount code -- ye script jodti hai, bharte aap hain.
DISCOUNT_COL = "J"
DISCOUNT_HEAD = "Discount_Code"


def open_input_tab(sheet_id=None, tab=None):
    """(worksheet, kahani) -- Input_details tab.

    Column J me 'Discount_Code' ka sir na ho to jod deti hai. Codes bharna aap
    par hai; jitne bhare honge, har order par unme se ek random uthega.
    """
    import sheet_log
    sheet_id = sheet_id or sheet_log.SHEET_ID
    tab = tab or INPUT_TAB
    creds, _src = sheet_log._creds()
    if not creds:
        return None, "credentials nahi mile"
    try:
        import gspread
    except ImportError:
        return None, "gspread nahi hai"
    try:
        gc = gspread.service_account_from_dict(creds)
        ws = gc.open_by_key(sheet_id).worksheet(tab)
    except Exception as e:
        return None, "tab nahi khula: %s" % str(e)[:140]

    try:
        first = ws.row_values(1)
        j = (first[9].strip() if len(first) > 9 else "")
        if not j:
            ws.update([[DISCOUNT_HEAD]], "%s1" % DISCOUNT_COL,
                      value_input_option="RAW")
            return ws, "ok (Discount_Code ka column jod diya)"
    except Exception as e:
        return ws, "ok, par header dekh nahi paye (%s)" % str(e)[:70]
    return ws, "ok"


def read_inputs(ws):
    """Input_details tab padho. Jo khaana khaali hai wo khaali hi rehne do --
    uski jagah baad me khud bhar denge."""
    vals = ws.get_all_values()
    out = []
    for i, r in enumerate(vals[1:], start=2):
        def g(n):
            return (r[n] if len(r) > n else "").strip()
        out.append({
            "row": i, "email": g(0), "first": g(1), "last": g(2),
            "address": g(3), "apartment": g(4), "city": g(5),
            "state": g(6), "pin": g(7), "phone": g(8),
            "discount": g(9),
        })
    return out


def _pool(rows, key):
    """Ek column me jo bhi bhara hai, uski alag-alag list."""
    seen, out = set(), []
    for r in rows:
        v = (r.get(key) or "").strip()
        if v and v.lower() not in seen:
            seen.add(v.lower())
            out.append(v)
    return out


# Is run ki apni pehchaan -- pata banane ke beej me jaati hai.
_CHAL = int(time.time())


def make_identity(rows, n, seed=None, phones=None):
    """Ek order ke liye pata banao -- har baar alag.

    `n` order ka number hai (0, 1, 2...). Isse do faayde hain: ek, sheet ki
    rows kram se ghoomti hain (kisi ek par bhaar nahi padta); do, wahi n random
    ke beej me bhi jaata hai, isliye ek hi batch me do order ka pata kabhi ek
    jaisa nahi banta.

    Phone JAAN BUJH KAR nahi badla jaata. Jo number diye gaye hain wahi kram se
    ghoomte hain -- number banaya nahi ja sakta, wo kisi asli SIM ka hona
    chahiye.
    """
    # Beej: seed diya ho to wahi (wahi pata dobara banega -- jaanch ke
    # kaam ka). Na diya ho to har CHALNE par naya. Pehle yahan 0 tha,
    # jiska matlab tha ki har nayi run ka pehla order hamesha wahi pata
    # uthata tha -- ek batch ke andar pate alag the, par do batch ke
    # pehle order ka pata ek jaisa. _CHAL ek baar module khulne par tay
    # hota hai, isliye ek run ke andar n se ginti aage badhti rehti hai.
    rnd = random.Random(((seed if seed is not None else _CHAL) * 100003) + n)
    if not rows:
        rows = [{}]
    base = rows[n % len(rows)]

    # --- pincode: sheet me jo asli hain unhi me se ---
    pins = _pool(rows, "pin")
    pin = base.get("pin") or (pins[n % len(pins)] if pins else "208001")

    # --- city/state: pincode se hi. Sheet me likha ho to wahi. ---
    shehar, rajya = _shehar_from_pin(pin)
    # Sheet me "kanpur" / "uttar pradesh" chhote akshar me pade hain. Checkout
    # ka state wala dropdown akshar ka farak maanta hai, isliye pehle akshar
    # bade kar dete hain -- "Uttar Pradesh".
    city = (base.get("city") or shehar).strip().title()
    state = (base.get("state") or rajya).strip().title()

    # --- naam: sheet ke naam + apni list, dono milakar ---
    pehle = _pool(rows, "first") or []
    doosre = _pool(rows, "last") or []
    first = rnd.choice(pehle + PEHLA_NAAM) if (pehle or PEHLA_NAAM) else "Amit"
    last = rnd.choice(doosre + DUSRA_NAAM) if (doosre or DUSRA_NAAM) else "Sharma"

    # --- address: har order par naya. Yahi asli alagav hai. ---
    m = rnd.choice(MOHALLA)
    ghar = rnd.choice(GHAR_ROOP).format(a=rnd.randint(1, 399),
                                        b=rnd.randint(1, 99))
    address1 = "CHANGE_ME_ADDR1" % (ghar, m)

    if rnd.random() < 0.5:
        address2 = rnd.choice(NISHANI).format(m=rnd.choice(MOHALLA))
    else:
        address2 = "CHANGE_ME_ADDR2" % (rnd.randint(1, 12),
                                      rnd.choice("ABCD"),
                                      rnd.choice(BHAWAN))

    # --- phone: badalna nahi, sirf ghumana ---
    number = list(phones or []) or [p for p in _pool(rows, "phone")]
    phone = number[n % len(number)] if number else ""

    # --- email: sirf tab kaam aata hai jab checkout par email ka khaana ho
    # (logged-in par Shopify wo dikhata hi nahi). Plus-tag lagane se pata alag
    # dikhta hai par chitthi usi dabbe me girti hai.
    email = base.get("email") or ""
    if email and "@" in email:
        naam, ghar_ka = email.split("@", 1)
        email = "test@example.com" % (naam.split("+")[0], int(time.time()) % 100000,
                               ghar_ka)

    # Discount code: sheet me jitne bhare hain unme se ek, har baar random.
    # Ek hi code baar baar lagana aankh me chubhta hai; alag-alag code aam
    # grahakon jaisa lagta hai.
    codes = _pool(rows, "discount")
    code = rnd.choice(codes) if codes else ""

    return {
        "sheet_row": base.get("row", 0),
        "discount": code,
        "email": email,
        "first_name": first,
        "last_name": last,
        "address1": address1,
        "address2": address2,
        "city": city,
        "province": state,
        "zip": pin,
        "phone": phone,
    }


# ---------------------------------------------------------- 3. PAISA
# payment_details tab: Card number | MM/YY | Card Holder Name | CVV |
#                      Corporate ID | Employee ID
# Iske aage script teen column jodti hai: Status | Used_At | Note
# Niyam wahi hai jo Account_emails me hai -- Status khaali = row baaki hai.

PAY_TAB = os.environ.get("ESTUARY_PAY_TAB") or "payment_details"
PAY_OUT_COLS = ["Status", "Used_At", "Note"]
PAY_FIRST_OUT = "John"
PAY_LAST_OUT = "Doe"
PAY_DONE = "complete"
PAY_BUSY = "RUNNING"


def open_pay_tab(sheet_id=None, tab=None):
    """(worksheet, kahani)."""
    import sheet_log
    sheet_id = sheet_id or sheet_log.SHEET_ID
    tab = tab or PAY_TAB
    creds, _src = sheet_log._creds()
    if not creds:
        return None, "credentials nahi mile"
    try:
        import gspread
    except ImportError:
        return None, "gspread nahi hai"
    try:
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_key(sheet_id)
        ws = sh.worksheet(tab)
    except Exception as e:
        return None, "tab nahi khula: %s" % str(e)[:140]

    try:
        first = ws.row_values(1)
        if len(first) < 6:
            return ws, ("CHETAVNI: tab me sirf %d column hain -- "
                        "Card number..Employee ID chahiye" % len(first))
        aage = [c.strip() for c in first[6:9]]
        if not any(aage):
            ws.update([PAY_OUT_COLS], "%s1:%s1" % (PAY_FIRST_OUT, PAY_LAST_OUT),
                      value_input_option="RAW")
            return ws, "ok (Status..Note ke column jod diye)"
    except Exception as e:
        return ws, "ok, par header dekh nahi paye (%s)" % str(e)[:70]
    return ws, "ok"


def read_payments(ws):
    """Saari card rows, unke kram me.

    Corporate/Employee ID sirf pehli row me bhare hote hain. Wo har card ke
    liye ek hi hain, isliye khaali rows me upar wali row ki id chal jaati hai
    -- warna doosra card kabhi bank ke form se aage badhta hi nahi.
    """
    vals = ws.get_all_values()
    out = []
    aakhri_corp = aakhri_emp = "CHANGE_ME_EMP_ID"
    for i, r in enumerate(vals[1:], start=2):
        def g(n):
            return (r[n] if len(r) > n else "").strip()
        card = g(0)
        if not card:
            continue
        corp, emp = g(4), g(5)
        if corp:
            aakhri_corp = corp
        if emp:
            aakhri_emp = emp
        out.append({
            "row": i,
            "card": re.sub(r"\s+", "", card),
            "exp": g(1),
            "holder": g(2),
            "cvv": g(3),
            "corp_id": corp or aakhri_corp,
            "emp_id": emp or aakhri_emp,
            "status": g(6),
            "virasat": not (corp and emp),   # id upar wali row se li gayi
        })
    return out


def pending_payments(ws):
    return [p for p in read_payments(ws) if not p["status"]]


def release_payment(ws, row):
    """Claim wापas lo -- row phir se khaali (bina-use) ho jaye.

    Do instance ne ek hi pal me ek hi employee id ke do card pakad liye to ek
    ko haar maan kar apna card chhodna padta hai. Tabhi ye kaam aata hai.
    """
    try:
        _pay_write(ws, row, ["", "", ""])
        return True
    except Exception as e:
        print("   [sheet] payment row %d chhodi nahi gayi: %s" % (row, str(e)[:80]))
        return False


def claim_next_card(ws, avoid_emps=(), tries=4):
    """Ek bina-use card claim karo -- aisa jiska employee id abhi kahin aur
    na chal raha ho.

    Do pakke niyam:
      1) Jis card ka status khaali ho, wahi (pehle se use/RUNNING chhod do).
      2) Jis employee id par abhi koi transaction CHAL rahi ho (kisi row par
         RUNNING likha ho), us employee id ka koi card mat lo. Yahi OTP ke
         clash se bachata hai.
    Ek narm niyam:
      3) `avoid_emps` me wo employee id hain jo isi run me pehle le chuke hain.
         Ho sake to inse alag emp id ka card do ("har baar alag"). Par agar
         aisa card na bache to majboori me inhi me se le lo -- warna 50 order
         ka lakshya ruk jayega, jabki ek instance ke andar order ek-ek karke
         (kramvaar) lagte hain, isliye us emp id ko dobara lena surakshit hai.

    Claim karne ke baad ek race-jaanch hoti hai: dobara padh kar dekhte hain
    ki usi emp id par kisi CHHOTE row number par RUNNING to nahi -- agar hai to
    hum haar gaye, apna card chhod kar dobara koshish. Isse do instance ek pal
    me ek hi emp id na utha lein.

    Lautata hai: card dict (jaisa read_payments deta hai) ya None.
    """
    avoid = set(e for e in avoid_emps if e)
    for _ in range(max(1, tries)):
        rows = read_payments(ws)
        chalu_emp = set(r["emp_id"] for r in rows
                        if (r["status"] or "").strip().upper() == PAY_BUSY)
        free = [r for r in rows if not r["status"]]

        def chuno(pool):
            for r in pool:
                if r["emp_id"] and r["emp_id"] in chalu_emp:
                    continue                    # is emp par transaction chalu
                return r
            return None

        cand = chuno([r for r in free if r["emp_id"] not in avoid])
        if cand is None:
            cand = chuno(free)                  # majboori: emp dobara (par chalu nahi)
        if cand is None:
            return None

        claim_payment(ws, cand["row"])

        # race-jaanch: usi emp par koi chhota row RUNNING to nahi?
        if cand["emp_id"]:
            rows2 = read_payments(ws)
            haar = [r for r in rows2
                    if r["emp_id"] == cand["emp_id"]
                    and (r["status"] or "").strip().upper() == PAY_BUSY
                    and r["row"] < cand["row"]]
            if haar:
                release_payment(ws, cand["row"])
                continue                        # dobara koshish
        return cand
    return None


def _pay_write(ws, row, values):
    ws.update([values], "%s%d:%s%d" % (PAY_FIRST_OUT, row, PAY_LAST_OUT, row),
              value_input_option="RAW")


def claim_payment(ws, row):
    try:
        _pay_write(ws, row, [PAY_BUSY, time.strftime("%Y-%m-%d %H:%M:%S"), ""])
        return True
    except Exception as e:
        print("   [sheet] payment row %d claim nahi hui: %s" % (row, str(e)[:80]))
        return False


def mark_payment(ws, row, status, note=""):
    try:
        _pay_write(ws, row, [status, time.strftime("%Y-%m-%d %H:%M:%S"),
                             note[:200]])
        return True
    except Exception as e:
        print("   [sheet] payment row %d likhi nahi gayi: %s" % (row, str(e)[:80]))
        return False


# ---------------------------------------------------------------- dekho
def main():
    import argparse
    ap = argparse.ArgumentParser(description="order ki yojna dekho (banao mat)")
    ap.add_argument("--link", action="append", default=[],
                    help="product ka link (kai baar de sakte ho)")
    ap.add_argument("--max", type=float, default=5000.0)
    ap.add_argument("--min", type=float, default=0.0,
                    help="0 = max ka 60%%")
    ap.add_argument("--orders", type=int, default=3,
                    help="itne order ke pate bana kar dikhao")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()

    lo = a.min or round(a.max * 0.6, 2)
    print("range : Rs %.2f -- Rs %.2f" % (lo, a.max))

    if a.link:
        print("\nproducts:")
        vs = variants_from_links(a.link)
        items, kul = pick_cart(vs, lo, a.max, seed=a.seed)
        print("\ncart (Rs %.2f):" % kul)
        for it in items:
            print("   %-42s %-12s x%d  Rs %8.2f"
                  % (it["product"][:42], it["variant_name"][:12],
                     it["quantity"], it["price"] * it["quantity"]))
        if not items:
            print("   is range me cart nahi ban paya")

    try:
        import sheet_log
        import gspread
        creds, _ = sheet_log._creds()
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_key(sheet_log.SHEET_ID)
        rows = read_inputs(sh.worksheet("Input_details"))
        print("\nInput_details: %d rows" % len(rows))
        for n in range(a.orders):
            idn = make_identity(rows, n, seed=a.seed)
            print("   %d) %s %s | %s | %s | %s %s - %s | ph %s"
                  % (n + 1, idn["first_name"], idn["last_name"],
                     idn["address1"], idn["address2"], idn["city"],
                     idn["province"], idn["zip"], idn["phone"] or "(koi nahi)"))

        ws, kahani = open_pay_tab()
        print("\npayment_details -> %s" % kahani)
        if ws is not None:
            for p in read_payments(ws):
                print("   row %d  ****%s  %s  corp=%s emp=%s%s  status=%s"
                      % (p["row"], p["card"][-4:], p["exp"], p["corp_id"],
                         p["emp_id"], " (upar se li)" if p["virasat"] else "",
                         p["status"] or "-"))
    except Exception as e:
        print("\nsheet nahi padhi gayi: %s" % str(e)[:140])
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ------------------------------------------------- 4. ORDER KA RECORD
# Har lage hue order ki ek line -- kis account par, kya gaya, kitne ka, kaunsa
# card, kaunsa code, kab. Ye tab script khud bana leti hai.
#
# Ye orders.csv ki nakal nahi hai: CSV us machine par padi rehti hai jahan
# script chali, aur sheet har kisi ko dikhti hai. Dono isliye rakhe hain ki
# internet ya credentials kharaab hone par bhi record kahin to bache.

ORDER_TAB = os.environ.get("ESTUARY_ORDER_TAB") or "Order_Records"


def _col_letter(n):
    """1 -> A, 26 -> Z, 27 -> AA"""
    out = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        out = chr(65 + r) + out
    return out

ORDER_COLS = [
    "When", "Status", "Order_Ref",
    "Account_Email", "Customer_ID", "Session_File",
    "Ship_Name", "Address", "Apartment", "City", "State", "Pincode", "Phone",
    "Items", "Cart_Value", "Discount_Code", "Paid",
    "Card_Last4", "Corp_ID", "Emp_ID", "OTP",
    "Payment_Row", "Input_Row", "Product_Links", "Checkout_URL", "Note",
    # Ye paanch order lag jaane ke BAAD /account panne se aate hain.
    # Thank-you page ka "Confirmation #TE5KTZ0DF" dukaan ka andaruni
    # number hai; grahak ko jo dikhta hai wo "#136267" hai. Sheet me dono
    # chahiye -- ek se doosre ka mel baithana padta hai.
    "Acct_Order_No", "Order_Date", "Payment_Status", "Order_Total",
    "Order_URL",
]


def open_orders_tab(sheet_id=None, tab=None):
    """(worksheet, kahani). Tab na ho to bana deti hai."""
    import sheet_log
    sheet_id = sheet_id or sheet_log.SHEET_ID
    tab = tab or ORDER_TAB
    creds, _src = sheet_log._creds()
    if not creds:
        return None, "credentials nahi mile"
    try:
        import gspread
    except ImportError:
        return None, "gspread nahi hai"
    try:
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_key(sheet_id)
    except Exception as e:
        return None, "sheet nahi khuli: %s" % str(e)[:140]

    try:
        ws = sh.worksheet(tab)
    except Exception:
        try:
            ws = sh.add_worksheet(title=tab, rows=2000, cols=len(ORDER_COLS))
            ws.append_row(ORDER_COLS, value_input_option="RAW")
            return ws, "naya tab bana diya"
        except Exception as e:
            return None, "tab bana nahi paye: %s" % str(e)[:120]

    try:
        first = ws.row_values(1)
        if not first:
            ws.append_row(ORDER_COLS, value_input_option="RAW")
        elif [c.strip().lower() for c in first[:3]] != \
                [h.lower() for h in ORDER_COLS[:3]]:
            # Kisi aur ke tab me likhna shuru kar dena sabse bura hai --
            # isliye mel na baithe to haath hi nahi lagate.
            return ws, ("CHETAVNI: is tab ke column alag hain -- mile: %s"
                        % ", ".join(first[:5]))
        elif len(first) < len(ORDER_COLS):
            # Naye column jud gaye (jaise /account se aane wale). Purani lines
            # waisi ki waisi rehti hain -- bas sir aage badha dete hain, warna
            # nayi values bina naam ke column me girti hain.
            try:
                ws.update([ORDER_COLS],
                          "A1:%s1" % _col_letter(len(ORDER_COLS)),
                          value_input_option="RAW")
                return ws, "ok (naye column jod diye)"
            except Exception as e:
                return ws, "ok, par naye column nahi jud paye (%s)" % str(e)[:70]
    except Exception as e:
        return ws, "ok, par header dekh nahi paye (%s)" % str(e)[:70]
    return ws, "ok"


def log_order(ws, rec):
    """Ek order ki line likh do. Kabhi exception nahi phenkti -- sheet ki
    dikkat se order ka kaam nahi rukna chahiye. (Purana naam; ab append_order
    ke upar hai.)"""
    return bool(append_order(ws, rec))


def append_order(ws, rec):
    """Line jodo aur uska row number lauta do (na ja paye to 0).

    Row number isliye chahiye ki baad me (account history se order id aane par)
    isi line ko update kiya ja sake -- nayi line nahi.
    """
    if ws is None:
        return 0
    row = [str(rec.get(c, "") if rec.get(c) is not None else "")
           for c in ORDER_COLS]
    try:
        r = ws.append_row(row, value_input_option="RAW")
    except Exception as e:
        print("   [sheet] order ki line nahi gayi: %s" % str(e)[:110])
        return 0
    # gspread lautata hai: {'updates': {'updatedRange': 'Order_Records!A5:AE5'}}
    try:
        rng = r["updates"]["updatedRange"]
        m = re.search(r"![A-Z]+(\d+)", rng)
        return int(m.group(1)) if m else 0
    except Exception:
        return 0


def update_order(ws, row, field_vals):
    """Ek likhi hui line ke kuch column badal do. field_vals = {col_naam: val}.

    Sirf wahi cells chhoote hain jo diye gaye -- baaki line waisi ki waisi.
    """
    if ws is None or not row or not field_vals:
        return False
    data = []
    for col, val in field_vals.items():
        try:
            i = ORDER_COLS.index(col)
        except ValueError:
            continue
        a1 = "%s%d" % (_col_letter(i + 1), row)
        data.append({"range": a1,
                     "values": [[str(val if val is not None else "")]]})
    if not data:
        return False
    try:
        ws.batch_update(data, value_input_option="RAW")
        return True
    except Exception as e:
        print("   [sheet] order line %d update nahi hui: %s" % (row, str(e)[:100]))
        return False
