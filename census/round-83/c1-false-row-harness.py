#!/usr/bin/env python3
"""souji r83 C1 counter: how many false ledger rows a pointer-resolution counter accepts and how many true rows it
refuses, over the frozen r83 population census/round-83/c1-false-rows.tsv (pinned by sha256 below).

r83 changes (r82 routed defect 1/2, lesson round-82.md `## Routed to round 83`, plans/round-83.md): the population
is the r82 population (32 rows, columns unchanged, R1-R5 rebuilt byte-for-byte) plus four MOVED rows judged at the
new fixture revision R6, all using the r77 population item P04 whose token is `.ufo/waves/round-32/a2w1/...`
(an own-round-tree token — the class the r82 rule refuses): TF6 and TF7 are TRUE rows (byte-equal copies in the
lane's real wave-directory shapes `w2/` and `w1/`, which the r82 `CAPTURE` does not name and therefore refuses);
NF-J (a duplicated middle directory under a real `w1/`) and NF-K (a flattened copy at the round-tree root) must
stay REFUSED. A true row (expected got = a resolving class)
that the counter refuses is counted in refused_true; `accepted` counts only rows whose expectation is
non-resolving.

Successor of census/round-82/c1-false-row-harness.py (frozen and unchanged). r82 text follows: how many false
ledger rows a pointer-resolution counter accepts and how many true rows it
refuses, over the frozen r82 population census/round-82/c1-false-rows.tsv (pinned by sha256 below). Successor of
census/round-81/c1-false-row-harness.py (frozen and unchanged). The r82 population is the r81 population (25 rows,
columns unchanged, R1-R4 rebuilt byte-for-byte, fixture rev HEAD = R4 renamed R5 below) plus seven MOVED rows: NF-F and
NF-G (S81MutCounter NF-F/NF-G: a byte-equal decoy inside the token's own round tree under .ufo/waves/round-32/, accepted
by every r79-r81 counter), NF-H (the M8 killer: a non-wave directory under census/round-32/records/), NF-I and PF-1
(partial-suffix instances of the r81 stated limit) and TRUE rows TF4 and TF5 that any binding rule must keep (TF4 a
true capture in the token's own round tree; TF5 a true records/wave-<w>/ capture). A true row (expected got = a
resolving class) that the counter refuses is counted in refused_true; `accepted` counts only rows whose expectation
is non-resolving.

Successor of census/round-80/c1-false-row-harness.py (frozen and unchanged). r81 changes: the population is the r80
population (18 rows, columns unchanged, R1-R3 rebuilt byte-for-byte) plus seven MOVED rows judged at a new fixture
revision R4 (or, for TF3, at BASE): NF12 (the r80 wave's S80MutCounter decoy census/round-32/decoy/, accepted by
the r80 counter), NF12b (its census-archive/ sibling, refused by the r80 counter: the M05 detector), NF12c and
NF12d (decoys inside census/round-32/ built this round: waves/decoy/ and records/), and three TRUE rows that any
binding rule must keep: TF1 a flattened capture census/round-32/waves/SwarmExecutor08.md, TF2 a records/wave-a2w1/
capture, TF3 the real r77 ledger row P04 at BASE. A true row (expected got = a resolving class) that the counter
refuses is counted in refused_true; `accepted` counts only rows whose expectation is non-resolving.
  rev=R4    R3 + byte-equal copies of census/round-32/waves/a2w1/SwarmExecutor08.md at census/round-32/decoy/,
            census-archive/round-32/decoy/, census/round-32/waves/decoy/, census/round-32/records/,
            census/round-32/waves/ and census/round-32/records/wave-a2w1/
Output: `ROW ...` per row, then `SUMMARY rows=<N> mismatches=<M> accepted=<A> refused_true=<T> errors=<E>`.
r80 text follows:
souji r80 C1 counter: how many false ledger rows a pointer-resolution counter accepts, over the frozen r80
population census/round-80/c1-false-rows.tsv.

Successor of census/round-79/c2-false-row-harness.py (frozen and unchanged). The population is the r79 population
(9 rows, byte-equal columns, plus a rev column) and the r79 wave's non-author attack on the r79 counter
(census/round-79/records/wave-w1/seats/S79MutCounter.md, fixture.txt, probes.txt): the three false ledger rows the
r79 counter accepts (NF6b a QUARANTINED declaration whose token and target match only as substrings of other
paths; NF8 a `..` range member that is a directory; NF10 a MOVED target that is a byte-equal copy in an unrelated
subtree of the same round number) and the six detector rows that seat used to kill the r79 counter's surviving
mutants (DM01 M01, DM07 M07, DM11 M11, NF6c M09, NF6d M12, NF6e M13; each already refused by the r79 counter).

Each row is judged by running the counter under test (--counter) once, with a one-row forgery file, the row's
population and that population's frozen ledger:
  rev=BASE  --root <lane> --rev <BASE> (the r79 lane base, unchanged)
  rev=F0    --root <fixture> --rev <F0>: F0 is the r79 harness fixture commit, rebuilt byte-for-byte (same
            parent, files, identity and dates, so the same commit id 6436db6a...)
  rev=R1    F0 + census/round-73/records/c2-after-D3.txt replaced by a directory (D3.txt/inner.txt),
            c2-after-D9.txt kept, byte-equal copies of census/round-32/waves/a2w1/SwarmExecutor08.md at
            corpus/round-32/decoy/ and corpus/round-321/decoy/ (S79MutCounter REV1)
  rev=R2    R1 + corpus/lessons/round-79-collision.md (the other-stub.bak / .gitignore-p6repo line and the
            ghost-stub line) and a README.md note for readme-stub (S79MutCounter REV3 minus the late line)
  rev=R3    R2 + the late-stub declaration line appended to corpus/lessons/round-79-collision.md
            (fixture HEAD = R3, so a counter that greps HEAD instead of --rev finds it; NF6e is judged at R2)
  The fixture disk also carries a copy of the lane disk's .ufo/quarantine/ with NOT-THE-STUB, NOT-THE-L0 and the
  quarantine leaves other-stub, ghost-stub, readme-stub and late-stub added (untracked).
A row matches iff the counter's `FORGE <fid>` line reports got=<expect_got> and, when expect_rc is not '-', the
counter's exit code equals expect_rc. A row is ACCEPTED when got is a resolving class (anything but REFUSED,
MISMATCH, UNRESOLVED, ERROR).
Output: `ROW <id> where=<w> rev=<label> item=<i> class=<c> expect=<g>/<rc> got=<s> rc=<n> match=<yes|no>` per
row, then `SUMMARY rows=<N> mismatches=<M> accepted=<A> errors=<E>`. Exit 0 iff M == 0 and E == 0; 1 otherwise;
2 usage.
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
POP_PIN = "c9a6d58c1cf84a40a02a85a7342df2f2bd37301ba02e8f61ac91eded624e02eb"
P04_PIN = "d0693448c0895860ebe7ece2549d3f70f694247ddb717d1fa2c66a4518d5aa89"
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
    revs = {"F0": git(fx, "rev-parse", "HEAD")}
    # R1 (S79MutCounter REV1): D3.txt becomes a directory; byte-equal decoys in unrelated subtrees
    git(fx, "rm", "-q", "--", "census/round-73/records/c2-after-D3.txt")
    put("census/round-73/records/c2-after-D3.txt/inner.txt", b"r80 fixture: D3.txt is a directory here\n")
    with open(os.path.join(lane, "census/round-32/waves/a2w1/SwarmExecutor08.md"), "rb") as f:
        se = f.read()
    put("corpus/round-32/decoy/SwarmExecutor08.md", se)
    put("corpus/round-321/decoy/SwarmExecutor08.md", se)
    git(fx, "add", "-f", "--", "census/round-73/records/c2-after-D3.txt/inner.txt",
        "corpus/round-32/decoy/SwarmExecutor08.md", "corpus/round-321/decoy/SwarmExecutor08.md")
    git(fx, "commit", "-q", "--no-verify", "-m", "r80 C1 fixture R1 (S79MutCounter REV1)")
    revs["R1"] = git(fx, "rev-parse", "HEAD")
    # R2: substring collision and unbound slot in an authority file; a declaration outside AUTHORITY
    q6 = ".ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/"
    coll = ("# fixture lesson (r80 C1, S79MutCounter REV3)\n\n"
            f"- quarantined `{q6}other-stub.bak` (the pre-r17 copy) -- pointer "
            "`tests/vault/vadv54-run/p/p6repo/.gitignore-p6repo` retargeted there.\n"
            f"- quarantine slot {q6}ghost-stub left unbound (no pointer recorded).\n")
    put("corpus/lessons/round-79-collision.md", coll.encode())
    with open(os.path.join(fx, "README.md"), "ab") as f:
        f.write(f"\n- readme note: {q6}readme-stub for tests/vault/vadv54-run/p/p6repo/.git\n".encode())
    git(fx, "add", "-f", "--", "corpus/lessons/round-79-collision.md", "README.md")
    git(fx, "commit", "-q", "--no-verify", "-m", "r80 C1 fixture R2")
    revs["R2"] = git(fx, "rev-parse", "HEAD")
    # R3: a late declaration (judged at R2 by NF6e)
    with open(os.path.join(fx, "corpus/lessons/round-79-collision.md"), "ab") as f:
        f.write(f"- late declaration: {q6}late-stub for tests/vault/vadv54-run/p/p6repo/.git\n".encode())
    git(fx, "add", "-f", "--", "corpus/lessons/round-79-collision.md")
    git(fx, "commit", "-q", "--no-verify", "-m", "r80 C1 fixture R3")
    revs["R3"] = git(fx, "rev-parse", "HEAD")
    # R4 (r81): decoys and true captures of SwarmExecutor08.md inside and beside the capture root
    for rel in ("census/round-32/decoy/", "census-archive/round-32/decoy/", "census/round-32/waves/decoy/",
                "census/round-32/records/", "census/round-32/waves/", "census/round-32/records/wave-a2w1/"):
        put(rel + "SwarmExecutor08.md", se)
    git(fx, "add", "-f", "--", "census/round-32/decoy", "census-archive/round-32/decoy",
        "census/round-32/waves/decoy", "census/round-32/records/SwarmExecutor08.md",
        "census/round-32/waves/SwarmExecutor08.md", "census/round-32/records/wave-a2w1")
    git(fx, "commit", "-q", "--no-verify", "-m", "r81 C1 fixture R4")
    revs["R4"] = git(fx, "rev-parse", "HEAD")
    # R5 (r82): S81MutCounter new-row fixture copies (byte-equal SwarmExecutor08.md) + the P07 byte source
    with open(os.path.join(lane, ".ufo/waves/round-61/w1/S61ExecRealRecord/erratum-evidence.txt"), "rb") as f:
        p7 = f.read()
    for rel in (".ufo/waves/round-32/decoy/", ".ufo/waves/round-32/decoy/deeper/",
                "census/round-32/records/decoy/", "census/round-32/records/decoy/a2w1/",
                "census/round-32/waves/a2w1/a2w1/", "census/round-32/wave/", "census/round-32/records/wave-9/",
                ".ufo/waves/round-32/waves/a2w1/", "census/round-32/records/wave-a2w1/"):
        put(rel + "SwarmExecutor08.md", se)
    put("census/round-61/wave/S61ExecRealRecord/erratum-evidence.txt", p7)
    git(fx, "add", "-f", "--", ".ufo/waves/round-32/decoy", "census/round-32/records/decoy",
        "census/round-32/waves/a2w1/a2w1", "census/round-32/wave", "census/round-32/records/wave-9",
        ".ufo/waves/round-32/waves/a2w1", "census/round-61/wave")
    git(fx, "commit", "-q", "--no-verify", "-m", "r82 C1 fixture R5 (S81MutCounter newrows repl)")
    revs["R5"] = git(fx, "rev-parse", "HEAD")
    # R6 (r83): own-round-tree targets for the r77 population item P04, whose token
    # `.ufo/waves/round-32/a2w1/SwarmExecutor08.md` is absent at BASE. The lane's real wave directories are
    # w1/, w2/, w3/ and a2w1/ (census/round-83/records/wave-dirs.txt); w2/ and w1/ are TRUE rows, a duplicated
    # middle dir under w1/ and a flattened copy at the round-tree root stay REFUSED.
    if hashlib.sha256(se).hexdigest() != P04_PIN:
        raise FixtureError(f"P04 byte source sha256 {hashlib.sha256(se).hexdigest()} is not the frozen {P04_PIN}")
    for rel in (".ufo/waves/round-32/w2/", ".ufo/waves/round-32/w1/", ".ufo/waves/round-32/w1/a2w1/",
                ".ufo/waves/round-32/"):
        put(rel + "SwarmExecutor08.md", se)
    git(fx, "add", "-f", "--", ".ufo/waves/round-32")
    git(fx, "commit", "-q", "--no-verify", "-m", "r83 C1 fixture R6 (own-tree real shapes)")
    revs["R6"] = git(fx, "rev-parse", "HEAD")
    q = os.path.join(lane, ".ufo/quarantine")
    if not os.path.isdir(q):
        raise FixtureError("lane disk lacks .ufo/quarantine")
    shutil.copytree(q, os.path.join(fx, ".ufo/quarantine"), symlinks=True)
    put(".ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/NOT-THE-STUB", b"not the stub\n")
    put(".ufo/quarantine/round-17/.ufo/NOT-THE-L0", b"not the L0 file\n")
    for leaf in ("other-stub", "ghost-stub", "readme-stub", "late-stub"):
        put(".ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/" + leaf, f"r80 fixture {leaf}\n".encode())
    return fx, revs


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True, help="pointer-resolution counter under test")
    ap.add_argument("--lane", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--work", required=True, help="empty scratch dir (never under /tmp)")
    ns = ap.parse_args(argv)
    lane, fleet, work = (os.path.abspath(x) for x in (ns.lane, ns.fleet_root, ns.work))
    counter = os.path.abspath(ns.counter)
    pop = os.path.join(HERE, "c1-false-rows.tsv")
    if sha(pop) != POP_PIN:
        print(f"C1-HARNESS-FATAL: population sha256 {sha(pop)} is not the pinned {POP_PIN}", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C1-HARNESS-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C1-HARNESS-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    with open(pop, encoding="utf-8") as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    if len(rows) != 36 or any(len(r) != 10 for r in rows) or len({r[0] for r in rows}) != 36 \
            or any(r[2] not in ("BASE", "F0", "R1", "R2", "R3", "R5", "R6") for r in rows):
        print("C1-HARNESS-FATAL: population is not 36 well-formed rows", file=sys.stderr)
        return 2
    print(f"# harness sha256={sha(os.path.abspath(__file__))} base={BASE}")
    print(f"# population path={pop} sha256={sha(pop)}")
    print(f"# counter path={counter} sha256={sha(counter)}")
    try:
        fx, revs = build_fixture(lane, work)
    except (FixtureError, OSError, subprocess.SubprocessError) as exc:
        print(f"C1-HARNESS-FATAL: fixture: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print("# fixture " + " ".join(f"{k}={v}" for k, v in revs.items()))
    mism = acc = reft = errs = 0
    for rid, where, rlabel, popl, item, cls, target, exp_got, exp_rc, _src in rows:
        if (where == "lane") != (rlabel == "BASE"):
            print("C1-HARNESS-FATAL: lane rows are judged at BASE and fixture rows at a fixture rev", file=sys.stderr)
            return 2
        root, rev = (lane, BASE) if where == "lane" else (fx, revs[rlabel])
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
            print(f"ROW {rid} where={where} rev={rlabel} item={item} class={cls} expect={exp_got}/{exp_rc} got=- "
                  f"rc={p.returncode} match=error detail={p.stderr.decode()[:200]!r}")
            continue
        got = m.group(1)
        ok = got == exp_got and (exp_rc == "-" or p.returncode == int(exp_rc))
        if exp_got in RESOLVING_NOT:
            acc += got not in RESOLVING_NOT
        else:
            reft += got in RESOLVING_NOT
        mism += 0 if ok else 1
        print(f"ROW {rid} where={where} rev={rlabel} item={item} class={cls} expect={exp_got}/{exp_rc} got={got} "
              f"rc={p.returncode} match={'yes' if ok else 'no'}")
    print(f"SUMMARY rows={len(rows)} mismatches={mism} accepted={acc} refused_true={reft} errors={errs}")
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
