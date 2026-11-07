# MutLessonTick — R27-M1 mistakes-row plan mutation test (souji round 27, w1)

## Status

STATUS: PASS — the R27-M1 fix (C3 pre-report gate) is shown able to fail: red-before runs fail exactly check `prereg` (preregistration file missing) and check `shonen` (`## SHONEN` heading missing), rc 1; restoring each defect's bytes alone flips rc to 0; a gate mutant with those two checks disabled lets both red worlds pass, proving the checks are the only verdict delta; the lesson row's evidence pointer (watchdog.log:1377) resolves.

## Evidence

Revision: lane HEAD read-only `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `e78ac7c4837b81b634db4a927605a751a7f006ba` (base; branch `master`). Gate under test: `.ufo/waves/round-27/w1/souji-pre-report-gate.sh` (not yet at `tools/` in this worktree), sha256 `a0082bca1c926de12b5fad9326b17b83340b314cc05088acc1834c25a51cf04b`, copied byte-identical into scratch before all runs and unchanged after.

Worlds (each: own `git init --bare` origin + `git init` lane on `master`, committed, pushed; `git rev-parse --show-toplevel` verified equal to the world lane dir before first commit; hermetic env `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0`):

- pristine: report.md with `## SHONEN` + prereg.txt present (sha256 report `97a33280…f3814bd`, prereg `b420f1e0…9508c6816`).
- worldA: pristine minus `prereg.txt` (only tracked-file delta: `diff` of `git ls-files` → `1d0 < prereg.txt`; report bytes identical to pristine).
- worldB: pristine report minus the single line `## SHONEN` (`diff` → `2d1 < ## SHONEN`; all else identical).
- worldA-green / worldB-green: same worlds with the defect's bytes restored; content hashes byte-identical to pristine.

Command: `bash /var/tmp/souji-r27-MutLessonTick/run-gate.sh` → `bash $D/gate.sh --lane <world>/lane --branch master --report <world>/lane/report.md --prereg <world>/lane/prereg.txt`. Output excerpts:

- pristine → `check-tip/report/shonen/clean/prereg=PASS`, rc 0 (baseline green; detector not vacuously red).
- worldA → `check-prereg=FAIL` + stderr `detail-prereg: missing: /var/tmp/souji-r27-MutLessonTick/worldA/lane/prereg.txt`; other four checks PASS; rc 1.
- worldB → `check-shonen=FAIL` + stderr `detail-shonen: found 0 '^## SHONEN' headings (want exactly 1)`; other four checks PASS; rc 1.
- worldA-green, worldB-green → all five checks PASS, rc 0.
- Detector sha256 after all runs: `a0082bca…a51cf04b` (unchanged).

Only-delta probe: `bash /var/tmp/souji-r27-MutLessonTick/run-gate-mutant.sh` — scratch gate copy `gate-nochecks.sh` (sha256 `8b0409fd…9793f9f87d4`) with the `shonen` and `prereg` check bodies replaced by SKIP lines (edits at its lines 97 and 127); on pristine, worldA and worldB it prints `check-shonen=SKIP`, `check-prereg=SKIP`, rc 0 everywhere — both red worlds pass once the two checks are removed.

Evidence pointer: `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log:1377` (read-only) = `2026-10-25T14:46:45-03:00 lane-dead-no-report souji round=27; retry same round (hyaku-inline attempt=1: L1 misread inline-spawn handoff (expected orchestrator to supply claims/ready), declared blocked, refused resume; no lane writes)` — matches the R27-M1 row in `.ufo/waves/round-27/w1/round-27.md` (Mistakes section).

## Findings

1. `.ufo/waves/round-27/w1/souji-pre-report-gate.sh` (check `prereg`, lines ~129-139 of the delivered draft): on a workspace whose preregistration file is missing — and only that delta — the gate fails `check-prereg` with `missing: <path>` and exits 1. Red-before demonstrated; mutant KILLED.
2. Same file (check `shonen`, lines ~96-102): on a workspace whose report lacks the `## SHONEN` heading — and only that delta — the gate fails `check-shonen` with `found 0 '^## SHONEN' headings (want exactly 1)` and exits 1. Red-before demonstrated; mutant KILLED.
3. Only-delta confirmed twice: (a) red↔green worlds differ byte-wise only in the targeted element (report `97a33280…`, prereg `b420f1e0…`); (b) with the two checks disabled in a scratch gate copy, red worlds pass rc 0 — the checks are the load-bearing, sufficient delta; without them the R27-M1 defect classes are invisible (survivor → coverage necessity of the checks).
4. `.ufo/waves/round-27/w1/round-27.md` (Mistakes, R27-M1) plus `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log:1377`: pointer resolves; quoted clause "L1 misread inline-spawn handoff (expected orchestrator to supply claims/ready), declared blocked, refused resume" matches log bytes verbatim. [INFERENCE] The row's fix claim is supported for the demonstrated edge classes (missing prereg/heading block report acceptance); the gate's `prereg` check verifies file presence, not handoff comprehension — the row's wording ("prereg/handoff readiness check") is broader than what the check can prove.
5. Harness note (no gate defect): v1 green worlds were built with `cp -a`, which copied the lane's `origin` URL, so a green push desynced the red world's bare remote and produced a spurious `check-tip=FAIL`; rebuilt with `remote set-url origin` per world. Incidental positive: the gate rejects relative `--lane/--report` (rc 2 usage) via its `is_abs` guard.

## Attack log

- Attack (mutation): workspace mutant worldA = pristine minus preregistration file. Expected detector: `check-prereg=FAIL`, rc 1. Output: `check-prereg=FAIL` / `detail-prereg: missing: /var/tmp/souji-r27-MutLessonTick/worldA/lane/prereg.txt`, rc 1, no other check failed. Verdict: KILLED.
- Attack (mutation): workspace mutant worldB = pristine report minus the `## SHONEN` line. Expected detector: `check-shonen=FAIL`, rc 1. Output: `check-shonen=FAIL` / `detail-shonen: found 0 '^## SHONEN' headings (want exactly 1)`, rc 1, no other check failed. Verdict: KILLED.
- Attack (mutation, gate-side): scratch gate copy with `shonen`+`prereg` checks reduced to SKIP, run on both red worlds. Expected: rc 0 if and only if those checks are the only verdict delta. Output: `check-shonen=SKIP`, `check-prereg=SKIP`, rc 0 on worldA and worldB. Verdict: SURVIVED (coverage finding: the two checks are necessary for red; no contract change proposed).
- Restoration: nothing in the lane repo or the fleet tree was written; all mutants lived in `/var/tmp/souji-r27-MutLessonTick/` (scratch removed after this report). Restored arms worldA-green/worldB-green run green (rc 0) with content hashes identical to pristine; pristine gate bytes hashed identical before and after every run (`a0082bca…a51cf04b`). No tools installed (none needed); no lane Python executed.

Seat: MutLessonTick (mutation-tester, leaf — no subagents). Preregistration read first; C3 kill rule respected (no case faked; false-green control logic untouched).
