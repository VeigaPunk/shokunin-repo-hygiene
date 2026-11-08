#!/usr/bin/env python3
"""S84Sentinel C1 wrong-file demonstration: the c7 clause ("a census/round-<N> target must be a wave capture
keeping the token's full path suffix") is UNBOUND by BOTH pinned populations (measured: a mutant that drops it
scores mismatches=0 on the 36-row r83 population AND on the 44-row r84 population), and dropping it makes the
counter RESOLVE A WRONG FILE.

The demonstration calls the FILED counter's own judge() on a hand-built synthetic case (a synthetic git repo in
scratch). The lane's population files are never edited; the counter module is imported read-only.

Usage: c1_wrong_file_demo.py --work <empty dir>
"""
import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-84/c1-pointer-counter.py")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r84 sentinel", "GIT_AUTHOR_EMAIL": "sentinel@example.invalid",
            "GIT_COMMITTER_NAME": "r84 sentinel", "GIT_COMMITTER_EMAIL": "sentinel@example.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=ENV)
    if p.returncode != 0:
        raise RuntimeError(f"git {args}: {p.stdout.decode()[:400]}")
    return p.stdout.decode()


def load_counter(path):
    spec = importlib.util.spec_from_file_location("c1counter_probe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_repo(path):
    """The token census/round-61/waves/a2w1/S61ExecRealRecord/erratum-evidence.txt is ABSENT at the rev (it was
    moved away); a byte-equal copy sits at census/round-61/w2/a2w1/S61ExecRealRecord/erratum-evidence.txt, which
    is under a real wave dir but NOT under a capture subtree (waves/, wave/, records/wave-<w>/)."""
    os.makedirs(path, exist_ok=True)
    payload = b"r84 sentinel c7 demo payload\n"
    decoy = os.path.join(path, "census", "round-61", "w2", "a2w1", "S61ExecRealRecord", "erratum-evidence.txt")
    os.makedirs(os.path.dirname(decoy), exist_ok=True)
    with open(decoy, "wb") as f:
        f.write(payload)
    token = "census/round-61/waves/a2w1/S61ExecRealRecord/erratum-evidence.txt"
    with open(os.path.join(path, "SCORECARD.md"), "w", encoding="utf-8") as f:
        f.write(f"pointer {token}\n")
    git(path, "init", "-q", "--initial-branch=main")
    git(path, "add", "-A")
    git(path, "-c", "user.name=r84 sentinel", "-c", "user.email=s@example.invalid", "commit", "-q", "-m", "demo")
    return git(path, "rev-parse", "HEAD").strip(), token, payload


def judge_with(mod, root, rev, token, target, blob, frozen):
    # judge()'s item tuple is (id, file, line, token, frozen); `line` is a STRING (base-file line number) and
    # `frozen` is the token's frozen digest (as the population row supplies it).
    item = ("X01", "SCORECARD.md", "1", token, frozen)
    st, why = mod.judge(root, rev, root, item, ("MOVED", target), blob)
    return st, why


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--counter", default=COUNTER)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.exists(work) and os.listdir(work):
        print(f"FATAL: --work {work} not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    repo = os.path.join(work, "repo")
    rev, token, payload = build_repo(repo)
    blob = [f"pointer {token}"]
    frozen = "f:" + hashlib.sha256(payload).hexdigest()
    decoy = "census/round-61/w2/a2w1/S61ExecRealRecord/erratum-evidence.txt"
    print(f"# synthetic repo rev={rev}")
    print(f"# token   (absent at rev): {token}")
    print(f"# target  (decoy present) : {decoy}")

    filed = load_counter(ns.counter)
    st, why = judge_with(filed, repo, rev, token, decoy, blob, frozen)
    print(f"FILED counter  -> {st}  {why}")

    # the c7 mutant: drop the census-in-census clause
    base = open(ns.counter, encoding="utf-8").read()
    old = ('        elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" \\\n'
           '                and not _capture_ok(token, kr, target, tr):\n')
    assert base.count(old) == 1, base.count(old)
    mp = os.path.join(work, "counter-c7-dropped.py")
    with open(mp, "w", encoding="utf-8") as f:
        f.write(base.replace(old, '        elif False:\n'))
    mut = load_counter(mp)
    st2, why2 = judge_with(mut, repo, rev, token, decoy, blob, frozen)
    print(f"C7-DROPPED     -> {st2}  {why2}")
    verdict = "WRONG FILE RESOLVED (claim: the population certifies a rule that resolves a wrong file)" \
        if st2 not in ("REFUSED", "MISMATCH") else "still refused"
    print(f"VERDICT: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
