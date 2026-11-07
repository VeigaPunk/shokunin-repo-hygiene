#!/usr/bin/env python3
"""souji r77 C2 counter: every evidence pointer the lane's self-assessment files make that
tools/souji-pointer-check.py reports MISSING at the base (35 findings over SCORECARD.md, SKILL.md,
corpus/QUALITY.md, corpus/README.md, PROVINCE.md; SHONEN.md has none) must resolve at the measured revision
to bytes whose location and identity the counter verifies itself, or stays UNRESOLVED.

Population: census/round-77/c2-population.tsv (frozen; one row per base finding: id, file, line, token,
frozen digest of the bytes the lane disk held at the token path when the population was frozen, or `-`).
Ledger (the claimed work, optional): TSV rows `id <TAB> class <TAB> target <TAB> note`.

Resolution rules (per item; first rule that applies decides; nothing else resolves an item):
  R0  integrity: the base blob of <file> carries <token> on <line>; else the item is an ERROR.
  R1  CAPTURED   the token path exists at --rev and the digest of its bytes there equals the frozen digest.
                 An item with no frozen digest is never resolved by a path appearing at --rev (it was
                 stated as absent or non-lane), and an unequal digest is a MISMATCH (stub capture).
  Ledger classes (an item already CAPTURED ignores its ledger row):
  MOVED <path>   frozen digest present; <path> exists at --rev with the same digest.
  LOCAL-POLICY   frozen digest present; the token sits under a frozen policy-local prefix
                 (.ufo/quarantine, census/operator-sweep-) and the lane disk still holds equal bytes.
  QUARANTINED <path>  no frozen digest; token absent at --rev and on the lane disk; <path> sits under
                 .ufo/quarantine/ on the lane disk.
  FLEET          no frozen digest; token absent at --rev and on the lane disk; it starts with `.ufo/` and
                 exists under --fleet-root (runtime the lane never owns).
  TOKEN <t;t>    no frozen digest; the token carries a parse artefact (trailing `>`, `\\` or `-`, or `..`
                 inside its last component); every target exists (at --rev, or under --fleet-root when
                 written `fleet:<path>`) and continues the token (trailing artefact: target starts with
                 the stripped token; `..`: same directory, same stem before the digits and same suffix).
  ABSENT         no frozen digest; no parse artefact (those are TOKEN items); token absent at --rev, on
                 the lane disk, under --fleet-root and in every lane ref's history (`git log --all --
                 <token>` empty).
  A ledger row whose rule fails, an unknown id or class, or a duplicate id is a REFUSED item.

Output: one `ITEM <id> <file>:<line> status=<CAPTURED|MOVED|...|UNRESOLVED|REFUSED|MISMATCH|ERROR>
[why=...]` line per item, then `SUMMARY items=<N> resolved=<R> unresolved=<U> refused=<F> mismatched=<M>
errors=<E>`; exit 0 iff resolved == N, 1 otherwise, 2 on usage.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "d4f515637884695b3aa016da169d859d3ece6ac4"
POLICY_LOCAL = (".ufo/quarantine", "census/operator-sweep-")
CLASSES = ("MOVED", "LOCAL-POLICY", "QUARANTINED", "FLEET", "TOKEN", "ABSENT")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_OPTIONAL_LOCKS": "0"})


def git(root, *args, check=True):
    p = subprocess.run(["git", "-C", root, "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
                        *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}")
    return p


def _listing_digest(entries):
    h = hashlib.sha256()
    for rel, kind, digest in sorted(entries):
        h.update(rel + b"\0" + kind + b"\0" + digest.encode() + b"\n")
    return h.hexdigest()


def disk_digest(path):
    """f:<sha256> for a regular file, d:<listing sha256> for a directory (files and symlinks below it),
    l:<sha256 of target> for a symlink, None when absent."""
    if os.path.islink(path):
        return "l:" + hashlib.sha256(os.fsencode(os.readlink(path))).hexdigest()
    if os.path.isfile(path):
        with open(path, "rb") as f:
            return "f:" + hashlib.sha256(f.read()).hexdigest()
    if os.path.isdir(path):
        ent = []
        for dp, dns, fns in os.walk(path):
            for n in fns + [d for d in dns if os.path.islink(os.path.join(dp, d))]:
                p = os.path.join(dp, n)
                rel = os.fsencode(os.path.relpath(p, path))
                if os.path.islink(p):
                    ent.append((rel, b"l", hashlib.sha256(os.fsencode(os.readlink(p))).hexdigest()))
                elif os.path.isfile(p):
                    with open(p, "rb") as f:
                        ent.append((rel, b"f", hashlib.sha256(f.read()).hexdigest()))
                else:
                    ent.append((rel, b"x", "-"))
        return "d:" + _listing_digest(ent)
    if os.path.lexists(path):
        return "x:-"
    return None


def rev_digest(root, rev, path):
    """Same digest shape for <path> at <rev>, None when absent."""
    t = git(root, "cat-file", "-t", f"{rev}:{path}", check=False)
    if t.returncode != 0:
        return None
    kind = t.stdout.strip()
    if kind == b"blob":
        mode = git(root, "ls-tree", "-z", rev, "--", path).stdout.split(b" ", 1)[0]
        data = git(root, "cat-file", "blob", f"{rev}:{path}").stdout
        return ("l:" if mode == b"120000" else "f:") + hashlib.sha256(data).hexdigest()
    if kind == b"tree":
        out = git(root, "ls-tree", "-r", "-z", f"{rev}:{path}").stdout
        ent = []
        for rec in out.split(b"\0"):
            if not rec:
                continue
            meta, rel = rec.split(b"\t", 1)
            mode, typ, oid = meta.split(b" ")
            if typ != b"blob":
                ent.append((rel, b"x", "-"))
                continue
            data = git(root, "cat-file", "blob", oid.decode()).stdout
            ent.append((rel, b"l" if mode == b"120000" else b"f", hashlib.sha256(data).hexdigest()))
        return "d:" + _listing_digest(ent)
    return "x:-"


def token_ok(root, rev, fleet, token, targets):
    last = token.rsplit("/", 1)[-1]
    trailing = token[-1] in ">\\-"
    dots = ".." in last
    if not (trailing or dots) or not targets:
        return "no parse artefact" if not (trailing or dots) else "no target"
    for t in targets:
        if t.startswith("fleet:"):
            t = t[len("fleet:"):]
            if not os.path.lexists(os.path.join(fleet, t)):
                return f"target absent under fleet root: {t}"
        elif rev_digest(root, rev, t) is None:
            return f"target absent at rev: {t}"
        if trailing:
            stem = token.rstrip(">\\")
            if not t.startswith(stem):
                return f"target does not continue the token: {t}"
        else:
            d, b = os.path.split(t)
            pre, suf = last.split("..", 1)
            stem = pre.rstrip("0123456789")
            m = re.match(r"^[A-Za-z_-]*[0-9]+(.*)$", suf)
            if not m or not stem or stem == pre:
                return "range endpoints carry no digits"
            sfx = m.group(1)
            mid = b[len(stem):len(b) - len(sfx)] if sfx else b[len(stem):]
            if (d != os.path.dirname(token) or not b.startswith(stem) or not b.endswith(sfx)
                    or not mid.isdigit()):
                return f"target is not an expansion of the range: {t}"
    return ""


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--ledger", help="ledger TSV (absent = no ledger)")
    ns = ap.parse_args(argv)
    root, fleet = os.path.abspath(ns.root), os.path.abspath(ns.fleet_root)
    rv = git(root, "rev-parse", "--verify", ns.rev + "^{commit}", check=False)
    if rv.returncode != 0:
        print("C2-COUNTER-FATAL: --rev does not name a commit", file=sys.stderr)
        return 2
    rev = rv.stdout.decode().strip()
    pop_path = os.path.join(HERE, "c2-population.tsv")
    with open(pop_path, encoding="utf-8") as f:
        pop = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    if len(pop) != 35 or len({r[0] for r in pop}) != 35 or any(len(r) != 5 for r in pop):
        print("C2-COUNTER-FATAL: population is not 35 well-formed rows", file=sys.stderr)
        return 2
    ledger, bad_ledger = {}, []
    if ns.ledger:
        with open(ns.ledger, encoding="utf-8") as f:
            for l in f:
                if not l.strip() or l.startswith("#"):
                    continue
                r = l.rstrip("\n").split("\t")
                if len(r) < 3 or r[0] in ledger:
                    bad_ledger.append(r[0] if r else "?")
                    continue
                ledger[r[0]] = (r[1], r[2])
    me = os.path.abspath(__file__)
    with open(me, "rb") as f:
        print(f"# counter sha256={hashlib.sha256(f.read()).hexdigest()} base={BASE} rev={rev}")
    with open(pop_path, "rb") as f:
        print(f"# population sha256={hashlib.sha256(f.read()).hexdigest()}")
    if ns.ledger:
        with open(ns.ledger, "rb") as f:
            print(f"# ledger path={ns.ledger} sha256={hashlib.sha256(f.read()).hexdigest()}")
    else:
        print("# ledger none")
    ids = {r[0] for r in pop}
    unknown = sorted(set(ledger) - ids) + bad_ledger
    counts = dict(resolved=0, unresolved=0, refused=0, mismatched=0, errors=0)
    for iid, file, line, token, frozen in pop:
        frozen = None if frozen == "-" else frozen
        where = f"{file}:{line}"
        blob = git(root, "show", f"{BASE}:{file}", check=False).stdout.decode("utf-8", "replace").split("\n")
        if not (line.isdigit() and 0 < int(line) <= len(blob) and token in blob[int(line) - 1]):
            counts["errors"] += 1
            print(f"ITEM {iid} {where} status=ERROR why=token not on the base line")
            continue
        at_rev = rev_digest(root, rev, token)
        if at_rev is not None:
            if frozen is not None and at_rev == frozen:
                counts["resolved"] += 1
                print(f"ITEM {iid} {where} status=CAPTURED")
            else:
                counts["mismatched"] += 1
                why = "no frozen bytes (stated absent or non-lane)" if frozen is None else "digest differs"
                print(f"ITEM {iid} {where} status=MISMATCH why={why}")
            continue
        if iid not in ledger:
            counts["unresolved"] += 1
            print(f"ITEM {iid} {where} status=UNRESOLVED")
            continue
        cls, target = ledger[iid]
        on_disk = disk_digest(os.path.join(root, token))
        why = ""
        if cls not in CLASSES:
            why = f"unknown class {cls}"
        elif cls == "MOVED":
            if frozen is None:
                why = "no frozen bytes to move"
            elif rev_digest(root, rev, target) != frozen:
                why = "target absent at rev or digest differs"
        elif cls == "LOCAL-POLICY":
            if frozen is None:
                why = "no frozen bytes"
            elif not token.startswith(POLICY_LOCAL):
                why = "not under a policy-local prefix"
            elif on_disk != frozen:
                why = "lane disk bytes absent or changed"
        elif frozen is not None:
            why = f"{cls} refused: the lane disk held bytes at the token path at freeze"
        elif on_disk is not None:
            why = f"{cls} refused: the lane disk holds the token path"
        elif cls == "QUARANTINED":
            if not target.startswith(".ufo/quarantine/") or not os.path.lexists(os.path.join(root, target)):
                why = "quarantine target absent on the lane disk"
        elif cls == "FLEET":
            if not token.startswith(".ufo/") or not os.path.lexists(os.path.join(fleet, token)):
                why = "not under the fleet root"
        elif cls == "TOKEN":
            why = token_ok(root, rev, fleet, token, [t for t in target.split(";") if t])
        elif cls == "ABSENT":
            if token[-1] in ">\\-" or ".." in token.rsplit("/", 1)[-1]:
                why = "token carries a parse artefact (TOKEN, not ABSENT)"
            elif os.path.lexists(os.path.join(fleet, token)):
                why = "exists under the fleet root"
            elif git(root, "log", "--all", "--format=%H", "-1", "--", token).stdout.strip():
                why = "present in lane history"
        if why:
            counts["refused"] += 1
            print(f"ITEM {iid} {where} status=REFUSED class={cls} why={why}")
        else:
            counts["resolved"] += 1
            print(f"ITEM {iid} {where} status={cls}")
    for u in unknown:
        counts["refused"] += 1
        print(f"LEDGER-REFUSED id={u} why=unknown or duplicate id")
    print(f"SUMMARY items={len(pop)} resolved={counts['resolved']} unresolved={counts['unresolved']} "
          f"refused={counts['refused']} mismatched={counts['mismatched']} errors={counts['errors']}")
    return 0 if counts["resolved"] == len(pop) and not unknown else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
