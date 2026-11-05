"""Shared harness for the S60SentinelRound probes. Read-only helpers + isolated fixture repos.

Every fixture repo is created under an explicit --work directory the caller owns; nothing here
writes outside it. Git is invoked with an allowlisted environment and an explicit `-C <repo>`.
"""
import os
import shutil
import subprocess
import sys

GIT_ENV = {
    "PATH": "/usr/bin:/bin",
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_AUTHOR_NAME": "probe",
    "GIT_AUTHOR_EMAIL": "probe@example.invalid",
    "GIT_COMMITTER_NAME": "probe",
    "GIT_COMMITTER_EMAIL": "probe@example.invalid",
}


def git(repo, *args, env=None, check=True):
    e = dict(GIT_ENV)
    if env:
        e.update(env)
    p = subprocess.run(["git", "-C", repo] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=e, check=False)
    if check and p.returncode != 0:
        raise RuntimeError("git %s failed rc=%d: %s" % (" ".join(args), p.returncode,
                                                        p.stderr.decode("utf-8", "replace")))
    return p


def out(p):
    return p.stdout.decode("utf-8", "replace").strip()


def make_repo(path):
    """Create a fresh repo at path and assert git agrees the toplevel is exactly path."""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    git(path, "init", "-q")
    top = os.path.realpath(out(git(path, "rev-parse", "--show-toplevel")))
    want = os.path.realpath(path)
    if top != want:
        raise SystemExit("FIXTURE-GUARD: git toplevel %r != %r" % (top, want))
    return path


def write(repo, rel, data):
    fp = os.path.join(repo, rel)
    parent = os.path.dirname(fp)
    if parent:
        os.makedirs(parent, exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(fp, mode) as fh:
        fh.write(data)
    return fp


def commit(repo, msg="c"):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)
    return out(git(repo, "rev-parse", "HEAD"))


def run(argv, cwd=None, env=None, timeout=60):
    """Run a tool argv (no shell). Returns (rc, stdout, stderr)."""
    e = {"PATH": "/usr/bin:/bin:/usr/local/bin", "LC_ALL": "C", "HOME": cwd or "/nonexistent",
         "PYTHONDONTWRITEBYTECODE": "1"}
    if env:
        e.update(env)
    try:
        p = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=e, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"
    except OSError as exc:
        return 127, "", "OSError: %s" % exc
    return (p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"))


class Probe:
    def __init__(self, name):
        self.name = name
        self.rows = []

    def check(self, cid, ok, detail):
        self.rows.append((cid, bool(ok), detail))
        print("%-28s %-8s %s" % (cid, "PASS" if ok else "FAIL", detail))

    def note(self, text):
        print("NOTE %s" % text)

    def finish(self):
        bad = [r for r in self.rows if not r[1]]
        print("PROBE %s checks=%d fail=%d" % (self.name, len(self.rows), len(bad)))
        return 0 if not bad else 1


def scratch_root(argv):
    """Require an explicit work dir: never inherit TMPDIR."""
    if "--work" not in argv:
        raise SystemExit("usage: %s --work DIR [--tool PATH]" % sys.argv[0])
    i = argv.index("--work")
    return os.path.abspath(argv[i + 1])


def opt(argv, flag, default=None):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default
