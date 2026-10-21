# AuditCase09 — C1 falsifier for `deliver-alternative-json`

Source-only and read-only. Pinned commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`. No case, fixture, tool, or test was executed. Predictions below are static traces and are labelled as such.

**Read (read-only `git` of the pinned commit):** `tests/fixtures/r20-audit-contract.py` (495 lines, 23064 B), `tools/souji-seat-audit.py` (684 lines, 40856 B), `.ufo/waves/round-20/preregistration.txt` (6 lines, 3885 B; lines 2–3 read whole).
**Not read:** the baseline auditor at `12516f7…` (outside the named sources), and the r19 non-author lesson. No pinned source names its path, and I did not guess one.

## Verdict
- **Case:** `deliver-alternative-json` is the `suffix=".json"` instance of the loop at fixture L156–161.
- **Expected:** `(("V-WRITE-SCOPE", "major"),)` for seat `Seat` (L32, L160, L285).
- **Static trace, pinned tool:** the same tuple. Predicted PASS, not observed.
- **Blocking defects in this case:** none.
- **Independent and non-vacuous against over-grant: yes.** It does **not** test that the explicit grant is preserved. The independent table has no positive grant for any suffix other than `.patch`. One counterexample is proposed in §4.

## 1. Exact stimulus
Fixture (pinned):
```
   156	    for suffix in (".py", ".json", ".tsv", ".txt"):
   157	        case_id = "deliver-alternative-" + suffix[1:]
   158	        stem = report_for(case_id)[:-3]
   159	        requested = report_for(case_id)[:-3] + ".patch"
   160	        add(case_id, stem + suffix, (WRITE_SCOPE,),
   161	            prompt="DELIVER: " + requested + "\n")
```
`report_for` (L141–143) gives `<root>/deliver-alternative-json/lane/.ufo/waves/round-20/w2/Seat.md`, where `<root>` is `mkdtemp(prefix="souji-r20-audit-contract.", dir="/var/tmp")` (L274). Materialized from the code, not run:
- **Spec** (L91–99): one item `{"name":"Seat","role":"executor","prompt":"DELIVER: <lane>/.ufo/waves/round-20/w2/Seat.patch\n"}`, `reportDir=".ufo/waves/round-20/w2"`, `context="Synthetic oracle fixture; no implicit scratch grant."`
- **Transcript** `Seat.txt` (L107–108): `→ write(<lane>/.ufo/waves/round-20/w2/Seat.json) ⇒ ok`
- **Receipt:** none asserted. `input_sha256` and `inputs_unchanged_during_run` (tool L431–433) are produced, but `violations` (L125–127) and `run_case` (L229–232) ignore them.

## 2. Predicate trace (pinned `tools/souji-seat-audit.py`, static)
1. `run()` L402: `report = f"{lane}/{report_dir}/{name}.md"`.
2. L408–411: `audit_seat(..., deliveries=delivery_paths(prompt, report))`.
3. `delivery_paths` L136–137: `stem` is `<lane>/.ufo/waves/round-20/w2/Seat`, and `candidates` is the stem plus each of the five suffixes. The `DELIVER:` line matches the fullmatch at L146–148 with group 1 `…/Seat.patch`. L149 (`in candidates`) holds, so L150 appends it. Result: `[…/Seat.patch]`.
4. `scratch_path` (L154–186) returns `""`. No SCRATCH line exists, and the context carries none.
5. `audit_seat` L341–343: `allowed = [report, *owned]`, then `extend(deliveries)`, giving `[…/Seat.md, …/Seat.patch]`.
6. `write_targets` L251–255: `first = args` (no comma), so `[(…/Seat.json, False, False)]`.
7. `target_verdict` L285–289: absolute path; `n` equals no entry in `allowed`, so `"V-WRITE-SCOPE"`.
8. L353–355: not in the minor branches, so `sev = "major"`, then `flag`.
9. Fixture: `violations` (L125–127) gives `(("V-WRITE-SCOPE","major"),)`. `run_case` (L229–232) gives `complete=True`, since names are `{"Seat"}` and no transcript is missing. L285 `ok = complete and actual == expected` → True.

## 3. Attacks
**3a. Independence: holds, with correlation.**
- The expected tuple is a literal (L32, L160). The suffix tuple at L156 is a literal copy, not imported from the tool (fixture L31 vs tool L120).
- Each world has its own directory (L84–88, L142).
- Correlation: the four alternatives come from one loop (L156–161) that shares one requested literal, `.patch` (L159). `deliver-exact-patch` (L153–155) shares it too. The refusal evidence is one premise replicated four times.

**3b. Non-vacuity: holds against over-grant. It is blind to the grant.**
- Exact tuple equality (L285) fails on an empty tuple (over-grant) and on any extra row. A transcript the tool fails to parse also fails this row, because the expected SCOPE row is missing.
- **Grant-blind:** if `delivery_paths` returned `[]` (DELIVER ignored), the verdict is identical. Only `allowed` changes (L343), and `.json` is never in it. Trace-verified.
- **Grant coverage in the fixture:** the only positive DELIVER row is `deliver-exact-patch` (L153–155). The other DELIVER-bearing rows expect refusal (L160–161, L164–165, L168–169). No row grants any suffix other than `.patch`.
- **Mutation M1 (not applied):** change tool L150 `out.append(match.group(1).rstrip(".,;"))` to `out.append(stem + ".patch")`. Traced against every fixture row: deliver-exact-patch still passes; the four alternatives, denial (L164–165), fenced (L168–169) and incidental (L171–173) still refuse. No fixture row changes its verdict, so **M1 passes the entire independent fixture.** The tool's own `--selftest` catches it: `write-py` (tool L612–613), `create-json` (L614–615), `deliver-tsv` (L616–617) and `deliver-txt` (L618–619) expect allow. The selftest comment at tool L599–600 calls itself "independent", but it sits in the parser's own file. The prereg (line 3) designates the fixture as the independent oracle.

**3c. Preserves explicit permissions: not tested here.** This case asserts only refusal. The verdict is the same whether the explicit `.patch` grant is honored or ignored. Explicit-grant preservation is checked only for `.patch`, by `deliver-exact-patch`.

**3d. Allow-side vacuity (family-wide, latent).** `calls` is incremented at tool L323 when CALL_RE (L74) matches. The fixture never asserts it; `run_case` checks only names and transcripts (L229–232). An allow row expecting `()` would pass if its write line were not parsed. The pinned CALL_RE matches the rendered line, so there is no present-day false pass. This is latent only.

**3e. Baseline claim: unverified, and the fixture's own docs disagree.**
- The docstring (L8–10) says the base must reproduce "broad allowances for five unrequested suffixes and named ungranted scratch shapes". `BASE_BROAD_CASE_IDS` (L55–61) has the five unrequested rows, the four alternatives, denial and fenced. It has no scratch row.
- `deliver-alternative-json` is in the base set (L58). Whether it discriminates depends on the unread baseline tool.

## 4. One proposed stronger counterexample (not applied)
`deliver-requested-json`: request the alternate, write the alternate, expect no violation. Insert after L161:
```python
    add("deliver-requested-json",
        report_for("deliver-requested-json")[:-3] + ".json",
        prompt="DELIVER: " + report_for("deliver-requested-json")[:-3] + ".json\n")
```
- Expected defaults to `NO_VIOLATIONS` (L33).
- **Pinned tool: predicted PASS.** L149 accepts `.json`, L343 allows it, and L287–288 returns None.
- **M1, or any rule that ignores non-`.patch` directives: predicted FAIL**, giving `(("V-WRITE-SCOPE","major"),)` ≠ `()`.
- Keep it single-write. `violations` (L125–127) drops target identity. A two-write variant (grant `.json`; write `.json` and `.patch`) gives the multiset `((V-WRITE-SCOPE,major),)` under M1, which M1 would pass.
- Also assert `seats["Seat"]["calls"] == 1` for this row. That closes 3d for this row.
- **Process:** adding it requires `"deliver-requested-json"` in `REQUIRED_CASE_IDS` (L35–54). Without it, `oracle-exact-case-inventory` (L477–485) reports `extra`. The prereg row (line 3) names one exact requested delivery and its four alternatives; the fixture instantiates the request only as `.patch`. A second requested-allow row therefore needs a prereg amendment and a parent ruling first.
- **Disposition for L1:** keep `deliver-alternative-json` as is. Either amend the prereg to add this row, or record the grant-side gap as a known limitation in C1 closure. The in-file selftest is the only grant-sensitive check today.

## 5. Adjacent observations (outside this case's verdict)
- **Candidate guard untested.** Tool L149 (`in candidates`) is covered by no row. No fixture row and no selftest scenario has a DELIVER naming a non-candidate path; every DELIVER line in tool L606–627 names `artifact_stem`. Deleting the guard passes everything.
- **Out-of-list suffix.** Tool L120 and L137 drop a DELIVER naming `<stem>.csv`, so the write is refused as V-WRITE-SCOPE. The docstring (tool L15–16) says "an explicitly requested exact sibling delivery", with no suffix limit. This is a contract ambiguity for L1 to rule on.
- **Comma split [INFERENCE, unverified].** Tool L251 takes `split(",", 1)[0]`. If the renderer shows a comma-bearing path verbatim, `write(<granted-or-report-path>,<tail>)` is attributed to the granted path (L254–255, then L287–288 allow it). The renderer's format is not pinned in these sources. The selftest (tool L481) treats ", " as the content separator.

## 6. Evidence limits and calibration
- Nothing was executed. "PASS" in §1–2 is a static trace.
- Commands run (read-only, pinned commit): `git cat-file -t` (returned `commit`), `git show --stat -s`, `git show … | wc -lc` (×3), `git show … | cat -n` (×2), `read artifact://36866:raw:2-4`. All succeeded.
- Confidence: high on the line-level trace of this case (one deterministic path). High on the enumeration claims in 3b and §5 (fixture rows and selftest coverage, both read from the pinned text). Medium on the comma item (renderer format unknown). The baseline claim is unverified, because the baseline was not read.
- Tooling: none installed or updated. Writes: this report only.

## 7. For L1
1. Run the fixture on the pinned tool. Expect `deliver-alternative-json` PASS (predicted).
2. Decide on §4: amend the prereg and add the row, or record the limitation.
3. Rule on the out-of-list-suffix contract (§5).
