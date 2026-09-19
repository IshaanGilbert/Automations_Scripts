#!/usr/bin/env python3
"""Sort nodes.json by name and renumber instance_offset with no gaps or overlaps.

Edits the live file IN PLACE, so the per-node `token` survives. Hand-editing this file
is how tokens get lost: paste a copy that was shared with the tokens stripped and every
agent starts answering 401, i.e. the whole fleet goes offline at once.

Offsets are reassigned as a running total of max_instances in sorted order, so the
global instance ids form one contiguous range. Overlaps matter: two boxes on the same
ids means source_tasks.ran_by is ambiguous and a bot's crash-recovery ("resume the row
I left running") can pick up a DIFFERENT box's row and run that visit twice.

    sudo ./venv/bin/python fix_nodes.py            # show the change
    sudo ./venv/bin/python fix_nodes.py --write    # apply (backup kept)

max_instances is never touched — that is a capacity decision, not a bookkeeping one.
After writing, restart the controller and push the plan to the agents:

    sudo systemctl restart magzterv3-controller
    ./apply_nodes.sh nodes.json
"""

import json
import os
import re
import sys

NODES_FILE = os.environ.get("NODES_FILE", "/var/www/html/magzter-v3/nodes.json")
WRITE = "--write" in sys.argv


def sort_key(node):
    """Sort by the Server-X letter when there is one, else by plain name.

    'Server-A*' and 'Server-A' must land together, so the trailing marker is ignored.
    """
    m = re.match(r"\s*server[-_ ]*([a-z0-9]+)", node.get("name", ""), re.I)
    return (0, m.group(1).lower()) if m else (1, node.get("name", "").lower())


def main():
    data = json.load(open(NODES_FILE))
    nodes = data.get("nodes", [])
    if not nodes:
        print(f"no nodes in {NODES_FILE}")
        return 0

    before = [(n.get("name", "?"), int(n.get("instance_offset") or 0),
               int(n.get("max_instances") or 0)) for n in nodes]

    ordered = sorted(nodes, key=sort_key)
    off = 0
    for n in ordered:
        n["instance_offset"] = off
        off += int(n.get("max_instances") or 0)

    print(f"{'server':42} {'before':>14}   {'after':>14}")
    print("-" * 76)
    old = {name: (o, m) for name, o, m in before}
    for n in ordered:
        name = n.get("name", "?")
        o_off, o_max = old.get(name, (None, None))
        n_off, n_max = n["instance_offset"], int(n.get("max_instances") or 0)
        mark = "" if o_off == n_off else "   <-- moved"
        print(f"{name[:40]:42} off={str(o_off):<4} ids {(o_off or 0)+1}-{(o_off or 0)+(o_max or 0):<5}"
              f"   off={n_off:<4} ids {n_off+1}-{n_off+n_max}{mark}")

    missing = [n.get("name", "?") for n in ordered if not str(n.get("token", "")).strip()]
    if missing:
        print("\n⚠️  EMPTY TOKEN on: " + ", ".join(missing))
        print("   Those agents will answer 401 and show offline. Fill them in on the")
        print("   Servers page before relying on this file.")

    if not WRITE:
        print("\n(preview only — pass --write to apply)")
        return 0

    backup = NODES_FILE + ".bak"
    with open(backup, "w") as f:
        json.dump({"nodes": nodes, **{k: v for k, v in data.items() if k != "nodes"}},
                  f, indent=2)
    data["nodes"] = ordered
    tmp = NODES_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, NODES_FILE)
    os.chmod(NODES_FILE, 0o600)
    print(f"\nWritten. Backup: {backup}")
    print("Now:  sudo systemctl restart magzterv3-controller")
    print("Then: ./apply_nodes.sh nodes.json     (push the plan to the agents)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
