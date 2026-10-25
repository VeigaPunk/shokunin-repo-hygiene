# W2Control — do-nothing control for C1/C2/C3

Seat: L1Souji23.W2Control (critic, leaf). Round 23, wave 2.
Base revision under test: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`.
Lane tip at review: `102690017115cb202f292828c90b72705f69bf09` (master).
Scratch: `/var/tmp/souji-r23-w2-W2Control/` (base tree via `git archive`, plus a
`git clone --no-local` for the git-plumbing instruments). Removed before finish.

Question asked: **at the base revision, is any of C1/C2/C3's after-value reachable without the
round's work, and which arm of each counter does a do-nothing tree satisfy?**

Headline: **no after-value is reachable at base for any of the three claims.** But C1's control
arm is *vacuous* — it is satisfied by a single hard-coded round-23 path's absence, so it cannot
fail for any pre-round revision and cannot detect a dead K2/K3 predicate. C2's and C3's controls
survive, with two C3 after-arms pre-satisfied at base (disclose, not falsify).

---

## Verdicts

| Claim | After-value reachable at base? | Do-nothing arm satisfied | Verdict |
|---|---|---|---|
| C1 calibration (M=0) | **No** — counter file absent (`exit 2`); same bytes at base = 6 mismatches | before/control arm (M>=1) is satisfied **only by transplanting the round's instrument, and then it is vacuous** | **falsified as a control**; claim's after-value survives |
| C2 operability (>=4 bound receipts) | **No** — base count 0, runner absent | the **before** arm exactly (0) — genuine measurement, intended before state | **survives** |
| C3 coverage (entries=2 ok=2, rows>=117, census exit 0) | **No** — `fail=3`, 114 rows | `census exit 0` and `0 malformed/0 duplicate` arms are **pre-satisfied (vacuous)**; append-as-is control fires E03 non-vacuously | **survives**, two arms disclose |

---

## C1 — record agreement

### 1. Base tree, own bytes (true do-nothing)

```
$ cd /var/tmp/souji-r23-w2-W2Control/base
$ python3 -B tools/souji-record-agreement.py --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd \
    --root /var/tmp/souji-r23-w2-W2Control/base --no-worktree
python3: can't open file '.../base/tools/souji-record-agreement.py': [Errno 2] No such file or directory
exit=2
```

The counter command itself does not exist at base (also: `tests/fixtures/r23-record-agreement.py`
absent, `census/round-23/` absent). **The after-value M=0 is unreachable by a do-nothing tree —
not because the base is defective, but because the measuring instrument is the round's work.**

### 2. Same bytes at base (the control the round actually committed)

```
$ cd /var/tmp/souji-r23-w2-W2Control/clone            # --no-local clone, detached at 1208bfb
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py \
    --rev 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd --root . --no-worktree
MISMATCH	K1	census/round-23/records/declared-evidence-after.tsv	receipt-absent	not in tree at 1208bfb…
MISMATCH	K2	LOG.md:1478	uncorrected	'assertions=56 resolved=53 skipped=33 mismatches=3' has no later 'superseded by' line
MISMATCH	K2	LOG.md:1495	uncorrected	'1 present' has no later 'superseded by' line
MISMATCH	K2	LOG.md:1495	uncorrected	'1 refused' has no later 'superseded by' line
MISMATCH	K3	corpus/README.md:440	tally-disagree	1 present != receipt 2 present
MISMATCH	K3	corpus/README.md:440	tally-disagree	1 refused != receipt 0 refused
keys=4 records=3 occurrences=13 mismatches=6
exit=1
```

Byte-identical to the committed receipt `census/round-23/records/agreement-control-base.txt`
(6 mismatches, 13 occurrences). Tip, committed bytes only:

```
$ python3 -B tools/souji-record-agreement.py --rev 1026900… --root . --no-worktree
keys=4 records=4 occurrences=17 mismatches=0
exit=0
```

So the *number* is right: 6 → 0. What is wrong is what the 6 proves.

### 3. The ">=1" arm is vacuous — proof

`K1_RECEIPT` is a hard-coded round-23 path (`tools/souji-record-agreement.py:43`), and K1's first
branch emits a mismatch whenever that path is absent at `--rev` (`tools/souji-record-agreement.py:142`):

```python
K1_RECEIPT = "census/round-23/records/declared-evidence-after.tsv"
...
if text is None:
    self.bad("K1", K1_RECEIPT, "receipt-absent", f"not in tree at {self.rev}")
```

No pre-round revision can contain that path. Empirical confirmation, three distinct pre-round
revisions, all identical:

```
$ for r in 77d6595 9301d98 dd8a6b7; do python3 -B tools/souji-record-agreement.py \
    --rev $(git rev-parse $r) --root . --no-worktree | grep -E 'K1|mismatches='; done
rev 77d6595:  K1 … receipt-absent … ; keys=4 records=3 occurrences=13 mismatches=6
rev 9301d98:  K1 … receipt-absent … ; keys=4 records=3 occurrences=13 mismatches=6
rev dd8a6b7:  K1 … receipt-absent … ; keys=4 records=3 occurrences=13 mismatches=6
```

And the decisive probe — **the tip tree with only the K1 receipt deleted** (all round repairs
present, nothing else changed), committed in the scratch clone:

```
$ git checkout -b probe-no-receipt 1026900… && git rm census/round-23/records/declared-evidence-after.tsv
$ python3 -B tools/souji-record-agreement.py --rev a1dacbe0ad0db28a3f205bdad7c33e7a4ae7edf0 --root . --no-worktree
MISMATCH	K1	census/round-23/records/declared-evidence-after.tsv	receipt-absent	not in tree at a1dacbe…
keys=4 records=3 occurrences=15 mismatches=1
exit=1
```

**One row, produced by a file that only the round can create, is the entire control arm.** The
prereg's gate (`.ufo/waves/round-23/preregistration.txt:55-57`) is "if that control reports M=0 the
counter or target is wrong". That gate can never fire for any pre-round revision, so it cannot
detect a counter whose K2/K3 predicates are dead: an instrument that emitted K2=K3=0 always and
carried this K1 branch would pass the control with M=1. The prereg's own word for the arm is also
wrong: the control is not "do nothing" — it is *instrument-transplant* (round bytes, base tree), a
fact the receipt already discloses on line 6: "the tool does not exist at the base revision, so
receipt-run cannot bind it there".

An earlier probe (base tree + a syntactically valid K1 receipt only) showed the row does not
collapse to file existence alone — K1 then reports `value-disagree` at `SCORECARD.md:14`, because
the r22 dual-end row binds the before-tuple to the receipt rev. That strengthens the point: no base
tree can clear K1 without the round's SCORECARD rewrite, i.e. the arm is guaranteed *more* strongly
than a mere existence check.

### What the round must do (C1)

**Disclose and fix the control predicate** — not the claim. Smallest safe correction: freeze the
control as the receipt-independent keys, e.g.

```
control: mismatches(K2) >= 1 AND mismatches(K3) >= 1 at 1208bfb
```

measured at base as **K2=3, K3=2** (rows above) — falsifiable, because a base with corrected LOG.md
and corpus/README.md would give 0. Keep K1 in the after-predicate (it is the D2 repair) but out of
the control. The prereg is frozen pre-data, so this lands as a disclosure in the report + a
QUALITY/LESSON row, or the round reports the control as `claim-sizing gate: partial (K1 arm
structural)`. The claim's after-value is unaffected.

Live observation, not this seat's finding: the counter over the *live* worktree currently reports
`mismatches=1` (K4 `?? .ufo/waves/round-23/report-draft.md`) — an in-flight draft of the round's own
report, not committed bytes. W2K4 / W2C1Ctl own that; committed bytes give 0.

---

## C2 — blob-bound receipts

Base tree, the claim's own counting command:

```
$ cd /var/tmp/souji-r23-w2-W2Control/base
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
0
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' . | wc -l
0
$ ls tools/ | grep -c receipt-run
0
```

`census/` exists at base (21 round directories, `operator-sweep-20261018`, `round-1`…`round-22`), so
the `0` is a real measurement over real bytes, not a missing-directory artefact. Tip:

```
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ | wc -l
5
$ grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/
census/round-23/records/declared-evidence-after.tsv
census/round-23/records/gate-check-at-first-landing.tsv
census/round-23/records/gate-check-at-lane-base.tsv
census/round-23/records/agreement-after.tsv
census/round-23/records/gate-check-c3.tsv
```

Arms:

| Arm | Base | Tip | Do-nothing satisfies? |
|---|---|---|---|
| before = 0 | 0 | — | **yes, exactly** — this is the intended before state, and it is falsifiable (any bound receipt predating the round would break it) |
| after >= 4 | 0 | 5 | no |
| refusal demo (`RECEIPT-TOOL-DIGEST-MISMATCH`) | runner absent | fires per W2C2Verify | no |

**Verdict: survives.** The do-nothing tree satisfies only the before arm, which is the claim's own
before target and is non-vacuous. No after-arm is reachable at base. (Whether the after count can be
inflated with an unverifiable file is W2C2Count's lane; not tested here.)

---

## C3 — F2 read side

### After-arms at base (own bytes; `tools/souji-gate-check.py` *does* exist at base)

```
$ cd /var/tmp/souji-r23-w2-W2Control/base
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/repo-size-census-readonly.md \
              corpus/knowledge/count-objects-garbage-readings-r25.md \
    --snapshot-dir census/round-23/sources \
    --slice census/round-23/records/empty-slice \
    --slice-verdicts census/round-23/records/empty-verdicts
FAIL corpus/knowledge/repo-size-census-readonly.md entry-missing: …
FAIL corpus/knowledge/count-objects-garbage-readings-r25.md entry-missing: …
FAIL slice slice-missing
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=3
exit=1
```

Same command with the **tip** gate-check bytes against the base tree gives the identical
`entries=2 ok=0 … fail=3` — so C3's control is *not* instrument-dependent (unlike C1); the base tree
fails on its own bytes. Tip for comparison:

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries … 
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0
exit=0
```

### Registry and census at base

```
$ grep -cE '^\| *S[0-9]+' corpus/SOURCES.md          # 114
$ grep -oE '^\| *S[0-9]+' corpus/SOURCES.md | tail -1 # | S114
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file corpus/SOURCES.md
file	W04	S035 duplicate url …
… (30 W04 warnings)
file	ok	/var/tmp/souji-r23-w2-W2Control/base/corpus/SOURCES.md
exit=0
```

Tip: 119 rows, max `S119`, census `souji ok … exit=0`.

### The C3 cheap control, reproduced at base

Base ids `S112`/`S113`/`S114` are already occupied by **different** sources (`gio(1)`, the GLib
`g_file_trash()` reference, `statx(2)` — `corpus/SOURCES.md:132-134`). Appending the staged
`/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` rows 10-12 verbatim into the base
registry (scratch copy `base-append/`) gives:

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file corpus/SOURCES.md
file	E03	S112 duplicate id
file	E09	S112 recheck=on-release — re-read `man git-count-objects` after a host git upgrade
file	E03	S113 duplicate id
file	E09	S113 recheck=on-release — re-read `man git-fsck` after a host git upgrade
file	E03	S114 duplicate id
file	E09	S114 recheck=on-release — re-read `man git-prune` after a host git upgrade
file	E11	S112 missing used-by corpus/knowledge/repo-size-census-readonly.md
file	E11	S113 missing used-by corpus/knowledge/repo-size-census-readonly.md
file	E11	S114 missing used-by corpus/knowledge/repo-size-census-readonly.md
exit=1
```

(The E11 rows are the staged entries' used-by targets, absent at base; E09 is an independent defect
in the staged rows' `recheck` cell — worth a line in the report, not this seat's claim. My first
attempt appended outside `## Registry` and produced E12 instead of E03; that run is discarded.)

### Arms

| Arm | Base | Do-nothing satisfies? |
|---|---|---|
| `entries=2 ok=2 fail=0` | `fail=3` | **no** — discriminating |
| registry 114 → >=117 | 114, max S114 | **no** — discriminating |
| 0 malformed, 0 duplicate ids | 0, 0 | **yes → vacuous** (base validate exit 0, W04 only) |
| census exit 0 | 0 | **yes → vacuous** (unchanged by the round) |
| control: append-as-is must fail | E03 ×3 | **yes, non-vacuously** (ids occupied by different sources) |

**Verdict: survives.** The after-value is unreachable at base and the cheap control genuinely fires.
Two of the four after-arms (`census exit 0`; `0 malformed / 0 duplicate`) were already true at base
and therefore carry no evidence — the round should say so when it quotes "census exit 0" as a C3
after-value, or drop it from the after set. That is a one-line disclosure, not a repair.

---

## Smallest safe corrections (one line each)

1. **C1** — `.ufo/waves/round-23/preregistration.txt:55` and the report's control row: replace
   "do nothing = run the instrument at base" with "instrument-transplant control; discriminating
   arm = `mismatches(K2)>=1 AND mismatches(K3)>=1` at base (measured 3 and 2)". Disclose that the
   K1 row is structural. No code change to `tools/souji-record-agreement.py` is required; if the
   round prefers code, the control must be a separate predicate, not `mismatches>=1`.
2. **C2** — no change. Record that the do-nothing tree satisfies the *before* arm (0) by design.
3. **C3** — one disclosure line: `census exit 0` and `0 malformed/0 duplicate` hold at base already
   (`corpus/SOURCES.md` validates exit 0 at 1208bfb), so only `entries=2 ok=2` and `114→119` are
   evidence. No repair.

## Bounds observed

Read-only against the lane: only `git archive`, `git cat-file`/`show` via the instruments, `git
status` (read), and the census/gate tools. The two commits I made are in
`/var/tmp/souji-r23-w2-W2Control/clone` (a `--no-local` scratch clone), never in the lane. No
install, no `rm`/`mv` outside scratch, no signals, no writes to `.ufo/state/`, `MANIFEST.json`,
`.scratch/`, fleet `scripts/`/`templates/`, or sibling lanes. Scratch removed after this report.

## Report trailer

`Report: .ufo/waves/round-23/w2/W2Control.md`
