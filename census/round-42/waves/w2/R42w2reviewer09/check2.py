#!/usr/bin/env python3
"""R42w2reviewer09 — v2: logical-cell scoped token-coverage of the C1 register's 65 resolved rows.

v1 (check.py) scoped each row's tokens to the SINGLE physical line that holds the token.
That is too narrow: SCORECARD.md wraps one table row (or one prose paragraph) over several
physical lines, and the numbers that belong to a token often sit on a neighbouring line of
the SAME logical cell.

v2 scopes to the LOGICAL cell:
  * a table row: the physical line starting with '|' plus every following line until a line
    that ends the row with '|';
  * a prose paragraph: consecutive non-blank lines until a blank line;
  * a heading: the heading line alone.

For each resolved row: pull number-like tokens (key=value, N/M fractions, hex runs >= 7)
from the logical cell that holds the token and test each against the resolved file's bytes
(at the base bf618f6c and at the tip 3105a63b).

Read-only. Usage: python3 -B check2.py --out SEATDIR
"""
import argparse
import json
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "bf618f6c5c09d302994871c94903abbea2deb60d"
TIP = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
REGISTER = "census/round-42/c1-register.tsv"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}

RE_EQ = re.compile(r"[A-Za-z_][A-Za-z0-9_.\-]*=(\d+)\b")
RE_FRAC = re.compile(r"(?<![\w.])(\d+)/(\d+)(?![\w.])")
RE_HEX = re.compile(r"(?<![0-9a-zA-Z])([0-9a-f]{7,64})(?![0-9a-zA-Z])")


def show(rev, path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (rev, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env={**os.environ, **GIT_ENV}, check=False)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def logical_units(lines):
    """Map physical line number -> (kind, unit_text, [physical line numbers])."""
    units = []
    i = 0
    n = len(lines)
    while i < n:
        text = lines[i]
        if not text.strip():
            i += 1
            continue
        if text.startswith("|"):
            j = i
            while j < n and not lines[j].rstrip().endswith("|"):
                j += 1
            j = min(j, n - 1)
            unit = "\n".join(lines[i:j + 1])
            units.append(("table", unit, list(range(i + 1, j + 2))))
            i = j + 1
            continue
        if text.startswith("#"):
            units.append(("heading", text, [i + 1]))
            i += 1
            continue
        j = i
        while j < n and lines[j].strip() and not lines[j].startswith("|") and not lines[j].startswith("#"):
            j += 1
        unit = "\n".join(lines[i:j])
        units.append(("prose", unit, list(range(i + 1, j + 1))))
        i = j
    out = {}
    for kind, unit, nums in units:
        for ln in nums:
            out[ln] = (kind, unit, nums)
    return out


def tokens_of(unit):
    out = []
    for m in RE_EQ.finditer(unit):
        out.append(("eq", m.group(0)))
    for m in RE_FRAC.finditer(unit):
        out.append(("frac", m.group(0)))
    for m in RE_HEX.finditer(unit):
        out.append(("hex", m.group(1)))
    seen = set()
    uniq = []
    for k, t in out:
        if t in seen:
            continue
        seen.add(t)
        uniq.append((k, t))
    return uniq


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    score = show(BASE, "SCORECARD.md")
    if score is None:
        print("REFUSAL base SCORECARD absent")
        return 2
    base_lines = score.split("\n")
    units = logical_units(base_lines)

    reg = show(TIP, REGISTER)
    rows = []
    for n, text in enumerate(reg.split("\n")):
        if n == 0 or not text.strip():
            continue
        f = text.split("\t")
        rows.append((int(f[0]), f[1], f[2], f[3]))

    resolved = [r for r in rows if r[2] == "resolved"]
    cache = {}

    def blob(rev, path):
        if (rev, path) not in cache:
            cache[(rev, path)] = show(rev, path)
        return cache[(rev, path)]

    results = []
    for line_no, token, cls, path in resolved:
        kind, unit, nums = units.get(line_no, ("?", base_lines[line_no - 1] if line_no <= len(base_lines) else "", [line_no]))
        toks = tokens_of(unit)
        bb = blob(BASE, path)
        bt = blob(TIP, path)
        hb = bb or ""
        ht = bt or ""
        entry = {"line": line_no, "token": token, "resolved_to": path,
                 "unit_kind": kind, "unit_lines": nums,
                 "exists_at_base": bb is not None, "exists_at_tip": bt is not None,
                 "unit": unit, "tokens": []}
        nf = nm = 0
        for k, t in toks:
            ib = t in hb
            it = t in ht
            state = "found" if (ib or it) else "not-found"
            if state == "found":
                nf += 1
            else:
                nm += 1
            entry["tokens"].append({"shape": k, "token": t, "state": state,
                                    "in_base": ib, "in_tip": it})
        entry["tokens_total"] = len(toks)
        entry["tokens_found"] = nf
        entry["tokens_not_found"] = nm
        entry["coverage_pct"] = 100 if not toks else round(100.0 * nf / len(toks), 1)
        results.append(entry)

    full = sum(1 for r in results if r["coverage_pct"] == 100)
    low = [r for r in results if r["coverage_pct"] < 100]
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "coverage2.json"), "w") as h:
        json.dump(results, h, indent=1, sort_keys=True)
    with open(os.path.join(args.out, "low-coverage2.tsv"), "w") as h:
        h.write("line\ttoken\tresolved_to\tunit_kind\tunit_lines\ttotal\tfound\tnotfound\tcoverage\tmissing\n")
        for r in low:
            missing = ",".join("%s(%s)" % (t["token"], t["shape"]) for t in r["tokens"] if t["state"] != "found")
            h.write("%d\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%s\t%s\n" % (
                r["line"], r["token"], r["resolved_to"], r["unit_kind"],
                ",".join(map(str, r["unit_lines"])), r["tokens_total"], r["tokens_found"],
                r["tokens_not_found"], r["coverage_pct"], missing))
    print("SUMMARY resolved_rows=%d coverage_100=%d coverage_below_100=%d" % (len(results), full, len(low)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
