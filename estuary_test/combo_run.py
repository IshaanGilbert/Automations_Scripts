#!/usr/bin/env python3
"""combo_run.py -- ek hi chakkar me: account banao, phir usi par order lagao.

Pehle do alag kaam the: `make_accounts_email.py` account banati thi aur baad
me `order_batch.py` sessions/ folder me padi kisi purani session par order
lagati thi. Beech me haath se ye dekhna padta tha ki kaun sa account bacha
hai. Yahan wo beech ka hissa hi nahi hai:

    Account_emails ki ek khaali row  ->  account ban gaya (session save)
                                     ->  USI session par turant order
                                     ->  dono jagah nateeja likh diya

Ek chakkar = ek account + ek order. Isliye ginti bhi ek hi hai: "5" ka matlab
paanch naye account aur unhi par paanch order.

Kuch baatein jaan-boojh kar aise hain:

* **Card pehle ginte hain, phir account banate hain.** Ek email row aur ek
  card, dono ek hi baar kaam aate hain. Card na bacha ho aur account bana
  diya, to ek email row bekaar kharch ho gayi. Isliye har chakkar se pehle
  card dekh lete hain.
* **Do alag browser.** Account banane ke baad browser band ho jaata hai aur
  order naye browser me, session file se, chalta hai. Ye ghuma-phira ka kaam
  lagta hai par isi se ye pakka hota hai ki session file sach me kaam karti
  hai -- wahi file baad me kisi aur din bhi chalegi. Order wala raasta bhi
  bilkul wahi rehta hai jo pehle se jaanchaa hua hai.
* **Order na lage tab bhi account ka nateeja sheet me rehta hai.** Account bana
  to bana -- uski session bachi rehti hai aur agli baar `order_batch.py` use
  utha sakti hai.

    python combo_run.py --link <url> --link <url> --cart-max 5000 --count 2
    python combo_run.py --list          # sirf ginti dikhao
"""
import os
import sys
import time
import argparse
import traceback
import json

import place_order as po
import order_plan
import order_batch as ob
import sheet_emails
import make_accounts_email as mae


def log(*a):
    print(*a, flush=True)


def sessions_lagao(path):
    """Sessions ka folder poore program ke liye ek jaisa kar do.

    Yahan teen module milte hain aur teeno ne import ke waqt apna raasta yaad
    kar liya tha: account banane wali (jo file LIKHTI hai), order wali (jo
    naam se dhoondhti hai) aur batch wali. Ek jagah badalne se doosri purani
    jagah dekhti reh jaati -- session ek folder me banti aur doosre me
    dhoondhi jaati. Isliye ek hi jagah se teeno set hote hain.
    """
    path = os.path.abspath(path)
    os.environ["ESTUARY_SESSIONS"] = path
    po.SESSIONS = path
    ob.SESSIONS = path
    mae.SESSIONS = path
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass
    return path


# import ke waqt hi teeno ko ek line par le aao
sessions_lagao(po.SESSIONS)


def _order_note(laga, rec):
    """Account_emails ki Note me jaane wali chhoti si line."""
    if laga:
        return "order %s | Rs %s | %s" % (
            rec.get("Acct_Order_No") or rec.get("Order_Ref") or "?",
            rec.get("Paid") or rec.get("Cart_Value") or "?",
            rec.get("Discount_Code") or "")
    return "order nahi laga: %s" % (rec.get("Note") or "wajah log me")[:120]


def one_cycle(row, links, cart_max, cart_min, n, phones, discount,
              watch, hold, proxy_port, email_ws, pay_tab="", avoid_emps=None,
              log=log):
    """Ek row -> account -> usi par order. Lautata hai (kya_hua, rec).

    kya_hua: "done" (dono ho gaye) | "acct_fail" | "order_fail" | "skip"
    """
    # ---------------- 1) account ----------------
    # Kahin beech me kisi aur ne to ye row nahi utha li? Ye poochhna sasta hai
    # (ek khaana) aur bachata bahut kuch hai -- ek hi email par do jagah
    # account banne se dono taraf gadbad hoti hai.
    if not sheet_emails.still_free(email_ws, row["row"]):
        log("   row %d beech me kisi aur ne le li -- chhod kar aage badhte hain"
            % row["row"])
        return "skip", {}

    log("   [1/2] account bana rahe hain (usi browser me order bhi lagega) -- "
        "%s %s <%s>" % (row["first"], row["last"], row["email"]))
    # Row pehle apne naam kar lo, phir kaam. Beech me kuch bhi ho jaye to ye
    # row dobara na uthe -- ho sakta hai account ban chuka ho.
    sheet_emails.claim(email_ws, row["row"])

    # EK HI BROWSER: pehle account banao, phir usi khule browser me turant order
    # laga do, aur ant me band. Pehle account ban kar browser band hota tha, phir
    # order ke liye naya browser session file se khulta tha -- ab wo do-baar
    # khulna-band hona hata diya.
    cid = ""
    sess_name = ""
    driver = None
    laga, rec, rc = False, {}, -1
    try:
        try:
            driver = po.launch_waterfox(proxy_port=proxy_port, headless=False)
        except Exception as e:
            sheet_emails.mark(email_ws, row["row"], sheet_emails.FAIL,
                              "", "", "browser nahi khuli: %s" % str(e)[:90])
            log("   [sheet] row %d -> failed (browser nahi khuli)" % row["row"])
            return "acct_fail", {}

        page = po.Scope(driver, driver.current_window_handle)
        ok, note, cid = mae.create_account(page, row)
        if not ok:
            sheet_emails.mark(email_ws, row["row"], sheet_emails.FAIL,
                              "", cid, note)
            log("   [sheet] row %d -> failed (%s)" % (row["row"], (note or "?")[:90]))
            try:
                driver.quit()
            except Exception:
                pass
            return "acct_fail", {}

        log("      account ban gaya: customerId=%s" % cid)
        # Session file record ke liye -- baad me kabhi isi account par phir
        # order lagana ho to kaam aati hai. Save na bhi ho to order isi khule
        # browser me lag jayega (login to ho hi chuka hai).
        sess_name = mae.save_the_session(driver, row, cid)
        if sess_name:
            sess_path = os.path.join(mae.SESSIONS, sess_name)
            try:
                d = json.load(open(sess_path, encoding="utf-8"))
            except Exception:
                d = {}
        else:
            sess_path = ""
            d = {"email": row["email"], "customer_id": cid, "phone": "9999999999",
                 "first_name": row["first"], "last_name": row["last"]}
        sheet_emails.mark(email_ws, row["row"], sheet_emails.DONE,
                          sess_name, cid, "account bana, usi browser me order chalu")
        log("   [sheet] row %d -> complete | session %s"
            % (row["row"], sess_name or "(save nahi hui)"))

        # ---------------- 2) USI browser me order ----------------
        log("   [2/2] usi khule browser me order laga rahe hain")
        argv = ["--from-sheet",
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
        if sess_name:
            argv += ["--session", sess_name]

        po.LAST_ORDER.clear()
        # driver inject: naya browser nahi khulega, session load nahi hogi,
        # proxy wahi rahegi. own_close=True -- order ke ant me browser band.
        rc = po.run_once(po.parse_args(argv), driver=driver, own_close=True,
                         acct=d, session_path=sess_path)
        driver = None            # run_once ne band kar diya
        rec = dict(po.LAST_ORDER)
        laga = rec.get("Status") == "CONFIRMED"
    except Exception:
        log("   GADBAD (chakkar):")
        for l in traceback.format_exc().splitlines()[-6:]:
            log("      " + l)
        laga, rec, rc = False, {}, -1
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass

    # Account wali row me bhi likh do ki us account par kya hua.
    sheet_emails.mark(email_ws, row["row"], sheet_emails.DONE, sess_name,
                      cid, _order_note(laga, rec))

    if laga:
        log("   >>> ORDER LAGA -- %s | Rs %s | %s"
            % (rec.get("Order_Ref", "?"),
               rec.get("Paid") or rec.get("Cart_Value", "?"),
               rec.get("Discount_Code", "")))
        return "done", rec
    log("   >>> ORDER NAHI LAGA (rc=%s) -- %s"
        % (rc, (rec.get("Note") or "wajah log me upar hai")[:110]))
    return "order_fail", rec


def run_combo(links, cart_max, count, cart_min=0, phones=None, discount="",
              watch=6, hold=15, gap=20, proxy_port=None, email_ws=None,
              pay_tab="", log=log, should_stop=None, on_progress=None):
    """Utne chakkar chalao jitne maange gaye. Lautata hai (lage, fail).

    log / should_stop / on_progress isliye hain ki yahi function GUI se bhi
    seedha chalta hai.
    """
    if not links:
        log("koi product link nahi diya -- kuch nahi kar sakte")
        return 0, 0

    if email_ws is None:
        email_ws, kahani = sheet_emails.open_tab()
        log("sheet : %s -> %s" % (sheet_emails.TAB, kahani))
        if email_ws is None:
            return 0, 0

    ord_ws, kahani = order_plan.open_orders_tab()
    log("sheet : %s -> %s" % (order_plan.ORDER_TAB, kahani))

    # Zaroorat se thodi zyada rows utha lete hain. Kuch beech me kisi aur
    # script ke haath lag sakti hain -- tab agli row se kaam chal jaata hai,
    # dobara poori sheet padhne ki nahi padti.
    baaki = sheet_emails.pending(email_ws, limit=count + 10)
    log("email : %d khaali row mili (maange gaye %d)" % (len(baaki), count))
    if not baaki:
        log("Account_emails me koi khaali row nahi bachi -- pehle sheet me "
            "naye email/password daaliye")
        return 0, 0

    pay_ws, _k = order_plan.open_pay_tab(tab=pay_tab or None)
    bache_card = len(order_plan.pending_payments(pay_ws)) if pay_ws else 0
    log("card  : tab '%s' me %d bina-use card"
        % (pay_tab or order_plan.PAY_TAB, bache_card))
    if not bache_card:
        log("payment_details me ek bhi bina-use card nahi -- order nahi lag "
            "payega, isliye account bhi nahi bana rahe")
        return 0, 0

    ho_sakte = min(count, len(baaki), bache_card)
    if ho_sakte < count:
        log("CHETAVNI: %d maange the, par %d hi ho sakte hain "
            "(email row %d, card %d)" % (count, ho_sakte, len(baaki), bache_card))

    lage = fail = 0
    n = 0                    # kaun sa chakkar (pata/cart isi se ghoomta hai)
    used_emp = []            # is run me jo employee id le chuke -- dobara nahi
    for row in baaki:
        if n >= ho_sakte:
            break
        if should_stop is not None and should_stop():
            log("")
            log("[STOP] rok diya gaya -- %d order lag chuke the" % lage)
            break

        log("")
        log("=" * 66)
        log("CHAKKAR %d/%d   row %d   %s %s   <%s>"
            % (n + 1, ho_sakte, row["row"], row["first"], row["last"],
               row["email"]))
        log("=" * 66)

        try:
            kya, rec = one_cycle(row, links, cart_max, cart_min, n, phones,
                                 discount, watch, hold, proxy_port, email_ws,
                                 pay_tab=pay_tab, avoid_emps=used_emp, log=log)
            emp = (rec.get("Emp_ID") or "").strip()
            if emp and emp not in used_emp:
                used_emp.append(emp)
        except Exception:
            kya = "acct_fail"
            log("GADBAD:")
            for l in traceback.format_exc().splitlines()[-6:]:
                log("   " + l)

        if kya == "skip":
            # Ye chakkar hua hi nahi -- na ginti badhti hai, na intezaar.
            continue

        n += 1
        if kya == "done":
            lage += 1
        else:
            fail += 1

        if on_progress is not None:
            try:
                on_progress(lage, fail, ho_sakte)
            except Exception:
                pass

        if n < ho_sakte:
            for _ in range(max(0, int(gap))):
                if should_stop is not None and should_stop():
                    break
                time.sleep(1)
    return lage, fail


def main():
    ap = argparse.ArgumentParser(
        description="account banao aur usi par turant order lagao")
    ap.add_argument("--link", action="append", default=[],
                    help="product ka link (kai baar de sakte ho)")
    ap.add_argument("--cart-max", type=float, default=5000.0)
    ap.add_argument("--cart-min", type=float, default=0.0,
                    help="0 = cart-max ka 60%%")
    ap.add_argument("--count", type=int, default=1,
                    help="kitne account+order (ek chakkar = ek account, ek order)")
    ap.add_argument("--phone", action="append", default=[])
    ap.add_argument("--discount", default="", help="khali = sheet se random")
    ap.add_argument("--watch", type=int, default=6)
    ap.add_argument("--hold", type=int, default=15)
    ap.add_argument("--gap", type=int, default=20,
                    help="do chakkar ke beech kitne second")
    ap.add_argument("--pay-tab", default=os.environ.get("ESTUARY_PAY_TAB", ""),
                    help="card kis tab se (jaise System_1). khali = payment_details")
    ap.add_argument("--tab", default=sheet_emails.TAB)
    ap.add_argument("--no-proxy", action="store_true",
                    help="account banate waqt proxy band (order apni proxy "
                         "khud uthata hai)")
    ap.add_argument("--proxy-country", default=po.GEONODE_COUNTRY)
    ap.add_argument("--list", action="store_true",
                    help="sirf batao kitni email row aur kitne card bache hain")
    a = ap.parse_args()

    email_ws, kahani = sheet_emails.open_tab(tab=a.tab)
    log("sheet : tab '%s' -> %s" % (a.tab, kahani))
    if email_ws is None:
        return 1

    if a.list:
        baaki = sheet_emails.pending(email_ws)
        log("khaali email row : %d" % len(baaki))
        for r in baaki[:15]:
            log("   row %-4d %-12s %-12s %s"
                % (r["row"], r["first"], r["last"], r["email"]))
        pay_ws, k2 = order_plan.open_pay_tab(tab=a.pay_tab or None)
        log("card tab '%s'  -> %s" % (a.pay_tab or order_plan.PAY_TAB, k2))
        if pay_ws is not None:
            log("bina-use card    : %d"
                % len(order_plan.pending_payments(pay_ws)))
        log("ho sakte hain    : %d chakkar" % min(
            len(baaki),
            len(order_plan.pending_payments(pay_ws)) if pay_ws else 0))
        return 0

    if not a.link:
        log("kam se kam ek --link do")
        return 1

    # Account banane wali proxy. Order apni proxy khud uthata hai (har order ke
    # liye naya IP) -- isliye yahan sirf account wala hissa dekhna hai.
    port = None
    stop_bridge = None
    if not a.no_proxy:
        user = po.geonode_username(a.proxy_country, sticky=False)
        try:
            port, stop_bridge = po.start_geonode_bridge(user)
            log("proxy : Geonode %s | bridge 127.0.0.1:%d"
                % (a.proxy_country, port))
        except Exception as e:
            log("proxy : shuru nahi hui (%s) -- bina proxy chalenge" % str(e)[:80])
    else:
        log("proxy : OFF (account banane me)")

    lage = fail = 0
    try:
        lage, fail = run_combo(a.link, a.cart_max, a.count, cart_min=a.cart_min,
                               phones=a.phone, discount=a.discount,
                               watch=a.watch, hold=a.hold, gap=a.gap,
                               proxy_port=port, email_ws=email_ws,
                               pay_tab=a.pay_tab)
    except KeyboardInterrupt:
        log("\n(rok diya gaya)")
    except Exception:
        log("\nGADBAD:")
        for l in traceback.format_exc().splitlines()[-8:]:
            log("   " + l)
    finally:
        if stop_bridge is not None:
            stop_bridge.set()

    log("")
    log("================ hisaab ================")
    log("   maange gaye : %d" % a.count)
    log("   poore hue   : %d  (account + order)" % lage)
    log("   adhoore     : %d" % fail)
    log("   sessions    : %s" % po.SESSIONS)
    log("   record      : %s tab" % order_plan.ORDER_TAB)
    return 0


if __name__ == "__main__":
    sys.exit(main())
