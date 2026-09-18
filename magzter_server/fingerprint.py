#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fingerprint.py — GoLogin-style browser fingerprint spoofing for Playwright.

A self-contained "anti-detect profile" generator. It builds ONE internally-consistent,
realistic desktop-Chrome fingerprint and hands back everything the buyer/reader need:

    from fingerprint import Fingerprint
    fp = Fingerprint(seed=email)                 # stable per account (retry-safe)
    ctx = browser.new_context(**fp.context_kwargs(proxy_server=local_proxy))
    ctx.add_init_script(fp.init_script())        # patches every page in the context

SEED:  pass a stable value (the account email) and the SAME fingerprint comes back every
       time — so a re-run of an account looks like the SAME device, not a brand-new one
       (a fingerprint that flips every run is itself a detection signal). seed=None => a
       fresh random fingerprint.

WHAT IT SPOOFS (like GoLogin / Multilogin / AdsPower):
  • User-Agent + Client Hints (sec-ch-ua, userAgentData.brands/platform/mobile)
  • navigator: platform, hardwareConcurrency, deviceMemory, languages, vendor,
    maxTouchPoints, webdriver(=undefined), plugins/mimeTypes
  • screen: width/height/avail*, colorDepth, pixelDepth, devicePixelRatio
  • WebGL / WebGL2: UNMASKED_VENDOR_WEBGL + UNMASKED_RENDERER_WEBGL (GPU spoof)
  • Canvas 2D + WebGL readback: deterministic per-profile NOISE (breaks canvas hashing)
  • AudioContext: deterministic noise on channel data (breaks audio hashing)
  • WebRTC: strips host/srflx ICE candidates so the real IP can't leak around the proxy
  • permissions.query, chrome runtime, battery, mediaDevices — realistic fakes

NOTE: the timezone/locale here should match the proxy's exit country (India => Asia/
Kolkata, en-IN) — that's already what the buyer/reader use.
"""

import hashlib
import random

# ---- realistic current desktop Chrome builds (UA + the bits that must match it) ----
_CHROME_MAJORS = [122, 123, 124, 125, 126]

_OS_PROFILES = [
    {
        "os": "win10", "platform": "Win32", "ch_platform": "Windows",
        "ch_platform_version": "10.0.0",
        "ua_os": "Windows NT 10.0; Win64; x64",
        "webgl": [
            ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
            ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
            ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
            ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 6600 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
        ],
    },
    {
        "os": "win11", "platform": "Win32", "ch_platform": "Windows",
        "ch_platform_version": "15.0.0",
        "ua_os": "Windows NT 10.0; Win64; x64",
        "webgl": [
            ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 4060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
            ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
        ],
    },
    {
        "os": "mac", "platform": "MacIntel", "ch_platform": "macOS",
        "ch_platform_version": "14.4.1",
        "ua_os": "Macintosh; Intel Mac OS X 10_15_7",
        "webgl": [
            ("Google Inc. (Apple)", "ANGLE (Apple, ANGLE Metal Renderer: Apple M1, Unspecified Version)"),
            ("Google Inc. (Apple)", "ANGLE (Apple, ANGLE Metal Renderer: Apple M2, Unspecified Version)"),
            ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(TM) Plus Graphics OpenGL Engine, OpenGL 4.1)"),
        ],
    },
]

_SCREENS = [(1920, 1080), (1536, 864), (1366, 768), (1440, 900), (1600, 900), (2560, 1440)]
_CORES = [4, 6, 8, 8, 12, 16]
_MEMORY = [4, 8, 8, 8, 16]
_DPR = [1, 1, 1.25, 1.5, 2]
# India-first (matches the India proxy); keep en-US as a minority for variety.
_LANGS = [["en-IN", "en"], ["en-IN", "en", "hi"], ["en-US", "en"], ["en-GB", "en"]]


def _rng(seed):
    if seed is None:
        return random.Random()
    h = int(hashlib.sha256(str(seed).encode("utf-8")).hexdigest(), 16)
    return random.Random(h)


class Fingerprint:
    """One consistent anti-detect profile. Deterministic from `seed`."""

    def __init__(self, seed=None, locale="en-IN", timezone_id="Asia/Kolkata"):
        r = _rng(seed)
        osp = r.choice(_OS_PROFILES)
        major = r.choice(_CHROME_MAJORS)
        full_ver = f"{major}.0.{r.randint(6000, 6300)}.{r.randint(50, 199)}"

        sw, sh = r.choice(_SCREENS)
        webgl_vendor, webgl_renderer = r.choice(osp["webgl"])

        self.locale = locale
        self.timezone_id = timezone_id
        self.languages = r.choice(_LANGS)
        # keep primary language aligned with the requested locale when possible
        if locale and locale not in self.languages:
            self.languages = [locale] + [l for l in self.languages if l != locale]

        self.platform = osp["platform"]
        self.ch_platform = osp["ch_platform"]
        self.ch_platform_version = osp["ch_platform_version"]
        self.ua = (f"Mozilla/5.0 ({osp['ua_os']}) AppleWebKit/537.36 "
                   f"(KHTML, like Gecko) Chrome/{major}.0.0.0 Safari/537.36")
        self.ua_full_version = full_ver
        self.chrome_major = major

        self.screen_w, self.screen_h = sw, sh
        # taskbar / menubar reduce avail height a touch
        self.avail_w = sw
        self.avail_h = sh - (osp["os"] == "mac" and 25 or 48)
        self.color_depth = 24
        self.dpr = r.choice(_DPR)
        self.cores = r.choice(_CORES)
        self.memory = r.choice(_MEMORY)
        self.max_touch = 0
        self.webgl_vendor = webgl_vendor
        self.webgl_renderer = webgl_renderer
        # deterministic noise seeds (small, stable) for canvas/audio
        self.canvas_noise = r.randint(1, 240)
        self.audio_noise = (r.random() * 1e-4) - 5e-5

        # viewport: slightly smaller than the screen (window chrome)
        self.viewport_w = sw
        self.viewport_h = self.avail_h

    # ---- Playwright context kwargs ----------------------------------------
    def context_kwargs(self, proxy_server=None, ignore_https_errors=True):
        """Kwargs for browser.new_context(...). Merge proxy yourself or pass
        proxy_server to have it added."""
        kw = dict(
            user_agent=self.ua,
            locale=self.locale,
            timezone_id=self.timezone_id,
            viewport={"width": self.viewport_w, "height": self.viewport_h},
            screen={"width": self.screen_w, "height": self.screen_h},
            device_scale_factor=self.dpr,
            is_mobile=False,
            has_touch=False,
            color_scheme="light",
            extra_http_headers={
                "sec-ch-ua": self._sec_ch_ua(),
                "sec-ch-ua-mobile": "9999999999",
                "sec-ch-ua-platform": f'"{self.ch_platform}"',
                "Accept-Language": ",".join(
                    f"{l}{'' if i == 0 else f';q=0.{9 - i}'}" for i, l in enumerate(self.languages)
                ),
            },
        )
        if proxy_server:
            kw["proxy"] = {"server": proxy_server}
            kw["ignore_https_errors"] = ignore_https_errors
        elif ignore_https_errors:
            kw["ignore_https_errors"] = True
        return kw

    def _sec_ch_ua(self):
        m = self.chrome_major
        return f'"Chromium";v="{m}", "Google Chrome";v="{m}", "Not?A_Brand";v="99"'

    def _brands_json(self):
        m = self.chrome_major
        return (f'[{{"brand":"Chromium","version":"{m}"}},'
                f'{{"brand":"Google Chrome","version":"{m}"}},'
                f'{{"brand":"Not?A_Brand","version":"99"}}]')

    # ---- the page-level patch (one init script for the whole context) -----
    def init_script(self):
        repl = {
            "@@PLATFORM@@": self.platform,
            "@@CORES@@": str(self.cores),
            "@@MEMORY@@": str(self.memory),
            "@@MAXTOUCH@@": str(self.max_touch),
            "@@LANGS@@": str(self.languages).replace("'", '"'),
            "@@LANG0@@": self.languages[0],
            "@@SCREEN_W@@": str(self.screen_w),
            "@@SCREEN_H@@": str(self.screen_h),
            "@@AVAIL_W@@": str(self.avail_w),
            "@@AVAIL_H@@": str(self.avail_h),
            "@@COLOR_DEPTH@@": str(self.color_depth),
            "@@DPR@@": str(self.dpr),
            "@@WEBGL_VENDOR@@": self.webgl_vendor.replace("'", ""),
            "@@WEBGL_RENDERER@@": self.webgl_renderer.replace("'", ""),
            "@@CANVAS_NOISE@@": str(self.canvas_noise),
            "@@AUDIO_NOISE@@": repr(self.audio_noise),
            "@@CH_PLATFORM@@": self.ch_platform,
            "@@CH_PLATFORM_VERSION@@": self.ch_platform_version,
            "@@UA_FULL@@": self.ua_full_version,
            "@@CHROME_MAJOR@@": str(self.chrome_major),
            "@@BRANDS@@": self._brands_json(),
        }
        js = _INIT_JS
        for k, v in repl.items():
            js = js.replace(k, v)
        return js


# Convenience: one-shot helpers
def context_kwargs(seed=None, proxy_server=None, locale="en-IN", timezone_id="Asia/Kolkata"):
    return Fingerprint(seed, locale, timezone_id).context_kwargs(proxy_server)


def init_script(seed=None, locale="en-IN", timezone_id="Asia/Kolkata"):
    return Fingerprint(seed, locale, timezone_id).init_script()


# Tokens are replaced in Fingerprint.init_script(). Every override is wrapped in try/catch
# so a failure on one surface never breaks the page. Runs BEFORE the site's own scripts.
_INIT_JS = r"""
(() => {
  const D = (obj, prop, val) => {
    try { Object.defineProperty(obj, prop, { get: () => val, configurable: true }); } catch (e) {}
  };

  // ---- navigator ----
  try { D(navigator, 'webdriver', undefined); } catch (e) {}
  D(navigator, 'platform', '@@PLATFORM@@');
  D(navigator, 'hardwareConcurrency', @@CORES@@);
  D(navigator, 'deviceMemory', @@MEMORY@@);
  D(navigator, 'maxTouchPoints', @@MAXTOUCH@@);
  D(navigator, 'vendor', 'Google Inc.');
  D(navigator, 'languages', @@LANGS@@);
  try {
    Object.defineProperty(navigator, 'language', { get: () => '@@LANG0@@', configurable: true });
  } catch (e) {}

  // ---- Client Hints (userAgentData) ----
  try {
    const brands = @@BRANDS@@;
    const uaData = {
      brands: brands,
      mobile: false,
      platform: '@@CH_PLATFORM@@',
      getHighEntropyValues: (hints) => Promise.resolve({
        brands: brands,
        mobile: false,
        platform: '@@CH_PLATFORM@@',
        platformVersion: '@@CH_PLATFORM_VERSION@@',
        architecture: 'x86',
        bitness: '64',
        model: '',
        uaFullVersion: '@@UA_FULL@@',
        fullVersionList: brands.map(b => ({ brand: b.brand, version: '@@UA_FULL@@' }))
      }),
      toJSON: () => ({ brands: brands, mobile: false, platform: '@@CH_PLATFORM@@' })
    };
    Object.defineProperty(navigator, 'userAgentData', { get: () => uaData, configurable: true });
  } catch (e) {}

  // ---- window.chrome ----
  try {
    if (!window.chrome) window.chrome = {};
    window.chrome.runtime = window.chrome.runtime || {};
    window.chrome.app = window.chrome.app || { isInstalled: false };
  } catch (e) {}

  // ---- screen ----
  D(screen, 'width', @@SCREEN_W@@);
  D(screen, 'height', @@SCREEN_H@@);
  D(screen, 'availWidth', @@AVAIL_W@@);
  D(screen, 'availHeight', @@AVAIL_H@@);
  D(screen, 'colorDepth', @@COLOR_DEPTH@@);
  D(screen, 'pixelDepth', @@COLOR_DEPTH@@);
  try { Object.defineProperty(window, 'devicePixelRatio', { get: () => @@DPR@@, configurable: true }); } catch (e) {}

  // ---- permissions.query (Notification should reflect denied, not 'prompt' under automation) ----
  try {
    const origQuery = navigator.permissions && navigator.permissions.query;
    if (origQuery) {
      navigator.permissions.query = (p) =>
        (p && p.name === 'notifications')
          ? Promise.resolve({ state: Notification.permission, onchange: null })
          : origQuery.call(navigator.permissions, p);
    }
  } catch (e) {}

  // ---- plugins / mimeTypes (a real Chrome exposes the PDF viewer set) ----
  try {
    const mk = (name, fn, desc) => ({ name, filename: fn, description: desc, length: 1 });
    const plugins = [
      mk('PDF Viewer', 'internal-pdf-viewer', 'Portable Document Format'),
      mk('Chrome PDF Viewer', 'internal-pdf-viewer', 'Portable Document Format'),
      mk('Chromium PDF Viewer', 'internal-pdf-viewer', 'Portable Document Format'),
      mk('Microsoft Edge PDF Viewer', 'internal-pdf-viewer', 'Portable Document Format'),
      mk('WebKit built-in PDF', 'internal-pdf-viewer', 'Portable Document Format'),
    ];
    D(navigator, 'plugins', plugins);
    D(navigator, 'mimeTypes', [{ type: 'application/pdf', suffixes: 'pdf', description: '' }]);
  } catch (e) {}

  // ---- WebGL GPU spoof (both webgl and webgl2) ----
  try {
    const patch = (proto) => {
      const gp = proto.getParameter;
      proto.getParameter = function (p) {
        if (p === 37445) return '@@WEBGL_VENDOR@@';     // UNMASKED_VENDOR_WEBGL
        if (p === 37446) return '@@WEBGL_RENDERER@@';   // UNMASKED_RENDERER_WEBGL
        return gp.call(this, p);
      };
    };
    if (window.WebGLRenderingContext) patch(WebGLRenderingContext.prototype);
    if (window.WebGL2RenderingContext) patch(WebGL2RenderingContext.prototype);
  } catch (e) {}

  // ---- Canvas noise (deterministic) — breaks canvas hashing without obvious breakage ----
  try {
    const N = @@CANVAS_NOISE@@;
    const shift = (data) => {
      for (let i = 0; i < data.length; i += 4) {
        data[i]     = (data[i]     + (N % 3) - 1 + 256) % 256;
        data[i + 1] = (data[i + 1] + ((N >> 1) % 3) - 1 + 256) % 256;
        data[i + 2] = (data[i + 2] + ((N >> 2) % 3) - 1 + 256) % 256;
      }
    };
    const origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function (...a) {
      const img = origGetImageData.apply(this, a);
      try { shift(img.data); } catch (e) {}
      return img;
    };
    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function (...a) {
      try {
        const ctx = this.getContext('2d');
        if (ctx) {
          const img = origGetImageData.call(ctx, 0, 0, this.width, this.height);
          shift(img.data); ctx.putImageData(img, 0, 0);
        }
      } catch (e) {}
      return origToDataURL.apply(this, a);
    };
  } catch (e) {}

  // ---- AudioContext noise (deterministic) — breaks audio fingerprinting ----
  try {
    const AN = @@AUDIO_NOISE@@;
    const origGCD = AudioBuffer.prototype.getChannelData;
    AudioBuffer.prototype.getChannelData = function (...a) {
      const d = origGCD.apply(this, a);
      try { for (let i = 0; i < d.length; i += 137) d[i] = d[i] + AN; } catch (e) {}
      return d;
    };
    if (window.AnalyserNode) {
      const origFF = AnalyserNode.prototype.getFloatFrequencyData;
      AnalyserNode.prototype.getFloatFrequencyData = function (arr) {
        origFF.call(this, arr);
        try { for (let i = 0; i < arr.length; i += 71) arr[i] = arr[i] + AN * 1e3; } catch (e) {}
      };
    }
  } catch (e) {}

  // ---- WebRTC: stop the real IP leaking around the proxy (drop host/srflx candidates) ----
  try {
    const RTC = window.RTCPeerConnection || window.webkitRTCPeerConnection;
    if (RTC) {
      const Wrapped = function (cfg, con) {
        const pc = new RTC(cfg, con);
        const origAdd = pc.addEventListener.bind(pc);
        pc.addEventListener = (type, cb, opts) => {
          if (type === 'icecandidate') {
            const wrap = (ev) => {
              try {
                if (ev && ev.candidate && /typ (host|srflx)/.test(ev.candidate.candidate || '')) return;
              } catch (e) {}
              return cb(ev);
            };
            return origAdd(type, wrap, opts);
          }
          return origAdd(type, cb, opts);
        };
        return pc;
      };
      Wrapped.prototype = RTC.prototype;
      window.RTCPeerConnection = Wrapped;
      if (window.webkitRTCPeerConnection) window.webkitRTCPeerConnection = Wrapped;
    }
  } catch (e) {}

  // ---- battery (fake healthy desktop) ----
  try {
    if (navigator.getBattery) {
      navigator.getBattery = () => Promise.resolve({
        charging: true, chargingTime: 0, dischargingTime: Infinity, level: 1,
        addEventListener: () => {}, removeEventListener: () => {}
      });
    }
  } catch (e) {}
})();
"""
