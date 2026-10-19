# S16 — prospective scorecard rubric

Status: **DRAFT, not an adopted score change**. Rubric ID: `souji-r9-s16-v1`.
Axes: **calibration, operability, coverage**. The parent alone integrates the
scorecard and adjudicates round admission.

## Measurement boundary

Baseline captured at `2026-10-18T23:50:27Z`, lane commit
`14916c075c7de4b905d92c472e6312026d12d44a`:

- `tools/souji-verify.sh`: `a91049c96e5fba7c3db83df288a261717156c3834532e54d712ed0c555e350c4`
- `tools/souji-vault-verify.sh`: `53f92421b254426c7e4882c1da9cfaa444bddde7ff90ee30afcd48fa229328b1`
- `tools/souji-quarantine.sh`: `5780ad751aa49d1bb587690154cab98ab6aa71b4def518673c2f383301c51c4f`
- `tools/souji-census.sh`: `11bf9cdf8d4f75415b18e046aef0e96215b983f0d5b3ff7842301ff6ac65d381`
- `SCORECARD.md`: `7c0039a528a2a760622ce9d9b69427e2ee695a993b7acca72968fc048cfd2378`

These are capture-time identities, not promises about concurrent S17/S18 edits.
Grounding: fleet `AXES.md:9-16,25-55,75-83`; lane `AGENTS.md:3-18`;
`PROVINCE.md:5-36`; tool output/stage contracts in their headers.

All adversarial executions must use new fixture repos under
`mktemp -d -p /var/tmp`. Never fetch/push/commit/branch on live repos, read
secret-shaped contents, touch `.ufo/state` or `.ufo/watchdog.log`, or launch a
GUI. Missing prerequisites produce UNKNOWN, never simulated success. No new
live mutation, remote creation, or operator approval is authorized by this rubric.

## Evidence, outcomes, and counting

Freeze a manifest **before scoring**: rubric ID, case IDs, tool hashes, expected
outcomes, affected surface/gate, fixture recipe, and independently established
oracle. Every completed case records its exact command and cwd, relevant env,
stdout, stderr, exit status, and before/after content/index/ref assertions.
Pin the installed wrapper and its actual child engine; a passing uninstalled
candidate does not certify the installed tool. Recreate fixtures for each run.

- **PASS:** every obligation in the gate is demonstrated. A negative control
  correctly refused is PASS; `NOT-SAFE` with exit 0 is normal verifier behavior.
- **FAIL:** an obligation is demonstrably unmet. This is a rubric failure,
  **not automatically a tool defect**. For example, a missing score formula
  fails calibration without implying any unsafe file removal.
- **UNKNOWN:** not executed, blocked, stale identity, incomplete transcript,
  or inconclusive. Mark an unconfirmed alleged defect **NOT-REPRODUCED**.
  A refusal of a positive control does not establish a defect or capability;
  record the capability as unproved, rather than forcing authorization.

A confirmed tool defect requires a fresh, self-contained fixture command
sequence, independent unsafe-state assertions, actual unsafe authorization or
mutation, and the exact affected tool identity. Source inspection, peer votes,
old logs, and wrapper agreement alone cannot confirm one. An unexplained
nonzero exit or conservative refusal is not a false SAFE/DELETE.

Deduplicate defects by reproducible root cause plus affected tool/entry point;
keep per-case occurrences separately. Count documentary contradictions as
unique `(subject, field, measurement boundary)` disagreements. Historical
changes are not contradictions unless presented as simultaneously current.
Report at least: case totals by outcome; unique confirmed defects; unsafe
SAFE/VERIFIED cases; unsafe DELETE cases; documentary contradictions; and
NOT-REPRODUCED allegations. All totals must reconcile to enumerated IDs.

Differential checks compare the same fixture state and pinned identities.
Normalize only serialization, path echo, and documented vocabulary/precedence:
`SAFE`/`VERIFIED` authorize; `NOT-SAFE`/`NOT-VERIFIED` refuse. Compare receipt
classes when both authorize; preserve reason differences as observations.
Quarantine adds preflight/second-check gates, so its refusal after a verifier's
SAFE is not inherently a contradiction. Agreement can still be jointly wrong;
adjudicate disagreements against the independent oracle, not majority vote.

## Numeric mapping and safety veto

There are exactly ten fixed, equally weighted gates per axis below. A compound
gate earns one point only when **all** its listed obligations pass; duplicates,
extra seats, repeated runs, and extra easy cases earn no additional points.
Within a gate, any evidenced unmet obligation makes it FAIL; otherwise any
unverified obligation makes it UNKNOWN; only all-PASS obligations make it PASS.

For a fully evaluated axis: `score = number of PASS gates` (integer 0–10).
If any gate is UNKNOWN: publish **N/A — incomplete**, its PASS/FAIL/UNKNOWN
counts, and optionally the bounds `[PASS, PASS + UNKNOWN]`, not a point score.
A known failure is not silently removed from the denominator. New scope or
changed weights require a new rubric ID and a remeasured baseline. Do not
compare an old informal score against this new formula as an improvement.

**Safety is non-compensable.** Any unresolved, freshly confirmed false
SAFE/VERIFIED, unsafe DELETE, protected-surface access, or out-of-scope mutation
blocks operational certification regardless of the three numeric totals.
Undetermined safety blocks certification as UNVERIFIED, not as a confirmed
defect. A high coverage score or many correct refusals cannot average this away.
Audit discoveries may improve calibration while exposing a pre-existing tool
deficit; distinguish disclosure from a regression introduced by the candidate.

## Calibration gates — K1–K10

- **K1 Identity:** every scored observation names commit, measurement time,
  rubric version, and hashes of the exact tool/child-engine bytes exercised.
- **K2 Replayability:** every completed case has a fresh fixture recipe,
  runnable command/cwd/env, stdout/stderr/status, and expected/actual result.
- **K3 Independent oracle:** positive preservation and negative unsafe-state
  expectations are established independently of tool output or peer agreement.
- **K4 Defect discipline:** every confirmed defect freshly reproduces;
  everything else is NOT-REPRODUCED or explicitly untested, never promoted by vote.
- **K5 Honest counts:** deduplicated defects, per-case occurrences,
  contradictions, and outcome totals reconcile exactly to their enumerated IDs.
- **K6 Repair closure:** each claimed fix has an unsafe before-case, a fresh
  refusing after-case, and a still-working legitimate control on the final bytes.
  If no fixes are claimed, record that fact and the empty fix inventory explicitly.
- **K7 Gaps visible:** every open issue, unknown, external gate, and dissent
  has an explicit disposition; historical closure is not reused as current proof.
- **K8 Card concordance:** axis rows, saturation/lowest-axis prose, last-change
  rounds, and the versioned numeric calculation agree at the same boundary.
- **K9 Executable evidence:** every current counting command runs from its
  declared cwd and preserves upstream errors; failed pipelines cannot become 0s.
- **K10 Provenance:** capability claims cite actual demonstrations and distinguish
  installed/current from historical hashes, parent completion from round admission,
  fixture proof from live exercise, and closed history from future plans.

## Operability gates — O1–O10

- **O1 Entry points:** the four installed scripts parse, required dependencies
  exist, help/usage and invalid-argument statuses match their contracts.
- **O2 Output contracts:** real calls produce parseable JSON/TSV, exact record
  cardinality and ordering, consistent verdict/status vocabulary, and either
  unambiguous handling or refusal of delimiter/control-character paths.
- **O3 Receipt engine:** end-to-end verifier calls demonstrate all supported
  receipt classes and no-receipt refusal with independent preservation assertions.
- **O4 Vault verification:** actual source/vault checks and `--fallback` work;
  invalid rows/mismatches refuse; the source, vault, and ledger remain unchanged;
  no GUI or advisory CLI claim substitutes for byte evidence.
- **O5 Dry run:** quarantine computes real preflight verdicts but does not move,
  sleep through the hold, alter content/index, or create quarantine directories.
- **O6 Successful lifecycle:** real fixture executions for pushed,
  moved-to-obsidian, and stale show staging → configured hold → second check →
  deletion only within quarantine, correct tracked/untracked handling, and a
  surviving independent preservation basis. Metadata-only cases are skipped.
- **O7 Preflight refusal:** no receipt, dirty/unpushed target, authorization-pin
  mismatch, collision, or out-of-scope path leaves originals/index unchanged
  without staging; exit/result/summary agree.
- **O8 Failed second check:** changed bytes/mtime/receipt/ref/vault or an engine
  error cannot delete; the staged object remains recoverable and the failure is
  reported. A successful first check alone is never deletion authority.
- **O9 Census:** repeated unchanged fixtures are byte-stable; independently
  checked fields agree; identical comparison is header-only/exit 0, real changes
  produce correct deltas/exit 3, and invalid input cannot masquerade as no change.
- **O10 Repeatable delivery:** the project's applicable standard tests and the
  registered independent end-to-end cases pass on the delivered identities;
  commands are bounded, headless, fixture-isolated, and disclose environmental
  blockers. Syntax/import/selftest-only evidence cannot replace a real flow.

## Coverage gates — C1–C10

Each family requires explicit decision rules, an enumerated case manifest,
independent expected outcomes, and fresh passing positive/negative controls
where authorization is supported. Refusal-only families instead require
boundary controls. An explored but unsafe/unproved family is not fully governed.

- **C1 Pushed artifacts:** remote-default resolution, missing/ambiguous remote
  refs, introducing commit ancestry, later unpushed edits, dirty/index/HEAD
  divergence, and detached/named-branch contexts.
- **C2 Vault files:** complete and incomplete rows, both hash mismatches,
  missing endpoints, relative/duplicate rows, and self/alias references whose
  alleged preservation copy would not independently survive removal.
- **C3 Directories:** deterministic digest scope, unreadable/special entries,
  nested/protected content, symlinks, and a vault inside the removal scope.
- **C4 Staleness:** every supported scratch family, age boundary and recent
  content, real references including hidden/ignored files, intended evidence
  exclusions, and unreadable/erroring sweeps that must not mean zero references.
- **C5 Worktree metadata:** absent/present, detached/named, unique/unpushed,
  clean/dirty, locked registrations, and owner/ref-query failure.
- **C6 Repository roots:** explicit kind handling and independent preservation,
  dirty/unpushed/missing-remote states, linked/bare/nested layouts, and refusal
  to treat a clean root as an ordinary discardable artifact.
- **C7 Hostile paths:** spaces, tabs/newlines/CR, option-like/glob characters,
  symlinked ancestors, traversal, outside-repo aliases, and containment collisions.
- **C8 Protected surfaces:** secret-shaped paths and operator/driver boundaries
  refused before content access; headless and read-only checks. Never read real
  secrets or touch forbidden runtime surfaces merely to test this gate.
- **C9 Quarantine:** list/positional modes, receipt pinning, all supported
  classes and tracked/untracked transitions, dry run, hold-time tamper, second-
  check errors, index state, collisions/concurrency, and recovery after abort.
- **C10 Census/compare:** eligible/root/hidden/gitfile repo enumeration,
  worktree/unpushed/dirty/scratch/mtime flags, no-remote and query-error states,
  stable sorting, schema/duplicate/malformed input, and added/removed/changed rows.

This fixed family count is an explicit coarse coverage model, not a claim that
ten tests or ten families exhaust every possible attack. Expanding the frontier
adds registered cases; it never deletes hard cases to improve the fraction.

## Before/after and admission

Remeasure baseline and candidate against the same rubric/manifest, with fresh
fixtures and identities. A measurable axis improvement needs at least one
FAIL/UNKNOWN → PASS backed by new proof; numeric increases require comparable,
fully evaluated scores. Preserve every previous PASS and registered safe
capability across **all three axes**. A regression or loss of proof cannot be
hidden by a net-positive total. If another seat changes the tool, rerun affected
cases against the integrated bytes before attributing a result to that delivery.

Per fleet `AXES.md:25-55`, admit only the declared 1–3 distinct-axis claims that
all verify with no axis harmed. Safety blocks operational claims as above;
unknown no-harm is not verified no-harm. Publishing this draft alone does not
verify hardening, complete the differential audit, authorize removal, or satisfy
the non-author review required for an exploratory claim.

## Fresh S16 observations and rubric verdicts

- **2 confirmed current numeric documentary contradictions:**
  `SCORECARD.md:14` calibration 7 versus `:45` calibration 6;
  `SCORECARD.md:15` operability 8 versus `:45` operability 7.
  Coverage is 8 in both. This is a current K8 failure, not two executable defects.
- **0 confirmed tool defects established by S16**; no adversarial execution
  finding is claimed. This does not mean the tools have zero defects.
- `bash -n` on the four installed scripts: PASS, exit 0. Rubric calculator and
  conservative-refusal checks below: **11/11 PASS**.
- No 30-gate manifest has been fully evaluated by this seat. Prospective scores:
  **calibration N/A, operability N/A, coverage N/A**. Historical table scores
  remain calibration 7 / operability 8 / coverage 8; no new mapping or scores
  have been applied. Operational/round certification is **UNVERIFIED** here.

Reproduce from the lane root; this command reads only the card and tool source
and does not exercise the live fleet. The Python block is also the reference
calculator. Its refusal classifier deliberately returns UNKNOWN for an unproved
positive capability, not a defect. Only independently reproduced unsafe behavior
sets the example's `unsafe_reproduced` flag.

```bash
for tool in tools/souji-verify.sh tools/souji-vault-verify.sh \
  tools/souji-quarantine.sh tools/souji-census.sh; do
  bash -n "$tool" || exit "$?"
done
```

```python
from pathlib import Path
import json
import re

VALID = {"PASS", "FAIL", "UNKNOWN"}


def score(checks):
    if len(checks) != 10 or set(checks) - VALID:
        raise ValueError("exactly ten PASS/FAIL/UNKNOWN cells required")
    return None if "UNKNOWN" in checks else checks.count("PASS")


def decision(expected, actual, unsafe_reproduced=False):
    if unsafe_reproduced:
        return "FAIL"
    if actual == "REFUSED":
        return "PASS" if expected == "REFUSED" else "UNKNOWN"
    return "PASS" if actual == expected else "UNKNOWN"


tests = 0
for cells, want in [
    (["PASS"] * 10, 10),
    (["PASS"] * 8 + ["FAIL"] * 2, 8),
    (["FAIL"] * 10, 0),
    (["UNKNOWN"] * 10, None),
    (["PASS"] * 8 + ["FAIL", "UNKNOWN"], None),
]:
    assert score(cells) == want
    tests += 1
for cells in (["PASS"] * 9, ["PASS"] * 9 + ["SKIP"]):
    try:
        score(cells)
    except ValueError:
        tests += 1
    else:
        raise AssertionError("malformed cells accepted")
for expected, actual, unsafe, want in [
    ("REFUSED", "REFUSED", False, "PASS"),
    ("SAFE", "REFUSED", False, "UNKNOWN"),
    ("REFUSED", "SAFE", True, "FAIL"),
    ("DELETED", "ABORTED", False, "UNKNOWN"),
]:
    assert decision(expected, actual, unsafe) == want
    tests += 1

s = Path("SCORECARD.md").read_text()
axes = {"coverage", "calibration", "operability"}
rows = {p[1].strip(): int(p[2].strip())
        for line in s.splitlines() if line.startswith("| ")
        for p in [line.split("|")]
        if len(p) > 3 and p[1].strip() in axes}
prose = {a.lower(): int(n) for a, n in re.findall(
    r"(coverage|calibration|operability)\s+(\d+)",
    s.split("## Saturation / stagnation", 1)[1], re.I)}
assert rows.keys() == prose.keys() == axes
contradictions = [{"axis": a, "axis_row": rows[a], "saturation_prose": prose[a]}
                  for a in sorted(axes) if rows[a] != prose[a]]
print(json.dumps({"rubric_selfchecks_passed": tests,
                  "numeric_contradictions": len(contradictions),
                  "details": contradictions}, sort_keys=True))
```

Observed output: `rubric_selfchecks_passed=11`, `numeric_contradictions=2`,
calibration `(axis_row=7, saturation_prose=6)`, operability `(8, 7)`.
