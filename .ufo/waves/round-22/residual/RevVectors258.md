STATUS: PASS

# RevVectors258: bounded non-author resolution review of the 13 `adequacy/residual2/*` vectors (souji r22 C1 calibration)

Seat: `SoujiR22-2.RevVectors258-7` (reviewer, non-author).
Reviewed author: `SoujiR22-2` (replacement L1). Reviewed finding: `CritAdequacy245` (N1–N4, R1–R5).

## Scope and method

Bounded to the 13 appended `adequacy/residual2/*` vectors and the resolution of
CritAdequacy245 N1–N4/R1–R5. No search for unrelated extra mutants. Every mutant was
rebuilt from the literal source anchors and graded in memory; no scratch file was
written to the lane or to `/tmp` (two transient `/tmp` files created in the first
minute were removed immediately; all later work was in-memory via
`python3 -B -` heredocs and pipes).

Observed artefacts (sha256, working tree = HEAD `473e98a`):

- oracle `tests/fixtures/r22-result-oracle.json`: `970b7362a0f0db9636e4141b12f798ca339b29fe90d23fadb4736b9634098027` (258 cases)
- probe `census/round-22/mutation-adequacy.py`: `5a46027cde7a50fa360d7cf02849d06589249cb9dede8527e152aa262dbbcd07` (59 mutants)
- runner under test `census/round-21/run-acceptance.py`: `00d0e9c2fda2fde2d21cb74b1a1dd5b1db7b1ea679cdfd4239d91aa186e080a6`
- base runner `41553adb:census/round-21/run-acceptance.py`: `1141839963d04e9e1b968d123fa8ffebeef5d33438537cdc636350c970eeaa2b`
- pinned receipt `census/round-21/final-out-S1.json`: `bc53a752…38fe` (matches `source_receipt_sha256`)
- pinned inventory `census/round-21/step-inventory.json`: `8b7b1cd8…d1310` (matches `frozen_inventory_sha256`)

Host: Python 3.14.8, `sys.getrecursionlimit()` 1000, soft stack 8388608 bytes.
No tool was installed or updated. The only file written is this report.

## Verdict

**PASS.** All 13 vectors are correctly constructed, correctly fed, and correctly
wanted `false`. Each of the 14 additional mutants is killed by exactly one
residual2 vector, and no residual2 vector is redundant. The two
base-discriminating vectors behave exactly as the author claimed, and the other
11 are `False` on base, matching the claim.

Two observations are recorded as residual risk (not defects): the N1 deep-dict
witness has a narrow `sys.getrecursionlimit()` margin, and the base receipt is
not byte-reproducible because the CPython `RecursionError` message embeds a
stack-usage number. Neither changes a vector's `want`, a feed, or a mutant kill.

## Independent reconstruction of every delta

Each delta was rebuilt from the pinned `final-out-S1.json` stdout for the named
step plus the pinned `step-inventory.json` expectation, then compared to the
effective input the fixture actually feeds (the oracle harness applies
`case['stdout']`, then `json_set` paths, else the pinned record stdout; stderr
likewise). All 13 matched byte-for-byte or exactly-under-JSON-canonicalisation.

| # | vector id | step | delta source | reconstruction |
|---|---|---|---|---|
| 1 | `…/n1/r13-counter-31984f4/deep-dict-1200` | r13-counter-31984f4 | literal `{"a":*1200 + "0" + "}"*1200` | exact literal match (`True`) |
| 2 | `…/n2/cache/phases-swapped` | clean-cache-demonstration | `json_set ["cases"]` → pinned rows reordered `[1,0,2,3]` | effective stdout identical to pinned-with-`cases` permuted; fixture list equals pinned rows `[cl[1],cl[0]]+cl[2:]` |
| 3 | `…/n3/r13-counter-31984f4/missing-sources` | r13-counter-31984f4 | pinned stdout minus `"sources": 33, ` | pinned-minus-field is byte-identical modulo the pinned trailing `\n` (fixture omits it; the decoded document is identical) |
| 4 | `…/n4/r13-counter-31984f4/empty-stdout` | r13-counter-31984f4 | stdout `""` | exact |
| 5 | `…/n4/cache/empty-stdout` | clean-cache-demonstration | stdout `""` | exact |
| 6 | `…/r1/r20-input-binding/empty-stdout` | r20-input-binding | stdout `""` | exact |
| 7 | `…/r2/cache/cases-null` | clean-cache-demonstration | `json_set ["cases"] = null` on pinned payload | derived effective stdout identical to fixture effective |
| 8 | `…/r3/cache/gate-empty` | clean-cache-demonstration | `json_set ["gate"] = {}` | effective stdout differs from pinned at exactly `['gate']` |
| 9 | `…/r3/cache/isolation-missing-cleaned` | clean-cache-demonstration | pinned payload minus `isolation.cleaned` | deep diff: only `/isolation/cleaned` absent; `measured_commit`/`harness_revision` still equal the revision; `gate.sha256` present |
| 10 | `…/r3/cache/isolation-missing-residue` | clean-cache-demonstration | pinned payload minus `isolation.residue` | deep diff: only `/isolation/residue` absent |
| 11 | `…/r4/cache/missing-status` | clean-cache-demonstration | pinned payload minus `status` | deep diff: only `/status` absent; `measured_commit`/`harness_revision` still equal the revision |
| 12 | `…/r5/r13-counter-31984f4/newline-stderr` | r13-counter-31984f4 | stderr `"\n"`, stdout = pinned | exact (stdout equals pinned; stderr `"\n"`) |
| 13 | `…/r5/cache/newline-stderr` | clean-cache-demonstration | stderr `"\n"`, stdout = pinned | exact |

Every vector is a single-cause delta against the pinned record. No vector alters
an unrelated conjunct, and no vector's payload diverges in more than the one
named field. Vector 2 is the only one that reorders rather than deletes, and
reordering the two first case rows changes exactly one thing: the order of
`case_phases`, which is what the ordered-phase conjunct compares.

## Per-vector results (independent grading, in memory)

Grading was done twice and independently: (a) through the unchanged
`tests/fixtures/r22-result-oracle.py` with `load_runner` monkeypatched to
`exec(compile(source))` for a chosen source string, and (b) through the
author's own probe via `python3 -B census/round-22/mutation-adequacy.py
--grade-stdin` on the current and base sources.

| # | vector id | want | current source | base source `41553adb` | base discriminating? |
|---|---|---|---|---|---|
| 1 | `…/n1/…/deep-dict-1200` | false | `False` (no exception) | **`None` + `RecursionError: maximum recursion depth exceeded`** | yes — base raises |
| 2 | `…/n2/cache/phases-swapped` | false | `False` | **`True`** (false green) | yes — base accepts reordered phases |
| 3 | `…/n3/…/missing-sources` | false | `False` | `False` | no (regression pin) |
| 4 | `…/n4/…/empty-stdout` | false | `False` | `False` | no |
| 5 | `…/n4/cache/empty-stdout` | false | `False` | `False` | no |
| 6 | `…/r1/…/empty-stdout` | false | `False` | `False` | no |
| 7 | `…/r2/cache/cases-null` | false | `False` | `False` | no |
| 8 | `…/r3/cache/gate-empty` | false | `False` | `False` | no |
| 9 | `…/r3/cache/isolation-missing-cleaned` | false | `False` | `False` | no |
| 10 | `…/r3/cache/isolation-missing-residue` | false | `False` | `False` | no |
| 11 | `…/r4/cache/missing-status` | false | `False` | `False` | no |
| 12 | `…/r5/…/newline-stderr` | false | `False` | `False` | no |
| 13 | `…/r5/cache/newline-stderr` | false | `False` | `False` | no |

All 13 current-source observations are exactly `False` (not an exception), so
every `want=false` is met by a clean negative decision on the changed runner.
The claim "two base discriminators (deep dictionary → base exception; phase
order → base `True`), remaining 11 base `False`" is confirmed exactly.

For vector 2, the sole-cause claim was checked directly against the runner:
the pinned payload grades `matched=True`, the fixture's swapped payload grades
`matched=False`, and swapping the two rows back in the *swapped* payload
restores `matched=True`. The rejection is caused by phase order and nothing else.

## Mutant resolution: the 14 added mutants

Each of the 14 mutants named after the `# Diff-enumerated survivors` comment was
independently rebuilt from the literal anchor text against the current runner
(not read from the probe's list) and graded against the 258 oracle in memory.
Every one is killed by exactly one vector, and every vector kills at least one
mutant, with no vector doing redundant work.

| mutant | killing vector | flip on the current runner | independent result |
|---|---|---|---|
| `numeric-leaves-recursive-base` | `n1/…/deep-dict-1200` | `False` → `RecursionError: maximum recursion depth exceeded` | killed (1 killer) |
| `cache-phases-sorted` | `n2/cache/phases-swapped` | `False` → `True` | killed (1 killer) |
| `cache-phases-set` | `n2/cache/phases-swapped` | `False` → `True` | killed (1 killer) |
| `json-exact-keys-subset` | `n3/…/missing-sources` | `False` → `KeyError: 'sources'` | killed (1 killer) |
| `counter-except-no-valueerror` | `n4/…/empty-stdout` | `False` → `JSONDecodeError: Expecting value` | killed (1 killer) |
| `cache-except-no-valueerror` | `n4/cache/empty-stdout` | `False` → `JSONDecodeError: Expecting value` | killed (1 killer) |
| `summary-group-guard-drop` | `r1/…/empty-stdout` | `False` → `IndexError: list index out of range` | killed (1 killer) |
| `cache-caserows-isinstance-drop` | `r2/cache/cases-null` | `False` → `TypeError: 'NoneType' object has no len()` | killed (1 killer) |
| `cache-gate-sha-default` | `r3/cache/gate-empty` | `False` → `True` | killed (1 killer) |
| `cache-cleaned-default` | `r3/cache/isolation-missing-cleaned` | `False` → `True` | killed (1 killer) |
| `cache-residue-default` | `r3/cache/isolation-missing-residue` | `False` → `True` | killed (1 killer) |
| `cache-status-default` | `r4/cache/missing-status` | `False` → `True` | killed (1 killer) |
| `counter-stderr-strip` | `r5/…/newline-stderr` | `False` → `True` | killed (1 killer) |
| `cache-stderr-strip` | `r5/cache/newline-stderr` | `False` → `True` | killed (1 killer) |

Mapping to CritAdequacy245: N1→`numeric-leaves-recursive-base`; N2→`cache-phases-sorted`+`cache-phases-set`; N3→`json-exact-keys-subset`; N4→`counter-except-no-valueerror`+`cache-except-no-valueerror`; R1→`summary-group-guard-drop`; R2→`cache-caserows-isinstance-drop`; R3→`cache-gate-sha-default`+`cache-cleaned-default`+`cache-residue-default`; R4→`cache-status-default`; R5→`counter-stderr-strip`+`cache-stderr-strip`. All nine findings are resolved, and each of the 14 mutants is attributed to the finding it belongs to.

## The specific check: is `numeric-leaves-recursive-base` truly killed by the deep-DICT vector?

Yes, and it is not equivalent.

- **Causal chain confirmed.** The mutant restores the base's recursive body. On
  the deep 1200-level dict, `json.loads` itself succeeds (the C decoder handled
  depth 1200 here), and the `RecursionError` arises inside the mutant's
  recursive `numeric_leaves` — the traceback shows repeated frames at
  `numeric_leaves` (line 367 of the mutant source), not at the decoder. The
  iterative current implementation returns `False` cleanly.
- **Minimal raising depth measured: 998** (with `sys.getrecursionlimit()` 1000),
  against a witness depth of 1200. So the witness sits ~20% above the threshold
  in recursion-depth terms, not at the boundary.
- **Shallow-input equivalence claim is falsified.** RevMutants245's inference
  from shallow inputs does not hold: on the 245 oracle the mutant survived
  with zero killers (`mutation-adequacy-listed59-oracle245.json` records
  `expect=killed, observed=survived, killing_vectors=[]`), and on 258 it is
  killed. The lesson text already records this correction.
- **CritAdequacy245's own distinguishing input is the one implemented.** Its
  N1 proposal was `'{"a":'*1200+'0'+'}'*1200` on `r13-counter-31984f4` with
  `want=false`; the fixture uses that exact literal.

## The other CritAdequacy245 extras (equivalences) re-checked on 258

CritAdequacy245 also named seven equivalence families (E1–E7) with reasons. I
rebuilt each of those mutants independently and graded them against the 258
oracle. All seven families still survive, so none of the recorded equivalences
is silently falsified by the new vectors:

| family | rebuilt mutant | 258 result |
|---|---|---|
| E1 | `je-list-branch-false`, `je-list-recurse-drop`, `je-zip-empty` | all survive |
| E2 | `sum-except-broad` | survives |
| E3 | `ctr-except-no-typeerror` | survives |
| E4 | `ctr-fields-guard-drop` | survives |
| E5 | `numeric-leaves-no-reversed` | survives |
| E6 | `cache-names-subset` | survives |
| E7 | `cache-producer-literal` | survives |

The 31 further non-equivalent extras from CritAdequacy245's own table were also
rebuilt; every one is killed on 258 (several now by the new residual2 vectors —
`cache-phases-list-guard-drop` and `cache-payload-isinstance-drop` by
`n4/cache/empty-stdout` and `r2/cache/cases-null`, `const-phase-swap` by
`n2/cache/phases-swapped`, `cache-demomatch-drop`/`ctr-jsonmatch-drop` by many,
and the three `cache-*-default` family by `r3`/`r4`). No unexplained survivor
remains in CritAdequacy245's enumeration.

## Receipt reproduction and prefix stability

- `python3 -B census/round-22/mutation-adequacy.py` exits 0 and its stdout is
  **byte-identical** to `census/round-22/mutation-adequacy-oracle258.json`
  (`cmp` clean): `mutants 59, killed 52, survived 7,
  disagreeing_with_expect []`, `oracle_total 258`, `pristine 258/258`.
- The 7 survivors are the expected equivalents: `nonexact-keyin-get`,
  `failed-checks-to-eq`, `names-len-constant`, `phases-len-constant`,
  `baseline-guard-pass`, `checks-len-drop`, `caserows-len-drop`.
- `python3 -B census/round-22/mutation-adequacy.py --grade-stdin < census/round-21/run-acceptance.py`
  gives 258/258 pass, 0 fail. Its `results` array is identical to
  `census/round-22/oracle258-changed.json`; that file additionally carries the
  five probe-side environment fields (`python`, `stack_soft_limit`,
  `depth_100000_decode_raises`, `probe_sha256`, `runner_source`), which the
  plain oracle run does not emit — a field-set difference only, no decision
  difference.
- `git show 41553adb:census/round-21/run-acceptance.py | … --grade-stdin` gives
  99 pass / 159 fail with 8 exceptions, matching
  `census/round-22/oracle258-baseline.json` on every id, every `observed`
  value, and every `pass` flag. Positive controls pass 20/20 on both runners.
- **Frozen prefix intact.** Splicing the 258 file back to 225 cases reproduces
  the 245-oracle bytes exactly: sha256
  `63de539f2e6113b525c068e9f54872203088d3fadf1ead605c31ccdf75151795`, which is
  the `oracle_sha256` recorded in `mutation-adequacy-oracle245.json`. The 225
  case objects are also byte-identical to those in the committed 225 file
  (`095af0e`), and `contract`, `revision`, `source_receipt_sha256` and
  `frozen_inventory_sha256` are unchanged across 225→258. The 13 new cases are
  a strict append; no earlier case was edited.

## Residual risk and verification gaps

1. **N1's witness depends on `sys.getrecursionlimit()`, and that limit is not
   in the receipt.** The deep-dict witness kills the recursive mutant only
   because the mutant's recursion exceeds the interpreter's recursion limit.
   Measured: the mutant still raises at limits 1000–1200 but survives at 1250 and
   above, so the vector stops killing at a limit ≳1250. Running the probe with
   `sys.setrecursionlimit(3000)` yields
   `disagreeing_with_expect: ['numeric-leaves-recursive-base']` — i.e. the
   adequacy claim fails loudly rather than silently, which is the right failure
   direction, but the probe receipt records `stack_soft_limit` and
   `depth_100000_decode_raises` and **not** `sys.getrecursionlimit()`. The
   lesson's prose (round-22.md, "Final measured witness set") does state
   `recursionlimit1000`, so the dependency is disclosed in prose but not
   machine-readable in the receipt. Not a defect in the vector; a
   receipt-completeness gap for the next revision.
2. **Stack size is not the deciding axis for N1, but the receipt implies it
   might be.** Sweeping `ulimit -s` over 1024/2048/4096/8192/16384/65536 KiB:
   the decode of a 1200-deep dict succeeds and the recursive mutant still
   raises at every one of these stack sizes, and `numeric-leaves-recursive-base`
   stays killed by `n1` in all six runs. So N1 is bound to the *recursion
   limit*, not the C stack — the opposite of the depth-100000 vectors, which
   are stack-bound. The two witness families must not be described as sharing a
   threshold; the current lesson text keeps them separate, and this review
   confirms the separation empirically.
3. **The base receipt is not byte-reproducible.** Re-running the base grading
   reproduces all 258 decisions but not the two `decoder-depth-100000` exception
   *strings*: fresh run says `Stack overflow (used 8144 kB)`, the recorded
   receipt says `used 8156 kB`. Same exception type, same `observed: null`,
   same `pass: false`; only the embedded stack-usage number differs, and it is
   a per-process measurement. The receipt is decision-reproducible, not
   byte-reproducible. Anyone comparing receipts with `cmp` must compare the
   decision fields, not the bytes.
4. **Environment observations that were not re-run here** (out of scope by the
   assignment, recorded for honesty): the real 18-step acceptance replay, the
   producer scripts, and any harness beyond the oracle were never executed. The
   review is confined to the oracle fixture and the in-memory probe, as
   instructed.
5. **Two of the 13 vectors are retained-behaviour pins rather than
   contract-derived.** `r3/*` and `r4/cache/missing-status` encode the runner's
   own key-presence behaviour (`gate.get("sha256")`, `isolation.get("cleaned")`,
   `isolation.get("residue") == []`, `payload.get("status")`) rather than a
   clause of the frozen oracle `contract` string, which is inside the immutable
   prefix and mentions only "replaced cache check identities and case
   stable-field/shape mismatches". These are conservative rejections (the
   runner rejects a missing field), they are correct, and the lesson already
   labels runner-only wants as retained-behaviour pins. The same applies to
   `r1` (summary-group guard) and `r5` (stderr without stripping). Recorded as
   provenance, not as a wrong decision.
6. **The `r5` newline-stderr vectors pin `not stderr`, not
   `not stderr.strip()`**, for the counter and cache kinds. The frozen
   `contract` string speaks of "nonempty summary stderr" and its literal scope
   in Q51 is the summary kind; the counter/cache stderr rule is retained runner
   behaviour. The vector is correct against the runner and is a conservative
   rejection, but its authority is the runner, not the contract string. Same
   provenance note as item 5.

## Verdict on the acceptance criteria

- Independently reconstruct each delta from pinned `final-out-S1.json` +
  `step-inventory.json`: **done for all 13; every reconstruction matched.**
- Decide `want=false`: **confirmed for all 13**; each current-source decision is
  exactly `False`, no exceptions, and each is a genuine negative (a wrong
  value, a wrong shape, a missing key, a wrong phase order, or nonempty stderr
  where the contract requires empty).
- Confirm the fixture feeds it: **confirmed for all 13** by reconstructing the
  effective input and by observing the intended mutant flip.
- Run each/current and base source via probe `--grade-stdin` in memory:
  **done**; current 258/258, base 99/258 with 8 exceptions; both match the
  recorded receipts on decisions.
- `numeric-leaves-recursive-base` truly killed by the deep-DICT vector, not
  equivalent: **confirmed** — it raises inside `numeric_leaves` (not at the
  decoder), minimal raising depth 998 vs witness depth 1200, and the mutant
  survived all 245 shallower vectors.
- Two base discriminators (deep dict → base exception; phase order → base
  `True`), other 11 base `False`: **confirmed exactly.**
- Wrong `want`/`want`/feed or missing finding resolution: **none found.** All of
  N1–N4 and R1–R5 are resolved with a killed, non-equivalent mutant per
  finding, and all seven CritAdequacy245 equivalence families still hold on the
  258 oracle.

## Commands run (all read-only; no file writes outside this report)

- `sha256sum` on the oracle, the probe, the runner, the pinned receipt, the pinned inventory
- `git show 473e98a:…`, `git show 095af0e:…`, `git show 41553adb:…` (read-only)
- `python3 -B census/round-22/mutation-adequacy.py` (stdout compared with `cmp` to the receipt)
- `python3 -B census/round-22/mutation-adequacy.py --grade-stdin < census/round-21/run-acceptance.py`
- `git show 41553adb:census/round-21/run-acceptance.py | python3 -B census/round-22/mutation-adequacy.py --grade-stdin`
- `python3 -B -` heredoc scripts that (a) import the oracle module and monkeypatch `load_runner` to grade an in-memory source per case, (b) rebuild the 14 residual2 mutants and ~40 CritAdequacy245 extras from literal anchors and grade them, (c) reconstruct every delta from the pinned receipt and compare with the fixture effective input, (d) measure decoder depth limits and the recursive-walk raising depth, and (e) sweep `ulimit -s` and `sys.setrecursionlimit()`.
- `ulimit -s` sweep at 1024/2048/4096/8192/16384/65536 KiB running the probe.
