# SwarmExecutor02 — r30 C2 fixture (BUILD + first falsifiers)

## Status
STATUS: PASS — `tests/fixtures`-bound fixture delivered as a wave file and measured red-before on the base gate (`cases=7 pass=3`), satisfiable on a scratch green prototype (`cases=7 pass=7`), and each D6 hardening world proven load-bearing by its own mutant arm; no lane mutation, no scratch tree left on disk.

## Evidence

Lane revision facts (read-only): base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`, preregistration `d4928ec86b667e3d1ed0adb07fb088e500cf1631`, controls `bae103cba91884947a0557940e60c320f5512f75`, lane HEAD while working `df6afe817d096e4ad71ba2b9cc21a83f126eb658`. The gate is unchanged base..HEAD: `git -C <lane> diff --numstat 9420341d..HEAD -- tools/souji-landing-gate.py | wc -l` -> `0`.

Base tool extracted from committed bytes, never the worktree:
`git -C <lane> show 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b:tools/souji-landing-gate.py > /fast/scratch/hyaku/souji-r30/C2Fixture/base-gate.py`
-> blob `e67810d130817879fddd71c5ceeb5d5fd37e6ea8`, sha256 `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`, 2326 lines.

Fixture frozen at sha256 `e830339332aa6ae1b1f614e33445327b68f47d0904428a04d6d812e394c66271` (554 lines).

RED-BEFORE (required by the frozen contract; full receipt `deliver-c2-fixture-red-before.txt`):
```
TMPDIR=/fast/scratch/hyaku/souji-r30/C2Fixture python3 -B .ufo/waves/round-30/w1/deliver-r30-landing-gate-discovery.py --tool <scratch>/base-gate.py
CASE D1 FAIL exit=2 reports=0 status=0 findings=0 FAIL(COULD-NOT-EVALUATE printed; exit=2; checked_reports=0 want 2; status_lines=0 want 2)
CASE D2 PASS exit=2 reports=0 status=0 findings=0
CASE D3 PASS exit=1 reports=1 status=1 findings=1
CASE D4 FAIL exit=1 reports=1 status=1 findings=3 FAIL(template token flagged: round-%s; template token flagged: round-{N})
CASE D5 PASS exit=1 reports=1 status=1 findings=3
CASE D6 FAIL exit=1 reports=1 status=1 findings=1 FAIL(mapped: exit=1 want 0; mapped: capture-backed pointer flagged)
CASE D7 FAIL exit=2 reports=0 status=0 findings=0 FAIL(COULD-NOT-EVALUATE printed; exit=2 want 1; checked_reports=0 want 1; missing LG-SEAT-UNCARRIED)
CONTROL always-zero-emitter FALSE-GREEN-REJECTED failed=D1,D2,D3,D5,D6,D7
cases=7 pass=3 control=FALSE-GREEN-REJECTED
RC=1
```
Base fails D1, D4, D6, D7 — D1 red satisfies the assignment's minimum.

SATISFIABLE + mutant arms (receipt `receipt-c2-fixture-arms.txt`), same fixture bytes, three scratch prototypes that replace only `check_carry`, `_pointer_paths` and `_path_exists_in_tree`:

- green: discovery + template skip + round-bound capture alias -> `cases=7 pass=7 control=FALSE-GREEN-REJECTED`, `RC=0`.
- loose mapper: capture alias ignores the pointer's round -> `cases=7 pass=6`, `D6 FAIL ... mapped-missing: uncaptured pointer not flagged`.
- directory-only: alias resolves on the capture directory only -> `cases=7 pass=6`, `D6 FAIL ... mapped-dir: capture-directory-only resolution`.

Green prototype `--selftest` printed `SELFTEST pass=65 fail=0` — the base value, so the patch list above does not move the REGRESS literal the frozen contract pins.

Fixture self-guards (run against the base tool): `TMPDIR` unset -> `PREREQ FAIL TMPDIR is unset (build synthetic repos under $TMPDIR)` + `cases=0 ... control=FALSE-GREEN-ACCEPTED`, rc 2; `TMPDIR` inside the lane -> `PREREQ FAIL TMPDIR /home/vgpnk/Projects/shokunin/souji-shokunin/census is inside the fixture git checkout /home/vgpnk/Projects/shokunin/souji-shokunin`, rc 2, refused before any repository was created.

Default `--tool` resolution (the L1's invocation, no flag): `TMPDIR=<scratch> python3 -B <scratch>/fakelane/tests/fixtures/r30-landing-gate-discovery.py` -> `cases=7 pass=3`, i.e. it resolves `<lane>/tools/souji-landing-gate.py` from the fixture's own path.

Cross-check against the wave-1 candidate gate (receipt `receipt-c2-fixture-candidate.txt`): `.ufo/waves/round-30/w1/deliver-souji-landing-gate.py`, sha256 `ba37e6bf804db1ad16b2ab53878a6626308bebb854af9bc2e7d230de81cd9056`, run through the same fixture bytes -> `cases=7 pass=7 control=FALSE-GREEN-REJECTED`, and its own `--selftest` -> `SELFTEST pass=65 fail=0`.

Report-count facts for the C2 target, both `86`:
`git -C <lane> ls-tree -r --name-only 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b census/round-29/waves | grep -c '\.md$'` -> `86`; `find <lane>/.ufo/waves/round-29 -name '*.md' -type f | wc -l` -> `86`.

Environment hygiene: no packages installed or upgraded (nothing was needed, pacman untouched); every synthetic repo built under `/fast/scratch/hyaku/souji-r30/C2Fixture`; `python3 -B` throughout; `/var/tmp/souji-landing-gate-*` leftovers after the final runs: `0`; the scratch dir was removed after the receipts were copied into this wave dir.

## Findings

1. The base gate cannot evaluate a round's committed reports at all. `tools/souji-landing-gate.py:469` `prefix = ".ufo/waves/round-%d/" % round_no` and `:474` `raise EvalError("no .md reports under %s at %s" % (prefix, rev))` — the capture `census/round-29/waves/` (86 .md) is never consulted, so round 29 is exit 2 / COULD-NOT-EVALUATE. Measured: D1 `exit=2 reports=0`, D7 `exit=2`.

2. Template tokens still dangle at base. `tools/souji-landing-gate.py:148` `ROUND_PLACEHOLDER_RE = re.compile(r"round-N", re.IGNORECASE)` covers only the literal `round-N`, and the `<>*` skip at `:829` covers only `round-<N>`; measured D4 rows flag both `census/round-%s/` and `census/round-{N}/x` as LG-DANGLING-PTR.

3. Capture-mapped pointers are unresolved at base: `.ufo/waves/round-31/w1/X.md` is flagged although `census/round-31/waves/w1/X.md` is committed (D6 `mapped: exit=1 want 0`). No mapping from `.ufo/waves/round-<n>/` to `census/round-<n>/waves/` exists in `check_pointers` (`:905-990`).

4. D3 passes on base, so live-dir precedence is pre-existing behaviour, not new surface: the fixture pins `checked_reports=1` and `status_lines=1` with the same report name in both places, so a fix that prefers the capture or sums the two is rejected.

5. The fixture is satisfiable with three behaviour changes and nothing else (green arm 7/7), so D1-D7 is not an always-red contract, and the control emitter is rejected on six of seven cases (D1, D2, D3, D5, D6, D7) rather than on one lucky assertion.

6. Both D6 hardening worlds are load-bearing and neither adds a case: dropping the round binding reddens only `mapped-missing`; resolving on the capture directory alone reddens only `mapped-dir`. Both are strictness inside D6's frozen words, not a new case id and not a predicate change.

7. The gate pins its parse-snapshot directories to a hardcoded `/var/tmp`, not `$TMPDIR`: `tools/souji-landing-gate.py:1022` `snapdir = tempfile.mkdtemp(prefix="souji-landing-gate-", dir="/var/tmp")` and `:1339` (selftest variant, same literal). This is the tool's own behaviour, inherited unchanged by the fixture; it is a residual deviation from the operator scratch directive and is the L1's call, since the file is being touched for C2 anyway.

8. `reports=86` does not discriminate tree-read from disk-read of the live wave dir: at base both `census/round-29/waves/**.md` and `.ufo/waves/round-29/**.md` are 86. An implementation that stats the working tree instead of the REV tree would hit the same number today and drift silently later; the fixture itself commits its `.ufo/waves` reports into the synthetic tree, so it is satisfied by either reading.

9. My deliverable is a copy under the wave dir, not the frozen path: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/deliver-r30-landing-gate-discovery.py` must land byte-identically at `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r30-landing-gate-discovery.py` (sha256 `e83033...66271`). `tests/fixtures/` currently holds no `r30-*` file: `git -C <lane> ls-tree -r --name-only HEAD tests/fixtures/ | grep r30` -> no output.

10. Sibling state observed, not mine: `git -C <lane> status --porcelain` shows `?? corpus/lessons/round-30.md`, untracked before my first command and untouched by me.

11. The wave-1 candidate gate (`.ufo/waves/round-30/w1/deliver-souji-landing-gate.py`, sha256 `ba37e6bf...cd9056`) already satisfies the frozen fixture 7/7 and keeps `SELFTEST pass=65 fail=0`, so the fixture and the candidate agree before integration; the candidate is not mine and I neither edited nor extended it. Absent from that file's own diff: any reference to `r30-landing-gate-discovery` (`grep -n r30-landing-gate-discovery deliver-souji-landing-gate.diff` -> no rows), so the fixture must be installed separately by the L1.

## Attack log

1. ATTACK — D6 was gameable by a capture-directory-only resolver before hardening: with only `mapped` and `mapped-missing`, an implementation that tests `census/round-<n>/waves` as a directory passed D6 while mis-resolving any pointer into an existing capture dir. Fixed inside D6's frozen statement by the `mapped-dir` world (capture dir exists, pointed-at file does not, must be LG-DANGLING-PTR); proven by the directory-only arm. No case id added, no target moved.

2. ATTACK — the counter's `reports=86` is blind to whether the gate reads the REV tree or the working tree for the live wave dir (both 86 today, Finding 8). Not a false-green for the frozen target, but it cannot detect a discovery implemented over the filesystem.

3. ATTACK — D2 is the only case pinning could-not-evaluate-on-absence, so an implementation that raises EvalError unconditionally passes D2 alone; it is caught by D1 (`exit=2` rejected) and D7 (`checked_reports=1` rejected). Recorded so a later wave does not read D2-pass as discovery evidence.

4. ATTACK — the fixture asserts `findings=0` in D1's and D6's clean worlds, so an implementation that adds any new unconditional finding class to an otherwise clean synthetic repo reddens D1/D6. That is deliberate (a discovery fix must not manufacture findings) but it is the most likely source of a false red if the L1's fix adds an unrelated check.

## Deliveries

1. `.ufo/waves/round-30/w1/deliver-r30-landing-gate-discovery.py` — sha256 `e830339332aa6ae1b1f614e33445327b68f47d0904428a04d6d812e394c66271`, 554 lines; frozen-path target `tests/fixtures/r30-landing-gate-discovery.py`; `--tool PATH`, synthetic repos under `$TMPDIR` only, `CASE D<k> PASS|FAIL <detail>` lines, `CONTROL` line, last line `cases=N pass=M control=...`, exit 0 iff 7/7 and control rejected.
2. `.ufo/waves/round-30/w1/deliver-c2-fixture-red-before.txt` — base-tool run output, `cases=7 pass=3 control=FALSE-GREEN-REJECTED`, exit 1.
3. `.ufo/waves/round-30/w1/receipt-c2-fixture-arms.txt` — green, loose-mapper and directory-only arm outputs plus the two guard refusals.
4. `.ufo/waves/round-30/w1/receipt-c2-fixture-candidate.txt` — the same fixture against the sibling candidate gate (7/7) and that candidate's `--selftest` line; read-only cross-check, the candidate is not my file.
