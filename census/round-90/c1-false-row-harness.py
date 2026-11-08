#!/usr/bin/env python3
"""souji r90 C1 counter: the r89 harness plus ONE pinned population (census/round-90/c1-false-rows.tsv, 58 rows =
the r89 57 byte-for-byte plus LD2b at the `where=ledger` row type) and one mechanical extension. LD2b appends the
same 2-column malformed row under an id ABSENT from the frozen ledger (`ZZ9`), so the malformed guard `len(r) < 3`
is the only refusal left for it; the r89 LD2 row could not reach that guard because its id `P02` is already in the
ledger (r89 A1). No judgement code changed for lane/fixture rows; the counter under test
(census/round-87/c1-pointer-counter.py) is unchanged.

souji r89 C1 counter: the r88 harness plus ONE pinned population (census/round-89/c1-false-rows.tsv, 57 rows =
the r88 53 byte-for-byte plus NF6h/NF6i at fixture revision R12 and LD1b/LD2) and three mechanical extensions. NF6g needs R11,
a declaration that names the L06 token only as the suffix of a longer path (the `_whole` before-byte half), so R11
joins the accepted rev labels and the fixture builder. NF6h/NF6i need R12 (the slash predecessor + the twice-token line). LD1b/LD2 extend the `where=ledger` row TYPE: LD1b appends the same item with a different target, LD2 a 2-column malformed row. No judgement code changed for lane/fixture rows; the counter under test is unchanged.

souji r88 C1 counter: the r87 harness plus ONE pinned population (census/round-88/c1-false-rows.tsv, 53 rows =
the r87 51 byte-for-byte plus NF6g at fixture revision R11 and LD1) and two mechanical extensions. NF6g needs R11,
a declaration that names the L06 token only as the suffix of a longer path (the `_whole` before-byte half), so R11
joins the accepted rev labels and the fixture builder. LD1 is a new row TYPE: `where=ledger` appends a second row
for the named item to the population's frozen ledger and expects the counter's `LEDGER-REFUSED id=<item>` plus the
exit code in the row. No judgement code changed: the counter under test is unchanged.

souji r87 C1 counter: the r86 harness plus ONE pinned population (census/round-87/c1-false-rows.tsv, 51 rows =
the r86 49 byte-for-byte plus TQ1 and NE1) and one fixture revision R10 that carries TQ1's sentence-final
quarantine declaration (the quarantine leaf itself is written beside the other fixture leaves, disk-only). Two
mechanical extensions: the forged-expectation cell can carry ERROR (only NE1 uses it: the row expects the R0
diagnostic class) and R10 joins the accepted rev labels. No judgement code changed.

souji r84 C1 counter: how many false ledger rows a pointer-resolution counter accepts, over one of two pinned
populations (the r83 36-row population or the r84 44-row population that adds the eight clause-binding rows).

r84 changes (r83 lesson `## Measured`, SCORECARD `### Planned (r84)`): the r83 population left five clauses of the
pointer counter unbound (mutants m6 digest-blind, m7 round-blind, m8 w-only shapes, m9 basename-only, m10
records-as-wave all survived 36/36). The population is the r83 36 rows byte-for-byte (same order) plus TF8, TF9, TF10
(TRUE rows: a deep token kept under a real w2/, the a2w1/ and assimilation/ wave directories as real decisions) and
NF-P, NF-L, NF-L2, NF-M, NF-Q (false rows: the deep token flattened, a real w3/ copy with different bytes, a
byte-equal copy in another round's tree, a non-wave records/ dir under the own tree, a real wN/ prefix that drops the
token's suffix) at fixture revision R7. `--population` selects which pinned population is scored; the row count must
match its pin. Text follows.
souji r83 C1 counter: how many false ledger rows a pointer-resolution counter accepts and how many true rows it
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
POP_PINS = {"c9a6d58c1cf84a40a02a85a7342df2f2bd37301ba02e8f61ac91eded624e02eb": 36,
            "4795f009d6c873e733a2992bc86405d509dfb105b5f9950b3b9f82b2596e8f6f": 44,
            "1468236cfc3c8f65e7fa9bb07884324ee8ae8b7f62d6d5ca984b9dfa04698d42": 47,
            "79db70f6740de41a326dc4193bf80c5394fe126d636cc98d4e26e4b5e140f561": 49,
            "b066fa0fc686efdf96c8ebf21a32764070661796c3b4d6e5e99f8aad18669220": 51,
            "b710e368de862a72bc430610003d3cdf1499bea1b6e4ff2325417a1d388a68c3": 53,
            "04570a64855978bf697af71c161fe215945da5849f2f393fee15bb0d9f21e093": 57,
            "d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45": 58}
P04_PIN = "d0693448c0895860ebe7ece2549d3f70f694247ddb717d1fa2c66a4518d5aa89"
P07_PIN = "5212878dc0e8156e5cf27bd639a732a51d33473547b7e03ddf1a17ad6baddaaa"
# r86: the r83 counter's bytes are the NF-Y row's content source (a round-root token moved into a capture)
I86S_PIN = "052c4f3fdb3f902971b70f80653b4e84dc9a6b1c8deed355f067b3ff7d131d79"
POPS = {"r77": ("census/round-77/c2-population.tsv", "census/round-77/c2-pointer-ledger.tsv"),
        "r78": ("census/round-78/c2-population.tsv", "census/round-78/c2-pointer-ledger.tsv"),
        "r85": ("census/round-85/c1-items.tsv", "census/round-85/c1-ledger.tsv"),
        "r86": ("census/round-86/c1-items.tsv", "census/round-86/c1-ledger.tsv"),
        "r87": ("census/round-87/c1-items.tsv", "census/round-87/c1-ledger.tsv")}
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
    # R7 (r84): the clause-binding copies. P04's byte source lands in w3/ with DIFFERENT bytes (a digest-blind rule
    # accepts it), in another round's w2/ (a round-blind rule accepts it), in an own-tree records/ dir and under a
    # real w2/ with the suffix dropped (shape-only rules accept those). P07's deep token (two components below its
    # wave dir) lands byte-equal in w2/, in a2w1/ and in assimilation/ (TRUE), and flattened one component (FALSE).
    put(".ufo/waves/round-32/w3/SwarmExecutor08.md", b"r84 fixture: this copy differs from the frozen digest\n")
    for rel in (".ufo/waves/round-33/w2/SwarmExecutor08.md", ".ufo/waves/round-32/records/SwarmExecutor08.md",
                ".ufo/waves/round-32/w2/decoy/SwarmExecutor08.md"):
        put(rel, se)
    if hashlib.sha256(p7).hexdigest() != P07_PIN:
        raise FixtureError(f"P07 byte source sha256 {hashlib.sha256(p7).hexdigest()} is not the frozen {P07_PIN}")
    for rel in (".ufo/waves/round-61/w2/S61ExecRealRecord/erratum-evidence.txt",
                ".ufo/waves/round-61/w2/erratum-evidence.txt",
                ".ufo/waves/round-61/a2w1/S61ExecRealRecord/erratum-evidence.txt",
                ".ufo/waves/round-61/assimilation/S61ExecRealRecord/erratum-evidence.txt"):
        put(rel, p7)
    git(fx, "add", "-f", "--", ".ufo/waves/round-32/w3", ".ufo/waves/round-33/w2",
        ".ufo/waves/round-32/records", ".ufo/waves/round-32/w2/decoy", ".ufo/waves/round-61")
    git(fx, "commit", "-q", "--no-verify", "-m", "r84 C1 fixture R7 (clause-binding rows)")
    revs["R7"] = git(fx, "rev-parse", "HEAD")
    # R8 (r85): the census-token item. I85R's token `census/round-84/records/c1-after.txt` leaves the census round
    # tree and lands twice: in a real capture shape (waves/, the TRUE row TF11) and in a NON-capture shape
    # (records/copy/, the FALSE row NF-R, which only the census-in-tree clause refuses).
    with open(os.path.join(lane, "census/round-84/records/c1-after.txt"), "rb") as f:
        c1a = f.read()
    # The token path does not exist in this fixture (it is built from BASE, before round 84), so R8 only has to
    # place the two targets; the token is absent at R8 by construction.
    put("census/round-84/waves/c1-after.txt", c1a)
    put("census/round-84/records/copy/c1-after.txt", c1a)
    git(fx, "add", "-f", "--", "census/round-84/waves/c1-after.txt",
        "census/round-84/records/copy/c1-after.txt")
    git(fx, "commit", "-q", "--no-verify", "-m", "r85 C1 fixture R8 (census-token move, capture and non-capture)")
    revs["R8"] = git(fx, "rev-parse", "HEAD")
    # R9 (r86): the two clause-grounding targets. NF-W is the reachable-and-unrowed census-in-tree shape (r85 A1 /
    # S85Scribe F1): I85R's frozen bytes under census/round-84/w1/, which only the census-in-tree clause refuses.
    # NF-Y is the short-shape shape (S85MutCounter m14): a token ONE component below its round moved into a wave
    # capture under the same round, which only the len(want)<2||len(got)<2 guard refuses.
    c1f = os.path.join(lane, "census/round-84/records/c1-after.txt")
    with open(c1f, "rb") as f:
        c1b = f.read()
    put("census/round-84/w1/c1-after.txt", c1b)
    with open(os.path.join(lane, "census/round-83/c1-pointer-counter.py"), "rb") as f:
        i86 = f.read()
    if hashlib.sha256(i86).hexdigest() != I86S_PIN:
        raise FixtureError(f"NF-Y byte source sha256 {hashlib.sha256(i86).hexdigest()} is not the frozen {I86S_PIN}")
    put("census/round-83/waves/c1-pointer-counter.py", i86)
    git(fx, "add", "-f", "--", "census/round-84/w1/c1-after.txt", "census/round-83/waves/c1-pointer-counter.py")
    git(fx, "commit", "-q", "--no-verify", "-m", "r86 C1 fixture R9 (census-in-tree + short-shape targets)")
    revs["R9"] = git(fx, "rev-parse", "HEAD")
    # R10 (r87): TQ1's declaration. The line names the L06 token at a sentence end (`.git.`), so only `_whole`'s
    # punctuation disjunct makes that token whole; under m16 the declaration stops matching and the QUARANTINED item
    # is refused. The leaf itself is written beside the other fixture leaves below (disk-only, as they are).
    with open(os.path.join(fx, "corpus/lessons/round-79-collision.md"), "ab") as f:
        f.write(f"\n- quarantine slot `{q6}lemma-stub` keeps tests/vault/vadv54-run/p/p6repo/.git.\n".encode())
    git(fx, "add", "-f", "--", "corpus/lessons/round-79-collision.md")
    git(fx, "commit", "-q", "--no-verify", "-m", "r87 C1 fixture R10 (sentence-final quarantine declaration)")
    revs["R10"] = git(fx, "rev-parse", "HEAD")
    # R11 (r88): NF6g's declaration. The line names the L06 token only as the SUFFIX of a longer path
    # (`xtests/vault/.../.git`): the byte before the token is a path character, so only `_whole`'s before-byte half
    # refuses the row. The target is a fresh leaf (`git-stub`) so this line is the only one `git grep -e <target>`
    # returns; the leaf is written beside the other fixture leaves below (disk-only, as they are).
    with open(os.path.join(fx, "corpus/lessons/round-79-collision.md"), "ab") as f:
        f.write(f"\n- retired copy: xtests/vault/vadv54-run/p/p6repo/.git; quarantine slot `{q6}git-stub`.\n".encode())
    git(fx, "add", "-f", "--", "corpus/lessons/round-79-collision.md")
    git(fx, "commit", "-q", "--no-verify", "-m", "r88 C1 fixture R11 (longer-path before-byte declaration)")
    revs["R11"] = git(fx, "rev-parse", "HEAD")
    # R12 (r89): NF6h + NF6i. NF6h's declaration names the L06 token after `vendor/tests/.../.git` (`/` predecessor):
    # pristine refuses, m18b (alnum-only guard) accepts. NF6i's declaration carries the L06 token twice in one line
    # — first as a suffix of `xtests/.../.git`, later whole — so pristine (full loop) resolves it and m18d
    # (first-occurrence-only) does not. Each target is a fresh leaf so `git grep -e <target>` returns only its line.
    with open(os.path.join(fx, "corpus/lessons/round-79-collision.md"), "ab") as f:
        f.write(f"\n- retired copy: vendor/tests/vault/vadv54-run/p/p6repo/.git; quarantine slot `{q6}slash-stub`.\n".encode())
    with open(os.path.join(fx, "corpus/lessons/round-79-collision.md"), "ab") as f:
        f.write(f"- retired copy: xtests/vault/vadv54-run/p/p6repo/.git and tests/vault/vadv54-run/p/p6repo/.git; quarantine slot `{q6}twice-stub`.\n".encode())
    git(fx, "add", "-f", "--", "corpus/lessons/round-79-collision.md")
    git(fx, "commit", "-q", "--no-verify", "-m", "r89 C1 fixture R12 (slash predecessor + twice-token)")
    revs["R12"] = git(fx, "rev-parse", "HEAD")
    q = os.path.join(lane, ".ufo/quarantine")
    if not os.path.isdir(q):
        raise FixtureError("lane disk lacks .ufo/quarantine")
    shutil.copytree(q, os.path.join(fx, ".ufo/quarantine"), symlinks=True)
    put(".ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/NOT-THE-STUB", b"not the stub\n")
    put(".ufo/quarantine/round-17/.ufo/NOT-THE-L0", b"not the L0 file\n")
    for leaf in ("other-stub", "ghost-stub", "readme-stub", "late-stub", "lemma-stub", "git-stub",
               "slash-stub", "twice-stub"):
        put(".ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/" + leaf, f"r80 fixture {leaf}\n".encode())
    return fx, revs


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True, help="pointer-resolution counter under test")
    ap.add_argument("--lane", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--work", required=True, help="empty scratch dir (never under /tmp)")
    ap.add_argument("--population", default=None,
                    help="a pinned population TSV (default: this round's 44-row population)")
    ns = ap.parse_args(argv)
    lane, fleet, work = (os.path.abspath(x) for x in (ns.lane, ns.fleet_root, ns.work))
    counter = os.path.abspath(ns.counter)
    pop = os.path.abspath(ns.population) if ns.population else os.path.join(HERE, "c1-false-rows.tsv")
    if not os.path.isfile(pop) or sha(pop) not in POP_PINS:
        print(f"C1-HARNESS-FATAL: population sha256 {sha(pop) if os.path.isfile(pop) else '-'} is not a pinned "
              f"population ({', '.join(sorted(POP_PINS))})", file=sys.stderr)
        return 2
    nrows = POP_PINS[sha(pop)]
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C1-HARNESS-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C1-HARNESS-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    with open(pop, encoding="utf-8") as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    if len(rows) != nrows or any(len(r) != 10 for r in rows) or len({r[0] for r in rows}) != nrows \
            or any(r[2] not in ("BASE", "F0", "R1", "R2", "R3", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12")
                   for r in rows):
        print(f"C1-HARNESS-FATAL: population is not {nrows} well-formed rows", file=sys.stderr)
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
        if where not in ("lane", "fixture", "ledger"):
            print(f"C1-HARNESS-FATAL: unknown row where={where}", file=sys.stderr)
            return 2
        if (where in ("lane", "ledger")) != (rlabel == "BASE"):
            print("C1-HARNESS-FATAL: lane/ledger rows are judged at BASE and fixture rows at a fixture rev",
                  file=sys.stderr)
            return 2
        root, rev = (lane, BASE) if where in ("lane", "ledger") else (fx, revs[rlabel])
        pfile, lfile = POPS[popl]
        if where == "ledger":
            # r88 (LD1): append a duplicate row for <item> to the population's frozen ledger. The counter's
            # `_ledger` must refuse the duplicate id and fail closed (LEDGER-REFUSED + the row's exit code); a rule
            # that lets the last row win prints no marker, so the row goes red.
            dup = os.path.join(work, f"ledger-{rid}.tsv")
            with open(os.path.join(lane, lfile), "rb") as f:
                base = f.read()
            if base and not base.endswith(b"\n"):
                base += b"\n"
            # r89: LD1b appends the SAME item with a DIFFERENT target (kills the target-keyed m17b);
            # LD2 appends a 2-column malformed row (kills the dropped-guard m17c). LD1 is unchanged.
            # r90: LD2b appends the same 2-column shape under an id ABSENT from the frozen ledger, so the
            # malformed guard (not the duplicate leg) is the only refusal left for it.
            if rid == "LD1b":
                appended = f"{item}\tABSENT\tcensus/nowhere/ld1b\tr89 {rid} different-target duplicate\n"
            elif rid in ("LD2", "LD2b"):
                appended = f"{item}\tABSENT\n"
            else:
                appended = f"{item}\tABSENT\t-\tr88 {rid} duplicate-id control\n"
            with open(dup, "wb") as f:
                f.write(base + appended.encode())
            p = subprocess.run([sys.executable, "-B", counter, "--root", root, "--rev", rev, "--fleet-root", fleet,
                                "--population", os.path.join(lane, pfile), "--ledger", dup],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=lane)
            out = p.stdout.decode("utf-8", "replace")
            marker = f"LEDGER-REFUSED id={item}"
            got = "LEDGER-REFUSED" if any(l.startswith(marker) for l in out.splitlines()) else "-"
            if p.returncode == 2:
                errs += 1
                print(f"ROW {rid} where={where} rev={rlabel} item={item} class={cls} expect={exp_got}/{exp_rc} got=- "
                      f"rc=2 match=error detail={p.stderr.decode()[:200]!r}")
                continue
            ok = got == exp_got and (exp_rc == "-" or p.returncode == int(exp_rc))
            mism += 0 if ok else 1
            print(f"ROW {rid} where={where} rev={rlabel} item={item} class={cls} expect={exp_got}/{exp_rc} got={got} "
                  f"rc={p.returncode} match={'yes' if ok else 'no'}")
            continue
        forge = os.path.join(work, f"forge-{rid}.tsv")
        with open(forge, "w", encoding="utf-8") as f:
            f.write(f"{rid}\t{item}\t{cls}\t{target}\t"
                    f"{'ERROR' if exp_got == 'ERROR' else ('MISMATCH' if exp_rc != '-' else 'REFUSED')}\n")
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
