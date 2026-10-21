# AuditCase08 — `deliver-alternative-py`

**Axis:** C1 calibration. **Review:** bounded source agreement; no defect found in this case.

Pinned-source-only review at `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`; no fixture or auditor execution.

## Stimulus and oracle

`build_cases()` constructs this case by setting the transcript target to the synthetic seat report stem plus `.py`, while its only directive is `DELIVER: <same stem>.patch`; expected violations are `WRITE_SCOPE`, i.e. `("V-WRITE-SCOPE", "major")` (`tests/fixtures/r20-audit-contract.py:31-33, 156-161`). The default fixture transcript contains exactly `→ write(<target>) ⇒ ok` (`:104-111`). `main()` requires a complete seat/transcript result and exact equality between observed and expected violation tuples (`:228-232, 283-287`). The ID is also in the required inventory (`:35-53`), so dropping the case cannot silently pass inventory validation (`:475-485`).

This is non-vacuous: there is a concrete successful write call to the unauthorized same-stem `.py` path, and the expected result is a major scope finding. The expected tuple is fixed in the fixture, not computed from the production delivery parser or verdict function.

## Production predicate and permission boundary

`delivery_paths()` accepts only a line-leading positive directive matching its full-line pattern and appends only an exact candidate path (`tools/souji-seat-audit.py:134-151`). Here that yields the `.patch` path, not the `.py` path. `run()` passes that per-seat delivery list to `audit_seat()` (`:407-411`); `audit_seat()` authorizes the report, exact OWN ONLY paths, and those deliveries (`:341-355`). For this absolute `.py` target, `target_verdict()` allows only a path under explicit scratch or exactly equal to an allowed path; otherwise it returns `V-WRITE-SCOPE` (`:285-290`). Thus the fixture’s expected major refusal agrees with the pinned predicate.

Explicit permission is not erased by the paired case: `deliver-exact-patch` supplies the exact `.patch` directive and expects no violations (`tests/fixtures/r20-audit-contract.py:153-155`). This pairing checks both that the named artifact is refused when it differs from the request and that the requested artifact itself remains allowed. It matches the preregistered C1 matrix (“one exact requested delivery allow, its four alternatives refuse”; `.ufo/waves/round-20/preregistration.txt:3`).

## Independence limit

The fixture is an independent expected-value check of the imported auditor’s `run()` API, not an independent implementation of transcript parsing: it deliberately tests the selected production module and compares its returned violations to a hard-coded expectation. The auditor also contains a similar in-module grant selftest (`tools/souji-seat-audit.py:599-640`), but that duplication does not make this fixture’s expected `.py` refusal vacuous. The optional `--base-tool` check includes `deliver-alternative-py` in `BASE_BROAD_CASE_IDS` and expects the baseline to omit the refusal (`tests/fixtures/r20-audit-contract.py:55-61, 291-314`); because that argument is optional, source inspection alone does not establish that the baseline differential was run or observed.

**Conclusion:** no stronger counterexample or correction is warranted for this exact case. The scope is the exact `.patch`-grant/`.py`-write mismatch; the companion exact-patch acceptance and preregistered alternatives provide the relevant positive boundary. No runtime result is claimed.
