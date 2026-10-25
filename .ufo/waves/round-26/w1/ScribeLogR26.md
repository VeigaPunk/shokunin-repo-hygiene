# ScribeLogR26 — Round 26 LOG.md block (delivery + report)

Deliverable: `.ufo/waves/round-26/w1/log-r26.md` (full paste-ready LOG.md Round26 block,
mirroring the Round25 block shape, every `RECEIPT-PENDING` named).

## Status

STATUS: PARTIAL — the block is drafted with measured literals, but two frozen-counter conflicts
must be resolved by L1 before the block is true: C2's K2 gate check is RED at the tip
(`entries=2 ok=0 … fail=2`, rc 1), and C3's K2 prints `cases=11 pass=11`, not the frozen
`cases=12 pass=12`. Wave/dead-seat totals and admission verdicts remain `RECEIPT-PENDING`.

## Evidence

All commands run from `/home/vgpnk/Projects/shokunin/souji-shokunin` (fleet root is the tool start
dir, so every path below is the lane path). Lane base
`0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; measurement tip
`ba8b54b85814dd980aa96050fe111c7cbfd4956a`, 2026-10-25T17:32–17:33Z.

1. Freeze chain — `git log --oneline 0eca7c8..HEAD`:
   `12fd90b` freeze · `89e0fce` amendment 1 + red receipts · `bd6588c` wave evidence ·
   `965b869` amendment 2 · `a529c76` C1 integration · `4453128` C1 green receipt ·
   `0833de9` C3 tool+fixture · `d2e6253` C3 `--stub` arm · `e0f8dcd` C3 receipts ·
   `d6c13b0` C2 receipts · `ea0bbe6` lessons + Entry B · `d6fe8a1` SCORECARD EOF mapping note ·
   `07f83e6` C1 capability-row fix.

2. C1 counters — `bash census/round-26/c1-counter.sh`:
   base (`c1-before.tsv`, rev `12fd90bc…`): `markers=2`, `headings=17 175 231`
   tip (`c1-after.tsv`, rev `07f83e6…`, `utc=2026-10-25T17:32:37Z`): `markers=0`, `headings=17 44 78`
   Ordering holds (17 < 44 < 78). `SCORECARD.md` 261 lines; `### Round 26 append-only corrections`
   at :239; capability rows at :155-156; R3 note at :153; planned bullets at :201-202.

3. C2 counters — `bash census/round-26/c2-counter.sh`: `grounded_f1=2`, `registry_rows=132`
   (`c2-before.tsv` rev `89e0fce…`: `grounded_f1=0`, `registry_rows=127`).
   `python3 -B tools/souji-coverage-agreement.py --root . --rev ba8b54b… --base-rev 0eca7c8…`:
   `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, rc 0
   (base receipt `c2-k4-base.tsv`: `grounded=7 … kill_tested=7`).
   K3 `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`:
   rc 0, last line `souji\tok\t…/corpus/SOURCES.md`, 34 `W04` rows.
   K2 (frozen command, `--snapshot-dir census/round-26/sources --slice …/empty-slice
   --slice-verdicts …/empty-verdicts`): `FAIL … check1-no-gate` on both entries;
   `entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2`, rc 1 — run twice, at `ea0bbe6` and `ba8b54b`.

4. C3 counters — `bash census/round-26/c3-counter.sh` → `axis_check_tool=present`,
   `claims=3 flags=0`, `axis_check_exit=0` (receipt `c3-after.tsv`, rev `d2e6253…`).
   `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py` → `cases=11 pass=11`, rc 0.
   `python3 -B tests/fixtures/r26-axis-check.py --stub` → `cases=11 pass=4`,
   `control=FALSE-GREEN-REJECTED`, rc 1 (receipt `c3-control.tsv`, rev `d2e6253…`).
   Base: `axis_check_tool=absent` (`c3-before.tsv`, rev `89e0fce…`).
   `grep -c 'dict(id=' tests/fixtures/r26-axis-check.py` = 11.

5. SOURCES tallies, parsed from `git show <rev>:corpus/SOURCES.md`:
   base 127 rows, A=120/B=5/C=2, mined=103/queued=15/rejected=9, malformed 0, dup ids 0;
   tip 132 rows, A=125/B=5/C=2, mined=108/queued=15/rejected=9, malformed 0, dup ids 0.

6. Seats — `python3 -B` over `.ufo/waves/round-26/w1-spec.json` and `w1/swarm-registry.json`:
   both 87 items, roles 31 executor / 15 reviewer / 11 scribe / 10 scout / 9 critic /
   6 mutation-tester / 2 connector / 2 simplifier / 1 sentinel; `w1.ready.dispatched`
   `2026-10-25T14:15:44`; 41 `.md` deliverables under `w1/` at 17:33Z (grew from 10 → 23 → 29 → 41
   while this seat measured, so the count is a snapshot, not a total).

## Findings

1. **C2's frozen K2 is red at the tip.** Frozen command (prereg C2, K2) at `ba8b54b` prints
   `entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2`, rc 1, with
   `check1-no-gate: corpus/knowledge/git-auto-maintenance-trigger-set{,-r23}.md`. Cause is
   structural, not a receipt gap: neither entry has a `## Gate` heading
   (`corpus/knowledge/git-auto-maintenance-trigger-set.md` headings are `## Claim (F1…)` at :10,
   `## What this does NOT establish` :37, `## Lane link and consequence` :54, `## Freshness` :62;
   Entry B likewise has no Gate). The round lesson Gate (`corpus/lessons/round-26.md:9`) is not what
   the tool reads. `census/round-26/records/c2-gate.tsv` and `c2-k4-after.tsv` are absent from
   `census/round-26/records/`.
2. **C3's frozen K2 literal cannot be produced by the landed fixture.** Prereg demands one line
   `cases=12 pass=12 control=FALSE-GREEN-REJECTED`; `tests/fixtures/r26-axis-check.py:73` defines 11
   `CASES`, the real arm prints `cases=11 pass=11` with no control token, and the control token
   appears only in the separate `--stub` arm (`cases=11 pass=4`). Subject of `0833de9` already says
   "11-case fixture", so this is a landed-vs-frozen mismatch, not a measurement guess.
3. **Commit subject ≠ content for C2.** `0833de9` is titled `round-26 C3: …` yet `git show --stat`
   lists the entire C2 surface: `corpus/SOURCES.md` (+5), both knowledge entries,
   `corpus/README.md`, `census/round-26/sources/*` (+7 snapshots, `SHA256SUMS`). C2's green counter
   receipt also binds `rev=e0f8dcd…`, a commit whose subject is a C3 receipts commit.
4. **Lesson § Receipts contradicts the receipt files.** `corpus/lessons/round-26.md` § Receipts says
   `c1-after.tsv (a529c76 …)`; the file records `rev=07f83e6…` with `utc=2026-10-25T17:32:37Z`.
   It says `c2-after.tsv (d6c13b0 …)`; the file records `rev=e0f8dcd…`. Same file says the C3
   fixture is "11-case", contradicting the prereg's 12-case set.
5. **`QUALITY` Q59 is not landed.** `grep -c Q59 corpus/QUALITY.md` = 0. The prereg names Q59 as
   C3's fix deliverable; the row text exists only as a draft in
   `.ufo/waves/round-26/w1/axis-check-docs.md:30`, and `corpus/lessons/round-26.md` has no mistakes
   table (headings: Gate, Findings, Residuals, Receipts), so R26-M1 has no lesson row.
6. **C1's protected span 5 landed late, after its green receipt.** At `d6fe8a1` the counter printed
   `markers=0 headings=17 44 78` while `grep -c '^| debris census (r24) |' SCORECARD.md` = 0 and
   `… | coverage-map agreement (r24) |` = 0; both rows appeared only in `07f83e6` (:155-156). The
   prereg's C1 K1/K2 predicates cannot see this; amendment 2's span-5 byte diff is the only guard,
   and the green receipt was then refreshed at `07f83e6` (17:32:37Z).
7. **`considerthese/` absent** in the lane (`ls -d considerthese` → no such file or directory),
   matching the prereg's one-report-line requirement.
8. **Receipts are pinned at intermediate revs, not one tip.** `c1-after` at `07f83e6`,
   `c2-after` at `e0f8dcd`, `c3-after`/`c3-control` at `d2e6253`, current tip `ba8b54b`. The prereg
   says "green-after: … at the landing tip"; whether `07f83e6`/`d2e6253` are the intended landing
   revs is L1's call. The C1 counter re-run at `ba8b54b` reproduces `markers=0 headings=17 44 78`.
9. **Zero-byte `records/empty-slice` and `records/empty-verdicts`** are the inert slice arms the
   prereg names; they carry no `receipt=` header by design. `c3-control.tsv` and `c3-after.tsv` do
   carry `receipt=v1` with matching `tool_sha256=b60bcede…` and their own argv labels.

## Attack log

- **A1 — C1 counter is blind to the amendment-2 payload it is supposed to protect.** Witnessed at
  `d6fe8a1`: `markers=0 headings=17 44 78` (both frozen predicates green) with both r24 capability
  rows missing from `SCORECARD.md`. A seat could delete span-5 payload and keep C1 green; only a
  byte-diff of the seven amendment-2 spans catches it. No predicate is proposed for change here —
  the prereg's K1/K2 literals are frozen; this is the attack, for the canonical judge.
- **A2 — C3's control token is separable from the fixture score.** `control=FALSE-GREEN-REJECTED`
  is emitted only under `--stub`, where `pass=4`; the real arm prints no control token. A reader
  taking the real-arm line alone cannot tell the control ran. The frozen K2 line (`cases=12 pass=12
  control=…`) was designed to bind both in one output; the landed fixture does not.
- **A3 — frozen target re-derivation holds.** Amendment 1's corrected `grounded=9/kill_tested=7` is
  what the frozen K4 command actually reports at `ba8b54b` (`grounded=9 … kill_tested=7`,
  `kill_violations=0`), and `c2-k4-base.tsv` at `0eca7c8` reports `grounded=7`. The Q58 catch is
  reproducible, not merely asserted.

## Scope

No product code, receipts, SCORECARD, LOG, QUALITY, README or lesson file was written by this seat;
only `.ufo/waves/round-26/w1/log-r26.md` and this report. No `git add/commit/push/stash/checkout/reset`,
no `jj` mutation, no `rm`/`mv`, no signals, no `agent://all`. No tool installs or updates (nothing
needed: `git`, `gawk`, `python3` sufficed; pacman untouched). Scratch used under
`/var/tmp/souji-r26-ScribeLogR26/` and `/var/tmp/souji-r26-ScribeLogR26-SOURCES-*.tsv`, removed
before finish. Out of scope and untouched: `/home/vgpnk/Projects/shokuknow` (read only through the
staged rows already in the lane and the renumber map), `/home/vgpnk/Projects/shokunin/.scratch/`,
`.ufo/state/`, `watchdog.log`, `MANIFEST.json`, fleet `scripts/`, `templates/`, sibling lanes.
