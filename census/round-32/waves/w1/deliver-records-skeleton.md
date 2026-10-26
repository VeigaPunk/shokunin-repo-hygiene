# round 32 wave-1 delivery — record skeletons for the L1 (SoujiR32)

Seat: SwarmScribe28. Nothing in this file is a measurement. Every `<...>` is filled by the L1 from counter output at
the committed revision named beside it; no reading may be carried from another revision and no target may be edited.

Frozen inputs used for the pre-filled cells (opened this run, all at lane HEAD `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`):

- `census/round-32/records/preregistration.txt` (committed `3ec84fc81b3243429c834a051880b0bcde06291c`) — targets.
- `census/round-32/records/controls.tsv` (committed `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`) — base readings, lines 2-4.
- `census/round-32/records/controls-a0.tsv` line 2 — v2 do-nothing reading.
- `census/round-32/records/amendments.txt` — A0 (stricter-only, landed before any wave seat ran).
- `census/round-32/records/m1-red-before.txt`, `census/round-32/c3-contract.txt`, `census/round-32/measure.sh`.
- `corpus/SOURCES.md` 146 rows and `corpus/knowledge/` 4 `ground: F1` entries at base `85b61a151923986e7e6b48f7084b9122561b5f3d`.

Pinned hashes for every command below: base `85b61a151923986e7e6b48f7084b9122561b5f3d`, prereg
`3ec84fc81b3243429c834a051880b0bcde06291c`, controls/A0 `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`.

---

## 1. SCORECARD.md — `### Round 32 measurements`

Insert at the end of the file, after `### Planned (appended at round 31)`'s bullet (line 428; the file's per-round block is measurements, capability rows, planned, and SCORECARD.md stays append-only — the r29 heading states that constraint). Column layout is `### Round 31 measurements`'s, unchanged.

```markdown
### Round 32 measurements (2026-10-26; base 85b61a151923986e7e6b48f7084b9122561b5f3d; preregistration 3ec84fc81b3243429c834a051880b0bcde06291c; amendment A0 landed in 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 capability-count literal binding (44 items: N01-N43 plus r31's unbound L29) | calibration 7 | `SUMMARY items=44 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=44 mismatches=44` (do-nothing control at the prereg; A0's v2 instrument prints the same reading) | <after, at the landing commit and again at the tip, under v1 AND under A0 v2: `SUMMARY items=44 bound_run=<a> bound_record=<b> bound_field=<c> withdrawn=<d> unbound=<0> mismatches=<0>` OR the honest miss naming the item, its base line and its reading> | `python3 -B census/round-32/c1-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`; `census/round-32/c1-counter-v2.py` (A0), same args | <landing full40> |
| C2 sandboxed scratch discipline (27 items T01-T12, T15-T27, T29, T30 over 22 committed files) | operability 8 | `SUMMARY items=27 pass=1 fail=26` | <after, at the landing commit and again at the tip: `SUMMARY items=27 pass=<27> fail=<0>` OR the honest miss naming the failing item ids> | `python3 -B census/round-32/c2-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c` | <landing full40> |
| C3 F1 abandoned-object mtime clock (jj 0.45.1, git 2.56.0) | coverage 8 | `SUMMARY legs=14 fail=13 f1_entries=4` | <after, at the landing commit and again at the tip: `SUMMARY legs=14 fail=<0> f1_entries=<5>` OR the honest miss naming the failing legs> | `python3 -B census/round-32/c3-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c` | <landing full40> |

<Owned-scores paragraph, r31 shape: whether calibration, coverage and operability are unchanged or moved, which claim met or missed its frozen target and by how much, and whether a round admission is claimed. C1's target is the conjunction under v1 AND v2 of `unbound=0 mismatches=0 withdrawn<=8`; C2's is `fail=0`; C3's is `legs=14 fail=0 f1_entries=5`.>
```

Fill rule: `--scratch` may be named explicitly (`census/round-32/measure.sh` passes `--scratch "$S/c1"`, `"$S/c1v2"`, `"$S/c2"`, `"$S/c3"` under `S=${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r32/measure`); if it is, write it in the command cell too, since the reading then depends on it.

## 2. SCORECARD.md — `### Round 32 capability rows`

Four candidate rows, one per line, `### Round 31 capability rows (appended)`'s columns. Admit only the rows whose
evidence pointer the L1 has itself re-run at the landing commit; drop the rest rather than ship a pointer with `<...>`.

```markdown
### Round 32 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| capability-count binding audit v2 (r32) | enumerates every count integer in the SCORECARD capability evidence cells (43 new items plus r31's unbound L29) and binds each to a run, a line-granular record or a JSON field, each row append-only; under A0 a record or field path must be cited on the item's own base line and a record line must carry its unit word next to each integer, so a mechanical binder over uncited files no longer reaches the target | `python3 -B census/round-32/c1-counter-v2.py --root <lane> --rev <landing full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c` -> `SUMMARY <landing reading>`; base `unbound=44 mismatches=44`; controls `census/round-32/records/controls.tsv`, `controls-a0.tsv` | 32 |
| sandboxed scratch-discipline gate (r32) | runs 27 self-contained lane commands with /tmp, /var/tmp and /dev/shm read-only and empty under bwrap and TMPDIR a fresh scratch dir, and passes one only when it prints the base run's exit code and last digit-bearing line and still performs at least half of base's file-creating syscalls, so a tool that honours TMPDIR is distinguished from one that stops working | `python3 -B census/round-32/c2-counter.py --root <lane> --rev <landing full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c` -> `SUMMARY <landing reading>`; base `pass=1 fail=26` (`census/round-32/records/controls.tsv:3`) | 32 |
| jj mtime-clock fixture (r32) | a real jj 0.45.1 plus git 2.56.0 fixture measuring how an abandoned commit object's own mtime decides its fate under `git gc` across arms recent, old, mixed, never and nocruft, including the per-object clock carried inside a cruft pack, with the record replayed twice, a PATH shim proving the real binaries were called, and two subtraction mutants | `TMPDIR=<scratch> bash tests/fixtures/r32-jj-mtime-clock.sh` -> RESULT lines identical to `census/round-32/records/jj-mtime-clock-run.txt`; `python3 -B census/round-32/c3-counter.py ...` -> `SUMMARY <landing reading>`; base `legs=14 fail=13 f1_entries=4` (`controls.tsv:4`) | 32 |
| record-contract check (r32, M1) | turns a frozen fixture field contract into a checkable predicate: every record line under the prefix carries exactly the contract's keys, in order, each value in its enumerated set; shown able to fail on the r31 record (`lines=17 bad=4`, the four `arm=reflog-only` lines) and wired into C3's L14 so the r32 record is checked at landing and at the tip | `python3 -B tools/souji-record-contract.py --record census/round-31/records/jj-object-clock-run.txt --contract census/round-32/m1-r31-contract.txt` -> `lines=17 bad=4`, exit 1 (`census/round-32/records/m1-red-before.txt`); contract `census/round-32/c3-contract.txt`; L14 reading `<fill>` | 32 |
```

## 3. SCORECARD.md — `### Planned (appended at round 32)`

```markdown
### Planned (appended at round 32)

- **r33 (planned r32):** <planned>
```

Shape for `<planned>` when the L1 writes it (r31's bullet names one move per axis plus named residuals): the
calibration move must be the lowest-axis obligation if C1 misses again or calibration stays 7; operability and
coverage name one move each; then the residuals carried out of r32 verbatim from the counters' own records — do not
invent residuals that no r32 counter reported.

## 4. LOG.md — round 32 entry skeleton

Append after the round-31 entry, in that entry's shape.

```markdown
## 2026-10-26 — Round 32 attempt 1: <C1 gist>, <C2 gist>, <C3 gist>

Preregistration 3ec84fc81b3243429c834a051880b0bcde06291c and controls 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 (base 85b61a151923986e7e6b48f7084b9122561b5f3d) before any seat data; start census rc 0 with 36 W04 duplicate-url warnings (`census/round-32/records/census-start.txt`). Wave-1 attacks led to stricter-only amendment A0 at 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 (`census/round-32/records/amendments.txt`): the C1 v2 instrument requires a record or field path cited on the item's base SCORECARD line and the unit word adjacent to each integer, because a mechanical binder met v1 by binding 39 of 44 items (`controls-a0.tsv`).
- C1 calibration (<landing40>): capability-count literals `items=44 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=44 mismatches=44` -> `<after under v1 and under A0>`; `<n>` append-only binding rows, or the honest miss naming the item, its base line and why no binding exists.
- C2 operability (<landing40>): `items=27 pass=1 fail=26` -> `<after>`; `<the tools and fixtures that now honour TMPDIR, and the literal /tmp or /var/tmp each one dropped>`.
- C3 coverage (<landing40>): `corpus/knowledge/jj-abandoned-object-mtime-clock.md` (`ground: F1`), row `<S-id>` new (`corpus/SOURCES.md` 146 -> `<147>`), fixture `tests/fixtures/r32-jj-mtime-clock.sh`, record `census/round-32/records/jj-mtime-clock-run.txt` (`<n>` RESULT lines, jj 0.45.1, git 2.56.0); `legs=14 fail=13 f1_entries=4` -> `<after>`.
- Mined mistake M1 (r31 D1, contract class): `tools/souji-record-contract.py` turns the r31 fixture contract into a check and prints `lines=17 bad=4`, exit 1 over the r31 record (`census/round-32/records/m1-red-before.txt`); C3's L14 holds the r32 contract at the landing commit and at the tip (`<record>`).
- Routed r31 defects: D1 -> M1 and L14; D2 append-only corrections (S051, S063 anchor, `gc.recentObjectsHook` quote) `<where committed>`; D3 `<disposition>`; D4 landing-text discipline `<receipts under census/round-32/records/>`; D5 `/var/tmp` gate snapshots -> C2 (`<items>`).
- Frontier: `corpus/SOURCES.md` 146 -> `<n>` rows, `<S-id>` opened this round with its snapshot and fetch receipt (`census/round-32/sources/`, `records/fetch-receipts.tsv`); census rc 0 at the start and at the end (`census/round-32/records/census-start.txt`, `census-end.txt`); F1 map row in `corpus/README.md` `## Round 32`; boundary note in `PROVINCE.md`.
- QUALITY `<Q-ids>`, SKILL gate-registry rows for the r32 instruments, README and PROVINCE text, and the round lesson `corpus/lessons/round-32.md`. Waves: w1 `<n>` seats `<n>` result payloads (`census/round-32/waves/w1-results.json`), w2 `<n>` seats.
Owned axis scores <unchanged (calibration 7, coverage 8, operability 8) or moved>; <round admission verdict>. No tools installed; pacman stayed paused. Certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged. Residuals routed to r33: `<...>`.
```

## 5. Report skeleton — `/home/vgpnk/Projects/shokunin/.ufo/reports/round-32/souji.md`

House style is round 31's file: header block, Work performed, Landed changes, Before -> after measurements,
Sources & frontier, Trend verdicts, SHONEN, Other report lines. Section order below is the assignment's and matches it.

```markdown
# souji — round 32 report (attempt 1)

Lane repo: `/home/vgpnk/Projects/shokunin/souji-shokunin`, branch `master`.

- Base: `85b61a151923986e7e6b48f7084b9122561b5f3d`.
- Preregistration: `3ec84fc81b3243429c834a051880b0bcde06291c`. Controls and amendment A0: `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`.
- Final lane HEAD: `<full40>`.
- `git ls-remote origin refs/heads/master` prints `<that hash>`.
- `jj-lane.sh state` reads `<ahead=0 behind=0 tracked=0 untracked=0>`.
- Lane L1: `<SoujiR32>`.

## Work performed

The claims were frozen in `census/round-32/records/preregistration.txt` at commit `3ec84fc81b3243429c834a051880b0bcde06291c`. The controls and amendment A0 were committed at `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`. Both landed before any seat ran.

- **C1 — calibration** (the lowest non-retired axis, 7). Claim: each of the 44 enumerated capability-count integers (the 43 the r31 `N/M` notation skipped, plus r31's unbound L29) carries one appended binding row — a `run:`, a line-granular `record:` or a `field:` — or an explicit `withdrawn:` row within the cap of 8. This answers routed r31 closure defect 1. **Verdict: <MET / MISSED by ...>.**
- **C2 — operability** (8). Claim: the 27 enumerated tool and fixture commands run with `/tmp`, `/var/tmp` and `/dev/shm` read-only and `TMPDIR` a scratch dir, printing the base run's exit code and last digit-bearing line while still doing their file work. This answers prompt section 7 item 4 and the r31 residual at `tools/souji-landing-gate.py:1182` and `:1499`. **Verdict: <...>.**
- **C3 — coverage** (8, the F1 frontier). Claim: a new entry on how an abandoned commit object's own mtime decides its fate under `git gc`, measured with real jj 0.45.1 and git 2.56.0, across arms recent, old, mixed, never and nocruft. It is the round's sourced claim, resting on `<S-id>`. **Verdict: <...>.**

Work items, each with its commit:

- Preregistration, frozen counters, enumerations, C3 contract, M1 record-contract tool and red-before, start census: `3ec84fc81b3243429c834a051880b0bcde06291c`.
- Controls (`census/round-32/records/controls.tsv`) and amendment A0 with its own controls: `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`.
- <each landing commit: C1 rows, C2 tools and fixture, C3 entry/fixture/record/docs, M1, lesson/QUALITY/SKILL/SCORECARD/LOG/census/waves, final-tip receipt, wave-2 capture>.

Round shape: **two v1 waves**, dispatched inline by the orchestrator through ready files.

| wave | purpose | seats | role mix | flash / attack |
|---|---|---|---|---|
| W1 `souji-r32-w1` | build plus first falsifiers | <n> | <roles> | <flash> / <attack> |
| W2 `souji-r32-w2` | falsify what landed | <n> | <roles> | <flash> / <attack> |

- Round total: **<n> seats**, no residual call, **<n> dead seats**.
- Every seat wrote its report: W1 `<n>/<n>` per `census/round-32/waves/w1-results.json`; W2 `<n>/<n>` per `w2-results.json`.
- The validator rejects `planner` as a swarm role, so the L1 held the canonical planner seat.
- <nudges, retries, aborted seats — or "none">.

## Landed changes

All rows tie to the LOG.md entry "2026-10-26 — Round 32 attempt 1: <gist>".

| change | commit |
|---|---|
| <change> | `<full40>` |

Inherited state: <worktree state at start, whether `.ufo/watchdog.log` carried an earlier attempt of this round, what was not touched>.

## Before -> after measurements

### C1

Command: `python3 -B census/round-32/c1-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`, and `census/round-32/c1-counter-v2.py` (A0) with the same arguments. The target is the conjunction: v1 AND v2 each `unbound=0 mismatches=0 withdrawn<=8`.

| when | revision | reading | record |
|---|---|---|---|
| base | `3ec84fc` | `items=44 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=44 mismatches=44` (v1 and v2) | `census/round-32/records/controls.tsv:2`, `controls-a0.tsv:2` |
| landing | `<full40>` | <v1 reading>; <v2 reading> | `<c1-after-v1.txt>`, `<c1-after-v2.txt>` |
| final tip | `<full40>` | <same reading> | `<final-tip-measure.txt>` |

**<MET / MISSED>** <why; if missed, the item, its base line and the reason no honest binding exists>.

### C2

Command: `python3 -B census/round-32/c2-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`.

| when | revision | reading | record |
|---|---|---|---|
| base | `3ec84fc` | `items=27 pass=1 fail=26` | `census/round-32/records/controls.tsv:3` |
| landing | `<full40>` | <reading> | `<c2-after.txt>` |
| final tip | `<full40>` | <same reading> | `<final-tip-measure.txt>` |

**<MET / MISSED>** <which items failed and why>.

### C3

Command: `python3 -B census/round-32/c3-counter.py --root <lane> --rev <full40> --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`.

| when | revision | reading | record |
|---|---|---|---|
| base | `3ec84fc` | `legs=14 fail=13 f1_entries=4` | `census/round-32/records/controls.tsv:4` |
| landing | `<full40>` | <reading> | `<c3-after.txt>` |
| final tip | `<full40>` | <same reading> | `<final-tip-measure.txt>` |

**<MET / MISSED>** <which legs, the record's line count, the replay result>.

### No harm

<the wave-2 sweep over the lane fixtures and selftests outside C2's set: how many print the same exit code and last line at base and at tip, and every difference named with why it is benign; the registry and coverage counters at both revisions>.

## Sources & frontier

- **SOURCES rows**: 146 at base, `<n>` at the tip. Count command: `git show <rev>:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`.
- **Rows added**: <tier, S-id, URL and version, `mined`, opened date>.
- **Rows touched** (`used-by` only, logged old->new in `corpus/lessons/round-32.md` `### SOURCES touched-row log`): <S-ids>.
- **Census**: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` printed `souji ok`, exit 0, 36 W04 at the start (`census/round-32/records/census-start.txt`) and at the end (`census-end.txt`).
- **Frontier advanced**: F1, the abandoned object's own mtime clock (`corpus/README.md` `## Round 32`). F1-grounded entries 4 -> `<5>`.
- **Sourced claim**: C3 (`<S-id>`).
- **Mined mistake**: M1. `tools/souji-record-contract.py` prints `lines=17 bad=4`, exit 1 over the r31 record (`census/round-32/records/m1-red-before.txt`); C3's L14 holds the r32 contract at landing and at the tip.
- **Assimilation: <none / entry>**. <the `merge/souji/` sweep with per-entry rejects, or "per-entry rejects are in the lesson's `## Gate`">.
- **considerthese/**: <absent in this lane / disposition>.

## Trend verdicts

- **expansion — <verdict>.** <one measured entry, its RESULT line count, whether an independent seat replicated it, and what argues against it>.
- **quality — <verdict>.** <what now works that did not: items fixed, false readings removed, records made checkable>.
- **discernment — <verdict>.** <which frozen counters wave-1 or wave-2 seats beat before landing, which stricter amendments followed, whether any target was missed>.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — <SKILL.md `## Gate registry` rows; corpus/SOURCES.md S-ids>
- [~] At least one end-to-end domain task executed and logged in LOG.md — LOG.md:362 (2026-10-19 operator sweep); round 32 LOG entry at the end of LOG.md
- [~] Instructions executable by an agent without oral context — <record that re-derives every claim from committed bytes>
- [~] No cross-domain bleed (PROVINCE.md still accurate) — <PROVINCE.md `## Round 32 boundary note (...)`; a connector seat report>

## Other report lines

- **Cross-domain evidence**: <none contested / what was scanned, how many sibling lanes, and what is reported rather than absorbed>.
- **Misroot sweep**: `git -C /home/vgpnk/Projects/shokunin status --porcelain` <what it shows, and that nothing outside the lane was written, deleted or classified>.
- **Stale-lane**: <launch time from `.ufo/watchdog.log`, lane commit count, whether another mission of this lane is open>.
- **Tool installs**: <none by the L1 and none reported by a seat, or tool/version/channel/reason per install>; pacman stayed paused.
- **Scratch**: `/fast/scratch/hyaku/souji-r32` is removed after landing.
- **Open L0 questions**: <none filed / the questions filed>.
```

Fill rules for section 5: the "before" cells above are the committed control readings and must not be restated from
memory; the "after" cells are copied from the counter output at the commit in the same row and nowhere else; wave
seat counts come from the captured `census/round-32/waves/*-results.json`, never from the dispatch spec.
