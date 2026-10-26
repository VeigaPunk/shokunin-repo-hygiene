# Round 30 records skeleton (r30 attempt 1, wave 1)

Drafted by SwarmScribe19 from committed bytes; **nothing here was measured by me**. Every `<...>`, `<after>` and `<commit>` is an L1 fill slot. Do not paste a placeholder as a result.

Frozen sources (read this run):

- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/preregistration.txt`, commit `d4928ec86b667e3d1ed0adb07fb088e500cf1631`; lines 5, 7, 9 are C1/C2/C3.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/controls.tsv`, commit `bae103cba91884947a0557940e60c320f5512f75`; do-nothing and junk rows.
- Lane base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; C1 list-rev `d4928ec86b667e3d1ed0adb07fb088e500cf1631`.

Layout references: `SCORECARD.md:299-307` (Round 29 measurements table + owned-scores line), `SCORECARD.md:309-314` (Round 29 capability rows), `SCORECARD.md:316-318` (Planned), newest `LOG.md` entry (Round 29 attempt 1), `/home/vgpnk/Projects/shokunin/.ufo/reports/round-29/souji.md`.

All runner invocations use absolute paths; pointer cells also use absolute lane paths so no cell depends on a cwd.

---

## (1) SCORECARD section — append after `SCORECARD.md:318`

```markdown
### Round 30 measurements (2026-10-26; base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b; preregistration d4928ec86b667e3d1ed0adb07fb088e500cf1631)

Frozen targets (preregistration.txt:5, 7, 9), required at the landing commit and again at the final lane tip: C1 `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10`; C2 `SUMMARY reports=86 cne=0 dangling=0 ... fixture=ok redarm=ok regress=same` with exit 0 (`other=` is reported, not targeted); C3 `SUMMARY legs=9 fail=0 f1_entries=3`.

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 capability-statement agreement | calibration 7 | `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10` (do-nothing control; junk controls `k1=2`, `1`, `1` — `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/controls.tsv`) | `<after>` | `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631` | `<commit>` |
| C2 committed-capture report discovery | operability 8 | `SUMMARY reports=0 cne=1 dangling=3 other=0 fixture=fail redarm=fail regress=same` (do-nothing control; junk control reaches the after shape but `redarm=fail regress=differs` — same `controls.tsv`) | `<after>` | `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --fleet-root /home/vgpnk/Projects/shokunin` | `<commit>` |
| C3 F1 keep-ref expiry entry | coverage 8 | `SUMMARY legs=9 fail=8 f1_entries=2` (do-nothing control; junk control `legs=9 fail=5 f1_entries=3` — same `controls.tsv`) | `<after>` | `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40>` | `<commit>` |

Owned scores `<calibration>`, `<coverage>`, `<operability>` after the round; `<disclosures>`; `<round admission>`.
```

Notes for the fill:

- C1's target omits the trailing `rev=<full40>` that the counter prints (`census/round-30/records/c1-before.txt:29` ends `... pointers=10 rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`). Quote the frozen literal as-is; disclose the `rev=` suffix in `<disclosures>` if the tip SUMMARY carries it (Round 29 disclosed the same shape).
- C2's target is quoted with the prereg's own ellipsis because `other=` sits between `dangling=` and `fixture=`; if the L1 wants a whole-line literal, write the observed line and mark `other=` as reported-not-targeted.
- 86, per prereg line 7, is `git ls-tree -r --name-only 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b census/round-29/waves | grep -c '\.md$'` — cite that derivation if the cell needs it.

---

## (2) SCORECARD section — append after (1)

```markdown
### Round 30 capability rows (appended, not inserted: keep SCORECARD.md append-only since the preregistration commit)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| capability-statement agreement audit (r30) | at a full 40-hex revision and a prereg list-rev, re-run each enumerated capability-table command and resolve each SHONEN pointer token against committed bytes, then report every stated count literal the command's last digit-bearing line contradicts and every unresolvable token unless an append-only `R30-CORRECTION` line records the observed `rc` and `observed` while keeping the row's script path | `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c1-rows.tsv` (`rows=18 pointers=10`); base `mismatches=13` -> `<after>`; `<fixture receipt>` | r30 |
| committed-capture report discovery (r30) | evaluate a round's committed `census/round-<N>/waves/**.md` capture when the gitignored `.ufo/waves/round-<N>/` is absent, read the dirty copy without double-counting when both exist, ignore template tokens, resolve capture-mapped report pointers, and flag an uncarried `STATUS: FAIL`; its D1-D7 fixture rejects the always-zero emitter and the base tool fails at least one case | `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r30-landing-gate-discovery.py` `cases=<N> pass=<M> control=FALSE-GREEN-REJECTED`; base `redarm=fail` -> `<after>` | r30 |
```

`<N>` must be >= 7 per the D1-D7 contract (preregistration.txt:7). If C1 lands no fixture, delete the `<fixture receipt>` slot rather than inventing a path — the frozen C1 target names none.

---

## (3) SCORECARD section — append after (2)

```markdown
### Planned (appended at round 30)

- **r31 (planned r30):** <planned>
```

Keep it to the lane's next move only; Round 29's bullet style is one wrapped line naming each axis move plus carried defects.

---

## (4) LOG.md entry — append at end of `/home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md`

```markdown
## 2026-10-26 — Round 30 attempt 1: capability-statement agreement, committed-capture report discovery, F1 keep-ref expiry

Claims frozen in `census/round-30/records/preregistration.txt` at d4928ec86b667e3d1ed0adb07fb088e500cf1631 (base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b) with do-nothing and junk controls (`records/controls.tsv`); start census `records/census-start.txt` rc 0; `python3 -B tools/souji-axis-check.py` `claims=3 flags=0`.
- C1 calibration (<commit>): `k1=13 k2=0 mismatches=13` -> `<after>`; `<n>` append-only `R30-CORRECTION` lines in `SCORECARD.md`/`SHONEN.md`; instrument `tools/souji-capability-agreement.py`, fixture `<cases>`.
- C2 operability (<commit>): `reports=0 cne=1 dangling=3` -> `<after>`; the landing gate now evaluates the committed `census/round-29/waves` capture (`reports=86`), template tokens and capture-mapped pointers no longer dangling; fixture `tests/fixtures/r30-landing-gate-discovery.py` D1-D7 `cases=<N> pass=<M> control=FALSE-GREEN-REJECTED`, base tool red; REGRESS unchanged (`SELFTEST pass=65 fail=0`, r16 `SUMMARY total=15 failed=0`).
- C3 coverage (<commit>): F1-grounded entries 2 -> `<after>`; `legs=9 fail=8` -> `<after>`; entry `corpus/knowledge/jj-keep-ref-expiry.md` measured with real jj (`census/round-30/records/jj-keep-expiry-run.txt`, fixture `tests/fixtures/r30-jj-keep-expiry.sh`), rows `<S-ids>`, snapshot `<paths>`, README F1 map row, PROVINCE/SKILL/QUALITY `<ids>`.
- Lesson `corpus/lessons/round-30.md`; SCORECARD Round 30 table, capability rows, r31 plan; wave: `<seats>` seats, `<reports>` reports (`census/round-30/waves/`).
Owned axis scores `<calibration/coverage/operability>`; `<round admission>`. Routed r29 defects: `<map>`. `considerthese/` absent; assimilation `<admit/reject in the lesson Gate>`. No tools installed. Certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged.
```

---

## (5) Report skeleton for `/home/vgpnk/Projects/shokunin/.ufo/reports/round-30/souji.md`

```markdown
# souji round 30 (attempt 1) — report

Lane HEAD `<full40>` (pushed state `<ls-remote result>`). Base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; frozen preregistration commit `d4928ec86b667e3d1ed0adb07fb088e500cf1631` (`census/round-30/records/preregistration.txt`, controls `bae103cba91884947a0557940e60c320f5512f75`).

## Work performed

Declared claims: **C1 calibration** (capability-table count statements agree with the committed commands), **C2 operability** (landing gate evaluates a round's committed reports), **C3 coverage** (F1 keep-ref expiry entry). Axes calibration 7 (lowest non-retired), operability 8, coverage 8; causally separable by landing commit; `python3 -B tools/souji-axis-check.py` `claims=3 flags=0` (`records/axis-check-before.txt`).

- Frozen counters and do-nothing/junk controls committed before any wave seat scored (`bae103c`): C1 base `k1=13 k2=0 mismatches=13`, C2 `reports=0 cne=1 dangling=3`, C3 `legs=9 fail=8 f1_entries=2`; junk states in `records/controls.tsv`.
- One `<v1|v2>` wave, `<seats>` seats (below).
- C1 (`<commit>`): `<edits and/or append-only correction count>`; instrument `tools/souji-capability-agreement.py`, `<fixture>`.
- C2 (`<commit>`): landing-gate discovery over `census/round-29/waves/`, fixture `tests/fixtures/r30-landing-gate-discovery.py` (`<cases>`), `<base-tool red arm>`.
- C3 (`<commit>`): `corpus/knowledge/jj-keep-ref-expiry.md` (jj receipt `census/round-30/records/jj-keep-expiry-run.txt`), rows `<S-ids>`, snapshot `<paths>`, map/docs `<ids>`.
- Lesson `corpus/lessons/round-30.md`; LOG entry; SCORECARD Round 30 table, capability rows, r31 plan.
- Misroot sweep (`git -C /home/vgpnk/Projects/shokunin status --porcelain`, no pathspec): `<untracked/tracked entries observed; nothing copied or deleted>`.
- Inherited: `<parked-seat edits, stray writes, sibling artifacts>`.

## Landed changes

| change | LOG entry | commit |
|---|---|---|
| freeze: counters, controls, start census, prereg | LOG Round 30 | d4928ec86b667e3d1ed0adb07fb088e500cf1631 |
| `<C1 change>` | LOG Round 30 | `<commit>` |
| `<C2 change>` | LOG Round 30 | `<commit>` |
| `<C3 change>` | LOG Round 30 | `<commit>` |
| lesson, SCORECARD, LOG, r30 wave capture, end census | LOG Round 30 | `<commit>` |
| `<pointer repairs>` | — | `<commit>` |

## Before -> after measurements

| claim | counting command | before (base) | after | measured commit |
|---|---|---|---|---|
| C1 | `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631` | `k1=13 k2=0 mismatches=13` | `<after>` | `<commit>`; re-run at `<tip>` |
| C2 | `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --fleet-root /home/vgpnk/Projects/shokunin` | `reports=0 cne=1 dangling=3 other=0 fixture=fail redarm=fail regress=same` | `<after>` | `<commit>`; re-run at `<tip>` |
| C3 | `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40>` | `legs=9 fail=8 f1_entries=2` | `<after>` | `<commit>`; re-run at `<tip>` |

Verdicts: `<C1/C2/C3 verified or missed, per the frozen kill rules>`. Honest disclosures: `<literal-shape deviations, unrun legs, inherited edits>`.

## Sources & frontier

- Rows before→after: `<n>` → `<n>` — `grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` (git show base vs tip). Census before `records/census-start.txt` (rc 0), after `records/census-end.txt` (`<rc, warning deltas>`).
- Rows added by tier: `<S-ids by tier>`, opened `<dates>`, quotes in the lesson `## Gate`.
- Rows touched old→new (`<cells>`): `<S-ids>`.
- Assimilation: `<admit/reject with flips>`; `considerthese/`: absent in this lane.
- Mined mistake (`## Mistakes`): `<mistake>` with its red-before at base; QUALITY `<Q-ids>` added citing the lesson.
- Sourced claim: C3 rests on `<S-ids>`. Frontier advanced: F1 keep-ref expiry gains one entry (`<still frontier | promotion>`).

## Trend verdicts

- expansion — `<improved | flat>`: `<evidence>`.
- quality — `<improved | flat>`: `<evidence>`.
- discernment — `<improved | unprovable-but-better>`: `<attack seats' effect on the claims>`.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — `<evidence: SKILL rows, SOURCES ids, lesson Gate>`.
- [~] At least one end-to-end domain task executed and logged in LOG.md — `<LOG entry; end-to-end receipt path>`.
- [~] Instructions executable by an agent without oral context — `<counter/fixture paths and case counts>`.
- [~] No cross-domain bleed (PROVINCE.md still accurate) — `<PROVINCE note; sibling-overlap scan path>`.

## Cross-domain evidence encountered

- `<lane/report pointer and what was encountered; "none encountered" is a valid fill>`

## Stale-lane

`<one line: driver state; any other open mission of this lane>`

## Tool installs

`<one line: none | tool, version, channel, reason>`

## Round shape

`<one line: wave count and ids, seats, role mix with flash/attack counts, dead seats, dispatch delays>`
```

---

## Filling hints (not part of any deliverable text)

- Wave-1 receipts already on disk when this skeleton was drafted, under `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/`: `deliver-c1-corrections-R01-R06.txt`, `deliver-c1-corrections-R07-R12.txt`, `deliver-c1-corrections-R13-R18.txt`, `c1-corrections-acceptance.txt`, `c1-stability-R03-R06.txt`, `deliver-souji-landing-gate.py`, `deliver-souji-landing-gate.diff`, `deliver-gate-root-cause.md`, `deliver-r30-landing-gate-discovery.py`, `deliver-c2-fixture-red-before.txt`, `receipt-c2-fixture-arms.txt`, `deliver-r30-jj-keep-expiry.sh`, `deliver-jj-keep-expiry-run.txt`, `receipt-SwarmExecutor06-keepref-mechanism.txt`, `receipt-SwarmExecutor01-*.txt`, `deliver-fetch-receipts.tsv`, `sources/`. Treat them as inputs to fill, not as verified results.
- The C1 counter prints `rev=` on its SUMMARY; keep the frozen target literal verbatim in the table and disclose the suffix once, as Round 29 did.
- Do not restate a capability count (e.g. `cases=20 pass=20`) until the fixture run receipt for r30 exists; that number is exactly what C1 audits.
