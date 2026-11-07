# ExecFixtureC3Tests — C3 selftest harness (souji round 27, w1)

## Status
STATUS: PASS — drafted `r27-pre-report-gate.sh` (L1 installs as `tests/fixtures/r27-pre-report-gate.sh`); exercised with a conformant reference gate: final line `cases=4 pass=4 control=FALSE-GREEN-REJECTED`, rc 0, byte-identical across two runs; always-pass and always-fail stub gates both rejected (rc 1, no frozen final line). Lane HEAD untouched at `e78ac7c`.

## Evidence
Deliverable: `.ufo/waves/round-27/w1/r27-pre-report-gate.sh` (7899 B draft; `bash -n` clean). It builds five isolated worlds under `/var/tmp/souji-r27-ExecFixtureC3Tests` — each `git init -b master` repo with a local bare remote (`remote add origin <abs>/remote.git`), committed report + prereg, `rev-parse --show-toplevel` verified before first commit — and runs the gate under test with the frozen CLI (`--lane --branch --report --prereg`).

- Reference gate (conformant to frozen interface, scratch copy): `SOUJI_PRE_REPORT_GATE=/var/tmp/souji-r27-ExecFixtureC3Tests/ref-gate.sh bash .ufo/waves/round-27/w1/r27-pre-report-gate.sh` →
  ```
  check-tip=PASS check-report=PASS check-shonen=PASS check-clean=PASS check-prereg=PASS
  case=1 clean-pass PASS
  case=2 remote-mismatch PASS
  case=3 missing-SHONEN PASS
  case=4 dirty-tree PASS
  control FALSE-GREEN-REJECTED
  cases=4 pass=4 control=FALSE-GREEN-REJECTED
  ```
  rc 0.
- Determinism: run twice, `diff run1.txt run2.txt` empty, both rc 0.
- Installed-layout discovery: copied harness into scratch `<R>/tests/fixtures/` + ref gate into `<R>/tools/souji-pre-report-gate.sh`, invoked from `/tmp` → same final line, rc 0 (lan root auto-resolved two dirs above the fixture).
- Mutant A (always-pass stub, identical to control stub): rc 1; `case=2/3/4 … FAIL`; `FAIL control world-not-red rc=0 clean=PASS`; no frozen final line.
- Mutant B (always exit 1, prints no checks): rc 1; every case FAIL (`check-*=missing`); `FAIL control world-not-red rc=1`.
- Lane state: `git rev-parse HEAD` = `e78ac7c4837b81b634db4a927605a751a7f006ba`; only `.ufo/waves/round-27/` (w1 drafts) untracked. No tools installed (git 2.56.0, bash only).

## Findings
1. Case assertions are non-vacuous: each case asserts rc **and** the exact failing check(s) (`tip`/`shonen`/`clean`) **and** that the count of FAIL check-lines equals the expected set; case 1 asserts all five checks PASS and rc 0. Mutants A/B are rejected (rc 1, no final line).
2. FALSE-GREEN control exercises the stub path: the control world's truth is first proven red with the real gate (rc 1, `check-clean=FAIL`); only then is the always-pass stub run; a green result there is detected and rejected, printing `control=FALSE-GREEN-REJECTED`.
3. Tool lookup: `SOUJI_PRE_REPORT_GATE` override; else `tests/fixtures/../..` → `tools/souji-pre-report-gate.sh` when installed, else `$SOUJI_LANE_ROOT`/`$PWD`. Works as draft and installed.
4. Hermetic/cleaned: fixed scratch root, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`, `HOME` under scratch; EXIT trap removes all five world dirs (verified: no `case*/control` residue after runs); no lane writes, no network, no wall-clock dependence.
5. Development fixes: `write_prereg` creates the `.ufo/waves/round-27/` parent dir; gate rc captured immediately after command substitution (no `|| true`), which had masked rc=0 in the first run.

## Sources
- `preregistration.txt:9` (frozen C3 contract): "report exists and carries exactly one `^## SHONEN` heading".
- `w1-dispatch.json:621` (frozen gate CLI, ExecFixtureC3Gate): "Checks (each prints `check-<name>=PASS|FAIL|SKIP`)" and `1lane <abs-lane> --branch <branch> --report <abs-report> [--prereg <abs-file>]`.

## Attack log
None — C3 is a build item. Observation (not an amendment): the control's rejection depends on the frozen check names/exit codes; any future gate that changes them fails these assertions loudly (Mutant A/B behavior) rather than silently passing.
