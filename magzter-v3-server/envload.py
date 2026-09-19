"""
Tiny .env loader — zero dependencies (no python-dotenv needed).

Reads KEY=VALUE lines from a .env file in the project root and puts them into
os.environ WITHOUT overriding variables that are already set in the real
environment (so systemd/Environment= or shell exports always win).

Usage (top of controller.py / node_agent.py):
    from envload import load_env
    load_env()
"""
import os


def load_env(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return
    try:
        with open(path) as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass
