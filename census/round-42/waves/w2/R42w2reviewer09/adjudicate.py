#!/usr/bin/env python3
"""R42w2reviewer09 — v3: clause-scoped adjudication of the C1 register's 65 resolved rows.

A SCORECARD logical cell holds SEVERAL claims, each naming one artifact and its own values
(`c1-vacuity2.txt` (`mismatches=9`)). Testing every number in the cell against one resolved
file is therefore meaningless: most numbers belong to a sibling claim.

v3 splits the logical cell into CLAUSES at artifact references. For every artifact reference
in the cell (expanded to the tree paths its basename denotes), the clause is the text from
that reference up to the next reference. The clause's number-like tokens are tested against
that artifact's bytes.

The register row is then judged by:
  * is the register's resolved_to among the cell's artifact references (a target the cell
    actually cites)?
  * do the clause tokens of THAT reference occur in the register's resolved file?
  * does the resolved file exist at base and at the tip?

Outputs: clause-adjudication.tsv, adjudication.json.
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


def refs_of(unit):
    """Artifact references in the unit, in order, with the character span."""
    out = []
    for m in RE_REF.finditer(unit):
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

    adjudged = []
    with open(os.path.join(args.out, "clause-adjudication.tsv"), "w") as h:
        h.write("line\ttoken\tresolved_to\tclause_ref\tclause_path\tclause_tokens\tfound_in_clause_path\tin_registered_path\n")
        for line_no, token, cls, path in resolved:
            kind, unit, nums = units.get(line_no, ("?", "", [line_no]))
            refs = refs_of(unit)
            rec = {"line": line_no, "token": token, "resolved_to": path,
                   "unit_kind": kind, "unit_lines": nums,
                   "exists_at_base": blob(BASE, path) is not None,
                   "exists_at_tip": blob(TIP, path) is not None,
                   "clauses": [], "cited_paths": set()}
            for idx, (name, s, e) in enumerate(refs):
                end = refs[idx + 1][1] if idx + 1 < len(refs) else len(unit)
                clause = unit[e:end]
                ctoks = tokens_of(clause)
                cpaths = paths_for(name)
                rec["cited_paths"].update(cpaths)
                hb = blob(BASE, path) or ""
                for cp in cpaths:
                    cb = blob(BASE, cp) or ""
                    found = [(k, t, t in cb) for k, t in ctoks]
                    rec["clauses"].append({"ref": name, "paths": cpaths, "tokens": ctoks,
                                           "found": found})
                    for k, t, ok in found:
                        h.write("%d\t%s\t%s\t%s\t%s\t%s(%s)\t%s\t%s\n" % (
                            line_no, token, path, name, cp, t, k, ok, t in hb))
            rec["cited_paths"] = sorted(rec["cited_paths"])
            rec["registered_is_cited"] = path in rec["cited_paths"]
            # the clause whose paths include the registered path
            own = None
            for c in rec["clauses"]:
                if path in c["paths"]:
                    own = c
                    break
            rec["own_clause_found"] = own is not None
            if own:
                cb = blob(BASE, path) or ""
                rec["own_clause_tokens"] = own["tokens"]
                rec["own_clause_hit"] = sum(1 for k, t in own["tokens"] if t in cb)
                rec["own_clause_total"] = len(own["tokens"])
                rec["own_clause_missing"] = [t for k, t in own["tokens"] if t not in cb]
                rec["own_clause_coverage_pct"] = 100 if not own["tokens"] else round(
                    100.0 * rec["own_clause_hit"] / len(own["tokens"]), 1)
            else:
                rec["own_clause_tokens"] = []
                rec["own_clause_hit"] = 0
                rec["own_clause_total"] = 0
                rec["own_clause_missing"] = []
                rec["own_clause_coverage_pct"] = None
            adjudged.append(rec)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "adjudication.json"), "w") as h:
        json.dump(adjudged, h, indent=1, sort_keys=True)
    cited = sum(1 for r in adjudged if r["registered_is_cited"])
    ownc = sum(1 for r in adjudged if r["own_clause_found"])
    full = sum(1 for r in adjudged if r["own_clause_coverage_pct"] == 100)
    part = sum(1 for r in adjudged if r["own_clause_coverage_pct"] is not None
               and r["own_clause_coverage_pct"] < 100)
    noown = sum(1 for r in adjudged if not r["own_clause_found"])
    print("SUMMARY resolved=%d registered_is_cited=%d own_clause_found=%d own_clause_100=%d own_clause_lt100=%d no_own_clause=%d"
          % (len(adjudged), cited, ownc, full, part, noown))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
