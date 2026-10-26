<!--
Round-report skeleton for /home/vgpnk/Projects/shokunin/.ufo/reports/round-29/souji.md
Fill every <...> from measured bytes, then delete this comment. Marker rule (prompt §4): a contentless
report (placeholders, missing required sections other than Sources & frontier and Trend verdicts, no
evidence pointers) counts as the round FAILED. Sections below are in the required order; extras follow
SHONEN. No value here was measured by the L1: values shown were measured by this seat or the named seat
and are marked with their pointer; everything else stays a placeholder.
-->

# Souji round 29 — attempt 1

## Work performed

Declared claims: **C1 calibration** (lowest non-retired axis, score 7), **C2 operability** (score 8), and **C3 coverage** (score 8). They are frozen in `souji-shokunin/census/round-29/records/preregistration.txt` at base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; preregistration committed as `b8cb4b31ce80e2e3314b88e85d40ea9873180804`. No axis harmed: <state calibration/operability/coverage verdicts, one clause each>.

- **C1 — calibration (declared records agree with committed bytes):** <what changed: 6 SOURCES used-by/source disagreements + 4 stale r26-manifest statements corrected append-only>. Evidence: `souji-shokunin/tools/souji-registry-agreement.py`; before receipt `souji-shokunin/census/round-29/records/controls.tsv`; correction lines `souji-shokunin/LOG.md:<line>`, `souji-shokunin/SCORECARD.md:<line>`, `souji-shokunin/corpus/lessons/round-28.md:<line>`, `:<line>`; after receipt `souji-shokunin/census/round-29/records/<c1-after>.tsv`.
- **C2 — operability (wave-evidence receipts verify over committed bytes):** <what changed: capture tool verifies the committed set, nested `.gitignore` neutralised without dropping the file, ignored names accounted as excluded, symlinks recorded, fixture extended from 6 cases, r26 recaptured>. Evidence: `souji-shokunin/tools/souji-wave-evidence-capture.sh:<line>`; fixture `souji-shokunin/tests/fixtures/r28-wave-evidence-capture.sh`; counter `souji-shokunin/census/round-29/c2-counter.py`; after receipt `souji-shokunin/census/round-29/records/<c2-after>.tsv`; r26 manifest `souji-shokunin/census/round-26/waves/manifest.sha256`.
- **C3 — coverage (F3 duplicate-verdict theme assimilated):** two re-grounded entries admitted and four rows appended. Evidence: `souji-shokunin/corpus/knowledge/duplicate-verdict-identity.md`, `souji-shokunin/corpus/knowledge/duplicate-verdict-byte-equality.md`, rows `souji-shokunin/corpus/SOURCES.md:<S216-S219 lines>`, coverage-map row `souji-shokunin/corpus/README.md:<line>`, snapshots `souji-shokunin/census/round-29/sources/<files>`.
- **Frontier step:** `corpus/lessons/round-29.md` with a located Gate, one `## Mistakes` row (class · evidence pointer · captured-by none · fix shown red-before by C1/C2 at base), and the S216–S219 search log. Evidence: `souji-shokunin/corpus/lessons/round-29.md:<line>`.
- **Wave:** one validated v2 wave `souji-r29-w1`, <seat count measured below> seats; spec `souji-shokunin/.ufo/waves/round-29/w1-spec.json`, dispatch `souji-shokunin/.ufo/waves/round-29/w1-dispatch.json`, results `souji-shokunin/.ufo/waves/round-29/w1-results.json`. <one bullet per further work item, each with an evidence pointer>.

## Landed changes

| commit | LOG.md entry | what it carries |
|---|---|---|
| `b8cb4b31ce80e2e3314b88e85d40ea9873180804` | `LOG.md` Round 29 | frozen preregistration, counters, controls and start census |
| `<C1 landing full40>` | `LOG.md` Round 29 | <C1 corrections, used-by/status old->new log> |
| `<C2 landing full40>` | `LOG.md` Round 29 | <capture tool v2, fixture cases, r26 recapture + supersession log> |
| `<C3 landing full40>` | `LOG.md` Round 29 | <two entries, S216-S219, F3 coverage-map row, snapshots> |
| `<final tip full40>` | `LOG.md` Round 29 | <after receipts, SCORECARD pointers, census-end, r29 wave capture> |

Lane tip `<final tip full40>`; `<jj-lane.sh state output: local=remote=…, ahead=0, behind=0>`.

## Before → after measurements

- **C1 calibration — `mismatches` 10 → 0.** Counter: `python3 -B tools/souji-registry-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40> --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804`. Before at `691dd29211c53d0ef94fa072394cb9c8a69fe92e`: `k1=6 k2=4 mismatches=10` (`census/round-29/records/controls.tsv`; do-nothing control 10). After at `<C1 landing full40>` and again at `<final tip full40>`: `SUMMARY k1=0 k2=0 mismatches=0`, rc 0. Junk controls scored with the same counter: markers only 6, markers plus in-place phrase edit 10, blanked used-by 68, two junk `ground: F3` entries 12 — none 0.
- **C2 operability — `failed` 152 → 0, `uncovered` 14 → 0.** Counter: `python3 -B census/round-29/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <full40>`. Before at base: `manifests=3 failed=152 uncovered=14 floor_violations=0`, rc 1 (r26 152/14; r27, r28 clean). After at `<C2 landing full40>`: `manifests=3 failed=0 uncovered=0 floor_violations=0`, rc 0; at `<final tip full40>`: same zeros, `manifests=4` (round 29 captured by the improved tool). Fixture: `bash tests/fixtures/r28-wave-evidence-capture.sh` → `cases=<N> pass=<N> control=TAMPER-REJECTED`, rc 0 (was 6 cases). Floors held: r26 1230, r27 124, r28 <new record count>.
- **C3 coverage — F3-grounded entries 0 → 2; SOURCES rows 139 → 143.** Counters: `git grep -lE '^ground: F3' <rev> -- corpus/knowledge/ | wc -l` → 0 at base, 2 at `<C3 landing full40>`; `git show <rev>:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → 139 at base, 143 at `<C3 landing full40>`. Supporting: `python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>` → `grounded=15 mapped=15 dangling=0 mismatches=0` (base 13/13/0/0); `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries <two entries> --snapshot-dir census/round-29/sources --slice census/round-29/records/quarantine-slice --slice-verdicts census/round-29/records/slice-verdicts.tsv` → `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`; `sources-census.sh validate` rc 0; C1 counter at the C3 landing commit still `mismatches=0`.

Owned scores after: calibration `<7|8>`, operability `<8|9>`, coverage `<8|9>` — `<no scalar delta | delta + reason>`; the SCORECARD `### Round 29 measurements` table carries each row's counting command and measured commit.

## Sources & frontier

Census command (both ends): `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`.

- Before: 139 rows, malformed 0, tiers `<A=… B=… C=…>`, statuses `<mined=… queued=… rejected=…>`, duplicate IDs 0; validate exit 0, 35 W04 warnings. Full output: `souji-shokunin/census/round-29/records/census-start.txt`.
- After: 143 rows, malformed 0, duplicate IDs 0, enum/tier-inflation 0; tiers `<A=… B=… C=…>`; statuses `<mined=… queued=… rejected=…>`; validate exit 0. Full output: `souji-shokunin/census/round-29/records/census-end.txt`.
- Rows added by tier: `<S216 statx, S217 link, S218 cmp → tier <A|B>; S219 Broder (author-hosted PDF, DOI landing 202/0 bytes) → tier <B>>`, all `status: mined`.
- Rows touched old→new: `<none | S### status/recheck/used-by: old → new, logged in corpus/lessons/round-29.md>`.
- Frontier rows advanced: `<F3 status old → new; remaining frontier rows unchanged, and why>`.
- `Assimilation:` theme **F3 duplicate verdicts** from `/home/vgpnk/Projects/shokuknow/merge/souji/` (read-only): <what was assimilated, e.g. two re-grounded entries + four rows + re-check of the S118 Broder payload-absent register row>. `considerthese/` is absent in this lane, so no proposal was available; <re-check statement and its command>.

## Trend verdicts

- **expansion — `<improved|harmed|unchanged|unprovable-but-better>`:** <evidence: F3 0→2, rows 139→143, what ground the map now holds that it did not>.
- **quality — `<verdict>`:** <evidence: gate `ok=2 fail=0`, pins/snapshots re-verified, census rc 0, receipt verification over committed bytes; disclose any non-verifying item>.
- **discernment — `<verdict>`:** <evidence: non-author spot-check of one admit and one reject if on record; otherwise state plainly that dispatched lane seats cannot satisfy that duty>.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — `souji-shokunin/SKILL.md` <sections + gate-registry row added this round>; a checked box requires a named non-author verifier on record.
- [~] At least one end-to-end domain task executed and logged in LOG.md — `souji-shokunin/LOG.md` Round 29; <receipt/manifest path>.
- [~] Instructions executable by an agent without oral context — `souji-shokunin/tests/fixtures/r28-wave-evidence-capture.sh` (`cases=<N>`), `souji-shokunin/tools/souji-pre-report-gate.sh`.
- [~] No cross-domain bleed (PROVINCE.md still accurate) — `souji-shokunin/PROVINCE.md` <Refuses/Adjacency>; round-29 lesson Gate; `/home/vgpnk/Projects/shokuknow` stayed read-only.

<!-- Exactly one `^## SHONEN` heading; one `- [~]`/`- [ ]` line per SHONEN.md box (four boxes today).
     A checked box requires a named non-author verifier; a lane seat or the L1 cannot self-verify. -->

## Round shape, waves and seats

- Shape: **one v2 wave** (build + attack together), band 64–128. Wave `souji-r29-w1`, validated under `<policy path>`, reportDir `.ufo/waves/round-29/w1`; `<validator output: rc 0, seats=N>`.
- Seats: **68** (dispatch `w1-dispatch.json`, `tasks` length 68; ready marker `w1.ready` written 20:21). Role mix measured from the dispatch: executor 21, scribe 10, scout 7, reviewer 8, critic 8, mutation-tester 6, connector 3, sentinel 2, simplifier 2, revenger 1. Flash-role seats 44 of 68; attack seats (reviewer + critic + mutation-tester) 22 of 68 = 32%. Planner seat: held by the L1 (`SoujiR29`), never dispatched; <bounded planning data-walk seat, if any>.
- Round total: **68**; residual calls: `<none | n seats, roles>`.
- Dead seats: `<n>` — `<seat name: last error text>`, unreplaced, kept in the evidence. Source: `souji-shokunin/.ufo/waves/round-29/w1-results.json` (`<status counts>`), plus `<any seat that returned an aborted/WAIT payload without a report>`.

**Stale-lane:** `<not stale — this was the steered souji round 29 mission | stale because …, and why the round still landed>`.

**Tool installs:** `<none | tool version, channel, reason per install/upgrade>`. Tooling directive honored: no `pacman` transaction (host-wide pause), official channels only.

**Misroot sweep:** `git -C /home/vgpnk/Projects/shokunin status --porcelain=v1` → 22 entries (18 ` M`, 4 `??`: `.tower/`, `.ufo/reports/round-41/mado.md`, `.ufo/waves/round-30/`, `demo-cwd.txt`); none names souji round 29, and `demo-cwd.txt` holds only `/home/vgpnk/Projects/shokunin`, so no souji file was misrooted into the fleet root and nothing outside the lane was copied, moved or deleted (same shape measured at base by `souji-shokunin/.ufo/waves/round-29/w1/SwarmExecutor17.md` finding 6). End-of-round recheck: `<same 22 / n entries, none naming souji round 29>`.

**Inherited state:** lane HEAD at round start `b8cb4b31ce80e2e3314b88e85d40ea9873180804` equals the round base commit. Inherited dirty tracked path: `.ufo/waves/round-26/w1/ScribeGateDraft.md` (2 insertions, 1 deletion — an inbound round-31 coordination note; `git -C <lane> diff` at base) — `<kept as-is | committed through the helper | restored from master:`>. No earlier-attempt seat artifacts were present under `.ufo/waves/round-29/` before this wave (directory listing at 20:20 held only this attempt's `make-spec.py`, `w1-spec.json`, `w1-dispatch.json`, `w1-run.err`, `w1.ready`), so `<nothing inherited to re-verify | list what was reused and what was discarded>`. `census/operator-sweep-*` contents and `.scratch/`, `.ufo/state/`, `.ufo/watchdog.log` were not read or changed.

## Routed-defect disposition (six r28 closure defects)

Source: `souji-shokunin/corpus/lessons/round-28-verifier-spotcheck.md` section Routed defects. Disposition owner: `souji-shokunin/.ufo/waves/round-29/w1/SwarmReviewer45.md` <and its delivery file>; the L1 fills status at landing.

| # | defect | addressed by | observable (command) | status |
|---|---|---|---|---|
| 1 | r26 receipt holds 152 records absent from git; capture verified disk not committed bytes; symlinks uncovered | C2 | `python3 -B census/round-29/c2-counter.py --root <lane> --rev <tip>` → `failed=0 uncovered=0 floor_violations=0`; fixture `cases=<N> pass=<N>` | `<closed / carried>` |
| 2 | LOG.md/SCORECARD.md/lesson-28 describe the real defect as two malformed records | C1 K2 | `souji-registry-agreement.py` → `k2=0`; `R29-CORRECTION ` lines at `LOG.md:<line>`, `SCORECARD.md:<line>`, `corpus/lessons/round-28.md:<line>,:<line>` | `<closed / carried>` |
| 3 | landing gate's report check can never evaluate because `.ufo/waves/` is gitignored (permanent rc 2) | `<not claimed this round / item>` | `<gate rc at tip + reason; or the item that points it at census/round-<N>/waves/>` | `<carried / closed / not addressed>` |
| 4 | C2 preregistration `6/6` literal not derived from the tool's output shape (Q58 class) | `<lesson/QUALITY item>` | `<Q60-Q62 rows and evidence>` | `<closed / carried>` |
| 5 | S215 used-by names an entry that never cites S215 | C1 K1 | `k1=0` at tip; `git grep -c S215 <tip> -- corpus/knowledge/<entry>` | `<closed / carried>` |
| 6 | the lane's self-ruled C2 "miss" misread its own frozen exclusion clause | `<lesson item>` | `corpus/lessons/round-29.md` `## Mistakes` row + the reading recorded before after-data | `<closed / carried>` |

Verdict on the six at round end: `<n closed / n carried, with the reason for each carried one>`.

<!-- If a defect stays carried, say so here and in LOG.md Round 29; never let the table imply closure. -->
