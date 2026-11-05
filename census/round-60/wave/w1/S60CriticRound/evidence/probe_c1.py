#!/usr/bin/env python3
"""C1 probe: does the base freeze-checker accept a forged Control receipt, and what does
`--substance` do at the base tool bytes?"""
import hashlib, os, shutil, subprocess, sys, tempfile

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOL = os.path.join(LANE, "tools/souji-freeze-check.py")
BASE_REV = "1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4"
ENV = {"PATH": os.environ["PATH"], "HOME": "/fast/scratch/hyaku/souji-r60/S60CriticRound/home",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
       "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
       "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid"}

def git(d, *a):
    return subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=ENV, check=True).stdout.decode().strip()

def commit(d, files):
    for p, c in files.items():
        fp = os.path.join(d, p)
        os.makedirs(os.path.dirname(fp) or d, exist_ok=True)
        with open(fp, "wb") as fh:
            fh.write(c if isinstance(c, bytes) else c.encode())
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", "c")
    return git(d, "rev-parse", "HEAD")

def sha(b):
    return hashlib.sha256(b).hexdigest()

def build(tmp, name, ctl_bytes):
    d = os.path.join(tmp, name)
    os.mkdir(d)
    git(d, "init", "-q")
    base = commit(d, {"a.py": "a\n"})
    c = b"c\n"
    p = b"h\nr\n"
    prereg = ("Round: 60\n\n## C1\n"
              "Base: %s\n"
              "Counter: c.py sha256=%s\n"
              "Population: p.tsv sha256=%s\n"
              "Control: ctl.txt\n"
              "Target: t\n"
              "Kill: k\n") % (base, sha(c), sha(p))
    commit(d, {"prereg.txt": prereg, "c.py": c, "p.tsv": p, "ctl.txt": ctl_bytes})
    return d, base

def run(tool_args):
    p = subprocess.run([sys.executable, "-B", TOOL] + tool_args,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    return p.returncode, p.stdout.decode(), p.stderr.decode()

def main():
    tmp = tempfile.mkdtemp(prefix="c1probe-", dir="/fast/scratch/hyaku/souji-r60/S60CriticRound")
    os.makedirs(os.path.join(os.path.dirname(tmp), "home"), exist_ok=True)
    try:
        zero = "0" * 64
        cases = {
            # honest: instrument digest + rev are truthful, last line EXIT=1
            "honest": None,
            # kind-only forgery: only a red last line, no binding at all
            "forgery-kind-only": b"EXIT=1\n",
        }
        # digest forgery: instrument_sha256 names a different blob
        cases["forgery-digest"] = None
        # rev forgery: rev = the freeze commit itself (not a strict ancestor)
        cases["forgery-rev-at-freeze"] = None
        # rev missing
        cases["forgery-rev-missing"] = None
        # command names another tool
        cases["forgery-command-other"] = None
        out = []
        for name, ctl in cases.items():
            d, base = build(tmp, name, b"")
            freeze = git(d, "rev-parse", "HEAD")
            good = ("instrument=c.py\ninstrument_sha256=%s\nrev=%s\ncommand=c1-counter.py\nEXIT=1\n"
                    % (sha(b"c\n"), base))
            if name == "honest":
                ctl = good
            elif name == "forgery-digest":
                ctl = ("instrument=c.py\ninstrument_sha256=%s\nrev=%s\ncommand=c1-counter.py\nEXIT=1\n"
                       % (zero, base))
            elif name == "forgery-rev-at-freeze":
                ctl = ("instrument=c.py\ninstrument_sha256=%s\nrev=%s\ncommand=c1-counter.py\nEXIT=1\n"
                       % (sha(b"c\n"), freeze))
            elif name == "forgery-rev-missing":
                ctl = ("instrument=c.py\ninstrument_sha256=%s\ncommand=c1-counter.py\nEXIT=1\n"
                       % sha(b"c\n"))
            elif name == "forgery-command-other":
                ctl = ("instrument=c.py\ninstrument_sha256=%s\nrev=%s\ncommand=other-tool.py\nEXIT=1\n"
                       % (sha(b"c\n"), base))
            with open(os.path.join(d, "ctl.txt"), "wb") as fh:
                fh.write(ctl if isinstance(ctl, bytes) else ctl.encode())
            git(d, "add", "-A")
            git(d, "commit", "-q", "-m", "ctl")
            rev = git(d, "rev-parse", "HEAD")
            rc, so, se = run(["--root", d, "--prereg", "prereg.txt", "--rev", rev])
            rc2, so2, se2 = run(["--root", d, "--prereg", "prereg.txt", "--rev", rev, "--substance"])
            out.append("CASE %-24s base_rc=%d base_summary=%r substance_rc=%d substance_err=%r"
                       % (name, rc, so.strip().splitlines()[-1] if so.strip() else "",
                          rc2, se2.strip().splitlines()[-1] if se2.strip() else ""))
        print("\n".join(out))
        # --substance at the base tool with no fixture: unknown flag?
        rc3, so3, se3 = run(["--root", LANE, "--prereg", "census/round-59/preregistration.txt",
                             "--rev", BASE_REV, "--substance"])
        print("BASE_TOOL_SUBSTANCE rc=%d stderr=%r" % (rc3, se3.strip().splitlines()[-1] if se3.strip() else ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

main()
