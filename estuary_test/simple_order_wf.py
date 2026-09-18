# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """simple_order_wf.py -- wahi simple_order flow, par ASLI WATERFOX par.

# place_order.py wala simple_order Playwright + Chrome par chalta hai. Playwright
# Waterfox (Gecko 140) ko drive nahi kar sakta, isliye ye version Selenium +
# geckodriver + Waterfox par chalta hai -- baaki poora flow, otpd (number khareed
# + OTP), aur auto-retry sab bilkul wahi.

# Selenium ka saara bhaari kaam `wf_core` me pehle se hai (project ka jaanchaa hua
# Waterfox setup): browser launch, proxy bridge, `Scope` (Playwright-jaisa API --
# frame ke andar bhi visible_first/click/fill), frames(), pages(), scroll_click,
# el_fill/el_type. Yahan sirf flow ke kadam hain.

# Flow:
#   1. Product page  2. Pack + Add to cart  3. Checkout
#   4. Mobile + OTP (otpdoctor se)  5. Address  6. Confirm email
#   7. Credit/Debit Card  8. Card type  9. Card fill + Pay
#  10. Corporate/Employee ID  11. Bank OTP (manual)

# Chalao:
#   python simple_order_wf.py --product black-white-ginger-ale --pack "Pack of 02" --guest --buy-number
# """
# import os
# import re
# import sys
# import time
# import argparse
# import traceback

# import wf_core as wf

# try:
#     import otpd
# except Exception:
#     otpd = None

# log = wf.log
# SHOP = wf.SHOP
# OUT = wf.OUT

# # ---------- default data (CLI se override) ----------
# DEFAULT_MOBILE = "9999999999"
# DEFAULT_PIN = "000000"
# DEFAULT_FIRST = "John"
# DEFAULT_LAST = "Doe"
# DEFAULT_LINE1 = "CHANGE_ME_ADDR1"
# DEFAULT_LINE2 = "CHANGE_ME_ADDR2"
# DEFAULT_EMAIL = "test@example.com"
# DEFAULT_CARD = "0000000000000000"
# DEFAULT_EXP = "01/30"
# DEFAULT_HOLDER = "Test Holder"
# DEFAULT_CVV = "000"
# DEFAULT_CORP = "streakads"
# DEFAULT_EMP = "CHANGE_ME_EMP_ID"


# def shot(scope, name):
#     try:
#         scope.screenshot(os.path.join(OUT, name))
#         log("   shot: %s" % name)
#     except Exception as e:
#         log("   shot fail: %s" % str(e)[:60])


# # ---------- frame-aware dhoondh (Playwright ke frame_with / any_frame_text jaisa) ----------
# def scope_with(driver, handle, sel, secs=12):
#     """Us window/frame ka Scope jisme `sel` dikhe (page + saare frames dekhta hai)."""
#     end = time.time() + secs
#     while time.time() < end:
#         base = wf.Scope(driver, handle)
#         try:
#             if base.count(sel):
#                 return base
#         except Exception:
#             pass
#         for fr in wf.frames(base):
#             try:
#                 if fr.count(sel):
#                     return fr
#             except Exception:
#                 continue
#         time.sleep(0.8)
#     return None


# def any_text(driver, handle, bits, secs=0):
#     """Kisi bhi frame/page me in me se koi text dikhe to True."""
#     bits = [b.lower() for b in bits]
#     end = time.time() + max(0, secs)
#     while True:
#         base = wf.Scope(driver, handle)
#         for sc in [base] + wf.frames(base):
#             try:
#                 t = (sc.body_text() or "").lower()
#                 if any(b in t for b in bits):
#                     return True
#             except Exception:
#                 continue
#         if time.time() >= end:
#             return False
#         time.sleep(0.8)


# def click_first(scope, sels):
#     for sel in sels:
#         try:
#             el = scope.visible_first(sel)
#             if el and wf.scroll_click(scope, el):
#                 return True
#         except Exception:
#             continue
#     return False


# def fill_first(scope, sels, value, label="field"):
#     for sel in sels:
#         try:
#             el = scope.visible_first(sel)
#             if el:
#                 wf.el_fill(scope, el, "")
#                 wf.el_type(scope, el, str(value), delay=40)
#                 log("      %s -> %s" % (label, value))
#                 return True
#         except Exception:
#             continue
#     log("      %s FAIL (nahi mila)" % label)
#     return False


# # ================= FLOW STEPS =================
# def step_product(page, product, pack="", unit=""):
#     log("\n[1] Product open: %s" % product)
#     page.goto("%s/products/%s" % (SHOP, product), timeout=120)
#     page.wait_for_timeout(3000)
#     try:
#         page.evaluate("window.scrollBy(0, 700);")
#         page.wait_for_timeout(400)
#         page.evaluate("window.scrollBy(0, 700);")
#     except Exception:
#         pass

#     if unit:
#         log("   unit: %s" % unit)
#         page.evaluate(
#             "const r=[...document.querySelectorAll('input[type=radio]')]"
#             ".find(x=>(x.value||'').trim()===arguments[0]); if(r&&!r.checked)r.click();",
#             unit)
#         page.wait_for_timeout(1500)

#     if pack:
#         log("   pack: %s" % pack)
#         ok = page.evaluate(
#             "const r=[...document.querySelectorAll('input[type=radio]')]"
#             ".find(x=>(x.value||'').trim()===arguments[0]);"
#             "if(!r)return false; if(!r.checked)r.click(); return true;", pack)
#         if not ok:
#             log("   FAIL: pack nahi mila")
#             shot(page, "fail_pack.png")
#             return False
#         page.wait_for_timeout(1500)

#     shot(page, "01_product.png")
#     return True


# def step_add_to_cart(page):
#     log("\n[2] Add to cart")
#     sels = ["button.add-to-cart", "button:has-text('Add to cart')",
#             "button:has-text('ADD TO CART')"]
#     if not click_first(page, sels):
#         log("   FAIL: Add to cart button nahi mila")
#         shot(page, "fail_add_cart.png")
#         return False
#     page.wait_for_timeout(5000)
#     try:
#         cart = page.evaluate(
#             "var x=new XMLHttpRequest(); x.open('GET','/cart.js',false); x.send(null);"
#             "return JSON.parse(x.responseText);")
#         log("   cart items=%s | Rs %s" % (
#             cart.get("item_count"), (cart.get("total_price") or 0) / 100))
#         if not cart.get("item_count"):
#             log("   FAIL: cart empty")
#             return False
#     except Exception as e:
#         log("   cart.js read: %s" % str(e)[:80])
#     shot(page, "02_cart.png")
#     return True


# def step_checkout(driver, page):
#     """Checkout dabao. Naya tab khule to uska Scope, warna wahi page."""
#     log("\n[3] Checkout click")
#     if not page.count("#yt-checkout-button, button:has-text('Checkout')"):
#         click_first(page, ["a[data-js-sidebar-handle]", "a[title='Open cart']",
#                            "a:has-text('Cart')"])
#         page.wait_for_timeout(3000)

#     before = set(driver.window_handles)
#     sels = ["#yt-checkout-button", "button:has-text('Checkout')",
#             "a:has-text('Checkout')"]
#     if not click_first(page, sels):
#         log("   FAIL: Checkout button nahi mila")
#         shot(page, "fail_checkout_btn.png")
#         return None

#     # naya tab aaya?
#     pay = page
#     for _ in range(15):
#         naye = set(driver.window_handles) - before
#         if naye:
#             pay = wf.Scope(driver, naye.pop())
#             log("   checkout naye tab me khula")
#             break
#         time.sleep(1)
#     pay.wait_for_timeout(8000)
#     shot(pay, "03_after_checkout.png")
#     return pay


# def step_mobile_otp(driver, pay, mobile, handle=None):
#     """handle diya ho to OTP otpdoctor se; nahi to haath se."""
#     log("\n[4] Mobile + OTP")
#     MOBILE_SEL = "9999999999'mobile'], input[type='tel']"
#     scope = scope_with(driver, pay.handle, MOBILE_SEL, secs=15)
#     if scope is None:
#         if scope_with(driver, pay.handle, "input#pincode", secs=3) or \
#                 any_text(driver, pay.handle, ["payment method", "credit/debit"]):
#             log("   SKIP: mobile already done")
#             return True
#         log("   FAIL: mobile input nahi mila")
#         shot(pay, "fail_mobile.png")
#         return False

#     fill_first(scope, [
#         "input#mobile", "input[name='mobile']", "input[type='tel']",
#         "input[placeholder*='mobile' i]", "input[placeholder*='phone' i]",
#     ], mobile, "mobile")
#     scope.wait_for_timeout(1000)

#     OTP_BOX = ('input[aria-label*="Digit"], input[autocomplete="one-time-code"], '
#                'input[maxlength="1"]')
#     SEND = ['button:has-text("Continue")', 'button:has-text("Send OTP")',
#             'button:has-text("Get OTP")', 'button[type="submit"]',
#             'button:has-text("Submit")']
#     click_first(scope, SEND)
#     pay.wait_for_timeout(3000)

#     # OTP ke khaane aane tak ruko -- 3 baar tak Send dobara (panna dhire load
#     # ho to bhi OTP page aa jaye). Yahi "OTP page nahi aaya" ko rokta hai.
#     otp_scope = None
#     for tryn in range(1, 4):
#         otp_scope = scope_with(driver, pay.handle, OTP_BOX, secs=15)
#         if otp_scope is not None:
#             break
#         if scope_with(driver, pay.handle, "input#pincode", secs=2) or \
#                 any_text(driver, pay.handle, ["payment method", "credit/debit"]):
#             log("   SKIP: OTP nahi maanga (already verified)")
#             return True
#         log("   OTP ke khaane abhi nahi aaye -- Send dobara (%d/3)" % tryn)
#         s2 = scope_with(driver, pay.handle, MOBILE_SEL, secs=3) or scope
#         click_first(s2, SEND)
#         pay.wait_for_timeout(4000)
#     if otp_scope is None:
#         log("   FAIL: OTP boxes nahi mile")
#         shot(pay, "fail_otp_boxes.png")
#         return False

#     # OTP lao
#     otp = ""
#     if handle is not None and otpd is not None:
#         log("   OTP otpdoctor se aa raha hai (number %s)" % handle.get("phone"))
#         otp = otpd.get_otp(handle, log=log)
#         if not otp:
#             log("   OTP nahi aaya -- resend keh kar dobara")
#             try:
#                 otpd.resend(handle)
#             except Exception:
#                 pass
#             otp = otpd.get_otp(handle, log=log)
#     else:
#         try:
#             otp = input("👉 OTP type karo: ").strip()
#         except Exception:
#             otp = ""
#     if not otp:
#         log("   FAIL: OTP nahi mila")
#         return False

#     log("   OTP fill: %s" % otp)
#     boxes = otp_scope.query(OTP_BOX)
#     if len(boxes) > 1:
#         otp_scope.use()
#         for i, ch in enumerate(otp):
#             if i >= len(boxes):
#                 break
#             try:
#                 boxes[i].send_keys(ch)
#             except Exception:
#                 pass
#             time.sleep(0.15)
#     elif boxes:
#         wf.el_fill(otp_scope, boxes[0], "")
#         wf.el_type(otp_scope, boxes[0], otp, delay=60)

#     otp_scope.wait_for_timeout(800)
#     click_first(otp_scope, [
#         'button:has-text("Verify")', 'button:has-text("Submit")',
#         'button[type="submit"]', 'button:has-text("Continue")',
#     ])
#     pay.wait_for_timeout(4000)
#     shot(pay, "04_after_mobile_otp.png")

#     if any_text(driver, pay.handle,
#                 ["invalid otp", "incorrect otp", "otp expired", "wrong otp"]):
#         log("   FAIL: OTP galat")
#         return False
#     if handle is not None:
#         handle["used"] = True
#     return True


# def step_address(driver, pay, a):
#     log("\n[5] Address form")
#     scope = scope_with(driver, pay.handle, "input#pincode, input[name='pincode']",
#                        secs=15)
#     if scope is None:
#         if any_text(driver, pay.handle,
#                     ["payment method", "credit/debit", "confirm your email"]):
#             log("   SKIP: address already saved")
#             return True
#         log("   FAIL: pincode box nahi mila")
#         shot(pay, "fail_address.png")
#         return False

#     fill_first(scope, ["input#pincode", "input[name='pincode']",
#                        "input[placeholder*='pincode' i]", "input[placeholder*='pin' i]"],
#                a.pin, "pincode")
#     scope.wait_for_timeout(2000)
#     fill_first(scope, ["input#name", "input[name='firstName']",
#                        "input[name='first_name']", "input[placeholder*='first' i]"],
#                a.first, "first")
#     fill_first(scope, ["input#lastName", "input[name='lastName']",
#                        "input[name='last_name']", "input[placeholder*='last' i]"],
#                a.last, "last")
#     fill_first(scope, ["textarea#line1", "input#line1", "input[name='address1']",
#                        "textarea[name='address1']", "input[placeholder*='address' i]"],
#                a.line1, "line1")
#     fill_first(scope, ["textarea#line2", "input#line2", "input[name='address2']",
#                        "textarea[name='address2']"], a.line2, "line2")
#     fill_first(scope, ["input#email", "input[name='email']", "input[type='email']"],
#                a.email, "email")
#     scope.wait_for_timeout(800)

#     try:
#         el = scope.visible_first("input[name='home']")
#         if el:
#             wf.scroll_click(scope, el)
#     except Exception:
#         pass

#     if not click_first(scope, [
#         "button#addAddressBtn", 'button:has-text("Add address")',
#         'button:has-text("Save and select")', 'button:has-text("Save")',
#         'button[type="submit"]',
#     ]):
#         log("   FAIL: Add address button nahi mila")
#         shot(pay, "fail_address_btn.png")
#         return False
#     pay.wait_for_timeout(5000)
#     shot(pay, "05_after_address.png")
#     return True


# def step_confirm_email(driver, pay, email):
#     log("\n[6] Confirm email")
#     if not any_text(driver, pay.handle, ["confirm your email", "confirm email"]):
#         log("   SKIP: email confirm ki zaroorat nahi")
#         return True

#     scope = scope_with(driver, pay.handle,
#                        'input#email, input[name="email"], input[type="email"]', secs=8)
#     if scope is not None:
#         fill_first(scope, ['input#email', 'input[name="email"]',
#                            'input[type="email"]'], email, "email")
#         scope.wait_for_timeout(600)

#     btn_sels = ['button#src-update-address-btn', 'button:has-text("Confirm email")',
#                 'button:has-text("Confirm Email")', 'button:has-text("Confirm")',
#                 'a:has-text("Confirm email")', 'button[type="submit"]']
#     clicked = False
#     base = wf.Scope(driver, pay.handle)
#     for sc in [base] + wf.frames(base):
#         if click_first(sc, btn_sels):
#             clicked = True
#             log("   Confirm email clicked")
#             break
#     if not clicked:
#         log("   FAIL: Confirm email button nahi mila")
#         shot(pay, "fail_confirm_email.png")
#         return False

#     pay.wait_for_timeout(4000)
#     if any_text(driver, pay.handle, ["please confirm your email"]) and not any_text(
#             driver, pay.handle, ["payment method", "credit/debit"]):
#         log("   FAIL: email confirm ke baad bhi error")
#         shot(pay, "fail_confirm_email_stuck.png")
#         return False
#     shot(pay, "06_after_email.png")
#     return True


# def step_pick_card(driver, pay):
#     log("\n[7] Credit/Debit Card select")
#     base = wf.Scope(driver, pay.handle)
#     scope = None
#     for fr in wf.frames(base):
#         u = (fr.url or "")
#         if "fastrr" in u or "pickrr" in u or "boost" in u:
#             scope = fr
#             break
#     if scope is None:
#         scope = base

#     sels = [
#         "#payment-method-button-Card label.payment-button-heading",
#         "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
#         "#payment-method-button-Card",
#         "label:has-text('Credit/Debit Card')",
#         "*:text-is('Credit/Debit Card')",
#         "div:has-text('Credit/Debit Card')",
#     ]
#     clicked = click_first(scope, sels)
#     if not clicked:
#         for sc in [base] + wf.frames(base):
#             if click_first(sc, sels):
#                 clicked = True
#                 break
#     if not clicked:
#         log("   FAIL: Credit/Debit Card option nahi mila")
#         shot(pay, "fail_card_pick.png")
#         return False
#     pay.wait_for_timeout(4000)
#     shot(pay, "07_card_method.png")
#     return True


# def step_card_type(driver, pay, kind="Credit"):
#     log("\n[8] Gateway %s Card choose" % kind)
#     sels = [
#         "span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
#         "span.lang-en:text-is('%s Card')" % kind,
#         "*:text-is('%s Card')" % kind,
#         "label:has-text('%s Card')" % kind,
#         "div:has-text('%s Card')" % kind,
#     ]
#     end = time.time() + 40
#     while time.time() < end:
#         base = wf.Scope(driver, pay.handle)
#         for sc in [base] + wf.frames(base):
#             if click_first(sc, sels):
#                 log("   %s Card clicked" % kind)
#                 pay.wait_for_timeout(4000)
#                 shot(pay, "08_card_type.png")
#                 return True
#         pay.wait_for_timeout(1500)
#     log("   WARN: %s Card option nahi mila -- form pehle se open ho sakta hai" % kind)
#     return True


# def step_fill_card(driver, pay, card, exp, holder, cvv, auto_pay=False):
#     log("\n[9] Card details fill")
#     CARD_SEL = '0000000000000000"card_number"], input[placeholder="Test Holder"]'
#     fr = scope_with(driver, pay.handle, CARD_SEL, secs=40)
#     if fr is None:
#         log("   FAIL: card form nahi aaya")
#         shot(pay, "fail_card_form.png")
#         return False

#     num = re.sub(r"\s+", "", card)
#     num_disp = " ".join(num[i:i + 4] for i in range(0, len(num), 4)) if len(num) == 16 else num
#     fill_first(fr, ['input[name="card_number"]', 'input[placeholder="Test Holder"]'],
#                num_disp, "card")
#     fill_first(fr, ['input[name="card_exp_date"]', 'input[placeholder="Test Holder"]'],
#                exp, "exp")
#     fill_first(fr, ['input[placeholder="Test Holder"]',
#                     'input[name*="card_holder" i]', 'input[name^="ebz_card_holder"]'],
#                holder, "holder")
#     fill_first(fr, ['input[name="card_cvv"]', 'input[placeholder="Test Holder"]'], cvv, "cvv")

#     log("   Pay se pehle wait...")
#     pay.wait_for_timeout(6000)
#     shot(pay, "09_card_filled.png")

#     if auto_pay:
#         log("   Pay click...")
#         base = wf.Scope(driver, pay.handle)
#         for sc in [fr, base] + wf.frames(base):
#             if click_first(sc, ['button:has-text("Pay")', 'button:has-text("Pay ₹")',
#                                 'button:has-text("Pay Rs")', 'button:has-text("PAY")']):
#                 pay.wait_for_timeout(5000)
#                 break
#     else:
#         log("   >>> Pay button MANUALLY dabao (script aage bank form ka wait karegi) <<<")
#         pay.wait_for_timeout(60000)
#     return True


# def step_corp_emp(driver, pay, corp_id, emp_id):
#     log("\n[10] Corporate + Employee ID")
#     bank = None
#     end = time.time() + 90
#     while time.time() < end and bank is None:
#         for pg in wf.pages(driver):
#             try:
#                 body = (pg.body_text() or "").lower()
#             except Exception:
#                 body = ""
#             if "loading bank" in body:
#                 continue
#             if pg.count("input#corporateId, input#employeeId") or \
#                     "corporate id" in body or "employee id" in body:
#                 bank = pg
#                 break
#         if bank is None:
#             time.sleep(1.5)

#     if bank is None:
#         log("   FAIL: bank / corporate form nahi aaya")
#         shot(pay, "fail_bank.png")
#         return False

#     log("   bank URL: %s" % (bank.url or "")[:100])
#     for _ in range(15):
#         if bank.count("input#corporateId"):
#             break
#         bank.wait_for_timeout(800)

#     ok = fill_first(bank, ["input#corporateId"], corp_id, "Corporate ID")
#     bank.wait_for_timeout(600)
#     ok = fill_first(bank, ["input#employeeId"], emp_id, "Employee ID") and ok
#     bank.wait_for_timeout(1000)
#     if not ok:
#         log("   FAIL: corp/emp fill nahi hua")
#         return False

#     clicked = click_first(bank, [
#         'a.btn.primary__btn:has-text("Submit")', 'a.primary__btn',
#         'button:has-text("Submit")', 'a.btn.primary__btn',
#     ])
#     if not clicked:
#         try:
#             bank.evaluate("if (typeof submit === 'function') submit();")
#             clicked = True
#             log("   Submit via JS")
#         except Exception:
#             pass
#     if not clicked:
#         log("   FAIL: Submit nahi hua")
#         return False
#     bank.wait_for_timeout(3000)
#     shot(bank, "10_after_corp.png")
#     log("   Corporate/Employee done -- ab BANK OTP manual bharo")
#     return True


# # ================= number ================
# def buy_number():
#     if otpd is None:
#         log("otpd module nahi mila -- --buy-number kaam nahi karega")
#         return None
#     try:
#         log("otpdoctor balance: %s" % otpd.balance())
#         h = otpd.buy()
#     except Exception as e:
#         log("otpdoctor se number nahi mila: %s" % str(e)[:120])
#         return None
#     if not h:
#         log("otpdoctor: kisi server par number nahi bacha")
#     return h


# # ================= MAIN =================
# def main():
#     ap = argparse.ArgumentParser(description="Simple Estuary order -- WATERFOX")
#     ap.add_argument("--product", required=True)
#     ap.add_argument("--pack", default="")
#     ap.add_argument("--unit", default="")
#     ap.add_argument("--session", default="")
#     ap.add_argument("--guest", action="store_true", help="bina session (logged out)")
#     ap.add_argument("--mobile", default=DEFAULT_MOBILE)
#     ap.add_argument("--pin", default=DEFAULT_PIN)
#     ap.add_argument("--first", default=DEFAULT_FIRST)
#     ap.add_argument("--last", default=DEFAULT_LAST)
#     ap.add_argument("--line1", default=DEFAULT_LINE1)
#     ap.add_argument("--line2", default=DEFAULT_LINE2)
#     ap.add_argument("--email", default=DEFAULT_EMAIL)
#     ap.add_argument("--card", default=DEFAULT_CARD)
#     ap.add_argument("--exp", default=DEFAULT_EXP)
#     ap.add_argument("--holder", default=DEFAULT_HOLDER)
#     ap.add_argument("--cvv", default=DEFAULT_CVV)
#     ap.add_argument("--corp-id", default=DEFAULT_CORP)
#     ap.add_argument("--emp-id", default=DEFAULT_EMP)
#     ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
#     ap.add_argument("--auto-pay", action="store_true", help="Pay auto click")
#     ap.add_argument("--no-proxy", action="store_true")
#     ap.add_argument("--hold", type=int, default=120, help="ant me kitne sec khula")
#     ap.add_argument("--buy-number", action="store_true",
#                     help="mobile number otpdoctor se khareedo aur OTP bhi wahin se")
#     ap.add_argument("--otp-tries", type=int, default=3,
#                     help="mobile+OTP kitni baar (har fail par naya number)")
#     a = ap.parse_args()

#     numbuy = None

#     # session (guest me nahi)
#     d = None
#     if not a.guest:
#         path = a.session or wf.newest_session()
#         if path and not os.path.isabs(path):
#             p2 = os.path.join(wf.SESSIONS, path)
#             path = p2 if os.path.exists(p2) else path
#         if path and os.path.exists(path):
#             import json
#             d = json.load(open(path, encoding="utf-8"))
#             log("session: %s / %s" % (d.get("phone"), d.get("email")))
#         else:
#             log("session nahi mili -- guest jaisa chalega")
#     else:
#         log("GUEST mode")

#     # proxy
#     stop_bridge = None
#     port = None
#     if not a.no_proxy:
#         try:
#             user = wf.geonode_username(wf.GEONODE_COUNTRY, sticky=False)
#             port, stop_bridge = wf.start_geonode_bridge(user)
#             log("proxy: Geonode | bridge 127.0.0.1:%d" % port)
#         except Exception as e:
#             log("proxy fail: %s -- bina proxy" % str(e)[:80])

#     driver = None
#     pay = None
#     page = None
#     try:
#         # Har koshish ke liye TAAZA Waterfox. Pehle ek hi browser me dobara
#         # checkout karte the -- par pichhli fail koshish ka adhoora Fastrr panna
#         # (ya beech me mara hua geckodriver) dobara istemal karne se crash aur
#         # orphan process bante the. Naye browser se har baar saaf shuruaat.
#         mobile_ok = False
#         kul = max(1, a.otp_tries)
#         for att in range(1, kul + 1):
#             log("\n==== koshish %d/%d (naya browser) ====" % (att, kul))
#             if a.buy_number:
#                 numbuy = buy_number()
#                 if numbuy is None:
#                     return 2
#                 a.mobile = numbuy["phone"]
#                 log("khareeda number: %s (isi par OTP aayega)" % a.mobile)

#             driver = wf.launch_waterfox(proxy_port=port, headless=False)
#             log("browser: WATERFOX (geckodriver)")
#             if d:
#                 try:
#                     wf.load_session(driver, d)
#                 except Exception as e:
#                     log("session load dikkat: %s" % str(e)[:80])
#             page = wf.Scope(driver, driver.current_window_handle)

#             try:
#                 if not step_product(page, a.product, a.pack, a.unit):
#                     return 3
#                 if not step_add_to_cart(page):
#                     return 4
#                 pay = step_checkout(driver, page)
#                 if pay is None:
#                     return 5
#                 if step_mobile_otp(driver, pay, a.mobile, handle=numbuy):
#                     mobile_ok = True
#                     break
#             except Exception:
#                 log("   is koshish me gadbad:")
#                 for l in traceback.format_exc().splitlines()[-4:]:
#                     log("      " + l)

#             # koshish fail -- number wapas, browser band, phir naya
#             if numbuy is not None and otpd is not None and not numbuy.get("used"):
#                 try:
#                     otpd.cancel(numbuy, log=log)
#                 except Exception:
#                     pass
#             numbuy = None
#             try:
#                 driver.quit()
#             except Exception:
#                 pass
#             driver = None
#             if not a.buy_number:
#                 break
#             time.sleep(3)

#         if not mobile_ok:
#             log("   FAIL: %d koshish ke baad bhi mobile+OTP nahi hua" % kul)
#             return 6

#         if not step_address(driver, pay, a):
#             return 7
#         if not step_confirm_email(driver, pay, a.email):
#             return 8
#         if not step_pick_card(driver, pay):
#             return 9
#         step_card_type(driver, pay, a.card_type)
#         if not step_fill_card(driver, pay, a.card, a.exp, a.holder, a.cvv,
#                               auto_pay=a.auto_pay):
#             return 10
#         if not step_corp_emp(driver, pay, a.corp_id, a.emp_id):
#             return 11

#         log("\n[11] Bank OTP ab MANUAL bharo, phir wait...")
#         log("==========================================================")
#         pay.wait_for_timeout(max(1, a.hold) * 1000)
#         log("DONE")
#         return 0
#     except Exception:
#         log("\nGADBAD:")
#         for l in traceback.format_exc().splitlines()[-8:]:
#             log("   " + l)
#         return 1
#     finally:
#         if driver is not None:
#             try:
#                 driver.quit()
#             except Exception:
#                 pass
#         if stop_bridge is not None:
#             stop_bridge.set()
#         if numbuy is not None and otpd is not None and not numbuy.get("used"):
#             try:
#                 otpd.cancel(numbuy, log=log)
#             except Exception:
#                 pass


# if __name__ == "__main__":
#     sys.exit(main() or 0)



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""simple_order_wf.py -- Waterfox se Estuary order (Shiprocket checkout).

Ab OTP-doctor / number-buy nahi -- website simple ho gayi hai: mobile number
sirf bharna hai (koi mobile OTP nahi). Sirf bank ka 3D-secure OTP API se aata
hai.

Flow:
  1. Product  2. Pack + Add to cart  3. Checkout (Shiprocket popup)
  4. Coupon apply  5. Mobile number (fixed)  6. Address form
  7. Pay Online  8. Credit/Debit Card  9. Card type
 10. Card fill + Pay  11. Corporate/Employee  12. Bank OTP (API se)

Chalao:
  python simple_order_wf.py --product black-white-ginger-ale --pack "Pack of 02" --guest
  python simple_order_wf.py --product black-white-ginger-ale --pack "Pack of 02" --guest --no-pay
"""
import os
import re
import sys
import time
import argparse
import traceback

import wf_core as wf

log = wf.log
SHOP = wf.SHOP
OUT = wf.OUT

# ---------- defaults (NO fixed mobile) ----------
DEFAULT_PIN = "000000"
DEFAULT_FIRST = "John"
DEFAULT_LAST = "Doe"
DEFAULT_LINE1 = "CHANGE_ME_ADDR1"
DEFAULT_LINE2 = "CHANGE_ME_ADDR2"
DEFAULT_EMAIL = "test@example.com"
DEFAULT_CARD = "0000000000000000"
DEFAULT_EXP = "01/30"
DEFAULT_HOLDER = "Test Holder"
DEFAULT_CVV = "000"
DEFAULT_CORP = "streakads"
DEFAULT_EMP = "CHANGE_ME_EMP_ID"
DEFAULT_COUPON = "EBSW"
DEFAULT_MOBILE = "9999999999"


def shot(scope, name):
    try:
        scope.screenshot(os.path.join(OUT, name))
        log("   shot: %s" % name)
    except Exception as e:
        log("   shot fail: %s" % str(e)[:60])


def scope_with(driver, handle, sel, secs=12):
    end = time.time() + secs
    while time.time() < end:
        base = wf.Scope(driver, handle)
        try:
            if base.count(sel):
                return base
        except Exception:
            pass
        for fr in wf.frames(base):
            try:
                if fr.count(sel):
                    return fr
            except Exception:
                continue
        time.sleep(0.8)
    return None


def any_text(driver, handle, bits, secs=0):
    bits = [b.lower() for b in bits]
    end = time.time() + max(0, secs)
    while True:
        base = wf.Scope(driver, handle)
        for sc in [base] + wf.frames(base):
            try:
                t = (sc.body_text() or "").lower()
                if any(b in t for b in bits):
                    return True
            except Exception:
                continue
        if time.time() >= end:
            return False
        time.sleep(0.8)


def click_first(scope, sels):
    for sel in sels:
        try:
            el = scope.visible_first(sel)
            if el and wf.scroll_click(scope, el):
                return True
        except Exception:
            continue
    return False


def fill_first(scope, sels, value, label="field"):
    for sel in sels:
        try:
            el = scope.visible_first(sel)
            if el:
                wf.el_fill(scope, el, "")
                wf.el_type(scope, el, str(value), delay=40)
                log("      %s -> %s" % (label, value))
                return True
        except Exception:
            continue
    log("      %s FAIL (nahi mila)" % label)
    return False


def js_click_text(scope, pattern):
    try:
        ok = scope.evaluate(
            """
            const want = new RegExp(arguments[0], 'i');
            const nodes = [...document.querySelectorAll(
                'button, a, label, [role="button"], [role="radio"], div, span, li')];
            const hits = nodes.filter(e => {
                const t = (e.innerText || e.value || '').trim();
                return want.test(t) && t.length < 80 && e.getClientRects().length;
            });
            if (!hits.length) return false;
            hits.sort((a,b) => (a.innerText||'').length - (b.innerText||'').length);
            const el = hits[0];
            const radio = (el.closest && el.closest('label') &&
                el.closest('label').querySelector('input[type=radio]'))
                || (el.querySelector && el.querySelector('input[type=radio]'));
            (radio || el).click();
            return true;
            """, pattern)
        return bool(ok)
    except Exception:
        return False


def click_anywhere(driver, handle, sels, text_pat=None, secs=25, label="",
                   extra_scope=None):
    """Kuch der tak, page + saare frames me, CSS phir text se click karta rahe.

    Ek hi baar dekhne se click reh jaata tha (panna abhi bhi ban raha hota, ya
    button frame ke andar). Isliye ~secs tak baar baar koshish -- yahi confirm
    email / card / pay wale chhoote clicks theek karta hai.
    """
    import time as _t
    end = _t.time() + secs
    while _t.time() < end:
        scopes = []
        if extra_scope is not None:
            scopes.append(extra_scope)
        base = wf.Scope(driver, handle)
        scopes += [base] + wf.frames(base)
        for sc in scopes:
            try:
                if click_first(sc, sels):
                    if label:
                        log("   %s clicked" % label)
                    return True
            except Exception:
                pass
            if text_pat:
                try:
                    if js_click_text(sc, text_pat):
                        if label:
                            log("   %s clicked (text)" % label)
                        return True
                except Exception:
                    pass
        _t.sleep(1.2)
    return False


def step_product(page, product, pack="", unit=""):
    log("\n[1] Product open: %s" % product)
    page.goto("%s/products/%s" % (SHOP, product), timeout=120)
    page.wait_for_timeout(3000)
    try:
        page.evaluate("window.scrollBy(0, 700);")
        page.wait_for_timeout(400)
        page.evaluate("window.scrollBy(0, 700);")
    except Exception:
        pass

    if unit:
        log("   unit: %s" % unit)
        page.evaluate(
            "const r=[...document.querySelectorAll('input[type=radio]')]"
            ".find(x=>(x.value||'').trim()===arguments[0]); if(r&&!r.checked)r.click();",
            unit)
        page.wait_for_timeout(1500)

    if pack:
        log("   pack: %s" % pack)
        ok = page.evaluate(
            "const r=[...document.querySelectorAll('input[type=radio]')]"
            ".find(x=>(x.value||'').trim()===arguments[0]);"
            "if(!r)return false; if(!r.checked)r.click(); return true;", pack)
        if not ok:
            log("   FAIL: pack nahi mila")
            shot(page, "fail_pack.png")
            return False
        page.wait_for_timeout(1500)

    shot(page, "01_product.png")
    return True


def step_add_to_cart(page):
    log("\n[2] Add to cart")
    sels = ["button.add-to-cart", "button:has-text('Add to cart')",
            "button:has-text('ADD TO CART')"]
    if not click_first(page, sels):
        if not js_click_text(page, r"add\s*to\s*cart"):
            log("   FAIL: Add to cart button nahi mila")
            shot(page, "fail_add_cart.png")
            return False
        log("   Add to cart (js)")
    page.wait_for_timeout(5000)
    try:
        cart = page.evaluate(
            "var x=new XMLHttpRequest(); x.open('GET','/cart.js',false); x.send(null);"
            "return JSON.parse(x.responseText);")
        log("   cart items=%s | Rs %s" % (
            cart.get("item_count"), (cart.get("total_price") or 0) / 100))
        if not cart.get("item_count"):
            log("   FAIL: cart empty")
            return False
    except Exception as e:
        log("   cart.js read: %s" % str(e)[:80])
    shot(page, "02_cart.png")
    return True


def step_checkout(driver, page):
    log("\n[3] Checkout click")
    if not page.count("#yt-checkout-button") and not page.count("button:has-text('Checkout')"):
        click_first(page, ["a[data-js-sidebar-handle]", "a[title='Open cart']",
                           "a:has-text('Cart')"])
        page.wait_for_timeout(3000)

    before = set(driver.window_handles)
    sels = ["#yt-checkout-button", "button:has-text('Checkout')", "a:has-text('Checkout')"]
    if not click_first(page, sels):
        if not js_click_text(page, r"checkout|check\s*out"):
            log("   FAIL: Checkout button nahi mila")
            shot(page, "fail_checkout_btn.png")
            return None
        log("   Checkout (js)")

    pay = page
    for _ in range(18):
        naye = set(driver.window_handles) - before
        if naye:
            pay = wf.Scope(driver, naye.pop())
            log("   checkout naye tab me khula")
            break
        time.sleep(1)
    pay.wait_for_timeout(8000)
    shot(pay, "03_after_checkout.png")
    return pay


def step_mobile(driver, pay, mobile):
    """Mobile number bharo -- ab koi OTP nahi (website simple ho gayi).

    Shiprocket popup me sirf ek phone ka khaana hota hai (id=contactNumber).
    Number fixed hai (script/arg se); OTP maangne/verify karne ka kuch nahi."""
    log("\n[5] Mobile number: %s" % mobile)
    MOBILE_SEL = ("input#contactNumber, input[autocomplete='tel'], "
                  "input[type='tel'], input[name='mobile']")
    scope = scope_with(driver, pay.handle, MOBILE_SEL, secs=20)
    if scope is None:
        if any_text(driver, pay.handle,
                    ["payment method", "credit/debit", "pay online"]):
            log("   SKIP: mobile pehle se bhara")
            return True
        log("   FAIL: mobile input nahi mila")
        shot(pay, "fail_mobile.png")
        return False

    if not fill_first(scope, [
        "input#contactNumber",
        "input[autocomplete='tel']",
        "input[type='tel']",
        "input[name='mobile']",
    ], mobile, "mobile"):
        log("   FAIL: mobile fill nahi hua")
        return False
    scope.wait_for_timeout(1000)
    shot(pay, "04_mobile.png")
    return True


def step_pay_online(driver, pay):
    """Address/mobile bharne ke baad neeche 'Pay Online' button dabana.

    Shiprocket popup me do button aate hain -- 'Order now - Cash on Delivery'
    aur 'Pay Online'. Hume prepaid chahiye, isliye 'Pay Online' -- yahi aage
    payment gateway (Credit/Debit Card) tak le jaata hai."""
    log("\n[7] Pay Online")
    sels = [
        "button.cod-form-prepaid-button",
        "button:has-text('Pay Online')",
    ]
    if not click_anywhere(driver, pay.handle, sels,
                          text_pat=r"pay\s*online", secs=30,
                          label="Pay Online"):
        log("   FAIL: Pay Online button nahi mila")
        shot(pay, "fail_pay_online.png")
        return False
    pay.wait_for_timeout(5000)
    shot(pay, "07_after_pay_online.png")
    return True


def step_address(driver, pay, a):
    log("\n[5] Address form")
    scope = scope_with(driver, pay.handle, "input#pincode, input[name='pincode']", secs=18)
    if scope is None:
        if any_text(driver, pay.handle,
                    ["payment method", "credit/debit", "confirm your email"]):
            log("   SKIP: address already saved")
            return True
        log("   FAIL: pincode box nahi mila")
        shot(pay, "fail_address.png")
        return False

    fill_first(scope, ["input#pincode", "input[name='pincode']"], a.pin, "pincode")
    scope.wait_for_timeout(2000)
    fill_first(scope, ["input#name", "input[name='firstName']", "input[name='first_name']"],
               a.first, "first")
    fill_first(scope, ["input#lastName", "input[name='lastName']", "input[name='last_name']"],
               a.last, "last")
    fill_first(scope, ["textarea#line1", "input#line1", "input[name='address1']",
                       "textarea[name='address1']"], a.line1, "line1")
    fill_first(scope, ["textarea#line2", "input#line2", "input[name='address2']",
                       "textarea[name='address2']"], a.line2, "line2")
    fill_first(scope, ["input#email", "input[name='email']", "input[type='email']"],
               a.email, "email")
    scope.wait_for_timeout(800)

    # Address type (Home/Work) -- ho to Home chun do (zaroori nahi hota)
    try:
        el = scope.visible_first("input[name='home']")
        if el:
            wf.scroll_click(scope, el)
    except Exception:
        pass
    # (bare 'Home' text-click nahi -- site ka nav 'Home' link galti se dab sakta
    #  hai; sirf address-type ke radio/label tak seemit rakhte hain)
    click_first(scope, ["label:has-text('Home')",
                        "input[value='home' i]", "input[value='Home']"])

    # Is Shiprocket form me alag 'Add address' button zaroori NAHI -- form bhar
    # ke seedha neeche 'Pay Online' aata hai. Isliye save/add wala button ho to
    # daba do, na ho to koi baat nahi (aage step_pay_online sambhal lega).
    # Pehle yahan FAIL karke order rok dena galat tha.
    if click_first(scope, [
        "button#addAddressBtn", 'button:has-text("Add address")',
        'button:has-text("Save and select")', 'button:has-text("Save address")',
        'button:has-text("Save")',
    ]) or js_click_text(scope, r"add\s*address|save\s*and\s*select|save\s*address"):
        log("   address save/add button dabaya")
        pay.wait_for_timeout(4000)
    else:
        log("   (koi Add-address button nahi -- form inline hai, aage Pay Online)")
    shot(pay, "05_after_address.png")
    return True


def step_coupon(driver, pay, coupon):
    """OTP ke baad wale panne par sabse upar coupon lagana.

    Kadam: 'View all coupons >' (#src-enter-coupon-button) dabao -> coupon ka
    khaana (#src-coupon-cart-value) me code type karo -> 'Apply'
    (#src-cart-apply-coupon-btn) dabao. Coupon na lage to order ruke nahi --
    isliye har haal me True lautata hai (sirf warn karta hai).
    """
    log("\n[5b] Coupon lagao: %s" % (coupon or "(koi nahi)"))
    if not coupon:
        log("   SKIP: coupon nahi diya")
        return True

    # 1) 'View all coupons >' kholo
    if not click_anywhere(driver, pay.handle,
                          ["#src-enter-coupon-button",
                           "#src-enter-coupon-button span",
                           "div:has-text('View all coupons')"],
                          text_pat=r"view\s*all\s*coupons", secs=15,
                          label="View all coupons"):
        log("   WARN: 'View all coupons' nahi mila -- coupon skip")
        return True
    pay.wait_for_timeout(2000)

    # 2) coupon ka khaana bharo
    scope = scope_with(driver, pay.handle,
                       "input#src-coupon-cart-value, "
                       "input[placeholder='Test Holder']", secs=12)
    if scope is None:
        log("   WARN: coupon input nahi aaya -- skip")
        shot(pay, "fail_coupon_input.png")
        return True
    if not fill_first(scope, [
        "input#src-coupon-cart-value",
        "input[placeholder='Test Holder']",
    ], coupon, "coupon"):
        log("   WARN: coupon type nahi hua -- skip")
        return True
    scope.wait_for_timeout(800)

    # 3) Apply dabao
    if not click_anywhere(driver, pay.handle,
                          ["#src-cart-apply-coupon-btn",
                           "button#src-cart-apply-coupon-btn",
                           "button:has-text('Apply')"],
                          text_pat=r"^\s*apply\s*$", secs=15,
                          label="Apply coupon", extra_scope=scope):
        log("   WARN: Apply button nahi mila -- coupon skip")
        return True
    pay.wait_for_timeout(3500)
    shot(pay, "05b_after_coupon.png")

    if any_text(driver, pay.handle,
                ["invalid coupon", "coupon is not", "not applicable",
                 "coupon expired", "invalid code"], secs=1):
        log("   WARN: coupon shayad na laga (invalid/na-applicable) -- aage badh rahe")
    else:
        log("   coupon apply ho gaya")
    return True


def step_confirm_email(driver, pay, email):
    log("\n[6] Confirm email")
    if not any_text(driver, pay.handle, ["confirm your email", "confirm email"], secs=2):
        log("   SKIP: email confirm ki zaroorat nahi")
        return True

    scope = scope_with(
        driver, pay.handle,
        'input#email, input[name="email"], input[type="email"]', secs=8)
    if scope is not None:
        fill_first(scope, [
            'input#email', 'input[name="email"]', 'input[type="email"]',
        ], email, "email")
        scope.wait_for_timeout(600)

    btn_sels = [
        'button#src-update-address-btn',
        'button:has-text("Confirm email")',
        'button:has-text("Confirm Email")',
        'button:has-text("Confirm")',
        'a:has-text("Confirm email")',
    ]
    if not click_anywhere(driver, pay.handle, btn_sels,
                          text_pat=r"confirm\s*email", secs=25,
                          label="Confirm email"):
        log("   FAIL: Confirm email button nahi mila")
        shot(pay, "fail_confirm_email.png")
        return False

    pay.wait_for_timeout(4000)
    shot(pay, "06_after_email.png")
    return True


def step_pick_card(driver, pay):
    log("\n[7] Credit/Debit Card select")
    sels = [
        "#payment-method-button-Card label.payment-button-heading",
        "label.payment-button-heading:has(span:text-is('Credit/Debit Card'))",
        "#payment-method-button-Card",
        "label:has-text('Credit/Debit Card')",
        "*:text-is('Credit/Debit Card')",
        "div:has-text('Credit/Debit Card')",
    ]
    if not click_anywhere(driver, pay.handle, sels,
                          text_pat=r"credit\s*/?\s*debit\s*card", secs=30,
                          label="Credit/Debit Card"):
        log("   FAIL: Credit/Debit Card option nahi mila")
        shot(pay, "fail_card_pick.png")
        return False
    pay.wait_for_timeout(4000)
    shot(pay, "07_card_method.png")
    return True


def step_card_type(driver, pay, kind="Credit"):
    log("\n[8] Gateway %s Card choose" % kind)
    sels = [
        "span.payment-mode-label:has(span.lang-en:text-is('%s Card'))" % kind,
        "span.lang-en:text-is('%s Card')" % kind,
        "*:text-is('%s Card')" % kind,
        "label:has-text('%s Card')" % kind,
        "div:has-text('%s Card')" % kind,
    ]
    if click_anywhere(driver, pay.handle, sels,
                      text_pat=r"%s\s*card" % re.escape(kind), secs=40,
                      label="%s Card" % kind):
        pay.wait_for_timeout(4000)
        shot(pay, "08_card_type.png")
        return True
    log("   WARN: %s Card option nahi mila -- form pehle se open ho sakta hai" % kind)
    return True


def step_fill_card(driver, pay, card, exp, holder, cvv, auto_pay=False):
    log("\n[9] Card details fill")
    CARD_SEL = '0000000000000000"card_number"], input[placeholder="Test Holder"]'
    fr = scope_with(driver, pay.handle, CARD_SEL, secs=40)
    if fr is None:
        log("   FAIL: card form nahi aaya")
        shot(pay, "fail_card_form.png")
        return False

    num = re.sub(r"\s+", "", card)
    num_disp = (" ".join(num[i:i + 4] for i in range(0, len(num), 4))
                if len(num) == 16 else num)
    fill_first(fr, ['input[name="card_number"]', 'input[placeholder="Test Holder"]'],
               num_disp, "card")
    fill_first(fr, ['input[name="card_exp_date"]', 'input[placeholder="Test Holder"]'],
               exp, "exp")
    fill_first(fr, [
        'input[placeholder="Test Holder"]',
        'input[name*="card_holder" i]',
        'input[name^="ebz_card_holder"]',
    ], holder, "holder")
    fill_first(fr, ['input[name="card_cvv"]', 'input[placeholder="Test Holder"]'], cvv, "cvv")

    log("   Pay se pehle wait...")
    pay.wait_for_timeout(6000)
    shot(pay, "09_card_filled.png")

    if auto_pay:
        log("   Pay click...")
        if click_anywhere(driver, pay.handle,
                          ['button:has-text("Pay")', 'button:has-text("Pay ₹")',
                           'button:has-text("Pay Rs")', 'button:has-text("PAY")'],
                          text_pat=r"^\s*pay(\s|₹|rs|now|$)", secs=25,
                          label="Pay", extra_scope=fr):
            pay.wait_for_timeout(5000)
        else:
            log("   WARN: Pay button nahi mila")
    else:
        log("   >>> Pay MANUALLY dabao (script bank form ka wait karegi) <<<")
        pay.wait_for_timeout(60000)
    return True


def find_bank_tab(driver, pay, secs=90):
    """Pay ke baad khule bank tab par TIKO -- baar-baar sab tab switch kiye
    bina.

    Purana tareeka har 1.5 sec me saari tabs par ghoom kar body padhta tha;
    har body-read tab badalta hai, isliye screen 'jhalak-jhalak' tab badalti
    dikhti thi. Ab: sabse naye tab ko pehle dekho (Pay usi naye tab me bank
    kholta hai), us tab par jaakar THODI DER RUKO (load hone do), tabhi agli
    tab dekho. Bank tab mil gaya to wahin ruk kar uska load poora hone do."""
    end = time.time() + secs
    while time.time() < end:
        handles = list(driver.window_handles)
        # newest tab pehle; pay/shopify wali tab sabse aakhir me.
        order = list(dict.fromkeys(
            [h for h in reversed(handles) if h != pay.handle]
            + ([pay.handle] if pay.handle in handles else [])))
        for h in order:
            sc = wf.Scope(driver, h)
            try:
                sc.use()                 # is tab par aao...
            except Exception:
                continue
            sc.wait_for_timeout(2500)    # ...aur RUKO, jaldi mat badlo
            try:
                body = (sc.body_text() or "").lower()
            except Exception:
                body = ""
            if sc.count("input#corporateId") or sc.count("input#employeeId") or \
                    "corporate id" in body or "employee id" in body:
                return sc
            if "loading bank" in body:
                # yahi bank tab hai -- bas load ho raha; isi par ruk kar dekho
                inner = time.time() + 45
                while time.time() < inner:
                    sc.wait_for_timeout(2000)
                    if sc.count("input#corporateId") or sc.count("input#employeeId"):
                        return sc
        time.sleep(1.0)
    return None


def find_in_tab(driver, handle, sels, secs=60, dwell=2.0):
    """Sirf EK tab (handle) ke andar -- page + uske frames -- koi selector
    dhoondho, doosri tab par switch kiye bina. Milte hi (scope, sel) do.

    Isse OTP ka khaana dhoondhte waqt bhi tab nahi jhalakti -- kaam usi bank
    tab me hota hai jahan pehle se hain."""
    end = time.time() + secs
    while time.time() < end:
        base = wf.Scope(driver, handle)
        try:
            base.use()
        except Exception:
            base.wait_for_timeout(int(dwell * 1000))
            continue
        for sc in [base] + wf.frames(base):
            for sel in sels:
                try:
                    if sc.visible_first(sel) is not None:
                        return sc, sel
                except Exception:
                    continue
        base.wait_for_timeout(int(dwell * 1000))
    return None, None


def step_corp_emp(driver, pay, corp_id, emp_id):
    log("\n[10] Corporate + Employee ID")
    bank = find_bank_tab(driver, pay, secs=90)
    if bank is None:
        log("   FAIL: bank / corporate form nahi aaya")
        shot(pay, "fail_bank.png")
        return None

    try:
        bank.use()          # isi bank tab par tiko -- ab switch nahi
    except Exception:
        pass
    log("   bank URL: %s" % ((bank.url or "")[:100]))
    for _ in range(15):
        if bank.count("input#corporateId"):
            break
        bank.wait_for_timeout(800)

    ok1 = fill_first(bank, ["input#corporateId"], corp_id, "Corporate ID")
    bank.wait_for_timeout(600)
    ok2 = fill_first(bank, ["input#employeeId"], emp_id, "Employee ID")
    bank.wait_for_timeout(1000)
    if not (ok1 and ok2):
        log("   FAIL: corp/emp fill nahi hua")
        return None

    clicked = click_first(bank, [
        'a.btn.primary__btn:has-text("Submit")',
        'a.primary__btn',
        'button:has-text("Submit")',
        'a.btn.primary__btn',
    ])
    if not clicked:
        try:
            bank.evaluate("if (typeof submit === 'function') submit();")
            clicked = True
            log("   Submit via JS")
        except Exception:
            pass
    if not clicked and not js_click_text(bank, r"^submit$"):
        log("   FAIL: Submit nahi hua")
        return None

    bank.wait_for_timeout(3000)
    shot(bank, "10_after_corp.png")
    log("   Corporate/Employee done -- ab BANK OTP")
    return bank


def step_bank_otp(driver, bank, emp_id, card_no):
    """Bank OTP usi bank tab me bharo -- doosri tab par mat jao.

    wf.do_otp poore browser (saari tabs) me OTP ka khaana dhoondhta hai, jisse
    fir se tab jhalakti. Yahan hum sirf isi bank tab (jahan corp/emp bhara) ke
    andar dekhte hain: API se OTP la kar bharte hain aur usi tab me SUBMIT.
    Kisi wajah se yahan na mile to hi (fallback) wf.do_otp par jaate hain."""
    log("\n[11] Bank OTP (API se, emp=%s)" % emp_id)
    sels = list(wf.OTP_FIELD_SELS)
    sc, fsel = find_in_tab(driver, bank.handle, sels, secs=90)
    if sc is None:
        log("   bank tab me OTP khaana nahi mila -- poore browser me dekhte hain")
        try:
            log("   " + wf.do_otp(driver, emp_id, card_no=card_no, manual=False))
        except Exception as e:
            log("   bank OTP gadbad: %s" % str(e)[:120])
        return
    log("   OTP khaana mila (%s)" % fsel)

    for attempt in range(1, wf.MAX_OTP_ATTEMPTS + 1):
        otp = wf.fetch_otp(emp_id, card_last4=card_no)
        if not otp:
            log("   OTP API se nahi aaya (%d/%d)" % (attempt, wf.MAX_OTP_ATTEMPTS))
            return
        el = sc.visible_first(fsel)
        if el is None:
            sc, fsel = find_in_tab(driver, bank.handle, sels, secs=20)
            if sc is None:
                log("   OTP ka khaana gayab ho gaya")
                return
            el = sc.visible_first(fsel)
        wf.el_fill(sc, el, "")
        wf.el_type(sc, el, otp, delay=120)
        log("   OTP bhar diya: %s" % otp)
        sc.wait_for_timeout(1000)

        # SUBMIT sirf isi tab me (frame + page dono, par tab wahi)
        submitted = False
        for s2 in [sc, wf.Scope(driver, bank.handle)]:
            if click_first(s2, list(wf.OTP_SUBMIT_SELS)) or \
                    js_click_text(s2, r"^\s*submit\s*$"):
                submitted = True
                break
        log("   SUBMIT: %s" % ("daba diya" if submitted else "button nahi mila"))
        sc.wait_for_timeout(4000)

        body = ""
        try:
            body = (sc.body_text() or "").lower()
        except Exception:
            pass
        if not any(m in body for m in wf.OTP_BAD_MSGS):
            log("   Bank OTP ho gaya")
            return
        log("   bank ne OTP galat kaha -- dobara mangwate hain")
    log("   OTP baar-baar galat -- ruk gaye")


def main():
    ap = argparse.ArgumentParser(
        description="Simple Estuary order -- WATERFOX (Shiprocket, no mobile OTP)")
    ap.add_argument("--product", required=True)
    ap.add_argument("--pack", default="")
    ap.add_argument("--unit", default="")
    ap.add_argument("--session", default="")
    ap.add_argument("--guest", action="store_true")
    ap.add_argument("--pin", default=DEFAULT_PIN)
    ap.add_argument("--first", default=DEFAULT_FIRST)
    ap.add_argument("--last", default=DEFAULT_LAST)
    ap.add_argument("--line1", default=DEFAULT_LINE1)
    ap.add_argument("--line2", default=DEFAULT_LINE2)
    ap.add_argument("--email", default=DEFAULT_EMAIL)
    ap.add_argument("--card", default=DEFAULT_CARD)
    ap.add_argument("--exp", default=DEFAULT_EXP)
    ap.add_argument("--holder", default=DEFAULT_HOLDER)
    ap.add_argument("--cvv", default=DEFAULT_CVV)
    ap.add_argument("--corp-id", default=DEFAULT_CORP)
    ap.add_argument("--emp-id", default=DEFAULT_EMP)
    ap.add_argument("--mobile", default=DEFAULT_MOBILE,
                    help="mobile number (fixed; ab koi OTP nahi)")
    ap.add_argument("--coupon", default=DEFAULT_COUPON,
                    help="coupon code (khaali chhodo to coupon skip)")
    ap.add_argument("--card-type", default="Credit", choices=["Credit", "Debit"])
    ap.add_argument("--auto-pay", action="store_true",
                    help="(ab default hi Pay dabta hai; rakha hai purane command ke liye)")
    ap.add_argument("--no-pay", action="store_true",
                    help="Pay mat dabao -- card fill karke ruk jao")
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument("--hold", type=int, default=120)
    a = ap.parse_args()

    d = None
    if not a.guest:
        path = a.session or wf.newest_session()
        if path and not os.path.isabs(path):
            p2 = os.path.join(wf.SESSIONS, path)
            path = p2 if os.path.exists(p2) else path
        if path and os.path.exists(path):
            import json
            d = json.load(open(path, encoding="utf-8"))
            log("session: %s / %s" % (d.get("phone"), d.get("email")))
        else:
            log("session nahi -- guest jaisa")
    else:
        log("GUEST mode")

    log("card: ****%s | %s | %s | corp=%s emp=%s" % (
        a.card[-4:], a.exp, a.holder, a.corp_id, a.emp_id))

    stop_bridge = None
    port = None
    if not a.no_proxy:
        try:
            user = wf.geonode_username(wf.GEONODE_COUNTRY, sticky=False)
            port, stop_bridge = wf.start_geonode_bridge(user)
            log("proxy: Geonode | bridge 127.0.0.1:%d" % port)
        except Exception as e:
            log("proxy fail: %s -- bina proxy" % str(e)[:80])

    driver = None
    pay = None
    try:
        driver = wf.launch_waterfox(proxy_port=port, headless=False)
        log("browser: WATERFOX")
        if d:
            try:
                wf.load_session(driver, d)
            except Exception as e:
                log("session load: %s" % str(e)[:80])
        page = wf.Scope(driver, driver.current_window_handle)

        if not step_product(page, a.product, a.pack, a.unit):
            return 3
        if not step_add_to_cart(page):
            return 4
        pay = step_checkout(driver, page)
        if pay is None:
            return 5

        # Naya (simple) flow: coupon -> mobile (bina OTP) -> address ->
        # Pay Online -> Credit/Debit Card -> ... -> bank OTP.
        step_coupon(driver, pay, a.coupon)
        if not step_mobile(driver, pay, a.mobile):
            return 6
        if not step_address(driver, pay, a):
            return 7
        if not step_pay_online(driver, pay):
            return 8
        step_confirm_email(driver, pay, a.email)   # ho to bhar de, warna skip
        if not step_pick_card(driver, pay):
            return 9
        step_card_type(driver, pay, a.card_type)
        if not step_fill_card(driver, pay, a.card, a.exp, a.holder, a.cvv,
                              auto_pay=not a.no_pay):
            return 10
        bank = step_corp_emp(driver, pay, a.corp_id, a.emp_id)
        if bank is None:
            return 11

        # Bank OTP -- usi bank tab me (tab jhalakne se bachne ke liye).
        step_bank_otp(driver, bank, a.emp_id, a.card)
        pay.wait_for_timeout(max(1, a.hold) * 1000)
        log("DONE")
        return 0
    except Exception:
        log("\nGADBAD:")
        for l in traceback.format_exc().splitlines()[-8:]:
            log("   " + l)
        return 1
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
        if stop_bridge is not None:
            stop_bridge.set()


if __name__ == "__main__":
    sys.exit(main() or 0)