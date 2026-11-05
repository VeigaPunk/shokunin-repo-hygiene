#!/usr/bin/env python3
"""k67-proposed.py — PROPOSED fixture rows for the r66 survivors K3/K4/K6/K7 and the r67 GIT_COMMON_DIR
non-canonical / empty / relative cases (S67MutKill, scratch only).

NOT part of the frozen 31-row matrix. Imports the frozen counter (a read-only scratch copy of
census/round-67/c1-counter.py) only for its fixture machinery (build_repo, clean_env, judge, GIT_DATE, FORGED_INSTR);
the frozen file is never edited. Each defect row has an honest control (the same fixture without the defect).

Usage: k67-proposed.py --base-slot BASE.py [--new-slot NAME=PATH ...] [--rows a,b] --work DIR
  --work must exist; writes only under DIR/<row>/<slot>/.
Output per (row, slot): PROP <row> slot=<name> expect=<accept|refuse> verdict=<v> class=<hit|-> rc=<n> stderr=<...>
"""
import argparse
import importlib.util
import os
import subprocess
import sys

FROZEN = "/fast/scratch/hyaku/souji-r67/S67MutKill/frozen/c1-counter.py"
_spec = importlib.util.spec_from_file_location("c1frozen", FROZEN)
c1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c1)

GIT_ID = {"GIT_AUTHOR_NAME": "S67 Proposed", "GIT_AUTHOR_EMAIL": "s67-proposed@invalid",
          "GIT_COMMITTER_NAME": "S67 Proposed", "GIT_COMMITTER_EMAIL": "s67-proposed@invalid",
          "GIT_AUTHOR_DATE": c1.GIT_DATE, "GIT_COMMITTER_DATE": c1.GIT_DATE}


def git(repo, *args, env=None):
    r = subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=c1.clean_env(env), timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed rc={r.returncode}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r


def assert_toplevel(repo):
    top = git(repo, "rev-parse", "--show-toplevel").stdout.decode().strip()
    if os.path.realpath(top) != os.path.realpath(repo):
        raise RuntimeError(f"toplevel {top!r} != {repo!r}")


def write(path, data: bytes, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    if mode is not None:
        os.chmod(path, mode)


# ---- fixture setups: (repo, case_dir, honest) -> env_extra ----

def setup_k3_local_excludes(repo, case, honest):
    """K3: REPOSITORY-LOCAL core.excludesFile naming hidden.txt; the untracked file hides only if the -c pin loses."""
    excl = os.path.join(case, "excl-local.txt")
    write(excl, b"hidden.txt\n")
    git(repo, "config", "core.excludesFile", excl)
    if not honest:
        write(os.path.join(repo, "tools", "hidden.txt"), b"u\n")
    return {}


def setup_k4_global_mode(repo, case, honest):
    """K4: caller-named GLOBAL config with core.fileMode=false (not an excludes key, so the -c pin does not cover it).
    Repo-local core.filemode UNSET so the global value is effective; tracked 755->644 in the defect variant."""
    git(repo, "config", "--unset", "core.filemode")
    gcfg = os.path.join(case, "global-mode.gitconfig")
    write(gcfg, b"[core]\n\tfileMode = false\n")
    if not honest:
        os.chmod(os.path.join(repo, "tools", "instr.sh"), 0o644)
    return {"GIT_CONFIG_GLOBAL": gcfg}


def setup_k6_replace(repo, case, honest):
    """K6: replace ref for HEAD whose replacement tree carries FORGED instrument bytes; worktree and index carry the
    same forged bytes, so only a replacement-honouring read sees a clean, matching tree."""
    if honest:
        return {}
    head = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
    fpath = os.path.join(case, "forged-instr.sh")
    write(fpath, c1.FORGED_INSTR, 0o755)
    blob = git(repo, "hash-object", "-w", fpath).stdout.decode().strip()
    ienv = {"GIT_INDEX_FILE": os.path.join(case, "forge-idx")}
    git(repo, "read-tree", head, env=ienv)
    git(repo, "update-index", "--add", "--cacheinfo", f"100755,{blob},tools/instr.sh", env=ienv)
    tree = git(repo, "write-tree", env=ienv).stdout.decode().strip()
    rep = git(repo, "commit-tree", tree, "-p", head, "-m", "s67 forged replacement", env=GIT_ID).stdout.decode().strip()
    git(repo, "update-ref", f"refs/replace/{head}", rep)
    write(os.path.join(repo, "tools", "instr.sh"), c1.FORGED_INSTR, 0o755)
    git(repo, "update-index", "--cacheinfo", f"100755,{blob},tools/instr.sh")
    return {}


def setup_k7_system_mode(repo, case, honest):
    """K7: caller-named SYSTEM config with core.fileMode=false; base pins GIT_CONFIG_NOSYSTEM=1; repo-local
    core.filemode UNSET; tracked 755->644 in the defect variant."""
    git(repo, "config", "--unset", "core.filemode")
    scfg = os.path.join(case, "system-mode.gitconfig")
    write(scfg, b"[core]\n\tfileMode = false\n")
    if not honest:
        os.chmod(os.path.join(repo, "tools", "instr.sh"), 0o644)
    return {"GIT_CONFIG_SYSTEM": scfg}


def setup_repo_local_filemode(repo, case, honest):
    """PRL-fm (measured named limit, NOT a kill target): repo-local core.fileMode=false (a repository's own config,
    the L0 361 scope) with a tracked 755->644 change. Expected accept on base and candidate: the writer does not
    read repo-local mode config as an attack surface."""
    git(repo, "config", "core.filemode", "false")
    os.chmod(os.path.join(repo, "tools", "instr.sh"), 0o644)
    return {}


def setup_commondir_alias(repo, case, honest):
    """W3-alias: GIT_COMMON_DIR is a SYMLINK to the repository's own .git (equal after canonicalization)."""
    alias = os.path.join(case, "alias-git")
    os.symlink(os.path.realpath(os.path.join(repo, ".git")), alias)
    return {"GIT_COMMON_DIR": alias}


def setup_commondir_relative(repo, case, honest):
    """W3-rel: GIT_COMMON_DIR='.git' with the writer run from the repo root (git's own relative rule)."""
    return {"GIT_COMMON_DIR": ".git"}


def setup_commondir_relative_up(repo, case, honest):
    """W3-up: GIT_COMMON_DIR='../.git' with the writer run from <repo>/tools (cwd-relative, not root-relative)."""
    return {"GIT_COMMON_DIR": "../.git"}


def setup_commondir_empty(repo, case, honest):
    """E-empty: GIT_COMMON_DIR set to the empty string; the writer runs FROM <repo>/.git, where realpath('') is the
    common dir itself. Defect (no empty refusal) accepts; candidate refuses on presence."""
    return {"GIT_COMMON_DIR": ""}


# row id, expect (candidate/canonical expectation), setup, expected class token or '-', run cwd ('root'|'gitdir'|'tools'), note
PROPOSED = [
    ("PK3", "refuse", setup_k3_local_excludes, "lane worktree is dirty", "root", "repo-local core.excludesFile hides untracked"),
    ("PK3h", "accept", setup_k3_local_excludes, "-", "root", "honest control: same excludes config, no untracked file"),
    ("PK4", "refuse", setup_k4_global_mode, "lane worktree is dirty", "root", "global core.fileMode=false hides tracked 755->644"),
    ("PK4h", "accept", setup_k4_global_mode, "-", "root", "honest control: same global config, no mode change"),
    ("PK6", "refuse", setup_k6_replace, "-", "root", "replace ref forges HEAD's instrument tree"),
    ("PK6h", "accept", setup_k6_replace, "-", "root", "honest control: no replace ref"),
    ("PK7", "refuse", setup_k7_system_mode, "lane worktree is dirty", "root", "GIT_CONFIG_SYSTEM core.fileMode=false hides 755->644"),
    ("PK7h", "accept", setup_k7_system_mode, "-", "root", "honest control: same system config, no mode change"),
    ("PCD-alias", "accept", setup_commondir_alias, "-", "root", "symlink GIT_COMMON_DIR equal after canonicalization"),
    ("PCD-rel", "accept", setup_commondir_relative, "-", "root", "relative '.git' run from the root"),
    ("PCD-up", "accept", setup_commondir_relative_up, "-", "tools", "relative '../.git' run from tools/ (cwd-relative)"),
    ("PCD-empty", "refuse", setup_commondir_empty, "RECEIPT-ENV-COMMONDIR-MISMATCH", "gitdir", "empty value, cwd == common dir"),
    ("PRL-fm", "accept", setup_repo_local_filemode, "-", "root", "measured L1 limit: repo-local core.fileMode=false hides a mode change (not a kill target)"),
]


def run_writer(slot, repo, rev, out, wrapped, cwd, env_extra):
    argv = [sys.executable, "-B", slot, "--root", repo, "--rev", rev,
            "--instrument", "tools/instr.sh", "--out", out, "--allow-outside", "--", *wrapped]
    try:
        p = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=c1.clean_env(env_extra), timeout=180)
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    return p.returncode, p.stderr.decode("utf-8", "replace")


def run_row(row, expect, setup, klass, cwd_kind, note, slot, slot_name, work):
    case_root = os.path.join(work, row, slot_name)
    repo, rev = c1.build_repo(case_root)
    assert_toplevel(repo)
    honest = row.endswith("h") or row.startswith("PCD")
    env_extra = setup(repo, case_root, honest)
    cwd = {"root": repo, "gitdir": os.path.join(repo, ".git"), "tools": os.path.join(repo, "tools")}[cwd_kind]
    out = os.path.join(case_root, "out", "receipt.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rc, se = run_writer(slot, repo, rev, out, ["/bin/echo", "hi"], cwd, env_extra)
    verdict = c1.judge(rc, out)
    hit = klass if (verdict == "refuse" and klass != "-" and klass in se) else "-"
    one = " ".join(se.split())[:200]
    print(f"PROP {row} slot={slot_name} expect={expect} verdict={verdict} class={hit} rc={rc} stderr={one!r}")
    return verdict


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-slot", required=True)
    ap.add_argument("--new-slot", action="append", default=[], help="NAME=PATH (repeatable)")
    ap.add_argument("--work", required=True)
    ap.add_argument("--rows", default=None, help="comma list of row ids (default all)")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if not os.path.isdir(work):
        print("work dir missing", file=sys.stderr)
        return 2
    slots = [("base", os.path.abspath(ns.base_slot))]
    for spec in ns.new_slot:
        name, _, path = spec.partition("=")
        slots.append((name, os.path.abspath(path)))
    wanted = set(ns.rows.split(",")) if ns.rows else None
    for row, expect, setup, klass, cwd_kind, note in PROPOSED:
        if wanted and row not in wanted:
            continue
        print(f"# row {row} expect={expect} class={klass} cwd={cwd_kind} note={note}")
        for name, path in slots:
            run_row(row, expect, setup, klass, cwd_kind, note, path, name, work)
    print("EXIT=0")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
