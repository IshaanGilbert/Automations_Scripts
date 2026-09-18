#!/usr/bin/env python3
"""open_session.py -- ek saved session ko Waterfox me khol kar CHHOD do.

Order lagne ke baad khud aankhon se dekhna hota hai ki account me order
pahuncha ya nahi. place_order.py ka browser apna kaam khatam karke band ho
jaata hai, isliye ye alag chhoti script: sirf cookies daalo, /account/orders
khol do, aur window khuli rehne do jab tak tum band na karo.

Ye script session file me kuch LIKHTI NAHI -- sirf padhti hai. Isliye isse
order wali script ki taaza cookies kabhi kharaab nahi hotin.

    python open_session.py                       # sabse nayi session
    python open_session.py estuary_978...json    # koi ek
    python open_session.py --no-proxy            # bina Geonode
"""
import os
import sys
import json
import time
import glob
import argparse

import place_order as po

HERE = po.HERE
SESSIONS = po.SESSIONS
ORDERS_URL = "https://estuaryworld.com/account"


def newest():
    fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
    return fs[-1] if fs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session", nargs="?", default="")
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument("--url", default=ORDERS_URL)
    ap.add_argument("--hold", type=int, default=0,
                    help="0 = jab tak tum band na karo")
    a = ap.parse_args()

    path = a.session or newest()
    if not path:
        print("koi session file nahi mili")
        return 1
    if not os.path.isabs(path):
        p2 = os.path.join(SESSIONS, path)
        path = p2 if os.path.exists(p2) else path
    if not os.path.exists(path):
        print("session file nahi mili:", path)
        return 1

    d = json.load(open(path, encoding="utf-8"))
    print("file    :", os.path.basename(path))
    print("account :", d.get("phone", "?"), "/", d.get("email", "?"))

    port = None
    stop_bridge = None
    if not a.no_proxy:
        user = po.geonode_username(po.GEONODE_COUNTRY, sticky=False)
        port, stop_bridge = po.start_geonode_bridge(user)
        print("proxy   : Geonode | bridge 127.0.0.1:%d" % port)

    driver = po.launch_waterfox(proxy_port=port, headless=False)
    try:
        print("session daal rahe hain...")
        daale = po.load_session(driver, d)
        if not daale:
            print("CHETAVNI: ek bhi cookie nahi gayi -- account logged-out khulega")

        page = po.Scope(driver, driver.current_window_handle)
        page.goto(a.url, timeout=120)
        page.wait_for_timeout(4000)

        # login ka pakka saboot: Shopify khud customerId batata hai
        cid = page.evaluate(
            "return (window.__st && window.__st.cid) ? String(window.__st.cid) : '';")
        print("URL     :", page.url)
        print("login   :", ("HAAN  customerId=%s" % cid) if cid else "NAHI")

        print("")
        print("Window khuli hai -- khud dekh lijiye. Band karne ke liye yahan Enter.")
        if a.hold:
            page.wait_for_timeout(a.hold * 1000)
        else:
            try:
                input()
            except Exception:
                page.wait_for_timeout(1800000)      # 30 minute
    finally:
        # jaan bujh kar save_session NAHI -- ye script sirf padhne ke liye hai
        try:
            driver.quit()
        except Exception:
            pass
        if stop_bridge is not None:
            stop_bridge.set()
    return 0


if __name__ == "__main__":
    sys.exit(main())
