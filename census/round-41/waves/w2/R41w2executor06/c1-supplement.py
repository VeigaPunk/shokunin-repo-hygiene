#!/usr/bin/env python3
"""c1-supplement.py - independent r41 C1 checks the frozen c1-counter.py lacks.

  python3 -B c1-supplement.py --root LANE --rev FULL40 [--base FULL40]

Checks (one line each, then SUMMARY; exit 0 only if all pass, 1 if any fails, 2 if unresolvable):
  K1 CORRECTION lines (start of line, optionally indented / quoted) lie outside code fences, are
     exactly three (I1,I3,I4), each id once, no line text repeated.
  K2 corpus/SOURCES.md at --rev only gains lines over --base: every old line byte-identical and in
     order (old lines are a subsequence of new lines), old content ended in a newline. The insertions
     need not sit at end of file (the registry has a table, then sections); tail_append= reports
     whether they do.
  K3 the S258 row: exactly one at --rev, 11 cells, its double-quoted quote occurs verbatim in the
     snapshot named by the row, and sha256(snapshot at --rev) equals the sha256 the row states.
  K4 corpus/lessons/round-40.md, SCORECARD.md, LOG.md at --rev begin with their --base bytes.
Reads only git objects (git show); writes nothing.
"""
import argparse, hashlib, os, re, subprocess, sys

BASE = "bffcc0f660ff36eb8add3f61582748a7af019a5b"
ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_TERMINAL_PROMPT": "0", "PATH": os.environ.get("PATH", "")}
LESSON, REG = "corpus/lessons/round-41.md", "corpus/SOURCES.md"
APPEND_ONLY = ["corpus/lessons/round-40.md", "SCORECARD.md", "LOG.md"]


def show(root, rev, path):
    p = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=ENV)
    return p.stdout if p.returncode == 0 else None


def k1(root, rev, base):
    raw = show(root, rev, LESSON)
    if raw is None:
        return False, "lesson %s absent at rev" % LESSON
    fence = None  # (char, length)
    outside, inside = [], 0
    for n, line in enumerate(raw.decode("utf-8", "replace").splitlines(), 1):
        m = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence is None:
            if m:
                fence = (m.group(1)[0], len(m.group(1)))
                continue
        else:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] \
                    and line.strip() == m.group(1):
                fence = None
            elif re.match(r"^[\s>*-]*CORRECTION\s", line):
                inside += 1
            continue
        if re.match(r"^[\s>*-]*CORRECTION\s", line):
            outside.append((n, line))
    ids = [(re.match(r"^[\s>*-]*CORRECTION\s+(\S+)", l).group(1)) for _, l in outside]
    texts = [l.strip() for _, l in outside]
    dup_ids = sorted({i for i in ids if ids.count(i) > 1})
    dup_text = len(texts) - len(set(texts))
    ok = (inside == 0 and fence is None and sorted(ids) == ["I1", "I3", "I4"] and not dup_ids and dup_text == 0)
    return ok, "outside=%d inside_fence=%d ids=%s dup_ids=%s dup_text=%d unclosed_fence=%s" % (
        len(outside), inside, ",".join(ids), ",".join(dup_ids) or "-", dup_text, fence is not None)


def k2(root, rev, base):
    old, new = show(root, base, REG), show(root, rev, REG)
    if old is None or new is None:
        return False, "registry absent (base=%s rev=%s)" % (old is not None, new is not None)
    a, b = old.splitlines(True), new.splitlines(True)
    # every old line byte-identical and in order: old is a subsequence of new (greedy match is exact
    # for subsequence existence); a changed, removed or reordered old line leaves a line unmatched.
    j, first_bad = 0, None
    for i, line in enumerate(a):
        while j < len(b) and b[j] != line:
            j += 1
        if j == len(b):
            first_bad = i + 1
            break
        j += 1
    tail = new.startswith(old)
    ok = first_bad is None and (len(old) == 0 or old.endswith(b"\n"))
    return ok, "old_lines=%d new_lines=%d inserted_lines=%d unmatched_old_line=%s tail_append=%s" % (
        len(a), len(b), len(b) - len(a), first_bad if first_bad else "-", tail)


def k3(root, rev, base):
    raw = show(root, rev, REG)
    if raw is None:
        return False, "registry absent"
    rows = [l for l in raw.decode("utf-8", "replace").splitlines() if re.match(r"^\|\s*S258\s*\|", l)]
    if len(rows) != 1:
        return False, "S258 rows=%d" % len(rows)
    cells = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    if len(cells) != 11:
        return False, "cells=%d" % len(cells)
    q = re.search(r'"([^"]+)"', cells[6])
    sp = re.search(r"`(census/round-41/sources/[^`]+)` sha256 ([0-9a-f]{64})", cells[5])
    if not q or not sp:
        return False, "cells=11 quote_found=%s snapshot_sha_found=%s" % (bool(q), bool(sp))
    snap = show(root, rev, sp.group(1))
    if snap is None:
        return False, "cells=11 snapshot %s absent at rev" % sp.group(1)
    digest = hashlib.sha256(snap).hexdigest()
    occ = snap.count(q.group(1).encode("utf-8"))
    ok = occ >= 1 and digest == sp.group(2)
    return ok, "cells=11 quote_occurrences=%d sha_match=%s snapshot=%s" % (occ, digest == sp.group(2), sp.group(1))


def k4(root, rev, base):
    res, ok = [], True
    for p in APPEND_ONLY:
        old, new = show(root, base, p), show(root, rev, p)
        good = old is not None and new is not None and new.startswith(old)
        ok &= good
        res.append("%s=%s" % (p, "prefix" if good else "BROKEN"))
    return ok, " ".join(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", default=BASE)
    a = ap.parse_args()
    for r in (a.rev, a.base):
        if subprocess.run(["git", "-C", a.root, "cat-file", "-e", r + "^{commit}"], env=ENV,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s does not resolve\n" % r)
            return 2
    passed = 0
    for name, fn in (("K1-corrections-fence-dup", k1), ("K2-sources-insert-only", k2),
                     ("K3-S258-row-quote-sha", k3), ("K4-r40-files-prefix", k4)):
        ok, detail = fn(a.root, a.rev, a.base)
        passed += ok
        print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    print("SUMMARY checks=4 pass=%d fail=%d rev=%s" % (passed, 4 - passed, a.rev))
    return 0 if passed == 4 else 1


sys.exit(main())
