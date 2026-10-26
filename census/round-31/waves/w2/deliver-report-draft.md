# souji — round 31 report (attempt 1) — DRAFT (wave 2 in flight)

Lane repo `/home/vgpnk/Projects/shokunin/souji-shokunin`, branch `master`. Base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`. Final lane HEAD `<final>` (this draft measures `2c16d018e40db7c23420a2c3bb546b52957bcc25`); `git ls-remote origin refs/heads/master` prints `<final>`; `jj-lane.sh state` reads `<final>`. Lane L1: SoujiR31. Report commit `<final>`.

## Work performed

Declared claims (frozen in `census/round-31/records/preregistration.txt`, preregistration commit `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; controls and amendment A0 `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc`; wave 1 was dispatched after both landed):

- **C1 — calibration** (lowest non-retired axis, 7): every enumerated capability-cell count literal is bound to an observable that shows it at the revision, either a `run:` that prints it or an unchanged `record:` of the row's own round. Verdict: **missed** by the frozen kill rule at its landing commit `24f343c8ffc820c0f89b4252cbdc94ab9a673aab`: 41 items, `unbound=1 mismatches=1` against the target `unbound=0 mismatches=0`. The one item is L29 (`remote-source-after.json18/18`, SCORECARD.md:170); its record states the count only as separate scalar fields (`"matched_command_count": 18`), so the L1 recorded no binding rather than a dishonest one. The reading is unchanged at the draft tip.
- **C2 — operability** (8): `tools/souji-landing-gate.py` reads the committed record as written — union discovery of `.ufo/waves/round-N/` and `census/round-N/waves/`, every `## Seat-reported failures` section, and a tokenizer that keeps real missing paths while ignoring ellipses, line ranges, `.captured` names, printf templates and prose alternations. Verdict: **met** at its landing commit `8024b540b04d677d47cf51a0d1132ec8705ef14a` and at the draft tip, including the stricter A3 SHIFT leg under A5's random probes.
- **C3 — coverage** (8; F1 frontier "the object-prune clock behind a dropped keep ref is unmeasured"): one sourced, measured knowledge entry admitted with `ground: F1`. Verdict: **met** at its landing commit `1baf4da02b71b012ee2426ea7c309496c0c3aca0` and at the draft tip under v1, A0 v2 and A1 v3.

Work items:

- Preregistration, the three frozen counters, the 41-item C1 enumeration `census/round-31/c1-cells.tsv`, axis check (`claims=3 flags=0`) and start census: commit `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`.
- Do-nothing and junk controls scored with the frozen counters (`census/round-31/records/controls.tsv`) and stricter amendment A0 (C3 v2 reality leg): commit `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc`.
- C1 base output (`c1-before.txt`: `unbound=22 mismatches=34`) and M1's red-before receipt (base gate rounds 26/27/28: 18/29/21 findings, `carry_heading=0`): commit `1b811368461785040e955f41f9c97e62f61fd67c`.
- Wave-1 attacks produced stricter amendments A1 (C3 v3 remover subtraction), A2 (C1 count shape) and A3 (C2 v2 SHIFT), with amended controls: commit `26153a421374db2497e451230f33b2af78b3d128`.
- Append-only correction to the amendment record (shell-dropped backticked spans restored; no rule changed): commit `52ebd480461b481aeabadf143881223290c6fea2`.
- C2: the gate change, the 10-case precision fixture `tests/fixtures/r31-landing-gate-precision.py` and its red-before record: commit `8024b540b04d677d47cf51a0d1132ec8705ef14a`.
- C3: `corpus/knowledge/jj-dropped-keep-object-lifetime.md`, row S222, fixture `tests/fixtures/r31-jj-object-clock.sh`, record `census/round-31/records/jj-object-clock-run.txt`, tag-pinned snapshots, the F1 map row, README/PROVINCE/SKILL text (incl. the routed r30 SKILL keep-ref bullet fix), and the C2 landing measurements: commit `1baf4da02b71b012ee2426ea7c309496c0c3aca0`.
- Stricter amendment A4 (C1 record/run binding rules) and its four cheat-shape controls; C3 landing measurements: commit `6fdd69673e3aec5ef64ce4f9f25f452c4f4447d3`.
- C1: 40 append-only supersession rows under `### Round 31 capability-cell supersessions` at the end of `SCORECARD.md`; L29 has no row: commit `24f343c8ffc820c0f89b4252cbdc94ab9a673aab`.
- M1 mined-mistake fix: append-only `## Seat-reported failures` carries for rounds 26, 27 and 28 (26 + 29 + 19 entries, each with `open` or `resolved@<40hex>`); C1 landing measurements at the C1 commit: commit `c6108301cbf0ca0ad086ff0ece6b76adad6b74b6`.
- Wave-1 capture, stricter amendment A5 (C2 v3 random SHIFT probes) with the landed claim re-measured, the M1 after-receipt and the routed r30 defect-3 A1-regex receipt: commit `2c16d018e40db7c23420a2c3bb546b52957bcc25`.
- Wave 2 (falsify what landed): 36 seats dispatched from `census/round-31/waves/w2-spec.json`; no wave-2 result is integrated at this draft, and every after-value below was re-run by the scribe seat at `2c16d018…` (`deliver-tip-measure.txt`).

Round shape: **two v1 waves**. W1 `souji-r31-w1` had 38 seats (executor 10, scribe 9, scout 4, critic 4, reviewer 3, mutation-tester 3, connector 2, sentinel 1, revenger 1, simplifier 1; `census/round-31/waves/w1-spec.json`). Flash roles were 26/38 and attack seats 10/38 (`census/round-31/waves/w1/SwarmSimplifier38.md` line 4). W2 `souji-r31-w2` was dispatched with 36 seats (critic 10, executor 6, scribe 6, reviewer 5, mutation-tester 3, scout 2, connector 2, sentinel 1, simplifier 1; `w2-spec.json`); its result count and flash split are `<final>`. Round total: **74 planned seats**. The L1 held the canonical planner seat and is the single integration owner. Wave-1 capture: `census/round-31/waves/w1/`; the tip gate's deduplicated union reads `checked_reports=60`.

## Landed changes

Each change ties to its commit; the `LOG.md` entry naming them lands with the lesson at close.

| change | commit |
|---|---|
| preregistration, frozen counters, C1 enumeration, start census | `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` |
| controls + amendment A0 | `ed17ff6d95cc35d95038fdaef0e7e51c8e5d6bfc` |
| C1 base output, M1 red-before | `1b811368461785040e955f41f9c97e62f61fd67c` |
| amendments A1-A3, amended controls | `26153a421374db2497e451230f33b2af78b3d128` |
| amendment-record correction | `52ebd480461b481aeabadf143881223290c6fea2` |
| C2 gate + precision fixture + red-before | `8024b540b04d677d47cf51a0d1132ec8705ef14a` |
| C3 entry, S222, fixture, record, snapshots, docs, C2 measurements | `1baf4da02b71b012ee2426ea7c309496c0c3aca0` |
| amendment A4 + controls, C3 measurements | `6fdd69673e3aec5ef64ce4f9f25f452c4f4447d3` |
| C1 supersession rows (40) | `24f343c8ffc820c0f89b4252cbdc94ab9a673aab` |
| M1 carries rounds 26-28, C1 landing measurements | `c6108301cbf0ca0ad086ff0ece6b76adad6b74b6` |
| wave-1 capture, amendment A5, M1 after, A1-regex receipt | `2c16d018e40db7c23420a2c3bb546b52957bcc25` |

Inherited state: the worktree was clean at round start and is clean at `2c16d01` (`git status --porcelain` empty). Nothing was inherited and nothing was discarded.

## Before → after measurements

- **C1** — `python3 -B tools/souji-capability-cells.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` (v1 is the blob at `1d45496`; A2+A4 is the current file, sha256 `edf0933d…`).
  - Before, at the prereg content: `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` (`census/round-31/records/c1-before.txt`; do-nothing row of `controls.tsv`).
  - At the C1 landing commit `24f343c8ffc820c0f89b4252cbdc94ab9a673aab`: `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` under v1 and under A2+A4 (`c1-after-v1.txt`, `c1-after-a4.txt`); the only item line is `ITEM L29 SCORECARD.md:170 literal=18/18 base-cell binding=- UNBOUND`.
  - Draft tip `2c16d018…`: the same reading under v1 and under A2+A4 (scribe re-run, `deliver-tip-measure.txt`).
  - **Missed.** The frozen kill rule requires `unbound=0 mismatches=0` at the landing commit and at the tip. A4 recorded this before landing (it disclosed the one-item miss), and the cell text still states the old literal, superseded by 40 dated rows rather than edited.
- **C2** — `python3 -B census/round-31/c2-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --fleet-root /home/vgpnk/Projects/shokunin`, plus A3 `c2-counter-v2.py` and A5 `c2-counter-v3.py` with the same arguments.
  - Before, at the prereg content: `SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same` (`controls.tsv`); under A3 SHIFT the base gate legs fail (`controls-amended.tsv`).
  - At the C2 landing commit `8024b540b04d677d47cf51a0d1132ec8705ef14a`: v1 `SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same` (`c2-after-v1.txt`); v2 `… shift=ok` (`c2-after-v2.txt`); v3 two random-probe runs `… shift=ok` plus the base-gate control `fp=13 … r26=466 … shift=fail` (`c2-after-v3.txt`).
  - Draft tip `2c16d018…`: v1 the landing reading; v3 two runs with distinct random probes, both `shift=ok` (scribe re-run, `deliver-tip-measure.txt`).
  - **Met** under the v1 target and both stricter amendments. A5 landed after the claim (`2c16d01`) and re-measured the landed claim; it changed the counter, not the gate blob (`git diff 8024b54..2c16d01 -- tools/souji-landing-gate.py` is empty).
- **C3** — `python3 -B census/round-31/c3-counter.py --root <lane> --rev <full40> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, plus A0 `c3-counter-v2.py` and A1 `c3-counter-v3.py`.
  - Before, at the prereg content: v1 `SUMMARY legs=11 fail=10 f1_entries=3`; v2 `SUMMARY legs=12 fail=11 f1_entries=3` (`controls.tsv`, do-nothing rows).
  - At the C3 landing commit `1baf4da02b71b012ee2426ea7c309496c0c3aca0`: v1 `legs=11 fail=0 f1_entries=4`; v2 `legs=12 fail=0 f1_entries=4`; v3 `legs=13 fail=0 f1_entries=4` (`c3-after-c3-counter*.txt`).
  - Draft tip `2c16d018…`: the same three readings, with `L12 … jj_calls=26 git_calls=111 missing=[]` and `L13 … M1 … no=0<4=True M2 … no=0<4=True` (scribe re-run, `deliver-tip-measure.txt`).
  - **Met** under the v1 target and both stricter amendments.
- **M1 (mined mistake, not a claim)** — the lessons of rounds 26, 27 and 28 carried no `## Seat-reported failures` section, so their committed seat STATUS failures were uncarried.
  - Before, base gate blob at the prereg content: round 26 `findings=18`, round 27 `findings=29`, round 28 `findings=21` (19 `LG-SEAT-UNCARRIED` + 2 pre-existing `LG-DANGLING-PTR`), all `carry_heading=0` (`m1-red-before.txt`).
  - After at `c6108301…`, base gate: round 26 `findings=0`, round 27 `findings=0`, round 28 `findings=2` (the same two dangling pointers, zero uncarried); tip gate: 0/0/0 (`m1-after.txt`).

No-harm counters, base → draft tip (`deliver-tip-measure.txt`; every value is a run of this seat):

| counter | base → draft tip |
|---|---|
| coverage agreement | `grounded=16 mapped=16 dangling=0 mismatches=0` → `grounded=17 mapped=17 dangling=0 mismatches=0 kill_tested=16 kill_violations=0` |
| SOURCES census (`scripts/sources-census.sh validate --root <fleet> souji`) | exit 0, 36 W04 → exit 0, 36 W04 |
| round-31 landing gate (tip gate) | could-not-evaluate at `24f343c8` and `8024b54` (no committed round-31 reports yet) → `findings=7`, all `LG-SEAT-UNCARRIED`, 0 dangling, `checked_reports=60`; the carry is due in `corpus/lessons/round-31.md` at close |
| C1 counter at the tip | identical to its landing reading (no drift) |
| C2 gate + v3 counter at the tip | identical to their landing readings (no drift) |
| C3 v1/v2/v3 at the tip | identical to their landing readings (no drift) |
| registry agreement | `COULD-NOT-EVALUATE derived facts are trivial` at both the round-30 committed pair and the round-31 pair (`tools/souji-registry-agreement.py:115`); the r29 fixture still prints `cases=20 pass=20`. Pre-existing r29 instrument defect — filed as a finding, and no no-harm reading is claimed from it |

Owned scores are unchanged (calibration 7, coverage 8, operability 8).

## Sources & frontier

- **SOURCES rows:** `git show <rev>:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` gives 145 at base `9f17a1ef…` and 146 at the draft tip `2c16d018…`.
- **Rows added by tier:** A=1 — S222 (`git Documentation/git-reflog.adoc` at tag v2.56.0, docs, `mined`, opened 2026-10-26). `corpus/SOURCES.md:167` states its subject: "entries past the expire-unreachable time that are not reachable from the current tip".
- **Rows touched (old → new):** S002, S054, S063, S117 and S220 each gained `corpus/knowledge/jj-dropped-keep-object-lifetime.md` in `used-by`; S222 names that entry alone. The entry's six `source:` lines cite S222, S063, S002, S117, S220 and S054, so the Q62 bidirectional check has both directions.
- **Census:** `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
  - Start: `souji ok …/corpus/SOURCES.md`, exit 0, 36 W04 (`census/round-31/records/census-start.txt`).
  - End at the draft tip: exit 0, 36 W04, no error class (run by this seat; the L1 commits `census-end.txt` at close).
- **Frontier advanced:** F1 "the object-prune clock behind a dropped keep ref" is now measured — `corpus/README.md` `## Round 31 — F1 object lifetime behind a dropped keep ref` (:643), the F1 map row at `:39` names the sixth entry with status unchanged (`frontier, entries held`), and `PROVINCE.md:213` `## Round 31 boundary note` keeps F1 frontier. Remaining on F1: the fleet exposure numerator re-census; sourced but unmeasured edges (which reflog file carries the entry, cruft-pack handling, the real 90/30-day windows).
- **Assimilation:** no staged entry admitted (`deliver-assim-sweep.md`). The sweep rejected all 68 `shokuknow/merge/souji` entries for C3 use: no entry measures object lifetime behind a dropped keep ref, staged rows are opened 2026-10-23/24 (so C3's L6 fails verbatim), and 37 ids collide (S109-S132, S152, S210-S221). S222 was opened fresh this round; no package row was appended.
- **considerthese/:** absent in this lane.
- **Mined mistake:** M1 (rounds 26-28 uncarried seat failures), shown able to fail by the base gate's per-round `LG-SEAT-UNCARRIED` counts and cleared at `c6108301…`.
- **Sourced claim:** C3 (S222).

## Trend verdicts

- **expansion — improved, narrowly.** One admitted entry on F1 ground the map listed as unmeasured, measured this round with real jj 0.45.1 and git 2.56.0 (17-step fixture; `legs=11/12/13 fail=0`), and the map row now names it. Counter-argument on record: C1 missed its frozen target by one item, wave-2 refutations are still in flight, and A0/A1 disclose that C3's L4 fetch receipts are self-attested.
- **quality — improved.** The 40 supersession rows bind as many stated literals to a run or an unchanged record of the row's own round; C2's gate now reads the committed record (base 13 false dangling pointers over 466 reports → 0 over 495); rounds 26-28's seat failures are carried (18/29/21 findings → 0 uncarried); the routed r30 SKILL keep-ref bullet is fixed; the routed A1-regex defect has its receipt. Deduction: L29 stays unbound, and 7 wave-1 STATUS lines are uncarried at the draft tip because the round-31 lesson has not landed.
- **discernment — unchanged.** No outside spot-check of this round's gate decisions exists yet. Wave 2 is the falsifier and is in flight; A5 is the one amendment forced by a wave-1 attack. The round's own gate record has at least one admit (the entry and S222) and one reject (all 68 staged assimilation entries) for the closure's spot-check.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — `SKILL.md:116` (r31 jj rule: an object outlives its keep ref); `corpus/SOURCES.md:167` (S222)
- [~] At least one end-to-end domain task executed and logged in LOG.md — `LOG.md:362` (2026-10-19 operator sweep; the round-31 `LOG.md` entry lands with the lesson)
- [~] Instructions executable by an agent without oral context — `census/round-31/records/jj-object-clock-run.txt`; `tests/fixtures/r31-jj-object-clock.sh`; `census/round-31/records/frozen-digests.txt`
- [~] No cross-domain bleed (PROVINCE.md still accurate) — `PROVINCE.md:213` (Round 31 boundary note); `census/round-31/waves/w1/SwarmConnector35.md` (PASS: no sibling claims souji ground)

## Other report lines

- **Cross-domain evidence encountered:** the assimilation sweep read `shokuknow/merge/souji/` read-only (68 entries, 37 id collisions) and adopted nothing; connector seats swept 19 sibling lanes plus `scripts/hyaku/jj-lane.sh` and found no contested scope. Fleet-tooling ground, reported, not absorbed.
- **Misroot sweep:** `git -C /home/vgpnk/Projects/shokunin status --porcelain` shows only pre-existing `.scratch/` and `.tower/` entries; no souji round-31 path was written outside the lane.
- **Stale-lane:** the mission launch line in `.ufo/watchdog.log` was not re-read (the hard bound forbids touching it). The lane has 11 commits in `9f17a1ef…2c16d01`.
- **Tool installs:** none, by the L1 or any seat. pacman stayed paused.
- **Scratch:** `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe34` was removed after the deliveries were copied.
- **Open L0 questions:** none filed this round.
- **Residuals routed to r32:**
  - L29's record states its count as separate scalar fields, so the frozen record rule leaves it unbound.
  - A4's `record:` rule is file-granular, not line-granular.
  - A3's letters-only prose rule cannot tell `corpus/authority` from a real dangling `census/waves`.
  - The C1 tail scan is last-row-wins: any later `| Lnn | SCORECARD.md:<n> |` row in the append tail silently supersedes a binding (keep the 40 rows last, or keep measurement tables' first two cells distinct).
  - `tools/souji-registry-agreement.py:115` raises `COULD-NOT-EVALUATE derived facts are trivial` whenever the r29 counter's `r26` line reports `failed=0`; the r29 fixture does not exercise that guard.
  - The prereg's routed defect-5 process receipt `census/round-31/records/landing-gate-per-commit.txt` is not committed at the draft tip.
