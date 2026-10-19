#!/usr/bin/env python3
"""S13 (round 10) cluster-G repro: G1 index-write contract, G2 fresh-descendant.

Fresh fixtures only, under TMPDIR (forced to /var/tmp). Read-only against the
installed tools: every destructive call runs inside a mktemp fixture repo.

Usage: python3 S13-cluster-G-repro.py [--tools DIR] [--only a,b] [--out FILE]
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

P = argparse.ArgumentParser()
P.add_argument("--tools", default="/home/vgpnk/Projects/shokunin/souji-shokunin/tools")
P.add_argument("--only", default="")
P.add_argument("--out", default="")
A = P.parse_args()
TOOLS = Path(A.tools).resolve()
OLD = int(time.time()) - 6 * 86400


def sh(cmd, env, cwd=None, data=None):
    return subprocess.run([str(x) for x in cmd], input=data, text=True,
                          capture_output=True, env=env, cwd=cwd, timeout=60)


class Fx:
    def __init__(self, name):
        self.root = Path(tempfile.mkdtemp(prefix="s13-g-" + name + ".", dir="/var/tmp"))
        self.fleet = self.root / "fleet"
        self.repo = self.fleet / (name + "-shokunin")
        self.repo.mkdir(parents=True)
        self.home = self.root / "home"
        self.home.mkdir()
        self.ledger = self.root / "ledger.tsv"
        self.ledger.write_text("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        e = os.environ.copy()
        for k in list(e):
            if k.startswith("GIT_") or k.startswith("SOUJI_") or k in ("SHOKUNIN_ROOT",):
                e.pop(k)
        e.update({
            "PATH": os.environ["PATH"], "HOME": str(self.home), "TMPDIR": "/var/tmp",
            "LC_ALL": "C", "LANG": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "S13 fixture", "GIT_AUTHOR_EMAIL": "s13@example.invalid",
            "GIT_COMMITTER_NAME": "S13 fixture", "GIT_COMMITTER_EMAIL": "s13@example.invalid",
            "SHOKUNIN_ROOT": str(self.fleet), "SOUJI_LEDGER": str(self.ledger),
            "SOUJI_Q_SHOKUNIN_ROOT": str(self.fleet), "SOUJI_Q_LEDGER": str(self.ledger),
            "SOUJI_VERIFY_BIN": str(TOOLS / "souji-verify.sh"),
        })
        self.env = e
        self.git("init", "-q", "--initial-branch=main", str(self.repo))
        self.write("base.txt", "base\n")
        self.head = self.commit()
        self.pushed(self.head)

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

    def commit(self, remote=False):
        self.git("add", "-A")
        tree = self.git("write-tree")
        args = ["commit-tree", tree]
        if getattr(self, "head", None):
            args += ["-p", self.head]
        sha = self.git(*args, data="S13 fixture\n")
        self.git("update-ref", "refs/heads/main", sha)
        self.head = sha
        if remote:
            self.pushed(sha)
        return sha

    def pushed(self, sha):
        self.git("update-ref", "refs/remotes/origin/main", sha)
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")

    def age(self, *paths):
        for p in paths:
            os.utime(p, (OLD, OLD), follow_symlinks=False)

    def index_sha(self):
        p = self.repo / ".git/index"
        return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "ABSENT"

    def snapshot(self, path):
        path = Path(path)
        if not path.exists():
            return {"exists": False}
        out = {}
        items = [path] if path.is_file() else sorted(path.rglob("*"))
        for p in items:
            st = p.lstat()
            rel = str(p.relative_to(path)) if path.is_dir() else "."
            out[rel] = {"dir": p.is_dir(), "link": p.is_symlink(),
                        "mtime_ns": st.st_mtime_ns,
                        "sha256": (hashlib.sha256(p.read_bytes()).hexdigest()
                                   if p.is_file() and not p.is_symlink() else None)}
        return {"exists": True, "entries": out}

    def verify(self, target, tool="souji-verify.sh"):
        r = sh(["bash", TOOLS / tool, "--json", "--", str(target)], self.env)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"verdict": "UNPARSEABLE", "raw": r.stdout, "rc": r.returncode, "stderr": r.stderr}
        return d

    def quarantine(self, target, dry=False, hold=0, tool="souji-quarantine.sh"):
        args = ["bash", TOOLS / tool, "--hold", str(hold)]
        if dry:
            args += ["--dry-run"]
        r = sh(args + [str(self.repo), str(target)], self.env)
        rows = [l.split("\t") for l in r.stdout.splitlines() if l.startswith("RESULT\t")]
        return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr,
                "result": rows[-1][2] if rows else "NO-RESULT",
                "receipt": rows[-1][3] if rows and len(rows[-1]) > 3 else ""}


# ------------------------------------------------------------------ G1 ------
def g1_index_contract(tag, shift_file_mtime=True, delete_index=False, target="root"):
    f = Fx("g1-" + tag)
    art = f.write("artifact.txt", "same bytes\n")
    f.commit(remote=True)
    if shift_file_mtime:
        os.utime(art, (int(time.time()) - 7, int(time.time()) - 7))
    if delete_index:
        (f.repo / ".git/index").unlink()
    tgt = f.repo if target == "root" else art
    env = dict(f.env)
    env.pop("GIT_OPTIONAL_LOCKS", None)
    rec = {"case": "G1-" + tag, "target": str(tgt), "delete_index": delete_index}
    for name, fn in (
        ("verify", lambda: f.verify(tgt)),
        ("vault_verify", lambda: f.verify(tgt, "souji-vault-verify.sh")),
        ("quarantine_dry", lambda: f.quarantine(tgt, dry=True)),
        ("census", lambda: sh(["bash", TOOLS / "souji-census.sh", "--root", str(f.fleet)],
                              env).returncode),
    ):
        before = f.index_sha()
        before_snap = f.snapshot(tgt)
        try:
            res = fn()
        except Exception as e:  # noqa: BLE001
            res = {"error": repr(e)}
        after = f.index_sha()
        after_snap = f.snapshot(tgt)
        rec[name] = {
            "index_before": before, "index_after": after,
            "index_unchanged": before == after,
            "target_unchanged": before_snap == after_snap,
            "verdict": res.get("verdict") if isinstance(res, dict) else res,
            "receipt": res.get("receipt") if isinstance(res, dict) else None,
            "result": res.get("result") if isinstance(res, dict) else None,
            "rc": res.get("rc") if isinstance(res, dict) else res,
        }
    rec["index_write_violation"] = [
        k for k in ("verify", "vault_verify", "quarantine_dry", "census")
        if isinstance(rec[k], dict) and rec[k].get("index_unchanged") is False
    ]
    return rec, f


def g1_missing_index_created(tag):
    """A repo whose index is absent: does a read-only probe create it?"""
    f = Fx("g1-" + tag)
    art = f.write("artifact.txt", "same bytes\n")
    f.commit(remote=True)
    (f.repo / ".git/index").unlink()
    rec, _ = g1_index_contract(tag, shift_file_mtime=False, delete_index=True)
    rec["index_absent_before"] = True
    rec["index_created"] = rec["verify"]["index_after"] != "ABSENT"
    return rec, f


# ------------------------------------------------------------------ G2 ------
def g2_fresh_descendant(tag, mode):
    """Aged .scratch container; fresh unique descendant; is it protected?"""
    f = Fx("g2-" + tag)
    d = f.write(".scratch/aged-bundle/fresh-child.md", "S13 fresh unique child payload\n").parent
    f.age(d)
    if mode == "plain":
        pass
    elif mode == "ignored":
        f.write(".gitignore", ".scratch/aged-bundle/fresh-child.md\n")
        f.commit(remote=True)
    elif mode == "live-ref-child":
        f.write("active-refs.md", "next run loads fresh-child.md\n")
        f.age(d / "fresh-child.md")
    elif mode == "live-ref-child-hidden":
        f.write(".hidden-refs.md", "next run loads fresh-child.md\n")
        f.age(d / "fresh-child.md")
    elif mode == "fresh-dir-child":
        f.write(".scratch/aged-bundle/newdir/note.md", "fresh nested child\n")
        f.age(d)
    elif mode == "content-fresh-mtime-old":
        # child bytes changed but mtime restored old -> mtime pin blind
        f.age(d / "fresh-child.md")
    rec = {"case": "G2-" + tag, "mode": mode, "target": str(d)}
    rec["verify"] = f.verify(d)
    rec["vault_verify"] = f.verify(d, "souji-vault-verify.sh")
    rec["quarantine_dry"] = f.quarantine(d, dry=True)
    before = f.snapshot(d)
    rec["quarantine_live"] = f.quarantine(d, hold=0)
    after = f.snapshot(d)
    rec["target_survives"] = after.get("exists", False)
    rec["target_bytes_unchanged"] = before == after
    rec["staged"] = [str(p) for p in (f.repo / ".ufo-quarantine").rglob("*")] \
        if (f.repo / ".ufo-quarantine").exists() else []
    rec["false_safe"] = rec["verify"].get("verdict") == "SAFE"
    rec["unsafe_delete"] = rec["quarantine_live"]["result"] == "DELETED"
    return rec, f


def main():
    sel = set(x for x in A.only.split(",") if x)
    out = {"tools": str(TOOLS),
           "tools_sha256": {n: hashlib.sha256((TOOLS / n).read_bytes()).hexdigest()
                            for n in ("souji-verify.sh", "souji-vault-verify.sh",
                                      "souji-quarantine.sh", "souji-census.sh")},
           "fixture_root": "/var/tmp", "cases": []}
    keep = []
    cases = [
        ("index-stale-stat", lambda: g1_index_contract("stale-stat")),
        ("index-stale-stat-file", lambda: g1_index_contract("stale-stat-file", target="file")),
        ("index-absent", lambda: g1_missing_index_created("absent")),
        ("fresh-child", lambda: g2_fresh_descendant("fresh-child", "plain")),
        ("fresh-child-ignored", lambda: g2_fresh_descendant("fresh-ignored", "ignored")),
        ("live-ref-child", lambda: g2_fresh_descendant("live-ref", "live-ref-child")),
        ("live-ref-child-hidden", lambda: g2_fresh_descendant("live-ref-hidden", "live-ref-child-hidden")),
        ("fresh-dir-child", lambda: g2_fresh_descendant("fresh-dir", "fresh-dir-child")),
        ("content-fresh-mtime-old", lambda: g2_fresh_descendant("content-fresh", "content-fresh-mtime-old")),
    ]
    for name, fn in cases:
        if sel and name not in sel:
            continue
        try:
            rec, f = fn()
        except Exception as e:  # noqa: BLE001
            rec, f = {"case": name, "harness_error": repr(e)}, None
        rec["name"] = name
        out["cases"].append(rec)
        if f is not None:
            keep.append(f)
        print(json.dumps({k: v for k, v in rec.items()
                          if k not in ("quarantine_live", "quarantine_dry")}, indent=2)[:1800])
        print("-" * 60)
    if A.out:
        Path(A.out).write_text(json.dumps(out, indent=2) + "\n")
        print("wrote", A.out)
    # fixtures retained for inspection; print roots
    print("fixture roots:", [str(f.root) for f in keep])
    return 0


if __name__ == "__main__":
    sys.exit(main())
