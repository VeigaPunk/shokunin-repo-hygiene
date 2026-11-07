# MutC3Tool — mutation test of the C3 pre-report gate (souji round-27 w1)

## Status
STATUS: PASS — all four assigned mutants built from pristine bytes and run through the C3 fixture; baseline green; (a), (c), (d) killed; (b) survived as a coverage finding (contract unchanged); lane bytes byte-identical before/after; scratch removed.

## Evidence

Target under test (lane drafts; never written by this seat):
- `.ufo/waves/round-27/w1/souji-pre-report-gate.sh` sha256 `a0082bca1c926de12b5fad9326b17b83340b314cc05088acc1834c25a51cf04b` (143 lines)
- `.ufo/waves/round-27/w1/r27-pre-report-gate.sh` sha256 `92c4be6ed0e1c46ef4869ab675a131954eee5ead79622a3dc536337bb79bc07e` (226 lines)

Method: copies under `/var/tmp/souji-r27-MutC3Tool/`, cp-verified identical hashes to the lane drafts. The fixture hardcodes the sibling's scratch root, so the fixture copy differs from pristine by exactly one line — `WORLD_ROOT=/var/tmp/souji-r27-MutC3Tool/worlds` (hard bound: this seat's scratch only); case assertions and control logic untouched. Per-run tool selection via `SOUJI_PRE_REPORT_GATE` (no harness mutation per run). Detector: `SOUJI_PRE_REPORT_GATE=<variant> SOUJI_LANE_ROOT=/home/vgpnk/Projects/shokunin/souji-shokunin bash harness.sh`; verdict = exit code + final line. bash 5.3.20, git 2.56.0. No tools installed (none needed); no pacman transactions.

Baseline (pristine gate): `cases=4 pass=4 control=FALSE-GREEN-REJECTED`, rc 0. Detector valid; every mutant verdict below is meaningful.

| # | mutant (smallest behavior-bearing point) | verdict | observed output |
|---|---|---|---|
| a | gate `check()` (souji-pre-report-gate.sh:71) rewritten to always print `check-<name>=PASS`, `fail` never set, exit 0 | KILLED, harness rc 1 | cases 2/3/4: `FAIL rc=0 want=1`, `check-tip=PASS want=FAIL`, `check-shonen=PASS want=FAIL`, `check-clean=PASS want=FAIL`, `fail-check-count=0 want=1`; control: `FAIL control world-not-red rc=0 clean=PASS`; no `cases=` line |
| b | gate line 21 `set -u` deleted | SURVIVED, harness rc 0 | output identical to baseline: `cases=4 pass=4 control=FALSE-GREEN-REJECTED` |
| c | gate line 82 extraction `awk 'NR==1{print $1; exit}'` → `awk 'NR==1{print; exit}'` — comparison now receives the raw ls-remote line incl. trailing whitespace/tab/refname | KILLED, harness rc 1 | case1 `detail-tip: local=d5be8924…c4 remote=d5be8924…c4<TAB>refs/heads/master` — true tips equal, bytes unequal → `case=1 clean-pass FAIL check-tip=FAIL want=PASS`, `rc=1 want=0` |
| c-rob | no mutation: pristine gate + PATH shim (`/usr/bin/git` wrapper appending three spaces + CR to every `ls-remote` output line) | GREEN, harness rc 0 | `cases=4 pass=4 control=FALSE-GREEN-REJECTED` — pristine gate tolerates trailing whitespace + CR |
| c-mut+ws | mutant c + same whitespace shim | KILLED, harness rc 1 | case1 `remote=…refs/heads/master   ` (trailing spaces in detail) → tip FAIL despite equal true tip |
| d | gate check #2 block (`if [ -s "$report" ]` … `check report PASS/FAIL`, lines 90-94) deleted | KILLED, harness rc 1 | case1 `case=1 clean-pass FAIL check-report=missing want=PASS`; cases 2-4 and control still PASS |

Answer to (c): the comparison itself does NOT normalize — `[ "$local_tip" = "$remote_tip" ]` (souji-pre-report-gate.sh:83) is byte-exact, so whitespace reaching it flips a true-equal tip to FAIL (killed as a false-red). The pristine gate is whitespace-robust only because `awk` field extraction `$1` splits on spaces/tabs and strips leading/trailing whitespace, so trailing spaces or a CR in real `git ls-remote` output never reach the comparison (c-rob green). The mutant dies with or without injected whitespace.

Restoration: lane drafts re-hashed after all runs — `a0082bca…` and `92c4be6e…`, identical to pre-run values. This seat wrote nothing in the lane except this report. Scratch `/var/tmp/souji-r27-MutC3Tool/` removed (verified absent). No personal git repo was needed in scratch (the fixture builds its own hermetic worlds), so no `rev-parse --show-toplevel` check applies.

## Findings
1. [coverage] `r27-pre-report-gate.sh:35` / gate `souji-pre-report-gate.sh:21` — deleting the gate's `set -u` is invisible to all four cases and the control: every case supplies all flags and the gate pre-initializes `lane= branch= report= prereg=`, so no exercised input path reads an unset variable. The harness cannot detect loss of unset-variable hardening; a future regression turning an unset-variable abort into silent behavior would pass the selftest. Coverage gap, not a counter failure — the frozen counter still holds for the pristine gate.
2. [coverage] The fixture has no case whose report file is missing or empty; mutant (d) is caught only by case1's positive assertion loop (`r27-pre-report-gate.sh:154`, expects `check-report=PASS`), never by a red world. If that loop ever dropped `report`, a gate with the report-exists check removed would go green.
3. [strength] The FALSE-GREEN control is non-vacuous: with mutant (a) installed as the tool, the control's independent red-truth proof (`r27-pre-report-gate.sh:205`) fires first — `FAIL control world-not-red rc=0 clean=PASS` — and cases 2-4 fail independently. An always-pass gate cannot produce the frozen success line, so the counter's `control=FALSE-GREEN-REJECTED` is a real rejection, not a tautology.
4. [strength] Tip-equality robustness lives in extraction, not comparison: trailing whitespace/CRLF in `git ls-remote` output is normalized by the `awk '$1'` field (gate line 82); the equality test itself is strict byte equality. No whitespace-boundary mutation survives without also breaking case1, which the fixture catches.

## Attack log
- A1 — assigned (a) always-PASS gate: KILLED (rc 1; cases 2-4 + `world-not-red` control). Matches the frozen kill rule: "the false-green passing fails C3".
- A2 — assigned (b) `set -u` removal: SURVIVED green. Recorded as coverage finding 1; no contract change proposed.
- A3 — assigned (c) trailing-whitespace comparison: comparison is byte-exact (no normalization); raw-line mutant KILLED via case1 false-red; pristine gate proven whitespace-robust by the shim probe (c-rob green).
- A4 — assigned (d) report-exists check omitted: KILLED via case1's positive assertion; coverage note in finding 2.
- A5 — self-incident, discarded: the first mutant batch ran four harness copies CONCURRENTLY against the single shared relocated `WORLD_ROOT`; their `mkworld`/EXIT-cleanup `rm -rf` raced (case2 world-setup FATAL, rc 2 on all four). Results invalid and discarded; all reported runs are strictly sequential. No lane impact.
- A6 — environment delta: one-line `WORLD_ROOT` relocation in the fixture copy (scratch-ownership bound); baseline re-proven green after relocation, so harness semantics unchanged.

Quotes (bytes opened this run; no pipe characters):
- `.ufo/waves/round-27/preregistration.txt:9`: "the selftest runs 4 isolated `/var/tmp` cases including a FALSE-GREEN always-pass control that MUST be rejected"
- `.ufo/waves/round-27/preregistration.txt:9`: "`bash tests/fixtures/r27-pre-report-gate.sh` → `cases=4 pass=4 control=FALSE-GREEN-REJECTED` rc 0"
- `.ufo/waves/round-27/w1/r27-pre-report-gate.sh:205`: "FAIL control world-not-red rc=%s clean=%s"
- `.ufo/waves/round-27/w1/souji-pre-report-gate.sh:82`: "awk 'NR==1{print $1; exit}'"
