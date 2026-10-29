#!/usr/bin/env python3
"""R42w2reviewer09 — mechanical second reading of the C1 register's 65 resolved rows.

For each register row with class `resolved`:
  * locate the token in the BASE SCORECARD.md (bf618f6c...);
  * take the table cell (or the whole line) that holds the token;
  * pull every number-like token out of that cell (key=value, N/M fractions, hex
    runs >= 7 chars: sha256 prefixes and commit prefixes);
  * test, literally, whether each token occurs in the resolved file's bytes.

Read-only. Writes nothing outside the seat directory. Usage:
    python3 -B check.py [--lane LANE] [--out OUTDIR]
"""
import argparse
import os
import re
import subprocess
import sys
import json

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "bf618f6c5c09d302994871c94903abbea2deb60d"
TIP = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
REGISTER = "census/round-42/c1-register.tsv"

GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}

# number-like token shapes
RE_EQ = re.compile(r"[A-Za-z_][A-Za-z0-9_.\-]*=(\d+)\b")
RE_FRAC = re.compile(r"(?<![\w.])(\d+)/(\d+)(?![\w.])")
RE_HEX = re.compile(r"(?<![0-9a-zA-Z])([0-9a-f]{7,64})(?![0-9a-zA-Z])")


def git(*args, root=LANE):
    env = dict(os.environ)
    env.update(GIT_ENV)
    p = subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env, check=False)
    return p.stdout


def show(rev, path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (rev, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env={**os.environ, **GIT_ENV}, check=False)
    if p.returncode != 0:
        return None
    return p.stdout


def cells_for_line(text, token):
    """Return the list of cells (table cells, or the whole line) that hold the token."""
    if "|" in text:
        cells = [c for c in text.split("|")]
        hits = [c for c in cells if token in c]
        if hits:
            return hits, "cell"
    return [text], "line"


def tokens_of(cell):
    """Pull number-like tokens out of a cell, with their shape class."""
    out = []
    for m in RE_EQ.finditer(cell):
        out.append(("eq", m.group(0)))
    for m in RE_FRAC.finditer(cell):
        out.append(("frac", m.group(0)))
    for m in RE_HEX.finditer(cell):
        out.append(("hex", m.group(1)))
    # de-duplicate, keep first occurrence order
    seen = set()
    uniq = []
    for kind, tok in out:
        if tok in seen:
            continue
        seen.add(tok)
        uniq.append((kind, tok))
    return uniq


def main(argv):
    global LANE
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=LANE)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    LANE = args.lane

    score = show(BASE, "SCORECARD.md")
    if score is None:
        sys.stderr.write("REFUSAL: base SCORECARD.md absent\n")
        return 2
    base_lines = score.decode("utf-8").split("\n")

    reg_blob = show(TIP, REGISTER)
    if reg_blob is None:
        sys.stderr.write("REFUSAL: register absent at tip\n")
        return 2
    rows = []
    for n, text in enumerate(reg_blob.decode("utf-8").split("\n")):
        if n == 0 or not text.strip():
            continue
        f = text.split("\t")
        if len(f) != 4:
            sys.stderr.write("REFUSAL: malformed register row %r\n" % text)
            return 2
        rows.append((int(f[0]), f[1], f[2], f[3]))

    resolved = [r for r in rows if r[2] == "resolved"]
    unresolved = [r for r in rows if r[2] != "resolved"]
    sys.stderr.write("register rows=%d resolved=%d unresolved=%d\n" % (len(rows), len(resolved), len(unresolved)))

    file_cache = {}

    def blob_at(rev, path):
        key = (rev, path)
        if key not in file_cache:
            file_cache[key] = show(rev, path)
        return file_cache[key]

    results = []
    for line_no, token, cls, path in resolved:
        if line_no < 1 or line_no > len(base_lines):
            results.append({"line": line_no, "token": token, "resolved_to": path,
                            "error": "base line out of range"})
            continue
        text = base_lines[line_no - 1]
        cells, kind = cells_for_line(text, token)
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
        blob_base = blob_at(BASE, path)
        blob_tip = blob_at(TIP, path)
        entry = {
            "line": line_no, "token": token, "resolved_to": path,
            "cell_kind": kind, "cell_count": len(cells),
            "cells": cells,
            "exists_at_base": blob_base is not None,
            "exists_at_tip": blob_tip is not None,
            "tokens": [],
        }
        hay_base = blob_base.decode("utf-8", "replace") if blob_base is not None else ""
        hay_tip = blob_tip.decode("utf-8", "replace") if blob_tip is not None else ""
        nfound = nmiss = 0
        for k, t in uniq:
            in_base = t in hay_base
            in_tip = t in hay_tip
            if in_base or in_tip:
                nfound += 1
                state = "found"
            else:
                nmiss += 1
                state = "not-found"
            entry["tokens"].append({"shape": k, "token": t, "state": state,
                                    "in_base": in_base, "in_tip": in_tip})
        entry["tokens_total"] = len(uniq)
        entry["tokens_found"] = nfound
        entry["tokens_not_found"] = nmiss
        entry["coverage_pct"] = 100 if not uniq else round(100.0 * nfound / len(uniq), 1)
        results.append(entry)

    full = len(results)
    fullcov = sum(1 for r in results if r.get("coverage_pct") == 100)
    low = [r for r in results if r.get("coverage_pct", 0) < 100]
    sys.stderr.write("resolved rows=%d coverage=100%%: %d  coverage<100%%: %d\n" % (full, fullcov, len(low)))

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "coverage.json"), "w") as h:
        json.dump(results, h, indent=1, sort_keys=True)
    with open(os.path.join(args.out, "low-coverage.tsv"), "w") as h:
        h.write("line\ttoken\tresolved_to\ttokens_total\ttokens_found\ttokens_not_found\tcoverage_pct\tmissing\n")
        for r in low:
            missing = ",".join("%s(%s)" % (t["token"], t["shape"]) for t in r["tokens"] if t["state"] != "found")
            h.write("%d\t%s\t%s\t%d\t%d\t%d\t%s\t%s\n" % (
                r["line"], r["token"], r["resolved_to"], r.get("tokens_total", 0),
                r.get("tokens_found", 0), r.get("tokens_not_found", 0),
                r.get("coverage_pct"), missing))
    print("SUMMARY rows=%d coverage_full=%d coverage_below_full=%d" % (full, fullcov, len(low)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
