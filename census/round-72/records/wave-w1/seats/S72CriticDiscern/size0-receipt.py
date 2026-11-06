#!/usr/bin/env python3
"""S72CriticDiscern receipt: size-0 .gitattributes re-hash frequency, git 2.56.0.

Reproduces the FWw shape (committed empty .gitattributes; worktree copy assigns itself
filter=e with a self-erasing clean) and the non-empty control, counting clean-filter
invocations per `git status --porcelain` read via a logging filter.
"""
import os, shutil, subprocess, time

S = "/fast/scratch/hyaku/souji-r72/S72CriticDiscern"
LOG_E = os.path.join(S, "rc-log-e.txt")
LOG_T = os.path.join(S, "rc-log-t.txt")
F_E = os.path.join(S, "rc-filter-e.sh")
F_T = os.path.join(S, "rc-filter-t.sh")


def env():
    e = {k: v for k, v in os.environ.items()
         if not k.startswith("GIT_") and k not in ("HOME", "XDG_CONFIG_HOME")}
    e.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
              "GIT_AUTHOR_DATE": "2026-11-06T12:00:00Z",
              "GIT_COMMITTER_DATE": "2026-11-06T12:00:00Z"})
    return e


def g(repo, *a):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, env=env())
    if r.returncode != 0:
        raise SystemExit(f"git {a} failed: {r.stderr.decode()}")
    return r.stdout.decode("utf-8", "replace")


def hits():
    return sum(1 for _ in open(LOG_E)) if os.path.exists(LOG_E) else 0


def build(case, committed, werk):
    d = os.path.join(S, case)
    shutil.rmtree(d, ignore_errors=True)
    repo = os.path.join(d, "repo")
    os.makedirs(os.path.join(repo, "tools"))
    g(repo, "init", "-q")
    top = os.path.realpath(g(repo, "rev-parse", "--show-toplevel").strip())
    assert top == os.path.realpath(repo), (top, repo)
    g(repo, "config", "user.name", "disc"); g(repo, "config", "user.email", "disc@invalid")
    open(os.path.join(repo, ".gitattributes"), "wb").write(committed)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(b"counter v1\n")
    g(repo, "add", "-A"); g(repo, "commit", "-q", "-m", "seed")
    g(repo, "config", "filter.e.clean", F_E)
    g(repo, "config", "filter.t.clean", F_T)
    open(os.path.join(repo, ".gitattributes"), "wb").write(werk)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(b"counter v2\n")
    return repo


def run(label, repo, sleep_first):
    if sleep_first:
        time.sleep(2.2)  # leave the racy-git same-second window
    blob = g(repo, "ls-files", "-s", ".gitattributes").split()[1]
    print(f"CASE {label}: idx_blob={blob} blob_size={g(repo,'cat-file','-s',blob).strip()} "
          f"wt_size={os.path.getsize(os.path.join(repo,'.gitattributes'))}")
    for i in (1, 2, 3):
        b = hits()
        st = g(repo, "status", "--porcelain")
        print(f"  status#{i}: filter_hits={hits()-b} porcelain={st.strip()!r}")
    print(f"  index_stat_size_after={g(repo,'ls-files','--debug','.gitattributes').split('size: ')[1].split()[0]} "
          f"hash_object_path={subprocess.run(['git','-C',repo,'hash-object','--path=.gitattributes',os.path.join(repo,'.gitattributes')],capture_output=True,env=env()).stdout.decode().strip()[:12]}")


def main():
    open(F_E, "w").write(f"#!/bin/sh\ncat >/dev/null\nprintf 'hit\\n' >> {LOG_E}\n")
    open(F_T, "w").write(f"#!/bin/sh\ncat | sed s/v2/v1/\nprintf 'hit\\n' >> {LOG_T}\n")
    os.chmod(F_E, 0o755); os.chmod(F_T, 0o755)
    for p in (LOG_E, LOG_T):
        if os.path.exists(p):
            os.unlink(p)
    self_attr = b".gitattributes filter=e\ntools/counter.py filter=t\n"
    run("A size-0 committed, worktree self-filtered (FWw shape), no sleep", build("RCA", b"", self_attr), False)
    run("C non-empty(7) committed, worktree longer, no sleep", build("RCC", b"# base\n", self_attr), False)
    run("G1 size-0 committed, worktree self-filtered, 2.2s sleep", build("RCG", b"", self_attr), True)


if __name__ == "__main__":
    main()
