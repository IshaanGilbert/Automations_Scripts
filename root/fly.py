import asyncio
import json
import os
import sys
import socket
import random
import threading
import queue
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


# When frozen into an .exe, point Playwright at the Chromium we bundle next to
# the executable (so nothing needs to be installed on the target machine).
def _configure_bundled_browsers():
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        bundled = os.path.join(base, "ms-playwright")
        if os.path.isdir(bundled):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = bundled
        # Skip Playwright's own validation/host-requirements checks
        os.environ.setdefault("PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS", "1")


_configure_bundled_browsers()

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from playwright.async_api import async_playwright

# ================= GEONODE CONFIG =================
GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
GEONODE_PASS      = "CHANGE_ME_SECRET"
GEONODE_HOST      = "sg.proxy.geonode.io"
GEONODE_PORT      = "11000"

# ================= DEFAULTS =================
DEFAULT_URL     = "https://partners.streakads.com/click?aid=3&oid=414"
DEFAULT_VISITS  = 1000
DEFAULT_GEOS    = "IN"
LOG_FILE        = "fly_visits.json"
TEXT_LOG_FILE   = "fly_visits.txt"

# The playable ad domain (Aviator game). We tap FLY once, then the click-out
# lands us on the real offer (join4ra.com etc.).
AD_DOMAIN = "4rapwavi"

# iPhone / iOS Safari UAs. iOS is required: on iOS the ad's Install handler does
# window.location.href = <offer>, which reliably opens the offer page. On desktop
# it relies on the PWA install prompt which never fires under automation.
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
]


# ---------------- Proxy bridge (in-process, no dependencies) ----------------
# Chromium cannot authenticate SOCKS5 (username/password) proxies. So we run a
# tiny in-process HTTP proxy on 127.0.0.1 (no auth) that tunnels every connection
# through the authenticated Geonode SOCKS5 upstream. Chromium then uses the local
# no-auth proxy via Playwright's native proxy option. Pure asyncio, so it works
# fine inside a frozen .exe (no subprocess, no external package).
def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _socks5_connect(dst_host, dst_port, user, pw):
    """Open a SOCKS5 tunnel to dst_host:dst_port via the Geonode upstream (RFC1928/1929)."""
    reader, writer = await asyncio.open_connection(GEONODE_HOST, int(GEONODE_PORT))
    # greeting: version 5, 1 method, username/password (0x02)
    writer.write(b"\x05\x01\x02")
    await writer.drain()
    resp = await reader.readexactly(2)
    if resp[1] != 0x02:
        raise OSError("SOCKS5 upstream refused username/password auth")
    # auth (RFC1929)
    ub = user.encode(); pb = pw.encode()
    writer.write(b"\x01" + bytes([len(ub)]) + ub + bytes([len(pb)]) + pb)
    await writer.drain()
    a = await reader.readexactly(2)
    if a[1] != 0x00:
        raise OSError("SOCKS5 auth failed")
    # connect request, address type = domain (0x03)
    db = dst_host.encode()
    writer.write(b"\x05\x01\x00\x03" + bytes([len(db)]) + db + int(dst_port).to_bytes(2, "big"))
    await writer.drain()
    r = await reader.readexactly(4)
    if r[1] != 0x00:
        raise OSError(f"SOCKS5 connect failed (code {r[1]})")
    atyp = r[3]
    if atyp == 0x01:
        await reader.readexactly(4)
    elif atyp == 0x03:
        ln = await reader.readexactly(1)
        await reader.readexactly(ln[0])
    elif atyp == 0x04:
        await reader.readexactly(16)
    await reader.readexactly(2)  # bound port
    return reader, writer


async def _pipe(src_reader, dst_writer):
    try:
        while True:
            data = await src_reader.read(65536)
            if not data:
                break
            dst_writer.write(data)
            await dst_writer.drain()
    except Exception:
        pass
    finally:
        try:
            dst_writer.close()
        except Exception:
            pass


def _make_bridge_handler(username, tasks):
    async def handle(client_reader, client_writer):
        tasks.add(asyncio.current_task())
        up_writer = None
        try:
            # read request head
            header = b""
            while b"\r\n\r\n" not in header:
                chunk = await client_reader.read(65536)
                if not chunk:
                    return
                header += chunk
                if len(header) > 262144:
                    return
            head, _, leftover = header.partition(b"\r\n\r\n")
            request_line = head.split(b"\r\n", 1)[0].decode("latin1")
            method, target, _ver = request_line.split(" ", 2)

            if method.upper() == "CONNECT":
                host, _, port = target.rpartition(":")
                up_reader, up_writer = await _socks5_connect(host, int(port), username, GEONODE_PASS)
                client_writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
                await client_writer.drain()
                if leftover:
                    up_writer.write(leftover)
                    await up_writer.drain()
            else:
                u = urlparse(target)
                host = u.hostname
                port = u.port or 80
                up_reader, up_writer = await _socks5_connect(host, int(port), username, GEONODE_PASS)
                path = u.path or "/"
                if u.query:
                    path += "?" + u.query
                rebuilt = header.replace(target.encode(), path.encode(), 1)
                up_writer.write(rebuilt)
                await up_writer.drain()

            await asyncio.gather(
                _pipe(client_reader, up_writer),
                _pipe(up_reader, client_writer),
            )
        except Exception:
            try:
                client_writer.close()
            except Exception:
                pass
            if up_writer is not None:
                try:
                    up_writer.close()
                except Exception:
                    pass
        finally:
            tasks.discard(asyncio.current_task())
    return handle


async def start_proxy_bridge(username):
    """Start the in-process HTTP->SOCKS5 bridge. Returns (server, local_port)."""
    local_port = _free_port()
    tasks = set()
    server = await asyncio.start_server(_make_bridge_handler(username, tasks), "127.0.0.1", local_port)
    server._bridge_tasks = tasks
    return server, local_port


async def stop_proxy_bridge(server):
    if server is None:
        return
    try:
        server.close()
        await server.wait_closed()
    except Exception:
        pass
    # cancel any lingering tunnel tasks so they don't accumulate across visits
    for t in list(getattr(server, "_bridge_tasks", ())):
        if not t.done():
            t.cancel()


def make_pwa_url(real_landing):
    """Build the ad's PWA-mode URL (pathname '/', pwa=1). Opening this in a new
    tab makes the ad redirect that tab to the real offer, leaving the game intact."""
    u = urlparse(real_landing)
    q = parse_qs(u.query, keep_blank_values=True)
    q["pwa"] = ["1"]
    newq = urlencode({k: v[0] for k, v in q.items()})
    return urlunparse((u.scheme, u.netloc, "/", "", newq, ""))


def save_log(data):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(data)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def save_text_log(data):
    """Append one human-readable line per visit to jump_visits.txt."""
    line = (
        f"[{data['timestamp']}] Visit #{data['run_number']:<4} "
        f"| {data['status'].upper():<7} "
        f"| Geo: {data['geo']:<3} "
        f"| IP: {data.get('ip', 'unknown'):<16} "
        f"| Fly: {data['jumps']:<2} "
        f"| Offer: {data.get('offer_url', '')[:70]}"
    )
    if data.get("error"):
        line += f" | Error: {data['error']}"
    with open(TEXT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


async def get_proxy_ip(context):
    """Fetch the proxy exit IP using the browser (goes through the proxy bridge)."""
    ip = "unknown"
    tmp = None
    try:
        tmp = await context.new_page()
        await tmp.goto("https://api.ipify.org?format=json", timeout=30000, wait_until="domcontentloaded")
        body = await tmp.evaluate("() => document.body.innerText")
        ip = json.loads(body).get("ip", "unknown")
    except Exception:
        ip = "unknown"
    finally:
        if tmp is not None:
            try:
                await tmp.close()
            except Exception:
                pass
    return ip


# ---------------- One visit ----------------
async def run_one_visit(run_number, url, country_code, headless, log):
    username = GEONODE_USER_BASE.format(country_code.lower())
    log(f"\n🚀 Visit #{run_number} | Geo: {country_code} | Proxy: {username}@{GEONODE_HOST}:{GEONODE_PORT}")

    status = "failed"
    err = None
    jumps = 0
    ip_addr = "unknown"

    # Start the local proxy bridge for this visit (fresh upstream = rotating IP)
    bridge_server, local_port = await start_proxy_bridge(username)

    try:
      async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            proxy={"server": f"http://127.0.0.1:{local_port}"},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )

        # iPhone emulation (iOS Safari) -> ad's Install handler redirects to the offer.
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            user_agent=random.choice(USER_AGENTS),
            locale="en-US",
            timezone_id="Asia/Kolkata",
            geolocation={"latitude": 28.6139 + random.uniform(-0.5, 0.5),
                         "longitude": 77.2090 + random.uniform(-0.5, 0.5)},
            permissions=["geolocation"],
            bypass_csp=True,
            ignore_https_errors=True,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

        await context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
            """
        )

        page = await context.new_page()

        async def tap_or_click(loc):
            """Prefer a real touch tap; fall back to click."""
            try:
                await loc.first.tap(timeout=6000)
                return True
            except Exception:
                try:
                    await loc.first.click(timeout=6000)
                    return True
                except Exception:
                    return False

        try:
            # 0) Capture the proxy exit IP for this visit
            ip_addr = await get_proxy_ip(context)
            log(f"   🌐 Exit IP: {ip_addr}")

            # 1) Open the tracking/click URL -> redirects to the game page
            await page.goto(url, timeout=90000, wait_until="domcontentloaded")
            await page.wait_for_timeout(random.randint(3500, 6000))
            log(f"   ➡️  Landed on: {page.url[:90]}")

            fly_btn = page.locator('button:has-text("FLY")')
            install_btn = page.locator('button:has-text("Install")')

            # Wait for the FLY button to appear (game loaded)
            await fly_btn.first.wait_for(state="visible", timeout=35000)

            # 2) Tap FLY ONCE, then wait for the Install card to appear
            if await tap_or_click(fly_btn):
                jumps += 1
                log("   ✈️  FLY tapped")

            for _ in range(30):  # wait up to ~30s for the Install card
                if await install_btn.count() > 0 and await install_btn.first.is_visible():
                    break
                await page.wait_for_timeout(1000)

            # 3) Install card is up. Capture the real landing URL FIRST (page.url,
            #    no evaluate) because tapping Install navigates the game tab away.
            if await install_btn.count() > 0 and await install_btn.first.is_visible():
                log("   🎁 Install card appeared")
                real_landing = page.url
                pwa_url = make_pwa_url(real_landing)

                # 4) Open the offer in a NEW tab (the Install click-out target).
                #    Game tab stays intact; this tab redirects to the real offer.
                log("   👆 Install -> opening offer in new tab")
                offer_page = await context.new_page()
                await offer_page.goto(pwa_url, timeout=90000, wait_until="domcontentloaded")

                reached_offer = False
                for _ in range(15):
                    await offer_page.wait_for_timeout(1500)
                    if AD_DOMAIN not in offer_page.url and "href.li" not in offer_page.url:
                        reached_offer = True
                        break

                if reached_offer:
                    try:
                        await offer_page.wait_for_load_state("domcontentloaded", timeout=20000)
                    except Exception:
                        pass
                    offer_url = offer_page.url
                    log(f"   🎯 Offer page opened in new tab: {offer_url[:90]}")
                    status = "success"
                else:
                    err = "Offer page did not open"
                    log(f"   ⚠️  {err}")

                # 5) Keep the offer tab open 10-20 seconds
                hold = random.randint(10, 20)
                log(f"   ⏱️  Holding offer tab open for {hold}s")
                await offer_page.wait_for_timeout(hold * 1000)
                log(f"   ✅ Visit #{run_number} done")
            else:
                err = "Install card never appeared"
                log(f"   ⚠️  {err}")

        except Exception as e:
            err = str(e)[:300]
            log(f"   ❌ Visit #{run_number} failed: {err}")
        finally:
            final_url = ""
            try:
                final_url = offer_url
            except Exception:
                try:
                    final_url = page.url
                except Exception:
                    pass
            record = {
                "run_number": run_number,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "geo": country_code,
                "ip": ip_addr,
                "jumps": jumps,
                "status": status,
                "offer_url": final_url[:200],
                "error": err,
            }
            save_log(record)
            save_text_log(record)
            try:
                await browser.close()
            except Exception:
                pass
    finally:
        await stop_proxy_bridge(bridge_server)

    return status == "success"


# ---------------- Runner loop ----------------
async def run_all(url, total, geos, headless, log, stop_event, on_progress):
    success = 0
    done = 0
    for i in range(1, total + 1):
        if stop_event.is_set():
            log("\n⏹️  Stopped by user.")
            break

        country = random.choice(geos)
        try:
            ok = await run_one_visit(i, url, country, headless, log)
            if ok:
                success += 1
        except Exception as e:
            log(f"   ❌ Unexpected error on visit #{i}: {str(e)[:200]}")

        done = i
        on_progress(i, total, success)

        if i < total and not stop_event.is_set():
            wait = random.uniform(5, 12)
            log(f"⏳ Waiting {wait:.1f}s before next visit...")
            await asyncio.sleep(wait)

    failed = done - success
    log(f"\n🎉 Finished. Total: {done} | ✅ Success: {success} | ❌ Failed: {failed}")
    log(f"📄 Detailed log: {TEXT_LOG_FILE}  |  JSON: {LOG_FILE}")


# ================= GUI =================
class JumpBotGUI:
    def __init__(self, root):
        self.root = root
        root.title("StreakAds FLY Bot")
        root.geometry("760x600")

        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = None

        pad = {"padx": 8, "pady": 4}

        frm = ttk.Frame(root)
        frm.pack(fill="x", padx=10, pady=8)

        # URL (default fixed, editable)
        ttk.Label(frm, text="Click URL:").grid(row=0, column=0, sticky="w", **pad)
        self.url_var = tk.StringVar(value=DEFAULT_URL)
        ttk.Entry(frm, textvariable=self.url_var, width=70).grid(row=0, column=1, columnspan=3, sticky="we", **pad)

        # Total visits
        ttk.Label(frm, text="Total Visits:").grid(row=1, column=0, sticky="w", **pad)
        self.visits_var = tk.StringVar(value=str(DEFAULT_VISITS))
        ttk.Entry(frm, textvariable=self.visits_var, width=12).grid(row=1, column=1, sticky="w", **pad)

        # Geos
        ttk.Label(frm, text="Geos (e.g. IN  or  IN,US):").grid(row=2, column=0, sticky="w", **pad)
        self.geos_var = tk.StringVar(value=DEFAULT_GEOS)
        ttk.Entry(frm, textvariable=self.geos_var, width=30).grid(row=2, column=1, columnspan=2, sticky="w", **pad)

        # Headless
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Headless (no window)", variable=self.headless_var).grid(
            row=3, column=1, sticky="w", **pad)

        frm.columnconfigure(1, weight=1)

        # Buttons
        btns = ttk.Frame(root)
        btns.pack(fill="x", padx=10)
        self.start_btn = ttk.Button(btns, text="▶ Start", command=self.start)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = ttk.Button(btns, text="⏹ Stop", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # Progress
        self.progress_var = tk.StringVar(value="Idle")
        ttk.Label(root, textvariable=self.progress_var).pack(anchor="w", padx=12, pady=(6, 0))
        self.progress = ttk.Progressbar(root, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=4)

        # Log box
        self.log_box = scrolledtext.ScrolledText(root, height=22, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=8)

        self.root.after(100, self.drain_log)

    def log(self, msg):
        self.log_queue.put(msg)

    def drain_log(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.root.after(100, self.drain_log)

    def set_progress(self, done, total, success):
        def _update():
            self.progress["maximum"] = total
            self.progress["value"] = done
            self.progress_var.set(f"Progress: {done}/{total}  |  Success: {success}")
        self.root.after(0, _update)

    def start(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "URL cannot be empty")
            return
        try:
            total = int(self.visits_var.get().strip())
            if total <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Total Visits must be a positive number")
            return

        geos = [g.strip().upper() for g in self.geos_var.get().split(",") if g.strip()]
        if not geos:
            messagebox.showerror("Error", "Enter at least one geo (e.g. IN)")
            return

        headless = self.headless_var.get()

        self.stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.log(f"=== Starting: {total} visits | Geos: {', '.join(geos)} | Headless: {headless} ===")

        self.worker = threading.Thread(
            target=self._run_thread, args=(url, total, geos, headless), daemon=True
        )
        self.worker.start()

    def _run_thread(self, url, total, geos, headless):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                run_all(url, total, geos, headless, self.log, self.stop_event, self.set_progress)
            )
        except Exception as e:
            self.log(f"❌ Fatal: {str(e)[:300]}")
        finally:
            loop.close()
            self.root.after(0, self._on_done)

    def _on_done(self):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_var.set(self.progress_var.get() + "  |  DONE")

    def stop(self):
        self.stop_event.set()
        self.log("⏹️  Stop requested... finishing current visit.")
        self.stop_btn.configure(state="disabled")


def _selftest():
    """Non-GUI smoke test: run one headless visit and write the result.
    Used to validate a frozen build end-to-end (bundled Chromium + proxy bridge).
    Windowed-safe: also logs to selftest.log since a GUI exe has no console."""
    logf = open("selftest.log", "w", encoding="utf-8")

    def log(m):
        try:
            print(m, flush=True)
        except Exception:
            pass
        try:
            logf.write(str(m) + "\n")
            logf.flush()
        except Exception:
            pass

    async def _main():
        ok = await run_one_visit(1, DEFAULT_URL, "IN", headless=True, log=log)
        log("\n=== SELFTEST RESULT: " + ("SUCCESS" if ok else "FAILED") + " ===")
        return ok

    result = asyncio.run(_main())
    logf.close()
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        root = tk.Tk()
        app = JumpBotGUI(root)
        root.mainloop()
