#!/usr/bin/env python3
"""R42w2reviewer09 — v5: whole-cell sibling attribution, the final per-row decision.

For each of the 65 resolved rows:
  * collect EVERY artifact the row's logical cell names (backticked or bare path-shaped
    names), each expanded to the tree paths its basename denotes at the base;
  * collect every number-like token of the cell;
  * for each token, record which named artifact's bytes carry it.

A token that NO named artifact carries is a claim value with no committed backing anywhere
in the cell — that is what a mis-resolution would look like.  A token carried by a sibling
artifact of the same cell is a shape/attribution artifact: the register's resolution is
untouched.

Outputs: v5-attribution.json, v5-table.tsv.
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
RE_REF = re.compile(r"`([^`\s]+)`|(?<![\w/.])((?:[\w.\-]+/)*[\w.\-]+\.(?:tsv|txt|md|py|sh|json))")
EXTS = (".tsv", ".txt", ".md", ".py", ".sh", ".json")


def show(rev, path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (rev, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env={**os.environ, **GIT_ENV}, check=False)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def logical_units(lines):
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
            units.append(("table", "\n".join(lines[i:j + 1]), list(range(i + 1, j + 2))))
            i = j + 1
            continue
        if text.startswith("#"):
            units.append(("heading", text, [i + 1]))
            i += 1
            continue
        j = i
        while j < n and lines[j].strip() and not lines[j].startswith("|") and not lines[j].startswith("#"):
            j += 1
        units.append(("prose", "\n".join(lines[i:j]), list(range(i + 1, j + 1))))
        i = j
    out = {}
    for kind, unit, nums in units:
        for ln in nums:
            out[ln] = (kind, unit, nums)
    return out


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


def frac_forms(frac):
    a, b = frac.split("/")
    return ["cases=%s pass=%s" % (a, b), "cases=%s" % a, "pass=%s" % b, "sites=%s" % a,
            "survived=%s" % b, "legs=%s" % a, "probes=%s" % a, "(%s, %s)" % (a, b),
            "(%s,%s)" % (a, b), "new=(%s, %s" % (a, b), "old=(%s, %s" % (a, b),
            "=%s" % a, "=%s" % b]


def refs_of(unit):
    out = []
    for m in RE_REF.finditer(unit):
        name = m.group(1) or m.group(2)
        if not name:
            continue
        if not (name.endswith(EXTS) or "/" in name):
            continue
        out.append(name)
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    score = show(BASE, "SCORECARD.md")
    if score is None:
        print("REFUSAL base SCORECARD absent")
        return 2
    units = logical_units(score.split("\n"))
    tp = subprocess.run(["git", "-C", LANE, "ls-tree", "-r", "--name-only", BASE],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env={**os.environ, **GIT_ENV}, check=False).stdout.decode().split("\n")
    tree = set(p for p in tp if p)

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

    def paths_for(name):
        if name in tree:
            return [name]
        return sorted(p for p in tree if p.rsplit("/", 1)[-1] == name.rsplit("/", 1)[-1])

    table = []
    detail = []
    for line_no, token, cls, path in resolved:
        kind, unit, nums = units.get(line_no, ("?", "", [line_no]))
        named = refs_of(unit)
        art_paths = set()
        for n in named:
            art_paths.update(paths_for(n))
        art_paths = sorted(art_paths)
        toks = tokens_of(unit)
        hb = blob(BASE, path) or ""
        ht = blob(TIP, path) or ""
        carriers = {}
        for k, t in toks:
            own = (t in hb) or (t in ht)
            if own:
                carriers[t] = [path]
                continue
            hit = []
            if k == "frac":
                for f in frac_forms(t):
                    for p in art_paths:
                        b = blob(BASE, p) or blob(TIP, p) or ""
                        if f in b:
                            hit.append(p)
                    if hit:
                        break
            if not hit:
                for p in art_paths:
                    b = blob(BASE, p) or blob(TIP, p) or ""
                    if t in b:
                        hit.append(p)
            carriers[t] = hit
        unbacked = [t for t, c in carriers.items() if not c]
        row = {"line": line_no, "token": token, "resolved_to": path,
               "unit_kind": kind, "unit_lines": nums,
               "exists_at_base": blob(BASE, path) is not None,
               "exists_at_tip": blob(TIP, path) is not None,
               "cell_artifacts": art_paths,
               "tokens_total": len(toks),
               "tokens_in_resolved": sum(1 for t, c in carriers.items() if path in c),
               "tokens_in_sibling": sum(1 for t, c in carriers.items() if c and path not in c),
               "tokens_unbacked": len(unbacked),
               "unbacked": unbacked,
               "carriers": carriers}
        table.append(row)
        detail.append(row)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "v5-attribution.json"), "w") as h:
        json.dump(detail, h, indent=1, sort_keys=True)
    with open(os.path.join(args.out, "v5-table.tsv"), "w") as h:
        h.write("line\ttoken\tresolved_to\ttotal\tin_resolved\tin_sibling\tunbacked\tunbacked_list\n")
        for r in table:
            h.write("%d\t%s\t%s\t%d\t%d\t%d\t%d\t%s\n" % (
                r["line"], r["token"], r["resolved_to"], r["tokens_total"],
                r["tokens_in_resolved"], r["tokens_in_sibling"], r["tokens_unbacked"],
                ",".join(r["unbacked"])))
    ok = sum(1 for r in table if r["tokens_unbacked"] == 0)
    print("SUMMARY resolved=%d cell_fully_backed=%d cell_with_unbacked=%d" % (
        len(table), ok, len(table) - ok))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
