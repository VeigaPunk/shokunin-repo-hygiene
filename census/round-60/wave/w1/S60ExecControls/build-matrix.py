#!/usr/bin/env python3
"""C1 matrix builder (souji round 60 pre-freeze controls, seat S60ExecControls).

Minimal equivalent of the S60ExecMatrix seat's frozen builder: at control time
that seat had delivered nothing into .ufo/waves/round-60/w1/, so this module
rebuilds the SAME frozen 8-case design from the wave spec (3 honest accept,
5 forgery refuse) as synthetic git repositories under a caller-owned work dir.

Case repo shape (every git call names -C <case repo>; toplevel asserted equal
to the case dir BEFORE the first commit; throwaway identity is env-scoped and
used only inside fixture repos):

  c0  BASE0   a.txt                strict ancestor; honest-3 control rev
  c1  PRE1    notes/notes.md       strict ancestor; honest-1 control rev
  c*  ORPHAN  commit-tree(c1 tree) resolves, is NOT an ancestor of freeze
  c2  FREEZE  pre.txt c.py p.tsv ctl*.txt   first commit adding the preregistration
  c3  TIP     post/post.txt        measured revision handed to the tool

Control receipts are column-0 lines. Honest receipts bind instrument=c.py,
instrument_sha256=sha256(c.py blob at freeze), rev=<strict ancestor of freeze>,
command naming the counter, last line EXIT=1. The five forgeries each break
exactly one binding named in the class column of c1-matrix.tsv.

Disclosed stand-in: the wave spec's `forgery-rev-at-freeze` row says
`rev = the freeze commit itself`. A commit cannot contain its own id
(self-referential sha256), so the case uses an orphan commit that resolves but
is not before the freeze - the exact condition CONTROL-REV-NOT-BEFORE-FREEZE
refuses. Named limit in the seat report.

Standalone use:  python3 -B build-matrix.py --work DIR [--tsv OUT.tsv]
"""
import argparse
import hashlib
import os
import subprocess

ROWS = [
    ("honest-1", "accept", "ctl.txt", ""),
    ("honest-2", "accept", "ctl1.txt,ctl2.txt", ""),
    ("honest-3", "accept", "ctl.txt", ""),
    ("forgery-kind-only", "refuse", "ctl.txt", "CONTROL-INSTRUMENT-MISSING"),
    ("forgery-digest", "refuse", "ctl.txt", "CONTROL-INSTRUMENT-MISMATCH"),
    ("forgery-rev-at-freeze", "refuse", "ctl.txt", "CONTROL-REV-NOT-BEFORE-FREEZE"),
    ("forgery-rev-missing", "refuse", "ctl.txt", "CONTROL-REV-MISSING"),
    ("forgery-command-other", "refuse", "ctl.txt", "CONTROL-COMMAND-MISMATCH"),
]

COUNTER_BYTES = "print('counter v60-substance-subject')\n"
POPULATION_BYTES = "h\nr\n"

STUB_ALWAYS_ACCEPT = (
    "#!/usr/bin/env python3\n"
    '"""stub control: always accepts (exit 0, no findings)."""\n'
    "import sys\n"
    "sys.exit(0)\n"
)
STUB_ALWAYS_REFUSE = (
    "#!/usr/bin/env python3\n"
    '"""stub control: always refuses (exit 1)."""\n'
    "import sys\n"
    "print('FINDING S0 STUB-ALWAYS-REFUSE refuses every case')\n"
    "sys.exit(1)\n"
)


def git_env():
    return {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
            "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_AUTHOR_NAME": "r60-controls", "GIT_AUTHOR_EMAIL": "r60-controls@fixture.invalid",
            "GIT_COMMITTER_NAME": "r60-controls", "GIT_COMMITTER_EMAIL": "r60-controls@fixture.invalid"}


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=git_env())
    if p.returncode != 0:
        raise RuntimeError("git -C %s %s -> %d: %s" % (repo, " ".join(args), p.returncode,
                                                       p.stderr.decode("utf-8", "replace").strip()))
    return p.stdout.decode("utf-8", "replace").strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tsv_bytes() -> bytes:
    lines = ["\t".join(("case", "expect", "control_receipt", "class"))]
    lines.extend("\t".join(row) for row in ROWS)
    return ("\n".join(lines) + "\n").encode("utf-8")


def commit_files(d, files):
    for rel, data in files.items():
        fp = os.path.join(d, rel)
        parent = os.path.dirname(fp)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(fp, "wb") as fh:
            fh.write(data.encode("utf-8") if isinstance(data, str) else data)
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "r60 c1 matrix case")
    return git(d, "rev-parse", "HEAD")


def case_text(name, base0, pre1, orphan, sha_c, sha_p):
    """(preregistration text, {receipt path: receipt bytes}) for one case."""
    def block(control_path, label):
        return ("## %s\nBase: %s\nCounter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\n"
                "Control: %s\nTarget: t\nKill: k\n" % (label, base0, sha_c, sha_p, control_path))

    def ctl(rev=None, digest=None, command="python3 -B c.py --selftest", lines=None, instrument="c.py"):
        if lines is not None:
            return lines
        return ("instrument=%s\ninstrument_sha256=%s\nrev=%s\ncommand=%s\nEXIT=1\n"
                % (instrument, digest, rev, command))

    pre = "Round: 60\n\n"
    if name == "honest-1":
        return pre + block("ctl.txt", "C1"), {"ctl.txt": ctl(rev=pre1, digest=sha_c)}
    if name == "honest-2":
        return (pre + block("ctl1.txt", "C1") + "\n" + block("ctl2.txt", "C2"),
                {"ctl1.txt": ctl(rev=pre1, digest=sha_c),
                 "ctl2.txt": ctl(rev=base0, digest=sha_c)})
    if name == "honest-3":
        return pre + block("ctl.txt", "C1"), {"ctl.txt": ctl(rev=base0, digest=sha_c)}
    if name == "forgery-kind-only":
        return pre + block("ctl.txt", "C1"), {"ctl.txt": "EXIT=1\n"}
    if name == "forgery-digest":
        # instrument_sha256 of a DIFFERENT blob (p.tsv, not c.py)
        return pre + block("ctl.txt", "C1"), {"ctl.txt": ctl(rev=pre1, digest=sha_p)}
    if name == "forgery-rev-at-freeze":
        # resolves, but is not a strict ancestor of the freeze (orphan stand-in, see docstring)
        return pre + block("ctl.txt", "C1"), {"ctl.txt": ctl(rev=orphan, digest=sha_c)}
    if name == "forgery-rev-missing":
        return pre + block("ctl.txt", "C1"), {"ctl.txt": (
            "instrument=c.py\ninstrument_sha256=%s\ncommand=python3 -B c.py --selftest\nEXIT=1\n" % sha_c)}
    if name == "forgery-command-other":
        return (pre + block("ctl.txt", "C1"),
                {"ctl.txt": ctl(rev=pre1, digest=sha_c,
                                command="python3 -B other-tool.py --selftest")})
    raise KeyError(name)


def build_cases(work):
    """Build the 8 case repos and the 2 stub tools under work.

    Returns (cases, stubs): cases maps name -> {dir, base0, pre1, orphan,
    freeze, tip, sha_counter, sha_population}; stubs maps tag -> script path.
    """
    cases = {}
    sha_c = sha256(COUNTER_BYTES.encode("utf-8"))
    sha_p = sha256(POPULATION_BYTES.encode("utf-8"))
    for row in ROWS:
        name = row[0]
        d = os.path.join(work, "case-" + name)
        os.makedirs(d)
        subprocess.run(["git", "-C", d, "init", "-q"], check=True, env=git_env(),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        top = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=git_env())
        top_out = top.stdout.decode("utf-8", "replace").strip()
        if top.returncode != 0 or os.path.realpath(top_out) != os.path.realpath(d):
            raise RuntimeError("fixture rule violated: toplevel %r != case dir %s" % (top_out, d))
        base0 = commit_files(d, {"a.txt": "a\n"})
        pre1 = commit_files(d, {"notes/notes.md": "notes\n"})
        tree1 = git(d, "rev-parse", "HEAD^{tree}")
        orphan = git(d, "commit-tree", tree1, "-m", "orphan: resolves, not an ancestor of any branch")
        pre, ctls = case_text(name, base0, pre1, orphan, sha_c, sha_p)
        freeze = commit_files(d, dict({"pre.txt": pre, "c.py": COUNTER_BYTES,
                                       "p.tsv": POPULATION_BYTES}, **ctls))
        tip = commit_files(d, {"post/post.txt": "post\n"})
        cases[name] = {"dir": d, "base0": base0, "pre1": pre1, "orphan": orphan,
                       "freeze": freeze, "tip": tip, "sha_counter": sha_c,
                       "sha_population": sha_p}
    stubs = {}
    for tag, body in (("always-accept", STUB_ALWAYS_ACCEPT), ("always-refuse", STUB_ALWAYS_REFUSE)):
        sp = os.path.join(work, "stub-%s.py" % tag)
        with open(sp, "w", encoding="utf-8") as fh:
            fh.write(body)
        stubs[tag] = sp
    return cases, stubs


def main():
    ap = argparse.ArgumentParser(description="Build the round-60 C1 matrix fixture repos.")
    ap.add_argument("--work", required=True)
    ap.add_argument("--tsv", default=None, help="write the frozen matrix TSV to this path")
    args = ap.parse_args()
    os.makedirs(args.work, exist_ok=True)
    cases, _ = build_cases(args.work)
    if args.tsv:
        with open(args.tsv, "wb") as fh:
            fh.write(tsv_bytes())
    for name in cases:
        c = cases[name]
        print("CASE-BUILT %s freeze=%s tip=%s" % (name, c["freeze"][:12], c["tip"][:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
