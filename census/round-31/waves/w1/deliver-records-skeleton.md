# Round 31 records skeletons — SCORECARD rows, capability rows, planned r32, LOG entry, report

Seat: SwarmScribe23 (scribe; leaf, no dispatch). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base
`9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, preregistration `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`,
controls `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc`.

This file is a **skeleton only**. Every `<...>` is an L1 fill-in after data. No measurement in it was run by
this seat; the before-values are copied from `census/round-31/records/controls.tsv` and the targets from
`census/round-31/records/preregistration.txt` (C1/C2/C3 paragraphs) as read this run. Insertion point for
sections 1-3: immediately after `SCORECARD.md:359` (the last byte of the file at base; the r30 planned bullet).
Section 4 appends to `LOG.md`; section 5 is written fresh at `/home/vgpnk/Projects/shokunin/.ufo/reports/round-31/souji.md`.

## 1. `### Round 31 measurements` — for SCORECARD.md

Verbatim target block (column layout of `### Round 30 measurements`, SCORECARD.md:340):

```
### Round 31 measurements (<YYYY-MM-DD>; base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc; preregistration 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525; amendments <rev>)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 capability-cell literal binding | calibration 7 | `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` | <after reading>: **<met|missed>** | `python3 -B tools/souji-capability-cells.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` | <census/round-31/records/c1-after.txt>; landing <full40> |
| C2 landing-gate reading precision | operability 8 | `SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same` | <after reading>: **<met|missed>** | `python3 -B census/round-31/c2-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --fleet-root /home/vgpnk/Projects/shokunin` | <census/round-31/records/c2-after-v1.txt>; landing <full40> |
| C3 F1 dropped-keep-ref object lifetime entry | coverage 8 | `SUMMARY legs=11 fail=10 f1_entries=3`; v2 `legs=12 fail=11 f1_entries=3` | `SUMMARY legs=11 fail=0 f1_entries=4`; v2 `legs=12 fail=0 f1_entries=4` **only if measured so**: **<met|missed>** | `python3 -B census/round-31/c3-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; `census/round-31/c3-counter-v2.py` same args | <census/round-31/records/c3-after-v1.txt>, <c3-after-v2.txt>; landing <full40> |
```

Fill rules (frozen contract, `census/round-31/records/preregistration.txt` MACHINE BLOCK):

- C1 target is `unbound=0 mismatches=0` with `items=41` unchanged; only append-only rows
  `| Lnn | SCORECARD.md:<line> | <literal> | run: <argv> | <note> |` or `| ... | record: <path> | <note> |`
  may change the reading; `R30-CORRECTION` lines do not count (`tools/souji-capability-cells.py` docstring,
  lines 8-31).
- C2 target is `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same`; `real=2` is a fixed
  do-not-degrade value, not a floor that may grow.
- C3 v1 and v2 both must meet; v2 leg L12 (PATH-shim reality leg) is amendment A0, timestamped
  `2026-10-26T03:16:18-03:00` in `census/round-31/records/amendments.txt` before wave 1 was dispatched.
- Every claim must hold at its own landing commit **and** at the final lane tip; the closing line under the
  table in r30 style is:
  `Owned scores <unchanged (calibration 7, coverage 8, operability 8) | …>: <reason>. The final-tip re-measurement of all three claims is committed in the records directory right after this table lands (final-tip-measure.txt). <Round admission line>.`

## 2. `### Round 31 capability rows (appended)` — one line per claim

Column layout of `SCORECARD.md` r30 capability table (`| name | what it can now do | evidence pointer | first-working round |`):

```
### Round 31 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| capability-cell binding audit (r31) | reads the SCORECARD capability cells themselves, not an append-only correction block, and binds each of the 41 enumerated count literals to a run whose command prints it or to an unchanged record of the row's own round; independent of the r30 literal-agreement audit over `R30-CORRECTION` lines | `census/round-31/records/c1-before.txt` (`unbound=22 mismatches=34`) -> <census/round-31/records/c1-after.txt> (`unbound=0 mismatches=0`); `census/round-31/c1-cells.tsv` (41 items) | r31 |
| landing-gate reading precision (r31) | the landing gate reads the written record: it unions `.ufo/waves/round-N/` with `census/round-N/waves/`, reads every `## Seat-reported failures` section including append-only carries, and resolves ellipsis placeholders, en-dash line ranges, `.captured` names, `%d` templates and prose slash alternations without tokenizer false positives | `census/round-31/records/controls.tsv` (`fp=13 … fixture=fail redarm=fail`) -> <c2-after-v1.txt> (`fp=0 … fixture=ok redarm=ok`); fixture contract G1-G10 in `census/round-31/records/preregistration.txt`; <red-before receipt> | r31 |
| jj dropped-keep-ref object-clock fixture (r31) | a real jj 0.45.1 + git 2.56.0 fixture that measures what keeps an abandoned commit's object present after its own keep ref is dropped (descendant keep ref, reflog) and what removes it; L12 observes the fixture actually calling `jj abandon`/`jj util gc` and `git reflog expire`/`gc`/`cat-file -e` through a PATH shim, so the record is bound to reality rather than to a `cat` of itself | `census/round-31/records/controls.tsv` (v1 `fail=10`, v2 `fail=11`) -> <c3-after-v1.txt>, <c3-after-v2.txt>; `tests/fixtures/<r31-jj-object-clock>.sh`; record `<census/round-31/records/jj-object-lifetime-run.txt>` | r31 |
```

First-working-round cell follows r30 house style: `r31` when both the v1 reading and the amended reading pass,
`r31 (<claim status note>)` when the capability runs but the claim missed.

## 3. `### Planned (appended at round 31)`

```
### Planned (appended at round 31)

- **r32 (planned r31):** <planned>
```

`<planned>` is filled by the L1 from `corpus/lessons/round-31.md` `## Residuals` at integration; no residual may
be promoted to a target after data (preregistration closing rule).

## 4. LOG.md entry skeleton

Append after the last line of `LOG.md` (r31 style mirrors the last entry, `## 2026-10-26 — Round 30 attempt 1`):

```
## 2026-10-26 — Round 31 attempt 1: <one clause per claim, e.g. capability-cell binding, landing-gate reading precision, F1 dropped-keep-ref object lifetime>

Preregistration 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 and controls ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc (base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc) before any seat data; start census rc <0> (`census/round-31/records/census-start.txt`). Wave-1 attacks led to <no amendment beyond A0 | stricter-only amendment(s) <ids> at <rev>> (`census/round-31/records/amendments.txt`); A0 (C3 v2 reality leg) was landed by the L1 before wave 1 dispatched.
- C1 calibration (<landing full40>): capability-cell literals `items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` -> `unbound=<n> mismatches=<n>`; <n> append-only `Lnn` binding rows; <met | missed by the frozen kill rule, reason>.
- C2 operability (<landing full40>): landing gate `fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same` -> `fp=<n> real=2 cne=0 r26=<n> fixture=<ok|fail> redarm=<ok|fail> regress=same`; fixture G1-G10 `cases=<n> pass=<n> control=<…>` (base <n>/10); <met | missed, reason>.
- C3 coverage (<landing full40>): `corpus/knowledge/jj-dropped-keep-object-lifetime.md` (`ground: F1`), rows <S2xx> new, fixture `tests/fixtures/<…>.sh`, record `<…>`; v1 `legs=11 fail=10 f1_entries=3` -> `legs=11 fail=0 f1_entries=4`, v2 `legs=12 fail=11` -> `legs=12 fail=0 f1_entries=4`; <met | missed, reason>.
- Mined mistake M1: append-only carry sections in `corpus/lessons/round-2{6,7,8}.md` with a disposition per entry (`open` or `resolved@<full40>`); shown able to fail by the base gate's per-round LG-SEAT-UNCARRIED count (`census/round-31/records/m1-red-before.txt`: round 26 findings=18 over 466 reports, round 27 29, round 28 19 + 2 dangling).
- Frontier: SOURCES rows <n> -> <n> (<S2xx ids>, each opened this round, `mined`), census rc <0> start and end; F1 row "<dropped keep ref object lifetime measured>" in `corpus/README.md`.
- QUALITY <Q67-Qn>, SKILL <rows/bullets>, PROVINCE boundary note. Lesson: `corpus/lessons/round-31.md`. Waves: w1 <n> seats, w2 <n> seats, <n> reports (`census/round-31/waves/`).
Owned axis scores <unchanged (calibration 7, coverage 8, operability 8) | changed …>. <No tools installed. >Certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged. <Round-admission sentence>.
```

## 5. Report skeleton — `/home/vgpnk/Projects/shokunin/.ufo/reports/round-31/souji.md`

Sections in the required order; house style copied from `/home/vgpnk/Projects/shokunin/.ufo/reports/round-30/souji.md`
(title line, italic-free terse bullets, `## Other report lines` for the tail labels):

```
# souji — round 31 report (attempt 1)

Lane repo `/home/vgpnk/Projects/shokunin/souji-shokunin`, branch `master`. Base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`. Final lane HEAD `<full40>`; `git ls-remote origin refs/heads/master` prints <that hash | …>, and `jj-lane.sh state` reads `<ahead=0 behind=0 tracked=0 untracked=0 | …>`. Lane L1: <SoujiR31>.

## Work performed

Declared claims (frozen in `census/round-31/records/preregistration.txt`, preregistration commit `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; controls `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc`; both landed before any seat ran):

- **C1 — calibration** (lowest non-retired axis, 7): every one of the 41 count literals in the SCORECARD capability cells is bound to an observable that shows it. Verdict: **<met|missed>**.
- **C2 — operability** (8): the landing gate reads the committed record as written, with no tokenizer false positives. Verdict: **<met|missed>**.
- **C3 — coverage** (8; F1 frontier "object lifetime behind a dropped jj keep ref"): one sourced, measured knowledge entry. Verdict: **<met|missed>**. <This is the round's sourced claim (<S2xx ids> opened this round). | …>

Work items:

- <commit> preregistration, three frozen counters, the 41-item C1 enumeration, start census, axis check `<claims=3 flags=<n>>`.
- <commit> do-nothing and junk controls, C1 base output, M1 red-before receipt.
- <commit?> wave-1 amendments, if any; otherwise state "no wave-1 amendment landed; A0 stood".
- <commit> C1 append-only SCORECARD binding rows.
- <commit> C2 gate change plus the frozen G1-G10 fixture and its red-before record.
- <commit> C3 entry, rows, fixture, record, F1 map row, docs.
- <commit> M1 carry sections in `corpus/lessons/round-2{6,7,8}.md`.
- <commit> wave-2 integration and append-only corrections.
- <commit> lesson, QUALITY, SCORECARD, LOG, end census.
- <commit> final-tip receipt `census/round-31/records/final-tip-measure.txt`.

Round shape: **two v1 waves**. W1 `souji-r31-w1` had <n> seats: <role n, …>. Flash roles were <n>/<n> and attack seats <n>/<n>. W2 `souji-r31-w2` had <n> seats: <role n, …>. Flash roles were <n>/<n> and attack seats <n>/<n>. Round total: **<n> seats**, <n> dead seats (`census/round-31/waves/w1-results.json`, `w2-results.json`). The L1 held the canonical planner seat.

## Landed changes

Each change ties to the `LOG.md` entry "2026-10-26 — Round 31 attempt 1: <title>" and to its commit:

| change | commit |
|---|---|
| preregistration, frozen counters, C1 enumeration, start census | `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` |
| controls (do-nothing + junk) and amendment A0 | `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc` |
| C1 base output and M1 red-before receipt | `1b811368461785040e955f41f9c97e62f61fd67c` |
| <C1 binding rows> | `<full40>` |
| <C2 gate + fixture> | `<full40>` |
| <C3 entry, rows, fixture, record, docs> | `<full40>` |
| <M1 carry sections> | `<full40>` |
| <wave-2 integration and corrections> | `<full40>` |
| <lesson, QUALITY, SCORECARD, LOG, end census> | `<full40>` |
| <final-tip receipt> | `<full40>` |

Inherited state: <the worktree state at round start and the watchdog attempt count>.

## Before → after measurements

- **C1** — `python3 -B tools/souji-capability-cells.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`.
  - Before, at base: `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` (`census/round-31/records/c1-before.txt`, rc 1).
  - After, at the C1 landing commit `<full40>`: `<SUMMARY line>` (`<receipt>`).
  - Final tip `<full40>`: `<same | reading>`.
  - **<Met|Missed>.** <honest split of the 34 base mismatches: UNBOUND n, RUN-MISMATCH n, other n>.
- **C2** — `python3 -B census/round-31/c2-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --fleet-root /home/vgpnk/Projects/shokunin`.
  - Before, at base: `fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same` (`controls.tsv`).
  - After, at the C2 landing commit `<full40>`: `<SUMMARY line>`.
  - Final tip `<full40>`: `<SUMMARY line>`.
  - **<Met|Missed>.** <cause of any residual fp; REDARM legs the base tool failed and passed>.
- **C3** — `python3 -B census/round-31/c3-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; A0 `census/round-31/c3-counter-v2.py` same args.
  - Before, at base: v1 `legs=11 fail=10 f1_entries=3`; v2 `legs=12 fail=11 f1_entries=3`.
  - After, at the C3 landing commit `<full40>` and again at the final tip: v1 `<SUMMARY>`; v2 `<SUMMARY>`.
  - **<Met|Missed>.** <sentences refuted by wave 2 and corrected append-only, if any>.

No-harm counters, base → final tip (`final-tip-measure.txt`; wave-2 no-harm seats):

| counter | base → final tip |
|---|---|
| capability-literal agreement (r30 instrument) | `<k1=0 k2=0 mismatches=0>` → `<same>` |
| coverage agreement | `<grounded=<n> mapped=<n>>` → `<…>` |
| declared-evidence | `<mismatches=<n>>` → `<n>` |
| r30 receipts counter | `<manifests=… failed=0 uncovered=0>` |
| round-31 capture verify | `<records=<n> failed=0 uncovered=0>` |
| every lane fixture/selftest green at base | <still green at the tip (n commands, 0 harms) | …> |

<Owned scores line.>

## Sources & frontier

- **SOURCES rows:** `git show <rev>:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` gives <n> at base `9f17a1ef…` and <n> at the tip `<full40>`.
- **Rows added by tier:** <(tier)=n — S2xx (<title>, <kind>, docs|spec)>.
- **Rows touched (old → new):** <S0xx/S1xx `used-by` additions, logged in `corpus/lessons/round-31.md` `### SOURCES touched-row log`>.
- **Census:** `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
  - Start: `census/round-31/records/census-start.txt` (<rc>, <W04 count>).
  - End: `census/round-31/records/census-end.txt` (<rc>, <W04 count>).
- **Frontier advanced:** F1 "<what is now measured>" (`corpus/README.md` `<section>`, F1 map row). <F1 stays frontier | F1 retires>.
- **Mined mistakes:** `corpus/lessons/round-31.md` `## Mistakes`; M1 red-before `census/round-31/records/m1-red-before.txt`.
- **Sourced claim:** <C3>.
- **Assimilation:** <none | rows appended/rejected per entry>.
- **considerthese/:** <absent in this lane | …>.
- **Gate:** <at least one admit and one reject recorded for the closure's spot-check>.

## Trend verdicts

- **expansion — <improved|unchanged>.** <one entry on F1 ground the map listed as unmeasured, rows opened this round; counter-argument on record>.
- **quality — <improved|unchanged>.** <cell literals now bound, carried failures, corrected receipts>.
- **discernment — <unchanged|improved>.** <outside spot-check status; criteria ids>.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — SKILL.md Gate registry rows `<…>`; error-pattern bullet `<…>`; corpus/SOURCES.md `<S2xx>`
- [~] At least one end-to-end domain task executed and logged in LOG.md — LOG.md:362 (2026-10-19 operator sweep); round 31 LOG entry at the end of LOG.md
- [~] Instructions executable by an agent without oral context — census/round-31/records/final-tip-measure.txt (every claim re-measured from committed bytes by documented commands); `tests/fixtures/<…>` `<cases=n pass=n>`
- [~] No cross-domain bleed (PROVINCE.md still accurate) — PROVINCE.md `## Round 31 boundary note (<…>)`; census/round-31/waves/w1/`<connector report>` and w2/`<…>` (zero contested scope)

## Other report lines

- **Cross-domain evidence encountered:** <sibling scans, fleet-tooling ground reported not absorbed; untracked fleet-root files not touched>.
- **Misroot sweep:** `git -C /home/vgpnk/Projects/shokunin status --porcelain` <showed | …>; <no copy or delete needed | …>.
- **Stale-lane:** this mission launched `<ISO timestamp>` (`.ufo/watchdog.log`); <lane commits since launch>. <No other mission of this lane is open | …>.
- **Tool installs:** <none, by the L1 or any seat. pacman stayed paused. | tool version, channel, reason>.
- **Scratch:** `/fast/scratch/hyaku/souji-r31` <was removed after landing | …>.
- **Open L0 questions:** <none filed this round | Qnn: …>.
- **Residuals routed to r32:** <list, mirrored in SCORECARD `### Planned (appended at round 31)` and the lesson's `## Residuals`>.
```
