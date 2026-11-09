#!/usr/bin/env python3
"""R95ScoutSources — replicate the fleet sources-census validate rules for the
five new rows S360-S364 (read-only over the lane's committed SOURCES.md).

Implements exactly the checks the fleet script's `validate` mode applies to a
registry row (E01/E02/E03/E04/W04/E05/E06/E07), because the lane's own
census-before record predates P1 and does not cover the new rows.

url_of(): the fleet's own normalization — take the first https?:// URL, drop
the fragment, drop a trailing slash, lowercase the host.
"""
import re
import sys
from collections import Counter

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
NEW = {"S360", "S361", "S362", "S363", "S364"}

URL_RE = re.compile(r"https?://[^\s|]+")
KINDS = {"spec", "docs", "paper", "code", "tool", "dataset", "talk", "book",
         "community", "own-work"}


def url_of(source):
    m = URL_RE.search(source)
    if not m:
        return ""
    u = m.group(0)
    u = re.sub(r"#.*$", "", u)
    u = re.sub(r"/$", "", u)
    u = re.sub(r"^[A-Za-z]+://", "", u)
    n = u.find("/")
    if n:
        u = u[:n].lower() + u[n:]
    else:
        u = u.lower()
    return u


def main():
    rows = []
    in_registry = False
    with open(f"{LANE}/corpus/SOURCES.md", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if re.match(r"^ {0,3}##[ \t]", line):
                in_registry = line.lstrip().strip("# \t") == "Registry"
                continue
            if re.match(r"^ {0,3}#[ \t]", line):
                in_registry = False
                continue
            if not line.lstrip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) != 11:
                if in_registry and re.match(r"^S\d{3,}$", cells[0] if cells else ""):
                    print(f"E01\t{line}")
                continue
            rid, source, kind, tier, scope, anchor, teaches, status, opened, recheck, usedby = cells
            if not in_registry:
                continue
            rows.append(dict(id=rid, source=source, kind=kind, tier=tier, scope=scope,
                             anchor=anchor, teaches=teaches, status=status, opened=opened,
                             recheck=recheck, usedby=usedby))

    findings = []
    seen = set()
    url_seen = set()
    url_scopes = set()
    url_scope_nonrejected = set()
    for r in rows:
        rid = r["id"]
        u = url_of(r["source"])
        scope_key = (u, r["scope"])
        if rid in seen:
            findings.append(f"E03\t{rid} duplicate id")
        seen.add(rid)
        if u and u in url_seen and scope_key not in url_scopes:
            findings.append(f"W04\t{rid} duplicate url {u} across scopes")
        if (u and scope_key in url_scopes and r["status"] != "rejected"
                and scope_key in url_scope_nonrejected
                and not re.search(r"supersedes S\d{3}", r["teaches"])):
            findings.append(f"E04\t{rid} duplicate url {u} within scope {r['scope']}")
        if u:
            url_seen.add(u)
            url_scopes.add(scope_key)
            if r["status"] != "rejected":
                url_scope_nonrejected.add(scope_key)
        if r["kind"] not in KINDS:
            findings.append(f"E05\t{rid} kind={r['kind']}")
        if r["tier"] not in ("A", "B", "C"):
            findings.append(f"E06\t{rid} tier={r['tier']}")
        if r["status"] not in ("queued", "mined", "rejected"):
            findings.append(f"E07\t{rid} status={r['status']}")
        if r["status"] == "mined":
            for p in re.split(r"[,;]", r["usedby"]):
                p = p.strip()
                if p and p != "—":
                    import os
                    if not os.path.exists(os.path.join(LANE, p)):
                        findings.append(f"E08\t{rid} used-by path missing: {p}")

    print(f"rows={len(rows)}")
    counts = Counter(r["id"] for r in rows)
    print(f"duplicate_ids={[k for k,v in counts.items() if v>1]}")
    print("--- findings touching S360-S364 ---")
    touch = [f for f in findings if f.split("\t")[1].split()[0] in NEW]
    for f in touch:
        print(f)
    print(f"new_row_findings={len(touch)} total_findings={len(findings)}")
    print("--- all findings (context) ---")
    for f in findings:
        print(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
