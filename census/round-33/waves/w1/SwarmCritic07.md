# SwarmCritic07 — C1 item K07 falsification (Souji r33, w1)

## Status
STATUS: PASS — K07 **HOLDS**. The frozen argv printed `SUMMARY total=29 failed=0` with rc 0 in all five clean runs at
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; the frozen predicate is a faithful, mutant-discriminating reading of the
cell's stated outcome; the cell carries no second stale count. Verdict: **HOLDS**. Three out-of-set residuals are
reported (items 4–7 in Findings); none of them is a defect of the item, the predicated command or the tool.

## Evidence
Revision measured everywhere: `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. Scratch clone
`/fast/scratch/hyaku/souji-r33/AuditK07/c` (`git rev-parse --show-toplevel` printed it; `status --porcelain` = 0 lines;
detached at 2d9bca5; `remote remove origin` at once). No tool installs, no pacman, no lane writes outside this file.

E1 — cell under test (SCORECARD.md:160 at base; `git diff --stat 6017a48..2d9bca5 -- SCORECARD.md` empty, so the row is
byte-identical at the measured rev). Verbatim cells: `python3 tests/fixtures/r17-census-hygiene.py --census
tools/souji-census.sh` then `29/0`; second span `census/round-17/c1-matrix-4f48343.json`; prose clauses: dirty counts
immune to repo-local/included/config.worktree suppression; hardlinked or non-regular `info/attributes` degrades only its
repository; empty metadata files and non-C message locales stay accepted.

E2 — determinism, direct argv, three runs (runs 1–2 fresh `TMPDIR`, run 3 `TMPDIR` unset via `env -u TMPDIR`):
```
$ cd <clone> && TMPDIR=<fresh> python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh
TOOL	<clone>/tools/souji-census.sh	sha256=c1671f4c5ef9d45cf483cf12787103ecb60aae8a5f4059425dc4da1feb79b114
SUMMARY	total=29	failed=0
rc=0
```
runs 1/2/3 identical: `SUMMARY total=29 failed=0`, rc=0 each; `diff` of the non-SUMMARY output run1-vs-run2 and
run1-vs-run3 = `IDENTICAL`. Per-case distribution run1: 29 CASE lines, `observed_exit=0` ×21, `observed_exit=2` ×8;
classes 13 repair, 8 preserve, 8 refuse. The fixture hardcodes its scratch root (`dir="/var/tmp"`, fixture:1279), so
`TMPDIR` cannot change the run.

E3 — frozen counter, clean PATH (`PATH=/usr/local/bin:/usr/bin:/bin`), two runs:
```
$ python3 -B …/census/round-33/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/AuditK07/cnt2|3 --only K07
ITEM	K07	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=29 failed=0
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
counter rc=0
```
(`partial=1` is the counter's own `--only` marker, c1-counter.py:307.)

E4 — same counter, inherited PATH, 14:07, same rev/`--only K07`:
```
ITEM	K07	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=FileNotFoundError: [Errno 2] No such file or directory: '/home/vgpnk/.local/bin/git'
SUMMARY items=1 agree=0 mismatches=1 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
```
Cause is foreign, not the item: at 14:05 `ls -l /home/vgpnk/.local/bin/git` showed
`-rwxr-xr-x 1 vgpnk vgpnk 2923 Oct 26 14:05 /home/vgpnk/.local/bin/git`; its body set
`ROOT = "/fast/scratch/hyaku/kengaku-r40/R40CritC1Counter/w/k40-c1-khz2nxzu"` and it `execv`s `/usr/bin/git` for repos
not in its PLAN. By 14:09 the path was gone (`No such file or directory`); the child that had resolved it died with the
FileNotFoundError above. Its owner (`R40CritC1Counter`, round-40 C1 critic attack, fixture `crit_git_shim.py`) confirmed
on the record: the build wrote the shim into a directory on the ambient PATH, its own cleanup `rm -f` removed it between
lookup and exec, so the failure is a TOCTOU on a foreign artefact, not an r33 counter behaviour; that sweep is over and
`~/.local/bin/git` is absent now.

E5 — predicate discrimination, mutant tools in scratch only (copies of the committed bytes; lane untouched):
- mutant A (`--untracked-files=normal` removed from `tools/souji-census.sh:1240`): `SUMMARY total=29 failed=5`, rc=1,
  failures R17-01 R17-02 R17-03 R17-04 R17-16 → the D1 immunity clause is enforced.
- mutant B (`meta_soft "git-metadata-nonregular"` removed, `tools/souji-census.sh:690`): `SUMMARY total=29 failed=4`,
  rc=1, failures R17-08 R17-09 R17-24 R17-26 (`git-metadata-unsupported line count 0 want 1|2`) → the D2 degradation
  clause is enforced.
Both mutants make the frozen predicate FAIL, so the predicate is not satisfied by a regressed tool.

E6 — locale clause is live here, and vacuity is scored: `stat -L -c %F` under `LANGUAGE=de` printed `reguläre Datei`, so
R17-28 is non-vacuous on this host. Forcing the branch (fixture copy, `vacuous = True`) gave
`CASE R17-28 FAIL … locale discrimination is vacuous on this host`, `SUMMARY total=1 failed=1`, rc=1.

E7 — cell's second span re-derived: `git rev-parse --verify 4f48343` = `4f4834390ad4845b76804e94cc04d8f867ef9b54`;
`census/round-17/c1-matrix-4f48343.json` `arms.changed.r17-hygiene` = `total 29, failed 0, rc 0`; control arms
`pre-harm` failed 21, `r14-harm` failed 14, `r16` failed 14. The record binds `fixtures_sha256[r17-hygiene]` =
`8cd53c56e190d537eda46e8d6bf36156607c7e6a0227951040c8f0a9e5fc7290`, while the fixture at 2d9bca5 hashes
`367b3bcb8013a860cbde763f472874a154c4e82986441adc53125da2d1bad556`; the record carries no tool digest.

## Findings
1. K07 agrees at the measured revision: row at SCORECARD.md:160, command and outcome reproduce (E2, E3). No
   restatement is needed and none is required by the frozen rules.
2. The frozen predicate (`total=29 && failed=0`, alt `29/29`) is a faithful reading of `29/0`: the fixture prints
   `SUMMARY total=29 failed=0`, returns 0 iff `failed == 0`, `total` is `len(ran)` over `EXPECTED_IDS` (29 unique,
   fixture:73), and an id-set guard turns any short/long run into a failure. The `29/29` alternative is dead for this
   command (the fixture never prints that form) and cannot admit a failing run because the exit gate requires rc 0.
3. Not lax: both prose clauses have an executed counterexample (E5). Not stricter: nothing beyond the cell's 29/0 plus
   the exit the 0-failure count implies. A legitimate future case addition would break the predicate — intended, that is
   exactly what a restatement row is for.
4. No other stale outcome in the cell: the only other span is a record path with no stated count, and that record's
   `changed` arm still reads 29/0 (E7). Residual: the record cannot certify the current command — it binds an older
   fixture digest and no tool digest, so it is a historical pointer only (location:
   census/round-17/c1-matrix-4f48343.json, keys `fixtures_sha256`, `runner_sha256`).
5. Measurement is PATH-inherited, not PATH-scrubbed: `run_item` passes `dict(os.environ, …)` to `bash -c`
   (c1-counter.py:163), so any `git` earlier on the caller PATH is used by the fixture. A foreign shim on
   `~/.local/bin` (on the fleet PATH) flipped this seat's first counter reading to MISMATCH (E4); its owner confirmed
   the plant-and-cleanup TOCTOU. That is a caller-environment artefact, not a K07 nondeterminism — the two clean-PATH
   readings agree, and it is reported so no seat scores the MISMATCH against C1.
6. The fixture ignores `TMPDIR` and writes under a literal `/var/tmp` (tests/fixtures/r17-census-hygiene.py:1279), dying
   with `cannot create /var/tmp fixture` if that root is unwritable. That is the same scratch-discipline class C2 routes
   for the r15 fixtures, but this fixture is not in C2's frozen legs — out-of-set residual, no leg change proposed.
   Failure mode is [INFERENCE] from the code path (not executed). Residue observed after this seat's runs:
   four dirs `/var/tmp/r17-census-hygiene.*` (14:07:02, 14:09:30, 14:09:36, 14:09:39; 2.5–7.2 MB each). The fixture's
   `cleanup()` should have removed them; ownership (this seat vs another concurrent seat) is not provable, so they were
   left in place and are reported, not deleted.
7. Host-conditioned truth: R17-28 FAILs by design when no `de` gettext catalog exists (E6), so the cell's
   `non-C message locales stay accepted` clause — and therefore K07's 29/0 — holds only on a host with that catalog.
   Present here (`reguläre Datei`). [INFERENCE] for other hosts.
8. C2 coupling: `tools/souji-census.sh` is a C2 repair target (leg O4). Once C2 lands, the C1 tip reading re-runs K07
   against changed tool bytes; O4's own leg pins no-slash output equality with base, so agreement is expected
   [INFERENCE] — but the tip reading is the only thing that can show it.

## Attack log
A1 Determinism: 3 direct runs at fixed bytes (fresh TMPDIR ×2, TMPDIR unset ×1) → identical output, 29/0, rc 0.
A2 Determinism under the frozen counter: 2 clean-PATH runs → AGREE. A third reading (inherited PATH) MISMATCHed only
   because a foreign `~/.local/bin/git` shim was installed and then removed by another lane mid-run (E4); re-run with a
   scrubbed PATH agrees. Not scored as item nondeterminism.
A3 Predicate laxness: 2 regressed tools (drop pinned untracked flag; drop non-regular diagnostic) → failed=5 and
   failed=4, rc=1, predicate FAILS both times. No regressed tool passing the predicate was found, and the exit gate
   closes the "stray digits in output" route because rc 0 requires failed == 0.
A4 Predicate strictness: no run that satisfies the cell fails the predicate; the only way a true 29/0 run can fail it is
   a fixture edit that changes the case count, which is a changed statement, not a stricter predicate.
A5 Stale-outcome sweep inside the cell: prose clauses executed (E5, E6); record re-read (E7). Nothing stale.
A6 Frozen-surface check: item, predicate, argv, files and legs unchanged; all mutation work happened on copies under
   `/fast/scratch/hyaku/souji-r33/AuditK07/`, never on a lane file.

Verdict: **HOLDS**. (Not LAX-PREDICATE, not STRICT-PREDICATE, not NONDETERMINISTIC — the one divergent reading was a
foreign PATH shim, reproduced and attributable, with two clean readings agreeing before and after.)

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic07.md` (this report).
- Scratch `/fast/scratch/hyaku/souji-r33/AuditK07/` removed after these receipts were copied out (clone, mutants,
  fixture copy, counter scratch dirs).
