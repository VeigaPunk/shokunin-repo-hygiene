# souji — round 32 report (attempt 2)

Lane repo: `/home/vgpnk/Projects/shokunin/souji-shokunin`, branch `master`.

- Base: `85b61a151923986e7e6b48f7084b9122561b5f3d`.
- Preregistration: `3ec84fc81b3243429c834a051880b0bcde06291c`. Controls and amendment A0: `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`. Amendment A1: `a92e1aae91dbf46c2d7eff713932cfc820186970`.
- Final lane HEAD: `<L1>`.
- Draft-time lane HEAD: `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`, the orchestrator salvage commit ("hyaku run-8 orchestrator salvage of unlanded attempt-1 census records (L1 died in the orchestrator host crash 2026-10-26 ~08:50 -03; not a landed round)"). `git ls-remote origin refs/heads/master` printed that hash at draft time.
- `jj-lane.sh state` reads `<L1>`.
- Lane L1: `SoujiR32` (attempt 1, died with the orchestrator host crash) and `SoujiR32a2` (attempt 2, the single integration owner from the salvage tip).

`<L1>` marks a value this draft could not read from committed bytes; the attempt-2 L1 fills it at integration.

## Work performed

The claims were frozen in `census/round-32/records/preregistration.txt` at commit `3ec84fc81b3243429c834a051880b0bcde06291c`; the controls and amendment A0 were committed at `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`. Both landed before any seat ran.

**Round shape.** Attempt 1 is **attempt 1** and it did not finish: it dispatched wave `w1` (44 seats), landed C2, C3 and C1, and then its L1 died in the orchestrator host crash of 2026-10-26 ~08:50 -03, before its falsify wave ran. The orchestrator salvaged attempt 1's five after-records as `4e56c48b8fc828f9aba2746e324dc46aa538bdbf` — census/round-32/records/ `c1-after-v1.txt`, `c1-after-v2.txt`, `c2-after-v1.txt`, `c3-after-v1.txt`, `c3-after-v2.txt` — and the attempt-2 wave `a2w1` (38 seats) is that falsify wave: it attacks what wave 1 produced and what landed. Attempt 1's `w2` spec (34 seats, `make-spec-w2.py`) was **never dispatched — marker ABANDONED**: `.ufo/waves/round-32/w2.ready.dispatched` reads "2026-10-26T09:04:54 ABANDONED by hyaku run-8 orchestrator cleanup: no seat was spawned", and `w2/` holds only its empty `swarm-registry.json`.

- **C1 — calibration** (the lowest non-retired axis, 7). Claim: each of the 44 enumerated capability-count integers (N01-N43, the maximal digit runs in the SCORECARD capability evidence cells that the r31 `N/M` notation skipped, plus r31's unbound L29) carries one appended binding row — a `run:`, a line-granular `record:` or a `field:` — or an explicit `withdrawn:` row within the cap of 8; target `unbound=0 mismatches=0 withdrawn<=8` under v1 **and** under A0 v2. This answers routed r31 closure defect 1. **Verdict: MISSED.** The landed block has 38 rows for 44 items: `SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6` (`census/round-32/records/c1-after-v1.txt:46`, `c1-after-v2.txt:46`). Six items are unbound (N28, N29, N30, N31, N33, N34, all `SCORECARD.md:422`) and 17 withdrawals exceed the cap by nine.
- **C2 — operability** (8). Claim: the 27 enumerated tool and fixture commands run with `/tmp`, `/var/tmp` and `/dev/shm` read-only under bwrap and `TMPDIR` a fresh scratch dir, printing the base run's exit code and last digit-bearing line while still creating at least half of the base run's files; target `fail=0`. This answers prompt section 7 item 4 and the r31 residual at `tools/souji-landing-gate.py` (the `tempfile.mkdtemp(dir='/var/tmp')` snapshot and selftest). **Verdict: MISSED.** The salvaged landing reading is 26/27 PASS with T18 FAIL (`census/round-32/records/c2-after-v1.txt:29`); the falsify wave re-measures 25/27 at the same commit, T12 and T18 failing (`a2w1/SwarmExecutor08.md`), and the attempt-2 L1's own tip run prints `SUMMARY items=27 pass=25 fail=2` (uncommitted `census/round-32/records/a2-l1-salvage-tip-measure.txt`; the final-tip cell is `<L1>`).
- **C3 — coverage** (8, the F1 frontier). Claim: one new entry `corpus/knowledge/jj-abandoned-object-mtime-clock.md` (`ground: F1`) on how an abandoned commit object's own mtime decides its fate under `git gc`, measured with real jj 0.45.1 and git 2.56.0 across arms recent, old, mixed, never and nocruft; target `legs=14 fail=0 f1_entries=5`. It is the round's sourced claim, resting on S223. **Verdict: MET.** `SUMMARY legs=14 fail=0 f1_entries=5` at `a92e1aa` (`census/round-32/records/c3-after-v1.txt:16`) and under A1's stricter instrument `SUMMARY legs=17 fail=0 f1_entries=5` (`c3-after-v2.txt:19`); the final-tip reading is `<L1>`.

Work items, each with its commit:

- Preregistration, the frozen C1-C3 counters, both enumerations, the C3 contract, `tools/souji-record-contract.py` with its red-before receipt, and the start census: `3ec84fc81b3243429c834a051880b0bcde06291c` (16 files, +1292).
- Controls (`census/round-32/records/controls.tsv`) and stricter-only amendment A0 (C1 v2: cited evidence, count adjacency) with its own controls (`controls-a0.tsv`): `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`.
- C2 scratch discipline: 26 tools and fixtures take scratch from `TMPDIR`; the two r20 fixtures re-exec under a private `/var/tmp` backed by `TMPDIR`: `98e5203d45b4e419a9e72801733d93303acc7ebd` (27 files, +174/−93).
- C3 F1 mtime-clock entry, fixture `tests/fixtures/r32-jj-mtime-clock.sh`, record, S223, three snapshots with `SHA256SUMS` and fetch receipts, README `## Round 32` + corrections, PROVINCE `## Round 32 boundary note (F1 mtime clock)`, SKILL error-pattern bullet and two Gate-registry rows; stricter-only amendment A1 (C3 v2, legs L15-L17); routed r31 defect 2 corrections (S051 cite, S063 anchor, `gc.recentObjectsHook` quote): `a92e1aae91dbf46c2d7eff713932cfc820186970` (17 files, +2514/−4).
- C1 capability-count binding rows: 38 rows for 44 items (21 bound, 17 withdrawn, 6 unbound), append-only after the base 81245 bytes: `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93` (`SCORECARD.md` +43).
- Orchestrator salvage of attempt 1's five after-records: `4e56c48b8fc828f9aba2746e324dc46aa538bdbf` (5 files, +156).
- Round lesson `corpus/lessons/round-32.md`, QUALITY Q70-Q72, the C1 and C3 Gate-registry rows, SCORECARD round-32 measurements / capability rows / planned r33, LOG entry, end census, wave capture and final-tip receipt: `<L1>`.

Round shape, seat accounting:

| wave | attempt | purpose | seats | role mix | flash / attack | reports |
|---|---|---|---|---|---|---|
| `w1` | 1 | build plus first falsifiers | 44 | executor 19, scribe 7, critic 5, reviewer 3, mutation-tester 3, scout 2, connector 2, revenger 1, sentinel 1, simplifier 1 | 34 / 11 (77.3 % / 25.0 %) | 41 of 44 |
| `w2` | 1 | falsify what landed | 0 spawned (34 specced) | critic 7, reviewer 12, executor 5, scribe 3, mutation-tester 2, connector 2, scout 1, sentinel 1, simplifier 1 | — | ABANDONED, no seat spawned |
| `a2w1` | 2 | falsify what wave 1 produced and what landed | 38 | reviewer 13, critic 8, executor 6, scribe 3, connector 2, scout 2, mutation-tester 2, sentinel 1, simplifier 1 | 19 / 23 (50.0 % / 60.5 %) | `<L1>` (15 at draft time) |

- Round total: **82 seats spawned** (44 + 38) plus one abandoned 34-seat spec; seat counts read from the wave registries (`.ufo/waves/round-32/{w1,a2w1}/swarm-registry.json`, gitignored); flash and attack counts apply the dispatch generator's own role sets (`executor, scribe, critic, sentinel, revenger, simplifier` = flash; `reviewer, critic, mutation-tester` = attack). Committed capture `census/round-32/waves/*-results.json`: `<L1>`.
- Three attempt-1 seats have no report: `SwarmReviewer30`, `SwarmReviewer31`, `SwarmMutationTester40` — lost with the crash (41 of 44 report files present under `w1/`).
- The validator rejects `planner` as a swarm role, so the L1 held the canonical planner seat in both attempts.
- Attempt-1 wave attacks that changed the contract: A0 before any seat ran (the v1 mechanical binder bound 39 of 44 items, `census/round-32/records/controls.tsv:6`), and A1 after wave 1 (W1 `SwarmCritic35` met the frozen C3 v1 target with a fixture printing RESULT lines from constants). C2's v1 predicate is disclosed as accepting a clone-local scratch and a fabricated anchor (W1 `SwarmCritic34`), not amended.

## Landed changes

All rows tie to the round-32 LOG.md entry, which lands with the integration commit (`<L1>`; its title and body are the L1's, drafted in `.ufo/waves/round-32/w1/deliver-records-skeleton.md` §4).

| change | commit |
|---|---|
| preregistration, frozen counters C1-C3, enumerations, C3 contract, M1 record-contract tool and red-before, start census | `3ec84fc81b3243429c834a051880b0bcde06291c` |
| controls and stricter-only amendment A0 (C1 v2) with its controls | `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` |
| C2 scratch discipline: 26 tools and fixtures take scratch from `TMPDIR`; r20 fixtures inside a private `/var/tmp` backed by `TMPDIR` | `98e5203d45b4e419a9e72801733d93303acc7ebd` |
| C3 F1 mtime-clock entry, fixture, record, S223, snapshots, docs; amendment A1 (C3 v2); routed r31 defect 2 (S051 cite, S063 anchor, `gc.recentObjectsHook` quote) | `a92e1aae91dbf46c2d7eff713932cfc820186970` |
| C1 capability-count binding rows (38 of 44 items: 21 bound, 17 withdrawn, 6 unbound) | `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93` |
| orchestrator salvage of attempt 1's five after-records | `4e56c48b8fc828f9aba2746e324dc46aa538bdbf` |
| lesson, QUALITY Q70-Q72, C1/C3 Gate-registry rows, SCORECARD measurements, capability rows, planned r33, LOG entry, end census, wave capture | `<L1>` |
| final-tip receipt `census/round-32/records/final-tip-measure.txt` | `<L1>` |

Inherited state: the worktree was clean at the base and at both dispatches; `.ufo/watchdog.log` holds only round 32's launch line, so no earlier attempt of this round was inherited (preregistration, line 1). **Reused after re-verification:** the three landed claims' bytes and their wave-1 deliveries — the C1 rows audited row-by-row under both counters (`a2w1/SwarmReviewer03.md`, `SwarmCritic04.md`, `SwarmCritic06.md`), C2 re-run at its landing commit (`a2w1/SwarmExecutor08.md`), C3 replayed and re-fetched (`census/round-32/records/c3-after-v1.txt`, `c3-after-v2.txt`). **Discarded as measurements:** attempt 1's salvaged after-records' readings — they stay in the tree as what attempt 1 read, but no number below is taken from them alone; the tip reading is re-taken `<L1>`. **Discarded outright:** the attempt-1 `w2` spec (34 seats, ABANDONED, no seat spawned) and the three seat reports that died with the crash.

## Before -> after measurements

### C1

Command: `python3 -B census/round-32/c1-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`, and `census/round-32/c1-counter-v2.py` (A0) with the same arguments. The target is the conjunction: v1 AND v2 each `unbound=0 mismatches=0 withdrawn<=8`.

| when | revision | reading | record |
|---|---|---|---|
| base | `3ec84fc` | `SUMMARY items=44 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=44 mismatches=44` (v1 and v2) | `census/round-32/records/controls.tsv:2`, `controls-a0.tsv:2` |
| landing | `9e8982b` | `SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6` under v1 and v2 | `c1-after-v1.txt:46`, `c1-after-v2.txt:46` |
| final tip | `<L1>` | same reading at the draft-time tip `4e56c48` (`a2-l1-salvage-tip-measure.txt`, uncommitted) | `<L1>` |

**MISSED** on all three frozen limbs: `unbound=6`, `mismatches=6`, `withdrawn=17 > 8`. The six unbound items are N28-N31, N33 and N34 — the r31 rows' `items=41 bound_run 20 bound_record 20 ... unbound=22 mismatches=34` cell at `SCORECARD.md:422`, whose integers the r31 coverage-agreement record states only as separate counts with no unit word. The falsify wave also finds two withdrawals that are grammar-blocked rather than evidence-absent (N42's unit `r26` and N43's plural `results` defeat A0(b) adjacency, `a2w1/SwarmCritic06.md`), one wrong withdrawal (N25 binds as `k13`, `a2w1/SwarmCritic04.md` attack A1), and decoy rows at a wrong base line dropped silently by the counter (same report, attack A2).

### C2

Command: `python3 -B census/round-32/c2-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`.

| when | revision | reading | record |
|---|---|---|---|
| base | `3ec84fc` | `SUMMARY items=27 pass=1 fail=26` | `census/round-32/records/controls.tsv:3` |
| landing | `98e5203` | `SUMMARY items=27 pass=26 fail=1`, T18 `regress` (`baseline_mismatches=26` -> `31`) | `c2-after-v1.txt:29` |
| landing, re-derived | `98e5203` | `SUMMARY items=27 pass=25 fail=2`, T12 and T18 `regress` (two independent full runs) | `a2w1/SwarmExecutor08.md` |
| final tip | `<L1>` | `SUMMARY items=27 pass=25 fail=2` at the draft-time tip `4e56c48`; T18 reads `32` | `<L1>` |

**MISSED.** T18's anchor line embeds `baseline_mismatches=<n>`, a count of files differing from the pinned `12516f7d` revision; five of the closure files are repaired by the C2 landing commit itself (four of them the enumerated items' own files), so each honest repair costs +1 and no repair of the enumerated set can hold 26: measured 26 (T18 hunk alone), 27 (one repair), 30 (four), 31 (the landed commit), 32 once C3's entry lands. T12 is instrument-induced: four sandbox runs without the tracer pass 69/0 at 3.9-4.0 s, and the tracer alone trips the fixture's 6 000 ms watchdog bound, so the fail count is not invariant (`a2w1/SwarmExecutor08.md`, A2). The disclosed C2 predicate weakness stands: the v1 instrument also accepts a clone-local scratch and a fabricated anchor (W1 `SwarmCritic34`).

### C3

Command: `python3 -B census/round-32/c3-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`, plus `census/round-32/c3-counter-v2.py` (A1) with the same arguments.

| when | revision | reading | record |
|---|---|---|---|
| base | `3ec84fc` | `SUMMARY legs=14 fail=13 f1_entries=4` | `census/round-32/records/controls.tsv:4` |
| landing | `a92e1aa` | v1 `SUMMARY legs=14 fail=0 f1_entries=5`; v2 `SUMMARY legs=17 fail=0 f1_entries=5` | `c3-after-v1.txt:16`, `c3-after-v2.txt:19` |
| final tip | `<L1>` | v1 `legs=14 fail=0 f1_entries=5`, v2 `legs=17 fail=0 f1_entries=5` at the draft-time tip `4e56c48` | `<L1>` |

**MET.** The record `census/round-32/records/jj-mtime-clock-run.txt` carries `jj 0.45.1-7c41cdeb`, `git version 2.56.0` and 22 `RESULT` lines over five arms; contract L14 reads `lines=22 contract_unchanged=True bad=[]`; L9 replays twice equal; L12 shows the shimmed `jj`/`git`/`touch` calls were real (32 jj, 366 git, 16 touch); L13's two subtraction mutants differ; A1's L15-L17 (plain-git probe, shim exit statuses, live re-fetch of every receipt snapshot) pass.

### No harm

The frozen no-harm watch (lane fixtures and selftests outside C2's set, base vs tip) was wave-2 work and attempt 1's wave 2 never ran; the falsify wave covers slices of it only. Recorded numbers: `<L1>`. Two deltas are witnessed and named: T12's tracer-dependent watchdog failure (above) and the receipt-run out-guard now following the caller's `TMPDIR` so that a fleet-root path is accepted where base refused it (`a2w1/SwarmReviewer13.md` finding 1, reproduced with `TMPDIR=/home/vgpnk/Projects/shokunin`). The registry and coverage-agreement counters at both revisions: `<L1>`.

## Sources & frontier

- **SOURCES rows**: 146 at base, 147 at the tip. Count command: `git show <rev>:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` -> `146` at `85b61a1`, `147` at `a92e1aa` and at `4e56c48`.
- **Row added**: one, tier A: `S223`, git `Documentation/gitformat-pack.adoc` at tag v2.56.0 (raw tag URL), status `mined`, opened 2026-10-26, `corpus/SOURCES.md:168`.
- **Rows touched** (`used-by` only, plus S063's anchor; logged old->new in `corpus/lessons/round-32.md` `### SOURCES touched-row log`, `<L1>`): S002 (`used-by` gains the new entry), S051 (`used-by` gains `jj-dropped-keep-object-lifetime.md`, the routed r31 defect 2 correction), S063 (`anchor` gains `§ CONFIGURATION gc.pruneExpire, gc.reflogExpire and gc.reflogExpireUnreachable`, `used-by` gains the new entry).
- **Census**: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` printed `souji ok` (exit 0) with 36 W04 duplicate-url warnings at the start (`census/round-32/records/census-start.txt:37`) and at the end: `<L1>` (no `census-end.txt` in the tree at draft time).
- **Frontier advanced**: F1, the abandoned object's own mtime clock (`corpus/README.md:703` `## Round 32 — F1 the abandoned object's own mtime clock`; boundary note `PROVINCE.md:238`). F1-grounded entries 4 -> 5. The remaining F1 item is the fleet exposure numerator.
- **Sourced claim**: C3 (S223; snapshots `census/round-32/sources/gitformat-pack.adoc`, `git-gc.adoc`, `gc.adoc` with `SHA256SUMS` and `census/round-32/records/fetch-receipts.tsv`).
- **Mined mistake**: M1 (r31 D1, contract class). `tools/souji-record-contract.py` over the r31 record with the r31 contract prints four `BAD … arm=reflog-only outside descendant|solo` lines and `lines=17 bad=4`, exit 1 (`census/round-32/records/m1-red-before.txt`); C3's L14 holds the r32 contract at landing and at the tip.
- **Assimilation: none adopted.** W1's sweep over `/home/vgpnk/Projects/shokuknow/merge/souji/` (68 entries, 134 rows) records 20 per-entry REJECTs; 0 staged files mention `cruft`, `.mtimes`, `gitformat-pack` or `gc.cruftPacks`, so no staged entry grounds the object clock. Id-collision guard: 38 collisions (S109-S132, S152, S210-S222) and 10 path collisions; nothing appended. Per-entry rejects are in the lesson's `## Gate` (`<L1>`; draft `.ufo/waves/round-32/w1/deliver-lesson-gate.md`).
- **considerthese/**: absent in this lane (`ls` -> no such file, checked 2026-10-26).

## Trend verdicts

- **expansion — better, with its strongest falsifier still running.** One admitted F1 entry, 22 `RESULT` lines across five arms and two replay-equal runs against real jj 0.45.1 and git 2.56.0, citing a row opened this round; measured at the landing commit and again at the tip. Against it: the sentence-to-record attack on every claim sentence (routed r31 defect 4) is a seat of this wave and its verdict is `<L1>`.
- **quality — improved.** 21 capability integers that no instrument read are now bound append-only, and the C3 record is checkable against a frozen field contract by two instruments. Of the 27 enumerated commands, 25 pass the sandboxed re-run at the landing commit (26 in the salvaged record), and the gate's own `/var/tmp` snapshot and selftest no longer write there. Against that: the C2 commit's own diff leaves a literal `/tmp` or `/var/tmp` as at least one scratch path in 12 of its 27 files when `TMPDIR` is unset or at a child env (see the seat report's findings 1-2), the two r20 fixtures meet the sandbox only by re-binding `/var/tmp` writable inside a nested bwrap, T18's anchor is self-defeating, T12 is load-dependent, and C1's withdrawal prose is unchecked by the counter.
- **discernment — unchanged.** Two of three frozen targets missed. A0 closed a cheapest-skip path that bound 39 of 44 items, and A1 closed a constant-printing fixture that met C3 v1 exactly; both are disclosed and stricter-only. C2's v1 predicate is shown gameable and left unamended by policy, and its landing target was unreachable by construction (T18). No outside spot-check exists yet.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — SKILL.md `## Gate registry` rows `r32-jj-mtime-clock` (:253), `souji-record-contract` (:254), `r32-c2-counter` (:255), plus the C1/C3 rows `<L1>`; error-pattern bullet at SKILL.md:156 (r32 `git cat-file -e` reach); corpus/SOURCES.md S223
- [~] At least one end-to-end domain task executed and logged in LOG.md — LOG.md:362 (2026-10-19 operator sweep); round-32 LOG entry at the end of LOG.md `<L1>`
- [~] Instructions executable by an agent without oral context — `census/round-32/records/jj-mtime-clock-run.txt` plus `census/round-32/c3-contract.txt` and legs L8-L14 re-derive the claim from committed bytes; full re-measurement `census/round-32/records/final-tip-measure.txt` `<L1>`
- [~] No cross-domain bleed (PROVINCE.md still accurate) — PROVINCE.md:238 `## Round 32 boundary note (F1 mtime clock)`; `.ufo/waves/round-32/w1/deliver-sibling-overlap.md` (20 sibling lanes scanned, no claim on the round's surfaces)

## Other report lines

- **Cross-domain evidence**: none contested. W1 `SwarmConnector41` scanned all 20 non-souji lanes' `PROVINCE.md`, `SKILL.md`, `corpus/README.md`, `corpus/knowledge/*.md` and `scripts/hyaku/*.sh` for `cruft`, `pruneExpire`, `mtimes`, `/var/tmp`, `TMPDIR`, `bwrap`, `capability`. Nearest neighbour: kumitate's jj abandoned-object persistence note (persistence until `jj util gc`, no mtime clock) — compatible, not contested. No sibling claims cruft-pack handling or a `.mtimes` clock. The fleet's own `scripts/hyaku/disk-guard.sh:291` uses the `${TMPDIR:-/var/tmp}` fallback C2 labels a defect; that is **reported, not absorbed** (outside this lane's write scope), as are the sibling norms that treat `/var/tmp` as sanctioned scratch (kaidoku, kotodama) and revenger's `/tmp` scratch.
- **Misroot sweep**: at draft time `git -C /home/vgpnk/Projects/shokunin status --porcelain` showed 152 staged `.tower/` message files, 19 `.ufo/` driver entries (`.ufo/state/*.report-baseline` modifications, `inline-dispatcher.log`, `watchdog.log`) and one transient untracked `s8-colon.txt` at the fleet root that was absent on a second read. Nothing outside `/home/vgpnk/Projects/shokunin/souji-shokunin/` was written, moved, deleted or classified by a souji seat; the lane's own scope is unchanged.
- **Stale-lane**: this mission launched with `w1.ready` reaching the driver at `2026-10-26T05:28:15` and the attempt-2 wave `a2w1` dispatched at `2026-10-26T09:26` (`.ufo/waves/round-32/*.ready*`, gitignored); `.ufo/watchdog.log` holds only round 32's launch line and no earlier attempt (preregistration, line 1). Attempt 1 made five lane commits before the crash; the round has six at draft time and lands `<L1>` more. No other mission of this lane is open.
- **Tool installs**: none. No seat report under `.ufo/waves/round-32/{w1,a2w1}/` mentions installing or upgrading a tool (grep for `uv tool install`, `npx `, `pacman -S`, `cargo install` -> 0 hits in the 56 reports present), and no pacman transaction was run — all pacman transactions stay paused host-wide.
- **Scratch**: `/fast/scratch/hyaku/souji-r32` holds the wave's per-seat dirs at draft time; it is removed after landing (`<L1>`).
- **Open L0 questions**: none filed — no seat report and no dispatch prompt of either wave files one.
