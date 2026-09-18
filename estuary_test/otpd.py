"""otpd.py -- otpdoctor.in se number aur OTP, LOCAL test ke liye.

Server wala `nykaa_otpdoctor.py` DB se key maangta hai aur project ke aadhe
module import karta hai. Yahan wo nahi chahiye -- ye ek akela test hai, isliye
sirf teen kaam: number lo, OTP lo, number wapas karo.

ESTUARY KE LIYE "OTHER"
-----------------------
otpdoctor par har site ka apna service id hota hai (Nykaa ke gyarah hain).
Estuary jaisi chhoti site ka koi id nahi hai -- uske liye "Any Other" wale
number hain, jo kisi bhi site ka SMS le lete hain. Neeche unki list SASTE SE
MEHNGE ke kram me hai, kyunki stock server ke hisaab se khatam hota hai: ek par
ruk jaana matlab baaki paanch ke paas number pade rehna.

`mothersgold` jaan bujh kar list me nahi hai -- uske naam me "other" ke akshar
aate hain, par wo "Any Other" wali cheez nahi hai.
"""
import os
import re
import time
import urllib.parse
import urllib.request

BASE = "https://otpdoctor.in/stubs/handler_api.php"
COUNTRY = "in"
KEY = os.environ.get("OTPDOCTOR_API_KEY", "CHANGE_ME_SECRET")

# (id, naam, server, daam) -- saste se mehnge
SERVICES = [
    ("3660",  "Any Other",       "IN-A",           11.0),
    ("6283",  "AnyOther",        "IN4",            12.5),
    ("7112",  "AnyOther",        "IN13",           13.0),
    ("15760", "All Any other",   "MultiSms IN2",   13.5),
    ("12827", "ALL Any Other",   "ALL (60 sec)",   14.0),
    ("13183", "ALL Any Other 2", "ALL (60 sec)",   14.0),
]

POLL_EVERY = 10
WAIT_MIN = float(os.environ.get("ESTUARY_OTP_WAIT_MIN", 5))


def _call(action, **params):
    q = {"api_key": KEY, "action": action}
    q.update({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(q),
                                 headers={"Accept": "text/plain",
                                          "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "ignore").strip()
    except Exception as e:
        return "HTTP_ERROR:%s" % e


def balance():
    r = _call("getBalance")
    return r.split(":", 1)[1] if r.startswith("ACCESS_BALANCE:") else r


def to_10(phone):
    """Provider country code ke saath deta hai (`919334013595`)."""
    d = re.sub(r"\D", "", phone or "")
    return d[-10:] if len(d) >= 10 else d


def buy():
    tried = []
    for sid, name, server, price in SERVICES:
        r = _call("getNumber", service=sid, country=COUNTRY)
        if r.startswith("ACCESS_NUMBER:"):
            p = r.split(":")
            if len(p) < 3:
                continue
            h = {"handle": p[1], "phone": to_10(p[2]), "service": sid,
                 "name": name, "server": server, "price": price,
                 "bought_at": time.time()}
            print("[otp] number: %s  (%s - %s - Rs %g)" % (h["phone"], name, server, price))
            return h
        if "NO_BALANCE" in r:
            raise RuntimeError("otpdoctor ka balance khatam")
        if "BAD_KEY" in r:
            raise RuntimeError("otpdoctor ki API key galat hai")
        tried.append("%s/%s:%s" % (name, server, r.split(":")[0][:18]))
    print("[otp] kisi server par number nahi mila -- " + ", ".join(tried))
    return None


def extract(sms):
    """SMS me se code. Pehle 'code 1234' jaisa dhoondho, warna koi bhi 4-6 ank."""
    m = re.search(r"(?:otp|code|pin)\D{0,12}(\d{4,6})", sms or "", re.I)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{4,6})\b", sms or "")
    return m.group(1) if m else None


def get_otp(h, log=print):
    tries = max(1, int(WAIT_MIN * 60 / POLL_EVERY))
    for i in range(1, tries + 1):
        time.sleep(POLL_EVERY)
        r = _call("getStatus", id=h["handle"])
        if r.startswith("STATUS_OK"):
            raw = r.split(":", 1)[1] if ":" in r else ""
            code = extract(raw)
            log("[otp] SMS: %s -> code %s" % (raw[:90], code))
            return code
        if "STATUS_CANCEL" in r or "NO_ACTIVATION" in r:
            log("[otp] number khatam ho gaya (%s)" % r[:40])
            return None
        log("[otp] wait %d/%d (%ds of %g min)" % (i, tries, i * POLL_EVERY, WAIT_MIN))
    return None


def resend(h):
    return _call("setStatus", id=h["handle"], status="3").startswith("ACCESS_RETRY_GET")


def cancel(h, log=print):
    """Number wapas -- aur SACH ME wapas.

    Pehle ~2 minute provider `WAIT_CANCEL:<second>` lautata hai aur number
    chalu rehta hai. Ek baar bhej kar bhool jaana matlab har fail hue test ka
    paisa jal jaana, isliye yahan intezaar karke dobara bheja jaata hai.
    """
    end = time.time() + 300
    while time.time() < end:
        r = _call("setStatus", id=h["handle"], status="8")
        if r.startswith("ACCESS_CANCEL") or "CANCEL" in r and "WAIT" not in r:
            log("[otp] number wapas kar diya")
            return True
        m = re.search(r"WAIT_CANCEL:(\d+)", r)
        if m:
            wait = min(int(m.group(1)) + 3, 70)
            log("[otp] cancel abhi manaa hai, %ds ruk kar dobara" % wait)
            time.sleep(wait)
            continue
        log("[otp] cancel ka jawab: %s" % r[:60])
        return False
    return False
