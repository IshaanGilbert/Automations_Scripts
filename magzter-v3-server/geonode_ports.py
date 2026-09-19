#!/usr/bin/env python3
"""geonode_ports.py — Geonode ke doosre gateway ports par Chrome chal jaata hai kya.

Ab tak pakka: 11000 wala gateway Chrome ki har connection par
    HTTP/1.1 400 Bad Request / Target website error
bhejta hai, jabki usi gateway se curl ko 200 milta hai. Farq ClientHello ka hai —
Chrome ka ~1785 bytes (do TCP packet), curl ka ~517 (ek packet).

Geonode ke rotating residential gateways aam taur par 11000-11010 range me hote hain aur
har port alag gateway par jaata hai. Ye script har port par pehle curl, phir Chrome
chalata hai. Jis port par Chrome ko status mile, wahi port bot me daalna hai:

    GEONODE_PORT=<wo port>

    sudo venv/bin/python3 geonode_ports.py
    sudo venv/bin/python3 geonode_ports.py 11000 11010
"""
import sys
import asyncio

import nykaa_login as nk

try:
    from patchright.async_api import async_playwright
except ImportError:
    from playwright.async_api import async_playwright

URL = "https://example.com/"
LO = int(sys.argv[1]) if len(sys.argv) > 2 else 11000
HI = int(sys.argv[2]) if len(sys.argv) > 2 else 11010


async def socks_connect(host, port, gate_port):
    """nykaa_login ka _socks5_connect, bas GEONODE_PORT badal kar."""
    old = nk.GEONODE_PORT
    nk.GEONODE_PORT = str(gate_port)
    try:
        user = nk.GEONODE_USER_BASE.format(nk.GEONODE_COUNTRY)
        return await nk._socks5_connect(host, port, user, nk.GEONODE_PASS)
    finally:
        nk.GEONODE_PORT = old


def make_handler(gate_port, box):
    async def handle(cr, cw):
        try:
            header = b""
            while b"\r\n\r\n" not in header:
                chunk = await cr.read(65536)
                if not chunk:
                    return
                header += chunk
            head, _, leftover = header.partition(b"\r\n\r\n")
            method, target, _v = head.split(b"\r\n", 1)[0].decode("latin1").split(" ", 2)
            if method.upper() != "CONNECT":
                cw.close()
                return
            h, _, p = target.rpartition(":")
            try:
                ur, uw = await socks_connect(h, int(p), gate_port)
            except Exception as e:
                box["socks"] = f"{type(e).__name__}"
                cw.close()
                return
            cw.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
            await cw.drain()
            if leftover:
                uw.write(leftover)
                await uw.drain()

            async def pump(src, dst, mark):
                try:
                    while True:
                        d = await src.read(65536)
                        if not d:
                            break
                        if mark and not box.get("head"):
                            box["head"] = d[:40]
                        dst.write(d)
                        await dst.drain()
                except Exception:
                    pass
                finally:
                    try:
                        dst.close()
                    except Exception:
                        pass

            await asyncio.gather(pump(cr, uw, False), pump(ur, cw, True))
        except Exception:
            pass
    return handle


async def curl_through(port):
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "30",
        "--proxy", f"http://127.0.0.1:{port}", URL,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    out, _ = await proc.communicate()
    return f"{out.decode().strip()}" if proc.returncode == 0 else f"err{proc.returncode}"


async def chrome_through(p, port):
    browser = await p.chromium.launch(
        headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        proxy={"server": f"http://127.0.0.1:{port}"})
    try:
        ctx = await browser.new_context(ignore_https_errors=True)
        page = await ctx.new_page()
        try:
            r = await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            return str(r.status if r else "?")
        except Exception as e:
            m = str(e).splitlines()[0]
            return "SSL" if "SSL_PROTOCOL" in m else m[-22:]
    finally:
        try:
            await browser.close()
        except Exception:
            pass


async def main():
    print(f"geonode {nk.GEONODE_HOST} ports {LO}..{HI} | country={nk.GEONODE_COUNTRY}\n")
    print(f"{'port':<8}{'curl':<10}{'chrome':<12}upstream ka jawab")
    async with async_playwright() as p:
        for gate in range(LO, HI + 1):
            box = {}
            server = await asyncio.start_server(make_handler(gate, box), "127.0.0.1", 0)
            lp = server.sockets[0].getsockname()[1]
            try:
                c = await curl_through(lp)
                ch = await chrome_through(p, lp)
            finally:
                server.close()
                await server.wait_closed()
            head = box.get("head", b"")
            txt = "".join(chr(x) if 32 <= x < 127 else "." for x in head)[:34]
            note = box.get("socks") or txt
            print(f"{gate:<8}{c:<10}{ch:<12}{note}")

    print("\nJis port par chrome column me 200 aaya, wahi port kaam karta hai:")
    print("  agent .env me GEONODE_PORT=<port> daal kar slot restart karo")
    print("Sab ports par 'SSL' + '400 Bad Request' -> Geonode ka poora gateway Chrome ko")
    print("  mana kar raha hai; unke support ko ye trace bhejo ya provider badlo.")


if __name__ == "__main__":
    asyncio.run(main())
