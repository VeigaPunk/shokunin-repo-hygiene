## Status
STATUS: PASS — 13/13 MISMATCH rows of c1-before.txt traced to the commit that wrote the literal, the round record that showed it, and the later change; all 13 stated counts were accurate when written (0 fabricated), and one MISMATCH (R18) is a counter artifact rather than a lane defect.

## Evidence
Preregistration read first: `census/round-30/records/preregistration.txt` (frozen C1/C2/C3). Base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; lane tip `df6afe817d096e4ad71ba2b9cc21a83f126eb658` (prereg `d4928ec`, controls `bae103c`, D3 `df6afe8`). All reads via read-only `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log/show/blame/cat-file/ls-tree/grep`. No lane writes except this report and the delivery TSV.

Attribution method (per row, two instruments):
1. Prescribed pickaxe: `git -C <lane> log -S'<literal>' --format='%h %ad %s' --date=short -- SCORECARD.md` — e.g. `-S'→ 5/5'` → `23014d4 2026-10-20 round-13: record verified claims, source frontier and measured revisions`; `-S'18/18'` → `163158a`, `42d9ff3`, `e41db6d`, `4eb2fda`; `-S'29/0'` → 5 commits; `-S'cases=15 pass=15'` → `de874ee` only.
2. Row disambiguation, because several rows share a literal: pickaxe on the literal plus its unique cell context (e.g. `→ 5/5; same corrected fixture baseline red`), and `git blame -L152,175` / `-L313,314` at base. Blame at base: 154→`23014d4`, 155→`23014d4`, 158→`163158a`, 160/161→`d98065d`, 166/167→`1db7108`, 173→`4765250`, 174/175→`07f83e6`, 314→`de874ee`.

Round records that showed the literal when written (verbatim from committed bytes at that round):
- `census/round-13/verification.json` results `quarantine-bounds`: `SUMMARY total=5 failed=0 hung=0`; results `structure-selftest`: `selftest=PASS ids=5/5`.
- `.ufo/waves/round-16/w1/LandingGate.md:56`: `` `SELFTEST pass=18 fail=0`, RC=0 ``; `.ufo/waves/round-16/w1/LandingGateFixture.md:45`: `SUMMARY total=15 failed=0`.
- `census/round-17/c1-matrix-4f48343.json` arms.changed.r17-hygiene: `"failed": 0, "total": 29`; `census/round-17/jj-receipts-4f48343.txt:54`: `SUMMARY total=35 failed=0 skipped=0`.
- `census/round-19/c2-smoke.txt:6`: `SUMMARY total=11 failed=0`; `:28`: `SUMMARY total=13 failed=0 base_discriminating=6`; `census/round-19/c1-carry.txt:18`: `SUMMARY total=4 failed=0 base_discriminating=2`; `:7`: `SELFTEST pass=65 fail=0`.
- `.ufo/waves/round-23/w1/ExecFixtureAgreement.md:39`: `Same fixture, same bytes, one case earlier in the wave: selftest=9/9`.
- `census/round-24/records/c1-after.tsv:17`: `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`; `c2-fixture-after.tsv:27`: `cases=9 pass=9 control=FALSE-GREEN-REJECTED` (both committed at `ca7fc1c`, r24).
- R18 has no committed green record; nearest is the red arm `census/round-29/records/c2-fixture-red-before.txt:22`: `cases=15 pass=8 control=TAMPER-REJECTED`.

Later changes (fixture/count histories):
- `728b2ce` (r25) extended `tests/fixtures/r13-repo-structure.sh`: comment changed to `final line: `selftest=PASS ids=7/7` (--probe mode)` (5→7 ids).
- Landing gate selftest count: 18 (r16) → 28 at `ddb7347` (`.ufo/waves/round-17/w2/MutateGateExact.md:18` control run: `(27 pass / 1 fail)`) → 61 at `4800fd7` (`corpus/lessons/round-18-verifier-spotcheck.md:82`: `gate selftest `pass=61 fail=0``) → 65 at `005f3d3` (`corpus/lessons/round-19.md:17`: `` `SELFTEST pass=65 fail=0` (61 before ``).
- r23 record-agreement fixture CASES (AST count of the `CASES` list): 9 at `4765250` → 11 at `1dd8b1e` → 12 at `c872eec` → 15 at `728b2ce`; `selftest=15/15` at `.ufo/waves/round-25/w1/RevR17-evidence/exec_fx-base.out:19`.
- r24 size-census fixture CASES: 8 at `1efe406` → 12 at `679e2d0` (r25); `census/round-25/records/c2-after.tsv:21`: `cases=12 pass=12 ...`.
- r28 capture fixture unchanged after `b862007`; `--tool` on the r24 coverage fixture required since creation: `tests/fixtures/r24-coverage-agreement.py:331` `ap.add_argument("--tool", required=True)` at both `1efe406` and base.

Executed check of R18 (my own run; base bytes confirmed): `sha256sum tests/fixtures/r28-wave-evidence-capture.sh` = `cfac67d9…` equals `git cat-file blob 9420341:tests/fixtures/r28-wave-evidence-capture.sh`; same for `tools/souji-wave-evidence-capture.sh` = `c19420a4…`. Run: `TMPDIR=/fast/scratch/hyaku/souji-r30/SwarmRevenger34 bash tests/fixtures/r28-wave-evidence-capture.sh` → rc=0; stdout line 47: `cases=15 pass=15 control=TAMPER-REJECTED`; stderr line 10: `Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]`.

## Findings
1. Zero fabricated literals. Every one of the 13 stated counts matched the round's recorded output when written; none is `never true`. Full attribution in `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`.
2. 10 of 13 are condensed forms the counter's substring test cannot match (`summary_line` returns one line; match is `stated in s`): `5/5` vs `SUMMARY total=5 failed=0`, `29/0`/`35/0`/`4/0`/`11/0`/`13/0` vs `total=N failed=0`, `15/15` vs `SUMMARY total=15 failed=0`, `8/8` vs `cases=8 pass=8` (tools/souji-capability-agreement.py:76,171).
3. Two rows were literally true and then drifted. R04 `SCORECARD.md:155` `→ 5/5` matched `selftest=PASS ids=5/5` (census/round-13/verification.json) and broke at `728b2ce`. R14 `SCORECARD.md:173` `9/9` matched `selftest=9/9` (.ufo/waves/round-23/w1/ExecFixtureAgreement.md:39) and broke at `1dd8b1e`, reaching 15 at `728b2ce`.
4. R05 `SCORECARD.md:158` has been stale since round 17: 18→28 at `ddb7347`, →61 at `4800fd7`, →65 at `005f3d3`; the same line carries `15/15` for a fixture that still prints `SUMMARY total=15 failed=0`, so only the gate half drifted.
5. R15/R16 `SCORECARD.md:174-175` were appended at `315422b` (r24, counts accurate then), removed at `a529c76` and re-appended verbatim at `07f83e6` (r26) — by then the size-census fixture had 12 cases (`679e2d0`), so the current line 174 text was already false when re-appended. Base blame therefore points at `07f83e6`, not the first writer.
6. R16 `SCORECARD.md:175` cites `python3 -B tests/fixtures/r24-coverage-agreement.py` with no `--tool`; the flag has been required since the fixture's creation (`1efe406`), so the cited command has never run (base rc=2, `c1-before.txt` R16 rc=2). The `9/9` itself is real: `census/round-24/records/c2-fixture-after.tsv:27` printed `cases=9 pass=9`.
7. R08 `SCORECARD.md:161` `35/0` is still accurate; its `skipped` moved 0→2 between the r17 record and base because the documented command omits `--baseline-dir` and both J6 comparisons then skip (tests/fixtures/r17-jj-receipts.sh:963,982; the r17 record header carries `TOOL-BASELINE`).
8. R18 `SCORECARD.md:314` `cases=15 pass=15` is printed by the base fixture on stdout (my run, rc=0). It has no committed green receipt anywhere in the lane (sweep: `git grep -n 'cases=15 pass=15' 9420341` returns only `SCORECARD.md:304`, `SCORECARD.md:314`, `SKILL.md:227`). The r29 claim rests on uncommitted runs; only the red arm is committed.
9. Fixture residue (observation, not deleted): `tests/fixtures/r28-wave-evidence-capture.sh:51` defaults its scratch root to `/var/tmp/souji-r29-wave-capture-fixture` and ignores `TMPDIR`; after my run that base directory exists empty. It may predate this run, so I left it in place rather than delete it.

## Attack log
A1 — C1 counter can be blinded by stderr (attack on the instrument, not a lane defect). `tools/souji-capability-agreement.py:155` builds the observed text as `rc, out = q.returncode, (q.stdout + q.stderr).decode("utf-8", "replace")` and `summary_line` (:76) returns the last digit-bearing line, so any stderr line emitted after stdout shadows a correct final summary. Demonstrated on R18 at base: rc=0, stdout ends `cases=15 pass=15 control=TAMPER-REJECTED`, stderr ends with the tool usage line, and the counter reports `MISMATCH kind=value` for a literal that is currently true. Consequences: (a) R18 must not be "corrected" as if it were a defect; (b) any future row whose command writes digits to stderr is uncorrectable through `R30-CORRECTION … observed=` lines; (c) the `k1` before/after numbers mix real drift with this artifact. Counter left unchanged per the frozen contract; classification of R18 in the delivery is stated as an artifact rather than one of the three provenance classes.

## Deliveries
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv (13 rows; columns id, line, stated, writing_commit, record_path, changing_commit, class)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/SwarmRevenger34.md (this report)

Scratch `/fast/scratch/hyaku/souji-r30/SwarmRevenger34/` removed after the receipt lines above were copied into this report. Tooling: no installs or upgrades. No lane git/jj mutation; no host service touched.
