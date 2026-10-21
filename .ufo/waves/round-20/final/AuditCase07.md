# AuditCase07: round-20 C1 case `deliver-exact-patch` (source-only falsifier)

**Pin:** `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Sources read only via `git show` of the three named paths. Nothing executed: no builds, tests, fixtures, or target code. No tool installs or updates. Author-side advisory, not non-author closure. No [x] marks.

**Optional r19 lesson:** not consulted. None of the three sources names an exact pinned path for it, and I did not open guessed paths. The named-defect reference is the auditor's own r19 C1 comments (`tools/souji-seat-audit.py` L118-119, L534-536).

## Verdict

- Case `deliver-exact-patch` traces to **PASS** under the pinned auditor: violations `()`, `complete` True, equal to the preregistered expectation. It is a correct positive control.
- **No blocking defect in this case.** No `STATUS: PARTIAL`.
- Non-blocking findings, by weight:
  1. Mutant V (grant any absolute `DELIVER:` path by dropping the candidate filter) passes the entire fixture and the in-tool selftest. Exactness of explicit grants across stems is unfalsified.
  2. The case does not require `calls == 1`. A parser that records zero calls passes it.
  3. Adjacent fence-toggle defect in `delivery_paths` (outside this case, section 5).
- Proposed stronger counterexample: section 4. It adds a row beyond the preregistered C1 table, so L1 must rule on it.

Confidence: high on the stimulus and production trace (line by line, source-only). Medium-high that mutant V passes the whole fixture (traced per case, not executed).

## 1. Stimulus and expectation (fixture @ pin)

Case definition:
```
L153  requested_patch = report_for("deliver-exact-patch")[:-3] + ".patch"
L154  add("deliver-exact-patch", requested_patch,
L155      prompt="DELIVER: " + requested_patch + "\n")
```
Default `expected=NO_VIOLATIONS` (L33, L133). Appended at L138. Required ID at L39.

Resolved, with `T = <top>/deliver-exact-patch/lane/.ufo/waves/round-20/w2/Seat.patch` and `<top> = /var/tmp/souji-r20-audit-contract.*`:
- World `<top>/deliver-exact-patch` (L84-85).
- `spec.json` (L93-101): one item `{"name":"Seat","role":"executor","prompt":"DELIVER: T\n"}`. `reportDir` `.ufo/waves/round-20/w2` (L30, L97). `context` "Synthetic oracle fixture; no implicit scratch grant." (L96). Wave `souji-r20w2-audit-contract` (L83). No Neighbor item.
- `transcripts/Seat.txt` (L104, L107-108): `→ write(T) ⇒ ok` plus newline.
- `transcripts/MANIFEST.sha256` (L102-103): synthetic bytes.
- Expected: `violations == ()`. `complete` is names-match and no missing transcript (L228-232). Verdict at L285: `ok = complete and actual == expected`.
- Receipt: **not asserted** by this case. Predicted `input_sha256` keys: auditor, `spec.json`, `transcripts/Seat.txt`, `transcripts/MANIFEST.sha256`, with `inputs_unchanged_during_run` True. Receipt keys are asserted only in `receipt-exact-digests` (L322-332). The DELIVER line sits inside hashed spec bytes (tools L386, L431-432), so the grant is receipt-bound by construction. No case checks that.

## 2. Production trace (`tools/souji-seat-audit.py` @ pin)

1. L386-388: spec parsed from consumed bytes. `fleet = <top>/deliver-exact-patch`.
2. L402: `R = <lane>/.ufo/waves/round-20/w2/Seat.md`.
3. L406-407: role stays `executor`. Prompt is the DELIVER line.
4. L408-411: `owned_paths` gives `[]`. `scratch_path` gives `""`: the prompt line fails the fullmatch at L166-170, and context line L96 does not match. `deliveries = delivery_paths(prompt, R)`.
5. L136-137: `candidates` contains `R[:-3] + ".patch" == T`.
6. L146-148: fullmatch on `DELIVER: T` with group `T`. L149: `T ∈ candidates`, so `deliveries = [T]`.
7. L320-324: CALL_RE matches tool `write`, args `T`, status `ok`. `calls = 1`.
8. L332: no surface match. L342-343: `allowed = [R, T]`.
9. L251-255: `write_targets` yields `(T, False, False)`.
10. L263-289: not None. No `..` (L267). Not truncated. Absolute. L287: `_norm(T) == _norm(T)`, so `None`.
11. No flag. L422-425 input-stability check passes. Seat `violations == []`.

Observed `()` equals expected `()`. PASS by trace.

## 3. Attacks

### 3a Independence: holds
- Own world directory per case (L84-85). No shared spec, transcript, lane, or manifest file with `unrequested-patch` (L151), `deliver-alternative-*` (L156-161), or any other world.
- Expectation is hard-coded (L133, L138), not derived from production. The fixture re-declares `DELIVERY_SUFFIXES` (L31) rather than importing it.
- Runs in the first loop (L279-287), before any `Path.read_bytes` patch (L415, L462). No drift patch can touch it.
- Not a baseline discriminator: absent from `BASE_BROAD_CASE_IDS` (L55-61). It is a preserve-permission control.
- Minimal pair with `unrequested-patch` (L151, empty prompt). The directive is the only varying input, apart from the world directory name.

### 3b Non-vacuity: partial
- **Grant dropped** (L149 or L343 effect removed): `allowed = [R]`, L289 returns `V-WRITE-SCOPE`, and L353-354 assign major. The case FAILs. Discriminates.
- **Parse lost** (tools L320-322 no-match `continue`, or any CALL_RE miss): `calls = 0`, `violations == ()`, and the case PASSes. Does not discriminate. Only the sibling `unrequested-*` cases (expect WRITE_SCOPE, L151) catch it. The suite still fails, but this case is vacuous.
- Hardening, with no new row: also require `result["seats"]["Seat"]["calls"] == 1` in the verdict (L285).

### 3c Explicit permission: exact path preserved, boundary untested

Mutant V: `delivery_paths` returns every absolute path matched at L146-148, with the L149 candidate test dropped. Traced across all DELIVER-bearing fixture cases:
- `deliver-exact-patch`: same path, so PASS.
- `deliver-alternative-{py,json,tsv,txt}` (L156-161): written path differs from the granted `.patch`, so refused, so PASS.
- `deliver-denial-trailing-text` (L163-165): fullmatch at L148 fails, so refused, so PASS.
- `deliver-example-fenced` (L167-169): fence skip at L141-145, so refused, so PASS.
- `incidental-delivery-mention` (L171-173): no directive, so PASS.

The selftest grant family (tools L599-627) also uses only candidate paths. So mutant V passes the entire fixture and the selftest. The preregistered C1 table (prereg line 3) has no row for a DELIVER naming a non-candidate path.

Form coverage, not pinned by the fixture: the case uses an absolute `write` target, the only unambiguous form. An absolute `edit` header is equivalent (L285-289). A relative header of the same delivery yields minor `V-WRITE-HEADER-INFERRED` (L301-306) by design. A bare relative write yields major `V-WRITE-RELATIVE` (L308-311), correctly, because it resolves at the fleet root.

## 4. Proposed stronger counterexample (not applied)

Fixture addition after L161:
```python
neighbor_grant = report_for("deliver-cross-seat-grant", "Neighbor")[:-3] + ".patch"
add("deliver-cross-seat-grant", neighbor_grant, (WRITE_SCOPE,), neighbor=True,
    prompt="DELIVER: " + neighbor_grant + "\n")
```
Also add `"deliver-cross-seat-grant"` to `REQUIRED_CASE_IDS` (L35-54). Without that second edit, `oracle-exact-case-inventory` (L475-485) fails.

Predicted by trace: Seat's candidates (L137) exclude `Neighbor.patch`, so `deliveries = []` (L149), so `allowed = [R]` (L342-343), so `V-WRITE-SCOPE` major (L289, L353-354), so PASS. Mutant V grants it and FAILs. A "same report directory, other stem" mutant also FAILs.

Consistent with the tool contract `DELIVER: /absolute/<Name>.suffix` (L49-50) and the r19 C1 scope note "a neighbour's stem … stay scoped" (L534-536). It adds a row beyond the preregistered table, so L1 must rule on amending the preregistration before it is added.

## 5. Adjacent predicate defect (outside this case; non-blocking)

`delivery_paths` L141-142 and `scratch_path` L159-160 toggle one `in_fence` flag on any line starting with ``` or ~~~, regardless of marker or length. Minimal input, lead-authored prompt:
```
~~~
```bash
DELIVER: T
~~~
```
The `DELIVER` line sits inside the `~~~` block. The ```` ```bash ```` line toggles the flag off, so L149 grants T. Traced, not executed.

No fixture case uses mixed or nested fences. `deliver-example-fenced` (L169) uses bare ``` only. Impact: a missed violation when the lead's prompt contains such an example. It is not seat-driven, because the spec is lead-authored. Suggested for L1: close a fence only on the same marker, at least as long as the opener (CommonMark). Not applied.

## 6. Caveats
- The `→` and `⇒` glyphs in fixture L108 and tools L74 match as displayed. Not byte-checked.
- All results are by source trace. Nothing was executed.

## Checks for the main agent
One run of `tests/fixtures/r20-audit-contract.py --tool tools/souji-seat-audit.py` after integration. Expected: `deliver-exact-patch` PASS (section 2). This report is not a pass.
