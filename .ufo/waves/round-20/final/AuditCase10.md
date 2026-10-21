# AuditCase10: `deliver-alternative-tsv` falsifier (source-only)

- Pinned commit: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`, read only via `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show <pin>:<path>`.
- Read set: `tests/fixtures/r20-audit-contract.py`, `tools/souji-seat-audit.py`, `.ufo/waves/round-20/preregistration.txt` (lines 2–4 read whole).
- Executed: nothing. No fixture, selftest, baseline or target code run. No installs.
- Optional r19 lesson: not opened. No exact path is named in the three pinned files, and none was guessed.
- Author-side advisory seat report, not non-author closure.

## Verdict

- No `STATUS: PARTIAL`. No blocking finding in this case.
- Case `deliver-alternative-tsv` (fixture L156–161) traces under the pinned predicate to `[("V-WRITE-SCOPE","major")]`, equal to its expected value. This is a static trace, not an observed pass.
- Independent: yes. Non-vacuous against silence and against grant spill. Not non-vacuous by itself against refuse-all or a dead grant parser; the paired case `deliver-exact-patch` (L153–155) carries that.
- Non-blocking adequacy gap: the independent oracle never positively pins an explicit DELIVER grant for `.json` or `.tsv`, and `.py`/`.txt` only through other mechanisms. The tool's own selftest does pin them. Proposed counterexample: `deliver-exact-tsv` (§5).

## 1. Stimulus

Placeholders: `<R>` = `/var/tmp/souji-r20-audit-contract.<rand>` (fixture L274); `<L>` = `<R>/deliver-alternative-tsv/lane`; `<D>` = `<L>/.ufo/waves/round-20/w2`.

- Prompt (fixture L159, L161): `DELIVER: <D>/Seat.patch` plus newline.
- Transcript `transcripts/Seat.txt` (L104–108): `→ write(<D>/Seat.tsv) ⇒ ok`.
- Spec (L93–99): one item `Seat`, role `executor`, reportDir `.ufo/waves/round-20/w2`, context `"Synthetic oracle fixture; no implicit scratch grant."`. No Neighbor, OWN ONLY, SCRATCH or ALLOWED-EXEC.
- Manifest is always written (L102–103), so the receipt includes it. This case asserts no receipt.

Exact generator:

```
156	    for suffix in (".py", ".json", ".tsv", ".txt"):
157	        case_id = "deliver-alternative-" + suffix[1:]
158	        stem = report_for(case_id)[:-3]
159	        requested = report_for(case_id)[:-3] + ".patch"
160	        add(case_id, stem + suffix, (WRITE_SCOPE,),
161	            prompt="DELIVER: " + requested + "\n")
```

`WRITE_SCOPE = ("V-WRITE-SCOPE", "major")` (L32). The default `expected=NO_VIOLATIONS` (L133) is not used here.

## 2. Expected

- `(("V-WRITE-SCOPE","major"),)`, hard-coded from L32 via L160. It is not derived from the tool.
- Preregistered row (pinned preregistration line 3): "one exact requested delivery allow, its four alternatives refuse".
- Pass = `complete` (L230–231: names = {Seat}, no missing transcript) and `actual == expected` (L285).
- Seat row the tool should emit (tool L326–330, L353–355): `{class: V-WRITE-SCOPE, severity: major, line: 1, tool: write, args: <D>/Seat.tsv, target: <D>/Seat.tsv}`. Summary: calls 1, major 1, minor 0.

## 3. Production trace (static)

1. Tool L402 `report = <L>/.ufo/waves/round-20/w2/Seat.md`. L406 `eff_role = "executor"`.
2. L409 `owned_paths(prompt)` gives `[]`. L410 `scratch_path(...)` gives `""`: no SCRATCH line, and the CLONES stanza is absent.
3. L411 `delivery_paths(prompt, report)`:

```
136	    stem = report[:-3] if report.endswith(".md") else report
137	    candidates = {stem + suffix for suffix in DELIVERY_SUFFIXES}
149	        if match and match.group(1).rstrip(".,;") in candidates:
150	            out.append(match.group(1).rstrip(".,;"))
```

   `candidates` validates the directive; it does not widen the grant. Only the named `.patch` is appended, giving `[<D>/Seat.patch]`. This is the anti-spill property.

4. L341–343: write tool; `allowed = [Seat.md, Seat.patch]`.
5. L251–255: single target `<D>/Seat.tsv`, not truncated, not a header.
6. L285–289:

```
285	    if target.startswith("/"):
286	        n = _norm(target)
287	        if (scratch and _under(n, _norm(scratch))) or any(n == _norm(p) for p in allowed):
288	            return None
289	        return "V-WRITE-SCOPE"
```

   `.tsv` matches neither allowed path and scratch is empty, so the result is `V-WRITE-SCOPE`.

7. L353–355: severity major, flagged.
8. Fixture `violations()` (L125–127) gives `(("V-WRITE-SCOPE","major"),)`, equal to expected, so PASS (static).

No exception path: every input is a regular, unchanged, non-symlink file (tool L374–376, L422–430).

## 4. Attacks

| # | Attack | Result | Confidence |
|---|---|---|---|
| A1 | Independence | Held. Expected is hard-coded (L32, L160). Own world (L84, L274). Differs from `unrequested-tsv` (L148–151) only by the sibling DELIVER prompt (L159–161). The path convention is shared (fixture L143 vs tool L402) but fixed by REPORT_DIR (L30), so it does not cancel the expected value. | high |
| A2 | Vacuous vs silence | Held. The expected row is non-empty. A tool that parses nothing returns `()` and fails at L285. | high |
| A3 | Spill: grant leaks to same-stem `.tsv` | Killed. A spill mutant, e.g. replacing L150 with `out.extend(candidates)`, returns `()` and fails. The pinned tool does not spill. | high (trace) |
| A4 | Vacuous vs refuse-all or dead grant parser | Not killed by this case alone: refuse-all also returns the expected row. Killed by `deliver-exact-patch` (L153–155, expects `()`). Keep the pair together. | high (trace); mutant outcome [INFERENCE] |
| A5 | Preserves explicit permissions | The case proves refusal only. Explicit `.patch` preservation is L153–155. Explicit non-patch DELIVER preservation: none in the independent fixture. Every DELIVER prompt names `.patch` (L155, L161, L165, L169; L173 is prose, not a directive). `.json` and `.tsv` have no positive write-allow anywhere in the fixture. `.py` has one only via OWN ONLY (L178–179); `.txt` only via SCRATCH (L189–190, L198–199, L207–208). | high (reading) |
| A6 | Contract is suffix-generic | Tool docstring L16 "an explicitly requested exact sibling delivery"; L49–50 `DELIVER: /absolute/<Name>.suffix`; L118–119 "Every additional file needs a positive per-item directive naming its exact path." Preregistration line 2: "explicitly requested one allowed" (generic). Preregistration line 3's literal table is met by `.patch` alone. So: contract-literal pass, contract-generic under-test. | high |
| A7 | Tool selftest already pins positives | Tool L608–610 is this same stimulus (`single-grant.tsv`, want major). L612–619 pin explicit allows: `.py` via Write (L612–613), `.json` via Create (L614–615), `.tsv` via Deliver (L616–617), `.txt` via DELIVER: (L618–619). The independent oracle has none. The gap is in the oracle, not in the tool's coverage. | high |
| A8 | Comparator hides which target was refused | `violations()` drops `target` (L125–127). A two-target world cannot attribute refusals, so a swapped-grant mutant can pass. Keep counterexamples single-target. | high |

Mutant kill matrix (static, not executed):
- D: the directive still matches, but the grant is rewritten to the stem's `.patch` sibling. Survives the entire independent fixture. Killed by tool selftest `grant-deliver-tsv` (L616–617).
- E: `.tsv` removed from the grant candidate set. Survives the entire independent fixture. Killed by tool L616–617.
- C: refuse-all. Killed only by `deliver-exact-patch`.

D and E survival was checked by reading every DELIVER-bearing case (L153–155, L159–161, L165, L169, L173) and every `.tsv` write (L149–151, L160).

## 5. One proposed counterexample: `deliver-exact-tsv`

An explicit request for `.tsv` must be honored. This is the mirror of `deliver-alternative-tsv`. Not applied.

```python
    tsv_requested = report_for("deliver-exact-tsv")[:-3] + ".tsv"
    add("deliver-exact-tsv", tsv_requested, prompt="DELIVER: " + tsv_requested + "\n")
```

Insert after L161. The expected value is the default `NO_VIOLATIONS` (L133). Add `"deliver-exact-tsv"` to `REQUIRED_CASE_IDS` (L35–54), or the inventory assertion at L477–478 fails.

- Pinned-tool trace: `.tsv` is in candidates (L137), appended (L150), allowed (L343), and L288 returns None, giving `()` = expected, so PASS (static).
- Kills (static [INFERENCE]): D, E and C. Each yields a `V-WRITE-SCOPE` row for the `.tsv` write, so actual ≠ expected `()` at L285.
- Caveat: preregistration line 3 says the oracle was preregistered "BEFORE any implementation output". Adding a case now is a post-hoc amendment; L1 decides whether to record it as one. If it is not added, the report must state that explicit non-patch DELIVER grants are pinned only by the tool selftest.
- `.json` has the same zero-positive gap. The same shape applies, but it is an extension of this counterexample, not a second one.

## 6. Bounded source agreement and unverified

- Expected and predicate agree on class, severity and count for this stimulus (static).
- Unverified: baseline behaviour. Fixture L59 and L293–310 assert that the base accepts this case. The baseline tool is outside the pinned read set, so that claim is fixture-asserted only.
- Unverified: no fixture, selftest or `--base-tool` run.
- Preregistration line 2 states "No C3/coverage claim", so the adequacy gap does not contradict a stated coverage claim.

## 7. Provenance

- Commands (all returned content, no errors): `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -s` on the three paths (sizes 23064, 40856, 3885); `git … show <pin>:<path>` on the same three; `… | cat -n` on the fixture, tool and preregistration; artifact reads of preregistration lines 2–4.
- Installs or updates: none.
- Writes: this report only.
