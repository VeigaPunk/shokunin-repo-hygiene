#!/usr/bin/env python3
"""Emit the acceptance table (markdown) from receipts/table2.json (written by analyze2.py)."""
import json
import os

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester05"
with open(os.path.join(SEAT, "receipts", "table2.json")) as h:
    d = json.load(h)
ARTS = ("stub-allpass", "stub-sniff", "landed-fixture")


def cell(p):
    if p.get("missing"):
        return "MISSING"
    parts = list(p["det"]) + ["(flake) " + x for x in p["noise"]]
    if p["rc_diff"]:
        parts.append("exit %s" % p["rc"])
    return "; ".join(parts) if parts else "identical"


print("| counter mutant | change (old -> new) | stub-allpass | stub-sniff | landed-fixture | verdict |")
print("|---|---|---|---|---|---|")
for r in d["rows"]:
    c = [cell(r["per"][a]) for a in ARTS]
    print("| %s %s | `%s` -> `%s` | %s | %s | %s | %s |" % (
        r["id"], r["cat"], r["old"].replace("|", "\\|"), r["new"].replace("|", "\\|"),
        c[0], c[1], c[2], r["verdict"]))
