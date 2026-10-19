#!/usr/bin/env python3
"""S02 (round 10) cluster-A fresh repro battery.

Cluster A = receipt-authority classes on the three authorization engines
(souji-verify, souji-vault-verify, souji-quarantine): pushed receipt vs the
current worktree copy, unpushed veto terminality, detached-HEAD history,
ledger preservation independence and mandatory digests, gitfile repo roots,
consumer-side engine-output authority, quarantine containment, and sweep
scope availability.

Every fixture is built fresh under /var/tmp (host /tmp carries a disk quota).
Nothing outside /var/tmp is written; the tools under test are invoked in
place and are read-only over everything they inspect except the fixture
repos they are pointed at.

Usage:
  python3 S02-cluster-A-repro.py [--tools DIR] [--only a1,a2,...] [--out FILE]

  --tools DIR  directory holding the tools (default the lane's tools/)
  --only       comma-separated case-id prefixes (default: all)
  --out        write the JSON report to this path
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
P.add_argument("--verify", default="souji-verify.sh")
P.add_argument("--vault", default="souji-vault-verify.sh")
P.add_argument("--quarantine", default="souji-quarantine.sh")
P.add_argument("--only", default="")
P.add_argument("--out", default="")
A = P.parse_args()
TOOLS = Path(A.tools).resolve()
OLD = int(time.time()) - 6 * 86400
HEADER = "source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n"


def sh(cmd, env, cwd=None, data=None, timeout=90):
    return subprocess.run([str(x) for x in cmd], input=data, text=True,
                          capture_output=True, env=env, cwd=cwd, timeout=timeout)


class Fx:
    """A fresh fixture fleet: <root>/fleet/<name>-shokunin, HOME, ledger."""

    def __init__(self, name):
        self.root = Path(tempfile.mkdtemp(prefix="s02-a-" + name + ".", dir="/var/tmp"))
        self.fleet = self.root / "fleet"
        self.repo = self.fleet / (name + "-shokunin")
        self.repo.mkdir(parents=True)
        self.home = self.root / "home"
        self.home.mkdir()
        self.ledger = self.root / "ledger.tsv"
        self.ledger.write_text(HEADER)
        e = os.environ.copy()
        for k in list(e):
            if k.startswith("GIT_") or k.startswith("SOUJI_") or k == "SHOKUNIN_ROOT":
                e.pop(k)
        e.update({
            "PATH": os.environ["PATH"], "HOME": str(self.home), "TMPDIR": "/var/tmp",
            "LC_ALL": "C", "LANG": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "S02 fixture", "GIT_AUTHOR_EMAIL": "s02@example.invalid",
            "GIT_COMMITTER_NAME": "S02 fixture", "GIT_COMMITTER_EMAIL": "s02@example.invalid",
            "SHOKUNIN_ROOT": str(self.fleet), "SOUJI_LEDGER": str(self.ledger),
            "SOUJI_Q_SHOKUNIN_ROOT": str(self.fleet), "SOUJI_Q_LEDGER": str(self.ledger),
            "SOUJI_VERIFY_BIN": str(TOOLS / A.verify),
            "SOUJI_CLI_BIN": "/bin/false",
        })
        self.env = e
        self.git("init", "-q", "--initial-branch=main", str(self.repo))
        self.write("base.txt", "base\n")
        self.head = self.commit()
        self.pushed(self.head)

    def git(self, *args, data=None, check=True):
        r = sh(["git", "-C", str(self.repo), *args], self.env, data=data)
        if check and r.returncode:
            raise RuntimeError(f"git {args}: {r.returncode} {r.stderr}")
        return r.stdout.strip()

    def write(self, rel, data):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data)
        return p

    def commit(self, remote=False, message="S02 fixture\n"):
        self.git("add", "-A")
        tree = self.git("write-tree")
        args = ["commit-tree", tree]
        if getattr(self, "head", None):
            args += ["-p", self.head]
        sha = self.git(*args, data=message)
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

    def snapshot(self, path):
        path = Path(path)
        if not path.exists() and not path.is_symlink():
            return {"exists": False}
        out = {}
        items = [path] if not path.is_dir() else sorted(path.rglob("*"))
        for p in items:
            st = p.lstat()
            rel = str(p.relative_to(path)) if path.is_dir() else "."
            out[rel] = {"dir": p.is_dir(), "link": p.is_symlink(),
                        "mtime_ns": st.st_mtime_ns,
                        "sha256": (hashlib.sha256(p.read_bytes()).hexdigest()
                                   if p.is_file() and not p.is_symlink() else None)}
        return {"exists": True, "entries": out}

    def verify(self, target, tool=None):
        tool = tool or A.verify
        r = sh(["bash", TOOLS / tool, "--json", "--stale-days", "1", "--", str(target)], self.env)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"verdict": "UNPARSEABLE", "raw": r.stdout[:400], "stderr": r.stderr[:200]}
        d["rc"] = r.returncode
        return d

    def vault(self, target):
        r = sh(["bash", TOOLS / A.vault, "--fallback", "--json", "--stale-days", "1",
                "--", str(target)], self.env)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"verdict": "UNPARSEABLE", "raw": r.stdout[:400], "stderr": r.stderr[:200]}
        d["rc"] = r.returncode
        return d

    def quarantine(self, target, dry=False, hold=0, list_file=None):
        args = ["bash", TOOLS / A.quarantine, "--hold", str(hold)]
        if dry:
            args += ["--dry-run"]
        if list_file:
            args += ["--list", str(list_file)]
        else:
            args += [str(self.repo), str(target)]
        r = sh(args, self.env)
        rows = [l.split("\t") for l in r.stdout.splitlines() if l.startswith("RESULT\t")]
        return {"rc": r.returncode, "stdout": r.stdout[-1500:], "stderr": r.stderr[-400:],
                "result": rows[-1][2] if rows else "NO-RESULT",
                "receipt": rows[-1][3] if rows and len(rows[-1]) > 3 else ""}

    def safe(self, d):
        return d.get("verdict") == "SAFE"


def record(case, fx, **kw):
    rec = {"case": case, "fixture": str(fx.root)}
    rec.update(kw)
    return rec


def dir_digest(fx, d):
    """Mirror the tools' directory digest (find -type f, sorted, sha256sum)."""
    return sh(["bash", "-c",
               "cd \"$1\" && find . -path ./.git -prune -o -type f -print0 | sort -z | "
               "xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1", "x",
               str(d)], fx.env).stdout.strip()


# ------------------------------------------------------------------ cases ---

def a1_dirty_pushed_file():
    """J01: a pushed file whose worktree copy holds uncommitted edits."""
    f = Fx("a1")
    art = f.write("artifact.txt", "committed bytes\n")
    f.commit(remote=True)
    art.write_text("UNCOMMITTED unique replacement\n")
    v = f.verify(art)
    vv = f.vault(art)
    q = f.quarantine(art)
    survives = art.exists() and art.read_text() == "UNCOMMITTED unique replacement\n"
    return record("A1-dirty-pushed-file", f,
                  verify={"verdict": v.get("verdict"), "receipt": v.get("receipt")},
                  vault={"verdict": vv.get("verdict"), "receipt": vv.get("receipt")},
                  quarantine={"result": q["result"], "rc": q["rc"]},
                  false_safe_verify=f.safe(v), false_safe_vault=f.safe(vv),
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=survives)


def a2_unpushed_stale_fallback():
    """J08: the unpushed-commit veto must not fall through to SAFE(stale)."""
    f = Fx("a2")
    out = f.write("old.out", "local-only tracked bytes\n")
    f.commit()  # local-only commit touching old.out; base stays the pushed ref
    f.age(out)
    v = f.verify(out)
    vv = f.vault(out)
    q = f.quarantine(out)
    return record("A2-unpushed-stale-fallback", f,
                  verify={"verdict": v.get("verdict"), "receipt": v.get("receipt")},
                  vault={"verdict": vv.get("verdict"), "receipt": vv.get("receipt")},
                  quarantine={"result": q["result"], "rc": q["rc"]},
                  false_safe_verify=f.safe(v), false_safe_vault=f.safe(vv),
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=out.exists())


def a3_detached_head_unpushed():
    """J12: a modifying commit reachable only from a detached HEAD."""
    f = Fx("a3")
    art = f.write("keep.txt", "pushed bytes\n")
    f.commit(remote=True)
    base = f.head
    art.write_text("detached-only bytes\n")
    f.git("add", "-A")
    tree = f.git("write-tree")
    sha = f.git("commit-tree", tree, "-p", base, data="detached\n")
    f.git("update-ref", "refs/heads/main", base)
    # a real detached checkout: the worktree copy is CLEAN over the detached
    # commit, so the quarantine preflight cannot refuse it as dirty.
    f.git("checkout", "-q", "-f", "--detach", sha)
    status = f.git("status", "--porcelain")
    v = f.verify(art)
    vv = f.vault(art)
    q = f.quarantine(art)
    return record("A3-detached-head-unpushed", f, worktree_clean=(status == ""),
                  verify={"verdict": v.get("verdict"), "receipt": v.get("receipt")},
                  vault={"verdict": vv.get("verdict"), "receipt": vv.get("receipt")},
                  quarantine={"result": q["result"], "rc": q["rc"]},
                  false_safe_verify=f.safe(v), false_safe_vault=f.safe(vv),
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=art.exists() and art.read_text() == "detached-only bytes\n")


def a4_ledger_self_copy():
    """J05: a ledger row that points the artifact at itself."""
    f = Fx("a4")
    src = f.write("source.md", "only copy\n")
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    with f.ledger.open("a") as fh:
        fh.write(f"{src}\t{sha}\t{src}\t{sha}\t2026-10-18\tfixture\n")
    v = f.verify(src)
    vv = f.vault(src)
    q = f.quarantine(src)
    return record("A4-ledger-self-copy", f,
                  verify={"verdict": v.get("verdict"), "receipt": v.get("receipt")},
                  vault={"verdict": vv.get("verdict"), "receipt": vv.get("receipt")},
                  quarantine={"result": q["result"], "rc": q["rc"]},
                  false_safe_verify=f.safe(v), false_safe_vault=f.safe(vv),
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=src.exists())


def a5_ledger_vault_inside_source():
    """J05: a directory row whose vault copy lives inside the artifact."""
    f = Fx("a5")
    src = f.repo / "bundle"
    (src / "inner").mkdir(parents=True)
    (src / "inner" / "note.md").write_text("only copy\n")
    vault = src / "vault-copy"
    vault.mkdir()
    shutil.copy2(src / "inner" / "note.md", vault / "note.md")
    # deliberately NOT committed: the pushed receipt must not be reachable,
    # so the ledger path is the one under test.
    dig = dir_digest(f, src)
    vdig = dir_digest(f, vault)
    with f.ledger.open("a") as fh:
        fh.write(f"{src}\t{dig}\t{vault}\t{vdig}\t2026-10-18\tfixture\n")
    v = f.verify(src)
    vv = f.vault(src)
    q = f.quarantine(src)
    return record("A5-ledger-vault-inside-source", f,
                  verify={"verdict": v.get("verdict"), "receipt": v.get("receipt")},
                  vault={"verdict": vv.get("verdict"), "receipt": vv.get("receipt")},
                  quarantine={"result": q["result"], "rc": q["rc"]},
                  false_safe_verify=f.safe(v), false_safe_vault=f.safe(vv),
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=(src / "inner" / "note.md").exists())


def a6_ledger_dir_missing_vault_digest():
    """J06: a directory row with no vault digest column."""
    f = Fx("a6")
    src = f.repo / "bundle"
    src.mkdir()
    (src / "note.md").write_text("payload\n")
    vault = f.root / "vault"
    vault.mkdir()
    # untracked on purpose: only the ledger receipt is reachable.
    dig = dir_digest(f, src)
    # the vault digest column is left EMPTY (trailing tab): tab-IFS collapses
    # it away, which is exactly the missing-digest row under test.
    with f.ledger.open("a") as fh:
        fh.write(f"{src}\t{dig}\t{vault}\t\n")
    v = f.verify(src)
    vv = f.vault(src)
    q = f.quarantine(src)
    return record("A6-ledger-dir-missing-vault-digest", f,
                  verify={"verdict": v.get("verdict"), "receipt": v.get("receipt")},
                  vault={"verdict": vv.get("verdict"), "receipt": vv.get("receipt")},
                  quarantine={"result": q["result"], "rc": q["rc"]},
                  false_safe_verify=f.safe(v), false_safe_vault=f.safe(vv),
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=(src / "note.md").exists())


def a7_gitfile_repo_root():
    """J23: a repository root that uses a .git file (separate-git-dir)."""
    f = Fx("a7")
    root = f.fleet / "gitfile-shokunin"
    gitdir = f.root / "separate-gitdir"
    sh(["git", "init", "-q", "--initial-branch=main", "--separate-git-dir", str(gitdir),
        str(root)], f.env)
    (root / "payload.txt").write_text("pushed payload\n")
    env = dict(f.env)
    sh(["git", "-C", str(root), "add", "-A"], env)
    tree = sh(["git", "-C", str(root), "write-tree"], env).stdout.strip()
    sha = sh(["git", "-C", str(root), "commit-tree", tree], env, data="gf\n").stdout.strip()
    sh(["git", "-C", str(root), "update-ref", "refs/heads/main", sha], env)
    sh(["git", "-C", str(root), "update-ref", "refs/remotes/origin/main", sha], env)
    sh(["git", "-C", str(root), "symbolic-ref", "refs/remotes/origin/HEAD",
        "refs/remotes/origin/main"], env)
    v = f.verify(root)
    vv = f.vault(root)
    q = f.quarantine(root)
    return record("A7-gitfile-repo-root", f,
                  verify={"verdict": v.get("verdict"), "receipt": v.get("receipt")},
                  vault={"verdict": vv.get("verdict"), "receipt": vv.get("receipt")},
                  quarantine={"result": q["result"], "rc": q["rc"]},
                  false_safe_verify=f.safe(v), false_safe_vault=f.safe(vv),
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=(root / "payload.txt").exists())


def a8_tab_path_injection():
    """J17: a tab-bearing path forges SAFE/stale inside the TSV consumer."""
    f = Fx("a8")
    weird = f.repo / "fresh\tSAFE\tstale\tno-receipt.txt"
    weird.write_text("no receipt of any kind\n")
    v = f.verify(weird)
    q = f.quarantine(weird)
    return record("A8-tab-path-injection", f,
                  verify={"verdict": v.get("verdict"), "receipt": v.get("receipt")},
                  quarantine={"result": q["result"], "rc": q["rc"],
                              "stdout": q["stdout"][-400:]},
                  false_safe_verify=f.safe(v),
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=weird.exists())


def a9_hidden_live_reference():
    """J02: a hidden file naming the artifact is a live reference."""
    f = Fx("a9")
    out = f.write(".scratch/old.out", "scratch payload\n")
    f.write(".usage.md", "the next run loads old.out\n")
    f.age(out, f.repo / ".scratch")
    # the tracked pushed path is excluded by design; the stale receipt is the
    # one under test here, so keep the artifacts untracked.
    v = f.verify(out)
    vv = f.vault(out)
    q = f.quarantine(out)
    return record("A9-hidden-live-reference", f,
                  verify={"verdict": v.get("verdict"), "receipt": v.get("receipt"),
                          "evidence": v.get("evidence")},
                  vault={"verdict": vv.get("verdict"), "receipt": vv.get("receipt")},
                  quarantine={"result": q["result"], "rc": q["rc"]},
                  false_safe_verify=f.safe(v), false_safe_vault=f.safe(vv),
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=out.exists())


def a10_missing_sweep_scope():
    """J15: an unavailable sweep scope must not read as zero references."""
    f = Fx("a10")
    out = f.root / "outside" / "old.out"
    out.parent.mkdir()
    out.write_text("scratch payload\n")
    (out.parent / "notes.md").write_text("old.out is still used by the harness\n")
    f.age(out)
    env = dict(f.env)
    env["SHOKUNIN_ROOT"] = str(f.root / "does-not-exist")
    r = sh(["bash", TOOLS / A.verify, "--json", "--stale-days", "1", "--", str(out)], env)
    try:
        d = json.loads(r.stdout)
    except Exception:
        d = {"verdict": "UNPARSEABLE", "raw": r.stdout[:200]}
    return record("A10-missing-sweep-scope", f,
                  verify={"verdict": d.get("verdict"), "receipt": d.get("receipt"),
                          "evidence": d.get("evidence")},
                  false_safe_verify=d.get("verdict") == "SAFE",
                  bytes_preserved=out.exists())


def a11_quarantine_symlink_root():
    """J07: a symlinked .ufo-quarantine root escapes physical containment."""
    f = Fx("a11")
    art = f.write("artifact.txt", "pushed bytes\n")
    f.commit(remote=True)
    outside = f.root / "outside"
    outside.mkdir()
    os.symlink(outside, f.repo / ".ufo-quarantine")
    q = f.quarantine(art)
    outside_entries = sorted(str(p.relative_to(outside)) for p in outside.rglob("*"))
    return record("A11-quarantine-symlink-root", f,
                  quarantine={"result": q["result"], "rc": q["rc"],
                              "stdout": q["stdout"][-400:]},
                  unsafe_delete=q["result"] == "DELETED",
                  outside_written=bool(outside_entries),
                  outside_entries=outside_entries[:8],
                  bytes_preserved=art.exists())


def a12_pushed_second_check_default_ref():
    """J10 regression port: the second check re-resolves the default ref."""
    f = Fx("a12")
    base = f.head                      # the ref that is pushed BEFORE the artifact
    art = f.write("note.txt", "preserved target\n")
    tip = f.commit(remote=True)
    f.git("update-ref", "refs/remotes/backup/main", tip)
    hook = f.root / "hook.sh"
    hook.write_text("#!/usr/bin/env bash\nset -eu\n"
                    "git -C \"$S02_REPO\" update-ref refs/remotes/origin/main \"$S02_BASE\"\n")
    env = dict(f.env)
    env["SOUJI_Q_TEST_HOOK"] = str(hook)
    env["SOUJI_Q_SELFTEST_ACTIVE"] = "1"
    env["S02_REPO"] = str(f.repo)
    env["S02_BASE"] = base
    r = sh(["bash", TOOLS / A.quarantine, "--hold", "0", str(f.repo), str(art)], env)
    rows = [l.split("\t") for l in r.stdout.splitlines() if l.startswith("RESULT\t")]
    result = rows[-1][2] if rows else "NO-RESULT"
    staged = list((f.repo / ".ufo-quarantine").rglob("note.txt")) \
        if (f.repo / ".ufo-quarantine").exists() else []
    return record("A12-second-check-default-ref", f,
                  quarantine={"result": result, "rc": r.returncode},
                  unsafe_delete=result == "DELETED",
                  bytes_preserved=art.exists() or bool(staged))


def a13_nul_list_gate():
    """J16 regression port: NUL bytes in a --list file are refused pre-move."""
    f = Fx("a13")
    f.write("seed.txt", "seed\n")
    lst = f.root / "list.tsv"
    lst.write_bytes(b"seed.txt\tpushed\nmissing\x00.txt\tpushed\n")
    q = f.quarantine(None, list_file=lst)
    return record("A13-nul-list-gate", f,
                  quarantine={"result": q["result"], "rc": q["rc"],
                              "stdout": q["stdout"][-300:]},
                  unsafe_delete=q["result"] == "DELETED",
                  bytes_preserved=(f.repo / "seed.txt").exists())


CASES = [
    ("a1", a1_dirty_pushed_file),
    ("a2", a2_unpushed_stale_fallback),
    ("a3", a3_detached_head_unpushed),
    ("a4", a4_ledger_self_copy),
    ("a5", a5_ledger_vault_inside_source),
    ("a6", a6_ledger_dir_missing_vault_digest),
    ("a7", a7_gitfile_repo_root),
    ("a8", a8_tab_path_injection),
    ("a9", a9_hidden_live_reference),
    ("a10", a10_missing_sweep_scope),
    ("a11", a11_quarantine_symlink_root),
    ("a12", a12_pushed_second_check_default_ref),
    ("a13", a13_nul_list_gate),
]


def main():
    sel = [x for x in A.only.split(",") if x]
    out = {
        "seat": "S02", "round": 10, "cluster": "A",
        "tools_dir": str(TOOLS), "fixture_root": "/var/tmp",
        "tool_sha256": {n: hashlib.sha256((TOOLS / n).read_bytes()).hexdigest()
                        for n in (A.verify, A.vault, A.quarantine)},
        "cases": [],
    }
    for cid, fn in CASES:
        if sel and not any(cid.startswith(s) for s in sel):
            continue
        try:
            rec = fn()
        except Exception as e:  # noqa: BLE001
            rec = {"case": cid, "error": repr(e)}
        out["cases"].append(rec)
        print(f"[{rec.get('case', cid)}] "
              f"verify={rec.get('verify', {}).get('verdict')}/"
              f"{rec.get('verify', {}).get('receipt')} "
              f"quarantine={rec.get('quarantine', {}).get('result')} "
              f"false_safe={rec.get('false_safe_verify')} "
              f"unsafe_delete={rec.get('unsafe_delete')} "
              f"error={rec.get('error', '')}", flush=True)
    fs = [c["case"] for c in out["cases"] if c.get("false_safe_verify") or c.get("false_safe_vault")]
    ud = [c["case"] for c in out["cases"] if c.get("unsafe_delete")]
    out["counts"] = {"cases": len(out["cases"]), "false_safe_cases": len(fs),
                     "unsafe_delete_cases": len(ud),
                     "false_safe": fs, "unsafe_delete": ud}
    print(f"COUNT cases={out['counts']['cases']} false_safe={len(fs)} unsafe_delete={len(ud)}")
    if A.out:
        Path(A.out).write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
