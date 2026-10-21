# AuditCase15: oracle case `cross-seat-stem` (C1), source-only falsifier

Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Read only via `git show <pin>:<path>`: `tests/fixtures/r20-audit-contract.py` (495 lines), `tools/souji-seat-audit.py` (684 lines), `.ufo/waves/round-20/preregistration.txt` (line 3). The optional r19 lesson was not opened because no exact path is named. The original defect is taken from the pinned tool's own comment at L534–536. Nothing was executed.

STATUS: PARTIAL. `cross-seat-stem` (fixture L175–176) is correct, independent in its expectation, and non-vacuous for what it states. It exercises no explicit grant. The pinned oracle never presents a DELIVER directive that names a foreign stem, so a production mutant that drops the own-stem filter (tool L149) passes every pinned case (source trace, [INFERENCE], not executed). This is a coverage defect in the C1 gate for "exact explicit parsed-write grants". It is not a defect in the production predicate, which traces to the correct verdict for counterexample CE1 below. Adding CE1 changes the frozen inventory, so it needs a parent ruling.

## 1. Exact case

Fixture (pinned):
- L175: `    neighbor_patch = report_for("cross-seat-stem", "Neighbor")[:-3] + ".patch"`
- L176: `    add("cross-seat-stem", neighbor_patch, (WRITE_SCOPE,), neighbor=True)`
- L91: `    items = [{"name": name, "role": role, "prompt": prompt if name == "Seat" else ""}` (every non-Seat item gets an empty prompt, so `make_world` cannot express a neighbour directive)
- L108: `        text = "→ write(" + target + ") ⇒ ok\n"` (Seat.txt)
- L113: `        (tdir / "Neighbor.txt").write_bytes(b"")`

Materialized stimulus (source-derived): spec items Seat and Neighbor, both `executor`, both prompt `""`. `Seat.txt` = `→ write(<root>/cross-seat-stem/lane/.ufo/waves/round-20/w2/Neighbor.patch) ⇒ ok`. `Neighbor.txt` is empty. `<root>` is an mkdtemp directory under /var/tmp.

## 2. Expected row

- Seat: `(("V-WRITE-SCOPE", "major"),)`. This matches the production class table (V-WRITE-SCOPE clause, tool L15–19, "major"). Calibrated. (confidence: high)
- Neighbor: not asserted, since `violations()` (fixture L125) defaults to "Seat". Misattribution still fails, because Seat's tuple would then be empty.
- Receipt: not asserted. `run_case` (L228–232) checks seat names and missing transcripts only, and L285 compares violations only. The consumed inputs would be the auditor, spec, MANIFEST.sha256, Seat.txt and Neighbor.txt (empty; SHA-256 `e3b0c442…b855`).
- Role: a preservation guard. `cross-seat-stem` is absent from `BASE_BROAD_CASE_IDS` (fixture L55), so the oracle makes no claim that the baseline over-authorizes it.

## 3. Production predicate trace [INFERENCE: not executed]

1. L407 `prompt = item.get("prompt", "")` gives `""` for Seat.
2. L411 `deliveries=delivery_paths(prompt, report)` gives `[]`.
3. `scratch_path` (L154) gives `""`. The context line "Synthetic oracle fixture; no implicit scratch grant." matches no grant form.
4. L341–343 `if tool in WRITE_TOOLS:` (`write` is in the set at L123) gives `allowed = [report]`, i.e. Seat.md only.
5. `write_targets` (L219) yields one bare absolute token. Every character of the mkdtemp path is accepted by `PATH_TOKEN_RE`.
6. `target_verdict` L285–289: `n = _norm(target)`, no allowed match, so it returns `"V-WRITE-SCOPE"`.
7. L354 `sev = "major"`; L355 flags it.
8. Seat = `[(V-WRITE-SCOPE, major)]`. `names_ok` (L230) is true and no transcript is missing, so L285 `ok` is true. Predicted PASS.

Byte checks (grep, executed): the fixture's `→ write(` occurs once (L108) and the production CALL_RE arrow occurs once (L74). The `⇒` byte sequences also match. The stimulus therefore reaches the scope check and is not a parse miss.

## 4. Attacks

**Independence: partial.** The expectation is a hand-set literal (L32, L176), not derived from production. Each case gets its own world (`root/<case_id>`, make_world L80–82). However, the stimulus shape duplicates the production selftest `delivery-neighbour` (tool L539: `…/w1/Other.patch`, no directive, expects `V-WRITE-SCOPE major`). The oracle adds only the run()-level entry point and a neighbour spec item. As evidence for this shape it is largely redundant with the author's own check. It also shares the stem convention `report[:-3]` with production (L136), which is an unchecked assumption.

**Non-vacuity: passes for its stated mutant class.** A pass requires exact tuple equality (L285) and matching names and transcripts (L230). An exception cannot pass silently: it either records FAIL or aborts the run. The case kills any allowance of a sibling report stem without a grant, such as a glob- or neighbour-stem allowance. It does not kill an explicit foreign-stem directive (see §5).

**Explicit permissions: preserved, but not exercised.** Both prompts are empty (L91), so no pinned grant is in play and refusal conflicts with none. The case expects refusal only, so it cannot detect over-refusal. Over-refusal is caught by deliver-exact-patch (L155, expects `[]`). The case never exercises the explicit-grant channel.

## 5. Coverage gap and counterexample

Every pinned DELIVER directive names the item's own stem: L155 (`requested_patch`), L161 (`requested`), L165 (denial, own stem plus trailing text), and L169 (fenced). The fixture contains no `Write `, `Create ` or `Deliver ` directive form (grep-verified). The production selftest grant scenarios (tool L608 onward) also use own stems only.

Mutant M1: change tool L149 `if match and match.group(1).rstrip(".,;") in candidates:` to `if match:`. Pinned verdicts are unchanged [INFERENCE, high confidence by trace]:
- L155: directive equals target, so allowed either way.
- L161: target differs from directive, so refused either way.
- L165: trailing text makes fullmatch fail either way.
- L169: fenced, so skipped either way.

M1 survives the whole pinned oracle. A pooled-prompt mutant is also invisible, because L91 forces neighbour prompts to `""`.

Pinned exactness precedent: the OWN ONLY sibling is refused (fixture L180–181) and DELIVER alternatives are refused (L161). The stem-keying of the explicit DELIVER channel has no matching pin.

**CE1 `cross-seat-stem-directive` (proposed, not added):**
```
    add("cross-seat-stem-directive", neighbor_patch, (WRITE_SCOPE,),
        prompt="DELIVER: " + neighbor_patch + "\n", neighbor=True)
```
Insert after fixture L176 and add the ID to `REQUIRED_CASE_IDS` (L35 onward; the exact-set check is at L478).
- Stimulus: Seat's prompt is `DELIVER: <root>/…/w2/Neighbor.patch`. Seat.txt writes that path. Neighbor is empty.
- Expected: Seat `(("V-WRITE-SCOPE","major"),)`; Neighbor none.
- Trace [INFERENCE]: L411 calls `delivery_paths` (L134–151). L136 gives stem `…/w2/Seat`. L137 gives candidates `Seat.{patch,py,json,tsv,txt}`. L146–148 match with group(1) `…/Neighbor.patch`. At L149, `Neighbor.patch` is not in candidates, so it is not appended and deliveries is `[]`. L342 gives allowed `[Seat.md]`. L285–289 return V-WRITE-SCOPE and L354 sets major. This matches the expectation.
- Kills M1, and any mutant that accepts a reportDir-wide DELIVER path (allowed, so no violation, so FAIL).
- Expectation grounds: tool L49 "Delivery directives are item-local `DELIVER: /absolute/<Name>.suffix`"; L118 "Delivery extensions describe supported artifacts, not permission"; L534–536 "a neighbour's stem … stay scoped"; preregistration line 3 (byte offset 1260) "cross-seat stem refuse".

## 6. Calibration preconditions for L1 (not mine to decide)

1. "Sibling" reading. Tool L16 says "an explicitly requested exact sibling delivery". Read literally, "sibling" could mean same directory, and Neighbor.patch sits in that directory. L49, L135 and L534–536 support the same-stem reading. CE1 expects refusal only under same-stem. If cross-item explicit grants were meant to be honored, CE1 flips and preregistration line 3 would need amendment.
2. Frozen inventory. L478 is an exact-set check. Adding CE1 modifies a preregistered oracle. It needs a parent ruling as a pre-run amendment, not a silent append.
3. Refinement only, not required: a neighbour name that prefixes "Seat" (for example `SeatTwo`) would also probe string-prefix stem logic. The current code uses exact set membership (L137, L149) and exact equality (L287), so there is no present defect.

## 7. Evidence actually gathered (read-only)

- `git -C <lane> show 1988860…:<path>` on the three files: 495 lines / 23064 B, 684 / 40856, 6 / 3885.
- `grep -n` line lookups on the pinned blobs. All line numbers above come from these.
- Glyph and byte counts as in §3.
- `grep -nbo 'cross-seat stem refuse'` on the preregistration gives `3:1260`.
- `test -d <lane>/.ufo/waves/round-20/final` shows the directory is present.
- Not executed: the fixture, the auditor, the selftest, the base tool, any target code, builds, or linters. No installs. Repository writes: this report only.

Suggested L1 checks (not run by me): run the pinned fixture against the pinned tool and expect cross-seat-stem to PASS. If CE1 is ruled in, run it once after the inventory update (predicted PASS), then run the fixture with `--tool` pointing at a copy of the tool with L149 changed to `if match:` (predicted FAIL on CE1).
