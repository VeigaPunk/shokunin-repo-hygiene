# souji — Round 26 report

> Draft assembled by `.ufo/waves/round-26/w1/report-assemble.py` at 2026-10-25T17:40:52Z from the wave results json (absent), `census/round-26/records/`, `corpus/lessons/round-26.md`, `LOG.md` and `SCORECARD.md` at `166baa1`. The L1 reviews and files the real report; `RECEIPT-PENDING` marks data absent at assembly time.

## Work performed

Declared claims (frozen `.ufo/waves/round-26/preregistration.txt`, lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`):

- **C1 — calibration** (surface-class: bookkeeping-file): `bash census/round-26/c1-counter.sh`; before markers=2; headings=17 175 231 @12fd90b; after markers=0; headings=17 44 78 @07f83e6.
- **C2 — coverage** (surface-class: knowledge-entry): `bash census/round-26/c2-counter.sh`; before grounded_f1=0; registry_rows=127 @89e0fce; after grounded_f1=2; registry_rows=132 @e0f8dcd.
- **C3 — operability** (surface-class: instrument-acquisition): `bash census/round-26/c3-counter.sh`; before axis_check_tool=absent @89e0fce; after axis_check_tool=present; claims=3 flags=0; axis_check_exit=0; cases=12 pass=12 control=FALSE-GREEN-REJECTED; fixture_exit=0 @c594901.

- **W1 wave results**: RECEIPT-PENDING — no results json at `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1-results.json` or `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/results.json`; 87 declared seats (registry).
- **LOG.md Round 26 entry**: RECEIPT-PENDING — no Round 26 heading in `LOG.md` at assembly time.
- **Lesson** (`corpus/lessons/round-26.md`): sections § Gate, § Findings, § Residuals, § Receipts, § Mistakes table.
- **Scope**: this assembler only reads the lane and writes one draft; no fleet path, sibling lane, `.scratch/`, `.ufo/state/`, `MANIFEST.json`, git index or jj state was touched. Tool installs/updates: none.

### Findings (verbatim, reflowed, `corpus/lessons/round-26.md` § Findings)

- The r25 "0 prunable, 3 locked" fleet census is history: S132 re-checks to **5 registrations, 0 prunable, 0 locked** even at `--expire=now`. The fleet is *currently* unexposed — but the mechanism (fetch/pull/merge/ rebase auto-maintenance) is live on five surface commands.
- The r24 scaffold's Round 24 measurements block was never landed (the r24 attempt was cut off). The r25 heading order therefore violated the file's own newest-first contract; C1 landed the block and reordered headings to round-25 < round-24 < round-23.
- Replacement "C1 kill-rule vs positional line numbers": the frozen claim's kill rule named base line ranges, but the integration the K2 counter demands moves the protected byte spans. Amendment 2 (accepted pre-data in session) clarified the regions are byte-content spans, and the post-edit byte-diff of each protected span against the committed base is empty. The counter (`census/round-26/c1-counter.sh`) verifies the *order* of the headings; the margin of C1 is the byte-diff, recorded in the report.
- The R3 receipt-label pitfall (from the r25 gate): the receipt's `tool` binds the labelled file's committed bytes *and* the argv label. The c3 counter changed mid-round (its `--stub` arm was replaced by the fixture's integrated case 12), so the regenerated receipts bind the new counter bytes at their own revs; each receipt's label is its own argv element.
- The frozen C3 case set is 12 cases (the r25-C2 replica and an integrated always-green stub control); the first 11-case fixture did not implement the frozen set. Wave ExecAxisFixture delivered the 12-case fixture; the L1 adopted it and fixed the tool's R4 to scan raw claim text (flag only when `enumerate:` is absent AND a universal word is present).
- C2 K2 requires a `## Gate` section per admitted entry (opened date, ADMIT/REJECT with reason, located ≤25-word snapshot quotes). Both entries gained Gate sections; the first quote attempts failed because the man-page HTML wraps the sentence in inline tags and the C comments carry a `* ` decoration — tag-free code/manual token quotes were substituted.
- Wave ExecC1Surgery found C1's first landing omitted the two r24 capability rows; they were appended and the c1-after receipt regenerated at the new tip (markers=0, headings=17 44 78, byte-spans re-verified).

### Residuals (verbatim, reflowed, `corpus/lessons/round-26.md` § Residuals)

- R-r26-1: `git maintenance run` strategy/task scope (which tasks run under which strategy) remains unmeasured; only the trigger and the per-command opt-out are held. The recheck command for S128 is in the entry's `recheck:` line and re-greps the call sites at the next host git tag.
- R-r26-2: the two stage candidate rows remain un-cited (see Gate). If the edition boundary of the zh/ja mirrors becomes provable on a later release, the S-language row can be reconsidered; it must then be cited with the version-stamp evidence rather than as a paraphrase.
- R-r26-3: keep-ref expiry (the `keep` ref option) is still not measured — the trigger set covers expiry via `gc.worktreePruneExpire`, not via the keep-ref guarantee. See `git-auto-maintenance-trigger-set.md` for the claim boundary.

## Landed changes

| lane commit | landed change |
|---|---|
| `12fd90bcd9cdfab495e178023eeaa838a977fcbe` | round-26: preregistration freeze (C1 calibration SCORECARD scaffold census, C2 coverage F1 trigger-set assimilation, C3 operability axis-check instrument) |
| `89e0fceeefcf28db313c94120be6d25e03c60094` | round-26: prereg amendment 1 (C2 K4 literal corrected to base-derived grounded=7/kill_tested=7) + red-before receipts |
| `bd6588c74ebfe86057b80035fdbc33aded8d7666` | round-26: wave evidence (make-spec, w1 spec+dispatch+registry 87 seats, validate) |
| `965b8699d480702828062a5e739fbd2a203b4fb8` | round-26: prereg amendment 2 (C1 kill rule clarified to content-spans, r26 slice verdicts) |
| `a529c762c81272d398727e6a623c801a230ac157` | round-26 C1: integrate r24 scaffold payloads (newest-first order, markers 2->0), R3 dated note, r24 planned bullets |
| `44531281914ddd200432cdc7dae8ad958c5447e3` | round-26 C1: green receipt at landing tip a529c76 (markers=0, newest-first order) |
| `0833de9591a7db81cdfa4efda2cdad2e75606f58` | round-26 C3: tools/souji-axis-check.py + 11-case fixture (real 11/11, stub control FALSE-GREEN-REJECTED), self-hosted flags=0 on r26 prereg |
| `d2e62533bc485bc68fae2c8ef083af0c36a1e1e3` | round-26 C3: counter gains --stub control-arm arm for FALSE-GREEN receipt |
| `e0f8dcd12b1df1c53f213dc3a71def77d8ddf3f3` | round-26 C3 receipts: c3-before/after/control (flags=0 at tip, FALSE-GREEN-REJECTED rc1) |
| `d6c13b0f00066cbb342fdc50167849a5f1c726e5` | round-26 C2 receipts: c2-before (F1=0, rows=127 at base) / c2-after (F1=2, rows=132 at tip), real gate rc=0 |
| `ea0bbe66c974062984134bb5b491b21bbb3c17d7` | round-26: lessons file (Gate decision, findings, residuals) + Entry B enriched citations (fixture/evidence lines, PROVINCE/SKILL pointers) |
| `d6fe8a1125a9723e7593df7b8b90ee6c05cdf9ff` | round-26 C1: append-only mapping note at SCORECARD EOF (five superseded-by line targets, per wave scribe draft) |
| `07f83e69979b1032f9de4fe876739a8dccc7242b` | round-26 C1 fix: append the two r24 capability rows (debris census, coverage-map agreement) after record-agreement row — wave ExecC1Surgery found omission; s... |
| `ba8b54b85814dd980aa96050fe111c7cbfd4956a` | round-26 C1: c1-after regenerated at fix tip 07f83e6 (markers=0, headings=17 44 78) |
| `c5949013f89fe0b8289bdb7050ab64a47e08c911` | round-26 C3: R4 per frozen contract (raw-block scan, only when enumerate absent); adopt wave 12-case fixture (cases=12 pass=12 control=FALSE-GREEN-REJECTED);... |
| `0c92c2e6fbe18f2f3009504d87240b6a22ad3d5b` | round-26 C3 receipts: c3-before (absent@base) / c3-after (claims=3 flags=0, fixture cases=12 pass=12 FALSE-GREEN-REJECTED, verify ok); obsolete c3-control.ts... |
| `33e6807ea54ad5fa295d9138067a9a78f3b0f7ec` | round-26 C2: Gate sections on both entries (opened/ADMIT/REJECT/located snapshot quotes); K2 gate entries=2 ok=2 fail=0 |
| `9a6e0f13b10cff82c1f6a05059779ed6c06f8a28` | round-26 C2 receipts at tip 33e6807: c2-gate (ok=2 fail=0), c2-k4-after (grounded=9 mapped=9, kill_violations=0) |
| `166baa18f808071bc385187691713044a26bd663` | round-26: measurements block + r26 planned bullet (SCORECARD), lessons updates, Q59 criterion, R26-M1 mistakes row, wave w1 seat record |

Lane tip at assembly: `166baa18f808071bc385187691713044a26bd663`.

## Before → after measurements

| claim | axis | before | after | counting command | receipt verify |
|---|---|---|---|---|---|
| C1 | calibration | markers=2; headings=17 175 231 @12fd90b | markers=0; headings=17 44 78 @07f83e6 | `bash census/round-26/c1-counter.sh` | before=RECEIPT-COUNTS-ABSENT; after=RECEIPT-COUNTS-ABSENT |
| C2 | coverage | grounded_f1=0; registry_rows=127 @89e0fce | grounded_f1=2; registry_rows=132 @e0f8dcd | `bash census/round-26/c2-counter.sh` | before=RECEIPT-COUNTS-ABSENT; after=RECEIPT-COUNTS-ABSENT |
| C3 | operability | axis_check_tool=absent @89e0fce | axis_check_tool=present; claims=3 flags=0; axis_check_exit=0; cases=12 pass=12 control=FALSE-GREEN-REJECTED; fixture_exit=0 @c594901 | `bash census/round-26/c3-counter.sh` | before=RECEIPT-COUNTS-ABSENT; after=ok |

### Receipt inventory

| receipt | rev | rc | verify | stdout |
|---|---|---|---|---|
| c1-after.tsv | 07f83e6 | 0 | RECEIPT-COUNTS-ABSENT | markers=0; headings=17 44 78 |
| c1-before.tsv | 12fd90b | 0 | RECEIPT-COUNTS-ABSENT | markers=2; headings=17 175 231 |
| c2-after.tsv | e0f8dcd | 0 | RECEIPT-COUNTS-ABSENT | grounded_f1=2; registry_rows=132 |
| c2-before.tsv | 89e0fce | 0 | RECEIPT-COUNTS-ABSENT | grounded_f1=0; registry_rows=127 |
| c2-gate.tsv | 33e6807 | 0 | ok | entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0 |
| c2-k4-after.tsv | 33e6807 | 0 | ok | grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0 |
| c2-k4-base.tsv | 0eca7c8 | 0 | ok | grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0 |
| c3-after.tsv | c594901 | 0 | ok | axis_check_tool=present; claims=3 flags=0; axis_check_exit=0; cases=12 pass=12 control=FALSE-GREEN-REJECTED; fixture_exit=0 |
| c3-before.tsv | 89e0fce | 0 | RECEIPT-COUNTS-ABSENT | axis_check_tool=absent |

- **Receipt verify refusals**: 5 of 9 receipts do not verify under the frozen `tools/souji-receipt-run.py verify`: c1-after.tsv=RECEIPT-COUNTS-ABSENT; c1-before.tsv=RECEIPT-COUNTS-ABSENT; c2-after.tsv=RECEIPT-COUNTS-ABSENT; c2-before.tsv=RECEIPT-COUNTS-ABSENT; c3-before.tsv=RECEIPT-COUNTS-ABSENT. Resolve or disclose before filing; the prereg RECEIPTS lines claim `verify=ok` for each.

- **After-receipt rev lag**: C1 after `07f83e6`, C2 after `e0f8dcd`, C3 after `c594901` do not match the lane tip `166baa1`; the frozen after values are read at the landing tip, so re-run or confirm before filing.

- C1 byte-diff annex (protected spans against base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`): RECEIPT-PENDING — no receipt file records it; the lesson § Receipts calls it a report annex.

## Sources & frontier

Counting command: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`

- **Registry rows**: 127 → 132 (c2-before/c2-after); on disk at assembly: 132.
- **Entry gate (K2)**: entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0 @33e6807; verify=ok.
- **Census validation (K3)**: RECEIPT-PENDING — no receipt records the validator exit code, malformed/duplicate/enum/used-by findings and tier/status histograms at the tip.
- **Coverage agreement (K4)**: base grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0 @0eca7c8; tip grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0 @33e6807.
- **Source snapshots**: 7 files under `census/round-26/sources/`; bound by `SHA256SUMS`.
- **F1 grounded entries at tip**: 2 (`corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`, `corpus/knowledge/git-auto-maintenance-trigger-set.md`).
- **`considerthese/`**: absent at the lane root (measured at assembly).
- **Frontier movement**: RECEIPT-PENDING — L1 verdict; the admission/refusal decision is recorded in the lesson § Gate below.

### Gate (verbatim, reflowed, `corpus/lessons/round-26.md` § Gate)

The r25 registry's staged S-language-edition row (zh/ja docs, a vendor page) was checked against the build's edition boundaries. What passed: the en `git-fetch(1)` manual (opened from `git-scm.com/docs/git-fetch`), the v2.56.0 tag sources (fetched snapshots in `census/round-26/sources/`, bound by `SHA256SUMS`), and the en `git(1)` pages already in the corpus. What was refused: the zh/ja docs (their version alignment with 2.56.0 on the mirrors was not provable and the pages' own build stamps were ambiguous) and the vendor page (it quoted an older 2.16.x-era workflow; parsing it to an argument would have silently changed the claim's public surface).

Admitted rows instead re-ground the *en* single source of truth: S128 (`git-fetch(1)` § OPTIONS switches), S129 (five v2.56.0 call sites of `run_auto_maintenance`), S130 (`builtin/pull.c` spawns `fetch`, so pull inherits fetch's trigger), S131 (the campaign's measured prune fixture, re-grounded byte-for-byte by sha256) and S132 (the fleet worktree census, 0 prunable / 5 registrations). S131/S132 are own-work tier A per the source registry contract: the lane's re-runnable gate output, re-run in r26 by sha256 verification rather than by re-executing the campaign fixture.

## Trend verdicts

- **coverage (8)** — axes-table bytes: identical (`axes-table` bytes at `0eca7c8` vs `166baa1`); SCORECARD last-change cell: r21 admitted; r22 no expansion claimed.
- **calibration (7)** — axes-table bytes: identical (`axes-table` bytes at `0eca7c8` vs `166baa1`); SCORECARD last-change cell: r22 attempt 2; after-state bound r23.
- **operability (8)** — axes-table bytes: identical (`axes-table` bytes at `0eca7c8` vs `166baa1`); SCORECARD last-change cell: r21 admitted; r22 no separate operability claim.
- **No owned-axis numeric change** (prereg AXIS-HARM GUARD; no re-derivable 0–10 mapping): RECEIPT-PENDING — L1 confirms at filing.
- **expansion** — RECEIPT-PENDING (L1 trend judgement).
- **quality** — RECEIPT-PENDING (L1 trend judgement; lesson § Residuals lists R-r26-1..R-r26-3).
- **discernment** — RECEIPT-PENDING (L1 trend judgement).

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — RECEIPT-PENDING r26 pointer (SHONEN.md records historical: SKILL.md Decision tables/Error patterns/Checklists/Gate registry; corpus/SOURCES.md S100-S103; corpus/lessons/round-21.md Gate)
- [~] At least one end-to-end domain task executed and logged in LOG.md — RECEIPT-PENDING r26 pointer (SHONEN.md records historical: LOG.md:362 (2026-10-19 operator sweep: 96 pushed-receipt artifacts quarantined, second-checked, removed))
- [~] Instructions executable by an agent without oral context — RECEIPT-PENDING r26 pointer (SHONEN.md records historical: census/round-21/run-acceptance.py; census/round-21/accepted-matrix.json (3/3 sources, each18/18); census/round-21/remote-source-after.json)
- [~] No cross-domain bleed (PROVINCE.md still accurate) — RECEIPT-PENDING r26 pointer (SHONEN.md records historical: PROVINCE.md Round21 privacy boundary; .ufo/waves/round-21/w1/ConnSiblingOverlap.md; corpus/lessons/round-21.md Boundaries)
