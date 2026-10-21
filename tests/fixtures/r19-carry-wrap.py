#!/usr/bin/env python3
"""r19-carry-wrap — external gate for the paragraph-aware carry rule (Q36).

Builds four isolated git worlds under /var/tmp and runs the landing gate's
CLI at a named commit with --round 18. Cases:

  wrap-unmarked          quote stops at the SOURCE's first physical line with
                         no ellipsis            -> exit 1, LG-SEAT-UNCARRIED
  wrap-marked            cut marked with an ellipsis at that line end
                                                -> exit 0
  wrap-complete          whole paragraph quoted on one line
                                                -> exit 0
  wrap-bullet-wrapped    the LESSON bullet itself wraps (false-fail control)
                                                -> exit 0

The same four cases run against a base-arm gate extracted with
`git show <base-rev>:tools/souji-landing-gate.py`. The base arm MUST expose
both the unmarked-cut false pass and wrapped-bullet false failure. Each
arm must also exercise one report, marker, STATUS line and carry heading.

Usage:
  python3 tests/fixtures/r19-carry-wrap.py [--tool PATH] [--base-rev REV]

Exit: 0 clean; 1 a case failed or the base arm showed no discriminating
failure; 2 usage/prerequisite. Scratch only under /var/tmp; no network, no
signals, no live census.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

SCRATCH_PREFIX = "souji-r19-carry-wrap."
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(
    TMPDIR="/var/tmp",
    LC_ALL="C",
    GIT_CONFIG_NOSYSTEM="1",
    GIT_TERMINAL_PROMPT="0",
    PYTHONDONTWRITEBYTECODE="1",
)

SKILL = (
    "# skill\n"
    "| probe | `bash tools/good.sh --x` | row |\n"
    "| gate | `python3 tools/good.py --x` | row |\n"
    "| runner | `python3 census/round-1/run.py --x` | row |\n"
    "| fixture | `python3 tests/fixtures/fx.py --tool T` | row |\n"
)
GOOD_SH = "#!/bin/sh\ntrue\n"
GOOD_PY = "VALUE = 1\n"

REPORT = (
    "# SeatWrap\n\n"
    "STATUS: PARTIAL \u2014 guarded repos measured and the\n"
    "remaining arm never runs under a bound.\n"
)

QUOTE_FIRST_LINE = (
    "\"STATUS: PARTIAL \u2014 guarded repos measured and the\""
)
QUOTE_MARKED = (
    "\"STATUS: PARTIAL \u2014 guarded repos measured and the \u2026\""
)
QUOTE_COMPLETE = (
    "\"STATUS: PARTIAL \u2014 guarded repos measured and the remaining "
    "arm never runs under a bound.\""
)

CASES = {
    "wrap-unmarked": {
        "bullet": "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
                  + QUOTE_FIRST_LINE + " \u2014 open\n",
        "expect_exit": 1,
        "expect_ids": ["LG-SEAT-UNCARRIED"],
    },
    "wrap-marked": {
        "bullet": "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
                  + QUOTE_MARKED + " \u2014 open\n",
        "expect_exit": 0,
        "expect_ids": [],
    },
    "wrap-complete": {
        "bullet": "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
                  + QUOTE_COMPLETE + " \u2014 open\n",
        "expect_exit": 0,
        "expect_ids": [],
    },
    "wrap-bullet-wrapped": {
        "bullet": "- SeatWrap `.ufo/waves/round-18/w1/SeatWrap.md:3` "
                  "\"STATUS: PARTIAL \u2014 guarded repos measured and the "
                  "remaining\narm never runs under a bound.\" \u2014 open\n",
        "expect_exit": 0,
        "expect_ids": [],
    },
}


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True, env=ENV
    )


def write(repo, rel, text):
    path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build_world(root, name, case):
    repo = os.path.join(root, name)
    os.makedirs(repo)
    init = subprocess.run(
        ["git", "init", "-q", "-b", "master", repo],
        capture_output=True, text=True, env=ENV,
    )
    if init.returncode != 0:
        raise RuntimeError("git init failed: %s" % init.stderr.strip())
    write(repo, "SKILL.md", SKILL)
    write(repo, "tools/good.sh", GOOD_SH)
    write(repo, "tools/good.py", GOOD_PY)
    write(repo, "census/round-1/run.py", GOOD_PY)
    write(repo, "tests/fixtures/fx.py", GOOD_PY)
    write(repo, ".ufo/waves/round-18/w1/SeatWrap.md", REPORT)
    write(repo, "corpus/lessons/round-18.md",
          "# Round 18\n\n## Seat-reported failures\n\n" + case["bullet"])
    add = git(repo, "add", "-A")
    if add.returncode != 0:
        raise RuntimeError("git add failed: %s" % add.stderr.strip())
    commit = git(
        repo, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-q", "-m", "case",
    )
    if commit.returncode != 0:
        raise RuntimeError("git commit failed: %s" % commit.stderr.strip())
    rev = git(repo, "rev-parse", "HEAD").stdout.strip()
    return repo, rev


def run_gate(tool, repo, rev, out_path):
    proc = subprocess.run(
        [sys.executable, tool, "--root", repo, "--rev", rev, "--round", "18",
         "--json", out_path],
        capture_output=True, text=True, env=ENV, timeout=180,
    )
    payload = {}
    if os.path.exists(out_path):
        try:
            with open(out_path, encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError):
            payload = {}
    ids = sorted({f.get("id") for f in payload.get("findings", [])
                  if isinstance(f, dict)})
    counts = payload.get("summary", {})
    expected_counts = {"checked_reports": 1, "checked_markers": 1,
                       "status_lines": 1, "carry_heading": 1}
    counters_ok = all(counts.get(key) == value for key, value in expected_counts.items())
    if not counters_ok:
        return 2, ids, "unexercised/mutated summary counters: %r" % counts
    return proc.returncode, ids, (proc.stderr or "").strip()[:200]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", default="tools/souji-landing-gate.py")
    parser.add_argument("--base-rev", default="3ab2c81479f5004c8bc91946eea482caec45408f")
    args = parser.parse_args(argv)

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    tool = args.tool if os.path.isabs(args.tool) else os.path.join(root_dir, args.tool)
    tool = os.path.abspath(tool)
    if not os.path.isfile(tool):
        print("r19-carry-wrap: prerequisite: tool %s is not a file" % tool,
              file=sys.stderr)
        return 2

    top = tempfile.mkdtemp(prefix=SCRATCH_PREFIX, dir="/var/tmp")
    passed = failed = 0
    base_failed = 0
    discriminators = set()
    try:
        base_tool = os.path.join(top, "base-gate.py")
        show = subprocess.run(
            ["git", "-C", root_dir, "show",
             "%s:tools/souji-landing-gate.py" % args.base_rev],
            capture_output=True, text=True, env=ENV,
        )
        if show.returncode != 0:
            print("r19-carry-wrap: prerequisite: cannot extract base gate at %s: %s"
                  % (args.base_rev, show.stderr.strip()[:200]), file=sys.stderr)
            return 2
        with open(base_tool, "w", encoding="utf-8") as handle:
            handle.write(show.stdout)

        for name, case in CASES.items():
            world = os.path.join(top, "w-" + name)
            os.makedirs(world)
            repo, rev = build_world(world, name, case)
            out_path = os.path.join(world, "changed.json")
            code, ids, err = run_gate(tool, repo, rev, out_path)
            ok = code == case["expect_exit"] and ids == case["expect_ids"]
            if ok:
                passed += 1
                print("CASE\tpass\tchanged/%s\texit=%d ids=%s" % (name, code, ids))
            else:
                failed += 1
                print("CASE\tFAIL\tchanged/%s\texit=%d ids=%s want_exit=%d want_ids=%s err=%s"
                      % (name, code, ids, case["expect_exit"],
                         case["expect_ids"], err))

            base_out = os.path.join(world, "base.json")
            bcode, bids, berr = run_gate(base_tool, repo, rev, base_out)
            bok = bcode == case["expect_exit"] and bids == case["expect_ids"]
            if not bok:
                base_failed += 1
                discriminators.add(name)
            print("CASE\t%s\tbase/%s\texit=%d ids=%s"
                  % ("pass" if bok else "discriminates", name, bcode, bids))

        total = passed + failed
        required_discriminators = {"wrap-unmarked", "wrap-bullet-wrapped"}
        if discriminators != required_discriminators:
            failed += 1
            print("CASE\tFAIL\tbase-vacuity\tgot=%s want=%s"
                  % (sorted(discriminators), sorted(required_discriminators)))
        print("SUMMARY total=%d failed=%d base_discriminating=%d"
              % (total, failed, base_failed))
        return 0 if failed == 0 else 1
    finally:
        shutil.rmtree(top, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
