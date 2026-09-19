"""
=====================================================================
 TRAFFIC BOT GUI  (based on dexsport.py)
=====================================================================
 Features:
   - GUI inputs : Target URL, Target Countries (geos), Total Visits,
                  Min/Max stay duration, Concurrent sessions,
                  Geonode proxy credentials (user/pass/host/port).
   - Buttons    : Start, Pause/Resume, Restart, Stop.
   - Per visit  : opens URL via country proxy (residential IP),
                  random scroll + random click,
                  stays a random duration (min..max seconds).
   - Auto stop  : rukti hai jab Total Visits complete ho jaye.
   - Logging    : live log GUI me dikhta hai AND ek log file
                  (bot_log_<timestamp>.txt) runtime par banti rehti hai.
                  Structured per-visit data visit_log.json me bhi save.
=====================================================================
"""

import os
import sys
import json
import time
import random
import threading
import warnings
from queue import Queue, Empty
from datetime import datetime

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

warnings.filterwarnings("ignore", category=UserWarning)

# ================= PYINSTALLER FIX - Hidden Imports =================
if getattr(sys, "frozen", False):
    import selenium.webdriver.chrome.webdriver       # noqa: F401
    import selenium.webdriver.firefox.webdriver      # noqa: F401
    import selenium.webdriver.edge.webdriver         # noqa: F401
    import selenium.webdriver.safari.webdriver       # noqa: F401
    import selenium.webdriver.remote.webdriver        # noqa: F401

# ================= SELENIUM IMPORTS =================
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


# ================= RESOURCE PATH (PyInstaller friendly) =================
def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def app_dir():
    """Writable folder: frozen me exe ke बगल, warna script ke बगल."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# ================= DEFAULTS (GUI me edit ho sakte hain) =================
# OS-aware defaults: Windows -> bundled portable Firefox; Linux (server) ->
# system Firefox + geckodriver installed at the standard locations.
import platform as _platform
if _platform.system() == "Windows":
    DEFAULT_FIREFOX_BINARY = resource_path("firefox_portable/FirefoxPortable/App/Firefox/firefox.exe")
    DEFAULT_GECKODRIVER    = resource_path("geckodriver-v0.36.0-win64/geckodriver.exe")
else:
    DEFAULT_FIREFOX_BINARY = "/usr/bin/firefox"
    DEFAULT_GECKODRIVER    = "/usr/local/bin/geckodriver"

DEFAULT_URL        = "https://partners.trackopia.com/click?aid=4&oid=311"
DEFAULT_COUNTRIES  = "IT, CH, AT, IN, FR, AU"
DEFAULT_USER_BASE  = "geonode_xvmYN44Bvz-type-residential-country-{}"
DEFAULT_PASS       = "CHANGE_ME_SECRET"
DEFAULT_HOST       = "sg.proxy.geonode.io"
DEFAULT_PORT       = "11000"

VISIT_LOG_JSON = os.path.join(app_dir(), "visit_log.json")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
]


# =====================================================================
#  BOT ENGINE  (GUI se alag, thread-safe)
# =====================================================================
class TrafficBot:
    def __init__(self, config, logger, on_progress, on_finish):
        self.cfg         = config
        self.log         = logger              # callable(msg)
        self.on_progress = on_progress         # callable(done, total)
        self.on_finish   = on_finish           # callable()

        self.stop_event  = threading.Event()
        self.pause_event = threading.Event()   # set() == paused
        self._lock       = threading.Lock()
        self._json_lock  = threading.Lock()

        self.completed   = 0
        self.threads     = []
        self._controller = None

    # ---------- public controls ----------
    def start(self):
        self.stop_event.clear()
        self.pause_event.clear()
        self.completed = 0
        self._controller = threading.Thread(target=self._run, daemon=True)
        self._controller.start()

    def pause(self):
        self.pause_event.set()
        self.log("⏸️  PAUSED — chal rahe visit ke baad ruk jayega.")

    def resume(self):
        self.pause_event.clear()
        self.log("▶️  RESUMED")

    def stop(self):
        self.stop_event.set()
        self.pause_event.clear()
        self.log("🛑 STOP requested — browsers band ho rahe hain...")

    def is_paused(self):
        return self.pause_event.is_set()

    # ---------- internals ----------
    def _wait_if_paused(self):
        while self.pause_event.is_set() and not self.stop_event.is_set():
            time.sleep(0.5)

    def _run(self):
        total = self.cfg["total_visits"]
        workers = max(1, min(self.cfg["concurrency"], total))

        self.log(f"🚀 START | Target visits: {total} | Concurrent: {workers}")
        self.log(f"🌍 Countries: {', '.join(self.cfg['countries'])}")

        q = Queue()
        for i in range(1, total + 1):
            q.put(i)

        self.threads = []
        for _ in range(workers):
            t = threading.Thread(target=self._worker, args=(q,), daemon=True)
            t.start()
            self.threads.append(t)
            time.sleep(random.uniform(1.0, 2.5))

        for t in self.threads:
            t.join()

        if self.stop_event.is_set():
            self.log(f"⏹️  Stopped. Completed {self.completed}/{total}.")
        else:
            self.log(f"🎉 DONE! All {self.completed}/{total} visits completed.")
        self.on_finish()

    def _worker(self, q):
        while not self.stop_event.is_set():
            self._wait_if_paused()
            if self.stop_event.is_set():
                break
            try:
                visit_number = q.get_nowait()
            except Empty:
                break

            self._do_visit(visit_number)

            with self._lock:
                self.completed += 1
                done = self.completed
            self.on_progress(done, self.cfg["total_visits"])

            time.sleep(random.uniform(0.8, 2.2))

    # ---------- single visit ----------
    def _do_visit(self, visit_number):
        cfg = self.cfg
        country = random.choice(cfg["countries"])
        username = cfg["user_base"].format(country.lower())
        proxy_url = f"socks5://{username}:{cfg['password']}@{cfg['host']}:{cfg['port']}"

        self.log(f"\n=== Visit #{visit_number} | Country: {country} ===")

        seleniumwire_options = {
            "proxy": {"http": proxy_url, "https": proxy_url, "no_proxy": "localhost,127.0.0.1"},
            "request_storage": "memory",
            "suppress_connection_errors": True,
            "connection_timeout": 45,
            "exclude_hosts": ["0.0.0.0", "127.0.0.1", "localhost"],
        }

        options = Options()
        # 'eager' => DOM ready hote hi aage badho, saare ads/trackers ka wait mat karo
        options.page_load_strategy = "eager"
        if os.path.exists(cfg["firefox_binary"]):
            options.binary_location = cfg["firefox_binary"]
        else:
            self.log(f"⚠️  Portable Firefox not found ({cfg['firefox_binary']}) — system Firefox try hoga.")

        options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("privacy.resistFingerprinting", False)

        width  = random.choice([1366, 1440, 1536, 1920])
        height = random.choice([768, 900, 1080])
        options.add_argument(f"--width={width}")
        options.add_argument(f"--height={height}")

        driver = None
        click_done = False
        landed_url = ""
        ip_used = "unknown"
        try:
            service = Service(executable_path=cfg["geckodriver"])

            # ---- driver start (1 retry agar proxy hiccup ho) ----
            driver = self._build_driver(seleniumwire_options, options, service)
            if driver is None:
                raise RuntimeError("Browser start nahi hua (proxy/driver issue).")

            driver.set_page_load_timeout(cfg["page_timeout"])

            # ---- proxy ki real exit-IP nikaalo (log ke liye) ----
            ip_used = self._get_proxy_ip(driver)
            self.log(f"🌐 IP: {ip_used} | Country: {country}")

            # ---- page open: timeout pe crash mat karo, jo loaded hai usi pe chalo ----
            try:
                driver.get(cfg["url"])
            except TimeoutException:
                self.log("   ⚠️ Page slow — load rok ke aage badh rahe (eager).")
                try:
                    driver.execute_script("window.stop();")
                except Exception:
                    pass

            time.sleep(random.uniform(4, 7))
            try:
                landed_url = driver.current_url
            except Exception:
                landed_url = cfg["url"]
            self.log(f"📍 Landed: {landed_url[:90]}")

            click_done = self._random_click(driver)

            stay_time = random.uniform(cfg["min_stay"], cfg["max_stay"])
            self.log(f"⏳ Staying {stay_time:.1f}s ...")
            start = time.time()
            while time.time() - start < stay_time and not self.stop_event.is_set():
                self._wait_if_paused()
                if self.stop_event.is_set():
                    break
                action = random.random()
                if action < 0.45:
                    driver.execute_script(f"window.scrollBy(0, {random.randint(200, 700)});")
                elif action < 0.70:
                    try:
                        ActionChains(driver).move_by_offset(
                            random.randint(-120, 120), random.randint(-70, 70)
                        ).perform()
                    except Exception:
                        pass
                time.sleep(random.uniform(1.0, 3.5))

            self.log(f"✅ Visit #{visit_number} done | {country} | IP {ip_used} | stayed {stay_time:.1f}s | click={click_done}")
            self._save_json({
                "visit_number": visit_number,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "country": country,
                "ip": ip_used,
                "landed_url": landed_url[:150],
                "stay_duration": round(stay_time, 1),
                "random_click": click_done,
                "status": "success",
            })

        except Exception as e:
            err = str(e)[:200]
            self.log(f"❌ Visit #{visit_number} error: {err}")
            self._save_json({
                "visit_number": visit_number,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "country": country,
                "ip": ip_used,
                "landed_url": landed_url[:150] if landed_url else "",
                "stay_duration": 0,
                "random_click": False,
                "status": "error",
                "error": err,
            })
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    def _build_driver(self, sw_options, options, service, retries=1):
        """Firefox start karo; proxy hiccup pe ek baar retry."""
        for attempt in range(retries + 1):
            if self.stop_event.is_set():
                return None
            try:
                return webdriver.Firefox(
                    seleniumwire_options=sw_options,
                    options=options,
                    service=service,
                )
            except Exception as e:
                self.log(f"   ⚠️ Browser start fail (try {attempt + 1}): {str(e)[:80]}")
                time.sleep(random.uniform(2, 4))
        return None

    def _get_proxy_ip(self, driver):
        """Proxy ka real exit-IP nikaalo (ipify se). Fail ho to 'unknown'."""
        for url in ("https://api.ipify.org/?format=text", "https://ifconfig.me/ip"):
            try:
                driver.get(url)
                time.sleep(random.uniform(1.2, 2.2))
                body = driver.find_element(By.TAG_NAME, "body").text.strip()
                ip = body.splitlines()[0].strip() if body else ""
                # IPv4 (3 dots) ya IPv6 (colon) jaisa dikhe to hi accept karo
                if ip and len(ip) <= 45 and (ip.count(".") == 3 or ":" in ip):
                    return ip
            except Exception:
                continue
        return "unknown"

    def _random_click(self, driver):
        try:
            selectors = ["a", "button", "input[type='button']", "input[type='submit']",
                         "div[onclick]", "span[onclick]", "[role='button']"]
            elems = []
            for sel in selectors:
                try:
                    elems.extend(driver.find_elements(By.CSS_SELECTOR, sel))
                except Exception:
                    pass
            clickable = [el for el in elems if el.is_displayed() and el.is_enabled()]
            if not clickable:
                return False
            el = random.choice(clickable)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(random.uniform(0.8, 1.5))
            ActionChains(driver).move_to_element(el).pause(random.uniform(0.3, 0.8)).click().perform()
            self.log("   ➤ Random click performed")
            return True
        except Exception as e:
            self.log(f"   ➤ Click error: {str(e)[:60]}")
            return False

    def _save_json(self, visit_data):
        with self._json_lock:
            logs = []
            if os.path.exists(VISIT_LOG_JSON):
                try:
                    with open(VISIT_LOG_JSON, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                except Exception:
                    logs = []
            logs.append(visit_data)
            try:
                with open(VISIT_LOG_JSON, "w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
            except Exception as e:
                self.log(f"⚠️ JSON log save failed: {e}")


# =====================================================================
#  GUI
# =====================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Traffic Bot — GUI")
        self.geometry("860x720")
        self.minsize(760, 640)

        self.bot = None
        self.log_queue = Queue()
        self.log_file_path = None
        self._file_lock = threading.Lock()

        self._build_ui()
        self.after(120, self._drain_log_queue)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------- UI ----------------
    def _build_ui(self):
        pad = {"padx": 6, "pady": 4}

        # ---- Inputs frame ----
        frm = ttk.LabelFrame(self, text="Settings")
        frm.pack(fill="x", padx=10, pady=8)
        for c in range(4):
            frm.columnconfigure(c, weight=1)

        # Target URL
        ttk.Label(frm, text="Target URL").grid(row=0, column=0, sticky="w", **pad)
        self.e_url = ttk.Entry(frm)
        self.e_url.insert(0, DEFAULT_URL)
        self.e_url.grid(row=0, column=1, columnspan=3, sticky="ew", **pad)

        # Countries
        ttk.Label(frm, text="Target Countries (e.g. IN, US, FR)").grid(row=1, column=0, sticky="w", **pad)
        self.e_countries = ttk.Entry(frm)
        self.e_countries.insert(0, DEFAULT_COUNTRIES)
        self.e_countries.grid(row=1, column=1, columnspan=3, sticky="ew", **pad)

        # Total visits / concurrency
        ttk.Label(frm, text="Total Visits").grid(row=2, column=0, sticky="w", **pad)
        self.e_total = ttk.Entry(frm)
        self.e_total.insert(0, "50")
        self.e_total.grid(row=2, column=1, sticky="ew", **pad)

        ttk.Label(frm, text="Concurrent Sessions").grid(row=2, column=2, sticky="w", **pad)
        self.e_concurrency = ttk.Entry(frm)
        self.e_concurrency.insert(0, "1")
        self.e_concurrency.grid(row=2, column=3, sticky="ew", **pad)

        # Min/Max stay
        ttk.Label(frm, text="Min Stay (sec)").grid(row=3, column=0, sticky="w", **pad)
        self.e_min = ttk.Entry(frm)
        self.e_min.insert(0, "20")
        self.e_min.grid(row=3, column=1, sticky="ew", **pad)

        ttk.Label(frm, text="Max Stay (sec)").grid(row=3, column=2, sticky="w", **pad)
        self.e_max = ttk.Entry(frm)
        self.e_max.insert(0, "50")
        self.e_max.grid(row=3, column=3, sticky="ew", **pad)

        # ---- Proxy frame ----
        pfrm = ttk.LabelFrame(self, text="Geonode Proxy (residential — country IP)")
        pfrm.pack(fill="x", padx=10, pady=4)
        for c in range(4):
            pfrm.columnconfigure(c, weight=1)

        ttk.Label(pfrm, text="User Base ( {} = country )").grid(row=0, column=0, sticky="w", **pad)
        self.e_userbase = ttk.Entry(pfrm)
        self.e_userbase.insert(0, DEFAULT_USER_BASE)
        self.e_userbase.grid(row=0, column=1, columnspan=3, sticky="ew", **pad)

        ttk.Label(pfrm, text="Password").grid(row=1, column=0, sticky="w", **pad)
        self.e_pass = ttk.Entry(pfrm)
        self.e_pass.insert(0, DEFAULT_PASS)
        self.e_pass.grid(row=1, column=1, columnspan=3, sticky="ew", **pad)

        ttk.Label(pfrm, text="Host").grid(row=2, column=0, sticky="w", **pad)
        self.e_host = ttk.Entry(pfrm)
        self.e_host.insert(0, DEFAULT_HOST)
        self.e_host.grid(row=2, column=1, sticky="ew", **pad)

        ttk.Label(pfrm, text="Port").grid(row=2, column=2, sticky="w", **pad)
        self.e_port = ttk.Entry(pfrm)
        self.e_port.insert(0, DEFAULT_PORT)
        self.e_port.grid(row=2, column=3, sticky="ew", **pad)

        # ---- Paths frame ----
        pathfrm = ttk.LabelFrame(self, text="Browser Paths")
        pathfrm.pack(fill="x", padx=10, pady=4)
        pathfrm.columnconfigure(1, weight=1)

        ttk.Label(pathfrm, text="Firefox binary").grid(row=0, column=0, sticky="w", **pad)
        self.e_firefox = ttk.Entry(pathfrm)
        self.e_firefox.insert(0, DEFAULT_FIREFOX_BINARY)
        self.e_firefox.grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(pathfrm, text="...", width=3,
                   command=lambda: self._browse(self.e_firefox)).grid(row=0, column=2, **pad)

        ttk.Label(pathfrm, text="Geckodriver").grid(row=1, column=0, sticky="w", **pad)
        self.e_gecko = ttk.Entry(pathfrm)
        self.e_gecko.insert(0, DEFAULT_GECKODRIVER)
        self.e_gecko.grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(pathfrm, text="...", width=3,
                   command=lambda: self._browse(self.e_gecko)).grid(row=1, column=2, **pad)

        # ---- Buttons ----
        btnfrm = ttk.Frame(self)
        btnfrm.pack(fill="x", padx=10, pady=8)
        self.btn_start   = ttk.Button(btnfrm, text="▶ Start", command=self.on_start)
        self.btn_pause   = ttk.Button(btnfrm, text="⏸ Pause", command=self.on_pause, state="disabled")
        self.btn_restart = ttk.Button(btnfrm, text="🔁 Restart", command=self.on_restart, state="disabled")
        self.btn_stop    = ttk.Button(btnfrm, text="⏹ Stop", command=self.on_stop, state="disabled")
        for b in (self.btn_start, self.btn_pause, self.btn_restart, self.btn_stop):
            b.pack(side="left", padx=5)

        # ---- Progress ----
        progfrm = ttk.Frame(self)
        progfrm.pack(fill="x", padx=10, pady=2)
        self.progress = ttk.Progressbar(progfrm, mode="determinate")
        self.progress.pack(fill="x", side="left", expand=True, padx=(0, 8))
        self.lbl_progress = ttk.Label(progfrm, text="0 / 0")
        self.lbl_progress.pack(side="right")

        # ---- Log ----
        logfrm = ttk.LabelFrame(self, text="Live Log")
        logfrm.pack(fill="both", expand=True, padx=10, pady=8)
        self.txt_log = scrolledtext.ScrolledText(logfrm, height=12, state="disabled", wrap="word")
        self.txt_log.pack(fill="both", expand=True, padx=4, pady=4)

    def _browse(self, entry):
        path = filedialog.askopenfilename()
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)

    # ---------------- logging ----------------
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self.log_queue.put(line)
        if self.log_file_path:
            try:
                with self._file_lock:
                    with open(self.log_file_path, "a", encoding="utf-8") as f:
                        f.write(line + "\n")
            except Exception:
                pass

    def _drain_log_queue(self):
        try:
            while True:
                line = self.log_queue.get_nowait()
                self.txt_log.configure(state="normal")
                self.txt_log.insert("end", line + "\n")
                self.txt_log.see("end")
                self.txt_log.configure(state="disabled")
        except Empty:
            pass
        self.after(120, self._drain_log_queue)

    # ---------------- validation ----------------
    def _read_config(self):
        url = self.e_url.get().strip()
        if not url:
            raise ValueError("Target URL khaali hai.")

        countries = [c.strip().upper() for c in self.e_countries.get().split(",") if c.strip()]
        if not countries:
            raise ValueError("Kam se kam ek country code daalo (e.g. IN).")

        total = int(self.e_total.get())
        concurrency = int(self.e_concurrency.get())
        min_stay = float(self.e_min.get())
        max_stay = float(self.e_max.get())
        if total <= 0:
            raise ValueError("Total Visits 0 se bada hona chahiye.")
        if concurrency <= 0:
            raise ValueError("Concurrent Sessions 0 se bada hona chahiye.")
        if min_stay <= 0 or max_stay < min_stay:
            raise ValueError("Stay duration galat hai (Max >= Min, dono > 0).")

        return {
            "url": url,
            "countries": countries,
            "total_visits": total,
            "concurrency": concurrency,
            "min_stay": min_stay,
            "max_stay": max_stay,
            "page_timeout": 75,
            "user_base": self.e_userbase.get().strip(),
            "password": self.e_pass.get().strip(),
            "host": self.e_host.get().strip(),
            "port": self.e_port.get().strip(),
            "firefox_binary": self.e_firefox.get().strip(),
            "geckodriver": self.e_gecko.get().strip(),
        }

    # ---------------- button handlers ----------------
    def on_start(self):
        try:
            cfg = self._read_config()
        except Exception as e:
            messagebox.showerror("Invalid input", str(e))
            return

        if not os.path.exists(cfg["geckodriver"]):
            if not messagebox.askyesno("Geckodriver missing",
                                       f"Geckodriver yahan nahi mila:\n{cfg['geckodriver']}\n\nPhir bhi continue karein?"):
                return

        # new log file for this run
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(app_dir(), f"bot_log_{stamp}.txt")

        self.progress.configure(maximum=cfg["total_visits"], value=0)
        self.lbl_progress.configure(text=f"0 / {cfg['total_visits']}")

        self.bot = TrafficBot(cfg, self.log, self._on_progress, self._on_finish)
        self.bot.start()

        self.log(f"📝 Log file: {self.log_file_path}")
        self._set_running_state(True)

    def on_pause(self):
        if not self.bot:
            return
        if self.bot.is_paused():
            self.bot.resume()
            self.btn_pause.configure(text="⏸ Pause")
        else:
            self.bot.pause()
            self.btn_pause.configure(text="▶ Resume")

    def on_stop(self):
        if self.bot:
            self.bot.stop()
        self.btn_stop.configure(state="disabled")

    def on_restart(self):
        # stop current run, then start fresh
        if self.bot:
            self.bot.stop()
            self.log("🔁 Restart: rukne ka intezaar...")

            def _wait_then_start():
                if self.bot and any(t.is_alive() for t in self.bot.threads):
                    self.after(300, _wait_then_start)
                    return
                self.on_start()

            self.after(300, _wait_then_start)
        else:
            self.on_start()

    # ---------------- callbacks from bot thread ----------------
    def _on_progress(self, done, total):
        def upd():
            self.progress.configure(value=done)
            self.lbl_progress.configure(text=f"{done} / {total}")
        self.after(0, upd)

    def _on_finish(self):
        self.after(0, lambda: self._set_running_state(False))

    def _set_running_state(self, running):
        if running:
            self.btn_start.configure(state="disabled")
            self.btn_pause.configure(state="normal", text="⏸ Pause")
            self.btn_restart.configure(state="normal")
            self.btn_stop.configure(state="normal")
        else:
            self.btn_start.configure(state="normal")
            self.btn_pause.configure(state="disabled", text="⏸ Pause")
            self.btn_restart.configure(state="disabled")
            self.btn_stop.configure(state="disabled")

    def _on_close(self):
        if self.bot and any(t.is_alive() for t in self.bot.threads):
            if not messagebox.askyesno("Exit", "Bot chal raha hai. Band karein?"):
                return
            self.bot.stop()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
