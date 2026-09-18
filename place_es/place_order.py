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






#!/usr/bin/env python3
"""place_order.py -- product -> cart -> checkout -> Credit Card -> fill details.

Card fill auto; bank OTP manual.
"""
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
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
SESSIONS = os.path.join(HERE, "sessions")
OUT = os.path.join(HERE, "out")
SHOP = "https://estuaryworld.com"
os.makedirs(OUT, exist_ok=True)

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
# ================= GEONODE =================
GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
GEONODE_PASS = "CHANGE_ME_SECRET"
GEONODE_HOST = "proxy.geonode.io"
GEONODE_PORT = "12000"          # Sticky port (11000 = Rotating, sticky user reject karta hai)
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


def geonode_username(country=None, sticky=True):
    """Geonode residential user string.
    sticky=False: rotating IP (no session)
    sticky=True: session-id for same IP awhile
    """
    c = (country or GEONODE_COUNTRY).lower()
    base = GEONODE_USER_BASE.format(c)
    if sticky:
        sess = uuid.uuid4().hex[:10]
        return "%s-session-%s-lifetime-30" % (base, sess)
    return base



def find_chrome_exe():
    """Windows / common Chrome paths."""
    candidates = [
        os.environ.get("CHROME_PATH") or "",
        shutil.which("chrome") or "",
        shutil.which("google-chrome") or "",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def wait_port(port, timeout=25):
    end = time.time() + timeout
    while time.time() < end:
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=1)
            s.close()
            return True
        except Exception:
            time.sleep(0.3)
    return False


def launch_real_chrome_cdp(port=None, profile_dir=None):
    """
    Real Google Chrome + remote debugging.
    Playwright connect_over_cdp se judta hai — popup bhi REAL Chrome hota hai,
    'Chrome for Testing' nahi.
    Returns (chrome_proc, port, profile_dir)
    """
    exe = find_chrome_exe()
    if not exe:
        raise RuntimeError(
            "Google Chrome nahi mila. Install karo ya CHROME_PATH set karo."
        )
    if port is None:
        port = _free_port()
    if profile_dir is None:
        profile_dir = tempfile.mkdtemp(prefix="estuary_chrome_")
    args = [
        exe,
        "--remote-debugging-port=%d" % port,
        "--user-data-dir=%s" % profile_dir,
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--start-maximized",
        "about:blank",
    ]
    log("real Chrome: %s" % exe)
    log("CDP port: %d | profile: %s" % (port, profile_dir))
    proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not wait_port(port, timeout=30):
        try:
            proc.terminate()
        except Exception:
            pass
        raise RuntimeError("Chrome debugging port %d open nahi hua" % port)
    return proc, port, profile_dir



def newest_session():
    fs = sorted(glob.glob(os.path.join(SESSIONS, "*.json")), key=os.path.getmtime)
    return fs[-1] if fs else None


def find(scope, sels):
    for s in sels:
        try:
            if scope.locator(s).count() and scope.locator(s).first.is_visible():
                return s
        except Exception:
            continue
    return None


def variant_id(page):
    return page.evaluate(
        """() => { const f = document.querySelector('form[action*="/cart/add"]');
                   const i = f && f.querySelector('input[name="id"], select[name="id"]');
                   return i ? String(i.value) : null; }""")


def pick(page, value):
    res = page.evaluate(
        """(v) => {
             const rs = [...document.querySelectorAll('input[type=radio]')]
                        .filter(x => (x.value || '').trim() === v);
             if (!rs.length) return 'nahi-mila';
             const r = rs[0];
             if (r.checked) return 'pehle-se-chuna';
             r.click();
             return 'daba-diya';
           }""", value)
    log("      %s" % res)
    if res == "nahi-mila":
        return False
    page.wait_for_timeout(2500)
    return True


def sr_frame(page):
    for fr in page.frames:
        if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
            try:
                if fr.locator("#pincode").count():
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

    f.locator("#pincode").fill(pin)
    page.wait_for_timeout(4000)
    f.locator("#name").fill(first)
    f.locator("#lastName").fill(last)
    f.locator("#line1").fill(line1)
    f.locator("#line2").fill(line2)
    for sel, val in (("#city", city), ("#state", state)):
        try:
            if not (f.locator(sel).input_value() or "").strip():
                f.locator(sel).fill(val)
        except Exception:
            pass
    if email:
        try:
            f.locator("#email").fill(email)
        except Exception:
            pass

    try:
        f.locator("input[name='home']").first.check()
    except Exception:
        pass

    got = f.locator("#addAddressBtn")
    if not got.count():
        return "'Add address' ka button nahi mila"

    box = got.first.bounding_box()
    if box:
        page.mouse.move(box["x"] + box["width"] / 2,
                        box["y"] + box["height"] / 2, steps=12)
        page.wait_for_timeout(400)
        page.mouse.down()
        page.wait_for_timeout(90)
        page.mouse.up()
    else:
        got.first.click()

    for _ in range(6):
        page.wait_for_timeout(4000)
        try:
            if "Add shipping address" not in (f.locator("body").inner_text() or ""):
                return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
        except Exception:
            return "pata lag gaya (%s, %s - %s)" % (city, state, pin)
    return "pata bhara par form abhi bhi khada hai -- dekh lijiye"


def real_click(page, loc):
    box = loc.bounding_box()
    if not box:
        loc.click()
        return
    page.mouse.move(box["x"] + box["width"] / 2,
                    box["y"] + box["height"] / 2, steps=12)
    page.wait_for_timeout(400)
    page.mouse.down()
    page.wait_for_timeout(90)
    page.mouse.up()


def confirm_email(page, acct):
    email = acct.get("email") or ""
    if not email:
        return "account par email hi nahi hai"
    f = sr_frame_any(page)
    if not f:
        return "checkout ka frame nahi mila"

    for _ in range(10):
        try:
            body = f.locator("body").inner_text() or ""
        except Exception:
            return "checkout ka frame chala gaya"
        if "onfirm your email" not in body:
            return "email confirm karne ki zaroorat nahi thi"

        btn = f.locator("button:has-text('Confirm email')")
        box = f.locator("input#email:visible, input[type='email']:visible")
        if btn.count() and box.count():
            box.first.fill(email)
            page.wait_for_timeout(800)
            real_click(page, btn.first)
            page.wait_for_timeout(6000)
            try:
                if "onfirm your email" not in (f.locator("body").inner_text() or ""):
                    return "email confirm ho gaya (%s)" % email
            except Exception:
                return "email confirm ho gaya (%s)" % email
        page.wait_for_timeout(2000)

    try:
        ins = f.locator("input").evaluate_all(
            "els => els.map(e => (e.id||'-')+'/'+(e.name||'-')+'/'+(e.type||'-'))")
    except Exception:
        ins = []
    return "email confirm nahi hua | frame ke input: %s" % ", ".join(ins[:10])


def sr_frame_any(page):
    for fr in page.frames:
        if "fastrr-boost-ui.pickrr.com" in (fr.url or ""):
            try:
                if (fr.locator("body").inner_text() or "").strip():
                    return fr
            except Exception:
                pass
    return None


def read_checkout(page):
    f = sr_frame_any(page)
    if not f:
        return None
    try:
        body = f.locator("body").inner_text() or ""
    except Exception:
        return None
    out = {"address": [], "pay": [], "total": ""}

    lines = [l.strip() for l in body.splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if re.search(r"\b\d{6}\b", l) and len(l) > 12:
            out["address"] = lines[max(0, i - 2):i + 3]
            break

    try:
        out["pay"] = [t.strip() for t in f.locator(
            "label, [class*='paymentMethod'], [class*='payment-method']"
        ).all_inner_texts() if 2 < len(t.strip()) < 60][:12]
    except Exception:
        pass

    m = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", body)
    if m:
        out["total"] = m[-1]
    return out


def card_frame(page):
    for fr in page.frames:
        u = (fr.url or "").lower()
        if any(k in u for k in ("easebuzz", "pay.", "payment", "3ds", "acs")):
            try:
                if fr.locator("input:visible").count():
                    return fr
            except Exception:
                pass
    return None


def card_fields(f):
    try:
        return f.locator("input:visible").evaluate_all(
            """els => els.map(e => ({id: e.id || '', name: e.name || '',
                                     ph: e.placeholder || '',
                                     aria: e.getAttribute('aria-label') || '',
                                     maxlen: e.maxLength}))
                        .filter(o => /card|number|cvv|cvc|expiry|month|year|holder/i
                                     .test(o.id + o.name + o.ph + o.aria)
                                  || (o.maxlen >= 3 && o.maxlen <= 19))""")
    except Exception:
        return []


def in_view(page, box):
    vp = page.viewport_size or {"width": 1500, "height": 950}
    return bool(box) and box["y"] > 0 and box["x"] > 0 \
        and box["y"] + box["height"] < vp["height"] \
        and box["x"] + box["width"] < vp["width"]


def scroll_click(page, loc, tries=3):
    for _ in range(tries):
        try:
            loc.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass
        page.wait_for_timeout(600)
        box = loc.bounding_box()
        if in_view(page, box):
            page.mouse.move(box["x"] + box["width"] / 2,
                            box["y"] + box["height"] / 2, steps=12)
            page.wait_for_timeout(300)
            page.mouse.down()
            page.wait_for_timeout(90)
            page.mouse.up()
            return "mouse"
    try:
        loc.click(timeout=5000)
        return "click()"
    except Exception:
        pass
    try:
        loc.evaluate("e => e.click()")
        return "dom-click"
    except Exception:
        return None


CARD_TARGETS = [
    "#payment-method-button-Card label.payment-button-heading",
    "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
    "#payment-method-button-Card",
]

GATEWAY_HINTS = ("easebuzz", "eazypay", "payment", "pay.", "3ds", "acs",
                 "razorpay", "payu", "billdesk")


def gateway_frames(page):
    out = set()
    for fr in page.frames:
        u = (fr.url or "")
        if u and any(k in u.lower() for k in GATEWAY_HINTS):
            out.add(u)
    return out


def card_state(page, f):
    st = {"qr": False, "h": 0.0, "frames": gateway_frames(page)}
    try:
        st["qr"] = f.locator("#src-qrcode-payment-btn").count() > 0
    except Exception:
        pass
    try:
        st["h"] = f.locator("#payment-method-button-Card").first.evaluate(
            "e => e.getBoundingClientRect().height") or 0.0
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


def pick_card_type(page, kind="Credit", secs=75):
    sels = ["span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
            "span.lang-en:text-is('%s Card')" % kind,
            "*:text-is('%s Card')" % kind]
    end = time.time() + secs
    while time.time() < end:
        for fr in page.frames:
            if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
                continue
            for sel in sels:
                try:
                    l = fr.locator(sel)
                    if not l.count():
                        continue
                except Exception:
                    continue
                how = scroll_click(page, l.first)
                if not how:
                    continue
                page.wait_for_timeout(5000)
                return "%s Card daba diya (%s) -- %s" % (
                    kind, how, card_form_ready(page))
        page.wait_for_timeout(2500)
    return "%s Card ka option gateway ke panne par nahi mila" % kind


def card_form_ready(page):
    for fr in page.frames:
        if not any(k in (fr.url or "").lower() for k in GATEWAY_HINTS):
            continue
        got = card_fields(fr)
        if got:
            return "form aa gaya (%s)" % ", ".join(
                (g["id"] or g["name"] or g["ph"] or "?") for g in got[:6])
    return "form abhi saamne nahi aaya"


def clear_blocker(page):
    f = sr_frame_any(page)
    if not f:
        return ""
    try:
        body = (f.locator("body").inner_text() or "").lower()
    except Exception:
        return ""
    if "active session" not in body and "page isn't available" not in body:
        return ""
    for sel in ("button:has-text('Continue here')",
                "a:has-text('Continue here')",
                "[role=button]:has-text('Continue here')"):
        try:
            l = f.locator(sel)
            if l.count():
                scroll_click(page, l.first)
                page.wait_for_timeout(8000)
                return "purana session ka parda hata diya (Continue here)"
        except Exception:
            continue
    return "CHETAVNI: purana session ka parda hai par 'Continue here' nahi mila"


def pick_card(page):
    f = sr_frame_any(page)
    if not f:
        return "checkout ka frame nahi mila"

    loc = None
    used = ""
    for _ in range(10):
        for sel in CARD_TARGETS:
            try:
                l = f.locator(sel)
                if l.count():
                    loc, used = l.first, sel
                    break
            except Exception:
                continue
        if loc:
            break
        page.wait_for_timeout(2000)
    if not loc:
        return "Credit/Debit Card ka khaana nahi mila (shayad email confirm baaki hai)"

    before = card_state(page, f)
    how = None
    for _ in range(3):
        how = scroll_click(page, loc)
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
            return "card ke khaane khul gaye (gateway ke frame me, %ds baad)" % ((i + 1) * 2.5)
        got = card_fields(f)
        if got:
            return "card ke khaane khul gaye (checkout ke frame me: %s)" % (
                ", ".join((g["id"] or g["name"] or g["ph"] or "?") for g in got[:6]))
    if naya:
        return "Card chun liya aur gateway ka panna khul gaya (agla kadam: step 10)"
    return "Card to chun liya, par khaane abhi tak nahi aaye -- out/ ki tasveer dekhiye"


def easebuzz_form_frame(page, secs=40):
    end = time.time() + secs
    while time.time() < end:
        for fr in page.frames:
            try:
                n = fr.locator(
                    'input[name="card_number"], '
                    'input[placeholder="Test Holder"], '
                    'input[name="card_exp_date"], '
                    'input[name="card_cvv"]'
                ).count()
                if n >= 1:
                    return fr
            except Exception:
                continue
        try:
            if page.locator('input[name="card_number"], input[name="card_cvv"]').count():
                return page
        except Exception:
            pass
        page.wait_for_timeout(1500)
    return None


def _fill_one(fr, page, sels, value, label):
    for sel in sels:
        try:
            loc = fr.locator(sel)
            if not loc.count():
                continue
            el = loc.first
            try:
                if not el.is_visible():
                    continue
            except Exception:
                pass
            el.scroll_into_view_if_needed(timeout=5000)
            page.wait_for_timeout(200)
            el.click(timeout=5000)
            page.wait_for_timeout(150)
            el.fill("")
            el.type(str(value), delay=50)
            page.wait_for_timeout(250)
            got = ""
            try:
                got = el.input_value() or ""
            except Exception:
                pass
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
        'input[name*="card_holder" i]',
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
        # catch popup/new window opened by Pay
        bank_popup = None
        for scope in (fr, page):
            for sel in (
                'button:has-text("Pay")',
                'button:has-text("Pay ₹")',
                'button:has-text("Pay Rs")',
            ):
                try:
                    loc = scope.locator(sel)
                    if not (loc.count() and loc.first.is_visible()):
                        continue
                    log("      Pay button click")
                    try:
                        with page.context.expect_page(timeout=20000) as pit:
                            scroll_click(page, loc.first)
                        bank_popup = pit.value
                        log("      Pay ne nayi window kholi: %s" % ((bank_popup.url or "")[:80]))
                    except Exception:
                        scroll_click(page, loc.first)
                    pay_ok = True
                    page.wait_for_timeout(5000)
                    break
                except Exception:
                    continue
            if pay_ok:
                break
        if bank_popup is not None:
            try:
                bank_popup.wait_for_load_state("domcontentloaded", timeout=60000)
            except Exception:
                pass

    return "number=%s | exp=%s | holder=%s | cvv=%s | pay=%s" % (
        "ok" if ok_n else "FAIL",
        "ok" if ok_e else "FAIL",
        "ok" if ok_h else "FAIL",
        "ok" if ok_c else "FAIL",
        "clicked" if pay_ok else "skip",
    )



def wait_bank_page(context, page, secs=120):
    """Pay ke baad ICICI / ACS / bank page (nayi window ya same)."""
    end = time.time() + secs
    loading_seen = False
    while time.time() < end:
        for pg in list(context.pages):
            try:
                u = (pg.url or "").lower()
                body = ""
                try:
                    body = (pg.inner_text("body") or "").lower()
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
                    if pg.locator("input#corporateId, input#employeeId").count():
                        return pg
                    # ACS URL but form not ready yet
                    if any(k in u for k in ("wibmo", "acs", "icici")):
                        try:
                            pg.wait_for_timeout(2000)
                        except Exception:
                            pass
                        if pg.locator("input#corporateId").count():
                            return pg
                if "corporate id" in body or pg.locator("input#corporateId").count():
                    return pg
            except Exception:
                continue
        page.wait_for_timeout(2000)
    if loading_seen:
        log("      (Loading Bank Page dekha, form nahi aaya — fingerprint/block ho sakta hai)")
    return None


def fill_bank_corporate(context, page, corp_id, emp_id):
    """
    ICICI ACS form:
      input#corporateId
      input#employeeId
      a.btn.primary__btn Submit
    Phir OTP manual.
    """
    log("      bank page ka wait...")
    bank = wait_bank_page(context, page, secs=120)
    if not bank:
        return "FAIL: bank/ACS page nahi mila (Loading Bank Page atak sakta hai)"

    log("      bank URL: %s" % ((bank.url or "")[:100]))

    # form load
    for _ in range(20):
        try:
            if bank.locator("input#corporateId").count():
                break
        except Exception:
            pass
        bank.wait_for_timeout(1000)
    else:
        return "FAIL: corporateId input nahi mila"

    try:
        bank.locator("input#corporateId").fill(corp_id)
        log("      Corporate ID -> %s" % corp_id)
    except Exception as e:
        return "FAIL: corporateId fill: %s" % str(e)[:60]

    bank.wait_for_timeout(800)
    try:
        bank.locator("input#employeeId").fill(emp_id)
        log("      Employee ID -> %s" % emp_id)
    except Exception as e:
        return "FAIL: employeeId fill: %s" % str(e)[:60]

    bank.wait_for_timeout(1500)

    # Submit
    submitted = False
    for sel in (
        'a.btn.primary__btn:has-text("Submit")',
        'a.btn.primary__btn:has-text("SUBMIT")',
        'a.primary__btn',
        'a.btn.primary__btn',
        'button:has-text("Submit")',
        'button:has-text("SUBMIT")',
    ):
        try:
            loc = bank.locator(sel)
            if loc.count() and loc.first.is_visible():
                log("      Submit click: %s" % sel)
                try:
                    loc.first.click()
                except Exception:
                    loc.first.evaluate("e => e.click()")
                submitted = True
                bank.wait_for_timeout(4000)
                break
        except Exception:
            continue

    if not submitted:
        # onclick=submit()
        try:
            bank.evaluate("() => { if (typeof submit === 'function') submit(); }")
            submitted = True
            log("      Submit via JS submit()")
            bank.wait_for_timeout(4000)
        except Exception:
            pass

    if not submitted:
        return "corp/emp filled par Submit nahi hua"

    return "Corporate+Employee filled, Submit OK — ab OTP manual"


def wait_for_order(page, acct, minutes=12):

    marks = ("thank you", "order placed", "order confirmed", "order id",
             "your order", "order number")
    end = time.time() + minutes * 60
    log("      order ka intezaar (%d minute tak)..." % minutes)
    while time.time() < end:
        page.wait_for_timeout(5000)
        url = ""
        txt = ""
        for pg in list(page.context.pages):
            try:
                u = pg.url or ""
                t = (pg.inner_text("body") or "")
            except Exception:
                continue
            if any(m in t.lower() for m in marks) or "/thank" in u or "/orders/" in u:
                url, txt, page = u, t, pg
                break
        if not txt:
            continue

        ref = ""
        m = re.search(r"(?:order\s*(?:id|no\.?|number)\s*[:#]?\s*)([A-Za-z0-9#\-]{4,})",
                      txt, re.I)
        if m:
            ref = m.group(1).strip("#")
        if not ref:
            m = re.search(r"#(\d{4,})", txt)
            ref = m.group(1) if m else ""

        try:
            page.screenshot(path=os.path.join(OUT, "order_5_confirmed.png"))
        except Exception:
            pass

        row = [time.strftime("%Y-%m-%d %H:%M:%S"), acct.get("phone", ""),
               acct.get("email", ""), ref or "(number nahi mila)", url[:120]]
        new_file = not os.path.exists(os.path.join(HERE, "orders.csv"))
        with open(os.path.join(HERE, "orders.csv"), "a", newline="",
                  encoding="utf-8") as fh:
            w = csv.writer(fh)
            if new_file:
                w.writerow(["when", "phone", "email", "order_ref", "url"])
            w.writerow(row)
        return "ORDER LAG GAYA -- %s  (orders.csv me likh diya)" % (ref or "number nahi mila")

    return "itne me order confirm hota nahi dikha (chhod diya, kuch bigda nahi)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", required=True)
    ap.add_argument("--pack", default="")
    ap.add_argument("--unit", default="")
    ap.add_argument("--session", default="")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
    ap.add_argument("--card", default=DEFAULT_CARD)
    ap.add_argument("--exp", default=DEFAULT_EXP)
    ap.add_argument("--holder", default=DEFAULT_HOLDER)
    ap.add_argument("--cvv", default=DEFAULT_CVV)
    ap.add_argument("--no-pay-click", action="store_true")
    ap.add_argument("--auto-pay", action="store_true",
                    help="Pay khud dabao (bank page fail ho sakti hai)")
    ap.add_argument("--manual-pay", action="store_true", default=True,
                    help="Pay tum dabao (default, bank page ke liye better)")
    ap.add_argument("--corp-id", default=DEFAULT_CORP_ID)
    ap.add_argument("--emp-id", default=DEFAULT_EMP_ID)
    ap.add_argument("--watch", type=int, default=0)
    ap.add_argument("--hold", type=int, default=60)
    ap.add_argument("--proxy", action="store_true", default=True,
                    help="Geonode India residential (default ON)")
    ap.add_argument("--no-proxy", action="store_true",
                    help="proxy band")
    ap.add_argument("--proxy-country", default=GEONODE_COUNTRY)
    a = ap.parse_args()

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

    use_proxy = not a.no_proxy
    stop_bridge = None
    proxy_kw = {}
    proxy_user = None
    if use_proxy:
        proxy_user = geonode_username(a.proxy_country, sticky=True)
        log("proxy : Geonode country=%s | user=%s" % (a.proxy_country, proxy_user))
        try:
            local_port, stop_bridge = start_geonode_bridge(proxy_user)
            proxy_kw["proxy"] = {"server": "http://127.0.0.1:%d" % local_port}
            log("proxy : local bridge 127.0.0.1:%d" % local_port)
        except Exception as e:
            log("proxy FAIL (%s) -- bina proxy chalega" % e)
            use_proxy = False
            proxy_kw = {}

    chrome_proc = None
    cdp_profile = None
    with sync_playwright() as p:
        # --- REAL Chrome ONLY via CDP (NO Chrome for Testing fallback) ---
        try:
            chrome_proc, cdp_port, cdp_profile = launch_real_chrome_cdp()
            b = p.chromium.connect_over_cdp("http://127.0.0.1:%d" % cdp_port)
            log("browser: REAL Chrome via CDP (not Chrome for Testing)")
            log("         agar popup me 'Chrome for Testing' dikhe to galat script chal rahi hai")
        except Exception as e:
            log("FAIL: Real Chrome CDP nahi khula: %s" % e)
            log("  1) Google Chrome install karo")
            log("  2) ya set: CHROME_PATH=C:\\Path\\to\\chrome.exe")
            log("  Bundled Chromium (Chrome for Testing) JAAN BUJH KAR band —")
            log("  usse bank page kabhi load nahi hoti.")
            if stop_bridge is not None:
                stop_bridge.set()
            return 2

        # Context: CDP pe naya context + storage_state (session cookies)
        ctx_kwargs = dict(
            storage_state=d["state"],
            locale="en-IN",
            viewport={"width": 1500, "height": 950},
            ignore_https_errors=True,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        if proxy_kw:
            ctx_kwargs.update(proxy_kw)

        try:
            ctx = b.new_context(**ctx_kwargs)
        except Exception as e:
            log("new_context fail (%s) — default context + cookies inject" % e)
            ctx = b.contexts[0] if b.contexts else b.new_context(**{k: v for k, v in ctx_kwargs.items() if k != "storage_state"})
            # inject cookies from storage_state
            try:
                st = d.get("state") or d
                cookies = st.get("cookies") if isinstance(st, dict) else None
                if cookies:
                    ctx.add_cookies(cookies)
            except Exception as e2:
                log("cookie inject: %s" % e2)

        try:
            ctx.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = window.chrome || { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en'] });
            """)
        except Exception:
            pass

        page = ctx.new_page()

        log("\n1) product khol rahe hain: %s" % a.product)
        product_url = "%s/products/%s" % (SHOP, a.product)
        nav_ok = False
        last_err = None
        for attempt in range(1, 4):
            try:
                page.goto(product_url, wait_until="domcontentloaded", timeout=120000)
                nav_ok = True
                break
            except Exception as e:
                last_err = e
                log("   goto fail try %d/3: %s" % (attempt, str(e)[:120]))
                page.wait_for_timeout(2000)
        if not nav_ok and use_proxy:
            # proxy se nahi chala -> bina proxy retry
            log("   proxy se site nahi khuli -- bina proxy retry...")
            try:
                if stop_bridge is not None:
                    stop_bridge.set()
                    stop_bridge = None
                ctx.close()
            except Exception:
                pass
            proxy_kw = {}
            use_proxy = False
            ctx = b.new_context(
                storage_state=d["state"],
                locale="en-IN",
                viewport={"width": 1500, "height": 950},
                ignore_https_errors=True,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            )
            ctx.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = window.chrome || { runtime: {} };
            """)
            page = ctx.new_page()
            try:
                page.goto(product_url, wait_until="domcontentloaded", timeout=120000)
                nav_ok = True
                log("   bina proxy OK (bank page baad me fail ho sakti hai)")
            except Exception as e:
                last_err = e
        if not nav_ok:
            log("FAIL: product page nahi khuli: %s" % last_err)
            try:
                b.close()
            except Exception:
                pass
            if stop_bridge is not None:
                stop_bridge.set()
            return 2
        page.wait_for_timeout(5000)
        for _ in range(3):
            page.mouse.wheel(0, 900)
            page.wait_for_timeout(700)

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
                page.screenshot(path=os.path.join(OUT, "order_fail_pack.png"),
                                full_page=True)
                b.close()
                return 3

        after = variant_id(page)
        log("   chunne ke baad variant: %s%s"
            % (after, "  (badal gaya)" if after != before else "  (wahi hai)"))
        page.screenshot(path=os.path.join(OUT, "order_1_product.png"))

        log("4) add to cart")
        sel = find(page, ADD_TO_CART)
        if not sel:
            log("   FAIL: 'Add to cart' ka button nahi mila")
            b.close()
            return 4
        page.locator(sel).first.click()
        page.wait_for_timeout(6000)
        page.screenshot(path=os.path.join(OUT, "order_2_added.png"))

        cart = page.evaluate(
            "async () => (await (await fetch('/cart.js')).json())")
        log("   cart me cheezein: %d | kul Rs %s"
            % (cart.get("item_count", 0), (cart.get("total_price", 0) or 0) / 100))
        for it in cart.get("items", []):
            log("      %s | %s | Rs %s"
                % (it.get("product_title"), it.get("variant_title"),
                   (it.get("line_price", 0) or 0) / 100))
        if not cart.get("item_count"):
            log("   FAIL: cart khaali hi rah gaya")
            b.close()
            return 5
        if after and str(cart["items"][0].get("variant_id")) != str(after):
            log("   CHETAVNI: cart me doosra variant gaya hai (%s) -- dekh lijiye"
                % cart["items"][0].get("variant_id"))

        log("5) cart")
        if find(page, CHECKOUT):
            log("      cart to khud hi khul gaya")
        else:
            sel = find(page, CART_OPEN)
            if sel:
                log("      cart khol rahe hain")
                page.locator(sel).first.click()
                page.wait_for_timeout(5000)
            else:
                log("      /cart panne par ja rahe hain")
                page.goto("%s/cart" % SHOP, wait_until="domcontentloaded",
                          timeout=60000)
                page.wait_for_timeout(5000)
        page.screenshot(path=os.path.join(OUT, "order_3_cart.png"))

        log("6) Checkout daba rahe hain")
        sel = find(page, CHECKOUT)
        if not sel:
            log("   FAIL: Checkout ka button nahi mila")
            page.screenshot(path=os.path.join(OUT, "order_fail_checkout.png"),
                            full_page=True)
            b.close()
            return 6

        newpage = None
        try:
            with ctx.expect_page(timeout=15000) as np:
                page.locator(sel).first.click()
            newpage = np.value
        except Exception:
            pass
        pay = newpage or page
        pay.wait_for_timeout(12000)

        blk = clear_blocker(pay)
        if blk:
            log("   %s" % blk)

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

        log("10) gateway par %s Card chun rahe hain" % a.card_type)
        log("      %s" % pick_card_type(pay, a.card_type))
        pay.wait_for_timeout(3000)

        auto_pay = bool(a.auto_pay) and not a.no_pay_click
        log("11) Card details fill (Pay auto=%s)" % auto_pay)
        log("      %s" % fill_card_details(
            pay, a.card, a.exp, a.holder, a.cvv,
            click_pay=auto_pay,
        ))

        if not auto_pay:
            log("\n==========================================================")
            log("   CARD FILL HO GAYA. Ab aap MANUALLY:")
            log("   1) Pay button dabao")
            log("   2) Bank page load hone do (Loading Bank Page...)")
            log("   3) Corporate ID / Employee ID bharo (ya wait for script)")
            log("   Jab Corporate/Employee form dikhe -> yahan Enter dabao")
            log("==========================================================")
            try:
                input("👉 Bank form dikhne ke baad Enter: ")
            except Exception:
                pay.wait_for_timeout(120000)
        else:
            pay.wait_for_timeout(8000)

        log("12) Bank Corporate / Employee ID")
        log("      %s" % fill_bank_corporate(ctx, pay, a.corp_id, a.emp_id))
        pay.wait_for_timeout(2000)

        log("\n==========================================================")
        log("   Bank OTP page aayi ho to OTP khud bharo.")
        log("   OTP ke baad Enter dabao (agar --hold 0).")
        log("==========================================================")

        log("\n   URL: %s" % pay.url)
        try:
            txt = pay.inner_text("body") or ""
        except Exception:
            txt = ""
        lines = [l.strip() for l in txt.splitlines() if l.strip()][:16]
        log("   panne par: %s" % " | ".join(lines)[:260])
        rup = re.findall(r"₹\s?([\d,]+(?:\.\d+)?)", txt)
        log("   panne par daam: %s" % (sorted(set(rup))[:8] or "koi nahi"))
        try:
            pay.screenshot(path=os.path.join(OUT, "order_4_payment.png"))
            log("   tasveer: out/order_4_payment.png")
        except Exception as e:
            log("   (tasveer nahi bani: %s)" % str(e)[:60])

        log("\n==========================================================")
        log("   CARD + CORP/EMP FILL HO GAYA. Bank OTP aap khud bhariye.")
        log("==========================================================")
        if a.watch:
            log("   OTP ke baad script order ka wait karegi.")
            log("      %s" % wait_for_order(pay, d, a.watch))
        if a.hold == 0:
            log("   Browser khula rahega. Kaam khatam ho to yahan Enter dabaiye.")
            try:
                input()
            except Exception:
                pay.wait_for_timeout(600000)
        else:
            log("   (%ds baad band)" % a.hold)
            pay.wait_for_timeout(a.hold * 1000)
        try:
            b.close()
        except Exception:
            pass
        if chrome_proc is not None:
            try:
                chrome_proc.terminate()
            except Exception:
                pass
        if stop_bridge is not None:
            stop_bridge.set()
        if cdp_profile and os.path.isdir(cdp_profile):
            try:
                shutil.rmtree(cdp_profile, ignore_errors=True)
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())


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
#         proxy_user = geonode_username(a.proxy_country, sticky=False)
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