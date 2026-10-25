# CritC1Gameable — pre-measurement falsification of C1 (record agreement, K1–K4)

Seat: L1Souji23.CritC1Gameable. Lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`.
Read-only; no tool or preregistration bytes edited. Scratch used and removed:
`/var/tmp/souji-r23-CritC1Gameable/`.

## Status

STATUS: PASS — falsification complete. **C1 does not survive**: every one of the four frozen keys
is reachable at `mismatches=0` by a move that repairs nothing, and under the predicate bytes in
force when this review opened the target was not reachable by anything at all. `M_after=0` is
therefore not evidence of the four repairs; it is evidence of four edits (two of them deletions).

## Evidence

All commands run from `/home/vgpnk/Projects/shokunin/souji-shokunin`.

Base control, predicate sha `52d98536`:
```
$ python3 tools/souji-record-agreement.py --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin
MISMATCH  K1  census/round-23/records/declared-evidence-after.tsv  receipt-absent
MISMATCH  K2  LOG.md:1478  uncorrected  'assertions=56 resolved=53 skipped=33 mismatches=3' ...
MISMATCH  K2  LOG.md:1495  uncorrected  '1 present' ...
MISMATCH  K2  LOG.md:1495  uncorrected  '1 refused' ...
MISMATCH  K3  corpus/README.md:440  tally-disagree  1 present != receipt 2 present
MISMATCH  K3  corpus/README.md:440  tally-disagree  1 refused != receipt 0 refused
MISMATCH  K4  <13 working-tree paths>  uncommitted-path
keys=4 records=3 occurrences=13 mismatches=19
rc=1
```
Per-key: K1=1, K2=3, K3=2, K4=13. With `--no-worktree`: `mismatches=6`.

The predicate's own bytes are not stable inside this round (three states in ~15 min):
```
$ sha256sum tools/souji-record-agreement.py ; wc -l tools/souji-record-agreement.py
a621e6fa41502ead9f7afcb1605244df1983a637536488819f938351a19b052a   299
7515bb29cf85f5a94e1b0fecb4368daad80ed9298b5d13d4dd9e2d991a7ab902   327
52d985366c896ee4f76f0351489670d2434562e505fb36bd7da6df499b334af8   329   <- last read
```
Caught mid-write, non-executable:
```
File "tools/souji-record-agreement.py", line 185, in k2
    paras = paragraphs(lines[body_start:end], body_start)
NameError: name 'paragraphs' is not defined
```
`git status --porcelain tools/souji-record-agreement.py` -> `??` at every read. No round-23
instrument digest pin exists (`census/round-22/attempt2/instrument-digests.txt` pins only
`souji-declared-evidence.py` and `souji-gate-check.py`). `w1/MutCounter.md:30` pins
`7515bb29…`, a blob that no longer exists.

The command is not a function of `--rev`: the identical command at the identical revision
returned `mismatches=17` and then `mismatches=19` (siblings created `census/round-23/`,
`tools/souji-receipt-run.py`, `tools/__pycache__/` between runs).

K1 hash fixed point, demonstrated in a throwaway repo:
```
commit C  = 05f5134e7b16adefcfe946cdbbdfd70989044f07   receipt at C says rev=0000…0000
commit C2 = e4257e69708bd62a2200fb8fcebbd09c7a56dd75   receipt at C2 says rev=05f5134e…(C)
=> header != measured rev: a blob naming the commit that contains it is a SHA-1 fixed point
```

K1's record side, at base (`SCORECARD.md` line 14, scoped by `(?i)\br22\b|round-22`):
```
occurrences: [(14,'assertions=55 resolved=52 skipped=33 mismatches=3'),
              (14,'assertions=63 resolved=63 skipped=40 mismatches=0'),   (x2 each)]
distinct values: 2
```

K2 oracle identity moved after the freeze:
```
census/round-22/attempt2/declared-evidence-before.tsv:56         assertions=55 resolved=52 ...
census/round-22/attempt2/declared-evidence-before-final.tsv:56   assertions=55 resolved=52 ...
```
Correction, verified: `declared-evidence-before.tsv:57` is `assertions=56 resolved=53 skipped=33
mismatches=3`; `declared-evidence-before-final.tsv:56` is `assertions=55 resolved=52 skipped=33
mismatches=3`. Neither file contains any `rev=` line. The preregistration names the first; the
code now reads the second (`K2_RECEIPT`, line 50).

K3 oracle at base: `tally_of(slice-verdicts.tsv)` = accepted 5, present 2, unverifiable 1,
refused 0.

## Findings

1. **K1 cannot be satisfied without deleting the r22 base measurement.** Location
   `tools/souji-record-agreement.py:150-166` (sha `52d98536`) against `SCORECARD.md:14`. The
   frozen text says "the r22 C1 **after** 4-tuple quoted in SCORECARD.md must equal the counts
   line". The code compares **every** scoped tuple on the line to that single value. Line 14
   carries four scoped tuples with two distinct values, so at least one must always disagree. The
   only reachable repair is deleting `assertions=55 resolved=52 skipped=33 mismatches=3` — the
   r22 before-measurement — from SCORECARD.md. The predicate compels destruction of the record it
   exists to protect.

2. **The revision binding was, in the bytes in force at review start, a SHA-1 fixed point.**
   Location: sha `7515bb29` lines 145-146, `if rev != self.rev: bad(... "receipt-rev" ...)`. The
   receipt is read at `--rev` and its `rev=` header had to equal `--rev`; a blob cannot name the
   commit that contains it. Demonstrated above. `M_after=0` was unreachable by repair, by
   do-nothing, or by any commit whatsoever. The frozen text does **not** contain this clause (it
   requires only that the record's token equal the receipt's header); it was an implementation
   addition. The current sha `52d98536` removes it and adds `if not rev: bad("receipt-rev-absent")`,
   which closes the vacuity hole but leaves the receipt's token bound to nothing that relates to
   the measured revision. This clause was removed mid-round, after the preregistration froze and
   after `MutCounter.md` pinned the superseded blob.

3. **K2 is cleared by pure deletion — the append-only rule is unimplemented.** Location
   `tools/souji-record-agreement.py:233-235`, `if found == 0:` is the *only* existence guard, and
   it is global to the section. Deleting the three stale scalars
   (`assertions=56 resolved=53 skipped=33 mismatches=3`, `1 present`, `1 refused`) leaves
   `['5 accepted', '1 unverifiable']`, so `found = 2 != 0` and no mismatch fires. Verified by
   simulation against the tool's own `paragraphs()`/regexes. The preregistration asserts "the filed
   historical occurrence must still exist (its deletion is itself a mismatch: filed bytes are
   append-only)" — the code does not implement that.

4. **K2 is also cleared by moving the number elsewhere.** Same root as (3). The stale scalar can be
   cut from `LOG.md` and pasted into `corpus/lessons/round-22.md` or a fresh census file: K2 scans
   only `LOG.md`, and K3 scans only `(\d+) class` tallies, so a relocated counts tuple is invisible
   to every predicate. Move and delete are equally free.

5. **K3's per-record class requirement is implemented as a union, so one deletion clears both
   mismatches.** Location `tools/souji-record-agreement.py:240` (`present: set[str] = set()`,
   declared outside the `for record in K3_RECORDS` loop at 245) and 259-261. Verified: deleting
   `corpus/README.md:440-441` (the D4 slice-tally sentence) yields tally mismatches 0, union still
   `['accepted','present','refused','unverifiable']` from `corpus/lessons/round-22.md:351-355`, and
   `class-absent` does not fire. The frozen text requires "each record must carry at least one
   occurrence of each class"; the code does not. This is the requested "relax K3" attack, and it
   needs no tool edit at all — only a deletion in the prose.

6. **K4 is cleared by a four-row exemption list.** Location `tools/souji-record-agreement.py:272-280`.
   `K4_EXEMPT_PREFIX` rows are matched by `path == e or path.startswith(e + "/")`, so one directory
   row exempts an unbounded subtree, and nothing checks ownership, provenance or count. Verified
   against the live 13 worktree paths: `uncommitted:.ufo/`, `uncommitted:census/`,
   `uncommitted:tools/`, `uncommitted:corpus/` leaves zero unexempted. The frozen text says
   "operator-owned paths only"; the committed file already violates that — all four existing rows
   (`corpus/pointer-exemptions.tsv`, no `uncommitted:` rows present) name lane-internal paths
   (`census/operator-sweep-20261019/`, `tests/vault/...`, `tests/fixtures/...`, `.ufo/quarantine/...`).

7. **K4 is not revision-bound, so "at the tip" is meaningless for it.** Location
   `tools/souji-record-agreement.py:272` (`git status --porcelain`, working tree). The same 13 K4
   rows appear at `--rev 77d659524c777276bcef33568be3c4cbcb9d1052` and at `--rev 1208bfb…`; only
   the rev-bound keys differ. 13 of the control's 19 mismatches (68 percent) therefore carry no
   information about base versus tip. K4 also punishes the round's own deliverables
   (`tools/souji-record-agreement.py`, `census/round-23/`, `tools/souji-receipt-run.py`) and
   ambient sibling artifacts (`tools/__pycache__/`), so the author cannot separate their D1 repair
   from other seats' writes.

8. **K1 accepts a hand-written receipt.** Location `counts_of()` (`tools/souji-record-agreement.py:105-111`)
   and `k1()`: the receipt is validated only for the presence of a counts line and a `rev=` header.
   There is no `tool_sha256`, no `command=`, no `rc=`, no derivation. `SCORECARD.md`'s tuple is then
   compared to that same author-written number, so K1 measures agreement between two documents the
   author controls, not agreement with observed repo state — the exact defect C1 claims to close.
   Both r22 receipts that K2 trusts are themselves unbound: neither carries a `rev=` header.

9. **The K2 oracle was silently changed after the freeze.** `K2_RECEIPT` now names
   `census/round-22/attempt2/declared-evidence-before-final.tsv` (55/52); the preregistration names
   `declared-evidence-before.tsv` (56/53). The two files disagree, so the verdict of K2 depends on
   which one is named. This is a post-freeze target change inside the counter — the move the
   preregistration forbids — even though it happened before after-data.

10. **The K2 section is unterminated.** `K2_SECTION_START` matches `LOG.md:1469`, but no
    `^=====` follows, so the scope runs to EOF (`LOG.md:1471-1522` at base). Any later LOG text,
    including this round's own entries, becomes a K2 occurrence and can create new mismatches.
    Related auditability defect: mismatch rows report the paragraph's first line
    (`LOG.md:1478`) while the offending tuple sits at `LOG.md:1484`.

11. **The counts line is version-defined, not spec-defined.** `occurrences` moved 10 -> 13 at the
    same revision purely because `TALLY_RE` gained `\s+` and `\*{0,2}` wrappers (sha `7515bb29` ->
    `52d98536`). `keys=K records=R occurrences=O mismatches=M` is therefore not reproducible from
    the frozen text plus the revision; it needs the tool digest, which is unpinned.

## Attack log

Cheap moves an author could make to reach `mismatches=0` without repairing anything. Verdict per
move: caught / not caught, with the smallest predicate change that closes it while leaving the
target (`M_after=0`) untouched.

A1. **Delete the quoted numbers** (K2, `LOG.md:1478`, `LOG.md:1495`). NOT CAUGHT — `found == 0` is
    global; two correct tallies survive and silence the guard. Verified.
    Smallest fix: pin the base-revision occurrence multiset and require containment —
    `for occ in base_occs: if occ not in " ".join(all_paragraph_text): bad("K2", …, "filed-occurrence-deleted", occ)`.

A2. **Move a number to another file** (K2). NOT CAUGHT — identical to A1; K2 scans only `LOG.md`
    and K3 matches only tallies, so a relocated counts tuple is invisible everywhere. Verified by
    code reading of `K2_RECORD`/`K3_RECORDS`. Same one-line fix as A1 (the base multiset check
    covers relocation and deletion together).

A3. **Relax K3 by removing the class-occurrence requirement** (K3). NOT CAUGHT — and needs no tool
    edit: `present` is union-scoped (line 240 outside the loop at 245), so deleting
    `corpus/README.md:440-441` clears both base mismatches and fires nothing. Verified.
    Smallest fix: move `present: set[str] = set()` inside the `for record in K3_RECORDS:` loop and
    emit `class-absent` per record instead of once after the loop.

A4. **Declare a giant `uncommitted:` exemption list** (K4). NOT CAUGHT — four directory rows give
    zero mismatches; no ownership, provenance or cardinality check. Verified against the live tree.
    Smallest fix: in the exemption loop require the named path to be untracked at the measured
    revision and outside the lane, e.g.
    `if path and read_at(self.root, self.rev, path.rstrip("/")) is None and not path.startswith(("corpus/","tools/",".ufo/","census/")):`.

A5. **Point K1 at a receipt the author writes by hand** (K1). NOT CAUGHT — no `tool_sha256`, no
    `command=`, no `rc=`; the two compared numbers are both author-authored.
    Smallest fix: one added guard in `counts_of`/`k1` requiring
    `^tool_sha256=([0-9a-f]{64})$` and comparing it to `git rev-parse <rev>:tools/souji-declared-evidence.py`
    (the mechanism C2 already builds in `tools/souji-receipt-run.py`).

A6. **Make the revision-token check vacuous** (K1). In the bytes in force at review start it was the
    mirror failure — unsatisfiable, not vacuous (finding 2, SHA-1 fixed point; demonstrated). The
    current sha `52d98536` catches a missing header (`receipt-rev-absent`), so plain vacuity is
    closed; what remains is that the token is never required to bear any relation to `--rev`, which
    matches the frozen text but leaves A5 unblocked. Smallest fix: none needed for vacuity; A5's
    digest binding is the substantive gap.

## Verdict — is `M_after=0` at the tip reachable by a do-nothing control?

**No, but for the wrong reasons — and that is the finding.**

Base-state facts used: control at `1208bfb` = `mismatches=19` (K1 1, K2 3, K3 2, K4 13), so the
preregistration's control rule is formally satisfied (control is non-zero). Strip K4's 13
rev-independent rows and the rev-bound residual is 6. Those 6 are exactly the four routed defects,
so the counter does carry real base signal for K2 and K3 (D5, D4) and a pure absence signal for K1
(D2).

A do-nothing control — commit the round's work, touch none of the four records — lands at
`mismatches=6`, not 0: K1 stays 1 (no receipt), K2 stays 3, K3 stays 2. So the target is *not*
reachable by doing nothing, and the claim is not trivially true.

But `M_after=0` is reachable by four edits that repair nothing: delete `LOG.md`'s three stale
scalars (A1), delete `corpus/README.md:440-441` (A3), add four `uncommitted:` directory rows (A4),
and write a receipt by hand (A5) while deleting SCORECARD.md's r22 before-tuple because finding 1
forces it. Every one of those moves *destroys* the record the claim is about, and none of them is
observable by any predicate. So the counter cannot distinguish "the four defects are repaired" from
"the four defects are deleted and exempted", which is the definition of a gameable calibration
counter.

And under the bytes that were in force when this review opened (sha `7515bb29`), the answer is
stronger: `M_after=0` was reachable by **nothing at all**, because K1's receipt-rev clause demanded
a SHA-1 fixed point. The counter therefore moved, during the review, from unpassable to
unfalsifiable.

Smallest safe correction, in priority order, all without touching the frozen target, key set or
preregistration text: (i) pin the tool blob in a committed digest file so the predicate has stable
bytes and one named version; (ii) delete the forced-deletion behaviour of finding 1 by binding each
counts tuple to the 40-hex token immediately preceding it and comparing only the tuple whose token
equals the receipt header; (iii) apply A1/A2, A3, A4 and A5. With (i)-(iii) the claim becomes
measurable: `M_after=0` then requires a rev-bound receipt, preserved filed bytes, per-record class
coverage, and a clean tree. Until then, a tip run reporting `mismatches=0` must not be recorded as
C1 evidence.
