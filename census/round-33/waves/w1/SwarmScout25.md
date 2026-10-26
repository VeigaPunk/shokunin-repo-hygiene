# SwarmScout25 - C1 enumeration rule vs SCORECARD.md / SKILL.md Gate registry (round 33, w1)

## Status
STATUS: PASS - every table row of SCORECARD.md and every numeric SKILL.md Gate registry row was classified, and each runnable miss or exclusion was executed once (some rerun) at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; 67 rows delivered. Nothing in the frozen set was touched.

## Evidence
Revisions: bytes read at `6017a482e7068d5afb7617640198fbb0fe743357` (`git show <base>:SCORECARD.md`, `:SKILL.md`, 494 and 425 lines); commands run at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`.
Method: scratch clone `/fast/scratch/hyaku/souji-r33/EnumerationMisses/c` (`git clone -q --no-local`, origin removed, `rev-parse --show-toplevel` printed the clone), one `git worktree add --detach` per command, `TMPDIR` under the scratch dir, PATH `/usr/bin:/bin` plus a jj symlink (see Finding 7).
Span sweep: Python `re` over every `|` row of the base SCORECARD.md for backticked spans naming `python3|bash|tools/|tests/fixtures/|git|grep|sha256sum|sources-census` (all sections); compared per line with the `line` column of `census/round-33/c1-items.tsv`. Inside `## Capabilities` and the five capability-rows sections every command-plus-outcome span is a Kxx; the lines :148, :150, :162, :172 (first span), :173 (first span), :174 (first span), :175 (first span), :487, :490 are command spans without an adjacent outcome.

Key readings (all rc as printed, at 2d9bca5):
- E01 `python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev 9301d98c1c689c79741f0f1ba1f171138d20af07 --format counts` -> rc 0 `assertions=63 resolved=63 skipped=40 mismatches=0`.
- E34 `python3 tests/fixtures/r13-cert-evidence.py` -> rc 0 `fixture: 5/5 checks passed`.
- G21 `python3 -B tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py` -> rc 1 `cases=20 pass=0 control=FALSE-GREEN-REJECTED`; same fixture with an absolute `--tool` or none -> rc 0 `cases=20 pass=20 control=FALSE-GREEN-REJECTED`.
- G17 `bash census/round-21/replay-matrix.sh --runner census/round-21/run-acceptance.py --lane <clone> --rev 2d9bca55... --work <new>` -> rc 1, `SCENARIO S1/S2/S3 ... matched=16/18`; unmatched `r20-audit-contract` and `r20-input-binding`.
- G08 `bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh` -> rc 1 `SUMMARY total=19 failed=18` (two runs).
- G11 `python3 tests/fixtures/r20-input-binding.py` -> `SUMMARY total=45 pass=45 ...` (registry: 36); with `--baseline 12516f7d...` `total=52 pass=52 ... baseline_mismatches=31`.
- E12 `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` -> `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`; E13 `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` -> `selftest=PASS ids=7/7` (K17 and K04 state 8/8 and 5/5 for these argvs).
- E32/G28: r32 C2 counter at `98e5203d...` -> `SUMMARY items=27 pass=26 fail=1` (T18); do-nothing arm `items=27 pass=1 fail=26`.
Full table with every command, outcome, clause and reading: `.ufo/waves/round-33/w1/deliver-c1-enumeration-misses.md`.

## Findings
1. Rule sound inside its scope: `census/round-33/c1-items.tsv` header vs SCORECARD.md `## Capabilities` (:143-175) and `### Round 29/30/31/32 capability rows` (:309-315, :350-356, :418-425, :483-491): no omitted command-plus-outcome span. K05, K04, K17, K18 have their stale numbers beside correct ones elsewhere (K05: SKILL.md:217 `65/0` reproduces; K04: SCORECARD.md:42 `ids=7/7`; K17: SCORECARD.md:41 `cases=12 pass=12`; K18: its `--tool` argv at :68 reproduces 9/9; the bare K18 argv was not run by this seat).
2. MISSED by the section clause (SCORECARD.md:14, Axes row; quote: "`--format counts` → `assertions=63 resolved=63 skipped=40 mismatches=0`, exit 0"): fully specified argv plus arrow outcome; reproduces. Also SCORECARD.md:369 (supersession table, bare `tests/fixtures/r13-cert-evidence.py`, quote: "records the stdout line `fixture: 5/5 checks passed`"); reproduces.
3. The `### Round N measurements` tables (SCORECARD.md:21-23, :31-33, :40-42, :67-71, :101-103, :303-305, :344-346, :412-414, :477-479) state outcomes in a `before`/`after` cell, not right after the command, and use `<full40>`/`<lane>` with a measured commit named in the last cell. The "immediately followed" clause cannot bind there. Run with the named commit filled in, most reproduce exactly; the ones that do not are drift or rev-bound counts (deliverable E04, E05, E06, E07, E14, E18, E20).
4. SKILL.md Gate registry is outside the rule. Rows with a numeric outcome for a self-contained or blob-completable command that do NOT reproduce at 2d9bca5: `:245` (G21, `--tool tools/souji-registry-agreement.py` as written -> `cases=20 pass=0`, relative path resolved from the fixture's scratch cwd; the fixture also hard-codes `/var/tmp/souji-r29-c1-fixture`), `:235`/`:241` (G17, 16/18), `:225` (G08, 1/19 pass), `:234` (G11, 36 vs 45), `:220` (G06, "r19 historical 73/0" vs 118/0).
5. `:201` (`TMPDIR=/var/tmp bash tools/souji-census.sh --selftest`, "69/0 at 4800fd7") is load-sensitive: first run `selftest: 69 checks, 3 failed`, second `69 checks, 0 failed` (host load average ~90).
6. Frozen-header wording nit: :148/:150 state no outcome but are listed with the "outcome without a backticked command" rows; :172, :487, :490 carry a backticked path. Verdicts unaffected.
7. Environment hazard: a transient `git` shim in `/home/vgpnk/.local/bin` (seen as `can't open file '/home/vgpnk/.local/bin/git'` in the first pass, rc 1 for the r28 wave-capture fixture and the r29 C2 counter, both rc 0 on the clean-PATH pass) is a shared-PATH risk for any counter that runs fixtures with the inherited PATH; my reported readings are from a pass with a clean PATH. One early `r25-coverage-agreement` rc 1 did not recur in three runs [INFERENCE: same shim].

## Deliveries
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-33/w1/deliver-c1-enumeration-misses.md`
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-33/w1/SwarmScout25.md` (this report)

Scratch `/fast/scratch/hyaku/souji-r33/EnumerationMisses` removed at the end of the run (see below). No tools installed. No lane file other than the two above was written.
