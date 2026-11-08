#!/usr/bin/env python3
"""S87Critic probes: C2 header/last-line scope; C1 weaker-counter sanity.

Runs entirely under /fast/scratch/hyaku/souji-r87/S87Critic/probe.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOL = os.path.join(LANE, "tools/souji-record-agreement.py")
WRITER = os.path.join(LANE, "tools/souji-receipt-write.py")
S = "/fast/scratch/hyaku/souji-r87/S87Critic/probe"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "s87critic", "GIT_AUTHOR_EMAIL": "s87critic@invalid",
            "GIT_COMMITTER_NAME": "s87critic", "GIT_COMMITTER_EMAIL": "s87critic@invalid"})


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, env=ENV, **kw)


def git(repo, *args, check=True):
    assert os.path.isabs(repo), repo
    p = run(["git", "-C", repo, *args])
    if check and p.returncode != 0:
        raise SystemExit(f"git {args} rc={p.returncode}: {p.stderr[:300]}")
    return p


def tiny_repo(path):
    os.makedirs(path, exist_ok=True)
    git(path, "init", "-q", "-b", "master")
    top = git(path, "rev-parse", "--show-toplevel").stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(path), (top, path)
    with open(os.path.join(path, "keep.txt"), "w") as f:
        f.write("keep\n")
    git(path, "add", "keep.txt")
    git(path, "commit", "-q", "--no-verify", "-m", "seed")
    return git(path, "rev-parse", "HEAD").stdout.strip()


def probe_stderr_tail():
    spec = importlib.util.spec_from_file_location("sra", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    long_exc = "AttributeError: " + "x" * 300
    text = "Traceback (most recent call last):\n  File \"w\", line 1, in <module>\n" + long_exc
    tail = mod._stderr_tail(text)
    print("PROBE stderr_tail long_line len=%d has_AttributeError=%s first=%r"
          % (len(tail), "AttributeError" in tail, tail[:12]))
    short = mod._stderr_tail("Traceback (most recent call last):\nOSError: boom")
    print("PROBE stderr_tail short=%r" % short)
    multi = mod._stderr_tail("first\n\n   \nlast-line   ")
    print("PROBE stderr_tail last_nonempty=%r" % multi)


def probe_writer_stdout(rev):
    """A stub writer that prints to stdout and then raises: the K4 detail carries stdout, not stderr."""
    kit = os.path.join(S, "kit_stdout")
    os.makedirs(kit, exist_ok=True)
    shutil.copyfile(TOOL, os.path.join(kit, "souji-record-agreement.py"))
    with open(os.path.join(kit, "souji-receipt-write.py"), "w") as f:
        f.write("def _truth_refusal(root):\n"
                "    print('STUB-STDOUT-NOISE')\n"
                "    raise AttributeError('STUB-EXCEPTION-WAS-HERE')\n"
                "def _flag_refusal(root, tag, path):\n"
                "    raise AttributeError('STUB-FLAG-EXCEPTION')\n")
    p = run([sys.executable, "-B", os.path.join(kit, "souji-record-agreement.py"),
             "--root", os.path.join(S, "repo"), "--rev", rev], cwd=kit)
    k4 = [l for l in p.stdout.splitlines() if l.startswith("MISMATCH\tK4")]
    print("PROBE stdout_writer rc=%d k4=%r stdout_flag=%s"
          % (p.returncode, k4, [l for l in p.stdout.splitlines() if l.startswith("# writer")]))


def probe_writer_stderr(rev):
    """Control: same stub without the stdout print."""
    kit = os.path.join(S, "kit_stderr")
    os.makedirs(kit, exist_ok=True)
    shutil.copyfile(TOOL, os.path.join(kit, "souji-record-agreement.py"))
    with open(os.path.join(kit, "souji-receipt-write.py"), "w") as f:
        f.write("def _truth_refusal(root):\n"
                "    raise AttributeError('STUB-EXCEPTION-WAS-HERE')\n"
                "def _flag_refusal(root, tag, path):\n"
                "    raise AttributeError('STUB-FLAG-EXCEPTION')\n")
    p = run([sys.executable, "-B", os.path.join(kit, "souji-record-agreement.py"),
             "--root", os.path.join(S, "repo"), "--rev", rev], cwd=kit)
    k4 = [l for l in p.stdout.splitlines() if l.startswith("MISMATCH\tK4")]
    print("PROBE stderr_writer rc=%d k4=%r" % (p.returncode, k4))


def probe_rename(rev):
    """A rename whose ORIGIN path's third byte is a space: is the second NUL field really skipped?"""
    repo = os.path.join(S, "rename")
    os.makedirs(repo, exist_ok=True)
    git(repo, "init", "-q", "-b", "master")
    assert os.path.realpath(git(repo, "rev-parse", "--show-toplevel").stdout.strip()) == os.path.realpath(repo)
    with open(os.path.join(repo, "ab cd.txt"), "w") as f:
        f.write("origin\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--no-verify", "-m", "seed")
    git(repo, "mv", "ab cd.txt", "x.txt")
    raw = git(repo, "status", "--porcelain", "-z").stdout
    print("PROBE git_status_z fields=%r" % raw.split("\0"))
    kit = os.path.join(S, "kit_rename")
    os.makedirs(kit, exist_ok=True)
    shutil.copyfile(TOOL, os.path.join(kit, "souji-record-agreement.py"))
    shutil.copyfile(WRITER, os.path.join(kit, "souji-receipt-write.py"))
    r = git(repo, "rev-parse", "HEAD").stdout.strip()
    p = run([sys.executable, "-B", os.path.join(kit, "souji-record-agreement.py"), "--root", repo, "--rev", r],
            cwd=kit)
    k4 = [l for l in p.stdout.splitlines() if l.startswith("MISMATCH\tK4")]
    print("PROBE rename_tool rc=%d k4=%r" % (p.returncode, k4))


def main():
    os.makedirs(S, exist_ok=True)
    repo = os.path.join(S, "repo")
    rev = tiny_repo(repo)
    probe_stderr_tail()
    probe_writer_stdout(rev)
    probe_writer_stderr(rev)
    probe_rename(rev)
    return 0


if __name__ == "__main__":
    sys.exit(main())
