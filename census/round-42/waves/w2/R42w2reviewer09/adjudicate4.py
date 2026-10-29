#!/usr/bin/env python3
"""R42w2reviewer09 — v4: bidirectional-segment attribution, the decisive per-row test.

A SCORECARD table row cites SEVERAL artifacts, each with its own claim values, in the shape
    `VALUES` (`path`)      or      (`path`: VALUES)
The values belong to the NEAREST reference, on EITHER side. So for each reference R in the cell:

    segment(R) = text between the previous reference's end and the next reference's start

segment(R) carries R's own claim values (the segment is bounded by the neighbouring
references, so it cannot borrow their numbers).

Then, for the register's resolved path:
  * the segment tokens that the resolved file DOES contain  -> the resolution is corroborated;
  * the segment tokens the resolved file does NOT contain    -> either the value belongs to a
    sibling artifact in the same segment, or the resolution is wrong.

For every missing token the script asks: does some OTHER artifact named in the same segment
carry it?  If yes -> shape/attribution artifact, resolution stands.
If no  -> the token is unaccounted for: the row is a suspected mis-resolution for the L1.

Outputs: adjudication4.json, adjudication4.tsv, decisions.tsv.
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
FRAC_VARIANTS = {
    # "N/M" may be printed as cases=N pass=N, or (N, N), or new=(N, N, ...)
    "cases", "pass", "fail", "sites", "survived", "legs", "probes", "new", "old", "ok",
}


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
    forms = ["cases=%s pass=%s" % (a, b), "cases=%s" % a, "pass=%s" % b, "sites=%s" % a,
             "survived=%s" % b, "legs=%s" % a, "probes=%s" % a, "(%s, %s)" % (a, b),
             "(%s,%s)" % (a, b), "new=(%s, %s" % (a, b), "old=(%s, %s" % (a, b),
             "=%s" % a, "=%s" % b, "%s/%s" % (a, b)]
    return forms


def refs_of(unit):
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

    decisions = []
    for line_no, token, cls, path in resolved:
        kind, unit, nums = units.get(line_no, ("?", "", [line_no]))
        refs = refs_of(unit)
        rec = {"line": line_no, "token": token, "resolved_to": path,
               "unit_kind": kind, "unit_lines": nums,
               "exists_at_base": blob(BASE, path) is not None,
               "exists_at_tip": blob(TIP, path) is not None,
               "segments": []}
        hb = blob(BASE, path) or ""
        ht = blob(TIP, path) or ""
        # find the reference whose basename == the token basename (or whose paths include path)
        target = None
        for idx, (name, s, e) in enumerate(refs):
            cands = paths_for(name)
            if path in cands or name.rsplit("/", 1)[-1] == token.rsplit("/", 1)[-1]:
                target = idx
                break
        if target is None:
            rec["decision"] = "NO-REFERENCE-FOR-TOKEN"
            rec["segment_tokens"] = []
            rec["segment_found"] = []
            rec["segment_missing"] = []
            rec["unaccounted"] = []
            decisions.append(rec)
            continue
        name, s, e = refs[target]
        seg_start = refs[target - 1][2] if target > 0 else 0
        seg_end = refs[target + 1][1] if target + 1 < len(refs) else len(unit)
        segment = unit[seg_start:seg_end]
        toks = tokens_of(segment)
        found, missing, unaccounted = [], [], []
        # sibling artifacts in the same segment
        sib_names = [n for (n, s2, e2) in refs if seg_start <= s2 < seg_end and n != name]
        sib_paths = []
        for n in sib_names:
            sib_paths.extend(paths_for(n))
        sib_paths = sorted(set(p for p in sib_paths if p != path))
        sib_text = ""
        for p in sib_paths:
            b = blob(BASE, p) or blob(TIP, p) or ""
            sib_text += "\n" + b
        for k, t in toks:
            in_own = (t in hb) or (t in ht)
            if in_own:
                found.append(t)
                continue
            if k == "frac":
                forms = frac_forms(t)
                if any(f in hb or f in ht for f in forms):
                    found.append(t)
                    continue
                if any(f in sib_text for f in forms):
                    missing.append(t)
                    continue
            if sib_text and t in sib_text:
                missing.append(t)
                continue
            missing.append(t)
            unaccounted.append(t)
        rec["segments"].append({"ref": name, "segment": segment, "sibling_paths": sib_paths})
        rec["segment_tokens"] = toks
        rec["segment_found"] = found
        rec["segment_missing"] = missing
        rec["unaccounted"] = unaccounted
        rec["decision"] = "CORROBORATED" if not unaccounted else "SUSPECT-MIS-RESOLUTION"
        decisions.append(rec)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "adjudication4.json"), "w") as h:
        json.dump(decisions, h, indent=1, sort_keys=True)
    with open(os.path.join(args.out, "decisions.tsv"), "w") as h:
        h.write("line\ttoken\tresolved_to\texists_base\texists_tip\tsegment_tokens\tfound\tmissing\tunaccounted\tdecision\n")
        for r in decisions:
            h.write("%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                r["line"], r["token"], r["resolved_to"], r["exists_at_base"], r["exists_at_tip"],
                len(r.get("segment_tokens", [])), len(r.get("segment_found", [])),
                len(r.get("segment_missing", [])), len(r.get("unaccounted", [])),
                r["decision"]))
    corrob = sum(1 for r in decisions if r["decision"] == "CORROBORATED")
    suspect = sum(1 for r in decisions if r["decision"] == "SUSPECT-MIS-RESOLUTION")
    norefs = sum(1 for r in decisions if r["decision"] == "NO-REFERENCE-FOR-TOKEN")
    print("SUMMARY resolved=%d corroborated=%d suspect=%d no_reference=%d" % (
        len(decisions), corrob, suspect, norefs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
