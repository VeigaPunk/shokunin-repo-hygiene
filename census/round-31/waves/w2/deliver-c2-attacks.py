#!/usr/bin/env python3
"""SwarmReviewer10 w2: smallest hiding inputs for each new r31 C2 gate rule.

Builds one throwaway repo per case, runs the BASE gate (9f17a1e) and the TIP
gate (2c16d01) on the same commit, and prints rc / findings / SUMMARY for both.
"""
import os
import subprocess
import sys

SCRATCH = "/fast/scratch/hyaku/souji-r31/w2-SwarmReviewer10"
BASE_GATE = os.path.join(SCRATCH, "base-gate.py")
TIP_GATE = os.path.join(SCRATCH, "tip-gate.py")
WORLDS = os.path.join(SCRATCH, "worlds")

SKILL = "# Synthetic lane\n\nNo registry citations in this spotcheck.\n"

REPO_SELECTING = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
)


def clean_env(base):
    env = {k: v for k, v in os.environ.items() if k not in REPO_SELECTING}
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.path.join(base, "no-global-gitconfig"),
        "GIT_TERMINAL_PROMPT": "0",
        "HOME": os.path.join(base, "home"),
        "GIT_AUTHOR_NAME": "w2-reviewer10",
        "GIT_AUTHOR_EMAIL": "w2r10@scratch.invalid",
        "GIT_COMMITTER_NAME": "w2-reviewer10",
        "GIT_COMMITTER_EMAIL": "w2r10@scratch.invalid",
        "GIT_AUTHOR_DATE": "2026-10-26T00:00:00Z",
        "GIT_COMMITTER_DATE": "2026-10-26T00:00:00Z",
    })
    return env


class Repo(object):
    def __init__(self, env, name):
        self.path = os.path.join(WORLDS, name)
        subprocess.run(["rm", "-rf", self.path], check=True)
        os.makedirs(self.path)
        self.env = env
        self._git("init", "-q", "-b", "main")
        self._git("config", "commit.gpgsign", "false")
        self._git("config", "user.name", "w2-reviewer10")
        self._git("config", "user.email", "w2r10@scratch.invalid")

    def _git(self, *args):
        proc = subprocess.run(["git", "-C", self.path] + list(args),
                              capture_output=True, text=True, env=self.env)
        if proc.returncode != 0:
            raise RuntimeError("git %s failed: %s" % (args[0], proc.stderr[:300]))
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


def gate(tool, root, rev, extra=()):
    cmd = [sys.executable, "-B", tool,
           "--root", root, "--rev", rev, "--round", "31"] + list(extra)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    return proc.returncode, proc.stdout, proc.stderr


def summarize(tag, rc, out, err):
    rows = [l for l in out.splitlines() if l.strip()]
    summary = next((r for r in rows if r.startswith("SUMMARY")), "SUMMARY missing")
    findings = [r for r in rows if not r.startswith("SUMMARY")]
    cne = [l for l in err.splitlines() if l.startswith("COULD-NOT-EVALUATE")]
    print("  %s rc=%d" % (tag, rc))
    print("    %s" % summary)
    for f in findings:
        print("    %s" % f)
    for c in cne:
        print("    stderr: %s" % c)


def case(name, files):
    print("== %s" % name)
    env = clean_env(WORLDS)
    repo = Repo(env, name)
    for rel, text in files.items():
        repo.write(rel, text)
    rev = repo.commit("world " + name)
    summarize("BASE", *gate(BASE_GATE, repo.path, rev))
    summarize("TIP ", *gate(TIP_GATE, repo.path, rev))


def lesson(text, **extra):
    files = {"SKILL.md": SKILL, "corpus/lessons/round-31.md": text}
    files.update(extra)
    return files


SPOT = "corpus/lessons/round-31-verifier-spotcheck.md"
ZREPORT = ".ufo/waves/round-31/w1/Z.md"
ZFAIL = "# Z\n\nSTATUS: FAIL - z: real failure.\n"
# A carry line that quotes Z's failure paragraph and marks it open.
ZCARRY = '- .ufo/waves/round-31/w1/Z.md — "STATUS: FAIL - z: real failure." — open\n'
ACARRY = '- .ufo/waves/round-31/w1/A.md — "STATUS: FAIL - a: real failure." — open\n'
AFAIL = "# A\n\nSTATUS: FAIL - a: real failure.\n"
APASS = "# A\n\nSTATUS: PASS - a: clean.\n"


# 1. union dedupe with divergent bytes: wave copy PASS, capture copy FAIL.
case("dedupe-divergent", lesson(
    "# Round 31 lesson\n\nNo seat failures carried.\n",
    **{
        ".ufo/waves/round-31/w1/A.md": APASS,
        "census/round-31/waves/w1/A.md": "# A\n\nSTATUS: FAIL - b: capture copy.\n",
    },
))

# 2. fence rule gap: quoted carry section inside a ~~~ fence.
case("fence-tilde", lesson(
    "# Round 31 lesson\n\n"
    "Carry format example:\n\n"
    "~~~\n"
    "## Seat-reported failures\n\n"
    + ZCARRY +
    "~~~\n",
    **{ZREPORT: ZFAIL},
))

# 2b. fence rule gap: quoted carry section inside a 4-space indented block.
case("fence-indent", lesson(
    "# Round 31 lesson\n\n"
    "Carry format example:\n\n"
    "    ## Seat-reported failures\n\n"
    "    " + ZCARRY,
    **{ZREPORT: ZFAIL},
))

# 2c. fence rule works for ``` fences (control: quoted carry must NOT carry).
case("fence-backtick-control", lesson(
    "# Round 31 lesson\n\n"
    "Carry format example:\n\n"
    "```\n"
    "## Seat-reported failures\n\n"
    + ZCARRY +
    "```\n",
    **{ZREPORT: ZFAIL},
))

# 2d. fence rule false-fail direction: unclosed ``` fence before a real section.
case("fence-unclosed", lesson(
    "# Round 31 lesson\n\n"
    "Usage:\n\n"
    "```\n"
    "souji-landing-gate --root LANE --rev REV\n"
    "\n"
    "## Seat-reported failures\n\n"
    + ACARRY,
    **{".ufo/waves/round-31/w1/A.md": AFAIL},
))

# 2e. fence false-fail, realistic: a 4-space-indented ``` line is CONTENT
# (an indented code block showing a literal fence), but the gate toggles on
# it and the real carry section after it goes unread.
case("fence-indent-close", lesson(
    "# Round 31 lesson\n\n"
    "A fenced block looks like this:\n\n"
    "    ```\n"
    "    key = value\n"
    "\n"
    "## Seat-reported failures\n\n"
    + ACARRY,
    **{".ufo/waves/round-31/w1/A.md": AFAIL},
))

# 3. ellipsis rule: real dangling path cited with a trailing ellipsis.
case("ellipsis-trailing", lesson(
    "# Round 31 lesson\n\nNo seat failures carried.\n",
    **{
        SPOT: "# Round 31 spotcheck\n\n"
              "Never committed: `census/round-3/garbage-census.out...`.\n",
        ".ufo/waves/round-31/w1/A.md": APASS,
    },
))

# 3b. ellipsis rule: real dangling path with an embedded ellipsis.
case("ellipsis-embedded", lesson(
    "# Round 31 lesson\n\nNo seat failures carried.\n",
    **{
        SPOT: "# Round 31 spotcheck\n\n"
              "Never committed: `census/round-3/garbage...census.out`.\n",
        ".ufo/waves/round-31/w1/A.md": APASS,
    },
))

# 4. template rule: absent path whose name carries an incidental printf span.
case("template-incident", lesson(
    "# Round 31 lesson\n\nNo seat failures carried.\n",
    **{
        SPOT: "# Round 31 spotcheck\n\n"
              "Never committed: `corpus/notes/50%done.md`.\n",
        ".ufo/waves/round-31/w1/A.md": APASS,
    },
))

# 5. letters-only prose rule: absent extension-less all-letters path.
case("prose-letters", lesson(
    "# Round 31 lesson\n\nNo seat failures carried.\n",
    **{
        SPOT: "# Round 31 spotcheck\n\n"
              "Never committed: `corpus/knowledge/missingnote`.\n",
        ".ufo/waves/round-31/w1/A.md": APASS,
    },
))

# 6. captured mapping: stored-name twin committed outside any capture dir.
case("captured-anywhere", lesson(
    "# Round 31 lesson\n\nNo seat failures carried.\n",
    **{
        SPOT: "# Round 31 spotcheck\n\n"
              "Never committed: `tools/.gitignore`.\n",
        "tools/.gitignore.captured": "build/\n",
        ".ufo/waves/round-31/w1/A.md": APASS,
    },
))

# 7. :text slot residual: committed file cited with a nonexistent slot.
case("slot-unverified", lesson(
    "# Round 31 lesson\n\nNo seat failures carried.\n",
    **{
        SPOT: "# Round 31 spotcheck\n\n"
              "See `census/r31demo.txt:NOSUCHSLOT`.\n",
        "census/r31demo.txt": "alpha\nbeta\n",
        ".ufo/waves/round-31/w1/A.md": APASS,
    },
))

# 8. precision control: genuinely dangling path must stay reported.
case("clean-control", lesson(
    "# Round 31 lesson\n\nNo seat failures carried.\n",
    **{
        SPOT: "# Round 31 spotcheck\n\n"
              "Missing file: `tools/missing.py`.\n",
        ".ufo/waves/round-31/w1/A.md": APASS,
    },
))
