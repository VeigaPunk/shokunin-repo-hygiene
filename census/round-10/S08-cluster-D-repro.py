#!/usr/bin/env python3
"""S08 (round 10) cluster-D extended repro: stale-sweep / worktree-metadata /
directory-receipt classes K-T (A-J live in tools/cand-d2-probe.sh).

Fresh fixtures only, forced under /var/tmp. Read-only against the tool under
test: every destructive call runs inside a mktemp fixture repo.

Usage: python3 S08-cluster-D-repro.py [--tools DIR] [--tool NAME] [--out FILE]
"""
import argparse
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
P.add_argument("--tool", default="souji-verify.sh")
P.add_argument("--out", default="")
A = P.parse_args()
TOOLS = Path(A.tools).resolve()
TOOL = TOOLS / A.tool
OLD = int(time.time()) - 6 * 86400

PASS = 0
FAIL = 0
ROWS = []


def sh(cmd, env, cwd=None, data=None):
    return subprocess.run([str(x) for x in cmd], input=data, text=True,
                          capture_output=True, env=env, cwd=cwd, timeout=60)


class Fx:
    def __init__(self, name):
        self.root = Path(tempfile.mkdtemp(prefix="s08-d-" + name + ".", dir="/var/tmp"))
        self.fleet = self.root / "fleet"
        self.repo = self.fleet / (name + "-shokunin")
        self.repo.mkdir(parents=True)
        self.home = self.root / "home"
        self.home.mkdir()
        self.ledger = self.root / "ledger.tsv"
        self.ledger.write_text("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        e = os.environ.copy()
        for k in list(e):
            if k.startswith("GIT_") or k.startswith("SOUJI_") or k == "SHOKUNIN_ROOT":
                e.pop(k)
        e.update({
            "PATH": os.environ["PATH"], "HOME": str(self.home), "TMPDIR": "/var/tmp",
            "LC_ALL": "C", "LANG": "C",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "S08 fixture", "GIT_AUTHOR_EMAIL": "s08@example.invalid",
            "GIT_COMMITTER_NAME": "S08 fixture", "GIT_COMMITTER_EMAIL": "s08@example.invalid",
            "SHOKUNIN_ROOT": str(self.fleet), "SOUJI_LEDGER": str(self.ledger),
            "SOUJI_Q_SHOKUNIN_ROOT": str(self.fleet), "SOUJI_Q_LEDGER": str(self.ledger),
        })
        self.env = e
        self.git("init", "-q", "--initial-branch=main", str(self.repo))
        self.write("seed.txt", "pushed seed\n")
        self.head = self.commit()
        self.pushed(self.head)

    def git(self, *args, data=None, repo=None):
        r = sh(["git", "-C", str(repo or self.repo), *args], self.env, data=data)
        if r.returncode:
            raise RuntimeError(f"git {args}: {r.returncode} {r.stderr}")
        return r.stdout.strip()

    def write(self, rel, data, repo=None):
        p = (repo or self.repo) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data)
        return p

    def commit(self, remote=False, repo=None):
        repo = repo or self.repo
        self.git("add", "-A", repo=repo)
        tree = self.git("write-tree", repo=repo)
        r = sh(["git", "-C", str(repo), "rev-parse", "--verify", "-q", "refs/heads/main"], self.env)
        parent = r.stdout.strip() or None
        args = ["commit-tree", tree]
        if parent:
            args += ["-p", parent]
        sha = self.git(*args, data="S08 fixture\n", repo=repo)
        self.git("update-ref", "refs/heads/main", sha, repo=repo)
        if repo == self.repo:
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

    def register_wt(self, owner, name, wt, head, link=False):
        adm = Path(owner) / ".git" / "worktrees" / name
        adm.mkdir(parents=True, exist_ok=True)
        (adm / "HEAD").write_text(head + "\n")
        (adm / "commondir").write_text("../..\n")
        (adm / "gitdir").write_text(f"{wt}/.git\n")
        if link:
            Path(wt).mkdir(parents=True, exist_ok=True)
            (Path(wt) / ".git").write_text(f"gitdir: {adm}\n")

    def verify(self, target, tool=None):
        r = sh(["bash", TOOLS / (tool or A.tool), "--json", "--", str(target)], self.env)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"verdict": "UNPARSEABLE", "receipt": "?", "evidence": r.stdout[:200],
                 "rc": r.returncode}
        return d


def check(cls, want_v, want_r, got, note):
    global PASS, FAIL
    ok = got.get("verdict") == want_v and (not want_r or got.get("receipt") == want_r)
    if ok:
        PASS += 1
        print(f"PASS\t{cls}\t{got.get('verdict')}({got.get('receipt')})")
    else:
        FAIL += 1
        print(f"DEFECT\t{cls}\tgot={got.get('verdict')}({got.get('receipt')})"
              f"\twant={want_v}({want_r})\tev={got.get('evidence')}\t{note}")
    ROWS.append({"class": cls, "want": [want_v, want_r], "got": got, "note": note, "ok": ok})


# ---------------------------------------------------------------- cases ----

def k_binary_referrer():
    """A reference that exists only inside a binary file (rg skips binaries
    without --text) must still block the stale receipt."""
    f = Fx("k-binary")
    f.write(".scratch/old-k.out", "payload\n")
    blob = b"\x00\x01old-k.out\x00\x02" * 8
    (f.repo / "asset.bin").write_bytes(blob)
    f.age(f.repo / ".scratch/old-k.out", f.repo / ".scratch")
    check("K-binary-referrer", "NOT-SAFE", "", f.verify(f.repo / ".scratch/old-k.out"),
          "a binary referrer is a live reference")


def l_secret_referrer():
    """A reference held only in a secret-shaped file. The province forbids
    reading secret content, so the sweep must exclude it -- but the receipt
    must DISCLOSE the unread surface rather than silently claim refs=0."""
    f = Fx("l-hiddenref")
    f.write(".scratch/old-l.out", "payload\n")
    f.write(".env", "KEEP=old-l.out\n")
    f.age(f.repo / ".scratch/old-l.out", f.repo / ".scratch")
    got = f.verify(f.repo / ".scratch/old-l.out")
    ok = got.get("verdict") == "SAFE" and got.get("receipt") == "stale" \
        and "unread-secret-shaped-files=1" in got.get("evidence", "")
    check("L-secret-shaped-referrer", "SAFE", "stale" if ok else "DISCLOSURE-MISSING", got,
          "unread secret surface must be disclosed in the receipt")


def l2_no_disclosure_when_clean():
    """Control: with no secret-shaped file in scope the receipt carries no
    disclosure clause (the flag is not boilerplate)."""
    f = Fx("l2-clean")
    f.write(".scratch/old-l2.out", "payload\n")
    f.age(f.repo / ".scratch/old-l2.out", f.repo / ".scratch")
    got = f.verify(f.repo / ".scratch/old-l2.out")
    ok = got.get("verdict") == "SAFE" and got.get("receipt") == "stale" \
        and "unread-secret-shaped-files" not in got.get("evidence", "")
    check("L2-no-disclosure-when-clean", "SAFE", "stale" if ok else "SPURIOUS-DISCLOSURE", got,
          "no disclosure clause when the surface is empty")


def m_detached_head_commit():
    """A commit reachable only from the main worktree's detached HEAD."""
    f = Fx("m-detached-head")
    art = f.write("keep-m.txt", "pushed bytes\n")
    tip = f.commit(remote=True)
    f.write("keep-m.txt", "detached-only bytes\n")
    f.git("add", "-A")
    tree = f.git("write-tree")
    det = f.git("commit-tree", tree, "-p", tip, data="detached\n")
    f.git("symbolic-ref", "HEAD", f"refs/heads/main")  # main stays at tip
    f.git("update-ref", "refs/heads/main", tip)
    f.git("checkout", "--detach", det, "--")
    f.git("read-tree", det)
    check("M-detached-HEAD-commit", "NOT-SAFE", "", f.verify(art),
          "bytes held only by a detached HEAD are not pushed")


def n_nested_ignored_child():
    """Pushed directory whose ignored child is nested two levels deep."""
    f = Fx("n-nested-ignored")
    f.write("bundle/deep/public.txt", "preserved\n")
    f.write(".gitignore", "bundle/deep/local.txt\n")
    tip = f.commit(remote=True)
    f.write("bundle/deep/local.txt", "ignored sole copy\n")
    check("N-nested-ignored-child", "NOT-SAFE", "", f.verify(f.repo / "bundle"),
          "an ignored descendant has no pushed copy")


def o_staged_deletion():
    """Pushed directory carrying a staged (index-level) deletion."""
    f = Fx("o-staged-deletion")
    f.write("bundle/public.txt", "preserved\n")
    f.write("bundle/gone.txt", "to be deleted\n")
    f.commit(remote=True)
    f.git("rm", "--cached", "-q", "bundle/gone.txt")
    check("O-staged-deletion", "NOT-SAFE", "", f.verify(f.repo / "bundle"),
          "a staged deletion is unpublished state")


def p_deep_fresh_grandchild():
    """Aged container, aged child, fresh grandchild (recursion depth 2)."""
    f = Fx("p-deep-fresh")
    f.write(".scratch/old-p/mid/leaf.md", "fresh unique leaf\n")
    f.age(f.repo / ".scratch", f.repo / ".scratch/old-p", f.repo / ".scratch/old-p/mid")
    check("P-deep-fresh-grandchild", "NOT-SAFE", "", f.verify(f.repo / ".scratch/old-p"),
          "a fresh grandchild must block the stale receipt")


def q_unmatched_owner_prune():
    """Control: dead registration in a repo the *-shokunin glob never matches,
    dir absent and no unique commit -> metadata-prune stays available."""
    f = Fx("q-unmatched-prune")
    legacy = f.fleet / "legacy-lane"
    legacy.mkdir()
    sh(["git", "-C", str(legacy), "init", "-q", "--initial-branch=main"], f.env)
    f.git("add", "-A", repo=legacy)
    tree = f.git("write-tree", repo=legacy)
    sha = f.git("commit-tree", tree, data="legacy\n", repo=legacy)
    f.git("update-ref", "refs/heads/main", sha, repo=legacy)
    f.git("update-ref", "refs/remotes/origin/main", sha, repo=legacy)
    f.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main", repo=legacy)
    f.register_wt(legacy, "wt-q", f.root / "wt-q-absent", sha)
    got = f.verify(f.root / "wt-q-absent")
    check("Q-unmatched-owner-prune-control", "SAFE", "metadata-prune", got,
          "a dead registration is prunable metadata")


def r_unmatched_owner_live():
    """A live (dirty) registered worktree in a repo the glob never matches."""
    f = Fx("r-unmatched-live")
    legacy = f.fleet / "legacy-lane"
    legacy.mkdir()
    sh(["git", "-C", str(legacy), "init", "-q", "--initial-branch=main"], f.env)
    f.git("add", "-A", repo=legacy)
    tree = f.git("write-tree", repo=legacy)
    sha = f.git("commit-tree", tree, data="legacy\n", repo=legacy)
    f.git("update-ref", "refs/heads/main", sha, repo=legacy)
    f.git("update-ref", "refs/remotes/origin/main", sha, repo=legacy)
    f.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main", repo=legacy)
    wt = legacy / ".scratch/wt-r"
    f.register_wt(legacy, "wt-r", wt, sha, link=True)
    f.write(".scratch/wt-r/stray.txt", "unpublished\n", repo=legacy)
    f.age(wt)
    check("R-unmatched-owner-live", "NOT-SAFE", "", f.verify(wt),
          "a live worktree of an unmatched owner is not stale")


def s_gitfile_worktree_dir():
    """The registered worktree dir contains a .git gitfile (real worktree):
    the stale sweep must not treat it as an ordinary scratch directory."""
    f = Fx("s-gitfile-wt")
    wt = f.repo / ".scratch/wt-s"
    f.register_wt(f.repo, "wt-s", wt, "ref: refs/heads/main", link=True)
    f.age(wt)
    check("S-gitfile-worktree-dir", "NOT-SAFE", "", f.verify(wt),
          "a gitfile marks a worktree, not stale scratch")


def t_dir_self_reference_only():
    """Control: aged scratch dir whose only basename mention is inside itself
    (self-reference) and nowhere else -> stale receipt stays available."""
    f = Fx("t-self-ref")
    f.write(".scratch/old-t/notes.txt", "old-t is this bundle's own name\n")
    f.age(f.repo / ".scratch/old-t", f.repo / ".scratch/old-t/notes.txt", f.repo / ".scratch")
    check("T-dir-self-reference-control", "SAFE", "stale", f.verify(f.repo / ".scratch/old-t"),
          "self-reference is not a live reference")


CASES = [k_binary_referrer, l_secret_referrer, l2_no_disclosure_when_clean,
         m_detached_head_commit, n_nested_ignored_child, o_staged_deletion,
         p_deep_fresh_grandchild, q_unmatched_owner_prune, r_unmatched_owner_live,
         s_gitfile_worktree_dir, t_dir_self_reference_only]

for fn in CASES:
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        FAIL += 1
        print(f"ERROR\t{fn.__name__}\t{e!r}")
        ROWS.append({"class": fn.__name__, "error": repr(e), "ok": False})

print(f"PROBE\t{A.tool}\tpass={PASS}\tdefect={FAIL}")
if A.out:
    Path(A.out).write_text(json.dumps({"tool": A.tool, "pass": PASS, "defect": FAIL,
                                       "rows": ROWS}, indent=1))
sys.exit(1 if FAIL else 0)
