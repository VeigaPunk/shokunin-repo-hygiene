# AuditCase22: falsifier for C1 oracle `scratch-r19w2-literal`

Pin: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. Source-only. Nothing was executed.

**Verdict:** Source agreement on the positive trace. No blocking defect, so no `STATUS: PARTIAL` marker. The expectation is independent of the parser, but the stimulus provenance is not pinned. The case is non-vacuous only as a pair with its twin `scratch-wave-name-only`. One strengthening counterexample is proposed in section 6: a literal grant naming a foreign seat must be refused. By reading, neither the oracle nor the selftest grants a foreign name, so a loosened name binding passes today.

**Confidence:** high on the production trace, since each branch and regex was checked at T:166-172 and T:285-289. Medium on provenance, which this seat cannot verify. By reading only, not run: high that the loosened-name mutant passes the current suite.

## 0. Provenance and method

- Blob IDs at the pin (`git rev-parse`):
  - `tests/fixtures/r20-audit-contract.py` 6987ebec65c891f4888a4236cd4451c26067d583
  - `tools/souji-seat-audit.py` 4e90f7d4d770aeeb84419c933efb8e8833d633f0
  - `.ufo/waves/round-20/preregistration.txt` 87892655fe73c29e1ec329c81b80345a6b38c51d
- Read-only commands actually run:
  - `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path>` for the three named files.
  - The two source files again, piped through `cat -n`, for line numbers.
  - `git rev-parse` on the three blobs.
  - Artifact reads of preregistration lines 2-4, which were truncated in the first view.
  - Each returned the pinned bytes with no error text. Exit status was not captured.
- Not run: the fixture, the tool, `--selftest`, builds, linters, installs. Tool installs: none.
- Optional r19 lesson: none of the three named files names its path. I did not open it or search for it.
- Line references: `F:` = fixture, `T:` = tool, `P:` = preregistration, all in the pinned blobs. "Predicted" means traced from source, not observed.

## 1. Case identity

- F:45 lists `scratch-r19w2-literal` in `REQUIRED_CASE_IDS`.
- F:197 `historical_root = "/var/tmp/souji-r19w2-Seat"`
- F:198-199:
  ```python
      add("scratch-r19w2-literal", historical_root + "/probe.txt",
          prompt="- Scratch only under /var/tmp/souji-r19w2-<YourName>/;\n")
  ```
- Expected: no explicit argument. The default `expected=NO_VIOLATIONS` (F:133, defined at F:33) is the empty tuple. Role defaults to `executor` (F:134). Wave defaults to `souji-r20w2-audit-contract` (F:135).
- Twin: F:200-201, `scratch-wave-name-only`. Same target, no prompt, wave `souji-r19w2`, expected `(WRITE_SCOPE,)`, where F:32 is `WRITE_SCOPE = ("V-WRITE-SCOPE", "major")`.

## 2. Exact stimulus

- Spec (F:90-99): one item `{"name": "Seat", "role": "executor", "prompt": <F:199 string>}`. `context` is `"Synthetic oracle fixture; no implicit scratch grant."` (F:96). `reportDir` is `.ufo/waves/round-20/w2`.
- Transcript `Seat.txt` (F:104, F:107-108): `→ write(/var/tmp/souji-r19w2-Seat/probe.txt) ⇒ ok`
- `MANIFEST.sha256` (F:102-103): synthetic bytes.
- Oracle decision (F:285): `ok = complete and actual == expected`.
  - `actual` is `violations()` (F:125-127): the sorted `(class, severity)` pairs for seat `Seat`.
  - `complete` (F:230-232) requires the seat set to equal `{Seat}` and no missing transcript.

## 3. Production trace (predicted from source, not executed)

`run()` in T:371-436:

1. T:406: `eff_role = "executor"`. No `ALLOWED-EXEC:` is present.
2. T:410 calls `scratch_path(prompt, context, "Seat", "executor")` (T:154-186):
   - T:164-165 replaces `<YourName>` with `Seat`. The line becomes `- Scratch only under /var/tmp/souji-r19w2-Seat/;`.
   - T:166-169 fullmatch: the `- ` bullet (T:166), the `Scratch only under ` alternative (T:167-168), group `/var/tmp/souji-r19w2-Seat/`, then `;` consumed by `[.;]` (T:169).
   - T:171: `path = /var/tmp/souji-r19w2-Seat`.
   - T:172-173: `re.fullmatch(r"/var/tmp/souji-r\d+(?:w\d+)?-" + re.escape("Seat"), path)` matches (`19`, `w2`, `-Seat`), and there is no `..`. T:174 returns the path.
   - Result: scratch = `/var/tmp/souji-r19w2-Seat`.
3. T:411: `deliveries = []`, because the T:146-150 pattern matches no DELIVER, Write, Create or Deliver form. T:127-131: `owned = []`.
4. `audit_seat` (T:314-368):
   - T:74 `CALL_RE` matches: tool `write`, status `ok`. T:323: `calls = 1`.
   - T:332: no SURFACE match.
   - T:341-355, write branch: `allowed = [report]` (T:342). `write_targets` (T:251-255) yields one target, not truncated, not a header.
5. `target_verdict` (T:259-311), absolute branch T:285-287: `_under(normpath(target), normpath(scratch))` (T:193-195, `startswith(prefix + os.sep)`) is True. T:288 returns `None`. T:347-348 skip.
6. `found = []`. T:412 records seat `Seat` with `calls 1` and `violations []`.

Predicted result: `violations = ()` equals expected `()`, and `complete = True`. PASS.

The `()` result depends on the scratch grant. If T:172 failed, T:289 would emit `V-WRITE-SCOPE` major and F:285 would FAIL.

## 4. Expected severity, class, receipt

- Severity and class: none, `()`. The twin's `(V-WRITE-SCOPE, major)` is the outcome if the grant is not parsed.
- Receipt: not asserted by this case. `run()` would still bind four consumed inputs:
  - the auditor (T:384-385),
  - the spec (T:386),
  - `MANIFEST.sha256` (T:389-392),
  - `Seat.txt` (T:396, T:408).
  Keys are resolved paths (T:378). `inputs_unchanged_during_run = True` (T:433). The receipt is checked only by `receipt-exact-digests` (F:316-336), on a different world.

## 5. Attack results

**A. Independence: partial.**

- Expectation: independent. It is a fixed default (F:133), not derived from the parser.
- Stimulus provenance: not pinned.
  - F:199 is typed by the fixture author.
  - The `<YourName>` token (T:164) and the whole grammar (T:166-169) belong to the production.
  - The fixture has no citation at F:197-199.
  - The tool docstring (T:49-51) documents only `SCRATCH:`, `Workdir` and `Scratch root`. `Scratch only under` (T:167-168) is code with no documentation.
  - The only pinned anchor is P:3, "r19w2 scratch exact grant allow". It states allow but does not quote the literal.
  - Without the r19 source bytes, this seat cannot confirm the literal is the historical text.
- Specific risk: T:169 accepts a tail `;\s*clean it up\.`. No fixture or selftest text I read contains "clean it up". If the historical line carried that tail, the positive does not cover the historical form.

**B. Non-vacuity: holds only as a pair.**

- Against loss of the grant: the positive FAILs (T:289). This is good.
- Against zero recognized calls (a T:74 miss) or no write audit (`WRITE_TOOLS`, T:123): the positive still PASSes, because the fixture asserts no call count. The twin (F:200-201) FAILs in both cases, since it expects `(WRITE_SCOPE,)`. The suite catches these failures, but the positive alone does not.
- The pair is not a controlled A/B. It varies both the wave (F:201 `souji-r19w2` against the default at F:135) and grant presence. The production reads no wave for scratch: `run()` passes only `context` (T:410). This is inert today.
- `violations()` compares only `(class, severity)` (F:125-127), not targets. This limits resolution but does not affect this case, which has no flags.
- Adjacent: F:8-9 says the base auditor must reproduce "named ungranted scratch shapes". `BASE_BROAD_CASE_IDS` (F:55-61) contains no scratch ID, and the base inventory check (F:310-314) enforces equality. The twin is therefore never baseline-checked.

**C. Explicit permission: the literal grant is honored; name binding is untested.**

- The positive confirms that the literal grant is honored for name `Seat`.
- Name binding (`re.escape(name)`, T:172) is never tested with a foreign name.
  - Every scratch grant in the oracle uses `Seat`: F:188-199, plus the CLONES prompt at F:206.
  - Selftest grant scenarios use `S` (T:611-627, item at T:631).
  - The `run-scratch-wiring` check (T:583-598) uses each seat's own name.
- I traced each of these grants. Loosening the name group at T:172 changes no outcome in the oracle or in these selftest scenarios.

## 6. One proposed stronger counterexample

ID: `scratch-r19w2-literal-foreign-name` (new). Insert after F:201:

```python
    add("scratch-r19w2-literal-foreign-name",
        "/var/tmp/souji-r19w2-Neighbor/probe.txt", (WRITE_SCOPE,),
        prompt="- Scratch only under /var/tmp/souji-r19w2-Neighbor/;\n")
```

- Add the ID to `REQUIRED_CASE_IDS` (F:45). Otherwise the inventory check (F:475-485) reports it as extra.
- Expected: `(("V-WRITE-SCOPE", "major"),)`. Basis: T:155 defines a grant as the seat's "own root"; T:172 binds the grant to the item name; P:2 requires "exact per-item auditor authorization".
- Predicted production trace (not executed):
  - T:164-165: no placeholder.
  - T:166-169: match.
  - T:171: path `/var/tmp/souji-r19w2-Neighbor`.
  - T:172: fails, because `-Seat` is required.
  - T:175-185: CLONES does not match.
  - Context does not match.
  - T:186 returns `""`.
  - T:285-289 yields `V-WRITE-SCOPE`, and T:353-354 maps it to major.
  - Observed `(("V-WRITE-SCOPE","major"),)` equals expected: PASS.
- Mutant it catches: the name group at T:172 is loosened (for example, `re.escape(name)` becomes `[\w.-]+`), or T:172-173 is removed. Then T:174 returns the Neighbor root, T:287 `_under` is True, nothing is flagged, and `() ≠ expected`: FAIL.
- Design constraints:
  - Do not use `<YourName>`. The placeholder becomes `Seat` (T:164-165), so the same mutant would refuse the write and the case would pass.
  - The case is self-non-vacuous. A zero-call or unaudited write yields `()`, which is not the expected value, so it FAILs. Unlike the positive, it cannot pass vacuously.
- Why this one: it targets name binding, which neither the oracle nor the selftest exercises (section 5C).
- Noted, not proposed:
  - Other slot under the literal. A realistic slot-broadening mutant either breaks the positive (`_under` needs the `/` boundary, T:195) or is a `/var/tmp` grant that `scratch-foreign-slot` (F:194-195) already fails.
  - Sibling prefix `…-Seat2/`. Refused by T:195 and covered by selftest T:512, but not by the independent oracle.
  - Denied literal `… is not authorized`. Refused by the fullmatch at T:166-169, but untested for scratch. The DELIVER analog is F:163-165.

## 7. Other observations

- The T:169 tail is untested (section 5A).
- The T:49-51 docs omit `Scratch only under` (section 5A).
- The F:8-9 versus F:55-61 mismatch (section 5B).
- The positive's expectation is an implicit default (F:133), while the twin states its expectation explicitly. Readability only.
- The optional r19 lesson was not opened (section 0).

## 8. Checks for L1 (not run here)

- If section 6 is accepted: add the case and its ID at F:45, then run the fixture once against the selected tool. Expected result: the new case PASSes and no existing case changes.
- Optional mutant check in an L1-owned clone: loosen T:172 and run the fixture. The trace predicts that `scratch-r19w2-literal-foreign-name` FAILs while the positive still PASSes. That is why the foreign-name case is needed.
