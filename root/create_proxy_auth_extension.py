import zipfile
import os

PROXY_HOST = "proxy.geonode.com"
PROXY_PORT = 11000
PROXY_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
PROXY_PASS = "CHANGE_ME_SECRET"

manifest_json = """
{
  "version": "1.0.0",
  "manifest_version": 2,
  "name": "Proxy Auth Extension",
  "permissions": [
    "proxy",
    "tabs",
    "unlimitedStorage",
    "storage",
    "<all_urls>",
    "webRequest",
    "webRequestBlocking"
  ],
  "background": {
    "scripts": ["background.js"]
  }
}
"""

background_js = f"""
var config = {{
  mode: "fixed_servers",
  rules: {{
    singleProxy: {{
      scheme: "socks5",
      host: "{PROXY_HOST}",
      port: parseInt({PROXY_PORT})
    }},
    bypassList: ["localhost"]
  }}
}};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

function callbackFn(details) {{
  return {{
    authCredentials: {{
      username: "{PROXY_USER}",
      password: "CHANGE_ME_PASSWORD"
    }}
  }};
}}

chrome.webRequest.onAuthRequired.addListener(
  callbackFn,
  {{urls: ["<all_urls>"]}},
  ['blocking']
);
"""

with zipfile.ZipFile("proxy_auth_extension.zip", "w") as zp:
    zp.writestr("manifest.json", manifest_json)
    zp.writestr("background.js", background_js)
