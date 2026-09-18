#!/usr/bin/env python3
"""bridge_trace.py — upstream ne jo 68 bytes bheje, unhe padho; aur naapo ki kaun sa
flag Chrome ka ClientHello chhota karta hai.

Pichle run ka data:
    curl   : up=841   down=5323  -> HTTP 200
    Chrome : up=1792  down=68    -> ERR_SSL_PROTOCOL_ERROR

1792 bytes ka ClientHello matlab post-quantum key share laga hua hai (curl ka 841 hai).
68 bytes ka jawab TLS alert (7 bytes) se bada hai — wo shayad TLS hai hi nahi. Ye script
un bytes ko hex + text dono me chhapti hai, aur har flag-config pe up/down naapti hai.
Jis config me up gir jaye aur down bade, wahi jeet gayi.

    sudo venv/bin/python3 bridge_trace.py
"""
import asyncio

import nykaa_login as nk

try:
    from patchright.async_api import async_playwright
except ImportError:
    from playwright.async_api import async_playwright

URL = "https://example.com/"

# Har candidate ka maqsad ek hi hai: ClientHello ko curl jitna chhota karna (~841).
# Naam ka andaaza nahi lagana — naap kar dekhna ki kaun sa sach me kaam karta hai.
CONFIGS = [
    ("curl (tulna ke liye)",              None),
    ("chrome: default",                   []),
    ("chrome: PostQuantumKeyAgreement",   ["--disable-features=PostQuantumKeyAgreement"]),
    ("chrome: TLS13KyberX25519",          ["--disable-features=TLS13KyberX25519"]),
    ("chrome: sab PQ naam ek saath",      ["--disable-features=PostQuantumKyber,UseMLKEM,"
                                           "X25519MLKEM768,X25519Kyber768,"
                                           "PostQuantumKeyAgreement,TLS13KyberX25519"]),
    ("chrome: TLS 1.2 max",               ["--ssl-version-max=tls1.2"]),
    ("chrome: 1.2 + sab PQ naam",         ["--ssl-version-max=tls1.2",
                                           "--disable-features=PostQuantumKyber,UseMLKEM,"
                                           "X25519MLKEM768,X25519Kyber768,"
                                           "PostQuantumKeyAgreement,TLS13KyberX25519"]),
]

STATS = []          # (label, up, down, first_down_bytes)
_cur = None


async def _copy(src, dst, box, key):
    try:
        while True:
            data = await src.read(65536)
            if not data:
                break
            box[key] += len(data)
            if key == "up" and not box["first"]:
                box["first"] = len(data)
            if key == "down" and not box["head"]:
                box["head"] = data[:120]
            dst.write(data)
            await dst.drain()
    except Exception:
        pass
    finally:
        try:
            dst.close()
        except Exception:
            pass


async def handler(client_reader, client_writer):
    box = {"up": 0, "down": 0, "head": b"", "first": 0}
    try:
        header = b""
        while b"\r\n\r\n" not in header:
            chunk = await client_reader.read(65536)
            if not chunk:
                return
            header += chunk
        head, _, leftover = header.partition(b"\r\n\r\n")
        method, target, _v = head.split(b"\r\n", 1)[0].decode("latin1").split(" ", 2)
        if method.upper() != "CONNECT":
            client_writer.close()
            return
        h, _, p = target.rpartition(":")
        user = nk.GEONODE_USER_BASE.format(nk.GEONODE_COUNTRY)
        try:
            up_reader, up_writer = await nk._socks5_connect(h, int(p), user, nk.GEONODE_PASS)
        except Exception as e:
            print(f"    SOCKS FAIL: {type(e).__name__}: {e}")
            client_writer.close()
            return
        client_writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
        await client_writer.drain()
        if leftover:
            box["first"] = box["first"] or len(leftover)
            box["up"] += len(leftover)
            up_writer.write(leftover)
            await up_writer.drain()
        await asyncio.gather(_copy(client_reader, up_writer, box, "up"),
                             _copy(up_reader, client_writer, box, "down"))
    finally:
        if _cur is not None and box["up"]:
            STATS.append((_cur, box["up"], box["down"], box["head"], box["first"]))


def _show_bytes(b):
    if not b:
        return "(kuch nahi)"
    txt = "".join(chr(c) if 32 <= c < 127 else "." for c in b)
    return f"\n        hex : {b[:48].hex(' ')}\n        text: {txt}"


async def run_curl(port):
    proc = await asyncio.create_subprocess_exec(
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "45",
        "--proxy", f"http://127.0.0.1:{port}", URL,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, _ = await proc.communicate()
    return f"exit={proc.returncode} http={out.decode().strip()}"


async def run_chrome(p, port, extra):
    browser = await p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"] + extra,
        proxy={"server": f"http://127.0.0.1:{port}"})
    try:
        ctx = await browser.new_context(ignore_https_errors=True)
        page = await ctx.new_page()
        try:
            r = await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
            return f"status={r.status if r else '?'}"
        except Exception as e:
            m = str(e).splitlines()[0]
            return "FAIL(SSL)" if "SSL_PROTOCOL" in m else f"FAIL({m[-30:]})"
    finally:
        try:
            await browser.close()
        except Exception:
            pass


async def main():
    global _cur
    server = await asyncio.start_server(handler, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    print(f"trace bridge 127.0.0.1:{port} | geonode {nk.GEONODE_HOST}:{nk.GEONODE_PORT}"
          f" country={nk.GEONODE_COUNTRY}\n")

    async with async_playwright() as p:
        for label, extra in CONFIGS:
            _cur = label
            before = len(STATS)
            out = await (run_curl(port) if extra is None else run_chrome(p, port, extra))
            await asyncio.sleep(1.0)          # connections ko band hone do
            rows = STATS[before:]
            up = rows[0][1] if rows else 0
            down = rows[0][2] if rows else 0
            first = rows[0][4] if rows else 0
            print(f"{label:<36} hello={first:<6} up={up:<6} down={down:<6} {out}")
    _cur = None

    server.close()
    await server.wait_closed()

    print("\n===== UPSTREAM NE KYA BHEJA (pehle bytes) =====")
    seen = set()
    for label, up, down, head, _f in STATS:
        if label in seen or not head:
            continue
        seen.add(label)
        print(f"  {label} (down={down}):{_show_bytes(head)}")

    print("\nPadhne ka tareeka:")
    print("  hello = ClientHello ka size. curl ka ~841 hai, chrome ka ~1790.")
    print("  koi row me hello ~800 aur status=200 -> wahi flags bot me daalne hain")
    print("  hello chhota ho gaya par phir bhi 400 -> Geonode size par nahi, Chrome ke")
    print("     TLS fingerprint par rok raha hai; tab flags se kuch nahi hoga")


if __name__ == "__main__":
    asyncio.run(main())
