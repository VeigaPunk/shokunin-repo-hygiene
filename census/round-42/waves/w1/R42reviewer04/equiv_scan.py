#!/usr/bin/env python3
"""Equivalence scan for the six EQUIV mutants of c3-counter.py (B3 B4 E5 E7 E9 H4).

Each scenario builds two identical fresh trees (one for the pristine tool, one for the mutant), runs
the tool, and compares rc, hang flag, stdout, stderr (base paths normalised) and a snapshot of every
file the scenario tree holds after the run (non-.git file contents by sha256, .git by name only).
Usage: python3 -B equiv_scan.py B3 B4 E5 E7 E9 H4
"""
import hashlib
import os
import stat
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import (PRISTINE, mut, fresh, build_fleet, mkrepo, add_worktree, write, run, norm)

RECORD_DRIFT = ("REPO\talpha\tregs=5\tprunable=0\nREPO\tbeta\tregs=1\tprunable=0\n"
                "TOTAL\trepos=2\tregs=6\tprunable=0\n")
SCEN = []


def scenario(fn):
    SCEN.append((fn.__name__, fn))
    return fn


def rec(b, text=None, name="record.tsv", data=None):
    path = os.path.join(b, name)
    if data is not None:
        return write(path, data)
    return write(path, text if text is not None else open(os.path.join(b, "record.tsv"), "rb").read())


@scenario
def S01_plain_no_json(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv")]], b


@scenario
def S02_json_outside_root(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", os.path.join(b, "out", "r.json")]], b


@scenario
def S03_drift_and_json_outside(b):
    F = build_fleet(b)
    r = write(os.path.join(b, "rec-drift.tsv"), RECORD_DRIFT)
    return [["--root", F, "--record", r, "--json", os.path.join(b, "out", "d.json")]], b


@scenario
def S04_json_inside_root(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", os.path.join(F, "out.json")]], b


@scenario
def S05_json_inside_measured_repo(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", os.path.join(F, "alpha", "out.json")]], b


@scenario
def S06_json_inside_repo_gitdir(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", os.path.join(F, "alpha", ".git", "out.json")]], b


@scenario
def S07_json_inside_linked_worktree_gitdir(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"),
             "--json", os.path.join(F, "alpha", ".git", "worktrees", "alpha-wt", "out.json")]], b


@scenario
def S08_json_is_record(b):
    F = build_fleet(b)
    r = os.path.join(b, "record.tsv")
    return [["--root", F, "--record", r, "--json", r]], b


@scenario
def S09_json_hardlink_alias_of_record(b):
    F = build_fleet(b)
    r = os.path.join(b, "record.tsv")
    os.makedirs(os.path.join(b, "out"), exist_ok=True)
    alias = os.path.join(b, "out", "alias.tsv")
    os.link(r, alias)
    return [["--root", F, "--record", r, "--json", alias]], b


@scenario
def S10_json_hardlinked_outside(b):
    F = build_fleet(b)
    os.makedirs(os.path.join(b, "out"), exist_ok=True)
    other = write(os.path.join(b, "out", "other.json"), b"keep")
    hl = os.path.join(b, "out", "hl.json")
    os.link(other, hl)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", hl]], b


@scenario
def S11_json_empty_string(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", ""]], b


@scenario
def S12_json_sibling_with_shared_name_prefix(b):
    F = build_fleet(b)
    os.makedirs(os.path.join(b, "fleet-out"))
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", os.path.join(b, "fleet-out", "x.json")]], b


@scenario
def S13_root_is_itself_a_repo(b):
    R = mkrepo(os.path.join(b, "rootrepo"))
    r = write(os.path.join(b, "rec-root.tsv"), "REPO\trootrepo\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return [["--root", R, "--record", r, "--json", os.path.join(b, "out", "x.json")]], b


@scenario
def S14_record_row_outside_root(b):
    F = build_fleet(b)
    mkrepo(os.path.join(b, "outside", "gamma"))
    r = write(os.path.join(b, "rec-out.tsv"), "REPO\t../outside/gamma\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return [["--root", F, "--record", r]], b


@scenario
def S15_gitdir_outside_root(b):
    F = build_fleet(b)
    gamma = mkrepo(os.path.join(b, "outside", "gamma"))
    add_worktree(gamma, os.path.join(F, "zeta"), "zz")
    r = write(os.path.join(b, "rec-zeta.tsv"), "REPO\tzeta\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return [["--root", F, "--record", r, "--json", os.path.join(b, "out", "z.json")]], b


@scenario
def S16_json_parent_missing(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", os.path.join(b, "nope", "x.json")]], b


@scenario
def S17_json_is_fifo_outside(b):
    F = build_fleet(b)
    os.makedirs(os.path.join(b, "out"), exist_ok=True)
    f = os.path.join(b, "out", "f.json")
    os.mkfifo(f)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", f]], b


@scenario
def S18_json_symlink_in_root_to_outside(b):
    F = build_fleet(b)
    os.makedirs(os.path.join(b, "out"), exist_ok=True)
    target = os.path.join(b, "out", "target.json")
    os.symlink(target, os.path.join(F, "ln.json"))
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", os.path.join(F, "ln.json")]], b


@scenario
def S19_json_symlink_in_root_to_inside_repo(b):
    F = build_fleet(b)
    os.symlink(os.path.join(F, "alpha", "out2.json"), os.path.join(F, "ln2.json"))
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", os.path.join(F, "ln2.json")]], b


@scenario
def S20_json_is_root_directory(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", F]], b


@scenario
def S21_large_record_and_json(b):
    F = build_fleet(b)
    lines = ["REPO\tn%04d\tregs=1\tprunable=0" % i for i in range(2000)]
    text = "\n".join(lines) + "\nTOTAL\trepos=2000\tregs=2000\tprunable=0\n"
    r = write(os.path.join(b, "rec-big.tsv"), text)
    return [["--root", F, "--record", r, "--skip-unrecorded", "--json", os.path.join(b, "out", "big.json")]], b


@scenario
def S22_record_is_directory(b):
    F = build_fleet(b)
    d = os.path.join(b, "recdir")
    os.makedirs(d)
    return [["--root", F, "--record", d]], b


@scenario
def S23_record_is_symlink_to_regular(b):
    F = build_fleet(b)
    link = os.path.join(b, "rec-link.tsv")
    os.symlink(os.path.join(b, "record.tsv"), link)
    return [["--root", F, "--record", link]], b


@scenario
def S24_empty_record(b):
    F = build_fleet(b)
    r = write(os.path.join(b, "rec-empty.tsv"), b"")
    return [["--root", F, "--record", r]], b


@scenario
def S25_nonutf8_and_multibyte_names(b):
    F = build_fleet(b)
    data = (b"# caf\xc3\xa9 census\nREPO\tcaf\xc3\xa9\tregs=1\tprunable=0\nREPO\talp\xffha\tregs=2\tprunable=0\n"
            b"TOTAL\trepos=2\tregs=3\tprunable=0\n")
    r = write(os.path.join(b, "rec-mb.tsv"), data)
    return [["--root", F, "--record", r, "--skip-unrecorded"]], b


@scenario
def S26_json_inside_unmeasured_outside_repo(b):
    F = build_fleet(b)
    gamma = mkrepo(os.path.join(b, "outside", "gamma"))
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", os.path.join(gamma, "out.json")]], b


@scenario
def S27_timeout_one_plain(b):
    F = build_fleet(b)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--timeout", "1", "--json", os.path.join(b, "out", "t.json")]], b


def under_objects(rel):
    # git object files are named by hashes of commit objects, which embed the commit time; they are
    # excluded from the snapshot (the tool never reads them), everything else under .git is kept by name.
    parts = rel.split(os.sep)
    return any(parts[i] == ".git" and i + 1 < len(parts) and parts[i + 1] == "objects" for i in range(len(parts)))


@scenario
def S28_json_prefilled_longer_target(b):
    F = build_fleet(b)
    t = write(os.path.join(b, "out", "long.json"), b"x" * 4096)
    return [["--root", F, "--record", os.path.join(b, "record.tsv"), "--json", t]], b


@scenario
def S29_json_prefilled_longer_target_with_drift(b):
    F = build_fleet(b)
    r = write(os.path.join(b, "rec-drift2.tsv"), RECORD_DRIFT)
    t = write(os.path.join(b, "out", "long2.json"), b"y" * 8192)
    return [["--root", F, "--record", r, "--json", t]], b


def snap(base):
    out = []
    real = os.path.realpath(base)
    for dp, dns, fns in os.walk(base):
        rel = os.path.relpath(dp, base)
        in_git = ".git" in rel.split(os.sep)
        if under_objects(rel):
            continue
        for name in sorted(dns + fns):
            p = os.path.join(dp, name)
            r = os.path.relpath(p, base)
            if under_objects(r):
                continue
            if os.path.islink(p):
                out.append((r, "link", norm(os.readlink(p), base).replace(real, "<BASE>")))
                continue
            st = os.lstat(p)
            if stat.S_ISDIR(st.st_mode):
                out.append((r, "dir", None))
            elif not stat.S_ISREG(st.st_mode):
                out.append((r, "special", stat.S_IFMT(st.st_mode)))
            elif in_git:
                out.append((r, "gitfile", None))
            else:
                with open(p, "rb") as f:
                    data = f.read()
                out.append((r, "file", hashlib.sha256(norm(data.decode("utf-8", "surrogateescape"), base)
                                                       .replace(real, "<BASE>").encode("utf-8", "surrogateescape")).hexdigest()[:16]))
    return sorted(out, key=lambda t: t[0])


def outcome(tool, tag, fn):
    base = fresh("equiv", tag)
    os.makedirs(os.path.join(base, "out"))
    argvs, cwd = fn(base)
    r = run(tool, argvs[0], cwd, timeout=30)
    real = os.path.realpath(base)
    return {"rc": r["rc"], "hang": r["hang"],
            "out": norm(r["out"], base).replace(real, "<BASE>"),
            "err": norm(r["err"], base).replace(real, "<BASE>"),
            "tree": snap(base)}


def main(ids):
    pristine = {}
    for name, fn in SCEN:
        pristine[name] = outcome(PRISTINE, "pristine-" + name, fn)
    print("pristine scenarios: %d; rc distribution %s" % (
        len(SCEN), {k: sum(1 for v in pristine.values() if v["rc"] == k) for k in sorted({v["rc"] for v in pristine.values()}, key=str)}))
    for mid in ids:
        diffs = []
        for name, fn in SCEN:
            m = outcome(mut(mid), "mut%s-%s" % (mid, name), fn)
            p = pristine[name]
            same = m == p
            if not same:
                diffs.append(name)
                for k in ("rc", "hang", "out", "err", "tree"):
                    if m[k] != p[k]:
                        if k == "tree":
                            sym = sorted(set(p[k]) ^ set(m[k]), key=str)
                            print("  DIFF %s %s field=tree symdiff=%r" % (mid, name, sym[:6]))
                        else:
                            print("  DIFF %s %s field=%s pristine=%r mutant=%r" % (mid, name, k, str(p[k])[:300], str(m[k])[:300]))
            print("  %s %-44s pristine_rc=%s mutant_rc=%s %s" % (mid, name, p["rc"], m["rc"], "same" if same else "DIFFERENT"))
        if diffs:
            print("EQUIV %s: OBSERVABLE DIFFERENCE in %d of %d scenarios: %s" % (mid, len(diffs), len(SCEN), diffs))
        else:
            print("EQUIV %s: no difference found in %d scenarios (rc, hang, stdout, stderr, full tree snapshot)" % (mid, len(SCEN)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
