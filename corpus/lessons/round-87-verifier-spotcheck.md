# Round 87 verifier spot-check — non-author closure

author: hyaku closure (non-author integrator, @m_zfl)
closure date: 2026-11-08; lane souji round 87; base `5e288bb3152328f371325d0bf4fee7309d629991`; tip `64079f21dc27b8964679ed6a580fb4079a65c874`

## Step-1 conformance

| check | result |
|---|---|
| report committed in the fleet repo by the lane identity | pass — `git log --format='%an %H' -- .ufo/reports/round-87/souji.md` → `souji-shokunin 21c703de04ec10f7a3a2e01d408e6a108d3c9953` (final) and `souji-shokunin b516a66398238edea1362b0ce96642d885ba4896` (draft) |
| `SHONEN` heading, one line per box | pass — `grep -n '^## SHONEN'` → line 161; four `[~]` lines with evidence pointers; no `[x]` |
| every cited lane commit exists and is an ancestor of the branch | pass — `77ccef7c 6ed2d368 6e502c5c 578cbf2c 89d36922 b0a64c94 1556010b f36fcf55 749c7829 c23a4b52` all exist and `git merge-base --is-ancestor <h> 64079f21`; base `5e288bb3` is the parent of `77ccef7c` and an ancestor of the tip |
| lane clean + pushed | pass — `scripts/hyaku/jj-lane.sh state` → `branch=master local=64079f21 remote=64079f21 ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` empty; `git ls-remote origin refs/heads/master` = `64079f21` |
| prompt carries the template contract | pass — `.ufo/prompts/souji-round-87.md` (committed by `souji-shokunin 8f4e5e25`, 06:26:51) carries §1 MISSION/AXES, §2 1–3 claims, §2b frontier, §3 L2 floor, §4 report contract (incl. `SHONEN` and commit-hash items), §5 commit-then-push + push scope + L0, and the five child-lane items (report path line 101, commit-then-push 133, `SHONEN` 118/521, commit-hash 107, write scope 448); §6 embeds the run-15/13/11 operator directives as history and §3 defers to the host route table; no model alias is passed by the r87 wave (`w1-spec.json`/`w1-dispatch.json` carry no `model` key) |
| marker vs report | not a marker — work performed, evidence pointers, LOG-tied landed changes, and resolvable commit hashes |
| dispatch/complete digest (copied; `.ufo/watchdog.log` lines 3322/3332) | `2026-11-08T06:26:53-03:00 launch souji round=87 pgid=2703437 driver=hyaku-inline attempt=1`; `2026-11-08T07:25:14-03:00 complete souji round=87; hyaku-inline attempt=1` |

## Per-claim re-check

### C1 — calibration 7 (two clauses get one row and one mutant each; a third candidate is measured already bound)

Frozen command, one per end: `python3 -B census/round-87/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work WORK --only r86,r87 --expect-killed 18` (after); `--only r86 --expect-killed 8` (before). Re-measured by me on the committed bytes in `/fast/scratch/r87verif.*` and `/fast/scratch/r87bef.*`:

| end | receipt | observed by me | exit | verdict |
|---|---|---|---|---|
| before (do-nothing: ten mutants on the r86 49 rows) | `census/round-87/controls/c1-before.txt` | `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`; `MUTANT m12-token-on-line pop=r86 killed=no mismatches=0 errors=0 exit=0`; `MUTANT m16-nf6b-punct pop=r86 killed=no mismatches=0 errors=0 exit=0`; `SUMMARY mutants=10 sets=r86 pristine_r86=ok killed_r86=8 killed_total=8`; `EXIT=0` | 0 | AGREE |
| after (51 rows) | `census/round-87/records/c1-after.txt` | `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`; `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`; `MUTANT m12-token-on-line pop=r86 killed=no … pop=r87 killed=yes mismatches=1`; `MUTANT m16-nf6b-punct pop=r86 killed=no … pop=r87 killed=yes mismatches=1`; `SUMMARY mutants=10 sets=r86,r87 pristine_r86=ok pristine_r87=ok killed_r86=8 killed_r87=10 killed_total=18`; `EXIT=0` | 0 | AGREE |

Pinned bytes cross-read: counter `fd0a8e24…`, harness `d6f4e612…`, mutants `9368b342…` (10 members), population `b066fa0f…` (51 rows), items `ce80195d…` (5 items, base `705fa138`), r86 population `79db70f6…` (49 rows). The r86 file is byte-identical at r87 offset 2 (`diff <(cat census/round-86/c1-false-rows.tsv) <(sed -n '2,51p' census/round-87/c1-false-rows.tsv)` empty), with `TQ1` and `NE1` appended. All six instruments/populations hash identically at P `77ccef7c` and at the tip. The one-row killer attribution ("NE1 only" for m12, "TQ1 only" for m16) is evidence-verified from `S87MutCounter` §3 (`51/1` rows and the `NE1 only` / `TQ1 only` cells) because the battery summary reports per-mutant counts; the third candidate is bound by NF12c in `records/c1-c8-measured.txt` (`SUMMARY rows=49 mismatches=1`, the mismatching row named), whose mutant bytes hash to `55a5f46f…`.

### C2 — operability 8 (K4 reads NUL status records, names its writer delegation, keeps the exception line)

Frozen command: `python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work WORK` (after); `--tool census/round-87/controls/c2-before-base-tool.py` (before). Re-measured by me:

| end | receipt | observed by me | exit | verdict |
|---|---|---|---|---|
| before (lane-base tool `cf875367…`, writer `70bbf1c2…`) | `census/round-87/controls/c2-before.txt` | `SUMMARY rows=12 mismatches=3 errors=0`; `ROW KN1 … named=no match=no`; `ROW KN2 … named=no match=no`; `ROW KN3 … named=no match=no k4rows=['"bad\\nname2.txt"|uncommitted-path']`; `EXIT=1` | 1 | AGREE |
| after (filed tool `e1b00e8a…`) | `census/round-87/records/c2-after.txt` | `SUMMARY rows=12 mismatches=0 errors=0`; KN1/KN2/KN3 `named=yes`; `ROW KN2 … writer_sha=70bbf1c2a92e appended_sha=1b8ecf328ed3`; KN3 record `bad\nname2.txt` / `uncommitted-path`; the nine r85/r86 rows `match=yes`; `EXIT=0` | 0 | AGREE |

The filed tool hashes to `e1b00e8ae14f7059cb5d649dd9ae6e3a3a0498813beb22427af2473c8ac67ccc`, which is the digest in the receipt header. Code spot-read confirms the four claimed mechanisms: `git_bytes(root, "status", "--porcelain", "-z")`; `_escape_record()` doubles `\` first, maps LF/TAB/CR and every other non-printable byte to `\xNN`; the rename/copy second field is skipped when `rec[:2]` contains `R` or `C`; `writer_binding()` prints `# writer path=… sha256=…` and stores the digest for the `RECEIPT-WRITER-SWAPPED` check; `_stderr_tail()` takes the last non-empty line and keeps both ends when over the bound; `CLEAN` counts only with exit 0. The byte arm re-measured: final tool `SUMMARY rows=10 mismatches=0` EXIT 0, lane-base control `SUMMARY rows=10 mismatches=8` EXIT 1. The real-lane receipt reports no K4 row and the inherited K3 tally row only. The regression-fixtures record is measured at `821e3703…`, not the filed `e1b00e8a…` (routed D3).

## Pre-file falsification ledger (Amendment 59)

`python3 scripts/hyaku/prefile-falsification.py --lane souji --round 87` → `PREFILE-FALSIFICATION: pass claims=2 rows=10 attack_seats=5 findings=0`, exit 0. The ledger `<lane>/.ufo/waves/round-87/claim-falsification.tsv` has 10 rows (C1 ×5, C2 ×5), covers both claims, and reads all five attack seats: `S87Reviewer`, `S87Critic`, `S87MutCounter`, `S87Sentinel`, `S87Connector`. Four rows are `falsifies-wording`, each naming its narrowing: C1 critic → `plans/round-87.md` A7; C1 mutation-tester → A4; C2 critic → A7; C2 sentinel → A9. I read A4/A7/A9: they reconcile the rows (one spelling per new row plus the p2/p3/p7/p8 carried limits; the harness BASE `e65538e7` naming; the R0 `isdigit()`/range limits; stderr preference and both-ends compaction; the rename status-letter skip; the injective byte escape). No row is unreconciled; the ledger's pass is not an artefact of an absent input.

## Discernment spot-check (LEARNING.md)

Lesson `corpus/lessons/round-87.md` `## Gate` sampled: two admits and one reject; each source re-opened live.

| item | lane decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S346 git-status(1) `-z` no-quoting rule | ADMIT `mined`, tier A | live `/usr/share/man/man1/git-status.1.gz`, decompressed sha256 `52d34e3a41e59a1683ac36ab7013a63e8701bfd687ab98c7630419676a2b2d95` = the filed capture; quoted sentence at roff 698, SOURCES row quote at roff 1102 | AGREE | both quotes are byte-exact (698: 14 words; 1102: 20 words ≤25) and the no-quoting rule is exactly what KN3's decision needs; official installed page, tier A. Precision nit: 698 is the Porcelain v1 alternate-`-z` paragraph, not the OPTIONS `-z` entry (211–217) — routed D6 |
| S347 git-grep(1) `-F` | ADMIT `mined`, tier A | live `/usr/share/man/man1/git-grep.1.gz`, decompressed sha256 `52603128b427d0cd8d2bfdc10790958a9d34b8762abc3a3d870504ac3b5b14a6` = the filed capture; quote at roff 212 | AGREE | byte-exact (10 words ≤25); fixed-string semantics is load-bearing for a path pattern containing `.` and `/`; official page, tier A |
| git-config(1) `core.quotePath` duplicate scope | REJECTED with flip | live `/usr/share/man/man1/git-config.1.gz` line 3564: double-quotes, C escapes for TAB/LF/backslash, then default/range | AGREE | the page states the line-form rule the lane does not parse (`-z` is not affected); duplicate scope for this surface and the flip names exactly when it becomes needed. Record defect: no `rejected` SOURCES row was written (delta is the two admits only) — routed D4 |

## Census

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok`, EXIT 0, 87 pre-existing `W04` cross-scope duplicate-URL warnings before and after, no `E0x`. Registry `268 → 270` (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` at `5e288bb3` = 268, at tip = 270; two admitted rows, none removed). `census/round-87/records/source-capture-check.txt` claims the captures are byte-identical to the installed pages; my `gzip -dc … | sha256sum` reproduces both digests.

## Per-axis verdicts

| axis | verdict | evidence |
|---|---|---|
| calibration | improved | C1: do-nothing control kills 8 of 10 mutants on the 49-row population and leaves m12/m16 alive; the 51-row population kills 10 of 10 with both pristine arms green (re-measured). The population is unpadded (the third candidate is measured already bound, Q162). The score stays 7 with the verdict, counting command and measured commit in the SCORECARD row. |
| operability | improved | C2: the 12-row counter goes `mismatches=3 → 0`; the byte arm goes `8 → 0` on the final bytes; the nine r85/r86 rows stay green; the real-lane run reports no K4 row. Three invisible fail-opens become measured rows. |
| coverage | unchanged | `PROVINCE.md` adds a boundary note only; Core/Frontier/Retired unchanged; two SOURCES rows are on already-held git-native ground; no frontier row advanced. |

No owned axis harmed: `git diff 5e288bb3 64079f21 -- SCORECARD.md` appends the r87 rows and changes no score (calibration 7, coverage 8, operability 8; the lane has no reproducible 0–10 mapping); the `PROVINCE.md` diff is the boundary note only. The two capability rows carry what it can now do → evidence pointer → first-working round, demonstrated in-round.

## Trend verdicts

- **expansion — unchanged.** No PROVINCE move, no frontier row to Core, no new receipt class; the two registry rows cover already-held git-native ground (S302/S341 cite the same pages for other scopes). The new knowledge entry is not mapped in `corpus/README.md` (routed D5), so it is not counted as expansion.
- **quality — improved.** The append-only correction to `corpus/knowledge/own-tree-pointer-binding.md` names the r86 fixture-only target paths (M5) instead of leaving a dangling-pointer class standing; `machine-parsed-path-spelling.md` states its boundary; C2 closes three fail-opens with measured rows and a no-regression arm on the final bytes. Caveat: the round's own records carry stale tool digests (routed D1).
- **discernment — improved.** The outside spot-check agrees with both admits and the one reject; the round measured its own plan down before the freeze (A0.1) and disclosed the pre-freeze after-runs rather than filing them as evidence (A0.2). Caveat: the rejected candidate was not written as a registry row (routed D4).

## Routed defects (status-neutral, for r88)

1. **Stale tool digest left standing in four places.** The filed tool and the filed receipt are `e1b00e8a…`, but `.ufo/reports/round-87/souji.md:47` calls `aac9a9ed…` the "final sha256" (that is the `89d36922` bytes), `SCORECARD.md` r87 C2 row names the filed tool `0ad9e3bf…` and the measured commit `6e502c5c` (first repair), `corpus/lessons/round-87.md:73` and `LOG.md:3297` name `0ad9e3bf…`. Append-only corrections naming the superseded text; never rewrite filed bytes (PROTOCOL §Evidence standard, "Corrections sweep every mention").
2. **LOG r87 chronology is inconsistent with `plans/round-87.md` A0.2.** `LOG.md` says "C2 06:44; F landed 06:58"; A0.2/report record C1 06:47:19, C2 the same minute, F committer 06:47:35 (`git log 6ed2d368` → `ci=2026-11-08 06:47:35 -0300`). Append-only correction.
3. **`census/round-87/records/c2-regression-fixtures.txt` is measured on `821e3703…`, not the filed `e1b00e8a…`** (its own header says "FINAL tool bytes (821e3703…)"). Re-run r23/r24/r25 on the filed bytes or mark the record superseded; the 12-row counter's nine-row arm is the claim's no-regression evidence and is already on `e1b00e8a`.
4. **Rejected source has no SOURCES row.** `git-config(1) core.quotePath` is recorded only in the lesson; template 2b step 1 and the SOURCES table semantics require a `rejected` row carrying reason + flip. The registry delta is +2 (admits) only.
5. **New knowledge entry is not indexed.** `corpus/knowledge/machine-parsed-path-spelling.md` has no row/bullet in `corpus/README.md` (the coverage map/index; "an index row is a claim — write the row when the file exists").
6. **Citation-precision nits.** The lesson and knowledge entry label roff 698 "OPTIONS `-z`" (it is the Porcelain v1 alternate-`-z` paragraph; OPTIONS `-z` is 211–217); `tools/souji-record-agreement.py`'s docstring line 23 still says `git status --porcelain` without `-z`; the report's C2 wave-repair paragraph says "seven shapes" while the filed probe has 10 rows (A8's `rows=7` is superseded by A9's `rows=10`).

## Conclusion

Verifier independently re-measured both claims on the committed bytes: C1 reproduces `killed_r86=8 killed_r87=10 killed_total=18` with m12/m16 alive on r86 only; C2 reproduces `rows=12 mismatches=0` on the filed tool `e1b00e8a…` and `mismatches=3` on the lane-base control; the byte arm reproduces `10/0` vs `10/8`. The pre-file ledger passes with no unreconciled wording row; the sources census is clean and the spot-check agrees on all three gate decisions; no owned axis is harmed. The six routed defects are evidence-hygiene and record-keeping, not claim falsifications. **admitted**.
