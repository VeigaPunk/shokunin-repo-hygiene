# deliver-docs-f1.md — documentation that lands with the C3 entry (round 30, F1)

Seat: SwarmScribe17 (leaf scribe). Integration owner: L1. Nothing here is applied; these are
the exact texts the C3 landing commit needs.

**Landing rule (Q56, `corpus/QUALITY.md:135`):** the four edits below land in the SAME commit as
`corpus/knowledge/jj-keep-ref-expiry.md`. Item 1 is what makes `tools/souji-coverage-agreement.py`
print `grounded=16 mapped=16` (c3-counter leg L2: `grounded=16 mapped=16 dangling=0
mismatches=0`); without it the new entry is a `MISSING-FROM-MAP` finding and C3 cannot reach
`fail=0`.

**Path convention:** every path inside a fenced block is written as it must read at its
destination — `../census/...` blocks are `corpus/README.md` text (corpus-relative), and the
PROVINCE/SKILL blocks are lane-root-relative. This delivery file is not a seat report and is not
a gate input.

Facts used below are read from the wave-1 delivery artifacts, not re-measured by this seat:
`../census/round-30/records/jj-keep-expiry-run.txt` (source delivery
`deliver-jj-keep-expiry-run.txt`), `deliver-r30-jj-keep-expiry.sh`, and
`receipt-SwarmExecutor06-keepref-mechanism.txt`; the `jj util gc` wording was re-read from
`jj util gc --help` on jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5 in this seat and
matches `sources/cli-reference@.md.snap:3793, 3801, 3803`.

---

## 1. `corpus/README.md` line 39 — in-place F1 row replacement

Anchor: the r12 coverage-map row whose ground cell is `F1 git-native housekeeping vs receipts`
(rendered as `corpus/README.md:39`; matches once, so match on the text, not the line number).

### Current line (verbatim)

```
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md` |
```

### Replacement line (verbatim)

```
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md`, `knowledge/jj-keep-ref-expiry.md` |
```

### What changes and what does not

- Entries cell gains exactly one backticked span, `knowledge/jj-keep-ref-expiry.md`, appended
  last; the four existing entries keep their order and wording.
- Status cell is untouched and already reads `frontier, entries held`; F1 is not promoted and
  no row is superseded by a later table (same in-place convention as r28's F4 row and r29's
  F3 row at `:41`).
- Nothing else in the file changes for this item.

Integrator check after the landing commit is made:

```
python3 -B tools/souji-coverage-agreement.py --root . --rev <full40> --base-rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
# expect: grounded=16 mapped=16 dangling=0 mismatches=0    (base: grounded=15 mapped=15)
```

---

## 2. `corpus/README.md` — append after line 596 (end of file)

Append with one blank line before the heading, matching the `## Round 29 — F3 duplicate
verdicts re-grounded` section that ends the file.

```markdown
## Round 30 — F1 keep-ref expiry measured

Appended; the sections above stand. One knowledge entry is admitted for F1, measured this round
with real jj 0.45.1 and git 2.56.0 in scratch repositories under the round's scratch root, never
against a lane:

- `knowledge/jj-keep-ref-expiry.md` — what removes a `refs/jj/keep/*` ref and when. One run of
  an eight-step fixture (steps 1-5 on a main repository, steps 6-8 on a control repository):
  `git gc --prune=now` leaves the keep ref naming the abandoned commit in place,
  `jj util gc --expire=now` removes it, and `jj op abandon ..@-` before a second
  `jj util gc --expire=now` leaves two keep refs where eight stood. The commit object stayed
  present in every step, so a dropped keep ref is not a deleted object and the object-prune
  clock is a separate question. The default threshold is two weeks, and `--expire` accepts only
  the string `now`; a future timestamp is refused, so the "not yet expired" arm is the default
  run. Fixture `../tests/fixtures/r30-jj-keep-expiry.sh`; measured record
  `../census/round-30/records/jj-keep-expiry-run.txt` (`jj-version: jj 0.45.1`, eight `RESULT`
  lines).

Coverage-map effect: the F1 row at `:39` now names a fifth entry with its status cell unchanged
(`frontier, entries held`); the four entries it already carried are unchanged. F1 stays
frontier — the entry measures a ref's lifetime, and one entry does not promote a frontier ground
to Core (PROVINCE `## Round 30 boundary note`).

### Frontier (r30)

- F1 — keep-ref expiry is now measured (the entry above; jj 0.45.1, eight `RESULT` steps,
  `../census/round-30/records/jj-keep-expiry-run.txt`). Remaining: the fleet exposure numerator
  re-census named at `:46`; and, disclosed rather than measured here, when the commit object
  behind a dropped keep ref is pruned by git's own clock — the run records `object_present=yes`
  at every step and stops before that question.
- F2, F3, F4 — unchanged. F5 stays list-only; the reap protocol and NAMESPACE pin remain
  operator-held. Certification OFF, K5 HELD.

### Round 30 corrections

- The r12 F1 row at `:39` was replaced in place rather than superseded by a later table: its
  entries cell gained `knowledge/jj-keep-ref-expiry.md` and its status cell, already
  `frontier, entries held`, was not reworded. Map rows are edited in place (r28 did the same to
  the F4 row at `:42`, r29 to the F3 row at `:41`); the append-only record is this section.
- `knowledge/jj-colocation-receipts.md` §3 marked the keep-ref timing `[INFERENCE]` and its
  `Limits` first bullet said the docs read do not state the lifetime. The r30 entry now carries
  the measured timing (ref removed by `jj util gc` with the operation log still naming the
  commit); the r17 text stands as history and is not rewritten. What remains unmeasured is the
  object-prune clock, not the ref's removal.
```

---

## 3. `PROVINCE.md` — append after line 193 (end of file)

```markdown
## Round 30 boundary note (F1 keep-ref expiry)

F1 now holds a measured entry — `corpus/knowledge/jj-keep-ref-expiry.md` — beside the four
entries its map row at `corpus/README.md:39` already named. One entry does not promote F1 to
Core: Core stays the `## Owns` and `## Work surfaces` list above (`:60`), the F1 row keeps the
status `frontier, entries held`, and this round adds nothing to either list. What the entry
records is the git-side lifetime of a keep ref: `git gc --prune=now` leaves a `refs/jj/keep/*`
ref in place, `jj util gc --expire=now` removes the ref of an abandoned commit while an
operation still names it, `jj op abandon ..@-` before a second `jj util gc --expire=now` leaves
two keep refs where eight stood, and the two-week default is the threshold that keeps a ref
until the lever is pulled. What it does not
record: jj's own store GC stays out of scope — this lane runs neither `jj op abandon` nor
`jj util gc` on a lane repository, acquires no authority to, and leaves the operator's store
alone; the object-prune clock that follows a dropped keep ref is unmeasured here; and no
receipt tool changes, so the r17 receipt rules stand unchanged. Certification OFF, K5 HELD.
Sources: `census/round-30/records/preregistration.txt` claim C3; the entry and its Gate; the
run record `census/round-30/records/jj-keep-expiry-run.txt`.
```

---

## 4. `SKILL.md` — one bullet in `## Error patterns (false-SAFE signatures)`

Insert as a new bullet immediately after the bullet that begins
`- **jj: unbookmarked / keep-only content is invisible to branch queries**` (currently line 114),
before `- **jj: nested `.git` → phantom deletions**` (line 115).

```markdown
- **jj: a keep-only commit's lifetime is the operation log's, not the ref's** (r30, F1): `git gc --prune=now` leaves a `refs/jj/keep/*` ref naming an abandoned commit in place, while `jj util gc --expire=now` removes that ref and `jj op abandon ..@-` before a second `jj util gc` leaves two keep refs where eight stood; the commit object stayed present at every step, so a dropped keep ref is not a deleted object. The default threshold is two weeks ("By default, only obsolete objects and operations older than 2 weeks are pruned." — `jj util gc --help`, jj 0.45.1) and `--expire` accepts only the string `now`, so an unrun `util gc` keeps a keep-only head alive and a kept ref is not evidence the content is reachable from a durable root. Facts, source rows and limits: `corpus/knowledge/jj-keep-ref-expiry.md`; recheck `bash tests/fixtures/r30-jj-keep-expiry.sh`.
```

---

## Out of scope for this delivery (named, not drafted)

- `SKILL.md` `## Gate registry` row for `r30-jj-keep-expiry` — the C3 counter reads the entry's
  Gate and the fixture, not the registry; a registry row is a separate landing with its own
  verdict map.
- `corpus/SOURCES.md` rows — assigned by the L1 at integration; this delivery cites no S-id so
  the entry's `source:` line stays the single authority.
- `corpus/lessons/round-30.md` and the README sections for C1/C2 — other seats.
