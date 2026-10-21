STATUS: PASS

# RevProbe258 — independent review of the 14 diff-enumerated mutants and the 258-byte adequacy receipts

Seat: `SoujiR22-2.RevProbe258-7` (reviewer, non-author). Not the author of the
13 appended vectors or the 14 appended mutants; no author claim is admitted
here. Review is bounded to the last 14 mutants after the
`# Diff-enumerated survivors` comment in `census/round-22/mutation-adequacy.py`,
the `census/round-22/oracle258-*.json` receipts and
`census/round-22/mutation-adequacy-oracle258.json`.

Host: Python 3.14.8, `RLIMIT_STACK` soft 8388608 bytes (8192 KiB),
`sys.getrecursionlimit()` 1000. No tool was installed or updated. The only
file written is this report. Every mutant, every historical oracle byte string
and every grade was held in memory (`python3 -B -` heredoc, `exec(compile(...))`,
the probe's own `mutate()` / `grade()`, `json.loads` on in-memory bytes). No
acceptance main/replay/producer was executed; only the oracle and the probe
were run, plus `git show` of committed bytes.

## Verdict

The 14 appended mutants are exactly the mutants CritAdequacy245's N1–N4/R1–R5
require, each anchored to the current runner at the reviewed line, each
non-degenerate and syntactically valid, and each killed by the intended
witness. No mutant is killed by an incidental syntax error, and no mutant
changes any oracle vector other than its own. The three headline numbers
reproduce: 52/59 killed with 7 named equivalents and 0 disagreements, 258/258
on the current runner, 99/258 with 8 exceptions on the base, 20/20 positives on
both.

Two disclosures are carried forward rather than treated as defects (they are
already stated in the lesson): the 258 base receipt is not byte-reproducible in
the RecursionError stack-use text, and only 2 of the 13 new witnesses
discriminate base (11 are retained-behaviour pins). Details and evidence below.

## Reviewed artefacts (observed sha256)

- `tests/fixtures/r22-result-oracle.json` — `970b7362a0f0db9636e4141b12f798ca339b29fe90d23fadb4736b9634098027`, 382529 bytes, 258 cases.
- `census/round-22/mutation-adequacy.py` — `5a46027cde7a50fa360d7cf02849d06589249cb9dede8527e152aa262dbbcd07`, 59 listed mutants.
- `census/round-21/run-acceptance.py` (runner under test) — `00d0e9c2fda2fde2d21cb74b1a1dd5b1db7b1ea679cdfd4239d91aa186e080a6`; identical to `git show 4f83fd2:` and to the working tree (no runner change after `4f83fd2`).
- `census/round-22/mutation-adequacy-oracle258.json`, `oracle258-changed.json`, `oracle258-baseline.json` — as stored.

Base runner under comparison: `git show 41553adb:census/round-21/run-acceptance.py`,
sha256 `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`.

## 1. The last 14 mutants: anchors vs the current runner

The comment `# Diff-enumerated survivors from residual CritAdequacy245` is
immediately followed by exactly 14 entries and they are the last 14 of the
59-entry `MUTANTS` list (`probe.MUTANTS[-14:]` equals that block, verified).
For each entry the anchor was located in the current runner source and the
replacement was exercised in memory:

| # | mutant id | anchor line(s) in current runner | anchor occurrences | syntax | no-op? |
|---|---|---|---|---|---|
| 1 | `numeric-leaves-recursive-base` | 364–371 (iterative walk) | 1 | OK | no |
| 2 | `cache-phases-sorted` | 513 `case_phases == list(CACHE_CASE_PHASES)` | 1 | OK | no |
| 3 | `cache-phases-set` | 513 | 1 | OK | no |
| 4 | `json-exact-keys-subset` | 380 `return (observed.keys() == expected.keys()` | 1 | OK | no |
| 5 | `counter-except-no-valueerror` | 469 `except (ValueError, TypeError, RecursionError):` (occurrence 0) | 2 total, occ 0 selected | OK | no |
| 6 | `cache-except-no-valueerror` | 496 same text (occurrence 1) | 2 total, occ 1 selected | OK | no |
| 7 | `summary-group-guard-drop` | 426 `if group is not None and summary_match:` | 1 | OK | no |
| 8 | `cache-caserows-isinstance-drop` | 511 `isinstance(case_rows, list) and len(case_rows) == expected["cases"]` | 1 | OK | no |
| 9 | `cache-gate-sha-default` | 522 `gate.get("sha256") == gate_sha` | 1 | OK | no |
| 10 | `cache-cleaned-default` | 524 `isolation.get("cleaned") is expected` | 1 | OK | no |
| 11 | `cache-residue-default` | 525 `and isolation.get("residue") == []` | 1 | OK | no |
| 12 | `cache-status-default` | 508 `payload.get("status") == expected["status"]` | 1 | OK | no |
| 13 | `counter-stderr-strip` | 492 `matched = matched and json_match and not stderr` | 1 | OK | no |
| 14 | `cache-stderr-strip` | 536 `matched = matched and demo_match and not stderr` | 1 | OK | no |

All 14 anchor lines coincide with the line numbers cited by
`.ufo/waves/round-22/residual/CritAdequacy245.md` (362–372 / 380 / 469 / 496 /
426 / 511 / 522 / 524 / 525 / 508 / 492 / 536), so the mutants still bind the
clauses the critic reviewed.

Occurrence semantics were checked rather than assumed: the anchor
`except (ValueError, TypeError, RecursionError):` occurs exactly twice in the
runner (line 469 inside `kind == "counter"`, line 496 inside
`kind == "cache-demo"`). `mutate(..., occurrence=0)` yields a source whose
changed line is inside the counter branch and `occurrence=1` inside the
cache-demo branch; this is independently confirmed by which witness kills each
mutant (counter witness vs cache witness, table 2).

`numeric-leaves-recursive-base` is a faithful revert: the mutated
`numeric_leaves` function is byte-identical to the base `41553adb` function
(compared as full function text) and its replacement text does not occur
anywhere in the current runner. It is a genuine reversion of the r22
iterative repair, not a paraphrase.

Whole-list hygiene (all 59, in scope for the "no incidental kill" question):
every mutant compiles (`compile()` succeeds), no mutant is a no-op (mutated
source differs from the pristine source), and no two mutants share a source
hash. So no malformed or duplicated mutant can be inflating the kill count.

## 2. Correspondence with CritAdequacy245 N1–N4 / R1–R5

Every finding is realised by the exact mutation the critic prescribed, with the
critic's own origin label:

| finding | critic's prescribed mutation | probe mutant(s) | origin label | prescribed distinguishing input | witness present |
|---|---|---|---|---|---|
| N1 | restore base recursive `numeric_leaves` | `numeric-leaves-recursive-base` | `r22-changed` | deep dict (base raises `RecursionError`) | `adequacy/residual2/n1/r13-counter-31984f4/deep-dict-1200` |
| N2 | order-insensitive phase equality | `cache-phases-sorted`, `cache-phases-set` | `r22-changed` | swapped `cases[0]`/`cases[1]` phases | `adequacy/residual2/n2/cache/phases-swapped` |
| N3 | `observed.keys() <= expected.keys()` | `json-exact-keys-subset` | `r22-changed` | expected key `sources` deleted | `adequacy/residual2/n3/r13-counter-31984f4/missing-sources` |
| N4 | `except (TypeError, RecursionError)` | `counter-except-no-valueerror`, `cache-except-no-valueerror` | `r22-changed` | empty stdout | `adequacy/residual2/n4/r13-counter-31984f4/empty-stdout`, `.../n4/cache/empty-stdout` |
| R1 | `if group is not None:` | `summary-group-guard-drop` | `pre-existing` | `r20-input-binding` empty stdout | `adequacy/residual2/r1/r20-input-binding/empty-stdout` |
| R2 | drop `isinstance(case_rows, list)` | `cache-caserows-isinstance-drop` | `pre-existing` | `cases: null` | `adequacy/residual2/r2/cache/cases-null` |
| R3 | `.get("sha256", gate_sha)` / `.get("cleaned", True)` / `.get("residue", [])` | `cache-gate-sha-default`, `cache-cleaned-default`, `cache-residue-default` | `pre-existing` | `gate: {}`, `isolation` without `cleaned`, without `residue` | `.../r3/cache/gate-empty`, `.../isolation-missing-cleaned`, `.../isolation-missing-residue` |
| R4 | `.get("status", "ok")` | `cache-status-default` | `pre-existing` | payload without `status` | `.../r4/cache/missing-status` |
| R5 | `not stderr` → `not stderr.strip()` | `counter-stderr-strip`, `cache-stderr-strip` | `pre-existing` | stderr `"\n"` | `.../r5/r13-counter-31984f4/newline-stderr`, `.../r5/cache/newline-stderr` |

9 findings, 14 mutants, 13 witnesses — the count matches exactly, and each
witness id embeds its finding key (`n1 n2 n3 n4 r1 r2 r3 r4 r5`), so the
mapping is one-to-one and auditable from the ids alone.

## 3. Each mutant is killed by the correct vector, and only by it

For every one of the 14 mutants I graded the mutated source against the
current 258 oracle and compared each case's `observed` and `exception` with
the pristine runner's, case by case:

| mutant | killing vector | pristine | mutant | other vectors changed |
|---|---|---|---|---|
| `numeric-leaves-recursive-base` | `residual2/n1/.../deep-dict-1200` | `False` | `None` + `RecursionError: maximum recursion depth exceeded` | none |
| `cache-phases-sorted` | `residual2/n2/cache/phases-swapped` | `False` | `True` | none |
| `cache-phases-set` | `residual2/n2/cache/phases-swapped` | `False` | `True` | none |
| `json-exact-keys-subset` | `residual2/n3/.../missing-sources` | `False` | `None` + `KeyError: 'sources'` | none |
| `counter-except-no-valueerror` | `residual2/n4/r13-counter-31984f4/empty-stdout` | `False` | `None` + `JSONDecodeError: Expecting value` | none |
| `cache-except-no-valueerror` | `residual2/n4/cache/empty-stdout` | `False` | `None` + `JSONDecodeError` | none |
| `summary-group-guard-drop` | `residual2/r1/r20-input-binding/empty-stdout` | `False` | `None` + `IndexError: list index out of range` | none |
| `cache-caserows-isinstance-drop` | `residual2/r2/cache/cases-null` | `False` | `None` + `TypeError: object of type 'NoneType' has no len()` | none |
| `cache-gate-sha-default` | `residual2/r3/cache/gate-empty` | `False` | `True` | none |
| `cache-cleaned-default` | `residual2/r3/cache/isolation-missing-cleaned` | `False` | `True` | none |
| `cache-residue-default` | `residual2/r3/cache/isolation-missing-residue` | `False` | `True` | none |
| `cache-status-default` | `residual2/r4/cache/missing-status` | `False` | `True` | none |
| `counter-stderr-strip` | `residual2/r5/r13-counter-31984f4/newline-stderr` | `False` | `True` | none |
| `cache-stderr-strip` | `residual2/r5/cache/newline-stderr` | `False` | `True` | none |

Findings from that table:

- **Correct vector.** Each mutant's only failing vector is the witness for its
  own finding. The counter/cache split of N4 and R5 lands on the counter and
  cache witnesses respectively, which independently confirms the `occurrence`
  parameter selects the intended branch.
- **No incidental syntax-error kill.** Every mutant compiles, and each kill is
  a *semantic* difference on the target clause: either the matched boolean
  flips (`False` → `True`, i.e. the mutant accepts a payload the contract
  must reject) or the mutant raises where the contract requires a retained
  mismatch. The six exception-shaped kills (`RecursionError`, `KeyError`,
  `JSONDecodeError` ×2, `IndexError`, `TypeError`) are exactly the C1 axis
  "malformed shape becomes a mismatch, not an exception": the pristine runner
  returns `matched=False` while the mutant raises. A syntax-error kill would
  have failed *all* 258 vectors; no mutant changes any vector but its own
  (`other vectors changed: none` for all 14).
- **Single-cause witnesses.** The 13 new witnesses differ from the pinned
  public outputs by exactly one edit, verified structurally against
  `census/round-21/final-out-S1.json`: `n3` deletes the `"sources": 33` entry
  from the pinned counter stdout (one insert in the diff); `r3/isolation-missing-cleaned`
  deletes `"cleaned": true`; `r3/isolation-missing-residue` deletes `"residue": []`;
  `r4/missing-status` deletes `"status": "ok"`; `r2/cases-null` sets `cases` to
  `null`; `n2/phases-swapped` swaps `cases[0]` and `cases[1]` (element 0 of the
  swapped array equals the pinned element 1 and vice versa, elements 2–3
  unchanged, phase order `initial-fresh, unchanged` → `unchanged, initial-fresh`);
  `n1/deep-dict-1200` is a 7201-byte literal of 1200 nested `{"a":…}` levels
  whose decode succeeds and whose *iterative* walk yields one numeric leaf,
  while the base recursive walk raises `RecursionError` at recursion limit
  1000 (verified independently in memory).

## 4. Reproduction of the headline numbers

- **Probe on the current 258 oracle.** `python3 -B census/round-22/mutation-adequacy.py`
  → exit 0; stdout byte-equal (`cmp`) to `census/round-22/mutation-adequacy-oracle258.json`
  (both sha256 `943516c3fca8cfe63666429d856632ac3b730f2455cf60c08f50c3d56c80da0b`).
  Summary `mutants 59, killed 52, survived 7, disagreeing_with_expect []`;
  `pristine {exit 0, pass 258, fail 0}`.
- **Oracle on the current runner.**
  `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py`
  → exit 0, stdout byte-equal to `census/round-22/oracle258-changed.json`
  (258 pass / 0 fail / 0 exceptions; `runner_sha256 00d0e9c2…e080a6`).
- **Base.** `git show 41553adb:… | python3 -B census/round-22/mutation-adequacy.py --grade-stdin`
  → exit 1, 99 pass / 159 fail, 8 exceptions, `runner_source "stdin, graded in memory"`,
  `runner_sha256 1141839963d0…eaa2b` (equal to the base bytes' own sha256).
  Compared with the stored `oracle258-baseline.json`: identical id set, **0
  decision-level differences** (`observed`/`pass`/`expected` all equal).
- **20/20 positives.** The oracle holds 20 `want: true` cases; base passes
  20/20 and changed passes 20/20.
- **Base outcome taxonomy** (recomputed): 79 want-False cases base rejects
  correctly, 151 want-False cases base accepts (**false greens**), 8 base
  exceptions, 20 positives. Base fail 159 = 151 + 8, base pass 99 = 79 + 20.
  This matches SCORECARD's "159 discriminating; 8 base exceptions; 151 false
  greens; positive 20/20 both".
- **The 7 equivalents** are exactly the seven named in the lesson
  (`nonexact-keyin-get`, `failed-checks-to-eq`, `names-len-constant`,
  `phases-len-constant`, `baseline-guard-pass`, `checks-len-drop`,
  `caserows-len-drop`) and survive unchanged. I re-checked their stated
  preconditions against the current runner and the frozen inventory
  (`census/round-21/step-inventory.json`): no counter expectation contains a
  null leaf (so `.get(key)` cannot satisfy a non-null expectation under
  `json_exact`), the cache expectation's `failed_checks` is literally `[]`,
  `checks.keys() == CACHE_CHECK_NAMES` plus `len(CACHE_CHECK_NAMES) == E`
  implies `len(checks) == E`, `case_phases == list(CACHE_CASE_PHASES)` plus
  `len(CACHE_CASE_PHASES) == E` implies `len(case_rows) == E`, and the only
  step with `baseline_mismatch_group` (`r20-input-binding`) also sets
  `baseline_mismatch_count`, so `None == count` already forces
  `summary_match = False`. The equivalence reasoning holds on the current
  source and pinned inventory; it remains conditional on that inventory, as
  the lesson states.
- **Round-trip of the 245→258 delta.** All 59 mutant ids are identical between
  `mutation-adequacy-listed59-oracle245.json` and `mutation-adequacy-oracle258.json`,
  and every `mutant_sha256` matches the value recomputed from the current probe
  (0 mismatches). Exactly the 14 appended mutants change `observed` from
  `survived` to `killed`; the other 45 are unchanged. This is the intended
  "14 additional mutants all survived 245 and are killed by 258" claim, verified
  rather than restated.

## 5. Environment fields: probe hash, decoder outcome, stack bytes

- `probe_sha256` recorded in `mutation-adequacy-oracle258.json` =
  `5a46027cde7a50fa360d7cf02849d06589249cb9dede8527e152aa262dbbcd07` = sha256
  of the current `census/round-22/mutation-adequacy.py` on disk = the value the
  probe computes for itself at run time (`probe.PROBE_SHA256`). All three agree.
- `depth_100000_decode_raises: true` in the receipt. Direct host observation,
  independent of the probe: `json.loads('['*100000 + '0' + ']'*100000)` raises
  `RecursionError` on this host. The runner's own decoder path shows the same
  (the `adequacy/.../decoder-depth-100000` cases are red on base with
  `RecursionError`). The two catch-repair mutants
  (`counter-recursion`, `cache-recursion`) are killed only under that
  condition, and the receipt records the condition rather than asserting a
  universal threshold. Confirmed: no threshold claim is made anywhere in the
  reviewed material.
- `stack_soft_limit: 8388608` in both `mutation-adequacy-oracle258.json` and
  `oracle258-baseline.json` equals this host's `resource.getrlimit(RLIMIT_STACK)`
  soft limit, and 8388608 = 8192 KiB, matching the "8192-KiB soft stack"
  wording in SKILL.md/SCORECARD.md and the lesson.

## 6. The listed59-oracle245 receipt is historical, not claimed current

`census/round-22/mutation-adequacy-listed59-oracle245.json` records
`oracle_sha256 63de539f…51795` and `oracle_total 245` — the pre-append oracle
— and its summary is the red "before new witnesses" state (38 killed, 21
survived, 14 disagreeing: exactly the 14 appended mutants). It is described as
historical everywhere it is cited: `SKILL.md:223` ("historical245 oracle bytes
with current59-mutant list must be red (14 non-equivalent survivors, …)"),
`LOG.md:1422` ("Historical red receipt listed59-oracle245.json has14
non-equivalent survivors; final mutation-adequacy-oracle258.json exits0"),
`corpus/lessons/round-22.md:24` ("Historical red receipts: … Final receipt:
mutation-adequacy-oracle258.json"). No document presents it as the current
result. The current receipts name the 258 oracle
(`970b7362…98027`, `oracle_total 258`) and the current probe hash.

Two completeness notes, neither a contradiction of the claims:

- The 245-byte oracle is not stored as an artifact anywhere in the tree. It is
  nevertheless exactly reconstructible: truncating the current 258-byte file
  at the `adequacy/residual2/n1/...` case boundary and closing the JSON array
  yields 228138 bytes with sha256 `63de539f…51795`, i.e. the historical bytes
  bit-for-bit. (I validated the same truncation method against the committed
  225-byte oracle: the reconstruction is byte-identical to
  `git show HEAD~1:tests/fixtures/r22-result-oracle.json`, sha256 `849a8569…a5cc`,
  187910 bytes.) Grading the current 59-mutant list against those reconstructed
  245 bytes in memory reproduces the stored historical receipt's 59 mutant rows
  **exactly** — same `observed`, same `killing_vectors`, same `mutant_sha256`,
  same `expect`, same `agrees`, and the same summary
  (`killed 38, survived 21`, same 14 disagreeing ids). The historical red
  receipt is therefore reproducible on demand.
- The stored historical receipt predates the `probe_sha256` /
  `depth_100000_decode_raises` fields, so it carries no probe identity of its
  own; the current probe does emit both, and the current receipt binds them.
  This is consistent with the historical label, not a defect in the claim.

## 7. Findings by severity

**No blocking finding.**

Minor (already disclosed in the corpus, re-confirmed here, no correction
required):

1. *Base receipt is not byte-reproducible.* `oracle258-baseline.json` stores
   `RecursionError: Stack overflow (used 8156 kB)` for the two depth-100000
   cases; fresh runs on this host produce `8152 kB`, `8144 kB` and `8140 kB`
   across three runs of the identical command. Decisions, ids, digests and the
   99/258 and 8-exception counts reproduce exactly; only the environment-
   dependent stack-use text varies. The lesson already states this class of
   variance ("receipts exactly is false for depth-error message bytes:
   decisions and runner/oracle digests reproduce, but stack-use text varies"),
   and no current document claims byte-exact reproduction of the 258 base
   receipt. Verified, not a contradiction.
2. *Base discrimination of the 13 new witnesses.* Exactly 2 discriminate base:
   `n1` (base raises `RecursionError`, base observed `None`) and `n2` (base
   observes `True`, a false green). The other 11 also reject on base, so they
   pin retained behaviour rather than prove a base→changed repair. This
   matches the lesson's wording ("The13 add2 base discriminators … Remaining11
   are retained-behaviour/malformed-input pins") and the critic's own
   assessment. Q53's "a repair witness must discriminate" clause is therefore
   exercised only where the runner behaviour actually changed (the r22
   iterative walk and the r22 ordered-phase conjunct); for N3/N4/R1–R5 the
   witnesses kill the listed mutants, which is what Q53's enumeration clause
   requires.

Residual risk / limits of this review (stated, not defects):

- The 59 mutants are the author's enumeration. My checks establish that these
  14 are correct, non-degenerate, correctly anchored and correctly killed;
  they do not establish that the enumeration is complete over the diff's
  conjuncts. Both the lesson and SKILL.md already state "no exhaustive
  mutant-space claim".
- Equivalence of the 7 survivors is conditional on the frozen inventory
  (checked, above) and is reasoning about the pinned inputs, not a proof of
  global mutation equivalence.
- The cache-demo positives depend on live `tools/souji-evidence-cache.py`
  bytes (sha256 `dd279ba9…39d6`), which the oracle does not hash. That is an
  unchanged, disclosed non-hermetic dependency, not introduced here.
- Depth behaviour is environment-bound on this host; a host where the
  100000-deep decode succeeds would turn `counter-recursion` and
  `cache-recursion` into survivors. The receipts record the direct decode
  outcome precisely so this is visible rather than implied.

## Commands run (all read-only; no acceptance main/replay/producer)

- `python3 -B census/round-22/mutation-adequacy.py` (exit 0) and `cmp` against
  `census/round-22/mutation-adequacy-oracle258.json`.
- `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py`
  (exit 0) and `cmp` against `census/round-22/oracle258-changed.json`.
- `git show 41553adb:census/round-21/run-acceptance.py | python3 -B census/round-22/mutation-adequacy.py --grade-stdin`
  (exit 1) and a field-level comparison against `census/round-22/oracle258-baseline.json`.
- `python3 -B -` heredocs that import the probe and the oracle modules and then:
  build each mutant with `probe.mutate()`; compile each mutated source;
  grade pristine and mutated runners with `probe.grade()`; diff every case's
  `observed`/`exception` between pristine and mutant; grade the reconstructed
  245-byte oracle bytes; recompute every `mutant_sha256`; and exercise
  `numeric_leaves` iteratively and recursively on the 1200-deep literal.
- `git show`, `git log --all`, `git diff` for the runner and oracle history;
  `sha256sum`/`cmp` for byte comparisons.
