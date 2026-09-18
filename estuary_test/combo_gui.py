#!/usr/bin/env python3
"""combo_gui.py -- ek window: account bhi banao, usi par order bhi lagao.

Pehle do window the -- ek account banane ka, doosra order lagane ka -- aur
beech me ye dekhna padta tha ki kaun sa naya account bacha hai. Yahan wo beech
ka kadam hai hi nahi: har chakkar me pehle ek naya account banta hai, phir usi
par turant order lagta hai.

"Kitne" ka matlab isliye ek hi ginti hai: 3 daala to teen naye account aur unhi
par teen order.

Dhaancha wahi hai jo doosri GUI ka hai, aur usi wajah se:
* Browser wala kaam ALAG THREAD me chalta hai -- warna window jam jaata.
* Thread se widget ko seedha haath nahi lagate; sab Queue se hota hai.
* Har line gui_log_combo.txt me bhi jaati hai -- exe me console hota hi nahi.
"""
import os
import sys
import time
import queue
import threading
import traceback
import webbrowser

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class _Sink(object):
    """Windowed exe me sys.stdout/stderr hote hi nahi (None hote hain).

    Sirf write/flush kaafi nahi: place_order import hote hi
    `sys.stdout.reconfigure(...)` chalata hai. Isliye wo saari cheezein yahan
    hain jo ek asli text stream me hoti hain.
    """

    encoding = "utf-8"
    errors = "replace"

    def write(self, s):
        return len(s) if s else 0

    def writelines(self, lines):
        for _ in lines:
            pass

    def flush(self):
        pass

    def close(self):
        pass

    def reconfigure(self, *a, **kw):
        pass

    def isatty(self):
        return False

    def readable(self):
        return False

    def writable(self):
        return True

    def seekable(self):
        return False

    def fileno(self):
        raise OSError("is dhaare ka koi fileno nahi hai")


if sys.stdout is None:
    sys.stdout = _Sink()
if sys.stderr is None:
    sys.stderr = _Sink()

import json                       # noqa: E402
import place_order as po          # noqa: E402
import order_plan                 # noqa: E402
import sheet_emails               # noqa: E402
import combo_run as cr            # noqa: E402
import sheet_log                  # noqa: E402

APP = "Estuary Account + Order"
LOGFILE = os.path.join(po.HERE, "gui_log_combo.txt")
SETTINGS = os.path.join(po.HERE, "combo_gui_settings.json")
SHEET_URL = "https://docs.google.com/spreadsheets/d/%s" % sheet_log.SHEET_ID

MISAAL = """https://estuaryworld.com/collections/diageo-brands/products/johnnie-walker-luxe-blended-water
https://estuaryworld.com/collections/blending-water/products/single-malt-blending-water-200ml
https://estuaryworld.com/collections/blending-water/products/godawan-estuary-premium-water-1"""


def yaad_padho():
    try:
        with open(SETTINGS, encoding="utf-8") as fh:
            return json.load(fh) or {}
    except Exception:
        return {}


def yaad_likho(d):
    try:
        with open(SETTINGS, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=1)
    except Exception:
        pass


class App(object):
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()
        self.worker = None
        self.stop_flag = threading.Event()

        root.title(APP)
        root.geometry("980x740")
        root.minsize(840, 620)

        self._build()
        self.root.after(100, self._drain)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.say("%s taiyaar hai." % APP)
        self.say("Har chakkar me: pehle naya account banega, phir USI account "
                 "par order lagega.")
        self.say("Account_emails sheet se email/password uthte hain, card "
                 "payment_details se.")
        self.say("naye account yahan bante hain: %s" % po.SESSIONS)
        self.say("Kai instance ek saath: 'Kitne instance' me ginti do (jaise "
                 "4). Card tab me comma se alag tab de sakte ho -- "
                 "System_1,System_2,System_3,System_4.")
        self.say("Ek hi employee id do jagah ek saath na chale iska dhyaan "
                 "script khud rakhti hai (RUNNING wale card chhod deti hai).")
        self.say("")

    # ------------------------------------------------------------ window
    def _build(self):
        pad = {"padx": 8, "pady": 6}

        lf = ttk.LabelFrame(self.root,
                            text=" Kaun se product (ek line me ek link) ")
        lf.pack(fill="x", **pad)
        self.links = tk.Text(lf, height=5, wrap="none", font=("Consolas", 9))
        self.links.pack(fill="x", padx=8, pady=8)
        self.links.insert("1.0", MISAAL)

        sf = ttk.LabelFrame(self.root, text=" Kitna aur kaise ")
        sf.pack(fill="x", **pad)

        ttk.Label(sf, text="Ek account par cart ki hadd (Rs):").grid(
            row=0, column=0, sticky="w", padx=8, pady=6)
        self.max_var = tk.StringVar(value="5000")
        ttk.Entry(sf, width=10, textvariable=self.max_var).grid(
            row=0, column=1, sticky="w")

        ttk.Label(sf, text="Kam se kam (0 = hadd ka 60%):").grid(
            row=0, column=2, sticky="e", padx=(20, 8))
        self.min_var = tk.StringVar(value="0")
        ttk.Entry(sf, width=10, textvariable=self.min_var).grid(
            row=0, column=3, sticky="w")

        ttk.Label(sf, text="Kitne account + order:").grid(
            row=1, column=0, sticky="w", padx=8, pady=6)
        self.count_var = tk.StringVar(value="1")
        ttk.Spinbox(sf, from_=1, to=500, width=8,
                    textvariable=self.count_var).grid(row=1, column=1, sticky="w")

        ttk.Label(sf, text="Phone (comma se alag):").grid(
            row=1, column=2, sticky="e", padx=(20, 8))
        self.phone_var = tk.StringVar(value="")
        ttk.Entry(sf, width=28, textvariable=self.phone_var).grid(
            row=1, column=3, sticky="w")

        ttk.Label(sf, text="Discount code (khali = sheet se random):").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=8, pady=6)
        self.disc_var = tk.StringVar(value="")
        ttk.Entry(sf, width=16, textvariable=self.disc_var).grid(
            row=2, column=2, sticky="e")

        ttk.Label(sf, text="Do chakkar ke beech (sec):").grid(
            row=2, column=3, sticky="e", padx=(20, 8))
        self.gap_var = tk.StringVar(value="20")
        ttk.Spinbox(sf, from_=0, to=600, width=6,
                    textvariable=self.gap_var).grid(row=2, column=4, sticky="w")

        ttk.Label(sf, text="Naye account (sessions) ka folder:").grid(
            row=3, column=0, sticky="w", padx=8, pady=6)
        self.sess_var = tk.StringVar(value=po.SESSIONS)
        ttk.Entry(sf, width=52, textvariable=self.sess_var).grid(
            row=3, column=1, columnspan=3, sticky="w")
        ttk.Button(sf, text="Badlo", command=self._pick_sessions).grid(
            row=3, column=4, sticky="w", padx=6)

        ttk.Label(sf, text="Kitne instance (ek saath):").grid(
            row=1, column=4, sticky="e", padx=(20, 8))
        self.inst_var = tk.StringVar(value="1")
        ttk.Spinbox(sf, from_=1, to=20, width=5,
                    textvariable=self.inst_var).grid(row=1, column=5, sticky="w")

        ttk.Label(sf, text="Card tab (System_1,System_2 ...):").grid(
            row=4, column=0, sticky="w", padx=8, pady=6)
        self.paytab_var = tk.StringVar(value="")
        ttk.Entry(sf, width=32, textvariable=self.paytab_var).grid(
            row=4, column=1, columnspan=2, sticky="w")
        ttk.Label(sf, text="(comma se -- har instance ko alag; khali=payment_details)").grid(
            row=4, column=3, columnspan=3, sticky="w")

        # Account banate waqt proxy. Order apni proxy khud uthata hai, isliye
        # ye sirf pehle aadhe hisse ka switch hai.
        self.proxy_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sf, text="Account banate waqt proxy (Geonode)",
                        variable=self.proxy_var).grid(
            row=5, column=0, columnspan=3, sticky="w", padx=8, pady=(0, 6))

        btns = ttk.Frame(self.root)
        btns.pack(fill="x", padx=8)
        self.start_btn = ttk.Button(btns, text="Shuru karo", command=self.start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(btns, text="Roko", command=self.stop,
                                   state="disabled")
        self.stop_btn.pack(side="left", padx=6)
        ttk.Button(btns, text="Kitni email row / card bache",
                   command=self.refresh_counts).pack(side="left")
        ttk.Button(btns, text="Sheet kholo",
                   command=lambda: webbrowser.open(SHEET_URL)).pack(
            side="left", padx=6)
        ttk.Button(btns, text="sessions folder",
                   command=self._open_sessions).pack(side="left")

        pf = ttk.Frame(self.root)
        pf.pack(fill="x", **pad)
        self.bar = ttk.Progressbar(pf, mode="determinate")
        self.bar.pack(fill="x")
        self.status = tk.StringVar(value="taiyaar")
        ttk.Label(pf, textvariable=self.status).pack(anchor="w", pady=(4, 0))

        lgf = ttk.LabelFrame(self.root, text=" Chal kya raha hai ")
        lgf.pack(fill="both", expand=True, **pad)
        self.log = tk.Text(lgf, wrap="none", height=16,
                           bg="#101418", fg="#d8e0e8",
                           insertbackground="#d8e0e8",
                           font=("Consolas", 9))
        sb = ttk.Scrollbar(lgf, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set, state="disabled")
        sb.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)

        for tag, col in (("ok", "#7ee787"), ("fail", "#ff7b72"),
                         ("head", "#79c0ff"), ("warn", "#e3b341")):
            self.log.tag_configure(tag, foreground=col)

    def _pick_sessions(self):
        got = filedialog.askdirectory(title="sessions folder chuno",
                                      initialdir=self.sess_var.get() or po.HERE)
        if not got:
            return
        path = cr.sessions_lagao(got)
        self.sess_var.set(path)
        yaad_likho({"sessions": path})
        self.say("sessions folder: %s" % path)

    def _open_sessions(self):
        try:
            os.startfile(self.sess_var.get() or po.SESSIONS)
        except Exception:
            messagebox.showinfo(APP, self.sess_var.get() or po.SESSIONS)

    # ------------------------------------------------------------ log
    def say(self, line=""):
        self.q.put(("log", str(line)))

    def _drain(self):
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == "log":
                    self._write(payload)
                elif kind == "progress":
                    lage, fail, kul = payload
                    self.bar["maximum"] = max(1, kul)
                    self.bar["value"] = lage + fail
                    self.status.set("poore: %d   |   adhoore: %d   |   kul: %d"
                                    % (lage, fail, kul))
                elif kind == "counts":
                    self.status.set(payload)
                elif kind == "done":
                    self._finish(payload)
        except queue.Empty:
            pass
        self.root.after(100, self._drain)

    def _write(self, line):
        tag = ""
        low = line.lower()
        if "order laga" in low or "ban gaya" in low or "-> complete" in low:
            tag = "ok"
        elif "nahi laga" in low or "fail" in low or "gadbad" in low:
            tag = "fail"
        elif line.startswith("=====") or line.startswith("CHAKKAR"):
            tag = "head"
        elif "chetavni" in low or "[stop]" in low:
            tag = "warn"

        self.log.configure(state="normal")
        self.log.insert("end", line + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")
        try:
            with open(LOGFILE, "a", encoding="utf-8") as fh:
                fh.write("%s %s\n" % (time.strftime("%H:%M:%S"), line))
        except Exception:
            pass

    # ------------------------------------------------------------ ginti
    def refresh_counts(self):
        """Sheet padhna network ka kaam hai -- window ke thread me nahi."""
        def kaam():
            try:
                ws, _k = sheet_emails.open_tab()
                rows = len(sheet_emails.pending(ws)) if ws is not None else 0
                pay_ws, _k2 = order_plan.open_pay_tab()
                card = len(order_plan.pending_payments(pay_ws)) if pay_ws else 0
                self.q.put(("counts", "khaali email row: %d   |   "
                                      "bina-use card: %d   |   ho sakte hain: %d"
                                      % (rows, card, min(rows, card))))
                self.say("khaali email row: %d | bina-use card: %d | "
                         "ho sakte hain: %d" % (rows, card, min(rows, card)))
            except Exception as e:
                self.say("ginti nahi ho payi: %s" % str(e)[:120])

        threading.Thread(target=kaam, daemon=True).start()

    # ------------------------------------------------------------ chalao
    def _links(self):
        raw = self.links.get("1.0", "end")
        return [l.strip() for l in raw.splitlines() if l.strip()]

    def start(self):
        links = self._links()
        if not links:
            messagebox.showerror(APP, "Kam se kam ek product ka link daaliye.")
            return
        try:
            cart_max = float(self.max_var.get())
            cart_min = float(self.min_var.get() or 0)
            count = int(self.count_var.get())
            gap = int(self.gap_var.get())
        except ValueError:
            messagebox.showerror(APP, "Ginti sahi likhiye (jaise 5000 aur 3).")
            return
        if cart_max <= 0:
            messagebox.showerror(APP, "Cart ki hadd 0 se badi honi chahiye.")
            return
        if cart_min and cart_min >= cart_max:
            messagebox.showerror(
                APP, "Kam se kam wali rakam hadd se chhoti honi chahiye.")
            return

        try:
            instances = max(1, int(self.inst_var.get()))
        except ValueError:
            messagebox.showerror(APP, "Instance ki ginti sahi likhiye (jaise 4).")
            return

        phones = [p.strip() for p in self.phone_var.get().replace(";", ",")
                  .split(",") if p.strip()]

        path = cr.sessions_lagao(self.sess_var.get() or po.SESSIONS)
        self.sess_var.set(path)
        pay_tab = self.paytab_var.get().strip()
        yaad_likho({"sessions": path, "pay_tab": pay_tab})

        # Card tab comma se: har instance ko ek. Ek hi tab diya to sab wahi
        # (lock ka bharosa). Khali diya to payment_details.
        tabs = [t.strip() for t in pay_tab.replace(";", ",").split(",")
                if t.strip()]
        inst_tabs = [(tabs[i % len(tabs)] if tabs else "")
                     for i in range(instances)]

        # count = HAR instance ka. 4 instance + count 1 = 4 order (har instance
        # ek). Isliye har instance ko poora count milta hai; kul = count x
        # instance. (Pehle count ko baant dete the, isliye 4 instance + count 1
        # par sirf 1 hi chalta tha -- baaki 3 ko 0 milta tha.)
        shares = [count] * instances
        total = count * instances
        inst_tabs = inst_tabs[:instances]

        self.stop_flag.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.bar["maximum"] = total
        self.bar["value"] = 0
        self.status.set("shuru kar rahe hain... (%d instance)" % instances)

        self.worker = threading.Thread(
            target=self._run_multi,
            args=(links, cart_max, cart_min, shares, inst_tabs, phones,
                  self.disc_var.get().strip(), gap, self.proxy_var.get(),
                  total),
            daemon=True)
        self.worker.start()

    def stop(self):
        self.stop_flag.set()
        self.stop_btn.configure(state="disabled")
        self.say("")
        self.say("[STOP] rok rahe hain -- abhi wala chakkar poora hone do...")

    def _run_multi(self, links, cart_max, cart_min, shares, inst_tabs, phones,
                   discount, gap, proxy, total):
        """ALAG THREAD. Utne worker thread chalao jitne instance maange gaye,
        aur sabke poore hone tak ruko. Yahan se koi widget nahi chhua jaata --
        sab kuch self.q ke zariye.

        Har worker apni alag Waterfox aur apni alag card tab par chalta hai.
        Do worker ek hi employee id par ek saath OTP nahi mangwayenge -- card
        ka claim_next_card RUNNING wale emp id ko chhod deta hai (chahe wo
        doosre instance ne pakda ho, kyunki wo bhi usi sheet par likhta hai).
        """
        n = len(shares)
        self._agg = [(0, 0)] * n           # har instance ka (lage, fail)
        self._agg_total = total
        self._agg_lock = threading.Lock()

        self.say("=" * 66)
        self.say("%d instance ek saath | kul %d account+order | cart hadd Rs %.2f"
                 % (n, total, cart_max))
        for l in links:
            self.say("   link: %s" % l)
        self.say("   phone: %s" % (", ".join(phones) or "(sheet se)"))
        self.say("   discount: %s" % (discount or "(sheet se random)"))
        for i in range(n):
            self.say("   instance %d -> %d order | card tab: %s"
                     % (i + 1, shares[i], inst_tabs[i] or "payment_details"))
        self.say("=" * 66)

        threads = []
        for i in range(n):
            t = threading.Thread(
                target=self._worker,
                args=(i, links, cart_max, cart_min, shares[i], inst_tabs[i],
                      phones, discount, gap, proxy),
                daemon=True)
            threads.append(t)
            t.start()
            # Thoda saans -- ek saath 4 proxy bridge + 4 Waterfox ek hi pal me
            # uthana bhaari padta hai; 2 second ke antar par sab zyada
            # bharosemand khulti hain.
            time.sleep(2)

        for t in threads:
            t.join()

        lage = sum(a for a, _ in self._agg)
        fail = sum(b for _, b in self._agg)
        self.q.put(("done", (lage, fail, total)))

    def _worker(self, idx, links, cart_max, cart_min, share, pay_tab, phones,
                discount, gap, proxy):
        """Ek instance. Apni proxy, apni Waterfox, apni card tab."""
        tag = "[I%d]" % (idx + 1)

        def say(line=""):
            self.q.put(("log", "%s %s" % (tag, line)))

        def progress(a, b, c):
            with self._agg_lock:
                self._agg[idx] = (a, b)
                la = sum(x for x, _ in self._agg)
                fa = sum(y for _, y in self._agg)
            self.q.put(("progress", (la, fa, self._agg_total)))

        stop_bridge = None
        try:
            port = None
            if proxy:
                try:
                    user = po.geonode_username(po.GEONODE_COUNTRY, sticky=False)
                    port, stop_bridge = po.start_geonode_bridge(user)
                    say("proxy : Geonode | bridge 127.0.0.1:%d" % port)
                except Exception as e:
                    say("proxy : shuru nahi hui (%s) -- bina proxy" % str(e)[:70])
            else:
                say("proxy : OFF")

            # email_ws=None -- har worker apna alag sheet handle khole. gspread
            # ke handle thread ke beech share karna theek nahi.
            cr.run_combo(
                links, cart_max, share, cart_min=cart_min, phones=phones,
                discount=discount, gap=gap, proxy_port=port, pay_tab=pay_tab,
                email_ws=None,
                log=say,
                should_stop=self.stop_flag.is_set,
                on_progress=progress,
            )
        except Exception:
            say("GADBAD:")
            for l in traceback.format_exc().splitlines()[-8:]:
                say("   " + l)
        finally:
            if stop_bridge is not None:
                try:
                    stop_bridge.set()
                except Exception:
                    pass

    def _finish(self, payload):
        lage, fail, count = payload
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.say("")
        self.say("=" * 66)
        self.say("   maange gaye : %d" % count)
        self.say("   poore hue   : %d  (account + order)" % lage)
        self.say("   adhoore     : %d" % fail)
        self.say("   record      : %s tab" % order_plan.ORDER_TAB)
        self.say("=" * 66)
        self.status.set("khatam -- poore: %d, adhoore: %d" % (lage, fail))
        self.refresh_counts()
        if lage and not fail:
            messagebox.showinfo(APP, "%d account bane aur unhi par %d order "
                                     "lag gaye." % (lage, lage))
        elif lage:
            messagebox.showwarning(
                APP, "%d poore hue, %d adhoore.\n\nAccount_emails ke Note aur "
                     "Order_Records ke Note me wajah likhi hai." % (lage, fail))
        else:
            messagebox.showwarning(APP, "Ek bhi chakkar poora nahi hua.\n\n"
                                        "Log me wajah likhi hai.")

    def _on_close(self):
        if self.worker is not None and self.worker.is_alive():
            if not messagebox.askyesno(
                    APP, "Kaam abhi chal raha hai. Band karna hai?\n\n"
                         "(Browser khula reh sakta hai, aur beech ka order "
                         "adhoora rah sakta hai.)"):
                return
            self.stop_flag.set()
        self.root.destroy()


def main():
    yaad = yaad_padho()
    if yaad.get("sessions"):
        cr.sessions_lagao(yaad["sessions"])
    root = tk.Tk()
    root._yaad_paytab = yaad.get("pay_tab", "")
    try:
        ttk.Style().theme_use("vista")
    except Exception:
        pass
    app = App(root)
    if getattr(root, "_yaad_paytab", ""):
        app.paytab_var.set(root._yaad_paytab)
    root.after(500, app.refresh_counts)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
