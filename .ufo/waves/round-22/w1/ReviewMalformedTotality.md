STATUS: PASS — scoped source review complete against pinned baseline `41553adb139d06511dc386bb3ce4326aebfba675`; no target execution or acceptance result is claimed.

## Axes

- **Calibration:** malformed producer shapes resolve to a false step verdict, not a crash or accidental green.
- **Operability:** a red replay still writes its complete result record and exits through the normal false-verdict path.
- **Coverage:** cover the specifically requested cache-demo `gate`/`isolation` shapes and counter JSON roots. No broader schema, hostile-producer, or execution-authentication claim is added.

## Reconstructed contract and evidence chain

The source reviewed is the pinned blob `census/round-21/run-acceptance.py` at the revision above, not the concurrently changing worktree file. In `main`, the runner calls `summarize_result` for each step at lines 608–626; the outer exception handler catches only `(OSError, ValueError, RuntimeError, Refusal, KeyError)` at lines 652–654. A completed record is written at line 651 and the runner returns 1 when `all_matched` is false (line 655).

### Cache demonstration: non-dict gate/isolation values can crash

In the `cache-demo` branch (lines 446–480), the runner parses stdout, then obtains `isolation` at line 455. The expected green predicate at lines 456–469 accesses:

- `payload.get("gate", {}).get("sha256")` at line 467; and
- `isolation.get("cleaned")` at line 468.

If a JSON object contains `"gate": null`, `.get("gate", {})` returns `None` (the default only applies when the key is absent), and the following `.get` raises `AttributeError`. A present list, string, number, or boolean gate value likewise raises `AttributeError` if evaluation reaches this conjunct. For isolation, a present `null`, list, string, number, or boolean is assigned directly at line 455 and raises `AttributeError` at line 468 if reached. `AttributeError` is absent from `main`'s exception tuple. **Source-inferred outcome:** instead of a false step verdict, this exception escapes the replay, produces an unhandled traceback, and prevents the normal result record from being written. This failure requires earlier `and` conjuncts to pass: a non-green payload normally short-circuits before either unsafe access. An isolation-shape failure also requires the preceding gate check to pass.

The existing `residue == []` comparison (line 469) does not call a method on producer data; an unexpected residue type simply compares unequal. Checks and cases are type-guarded at lines 451–452, 461–463, and 474–477. The ordinary producer does emit dictionaries for both fields: the pinned `cache-demonstration.py` returns `"gate": gate_state` and an isolation dictionary (lines 1020–1029); its finalization updates isolation state and `gate["sha256_after"]` (lines 1200–1208). Those ordinary shapes do not protect the summarizer from malformed or foreign stdout.

### Counter roots: current fixed inventory is crash-free and false

The counter branch parses stdout at lines 421–424. JSON parse failures caught as `ValueError`/`TypeError` set `observed = None`. For a successfully parsed non-object root—list, null, boolean, number, or string—the exact path compares it with the fixed expected object at line 427 and yields false; the non-exact path requires `isinstance(observed, dict)` at lines 430–431 and yields false. Numeric diagnostics are also guarded by `isinstance(observed, dict)` at line 433. All five committed `COUNTER_EXPECTATIONS` have dictionary expectations (four exact, one non-exact), so these malformed/non-object roots produce a false counter verdict rather than a crash under the current inventory. This is source-inferred, not executed.

This root-shape result does not clear the separate admitted scalar-type defect: Python equality permits `False == 0` and `True == 1` in nested dictionaries, so an object root with bools substituted for 0/1 integer fields can still match at line 427. That is not a root-shape defect and is outside this review's proposed change. Likewise, no arbitrary-depth JSON guarantee is claimed; no depth limit or additional producer validation is proposed.

## Bounded no-crash false-verdict specification

Draft only; no production file was edited. Extract possibly malformed fields without method calls, then guard their shapes before accessing them:

```python
# In summarize_result's cache-demo branch; draft lines only.
gate = payload.get("gate") if isinstance(payload, dict) else None
isolation = payload.get("isolation") if isinstance(payload, dict) else None

# In demo_match, retaining the existing sha256/cleaned/residue predicates:
and isinstance(gate, dict)
and gate.get("sha256") == gate_sha
and isinstance(isolation, dict)
and isolation.get("cleaned") is expected["isolation_cleaned"]
and isolation.get("residue") == []
```

The extraction mirrors the existing guarded `checks`/`cases` access. This changes only the crash cases into ordinary false predicates. Previously non-crashing cases keep their verdict: absent gate already fails the sha check; absent isolation already fails `cleaned is True`; dictionaries retain the same sha256, identity, and residue comparisons. It adds no gate-key/schema requirements beyond the existing `sha256` access, no new isolation fields, and no residue-type validation beyond the existing equality-to-empty-list check. It does not alter counter checks, summary stderr handling, or cache-check identity requirements.

Expected oracle outcomes for the malformed-shape vectors (with other fields set to an otherwise-green payload so evaluation reaches the selected field):

| Producer shape | Baseline behavior | Guarded behavior |
|---|---|---|
| Gate absent | False, no crash | False, no crash |
| Gate dictionary with matching / nonmatching `sha256` | Existing comparison | Same comparison |
| Gate `null`, list, string, number, or boolean | `AttributeError` if reached | Step `matched: false`; normal record path |
| Isolation absent | False, no crash | False, no crash |
| Isolation dictionary | Existing `cleaned` and `residue` comparisons | Same comparisons |
| Isolation `null`, list, string, number, or boolean | `AttributeError` if reached | Step `matched: false`; normal record path |
| Counter stdout root `[]`, `null`, `true`/`false`, number, or string | False for the fixed dictionary expectations | Remains false; no shape change needed |
| Counter malformed JSON (truncated document, extra trailing document, non-JSON text) | Parse failure becomes `None`, then false for current dictionary expectations | Remains false; no shape change needed |

For the cache-demo vectors, expected harness behavior is a completed record with that step false, `all_matched` false, and ordinary exit 1—not a traceback/no-record crash—assuming no unrelated runner refusal or input drift. Retain the existing fully green dictionary-shaped cache-demo and counter positive controls unchanged. These are fixture expectations, not executed results.

## Evidence limits and confidence

- **Source-inferred:** all behavior above comes from pinned source reads (`run-acceptance.py` lines 420–480, 608–655; `cache-demonstration.py` lines 1020–1029 and 1200–1208) and the named frozen inventory. No tests, probes, builds, or formatter were run.
- `lsp` was unavailable (`xd://lsp`: “No such tool”); grep was used only to locate source lines, not as semantic proof. The semantic claims are based on the source excerpts.
- At review time, the worktree runner differed from the pinned file (63 insertions/9 deletions); this report intentionally makes no claim about L1's in-flight integration or its acceptance result.
- No tools were installed or updated.