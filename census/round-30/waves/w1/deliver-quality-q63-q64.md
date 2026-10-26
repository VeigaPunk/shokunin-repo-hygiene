# Round 30 — draft QUALITY criteria Q63/Q64 + matching SKILL.md `## Gate registry` rows

Drafted by SwarmScribe18 (wave 1, leaf). **Not an integration**: the L1 inserts both blocks and decides
the SKILL.md patch note at the end. Nothing in `corpus/QUALITY.md` or `SKILL.md` was touched by this seat.

Layout sources read this run: `corpus/QUALITY.md:146-149` (round heading, blank, header, separator) and the
Q60/Q61/Q62 rows at `:150-152` (five columns `id`, `criterion`, `applies to`, `check`, `motivating evidence`);
`SKILL.md:178-179` (registry header `name`, `kind`, `entry command`, `verdict map`, `self-test command`,
`pinned-value path`, `write scope`, `owner`) and `:226-228` (last three rows; table ends at 228).

## 1. `corpus/QUALITY.md` — insertion

Append after line 152 (Q62, the last row of the `## Round 29 criteria` table), as a new block of the same
shape as `:146-149`. The two rows are column-identical to Q60-Q62, so they also append unchanged directly
under the r29 table if the L1 prefers that; no cell contains a pipe character.

```
## Round 30 criteria

| id | criterion | applies to | check | motivating evidence |
|---|---|---|---|---|
<Q63 row>
<Q64 row>
```

## 2. `corpus/QUALITY.md` rows (exact bytes)

| Q63 | A capability row's stated count is a literal the named command prints at the measured revision, re-run from committed bytes in a private clone, and a count that no longer agrees is corrected append-only: the base bytes stay and an `R30-CORRECTION SCORECARD.md:<line> <row-id> [cmd=<argv>] rc=<n> observed=<observed line>` line follows them, so the stale literal and the observed one are both legible and the correction must reproduce the re-run's `rc=` and `observed=`. The enumerated set is frozen at the preregistration commit (`--list-rev`), never re-derived at the measured revision, so a later commit cannot shrink it; an in-place rewrite of the literal fails the whole claim because the file no longer begins with its base bytes. Unresolved `SHONEN.md` pointer tokens take the same shape — `R30-CORRECTION SHONEN.md:<line> <token> -> <WITHDRAWN or same-basename blob>` — and the original token text stays. Prose agreement is not a measurement. | `SCORECARD.md` capability rows that state a count beside a runnable command; `SHONEN.md` pointer tokens; append-only `R30-CORRECTION` lines | `python3 -B tools/souji-capability-agreement.py --root <lane> --rev <full40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631` exits 0 only on `SUMMARY k1=0 k2=0 mismatches=0`; exit 1 prints one `ROW`/`PTR` line per item, each tagged `MATCH`, `RESOLVES`, `MISMATCH`, `MISMATCH(append-only-violated)` or `CORRECTED`, and `mismatches=` counts only the two `MISMATCH` forms, so a `CORRECTED` or `MATCH` line is not a failure but must still be printed; exit 2 is could-not-evaluate (usage, non-40-hex or unresolvable rev, `census/round-30/c1-rows.tsv` absent at `--list-rev`). Red arm: the same command at `--rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` prints `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10`, rc 1 (7 value, 5 shape, 1 rc); `--only R05,R10` prints `mismatches=2 rows=2 partial=1`, rc 1, and is diagnostic only — `partial=1` never satisfies the check | `corpus/lessons/round-30.md` `## Findings` (C1: 13 of 18 capability rows disagree with the command they cite); `census/round-30/records/c1-before.txt` (per-row before-run); the enumeration and exclusion rule in `census/round-30/c1-rows.tsv:1-6`; `census/round-30/records/preregistration.txt` C1 |

| Q64 | The landing gate reads a round's committed capture when the round's reports are not committed: with `census/round-N/waves/**.md` committed and no `.ufo/waves/round-N/` in the revision, it reports `checked_reports` equal to the capture's `.md` count and emits no could-not-evaluate, and when both exist it reads `.ufo/waves/round-N/` and does not double-count the capture copy of the same report. A `.ufo/waves/round-N/w1/X.md` citation resolves through `census/round-N/waves/w1/X.md` only for the pointer's own round number — a same-basename file captured for another round does not resolve it — and semantic template tokens (`round-%s`, `round-<N>`, `round-{N}`) are not pointers, while a real missing path in the same file is still a finding. A capture-only report carrying an uncarried `STATUS: FAIL` line is flagged, never silently clean. | `tools/souji-landing-gate.py` report discovery; `census/round-N/waves/` captures; `.ufo/waves/round-N/` pointer and template-token handling | `python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py` exits 0 only on `cases=7 pass=7 control=FALSE-GREEN-REJECTED`; exit 1 on any `CASE D<k> FAIL` line or `control=FALSE-GREEN-ACCEPTED`; exit 2 on a missing prerequisite (tool absent, no git, TMPDIR unset or inside a git checkout). The seven cases are D1-D7 of the fixture docstring; the control is an always-zero emitter printing one clean `findings=0 checked_reports=0` SUMMARY, which must fail at least one case, so a gate that is clean only because it read nothing cannot pass. Red arm: the base gate at `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` prints `cases=7 pass=3 control=FALSE-GREEN-REJECTED`, rc 1, failing D1 (capture-only round not discovered), D4 (`round-%s` and `round-{N}` flagged), D6 (capture-mapped pointer not resolved) and D7 (capture-only `STATUS: FAIL` not surfaced) | `corpus/lessons/round-30.md` `## Mistakes` (r29's lesson could not carry seat `STATUS: FAIL` lines because the gate read only the gitignored `.ufo/waves/`); `corpus/lessons/round-29-verifier-spotcheck.md:131-132` (routed defect 4: `findings=2` false positives on `round-%s` plus `COULD-NOT-EVALUATE` for a committed round); `census/round-30/records/preregistration.txt` C2 fixture contract D1-D7; red arm `census/round-30/waves/w1/deliver-c2-fixture-red-before.txt` |

Note for the L1: both rows cite `corpus/lessons/round-30.md` sections that the lesson's author still owes
(`## Findings`, `## Mistakes`; the file today carries the head, the reading line and nothing else). If the
lesson lands with different section names, adjust only that cell — the committed receipts named beside it
(`c1-before.txt`, `:131-132`, the capture) keep the row checkable.

## 3. `SKILL.md` `## Gate registry` — rows (exact bytes, append after line 228)

| souji-capability-agreement | gate | `python3 -B tools/souji-capability-agreement.py --root LANE --rev REV --base BASE --list-rev PREREG` | 0 `SUMMARY k1=0 k2=0 mismatches=0`; 1 one `ROW`/`PTR` line per item, tagged `MATCH`, `RESOLVES`, `MISMATCH`, `MISMATCH(append-only-violated)` or `CORRECTED`, with only the two `MISMATCH` forms counting against the target; 2 could-not-evaluate (usage, non-40-hex or unresolvable rev, `census/round-30/c1-rows.tsv` unreadable at `--list-rev`). Reads `git cat-file` and a `git clone --no-local` of `--root` at REV: the working tree is never consulted, and a rewrite of a base literal fails closed | no separate fixture; discriminating arms — frozen base `--rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631` → `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10`, rc 1; diagnostic `--only R05,R10` → `mismatches=2 rows=2 partial=1`, rc 1; the round's landing tip must print `k1=0 k2=0` | `census/round-30/c1-rows.tsv` (frozen 18-row plus 10-pointer enumeration, rule in its header); `census/round-30/records/c1-before.txt`; correction literals `R30-CORRECTION SCORECARD.md:<line> <row-id> ... rc=<n> observed=<line>` and `R30-CORRECTION SHONEN.md:<line> <token> -> <target>` | read-only on `--root`; each row runs as an argv list (no shell) in a private per-row clone under `--scratch` with `checkout -f` and `clean -fdxq`; TMPDIR is a fresh per-row directory; no lane write | souji |
| r30-landing-gate-discovery | gate | `python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py` | 0 `cases=7 pass=7 control=FALSE-GREEN-REJECTED`; 1 any `CASE D<k> FAIL` or `control=FALSE-GREEN-ACCEPTED`; 2 missing prerequisite (tool absent, no git, TMPDIR unset or pointing inside a git checkout) | same default invocation; paired red arm is the base gate at `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` → `cases=7 pass=3 control=FALSE-GREEN-REJECTED`, rc 1 (D1 D4 D6 D7 FAIL), and the always-zero-emitter control must fail at least one case | fixture `CASES` D1-D7 with their per-case assertions and the control emitter; `census/round-30/records/preregistration.txt` C2; red arm `census/round-30/waves/w1/deliver-c2-fixture-red-before.txt` | synthetic git repositories under a private directory in `$TMPDIR`, removed in `finally`; the gate's own `/var/tmp` parse snapshot; never a lane checkout | souji |

## 4. Advisory patch to the existing `souji-landing-gate` row (`SKILL.md:198`) — L1 decision, not a delivery

Q64 changes that row's inputs, so leaving 198 untouched would state an entry contract the gate no longer
obeys at round >= 30. Two cell additions, no pipe characters:

- verdict map, appended after the `LG-DANGLING-PTR-EXEMPT-STALE` clause: `at round >= 30 report discovery also reads the committed census/round-N/waves/ capture when .ufo/waves/round-N/ is absent from the revision, a .ufo/waves/round-N/ pointer resolves through the capture of its own round, and template tokens (round-%s, round-<N>, round-{N}) are not pointers`.
- self-test column, appended: `external discovery contract tests/fixtures/r30-landing-gate-discovery.py (D1-D7 plus always-zero-emitter control); selftest alone does not cover discovery`.

## 5. What was exercised here (red-before only), and what was not

Observed this run against the lane at `df6afe817d096e4ad71ba2b9cc21a83f126eb658` (working tree clean except
the untracked `corpus/lessons/round-30.md`):

- `python3 -B tools/souji-capability-agreement.py --root <lane> --rev 9420341d… --base 9420341d… --list-rev d4928ec8…`
  → `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10`, rc 1, 31 s (scratch clone per row under `/fast/scratch/hyaku/souji-r30/SwarmScribe18/`).
- `python3 -B .ufo/waves/round-30/w1/deliver-r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py`
  → `cases=7 pass=3 control=FALSE-GREEN-REJECTED`, rc 1, D1/D4/D6/D7 FAIL, 1 s; output byte-identical in
  substance to `deliver-c2-fixture-red-before.txt`.

Not exercised, and not claimed: the green arms. `tests/fixtures/r30-landing-gate-discovery.py` does not exist
in the lane yet (the fixture lives at `.ufo/waves/round-30/w1/deliver-r30-landing-gate-discovery.py`), so the
Q64 check as written currently exits 2 on a missing prerequisite; and `k1=0 k2=0` needs the wave-2
`R30-CORRECTION` lines landed. `[INFERENCE]` both become green only after the L1 integrates wave 1 and wave 2;
the fixture's own docstring (`exit 0 iff every case passes and the control is rejected`) is the only basis for
the expected green line.
