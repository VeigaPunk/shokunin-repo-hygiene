#!/usr/bin/env python3
"""S84Sentinel C1 clause-coverage scanner + wrong-file demonstration.

Part 1 (coverage): for each refusal clause of census/round-84/c1-pointer-counter.py, build a single-edit mutant
that DROPS that clause, score it on BOTH pinned populations (r83 36 rows, r84 44 rows) with the frozen harness, and
report the clauses the populations do NOT bind (mutant scores GREEN on both).

Part 2 (wrong file): for every clause the populations leave unbound, build a synthetic git repo in scratch with a
DECOY move and show the FILED counter REFUSES it while the mutant MOVES it (resolves a wrong file). The lane's
population files are never edited.

Usage: c1_clause_coverage.py --work <empty dir>
"""
import argparse
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-84/c1-pointer-counter.py")
HARNESS = os.path.join(LANE, "census/round-84/c1-false-row-harness.py")
POP83 = os.path.join(LANE, "census/round-83/c1-false-rows.tsv")
POP84 = os.path.join(LANE, "census/round-84/c1-false-rows.tsv")
FLEET = "/home/vgpnk/Projects/shokunin"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r84 sentinel", "GIT_AUTHOR_EMAIL": "sentinel@example.invalid",
            "GIT_COMMITTER_NAME": "r84 sentinel", "GIT_COMMITTER_EMAIL": "sentinel@example.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})

# (id, the exact text of the refusal clause, its replacement)
CLAUSES = [
    ("c1-digest",
     '        elif rev_digest(root, rev, target) != frozen:\n            why = "target absent at rev or digest differs"\n',
     '        elif False:\n            why = "c1-digest mutant"\n'),
    ("c2-last-component",
     '        elif os.path.basename(target.rstrip("/")) != os.path.basename(token.rstrip("/")):\n            why = "target\'s last component differs from the token\'s"\n',
     '        elif False:\n            why = "c2-last-component mutant"\n'),
    ("c3-round",
     '        elif kr and (not tr or tr.group(1) != kr.group(1)):\n            why = "target names a different round than the token"\n',
     '        elif False:\n            why = "c3-round mutant"\n'),
    ("c4-own-tree-shape",
     '        elif kr and target[:tr.start(0)] == token[:kr.start(0)] and not _owntree_ok(token, kr, target, tr):\n',
     '        elif False:\n'),
    ("c5-capture-root",
     '        elif kr and target[:tr.start(0)] not in (token[:kr.start(0)], "census"):\n',
     '        elif False:\n'),
    ("c6-census-capture",
     '        elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] != "census" \\\n                and not _capture_ok(token, kr, target, tr):\n',
     '        elif False:\n'),
    ("c7-census-in-census",
     '        elif kr and target[:tr.start(0)] == "census" and token[:kr.start(0)] == "census" \\\n                and not _capture_ok(token, kr, target, tr):\n',
     '        elif False:\n'),
    ("c8-token-has-no-round",
     '        elif not kr:\n',
     '        elif False:\n'),
]


def score(counter, work, pop):
    p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", counter, "--lane", LANE, "--fleet-root", FLEET,
                        "--work", work, "--population", pop], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       cwd=LANE, env=ENV)
    out = p.stdout.decode("utf-8", "replace")
    summary = next((l for l in out.splitlines() if l.startswith("SUMMARY")), "(no SUMMARY)")
    m = re.search(r"mismatches=(\d+)", summary)
    return (int(m.group(1)) if m else -1), p.returncode, out


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=ENV)
    if p.returncode != 0:
        raise RuntimeError(f"git {args}: {p.stdout.decode()[:300]}")
    return p.stdout.decode()


def build_demo_repo(path):
    """A synthetic lane: a token that lives under census/round-61/ (the capture root) and a DECOY copy of the
    token's bytes in a non-capture directory under the same round tree."""
    os.makedirs(os.path.join(path, "census", "round-61", "waves", "a2w1"), exist_ok=True)
    os.makedirs(os.path.join(path, "census", "round-61", "records", "decoy"), exist_ok=True)
    payload = b"r84 sentinel wrong-file demo payload\n"
    tok = os.path.join(path, "census", "round-61", "waves", "a2w1", "S61ExecRealRecord", "erratum-evidence.txt")
    os.makedirs(os.path.dirname(tok), exist_ok=True)
    with open(tok, "wb") as f:
        f.write(payload)
    with open(os.path.join(path, "census", "round-61", "records", "decoy", "erratum-evidence.txt"), "wb") as f:
        f.write(payload)
    git(path, "init", "-q", "--initial-branch=main")
    git(path, "add", "-A")
    git(path, "-c", "user.name=r84 sentinel", "-c", "user.email=s@example.invalid", "commit", "-q", "-m", "demo")
    return git(path, "rev-parse", "HEAD").strip()


def forge_verdict(counter, root, rev, token, target, cls="MOVED"):
    """Run the counter's judge() on one hand-built item through its --forge path, using a scratch population file."""
    import hashlib
    import tempfile
    # a scratch population: one item whose file/line/token we control
    d = tempfile.mkdtemp(dir=os.environ.get("S84_TMP", "/fast/scratch/hyaku/souji-r84/S84Sentinel"))
    src = os.path.join(d, "POP.md")
    with open(src, "w", encoding="utf-8") as f:
        f.write(f"token {token}\n")
    pop = os.path.join(d, "pop.tsv")
    with open(pop, "w", encoding="utf-8") as f:
        f.write("X01\tPOP.md\t1\t" + token + "\t-\n")
    led = os.path.join(d, "ledger.tsv")
    with open(led, "w", encoding="utf-8") as f:
        f.write("# id\tclass\ttarget\tnote\n")
    forge = os.path.join(d, "forge.tsv")
    with open(forge, "w", encoding="utf-8") as f:
        f.write(f"F1\tX01\t{cls}\t{target}\tREFUSED\n")
    p = subprocess.run([sys.executable, "-B", counter, "--root", root, "--rev", rev, "--fleet-root", d,
                        "--population", pop, "--ledger", led, "--forge", forge], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, cwd=root, env=ENV)
    out = p.stdout.decode("utf-8", "replace")
    m = re.search(r"^FORGE F1 .*?got=(\S+)", out, re.M)
    return (m.group(1) if m else "?"), out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.exists(work) and os.listdir(work):
        print(f"FATAL: --work {work} not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    os.environ["S84_TMP"] = work
    with open(COUNTER, encoding="utf-8") as f:
        base = f.read()
    print("# part 1: clause coverage over BOTH pinned populations (mismatches=0 => the clause is UNBOUND)")
    unbound = []
    for cid, old, new in CLAUSES:
        n = base.count(old)
        if n != 1:
            print(f"CLAUSE {cid} SKIPPED: old text occurs {n} times")
            continue
        mp = os.path.join(work, f"counter-{cid}.py")
        with open(mp, "w", encoding="utf-8") as f:
            f.write(base.replace(old, new))
        m83, rc83, _ = score(mp, os.path.join(work, "w83-" + cid), POP83)
        m84, rc84, _ = score(mp, os.path.join(work, "w84-" + cid), POP84)
        green = (rc83 == 0 and rc84 == 0)
        tag = "UNBOUND" if green else "bound"
        if green:
            unbound.append((cid, mp))
        print(f"CLAUSE {cid:<22} r83 mismatches={m83} rc={rc83} | r84 mismatches={m84} rc={rc84}  -> {tag}")
    print(f"# clauses the populations leave UNBOUND: {[c for c, _ in unbound]}")

    print("# part 2: for every unbound clause, does the mutant resolve a WRONG file the filed counter refuses?")
    demo = os.path.join(work, "demo-repo")
    os.makedirs(demo)
    rev = build_demo_repo(demo)
    token = "census/round-61/waves/a2w1/S61ExecRealRecord/erratum-evidence.txt"
    decoy = "census/round-61/records/decoy/erratum-evidence.txt"
    filed, out = forge_verdict(COUNTER, demo, rev, token, decoy)
    print(f"  filed counter on the decoy move: got={filed}")
    for cid, mp in unbound:
        got, _ = forge_verdict(mp, demo, rev, token, decoy)
        print(f"  mutant {cid}: got={got}  ({'WRONG FILE RESOLVED' if got not in ('REFUSED','MISMATCH') else 'still refused'})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
