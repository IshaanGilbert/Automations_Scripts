#!/usr/bin/env python3
"""account_gui.py -- Estuary account creator ka window.

User sirf ginti deta hai; script tab tak chalti hai jab tak utne account BAN
na jayen (koshishon ki ginti nahi -- bane hue accounts ki).

Kuch baatein jaan bujh kar aise hain:

* Browser wala kaam ek ALAG THREAD me chalta hai. Window ke thread me chalata
  to poora window jam jaata -- na Stop dabta, na log dikhta.
* Thread se seedha widget ko haath nahi lagaya jaata (tkinter uski ijazat nahi
  deta). Sab kuch ek Queue me daala jaata hai aur window har 100ms me use
  khaali karta hai.
* Stop turant lagta hai: har koshish se pehle, aur do account ke beech ke
  intezaar me har second, `should_stop()` poochha jaata hai.
* Har line ek log file me bhi jaati hai -- exe windowed hai, console nahi
  hota, aur gadbad hone par kuch to haath me hona chahiye.
"""
import os
import sys
import time
import queue
import threading
import traceback
import webbrowser

import tkinter as tk
from tkinter import ttk, messagebox

# ---- exe (windowed) me stdout/stderr None hote hain. Kisi bhi print se pehle
# ---- unhe surakshit bana do, warna import karte hi crash ho sakta hai.
class _Sink(object):
    """Windowed exe me sys.stdout/stderr hote hi nahi (None hote hain).

    Sirf write/flush kaafi nahi nikla: koi bhi library asli stream jaisi cheez
    maang sakti hai. place_order import hote hi `sys.stdout.reconfigure(...)`
    chalata hai, aur wahi exe ko khulte hi gira deta tha --
    "AttributeError: '_Sink' object has no attribute 'reconfigure'".
    Isliye ab wo saari cheezein yahan hain jo ek text stream me hoti hain.
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

import place_order as po          # noqa: E402
import make_accounts_wf as mk     # noqa: E402
import sheet_log                  # noqa: E402
import otpd                       # noqa: E402

APP = "Estuary Account Creator"
LOGFILE = os.path.join(po.HERE, "gui_log.txt")
SHEET_URL = "https://docs.google.com/spreadsheets/d/%s" % sheet_log.SHEET_ID


class App(object):
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()
        self.worker = None
        self.stop_flag = threading.Event()
        self.bane = 0
        self.chahiye = 0

        root.title(APP)
        root.geometry("860x600")
        root.minsize(720, 480)

        self._build()
        self.root.after(100, self._drain)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.say("%s taiyaar hai." % APP)
        self.say("Kitne account chahiye, wo likho aur 'Shuru karo' dabao.")
        self.say("")

    # ------------------------------------------------------------ window
    def _build(self):
        pad = {"padx": 8, "pady": 6}

        top = ttk.LabelFrame(self.root, text=" Kya karna hai ")
        top.pack(fill="x", **pad)

        ttk.Label(top, text="Kitne account banane hain:").grid(
            row=0, column=0, sticky="w", padx=8, pady=8)
        self.count_var = tk.StringVar(value="5")
        self.count_box = ttk.Spinbox(top, from_=1, to=500, width=8,
                                     textvariable=self.count_var)
        self.count_box.grid(row=0, column=1, sticky="w", pady=8)

        ttk.Label(top, text="Ek account par zyada se zyada koshish:").grid(
            row=0, column=2, sticky="e", padx=(24, 8))
        self.tries_var = tk.StringVar(value="3")
        ttk.Spinbox(top, from_=1, to=10, width=6,
                    textvariable=self.tries_var).grid(row=0, column=3, sticky="w")

        self.proxy_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Geonode India proxy",
                        variable=self.proxy_var).grid(row=1, column=0,
                                                      columnspan=2,
                                                      sticky="w", padx=8)
        self.sheet_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Google Sheet me likho",
                        variable=self.sheet_var).grid(row=1, column=2,
                                                      columnspan=2, sticky="w")

        # ---- buttons ----
        btns = ttk.Frame(self.root)
        btns.pack(fill="x", padx=8)
        self.start_btn = ttk.Button(btns, text="Shuru karo",
                                    command=self.start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(btns, text="Roko", command=self.stop,
                                   state="disabled")
        self.stop_btn.pack(side="left", padx=6)
        ttk.Button(btns, text="Sheet kholo",
                   command=lambda: webbrowser.open(SHEET_URL)).pack(side="left")
        ttk.Button(btns, text="sessions folder",
                   command=self._open_sessions).pack(side="left", padx=6)

        # ---- progress ----
        pf = ttk.Frame(self.root)
        pf.pack(fill="x", **pad)
        self.bar = ttk.Progressbar(pf, mode="determinate")
        self.bar.pack(fill="x")
        self.status = tk.StringVar(value="taiyaar")
        ttk.Label(pf, textvariable=self.status).pack(anchor="w", pady=(4, 0))

        # ---- log ----
        lf = ttk.LabelFrame(self.root, text=" Chal kya raha hai ")
        lf.pack(fill="both", expand=True, **pad)
        self.log = tk.Text(lf, wrap="none", height=18,
                           bg="#101418", fg="#d8e0e8",
                           insertbackground="#d8e0e8",
                           font=("Consolas", 9))
        sb = ttk.Scrollbar(lf, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set, state="disabled")
        sb.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)

        for tag, col in (("ok", "#7ee787"), ("fail", "#ff7b72"),
                         ("head", "#79c0ff"), ("warn", "#e3b341")):
            self.log.tag_configure(tag, foreground=col)

    def _open_sessions(self):
        try:
            os.startfile(po.SESSIONS)          # Windows
        except Exception:
            messagebox.showinfo(APP, po.SESSIONS)

    # ------------------------------------------------------------ log
    def say(self, line=""):
        """Kisi bhi thread se bulaya ja sakta hai -- seedha widget ko nahi
        chhuta, sirf queue me daalta hai."""
        self.q.put(("log", str(line)))

    def _drain(self):
        """Window ka thread: queue khaali karo. Har 100ms."""
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == "log":
                    self._write(payload)
                elif kind == "progress":
                    bane, chahiye, rounds = payload
                    self.bane = bane
                    self.bar["maximum"] = max(1, chahiye)
                    self.bar["value"] = bane
                    self.status.set("bane: %d / %d   |   round: %d"
                                    % (bane, chahiye, rounds))
                elif kind == "done":
                    self._finish(payload)
        except queue.Empty:
            pass
        self.root.after(100, self._drain)

    def _write(self, line):
        tag = ""
        low = line.lower()
        if "ban gaya" in low or "row jud gayi" in low or "login: haan" in low:
            tag = "ok"
        elif "nahi bana" in low or "fail" in low or "gadbad" in low:
            tag = "fail"
        elif line.startswith("=====") or line.startswith("======"):
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

    # ------------------------------------------------------------ chalao
    def start(self):
        try:
            count = int(self.count_var.get())
            tries = int(self.tries_var.get())
        except ValueError:
            messagebox.showerror(APP, "Ginti sahi likho (jaise 5).")
            return
        if count < 1:
            messagebox.showerror(APP, "Kam se kam 1 account.")
            return

        self.chahiye = count
        self.bane = 0
        self.stop_flag.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.count_box.configure(state="disabled")
        self.bar["maximum"] = count
        self.bar["value"] = 0
        self.status.set("shuru kar rahe hain...")

        self.worker = threading.Thread(
            target=self._run, args=(count, tries, self.proxy_var.get(),
                                    self.sheet_var.get()),
            daemon=True)
        self.worker.start()

    def stop(self):
        self.stop_flag.set()
        self.stop_btn.configure(state="disabled")
        self.say("")
        self.say("[STOP] rok rahe hain -- abhi wali koshish poori hone do...")

    def _run(self, count, tries, use_proxy, use_sheet):
        """ALAG THREAD. Yahan se koi widget nahi chhua jaata -- sab say()/queue se."""
        stop_bridge = None
        port = None
        bane = rounds = 0
        try:
            self.say("=" * 62)
            self.say("%d account banane hain" % count)
            try:
                self.say("otpdoctor balance: %s" % otpd.balance())
            except Exception as e:
                self.say("balance nahi mila: %s" % str(e)[:80])

            if use_sheet:
                ws, kahani = sheet_log.open_tab()
                self.say("sheet: tab '%s' -> %s" % (sheet_log.TAB, kahani))
                if ws is None:
                    use_sheet = False
                    self.say("sheet: row nahi likhi jayengi (account phir bhi banenge)")
            else:
                self.say("sheet: OFF")

            if use_proxy:
                user = po.geonode_username(po.GEONODE_COUNTRY, sticky=False)
                port, stop_bridge = po.start_geonode_bridge(user)
                self.say("proxy: Geonode India | bridge 127.0.0.1:%d" % port)
            else:
                self.say("proxy: OFF")

            self.say("=" * 62)

            bane, rounds = mk.run_batch(
                count, proxy_port=port, tries=tries,
                sheet_on=use_sheet,
                log=self.say,
                should_stop=self.stop_flag.is_set,
                on_progress=lambda b, c, r: self.q.put(("progress", (b, c, r))),
            )
        except Exception:
            self.say("")
            self.say("GADBAD:")
            for l in traceback.format_exc().splitlines()[-8:]:
                self.say("   " + l)
        finally:
            if stop_bridge is not None:
                try:
                    stop_bridge.set()
                except Exception:
                    pass
            self.q.put(("done", (bane, count, rounds)))

    def _finish(self, payload):
        bane, count, rounds = payload
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.count_box.configure(state="normal")
        self.say("")
        self.say("=" * 62)
        self.say("   maange gaye : %d" % count)
        self.say("   ban gaye    : %d" % bane)
        self.say("   round lage  : %d" % rounds)
        try:
            self.say("   balance ab  : %s" % otpd.balance())
        except Exception:
            pass
        self.say("   session     : %s" % po.SESSIONS)
        self.say("=" * 62)
        self.status.set("khatam -- bane: %d / %d" % (bane, count))
        if bane >= count:
            messagebox.showinfo(APP, "%d account ban gaye." % bane)
        else:
            messagebox.showwarning(
                APP, "%d/%d bane.\n\nLog me wajah likhi hai." % (bane, count))

    def _on_close(self):
        if self.worker is not None and self.worker.is_alive():
            if not messagebox.askyesno(
                    APP, "Kaam abhi chal raha hai. Band karna hai?\n\n"
                         "(Browser khula reh sakta hai.)"):
                return
            self.stop_flag.set()
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except Exception:
        pass
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
