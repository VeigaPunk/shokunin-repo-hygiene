#!/usr/bin/env python3
"""R42mutationtester03 analyser. Reads results.jsonl (mutant x input runs) and mutants.json, takes M00
(the identity mutant, byte-equal to the frozen counter) as the reference for every input, and prints per
mutant: the inputs on which its printed output or exit code differs from M00, the printed fields that
changed, and the verdict. A mutant is KILLED if any input shows a printed-field or exit-code change, and
SURVIVED if none does. stderr-only differences are reported separately."""
import collections
import json
import os
import re
import sys

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester03"
HARNESS = os.path.join(SEAT, "harness")

KV = re.compile(r"(\w+)=(\S+)")


def fields(stdout):
    """Map each printed line to (field name -> value). Lines are keyed by their label."""
    out = {}
    for line in stdout.splitlines():
        if line.startswith("MUTANT "):
            m = re.match(r"MUTANT (\S+) candidate=(\S+) prior=(\S*)", line)
            key = "MUTANT " + m.group(1)
            out[key] = {"candidate": m.group(2), "prior": m.group(3)} if m else {"raw": line}
        elif line.startswith("EQUIV "):
            m = re.match(r"EQUIV (\S+) candidate=(\S+) prior=(\S*)", line)
            key = "EQUIV " + m.group(1)
            out[key] = {"candidate": m.group(2), "prior": m.group(3)} if m else {"raw": line}
        elif line.startswith("SUMMARY"):
            out["SUMMARY"] = dict(KV.findall(line))
        elif line.startswith("PRISTINE"):
            out["PRISTINE"] = {"raw": line}
        else:
            out.setdefault("OTHER", []).append(line)
    return out


def diff_fields(ref, got):
    names = set()
    keys = set(ref) | set(got)
    for k in keys:
        a, b = ref.get(k), got.get(k)
        if a == b:
            continue
        if a is None or b is None:
            names.add("line:" + k)
            continue
        if isinstance(a, dict) and isinstance(b, dict):
            for f in set(a) | set(b):
                if a.get(f) != b.get(f):
                    names.add("%s.%s" % (k.split()[0] if k.startswith(("MUTANT", "EQUIV")) else k, f)
                              if k != "SUMMARY" else "SUMMARY." + f)
        else:
            names.add(k)
    return names


def main():
    recs = {}
    with open(os.path.join(HARNESS, "results.jsonl")) as h:
        for line in h:
            r = json.loads(line)
            recs[(r["mutant"], r["input"])] = r
    mut = json.load(open(os.path.join(HARNESS, "mutants.json")))
    inputs = sorted({k[1] for k in recs})
    rows = []
    for m in mut:
        mid = m["id"]
        if mid == "M00":
            continue
        ran = [i for i in inputs if (mid, i) in recs]
        if not ran:
            rows.append((mid, m, "NOT-RUN", {}, set(), set(), []))
            continue
        printed_inputs, exit_inputs, err_inputs = [], [], []
        names = set()
        for i in ran:
            ref = recs[("M00", i)]
            got = recs[(mid, i)]
            fd = diff_fields(fields(ref["stdout"]), fields(got["stdout"]))
            if fd:
                printed_inputs.append(i)
                names |= fd
            elif got["rc"] != ref["rc"]:
                exit_inputs.append(i)
            if got["rc"] == ref["rc"] and not fd and got["stderr"] != ref["stderr"]:
                err_inputs.append(i)
        if printed_inputs:
            verdict = "KILLED (printed)"
        elif exit_inputs:
            verdict = "KILLED (exit code only)"
        elif err_inputs:
            verdict = "SURVIVED on printed fields (stderr differs)"
        else:
            verdict = "SURVIVED"
        rows.append((mid, m, verdict, {"printed": printed_inputs, "exit": exit_inputs, "stderr": err_inputs},
                     names, ran, []))
    for mid, m, verdict, by, names, ran, _x in rows:
        print("%s | %s | %s | killed_by=%s | fields=%s | runs=%d" % (
            mid, m["change"], verdict,
            ",".join(by.get("printed", []) + by.get("exit", [])) or "-",
            ",".join(sorted(names)) or "-", len(ran)))
    c = collections.Counter(r[2].split(" (")[0].split(" on")[0] for r in rows)
    print("SURVIVOR-COUNT", sum(1 for r in rows if r[2].startswith("SURVIVED")))
    print("VERDICTS", dict(c))
    with open(os.path.join(HARNESS, "verdicts.json"), "w") as h:
        json.dump([{"id": mid, "class": m["class"], "change": m["change"], "verdict": verdict,
                    "by": by, "fields": sorted(names), "runs": len(ran)}
                   for mid, m, verdict, by, names, ran, _x in rows], h, indent=1)


if __name__ == "__main__":
    sys.exit(main())
