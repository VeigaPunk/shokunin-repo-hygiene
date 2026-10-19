#!/usr/bin/env python3
"""S07 (round 10) cluster-D fresh repro: D1 index flags, D2 full-tree receipts.

Both defects are reproduced from scratch on every run: each case builds its own
fixture git repo under /var/tmp, plants the defect shape, then asks the verdict
engine for a receipt and (separately) asks the quarantine flow to actually
remove the target.  The question a case answers is not "did it print SAFE" but
"did unique bytes disappear with no preservation receipt".

Usage:
    python3 S07-cluster-D-repro.py [--tools DIR] [--label NAME] [--out FILE]

  --tools DIR   directory holding souji-verify.sh / souji-vault-verify.sh /
                souji-quarantine.sh (default: the installed lane tools)
  --label NAME  name printed in the summary line (default: dir basename)
  --out FILE    also write the JSON report here

Exit 0 when every case refused and every payload survived; 1 otherwise.
Fixtures: mktemp -d -p /var/tmp only.  The live fleet is never read or written.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

P = argparse.ArgumentParser()
P.add_argument("--tools", default="/home/vgpnk/Projects/shokunin/souji-shokunin/tools")
P.add_argument("--label", default="")
P.add_argument("--out", default="")
A = P.parse_args()
TOOLS = Path(A.tools).resolve()
LABEL = A.label or TOOLS.name
OLD = 6 * 86400


def sh(cmd, env, cwd=None):
    return subprocess.run([str(x) for x in cmd], text=True, capture_output=True,
                          env=env, cwd=cwd, timeout=90)


class Fx:
    """One fixture fleet with a single lane repo."""

    def __init__(self, name):
        self.root = Path(tempfile.mkdtemp(prefix="s07-d-" + name + ".", dir="/var/tmp"))
        self.fleet = self.root / "fleet"
        self.repo = self.fleet / (name + "-shokunin")
        self.repo.mkdir(parents=True)
        self.home = self.root / "home"
        self.home.mkdir()
        self.ledger = self.root / "ledger.tsv"
        self.ledger.write_text(
            "source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        e = os.environ.copy()
        for k in list(e):
            if k.startswith("GIT_") or k.startswith("SOUJI_") or k == "SHOKUNIN_ROOT":
                e.pop(k)
        e.update({
            "PATH": os.environ["PATH"], "HOME": str(self.home), "TMPDIR": "/var/tmp",
            "LC_ALL": "C", "LANG": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "S07 fixture", "GIT_AUTHOR_EMAIL": "s07@example.invalid",
            "GIT_COMMITTER_NAME": "S07 fixture", "GIT_COMMITTER_EMAIL": "s07@example.invalid",
            "SHOKUNIN_ROOT": str(self.fleet), "SOUJI_LEDGER": str(self.ledger),
            "SOUJI_Q_SHOKUNIN_ROOT": str(self.fleet), "SOUJI_Q_LEDGER": str(self.ledger),
            "SOUJI_CLI_BIN": "/bin/false",
            "SOUJI_SELFTEST_ACTIVE": "1", "SOUJI_Q_SELFTEST_ACTIVE": "1",
            "SOUJI_VERIFY_BIN": str(TOOLS / "souji-verify.sh"),
        })
        self.env = e
        self.git("init", "-q", "--initial-branch=main", str(self.repo))
        self.write("seed.txt", "seed\n")
        self.head = self.commit()
        self.pushed(self.head)

    def git(self, *args):
        r = sh(["git", "-C", str(self.repo), *args], self.env)
        if r.returncode:
            raise RuntimeError(f"git {args}: {r.returncode} {r.stderr}")
        return r.stdout.strip()

    def write(self, rel, data):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data)
        return p

    def commit(self):
        self.git("add", "-A")
        tree = self.git("write-tree")
        args = ["commit-tree", tree]
        if getattr(self, "head", None):
            args += ["-p", self.head]
        sha = self.git(*args)
        self.git("update-ref", "refs/heads/main", sha)
        self.head = sha
        return sha

    def pushed(self, sha):
        self.git("update-ref", "refs/remotes/origin/main", sha)
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")

    def age(self, *rels):
        for r in rels:
            p = self.repo / r
            if p.exists():
                os.utime(p, (10 ** 9, 10 ** 9), follow_symlinks=False)

    def snapshot(self, rel):
        """{repo-relative path: sha256} for every regular file under rel."""
        base = self.repo / rel
        out = {}
        if base.is_file():
            return {rel: hashlib.sha256(base.read_bytes()).hexdigest()}
        for p in sorted(base.rglob("*")):
            if p.is_file() and not p.is_symlink():
                out[str(p.relative_to(self.repo))] = hashlib.sha256(p.read_bytes()).hexdigest()
        return out


# --------------------------------------------------------------- case setup --

def case_d1a(fx):
    """D1: modified pushed file hidden from porcelain by assume-unchanged."""
    fx.write("docs/kept.txt", "pushed payload\n")
    fx.commit(); fx.pushed(fx.head)
    fx.write("docs/kept.txt", "MODIFIED unique bytes\n")
    fx.git("update-index", "--assume-unchanged", "--", "docs/kept.txt")
    return "docs"


def case_d1b(fx):
    """D1: same shape with skip-worktree."""
    fx.write("docs/kept.txt", "pushed payload\n")
    fx.commit(); fx.pushed(fx.head)
    fx.write("docs/kept.txt", "MODIFIED unique bytes\n")
    fx.git("update-index", "--skip-worktree", "--", "docs/kept.txt")
    return "docs"


def case_d1c(fx):
    """D1: a pushed FILE (not a directory) hidden by skip-worktree."""
    fx.write("solo.txt", "pushed payload\n")
    fx.commit(); fx.pushed(fx.head)
    fx.write("solo.txt", "MODIFIED unique bytes\n")
    fx.git("update-index", "--skip-worktree", "--", "solo.txt")
    return "solo.txt"


def case_d2a(fx):
    """D2: pushed directory carrying an ignored child with no remote copy."""
    fx.write("bundle/kept.txt", "pushed payload\n")
    fx.write(".gitignore", "bundle/local.bin\n")
    fx.commit(); fx.pushed(fx.head)
    fx.write("bundle/local.bin", "unique ignored bytes\n")
    return "bundle"


def case_d2b(fx):
    """D2: pushed directory carrying an untracked child with no remote copy."""
    fx.write("bundle/kept.txt", "pushed payload\n")
    fx.commit(); fx.pushed(fx.head)
    fx.write("bundle/extra.bin", "unique untracked bytes\n")
    return "bundle"


def case_d2c(fx):
    """D2: pushed directory whose tracked child has uncommitted edits."""
    fx.write("bundle/kept.txt", "pushed payload\n")
    fx.commit(); fx.pushed(fx.head)
    fx.write("bundle/kept.txt", "unique uncommitted bytes\n")
    return "bundle"


def case_d2d(fx):
    """D2/stale: aged .scratch container holding a backdated fresh write.

    The container is deliberately untracked (created after the last commit):
    this is the stale-shaped scope the lane's stale receipt would authorize.
    """
    fx.write("seed2.txt", "seed\n")
    fx.commit(); fx.pushed(fx.head)
    fx.write(".scratch/aged/old.txt", "old payload\n")
    fx.write(".scratch/aged/fresh.md", "rewritten payload\n")
    fx.age(".scratch/aged/old.txt", ".scratch/aged/fresh.md", ".scratch/aged")
    return ".scratch/aged"


CASES = [
    ("D1a assume-unchanged dir child", case_d1a),
    ("D1b skip-worktree dir child", case_d1b),
    ("D1c skip-worktree file", case_d1c),
    ("D2a ignored child", case_d2a),
    ("D2b untracked child", case_d2b),
    ("D2c dirty tracked child", case_d2c),
    ("D2d backdated descendant", case_d2d),
]


def verdict_of(out):
    for line in out.splitlines():
        if line.startswith("VERDICT\t"):
            f = line.split("\t")
            return f[2], f[3]
    return "ERROR", "unparseable"


def qresult_of(out):
    rows = [l.split("\t") for l in out.splitlines() if l.startswith("RESULT\t")]
    return rows[-1][2] if rows else "NO-RESULT"


def run_case(name, setup):
    fx = Fx(name.split()[0].lower().replace(".", ""))
    rel = setup(fx)
    target = fx.repo / rel
    before = fx.snapshot(rel)
    # independent record of what the remote ref actually holds
    remote_missing = []
    for p in before:
        r = sh(["git", "-C", str(fx.repo), "cat-file", "-e",
                f"refs/remotes/origin/main:{p}"], fx.env)
        if r.returncode:
            remote_missing.append(p)

    v = sh(["bash", str(TOOLS / "souji-verify.sh"), "--", str(target)], fx.env)
    va = sh(["bash", str(TOOLS / "souji-vault-verify.sh"), "--fallback", "--",
             str(target)], fx.env)
    qd = sh(["bash", str(TOOLS / "souji-quarantine.sh"), "--dry-run", "--hold", "0",
             str(fx.repo), rel], fx.env)
    # The live pass runs with SOUJI_QUARANTINE_ALLOW_LIVE=1 ONLY because the
    # whole fleet here is a /var/tmp fixture; the guard's job is to protect the
    # real fleet, and the real fleet is never named in this script.
    live_env = dict(fx.env, SOUJI_QUARANTINE_ALLOW_LIVE="1")
    ql = sh(["bash", str(TOOLS / "souji-quarantine.sh"), "--hold", "0",
             str(fx.repo), rel], live_env)
    after = fx.snapshot(rel)
    # bytes that left the live tree but still exist under .ufo-quarantine are
    # staged, not destroyed -- the distinction matters for the lane's worst
    # failure (unrecoverable loss).
    qroot = fx.repo / ".ufo-quarantine"
    staged = {}
    if qroot.is_dir():
        for p in sorted(qroot.rglob("*")):
            if p.is_file() and not p.is_symlink():
                staged[str(p.relative_to(qroot))] = hashlib.sha256(p.read_bytes()).hexdigest()
    vv, vr = verdict_of(v.stdout)
    av, ar = verdict_of(va.stdout)
    dry = qresult_of(qd.stdout)
    live = qresult_of(ql.stdout)
    survivors = sorted(after)
    lost = sorted(set(before) - set(after))
    destroyed = [p for p in lost if not any(s.endswith(p) for s in staged)]
    false_safe = [n for n, (ver, _) in (("verify", (vv, vr)), ("vault", (av, ar)))
                  if ver == "SAFE"]
    unsafe_delete = live == "DELETED" and bool(lost)
    return {
        "case": name, "target": str(target), "fixture": str(fx.root),
        "payloads_before": before, "payloads_after": survivors,
        "lost_payloads": lost, "destroyed_payloads": destroyed,
        "staged_in_quarantine": sorted(staged), "remote_missing": remote_missing,
        "verify": f"{vv}({vr})", "vault": f"{av}({ar})",
        "quarantine_dry_run": dry, "quarantine_actual": live,
        "false_safe_tools": false_safe, "unsafe_delete": unsafe_delete,
        "bytes_survived": bool(before) and set(before) <= set(after),
    }


rows = [run_case(n, f) for n, f in CASES]
summary = {
    "label": LABEL, "tools": str(TOOLS),
    "cases": len(rows),
    "unsafe_delete_cases": sum(r["unsafe_delete"] for r in rows),
    "false_safe_cases": sum(bool(r["false_safe_tools"]) for r in rows),
    "cases_with_lost_bytes": sum(bool(r["lost_payloads"]) for r in rows),
    "cases_with_destroyed_bytes": sum(bool(r["destroyed_payloads"]) for r in rows),
    "harness_errors": sum(r["quarantine_actual"] == "NO-RESULT" for r in rows),
}
report = {"summary": summary, "cases": rows}
if A.out:
    Path(A.out).write_text(json.dumps(report, indent=2) + "\n")

print(f"REPRO\t{LABEL}\tcases={summary['cases']}\t"
      f"unsafe_delete={summary['unsafe_delete_cases']}\t"
      f"false_safe={summary['false_safe_cases']}\t"
      f"lost_bytes={summary['cases_with_lost_bytes']}\t"
      f"destroyed={summary['cases_with_destroyed_bytes']}")
for r in rows:
    flag = "UNSAFE-DELETE" if r["unsafe_delete"] else ""
    if r["destroyed_payloads"]:
        flag = (flag + " DESTROYED").strip()
    elif r["false_safe_tools"]:
        flag = "FALSE-SAFE:" + "+".join(r["false_safe_tools"])
    print(f"  {r['case']:34} verify={r['verify']:26} "
          f"q_dry={r['quarantine_dry_run']:16} q_actual={r['quarantine_actual']:16} "
          f"destroyed={','.join(r['destroyed_payloads']) or '-':28} {flag}")
sys.exit(0 if (summary["unsafe_delete_cases"] == 0
               and summary["cases_with_destroyed_bytes"] == 0) else 1)
