#!/usr/bin/env python3
"""r24-coverage-agreement.py — fixture (oracle) for tools/souji-coverage-agreement.py, round-24 C2.

Exercises the frozen instrument CLI (preregistration C2):

    python3 -B tools/souji-coverage-agreement.py --root <lane> --rev <full40>

Counts line on stdout: grounded=G mapped=M dangling=D mismatches=X  (exit 0 iff X==0)
Mismatch rows:         MISMATCH<TAB><class><TAB><path><TAB><detail>
Classes:               MISSING-FROM-MAP, DANGLING-MAP-PATH

Usage:

    python3 -B tests/fixtures/r24-coverage-agreement.py --tool <path>

Every case is a synthetic git repo under one mkdtemp in the caller's TMPDIR
(``tempfile.gettempdir()``, never a hard-coded /tmp or /var/tmp), removed in `finally` and on
SIGINT/SIGTERM/SIGHUP. The instrument runs with cwd = the scratch root (not the repo), so it must
honour --root. One `case=` line per case, then the always-zero control run through the
same cases, then the last line:

    cases=C pass=P control=FALSE-GREEN-REJECTED|FALSE-GREEN-ACCEPTED

Exit 0 iff P==C and control=FALSE-GREEN-REJECTED; 1 otherwise; 2 on usage error.

What a case asserts (only what the frozen text defines):
  - exactly one counts line; grounded, dangling, mismatches equal the expectation;
  - `mapped` is printed but NOT asserted: the frozen C2 text names the key without defining it;
  - MISMATCH rows: 4 tab fields, known class, multiset of (class, basename of path) equal to the
    expectation, row total == mismatches, DANGLING-MAP-PATH rows == dangling;
  - exit 0 when mismatches==0, non-zero otherwise; exit 2 for every non-40-hex --rev.

Shapes copied from the real corpus/README.md map, because that is the file the instrument runs on:
escaped `\\|` inside a status cell, both third-header forms (`entries`, `entries / runnable
evidence`), `F2 caveat, ...` and `F1-jj ...` ground cells, `ground: F<k> — ...` entry lines.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from collections import Counter

sys.dont_write_bytecode = True

SCRATCH_PARENT = tempfile.gettempdir()  # honours TMPDIR; never a hard-coded /tmp or /var/tmp
TOOL_TIMEOUT = 60
CLASSES = ("MISSING-FROM-MAP", "DANGLING-MAP-PATH")
COUNTS = re.compile(r"^grounded=(\d+) mapped=(\d+) dangling=(\d+) mismatches=(\d+)$")
CONTROL_SRC = (
    "import sys\n"
    "print('grounded=0 mapped=0 dangling=0 mismatches=0')\n"
    "sys.exit(0)\n"
)

_scratch: str | None = None


def cleanup() -> None:
    if _scratch:
        shutil.rmtree(_scratch, ignore_errors=True)


def arm_traps() -> None:
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        try:
            signal.signal(sig, lambda *_: (cleanup(), os._exit(130)))
        except (ValueError, OSError):
            pass


# --------------------------------------------------------------------------- git plumbing
def git_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("GIT_")}
    env.update({
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "souji-fixture", "GIT_AUTHOR_EMAIL": "fixture@shokunin.local",
        "GIT_COMMITTER_NAME": "souji-fixture", "GIT_COMMITTER_EMAIL": "fixture@shokunin.local",
        "GIT_AUTHOR_DATE": "2026-10-25T00:00:00Z", "GIT_COMMITTER_DATE": "2026-10-25T00:00:00Z",
        "LC_ALL": "C",
    })
    return env


def git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", repo, *args], env=git_env(), check=True,
                          capture_output=True, text=True).stdout.strip()


def apply(repo: str, files: dict[str, str | None]) -> None:
    for rel, body in files.items():
        path = os.path.join(repo, rel)
        if body is None:
            if os.path.exists(path):
                os.remove(path)
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)


def build(repo: str, commits: list[dict[str, str | None]],
          worktree: dict[str, str | None] | None = None) -> list[str]:
    """One commit per dict; then optional working-tree edits, staged but never committed."""
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "master")
    shas = []
    for i, files in enumerate(commits):
        apply(repo, files)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", f"fixture commit {i + 1}")
        shas.append(git(repo, "rev-parse", "HEAD"))
    if worktree:
        apply(repo, worktree)
        git(repo, "add", "-A")
    return shas


# --------------------------------------------------------------------------- corpus builders
def entry(ground: str | None) -> str:
    lines = ["title: synthetic entry", "source: S000 — synthetic fixture source"]
    if ground is not None:
        lines.append(f"ground: {ground}")
    lines += ["verified-at: 2026-10-25", "", "# body", "", "text", ""]
    return "\n".join(lines)


def table(rows: list[tuple[str, str, str]], header3: str = "entries",
          header1: str = "ground") -> str:
    out = [f"| {header1} | status | {header3} |", "|---|---|---|"]
    out += [f"| {a} | {b} | {c} |" for a, b, c in rows]
    return "\n".join(out)


def readme(*tables: str) -> str:
    return "# corpus\n\nSynthetic corpus README.\n\n" + "\n\nprose between tables\n\n".join(
        tables) + "\n"


def k(name: str) -> str:
    return f"`knowledge/{name}`"


RECEIPTS_ROW = ("receipts: pushed / stale", "core (SKILL.md, tools/)", k("ledger.tsv"))
F2_STATUS = r"frontier (sweep: `ls corpus/knowledge \| grep -ciE 'size\|sizer'` → 0)"


def base_files() -> dict[str, str | None]:
    return {
        "corpus/knowledge/a-f2.md": entry("F2 — repository size census"),
        "corpus/knowledge/b-f3.md": entry("F3 — duplicate verdicts"),
        "corpus/knowledge/ledger.tsv": "path\tstate\n",
    }


def base_map(f2_status: str = F2_STATUS, f2_entries: str = k("a-f2.md"),
             f3_entries: str = k("b-f3.md") + "; `../tools/absent-tool.py`",
             extra_rows: tuple[tuple[str, str, str], ...] = (),
             extra_tables: tuple[str, ...] = ()) -> str:
    t1 = table([RECEIPTS_ROW, ("F2 repository size census", f2_status, f2_entries)])
    t2 = table([("F3 duplicate verdicts", "frontier, entry held", f3_entries), *extra_rows],
               header3="entries / runnable evidence")
    return readme(t1, t2, *extra_tables)


# --------------------------------------------------------------------------- cases
class Case:
    def __init__(self, n: int, name: str, grounded: int | None = None,
                 rows: tuple[tuple[str, str], ...] = (), bad_revs: tuple[str, ...] = ()):
        self.n, self.name, self.grounded, self.rows = n, name, grounded, rows
        self.bad_revs = bad_revs
        self.repo = ""
        self.rev = ""

    @property
    def dangling(self) -> int:
        return sum(1 for c, _ in self.rows if c == "DANGLING-MAP-PATH")

    @property
    def mismatches(self) -> int:
        return len(self.rows)

    def expect_text(self) -> str:
        if self.bad_revs:
            return f"exit=2 for --rev in {list(self.bad_revs)}"
        rows = ",".join(f"{c}:{b}" for c, b in sorted(self.rows)) or "none"
        ex = "0" if self.mismatches == 0 else "nonzero"
        return (f"grounded={self.grounded} mapped=* dangling={self.dangling} "
                f"mismatches={self.mismatches} rows=[{rows}] exit={ex}")


def make_cases(root: str) -> list[Case]:
    cases: list[Case] = []

    def add(case: Case, commits, worktree=None, rev_index: int = -1) -> None:
        case.repo = os.path.join(root, f"case-{case.n}")
        shas = build(case.repo, commits, worktree)
        case.rev = shas[rev_index]
        cases.append(case)

    c_f2 = {"corpus/knowledge/c-f2.md": entry("F2 — repository size census")}

    # 1 clean map at --rev; HEAD is one commit later and adds an unmapped grounded entry,
    #   so an instrument that reads HEAD (not --rev) reports 1 and fails here.
    add(Case(1, "clean-map", grounded=2),
        [{**base_files(), "corpus/README.md": base_map()}, c_f2], rev_index=0)

    # 2 grounded F2 entry absent from every map row; named only in tables that are not
    #   coverage maps (first header cell not `ground`; third header cell not `entries...`).
    add(Case(2, "missing-from-map", grounded=3, rows=(("MISSING-FROM-MAP", "c-f2.md"),)),
        [{**base_files(), **c_f2, "corpus/README.md": base_map(extra_tables=(
            table([("F2 size", "decoy", k("c-f2.md"))], header3="notes"),
            table([("F2 size", "decoy", k("c-f2.md"))], header1="round"),
        ))}])

    # 3 entry named only in the STATUS column of its own ground's row
    add(Case(3, "status-column-only", grounded=3, rows=(("MISSING-FROM-MAP", "c-f2.md"),)),
        [{**base_files(), **c_f2, "corpus/README.md": base_map(
            f2_status=F2_STATUS + "; also holds " + k("c-f2.md"))}])

    # 4 F2 entry listed in the entries cell of the F3 row only
    add(Case(4, "other-ground-row", grounded=3, rows=(("MISSING-FROM-MAP", "c-f2.md"),)),
        [{**base_files(), **c_f2, "corpus/README.md": base_map(
            f3_entries=k("b-f3.md") + ", " + k("c-f2.md"))}])

    # 5 entries-column path to a missing knowledge file; a missing knowledge path in a STATUS
    #   cell and a missing non-knowledge path in an entries cell are not DANGLING-MAP-PATH.
    add(Case(5, "dangling-map-path", grounded=2, rows=(("DANGLING-MAP-PATH", "ghost.md"),)),
        [{**base_files(), "corpus/README.md": base_map(
            f2_status=F2_STATUS + "; see " + k("ghost-status.md"),
            f3_entries=k("b-f3.md") + ", " + k("ghost.md") + "; `../tools/absent-tool.py`")}])

    # 6 ground-cell token: `F2 caveat` counts as F2, `F21` does not; `F1-jj` counts as F1,
    #   a bare `F7` cell counts as F7, and an entry grounded F21 is satisfied by the F21 row.
    add(Case(6, "ground-token", grounded=7, rows=(("MISSING-FROM-MAP", "d-f2.md"),)),
        [{**base_files(), **c_f2,
          "corpus/knowledge/d-f2.md": entry("F2 — repository size census"),
          "corpus/knowledge/e-f1.md": entry("F1 — git-native housekeeping"),
          "corpus/knowledge/f-f21.md": entry("F21 — a later ground"),
          "corpus/knowledge/g-f7.md": entry("F7 — bare ground cell"),
          "corpus/README.md": base_map(extra_rows=(
              ("F2 caveat, disclosed only: colocated repos inflate counts", "observed, not claimed",
               k("c-f2.md")),
              ("F21 later ground", "frontier", k("d-f2.md") + ", " + k("f-f21.md")),
              ("F1-jj colocated lane repos (edge class of F1)", "candidate", k("e-f1.md")),
              ("F7", "frontier", k("g-f7.md")),
          ))}])

    # 7 the fix is in the working tree and the index, not in --rev (= HEAD)
    add(Case(7, "worktree-fix-uncommitted", grounded=3, rows=(("MISSING-FROM-MAP", "c-f2.md"),)),
        [{**base_files(), **c_f2, "corpus/README.md": base_map()}],
        worktree={"corpus/README.md": base_map(f2_entries=k("a-f2.md") + ", " + k("c-f2.md"))})

    # 8 entries with no `ground: F<k>` line (absent, or a non-F ground) are not grounded and,
    #   though unmapped, are not mismatches
    add(Case(8, "ungrounded-entry", grounded=2),
        [{**base_files(),
          "corpus/knowledge/h-none.md": entry(None),
          "corpus/knowledge/i-core.md": entry("core — receipts"),
          "corpus/README.md": base_map()}])

    # 9 non-40-hex --rev is refused with exit 2
    case9 = Case(9, "rev-not-full40")
    case9.repo = os.path.join(root, "case-9")
    sha = build(case9.repo, [{**base_files(), "corpus/README.md": base_map()}])[0]
    case9.rev = sha
    case9.bad_revs = (sha[:12], "HEAD", sha[:39] + "z")
    cases.append(case9)
    return cases


# --------------------------------------------------------------------------- scoring
def run_tool(tool: str, repo: str, rev: str, cwd: str) -> tuple[int, str]:
    try:
        proc = subprocess.run([sys.executable, "-B", tool, "--root", repo, "--rev", rev],
                              cwd=cwd, env=git_env(), capture_output=True, text=True,
                              timeout=TOOL_TIMEOUT)
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    return proc.returncode, proc.stdout


def score(case: Case, tool: str, cwd: str) -> tuple[bool, str]:
    if case.bad_revs:
        got = []
        for rev in case.bad_revs:
            code, _ = run_tool(tool, case.repo, rev, cwd)
            got.append(code)
        return all(c == 2 for c in got), f"exits={got}"

    code, out = run_tool(tool, case.repo, case.rev, cwd)
    lines = out.splitlines()
    counts = [m for m in (COUNTS.match(l) for l in lines) if m]
    if len(counts) != 1:
        return False, f"counts_lines={len(counts)} exit={code}"
    grounded, mapped, dangling, mismatches = (int(x) for x in counts[0].groups())
    rows: list[tuple[str, str]] = []
    bad_rows = 0
    for line in lines:
        if not line.startswith("MISMATCH"):
            continue
        parts = line.split("\t", 3)
        if len(parts) != 4 or parts[0] != "MISMATCH" or parts[1] not in CLASSES:
            bad_rows += 1
            continue
        rows.append((parts[1], os.path.basename(parts[2].rstrip("/"))))
    got_rows = ",".join(f"{c}:{b}" for c, b in sorted(rows)) or "none"
    got = (f"grounded={grounded} mapped={mapped} dangling={dangling} mismatches={mismatches} "
           f"rows=[{got_rows}] exit={code}" + (f" malformed_rows={bad_rows}" if bad_rows else ""))
    ok = (bad_rows == 0
          and grounded == case.grounded
          and dangling == case.dangling
          and mismatches == case.mismatches
          and Counter(rows) == Counter(case.rows)
          and len(rows) == mismatches
          and sum(1 for c, _ in rows if c == "DANGLING-MAP-PATH") == dangling
          and ((code == 0) if case.mismatches == 0 else (code not in (0, -1))))
    return ok, got


def main() -> int:
    global _scratch
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tool", required=True)
    args = ap.parse_args()
    tool = os.path.abspath(args.tool)
    tool_present = os.path.isfile(tool)

    arm_traps()
    _scratch = tempfile.mkdtemp(prefix="souji-r24-coverage-", dir=SCRATCH_PARENT)
    try:
        cases = make_cases(_scratch)
        control = os.path.join(_scratch, "always-zero.py")
        with open(control, "w", encoding="utf-8") as fh:
            fh.write(CONTROL_SRC)

        passed = 0
        for case in cases:
            if tool_present:
                ok, got = score(case, tool, _scratch)
            else:
                ok, got = False, "TOOL-ABSENT"
            passed += ok
            print(f"case={case.n} name={case.name} expect: {case.expect_text()} ; got: {got} "
                  f"-> {'pass' if ok else 'FAIL'}")

        control_pass = 0
        for case in cases:
            ok, got = score(case, control, _scratch)
            control_pass += ok
            print(f"control case={case.n} got: {got} -> {'pass' if ok else 'FAIL'}")
        verdict = ("FALSE-GREEN-REJECTED" if control_pass < len(cases)
                   else "FALSE-GREEN-ACCEPTED")
        print(f"cases={len(cases)} pass={passed} control={verdict}")
        return 0 if passed == len(cases) and verdict == "FALSE-GREEN-REJECTED" else 1
    finally:
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
