#!/usr/bin/env python3
"""R42w2reviewer09 — attribution pass over the low-coverage rows of check.py.

For each resolved row whose cell tokens were not found in the resolved file:
  * enumerate every file path the SAME cell names (backticked, path-shaped);
  * for each missing token, look for it in each of those sibling paths' bytes
    (at the base and at the tip);
  * try shape variants of the missing token (N/N -> cases=N pass=N, "=N" forms,
    tuple forms (N, N), sha256 -> any 16-hex prefix of the same length).

Output: attribution.tsv. Read-only; no writes outside the seat directory.
"""
import json
import os
import re
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "bf618f6c5c09d302994871c94903abbea2deb60d"
TIP = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2reviewer09"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}

PATHISH = re.compile(r"`([^`\s]+)`")
EXTS = (".tsv", ".txt", ".md", ".py", ".sh", ".json", ".html", ".csv")


def show(rev, path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (rev, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env={**os.environ, **GIT_ENV}, check=False)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def siblings(cells):
    """Every path-shaped token named in the cell (with or without backticks)."""
    out = []
    for c in cells:
        for m in PATHISH.finditer(c):
            t = m.group(1)
            if t.endswith(EXTS) or "/" in t:
                out.append(t)
    # also bare basenames that look like records
    for c in cells:
        for t in re.findall(r"(?<![\w/.])[\w.\-]+\.(?:tsv|txt|md|py|sh|json)(?![\w/])", c):
            out.append(t)
    return sorted(set(out))


def expand(tree):
    """All tree paths (base) so basenames can be expanded to candidates."""
    p = subprocess.run(["git", "-C", LANE, "ls-tree", "-r", "--name-only", BASE],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env={**os.environ, **GIT_ENV}, check=False)
    return p.stdout.decode("utf-8", "replace").split("\n")


TREE = expand(None)


def candidates(name):
    if name in TREE:
        return [name]
    return sorted(p for p in TREE if p.endswith("/" + name))


def variants(tok, shape):
    """Shape-tolerant restatements of a missing token."""
    out = []
    if shape == "frac":
        a, b = tok.split("/")
        out.append("cases=%s pass=%s" % (a, b))
        out.append("cases=%s" % a)
        out.append("pass=%s" % b)
        out.append("(%s, %s)" % (a, b))
        out.append("new=(%s, %s)" % (a, b))
        out.append("(%s,%s)" % (a, b))
        out.append("sites=%s" % a)
        out.append("survived=%s" % b)
        out.append("legs=%s" % a)
    elif shape == "eq":
        k, v = tok.split("=", 1)
        out.append("%s=%s" % (k, v))
    elif shape == "hex":
        out.append(tok[:16])
        out.append(tok[:12])
        out.append(tok[:8])
    return out


def main():
    rows = json.load(open(os.path.join(SEAT, "coverage.json")))
    low = [r for r in rows if r["coverage_pct"] < 100]
    cache = {}

    def blob(rev, path):
        if (rev, path) not in cache:
            cache[(rev, path)] = show(rev, path)
        return cache[(rev, path)]

    with open(os.path.join(SEAT, "attribution.tsv"), "w") as h:
        h.write("line\ttoken\tresolved_to\tsibling_path\twhere\tmissing_token\tvariant_hit\n")
        for r in low:
            sibs = siblings(r["cells"])
            cands = []
            for s in sibs:
                cands.extend(candidates(s))
            cands = sorted(set(cands))
            for t in r["tokens"]:
                if t["state"] == "found":
                    continue
                where = []
                variant_hit = ""
                for c in cands:
                    for rev in (BASE, TIP):
                        b = blob(rev, c)
                        if b is None:
                            continue
                        if t["token"] in b:
                            where.append("%s@%s" % (c, rev[:12]))
                if not where:
                    for c in cands:
                        for rev in (BASE, TIP):
                            b = blob(rev, c)
                            if b is None:
                                continue
                            for v in variants(t["token"], t["shape"]):
                                if v in b:
                                    where.append("%s@%s[var]" % (c, rev[:12]))
                                    variant_hit = v
                                    break
                            if variant_hit:
                                break
                if not where:
                    where = ["UNATTRIBUTED"]
                for w in where:
                    h.write("%d\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                        r["line"], r["token"], r["resolved_to"], w.split("@")[0],
                        w, t["token"], variant_hit))
    print("attribution rows written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
