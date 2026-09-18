#!/usr/bin/env python3
"""card_lock.py -- card aur Employee ID ka taala, kai instance aur kai system ke beech.

Ek hi waqt me kai browser order laga rahe hon (ek system par 4 instance, aur
waise hi doosre system par) to do cheezein takra sakti hain:

1. **Ek hi card do jagah uth jaye.** Sheet me koi "transaction" nahi hota --
   do instance ek saath padhein to dono ko wahi khaali row dikhti hai.
   Ilaaj: row par apna *token* likho, thoda ruko, dobara padho. Jiska token
   wahan bacha hai, row usi ki. Doosra agli row dekhta hai.

2. **Ek Employee ID par do payment ek saath.** Bank OTP us employee ke number
   par bhejta hai, aur OTP API bhi employee ID se hi OTP deti hai. Do order ek
   saath us ID par OTP maangein to dono ko ek hi OTP milta hai -- ek ka order
   galat OTP se marta hai, doosre ka OTP chori ho jaata hai.
   Ilaaj: payment shuru karne se pehle us card ki row `PAYING` ki jaati hai.
   Jab tak kisi bhi card tab (payment_details, System_1, System_2...) me usi
   Employee ID ki koi row `PAYING` hai, baaki line me rukte hain. Isliye ye
   taala saare systems ke beech kaam karta hai -- sab ek hi sheet dekhte hain.

   Taala sirf payment ke hisse par hai (checkout ka Pay now -> OTP -> confirm).
   Account banana, cart, pata bharna -- ye sab saath-saath chalte rehte hain.
   Ek hi Employee ID ke saare card hon to bhi kaam rukta nahi, bas payment ek
   ke baad ek hota hai.

Row ka `Status` (G) aur `Note` (I) hi taale ka kaam karte hain:

    (khaali)   card bacha hai
    RUNNING    kisi instance ne utha liya, abhi payment nahi  (Note: claim|ms|owner)
    PAYING     is card par payment/OTP chal raha hai          (Note: pay|ms|owner)
    complete   use ho gaya (place_order likhta hai)
    CHECK      card bhara gaya tha par nateeja pata nahi -- bank/order dekho

Instance mar jaye to taala hamesha na atka rahe, isliye `STALE_SEC` se purana
RUNNING/PAYING taala ginti me nahi aata (card phir bhi dobara nahi uthta --
wo haath se dekhna hai).
"""
import os
import re
import time
import random
import socket

import order_plan

PAY_BUSY = "RUNNING"
PAY_PAYING = "PAYING"
PAY_CHECK = "CHECK"

# Ek payment ka sabse lamba raasta: OTP 12 minute x 3 koshish + confirm. Isse
# purana taala kisi mare hue instance ka hi ho sakta hai.
STALE_SEC = 45 * 60

_TOKEN = re.compile(r"^(claim|pay|acct)\|(\d+)\|(.+)$")


def log(*a):
    print(*a, flush=True)


def owner_id(slot):
    """Kaun hai -- system ka naam, process, aur instance number."""
    return "%s:%d:W%s" % (socket.gethostname(), os.getpid(), slot)


def make_token(kind, owner, ms=None):
    return "%s|%d|%s" % (kind, int(ms if ms is not None else time.time() * 1000),
                         owner)


def parse_token(note):
    m = _TOKEN.match((note or "").strip())
    if not m:
        return None
    return {"kind": m.group(1), "ms": int(m.group(2)), "owner": m.group(3)}


def _now_str():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _age_sec(rec):
    """Taala kitna purana hai. Token me ms ho to wahi, warna