#!/usr/bin/env python3
"""order_batch.py -- ek ke baad ek kai order lagao.

User bas itna batata hai:
    * kaun se product (links)
    * ek account par cart ki hadd (jaise 5000)
    * kitne order chahiye
    * phone number (jo badle nahi jaate, bas ghoomte hain)

Baaki sab yahin tay hota hai:
    * har order ke liye ek ALAG account ki session (sessions/ folder se)
    * cart links se, keemat range ke andar
    * pata Input_details se, har baar alag
    * discount code Input_details ke column se, random
    * card payment_details se, ek row ek hi baar

Ek account ek hi baar kaam aata hai. Kaun sa account pehle use ho chuka hai --
ye Order_Records tab ke Session_File column se pata chalta hai, kisi alag
list se nahi. Wajah: record wahi ek jagah hai jo har machine par ek jaisi
rehti hai; local file kho sakti hai ya doosre system par hoti hi nahi.
"""
import os
import re
import sys
import glob
import time
import argparse
import traceback

import place_order as po
import order_plan

SESSIONS = po.SESSIONS


def log(*a):
    print(*a, flush=True)


def used_sessions(ord_ws):
    """Jo session pehle kisi order me lag chuki hain."""
    if ord_ws is None:
        return set()
    try:
        vals = ord_ws.get_all_values()
    except Exception as e:
        log("   Order_Records padhi nahi gayi: %s" % str(e)[:90])
        return set()
    if not vals:
        return set()
    head = [c.strip().lower() for c in vals[0]]
    try:
        k = head.index("session_file")
    except ValueError:
        return set()
    return set((r[k] or "").strip() for r in vals[1:] if len(r) > k and r[k].strip())


def free_sessions(ord_ws):
    """sessions/ me padi wo files jo ab tak kisi order me nahi lagi.

    Sabse purani pehle -- taaki jo account sabse pehle bana tha wahi pehle
    kaam aaye, aur naye accounts aage ke liye bachein.
    """
    lagi = used_sessions(ord_ws)
    sab = sorted(glob.glob(os.path.join(SESSIONS, "*.json")),
                 key=os.path.getmtime)
    return [p for p in sab if os.path.basename(p) not in lagi]


def one_order(session_path, links, cart_max, cart_min, n, phones, discount,
              watch, hold, pay_tab="", avoid_emps=None):
    """Ek order. Lautata hai (laga?, record, rc).

    pay_tab   -- card kis tab se (jaise System_1). khali = payment_details.
    avoid_emps-- ye employee id is run me pehle use ho chuki -- inse alag card.
    """
    argv = ["--session", os.path.basename(session_path),
            "--from-sheet",
            "--order-no", str(n),
            "--cart-max", str(cart_max),
            "--watch", str(watch),
            "--hold", str(hold)]
    if cart_min:
        argv += ["--cart-min", str(cart_min)]
    if pay_tab:
        argv += ["--pay-tab", pay_tab]
    for e in avoid_emps or []:
        argv += ["--avoid-emp", e]
    for l in links:
        argv += ["--link", l]
    for ph in phones or []:
        argv += ["--phone", ph]
    if discount:
        argv += ["--discount", discount]

    po.LAST_ORDER.clear()
    rc = po.run_once(po.parse_args(argv))
    rec = dict(po.LAST_ORDER)
    laga = rec.get("Status") == "CONFIRMED"
    return laga, rec, rc


def run_batch(links, cart_max, count, cart_min=0, phones=None, discount="",
              watch=6, hold=15, gap=20, pay_tab="", log=log, should_stop=None,
              on_progress=None):
    """Utne order lagao jitne maange gaye. Lautata hai (lage, fail)."""
    if not links:
        log("koi product link nahi diya -- kuch nahi kar sakte")
        return 0, 0

    ord_ws, kahani = order_plan.open_orders_tab()
    log("sheet : %s -> %s" % (order_plan.ORDER_TAB, kahani))

    khali = free_sessions(ord_ws)
    log("account: %d session bachi hain (jo pehle use nahi hui)" % len(khali))
    if not khali:
        log("koi bina-use account nahi bacha -- pehle naye account banaiye")
        return 0, 0

    pay_ws, _k = order_plan.open_pay_tab(tab=pay_tab or None)
    bache_card = len(order_plan.pending_payments(pay_ws)) if pay_ws else 0
    log("card   : tab '%s' me %d bina-use card"
        % (pay_tab or order_plan.PAY_TAB, bache_card))

    ho_sakte = min(count, len(khali), bache_card or count)
    if ho_sakte < count:
        log("CHETAVNI: %d maange the, par %d hi ho sakte hain "
            "(account %d, card %d)" % (count, ho_sakte, len(khali), bache_card))

    lage = fail = 0
    used_emp = []          # is run me jo employee id le chuke -- dobara nahi
    for n in range(ho_sakte):
        if should_stop is not None and should_stop():
            log("")
            log("[STOP] rok diya gaya -- %d order lag chuke the" % lage)
            break

        sess = khali[n]
        log("")
        log("=" * 66)
        log("ORDER %d/%d   account: %s" % (n + 1, ho_sakte,
                                           os.path.basename(sess)))
        log("=" * 66)
        try:
            laga, rec, rc = one_order(sess, links, cart_max, cart_min, n,
                                      phones, discount, watch, hold,
                                      pay_tab=pay_tab, avoid_emps=used_emp)
            emp = (rec.get("Emp_ID") or "").strip()
            if emp and emp not in used_emp:
                used_emp.append(emp)
        except Exception:
            laga, rec, rc = False, {}, -1
            log("GADBAD:")
            for l in traceback.format_exc().splitlines()[-6:]:
                log("   " + l)

        if laga:
            lage += 1
            log(">>> ORDER LAGA -- %s | Rs %s | %s"
                % (rec.get("Order_Ref", "?"), rec.get("Paid")
                   or rec.get("Cart_Value", "?"), rec.get("Discount_Code", "")))
        else:
            fail += 1
            log(">>> ORDER NAHI LAGA (rc=%s) -- %s"
                % (rc, (rec.get("Note") or "wajah log me upar hai")[:110]))

        if on_progress is not None:
            try:
                on_progress(lage, fail, ho_sakte)
            except Exception:
                pass

        if n + 1 < ho_sakte:
            for _ in range(max(0, int(gap))):
                if should_stop is not None and should_stop():
                    break
                time.sleep(1)
    return lage, fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--link", action="append", default=[],
                    help="product ka link (kai baar de sakte ho)")
    ap.add_argument("--cart-max", type=float, default=5000.0)
    ap.add_argument("--cart-min", type=float, default=0.0,
                    help="0 = cart-max ka 60%%")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--phone", action="append", default=[])
    ap.add_argument("--discount", default="",
                    help="khali = sheet se random")
    ap.add_argument("--watch", type=int, default=6)
    ap.add_argument("--hold", type=int, default=15)
    ap.add_argument("--gap", type=int, default=20)
    ap.add_argument("--pay-tab", default=os.environ.get("ESTUARY_PAY_TAB", ""),
                    help="card kis tab se (jaise System_1). khali = payment_details")
    ap.add_argument("--list", action="store_true",
                    help="sirf batao kitne account/card bache hain")
    a = ap.parse_args()

    if a.list:
        ord_ws, kahani = order_plan.open_orders_tab()
        log("Order_Records -> %s" % kahani)
        khali = free_sessions(ord_ws)
        log("bina-use session: %d" % len(khali))
        for p in khali[:15]:
            log("   %s" % os.path.basename(p))
        pay_ws, k2 = order_plan.open_pay_tab(tab=a.pay_tab or None)
        log("card tab '%s' -> %s" % (a.pay_tab or order_plan.PAY_TAB, k2))
        if pay_ws is not None:
            log("bina-use card   : %d" % len(order_plan.pending_payments(pay_ws)))
        return 0

    lage, fail = run_batch(a.link, a.cart_max, a.count, cart_min=a.cart_min,
                           phones=a.phone, discount=a.discount,
                           watch=a.watch, hold=a.hold, gap=a.gap,
                           pay_tab=a.pay_tab)
    log("")
    log("================ hisaab ================")
    log("   maange gaye : %d" % a.count)
    log("   lag gaye    : %d" % lage)
    log("   nahi lage   : %d" % fail)
    return 0


if __name__ == "__main__":
    sys.exit(main())
