# W2C3Control — does C3's cheap control actually fail, and is the do-nothing tree excluded?

Lane tip under test: `1026900` (wave-2 spec); C3 landed at `4765250`. Base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`.
All commands read-only; mirror work in `/var/tmp/souji-r23-w2-W2C3Control/` (removed at finish).

## Verdict

- **Claim limb A — "an append of the staged rows as-is must fail the census (duplicate id)": `survives`
  as a mechanism, `falsified` as filed evidence.** The append does fail, with `E03` on S112/S113/S114
  (`rc=1`). But `preregistration.txt:116` says "That receipt is committed before append", and **no such
  receipt exists anywhere in the tip tree**.
- **Claim limb B — a do-nothing tree (the base revision) cannot reach `entries=2 ok=2 fail=0` for the two
  NEW entries: `survives`.** At `1208bfb` the gate reports `ok=0 fail=3 rc=1`, with byte-identical tool
  (`sha256 d5ed0805…` at both revisions).
- Two **precision defects** in the frozen control sentence (`preregistration.txt:114-116`): the gate limb
  cannot detect a duplicate id at all, and the "duplicate id" mechanism covers only entry 1 — entry 2's
  staged ids are absent, not colliding.
- One **stale claim shape**: the C3 header says "3 rows" (`:91`); the bytes are 5.

## Evidence

### A1 — the cheap control reproduced (staged S112–S114 appended to a copy of the registry)

Mirror = `corpus/SOURCES.md` at tip (119 registry rows) + the three staged rows from
`/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:10-12` inserted directly after the last
registry row (`| S119 |`), i.e. appended as-is, ids untouched. Census run against the full mirrored
lane so `used-by` paths resolve:

```
$ bash scripts/sources-census.sh validate --root /var/tmp/souji-r23-w2-W2C3Control/mirror \
    /var/tmp/souji-r23-w2-W2C3Control/mirror/souji-shokunin ; echo rc=$?
souji-shokunin	E03	S112 duplicate id
souji-shokunin	E03	S113 duplicate id
souji-shokunin	E03	S114 duplicate id
souji-shokunin	E09	S112 recheck=on-release — re-read `man git-count-objects` after a host git upgrade
souji-shokunin	E09	S113 recheck=on-release — re-read `man git-fsck` after a host git upgrade
souji-shokunin	E09	S114 recheck=on-release — re-read `man git-prune` after a host git upgrade
souji-shokunin	E11	S112 missing used-by corpus/knowledge/count-objects-garbage-semantics-r23.md
souji-shokunin	E11	S113 missing used-by corpus/knowledge/count-objects-garbage-semantics-r23.md
(33 × W04, pre-existing)
rc=1
```

Code tally: `3 E03, 3 E09, 2 E11, 33 W04`. Rows go 119 → 122. So the control fails on **three**
independent classes, not only the duplicate id — the staged rows are also malformed on `recheck` and cite
a `used-by` file this lane does not hold. That is a stronger refusal than the claim states.

### A2 — the gate limb cannot see a duplicate id

`tools/souji-gate-check.py:123-130` builds a **set** of ids (`known`) and rejects only
`check5-dangling-source` (`sid not in known`). A duplicated id is invisible. Proof: same registry as A1
(S112 appears twice) but the lane's real entry files:

```
$ python3 -B tools/souji-gate-check.py --root mirror3 --round-date 2026-10-25 \
    --entries corpus/knowledge/repo-size-census-readonly.md \
              corpus/knowledge/count-objects-garbage-readings-r25.md \
    --snapshot-dir census/round-23/sources --slice census/round-23/records/empty-slice \
    --slice-verdicts census/round-23/records/empty-verdicts ; echo rc=$?
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0
rc=0
$ grep -cE '^\| S112 ' mirror3/corpus/SOURCES.md
2
```

The gate passes with the duplicate present. `preregistration.txt:116`'s "must fail the census/gate
(duplicate id)" is therefore half-inaccurate: the duplicate-id refusal is **census-only (E03)**.

### A3 — entry 2's staged ids are absent, not colliding (the mechanism does not generalise)

`preregistration.txt:114-115` asserts "the two staged entries cite staged ids that resolve to DIFFERENT
sources in this lane's registry". Base registry max id is S114 and staged entry 2 cites S134/S138/S139 —
none of which resolves to anything here. Appending only those three staged rows as-is:

```
$ bash scripts/sources-census.sh validate --root .../mirror2 .../mirror2/souji-shokunin ; echo rc=$?
souji-shokunin	E09	S134 recheck=90d — re-run the garbage census (expect garbage: 0 everywhere)
souji-shokunin	E09	S138 recheck=365d — re-fetch the Qiita item
souji-shokunin	E09	S139 recheck=365d — re-fetch the bbs.csdn.net page
souji-shokunin	E11	S134 missing used-by corpus/knowledge/count-objects-garbage-semantics-r24.md
souji-shokunin	E11	S138 missing used-by corpus/knowledge/count-objects-garbage-semantics-r24.md
souji-shokunin	E11	S139 missing used-by corpus/knowledge/count-objects-garbage-semantics-r24.md
rc=1
```

**Zero E03.** The refusal here is malformed `recheck` + dangling `used-by`; a lane that appended only
entry 2's rows would have been refused, but for reasons the frozen control sentence does not name. The
"different sources" premise is true only of S112–S114.

### A4 — do-nothing tree (base revision) cannot reach the C3 target

Base tree materialised with `git archive 1208bfb | tar -x -C /var/tmp/…/base` (no lane mutation), then the
frozen C3 command pointed at it. Both the tip tool and the base tool (identical bytes) agree:

```
$ python3 -B <tip>/tools/souji-gate-check.py --root base --round-date 2026-10-25 \
    --entries corpus/knowledge/repo-size-census-readonly.md \
              corpus/knowledge/count-objects-garbage-readings-r25.md \
    --snapshot-dir census/round-23/sources --slice census/round-23/records/empty-slice \
    --slice-verdicts census/round-23/records/empty-verdicts ; echo rc=$?
FAIL corpus/knowledge/repo-size-census-readonly.md entry-missing: …
FAIL corpus/knowledge/count-objects-garbage-readings-r25.md entry-missing: …
FAIL slice slice-missing
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=3
rc=1
```

`git ls-tree -r --name-only 1208bfb | grep -E 'repo-size-census|count-objects-garbage-readings'` → empty;
`base/census/round-23` does not exist. Same result with `base/tools/souji-gate-check.py` (`rc=1`), and
`sha256sum` gives `d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d` for both revisions —
so the failure is caused by missing content, not by a tool that got stricter. **Do-nothing is excluded.**

The counter is also discriminating on the *other* half: entries landed at base, registry untouched →

```
FAIL …repo-size-census-readonly.md check5-dangling-source: S115 / S116 / S117
FAIL …count-objects-garbage-readings-r25.md check5-dangling-source: S118 / S119
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=5   rc=1
```

Neither limb passes alone; the tip run reproduces the target exactly (`entries=2 ok=2 fail=0`, `rc=0`,
tip registry 119 rows, census `validate` `rc=0`, `rows 119 / tier.invalid 0`).

## Findings

1. **The control receipt the prereg promises does not exist (calibration class).**
   `preregistration.txt:116`: "That receipt is committed before append."
   `git ls-tree -r --name-only HEAD census/round-23/records/` → 11 files
   (`agreement-after.tsv`, `agreement-control-base{,-worktree}.txt`, `declared-evidence-after.tsv`,
   `empty-slice`, `empty-verdicts`, `gate-check-at-first-landing.tsv`, `gate-check-at-lane-base.tsv`,
   `gate-check-c3.tsv`, `refusal-stale-digest.txt`, `uncommitted-exemptions.tsv`) — none is a census
   control. `grep -rln 'E03\|duplicate id' census/round-23/` → no hits. The landed C3 paragraphs
   (`corpus/lessons/round-23.md:35-40`, `LOG.md:1594-1600`, `corpus/README.md:458`, `SCORECARD.md:23`)
   never cite a control run. This is the **same defect class as D2** (an assertion with no committed
   byte binding it) that C1 exists to repair, reintroduced in C3 — and no frozen C1 key covers it
   (K1 binds the after-tuple, K2/K3 scan LOG/README tallies, K4 scans the worktree).
   **Round must:** commit the receipt as a **post-hoc re-derivation at the tip** — append the staged rows
   to a `/var/tmp` mirror of `corpus/SOURCES.md`, run `sources-census.sh validate`, record the E03 lines
   and `rc=1` under `census/round-23/records/` — and state in LOG/lesson that the pre-append receipt the
   prereg required was **not** filed, rather than implying it was. It may not be labelled a pre-append run.

2. **"census/gate (duplicate id)" is not a gate predicate.** `preregistration.txt:116` vs
   `tools/souji-gate-check.py:123-130` (set membership). Demonstrated: the gate returns
   `entries=2 ok=2 fail=0 rc=0` against a registry containing two `S112` rows. **Round must:** disclose in
   the lesson/report that the cheap control is refused by the **census** (`E03`), and that the gate arm of
   C3 has no id-uniqueness test — it cannot be the witness for this control.

3. **The "different sources" premise holds for entry 1 only.** `preregistration.txt:114-115`. Entry 2's
   staged ids (S134/S138/S139) are absent from a 114-row registry, so they collide with nothing; the
   append-only-entry-2 control fails on `E09`+`E11` with zero `E03` (A3). **Round must:** state the two
   limbs separately — entry 1 = duplicate-id collision (E03), entry 2 = dangling `used-by` + malformed
   `recheck` — or the control reads as evidence for a mechanism that only half applies.

4. **Stale claim shape, record already correct.** `preregistration.txt:91` says "2 entries, 3 rows" and
   `:111` targets "registry rows 114 -> >=117". The landed bytes add **five** rows (S115–S119; diff of id
   lists between `1208bfb` and tip = `S115 S116 S117 S118 S119`), and `>=117` is satisfiable by a lane
   that adopted only three. The landed prose is accurate (`corpus/lessons/round-23.md:37` and
   `LOG.md:1599`: "Registry 114 → 119 rows"), so this is a frozen-prereg artifact, not a false claim in
   the record. **Round must:** disclose it in the report (prereg is frozen; no edit).

## Impacted axes

- **calibration (7)** — Finding 1: an unreceipted control in the claim that carries the round's lowest
  axis; the round's own K-set cannot see it.
- **coverage (8)** — Findings 2–3: C3's evidence chain names a gate predicate that does not exist and a
  collision mechanism that covers one of two entries; the claim's discriminating power is smaller than
  stated. No entry content is impugned — the two entries pass their own gate on the real bytes.
- **operability (8)** — untouched (C2's receipts were not exercised here).

## Smallest safe correction

1. Commit a tip-labelled control receipt (`census/round-23/records/`) reproducing A1: mirror append of
   staged S112–S114 → `E03` ×3, `E09` ×3, `E11` ×2, `rc=1`; mark it post-hoc.
2. One disclosure line in `corpus/lessons/round-23.md` C3 block and the LOG C3 paragraph: the control is
   a **census** refusal (`E03`); `souji-gate-check.py` has no duplicate-id predicate; entry 2's staged ids
   are absent, not colliding; the prereg's pre-append receipt was not filed.
3. Disclose the 3-vs-5 row count in the report (no prereg edit). Nothing in the entries, the registry, or
   the two landed commits needs to change.

## Verdict

**C3's control survives on its operational content and is falsified on its filed evidence.** The cheap
append fails exactly as required (E03 on the three colliding ids, `rc=1`), the do-nothing base tree is
excluded with byte-identical tooling (`ok=0 fail=3 rc=1`), and neither half of the work passes alone. What
is missing is the receipt the prereg itself demanded before the append, and two sentences that describe a
gate predicate and a collision mechanism more broadly than the bytes support.

## Lane state at review time (transient, not a finding)

`git status --porcelain` at tip `1026900` while wave 2 is in flight: `M` on
`census/round-23/records/refusal-stale-digest.txt`, `corpus/lessons/round-23.md`,
`tests/fixtures/r23-locator-heading.py`, `tests/fixtures/r23-record-agreement.py`,
`tools/souji-receipt-run.py`; untracked `tools/__pycache__/` and `census/operator-sweep-20261019/`
(the latter is the one committed K4 exemption). `tools/__pycache__/` is the R23-M8 class recurring —
whoever lands must remove it, since K4 counts it and `uncommitted-exemptions.tsv` names only the sweep
directory. My citations to `corpus/lessons/round-23.md:37` were checked against the `HEAD` blob and
agree with the worktree, so no finding above rests on an in-flight edit.

## Tooling

No installs, no upgrades (pacman paused host-wide; none needed). No subagent (leaf seat). Scratch
`/var/tmp/souji-r23-w2-W2C3Control/` removed at finish. Read-only commands only: `git archive`,
`git ls-tree`, `sha256sum`, `sources-census.sh validate|census`, `souji-gate-check.py`, `grep`, `awk`.
