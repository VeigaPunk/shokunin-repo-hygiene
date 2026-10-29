#!/usr/bin/env python3
"""Emit the report's two tables (single-point mutants, stacks) as markdown."""
import json
import os
import re

S = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07"
LANDED = "tools/souji-freeze-check.py"
CONTROL = "census/round-42/controls/c2-stub-tool.py"
BL = ("SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok "
      "retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb")
BC = ("SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=ok "
      "retro=red retro_clean=ok selftest=ok patches=0/3 tool_sha=6e1c564a94b5")

man, res = {}, []
for t in ("results.json", "results-g.json", "results-h.json"):
    R = json.load(open(os.path.join(S, "receipts", t)))
    for m in R["manifest"]:
        man[m["id"]] = m
    res += R["results"]
by = {}
for r in res:
    by.setdefault(r["id"], {})[r["tool"]] = r


def short(s, base_s):
    """Compact the SUMMARY to only the fields that differ from that artifact's own baseline."""
    if s is None:
        return "NO SUMMARY (counter crashed)"
    f = dict(re.findall(r"(\w+)=([^\s]+)", s))
    base = dict(re.findall(r"(\w+)=([^\s]+)", base_s))
    order = ["cases", "pass", "fail", "control_clean", "control_findings", "real", "retro",
             "retro_clean", "selftest", "patches", "tool_sha"]
    out = []
    for k in order:
        if k in f and f[k] != base[k]:
            out.append("%s=%s" % (k, f[k]))
    return ("(unchanged)" if not out else " ".join(out))


def verdict(mid):
    L, C = by[mid][LANDED], by[mid][CONTROL]
    if L["summary"] is None or C["summary"] is None:
        return "COUNTER CRASHED (no SUMMARY; exit %s/%s)" % (L["rc"], C["rc"])
    if L["rc"] == 0 and C["rc"] == 1:
        return "correct"
    if L["rc"] == 1 and C["rc"] == 1:
        return "FALSE RED on the landed tool"
    if L["rc"] == 0 and C["rc"] == 0:
        return "FALSE GREEN on the r41 control (vacuity)"
    return "landed rc=%s control rc=%s" % (L["rc"], C["rc"])


def rows(ids):
    for mid in ids:
        m = man[mid]
        L, C = by[mid][LANDED], by[mid][CONTROL]
        print("| `%s` | %s | %s | %s | %s |" % (
            mid, m["region"], m["desc"], short(L["summary"], BL) + " / " + short(C["summary"], BC),
            verdict(mid)))


single = [i for i in man if i not in ("S1", "S2", "S3", "S4")]
single.sort(key=lambda k: (k[0], int(k[1:])))
stacks = [i for i in man if i.startswith("S")]
stacks.sort()
print("### TABLE 1 — single-point counter mutants\n")
rows(single)
print("\n### TABLE 2 — stacked mutants (two or three single-point changes together)\n")
rows(stacks)

print("\n### no-SUMMARY-change set (verbatim SUMMARY, both artifacts)\n")
both = [i for i in single
        if by[i][LANDED]["summary"] == BL and by[i][CONTROL]["summary"] == BC]
print(", ".join("`%s`" % i for i in both))
print("count:", len(both))
print("\n### landed-only-identical set\n")
lo = [i for i in single if by[i][LANDED]["summary"] == BL]
print(", ".join("`%s`" % i for i in lo), "count:", len(lo))
print("\n### control-only-identical set\n")
co = [i for i in single if by[i][CONTROL]["summary"] == BC]
print(", ".join("`%s`" % i for i in co), "count:", len(co))
