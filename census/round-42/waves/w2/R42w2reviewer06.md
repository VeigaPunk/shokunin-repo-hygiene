# R42w2reviewer06 — bookkeeping review of souji round 42 (reviewer, falsify)

Seat: R42w2reviewer06 · Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · Base `bf618f6c5c09d302994871c94903abbea2deb60d` · Freeze `afe17f416eec04dcf3f480b580a8f928de61d19d` · Tip attacked `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.
Scope: the bookkeeping diff base→tip over SCORECARD.md, LOG.md, corpus/QUALITY.md, SKILL.md, corpus/README.md, corpus/SOURCES.md, corpus/pointer-exemptions.tsv, corpus/knowledge. Read-only; no lane write; no git mutation.
Receipts (copied verbatim from this seat's runs, inside this seat directory): `.ufo/waves/round-42/w2/R42w2reviewer06/receipts/`.

## Verdict

**Append-only and resolution claims HOLD; the number-to-receipt claims HOLD for every cell I could match byte for byte. Six evidence or wording defects (D1–D6) are reported, none of which moves a frozen counter's verdict.** Two of them (D4, D5) are misses against the round's own new rules (QUALITY Q104 and the start/end census rule).

- Pure-append: SCORECARD, LOG, QUALITY, SKILL, SOURCES are insert-only (`git diff` hunks `-N,0`, numstat deletions 0). The only in-place edits are two single lines: `corpus/README.md:217` (F2 row pointers) and `corpus/knowledge/jj-colocation-receipts.md:148` (lane-reports sentence). Numstat total 66 insertions, 2 deletions, and the 2 deletions are exactly those lines.
- Resolution: every backticked repo path in the appended text resolves at the tip except one deliberate absence claim (`considerthese/`, verified absent) and two shorthand forms (D9, and a brace form already in base). Every 40-hex commit resolves at the tip (ancestors of the tip). Every sha256 cited in SKILL / SOURCES / README matches the committed bytes.
- Numbers: every counter SUMMARY quoted in SCORECARD/LOG/SKILL/QUALITY re-measured at the tip matches its receipt; SOURCES 182→183 and W04 52→52 re-measured.

## Table — file | change class | resolves? | discrepancies

| file | change class (git hunk) | resolves at tip? | discrepancies |
|---|---|---|---|
| SCORECARD.md | pure append `@@ -839,0 +840,26 @@` (26 ins / 0 del); base line 839 kept | yes: all `census/round-42/...`, `corpus/lessons/round-42.md`, commits afe17f416eec, b7408095543579, 34e33a662cd0, 133206705f32, 5ad7046d44c3, 51f204fb7c63, bf618f6c5c09; C1/C2/C3 'before' and 'after' cells checked against receipts | D1 (plan-vs-actual count), D2 (C2 'before' cell elided with `...`), D3 (R1 after-cell counter value has no committed receipt), D4 (no tip counts line for Q104), D5 ("census exit 0 both ends" — end receipt absent) |
| LOG.md | pure append `@@ -1921,0 +1922,12 @@` (12 ins / 0 del) | yes (same commits; `tools/souji-freeze-check.py`, `tests/fixtures/r42-drift-conditions.py`, `corpus/SOURCES.md`, `census/round-42/records/census-before.txt`, `SCORECARD.md`, `census/round-42/preregistration.txt`, `considerthese/` absence) | D5 (same "both ends" sentence, LOG Frontier bullet); D6 (LOG "wave 1 = 40 seats" vs 39 reports) |
| corpus/QUALITY.md | pure append `@@ -258,0 +259,8 @@` (8 ins / 0 del); Q103–Q105 | yes (`corpus/lessons/round-42.md`, `tools/souji-declared-evidence.py`, `SCORECARD.md`, `census/round-42/waves/w1/R42sentinel02.md`) | D4 (Q104 requires the tip counts line with its revision; no committed copy exists) |
| SKILL.md | pure append `@@ -286,0 +287,6 @@` (6 ins / 0 del); six `r42-*` gate rows, 9 pipes each (matches the 8-column header) | yes; sha256 of c1-items, c1-counter, c2-cases, c2-counter, c3-mutants, c3-counter, pinned drift tool, r1-counter all MATCH the committed bytes | D7 (drift-fixture digest "recorded at landing" not in row), D8 (fixture's exit 2 not named), D9 (bare basename `c3-stub-sniff.py`) |
| corpus/README.md | two hunks: in-place `@@ -217 +217 @@` (one line, F2 row) and pure append `@@ -810,0 +811,11 @@` (Round 42 frontier update) | yes: `census/round-42/jj-w1-reports/{JjAuditSouji,JjTrialSouji}.md` and `SHA256SUMS` exist; copies match SHA256SUMS and match the fleet files (fleet commit f47ad6ba8d30) | D11 (the fleet commit cited in the cell resolves only in the fleet repo, not the lane); otherwise the frontier numbers (182→183, census exit 0 at start) match |
| corpus/SOURCES.md | pure append `@@ -212,0 +213 @@` (1 row, S259) | yes: snapshot sha256 620581fe…5546a matches `census/round-42/sources/SHA256SUMS`; "Python 3.15.2 documentation" present; quoted sentence at snapshot lines 418-419; `corpus/lessons/round-42.md` (used-by) exists; `census validate` rc 0, 0 E-codes | none |
| corpus/knowledge/jj-colocation-receipts.md | in-place `@@ -148 +148 @@` (one line, lane-reports sentence) | yes (`census/round-42/jj-w1-reports/` exists; `census/round-17/jj-receipts-{base5fa6017,4f48343}.txt` both exist) | none |
| corpus/pointer-exemptions.tsv | unchanged (no diff) | n/a | R1's frozen predicate expects `rows_added=3`; the repoint landed with 0 rows, so the frozen R1 counter reads red by its letter (reported in SCORECARD; no discrepancy in the wording) |

## Discrepancies (ranked by consequence)

- **D4 — QUALITY Q104 not met by the round's own ledger.** Q104 requires "the instrument's counts line at the tip with its revision". SCORECARD quotes the instrument only at the base (`assertions=474 resolved=404 skipped=780 mismatches=70`). No committed file contains the tip line. Measured at the tip: `assertions=490 resolved=420 skipped=810 mismatches=70` (`receipts/declared-evidence-tip.txt`). Gate-relevant: the total stayed 70, so the new-mismatch test is the right gate, but the quoted revision line is missing. Attacks: QUALITY Q104, SCORECARD C1 row.
- **D5 — "census exit 0 at both ends" cites only the start.** SCORECARD (frontier sentence) and LOG (Frontier bullet) say "census exit 0 both ends (`census/round-42/records/census-before.txt`)". Only `census-before.txt` is committed; no end receipt exists in `census/round-42/records/`. Measured now, read-only: `sources-census.sh validate` rc=0, `rows=183`, `W04=52`, no E-codes (`receipts/census-end-validate.txt`, `receipts/census-end-census.txt`). The sentence is true but unreceipted; the frozen start/end rule in the preregistration is only half-evidenced. Attacks: preregistration "Frontier step" rule.
- **D6 — wave-1 seat count and report evidence.** LOG: "wave 1 = 40 seats". `census/round-42/waves/w1-spec.json` has 40 items; `census/round-42/waves/w1/` holds 39 `.md` reports. `R42mutationtester03` has a directory (`c3-counter.mut.py`, `harness/`) and no report, and the lesson never mentions its outcome. `.ufo/waves/round-42/w1/` has no results JSON (`ls | grep -i result` empty). The LOG does not claim settlement, so this is an evidence gap rather than a false statement. Attacks: LOG Swarm bullet, lane addendum "WAVE-DONE before report".
- **D1 — plan-vs-actual count and its parenthetical.** SCORECARD: "Plan-vs-actual against the r41 plan sentence: three of nine planned items done as written (lesson, CORRECTION-SC at line 839)." The parenthetical names two entries that are not planned items. The lesson's own accounting (`corpus/lessons/round-42.md`, "Plan-vs-actual" paragraph) lists KEY-DUPLICATE, HEADING-MALFORMED, widened dispatch names, condition-level mutants and M40-12 (as D4) as done in part or whole, and says "Three planned items out of nine were done as written" without naming which. The SCORECARD count is therefore not reproducible from the text. Attacks: SCORECARD r41 plan sentence (line 839), lesson.
- **D2 — C2 'before' cell is not byte-for-byte.** SCORECARD C2 before: `cases=37 pass=24 fail=13 ... selftest=FAIL patches=0/3`. The receipt (`census/round-42/controls/c2-control.txt`) reads `SUMMARY cases=37 pass=24 fail=13 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=red retro_clean=ok selftest=FAIL patches=0/3 tool_sha=8131847bcfc5`. The elided middle is substantive (`real=FAIL`). The cell's tokens are all present; the cell is not a byte match. Attacks: SCORECARD C2 row.
- **D3 — R1 after-cell counter value has no committed receipt.** SCORECARD R1 after: `frozen counter findings=0 deleted=2 rows_added=0 stale=0`. The cited receipt `census/round-42/records/gate-both-modes.txt` contains only the gate's output, not the counter's `SUMMARY`. The value is reproduced at the tip (`receipts/r1-counter-at-tip.txt`, `EXIT=1`), but nothing in the lane records it. Attacks: SCORECARD R1 row.
- **D7 — SKILL r42-drift-conditions row: digest "recorded at landing" is not recorded in the row.** The row says `sha256 (recorded at landing; ...)` but carries no digest. The only committed digest is `census/round-42/waves/manifest.sha256:260` (`03392c7d…`, path `./w1/R42executor10/...`), which equals the landed bytes (`sha256sum tests/fixtures/r42-drift-conditions.py` = `03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45`). Attacks: SKILL row r42-drift-conditions.
- **D8 — SKILL r42-drift-conditions exit map omits the root refusal.** The fixture returns 2 for euid 0 (`tests/fixtures/r42-drift-conditions.py` line ~204) and `sys.exit(main())`. The row says "0 … ; 1 any case FAIL" and "Codes other than 0 and 1 are not named by the counter docstring" — honest, but the exit 2 exists in code and is not in the row. Attacks: SKILL row r42-drift-conditions.
- **D9 — SKILL r42-c3 row cites a bare basename.** The row lists `` `census/round-42/controls/c3-stub-allpass.py`, `c3-stub-sniff.py` ``. The second item resolves only in context (`census/round-42/controls/c3-stub-sniff.py`, present). Minor.
- **D10 (disclosure, not a discrepancy) — post-freeze harness edit.** `census/round-42/score-candidate.sh` changed after the freeze (`afe17f4`→tip: +7 lines, an allowlist and symlink refusal, commit 34e33a6). The preregistration's frozen list (rule 1) names counters, populations, controls, the pinned tool and prior fixtures, not the harness, so the change is not a freeze violation as written. The counter blobs (c1/c2/c3/r1), population blobs and pinned tool are byte-identical from freeze to tip (checked with `git diff --stat afe17f4 3105a63 -- <frozen paths>`; only score-candidate.sh differs). Reported so the L1 can decide.
- **D11 (disclosure) — fleet commit in README/knowledge cell.** `f47ad6ba8d30` resolves in the fleet repo (`git -C /home/vgpnk/Projects/shokunin cat-file -t f47ad6ba8d30` → commit), not in the lane. The cell says "fleet commit"; it is accurate, but it is not verifiable from the lane alone.

## Checks that found no discrepancy

- SCORECARD C1 before cell: `assertions=474 resolved=404 skipped=780 mismatches=70` = `receipts/declared-evidence-base.txt` (`EXIT=1`). C1 after cell = `census/round-42/records/c1-after.txt` byte for byte (`SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`); re-run at tip: same line, EXIT=0.
- C1 control cell: `registered=0 class_ok=0 corrected=0` and `class_ok=42` are substrings of `controls/c1-control.txt` (control A, control B).
- C2 after cell `cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3` = `records/c2-after.txt` substring; re-run at tip: identical, EXIT=0 (`receipts/c2-counter-at-tip.txt`).
- C3 after cell `mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok` = `records/c3-after.txt` substring; re-run at tip: identical, EXIT=0 (`receipts/c3-counter-at-tip.txt`).
- C3 control cell `survived=13`, `equiv_killed=6` = `controls/c3-control.txt`.
- R1 before cell (plain `findings=3`, fleet-root `findings=0`) = `records/gate-both-modes.txt` base readings. R1 gate at tip, both modes: `findings=0` (`receipts/landing-gate-{plain,fleet}-at-tip.txt`).
- LOG numbers: "items=70 … class_ok=70 unresolved=5 corrected=5" at 34e33a66; "cases=37 pass=37"; "self-test 31 cases" (`receipts/freeze-check-selftest-at-tip.txt` `SELFTEST cases=31 pass=31 fail=0`, EXIT=0); "13 condition-level mutants"; six r41-list survivors killed by older fixtures (`census/round-42/records/survey-prior.txt`: D3, F2, H3, J5, N1, T2 → killed, F1 → `-`); "attack 15 = 37.5 %" (spec: critic 6 + reviewer 4 + mutation-tester 3 + sentinel 2 = 15 of 40); "SOURCES 182 -> 183", "W04 52 -> 52".
- Commit hashes in appended SCORECARD/LOG/SKILL/README text: 15 short or full tokens, all resolve as commits at the tip (`receipts/shorthex-appended-tokens.txt`, `tokens checked: 15`). The 40-hex list in the same lines also resolves (LOG 1925-1929, SCORECARD 841-848, SKILL 292).
- Lesson CORRECTION-DE lines (5): `rev=bf618f6c…` and `derived=` values match the register rows (`census/round-42/c1-register.tsv`: 65 resolved, 5 unresolved; every resolved target exists at base and tip).
- SCORECARD 'C2 measured commit' `5ad7046d…`: the tool blob is identical at `1332067`, `5ad7046` and the tip (`384fc05f280f14496c7bf9e76a0bef699d9834f7`), and `git log 1332067..3105a63 -- tools/souji-freeze-check.py` is empty, so "tool landed at 133206705f" and "measured at 5ad7046d" are consistent.
- SKILL row commands and exit maps, against each counter's docstring and argparse:
  - `r42-c1-counter`: `--root/--rev/--base/--scratch` exist; exit 0/1/2 as docstring (`return 2` at lines 156-172; `return 0 if met else 1` line 249). Tip run: `SUMMARY items=70 … new_mismatches=0`, EXIT=0.
  - `r42-c2-counter`: `--root/--rev/--tool/--scratch` exist; exit 0 met / 1 unmet / 2 could-not-evaluate (lines 365-371, 422). Tip run EXIT=0.
  - `r42-freeze-check-selftest`: `python3 -B tools/souji-freeze-check.py --selftest` → `SELFTEST cases=31 pass=31 fail=0`, EXIT=0. Row's "0 iff … n >= 12" matches docstring.
  - `r42-c3-counter`: `--root/--rev/--fixture/--scratch/--survey` exist (`--survey` once); exit 0/1/2 as docstring. Tip run EXIT=0.
  - `r42-drift-conditions`: `SUMMARY cases=13 pass=13 fail=0`, EXIT=0 (`receipts/r42-drift-conditions-at-tip.txt`); bad tool path gives `SUMMARY cases=13 pass=0 fail=13`, EXIT=1 (seat probe, not a receipt).
  - `r42-r1-counter`: `--root/--rev/--base/--scratch` exist; exit 0/1/2 as docstring. Tip run `SUMMARY findings=0 deleted=2 rows_added=0 stale=0`, EXIT=1 = red by its letter, which the row states.
  - Counter digests in SKILL (c1-items b2601340…, c1-counter 0ab07cd3…, c2-cases 148b7b87…, c2-counter fa44392d…, c3-mutants 2f6f8df3…, c3-counter bf0ebf4f…, drift tool b2a603cf…, r1-counter f2dcbd06…): all match the committed bytes.

## Commands run (exact; output is in `receipts/`)

Read-only, from this seat's scratch clone `/fast/scratch/hyaku/souji-r42/R42w2reviewer06/clone` (`git clone --no-local` of the lane; the lane's own object store reported `bad object bf618f6…` on some calls, a transient state, and the base commit resolved in the fresh clone; `git -C <clone> rev-parse --show-toplevel` = clone dir before any run):

- `git -C <lane> diff --numstat bf618f6… 3105a63… -- SCORECARD.md LOG.md corpus/QUALITY.md SKILL.md corpus/README.md corpus/SOURCES.md corpus/pointer-exemptions.tsv corpus/knowledge` (→ `receipts/numstat-base-to-tip.txt`)
- `git -C <clone> diff --unified=0 bf618f6… 3105a63… -- <same paths>` (hunk headers listed in the table; full diff → `receipts/bookkeeping-base-to-tip.diff`)
- `git -C <clone> show 3105a63…:<file>` for each appended range; `git cat-file -e` / `rev-parse --verify` for paths and commits (→ `receipts/shorthex-appended-tokens.txt`; the path scan was run inline)
- `sha256sum` of pinned blobs (`git show` piped), of fleet files, and `sha256sum -c` of `census/round-42/jj-w1-reports/SHA256SUMS` in the fleet reports directory (OK, OK)
- `python3 -B census/round-42/c1-counter.py --root . --rev 3105a63… --scratch <scratch>` → `receipts/c1-counter-at-tip.txt` (`EXIT=0`)
- `python3 -B census/round-42/c2-counter.py --root . --rev 3105a63… --scratch <scratch>` → `receipts/c2-counter-at-tip.txt` (`EXIT=0`)
- `python3 -B census/round-42/c3-counter.py --root . --rev 3105a63… --scratch <scratch>` → `receipts/c3-counter-at-tip.txt` (`EXIT=0`)
- `python3 -B census/round-42/r1-counter.py --root . --rev 3105a63… --scratch <scratch>` → `receipts/r1-counter-at-tip.txt` (`EXIT=1`, red by letter)
- `python3 -B tools/souji-freeze-check.py --selftest` → `receipts/freeze-check-selftest-at-tip.txt` (`EXIT=0`)
- `python3 -B tools/souji-landing-gate.py --root . --rev 3105a63… --round 41` (plain and `--fleet-root /home/vgpnk/Projects/shokunin`) → `receipts/landing-gate-{plain,fleet}-at-tip.txt` (`findings=0`, EXIT=0 each)
- `python3 -B tools/souji-declared-evidence.py --root . --rev {bf618f6…,3105a63…} --file SCORECARD.md --format counts` → `receipts/declared-evidence-{base,tip}.txt` (`mismatches=70` both; tip `assertions=490 resolved=420 skipped=810`)
- `python3 -B tests/fixtures/r42-drift-conditions.py --tool tools/souji-worktree-drift.py --work <scratch>` → `receipts/r42-drift-conditions-at-tip.txt` (`SUMMARY cases=13 pass=13 fail=0`, EXIT=0)
- `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `receipts/census-end-validate.txt` (rc=0; 52 W04 lines; `ok` line) and `… census …` → `receipts/census-end-census.txt` (`rows 183`, `tier.A 174`, `tier.B 6`, `tier.C 3`, `status.mined 153`, `status.queued 14`, `status.rejected 16`; rc=0)
- The C2 and C3 SUMMARY lines were also observed in full in the first run this session; the receipts above are the re-runs.

Not run: the wave-2 seats' outputs and the other wave-1 seats' attacks (out of this item's scope).

## Environment, tools, and incidents

- No tool was installed, upgraded or removed by this seat (no pacman, uv, npm or cargo). The only processes were the counters and read-only git/census calls above.
- One read-only `find /` (a mistaken scan for a report file) ran as background job `bg_27333` and was killed by the harness at 300 s; it wrote nothing. Disclosed for completeness.
- Scratch `/fast/scratch/hyaku/souji-r42/R42w2reviewer06/` (clone and work dirs) is deleted after the receipts are copied into this seat directory; `shorthex.py` is copied into `receipts/`.
- No write to the lane's tracked files, `.git`, `.jj`, `.ufo/state`, the fleet repo, or `~/.local/bin`. The only file written in the lane is this report and its `receipts/`.

## Residual risk and verification gaps

- The counters admit shape, not substance (lesson N-C1a/N-C2a/N-C3a); this review is a substance check of the bookkeeping text only. I did not re-verify the counters' own logic.
- I did not re-derive the C1 register (65/5) item by item; the register rows and the five CORRECTION-DE lines were checked for shape and for each resolved target existing at base and tip.
- The tip count line for the instrument (D4) is not a claim the counter can fail; it is a QUALITY Q104 clause.
- Wave-1 settlement is not established from committed evidence (D6); this review does not judge the seats' verdicts.
