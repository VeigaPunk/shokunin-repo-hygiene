#!/usr/bin/env python3
"""r23-record-agreement.py — fixture (oracle) for tools/souji-record-agreement.py, round-23 C1.

Exercises the frozen instrument CLI:

    python3 tools/souji-record-agreement.py --root <repo> [--rev <full40>] [--json <path>]

Counts line on stdout: keys=K records=R occurrences=O mismatches=M  (exit 0 iff M==0)
Mismatch rows:         MISMATCH<TAB><key><TAB><record><TAB><class><TAB><detail>

It builds a synthetic lane repo under /var/tmp (hard-coded; never /tmp), trap-cleaned on exit,
runs the instrument against it and prints one `case=<n> expect=<...> got=<...>` line per case,
then `selftest=<pass>/<total>`, then the always-zero control verdict. Exit 0 iff every case
observes its expectation.

Frozen paths the synthetic repo carries (preregistration C1):
  SCORECARD.md                                           K1 record: r22 after 4-tuple + rev token
  census/round-23/records/declared-evidence-after.tsv    K1 receipt: counts line + rev= header
  LOG.md                                                 K2 record: "Round22 attempt2" section
  census/round-22/attempt2/declared-evidence-before.tsv  K2 receipt
  census/round-22/attempt2/slice-verdicts.tsv            K3 receipt
  corpus/README.md, corpus/lessons/round-22.md           K3 records
  census/round-23/records/uncommitted-exemptions.tsv      K4 exemption allowlist (path<TAB>reason)

Two-commit shape. A commit cannot contain its own object id, so the K1 receipt cannot name the
revision that carries it. The repo is therefore built as: commit 1 = the measured revision
(carries the files with a placeholder token), commit 2 = the tip (--rev) carrying the receipt
whose `rev=` header and whose SCORECARD line both name commit 1. That is the only shape the
frozen contract admits ("the revision token on that same physical line must equal the receipt's
rev= header, and the receipt must exist in the tree at --rev"): the token binds the *measured*
revision, the tree binding is satisfied at the tip.

The LOG fixture mirrors the physical shape of the real entry (LOG.md:1469 header, :1470 `=`-rule
on the very next line, :1484-1485 4-tuple wrapped across two lines) because that is the file the
instrument must run on, not an idealised one. A decoy tuple in the preamble sits outside the
section and must not be scanned.

Cases 2-8 are the always-zero control: each demands >=1 mismatch of a named class, so an emitter
that always prints `mismatches=0` fails every one of them.
"""
from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys

sys.dont_write_bytecode = True

SCRATCH_ROOT = "/var/tmp/souji-r23-ExecFixtureAgreement"
TOOL_REL = os.path.join("tools", "souji-record-agreement.py")

# Frozen paths (preregistration C1) — code constants, never data.
K1_RECEIPT = "census/round-23/records/declared-evidence-after.tsv"
K1_RECORD = "SCORECARD.md"
K2_RECORD = "LOG.md"
K2_RECEIPT = "census/round-22/attempt2/declared-evidence-before.tsv"
# the lane holds both variants of the base receipt; the fixture writes both so the case does not
# depend on which one the instrument's frozen constant selects
K2_RECEIPT_FINAL = "census/round-22/attempt2/declared-evidence-before-final.tsv"
WAVE_NOTE = ".ufo/waves/round-23/w1/seat-notes.md"
K3_RECEIPT = "census/round-22/attempt2/slice-verdicts.tsv"
K3_RECORDS = ("corpus/README.md", "corpus/lessons/round-22.md")
K4_EXEMPT = "census/round-23/records/uncommitted-exemptions.tsv"
OPERATOR_DIR = "census/operator-sweep-20261019/"
OPERATOR_FILE = OPERATOR_DIR + "probe.out"
STRAY_PATH = ".ufo/waves/round-23/w1/evidence/impl-a/head-c9f1fe3.tsv"

AFTER_TUPLE = "assertions=63 resolved=63 skipped=40 mismatches=0"
AFTER_TUPLE_WRONG = "assertions=63 resolved=61 skipped=40 mismatches=2"
BEFORE_TUPLE = "assertions=55 resolved=52 skipped=33 mismatches=3"
FILED_TUPLE_HEAD = "assertions=56 resolved=53"        # wrapped on purpose: mirrors LOG.md:1484
FILED_TUPLE_TAIL = "skipped=33 mismatches=3"          # LOG.md:1485
WRONG_REV = "ab" * 20

COUNTS_OUT = re.compile(
    r"^keys=(\d+) records=(\d+) occurrences=(\d+) mismatches=(\d+)$", re.M)
SCANNED = re.compile(
    r"assertions=|resolved=|skipped=|mismatches=|"
    r"[0-9]+ (?:accepted|present|unverifiable|refused)")


# --------------------------------------------------------------------------- scratch lifecycle
def cleanup() -> None:
    shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)


def arm_traps() -> None:
    atexit.register(cleanup)
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        try:
            signal.signal(sig, lambda *_: (cleanup(), os._exit(130)))
        except (ValueError, OSError):
            pass


# --------------------------------------------------------------------------- git plumbing
def git_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    env.update({
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_AUTHOR_NAME": "souji-fixture", "GIT_AUTHOR_EMAIL": "fixture@shokunin.local",
        "GIT_COMMITTER_NAME": "souji-fixture", "GIT_COMMITTER_EMAIL": "fixture@shokunin.local",
        "GIT_AUTHOR_DATE": "2026-10-25T00:00:00Z", "GIT_COMMITTER_DATE": "2026-10-25T00:00:00Z",
        "LC_ALL": "C", "TZ": "UTC",
    })
    return env


def git(repo: str | None, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["git"]
    if repo is not None:
        cmd += ["-C", repo]
    cmd += ["-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
            "-c", "maintenance.auto=false", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=git_env())
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc


def commit(repo: str, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message, "--allow-empty")
    return git(repo, "rev-parse", "HEAD").stdout.strip()


# --------------------------------------------------------------------------- fixture payloads
def f_scorecard(rev: str) -> str:
    return (
        "# SCORECARD (synthetic fixture for r23 C1)\n"
        "\n"
        "| axis | score | note |\n"
        "|---|---|---|\n"
        f"| calibration | 7 | R22 **attempt 2** C1 after receipt measured at {rev}: "
        f"`{AFTER_TUPLE}`, re-derived from committed bytes at the tip. |\n"
        "| operability | 8 | unchanged |\n"
        "| coverage | 8 | unchanged |\n"
    )


def f_receipt_after(rev: str) -> str:
    return (
        "# r23 C1 after receipt (synthetic fixture): declared-evidence at the named revision\n"
        f"rev={rev}\n"
        f"{AFTER_TUPLE}\n"
        "3\tAXES.md\tA\tresolved\tpresent at the named revision\n"
        "14\t41553adb139d06511dc386bb3ce4326aebfba675\tB\tresolved\tcommit/object resolves\n"
    )


def f_receipt_before() -> str:
    return (
        "# r22 attempt2 declared-evidence before (synthetic fixture)\n"
        f"{BEFORE_TUPLE}\n"
        "3\tAXES.md\tA\tmismatch:path-absent\tnot in tree at the base revision\n"
        "14\t41553adb139d06511dc386bb3ce4326aebfba675\tB\tresolved\tcommit/object resolves\n"
    )


def f_slice_verdicts() -> str:
    rows = [
        ("S114", "accepted"), ("S118", "unverifiable"), ("S123", "accepted"),
        ("S124", "accepted"), ("S126", "present"), ("S131", "accepted"),
        ("S133", "accepted"), ("S138", "present"),
    ]
    head = ("# campaign register ids, not lane registry ids "
            "(mirrors census/round-22/attempt2/slice-verdicts.tsv)\n")
    return head + "".join(f"{i}\t{c}\tsynthetic verdict row\n" for i, c in rows)


def f_readme() -> str:
    return (
        "# corpus/README (synthetic fixture)\n"
        "\n"
        "## Round22 attempt 2\n"
        "\n"
        "Register slice (8 rows): 5 accepted with corrected quotes, 2 present, 1 unverifiable,\n"
        "0 refused. Verdict table: census/round-22/attempt2/slice-verdicts.tsv.\n"
    )


def f_lesson() -> str:
    return (
        "# Round 22 lesson (synthetic fixture)\n"
        "\n"
        "Slice: 5 accepted, 2 present, 1 unverifiable, 0 refused (receipt\n"
        "census/round-22/attempt2/slice-verdicts.tsv).\n"
    )


def f_exemptions() -> str:
    # the instrument reads a dedicated file whose rows are `path<TAB>reason`; the allowlist is a
    # frozen constant, so only an operator-owned path can ever be exempted
    return (
        "# uncommitted exemptions (synthetic fixture)\n"
        f"{OPERATOR_DIR}\toperator-owned untracked output, never committed or opened by the lane\n"
    )


def f_log() -> str:
    # Shape mirrors LOG.md: header line, '=' rule on the NEXT line, body after it, and the
    # 4-tuple wrapped across two lines (LOG.md:1484-1485).
    return (
        "# LOG (synthetic fixture for r23 C1)\n"
        "\n"
        f"Round21 (decoy, outside the scanned section): assertions=12 resolved=12 skipped=3 "
        "mismatches=0\n"
        "\n"
        "Round22 attempt2 (hyaku retry; synthetic fixture, mirrors LOG.md:1469)\n"
        "=============================================================\n"
        "Claim boundary. C1 declared-evidence audit. Base measurement\n"
        f"`--rev 4edb25d --file SCORECARD.md` -> {FILED_TUPLE_HEAD}\n"
        f"{FILED_TUPLE_TAIL} (receipt census/round-22/attempt2/\n"
        "declared-evidence-before.tsv). Register slice verdicts as filed: 1 present,\n"
        "1 refused (S123). Filed bytes are append-only: corrections are appended below.\n"
        "\n"
        "Round23 append-only correction (r23 C1, routed defect D5)\n"
        "=============================================================\n"
        f"{FILED_TUPLE_HEAD} {FILED_TUPLE_TAIL} superseded by {BEFORE_TUPLE}\n"
        "1 present superseded by 2 present; 1 refused superseded by 0 refused (S123)\n"
    )


def payload(rev: str) -> dict[str, str]:
    return {
        K1_RECEIPT: f_receipt_after(rev),
        K1_RECORD: f_scorecard(rev),
        K2_RECORD: f_log(),
        K2_RECEIPT: f_receipt_before(),
        K2_RECEIPT_FINAL: f_receipt_before(),
        K3_RECEIPT: f_slice_verdicts(),
        K3_RECORDS[0]: f_readme(),
        K3_RECORDS[1]: f_lesson(),
        K4_EXEMPT: f_exemptions(),
    }


def write_file(repo: str, rel: str, text: str) -> None:
    path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(path) or repo, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def rewrite(repo: str, rel: str, fn) -> None:
    path = os.path.join(repo, rel)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    write_file(repo, rel, fn(text))


# --------------------------------------------------------------------------- variants
def mutate(repo: str, variant: str) -> None:
    """Apply the case's defect. Committed mutations move the tip; worktree ones stay dirty."""
    if variant == "repaired":
        return
    if variant == "receipt-absent":
        os.unlink(os.path.join(repo, K1_RECEIPT))
        commit(repo, "case: receipt deleted (K1 receipt-absent)")
        return
    if variant == "counts-disagree":
        rewrite(repo, K1_RECORD, lambda t: t.replace(AFTER_TUPLE, AFTER_TUPLE_WRONG))
        commit(repo, "case: SCORECARD tuple disagrees with the receipt (K1 value-disagree)")
        return
    if variant == "rev-disagree":
        # Only the revision token moves; the tuple still equals the receipt.
        rewrite(repo, K1_RECORD, lambda t: re.sub(
            r"measured at [0-9a-f]{40}", "measured at " + WRONG_REV, t))
        commit(repo, "case: SCORECARD line names a token that is not the receipt rev= "
                     "(K1 rev-disagree)")
        return
    if variant == "unbound-tuple":
        # W2K1 F1: the rev token moves off the tuple's physical line AND the tuple is wrong.
        # A silently-dropped tuple would buy a green; the instrument must flag unbound-tuple.
        rewrite(repo, K1_RECORD, lambda t: re.sub(
            r"measured at [0-9a-f]{40}", "measured-on-another-line", t))
        rewrite(repo, K1_RECORD, lambda t: t.replace(AFTER_TUPLE, AFTER_TUPLE_WRONG))
        commit(repo, "case: unbound wrong tuple (K1 unbound-tuple)")
        return
    if variant == "uncorrected-log":
        rewrite(repo, K2_RECORD, lambda t: "".join(
            line for line in t.splitlines(keepends=True)
            if "superseded by" not in line))
        commit(repo, "case: correction lines removed (K2 uncorrected)")
        return
    if variant == "filed-deleted":
        def drop(text: str) -> str:
            out, in_section = [], False
            for line in text.splitlines(keepends=True):
                if line.startswith("Round22 attempt2"):
                    in_section = True
                elif line.startswith("Round23 append-only correction"):
                    in_section = False
                if in_section and SCANNED.search(line):
                    continue
                out.append(line)
            return "".join(out)
        rewrite(repo, K2_RECORD, drop)
        commit(repo, "case: filed LOG occurrence deleted (K2 filed bytes are append-only)")
        return
    if variant == "tally-wrong":
        rewrite(repo, K3_RECORDS[0], lambda t: t.replace("2 present", "1 present"))
        commit(repo, "case: README tally disagrees with slice-verdicts (K3 tally-disagree)")
        return
    if variant == "dirty-unexempted":
        write_file(repo, STRAY_PATH, "round work left in the working tree\n")
        return
    if variant == "class-missing":
        rewrite(repo, K3_RECORDS[0], lambda t: t.replace("unverifiable", "unknown"))
        commit(repo, "case: README loses a tally class (K3 class-absent)")
        return
    if variant == "tally-stale-log":
        # drop the correction line so the filed stale tally is uncovered: the K2 tally arm
        def drop_correction(t: str) -> str:
            return "".join(l for l in t.splitlines(True) if "superseded by 2 present" not in l)
        rewrite(repo, K2_RECORD, drop_correction)
        commit(repo, "case: LOG tally disagrees and its correction is gone (K2 tally arm)")
        return
    if variant == "exempted-dirty":
        write_file(repo, OPERATOR_FILE, "operator-owned, never committed\n")
        return
    raise SystemExit(f"fixture: unknown variant {variant!r}")


def build(variant: str) -> tuple[str, str]:
    """Create the repo for one case. Returns (repo_path, tip)."""
    repo = os.path.join(SCRATCH_ROOT, variant)
    os.makedirs(repo, exist_ok=True)
    git(None, "init", "-q", "-b", "master", repo)
    # commit 1 — the measured revision, carrying a placeholder token
    for rel, text in payload("0" * 40).items():
        write_file(repo, rel, text)
    write_file(repo, OPERATOR_FILE, "operator-owned, never committed\n")
    write_file(repo, WAVE_NOTE, "# wave seat notes (fixture)\n")
    measured = commit(repo, "measured revision (fixture)")
    # commit 2 — the tip carries the receipt/record bound to the measured revision
    for rel, text in payload(measured).items():
        write_file(repo, rel, text)
    commit(repo, "tip: receipts bound to the measured revision (fixture)")
    mutate(repo, variant)
    tip = git(repo, "rev-parse", "HEAD").stdout.strip()
    return repo, tip


# --------------------------------------------------------------------------- instrument driver
def run_tool(tool: str, repo: str, rev: str, json_path: str) -> dict:
    proc = subprocess.run(
        [sys.executable, tool, "--root", repo, "--rev", rev, "--json", json_path],
        capture_output=True, text=True, env=git_env())
    rows = []
    for line in proc.stdout.splitlines():
        if line.startswith("MISMATCH\t"):
            cells = line.split("\t")
            if len(cells) >= 5:
                rows.append({"key": cells[1], "record": cells[2],
                             "cls": cells[3], "detail": cells[4]})
    m = COUNTS_OUT.search(proc.stdout)
    counts = None
    if m:
        counts = {"keys": int(m.group(1)), "records": int(m.group(2)),
                  "occurrences": int(m.group(3)), "mismatches": int(m.group(4))}
    # --json is part of the frozen CLI: a run that does not bind the same line/rows to the
    # written file has not exercised the surface.
    json_ok = False
    try:
        with open(json_path, encoding="utf-8") as fh:
            doc = json.load(fh)
        json_ok = bool(
            counts is not None
            and doc.get("line") == m.group(0)
            and doc.get("rev") == rev
            and len(doc.get("mismatches", [])) == counts["mismatches"]
            and len(doc.get("mismatches", [])) == len(rows))
    except (OSError, ValueError):
        json_ok = False
    return {"rc": proc.returncode, "rows": rows, "counts": counts, "json_ok": json_ok,
            "stdout": proc.stdout, "stderr": proc.stderr, "json": json_path}


def classes(result: dict, key: str | None = None) -> list[str]:
    return [r["cls"] for r in result["rows"] if key is None or r["key"] == key]


def got_text(result: dict) -> str:
    c = result["counts"]
    counts = ("counts=None" if c is None
              else f"mismatches={c['mismatches']} keys={c['keys']}")
    seen = sorted({f"{r['key']}/{r['cls']}" for r in result["rows"]})
    return f"rc={result['rc']} {counts}" + (f" [{','.join(seen)}]" if seen else "")


# --------------------------------------------------------------------------- cases
def case_unbound(res: dict) -> tuple[bool, str]:
    have = classes(res, "K1")
    return ("unbound-tuple" in have and res["rc"] != 0,
            "rc!=0 K1 unbound-tuple>=1")


def case_repaired(res: dict) -> tuple[bool, str]:
    c = res["counts"]
    ok = (res["rc"] == 0 and c is not None and c["mismatches"] == 0
          and c["keys"] == 4 and not res["rows"] and res["json_ok"])
    return ok, "rc=0 mismatches=0 keys=4 json-bound"


def case_k1(res: dict, cls: str, forbid: tuple[str, ...] = ()) -> tuple[bool, str]:
    have = classes(res, "K1")
    ok = cls in have and res["rc"] != 0 and not any(f in have for f in forbid)
    expect = f"rc!=0 K1 {cls}>=1" + (f" {','.join(forbid)}=0" if forbid else "")
    return ok, expect


def case_k2(res: dict, prefix: str) -> tuple[bool, str]:
    have = classes(res, "K2")
    ok = any(h.startswith(prefix) for h in have) and res["rc"] != 0
    return ok, f"rc!=0 K2 {prefix}*>=1"


def case_k3(res: dict) -> tuple[bool, str]:
    have = classes(res, "K3")
    return ("tally-disagree" in have and res["rc"] != 0,
            "rc!=0 K3 tally-disagree>=1")


def case_k4_stray(res: dict) -> tuple[bool, str]:
    hits = [r for r in res["rows"]
            if r["key"] == "K4" and r["cls"] == "uncommitted-path"
            and r["record"].startswith(".ufo/waves/round-23/w1/evidence")]
    return (bool(hits) and res["rc"] != 0,
            "rc!=0 K4 uncommitted-path naming the stray round path")


def case_k3_class(res: dict) -> tuple[bool, str]:
    hits = [r for r in res["rows"] if r["key"] == "K3" and r["cls"] == "class-absent"]
    return (bool(hits) and res["rc"] != 0, "rc!=0 K3 class-absent>=1")


def case_k2_tally(res: dict) -> tuple[bool, str]:
    hits = [r for r in res["rows"] if r["key"] == "K2" and r["cls"] == "uncorrected"]
    return (bool(hits) and res["rc"] != 0, "rc!=0 K2 uncorrected>=1 (tally arm)")


def case_k4_exempt(res: dict) -> tuple[bool, str]:
    have = classes(res, "K4")
    return (not have, "K4 rows=0 (exempted operator path is not a mismatch)")


CASES = [
    # case 1 is the target (green-on-clean); every other case requires >=1 mismatch
    ("repaired", case_repaired, False),
    ("receipt-absent", lambda r: case_k1(r, "receipt-absent"), True),
    ("counts-disagree", lambda r: case_k1(r, "value-disagree", ("rev-disagree",)), True),
    ("rev-disagree", lambda r: case_k1(r, "rev-disagree"), True),
    ("unbound-tuple", case_unbound, True),
    ("uncorrected-log", lambda r: case_k2(r, "uncorrected"), True),
    ("filed-deleted", lambda r: case_k2(r, "filed"), True),
    ("tally-wrong", case_k3, True),
    ("dirty-unexempted", case_k4_stray, True),
    ("exempted-dirty", case_k4_exempt, False),  # green-on-clean is not a false-green control
    ("class-missing", case_k3_class, True),
    ("tally-stale-log", case_k2_tally, True),
]


# --------------------------------------------------------------------------- discovery
def find_tool(explicit: str | None) -> str | None:
    if explicit:
        return os.path.abspath(explicit)
    cands = []
    env = os.environ.get("SOUJI_RECORD_AGREEMENT")
    if env:
        cands.append(os.path.abspath(env))
    for base in (os.path.dirname(os.path.abspath(__file__)), os.getcwd()):
        node = base
        while True:
            cands.append(os.path.join(node, TOOL_REL))
            parent = os.path.dirname(node)
            if parent == node:
                break
            node = parent
    for cand in cands:
        if os.path.isfile(cand):
            return cand
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="fixture for tools/souji-record-agreement.py (r23 C1)")
    ap.add_argument("--tool", default=None, help="instrument path (default: walk up for tools/…)")
    ap.add_argument("--keep", action="store_true", help="keep the /var/tmp scratch tree")
    ap.add_argument("--verbose", action="store_true", help="echo every case's tool stdout")
    args = ap.parse_args(argv)

    tool = find_tool(args.tool)
    if tool is None:
        print("fixture: instrument not found (pass --tool or set SOUJI_RECORD_AGREEMENT)")
        return 2
    digest = hashlib.sha256(open(tool, "rb").read()).hexdigest()
    print(f"tool={tool}")
    print(f"tool_sha256={digest}")
    print(f"scratch={SCRATCH_ROOT}")
    arm_traps()
    cleanup()
    os.makedirs(SCRATCH_ROOT, exist_ok=True)

    passed = 0
    control_observed = False
    for idx, (variant, check, is_control) in enumerate(CASES, 1):
        repo, tip = build(variant)
        res = run_tool(tool, repo, tip, os.path.join(SCRATCH_ROOT, f"case-{idx}.json"))
        ok, expect = check(res)
        if ok:
            passed += 1
            if is_control:
                control_observed = True
        print(f"case={idx} expect={expect} got={got_text(res)}"
              + ("" if ok else " -> FAIL"))
        if args.verbose or not ok:
            for row in res["rows"]:
                print(f"  > {row['key']}\t{row['record']}\t{row['cls']}\t{row['detail']}")
            if not res["rows"] and not ok:
                print(f"  > stdout: {res['stdout'].strip() or '<empty>'}"
                      f" stderr: {res['stderr'].strip() or '<empty>'}")

    total = len(CASES)
    print(f"selftest={passed}/{total}")
    print("control=" + ("FALSE-GREEN-REJECTED" if control_observed else "NOT-REJECTED"))
    if not args.keep:
        cleanup()
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
