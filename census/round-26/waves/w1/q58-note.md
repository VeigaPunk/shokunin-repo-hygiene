# Q58 note — amendment 1: C2's K4 target copied from r25's base (round 26)

Seat: `ScribeQ58Note`. Draft text for `LOG.md` (the round-26 entry) and
`corpus/lessons/round-26.md` (§ Process deviations, § Mistakes table). Nothing
here is landed; L1 applies it. Revisions in play: freeze `12fd90b`
(2026-10-25 14:04:30 -0300), amendment 1 `89e0fce` (14:07:27), wave dispatch
`bd6588c` (14:15:40), first green receipt `4453128` (14:19:16). Landing state
observed at lane tip `166baa1` (the tip advanced from `0c92c2e` mid-run; L1
landed `33e6807`, `9a6e0f1`, `166baa1`).

## 1. LOG.md paste block

Place as its own paragraph inside the round-26 LOG entry, after the
three-claims/amendments paragraph. The round-26 entry is not landed:
`grep -c -i 'round 26\|round-26' LOG.md` prints `0` (rc 1) at `166baa1`; the
current last heading is `LOG.md:1735` (`### Round25 final evidence addendum`).

> Q58 catch (amendment 1, pre-data). The freeze `12fd90b` set C2's K4
> after-target to `grounded=8 … kill_tested=6` — the round-25 base count of six
> grounded entries (`a6d2d15`) plus this round's two admitted entries — without
> re-deriving the count at this round's own base. Between those bases the round-25
> landing `728b2ce` (the r25 C3 candidate tip) grounded a seventh entry,
> `corpus/knowledge/git-repo-structure-common-dir.md` (ground F2), so the frozen
> counter at `0eca7c8` prints `grounded=7 mapped=7 dangling=0 mismatches=0
> kill_tested=7 kill_violations=0` (`census/round-26/records/c2-k4-base.tsv`,
> utc `2026-10-25T17:06:13Z`, 74 s before the amendment commit). Amendment 1
> (`89e0fce`, 14:07:27 -0300) corrected the target to `grounded=9` /
> `kill_tested=7` and the do-nothing control from `grounded=6` to `grounded=7`.
> No predicate, case set or axis changed. This is the R25-M1 class — a target
> copied from a different base — caught before any seat scored: the amendment
> commit precedes wave dispatch (`bd6588c`, 14:15:40) and the first green receipt
> (`4453128`, 14:19:16).

## 2. Lesson text

At `166baa1` the lesson has sections Gate (9), Findings (30), Residuals (66),
Receipts (81), Mistakes table (93); it has no `## Process deviations`, and its
`## Mistakes table` holds a single bullet, `R26-M1` at `:95`.

### 2a. `## Process deviations` — one line (the requested note)

New section, placed before `## Gate` at `corpus/lessons/round-26.md:9` (round-25
lesson order: Process deviations precedes Gate):

- Amendment 1 was logged at `89e0fce` (2026-10-25 14:07:27 -0300), before wave
  dispatch `bd6588c` (14:15:40) and before the first green receipt `4453128`
  (14:19:16), so no seat had scored claim data when C2's K4 target was
  corrected; the base re-derivation receipt `c2-k4-base.tsv` (rev `0eca7c8`) is
  committed in that same commit.

### 2b. `## Mistakes table` — bullet (primary paste)

Append under `## Mistakes table` (`corpus/lessons/round-26.md:93`), after the
`R26-M1` bullet at `:95`, matching that bullet's shape:

- R26-M2 (number-drift; Q58 catch, pre-data): C2's K4 after-target copied the
  round-25 base count of six grounded entries (`a6d2d15`) plus this round's two
  admitted entries instead of re-deriving the count at this round's base. The
  round-25 landing `728b2ce` had grounded a seventh entry
  (`corpus/knowledge/git-repo-structure-common-dir.md`, ground F2), so the frozen
  counter at `0eca7c8` prints `grounded=7 mapped=7 dangling=0 mismatches=0
  kill_tested=7 kill_violations=0`; the target should be `grounded=9` /
  `kill_tested=7`, not `grounded=8` / `kill_tested=6`. Amendment 1 (`89e0fce`,
  before wave dispatch `bd6588c`, before any green receipt) corrected the
  after-target and the do-nothing control (`grounded=6` → `grounded=7`); no
  predicate, case set or axis changed. Witness SHOWN: re-running the frozen K4
  command at `0eca7c8` with `--base-rev 0eca7c8` prints `grounded=7 … kill_tested=7`
  (rc 0) — one above the copied base count of six and one under the copied
  target of eight.

### 2c. Word-table row (only if the wave draft `.ufo/waves/round-26/w1/lesson-r26.md:52` lands instead)

That draft already carries an `R26-M2` row for the same defect; keep one row,
not two. If a table shape is wanted, this row replaces it (it adds the
`a6d2d15` → `728b2ce` provenance and the arithmetic):

| id | class | evidence | captured-by | fix | failure witness |
|---|---|---|---|---|---|
| R26-M2 | number-drift (Q58 catch) — C2's K4 after-target copied the round-25 base count instead of re-deriving the count at this round's base | Freeze `12fd90b` literal `grounded=8 … kill_tested=6` equals r25 base six grounded at `a6d2d15` plus two admitted entries; r25 C3 landing `728b2ce` added a seventh grounded entry (`git-repo-structure-common-dir.md`, ground F2), so the frozen counter at `0eca7c8` prints `grounded=7 … kill_tested=7` (`census/round-26/records/c2-k4-base.tsv`) | Q58 (`corpus/QUALITY.md:142`) — caught pre-data, before any seat scored | Amendment 1 (`89e0fce`) corrected the target to `grounded=9` / `kill_tested=7` and the do-nothing control to `grounded=7`; predicate, case set and axis unchanged | **SHOWN**: frozen literal says eight grounded and kill_tested six; re-running the frozen K4 command at `0eca7c8` with `--base-rev 0eca7c8` prints `grounded=7 … kill_tested=7` (rc 0), so the copied base count was one low (6 vs 7) and the target one short (8 vs 9) |

## 3. Witness and provenance (executed this run)

- Frozen literal: `git show 12fd90b:.ufo/waves/round-26/preregistration.txt | grep -n 'grounded=\|K4 grounded'` → line 116 `After value: grounded=8 mapped=8 dangling=0 mismatches=0 kill_tested=6` (with `kill_violations=0` and `the 6 base-grounded entries` on line 117) and line 136 `DO-NOTHING CONTROL: base bytes left untouched score K1=0 and K4 grounded=6.`
- Base count re-derived by execution: `python3 -B tools/souji-coverage-agreement.py --root . --rev 0eca7c8… --base-rev 0eca7c8…` → `grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, rc 0; committed receipt `census/round-26/records/c2-k4-base.tsv` (`rev=0eca7c8…`, `rc=0`, `utc=2026-10-25T17:06:13Z`) is byte-equal on the counts line; tool `sha256 bb506469be86…` matches its `tool_sha256`.
- Entry count at r25 base: `git grep -l '^ground: F' a6d2d15775… -- corpus/knowledge/ | wc -l` → `6`.
- Seventh entry: `git log --diff-filter=A -- corpus/knowledge/git-repo-structure-common-dir.md` → `728b2ce 2026-10-25 10:25:55 -0300 round-25: integrate claims, sources, lessons and wave evidence`; its `ground: F2` is at `:6` in the base blob.
- Amendment diff: `git show 89e0fce -- .ufo/waves/round-26/preregistration.txt` removes the `grounded=8 … kill_tested=6` after-literal and adds `Base value … grounded=7 … kill_tested=7` plus `After value: grounded=9 … kill_tested=7`; control line `grounded=6` → `grounded=7`. No predicate, case-set or axis line in the diff. Commit stat includes `census/round-26/records/c2-k4-base.tsv`.
- Pre-data ordering: `git log --format='%h %ci %s' 12fd90b~1..HEAD` → `12fd90b` 14:04:30 (freeze), `89e0fce` 14:07:27 (amendment 1), `bd6588c` 14:15:40 (wave spec/dispatch), `a529c76` 14:18:42 (first claim integration), `4453128` 14:19:16 (first green receipt). No after-data commit precedes `89e0fce`.
- Landing surfaces at `166baa1`: `git show HEAD:corpus/lessons/round-26.md | grep -n 'R26-M1'` → `95:`; no `Process deviations` or `R26-M2` in that blob (grep rc 1); `git show HEAD:corpus/QUALITY.md | grep -n '^| Q59'` → `143:`; `git show HEAD:LOG.md | grep -c -i 'round 26\|round-26'` → `0`.

## 4. For L1 (not part of the pasted text)

- The contract names `89e0fce` as the lane commit at which claims were frozen, but
  the freeze commit is `12fd90b` and `89e0fce` is the amendment commit; the
  prereg header's "Frozen at: this file's landing commit" therefore resolves to
  the amended bytes. The stale literals exist only at `12fd90b`, which is why
  this note cites that revision rather than the frozen-at name. The report
  should state both.
- `LOG.md` still carries no round-26 entry at `166baa1`, though the prereg's
  amendment rule requires the LOG record: the paste in § 1 is `RECEIPT-PENDING`.
- Q59 is landed (`corpus/QUALITY.md:143`, commit `166baa1`); Q58's own provenance
  cell (`:142`) still cites only R25-M1. Adding R26-M2 there would extend the
  criterion's witness list; that edit is not in any claim's write scope and is
  left to L1.
- The tip moved under this seat (`0c92c2e` → `166baa1`) while other seats were
  writing. Every literal above is anchored to a named revision, not to the tip,
  so none of them depends on the moving state.
