#!/usr/bin/env python3
"""External precision fixture for tools/souji-landing-gate.py (round 31, C2).

Usage: python3 -B tests/fixtures/r31-landing-gate-precision.py [--tool PATH]
       TMPDIR must be set and must not lie inside the lane or the fleet.

Frozen contract (census/round-31/records/preregistration.txt, C2 paragraph):

  G1 union: round N has `.ufo/waves/round-N/w1/A.md` (STATUS: PASS) and
     `census/round-N/waves/w1/B.md` (STATUS: FAIL — b) and the lesson carries
     nothing -> PASS iff checked_reports=2 and exactly one
     LG-SEAT-UNCARRIED, naming B.
  G2 dedupe: the same relative `w1/A.md` (identical bytes, STATUS: FAIL — a)
     under both trees and the lesson carries it with `open` -> PASS iff
     checked_reports=1 and no LG-SEAT-UNCARRIED.
  G3 append-only carry: lesson has `## Seat-reported failures` carrying
     report X, then another heading, then a second `## Seat-reported
     failures` section at the end carrying report Y (X and Y both STATUS:
     FAIL) -> PASS iff no LG-SEAT-UNCARRIED.
  G4 ellipsis placeholder: a scanned file cites
     `census/round-18/...seat-audit...json` -> PASS iff no LG-DANGLING-PTR.
  G5 line ranges: cites `tools/x.py:274–277` (en dash) and `tools/x.py:2-3`,
     tools/x.py committed -> PASS iff no LG-DANGLING-PTR.
  G6 captured names: cites `census/round-N/waves/v/.gitignore`,
     `.ufo/waves/round-N/v/.gitattributes` and
     `census/round-N/waves/v/.gitignore:fixture/`, with
     `census/round-N/waves/v/.gitignore.captured` and
     `census/round-N/waves/v/.gitattributes.captured` committed -> PASS iff
     no LG-DANGLING-PTR.
  G7 printf templates: cites `census/round-%d/waves/` and
     `corpus/lessons/round-%02d.md` -> PASS iff no LG-DANGLING-PTR.
  G8 prose alternation: cites `tools/tests/census/corpus`, `corpus/authority`
     and `tools/kill/killpg` (no extension, no trailing slash, absent) ->
     PASS iff no LG-DANGLING-PTR.
  G9 precision control: cites `tools/missing.py`,
     `census/round-N/waves/w1/missing.md`, `.ufo/waves/round-N/w1/missing.md`,
     `corpus/knowledge/missing.md:12–14`, `census/round-3/garbage-census.out`
     and `tools/__pycache__/`, none committed -> PASS iff exactly 6
     LG-DANGLING-PTR lines, one containing each of those six paths (line spec
     removed).
  G10 carry control: two `## Seat-reported failures` sections, neither
     carrying report Z (STATUS: FAIL) -> PASS iff exactly one
     LG-SEAT-UNCARRIED, naming Z.

Output: one `CASE G<k> PASS|FAIL <detail>` line per case (space-separated, so
`^CASE G<k> PASS` greps cleanly), then one `CONTROL ...` line, then the last
line `cases=N pass=M control=FALSE-GREEN-REJECTED|FALSE-GREEN-ACCEPTED`.
The control is an always-zero emitter (a stub tool printing one clean SUMMARY
with findings=0 and checked_reports=0 and nothing else) run through the same
ten cases; it must fail at least one of them.

Exit 0 iff every case passes and the control is rejected; 1 otherwise; 2 on a
missing prerequisite (tool absent, no git, TMPDIR unset or inside the lane or
the fleet).

Boundary: this fixture only runs the selected gate binary against real git
repositories it creates under a private directory inside $TMPDIR (removed in
finally). It never writes in a lane checkout, never runs lane scripts, and
never touches .ufo/state, MANIFEST.json or a sibling lane. Note: the gate
itself pins its parse-snapshot directory to /var/tmp and removes it in
finally; that path is the tool's own behaviour, not this fixture's.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROUND = 31          # round under evaluation; capture lives at census/round-31/waves
PLACEHOLDER_ROUND = 18  # round named by the G4 ellipsis placeholder, never evaluated
MISSING_ROUND = 3   # round named by the G9 real dangling pointer, never evaluated

LANE_ROOT = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET_ROOT = "/home/vgpnk/Projects/shokunin"

SKILL = "# Synthetic lane\n\nNo registry citations in this fixture.\n"


# ---------------------------------------------------------------------------
# Git plumbing (throwaway repositories only, deterministic identity)
# ---------------------------------------------------------------------------

REPO_SELECTING = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
)


def clean_env():
    return {k: v for k, v in os.environ.items() if k not in REPO_SELECTING}


def git_env(base):
    env = clean_env()
    env.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.path.join(base, "no-global-gitconfig"),
            "GIT_TERMINAL_PROMPT": "0",
            "HOME": os.path.join(base, "home"),
            "GIT_AUTHOR_NAME": "r31-precision-fixture",
            "GIT_AUTHOR_EMAIL": "r31@fixture.invalid",
            "GIT_COMMITTER_NAME": "r31-precision-fixture",
            "GIT_COMMITTER_EMAIL": "r31@fixture.invalid",
            "GIT_AUTHOR_DATE": "2026-10-26T00:00:00Z",
            "GIT_COMMITTER_DATE": "2026-10-26T00:00:00Z",
        }
    )
    return env


class Repo(object):
    """A throwaway git repository used as gate --root input."""

    def __init__(self, base, name, env):
        self.path = os.path.join(base, name)
        os.makedirs(self.path)
        self.env = env
        self._git("init", "-q", "-b", "main")
        self._git("config", "commit.gpgsign", "false")
        self._git("config", "user.name", "r31-precision-fixture")
        self._git("config", "user.email", "r31@fixture.invalid")

    def _git(self, *args):
        proc = subprocess.run(
            ["git", "-C", self.path] + list(args),
            capture_output=True,
            text=True,
            env=self.env,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                "git %s failed in %s: %s"
                % (args[0], self.path, proc.stderr.strip()[:300])
            )
        return proc.stdout.strip()

    def write(self, rel, text):
        dest = os.path.join(self.path, rel)
        parent = os.path.dirname(dest)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(text)

    def commit(self, msg):
        self._git("add", "-A")
        self._git("commit", "-q", "-m", msg)
        return self._git("rev-parse", "HEAD")


# ---------------------------------------------------------------------------
# Gate invocation + output parsing
# ---------------------------------------------------------------------------


class Run(object):
    def __init__(self, rc, stdout, stderr):
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr
        self.rows = [line for line in stdout.splitlines() if line.strip()]
        self.cne = ("COULD-NOT-EVALUATE" in stdout) or (
            "COULD-NOT-EVALUATE" in stderr
        )

    def summary(self, key):
        line = None
        for row in self.rows:
            if row.split("\t", 1)[0] == "SUMMARY":
                line = row
        if line is None:
            return None
        match = re.search(r"\b%s=(\d+)" % re.escape(key), line)
        return int(match.group(1)) if match else None

    def finding_rows(self, finding_id):
        return [
            row for row in self.rows if row.split("\t", 1)[0] == finding_id
        ]


def gate_argv(tool):
    if tool.endswith(".py"):
        return [sys.executable, "-B", tool]
    return [tool]


def run_gate(tool, root, rev, round_no):
    cmd = gate_argv(tool) + [
        "--root", root,
        "--rev", rev,
        "--round", str(round_no),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return Run(124, "", "TIMEOUT after 180s")
    return Run(proc.returncode, proc.stdout, proc.stderr)


# ---------------------------------------------------------------------------
# Synthetic worlds (one repository per world, built once, read by both tools)
# ---------------------------------------------------------------------------

CLEAN_REPORT = "# Seat\n\nSTATUS: ok - clean.\n"

LESSON_CLEAN = "# Round 31 lesson\n\nNo seat failures carried.\n"


def carry_section(entries):
    return "## Seat-reported failures\n\n" + "\n".join(entries) + "\n"


def spotcheck(citations):
    return "# Round 31 spotcheck\n\n" + "\n\n".join(citations) + "\n"


def build_world(base, env, name):
    """Build one named synthetic repository. Return (path, head_rev)."""
    repo = Repo(base, name, env)
    repo.write("SKILL.md", SKILL)
    repo.write("corpus/lessons/round-%d.md" % ROUND, LESSON_CLEAN)

    if name == "g1":
        # G1: one PASS report in the wave tree, one failing report capture-only.
        repo.write(
            ".ufo/waves/round-%d/w1/A.md" % ROUND,
            "# A\n\nSTATUS: PASS - synthetic pass.\n",
        )
        repo.write(
            "census/round-%d/waves/w1/B.md" % ROUND,
            "# B\n\nSTATUS: FAIL - synthetic union failure b.\n",
        )
    elif name == "g2":
        # G2: identical bytes at the same relative path in both trees; the
        # lesson carries the one report with `open`.
        duplicate = "# A\n\nSTATUS: FAIL - synthetic duplicate a.\n"
        repo.write(".ufo/waves/round-%d/w1/A.md" % ROUND, duplicate)
        repo.write("census/round-%d/waves/w1/A.md" % ROUND, duplicate)
        repo.write(
            "corpus/lessons/round-%d.md" % ROUND,
            "# Round 31 lesson\n\n"
            + carry_section(["- STATUS: FAIL - synthetic duplicate a. (open)"]),
        )
    elif name == "g3":
        # G3: a carry section, a later heading, then a second carry section at
        # the end; each section carries one of the two failing reports.
        repo.write(
            ".ufo/waves/round-%d/w1/X.md" % ROUND,
            "# X\n\nSTATUS: FAIL - synthetic carry x.\n",
        )
        repo.write(
            ".ufo/waves/round-%d/w1/Y.md" % ROUND,
            "# Y\n\nSTATUS: FAIL - synthetic carry y.\n",
        )
        repo.write(
            "corpus/lessons/round-%d.md" % ROUND,
            "# Round 31 lesson\n\n"
            + carry_section(["- STATUS: FAIL - synthetic carry x. (open)"])
            + "\n## Notes\n\nNothing else.\n\n"
            + carry_section(["- STATUS: FAIL - synthetic carry y. (open)"]),
        )
    elif name == "g4":
        # G4: an ellipsis placeholder names no path.
        repo.write(
            "corpus/lessons/round-%d-verifier-spotcheck.md" % ROUND,
            spotcheck(
                [
                    "Placeholder citation: "
                    "`census/round-%d/...seat-audit...json`." % PLACEHOLDER_ROUND
                ]
            ),
        )
        repo.write(".ufo/waves/round-%d/w1/Seat.md" % ROUND, CLEAN_REPORT)
    elif name == "g5":
        # G5: an en-dash range and an ASCII range on a committed script.
        repo.write("tools/x.py", "print('ok')\n")
        repo.write(
            "corpus/lessons/round-%d-verifier-spotcheck.md" % ROUND,
            spotcheck(
                [
                    "Ranges on a committed script: `tools/x.py:274\u2013277` "
                    "and `tools/x.py:2-3`."
                ]
            ),
        )
        repo.write(".ufo/waves/round-%d/w1/Seat.md" % ROUND, CLEAN_REPORT)
    elif name == "g6":
        # G6: the committed names carry a `.captured` suffix; one citation
        # also carries a `:text` suffix.
        repo.write(
            "census/round-%d/waves/v/.gitignore.captured" % ROUND, "/tmp/\n"
        )
        repo.write(
            "census/round-%d/waves/v/.gitattributes.captured" % ROUND,
            "*.md text\n",
        )
        repo.write(
            "corpus/lessons/round-%d-verifier-spotcheck.md" % ROUND,
            spotcheck(
                [
                    "Capture names: "
                    "`census/round-%d/waves/v/.gitignore`, "
                    "`.ufo/waves/round-%d/v/.gitattributes` and "
                    "`census/round-%d/waves/v/.gitignore:fixture/`."
                    % (ROUND, ROUND, ROUND)
                ]
            ),
        )
        repo.write(".ufo/waves/round-%d/w1/Seat.md" % ROUND, CLEAN_REPORT)
    elif name == "g7":
        # G7: printf templates are not paths.
        repo.write(
            "corpus/lessons/round-%d-verifier-spotcheck.md" % ROUND,
            spotcheck(
                [
                    "Templates: `census/round-%d/waves/` and "
                    "`corpus/lessons/round-%02d.md`."
                ]
            ),
        )
        repo.write(".ufo/waves/round-%d/w1/Seat.md" % ROUND, CLEAN_REPORT)
    elif name == "g8":
        # G8: prose slash alternations, extension-less and absent.
        repo.write(
            "corpus/lessons/round-%d-verifier-spotcheck.md" % ROUND,
            spotcheck(
                [
                    "Prose alternations: `tools/tests/census/corpus`, "
                    "`corpus/authority` and `tools/kill/killpg`."
                ]
            ),
        )
        repo.write(".ufo/waves/round-%d/w1/Seat.md" % ROUND, CLEAN_REPORT)
    elif name == "g9":
        # G9: six real dangling pointers, none committed.
        repo.write(
            "corpus/lessons/round-%d-verifier-spotcheck.md" % ROUND,
            spotcheck(
                [
                    "Missing file: `tools/missing.py`.",
                    "Missing capture report: `census/round-%d/waves/w1/"
                    "missing.md`." % ROUND,
                    "Missing wave report: `.ufo/waves/round-%d/w1/"
                    "missing.md`." % ROUND,
                    "Missing knowledge entry: "
                    "`corpus/knowledge/missing.md:12\u201314`.",
                    "Missing census output: `census/round-%d/"
                    "garbage-census.out`." % MISSING_ROUND,
                    "Ignored absent directory: `tools/__pycache__/`.",
                ]
            ),
        )
        repo.write(".ufo/waves/round-%d/w1/Seat.md" % ROUND, CLEAN_REPORT)
    elif name == "g10":
        # G10: report Z is carried by neither section.
        repo.write(
            ".ufo/waves/round-%d/w1/Z.md" % ROUND,
            "# Z\n\nSTATUS: FAIL - synthetic carry z.\n",
        )
        repo.write(
            "corpus/lessons/round-%d.md" % ROUND,
            "# Round 31 lesson\n\n"
            + carry_section(["- STATUS: FAIL - synthetic witness x. (open)"])
            + "\n## Notes\n\nNothing else.\n\n"
            + carry_section(["- STATUS: FAIL - synthetic witness y. (open)"]),
        )
    else:
        raise RuntimeError("unknown world %r" % name)

    return repo.path, repo.commit("world " + name)


# ---------------------------------------------------------------------------
# Case judges
# ---------------------------------------------------------------------------


class Checker(object):
    def __init__(self):
        self.problems = []

    def expect(self, cond, msg):
        if not cond:
            self.problems.append(msg)
        return cond


def exercised(c, r, label):
    """Both output shapes this fixture judges require a completed evaluation."""
    c.expect(not r.cne, "%s: COULD-NOT-EVALUATE printed" % label)
    c.expect(r.rc in (0, 1), "%s: exit=%s want 0 or 1" % (label, r.rc))
    c.expect(r.summary("checked_reports") is not None,
             "%s: no SUMMARY line" % label)


def dangling(r):
    return r.finding_rows("LG-DANGLING-PTR")


def uncarried(r):
    return r.finding_rows("LG-SEAT-UNCARRIED")


def judge(cid, worlds):
    """worlds: {world_name: Run}. Return list of problem strings (empty = pass)."""
    c = Checker()

    if cid == "G1":
        r = worlds["g1"]
        exercised(c, r, "g1")
        c.expect(r.summary("checked_reports") == 2,
                 "g1: checked_reports=%s want 2 (union)"
                 % r.summary("checked_reports"))
        rows = uncarried(r)
        c.expect(len(rows) == 1,
                 "g1: LG-SEAT-UNCARRIED count=%d want 1" % len(rows))
        c.expect(any("w1/B.md" in row for row in rows),
                 "g1: LG-SEAT-UNCARRIED does not name w1/B.md")
    elif cid == "G2":
        r = worlds["g2"]
        exercised(c, r, "g2")
        c.expect(r.summary("checked_reports") == 1,
                 "g2: checked_reports=%s want 1 (double count?)"
                 % r.summary("checked_reports"))
        c.expect(not uncarried(r), "g2: LG-SEAT-UNCARRIED for a carried report")
    elif cid == "G3":
        r = worlds["g3"]
        exercised(c, r, "g3")
        rows = uncarried(r)
        c.expect(not rows,
                 "g3: LG-SEAT-UNCARRIED count=%d want 0 (second section unseen?)"
                 % len(rows))
    elif cid in ("G4", "G5", "G6", "G7", "G8"):
        world = {"G4": "g4", "G5": "g5", "G6": "g6",
                 "G7": "g7", "G8": "g8"}[cid]
        r = worlds[world]
        exercised(c, r, world)
        rows = dangling(r)
        c.expect(not rows,
                 "%s: LG-DANGLING-PTR count=%d want 0: %s"
                 % (world, len(rows),
                    " | ".join(row.split("\t")[1] for row in rows[:4])))
    elif cid == "G9":
        r = worlds["g9"]
        exercised(c, r, "g9")
        rows = dangling(r)
        c.expect(len(rows) == 6,
                 "g9: LG-DANGLING-PTR count=%d want 6" % len(rows))
        needles = (
            "tools/missing.py",
            "census/round-%d/waves/w1/missing.md" % ROUND,
            ".ufo/waves/round-%d/w1/missing.md" % ROUND,
            "corpus/knowledge/missing.md",
            "census/round-%d/garbage-census.out" % MISSING_ROUND,
            "tools/__pycache__/",
        )
        for needle in needles:
            c.expect(any(needle in row for row in rows),
                     "g9: no LG-DANGLING-PTR containing %s" % needle)
    elif cid == "G10":
        r = worlds["g10"]
        exercised(c, r, "g10")
        rows = uncarried(r)
        c.expect(len(rows) == 1,
                 "g10: LG-SEAT-UNCARRIED count=%d want 1" % len(rows))
        c.expect(any("w1/Z.md" in row for row in rows),
                 "g10: LG-SEAT-UNCARRIED does not name w1/Z.md")
    else:
        raise RuntimeError("unknown case %r" % cid)

    return c.problems


def detail_of(cid, worlds, problems):
    r = worlds[WORLD_OF[cid][0]]
    return "exit=%d reports=%s status=%s findings=%s dangling=%d uncarried=%d%s" % (
        r.rc,
        r.summary("checked_reports"),
        r.summary("status_lines"),
        r.summary("findings"),
        len(dangling(r)),
        len(uncarried(r)),
        "" if not problems else " FAIL(" + "; ".join(problems) + ")",
    )


CASES = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10")
WORLD_OF = {
    "G1": ["g1"],
    "G2": ["g2"],
    "G3": ["g3"],
    "G4": ["g4"],
    "G5": ["g5"],
    "G6": ["g6"],
    "G7": ["g7"],
    "G8": ["g8"],
    "G9": ["g9"],
    "G10": ["g10"],
}

CONTROL_SOURCE = (
    "import sys\n"
    "print(\"SUMMARY\\tfindings=0\\tchecked_reg=0\\tchecked_changed=0\\t"
    "checked_pins=0\\tchecked_measured=0\\tchecked_markers=0\\t"
    "status_lines=0\\tcarry_heading=0\\tchecked_reports=0\")\n"
    "sys.exit(0)\n"
)


# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------


def inside(child, parent):
    return child == parent or child.startswith(parent.rstrip(os.sep) + os.sep)


def prerequisites(tool):
    problems = []
    tmpdir = os.environ.get("TMPDIR")
    if not tmpdir:
        problems.append("TMPDIR is unset (build synthetic repos under $TMPDIR)")
    elif not os.path.isdir(tmpdir):
        problems.append("TMPDIR is not a directory: %s" % tmpdir)
    if shutil.which("git") is None:
        problems.append("git not found on PATH")
    if not os.path.isfile(tool):
        problems.append("tool not found: %s" % tool)
    if not problems:
        tmp_real = os.path.realpath(tmpdir)
        for label, root in (("lane", LANE_ROOT), ("fleet", FLEET_ROOT)):
            if inside(tmp_real, os.path.realpath(root)):
                problems.append(
                    "TMPDIR %s is inside the %s root %s"
                    % (tmp_real, label, root)
                )
    return problems


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def default_tool():
    here = os.path.dirname(os.path.abspath(__file__))
    lane = os.path.dirname(os.path.dirname(here))
    return os.path.join(lane, "tools", "souji-landing-gate.py")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="r31 landing-gate precision fixture (C2 G1-G10)"
    )
    ap.add_argument("--tool", default=None,
                    help="gate binary to exercise (default: this lane's tools/souji-landing-gate.py)")
    args = ap.parse_args(argv)
    tool = os.path.abspath(args.tool or default_tool())

    problems = prerequisites(tool)
    if problems:
        for msg in problems:
            print("PREREQ FAIL %s" % msg)
        print("cases=0 pass=0 control=FALSE-GREEN-ACCEPTED")
        return 2

    scratch = tempfile.mkdtemp(prefix="r31-precision-fixture-",
                               dir=os.path.realpath(os.environ["TMPDIR"]))
    try:
        env = git_env(scratch)
        os.makedirs(os.path.join(scratch, "home"), exist_ok=True)

        control = os.path.join(scratch, "always-zero-emitter.py")
        with open(control, "w", encoding="utf-8") as fh:
            fh.write(CONTROL_SOURCE)

        roots = {}
        for name in sorted({w for worlds in WORLD_OF.values() for w in worlds}):
            roots[name] = build_world(os.path.join(scratch, "repos"), env, name)

        run_cache = {}

        def runs_for(tool_path):
            out = {}
            for name in roots:
                key = (tool_path, name)
                if key not in run_cache:
                    path, rev = roots[name]
                    run_cache[key] = run_gate(tool_path, path, rev, ROUND)
                out[name] = run_cache[key]
            return out

        primary = runs_for(tool)
        control_runs = runs_for(control)

        passed = 0
        control_failed = []
        for cid in CASES:
            worlds = {name: primary[name] for name in WORLD_OF[cid]}
            case_problems = judge(cid, worlds)
            if not case_problems:
                passed += 1
            print("CASE %s %s %s" % (
                cid,
                "PASS" if not case_problems else "FAIL",
                detail_of(cid, worlds, case_problems),
            ))
            c_worlds = {name: control_runs[name] for name in WORLD_OF[cid]}
            if judge(cid, c_worlds):
                control_failed.append(cid)

        rejected = bool(control_failed)
        print("CONTROL always-zero-emitter %s failed=%s" % (
            "FALSE-GREEN-REJECTED" if rejected else "FALSE-GREEN-ACCEPTED",
            ",".join(control_failed) if control_failed else "none",
        ))
        print("cases=%d pass=%d control=%s" % (
            len(CASES), passed,
            "FALSE-GREEN-REJECTED" if rejected else "FALSE-GREEN-ACCEPTED",
        ))
        return 0 if (passed == len(CASES) and rejected) else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
