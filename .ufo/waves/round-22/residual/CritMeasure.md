STATUS: PARTIAL

Seat: SoujiR22R.CritMeasure-17 (residual non-author critic, C1 before→after measurement). Lane HEAD 81a2646d53f914a226b6faa96e69ee5d01e8d348; `git diff --stat HEAD` over runner, oracle, oracle .py, probe and census/round-22/ is empty. Python 3.14.8, host soft stack `ulimit -s` = 8192 KiB.

Verdict: every number L1 claims reproduces on this host's default stack. The 214-oracle before→after (60/214 → 214/214) does not depend on the environment. The 225-oracle base count (69/225) and the probe's "21/21 non-equivalent killed, exit 0" hold only while the soft stack is at most 14 MiB. At 16 MiB or more, base scores 71/225 and the probe exits 1 with two expected kills surviving. No receipt records the stack size or the command used. One statement saying the receipts reproduce "exactly" is false for oracle225-baseline.

## Observed (I ran these)

### Reproduced counts
| Oracle bytes | Runner | Pass | Positives | Exceptions | Matches receipt |
|---|---|---|---|---|---|
| 214 (b912328, sha256 292442a6…0651), graded in memory | base 41553adb (sha256 1141839…aa2b) | 60/214 | 20/20 | 5 | yes, results digest a10e36e0… equals oracle214-baseline.json |
| 214, graded in memory | current (00d0e9c2…80a6) | 214/214 | 20/20 | 0 | yes, digest 01305109… equals oracle214-changed.json |
| 225 (current, 849a8569…a5cc) | base via `--grade-stdin` | 69/225 | 20/20 | 7 | counts yes; results bytes only sometimes (D2 below) |
| 225 | current, oracle .py file run | 225/225 | 20/20 | 0 | yes, digest c1b0df6d… equals oracle225-changed.json |

- How I graded the 214 oracle: `git show b912328…:tests/fixtures/r22-result-oracle.json` (with the base runner joined by a NUL separator when needed) was piped into `python3 -B -c`. That one-liner loads the unchanged `tests/fixtures/r22-result-oracle.py`, swaps `ORACLE` for an in-memory object that returns those bytes, and swaps `load_runner` for an exec of the runner source. It writes no file.
- The 5 base exceptions on the 214 oracle are: `cache/shape/{gate,isolation}/{null,array}` (AttributeError) and `summary/r20-input-binding/oversized-count` (ValueError from the int-digit limit). The 225 oracle adds 2 more: `adequacy/{r13-counter-31984f4,cache-demo}/decoder-depth-100000` (RecursionError: Stack overflow).
- Per-group results for base on the 225 oracle: scalar 0/62, stderr 0/49, cache-names 0/33, cache-cases 0/5, malformed 9/14, adequacy 9/11. Exit (18/18), summary-control (12/12), positive (20/20) and cache-value (1/1) all pass.

### The 214 prefix is identical
- Pipe-to-`python3 -c` comparison: the old file has 214 cases and the new one has 225. `cases[0:214]` are structurally equal and equal as canonical (sort_keys) JSON. The two files share their first 184527 bytes; after that the old file has `\n  ]\n}\n` and the new one has `,\n    {…adequacy…`. So the cases were appended only.
- Top-level keys (contract, revision ff425ab8…, source_receipt, frozen_inventory, both sha256 values, schema) are identical. All 225 ids are unique.
- History: `git log` for the oracle JSON shows 36c78ba (created), 4f83fd2 (+14 lines, 0 deletions, adding the two depth-1200 vectors) and 095af0e (+11 adequacy vectors). No `want` value was ever edited after creation. `git diff 4f83fd2 HEAD -- tests/fixtures/r22-result-oracle.py` is empty, so the 214 and 225 receipts used the same oracle code.

### Per-id agreement between the 214 and 225 receipts
- For both `baseline` and `changed`, the 214 receipt's id list equals the first 214 ids of the matching 225 receipt, in the same order. The full per-id records (expected, observed, exception, pass) differ in 0 of 214 cases on each side.

### Hash bindings inside the receipts
- In all four oracle receipts, `runner_sha256` matches the bytes it names (current file 00d0e9c2…; `git show 41553adb…` 1141839…). `oracle_sha256` matches `git show b912328…` (292442a6…) or the current file (849a8569…). `source_receipt_sha256` bc53a752… equals `sha256sum census/round-21/final-out-S1.json`.
- The oracle's `frozen_inventory_sha256` 8b7b1cd8… equals `step-inventory.json`. The oracle .py checks both input hashes before grading (lines 31–36).
- Rerunning `mutation-adequacy.py` now gives JSON identical to `mutation-adequacy-oracle225.json`. Its per-mutant `mutant_sha256` list is identical in the 214 and 225 probe receipts. Pristine runs are 214/214 and 225/225.

## Discrepancies

D1 (calibration, the main counterexample): the 225 base count and the adequacy probe depend on stack size. Sweep in a subshell (`ulimit -s N`), every runner/oracle pair:

| soft stack KiB | base/214 | changed/214 | base/225 | changed/225 | probe disagreeing_with_expect |
|---|---|---|---|---|---|
| 512 to 8192 | 60 | 214 | 69 | 225 | [] |
| 10240, 12288, 14336 | (not swept) | (not swept) | (not swept) | (not swept) | [] |
| 16384, unlimited | 60 | 214 | **71** | 225 | **['counter-recursion', 'cache-recursion']** (19 killed, 6 survived) |

- With a stack of 16 MiB or more, the C JSON decoder handles a 100000-deep array without raising. The base runner then returns `matched=False` for both `adequacy/*/decoder-depth-100000` vectors (they pass), and deleting either RecursionError catch survives all 225 vectors.
- So the lesson's "Base passes 69/225 … both depth-100000 vectors crash the base" and "All 21 non-equivalent mutants are killed … exit 0" (corpus/lessons/round-22.md:82, :20) hold only when the stack is at most about 14 MiB. The flip happens somewhere between 14336 and 16384 KiB.
- R22-M7 (round-22.md:21) does say "Interpreter- and stack-dependent observation", but no number states the condition. The receipts do not record `ulimit -s`, and the probe receipt records only `python`.
- corpus/SOURCES.md:127 (S107) says "100000 raises" with no stack qualifier.

D2 (provenance wording): round-22.md:83 and R22-M8 (:22) say stdin grading "reproduces the file-graded … receipts exactly". That is false for oracle225-baseline.
- The RecursionError text includes the measured stack use. Three back-to-back base runs gave "used 8144 kB" once and "used 8140 kB" twice.
- Only the 8144 run matched the receipt's results byte for byte (digest 3d8bf6ab…). The 8140 runs gave 8fa4c846…. Pass/fail decisions were identical every time.
- The 214 receipts reproduce exactly because no RecursionError occurs there.

D3 (provenance): the receipts do not say which command produced them.
- `--grade-stdin` always adds `runner_source: "stdin, graded in memory"` (mutation-adequacy.py:138). Neither baseline receipt has that field.
- oracle .py computes `runner_sha256` from `args.runner.read_bytes()` (r22-result-oracle.py:104).
- [INFERENCE] So oracle214-baseline.json and oracle225-baseline.json were produced by running the oracle .py against base runner bytes stored in some file path, not by the stdin route the lesson documents. Neither the path nor the command is recorded. This does not change any number.

D4 (scope note, already disclosed by L1 at round-22.md:59): the cache-demo positive hashes the live `tools/souji-evidence-cache.py` (run-acceptance.py:503, :522), and no receipt binds that hash. It is currently clean: `git diff --stat HEAD -- tools/souji-evidence-cache.py` is empty (exit 0), last touched in 48f8945. This is a reproducibility dependency, not a defect in the measurement.

## Attack: did the 214→225 additions change what C1's before→after means?
- Not for the defect classes C1 names. Base passes 9 of the 11 additions: `exact-json/extra-key`, `cache/failed-checks-nonempty`, `counter-stderr/warning`, `cache-stderr/warning`, `cache/gate-sha-mismatch`, `cache/isolation-cleaned-{false,int}`, `cache/isolation-residue-nonempty` and `summary/…/earlier-summary`. Those 9 add mutation adequacy only. They make the denominator larger but do not move the base→changed delta.
- The only base-discriminating additions are the two depth-100000 vectors. Base does not wrongly accept there; it raises. C1's "decoder RecursionError becomes a mismatch" part therefore has no witness at all on the 214 oracle (both depth-1200 rows pass on base, as R22-M7 says). On the 225 oracle it is witnessed only below about 16 MiB of stack (D1).
- Deltas: 214 oracle +154; 225 oracle +156 at the default stack and +154 at a stack of 16 MiB or more.
- [INFERENCE] The before→after for C1 should be headlined on the 214 oracle. The 225 result should be read as adequacy evidence that depends on the environment.

## Attack: are any expected decisions derived from the implementation under test?
- The oracle was created in the same commit as the runner fix (36c78ba, same author, together with the oracle .py). There is no independent oracle author. No `want` was ever edited later (append-only history, see above).
- Want distribution: all 205 non-positive vectors have want=false. The 20 positives have want=true and use pinned real outputs (18 steps, plus `subset-extra-fields` and one `cache-tra…` json_set control). Base also passes all 20, so the positives do not encode the change.
- [INFERENCE] The 9 base-passing adequacy wants were chosen by mutation guidance, so they agree with the pristine implementation on clauses that existed before the change. Two of them encode policy the contract string does not state: `summary/…/earlier-summary` requires exactly one SUMMARY line, and `cache/isolation-cleaned-int` requires `cleaned is True` rather than any truthy value. Both runners already enforce these, so the C1 delta is unaffected. They do, however, codify current behavior as specification.
- None of the 154/156 discriminating wants depends on the changed implementation's output. Each one is a literal rejection of a mutated input under the contract text (wrong scalar type, nonempty stderr, replaced cache check names or case phases, malformed shapes). I found no counterexample of a want that was flipped to match the changed runner.

## Impacted axes
calibration (D1, D2), provenance (D2, D3), scope reproducibility (D4, already disclosed).

## Smallest safe correction
1. State the condition wherever the 225 numbers appear (round-22.md:20/:82, S107): "69/225 and 21/21 killed hold at a soft stack of at most 14 MiB (observed on 3.14.8, 8 MiB host default); at 16 MiB or more base gives 71/225 and counter-recursion/cache-recursion survive". Record `ulimit -s` next to `python` in the probe and oracle receipts.
2. Change "reproduces … exactly" (round-22.md:22, :83) to "reproduces decisions; the RecursionError message's stack-usage text can vary". Alternatively, store only the exception type for RecursionError in the receipts.
3. Record the command (and runner path or stdin route) that produced each baseline receipt.

No fix to the runner or oracle decisions is needed.

## Hard-bound compliance and tooling
- I ran only the allowed oracle/probe commands, read-only git commands (show, diff, log, rev-parse), sha256sum, and `python3 -B -c` read/print one-liners fed by pipes, some in subshells with `ulimit -s` changed.
- I did not read /proc, any process table or operator-sweep content, and did not bare-list the lane, census or fleet roots. The only file written is this report. Nothing was installed or updated.
