#!/usr/bin/env python3
"""
Shared config/settings loader for all automation scripts.

The dashboard (controller) pushes config.json /
settings.json to every node, which writes them into this directory (BASE). These
helpers read them with safe fallbacks so a missing/!partial file never crashes a
script.
"""

import os
import sys
import json

# EXE (PyInstaller) me: config.json / settings.json exe ke FOLDER se padho (user usse
# edit kar sake), bundled temp se nahi. Normal (script) me: is file ke folder se.
if getattr(sys, "frozen", False):
    BASE = os.path.dirname(sys.executable)
else:
    BASE = os.path.dirname(os.path.abspath(__file__))


def load_json(name, default=None):
    """Read BASE/<name> as JSON. Returns `default` (or {}) on any error."""
    try:
        with open(os.path.join(BASE, name)) as f:
            return json.loads(f.read().strip())
    except Exception:
        return {} if default is None else default


def load_settings(section):
    """Return the per-script section of settings.json (e.g. 'reader',
    'eligibility', 'card_generation'), or {} if absent."""
    data = load_json("settings.json", {}) or {}
    sec = data.get(section, {})
    return sec if isinstance(sec, dict) else {}


