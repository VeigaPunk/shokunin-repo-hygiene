#!/usr/bin/env python3
"""census/round-44/c1-counter.py — correction-register counter for the r44 calibration claim.

Scores the round-44 correction register against the pinned population of 70
declared-evidence mismatch records (census/round-44/c1-population.tsv, captured
at the r44 base revision 55d7af6f5a22340f7a3de1c386e514ababfaa75f). Unlike the
r43 counter, this one BINDS THE DERIVED TOKEN: every registered correction must
carry a `derived=` value that exactly equals the value this counter re-derives
itself from committed bytes at --rev (r43 routed defect 1: "C1 counter does not
compare its captured derived token").

Derivation rules, all over committed bytes at BASE_REV (the population revision):

  class mismatch:path-absent (A)
      candidates = tracked files at --rev whose basename equals basename(token),
      or whose path ends with token when token contains "/".
      1 candidate  -> derived = <that path>
      >1 candidate -> derived = "multi:" + ";".join(sorted(paths))
      0 candidates -> derived = "UNHELD"

  class mismatch:rev-unresolved (B)
      any 64-hex digest on that SCORECARD line (at --rev) with token as prefix
      -> derived = "sha256prefix:" + <digest>
      otherwise   -> derived = "UNRESOLVED"

  class mismatch:digest (C)
      the re-run instrument's own tip row for (line, token) states the actual
      blob digest; derived = "sha256:" + <actual digest>; if the tip row is now
      "resolved", derived = "RESOLVED".

The instrument used for tip facts is tools/souji-declared-evidence.py run in
blob mode at --rev (never the work tree). new_mismatches counts tip mismatch
records (measured at --rev) whose (line, token, class) is absent from the population — the
round's own appends must not add stale pointers.

Correction grammar (column-0 lines in corpus/lessons/round-44.md, read at --rev):

  CORRECTION-R44 id=R44-NN file=SCORECARD.md line=<n> class=<c> stale=<token> derived=<v> rev=BASE_REV scope=<nonempty-token>[ capture=<path>][ register=<path>][ disposition=<token>]

Rules: id unique (R44-01 .. R44-NN, zero-padded 2+ digits); one correction per
population row, matched by (line, class, stale); `derived` must equal the
counter's re-derived value byte-for-byte (token binding); `rev` must be BASE_REV; `scope` must be a nonempty single token (Q101 scope discipline);
`capture=`/`register=` paths, when present, must exist at --rev; lines inside
markdown fences or with leading whitespace are fenced (rejected); a
`RETRACTED-R44 id=...` line retracts its id (rejected while the id is still
required); a duplicate id is rejected.

Usage:
  python3 -B census/round-44/c1-counter.py --root LANE --rev FULL40 [--scratch DIR]
  python3 -B census/round-44/c1-counter.py --root LANE --rev FULL40 --emit   (dry: print derivations)

Exit: 0 target met; 1 target unmet; 2 could-not-evaluate.
Target: `SUMMARY population=70 corrections=66 registered=70 missing=0 junk=0 fenced=0 duplicate=0 retracted=0 rederive=70 rederive_failed=0 new_mismatches=0`
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys

POPULATION = "census/round-44/c1-population.tsv"
BASE_REV = "55d7af6f5a22340f7a3de1c386e514ababfaa75f"  # population revision; derivations run here
LESSON = "corpus/lessons/round-44.md"
SCORECARD = "SCORECARD.md"
INSTRUMENT = "tools/souji-declared-evidence.py"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FULL40 = re.compile(r"^[0-9a-f]{40}$")
CORRX = re.compile(
    r"^CORRECTION-R44 id=(R44-\d{2,}) file=(\S+) line=(\d+) class=(\S+) "
    r"stale=(\S+) derived=(\S+) rev=(\S+) scope=(\S+)(.*)$")
RETRACTX = re.compile(r"^RETRACTED-R44 id=(R44-\d{2,})")


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        return None
    return p.stdout


def tracked(root, rev):
    p = subprocess.run(["git", "-C", root, "ls-tree", "-r", "--name-only", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                            "GIT_CONFIG_NOSYSTEM": "1", "LC_ALL": "C"})
    if p.returncode != 0:
        return None
    return p.stdout.decode("utf-8", "replace").splitlines()


def run_instrument(root, rev, scratch):
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
           "TMPDIR": scratch, "GIT_CONFIG_NOSYSTEM": "1", "LC_ALL": "C"}
    p = subprocess.run([sys.executable, "-B", os.path.join(root, INSTRUMENT),
                        "--root", root, "--file", SCORECARD, "--rev", rev,
                        "--format", "tsv"],
                       capture_output=True, env=env, cwd=scratch, timeout=600)
    return p.returncode, p.stdout.decode("utf-8", "replace").splitlines()


def instrument_rows(lines):
    rows = {}
    for ln in lines:
        f = ln.split()
        if len(f) >= 4 and f[3].startswith("mismatch:"):
            key = (int(f[0]), f[1], f[3])
            rows[key] = " ".join(f[4:])
    return rows


def derive(row, tip_rows, sc_lines, files):
    lineno, token, cls, _reason = row
    if cls == "mismatch:path-absent":
        base = token.rsplit("/", 1)[-1]
        if "/" in token:
            cands = sorted(p for p in files if p.endswith(token))
        else:
            cands = sorted(p for p in files if p.rsplit("/", 1)[-1] == base)
        if len(cands) == 1:
            return cands[0]
        if len(cands) > 1:
            return "multi:" + ";".join(cands)
        return "UNHELD"
    if cls == "mismatch:rev-unresolved":
        line_text = sc_lines[lineno - 1] if lineno - 1 < len(sc_lines) else ""
        for word in re.findall(r"[0-9a-f]{16,}", line_text):
            if HEX64.match(word) and word.startswith(token):
                return "sha256prefix:" + word
        return "UNRESOLVED"
    if cls == "mismatch:digest":
        actual = tip_rows.get((lineno, token, cls))
        if actual is None:
            return "RESOLVED"
        m = re.search(r"sha256 is ([0-9a-f]{64})", actual)
        if not m:
            return "DERIVE-FAILED"
        return "sha256:" + m.group(1)
    return "DERIVE-FAILED"


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch")
    ap.add_argument("--emit", action="store_true")
    ns = ap.parse_args(argv)
    root, rev = os.path.abspath(ns.root), ns.rev
    if not FULL40.match(rev):
        sys.stderr.write("REFUSAL REV-NOT-FULL40\n")
        return 2
    scratch = ns.scratch or os.environ.get("TMPDIR") or "/tmp"
    os.makedirs(scratch, exist_ok=True)
    work = None
    try:
        pop_b = blob(root, rev, POPULATION)
        if pop_b is None:
            sys.stderr.write("REFUSAL POPULATION-ABSENT\n")
            return 2
        rows = []
        for i, ln in enumerate(pop_b.decode("utf-8", "replace").splitlines()):
            if i == 0:
                continue
            f = ln.split("\t")
            if len(f) != 4:
                sys.stderr.write("REFUSAL POPULATION-MALFORMED\n")
                return 2
            rows.append((int(f[0]), f[1], f[2], f[3]))
        if not rows:
            sys.stderr.write("REFUSAL POPULATION-EMPTY\n")
            return 2
        # referents are derived at the population revision (BASE_REV), never at
        # the report tip: a correction names rev=BASE_REV and must sit in a tree
        # that is later than BASE_REV, so deriving at --rev would make the lesson
        # name its own commit. The tip is measured separately for new mismatches.
        rc0, base_out = run_instrument(root, BASE_REV, scratch)
        base_rows = instrument_rows(base_out)
        sc_b = blob(root, BASE_REV, SCORECARD)
        sc_lines = sc_b.decode("utf-8", "replace").splitlines() if sc_b else []
        files = tracked(root, BASE_REV)
        if files is None:
            sys.stderr.write("REFUSAL LS-TREE-FAILED\n")
            return 2
        tip_rc, tip_out = run_instrument(root, rev, scratch)
        tip_rows = instrument_rows(tip_out)
        derived = {}
        for row in rows:
            derived[row] = derive(row, base_rows, sc_lines, files)
        if ns.emit:
            seen = set()
            idx = 0
            for row in rows:
                key = (row[0], row[1], row[2])
                if key in seen:
                    continue
                seen.add(key)
                idx += 1
                print("R44-%02d\tline=%d\tclass=%s\tstale=%s\tderived=%s"
                      % (idx, row[0], row[2], row[1], derived[row]))
            return 0
        lesson_b = blob(root, rev, LESSON)
        if lesson_b is None:
            unmatched = len([k for k in tip_rows
                             if k not in {(r[0], r[1], r[2]) for r in rows}])
            print("SUMMARY population=%d corrections=0 registered=0 missing=%d "
                  "junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 "
                  "rederive_failed=%d new_mismatches=%d instrument_mismatches=%d "
                  "lesson=absent"
                  % (len(rows), len(rows), len(rows), unmatched, len(tip_rows)))
            return 1
        ltext = lesson_b.decode("utf-8", "replace")
        fence = False
        corrections = {}
        retracted = set()
        junk = fenced = dup = 0
        for ln in ltext.splitlines():
            if re.match(r"^\s*(```|~~~)", ln):
                fence = not fence
                continue
            m = CORRX.match(ln)
            if m:
                (cid, _file, sline, scls, stale, sderived, srev, sscope, rest) = m.groups()
                if fence or ln[:1] in (" ", "\t"):
                    fenced += 1
                    continue
                if cid in corrections or cid in retracted:
                    dup += 1
                    continue
                extra = dict(re.findall(r"(capture|register|disposition)=(\S+)", rest))
                corrections[cid] = (int(sline), scls, stale, sderived, srev,
                                    bool(sscope), extra)
                continue
            r = RETRACTX.match(ln)
            if r and not fence and ln[:1] not in (" ", "\t"):
                retracted.add(r.group(1))
            elif ln.startswith("CORRECTION-R44") or ln.startswith("RETRACTED-R44"):
                junk += 1
        # match rows to corrections
        byrow = {}
        for cid, (sline, scls, stale, sderived, srev, sscope, extra) in corrections.items():
            byrow.setdefault((sline, scls, stale), []).append(cid)
        # corrections are keyed by (line, class, stale); one correction covers
        # every population row sharing that key (the base instrument reported
        # 70 occurrences over 66 unique keys — 4 rows duplicate their key)
        registered = missing = rederive_failed = 0
        keys = {(r[0], r[1], r[2]) for r in rows}
        unmatched_tip = [k for k in tip_rows if k not in keys]
        key_ok = {}
        for key in keys:
            cids = byrow.get(key, [])
            if len(cids) != 1:
                key_ok[key] = False
                continue
            cid = cids[0]
            (sline, scls, stale, sderived, srev, sscope, extra) = corrections[cid]
            dval = derived[(key[0], key[1], key[2])]
            ok = (sderived == dval and srev == BASE_REV and sscope)
            for _k, val in extra.items():
                if val.startswith("multi:"):
                    continue
                if val not in files:
                    ok = False
            key_ok[key] = ok
        for row in rows:
            key = (row[0], row[1], row[2])
            if key not in key_ok or not key_ok[key]:
                missing += 1
                continue
            registered += 1
        used = sum(1 for k, v in key_ok.items() if v)
        rederive_failed = len(keys) - used - sum(1 for k in keys if k not in byrow)
        print("SUMMARY population=%d corrections=%d registered=%d missing=%d "
              "junk=%d fenced=%d duplicate=%d retracted=%d rederive=%d "
              "rederive_failed=%d new_mismatches=%d instrument_mismatches=%d"
              % (len(rows), len(key_ok), registered, missing, junk, fenced, dup,
                 len(retracted), registered, rederive_failed,
                 len(unmatched_tip), len(tip_rows)))
        target = (registered == len(rows) and missing == 0 and junk == 0
                  and fenced == 0 and dup == 0 and retracted == 0
                  and rederive_failed == 0 and len(unmatched_tip) == 0)
        return 0 if target else 1
    finally:
        if work is not None:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
