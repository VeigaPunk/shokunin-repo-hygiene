# S59ExecGate — r59 assessment gate and executable self-invocation

Axes: (1) classification and exact note-derivation fidelity; (2) self-test
discrimination of exit code, finding id and derived counts; (3) read-only
confinement and rc2 error mapping; (4) legacy preservation / no visibility work.

## Result

Implemented a new `assessment-gate.py` derived from `census/round-58/c1-counter.py`.
The two note derivations are preserved verbatim: positional matrix column 5 equals
`0` per matrix (`exit_zero=<v5>,<v6>`), and row-wise equality of `exit` plus
`findings_all` (`carry_identical`). The clean-path output is byte-identical to the
r58 counter at both `19f44552` and `da5af55b`; the only added normal-mode line is
one stable `FINDING ASSESSMENT-MISMATCH` when `mismatches>0`. Errors map to rc2
without a traceback.

The self-test executes the gate as an actual CLI subprocess over a unique isolated
Git fixture under `--work`: five cases are committed at fixed dates and scored
against the adjacent independent `assessment-selftest-expected.tsv`. Observed:

| Case | rc | FINDING | mismatches | carry_identical | exit_zero |
|---|---:|---|---:|---:|---|
| HONEST | 0 | — | 0 | 34 | 10,8 |
| OMIT-FIRST | 1 | ASSESSMENT-MISMATCH | 1 | 34 | 10,8 |
| OMIT-SECOND | 1 | ASSESSMENT-MISMATCH | 1 | 34 | 10,8 |
| BOTH-MISSING | 1 | ASSESSMENT-MISMATCH | 2 | 34 | 10,8 |
| WRONG-VALUE | 1 | ASSESSMENT-MISMATCH | 1 | 34 | 10,8 |

`SELFTEST-EXPECTED-SET cases=5 expected=5 extra=- missing=-`;
`SELFTEST control=FALSE-GREEN-REJECTED stub_meets=1 discriminated=4 cases=5`;
`SELFTEST pass cases=5`; EXIT=0. A second run produced an identical receipt. The
unique fixture child was absent after the first run (cleanup observed); the
second run uses the same `finally` path and also exited 0.

The expected values were independently derived with `awk` over the pinned base
matrices before the gate was written (`independent-derivation.txt`): v5 zero=10,
v6 zero=8, identical=34. They are frozen in the expected TSV, not recomputed by
the oracle.

Together these cover the prereg production trial at this seat's boundary: the
new gate over the committed lane snapshot returns rc0 with both derived notes,
and over the isolated negative fixture with one correction omitted returns rc1
with `ASSESSMENT-MISMATCH`. That supports the r58 comparator's assessment
behavior being gate behavior on the committed snapshot; it does not itself edit
or certify the registry row. The prereg's classification remains counting, not
execution authentication: a truthful kind edit is what the counter legitimately
passes.

## Deliverables (own delivery directory only)

| Path | SHA-256 | Role |
|---|---|---|
| `.ufo/waves/round-59/w1/S59ExecGate/assessment-gate.py` | `4dfdd13eb7061e52da709e7ee7bd51cada64322cf26939bbf4768ecf53913b66` | gate implementation + subprocess self-test |
| `.ufo/waves/round-59/w1/S59ExecGate/assessment-selftest-expected.tsv` | `2eb315f8352b55c6a3ba1c90fc3f4f58a33736c51547f118d199bdb5781635ef` | independent expected rc/finding/counts for 5 cases |
| `.ufo/waves/round-59/w1/S59ExecGate/precondition.txt` | `5b2d41dff008c61c2a2a3b8936b95c02bf9bb17c8bcd124c439f76be4e45dfea` | post-freeze candidate-scoring record |
| `.ufo/waves/round-59/w1/S59ExecGate/{selftest-receipt,selftest-receipt-2}.txt` | — | exact self-test stdout and EXIT |
| `.ufo/waves/round-59/w1/S59ExecGate/{normal-freeze,normal-base}-receipt.txt` | — | clean normal-mode output over committed snapshots |
| `.ufo/waves/round-59/w1/S59ExecGate/parity-receipt.txt` | — | r58-counter vs new-gate clean-output diff |
| `.ufo/waves/round-59/w1/S59ExecGate/error-{missing-rev,nonrepo}-receipt.txt` | — | rc2/no-traceback observations |
| `.ufo/waves/round-59/w1/S59ExecGate/{independent-derivation,digests}.txt` | — | oracle independence and digest pins |

No production file, registry row, `SKILL.md`, historical gate, fleet file or
sibling path was written. No commit, push or jj mutation was made. Scratch
`/fast/scratch/hyaku/souji-r59/S59ExecGate/` was removed after these receipts
were retained.

## Exact evidence

Freeze ordering (`precondition.txt`, recorded before any candidate run):
`lane_head_at_record=19f44552378d333f401ff2f0864c4e8b9c59ab1f`,
`recorded_utc=2026-11-04T18:41:11Z`; the freeze commit is HEAD and the executed
controls commit `74455b72` precedes it. Candidate scoring therefore occurred
after freeze; no candidate score ran before it.

Normal mode over committed snapshots (EXIT=0 both, no FINDING):

```text
$ python3 -B .ufo/waves/round-59/w1/S59ExecGate/assessment-gate.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 19f44552378d333f401ff2f0864c4e8b9c59ab1f
MATCH R58-CALIBRATION carry_identical=34 supersedes the r57 SCORECARD claim "all 33 carry-over rows".
MATCH R58-CALIBRATION exit_zero=10,8 counted separately per matrix; the r57 two-file awk command emits the combined total 18, not the pair.
SUMMARY assertions=2 mismatches=0 carry_identical=34 exit_zero=10,8

$ python3 -B ... --rev da5af55b5ea0a2a38edea05635a13416c698e6e7
(same two MATCH lines and SUMMARY; EXIT=0)
```

Clean-path parity (`parity-receipt.txt`): r58 counter and new gate stdout were
identical at both revisions (`base_rc=0 new_rc=0 freeze_stdout=identical`;
`base_rc=0 new_rc=0 base_stdout=identical`).

Self-test command and receipt (`selftest-receipt.txt`; second run identical):

```text
$ python3 -B .ufo/waves/round-59/w1/S59ExecGate/assessment-gate.py \
    --selftest --work /fast/scratch/hyaku/souji-r59/S59ExecGate/work-r59-a
SELFTEST-EXPECTED-SET cases=5 expected=5 extra=- missing=-
SELFTEST-CASE BOTH-MISSING pass rc=1 want_rc=1 findings=ASSESSMENT-MISMATCH want_findings=ASSESSMENT-MISMATCH mismatches=2 want_mismatches=2 detail=-
SELFTEST-CASE HONEST pass rc=0 want_rc=0 findings=- want_findings=- mismatches=0 want_mismatches=0 detail=-
SELFTEST-CASE OMIT-FIRST pass rc=1 want_rc=1 findings=ASSESSMENT-MISMATCH want_findings=ASSESSMENT-MISMATCH mismatches=1 want_mismatches=1 detail=-
SELFTEST-CASE OMIT-SECOND pass rc=1 want_rc=1 findings=ASSESSMENT-MISMATCH want_findings=ASSESSMENT-MISMATCH mismatches=1 want_mismatches=1 detail=-
SELFTEST-CASE WRONG-VALUE pass rc=1 want_rc=1 findings=ASSESSMENT-MISMATCH want_findings=ASSESSMENT-MISMATCH mismatches=1 want_mismatches=1 detail=-
SELFTEST control=FALSE-GREEN-REJECTED stub_meets=1 discriminated=4 cases=5
SELFTEST pass cases=5
EXIT=0
```

Error mapping (no `Traceback` in either receipt):

```text
$ ... --root LANE --rev 0000000000000000000000000000000000000000
CANNOT-EVALUATE git show 000...:census/round-57/records/c1-matrix-v5.tsv rc=128 fatal: ...
EXIT=2

$ ... --root /fast/scratch/hyaku/souji-r59/S59ExecGate --rev 19f44552...
CANNOT-EVALUATE git show 19f44552...:census/round-57/... rc=128 Stopping at filesystem boundary ...
EXIT=2
```

## Implementation notes

- Normal mode reads only committed Git blobs (`git show --rev:path`) with a
  scrubbed Git environment; the working tree is never consulted and nothing is
  written. `--root`/`--rev` and the existing MATCH/MISSING + SUMMARY grammar and
  0/1 verdict are preserved.
- `ASSESSMENT-MISMATCH` is emitted once for any `mismatches>0`. The
  BOTH-MISSING case therefore carries the same stable id as the single-omission
  cases while the expected TSV separately pins `mismatches=2`; this keeps the
  finding vocabulary stable instead of inventing a second id.
- Self-test fixture: one `tempfile.mkdtemp` child under `--work`; both matrices
  and the base `SCORECARD.md` are copied from pinned base
  `da5af55b5ea0a2a38edea05635a13416c698e6e7` with `git show`; five variants are
  committed with fixed author/committer dates and `git -C <fixture>`; the
  fixture toplevel is asserted after init and before each add/commit; only the
  created child is removed in `finally`.
- Each case invokes `sys.executable -B <this file> --root <fixture> --rev <full40>`
  as a subprocess and asserts rc, ordered finding ids, the parsed SUMMARY
  mismatch count, `carry_identical` and `exit_zero` against the expected TSV.
  An always-clean stub is scored over the same expected rows; it meets only
  HONEST, so the fixture set rejects it as FALSE-GREEN.
- Errors from Git, fixture construction, expected parsing or any unexpected
  normal-mode exception are caught at the CLI boundary and printed as
  `CANNOT-EVALUATE ...` with rc2; no traceback is emitted.

## Bounds, limits and risks

- Substring presence in `SCORECARD.md` remains the predicate. This is the r58
  semantics and the prereg's bounded classification; it is not Markdown
  visibility, parser repair, authenticity, or a claim that a prose look-alike
  cannot satisfy the note. No new parser/visibility capability is claimed.
- `--rev` still accepts any Git revision expression, as before; the self-test
  uses full40 revisions.
- The self-test re-fetches the pinned base and both matrix blobs from the lane
  Git object store. If those objects are unavailable it returns rc2 rather than
  silently substituting bytes; the expected TSV itself is host-independent and
  retained.
- The expected TSV is delivered adjacent to the gate but is not committed by
  this seat (commits are outside this seat's authority). Integration must copy
  both files to the tracked production path and commit the expected TSV with
  the gate; the default `DEFAULT_EXPECTED = HERE / 'assessment-selftest-expected.tsv'`
  follows the gate if both move together.
- `.ufo/waves/` is ignored by the lane `.gitignore`; these are wave receipts,
  not committed production artifacts.
- The expected TSV is read from disk as the oracle. Its integrity is the
  integration commit that places it beside the gate, not a digest embedded in
  the gate; no digest-pinned oracle is claimed in this bounded scope.
- Not run: builds, lint, formatters, registry edits, unrelated tests, or any
  mutation of the frozen counter (S59Mutation owns frozen-counter mutation
  testing). No claim about a production registry row or score mapping.
- No non-author closure authority is claimed. Admission/rejection and the
  registry-kind edit belong to L1/integration. This report is bounded executor
  evidence for the assigned implementation and its self-test.

## Legacy debts preserved (unchanged, still OPEN)

Parser visibility / second opener / code-span / escape / link / TAB; recorder
dirty-overwrite; receipt confinement atomicity / resource bounds; capture
row-set meta-test; historical receipt bindings and diagnostic escaping.
Certification remains OFF; prior rejected admissions are not repaired
retroactively. No visibility work was attempted.

Report: .ufo/waves/round-59/w1/S59ExecGate.md
