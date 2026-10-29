"""Shared helpers for the R42reviewer04 probes (C3 group B).

Scratch-only: every fixture lives under /fast/scratch/hyaku/souji-r42/R42reviewer04. Every git call
names -C; identity comes only from GIT_AUTHOR_*/GIT_COMMITTER_* in the environment; no git config.
"""
import os
import shutil
import subprocess
import sys
import time

SCRATCH = "/fast/scratch/hyaku/souji-r42/R42reviewer04"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42reviewer04"
PRISTINE = os.path.join(SEAT, "pristine-tool.py")  # copy of tools/souji-worktree-drift.py, sha256 b2a6...3e34dc6
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42reviewer04"
TMP = os.path.join(SCRATCH, "tmp")
GIT_ENV = {
    "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
    "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}
RECORD_OK = ("# r42 probe census\nREPO\talpha\tregs=2\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\n"
             "TOTAL\trepos=2\tregs=3\tprunable=0\n")


def mut(mid):
    return os.path.join(SEAT, "mut-%s.py" % mid)


def genv():
    e = dict(GIT_ENV)
    e["PATH"] = os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")
    e["TMPDIR"] = TMP
    return e


def git(d, *args):
    p = subprocess.run(["git", "-C", d] + list(args), env=genv(), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, check=False)
    if p.returncode != 0:
        raise RuntimeError("git -C %s %s rc=%d: %s" % (d, " ".join(args), p.returncode, p.stderr.strip()))
    return p.stdout


def mkrepo(path):
    os.makedirs(path, exist_ok=True)
    git(path, "init", "-q")
    top = git(path, "rev-parse", "--show-toplevel").strip()
    if os.path.realpath(top) != os.path.realpath(path):
        raise RuntimeError("toplevel mismatch %s != %s" % (top, path))
    git(path, "commit", "-q", "--allow-empty", "-m", "init")
    return path


def add_worktree(repo, wt, branch):
    os.makedirs(os.path.dirname(wt), exist_ok=True)
    git(repo, "worktree", "add", "-q", "-b", branch, wt)


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def fresh(*parts):
    d = os.path.join(SCRATCH, "probe", *parts)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    os.makedirs(TMP, exist_ok=True)
    return d


def build_fleet(base):
    """base/fleet: alpha (main + one worktree outside root, regs=2), beta (regs=1); base/record.tsv
    consistent with the live state; base/outside/gamma is a repo outside the root."""
    fleet = os.path.join(base, "fleet")
    os.makedirs(fleet)
    alpha = mkrepo(os.path.join(fleet, "alpha"))
    add_worktree(alpha, os.path.join(base, "wt", "alpha-wt"), "alpha-wt")
    mkrepo(os.path.join(fleet, "beta"))
    write(os.path.join(base, "record.tsv"), RECORD_OK)
    return fleet


def run(tool, argv, cwd, timeout=20):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": TMP,
         "LC_ALL": "C", "HOME": TMP}
    t0 = time.monotonic()
    try:
        p = subprocess.run([sys.executable, "-B", tool] + list(argv), cwd=cwd, env=e,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return {"rc": p.returncode, "out": p.stdout.decode("utf-8", "replace"),
                "err": p.stderr.decode("utf-8", "replace"), "hang": False,
                "secs": round(time.monotonic() - t0, 2)}
    except subprocess.TimeoutExpired as ex:
        return {"rc": None, "out": (ex.stdout or b"").decode("utf-8", "replace"),
                "err": (ex.stderr or b"").decode("utf-8", "replace"), "hang": True,
                "secs": round(time.monotonic() - t0, 2)}


def trial(tag, tool, setup, timeout=20):
    """setup(base) -> {"argv": [...], "cwd": path, "watch": [paths]}; runs tool in a fresh base."""
    base = fresh(tag)
    spec = setup(base)
    r = run(tool, spec["argv"], spec["cwd"], timeout)
    r["base"] = base
    r["files"] = {}
    for p in spec.get("watch", []):
        try:
            with open(p, "rb") as f:
                r["files"][os.path.basename(p)] = f.read().decode("utf-8", "replace").replace(base, "<BASE>")
        except OSError as exc:
            r["files"][os.path.basename(p)] = "MISSING (%s)" % exc.__class__.__name__
    return r


def norm(text, base):
    return text.replace(base, "<BASE>")


def key(r):
    return (r["rc"], r["hang"], norm(r["out"], r["base"]), norm(r["err"], r["base"]), r["files"])


def show(label, r):
    print("  %-10s rc=%s hang=%s secs=%s" % (label, r["rc"], r["hang"], r["secs"]))
    for line in norm(r["out"], r["base"]).splitlines()[:14]:
        print("    stdout| " + line)
    for line in norm(r["err"], r["base"]).splitlines()[-4:]:
        print("    stderr| " + line)
    for name, text in r["files"].items():
        print("    file %s: %d bytes; %s" % (name, len(text), text[:160].replace("\n", "\\n")))


def verdict(mid, p, m):
    differ = key(p) != key(m)
    print("VERDICT %s: %s" % (mid, "OBSERVABLE (pristine != mutant)" if differ else "NOT OBSERVABLE in this probe"))
    return 0 if differ else 1
