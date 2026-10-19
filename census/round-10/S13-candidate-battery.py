#!/usr/bin/env python3
"""S13 (round 10) cluster-G candidate battery.

Fresh /var/tmp fixtures only. Every case is built from scratch, run against the
installed S17-patched tools and against the cand-g1-* candidates, and recorded
with its safety outcome.

G1  index-write contract: sha256 + mtime_ns + inode + index.lock, on five
    hostile constructions, for all four tools.
G2  fresh-descendant closure: six descendant constructions end to end through
    quarantine (stage -> hold -> second check -> delete), plus a real
    in-hold-window write via the documented test hook.

Usage: python3 S13-candidate-battery.py [--installed DIR] [--cand DIR] [--out F]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

P = argparse.ArgumentParser()
P.add_argument("--installed", default="/home/vgpnk/Projects/shokunin/souji-shokunin/tools")
P.add_argument("--cand", default="/home/vgpnk/Projects/shokunin/souji-shokunin/tools")
P.add_argument("--out", default="/var/tmp/s13-r10/battery.json")
P.add_argument("--only", default="")
A = P.parse_args()
INST = Path(A.installed).resolve()
CAND = Path(A.cand).resolve()
OLD = int(time.time()) - 6 * 86400
RECORDS = []


def sh(cmd, env, data=None, timeout=120):
    return subprocess.run([str(x) for x in cmd], input=data, text=True,
                          capture_output=True, env=env, timeout=timeout)


class Fx:
    """A fresh fixture fleet with one pushed repo."""

    def __init__(self, name, tools, cand):
        self.root = Path(tempfile.mkdtemp(prefix="s13b-" + name + ".", dir="/var/tmp"))
        self.fleet = self.root / "fleet"
        self.repo = self.fleet / (name + "-shokunin")
        self.repo.mkdir(parents=True)
        self.home = self.root / "home"
        self.home.mkdir()
        self.ledger = self.root / "ledger.tsv"
        self.ledger.write_text("source_path\tsource_sha256\tvault_path\tvault_sha256\t"
                               "exported_at\tnote\n")
        e = os.environ.copy()
        for k in list(e):
            if k.startswith("GIT_") or k.startswith("SOUJI_") or k == "SHOKUNIN_ROOT":
                e.pop(k)
        self.verify_bin = (tools / ("cand-g1-verify.sh" if cand else "souji-verify.sh"))
        e.update({
            "PATH": os.environ["PATH"], "HOME": str(self.home), "TMPDIR": "/var/tmp",
            "LC_ALL": "C", "LANG": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "S13 fixture", "GIT_AUTHOR_EMAIL": "s13@example.invalid",
            "GIT_COMMITTER_NAME": "S13 fixture", "GIT_COMMITTER_EMAIL": "s13@example.invalid",
            "SHOKUNIN_ROOT": str(self.fleet), "SOUJI_LEDGER": str(self.ledger),
            "SOUJI_Q_SHOKUNIN_ROOT": str(self.fleet), "SOUJI_Q_LEDGER": str(self.ledger),
            "SOUJI_VERIFY_BIN": str(self.verify_bin),
        })
        self.env = e
        self.git("init", "-q", "--initial-branch=main", str(self.repo))
        self.write("base.txt", "base\n")
        self.head = self.commit(pushed=True)

    def git(self, *args, data=None):
        r = sh(["git", "-C", str(self.repo), *args], self.env, data=data)
        if r.returncode:
            raise RuntimeError(f"git {args}: {r.returncode} {r.stderr}")
        return r.stdout.strip()

    def write(self, rel, data):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data)
        return p

    def commit(self, pushed=False):
        self.git("add", "-A")
        tree = self.git("write-tree")
        args = ["commit-tree", tree]
        if getattr(self, "head", None):
            args += ["-p", self.head]
        sha = self.git(*args, data="S13 fixture\n")
        self.git("update-ref", "refs/heads/main", sha)
        self.head = sha
        if pushed:
            self.git("update-ref", "refs/remotes/origin/main", sha)
            self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        return sha

    def age(self, *paths):
        for p in paths:
            os.utime(p, (OLD, OLD), follow_symlinks=False)

    def idx(self):
        p = self.repo / ".git/index"
        if not p.exists():
            return {"absent": True}
        st = p.stat()
        return {"absent": False, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "mtime_ns": st.st_mtime_ns, "ino": st.st_ino, "size": st.st_size}

    def snapshot(self, path):
        path = Path(path)
        if not path.exists():
            return {"exists": False}
        out = {}
        for p in ([path] if path.is_file() else sorted(path.rglob("*"))):
            st = p.lstat()
            out[str(p.relative_to(path))] = {
                "mtime_ns": st.st_mtime_ns,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest()
                if p.is_file() and not p.is_symlink() else None}
        return {"exists": True, "entries": out}

    def verify(self, target, tools, vault=False, cand=None):
        if cand is None:
            cand = tools == CAND
        if cand:
            binary = tools / ("cand-g1-vault.sh" if vault else "cand-g1-verify.sh")
        else:
            binary = tools / ("souji-vault-verify.sh" if vault else "souji-verify.sh")
        r = sh(["bash", binary, "--json", "--", str(target)], self.env)
        try:
            return json.loads(r.stdout)
        except Exception:
            return {"verdict": "UNPARSEABLE", "raw": r.stdout[:200]}

    def quarantine(self, target, tools, dry=False, hold=0, extra=None, cand=None):
        if cand is None:
            cand = tools == CAND
        binary = tools / ("cand-g1-quarantine.sh" if cand else "souji-quarantine.sh")
        # Copied tools recompute their live-fleet root as the fixture parent
        # (/var/tmp), so the documented affordance is required. It is applied
        # identically to both sides and only after containment is asserted.
        root = str(self.root)
        assert root.startswith("/var/tmp/"), f"fixture escaped /var/tmp: {root}"
        args = ["bash", binary, "--hold", str(hold)]
        if dry:
            args += ["--dry-run"]
        e = dict(self.env)
        e["SOUJI_QUARANTINE_ALLOW_LIVE"] = "1"
        if extra:
            e.update(extra)
        r = sh(args + [str(self.repo), str(target)], e)
        rows = [l.split("\t") for l in r.stdout.splitlines() if l.startswith("RESULT\t")]
        return {"rc": r.returncode, "result": rows[-1][2] if rows else "NO-RESULT",
                "ev": rows[-1][3] if rows and len(rows[-1]) > 3 else "",
                "out": r.stdout[-600:]}


def rec(**kw):
    RECORDS.append(kw)


# ------------------------------------------------------------------ G1 ------
def g1_case(tool, label, mutate=None, target_mode="root", locks="1"):
    fx = Fx("g1-" + label, INST, False)
    fx.write("artifact.txt", "same bytes\n")
    fx.commit(pushed=True)
    os.utime(fx.repo / "artifact.txt", (int(time.time()) - 7, int(time.time()) - 7))
    if mutate:
        mutate(fx)
    tgt = str(fx.repo) if target_mode == "root" else str(fx.repo / "artifact.txt")

    out = {}
    for name, tools, cand in (("installed", INST, False), ("candidate", CAND, True)):
        f2 = Fx("g1-" + label + "-" + name, tools, cand)
        f2.write("artifact.txt", "same bytes\n")
        f2.commit(pushed=True)
        os.utime(f2.repo / "artifact.txt", (int(time.time()) - 7, int(time.time()) - 7))
        if mutate:
            mutate(f2)
        tgt2 = str(f2.repo) if target_mode == "root" else str(f2.repo / "artifact.txt")
        binary = tools / ("cand-g1-" + tool + ".sh" if cand else "souji-" + tool + ".sh")
        if not binary.exists():
            binary = tools / ("cand-g1-" + tool + ".sh")
        before = f2.idx()
        preexisting_lock = (f2.repo / ".git/index.lock").exists()
        e = dict(f2.env)
        e["GIT_OPTIONAL_LOCKS"] = locks
        if tool == "census":
            r = sh(["bash", binary, "--root", str(f2.fleet)], e)
        elif tool == "quarantine":
            r = sh(["bash", binary, "--dry-run", "--hold", "0", str(f2.repo), tgt2], e)
        else:
            r = sh(["bash", binary, "--json", "--", tgt2], e)
        after = f2.idx()
        lock = (f2.repo / ".git/index.lock").exists()
        # A pre-existing foreign lock must be preserved, not stolen: only a
        # lock that the tool itself created counts as a violation.
        lock_is_violation = lock and not preexisting_lock
        out[name] = {"index_unchanged": before == after, "lock_left": lock,
                     "lock_is_violation": lock_is_violation,
                     "rc": r.returncode, "before": before, "after": after}
    rec(case=f"G1-{tool}-{label}", **out)


def g1_suite():
    g1_case("verify", "stale-stat")
    g1_case("verify", "file-target", target_mode="file")
    g1_case("verify", "locks-unset", locks="")
    g1_case("verify", "index-absent",
            mutate=lambda f: (f.repo / ".git/index").unlink())
    g1_case("verify", "index-readonly",
            mutate=lambda f: (f.repo / ".git/index").chmod(0o444))
    g1_case("verify", "foreign-lock",
            mutate=lambda f: (f.repo / ".git/index.lock").write_text("foreign\n"))
    g1_case("vault", "stale-stat")
    g1_case("vault", "index-absent",
            mutate=lambda f: (f.repo / ".git/index").unlink())
    g1_case("census", "stale-stat")
    g1_case("census", "index-absent",
            mutate=lambda f: (f.repo / ".git/index").unlink())
    g1_case("quarantine", "stale-stat")
    g1_case("quarantine", "file-target", target_mode="file")


# ------------------------------------------------------------------ G2 ------
def g2_case(mode):
    """Build the descendant construction; run both toolchains end to end."""
    out = {}
    for name, tools, cand in (("installed", INST, False), ("candidate", CAND, True)):
        fx = Fx("g2-" + mode + "-" + name, tools, cand)
        d = fx.write(".scratch/aged-bundle/fresh-child.md",
                     "S13 live descendant payload\n").parent
        fx.age(d)
        if mode == "plain":
            pass
        elif mode == "ignored":
            fx.write(".gitignore", ".scratch/aged-bundle/fresh-child.md\n")
            fx.commit(pushed=True)
        elif mode == "live-ref-child":
            fx.write("active-refs.md", "next run loads fresh-child.md\n")
            fx.age(d / "fresh-child.md")
        elif mode == "live-ref-child-hidden":
            fx.write(".hidden-refs.md", "next run loads fresh-child.md\n")
            fx.age(d / "fresh-child.md")
        elif mode == "fresh-dir-child":
            fx.write(".scratch/aged-bundle/newdir/note.md", "fresh nested child\n")
            fx.age(d)
        elif mode == "content-fresh-mtime-old":
            fx.age(d / "fresh-child.md")

        v = fx.verify(d, tools)
        vv = fx.verify(d, tools, vault=True)
        qd = fx.quarantine(d, tools, dry=True)
        before = fx.snapshot(d)
        ql = fx.quarantine(d, tools, hold=0)
        after = fx.snapshot(d)
        staged = [str(p) for p in (fx.repo / ".ufo-quarantine").rglob("*")] \
            if (fx.repo / ".ufo-quarantine").exists() else []
        out[name] = {
            "verify": v.get("verdict"), "verify_ev": str(v.get("evidence"))[:120],
            "vault": vv.get("verdict"),
            "qdry": qd["result"], "qlive": ql["result"], "qlive_ev": ql["ev"][:120],
            "survives": after.get("exists", False),
            "bytes_unchanged": before == after,
            "staged": staged,
            "false_safe": v.get("verdict") == "SAFE" or vv.get("verdict") == "SAFE",
            "unsafe_delete": ql["result"] == "DELETED" and not after.get("exists", False),
        }
    rec(case=f"G2-{mode}", **out)


def g2_hold_race():
    """A real write into a staged descendant during the hold window."""
    out = {}
    for name, tools, cand in (("installed", INST, False), ("candidate", CAND, True)):
        fx = Fx("g2-race-" + name, tools, cand)
        d = fx.write(".scratch/aged-bundle/child.md", "S13 hold-race payload\n").parent
        fx.age(d)
        fx.age(d / "child.md")
        hook = fx.root / "hook.sh"
        hook.write_text('#!/usr/bin/env bash\n'
                        'printf "written during hold\\n" >> "$1/child.md"\n')
        q = fx.quarantine(d, tools, hold=0,
                          extra={"SOUJI_Q_TEST_HOOK": str(hook),
                                 "SOUJI_Q_SELFTEST_ACTIVE": "1"})
        out[name] = {"result": q["result"], "ev": q["ev"][:160],
                     "survives": d.exists(),
                     "unsafe_delete": q["result"] == "DELETED" and not d.exists()}
    rec(case="G2-hold-window-write", **out)


def main():
    only = set(x for x in A.only.split(",") if x)
    if not only or "g1" in only:
        g1_suite()
    if not only or "g2" in only:
        for mode in ("plain", "ignored", "live-ref-child", "live-ref-child-hidden",
                     "fresh-dir-child", "content-fresh-mtime-old"):
            g2_case(mode)
        g2_hold_race()

    summary = {}
    for side in ("installed", "candidate"):
        cases = [r for r in RECORDS if side in r]
        summary[side] = {
            "cases": len(cases),
            "index_violations": sum(1 for r in cases
                                    if r[side].get("index_unchanged") is False
                                    or r[side].get("lock_is_violation")),
            "false_safe": sum(1 for r in cases if r[side].get("false_safe")),
            "unsafe_deletes": sum(1 for r in cases if r[side].get("unsafe_delete")),
            "refused": sum(1 for r in cases
                           if r[side].get("verify") == "NOT-SAFE"
                           or r[side].get("result") in ("DRY-RUN-BLOCKED", "NOT-AUTHORIZED",
                                                        "ABORTED", "STAGE2-FAILED")),
        }
    payload = {"installed": str(INST), "candidate": str(CAND),
               "fixture_root": "/var/tmp", "summary": summary, "cases": RECORDS}
    Path(A.out).write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print("wrote", A.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
