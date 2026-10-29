#!/usr/bin/env python3
"""Final analysis of the r42 C2 counter-mutant sweep (batches A/B/C/D/E/F, G, H)."""
import json
import os
import re

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07"
LANDED = "tools/souji-freeze-check.py"
CONTROL = "census/round-42/controls/c2-stub-tool.py"

BASE_L = {"cases": "37", "pass": "37", "fail": "0", "control_clean": "REJECTED",
          "control_findings": "REJECTED", "real": "ok", "retro": "red", "retro_clean": "ok",
          "selftest": "ok", "patches": "3/3", "tool_sha": "9ddd596b98fb"}
BASE_C = {"cases": "37", "pass": "24", "fail": "13", "control_clean": "REJECTED",
          "control_findings": "REJECTED", "real": "ok", "retro": "red", "retro_clean": "ok",
          "selftest": "ok", "patches": "0/3", "tool_sha": "6e1c564a94b5"}
SHA_FIELDS = {"tool_sha"}


def d(b, f):
    out = {}
    for k, v in b.items():
        if k in SHA_FIELDS:
            continue
        if f.get(k) != v:
            out[k] = (v, f.get(k))
    return out


man, res = {}, []
for tag in ("results.json", "results-g.json", "results-h.json"):
    R = json.load(open(os.path.join(SEAT, "receipts", tag)))
    for m in R["manifest"]:
        man[m["id"]] = m
    res.extend(R["results"])
by = {}
for r in res:
    by.setdefault(r["id"], {})[r["tool"]] = r

order = sorted(man, key=lambda k: (k[0], int(k[1:]) if k[1:].isdigit() else 0))
print("%-5s %-9s %-9s %s" % ("id", "L change", "C change", "verdict"))
rows = []
for mid in order:
    L = by[mid][LANDED]
    C = by[mid][CONTROL]
    lf = L["summary_fields"] or {}
    cf = C["summary_fields"] or {}
    ld, cd = d(BASE_L, lf), d(BASE_C, cf)
    lsame = (not ld) and L["summary"] is not None
    csame = (not cd) and C["summary"] is not None
    rows.append((mid, lsame, csame, ld, cd, L, C))
    print("%-5s %-9s %-9s %s" % (
        mid, "none" if lsame else "CHANGED", "none" if csame else "CHANGED",
        ("L: " + "; ".join("%s %s->%s" % (k, v[0], v[1]) for k, v in ld.items()) if ld else "")
        + ("  ||  " if ld and cd else "") +
        ("C: " + "; ".join("%s %s->%s" % (k, v[0], v[1]) for k, v in cd.items()) if cd else "")
        + ("  [SUMMARY absent: counter crashed]" if L["summary"] is None or C["summary"] is None else "")))

print()
nochange = [m for m, ls, cs, *_ in rows if ls and cs]
print("MUTANTS WITH NO SUMMARY FIELD CHANGE FOR EITHER ARTIFACT (%d): %s" % (len(nochange), nochange))
print()
crash = [m for m, *_ in [(r[0],) for r in rows] if by[m][LANDED]["summary"] is None or by[m][CONTROL]["summary"] is None]
print("MUTANTS WHERE THE COUNTER ITSELF CRASHED (no SUMMARY at all): %s" % crash)
print()
print("EXIT CODES (baseline: landed rc=0, control rc=1)")
for mid in order:
    L, C = by[mid][LANDED], by[mid][CONTROL]
    flag = ""
    if L["rc"] != 0 or C["rc"] != 1:
        flag = "  <-- VERDICT FLIPPED"
    print("%-5s L rc=%s  C rc=%s%s" % (mid, L["rc"], C["rc"], flag))
print()
print("FULL SUMMARY LINES")
for mid in order:
    L, C = by[mid][LANDED], by[mid][CONTROL]
    print("%-5s L %s" % (mid, L["summary"]))
    print("%-5s C %s" % (mid, C["summary"]))
