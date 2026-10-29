#!/usr/bin/env python3
"""R42w2reviewer09 — v6: CANONICAL coverage, by the `|`-delimited TABLE FIELD that holds the token.

The task's wording: "extract the SCORECARD cell (the table cell or line holding the token),
pull every number-like token ... and test whether each such token occurs in the resolved
file's bytes."

In this SCORECARD a table ROW wraps over several physical lines, and the row's `|`-delimited
FIELDS are the cells.  So:

  * a logical table row is assembled from its physical lines (a row ends at a line ending '|');
  * the row is split on '|' into fields; the field(s) containing the token are that row's cell;
  * for a non-table (prose) unit, the whole paragraph is the "line".

For each of the 65 resolved register rows: pull every number-like token (key=value, N/M
fraction, hex run >= 7 = sha256/commit prefix) from the cell and test it against the
resolved file's bytes at the base bf618f6c and at the tip 3105a63b.

Outputs: v6-table.tsv (per row), v6-results.json.
Read-only.
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
    """line number -> (kind, unit_text, unit_line_numbers)."""
    units = []
    i, n = 0, len(lines)
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
            units.append(("table", lines[i:j + 1], list(range(i + 1, j + 2))))
            i = j + 1
            continue
        if text.startswith("#"):
            units.append(("heading", [text], [i + 1]))
            i += 1
            continue
        j = i
        while j < n and lines[j].strip() and not lines[j].startswith("|") and not lines[j].startswith("#"):
            j += 1
        units.append(("prose", lines[i:j], list(range(i + 1, j + 1))))
        i = j
    out = {}
    for kind, ulines, nums in units:
        for ln in nums:
            out[ln] = (kind, ulines, nums)
    return out


def cells_for(kind, ulines, token):
    """The cell(s) holding the token: table -> the '|'-delimited field(s); prose -> the paragraph."""
    if kind == "table":
        row = "\n".join(ulines)
        fields = row.split("|")
        hits = [f for f in fields if token in f]
        if hits:
            return hits, "table-field"
        return [row], "table-row"
    return ["\n".join(ulines)], "prose-paragraph"


def tokens_of(text):
    out = []
    for m in RE_EQ.finditer(text):
        out.append(("eq", m.group(0)))
    for m in RE_FRAC.finditer(text):
        out.append(("frac", m.group(0)))
    for m in RE_HEX.finditer(text):
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
    units = logical_units(score.split("\n"))
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
        kind, ulines, nums = units.get(line_no, ("?", [""], [line_no]))
        cells, cell_kind = cells_for(kind, ulines, token)
        toks = []
        for c in cells:
            toks.extend(tokens_of(c))
        seen = set()
        uniq = []
        for k, t in toks:
            if t in seen:
                continue
            seen.add(t)
            uniq.append((k, t))
        hb = blob(BASE, path) or ""
        ht = blob(TIP, path) or ""
        toks_out = []
        nf = nm = 0
        for k, t in uniq:
            ib = t in hb
            it = t in ht
            st = "found" if (ib or it) else "not-found"
            if st == "found":
                nf += 1
            else:
                nm += 1
            toks_out.append({"shape": k, "token": t, "state": st, "in_base": ib, "in_tip": it})
        results.append({
            "line": line_no, "token": token, "resolved_to": path,
            "cell_kind": cell_kind, "cell_field_count": len(cells),
            "cell_text": cells, "unit_lines": nums,
            "exists_at_base": blob(BASE, path) is not None,
            "exists_at_tip": blob(TIP, path) is not None,
            "tokens": toks_out, "tokens_total": len(uniq),
            "tokens_found": nf, "tokens_not_found": nm,
            "coverage_pct": 100 if not uniq else round(100.0 * nf / len(uniq), 1),
        })

    full = sum(1 for r in results if r["coverage_pct"] == 100)
    low = [r for r in results if r["coverage_pct"] < 100]
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "v6-results.json"), "w") as h:
        json.dump(results, h, indent=1, sort_keys=True)
    with open(os.path.join(args.out, "v6-table.tsv"), "w") as h:
        h.write("line\ttoken\tresolved_to\tcell_kind\tfields\ttotal\tfound\tnotfound\tcoverage\tmissing\n")
        for r in results:
            missing = ",".join("%s(%s)" % (t["token"], t["shape"]) for t in r["tokens"] if t["state"] != "found")
            h.write("%d\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%s\t%s\n" % (
                r["line"], r["token"], r["resolved_to"], r["cell_kind"], r["cell_field_count"],
                r["tokens_total"], r["tokens_found"], r["tokens_not_found"], r["coverage_pct"], missing))
    print("SUMMARY resolved_rows=%d coverage_100=%d coverage_lt100=%d" % (len(results), full, len(low)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
