# S44reviewer20 — C2 scenario 4/10

## Result and axes

Axes: calibration / operability / coverage. Assigned axis: **operability**. Frozen source: `d314fd6e85d62565344fa6c4b102f52f62297884`.

**Scenario h4 passes with the repaired r44 oracle; the same checker fails the historical r43 oracle; r44 kills a single-defect missing-Control mutant.** This is a scoped recommendation/evidence receipt, not admission, certification, whole-population success, or saturation. No actionable defect found in h4's repaired expected multiset.

## Findings, by severity

- Historical oracle defect, reproduced: `census/round-43/c2-hidden-audit.py:115-116` expects the literal class `C2:FIELD-MISSING*4`. `classes()` at lines 100-106 extracts individual claim/class pairs and never expands repetition. Therefore the correct six findings cannot equal that three-element expectation. The historical selected audit remains red; no historical or frozen file was changed.
- Repaired behavior is correct for h4: `census/round-44/c2-hidden-audit.py:116-118` explicitly repeats the missing-field class four times; `census/round-44/c2-scenarios.tsv:5` agrees. The selected run passes, including exact multiplicity and exit status.

## Independent derivation from the checker grammar

`tools/souji-freeze-check.py:11-25` defines six required keys and makes malformed headings close a block, subsequent keys unattached, until the next valid claim heading. Its canonical implementation is `parse_claims()` lines 96-120 and `evaluate()` lines 185-238; main lines 398-406 sorts findings and exits 1 when findings exist.

The complete initial C1 contributes no finding. The tail is:

```text
##C2 bad
Target: t
## C2 — second
Target: t2
Kill: k2
```

`##C2 bad` (fixture line 12) is malformed, not a valid C2 header: one `C0:HEADING-MALFORMED`. `Target: t` (line 13) is unattached: one `C0:UNATTACHED-KEY`. The valid C2 block has Target and Kill but lacks Base, Counter, Population, Control: four separate `C2:FIELD-MISSING` findings. No post-freeze edit occurs in h4; the initial C1 paths, digests, ancestry, control and Round are valid.

Independently derived sorted multiset:

```text
C0:HEADING-MALFORMED
C0:UNATTACHED-KEY
C2:FIELD-MISSING
C2:FIELD-MISSING
C2:FIELD-MISSING
C2:FIELD-MISSING
```

Checker exit 1; `SUMMARY claims=2 findings=6`.

## Exact bounded execution and receipts

Executed:

```sh
mkdir -p /fast/scratch/hyaku/souji-r44/S44reviewer20 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer20
# cwd: /fast/scratch/hyaku/souji-r44/S44reviewer20
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer20/probe.py
# cwd: /home/vgpnk/Projects/shokunin
rm -rf /fast/scratch/hyaku/souji-r44/S44reviewer20
```

`probe.py` preserves its full reproducible source here. It obtains inputs with `git -C LANE show REV:PATH`; exact input bytes and hashes are retained as `frozen-*` files and `frozen-sha256.json`. It copies each audit and AST-selects only tuple index 3, retaining that tuple literally. It adds a fixture-root assertion before every git operation except initialization and logs raw checker output. No fixture construction or oracle comparison logic is otherwise changed. `r44-canonical-audit.py`, `r43-canonical-audit.py`, and `r44-mutant-audit.py` preserve these copies. The audit removes its fixture work directories after each selected run.

`results.json` contains every exact subprocess command, cwd, exit code, stdout and stderr, including the fixture revision and raw expected/actual multisets. The canonical checker command was:

```sh
python3 -B /fast/scratch/hyaku/souji-r44/S44reviewer20/tool.py --root /fast/scratch/hyaku/souji-r44/S44reviewer20/r44-canonical-work/h4-unattached-before-valid-claim --prereg prereg.txt --rev 8cc403ffe266232cd188ba0909f2d5825e223fe7
```

Observed canonical checker stdout, exit 1, stderr empty:

```text
FINDING C0 HEADING-MALFORMED line=12
FINDING C0 UNATTACHED-KEY line=13
FINDING C2 FIELD-MISSING Base
FINDING C2 FIELD-MISSING Control
FINDING C2 FIELD-MISSING Counter
FINDING C2 FIELD-MISSING Population
SUMMARY claims=2 findings=6
```

Selected r44 audit exit 0:

```text
scenario-h4-unattached-before-valid-claim=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

Selected r43 audit, with identical raw checker output and exit 1, audit exit 1:

```text
scenario-h4-unattached-before-valid-claim=FAIL
#   got rc=1 classes=C0:HEADING-MALFORMED,C0:UNATTACHED-KEY,C2:FIELD-MISSING,C2:FIELD-MISSING,C2:FIELD-MISSING,C2:FIELD-MISSING
SUMMARY scenarios=1 pass=0 fail=1
```

## Single-defect mutant killed

The retained `mutant-omit-control-required.py` changes exactly one checker predicate at `tools/souji-freeze-check.py:199`:

```diff
-            if key not in f:
+            if key not in f and key != "Control":
```

This wrongly exempts Control from missing-field reporting; it does not hardcode scenario output or alter any audit. Observed checker exit remains 1, so the kill specifically depends on the findings multiset, not exit mismatch. Mutant checker stdout, stderr empty:

```text
FINDING C0 HEADING-MALFORMED line=12
FINDING C0 UNATTACHED-KEY line=13
FINDING C2 FIELD-MISSING Base
FINDING C2 FIELD-MISSING Counter
FINDING C2 FIELD-MISSING Population
SUMMARY claims=2 findings=5
```

Actual mutant multiset has only three `C2:FIELD-MISSING` entries. Selected r44 audit exit 1:

```text
scenario-h4-unattached-before-valid-claim=FAIL
#   got rc=1 classes=C0:HEADING-MALFORMED,C0:UNATTACHED-KEY,C2:FIELD-MISSING,C2:FIELD-MISSING,C2:FIELD-MISSING
SUMMARY scenarios=1 pass=0 fail=1
```

## Residual risk and verification gaps

Only h4 was exercised, three bounded runs; no counter-wide selftest, stubs, other nine scenarios, or whole-suite validation was run. The audit compares only claim/class pairs, not missing-field detail names: four incorrect same-class detail strings could escape h4's assertion. This is a source-observed limitation (`classes()` lines 101-107), not an exercised second mutation. Frozen counter inspection confirms its broader target, but this report does not assert that target passes.

The `xd://lsp` device is unavailable (returned “No such tool”); semantic references/definition/diagnostics could not be requested. Source inspection and executable receipts are the evidence, not semantic-search proof. No runtime/rerouting/resume code is in this assigned scenario. Domain files and frozen counters were read-only; only this seat's artifacts and scratch were written. Scratch removal completed successfully. No installs, upgrades, pacman transactions, service restarts, production edits, shared bookkeeping edits, index changes, or delegation occurred. Tools: Python 3.14.8 and git 2.56.0 (existing host tools; `versions.json`).

## Self-evaluation

Accuracy 4/5: exact receipts and frozen input hashes; no LSP available. Completeness 5/5: selected scenario, grammar derivation, historical contrast, killed mutant, commands and cleanup retained. Clarity 4/5: exact receipt detail makes the report longer. Actionability 5/5: preserved driver, input bytes and mutant permit reproduction. Conciseness 4/5: raw excerpts intentionally overlap machine receipts. Overall 4.4/5. Highest-value improvements would be detail-sensitive assertions and semantic diagnostics when an LSP is available; neither is claimed implemented. Self-check: the scope and limitations should match the user's requested bounded evidence.
