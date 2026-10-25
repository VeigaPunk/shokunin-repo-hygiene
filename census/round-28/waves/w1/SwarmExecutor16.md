# SwarmExecutor16 — round 28 w1 report (pre-report gate demo)

## Status
STATUS: PASS — green and red pre-report-gate cases both behaved exactly as frozen: green → `check-tip=PASS check-report=PASS check-shonen=PASS check-clean=PASS check-prereg=PASS` rc 0; red (zero SHONEN headings) → `check-shonen=FAIL` rc 1. Run after the C3 cleanup landed and the L1 integrated: lane clean, local tip == origin, C3 artifacts present.

## Evidence
- Lane state at run time: `git status --porcelain=v1 --untracked-files=all` → 0 lines; `git rev-parse HEAD` → `765fe8bd602ac679d01e7a0790711485209ab8bd`; `git ls-remote origin refs/heads/master` → same SHA. C3 landed: `tools/souji-wave-evidence-capture.sh` and `tests/fixtures/r28-wave-evidence-capture.sh` present; `census/round-26/waves/manifest.sha256` (174637 B), `census/round-27/waves/manifest.sha256` (11036 B), `summary.tsv` both rounds; `.gitignore` at HEAD contains `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/`.
- Green case (temp report `/var/tmp/souji-r28-ExecC3GatePrep/report.md`, exactly one `## SHONEN` heading + 52 bytes):
  - Command: `bash tools/souji-pre-report-gate.sh --lane /home/vgpnk/Projects/shokunin/souji-shokunin --branch master --report /var/tmp/souji-r28-ExecC3GatePrep/report.md --prereg /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-28/records/preregistration.txt`
  - Output: `check-tip=PASS` / `check-report=PASS` / `check-shonen=PASS` / `check-clean=PASS` / `check-prereg=PASS` / `rc=0`
- Red case (temp report `/var/tmp/souji-r28-ExecC3GatePrep/report-no-shonen.md`, 28 bytes, zero `^## SHONEN` headings):
  - Same command with `--report /var/tmp/souji-r28-ExecC3GatePrep/report-no-shonen.md`
  - Output: `check-tip=PASS` / `check-report=PASS` / `check-shonen=FAIL` / `detail-shonen: found 0 headings, expected 1` (stderr) / `check-clean=PASS` / `check-prereg=PASS` / `rc=1`
- Gate script bytes: `sha256=a9d9f520b89396f679390c42fef58767d499c133a49921929de31dd284c94e49` for `tools/souji-pre-report-gate.sh` (HEAD blob `9f814366632ea0714061cff8671223c9ab684763`).
- No tool installs/updates this run; no lane writes outside `.ufo/waves/round-28/w1/`; scratch `/var/tmp/souji-r28-ExecC3GatePrep/` removed.

## Findings
1. **Frozen CLI matches committed gate exactly** (`tools/souji-pre-report-gate.sh`): flags `--lane/--branch/--report/--prereg`, absolute-path validation, fixed check order tip/report/shonen/clean/prereg, `check-<name>=PASS|FAIL` on stdout, human detail on stderr (`detail-shonen:`), exit 0 iff no FAIL, 1 on any FAIL.
2. **Green case fully green**: all five checks PASS, rc 0 — confirms tip sync (local == origin `765fe8bd`), report existence, exactly-one SHONEN heading, clean lane, and prereg presence at `census/round-28/records/preregistration.txt`.
3. **Red case fails only on shonen**: zero-heading report → `check-shonen=FAIL` with detail line, rc 1; all other checks remain PASS (tip/report/clean/prereg), isolating the shonen predicate. Lane stayed clean after both runs (gate exports `GIT_OPTIONAL_LOCKS=0`).
4. **Precondition verified**: the green run was executed only after the C3 cleanup landed (tool + fixture + r26/r27 manifests + gitignore) and the L1 integrated/pushed; before that the lane carried 327 porcelain entries (169 under `.ufo/waves/`), so check-clean would have been FAIL.

## Attack log
No attack item assigned to this seat; no counter or predicate contested.
