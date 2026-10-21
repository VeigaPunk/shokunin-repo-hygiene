STATUS: PASS

# RevVectors245 — independent review of the 20 appended `adequacy/residual/` oracle vectors

Seat: `SoujiR22-2.RevVectors245` (reviewer, non-author).
Target: the 20 cases whose `id` starts with `adequacy/residual/` in
`/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r22-result-oracle.json`
(working-tree change by `SoujiR22-2`, uncommitted; compare with
`git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff HEAD -- <path>`).
Runner under test: `census/round-21/run-acceptance.py` (current working tree).
Base runner: `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py`.
Pinned inputs: `census/round-21/final-out-S1.json` (source receipt),
`census/round-21/step-inventory.json` (frozen inventory).

No tool was installed or updated by this seat (nothing was needed).
Read-only: the only file written by this seat is this report.

---

## 1. Method (reconstruction before predicate reading)

For every vector I reconstructed the fed input from the pinned record and the frozen
inventory step **before** reading `summarize_result`, then independently decided
whether literal `want=false` is right under the result contract, then executed.

1. Pinned record = `final-out-S1.json` → `commands[]` entry with the vector's
   `step_name` (stdout/stderr/returncode). All 18 records are genuine positives:
   `all_matched=true`, 18/18 matched, `returncode=0`, `stderr` empty, and every
   `stdout_sha256` re-verifies against its own bytes (observed).
2. Frozen step = `step-inventory.json` → `steps[]` entry, `<REVISION>`/`<REV>`
   substituted with the oracle `revision` = `ff425ab835614f38205426330b9cdb93fd267045`.
   The receipt's own `expected_summary` equals the inventory's for 17/18 commands;
   the one difference is `clean-cache-demonstration`, where the inventory holds the
   literal `"<REV>"` placeholder and the receipt holds the resolved
   `ff425ab8…` — benign, and the fixture overwrites it with the oracle revision
   anyway (`tests/fixtures/r22-result-oracle.py:84-85`).
3. Delta = the vector's `json_set` (applied to the decoded pinned stdout) or its
   literal `stdout` override.
4. Independent contract decision: I re-derived the relevant conjunct of
   `summarize_result` from the runner source before looking at any observed value.
5. Execution: `python3 -B tests/fixtures/r22-result-oracle.py --runner
   census/round-21/run-acceptance.py --case <id>` for each of the 20, plus the
   full 245-case run, plus the base runner graded in memory via
   `git show 41553adb…:census/round-21/run-acceptance.py | python3 -B
   census/round-22/mutation-adequacy.py --grade-stdin`.
6. **Proof that the fixture feeds exactly the reconstructed input**: I imported
   `tests/fixtures/r22-result-oracle.py` in memory, patched its `load_runner` to
   return a spy-wrapped current runner, and captured the exact
   `(step, returncode, stdout_bytes, stderr_bytes, revision, root)` tuple the
   fixture passes to `summarize_result` for each of the 20 cases. All 20 matched
   my independent reconstruction byte-for-byte (step object equal, stdout bytes
   equal, stderr bytes equal, returncode equal, revision equal, root equal).
   **0 feed mismatches.**
7. **Single-cause attribution**: an independent replica of every conjunct of the
   current runner's `summarize_result` (summary / counter / cache-demo branches)
   was evaluated per vector; the table below names the *only* conjunct that flips.

---

## 2. Append integrity versus HEAD (observed)

| Claim | Verdict | Evidence |
|---|---|---|
| first 187903 bytes identical | **TRUE** | `cur[:187903] == head[:187903]` → `True`; first differing byte index = 187903 |
| zero deleted lines | **TRUE** | `git diff HEAD --numstat` → `253  0  tests/fixtures/r22-result-oracle.json`; `grep -c '^-[^-]'` on the diff → `0` |
| ids unique | **TRUE** | 245 cases, 245 distinct ids, 0 duplicates (all ids, not just the new 20) |
| only the 20 residual ids were added | **TRUE** | HEAD has 225 cases, worktree has 245; ids of the first 225 are identical; the last 20 are exactly the `adequacy/residual/` ones; every other top-level oracle key is unchanged |

**One precision note (not an error).** The change is *prefix-append + insertion*,
not an append at EOF: the previous last vector's closing `    }` line becomes
`    },`, the 20 new objects are inserted, and the file's final `  ]\n}\n`
(7 bytes) is re-emitted. HEAD length 187910 → worktree 228138 (+40228). The
preceding 187903 bytes are byte-identical, nothing was deleted or reordered, and
the JSON parses — so "byte-append-only" holds in the prefix/no-deletion sense
that the 187903-byte figure asserts, but the bytes were not added at end-of-file.

**Reconstruction of the delta shape (observed).**
* 13 vectors use `json_set`; 7 use a literal `stdout` override.
* Structural leaf diff of the decoded JSON vs the pinned record:
  exactly **one** leaf changes for 11 of 13 `json_set` vectors;
  `gate-both-slots-wrong` changes **two** leaves (`gate.sha256`,
  `gate.sha256_after`); `malformed/cache/case-rows-int` replaces the whole
  `cases` array; `isolation-residue-null` replaces `isolation.residue`
  (`[]` → `null`). No vector adds or drops a sibling field.
* All 7 `stdout`-override vectors differ from the pinned record by **exactly one
  added or removed line** (line-level `difflib` diff): `FAIL\tsynthetic`,
  `INVENTORY\tsynthetic`, `BASELINE_MISMATCH\tsynthetic`,
  `VIOLATION\tsynthetic`, one deleted `PASS\tgrant-clone-negated-prose`, and
  `null\n` replacing the whole JSON document for the malformed case.
* The `json_set` vectors feed `json.dumps(payload)`, so the *bytes* fed differ
  from the pinned record's bytes (cache payload 43435 → 37214 bytes) even though
  the decoded content differs by the one leaf above. This is the fixture's
  re-serialization, not a second delta.

---

## 3. Per-vector verdict table

`want` is literal `false` for all 20 (observed in the fixture).
"cur" = current runner observed `matched`; "base" = base runner `41553adb…` observed `matched`.
"single-cause" = exactly one conjunct of the relevant `summarize_result` branch flips.

| # | id | want correct? | fed input (delta from pinned record) | cur | base | single-cause? | only failing conjunct (observed) |
|---|---|---|---|---|---|---|---|
| 1 | `adequacy/residual/value/r13-counter-31984f4/F2_entry` | YES | `F2_entry` 0→1 | False | False | YES | `json_exact(F2_entry: 1 != 0)` |
| 2 | `adequacy/residual/value/r13-counter-6f8ee0f/sources` | YES | `sources` 37→38 | False | False | YES | `json_exact(sources: 38 != 37)` |
| 3 | `adequacy/residual/value/r14-counter-a31642d/tiers-A` | YES | `tiers.A` 33→34 | False | False | YES | `json_exact(tiers.A: 34 != 33)` |
| 4 | `adequacy/residual/value/r14-counter-552cae4/measured_commit` | YES | `measured_commit` → 40×`0` | False | False | YES | `json_exact(measured_commit: 000… != 552cae42…)` |
| 5 | `adequacy/residual/value/r13-counter-b576341/admitted_entries` | YES | `admitted_entries` 6→7 | False | False | YES | `json_subset(admitted_entries: 7 != 6)` (this step has `exact_json=false`, so the subset branch is the right one) |
| 6 | `adequacy/residual/value/cache/producer_executions_new_policy` | YES | `producer_executions_new_policy` 3→4 | False | False | YES | `demo:producer_executions_new_policy` (`json_exact` vs expected 3) |
| 7 | `adequacy/residual/malformed/cache/case-rows-int` | YES | `cases` = 4 dicts → `[1,2,3,4]` | False | **True** | YES | `demo:case_phases` (`[None,None,None,None] != CACHE_CASE_PHASES`) |
| 8 | `adequacy/residual/malformed/r13-counter-b576341/null` | YES | stdout → `null\n` | False | False | YES | `json_subset(observed_not_dict: None)` (`isinstance(observed, dict)` fails) |
| 9 | `adequacy/residual/cache/gate-both-slots-wrong` | YES (see F1) | `gate.sha256` and `gate.sha256_after` → 64×`0` | False | False | YES | `demo:gate.sha256==gate_sha` — **only this one conjunct reads either slot** |
| 10 | `adequacy/residual/cache/status-failed` | YES | `status` `ok`→`failed` | False | False | YES | `demo:status` |
| 11 | `adequacy/residual/cache/measured-commit-wrong` | YES | `measured_commit` → 40×`0` | False | False | YES | `demo:measured_commit==revision` |
| 12 | `adequacy/residual/cache/harness-revision-wrong` | YES | `harness_revision` → 40×`0` | False | False | YES | `demo:harness_revision==revision` |
| 13 | `adequacy/residual/cache/inputs-unchanged-false` | YES | `inputs_unchanged_during_run` `True`→`False` | False | False | YES | `demo:inputs_unchanged_identity` (`is True` identity check) |
| 14 | `adequacy/residual/cache/inputs-unchanged-int` | YES | `inputs_unchanged_during_run` `True`→`1` | False | False | YES | `demo:inputs_unchanged_identity` (`1 is True` is false) |
| 15 | `adequacy/residual/cache/isolation-residue-null` | YES | `isolation.residue` `[]`→`null` | False | False | YES | `demo:isolation.residue==[]` |
| 16 | `adequacy/residual/summary/auditor-selftest/fail-line` | YES | one line appended: `FAIL\tsynthetic` | False | False | YES | `base:returncode0_and_no_failure_lines` (`failure_lines` non-empty) |
| 17 | `adequacy/residual/summary/r20-input-binding/extra-inventory` | YES | one line appended: `INVENTORY\tsynthetic` | False | False | YES | `summary_match[auxiliary_lines]` (`observed_auxiliary` 2 lines vs expected 1) |
| 18 | `adequacy/residual/summary/r20-input-binding/extra-baseline-mismatch` | YES | one line appended: `BASELINE_MISMATCH\tsynthetic` | False | False | YES | `summary_match[baseline_mismatch_count(reported=8, lines=9)]` |
| 19 | `adequacy/residual/summary/carry-invariant-probe/violation-line` | YES | one line appended: `VIOLATION\tsynthetic` | False | False | YES | `carry_invariant_probe_violation_line` (the `step["name"]=="carry-invariant-probe"` clause) |
| 20 | `adequacy/residual/summary/auditor-selftest/missing-pass-line` | YES | one line removed: `PASS\tgrant-clone-negated-prose` (118→117 PASS lines) | False | False | YES | `pass_match(117 != 118)` |

### Independent contract judgement (why every `want=false` is right)

Each delta corrupts exactly one producer-output fact that the pinned
`expected_summary` (or the reviewed identity constants `CACHE_CHECK_NAMES`,
`CACHE_CASE_PHASES`) asserts: a counter leaf, a cache-demo identity field, a
boolean that must be exactly `True`, an empty residue list, a gate digest, a
`PASS`/`FAIL` line, an auxiliary `INVENTORY` line, a baseline-mismatch count, or a
`VIOLATION` line. The contract's stated purpose ("reject … decoded wrong scalar
types, replaced cache check identities and case stable-field/shape mismatches")
covers every one of them, and a *corrupted* producer output must not be reported
as matched. So `want=false` is correct for all 20 vectors independently of the
implementation that produced it. The pinned, unmutated counterpart of every one
of the 20 is a positive under the current runner (observed `matched=True` for all
20), so the delta is the sole cause of the rejection in every case.

### Execution evidence

* Current runner, full oracle: `total 245, pass 245, fail 0, finding_id None`,
  `runner_sha256 00d0e9c2fda2fde2d21cb74b1a1dd5b1db7b1ea679cdfd4239d91aa186e080a6`,
  `oracle_sha256 63de539f2e6113b525c068e9f54872203088d3fadf1ead605c31ccdf75151795`
  — identical to `census/round-22/oracle245-changed.json` (observed).
* Per-case `--case` runs for all 20: each exits 0 with
  `expected=False, observed=False, exception=None, pass=True` (observed).
* Base runner `41553adb…` graded in memory: `total 245, pass 88, fail 157`,
  `finding_id R22-RESULT-CONTRACT` — identical to
  `census/round-22/oracle245-baseline.json` (observed). **19 of the 20 residual
  vectors are rejected by the base runner too**; only #7
  (`malformed/cache/case-rows-int`) is accepted by the base runner
  (`observed=True`), i.e. that vector is a genuine coverage hole closed by the
  current runner's `case_phases` check, and it is the one vector in this append
  that the base/current distinction is about.

---

## 4. Findings

### F1 — MEDIUM (naming/coverage over-claim, not a wrong verdict): `gate-both-slots-wrong` tests one slot, not two

`adequacy/residual/cache/gate-both-slots-wrong` sets **both**
`gate.sha256` and `gate.sha256_after` to 64×`0`. The result contract reads
**only** `gate["sha256"]` (`census/round-21/run-acceptance.py:522`); `gate["sha256_after"]`
and the top-level `gate_sha256_after` are read by no conjunct. Measured
(observed, in memory, current runner):

| payload delta | observed `matched` |
|---|---|
| `gate.sha256_after` only → zeros | **True** (accepted) |
| top-level `gate_sha256_after` only → zeros | **True** (accepted) |
| `gate.sha256` only → zeros | False (rejected) |
| both (the shipped vector) | False (rejected) |
| `gate.sha256_after` + `gate.installed_default.sha256` → zeros | **True** (accepted) |

Consequences: (a) the vector's rejection is single-cause at the predicate level
(only `gate.sha256==gate_sha` flips) — so the literal `want=false` is correct and
the "single-cause" column stands; but (b) the id asserts coverage of two slots
where only one is observable, and a reviewer reading the id would believe
`sha256_after` is validated. The vector is not useless: it is the **unique**
killer of the `gate-self-consistency` mutant (`gate.get("sha256") == gate_sha`
→ `gate.get("sha256") == gate.get("sha256_after")`), which a `gate.sha256`-only
delta would not kill, because with both slots equal the swapped comparison still
succeeds. [INFERENCE] The minimal honest fix is to rename the id (e.g.
`…/gate-sha256-wrong`) or to add a `gate.sha256_after` conjunct to the
contract; as shipped the vector's marginal value is real but narrower than its
name claims.

### F2 — LOW (redundancy): 6 of the 20 appended vectors add no discriminating power beyond their siblings

I re-derived the killing-vector sets for all 45 mutants (in memory, same
`mutate`/`grade` machinery as `census/round-22/mutation-adequacy.py`).
**15 of the 45 mutants are killed only by the newly appended vectors** — i.e. the
append does retire the previously-alive mutants. Cross-checked against the
pre-append receipt `census/round-22/mutation-adequacy-listed45-oracle225.json`
(observed): under the 225-vector oracle the probe reported
`killed 23, survived 22, disagreeing_with_expect` = exactly those 15 ids
(`json-exact-leaf-true`, `case-row-isinstance-drop`, `nonexact-isinstance-drop`,
`gate-self-consistency`, `status-drop`, `measured-commit-drop`,
`harness-revision-drop`, `inputs-unchanged-drop`, `inputs-unchanged-eq`,
`isolation-residue-falsy`, `failures-drop`, `aux-drop`, `bm-count-drop`,
`pass-match-drop`, `violation-drop`). With the 245-vector oracle the same probe
reports `killed 38, survived 7, disagreeing_with_expect []` — i.e. the append
retires **all 15** previously-disagreeing mutants, and the remaining 7 survivors
are exactly the 7 declared `equivalent`. But:

* the five `adequacy/residual/value/*` counter vectors each kill **only**
  `json-exact-leaf-true`, which all five (plus `value/cache/producer_executions_new_policy`)
  kill together; no pre-existing vector kills it. So five of the six
  `value/*` vectors are mutually redundant;
* `adequacy/residual/cache/inputs-unchanged-false` kills only
  `inputs-unchanged-drop`, which `inputs-unchanged-int` also kills (and
  `inputs-unchanged-int` additionally uniquely kills `inputs-unchanged-eq`).

Net: 14 of the 20 are unique killers of 15 previously-alive mutants; 6 are
redundant. Redundancy is not an error, but the headline "20 vectors" overstates
the coverage actually added (15 mutants). [INFERENCE] If the receipt is meant to
state coverage, the honest number is "15 previously-alive mutants retired by 14
independent vectors (20 appended, 6 redundant)".

### F3 — MEDIUM (residual risk, disclosed but not caused by this append): the oracle verdict is stack-size dependent

`census/round-22/stack-sweep-oracle245.txt` claims the verdict varies with the
C-stack soft limit. I reproduced every row (observed):

| stack | base pass | changed pass | probe killed | disagreeing |
|---|---|---|---|---|
| 8192 KiB (= this host's `RLIMIT_STACK` soft 8388608) | 88/245 | 245/245 | 38/45 | — |
| 14336 / 15360 KiB | 88/245 | 245/245 | 38/45 | — |
| 16384 KiB | 90/245 | 245/245 | 36/45 | `counter-recursion`, `cache-recursion` |
| unlimited | 90/245 | 245/245 | 36/45 | `counter-recursion`, `cache-recursion` |

The two flipping cases are the **pre-existing** vectors
`adequacy/r13-counter-31984f4/decoder-depth-100000` and
`adequacy/cache-demo/decoder-depth-100000`: the base runner lacks
`except (…, RecursionError)`, so at 8 MiB the deep decode raises
`RecursionError: Stack overflow (used 8140 kB)` → `observed=None` → vector fails;
at ≥16 MiB the decode succeeds → `observed=False` → vector passes. The newly
added `stack_soft_limit` field in the receipts (8388608 here) discloses the
dependency, and the sweep receipt is honest and reproducible. **None of the 20
appended vectors is stack-sensitive** (all 20 are `observed=False` at 8 MiB,
16 MiB and unlimited; changed runner = 245/245 at all three), so this append does
not add a new stack dependency. It does mean the recorded `88/245` base figure
and `38/45` kill count are valid **only** at the recorded 8 MiB soft limit.

### F4 — INFO: fixture re-serialization is faithful but changes the fed bytes

For `json_set` vectors the fixture decodes the pinned stdout and re-emits it with
`json.dumps` (`tests/fixtures/r22-result-oracle.py:73-82`), so the fed stdout is
not byte-equal to the pinned record's stdout (cache payload 43435 → 37214
bytes; counter payload 229 → 228 bytes). The decoded content differs from the
pinned record by exactly the one leaf/field listed in the table, and the
`stdout_sha256` therefore differs from the pinned record's. This is harmless for
`matched` (no conjunct reads the stdout digest) and is verified by the
feed-equality proof in §1, but it means "the fixture feeds exactly that input"
holds for the *decoded* payload, not for the pinned stdout bytes.

### F5 — INFO (positive): no vector is double-counted or masked

For all 20 vectors exactly one conjunct flips, and no vector relies on a
side-effect (exception, stderr, returncode) other than the one named in the
table. Vector #8 is the only one that reaches the "wrong scalar type" clause
(`observed` is `None`, not a dict) and it does so without raising.

---

## 5. Residual risk and verification gaps

1. **Coverage of the identity constants** (not in this append's scope, but
   adjacent): `CACHE_CHECK_NAMES` (33 names) and `CACHE_CASE_PHASES` (4 phases)
   are asserted against the pinned payload by exact identity, and the appended
   vectors exercise one phase-array mutation (#7). No appended vector mutates
   `checks` (e.g. removes a key or flips one `True` to `False`), so the
   `checks.keys() == CACHE_CHECK_NAMES` and `all(value is True …)` conjuncts are
   still exercised only by the pre-existing 225. [INFERENCE] A
   `checks`→`{"x": true}` or one-check-flipped vector would cover them; that is
   outside the 20 under review.
2. **Unobserved cache fields** (F1): `gate.sha256_after`,
   `gate.installed_default.sha256`, and top-level `gate_sha256_after` are
   accepted in any value by the contract. If the reviewed identity is supposed
   to include them, the contract (not the vectors) is what is missing.
3. **Stack dependence** (F3): any consumer of `oracle245-baseline.json` /
   `mutation-adequacy-oracle245.json` must honour the recorded
   `stack_soft_limit`; on a host with a different soft limit the base pass count
   is 88 or 90 and the kill count 38 or 36.
4. **Not verified by this seat** (other seats' scope): the correctness of the
   20 appended *mutants* and their `expect` labels in
   `census/round-22/mutation-adequacy.py`; the 7 surviving mutants
   (`nonexact-keyin-get`, `failed-checks-to-eq`, `names-len-constant`,
   `phases-len-constant`, `baseline-guard-pass`, `checks-len-drop`,
   `caserows-len-drop`) are all declared `equivalent` in the probe, so
   `disagreeing_with_expect` is empty and the probe exits 0 — I confirmed the
   probe's own summary (`killed 38, survived 7, disagreeing []`, `pristine
   245/245`) reproduces at this host's 8 MiB soft limit, but I did not
   independently re-derive those equivalence claims.
5. **I did not run** the real acceptance `main()`, the replay, or any producer;
   no git/jj state was mutated; no `/proc`, process table, credential, or
   `census/operator-sweep-20261019/` access; no scratch file was written
   anywhere (all mutant and alternate-input evaluation was in memory via
   `python3 -B` / in-process `exec(compile(...))`).

---

## 6. Reproducible commands (all read-only)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
git diff HEAD -- tests/fixtures/r22-result-oracle.json | grep -c '^-[^-]'      # 0
git diff HEAD --numstat -- tests/fixtures/r22-result-oracle.json                 # 253 0
python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py   # 245/245, exit 0
python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py --case <id>   # per vector, exit 0
git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py \
  | python3 -B census/round-22/mutation-adequacy.py --grade-stdin               # base: 88/245
( ulimit -s unlimited; git show 41553adb…:census/round-21/run-acceptance.py \
  | python3 -B census/round-22/mutation-adequacy.py --grade-stdin )             # base: 90/245
python3 -B census/round-22/mutation-adequacy.py                                 # killed 38/45, exit 0
( ulimit -s 16384; python3 -B census/round-22/mutation-adequacy.py )            # killed 36/45, 2 disagreeing
```

## 7. Bottom line

All 20 appended vectors are **correct** (`want=false` is right under the result
contract), each is fed by the fixture exactly the input it claims, each rejects
for exactly one identified reason, the append is a clean prefix-preserving
insertion with unique ids and zero deletions, and the append does retire 15
previously-alive mutants. Two honest-reporting defects: the
`gate-both-slots-wrong` id over-claims (only one of its two slots is observable
by the contract, F1), and 6 of the 20 vectors are redundant relative to their
siblings (F2). Neither changes a `want` value or a measured outcome.
