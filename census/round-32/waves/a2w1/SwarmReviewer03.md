# SwarmReviewer03 — audit of landed C1 rows N12–N19 (round 32, attempt 2, wave a2w1)

## Status

STATUS: PASS — all eight landed rows are honest under the frozen v1+v2 rules at the C1 landing commit: both counters exit 0 on the slice (`unbound=0 mismatches=0 withdrawn=4`), every MATCH row is the cell's own measurement channel (reproduced this run), and every withdrawal reason verified true (three forced, one discretionary-but-true). Two informational observations, no target impact. No coincidental binding found; no wrong withdrawal found.

## Evidence

Audited rev `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93` (C1 landing), base `85b61a151923986e7e6b48f7084b9122561b5f3d`, list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`. Scratch clone `/fast/scratch/hyaku/souji-r32/AuditC1N12N19/r.Q7GJtb/c` (`git clone -q --no-local`, origin removed, detached at the rev; `git rev-parse --show-toplevel` printed the clone). TMPDIR under the seat scratch. No tools installed (none needed).

- Append-only holds: `git diff --stat 85b61a1..9e8982b7 -- SCORECARD.md` = `1 file changed, 43 insertions(+)`; `cmp` of the first 81245 base bytes against the rev bytes: identical prefix.
- Landed rows are the wave-1 delivery insert verbatim: diff of the eight `| N1x |` rows between `.ufo/waves/round-32/w1/deliver-c1-bind-N12-N19.md` and `SCORECARD.md:446-453` at the rev shows zero changes (the delivery's second table is its own explanation, not SCORECARD bytes).
- Blob identity base↔REV: `census/round-21/reason-after.txt`, `census/round-24/records/c2-control-base.tsv`, `census/round-24/records/c2-after.tsv`, `census/round-17/jj-receipts-base5fa6017.txt`, `census/round-21/step-inventory.json`, `census/round-21/r20-closure-excerpt.json`, `tests/fixtures/r17-jj-receipts.sh`, `tests/fixtures/r19-seat-audit-shapes.py`, `tools/souji-coverage-agreement.py` — all SAME. `tests/fixtures/r24-coverage-agreement.py` DIFF (C2 item; the counter runs the base blob, which I ran separately).
- Run reproductions (in the clone, `python3 -B` / bash as bound):
  - N12 `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` rc=0, last digit-bearing line `SUMMARY total=35 failed=0 skipped=2`.
  - N16 `python3 -B tests/fixtures/r19-seat-audit-shapes.py` rc=0, `SUMMARY total=17 failed=0 base_discriminating=12`.
  - N19 `python3 -B tools/souji-coverage-agreement.py --root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c` rc=0, stdout `grounded=6 mapped=6 dangling=0 mismatches=0`, stderr empty.
- Record opens (quotes from bytes opened this run):
  - `census/round-21/reason-after.txt:29`: `SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160` — the only line of the file containing the unit "leaks" (lines 2–28 carry `leak=0`/`base_leak=1`, no "leaks").
  - `census/round-17/jj-receipts-base5fa6017.txt:51`: `SUMMARY total=33 failed=13 skipped=2` — the cell's 13.
  - `census/round-24/records/c2-control-base.tsv:11`: `grounded=4 mapped=2 dangling=0 mismatches=2`; the word "base" occurs zero times in the whole 13-line file.
  - `census/round-24/records/c2-after.tsv:5`: `cmd=python3 -B tools/souji-coverage-agreement.py --root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c`; `:9`: `grounded=6 mapped=6 dangling=0 mismatches=0`.
  - `census/round-21/step-inventory.json`: `steps= 18`; `census/round-21/r20-closure-excerpt.json:40`: `r20-audit-contract 78/78/0 base_discriminating=11`.

Counter v2 (`python3 -B census/round-32/c1-counter-v2.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only N12,N13,N14,N15,N16,N17,N18,N19 --scratch /fast/scratch/hyaku/souji-r32/AuditC1N12N19/cnt`):

```
ITEM	N12	SCORECARD.md:161	literal=failed=0	binding=run	MATCH	bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools rc=0 observed=SUMMARY total=35 failed=0 skipped=2
ITEM	N13	SCORECARD.md:165	literal=19 leaks	binding=withdrawn	WITHDRAWN	the only cited occurrence base_leaks=19 sits on reason-after.txt line 29, which N14 already binds, and the counter forbids a shared occurrence
ITEM	N14	SCORECARD.md:165	literal=leaks=0	binding=record	MATCH	census/round-21/reason-after.txt:29
ITEM	N15	SCORECARD.md:168	literal=18 step	binding=withdrawn	WITHDRAWN	the 18 steps live in census/round-21/step-inventory.json, whose basename line 168 never cites, and no line-named script prints them
ITEM	N16	SCORECARD.md:168	literal=base_discriminating=12	binding=run	MATCH	python3 -B tests/fixtures/r19-seat-audit-shapes.py rc=0 observed=SUMMARY total=17 failed=0 base_discriminating=12
ITEM	N17	SCORECARD.md:168	literal=11 base	binding=withdrawn	WITHDRAWN	the 11 needs the pre-r20 auditor passed as --base-tool, no committed copy of it exists, and line 168 cites no round-20 record
ITEM	N18	SCORECARD.md:175	literal=2 base	binding=withdrawn	WITHDRAWN	census/round-24/records/c2-control-base.tsv line 11 holds mismatches=2 but never the word base, so the A0(b) adjacency the unit demands cannot hold
ITEM	N19	SCORECARD.md:175	literal=mismatches=0	binding=run	MATCH	python3 -B tools/souji-coverage-agreement.py --root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c rc=0 observed=grounded=6 mapped=6 dangling=0 mismatches=0
SUMMARY items=8 bound_run=3 bound_record=1 bound_field=0 withdrawn=4 unbound=0 mismatches=0 partial=1 rev=9e8982b7a6ac57dffa415f9db43cf7cd6e829c93
EXIT=0
```

Counter v1 (`census/round-32/c1-counter.py`, same arguments, scratch `.../cnt-v1`): identical eight ITEM lines, `SUMMARY items=8 bound_run=3 bound_record=1 bound_field=0 withdrawn=4 unbound=0 mismatches=0 partial=1`, EXIT=0.

## Findings — per-row verdicts

| item | verdict | evidence |
|---|---|---|
| N12 | HONEST | The run is the cell's own quoted command (`SCORECARD.md:161` quotes `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` verbatim); the observed `failed=0` is the same SUMMARY field's corrected count — the cell's 13 is the same command's failed count against the 5fa6017 tool dir, recorded at `census/round-17/jj-receipts-base5fa6017.txt:51` `SUMMARY total=33 failed=13 skipped=2`. Restatement is explicitly allowed by the frozen v1 rules ("A run literal may restate the integer (a corrected count)"). Not coincidental: same instrument, same field, deliberately restated. The same-measurement record route is mechanically dead (finding 4), so the run was the only admissible binding. |
| N13 | HONEST (withdrawal forced) | `census/round-21/reason-after.txt` is the only record line 165 cites (no other path, no script stem, no .json); the unit "leaks" occurs on exactly one line of the file (line 29), which N14 binds; the shared-occurrence ban forbids a second binding of (path, line); no run route exists (no tools/ or tests/fixtures/ stem on line 165). Exactly one of N13/N14 had to withdraw; the reason as stated is true. |
| N14 | HONEST | `record: census/round-21/reason-after.txt:29` is the cell's own cited record (`SCORECARD.md:165` names it); `leaks=0` on that line is the repaired count beside `base_leaks=19` — the cell's `leaks19→0` — same round (r21), same measurement. Blob byte-identical base↔REV. |
| N15 | HONEST (withdrawal forced) | `census/round-21/step-inventory.json` does hold 18 steps, but its basename occurs nowhere on line 168 (A0(a) dead — the line names no path at all); the only line-168 script stems are `r19-seat-audit-shapes` and `r20-audit-contract`, and neither fixture's output contains "step" at all (grep count 0 over both base-blob runs), so no run literal with the unit "step" can occur in S. No admissible observable for 18+step. |
| N16 | HONEST | The cell's `r19-seat-audit-shapes17/0 (base12)` is that fixture's own SUMMARY; re-run rc=0 prints `SUMMARY total=17 failed=0 base_discriminating=12` — same measurement, deterministic over committed data, independently re-derived at r21 (`census/round-21/r20-closure-excerpt.json:40` "r19-seat-audit-shapes 17/0 (12 base-disc)"). Not coincidental. |
| N17 | HONEST (withdrawal reason true; discretionary escape documented in finding 1) | All three reason claims verified: (1) the base-blob plain run prints `base_discriminating=0` (no baseline passed) — the 11 indeed requires `--base-tool`; (2) no pre-r20 auditor copy exists at base/REV (three distinct blobs: base `6cf3a85b`, pre-r20 `e5ce94b1` at 12516f7, rev `a9cd8598`) and a counter run argv cannot reach the historical blob (finding 2); (3) line 168 cites no round-20 record. No admissible observable shows the cell's integer 11 — the withdrawn definition ("no observable shows it") is satisfied. |
| N18 | HONEST (withdrawal forced) | All three citable records (`c2-control-base.tsv`, `c2-after.tsv`, `c2-fixture-after.tsv`) contain the word "base" zero times (whole-file sweeps), so no record line can carry the unit; both line-175-named scripts' last digit-bearing lines (`grounded=… mismatches=…`, `cases=9 pass=9 control=FALSE-GREEN-REJECTED`) contain no "base"; no .json is cited on line 175, so no field route. No admissible observable for 2+base. |
| N19 | HONEST | The run is the exact argv recorded at `census/round-24/records/c2-after.tsv:5`, pinned to rev 778747e; the re-run reproduces `:9`'s `grounded=6 mapped=6 dangling=0 mismatches=0` exactly (rc=0). The cell's 0 is that record. Same measurement, reproduced. Tool-byte drift since the r24 receipt noted in finding 3. |

Numbered findings:

1. **(low, informational) N17's withdrawal is discretionary, not forced.** The counter's restated-run clause admits a binding the withdrawal reason does not consider: with the base blob of `tests/fixtures/r20-audit-contract.py` written into the clone at its own path (the counter's exact run harness — `c1-counter-v2.py` run() does checkout/clean then writes the base blob at the script path), a plain run exits 0 with S `SUMMARY total=66 pass=66 fail=0 base_discriminating=0`, so the literal `base_discriminating=0` (one integer, contains the unit "base") would MATCH. The restated 0 is a degenerate no-baseline value, not a corrected count of the baseline-discriminator quantity the cell's `(base11)` names — I do not recommend it as evidence; the honest 11 remains unshowable. Location: landed row `SCORECARD.md:451`; harness `census/round-32/c1-counter-v2.py` run(). No target impact (withdrawn=4 ≤ 8 either way).
2. **(info) N17's "no committed copy of it exists" is true at base/REV but the bytes exist in history.** `tools/souji-seat-audit.py` at `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (ancestor of the audited rev) hashes sha256 `62522acc350c2351…`, matching the r21 recheck's "base auditor extracted from 12516f7 sha256 62522acc". A counter run argv cannot reach it: the fixture's `selected_path` is filesystem-only (`if not candidate.is_file():`, `tests/fixtures/r20-audit-contract.py` blob at 85b61a1, line 420) and the counter runs argv with no shell. Location: `census/round-21/r20-closure-excerpt.json:40`.
3. **(info) N19's re-run is not byte-identical instrumentation.** `census/round-24/records/c2-after.tsv:4` records `tool_sha256=71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897`; the current blob hashes `bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f`. The drift predates the r32 base (`tools/souji-coverage-agreement.py` is byte-identical base↔REV), and the measurement over committed bytes at the pinned rev reproduces exactly — honest, but the receipt's tool sha and the re-run's tool bytes differ.
4. **(info) N12's same-measurement record route is dead by line-level adjacency, not merely by the literal rule.** Record MATCH also requires unit–integer adjacency ON the line (`adjacent(text, units, x)` in the counter); no line of either glob-cited `census/round-17/jj-receipts-*.txt` at base has "fail" adjacent to 13 (adjacency sweep over both files: zero hits — `failed=13` puts "ed=" between). So the run restatement was the only admissible binding, and the cell's 13 remains evidenced by `census/round-17/jj-receipts-base5fa6017.txt:51`.
5. **(scope note) My slice is clean at the C1 landing commit; the disclosed full-set miss lives outside it.** `census/round-32/records/amendments.txt` discloses the L1's attempt-1 after-reading `unbound=6 mismatches=6 withdrawn=17` at the integration commit (unverified per the wave brief). My eight rows contribute 4 verified withdrawals and 0 unbound / 0 mismatches at `9e8982b7`; if the full-set reading holds anywhere, the frozen `withdrawn<=8` cap fails on the other 36 items — the L1's re-landing problem, not a defect in N12–N19.

## Attack log

- **A1 — rebind N12 to its own round-17 record (same measurement).** DEAD: swept both `census/round-17/jj-receipts-*.txt` blobs at base with the exact adjacency pattern (`fail[^A-Za-z0-9]{0,3}13` / `13[^A-Za-z0-9]{0,3}fail`): zero hits; the run restatement is the only admissible route.
- **A2 — free line 29 for N13 by rebinding N14 elsewhere.** DEAD: lines 2–28 of `census/round-21/reason-after.txt` carry `leak=0`/`base_leak=1` — the unit "leaks" occurs only on line 29; N14 has no alternative either; one withdrawal was forced.
- **A3 — run route for N15 (step observable from a line-168-named script).** DEAD: base blobs of `r19-seat-audit-shapes.py` and `r20-audit-contract.py` print no "step" anywhere (grep count 0 in both outputs); no other stem occurs on line 168.
- **A4 — break N17's withdrawal via a restated run.** LIVE mechanically (finding 1, reproduced in the counter's own harness), but the restated 0 does not show the cell's 11; the withdrawal reason's claims are all true, so the row stands as HONEST with the escape documented.
- **A5 — break N18's withdrawal via the run route.** DEAD: base blob of `r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` in-clone: rc=0, S `cases=9 pass=9 control=FALSE-GREEN-REJECTED`, zero "base" in the whole output; `souji-coverage-agreement.py`'s counts line never contains "base"; all three citable records contain "base" zero times; no .json cited on line 175.
- **A6 — reach the pre-r20 auditor for N17's true 11 via `--base-tool`.** DEAD: `selected_path` is filesystem-only (`tests/fixtures/r20-audit-contract.py` blob at 85b61a1:414-422), the counter runs argv with no shell, and the worktree at REV holds the current auditor; the historical blob is unreachable from a single argv.

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmReviewer03.md` (this report). No other files written; no tools installed; scratch `/fast/scratch/hyaku/souji-r32/AuditC1N12N19/` removed after writing.
