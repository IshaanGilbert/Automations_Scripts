#!/usr/bin/env python3
"""make_accounts_email.py -- Estuary par EMAIL + PASSWORD se account banao.

Ye purani `make_accounts_wf.py` ki jagah nahi leti -- wo mobile+OTP wala
tareeka hai aur waisa ka waisa chalta rahega. Ye alag raasta hai:

    Sheet 'Account_emails' se ek row lo (First_Name, Last_Name, Email, Password)
        -> /account/login khol kar 'New Customer?' dabao
        -> register ka form bharo, checkbox tick karo, Create account
        -> login ho gaya to cookies sessions/ me likh do
        -> sheet me us row ke aage 'complete' ya 'failed'

Ek row dobara kabhi kaam nahi aati -- niyam sheet_emails.py me likha hai.

Do baatein jo dikhne me chhoti hain par isi par sab tika hai:

* **Popup**: site ka ShiprocketLogin wala popup kabhi bhi, kisi bhi panne par
  aa jaata hai aur form ko dhak leta hai. Har kadam par ek baar dekh lena kaafi
  nahi -- wo theek typing ke beech me bhi aa sakta hai. Isliye panne ke andar
  ek pehredaar bitha diya jaata hai jo popup bante hi use hata deta hai.
* **Login ka saboot**: "account ban gaya" maan lene ke liye panne ka text
  padhna bharosemand nahi. Shopify khud `window.__st.cid` me customer ka id
  deta hai -- wahi ek pakka saboot hai. Wo na mile to account bana hi nahi.

    python make_accounts_email.py --count 5
    python make_accounts_email.py --count 1 --no-proxy
    python make_accounts_email.py --list          # sirf dekho, banao mat
"""
import os
import re
import sys
import time
import argparse
import traceback

import place_order as po
import sheet_emails

HERE = po.HERE
SESSIONS = po.SESSIONS
LOGIN_URL = "https://estuaryworld.com/account/login?return_url=%2Faccount"
REGISTER_URL = "https://estuaryworld.com/account/register"

# ---------------------------- POPUP ----------------------------
# Shiprocket ka login popup kisi bhi pal khud aa jaata hai aur poore form ko
# dhak leta hai. Zaroori baat: ye panne ka koi `div` NAHI hai -- ye ek poora
# iframe hai jo screen bhar ka hota hai:
#
#     <iframe id="headless-iframe-login"
#             src="https://fastrr-boost-ui.pickrr.com/?popupType=shiprocketLogin&...">
#
# Jo HTML dikhta hai (ShiprocketLogin_Container, ShiprocketLogin_close) wo isi
# iframe ke ANDAR ka hai. Isliye top document me un class ko dhoondhna bekaar
# hai -- wahan wo milti hi nahin (jaanch me nodes=0 aaya tha), aur script
# chupchaap us paardarshi parde par click karti reh jaati thi. Yahi wajah thi
# ki 'Create account' dabta to tha par kuch hota nahi tha.
#
# Isliye ilaaj seedha hai: iframe ko hi nikaal do. Uske andar ka close dabane
# ke liye frame me ghusna padta (aur wo cross-origin bhi hai); iframe hata dene
# se parda ek jhatke me chala jaata hai. React use dobara laga de to pehredaar
# (MutationObserver + har 700ms) use phir hata deta hai -- isliye script ko
# kabhi rukna nahi padta.
POPUP_ARM_JS = """
  if (window.__srPopupGuard) { return window.__srPopupKilled || 0; }
  window.__srPopupGuard = true;
  window.__srPopupKilled = 0;

  const PARDA = 'iframe#headless-iframe-login,'
              + 'iframe[src*="popupType=shiprocketLogin"],'
              + 'iframe[src*="fastrr-boost-ui"]';

  const hatao = () => {
    document.querySelectorAll(PARDA).forEach(f => {
      try { f.remove(); window.__srPopupKilled++; } catch (err) {}
    });
    // kabhi popup usi panne me bhi aa sakta hai -- tab uska apna close dabao
    document.querySelectorAll('[class*="ShiprocketLogin_close"]').forEach(e => {
      if (e.getClientRects().length) {
        try { e.click(); window.__srPopupKilled++; } catch (err) {}
      }
    });
    // popup body ka scroll rok deta hai -- hatne ke baad use khol do
    if (document.body && document.body.style.overflow === 'hidden') {
      document.body.style.overflow = '';
    }
  };

  hatao();
  try {
    new MutationObserver(hatao).observe(document.documentElement,
                                        {childList: true, subtree: true});
  } catch (err) {}
  window.setInterval(hatao, 700);
  return window.__srPopupKilled || 0;"""

# Ek jhatke me abhi hata do (pehredaar ke alawa). Kisi bhi nazuk kadam se
# pehle -- khaas kar 'Create account' dabane se pehle -- ye chalaya jaata hai,
# taaki click parde par na chala jaye.
POPUP_KILL_JS = """
  let n = 0;
  const PARDA = 'iframe#headless-iframe-login,'
              + 'iframe[src*="popupType=shiprocketLogin"],'
              + 'iframe[src*="fastrr-boost-ui"]';
  document.querySelectorAll(PARDA).forEach(f => {
    try { f.remove(); n++; } catch (err) {}
  });
  document.querySelectorAll('[class*="ShiprocketLogin_close"]').forEach(e => {
    if (e.getClientRects().length) { try { e.click(); n++; } catch (err) {} }
  });
  if (document.body && document.body.style.overflow === 'hidden') {
    document.body.style.overflow = '';
  }
  window.__srPopupKilled = (window.__srPopupKilled || 0) + n;
  return n;"""

# register form ke khaane -- ye id sthir hain (jaanch kar liye gaye)
F_FIRST = 'John"customer[first_name]"]'
F_LAST = 'Doe"customer[last_name]"]'
F_EMAIL = 'test@example.com"customer[email]"]'
F_PASS = 'input#create_password, input[name="customer[password]"]'
F_SUBMIT = ('input[type="submit"][value="Create account"], '
            'input.submit-button[type="submit"]')
REGISTER_LINK = 'a#customer_register_link'


def log(*a):
    print(*a, flush=True)


def arm_popup_guard(page, kaun=""):
    """Panne me popup ka pehredaar bitha do.

    Har navigation ke baad dobara bithana padta hai -- naya panna, naya
    JavaScript sansaar; purana observer wahin mit jaata hai.
    """
    try:
        page.evaluate(POPUP_ARM_JS)
        return True
    except Exception as e:
        log("      popup guard nahi laga%s: %s"
            % ((" (%s)" % kaun) if kaun else "", str(e)[:60]))
        return False


def close_popup(page, kaun=""):
    """Parda abhi ke abhi hata do (aur bata do ki hataya)."""
    try:
        n = page.evaluate(POPUP_KILL_JS) or 0
    except Exception:
        return 0
    if n:
        log("      popup ka parda hata diya%s"
            % ((" (%s)" % kaun) if kaun else ""))
        page.wait_for_timeout(500)
    return n


def customer_id(page):
    """Shopify ka apna customer id -- login ka pakka saboot."""
    try:
        return page.evaluate(
            "return (window.__st && window.__st.cid) ? String(window.__st.cid) : '';"
        ) or ""
    except Exception:
        return ""


def form_taiyaar(page):
    """Chaaron khaane sach me dikh rahe hain?

    Sirf `#email` dekh kar aage badh jaana galti thi: register ka panna abhi
    ban hi raha hota hai aur email pehle aa jaata hai, first/last naam baad me.
    Us beech me bhar diya to naam ke khaane 'nahi mile' aur account adhoora reh
    gaya. Isliye ab chaaron ka intezaar hota hai.
    """
    try:
        return bool(page.evaluate("""
          const ids = ['first_name', 'last_name', 'email', 'create_password'];
          return ids.every(id => {
            const e = document.getElementById(id);
            if (!e) return false;
            const r = e.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
          });"""))
    except Exception:
        return False


def open_register(page):
    """Register ka panna kholo aur form ke poora aane tak ruko.

    Pehle ye login panne se hokar 'New Customer?' dabata tha. Wo kaam to karta
    hai (jaanch me link asli navigation nikla, koi toggle nahi), par usme do
    panne khulte hain -- yaani popup ke aane ke do mauke, aur ek click jo parde
    par chala ja sakta hai. Seedha /account/register par jaane se wahi form,
    theek waisa hi, ek hi panne me mil jaata hai. Isliye ab seedha wahi.

    Login wala raasta phir bhi rakha hai -- agar kabhi seedha panna na khule.
    """
    page.goto(REGISTER_URL, timeout=120)
    page.wait_for_timeout(3000)
    arm_popup_guard(page, "register panna")

    for _ in range(12):
        close_popup(page)
        if form_taiyaar(page):
            return True
        page.wait_for_timeout(1500)

    # aakhri sahara: login panne se hokar
    log("      register ka form seedha nahi aaya -- login panne se koshish")
    page.goto(LOGIN_URL, timeout=120)
    page.wait_for_timeout(3000)
    arm_popup_guard(page, "login panna")
    page.wait_for_timeout(2000)

    el = None
    for _ in range(8):
        close_popup(page)
        el = page.visible_first(REGISTER_LINK)
        if el is not None:
            break
        page.wait_for_timeout(1500)
    if el is None:
        log("      'New Customer?' bhi nahi mila")
        return False

    how = po.scroll_click(page, el)
    log("      'New Customer?' daba diya (%s)" % (how or "nahi daba"))
    page.wait_for_timeout(3000)
    arm_popup_guard(page, "register panna")

    for _ in range(12):
        close_popup(page)
        if form_taiyaar(page):
            return True
        page.wait_for_timeout(1500)
    return False


def _put(page, sels, value, label):
    """Ek khaana bharo. Bharne se pehle popup hata do -- wahi sabse aam wajah
    hai jisse click doosri jagah chala jaata hai."""
    close_popup(page)
    el = page.visible_first(sels)
    if el is None:
        log("      %s: khaana nahi mila" % label)
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
    po.el_fill(page, el, "")
    po.el_type(page, el, value, delay=45)
    time.sleep(0.2)
    got = po.el_value(el)
    ok = got.strip() == str(value).strip()
    log("      %s -> %s%s"
        % (label, value, "" if ok else "  (CHETAVNI: '%s' bharaa)" % got))
    return ok


def tick_terms(page):
    """Terms wala checkbox tick karo.

    Ye dikhne me maamuli kadam hai par isi par sab atakta hai. Checkbox par
    `required` laga hai: bina tick kiye Create account dabane par browser KHUD
    form rok deta hai -- panna wahin khada rehta hai, koi error text DOM me
    aata hi nahi, aur bahar se ye "pata nahi kya hua" jaisa dikhta hai.

    Isliye panne ka 'pehla checkbox' uthana kaafi nahi -- header, newsletter
    ya popup ka koi aur checkbox pehle aa sakta hai. Dhoondhne ka kram:
        1) register form ke andar ka `required` wala checkbox
        2) register form ke andar ka pehla checkbox
        3) (aakhri sahara) poore panne ka pehla checkbox
    """
    close_popup(page)
    try:
        got = page.evaluate("""
          const dikhta = e => e.getClientRects().length > 0;
          const form = document.querySelector('#create_password')
                     ? document.querySelector('#create_password').form
                     : null;
          const jagah = form || document;
          let b = [...jagah.querySelectorAll('input[type=checkbox][required]')]
                  .filter(dikhta)[0];
          let kahan = 'form ka required';
          if (!b) {
            b = [...jagah.querySelectorAll('input[type=checkbox]')].filter(dikhta)[0];
            kahan = form ? 'form ka pehla' : 'panne ka pehla';
          }
          if (!b) {
            b = [...document.querySelectorAll('input[type=checkbox]')]
                .filter(dikhta)[0];
            kahan = 'panne ka pehla (aakhri sahara)';
          }
          if (!b) return 'nahi-mila|-';
          if (!b.checked) { b.click(); }
          if (!b.checked) {                       // label par click chahiye ho
            const lab = b.closest('label') ||
                        (b.id ? document.querySelector('label[for="' + b.id + '"]') : null);
            if (lab) lab.click();
          }
          return (b.checked ? 'tick' : 'tick-nahi-hua') + '|' + kahan;""")
    except Exception as e:
        log("      checkbox: %s" % str(e)[:60])
        return False
    haal, kahan = (got.split("|", 1) + ["-"])[:2]
    log("      terms checkbox -> %s  (%s)" % (haal, kahan))
    return haal == "tick"


def form_ki_shikayat(page):
    """Browser ne khud form roka ho to uski shikayat lauta do.

    HTML5 validation ka sandesh DOM me nahi hota -- sirf validationMessage me
    milta hai. Yahi wo cheez hai jo 'kuch pata nahi chala' wali fail ko saaf
    kar deti hai.
    """
    try:
        return (page.evaluate("""
          const el = document.querySelector('#create_password');
          const form = el ? el.form : null;
          if (!form) return '';
          const bure = [...form.elements].filter(e => e.willValidate && !e.checkValidity());
          return bure.map(e => (e.name || e.id || e.type) + ': ' + e.validationMessage)
                     .slice(0, 3).join(' | ');""") or "").strip()
    except Exception:
        return ""


def page_error(page):
    """Form ne koi galti batayi ho to wo text lauta do."""
    try:
        return (page.evaluate("""
          const bits = [...document.querySelectorAll(
              '.errors, .form-message, .form-message--error, [class*="error"]')]
            .map(e => (e.innerText || '').trim())
            .filter(t => t && t.length < 300);
          return bits.slice(0, 3).join(' | ');""") or "").strip()
    except Exception:
        return ""


def create_account(page, row):
    """Form bharo aur Create account dabao. (ok, note, customer_id)"""
    if not open_register(page):
        return False, "register ka form nahi khula", ""

    ok = True
    ok &= _put(page, F_FIRST, row["first"], "First name")
    ok &= _put(page, F_LAST, row["last"], "Last name")
    ok &= _put(page, F_EMAIL, row["email"], "Email")
    ok &= _put(page, F_PASS, row["password"], "Password")
    tick_terms(page)

    # Sabse nazuk kadam. Parda hataye bina click usi parde par chala jaata hai
    # aur bahar se lagta hai ki button daba par kuch hua hi nahi.
    close_popup(page, "submit se pehle")
    page.wait_for_timeout(500)
    btn = page.visible_first(F_SUBMIT)
    if btn is None:
        return False, "'Create account' ka button nahi mila", ""

    # Pehle asli mouse click -- aadmi jaisa, aur isse khaanon ka blur/change
    # bhi theek se chalta hai.
    how = po.scroll_click(page, btn)
    log("      Create account daba diya (%s)" % (how or "nahi daba"))

    # ...par is theme par sirf click se form chalta NAHI. Jaanch me saaf hua:
    # mouse click ke baad panna /account/register par hi khada rehta hai (koi
    # error nahi, khaane bhare ke bhare), jabki browser ka apna requestSubmit
    # chalate hi account ban jaata hai. Panne par baithi koi cheez (ek
    # __uc_iframe bhi hai) click ko kha jaati hai. reCAPTCHA yahan hai hi nahi
    # -- jaanch me grecaptcha=undefined mila -- isliye ye koi bot-rok nahi,
    # bas theme ka bartaav hai.
    # Isliye: click ke baad thoda dekho, kuch na ho to form ko khud bhejo.
    for _ in range(3):
        page.wait_for_timeout(2000)
        if customer_id(page) or "/register" not in (page.url or ""):
            break
    else:
        bheja = page.evaluate("""
          const f = document.getElementById('create_password');
          const form = f ? f.form : null;
          if (!form) return 'form nahi mila';
          const b = form.querySelector('input[type=submit]');
          try {
            if (form.requestSubmit) { form.requestSubmit(b || undefined);
                                      return 'requestSubmit'; }
            form.submit(); return 'submit()';
          } catch (e) { return 'gadbad: ' + e; }""")
        log("      click se kuch nahi hua -- form khud bheja (%s)" % bheja)

    # Shopify naya customer banate hi login kar deta hai aur /account par
    # bhej deta hai. Kabhi ye 3-4 second leta hai, isliye thoda intezaar.
    cid = ""
    for _ in range(12):
        page.wait_for_timeout(2500)
        # Submit ke baad panna badal jaata hai aur pehredaar wahin mit jaata
        # hai -- naye panne par use dobara bithana padta hai.
        arm_popup_guard(page)
        close_popup(page)
        cid = customer_id(page)
        if cid:
            break

    if cid:
        return True, "", cid

    # Yahan tak aana matlab account bana nahi. Sirf "customerId nahi mila"
    # likh dena kaafi nahi -- har fail sheet ki ek row hamesha ke liye kharch
    # kar deta hai, isliye wajah abhi ke abhi pakadni hai.
    galti = page_error(page)
    shikayat = form_ki_shikayat(page)
    try:
        url = (page.url or "")[:120]
    except Exception:
        url = "?"
    log("      fail ka haal -- URL: %s" % url)
    if shikayat:
        log("      browser ne form roka: %s" % shikayat)
    if galti:
        log("      panne par galti: %s" % galti[:200])
    try:
        thoda = " / ".join(
            l.strip() for l in (page.body_text() or "").splitlines() if l.strip())
        log("      panne par: %s" % thoda[:220])
    except Exception:
        pass
    try:
        shot = os.path.join(po.OUT, "reg_fail_%d.png" % int(time.time()))
        page.screenshot(shot)
        log("      tasveer: %s" % os.path.basename(shot))
    except Exception:
        pass

    wajah = shikayat or galti or "customerId nahi mila (account bana nahi)"
    return False, wajah[:200], ""


def save_the_session(driver, row, cid):
    """Cookies sessions/ me likh do. Faayda tabhi hai jab account sach me bana
    ho, isliye ye sirf safal hone par bulaya jaata hai."""
    local = re.sub(r"[^a-z0-9]+", "", (row["email"].split("@")[0] or "acct").lower())
    name = "estuary_%s_%d.json" % (local[:24], int(time.time()))
    d = {
        "email": row["email"],
        "password": row["password"],
        "first_name": row["first"],
        "last_name": row["last"],
        "phone": "9999999999",
        "customer_id": cid,
        "how": "email-signup",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "state": {"cookies": [], "origins": []},
    }
    path = os.path.join(SESSIONS, name)
    if po.save_session(driver, d, path):
        return name
    return ""


def one_account(row, proxy_port):
    """Ek row -> ek account. {ok, note, cid, session}"""
    driver = None
    out = {"ok": False, "note": "", "cid": "", "session": ""}
    try:
        driver = po.launch_waterfox(proxy_port=proxy_port, headless=False)
        page = po.Scope(driver, driver.current_window_handle)
        ok, note, cid = create_account(page, row)
        out["note"], out["cid"] = note, cid
        if not ok:
            log("      NAHI BANA: %s" % (note or "wajah saaf nahi"))
            return out

        log("      BAN GAYA: customerId=%s" % cid)
        sess = save_the_session(driver, row, cid)
        if not sess:
            # session ke bina account kisi kaam ka nahi -- order lagane ke waqt
            # phir se login karna padega. Isliye ise poora hua nahi maanenge.
            out["note"] = "account bana par session save nahi hui"
            log("      %s" % out["note"])
            return out
        out["ok"] = True
        out["session"] = sess
        return out
    except Exception as e:
        out["note"] = ("%s: %s" % (type(e).__name__, e))[:200]
        log("      gadbad: %s" % out["note"])
        return out
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


def run_batch(count, proxy_port=None, ws=None, gap=6, dry=False,
              log=log, should_stop=None, on_progress=None):
    """Ek ke baad ek account banao.

    log / should_stop / on_progress isliye hain ki yahi function seedha GUI se
    bhi chalta hai. GUI apna log dega (jo window me dikhta hai), Roko ka
    button `should_stop` se poochha jaata hai, aur pattee (progress bar)
    `on_progress` se aage badhti hai. Command line par ye teeno apne aap
    default par chalte hain, isliye purana command jaisa tha waisa hi rehta hai.
    """
    baaki = sheet_emails.pending(ws, limit=count)
    if not baaki:
        log("sheet me koi khaali row nahi bachi -- sab use ho chuki hain")
        return 0, 0

    log("sheet se %d row uthai (maange gaye %d)" % (len(baaki), count))
    bane = fail = 0
    kul = len(baaki)
    for i, row in enumerate(baaki, 1):
        if should_stop is not None and should_stop():
            log("")
            log("[STOP] rok diya gaya -- %d ban chuke the" % bane)
            break

        log("")
        log("===== %d/%d  row %d  %s %s  <%s> ====="
            % (i, kul, row["row"], row["first"], row["last"], row["email"]))
        if dry:
            log("      (--dry: sirf dikhaya, banaya nahi)")
            continue

        # pehle row apne naam kar lo, phir kaam -- taaki beech me kuch bhi ho
        # jaye to ye row dobara na uthe
        sheet_emails.claim(ws, row["row"])

        res = one_account(row, proxy_port)
        if res["ok"]:
            bane += 1
            sheet_emails.mark(ws, row["row"], sheet_emails.DONE,
                              res["session"], res["cid"], "")
            log("      [sheet] row %d -> complete" % row["row"])
        else:
            fail += 1
            sheet_emails.mark(ws, row["row"], sheet_emails.FAIL,
                              "", res["cid"], res["note"])
            log("      [sheet] row %d -> failed" % row["row"])

        if on_progress is not None:
            try:
                on_progress(bane, fail, kul)
            except Exception:
                pass

        if i < kul:
            # ek-ek second so kar, taaki Roko turant lage
            for _ in range(max(0, int(gap))):
                if should_stop is not None and should_stop():
                    break
                time.sleep(1)
    return bane, fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1,
                    help="kitne account banane hain")
    ap.add_argument("--tab", default=sheet_emails.TAB)
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument("--proxy-country", default=po.GEONODE_COUNTRY)
    ap.add_argument("--gap", type=int, default=6,
                    help="do account ke beech kitne second")
    ap.add_argument("--list", action="store_true",
                    help="sirf batao kaun si rows baaki hain")
    ap.add_argument("--dry", action="store_true",
                    help="rows uthao par browser mat kholo")
    a = ap.parse_args()

    ws, kahani = sheet_emails.open_tab(tab=a.tab)
    log("sheet : tab '%s' -> %s" % (a.tab, kahani))
    if ws is None:
        return 1

    if a.list:
        baaki = sheet_emails.pending(ws)
        log("baaki rows: %d" % len(baaki))
        for r in baaki[:20]:
            log("   row %-4d %-12s %-12s %s"
                % (r["row"], r["first"], r["last"], r["email"]))
        return 0

    port = None
    stop_bridge = None
    if not a.no_proxy:
        user = po.geonode_username(a.proxy_country, sticky=False)
        try:
            port, stop_bridge = po.start_geonode_bridge(user)
            log("proxy : Geonode %s | bridge 127.0.0.1:%d" % (a.proxy_country, port))
        except Exception as e:
            log("proxy : shuru nahi hui (%s) -- bina proxy chalenge" % str(e)[:80])
    else:
        log("proxy : OFF")

    bane = fail = 0
    try:
        bane, fail = run_batch(a.count, proxy_port=port, ws=ws, gap=a.gap,
                               dry=a.dry)
    except KeyboardInterrupt:
        log("\n(rok diya gaya)")
    except Exception:
        log("\nGADBAD:")
        for l in traceback.format_exc().splitlines()[-8:]:
            log("   " + l)
    finally:
        if stop_bridge is not None:
            stop_bridge.set()

    log("")
    log("================ hisaab ================")
    log("   maange gaye : %d" % a.count)
    log("   ban gaye    : %d" % bane)
    log("   fail        : %d" % fail)
    log("   sessions    : %s" % SESSIONS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
