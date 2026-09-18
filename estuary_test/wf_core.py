# #!/usr/bin/env python3
# """place_order.py -- product chuno, cart me daalo, aur checkout tak le jao.

#     python place_order.py --product black-white-ginger-ale --pack "Pack of 02"
#     python place_order.py --product whisky-blending-water-750ml --pack "Pack of 01"
#     python place_order.py --product ... --pack ... --show      # browser dikhao


# -------------------------------------------------------------
# Checkout dabane ke baad payment ka panna khul jaata hai aur script wahin ruk
# kar browser KHULA CHHOD DETI hai. Card ke number, CVV, aur uske baad bank ka
# apna panna (Corporate ID / Employee ID / OTP) -- ye bank ki payment-jaanch hai,
# aur use script se bharna is auzaar ka kaam nahi hai. Wo ek kadam aadmi ke haath
# me rehta hai.

# Waise bhi bank ka OTP CARDHOLDER ke phone par jaata hai, kisi rented number par
# nahi -- to wo kadam script se ho hi nahi sakta.

# DO BAATEIN JO NAAP KAR MILI
# ---------------------------
# 1. Pack/unit ka chunav radio button se hota hai aur uske badalne par form ka
#    chhupa hua `id` (variant id) badalta hai. Isliye add-to-cart se PEHLE wahi
#    id padh kar milaayi jaati hai -- warna galat pack cart me chala jaata aur
#    pata bhi na chalta.
# 2. Cart ka checkout button (`#yt-checkout-button`) ek alag app ka hai, aur wo
#    nayi tab bhi khol sakta hai. Dono haal sambhale gaye hain.
# """
# import os
# import re
# import sys
# import glob
# import json
# import csv
# import time
# import argparse

# from playwright.sync_api import sync_playwright

# sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# HERE = os.path.dirname(os.path.abspath(__file__))
# SESSIONS = os.path.join(HERE, "sessions")
# OUT = os.path.join(HERE, "out")
# SHOP = "https://estuaryworld.com"
# os.makedirs(OUT, exist_ok=True)

# ADD_TO_CART = ["button.add-to-cart", "button:has-text('Add to cart')"]
# CART_OPEN = ["a[data-js-sidebar-handle]", "a[title='Open cart']"]
# CHECKOUT = ["#yt-checkout-button", "button:has-text('Checkout')",
#             "a:has-text('Checkout')"]


# def log(*a):
#     print(*a, flush=True)


# def newest_session():
#     fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
#     return fs[-1] if fs else None


# def find(scope, sels):
#     for s in sels:
#         try:
#             if scope.locator(s).count() and scope.locator(s).first.is_visible():
#                 return s
#         except Exception:
#             continue
#     return None


# def variant_id(page):
#     """Form me abhi kaunsa variant baitha hai."""
#     return page.evaluate(
#         """() => { const f = document.querySelector('form[action*="/cart/add"]');
#                    const i = f && f.querySelector('input[name="id"], select[name="id"]');
#                    return i ? String(i.value) : null; }""")


# def pick(page, value):
#     """Ek option (pack ya unit) chuno.

#     DO BAATEIN JO PEHLI KOSHISH ME TOOTI THIN:

#     1. Kai baar wo option PEHLE SE chuna hua hota hai (jaise "Pack of 02" is
#        panne ka default hai). Us par dobara click karne ki zaroorat hi nahi --
#        aur click karne ki koshish me script 30 second bekaar ganwati hai.
#     2. Label par seedha click nahi lagta: upar chipka hua header us par aa
#        jaata hai, aur Playwright dhake se click karne se mana kar deta hai
#        ("subtree intercepts pointer events"). Isliye click radio par kiya
#        jaata hai -- wahi cheez jo label dabane par bhi dabti hai, aur theme ko
#        wahi `change` milta hai.
#     """
#     res = page.evaluate(
#         """(v) => {
#              const rs = [...document.querySelectorAll('input[type=radio]')]
#                         .filter(x => (x.value || '').trim() === v);
#              if (!rs.length) return 'nahi-mila';
#              const r = rs[0];
#              if (r.checked) return 'pehle-se-chuna';
#              r.click();
#              return 'daba-diya';
#            }""", value)
#     log("      %s" % res)
#     if res == "nahi-mila":
#         return False
#     page.wait_for_timeout(2500)
#     return True


# def sr_frame(page):
#     """Checkout ka apna frame (Shiprocket). Wahi jisme pata bharna hai."""
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if fr.locator("#pincode").count():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def ship_address(page, acct):
#     """Checkout ke andar wala "Add shipping address" ka form.

#     ACCOUNT KA PATA YAHAN NAHI AATA. Ye Shiprocket ka apna checkout hai aur wo
#     apna alag pata maangta hai -- pincode, naam, flat, area, city, state,
#     email. Account par pata jodne se sirf Shopify ka khaata bharta hai; order
#     isi form se jaata hai.

#     Pincode bharne par city/state apne aap bhar jaate hain, isliye pehle
#     pincode jaata hai aur phir DEKHA jaata hai ki wo bhare ya nahi -- khaali
#     rahen to haath se bhare jaate hain.
#     """
#     f = None
#     for _ in range(20):
#         f = sr_frame(page)
#         if f:
#             break
#         page.wait_for_timeout(1500)
#     if not f:
#         return "checkout ka pata wala form nahi mila (shayad pata pehle se hai)"

#     ad = acct.get("address") or {}
#     pin = ad.get("zip") or "000000"
#     first = ad.get("first_name") or "Ishan"
#     last = ad.get("last_name") or "Gupta"
#     line1 = ad.get("address1") or "55/34 Shastri Nagar"
#     line2 = ad.get("address2") or "Near Kidwai Nagar Market"
#     city = ad.get("city") or "Kanpur"
#     state = ad.get("province") or "Uttar Pradesh"
#     email = acct.get("email") or ""

#     f.locator("#pincode").fill(pin)
#     page.wait_for_timeout(4000)          # city/state khud bharne ka mauka
#     f.locator("#name").fill(first)
#     f.locator("#lastName").fill(last)
#     f.locator("#line1").fill(line1)
#     f.locator("#line2").fill(line2)
#     for sel, val in (("#city", city), ("#state", state)):
#         try:
#             if not (f.locator(sel).input_value() or "").strip():
#                 f.locator(sel).fill(val)
#         except Exception:
#             pass
#     # EMAIL ZAROORI HAI. Ye form email ke bina aage badhta hi nahi -- aur wo
#     # chup-chaap rukta hai: koi laal lakeer nahi, bas button dabta hai aur wahi
#     # form khada rehta hai. Naap kar dekha gaya, isliye ye hamesha bhara jaata
#     # hai (khaali hone par hi nahi).
#     if email:
#         try:
#             f.locator("#email").fill(email)
#         except Exception:
#             pass

#     try:
#         f.locator("input[name='home']").first.check()
#     except Exception:
#         pass

#     got = f.locator("#addAddressBtn")
#     if not got.count():
#         return "'Add address' ka button nahi mila"

#     # ASLI MOUSE SE. Seedhe `click()` par ye button kuch nahi karta -- wahi baat
#     # jo Nykaa ke Proceed par mili thi. Mouse ko chalaate hue le jaao, dabao,
#     # chhodo -- tabhi form aage badhta hai.
#     box = got.first.bounding_box()
#     if box:
#         page.mouse.move(box["x"] + box["width"] / 2,
#                         box["y"] + box["height"] / 2, steps=12)
#         page.wait_for_timeout(400)
#         page.mouse.down()
#         page.wait_for_timeout(90)
#         page.mouse.up()
#     else:
#         got.first.click()

#     # Aage badha ya nahi -- FORM KE GAYAB HONE SE, andaze se nahi.
#     for _ in range(6):
#         page.wait_for_timeout(4000)
#         try:
#             if "Add shipping address" not in (f.locator("body").inner_text() or ""):
#                 return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#         except Exception:
#             return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#     return "pata bhara par form abhi bhi khada hai -- dekh lijiye"


# def real_click(page, loc):
#     """Asli mouse se dabao -- move, down, up.

#     Is checkout ke button seedhe `click()` par kuch nahi karte. Wahi baat Nykaa
#     ke Proceed par bhi mili thi: handler sirf us click ko maanta hai jo sach me
#     mouse se aaya ho.
#     """
#     box = loc.bounding_box()
#     if not box:
#         loc.click()
#         return
#     page.mouse.move(box["x"] + box["width"] / 2,
#                     box["y"] + box["height"] / 2, steps=12)
#     page.wait_for_timeout(400)
#     page.mouse.down()
#     page.wait_for_timeout(90)
#     page.mouse.up()


# def confirm_email(page, acct):
#     """Pata lagne ke BAAD ek aur kadam: "Confirm your email".

#     Pata jud jaane par checkout email alag se maangta hai ("Enter your email
#     address to receive order updates"), aur jab tak wo confirm na ho, payment
#     ke tareeke chunne layak nahi hote.
#     """
#     email = acct.get("email") or ""
#     if not email:
#         return "account par email hi nahi hai"
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     for _ in range(10):
#         try:
#             body = f.locator("body").inner_text() or ""
#         except Exception:
#             return "checkout ka frame chala gaya"
#         if "onfirm your email" not in body:
#             return "email confirm karne ki zaroorat nahi thi"

#         btn = f.locator("button:has-text('Confirm email')")
#         # DIKHNE WALA khaana chahiye, koi bhi nahi.
#         # Pata wale form ka `#email` DOM me pada rehta hai (chhupa hua), aur
#         # `.first` usi ko pakad leta hai -- phir `fill` 30 second baad timeout
#         # de kar mar jaata hai. `:visible` wahi ek shabd hai jo ye galti
#         # namumkin kar deta hai.
#         box = f.locator("input#email:visible, input[type='email']:visible")
#         if btn.count() and box.count():
#             box.first.fill(email)
#             page.wait_for_timeout(800)
#             real_click(page, btn.first)
#             page.wait_for_timeout(6000)
#             try:
#                 if "onfirm your email" not in (f.locator("body").inner_text() or ""):
#                     return "email confirm ho gaya (%s)" % email
#             except Exception:
#                 return "email confirm ho gaya (%s)" % email
#         page.wait_for_timeout(2000)

#     # Na ho paye to bata do ki wahan hai kya -- andaza mat lagao.
#     try:
#         ins = f.locator("input").evaluate_all(
#             "els => els.map(e => (e.id||'-')+'/'+(e.name||'-')+'/'+(e.type||'-'))")
#     except Exception:
#         ins = []
#     return "email confirm nahi hua | frame ke input: %s" % ", ".join(ins[:10])


# def sr_frame_any(page):
#     """Checkout ka frame -- chahe usme pata ka form ho ya delivery details."""
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if (fr.locator("body").inner_text() or "").strip():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def read_checkout(page):
#     """Checkout par abhi hai kya -- naap kar batao, andaza mat lagao.

#     Step 7 pehle "shayad pata pehle se hai" keh kar aage badh jaata tha. Wo
#     andaza tha. Yahan checkout ke frame se seedha padha jaata hai: kaun sa
#     pata laga hai, kitna shipping juda, aur payment ke kaun kaun se tareeke
#     saamne hain. Isse report me sirf wahi jaata hai jo sach me panne par hai.
#     """
#     f = sr_frame_any(page)
#     if not f:
#         return None
#     try:
#         body = f.locator("body").inner_text() or ""
#     except Exception:
#         return None
#     out = {"address": [], "pay": [], "total": ""}

#     # Pata: pincode wali line aur uske aas paas ki do line.
#     lines = [l.strip() for l in body.splitlines() if l.strip()]
#     for i, l in enumerate(lines):
#         if re.search(r"\d{6}", l) and len(l) > 12:
#             out["address"] = lines[max(0, i - 2):i + 3]
#             break

#     # Payment ke tareeke: unke apne dabbe se, poore panne ke shabdon se nahi.
#     try:
#         out["pay"] = [t.strip() for t in f.locator(
#             "label, [class*='paymentMethod'], [class*='payment-method']"
#         ).all_inner_texts() if 2 < len(t.strip()) < 60][:12]
#     except Exception:
#         pass

#     m = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", body)
#     if m:
#         out["total"] = m[-1]
#     return out


# def card_frame(page):
#     """Jahan card ke khaane hain. Easebuzz apna alag frame khol sakta hai."""
#     for fr in page.frames:
#         u = (fr.url or "").lower()
#         if any(k in u for k in ("easebuzz", "pay.", "payment", "3ds", "acs")):
#             try:
#                 if fr.locator("input:visible").count():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def card_fields(f):
#     """Frame me card ka khaana hai ya nahi -- GIN kar, andaza laga kar nahi.

#     Card ka khaana pehchaanne ka sabse pakka nishaan uski lambai hai: number
#     ka maxlength 16-19 hota hai aur CVV ka 3-4. Naam/placeholder har gateway
#     par alag hote hain, lambai nahi badalti.
#     """
#     try:
#         return f.locator("input:visible").evaluate_all(
#             """els => els.map(e => ({id: e.id || '', name: e.name || '',
#                                      ph: e.placeholder || '',
#                                      aria: e.getAttribute('aria-label') || '',
#                                      maxlen: e.maxLength}))
#                         .filter(o => /card|number|cvv|cvc|expiry|month|year|holder/i
#                                      .test(o.id + o.name + o.ph + o.aria)
#                                   || (o.maxlen >= 3 && o.maxlen <= 19))""")
#     except Exception:
#         return []


# def in_view(page, box):
#     """Ye jagah viewport ke andar hai ya nahi."""
#     vp = page.viewport_size or {"width": 1500, "height": 950}
#     return bool(box) and box["y"] > 0 and box["x"] > 0 \
#         and box["y"] + box["height"] < vp["height"] \
#         and box["x"] + box["width"] < vp["width"]


# def scroll_click(page, loc, tries=3):
#     """Pehle nazar ke saamne lao, PHIR asli mouse se dabao.

#     YAHI WO GALTI THI JISSE CARD KABHI CHUNA HI NAHI GAYA
#     -----------------------------------------------------
#     `bounding_box()` MAIN PANNE ke viewport ke hisaab se naapta hai, iframe ke
#     apne scroll ke hisaab se nahi. Card ka button checkout ke frame me neeche
#     pada tha -- UPI ka QR khula hone se aur neeche khisak gaya tha -- uska y
#     ~990 aata tha jabki viewport 950 ka hai. Mouse wahan pahunch hi nahi sakta,
#     to click panne ke kinare par gir jaata tha aur DOM me kuch nahi badalta tha.

#     Dhoka isme tha ki `count()` sach bolta raha ("button to hai") aur click
#     jhoothi nikalti rahi. Isliye ab: scroll karo, box DOBARA padho, aur tabhi
#     mouse chalao jab wo sach me saamne ho.
#     """
#     for _ in range(tries):
#         try:
#             loc.scroll_into_view_if_needed(timeout=5000)
#         except Exception:
#             pass
#         page.wait_for_timeout(600)
#         box = loc.bounding_box()
#         if in_view(page, box):
#             page.mouse.move(box["x"] + box["width"] / 2,
#                             box["y"] + box["height"] / 2, steps=12)
#             page.wait_for_timeout(300)
#             page.mouse.down()
#             page.wait_for_timeout(90)
#             page.mouse.up()
#             return "mouse"
#     # Saamne aaya hi nahi -- ab Playwright ka apna click, phir DOM ka.
#     try:
#         loc.click(timeout=5000)
#         return "click()"
#     except Exception:
#         pass
#     try:
#         loc.evaluate("e => e.click()")
#         return "dom-click"
#     except Exception:
#         return None


# # Card ka dabne wala hissa: ANDAR ka label, bahar ka wrapper nahi.
# CARD_TARGETS = [
#     "#payment-method-button-Card label.payment-button-heading",
#     "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
#     "#payment-method-button-Card",
# ]


# # Gateway ke panne ki pehchaan -- uski url me se koi shabd.
# GATEWAY_HINTS = ("easebuzz", "eazypay", "payment", "pay.", "3ds", "acs",
#                  "razorpay", "payu", "billdesk")


# def gateway_frames(page):
#     """Abhi khule hue gateway ke panne (frames) ki url."""
#     out = set()
#     for fr in page.frames:
#         u = (fr.url or "")
#         if u and any(k in u.lower() for k in GATEWAY_HINTS):
#             out.add(u)
#     return out


# def card_state(page, f):
#     """Card dabane se pehle/baad ka haal -- teen naap, teeno DOM se.

#     `frames`: gateway ke khule hue panne. YEHI SABSE PAKKA NISHAAN HAI.
#     `qr`    : UPI ka `#src-qrcode-payment-btn` maujood hai ya nahi.
#     `h`     : Card ke apne dabbe ki oonchai.

#     Teeno isliye ki akela koi bharosemand nahi nikla -- ek run me click SACH ME
#     laga tha (tasveer me Easebuzz ka panna khula dikha), phir bhi script ne
#     "daba nahi paye" bola. Wajah: Easebuzz ek ALAG overlay/iframe me khulta hai,
#     checkout ke andar accordion ki tarah nahi. To `h` waisi ki waisi rahi, aur
#     UPI ka QR button DOM me chhupa hua pada raha -- `qr` bhi nahi badla.
#     """
#     st = {"qr": False, "h": 0.0, "frames": gateway_frames(page)}
#     try:
#         st["qr"] = f.locator("#src-qrcode-payment-btn").count() > 0
#     except Exception:
#         pass
#     try:
#         st["h"] = f.locator("#payment-method-button-Card").first.evaluate(
#             "e => e.getBoundingClientRect().height") or 0.0
#     except Exception:
#         pass
#     return st


# def card_chosen(page, f, before):
#     """Click ke BAAD ka haal `before` se milao -- kuch bhi badla to chunav hua."""
#     now = card_state(page, f)
#     if now["frames"] - before["frames"]:
#         return True
#     if before["qr"] and not now["qr"]:
#         return True
#     if now["h"] > before["h"] + 30:
#         return True
#     return bool(card_fields(f))


# def pick_card_type(page, kind="Credit", secs=75):
#     """Easebuzz ke panne par "Credit Card" ya "Debit Card" chuno -- sirf click.

#     Card ka chunav DO kadam ka hai, ek nahi:
#       1. checkout par "Credit/Debit Card"  -> Easebuzz ka panna khulta hai
#       2. Easebuzz ke panne par "Credit Card" / "Debit Card" -> tab form aata hai
#     Pehla kadam `pick_card` karta hai, doosra ye. Form BHARNA isme nahi hai.

#     `text-is` se poora milaan hota hai, `has-text` se nahi -- warna checkout ka
#     "Credit/Debit Card" bhi is jaanch me aa girta, aur script galat frame me
#     click kar baithti.

#     Easebuzz DHEERE aata hai, isliye har frame ko baar baar dekha jaata hai --
#     ek baar dekh kar "nahi mila" keh dena wahi galti hoti jo pehle ho chuki hai.
#     """
#     sels = ["span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
#             "span.lang-en:text-is('%s Card')" % kind,
#             "*:text-is('%s Card')" % kind]
#     end = time.time() + secs
#     while time.time() < end:
#         for fr in page.frames:
#             if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#                 continue
#             for sel in sels:
#                 try:
#                     l = fr.locator(sel)
#                     if not l.count():
#                         continue
#                 except Exception:
#                     continue
#                 how = scroll_click(page, l.first)
#                 if not how:
#                     continue
#                 page.wait_for_timeout(5000)
#                 return "%s Card daba diya (%s) -- %s" % (
#                     kind, how, card_form_ready(page))
#         page.wait_for_timeout(2500)
#     return "%s Card ka option gateway ke panne par nahi mila" % kind


# def card_form_ready(page):
#     """Form saamne aaya ya nahi -- khaane GIN kar, andaze se nahi."""
#     for fr in page.frames:
#         if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#             continue
#         got = card_fields(fr)
#         if got:
#             return "form aa gaya (%s)" % ", ".join(
#                 (g["id"] or g["name"] or g["ph"] or "?") for g in got[:6])
#     return "form abhi saamne nahi aaya"


# def clear_blocker(page):
#     """Checkout ka "pehle se ek session khula hai" wala parda hatao.

#     NAAP KAR MILA: agar pichhli baar checkout beech me chhod diya gaya ho (jaise
#     payment ka panna khul jaane ke baad browser band kar dena), to Shiprocket
#     agli baar payment ke tareeke dikhata hi nahi. Uski jagah aata hai --
#     "This page isn't available! You already have an active session for the same
#     store" aur ek "Continue here" ka button.

#     Us haal me script "Credit/Debit Card ka khaana nahi mila" bolti thi, jo
#     sach to tha par gumraah karta tha: khaana isliye nahi tha ki panna hi doosra
#     tha. Ab parda pehle hataya jaata hai, aur hataya to bata diya jaata hai.
#     """
#     f = sr_frame_any(page)
#     if not f:
#         return ""
#     try:
#         body = (f.locator("body").inner_text() or "").lower()
#     except Exception:
#         return ""
#     if "active session" not in body and "page isn't available" not in body:
#         return ""
#     for sel in ("button:has-text('Continue here')",
#                 "a:has-text('Continue here')",
#                 "[role=button]:has-text('Continue here')"):
#         try:
#             l = f.locator(sel)
#             if l.count():
#                 scroll_click(page, l.first)
#                 page.wait_for_timeout(8000)
#                 return "purana session ka parda hata diya (Continue here)"
#         except Exception:
#             continue
#     return "CHETAVNI: purana session ka parda hai par 'Continue here' nahi mila"


# def pick_card(page):
#     """Payment ka tareeka chuno: Credit/Debit Card.

#     TEEN BAATEIN JO NAAP KAR MILIN
#     ------------------------------
#     1. Akela `label:has-text('Credit/Debit Card')` GALAT cheez pakadta hai --
#        wo poori list ko lapetne wale label se mil jaata hai. Isliye ya to
#        `#payment-method-button-Card` ke ANDAR ka label, ya `text-is` se poora
#        milaan -- `has-text` se nahi.
#     2. Handler wrapper par nahi, uske andar wale `label.payment-button-heading`
#        par baitha hai. Isliye pehle wahi dabaya jaata hai, wrapper aakhir me.
#     3. "Card khul gaya" ki purani jaanch sirf card ke KHAANE ginti thi. Par
#        khaane Easebuzz ke aane ke baad aate hain, aur chunav usse bahut pehle
#        ho jaata hai -- to khaane na dikhne par script "click nahi laga" samajh
#        leti thi, jabki asli baat ulti thi. Ab chunav aur khaane ALAG ALAG naape
#        jaate hain.
#     """
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     loc = None
#     used = ""
#     for _ in range(10):
#         for sel in CARD_TARGETS:
#             try:
#                 l = f.locator(sel)
#                 if l.count():
#                     loc, used = l.first, sel
#                     break
#             except Exception:
#                 continue
#         if loc:
#             break
#         page.wait_for_timeout(2000)
#     if not loc:
#         return "Credit/Debit Card ka khaana nahi mila (shayad email confirm baaki hai)"

#     # Chunav: teen koshish, har koshish ke baad 9 second tak dekho.
#     before = card_state(page, f)
#     how = None
#     for _ in range(3):
#         how = scroll_click(page, loc)
#         for _ in range(6):
#             page.wait_for_timeout(1500)
#             if card_chosen(page, f, before):
#                 break
#         if card_chosen(page, f, before):
#             break
#     if not card_chosen(page, f, before):
#         return "Card daba nahi paye (%s se koshish ki, UPI hi khula raha)" % (
#             how or "kisi tareeke")

#     log("      Card chun liya (%s | %s)" % (how, used))
#     naya = card_state(page, f)["frames"] - before["frames"]
#     if naya:
#         log("      gateway ka panna khula: %s" % list(naya)[0][:90])

#     # Ab khaano ka intezaar. Easebuzz pehle sirf "Credit Card / Debit Card"
#     # dikhata hai -- khaane usme se ek chunne ke BAAD aate hain. Isliye "khaane
#     # nahi aaye" ka matlab "click nahi laga" NAHI hai; wo do alag baatein hain
#     # aur alag alag batayi jaati hain.
#     for i in range(12):
#         page.wait_for_timeout(2500)
#         cf = card_frame(page)
#         if cf:
#             return "card ke khaane khul gaye (gateway ke frame me, %ds baad)" % ((i + 1) * 2.5)
#         got = card_fields(f)
#         if got:
#             return "card ke khaane khul gaye (checkout ke frame me: %s)" % (
#                 ", ".join((g["id"] or g["name"] or g["ph"] or "?") for g in got[:6]))
#     if naya:
#         return "Card chun liya aur gateway ka panna khul gaya (agla kadam: step 10)"
#     return "Card to chun liya, par khaane abhi tak nahi aaye -- out/ ki tasveer dekhiye"


# def wait_for_order(page, acct, minutes=12):
#     """Card bharne ke BAAD ka poora kaam -- order pakdo aur likh do.

#     Beech ka ek kadam (card aur bank ka OTP) aadmi karta hai. Uske baad script
#     khud dekhti rehti hai: order confirm hua ya nahi, uska number kya hai, aur
#     wo sab `orders.csv` me chala jaata hai. Yaani haath se sirf tees second ka
#     kaam bachta hai, us se pehle aur uske baad ka sab script ka.

#     Order hua ya nahi -- ye SHOPIFY SE poochha jaata hai (`/cart.js` khaali ho
#     jaana + confirmation ka panna), screen ke shabdon par bharosa karke nahi.
#     """
#     marks = ("thank you", "order placed", "order confirmed", "order id",
#              "your order", "order number")
#     end = time.time() + minutes * 60
#     log("      order ka intezaar (%d minute tak)..." % minutes)
#     while time.time() < end:
#         page.wait_for_timeout(5000)
#         url = ""
#         txt = ""
#         for pg in list(page.context.pages):
#             try:
#                 u = pg.url or ""
#                 t = (pg.inner_text("body") or "")
#             except Exception:
#                 continue
#             if any(m in t.lower() for m in marks) or "/thank" in u or "/orders/" in u:
#                 url, txt, page = u, t, pg
#                 break
#         if not txt:
#             continue

#         ref = ""
#         m = re.search(r"(?:order\s*(?:id|no\.?|number)\s*[:#]?\s*)([A-Za-z0-9#\-]{4,})",
#                       txt, re.I)
#         if m:
#             ref = m.group(1).strip("#")
#         if not ref:
#             m = re.search(r"#(\d{4,})", txt)
#             ref = m.group(1) if m else ""

#         try:
#             page.screenshot(path=os.path.join(OUT, "order_5_confirmed.png"))
#         except Exception:
#             pass

#         row = [time.strftime("%Y-%m-%d %H:%M:%S"), acct.get("phone", ""),
#                acct.get("email", ""), ref or "(number nahi mila)", url[:120]]
#         new_file = not os.path.exists(os.path.join(HERE, "orders.csv"))
#         with open(os.path.join(HERE, "orders.csv"), "a", newline="",
#                   encoding="utf-8") as fh:
#             w = csv.writer(fh)
#             if new_file:
#                 w.writerow(["when", "phone", "email", "order_ref", "url"])
#             w.writerow(row)
#         return "ORDER LAG GAYA -- %s  (orders.csv me likh diya)" % (ref or "number nahi mila")

#     return "itne me order confirm hota nahi dikha (chhod diya, kuch bigda nahi)"


# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--product", required=True, help="url ka aakhri hissa (handle)")
#     ap.add_argument("--pack", default="", help="jaise 'Pack of 02'")
#     ap.add_argument("--unit", default="", help="jaise '750 ML' (agar us product par ho)")
#     ap.add_argument("--session", default="")
#     ap.add_argument("--show", action="store_true", help="browser dikhao")
#     ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"],
#                     help="gateway ke panne par kaun sa -- Credit ya Debit")
#     ap.add_argument("--watch", type=int, default=0,
#                     help="card bharne ke baad itne minute tak order ka intezaar")
#     ap.add_argument("--hold", type=int, default=60,
#                     help="payment ka panna kitne second khula rahe")
#     a = ap.parse_args()

#     path = a.session or newest_session()
#     if not path:
#         log("koi session nahi mili -- pehle make_accounts.py chalao")
#         return 1
#     if not os.path.isabs(path):
#         p2 = os.path.join(SESSIONS, path)
#         path = p2 if os.path.exists(p2) else path
#     d = json.load(open(path, encoding="utf-8"))
#     log("account : %s / %s" % (d.get("phone"), d.get("email")))
#     if not d.get("address"):
#         log("CHETAVNI: is account par pata darj nahi hai -- pehle add_address.py chalao")

#     with sync_playwright() as p:
#         b = p.chromium.launch(headless=False, args=["--start-maximized"])
#         ctx = b.new_context(storage_state=d["state"], locale="en-IN",
#                             viewport={"width": 1500, "height": 950})
#         page = ctx.new_page()

#         log("\n1) product khol rahe hain: %s" % a.product)
#         page.goto("%s/products/%s" % (SHOP, a.product),
#                   wait_until="domcontentloaded", timeout=90000)
#         page.wait_for_timeout(5000)
#         for _ in range(3):
#             page.mouse.wheel(0, 900)
#             page.wait_for_timeout(700)

#         title = (page.title() or "").split("|")[0].strip()
#         log("   %s" % title)
#         before = variant_id(page)
#         log("   abhi ka variant: %s" % before)

#         if a.unit:
#             log("2) unit chun rahe hain: %s" % a.unit)
#             if not pick(page, a.unit):
#                 log("   (ye unit is panne par nahi mila -- aage badh rahe hain)")
#         if a.pack:
#             log("3) pack chun rahe hain: %s" % a.pack)
#             if not pick(page, a.pack):
#                 log("   FAIL: ye pack is panne par nahi mila")
#                 page.screenshot(path=os.path.join(OUT, "order_fail_pack.png"),
#                                 full_page=True)
#                 b.close()
#                 return 3

#         after = variant_id(page)
#         log("   chunne ke baad variant: %s%s"
#             % (after, "  (badal gaya)" if after != before else "  (wahi hai)"))
#         page.screenshot(path=os.path.join(OUT, "order_1_product.png"))

#         log("4) add to cart")
#         sel = find(page, ADD_TO_CART)
#         if not sel:
#             log("   FAIL: 'Add to cart' ka button nahi mila")
#             b.close()
#             return 4
#         page.locator(sel).first.click()
#         page.wait_for_timeout(6000)
#         page.screenshot(path=os.path.join(OUT, "order_2_added.png"))

#         # CART SACH ME BHARA YA NAHI -- Shopify se hi poochho, screen se nahi.
#         cart = page.evaluate(
#             "async () => (await (await fetch('/cart.js')).json())")
#         log("   cart me cheezein: %d | kul Rs %s"
#             % (cart.get("item_count", 0), (cart.get("total_price", 0) or 0) / 100))
#         for it in cart.get("items", []):
#             log("      %s | %s | Rs %s"
#                 % (it.get("product_title"), it.get("variant_title"),
#                    (it.get("line_price", 0) or 0) / 100))
#         if not cart.get("item_count"):
#             log("   FAIL: cart khaali hi rah gaya")
#             b.close()
#             return 5
#         if after and str(cart["items"][0].get("variant_id")) != str(after):
#             log("   CHETAVNI: cart me doosra variant gaya hai (%s) -- dekh lijiye"
#                 % cart["items"][0].get("variant_id"))

#         # CART KHUD KHUL JAATA HAI. Add to cart ke baad ye theme apna cart ka
#         # drawer khol deta hai. Us haal me "Open cart" par dobara click karna
#         # sirf nakaam nahi hota -- wo drawer ka apna overlay click ko rok deta
#         # hai aur script wahin 30 second atak jaati hai. Isliye pehle DEKHA
#         # jaata hai ki Checkout saamne hai ya nahi.
#         log("5) cart")
#         if find(page, CHECKOUT):
#             log("      cart to khud hi khul gaya")
#         else:
#             sel = find(page, CART_OPEN)
#             if sel:
#                 log("      cart khol rahe hain")
#                 page.locator(sel).first.click()
#                 page.wait_for_timeout(5000)
#             else:
#                 log("      /cart panne par ja rahe hain")
#                 page.goto("%s/cart" % SHOP, wait_until="domcontentloaded",
#                           timeout=60000)
#                 page.wait_for_timeout(5000)
#         page.screenshot(path=os.path.join(OUT, "order_3_cart.png"))

#         log("6) Checkout daba rahe hain")
#         sel = find(page, CHECKOUT)
#         if not sel:
#             log("   FAIL: Checkout ka button nahi mila")
#             page.screenshot(path=os.path.join(OUT, "order_fail_checkout.png"),
#                             full_page=True)
#             b.close()
#             return 6

#         # Checkout nayi tab bhi khol sakta hai -- dono haal sambhalo.
#         newpage = None
#         try:
#             with ctx.expect_page(timeout=15000) as np:
#                 page.locator(sel).first.click()
#             newpage = np.value
#         except Exception:
#             page.locator(sel).first.click() if False else None
#         pay = newpage or page
#         pay.wait_for_timeout(12000)

#         blk = clear_blocker(pay)
#         if blk:
#             log("   %s" % blk)

#         log("7) checkout ka apna pata")
#         ship = ship_address(pay, d)
#         log("      %s" % ship)
#         pay.wait_for_timeout(6000)

#         log("8) email confirm")
#         log("      %s" % confirm_email(pay, d))
#         pay.wait_for_timeout(4000)

#         st = read_checkout(pay)
#         if st:
#             log("   checkout par abhi:")
#             if st["address"]:
#                 for l in st["address"]:
#                     log("      pata: %s" % l[:90])
#             else:
#                 log("      pata: panne par koi pincode nahi dikha")
#             if st["pay"]:
#                 log("      payment ke tareeke: %s" % ", ".join(st["pay"])[:200])
#             if st["total"]:
#                 log("      panne ka aakhri daam: Rs %s" % st["total"])
#         else:
#             log("   (checkout ka frame nahi mila -- neeche ki tasveer dekhiye)")

#         log("9) Credit/Debit Card chun rahe hain")
#         log("      %s" % pick_card(pay))
#         pay.wait_for_timeout(5000)

#         log("10) gateway par %s Card chun rahe hain" % a.card_type)
#         log("      %s" % pick_card_type(pay, a.card_type))
#         pay.wait_for_timeout(3000)

#         log("\n   URL: %s" % pay.url)
#         try:
#             txt = pay.inner_text("body") or ""
#         except Exception:
#             txt = ""
#         lines = [l.strip() for l in txt.splitlines() if l.strip()][:16]
#         log("   panne par: %s" % " | ".join(lines)[:260])
#         rup = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", txt)
#         log("   panne par daam: %s" % (sorted(set(rup))[:8] or "koi nahi"))
#         # full_page ki tasveer par ye panna crash ho jaata hai (naap kar dekha:
#         # "Page crashed"). Sirf dikhne wala hissa kaafi hai.
#         try:
#             pay.screenshot(path=os.path.join(OUT, "order_4_payment.png"))
#             log("   tasveer: out/order_4_payment.png")
#         except Exception as e:
#             log("   (tasveer nahi bani: %s)" % str(e)[:60])

#         log("\n==========================================================")
#         log("   PAYMENT KA PANNA KHUL GAYA. Script yahin ruk rahi hai.")
#         log("   Card ke details aur bank ka OTP aap khud bhariye --")
#         log("   wo kadam jaan bujh kar is script me nahi hai.")
#         log("==========================================================")
#         if a.watch:
#             log("   Card aap bhariye. Uske baad ka kaam script khud kar legi.")
#             log("      %s" % wait_for_order(pay, d, a.watch))
#         if a.hold == 0:
#             log("   Browser khula rahega. Kaam khatam ho to yahan Enter dabaiye.")
#             try:
#                 input()
#             except Exception:
#                 pay.wait_for_timeout(600000)
#         else:
#             log("   (Enter ke liye koi keyboard nahi hai -- %ds baad band ho jayega)"
#                 % a.hold)
#             pay.wait_for_timeout(a.hold * 1000)
#         try:
#             b.close()
#         except Exception:
#             pass
#     return 0


# if __name__ == "__main__":
#     sys.exit(main())





# #!/usr/bin/env python3
# """place_order.py -- product -> cart -> checkout -> Credit Card -> fill details.

# Card fill auto; bank OTP manual.
# """
# import os
# import re
# import sys
# import glob
# import json
# import csv
# import time
# import argparse

# from playwright.sync_api import sync_playwright

# sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# HERE = os.path.dirname(os.path.abspath(__file__))
# SESSIONS = os.path.join(HERE, "sessions")
# OUT = os.path.join(HERE, "out")
# SHOP = "https://estuaryworld.com"
# os.makedirs(OUT, exist_ok=True)

# ADD_TO_CART = ["button.add-to-cart", "button:has-text('Add to cart')"]
# CART_OPEN = ["a[data-js-sidebar-handle]", "a[title='Open cart']"]
# CHECKOUT = ["#yt-checkout-button", "button:has-text('Checkout')",
#             "a:has-text('Checkout')"]

# DEFAULT_CARD = "0000000000000000"
# DEFAULT_EXP = "01/30"
# DEFAULT_HOLDER = "Test Holder"
# DEFAULT_CVV = "000"


# def log(*a):
#     print(*a, flush=True)


# def newest_session():
#     fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
#     return fs[-1] if fs else None


# def find(scope, sels):
#     for s in sels:
#         try:
#             if scope.locator(s).count() and scope.locator(s).first.is_visible():
#                 return s
#         except Exception:
#             continue
#     return None


# def variant_id(page):
#     return page.evaluate(
#         """() => { const f = document.querySelector('form[action*="/cart/add"]');
#                    const i = f && f.querySelector('input[name="id"], select[name="id"]');
#                    return i ? String(i.value) : null; }""")


# def pick(page, value):
#     res = page.evaluate(
#         """(v) => {
#              const rs = [...document.querySelectorAll('input[type=radio]')]
#                         .filter(x => (x.value || '').trim() === v);
#              if (!rs.length) return 'nahi-mila';
#              const r = rs[0];
#              if (r.checked) return 'pehle-se-chuna';
#              r.click();
#              return 'daba-diya';
#            }""", value)
#     log("      %s" % res)
#     if res == "nahi-mila":
#         return False
#     page.wait_for_timeout(2500)
#     return True


# def sr_frame(page):
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if fr.locator("#pincode").count():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def ship_address(page, acct):
#     f = None
#     for _ in range(20):
#         f = sr_frame(page)
#         if f:
#             break
#         page.wait_for_timeout(1500)
#     if not f:
#         return "checkout ka pata wala form nahi mila (shayad pata pehle se hai)"

#     ad = acct.get("address") or {}
#     pin = ad.get("zip") or "000000"
#     first = ad.get("first_name") or "Ishan"
#     last = ad.get("last_name") or "Gupta"
#     line1 = ad.get("address1") or "55/34 Shastri Nagar"
#     line2 = ad.get("address2") or "Near Kidwai Nagar Market"
#     city = ad.get("city") or "Kanpur"
#     state = ad.get("province") or "Uttar Pradesh"
#     email = acct.get("email") or ""

#     f.locator("#pincode").fill(pin)
#     page.wait_for_timeout(4000)
#     f.locator("#name").fill(first)
#     f.locator("#lastName").fill(last)
#     f.locator("#line1").fill(line1)
#     f.locator("#line2").fill(line2)
#     for sel, val in (("#city", city), ("#state", state)):
#         try:
#             if not (f.locator(sel).input_value() or "").strip():
#                 f.locator(sel).fill(val)
#         except Exception:
#             pass
#     if email:
#         try:
#             f.locator("#email").fill(email)
#         except Exception:
#             pass

#     try:
#         f.locator("input[name='home']").first.check()
#     except Exception:
#         pass

#     got = f.locator("#addAddressBtn")
#     if not got.count():
#         return "'Add address' ka button nahi mila"

#     box = got.first.bounding_box()
#     if box:
#         page.mouse.move(box["x"] + box["width"] / 2,
#                         box["y"] + box["height"] / 2, steps=12)
#         page.wait_for_timeout(400)
#         page.mouse.down()
#         page.wait_for_timeout(90)
#         page.mouse.up()
#     else:
#         got.first.click()

#     for _ in range(6):
#         page.wait_for_timeout(4000)
#         try:
#             if "Add shipping address" not in (f.locator("body").inner_text() or ""):
#                 return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#         except Exception:
#             return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#     return "pata bhara par form abhi bhi khada hai -- dekh lijiye"


# def real_click(page, loc):
#     box = loc.bounding_box()
#     if not box:
#         loc.click()
#         return
#     page.mouse.move(box["x"] + box["width"] / 2,
#                     box["y"] + box["height"] / 2, steps=12)
#     page.wait_for_timeout(400)
#     page.mouse.down()
#     page.wait_for_timeout(90)
#     page.mouse.up()


# def confirm_email(page, acct):
#     email = acct.get("email") or ""
#     if not email:
#         return "account par email hi nahi hai"
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     for _ in range(10):
#         try:
#             body = f.locator("body").inner_text() or ""
#         except Exception:
#             return "checkout ka frame chala gaya"
#         if "onfirm your email" not in body:
#             return "email confirm karne ki zaroorat nahi thi"

#         btn = f.locator("button:has-text('Confirm email')")
#         box = f.locator("input#email:visible, input[type='email']:visible")
#         if btn.count() and box.count():
#             box.first.fill(email)
#             page.wait_for_timeout(800)
#             real_click(page, btn.first)
#             page.wait_for_timeout(6000)
#             try:
#                 if "onfirm your email" not in (f.locator("body").inner_text() or ""):
#                     return "email confirm ho gaya (%s)" % email
#             except Exception:
#                 return "email confirm ho gaya (%s)" % email
#         page.wait_for_timeout(2000)

#     try:
#         ins = f.locator("input").evaluate_all(
#             "els => els.map(e => (e.id||'-')+'/'+(e.name||'-')+'/'+(e.type||'-'))")
#     except Exception:
#         ins = []
#     return "email confirm nahi hua | frame ke input: %s" % ", ".join(ins[:10])


# def sr_frame_any(page):
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if (fr.locator("body").inner_text() or "").strip():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def read_checkout(page):
#     f = sr_frame_any(page)
#     if not f:
#         return None
#     try:
#         body = f.locator("body").inner_text() or ""
#     except Exception:
#         return None
#     out = {"address": [], "pay": [], "total": ""}

#     lines = [l.strip() for l in body.splitlines() if l.strip()]
#     for i, l in enumerate(lines):
#         if re.search(r"\b\d{6}\b", l) and len(l) > 12:
#             out["address"] = lines[max(0, i - 2):i + 3]
#             break

#     try:
#         out["pay"] = [t.strip() for t in f.locator(
#             "label, [class*='paymentMethod'], [class*='payment-method']"
#         ).all_inner_texts() if 2 < len(t.strip()) < 60][:12]
#     except Exception:
#         pass

#     m = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", body)
#     if m:
#         out["total"] = m[-1]
#     return out


# def card_frame(page):
#     for fr in page.frames:
#         u = (fr.url or "").lower()
#         if any(k in u for k in ("easebuzz", "pay.", "payment", "3ds", "acs")):
#             try:
#                 if fr.locator("input:visible").count():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def card_fields(f):
#     try:
#         return f.locator("input:visible").evaluate_all(
#             """els => els.map(e => ({id: e.id || '', name: e.name || '',
#                                      ph: e.placeholder || '',
#                                      aria: e.getAttribute('aria-label') || '',
#                                      maxlen: e.maxLength}))
#                         .filter(o => /card|number|cvv|cvc|expiry|month|year|holder/i
#                                      .test(o.id + o.name + o.ph + o.aria)
#                                   || (o.maxlen >= 3 && o.maxlen <= 19))""")
#     except Exception:
#         return []


# def in_view(page, box):
#     vp = page.viewport_size or {"width": 1500, "height": 950}
#     return bool(box) and box["y"] > 0 and box["x"] > 0 \
#         and box["y"] + box["height"] < vp["height"] \
#         and box["x"] + box["width"] < vp["width"]


# def scroll_click(page, loc, tries=3):
#     for _ in range(tries):
#         try:
#             loc.scroll_into_view_if_needed(timeout=5000)
#         except Exception:
#             pass
#         page.wait_for_timeout(600)
#         box = loc.bounding_box()
#         if in_view(page, box):
#             page.mouse.move(box["x"] + box["width"] / 2,
#                             box["y"] + box["height"] / 2, steps=12)
#             page.wait_for_timeout(300)
#             page.mouse.down()
#             page.wait_for_timeout(90)
#             page.mouse.up()
#             return "mouse"
#     try:
#         loc.click(timeout=5000)
#         return "click()"
#     except Exception:
#         pass
#     try:
#         loc.evaluate("e => e.click()")
#         return "dom-click"
#     except Exception:
#         return None


# CARD_TARGETS = [
#     "#payment-method-button-Card label.payment-button-heading",
#     "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
#     "#payment-method-button-Card",
# ]

# GATEWAY_HINTS = ("easebuzz", "eazypay", "payment", "pay.", "3ds", "acs",
#                  "razorpay", "payu", "billdesk")


# def gateway_frames(page):
#     out = set()
#     for fr in page.frames:
#         u = (fr.url or "")
#         if u and any(k in u.lower() for k in GATEWAY_HINTS):
#             out.add(u)
#     return out


# def card_state(page, f):
#     st = {"qr": False, "h": 0.0, "frames": gateway_frames(page)}
#     try:
#         st["qr"] = f.locator("#src-qrcode-payment-btn").count() > 0
#     except Exception:
#         pass
#     try:
#         st["h"] = f.locator("#payment-method-button-Card").first.evaluate(
#             "e => e.getBoundingClientRect().height") or 0.0
#     except Exception:
#         pass
#     return st


# def card_chosen(page, f, before):
#     now = card_state(page, f)
#     if now["frames"] - before["frames"]:
#         return True
#     if before["qr"] and not now["qr"]:
#         return True
#     if now["h"] > before["h"] + 30:
#         return True
#     return bool(card_fields(f))


# def pick_card_type(page, kind="Credit", secs=75):
#     sels = ["span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
#             "span.lang-en:text-is('%s Card')" % kind,
#             "*:text-is('%s Card')" % kind]
#     end = time.time() + secs
#     while time.time() < end:
#         for fr in page.frames:
#             if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#                 continue
#             for sel in sels:
#                 try:
#                     l = fr.locator(sel)
#                     if not l.count():
#                         continue
#                 except Exception:
#                     continue
#                 how = scroll_click(page, l.first)
#                 if not how:
#                     continue
#                 page.wait_for_timeout(5000)
#                 return "%s Card daba diya (%s) -- %s" % (
#                     kind, how, card_form_ready(page))
#         page.wait_for_timeout(2500)
#     return "%s Card ka option gateway ke panne par nahi mila" % kind


# def card_form_ready(page):
#     for fr in page.frames:
#         if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#             continue
#         got = card_fields(fr)
#         if got:
#             return "form aa gaya (%s)" % ", ".join(
#                 (g["id"] or g["name"] or g["ph"] or "?") for g in got[:6])
#     return "form abhi saamne nahi aaya"


# def clear_blocker(page):
#     f = sr_frame_any(page)
#     if not f:
#         return ""
#     try:
#         body = (f.locator("body").inner_text() or "").lower()
#     except Exception:
#         return ""
#     if "active session" not in body and "page isn't available" not in body:
#         return ""
#     for sel in ("button:has-text('Continue here')",
#                 "a:has-text('Continue here')",
#                 "[role=button]:has-text('Continue here')"):
#         try:
#             l = f.locator(sel)
#             if l.count():
#                 scroll_click(page, l.first)
#                 page.wait_for_timeout(8000)
#                 return "purana session ka parda hata diya (Continue here)"
#         except Exception:
#             continue
#     return "CHETAVNI: purana session ka parda hai par 'Continue here' nahi mila"


# def pick_card(page):
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     loc = None
#     used = ""
#     for _ in range(10):
#         for sel in CARD_TARGETS:
#             try:
#                 l = f.locator(sel)
#                 if l.count():
#                     loc, used = l.first, sel
#                     break
#             except Exception:
#                 continue
#         if loc:
#             break
#         page.wait_for_timeout(2000)
#     if not loc:
#         return "Credit/Debit Card ka khaana nahi mila (shayad email confirm baaki hai)"

#     before = card_state(page, f)
#     how = None
#     for _ in range(3):
#         how = scroll_click(page, loc)
#         for _ in range(6):
#             page.wait_for_timeout(1500)
#             if card_chosen(page, f, before):
#                 break
#         if card_chosen(page, f, before):
#             break
#     if not card_chosen(page, f, before):
#         return "Card daba nahi paye (%s se koshish ki, UPI hi khula raha)" % (
#             how or "kisi tareeke")

#     log("      Card chun liya (%s | %s)" % (how, used))
#     naya = card_state(page, f)["frames"] - before["frames"]
#     if naya:
#         log("      gateway ka panna khula: %s" % list(naya)[0][:90])

#     for i in range(12):
#         page.wait_for_timeout(2500)
#         cf = card_frame(page)
#         if cf:
#             return "card ke khaane khul gaye (gateway ke frame me, %ds baad)" % ((i + 1) * 2.5)
#         got = card_fields(f)
#         if got:
#             return "card ke khaane khul gaye (checkout ke frame me: %s)" % (
#                 ", ".join((g["id"] or g["name"] or g["ph"] or "?") for g in got[:6]))
#     if naya:
#         return "Card chun liya aur gateway ka panna khul gaya (agla kadam: step 10)"
#     return "Card to chun liya, par khaane abhi tak nahi aaye -- out/ ki tasveer dekhiye"


# def easebuzz_form_frame(page, secs=40):
#     end = time.time() + secs
#     while time.time() < end:
#         for fr in page.frames:
#             try:
#                 n = fr.locator(
#                     'input[name="card_number"], '
#                     'input[placeholder="Test Holder"], '
#                     'input[name="card_exp_date"], '
#                     'input[name="card_cvv"]'
#                 ).count()
#                 if n >= 1:
#                     return fr
#             except Exception:
#                 continue
#         try:
#             if page.locator('input[name="card_number"], input[name="card_cvv"]').count():
#                 return page
#         except Exception:
#             pass
#         page.wait_for_timeout(1500)
#     return None


# def _fill_one(fr, page, sels, value, label):
#     for sel in sels:
#         try:
#             loc = fr.locator(sel)
#             if not loc.count():
#                 continue
#             el = loc.first
#             try:
#                 if not el.is_visible():
#                     continue
#             except Exception:
#                 pass
#             el.scroll_into_view_if_needed(timeout=5000)
#             page.wait_for_timeout(200)
#             el.click(timeout=5000)
#             page.wait_for_timeout(150)
#             el.fill("")
#             el.type(str(value), delay=50)
#             page.wait_for_timeout(250)
#             got = ""
#             try:
#                 got = el.input_value() or ""
#             except Exception:
#                 pass
#             log("      %s fill -> '%s'" % (label, got[:28] if got else value))
#             return True
#         except Exception as e:
#             log("      %s try fail (%s): %s" % (label, sel[:40], str(e)[:50]))
#     return False


# def fill_card_details(page, number, exp, holder, cvv, click_pay=True):
#     fr = easebuzz_form_frame(page)
#     if not fr:
#         return "FAIL: card form frame nahi mila (Credit Card choose ke baad wait karo)"

#     num_clean = re.sub(r"\s+", "", number or "")
#     num_disp = " ".join(num_clean[i:i + 4] for i in range(0, len(num_clean), 4))

#     ok_n = _fill_one(fr, page, [
#         'input[name="card_number"]',
#         'input[placeholder="Test Holder"]',
#     ], num_disp, "Card Number")

#     ok_e = _fill_one(fr, page, [
#         'input[name="card_exp_date"]',
#         'input[placeholder="Test Holder"]',
#     ], exp, "MM/YY")

#     ok_h = _fill_one(fr, page, [
#         'input[placeholder="Test Holder"]',
#         'input[name^="ebz_card_holder_name"]',
#         'input[name*="card_holder" i]',
#     ], holder, "Card Holder")

#     ok_c = _fill_one(fr, page, [
#         'input[name="card_cvv"]',
#         'input[placeholder="Test Holder"]',
#     ], cvv, "CVV")

#     page.wait_for_timeout(1000)

#     pay_ok = False
#     if click_pay:
#         for scope in (fr, page):
#             for sel in (
#                 'button:has-text("Pay")',
#                 'button:has-text("Pay ₹")',
#                 'button:has-text("Pay Rs")',
#             ):
#                 try:
#                     loc = scope.locator(sel)
#                     if loc.count() and loc.first.is_visible():
#                         log("      Pay button click")
#                         scroll_click(page, loc.first)
#                         pay_ok = True
#                         page.wait_for_timeout(3000)
#                         break
#                 except Exception:
#                     continue
#             if pay_ok:
#                 break

#     return "number=%s | exp=%s | holder=%s | cvv=%s | pay=%s" % (
#         "ok" if ok_n else "FAIL",
#         "ok" if ok_e else "FAIL",
#         "ok" if ok_h else "FAIL",
#         "ok" if ok_c else "FAIL",
#         "clicked" if pay_ok else "skip",
#     )


# def wait_for_order(page, acct, minutes=12):
#     marks = ("thank you", "order placed", "order confirmed", "order id",
#              "your order", "order number")
#     end = time.time() + minutes * 60
#     log("      order ka intezaar (%d minute tak)..." % minutes)
#     while time.time() < end:
#         page.wait_for_timeout(5000)
#         url = ""
#         txt = ""
#         for pg in list(page.context.pages):
#             try:
#                 u = pg.url or ""
#                 t = (pg.inner_text("body") or "")
#             except Exception:
#                 continue
#             if any(m in t.lower() for m in marks) or "/thank" in u or "/orders/" in u:
#                 url, txt, page = u, t, pg
#                 break
#         if not txt:
#             continue

#         ref = ""
#         m = re.search(r"(?:order\s*(?:id|no\.?|number)\s*[:#]?\s*)([A-Za-z0-9#\-]{4,})",
#                       txt, re.I)
#         if m:
#             ref = m.group(1).strip("#")
#         if not ref:
#             m = re.search(r"#(\d{4,})", txt)
#             ref = m.group(1) if m else ""

#         try:
#             page.screenshot(path=os.path.join(OUT, "order_5_confirmed.png"))
#         except Exception:
#             pass

#         row = [time.strftime("%Y-%m-%d %H:%M:%S"), acct.get("phone", ""),
#                acct.get("email", ""), ref or "(number nahi mila)", url[:120]]
#         new_file = not os.path.exists(os.path.join(HERE, "orders.csv"))
#         with open(os.path.join(HERE, "orders.csv"), "a", newline="",
#                   encoding="utf-8") as fh:
#             w = csv.writer(fh)
#             if new_file:
#                 w.writerow(["when", "phone", "email", "order_ref", "url"])
#             w.writerow(row)
#         return "ORDER LAG GAYA -- %s  (orders.csv me likh diya)" % (ref or "number nahi mila")

#     return "itne me order confirm hota nahi dikha (chhod diya, kuch bigda nahi)"


# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--product", required=True)
#     ap.add_argument("--pack", default="")
#     ap.add_argument("--unit", default="")
#     ap.add_argument("--session", default="")
#     ap.add_argument("--show", action="store_true")
#     ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
#     ap.add_argument("--card", default=DEFAULT_CARD)
#     ap.add_argument("--exp", default=DEFAULT_EXP)
#     ap.add_argument("--holder", default=DEFAULT_HOLDER)
#     ap.add_argument("--cvv", default=DEFAULT_CVV)
#     ap.add_argument("--no-pay-click", action="store_true")
#     ap.add_argument("--watch", type=int, default=0)
#     ap.add_argument("--hold", type=int, default=60)
#     a = ap.parse_args()

#     path = a.session or newest_session()
#     if not path:
#         log("koi session nahi mili -- pehle make_accounts.py chalao")
#         return 1
#     if not os.path.isabs(path):
#         p2 = os.path.join(SESSIONS, path)
#         path = p2 if os.path.exists(p2) else path
#     d = json.load(open(path, encoding="utf-8"))
#     log("account : %s / %s" % (d.get("phone"), d.get("email")))
#     if not d.get("address"):
#         log("CHETAVNI: is account par pata darj nahi hai -- pehle add_address.py chalao")

#     with sync_playwright() as p:
#         b = p.chromium.launch(headless=False, args=["--start-maximized"])
#         ctx = b.new_context(storage_state=d["state"], locale="en-IN",
#                             viewport={"width": 1500, "height": 950})
#         page = ctx.new_page()

#         log("\n1) product khol rahe hain: %s" % a.product)
#         page.goto("%s/products/%s" % (SHOP, a.product),
#                   wait_until="domcontentloaded", timeout=90000)
#         page.wait_for_timeout(5000)
#         for _ in range(3):
#             page.mouse.wheel(0, 900)
#             page.wait_for_timeout(700)

#         title = (page.title() or "").split("|")[0].strip()
#         log("   %s" % title)
#         before = variant_id(page)
#         log("   abhi ka variant: %s" % before)

#         if a.unit:
#             log("2) unit chun rahe hain: %s" % a.unit)
#             if not pick(page, a.unit):
#                 log("   (ye unit is panne par nahi mila -- aage badh rahe hain)")
#         if a.pack:
#             log("3) pack chun rahe hain: %s" % a.pack)
#             if not pick(page, a.pack):
#                 log("   FAIL: ye pack is panne par nahi mila")
#                 page.screenshot(path=os.path.join(OUT, "order_fail_pack.png"),
#                                 full_page=True)
#                 b.close()
#                 return 3

#         after = variant_id(page)
#         log("   chunne ke baad variant: %s%s"
#             % (after, "  (badal gaya)" if after != before else "  (wahi hai)"))
#         page.screenshot(path=os.path.join(OUT, "order_1_product.png"))

#         log("4) add to cart")
#         sel = find(page, ADD_TO_CART)
#         if not sel:
#             log("   FAIL: 'Add to cart' ka button nahi mila")
#             b.close()
#             return 4
#         page.locator(sel).first.click()
#         page.wait_for_timeout(6000)
#         page.screenshot(path=os.path.join(OUT, "order_2_added.png"))

#         cart = page.evaluate(
#             "async () => (await (await fetch('/cart.js')).json())")
#         log("   cart me cheezein: %d | kul Rs %s"
#             % (cart.get("item_count", 0), (cart.get("total_price", 0) or 0) / 100))
#         for it in cart.get("items", []):
#             log("      %s | %s | Rs %s"
#                 % (it.get("product_title"), it.get("variant_title"),
#                    (it.get("line_price", 0) or 0) / 100))
#         if not cart.get("item_count"):
#             log("   FAIL: cart khaali hi rah gaya")
#             b.close()
#             return 5
#         if after and str(cart["items"][0].get("variant_id")) != str(after):
#             log("   CHETAVNI: cart me doosra variant gaya hai (%s) -- dekh lijiye"
#                 % cart["items"][0].get("variant_id"))

#         log("5) cart")
#         if find(page, CHECKOUT):
#             log("      cart to khud hi khul gaya")
#         else:
#             sel = find(page, CART_OPEN)
#             if sel:
#                 log("      cart khol rahe hain")
#                 page.locator(sel).first.click()
#                 page.wait_for_timeout(5000)
#             else:
#                 log("      /cart panne par ja rahe hain")
#                 page.goto("%s/cart" % SHOP, wait_until="domcontentloaded",
#                           timeout=60000)
#                 page.wait_for_timeout(5000)
#         page.screenshot(path=os.path.join(OUT, "order_3_cart.png"))

#         log("6) Checkout daba rahe hain")
#         sel = find(page, CHECKOUT)
#         if not sel:
#             log("   FAIL: Checkout ka button nahi mila")
#             page.screenshot(path=os.path.join(OUT, "order_fail_checkout.png"),
#                             full_page=True)
#             b.close()
#             return 6

#         newpage = None
#         try:
#             with ctx.expect_page(timeout=15000) as np:
#                 page.locator(sel).first.click()
#             newpage = np.value
#         except Exception:
#             pass
#         pay = newpage or page
#         pay.wait_for_timeout(12000)

#         blk = clear_blocker(pay)
#         if blk:
#             log("   %s" % blk)

#         log("7) checkout ka apna pata")
#         ship = ship_address(pay, d)
#         log("      %s" % ship)
#         pay.wait_for_timeout(6000)

#         log("8) email confirm")
#         log("      %s" % confirm_email(pay, d))
#         pay.wait_for_timeout(4000)

#         st = read_checkout(pay)
#         if st:
#             log("   checkout par abhi:")
#             if st["address"]:
#                 for l in st["address"]:
#                     log("      pata: %s" % l[:90])
#             else:
#                 log("      pata: panne par koi pincode nahi dikha")
#             if st["pay"]:
#                 log("      payment ke tareeke: %s" % ", ".join(st["pay"])[:200])
#             if st["total"]:
#                 log("      panne ka aakhri daam: Rs %s" % st["total"])
#         else:
#             log("   (checkout ka frame nahi mila -- neeche ki tasveer dekhiye)")

#         log("9) Credit/Debit Card chun rahe hain")
#         log("      %s" % pick_card(pay))
#         pay.wait_for_timeout(5000)

#         log("10) gateway par %s Card chun rahe hain" % a.card_type)
#         log("      %s" % pick_card_type(pay, a.card_type))
#         pay.wait_for_timeout(3000)

#         log("11) Card details fill")
#         log("      %s" % fill_card_details(
#             pay, a.card, a.exp, a.holder, a.cvv,
#             click_pay=not a.no_pay_click,
#         ))
#         pay.wait_for_timeout(2000)

#         log("\n   URL: %s" % pay.url)
#         try:
#             txt = pay.inner_text("body") or ""
#         except Exception:
#             txt = ""
#         lines = [l.strip() for l in txt.splitlines() if l.strip()][:16]
#         log("   panne par: %s" % " | ".join(lines)[:260])
#         rup = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", txt)
#         log("   panne par daam: %s" % (sorted(set(rup))[:8] or "koi nahi"))
#         try:
#             pay.screenshot(path=os.path.join(OUT, "order_4_payment.png"))
#             log("   tasveer: out/order_4_payment.png")
#         except Exception as e:
#             log("   (tasveer nahi bani: %s)" % str(e)[:60])

#         log("\n==========================================================")
#         log("   CARD FILL HO GAYA. Bank OTP aap khud bhariye.")
#         log("==========================================================")
#         if a.watch:
#             log("   OTP ke baad script order ka wait karegi.")
#             log("      %s" % wait_for_order(pay, d, a.watch))
#         if a.hold == 0:
#             log("   Browser khula rahega. Kaam khatam ho to yahan Enter dabaiye.")
#             try:
#                 input()
#             except Exception:
#                 pay.wait_for_timeout(600000)
#         else:
#             log("   (%ds baad band)" % a.hold)
#             pay.wait_for_timeout(a.hold * 1000)
#         try:
#             b.close()
#         except Exception:
#             pass
#     return 0


# if __name__ == "__main__":
#     sys.exit(main())


# #!/usr/bin/env python3
# """place_order.py -- product -> cart -> checkout -> Credit Card -> fill details.

# Card fill auto; bank OTP manual.
# """
# import os
# import re
# import sys
# import glob
# import json
# import csv
# import time
# import argparse

# from playwright.sync_api import sync_playwright

# sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# HERE = os.path.dirname(os.path.abspath(__file__))
# SESSIONS = os.path.join(HERE, "sessions")
# OUT = os.path.join(HERE, "out")
# SHOP = "https://estuaryworld.com"
# os.makedirs(OUT, exist_ok=True)

# ADD_TO_CART = ["button.add-to-cart", "button:has-text('Add to cart')"]
# CART_OPEN = ["a[data-js-sidebar-handle]", "a[title='Open cart']"]
# CHECKOUT = ["#yt-checkout-button", "button:has-text('Checkout')",
#             "a:has-text('Checkout')"]

# DEFAULT_CARD = "0000000000000000"
# DEFAULT_EXP = "01/30"
# DEFAULT_HOLDER = "Test Holder"
# DEFAULT_CVV = "000"
# DEFAULT_CORP_ID = "streakads"
# DEFAULT_EMP_ID = "CHANGE_ME_EMP_ID"


# def log(*a):
#     print(*a, flush=True)


# def newest_session():
#     fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
#     return fs[-1] if fs else None


# def find(scope, sels):
#     for s in sels:
#         try:
#             if scope.locator(s).count() and scope.locator(s).first.is_visible():
#                 return s
#         except Exception:
#             continue
#     return None


# def variant_id(page):
#     return page.evaluate(
#         """() => { const f = document.querySelector('form[action*="/cart/add"]');
#                    const i = f && f.querySelector('input[name="id"], select[name="id"]');
#                    return i ? String(i.value) : null; }""")


# def pick(page, value):
#     res = page.evaluate(
#         """(v) => {
#              const rs = [...document.querySelectorAll('input[type=radio]')]
#                         .filter(x => (x.value || '').trim() === v);
#              if (!rs.length) return 'nahi-mila';
#              const r = rs[0];
#              if (r.checked) return 'pehle-se-chuna';
#              r.click();
#              return 'daba-diya';
#            }""", value)
#     log("      %s" % res)
#     if res == "nahi-mila":
#         return False
#     page.wait_for_timeout(2500)
#     return True


# def sr_frame(page):
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if fr.locator("#pincode").count():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def ship_address(page, acct):
#     f = None
#     for _ in range(20):
#         f = sr_frame(page)
#         if f:
#             break
#         page.wait_for_timeout(1500)
#     if not f:
#         return "checkout ka pata wala form nahi mila (shayad pata pehle se hai)"

#     ad = acct.get("address") or {}
#     pin = ad.get("zip") or "000000"
#     first = ad.get("first_name") or "Ishan"
#     last = ad.get("last_name") or "Gupta"
#     line1 = ad.get("address1") or "55/34 Shastri Nagar"
#     line2 = ad.get("address2") or "Near Kidwai Nagar Market"
#     city = ad.get("city") or "Kanpur"
#     state = ad.get("province") or "Uttar Pradesh"
#     email = acct.get("email") or ""

#     f.locator("#pincode").fill(pin)
#     page.wait_for_timeout(4000)
#     f.locator("#name").fill(first)
#     f.locator("#lastName").fill(last)
#     f.locator("#line1").fill(line1)
#     f.locator("#line2").fill(line2)
#     for sel, val in (("#city", city), ("#state", state)):
#         try:
#             if not (f.locator(sel).input_value() or "").strip():
#                 f.locator(sel).fill(val)
#         except Exception:
#             pass
#     if email:
#         try:
#             f.locator("#email").fill(email)
#         except Exception:
#             pass

#     try:
#         f.locator("input[name='home']").first.check()
#     except Exception:
#         pass

#     got = f.locator("#addAddressBtn")
#     if not got.count():
#         return "'Add address' ka button nahi mila"

#     box = got.first.bounding_box()
#     if box:
#         page.mouse.move(box["x"] + box["width"] / 2,
#                         box["y"] + box["height"] / 2, steps=12)
#         page.wait_for_timeout(400)
#         page.mouse.down()
#         page.wait_for_timeout(90)
#         page.mouse.up()
#     else:
#         got.first.click()

#     for _ in range(6):
#         page.wait_for_timeout(4000)
#         try:
#             if "Add shipping address" not in (f.locator("body").inner_text() or ""):
#                 return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#         except Exception:
#             return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#     return "pata bhara par form abhi bhi khada hai -- dekh lijiye"


# def real_click(page, loc):
#     box = loc.bounding_box()
#     if not box:
#         loc.click()
#         return
#     page.mouse.move(box["x"] + box["width"] / 2,
#                     box["y"] + box["height"] / 2, steps=12)
#     page.wait_for_timeout(400)
#     page.mouse.down()
#     page.wait_for_timeout(90)
#     page.mouse.up()


# def confirm_email(page, acct):
#     email = acct.get("email") or ""
#     if not email:
#         return "account par email hi nahi hai"
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     for _ in range(10):
#         try:
#             body = f.locator("body").inner_text() or ""
#         except Exception:
#             return "checkout ka frame chala gaya"
#         if "onfirm your email" not in body:
#             return "email confirm karne ki zaroorat nahi thi"

#         btn = f.locator("button:has-text('Confirm email')")
#         box = f.locator("input#email:visible, input[type='email']:visible")
#         if btn.count() and box.count():
#             box.first.fill(email)
#             page.wait_for_timeout(800)
#             real_click(page, btn.first)
#             page.wait_for_timeout(6000)
#             try:
#                 if "onfirm your email" not in (f.locator("body").inner_text() or ""):
#                     return "email confirm ho gaya (%s)" % email
#             except Exception:
#                 return "email confirm ho gaya (%s)" % email
#         page.wait_for_timeout(2000)

#     try:
#         ins = f.locator("input").evaluate_all(
#             "els => els.map(e => (e.id||'-')+'/'+(e.name||'-')+'/'+(e.type||'-'))")
#     except Exception:
#         ins = []
#     return "email confirm nahi hua | frame ke input: %s" % ", ".join(ins[:10])


# def sr_frame_any(page):
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if (fr.locator("body").inner_text() or "").strip():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def read_checkout(page):
#     f = sr_frame_any(page)
#     if not f:
#         return None
#     try:
#         body = f.locator("body").inner_text() or ""
#     except Exception:
#         return None
#     out = {"address": [], "pay": [], "total": ""}

#     lines = [l.strip() for l in body.splitlines() if l.strip()]
#     for i, l in enumerate(lines):
#         if re.search(r"\b\d{6}\b", l) and len(l) > 12:
#             out["address"] = lines[max(0, i - 2):i + 3]
#             break

#     try:
#         out["pay"] = [t.strip() for t in f.locator(
#             "label, [class*='paymentMethod'], [class*='payment-method']"
#         ).all_inner_texts() if 2 < len(t.strip()) < 60][:12]
#     except Exception:
#         pass

#     m = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", body)
#     if m:
#         out["total"] = m[-1]
#     return out


# def card_frame(page):
#     for fr in page.frames:
#         u = (fr.url or "").lower()
#         if any(k in u for k in ("easebuzz", "pay.", "payment", "3ds", "acs")):
#             try:
#                 if fr.locator("input:visible").count():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def card_fields(f):
#     try:
#         return f.locator("input:visible").evaluate_all(
#             """els => els.map(e => ({id: e.id || '', name: e.name || '',
#                                      ph: e.placeholder || '',
#                                      aria: e.getAttribute('aria-label') || '',
#                                      maxlen: e.maxLength}))
#                         .filter(o => /card|number|cvv|cvc|expiry|month|year|holder/i
#                                      .test(o.id + o.name + o.ph + o.aria)
#                                   || (o.maxlen >= 3 && o.maxlen <= 19))""")
#     except Exception:
#         return []


# def in_view(page, box):
#     vp = page.viewport_size or {"width": 1500, "height": 950}
#     return bool(box) and box["y"] > 0 and box["x"] > 0 \
#         and box["y"] + box["height"] < vp["height"] \
#         and box["x"] + box["width"] < vp["width"]


# def scroll_click(page, loc, tries=3):
#     for _ in range(tries):
#         try:
#             loc.scroll_into_view_if_needed(timeout=5000)
#         except Exception:
#             pass
#         page.wait_for_timeout(600)
#         box = loc.bounding_box()
#         if in_view(page, box):
#             page.mouse.move(box["x"] + box["width"] / 2,
#                             box["y"] + box["height"] / 2, steps=12)
#             page.wait_for_timeout(300)
#             page.mouse.down()
#             page.wait_for_timeout(90)
#             page.mouse.up()
#             return "mouse"
#     try:
#         loc.click(timeout=5000)
#         return "click()"
#     except Exception:
#         pass
#     try:
#         loc.evaluate("e => e.click()")
#         return "dom-click"
#     except Exception:
#         return None


# CARD_TARGETS = [
#     "#payment-method-button-Card label.payment-button-heading",
#     "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
#     "#payment-method-button-Card",
# ]

# GATEWAY_HINTS = ("easebuzz", "eazypay", "payment", "pay.", "3ds", "acs",
#                  "razorpay", "payu", "billdesk")


# def gateway_frames(page):
#     out = set()
#     for fr in page.frames:
#         u = (fr.url or "")
#         if u and any(k in u.lower() for k in GATEWAY_HINTS):
#             out.add(u)
#     return out


# def card_state(page, f):
#     st = {"qr": False, "h": 0.0, "frames": gateway_frames(page)}
#     try:
#         st["qr"] = f.locator("#src-qrcode-payment-btn").count() > 0
#     except Exception:
#         pass
#     try:
#         st["h"] = f.locator("#payment-method-button-Card").first.evaluate(
#             "e => e.getBoundingClientRect().height") or 0.0
#     except Exception:
#         pass
#     return st


# def card_chosen(page, f, before):
#     now = card_state(page, f)
#     if now["frames"] - before["frames"]:
#         return True
#     if before["qr"] and not now["qr"]:
#         return True
#     if now["h"] > before["h"] + 30:
#         return True
#     return bool(card_fields(f))


# def pick_card_type(page, kind="Credit", secs=75):
#     sels = ["span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
#             "span.lang-en:text-is('%s Card')" % kind,
#             "*:text-is('%s Card')" % kind]
#     end = time.time() + secs
#     while time.time() < end:
#         for fr in page.frames:
#             if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#                 continue
#             for sel in sels:
#                 try:
#                     l = fr.locator(sel)
#                     if not l.count():
#                         continue
#                 except Exception:
#                     continue
#                 how = scroll_click(page, l.first)
#                 if not how:
#                     continue
#                 page.wait_for_timeout(5000)
#                 return "%s Card daba diya (%s) -- %s" % (
#                     kind, how, card_form_ready(page))
#         page.wait_for_timeout(2500)
#     return "%s Card ka option gateway ke panne par nahi mila" % kind


# def card_form_ready(page):
#     for fr in page.frames:
#         if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#             continue
#         got = card_fields(fr)
#         if got:
#             return "form aa gaya (%s)" % ", ".join(
#                 (g["id"] or g["name"] or g["ph"] or "?") for g in got[:6])
#     return "form abhi saamne nahi aaya"


# def clear_blocker(page):
#     f = sr_frame_any(page)
#     if not f:
#         return ""
#     try:
#         body = (f.locator("body").inner_text() or "").lower()
#     except Exception:
#         return ""
#     if "active session" not in body and "page isn't available" not in body:
#         return ""
#     for sel in ("button:has-text('Continue here')",
#                 "a:has-text('Continue here')",
#                 "[role=button]:has-text('Continue here')"):
#         try:
#             l = f.locator(sel)
#             if l.count():
#                 scroll_click(page, l.first)
#                 page.wait_for_timeout(8000)
#                 return "purana session ka parda hata diya (Continue here)"
#         except Exception:
#             continue
#     return "CHETAVNI: purana session ka parda hai par 'Continue here' nahi mila"


# def pick_card(page):
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     loc = None
#     used = ""
#     for _ in range(10):
#         for sel in CARD_TARGETS:
#             try:
#                 l = f.locator(sel)
#                 if l.count():
#                     loc, used = l.first, sel
#                     break
#             except Exception:
#                 continue
#         if loc:
#             break
#         page.wait_for_timeout(2000)
#     if not loc:
#         return "Credit/Debit Card ka khaana nahi mila (shayad email confirm baaki hai)"

#     before = card_state(page, f)
#     how = None
#     for _ in range(3):
#         how = scroll_click(page, loc)
#         for _ in range(6):
#             page.wait_for_timeout(1500)
#             if card_chosen(page, f, before):
#                 break
#         if card_chosen(page, f, before):
#             break
#     if not card_chosen(page, f, before):
#         return "Card daba nahi paye (%s se koshish ki, UPI hi khula raha)" % (
#             how or "kisi tareeke")

#     log("      Card chun liya (%s | %s)" % (how, used))
#     naya = card_state(page, f)["frames"] - before["frames"]
#     if naya:
#         log("      gateway ka panna khula: %s" % list(naya)[0][:90])

#     for i in range(12):
#         page.wait_for_timeout(2500)
#         cf = card_frame(page)
#         if cf:
#             return "card ke khaane khul gaye (gateway ke frame me, %ds baad)" % ((i + 1) * 2.5)
#         got = card_fields(f)
#         if got:
#             return "card ke khaane khul gaye (checkout ke frame me: %s)" % (
#                 ", ".join((g["id"] or g["name"] or g["ph"] or "?") for g in got[:6]))
#     if naya:
#         return "Card chun liya aur gateway ka panna khul gaya (agla kadam: step 10)"
#     return "Card to chun liya, par khaane abhi tak nahi aaye -- out/ ki tasveer dekhiye"


# def easebuzz_form_frame(page, secs=40):
#     end = time.time() + secs
#     while time.time() < end:
#         for fr in page.frames:
#             try:
#                 n = fr.locator(
#                     'input[name="card_number"], '
#                     'input[placeholder="Test Holder"], '
#                     'input[name="card_exp_date"], '
#                     'input[name="card_cvv"]'
#                 ).count()
#                 if n >= 1:
#                     return fr
#             except Exception:
#                 continue
#         try:
#             if page.locator('input[name="card_number"], input[name="card_cvv"]').count():
#                 return page
#         except Exception:
#             pass
#         page.wait_for_timeout(1500)
#     return None


# def _fill_one(fr, page, sels, value, label):
#     for sel in sels:
#         try:
#             loc = fr.locator(sel)
#             if not loc.count():
#                 continue
#             el = loc.first
#             try:
#                 if not el.is_visible():
#                     continue
#             except Exception:
#                 pass
#             el.scroll_into_view_if_needed(timeout=5000)
#             page.wait_for_timeout(200)
#             el.click(timeout=5000)
#             page.wait_for_timeout(150)
#             el.fill("")
#             el.type(str(value), delay=50)
#             page.wait_for_timeout(250)
#             got = ""
#             try:
#                 got = el.input_value() or ""
#             except Exception:
#                 pass
#             log("      %s fill -> '%s'" % (label, got[:28] if got else value))
#             return True
#         except Exception as e:
#             log("      %s try fail (%s): %s" % (label, sel[:40], str(e)[:50]))
#     return False


# def fill_card_details(page, number, exp, holder, cvv, click_pay=True):
#     fr = easebuzz_form_frame(page)
#     if not fr:
#         return "FAIL: card form frame nahi mila (Credit Card choose ke baad wait karo)"

#     num_clean = re.sub(r"\s+", "", number or "")
#     num_disp = " ".join(num_clean[i:i + 4] for i in range(0, len(num_clean), 4))

#     ok_n = _fill_one(fr, page, [
#         'input[name="card_number"]',
#         'input[placeholder="Test Holder"]',
#     ], num_disp, "Card Number")

#     ok_e = _fill_one(fr, page, [
#         'input[name="card_exp_date"]',
#         'input[placeholder="Test Holder"]',
#     ], exp, "MM/YY")

#     ok_h = _fill_one(fr, page, [
#         'input[placeholder="Test Holder"]',
#         'input[name^="ebz_card_holder_name"]',
#         'input[name*="card_holder" i]',
#     ], holder, "Card Holder")

#     ok_c = _fill_one(fr, page, [
#         'input[name="card_cvv"]',
#         'input[placeholder="Test Holder"]',
#     ], cvv, "CVV")

#     page.wait_for_timeout(1000)

#     pay_ok = False
#     if click_pay:
#         for scope in (fr, page):
#             for sel in (
#                 'button:has-text("Pay")',
#                 'button:has-text("Pay ₹")',
#                 'button:has-text("Pay Rs")',
#             ):
#                 try:
#                     loc = scope.locator(sel)
#                     if loc.count() and loc.first.is_visible():
#                         log("      Pay button click")
#                         scroll_click(page, loc.first)
#                         pay_ok = True
#                         page.wait_for_timeout(3000)
#                         break
#                 except Exception:
#                     continue
#             if pay_ok:
#                 break

#     return "number=%s | exp=%s | holder=%s | cvv=%s | pay=%s" % (
#         "ok" if ok_n else "FAIL",
#         "ok" if ok_e else "FAIL",
#         "ok" if ok_h else "FAIL",
#         "ok" if ok_c else "FAIL",
#         "clicked" if pay_ok else "skip",
#     )



# def wait_bank_page(context, page, secs=90):
#     """Pay ke baad ICICI / ACS / bank page (nayi window ya same)."""
#     end = time.time() + secs
#     while time.time() < end:
#         for pg in list(context.pages):
#             try:
#                 u = (pg.url or "").lower()
#                 body = ""
#                 try:
#                     body = (pg.inner_text("body") or "").lower()
#                 except Exception:
#                     pass
#                 if any(k in u for k in ("wibmo", "acs", "icici", "3ds", "bank")):
#                     if "loading bank" in body:
#                         continue
#                     return pg
#                 if "corporate id" in body or pg.locator("input#corporateId").count():
#                     return pg
#             except Exception:
#                 continue
#         page.wait_for_timeout(1500)
#     return None


# def fill_bank_corporate(context, page, corp_id, emp_id):
#     """
#     ICICI ACS form:
#       input#corporateId
#       input#employeeId
#       a.btn.primary__btn Submit
#     Phir OTP manual.
#     """
#     log("      bank page ka wait...")
#     bank = wait_bank_page(context, page, secs=90)
#     if not bank:
#         return "FAIL: bank/ACS page nahi mila (Loading Bank Page atak sakta hai)"

#     log("      bank URL: %s" % ((bank.url or "")[:100]))

#     # form load
#     for _ in range(20):
#         try:
#             if bank.locator("input#corporateId").count():
#                 break
#         except Exception:
#             pass
#         bank.wait_for_timeout(1000)
#     else:
#         return "FAIL: corporateId input nahi mila"

#     try:
#         bank.locator("input#corporateId").fill(corp_id)
#         log("      Corporate ID -> %s" % corp_id)
#     except Exception as e:
#         return "FAIL: corporateId fill: %s" % str(e)[:60]

#     bank.wait_for_timeout(800)
#     try:
#         bank.locator("input#employeeId").fill(emp_id)
#         log("      Employee ID -> %s" % emp_id)
#     except Exception as e:
#         return "FAIL: employeeId fill: %s" % str(e)[:60]

#     bank.wait_for_timeout(1500)

#     # Submit
#     submitted = False
#     for sel in (
#         'a.btn.primary__btn:has-text("Submit")',
#         'a.btn.primary__btn:has-text("SUBMIT")',
#         'a.primary__btn',
#         'a.btn.primary__btn',
#         'button:has-text("Submit")',
#         'button:has-text("SUBMIT")',
#     ):
#         try:
#             loc = bank.locator(sel)
#             if loc.count() and loc.first.is_visible():
#                 log("      Submit click: %s" % sel)
#                 try:
#                     loc.first.click()
#                 except Exception:
#                     loc.first.evaluate("e => e.click()")
#                 submitted = True
#                 bank.wait_for_timeout(4000)
#                 break
#         except Exception:
#             continue

#     if not submitted:
#         # onclick=submit()
#         try:
#             bank.evaluate("() => { if (typeof submit === 'function') submit(); }")
#             submitted = True
#             log("      Submit via JS submit()")
#             bank.wait_for_timeout(4000)
#         except Exception:
#             pass

#     if not submitted:
#         return "corp/emp filled par Submit nahi hua"

#     return "Corporate+Employee filled, Submit OK — ab OTP manual"


# def wait_for_order(page, acct, minutes=12):

#     marks = ("thank you", "order placed", "order confirmed", "order id",
#              "your order", "order number")
#     end = time.time() + minutes * 60
#     log("      order ka intezaar (%d minute tak)..." % minutes)
#     while time.time() < end:
#         page.wait_for_timeout(5000)
#         url = ""
#         txt = ""
#         for pg in list(page.context.pages):
#             try:
#                 u = pg.url or ""
#                 t = (pg.inner_text("body") or "")
#             except Exception:
#                 continue
#             if any(m in t.lower() for m in marks) or "/thank" in u or "/orders/" in u:
#                 url, txt, page = u, t, pg
#                 break
#         if not txt:
#             continue

#         ref = ""
#         m = re.search(r"(?:order\s*(?:id|no\.?|number)\s*[:#]?\s*)([A-Za-z0-9#\-]{4,})",
#                       txt, re.I)
#         if m:
#             ref = m.group(1).strip("#")
#         if not ref:
#             m = re.search(r"#(\d{4,})", txt)
#             ref = m.group(1) if m else ""

#         try:
#             page.screenshot(path=os.path.join(OUT, "order_5_confirmed.png"))
#         except Exception:
#             pass

#         row = [time.strftime("%Y-%m-%d %H:%M:%S"), acct.get("phone", ""),
#                acct.get("email", ""), ref or "(number nahi mila)", url[:120]]
#         new_file = not os.path.exists(os.path.join(HERE, "orders.csv"))
#         with open(os.path.join(HERE, "orders.csv"), "a", newline="",
#                   encoding="utf-8") as fh:
#             w = csv.writer(fh)
#             if new_file:
#                 w.writerow(["when", "phone", "email", "order_ref", "url"])
#             w.writerow(row)
#         return "ORDER LAG GAYA -- %s  (orders.csv me likh diya)" % (ref or "number nahi mila")

#     return "itne me order confirm hota nahi dikha (chhod diya, kuch bigda nahi)"


# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--product", required=True)
#     ap.add_argument("--pack", default="")
#     ap.add_argument("--unit", default="")
#     ap.add_argument("--session", default="")
#     ap.add_argument("--show", action="store_true")
#     ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
#     ap.add_argument("--card", default=DEFAULT_CARD)
#     ap.add_argument("--exp", default=DEFAULT_EXP)
#     ap.add_argument("--holder", default=DEFAULT_HOLDER)
#     ap.add_argument("--cvv", default=DEFAULT_CVV)
#     ap.add_argument("--no-pay-click", action="store_true")
#     ap.add_argument("--corp-id", default=DEFAULT_CORP_ID)
#     ap.add_argument("--emp-id", default=DEFAULT_EMP_ID)
#     ap.add_argument("--watch", type=int, default=0)
#     ap.add_argument("--hold", type=int, default=60)
#     a = ap.parse_args()

#     path = a.session or newest_session()
#     if not path:
#         log("koi session nahi mili -- pehle make_accounts.py chalao")
#         return 1
#     if not os.path.isabs(path):
#         p2 = os.path.join(SESSIONS, path)
#         path = p2 if os.path.exists(p2) else path
#     d = json.load(open(path, encoding="utf-8"))
#     log("account : %s / %s" % (d.get("phone"), d.get("email")))
#     if not d.get("address"):
#         log("CHETAVNI: is account par pata darj nahi hai -- pehle add_address.py chalao")

#     with sync_playwright() as p:
#         b = p.chromium.launch(headless=False, args=["--start-maximized"])
#         ctx = b.new_context(storage_state=d["state"], locale="en-IN",
#                             viewport={"width": 1500, "height": 950})
#         page = ctx.new_page()

#         log("\n1) product khol rahe hain: %s" % a.product)
#         page.goto("%s/products/%s" % (SHOP, a.product),
#                   wait_until="domcontentloaded", timeout=90000)
#         page.wait_for_timeout(5000)
#         for _ in range(3):
#             page.mouse.wheel(0, 900)
#             page.wait_for_timeout(700)

#         title = (page.title() or "").split("|")[0].strip()
#         log("   %s" % title)
#         before = variant_id(page)
#         log("   abhi ka variant: %s" % before)

#         if a.unit:
#             log("2) unit chun rahe hain: %s" % a.unit)
#             if not pick(page, a.unit):
#                 log("   (ye unit is panne par nahi mila -- aage badh rahe hain)")
#         if a.pack:
#             log("3) pack chun rahe hain: %s" % a.pack)
#             if not pick(page, a.pack):
#                 log("   FAIL: ye pack is panne par nahi mila")
#                 page.screenshot(path=os.path.join(OUT, "order_fail_pack.png"),
#                                 full_page=True)
#                 b.close()
#                 return 3

#         after = variant_id(page)
#         log("   chunne ke baad variant: %s%s"
#             % (after, "  (badal gaya)" if after != before else "  (wahi hai)"))
#         page.screenshot(path=os.path.join(OUT, "order_1_product.png"))

#         log("4) add to cart")
#         sel = find(page, ADD_TO_CART)
#         if not sel:
#             log("   FAIL: 'Add to cart' ka button nahi mila")
#             b.close()
#             return 4
#         page.locator(sel).first.click()
#         page.wait_for_timeout(6000)
#         page.screenshot(path=os.path.join(OUT, "order_2_added.png"))

#         cart = page.evaluate(
#             "async () => (await (await fetch('/cart.js')).json())")
#         log("   cart me cheezein: %d | kul Rs %s"
#             % (cart.get("item_count", 0), (cart.get("total_price", 0) or 0) / 100))
#         for it in cart.get("items", []):
#             log("      %s | %s | Rs %s"
#                 % (it.get("product_title"), it.get("variant_title"),
#                    (it.get("line_price", 0) or 0) / 100))
#         if not cart.get("item_count"):
#             log("   FAIL: cart khaali hi rah gaya")
#             b.close()
#             return 5
#         if after and str(cart["items"][0].get("variant_id")) != str(after):
#             log("   CHETAVNI: cart me doosra variant gaya hai (%s) -- dekh lijiye"
#                 % cart["items"][0].get("variant_id"))

#         log("5) cart")
#         if find(page, CHECKOUT):
#             log("      cart to khud hi khul gaya")
#         else:
#             sel = find(page, CART_OPEN)
#             if sel:
#                 log("      cart khol rahe hain")
#                 page.locator(sel).first.click()
#                 page.wait_for_timeout(5000)
#             else:
#                 log("      /cart panne par ja rahe hain")
#                 page.goto("%s/cart" % SHOP, wait_until="domcontentloaded",
#                           timeout=60000)
#                 page.wait_for_timeout(5000)
#         page.screenshot(path=os.path.join(OUT, "order_3_cart.png"))

#         log("6) Checkout daba rahe hain")
#         sel = find(page, CHECKOUT)
#         if not sel:
#             log("   FAIL: Checkout ka button nahi mila")
#             page.screenshot(path=os.path.join(OUT, "order_fail_checkout.png"),
#                             full_page=True)
#             b.close()
#             return 6

#         newpage = None
#         try:
#             with ctx.expect_page(timeout=15000) as np:
#                 page.locator(sel).first.click()
#             newpage = np.value
#         except Exception:
#             pass
#         pay = newpage or page
#         pay.wait_for_timeout(12000)

#         blk = clear_blocker(pay)
#         if blk:
#             log("   %s" % blk)

#         log("7) checkout ka apna pata")
#         ship = ship_address(pay, d)
#         log("      %s" % ship)
#         pay.wait_for_timeout(6000)

#         log("8) email confirm")
#         log("      %s" % confirm_email(pay, d))
#         pay.wait_for_timeout(4000)

#         st = read_checkout(pay)
#         if st:
#             log("   checkout par abhi:")
#             if st["address"]:
#                 for l in st["address"]:
#                     log("      pata: %s" % l[:90])
#             else:
#                 log("      pata: panne par koi pincode nahi dikha")
#             if st["pay"]:
#                 log("      payment ke tareeke: %s" % ", ".join(st["pay"])[:200])
#             if st["total"]:
#                 log("      panne ka aakhri daam: Rs %s" % st["total"])
#         else:
#             log("   (checkout ka frame nahi mila -- neeche ki tasveer dekhiye)")

#         log("9) Credit/Debit Card chun rahe hain")
#         log("      %s" % pick_card(pay))
#         pay.wait_for_timeout(5000)

#         log("10) gateway par %s Card chun rahe hain" % a.card_type)
#         log("      %s" % pick_card_type(pay, a.card_type))
#         pay.wait_for_timeout(3000)

#         log("11) Card details fill")
#         log("      %s" % fill_card_details(
#             pay, a.card, a.exp, a.holder, a.cvv,
#             click_pay=not a.no_pay_click,
#         ))
#         pay.wait_for_timeout(3000)

#         log("12) Bank Corporate / Employee ID")
#         log("      %s" % fill_bank_corporate(ctx, pay, a.corp_id, a.emp_id))
#         pay.wait_for_timeout(2000)

#         log("\n==========================================================")
#         log("   Bank OTP page aayi ho to OTP khud bharo.")
#         log("   OTP ke baad Enter dabao (agar --hold 0).")
#         log("==========================================================")

#         log("\n   URL: %s" % pay.url)
#         try:
#             txt = pay.inner_text("body") or ""
#         except Exception:
#             txt = ""
#         lines = [l.strip() for l in txt.splitlines() if l.strip()][:16]
#         log("   panne par: %s" % " | ".join(lines)[:260])
#         rup = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", txt)
#         log("   panne par daam: %s" % (sorted(set(rup))[:8] or "koi nahi"))
#         try:
#             pay.screenshot(path=os.path.join(OUT, "order_4_payment.png"))
#             log("   tasveer: out/order_4_payment.png")
#         except Exception as e:
#             log("   (tasveer nahi bani: %s)" % str(e)[:60])

#         log("\n==========================================================")
#         log("   CARD + CORP/EMP FILL HO GAYA. Bank OTP aap khud bhariye.")
#         log("==========================================================")
#         if a.watch:
#             log("   OTP ke baad script order ka wait karegi.")
#             log("      %s" % wait_for_order(pay, d, a.watch))
#         if a.hold == 0:
#             log("   Browser khula rahega. Kaam khatam ho to yahan Enter dabaiye.")
#             try:
#                 input()
#             except Exception:
#                 pay.wait_for_timeout(600000)
#         else:
#             log("   (%ds baad band)" % a.hold)
#             pay.wait_for_timeout(a.hold * 1000)
#         try:
#             b.close()
#         except Exception:
#             pass
#     return 0


# if __name__ == "__main__":
#     sys.exit(main())






# #!/usr/bin/env python3
# """place_order.py -- product -> cart -> checkout -> Credit Card -> fill details.

# Card fill auto; bank OTP manual.
# """
# import os
# import re
# import sys
# import glob
# import json
# import csv
# import time
# import argparse
# import socket
# import threading
# import uuid
# import subprocess
# import tempfile
# import shutil
# import asyncio
# from urllib.parse import urlparse

# from playwright.sync_api import sync_playwright

# sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# HERE = os.path.dirname(os.path.abspath(__file__))
# SESSIONS = os.path.join(HERE, "sessions")
# OUT = os.path.join(HERE, "out")
# SHOP = "https://estuaryworld.com"
# os.makedirs(OUT, exist_ok=True)

# ADD_TO_CART = ["button.add-to-cart", "button:has-text('Add to cart')"]
# CART_OPEN = ["a[data-js-sidebar-handle]", "a[title='Open cart']"]
# CHECKOUT = ["#yt-checkout-button", "button:has-text('Checkout')",
#             "a:has-text('Checkout')"]

# DEFAULT_CARD = "0000000000000000"
# DEFAULT_EXP = "01/30"
# DEFAULT_HOLDER = "Test Holder"
# DEFAULT_CVV = "000"
# DEFAULT_CORP_ID = "streakads"
# DEFAULT_EMP_ID = "CHANGE_ME_EMP_ID"
# # ================= GEONODE =================
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "proxy.geonode.io"
# GEONODE_PORT = "12000"          # Sticky port (11000 = Rotating, sticky user reject karta hai)
# GEONODE_COUNTRY = "in"



# def log(*a):
#     print(*a, flush=True)


# # ---------- Geonode SOCKS5 -> local HTTP bridge ----------
# def _free_port():
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind(("127.0.0.1", 0))
#     port = s.getsockname()[1]
#     s.close()
#     return port


# async def _socks5_connect(dst_host, dst_port, user, pw):
#     reader, writer = await asyncio.open_connection(GEONODE_HOST, int(GEONODE_PORT))
#     writer.write(b"\x05\x01\x02")
#     await writer.drain()
#     resp = await reader.readexactly(2)
#     if resp[1] != 0x02:
#         raise OSError("SOCKS5 auth method refused")
#     ub, pb = user.encode(), pw.encode()
#     writer.write(b"\x01" + bytes([len(ub)]) + ub + bytes([len(pb)]) + pb)
#     await writer.drain()
#     a = await reader.readexactly(2)
#     if a[1] != 0x00:
#         raise OSError("SOCKS5 auth failed")
#     dbytes = dst_host.encode()
#     writer.write(
#         b"\x05\x01\x00\x03" + bytes([len(dbytes)]) + dbytes + int(dst_port).to_bytes(2, "big")
#     )
#     await writer.drain()
#     r = await reader.readexactly(4)
#     if r[1] != 0x00:
#         raise OSError("SOCKS5 connect failed code=%s" % r[1])
#     atyp = r[3]
#     if atyp == 0x01:
#         await reader.readexactly(4)
#     elif atyp == 0x03:
#         ln = await reader.readexactly(1)
#         await reader.readexactly(ln[0])
#     elif atyp == 0x04:
#         await reader.readexactly(16)
#     await reader.readexactly(2)
#     return reader, writer


# async def _pipe(src, dst):
#     try:
#         while True:
#             data = await src.read(65536)
#             if not data:
#                 break
#             dst.write(data)
#             await dst.drain()
#     except Exception:
#         pass
#     finally:
#         try:
#             dst.close()
#         except Exception:
#             pass


# def start_geonode_bridge(username):
#     """Background thread: local HTTP proxy -> Geonode SOCKS5. Returns (port, stop_event)."""
#     local_port = _free_port()
#     stop = threading.Event()
#     ready = threading.Event()

#     async def run_server():
#         tasks = set()

#         async def handle(client_reader, client_writer):
#             tasks.add(asyncio.current_task())
#             up_writer = None
#             try:
#                 header = b""
#                 while b"\r\n\r\n" not in header:
#                     chunk = await client_reader.read(65536)
#                     if not chunk:
#                         return
#                     header += chunk
#                     if len(header) > 262144:
#                         return
#                 head, _, leftover = header.partition(b"\r\n\r\n")
#                 request_line = head.split(b"\r\n", 1)[0].decode("latin1")
#                 method, target, _ver = request_line.split(" ", 2)
#                 if method.upper() == "CONNECT":
#                     host, _, port = target.rpartition(":")
#                     up_reader, up_writer = await _socks5_connect(
#                         host, int(port), username, GEONODE_PASS
#                     )
#                     client_writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
#                     await client_writer.drain()
#                     if leftover:
#                         up_writer.write(leftover)
#                         await up_writer.drain()
#                 else:
#                     u = urlparse(target)
#                     host, port = u.hostname, u.port or 80
#                     up_reader, up_writer = await _socks5_connect(
#                         host, int(port), username, GEONODE_PASS
#                     )
#                     path = u.path or "/"
#                     if u.query:
#                         path += "?" + u.query
#                     rebuilt = header.replace(target.encode(), path.encode(), 1)
#                     up_writer.write(rebuilt)
#                     await up_writer.drain()
#                 await asyncio.gather(
#                     _pipe(client_reader, up_writer), _pipe(up_reader, client_writer)
#                 )
#             except Exception:
#                 try:
#                     client_writer.close()
#                 except Exception:
#                     pass
#                 if up_writer is not None:
#                     try:
#                         up_writer.close()
#                     except Exception:
#                         pass
#             finally:
#                 tasks.discard(asyncio.current_task())

#         server = await asyncio.start_server(handle, "127.0.0.1", local_port)
#         ready.set()
#         while not stop.is_set():
#             await asyncio.sleep(0.3)
#         server.close()
#         await server.wait_closed()
#         for t in list(tasks):
#             if not t.done():
#                 t.cancel()

#     def thread_main():
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         try:
#             loop.run_until_complete(run_server())
#         finally:
#             loop.close()

#     t = threading.Thread(target=thread_main, daemon=True)
#     t.start()
#     if not ready.wait(timeout=10):
#         raise RuntimeError("Geonode bridge start fail")
#     return local_port, stop


# def geonode_username(country=None, sticky=True):
#     """Geonode residential user string.
#     sticky=False: rotating IP (no session)
#     sticky=True: session-id for same IP awhile
#     """
#     c = (country or GEONODE_COUNTRY).lower()
#     base = GEONODE_USER_BASE.format(c)
#     if sticky:
#         sess = uuid.uuid4().hex[:10]
#         return "%s-session-%s-lifetime-30" % (base, sess)
#     return base



# def find_chrome_exe():
#     """Windows / common Chrome paths."""
#     candidates = [
#         os.environ.get("CHROME_PATH") or "",
#         shutil.which("chrome") or "",
#         shutil.which("google-chrome") or "",
#         r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#         r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
#         os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
#         "/usr/bin/google-chrome",
#         "/usr/bin/google-chrome-stable",
#         "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
#     ]
#     for c in candidates:
#         if c and os.path.isfile(c):
#             return c
#     return None


# def wait_port(port, timeout=25):
#     end = time.time() + timeout
#     while time.time() < end:
#         try:
#             s = socket.create_connection(("127.0.0.1", port), timeout=1)
#             s.close()
#             return True
#         except Exception:
#             time.sleep(0.3)
#     return False


# def launch_real_chrome_cdp(port=None, profile_dir=None):
#     """
#     Real Google Chrome + remote debugging.
#     Playwright connect_over_cdp se judta hai — popup bhi REAL Chrome hota hai,
#     'Chrome for Testing' nahi.
#     Returns (chrome_proc, port, profile_dir)
#     """
#     exe = find_chrome_exe()
#     if not exe:
#         raise RuntimeError(
#             "Google Chrome nahi mila. Install karo ya CHROME_PATH set karo."
#         )
#     if port is None:
#         port = _free_port()
#     if profile_dir is None:
#         profile_dir = tempfile.mkdtemp(prefix="estuary_chrome_")
#     args = [
#         exe,
#         "--remote-debugging-port=%d" % port,
#         "--user-data-dir=%s" % profile_dir,
#         "--no-first-run",
#         "--no-default-browser-check",
#         "--disable-blink-features=AutomationControlled",
#         "--disable-infobars",
#         "--start-maximized",
#         "about:blank",
#     ]
#     log("real Chrome: %s" % exe)
#     log("CDP port: %d | profile: %s" % (port, profile_dir))
#     proc = subprocess.Popen(
#         args,
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL,
#     )
#     if not wait_port(port, timeout=30):
#         try:
#             proc.terminate()
#         except Exception:
#             pass
#         raise RuntimeError("Chrome debugging port %d open nahi hua" % port)
#     return proc, port, profile_dir



# def newest_session():
#     fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
#     return fs[-1] if fs else None


# def find(scope, sels):
#     for s in sels:
#         try:
#             if scope.locator(s).count() and scope.locator(s).first.is_visible():
#                 return s
#         except Exception:
#             continue
#     return None


# def variant_id(page):
#     return page.evaluate(
#         """() => { const f = document.querySelector('form[action*="/cart/add"]');
#                    const i = f && f.querySelector('input[name="id"], select[name="id"]');
#                    return i ? String(i.value) : null; }""")


# def pick(page, value):
#     res = page.evaluate(
#         """(v) => {
#              const rs = [...document.querySelectorAll('input[type=radio]')]
#                         .filter(x => (x.value || '').trim() === v);
#              if (!rs.length) return 'nahi-mila';
#              const r = rs[0];
#              if (r.checked) return 'pehle-se-chuna';
#              r.click();
#              return 'daba-diya';
#            }""", value)
#     log("      %s" % res)
#     if res == "nahi-mila":
#         return False
#     page.wait_for_timeout(2500)
#     return True


# def sr_frame(page):
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if fr.locator("#pincode").count():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def ship_address(page, acct):
#     f = None
#     for _ in range(20):
#         f = sr_frame(page)
#         if f:
#             break
#         page.wait_for_timeout(1500)
#     if not f:
#         return "checkout ka pata wala form nahi mila (shayad pata pehle se hai)"

#     ad = acct.get("address") or {}
#     pin = ad.get("zip") or "000000"
#     first = ad.get("first_name") or "Ishan"
#     last = ad.get("last_name") or "Gupta"
#     line1 = ad.get("address1") or "55/34 Shastri Nagar"
#     line2 = ad.get("address2") or "Near Kidwai Nagar Market"
#     city = ad.get("city") or "Kanpur"
#     state = ad.get("province") or "Uttar Pradesh"
#     email = acct.get("email") or ""

#     f.locator("#pincode").fill(pin)
#     page.wait_for_timeout(4000)
#     f.locator("#name").fill(first)
#     f.locator("#lastName").fill(last)
#     f.locator("#line1").fill(line1)
#     f.locator("#line2").fill(line2)
#     for sel, val in (("#city", city), ("#state", state)):
#         try:
#             if not (f.locator(sel).input_value() or "").strip():
#                 f.locator(sel).fill(val)
#         except Exception:
#             pass
#     if email:
#         try:
#             f.locator("#email").fill(email)
#         except Exception:
#             pass

#     try:
#         f.locator("input[name='home']").first.check()
#     except Exception:
#         pass

#     got = f.locator("#addAddressBtn")
#     if not got.count():
#         return "'Add address' ka button nahi mila"

#     box = got.first.bounding_box()
#     if box:
#         page.mouse.move(box["x"] + box["width"] / 2,
#                         box["y"] + box["height"] / 2, steps=12)
#         page.wait_for_timeout(400)
#         page.mouse.down()
#         page.wait_for_timeout(90)
#         page.mouse.up()
#     else:
#         got.first.click()

#     for _ in range(6):
#         page.wait_for_timeout(4000)
#         try:
#             if "Add shipping address" not in (f.locator("body").inner_text() or ""):
#                 return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#         except Exception:
#             return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#     return "pata bhara par form abhi bhi khada hai -- dekh lijiye"


# def real_click(page, loc):
#     box = loc.bounding_box()
#     if not box:
#         loc.click()
#         return
#     page.mouse.move(box["x"] + box["width"] / 2,
#                     box["y"] + box["height"] / 2, steps=12)
#     page.wait_for_timeout(400)
#     page.mouse.down()
#     page.wait_for_timeout(90)
#     page.mouse.up()


# def confirm_email(page, acct):
#     email = acct.get("email") or ""
#     if not email:
#         return "account par email hi nahi hai"
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     for _ in range(10):
#         try:
#             body = f.locator("body").inner_text() or ""
#         except Exception:
#             return "checkout ka frame chala gaya"
#         if "onfirm your email" not in body:
#             return "email confirm karne ki zaroorat nahi thi"

#         btn = f.locator("button:has-text('Confirm email')")
#         box = f.locator("input#email:visible, input[type='email']:visible")
#         if btn.count() and box.count():
#             box.first.fill(email)
#             page.wait_for_timeout(800)
#             real_click(page, btn.first)
#             page.wait_for_timeout(6000)
#             try:
#                 if "onfirm your email" not in (f.locator("body").inner_text() or ""):
#                     return "email confirm ho gaya (%s)" % email
#             except Exception:
#                 return "email confirm ho gaya (%s)" % email
#         page.wait_for_timeout(2000)

#     try:
#         ins = f.locator("input").evaluate_all(
#             "els => els.map(e => (e.id||'-')+'/'+(e.name||'-')+'/'+(e.type||'-'))")
#     except Exception:
#         ins = []
#     return "email confirm nahi hua | frame ke input: %s" % ", ".join(ins[:10])


# def sr_frame_any(page):
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if (fr.locator("body").inner_text() or "").strip():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def read_checkout(page):
#     f = sr_frame_any(page)
#     if not f:
#         return None
#     try:
#         body = f.locator("body").inner_text() or ""
#     except Exception:
#         return None
#     out = {"address": [], "pay": [], "total": ""}

#     lines = [l.strip() for l in body.splitlines() if l.strip()]
#     for i, l in enumerate(lines):
#         if re.search(r"\b\d{6}\b", l) and len(l) > 12:
#             out["address"] = lines[max(0, i - 2):i + 3]
#             break

#     try:
#         out["pay"] = [t.strip() for t in f.locator(
#             "label, [class*='paymentMethod'], [class*='payment-method']"
#         ).all_inner_texts() if 2 < len(t.strip()) < 60][:12]
#     except Exception:
#         pass

#     m = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", body)
#     if m:
#         out["total"] = m[-1]
#     return out


# def card_frame(page):
#     for fr in page.frames:
#         u = (fr.url or "").lower()
#         if any(k in u for k in ("easebuzz", "pay.", "payment", "3ds", "acs")):
#             try:
#                 if fr.locator("input:visible").count():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def card_fields(f):
#     try:
#         return f.locator("input:visible").evaluate_all(
#             """els => els.map(e => ({id: e.id || '', name: e.name || '',
#                                      ph: e.placeholder || '',
#                                      aria: e.getAttribute('aria-label') || '',
#                                      maxlen: e.maxLength}))
#                         .filter(o => /card|number|cvv|cvc|expiry|month|year|holder/i
#                                      .test(o.id + o.name + o.ph + o.aria)
#                                   || (o.maxlen >= 3 && o.maxlen <= 19))""")
#     except Exception:
#         return []


# def in_view(page, box):
#     vp = page.viewport_size or {"width": 1500, "height": 950}
#     return bool(box) and box["y"] > 0 and box["x"] > 0 \
#         and box["y"] + box["height"] < vp["height"] \
#         and box["x"] + box["width"] < vp["width"]


# def scroll_click(page, loc, tries=3):
#     for _ in range(tries):
#         try:
#             loc.scroll_into_view_if_needed(timeout=5000)
#         except Exception:
#             pass
#         page.wait_for_timeout(600)
#         box = loc.bounding_box()
#         if in_view(page, box):
#             page.mouse.move(box["x"] + box["width"] / 2,
#                             box["y"] + box["height"] / 2, steps=12)
#             page.wait_for_timeout(300)
#             page.mouse.down()
#             page.wait_for_timeout(90)
#             page.mouse.up()
#             return "mouse"
#     try:
#         loc.click(timeout=5000)
#         return "click()"
#     except Exception:
#         pass
#     try:
#         loc.evaluate("e => e.click()")
#         return "dom-click"
#     except Exception:
#         return None


# CARD_TARGETS = [
#     "#payment-method-button-Card label.payment-button-heading",
#     "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
#     "#payment-method-button-Card",
# ]

# GATEWAY_HINTS = ("easebuzz", "eazypay", "payment", "pay.", "3ds", "acs",
#                  "razorpay", "payu", "billdesk")


# def gateway_frames(page):
#     out = set()
#     for fr in page.frames:
#         u = (fr.url or "")
#         if u and any(k in u.lower() for k in GATEWAY_HINTS):
#             out.add(u)
#     return out


# def card_state(page, f):
#     st = {"qr": False, "h": 0.0, "frames": gateway_frames(page)}
#     try:
#         st["qr"] = f.locator("#src-qrcode-payment-btn").count() > 0
#     except Exception:
#         pass
#     try:
#         st["h"] = f.locator("#payment-method-button-Card").first.evaluate(
#             "e => e.getBoundingClientRect().height") or 0.0
#     except Exception:
#         pass
#     return st


# def card_chosen(page, f, before):
#     now = card_state(page, f)
#     if now["frames"] - before["frames"]:
#         return True
#     if before["qr"] and not now["qr"]:
#         return True
#     if now["h"] > before["h"] + 30:
#         return True
#     return bool(card_fields(f))


# def pick_card_type(page, kind="Credit", secs=75):
#     sels = ["span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
#             "span.lang-en:text-is('%s Card')" % kind,
#             "*:text-is('%s Card')" % kind]
#     end = time.time() + secs
#     while time.time() < end:
#         for fr in page.frames:
#             if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#                 continue
#             for sel in sels:
#                 try:
#                     l = fr.locator(sel)
#                     if not l.count():
#                         continue
#                 except Exception:
#                     continue
#                 how = scroll_click(page, l.first)
#                 if not how:
#                     continue
#                 page.wait_for_timeout(5000)
#                 return "%s Card daba diya (%s) -- %s" % (
#                     kind, how, card_form_ready(page))
#         page.wait_for_timeout(2500)
#     return "%s Card ka option gateway ke panne par nahi mila" % kind


# def card_form_ready(page):
#     for fr in page.frames:
#         if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#             continue
#         got = card_fields(fr)
#         if got:
#             return "form aa gaya (%s)" % ", ".join(
#                 (g["id"] or g["name"] or g["ph"] or "?") for g in got[:6])
#     return "form abhi saamne nahi aaya"


# def clear_blocker(page):
#     f = sr_frame_any(page)
#     if not f:
#         return ""
#     try:
#         body = (f.locator("body").inner_text() or "").lower()
#     except Exception:
#         return ""
#     if "active session" not in body and "page isn't available" not in body:
#         return ""
#     for sel in ("button:has-text('Continue here')",
#                 "a:has-text('Continue here')",
#                 "[role=button]:has-text('Continue here')"):
#         try:
#             l = f.locator(sel)
#             if l.count():
#                 scroll_click(page, l.first)
#                 page.wait_for_timeout(8000)
#                 return "purana session ka parda hata diya (Continue here)"
#         except Exception:
#             continue
#     return "CHETAVNI: purana session ka parda hai par 'Continue here' nahi mila"


# def pick_card(page):
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     loc = None
#     used = ""
#     for _ in range(10):
#         for sel in CARD_TARGETS:
#             try:
#                 l = f.locator(sel)
#                 if l.count():
#                     loc, used = l.first, sel
#                     break
#             except Exception:
#                 continue
#         if loc:
#             break
#         page.wait_for_timeout(2000)
#     if not loc:
#         return "Credit/Debit Card ka khaana nahi mila (shayad email confirm baaki hai)"

#     before = card_state(page, f)
#     how = None
#     for _ in range(3):
#         how = scroll_click(page, loc)
#         for _ in range(6):
#             page.wait_for_timeout(1500)
#             if card_chosen(page, f, before):
#                 break
#         if card_chosen(page, f, before):
#             break
#     if not card_chosen(page, f, before):
#         return "Card daba nahi paye (%s se koshish ki, UPI hi khula raha)" % (
#             how or "kisi tareeke")

#     log("      Card chun liya (%s | %s)" % (how, used))
#     naya = card_state(page, f)["frames"] - before["frames"]
#     if naya:
#         log("      gateway ka panna khula: %s" % list(naya)[0][:90])

#     for i in range(12):
#         page.wait_for_timeout(2500)
#         cf = card_frame(page)
#         if cf:
#             return "card ke khaane khul gaye (gateway ke frame me, %ds baad)" % ((i + 1) * 2.5)
#         got = card_fields(f)
#         if got:
#             return "card ke khaane khul gaye (checkout ke frame me: %s)" % (
#                 ", ".join((g["id"] or g["name"] or g["ph"] or "?") for g in got[:6]))
#     if naya:
#         return "Card chun liya aur gateway ka panna khul gaya (agla kadam: step 10)"
#     return "Card to chun liya, par khaane abhi tak nahi aaye -- out/ ki tasveer dekhiye"


# def easebuzz_form_frame(page, secs=40):
#     end = time.time() + secs
#     while time.time() < end:
#         for fr in page.frames:
#             try:
#                 n = fr.locator(
#                     'input[name="card_number"], '
#                     'input[placeholder="Test Holder"], '
#                     'input[name="card_exp_date"], '
#                     'input[name="card_cvv"]'
#                 ).count()
#                 if n >= 1:
#                     return fr
#             except Exception:
#                 continue
#         try:
#             if page.locator('input[name="card_number"], input[name="card_cvv"]').count():
#                 return page
#         except Exception:
#             pass
#         page.wait_for_timeout(1500)
#     return None


# def _fill_one(fr, page, sels, value, label):
#     for sel in sels:
#         try:
#             loc = fr.locator(sel)
#             if not loc.count():
#                 continue
#             el = loc.first
#             try:
#                 if not el.is_visible():
#                     continue
#             except Exception:
#                 pass
#             el.scroll_into_view_if_needed(timeout=5000)
#             page.wait_for_timeout(200)
#             el.click(timeout=5000)
#             page.wait_for_timeout(150)
#             el.fill("")
#             el.type(str(value), delay=50)
#             page.wait_for_timeout(250)
#             got = ""
#             try:
#                 got = el.input_value() or ""
#             except Exception:
#                 pass
#             log("      %s fill -> '%s'" % (label, got[:28] if got else value))
#             return True
#         except Exception as e:
#             log("      %s try fail (%s): %s" % (label, sel[:40], str(e)[:50]))
#     return False


# def fill_card_details(page, number, exp, holder, cvv, click_pay=True):
#     fr = easebuzz_form_frame(page)
#     if not fr:
#         return "FAIL: card form frame nahi mila (Credit Card choose ke baad wait karo)"

#     num_clean = re.sub(r"\s+", "", number or "")
#     num_disp = " ".join(num_clean[i:i + 4] for i in range(0, len(num_clean), 4))

#     ok_n = _fill_one(fr, page, [
#         'input[name="card_number"]',
#         'input[placeholder="Test Holder"]',
#     ], num_disp, "Card Number")

#     ok_e = _fill_one(fr, page, [
#         'input[name="card_exp_date"]',
#         'input[placeholder="Test Holder"]',
#     ], exp, "MM/YY")

#     ok_h = _fill_one(fr, page, [
#         'input[placeholder="Test Holder"]',
#         'input[name^="ebz_card_holder_name"]',
#         'input[name*="card_holder" i]',
#     ], holder, "Card Holder")

#     ok_c = _fill_one(fr, page, [
#         'input[name="card_cvv"]',
#         'input[placeholder="Test Holder"]',
#     ], cvv, "CVV")

#     # human-like pause before Pay (gateway timing checks)
#     log("      Pay se pehle wait 6-8s...")
#     page.wait_for_timeout(7000)

#     pay_ok = False
#     if click_pay:
#         # catch popup/new window opened by Pay
#         bank_popup = None
#         for scope in (fr, page):
#             for sel in (
#                 'button:has-text("Pay")',
#                 'button:has-text("Pay ₹")',
#                 'button:has-text("Pay Rs")',
#             ):
#                 try:
#                     loc = scope.locator(sel)
#                     if not (loc.count() and loc.first.is_visible()):
#                         continue
#                     log("      Pay button click")
#                     try:
#                         with page.context.expect_page(timeout=20000) as pit:
#                             scroll_click(page, loc.first)
#                         bank_popup = pit.value
#                         log("      Pay ne nayi window kholi: %s" % ((bank_popup.url or "")[:80]))
#                     except Exception:
#                         scroll_click(page, loc.first)
#                     pay_ok = True
#                     page.wait_for_timeout(5000)
#                     break
#                 except Exception:
#                     continue
#             if pay_ok:
#                 break
#         if bank_popup is not None:
#             try:
#                 bank_popup.wait_for_load_state("domcontentloaded", timeout=60000)
#             except Exception:
#                 pass

#     return "number=%s | exp=%s | holder=%s | cvv=%s | pay=%s" % (
#         "ok" if ok_n else "FAIL",
#         "ok" if ok_e else "FAIL",
#         "ok" if ok_h else "FAIL",
#         "ok" if ok_c else "FAIL",
#         "clicked" if pay_ok else "skip",
#     )



# def wait_bank_page(context, page, secs=120):
#     """Pay ke baad ICICI / ACS / bank page (nayi window ya same)."""
#     end = time.time() + secs
#     loading_seen = False
#     while time.time() < end:
#         for pg in list(context.pages):
#             try:
#                 u = (pg.url or "").lower()
#                 body = ""
#                 try:
#                     body = (pg.inner_text("body") or "").lower()
#                 except Exception:
#                     pass
#                 if "loading bank" in body:
#                     loading_seen = True
#                     continue
#                 if any(k in u for k in (
#                     "wibmo", "acs", "icici", "3ds", "bank", "easebuzz",
#                     "secure-acs", "mumrdc",
#                 )):
#                     if "corporate id" in body or "employee id" in body:
#                         return pg
#                     if pg.locator("input#corporateId, input#employeeId").count():
#                         return pg
#                     # ACS URL but form not ready yet
#                     if any(k in u for k in ("wibmo", "acs", "icici")):
#                         try:
#                             pg.wait_for_timeout(2000)
#                         except Exception:
#                             pass
#                         if pg.locator("input#corporateId").count():
#                             return pg
#                 if "corporate id" in body or pg.locator("input#corporateId").count():
#                     return pg
#             except Exception:
#                 continue
#         page.wait_for_timeout(2000)
#     if loading_seen:
#         log("      (Loading Bank Page dekha, form nahi aaya — fingerprint/block ho sakta hai)")
#     return None


# def fill_bank_corporate(context, page, corp_id, emp_id):
#     """
#     ICICI ACS form:
#       input#corporateId
#       input#employeeId
#       a.btn.primary__btn Submit
#     Phir OTP manual.
#     """
#     log("      bank page ka wait...")
#     bank = wait_bank_page(context, page, secs=120)
#     if not bank:
#         return "FAIL: bank/ACS page nahi mila (Loading Bank Page atak sakta hai)"

#     log("      bank URL: %s" % ((bank.url or "")[:100]))

#     # form load
#     for _ in range(20):
#         try:
#             if bank.locator("input#corporateId").count():
#                 break
#         except Exception:
#             pass
#         bank.wait_for_timeout(1000)
#     else:
#         return "FAIL: corporateId input nahi mila"

#     try:
#         bank.locator("input#corporateId").fill(corp_id)
#         log("      Corporate ID -> %s" % corp_id)
#     except Exception as e:
#         return "FAIL: corporateId fill: %s" % str(e)[:60]

#     bank.wait_for_timeout(800)
#     try:
#         bank.locator("input#employeeId").fill(emp_id)
#         log("      Employee ID -> %s" % emp_id)
#     except Exception as e:
#         return "FAIL: employeeId fill: %s" % str(e)[:60]

#     bank.wait_for_timeout(1500)

#     # Submit
#     submitted = False
#     for sel in (
#         'a.btn.primary__btn:has-text("Submit")',
#         'a.btn.primary__btn:has-text("SUBMIT")',
#         'a.primary__btn',
#         'a.btn.primary__btn',
#         'button:has-text("Submit")',
#         'button:has-text("SUBMIT")',
#     ):
#         try:
#             loc = bank.locator(sel)
#             if loc.count() and loc.first.is_visible():
#                 log("      Submit click: %s" % sel)
#                 try:
#                     loc.first.click()
#                 except Exception:
#                     loc.first.evaluate("e => e.click()")
#                 submitted = True
#                 bank.wait_for_timeout(4000)
#                 break
#         except Exception:
#             continue

#     if not submitted:
#         # onclick=submit()
#         try:
#             bank.evaluate("() => { if (typeof submit === 'function') submit(); }")
#             submitted = True
#             log("      Submit via JS submit()")
#             bank.wait_for_timeout(4000)
#         except Exception:
#             pass

#     if not submitted:
#         return "corp/emp filled par Submit nahi hua"

#     return "Corporate+Employee filled, Submit OK — ab OTP manual"


# def wait_for_order(page, acct, minutes=12):

#     marks = ("thank you", "order placed", "order confirmed", "order id",
#              "your order", "order number")
#     end = time.time() + minutes * 60
#     log("      order ka intezaar (%d minute tak)..." % minutes)
#     while time.time() < end:
#         page.wait_for_timeout(5000)
#         url = ""
#         txt = ""
#         for pg in list(page.context.pages):
#             try:
#                 u = pg.url or ""
#                 t = (pg.inner_text("body") or "")
#             except Exception:
#                 continue
#             if any(m in t.lower() for m in marks) or "/thank" in u or "/orders/" in u:
#                 url, txt, page = u, t, pg
#                 break
#         if not txt:
#             continue

#         ref = ""
#         m = re.search(r"(?:order\s*(?:id|no\.?|number)\s*[:#]?\s*)([A-Za-z0-9#\-]{4,})",
#                       txt, re.I)
#         if m:
#             ref = m.group(1).strip("#")
#         if not ref:
#             m = re.search(r"#(\d{4,})", txt)
#             ref = m.group(1) if m else ""

#         try:
#             page.screenshot(path=os.path.join(OUT, "order_5_confirmed.png"))
#         except Exception:
#             pass

#         row = [time.strftime("%Y-%m-%d %H:%M:%S"), acct.get("phone", ""),
#                acct.get("email", ""), ref or "(number nahi mila)", url[:120]]
#         new_file = not os.path.exists(os.path.join(HERE, "orders.csv"))
#         with open(os.path.join(HERE, "orders.csv"), "a", newline="",
#                   encoding="utf-8") as fh:
#             w = csv.writer(fh)
#             if new_file:
#                 w.writerow(["when", "phone", "email", "order_ref", "url"])
#             w.writerow(row)
#         return "ORDER LAG GAYA -- %s  (orders.csv me likh diya)" % (ref or "number nahi mila")

#     return "itne me order confirm hota nahi dikha (chhod diya, kuch bigda nahi)"


# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--product", required=True)
#     ap.add_argument("--pack", default="")
#     ap.add_argument("--unit", default="")
#     ap.add_argument("--session", default="")
#     ap.add_argument("--show", action="store_true")
#     ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
#     ap.add_argument("--card", default=DEFAULT_CARD)
#     ap.add_argument("--exp", default=DEFAULT_EXP)
#     ap.add_argument("--holder", default=DEFAULT_HOLDER)
#     ap.add_argument("--cvv", default=DEFAULT_CVV)
#     ap.add_argument("--no-pay-click", action="store_true")
#     ap.add_argument("--auto-pay", action="store_true",
#                     help="Pay khud dabao (bank page fail ho sakti hai)")
#     ap.add_argument("--manual-pay", action="store_true", default=True,
#                     help="Pay tum dabao (default, bank page ke liye better)")
#     ap.add_argument("--corp-id", default=DEFAULT_CORP_ID)
#     ap.add_argument("--emp-id", default=DEFAULT_EMP_ID)
#     ap.add_argument("--watch", type=int, default=0)
#     ap.add_argument("--hold", type=int, default=60)
#     ap.add_argument("--proxy", action="store_true", default=True,
#                     help="Geonode India residential (default ON)")
#     ap.add_argument("--no-proxy", action="store_true",
#                     help="proxy band")
#     ap.add_argument("--proxy-country", default=GEONODE_COUNTRY)
#     a = ap.parse_args()

#     path = a.session or newest_session()
#     if not path:
#         log("koi session nahi mili -- pehle make_accounts.py chalao")
#         return 1
#     if not os.path.isabs(path):
#         p2 = os.path.join(SESSIONS, path)
#         path = p2 if os.path.exists(p2) else path
#     d = json.load(open(path, encoding="utf-8"))
#     log("account : %s / %s" % (d.get("phone"), d.get("email")))
#     if not d.get("address"):
#         log("CHETAVNI: is account par pata darj nahi hai -- pehle add_address.py chalao")

#     use_proxy = not a.no_proxy
#     stop_bridge = None
#     proxy_kw = {}
#     proxy_user = None
#     if use_proxy:
#         proxy_user = geonode_username(a.proxy_country, sticky=True)
#         log("proxy : Geonode country=%s | user=%s" % (a.proxy_country, proxy_user))
#         try:
#             local_port, stop_bridge = start_geonode_bridge(proxy_user)
#             proxy_kw["proxy"] = {"server": "http://127.0.0.1:%d" % local_port}
#             log("proxy : local bridge 127.0.0.1:%d" % local_port)
#         except Exception as e:
#             log("proxy FAIL (%s) -- bina proxy chalega" % e)
#             use_proxy = False
#             proxy_kw = {}

#     chrome_proc = None
#     cdp_profile = None
#     with sync_playwright() as p:
#         # --- REAL Chrome ONLY via CDP (NO Chrome for Testing fallback) ---
#         try:
#             chrome_proc, cdp_port, cdp_profile = launch_real_chrome_cdp()
#             b = p.chromium.connect_over_cdp("http://127.0.0.1:%d" % cdp_port)
#             log("browser: REAL Chrome via CDP (not Chrome for Testing)")
#             log("         agar popup me 'Chrome for Testing' dikhe to galat script chal rahi hai")
#         except Exception as e:
#             log("FAIL: Real Chrome CDP nahi khula: %s" % e)
#             log("  1) Google Chrome install karo")
#             log("  2) ya set: CHROME_PATH=C:\\Path\\to\\chrome.exe")
#             log("  Bundled Chromium (Chrome for Testing) JAAN BUJH KAR band —")
#             log("  usse bank page kabhi load nahi hoti.")
#             if stop_bridge is not None:
#                 stop_bridge.set()
#             return 2

#         # Context: CDP pe naya context + storage_state (session cookies)
#         ctx_kwargs = dict(
#             storage_state=d["state"],
#             locale="en-IN",
#             viewport={"width": 1500, "height": 950},
#             ignore_https_errors=True,
#             user_agent=(
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/124.0.0.0 Safari/537.36"
#             ),
#         )
#         if proxy_kw:
#             ctx_kwargs.update(proxy_kw)

#         try:
#             ctx = b.new_context(**ctx_kwargs)
#         except Exception as e:
#             log("new_context fail (%s) — default context + cookies inject" % e)
#             ctx = b.contexts[0] if b.contexts else b.new_context(**{k: v for k, v in ctx_kwargs.items() if k != "storage_state"})
#             # inject cookies from storage_state
#             try:
#                 st = d.get("state") or d
#                 cookies = st.get("cookies") if isinstance(st, dict) else None
#                 if cookies:
#                     ctx.add_cookies(cookies)
#             except Exception as e2:
#                 log("cookie inject: %s" % e2)

#         try:
#             ctx.add_init_script("""
#                 Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
#                 window.chrome = window.chrome || { runtime: {} };
#                 Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
#                 Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en'] });
#             """)
#         except Exception:
#             pass

#         page = ctx.new_page()

#         log("\n1) product khol rahe hain: %s" % a.product)
#         product_url = "%s/products/%s" % (SHOP, a.product)
#         nav_ok = False
#         last_err = None
#         for attempt in range(1, 4):
#             try:
#                 page.goto(product_url, wait_until="domcontentloaded", timeout=120000)
#                 nav_ok = True
#                 break
#             except Exception as e:
#                 last_err = e
#                 log("   goto fail try %d/3: %s" % (attempt, str(e)[:120]))
#                 page.wait_for_timeout(2000)
#         if not nav_ok and use_proxy:
#             # proxy se nahi chala -> bina proxy retry
#             log("   proxy se site nahi khuli -- bina proxy retry...")
#             try:
#                 if stop_bridge is not None:
#                     stop_bridge.set()
#                     stop_bridge = None
#                 ctx.close()
#             except Exception:
#                 pass
#             proxy_kw = {}
#             use_proxy = False
#             ctx = b.new_context(
#                 storage_state=d["state"],
#                 locale="en-IN",
#                 viewport={"width": 1500, "height": 950},
#                 ignore_https_errors=True,
#                 user_agent=(
#                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                     "AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/124.0.0.0 Safari/537.36"
#                 ),
#             )
#             ctx.add_init_script("""
#                 Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
#                 window.chrome = window.chrome || { runtime: {} };
#             """)
#             page = ctx.new_page()
#             try:
#                 page.goto(product_url, wait_until="domcontentloaded", timeout=120000)
#                 nav_ok = True
#                 log("   bina proxy OK (bank page baad me fail ho sakti hai)")
#             except Exception as e:
#                 last_err = e
#         if not nav_ok:
#             log("FAIL: product page nahi khuli: %s" % last_err)
#             try:
#                 b.close()
#             except Exception:
#                 pass
#             if stop_bridge is not None:
#                 stop_bridge.set()
#             return 2
#         page.wait_for_timeout(5000)
#         for _ in range(3):
#             page.mouse.wheel(0, 900)
#             page.wait_for_timeout(700)

#         title = (page.title() or "").split("|")[0].strip()
#         log("   %s" % title)
#         before = variant_id(page)
#         log("   abhi ka variant: %s" % before)

#         if a.unit:
#             log("2) unit chun rahe hain: %s" % a.unit)
#             if not pick(page, a.unit):
#                 log("   (ye unit is panne par nahi mila -- aage badh rahe hain)")
#         if a.pack:
#             log("3) pack chun rahe hain: %s" % a.pack)
#             if not pick(page, a.pack):
#                 log("   FAIL: ye pack is panne par nahi mila")
#                 page.screenshot(path=os.path.join(OUT, "order_fail_pack.png"),
#                                 full_page=True)
#                 b.close()
#                 return 3

#         after = variant_id(page)
#         log("   chunne ke baad variant: %s%s"
#             % (after, "  (badal gaya)" if after != before else "  (wahi hai)"))
#         page.screenshot(path=os.path.join(OUT, "order_1_product.png"))

#         log("4) add to cart")
#         sel = find(page, ADD_TO_CART)
#         if not sel:
#             log("   FAIL: 'Add to cart' ka button nahi mila")
#             b.close()
#             return 4
#         page.locator(sel).first.click()
#         page.wait_for_timeout(6000)
#         page.screenshot(path=os.path.join(OUT, "order_2_added.png"))

#         cart = page.evaluate(
#             "async () => (await (await fetch('/cart.js')).json())")
#         log("   cart me cheezein: %d | kul Rs %s"
#             % (cart.get("item_count", 0), (cart.get("total_price", 0) or 0) / 100))
#         for it in cart.get("items", []):
#             log("      %s | %s | Rs %s"
#                 % (it.get("product_title"), it.get("variant_title"),
#                    (it.get("line_price", 0) or 0) / 100))
#         if not cart.get("item_count"):
#             log("   FAIL: cart khaali hi rah gaya")
#             b.close()
#             return 5
#         if after and str(cart["items"][0].get("variant_id")) != str(after):
#             log("   CHETAVNI: cart me doosra variant gaya hai (%s) -- dekh lijiye"
#                 % cart["items"][0].get("variant_id"))

#         log("5) cart")
#         if find(page, CHECKOUT):
#             log("      cart to khud hi khul gaya")
#         else:
#             sel = find(page, CART_OPEN)
#             if sel:
#                 log("      cart khol rahe hain")
#                 page.locator(sel).first.click()
#                 page.wait_for_timeout(5000)
#             else:
#                 log("      /cart panne par ja rahe hain")
#                 page.goto("%s/cart" % SHOP, wait_until="domcontentloaded",
#                           timeout=60000)
#                 page.wait_for_timeout(5000)
#         page.screenshot(path=os.path.join(OUT, "order_3_cart.png"))

#         log("6) Checkout daba rahe hain")
#         sel = find(page, CHECKOUT)
#         if not sel:
#             log("   FAIL: Checkout ka button nahi mila")
#             page.screenshot(path=os.path.join(OUT, "order_fail_checkout.png"),
#                             full_page=True)
#             b.close()
#             return 6

#         newpage = None
#         try:
#             with ctx.expect_page(timeout=15000) as np:
#                 page.locator(sel).first.click()
#             newpage = np.value
#         except Exception:
#             pass
#         pay = newpage or page
#         pay.wait_for_timeout(12000)

#         blk = clear_blocker(pay)
#         if blk:
#             log("   %s" % blk)

#         log("7) checkout ka apna pata")
#         ship = ship_address(pay, d)
#         log("      %s" % ship)
#         pay.wait_for_timeout(6000)

#         log("8) email confirm")
#         log("      %s" % confirm_email(pay, d))
#         pay.wait_for_timeout(4000)

#         st = read_checkout(pay)
#         if st:
#             log("   checkout par abhi:")
#             if st["address"]:
#                 for l in st["address"]:
#                     log("      pata: %s" % l[:90])
#             else:
#                 log("      pata: panne par koi pincode nahi dikha")
#             if st["pay"]:
#                 log("      payment ke tareeke: %s" % ", ".join(st["pay"])[:200])
#             if st["total"]:
#                 log("      panne ka aakhri daam: Rs %s" % st["total"])
#         else:
#             log("   (checkout ka frame nahi mila -- neeche ki tasveer dekhiye)")

#         log("9) Credit/Debit Card chun rahe hain")
#         log("      %s" % pick_card(pay))
#         pay.wait_for_timeout(5000)

#         log("10) gateway par %s Card chun rahe hain" % a.card_type)
#         log("      %s" % pick_card_type(pay, a.card_type))
#         pay.wait_for_timeout(3000)

#         auto_pay = bool(a.auto_pay) and not a.no_pay_click
#         log("11) Card details fill (Pay auto=%s)" % auto_pay)
#         log("      %s" % fill_card_details(
#             pay, a.card, a.exp, a.holder, a.cvv,
#             click_pay=auto_pay,
#         ))

#         if not auto_pay:
#             log("\n==========================================================")
#             log("   CARD FILL HO GAYA. Ab aap MANUALLY:")
#             log("   1) Pay button dabao")
#             log("   2) Bank page load hone do (Loading Bank Page...)")
#             log("   3) Corporate ID / Employee ID bharo (ya wait for script)")
#             log("   Jab Corporate/Employee form dikhe -> yahan Enter dabao")
#             log("==========================================================")
#             try:
#                 input("👉 Bank form dikhne ke baad Enter: ")
#             except Exception:
#                 pay.wait_for_timeout(120000)
#         else:
#             pay.wait_for_timeout(8000)

#         log("12) Bank Corporate / Employee ID")
#         log("      %s" % fill_bank_corporate(ctx, pay, a.corp_id, a.emp_id))
#         pay.wait_for_timeout(2000)

#         log("\n==========================================================")
#         log("   Bank OTP page aayi ho to OTP khud bharo.")
#         log("   OTP ke baad Enter dabao (agar --hold 0).")
#         log("==========================================================")

#         log("\n   URL: %s" % pay.url)
#         try:
#             txt = pay.inner_text("body") or ""
#         except Exception:
#             txt = ""
#         lines = [l.strip() for l in txt.splitlines() if l.strip()][:16]
#         log("   panne par: %s" % " | ".join(lines)[:260])
#         rup = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", txt)
#         log("   panne par daam: %s" % (sorted(set(rup))[:8] or "koi nahi"))
#         try:
#             pay.screenshot(path=os.path.join(OUT, "order_4_payment.png"))
#             log("   tasveer: out/order_4_payment.png")
#         except Exception as e:
#             log("   (tasveer nahi bani: %s)" % str(e)[:60])

#         log("\n==========================================================")
#         log("   CARD + CORP/EMP FILL HO GAYA. Bank OTP aap khud bhariye.")
#         log("==========================================================")
#         if a.watch:
#             log("   OTP ke baad script order ka wait karegi.")
#             log("      %s" % wait_for_order(pay, d, a.watch))
#         if a.hold == 0:
#             log("   Browser khula rahega. Kaam khatam ho to yahan Enter dabaiye.")
#             try:
#                 input()
#             except Exception:
#                 pay.wait_for_timeout(600000)
#         else:
#             log("   (%ds baad band)" % a.hold)
#             pay.wait_for_timeout(a.hold * 1000)
#         try:
#             b.close()
#         except Exception:
#             pass
#         if chrome_proc is not None:
#             try:
#                 chrome_proc.terminate()
#             except Exception:
#                 pass
#         if stop_bridge is not None:
#             stop_bridge.set()
#         if cdp_profile and os.path.isdir(cdp_profile):
#             try:
#                 shutil.rmtree(cdp_profile, ignore_errors=True)
#             except Exception:
#                 pass
#     return 0


# if __name__ == "__main__":
#     sys.exit(main())


# geonode with sticky ip
# #!/usr/bin/env python3
# """place_order.py -- Estuary order automation.

#   python place_order.py --product black-white-ginger-ale --pack "Pack of 02" --hold 0 --watch 12

# Browser: REAL Google Chrome via CDP (not Chrome for Testing)
# Proxy: Geonode sticky India SOCKS5 port 12000 (verified same IP + estuaryworld 200)
# """
# import os
# import re
# import sys
# import glob
# import json
# import csv
# import time
# import argparse
# import socket
# import subprocess
# import tempfile
# import shutil
# import uuid
# import asyncio
# from urllib.parse import urlparse

# from playwright.sync_api import sync_playwright

# try:
#     sys.stdout.reconfigure(encoding="utf-8", errors="replace")
#     sys.stderr.reconfigure(encoding="utf-8", errors="replace")
# except Exception:
#     pass

# HERE = os.path.dirname(os.path.abspath(__file__))
# SESSIONS = os.path.join(HERE, "sessions")
# OUT = os.path.join(HERE, "out")
# SHOP = "https://estuaryworld.com"
# os.makedirs(OUT, exist_ok=True)

# ADD_TO_CART = ["button.add-to-cart", "button:has-text('Add to cart')"]
# CART_OPEN = ["a[data-js-sidebar-handle]", "a[title='Open cart']"]
# CHECKOUT = ["#yt-checkout-button", "button:has-text('Checkout')", "a:has-text('Checkout')"]

# # ================= GEONODE (sticky verified 2026-09-09) =================
# # Dashboard: India | SOCKS5 | Sticky | Port 12000
# # curl test: same IP twice + estuaryworld HTTP/2 200
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "proxy.geonode.io"   # France gateway (dashboard)
# GEONODE_PORT = "12000"              # STICKY (11000 = rotating)
# GEONODE_COUNTRY = "in"

# # Card defaults
# DEFAULT_CARD = "0000000000000000"
# DEFAULT_EXP = "01/30"
# DEFAULT_HOLDER = "Test Holder"
# DEFAULT_CVV = "000"
# DEFAULT_CORP = "streakads"
# DEFAULT_EMP = "CHANGE_ME_EMP_ID"


# def log(*a):
#     print(*a, flush=True)


# def newest_session():
#     fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
#     return fs[-1] if fs else None


# def find(scope, sels):
#     for s in sels:
#         try:
#             if scope.locator(s).count() and scope.locator(s).first.is_visible():
#                 return s
#         except Exception:
#             continue
#     return None


# def variant_id(page):
#     return page.evaluate(
#         """() => { const f = document.querySelector('form[action*="/cart/add"]');
#                    const i = f && f.querySelector('input[name="id"], select[name="id"]');
#                    return i ? String(i.value) : null; }""")


# def pick(page, value):
#     res = page.evaluate(
#         """(v) => {
#              const rs = [...document.querySelectorAll('input[type=radio]')]
#                         .filter(x => (x.value || '').trim() === v);
#              if (!rs.length) return 'nahi-mila';
#              const r = rs[0];
#              if (r.checked) return 'pehle-se-chuna';
#              r.click();
#              return 'daba-diya';
#            }""", value)
#     log("      %s" % res)
#     if res == "nahi-mila":
#         return False
#     page.wait_for_timeout(2500)
#     return True


# # ---------- Geonode SOCKS5 -> local HTTP bridge ----------
# _BRIDGES = []


# def _free_port():
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind(("127.0.0.1", 0))
#     port = s.getsockname()[1]
#     s.close()
#     return port


# def geonode_username(country=None, sticky=True):
#     c = (country or GEONODE_COUNTRY).lower()
#     base = GEONODE_USER_BASE.format(c)
#     if sticky:
#         sess = uuid.uuid4().hex[:10]
#         return "%s-session-%s-lifetime-30" % (base, sess)
#     return base


# async def _socks5_connect(dst_host, dst_port, user, pw):
#     reader, writer = await asyncio.open_connection(GEONODE_HOST, int(GEONODE_PORT))
#     writer.write(b"\x05\x01\x02")
#     await writer.drain()
#     resp = await reader.readexactly(2)
#     if resp[1] != 0x02:
#         raise OSError("SOCKS5 auth method refused")
#     ub, pb = user.encode(), pw.encode()
#     writer.write(b"\x01" + bytes([len(ub)]) + ub + bytes([len(pb)]) + pb)
#     await writer.drain()
#     a = await reader.readexactly(2)
#     if a[1] != 0x00:
#         raise OSError("SOCKS5 auth failed")
#     dbytes = dst_host.encode()
#     writer.write(b"\x05\x01\x00\x03" + bytes([len(dbytes)]) + dbytes + int(dst_port).to_bytes(2, "big"))
#     await writer.drain()
#     r = await reader.readexactly(4)
#     if r[1] != 0x00:
#         raise OSError("SOCKS5 connect failed code=%s" % r[1])
#     atyp = r[3]
#     if atyp == 0x01:
#         await reader.readexactly(4)
#     elif atyp == 0x03:
#         ln = await reader.readexactly(1)
#         await reader.readexactly(ln[0])
#     elif atyp == 0x04:
#         await reader.readexactly(16)
#     await reader.readexactly(2)
#     return reader, writer


# async def _pipe(src_reader, dst_writer):
#     try:
#         while True:
#             data = await src_reader.read(65536)
#             if not data:
#                 break
#             dst_writer.write(data)
#             await dst_writer.drain()
#     except Exception:
#         pass
#     finally:
#         try:
#             dst_writer.close()
#         except Exception:
#             pass


# def _make_bridge_handler(username, tasks):
#     async def handle(client_reader, client_writer):
#         tasks.add(asyncio.current_task())
#         up_writer = None
#         try:
#             header = b""
#             while b"\r\n\r\n" not in header:
#                 chunk = await client_reader.read(65536)
#                 if not chunk:
#                     return
#                 header += chunk
#                 if len(header) > 262144:
#                     return
#             head, _, leftover = header.partition(b"\r\n\r\n")
#             request_line = head.split(b"\r\n", 1)[0].decode("latin1")
#             method, target, _ver = request_line.split(" ", 2)
#             if method.upper() == "CONNECT":
#                 host, _, port = target.rpartition(":")
#                 up_reader, up_writer = await _socks5_connect(host, int(port), username, GEONODE_PASS)
#                 client_writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
#                 await client_writer.drain()
#                 if leftover:
#                     up_writer.write(leftover)
#                     await up_writer.drain()
#             else:
#                 u = urlparse(target)
#                 host = u.hostname
#                 port = u.port or 80
#                 up_reader, up_writer = await _socks5_connect(host, int(port), username, GEONODE_PASS)
#                 path = u.path or "/"
#                 if u.query:
#                     path += "?" + u.query
#                 rebuilt = header.replace(target.encode(), path.encode(), 1)
#                 up_writer.write(rebuilt)
#                 await up_writer.drain()
#             await asyncio.gather(_pipe(client_reader, up_writer), _pipe(up_reader, client_writer))
#         except Exception:
#             try:
#                 client_writer.close()
#             except Exception:
#                 pass
#             if up_writer is not None:
#                 try:
#                     up_writer.close()
#                 except Exception:
#                     pass
#         finally:
#             tasks.discard(asyncio.current_task())
#     return handle


# async def start_proxy_bridge(username):
#     local_port = _free_port()
#     tasks = set()
#     server = await asyncio.start_server(_make_bridge_handler(username, tasks), "127.0.0.1", local_port)
#     server._bridge_tasks = tasks
#     return server, local_port


# def stop_proxy_bridge_sync(server):
#     if server is None:
#         return
#     try:
#         loop = asyncio.new_event_loop()
#         async def _stop():
#             server.close()
#             await server.wait_closed()
#             for t in list(getattr(server, "_bridge_tasks", ())):
#                 if not t.done():
#                     t.cancel()
#         loop.run_until_complete(_stop())
#         loop.close()
#     except Exception:
#         pass


# def start_bridge_sync(username):
#     loop = asyncio.new_event_loop()
#     server, port = loop.run_until_complete(start_proxy_bridge(username))
#     # keep loop running bridge in background thread
#     import threading
#     def run():
#         asyncio.set_event_loop(loop)
#         loop.run_forever()
#     th = threading.Thread(target=run, daemon=True)
#     th.start()
#     return server, port, loop


# # ---------- Real Chrome CDP ----------
# def find_chrome_exe():
#     candidates = [
#         os.environ.get("CHROME_PATH") or "",
#         shutil.which("chrome") or "",
#         r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#         r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
#         os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
#         "/usr/bin/google-chrome",
#         "/usr/bin/google-chrome-stable",
#         "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
#     ]
#     for c in candidates:
#         if c and os.path.isfile(c):
#             return c
#     return None


# def wait_port(port, timeout=30):
#     end = time.time() + timeout
#     while time.time() < end:
#         try:
#             s = socket.create_connection(("127.0.0.1", port), timeout=1)
#             s.close()
#             return True
#         except Exception:
#             time.sleep(0.3)
#     return False


# def launch_real_chrome_cdp(port=None, profile_dir=None):
#     exe = find_chrome_exe()
#     if not exe:
#         raise RuntimeError("Google Chrome nahi mila. Install karo ya CHROME_PATH set karo.")
#     if port is None:
#         port = _free_port()
#     if profile_dir is None:
#         profile_dir = tempfile.mkdtemp(prefix="estuary_chrome_")
#     args = [
#         exe,
#         "--remote-debugging-port=%d" % port,
#         "--user-data-dir=%s" % profile_dir,
#         "--no-first-run",
#         "--no-default-browser-check",
#         "--disable-blink-features=AutomationControlled",
#         "--start-maximized",
#         "about:blank",
#     ]
#     log("real Chrome: %s" % exe)
#     log("CDP port: %d | profile: %s" % (port, profile_dir))
#     proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     if not wait_port(port, timeout=30):
#         try:
#             proc.terminate()
#         except Exception:
#             pass
#         raise RuntimeError("Chrome CDP port %d open nahi hua" % port)
#     return proc, port, profile_dir


# # ---------- Checkout helpers ----------
# def sr_frame(page):
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if fr.locator("#pincode").count():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def sr_frame_any(page):
#     for fr in page.frames:
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if (fr.locator("body").inner_text() or "").strip():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def real_click(page, loc):
#     box = loc.bounding_box()
#     if not box:
#         loc.click()
#         return
#     page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=12)
#     page.wait_for_timeout(400)
#     page.mouse.down()
#     page.wait_for_timeout(90)
#     page.mouse.up()


# def in_view(page, box):
#     vp = page.viewport_size or {"width": 1500, "height": 950}
#     return bool(box) and box["y"] > 0 and box["x"] > 0 \
#         and box["y"] + box["height"] < vp["height"] \
#         and box["x"] + box["width"] < vp["width"]


# def scroll_click(page, loc, tries=3):
#     for _ in range(tries):
#         try:
#             loc.scroll_into_view_if_needed(timeout=5000)
#         except Exception:
#             pass
#         page.wait_for_timeout(600)
#         box = loc.bounding_box()
#         if in_view(page, box):
#             page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=12)
#             page.wait_for_timeout(300)
#             page.mouse.down()
#             page.wait_for_timeout(90)
#             page.mouse.up()
#             return "mouse"
#     try:
#         loc.click(timeout=5000)
#         return "click()"
#     except Exception:
#         pass
#     try:
#         loc.evaluate("e => e.click()")
#         return "dom-click"
#     except Exception:
#         return None


# def ship_address(page, acct):
#     f = None
#     for _ in range(20):
#         f = sr_frame(page)
#         if f:
#             break
#         page.wait_for_timeout(1500)
#     if not f:
#         return "checkout ka pata wala form nahi mila (shayad pata pehle se hai)"

#     ad = acct.get("address") or {}
#     pin = ad.get("zip") or "000000"
#     first = ad.get("first_name") or "Ishan"
#     last = ad.get("last_name") or "Gupta"
#     line1 = ad.get("address1") or "55/34 Shastri Nagar"
#     line2 = ad.get("address2") or "Near Kidwai Nagar Market"
#     city = ad.get("city") or "Kanpur"
#     state = ad.get("province") or "Uttar Pradesh"
#     email = acct.get("email") or ""

#     f.locator("#pincode").fill(pin)
#     page.wait_for_timeout(4000)
#     f.locator("#name").fill(first)
#     f.locator("#lastName").fill(last)
#     f.locator("#line1").fill(line1)
#     f.locator("#line2").fill(line2)
#     for sel, val in (("#city", city), ("#state", state)):
#         try:
#             if not (f.locator(sel).input_value() or "").strip():
#                 f.locator(sel).fill(val)
#         except Exception:
#             pass
#     if email:
#         try:
#             f.locator("#email").fill(email)
#         except Exception:
#             pass
#     try:
#         f.locator("input[name='home']").first.check()
#     except Exception:
#         pass
#     got = f.locator("#addAddressBtn")
#     if not got.count():
#         return "'Add address' ka button nahi mila"
#     box = got.first.bounding_box()
#     if box:
#         page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=12)
#         page.wait_for_timeout(400)
#         page.mouse.down()
#         page.wait_for_timeout(90)
#         page.mouse.up()
#     else:
#         got.first.click()
#     for _ in range(6):
#         page.wait_for_timeout(4000)
#         try:
#             if "Add shipping address" not in (f.locator("body").inner_text() or ""):
#                 return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#         except Exception:
#             return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#     return "pata bhara par form abhi bhi khada hai"


# def confirm_email(page, acct):
#     email = acct.get("email") or ""
#     if not email:
#         return "account par email hi nahi hai"
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"
#     for _ in range(10):
#         try:
#             body = f.locator("body").inner_text() or ""
#         except Exception:
#             return "checkout ka frame chala gaya"
#         if "onfirm your email" not in body:
#             return "email confirm karne ki zaroorat nahi thi"
#         btn = f.locator("button:has-text('Confirm email')")
#         box = f.locator("input#email:visible, input[type='email']:visible")
#         if btn.count() and box.count():
#             box.first.fill(email)
#             page.wait_for_timeout(800)
#             real_click(page, btn.first)
#             page.wait_for_timeout(6000)
#             try:
#                 if "onfirm your email" not in (f.locator("body").inner_text() or ""):
#                     return "email confirm ho gaya (%s)" % email
#             except Exception:
#                 return "email confirm ho gaya (%s)" % email
#         page.wait_for_timeout(2000)
#     return "email confirm nahi hua"


# def clear_blocker(page):
#     f = sr_frame_any(page)
#     if not f:
#         return ""
#     try:
#         body = (f.locator("body").inner_text() or "").lower()
#     except Exception:
#         return ""
#     if "active session" not in body and "page isn't available" not in body:
#         return ""
#     for sel in ("button:has-text('Continue here')", "a:has-text('Continue here')"):
#         try:
#             l = f.locator(sel)
#             if l.count():
#                 scroll_click(page, l.first)
#                 page.wait_for_timeout(8000)
#                 return "purana session ka parda hata diya"
#         except Exception:
#             continue
#     return "CHETAVNI: active session parda hai"


# def read_checkout(page):
#     f = sr_frame_any(page)
#     if not f:
#         return None
#     try:
#         body = f.locator("body").inner_text() or ""
#     except Exception:
#         return None
#     out = {"address": [], "pay": [], "total": ""}
#     lines = [l.strip() for l in body.splitlines() if l.strip()]
#     for i, l in enumerate(lines):
#         if re.search(r"\b\d{6}\b", l) and len(l) > 12:
#             out["address"] = lines[max(0, i - 2):i + 3]
#             break
#     try:
#         out["pay"] = [t.strip() for t in f.locator(
#             "label, [class*='paymentMethod'], [class*='payment-method']"
#         ).all_inner_texts() if 2 < len(t.strip()) < 60][:12]
#     except Exception:
#         pass
#     m = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", body)
#     if m:
#         out["total"] = m[-1]
#     return out


# GATEWAY_HINTS = ("easebuzz", "eazypay", "payment", "pay.", "3ds", "acs",
#                  "razorpay", "payu", "billdesk", "wibmo")

# CARD_TARGETS = [
#     "#payment-method-button-Card label.payment-button-heading",
#     "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
#     "#payment-method-button-Card",
# ]


# def gateway_frames(page):
#     out = set()
#     for fr in page.frames:
#         u = (fr.url or "")
#         if u and any(k in u.lower() for k in GATEWAY_HINTS):
#             out.add(u)
#     return out


# def card_fields(f):
#     try:
#         return f.locator("input:visible").evaluate_all(
#             """els => els.map(e => ({id: e.id || '', name: e.name || '',
#                                      ph: e.placeholder || '',
#                                      aria: e.getAttribute('aria-label') || '',
#                                      maxlen: e.maxLength}))
#                         .filter(o => /card|number|cvv|cvc|expiry|month|year|holder/i
#                                      .test(o.id + o.name + o.ph + o.aria)
#                                   || (o.maxlen >= 3 && o.maxlen <= 19))""")
#     except Exception:
#         return []


# def card_state(page, f):
#     st = {"qr": False, "h": 0.0, "frames": gateway_frames(page)}
#     try:
#         st["qr"] = f.locator("#src-qrcode-payment-btn").count() > 0
#     except Exception:
#         pass
#     try:
#         st["h"] = f.locator("#payment-method-button-Card").first.evaluate(
#             "e => e.getBoundingClientRect().height") or 0.0
#     except Exception:
#         pass
#     return st


# def card_chosen(page, f, before):
#     now = card_state(page, f)
#     if now["frames"] - before["frames"]:
#         return True
#     if before["qr"] and not now["qr"]:
#         return True
#     if now["h"] > before["h"] + 30:
#         return True
#     return bool(card_fields(f))


# def card_form_ready(page):
#     for fr in page.frames:
#         if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#             continue
#         got = card_fields(fr)
#         if got:
#             return "form aa gaya (%s)" % ", ".join(
#                 (g["id"] or g["name"] or g["ph"] or "?") for g in got[:6])
#     return "form abhi saamne nahi aaya"


# def pick_card(page):
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"
#     loc = None
#     used = ""
#     for _ in range(10):
#         for sel in CARD_TARGETS:
#             try:
#                 l = f.locator(sel)
#                 if l.count():
#                     loc, used = l.first, sel
#                     break
#             except Exception:
#                 continue
#         if loc:
#             break
#         page.wait_for_timeout(2000)
#     if not loc:
#         return "Credit/Debit Card ka khaana nahi mila"
#     before = card_state(page, f)
#     how = None
#     for _ in range(3):
#         how = scroll_click(page, loc)
#         for _ in range(6):
#             page.wait_for_timeout(1500)
#             if card_chosen(page, f, before):
#                 break
#         if card_chosen(page, f, before):
#             break
#     if not card_chosen(page, f, before):
#         return "Card daba nahi paye (%s)" % (how or "?")
#     log("      Card chun liya (%s | %s)" % (how, used))
#     naya = card_state(page, f)["frames"] - before["frames"]
#     if naya:
#         log("      gateway ka panna khula: %s" % list(naya)[0][:90])
#         return "Card chun liya aur gateway ka panna khul gaya (agla kadam: step 10)"
#     for i in range(12):
#         page.wait_for_timeout(2500)
#         got = card_fields(f)
#         if got:
#             return "card ke khaane khul gaye"
#     return "Card chun liya, form wait..."


# def pick_card_type(page, kind="Credit", secs=75):
#     sels = [
#         "span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
#         "span.lang-en:text-is('%s Card')" % kind,
#         "*:text-is('%s Card')" % kind,
#     ]
#     end = time.time() + secs
#     while time.time() < end:
#         for fr in page.frames:
#             if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#                 continue
#             for sel in sels:
#                 try:
#                     l = fr.locator(sel)
#                     if not l.count():
#                         continue
#                 except Exception:
#                     continue
#                 how = scroll_click(page, l.first)
#                 if not how:
#                     continue
#                 page.wait_for_timeout(5000)
#                 return "%s Card daba diya (%s) -- %s" % (kind, how, card_form_ready(page))
#         page.wait_for_timeout(2500)
#     return "%s Card option nahi mila" % kind


# def fill_card_details(page, number, exp, holder, cvv, do_pay=False):
#     """Easebuzz iframe: card_number, card_exp_date, holder, card_cvv."""
#     target = None
#     for _ in range(20):
#         for fr in page.frames:
#             try:
#                 if fr.locator('input[name="card_number"], input[placeholder="Test Holder"]').count():
#                     target = fr
#                     break
#             except Exception:
#                 continue
#         if target:
#             break
#         page.wait_for_timeout(1500)
#     if not target:
#         # also search all pages
#         for pg in page.context.pages:
#             for fr in pg.frames:
#                 try:
#                     if fr.locator('input[name="card_number"], input[placeholder="Test Holder"]').count():
#                         target = fr
#                         page = pg
#                         break
#                 except Exception:
#                     continue
#             if target:
#                 break
#     if not target:
#         return "card form frame nahi mila"

#     def _fill(sel_list, val, label):
#         for sel in sel_list:
#             try:
#                 loc = target.locator(sel)
#                 if loc.count():
#                     loc.first.click(timeout=3000)
#                     loc.first.fill("")
#                     loc.first.type(val, delay=40)
#                     log("      %s fill -> '%s'" % (label, val))
#                     return True
#             except Exception as e:
#                 log("      %s try fail: %s" % (label, str(e)[:60]))
#         log("      %s FAIL" % label)
#         return False

#     num = re.sub(r"\s+", "", number)
#     # spaced display optional
#     num_disp = " ".join([num[i:i+4] for i in range(0, len(num), 4)]) if len(num) == 16 else num
#     ok_n = _fill(['input[name="card_number"]', 'input[placeholder="Test Holder"]'], num_disp, "Card Number")
#     page.wait_for_timeout(500)
#     ok_e = _fill(['input[name="card_exp_date"]', 'input[placeholder="Test Holder"]'], exp, "MM/YY")
#     page.wait_for_timeout(400)
#     ok_h = _fill(['input[placeholder="Test Holder"]', 'input[name*="card_holder"]'], holder, "Card Holder")
#     page.wait_for_timeout(400)
#     ok_c = _fill(['input[name="card_cvv"]', 'input[placeholder="Test Holder"]'], cvv, "CVV")
#     page.wait_for_timeout(1500)

#     pay_status = "skip"
#     if do_pay:
#         log("      Pay se pehle wait 6-8s...")
#         page.wait_for_timeout(7000)
#         for sel in ('button:has-text("Pay")', 'button:has-text("PAY")', '[class*="pay"] button'):
#             try:
#                 btn = target.locator(sel)
#                 if btn.count():
#                     scroll_click(page, btn.first)
#                     pay_status = "clicked"
#                     break
#             except Exception:
#                 continue
#         page.wait_for_timeout(3000)

#     return "number=%s | exp=%s | holder=%s | cvv=%s | pay=%s" % (
#         "ok" if ok_n else "FAIL", "ok" if ok_e else "FAIL",
#         "ok" if ok_h else "FAIL", "ok" if ok_c else "FAIL", pay_status)


# def fill_corporate(page, corp_id, emp_id, timeout_sec=120):
#     """ICICI / Wibmo: corporateId + employeeId + Submit."""
#     log("      bank page ka wait...")
#     end = time.time() + timeout_sec
#     target = None
#     while time.time() < end:
#         for pg in page.context.pages:
#             for fr in ([pg.main_frame] + list(pg.frames)):
#                 try:
#                     if fr.locator("input#corporateId, input[name='corporateId']").count():
#                         target = fr
#                         page = pg
#                         break
#                 except Exception:
#                     continue
#             if target:
#                 break
#         if target:
#             break
#         # loading text
#         for pg in page.context.pages:
#             try:
#                 t = (pg.title() or "") + " " + (pg.inner_text("body") or "")[:200]
#                 if "Loading Bank" in t or "Authenticate" in t:
#                     log("      still loading / auth page...")
#             except Exception:
#                 pass
#         page.wait_for_timeout(2000)

#     if not target:
#         return "Corporate form %ds me nahi aaya (Loading Bank atka ho sakta hai)" % timeout_sec

#     try:
#         target.locator("input#corporateId, input[name='corporateId']").first.fill(corp_id)
#         log("      Corporate ID -> %s" % corp_id)
#         page.wait_for_timeout(800)
#         target.locator("input#employeeId, input[name='employeeId']").first.fill(emp_id)
#         log("      Employee ID -> %s" % emp_id)
#         page.wait_for_timeout(1500)
#         btn = target.locator("a.btn.primary__btn:has-text('Submit'), a.primary__btn, a.btn.primary__btn")
#         if btn.count():
#             scroll_click(page, btn.first)
#             log("      Submit click")
#         else:
#             target.evaluate("() => { const a=[...document.querySelectorAll('a')].find(x=>/submit/i.test(x.textContent)); if(a) a.click(); }")
#             log("      Submit JS click")
#         page.wait_for_timeout(5000)
#         return "Corporate/Employee fill + Submit OK"
#     except Exception as e:
#         return "Corporate fill error: %s" % str(e)[:80]


# def wait_for_order(page, acct, minutes=12):
#     marks = ("thank you", "order placed", "order confirmed", "order id",
#              "your order", "order number")
#     end = time.time() + minutes * 60
#     log("      order ka intezaar (%d minute tak)..." % minutes)
#     while time.time() < end:
#         page.wait_for_timeout(5000)
#         url, txt = "", ""
#         for pg in list(page.context.pages):
#             try:
#                 u = pg.url or ""
#                 t = (pg.inner_text("body") or "")
#             except Exception:
#                 continue
#             if any(m in t.lower() for m in marks) or "/thank" in u or "/orders/" in u:
#                 url, txt, page = u, t, pg
#                 break
#         if not txt:
#             continue
#         ref = ""
#         m = re.search(r"(?:order\s*(?:id|no\.?|number)\s*[:#]?\s*)([A-Za-z0-9#\-]{4,})", txt, re.I)
#         if m:
#             ref = m.group(1).strip("#")
#         if not ref:
#             m = re.search(r"#(\d{4,})", txt)
#             ref = m.group(1) if m else ""
#         try:
#             page.screenshot(path=os.path.join(OUT, "order_5_confirmed.png"))
#         except Exception:
#             pass
#         row = [time.strftime("%Y-%m-%d %H:%M:%S"), acct.get("phone", ""),
#                acct.get("email", ""), ref or "(number nahi mila)", url[:120]]
#         new_file = not os.path.exists(os.path.join(HERE, "orders.csv"))
#         with open(os.path.join(HERE, "orders.csv"), "a", newline="", encoding="utf-8") as fh:
#             w = csv.writer(fh)
#             if new_file:
#                 w.writerow(["when", "phone", "email", "order_ref", "url"])
#             w.writerow(row)
#         return "ORDER LAG GAYA -- %s (orders.csv)" % (ref or "number nahi mila")
#     return "order confirm timeout"


# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--product", required=True)
#     ap.add_argument("--pack", default="")
#     ap.add_argument("--unit", default="")
#     ap.add_argument("--session", default="")
#     ap.add_argument("--card", default=DEFAULT_CARD)
#     ap.add_argument("--exp", default=DEFAULT_EXP)
#     ap.add_argument("--holder", default=DEFAULT_HOLDER)
#     ap.add_argument("--cvv", default=DEFAULT_CVV)
#     ap.add_argument("--corp-id", default=DEFAULT_CORP)
#     ap.add_argument("--emp-id", default=DEFAULT_EMP)
#     ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
#     ap.add_argument("--auto-pay", action="store_true", help="Pay auto click (default: manual Pay)")
#     ap.add_argument("--no-proxy", action="store_true")
#     ap.add_argument("--proxy-country", default=GEONODE_COUNTRY)
#     ap.add_argument("--watch", type=int, default=0)
#     ap.add_argument("--hold", type=int, default=60)
#     a = ap.parse_args()

#     path = a.session or newest_session()
#     if not path:
#         log("koi session nahi -- sessions/*.json chahiye")
#         return 1
#     if not os.path.isabs(path):
#         p2 = os.path.join(SESSIONS, path)
#         path = p2 if os.path.exists(p2) else path
#     d = json.load(open(path, encoding="utf-8"))
#     log("account : %s / %s" % (d.get("phone"), d.get("email")))

#     bridge_server = None
#     bridge_loop = None
#     chrome_proc = None
#     proxy_cfg = None

#     if not a.no_proxy:
#         user = geonode_username(a.proxy_country, sticky=True)
#         log("proxy : Geonode country=%s | user=%s" % (a.proxy_country, user))
#         log("proxy : host=%s port=%s (STICKY)" % (GEONODE_HOST, GEONODE_PORT))
#         try:
#             bridge_server, local_port, bridge_loop = start_bridge_sync(user)
#             proxy_cfg = {"server": "http://127.0.0.1:%d" % local_port}
#             log("proxy : local bridge 127.0.0.1:%d" % local_port)
#         except Exception as e:
#             log("proxy bridge fail: %s -- bina proxy" % e)
#             proxy_cfg = None
#     else:
#         log("proxy : OFF")

#     with sync_playwright() as p:
#         try:
#             chrome_proc, cdp_port, cdp_profile = launch_real_chrome_cdp()
#             b = p.chromium.connect_over_cdp("http://127.0.0.1:%d" % cdp_port)
#             log("browser: REAL Chrome via CDP (not Chrome for Testing)")
#         except Exception as e:
#             log("FAIL: Real Chrome nahi khula: %s" % e)
#             return 2

#         ctx_kwargs = {
#             "storage_state": d["state"],
#             "locale": "en-IN",
#             "viewport": {"width": 1500, "height": 950},
#             "ignore_https_errors": True,
#         }
#         if proxy_cfg:
#             ctx_kwargs["proxy"] = proxy_cfg
#         ctx = b.new_context(**ctx_kwargs)
#         ctx.add_init_script("""
#             Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
#             window.chrome = window.chrome || { runtime: {} };
#         """)
#         page = ctx.new_page()

#         log("\n1) product khol rahe hain: %s" % a.product)
#         url = "%s/products/%s" % (SHOP, a.product)
#         opened = False
#         for attempt in range(1, 4):
#             try:
#                 page.goto(url, wait_until="domcontentloaded", timeout=120000)
#                 opened = True
#                 break
#             except Exception as e:
#                 log("   goto fail try %d/3: %s" % (attempt, str(e).split("\n")[0][:120]))
#                 page.wait_for_timeout(2000)
#         if not opened and proxy_cfg:
#             log("   proxy se site nahi khuli -- bina proxy retry...")
#             try:
#                 page.close()
#             except Exception:
#                 pass
#             ctx2 = b.new_context(
#                 storage_state=d["state"], locale="en-IN",
#                 viewport={"width": 1500, "height": 950}, ignore_https_errors=True)
#             ctx2.add_init_script("""
#                 Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
#             """)
#             page = ctx2.new_page()
#             try:
#                 page.goto(url, wait_until="domcontentloaded", timeout=120000)
#                 opened = True
#                 log("   bina proxy OK")
#             except Exception as e:
#                 log("   bina proxy bhi fail: %s" % e)
#                 return 3
#         if not opened:
#             log("   product page open fail")
#             return 3

#         page.wait_for_timeout(4000)
#         for _ in range(3):
#             page.mouse.wheel(0, 900)
#             page.wait_for_timeout(500)

#         title = (page.title() or "").split("|")[0].strip()
#         log("   %s" % title)
#         before = variant_id(page)
#         log("   abhi ka variant: %s" % before)

#         if a.unit:
#             log("2) unit: %s" % a.unit)
#             pick(page, a.unit)
#         if a.pack:
#             log("3) pack: %s" % a.pack)
#             if not pick(page, a.pack):
#                 log("   FAIL pack")
#                 return 3
#         after = variant_id(page)
#         log("   variant after: %s" % after)
#         page.screenshot(path=os.path.join(OUT, "order_1_product.png"))

#         log("4) add to cart")
#         sel = find(page, ADD_TO_CART)
#         if not sel:
#             log("   FAIL add to cart")
#             return 4
#         page.locator(sel).first.click()
#         page.wait_for_timeout(6000)
#         cart = page.evaluate("async () => (await (await fetch('/cart.js')).json())")
#         log("   cart items: %d | Rs %s" % (
#             cart.get("item_count", 0), (cart.get("total_price", 0) or 0) / 100))
#         if not cart.get("item_count"):
#             log("   FAIL empty cart")
#             return 5

#         log("5) cart")
#         if not find(page, CHECKOUT):
#             sel = find(page, CART_OPEN)
#             if sel:
#                 page.locator(sel).first.click()
#                 page.wait_for_timeout(4000)
#             else:
#                 page.goto("%s/cart" % SHOP, wait_until="domcontentloaded", timeout=60000)
#                 page.wait_for_timeout(4000)
#         else:
#             log("      cart pehle se open")

#         log("6) Checkout")
#         sel = find(page, CHECKOUT)
#         if not sel:
#             log("   FAIL checkout button")
#             return 6
#         newpage = None
#         try:
#             with page.context.expect_page(timeout=15000) as np:
#                 page.locator(sel).first.click()
#             newpage = np.value
#         except Exception:
#             try:
#                 page.locator(sel).first.click()
#             except Exception:
#                 pass
#         pay = newpage or page
#         pay.wait_for_timeout(10000)

#         blk = clear_blocker(pay)
#         if blk:
#             log("   %s" % blk)

#         log("7) address")
#         log("      %s" % ship_address(pay, d))
#         pay.wait_for_timeout(4000)

#         log("8) email confirm")
#         log("      %s" % confirm_email(pay, d))
#         pay.wait_for_timeout(3000)

#         st = read_checkout(pay)
#         if st:
#             log("   checkout:")
#             for l in (st.get("address") or [])[:5]:
#                 log("      pata: %s" % l[:90])
#             if st.get("pay"):
#                 log("      pay methods: %s" % ", ".join(st["pay"])[:180])
#             if st.get("total"):
#                 log("      total: Rs %s" % st["total"])

#         log("9) Credit/Debit Card")
#         log("      %s" % pick_card(pay))
#         pay.wait_for_timeout(4000)

#         log("10) gateway %s Card" % a.card_type)
#         log("      %s" % pick_card_type(pay, a.card_type))
#         pay.wait_for_timeout(3000)

#         log("11) Card details fill (Pay auto=%s)" % a.auto_pay)
#         log("      %s" % fill_card_details(
#             pay, a.card, a.exp, a.holder, a.cvv, do_pay=a.auto_pay))

#         if not a.auto_pay:
#             log("\n==========================================================")
#             log("   CARD FILL HO GAYA. Ab MANUALLY:")
#             log("   1) Pay button dabao")
#             log("   2) Bank page load hone do")
#             log("   3) Jab Corporate/Employee form dikhe -> yahan Enter")
#             log("==========================================================")
#             try:
#                 input("👉 Bank form dikhne ke baad Enter: ")
#             except Exception:
#                 pay.wait_for_timeout(60000)

#         log("12) Bank Corporate / Employee ID")
#         log("      %s" % fill_corporate(pay, a.corp_id, a.emp_id, timeout_sec=120))

#         log("\n==========================================================")
#         log("   OTP manual. Browser Enter tak open.")
#         log("==========================================================")

#         try:
#             pay.screenshot(path=os.path.join(OUT, "order_4_payment.png"))
#         except Exception:
#             pass

#         if a.watch:
#             log("      %s" % wait_for_order(pay, d, a.watch))

#         if a.hold == 0:
#             try:
#                 input("👉 Band karne ke liye Enter: ")
#             except Exception:
#                 pay.wait_for_timeout(600000)
#         else:
#             pay.wait_for_timeout(a.hold * 1000)

#         try:
#             b.close()
#         except Exception:
#             pass
#         if chrome_proc is not None:
#             try:
#                 chrome_proc.terminate()
#             except Exception:
#                 pass

#     if bridge_loop is not None:
#         try:
#             bridge_loop.call_soon_threadsafe(bridge_loop.stop)
#         except Exception:
#             pass
#     return 0


# if __name__ == "__main__":
#     sys.exit(main())


# geonode with rotating ip
#!/usr/bin/env python3
# """place_order.py -- product -> cart -> checkout -> Credit Card -> fill details.

# # Card fill auto; bank OTP manual.
# # """
import os
import re
import sys
import glob
import json
import csv
import time
import argparse
import socket
import threading
import uuid
import subprocess
import tempfile
import shutil
import asyncio
import requests
from urllib.parse import urlparse

import order_plan          # links -> cart, sheet -> pata/card

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

# Windowed exe (bina console wali) me sys.stdout ya to None hota hai, ya koi
# nakli likhne wali cheez jisme reconfigure jaisa kuch hota hi nahi. Aisi
# haalat me ye ek line poore import ko gira deti thi -- exe khulte hi
# "AttributeError: '_Sink' object has no attribute 'reconfigure'".
# Encoding set karna sirf console par sundar dikhne ke liye hai; na ho paye to
# kuch bigadta nahi. Isliye koshish karo aur aage badh jao.
for _dhara in ("stdout", "stderr"):
    try:
        getattr(sys, _dhara).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# exe bana kar chalane par __file__ ek temp folder hota hai jo band hote hi mit
# jaata hai -- sessions aur CSV wahan chale gaye to har run ke baad gayab. Isliye
# frozen (exe) me sab kuch EXE KE BAGAL me rakha jaata hai.
FROZEN = bool(getattr(sys, "frozen", False))
HERE = (os.path.dirname(sys.executable) if FROZEN
        else os.path.dirname(os.path.abspath(__file__)))
# PyInstaller jo cheezein exe ke andar rakhta hai (geckodriver, credentials)
# unka temp folder -- sirf padhne ke liye.
BUNDLE = getattr(sys, "_MEIPASS", HERE)

# Sessions kahan hain? Aam taur par exe/script ke bagal me. Par yahan teen
# alag exe hain -- do account banati hain aur ek order lagati hai -- aur unke
# folder alag hote hain. Order wali exe ko un accounts tak pahunchna hota hai
# jo doosri exe ne banaye. Isliye raasta bahar se bhi diya ja sakta hai.
SESSIONS = (os.environ.get("ESTUARY_SESSIONS")
            or os.path.join(HERE, "sessions"))
OUT = os.path.join(HERE, "out")
SHOP = "https://estuaryworld.com"
os.makedirs(OUT, exist_ok=True)
os.makedirs(SESSIONS, exist_ok=True)

ADD_TO_CART = ["button.add-to-cart", "button:has-text('Add to cart')"]
CART_OPEN = ["a[data-js-sidebar-handle]", "a[title='Open cart']"]
CHECKOUT = ["#yt-checkout-button", "button:has-text('Checkout')",
            "a:has-text('Checkout')"]

DEFAULT_CARD = "0000000000000000"
DEFAULT_EXP = "01/30"
DEFAULT_HOLDER = "Test Holder"
DEFAULT_CVV = "000"
DEFAULT_CORP_ID = "streakads"
DEFAULT_EMP_ID = "CHANGE_ME_EMP_ID"
# ================= GEONODE (ROTATING SOCKS5) =================
# Dashboard: India + SOCKS5 + Rotating + Port 11000
# Sticky (12000) mat use — rotating jaise pehle chal raha tha.
GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
GEONODE_PASS = "CHANGE_ME_SECRET"
GEONODE_HOST = "sg.proxy.geonode.io"   # Singapore gateway (rotating)
GEONODE_PORT = "11000"                 # ROTATING SOCKS5 (12000 = sticky)
GEONODE_COUNTRY = "in"




def log(*a):
    print(*a, flush=True)


# ---------- Geonode SOCKS5 -> local HTTP bridge ----------
def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


async def _socks5_connect(dst_host, dst_port, user, pw):
    reader, writer = await asyncio.open_connection(GEONODE_HOST, int(GEONODE_PORT))
    writer.write(b"\x05\x01\x02")
    await writer.drain()
    resp = await reader.readexactly(2)
    if resp[1] != 0x02:
        raise OSError("SOCKS5 auth method refused")
    ub, pb = user.encode(), pw.encode()
    writer.write(b"\x01" + bytes([len(ub)]) + ub + bytes([len(pb)]) + pb)
    await writer.drain()
    a = await reader.readexactly(2)
    if a[1] != 0x00:
        raise OSError("SOCKS5 auth failed")
    dbytes = dst_host.encode()
    writer.write(
        b"\x05\x01\x00\x03" + bytes([len(dbytes)]) + dbytes + int(dst_port).to_bytes(2, "big")
    )
    await writer.drain()
    r = await reader.readexactly(4)
    if r[1] != 0x00:
        raise OSError("SOCKS5 connect failed code=%s" % r[1])
    atyp = r[3]
    if atyp == 0x01:
        await reader.readexactly(4)
    elif atyp == 0x03:
        ln = await reader.readexactly(1)
        await reader.readexactly(ln[0])
    elif atyp == 0x04:
        await reader.readexactly(16)
    await reader.readexactly(2)
    return reader, writer


async def _pipe(src, dst):
    try:
        while True:
            data = await src.read(65536)
            if not data:
                break
            dst.write(data)
            await dst.drain()
    except Exception:
        pass
    finally:
        try:
            dst.close()
        except Exception:
            pass


def start_geonode_bridge(username):
    """Background thread: local HTTP proxy -> Geonode SOCKS5. Returns (port, stop_event)."""
    local_port = _free_port()
    stop = threading.Event()
    ready = threading.Event()

    async def run_server():
        tasks = set()

        async def handle(client_reader, client_writer):
            tasks.add(asyncio.current_task())
            up_writer = None
            try:
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
                    up_reader, up_writer = await _socks5_connect(
                        host, int(port), username, GEONODE_PASS
                    )
                    client_writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
                    await client_writer.drain()
                    if leftover:
                        up_writer.write(leftover)
                        await up_writer.drain()
                else:
                    u = urlparse(target)
                    host, port = u.hostname, u.port or 80
                    up_reader, up_writer = await _socks5_connect(
                        host, int(port), username, GEONODE_PASS
                    )
                    path = u.path or "/"
                    if u.query:
                        path += "?" + u.query
                    rebuilt = header.replace(target.encode(), path.encode(), 1)
                    up_writer.write(rebuilt)
                    await up_writer.drain()
                await asyncio.gather(
                    _pipe(client_reader, up_writer), _pipe(up_reader, client_writer)
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

        server = await asyncio.start_server(handle, "127.0.0.1", local_port)
        ready.set()
        while not stop.is_set():
            await asyncio.sleep(0.3)
        server.close()
        await server.wait_closed()
        for t in list(tasks):
            if not t.done():
                t.cancel()

    def thread_main():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_server())
        finally:
            loop.close()

    t = threading.Thread(target=thread_main, daemon=True)
    t.start()
    if not ready.wait(timeout=10):
        raise RuntimeError("Geonode bridge start fail")
    return local_port, stop


def geonode_username(country=None, sticky=False):
    """Rotating residential username (default).
    sticky=True only if kabhi sticky chahiye (port 12000 + lifetime).
    """
    c = (country or GEONODE_COUNTRY).lower()
    base = GEONODE_USER_BASE.format(c)
    if sticky:
        sess = uuid.uuid4().hex[:8]
        return "%s-session-%s-lifetime-30" % (base, sess)
    return base


# ================= WATERFOX (Selenium + geckodriver) =================
# Chrome/CDP ki jagah ab Waterfox chalti hai.
# Proxy wahi ka wahi: Geonode SOCKS5 -> upar wala local HTTP bridge -> Waterfox
# ka manual HTTP proxy pref. Yaani exit IP pehle jaisa hi India ka residential.
#
# Playwright kyun nahi: Playwright 1.58 ka BiDi mode connect hote hi
# 'network.addDataCollector' bhejta hai, jo Gecko 141+ ka command hai. Waterfox
# 140 par wo 'unknown command' deta hai aur session wahin mar jaati hai. Isliye
# Waterfox ko geckodriver (WebDriver) se chalaya jaata hai.

# Kram maayne rakhta hai: pehle wo jagah jo is machine par sach me ho sakti hai
# (env, exe ke bagal ka folder, exe ke andar bandhi hui copy), phir is machine
# ke apne install, aur aakhir me hamari purani D:\streakads wali jagah. Isi
# kram se exe kisi bhi system par chalta hai -- Waterfox ko uske bagal me rakh
# do, bas.
WATERFOX_CANDIDATES = [
    os.environ.get("WATERFOX_PATH") or "",
    os.path.join(HERE, "Waterfox", "waterfox.exe"),
    os.path.join(HERE, "waterfox", "waterfox.exe"),
    os.path.join(os.path.dirname(HERE), "Waterfox", "waterfox.exe"),
    os.path.join(BUNDLE, "Waterfox", "waterfox.exe"),
    r"C:\Program Files\Waterfox\waterfox.exe",
    r"C:\Program Files (x86)\Waterfox\waterfox.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Waterfox\waterfox.exe"),
    r"D:\streakads\Waterfox\waterfox.exe",
    "/usr/bin/waterfox",
    "/Applications/Waterfox.app/Contents/MacOS/waterfox",
]

GECKODRIVER_CANDIDATES = [
    os.environ.get("GECKODRIVER_PATH") or "",
    os.path.join(BUNDLE, "geckodriver.exe"),        # exe ke andar bandhi copy
    os.path.join(HERE, "geckodriver.exe"),          # exe ke bagal me
    shutil.which("geckodriver") or "",
    os.path.join(os.path.dirname(HERE), "geckodriver-v0.36.0-win64",
                 "geckodriver.exe"),
    r"D:\streakads\geckodriver-v0.36.0-win64\geckodriver.exe",
    os.path.expandvars(
        r"%USERPROFILE%\.wdm\drivers\geckodriver\win64\v0.36.0\geckodriver.exe"),
    os.path.join(BUNDLE, "geckodriver"),            # linux/mac
    "/usr/local/bin/geckodriver",
]

# Waterfox apne aap ko Firefox hi batati hai; UA ko Chrome banane ka koi fayda
# nahi -- Gecko engine + Chrome UA ka mel na khana khud ek pehchaan hai.
WATERFOX_UA = None      # None = Waterfox ki apni UA

VIEWPORT = {"width": 1500, "height": 950}


def find_waterfox_exe():
    for c in WATERFOX_CANDIDATES:
        if c and os.path.isfile(c):
            return c
    return None


def find_geckodriver():
    for c in GECKODRIVER_CANDIDATES:
        if c and os.path.isfile(c):
            return c
    return None


def launch_waterfox(proxy_port=None, headless=False, extra_prefs=None):
    """Waterfox + geckodriver. Returns driver.

    proxy_port: upar wale local HTTP bridge ka port (None = bina proxy).
    extra_prefs: aur prefs jo launch ke waqt lagani hon (dict).
    """
    exe = find_waterfox_exe()
    if not exe:
        raise RuntimeError(
            "Waterfox nahi mili. WATERFOX_PATH set karo ya "
            "D:\\streakads\\Waterfox\\waterfox.exe rakho.")
    drv_path = find_geckodriver()
    if not drv_path:
        raise RuntimeError(
            "geckodriver nahi mila. GECKODRIVER_PATH set karo ya "
            "D:\\streakads\\geckodriver-v0.36.0-win64\\geckodriver.exe rakho.")

    opts = FirefoxOptions()
    opts.binary_location = exe
    if headless:
        opts.add_argument("-headless")

    # --- proxy: bridge ko manual HTTP proxy ki tarah ---
    if proxy_port:
        opts.set_preference("network.proxy.type", 1)
        opts.set_preference("network.proxy.http", "127.0.0.1")
        opts.set_preference("network.proxy.http_port", int(proxy_port))
        opts.set_preference("network.proxy.ssl", "127.0.0.1")
        opts.set_preference("network.proxy.ssl_port", int(proxy_port))
        opts.set_preference("network.proxy.share_proxy_settings", True)
        # DNS bhi proxy ke us paar -- warna local DNS leak hota hai
        opts.set_preference("network.proxy.socks_remote_dns", True)
        opts.set_preference("network.proxy.no_proxies_on", "")
    else:
        opts.set_preference("network.proxy.type", 0)

    # --- automation ke nishaan kam karo (Chrome build me jo init script tha) ---
    opts.set_preference("dom.webdriver.enabled", False)
    opts.set_preference("useAutomationExtension", False)
    opts.set_preference("marionette.enabled", True)
    opts.set_preference("privacy.resistFingerprinting", False)
    opts.set_preference("intl.accept_languages", "en-IN, en")   # locale="en-IN"
    opts.set_preference("browser.startup.homepage", "about:blank")
    opts.set_preference("browser.startup.page", 0)
    opts.set_preference("datareporting.healthreport.uploadEnabled", False)
    opts.set_preference("app.update.auto", False)
    opts.set_preference("browser.shell.checkDefaultBrowser", False)
    # popup/nayi window: Pay ke baad bank page nayi window me aati hai
    opts.set_preference("browser.link.open_newwindow", 3)        # naye tab me
    opts.set_preference("browser.link.open_newwindow.restriction", 0)
    if WATERFOX_UA:
        opts.set_preference("general.useragent.override", WATERFOX_UA)

    for k, v in (extra_prefs or {}).items():
        opts.set_preference(k, v)

    # ignore_https_errors=True ka Selenium roop
    opts.set_capability("acceptInsecureCerts", True)
    opts.set_capability("pageLoadStrategy", "eager")   # wait_until="domcontentloaded"

    service = FirefoxService(executable_path=drv_path, log_output=os.devnull)

    log("Waterfox  : %s" % exe)
    log("geckodriver: %s" % drv_path)
    driver = webdriver.Firefox(service=service, options=opts)

    driver.set_page_load_timeout(120)
    driver.set_script_timeout(60)
    driver.implicitly_wait(0)       # har intezaar humara apna, chhupa hua nahi

    # viewport ~1500x950 (window chrome ka farq nikaal kar)
    try:
        driver.set_window_size(VIEWPORT["width"], VIEWPORT["height"] + 90)
        inner = driver.execute_script(
            "return [window.innerWidth, window.innerHeight];")
        dw = VIEWPORT["width"] - int(inner[0])
        dh = VIEWPORT["height"] - int(inner[1])
        if dw or dh:
            driver.set_window_size(VIEWPORT["width"] + dw,
                                   VIEWPORT["height"] + 90 + dh)
    except Exception:
        pass
    return driver


def load_session(driver, d):
    """storage_state (cookies + localStorage) Waterfox me daalo.

    Cookie tabhi jaati hai jab browser usi domain par khada ho, isliye har
    origin ek baar khola jaata hai. Analytics ke cookies (bing/clarity/fb)
    chhod diye jaate hain -- login ya checkout unse nahi chalta.
    """
    st = d.get("state") or {}
    cookies = st.get("cookies") or []
    origins = st.get("origins") or []

    # Fastrr/pickrr ab is raaste me aata hi nahi -- checkout Shopify ka apna hai.
    # Pehle uska origin bhi khola jaata tha (uske cookies/localStorage ke liye);
    # ab wo sirf waqt kharab karta tha, isliye hata diya. Agar kisi purani
    # session file me uska localStorage darj hai to wo neeche khud jud jayega.
    wanted = {
        "https://estuaryworld.com": ("estuaryworld.com",),
    }
    # jis origin ka localStorage hai wo bhi list me aa jaye
    for o in origins:
        og = o.get("origin") or ""
        if og and og not in wanted:
            host = urlparse(og).hostname or ""
            wanted[og] = (host,)

    ok_c = fail_c = ok_ls = 0
    for origin, suffixes in wanted.items():
        # Residential proxy pehli baar aksar slow hota hai aur pehla load timeout
        # kha jaata hai. Ek hi koshish par haar maan lene ka natija bura hai:
        # cookie ek bhi nahi jaati aur poora order LOGGED-OUT chala jaata hai --
        # bina kisi saaf gadbad ke. Isliye teen koshish.
        khula = False
        for koshish in range(1, 4):
            try:
                driver.get(origin)
                khula = True
                break
            except Exception as e:
                log("   %s khula nahi (koshish %d/3: %s)"
                    % (origin, koshish, str(e)[:60]))
                time.sleep(3.0)
        if not khula:
            log("   %s teen baar me bhi nahi khula -- iske cookies chhod diye"
                % origin)
            continue
        time.sleep(1.0)

        host = urlparse(origin).hostname or ""
        # Pehle '.domain' wali, phir host-only. Ek hi naam ki dono ho sakti hain
        # (Shopify ka _shopify_essential aisa hi hai) aur browser inhe kabhi ek
        # hi maan kar ek doosri se badal deta hai. Asli session host-only wali
        # me hota hai, isliye wo AAKHIR me daali jaati hai -- takraav ho to
        # wahi bache.
        ordered = sorted(cookies,
                         key=lambda c: 0 if (c.get("domain") or "").startswith(".") else 1)
        for c in ordered:
            raw_dom = c.get("domain") or ""
            dom = raw_dom.lstrip(".")
            if not any(dom == s or dom.endswith("." + s) or s in dom
                       for s in suffixes):
                continue

            ck = {
                "name": c.get("name"),
                "value": c.get("value"),
                "path": c.get("path") or "/",
                "secure": bool(c.get("secure")),
                # httpOnly zaroori hai: Shopify ka asli session cookie
                # (_shopify_essential, host-only wala) httpOnly hota hai. Ise
                # chhod do to browser hamari daali cookie ko doosri maan kar
                # server ki nayi (logged-out) cookie se badal deta hai.
                "httpOnly": bool(c.get("httpOnly")),
            }

            # Ek hi naam ki DO cookies ho sakti hain -- ek '.domain' wali
            # (subdomains ke liye) aur ek host-only. Dono alag cookies hain.
            # Domain hamesha bhej dene se dono ek doosri ko mita deti thin, aur
            # jo bachti thi wo aksar galat wali hoti thi -- isi wajah se login
            # restore nahi hota tha.
            if raw_dom.startswith("."):
                ck["domain"] = raw_dom            # subdomains ke liye
            elif dom != host:
                continue                          # host-only, par abhi us host par nahi hain
            # host-only: domain bhejte hi nahi -- browser khud current host par lagata hai

            exp = c.get("expires")
            if exp and exp > 0:
                ck["expiry"] = int(exp)
            ss = c.get("sameSite")
            if ss in ("Strict", "Lax", "None"):
                ck["sameSite"] = ss
            try:
                driver.add_cookie(ck)
                ok_c += 1
            except Exception:
                ck.pop("domain", None)
                try:
                    driver.add_cookie(ck)
                    ok_c += 1
                except Exception:
                    fail_c += 1

        for o in origins:
            if (o.get("origin") or "") != origin:
                continue
            items = o.get("localStorage") or []
            if not items:
                continue
            try:
                driver.execute_script(
                    "for (const kv of arguments[0]) {"
                    "  try { localStorage.setItem(kv.name, kv.value); } catch (e) {}"
                    "}", items)
                ok_ls += len(items)
            except Exception as e:
                log("   localStorage (%s): %s" % (origin, str(e)[:60]))

    log("   session: %d cookie daale (%d chhode), %d localStorage"
        % (ok_c, fail_c, ok_ls))
    return ok_c


def save_session(driver, d, path):
    """Browser ki abhi ki haalat (taaza cookies + localStorage) session file me
    wapas likh do.

    Kaam khatam hone par cookies wo nahi rehtin jo shuru me thi -- site nayi
    deti hai, purani badal deti hai. Purani file waisi hi chhod dene ka matlab
    hai agli baar basi cookies le kar jaana. Isliye band karne se PEHLE haalat
    dobara utha kar likhi jaati hai.

    Cookie us domain par khade hokar hi milti hai, isliye har origin ek baar
    khola jaata hai -- par NAYE TAB me, taaki payment wala panna chhede bina
    rahe.
    """
    # sirf shop ka origin -- pickrr/Fastrr ab is flow me use hi nahi hota
    origins = ["https://estuaryworld.com"]
    old_state = d.get("state") or {}
    for o in (old_state.get("origins") or []):
        if o.get("origin") and o["origin"] not in origins:
            origins.append(o["origin"])

    main_handle = None
    tab = None
    try:
        main_handle = driver.current_window_handle
    except Exception:
        pass

    cookies = {}
    new_origins = []
    try:
        driver.switch_to.new_window("tab")
        tab = driver.current_window_handle
        for origin in origins:
            try:
                driver.get(origin)
                time.sleep(1.5)
            except Exception as e:
                log("   %s khula nahi (%s)" % (origin, str(e)[:50]))
                continue

            for c in driver.get_cookies():
                # Playwright ka storage_state format -- dono script isi ko padhti hain
                pc = {
                    "name": c.get("name"),
                    "value": c.get("value"),
                    "domain": c.get("domain"),
                    "path": c.get("path") or "/",
                    "expires": float(c.get("expiry")) if c.get("expiry") else -1,
                    "httpOnly": bool(c.get("httpOnly")),
                    "secure": bool(c.get("secure")),
                    "sameSite": (c.get("sameSite") or "Lax").capitalize(),
                }
                if pc["sameSite"] not in ("Strict", "Lax", "None"):
                    pc["sameSite"] = "Lax"
                cookies[(pc["name"], pc["domain"], pc["path"])] = pc

            try:
                items = driver.execute_script(
                    "const out = [];"
                    "for (let i = 0; i < localStorage.length; i++) {"
                    "  const k = localStorage.key(i);"
                    "  out.push({name: k, value: localStorage.getItem(k)});"
                    "}"
                    "return out;") or []
                if items:
                    new_origins.append({"origin": origin, "localStorage": items})
            except Exception:
                pass
    except Exception as e:
        log("   session dobara uthane me dikkat: %s" % str(e)[:80])
    finally:
        try:
            if tab:
                driver.switch_to.window(tab)
                driver.close()
            if main_handle:
                driver.switch_to.window(main_handle)
        except Exception:
            pass

    if not cookies:
        log("   taaza cookies nahi mili -- purani file waisi hi rehne di")
        return False

    d = dict(d)
    d["state"] = {"cookies": list(cookies.values()), "origins": new_origins}
    d["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
        log("   session taaza karke likh di: %s (%d cookie, %d origin)"
            % (os.path.basename(path), len(cookies), len(new_origins)))
        return True
    except Exception as e:
        log("   session likhi nahi gayi: %s" % str(e)[:80])
        return False


# ---------- Playwright ke jo thode selectors the, unka Selenium roop ----------
# Script me sirf ye khaas selectors the: :has-text(), :text-is(), :has(), :visible.
# CSS baaki sab seedha chalta hai.

_HAS_TEXT = re.compile(r"^(?P<base>.*?):has-text\((?P<q>['\"])(?P<txt>.*?)(?P=q)\)$")
_TEXT_IS = re.compile(r"^(?P<base>.*?):text-is\((?P<q>['\"])(?P<txt>.*?)(?P=q)\)$")
_HAS = re.compile(r"^(?P<base>.*?):has\((?P<inner>.+)\)$")


def _css_step_to_xpath(css):
    """'span.lang-en' -> 'span[contains(concat(" ",@class," ")," lang-en ")]'"""
    css = (css or "").strip() or "*"
    m = re.match(r"^([a-zA-Z][\w-]*|\*)?(.*)$", css)
    tag = m.group(1) or "*"
    rest = m.group(2) or ""
    preds = []
    for part in re.finditer(r"\.([\w-]+)|#([\w-]+)|\[([^\]]+)\]", rest):
        cls, idd, attr = part.group(1), part.group(2), part.group(3)
        if cls:
            preds.append(
                'contains(concat(" ", normalize-space(@class), " "), " %s ")' % cls)
        elif idd:
            preds.append('@id="%s"' % idd)
        elif attr:
            am = re.match(r"^\s*([\w-]+)\s*(?:([~^$*|]?=)\s*['\"]?([^'\"]*)['\"]?)?\s*$",
                          attr)
            if not am:
                continue
            name, op, val = am.group(1), am.group(2), am.group(3)
            if not op:
                preds.append("@%s" % name)
            elif op == "=":
                preds.append('@%s="%s"' % (name, val))
            elif op == "*=":
                preds.append('contains(@%s, "%s")' % (name, val))
            elif op == "^=":
                preds.append('starts-with(@%s, "%s")' % (name, val))
            else:
                preds.append('contains(@%s, "%s")' % (name, val))
    return tag + "".join("[%s]" % p for p in preds)


def _one_selector(sel):
    """Ek selector -> (by, expr, visible_only)."""
    sel = sel.strip()
    visible_only = False
    if ":visible" in sel:
        visible_only = True
        sel = sel.replace(":visible", "")

    m = _HAS_TEXT.match(sel)
    if m:
        xp = "//%s[contains(normalize-space(.), %s)]" % (
            _css_step_to_xpath(m.group("base")), _xq(m.group("txt")))
        return By.XPATH, xp, visible_only

    m = _TEXT_IS.match(sel)
    if m:
        xp = "//%s[normalize-space(.)=%s]" % (
            _css_step_to_xpath(m.group("base")), _xq(m.group("txt")))
        return By.XPATH, xp, visible_only

    m = _HAS.match(sel)
    if m:
        inner = m.group("inner").strip()
        im = _TEXT_IS.match(inner)
        if im:
            inner_xp = "%s[normalize-space(.)=%s]" % (
                _css_step_to_xpath(im.group("base")), _xq(im.group("txt")))
        else:
            ihm = _HAS_TEXT.match(inner)
            if ihm:
                inner_xp = "%s[contains(normalize-space(.), %s)]" % (
                    _css_step_to_xpath(ihm.group("base")), _xq(ihm.group("txt")))
            else:
                inner_xp = _css_step_to_xpath(inner)
        xp = "//%s[.//%s]" % (_css_step_to_xpath(m.group("base")), inner_xp)
        return By.XPATH, xp, visible_only

    return By.CSS_SELECTOR, sel, visible_only


def _xq(text):
    """XPath me quote -- text me ' ho to concat() lagta hai."""
    if "'" not in text:
        return "'%s'" % text
    if '"' not in text:
        return '"%s"' % text
    parts = text.split("'")
    return "concat(%s)" % ", ".join(
        ["'%s'" % p if i == 0 else "\"'\", '%s'" % p for i, p in enumerate(parts)])


def _split_selectors(sel):
    """Top-level comma par todo (bracket/quote ke andar wale comma chhod kar)."""
    out, depth, cur, quote = [], 0, "", None
    for ch in sel:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
            cur += ch
        elif ch in "([":
            depth += 1
            cur += ch
        elif ch in ")]":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [s.strip() for s in out if s.strip()]


# ---------- Scope: ek window ya uske andar ka ek frame ----------
class Scope(object):
    """Selenium me frame ke andar kaam karne ke liye har baar switch karna padta
    hai. Isliye har Scope apna raasta (window handle + frame index chain) yaad
    rakhta hai aur kaam se pehle khud us jagah pahunch jaata hai."""

    def __init__(self, driver, handle, path=(), url=""):
        self.d = driver
        self.handle = handle
        self.path = tuple(path)
        self._url = url

    # -- jagah par pahuncho --
    def use(self):
        """Us window/frame me pahuncho jiska ye Scope hai.

        Frame me index se ghusna bharosemand nahi: switch_to.frame(int) window.frames
        ka index leta hai, jabki humne raasta 'iframe, frame' elements gin kar banaya
        tha. Bina src wale ya baad me bane iframe se dono ginti alag ho jaati hain aur
        aadmi doosre frame me pahunch jaata hai. Isliye jis list se raasta bana tha,
        switch bhi usi list ke element se hota hai.
        """
        if self.d.current_window_handle != self.handle:
            self.d.switch_to.window(self.handle)
        self.d.switch_to.default_content()
        for idx in self.path:
            els = self.d.find_elements(By.CSS_SELECTOR, "iframe, frame")
            if idx >= len(els):
                raise RuntimeError("frame %d ab maujood nahi (kul %d)"
                                   % (idx, len(els)))
            self.d.switch_to.frame(els[idx])
        return self

    @property
    def url(self):
        if self.path:
            return self._url
        try:
            self.use()
            return self.d.current_url
        except Exception:
            return self._url

    def is_page(self):
        return not self.path

    # -- dhoondho --
    def query(self, sel, visible=None):
        self.use()
        out = []
        for one in _split_selectors(sel):
            by, expr, vis_only = _one_selector(one)
            want_vis = vis_only if visible is None else visible
            try:
                els = self.d.find_elements(by, expr)
            except Exception:
                continue
            for e in els:
                if want_vis:
                    try:
                        if not e.is_displayed():
                            continue
                    except Exception:
                        continue
                out.append(e)
        return out

    def count(self, sel):
        return len(self.query(sel))

    def first(self, sel):
        got = self.query(sel)
        return got[0] if got else None

    def visible_first(self, sel):
        got = self.query(sel, visible=True)
        return got[0] if got else None

    # -- padho --
    def body_text(self):
        try:
            self.use()
            return self.d.execute_script(
                "return document.body ? document.body.innerText : '';") or ""
        except Exception:
            return ""

    def evaluate(self, js, *args):
        self.use()
        return self.d.execute_script(js, *args)

    def evaluate_async(self, js, *args):
        self.use()
        return self.d.execute_async_script(js, *args)

    def title(self):
        self.use()
        return self.d.title or ""

    # -- Playwright jaisa wait --
    def wait_for_timeout(self, ms):
        time.sleep(ms / 1000.0)

    def goto(self, url, timeout=120):
        self.use()
        old = self.d.timeouts.page_load if hasattr(self.d, "timeouts") else None
        try:
            self.d.set_page_load_timeout(timeout)
            self.d.get(url)
        finally:
            if old:
                try:
                    self.d.set_page_load_timeout(old)
                except Exception:
                    pass

    def screenshot(self, path, full_page=False):
        self.use()
        if full_page:
            try:
                self.d.get_full_page_screenshot_as_file(path)
                return
            except Exception:
                pass
        self.d.save_screenshot(path)


def pages(driver):
    """Sabhi khuli windows/tabs -- Playwright ke context.pages jaisa."""
    out = []
    cur = None
    try:
        cur = driver.current_window_handle
    except Exception:
        pass
    for h in list(driver.window_handles):
        out.append(Scope(driver, h))
    if cur:
        try:
            driver.switch_to.window(cur)
        except Exception:
            pass
    return out


def frames(page):
    """Page ke andar ke saare frames (nested bhi), URL ke saath."""
    d = page.d
    found = []

    def _goto(path):
        d.switch_to.default_content()
        for idx in path:
            els = d.find_elements(By.CSS_SELECTOR, "iframe, frame")
            if idx >= len(els):
                raise RuntimeError("frame gayab")
            d.switch_to.frame(els[idx])

    def walk(path):
        try:
            _goto(path)
            n = len(d.find_elements(By.CSS_SELECTOR, "iframe, frame"))
        except Exception:
            return
        for i in range(n):
            child = path + (i,)
            try:
                _goto(child)
                url = d.execute_script("return location.href;") or ""
            except Exception:
                continue
            found.append(Scope(d, page.handle, child, url))
            walk(child)

    try:
        if d.current_window_handle != page.handle:
            d.switch_to.window(page.handle)
        walk(())
        d.switch_to.default_content()
    except Exception:
        pass
    return found


# ---------- element ke saath kaam ----------
def el_fill(scope, el, value):
    """Playwright ke fill() jaisa: purana hatao, naya likho, event bhejo."""
    scope.use()
    try:
        el.click()
    except Exception:
        pass
    try:
        el.clear()
    except Exception:
        pass
    try:
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)
    except Exception:
        pass
    el.send_keys(str(value))
    try:
        scope.d.execute_script(
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", el)
    except Exception:
        pass


def el_type(scope, el, value, delay=50):
    """Playwright ke type(delay=) jaisa -- ek ek akshar, thoda ruk kar."""
    scope.use()
    for ch in str(value):
        el.send_keys(ch)
        time.sleep(delay / 1000.0)


def el_value(el):
    try:
        return el.get_attribute("value") or ""
    except Exception:
        return ""


def real_click(scope, el):
    """Aadmi jaisa click: pahuncho, thoda ruko, dabao, chhodo."""
    scope.use()
    try:
        scope.d.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'center'});", el)
        time.sleep(0.4)
    except Exception:
        pass
    try:
        ActionChains(scope.d).move_to_element(el).pause(0.4) \
            .click_and_hold(el).pause(0.09).release().perform()
        return True
    except Exception:
        try:
            el.click()
            return True
        except Exception:
            return False


def in_view(scope, el):
    try:
        return bool(scope.d.execute_script(
            "const r = arguments[0].getBoundingClientRect();"
            "return r.width > 0 && r.height > 0 && r.top >= 0 && r.left >= 0"
            " && r.bottom <= (window.innerHeight || 0)"
            " && r.right <= (window.innerWidth || 0);", el))
    except Exception:
        return False


def scroll_click(scope, el, tries=3):
    """Teen tareeke, usi kram me: asli mouse -> click() -> DOM click."""
    for _ in range(tries):
        scope.use()
        try:
            scope.d.execute_script(
                "arguments[0].scrollIntoView({block:'center', inline:'center'});", el)
        except Exception:
            pass
        time.sleep(0.6)
        if in_view(scope, el):
            try:
                ActionChains(scope.d).move_to_element(el).pause(0.3) \
                    .click_and_hold(el).pause(0.09).release().perform()
                return "mouse"
            except Exception:
                pass
    try:
        scope.use()
        el.click()
        return "click()"
    except Exception:
        pass
    try:
        scope.use()
        scope.d.execute_script("arguments[0].click();", el)
        return "dom-click"
    except Exception:
        return None


def expect_new_page(driver, do_click, timeout=15):
    """Click ke baad nayi window khuli to uska Scope do, warna None."""
    before = set(driver.window_handles)
    try:
        do_click()
    except Exception:
        pass
    end = time.time() + timeout
    while time.time() < end:
        naye = set(driver.window_handles) - before
        if naye:
            h = naye.pop()
            try:
                driver.switch_to.window(h)
            except Exception:
                pass
            return Scope(driver, h)
        time.sleep(0.5)
    return None


# ---------- session / product helpers ----------
def newest_session():
    fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
    return fs[-1] if fs else None


def find(scope, sels):
    for s in sels:
        try:
            if scope.query(s, visible=True):
                return s
        except Exception:
            continue
    return None


def variant_id(page):
    return page.evaluate(
        """const f = document.querySelector('form[action*="/cart/add"]');
           const i = f && f.querySelector('input[name="id"], select[name="id"]');
           return i ? String(i.value) : null;""")


def pick(page, value):
    res = page.evaluate(
        """const v = arguments[0];
           const rs = [...document.querySelectorAll('input[type=radio]')]
                      .filter(x => (x.value || '').trim() === v);
           if (!rs.length) return 'nahi-mila';
           const r = rs[0];
           if (r.checked) return 'pehle-se-chuna';
           r.click();
           return 'daba-diya';""", value)
    log("      %s" % res)
    if res == "nahi-mila":
        return False
    page.wait_for_timeout(2500)
    return True


# ---------- checkout (Fastrr) ke frames ----------
def sr_frame(page):
    for fr in frames(page):
        if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
            try:
                if fr.count("#pincode"):
                    return fr
            except Exception:
                pass
    return None


def sr_frame_any(page):
    for fr in frames(page):
        if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
            try:
                if (fr.body_text() or "").strip():
                    return fr
            except Exception:
                pass
    return None


def ship_address(page, acct):
    f = None
    for _ in range(20):
        f = sr_frame(page)
        if f:
            break
        page.wait_for_timeout(1500)
    if not f:
        return "checkout ka pata wala form nahi mila (shayad pata pehle se hai)"

    ad = acct.get("address") or {}
    pin = ad.get("zip") or "000000"
    first = ad.get("first_name") or "Ishan"
    last = ad.get("last_name") or "Gupta"
    line1 = ad.get("address1") or "55/34 Shastri Nagar"
    line2 = ad.get("address2") or "Near Kidwai Nagar Market"
    city = ad.get("city") or "Kanpur"
    state = ad.get("province") or "Uttar Pradesh"
    email = acct.get("email") or ""

    def _put(sel, val):
        el = f.first(sel)
        if el is not None:
            el_fill(f, el, val)
        return el is not None

    _put("#pincode", pin)
    page.wait_for_timeout(4000)
    _put("#name", first)
    _put("#lastName", last)
    _put("#line1", line1)
    _put("#line2", line2)
    for sel, val in (("#city", city), ("#state", state)):
        try:
            el = f.first(sel)
            if el is not None and not el_value(el).strip():
                el_fill(f, el, val)
        except Exception:
            pass
    if email:
        try:
            _put("#email", email)
        except Exception:
            pass

    try:
        home = f.first("input[name='home']")
        if home is not None and not home.is_selected():
            f.d.execute_script("arguments[0].click();", home)
    except Exception:
        pass

    got = f.first("#addAddressBtn")
    if got is None:
        return "'Add address' ka button nahi mila"
    if not real_click(f, got):
        try:
            f.use()
            got.click()
        except Exception:
            pass

    for _ in range(6):
        page.wait_for_timeout(4000)
        try:
            if "Add shipping address" not in (f.body_text() or ""):
                return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
        except Exception:
            return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
    return "pata bhara par form abhi bhi khada hai -- dekh lijiye"


def confirm_email(page, acct):
    email = acct.get("email") or ""
    if not email:
        return "account par email hi nahi hai"
    f = sr_frame_any(page)
    if not f:
        return "checkout ka frame nahi mila"

    for _ in range(10):
        try:
            body = f.body_text() or ""
        except Exception:
            return "checkout ka frame chala gaya"
        if "onfirm your email" not in body:
            return "email confirm karne ki zaroorat nahi thi"

        btn = f.first("button:has-text('Confirm email')")
        box = f.visible_first("input#email, input[type='email']")
        if btn is not None and box is not None:
            el_fill(f, box, email)
            page.wait_for_timeout(800)
            real_click(f, btn)
            page.wait_for_timeout(6000)
            try:
                if "onfirm your email" not in (f.body_text() or ""):
                    return "email confirm ho gaya (%s)" % email
            except Exception:
                return "email confirm ho gaya (%s)" % email
        page.wait_for_timeout(2000)

    try:
        ins = f.evaluate(
            "return [...document.querySelectorAll('input')]"
            ".map(e => (e.id||'-')+'/'+(e.name||'-')+'/'+(e.type||'-'));") or []
    except Exception:
        ins = []
    return "email confirm nahi hua | frame ke input: %s" % ", ".join(ins[:10])


def read_checkout(page):
    f = sr_frame_any(page)
    if not f:
        return None
    try:
        body = f.body_text() or ""
    except Exception:
        return None
    out = {"address": [], "pay": [], "total": ""}

    lines = [l.strip() for l in body.splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if re.search(r"\b\d{6}\b", l) and len(l) > 12:
            out["address"] = lines[max(0, i - 2):i + 3]
            break

    try:
        texts = f.evaluate(
            "return [...document.querySelectorAll("
            "\"label, [class*='paymentMethod'], [class*='payment-method']\")]"
            ".map(e => e.innerText || '');") or []
        out["pay"] = [t.strip() for t in texts if 2 < len(t.strip()) < 60][:12]
    except Exception:
        pass

    m = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", body)
    if m:
        out["total"] = m[-1]
    return out


# ---------- gateway / card ----------
CARD_TARGETS = [
    "#payment-method-button-Card label.payment-button-heading",
    "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
    "#payment-method-button-Card",
]

GATEWAY_HINTS = ("easebuzz", "eazypay", "payment", "pay.", "3ds", "acs",
                 "razorpay", "payu", "billdesk")


def card_frame(page):
    for fr in frames(page):
        u = (fr.url or "").lower()
        if any(k in u for k in ("easebuzz", "pay.", "payment", "3ds", "acs")):
            try:
                if fr.query("input", visible=True):
                    return fr
            except Exception:
                pass
    return None


def card_fields(f):
    try:
        return f.evaluate(
            """return [...document.querySelectorAll('input')]
                 .filter(e => e.offsetParent !== null || e.getClientRects().length)
                 .map(e => ({id: e.id || '', name: e.name || '',
                             ph: e.placeholder || '',
                             aria: e.getAttribute('aria-label') || '',
                             maxlen: e.maxLength}))
                 .filter(o => /card|number|cvv|cvc|expiry|month|year|holder/i
                              .test(o.id + o.name + o.ph + o.aria)
                           || (o.maxlen >= 3 && o.maxlen <= 19));""") or []
    except Exception:
        return []


def gateway_frames(page):
    out = set()
    for fr in frames(page):
        u = (fr.url or "")
        if u and any(k in u.lower() for k in GATEWAY_HINTS):
            out.add(u)
    return out


def card_state(page, f):
    st = {"qr": False, "h": 0.0, "frames": gateway_frames(page)}
    try:
        st["qr"] = f.count("#src-qrcode-payment-btn") > 0
    except Exception:
        pass
    try:
        st["h"] = f.evaluate(
            "const e = document.querySelector('#payment-method-button-Card');"
            "return e ? e.getBoundingClientRect().height : 0;") or 0.0
    except Exception:
        pass
    return st


def card_chosen(page, f, before):
    now = card_state(page, f)
    if now["frames"] - before["frames"]:
        return True
    if before["qr"] and not now["qr"]:
        return True
    if now["h"] > before["h"] + 30:
        return True
    return bool(card_fields(f))


def card_form_ready(page):
    for fr in all_scopes(page.d):
        got = card_fields(fr)
        if got:
            return "form aa gaya (%s)" % ", ".join(
                (g["id"] or g["name"] or g["ph"] or "?") for g in got[:6])
    return "form abhi saamne nahi aaya"


def all_scopes(driver):
    """Har khuli tab, aur har tab ke andar ke saare frames.

    Fastrr wale raaste me gateway ek iframe me aata tha, isliye sirf frames
    dekhna kaafi tha. Shopify ke apne checkout se 'Pay now' dabane par Easebuzz
    poore panne ke roop me khulta hai (kabhi nayi tab me) -- wahan frame me
    dhoondhne se kuch nahi milta. Isliye ab dono jagah dekhi jaati hai.
    """
    out = []
    for pg in pages(driver):
        out.append(pg)
        try:
            out.extend(frames(pg))
        except Exception:
            continue
    return out


def pick_card_type(page, kind="Credit", secs=75):
    sels = ["span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
            "span.lang-en:text-is('%s Card')" % kind,
            "*:text-is('%s Card')" % kind]
    end = time.time() + secs
    while time.time() < end:
        for fr in all_scopes(page.d):
            for sel in sels:
                try:
                    el = fr.first(sel)
                    if el is None:
                        continue
                except Exception:
                    continue
                how = scroll_click(fr, el)
                if not how:
                    continue
                page.wait_for_timeout(5000)
                return "%s Card daba diya (%s) -- %s" % (
                    kind, how, card_form_ready(page))
        page.wait_for_timeout(2500)
    return "%s Card ka option gateway ke panne par nahi mila" % kind


def clear_blocker(page):
    f = sr_frame_any(page)
    if not f:
        return ""
    try:
        body = (f.body_text() or "").lower()
    except Exception:
        return ""
    if "active session" not in body and "page isn't available" not in body:
        return ""
    for sel in ("button:has-text('Continue here')",
                "a:has-text('Continue here')",
                "[role=button]:has-text('Continue here')"):
        try:
            el = f.first(sel)
            if el is not None:
                scroll_click(f, el)
                page.wait_for_timeout(8000)
                return "purana session ka parda hata diya (Continue here)"
        except Exception:
            continue
    return "CHETAVNI: purana session ka parda hai par 'Continue here' nahi mila"


def pick_card(page):
    f = sr_frame_any(page)
    if not f:
        return "checkout ka frame nahi mila"

    el = None
    used = ""
    for _ in range(10):
        for sel in CARD_TARGETS:
            try:
                got = f.first(sel)
                if got is not None:
                    el, used = got, sel
                    break
            except Exception:
                continue
        if el is not None:
            break
        page.wait_for_timeout(2000)
    if el is None:
        return "Credit/Debit Card ka khaana nahi mila (shayad email confirm baaki hai)"

    before = card_state(page, f)
    how = None
    for _ in range(3):
        how = scroll_click(f, el)
        for _ in range(6):
            page.wait_for_timeout(1500)
            if card_chosen(page, f, before):
                break
        if card_chosen(page, f, before):
            break
    if not card_chosen(page, f, before):
        return "Card daba nahi paye (%s se koshish ki, UPI hi khula raha)" % (
            how or "kisi tareeke")

    log("      Card chun liya (%s | %s)" % (how, used))
    naya = card_state(page, f)["frames"] - before["frames"]
    if naya:
        log("      gateway ka panna khula: %s" % list(naya)[0][:90])

    for i in range(12):
        page.wait_for_timeout(2500)
        cf = card_frame(page)
        if cf:
            return "card ke khaane khul gaye (gateway ke frame me, %ds baad)" % (
                (i + 1) * 2.5)
        got = card_fields(f)
        if got:
            return "card ke khaane khul gaye (checkout ke frame me: %s)" % (
                ", ".join((g["id"] or g["name"] or g["ph"] or "?") for g in got[:6]))
    if naya:
        return "Card chun liya aur gateway ka panna khul gaya (agla kadam: step 10)"
    return "Card to chun liya, par khaane abhi tak nahi aaye -- out/ ki tasveer dekhiye"


def easebuzz_form_frame(page, secs=40):
    sel = ('input[name="card_number"], input[placeholder="Test Holder"], '
           'input[name="card_exp_date"], input[name="card_cvv"]')
    end = time.time() + secs
    while time.time() < end:
        # tab ho ya frame -- jahan bhi card ka khaana mile
        for fr in all_scopes(page.d):
            try:
                if fr.count(sel) >= 1:
                    return fr
            except Exception:
                continue
        page.wait_for_timeout(1500)
    return None


def _fill_one(fr, page, sels, value, label):
    for sel in sels:
        try:
            el = fr.first(sel)
            if el is None:
                continue
            try:
                if not el.is_displayed():
                    continue
            except Exception:
                pass
            fr.use()
            try:
                fr.d.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", el)
            except Exception:
                pass
            page.wait_for_timeout(200)
            el.click()
            page.wait_for_timeout(150)
            el_fill(fr, el, "")
            el_type(fr, el, str(value), delay=50)
            page.wait_for_timeout(250)
            got = el_value(el)
            log("      %s fill -> '%s'" % (label, got[:28] if got else value))
            return True
        except Exception as e:
            log("      %s try fail (%s): %s" % (label, sel[:40], str(e)[:50]))
    return False


def fill_card_details(page, number, exp, holder, cvv, click_pay=True):
    fr = easebuzz_form_frame(page)
    if not fr:
        return "FAIL: card form frame nahi mila (Credit Card choose ke baad wait karo)"

    num_clean = re.sub(r"\s+", "", number or "")
    num_disp = " ".join(num_clean[i:i + 4] for i in range(0, len(num_clean), 4))

    ok_n = _fill_one(fr, page, [
        'input[name="card_number"]',
        'input[placeholder="Test Holder"]',
    ], num_disp, "Card Number")

    ok_e = _fill_one(fr, page, [
        'input[name="card_exp_date"]',
        'input[placeholder="Test Holder"]',
    ], exp, "MM/YY")

    ok_h = _fill_one(fr, page, [
        'input[placeholder="Test Holder"]',
        'input[name^="ebz_card_holder_name"]',
        'input[name*="card_holder"]',
    ], holder, "Card Holder")

    ok_c = _fill_one(fr, page, [
        'input[name="card_cvv"]',
        'input[placeholder="Test Holder"]',
    ], cvv, "CVV")

    # human-like pause before Pay (gateway timing checks)
    log("      Pay se pehle wait 6-8s...")
    page.wait_for_timeout(7000)

    pay_ok = False
    if click_pay:
        bank_popup = None
        for scope in (fr, page):
            # data-testid sabse bharosemand hai. Button ke andar ka text kai
            # span me tuta hua hai ("Pay" alag, "₹ 250.00" alag), isliye text se
            # dhoondhna aakhri sahara hai, pehla nahi.
            for sel in ('button[data-testid="pay-button"]',
                        'button.pay-btn',
                        'button:has-text("Pay ₹")',
                        'button:has-text("Pay Rs")',
                        'button:has-text("Pay")'):
                try:
                    el = scope.visible_first(sel)
                    if el is None:
                        continue
                    log("      Pay button click")
                    bank_popup = expect_new_page(
                        page.d, lambda: scroll_click(scope, el), timeout=20)
                    if bank_popup is not None:
                        log("      Pay ne nayi window kholi: %s"
                            % ((bank_popup.url or "")[:80]))
                    pay_ok = True
                    page.wait_for_timeout(5000)
                    break
                except Exception:
                    continue
            if pay_ok:
                break
        if bank_popup is not None:
            try:
                bank_popup.use()
                end = time.time() + 60
                while time.time() < end:
                    st = page.d.execute_script("return document.readyState;")
                    if st in ("interactive", "complete"):
                        break
                    time.sleep(1)
            except Exception:
                pass

    return "number=%s | exp=%s | holder=%s | cvv=%s | pay=%s" % (
        "ok" if ok_n else "FAIL",
        "ok" if ok_e else "FAIL",
        "ok" if ok_h else "FAIL",
        "ok" if ok_c else "FAIL",
        "clicked" if pay_ok else "skip",
    )


def wait_bank_page(driver, page, secs=120):
    """Pay ke baad ICICI / ACS / bank page (nayi window ya same)."""
    end = time.time() + secs
    loading_seen = False
    while time.time() < end:
        for pg in pages(driver):
            try:
                u = (pg.url or "").lower()
                body = ""
                try:
                    body = (pg.body_text() or "").lower()
                except Exception:
                    pass
                if "loading bank" in body:
                    loading_seen = True
                    continue
                if any(k in u for k in (
                    "wibmo", "acs", "icici", "3ds", "bank", "easebuzz",
                    "secure-acs", "mumrdc",
                )):
                    if "corporate id" in body or "employee id" in body:
                        return pg
                    if pg.count("input#corporateId, input#employeeId"):
                        return pg
                    if any(k in u for k in ("wibmo", "acs", "icici")):
                        pg.wait_for_timeout(2000)
                        if pg.count("input#corporateId"):
                            return pg
                if "corporate id" in body or pg.count("input#corporateId"):
                    return pg
                # bank form kisi frame ke andar bhi ho sakta hai
                for fr in frames(pg):
                    try:
                        if fr.count("input#corporateId"):
                            return fr
                    except Exception:
                        continue
            except Exception:
                continue
        page.wait_for_timeout(2000)
    if loading_seen:
        log("      (Loading Bank Page dekha, form nahi aaya — fingerprint/block ho sakta hai)")
    return None


def fill_bank_corporate(driver, page, corp_id, emp_id):
    """ICICI ACS form: input#corporateId, input#employeeId, a.btn.primary__btn.
    Phir OTP manual."""
    log("      bank page ka wait...")
    bank = wait_bank_page(driver, page, secs=120)
    if not bank:
        return "FAIL: bank/ACS page nahi mila (Loading Bank Page atak sakta hai)"

    log("      bank URL: %s" % ((bank.url or "")[:100]))

    for _ in range(20):
        try:
            if bank.count("input#corporateId"):
                break
        except Exception:
            pass
        bank.wait_for_timeout(1000)
    else:
        return "FAIL: corporateId input nahi mila"

    try:
        el_fill(bank, bank.first("input#corporateId"), corp_id)
        log("      Corporate ID -> %s" % corp_id)
    except Exception as e:
        return "FAIL: corporateId fill: %s" % str(e)[:60]

    bank.wait_for_timeout(800)
    try:
        el_fill(bank, bank.first("input#employeeId"), emp_id)
        log("      Employee ID -> %s" % emp_id)
    except Exception as e:
        return "FAIL: employeeId fill: %s" % str(e)[:60]

    bank.wait_for_timeout(1500)

    submitted = False
    for sel in ('a.btn.primary__btn:has-text("Submit")',
                'a.btn.primary__btn:has-text("SUBMIT")',
                'a.primary__btn',
                'a.btn.primary__btn',
                'button:has-text("Submit")',
                'button:has-text("SUBMIT")'):
        try:
            el = bank.visible_first(sel)
            if el is None:
                continue
            log("      Submit click: %s" % sel)
            bank.use()
            try:
                el.click()
            except Exception:
                bank.d.execute_script("arguments[0].click();", el)
            submitted = True
            bank.wait_for_timeout(4000)
            break
        except Exception:
            continue

    if not submitted:
        try:
            bank.evaluate("if (typeof submit === 'function') submit();")
            submitted = True
            log("      Submit via JS submit()")
            bank.wait_for_timeout(4000)
        except Exception:
            pass

    if not submitted:
        return "corp/emp filled par Submit nahi hua"

    return "Corporate+Employee filled, Submit OK — ab OTP manual"


# ================= OTP: API se laao, khud bharo =================
# Corporate/Employee ID Submit ke baad bank OTP bhejta hai. Wo OTP employee ke
# paas jaata hai, aur ek API se padha ja sakta hai.
#
# API ka bartaav (magzter wale setup jaisa hi):
#   200 -> taaza OTP mila; API use KHATM kar deti hai (dobara 404 aayega)
#   404 -> abhi OTP aaya nahi -- ruko aur phir poochho
#   401 -> token galat/nadaarad     503 -> server par token set nahi
#   429 -> bahut jaldi poochha -- thoda ruk kar
# Isliye 200 milte hi wahi asli OTP hai; 404 par bas intezaar.

OTP_API_URL = (os.environ.get("OTP_API_URL")
               or "https://test.trackopia.in/api/employees/{API_EMPLOYEE_ID}/latest-otp")
OTP_FETCH_TOKEN = (os.environ.get("OTP_FETCH_TOKEN")
                   or "DIrZA4lVF52YBTbVc_n8eTLgnGV8CLrD5rOtd5oHVZ0")

OTP_FIELD_SELS = ('input[name="otpValue"]',
                  'input[autocomplete="one-time-code"]',
                  'input[name="otp"]',
                  'input#otp',
                  'input[id*="otp"]',
                  'input[placeholder*="OTP"]')

OTP_SUBMIT_SELS = ('button#submitBtn',
                   'button.submit',
                   'button:has-text("SUBMIT")',
                   'a.btn.primary__btn:has-text("Submit")',
                   'input[type="submit"]')

OTP_RESEND_SELS = ('button#otpResend',
                   'button.resendcode',
                   'button:has-text("RESEND")')

# OTP galat hone ke sandesh -- inhe dekh kar dobara OTP mangwaya jaata hai.
OTP_BAD_MSGS = ("invalid otp", "incorrect otp", "otp expired", "wrong otp",
                "otp did not match", "please fill in the otp",
                "invalid verification code", "incorrect code")

MAX_OTP_ATTEMPTS = 3


def _otp_digits(data):
    """Jawaab (dict/list/str) me kahin bhi chhupa 4-8 ank ka OTP nikalo."""
    if isinstance(data, dict):
        for k, v in data.items():
            kl = str(k).lower()
            if ("otp" in kl or "code" in kl) and isinstance(v, (str, int)):
                dig = re.sub(r"\D", "", str(v))
                if 4 <= len(dig) <= 8:
                    return dig
        for v in data.values():
            got = _otp_digits(v)
            if got:
                return got
    elif isinstance(data, list):
        for v in data:
            got = _otp_digits(v)
            if got:
                return got
    return None


def fetch_otp(emp_id, card_last4="Doe", max_polls=180, delay=4,
              api_url=None, token=None):
    # 180 x 4s = 12 minute. Pehle 60 (4 minute) tha aur wahi kam pad gaya --
    # ek asli run me bank ka SMS Submit ke gyarah minute baad aaya tha.
    """API se taaza OTP lao. Milne tak poochhte raho. Na mile to None."""
    api_url = api_url or OTP_API_URL
    token = token or OTP_FETCH_TOKEN
    if not api_url:
        return None
    if not token:
        # Bina token ke endpoint par jaana hi nahi -- wahi niyam magzter wale
        # setup me bhi hai.
        log("      OTP token set nahi hai -- API se OTP nahi mangwayenge")
        return None

    url = api_url.replace("{API_EMPLOYEE_ID}", str(emp_id).upper().strip())
    headers = {"Accept": "application/json",
               "X-OTP-Token": token,
               "Authorization": "Bearer %s" % token}
    want4 = str(card_last4).strip()[-4:] if card_last4 else ""
    log("      OTP maang rahe hain: %s%s"
        % (url, ("  (card ****%s)" % want4) if want4 else ""))

    last_err = "Doe"
    for i in range(max_polls):
        try:
            r = requests.get(url, headers=headers, timeout=20)
            sc = r.status_code

            if sc == 200:
                try:
                    data = r.json()
                except ValueError:
                    dig = re.sub(r"\D", "", r.text)
                    if 4 <= len(dig) <= 8:
                        log("      OTP mila: %s" % dig)
                        return dig
                    time.sleep(delay)
                    continue
                otp = _otp_digits(data)
                if otp:
                    c4 = ""
                    if isinstance(data, dict):
                        c4 = str(data.get("card_last_four", "")).strip()
                    # Pehle ye OTP chhod diya jaata tha agar API ka
                    # card_last_four hamare card se mel nahi khata tha. Asli
                    # jaanch me pata chala ki ICICI ke SMS me jo 4 ank aate
                    # hain wo hamesha card ke aakhri 4 ank hote hi nahi (hamara
                    # card ****8363 tha, API ne ****7002 bataya) -- yaani wo
                    # filter sahi OTP ko bhi chhod deta tha aur transaction
                    # wahin mar jaata tha. Ab: mel na khaye to chetavni do,
                    # par OTP le lo. Ek employee ek waqt me ek hi transaction
                    # karta hai, isliye taaza OTP wahi hai jiska intezaar hai.
                    if want4 and c4 and c4 != want4:
                        log("      CHETAVNI: API ka card ****%s hai, hamara "
                            "****%s -- phir bhi yahi OTP le rahe hain" % (c4, want4))
                    log("      OTP mila: %s%s" % (otp, ("  (card ****%s)" % c4) if c4 else ""))
                    return otp
                time.sleep(delay)
                continue

            if sc == 404:
                if i % 10 == 0:
                    log("      abhi OTP aaya nahi (404) -- intezaar...")
                time.sleep(delay)
                continue
            if sc == 401:
                log("      OTP token galat hai (401)")
                return None
            if sc == 503:
                log("      OTP server par token set nahi (503)")
                return None
            if sc == 429:
                log("      bahut jaldi poochh liya (429) -- thoda ruk kar")
                time.sleep(max(delay, 6))
                continue

            if i % 10 == 0:
                log("      OTP API HTTP %s: %s" % (sc, r.text[:120]))
            time.sleep(delay)
        except Exception as e:
            msg = str(e)[:100]
            if msg != last_err:
                log("      OTP API se baat nahi hui: %s" % msg)
                last_err = msg
            time.sleep(delay)

    log("      itni der me OTP nahi aaya")
    return None


def otp_scope(driver, secs=60):
    """Jis tab/frame me OTP ka khaana hai wo scope do."""
    end = time.time() + secs
    while time.time() < end:
        for scope in all_scopes(driver):
            for sel in OTP_FIELD_SELS:
                try:
                    if scope.visible_first(sel) is not None:
                        return scope, sel
                except Exception:
                    continue
        time.sleep(2)
    return None, None


def submit_otp(driver, scope=None):
    """OTP ka SUBMIT dabao (har tab/frame me dhoondh kar)."""
    scopes = [scope] if scope is not None else all_scopes(driver)
    for sc in scopes:
        for sel in OTP_SUBMIT_SELS:
            try:
                el = sc.visible_first(sel)
                if el is None:
                    continue
                how = scroll_click(sc, el)
                if how:
                    time.sleep(6)
                    return "SUBMIT daba diya (%s | %s)" % (how, sel)
            except Exception:
                continue
    if scope is not None:      # us scope me nahi mila to poore browser me dekho
        return submit_otp(driver)
    return "SUBMIT ka button nahi mila (shayad pehle hi ho gaya)"


def resend_otp(driver, scope=None):
    scopes = [scope] if scope is not None else all_scopes(driver)
    for sc in scopes:
        for sel in OTP_RESEND_SELS:
            try:
                el = sc.visible_first(sel)
                if el is None:
                    continue
                if scroll_click(sc, el):
                    time.sleep(5)
                    return True
            except Exception:
                continue
    return False


def do_otp(driver, emp_id, card_no="0000000000000000", manual=False,
           api_url=None, token=None, record=None):
    """OTP ka pura kaam: API se lao -> khaane me bharo -> SUBMIT.

    manual=True par script sirf intezaar karti hai ki tum OTP bhar do, phir
    SUBMIT khud daba deti hai.
    """
    scope, fsel = otp_scope(driver, secs=90)
    if scope is None:
        return "OTP ka khaana nahi mila (shayad OTP maanga hi nahi gaya)"
    log("      OTP ka khaana mila (%s)" % fsel)

    if manual:
        log("      OTP tum bharo -- bhar kar Enter dabao")
        try:
            input("👉 OTP bharne ke baad Enter: ")
        except Exception:
            time.sleep(90)
        return submit_otp(driver, scope)

    last = "Doe"
    for attempt in range(1, MAX_OTP_ATTEMPTS + 1):
        otp = fetch_otp(emp_id, card_last4=card_no, api_url=api_url, token=token)
        if not otp:
            return "OTP nahi mila (koshish %d/%d)" % (attempt, MAX_OTP_ATTEMPTS)

        el = scope.visible_first(fsel)
        if el is None:
            scope, fsel = otp_scope(driver, secs=30)
            if scope is None:
                return "OTP bharne se pehle hi khaana gayab ho gaya"
            el = scope.visible_first(fsel)
        el_fill(scope, el, "")
        el_type(scope, el, otp, delay=120)     # ek ek ank, aadmi ki raftaar se
        if record is not None:
            record["otp"] = otp                # CSV me isi ka nishaan jaata hai
        log("      OTP bhar diya: %s" % otp)
        time.sleep(1.0)

        last = submit_otp(driver, scope)
        log("      %s" % last)
        time.sleep(4)

        # galat OTP ka sandesh dikha to naya OTP mangwao
        body = ""
        try:
            body = (scope.body_text() or "").lower()
        except Exception:
            pass
        bad = next((m for m in OTP_BAD_MSGS if m in body), None)
        if not bad:
            return "OTP ho gaya (%s)" % last
        log("      bank ne kaha: '%s' -- dobara OTP mangwate hain" % bad)
        if attempt < MAX_OTP_ATTEMPTS:
            resend_otp(driver, scope)

    return "OTP %d baar try kiya, phir bhi nahi chala" % MAX_OTP_ATTEMPTS


ORDER_CSV_COLS = ["when", "status", "phone", "email", "checkout_email",
                  "session_file", "order_ref", "amount", "paid", "items",
                  "card_last4", "otp", "product", "url"]


def likho_order_row(acct, status, ref="", url="", extra=None):
    """orders.csv me ek line -- kis account par kya hua.

    Pehle ye line SIRF tab likhi jaati thi jab thank-you panna mil jaye. Uska
    natija ye tha ki jo order OTP tak pahunch kar bhi confirm hote nahi dikha,
    uska koi nishaan hi nahi bachta -- kaunsa account, kitne ka, kaunsa card,
    kuch nahi. Ab har run ki line jaati hai, aur `status` batata hai kya hua.
    """
    e = extra or {}
    path = os.path.join(HERE, "orders.csv")
    row = [time.strftime("%Y-%m-%d %H:%M:%S"), status,
           acct.get("phone", ""), acct.get("email", ""),
           e.get("checkout_email", ""), e.get("session_file", ""), ref,
           e.get("amount", ""), e.get("paid", ""), e.get("items", ""),
           e.get("card_last4", ""), e.get("otp", ""),
           e.get("product", ""), (url or "")[:160]]
    try:
        naya = not os.path.exists(path)
        if not naya:
            # Purani file ke column naye se mel nahi khate to line tedhi jaakar
            # baithegi -- ek column ka data doosre ke neeche. Aisi file ko
            # chhedne ke bajaye kinare kar do aur nayi shuru karo.
            try:
                with open(path, newline="", encoding="utf-8") as fh:
                    pehli = next(csv.reader(fh), [])
                if pehli and pehli != ORDER_CSV_COLS:
                    purani = "%s.%s.csv" % (path[:-4], time.strftime("%Y%m%d_%H%M%S"))
                    os.rename(path, purani)
                    log("   orders.csv ke column badal gaye -- purani file: %s"
                        % os.path.basename(purani))
                    naya = True
            except Exception:
                pass
        with open(path, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if naya:
                w.writerow(ORDER_CSV_COLS)
            w.writerow(row)
        return True
    except Exception as ex:
        log("   orders.csv me nahi likh paye: %s" % str(ex)[:80])
        return False


def read_account_order(driver, secs=60):
    """Order lag jaane ke baad /account se uski asli details lao.

    Thank-you page par jo "Confirmation #TE5KTZ0DF" dikhta hai wo dukaan ka
    andaruni number hai. Grahak ke account me order ka apna number hota hai
    (#136267), aur uske saath date, payment status aur kul rakam bhi. Record
    ke liye yahi kaam ka hai -- support se baat karni ho ya milaan karna ho to
    isi number se hota hai.

    Panna NAYE TAB me khola jaata hai. Payment/thank-you wala tab chhedna
    theek nahi -- wo abhi bhi kaam ka ho sakta hai, aur uska URL record me
    jaata hai.
    """
    tab = None
    pehla = None
    try:
        pehla = driver.current_window_handle
    except Exception:
        pass
    try:
        driver.switch_to.new_window("tab")
        tab = driver.current_window_handle
        pg = Scope(driver, tab)
        pg.goto("%s/account" % SHOP, timeout=90)

        # Order table React se nahi, seedha panne me aata hai -- par panna
        # dhire khul sakta hai, isliye thodi der dekhte rehte hain.
        end = time.time() + secs
        got = None
        while time.time() < end:
            pg.wait_for_timeout(2000)
            got = pg.evaluate("""
              const box = document.querySelector('.account-table .tbody');
              if (!box) return null;
              const row = box.querySelector('.tr.orders');
              if (!row) return null;
              const saaf = (td) => {
                if (!td) return '';
                let t = (td.innerText || '').trim();
                const lab = td.querySelector('.label');
                if (lab) {
                  const lt = (lab.innerText || '').trim();
                  if (lt && t.indexOf(lt) === 0) t = t.slice(lt.length);
                }
                return t.replace(/\s+/g, ' ').trim();
              };
              const tds = [...row.querySelectorAll('.td')];
              const a = row.querySelector('a[href*="/account/orders/"]');
              return {
                no: a ? (a.innerText || '').trim() : saaf(tds[0]),
                url: a ? a.href : '',
                date: saaf(tds[1]),
                pay: saaf(tds[2]),
                total: saaf(tds[3])
              };""")
            if got and (got.get("no") or got.get("url")):
                break

        if not got:
            log("   /account par order ki list nahi mili")
            return {}
        log("   account me order: %s | %s | %s | %s"
            % (got.get("no", "?"), got.get("date", "?"),
               got.get("pay", "?"), got.get("total", "?")))
        return got
    except Exception as e:
        log("   /account padha nahi gaya: %s" % str(e)[:90])
        return {}
    finally:
        try:
            if tab:
                driver.switch_to.window(tab)
                driver.close()
            if pehla:
                driver.switch_to.window(pehla)
        except Exception:
            pass


# Aakhri order ka poora record -- batch/GUI isi se poochhte hain ki kya hua.
LAST_ORDER = {}


def _sheet_order_row(ord_ws, acct, info, nateeja, page,
                     status_override=None, return_row=False):
    """Order_Records tab me ek line -- kis account par kya hua.

    Ye orders.csv ke ALAWA hai, uski jagah nahi. CSV usi machine par rehti hai
    jahan script chali; sheet sabko dikhti hai. Dono isliye ki ek kharaab ho
    to doosra bacha rahe.

    status_override: Status column me yahi likho (jaise 'OTP_SUBMIT_OK'). Na do
        to nateeja se tay hota hai (purana bartaav).
    return_row: True par lauti hui cheez line ka row number hai (baad me usi
        line ko update karne ke liye) -- warna sirf True/False.
    """
    if ord_ws is None:
        return 0 if return_row else False
    ad = acct.get("address") or {}
    laga = str(nateeja or "").startswith("ORDER LAG GAYA")
    ref = ""
    m = re.search(r"ORDER LAG GAYA -- (\S+)", str(nateeja or ""))
    if m:
        ref = m.group(1)
    try:
        url = (page.url or "")[:200]
    except Exception:
        url = ""
    rec = {
        "When": time.strftime("%Y-%m-%d %H:%M:%S"),
        "Status": status_override or ("CONFIRMED" if laga else "NOT_CONFIRMED"),
        "Order_Ref": ref,
        "Account_Email": info.get("checkout_email") or acct.get("email", ""),
        "Customer_ID": acct.get("customer_id", ""),
        "Session_File": info.get("session_file", ""),
        "Ship_Name": ("%s %s" % (ad.get("first_name", ""),
                                 ad.get("last_name", ""))).strip(),
        "Address": ad.get("address1", ""),
        "Apartment": ad.get("address2", ""),
        "City": ad.get("city", ""),
        "State": ad.get("province", ""),
        "Pincode": ad.get("zip", ""),
        "Phone": ad.get("phone", ""),
        "Items": info.get("items", ""),
        "Cart_Value": info.get("amount", ""),
        "Discount_Code": info.get("discount", ""),
        "Paid": info.get("paid", ""),
        "Card_Last4": info.get("card_last4", ""),
        "Corp_ID": info.get("corp_id", ""),
        "Emp_ID": info.get("emp_id", ""),
        "OTP": info.get("otp", ""),
        "Payment_Row": info.get("pay_row", ""),
        "Input_Row": info.get("input_row", ""),
        "Product_Links": info.get("links", ""),
        "Checkout_URL": url,
        "Note": "" if laga else str(nateeja or "")[:180],
        "Acct_Order_No": info.get("acct_order_no", ""),
        "Order_Date": info.get("order_date", ""),
        "Payment_Status": info.get("payment_status", ""),
        "Order_Total": info.get("order_total", ""),
        "Order_URL": info.get("order_url", ""),
    }
    # Batch aur GUI ko jaanna hota hai ki abhi wale order ka kya bana. run_once
    # sirf ek number lautata hai (0 = chal gaya), jo "order laga ya nahi" nahi
    # batata. Isliye poora record yahan rakh dete hain.
    LAST_ORDER.clear()
    LAST_ORDER.update(rec)

    row = order_plan.append_order(ord_ws, rec)
    log("   [sheet] %s me line %s"
        % (order_plan.ORDER_TAB, ("row %d par likh di" % row) if row
           else "nahi ja payi"))
    return row if return_row else bool(row)


def wait_for_order(driver, page, acct, minutes=12, extra=None):
    marks = ("thank you", "order placed", "order confirmed", "order id",
             "your order", "order number")
    end = time.time() + minutes * 60
    log("      order ka intezaar (%d minute tak)..." % minutes)
    while time.time() < end:
        page.wait_for_timeout(5000)
        url = ""
        txt = ""
        hit = None
        for pg in pages(driver):
            try:
                u = pg.url or ""
                t = pg.body_text() or ""
            except Exception:
                continue
            if any(m in t.lower() for m in marks) or "/thank" in u or "/orders/" in u:
                url, txt, hit = u, t, pg
                break
        if not txt:
            continue

        # Shopify ke thank-you panne par number "Confirmation #0GXE3DAJ4" jaisa
        # hota hai -- akshar aur ank dono. Pehle sirf ank dhoonde jaate the,
        # isliye asli confirm hue order par bhi "number nahi mila" likha aata tha.
        ref = ""
        for pat in (r"confirmation\s*[:#]?\s*#?\s*([A-Z0-9]{6,})",
                    r"(?:order\s*(?:id|no\.?|number)\s*[:#]?\s*)([A-Za-z0-9#\-]{4,})",
                    r"#(\d{4,})"):
            m = re.search(pat, txt, re.I)
            if m:
                ref = m.group(1).strip("#")
                break

        try:
            hit.screenshot(os.path.join(OUT, "order_5_confirmed.png"))
        except Exception:
            pass

        # Session file me jo email likha hai wo hamesha sach nahi hota -- SMS
        # provider number dobara de de to purane Shopify account par hi login
        # ho jaata hai aur order KISI AUR email par darj hota hai. Isliye email
        # aur kul rakam dono thank-you panne se hi uthate hain.
        info = dict(extra or {})
        m = re.search(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", txt)
        asli_mail = m.group(0) if m else ""
        if asli_mail:
            info["checkout_email"] = asli_mail
            if asli_mail.lower() != str(acct.get("email", "")).lower():
                log("      CHETAVNI: order is email par gaya -- %s "
                    "(session file me %s likha hai)"
                    % (asli_mail, acct.get("email", "?")))
        # 'Total' ke turant baad ki rakam. Pehle ek hi patthar-jaisa regex tha
        # (total ke baad seedha rupya ka nishaan), par discount lagne par beech
        # me "Including taxes" jaisa text aa jaata hai aur match toot jaata hai
        # -- isi wajah se pichhle order me Paid khaali reh gaya tha. Ab 'Total'
        # ke aage ka thoda hissa lekar usme pehli rakam dhoondhte hain.
        low = txt.lower()
        k = low.rfind("total")
        if k >= 0:
            aage = txt[k:k + 200]
            m = re.search(r"₹\s?([\d,]+(?:\.\d+)?)", aage)
            if m:
                info["paid"] = m.group(1).replace(",", "")

        likho_order_row(acct, "CONFIRMED", ref or "(number nahi mila)", url,
                        info)
        return "ORDER LAG GAYA -- %s  (orders.csv me likh diya)" % (
            ref or "number nahi mila")

    return "itne me order confirm hota nahi dikha (chhod diya, kuch bigda nahi)"


# ================= SHOPIFY KA APNA (NATIVE) CHECKOUT =================
# /checkout par Fastrr ka iframe na aakar Shopify ka apna one-page checkout
# aata hai. Uske id har load par badalte hain (TextFieldP0-46, TextFieldP0-52...),
# isliye har khaana `name` aur `autocomplete` se pakda gaya hai -- wo sthir hain.


def is_shopify_checkout(page):
    """Ye Shopify ka apna checkout hai (Fastrr ka iframe nahi)?"""
    try:
        if "/checkouts/" in (page.url or ""):
            return True
    except Exception:
        pass
    try:
        return page.count('input[name="email"], input#email') > 0
    except Exception:
        return False


def _sh_put(page, sels, value, label, delay=40):
    """Ek khaana bharo -- asli keyboard ki tarah, ek ek akshar."""
    el = page.visible_first(sels)
    if el is None:
        log("      %s: khaana nahi mila" % label)
        return False
    page.use()
    try:
        page.d.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", el)
    except Exception:
        pass
    time.sleep(0.2)
    try:
        el.click()
    except Exception:
        pass
    el_fill(page, el, "")
    el_type(page, el, value, delay=delay)
    time.sleep(0.3)
    log("      %s -> %s" % (label, value))
    return True


def _sh_dismiss_dropdown(page, el):
    """Address wala khaana combobox hai -- uski suggestion list agle khaane ko
    dhak leti hai, isliye Escape se band kar dete hain."""
    try:
        page.use()
        el.send_keys(Keys.ESCAPE)
        time.sleep(0.3)
    except Exception:
        pass


def _sh_state(page, value):
    """State: pehle seedha <select>, warna combobox -- type karo, list me se chuno.

    User ne yahi kaha tha: 'type karna padega, keyboard signal jayega, phir wo
    choose karna hai'. Isliye value type hoti hai aur phir listbox me se milta
    hua option daba diya jaata hai.
    """
    # 1) purana checkout: seedha dropdown
    sel_el = page.first('select[name="zone"], select[name="province"], '
                        'select[name="provinceCode"]')
    if sel_el is not None:
        # select_by_visible_text chhote-bade akshar ka farak maanta hai. Sheet
        # me "uttar pradesh" likha tha aur dropdown me "Uttar Pradesh" -- isi
        # se state khaali reh gaya tha, aur khaali state par order galat jagah
        # ja sakta hai. Isliye milaan ab khud karte hain: chhote akshar me,
        # aage-peechhe ki jagah hataa kar.
        try:
            page.use()
            laga = page.d.execute_script(
                """const sel = arguments[0];
                   const want = String(arguments[1]).trim().toLowerCase();
                   let hit = null;
                   for (const o of sel.options) {
                     const t = (o.textContent || '').trim().toLowerCase();
                     if (t === want) { hit = o; break; }
                   }
                   if (!hit) {
                     for (const o of sel.options) {
                       const t = (o.textContent || '').trim().toLowerCase();
                       if (t && (t.indexOf(want) === 0 || want.indexOf(t) === 0)) {
                         hit = o; break;
                       }
                     }
                   }
                   if (!hit) return '';
                   sel.value = hit.value;
                   sel.dispatchEvent(new Event('input', {bubbles: true}));
                   sel.dispatchEvent(new Event('change', {bubbles: true}));
                   return (hit.textContent || '').trim();""",
                sel_el, value)
            if laga:
                log("      State -> %s (select)" % laga)
                return True
            log("      State: dropdown me '%s' jaisa kuch nahi mila" % value)
        except Exception as e:
            log("      State select fail: %s" % str(e)[:70])

    # 2) naya checkout: combobox
    el = page.visible_first(
        'input[autocomplete="shipping address-level1"], '
        'input[name="zone"], input[name="province"], input[name="state"]')
    if el is None:
        log("      State: khaana nahi mila")
        return False

    page.use()
    try:
        page.d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    except Exception:
        pass
    try:
        el.click()
    except Exception:
        pass
    el_fill(page, el, "")
    el_type(page, el, value, delay=60)
    time.sleep(1.2)

    # list me se milta hua option
    picked = None
    try:
        picked = page.evaluate(
            """const want = arguments[0].toLowerCase();
               const opts = [...document.querySelectorAll(
                   '[role="option"], [role="listbox"] li, ul[id*="listbox"] li')];
               const hit = opts.find(o => (o.innerText || '').toLowerCase()
                                            .includes(want));
               if (!hit) return null;
               hit.scrollIntoView({block: 'center'});
               hit.click();
               return (hit.innerText || '').trim().slice(0, 40);""", value)
    except Exception:
        picked = None

    if not picked:
        # list JS se nahi dabi to keyboard se: neeche + Enter
        try:
            page.use()
            el.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.4)
            el.send_keys(Keys.ENTER)
            picked = "(keyboard)"
        except Exception:
            pass

    time.sleep(0.6)
    log("      State -> %s %s" % (value, "[%s]" % picked if picked else "(chuna nahi gaya)"))
    return bool(picked)


def _sh_discount(page, code):
    """Discount code bharo aur Apply dabao.

    Khaane ka id har load par badal jaata hai (ReductionsInputP0-122,
    ReductionsInputP0-139...), isliye use `name="reductions"` se pakda jaata
    hai -- wo sthir hai. Button ka bharosemand nishaan uska
    data-event-name="apply_discount" hai; uske class ke naam bhi har build par
    badalte rehte hain.

    Ye payment se PEHLE lagta hai, kyunki discount lagte hi kul rakam badalti
    hai -- aur gateway par wahi rakam jaati hai.
    """
    if not code:
        return None                      # koi code hi nahi diya -- chhod do

    el = page.visible_first('input[name="reductions"], '
                            'input[placeholder="Test Holder"]')
    if el is None:
        log("      discount: khaana nahi mila")
        return False

    page.use()
    try:
        page.d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    except Exception:
        pass
    time.sleep(0.2)
    try:
        el.click()
    except Exception:
        pass
    el_fill(page, el, "")
    el_type(page, el, code, delay=60)
    time.sleep(0.4)

    btn = page.visible_first('button[data-event-name="apply_discount"], '
                             'button[aria-label="Apply Discount Code"]')
    if btn is None:
        # button na mile to Enter bhi kaam kar jaata hai
        try:
            el.send_keys(Keys.ENTER)
            log("      discount '%s' -- Enter se bheja" % code)
        except Exception:
            log("      discount: Apply ka button nahi mila")
            return False
    else:
        how = scroll_click(page, btn)
        log("      discount '%s' -- Apply daba diya (%s)" % (code, how or "nahi daba"))

    page.wait_for_timeout(4000)

    # Laga ya nahi? Shopify galat code par saaf sandesh dikhata hai.
    try:
        txt = (page.body_text() or "").lower()
    except Exception:
        txt = ""
    for bura in ("isn't valid", "is not valid", "can't be used", "cannot be used",
                 "expired", "not available", "enter a valid discount"):
        if bura in txt:
            log("      CHETAVNI: discount code laga nahi -- panne par '%s'" % bura)
            return False
    log("      discount lag gaya lagta hai")
    return True


def _sh_payment_method(page, hint="easebuzz"):
    """Payment ke tareekon me se Easebuzz wala chuno.

    Iska koi sthir id/class nahi mila, isliye likhe hue naam se dhoondha jaata
    hai -- sabse chhota element jisme wo naam ho (yaani sabse andar wala), taaki
    poora payment section click na ho jaye.
    """
    try:
        got = page.evaluate(
            """const want = arguments[0].toLowerCase();
               const nodes = [...document.querySelectorAll(
                   'label, li, button, [role="radio"], div')];
               const hits = nodes.filter(e => ((e.innerText || '').toLowerCase()
                                                 .includes(want))
                                          && e.getClientRects().length);
               if (!hits.length) return null;
               hits.sort((a, b) => (a.innerText || '').length
                                 - (b.innerText || '').length);
               const box = hits[0];
               const radio = box.querySelector('input[type=radio]');
               (radio || box).click();
               return (box.innerText || '').trim().slice(0, 60);""", hint)
    except Exception as e:
        log("      payment method dhoondhne me dikkat: %s" % str(e)[:60])
        got = None

    if got:
        log("      payment method -> %s" % got.replace("\n", " / "))
        time.sleep(2.0)
        return True

    log("      '%s' wala payment method nahi mila" % hint)
    return False


def _sh_pay_now(page):
    """'Pay now' dabao."""
    for sel in ('button#checkout-pay-button',
                'button:has-text("Pay now")',
                'button:has-text("Pay Now")',
                'button:has-text("Complete order")',
                'button[type="submit"]:has-text("Pay")'):
        try:
            el = page.visible_first(sel)
            if el is None:
                continue
            how = scroll_click(page, el)
            if how:
                log("      Pay now daba diya (%s | %s)" % (how, sel))
                return True
        except Exception:
            continue
    log("      'Pay now' ka button nahi mila")
    return False


def fill_shopify_checkout(page, acct, do_pay=True, pay_hint="easebuzz",
                          discount=""):
    """Shopify ke apne checkout ka poora form + payment method + Pay now.

    Values abhi session ke pate se aati hain; jo na ho uske liye neeche wale
    default lag jaate hain. Baad me asli values aane par sirf ye do jagah
    badalni hongi.
    """
    # form ke aane ka intezaar
    for _ in range(20):
        if page.count('input[name="email"], input#email, input[name="firstName"]'):
            break
        page.wait_for_timeout(1500)
    else:
        return "FAIL: Shopify checkout ka form nahi aaya"

    ad = acct.get("address") or {}
    email = acct.get("email") or "test@example.com"
    first = ad.get("first_name") or "Ishan"
    last = ad.get("last_name") or "Gupta"
    line1 = ad.get("address1") or "55/34 Shastri Nagar"
    line2 = ad.get("address2") or "Near Kidwai Nagar Market"
    city = ad.get("city") or "Kanpur"
    state = ad.get("province") or "Uttar Pradesh"
    pin = ad.get("zip") or "000000"
    phone = ad.get("phone") or acct.get("phone") or "9999999999"

    ok = {}
    ok["email"] = _sh_put(page, 'input#email, input[name="email"], '
                                'input[autocomplete="shipping email"]',
                          email, "Email")

    ok["first"] = _sh_put(page, 'input[name="firstName"], '
                                'input[autocomplete="shipping given-name"]',
                          first, "First name")

    ok["last"] = _sh_put(page, 'input[name="lastName"], '
                               'input[autocomplete="shipping family-name"]',
                         last, "Last name")

    # address1 combobox hai -- likhne ke baad uski list band karni padti hai
    addr_el = page.visible_first('input#shipping-address1, input[name="address1"], '
                                 'input[autocomplete="shipping address-line1"]')
    if addr_el is not None:
        ok["address1"] = _sh_put(page, 'input#shipping-address1, '
                                       'input[name="address1"], '
                                       'input[autocomplete="shipping address-line1"]',
                                 line1, "Address")
        _sh_dismiss_dropdown(page, addr_el)
    else:
        ok["address1"] = False
        log("      Address: khaana nahi mila")

    ok["address2"] = _sh_put(page, 'input[name="address2"], '
                                   'input[autocomplete="shipping address-line2"]',
                             line2, "Apartment")

    ok["city"] = _sh_put(page, 'input[name="city"], '
                               'input[autocomplete="shipping address-level2"]',
                         city, "City")

    ok["state"] = _sh_state(page, state)

    ok["pin"] = _sh_put(page, 'input[name="postalCode"], '
                              'input[autocomplete="shipping postal-code"]',
                        pin, "PIN code")

    ok["phone"] = _sh_put(page, 'input[name="phone"], '
                                'input[autocomplete="shipping tel-national"], '
                                'input[type="tel"]',
                          phone, "Phone")

    page.wait_for_timeout(2500)
    try:
        page.screenshot(os.path.join(OUT, "order_3b_form_filled.png"))
        log("      tasveer: out/order_3b_form_filled.png")
    except Exception:
        pass

    # Discount payment se PEHLE -- warna gateway par purani rakam chali jaati.
    got = _sh_discount(page, discount)
    if got is not None:
        ok["discount"] = got

    ok["payment"] = _sh_payment_method(page, pay_hint)
    page.wait_for_timeout(2000)

    ok["pay_now"] = _sh_pay_now(page) if do_pay else False
    if do_pay:
        page.wait_for_timeout(8000)

    return " | ".join("%s=%s" % (k, "ok" if v else "FAIL") for k, v in ok.items())


def parse_args(argv=None):
    """Command padho. GUI apni list bana kar de sakta hai."""
    ap = argparse.ArgumentParser()
    # --product ya --link, do me se ek. Purane command na tootein isliye
    # --product ka roop waisa hi hai, bas ab zaroori nahi raha.
    ap.add_argument("--product", default="")
    ap.add_argument("--link", action="append", default=[],
                    help="product ka link (kai baar de sakte ho) -- inhi se cart banega")
    ap.add_argument("--cart-max", type=float, default=5000.0,
                    help="ek account par cart ki sabse zyada keemat")
    ap.add_argument("--cart-min", type=float, default=0.0,
                    help="cart ki sabse kam keemat (0 = --cart-max ka 60%%)")
    ap.add_argument("--cart-seed", type=int, default=None,
                    help="wahi cart dobara banane ke liye")
    # ---- sheet se pata aur card ----
    ap.add_argument("--from-sheet", action="store_true",
                    help="pata Input_details se aur card payment_details se lo")
    ap.add_argument("--pay-tab", default=os.environ.get("ESTUARY_PAY_TAB", ""),
                    help="card kis tab se (jaise System_1). khali = payment_details")
    ap.add_argument("--avoid-emp", action="append", default=[],
                    help="ye employee id is run me pehle use ho chuki -- inse "
                         "alag card do (batch/combo bharte hain)")
    ap.add_argument("--order-no", type=int, default=0,
                    help="kaunsa order (0,1,2...) -- isi se pata ghoomta hai")
    ap.add_argument("--discount", default="",
                    help="checkout par lagane ka discount code")
    ap.add_argument("--phone", action="append", default=[],
                    help="phone number (kai baar de sakte ho) -- ye BADLE nahi jaate, bas kram se ghoomte hain")
    ap.add_argument("--pack", default="")
    ap.add_argument("--unit", default="")
    ap.add_argument("--session", default="")
    ap.add_argument("--show", action="store_true")
    # Headless BAND hai. Bank/ACS ka panna aur gateway bina window ke theek se
    # nahi chalte -- 'Loading Bank Page' wahin atak jaata hai. Flag isliye rakha
    # hai ki purane command na toote; ye ab kuch karta nahi.
    ap.add_argument("--headless", action="store_true",
                    help="(band kar diya gaya -- browser hamesha window ke saath)")
    ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
    ap.add_argument("--card", default=DEFAULT_CARD)
    ap.add_argument("--exp", default=DEFAULT_EXP)
    ap.add_argument("--holder", default=DEFAULT_HOLDER)
    ap.add_argument("--cvv", default=DEFAULT_CVV)
    ap.add_argument("--no-pay-click", action="store_true",
                    help="gateway ka Pay mat dabao -- tum khud dabaoge")
    ap.add_argument("--auto-pay", action="store_true",
                    help="(ab default hi yahi hai -- rakha hai taaki purane "
                         "command chalte rahein)")
    ap.add_argument("--manual-pay", action="store_true", default=True,
                    help="(ab bemaani -- Pay rokna ho to --no-pay-click do)")
    ap.add_argument("--corp-id", default=DEFAULT_CORP_ID)
    ap.add_argument("--emp-id", default=DEFAULT_EMP_ID)
    # ---- OTP ----
    ap.add_argument("--manual-otp", action="store_true",
                    help="OTP tum bharo (API se nahi); SUBMIT script dabayegi")
    ap.add_argument("--otp-emp-id", default="",
                    help="API me employee id (khali = --emp-id wahi hai)")
    ap.add_argument("--otp-api-url", default=OTP_API_URL,
                    help="OTP API ka pata ({API_EMPLOYEE_ID} badal jaata hai)")
    ap.add_argument("--otp-token", default=OTP_FETCH_TOKEN,
                    help="OTP API ka token (bina token API call nahi hogi)")
    ap.add_argument("--watch", type=int, default=0)
    ap.add_argument("--hold", type=int, default=60)
    ap.add_argument("--proxy", action="store_true", default=True,
                    help="Geonode India residential (default ON)")
    ap.add_argument("--no-proxy", action="store_true",
                    help="proxy band")
    ap.add_argument("--proxy-country", default=GEONODE_COUNTRY)
    ap.add_argument("--keep-cart", action="store_true",
                    help="cart pehle se bhara ho to use rehne do (default: khaali karo)")
    ap.add_argument("--no-save-session", action="store_true",
                    help="band karte waqt taaza cookies session file me mat likho")
    a = ap.parse_args(argv)
    return a


def run_once(a):
    """Ek order lagao. `a` parse_args() se aata hai.

    Lautata hai: 0 = kaam ho gaya, baaki sab galti ka number.
    """

    if a.headless:
        log("(--headless ab kaam nahi karta -- browser window ke saath hi chalega)")
    a.headless = False          # har haal me headed

    path = a.session or newest_session()
    if not path:
        log("koi session nahi mili -- pehle make_accounts.py chalao")
        return 1
    if not os.path.isabs(path):
        p2 = os.path.join(SESSIONS, path)
        path = p2 if os.path.exists(p2) else path
    d = json.load(open(path, encoding="utf-8"))
    log("account : %s / %s" % (d.get("phone"), d.get("email")))
    if not d.get("address"):
        log("CHETAVNI: is account par pata darj nahi hai -- pehle add_address.py chalao")

    # ---------------- sheet se pata aur card ----------------
    # Ye session load hone ke turant baad hota hai, browser khulne se PEHLE.
    # Wajah: agar sheet me card hi na bache ho to browser kholna, proxy uthana
    # aur cart banana sab bekaar mehnat hai -- yahin ruk jana behtar hai.
    pay_ws = None
    pay_row = 0
    ord_ws = None
    if a.from_sheet:
        in_ws, kahani = order_plan.open_input_tab()
        log("sheet : Input_details -> %s" % kahani)
        if in_ws is None:
            log("FAIL: pata nahi mila -- --from-sheet ke bina chalao")
            return 1
        rows = order_plan.read_inputs(in_ws)
        idn = order_plan.make_identity(rows, a.order_no, seed=a.cart_seed,
                                       phones=a.phone or None)
        # place_order ka poora checkout pehle se hi acct["address"] padhta hai,
        # isliye yahi ek jagah bharna kaafi hai -- form bharne wala code
        # chhedna nahi pada.
        d["address"] = idn
        # Discount code sheet ke Discount Code column se, har baar random.
        # Command line par --discount diya ho to wahi jeetta hai.
        if not a.discount and idn.get("discount"):
            a.discount = idn["discount"]
            log("code  : %s (sheet se, random)" % a.discount)
        log("pata  : %s %s | %s | %s | %s %s - %s | ph %s"
            % (idn["first_name"], idn["last_name"], idn["address1"],
               idn["address2"], idn["city"], idn["province"], idn["zip"],
               idn["phone"] or "(sheet me koi phone nahi)"))
        if not idn["phone"]:
            log("CHETAVNI: phone kahin se nahi mila -- checkout atak sakta hai."
                " --phone 9999999999 de dijiye")

        pay_ws, kahani = order_plan.open_pay_tab(tab=a.pay_tab or None)
        log("sheet : card tab '%s' -> %s"
            % (a.pay_tab or order_plan.PAY_TAB, kahani))
        if pay_ws is None:
            log("FAIL: card nahi mile -- --from-sheet ke bina chalao")
            return 1
        # Card aisa chuno jiska employee id abhi kahin aur na chal raha ho --
        # OTP employee id ke number par aata hai, isliye ek waqt me ek hi
        # transaction ek emp id par. claim_next_card yahi pakka karta hai aur
        # chunte hi row ko 'RUNNING' bhi kar deta hai (alag se claim ki zaroorat
        # nahi). --avoid-emp me wo id hain jo isi run me pehle le chuke.
        card = order_plan.claim_next_card(pay_ws, avoid_emps=a.avoid_emp)
        if not card:
            log("FAIL: is tab me koi aisa bina-use card nahi bacha jiska "
                "employee id free ho (baaki abhi chal rahe hain ya khatam)")
            return 1
        pay_row = card["row"]
        a.card, a.exp = card["card"], card["exp"]
        a.holder = card["holder"] or a.holder
        a.cvv = card["cvv"]
        a.corp_id = card["corp_id"] or a.corp_id
        a.emp_id = card["emp_id"] or a.emp_id
        log("card  : row %d | ****%s | %s | corp=%s emp=%s%s"
            % (pay_row, a.card[-4:], a.exp, a.corp_id, a.emp_id,
               " (id upar wali row se)" if card["virasat"] else ""))

        ord_ws, kahani = order_plan.open_orders_tab()
        log("sheet : %s -> %s" % (order_plan.ORDER_TAB, kahani))

    use_proxy = not a.no_proxy
    stop_bridge = None
    bridge_port = None
    if use_proxy:
        proxy_user = geonode_username(a.proxy_country, sticky=False)
        log("proxy : Geonode country=%s | user=%s" % (a.proxy_country, proxy_user))
        try:
            bridge_port, stop_bridge = start_geonode_bridge(proxy_user)
            log("proxy : local bridge 127.0.0.1:%d" % bridge_port)
        except Exception as e:
            log("proxy FAIL (%s) -- bina proxy chalega" % e)
            use_proxy = False
            bridge_port = None

    driver = None
    try:
        try:
            driver = launch_waterfox(proxy_port=bridge_port, headless=a.headless)
            log("browser: WATERFOX (geckodriver) -- Chrome/CDP nahi")
        except Exception as e:
            log("FAIL: Waterfox nahi khuli: %s" % e)
            log("  1) D:\\streakads\\Waterfox\\waterfox.exe hona chahiye")
            log("  2) ya set: WATERFOX_PATH / GECKODRIVER_PATH")
            if stop_bridge is not None:
                stop_bridge.set()
            return 2

        log("   session (cookies + localStorage) daal rahe hain...")
        daale = 0
        try:
            daale = load_session(driver, d)
        except Exception as e:
            log("   session load me dikkat: %s" % str(e)[:120])
        if not daale:
            # Ek bhi cookie na jaane ka matlab hai account logged-out hai. Aage
            # badhne par order to lag jaata hai par kisi account se nahi juda
            # hota -- aur pata chalta hai tab, jab paisa kat chuka hota hai.
            log("   RUKO: ek bhi cookie nahi gayi -- ye account logged-out hai.")
            log("   (proxy/network ki wajah se site nahi khuli. Dobara chalao.)")
            try:
                driver.quit()
            except Exception:
                pass
            driver = None          # finally me session dobara likhne ki koshish na ho
            if stop_bridge is not None:
                stop_bridge.set()
            return 2

        page = Scope(driver, driver.current_window_handle)

        # Links wale raaste me kisi ek product ka panna kholne ka matlab
        # nahi -- cart AJAX se banta hai. Par domain par khada hona
        # zaroori hai, warna /cart/add.js chalega hi nahi. Isliye ghar ka
        # panna khol lete hain.
        if a.link:
            log("\n1) dukaan khol rahe hain (cart links se banega)")
            pehla_url = SHOP + "/"
        else:
            log("\n1) product khol rahe hain: %s" % a.product)
            pehla_url = "%s/products/%s" % (SHOP, a.product)
        nav_ok = False
        last_err = None
        for attempt in range(1, 4):
            try:
                page.goto(pehla_url, timeout=120)
                nav_ok = True
                break
            except Exception as e:
                last_err = e
                log("   goto fail try %d/3: %s" % (attempt, str(e)[:120]))
                page.wait_for_timeout(2000)

        if not nav_ok and use_proxy:
            # proxy se nahi chala -> bina proxy retry (Waterfox ko naye sire se
            # kholna padta hai, proxy pref launch ke waqt tay hoti hai)
            log("   proxy se site nahi khuli -- bina proxy retry...")
            try:
                driver.quit()
            except Exception:
                pass
            if stop_bridge is not None:
                stop_bridge.set()
                stop_bridge = None
            use_proxy = False
            try:
                driver = launch_waterfox(proxy_port=None, headless=a.headless)
                load_session(driver, d)
                page = Scope(driver, driver.current_window_handle)
                page.goto(pehla_url, timeout=120)
                nav_ok = True
                log("   bina proxy OK (bank page baad me fail ho sakti hai)")
            except Exception as e:
                last_err = e

        if not nav_ok:
            log("FAIL: product page nahi khuli: %s" % last_err)
            try:
                driver.quit()
            except Exception:
                pass
            if stop_bridge is not None:
                stop_bridge.set()
            return 2

        page.wait_for_timeout(5000)
        for _ in range(3):
            page.evaluate("window.scrollBy(0, 900);")
            page.wait_for_timeout(700)

        if not a.link:
            title = (page.title() or "").split("|")[0].strip()
            log("   %s" % title)
            before = variant_id(page)
            log("   abhi ka variant: %s" % before)

            if a.unit:
                log("2) unit chun rahe hain: %s" % a.unit)
                if not pick(page, a.unit):
                    log("   (ye unit is panne par nahi mila -- aage badh rahe hain)")
            if a.pack:
                log("3) pack chun rahe hain: %s" % a.pack)
                if not pick(page, a.pack):
                    log("   FAIL: ye pack is panne par nahi mila")
                    page.screenshot(os.path.join(OUT, "order_fail_pack.png"),
                                    full_page=True)
                    driver.quit()
                    return 3

            after = variant_id(page)
            log("   chunne ke baad variant: %s%s"
                % (after, "  (badal gaya)" if after != before else "  (wahi hai)"))
            page.screenshot(os.path.join(OUT, "order_1_product.png"))

            # Session ke saath purana cart bhi wapas aa jaata hai. Ek asli run me
            # isi wajah se ek item maangne par cart me DO chale gaye the (Rs 160 ki
            # jagah Rs 320). Har order apne aap me poora hona chahiye, warna
            # Rs 2000-per-account ka hisaab hi galat ho jayega.
            if not a.keep_cart:
                purana = page.evaluate_async(
                    "const cb = arguments[arguments.length - 1];"
                    "fetch('/cart.js').then(r => r.json()).then(j => cb(j))"
                    ".catch(e => cb(null));") or {}
                if purana.get("item_count"):
                    log("   cart me pehle se %d cheez thi (Rs %s) -- khaali kar rahe hain"
                        % (purana.get("item_count", 0),
                           (purana.get("total_price", 0) or 0) / 100))
                    page.evaluate_async(
                        "const cb = arguments[arguments.length - 1];"
                        "fetch('/cart/clear.js', {method:'POST'})"
                        ".then(r => r.json()).then(j => cb(true)).catch(e => cb(false));")
                    page.wait_for_timeout(1500)

            log("4) add to cart")
            sel = find(page, ADD_TO_CART)
            if not sel:
                log("   FAIL: 'Add to cart' ka button nahi mila")
                driver.quit()
                return 4
            el = page.first(sel)
            if not scroll_click(page, el):
                log("   FAIL: 'Add to cart' daba nahi paye")
                driver.quit()
                return 4
            page.wait_for_timeout(6000)
            page.screenshot(os.path.join(OUT, "order_2_added.png"))

            cart = page.evaluate_async(
                "const cb = arguments[arguments.length - 1];"
                "fetch('/cart.js').then(r => r.json()).then(j => cb(j))"
                ".catch(e => cb(null));") or {}
            log("   cart me cheezein: %d | kul Rs %s"
                % (cart.get("item_count", 0), (cart.get("total_price", 0) or 0) / 100))
            for it in cart.get("items", []):
                log("      %s | %s | Rs %s"
                    % (it.get("product_title"), it.get("variant_title"),
                       (it.get("line_price", 0) or 0) / 100))
            if not cart.get("item_count"):
                log("   FAIL: cart khaali hi rah gaya")
                driver.quit()
                return 5
            if after and str(cart["items"][0].get("variant_id")) != str(after):
                log("   CHETAVNI: cart me doosra variant gaya hai (%s) -- dekh lijiye"
                    % cart["items"][0].get("variant_id"))


        else:
            # ---------------- links se cart ----------------
            # Yahan product ka panna kholte hi nahi. Har link ka JSON
            # (/products/<handle>.js) pehle padh liya jaata hai, isliye variant
            # id aur daam haath me hote hain -- unhe seedha /cart/add.js par
            # bhej dete hain. Teen faayde: pack chunne ka jhamela nahi, kai
            # product ek saath, aur cart ki keemat pehle se tay.
            lo = a.cart_min or round(a.cart_max * 0.6, 2)
            log("2) links se cart chun rahe hain (Rs %.2f -- Rs %.2f)"
                % (lo, a.cart_max))
            saare = order_plan.variants_from_links(a.link, log=log)
            if not saare:
                log("   FAIL: kisi bhi link se pack nahi mila "
                    "(sab out of stock ho sakte hain)")
                driver.quit()
                return 4
            chune, kul = order_plan.pick_cart(saare, lo, a.cart_max,
                                              seed=a.cart_seed)
            if not chune:
                log("   FAIL: is range me cart nahi ban paya. Sabse sasta "
                    "pack Rs %.2f ka hai -- range badhaiye."
                    % min(v["price"] for v in saare))
                driver.quit()
                return 4
            log("   chuna gaya -- kul Rs %.2f:" % kul)
            for it in chune:
                log("      %-38s %-12s x%d  Rs %8.2f"
                    % (it["product"][:38], it["variant_name"][:12],
                       it["quantity"], it["price"] * it["quantity"]))

            # Session ke saath purana cart bhi lautta hai. Use hatana zaroori
            # hai, warna keemat range se bahar nikal jayegi.
            if not a.keep_cart:
                purana_cart = page.evaluate_async(
                    "const cb = arguments[arguments.length - 1];"
                    "fetch('/cart.js').then(r => r.json()).then(j => cb(j))"
                    ".catch(e => cb(null));") or {}
                if purana_cart.get("item_count"):
                    log("   cart me pehle se %d cheez thi (Rs %s) -- hata rahe hain"
                        % (purana_cart.get("item_count", 0),
                           (purana_cart.get("total_price", 0) or 0) / 100))
                    page.evaluate_async(
                        "const cb = arguments[arguments.length - 1];"
                        "fetch('/cart/clear.js', {method:'POST'})"
                        ".then(r => r.json()).then(j => cb(true))"
                        ".catch(e => cb(false));")
                    page.wait_for_timeout(1500)

            log("3) cart me daal rahe hain")
            # Ek-ek karke bheja jaata hai. Ek saath bhejne par ek bhi variant
            # out-of-stock nikle to POORA call fail hota hai; ek-ek me sirf
            # wahi item chhoot ta hai aur pata bhi chal jaata hai kaun chhoota.
            for it in chune:
                res = page.evaluate_async(
                    "const cb = arguments[arguments.length - 1];"
                    "fetch('/cart/add.js', {method: 'POST',"
                    " headers: {'Content-Type': 'application/json'},"
                    " body: JSON.stringify({items: [{id: arguments[0],"
                    " quantity: arguments[1]}]})})"
                    ".then(r => r.json().then(j => cb({ok: r.ok, body: j})))"
                    ".catch(e => cb({ok: false, body: String(e)}));",
                    it["variant_id"], it["quantity"])
                if res and res.get("ok"):
                    log("      + %-38s %-12s x%d"
                        % (it["product"][:38], it["variant_name"][:12],
                           it["quantity"]))
                else:
                    kyun = ""
                    if isinstance(res, dict):
                        b = res.get("body")
                        kyun = ((b.get("description") or b.get("message") or "")
                                if isinstance(b, dict) else str(b))[:70]
                    log("      x %-38s %-12s -- %s"
                        % (it["product"][:38], it["variant_name"][:12],
                           kyun or "nahi gaya"))
                page.wait_for_timeout(700)

            log("4) cart padh rahe hain")
            cart = page.evaluate_async(
                "const cb = arguments[arguments.length - 1];"
                "fetch('/cart.js').then(r => r.json()).then(j => cb(j))"
                ".catch(e => cb(null));") or {}
            log("   cart me cheezein: %d | kul Rs %s"
                % (cart.get("item_count", 0),
                   (cart.get("total_price", 0) or 0) / 100))
            for it in cart.get("items", []):
                log("      %s | %s x%s | Rs %s"
                    % (it.get("product_title"), it.get("variant_title"),
                       it.get("quantity"),
                       (it.get("line_price", 0) or 0) / 100))
            if not cart.get("item_count"):
                log("   FAIL: cart khaali hi rah gaya")
                driver.quit()
                return 5
            asli = (cart.get("total_price", 0) or 0) / 100.0
            if asli > a.cart_max:
                log("   CHETAVNI: cart Rs %.2f ka hai, hadd Rs %.2f thi"
                    % (asli, a.cart_max))

        # orders.csv me kya-kya jayega -- yahin bhar lete hain, kyunki cart ki
        # jaankari sirf isi jagah taaza hai (checkout par jaate hi badal sakti hai).
        order_info = {
            "session_file": os.path.basename(path),
            "amount": "%.2f" % ((cart.get("total_price", 0) or 0) / 100.0),
            "items": " + ".join(
                "%s (%s) x%s" % (it.get("product_title"),
                                 it.get("variant_title"),
                                 it.get("quantity", 1))
                for it in cart.get("items", [])),
            "card_last4": str(a.card).replace(" ", "")[-4:],
            "discount": a.discount,
            "corp_id": a.corp_id,
            "emp_id": a.emp_id,
            "pay_row": pay_row,
            "input_row": (d.get("address") or {}).get("sheet_row", ""),
            "links": " | ".join(a.link),
            "product": (a.product or ", ".join(
                order_plan.handle_from_link(l) for l in a.link)),
            "otp": "",
        }

        log("5) cart")
        page.screenshot(os.path.join(OUT, "order_3_cart.png"))

        # Cart ka sidebar kholna aur us par Checkout ka button dhoondhna chhod
        # diya -- add to cart ke turant baad seedha /checkout par jaate hain.
        log("6) Checkout: %s/checkout par ja rahe hain" % SHOP)
        khule_the = set(driver.window_handles)
        try:
            page.goto("%s/checkout" % SHOP, timeout=120)
        except Exception as e:
            log("   goto fail: %s" % str(e)[:120])
        page.wait_for_timeout(8000)

        landed = page.url or ""
        log("   pahunche: %s" % landed[:120])

        # /checkout kabhi wapas /cart ya home par phenk deta hai (cart khaali
        # rah gaya, ya session nahi pehchana). Tab purana tareeka: cart kholo,
        # Checkout ka button dabao.
        if "/checkout" not in landed:
            log("   /checkout ne wapas bhej diya -- Checkout button se koshish")
            sel = find(page, CHECKOUT)
            if not sel:
                sel_open = find(page, CART_OPEN)
                if sel_open:
                    log("      cart khol rahe hain")
                    scroll_click(page, page.first(sel_open))
                    page.wait_for_timeout(5000)
                    sel = find(page, CHECKOUT)
            if not sel:
                log("   FAIL: Checkout ka button bhi nahi mila")
                page.screenshot(os.path.join(OUT, "order_fail_checkout.png"),
                                full_page=True)
                driver.quit()
                return 6
            btn = page.first(sel)
            expect_new_page(driver, lambda: scroll_click(page, btn), timeout=15)
            page.wait_for_timeout(8000)

        # Checkout nayi window/tab me khula ho to aage ka saara kaam usi par
        naye = set(driver.window_handles) - khule_the
        pay = Scope(driver, naye.pop()) if naye else page
        pay.use()
        pay.wait_for_timeout(12000)
        try:
            pay.screenshot(os.path.join(OUT, "order_3_checkout.png"))
            log("   tasveer: out/order_3_checkout.png")
        except Exception:
            pass

        blk = clear_blocker(pay)
        if blk:
            log("   %s" % blk)

        # /checkout do me se ek cheez deta hai:
        #   a) Fastrr ka iframe (fastrr-boost-ui.pickrr.com) -- purana raasta
        #   b) Shopify ka apna one-page checkout -- ab yahi aata hai
        # Dono ke form bilkul alag hain, isliye pehle ye tay hota hai ki panne
        # par hai kya, phir usi ke hisaab se step 7-9 chalte hain.
        fr_list = frames(pay)
        log("   checkout ka panna: %s" % (pay.url or "")[:100])
        log("   frames (%d): %s" % (
            len(fr_list),
            ", ".join((f.url or "?")[:60] for f in fr_list[:5]) or "koi nahi"))

        fastrr = any("fastrr-boost-ui.pickrr.com" in (f.url or "") for f in fr_list)
        native = (not fastrr) and is_shopify_checkout(pay)
        log("   checkout ka tareeka: %s" % (
            "Fastrr (iframe)" if fastrr else
            "Shopify ka apna form" if native else "pehchana nahi gaya"))

        if native:
            # ---- Shopify ka apna checkout: pura form + Easebuzz + Pay now ----
            log("7) Shopify checkout ka form bhar rahe hain")
            log("      %s" % fill_shopify_checkout(
                pay, d, do_pay=True, pay_hint="easebuzz",
                discount=a.discount))
            pay.wait_for_timeout(5000)
            log("8) email confirm -- Shopify ke form me email upar hi bhar diya")
            log("9) payment method -- Easebuzz form me hi chun liya")
            try:
                pay.screenshot(os.path.join(OUT, "order_3c_after_pay_now.png"))
                log("   tasveer: out/order_3c_after_pay_now.png")
            except Exception:
                pass
        elif fastrr:
            log("7) checkout ka apna pata")
            ship = ship_address(pay, d)
            log("      %s" % ship)
            pay.wait_for_timeout(6000)

            log("8) email confirm")
            log("      %s" % confirm_email(pay, d))
            pay.wait_for_timeout(4000)

            st = read_checkout(pay)
            if st:
                log("   checkout par abhi:")
                if st["address"]:
                    for l in st["address"]:
                        log("      pata: %s" % l[:90])
                else:
                    log("      pata: panne par koi pincode nahi dikha")
                if st["pay"]:
                    log("      payment ke tareeke: %s" % ", ".join(st["pay"])[:200])
                if st["total"]:
                    log("      panne ka aakhri daam: Rs %s" % st["total"])
            else:
                log("   (checkout ka frame nahi mila -- neeche ki tasveer dekhiye)")

            log("9) Credit/Debit Card chun rahe hain")
            log("      %s" % pick_card(pay))
            pay.wait_for_timeout(5000)
        else:
            log("   CHETAVNI: na Fastrr ka frame mila na Shopify ka form --"
                " step 7 se 9 chhod rahe hain")
            try:
                pay.screenshot(os.path.join(OUT, "order_fail_checkout_frame.png"),
                               full_page=True)
                log("   tasveer: out/order_fail_checkout_frame.png")
            except Exception:
                pass

        log("10) gateway par %s Card chun rahe hain" % a.card_type)
        log("      %s" % pick_card_type(pay, a.card_type))
        pay.wait_for_timeout(3000)

        # Gateway ka Pay ab script khud dabati hai. Pehle ye sirf --auto-pay par
        # hota tha, isliye script card bhar kar chup baith jaati thi.
        # Rokna ho to: --no-pay-click
        click_pay = not a.no_pay_click
        log("11) Card details fill (Pay click=%s)" % click_pay)
        log("      %s" % fill_card_details(
            pay, a.card, a.exp, a.holder, a.cvv,
            click_pay=click_pay,
        ))

        if not click_pay:
            log("\n==========================================================")
            log("   CARD FILL HO GAYA. Pay aap MANUALLY dabaiye.")
            log("   Jab Corporate/Employee form dikhe -> yahan Enter dabao")
            log("==========================================================")
            try:
                input("👉 Bank form dikhne ke baad Enter: ")
            except Exception:
                pay.wait_for_timeout(120000)
        else:
            # Pay ke baad bank ka panna aane me der lagti hai -- 'Loading Bank
            # Page' kai baar 20-30 second khada rehta hai. Agla step khud 120s
            # tak intezaar karta hai, yahan bas thoda saans lene ka waqt.
            pay.wait_for_timeout(10000)

        log("12) Bank Corporate / Employee ID")
        log("      %s" % fill_bank_corporate(driver, pay, a.corp_id, a.emp_id))
        pay.wait_for_timeout(2000)

        log("13) OTP (%s)" % ("tum bharoge" if a.manual_otp else "API se"))
        otp_msg = do_otp(driver,
                         a.otp_emp_id or a.emp_id,
                         card_no=a.card,
                         manual=a.manual_otp,
                         api_url=a.otp_api_url,
                         token=a.otp_token,
                         record=order_info)
        log("      %s" % otp_msg)
        pay.wait_for_timeout(3000)

        log("\n   URL: %s" % pay.url)
        try:
            txt = pay.body_text() or ""
        except Exception:
            txt = ""
        lines = [l.strip() for l in txt.splitlines() if l.strip()][:16]
        log("   panne par: %s" % " | ".join(lines)[:260])
        rup = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", txt)
        log("   panne par daam: %s" % (sorted(set(rup))[:8] or "koi nahi"))
        try:
            pay.screenshot(os.path.join(OUT, "order_4_payment.png"))
            log("   tasveer: out/order_4_payment.png")
        except Exception as e:
            log("   (tasveer nahi bani: %s)" % str(e)[:60])

        # OTP submit hua ya nahi -- do_otp ka jawab isi se pata chalta hai.
        # "OTP ho gaya" (API raah) ya "SUBMIT daba diya" (manual raah) = submit
        # ho gaya. Baaki matlab submit hi nahi hua (khaana/button nahi mila,
        # ya OTP nahi aaya).
        otp_ok = ("OTP ho gaya" in otp_msg) or ("SUBMIT daba diya" in otp_msg)
        order_info["otp_submitted"] = "haan" if otp_ok else "nahi"
        log("\n   OTP SUBMIT: %s" % ("SAFAL" if otp_ok else "NAHI HUA"))

        # ---- 1) TURANT line -- OTP submit hote hi ----
        # Transaction OTP submit ke saath ho jaati hai; site par confirm dikhne
        # me waqt lagta hai. Isliye yahin, bina ruke, darj kar dete hain ki kis
        # account par order gaya aur submit safal raha ya nahi. Baad me kuch bhi
        # ho, ye nishaan reh jaata hai.
        status0 = "OTP_SUBMIT_OK" if otp_ok else "OTP_SUBMIT_FAIL"
        nateeja0 = ("OTP submit safal -- site par confirm hone me waqt lag sakta hai"
                    if otp_ok else ("OTP submit nahi hua: %s" % otp_msg))
        rec_row = _sheet_order_row(ord_ws, d, order_info, nateeja0, pay,
                                   status_override=status0, return_row=True)

        # Card ko complete kar do -- submit ho gaya to paisa kat sakta hai;
        # submit nahi bhi hua to us card ko dobara chalane ka koi faayda nahi
        # (ek hi employee ka OTP tha).
        if pay_ws is not None and pay_row:
            order_plan.mark_payment(
                pay_ws, pay_row, order_plan.PAY_DONE,
                "otp submit " + ("ok" if otp_ok else "fail"))
            log("   [sheet] payment row %d -> complete" % pay_row)

        # ---- 2) safal -> usi session me account history se order id ----
        likha = otp_ok
        if otp_ok:
            log("   account history se order id nikaal rahe hain (usi session)")
            got = read_account_order(driver, secs=max(30, a.watch * 6 or 60))
            if got:
                order_info["acct_order_no"] = got.get("no", "")
                order_info["order_date"] = got.get("date", "")
                order_info["payment_status"] = got.get("pay", "")
                order_info["order_total"] = got.get("total", "")
                order_info["order_url"] = got.get("url", "")
                # usi line ko bhar do -- nayi line nahi
                if rec_row:
                    order_plan.update_order(ord_ws, rec_row, {
                        "Status": "CONFIRMED",
                        "Order_Ref": got.get("no", "") or order_info.get("order_ref", ""),
                        "Acct_Order_No": got.get("no", ""),
                        "Order_Date": got.get("date", ""),
                        "Payment_Status": got.get("pay", ""),
                        "Order_Total": got.get("total", ""),
                        "Order_URL": got.get("url", ""),
                        "Note": "",
                    })
                    # LAST_ORDER bhi taaza -- batch/combo isi se ginte hain
                    LAST_ORDER.update({
                        "Status": "CONFIRMED",
                        "Order_Ref": got.get("no", "") or LAST_ORDER.get("Order_Ref", ""),
                        "Acct_Order_No": got.get("no", ""),
                        "Order_Date": got.get("date", ""),
                        "Payment_Status": got.get("pay", ""),
                        "Order_Total": got.get("total", ""),
                        "Order_URL": got.get("url", ""),
                    })
                log("   [sheet] order id se line update ki: %s"
                    % (got.get("no") or "?"))
            else:
                log("   account history me abhi order nahi dikha -- site par "
                    "aane me waqt lag sakta hai (submit to safal tha)")

        # orders.csv (local) me bhi ek nishaan
        haal = status0
        likho_order_row(d, haal, order_info.get("acct_order_no", ""),
                        pay.url, order_info)
        log("   orders.csv me line likh di (status: %s)" % haal)
        if a.hold == 0:
            log("   Browser khula rahega. Kaam khatam ho to yahan Enter dabaiye.")
            try:
                input()
            except Exception:
                pay.wait_for_timeout(600000)
        else:
            log("   (%ds baad band)" % a.hold)
            pay.wait_for_timeout(a.hold * 1000)
    finally:
        # Band karne se PEHLE taaza cookies utha kar session file me likho --
        # warna agli baar basi cookies le kar jayenge.
        if driver is not None and not a.no_save_session:
            log("\n   session band karne se pehle taaza cookies utha rahe hain...")
            try:
                save_session(driver, d, path)
            except Exception as e:
                log("   session save fail: %s" % str(e)[:100])
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
        if stop_bridge is not None:
            stop_bridge.set()
    return 0


def main():
    """Command line se ek order."""
    return run_once(parse_args())


if __name__ == "__main__":
    sys.exit(main())



# #!/usr/bin/env python3
# """place_order.py — Estuary order via Waterfox (Selenium) + Geonode rotating.

# Chrome/Playwright hata kar Waterfox + geckodriver.
# Flow: product -> cart -> checkout -> card -> (manual Pay) -> bank corp/emp -> OTP manual.
# """
# import os
# import re
# import sys
# import glob
# import json
# import csv
# import time
# import argparse
# import socket
# import threading
# import uuid
# import subprocess
# import tempfile
# import shutil
# import asyncio
# from urllib.parse import urlparse

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.firefox.service import Service as FirefoxService

# sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# HERE = os.path.dirname(os.path.abspath(__file__))
# SESSIONS = os.path.join(HERE, "sessions")
# OUT = os.path.join(HERE, "out")
# SHOP = "https://estuaryworld.com"
# os.makedirs(OUT, exist_ok=True)

# ADD_TO_CART = ["button.add-to-cart", "button:has-text('Add to cart')"]
# CART_OPEN = ["a[data-js-sidebar-handle]", "a[title='Open cart']"]
# CHECKOUT = ["#yt-checkout-button", "button:has-text('Checkout')",
#             "a:has-text('Checkout')"]

# DEFAULT_CARD = "0000000000000000"
# DEFAULT_EXP = "01/30"
# DEFAULT_HOLDER = "Test Holder"
# DEFAULT_CVV = "000"
# DEFAULT_CORP_ID = "streakads"
# DEFAULT_EMP_ID = "CHANGE_ME_EMP_ID"
# # ================= GEONODE (ROTATING SOCKS5) =================
# # Dashboard: India + SOCKS5 + Rotating + Port 11000
# # Sticky (12000) mat use — rotating jaise pehle chal raha tha.
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"   # Singapore gateway (rotating)
# GEONODE_PORT = "11000"                 # ROTATING SOCKS5 (12000 = sticky)
# GEONODE_COUNTRY = "in"




# def log(*a):
#     print(*a, flush=True)


# # ---------- Geonode SOCKS5 -> local HTTP bridge ----------
# def _free_port():
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind(("127.0.0.1", 0))
#     port = s.getsockname()[1]
#     s.close()
#     return port


# async def _socks5_connect(dst_host, dst_port, user, pw):
#     reader, writer = await asyncio.open_connection(GEONODE_HOST, int(GEONODE_PORT))
#     writer.write(b"\x05\x01\x02")
#     await writer.drain()
#     resp = await reader.readexactly(2)
#     if resp[1] != 0x02:
#         raise OSError("SOCKS5 auth method refused")
#     ub, pb = user.encode(), pw.encode()
#     writer.write(b"\x01" + bytes([len(ub)]) + ub + bytes([len(pb)]) + pb)
#     await writer.drain()
#     a = await reader.readexactly(2)
#     if a[1] != 0x00:
#         raise OSError("SOCKS5 auth failed")
#     dbytes = dst_host.encode()
#     writer.write(
#         b"\x05\x01\x00\x03" + bytes([len(dbytes)]) + dbytes + int(dst_port).to_bytes(2, "big")
#     )
#     await writer.drain()
#     r = await reader.readexactly(4)
#     if r[1] != 0x00:
#         raise OSError("SOCKS5 connect failed code=%s" % r[1])
#     atyp = r[3]
#     if atyp == 0x01:
#         await reader.readexactly(4)
#     elif atyp == 0x03:
#         ln = await reader.readexactly(1)
#         await reader.readexactly(ln[0])
#     elif atyp == 0x04:
#         await reader.readexactly(16)
#     await reader.readexactly(2)
#     return reader, writer


# async def _pipe(src, dst):
#     try:
#         while True:
#             data = await src.read(65536)
#             if not data:
#                 break
#             dst.write(data)
#             await dst.drain()
#     except Exception:
#         pass
#     finally:
#         try:
#             dst.close()
#         except Exception:
#             pass


# def start_geonode_bridge(username):
#     """Background thread: local HTTP proxy -> Geonode SOCKS5. Returns (port, stop_event)."""
#     local_port = _free_port()
#     stop = threading.Event()
#     ready = threading.Event()

#     async def run_server():
#         tasks = set()

#         async def handle(client_reader, client_writer):
#             tasks.add(asyncio.current_task())
#             up_writer = None
#             try:
#                 header = b""
#                 while b"\r\n\r\n" not in header:
#                     chunk = await client_reader.read(65536)
#                     if not chunk:
#                         return
#                     header += chunk
#                     if len(header) > 262144:
#                         return
#                 head, _, leftover = header.partition(b"\r\n\r\n")
#                 request_line = head.split(b"\r\n", 1)[0].decode("latin1")
#                 method, target, _ver = request_line.split(" ", 2)
#                 if method.upper() == "CONNECT":
#                     host, _, port = target.rpartition(":")
#                     up_reader, up_writer = await _socks5_connect(
#                         host, int(port), username, GEONODE_PASS
#                     )
#                     client_writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
#                     await client_writer.drain()
#                     if leftover:
#                         up_writer.write(leftover)
#                         await up_writer.drain()
#                 else:
#                     u = urlparse(target)
#                     host, port = u.hostname, u.port or 80
#                     up_reader, up_writer = await _socks5_connect(
#                         host, int(port), username, GEONODE_PASS
#                     )
#                     path = u.path or "/"
#                     if u.query:
#                         path += "?" + u.query
#                     rebuilt = header.replace(target.encode(), path.encode(), 1)
#                     up_writer.write(rebuilt)
#                     await up_writer.drain()
#                 await asyncio.gather(
#                     _pipe(client_reader, up_writer), _pipe(up_reader, client_writer)
#                 )
#             except Exception:
#                 try:
#                     client_writer.close()
#                 except Exception:
#                     pass
#                 if up_writer is not None:
#                     try:
#                         up_writer.close()
#                     except Exception:
#                         pass
#             finally:
#                 tasks.discard(asyncio.current_task())

#         server = await asyncio.start_server(handle, "127.0.0.1", local_port)
#         ready.set()
#         while not stop.is_set():
#             await asyncio.sleep(0.3)
#         server.close()
#         await server.wait_closed()
#         for t in list(tasks):
#             if not t.done():
#                 t.cancel()

#     def thread_main():
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         try:
#             loop.run_until_complete(run_server())
#         finally:
#             loop.close()

#     t = threading.Thread(target=thread_main, daemon=True)
#     t.start()
#     if not ready.wait(timeout=10):
#         raise RuntimeError("Geonode bridge start fail")
#     return local_port, stop


# def geonode_username(country=None, sticky=False):
#     """Rotating residential username (default).
#     sticky=True only if kabhi sticky chahiye (port 12000 + lifetime).
#     """
#     c = (country or GEONODE_COUNTRY).lower()
#     base = GEONODE_USER_BASE.format(c)
#     if sticky:
#         sess = uuid.uuid4().hex[:8]
#         return "%s-session-%s-lifetime-30" % (base, sess)
#     return base


# # ================= WATERFOX (Selenium + geckodriver) =================
# # Chrome/CDP ki jagah ab Waterfox chalti hai.
# # Proxy wahi ka wahi: Geonode SOCKS5 -> upar wala local HTTP bridge -> Waterfox
# # ka manual HTTP proxy pref. Yaani exit IP pehle jaisa hi India ka residential.
# #
# # Playwright kyun nahi: Playwright 1.58 ka BiDi mode connect hote hi
# # 'network.addDataCollector' bhejta hai, jo Gecko 141+ ka command hai. Waterfox
# # 140 par wo 'unknown command' deta hai aur session wahin mar jaati hai. Isliye
# # Waterfox ko geckodriver (WebDriver) se chalaya jaata hai.

# WATERFOX_CANDIDATES = [
#     os.environ.get("WATERFOX_PATH") or "",
#     os.path.join(os.path.dirname(HERE), "Waterfox", "waterfox.exe"),
#     r"D:\streakads\Waterfox\waterfox.exe",
#     r"C:\Program Files\Waterfox\waterfox.exe",
#     r"C:\Program Files (x86)\Waterfox\waterfox.exe",
#     "/usr/bin/waterfox",
#     "/Applications/Waterfox.app/Contents/MacOS/waterfox",
# ]

# GECKODRIVER_CANDIDATES = [
#     os.environ.get("GECKODRIVER_PATH") or "",
#     shutil.which("geckodriver") or "",
#     os.path.join(os.path.dirname(HERE), "geckodriver-v0.36.0-win64",
#                  "geckodriver.exe"),
#     r"D:\streakads\geckodriver-v0.36.0-win64\geckodriver.exe",
#     os.path.expandvars(
#         r"%USERPROFILE%\.wdm\drivers\geckodriver\win64\v0.36.0\geckodriver.exe"),
# ]

# # Waterfox apne aap ko Firefox hi batati hai; UA ko Chrome banane ka koi fayda
# # nahi -- Gecko engine + Chrome UA ka mel na khana khud ek pehchaan hai.
# WATERFOX_UA = None      # None = Waterfox ki apni UA

# VIEWPORT = {"width": 1500, "height": 950}


# def find_waterfox_exe():
#     for c in WATERFOX_CANDIDATES:
#         if c and os.path.isfile(c):
#             return c
#     return None


# def find_geckodriver():
#     for c in GECKODRIVER_CANDIDATES:
#         if c and os.path.isfile(c):
#             return c
#     return None


# def launch_waterfox(proxy_port=None, headless=False):
#     """Waterfox + geckodriver. Returns driver.

#     proxy_port: upar wale local HTTP bridge ka port (None = bina proxy).
#     """
#     exe = find_waterfox_exe()
#     if not exe:
#         raise RuntimeError(
#             "Waterfox nahi mili. WATERFOX_PATH set karo ya "
#             "D:\\streakads\\Waterfox\\waterfox.exe rakho.")
#     drv_path = find_geckodriver()
#     if not drv_path:
#         raise RuntimeError(
#             "geckodriver nahi mila. GECKODRIVER_PATH set karo ya "
#             "D:\\streakads\\geckodriver-v0.36.0-win64\\geckodriver.exe rakho.")

#     opts = FirefoxOptions()
#     opts.binary_location = exe
#     if headless:
#         opts.add_argument("-headless")

#     # --- proxy: bridge ko manual HTTP proxy ki tarah ---
#     if proxy_port:
#         opts.set_preference("network.proxy.type", 1)
#         opts.set_preference("network.proxy.http", "127.0.0.1")
#         opts.set_preference("network.proxy.http_port", int(proxy_port))
#         opts.set_preference("network.proxy.ssl", "127.0.0.1")
#         opts.set_preference("network.proxy.ssl_port", int(proxy_port))
#         opts.set_preference("network.proxy.share_proxy_settings", True)
#         # DNS bhi proxy ke us paar -- warna local DNS leak hota hai
#         opts.set_preference("network.proxy.socks_remote_dns", True)
#         opts.set_preference("network.proxy.no_proxies_on", "")
#     else:
#         opts.set_preference("network.proxy.type", 0)

#     # --- automation ke nishaan kam karo (Chrome build me jo init script tha) ---
#     opts.set_preference("dom.webdriver.enabled", False)
#     opts.set_preference("useAutomationExtension", False)
#     opts.set_preference("marionette.enabled", True)
#     opts.set_preference("privacy.resistFingerprinting", False)
#     opts.set_preference("intl.accept_languages", "en-IN, en")   # locale="en-IN"
#     opts.set_preference("browser.startup.homepage", "about:blank")
#     opts.set_preference("browser.startup.page", 0)
#     opts.set_preference("datareporting.healthreport.uploadEnabled", False)
#     opts.set_preference("app.update.auto", False)
#     opts.set_preference("browser.shell.checkDefaultBrowser", False)
#     # popup/nayi window: Pay ke baad bank page nayi window me aati hai
#     opts.set_preference("browser.link.open_newwindow", 3)        # naye tab me
#     opts.set_preference("browser.link.open_newwindow.restriction", 0)
#     if WATERFOX_UA:
#         opts.set_preference("general.useragent.override", WATERFOX_UA)

#     # ignore_https_errors=True ka Selenium roop
#     opts.set_capability("acceptInsecureCerts", True)
#     opts.set_capability("pageLoadStrategy", "eager")   # wait_until="domcontentloaded"

#     service = FirefoxService(executable_path=drv_path, log_output=os.devnull)

#     log("Waterfox  : %s" % exe)
#     log("geckodriver: %s" % drv_path)
#     driver = webdriver.Firefox(service=service, options=opts)

#     driver.set_page_load_timeout(120)
#     driver.set_script_timeout(60)
#     driver.implicitly_wait(0)       # har intezaar humara apna, chhupa hua nahi

#     # viewport ~1500x950 (window chrome ka farq nikaal kar)
#     try:
#         driver.set_window_size(VIEWPORT["width"], VIEWPORT["height"] + 90)
#         inner = driver.execute_script(
#             "return [window.innerWidth, window.innerHeight];")
#         dw = VIEWPORT["width"] - int(inner[0])
#         dh = VIEWPORT["height"] - int(inner[1])
#         if dw or dh:
#             driver.set_window_size(VIEWPORT["width"] + dw,
#                                    VIEWPORT["height"] + 90 + dh)
#     except Exception:
#         pass
#     return driver


# def load_session(driver, d):
#     """storage_state (cookies + localStorage) Waterfox me daalo.

#     Cookie tabhi jaati hai jab browser usi domain par khada ho, isliye har
#     origin ek baar khola jaata hai. Analytics ke cookies (bing/clarity/fb)
#     chhod diye jaate hain -- login ya checkout unse nahi chalta.
#     """
#     st = d.get("state") or {}
#     cookies = st.get("cookies") or []
#     origins = st.get("origins") or []

#     wanted = {
#         "https://estuaryworld.com": ("estuaryworld.com",),
#         "https://fastrr-boost-ui.pickrr.com": ("pickrr.com", "shiprocket.in"),
#     }
#     # jis origin ka localStorage hai wo bhi list me aa jaye
#     for o in origins:
#         og = o.get("origin") or ""
#         if og and og not in wanted:
#             host = urlparse(og).hostname or ""
#             wanted[og] = (host,)

#     ok_c = fail_c = ok_ls = 0
#     for origin, suffixes in wanted.items():
#         try:
#             driver.get(origin)
#         except Exception as e:
#             log("   %s khula nahi (%s) -- iske cookies chhod diye"
#                 % (origin, str(e)[:60]))
#             continue
#         time.sleep(1.0)

#         for c in cookies:
#             dom = (c.get("domain") or "").lstrip(".")
#             if not any(dom == s or dom.endswith("." + s) or s in dom
#                        for s in suffixes):
#                 continue
#             ck = {
#                 "name": c.get("name"),
#                 "value": c.get("value"),
#                 "path": c.get("path") or "/",
#                 "domain": c.get("domain"),
#                 "secure": bool(c.get("secure")),
#             }
#             exp = c.get("expires")
#             if exp and exp > 0:
#                 ck["expiry"] = int(exp)
#             ss = c.get("sameSite")
#             if ss in ("Strict", "Lax", "None"):
#                 ck["sameSite"] = ss
#             try:
#                 driver.add_cookie(ck)
#                 ok_c += 1
#             except Exception:
#                 # domain thoda alag ho to bina domain ke daal ke dekho
#                 ck.pop("domain", None)
#                 try:
#                     driver.add_cookie(ck)
#                     ok_c += 1
#                 except Exception:
#                     fail_c += 1

#         for o in origins:
#             if (o.get("origin") or "") != origin:
#                 continue
#             items = o.get("localStorage") or []
#             if not items:
#                 continue
#             try:
#                 driver.execute_script(
#                     "for (const kv of arguments[0]) {"
#                     "  try { localStorage.setItem(kv.name, kv.value); } catch (e) {}"
#                     "}", items)
#                 ok_ls += len(items)
#             except Exception as e:
#                 log("   localStorage (%s): %s" % (origin, str(e)[:60]))

#     log("   session: %d cookie daale (%d chhode), %d localStorage"
#         % (ok_c, fail_c, ok_ls))
#     return ok_c


# # ---------- Playwright ke jo thode selectors the, unka Selenium roop ----------
# # Script me sirf ye khaas selectors the: :has-text(), :text-is(), :has(), :visible.
# # CSS baaki sab seedha chalta hai.

# _HAS_TEXT = re.compile(r"^(?P<base>.*?):has-text\((?P<q>['\"])(?P<txt>.*?)(?P=q)\)$")
# _TEXT_IS = re.compile(r"^(?P<base>.*?):text-is\((?P<q>['\"])(?P<txt>.*?)(?P=q)\)$")
# _HAS = re.compile(r"^(?P<base>.*?):has\((?P<inner>.+)\)$")


# def _css_step_to_xpath(css):
#     """'span.lang-en' -> 'span[contains(concat(" ",@class," ")," lang-en ")]'"""
#     css = (css or "").strip() or "*"
#     m = re.match(r"^([a-zA-Z][\w-]*|\*)?(.*)$", css)
#     tag = m.group(1) or "*"
#     rest = m.group(2) or ""
#     preds = []
#     for part in re.finditer(r"\.([\w-]+)|#([\w-]+)|\[([^\]]+)\]", rest):
#         cls, idd, attr = part.group(1), part.group(2), part.group(3)
#         if cls:
#             preds.append(
#                 'contains(concat(" ", normalize-space(@class), " "), " %s ")' % cls)
#         elif idd:
#             preds.append('@id="%s"' % idd)
#         elif attr:
#             am = re.match(r"^\s*([\w-]+)\s*(?:([~^$*|]?=)\s*['\"]?([^'\"]*)['\"]?)?\s*$",
#                           attr)
#             if not am:
#                 continue
#             name, op, val = am.group(1), am.group(2), am.group(3)
#             if not op:
#                 preds.append("@%s" % name)
#             elif op == "=":
#                 preds.append('@%s="%s"' % (name, val))
#             elif op == "*=":
#                 preds.append('contains(@%s, "%s")' % (name, val))
#             elif op == "^=":
#                 preds.append('starts-with(@%s, "%s")' % (name, val))
#             else:
#                 preds.append('contains(@%s, "%s")' % (name, val))
#     return tag + "".join("[%s]" % p for p in preds)


# def _one_selector(sel):
#     """Ek selector -> (by, expr, visible_only)."""
#     sel = sel.strip()
#     visible_only = False
#     if ":visible" in sel:
#         visible_only = True
#         sel = sel.replace(":visible", "")

#     m = _HAS_TEXT.match(sel)
#     if m:
#         xp = "//%s[contains(normalize-space(.), %s)]" % (
#             _css_step_to_xpath(m.group("base")), _xq(m.group("txt")))
#         return By.XPATH, xp, visible_only

#     m = _TEXT_IS.match(sel)
#     if m:
#         xp = "//%s[normalize-space(.)=%s]" % (
#             _css_step_to_xpath(m.group("base")), _xq(m.group("txt")))
#         return By.XPATH, xp, visible_only

#     m = _HAS.match(sel)
#     if m:
#         inner = m.group("inner").strip()
#         im = _TEXT_IS.match(inner)
#         if im:
#             inner_xp = "%s[normalize-space(.)=%s]" % (
#                 _css_step_to_xpath(im.group("base")), _xq(im.group("txt")))
#         else:
#             ihm = _HAS_TEXT.match(inner)
#             if ihm:
#                 inner_xp = "%s[contains(normalize-space(.), %s)]" % (
#                     _css_step_to_xpath(ihm.group("base")), _xq(ihm.group("txt")))
#             else:
#                 inner_xp = _css_step_to_xpath(inner)
#         xp = "//%s[.//%s]" % (_css_step_to_xpath(m.group("base")), inner_xp)
#         return By.XPATH, xp, visible_only

#     return By.CSS_SELECTOR, sel, visible_only


# def _xq(text):
#     """XPath me quote -- text me ' ho to concat() lagta hai."""
#     if "'" not in text:
#         return "'%s'" % text
#     if '"' not in text:
#         return '"%s"' % text
#     parts = text.split("'")
#     return "concat(%s)" % ", ".join(
#         ["'%s'" % p if i == 0 else "\"'\", '%s'" % p for i, p in enumerate(parts)])


# def _split_selectors(sel):
#     """Top-level comma par todo (bracket/quote ke andar wale comma chhod kar)."""
#     out, depth, cur, quote = [], 0, "", None
#     for ch in sel:
#         if quote:
#             cur += ch
#             if ch == quote:
#                 quote = None
#             continue
#         if ch in "'\"":
#             quote = ch
#             cur += ch
#         elif ch in "([":
#             depth += 1
#             cur += ch
#         elif ch in ")]":
#             depth -= 1
#             cur += ch
#         elif ch == "," and depth == 0:
#             out.append(cur)
#             cur = ""
#         else:
#             cur += ch
#     if cur.strip():
#         out.append(cur)
#     return [s.strip() for s in out if s.strip()]


# # ---------- Scope: ek window ya uske andar ka ek frame ----------
# class Scope(object):
#     """Selenium me frame ke andar kaam karne ke liye har baar switch karna padta
#     hai. Isliye har Scope apna raasta (window handle + frame index chain) yaad
#     rakhta hai aur kaam se pehle khud us jagah pahunch jaata hai."""

#     def __init__(self, driver, handle, path=(), url=""):
#         self.d = driver
#         self.handle = handle
#         self.path = tuple(path)
#         self._url = url

#     # -- jagah par pahuncho --
#     def use(self):
#         """Us window/frame me pahuncho jiska ye Scope hai.

#         Frame me index se ghusna bharosemand nahi: switch_to.frame(int) window.frames
#         ka index leta hai, jabki humne raasta 'iframe, frame' elements gin kar banaya
#         tha. Bina src wale ya baad me bane iframe se dono ginti alag ho jaati hain aur
#         aadmi doosre frame me pahunch jaata hai. Isliye jis list se raasta bana tha,
#         switch bhi usi list ke element se hota hai.
#         """
#         if self.d.current_window_handle != self.handle:
#             self.d.switch_to.window(self.handle)
#         self.d.switch_to.default_content()
#         for idx in self.path:
#             els = self.d.find_elements(By.CSS_SELECTOR, "iframe, frame")
#             if idx >= len(els):
#                 raise RuntimeError("frame %d ab maujood nahi (kul %d)"
#                                    % (idx, len(els)))
#             self.d.switch_to.frame(els[idx])
#         return self

#     @property
#     def url(self):
#         if self.path:
#             return self._url
#         try:
#             self.use()
#             return self.d.current_url
#         except Exception:
#             return self._url

#     def is_page(self):
#         return not self.path

#     # -- dhoondho --
#     def query(self, sel, visible=None):
#         self.use()
#         out = []
#         for one in _split_selectors(sel):
#             by, expr, vis_only = _one_selector(one)
#             want_vis = vis_only if visible is None else visible
#             try:
#                 els = self.d.find_elements(by, expr)
#             except Exception:
#                 continue
#             for e in els:
#                 if want_vis:
#                     try:
#                         if not e.is_displayed():
#                             continue
#                     except Exception:
#                         continue
#                 out.append(e)
#         return out

#     def count(self, sel):
#         return len(self.query(sel))

#     def first(self, sel):
#         got = self.query(sel)
#         return got[0] if got else None

#     def visible_first(self, sel):
#         got = self.query(sel, visible=True)
#         return got[0] if got else None

#     # -- padho --
#     def body_text(self):
#         try:
#             self.use()
#             return self.d.execute_script(
#                 "return document.body ? document.body.innerText : '';") or ""
#         except Exception:
#             return ""

#     def evaluate(self, js, *args):
#         self.use()
#         return self.d.execute_script(js, *args)

#     def evaluate_async(self, js, *args):
#         self.use()
#         return self.d.execute_async_script(js, *args)

#     def title(self):
#         self.use()
#         return self.d.title or ""

#     # -- Playwright jaisa wait --
#     def wait_for_timeout(self, ms):
#         time.sleep(ms / 1000.0)

#     def goto(self, url, timeout=120):
#         self.use()
#         old = self.d.timeouts.page_load if hasattr(self.d, "timeouts") else None
#         try:
#             self.d.set_page_load_timeout(timeout)
#             self.d.get(url)
#         finally:
#             if old:
#                 try:
#                     self.d.set_page_load_timeout(old)
#                 except Exception:
#                     pass

#     def screenshot(self, path, full_page=False):
#         self.use()
#         if full_page:
#             try:
#                 self.d.get_full_page_screenshot_as_file(path)
#                 return
#             except Exception:
#                 pass
#         self.d.save_screenshot(path)


# def pages(driver):
#     """Sabhi khuli windows/tabs -- Playwright ke context.pages jaisa."""
#     out = []
#     cur = None
#     try:
#         cur = driver.current_window_handle
#     except Exception:
#         pass
#     for h in list(driver.window_handles):
#         out.append(Scope(driver, h))
#     if cur:
#         try:
#             driver.switch_to.window(cur)
#         except Exception:
#             pass
#     return out


# def frames(page):
#     """Page ke andar ke saare frames (nested bhi), URL ke saath."""
#     d = page.d
#     found = []

#     def _goto(path):
#         d.switch_to.default_content()
#         for idx in path:
#             els = d.find_elements(By.CSS_SELECTOR, "iframe, frame")
#             if idx >= len(els):
#                 raise RuntimeError("frame gayab")
#             d.switch_to.frame(els[idx])

#     def walk(path):
#         try:
#             _goto(path)
#             n = len(d.find_elements(By.CSS_SELECTOR, "iframe, frame"))
#         except Exception:
#             return
#         for i in range(n):
#             child = path + (i,)
#             try:
#                 _goto(child)
#                 url = d.execute_script("return location.href;") or ""
#             except Exception:
#                 continue
#             found.append(Scope(d, page.handle, child, url))
#             walk(child)

#     try:
#         if d.current_window_handle != page.handle:
#             d.switch_to.window(page.handle)
#         walk(())
#         d.switch_to.default_content()
#     except Exception:
#         pass
#     return found


# # ---------- element ke saath kaam ----------
# def el_fill(scope, el, value):
#     """Playwright ke fill() jaisa: purana hatao, naya likho, event bhejo."""
#     scope.use()
#     try:
#         el.click()
#     except Exception:
#         pass
#     try:
#         el.clear()
#     except Exception:
#         pass
#     try:
#         el.send_keys(Keys.CONTROL, "a")
#         el.send_keys(Keys.DELETE)
#     except Exception:
#         pass
#     el.send_keys(str(value))
#     try:
#         scope.d.execute_script(
#             "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
#             "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", el)
#     except Exception:
#         pass


# def el_type(scope, el, value, delay=50):
#     """Playwright ke type(delay=) jaisa -- ek ek akshar, thoda ruk kar."""
#     scope.use()
#     for ch in str(value):
#         el.send_keys(ch)
#         time.sleep(delay / 1000.0)


# def el_value(el):
#     try:
#         return el.get_attribute("value") or ""
#     except Exception:
#         return ""


# def real_click(scope, el):
#     """Aadmi jaisa click: pahuncho, thoda ruko, dabao, chhodo."""
#     scope.use()
#     try:
#         scope.d.execute_script(
#             "arguments[0].scrollIntoView({block:'center', inline:'center'});", el)
#         time.sleep(0.4)
#     except Exception:
#         pass
#     try:
#         ActionChains(scope.d).move_to_element(el).pause(0.4) \
#             .click_and_hold(el).pause(0.09).release().perform()
#         return True
#     except Exception:
#         try:
#             el.click()
#             return True
#         except Exception:
#             return False


# def in_view(scope, el):
#     try:
#         return bool(scope.d.execute_script(
#             "const r = arguments[0].getBoundingClientRect();"
#             "return r.width > 0 && r.height > 0 && r.top >= 0 && r.left >= 0"
#             " && r.bottom <= (window.innerHeight || 0)"
#             " && r.right <= (window.innerWidth || 0);", el))
#     except Exception:
#         return False


# def scroll_click(scope, el, tries=3):
#     """Teen tareeke, usi kram me: asli mouse -> click() -> DOM click."""
#     for _ in range(tries):
#         scope.use()
#         try:
#             scope.d.execute_script(
#                 "arguments[0].scrollIntoView({block:'center', inline:'center'});", el)
#         except Exception:
#             pass
#         time.sleep(0.6)
#         if in_view(scope, el):
#             try:
#                 ActionChains(scope.d).move_to_element(el).pause(0.3) \
#                     .click_and_hold(el).pause(0.09).release().perform()
#                 return "mouse"
#             except Exception:
#                 pass
#     try:
#         scope.use()
#         el.click()
#         return "click()"
#     except Exception:
#         pass
#     try:
#         scope.use()
#         scope.d.execute_script("arguments[0].click();", el)
#         return "dom-click"
#     except Exception:
#         return None


# def expect_new_page(driver, do_click, timeout=15):
#     """Click ke baad nayi window khuli to uska Scope do, warna None."""
#     before = set(driver.window_handles)
#     try:
#         do_click()
#     except Exception:
#         pass
#     end = time.time() + timeout
#     while time.time() < end:
#         naye = set(driver.window_handles) - before
#         if naye:
#             h = naye.pop()
#             try:
#                 driver.switch_to.window(h)
#             except Exception:
#                 pass
#             return Scope(driver, h)
#         time.sleep(0.5)
#     return None


# # ---------- session / product helpers ----------
# def newest_session():
#     fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
#     return fs[-1] if fs else None


# def find(scope, sels):
#     for s in sels:
#         try:
#             if scope.query(s, visible=True):
#                 return s
#         except Exception:
#             continue
#     return None


# def variant_id(page):
#     return page.evaluate(
#         """const f = document.querySelector('form[action*="/cart/add"]');
#            const i = f && f.querySelector('input[name="id"], select[name="id"]');
#            return i ? String(i.value) : null;""")


# def pick(page, value):
#     res = page.evaluate(
#         """const v = arguments[0];
#            const rs = [...document.querySelectorAll('input[type=radio]')]
#                       .filter(x => (x.value || '').trim() === v);
#            if (!rs.length) return 'nahi-mila';
#            const r = rs[0];
#            if (r.checked) return 'pehle-se-chuna';
#            r.click();
#            return 'daba-diya';""", value)
#     log("      %s" % res)
#     if res == "nahi-mila":
#         return False
#     page.wait_for_timeout(2500)
#     return True


# # ---------- checkout (Fastrr) ke frames ----------
# def sr_frame(page):
#     for fr in frames(page):
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if fr.count("#pincode"):
#                     return fr
#             except Exception:
#                 pass
#     return None


# def sr_frame_any(page):
#     for fr in frames(page):
#         if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
#             try:
#                 if (fr.body_text() or "").strip():
#                     return fr
#             except Exception:
#                 pass
#     return None


# def ship_address(page, acct):
#     f = None
#     for _ in range(20):
#         f = sr_frame(page)
#         if f:
#             break
#         page.wait_for_timeout(1500)
#     if not f:
#         return "checkout ka pata wala form nahi mila (shayad pata pehle se hai)"

#     ad = acct.get("address") or {}
#     pin = ad.get("zip") or "000000"
#     first = ad.get("first_name") or "Ishan"
#     last = ad.get("last_name") or "Gupta"
#     line1 = ad.get("address1") or "55/34 Shastri Nagar"
#     line2 = ad.get("address2") or "Near Kidwai Nagar Market"
#     city = ad.get("city") or "Kanpur"
#     state = ad.get("province") or "Uttar Pradesh"
#     email = acct.get("email") or ""

#     def _put(sel, val):
#         el = f.first(sel)
#         if el is not None:
#             el_fill(f, el, val)
#         return el is not None

#     _put("#pincode", pin)
#     page.wait_for_timeout(4000)
#     _put("#name", first)
#     _put("#lastName", last)
#     _put("#line1", line1)
#     _put("#line2", line2)
#     for sel, val in (("#city", city), ("#state", state)):
#         try:
#             el = f.first(sel)
#             if el is not None and not el_value(el).strip():
#                 el_fill(f, el, val)
#         except Exception:
#             pass
#     if email:
#         try:
#             _put("#email", email)
#         except Exception:
#             pass

#     try:
#         home = f.first("input[name='home']")
#         if home is not None and not home.is_selected():
#             f.d.execute_script("arguments[0].click();", home)
#     except Exception:
#         pass

#     got = f.first("#addAddressBtn")
#     if got is None:
#         return "'Add address' ka button nahi mila"
#     if not real_click(f, got):
#         try:
#             f.use()
#             got.click()
#         except Exception:
#             pass

#     for _ in range(6):
#         page.wait_for_timeout(4000)
#         try:
#             if "Add shipping address" not in (f.body_text() or ""):
#                 return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#         except Exception:
#             return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#     return "pata bhara par form abhi bhi khada hai -- dekh lijiye"


# def confirm_email(page, acct):
#     email = acct.get("email") or ""
#     if not email:
#         return "account par email hi nahi hai"
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     for _ in range(10):
#         try:
#             body = f.body_text() or ""
#         except Exception:
#             return "checkout ka frame chala gaya"
#         if "onfirm your email" not in body:
#             return "email confirm karne ki zaroorat nahi thi"

#         btn = f.first("button:has-text('Confirm email')")
#         box = f.visible_first("input#email, input[type='email']")
#         if btn is not None and box is not None:
#             el_fill(f, box, email)
#             page.wait_for_timeout(800)
#             real_click(f, btn)
#             page.wait_for_timeout(6000)
#             try:
#                 if "onfirm your email" not in (f.body_text() or ""):
#                     return "email confirm ho gaya (%s)" % email
#             except Exception:
#                 return "email confirm ho gaya (%s)" % email
#         page.wait_for_timeout(2000)

#     try:
#         ins = f.evaluate(
#             "return [...document.querySelectorAll('input')]"
#             ".map(e => (e.id||'-')+'/'+(e.name||'-')+'/'+(e.type||'-'));") or []
#     except Exception:
#         ins = []
#     return "email confirm nahi hua | frame ke input: %s" % ", ".join(ins[:10])


# def read_checkout(page):
#     f = sr_frame_any(page)
#     if not f:
#         return None
#     try:
#         body = f.body_text() or ""
#     except Exception:
#         return None
#     out = {"address": [], "pay": [], "total": ""}

#     lines = [l.strip() for l in body.splitlines() if l.strip()]
#     for i, l in enumerate(lines):
#         if re.search(r"\b\d{6}\b", l) and len(l) > 12:
#             out["address"] = lines[max(0, i - 2):i + 3]
#             break

#     try:
#         texts = f.evaluate(
#             "return [...document.querySelectorAll("
#             "\"label, [class*='paymentMethod'], [class*='payment-method']\")]"
#             ".map(e => e.innerText || '');") or []
#         out["pay"] = [t.strip() for t in texts if 2 < len(t.strip()) < 60][:12]
#     except Exception:
#         pass

#     m = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", body)
#     if m:
#         out["total"] = m[-1]
#     return out


# # ---------- gateway / card ----------
# CARD_TARGETS = [
#     "#payment-method-button-Card label.payment-button-heading",
#     "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
#     "#payment-method-button-Card",
# ]

# GATEWAY_HINTS = ("easebuzz", "eazypay", "payment", "pay.", "3ds", "acs",
#                  "razorpay", "payu", "billdesk")


# def card_frame(page):
#     for fr in frames(page):
#         u = (fr.url or "").lower()
#         if any(k in u for k in ("easebuzz", "pay.", "payment", "3ds", "acs")):
#             try:
#                 if fr.query("input", visible=True):
#                     return fr
#             except Exception:
#                 pass
#     return None


# def card_fields(f):
#     try:
#         return f.evaluate(
#             """return [...document.querySelectorAll('input')]
#                  .filter(e => e.offsetParent !== null || e.getClientRects().length)
#                  .map(e => ({id: e.id || '', name: e.name || '',
#                              ph: e.placeholder || '',
#                              aria: e.getAttribute('aria-label') || '',
#                              maxlen: e.maxLength}))
#                  .filter(o => /card|number|cvv|cvc|expiry|month|year|holder/i
#                               .test(o.id + o.name + o.ph + o.aria)
#                            || (o.maxlen >= 3 && o.maxlen <= 19));""") or []
#     except Exception:
#         return []


# def gateway_frames(page):
#     out = set()
#     for fr in frames(page):
#         u = (fr.url or "")
#         if u and any(k in u.lower() for k in GATEWAY_HINTS):
#             out.add(u)
#     return out


# def card_state(page, f):
#     st = {"qr": False, "h": 0.0, "frames": gateway_frames(page)}
#     try:
#         st["qr"] = f.count("#src-qrcode-payment-btn") > 0
#     except Exception:
#         pass
#     try:
#         st["h"] = f.evaluate(
#             "const e = document.querySelector('#payment-method-button-Card');"
#             "return e ? e.getBoundingClientRect().height : 0;") or 0.0
#     except Exception:
#         pass
#     return st


# def card_chosen(page, f, before):
#     now = card_state(page, f)
#     if now["frames"] - before["frames"]:
#         return True
#     if before["qr"] and not now["qr"]:
#         return True
#     if now["h"] > before["h"] + 30:
#         return True
#     return bool(card_fields(f))


# def card_form_ready(page):
#     for fr in frames(page):
#         if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#             continue
#         got = card_fields(fr)
#         if got:
#             return "form aa gaya (%s)" % ", ".join(
#                 (g["id"] or g["name"] or g["ph"] or "?") for g in got[:6])
#     return "form abhi saamne nahi aaya"


# def pick_card_type(page, kind="Credit", secs=75):
#     """Easebuzz nayi window me bhi khul sakta hai — saari windows + frames."""
#     sels = ["span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
#             "span.lang-en:text-is('%s Card')" % kind,
#             "*:text-is('%s Card')" % kind]
#     end = time.time() + secs
#     while time.time() < end:
#         scopes = []
#         for pg in pages(page.d):
#             scopes.append(pg)
#             scopes.extend(frames(pg))
#         for fr in scopes:
#             try:
#                 u = (fr.url or "").lower()
#             except Exception:
#                 u = ""
#             # gateway URL ya seedha Credit Card text
#             is_gw = any(k in u for k in GATEWAY_HINTS) if u else False
#             for sel in sels:
#                 try:
#                     el = fr.first(sel)
#                     if el is None:
#                         continue
#                     if not is_gw:
#                         # sirf tab jab text clearly Credit Card ho
#                         pass
#                 except Exception:
#                     continue
#                 how = scroll_click(fr, el)
#                 if not how:
#                     continue
#                 page.wait_for_timeout(5000)
#                 return "%s Card daba diya (%s) -- %s" % (
#                     kind, how, card_form_ready(page))
#         page.wait_for_timeout(2500)
#     return "%s Card ka option gateway ke panne par nahi mila" % kind


# def clear_blocker(page):
#     f = sr_frame_any(page)
#     if not f:
#         return ""
#     try:
#         body = (f.body_text() or "").lower()
#     except Exception:
#         return ""
#     if "active session" not in body and "page isn't available" not in body:
#         return ""
#     for sel in ("button:has-text('Continue here')",
#                 "a:has-text('Continue here')",
#                 "[role=button]:has-text('Continue here')"):
#         try:
#             el = f.first(sel)
#             if el is not None:
#                 scroll_click(f, el)
#                 page.wait_for_timeout(8000)
#                 return "purana session ka parda hata diya (Continue here)"
#         except Exception:
#             continue
#     return "CHETAVNI: purana session ka parda hai par 'Continue here' nahi mila"


# def pick_card(page):
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     el = None
#     used = ""
#     for _ in range(10):
#         for sel in CARD_TARGETS:
#             try:
#                 got = f.first(sel)
#                 if got is not None:
#                     el, used = got, sel
#                     break
#             except Exception:
#                 continue
#         if el is not None:
#             break
#         page.wait_for_timeout(2000)
#     if el is None:
#         return "Credit/Debit Card ka khaana nahi mila (shayad email confirm baaki hai)"

#     before = card_state(page, f)
#     how = None
#     for _ in range(3):
#         how = scroll_click(f, el)
#         for _ in range(6):
#             page.wait_for_timeout(1500)
#             if card_chosen(page, f, before):
#                 break
#         if card_chosen(page, f, before):
#             break
#     if not card_chosen(page, f, before):
#         return "Card daba nahi paye (%s se koshish ki, UPI hi khula raha)" % (
#             how or "kisi tareeke")

#     log("      Card chun liya (%s | %s)" % (how, used))
#     naya = card_state(page, f)["frames"] - before["frames"]
#     if naya:
#         log("      gateway ka panna khula: %s" % list(naya)[0][:90])

#     for i in range(12):
#         page.wait_for_timeout(2500)
#         cf = card_frame(page)
#         if cf:
#             return "card ke khaane khul gaye (gateway ke frame me, %ds baad)" % (
#                 (i + 1) * 2.5)
#         got = card_fields(f)
#         if got:
#             return "card ke khaane khul gaye (checkout ke frame me: %s)" % (
#                 ", ".join((g["id"] or g["name"] or g["ph"] or "?") for g in got[:6]))
#     if naya:
#         return "Card chun liya aur gateway ka panna khul gaya (agla kadam: step 10)"
#     return "Card to chun liya, par khaane abhi tak nahi aaye -- out/ ki tasveer dekhiye"


# def easebuzz_form_frame(page, secs=40):
#     """Card inputs Easebuzz window YA uske frame me — saari windows scan."""
#     sel = ('input[name="card_number"], input[placeholder="Test Holder"], '
#            'input[name="card_exp_date"], input[name="card_cvv"]')
#     end = time.time() + secs
#     while time.time() < end:
#         # har open window
#         for pg in pages(page.d):
#             try:
#                 if pg.count(sel) >= 1:
#                     return pg
#             except Exception:
#                 pass
#             for fr in frames(pg):
#                 try:
#                     if fr.count(sel) >= 1:
#                         return fr
#                 except Exception:
#                     continue
#         try:
#             if page.count('input[name="card_number"], input[name="card_cvv"]'):
#                 return page
#         except Exception:
#             pass
#         page.wait_for_timeout(1500)
#     return None


# def _fill_one(fr, page, sels, value, label):
#     for sel in sels:
#         try:
#             el = fr.first(sel)
#             if el is None:
#                 continue
#             try:
#                 if not el.is_displayed():
#                     continue
#             except Exception:
#                 pass
#             fr.use()
#             try:
#                 fr.d.execute_script(
#                     "arguments[0].scrollIntoView({block:'center'});", el)
#             except Exception:
#                 pass
#             page.wait_for_timeout(200)
#             el.click()
#             page.wait_for_timeout(150)
#             el_fill(fr, el, "")
#             el_type(fr, el, str(value), delay=50)
#             page.wait_for_timeout(250)
#             got = el_value(el)
#             log("      %s fill -> '%s'" % (label, got[:28] if got else value))
#             return True
#         except Exception as e:
#             log("      %s try fail (%s): %s" % (label, sel[:40], str(e)[:50]))
#     return False


# def fill_card_details(page, number, exp, holder, cvv, click_pay=True):
#     fr = easebuzz_form_frame(page)
#     if not fr:
#         return "FAIL: card form frame nahi mila (Credit Card choose ke baad wait karo)"

#     num_clean = re.sub(r"\s+", "", number or "")
#     num_disp = " ".join(num_clean[i:i + 4] for i in range(0, len(num_clean), 4))

#     ok_n = _fill_one(fr, page, [
#         'input[name="card_number"]',
#         'input[placeholder="Test Holder"]',
#     ], num_disp, "Card Number")

#     ok_e = _fill_one(fr, page, [
#         'input[name="card_exp_date"]',
#         'input[placeholder="Test Holder"]',
#     ], exp, "MM/YY")

#     ok_h = _fill_one(fr, page, [
#         'input[placeholder="Test Holder"]',
#         'input[name^="ebz_card_holder_name"]',
#         'input[name*="card_holder"]',
#     ], holder, "Card Holder")

#     ok_c = _fill_one(fr, page, [
#         'input[name="card_cvv"]',
#         'input[placeholder="Test Holder"]',
#     ], cvv, "CVV")

#     # human-like pause before Pay (gateway timing checks)
#     log("      Pay se pehle wait 6-8s...")
#     page.wait_for_timeout(7000)

#     pay_ok = False
#     if click_pay:
#         bank_popup = None
#         for scope in (fr, page):
#             for sel in ('button:has-text("Pay")',
#                         'button:has-text("Pay ₹")',
#                         'button:has-text("Pay Rs")'):
#                 try:
#                     el = scope.visible_first(sel)
#                     if el is None:
#                         continue
#                     log("      Pay button click")
#                     bank_popup = expect_new_page(
#                         page.d, lambda: scroll_click(scope, el), timeout=20)
#                     if bank_popup is not None:
#                         log("      Pay ne nayi window kholi: %s"
#                             % ((bank_popup.url or "")[:80]))
#                     pay_ok = True
#                     page.wait_for_timeout(5000)
#                     break
#                 except Exception:
#                     continue
#             if pay_ok:
#                 break
#         if bank_popup is not None:
#             try:
#                 bank_popup.use()
#                 end = time.time() + 60
#                 while time.time() < end:
#                     st = page.d.execute_script("return document.readyState;")
#                     if st in ("interactive", "complete"):
#                         break
#                     time.sleep(1)
#             except Exception:
#                 pass

#     return "number=%s | exp=%s | holder=%s | cvv=%s | pay=%s" % (
#         "ok" if ok_n else "FAIL",
#         "ok" if ok_e else "FAIL",
#         "ok" if ok_h else "FAIL",
#         "ok" if ok_c else "FAIL",
#         "clicked" if pay_ok else "skip",
#     )


# def wait_bank_page(driver, page, secs=120):
#     """Pay ke baad ICICI / ACS / bank page (nayi window ya same)."""
#     end = time.time() + secs
#     loading_seen = False
#     while time.time() < end:
#         for pg in pages(driver):
#             try:
#                 u = (pg.url or "").lower()
#                 body = ""
#                 try:
#                     body = (pg.body_text() or "").lower()
#                 except Exception:
#                     pass
#                 if "loading bank" in body:
#                     loading_seen = True
#                     continue
#                 if any(k in u for k in (
#                     "wibmo", "acs", "icici", "3ds", "bank", "easebuzz",
#                     "secure-acs", "mumrdc",
#                 )):
#                     if "corporate id" in body or "employee id" in body:
#                         return pg
#                     if pg.count("input#corporateId, input#employeeId"):
#                         return pg
#                     if any(k in u for k in ("wibmo", "acs", "icici")):
#                         pg.wait_for_timeout(2000)
#                         if pg.count("input#corporateId"):
#                             return pg
#                 if "corporate id" in body or pg.count("input#corporateId"):
#                     return pg
#                 # bank form kisi frame ke andar bhi ho sakta hai
#                 for fr in frames(pg):
#                     try:
#                         if fr.count("input#corporateId"):
#                             return fr
#                     except Exception:
#                         continue
#             except Exception:
#                 continue
#         page.wait_for_timeout(2000)
#     if loading_seen:
#         log("      (Loading Bank Page dekha, form nahi aaya — fingerprint/block ho sakta hai)")
#     return None


# def fill_bank_corporate(driver, page, corp_id, emp_id):
#     """ICICI ACS form: input#corporateId, input#employeeId, a.btn.primary__btn.
#     Phir OTP manual."""
#     log("      bank page ka wait...")
#     bank = wait_bank_page(driver, page, secs=120)
#     if not bank:
#         return "FAIL: bank/ACS page nahi mila (Loading Bank Page atak sakta hai)"

#     log("      bank URL: %s" % ((bank.url or "")[:100]))

#     for _ in range(20):
#         try:
#             if bank.count("input#corporateId"):
#                 break
#         except Exception:
#             pass
#         bank.wait_for_timeout(1000)
#     else:
#         return "FAIL: corporateId input nahi mila"

#     try:
#         el_fill(bank, bank.first("input#corporateId"), corp_id)
#         log("      Corporate ID -> %s" % corp_id)
#     except Exception as e:
#         return "FAIL: corporateId fill: %s" % str(e)[:60]

#     bank.wait_for_timeout(800)
#     try:
#         el_fill(bank, bank.first("input#employeeId"), emp_id)
#         log("      Employee ID -> %s" % emp_id)
#     except Exception as e:
#         return "FAIL: employeeId fill: %s" % str(e)[:60]

#     bank.wait_for_timeout(1500)

#     submitted = False
#     for sel in ('a.btn.primary__btn:has-text("Submit")',
#                 'a.btn.primary__btn:has-text("SUBMIT")',
#                 'a.primary__btn',
#                 'a.btn.primary__btn',
#                 'button:has-text("Submit")',
#                 'button:has-text("SUBMIT")'):
#         try:
#             el = bank.visible_first(sel)
#             if el is None:
#                 continue
#             log("      Submit click: %s" % sel)
#             bank.use()
#             try:
#                 el.click()
#             except Exception:
#                 bank.d.execute_script("arguments[0].click();", el)
#             submitted = True
#             bank.wait_for_timeout(4000)
#             break
#         except Exception:
#             continue

#     if not submitted:
#         try:
#             bank.evaluate("if (typeof submit === 'function') submit();")
#             submitted = True
#             log("      Submit via JS submit()")
#             bank.wait_for_timeout(4000)
#         except Exception:
#             pass

#     if not submitted:
#         return "corp/emp filled par Submit nahi hua"

#     return "Corporate+Employee filled, Submit OK — ab OTP manual"


# def wait_for_order(driver, page, acct, minutes=12):
#     marks = ("thank you", "order placed", "order confirmed", "order id",
#              "your order", "order number")
#     end = time.time() + minutes * 60
#     log("      order ka intezaar (%d minute tak)..." % minutes)
#     while time.time() < end:
#         page.wait_for_timeout(5000)
#         url = ""
#         txt = ""
#         hit = None
#         for pg in pages(driver):
#             try:
#                 u = pg.url or ""
#                 t = pg.body_text() or ""
#             except Exception:
#                 continue
#             if any(m in t.lower() for m in marks) or "/thank" in u or "/orders/" in u:
#                 url, txt, hit = u, t, pg
#                 break
#         if not txt:
#             continue

#         ref = ""
#         m = re.search(r"(?:order\s*(?:id|no\.?|number)\s*[:#]?\s*)([A-Za-z0-9#\-]{4,})",
#                       txt, re.I)
#         if m:
#             ref = m.group(1).strip("#")
#         if not ref:
#             m = re.search(r"#(\d{4,})", txt)
#             ref = m.group(1) if m else ""

#         try:
#             hit.screenshot(os.path.join(OUT, "order_5_confirmed.png"))
#         except Exception:
#             pass

#         row = [time.strftime("%Y-%m-%d %H:%M:%S"), acct.get("phone", ""),
#                acct.get("email", ""), ref or "(number nahi mila)", url[:120]]
#         new_file = not os.path.exists(os.path.join(HERE, "orders.csv"))
#         with open(os.path.join(HERE, "orders.csv"), "a", newline="",
#                   encoding="utf-8") as fh:
#             w = csv.writer(fh)
#             if new_file:
#                 w.writerow(["when", "phone", "email", "order_ref", "url"])
#             w.writerow(row)
#         return "ORDER LAG GAYA -- %s  (orders.csv me likh diya)" % (
#             ref or "number nahi mila")

#     return "itne me order confirm hota nahi dikha (chhod diya, kuch bigda nahi)"


# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--product", required=True)
#     ap.add_argument("--pack", default="")
#     ap.add_argument("--unit", default="")
#     ap.add_argument("--session", default="")
#     ap.add_argument("--show", action="store_true")
#     ap.add_argument("--headless", action="store_true",
#                     help="Waterfox bina window ke (bank page ke liye theek nahi)")
#     ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
#     ap.add_argument("--card", default=DEFAULT_CARD)
#     ap.add_argument("--exp", default=DEFAULT_EXP)
#     ap.add_argument("--holder", default=DEFAULT_HOLDER)
#     ap.add_argument("--cvv", default=DEFAULT_CVV)
#     ap.add_argument("--no-pay-click", action="store_true")
#     ap.add_argument("--auto-pay", action="store_true",
#                     help="Pay khud dabao (bank page fail ho sakti hai)")
#     ap.add_argument("--manual-pay", action="store_true", default=True,
#                     help="Pay tum dabao (default, bank page ke liye better)")
#     ap.add_argument("--corp-id", default=DEFAULT_CORP_ID)
#     ap.add_argument("--emp-id", default=DEFAULT_EMP_ID)
#     ap.add_argument("--watch", type=int, default=0)
#     ap.add_argument("--hold", type=int, default=60)
#     ap.add_argument("--proxy", action="store_true", default=True,
#                     help="Geonode India residential (default ON)")
#     ap.add_argument("--no-proxy", action="store_true",
#                     help="proxy band")
#     ap.add_argument("--proxy-country", default=GEONODE_COUNTRY)
#     a = ap.parse_args()

#     path = a.session or newest_session()
#     if not path:
#         log("koi session nahi mili -- pehle make_accounts.py chalao")
#         return 1
#     if not os.path.isabs(path):
#         p2 = os.path.join(SESSIONS, path)
#         path = p2 if os.path.exists(p2) else path
#     d = json.load(open(path, encoding="utf-8"))
#     log("account : %s / %s" % (d.get("phone"), d.get("email")))
#     if not d.get("address"):
#         log("CHETAVNI: is account par pata darj nahi hai -- pehle add_address.py chalao")

#     use_proxy = not a.no_proxy
#     stop_bridge = None
#     bridge_port = None
#     if use_proxy:
#         proxy_user = geonode_username(a.proxy_country, sticky=False)
#         log("proxy : Geonode country=%s | user=%s" % (a.proxy_country, proxy_user))
#         try:
#             bridge_port, stop_bridge = start_geonode_bridge(proxy_user)
#             log("proxy : local bridge 127.0.0.1:%d" % bridge_port)
#         except Exception as e:
#             log("proxy FAIL (%s) -- bina proxy chalega" % e)
#             use_proxy = False
#             bridge_port = None

#     driver = None
#     try:
#         try:
#             driver = launch_waterfox(proxy_port=bridge_port, headless=a.headless)
#             log("browser: WATERFOX (geckodriver) -- Chrome/CDP nahi")
#         except Exception as e:
#             log("FAIL: Waterfox nahi khuli: %s" % e)
#             log("  1) D:\\streakads\\Waterfox\\waterfox.exe hona chahiye")
#             log("  2) ya set: WATERFOX_PATH / GECKODRIVER_PATH")
#             if stop_bridge is not None:
#                 stop_bridge.set()
#             return 2

#         log("   session (cookies + localStorage) daal rahe hain...")
#         try:
#             load_session(driver, d)
#         except Exception as e:
#             log("   session load me dikkat: %s" % str(e)[:120])

#         page = Scope(driver, driver.current_window_handle)

#         log("\n1) product khol rahe hain: %s" % a.product)
#         product_url = "%s/products/%s" % (SHOP, a.product)
#         nav_ok = False
#         last_err = None
#         for attempt in range(1, 4):
#             try:
#                 page.goto(pehla_url, timeout=120)
#                 nav_ok = True
#                 break
#             except Exception as e:
#                 last_err = e
#                 log("   goto fail try %d/3: %s" % (attempt, str(e)[:120]))
#                 page.wait_for_timeout(2000)

#         if not nav_ok and use_proxy:
#             # proxy se nahi chala -> bina proxy retry (Waterfox ko naye sire se
#             # kholna padta hai, proxy pref launch ke waqt tay hoti hai)
#             log("   proxy se site nahi khuli -- bina proxy retry...")
#             try:
#                 driver.quit()
#             except Exception:
#                 pass
#             if stop_bridge is not None:
#                 stop_bridge.set()
#                 stop_bridge = None
#             use_proxy = False
#             try:
#                 driver = launch_waterfox(proxy_port=None, headless=a.headless)
#                 load_session(driver, d)
#                 page = Scope(driver, driver.current_window_handle)
#                 page.goto(pehla_url, timeout=120)
#                 nav_ok = True
#                 log("   bina proxy OK (bank page baad me fail ho sakti hai)")
#             except Exception as e:
#                 last_err = e

#         if not nav_ok:
#             log("FAIL: product page nahi khuli: %s" % last_err)
#             try:
#                 driver.quit()
#             except Exception:
#                 pass
#             if stop_bridge is not None:
#                 stop_bridge.set()
#             return 2

#         page.wait_for_timeout(5000)
#         for _ in range(3):
#             page.evaluate("window.scrollBy(0, 900);")
#             page.wait_for_timeout(700)

#         title = (page.title() or "").split("|")[0].strip()
#         log("   %s" % title)
#         before = variant_id(page)
#         log("   abhi ka variant: %s" % before)

#         if a.unit:
#             log("2) unit chun rahe hain: %s" % a.unit)
#             if not pick(page, a.unit):
#                 log("   (ye unit is panne par nahi mila -- aage badh rahe hain)")
#         if a.pack:
#             log("3) pack chun rahe hain: %s" % a.pack)
#             if not pick(page, a.pack):
#                 log("   FAIL: ye pack is panne par nahi mila")
#                 page.screenshot(os.path.join(OUT, "order_fail_pack.png"),
#                                 full_page=True)
#                 driver.quit()
#                 return 3

#         after = variant_id(page)
#         log("   chunne ke baad variant: %s%s"
#             % (after, "  (badal gaya)" if after != before else "  (wahi hai)"))
#         page.screenshot(os.path.join(OUT, "order_1_product.png"))

#         log("4) add to cart")
#         sel = find(page, ADD_TO_CART)
#         if not sel:
#             log("   FAIL: 'Add to cart' ka button nahi mila")
#             driver.quit()
#             return 4
#         el = page.first(sel)
#         if not scroll_click(page, el):
#             log("   FAIL: 'Add to cart' daba nahi paye")
#             driver.quit()
#             return 4
#         page.wait_for_timeout(6000)
#         page.screenshot(os.path.join(OUT, "order_2_added.png"))

#         cart = page.evaluate_async(
#             "const cb = arguments[arguments.length - 1];"
#             "fetch('/cart.js').then(r => r.json()).then(j => cb(j))"
#             ".catch(e => cb(null));") or {}
#         log("   cart me cheezein: %d | kul Rs %s"
#             % (cart.get("item_count", 0), (cart.get("total_price", 0) or 0) / 100))
#         for it in cart.get("items", []):
#             log("      %s | %s | Rs %s"
#                 % (it.get("product_title"), it.get("variant_title"),
#                    (it.get("line_price", 0) or 0) / 100))
#         if not cart.get("item_count"):
#             log("   FAIL: cart khaali hi rah gaya")
#             driver.quit()
#             return 5
#         if after and str(cart["items"][0].get("variant_id")) != str(after):
#             log("   CHETAVNI: cart me doosra variant gaya hai (%s) -- dekh lijiye"
#                 % cart["items"][0].get("variant_id"))

#         log("5) cart")
#         if find(page, CHECKOUT):
#             log("      cart to khud hi khul gaya")
#         else:
#             sel = find(page, CART_OPEN)
#             if sel:
#                 log("      cart khol rahe hain")
#                 scroll_click(page, page.first(sel))
#                 page.wait_for_timeout(5000)
#             else:
#                 log("      /cart panne par ja rahe hain")
#                 page.goto("%s/cart" % SHOP, timeout=60)
#                 page.wait_for_timeout(5000)
#         page.screenshot(os.path.join(OUT, "order_3_cart.png"))

#         log("6) Checkout daba rahe hain")
#         sel = find(page, CHECKOUT)
#         if not sel:
#             log("   FAIL: Checkout ka button nahi mila")
#             page.screenshot(os.path.join(OUT, "order_fail_checkout.png"),
#                             full_page=True)
#             driver.quit()
#             return 6

#         btn = page.first(sel)
#         newpage = expect_new_page(driver, lambda: scroll_click(page, btn), timeout=15)
#         pay = newpage or page
#         pay.use()
#         pay.wait_for_timeout(12000)

#         blk = clear_blocker(pay)
#         if blk:
#             log("   %s" % blk)

#         # Step 7 se 12 tak ka saara kaam Fastrr ke iframe par tika hai. Wo frame
#         # na mile to sab "frame nahi mila" bol kar chup-chaap nikal jaate the aur
#         # aisa lagta tha ki script ne checkout ke baad kuch kiya hi nahi. Ab wajah
#         # saamne likhi jaati hai.
#         # Fastrr iframe dheere load hota hai — wait + re-scan
#         fr_list = []
#         for _wait in range(20):
#             fr_list = frames(pay)
#             if any("fastrr-boost-ui.pickrr.com" in (f.url or "")
#                    or "pickrr" in (f.url or "")
#                    or "shiprocket" in (f.url or "") for f in fr_list):
#                 break
#             pay.wait_for_timeout(1500)
#         log("   checkout ka panna: %s" % (pay.url or "")[:100])
#         log("   frames (%d): %s" % (
#             len(fr_list),
#             ", ".join((f.url or "?")[:60] for f in fr_list[:5]) or "koi nahi"))
#         if not any("fastrr" in (f.url or "") or "pickrr" in (f.url or "")
#                    for f in fr_list):
#             log("   CHETAVNI: Fastrr checkout ka frame nahi dikha --"
#                 " step 7 se 12 tak kuch nahi kar payenge")
#             try:
#                 pay.screenshot(os.path.join(OUT, "order_fail_checkout_frame.png"),
#                                full_page=True)
#                 log("   tasveer: out/order_fail_checkout_frame.png")
#             except Exception:
#                 pass

#         log("7) checkout ka apna pata")
#         ship = ship_address(pay, d)
#         log("      %s" % ship)
#         pay.wait_for_timeout(6000)

#         log("8) email confirm")
#         log("      %s" % confirm_email(pay, d))
#         pay.wait_for_timeout(4000)

#         st = read_checkout(pay)
#         if st:
#             log("   checkout par abhi:")
#             if st["address"]:
#                 for l in st["address"]:
#                     log("      pata: %s" % l[:90])
#             else:
#                 log("      pata: panne par koi pincode nahi dikha")
#             if st["pay"]:
#                 log("      payment ke tareeke: %s" % ", ".join(st["pay"])[:200])
#             if st["total"]:
#                 log("      panne ka aakhri daam: Rs %s" % st["total"])
#         else:
#             log("   (checkout ka frame nahi mila -- neeche ki tasveer dekhiye)")

#         log("9) Credit/Debit Card chun rahe hain")
#         log("      %s" % pick_card(pay))
#         pay.wait_for_timeout(5000)

#         log("10) gateway par %s Card chun rahe hain" % a.card_type)
#         log("      %s" % pick_card_type(pay, a.card_type))
#         pay.wait_for_timeout(3000)

#         auto_pay = bool(a.auto_pay) and not a.no_pay_click
#         log("11) Card details fill (Pay auto=%s)" % auto_pay)
#         log("      %s" % fill_card_details(
#             pay, a.card, a.exp, a.holder, a.cvv,
#             click_pay=auto_pay,
#         ))

#         if not auto_pay:
#             log("\n==========================================================")
#             log("   CARD FILL HO GAYA. Ab aap MANUALLY:")
#             log("   1) Pay button dabao")
#             log("   2) Bank page load hone do (Loading Bank Page...)")
#             log("   3) Corporate ID / Employee ID bharo (ya wait for script)")
#             log("   Jab Corporate/Employee form dikhe -> yahan Enter dabao")
#             log("==========================================================")
#             try:
#                 input("👉 Bank form dikhne ke baad Enter: ")
#             except Exception:
#                 pay.wait_for_timeout(120000)
#         else:
#             pay.wait_for_timeout(8000)

#         log("12) Bank Corporate / Employee ID")
#         log("      %s" % fill_bank_corporate(driver, pay, a.corp_id, a.emp_id))
#         pay.wait_for_timeout(2000)

#         log("\n==========================================================")
#         log("   Bank OTP page aayi ho to OTP khud bharo.")
#         log("   OTP ke baad Enter dabao (agar --hold 0).")
#         log("==========================================================")

#         log("\n   URL: %s" % pay.url)
#         try:
#             txt = pay.body_text() or ""
#         except Exception:
#             txt = ""
#         lines = [l.strip() for l in txt.splitlines() if l.strip()][:16]
#         log("   panne par: %s" % " | ".join(lines)[:260])
#         rup = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", txt)
#         log("   panne par daam: %s" % (sorted(set(rup))[:8] or "koi nahi"))
#         try:
#             pay.screenshot(os.path.join(OUT, "order_4_payment.png"))
#             log("   tasveer: out/order_4_payment.png")
#         except Exception as e:
#             log("   (tasveer nahi bani: %s)" % str(e)[:60])

#         log("\n==========================================================")
#         log("   CARD + CORP/EMP FILL HO GAYA. Bank OTP aap khud bhariye.")
#         log("==========================================================")
#         if a.watch:
#             log("   OTP ke baad script order ka wait karegi.")
#             log("      %s" % wait_for_order(driver, pay, d, a.watch))
#         if a.hold == 0:
#             log("   Browser khula rahega. Kaam khatam ho to yahan Enter dabaiye.")
#             try:
#                 input()
#             except Exception:
#                 pay.wait_for_timeout(600000)
#         else:
#             log("   (%ds baad band)" % a.hold)
#             pay.wait_for_timeout(a.hold * 1000)
#     finally:
#         if driver is not None:
#             try:
#                 driver.quit()
#             except Exception:
#                 pass
#         if stop_bridge is not None:
#             stop_bridge.set()
#     return 0


# if __name__ == "__main__":
#     sys.exit(main())








# #!/usr/bin/env python3
# """place_order.py — Estuary order via Waterfox (Selenium) + Geonode rotating.

# Chrome/Playwright hata kar Waterfox + geckodriver.
# Flow: product -> cart -> checkout -> card -> (manual Pay) -> bank corp/emp -> OTP manual.
# """
# import os
# import re
# import sys
# import glob
# import json
# import csv
# import time
# import argparse
# import socket
# import threading
# import uuid
# import subprocess
# import tempfile
# import shutil
# import asyncio
# from urllib.parse import urlparse

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.firefox.service import Service as FirefoxService

# sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# HERE = os.path.dirname(os.path.abspath(__file__))
# SESSIONS = os.path.join(HERE, "sessions")
# OUT = os.path.join(HERE, "out")
# SHOP = "https://estuaryworld.com"
# os.makedirs(OUT, exist_ok=True)

# ADD_TO_CART = ["button.add-to-cart", "button:has-text('Add to cart')"]
# CART_OPEN = ["a[data-js-sidebar-handle]", "a[title='Open cart']"]
# CHECKOUT = ["#yt-checkout-button", "button:has-text('Checkout')",
#             "a:has-text('Checkout')"]

# DEFAULT_CARD = "0000000000000000"
# DEFAULT_EXP = "01/30"
# DEFAULT_HOLDER = "Test Holder"
# DEFAULT_CVV = "000"
# DEFAULT_CORP_ID = "streakads"
# DEFAULT_EMP_ID = "CHANGE_ME_EMP_ID"
# # ================= GEONODE (ROTATING SOCKS5) =================
# # Dashboard: India + SOCKS5 + Rotating + Port 11000
# # Sticky (12000) mat use — rotating jaise pehle chal raha tha.
# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"   # Singapore gateway (rotating)
# GEONODE_PORT = "11000"                 # ROTATING SOCKS5 (12000 = sticky)
# GEONODE_COUNTRY = "in"




# def log(*a):
#     print(*a, flush=True)


# # ---------- Geonode SOCKS5 -> local HTTP bridge ----------
# def _free_port():
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind(("127.0.0.1", 0))
#     port = s.getsockname()[1]
#     s.close()
#     return port


# async def _socks5_connect(dst_host, dst_port, user, pw):
#     reader, writer = await asyncio.open_connection(GEONODE_HOST, int(GEONODE_PORT))
#     writer.write(b"\x05\x01\x02")
#     await writer.drain()
#     resp = await reader.readexactly(2)
#     if resp[1] != 0x02:
#         raise OSError("SOCKS5 auth method refused")
#     ub, pb = user.encode(), pw.encode()
#     writer.write(b"\x01" + bytes([len(ub)]) + ub + bytes([len(pb)]) + pb)
#     await writer.drain()
#     a = await reader.readexactly(2)
#     if a[1] != 0x00:
#         raise OSError("SOCKS5 auth failed")
#     dbytes = dst_host.encode()
#     writer.write(
#         b"\x05\x01\x00\x03" + bytes([len(dbytes)]) + dbytes + int(dst_port).to_bytes(2, "big")
#     )
#     await writer.drain()
#     r = await reader.readexactly(4)
#     if r[1] != 0x00:
#         raise OSError("SOCKS5 connect failed code=%s" % r[1])
#     atyp = r[3]
#     if atyp == 0x01:
#         await reader.readexactly(4)
#     elif atyp == 0x03:
#         ln = await reader.readexactly(1)
#         await reader.readexactly(ln[0])
#     elif atyp == 0x04:
#         await reader.readexactly(16)
#     await reader.readexactly(2)
#     return reader, writer


# async def _pipe(src, dst):
#     try:
#         while True:
#             data = await src.read(65536)
#             if not data:
#                 break
#             dst.write(data)
#             await dst.drain()
#     except Exception:
#         pass
#     finally:
#         try:
#             dst.close()
#         except Exception:
#             pass


# def start_geonode_bridge(username):
#     """Background thread: local HTTP proxy -> Geonode SOCKS5. Returns (port, stop_event)."""
#     local_port = _free_port()
#     stop = threading.Event()
#     ready = threading.Event()

#     async def run_server():
#         tasks = set()

#         async def handle(client_reader, client_writer):
#             tasks.add(asyncio.current_task())
#             up_writer = None
#             try:
#                 header = b""
#                 while b"\r\n\r\n" not in header:
#                     chunk = await client_reader.read(65536)
#                     if not chunk:
#                         return
#                     header += chunk
#                     if len(header) > 262144:
#                         return
#                 head, _, leftover = header.partition(b"\r\n\r\n")
#                 request_line = head.split(b"\r\n", 1)[0].decode("latin1")
#                 method, target, _ver = request_line.split(" ", 2)
#                 if method.upper() == "CONNECT":
#                     host, _, port = target.rpartition(":")
#                     up_reader, up_writer = await _socks5_connect(
#                         host, int(port), username, GEONODE_PASS
#                     )
#                     client_writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
#                     await client_writer.drain()
#                     if leftover:
#                         up_writer.write(leftover)
#                         await up_writer.drain()
#                 else:
#                     u = urlparse(target)
#                     host, port = u.hostname, u.port or 80
#                     up_reader, up_writer = await _socks5_connect(
#                         host, int(port), username, GEONODE_PASS
#                     )
#                     path = u.path or "/"
#                     if u.query:
#                         path += "?" + u.query
#                     rebuilt = header.replace(target.encode(), path.encode(), 1)
#                     up_writer.write(rebuilt)
#                     await up_writer.drain()
#                 await asyncio.gather(
#                     _pipe(client_reader, up_writer), _pipe(up_reader, client_writer)
#                 )
#             except Exception:
#                 try:
#                     client_writer.close()
#                 except Exception:
#                     pass
#                 if up_writer is not None:
#                     try:
#                         up_writer.close()
#                     except Exception:
#                         pass
#             finally:
#                 tasks.discard(asyncio.current_task())

#         server = await asyncio.start_server(handle, "127.0.0.1", local_port)
#         ready.set()
#         while not stop.is_set():
#             await asyncio.sleep(0.3)
#         server.close()
#         await server.wait_closed()
#         for t in list(tasks):
#             if not t.done():
#                 t.cancel()

#     def thread_main():
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         try:
#             loop.run_until_complete(run_server())
#         finally:
#             loop.close()

#     t = threading.Thread(target=thread_main, daemon=True)
#     t.start()
#     if not ready.wait(timeout=10):
#         raise RuntimeError("Geonode bridge start fail")
#     return local_port, stop


# def geonode_username(country=None, sticky=False):
#     """Rotating residential username (default).
#     sticky=True only if kabhi sticky chahiye (port 12000 + lifetime).
#     """
#     c = (country or GEONODE_COUNTRY).lower()
#     base = GEONODE_USER_BASE.format(c)
#     if sticky:
#         sess = uuid.uuid4().hex[:8]
#         return "%s-session-%s-lifetime-30" % (base, sess)
#     return base


# # ================= WATERFOX (Selenium + geckodriver) =================
# # Chrome/CDP ki jagah ab Waterfox chalti hai.
# # Proxy wahi ka wahi: Geonode SOCKS5 -> upar wala local HTTP bridge -> Waterfox
# # ka manual HTTP proxy pref. Yaani exit IP pehle jaisa hi India ka residential.
# #
# # Playwright kyun nahi: Playwright 1.58 ka BiDi mode connect hote hi
# # 'network.addDataCollector' bhejta hai, jo Gecko 141+ ka command hai. Waterfox
# # 140 par wo 'unknown command' deta hai aur session wahin mar jaati hai. Isliye
# # Waterfox ko geckodriver (WebDriver) se chalaya jaata hai.

# WATERFOX_CANDIDATES = [
#     os.environ.get("WATERFOX_PATH") or "",
#     os.path.join(os.path.dirname(HERE), "Waterfox", "waterfox.exe"),
#     r"D:\streakads\Waterfox\waterfox.exe",
#     r"C:\Program Files\Waterfox\waterfox.exe",
#     r"C:\Program Files (x86)\Waterfox\waterfox.exe",
#     "/usr/bin/waterfox",
#     "/Applications/Waterfox.app/Contents/MacOS/waterfox",
# ]

# GECKODRIVER_CANDIDATES = [
#     os.environ.get("GECKODRIVER_PATH") or "",
#     shutil.which("geckodriver") or "",
#     os.path.join(os.path.dirname(HERE), "geckodriver-v0.36.0-win64",
#                  "geckodriver.exe"),
#     r"D:\streakads\geckodriver-v0.36.0-win64\geckodriver.exe",
#     os.path.expandvars(
#         r"%USERPROFILE%\.wdm\drivers\geckodriver\win64\v0.36.0\geckodriver.exe"),
# ]

# # Waterfox apne aap ko Firefox hi batati hai; UA ko Chrome banane ka koi fayda
# # nahi -- Gecko engine + Chrome UA ka mel na khana khud ek pehchaan hai.
# WATERFOX_UA = None      # None = Waterfox ki apni UA

# VIEWPORT = {"width": 1500, "height": 950}


# def find_waterfox_exe():
#     for c in WATERFOX_CANDIDATES:
#         if c and os.path.isfile(c):
#             return c
#     return None


# def find_geckodriver():
#     for c in GECKODRIVER_CANDIDATES:
#         if c and os.path.isfile(c):
#             return c
#     return None


# def launch_waterfox(proxy_port=None, headless=False):
#     """Waterfox + geckodriver. Returns driver.

#     proxy_port: upar wale local HTTP bridge ka port (None = bina proxy).
#     """
#     exe = find_waterfox_exe()
#     if not exe:
#         raise RuntimeError(
#             "Waterfox nahi mili. WATERFOX_PATH set karo ya "
#             "D:\\streakads\\Waterfox\\waterfox.exe rakho.")
#     drv_path = find_geckodriver()
#     if not drv_path:
#         raise RuntimeError(
#             "geckodriver nahi mila. GECKODRIVER_PATH set karo ya "
#             "D:\\streakads\\geckodriver-v0.36.0-win64\\geckodriver.exe rakho.")

#     opts = FirefoxOptions()
#     opts.binary_location = exe
#     if headless:
#         opts.add_argument("-headless")

#     # --- proxy: bridge ko manual HTTP proxy ki tarah ---
#     if proxy_port:
#         opts.set_preference("network.proxy.type", 1)
#         opts.set_preference("network.proxy.http", "127.0.0.1")
#         opts.set_preference("network.proxy.http_port", int(proxy_port))
#         opts.set_preference("network.proxy.ssl", "127.0.0.1")
#         opts.set_preference("network.proxy.ssl_port", int(proxy_port))
#         opts.set_preference("network.proxy.share_proxy_settings", True)
#         # DNS bhi proxy ke us paar -- warna local DNS leak hota hai
#         opts.set_preference("network.proxy.socks_remote_dns", True)
#         opts.set_preference("network.proxy.no_proxies_on", "")
#     else:
#         opts.set_preference("network.proxy.type", 0)

#     # --- automation ke nishaan kam karo (Chrome build me jo init script tha) ---
#     opts.set_preference("dom.webdriver.enabled", False)
#     opts.set_preference("useAutomationExtension", False)
#     opts.set_preference("marionette.enabled", True)
#     opts.set_preference("privacy.resistFingerprinting", False)
#     opts.set_preference("intl.accept_languages", "en-IN, en")   # locale="en-IN"
#     opts.set_preference("browser.startup.homepage", "about:blank")
#     opts.set_preference("browser.startup.page", 0)
#     opts.set_preference("datareporting.healthreport.uploadEnabled", False)
#     opts.set_preference("app.update.auto", False)
#     opts.set_preference("browser.shell.checkDefaultBrowser", False)
#     # popup/nayi window: Pay ke baad bank page nayi window me aati hai
#     opts.set_preference("browser.link.open_newwindow", 3)        # naye tab me
#     opts.set_preference("browser.link.open_newwindow.restriction", 0)
#     if WATERFOX_UA:
#         opts.set_preference("general.useragent.override", WATERFOX_UA)

#     # ignore_https_errors=True ka Selenium roop
#     opts.set_capability("acceptInsecureCerts", True)
#     opts.set_capability("pageLoadStrategy", "eager")   # wait_until="domcontentloaded"

#     service = FirefoxService(executable_path=drv_path, log_output=os.devnull)

#     log("Waterfox  : %s" % exe)
#     log("geckodriver: %s" % drv_path)
#     driver = webdriver.Firefox(service=service, options=opts)

#     driver.set_page_load_timeout(120)
#     driver.set_script_timeout(60)
#     driver.implicitly_wait(0)       # har intezaar humara apna, chhupa hua nahi

#     # viewport ~1500x950 (window chrome ka farq nikaal kar)
#     try:
#         driver.set_window_size(VIEWPORT["width"], VIEWPORT["height"] + 90)
#         inner = driver.execute_script(
#             "return [window.innerWidth, window.innerHeight];")
#         dw = VIEWPORT["width"] - int(inner[0])
#         dh = VIEWPORT["height"] - int(inner[1])
#         if dw or dh:
#             driver.set_window_size(VIEWPORT["width"] + dw,
#                                    VIEWPORT["height"] + 90 + dh)
#     except Exception:
#         pass
#     return driver


# def load_session(driver, d):
#     """storage_state (cookies + localStorage) Waterfox me daalo.

#     Cookie tabhi jaati hai jab browser usi domain par khada ho, isliye har
#     origin ek baar khola jaata hai. Analytics ke cookies (bing/clarity/fb)
#     chhod diye jaate hain -- login ya checkout unse nahi chalta.
#     """
#     st = d.get("state") or {}
#     cookies = st.get("cookies") or []
#     origins = st.get("origins") or []

#     wanted = {
#         "https://estuaryworld.com": ("estuaryworld.com",),
#         "https://fastrr-boost-ui.pickrr.com": ("pickrr.com", "shiprocket.in"),
#     }
#     # jis origin ka localStorage hai wo bhi list me aa jaye
#     for o in origins:
#         og = o.get("origin") or ""
#         if og and og not in wanted:
#             host = urlparse(og).hostname or ""
#             wanted[og] = (host,)

#     ok_c = fail_c = ok_ls = 0
#     for origin, suffixes in wanted.items():
#         try:
#             driver.get(origin)
#         except Exception as e:
#             log("   %s khula nahi (%s) -- iske cookies chhod diye"
#                 % (origin, str(e)[:60]))
#             continue
#         time.sleep(1.0)

#         for c in cookies:
#             dom = (c.get("domain") or "").lstrip(".")
#             if not any(dom == s or dom.endswith("." + s) or s in dom
#                        for s in suffixes):
#                 continue
#             ck = {
#                 "name": c.get("name"),
#                 "value": c.get("value"),
#                 "path": c.get("path") or "/",
#                 "domain": c.get("domain"),
#                 "secure": bool(c.get("secure")),
#             }
#             exp = c.get("expires")
#             if exp and exp > 0:
#                 ck["expiry"] = int(exp)
#             ss = c.get("sameSite")
#             if ss in ("Strict", "Lax", "None"):
#                 ck["sameSite"] = ss
#             try:
#                 driver.add_cookie(ck)
#                 ok_c += 1
#             except Exception:
#                 # domain thoda alag ho to bina domain ke daal ke dekho
#                 ck.pop("domain", None)
#                 try:
#                     driver.add_cookie(ck)
#                     ok_c += 1
#                 except Exception:
#                     fail_c += 1

#         for o in origins:
#             if (o.get("origin") or "") != origin:
#                 continue
#             items = o.get("localStorage") or []
#             if not items:
#                 continue
#             try:
#                 driver.execute_script(
#                     "for (const kv of arguments[0]) {"
#                     "  try { localStorage.setItem(kv.name, kv.value); } catch (e) {}"
#                     "}", items)
#                 ok_ls += len(items)
#             except Exception as e:
#                 log("   localStorage (%s): %s" % (origin, str(e)[:60]))

#     log("   session: %d cookie daale (%d chhode), %d localStorage"
#         % (ok_c, fail_c, ok_ls))
#     return ok_c


# # ---------- Playwright ke jo thode selectors the, unka Selenium roop ----------
# # Script me sirf ye khaas selectors the: :has-text(), :text-is(), :has(), :visible.
# # CSS baaki sab seedha chalta hai.

# _HAS_TEXT = re.compile(r"^(?P<base>.*?):has-text\((?P<q>['\"])(?P<txt>.*?)(?P=q)\)$")
# _TEXT_IS = re.compile(r"^(?P<base>.*?):text-is\((?P<q>['\"])(?P<txt>.*?)(?P=q)\)$")
# _HAS = re.compile(r"^(?P<base>.*?):has\((?P<inner>.+)\)$")


# def _css_step_to_xpath(css):
#     """'span.lang-en' -> 'span[contains(concat(" ",@class," ")," lang-en ")]'"""
#     css = (css or "").strip() or "*"
#     m = re.match(r"^([a-zA-Z][\w-]*|\*)?(.*)$", css)
#     tag = m.group(1) or "*"
#     rest = m.group(2) or ""
#     preds = []
#     for part in re.finditer(r"\.([\w-]+)|#([\w-]+)|\[([^\]]+)\]", rest):
#         cls, idd, attr = part.group(1), part.group(2), part.group(3)
#         if cls:
#             preds.append(
#                 'contains(concat(" ", normalize-space(@class), " "), " %s ")' % cls)
#         elif idd:
#             preds.append('@id="%s"' % idd)
#         elif attr:
#             am = re.match(r"^\s*([\w-]+)\s*(?:([~^$*|]?=)\s*['\"]?([^'\"]*)['\"]?)?\s*$",
#                           attr)
#             if not am:
#                 continue
#             name, op, val = am.group(1), am.group(2), am.group(3)
#             if not op:
#                 preds.append("@%s" % name)
#             elif op == "=":
#                 preds.append('@%s="%s"' % (name, val))
#             elif op == "*=":
#                 preds.append('contains(@%s, "%s")' % (name, val))
#             elif op == "^=":
#                 preds.append('starts-with(@%s, "%s")' % (name, val))
#             else:
#                 preds.append('contains(@%s, "%s")' % (name, val))
#     return tag + "".join("[%s]" % p for p in preds)


# def _one_selector(sel):
#     """Ek selector -> (by, expr, visible_only)."""
#     sel = sel.strip()
#     visible_only = False
#     if ":visible" in sel:
#         visible_only = True
#         sel = sel.replace(":visible", "")

#     m = _HAS_TEXT.match(sel)
#     if m:
#         xp = "//%s[contains(normalize-space(.), %s)]" % (
#             _css_step_to_xpath(m.group("base")), _xq(m.group("txt")))
#         return By.XPATH, xp, visible_only

#     m = _TEXT_IS.match(sel)
#     if m:
#         xp = "//%s[normalize-space(.)=%s]" % (
#             _css_step_to_xpath(m.group("base")), _xq(m.group("txt")))
#         return By.XPATH, xp, visible_only

#     m = _HAS.match(sel)
#     if m:
#         inner = m.group("inner").strip()
#         im = _TEXT_IS.match(inner)
#         if im:
#             inner_xp = "%s[normalize-space(.)=%s]" % (
#                 _css_step_to_xpath(im.group("base")), _xq(im.group("txt")))
#         else:
#             ihm = _HAS_TEXT.match(inner)
#             if ihm:
#                 inner_xp = "%s[contains(normalize-space(.), %s)]" % (
#                     _css_step_to_xpath(ihm.group("base")), _xq(ihm.group("txt")))
#             else:
#                 inner_xp = _css_step_to_xpath(inner)
#         xp = "//%s[.//%s]" % (_css_step_to_xpath(m.group("base")), inner_xp)
#         return By.XPATH, xp, visible_only

#     return By.CSS_SELECTOR, sel, visible_only


# def _xq(text):
#     """XPath me quote -- text me ' ho to concat() lagta hai."""
#     if "'" not in text:
#         return "'%s'" % text
#     if '"' not in text:
#         return '"%s"' % text
#     parts = text.split("'")
#     return "concat(%s)" % ", ".join(
#         ["'%s'" % p if i == 0 else "\"'\", '%s'" % p for i, p in enumerate(parts)])


# def _split_selectors(sel):
#     """Top-level comma par todo (bracket/quote ke andar wale comma chhod kar)."""
#     out, depth, cur, quote = [], 0, "", None
#     for ch in sel:
#         if quote:
#             cur += ch
#             if ch == quote:
#                 quote = None
#             continue
#         if ch in "'\"":
#             quote = ch
#             cur += ch
#         elif ch in "([":
#             depth += 1
#             cur += ch
#         elif ch in ")]":
#             depth -= 1
#             cur += ch
#         elif ch == "," and depth == 0:
#             out.append(cur)
#             cur = ""
#         else:
#             cur += ch
#     if cur.strip():
#         out.append(cur)
#     return [s.strip() for s in out if s.strip()]


# # ---------- Scope: ek window ya uske andar ka ek frame ----------
# class Scope(object):
#     """Selenium me frame ke andar kaam karne ke liye har baar switch karna padta
#     hai. Isliye har Scope apna raasta (window handle + frame index chain) yaad
#     rakhta hai aur kaam se pehle khud us jagah pahunch jaata hai."""

#     def __init__(self, driver, handle, path=(), url=""):
#         self.d = driver
#         self.handle = handle
#         self.path = tuple(path)
#         self._url = url

#     # -- jagah par pahuncho --
#     def use(self):
#         """Us window/frame me pahuncho jiska ye Scope hai.

#         Frame me index se ghusna bharosemand nahi: switch_to.frame(int) window.frames
#         ka index leta hai, jabki humne raasta 'iframe, frame' elements gin kar banaya
#         tha. Bina src wale ya baad me bane iframe se dono ginti alag ho jaati hain aur
#         aadmi doosre frame me pahunch jaata hai. Isliye jis list se raasta bana tha,
#         switch bhi usi list ke element se hota hai.
#         """
#         if self.d.current_window_handle != self.handle:
#             self.d.switch_to.window(self.handle)
#         self.d.switch_to.default_content()
#         for idx in self.path:
#             els = self.d.find_elements(By.CSS_SELECTOR, "iframe, frame")
#             if idx >= len(els):
#                 raise RuntimeError("frame %d ab maujood nahi (kul %d)"
#                                    % (idx, len(els)))
#             self.d.switch_to.frame(els[idx])
#         return self

#     @property
#     def url(self):
#         if self.path:
#             return self._url
#         try:
#             self.use()
#             return self.d.current_url
#         except Exception:
#             return self._url

#     def is_page(self):
#         return not self.path

#     # -- dhoondho --
#     def query(self, sel, visible=None):
#         self.use()
#         out = []
#         for one in _split_selectors(sel):
#             by, expr, vis_only = _one_selector(one)
#             want_vis = vis_only if visible is None else visible
#             try:
#                 els = self.d.find_elements(by, expr)
#             except Exception:
#                 continue
#             for e in els:
#                 if want_vis:
#                     try:
#                         if not e.is_displayed():
#                             continue
#                     except Exception:
#                         continue
#                 out.append(e)
#         return out

#     def count(self, sel):
#         return len(self.query(sel))

#     def first(self, sel):
#         got = self.query(sel)
#         return got[0] if got else None

#     def visible_first(self, sel):
#         got = self.query(sel, visible=True)
#         return got[0] if got else None

#     # -- padho --
#     def body_text(self):
#         try:
#             self.use()
#             return self.d.execute_script(
#                 "return document.body ? document.body.innerText : '';") or ""
#         except Exception:
#             return ""

#     def evaluate(self, js, *args):
#         self.use()
#         return self.d.execute_script(js, *args)

#     def evaluate_async(self, js, *args):
#         self.use()
#         return self.d.execute_async_script(js, *args)

#     def title(self):
#         self.use()
#         return self.d.title or ""

#     # -- Playwright jaisa wait --
#     def wait_for_timeout(self, ms):
#         time.sleep(ms / 1000.0)

#     def goto(self, url, timeout=120):
#         self.use()
#         old = self.d.timeouts.page_load if hasattr(self.d, "timeouts") else None
#         try:
#             self.d.set_page_load_timeout(timeout)
#             self.d.get(url)
#         finally:
#             if old:
#                 try:
#                     self.d.set_page_load_timeout(old)
#                 except Exception:
#                     pass

#     def screenshot(self, path, full_page=False):
#         self.use()
#         if full_page:
#             try:
#                 self.d.get_full_page_screenshot_as_file(path)
#                 return
#             except Exception:
#                 pass
#         self.d.save_screenshot(path)


# def pages(driver):
#     """Sabhi khuli windows/tabs -- Playwright ke context.pages jaisa."""
#     out = []
#     cur = None
#     try:
#         cur = driver.current_window_handle
#     except Exception:
#         pass
#     for h in list(driver.window_handles):
#         out.append(Scope(driver, h))
#     if cur:
#         try:
#             driver.switch_to.window(cur)
#         except Exception:
#             pass
#     return out


# def frames(page):
#     """Page ke andar ke saare frames (nested bhi), URL ke saath."""
#     d = page.d
#     found = []

#     def _goto(path):
#         d.switch_to.default_content()
#         for idx in path:
#             els = d.find_elements(By.CSS_SELECTOR, "iframe, frame")
#             if idx >= len(els):
#                 raise RuntimeError("frame gayab")
#             d.switch_to.frame(els[idx])

#     def walk(path):
#         try:
#             _goto(path)
#             n = len(d.find_elements(By.CSS_SELECTOR, "iframe, frame"))
#         except Exception:
#             return
#         for i in range(n):
#             child = path + (i,)
#             try:
#                 _goto(child)
#                 url = d.execute_script("return location.href;") or ""
#             except Exception:
#                 continue
#             found.append(Scope(d, page.handle, child, url))
#             walk(child)

#     try:
#         if d.current_window_handle != page.handle:
#             d.switch_to.window(page.handle)
#         walk(())
#         d.switch_to.default_content()
#     except Exception:
#         pass
#     return found


# # ---------- element ke saath kaam ----------
# def el_fill(scope, el, value):
#     """Playwright ke fill() jaisa: purana hatao, naya likho, event bhejo."""
#     scope.use()
#     try:
#         el.click()
#     except Exception:
#         pass
#     try:
#         el.clear()
#     except Exception:
#         pass
#     try:
#         el.send_keys(Keys.CONTROL, "a")
#         el.send_keys(Keys.DELETE)
#     except Exception:
#         pass
#     el.send_keys(str(value))
#     try:
#         scope.d.execute_script(
#             "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
#             "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", el)
#     except Exception:
#         pass


# def el_type(scope, el, value, delay=50):
#     """Playwright ke type(delay=) jaisa -- ek ek akshar, thoda ruk kar."""
#     scope.use()
#     for ch in str(value):
#         el.send_keys(ch)
#         time.sleep(delay / 1000.0)


# def el_value(el):
#     try:
#         return el.get_attribute("value") or ""
#     except Exception:
#         return ""


# def real_click(scope, el):
#     """Aadmi jaisa click: pahuncho, thoda ruko, dabao, chhodo."""
#     scope.use()
#     try:
#         scope.d.execute_script(
#             "arguments[0].scrollIntoView({block:'center', inline:'center'});", el)
#         time.sleep(0.4)
#     except Exception:
#         pass
#     try:
#         ActionChains(scope.d).move_to_element(el).pause(0.4) \
#             .click_and_hold(el).pause(0.09).release().perform()
#         return True
#     except Exception:
#         try:
#             el.click()
#             return True
#         except Exception:
#             return False


# def in_view(scope, el):
#     try:
#         return bool(scope.d.execute_script(
#             "const r = arguments[0].getBoundingClientRect();"
#             "return r.width > 0 && r.height > 0 && r.top >= 0 && r.left >= 0"
#             " && r.bottom <= (window.innerHeight || 0)"
#             " && r.right <= (window.innerWidth || 0);", el))
#     except Exception:
#         return False


# def scroll_click(scope, el, tries=3):
#     """Teen tareeke, usi kram me: asli mouse -> click() -> DOM click."""
#     for _ in range(tries):
#         scope.use()
#         try:
#             scope.d.execute_script(
#                 "arguments[0].scrollIntoView({block:'center', inline:'center'});", el)
#         except Exception:
#             pass
#         time.sleep(0.6)
#         if in_view(scope, el):
#             try:
#                 ActionChains(scope.d).move_to_element(el).pause(0.3) \
#                     .click_and_hold(el).pause(0.09).release().perform()
#                 return "mouse"
#             except Exception:
#                 pass
#     try:
#         scope.use()
#         el.click()
#         return "click()"
#     except Exception:
#         pass
#     try:
#         scope.use()
#         scope.d.execute_script("arguments[0].click();", el)
#         return "dom-click"
#     except Exception:
#         return None


# def expect_new_page(driver, do_click, timeout=15):
#     """Click ke baad nayi window khuli to uska Scope do, warna None."""
#     before = set(driver.window_handles)
#     try:
#         do_click()
#     except Exception:
#         pass
#     end = time.time() + timeout
#     while time.time() < end:
#         naye = set(driver.window_handles) - before
#         if naye:
#             h = naye.pop()
#             try:
#                 driver.switch_to.window(h)
#             except Exception:
#                 pass
#             return Scope(driver, h)
#         time.sleep(0.5)
#     return None


# # ---------- session / product helpers ----------
# def newest_session():
#     fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
#     return fs[-1] if fs else None


# def find(scope, sels):
#     for s in sels:
#         try:
#             if scope.query(s, visible=True):
#                 return s
#         except Exception:
#             continue
#     return None


# def variant_id(page):
#     return page.evaluate(
#         """const f = document.querySelector('form[action*="/cart/add"]');
#            const i = f && f.querySelector('input[name="id"], select[name="id"]');
#            return i ? String(i.value) : null;""")


# def pick(page, value):
#     res = page.evaluate(
#         """const v = arguments[0];
#            const rs = [...document.querySelectorAll('input[type=radio]')]
#                       .filter(x => (x.value || '').trim() === v);
#            if (!rs.length) return 'nahi-mila';
#            const r = rs[0];
#            if (r.checked) return 'pehle-se-chuna';
#            r.click();
#            return 'daba-diya';""", value)
#     log("      %s" % res)
#     if res == "nahi-mila":
#         return False
#     page.wait_for_timeout(2500)
#     return True


# # ---------- checkout (Fastrr) ke frames ----------
# def sr_frame(page):
#     """Address form wala Fastrr frame — #pincode / Pincode label se."""
#     for fr in frames(page):
#         u = (fr.url or "").lower()
#         try:
#             if fr.count("#pincode") or fr.count("input[placeholder*='incode' i]"):
#                 return fr
#             body = (fr.body_text() or "")
#             if "Add shipping address" in body or "Pincode" in body:
#                 if "fastrr" in u or "pickrr" in u or "shiprocket" in u or fr.count("input"):
#                     return fr
#         except Exception:
#             pass
#     # URL se bhi
#     for fr in frames(page):
#         u = (fr.url or "").lower()
#         if "fastrr-boost-ui.pickrr.com" in u or "pickrr" in u:
#             return fr
#     return None


# def sr_frame_any(page):
#     for fr in frames(page):
#         u = (fr.url or "").lower()
#         if "fastrr" in u or "pickrr" in u or "shiprocket" in u:
#             try:
#                 if (fr.body_text() or "").strip():
#                     return fr
#             except Exception:
#                 pass
#     # fallback: koi bhi frame jisme payment / address
#     for fr in frames(page):
#         try:
#             b = (fr.body_text() or "").lower()
#             if "pincode" in b or "shipping" in b or "payment method" in b:
#                 return fr
#         except Exception:
#             pass
#     return None


# def _find_input(scope, selectors):
#     """Pehla milne wala input element."""
#     for sel in selectors:
#         try:
#             el = scope.first(sel)
#             if el is not None:
#                 return el, sel
#         except Exception:
#             continue
#     return None, None


# def ship_address(page, acct):
#     """Add shipping address form fill (Waterfox / Selenium).

#     Selectors: id pehle, phir name/placeholder fallback — kyunki theme
#     kabhi #pincode, kabhi sirf label+input deta hai.
#     """
#     f = None
#     for _ in range(25):
#         f = sr_frame(page)
#         if f:
#             break
#         page.wait_for_timeout(1200)
#     if not f:
#         # last try: saari frames log
#         frs = frames(page)
#         log("      address frame nahi mila | frames=%d %s" % (
#             len(frs),
#             ", ".join((x.url or "?")[:50] for x in frs[:6]) or "none"))
#         return "checkout ka pata wala form nahi mila (shayad pata pehle se hai)"

#     log("      address frame: %s" % ((f.url or "")[:80]))

#     ad = acct.get("address") or {}
#     pin = str(ad.get("zip") or ad.get("pincode") or "000000")
#     first = ad.get("first_name") or "Ishan"
#     last = ad.get("last_name") or "Gupta"
#     line1 = ad.get("address1") or "55/34 Shastri Nagar"
#     line2 = ad.get("address2") or "Near Kidwai Nagar Market"
#     city = ad.get("city") or "Kanpur"
#     state = ad.get("province") or ad.get("state") or "Uttar Pradesh"
#     email = acct.get("email") or ""

#     def _put(label, selectors, val):
#         el, used = _find_input(f, selectors)
#         if el is None:
#             log("      %s: input nahi mila %s" % (label, selectors[:2]))
#             return False
#         try:
#             f.use()
#             el_fill(f, el, val)
#             got = ""
#             try:
#                 got = el_value(el) or ""
#             except Exception:
#                 pass
#             log("      %s -> '%s' (%s)" % (label, (got or val)[:40], used))
#             return True
#         except Exception as e:
#             log("      %s FAIL: %s" % (label, str(e)[:50]))
#             return False

#     # Pincode pehle — city/state auto-fill ke liye
#     _put("Pincode", [
#         "#pincode",
#         "input#pincode",
#         "input[name='pincode']",
#         "input[name='zip']",
#         "input[placeholder*='incode' i]",
#         "input[placeholder*='Pincode' i]",
#     ], pin)
#     page.wait_for_timeout(4500)  # city/state auto

#     _put("First name", [
#         "#name", "input#name", "input[name='name']",
#         "input[name='firstName']", "input[name='first_name']",
#         "input[placeholder*='First' i]",
#     ], first)

#     _put("Last name", [
#         "#lastName", "input#lastName", "input[name='lastName']",
#         "input[name='last_name']", "input[placeholder*='Last' i]",
#     ], last)

#     _put("Address1", [
#         "#line1", "input#line1", "input[name='line1']",
#         "input[name='address1']", "input[name='address']",
#         "input[placeholder*='Flat' i]",
#         "input[placeholder*='house' i]",
#     ], line1)

#     _put("Address2", [
#         "#line2", "input#line2", "input[name='line2']",
#         "input[name='address2']",
#         "input[placeholder*='Area' i]",
#         "input[placeholder*='street' i]",
#         "input[placeholder*='Landmark' i]",
#     ], line2)

#     _put("City", [
#         "#city", "input#city", "input[name='city']",
#         "input[placeholder*='City' i]",
#     ], city)

#     _put("State", [
#         "#state", "input#state", "input[name='state']",
#         "input[placeholder*='State' i]",
#         "select#state", "select[name='state']",
#     ], state)

#     if email:
#         _put("Email", [
#             "#email", "input#email", "input[name='email']",
#             "input[type='email']", "input[placeholder*='mail' i]",
#         ], email)

#     # Home address type radio/checkbox
#     try:
#         for sel in ("input[name='home']", "input[value='home']",
#                     "input[type='radio'][value='Home']"):
#             home = f.first(sel)
#             if home is not None:
#                 f.use()
#                 try:
#                     if not home.is_selected():
#                         f.d.execute_script("arguments[0].click();", home)
#                 except Exception:
#                     try:
#                         home.click()
#                     except Exception:
#                         pass
#                 break
#     except Exception:
#         pass

#     page.wait_for_timeout(1000)

#     # Submit address
#     btn = None
#     for sel in (
#         "#addAddressBtn",
#         "button#addAddressBtn",
#         "button:has-text('Add address')",
#         "button:has-text('Save address')",
#         "button:has-text('Add Address')",
#         "button:has-text('Continue')",
#         "[class*='addAddress']",
#         "button[type='submit']",
#     ):
#         try:
#             el = f.first(sel)
#             if el is not None:
#                 btn, btn_sel = el, sel
#                 break
#         except Exception:
#             continue

#     if btn is None:
#         return "address fields try hue par 'Add address' button nahi mila"

#     log("      Add address click: %s" % btn_sel)
#     if not real_click(f, btn):
#         try:
#             f.use()
#             btn.click()
#         except Exception:
#             try:
#                 f.d.execute_script("arguments[0].click();", btn)
#             except Exception as e:
#                 return "Add address click FAIL: %s" % str(e)[:50]

#     for _ in range(8):
#         page.wait_for_timeout(3000)
#         try:
#             body = f.body_text() or ""
#             if "Add shipping address" not in body:
#                 return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#             if "Payment" in body and "Pincode" not in body:
#                 return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#         except Exception:
#             return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
#     return "pata bhara par form abhi bhi khada hai -- dekh lijiye"


# def confirm_email(page, acct):
#     email = acct.get("email") or ""
#     if not email:
#         return "account par email hi nahi hai"
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     for _ in range(10):
#         try:
#             body = f.body_text() or ""
#         except Exception:
#             return "checkout ka frame chala gaya"
#         if "onfirm your email" not in body:
#             return "email confirm karne ki zaroorat nahi thi"

#         btn = f.first("button:has-text('Confirm email')")
#         box = f.visible_first("input#email, input[type='email']")
#         if btn is not None and box is not None:
#             el_fill(f, box, email)
#             page.wait_for_timeout(800)
#             real_click(f, btn)
#             page.wait_for_timeout(6000)
#             try:
#                 if "onfirm your email" not in (f.body_text() or ""):
#                     return "email confirm ho gaya (%s)" % email
#             except Exception:
#                 return "email confirm ho gaya (%s)" % email
#         page.wait_for_timeout(2000)

#     try:
#         ins = f.evaluate(
#             "return [...document.querySelectorAll('input')]"
#             ".map(e => (e.id||'-')+'/'+(e.name||'-')+'/'+(e.type||'-'));") or []
#     except Exception:
#         ins = []
#     return "email confirm nahi hua | frame ke input: %s" % ", ".join(ins[:10])


# def read_checkout(page):
#     f = sr_frame_any(page)
#     if not f:
#         return None
#     try:
#         body = f.body_text() or ""
#     except Exception:
#         return None
#     out = {"address": [], "pay": [], "total": ""}

#     lines = [l.strip() for l in body.splitlines() if l.strip()]
#     for i, l in enumerate(lines):
#         if re.search(r"\b\d{6}\b", l) and len(l) > 12:
#             out["address"] = lines[max(0, i - 2):i + 3]
#             break

#     try:
#         texts = f.evaluate(
#             "return [...document.querySelectorAll("
#             "\"label, [class*='paymentMethod'], [class*='payment-method']\")]"
#             ".map(e => e.innerText || '');") or []
#         out["pay"] = [t.strip() for t in texts if 2 < len(t.strip()) < 60][:12]
#     except Exception:
#         pass

#     m = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", body)
#     if m:
#         out["total"] = m[-1]
#     return out


# # ---------- gateway / card ----------
# CARD_TARGETS = [
#     "#payment-method-button-Card label.payment-button-heading",
#     "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
#     "#payment-method-button-Card",
# ]

# GATEWAY_HINTS = ("easebuzz", "eazypay", "payment", "pay.", "3ds", "acs",
#                  "razorpay", "payu", "billdesk")


# def card_frame(page):
#     for fr in frames(page):
#         u = (fr.url or "").lower()
#         if any(k in u for k in ("easebuzz", "pay.", "payment", "3ds", "acs")):
#             try:
#                 if fr.query("input", visible=True):
#                     return fr
#             except Exception:
#                 pass
#     return None


# def card_fields(f):
#     try:
#         return f.evaluate(
#             """return [...document.querySelectorAll('input')]
#                  .filter(e => e.offsetParent !== null || e.getClientRects().length)
#                  .map(e => ({id: e.id || '', name: e.name || '',
#                              ph: e.placeholder || '',
#                              aria: e.getAttribute('aria-label') || '',
#                              maxlen: e.maxLength}))
#                  .filter(o => /card|number|cvv|cvc|expiry|month|year|holder/i
#                               .test(o.id + o.name + o.ph + o.aria)
#                            || (o.maxlen >= 3 && o.maxlen <= 19));""") or []
#     except Exception:
#         return []


# def gateway_frames(page):
#     out = set()
#     for fr in frames(page):
#         u = (fr.url or "")
#         if u and any(k in u.lower() for k in GATEWAY_HINTS):
#             out.add(u)
#     return out


# def card_state(page, f):
#     st = {"qr": False, "h": 0.0, "frames": gateway_frames(page)}
#     try:
#         st["qr"] = f.count("#src-qrcode-payment-btn") > 0
#     except Exception:
#         pass
#     try:
#         st["h"] = f.evaluate(
#             "const e = document.querySelector('#payment-method-button-Card');"
#             "return e ? e.getBoundingClientRect().height : 0;") or 0.0
#     except Exception:
#         pass
#     return st


# def card_chosen(page, f, before):
#     now = card_state(page, f)
#     if now["frames"] - before["frames"]:
#         return True
#     if before["qr"] and not now["qr"]:
#         return True
#     if now["h"] > before["h"] + 30:
#         return True
#     return bool(card_fields(f))


# def card_form_ready(page):
#     for fr in frames(page):
#         if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
#             continue
#         got = card_fields(fr)
#         if got:
#             return "form aa gaya (%s)" % ", ".join(
#                 (g["id"] or g["name"] or g["ph"] or "?") for g in got[:6])
#     return "form abhi saamne nahi aaya"


# def pick_card_type(page, kind="Credit", secs=75):
#     """Easebuzz nayi window me bhi khul sakta hai — saari windows + frames."""
#     sels = ["span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
#             "span.lang-en:text-is('%s Card')" % kind,
#             "*:text-is('%s Card')" % kind]
#     end = time.time() + secs
#     while time.time() < end:
#         scopes = []
#         for pg in pages(page.d):
#             scopes.append(pg)
#             scopes.extend(frames(pg))
#         for fr in scopes:
#             try:
#                 u = (fr.url or "").lower()
#             except Exception:
#                 u = ""
#             # gateway URL ya seedha Credit Card text
#             is_gw = any(k in u for k in GATEWAY_HINTS) if u else False
#             for sel in sels:
#                 try:
#                     el = fr.first(sel)
#                     if el is None:
#                         continue
#                     if not is_gw:
#                         # sirf tab jab text clearly Credit Card ho
#                         pass
#                 except Exception:
#                     continue
#                 how = scroll_click(fr, el)
#                 if not how:
#                     continue
#                 page.wait_for_timeout(5000)
#                 return "%s Card daba diya (%s) -- %s" % (
#                     kind, how, card_form_ready(page))
#         page.wait_for_timeout(2500)
#     return "%s Card ka option gateway ke panne par nahi mila" % kind


# def clear_blocker(page):
#     f = sr_frame_any(page)
#     if not f:
#         return ""
#     try:
#         body = (f.body_text() or "").lower()
#     except Exception:
#         return ""
#     if "active session" not in body and "page isn't available" not in body:
#         return ""
#     for sel in ("button:has-text('Continue here')",
#                 "a:has-text('Continue here')",
#                 "[role=button]:has-text('Continue here')"):
#         try:
#             el = f.first(sel)
#             if el is not None:
#                 scroll_click(f, el)
#                 page.wait_for_timeout(8000)
#                 return "purana session ka parda hata diya (Continue here)"
#         except Exception:
#             continue
#     return "CHETAVNI: purana session ka parda hai par 'Continue here' nahi mila"


# def pick_card(page):
#     f = sr_frame_any(page)
#     if not f:
#         return "checkout ka frame nahi mila"

#     el = None
#     used = ""
#     for _ in range(10):
#         for sel in CARD_TARGETS:
#             try:
#                 got = f.first(sel)
#                 if got is not None:
#                     el, used = got, sel
#                     break
#             except Exception:
#                 continue
#         if el is not None:
#             break
#         page.wait_for_timeout(2000)
#     if el is None:
#         return "Credit/Debit Card ka khaana nahi mila (shayad email confirm baaki hai)"

#     before = card_state(page, f)
#     how = None
#     for _ in range(3):
#         how = scroll_click(f, el)
#         for _ in range(6):
#             page.wait_for_timeout(1500)
#             if card_chosen(page, f, before):
#                 break
#         if card_chosen(page, f, before):
#             break
#     if not card_chosen(page, f, before):
#         return "Card daba nahi paye (%s se koshish ki, UPI hi khula raha)" % (
#             how or "kisi tareeke")

#     log("      Card chun liya (%s | %s)" % (how, used))
#     naya = card_state(page, f)["frames"] - before["frames"]
#     if naya:
#         log("      gateway ka panna khula: %s" % list(naya)[0][:90])

#     for i in range(12):
#         page.wait_for_timeout(2500)
#         cf = card_frame(page)
#         if cf:
#             return "card ke khaane khul gaye (gateway ke frame me, %ds baad)" % (
#                 (i + 1) * 2.5)
#         got = card_fields(f)
#         if got:
#             return "card ke khaane khul gaye (checkout ke frame me: %s)" % (
#                 ", ".join((g["id"] or g["name"] or g["ph"] or "?") for g in got[:6]))
#     if naya:
#         return "Card chun liya aur gateway ka panna khul gaya (agla kadam: step 10)"
#     return "Card to chun liya, par khaane abhi tak nahi aaye -- out/ ki tasveer dekhiye"


# def easebuzz_form_frame(page, secs=40):
#     """Card inputs Easebuzz window YA uske frame me — saari windows scan."""
#     sel = ('input[name="card_number"], input[placeholder="Test Holder"], '
#            'input[name="card_exp_date"], input[name="card_cvv"]')
#     end = time.time() + secs
#     while time.time() < end:
#         # har open window
#         for pg in pages(page.d):
#             try:
#                 if pg.count(sel) >= 1:
#                     return pg
#             except Exception:
#                 pass
#             for fr in frames(pg):
#                 try:
#                     if fr.count(sel) >= 1:
#                         return fr
#                 except Exception:
#                     continue
#         try:
#             if page.count('input[name="card_number"], input[name="card_cvv"]'):
#                 return page
#         except Exception:
#             pass
#         page.wait_for_timeout(1500)
#     return None


# def _fill_one(fr, page, sels, value, label):
#     for sel in sels:
#         try:
#             el = fr.first(sel)
#             if el is None:
#                 continue
#             try:
#                 if not el.is_displayed():
#                     continue
#             except Exception:
#                 pass
#             fr.use()
#             try:
#                 fr.d.execute_script(
#                     "arguments[0].scrollIntoView({block:'center'});", el)
#             except Exception:
#                 pass
#             page.wait_for_timeout(200)
#             el.click()
#             page.wait_for_timeout(150)
#             el_fill(fr, el, "")
#             el_type(fr, el, str(value), delay=50)
#             page.wait_for_timeout(250)
#             got = el_value(el)
#             log("      %s fill -> '%s'" % (label, got[:28] if got else value))
#             return True
#         except Exception as e:
#             log("      %s try fail (%s): %s" % (label, sel[:40], str(e)[:50]))
#     return False


# def fill_card_details(page, number, exp, holder, cvv, click_pay=True):
#     fr = easebuzz_form_frame(page)
#     if not fr:
#         return "FAIL: card form frame nahi mila (Credit Card choose ke baad wait karo)"

#     num_clean = re.sub(r"\s+", "", number or "")
#     num_disp = " ".join(num_clean[i:i + 4] for i in range(0, len(num_clean), 4))

#     ok_n = _fill_one(fr, page, [
#         'input[name="card_number"]',
#         'input[placeholder="Test Holder"]',
#     ], num_disp, "Card Number")

#     ok_e = _fill_one(fr, page, [
#         'input[name="card_exp_date"]',
#         'input[placeholder="Test Holder"]',
#     ], exp, "MM/YY")

#     ok_h = _fill_one(fr, page, [
#         'input[placeholder="Test Holder"]',
#         'input[name^="ebz_card_holder_name"]',
#         'input[name*="card_holder"]',
#     ], holder, "Card Holder")

#     ok_c = _fill_one(fr, page, [
#         'input[name="card_cvv"]',
#         'input[placeholder="Test Holder"]',
#     ], cvv, "CVV")

#     # human-like pause before Pay (gateway timing checks)
#     log("      Pay se pehle wait 6-8s...")
#     page.wait_for_timeout(7000)

#     pay_ok = False
#     if click_pay:
#         bank_popup = None
#         for scope in (fr, page):
#             for sel in ('button:has-text("Pay")',
#                         'button:has-text("Pay ₹")',
#                         'button:has-text("Pay Rs")'):
#                 try:
#                     el = scope.visible_first(sel)
#                     if el is None:
#                         continue
#                     log("      Pay button click")
#                     bank_popup = expect_new_page(
#                         page.d, lambda: scroll_click(scope, el), timeout=20)
#                     if bank_popup is not None:
#                         log("      Pay ne nayi window kholi: %s"
#                             % ((bank_popup.url or "")[:80]))
#                     pay_ok = True
#                     page.wait_for_timeout(5000)
#                     break
#                 except Exception:
#                     continue
#             if pay_ok:
#                 break
#         if bank_popup is not None:
#             try:
#                 bank_popup.use()
#                 end = time.time() + 60
#                 while time.time() < end:
#                     st = page.d.execute_script("return document.readyState;")
#                     if st in ("interactive", "complete"):
#                         break
#                     time.sleep(1)
#             except Exception:
#                 pass

#     return "number=%s | exp=%s | holder=%s | cvv=%s | pay=%s" % (
#         "ok" if ok_n else "FAIL",
#         "ok" if ok_e else "FAIL",
#         "ok" if ok_h else "FAIL",
#         "ok" if ok_c else "FAIL",
#         "clicked" if pay_ok else "skip",
#     )


# def wait_bank_page(driver, page, secs=120):
#     """Pay ke baad ICICI / ACS / bank page (nayi window ya same)."""
#     end = time.time() + secs
#     loading_seen = False
#     while time.time() < end:
#         for pg in pages(driver):
#             try:
#                 u = (pg.url or "").lower()
#                 body = ""
#                 try:
#                     body = (pg.body_text() or "").lower()
#                 except Exception:
#                     pass
#                 if "loading bank" in body:
#                     loading_seen = True
#                     continue
#                 if any(k in u for k in (
#                     "wibmo", "acs", "icici", "3ds", "bank", "easebuzz",
#                     "secure-acs", "mumrdc",
#                 )):
#                     if "corporate id" in body or "employee id" in body:
#                         return pg
#                     if pg.count("input#corporateId, input#employeeId"):
#                         return pg
#                     if any(k in u for k in ("wibmo", "acs", "icici")):
#                         pg.wait_for_timeout(2000)
#                         if pg.count("input#corporateId"):
#                             return pg
#                 if "corporate id" in body or pg.count("input#corporateId"):
#                     return pg
#                 # bank form kisi frame ke andar bhi ho sakta hai
#                 for fr in frames(pg):
#                     try:
#                         if fr.count("input#corporateId"):
#                             return fr
#                     except Exception:
#                         continue
#             except Exception:
#                 continue
#         page.wait_for_timeout(2000)
#     if loading_seen:
#         log("      (Loading Bank Page dekha, form nahi aaya — fingerprint/block ho sakta hai)")
#     return None


# def fill_bank_corporate(driver, page, corp_id, emp_id):
#     """ICICI ACS form: input#corporateId, input#employeeId, a.btn.primary__btn.
#     Phir OTP manual."""
#     log("      bank page ka wait...")
#     bank = wait_bank_page(driver, page, secs=120)
#     if not bank:
#         return "FAIL: bank/ACS page nahi mila (Loading Bank Page atak sakta hai)"

#     log("      bank URL: %s" % ((bank.url or "")[:100]))

#     for _ in range(20):
#         try:
#             if bank.count("input#corporateId"):
#                 break
#         except Exception:
#             pass
#         bank.wait_for_timeout(1000)
#     else:
#         return "FAIL: corporateId input nahi mila"

#     try:
#         el_fill(bank, bank.first("input#corporateId"), corp_id)
#         log("      Corporate ID -> %s" % corp_id)
#     except Exception as e:
#         return "FAIL: corporateId fill: %s" % str(e)[:60]

#     bank.wait_for_timeout(800)
#     try:
#         el_fill(bank, bank.first("input#employeeId"), emp_id)
#         log("      Employee ID -> %s" % emp_id)
#     except Exception as e:
#         return "FAIL: employeeId fill: %s" % str(e)[:60]

#     bank.wait_for_timeout(1500)

#     submitted = False
#     for sel in ('a.btn.primary__btn:has-text("Submit")',
#                 'a.btn.primary__btn:has-text("SUBMIT")',
#                 'a.primary__btn',
#                 'a.btn.primary__btn',
#                 'button:has-text("Submit")',
#                 'button:has-text("SUBMIT")'):
#         try:
#             el = bank.visible_first(sel)
#             if el is None:
#                 continue
#             log("      Submit click: %s" % sel)
#             bank.use()
#             try:
#                 el.click()
#             except Exception:
#                 bank.d.execute_script("arguments[0].click();", el)
#             submitted = True
#             bank.wait_for_timeout(4000)
#             break
#         except Exception:
#             continue

#     if not submitted:
#         try:
#             bank.evaluate("if (typeof submit === 'function') submit();")
#             submitted = True
#             log("      Submit via JS submit()")
#             bank.wait_for_timeout(4000)
#         except Exception:
#             pass

#     if not submitted:
#         return "corp/emp filled par Submit nahi hua"

#     return "Corporate+Employee filled, Submit OK — ab OTP manual"


# def wait_for_order(driver, page, acct, minutes=12):
#     marks = ("thank you", "order placed", "order confirmed", "order id",
#              "your order", "order number")
#     end = time.time() + minutes * 60
#     log("      order ka intezaar (%d minute tak)..." % minutes)
#     while time.time() < end:
#         page.wait_for_timeout(5000)
#         url = ""
#         txt = ""
#         hit = None
#         for pg in pages(driver):
#             try:
#                 u = pg.url or ""
#                 t = pg.body_text() or ""
#             except Exception:
#                 continue
#             if any(m in t.lower() for m in marks) or "/thank" in u or "/orders/" in u:
#                 url, txt, hit = u, t, pg
#                 break
#         if not txt:
#             continue

#         ref = ""
#         m = re.search(r"(?:order\s*(?:id|no\.?|number)\s*[:#]?\s*)([A-Za-z0-9#\-]{4,})",
#                       txt, re.I)
#         if m:
#             ref = m.group(1).strip("#")
#         if not ref:
#             m = re.search(r"#(\d{4,})", txt)
#             ref = m.group(1) if m else ""

#         try:
#             hit.screenshot(os.path.join(OUT, "order_5_confirmed.png"))
#         except Exception:
#             pass

#         row = [time.strftime("%Y-%m-%d %H:%M:%S"), acct.get("phone", ""),
#                acct.get("email", ""), ref or "(number nahi mila)", url[:120]]
#         new_file = not os.path.exists(os.path.join(HERE, "orders.csv"))
#         with open(os.path.join(HERE, "orders.csv"), "a", newline="",
#                   encoding="utf-8") as fh:
#             w = csv.writer(fh)
#             if new_file:
#                 w.writerow(["when", "phone", "email", "order_ref", "url"])
#             w.writerow(row)
#         return "ORDER LAG GAYA -- %s  (orders.csv me likh diya)" % (
#             ref or "number nahi mila")

#     return "itne me order confirm hota nahi dikha (chhod diya, kuch bigda nahi)"


# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--product", required=True)
#     ap.add_argument("--pack", default="")
#     ap.add_argument("--unit", default="")
#     ap.add_argument("--session", default="")
#     ap.add_argument("--show", action="store_true")
#     ap.add_argument("--headless", action="store_true",
#                     help="Waterfox bina window ke (bank page ke liye theek nahi)")
#     ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
#     ap.add_argument("--card", default=DEFAULT_CARD)
#     ap.add_argument("--exp", default=DEFAULT_EXP)
#     ap.add_argument("--holder", default=DEFAULT_HOLDER)
#     ap.add_argument("--cvv", default=DEFAULT_CVV)
#     ap.add_argument("--no-pay-click", action="store_true")
#     ap.add_argument("--auto-pay", action="store_true",
#                     help="Pay khud dabao (bank page fail ho sakti hai)")
#     ap.add_argument("--manual-pay", action="store_true", default=True,
#                     help="Pay tum dabao (default, bank page ke liye better)")
#     ap.add_argument("--corp-id", default=DEFAULT_CORP_ID)
#     ap.add_argument("--emp-id", default=DEFAULT_EMP_ID)
#     ap.add_argument("--watch", type=int, default=0)
#     ap.add_argument("--hold", type=int, default=60)
#     ap.add_argument("--proxy", action="store_true", default=True,
#                     help="Geonode India residential (default ON)")
#     ap.add_argument("--no-proxy", action="store_true",
#                     help="proxy band")
#     ap.add_argument("--proxy-country", default=GEONODE_COUNTRY)
#     a = ap.parse_args()

#     path = a.session or newest_session()
#     if not path:
#         log("koi session nahi mili -- pehle make_accounts.py chalao")
#         return 1
#     if not os.path.isabs(path):
#         p2 = os.path.join(SESSIONS, path)
#         path = p2 if os.path.exists(p2) else path
#     d = json.load(open(path, encoding="utf-8"))
#     log("account : %s / %s" % (d.get("phone"), d.get("email")))
#     if not d.get("address"):
#         log("CHETAVNI: is account par pata darj nahi hai -- pehle add_address.py chalao")

#     use_proxy = not a.no_proxy
#     stop_bridge = None
#     bridge_port = None
#     if use_proxy:
#         proxy_user = geonode_username(a.proxy_country, sticky=False)
#         log("proxy : Geonode country=%s | user=%s" % (a.proxy_country, proxy_user))
#         try:
#             bridge_port, stop_bridge = start_geonode_bridge(proxy_user)
#             log("proxy : local bridge 127.0.0.1:%d" % bridge_port)
#         except Exception as e:
#             log("proxy FAIL (%s) -- bina proxy chalega" % e)
#             use_proxy = False
#             bridge_port = None

#     driver = None
#     try:
#         try:
#             driver = launch_waterfox(proxy_port=bridge_port, headless=a.headless)
#             log("browser: WATERFOX (geckodriver) -- Chrome/CDP nahi")
#         except Exception as e:
#             log("FAIL: Waterfox nahi khuli: %s" % e)
#             log("  1) D:\\streakads\\Waterfox\\waterfox.exe hona chahiye")
#             log("  2) ya set: WATERFOX_PATH / GECKODRIVER_PATH")
#             if stop_bridge is not None:
#                 stop_bridge.set()
#             return 2

#         log("   session (cookies + localStorage) daal rahe hain...")
#         try:
#             load_session(driver, d)
#         except Exception as e:
#             log("   session load me dikkat: %s" % str(e)[:120])

#         page = Scope(driver, driver.current_window_handle)

#         log("\n1) product khol rahe hain: %s" % a.product)
#         product_url = "%s/products/%s" % (SHOP, a.product)
#         nav_ok = False
#         last_err = None
#         for attempt in range(1, 4):
#             try:
#                 page.goto(pehla_url, timeout=120)
#                 nav_ok = True
#                 break
#             except Exception as e:
#                 last_err = e
#                 log("   goto fail try %d/3: %s" % (attempt, str(e)[:120]))
#                 page.wait_for_timeout(2000)

#         if not nav_ok and use_proxy:
#             # proxy se nahi chala -> bina proxy retry (Waterfox ko naye sire se
#             # kholna padta hai, proxy pref launch ke waqt tay hoti hai)
#             log("   proxy se site nahi khuli -- bina proxy retry...")
#             try:
#                 driver.quit()
#             except Exception:
#                 pass
#             if stop_bridge is not None:
#                 stop_bridge.set()
#                 stop_bridge = None
#             use_proxy = False
#             try:
#                 driver = launch_waterfox(proxy_port=None, headless=a.headless)
#                 load_session(driver, d)
#                 page = Scope(driver, driver.current_window_handle)
#                 page.goto(pehla_url, timeout=120)
#                 nav_ok = True
#                 log("   bina proxy OK (bank page baad me fail ho sakti hai)")
#             except Exception as e:
#                 last_err = e

#         if not nav_ok:
#             log("FAIL: product page nahi khuli: %s" % last_err)
#             try:
#                 driver.quit()
#             except Exception:
#                 pass
#             if stop_bridge is not None:
#                 stop_bridge.set()
#             return 2

#         page.wait_for_timeout(5000)
#         for _ in range(3):
#             page.evaluate("window.scrollBy(0, 900);")
#             page.wait_for_timeout(700)

#         title = (page.title() or "").split("|")[0].strip()
#         log("   %s" % title)
#         before = variant_id(page)
#         log("   abhi ka variant: %s" % before)

#         if a.unit:
#             log("2) unit chun rahe hain: %s" % a.unit)
#             if not pick(page, a.unit):
#                 log("   (ye unit is panne par nahi mila -- aage badh rahe hain)")
#         if a.pack:
#             log("3) pack chun rahe hain: %s" % a.pack)
#             if not pick(page, a.pack):
#                 log("   FAIL: ye pack is panne par nahi mila")
#                 page.screenshot(os.path.join(OUT, "order_fail_pack.png"),
#                                 full_page=True)
#                 driver.quit()
#                 return 3

#         after = variant_id(page)
#         log("   chunne ke baad variant: %s%s"
#             % (after, "  (badal gaya)" if after != before else "  (wahi hai)"))
#         page.screenshot(os.path.join(OUT, "order_1_product.png"))

#         log("4) add to cart")
#         sel = find(page, ADD_TO_CART)
#         if not sel:
#             log("   FAIL: 'Add to cart' ka button nahi mila")
#             driver.quit()
#             return 4
#         el = page.first(sel)
#         if not scroll_click(page, el):
#             log("   FAIL: 'Add to cart' daba nahi paye")
#             driver.quit()
#             return 4
#         page.wait_for_timeout(6000)
#         page.screenshot(os.path.join(OUT, "order_2_added.png"))

#         cart = page.evaluate_async(
#             "const cb = arguments[arguments.length - 1];"
#             "fetch('/cart.js').then(r => r.json()).then(j => cb(j))"
#             ".catch(e => cb(null));") or {}
#         log("   cart me cheezein: %d | kul Rs %s"
#             % (cart.get("item_count", 0), (cart.get("total_price", 0) or 0) / 100))
#         for it in cart.get("items", []):
#             log("      %s | %s | Rs %s"
#                 % (it.get("product_title"), it.get("variant_title"),
#                    (it.get("line_price", 0) or 0) / 100))
#         if not cart.get("item_count"):
#             log("   FAIL: cart khaali hi rah gaya")
#             driver.quit()
#             return 5
#         if after and str(cart["items"][0].get("variant_id")) != str(after):
#             log("   CHETAVNI: cart me doosra variant gaya hai (%s) -- dekh lijiye"
#                 % cart["items"][0].get("variant_id"))

#         log("5) cart")
#         if find(page, CHECKOUT):
#             log("      cart to khud hi khul gaya")
#         else:
#             sel = find(page, CART_OPEN)
#             if sel:
#                 log("      cart khol rahe hain")
#                 scroll_click(page, page.first(sel))
#                 page.wait_for_timeout(5000)
#             else:
#                 log("      /cart panne par ja rahe hain")
#                 page.goto("%s/cart" % SHOP, timeout=60)
#                 page.wait_for_timeout(5000)
#         page.screenshot(os.path.join(OUT, "order_3_cart.png"))

#         log("6) Checkout daba rahe hain")
#         sel = find(page, CHECKOUT)
#         if not sel:
#             log("   FAIL: Checkout ka button nahi mila")
#             page.screenshot(os.path.join(OUT, "order_fail_checkout.png"),
#                             full_page=True)
#             driver.quit()
#             return 6

#         btn = page.first(sel)
#         newpage = expect_new_page(driver, lambda: scroll_click(page, btn), timeout=15)
#         pay = newpage or page
#         pay.use()
#         pay.wait_for_timeout(12000)

#         blk = clear_blocker(pay)
#         if blk:
#             log("   %s" % blk)

#         # Step 7 se 12 tak ka saara kaam Fastrr ke iframe par tika hai. Wo frame
#         # na mile to sab "frame nahi mila" bol kar chup-chaap nikal jaate the aur
#         # aisa lagta tha ki script ne checkout ke baad kuch kiya hi nahi. Ab wajah
#         # saamne likhi jaati hai.
#         # Fastrr iframe dheere load hota hai — wait + re-scan
#         fr_list = []
#         for _wait in range(20):
#             fr_list = frames(pay)
#             if any("fastrr-boost-ui.pickrr.com" in (f.url or "")
#                    or "pickrr" in (f.url or "")
#                    or "shiprocket" in (f.url or "") for f in fr_list):
#                 break
#             pay.wait_for_timeout(1500)
#         log("   checkout ka panna: %s" % (pay.url or "")[:100])
#         log("   frames (%d): %s" % (
#             len(fr_list),
#             ", ".join((f.url or "?")[:60] for f in fr_list[:5]) or "koi nahi"))
#         if not any("fastrr" in (f.url or "") or "pickrr" in (f.url or "")
#                    for f in fr_list):
#             log("   CHETAVNI: Fastrr checkout ka frame nahi dikha --"
#                 " step 7 se 12 tak kuch nahi kar payenge")
#             try:
#                 pay.screenshot(os.path.join(OUT, "order_fail_checkout_frame.png"),
#                                full_page=True)
#                 log("   tasveer: out/order_fail_checkout_frame.png")
#             except Exception:
#                 pass

#         log("7) checkout ka apna pata")
#         ship = ship_address(pay, d)
#         log("      %s" % ship)
#         pay.wait_for_timeout(6000)

#         log("8) email confirm")
#         log("      %s" % confirm_email(pay, d))
#         pay.wait_for_timeout(4000)

#         st = read_checkout(pay)
#         if st:
#             log("   checkout par abhi:")
#             if st["address"]:
#                 for l in st["address"]:
#                     log("      pata: %s" % l[:90])
#             else:
#                 log("      pata: panne par koi pincode nahi dikha")
#             if st["pay"]:
#                 log("      payment ke tareeke: %s" % ", ".join(st["pay"])[:200])
#             if st["total"]:
#                 log("      panne ka aakhri daam: Rs %s" % st["total"])
#         else:
#             log("   (checkout ka frame nahi mila -- neeche ki tasveer dekhiye)")

#         log("9) Credit/Debit Card chun rahe hain")
#         log("      %s" % pick_card(pay))
#         pay.wait_for_timeout(5000)

#         log("10) gateway par %s Card chun rahe hain" % a.card_type)
#         log("      %s" % pick_card_type(pay, a.card_type))
#         pay.wait_for_timeout(3000)

#         auto_pay = bool(a.auto_pay) and not a.no_pay_click
#         log("11) Card details fill (Pay auto=%s)" % auto_pay)
#         log("      %s" % fill_card_details(
#             pay, a.card, a.exp, a.holder, a.cvv,
#             click_pay=auto_pay,
#         ))

#         if not auto_pay:
#             log("\n==========================================================")
#             log("   CARD FILL HO GAYA. Ab aap MANUALLY:")
#             log("   1) Pay button dabao")
#             log("   2) Bank page load hone do (Loading Bank Page...)")
#             log("   3) Corporate ID / Employee ID bharo (ya wait for script)")
#             log("   Jab Corporate/Employee form dikhe -> yahan Enter dabao")
#             log("==========================================================")
#             try:
#                 input("👉 Bank form dikhne ke baad Enter: ")
#             except Exception:
#                 pay.wait_for_timeout(120000)
#         else:
#             pay.wait_for_timeout(8000)

#         log("12) Bank Corporate / Employee ID")
#         log("      %s" % fill_bank_corporate(driver, pay, a.corp_id, a.emp_id))
#         pay.wait_for_timeout(2000)

#         log("\n==========================================================")
#         log("   Bank OTP page aayi ho to OTP khud bharo.")
#         log("   OTP ke baad Enter dabao (agar --hold 0).")
#         log("==========================================================")

#         log("\n   URL: %s" % pay.url)
#         try:
#             txt = pay.body_text() or ""
#         except Exception:
#             txt = ""
#         lines = [l.strip() for l in txt.splitlines() if l.strip()][:16]
#         log("   panne par: %s" % " | ".join(lines)[:260])
#         rup = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", txt)
#         log("   panne par daam: %s" % (sorted(set(rup))[:8] or "koi nahi"))
#         try:
#             pay.screenshot(os.path.join(OUT, "order_4_payment.png"))
#             log("   tasveer: out/order_4_payment.png")
#         except Exception as e:
#             log("   (tasveer nahi bani: %s)" % str(e)[:60])

#         log("\n==========================================================")
#         log("   CARD + CORP/EMP FILL HO GAYA. Bank OTP aap khud bhariye.")
#         log("==========================================================")
#         if a.watch:
#             log("   OTP ke baad script order ka wait karegi.")
#             log("      %s" % wait_for_order(driver, pay, d, a.watch))
#         if a.hold == 0:
#             log("   Browser khula rahega. Kaam khatam ho to yahan Enter dabaiye.")
#             try:
#                 input()
#             except Exception:
#                 pay.wait_for_timeout(600000)
#         else:
#             log("   (%ds baad band)" % a.hold)
#             pay.wait_for_timeout(a.hold * 1000)
#     finally:
#         if driver is not None:
#             try:
#                 driver.quit()
#             except Exception:
#                 pass
#         if stop_bridge is not None:
#             stop_bridge.set()
#     return 0


# if __name__ == "__main__":
#     sys.exit(main())