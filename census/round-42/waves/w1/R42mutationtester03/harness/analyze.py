#!/usr/bin/env python3
"""R42mutationtester03 analyser. Reads results.jsonl and mutants.json. M00 (identity mutant, byte-equal to the
frozen counter) is the reference for every input. For each mutant it reports, per input, which printed fields
differ from M00 and whether the exit code or stderr differ. Printed fields are split into candidate-level
(verdicts, SUMMARY counts, PRISTINE, anchors, tool_sha) and prior-level (prior=, old_killed) so that a
prior-fixture difference is visible as such. Verdicts:
  KILLED-PRINTED  a candidate-level printed field differs on some input
  KILLED-PRIOR    only prior-level printed fields differ
  KILLED-EXIT     only the exit code differs
  KILLED-STDERR   only stderr differs
  SURVIVED        nothing observable differs on any run
"""
import json
import os
import re
import sys
from collections import defaultdict

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester03"
HARNESS = os.path.join(SEAT, "harness")
KV = re.compile(r"(\w+)=(\S+)")
PRIOR_FIELDS = {"SUMMARY.prior", "SUMMARY.old_killed", "MUTANT.prior", "EQUIV.prior"}


def parse(stdout):
    out = {}
    for line in stdout.splitlines():
        if line.startswith(("MUTANT ", "EQUIV ")):
            m = re.match(r"(MUTANT|EQUIV) (\S+) candidate=(\S+) prior=(\S*)$", line)
            out["%s %s" % (m.group(1), m.group(2))] = (
                {"candidate": m.group(3), "prior": m.group(4)} if m else {"raw": line})
        elif line.startswith("SUMMARY"):
            out["SUMMARY"] = dict(KV.findall(line))
        elif line.startswith("PRISTINE"):
            out["PRISTINE"] = {"raw": line}
        else:
            out.setdefault("OTHER", []).append(line)
    return out


def diff(ref, got):
    names = set()
    for k in set(ref) | set(got):
        a, b = ref.get(k), got.get(k)
        if a == b:
            continue
        if a is None or b is None:
            names.add("line:" + k)
        elif isinstance(a, dict) and isinstance(b, dict) and not k.startswith("SUMMARY") or (
                k == "SUMMARY"):
            if k == "SUMMARY":
                for f in set(a) | set(b):
                    if a.get(f) != b.get(f):
                        names.add("SUMMARY." + f)
            elif "raw" in a or "raw" in b:
                names.add(k)
            else:
                for f in ("candidate", "prior"):
                    if a.get(f) != b.get(f):
                        names.add("%s.%s" % (k.split()[0], f))
        else:
            names.add(k)
    return names


def main():
    recs = defaultdict(list)
    with open(os.path.join(HARNESS, "results.jsonl")) as h:
        for line in h:
            r = json.loads(line)
            recs[(r["mutant"], r["input"])].append(r)
    mut = json.load(open(os.path.join(HARNESS, "mutants.json")))
    inputs = sorted({k[1] for k in recs})
    ref = {i: recs[("M00", i)][-1] for i in inputs if ("M00", i) in recs}
    verdicts = []
    for m in mut:
        mid = m["id"]
        if mid == "M00":
            continue
        cells = {i: recs[(mid, i)][-1] for i in inputs if (mid, i) in recs}
        if not cells:
            verdicts.append({"id": mid, "class": m["class"], "change": m["change"], "verdict": "NOT-RUN",
                             "fields": [], "by": {}, "runs": 0})
            continue
        by = {"printed": [], "prior": [], "exit": [], "stderr": []}
        fields = set()
        for i, got in cells.items():
            r0 = ref.get(i)
            if r0 is None:
                continue
            d = diff(parse(r0["stdout"]), parse(got["stdout"]))
            cand = {f for f in d if f not in PRIOR_FIELDS}
            prior = {f for f in d if f in PRIOR_FIELDS}
            if cand:
                by["printed"].append(i)
                fields |= cand
            if prior:
                by["prior"].append(i)
                fields |= prior
            if not d and got["rc"] != r0["rc"]:
                by["exit"].append(i)
            if not d and got["rc"] == r0["rc"] and got["stderr"] != r0["stderr"]:
                by["stderr"].append(i)
        if by["printed"]:
            v = "KILLED-PRINTED"
        elif by["prior"]:
            v = "KILLED-PRIOR"
        elif by["exit"]:
            v = "KILLED-EXIT"
        elif by["stderr"]:
            v = "KILLED-STDERR"
        else:
            v = "SURVIVED"
        verdicts.append({"id": mid, "class": m["class"], "change": m["change"], "verdict": v,
                         "fields": sorted(fields), "by": by, "runs": len(cells)})
    for v in verdicts:
        print("%-4s | %-40s | %-16s | runs=%-3d | printed-by=%s | fields=%s" % (
            v["id"], v["change"][:40], v["verdict"], v["runs"],
            ",".join(v["by"].get("printed", [])) or "-", ",".join(v["fields"]) or "-"))
    survivors = [v["id"] for v in verdicts if v["verdict"] == "SURVIVED"]
    print("SURVIVOR-COUNT", len(survivors), " ".join(survivors))
    print("VERDICT-COUNTS", json.dumps(
        {k: sum(1 for v in verdicts if v["verdict"] == k) for k in sorted({v["verdict"] for v in verdicts})}))
    with open(os.path.join(HARNESS, "verdicts.json"), "w") as h:
        json.dump(verdicts, h, indent=1)


if __name__ == "__main__":
    sys.exit(main())
