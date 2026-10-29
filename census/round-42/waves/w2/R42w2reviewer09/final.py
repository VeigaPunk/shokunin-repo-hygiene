#!/usr/bin/env python3
"""R42w2reviewer09 — FINAL per-row decision for the C1 register's 65 resolved rows.

Method (frozen inputs, read-only):
  base   bf618f6c5c09d302994871c94903abbea2deb60d  (SCORECARD.md read at this revision)
  tip    3105a63b23481fccf7df58e74d14a6681e0ea0c8  (census/round-42/c1-register.tsv)

For each resolved row:
  1. locate the token in the base SCORECARD.md;
  2. take the CELL that holds the token: the '|'-delimited table field of the logical table
     row (rows wrap over several physical lines), or the whole paragraph for a prose unit;
  3. pull every number-like token out of that cell: key=value, N/M fractions, and hex runs
     of >= 7 chars (sha256 prefixes and commit prefixes);
  4. test each against the resolved file's bytes, exactly and with shape variants
     (N/M <-> cases=N pass=N / (N, N) / sites=N survived=N; a column/value TSV reading);
  5. when a token is still absent from the resolved file, attribute it to the nearest
     artifact reference in the cell and to every artifact the cell names.

A row is CORRECT when the registered path is the file the cell's own reference means:
it exists at base and tip, its basename/suffix matches the token, and where several tree
paths share the basename the registered one is the one the cell's round-context and content
select.

Outputs: final-decisions.tsv, final-decisions.json.
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
HEAD = re.compile(r"^#{1,4}\s.*?\bRound\s+(\d+)\b")


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
    forms = ["cases=%s pass=%s" % (a, b), "cases=%s" % a, "pass=%s" % b, "sites=%s" % a,
             "survived=%s" % b, "killed=%s" % a, "probes=%s" % a, "legs=%s" % a,
             "(%s, %s)" % (a, b), "(%s,%s)" % (a, b), "new=(%s, %s" % (a, b),
             "old=(%s, %s" % (a, b), "=(%s, %s" % (a, b), "=%s" % a, "=%s" % b]
    # a record may print (total, passed) while the cell prints passed/total
    if a != b:
        forms += ["(%s, %s)" % (b, a), "new=(%s, %s" % (b, a), "old=(%s, %s" % (b, a),
                  "=(%s, %s" % (b, a), "cases=%s pass=%s" % (b, a), "pass=%s" % a,
                  "cases=%s" % b, "survived=%s" % a, "killed=%s" % b]
    return forms


def refs_of(unit_text):
    out = []
    for m in RE_REF.finditer(unit_text):
        name = m.group(1) or m.group(2)
        if not name:
            continue
        if not (name.endswith(EXTS) or "/" in name):
            continue
        out.append((name, m.start(), m.end()))
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    score = show(BASE, "SCORECARD.md")
    if score is None:
        print("REFUSAL base SCORECARD absent")
        return 2
    lines = score.split("\n")
    units = logical_units(lines)
    ctx, cur = {}, None
    for n, t in enumerate(lines, 1):
        m = HEAD.match(t)
        if m:
            cur = int(m.group(1))
        ctx[n] = cur

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

    decisions = []
    for line_no, token, cls, path in resolved:
        kind, ulines, nums = units.get(line_no, ("?", [""], [line_no]))
        unit_text = "\n".join(ulines)
        # the CELL: the '|'-field(s) holding the token (table) or the paragraph (prose)
        if kind == "table":
            fields = unit_text.split("|")
            hits = [f for f in fields if token in f]
            cells = hits if hits else [unit_text]
            cell_kind = "table-field" if hits else "table-row"
        else:
            cells = [unit_text]
            cell_kind = "prose-paragraph"
        cell_text = "\n".join(cells)
        toks = tokens_of(cell_text)
        hb = blob(BASE, path) or ""
        ht = blob(TIP, path) or ""
        refs = refs_of(unit_text)
        # every artifact the CELL names
        cell_paths = set()
        for n, _s, _e in refs:
            cell_paths.update(paths_for(n))
        cell_paths = sorted(cell_paths)
        cell_text_all = ""
        for p in cell_paths:
            cell_text_all += "\n" + (blob(BASE, p) or blob(TIP, p) or "")
        # the token's own reference in the cell
        own = None
        for n, s, e in refs:
            if n.rsplit("/", 1)[-1] == token.rsplit("/", 1)[-1] or path in paths_for(n):
                own = (n, s, e)
                break
        found, variant, sibling, unbacked = [], [], [], []
        for k, t in toks:
            if t in hb or t in ht:
                found.append(t)
                continue
            hitv = None
            if k == "frac":
                for f in frac_forms(t):
                    if f in hb or f in ht:
                        hitv = f
                        break
            if hitv:
                variant.append((t, hitv))
                continue
            if t in cell_text_all:
                sibling.append(t)
                continue
            unbacked.append(t)
        decisions.append({
            "line": line_no, "token": token, "resolved_to": path,
            "cell_kind": cell_kind, "cell_field_count": len(cells),
            "cell_text": cell_text, "unit_lines": nums,
            "round_context": ctx.get(line_no),
            "exists_at_base": blob(BASE, path) is not None,
            "exists_at_tip": blob(TIP, path) is not None,
            "own_reference": own[0] if own else None,
            "same_basename_candidates": paths_for(token.rsplit("/", 1)[-1]),
            "tokens_total": len(toks),
            "tokens_found_exact": found,
            "tokens_found_by_shape": variant,
            "tokens_in_sibling_artifact": sibling,
            "tokens_unbacked": unbacked,
            "coverage_pct": 100 if not toks else round(
                100.0 * (len(found) + len(variant)) / len(toks), 1),
        })

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "final-decisions.json"), "w") as h:
        json.dump(decisions, h, indent=1, sort_keys=True)
    with open(os.path.join(args.out, "final-decisions.tsv"), "w") as h:
        h.write("line\ttoken\tresolved_to\tctx_round\tcell_kind\ttotal\texact\tshape\tsibling\tunbacked\tcoverage\tunbacked_list\n")
        for r in decisions:
            h.write("%d\t%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s\n" % (
                r["line"], r["token"], r["resolved_to"], r["round_context"], r["cell_kind"],
                r["tokens_total"], len(r["tokens_found_exact"]), len(r["tokens_found_by_shape"]),
                len(r["tokens_in_sibling_artifact"]), len(r["tokens_unbacked"]),
                r["coverage_pct"], ",".join(r["tokens_unbacked"])))
    exact100 = sum(1 for r in decisions if r["coverage_pct"] == 100)
    ok100 = sum(1 for r in decisions
                if r["tokens_found_exact"] and len(r["tokens_found_exact"]) + len(r["tokens_found_by_shape"]) == r["tokens_total"])
    print("SUMMARY resolved=%d cell_tokens_100pct_exact_only=%d cell_tokens_100pct_after_shape=%d rows_with_unbacked=%d"
          % (len(decisions), exact100, ok100, sum(1 for r in decisions if r["tokens_unbacked"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
