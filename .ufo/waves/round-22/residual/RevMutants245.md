STATUS: PARTIAL

# RevMutants245 — non-author residual review of the 20 residual mutants + `stack_soft_limit` (souji lane, round 22)

Seat: `SoujiR22-2.RevMutants245` (reviewer, residual, non-author).
Author of the reviewed work: `SoujiR22-2` (replacement L1).
Reviewed artefacts (uncommitted working-tree changes vs lane HEAD `81a2646`):
`census/round-22/mutation-adequacy.py` (sha256 `5a46027c…bcd07` at read time),
`tests/fixtures/r22-result-oracle.json` (sha256 `63de539f…51795`),
receipts `census/round-22/{oracle245-changed,oracle245-baseline,mutation-adequacy-oracle245,mutation-adequacy-listed45-oracle225,stack-sweep-oracle245}.{json,txt}`.

Runner under test: `census/round-21/run-acceptance.py` sha256 `00d0e9c2…e080a6` (unmodified in the working tree).
Base runner for origin labels: `41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`
sha256 `1141839963…ea2b`.

Scope, as instructed by the parent: the **20 mutants after the `# Residual review` comment** in `MUTANTS`
(ids `json-exact-leaf-true` … `violation-drop`, `MUTANTS` indices 25–44), plus the new `stack_soft_limit` receipt field.
The 14 mutants added later by the parent (after the `# Diff-enumerated survivors from residual CritAdequacy245`
comment, indices 45–58) are **out of scope**; I note them only where they affect a claim about my scope.

No installs or updates were made. Everything ran on the existing python3 3.14.8 and git.
Writes: this report only. No scratch file was written anywhere; all mutants and alternate inputs were
evaluated in memory (`exec(compile(...))` inside `python3 -B -` one-liners / pipes).

---

## 0. Headline

* **All 20 assigned mutants are correctly anchored, uniquely anchored, correctly labelled by origin, and
  behave exactly as `expect` claims against the 245-vector oracle.** 17 are killed by named vectors;
  3 (`baseline-guard-pass`, `checks-len-drop`, `caserows-len-drop`) survive, and I could not construct a
  distinguishing input for any of them under the pinned inventory steps.
* **The three new `equivalent` marks are genuinely equivalent under the pinned inventory** — but
  `baseline-guard-pass` is equivalent only *conditionally*, and the condition is stated in the source
  comment. See Finding 1: it is a **conditional** equivalence, not an unconditional one, and the surviving
  mutants are not interchangeable with the original on an off-inventory step. That is disclosed in the
  comment, so it is honest labelling — but the `equivalent` field itself carries no scope marker.
* **`stack_soft_limit` is honest but insufficient by itself.** It records the RLIMIT_STACK soft limit
  (bytes). The sweep receipt `stack-sweep-oracle245.txt` shows the probe's result is *not* a function of
  the soft limit alone: the flip happens between 14336 and 16384 KiB, and the parent has since added
  `depth_100000_decode_raises` to record the actually-decisive predicate. See Finding 2.
* **One material discrepancy in the receipt set** (Finding 3): `oracle245-baseline.json` does not
  reproduce byte-for-byte — its `results` row for the RecursionError vector carries a *different measured
  stack-usage number* than a fresh run of the same bytes. The pass/fail counts (88/245) reproduce.
* **The probe is not byte-reproducible from its own file** (Finding 4): the stored receipts
  `mutation-adequacy-oracle245.json` and `mutation-adequacy-listed45-oracle225.json` were produced by
  the 45-mutant version of the file; the current file has 59 mutants and two extra receipt keys, so
  `python3 -B census/round-22/mutation-adequacy.py` today prints a *different* receipt than either
  stored one, and it **exits 1** because of the 14 out-of-scope mutants. The stored receipts are still
  internally consistent and their mutant rows reproduce exactly (verified below).
* Verdict is PARTIAL, not PASS, for two reasons: the 245-state receipt set is not byte-reproducible
  (Findings 3, 4), and the `stack_soft_limit` field alone does not discharge the stack-dependence claim
  that the receipt set was created to discharge (Finding 2). Neither is a defect in the 20 mutants.

---

## 1. Observed: the 20 mutants, anchor by anchor

`mutate()` raises `ValueError` unless the anchor occurs exactly once (or, for the two occurrence-indexed
mutants, unless the index exists). The probe ran to completion and did **not** exit 2, so every anchor
resolved. I re-checked uniqueness independently of `mutate()`:

```
$ python3 -B -  (in memory, src.count(old) for each of MUTANTS[25:45])
all 20 → cur_count == 1
```

Line numbers below are lines of `census/round-21/run-acceptance.py` at sha256 `00d0e9c2…`.

| # | id | origin | expect | anchor → new | runner line | anchor unique | base count | verdict |
|---|---|---|---|---|---|---|---|---|
| 25 | `json-exact-leaf-true` | r22-changed | killed | `    return observed == expected\n` → `    return True\n` | 387 | yes | 0 | **OK** |
| 26 | `case-row-isinstance-drop` | r22-changed | killed | `row.get("phase") if isinstance(row, dict) else None` → `row.get("phase")` | 504 | yes | 0 | **OK** |
| 27 | `baseline-guard-pass` | r22-changed | equivalent | `except ValueError:\n  summary_match = False\n` → `…pass\n` | 430–431 | yes | 0 | **OK (conditional)** |
| 28 | `nonexact-isinstance-drop` | pre-existing | killed | `json_match = (isinstance(observed, dict)\n and all(` → `json_match = (all(` | 476–477 | yes | 1 | **OK** |
| 29 | `gate-self-consistency` | pre-existing | killed | `gate.get("sha256") == gate_sha` → `gate.get("sha256") == gate.get("sha256_after")` | 522 | yes | 1 | **OK** |
| 30 | `status-drop` | pre-existing | killed | `            and payload.get("status") == expected["status"]\n` → `` | 508 | yes | 1 | **OK** |
| 31 | `measured-commit-drop` | pre-existing | killed | `            and payload.get("measured_commit") == revision\n` → `` | 509 | yes | 1 | **OK** |
| 32 | `harness-revision-drop` | pre-existing | killed | `            and payload.get("harness_revision") == revision\n` → `` | 510 | yes | 1 | **OK** |
| 33 | `inputs-unchanged-drop` | pre-existing | killed | `            and payload.get("inputs_unchanged_during_run") is expected["inputs_unchanged_during_run"]\n` → `` | 521 | yes | 1 | **OK** |
| 34 | `inputs-unchanged-eq` | pre-existing | killed | `payload.get("inputs_unchanged_during_run") is expected` → `… == expected` | 521 | yes | 1 | **OK** |
| 35 | `isolation-residue-falsy` | pre-existing | killed | `and isolation.get("residue") == []\n` → `and not isolation.get("residue")\n` | 525 | yes | 1 | **OK** |
| 36 | `checks-all-true-drop` | pre-existing | killed | `            and all(value is True for value in checks.values())\n` → `` | 517 | yes | 1 | **OK** |
| 37 | `checks-len-drop` | pre-existing | equivalent | `and isinstance(checks, dict) and len(checks) == expected["checks"]\n` → `and isinstance(checks, dict)\n` | 514 | yes | 1 | **OK (unconditional)** |
| 38 | `caserows-len-drop` | pre-existing | equivalent | `and isinstance(case_rows, list) and len(case_rows) == expected["cases"]\n` → `and isinstance(case_rows, list)\n` | 511 | yes | 1 | **OK (unconditional)** |
| 39 | `failures-drop` | pre-existing | killed | `matched = returncode == 0 and not failures` → `matched = returncode == 0` | 410 | yes | 1 | **OK** |
| 40 | `returncode-drop` | pre-existing | killed | `matched = returncode == 0 and not failures` → `matched = not failures` | 410 | yes | 1 | **OK** |
| 41 | `aux-drop` | pre-existing | killed | `summary_match = summary_match and auxiliary_match` → `summary_match = summary_match` | 436 | yes | 1 | **OK** |
| 42 | `bm-count-drop` | pre-existing | killed | `                and reported_baseline_mismatches == baseline_mismatch_lines\n` → `` | 443 | yes | 1 | **OK** |
| 43 | `pass-match-drop` | pre-existing | killed | `matched = matched and summary_match and pass_match and not stderr` → `matched = matched and summary_match and not stderr` | 463 | yes | 1 | **OK** |
| 44 | `violation-drop` | pre-existing | killed | `matched = matched and not any(line.startswith("VIOLATION\t")` → `matched = matched and not any(False` | 465 | yes | 1 | **OK** |

### 1a. "Mutates exactly what its id names" — check

Every one of the 20 mutates the clause its id names, and nothing else. Spot evidence:

* `json-exact-leaf-true` replaces only the **leaf** comparison of `json_exact` (`return observed == expected`,
  runner:387). It does not touch the dict/list branches or the type check, so the mutant still rejects
  wrong *types* and wrong *shapes*; it accepts only wrong *values* of the right type. That is exactly what
  the six `adequacy/residual/value/*` vectors probe.
* `case-row-isinstance-drop` removes only the `isinstance(row, dict)` guard inside the `case_phases`
  comprehension (runner:504). With `cases: [1,2,3,4]` the mutant raises `AttributeError` where the
  original yields `phase=None` — the difference the vector `adequacy/residual/malformed/cache/case-rows-int`
  witnesses (I confirmed: original `matched=False`, mutant `AttributeError`).
* `nonexact-isinstance-drop` removes only the `isinstance(observed, dict)` guard on the **non-exact**
  counter branch (runner:476). With stdout `null` the original returns `matched=False`; the mutant raises
  `TypeError`. Killed by `adequacy/residual/malformed/r13-counter-b576341/null`.
* `gate-self-consistency` replaces the live-file digest comparison `gate.get("sha256") == gate_sha` with a
  self-consistency comparison `gate.get("sha256") == gate.get("sha256_after")`. This is the exact defect
  class ResidAdequacyB B3 named. Killed by `adequacy/residual/cache/gate-both-slots-wrong`.
* `violation-drop` replaces `not any(line.startswith("VIOLATION\t")` with `not any(False`, i.e. it *drops*
  the violation check rather than inverting it. The mutant therefore accepts a stdout carrying a
  `VIOLATION\t` line. Killed by `adequacy/residual/summary/carry-invariant-probe/violation-line`.
* `failures-drop` and `returncode-drop` share the anchor `matched = returncode == 0 and not failures`
  (runner:410) and differ only in the replacement — `matched = returncode == 0` vs `matched = not failures`.
  They are distinct mutants of distinct conjuncts; both anchors are unique in the file, so `mutate()`
  applies them independently. Confirmed distinct behaviour: `failures-drop` still rejects a nonzero
  return code, `returncode-drop` accepts one.

### 1b. Origin labels against `git diff 41553adb… HEAD -- census/round-21/run-acceptance.py`

The base diff shows which clauses the r22 work introduced. I compared every anchor's **clause** (not just
its literal text) against the base file:

* **r22-changed (3):** `json-exact-leaf-true` (the whole `json_exact` function is new in r22 — base has no
  `json_exact` at all), `case-row-isinstance-drop` (the `case_phases` comprehension is new in r22), and
  `baseline-guard-pass` (the `try/except ValueError` around `int(baseline_match.group(group))` is new in
  r22 — base line 391 is a bare `reported_baseline_mismatches = int(baseline_match.group(group))` with no
  guard). All three anchors have **base count 0** and the corresponding clauses are absent from the base.
  ✓
* **pre-existing (17):** every one of these anchors occurs in the base file with the same literal text
  (base count 1). Verified against base lines 316, 367, 390, 397, 417, 419, 430, 433, 458–469, 474, 476, 477.
  ✓

One nuance worth recording, because it is the same nuance the earlier `CritMutation.md` reviewer raised for
the pre-existing `gate-sha` mutant: `gate-self-consistency`'s anchor text `gate.get("sha256") == gate_sha`
does **not** occur verbatim in the base (base:467 reads
`and payload.get("gate", {}).get("sha256") == gate_sha`), yet the *clause* — "the reported gate digest must
equal the live gate file's digest" — is pre-existing, only rewritten by r22 into the `gate` local. The
label `pre-existing` is therefore correct at clause level and consistent with how the file's own
`gate-sha` mutant is labelled. The same applies to `pass-match-drop` (base:417
`matched = matched and summary_match and pass_match`; r22 added `and not stderr` to the same line — the
mutant drops the *pre-existing* `pass_match` conjunct and keeps the r22 `not stderr`). Labelling is
**consistent** across the file; it is a clause-level convention, not a literal-text convention, and the
file's own comment says so: `# id, origin (r22-changed clause | pre-existing clause), expect, old, new, occurrence`.

### 1c. Probe result on the 245 oracle, and the killing vectors

Reproduced the 45-mutant scope (the 20 assigned + the 25 pre-existing) against the current 245-vector
oracle, in memory:

```
45-row scope vs 245 oracle: killed 38, survived 7
survivors: nonexact-keyin-get, failed-checks-to-eq, names-len-constant,
           phases-len-constant, baseline-guard-pass, checks-len-drop, caserows-len-drop
disagreeing_with_expect: []
```

The 7 survivors are exactly the 7 mutants labelled `equivalent`; all 38 `expect=killed` mutants are killed.
Per-mutant killing vectors for the 20 assigned mutants (from the stored receipt and reproduced identically
by me):

| id | killing vectors (245 oracle) |
|---|---|
| `json-exact-leaf-true` | `adequacy/residual/value/r13-counter-31984f4/F2_entry`, `…/r13-counter-6f8ee0f/sources`, `…/r14-counter-a31642d/tiers-A`, `…/r14-counter-552cae4/measured_commit`, `…/r13-counter-b576341/admitted_entries`, `…/cache/producer_executions_new_policy` |
| `case-row-isinstance-drop` | `adequacy/residual/malformed/cache/case-rows-int` |
| `baseline-guard-pass` | — (survived; `equivalent`) |
| `nonexact-isinstance-drop` | `adequacy/residual/malformed/r13-counter-b576341/null` |
| `gate-self-consistency` | `adequacy/residual/cache/gate-both-slots-wrong` |
| `status-drop` | `adequacy/residual/cache/status-failed` |
| `measured-commit-drop` | `adequacy/residual/cache/measured-commit-wrong` |
| `harness-revision-drop` | `adequacy/residual/cache/harness-revision-wrong` |
| `inputs-unchanged-drop` | `adequacy/residual/cache/inputs-unchanged-false`, `…/inputs-unchanged-int` |
| `inputs-unchanged-eq` | `adequacy/residual/cache/inputs-unchanged-int` |
| `isolation-residue-falsy` | `adequacy/residual/cache/isolation-residue-null` |
| `checks-all-true-drop` | `cache/value/int-one` (a pre-existing 225 vector — this mutant was already killable) |
| `checks-len-drop` | — (survived; `equivalent`) |
| `caserows-len-drop` | — (survived; `equivalent`) |
| `failures-drop` | `adequacy/residual/summary/auditor-selftest/fail-line` |
| `returncode-drop` | 18 × `exit/*` vectors |
| `aux-drop` | `adequacy/residual/summary/r20-input-binding/extra-inventory` |
| `bm-count-drop` | `adequacy/residual/summary/r20-input-binding/extra-baseline-mismatch` |
| `pass-match-drop` | `adequacy/residual/summary/auditor-selftest/missing-pass-line` |
| `violation-drop` | `adequacy/residual/summary/carry-invariant-probe/violation-line` |

**Each of the 20 appended `adequacy/residual/*` vectors kills at least one assigned mutant, and no appended
vector is dead weight** — every one of the 20 appears in the table above. Conversely every assigned mutant
marked `killed` has at least one appended vector as its killer except `checks-all-true-drop`, whose killer
is the pre-existing `cache/value/int-one`. So the 20 new vectors exactly cover the 19 newly-killable
mutants (one vector, `inputs-unchanged-int`, covers two mutants). That is a tight, non-padded mapping.

The 245-vector oracle's *new* vectors are all `want: false` and all in group `adequacy`, ids prefixed
`adequacy/residual/`. Against the **base** runner the 245 oracle yields 88/245 — so the appended vectors do
not all fail on base. Only one of the 20 (`adequacy/residual/malformed/cache/case-rows-int`) is
base-discriminating; the other 19 are accepted (as `want:false`) by base too. That is expected: these are
*mutant-killing* vectors, not base-discrimination vectors, and the base runner was never the target of the
residual fix. The base-discrimination role is carried by the pre-existing vectors.

### 1d. The oracle file's byte-prefix claim

The instruction said "first 187903 bytes unchanged". Verified:

```
old (HEAD:tests/fixtures/r22-result-oracle.json) len 187910, sha 849a8569…a5cc
new (working tree)                                  len 228138, sha 63de539f…1795
new[:187903] == old[:187903]  →  True
first differing byte offset = 187903 (the '}' → '},' that opens the appended case list)
old['cases'] == new['cases'][:225]  →  True
all 8 non-case top-level keys (schema, source_receipt(+sha), frozen_inventory(+sha), revision, contract) unchanged → True
all 245 case ids unique → True
```

Append-only in the strict sense: no existing case byte changed, only 20 new cases were appended and the
closing bracket moved. ✓

---

## 2. Attack on the three new `equivalent` marks — no distinguishing input found

Method: in-memory differential. I loaded the pristine runner and each mutant with `exec(compile(...))`,
called `summarize_result` directly with the **pinned inventory step** (`census/round-21/step-inventory.json`,
revision-substituted exactly as `tests/fixtures/r22-result-oracle.py` does), and compared `result['matched']`.
**1180 differential cases** per mutant, in three families:

1. `baseline-guard-pass`: 20 hand-built `r20-input-binding` stdouts (digit-count substitutions into the
   real `baseline_mismatches=8` field at 1/8/10/100/1000/4300/4301/5000/10000/20000 digits, extra
   `BASELINE_MISMATCH` lines, extra/missing/duplicated `INVENTORY` lines, a malformed `SUMMARY` line, a
   `total=52000000000000000000000` line, a non-matching group capture via 4 different regexes × 5 captures)
   plus 1160 randomized cache-payload and step-mutation cases.
2. `checks-len-drop` / `caserows-len-drop`: 1160 cases over the real `clean-cache-demonstration` payload
   mutated 8 ways (a check value flipped, an extra check key, a check key removed, a check key renamed,
   `cases` shortened to 0–7 rows, `cases` rows replaced by non-dicts, `cases` set to a non-list, `checks`
   set to a non-dict) crossed with 9 altered `expected["checks"]` values (0/1/32/33/34/33.0/True/False/None)
   and 10 altered `expected["cases"]` values (0/1/3/4/5/6/4.0/True/False/None).

**Result: 0 differences on all three mutants over all 1180 cases.** `baseline-guard-pass`: 0/1180.
`checks-len-drop`: 0/1180. `caserows-len-drop`: 0/1180.

### Finding 1 (minor, disclosed but under-marked) — `baseline-guard-pass` is a *conditional* equivalence

The mutant replaces the `except ValueError: summary_match = False` handler with `pass`. The
`ValueError` is raised by `int(baseline_match.group(group))` when the captured group is not a valid
integer — reachable only when the regex's `(\d+)` group captures something `int()` rejects. Note the
`\d+` group can only match digits, so under the *pinned* regex the only reachable `ValueError` is
CPython's own 4300-digit integer-string conversion limit (`sys.set_int_max_str_digits`), which is exactly
what the pre-existing `summary/r20-input-binding/oversized-count` vector exercises.

Under the pinned step, `baseline_mismatch_count` is `true` (both in `make_steps` and in the frozen
`census/round-21/step-inventory.json`). The mutant therefore cannot change the outcome, because with
`baseline_mismatch_count` set, `summary_match` is later ANDed with
`reported_baseline_mismatches == baseline_mismatch_lines`; on the `ValueError` path
`reported_baseline_mismatches` is left as `None`, and `None == <int>` is `False`, so `summary_match`
becomes `False` regardless of whether the handler set it. Hence equivalent.

**But** it is not equivalent on a step that sets `baseline_mismatch_group` without
`baseline_mismatch_count`. Demonstrated, in memory, on a step copy with `baseline_mismatch_count` removed:

```
off-inventory step (baseline_mismatch_count=False), stdout baseline_mismatches=<5000 nines>:
  original  matched = False
  mutant    matched = True      ← DISTINGUISHING
```

So the equivalence rests entirely on the pinned step's `baseline_mismatch_count: true`. The source comment
says exactly this ("Equivalent under the pinned inventory: the only baseline_mismatch_group step also sets
baseline_mismatch_count, so None == int already forces summary_match False"), so the labelling is **honest
and disclosed**. The only defect is presentational: the `expect` field is the bare string `equivalent`,
with no scope qualifier, and the probe's `scope` string says "Equivalent marks are L1 reasoning, not
proof." A reader of the JSON receipt alone cannot tell that this particular mark is inventory-conditional
while `checks-len-drop`/`caserows-len-drop` are unconditional. **Not a correctness defect.** Smallest
correction if the judge wants it: rename the field value to `equivalent-under-pinned-inventory`, or add a
`scope` field per row.

By contrast `checks-len-drop` and `caserows-len-drop` are **unconditionally** equivalent, and the source
comment says so ("implied by the reviewed-constant length plus exact name/phase identity"). Proof sketch:
`checks.keys() == CACHE_CHECK_NAMES` and `len(CACHE_CHECK_NAMES) == expected["checks"]` together already
force `len(checks) == expected["checks"]` whenever the checks dict is well-formed; dropping the separate
length conjunct cannot change the conjunction's value. Same shape for `case_phases == list(CACHE_CASE_PHASES)`
and `len(CACHE_CASE_PHASES) == expected["cases"]` vs `len(case_rows) == expected["cases"]`. The
off-inventory step mutations I ran (expected values 0/1/32/34/…) confirm this holds beyond the pinned
values. ✓

---

## 3. `stack_soft_limit` — what it records, and what it does not

Field, as of the file I read:

```python
_SOFT_STACK = resource.getrlimit(resource.RLIMIT_STACK)[0]
STACK = 'unlimited' if _SOFT_STACK == resource.RLIM_INFINITY else _SOFT_STACK
```

and it is emitted in **both** receipt paths (`receipt['stack_soft_limit'] = STACK` in `--grade-stdin`, and
`'stack_soft_limit': STACK` in the main probe receipt). Verified present in the stored receipts:
`mutation-adequacy-oracle245.json` → `8388608`; `mutation-adequacy-listed45-oracle225.json` → `8388608`;
`oracle245-baseline.json` → `8388608`.

Observed values on this host: `getrlimit(RLIMIT_STACK)` → `(8388608, -1)`, i.e. soft 8 MiB, hard unlimited.
Under `ulimit -s unlimited` the probe prints `stack_soft_limit: "unlimited"`. Correct and honest.

### Finding 2 (moderate, measurement-relevant) — the soft limit alone does not predict the probe's verdict

`stack-sweep-oracle245.txt` records the sweep the author ran, and it is truthful:

```
stack_kib=8192    base=88/245  changed=245/245  probe killed=38/45  disagreeing=
stack_kib=14336   base=88/245  changed=245/245  probe killed=38/45  disagreeing=
stack_kib=15360   base=88/245  changed=245/245  probe killed=38/45  disagreeing=
stack_kib=16384   base=90/245  changed=245/245  probe killed=36/45  disagreeing=counter-recursion,cache-recursion
stack_kib=unlimited base=90/245 changed=245/245 probe killed=36/45  disagreeing=counter-recursion,cache-recursion
```

I reproduced the two ends of that sweep independently (read-only, in-memory, no receipt written):

```
ulimit -s 8192  → 45-row scope disagreeing = []                          (matches sweep row 1)
ulimit -s 16384 → 45-row scope disagreeing = ['counter-recursion','cache-recursion']   (matches sweep row 4)
```

So the sweep is **accurate**, and `stack_soft_limit` is the right *kind* of field — but on its own it is
**not sufficient** to interpret a stored receipt, because the flip is not at a round soft limit: it sits
between 14336 and 16384 KiB, and the deciding physical fact is not "how big is the soft limit" but "does
this interpreter's C JSON decoder actually raise `RecursionError` on a 100000-deep array". I measured that
predicate directly:

```
ulimit -s 8192  → json.loads('['*100000+'0'+']'*100000) raises RecursionError
ulimit -s 16384 → the same decode SUCCEEDS (parsed ok, depth 1)
```

A reader holding `mutation-adequacy-oracle245.json` (`stack_soft_limit: 8388608`, `disagreeing_with_expect: []`)
cannot tell from the receipt alone whether that verdict would hold on their host; they must consult the
sweep file and interpolate. The author has since (13:41, after the version I was asked to review) added
`depth_100000_decode_raises` to the receipt — which records exactly the decisive predicate — and I
confirmed it works:

```
ulimit -s 8192  → depth_100000_decode_raises = true
ulimit -s 16384 → depth_100000_decode_raises = false
```

So the *current* file is better than the version under review, and the parent is mid-flight on this.
My finding is scoped to the 13:30 version named in my instructions: at that version `stack_soft_limit` was
the only environment field, and it under-determines the verdict.

---

## 4. Receipt-set discrepancies (honest reporting)

### Finding 3 (minor) — `oracle245-baseline.json` is not byte-reproducible

The receipt records the base runner graded via `--grade-stdin` against the 245 oracle: `total 245`,
`pass 88`, `fail 157`, `runner_sha256 1141839963…` (the base runner), `stack_soft_limit 8388608`.

Re-running the same command today:

```
$ git show 41553adb…:census/round-21/run-acceptance.py | python3 -B census/round-22/mutation-adequacy.py --grade-stdin
pass/fail 88/157 — identical
results: 244 of 245 rows identical; 1 row differs:
  id 'adequacy/r13-counter-31984f4/decoder-depth-100000'
  stored: 'RecursionError: Stack overflow (used 8144 kB) while decoding a JSON array from …'
  fresh : 'RecursionError: Stack overflow (used 8148 kB) while decoding a JSON array from …'
```

The `exception` string embeds the *measured stack usage*, which varies run to run. This is the same
non-reproducibility `CritMeasure.md` (D2) already recorded for `oracle225-baseline`, and it persists into
the 245 receipts. It is a property of the runner's exception text, not of the probe's logic. The
pass/fail counts and every decision reproduce exactly. Any wording of the form "the receipts reproduce
exactly" is false for this file; "the receipts reproduce decisions" is true.

`oracle245-changed.json` **does** reproduce exactly — `cur == rec` is `True` for the full JSON object,
including `results`, when produced by `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py`
(exit 0, 245/245).

### Finding 4 (moderate, presentational) — the stored probe receipts no longer match the probe file

The working-tree probe file changed at 13:41 (mtime), *after* the receipts were written at 13:30–13:31.
Concretely:

* `mutation-adequacy-oracle245.json` has **45** mutants and **10** top-level keys.
* `mutation-adequacy-listed45-oracle225.json` has **45** mutants and **10** top-level keys.
* `mutation-adequacy-listed59-oracle245.json` (written 13:40) has **59** mutants and **10** top-level keys.
* The **current** file has **59** mutants and **12** top-level keys (adds `depth_100000_decode_raises`,
  `probe_sha256`).

So `python3 -B census/round-22/mutation-adequacy.py` today prints a receipt that is byte-different from
every stored receipt, and it **exits 1** — `summary.disagreeing_with_expect` lists 14 ids, all of them the
parent's out-of-scope additions (indices 45–58): `numeric-leaves-recursive-base`, `cache-phases-sorted`,
`cache-phases-set`, `json-exact-keys-subset`, `counter-except-no-valueerror`,
`cache-except-no-valueerror`, `summary-group-guard-drop`, `cache-caserows-isinstance-drop`,
`cache-gate-sha-default`, `cache-cleaned-default`, `cache-residue-default`, `cache-status-default`,
`counter-stderr-strip`, `cache-stderr-strip`.

This is **not** a defect in my 20 — it is the parent mid-flight, and the parent has told me the 245 oracle
is being frozen to accept the new witnesses. Two of those 14 I probed anyway, because they bear on whether
the 245 oracle's *coverage* claim is safe to freeze:

* `cache-phases-sorted` / `cache-phases-set` — **genuinely distinguishable**, and the current 245 oracle
  does *not* kill them. In-memory: cache payload with the four `cases` rows' `phase` values **reordered**
  (`unchanged, initial-fresh, dependency-modified, legacy-no-dependencies`) gives
  original `matched=False`, mutant `matched=True`. The 245 oracle has no vector with reordered phases, so
  both survive. **This is a real coverage hole in the 245 oracle** and must be closed before the freeze.
* `cache-gate-sha-default`, `cache-cleaned-default`, `cache-residue-default`, `cache-status-default` —
  all **genuinely distinguishable** by omitting the key entirely from the payload (original `False`,
  mutant `True`), and **not** killed by the 245 oracle.
* `counter-except-no-valueerror` — original `matched=False`, mutant raises `JSONDecodeError` on a
  non-JSON stdout. Not killed by 245.
* `summary-group-guard-drop` — original `matched=False`, mutant raises `AttributeError` on a
  `SUMMARY` line that does not match the regex. Not killed by 245.
* `counter-stderr-strip` / `cache-stderr-strip` — original `matched=False`, mutant `matched=True` on a
  whitespace-only stderr. Not killed by 245.
* `cache-caserows-isinstance-drop` — original `matched=False`, mutant raises `TypeError` when
  `cases` is not a list. Not killed by 245.
* `json-exact-keys-subset` — original `matched=False`; mutant raises `KeyError` when the observed
  exact-JSON payload is *missing* an expected key. Not killed by 245.
* `numeric-leaves-recursive-base` — I could **not** distinguish it on the pinned steps: over 10
  counter-step inputs, `matched` and the full `matched_counts` were identical. [INFERENCE] This one looks
  genuinely equivalent to the current iterative `numeric_leaves` for every input the pinned steps can
  produce; the two differ only in dict-iteration order, which `matched_counts` does not expose. If so it
  should be labelled `equivalent`, not `killed` — but that is the parent's scope, not mine.

I raise these because the parent's stated goal is a freeze of the 245 oracle, and at least eight of the
14 have concrete distinguishing inputs that the 245 oracle does not pin. Flagging is not judging; the
parent owns the decision.

### Finding 5 (minor) — `mutation-adequacy-listed45-oracle225.json` is stale but internally reproducible

The 45-row receipt against the **225** oracle is exactly what the pre-245 state produced, and I reproduced
every one of its 45 rows in memory against `git show HEAD:tests/fixtures/r22-result-oracle.json` (the 225
bytes): **0 row mismatches**, summary identical
(`killed 23, survived 22, disagreeing_with_expect` = the same 15 ids). Its value is as a *before* picture:
it shows the 15 previously-disagreeing mutants that the 20 new vectors close. Cross-check: the 15 ids in
its `disagreeing_with_expect` are exactly the 15 of my 20 that the 245 oracle now kills — every one of my
20 that the 225 oracle left alive is now dead, and the three `equivalent` marks survived both. ✓ That is
the strongest single piece of evidence that the residual fix did what it claims.

---

## 5. Grading stays in memory (verified, no exception)

The instruction asks me to confirm grading stays in memory: no file write, no subprocess.

* **Audit-hook run** (`sys.addaudithook` over `open` with a write mode, `os.remove/rename/mkdir/rmdir/chmod`,
  `subprocess.Popen`, `os.system/exec/posix_spawn/fork`, `shutil.copyfile/move`, `tempfile.mkstemp`),
  wrapping a full `probe.main()`:
  `write/spawn audit events: []`, `total write/spawn events: 0`. 4353 `open()` calls, **all** with mode `'r'`.
* **Filesystem snapshot** across `census/round-22`, `census/round-21`, `tests/fixtures`, `census/round-20`
  before and after a probe run: `NEW files created: []`, `CHANGED files during probe run: []`.
* `sys.dont_write_bytecode = True` is set at the top of both the probe and the runner, and the probe
  imports the runner by `exec(compile(source, '<r22-mutant>', 'exec'))` into a fresh `ModuleType`
  (`mutation-adequacy.py:106–114`), never via `importlib` on a file path. The oracle's `load_runner` is
  monkey-patched to that in-memory loader (`mutation-adequacy.py:104`), so the mutated source never
  touches disk.
* The only `subprocess.Popen` events observed anywhere are the ones **I** created in the audit harness
  itself (my `git show` subprocess and my own `python3 -B …` invocation) — not the probe's.
* `census/round-21/__pycache__/run-acceptance.cpython-314.pyc` exists on disk (mtime 13:05, i.e. before my
  review and before the probe's current form), but the probe did not create or modify it — the before/after
  snapshot shows `CHANGED files: []`. It is a leftover from an earlier, differently-invoked run, and
  `git status` shows `census/round-21/__pycache__/` as untracked. It is **not** a product of the current
  probe. Worth a `rm -rf` by whoever owns the lane before commit, since it is untracked noise.
* The runner's real `main()` was never invoked: `grade()` calls `oracle_mod.main()` with the oracle's own
  `load_runner` replaced, and `oracle_mod.main()` only calls `module.summarize_result(...)` per case. The
  runner's `main()` (which would run `git clone`, subprocesses, temp dirs) is never reached. Confirmed by
  the zero spawn events.

---

## 6. Residual risk and verification gaps

* **`stack_soft_limit` on the reviewed version under-determines the verdict** (Finding 2). Fixed in the
  current file by `depth_100000_decode_raises`; my measurements show that field is the right predicate
  (true at 8 MiB, false at 16 MiB).
* **The 245 oracle does not pin the 8 distinguishable mutants** enumerated in Finding 4. The parent is
  freezing the oracle; these need vectors (reordered phases; omitted `gate.sha256` / `isolation.cleaned` /
  `isolation.residue` / `status` keys; non-JSON counter stdout; non-matching `SUMMARY` line; whitespace-only
  stderr; non-list `cases`; exact-JSON payload missing a key) or an explicit `equivalent` relabel.
* **`oracle245-baseline.json` will never reproduce byte-for-byte** while the runner's `RecursionError`
  message embeds measured stack usage (Finding 3). Either store only the exception *type* for `RecursionError`,
  or stop claiming byte-exact reproduction.
* **`numeric-leaves-recursive-base`** appears genuinely equivalent on the pinned steps (Finding 4,
  [INFERENCE]); if the freeze treats it as `killed`, it will keep showing as a disagreement for a reason
  no vector can fix.
* Not verified by me: the claim that the 20 new oracle vectors are *correct* as specifications of intent
  (i.e. that `want: false` is the right answer for each), rather than merely *effective* at killing the
  mutants. I verified each kills exactly the mutant it is named for and that the pristine runner accepts
  all 245 (245/245, exit 0) and the base runner rejects the one base-discriminating vector — but the
  semantic intent of each `want` was not independently re-derived.
* Not verified by me: the real acceptance `main()` path end-to-end. Out of bounds for this seat (the
  instruction forbids running the real acceptance `main()`), and it is out of scope for the mutant review.

---

## 7. Commands run (all read-only; no scratch file written)

```
git -C … log --oneline -3 ; git status --porcelain ; git diff HEAD -- census/round-22/mutation-adequacy.py
git -C … diff 41553adb… HEAD -- census/round-21/run-acceptance.py          # origin labels
git -C … show 41553adb…:census/round-21/run-acceptance.py                    # base clause inventory
git -C … show HEAD:tests/fixtures/r22-result-oracle.json                      # the 225 bytes, in memory
python3 -B census/round-22/mutation-adequacy.py                              # current probe (exit 1 today)
python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py
git show 41553adb…:census/round-21/run-acceptance.py | python3 -B census/round-22/mutation-adequacy.py --grade-stdin
bash -c "ulimit -s N; python3 -B …"                                          # N ∈ {8192, 16384, unlimited}
python3 -B - <heredoc>                                                       # all differentials: exec(compile(...)) only
```

Everything else was `python3 -B -` one-liners that read and print. No file was written except this report.
No tool was installed or upgraded.
