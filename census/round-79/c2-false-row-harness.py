#!/usr/bin/env python3
"""souji r79 C2 counter: how many false ledger rows a pointer-resolution counter accepts, over the frozen r79
population census/round-79/c2-false-rows.tsv (pinned by sha256 below).

The population is the r78 wave's non-author attack on the r78 counter (census/round-78/records/wave-w1/seats/
S78MutCounter.md, false-rows.tsv and repro.txt): the five false ledger rows NF1-NF5 the r78 counter accepts,
and the four detector rows FP2, FP8, LP2, LP3 that seat used to kill the r78 mutants M02, M04, M07 and M09 (each
already refused by the r78 counter; they keep a counter that loosens those rules from scoring as a gain).

Each row is judged by running the counter under test (--counter) once, with a one-row forgery file, the row's
population and that population's frozen ledger:
  where=lane     --root <lane> --rev <BASE>   (the r79 lane base below)
  where=fixture  --root <fixture> --rev <fixture commit>: a `git clone --shared` of the lane at BASE, plus the
                 S78MutCounter repro step 6 files committed in the fixture (byte-equal renamed copy of
                 census/round-32/waves/a2w1/SwarmExecutor08.md; census/round-73/records/c2-after-D9.txt;
                 census/round-49/sources/s272-python-open-l; census/round-02/operator-sweep-20261019 copied from
                 the lane disk's census/operator-sweep-20261019) and, on the fixture disk only, a copy of the
                 lane disk's .ufo/quarantine/ with .../p6repo/NOT-THE-STUB and .ufo/quarantine/round-17/.ufo/
                 NOT-THE-L0 added.
A row matches iff the counter's `FORGE <fid>` line reports got=<expect_got> and, when expect_rc is not '-', the
counter's exit code equals expect_rc (LP3: an expect=MISMATCH row the counter refuses must fail the run).
A row is ACCEPTED when got is a resolving class (anything but REFUSED, MISMATCH, UNRESOLVED, ERROR).
Output: `ROW <id> where=<w> item=<i> class=<c> expect=<g>/<rc> got=<s> rc=<n> match=<yes|no>` per row, then
`SUMMARY rows=<N> mismatches=<M> accepted=<A> errors=<E>`. Exit 0 iff M == 0 and E == 0; 1 otherwise; 2 usage.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "e65538e73c7f1a8f7570bc24a2215da8a90043f3"
POP_PIN = "7c108820a47467507e52af38f960726c032dba68dba818708730f7d2f826afdb"
POPS = {"r77": ("census/round-77/c2-population.tsv", "census/round-77/c2-pointer-ledger.tsv"),
        "r78": ("census/round-78/c2-population.tsv", "census/round-78/c2-pointer-ledger.tsv")}
RESOLVING_NOT = ("REFUSED", "MISMATCH", "UNRESOLVED", "ERROR")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r79 fixture", "GIT_AUTHOR_EMAIL": "fixture@r79.invalid",
            "GIT_COMMITTER_NAME": "r79 fixture", "GIT_COMMITTER_EMAIL": "fixture@r79.invalid",
            "GIT_AUTHOR_DATE": "2026-11-07T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-07T00:00:00Z"})


class FixtureError(Exception):
    pass


def git(repo, *args):
    if not repo or not os.path.isabs(repo):
        raise FixtureError(f"refusing git -C with {repo!r}")
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise FixtureError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.decode()[:200]}")
    return p.stdout.decode().strip()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def build_fixture(lane, work):
    fx = os.path.join(work, "fixture")
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", lane, fx], check=True, env=ENV,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if os.path.realpath(git(fx, "rev-parse", "--show-toplevel")) != os.path.realpath(fx):
        raise FixtureError("fixture toplevel is not the fixture dir")
    git(fx, "checkout", "-q", "--detach", BASE)

    def put(rel, data):
        p = os.path.join(fx, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    with open(os.path.join(lane, "census/round-32/waves/a2w1/SwarmExecutor08.md"), "rb") as f:
        put("census/round-32/waves/a2w1/renamed-SwarmExecutor08.md", f.read())
    put("census/round-73/records/c2-after-D9.txt", b"r79 fixture: outside the D1..D5 span\n")
    put("census/round-49/sources/s272-python-open-l", b"r79 fixture: one-character continuation\n")
    sweep = os.path.join(lane, "census/operator-sweep-20261019")
    if not os.path.isdir(sweep):
        raise FixtureError("lane disk lacks census/operator-sweep-20261019")
    shutil.copytree(sweep, os.path.join(fx, "census/round-02/operator-sweep-20261019"), symlinks=True)
    git(fx, "add", "-f", "--", "census/round-32/waves/a2w1/renamed-SwarmExecutor08.md",
        "census/round-73/records/c2-after-D9.txt", "census/round-49/sources/s272-python-open-l",
        "census/round-02/operator-sweep-20261019")
    git(fx, "commit", "-q", "--no-verify", "-m", "r79 C2 fixture (S78MutCounter repro step 6)")
    rev = git(fx, "rev-parse", "HEAD")
    q = os.path.join(lane, ".ufo/quarantine")
    if not os.path.isdir(q):
        raise FixtureError("lane disk lacks .ufo/quarantine")
    shutil.copytree(q, os.path.join(fx, ".ufo/quarantine"), symlinks=True)
    put(".ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/NOT-THE-STUB", b"not the stub\n")
    put(".ufo/quarantine/round-17/.ufo/NOT-THE-L0", b"not the L0 file\n")
    return fx, rev


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True, help="pointer-resolution counter under test")
    ap.add_argument("--lane", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--work", required=True, help="empty scratch dir (never under /tmp)")
    ns = ap.parse_args(argv)
    lane, fleet, work = (os.path.abspath(x) for x in (ns.lane, ns.fleet_root, ns.work))
    counter = os.path.abspath(ns.counter)
    pop = os.path.join(HERE, "c2-false-rows.tsv")
    if sha(pop) != POP_PIN:
        print(f"C2-HARNESS-FATAL: population sha256 {sha(pop)} is not the pinned {POP_PIN}", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C2-HARNESS-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C2-HARNESS-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    with open(pop, encoding="utf-8") as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    if len(rows) != 9 or any(len(r) != 9 for r in rows) or len({r[0] for r in rows}) != 9:
        print("C2-HARNESS-FATAL: population is not 9 well-formed rows", file=sys.stderr)
        return 2
    print(f"# harness sha256={sha(os.path.abspath(__file__))} base={BASE}")
    print(f"# population path={pop} sha256={sha(pop)}")
    print(f"# counter path={counter} sha256={sha(counter)}")
    try:
        fx, fxrev = build_fixture(lane, work)
    except (FixtureError, OSError, subprocess.SubprocessError) as exc:
        print(f"C2-HARNESS-FATAL: fixture: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(f"# fixture rev={fxrev}")
    mism = acc = errs = 0
    for rid, where, popl, item, cls, target, exp_got, exp_rc, _src in rows:
        root, rev = (lane, BASE) if where == "lane" else (fx, fxrev)
        pfile, lfile = POPS[popl]
        forge = os.path.join(work, f"forge-{rid}.tsv")
        with open(forge, "w", encoding="utf-8") as f:
            f.write(f"{rid}\t{item}\t{cls}\t{target}\t{'MISMATCH' if exp_rc != '-' else 'REFUSED'}\n")
        p = subprocess.run([sys.executable, "-B", counter, "--root", root, "--rev", rev, "--fleet-root", fleet,
                            "--population", os.path.join(lane, pfile), "--ledger", os.path.join(lane, lfile),
                            "--forge", forge], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=lane)
        out = p.stdout.decode("utf-8", "replace")
        m = re.search(rf"^FORGE {re.escape(rid)} item={re.escape(item)} .*?got=(\S+)", out, re.M)
        if not m:
            errs += 1
            print(f"ROW {rid} where={where} item={item} class={cls} expect={exp_got}/{exp_rc} got=- "
                  f"rc={p.returncode} match=error detail={p.stderr.decode()[:200]!r}")
            continue
        got = m.group(1)
        ok = got == exp_got and (exp_rc == "-" or p.returncode == int(exp_rc))
        acc += got not in RESOLVING_NOT
        mism += 0 if ok else 1
        print(f"ROW {rid} where={where} item={item} class={cls} expect={exp_got}/{exp_rc} got={got} "
              f"rc={p.returncode} match={'yes' if ok else 'no'}")
    print(f"SUMMARY rows={len(rows)} mismatches={mism} accepted={acc} errors={errs}")
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
