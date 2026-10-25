# CritC2Manifest — W2 audit: C2 cases 11/12 manifest assertions vs amendment 2 §3

Seat: `L1Souji25.CritC2Manifest` (leaf critic; read-only; no subagents; no lane writes beyond this report).
Scratch: `/var/tmp/souji-r25-CritC2Manifest/` (removed at finish). No tool installs.
Assignment: audit C2 cases 9–12 against amendment 2 and amendment 3; determine whether cases 11/12
actually assert manifest unchanged as amendment 2 says; test a tool that writes to the repo before
refusing. No predicate changes (frozen claim predicates untouched).

## Status

STATUS: PASS — attack executed; mismatch confirmed with file-line and observed-output evidence.

## The amendment promise (target of the audit)

`preregistration-amendment-2.txt:18-19` (verbatim):

> "Cases 11 and 12 freeze rc + stderr only in the prereg; the implementing fixture adds an unchanged-manifest condition to both, disclosed in the report."

## File-line evidence — cases 11/12 do NOT gate on the manifest

Integrated fixture `tests/fixtures/r24-size-census.py` (sha256 `9c8a512f94d5682efee725dc7ed7519c127fde6a775a038ec3292374970bd528`; identical to the W1 draft L1 integrated, `w1/ExecC2-2/r24-size-census.py`):

- Docstring `:9-10` (verbatim): "Case 9 requires the bare git dir's manifest unchanged; cases 10-12 report
  `manifest_changed` but do not gate on it (not in the frozen r25 C2 predicates)."
- `case_subdir` `:323`: `return code == 2 and named, describe_full(code, out, delta, stderr_must_name_repo=named)` — delta computed, never asserted.
- `case_partialclone_only` `:337`: `return code == 2 and partial, describe_full(code, out, delta, stderr_partial_clone=partial)` — delta computed, never asserted.
- Only case 9 gates on `not delta` (`case_bare_nonempty` `:300`), which matches amendment 2 §2 (manifest over the gitdir itself).

## Observed output — a tool that writes before refusing passes cases 10–12

Probe (in scratch): a mutant tool that writes a marker file into the gitdir/common dir, *then* refuses with the spec-exact diagnostics. Runs against the integrated fixture:

```
CASE 10 bare-empty PASS exit=1 counts=none manifest_changed=2 first=. stderr_git_failure=True stderr_no_default_references=True stdout_counts_line=False
CASE 11 subdir PASS exit=2 counts=none manifest_changed=2 first=. stderr_must_name_repo=True
CASE 12 partialClone-only PASS exit=2 counts=none manifest_changed=2 first=. stderr_partial_clone=True
CASE 9 bare-nonempty FAIL exit=1 counts=none manifest_changed=2 first=. invoked_from_bare=False
cases=12 pass=5 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
```

Green baseline (real tool, same fixture): `cases=12 pass=12` rc 0, cases 10–12 all `manifest_changed=0`
(identical to receipt `w1/ExecC2-receipts/c2-green.tsv`). The real tool does not write; the fixture's
predicates cannot observe a write on 10–12 even when one occurs.

## Findings

1. **Conformance defect (mismatch).** Amendment 2 §3 states the implementing fixture "adds an unchanged-manifest condition" to cases 11 and 12; the integrated fixture does not — it reports `manifest_changed` but never gates on it, and its own docstring (`:9-10`) says exactly that. This is not a frozen-predicate narrowing: the frozen C2 predicates for 11/12 (preregistration.txt:70-73) are rc + stderr only, and they are left intact. The defect is the amendment's stated fixture strengthening being unimplemented.
2. **Consequence demonstrated (strongest counterexample).** A tool that writes to the repo before refusing passes cases 10, 11 and 12 (`manifest_changed=2` on all three, still PASS). The no-write envelope (the F2 write-safety surface this claim covers) is unasserted on every refusal case; case 9 is the only manifest-gated case. A future real-tool regression that writes before refusing would be invisible to the counter.
3. **Consistency with W1 disclosures.** The W1 seats already recorded exactly this gap: `ExecC2.md:43` and `ExecC2-2/ExecC2.md:19` ("Cases 10–12 report manifest_changed but do not gate on it"), and `MutSizeCensus.md` finding 8 / `MutSizeCensus-s1.md` finding 7 flag the "internal inconsistency between amendment text and implementation". The integration carried the ungated fixture forward; the amendment record was never corrected.
4. **Amendment 3 scope.** Amendment 3 touches C1/C3; its only C2-relevant item (§5) is the regenerated base receipt. `census/round-25/records/c2-control-base.tsv` at tip shows `cases=8 pass=8` (fixture sha `373ef1f0…`, rc 0, rev a6d2d15) — matches amendment 3 §5; no C2 defect there. Red arms re-verified PASS by RevC2RedArm (1efe406 fails 11; 778747e fails 9/10), satisfying amendment 2 §1.

## Impacted axes

Operability (8) — C2 fixture/amendment fidelity; calibration (7) via counter rigor; no axis harmed by this audit.

## Smallest safe correction

- Least-change: append an append-only correction to the round record (e.g., an amendment note) stating cases 11/12 report but do not gate `manifest_changed`, aligning the record with implementation without touching frozen predicates.
- If the operator ratifies amendment 2 §3 as binding instead: add `and not delta` to `case_subdir` and `case_partialclone_only` (fixture-only change; frozen claim predicates unchanged), then re-run green, both red arms and the stub control to confirm no false rejection. Do not implement the gate silently mid-round — amendments are append-only and the gate is not in the frozen predicate.

## Attack log

- A1: read preregistration + amendments 1–3, integrated fixture bytes, W1 drafts and receipts.
- A2: ran integrated fixture vs real tool → 12/12 green; case 10–12 manifest_changed=0.
- A3: built write-then-refuse mutant in scratch; observed 10–12 PASS with manifest_changed=2; case 9 FAIL.
- A4: confirmed red-arm receipts (RevC2RedArm PASS) and regenerated base receipt (amendment 3 §5); no edits.
