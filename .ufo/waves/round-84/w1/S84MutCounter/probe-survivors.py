#!/usr/bin/env python3
"""souji r84 C1 extension (seat S84MutCounter): reproducer probes for the ten-mutant survivors.

For every mutant that survives both pinned populations, this probe asks: is the clause bindable at all, and by which
row shape? It calls the counter's own `judge`/`_ledger` on a small throwaway git repo (never the lane) with hand-made
population items, so the probe does not need a pinned population file and does not edit the lane.

Output: PROBE <name> pristine=<status> <mutant>=<status> would_kill=<yes|no> note=<...>
Exit 0 always (a probe report, not a gate).
"""
import importlib.util
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-84/w1/S84MutCounter")
SCRATCH = sys.argv[1]
COUNTER = os.path.join(LANE, "census/round-84/c1-pointer-counter.py")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, "-c", "user.name=probe", "-c", "user.email=probe@invalid",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise SystemExit(f"probe git {args} rc={p.returncode}: {p.stderr.decode()[:300]}")
    return p.stdout.decode().strip()


def main():
    repo = os.path.join(SCRATCH, "probe-repo")
    os.makedirs(repo, exist_ok=True)
    if not os.path.isdir(os.path.join(repo, ".git")):
        git(repo, "init", "-q")
    if os.path.realpath(git(repo, "rev-parse", "--show-toplevel")) != os.path.realpath(repo):
        raise SystemExit("probe repo toplevel is not the probe dir")
    one = b"same byte source\n"
    p = os.path.join(repo, ".ufo/waves/round-32/w2/one.txt")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(one)
    git(repo, "add", "-f", "--", ".ufo/waves/round-32/w2/one.txt")
    if subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "HEAD"], stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL).returncode != 0:
        git(repo, "commit", "-q", "--no-verify", "-m", "probe bytes")
    rev = git(repo, "rev-parse", "HEAD")
    q = os.path.join(repo, ".ufo/quarantine")
    os.makedirs(q, exist_ok=True)
    with open(os.path.join(q, "fixture-leaf.txt"), "wb") as f:
        f.write(b"the lane disk quarantine is not empty here\n")
    base = load(COUNTER, "pristine_counter")
    frozen_dir = base.rev_digest(repo, rev, ".ufo/waves/round-32/w2")
    assert frozen_dir and frozen_dir.startswith("d:"), frozen_dir

    mutants = {}
    for mid in ("x11-owntree-short-guard", "x13-basename-blind", "x15-unknown-class-free",
                "x17-localpolicy-disk-blind", "x19-token-on-line-free", "x20-duplicate-ledger-free"):
        mutants[mid] = load(os.path.join(SEAT, "mutants", mid + ".py"), "mut_" + mid)
    joint = os.path.join(SCRATCH, "joint-x11-x13.py")
    src = open(COUNTER, encoding="utf-8").read()
    doc = json.load(open(os.path.join(SEAT, "c1-mutants-ext.json"), encoding="utf-8"))
    edits = {m["id"]: (m["old"], m["new"]) for m in doc["members"]}
    text = src
    for mid in ("x11-owntree-short-guard", "x13-basename-blind"):
        old, new = edits[mid]
        assert text.count(old) == 1, mid
        text = text.replace(old, new)
    with open(joint, "w", encoding="utf-8") as f:
        f.write(text)
    joint_mod = load(joint, "joint_counter")

    def rows():
        yield ("x11+x13 joint: directory token one component below its round -> byte-equal wave dir",
               ("PB1", "SCORECARD.md", "3", ".ufo/waves/round-32/a2w1", frozen_dir), "MOVED",
               ".ufo/waves/round-32/w2", ["", "", "moved .ufo/waves/round-32/a2w1 elsewhere"])
        yield ("x15: an unknown ledger class for an item absent at rev and on disk",
               ("PB2", "SCORECARD.md", "2", "corpus/knowledge/absentdir", "-"), "RENAMED", "-",
               ["", "x corpus/knowledge/absentdir y"])
        yield ("x17: LOCAL-POLICY with frozen bytes whose lane-disk listing changed",
               ("PB3", "SKILL.md", "2", ".ufo/quarantine",
                "d:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"), "LOCAL-POLICY", "-",
               ["", "quarantine root .ufo/quarantine"])
        yield ("x19: item whose token is NOT on its recorded base line",
               ("PB4", "LOG.md", "2", "corpus/x", "-"), "ABSENT", "-", ["", "no token on this line"])
    for note, item, cls, target, blob in rows():
        line = int(item[2])
        if not (0 < line <= len(blob) and item[3] in blob[line - 1]):
            blob = blob[:line - 1] + ["(token deliberately absent)"] + blob[line:]
        item = (item[0], item[1], str(line), item[3], item[4])
        st = base.judge(repo, rev, "/home/vgpnk/Projects/shokunin", item, (cls, target), blob)
        outs = {}
        for mid in ("x11-owntree-short-guard", "x13-basename-blind", "x15-unknown-class-free",
                    "x17-localpolicy-disk-blind", "x19-token-on-line-free"):
            outs[mid] = mutants[mid].judge(repo, rev, "/home/vgpnk/Projects/shokunin", item, (cls, target), blob)[0]
        jt = joint_mod.judge(repo, rev, "/home/vgpnk/Projects/shokunin", item, (cls, target), blob)[0]
        print(f"PROBE pristine={st[0]}({st[1][:40]}) " +
              " ".join(f"{k}={v}" for k, v in outs.items()) + f" joint_x11_x13={jt} note={note}")

    # x20: the duplicate-ledger refusal is in _ledger, not judge: hand both counters the same duplicate ledger.
    bad_ledger = os.path.join(SCRATCH, "probe-dupe-ledger.tsv")
    with open(bad_ledger, "w", encoding="utf-8") as f:
        f.write("P01\tFLEET\t-\tfirst\nP01\tFLEET\t-\tduplicate id\nP02\tABSENT\t-\tok\n")
    pl, pbad = base._ledger(bad_ledger)
    ml, mbad = mutants["x20-duplicate-ledger-free"]._ledger(bad_ledger)
    print(f"PROBE-LEXER pristine_bad={pbad} pristine_ids={sorted(pl)} "
          f"x20_bad={mbad} x20_ids={sorted(ml)} would_kill=yes_if_the_harness_could_carry_a_ledger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
