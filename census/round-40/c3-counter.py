#!/usr/bin/env python3
"""census/round-40/c3-counter.py — r40 C3 record-branch mutation coverage.

The r39 C3 battery scored four record-file behaviours (M11 trailing space, M12 CRLF, M13 outside root,
M14 indented comment). Four branches of `tools/souji-worktree-drift.py` stayed uncovered by every
committed fixture, and the r39 planned r40 row named them: multiple TOTAL rows, `--skip-unrecorded`
and invalid UTF-8 record bytes. This counter scores four single-defect mutants of those branches:

  M15  the parser assigns the LAST TOTAL row it reads; the mutant keeps the FIRST, so a second
       conflicting TOTAL row is accepted instead of refused
  M16  `--skip-unrecorded` suppresses the UNRECORDED drift rows; the mutant always scans
  M17  the record is decoded with the `replace` error handler; the mutant uses `ignore`, so an
       undecodable byte disappears instead of becoming U+FFFD
  M18  a TOTAL row whose `repos` disagrees with the REPO row count is refused; the mutant accepts it

Each mutant is applied to the audited tool bytes (an anchor that does not occur exactly once is a
battery defect, not a kill) and scored by two fixtures: the candidate
`tests/fixtures/r40-drift-record-branches.py` (a kill needs its own `SUMMARY cases=... fail>0`, no
traceback and exit 1) and the base `tests/fixtures/r39-drift-record-rules.py`, which must keep every
mutant alive (`base_killed=0`).

r40 repair (wave-1 seat R40reviewer18, findings F1-F4): the r39 scoring contract scanned the
fixture's stdout AND stderr for a traceback marker, so a TOOL traceback laundered through the
fixture's diagnostic echo was scored as "the fixture crashed" and a genuinely detected mutant was
scored SURVIVED. This counter reads the crash marker from the fixture's STDERR only — a Python
traceback is written there, never to the fixture's stdout — and prints the failing case names, so a
kill is attributable to the branch case that covers it.

CLI:
  python3 -B census/round-40/c3-counter.py --root LANE --rev REV --base-rev REV [--scratch DIR]
      [--tool tools/souji-worktree-drift.py] [--fixture PATH] [--base-fixture PATH]

Exit: 0 `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=8`; 1 any survivor,
pristine failure, base kill or short fixture; 2 usage / could-not-evaluate input.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV = re.compile(r"^[0-9a-f]{40}$")
GIT_ENV = {
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_ATTR_NOSYSTEM": "1",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_TERMINAL_PROMPT": "0",
}
TOTAL_ASSIGN = ('            total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), '
                '"prunable": int(m.group("prunable"))}')
SKIP_GUARD = "    if not args.skip_unrecorded:"
DECODE = '        raw = b"".join(chunks).decode("utf-8", "replace")'
REPOS_GUARD = '        if total["repos"] != len(rows):'

MUTANTS = (
    ("M15", TOTAL_ASSIGN,
     '            if total is None:\n'
     '                total = {"repos": int(m.group("repos")), "regs": int(m.group("regs")), '
     '"prunable": int(m.group("prunable"))}'),
    ("M16", SKIP_GUARD, "    if True:"),
    ("M17", DECODE, '        raw = b"".join(chunks).decode("utf-8", "ignore")'),
    ("M18", REPOS_GUARD, "        if False:"),
)


def child_env(scratch=None):
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
           "TMPDIR": scratch or os.environ.get("TMPDIR") or "/var/tmp"}
    env.update(GIT_ENV)
    return env


def git_show(root, rev, path):
    proc = subprocess.run(
        ["git", "-C", root, "show", "%s:%s" % (rev, path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=child_env(), check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace")


def resolves(root, rev):
    return subprocess.run(
        ["git", "-C", root, "cat-file", "-e", rev + "^{commit}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=child_env(), check=False,
    ).returncode == 0


def score(fixture, tool, work):
    """Return (killed, detail, cases) — the fixture must report its own failure summary.

    The crash probe reads the fixture's STDERR only: a Python traceback is written there, while a
    TOOL traceback laundered into the fixture's stdout diagnostic echo must not mask a real kill
    (r40 repair of the r39 scoring contract).
    """
    proc = subprocess.run(
        ["python3", "-B", fixture, "--tool", tool, "--work", work],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
        env=child_env(work),
    )
    summaries = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
    if not summaries:
        return False, "NO-SUMMARY rc=%d" % proc.returncode, None
    match = re.search(r"cases=(\d+) pass=(\d+) fail=(\d+)", summaries[-1])
    if not match:
        return False, "BAD-SUMMARY %r" % summaries[-1], None
    cases, _passed, fails = (int(match.group(i)) for i in (1, 2, 3))
    crash = "Traceback (most recent call last)" in proc.stderr
    failing = [l.split("=", 1)[0][5:] for l in proc.stdout.splitlines()
               if l.startswith("case-") and "=FAIL" in l.split(" ", 1)[0]]
    killed = proc.returncode == 1 and fails > 0 and not crash
    return killed, "rc=%d fails=%d crash=%s failing=%s" % (
        proc.returncode, fails, crash, ",".join(failing) or "-"), cases


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base-rev", required=True)
    ap.add_argument("--tool", default="tools/souji-worktree-drift.py")
    ap.add_argument("--fixture", default="tests/fixtures/r40-drift-record-branches.py")
    ap.add_argument("--base-fixture", default="tests/fixtures/r39-drift-record-rules.py")
    ap.add_argument("--scratch")
    args = ap.parse_args(argv)
    for flag, rev in (("--rev", args.rev), ("--base-rev", args.base_rev)):
        if not REV.match(rev) or not resolves(args.root, rev):
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s %s does not resolve\n" % (flag, rev))
            return 2
    try:
        scratch = tempfile.mkdtemp(
            prefix="souji-r40-c3.", dir=args.scratch or os.environ.get("TMPDIR") or "/var/tmp")
    except OSError as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: scratch root unavailable: %s\n" % exc)
        return 2
    try:
        source = git_show(args.root, args.rev, args.tool)
        candidate_src = git_show(args.root, args.rev, args.fixture)
        base_src = git_show(args.root, args.base_rev, args.base_fixture)
        if source is None or candidate_src is None or base_src is None:
            sys.stderr.write(
                "REFUSAL COULD-NOT-EVALUATE: tool/candidate fixture absent at %s or base fixture absent at %s\n"
                % (args.rev, args.base_rev))
            return 2
        tool_sha = hashlib.sha256(source.encode()).hexdigest()[:12]
        fixture_sha = hashlib.sha256(candidate_src.encode()).hexdigest()[:12]
        pristine_tool = os.path.join(scratch, "pristine.py")
        with open(pristine_tool, "w", encoding="utf-8") as handle:
            handle.write(source)
        os.chmod(pristine_tool, 0o755)
        candidate = os.path.join(scratch, "r40-branches.py")
        with open(candidate, "w", encoding="utf-8") as handle:
            handle.write(candidate_src)
        base_fixture = os.path.join(scratch, "r39-rules.py")
        with open(base_fixture, "w", encoding="utf-8") as handle:
            handle.write(base_src)
        pristine_proc = subprocess.run(
            ["python3", "-B", candidate, "--tool", pristine_tool, "--work", scratch],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
            env=child_env(scratch),
        )
        summary = [l for l in pristine_proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
        pristine_ok = False
        cases = 0
        if summary:
            match = re.search(r"cases=(\d+) pass=(\d+) fail=(\d+)", summary[-1])
            if match:
                cases = int(match.group(1))
                pristine_ok = (
                    pristine_proc.returncode == 0
                    and int(match.group(3)) == 0
                    and int(match.group(2)) == cases
                    and cases >= 8
                )
        if not pristine_ok:
            print("SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=%d" % cases)
            return 1
        results = []
        for mid, old, new in MUTANTS:
            count = source.count(old)
            if count != 1:
                print("MUTANT %s ANCHOR-COUNT %d (expected 1)" % (mid, count))
                results.append((mid, False, False))
                continue
            path = os.path.join(scratch, mid + ".py")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(source.replace(old, new))
            os.chmod(path, 0o755)
            killed, detail, _ = score(candidate, path, scratch)
            base_killed, base_detail, _ = score(base_fixture, path, scratch)
            print("MUTANT %s killed=%s base_killed=%s %s base:%s" % (
                mid, "yes" if killed else "no", "yes" if base_killed else "no", detail, base_detail))
            results.append((mid, killed, base_killed))
        killed_n = sum(1 for _, k, _ in results if k)
        base_n = sum(1 for _, _, b in results if b)
        print("SUMMARY mutants=%d killed=%d survived=%d pristine=ok base_killed=%d cases=%d "
              "tool_sha=%s fixture_sha=%s" % (
                  len(results), killed_n, len(results) - killed_n, base_n, cases, tool_sha, fixture_sha))
        return 0 if killed_n == len(results) and base_n == 0 else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
