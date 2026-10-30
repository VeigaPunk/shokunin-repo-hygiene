# S44reviewer19 — C2 scenario 3/10

## Result and axes
Axes: calibration / operability / coverage. Assigned axis: operability. No actionable correctness defect found in h3. The frozen real checker passes this row, and the row kills a single malformed-heading-recognition defect without relying on a different exit status. This is evidence for this scenario only, not admission or an aggregate score increase.

## Frozen evidence and independent derivation
All executed sources were fetched using `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:<path>`. Exact source bytes and SHA-256 values are retained beside this report and in `receipts.json`. The C2 counter hash is `0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252`; population hash is `6a68a10161745c7974e93afe9724853f1a61fc192185c128c88840b1977a7054`, matching preregistration.

Selected row: `h3-two-unattached-keys` (`census/round-44/c2-hidden-audit.py:114-115`; `c2-scenarios.tsv:4`). Its tail is:

```text
##C2 bad
Population: census/pop.tsv sha256=<valid population digest>
Control: census/control.txt
```

Independent grammar derivation: the documented valid header requires `## C<digits>` followed by space/end (`tools/souji-freeze-check.py:11-13`). The r43 grammar amendment says malformed headings close the block and every subsequent key is unattached until another valid heading (`:21-23`). Therefore `##C2 bad` creates exactly one C0 HEADING-MALFORMED; the next two key lines create exactly two C0 UNATTACHED-KEY findings. There is no valid C2 block, so no C2 FIELD-MISSING. The original complete C1 remains valid: base is a strict ancestor, digests match, control ends EXIT=1, no post-freeze edits or early dispatch files. Expected exit is 1 and the sorted multiset is:

```text
C0:HEADING-MALFORMED
C0:UNATTACHED-KEY
C0:UNATTACHED-KEY
```

Definition fallback inspection confirms `parse_claims` at `:96-120` resets `cur` and accumulates every unattached line; `evaluate` at `:185-200` converts each into one finding. LSP device unavailable: reading `xd://lsp` returned `No such tool`; no semantic references/diagnostics claim is made.

## Exact bounded command and output
Invocation:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer19/probe.py
```

`probe.py` preserves frozen source copies in seat scratch, imports each copied audit, selects only the h3 tuple, asserts each fixture's `git rev-parse --show-toplevel` before add/commit, and captures the checker subprocess before the audit removes its fixture. Git init is confined to an explicitly created seat scratch child. Full argv, cwd, generated fixture revisions, stdout/stderr, exits, hashes, and versions are in `receipts.json`; generated preregistrations are retained as `*.prereg.txt`.

Real checker output (both r44 and r43 audit selections), tool exit 1 and empty stderr:

```text
FINDING C0 HEADING-MALFORMED line=12
FINDING C0 UNATTACHED-KEY line=13
FINDING C0 UNATTACHED-KEY line=14
SUMMARY claims=1 findings=3
```

Each selected audit exits 0:

```text
scenario-h3-two-unattached-keys=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

Historical contrast: r43 `c2-hidden-audit.py:113-114` has the same h3 construction, expected exit, and repeated-entry multiset. This row was already correct; it is not either repaired h4/h6 expectation. Its green result does not contradict the retained historical whole-audit red. No whole-audit run was performed.

## Single-defect mutant killed
Only change to copied checker, at its BADHEAD definition (`tools/souji-freeze-check.py:47`):

```diff
-BADHEAD = re.compile(r"^##(?!#) *[Cc] *\d")
+BADHEAD = re.compile(r"^##(?!#) +[Cc] *\d")
```

This changes zero-or-more spaces to one-or-more, failing to recognize the no-space malformed heading. The previous C1 remains current, so the two keys become duplicates. Mutant tool exit remains 1, stderr remains empty, but exact output is:

```text
FINDING C1 KEY-DUPLICATE Control
FINDING C1 KEY-DUPLICATE Population
SUMMARY claims=1 findings=2
```

The selected r44 audit exits 1:

```text
scenario-h3-two-unattached-keys=FAIL
#   got rc=1 classes=C1:KEY-DUPLICATE,C1:KEY-DUPLICATE
SUMMARY scenarios=1 pass=0 fail=1
```

Thus h3 detects a concrete grammar regression by multiset, not merely a generic findings exit. Mutation patch is retained in `mutant.patch.txt`.

## Residual risk and verification gaps
- Scope is exactly h3 on frozen sources; no full counter, other rows, unrelated tests, runtime/rerouting/resume paths, or saturation claims were exercised.
- The audit compares exit and claim/class multiset, not detail text, line numbers, or SUMMARY contents (`c2-hidden-audit.py:101-107,159-162`). Captured details are evidence, not additional asserted oracle guarantees.
- No production, sibling, index, shared bookkeeping, or installed-tool changes. Existing Python 3.14.8 and Git 2.56.0 used; no installations/upgrades.
- Seat scratch `/fast/scratch/hyaku/souji-r44/S44reviewer19` removed in driver `finally`; receipt records `scratch_removed: true`.

Self-evaluation: accuracy 4 (frozen bounded receipts; no LSP), completeness 4 (assigned row and mutant covered; no broader inference), clarity 4 (derivation separate from observations), actionability 4 (replay command and sources retained; fixture hashes are time-dependent), conciseness 4 (exact evidence adds length). Overall 4.0. Improvement priorities: preserve narrow scope when integrating; do not promote this row's success to whole-C2 admission. User agreement expected because the named acceptance evidence is present.
