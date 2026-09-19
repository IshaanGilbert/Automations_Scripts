#!/usr/bin/env python3
"""proxy_test.py — Geonode ka rasta alag-alag karke check karo.

`ERR_SSL_PROTOCOL_ERROR` do jagah se aa sakta hai: Geonode ke kharab exit node se, ya
hamare SOCKS->HTTP bridge se. curl seedha SOCKS5 pe chala kar sirf pehla hissa test hota
hai — bot us rastey se nahi jaata, wo bridge se jaata hai. Ye script dono ko N baar
chala kar batati hai kaun toot raha hai.

    sudo venv/bin/python3 proxy_test.py           # 10 try
    sudo venv/bin/python3 proxy_test.py 25        # 25 try
"""
import sys
import asyncio
import subprocess

import nykaa_login as nk

TRIES = int(sys.argv[1]) if len(sys.argv) > 1 else 10
URL = "https://www.nykaa.com/"


def _curl(args):
    """(http_code, exit_code, stderr-ka-aakhri-hissa) — curl ka exit code hi asli baat
    batata hai: 35 = TLS handshake fail, 0 = jawab mila (403 bhi jawab hai)."""
    p = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "45"] + args,
        capture_output=True, text=True)
    return p.stdout.strip(), p.returncode, (p.stderr or "").strip()[-120:]


async def main():
    user = nk.GEONODE_USER_BASE.format(nk.GEONODE_COUNTRY)
    socks = f"{user}:{nk.GEONODE_PASS}@{nk.GEONODE_HOST}:{nk.GEONODE_PORT}"

    print(f"URL      : {URL}")
    print(f"tries    : {TRIES}\n")

    print("--- A) SEEDHA SOCKS5 (bridge ke bina) ---")
    a_ok = a_tls = a_other = 0
    for i in range(1, TRIES + 1):
        code, rc, err = _curl(["--socks5-hostname", socks, URL])
        if rc == 0:
            a_ok += 1
            print(f"  {i:>3}. HTTP {code}")
        elif rc == 35:
            a_tls += 1
            print(f"  {i:>3}. TLS FAIL (curl 35) {err}")
        else:
            a_other += 1
            print(f"  {i:>3}. curl exit {rc} {err}")

    print("\n--- B) HAMARE BRIDGE KE THROUGH (bot isi rastey jaata hai) ---")
    server, port = await nk.start_proxy_bridge(user)
    b_ok = b_tls = b_other = 0
    try:
        for i in range(1, TRIES + 1):
            code, rc, err = await asyncio.get_event_loop().run_in_executor(
                None, _curl, ["--proxy", f"http://127.0.0.1:{port}", URL])
            if rc == 0:
                b_ok += 1
                print(f"  {i:>3}. HTTP {code}")
            elif rc == 35:
                b_tls += 1
                print(f"  {i:>3}. TLS FAIL (curl 35) {err}")
            else:
                b_other += 1
                print(f"  {i:>3}. curl exit {rc} {err}")
    finally:
        await nk.stop_proxy_bridge(server)

    print("\n===== NATEEJA =====")
    print(f"A seedha SOCKS5 : ok={a_ok}  TLS-fail={a_tls}  other={a_other}")
    print(f"B bridge se     : ok={b_ok}  TLS-fail={b_tls}  other={b_other}\n")
    if a_tls and b_tls:
        print("Dono me TLS fail -> Geonode ke kuch exit node kharab hain. Bridge theek hai.")
    elif b_tls and not a_tls:
        print("Sirf bridge me fail -> masla hamare bridge me hai.")
    elif not a_tls and not b_tls:
        print("Dono theek -> is waqt proxy ka rasta saaf hai; error tab ka haal tha.")
    else:
        print("Sirf seedha SOCKS5 fail -> ajeeb; dobara chala kar dekho.")


if __name__ == "__main__":
    asyncio.run(main())
