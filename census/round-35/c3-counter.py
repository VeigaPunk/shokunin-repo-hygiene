#!/usr/bin/env python3
r"""r35 C3 coverage counter (frozen at the r35 preregistration): F1 admitted-knowledge legs.

Claim (frozen): corpus/knowledge/fleet-prune-numerator-r35.md is an admitted knowledge
entry on frontier ground F1 (the lane coverage map's "fleet exposure numerator re-census"
item), carrying the provenance trio, citing opened-this-round SOURCES rows, and matching
the committed census record census/round-35/records/prune-census.tsv figure for figure;
plus a second staged-package entry when adopted (legs E2 row in c3-legs.tsv).

Legs (c3-legs.tsv rows; `entry` column names the knowledge path each row's legs cover,
`record` names the census record that grounds the numerator figures or `-` for none):

  L1 entry exists at --rev and opens with `source:`, `verified-at:`, `recheck:` in its
     first 8 lines (provenance trio, CORPUS.md).
  L2 entry carries a `ground: F1` line (coverage-map ground).
  L3 every `S\d{3,}` id the entry's `source:` line cites exists as a registry row in
     corpus/SOURCES.md at --rev with status `mined` and `used-by` containing the entry path.
  L4 (record legs only) the record exists at --rev, is well-formed (`REPO\t<name>\tregs=\d+\tprunable=\d+`
     rows plus one `TOTAL\trepos=\d+\tregs=\d+\tprunable=\d+` footer, >= 20 repos).
  L5 (record legs only) the entry's body contains the record's TOTAL regs and prunable
     integers verbatim (the entry cannot carry a figure the record does not prove).
  L6 sources-census validates at --rev: `sources-census.sh validate --root <fleet> souji`
     exits 0 (warnings allowed). Runs against the live lane root; a CNE on a missing lane
     checkout is a counter failure, not a pass.

SUMMARY entries=<n> legs=<m> fail=<f> rev=<r>; exit 0 iff fail=0.
do-nothing: at --rev <base> (pre-entry) the entry legs FAIL (absent entry) — the target is
not reachable without the work.
"""
import argparse
import os
import re
import subprocess
import sys

FULL = re.compile(r"[0-9a-f]{40}")
LEGS = "census/round-35/c3-legs.tsv"


def git(root, *a, check=True):
    p = subprocess.run(["git", "-C", root, "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", *a],
                       capture_output=True)
    if check and p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace").strip())
    return p


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def cne(msg):
    print("COULD-NOT-EVALUATE " + msg)
    return 2


def load_legs(root, list_rev):
    raw = blob(root, list_rev, LEGS)
    if raw is None:
        raise ValueError("legs absent at --list-rev")
    out = []
    for line in raw.decode().splitlines():
        if not line or line.startswith("#") or line.startswith("entry\t"):
            continue
        f = line.split("\t")
        if len(f) != 2:
            raise ValueError("malformed leg: " + line)
        out.append((f[0].strip(), f[1].strip()))
    if not out:
        raise ValueError("empty legs file")
    return out


def registry_rows(root, rev):
    """{sid: {'status': s, 'usedby': str}} for SOURCES.md rows at rev."""
    raw = blob(root, rev, "corpus/SOURCES.md") or b""
    rows = {}
    for ln in raw.decode("utf-8", "replace").splitlines():
        m = re.match(r"^ {0,3}\|\s*(S\d{3,})\s*\|", ln)
        if not m:
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) != 11:
            continue
        rows[m.group(1)] = {"status": cells[7], "usedby": cells[10]}
    return rows


def leg_entry(path, entry, rows, root, rev):
    text = entry.decode("utf-8", "replace")
    head = text.splitlines()[:8]
    if len(head) < 3 or not head[0].startswith("source:") or \
       not any(l.startswith("verified-at:") for l in head) or \
       not any(l.startswith("recheck:") for l in head):
        return [("L1", False, "provenance trio missing or out of order in first 8 lines")]
    out = [("L1", True, "provenance trio in first 8 lines")]
    out.append(("L2", bool(re.search(r"^ground:\s*F1\b", text, re.M)), "ground: F1"))
    sids = re.findall(r"S\d{3,}", head[0])
    bad = []
    for s in sids:
        row = rows.get(s)
        if row is None:
            bad.append(f"{s}:absent")
        elif row["status"] != "mined":
            bad.append(f"{s}:status={row['status']}")
        elif path not in row["usedby"]:
            bad.append(f"{s}:used-by-missing")
    out.append(("L3", not bad and bool(sids), " ".join(bad) if bad else f"{len(sids)} rows mined+used-by"))
    return out


def leg_record(path, entry, record, root, rev):
    raw = blob(root, rev, record)
    if raw is None:
        return [("L4", False, f"record {record} absent at rev"), ("L5", False, "no record")]
    lines = [l for l in raw.decode("utf-8", "replace").splitlines() if l.startswith("REPO\t") or l.startswith("TOTAL\t")]
    repos = [l for l in lines if l.startswith("REPO\t")]
    total = [l for l in lines if l.startswith("TOTAL\t")]
    well = len(repos) >= 20 and len(total) == 1 and \
        all(re.match(r"^REPO\t\S+\tregs=\d+\tprunable=\d+$", l) for l in repos) and \
        re.match(r"^TOTAL\trepos=\d+\tregs=\d+\tprunable=\d+$", total[0])
    out = [("L4", bool(well), f"repos={len(repos)} totals={len(total)} well={bool(well)}")]
    if not well:
        out.append(("L5", False, "record malformed"))
        return out
    m = re.match(r"^TOTAL\trepos=(\d+)\tregs=(\d+)\tprunable=(\d+)$", total[0])
    regs, prunable = m.group(2), m.group(3)
    text = entry.decode("utf-8", "replace")
    has = (regs in text) and (prunable in text)
    out.append(("L5", has, f"TOTAL regs={regs} prunable={prunable} in-entry={has}"))
    return out


def main():
    ap = argparse.ArgumentParser(prog="c3-counter.py")
    ap.add_argument("--root")
    ap.add_argument("--rev")
    ap.add_argument("--list-rev")
    ap.add_argument("--fleet-root", default="/home/vgpnk/Projects/shokunin")
    a = ap.parse_args()
    if not all((a.root, a.rev, a.list_rev)):
        return cne("required arguments missing")
    root = os.path.abspath(a.root)
    for x in (a.rev, a.list_rev):
        if not FULL.fullmatch(x):
            return cne("revision must be full 40 hex")
    legs = load_legs(root, a.list_rev)
    rows = registry_rows(root, a.rev)
    results = []
    for entry_path, record in legs:
        entry = blob(root, a.rev, entry_path)
        if entry is None:
            for tag in ("L1", "L2", "L3"):
                results.append((entry_path, tag, False, "entry absent at rev"))
            if record != "-":
                results.append((entry_path, "L4", False, "entry absent at rev"))
                results.append((entry_path, "L5", False, "entry absent at rev"))
            continue
        results += [(entry_path, t, ok, d) for t, ok, d in leg_entry(entry_path, entry, rows, root, a.rev)]
        if record != "-":
            results += [(entry_path, t, ok, d) for t, ok, d in leg_record(entry_path, entry, record, root, a.rev)]
    census = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"
    p = subprocess.run([census, "validate", "--root", a.fleet_root, "souji"], capture_output=True, text=True)
    results.append(("SOURCES.md", "L6", p.returncode == 0, f"census rc={p.returncode}"))
    failed = 0
    for ep, tag, ok, d in results:
        failed += not ok
        print(f"LEG\t{ep}\t{tag}\t{'PASS' if ok else 'FAIL'}\t{d}")
    print(f"SUMMARY entries={len(legs)} legs={len(results)} fail={failed} rev={a.rev}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
