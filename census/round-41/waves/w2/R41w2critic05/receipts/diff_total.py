#!/usr/bin/env python3
"""Differential + oracle test: pinned tool vs base tool on random TOTAL orders and root variants.

usage: diff_total.py WORKDIR N SEED
Oracle (refusal = rc 2): any malformed line, no REPO rows, duplicate REPO name, or a TOTAL row
that disagrees with the REPO rows (pinned: ANY TOTAL row; base: only the LAST TOTAL row).
"""
import os
import random
import re
import subprocess
import sys

PINNED = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py"
BASE = "/fast/scratch/hyaku/souji-r41/R41w2critic05/base-tool.py"
WORK, N, SEED = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_AUTHOR_NAME": "d", "GIT_AUTHOR_EMAIL": "d@example.invalid",
    "GIT_COMMITTER_NAME": "d", "GIT_COMMITTER_EMAIL": "d@example.invalid",
}
ROW = re.compile(r"^REPO\t([^\t]+)\tregs=(\d+)\tprunable=(\d+)$")
TOT = re.compile(r"^TOTAL\trepos=(\d+)\tregs=(\d+)\tprunable=(\d+)$")


def sh(*cmd):
    subprocess.run(list(cmd), env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def repo(path):
    os.makedirs(path)
    sh("git", "init", "-q", "-b", "main", path)
    with open(os.path.join(path, "f"), "w") as h:
        h.write("x\n")
    sh("git", "-C", path, "add", "f")
    sh("git", "-C", path, "commit", "-qm", "b")


def oracle(body, names_on_disk):
    """Return (pinned_refuse, base_refuse) under the schema/TOTAL rules (ignoring drift)."""
    rows, totals, seen = [], [], set()
    for line in body.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        m = ROW.match(line)
        if m:
            if m.group(1) in seen:
                return True, True
            seen.add(m.group(1))
            rows.append((int(m.group(2)), int(m.group(3))))
            continue
        m = TOT.match(line)
        if m:
            totals.append(tuple(int(x) for x in m.groups()))
            continue
        return True, True
    if not rows:
        return True, True

    def bad(t):
        return t[0] != len(rows) or t[1] != sum(r[0] for r in rows) or t[2] != sum(r[1] for r in rows)
    pinned = any(bad(t) for t in totals)
    base = bool(totals) and bad(totals[-1])
    return pinned, base


def run_tool(tool, root, rec, extra):
    p = subprocess.run(["python3", "-B", tool, "--root", root, "--record", rec, "--timeout", "30", *extra],
                       env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    norm = lambda s: re.sub(r"record=\S+", "record=R", s)
    return p.returncode, norm(p.stdout), norm(p.stderr), ("Traceback" in p.stderr)


def main():
    import random as R
    R.seed(SEED)
    os.makedirs(WORK, exist_ok=True)
    plain = os.path.join(WORK, "plain")
    os.makedirs(plain)
    repo(os.path.join(plain, "alpha"))
    repo(os.path.join(plain, "beta"))
    rootrepo = os.path.join(WORK, "rootrepo")
    repo(rootrepo)
    repo(os.path.join(rootrepo, "alpha"))
    stats = {"runs": 0, "same": 0, "differ_expected": 0, "differ_unexpected": 0,
             "oracle_mismatch_pinned": 0, "oracle_mismatch_base": 0, "traceback": 0}
    unexpected, cases = [], []
    names_pool = ["alpha", "beta", "nope", "..", "alpha/..", "rootrepo"]
    for i in range(N):
        root_kind = R.choice(["plain", "rootrepo"])
        root = plain if root_kind == "plain" else rootrepo
        k = R.randint(1, 3)
        pool = ["alpha", "beta", "rootrepo"] if root_kind == "rootrepo" else ["alpha", "beta", "nope"]
        chosen = R.sample(pool, k)
        rows = []
        for nm in chosen:
            rows.append("REPO\t%s\tregs=%d\tprunable=%d" % (nm, R.choice([1, 1, 2]), R.choice([0, 0, 1])))
        sr = sum(int(r.split("regs=")[1].split("\t")[0]) for r in rows)
        sp = sum(int(r.split("prunable=")[1]) for r in rows)
        nt = R.randint(0, 4)
        tots = []
        for _ in range(nt):
            t = [len(rows), sr, sp]
            if R.random() < 0.5:
                f = R.randrange(3)
                t[f] += R.choice([-1, 1, 2])
            tots.append("TOTAL\trepos=%d\tregs=%d\tprunable=%d" % tuple(t))
        lines = rows + tots
        R.shuffle(lines)
        if R.random() < 0.15:
            lines.insert(R.randrange(len(lines) + 1), "# comment")
        body = "\n".join(lines) + "\n"
        rec = os.path.join(WORK, "rec-%d.tsv" % i)
        with open(rec, "w") as h:
            h.write(body)
        extra = ["--skip-unrecorded"] if R.random() < 0.5 else []
        pr = run_tool(PINNED, root, rec, extra)
        br = run_tool(BASE, root, rec, extra)
        stats["runs"] += 1
        p_ref = pr[0] == 2
        b_ref = br[0] == 2
        o_p, o_b = oracle(body, None)
        if p_ref != o_p:
            stats["oracle_mismatch_pinned"] += 1
            unexpected.append(("ORACLE-PINNED", body, root_kind, extra, pr, br))
        if b_ref != o_b:
            stats["oracle_mismatch_base"] += 1
        if pr[3] or br[3]:
            stats["traceback"] += 1
        if pr == br:
            stats["same"] += 1
        else:
            msg_only = p_ref and b_ref and "TOTAL" in pr[2] and "TOTAL" in br[2]
            if o_p != o_b or msg_only:  # the only intended difference class: a non-last TOTAL decides
                stats["differ_expected"] += 1
                cases.append((root_kind, extra, body, pr[0], br[0]))
            else:
                stats["differ_unexpected"] += 1
                unexpected.append(("DIFF", body, root_kind, extra, pr, br))
        os.unlink(rec)
    print("STATS", stats)
    print("expected-class differing records (examples):")
    for c in cases[:6]:
        print("  root=%s extra=%s rcP=%d rcB=%d\n    " % (c[0], c[1], c[3], c[4]) + c[2].replace("\n", " | "))
    print("UNEXPECTED:", len(unexpected))
    for u in unexpected[:10]:
        print(u)


main()
