# Attack60 — cache/shape/isolation/array (want=False), source-only

Seat: SoujiR22.Attack60 (critic, leaf). Target code 4f83fd222ffbd8825340221a8c426550ef891191, base 41553adb139d06511dc386bb3ce4326aebfba675. No run, no probe, no delegation. Tools: none installed or updated. `/home/vgpnk/.omp/agent/RULES.md` was read first.

## STATUS

**Source-only PASS, with limits.**
- The literal expectation `want=False` is correct.
- The fixture really delivers `isolation = []` to `summarize_result`.
- By source reading, the changed predicate returns `False` without raising.
- By source reading, the base predicate raises `AttributeError`, which the oracle counts as a failure. The vector therefore separates base from changed.

Two non-blocking findings follow: a precondition that depends on the run (F1) and a gap in mutation coverage (F2). None of this is runtime evidence. L1's 214-vector run is the only source of observed decisions.

## Byte binding (read-only hashing of named paths)

The pinned commit, the base and the working tree have identical bytes for `final-out-S1.json` (`bc53a752…`, matching `oracle.source_receipt_sha256`), `step-inventory.json` (`8b7b1cd8…`, matching `oracle.frozen_inventory_sha256`) and `cache-demonstration.py` (`373daa9d…`).

The working tree equals 4f83fd for:
- `run-acceptance.py` (`00d0e9c2…`)
- `r22-result-oracle.py` (`3c0776ae…`)
- `r22-result-oracle.json` (`292442a6…`)

The literal `code4f83fd…` is not a valid git object. The commit resolves once the `code` prefix is removed.

## 1. Stored delta, reconstructed before reading the predicate

The oracle (`r22-result-oracle.json:2254-2266`) stores `step_name=clean-cache-demonstration` and `json_set=[[["isolation"], []]]`.

The original public record is `final-out-S1.json`, `commands[]` (key at :28), entry `name=clean-cache-demonstration` (:2515):
- `returncode 0` (:3380), `stderr ""` (:3381).
- `stdout` (:3383) contains the top-level key `"isolation"` at two-space indent, exactly once: `{"base": "/var/tmp/souji-r14-cache-demo.4uavk4gp", "cleaned": true, "fixture_files": [...], "kept": false, "records": ..., "residue": [], "results": ..., "root": ..., "under_var_tmp": true}`. This matches the parsed `observed_json.isolation` at :3246-3258.

The frozen inventory (`step-inventory.json:187-206`) sets `kind=cache-demo` with `expected_summary.isolation_cleaned=true` and `measured_commit "<REV>"`.

So the delta replaces one well-formed dict (`cleaned=true`, `residue=[]`) with an empty JSON array. Nothing else changes.

**Is the fixture's input real?** Yes.
- `r22-result-oracle.py:67-68` selects `record['stdout']`.
- :72-82 parse it, walk an empty `path[:-1]` so `at = payload`, then assign `payload["isolation"] = deepcopy([])` and re-dump.
- :83-85 copy the step (with `<REV>` replaced via :40-47/:59-60) and set `measured_commit` to `ff425ab…`.
- :86-91 pass `returncode 0`, the mutated stdout and `stderr ""`.

Re-serialization makes stdout a single line starting with `{`, so `failure_lines` (`run-acceptance.py:356-359`) stays empty. The producer itself can never emit a list here: `cache-demonstration.py:1022-1029`, :1200-1201 and :1099-1103 always produce a dict, and `.update` would crash on a list. This vector is therefore purely a fabricated malformed-input control, consistent with R22-M5 and the "no malicious-producer attestation" boundary.

**Is the expected decision right?** Yes. Without an isolation object, no `cleaned is True` / `residue == []` observation exists, so the frozen `isolation_cleaned=true` obligation cannot be met. Rejecting is required; accepting would be a false green.

## 2. Changed predicate vs this vector (`run-acceptance.py` @4f83fd)

- :494-497: decoding succeeds and the payload is a dict.
- :501: `isolation = payload.get("isolation")` evaluates to `[]`. The `{}` default was removed relative to base.
- :506-522: every earlier conjunct holds for the unmutated record and is untouched by this delta:
  - status `ok`, `measured_commit` and `harness_revision` equal `ff425ab…`.
  - Four cases, with phases `initial-fresh`/`unchanged`/`dependency-modified`/`legacy-no-dependencies` (final-out :2625/:2732/:2819/:2926), equal to `CACHE_CASE_PHASES`.
  - 33 checks keys (:2997-3029), all `true`, equal to `CACHE_CHECK_NAMES`.
  - `failed_checks=[]`, `producer_executions_new_policy=3` as an int, `inputs_unchanged_during_run=true`.
  - `gate` is a dict whose `sha256` is `dd279ba9…` (see F1).
- :523: `isinstance(isolation, dict)` is `False` for `[]`, so the expression short-circuits and the `.get` calls on :524-525 never run.
- :536-537: `matched = False` with no exception. The oracle's `passed` expression (:97) evaluates to True.

**Base @41553adb**, lines 446-470 of `git show`:
- :455 is `isolation = payload.get("isolation", {})`. The key is present, so the default does not apply and the value is `[]`.
- The prior conjuncts :457-467 hold under the same F1 precondition.
- :468 evaluates `[].get("cleaned")`, which raises `AttributeError`.
- The oracle catches it at :93-96, giving `observed=None` and `pass=False`.

So base fails this vector and changed passes it. This matches the R22-M5 claim.

**Paired positives**
- `positive/clean-cache-demonstration` (oracle :586-591) is the unmutated record. The isolation dict reaches :523-525 with `cleaned is True` and `residue == []`, so it is True under F1. This is the vector's real pair.
- `positive/cache-transient-path-and-time` (:4054-4075) changes only `cases[0].record` and the existing top-level `observed_at`. Neither is read by :506-526, isolation stays intact, so `want=True` is correct.

**Mutation kill (drafted, not executed).** Delete only `and isinstance(isolation, dict)` at :523. This vector then raises `AttributeError` at :524, the oracle gives `observed=None` and reports a fail, so the mutation is killed. The `/null` sibling also kills it.

## Findings

**F1 — the vector can pass vacuously; this is a run-time precondition for L1.**
- The gate conjunct (:522) comes before the isolation guard (:523) and compares against `sha256_bytes(read_regular(ROOT/"tools/souji-evidence-cache.py"))` (:503). That is a live working-tree file outside this contract's named read set, so it was not hashed here.
- If its bytes differ from the recorded `dd279ba9…` (final-out :3155/:3164), the predicate returns False before ever reading `isolation`. The vector would then report PASS in both base and changed, and the R22-M5 discrimination would be void. The positive would fail at the same time.
- `r22-result-oracle.py` has no pairing guard, so a single-vector run (`--case cache/shape/isolation/array`) reports PASS even if the cache predicate were completely broken.
- Impacted axes: calibration (provenance of discrimination). This is not a wrong expectation.
- Smallest safe correction: L1 counts this vector, and every cache negative, as discriminating only when `positive/clean-cache-demonstration` is True in the same full 214-vector run. Optionally the oracle could record a precondition group so a failing positive voids its negatives.

**F2 — gap in mutation coverage; the drafted mutation survives.**
- Drafted mutation: at :501 use `isolation = (payload.get("isolation") or {}) if isinstance(payload, dict) else None`, and drop `isinstance(isolation, dict)` at :523.
- `isolation=[]` and `isolation=null` both become `{}`, then `cleaned is True` is False and the result is False. Both shape vectors still pass, so the mutation is not killed, yet a non-empty list would crash.
- The same reasoning applies to the `gate/null` and `gate/array` pair (`payload.get("gate") or {}`).
- Impacted axes: coverage and operability (no-harm claim about crashes is only exercised on falsy shapes).
- Smallest safe correction: one additive literal vector, `cache/shape/isolation/array-nonempty`, with `json_set [[["isolation"], [{"cleaned": true, "residue": []}]]]` and `want=False`. Changed code gives False, base crashes, and the mutation crashes, so it is killed. A `gate` analogue would also help.
- Adding vectors is L1's call. The 214-vector file is frozen for this round, so this would be a next-round addition, not an edit.

**Out of scope, not a C1 defect.** An isolation object of the form `{"cleaned": true, "residue": [], "kept": true, "under_var_tmp": false}` is accepted. `kept`, `under_var_tmp` and the path fields were never compared in base or changed. Confinement rests only on the producer's own `checks.isolation_confined` claim (`cache-demonstration.py:937-941`). This is a tradeoff the claim deliberately excludes (lesson :34, "not a proof that each producer assertion executed"), so it is not something to fix within C1.

## Limits

This review is source-only, with no execution: base and changed outcomes above are derived from reading the code. F1's precondition is unverified because the gate file is not in the named read set. No historical private snapshots, `/proc`, process TSVs, or lane/fleet listings were opened. This is not malicious-producer attestation and not a claim of universal malformed-input totality. F5, reap, NAMESPACE, certification and K5 are untouched.
