#!/usr/bin/env python3
"""r25-coverage-agreement.py — fixture (oracle) for tools/souji-coverage-agreement.py, round-25 C1.

The round-24 C2 fixture (cases 1-9, unchanged) extended with the round-25 C1 kill-rule cases
k1-k7 (k7 is the veto-less-tool control) and the r24 always-zero control. Exercises the frozen
instrument CLI (round-24 prereg C2, round-25 prereg C1):

    python3 -B tools/souji-coverage-agreement.py --root <lane> --rev <full40> [--base-rev <full40>]

Counts line on stdout: grounded=G mapped=M dangling=D mismatches=X  (exit 0 iff X==0)
  with --base-rev:     ... mismatches=X kill_tested=N kill_violations=V  (exit 0 iff X==0, V==0)
Mismatch rows:         MISMATCH<TAB><class><TAB><path><TAB><detail>
Classes:               MISSING-FROM-MAP, DANGLING-MAP-PATH; KILL-RULE with --base-rev only

Usage:

    python3 -B tests/fixtures/r25-coverage-agreement.py --tool <path>

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
  - cases 1-9 run without --base-rev and accept only the four-key counts line and the two map
    classes, so a tool that leaks kill keys or KILL-RULE rows into the r24 output fails them;
  - kill cases k1-k6 run with --base-rev and assert, besides the above, kill_tested (entries
    grounded at base), kill_violations (entries with >=1 violation) == KILL-RULE rows, mismatches
    == map rows only, and exit 0 iff mismatches==0 and kill_violations==0. Each kill repo has
    exactly one base-grounded entry `e.md`, and HEAD is one commit past --rev with the opposite
    kill outcome, so a tool that reads HEAD, or compares --rev with itself, fails at least one
    kill case.
  - k7 is the veto-less-tool control: a tool that accepts --base-rev, prints kill_tested=0
    kill_violations=0 and exits 0 without checking must FAIL k1 and k2 (the always-zero emitter
    is rejected by k1/k2 too; k7 additionally requires the map counts the wrapped tool printed).
  - control: the always-zero emitter must fail >=1 case. C=16 = 9 r24 + k1..k6 + k7.

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
KILL_CLASSES = (*CLASSES, "KILL-RULE")
COUNTS = re.compile(r"^grounded=(\d+) mapped=(\d+) dangling=(\d+) mismatches=(\d+)$")
KILL_COUNTS = re.compile(r"^grounded=(\d+) mapped=(\d+) dangling=(\d+) mismatches=(\d+)"
                         r" kill_tested=(\d+) kill_violations=(\d+)$")
CONTROL_SRC = (
    "import sys\n"
    "kill = ' kill_tested=0 kill_violations=0' if '--base-rev' in sys.argv else ''\n"
    "print('grounded=0 mapped=0 dangling=0 mismatches=0' + kill)\n"
    "sys.exit(0)\n"
)
VETO_LESS_SRC = (
    "import subprocess, sys\n"
    "tool = sys.argv[1]\n"
    "argv = [sys.executable, '-B'] + sys.argv[1:]\n"
    "subprocess.run(argv)\n"
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
def entry(ground: str | None, *more: str, body: str = "text") -> str:
    lines = ["title: synthetic entry", "source: S000 — synthetic fixture source"]
    if ground is not None:
        lines.append(f"ground: {ground}")
    lines += [f"ground: {g}" for g in more]
    lines += ["verified-at: 2026-10-25", "", "# body", "", body, ""]
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


E_F1 = "F1 — git-native housekeeping"
E_F2 = "F2 — repository size census"
E_F3 = "F3 — duplicate verdicts"
E_F4 = "F4 — restorable quarantine"


def kill_map(f1: str = "—", f2: str = "—", f3: str = "—", f4: str = "—") -> str:
    return readme(table([RECEIPTS_ROW, ("F1 git-native housekeeping", "frontier", f1),
                         ("F2 repository size census", F2_STATUS, f2),
                         ("F3 duplicate verdicts", "frontier, entry held", f3),
                         ("F4 restorable quarantine", "frontier, entry held", f4)]))


# --------------------------------------------------------------------------- cases
class Case:
    def __init__(self, n: int | str, name: str, grounded: int | None = None,
                 rows: tuple[tuple[str, str], ...] = (), bad_revs: tuple[str, ...] = (),
                 kill_tested: int | None = None):
        self.n, self.name, self.grounded, self.rows = n, name, grounded, rows
        self.bad_revs = bad_revs
        self.kill_tested = kill_tested
        self.repo = ""
        self.rev = ""
        self.base_rev = ""

    @property
    def dangling(self) -> int:
        return sum(1 for c, _ in self.rows if c == "DANGLING-MAP-PATH")

    @property
    def mismatches(self) -> int:
        return sum(1 for c, _ in self.rows if c != "KILL-RULE")

    @property
    def kill_violations(self) -> int:
        return sum(1 for c, _ in self.rows if c == "KILL-RULE")

    def expect_text(self) -> str:
        if self.bad_revs:
            return f"exit=2 for --rev in {list(self.bad_revs)}"
        rows = ",".join(f"{c}:{b}" for c, b in sorted(self.rows)) or "none"
        ex = "0" if not self.rows else "nonzero"
        kill = (f" kill_tested={self.kill_tested} kill_violations={self.kill_violations}"
                if self.base_rev else "")
        return (f"grounded={self.grounded} mapped=* dangling={self.dangling} "
                f"mismatches={self.mismatches}{kill} rows=[{rows}] exit={ex}")


def make_cases(root: str) -> list[Case]:
    cases: list[Case] = []

    def add(case: Case, commits, worktree=None, rev_index: int = -1,
            base_index: int | None = None) -> None:
        case.repo = os.path.join(root, f"case-{case.n}")
        shas = build(case.repo, commits, worktree)
        case.rev = shas[rev_index]
        if base_index is not None:
            case.base_rev = shas[base_index]
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

    # Kill-rule cases (round-25 C1): --base-rev = commit 1, --rev = commit 2, HEAD = commit 3
    #   with the opposite kill outcome. The only base-grounded entry is `e.md`; the map at
    #   --rev is consistent, so a KILL-RULE row is the only thing that can make the exit non-zero.
    e = "corpus/knowledge/e.md"
    ledger = {"corpus/knowledge/ledger.tsv": "path\tstate\n"}

    # k1 base e.md grounded F2 -> --rev lacks e.md (HEAD restores it)
    add(Case("k1", "deleted", grounded=0, rows=(("KILL-RULE", "e.md"),), kill_tested=1),
        [{**ledger, e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))},
         {e: None, "corpus/README.md": kill_map()},
         {e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))}],
        rev_index=1, base_index=0)

    # k2 base e.md grounded F2 -> --rev e.md grounded F1, mapped under F1; `ground: F2` survives
    #   only below the `# ` heading (body text, not front matter). HEAD re-grounds it F2.
    add(Case("k2", "regrounded", grounded=1, rows=(("KILL-RULE", "e.md"),), kill_tested=1),
        [{**ledger, e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))},
         {e: entry(E_F1, body="ground: F2 — named in the body, not the front matter"),
          "corpus/README.md": kill_map(f1=k("e.md"))},
         {e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))}],
        rev_index=1, base_index=0)

    # k3 base e.md grounded F2 -> --rev same F2 (body revised), mapped. HEAD deletes e.md.
    add(Case("k3", "clean", grounded=1, kill_tested=1),
        [{**ledger, e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))},
         {e: entry(E_F2, body="text, revised"), "corpus/README.md": kill_map(f2=k("e.md"))},
         {e: None, "corpus/README.md": kill_map()}],
        rev_index=1, base_index=0)

    # k4 base e.md grounded F2+F3 -> --rev keeps both, both map rows list e.md.
    #   HEAD drops the F3 ground line.
    add(Case("k4", "multi", grounded=1, kill_tested=1),
        [{**ledger, e: entry(E_F2, E_F3),
          "corpus/README.md": kill_map(f2=k("e.md"), f3=k("e.md"))},
         {e: entry(E_F2, E_F3, body="text, revised"),
          "corpus/README.md": kill_map(f2=k("e.md"), f3=k("e.md"))},
         {e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))}],
        rev_index=1, base_index=0)

    # k5 base e.md grounded F2+F3 -> --rev keeps only F2 (both mapped); one KILL-RULE row.
    #   HEAD restores F3, so a HEAD-reader sees no violation at --rev and passes.
    add(Case("k5", "partial-removal", grounded=1, rows=(("KILL-RULE", "e.md"),),
             kill_tested=1),
        [{**ledger, e: entry(E_F2, E_F3),
          "corpus/README.md": kill_map(f2=k("e.md"), f3=k("e.md"))},
         {**ledger, e: entry(E_F2, body="text, revised"),
          "corpus/README.md": kill_map(f2=k("e.md"))},
         {**ledger, e: entry(E_F2, E_F3),
          "corpus/README.md": kill_map(f2=k("e.md"), f3=k("e.md"))}],
        rev_index=1, base_index=0)

    # k6 base e.md grounded F2 -> --rev e.md grounded F2+F4, both rows list e.md
    #   (extra grounds are allowed; no violation). HEAD drops the F4 ground line.
    add(Case("k6", "extra-ground-allowed", grounded=1, kill_tested=1),
        [{**ledger, e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))},
         {**ledger, e: entry(E_F2, E_F4, body="text, revised"),
          "corpus/README.md": kill_map(f2=k("e.md"), f4=k("e.md"))},
         {**ledger, e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))}],
        rev_index=1, base_index=0)

    # k7 the veto-less-tool control, scored as case 16: a tool that accepts --base-rev,
    #   prints kill_tested=0 kill_violations=0 and exits 0 without checking must FAIL k1 and
    #   k2. The real tool must match the clean expectation below (the map at --rev is the
    #   k1/k2 shape: e.md grounded F2, mapped). A tool whose kill counts differ from the
    #   observed ones fails this case, including the always-zero emitter.
    veto_path = os.path.join(root, "veto-less.py")
    with open(veto_path, "w", encoding="utf-8") as fh:
        fh.write(VETO_LESS_SRC)
    veto_rejected = True
    for n in ("k1", "k2"):
        subcase = next(c for c in cases if c.n == n)
        ok, got = score(subcase, veto_path, root)
        veto_rejected = veto_rejected and not ok
        print(f"case=k7 name=veto-less-control subcase={n} got: {got} "
              f"-> {'pass' if (not ok) else 'FAIL'}")
    add(Case("k7", "veto-less-control", grounded=1, kill_tested=1),
        [{**ledger, e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))},
         {e: entry(E_F2, body="text, revised"), "corpus/README.md": kill_map(f2=k("e.md"))},
         {e: entry(E_F2), "corpus/README.md": kill_map(f2=k("e.md"))}],
        rev_index=1, base_index=0)
    cases[-1].veto_rejected = veto_rejected
    return cases


# --------------------------------------------------------------------------- scoring
def run_tool(tool: str, repo: str, rev: str, cwd: str,
             base_rev: str = "") -> tuple[int, str]:
    argv = [sys.executable, "-B", tool, "--root", repo, "--rev", rev]
    if base_rev:
        argv += ["--base-rev", base_rev]
    try:
        proc = subprocess.run(argv, cwd=cwd, env=git_env(), capture_output=True, text=True,
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

    kill = bool(case.base_rev)
    code, out = run_tool(tool, case.repo, case.rev, cwd, case.base_rev)
    lines = out.splitlines()
    counts = [m for m in ((KILL_COUNTS if kill else COUNTS).match(l) for l in lines) if m]
    if len(counts) != 1:
        return False, f"counts_lines={len(counts)} exit={code}"
    grounded, mapped, dangling, mismatches = (int(x) for x in counts[0].groups()[:4])
    kill_tested, kill_violations = ((int(x) for x in counts[0].groups()[4:]) if kill
                                    else (None, 0))
    classes = KILL_CLASSES if kill else CLASSES
    rows: list[tuple[str, str]] = []
    bad_rows = 0
    for line in lines:
        if not line.startswith("MISMATCH"):
            continue
        parts = line.split("\t", 3)
        if len(parts) != 4 or parts[0] != "MISMATCH" or parts[1] not in classes:
            bad_rows += 1
            continue
        rows.append((parts[1], os.path.basename(parts[2].rstrip("/"))))
    kill_rows = sum(1 for c, _ in rows if c == "KILL-RULE")
    got_rows = ",".join(f"{c}:{b}" for c, b in sorted(rows)) or "none"
    got_kill = (f" kill_tested={kill_tested} kill_violations={kill_violations}" if kill else "")
    got = (f"grounded={grounded} mapped={mapped} dangling={dangling} mismatches={mismatches}"
           f"{got_kill} rows=[{got_rows}] exit={code}"
           + (f" malformed_rows={bad_rows}" if bad_rows else ""))
    ok = (bad_rows == 0
          and grounded == case.grounded
          and dangling == case.dangling
          and mismatches == case.mismatches
          and Counter(rows) == Counter(case.rows)
          and len(rows) - kill_rows == mismatches
          and sum(1 for c, _ in rows if c == "DANGLING-MAP-PATH") == dangling
          and kill_tested == case.kill_tested
          and kill_violations == case.kill_violations == kill_rows
          and ((code == 0) if not case.rows else (code not in (0, -1))))
    return ok, got


def run_control(source: str, cases: list[Case], label: str, scratch: str) -> int:
    """Write the control script from `source`, score it over `cases`, print per-case lines.

    Returns the number of cases the control passed; the caller combines this with the
    per-control rejection rule.
    """
    control = os.path.join(scratch, label + ".py")
    with open(control, "w", encoding="utf-8") as fh:
        fh.write(source)
    passed = 0
    for case in cases:
        ok, got = score(case, control, scratch)
        passed += ok
        print(f"{label} case={case.n} got: {got} -> {'pass' if ok else 'FAIL'}")
    return passed


def main() -> int:
    global _scratch
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tool", required=True)
    args = ap.parse_args()
    tool = os.path.abspath(args.tool)
    tool_present = os.path.isfile(tool)

    arm_traps()
    _scratch = tempfile.mkdtemp(prefix="souji-r25-coverage-", dir=SCRATCH_PARENT)
    try:
        cases = make_cases(_scratch)

        passed = 0
        for case in cases:
            if tool_present:
                ok, got = score(case, tool, _scratch)
            else:
                ok, got = False, "TOOL-ABSENT"
            passed += ok
            print(f"case={case.n} name={case.name} expect: {case.expect_text()} ; got: {got} "
                  f"-> {'pass' if ok else 'FAIL'}")

        # control 1: the always-zero emitter must fail >=1 case (r24 grammar, unchanged)
        az_pass = run_control(CONTROL_SRC, cases, "control", _scratch)
        az_rejected = az_pass < len(cases)

        # control 2: the veto-less tool ran against k1/k2 inside make_cases (k7); its
        # rejection verdict lives on the k7 case object.
        veto_rejected = cases[-1].veto_rejected

        verdict = ("FALSE-GREEN-REJECTED" if az_rejected and veto_rejected
                   else "FALSE-GREEN-ACCEPTED")
        print(f"cases={len(cases)} pass={passed} control={verdict}")
        return 0 if passed == len(cases) and verdict == "FALSE-GREEN-REJECTED" else 1
    finally:
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
