#!/usr/bin/env python3
"""Reconcile nodes.json with what the agents actually report, and check for overlaps.

Two numbers per server have to agree in two places:

    .env on the box        MAX_INSTANCES / INSTANCE_OFFSET   (what the agent enforces)
    nodes.json on the main max_instances  / instance_offset   (what the controller plans with)

When they drift, the controller builds a run plan for slots the agent does not have and
the agent answers 400 — or worse, two boxes hand out the SAME global instance ids, so
`ran_by` lies and a bot's crash-recovery resumes another box's row.

The agent is the source of truth here: it is what is actually running. This rewrites
nodes.json to match, after showing you the diff.

    sudo ./venv/bin/python sync_nodes.py            # report only
    sudo ./venv/bin/python sync_nodes.py --write    # rewrite nodes.json (backup kept)

Restart the controller afterwards — NODES is bound at import.
"""

import json
import os
import sys
import urllib.request

NODES_FILE = os.environ.get(
    "NODES_FILE", "/var/www/html/magzter-v3/nodes.json")
WRITE = "--write" in sys.argv


def agent_status(node):
    req = urllib.request.Request(
        node["base_url"].rstrip("/") + "/api/status",
        headers={"X-Agent-Token": node.get("token", "")})
    return json.load(urllib.request.urlopen(req, timeout=8))


def main():
    data = json.load(open(NODES_FILE))
    nodes = data.get("nodes", [])

    rows, unreachable = [], []
    for n in nodes:
        try:
            st = agent_status(n)
            rows.append((n, int(st.get("max_instances") or 0), int(st.get("offset") or 0)))
        except Exception as e:
            unreachable.append((n, str(e)[:40]))

    print(f"{'server':40} {'nodes.json':>18}   {'agent':>18}")
    print("-" * 82)
    changed = []
    for n, a_max, a_off in rows:
        c_max = int(n.get("max_instances") or 0)
        c_off = int(n.get("instance_offset") or 0)
        same = (a_max == c_max and a_off == c_off)
        print(f"{n['name'][:38]:40} slots={c_max:<3} off={c_off:<5}   "
              f"slots={a_max:<3} off={a_off:<5}  {'' if same else '<-- will update'}")
        if not same:
            changed.append(n["name"])

    for n, err in unreachable:
        print(f"{n['name'][:38]:40} UNREACHABLE ({err}) — left untouched")

    # Overlap check on the AGENT numbers, i.e. on the ids actually being handed out.
    # A collision here is the quiet kind of bug: nothing errors, the numbers are just
    # wrong, and two boxes claim to be the same instance.
    print()
    spans = sorted(((off + 1, off + mx, n["name"]) for n, mx, off in rows if mx)
                   , key=lambda s: s[0])
    clash = False
    for i in range(len(spans) - 1):
        lo1, hi1, n1 = spans[i]
        lo2, hi2, n2 = spans[i + 1]
        if lo2 <= hi1:
            clash = True
            print(f"❌ OVERLAP  {n1} ({lo1}-{hi1})  vs  {n2} ({lo2}-{hi2})")
    if not clash:
        print("✅ no instance-id overlaps")
        for lo, hi, name in spans:
            print(f"   {name[:38]:40} {lo}-{hi}")
    else:
        free = max((hi for _, hi, _ in spans), default=0)
        print(f"\n   Next free offset is {free} — set INSTANCE_OFFSET={free} in the")
        print("   offending box's .env, restart its agent, then re-run this.")

    if not WRITE:
        print("\n(report only — pass --write to update nodes.json)")
        return 0
    if not changed:
        print("\nnodes.json already matches; nothing written.")
        return 0
    if clash:
        print("\nRefusing to write while offsets overlap — fix the .env first.")
        return 1

    backup = NODES_FILE + ".bak"
    with open(backup, "w") as f:
        json.dump(data, f, indent=2)
    for n, a_max, a_off in rows:
        n["max_instances"] = a_max
        n["instance_offset"] = a_off
    tmp = NODES_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, NODES_FILE)
    os.chmod(NODES_FILE, 0o600)
    print(f"\nUpdated {len(changed)} entr{'y' if len(changed)==1 else 'ies'}: "
          f"{', '.join(changed)}")
    print(f"Backup: {backup}")
    print("Now:  sudo systemctl restart magzterv3-controller")
    return 0


if __name__ == "__main__":
    sys.exit(main())
