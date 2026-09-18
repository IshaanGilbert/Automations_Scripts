#!/usr/bin/env python3
"""order_gui.py -- order lagane ka window.

User se sirf chaar cheezein poochhi jaati hain:

    * kaun se product   -- link, ek line me ek
    * ek account par cart ki hadd   -- jaise 5000
    * kitne order chahiye
    * phone number      -- ye badle nahi jaate, bas ghoomte hain

Baaki sab sheet aur script tay karte hain: har order ke liye alag account,
alag pata, random discount code, aur agla bina-use card. Har lage hue order
ki poori line 'Order_Records' tab me jaati hai.

Dhaancha wahi hai jo account wali GUI ka hai, aur usi wajah se:
* Browser wala kaam ALAG THREAD me chalta hai -- warna window jam jaata.
* Thread se widget ko seedha haath nahi lagate; sab kuch Queue se hota hai.
* Har line gui_log_order.txt me bhi jaati hai -- exe me console hota hi nahi.
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
import order_batch as ob          # noqa: E402
import order_plan                 # noqa: E402
import sheet_log                  # noqa: E402

APP = "Estuary Order Runner"
LOGFILE = os.path.join(po.HERE, "gui_log_order.txt")
# Chuna hua sessions folder yahin yaad rehta hai -- har baar dobara
# batana na pade.
SETTINGS = os.path.join(po.HERE, "order_gui_settings.json")
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


def sessions_lagao(path):
    """Sessions ka folder poore program ke liye badal do.

    Teen exe hain: do account banati hain, ek order lagati hai. Har exe apne
    folder me chalti hai, isliye order wali exe ko un accounts tak pahunchna
    hota hai jo doosri exe ne kahin aur banaye. Module import ke waqt raasta
    tay ho jaata hai, isliye teeno jagah badalna padta hai -- sirf ek jagah
    badalne se doosri module purani jagah dekhti reh jaati hai.
    """
    path = os.path.abspath(path)
    os.environ["ESTUARY_SESSIONS"] = path
    po.SESSIONS = path
    ob.SESSIONS = path
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass
    return path


class App(object):
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()
        self.worker = None
        self.stop_flag = threading.Event()

        root.title(APP)
        root.geometry("960x720")
        root.minsize(820, 600)

        self._build()
        self.root.after(100, self._drain)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.say("%s taiyaar hai." % APP)
        self.say("Product ke link daaliye (ek line me ek), cart ki hadd aur "
                 "ginti likhiye, phir 'Shuru karo'.")
        self.say("accounts (sessions) ka folder: %s" % po.SESSIONS)
        self.say("")

    # ------------------------------------------------------------ window
    def _build(self):
        pad = {"padx": 8, "pady": 6}

        # ---- links ----
        lf = ttk.LabelFrame(self.root, text=" Kaun se product (ek line me ek link) ")
        lf.pack(fill="x", **pad)
        self.links = tk.Text(lf, height=5, wrap="none", font=("Consolas", 9))
        self.links.pack(fill="x", padx=8, pady=8)
        self.links.insert("1.0", MISAAL)

        # ---- settings ----
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

        ttk.Label(sf, text="Kitne order:").grid(
            row=1, column=0, sticky="w", padx=8, pady=6)
        self.count_var = tk.StringVar(value="1")
        self.count_box = ttk.Spinbox(sf, from_=1, to=500, width=8,
                                     textvariable=self.count_var)
        self.count_box.grid(row=1, column=1, sticky="w")

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

        ttk.Label(sf, text="Accounts (sessions) ka folder:").grid(
            row=3, column=0, sticky="w", padx=8, pady=6)
        self.sess_var = tk.StringVar(value=po.SESSIONS)
        ttk.Entry(sf, width=52, textvariable=self.sess_var).grid(
            row=3, column=1, columnspan=3, sticky="w")
        ttk.Button(sf, text="Badlo", command=self._pick_sessions).grid(
            row=3, column=4, sticky="w", padx=6)

        ttk.Label(sf, text="Do order ke beech (sec):").grid(
            row=2, column=3, sticky="e", padx=(20, 8))
        self.gap_var = tk.StringVar(value="20")
        ttk.Spinbox(sf, from_=0, to=600, width=6,
                    textvariable=self.gap_var).grid(row=2, column=4, sticky="w")

        # ---- buttons ----
        btns = ttk.Frame(self.root)
        btns.pack(fill="x", padx=8)
        self.start_btn = ttk.Button(btns, text="Shuru karo", command=self.start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(btns, text="Roko", command=self.stop,
                                   state="disabled")
        self.stop_btn.pack(side="left", padx=6)
        ttk.Button(btns, text="Kitne account/card bache",
                   command=self.refresh_counts).pack(side="left")
        ttk.Button(btns, text="Order record dekho",
                   command=lambda: webbrowser.open(SHEET_URL)).pack(
            side="left", padx=6)
        ttk.Button(btns, text="sessions folder",
                   command=self._open_sessions).pack(side="left")

        # ---- progress ----
        pf = ttk.Frame(self.root)
        pf.pack(fill="x", **pad)
        self.bar = ttk.Progressbar(pf, mode="determinate")
        self.bar.pack(fill="x")
        self.status = tk.StringVar(value="taiyaar")
        ttk.Label(pf, textvariable=self.status).pack(anchor="w", pady=(4, 0))

        # ---- log ----
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
        path = sessions_lagao(got)
        self.sess_var.set(path)
        yaad_likho({"sessions": path})
        self.say("sessions folder: %s" % path)
        self.refresh_counts()

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
                    self.status.set("lage: %d   |   nahi lage: %d   |   kul: %d"
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
        if "order laga" in low or "order lag gaya" in low or "-> complete" in low:
            tag = "ok"
        elif "nahi laga" in low or "fail" in low or "gadbad" in low:
            tag = "fail"
        elif line.startswith("=====") or line.startswith("ORDER "):
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
                ord_ws, _k = order_plan.open_orders_tab()
                khali = len(ob.free_sessions(ord_ws))
                pay_ws, _k2 = order_plan.open_pay_tab()
                card = len(order_plan.pending_payments(pay_ws)) if pay_ws else 0
                self.q.put(("counts", "bina-use account: %d   |   "
                                      "bina-use card: %d" % (khali, card)))
                self.say("bina-use account: %d | bina-use card: %d" % (khali, card))
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

        phones = [p.strip() for p in self.phone_var.get().replace(";", ",")
                  .split(",") if p.strip()]

        # Folder abhi ka abhi laga do -- user ne haath se path likha ho to
        # bhi wahi chale.
        path = sessions_lagao(self.sess_var.get() or po.SESSIONS)
        self.sess_var.set(path)
        yaad_likho({"sessions": path})

        self.stop_flag.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.bar["maximum"] = count
        self.bar["value"] = 0
        self.status.set("shuru kar rahe hain...")

        self.worker = threading.Thread(
            target=self._run,
            args=(links, cart_max, cart_min, count, phones,
                  self.disc_var.get().strip(), gap),
            daemon=True)
        self.worker.start()

    def stop(self):
        self.stop_flag.set()
        self.stop_btn.configure(state="disabled")
        self.say("")
        self.say("[STOP] rok rahe hain -- abhi wala order poora hone do...")

    def _run(self, links, cart_max, cart_min, count, phones, discount, gap):
        """ALAG THREAD. Yahan se koi widget nahi chhua jaata."""
        lage = fail = 0
        try:
            self.say("=" * 66)
            self.say("%d order lagane hain | cart hadd Rs %.2f" % (count, cart_max))
            for l in links:
                self.say("   link: %s" % l)
            self.say("   phone: %s" % (", ".join(phones) or "(sheet se)"))
            self.say("   discount: %s" % (discount or "(sheet se random)"))
            self.say("=" * 66)

            lage, fail = ob.run_batch(
                links, cart_max, count, cart_min=cart_min, phones=phones,
                discount=discount, gap=gap,
                log=self.say,
                should_stop=self.stop_flag.is_set,
                on_progress=lambda a, b, c: self.q.put(("progress", (a, b, c))),
            )
        except Exception:
            self.say("")
            self.say("GADBAD:")
            for l in traceback.format_exc().splitlines()[-8:]:
                self.say("   " + l)
        finally:
            self.q.put(("done", (lage, fail, count)))

    def _finish(self, payload):
        lage, fail, count = payload
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.say("")
        self.say("=" * 66)
        self.say("   maange gaye : %d" % count)
        self.say("   lag gaye    : %d" % lage)
        self.say("   nahi lage   : %d" % fail)
        self.say("   record      : %s tab" % order_plan.ORDER_TAB)
        self.say("=" * 66)
        self.status.set("khatam -- lage: %d, nahi lage: %d" % (lage, fail))
        self.refresh_counts()
        if lage and not fail:
            messagebox.showinfo(APP, "%d order lag gaye." % lage)
        elif lage:
            messagebox.showwarning(
                APP, "%d lage, %d nahi lage.\n\nOrder_Records ke Note column "
                     "me wajah likhi hai." % (lage, fail))
        else:
            messagebox.showwarning(APP, "Ek bhi order nahi laga.\n\n"
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
        sessions_lagao(yaad["sessions"])
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except Exception:
        pass
    app = App(root)
    root.after(500, app.refresh_counts)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
