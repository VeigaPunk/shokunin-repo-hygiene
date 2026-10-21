# AuditCase14 — `incidental-delivery-mention`

**Axis:** C1 calibration (exact write authorization). **Disposition:** bounded source agreement; no blocking defect found. This is a source-only review of commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`; no fixture, auditor, or target code was executed.

## Counterexample and source trace

The relevant counterexample is a write to the exact same-stem `.patch` path that appears in prose but is not granted: the fixture creates `incidental` from the seat's report stem and expects `("V-WRITE-SCOPE", "major")` for the write, while the prompt says `Possible output path: <that path>; this mention grants nothing.` (`tests/fixtures/r20-audit-contract.py:32, 140-173`; case ID inventory at `:35-54`). This is not merely an out-of-scope path: it would be accepted by an overbroad predicate that treats an arbitrary path mention as a sibling-delivery grant.

It is non-vacuous in the fixture's source flow. `make_world` puts the prompt in the `Seat` spec item and writes the actual `→ write(<target>) ⇒ ok` transcript (`:80-112`); `run_case` checks that the expected seat exists and no transcript is missing (`:228-232`); the main case loop calls `module.run` and compares the exact observed violation tuple with the independently declared expected tuple (`:279-289`). The ID is also required by the exact case inventory (`:41`, `:475-485`).

Production behavior agrees with that expectation. `delivery_paths` derives only same-report-stem candidates and accepts a full line matching a positive, line-leading `DELIVER:` or `Write`/`Create`/`Deliver` directive; it skips fenced, indented, and quoted lines (`tools/souji-seat-audit.py:134-151`). The fixture's prose line matches none of those forms, so it adds no delivery. `run` passes that result to `audit_seat` (`:408-411`); the allowed set is the report, exact OWN ONLY paths, and parsed deliveries (`:341-344`). For this absolute target, `target_verdict` allows only an exact allowed path or an explicitly granted scratch descendant, otherwise returning `V-WRITE-SCOPE` (`:285-289`); the write-scope class becomes major (`:349-355`).

## Independence and permission preservation

The expected result is a literal oracle constant, not calculated from the production predicate. The fixture exercises the public `run()` path and validates complete seat/transcript coverage before comparing results. Its natural-language stimulus differs from the auditor's inline `incidental-not-grant` case (`tools/souji-seat-audit.py:599-626`): the reviewed case specifically uses “Possible output path” and a `.patch` target, so it can expose a regression that grants that phrasing while the inline `Inspect …json` example does not.

This negative case alone says nothing about preserving a legitimate grant. The same fixture supplies that complement: the exact `DELIVER: <report-stem>.patch` request expects no violation (`tests/fixtures/r20-audit-contract.py:153-155`), and a request for `.patch` does not authorize the same-stem alternative suffixes (`:156-161`). Production's exact candidate check and allowed-path wiring support that distinction (`tools/souji-seat-audit.py:137-150, 341-344`). Thus the overall C1 oracle covers both refusal and the explicit-permission positive control.

One bounded limitation: `BASE_BROAD_CASE_IDS` does not include `incidental-delivery-mention` (`tests/fixtures/r20-audit-contract.py:55-61`), so the fixture's optional baseline-discrimination inventory does not establish that this particular stimulus reproduces a historical baseline failure. I make no baseline-failure claim from static inspection. This does not make the selected-auditor expected-result case vacuous, and the pinned preregistration names the behavior as C1's unrequested-delivery refusal (`.ufo/waves/round-20/preregistration.txt:2-3`).

**Smallest safe correction:** none indicated for this case or its production predicate. Treat the baseline-comparison limitation as a boundary on claims, not as justification to alter the predicate or broaden grants. No stronger replacement stimulus is warranted by the reviewed sources.
