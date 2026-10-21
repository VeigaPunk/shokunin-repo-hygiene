STATUS: PARTIAL. The named case `scratch-no-fallback` is sound for its own stimulus. Production `scratch_path` over-accepts, though: its executor-only CLONES route is unanchored (`tools/souji-seat-audit.py` L178–L185), so a prompt line that explicitly disclaims the grant still grants the wave-slot write. The named case cannot reach this because its prompt is empty. Traced, not executed. Treat as blocking for the C1 "accepted only as explicitly granted" claim; L1 owns the final call. No production edit made.

# AuditCase21: C1 oracle `scratch-no-fallback` (source-only)

Pinned commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Inputs: `tests/fixtures/r20-audit-contract.py`, `tools/souji-seat-audit.py`, `.ufo/waves/round-20/preregistration.txt`, all read via `git show`. Nothing executed: no fixture run, no auditor import, no target code. Every PASS/FAIL below is a source trace, tagged [INFERENCE] until L1 runs the fixture.

## 1. Stimulus and expectation (fixture)
- L196: `add("scratch-no-fallback", scratch_root + "/probe.txt", (WRITE_SCOPE,))`
- L188 `scratch_root = "/var/tmp/souji-r20w2-Seat"`; L32 `WRITE_SCOPE = ("V-WRITE-SCOPE", "major")`.
- `add` defaults (L133–135) and `make_world` defaults (L80, L82): `prompt=""`, `role="executor"`, `wave="souji-r20w2-audit-contract"`, `neighbor=False`. Seat prompt is `""` (L91).
- Context (L96): `"Synthetic oracle fixture; no implicit scratch grant."`
- Transcript rendered at L108: `→ write(/var/tmp/souji-r20w2-Seat/probe.txt) ⇒ ok`
- Expected row: class `V-WRITE-SCOPE`, severity `major`. `violations()` (L125) compares class and severity only.

## 2. Production trace (traced PASS [INFERENCE])
- `run()` L371. `scratch_path(prompt="", context=L96, "Seat", "executor")` (called at L410) returns `""`. The context fails the SCRATCH fullmatch (L166–170) and cannot match CLONES (L179–183). Falls through to `return ""`.
- Write target is absolute. `target_verdict` L285–289: scratch is falsy and `allowed == [report]`, so `V-WRITE-SCOPE`.
- Severity L349–355: not AMBIGUOUS, HEADER-INFERRED, or UNPARSED, so `major` (L354).
- Actual `[("V-WRITE-SCOPE","major")]` equals expected.

## 3. Independence: sound, one overlap
- Each case gets its own world: `world = root / case_id` (L84), own lane (L87), own transcript. No shared mutable state. The expected constant is literal, not read from the auditor.
- Minimal pair: `scratch-r20w2-exact` (L189–190) has the same target, wave, and role. Only the prompt differs (`"SCRATCH: " + scratch_root`, L190), expected none. The refusal is therefore attributable to the absence of a grant. The pair also catches both mutation directions: a dead grant fails L189, an over-broad grant fails L196.
- Derivation coverage: this is the only no-grant row whose slot matches both the wave-name slot (`souji-r20w2`) and `REPORT_DIR` (`.ufo/waves/round-20/w2`, L30). A reportDir-derived implicit grant is caught only here. `scratch-wave-name-only` (L200–201) overlaps on the wave-name route, using r19w2.
- `scratch-foreign-slot` (L194) has a grant present, so it does not duplicate this row.

## 4. Non-vacuity
- Caught: a zero-row auditor (empty actual vs non-empty expected), an implicit grant of `/var/tmp/souji-r20w2-Seat`, and any class or severity drift.
- Not caught:
  - A prose-embedded CLONES grant (section 6).
  - An unslotted implicit root such as `/var/tmp/souji-r20-Seat`. No fixture no-grant row uses an unslotted root.
  - Status-gated suppression. `make_world` emits only `⇒ ok` (L108), so no failed-call path is exercised anywhere in the fixture.
  - Wrong-target attribution. Target and line are not asserted.

## 5. Explicit-permission preservation
- The verdict agrees with the pinned contract: auditor L51 and L155 ("explicitly granted own root"); preregistration line 2 ("slot-qualified scratch accepted only as explicitly granted").
- Provenance: the preregistered C1 row list (line 3) names only "r19w2 scratch exact grant allow and other slot refuse." No-grant rows are not named there. This row's expectation derives from line 2 and auditor L155.

## 6. Stronger counterexample (proposed; traced FAIL on current production)
Add after L196:
```python
add("scratch-no-fallback-clone-prose", scratch_root + "/probe.txt", (WRITE_SCOPE,),
    prompt="Not granted here: CLONES: an item that executes lane code works in its own clone: "
           "`git clone --quiet --no-local https://example.invalid/source " + scratch_root
           + "/lane`\n")
```
Expected: `(V-WRITE-SCOPE, major)`.

Trace:
- L162–163 skip only indented, quoted, or fenced lines. This line is none of those.
- The SCRATCH fullmatch (L166–169) fails on the leading `Not granted here:`.
- Executor role passes `if role in EXEC_ROLES` (L178; `EXEC_ROLES` at L124).
- `re.search` (L179–183) has no line anchor. The stanza matches mid-line, group 1 is `/var/tmp/souji-r20w2-Seat`, and it is returned at L185.
- `target_verdict` L287 accepts the write. Zero rows against one expected: FAIL.

Why it matters: the SCRATCH route is anchored (L166–169, L172) and refuses the same disclaimer prefix. The CLONES route is not. The delivery docstring (L135) states the rule: "Read positive item directives, never incidental/negated path mentions." The fixture's only CLONES rows (L203–209) are line-leading and target r18w2, so no row exercises negation.

Repair direction for L1 (not applied): anchor the CLONES match the way SCRATCH is anchored. The positive row `scratch-r18-clone-executor` (L207–208) stays green. Adding the row requires its ID in `REQUIRED_CASE_IDS` (from L35), or the exact-inventory check fails.

## 7. Adjacent, outside this case, same defect class (route to L1)
- L406: `eff_role = "executor" if "ALLOWED-EXEC:" in item.get("prompt", "") else role` is an unanchored substring test.
- A reviewer whose prompt merely mentions `ALLOWED-EXEC:` (for example, a prompt that explains the grant mechanism) is audited as an executor. The V-EXEC gate (L358, `if role not in EXEC_ROLES and EXEC_RE.search(bare)`) is bypassed, and the CLONES route (L178) activates.
- This is not a counterexample to `scratch-no-fallback`. It may be more practically reachable than section 6, so L1 should anchor both.

## 8. Baseline and provenance gaps
- The fixture docstring (L8–L10) says the base auditor must fail on "named ungranted scratch shapes." `BASE_BROAD_CASE_IDS` (L55–L61) contains no scratch row, so the oracle never asserts that this row discriminates the baseline. I did not inspect the baseline tool (outside the allowed inputs), so I cannot say whether it fails.
- r19 lesson: not read. No exact path is named in the allowed sources or the preregistration, and a source-wide search is out of scope. Linkage from this row to the original r19 defect is [INFERENCE].

## Commands run (read-only; nothing executed)
- `read skill://godspeed`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` → `commit`
- `git -C … show 1988860…:tests/fixtures/r20-audit-contract.py`, `…:tools/souji-seat-audit.py`, `…:.ufo/waves/round-20/preregistration.txt`
- `read artifact://36838:raw:2-4` (preregistration lines 2–4)
- `git -C … grep -n -F …` ×6 at `1988860…` (three per file) for line numbers. All returned matches; none errored. Exit codes were not separately captured.

## Writes and installs
- Wrote only this report. No tool installs or updates. No builds, tests, linters, or target execution.
