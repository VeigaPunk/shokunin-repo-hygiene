STATUS: PASS

# ResidAdequacyB — residual non-author review of four `adequacy/cache/*` oracle vectors (Souji lane, round 22, C1 calibration)

Seat: `SoujiR22R.ResidAdequacyB-17` (reviewer, ordinary call of 6 seats after wave 2; residual, not a seat replacement).
Author of the reviewed work: `SoujiR22R` (L1). Reviewed artefacts: `tests/fixtures/r22-result-oracle.json`
(sha256 `849a8569e521f2d04576cbe9a2a8c85c8fd2d495cc7d0cd7c6cd37c58ce5a5cc`), `census/round-21/run-acceptance.py`
(sha256 `00d0e9c2fda2fde2d21cb74b1a1dd5b1db7b1ea679cdfd4239d91aa186e080a6`), `census/round-22/mutation-adequacy.py`.
Base runner for comparison: `41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`
(sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`).

Scope of this seat: the four vectors `adequacy/cache/gate-sha-mismatch`, `adequacy/cache/isolation-cleaned-false`,
`adequacy/cache/isolation-cleaned-int`, `adequacy/cache/isolation-residue-nonempty`; plus the question whether the
cache-demo positive depends on the live bytes of `tools/souji-evidence-cache.py` and whether that dependency is
disclosed in the receipts. No file was written except this report; no git/jj mutation; no lane file touched.

---

## 0. Method (observed commands, all read-only)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B tests/fixtures/r22-result-oracle.py \
    --runner census/round-21/run-acceptance.py --case <id>          # once per target vector
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 41553adb…:census/round-21/run-acceptance.py \
    | python3 -B census/round-22/mutation-adequacy.py --grade-stdin # base runner graded in memory
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-22/mutation-adequacy.py
git -C … show / diff / log / rev-parse (read-only); python3 -B -c one-liners that only read and print
```

Plus in-memory-only evaluation of the runner's own `summarize_result` and of extra mutants compiled in memory
(`exec(compile(src,…))` inside a `python3` session — no file written, no child process spawned, the real
acceptance `main()` was never invoked).

Tooling: **no tool was installed or upgraded** for this seat (the task needed only the repo's own Python 3.14.8
and `git`). Nothing was fetched from the network.

---

## 1. Stored delta reconstructed from the pinned original record BEFORE reading the predicate

Pinned inputs (immutable, digests checked by the oracle itself): `census/round-21/final-out-S1.json`
(`source_receipt`) and `census/round-21/step-inventory.json` (`frozen_inventory`). The record is
`commands[name="clean-cache-demonstration"]`:

| field | pinned value (observed) |
|---|---|
| `returncode` | `0` |
| `stderr` | `""` (empty) |
| `stdout` | raw JSON of the r14 cache demonstration (33 `checks`, 4 `cases`) |
| `stdout["gate"]["sha256"]` | `dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6` |
| `stdout["gate"]["sha256_after"]` | `dd279ba9…39d6` (same digest) |
| `stdout["isolation"]["cleaned"]` | `true` |
| `stdout["isolation"]["residue"]` | `[]` |
| `stdout["status"]` / `measured_commit` / `harness_revision` | `"ok"` / `ff425ab8…7045` / `ff425ab8…7045` |
| `stdout["failed_checks"]` / `producer_executions_new_policy` | `[]` / `3` |
| `stdout["checks"]` | 33 keys, every value `true` |
| `stdout["cases"]` phases | `initial-fresh`, `unchanged`, `dependency-modified`, `legacy-no-dependencies` |
| frozen inventory step | `kind: "cache-demo"`, `expected_summary.isolation_cleaned: true`, `cases: 4`, `checks: 33` |

The pinned record's own `input_sha256` and `gate.sha256` both carry `dd279ba9…39d6` for
`tools/souji-evidence-cache.py`, so the gate digest is the producer's *consumed* gate slot, not an arbitrary field.

Each target vector stores a single `json_set` delta and **no** `stdout`/`stderr`/`returncode` override, so the
fixture feeds the pinned stdout with exactly one field replaced. Observed applied deltas (recomputed by replaying
the oracle's own `json_set` walk over the pinned stdout and diffing the decoded payloads):

| vector | applied delta (pinned → mutated) |
|---|---|
| `adequacy/cache/gate-sha-mismatch` | `.gate.sha256`: `dd279ba9…39d6` → `0000…0000` (64 zeros) |
| `adequacy/cache/isolation-cleaned-false` | `.isolation.cleaned`: `True` → `False` |
| `adequacy/cache/isolation-cleaned-int` | `.isolation.cleaned`: `True` → `1` (JSON int) |
| `adequacy/cache/isolation-residue-nonempty` | `.isolation.residue`: `[]` → `["synthetic-residue"]` |

Each delta is exactly one leaf, at a path that exists in the pinned payload; nothing else in the payload differs
(verified by a recursive field-by-field diff of pinned vs mutated decoded payloads). The fixture really does feed
these inputs.

---

## 2. Independent judgement of `want=false` (decided from the pinned contract, not from the implementation)

* **`gate-sha-mismatch` → `want=false` is CORRECT.** The cache-demo payload is the producer's declaration of *which
  gate bytes were measured*. The pinned producer additionally self-certifies `gate_digest_recorded_and_unchanged`
  in its 33 checks and repeats the same digest in `input_sha256`. A payload whose `gate.sha256` is not the
  installed gate's digest is a false declaration and must not be reported as `matched`. The changed runner compares
  `gate.get("sha256")` with the digest of the live `tools/souji-evidence-cache.py`
  (`census/round-21/run-acceptance.py:503`, `:522`); a 64-zero digest can never equal a real sha256, so the
  rejection is robust and does not depend on the live file's current bytes.
* **`isolation-cleaned-false` → `want=false` is CORRECT.** The frozen inventory's `expected_summary.isolation_cleaned`
  is `true`; a payload declaring `cleaned: false` means the isolated tree was *not* cleaned, so the demonstration's
  isolation claim fails. The runner's identity check (`run-acceptance.py:524`) rejects it.
* **`isolation-cleaned-int` → `want=false` is CORRECT.** `1` is not `true`. The decoded JSON value is an `int`
  (JSON has no boolean subtype of int); the contract field is a boolean, so a producer that emits `1` is not
  declaring `cleaned`. This is precisely the bool/int confusion the C1 claim repairs, and the identity comparison
  at `run-acceptance.py:524` rejects it. (Python's `bool` being an `int` subclass is exactly why `==` would be
  wrong here — `1 == True`.)
* **`isolation-residue-nonempty` → `want=false` is CORRECT.** The runner requires `isolation.residue == []`
  (`run-acceptance.py:525`): any residue means the isolated demonstration left state behind, so the isolation
  claim fails even though the payload's own `isolation_confined: true` check still says otherwise (the payload is
  self-inconsistent; rejection is the right outcome).

No literal decision in these four vectors is wrong, and none is derived from the implementation under test.

---

## 3. Predicate-level single-cause check (observed)

I re-implemented the changed runner's cache-demo conjunct list verbatim (loaded `run-acceptance.py` as a module and
mirrored its `demo_match` expression) and evaluated every conjunct against each mutated payload:

| vector | conjuncts that fail | count |
|---|---|---|
| `gate-sha-mismatch` | `gate_sha_eq_live` | **1** (exactly the intended one) |
| `isolation-cleaned-false` | `isolation_cleaned_identity` | **1** |
| `isolation-cleaned-int` | `isolation_cleaned_identity` | **1** |
| `isolation-residue-nonempty` | `isolation_residue_empty` | **1** |

Every other conjunct (`status`, `measured_commit`, `harness_revision`, 4 cases + ordered phases, 33 named checks
all `true`, `failed_checks`, `producer_executions_new_policy`, `inputs_unchanged_during_run`, `gate` is a dict,
`isolation` is a dict) still holds in each mutated payload. **Each vector's rejection is single-cause at the
predicate level** — it is not an incidental rejection caused by an unrelated defect, a parse failure, or a
malformed shape.

---

## 4. Mutant attribution (observed)

`python3 -B census/round-22/mutation-adequacy.py` on the current runner + 225-byte oracle: exit **0**,
pristine 225/225, 25 mutants, 21 killed, 4 survived (all four marked *equivalent* by L1), 0 disagreeing.
`killing_vectors` per mutant:

| mutant (origin) | expect | observed | killing vectors |
|---|---|---|---|
| `gate-sha` (pre-existing) | killed | killed | `adequacy/cache/gate-sha-mismatch` — **sole killer** |
| `isolation-cleaned-drop` (pre-existing) | killed | killed | `adequacy/cache/isolation-cleaned-false`, `adequacy/cache/isolation-cleaned-int` |
| `isolation-cleaned-eq` (pre-existing) | killed | killed | `adequacy/cache/isolation-cleaned-int` — **sole killer** |
| `isolation-residue` (pre-existing) | killed | killed | `adequacy/cache/isolation-residue-nonempty` — **sole killer** |

Cross-check against `census/round-22/mutation-adequacy-oracle214.json`: on the 214-byte oracle all four of these
mutants are `survived` with `killing_vectors: []` — i.e. the 214-vector fixture left them alive, and the four
vectors under review are exactly what closes that hole (`mutation-adequacy-oracle225.json` shows all four killed,
`disagreeing_with_expect: []`).

### Per-vector verdict

| vector | verdict | kills | single-cause? |
|---|---|---|---|
| `adequacy/cache/gate-sha-mismatch` | **CORRECT**, discriminating | `gate-sha` (unique) | Yes — 1 failing conjunct; mutant's sole killer |
| `adequacy/cache/isolation-cleaned-false` | **CORRECT**, discriminating, but **redundant** | `isolation-cleaned-drop` | Yes at predicate level; **not a unique witness** — every mutant it kills is also killed by `isolation-cleaned-int` |
| `adequacy/cache/isolation-cleaned-int` | **CORRECT**, discriminating, **unique witness** | `isolation-cleaned-eq` (unique) + `isolation-cleaned-drop` | Yes — 1 failing conjunct; sole killer of the `==`-vs-`is` mutant |
| `adequacy/cache/isolation-residue-nonempty` | **CORRECT**, discriminating | `isolation-residue` (unique) | Yes — 1 failing conjunct; mutant's sole killer |

### Finding B1 (minor, coverage/redundancy — not a defect in the vectors)

`adequacy/cache/isolation-cleaned-false` is **subsumed** by `adequacy/cache/isolation-cleaned-int`: the mutant
`isolation-cleaned-drop` is killed by both, and the `-false` vector kills nothing that the `-int` vector does not
already kill (`isolation-cleaned-eq` is *not* killed by `-false`, because `False == True` is still false).
Consequence: the `-false` vector adds zero mutant coverage to the 225-byte fixture. It is harmless and truthful —
it is a valid negative control — but the round's adequacy narrative should not count it as an independent
kill. The `-int` vector is the load-bearing one: it is the only witness for the `is`→`==` downgrade
(`isolation.get("cleaned") == expected["isolation_cleaned"]` would accept `1` for `True`).

### Finding B2 (minor, disclosure — the live gate bytes)

**The cache-demo positive does depend on the live bytes of `tools/souji-evidence-cache.py`, and that dependency is
not disclosed in the receipts.**

* Dependency (observed): `census/round-21/run-acceptance.py:503` computes
  `gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))` from the **live working tree**,
  and `:522` requires `gate.get("sha256") == gate_sha`. The vector `positive/clean-cache-demonstration` uses the
  unmutated pinned stdout, whose `gate.sha256` is `dd279ba9…39d6`; therefore that positive passes **only while the
  live file still hashes to `dd279ba9…39d6`**. Observed now:
  `sha256sum tools/souji-evidence-cache.py` → `dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6`,
  and `git status --porcelain -- tools/souji-evidence-cache.py` is empty (working copy clean). So the positive
  currently passes; if that tool is edited or removed, the pristine runner itself would report
  `positive/clean-cache-demonstration` as `False` (and, if the file disappeared, `read_regular` raises `Refusal`
  at `run-acceptance.py:217-220`, so the whole cache-demo group would degrade to exceptions).
* The fixture does **not** bind that input: `tests/fixtures/r22-result-oracle.py` `inputs()` (lines 28-38) hashes
  only `source_receipt` and `frozen_inventory`; the gate file is never hashed, so a drift in it produces an
  unexplained oracle failure with no pointer to the cause.
* Disclosure status (observed by grep over `census/round-22/`): the six L1 receipts
  (`oracle214-baseline.json`, `oracle214-changed.json`, `oracle225-baseline.json`, `oracle225-changed.json`,
  `mutation-adequacy-oracle214.json`, `mutation-adequacy-oracle225.json`) contain **no** mention of
  `tools/souji-evidence-cache.py`, of the digest `dd279ba9…`, or of any live-file input; their only input bindings
  are `runner_sha256`, `oracle_sha256`, `source_receipt_sha256` and the scope string *"Pinned public outputs plus
  fabricated mutations; no command execution or process inspection."* `w2-dead-seat-residual.json` mentions the
  string only inside the embedded pinned stdout, not as a dependency. The dependency **is** disclosed in the corpus:
  `corpus/lessons/round-22.md:59` quotes W2 `Attack57` — *"the paired positive depends on the working-tree bytes of
  tools/souji-evidence-cache.py, which the oracle never hashes, so I could not check that it passes"* — and
  `.ufo/waves/round-22/w2/Attack57.md` §3 states it in full. So the information exists in the lane, but it was not
  carried into the receipts whose numbers are being cited, and it was not re-verified by L1 (the positive's
  live-byte condition was never executed and checked by the author; it holds today only by coincidence of the
  working tree).
  **Consequence for the claim under review:** the four `adequacy/cache/*` vectors are *not* affected (the
  zero-digest mutation can never equal a live sha256, and the isolation predicates do not read the gate file), so
  the vectors under review are robust. The exposure is confined to the paired **positive** control.
  **Recommendation (operator/L1 decision, not applied by me):** disclose the live-gate-byte input in the receipt
  scope fields (or hash it in `inputs()`), or pin the positive's gate digest to the frozen inventory.

### Finding B3 (minor, residual saturation gap — not a false claim)

The `gate-sha-mismatch` vector binds the payload's top-level `gate.sha256` slot only. A mutant that keeps a
digest comparison but compares the payload **against itself** instead of against the installed gate survives all
225 vectors. Observed (in-memory mutant, graded by the unchanged oracle via the probe's own `grade()`):

```
M2-internal-self-consistency:
  and isinstance(gate, dict) and gate.get("sha256") == gate_sha
→ and isinstance(gate, dict) and gate.get("sha256") == gate.get("sha256_after")
  → SURVIVED (0 failing vectors out of 225)
```

In the pinned payload `gate.sha256 == gate.sha256_after == dd279ba9…39d6`, so the internal self-consistency
check accepts the positive exactly as the live binding does, and no vector mutates both slots together.
The same in-memory probe shows the neighbouring mutants *are* caught, so the gap is specific:

```
M1-wrong-digest-slot (sha256_after instead of sha256)  → killed by adequacy/cache/gate-sha-mismatch
M3-wrong-gate-file (souji-census.sh instead of the gate) → killed by positive/clean-cache-demonstration,
                                                            positive/cache-transient-path-and-time
M4-inverted-cleaned  (is not)                           → killed by the two isolation-cleaned vectors + positives
M5-residue-empty-or-truthy                             → killed by adequacy/cache/isolation-residue-nonempty
```

This is a **coverage note, not a false claim**: the receipts claim "21 of 21 non-equivalent *enumerated* mutants
killed" (`mutation-adequacy-oracle225.json`, and `corpus/lessons/round-22.md:82`), and the probe's own scope string
states *"Equivalent marks are L1 reasoning, not proof."* No receipt claims the mutant space is exhausted. A vector
that sets `gate.sha256` **and** `gate.sha256_after` to the same wrong digest would close the gap.

### Finding B4 (informational — these four vectors are adequacy-only, not base/changed discriminators)

Base runner `41553adb` graded in memory against the 225-byte oracle
(`git show 41553adb…:census/round-21/run-acceptance.py | python3 -B census/round-22/mutation-adequacy.py --grade-stdin`)
gives `fail: 156, pass: 69`, and all four vectors under review are among the passes:

```
{'id': 'adequacy/cache/gate-sha-mismatch',          'expected': False, 'observed': False, 'exception': None, 'pass': True}
{'id': 'adequacy/cache/isolation-cleaned-false',     'expected': False, 'observed': False, 'exception': None, 'pass': True}
{'id': 'adequacy/cache/isolation-cleaned-int',       'expected': False, 'observed': False, 'exception': None, 'pass': True}
{'id': 'adequacy/cache/isolation-residue-nonempty',  'expected': False, 'observed': False, 'exception': None, 'pass': True}
```

That is the expected and correct behaviour: the base runner already had these four retained conjuncts, so these
vectors discriminate *pristine vs mutant*, not *base vs changed*. Of the 11 appended `adequacy` vectors only the
two `decoder-depth-100000` vectors discriminate base (RecursionError) from changed (`False`). Consistent with
`corpus/lessons/round-22.md:82` ("the nine retained-conjunct guards do not discriminate"). The base runner's
`positive/clean-cache-demonstration` also passes (the base already compared `gate.sha256` with the live digest), so
the four vectors are honest negative controls rather than restatements of the r22 changes.

---

## 5. Fixture-integrity check (the 214-prefix claim)

Observed: the current fixture has 225 cases, the pinned 214-byte fixture (`git show b912328d00d19f26918240710d0b5e0f334880ff:tests/fixtures/r22-result-oracle.json`,
sha256 `292442a6…0651`) has 214. Per-case decoded comparison of the first 214 entries: **0 differing indices**;
all top-level metadata keys (`schema`, `source_receipt`, `source_receipt_sha256`, `frozen_inventory`,
`frozen_inventory_sha256`, `revision`, `contract`) are byte-identical. Raw-byte check: the first differing byte is
at offset **184527**, which is exactly the `}`→`},` separator after the 214th case object; every byte of the 214
cases themselves is unchanged. The 11 appended entries are all `group: "adequacy"`, all `want: false`. The claim
"the first 214 cases are byte-for-byte unchanged" holds (the only byte added inside the array is the array
separator after case 214).

---

## 6. Residual risk and verification gaps

1. **Live working-tree coupling of the cache-demo positive** (Finding B2). Any edit to
   `tools/souji-evidence-cache.py` in this lane — including by a concurrent seat — silently turns
   `positive/clean-cache-demonstration` (and `positive/cache-transient-path-and-time`) into a failure of the
   pristine runner, with no digest in the receipt pointing at the cause. Currently satisfied (digest
   `dd279ba9…39d6`, working copy clean). Not disclosed in the round-22 receipts; disclosed in
   `corpus/lessons/round-22.md:59` and `.ufo/waves/round-22/w2/Attack57.md`.
2. **One surviving mutant class in the gate digest** (Finding B3): self-consistency instead of live-file binding.
   Not a false claim; a coverage note for whoever extends the fixture.
3. **One redundant vector** (Finding B1): `isolation-cleaned-false` adds no coverage beyond
   `isolation-cleaned-int`.
4. **Not verified by me (out of scope / forbidden by the seat's bounds):** the real acceptance `main()` was never
   executed (no subprocess-spawning test of it); the 18-step replay was not run; the *contents* of
   `tools/souji-evidence-cache.py` were not inspected (only its digest was compared, which is all the predicate
   reads); the `w2-dead-seat-residual.json` rows were not re-derived (they cover other vectors — none of the four
   under review appears in its 26 rows).
5. **Not verified by the author either:** the `sha256_after` self-consistency mutant above was not in L1's enumerated
   25-mutant list, so the probe's "21/21 killed" number does not cover it.
