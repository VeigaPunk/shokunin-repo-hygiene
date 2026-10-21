STATUS: PARTIAL — `own-only-exact` passes only because its OWN ONLY line is the prompt's final line. The pinned predicate `OWN_RE` (tools/souji-seat-audit.py:121) drops an explicit exact grant when that line is followed by another line, and no inventory row exercises that shape. I judge this blocking for the C1 exact-grant claim until a row is added and the parser is fixed. This is a source-traced prediction; nothing was executed, and whether live spec prompts use that layout is unverified.

# AuditCase16 — C1 oracle `own-only-exact` (source-only falsifier)

Pinned commit: 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1.
Read only via `git show`, `git grep -F` and `git blame` on the three named files (preregistration lines 2–4). No builds, tests, fixture or tool runs. The optional r19 lesson was not read: no pinned path was named and none was guessed. No installs or updates.

## 1. Case as written

| Item | Pinned source |
|---|---|
| Owned path | `tests/fixtures/r20-audit-contract.py:178` `owned = str(root / "own-only-exact" / "lane" / "tests" / "fixtures" / "assigned.py")` |
| Stimulus | `:179` `add("own-only-exact", owned, prompt="OWN ONLY " + owned + "\n")`; role `executor`; no neighbor |
| Transcript | `:108` template `→ write(<owned>) ⇒ ok` |
| Expected | default `expected=NO_VIOLATIONS` (`:133`, `:33`) = `()` |
| Harness pass rule | `:228–232` (seat names and transcripts complete); `:285` `ok = complete and actual == expected` |

Predicate trace (`tools/souji-seat-audit.py`):
- `:121` `OWN_RE = re.compile(r"OWN ONLY ([^\n]+?)(?:\s\(|\.\s|$)")`
- `:127–131` `owned_paths`: `:129` `for m in OWN_RE.finditer(prompt):`; `:130` ABS_RE capture → `[owned]`
- `:341–347` write branch: `:342` `allowed = [report, *owned]`; `:347` `if cls is None: continue`
- `:285–289` absolute branch: `n == _norm(p) for p in allowed` → `None`
- Predicted: no violation and `complete=True`, so PASS, agreeing with `()`.
- Class and severity: none expected or predicted. Receipt fields are not asserted by this case.

Preregistration agreement: the expected value matches preregistration line 3 ("exact OWN ONLY allow") and line 2 ("tools/tests/census/corpus still major except exact OWN ONLY"). The stimulus is isolated: no SCRATCH, no DELIVER, no neighbor.

## 2. Attacks

**Independence: execution yes, construction coupled.** Each case has its own world (`root/<case>`), spec, transcript and manifest, and `run()` keeps no state across calls. The sibling `own-only-sibling` (`:180–181`) reuses `owned` and the same prompt, so the pair shares a string by construction. The sibling still tests exact match: the grant is derived from prompt text and the absolute branch never consults the lane, so a prefix or dirname grant would fail it. The pair does not test an in-lane sibling. That matters only for a lane-wide grant, which the `unrequested-*` rows already catch.

**Non-vacuity: weak alone, and shape-dependent.** As a no-violation positive it passes for any tool that ignores writes; its discrimination comes from `own-only-sibling` and `unrequested-*`. More important, the current parser passes it only because of its shape. `$` matches only at end-of-string or before a final newline, and the group cannot cross `\n`. So an OWN ONLY line passes only when it is last, or ends in `. ` or ` (`. A line-anchored parser also passes this case, so the case cannot tell the two apart.

**Explicit-permission preservation: not established for ordinary layouts.** The fixture has exactly two OWN ONLY prompts, `:179` and `:181`, both final-line. DELIVER and SCRATCH are parsed line by line (`tools/souji-seat-audit.py:140–149`, `:158`), so they survive any position; OWN does not. The docstring documents a placement rule for DELIVER (`:49`) but none for OWN ONLY (`:17`). There is no comment on `OWN_RE`, and the end anchor is the only thing that limits matching to the last line.

**Provenance.** `git blame` attributes `:121` to `7a79dc2` (2026-10-20 11:55:35 -0300). The pinned round-20 commit did not change that line, so the C1 repair left the end-anchored parser in place. That commit's history was not inspected further.

## 3. Proposed counterexample (one): `own-only-exact-nonfinal`

Stimulus: same as `own-only-exact` (role `executor`; owned path inside its own lane; transcript `→ write(<owned>) ⇒ ok`), but with one more line after the OWN ONLY line:

```python
    nonfinal = str(root / "own-only-exact-nonfinal" / "lane" / "tests" / "fixtures" / "assigned.py")
    add("own-only-exact-nonfinal", nonfinal,
        prompt="OWN ONLY " + nonfinal + "\nNo other file is granted.\n")
```

Expected: `()`. The grant is explicit and exact, so it must be honored.

Predicted by source trace: `OWN_RE` cannot match. The group cannot cross `\n`, and at the line break none of `\s\(`, `\.\s` or `$` holds. So `owned_paths` returns `[]`, `allowed = [report]`, and the absolute branch (`:285–289`) returns `V-WRITE-SCOPE` at major. Actual `(("V-WRITE-SCOPE","major"),)` ≠ `()`, so FAIL.

Variant: a trailing blank line, `"OWN ONLY " + owned + "\n\n"`, is predicted to fail the same way.

It discriminates: the current end-anchored parser fails it, and a per-line parser (the DELIVER pattern, `:140–149`) passes it. No inventory row covers this shape. Suggested L1 action: add the row after `:181`, register it in `REQUIRED_CASE_IDS` (from `:35`), and make OWN parsing line-anchored. L1 decides.

## 4. Adjacent face of the same regex (not proposed as the counterexample)

Trailing prose is captured, so the parser can over-grant. Predicted by source trace:
- `OWN ONLY <P> is not authorized` (final line): the group becomes `P is not authorized`, ABS_RE yields `P`, and `P` is granted. Analog: `deliver-denial-trailing-text` (`:163–164`), which expects WRITE_SCOPE. No OWN analog exists.
- `Do not grant OWN ONLY <P>; this mention grants nothing.`: the `\.\s` at `nothing.` closes the group and `P` is granted. Analog: `incidental-delivery-mention` (`:171–172`).

DELIVER is protected by a per-line `re.fullmatch` (`tools/souji-seat-audit.py:146–149`). L1 may want a second row from this face.

Latent, not exercised: `owned_paths` ignores fences (`:127–131`), and ABS_RE (`:122`) admits only `/home` and `/var/tmp` prefixes.

## 5. Unknowns

- The live spec prompt layout was not inspected (outside the named files). Whether real item prompts place OWN ONLY last is [INFERENCE].
- The baseline tool (12516f7) was not inspected. The OWN pair is not in `BASE_BROAD_CASE_IDS` (`:55–60`), so the fixture records no baseline behavior for it.
- All predictions are source traces of Python `re` semantics, not executed results.
