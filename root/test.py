"""
Paisabazaar — Credit Card + Insurance Scraper (v2.2)
=====================================================

Verticals supported:
1. credit_card  — Cashback / Rewards / Travel / Premium / ...
2. insurance    — Health / Life / Vehicle / Other (Travel/Home/Accident)

Credit Card fields:
    title, slug, bank_name, category, category_type, supported_category_types,
    description, features, benefits, eligibility_criteria,
    joining_fee, annual_fee, image, image_url, card_url

Insurance fields:
    title, slug, bank_name (insurer), category, category_type,
    insurance_parent, supported_category_types, description,
    coverage, premium, eligibility, benefits_features, benefits,
    image, image_url, insurance_url

-----------------------------------------------------------------
WHY v2.2 CHANGED THE INSURANCE APPROACH (important — read this)
-----------------------------------------------------------------
v2.1 tried to treat insurance like credit cards: go to a "listing" page
(e.g. best-term-insurance-plans-india/) and scrape insurer-card blocks
out of it. This DOES NOT WORK on Paisabazaar for insurance because:

  1. Those "best-*-plans" pages are JS-hydrated (Next.js) article pages.
     Their static/SSR HTML only contains nav/header text — the actual
     insurer comparison cards are injected client-side in a way that
     isn't reliably scrapable, and even when rendered, they mostly link
     out to insurer-detail pages with NO consistent URL pattern.

  2. Real per-insurer detail pages exist and ARE scrapable (server-rendered,
     full of actual plan/benefit/eligibility content) — but their slugs are
     NOT predictable by regex. Examples (verified):
         /sbi-term-insurance-major-plans-benefits/
         /max-life-term-plans/
         /kotak-life-term-insurance-plans-check-compare-online/
         /aviva-life-term-insurance/
         /term-plans-3/                          (Bajaj Allianz!)
         /idbi-federal-term-insurance-plans/
         /term-insurance-plans/                  (Aegon Life!)
     No regex can derive these from a listing page — they have to be
     hand-verified once and hardcoded, exactly like the credit_card
     CATALOG already hardcodes category listing URLs.

SO: insurance sub-types now carry an explicit "insurer_urls" list — each
URL IS a final insurer/plan detail page. The scraper goes straight to each
one (no listing-extraction step), scrapes its sections, and lets the AI
enrich + the page <title>/<h1> determine the insurer name (instead of
guessing it from the URL slug, which is unreliable — e.g. "term-plans-3"
tells you nothing).

If you want to add more insurers/plans later, just add more verified URLs
to that sub-type's "insurer_urls" list.

NOTE: Sirf publicly-visible data scrape hota hai — koi login/OTP nahi.
"""

import os
import re
import sys
import json
import asyncio
import argparse
import aiohttp
from playwright.async_api import async_playwright

# Windows console UTF-8 force
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# =========================================================
# CONFIG
# =========================================================
BASE_URL      = "https://www.paisabazaar.com"
IMAGE_DIR     = "media/images"
OUTPUT_FILE   = "paisabazaar_data.json"

CATEGORY       = "insurance"        # "credit_card" ya "insurance"
RUN_TYPES      = ["Term Insurance"]
LIMIT_PER_TYPE = 3

HEADLESS      = True
DEBUG         = True
PAGE_TIMEOUT  = 90000
SCRAPE_DETAIL = True

os.makedirs(IMAGE_DIR, exist_ok=True)

def dprint(*args):
    if DEBUG:
        print("   [debug]", *args)

# =========================================================
# CATALOG
# =========================================================
CATALOG = {
    # ------------------------------------------------------------------
    # VERTICAL 1 — Credit Cards
    # (unchanged — listing-page scrape works fine for credit cards)
    # ------------------------------------------------------------------
    "credit_card": {
        "Cashback Cards":        f"{BASE_URL}/credit-card/best-cashback-credit-cards-india/",
        "Rewards Cards":         f"{BASE_URL}/credit-card/5-best-rewards-credit-cards/",
        "Travel Credit Cards":   f"{BASE_URL}/credit-card/travel-credit-cards/",
        "Shopping Credit Cards": [
            f"{BASE_URL}/credit-card/best-shopping-credit-cards-india/",
            f"{BASE_URL}/credit-card/best-online-shopping-credit-cards/",
        ],
        "Fuel Credit Cards":     f"{BASE_URL}/credit-card/best-fuel-credit-cards/",
        "Dining Credit Cards":   f"{BASE_URL}/credit-card/best-dining-credit-cards-india/",
        "Premium Credit Cards":  [
            f"{BASE_URL}/credit-card/best-premium-credit-cards-india/",
            f"{BASE_URL}/credit-card/best-super-premium-credit-cards-india/",
        ],
        "Lifetime Free Cards":   f"{BASE_URL}/credit-card/best-lifetime-free-credit-cards-in-india/",
        "Business Credit Cards": f"{BASE_URL}/credit-card/best-business-credit-cards-india/",
        "Co-branded Cards":      f"{BASE_URL}/credit-card/co-branded-credit-cards/",
    },

    # ------------------------------------------------------------------
    # VERTICAL 2 — Insurance
    # Each sub-type now carries hardcoded, hand-verified INSURER URLs
    # (final detail pages) instead of a "listing page to scrape".
    # ------------------------------------------------------------------
    "insurance": {

        # ---------------- Life Insurance : Term Insurance ----------------
        # Verified live (search + fetch) on 27-Jun-2026.
        "Term Insurance": {
            "insurer_urls": [
                f"{BASE_URL}/sbi-term-insurance-major-plans-benefits/",
                f"{BASE_URL}/max-life-term-plans/",
                f"{BASE_URL}/kotak-life-term-insurance-plans-check-compare-online/",
                f"{BASE_URL}/aviva-life-term-insurance/",
                f"{BASE_URL}/term-plans-3/",                      # Bajaj Allianz
                f"{BASE_URL}/idbi-federal-term-insurance-plans/",
                f"{BASE_URL}/term-insurance-plans/",              # Aegon Life
            ],
        },

        # ---------------- everything below: NOT yet hand-verified ----------------
        # These still use the OLD listing-page approach as a best-effort
        # fallback (kept so the script doesn't crash on other types), but
        # per the same root-cause analysis as Term Insurance, they will
        # likely return few/no records until someone verifies real
        # insurer URLs the same way and fills "insurer_urls" in.
        # TODO: repeat the verification process done for Term Insurance.

        "Individual Health Insurance": {
            "listing_urls": [
                f"{BASE_URL}/health-insurance/",
                f"{BASE_URL}/health-insurance/best-health-insurance-plans/",
            ],
        },
        "Family Health Insurance": {
            "listing_urls": [
                f"{BASE_URL}/health-insurance/family-health-insurance-plans/",
                f"{BASE_URL}/health-insurance/",
            ],
        },
        "Senior Citizen Insurance": {
            "listing_urls": [
                f"{BASE_URL}/health-insurance/senior-citizen-health-insurance/",
                f"{BASE_URL}/health-insurance/",
            ],
        },
        "Critical Illness Insurance": {
            "listing_urls": [
                f"{BASE_URL}/health-insurance/critical-illness-insurance/",
                f"{BASE_URL}/health-insurance/",
            ],
        },
        "Whole Life Insurance": {
            "listing_urls": [
                f"{BASE_URL}/life-insurance/whole-life-insurance-policy/",
                f"{BASE_URL}/life-insurance/",
            ],
        },
        "Investment + Insurance Plans": {
            "listing_urls": [f"{BASE_URL}/life-insurance/"],
        },
        "Car Insurance": {
            "listing_urls": [
                f"{BASE_URL}/motor-insurance/car-insurance/",
                f"{BASE_URL}/motor-insurance/",
            ],
        },
        "Bike Insurance": {
            "listing_urls": [
                f"{BASE_URL}/motor-insurance/two-wheeler-insurance/",
                f"{BASE_URL}/motor-insurance/",
            ],
        },
        "Travel Insurance": {
            "listing_urls": [f"{BASE_URL}/travel-insurance/"],
        },
        "Home Insurance": {
            "listing_urls": [
                f"{BASE_URL}/home-insurance/",
                f"{BASE_URL}/insurance/",
            ],
        },
        "Personal Accident Insurance": {
            "listing_urls": [
                f"{BASE_URL}/personal-accident-insurance/",
                f"{BASE_URL}/insurance/",
            ],
        },
    },
}

# Insurance parent grouping (for frontend display)
INSURANCE_PARENT_MAP = {
    "Individual Health Insurance":  "Health Insurance",
    "Family Health Insurance":      "Health Insurance",
    "Senior Citizen Insurance":     "Health Insurance",
    "Critical Illness Insurance":   "Health Insurance",
    "Term Insurance":               "Life Insurance",
    "Whole Life Insurance":         "Life Insurance",
    "Investment + Insurance Plans": "Life Insurance",
    "Car Insurance":                "Vehicle Insurance",
    "Bike Insurance":               "Vehicle Insurance",
    "Travel Insurance":             "Other Insurance",
    "Home Insurance":               "Other Insurance",
    "Personal Accident Insurance":  "Other Insurance",
}

def build_targets(category, run_types):
    """
    For credit_card: target['urls'] is a list of *listing* pages to try.
    For insurance:
        - if sub-type has 'insurer_urls'  -> target['mode']='insurer_urls', target['urls']=that list
        - else (legacy) 'listing_urls'    -> target['mode']='listing',      target['urls']=that list
    """
    sub_catalog = CATALOG.get(category)
    if not sub_catalog:
        print(f"❌ CATEGORY '{category}' CATALOG me nahi. Valid: {', '.join(CATALOG)}")
        return []
    if not run_types or any(str(t).lower() == "all" for t in run_types):
        chosen = list(sub_catalog.keys())
    else:
        chosen = []
        for t in run_types:
            key = next((k for k in sub_catalog if k.lower() == str(t).lower().strip()), None)
            if key:
                chosen.append(key)
            else:
                print(f"ℹ️  '{t}' '{category}' me nahi. Valid: {', '.join(sub_catalog)}")

    targets = []
    for ctype in chosen:
        val = sub_catalog[ctype]

        if category == "credit_card":
            urls = val if isinstance(val, list) else [val]
            targets.append({
                "category":      category,
                "category_type": ctype,
                "mode":          "listing",
                "url":           urls[0],
                "urls":          urls,
            })
            continue

        # category == "insurance"
        if isinstance(val, dict) and val.get("insurer_urls"):
            urls = val["insurer_urls"]
            targets.append({
                "category":      category,
                "category_type": ctype,
                "mode":          "insurer_urls",
                "url":           urls[0],
                "urls":          urls,
            })
        elif isinstance(val, dict) and val.get("listing_urls"):
            urls = val["listing_urls"]
            targets.append({
                "category":      category,
                "category_type": ctype,
                "mode":          "listing",
                "url":           urls[0],
                "urls":          urls,
            })
        else:
            # backward-compat: plain list/str value
            urls = val if isinstance(val, list) else [val]
            targets.append({
                "category":      category,
                "category_type": ctype,
                "mode":          "listing",
                "url":           urls[0],
                "urls":          urls,
            })

    return targets

# =========================================================
# HELPERS
# =========================================================
def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()

def safe_filename(name):
    name = re.sub(r"[^a-zA-Z0-9]", "_", str(name))
    name = re.sub(r"_+", "_", name).strip("_")
    return name[:80] or "item"

def _slug_from_url(url, fallback_name=""):
    try:
        seg = [s for s in url.split("?")[0].split("#")[0].split("/") if s]
        if seg:
            return seg[-1]
    except Exception:
        pass
    return re.sub(r"[^a-z0-9]+", "-", str(fallback_name).lower()).strip("-")

JUNK_IMAGE_HINTS = (
    "favicon", "logo", "sprite", "placeholder", "noimage", "loading",
    "searchicon", "arrow-", "chevron", "close.svg", "app-store",
    "play-store", "playstore", "appstore", "bank-logos", "download-app",
    "mobile-icon", "customer-support", "get-the-app",
)

async def goto_with_retry(page, url, retries=2, wait_after=5000):
    for attempt in range(retries + 1):
        try:
            resp = await page.goto(url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
            await page.wait_for_timeout(wait_after)
            return resp or True
        except Exception as e:
            if attempt < retries:
                print(f"   ↻ retry {attempt+1}/{retries} ({e.__class__.__name__})")
                await asyncio.sleep(2)
            else:
                print(f"   ⚠️ goto fail: {e}")
    return None

async def close_popups(page):
    for sel in [
        'button:has-text("Accept")', 'button:has-text("Got it")',
        'button[aria-label="Close"]', '.close-icon', '[data-dismiss="modal"]',
        'button:has-text("Close")', '.modal-close',
    ]:
        try:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible():
                await btn.click(timeout=2000)
                await asyncio.sleep(0.3)
        except Exception:
            pass
    try:
        await page.keyboard.press("Escape")
    except Exception:
        pass

async def scroll_full_page(page, step=700, max_height=12000):
    try:
        for y in range(0, max_height, step):
            await page.evaluate(f"window.scrollTo(0,{y})")
            await page.wait_for_timeout(200)
        await page.evaluate("window.scrollTo(0,0)")
        await page.wait_for_timeout(400)
    except Exception:
        pass

async def download_image(session, image_url, item_name, index):
    try:
        if not image_url or image_url.startswith("data:"):
            return None
        low = image_url.lower()
        if low.endswith(".svg") or low.endswith(".gif"):
            return None
        if any(x in low for x in JUNK_IMAGE_HINTS):
            return None
        ext = ".png"
        m   = re.search(r"\.(jpg|jpeg|png|webp|avif)", low)
        if m:
            ext = f".{m.group(1)}"
        filename = f"{safe_filename(item_name)}_{index}{ext}"
        filepath = os.path.join(IMAGE_DIR, filename)
        if os.path.exists(filepath):
            return f"/media/images/{filename}"
        async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status == 200:
                with open(filepath, "wb") as f:
                    f.write(await resp.read())
                return f"/media/images/{filename}"
    except Exception:
        pass
    return None

# =========================================================
# DETAIL — readable content + title/h1 (for insurer-name detection)
# =========================================================
async def extract_detail(page):
    return await page.evaluate(
        r"""
        () => {
            const main = document.querySelector('main') || document.body;
            const full = (main.innerText || '').replace(/[ \t]+/g, ' ').trim();
            const heads = [...main.querySelectorAll('h2,h3')]
                .map(h => (h.innerText || '').replace(/\s+/g, ' ').trim())
                .filter(Boolean);
            const h1 = (document.querySelector('h1')?.innerText || '').replace(/\s+/g, ' ').trim();
            const title = (document.title || '').replace(/\s+/g, ' ').trim();
            const firstImg = document.querySelector('main img, article img, img');
            let img = '';
            if (firstImg) {
                img = firstImg.getAttribute('src') || firstImg.getAttribute('data-src') || '';
                if (img.indexOf('/_next/image') !== -1) {
                    const m = img.match(/[?&]url=([^&]+)/);
                    if (m) img = decodeURIComponent(m[1]);
                }
                if (img.startsWith('/')) img = location.origin + img;
            }
            return { full, heads, h1, title, img };
        }
        """
    )

def _section(full, heads, *keys, limit=1500):
    target = None
    for h in heads:
        if any(k.lower() in h.lower() for k in keys):
            target = h
            break
    if not target:
        return ""
    i = full.find(target)
    if i < 0:
        return ""
    start = i + len(target)
    end   = start + limit
    ti    = heads.index(target)
    for h in heads[ti + 1:]:
        j = full.find(h, start)
        if j != -1:
            end = j
            break
    return clean_text(full[start:end])[:limit]

# =========================================================
# AI ENRICHMENT SETUP (GROQ)
# =========================================================
AI_ENRICH = True

CREDIT_CARD_TYPE_NAMES = list(CATALOG["credit_card"].keys())
INSURANCE_TYPE_NAMES   = list(CATALOG["insurance"].keys())

try:
    from dotenv import load_dotenv
    from groq import Groq
    load_dotenv()
    _GROQ_AVAILABLE = True
except Exception as _e:
    print(f"⚠️ Groq/dotenv import nahi hua, AI enrichment skip: {_e}")
    _GROQ_AVAILABLE = False

_groq_client = None
def get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("❌ GROQ_API_KEY missing in .env file")
        _groq_client = Groq(api_key=api_key)
        print("✅ Groq Client Initialized")
    return _groq_client

# =========================================================
# AI — CREDIT CARD
# =========================================================
CARD_AI_SYSTEM_PROMPT = (
    "You are a credit-card analyst for an Indian fintech website.\n\n"
    "STRICT RULES:\n"
    "- Return ONLY valid JSON. No markdown, no extra text.\n"
    "- Use ONLY the provided card data. Do not invent benefits or fees.\n"
    "- If a value is genuinely not present, use \"\" (or [] for lists).\n\n"
    "ALLOWED CATEGORY TYPES (use these EXACT strings):\n"
    f"{json.dumps(CREDIT_CARD_TYPE_NAMES)}\n\n"
    "FIELDS:\n"
    "- description: 3-4 sentence engaging overview of the card and who it suits.\n"
    "- supported_category_types: list of APPLICABLE types from the allowed list. 1-5 items.\n"
    "- features: 3-6 objects {\"heading\":..., \"content\":...} describing what the card offers.\n"
    "- benefits: list of short one-line perk strings.\n"
    "- eligibility_criteria: list of short one-line strings about WHO can apply.\n"
    "- joining_fee: short string e.g. \"₹500 + GST\", \"Nil\", \"Lifetime Free\".\n"
    "- annual_fee: short string (renewal fee). \"\" if unknown.\n\n"
    "OUTPUT FORMAT:\n"
    "{\n"
    '  "description": "...",\n'
    '  "supported_category_types": ["Cashback Cards"],\n'
    '  "features": [{"heading":"...","content":"..."}],\n'
    '  "benefits": ["..."],\n'
    '  "eligibility_criteria": ["Age: 21-60 years"],\n'
    '  "joining_fee": "₹500 + GST",\n'
    '  "annual_fee": "₹500 + GST"\n'
    "}"
)

def _empty_card_enrichment():
    return {
        "description": "", "supported_category_types": [], "features": [],
        "benefits": [], "eligibility_criteria": [], "joining_fee": "", "annual_fee": "",
    }

def _match_card_type(name):
    n = clean_text(name).lower()
    for t in CREDIT_CARD_TYPE_NAMES:
        if t.lower() == n:
            return t
    for t in CREDIT_CARD_TYPE_NAMES:
        key = t.lower().split(" cards")[0].split(" credit")[0]
        if key and key in n:
            return t
    return ""

def _normalize_card_enrichment(data):
    def _list_str(key):
        return [clean_text(x) for x in (data.get(key) or []) if clean_text(x)]
    sct = []
    for c in (data.get("supported_category_types") or []):
        m = _match_card_type(c)
        if m and m not in sct:
            sct.append(m)
    feats = []
    for f in (data.get("features") or data.get("key_features") or []):
        if isinstance(f, dict):
            h = clean_text(f.get("heading") or f.get("title"))
            c = clean_text(f.get("content") or f.get("description"))
            if h or c:
                feats.append({"heading": h, "content": c})
    return {
        "description":              clean_text(data.get("description") or data.get("summary")),
        "supported_category_types": sct,
        "features":                 feats[:6],
        "benefits":                 _list_str("benefits"),
        "eligibility_criteria":     _list_str("eligibility_criteria"),
        "joining_fee":              clean_text(data.get("joining_fee")),
        "annual_fee":               clean_text(data.get("annual_fee")),
    }

def enrich_card_with_ai(card):
    if not (AI_ENRICH and _GROQ_AVAILABLE):
        return _empty_card_enrichment()
    try:
        client = get_groq_client()
        sec = card.get("sections", {})
        raw = (
            f"Card Name: {card.get('name','')}\n"
            f"Bank: {card.get('bank','')}\n"
            f"Scraped under category type: {card.get('category_type','')}\n"
            f"Joining fee (listing): {card.get('joining_fee_raw','')}\n"
            f"Listing text: {card.get('listing_text','')}\n"
            f"-- About --\n{sec.get('about','')[:900]}\n"
            f"-- Rewards --\n{sec.get('rewards','')[:900]}\n"
            f"-- Features & Benefits --\n{sec.get('features','')[:1200]}\n"
            f"-- Fees & Charges --\n{sec.get('fees','')[:700]}\n"
            f"-- Get this card if --\n{sec.get('getif','')[:500]}\n"
            f"-- Eligibility Criteria --\n{sec.get('eligibility','')[:900]}\n"
        )
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=1800,
            messages=[
                {"role": "system", "content": CARD_AI_SYSTEM_PROMPT},
                {"role": "user",   "content": f"CREDIT CARD DATA:\n{raw}\n\nGenerate the JSON."},
            ],
        )
        text = resp.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return _normalize_card_enrichment(json.loads(text))
    except json.JSONDecodeError as e:
        print(f"⚠️ AI JSON parse error: {e}")
        return _empty_card_enrichment()
    except Exception as e:
        print(f"❌ AI enrichment error: {e}")
        return _empty_card_enrichment()

# =========================================================
# AI — INSURANCE
# =========================================================
INSURANCE_AI_SYSTEM_PROMPT = (
    "You are an insurance analyst for an Indian fintech website.\n\n"
    "STRICT RULES:\n"
    "- Return ONLY valid JSON. No markdown, no extra text.\n"
    "- Use ONLY the provided insurance plan data. Do not invent benefits or figures.\n"
    "- If a value is genuinely not present, use \"\" (or [] for lists).\n\n"
    "ALLOWED CATEGORY TYPES (use these EXACT strings):\n"
    f"{json.dumps(INSURANCE_TYPE_NAMES)}\n\n"
    "FIELDS:\n"
    "- title: clean, human-friendly plan/article title (e.g. \"SBI Life Term Insurance Plans\").\n"
    "  Clean up raw page titles — remove site-suffix junk like \"- Paisabazaar.com\", "
    "\"Check & Compare Online\" boilerplate, etc. Keep it natural and short.\n"
    "- insurer_name: the actual INSURANCE COMPANY name only (e.g. \"SBI Life\", \"Max Life\", "
    "\"Bajaj Allianz Life\", \"Aegon Life\", \"Kotak Life\", \"IDBI Federal Life\", \"Aviva Life\"). "
    "Never return a generic phrase like \"Term Insurance\" or \"Term Plans\" here — that is NOT "
    "an insurer name. If you truly cannot identify a real insurer/company name from the data, "
    "return \"\".\n"
    "- description: 3-4 sentence engaging overview of who this plan suits and why.\n"
    "- supported_category_types: list of APPLICABLE insurance types from the allowed list. 1-4 items.\n"
    "- coverage: list of short one-line strings describing what is covered.\n"
    "- premium: short string e.g. \"Starting ₹X/year for ₹5 lakh cover\", or \"\" if unknown.\n"
    "- eligibility: list of short one-line strings about WHO can buy "
    "(e.g. \"Age: 18-65 years\", \"Pre-existing diseases covered after 2-4 year waiting period\"). "
    "[] if absent.\n"
    "- benefits_features: 3-6 objects {\"heading\":..., \"content\":...} describing plan highlights.\n"
    "- benefits: list of short one-line perk strings.\n\n"
    "OUTPUT FORMAT:\n"
    "{\n"
    '  "title": "SBI Life Term Insurance Plans",\n'
    '  "insurer_name": "SBI Life",\n'
    '  "description": "...",\n'
    '  "supported_category_types": ["Term Insurance"],\n'
    '  "coverage": ["Hospitalisation up to sum insured"],\n'
    '  "premium": "Starting ₹5,000/year for ₹5 lakh cover",\n'
    '  "eligibility": ["Age: 18-65 years"],\n'
    '  "benefits_features": [{"heading":"...","content":"..."}],\n'
    '  "benefits": ["Cashless treatment at 10,000+ hospitals"]\n'
    "}"
)

def _empty_insurance_enrichment():
    return {
        "title": "", "insurer_name": "", "description": "", "supported_category_types": [],
        "coverage": [], "premium": "", "eligibility": [], "benefits_features": [], "benefits": [],
    }

def _match_insurance_type(name):
    n = clean_text(name).lower()
    for t in INSURANCE_TYPE_NAMES:
        if t.lower() == n:
            return t
    for t in INSURANCE_TYPE_NAMES:
        kw = t.lower().replace(" insurance", "").replace(" plans", "").strip()
        if kw and kw in n:
            return t
    return ""

# generic words that must NEVER be treated as an insurer name
_GENERIC_INSURER_BLOCKLIST = {
    "term insurance", "term plan", "term plans", "life insurance",
    "health insurance", "motor insurance", "car insurance",
    "bike insurance", "two wheeler insurance", "travel insurance",
    "home insurance", "personal accident insurance", "insurance",
    "best term insurance plans", "insurance plans",
}

def _is_generic_insurer_name(name):
    n = clean_text(name).lower().strip()
    if not n:
        return True
    if n in _GENERIC_INSURER_BLOCKLIST:
        return True
    # also catch things that are ONLY a category-type phrase
    for t in INSURANCE_TYPE_NAMES:
        if n == t.lower():
            return True
    return False

def _normalize_insurance_enrichment(data):
    def _list_str(key):
        return [clean_text(x) for x in (data.get(key) or []) if clean_text(x)]
    sct = []
    for c in (data.get("supported_category_types") or []):
        m = _match_insurance_type(c)
        if m and m not in sct:
            sct.append(m)
    feats = []
    for f in (data.get("benefits_features") or data.get("features") or []):
        if isinstance(f, dict):
            h = clean_text(f.get("heading") or f.get("title"))
            c = clean_text(f.get("content") or f.get("description"))
            if h or c:
                feats.append({"heading": h, "content": c})

    insurer_name = clean_text(data.get("insurer_name"))
    if _is_generic_insurer_name(insurer_name):
        insurer_name = ""  # let caller fall back to better source

    return {
        "title":                     clean_text(data.get("title")),
        "insurer_name":              insurer_name,
        "description":               clean_text(data.get("description") or data.get("summary")),
        "supported_category_types":  sct,
        "coverage":                  _list_str("coverage"),
        "premium":                   clean_text(data.get("premium")),
        "eligibility":               _list_str("eligibility"),
        "benefits_features":         feats[:6],
        "benefits":                  _list_str("benefits"),
    }

def enrich_insurance_with_ai(plan):
    if not (AI_ENRICH and _GROQ_AVAILABLE):
        return _empty_insurance_enrichment()
    try:
        client = get_groq_client()
        sec = plan.get("sections", {})
        raw = (
            f"Page Title: {plan.get('page_title','')}\n"
            f"Page H1: {plan.get('page_h1','')}\n"
            f"URL slug (often NOT a real insurer name — derive insurer from title/h1/content instead): "
            f"{plan.get('url_slug','')}\n"
            f"Scraped under category type: {plan.get('category_type','')}\n"
            f"-- About / Overview --\n{sec.get('about','')[:1000]}\n"
            f"-- Coverage / What is Covered --\n{sec.get('coverage','')[:1000]}\n"
            f"-- Benefits & Features --\n{sec.get('benefits','')[:1200]}\n"
            f"-- Premium / Fees --\n{sec.get('premium','')[:700]}\n"
            f"-- Eligibility / Who Can Buy --\n{sec.get('eligibility','')[:900]}\n"
            f"-- Exclusions --\n{sec.get('exclusions','')[:600]}\n"
        )
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=1800,
            messages=[
                {"role": "system", "content": INSURANCE_AI_SYSTEM_PROMPT},
                {"role": "user",   "content": f"INSURANCE PLAN DATA:\n{raw}\n\nGenerate the JSON."},
            ],
        )
        text = resp.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return _normalize_insurance_enrichment(json.loads(text))
    except json.JSONDecodeError as e:
        print(f"⚠️ AI JSON parse error: {e}")
        return _empty_insurance_enrichment()
    except Exception as e:
        print(f"❌ AI enrichment error: {e}")
        return _empty_insurance_enrichment()

# =========================================================
# INSURER-NAME FALLBACK (non-AI, regex based)
# =========================================================
# Common Indian life/health/general insurer brand names — used to detect
# the real insurer from page title/h1 text when AI enrichment is off or
# returns nothing usable. Extend this list as you add more insurer_urls.
KNOWN_INSURER_BRANDS = [
    "SBI Life", "HDFC Life", "ICICI Prudential", "Max Life", "Bajaj Allianz",
    "Kotak Life", "Aviva Life", "Aegon Life", "IDBI Federal", "Tata AIA",
    "PNB MetLife", "Canara HSBC", "Star Health", "HDFC ERGO", "ICICI Lombard",
    "Bajaj Allianz General", "Care Health", "Niva Bupa", "Max Bupa",
    "Reliance General", "Future Generali", "Bharti AXA", "Edelweiss Tokio",
    "Exide Life", "Shriram Life", "LIC",
]

# Short brand prefixes that often appear WITHOUT their full suffix in page
# headings (e.g. "SBI Term Insurance" instead of "SBI Life Term Insurance").
# Maps the short form -> canonical display name to return.
KNOWN_INSURER_SHORT_PREFIXES = {
    "sbi":    "SBI Life",
    "hdfc":   "HDFC Life",
    "icici":  "ICICI Prudential",
    "kotak":  "Kotak Life",
    "aviva":  "Aviva Life",
    "aegon":  "Aegon Life",
    "idbi":   "IDBI Federal",
    "tata":   "Tata AIA",
    "pnb":    "PNB MetLife",
    "canara": "Canara HSBC",
    "lic":    "LIC",
}

def _detect_insurer_from_text(*texts):
    blob = " ".join(t for t in texts if t)
    blob_low = blob.lower()
    # 1) full brand names first (more specific / reliable)
    for brand in KNOWN_INSURER_BRANDS:
        if brand.lower() in blob_low:
            return brand
    # 2) short prefixes as whole words (avoid matching inside other words)
    for prefix, canonical in KNOWN_INSURER_SHORT_PREFIXES.items():
        if re.search(rf"\b{re.escape(prefix)}\b", blob_low):
            return canonical
    return ""

def _clean_title_fallback(raw_title):
    t = clean_text(raw_title)
    # strip common site-suffix junk
    t = re.sub(r"\s*[-|]\s*Paisabazaar(\.com)?\s*$", "", t, flags=re.I)
    t = re.sub(r"\s*:\s*Check\s*&\s*Compare Online\s*$", "", t, flags=re.I)
    return t.strip() or raw_title

# =========================================================
# LISTING EXTRACTOR — Credit Card (unchanged, works fine)
# =========================================================
async def extract_cards_from_listing(page):
    return await page.evaluate(
        r"""
        () => {
            const txt = e => (e ? e.innerText : '').replace(/\s+/g, ' ').trim();
            const isDetail = h => {
                if (!h) return false;
                try {
                    const u = new URL(h);
                    if (!/paisabazaar\.com$/i.test(u.hostname)) return false;
                    const segs = u.pathname.split('/').filter(Boolean);
                    if (segs.length < 2) return false;
                    if (segs[0] === 'credit-card' || segs[0] === 'credit-cards') return false;
                    return /credit-card/i.test(segs[segs.length - 1]);
                } catch (e) { return false; }
            };
            const realImg = im => {
                if (!im) return '';
                let s = im.getAttribute('src') || im.getAttribute('data-src') || '';
                if (s.indexOf('/_next/image') !== -1) {
                    const m = s.match(/[?&]url=([^&]+)/);
                    if (m) s = decodeURIComponent(m[1]);
                }
                if (s.startsWith('/')) s = location.origin + s;
                return s;
            };
            const anchors = [...document.querySelectorAll('a[href]')].filter(a => isDetail(a.href));
            const out = [], seenNode = new Set(), seenUrl = new Set();
            anchors.forEach(a => {
                let node = a;
                while (node.parentElement) {
                    const p = node.parentElement;
                    const cnt = [...p.querySelectorAll('a[href]')].filter(x => isDetail(x.href)).length;
                    if (cnt !== 1) break;
                    node = p;
                }
                if (seenNode.has(node)) return;
                seenNode.add(node);
                const t = txt(node);
                if (!/joining fee/i.test(t)) return;
                const url = a.href.split('?')[0].split('#')[0];
                if (seenUrl.has(url)) return;
                seenUrl.add(url);
                const name = (node.querySelector('h2,h3,h4')?.innerText || a.innerText || '')
                    .replace(/\s+/g, ' ').trim();
                if (!name) return;
                const jm = t.match(/joining fee[:\s]*₹?\s*([\d,]+|nil|free|lifetime free|0)/i);
                const bm = url.match(/paisabazaar\.com\/([a-z0-9-]+)\//i);
                out.push({
                    name: name.slice(0, 120),
                    url,
                    bank: bm ? bm[1].replace(/-/g, ' ') : '',
                    joining_fee_raw: jm ? jm[0].replace(/\s+/g, ' ').trim() : '',
                    listing_text: t.slice(0, 600),
                    image: realImg(node.querySelector('img')),
                });
            });
            return out;
        }
        """
    )

# =========================================================
# LISTING EXTRACTOR — Insurance (legacy fallback only)
# =========================================================
# Kept ONLY as a best-effort fallback for sub-types that don't yet have
# verified insurer_urls (see CATALOG comment above). For Term Insurance
# and any other type with insurer_urls set, this function is NOT called —
# scrape_insurance_target() goes straight to the insurer_urls instead.
async def extract_insurance_from_listing(page):
    return await page.evaluate(
        r"""
        () => {
            const txt = e => (e ? e.innerText : '').replace(/\s+/g, ' ').trim();

            const INSURANCE_PATH_KEYWORDS = [
                'health-insurance', 'term-insurance', 'life-insurance',
                'motor-insurance', 'car-insurance', 'two-wheeler-insurance',
                'travel-insurance', 'home-insurance', 'personal-accident',
                'critical-illness', 'senior-citizen', 'family-health',
                'term-plans', 'term-plan', 'life-plan',
            ];
            const EXCLUDE_SLUGS = [
                'login', 'signup', 'register', 'credit-score', 'personal-loan',
                'home-loan', 'business-loan', 'cibil', 'mutual-fund',
                'insurance-premium-payment', 'term-insurance-premium-calculator',
                'life-insurance-premium-calculator', 'car-insurance-premium-calculator',
                'bike-insurance-premium-calculator', 'health-insurance-premium-calculator',
                'compare', 'blog', 'news',
            ];

            const isInsurancePage = href => {
                if (!href) return false;
                try {
                    const u = new URL(href);
                    if (!/paisabazaar\.com$/i.test(u.hostname)) return false;
                    const segs = u.pathname.split('/').filter(Boolean);
                    if (segs.length < 1) return false;
                    const pathLow = u.pathname.toLowerCase();
                    if (EXCLUDE_SLUGS.some(s => pathLow.includes(s))) return false;
                    const hasKeyword = INSURANCE_PATH_KEYWORDS.some(k => pathLow.includes(k));
                    if (hasKeyword) return true;
                    if (segs.length === 1) {
                        return /-insurance$|-plans$|-plan$|-term-plans$/.test(segs[0]);
                    }
                    return false;
                } catch { return false; }
            };

            const realImg = im => {
                if (!im) return '';
                let s = im.getAttribute('src') || im.getAttribute('data-src') || '';
                if (s.indexOf('/_next/image') !== -1) {
                    const m = s.match(/[?&]url=([^&]+)/);
                    if (m) s = decodeURIComponent(m[1]);
                }
                if (s.startsWith('/')) s = location.origin + s;
                return s;
            };

            const currentPath = location.pathname;
            const anchors = [...document.querySelectorAll('a[href]')].filter(a => isInsurancePage(a.href));
            const out = [], seenNode = new Set(), seenUrl = new Set();

            anchors.forEach(a => {
                try {
                    const u = new URL(a.href);
                    if (u.pathname === currentPath) return;
                } catch { return; }

                let node = a;
                while (node.parentElement) {
                    const p = node.parentElement;
                    const cnt = [...p.querySelectorAll('a[href]')].filter(x => isInsurancePage(x.href)).length;
                    if (cnt !== 1) break;
                    node = p;
                }
                if (seenNode.has(node)) return;
                seenNode.add(node);

                const url = a.href.split('?')[0].split('#')[0];
                if (seenUrl.has(url)) return;
                seenUrl.add(url);

                const t = txt(node);
                if (t.length < 10) return;

                let name = '';
                const hEl = node.querySelector('h2,h3,h4,h5,.plan-name,.card-title,.company-name,.insurer-name');
                if (hEl) name = txt(hEl);
                if (!name) name = txt(a);
                if (!name || name.length < 3) return;

                const segs = url.replace(/\/$/, '').split('/').filter(Boolean);
                const insurerSlug = segs[segs.length - 1] || '';
                const premMatch = t.match(/(?:premium|starting|price)[:\s]*₹?\s*([\d,]+)/i);

                out.push({
                    name:        name.slice(0, 140),
                    url,
                    insurer:     insurerSlug.replace(/-/g, ' '),
                    premium_raw: premMatch ? premMatch[0].replace(/\s+/g, ' ').trim() : '',
                    listing_text: t.slice(0, 600),
                    image:       realImg(node.querySelector('img')),
                });
            });

            return out;
        }
        """
    )

# =========================================================
# DETAIL SECTION SCRAPERS
# =========================================================

async def scrape_credit_card_detail_sections(context, url):
    page = await context.new_page()
    try:
        if not await goto_with_retry(page, url, wait_after=4000):
            return {}, {}
        await close_popups(page)
        try:
            await page.evaluate(
                "()=>{document.querySelectorAll('[aria-expanded=\"false\"]')"
                ".forEach(e=>{try{e.click()}catch(x){}})}",
            )
            await page.wait_for_timeout(500)
        except Exception:
            pass
        await scroll_full_page(page, max_height=14000)
        d    = await extract_detail(page)
        full = d.get("full", "")
        heads = d.get("heads", [])
        sections = {
            "about":       _section(full, heads, "About"),
            "rewards":     _section(full, heads, "Rewards Program", "Reward"),
            "features":    _section(full, heads, "Features and Benefits", "Other Features"),
            "fees":        _section(full, heads, "Fees and Charges", "Fees &"),
            "getif":       _section(full, heads, "Get this card if", "Things to Know"),
            "eligibility": _section(full, heads, "Eligibility Criteria", "Eligibility"),
        }
        return sections, d
    except Exception as e:
        dprint(f"card detail error: {e}")
        return {}, {}
    finally:
        await page.close()

async def scrape_insurance_detail_sections(context, url):
    """Returns (sections_dict, raw_detail_dict). raw_detail_dict has
    'h1', 'title', 'img' keys useful for insurer-name detection."""
    page = await context.new_page()
    try:
        if not await goto_with_retry(page, url, wait_after=4000):
            return {}, {}
        await close_popups(page)
        try:
            await page.evaluate(
                "()=>{[...document.querySelectorAll('[aria-expanded=\"false\"],"
                "details:not([open])')].forEach(e=>{try{e.click();}catch(x){}})}",
            )
            await page.wait_for_timeout(600)
        except Exception:
            pass
        await scroll_full_page(page, max_height=16000)
        d     = await extract_detail(page)
        full  = d.get("full", "")
        heads = d.get("heads", [])
        sections = {
            "about":       _section(full, heads, "About", "Overview", "Introduction"),
            "coverage":    _section(full, heads, "Coverage", "What is Covered", "Sum Insured",
                                    "What's Covered", "Inclusions"),
            "benefits":    _section(full, heads, "Benefits", "Features", "Key Features",
                                    "Plan Benefits", "Plan Features"),
            "premium":     _section(full, heads, "Premium", "Price", "Cost", "Charges"),
            "eligibility": _section(full, heads, "Eligibility", "Who Can Buy",
                                    "Entry Age", "Who Can Apply"),
            "exclusions":  _section(full, heads, "Exclusions", "What is Not Covered",
                                    "What's Not Covered"),
        }
        return sections, d
    except Exception as e:
        dprint(f"insurance detail error: {e}")
        return {}, {}
    finally:
        await page.close()

# =========================================================
# SCRAPE ONE TARGET — CREDIT CARD  (unchanged)
# =========================================================
async def scrape_credit_card_target(context, session, target, limit=None):
    name      = target["category_type"]
    urls_list = target.get("urls") or [target["url"]]
    print(f"\n{'='*65}")
    print(f"💳 CREDIT CARD / {name}")
    print(f"🎯 Limit    : {'ALL' if limit is None else limit}")

    page = await context.new_page()
    cards, used_url = [], None
    try:
        for ci, listing_url in enumerate(urls_list):
            tag = f"[try {ci+1}/{len(urls_list)}]" if len(urls_list) > 1 else ""
            print(f"🔗 URL      : {listing_url} {tag}")
            resp = await goto_with_retry(page, listing_url)
            if not resp:
                continue
            if resp is not True and getattr(resp, "status", 200) >= 400:
                dprint(f"   {listing_url} -> {resp.status}")
                continue
            await close_popups(page)
            await scroll_full_page(page)
            found = await extract_cards_from_listing(page)
            if found:
                cards    = found if limit is None else found[:limit]
                used_url = listing_url
                break
            else:
                print("   …is URL pe cards nahi mile")
    finally:
        await page.close()

    if not cards:
        print(f"⚠️ '{name}' pe koi card nahi mila — skip")
        return []

    print(f"💳 Scraping {len(cards)} cards  (URL: {used_url})\n")
    records = []
    for i, card in enumerate(cards):
        print(f"[{i+1}/{len(cards)}] {card['name'][:60]}...")
        sections = {}
        if SCRAPE_DETAIL:
            sections, _raw = await scrape_credit_card_detail_sections(context, card["url"])
            await asyncio.sleep(1)
        card["sections"]      = sections
        card["category_type"] = target["category_type"]
        enrich = await asyncio.to_thread(enrich_card_with_ai, card)
        image_local = None
        if card.get("image"):
            image_local = await download_image(session, card["image"], card["name"], 0)
        supported = list(enrich["supported_category_types"])
        if target["category_type"] not in supported:
            supported.insert(0, target["category_type"])
        eligibility = enrich["eligibility_criteria"]
        if not eligibility and sections.get("eligibility"):
            eligibility = [clean_text(sections["eligibility"])[:400]]
        record = {
            "title":                    card["name"],
            "slug":                     _slug_from_url(card["url"], card["name"]),
            "bank_name":                clean_text(card.get("bank", "")).title(),
            "category":                 target["category"],
            "category_type":            target["category_type"],
            "supported_category_types": supported,
            "description":              enrich["description"],
            "features":                 enrich["features"],
            "benefits":                 enrich["benefits"],
            "eligibility_criteria":     eligibility,
            "joining_fee":              enrich["joining_fee"] or clean_text(card.get("joining_fee_raw", "")),
            "annual_fee":               enrich["annual_fee"],
            "image":                    image_local or "",
            "image_url":                card.get("image", ""),
            "card_url":                 card["url"],
        }
        records.append(record)
        print(f"✅ Done | supports={supported} | elig={len(eligibility)} | feats={len(enrich['features'])}")
    return records

# =========================================================
# SCRAPE ONE TARGET — INSURANCE  (rewritten)
# =========================================================
async def scrape_insurance_target(context, session, target, limit=None):
    """
    mode == 'insurer_urls' (preferred path):
        target['urls'] is already a list of FINAL insurer/plan detail pages.
        We go straight to each one — no listing-page extraction needed.

    mode == 'listing' (legacy fallback for not-yet-verified sub-types):
        Old behaviour — try each listing URL, extract insurer blocks from it.
        Will likely yield few/no results until insurer_urls are added for
        that sub-type (see CATALOG TODO comment).
    """
    name   = target["category_type"]
    mode   = target.get("mode", "listing")
    parent = INSURANCE_PARENT_MAP.get(name, "Other Insurance")

    print(f"\n{'='*65}")
    print(f"🛡️  INSURANCE / {parent} / {name}  [mode={mode}]")
    print(f"🎯 Limit    : {'ALL' if limit is None else limit}")

    plans = []

    if mode == "insurer_urls":
        urls = target.get("urls") or []
        plans = [{"url": u, "from_listing": False} for u in (urls if limit is None else urls[:limit])]
        print(f"🔗 {len(plans)} verified insurer URL(s) queued directly (no listing scrape needed)")
    else:
        urls_list = target.get("urls") or [target["url"]]
        page = await context.new_page()
        used_url = None
        try:
            for ci, listing_url in enumerate(urls_list):
                tag = f"[try {ci+1}/{len(urls_list)}]" if len(urls_list) > 1 else ""
                print(f"🔗 URL      : {listing_url} {tag}")
                resp = await goto_with_retry(page, listing_url, wait_after=6000)
                if not resp:
                    continue
                status = getattr(resp, "status", 200) if resp is not True else 200
                if status >= 400:
                    dprint(f"   HTTP {status} — skip")
                    continue
                await close_popups(page)
                await scroll_full_page(page, max_height=14000)
                found = await extract_insurance_from_listing(page)
                dprint(f"   raw found: {len(found)} items")
                if found:
                    found    = found if limit is None else found[:limit]
                    used_url = listing_url
                    plans    = [{"url": f["url"], "from_listing": True, "listing_data": f} for f in found]
                    break
                else:
                    print("   …is URL pe insurance plans nahi mile")
        finally:
            await page.close()

        if not plans:
            print(f"⚠️ '{name}' pe koi plan nahi mila — skip "
                  f"(consider adding verified insurer_urls for this sub-type, "
                  f"like Term Insurance has)")
            return []

    print(f"🛡️  Scraping {len(plans)} insurer page(s)\n")
    records = []
    for i, plan_ref in enumerate(plans):
        url = plan_ref["url"]
        print(f"[{i+1}/{len(plans)}] {url}")

        sections, raw = await scrape_insurance_detail_sections(context, url)
        await asyncio.sleep(1)

        page_title = raw.get("title", "")
        page_h1    = raw.get("h1", "")
        page_img   = raw.get("img", "")
        url_slug   = _slug_from_url(url)

        listing_data = plan_ref.get("listing_data") or {}

        plan = {
            "url":            url,
            "url_slug":       url_slug,
            "page_title":     page_title,
            "page_h1":        page_h1,
            "sections":       sections,
            "category_type":  target["category_type"],
            "listing_text":   listing_data.get("listing_text", ""),
            "premium_raw":    listing_data.get("premium_raw", ""),
        }

        enrich = await asyncio.to_thread(enrich_insurance_with_ai, plan)

        # ---- Resolve insurer (bank_name) with layered fallback ----
        insurer_name = enrich.get("insurer_name") or ""
        if not insurer_name:
            insurer_name = _detect_insurer_from_text(page_h1, page_title, sections.get("about", ""))
        if not insurer_name and listing_data.get("insurer"):
            cand = clean_text(listing_data["insurer"]).title()
            if not _is_generic_insurer_name(cand):
                insurer_name = cand
        if not insurer_name:
            # last resort: still better than "Term Insurance" — use slug words,
            # but strip generic insurance words out of it first
            slug_words = url_slug.replace("-", " ")
            slug_words = re.sub(
                r"\b(term|insurance|plans?|major|check|compare|online|and|their|benefits|policies)\b",
                "", slug_words, flags=re.I,
            )
            insurer_name = clean_text(slug_words).title() or "Unknown Insurer"

        # ---- Resolve title ----
        title = enrich.get("title") or _clean_title_fallback(page_h1 or page_title) or insurer_name

        # ---- Resolve image ----
        image_remote = listing_data.get("image") or page_img or ""
        image_local = None
        if image_remote:
            image_local = await download_image(session, image_remote, insurer_name or title, 0)

        supported = list(enrich["supported_category_types"])
        if target["category_type"] not in supported:
            supported.insert(0, target["category_type"])

        eligibility = enrich["eligibility"]
        if not eligibility and sections.get("eligibility"):
            eligibility = [clean_text(sections["eligibility"])[:400]]

        coverage = enrich["coverage"]
        if not coverage and sections.get("coverage"):
            coverage = [clean_text(sections["coverage"])[:400]]

        record = {
            "title":                    title,
            "slug":                     url_slug,
            "bank_name":                insurer_name,
            "category":                 target["category"],
            "category_type":            target["category_type"],
            "insurance_parent":         parent,
            "supported_category_types": supported,
            "description":              enrich["description"],
            "coverage":                 coverage,
            "premium":                  enrich["premium"] or clean_text(plan.get("premium_raw", "")),
            "eligibility":              eligibility,
            "benefits_features":        enrich["benefits_features"],
            "benefits":                 enrich["benefits"],
            "image":                    image_local or "",
            "image_url":                image_remote,
            "insurance_url":            url,
        }
        records.append(record)
        print(
            f"✅ Done | insurer={insurer_name} | parent={parent} | supports={supported} | "
            f"coverage={len(coverage)} | feats={len(enrich['benefits_features'])}"
        )
    return records

# =========================================================
# ORCHESTRATOR
# =========================================================
def save_records(all_records):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

async def scrape_paisabazaar(category=None, run_types=None, limit_per_type=None, targets=None):
    category = category or CATEGORY
    if targets is None:
        targets = build_targets(category, run_types or RUN_TYPES)
    if not targets:
        print("❌ Koi valid sub-type nahi mila. CATEGORY / RUN_TYPES check karo.")
        return

    print("🚀 PAISABAZAAR SCRAPER STARTED...")
    print(f"📂 Category : {category}")
    print(f"📌 Sub-types: {len(targets)} | Limit/type: "
          f"{'ALL' if limit_per_type is None else limit_per_type}\n")

    all_records = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            ),
        )
        async with aiohttp.ClientSession() as session:
            for ti, target in enumerate(targets):
                print(f"\n########## [{ti+1}/{len(targets)}] {target['category_type']} ##########")
                try:
                    if category == "insurance":
                        recs = await scrape_insurance_target(ctx, session, target, limit_per_type)
                    else:
                        recs = await scrape_credit_card_target(ctx, session, target, limit_per_type)
                except Exception as e:
                    print(f"❌ '{target['category_type']}' fail: {e}")
                    recs = []
                all_records.extend(recs)
                save_records(all_records)
                print(f"✅ {target['category_type']}: {len(recs)} done | Total: {len(all_records)}")
                await asyncio.sleep(2)
        await browser.close()

    save_records(all_records)
    print(f"\n🎉 COMPLETED! Total: {len(all_records)} records -> {OUTPUT_FILE}")

# =========================================================
# CLI
# =========================================================
if __name__ == "__main__":
    """
    Usage examples:

    # Credit card
    python scraper.py --category credit_card --types "Cashback Cards,Travel Credit Cards" --limit 5
    python scraper.py --category credit_card --types all --limit all

    # Insurance
    python scraper.py --category insurance --types "Term Insurance" --limit 3
    python scraper.py --category insurance --types "Car Insurance,Bike Insurance" --limit 5
    python scraper.py --category insurance --types all --limit 3

    # List available sub-types
    python scraper.py --list
    python scraper.py --category insurance --list
    """
    parser = argparse.ArgumentParser(description="Paisabazaar Scraper v2.2")
    parser.add_argument("--category", type=str, default=None,
                        help=f"Vertical (default: {CATEGORY}). Valid: {', '.join(CATALOG)}")
    parser.add_argument("--types",    type=str, default=None,
                        help="Comma-separated sub-type names, ya 'all'")
    parser.add_argument("--limit",   type=str, default=None,
                        help="Per sub-type record count, ya 'all'")
    parser.add_argument("--list",    action="store_true",
                        help="Selected category ke sub-types list karke exit")
    args = parser.parse_args()
    cat  = args.category or CATEGORY

    if args.list:
        print(f"Category : {cat}")
        print("Sub-types:")
        for c in CATALOG.get(cat, {}):
            par   = INSURANCE_PARENT_MAP.get(c, "")
            label = f"  • {c}" + (f"  [{par}]" if par else "")
            print(label)
        raise SystemExit(0)

    if args.limit is None:
        limit = LIMIT_PER_TYPE
    elif args.limit.lower() in ("all", "none", "0"):
        limit = None
    else:
        limit = int(args.limit)

    run_types = (
        [t.strip() for t in args.types.split(",") if t.strip()]
        if args.types else RUN_TYPES
    )

    asyncio.run(scrape_paisabazaar(category=cat, run_types=run_types, limit_per_type=limit))