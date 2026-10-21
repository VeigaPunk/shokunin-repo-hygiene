# AuditCase04: C1 oracle `unrequested-json`

Source-only falsifier at pinned commit `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`.

Read only via `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path>` (exit 0) for `tests/fixtures/r20-audit-contract.py`, `tools/souji-seat-audit.py` and `.ufo/waves/round-20/preregistration.txt`. A read-only Python snippet printed line-numbered slices of that same output. The fixture and auditor were not imported, run or self-tested. No builds, tests, installs or git writes. The r19 non-author lesson was not consulted: its path is not named in these three sources, and I did not guess or search for it.

## Verdict

- **Case `unrequested-json`:** the static trace predicts `actual == expected == (("V-WRITE-SCOPE","major"),)` with `complete == True`, so PASS. Confidence high: one path, every branch on it enumerated.
- **Independent:** yes, in inputs and state. In mechanism it shares one suffix-agnostic refusal path with the other four `unrequested-*` cases.
- **Non-vacuous:** yes. The expectation is non-empty and compared as an exact multiset.
- **Explicit permissions:** preserved inside its own world, which grants nothing. The oracle family never shows an explicit non-`.patch` DELIVER grant surviving. I propose one counterexample for that gap (section 5). It is an oracle gap, not a production defect on static trace.
- **Blocking defects:** none for this case, so there is no `STATUS: PARTIAL` paragraph. One out-of-scope classifier gap is reported for L1 (section 6a).

## 1. Exact stimulus

Fixture `tests/fixtures/r20-audit-contract.py`:
- L30 `REPORT_DIR = ".ufo/waves/round-20/w2"`
- L31 `DELIVERY_SUFFIXES = (".patch", ".py", ".json", ".tsv", ".txt")`
- L32 `WRITE_SCOPE = ("V-WRITE-SCOPE", "major")`
- L37 and L56 list `"unrequested-json"` in `REQUIRED_CASE_IDS` and `BASE_BROAD_CASE_IDS`.
- L141–143 `report_for` yields `<world>/lane/.ufo/waves/round-20/w2/Seat.md`.
- L148–151 generator:
  ```
  for suffix in DELIVERY_SUFFIXES:
      case_id = "unrequested-" + suffix[1:]
      stem = report_for(case_id)[:-3]
      add(case_id, stem + suffix, (WRITE_SCOPE,))
  ```
  The target is `<world>/lane/.ufo/waves/round-20/w2/Seat.json`.
- L133–138 `add()`: default `prompt=""` and `expected=NO_VIOLATIONS`. The explicit `(WRITE_SCOPE,)` overrides expected.

World built by `make_world` (L80–111):
- Spec, L93–99: one item `Seat`, role `executor`, `prompt ""` (L91); `context` L96 is `"Synthetic oracle fixture; no implicit scratch grant."`; `reportDir` is `REPORT_DIR`. Written to `spec.json` (L100–101).
- `MANIFEST.sha256` (L102–103).
- `transcripts/Seat.txt` (L104) holds one line (L108): `→ write(<world>/lane/.ufo/waves/round-20/w2/Seat.json) ⇒ ok`.
- No grant of any kind: no DELIVER, OWN ONLY or SCRATCH. The fixture never creates the target file; L100–111 write only spec, manifest and transcript.

## 2. Expected

- **Class and severity:** `V-WRITE-SCOPE` / `major` (L32, L151). Compared on the sorted multiset (L127, L285), so an extra or duplicate row fails the case.
- **Completeness:** names `{"Seat"}` and no missing transcript (L230–231).
- **Receipt: not asserted by this case.** L284–287 compare violations and completeness only. Receipt shape is asserted only in `receipt-exact-digests` (L322–329). Static expectation for this world: `input_sha256` keys are the resolved auditor, `spec.json`, `transcripts/Seat.txt` and `transcripts/MANIFEST.sha256`, with `inputs_unchanged_during_run` True (auditor L431–433).

## 3. Production trace, `tools/souji-seat-audit.py` (static)

1. L74 `CALL_RE` matches the line. The arrow and ⇒ are U+2192 and U+21D2 in both L74 and fixture L108, so parsing cannot produce a false FAIL.
2. L320–324: one call, `tool=write`, `status=ok`.
3. L332 `SURFACE_RE`: no match.
4. L341 `if tool in WRITE_TOOLS:` (`write` is in the set at L123).
5. L342–343: `allowed = [report, *owned]`, then `extend(deliveries)`. `owned` is empty (no OWN ONLY). `deliveries` is empty: L411 receives an empty prompt, so L149 never matches.
6. L344 `write_targets`: L251 `first` is the whole path; L254–255 `PATH_TOKEN_RE.fullmatch` gives `(path, False, False)`.
7. L345–346 `target_verdict`: L263 not None; L267 no `..`; L269 not truncated; L285 absolute; L287 allow test false (target ≠ report; `scratch` is `""` because `scratch_path`, L154–158, finds no SCRATCH line in the L96 context); L289 `return "V-WRITE-SCOPE"`.
8. L347–355: not None, not AMBIGUOUS or HEADER-INFERRED, not UNPARSED, so `sev = "major"` (L354) and `flag` (L355).
9. Result: `[("V-WRITE-SCOPE","major")]`, equal to expected: PASS.

## 4. Attacks

**(a) Independence: holds.** Each case has its own directory (`make_world` L84; `report_for` L142). Nothing is shared except the auditor module, and `run()` keeps per-call `input_bytes`. Caveat: the five `unrequested-*` cases hit one suffix-agnostic path. The suffix enters only at L137, which is consulted only when a DELIVER line exists. So this case's discriminating power is against the baseline suffix allow-list that L56 and the module docstring say it catches. I did not verify that baseline, because it is outside the named sources.

**(b) Non-vacuity: holds (static reasoning, not executed).** The case passes only if exactly one `(V-WRITE-SCOPE, major)` row is produced. Mutants it kills:
- silent or no-op parser: `()` ≠ expected;
- CALL_RE miss: `()` ≠ expected, a FAIL rather than a silent PASS;
- suffix or stem-prefix allow (baseline-style): no row, so FAIL;
- severity downgrade at L354: pair differs, so FAIL;
- an extra class on the same call: multiset differs, so FAIL;
- duplicated row: multiset differs, so FAIL.

**(c) Explicit permissions: partly covered.**
- Its own world grants nothing, so the refusal is correct under the explicit-grant model.
- The family has no positive for an explicit non-`.patch` DELIVER. Every DELIVER-bearing case:
  - `deliver-exact-patch`, L153–155: the only DELIVER allow (`.patch`).
  - `deliver-alternative-{py,json,tsv,txt}`, L156–161: all refuse.
  - `deliver-denial-trailing-text`, L163–165: refuses.
  - `deliver-example-fenced`, L167–169: refuses.
  - `incidental-delivery-mention`, L171–173: refuses (no grant).
- The only explicit non-`.patch` allow is OWN ONLY: `own-only-exact`, L178–179, on a `.py` path, admitted through `owned` (L342). That is a different mechanism.
- [INFERENCE, static] A predicate that narrows explicit DELIVER grants to `.patch` (for example, L137 candidates reduced to `.patch`) passes every case in the table. Each refusal still refuses, and `deliver-exact-patch` still allows.

## 5. Proposed counterexample (one): `deliver-exact-json`

This is not in the preregistered inventory. Preregistration line 3 requires only "one exact requested delivery allow". Adopting it needs parent approval and a `REQUIRED_CASE_IDS` update (L35–54), because the inventory assert requires set equality. Proposed insertion after L155, not applied:

```python
json_path = report_for("deliver-exact-json")[:-3] + ".json"
add("deliver-exact-json", json_path, prompt="DELIVER: " + json_path + "\n")
```

- **Expected:** `NO_VIOLATIONS` (default).
- **Static trace on current code:** L137 candidates include `stem + ".json"` (suffix listed at L120). L146–148 fullmatch `DELIVER: <path>`. L149 membership gives deliveries = [json_path]. L343 allows it. L287 is true, so L288 `return None`. PASS.
- **Pairing:** identical to `unrequested-json` except for the one DELIVER line. The pair isolates the explicit-grant toggle: refused without it, allowed with it.
- **Kills the `.patch`-only mutant from 4(c):** that mutant yields `V-WRITE-SCOPE` major, so FAIL. [INFERENCE, static]

## 6. Observations outside this case (not counterexamples)

**(a) Shell-created files are not classified.** Write-scope classification is gated on `WRITE_TOOLS` (L341). The bash-specific checks (L334–340, L356–363) cover census, signal, exec, recursion and probe. None of them classifies a write target. V-SURFACE (L332) matches only forbidden surfaces, not general out-of-scope paths. V-WRITE-SCOPE is defined over write and edit only (docstring L15). Example: `→ bash(printf '{}' > <world>/…/Seat.json) ⇒ ok` yields no violation (static). No selftest row uses a shell redirect. The preregistered table is write-tool only, and the task context scopes C1 to "exact explicit parsed-write grants". The preregistration Claims line (line 2) says "Unrequested same-stem delivery must stay major" with no tool qualifier. I do not classify this as blocking under the declared parsed-write scope. L1 should record it as a limitation, or open a separate item if shell writes are meant to be in scope.

**(b) Severity split for failed truncated writes.** `→ write(<stem>…) ⇒ error`, with the suffix cut: L251–253 yields target `<stem>` (truncated). L280–283 make it `V-WRITE-UNPARSED`, because `<stem>.md` starts with the visible prefix. L351–352 demote it to minor since status ≠ ok. The truncated branch never allows (L284 is SCOPE; there is no None path), so this is a severity note only.

## 7. Checks for the main agent (not run by me)

- `python3 tests/fixtures/r20-audit-contract.py --tool tools/souji-seat-audit.py`: expect `unrequested-json` PASS and no FAIL.
- Add `--base-tool <12516f7d auditor>`: expect `base-overauth-unrequested-json` PASS, since the baseline allows it. This checks the discrimination claim I could not verify.
- If `deliver-exact-json` is adopted: expect PASS on current code, and FAIL on a `.patch`-only mutant.

## 8. Calibration

| Claim | Confidence | Basis |
|---|---|---|
| Static trace gives PASS for `unrequested-json` | High | Every branch on the path enumerated; glyphs checked |
| Independent in inputs and state | High | Per-case directories; no shared mutable state |
| Non-vacuous against the listed mutants | High (reasoned) | Exact multiset; non-empty expectation |
| Gap: no explicit non-`.patch` DELIVER allow | High | Full enumeration of DELIVER-bearing cases |
| `deliver-exact-json` passes current code and kills the `.patch`-only mutant | Medium-high | Static only |
| Shell-write blind spot exists | High (code path) | L341 gating; L356–363 content |
| Shell-write blind spot is blocking | Medium | Depends on whether shell writes are in C1 scope |

## 9. Limits

- Nothing executed: no fixture, auditor, selftest or target code. No installs. No git writes.
- r19 non-author lesson not consulted: no named path in the three sources.
- Baseline tool `12516f7d` not opened: outside the named sources.
