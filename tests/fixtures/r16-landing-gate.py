#!/usr/bin/env python3
"""External self-invocation fixture for tools/souji-landing-gate.py (round 16, C2).

Usage: python3 tests/fixtures/r16-landing-gate.py [--tool PATH]

The gate contract exercised here (per the round-16 LandingGate item plus the
two L1 steers):

    python3 tools/souji-landing-gate.py --root LANE --rev REV --round N [--base REV]

TSV output: one `ID\tpath\tdetail` row per finding, then
`SUMMARY\tfindings=K\tchecked_reg=A\tchecked_pins=B\tchecked_markers=C\tchecked_reports=R`.
Exit 0 no findings, 1 findings, 2 could-not-evaluate.

Finding ids: LG-PARSE-REG (SKILL.md-cited .sh fails `bash -n` — including
stderr-only warnings — or cited .py fails compile()), LG-MISSING-REG,
LG-PARSE-CHANGED (.sh/.py added/modified in --base..--rev fails to parse),
LG-FROZEN-PIN (tests/fixtures/*-frozen/expected.json `files` pins; keys starting
tools/ tests/ census/ corpus/ resolve at the snapshot root ONLY, other keys
inside the frozen dir ONLY; plus record_sha256), LG-FROZEN-MEASURED (pin bytes
vs record.json measured_commit), LG-SEAT-UNCARRIED (STATUS: lines whose first
word is outside the benign allowlist, plus parse/do-not-ship/snapshot_tampered
phrase markers outside ``` fences and table rows, not carried verbatim under
the lesson's `## Seat-reported failures` heading on an `open`/`resolved@<hex>`
line; HTML comments stripped), LG-OPEN-ADMITTED (open marker while the lesson
says admitted: true). Missing .ufo/waves/round-N/ at REV -> exit 2.

Cases:
 1. historical replay: --root <lane> --rev b410186 --round 15 must exit 1 with
    LG-PARSE-REG for tools/souji-census.sh, LG-FROZEN-PIN for the
    r15-preservation-frozen tools/souji-census.sh pin, and
    LG-SEAT-UNCARRIED for .ufo/waves/round-15/w1/ConfigRepair.md.
 2. held-out synthetic repos built under /var/tmp (none copied from the gate's
    own selftest): unterminated `case`, module-level `return` + tab/space
    IndentationError, truncated heredoc, missing cited path + --base change,
    pin whose lane-rooted key exists only inside the frozen dir, pin matching
    REV but not measured_commit, marker vs lesson differing by one character,
    reworded/decorated STATUS and phrase markers, HTML-comment carry,
    open+admitted:true, missing wave dir (exit 2), and a clean repo where
    every check is exercised on >=1 passing item (negative controls).
 3. vacuity guard: a --tool that exits 0 printing nothing must fail this
    fixture (proven in-fixture by evaluating the same assertions against the
    stub's empty output).

Exit 0 iff every case passes, 1 on any failed case, 2 on missing prerequisite
(tool absent, no git, lane root not a git worktree).

Boundary: this fixture only runs the selected gate binary against real git
repositories it creates under a private /var/tmp directory (removed in
finally) and, for the replay case, against the lane's committed history via
the gate itself. It never runs tools/souji-census.sh and never touches
census/operator-sweep-20261019/, ~/.omp, .ufo/state or MANIFEST.json.
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
DEFAULT_TOOL = os.path.join(LANE, "tools", "souji-landing-gate.py")
REPLAY_REV = "b410186"
REPLAY_ROUND = 15
ROUND = 77  # synthetic round number; never collides with real wave dirs

GIT_ENV = {
    "GIT_AUTHOR_NAME": "r16-landing-gate-fixture",
    "GIT_AUTHOR_EMAIL": "r16@fixture.invalid",
    "GIT_COMMITTER_NAME": "r16-landing-gate-fixture",
    "GIT_COMMITTER_EMAIL": "r16@fixture.invalid",
    "GIT_AUTHOR_DATE": "2026-10-20T00:00:00Z",
    "GIT_COMMITTER_DATE": "2026-10-20T00:00:00Z",
    "GIT_CONFIG_NOSYSTEM": "1",
    "HOME": "/nonexistent-fixture-home",
}

SKILL_TMPL = """# Synthetic lane

Run `bash {cited}` for the check.
"""


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(repo, *args):
    env = dict(os.environ)
    env.update(GIT_ENV)
    p = subprocess.run(["git", "-C", str(repo)] + list(args),
                       capture_output=True, text=True, env=env)
    if p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args),
                                                  p.stderr.strip()))
    return p.stdout.strip()


def w(repo, rel, text):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)


class Repo(object):
    """A throwaway git repository used as gate --root input."""

    def __init__(self, root, name):
        self.path = os.path.join(root, name)
        os.makedirs(self.path)
        git(self.path, "init", "-q", "-b", "main")
        git(self.path, "config", "commit.gpgsign", "false")

    def write(self, rel, text):
        w(self.path, rel, text)

    def commit(self, msg="c"):
        git(self.path, "add", "-A")
        git(self.path, "commit", "-q", "-m", msg, "--allow-empty")
        return git(self.path, "rev-parse", "HEAD")

    def waves(self, files):
        """files: {basename: text} committed under .ufo/waves/round-77/w1/."""
        for name, text in files.items():
            self.write(".ufo/waves/round-%d/w1/%s" % (ROUND, name), text)

    def lesson(self, body_lines):
        """body_lines appended after the carry heading in corpus/lessons/round-77.md."""
        text = "# round %d lesson\n\nadmitted: false\n\n## Seat-reported failures\n\n" % ROUND
        text += "\n".join(body_lines) + "\n"
        self.write("corpus/lessons/round-%d.md" % ROUND, text)


class Gate(object):
    def __init__(self, tool):
        self.tool = tool

    def argv(self):
        if self.tool.endswith(".py"):
            return [sys.executable, self.tool]
        return [self.tool]

    def run(self, root, rev, rnd, base=None, tool=None):
        argv = ([sys.executable, tool] if (tool and tool.endswith(".py"))
                else [tool] if tool else self.argv())
        cmd = argv + ["--root", str(root), "--rev", str(rev),
                      "--round", str(rnd)]
        if base:
            cmd += ["--base", str(base)]
        try:
            return subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=180)
        except FileNotFoundError as e:
            class P(object):
                returncode = 127
                stdout = ""
                stderr = str(e)
            return P()


def rows_of(proc):
    return [ln for ln in proc.stdout.splitlines() if ln.strip()]


def has(rows, fid, *alts):
    for ln in rows:
        head = ln.split("\t", 1)[0]
        if head == fid and any(a in ln for a in alts):
            return True
    return False


def evaluate(proc, exp_rc, need, absent):
    """Return (ok, detail). need/absent entries: (id, (substr,...))."""
    fails = []
    rows = rows_of(proc)
    if proc.returncode != exp_rc:
        fails.append("exit=%d want %d (stderr=%s)"
                     % (proc.returncode, exp_rc, proc.stderr.strip()[:120]))
    for fid, alts in need:
        if not has(rows, fid, *alts):
            fails.append("missing %s ~ %s" % (fid, "/".join(alts)))
    for fid, alts in absent:
        if has(rows, fid, *alts):
            fails.append("unexpected %s ~ %s" % (fid, "/".join(alts)))
    n = sum(1 for ln in rows if ln.startswith("LG-"))
    detail = "exit=%d lg_rows=%d" % (proc.returncode, n)
    if fails:
        detail += " FAIL(" + "; ".join(fails) + ")"
    return (not fails, detail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", default=DEFAULT_TOOL)
    args = ap.parse_args()
    tool = os.path.abspath(args.tool)

    prereq = []
    if not os.path.isfile(tool):
        prereq.append("tool not found: %s" % tool)
    if shutil.which("git") is None:
        prereq.append("git not found on PATH")
    if not os.path.isdir(os.path.join(LANE, ".git")):
        prereq.append("lane root is not a git worktree: %s" % LANE)
    if prereq:
        for msg in prereq:
            print("PREREQ\tFAIL\t%s" % msg)
        print("SUMMARY\ttotal=0\tfailed=%d" % len(prereq))
        return 2

    gate = Gate(tool)
    results = []

    def case(cid, proc, exp_rc, need=(), absent=()):
        ok, detail = evaluate(proc, exp_rc, need, absent)
        results.append((cid, ok, detail))
        print("CASE\t%s\t%s\t%s" % (cid, "PASS" if ok else "FAIL", detail))
        return ok

    scratch = tempfile.mkdtemp(prefix="souji-r16-lgfixture-",
                               dir="/var/tmp" if os.path.isdir("/var/tmp")
                               else None)
    try:
        # --- Case 1: historical replay ------------------------------------
        case("replay-b410186",
             gate.run(LANE, REPLAY_REV, REPLAY_ROUND), 1,
             need=[("LG-PARSE-REG", ("tools/souji-census.sh",)),
                   ("LG-FROZEN-PIN", ("tools/souji-census.sh",
                                    "r15-preservation-frozen")),
                   ("LG-SEAT-UNCARRIED", ("ConfigRepair.md",)),
                   ("SUMMARY", ("checked_reports=",))])

        # --- Case 2: cited .sh whose only defect is an unterminated case ---
        r = Repo(scratch, "ucase")
        r.write("SKILL.md", SKILL_TMPL.format(
            cited="tools/registry.sh tools/ok.sh tools/ok.py"))
        r.write("tools/registry.sh",
                "#!/bin/sh\ncase \"$1\" in\n  a) echo a;;\n")
        r.write("tools/ok.sh", "#!/bin/sh\necho ok\n")
        r.write("tools/ok.py", "print('ok')\n")
        r.waves({"SeatA.md": "# seat\n\nSTATUS: ok\n"})
        r.lesson([])
        rev = r.commit("unterminated case")
        case("unterminated-case",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-PARSE-REG", ("tools/registry.sh",))],
             absent=[("LG-PARSE-REG", ("tools/ok.sh", "tools/ok.py"))])

        # --- Case 3: cited .py defects only compile() catches ---------------
        r = Repo(scratch, "pydefects")
        r.write("SKILL.md", SKILL_TMPL.format(
            cited="tools/indented.py tools/returns.py"))
        r.write("tools/indented.py", "def f():\n    a = 1\n\tb = 2\n")
        r.write("tools/returns.py", "x = 1\nreturn 0\n")
        r.waves({"SeatA.md": "# seat\n\nSTATUS: clean\n"})
        r.lesson([])
        rev = r.commit("py defects")
        case("py-compile-defects",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-PARSE-REG", ("tools/indented.py",)),
                   ("LG-PARSE-REG", ("tools/returns.py",))])

        # --- Case 4: cited .sh truncated mid-heredoc ------------------------
        # bash -n exits 0 but warns on stderr; the gate must treat stderr as a
        # finding (r15 failure mode: edit truncated mid-write).
        r = Repo(scratch, "heredoc")
        r.write("SKILL.md", SKILL_TMPL.format(cited="tools/hd.sh"))
        r.write("tools/hd.sh",
                "#!/bin/sh\ncat <<EOF\nline one\nline two\n")
        r.waves({"SeatA.md": "# seat\n\nSTATUS: done\n"})
        r.lesson([])
        rev = r.commit("truncated heredoc")
        case("truncated-heredoc",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-PARSE-REG", ("tools/hd.sh",))])

        # --- Case 5: missing cited path + uncited --base change --------------
        r = Repo(scratch, "missing-changed")
        r.write("SKILL.md", SKILL_TMPL.format(
            cited="tools/ghost.sh tools/ok.sh"))
        r.write("tools/ok.sh", "#!/bin/sh\necho ok\n")
        r.write("tools/uncited.sh", "#!/bin/sh\necho fine\n")
        r.waves({"SeatA.md": "# seat\n\nSTATUS: pass\n"})
        r.lesson([])
        base = r.commit("base")
        r.write("tools/uncited.sh",
                "#!/bin/sh\nif true; then\n  echo broken\n")
        rev = r.commit("break uncited")
        case("missing-reg-and-changed",
             gate.run(r.path, rev, ROUND, base=base), 1,
             need=[("LG-MISSING-REG", ("tools/ghost.sh",)),
                   ("LG-PARSE-CHANGED", ("tools/uncited.sh",))],
             absent=[("LG-PARSE-REG", ("tools/uncited.sh",))])
        # Same REV without --base: the uncited breakage is invisible by design;
        # only the missing cited path remains.
        case("uncited-nobase-invisible",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-MISSING-REG", ("tools/ghost.sh",))],
             absent=[("LG-PARSE-CHANGED", ("tools/uncited.sh",)),
                     ("LG-PARSE-REG", ("tools/uncited.sh",))])

        # --- Case 6: pin whose lane-rooted key exists only inside frozen dir -
        r = Repo(scratch, "pinshadow")
        r.write("SKILL.md", SKILL_TMPL.format(cited="tools/real.sh"))
        r.write("tools/real.sh", "#!/bin/sh\necho real\n")
        r.waves({"SeatA.md": "# seat\n\nSTATUS: ok\n"})
        r.lesson([])
        pinned = "#!/bin/sh\necho pinned\n"
        notes = "notes for the frozen dir\n"
        r.write("tests/fixtures/shadow-frozen/tools/pinned.sh", pinned)
        r.write("tests/fixtures/shadow-frozen/notes.txt", notes)
        c1 = r.commit("frozen dir contents")
        record = '{"measured_commit": "%s", "schema": "x"}\n' % c1
        r.write("tests/fixtures/shadow-frozen/record.json", record)
        expected = ('{\n'
                    '  "files": {\n'
                    '    "tools/pinned.sh": "%s",\n'
                    '    "notes.txt": "%s"\n'
                    '  },\n'
                    '  "record": "record.json",\n'
                    '  "record_sha256": "%s"\n'
                    '}\n' % (sha256_text(pinned), sha256_text(notes),
                             sha256_text(record)))
        r.write("tests/fixtures/shadow-frozen/expected.json", expected)
        rev = r.commit("pin")
        # tools/pinned.sh does NOT exist at the snapshot root: lane-rooted keys
        # resolve at root only, so this must be LG-FROZEN-PIN; the dir-local
        # notes.txt pin is satisfied and must not fire.
        case("pin-only-inside-frozen-dir",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-FROZEN-PIN", ("tools/pinned.sh",))],
             absent=[("LG-FROZEN-PIN", ("notes.txt",))])

        # --- Case 7: pin matches REV but not record.measured_commit ----------
        r = Repo(scratch, "measured")
        r.write("SKILL.md", SKILL_TMPL.format(cited="tools/meas.py"))
        r.write("tools/meas.py", "print('v1')\n")
        r.waves({"SeatA.md": "# seat\n\nSTATUS: ok\n"})
        r.lesson([])
        c1 = r.commit("v1")
        v2 = "print('v2')\n"
        r.write("tools/meas.py", v2)
        record = '{"measured_commit": "%s", "schema": "x"}\n' % c1
        r.write("tests/fixtures/meas-frozen/record.json", record)
        expected = ('{\n'
                    '  "files": { "tools/meas.py": "%s" },\n'
                    '  "record": "record.json",\n'
                    '  "record_sha256": "%s"\n'
                    '}\n' % (sha256_text(v2), sha256_text(record)))
        r.write("tests/fixtures/meas-frozen/expected.json", expected)
        rev = r.commit("v2")
        case("pin-vs-measured-commit",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-FROZEN-MEASURED", ("tools/meas.py",))],
             absent=[("LG-FROZEN-PIN", ("tools/meas.py",))])

        # --- Case 8: marker differs from the lesson by one character ---------
        r = Repo(scratch, "onechar")
        r.write("SKILL.md", SKILL_TMPL.format(cited="tools/ok.sh"))
        r.write("tools/ok.sh", "#!/bin/sh\necho ok\n")
        r.waves({
            "SeatA.md": "# seat A\n\nSTATUS: INCOMPLETE — frobnicate the journal\n",
            "SeatB.md": "# seat B\n\nSTATUS: BLOCKED — jam seal the register\n",
        })
        c1 = r.commit("markers")
        # SeatA's line is carried with one character changed (journal ->
        # jouxrnal): must still be uncarried. SeatB's is carried exactly with
        # a resolved@ disposition pointing at a real ancestor commit.
        r.lesson([
            "STATUS: INCOMPLETE — frobnicate the jouxrnal — open",
            "STATUS: BLOCKED — jam seal the register — resolved@%s" % c1,
        ])
        rev = r.commit("lesson")
        case("marker-one-char-off",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-SEAT-UNCARRIED", ("SeatA",))],
             absent=[("LG-SEAT-UNCARRIED", ("SeatB",))])

        # --- Case 9: reworded/decorated STATUS and phrase markers ------------
        r = Repo(scratch, "reword")
        r.write("SKILL.md", SKILL_TMPL.format(cited="tools/ok.sh"))
        r.write("tools/ok.sh", "#!/bin/sh\necho ok\n")
        r.waves({
            "SeatA.md": "# a\n\n**STATUS:** INCOMPLETE — service does not run\n",
            "SeatB.md": "# b\n\nSTATUS: fails selftest 11/13\n",
            "SeatC.md": "# c\n\nThe file in tree doesn't parse.\n",
            "SeatD.md": "# d\n\nnote: do not ship this\n",
            "SeatE.md": "# e\n\nSTATUS — INCOMPLETE — colonless form\n",
            "SeatF.md": ("# f\n\n```\nSTATUS: ok inside fence\n"
                         "does not parse inside fence\n```\n\n"
                         "| code | cause |\n|---|---|\n"
                         "| 2 | syntax error, missing file |\n"),
        })
        r.lesson([])
        rev = r.commit("rewordings")
        case("marker-rewordings",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-SEAT-UNCARRIED", ("SeatA",)),
                   ("LG-SEAT-UNCARRIED", ("SeatB",)),
                   ("LG-SEAT-UNCARRIED", ("SeatC",)),
                   ("LG-SEAT-UNCARRIED", ("SeatD",)),
                   ("LG-SEAT-UNCARRIED", ("SeatE",))],
             absent=[("LG-SEAT-UNCARRIED", ("SeatF",))])

        # --- Case 10: marker carried only inside an HTML comment -------------
        r = Repo(scratch, "htmlcomment")
        r.write("SKILL.md", SKILL_TMPL.format(cited="tools/ok.sh"))
        r.write("tools/ok.sh", "#!/bin/sh\necho ok\n")
        r.waves({"SeatA.md":
                 "# seat\n\nSTATUS: INCOMPLETE — comment carry test\n"})
        r.lesson([
            "<!-- STATUS: INCOMPLETE — comment carry test — open -->",
        ])
        rev = r.commit("comment carry")
        case("carry-inside-html-comment",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-SEAT-UNCARRIED", ("SeatA",))])

        # --- Case 11: open marker while lesson says admitted: true ----------
        r = Repo(scratch, "openadmit")
        r.write("SKILL.md", SKILL_TMPL.format(cited="tools/ok.sh"))
        r.write("tools/ok.sh", "#!/bin/sh\necho ok\n")
        r.waves({"SeatA.md":
                 "# seat\n\nSTATUS: INCOMPLETE — admission window broken\n"})
        r.write("corpus/lessons/round-%d.md" % ROUND,
                "# round %d lesson\n\nadmitted: true\n\n"
                "## Seat-reported failures\n\n"
                "STATUS: INCOMPLETE — admission window broken — open\n"
                % ROUND)
        rev = r.commit("open admitted")
        case("open-marker-admitted-true",
             gate.run(r.path, rev, ROUND), 1,
             need=[("LG-OPEN-ADMITTED",
                    ("SeatA", "round-%d" % ROUND, "Seat-reported"))])

        # --- Case 12: missing wave dir -> exit 2 -----------------------------
        r = Repo(scratch, "nowaves")
        r.write("SKILL.md", SKILL_TMPL.format(cited="tools/ok.sh"))
        r.write("tools/ok.sh", "#!/bin/sh\necho ok\n")
        rev = r.commit("no wave dir")
        case("missing-wave-dir",
             gate.run(r.path, rev, ROUND), 2)

        # --- Case 13: clean repo — every check exercised on a passing item ---
        r = Repo(scratch, "green")
        r.write("SKILL.md", SKILL_TMPL.format(
            cited="tools/m.sh tools/m.py"))
        r.write("tools/m.sh", "#!/bin/sh\necho ok\n")
        r.write("tools/m.py", "print('ok')\n")
        r.waves({
            "SeatA.md": "# seat\n\nSTATUS: INCOMPLETE — widget red\n",
            "Notes.md": "# notes\n\nSTATUS: none\n",
        })
        r.write("tests/fixtures/m-frozen/notes.txt", "frozen notes\n")
        c1 = r.commit("green base")
        record = '{"measured_commit": "%s", "schema": "x"}\n' % c1
        r.write("tests/fixtures/m-frozen/record.json", record)
        expected = ('{\n'
                    '  "files": {\n'
                    '    "tools/m.sh": "%s",\n'
                    '    "notes.txt": "%s"\n'
                    '  },\n'
                    '  "record": "record.json",\n'
                    '  "record_sha256": "%s"\n'
                    '}\n' % (sha256_text("#!/bin/sh\necho ok\n"),
                             sha256_text("frozen notes\n"),
                             sha256_text(record)))
        r.write("tests/fixtures/m-frozen/expected.json", expected)
        r.lesson([
            "STATUS: INCOMPLETE — widget red — resolved@%s" % c1,
        ])
        rev = r.commit("green head")
        case("clean-all-green",
             gate.run(r.path, rev, ROUND, base=c1), 0,
             need=[("SUMMARY", ("findings=0",))],
             absent=[("LG-PARSE-REG", ("",)),
                     ("LG-MISSING-REG", ("",)),
                     ("LG-PARSE-CHANGED", ("",)),
                     ("LG-FROZEN-PIN", ("",)),
                     ("LG-FROZEN-MEASURED", ("",)),
                     ("LG-SEAT-UNCARRIED", ("",)),
                     ("LG-OPEN-ADMITTED", ("",))])

        # --- Case 14: vacuity guard ------------------------------------------
        # A tool that exits 0 printing nothing satisfies no assertion above;
        # running this fixture with it as --tool must therefore FAIL. Prove it
        # in-fixture by re-evaluating the replay assertions against the stub.
        stub = os.path.join(scratch, "empty-tool.py")
        with open(stub, "w") as f:
            f.write("import sys\nsys.exit(0)\n")
        stub_proc = gate.run(LANE, REPLAY_REV, REPLAY_ROUND, tool=stub)
        ok, detail = evaluate(stub_proc, 1,
                              need=[("LG-PARSE-REG", ("tools/souji-census.sh",)),
                                    ("LG-FROZEN-PIN", ("tools/souji-census.sh",
                                                       "r15-preservation-frozen")),
                                    ("LG-SEAT-UNCARRIED", ("ConfigRepair.md",))],
                              absent=())
        vacuous = (stub_proc.returncode == 0
                   and not stub_proc.stdout.strip())
        passed = vacuous and not ok
        detail = ("stub rc=%d stdout_bytes=%d; replay assertions failed as "
                  "required: %s" % (stub_proc.returncode,
                                    len(stub_proc.stdout),
                                    "yes" if not ok else "NO"))
        results.append(("vacuity-stub", passed, detail))
        print("CASE\tvacuity-stub\t%s\t%s"
              % ("PASS" if passed else "FAIL", detail))

    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    failed = sum(1 for _, ok, _ in results if not ok)
    print("SUMMARY\ttotal=%d\tfailed=%d" % (len(results), failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
