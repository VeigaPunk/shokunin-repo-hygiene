# souji-shokunin — round 23 report (hyaku, attempt 1)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (repo and workspace hygiene, 掃除).
Round base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`; lane tip at landing `94fe8094f52098b8d2a27dcdaeba953f6ec1a487`.
Preregistration `.ufo/waves/round-23/preregistration.txt`. Inbound work: the non-author spot-check
of round 22, `corpus/lessons/round-22-verifier-spotcheck.md` §5–§7, which routed defects D1–D8 to
this lane.

**HARD BOUND carried by every wave context:** souji's write scope is its own repo only. Nothing
outside `/home/vgpnk/Projects/shokunin/souji-shokunin/` was deleted, moved, quarantined or
classified for cleanup this round — including the incident's fleet `.scratch/` tree, which is
orchestrator-owned and was never read.

## Work performed

Three claims on three distinct axes, each with its own falsifiable before→after.

- **C1 — calibration (7, the lane's lowest non-retired axis): record agreement.** A new instrument,
  `tools/souji-record-agreement.py`, re-derives four declared-vs-observed keys over committed bytes
  (K1 receipt-bound after-state, K2 append-only superseded numbers, K3 register-slice tally,
  K4 uncommitted round work). Evidence: `.ufo/waves/round-23/preregistration.txt` §C1;
  `census/round-23/records/agreement-control-base.txt`; `tests/fixtures/r23-record-agreement.py`.
- **C2 — operability (8): blob-bound receipts.** `tools/souji-receipt-run.py` re-derives a counter at
  a full durable revision in a private `--no-local` clone and emits a receipt binding rev, tool path,
  tool sha256 of the bytes the command ran against, argv, rc and redacted output; `verify` refuses a
  digest that is not the committed blob at that revision. Evidence: `census/round-23/records/*.tsv`,
  `census/round-23/records/refusal-stale-digest.txt`, `tests/fixtures/r23-receipt-run.py`.
- **C3 — coverage (8): F2 read side (assimilation, one theme).** Two entries adopted from
  `corpus-expansion-1` and re-grounded this round — `corpus/knowledge/repo-size-census-readonly.md`
  (S115–S117) and `corpus/knowledge/count-objects-garbage-readings-r25.md` (S118–S119) — with five
  new registry rows and committed snapshots. Evidence: `corpus/SOURCES.md:135-139`,
  `census/round-23/sources/*`, `census/round-23/records/gate-check-c3.tsv`.

### Wave 1 — build (41 seats, one batched `task` call)

Spec `.ufo/waves/round-23/w1-spec.json`, validated under
`scripts/hyaku/ufo-wave-policy.json` (band 32–64, `spawn: 41`), registry
`.ufo/waves/round-23/w1/swarm-registry.json`. Role mix: 9 scout, 9 scribe, 9 reviewer, 4 critic,
3 executor, 2 revenger, 2 mutation-tester, 1 connector, 1 sentinel, 1 simplifier. The L1 holds the
canonical planner seat (the validator rejects `planner`); the bounded planning data-walk rode
`ScoutRegistryCensus`, `ScoutIdCollision` and `RevRecords`.

One bullet per item, each with its report:

- `ScoutCountObjects` — the `-v/--verbose` field set at git 2.56.0, the `garbage`/`alternate` quotes, and the finding that the page documents **no** write side effect (documentation-absence, not a proof) — `.ufo/waves/round-23/w1/ScoutCountObjects.md`.
- `ScoutFsck` — `--lost-found` is the only writing option and writes blob *contents* under `.git/lost-found/`; installed man page agrees — `…/ScoutFsck.md`.
- `ScoutPrune` — four executed counter-examples that `prune -n` is not the `fsck --unreachable` set — `…/ScoutPrune.md`.
- `ScoutCommunity` — both community pages reachable; the JA page never glosses the field; the ZH gloss mislabels the unit — `…/ScoutCommunity.md`.
- `ScoutLocalHost` — installed git 2.56.0-1 and the three man pages; one read-only `count-objects -v` on the lane repo only (`garbage: 0`) — `…/ScoutLocalHost.md`.
- `ScoutRegistryCensus` — C3 baseline: 114 rows, max S114, A110/B3/C1, mined91/queued15/rejected8, malformed 0, census exit 0 with 30 W04; attack A1 (census exit 0 is vacuous at base) accepted and disclosed — `…/ScoutRegistryCensus.md`.
- `ScoutIdCollision` — the frozen 0–3-space extractor; six collisions, none a same document; the indented-fixture guard proven; the staged rows fail E09 on `recheck` and E11 on order — `…/ScoutIdCollision.md`.
- `ScoutInherited` — all seven inherited round-22 leftovers are genuine in-round content; both evidence digests re-derived; recommend commit — `…/ScoutInherited.md`.
- `ScoutMisroot` — fleet sweep at HEAD `23629d98`: 5 untracked, 0 misroots, `.scratch/` untouched — `…/ScoutMisroot.md`.
- `RevRecords` — every r22 C1 4-tuple and C2 tally with its receipt binding, at base bytes — `…/RevRecords.md`.
- `RevGateHistory` — the gate-check digest chain; D3's "measured with f26aa728 while citing 5b8025a8" is a blob-sha1/sha256 false dichotomy — `…/RevGateHistory.md`.
- `ScribeEntryRepoSize` — C3 entry 1, gate-simulated green — `…/ScribeEntryRepoSize.md`.
- `ScribeEntryGarbage` — C3 entry 2, both pages opened, no fleet figure claimed — `…/ScribeEntryGarbage.md`.
- `ScribeSourcesRows` — five rows in the 11-column shape, census-validated in a mirror — `…/ScribeSourcesRows.md`.
- `ScribeScorecard` — the r23 axis rows, capability row and planned line — `…/ScribeScorecard.md`.
- `ScribeLog` — the append-only correction block and the Round23 entry — `…/ScribeLog.md`.
- `ScribeReadme` — the D4 in-place repair and the r23 README section — `…/ScribeReadme.md`.
- `ScribeQuality` — the first draft of the two criteria (re-scoped later to Q54/Q55) — `…/ScribeQuality.md`.
- `ScribeLesson` — the lesson draft — `…/ScribeLesson.md`.
- `ScribeReport` — this report's skeleton and placeholder index — `…/ScribeReport.md`.
- `ExecFixtureAgreement` — the C1 fixture; 9/9, `control=FALSE-GREEN-REJECTED`, an always-zero emitter scores 2/9 — `…/ExecFixtureAgreement.md`.
- `ExecFixtureReceiptRun` — the C2 fixture; 8/8, and 12/12 mutants of a compliant reference runner are caught — `…/ExecFixtureReceiptRun.md`.
- `ExecGateReproduce` — the r22 gate mirrors; `fail=10` reproduces only with blob `4309d769`, and no commit holds the tool without the entries — `…/ExecGateReproduce.md`.
- `RevD1`…`RevD8` — one reviewer per routed defect, each reproducing it at base and judging the planned repair — `…/RevD1.md` … `…/RevD8.md`.
- `RevSHONEN` — all four boxes' pointers resolve; no `[x]` claimed — `…/RevSHONEN.md`.
- `CritC1Gameable` — falsified the first C1 predicate; the four one-line repairs it named are landed — `…/CritC1Gameable.md`.
- `CritC2Value` — found the `refs/replace` hole (digest from the source repo, command in the clone) — `…/CritC2Value.md`.
- `CritC3Ground` — C3's ground was partly held; the claim is restated as F2 entries 1→3 — `…/CritC3Ground.md`.
- `CritPrereg` — separability, counter-moved-after-scoring, and the vacuous C3 arms — `…/CritPrereg.md`.
- `ConnSiblingSources` — no other lane holds any of the five URLs; nearest holder is kama, adjacent not duplicate — `…/ConnSiblingSources.md`.
- `SentinelScope` — argv escape, missing redaction, `GIT_OPTIONAL_LOCKS`, and the `grep`-counts-files attack; the runner guards landed — `…/SentinelScope.md`.
- `MutCounter` — 54 clause mutants, 28 uncovered, named against the final bytes — `…/MutCounter.md`.
- `MutReceipt` — 26 mutants, 17 uncovered; the "digest from tree at rev" clause is not case-3-killable and the report says why — `…/MutReceipt.md`.
- `SimplTouched` — the merge/deletion pass; it proved that an `uncommitted:` row in `corpus/pointer-exemptions.tsv` breaks the landing gate (whole-lane exit 2) — `…/SimplTouched.md`.

### Wave 2 — falsify (33 seats, one batched `task` call)

Spec `.ufo/waves/round-23/w2-spec.json` (`spawn: 33`, band 32–64). Role mix: 15 reviewer, 6 critic,
3 mutation-tester, 3 scout, 2 revenger, 1 sentinel — 100% attack roles. Every item names what it
attacks and targets the landed bytes. Results are carried in `## Wave 2 findings` below.

Round total: **74 seats** (41 + 33), both waves validated under policy v1 and dispatched as one
`task` call each. No seat was replaced; dead seats are listed in `## Round shape`.

## Landed changes

| change | LOG entry | commit |
|---|---|---|
| `tools/souji-record-agreement.py` (C1 instrument, 4 keys) | `Round23` | `476525026cdb179f2d49441e1cb6c6f7316f3124` |
| `tools/souji-receipt-run.py` (C2 runner + verifier) | `Round23` | `4765250…`; decode hardening `102690017115cb202f292828c90b72705f69bf09` |
| `tests/fixtures/r23-record-agreement.py`, `r23-receipt-run.py`, `r23-locator-heading.py` | `Round23` | `4765250…` |
| `corpus/knowledge/repo-size-census-readonly.md`, `count-objects-garbage-readings-r25.md` | `Round23` | `4765250…` |
| `corpus/SOURCES.md` S115–S119 (114 → 119 rows) | `Round23` | `4765250…` |
| `corpus/README.md` (D4 in-place repair + r23 section + F2 row) | `Round22 attempt2 corrections`, `Round23` | `4765250…` |
| `corpus/QUALITY.md` Q54, Q55 (D7) | `Round23` | `4765250…` |
| `corpus/lessons/round-22.md` (D6 append-only correction) | `Round22 attempt2 corrections` | `4765250…` |
| `corpus/lessons/round-23.md` | `Round23` | `4765250…` |
| `LOG.md` correction block + `Round23` entry (D5) | itself | `4765250…` |
| `SCORECARD.md` r23 measurements, two capability rows, planned | `Round23` | `4765250…`, `c0eeaa7a01d309710ab53c41afc6b0df734217a3` |
| `census/round-23/records/*` (5 bound receipts, 2 control records, refusal demo, exemptions) | `Round23` | `c0eeaa7…` |
| the seven inherited round-22 leftovers (D1) | `Round23` | `4765250…` |
| `.ufo/waves/round-23/**` (preregistration, two specs, 74 seat reports) | `Round23` | `4765250…`, `1026900…`, `eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a` |

## Before → after measurements

| claim | counting command | before | after | measured commit |
|---|---|---|---|---|
| C1 record agreement | `cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B tools/souji-record-agreement.py --rev <full40>` | `keys=4 records=3 occurrences=13 mismatches=6` at `1208bfb…` with `--no-worktree` (`mismatches=29` with the live-worktree K4 arm) | `mismatches=0` | tool `617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9`; before `census/round-23/records/agreement-control-base.txt`; after `census/round-23/records/agreement-after.tsv` (`rev=476525026cdb179f2d49441e1cb6c6f7316f3124`) and the tip run ``rev=eb1aa49783ae4a0d42e062aa5a61e49a91b0f76a` rc=0, tool sha256 `dd53c228…`; tip re-run `keys=4 records=4 occurrences=17 mismatches=0`` |
| C2 blob-bound receipts | `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l`, then `python3 tools/souji-receipt-run.py verify --root . <receipt>` | `0` | `5`, every one `verify=ok` | `census/round-23/records/{declared-evidence-after,gate-check-at-first-landing,gate-check-at-lane-base,gate-check-c3,agreement-after}.tsv` |
| C2 refusal | `python3 tools/souji-receipt-run.py verify --root . <receipt with the r22 stale digest 5b8025a8…>` | n/a (no verifier existed) | `RECEIPT-TOOL-DIGEST-MISMATCH receipt 5b8025a83f16 != tree d5ed0805b10f at 1208bfb…`, exit 2 | `census/round-23/records/refusal-stale-digest.txt` |
| C3 F2 read side | `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`; `python3 tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/count-objects-garbage-readings-r25.md --snapshot-dir census/round-23/sources --slice census/round-23/records/empty-slice --slice-verdicts census/round-23/records/empty-verdicts` | registry 114 rows, 30 W04, F2 held one entry; the two entries absent | registry 119 rows, `validate` exit 0, 0 E-findings; gate `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`; F2 entries 1 → 3 | `census/round-23/records/gate-check-c3.tsv` (`rev=476525026c…`, tool `d5ed0805…`) |

Controls. C1's control is the same instrument at the base revision, so a do-nothing tree scores 6,
not 0. C2's control is the base revision, which holds zero bound receipts. C3's control is the
staged rows appended as-is, which the census refuses with `E03 duplicate id` (the collision step's
own receipt). The three claims were also checked for separability: C1's predicate reads only its own
receipts and the records, and the coupling clause that once made it depend on C2's runner was
removed pre-data.

Named limits, not repaired: K4 is a live-worktree observation, so it is not revision-reproducible;
a receipt binds bytes, not execution (a typed receipt passes `verify`, which is why Q55 exists);
C3's gate slice arm is inert this round because no register rows were quarantined; the census
`validate` exit 0 is vacuous at base (ScoutRegistryCensus A1) and only the row/malformed/duplicate
counters discriminate.

## Sources & frontier

`SOURCES.md` rows **114 → 119** (`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`),
tier histogram A110/B3/C1 → A113/B5/C1, status mined91/queued15/rejected8 → mined96/queued15/rejected8,
malformed 0, duplicate ids 0, `sources-census.sh validate` exit 0 (30 pre-existing `W04`
duplicate-URL warnings, no `E` finding) at the tip. The census exit code was also 0 at round start.

Rows added by tier: **5** — tier A `docs` S115 (git-count-objects), S116 (git-fsck), S117
(git-prune); tier B `community` S118 (Qiita, JA), S119 (CSDN, ZH).

Rows touched old→new: **none**. No existing row's status, recheck or used-by cell changed; S115–S119
are new ids continuing the registry, and the staged package's ids were re-pointed **by document**
(the staged S112–S114 resolve to different documents in this lane).

Frontier rows advanced: **F2 (repository size census)** — from "frontier, entries held (one entry)"
to "frontier, three entries on the read side". F2 does **not** move to core: no SKILL rule and no
tool land, and `PROVINCE.md`'s core test is an admitted entry *plus* a SKILL rule. F1, F3, F4 and F5
are unchanged; the F5 reap protocol and NAMESPACE pin remain operator-held.

Assimilation: one theme (F2 read side), two admitted entries, five Gate decisions — two ADMIT and
three REJECT with flips, all in `corpus/lessons/round-23.md` `### Assimilation decisions`. The
staged own-work fleet-census row is refused because its evidence lives outside this repository. The
package's `S134/S138/S139` re-pointing note in the preregistration is corrected in the lesson: the
actual adopted ids are S115–S119 and the own-work row is refused. `considerthese/` does not exist in
this lane.

Id collision: registry 114 ids (S001–S114) vs staged 134 (S109–S242) → 6 collisions, none a same
document; the frozen 0–3-space extractor was proven against an indented `  | S115 |` fixture
(column-zero-only misses it). No renumber arithmetic was used: every adopted id was minted by
document.

## Trend verdicts

- **expansion — `improved` (bounded).** Two admitted entries and five tier-A/B rows on F2's read
  side, with committed snapshots; the bound is that F2 stays frontier (no SKILL rule, no tool), and
  a non-author closure may reasonably re-grade this as `unprovable-but-better` because the lane
  already held one F2 entry.
- **quality — `improved` (bounded).** Five receipts verify against their own revisions; both
  instruments reject a false green (9/9 and 8/8, plus 12/12 mutants of a reference runner); the
  routed record defects are closed by counters rather than prose. Bounds: K4 is not
  revision-reproducible, a receipt binds bytes not execution, and the counters were repaired after
  wave-1 scoring (disclosed in the lesson as a §9 deviation).
- **discernment — `improved` (bounded).** D6 became a corrected reject reason and D7 a new
  criterion; three wave-1 attacks that falsified parts of the plan were accepted in the round's own
  text (C2's `refs/replace` hole, C1's tuple-binding hole, C3's ground already held). Bounds: the
  spot-check's D3 premise is partly false (blob sha1 vs sha256 of the same bytes) and D7's M22 half
  is overstated; both are reported, not repaired.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — unchanged this round; `RevSHONEN` re-resolved all four pointers at base and found the SKILL's 0 URLs residual.
- [~] At least one end-to-end domain task executed and logged in LOG.md — `LOG.md:362` (2026-10-19 operator sweep) unchanged; `RevSHONEN` re-derived the 96-row receipt.
- [~] Instructions executable by an agent without oral context — `census/round-21/run-acceptance.py` + `accepted-matrix.json`; `RevSHONEN` re-ran the replay 18/18 at base.
- [~] No cross-domain bleed (PROVINCE.md still accurate) — `PROVINCE.md` unchanged; `W2Bounds` checked the certification/K5/F5 statements.

No box is `[x]`: promotion is operator-owned and this round has no non-author verifier on record.

## Routed defects D1–D8

| id | disposition |
|---|---|
| D1 | **closed** — the seven inherited round-22 files are committed at `4765250…`; both evidence digests re-derived (`ScoutInherited`), and K4 keeps it closed. |
| D2 | **closed** — `census/round-23/records/declared-evidence-after.tsv` binds `assertions=63 resolved=63 skipped=40 mismatches=0` at `9301d98c1c689c79741f0f1ba1f171138d20af07`, the revision SCORECARD names; SCORECARD's counting command now names that revision and the receipt. |
| D3 | **closed with disclosure** — the digest chain is recorded at three revisions (`d85c2696…`@`a211e4d`, `5b8025a8…`@`f26aa728`, `d5ed0805…`@`1208bfb`), the stale digest is refused by the verifier, and the `fail=10` before-state is reported **unrecoverable**: no commit holds the tool without the entries, and the tip blob scores `fail=0`. D3's framing is also partly false — `5b8025a8…` is the sha256 of the blob that produced the run (`RevGateHistory`, `RevD3`). |
| D4 | **closed** — README corrected in place; K3 fails on any disagreeing tally or a missing class. |
| D5 | **closed** — `LOG.md` `Round22 attempt2 corrections` names both superseded cells under `superseded by`; K2 fails when a stale scalar has no correction and when a filed occurrence is deleted. |
| D6 | **closed** — append-only correction at the end of `corpus/lessons/round-22.md` with the entry-level reason, the candidate's named delta and a flip it does not already satisfy. |
| D7 | **closed** — Q54 (locator-heading) with fixture `tests/fixtures/r23-locator-heading.py` (`selftest=2/2`, mutant 6 bad); the spot-check's M22 half is reported as overstated (that row names Q1/Q2). |
| D8 | **disclosed, not repaired** — the stray backtick in `census/round-22/attempt2/quarantine-slice` is inherited from the campaign register's id cell, digest-bound twice in r22 evidence and byte-identical to two committed copies; the count is unaffected (`slice_verdicts=8 slice_total=8`). Named in `LOG.md`. |

## Round shape

- Two v1 waves under `scripts/hyaku/ufo-wave-policy.json`: wave 1 build (41), wave 2 falsify (33);
  **74 seats**, both dispatched as exactly one `task` call each from their validated spec.
- Wave 1 role mix: 9 scout, 9 scribe, 9 reviewer, 4 critic, 3 executor, 2 revenger,
  2 mutation-tester, 1 connector, 1 sentinel, 1 simplifier. Wave 2: 15 reviewer, 6 critic,
  3 mutation-tester, 3 scout, 2 revenger, 1 sentinel.
- Planner seat: L1 (the validator rejects `planner`); planning data-walk rode three wave-1 items.
- Dead seats: `none (all 41 wave-1 seats completed; 33 wave-2 seats completed)`.
- Every seat ran read-only against the lane except its own report; the two executors delivered
  fixture files under the wave dir, which the L1 copied into `tests/fixtures/` after review.

## Wave 2 findings

Wave 2 (33 falsify seats) confirmed the claims' directions and forced the fixes listed in
`corpus/lessons/round-23.md` "## Wave 2 summary" — K1's three predicate holes (unbound-tuple,
receipt-rev-object, last-wins counts), Q54's heading resolution with the real r22 mutant, the
runner's sparse-checkout exclusion of `census/operator-sweep-*`, verifier `GIT_NO_REPLACE_OBJECTS`,
entry-1 corrections, snapshot digest binding, control numbers standardized to 6/29/0, and the
fixture counts 12/12, 8/8 and 2/2. Pending wave-2 details: `verify` accepts a non-durable rev
(`run` refuses it) and the `tool=` label is not bound to argv — both disclosed as named limits; the
production gate still checks quote presence only, while Q54's fixture is the heading check.

## Stale-lane

Respawn-per-round driver; this lane has no other mission open. Round 24 is the next dispatch; it
should re-run these counters at the new tip and carry the F2 actable remainder.

## Tool installs

None. No `pacman`, `uv`, `npx`, `cargo` or `npm` transaction was run this round; `git 2.56.0-1`,
`man-db 2.13.1-2` and the three git man pages were already installed.

## Misroot

`git -C /home/vgpnk/Projects/shokunin status --porcelain` at the round's start (fleet HEAD
`23629d98`): 17 tracked-modified + 5 untracked, **none** written by this lane (`ScoutMisroot`).
`W2Misroot` re-ran the sweep at the tip. Fleet `.scratch/`, `.ufo/state/` and sibling lanes were
never written; `.scratch/` contents were never read.
