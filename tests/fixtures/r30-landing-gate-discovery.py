#!/usr/bin/env python3
"""External discovery-contract fixture for tools/souji-landing-gate.py (round 30, C2).

Usage: python3 -B tests/fixtures/r30-landing-gate-discovery.py [--tool PATH]
       TMPDIR must be set; every synthetic repository is built under it.

Frozen contract (census/round-30/records/preregistration.txt, C2 paragraph):

  D1 capture-only round: committed census/round-N/waves/**.md and no
     .ufo/waves/round-N/ -> checked_reports equals the .md count and no
     COULD-NOT-EVALUATE.
  D2 neither present -> COULD-NOT-EVALUATE is still printed.
  D3 both present -> .ufo/waves/round-N/ is read and the capture copy of the
     same report is not double-counted.
  D4 template tokens `census/round-%s/`, `corpus/lessons/round-<N>.md` and
     `census/round-{N}/x` are not LG-DANGLING-PTR.
  D5 a real dangling `census/round-29/does-not-exist.md` in the same file IS
     LG-DANGLING-PTR.
  D6 a `.ufo/waves/round-N/w1/X.md` pointer resolves when
     census/round-N/waves/w1/X.md is committed and is LG-DANGLING-PTR when it
     is not. Both halves are pinned against shortcuts: a same-basename capture
     of the evaluated round does not resolve it (the mapping is bound to the
     pointer's own round number), and a capture directory that exists without
     the pointed-at file does not resolve it either.
  D7 a capture-only report with an uncarried `STATUS: FAIL` line yields
     LG-SEAT-UNCARRIED.

Output: one `CASE D<k> PASS|FAIL <detail>` line per case (space-separated, so
`^CASE D<k> PASS` greps cleanly), then one `CONTROL ...` line, then the last
line `cases=N pass=M control=FALSE-GREEN-REJECTED|FALSE-GREEN-ACCEPTED`.
The control is an always-zero emitter (a stub tool printing one clean SUMMARY
with findings=0 and checked_reports=0 and nothing else) run through the same
seven cases; it must fail at least one of them.

Exit 0 iff every case passes and the control is rejected; 1 otherwise; 2 on a
missing prerequisite (tool absent, no git, TMPDIR unset or pointing inside a
git checkout).

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

ROUND = 30          # round under evaluation; capture lives at census/round-30/waves
MAPPED_ROUND = 31   # round named by a capture-mapped pointer, never evaluated here

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
            "GIT_AUTHOR_NAME": "r30-discovery-fixture",
            "GIT_AUTHOR_EMAIL": "r30@fixture.invalid",
            "GIT_COMMITTER_NAME": "r30-discovery-fixture",
            "GIT_COMMITTER_EMAIL": "r30@fixture.invalid",
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
        self._git("config", "user.name", "r30-discovery-fixture")
        self._git("config", "user.email", "r30@fixture.invalid")

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

    def ids(self):
        return [row.split("\t", 1)[0] for row in self.rows if row.startswith("LG-")]

    def has(self, finding_id, needle=None):
        for row in self.rows:
            if row.split("\t", 1)[0] != finding_id:
                continue
            if needle is None or needle in row:
                return True
        return False


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


def lesson(extra_lines=()):
    text = "# Round 30 lesson\n\nadmitted: false\n"
    if extra_lines:
        text += "\n" + "\n".join(extra_lines) + "\n"
    return text


CLEAN_REPORT = "# Seat\n\nSTATUS: ok - clean.\n"


def build_world(base, env, name):
    """Build one named synthetic repository. Return (path, head_rev)."""
    repo = Repo(base, name, env)
    repo.write("SKILL.md", SKILL)
    repo.write("corpus/lessons/round-30.md", lesson())

    if name == "d1":
        # D1: committed capture only, no .ufo/waves/round-30/ anywhere.
        repo.write(
            "census/round-30/waves/w1/SeatA.md", "# SeatA\n\nSTATUS: ok - clean.\n"
        )
        repo.write(
            "census/round-30/waves/w2/SeatB.md", "# SeatB\n\nSTATUS: ok - clean.\n"
        )
    elif name == "d2":
        # D2: neither the capture nor the wave dir exists.
        pass
    elif name == "d3":
        # D3: both present, same relative report path, different bytes. The
        # capture copy carries no STATUS line, so status_lines=1 proves the
        # .ufo bytes were read; one file name proves no double count.
        repo.write(
            ".ufo/waves/round-30/w1/SeatDup.md",
            "# SeatDup\n\nSTATUS: FAIL - synthetic failure not carried.\n",
        )
        repo.write(
            "census/round-30/waves/w1/SeatDup.md",
            "# SeatDup\n\nduplicate capture copy with no status marker\n",
        )
    elif name == "templates":
        # D4/D5 share this file: three template tokens plus one real dangling
        # pointer, in the same committed lesson.
        repo.write(
            "corpus/lessons/round-30.md",
            lesson(
                [
                    "Template tokens in prose: `census/round-%s/`, "
                    "`corpus/lessons/round-<N>.md`, `census/round-{N}/x`.",
                    "",
                    "Real dangling pointer in the same file: "
                    "`census/round-29/does-not-exist.md`.",
                ]
            ),
        )
        repo.write(".ufo/waves/round-30/w1/Seat.md", CLEAN_REPORT)
    elif name == "mapped":
        # D6 (resolving half): the capture of round 31 is committed.
        repo.write(
            "corpus/lessons/round-30.md",
            lesson(
                ["Capture-mapped pointer: `.ufo/waves/round-%d/w1/X.md`." % MAPPED_ROUND]
            ),
        )
        repo.write(
            "census/round-%d/waves/w1/X.md" % MAPPED_ROUND, CLEAN_REPORT
        )
        repo.write(".ufo/waves/round-30/w1/Seat.md", CLEAN_REPORT)
    elif name == "mapped-missing":
        # D6 (dangling half): same pointer. The capture of the pointer's own
        # round is never committed; a same-basename capture of the EVALUATED
        # round is, so an implementation that maps the round number away (or
        # matches by basename across rounds) resolves it and fails this half.
        repo.write(
            "corpus/lessons/round-30.md",
            lesson(
                ["Capture-mapped pointer: `.ufo/waves/round-%d/w1/X.md`." % MAPPED_ROUND]
            ),
        )
        repo.write("census/round-%d/waves/w1/X.md" % ROUND, CLEAN_REPORT)
        repo.write(".ufo/waves/round-30/w1/Seat.md", CLEAN_REPORT)
    elif name == "mapped-dir":
        # D6 (file-level half): the capture directory for the pointer's own
        # round exists, the pointed-at file does not. A resolution that tests
        # only the capture directory resolves it and fails this half.
        repo.write(
            "corpus/lessons/round-30.md",
            lesson(
                ["Capture-mapped pointer: `.ufo/waves/round-%d/w1/X.md`." % MAPPED_ROUND]
            ),
        )
        repo.write("census/round-%d/waves/w1/Other.md" % MAPPED_ROUND, CLEAN_REPORT)
        repo.write(".ufo/waves/round-30/w1/Seat.md", CLEAN_REPORT)
    elif name == "d7":
        # D7: capture-only report with an uncarried failure line.
        repo.write(
            "census/round-30/waves/w1/SeatFail.md",
            "# SeatFail\n\nSTATUS: FAIL - synthetic discovery failure.\n",
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


def judge(cid, worlds):
    """worlds: {world_name: Run}. Return list of problem strings (empty = pass)."""
    c = Checker()

    if cid == "D1":
        r = worlds["d1"]
        c.expect(not r.cne, "COULD-NOT-EVALUATE printed")
        c.expect(r.rc != 2, "exit=2")
        c.expect(r.summary("checked_reports") == 2,
                 "checked_reports=%s want 2" % r.summary("checked_reports"))
        c.expect(r.summary("status_lines") == 2,
                 "status_lines=%s want 2" % r.summary("status_lines"))
        c.expect(r.summary("findings") == 0,
                 "findings=%s want 0" % r.summary("findings"))
    elif cid == "D2":
        r = worlds["d2"]
        c.expect(r.cne, "no COULD-NOT-EVALUATE")
        c.expect(r.rc == 2, "exit=%d want 2" % r.rc)
        c.expect(r.summary("checked_reports") == 0,
                 "checked_reports=%s want 0" % r.summary("checked_reports"))
    elif cid == "D3":
        r = worlds["d3"]
        c.expect(not r.cne, "COULD-NOT-EVALUATE printed")
        c.expect(r.rc == 1, "exit=%d want 1" % r.rc)
        c.expect(r.summary("checked_reports") == 1,
                 "checked_reports=%s want 1 (double count?)"
                 % r.summary("checked_reports"))
        c.expect(r.summary("status_lines") == 1,
                 "status_lines=%s want 1 (.ufo bytes not read?)"
                 % r.summary("status_lines"))
        c.expect(r.has("LG-SEAT-UNCARRIED"), "missing LG-SEAT-UNCARRIED")
    elif cid == "D4":
        r = worlds["templates"]
        c.expect(not r.cne, "COULD-NOT-EVALUATE printed")
        for token in ("round-%s", "round-<N>", "round-{N}"):
            c.expect(not r.has("LG-DANGLING-PTR", token),
                     "template token flagged: %s" % token)
    elif cid == "D5":
        r = worlds["templates"]
        c.expect(r.rc == 1, "exit=%d want 1" % r.rc)
        c.expect(r.has("LG-DANGLING-PTR", "does-not-exist.md"),
                 "missing LG-DANGLING-PTR for census/round-29/does-not-exist.md")
    elif cid == "D6":
        needle = "round-%d/w1/X.md" % MAPPED_ROUND
        present = worlds["mapped"]
        missing = worlds["mapped-missing"]
        c.expect(not present.cne, "mapped: COULD-NOT-EVALUATE printed")
        c.expect(present.rc == 0, "mapped: exit=%d want 0" % present.rc)
        c.expect(not present.has("LG-DANGLING-PTR", needle),
                 "mapped: capture-backed pointer flagged")
        c.expect(not missing.cne, "mapped-missing: COULD-NOT-EVALUATE printed")
        c.expect(missing.rc == 1, "mapped-missing: exit=%d want 1" % missing.rc)
        c.expect(missing.has("LG-DANGLING-PTR", needle),
                 "mapped-missing: uncaptured pointer not flagged")
        dir_only = worlds["mapped-dir"]
        c.expect(not dir_only.cne, "mapped-dir: COULD-NOT-EVALUATE printed")
        c.expect(dir_only.rc == 1, "mapped-dir: exit=%d want 1" % dir_only.rc)
        c.expect(dir_only.has("LG-DANGLING-PTR", needle),
                 "mapped-dir: capture-directory-only resolution")
    elif cid == "D7":
        r = worlds["d7"]
        c.expect(not r.cne, "COULD-NOT-EVALUATE printed")
        c.expect(r.rc == 1, "exit=%d want 1" % r.rc)
        c.expect(r.summary("checked_reports") == 1,
                 "checked_reports=%s want 1" % r.summary("checked_reports"))
        c.expect(r.has("LG-SEAT-UNCARRIED"), "missing LG-SEAT-UNCARRIED")
    else:
        raise RuntimeError("unknown case %r" % cid)

    return c.problems


def detail_of(cid, worlds, problems):
    r = worlds[WORLD_OF[cid][0]]
    return "exit=%d reports=%s status=%s findings=%s%s" % (
        r.rc,
        r.summary("checked_reports"),
        r.summary("status_lines"),
        r.summary("findings"),
        "" if not problems else " FAIL(" + "; ".join(problems) + ")",
    )


CASES = ("D1", "D2", "D3", "D4", "D5", "D6", "D7")
WORLD_OF = {
    "D1": ["d1"],
    "D2": ["d2"],
    "D3": ["d3"],
    "D4": ["templates"],
    "D5": ["templates"],
    "D6": ["mapped", "mapped-missing", "mapped-dir"],
    "D7": ["d7"],
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


def toplevel_of(path):
    directory = path if os.path.isdir(path) else os.path.dirname(path)
    if not directory or not os.path.isdir(directory):
        return None
    proc = subprocess.run(
        ["git", "-C", directory, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        env=clean_env(),
    )
    if proc.returncode != 0:
        return None
    return os.path.realpath(proc.stdout.strip())


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
        for label, path in (("tool", tool), ("fixture", os.path.abspath(__file__))):
            top = toplevel_of(path)
            if top and inside(tmp_real, top):
                problems.append(
                    "TMPDIR %s is inside the %s git checkout %s" % (tmp_real, label, top)
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
        description="r30 landing-gate discovery fixture (C2 D1-D7)"
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

    scratch = tempfile.mkdtemp(prefix="r30-discovery-fixture-",
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
