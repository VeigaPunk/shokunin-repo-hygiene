# round 32 attempt 2, wave a2w1 — ready-to-append SCORECARD, Planned and LOG blocks (scribe delivery)

Seat: SwarmScribe33. Lane read-only: nothing below was committed, and no lane file was edited.

Every reading below was read from a committed file at lane tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`
(branch `master`) and is cited by path and line. `rev=` inside a quoted SUMMARY is the revision that SUMMARY
names; it is not the revision of the file name. `<L1>` is the L1's to fill from the record named beside it —
never from a dispatch spec, a wave count, or a previous round's text.

Frozen inputs opened this run: `census/round-32/records/preregistration.txt` (3ec84fc8), `controls.tsv:2-4`,
`controls-a0.tsv:2`, `amendments.txt` (A0 at 7a6667cd, A1 at a92e1aae), `m1-red-before.txt`,
`c3-after-v1.txt`, `c3-after-v2.txt`, `c1-after-v1.txt`, `c1-after-v2.txt`, `c2-after-v1.txt`,
`a2-l1-salvage-tip-measure.txt`, `census/round-32/c2-items.tsv`, `census/round-32/measure.sh`,
`corpus/knowledge/jj-abandoned-object-mtime-clock.md`, `census/round-32/records/jj-mtime-clock-run.txt`,
`census/round-32/c3-contract.txt`, `corpus/SOURCES.md:168`, `.ufo/waves/round-32/w1/SwarmCritic34.md`,
`SwarmExecutor04.md`, `SwarmExecutor05.md`, `.ufo/waves/round-32/w2.ready.dispatched`.

---

## 1. SCORECARD.md — `### Round 32 measurements`

Insert at the end of `SCORECARD.md` (the file is 471 lines at `4e56c48`; last block is
`### Round 32 capability-count bindings`). Append-only: do not edit the block above. Columns are
`### Round 31 measurements`'s.

```markdown
### Round 32 measurements (2026-10-26; base 85b61a151923986e7e6b48f7084b9122561b5f3d; preregistration 3ec84fc81b3243429c834a051880b0bcde06291c; amendments 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 (A0), a92e1aae91dbf46c2d7eff713932cfc820186970 (A1))

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 capability-count literal binding (44 items: N01-N43, the integers the r31 `N/M` notation skipped, plus r31's unbound L29) | calibration 7 | `SUMMARY items=44 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=44 mismatches=44` (do-nothing control at the prereg, identical under v1 and A0 v2) | at the C1 landing commit `SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6`, identical under v1 and v2: **missed** the frozen target `unbound=0 mismatches=0 withdrawn<=8` on two counts — 6 items stay unbound (N28, N29, N30, N31, N33, N34, all `SCORECARD.md:422`) and 17 rows are withdrawn against a cap of 8; 38 of 44 items carry a row (21 bound, 17 withdrawn), and the six refusals are rule-level, not stale counts (the cell's integers are right) | `bash census/round-32/measure.sh <rev> c1` (runs `python3 -B census/round-32/c1-counter.py` and `c1-counter-v2.py` with `--root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --scratch $S/c1{,v2}`) | `census/round-32/records/c1-after-v1.txt:46`, `c1-after-v2.txt:46`; landing 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93; the same reading at the salvage tip in `a2-l1-salvage-tip-measure.txt:48` and `:95` (rev 4e56c48b8fc828f9aba2746e324dc46aa538bdbf) |
| C2 sandboxed scratch discipline (27 items T01-T12, T15-T27, T29, T30 over 22 committed files) | operability 8 | `SUMMARY items=27 pass=1 fail=26` | at the C2 landing commit `SUMMARY items=27 pass=26 fail=1`: **missed** the frozen target `fail=0` on T18 (`python3 -B tests/fixtures/r20-input-binding.py --baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812`), whose anchor line embeds `baseline_mismatches=` — 26 in the base run, 31 in the read-only-`/tmp` run, because the count is of closure files that differ from a pinned 2026-10-21 revision and this round's own edits to those files move it; the other 26 items keep the base exit code, base last digit-bearing line and at least half of base's file-creating syscalls. Re-measured at the salvage tip: `pass=25 fail=2` (T12 joins T18) | `bash census/round-32/measure.sh <rev> c2` (runs `python3 -B census/round-32/c2-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --scratch $S/c2`) | `census/round-32/records/c2-after-v1.txt:17` (T18; SUMMARY `:29`); landing 98e5203d45b4e419a9e72801733d93303acc7ebd; salvage-tip re-measure `a2-l1-salvage-tip-measure.txt:109` (T12), `:113` (T18), `:125` (SUMMARY, rev 4e56c48b) |
| C3 F1 abandoned-object mtime clock (jj 0.45.1, git 2.56.0) | coverage 8 | `SUMMARY legs=14 fail=13 f1_entries=4` | at the C3 landing commit v1 `SUMMARY legs=14 fail=0 f1_entries=5` and under A1 v2 `SUMMARY legs=17 fail=0 f1_entries=5`: **met** both targets; the record's 22 `RESULT` lines replay identically, the PATH shim logs 32 jj calls and 368 git calls under v1 (`c3-after-v1.txt:13`) and 32 and 366 under A1 (`c3-after-v2.txt:13`), both subtraction mutants differ from the record, and A1's plain-git probe (recent unreachable object survives a default `git gc`, old one does not) agrees with the record's recent/old lines; both readings hold at the salvage tip in the same notation | `bash census/round-32/measure.sh <rev> c3` (v1); `python3 -B census/round-32/c3-counter-v2.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --scratch $S/c3v2` — note `measure.sh` has no C3-v2 leg | `census/round-32/records/c3-after-v1.txt:16`, `c3-after-v2.txt:19`; landing a92e1aae91dbf46c2d7eff713932cfc820186970; salvage tip `a2-l1-salvage-tip-measure.txt:142` (v1), `:167` (v2, rev 4e56c48b) |

Owned scores unchanged (calibration 7, coverage 8, operability 8): C3 met its frozen target at the landing commit and at the salvage tip, but coverage 8 is the saturation line and C1 — the lowest-axis obligation, calibration 7 — missed again, so no calibration evidence accrued and no reproducible 0-10 mapping exists. C2 missed its frozen kill rule at the landing commit (T18) and at the salvage tip (T12, T18), so no operability evidence accrued; the 26 fixed items are capability evidence, not claim evidence. No round admission is claimed; the non-author closure rules. The final-tip re-measurement of all three claims under v1, A0 and A1 is committed in the records directory right after this table lands (`<L1: final-tip record>`).
```

Two fill rules for the L1:

1. The `after` cells above are the landing-commit readings only. If the L1's final-tip run differs by even one
   integer, write the tip reading as a second sentence in the same cell with its own record name — do not edit
   the landing reading.
2. `measure.sh` runs C1 v1+v2, C2 and C3 v1 only (`census/round-32/measure.sh:11-20`, 20 lines). The A1 v2 reading comes
   from a separate `c3-counter-v2.py --scratch` invocation; if the L1 adds a `c3v2` leg to `measure.sh` before
   the tip measurement, the command cell's second half should be replaced by the new leg, and the amendment is
   stricter-only (no target change).
3. Every citation to `census/round-32/records/a2-l1-salvage-tip-measure.txt` (lines 48, 95, 109, 113, 125, 142,
   147, 167) points at a file that is **untracked** at `4e56c48` (`git ls-files --error-unmatch` says it is not
   in the index). Either commit it with the round's records or replace those citations with the final-tip record
   before pasting; a SCORECARD cell may not rest on an uncommitted blob.

---

## 2. SCORECARD.md — `### Round 32 capability rows`

Four rows, `### Round 31 capability rows (appended)`'s columns. Admit each row only after re-running its
pointer at the landing revision; drop a row whose pointer cannot be re-run rather than ship `<...>`.

```markdown
### Round 32 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| sandboxed scratch-discipline gate (r32) | runs 27 self-contained lane commands under bwrap with `/tmp`, `/var/tmp` and `/dev/shm` read-only and `TMPDIR` a fresh scratch dir, and passes one only when it prints the base run's exit code and last digit-bearing line and still performs at least half of the base run's file-creating syscalls, so a tool that honours `TMPDIR` is told apart from one that stops working; 26 of 27 items now honour `TMPDIR` (27 files under `tools/` and `tests/fixtures/` changed) | base `SUMMARY items=27 pass=1 fail=26` (`census/round-32/records/controls.tsv:3`) -> landing `SUMMARY items=27 pass=26 fail=1` (`census/round-32/records/c2-after-v1.txt:29`); the one failing item T18 and its revision-sensitive `baseline_mismatches=` anchor are disclosed in the round table, and `census/round-32/records/amendments.txt`'s closing note records the wave-1 attack (`w1/SwarmCritic34.md`) that the frozen predicate also accepts a clone-local scratch and a fabricated anchor, disclosed there and not amended | r32 |
| jj mtime-clock fixture (r32) | a real jj 0.45.1 + git 2.56.0 fixture measuring how an abandoned commit object's own mtime decides its fate under `git gc` across arms recent, old, mixed, never and nocruft, including the clock carried per object inside a cruft pack; the record replays identically, a PATH shim proves the real binaries ran, and two subtraction mutants change the outcome | `TMPDIR=<scratch> bash tests/fixtures/r32-jj-mtime-clock.sh` -> `jj-version: jj 0.45.1-7c41cdeb…`, `git-version: git version 2.56.0` and 22 `RESULT arm=… step=… object_present=yes` (or `=no`) lines byte-identical to `census/round-32/records/jj-mtime-clock-run.txt`; `python3 -B census/round-32/c3-counter.py …` -> `SUMMARY legs=14 fail=0 f1_entries=5` (`census/round-32/records/c3-after-v1.txt:16`); mutants L13 M2/M3 differ with fewer `object_present=no` lines | r32 |
| record-contract check (r32, M1) | turns a frozen fixture field contract into a checkable predicate: every record line under the contract's prefix carries exactly its keys, in order, each value in its enumerated set; shown able to fail on the r31 record and wired into C3's L14, so the r32 record is checked at landing and at the tip | `python3 -B tools/souji-record-contract.py --record census/round-31/records/jj-object-clock-run.txt --contract census/round-32/m1-r31-contract.txt` -> `lines=17 bad=4`, exit 1, the four `arm=reflog-only` lines (`census/round-32/records/m1-red-before.txt`); r32 side `lines=22 contract_unchanged=True bad=[]` (`census/round-32/records/c3-after-v1.txt:15`) | r32 |
| C3 v2 independent probe (r32, A1) | re-derives a fixture record's central claim outside the record's own fixture: a plain-git probe of a recent and an old unreachable commit under a default `git gc` must agree with the record's recent/old lines and must not be produced by the record itself; also checks the shimmed calls' exit statuses and re-fetches every snapshot a receipt names | `census/round-32/c3-counter-v2.py` at the C3 landing commit -> `L15 PASS probe recent_present=True old_present=False record recent=yes old=no`, `L16 PASS abandon=7 nonzero=0 gc=6 nonzero=0 cat_file_e=44 rc0=38 results=22`, `L17 PASS refetched=4 bad=[]`, `SUMMARY legs=17 fail=0 f1_entries=5` (`census/round-32/records/c3-after-v2.txt:16-19`); A1's motive (a constants-printing fixture met v1) is in `census/round-32/records/amendments.txt` | r32 |
```

---

## 3. SCORECARD.md — `### Planned (appended at round 32)`

Append directly after the measurements block. Carries are the assignment's, in its order, each with the r32
record that shows why it is carried.

```markdown
### Planned (appended at round 32)

- **r33 (planned r32):** calibration: redesign the C1 enumeration so each item is one count *statement* rather than one digit run — unit words that carry no digit (`k1` makes `k1=13` unrepresentable, `SCORECARD.md:354`, N25), shared lines allowed with a per-statement occurrence (`SCORECARD.md:422` puts eight integers on two SUMMARY lines, which the one-row-per-`(path,line)` rule caps at two, N28-N31/N33/N34), and `withdrawn:` restricted to "no observable shows it" rather than used as a cap escape (17 rows against a cap of 8 at the landing commit, `census/round-32/records/c1-after-v1.txt:46`); the 6 unbound and 17 withdrawn r32 items are re-derived under the new rule, not dropped, since their integers are correct (`w1/SwarmExecutor05.md` Findings 1-5); operability: close the C2 v1 predicate gaps `w1/SwarmCritic34.md` reproduced — count only creations under the run's own `TMPDIR`, compare the whole stdout line multiset instead of the last line, bind `$HOME` and the clone read-only, apply a work floor to items whose base creates almost nothing (T03/T24), and either admit `tools/souji-vault-verify.sh --selftest` (`:742` `export TMPDIR="${TMPDIR:-/var/tmp}"`) and the `souji-round9-*` exporter or narrow the rule so it does not describe them; re-anchor the two revision- or run-sensitive items — T18's `baseline_mismatches=` count of files differing from a pinned 2026-10-21 revision (`census/round-32/records/c2-after-v1.txt:17`, 26 -> 31 at the landing commit, 26 -> 32 at the tip) and T12, whose base run reads `rc1 … 69 checks, 6 failed` in one committed record and `rc0 … 69 checks, 0 failed` for the same revision in another (`c2-after-v1.txt:13` vs `a2-l1-salvage-tip-measure.txt:147`), so neither item's verdict is reproducible; give `measure.sh` a C3-v2 leg so A1's `legs=17 fail=0` is re-derivable by the frozen runner; coverage: `<L1>` — no coverage carry is named in the attempt-2 assignment (C3 met v1 and A1 at the landing commit and at the salvage tip); residuals: the 54 uncarried seat-failure lines of rounds 15/19/23/24/25 (`LOG.md:1806`) are still uncarried after r32.
```

---

## 4. LOG.md — round 32 attempt 2 entry

Append after the round-31 entry (`LOG.md:1796-1806`), in that entry's shape. `<L1>` anywhere below is the L1's
own reading.

```markdown
## 2026-10-26 — Round 32 attempt 2: capability-count binding, sandboxed scratch discipline, F1 abandoned-object mtime clock

Preregistration 3ec84fc81b3243429c834a051880b0bcde06291c and controls 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 (base 85b61a151923986e7e6b48f7084b9122561b5f3d) before any seat data; start census rc 0 with 36 W04 duplicate-url warnings (`census/round-32/records/census-start.txt`, last line `souji ok`, `exit=0`). Attempt 1's L1 (SoujiR32) died in the orchestrator host crash (2026-10-26 ~08:50 -03) after wave 1 (44 seats, reports in `.ufo/waves/round-32/w1/`) and after landing C2, C3 and C1, but before its falsify wave ran: wave `w2` was never taken and the orchestrator marked it ABANDONED with no seat spawned (`.ufo/waves/round-32/w2.ready.dispatched`). Hyaku run 8's salvage commit 4e56c48b8fc828f9aba2746e324dc46aa538bdbf committed attempt-1's five after-records; attempt 2 re-derived every one of them at a named revision instead of carrying them, and the survivors agree with the counters. Wave-1 attacks had already forced stricter-only amendment A0 (C1 v2: cited evidence path on the item's base line, unit word adjacent to each integer) and A1 (C3 v2: plain-git probe, shim exit statuses, live snapshot re-fetch).
- C1 calibration (9e8982b7a6ac57dffa415f9db43cf7cd6e829c93): capability-count literals `items=44 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=44 mismatches=44` -> `bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6`, identical under v1 and A0 v2; 38 append-only binding rows (21 bound, 17 withdrawn) in `SCORECARD.md`. Missed by the frozen kill rule on two counts: six items (N28, N29, N30, N31, N33, N34 at `SCORECARD.md:422`) cannot be bound under the one-row-per-line rule while their eight integers stand on two SUMMARY lines, and 17 rows exceed the withdrawal cap of 8; the cell's integers themselves are correct, so the miss is a rule defect, not a stale count (`w1/SwarmExecutor05.md`).
- C2 operability (98e5203d45b4e419a9e72801733d93303acc7ebd): `items=27 pass=1 fail=26` -> `pass=26 fail=1`; 27 files under `tools/` and `tests/fixtures/` were changed so their scratch root comes from the caller's `TMPDIR` (the r20 fixture pair wraps a private `/var/tmp` backed by `TMPDIR`) (Python `tempfile` without a hard-coded `dir=`, shell `mktemp -d` under `${TMPDIR:?}`, child envs passing the caller's `TMPDIR`), and the r20 fixture pair runs inside a private `/var/tmp` backed by `TMPDIR`. Missed by the frozen kill rule on T18 (`r20-input-binding.py`), whose last line embeds `baseline_mismatches=` — 26 base, 31 sandboxed — a count of closure files that differ from a pinned 2026-10-21 revision, which this round's own C2 and C3 edits move; the predicate cannot hold for T18 while the round lands its work (`census/round-32/records/amendments.txt`).
- C3 coverage (a92e1aae91dbf46c2d7eff713932cfc820186970): `corpus/knowledge/jj-abandoned-object-mtime-clock.md` (`ground: F1`), row S223 new (`corpus/SOURCES.md` 146 -> 147, `corpus/SOURCES.md:168`), fixture `tests/fixtures/r32-jj-mtime-clock.sh`, record `census/round-32/records/jj-mtime-clock-run.txt` (22 `RESULT` lines, jj 0.45.1, git 2.56.0), four source snapshots with fetch receipts (`census/round-32/sources/`, `records/fetch-receipts.tsv`); `legs=14 fail=13 f1_entries=4` -> v1 `legs=14 fail=0 f1_entries=5`, A1 v2 `legs=17 fail=0 f1_entries=5`. Met both targets at the landing commit and at the salvage tip.
- Mined mistake M1 (r31 D1, contract class): `tools/souji-record-contract.py` turns a frozen fixture field contract into a check and prints `lines=17 bad=4`, exit 1 over the r31 record, the four `arm=reflog-only` lines (`census/round-32/records/m1-red-before.txt`); C3's L14 holds the r32 contract at the landing commit and at the tip (`lines=22 contract_unchanged=True bad=[]`).
- Routed r31 defects: D1 -> M1 and C3 L14; D2 append-only corrections for S051's cite, S063's anchor and the `gc.recentObjectsHook` quote landed with the C3 commit a92e1aae; D3 (landing-text discipline) `<L1: receipts under census/round-32/records/>`; D4 `<L1>`; D5 `/var/tmp` gate snapshots -> C2's `tools/souji-landing-gate.py` items (T01 selftest, T02 parse).
- Frontier: `corpus/SOURCES.md` 146 -> 147 rows, S223 opened this round with its snapshot and fetch receipt (tier A, git v2.56.0 `gitformat-pack.adoc`); census rc 0 at the start (`census/round-32/records/census-start.txt`) and `<L1: end census>`; F1 map row in `corpus/README.md` `## Round 32`, boundary note in `PROVINCE.md`; F1-grounded entries 4 -> 5.
- QUALITY Q70-Q72, SKILL gate-registry rows for the r32 instruments (`r32-c1-counter`, `r32-c2-counter`, `r32-c3-counter`, `r32-jj-mtime-clock`, `souji-record-contract`; drafts in `w1/deliver-quality-q70-q72.md`), README and PROVINCE text landed with C3, and the round lesson `corpus/lessons/round-32.md` `<L1>` (absent at 4e56c48). Waves: attempt 1 w1 44 seats (reports in `.ufo/waves/round-32/w1/`), attempt-1 w2 abandoned before dispatch; attempt 2 a2w1 `<L1: seat count>` seats `<L1: result payloads>`, reports in `.ufo/waves/round-32/a2w1/`.
Owned axis scores unchanged (calibration 7, coverage 8, operability 8). C3 met its frozen target but coverage is at the saturation line, and C1 — the lowest-axis obligation — missed again, so no calibration evidence accrued; C2 missed on one item, so no operability evidence accrued. No round admission is claimed; the non-author closure rules. No tools installed; pacman stayed paused. Certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged. Residuals routed to r33: the C1 per-statement enumeration and its digit-bearing units, the 6 unbound and 17 withdrawn r32 items, the C2 predicate gaps reproduced by `w1/SwarmCritic34.md`, T18's revision-sensitive anchor and T12's run-sensitive base, the missing C3-v2 leg in `measure.sh`, and the 54 uncarried seat-failure lines of rounds 15/19/23/24/25.
```

Do not paste the LOG entry's `ATTEMPT` framing into a round-1 narrative: this entry must stay an attempt-2
entry (the round's earlier measurement claims are the same frozen ones, and the salvage commit is not a landing).

---

## Deliveries

- `.ufo/waves/round-32/a2w1/deliver-records-w2.md` (this file)
- `.ufo/waves/round-32/a2w1/SwarmScribe33.md` (report)
