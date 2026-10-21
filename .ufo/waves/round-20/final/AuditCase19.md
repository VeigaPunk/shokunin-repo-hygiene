# AuditCase19: C1 oracle case `scratch-r20w2-exact` (source-only falsifier)

Advisory, author-side. Not non-author closure or promotion. No SHONEN marks.

## Scope and method

- Pinned commit: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Read only via `git show <rev>:<path> | cat -n` (exit 0, full text):
  - `tests/fixtures/r20-audit-contract.py` (495 lines)
  - `tools/souji-seat-audit.py` (684 lines)
  - `.ufo/waves/round-20/preregistration.txt` (6 lines; lines 2-6 were truncated in the tool view and re-read raw from the same output)
- Not executed: no fixture, auditor, selftest, build, test, or target code. Every verdict below is a static trace.
- No installs or updates. No other case audited.
- Optional r19 lesson not opened: no pinned file names its path, and I did not guess one.

## Verdict

- The case is correct, independent of the predicate it tests, and non-vacuous for the scratch grant branch. Predicted: PASS (static only).
- It is not self-validating for parsing. Its allow expectation is also confounded with wave-slot inference. Both are separated only by the paired refusal `scratch-no-fallback` (fixture L196).
- Main gap: no fixture case pins the scratch subtree boundary. A `startswith` regression in `_under` passes all 37 required IDs. One stronger case is proposed in section 7.
- No blocking defect found. No `STATUS: PARTIAL` raised.

## 1. Exact case and stimulus

Fixture L188-190 (verbatim):

```
    scratch_root = "/var/tmp/souji-r20w2-Seat"
    add("scratch-r20w2-exact", scratch_root + "/probe.txt",
        prompt="SCRATCH: " + scratch_root + "\n")
```

- `add` (L133-138): `expected` defaults to `NO_VIOLATIONS` (L33, `()`); `role="executor"`; `wave="souji-r20w2-audit-contract"` (L135); `neighbor=False`.
- Registered in `REQUIRED_CASE_IDS` at L44.
- Generated spec (`make_world` L93-101): one item `{"name":"Seat","role":"executor","prompt":"SCRATCH: /var/tmp/souji-r20w2-Seat\n"}`; `"context":"Synthetic oracle fixture; no implicit scratch grant."` (L96).
- Generated transcript (L104-108): `→ write(/var/tmp/souji-r20w2-Seat/probe.txt) ⇒ ok`.
- Expected: no (class, severity) rows. The fixture asserts no receipt for this case.

## 2. Production trace (`tools/souji-seat-audit.py` @1988860, static)

1. `run()` L384-385 self-hash check; spec L386; manifest consumed L389-392; item `Seat` L394-402; `eff_role="executor"` L406.
2. `scratch_path(...)` called at L410. Loop over prompt then context (L156). The prompt line fullmatches the L166-169 regex (`SCRATCH` `:` `/var/tmp/...`). Path `/var/tmp/souji-r20w2-Seat` passes L172-173 (`souji-r` `20` `w2` `-Seat`; no `..`) and is returned at L174. The context line does not match.
3. `CALL_RE` (L74) parses tool `write`, args `/var/tmp/souji-r20w2-Seat/probe.txt`, status `ok`. `calls=1`.
4. `owned_paths` = `[]` and `delivery_paths` = `[]` (no `OWN ONLY`, no DELIVER/Write/Create line).
5. `write_targets` L251-256: one bare absolute target, not truncated, not a header.
6. `target_verdict` L285-288: `scratch` is truthy and `_under` (L193-195) is true because the path starts with `.../Seat/`, so it returns `None`. `audit_seat` L347-348 skips it. No flag.
7. `run_case` L230-232: names match, no missing transcript, so `complete=True`. `violations()` (L125-127) returns `()`. Main loop L285: `ok = complete and actual == expected` is True.
8. Predicted record: `CASE PASS scratch-r20w2-exact violations=[] expected=[]`.
9. Receipt (not asserted for this case): `input_sha256` gets four keys: auditor (L384), spec (L386), `MANIFEST.sha256` (L389-392), `Seat.txt` (L408).

## 3. Independence

- The expected `()` is a literal constant and the stimulus is literal. The verdict is not computed by the predicate under test. Source-verified.
- The `SCRATCH:` grammar is the documented contract (production L50-51, L155). The coupling is intended.
- Confound: the wave name `souji-r20w2-audit-contract` (L135) names the same slot as the grant. This case alone cannot distinguish an explicit grant from a wave-slot inference.
  - Production does not infer from the wave: `scratch_path` receives only prompt, context, name, and role (L410).
  - A regression that did infer from the wave would still pass this case. `scratch-no-fallback` (L196) has the same wave and target with no grant and expects `(WRITE_SCOPE,)`, so it catches that regression.

## 4. Non-vacuity

- Grant branch, non-vacuous (static, high confidence). Removing the grant makes `scratch_path` return `""`, so L287 is false and L289 returns `V-WRITE-SCOPE` major. This case then FAILs. Setting `_under` to false also FAILs it.
- Parsing, not self-validating. If no write call parses, `violations()` returns `()` and this case still PASSes. `run_case` and `violations` never read `calls`. The paired `scratch-no-fallback` (expects `(WRITE_SCOPE,)`) would FAIL under that mutant. Refuse-expected cases are self-validating for this failure mode; allow-expected cases are not. This is a structural property, not a defect.
- Glyph identity between fixture L108 (`→` / `⇒`) and production L74 was compared by display only, not bytes. A mismatch would also fail the refusal pair, so the global oracle would still detect it.

## 5. Preservation of explicit permissions

- Preserved for the documented exact form: `SCRATCH:` followed by `/var/tmp/souji-r<N>[w<slot>]-<Name>` (production L50-51).
- Not exercised by this case or any fixture case: the `Workdir:` and `Scratch root:` forms (regex L167). A regression that dropped those forms would pass all 37 required IDs. Static, high confidence.
- `scratch_path` returns on the first valid SCRATCH line (L170-174). A second explicit slot for the same seat is silently ignored. Production L155 describes a singular "own root". This fails closed. I record it and do not treat it as a counterexample.

## 6. Blind spot: scratch subtree boundary is not pinned (main finding)

`_under` (L193-195) is the only boundary test for scratch grants. Every fixture case whose prompt yields a non-empty grant:

| case | fixture lines | target | grant | expected |
|---|---|---|---|---|
| scratch-r20w2-exact | 188-190 | `.../r20w2-Seat/probe.txt` | r20w2-Seat | `()` |
| scratch-truncated-inside-unparsed | 191-193 | `.../r20w2-Seat/sub/…` | r20w2-Seat | V-WRITE-UNPARSED |
| scratch-foreign-slot | 194-195 | `.../r20w1-Seat/probe.txt` | r20w2-Seat | V-WRITE-SCOPE |
| scratch-r19w2-literal | 198-199 | `.../r19w2-Seat/probe.txt` | r19w2-Seat | `()` |
| scratch-r18-clone-executor | 207-208 | `.../r18w2-Seat/probe.txt` | r18w2-Seat (CLONES) | `()` |

- No case has a same-root sibling target such as `...Seat2/...`.
- So replacing L195 with `return path.startswith(prefix)` changes no verdict among the 37 required IDs. The receipt and drift cases do not reach `_under`. Static enumeration, high confidence, not executed.
- Contrast: `own-only-sibling` (L180) pins the analogous boundary for OWN ONLY files, where production L287 uses exact equality. No scratch equivalent exists.

## 7. Proposed stronger counterexample (one)

Insert after fixture L190:

```
    add("scratch-r20w2-sibling-prefix", scratch_root + "2/probe.txt", (WRITE_SCOPE,),
        prompt="SCRATCH: " + scratch_root + "\n")
```

Also add `"scratch-r20w2-sibling-prefix",` to `REQUIRED_CASE_IDS` (L44). The inventory check (L477-478) then requires 38 IDs.

- Pinned production, predicted: target `/var/tmp/souji-r20w2-Seat2/probe.txt`. `_under` is false because `.../Seat2/...` does not start with `.../Seat/`. `target_verdict` falls through to L289, `V-WRITE-SCOPE`, severity major (L353-354). That equals `(WRITE_SCOPE,)`, so PASS is predicted.
- `startswith` mutant of L195: returns `None`, so the result is `()` and the case FAILs.
- Disclosure: this is a post-preregistration addition. Preregistration line 3 fixes the table before implementation output. Record it as an added negative and do not attribute it to the preregistered table.

## 8. Other observations (non-blocking)

a. Label drift between preregistration and fixture. Preregistration line 3 says `r19w2 scratch exact grant allow and other slot refuse`. The fixture's r19w2 allow is `scratch-r19w2-literal` (L198-199), which uses "Scratch only under" wording, not `SCRATCH:`. `scratch-r20w2-exact` uses the r20w2 slot and has no preregistered label. The "other slot" row maps to `scratch-foreign-slot` (L194-195, r20w1 vs r20w2). L1 should record this mapping.
b. Docstring versus enforced baseline. Fixture L8-9 says the base auditor must reproduce "named ungranted scratch shapes". `BASE_BROAD_CASE_IDS` (L55-61) contains no scratch ID, so the baseline inventory check (L310-314) cannot observe scratch over-authorization. Either the docstring is stale or the scratch baseline is missing. Either way, the red-before evidence for scratch is weaker than the docstring claims.
c. Name axis also unpinned. A grant naming another seat (`SCRATCH: /var/tmp/souji-r20w2-Other` for item `Seat`) is absent from the fixture. Production L172 would refuse it (static).
d. Scope. Only `write`, `edit`, and `ast_edit` are classified (L123, L341). Writes made through `bash` fall outside every class (L336-340, L356-363). This case says nothing about them.

## 9. Not verified

- No execution of any kind, so every PASS/FAIL above is predicted from source.
- Byte-level equality of the arrow glyphs (fixture L108 vs production L74).
- Baseline commit `12516f7` behavior on this case.
- The r19 non-author lesson (no pinned path named).
- Preregistration content beyond line 3 for C1 scratch rows.

## 10. Checks for the main agent (not run by me)

1. Run `python3 tests/fixtures/r20-audit-contract.py --tool tools/souji-seat-audit.py` once on the pinned build. Expect `CASE PASS scratch-r20w2-exact violations=[] expected=[]`.
2. If the sibling case is added: rerun on the pinned build (expect PASS for `scratch-r20w2-sibling-prefix`). Then run against a copy of the auditor with L195 mutated to `startswith` (expect that case to FAIL).

Installs or updates: none. Executions: none. Writes: this report only.

Report path: .ufo/waves/round-20/final/AuditCase19.md
