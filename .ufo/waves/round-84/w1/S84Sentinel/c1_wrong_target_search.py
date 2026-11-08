#!/usr/bin/env python3
"""S84Sentinel C1 wrong-target search: for each UNBOUND clause, find a concrete target path under which the
mutant resolves a file the FILED counter refuses.

The search builds a synthetic git repo (in scratch) holding byte-equal copies of the token's bytes at many
candidate target paths, then compares the filed counter's judge() verdict with the mutant's for each path. A path
where filed=REFUSED and mutant=MOVED is a WRONG FILE the population would certify (both populations score the
mutant green).

Usage: c1_wrong_target_search.py --work <empty dir>
"""
import argparse
import hashlib
import importlib.util
import itertools
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

CLAUSES = [
    ("c2-last-component",
     '        elif os.path.basename(target.rstrip("/")) != os.path.basename(token.rstrip("/")):\n'
     '            why = "target\'s last component differs from the token\'s"\n',
     '        elif False:\n            why = "c2 mutant"\n'),
    ("c7-census-in-census",
     '        elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" \\\n'
     '                and not _capture_ok(token, kr, target, tr):\n',
     '        elif False:\n'),
]


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=ENV)
    if p.returncode != 0:
        raise RuntimeError(f"git {args}: {p.stdout.decode()[:400]}")
    return p.stdout.decode()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.exists(work) and os.listdir(work):
        print(f"FATAL: --work {work} not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)

    payload = b"r84 sentinel wrong-target search payload\n"
    digest = "f:" + hashlib.sha256(payload).hexdigest()

    # token shapes to try (all under a census/ tree, so the c7 branch is reachable)
    tokens = ["census/round-61/waves/a2w1/S61ExecRealRecord/erratum-evidence.txt",
              "census/round-61/records/wave-a2w1/S61ExecRealRecord/erratum-evidence.txt",
              "census/round-61/wave/w1/S61ExecRealRecord/erratum-evidence.txt"]
    # target shapes: every directory layout under census/round-61/ and under a decoy wave dir
    dirs = ["waves/a2w1", "waves/a2w1/S61ExecRealRecord", "wave/w1", "wave/w1/S61ExecRealRecord",
            "records/wave-a2w1", "records/wave-a2w1/S61ExecRealRecord", "w2", "w2/a2w1",
            "w2/a2w1/S61ExecRealRecord", "w2/S61ExecRealRecord", "records/decoy", "records/decoy/a2w1",
            "records/decoy/S61ExecRealRecord", "waves/decoy", "waves/decoy/S61ExecRealRecord",
            "w1", "w1/a2w1", "w1/a2w1/S61ExecRealRecord"]
    names = ["erratum-evidence.txt", "erratum-evidence-RENAMED.txt", "other.txt"]

    # One repo per token shape, and the TOKEN PATH ITSELF IS NEVER CREATED at the rev (a MOVED row's token is
    # absent at the revision: it was moved away). Otherwise the counter returns CAPTURED before any class clause.
    repos = {}
    for ti, token in enumerate(tokens):
        repo = os.path.join(work, f"repo{ti}")
        os.makedirs(repo, exist_ok=True)
        with open(os.path.join(repo, "SCORECARD.md"), "w", encoding="utf-8") as f:
            f.write("pointer " + token + "\n")
        tokdir = os.path.dirname(os.path.join(repo, token))
        for d in dirs:
            p = os.path.join(repo, "census", "round-61", d)
            os.makedirs(p, exist_ok=True)
            for n in names:
                q = os.path.join(p, n)
                if os.path.join(repo, token) == q:
                    continue
                with open(q, "wb") as f:
                    f.write(payload)
        git(repo, "init", "-q", "--initial-branch=main")
        git(repo, "add", "-A")
        git(repo, "-c", "user.name=r84 sentinel", "-c", "user.email=s@example.invalid", "commit", "-q", "-m", "demo")
        repos[token] = (repo, git(repo, "rev-parse", "HEAD").strip())
        print(f"# token {token} -> repo rev={repos[token][1]} (the token path itself is absent at the rev)")

    base = open(COUNTER, encoding="utf-8").read()
    filed = load(COUNTER, "filed")
    muts = {}
    for cid, old, new in CLAUSES:
        assert base.count(old) == 1, (cid, base.count(old))
        mp = os.path.join(work, f"counter-{cid}.py")
        with open(mp, "w", encoding="utf-8") as f:
            f.write(base.replace(old, new))
        muts[cid] = load(mp, "mut_" + cid.replace("-", "_"))

    def verdict(mod, token, target):
        repo, rev = repos[token]
        blob = [f"pointer {token}"]
        st, why = mod.judge(repo, rev, repo, ("X01", "SCORECARD.md", "1", token, digest), ("MOVED", target), blob)
        return st, why

    for token in tokens:
        print(f"# token {token}")
        for cid, mod in muts.items():
            hits = []
            for d, n in itertools.product(dirs, names):
                target = f"census/round-61/{d}/{n}"
                sf, wf = verdict(filed, token, target)
                sm, wm = verdict(mod, token, target)
                if sf in ("REFUSED", "MISMATCH") and sm not in ("REFUSED", "MISMATCH"):
                    hits.append((target, sf, wf, sm, wm))
            print(f"  MUTANT {cid}: {len(hits)} wrong-file resolutions")
            for target, sf, wf, sm, wm in hits[:6]:
                print(f"    target={target}\n      filed  -> {sf} ({wf})\n      mutant -> {sm} ({wm})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
