# S44reviewer24 — C2 scenario 8/10

Axes: calibration / operability / coverage. Assigned axis: operability.
Frozen revision: `d314fd6e85d62565344fa6c4b102f52f62297884`.
Result: h8 passes; its CRLF regression mutant is killed. No actionable defect found in the selected scenario's oracle. This is a recommendation/evidence report, not admission or integration.

## Independent expected multiset

Selected row is `h8-crlf-prereg`, not TSV line 8: `census/round-44/c2-scenarios.tsv:9` and `c2-hidden-audit.py:122` both specify exit 0, empty finding multiset.

The expectation follows the checker grammar (`tools/souji-freeze-check.py:11-27`), rather than assuming the table is correct:
- CRLF must parse through `splitlines()` (`parse_claims:96-120`, dispatch parsing `130-137`). One valid C1 heading and all six nonempty unique required keys remain.
- Builder `c2-hidden-audit.py:48-89` creates a strict base ancestor, matching counter/population digests, a two-line population and a red control (`EXIT=1`). No dispatch artifact is added and preregistration is not edited after freeze.
- Thus no malformed/unattached/missing/duplicate/digest/control/freeze/dispatch findings arise. Expected multiset is exactly `[]`, exit exactly `0`, stdout exactly `SUMMARY claims=1 findings=0\n`, stderr empty. Canonical main `tools/souji-freeze-check.py:388-406` resolves the commit/blob/freeze, calls evaluate, prints sorted findings and summary, and returns 0 iff no finding lines exist.

## Exact bounded command and evidence

Executed from owned scratch:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer24/probe.py
```

`probe.py` is retained verbatim. It fetches each source with the exact `git -C <lane> show <frozen-rev>:<path>` commands recorded in `receipts.json`, copies audit/checker into scratch, imports each copied audit and selects only its h8 row. Instrumentation records the subprocess command, stdout, stderr, exit and classes without changing the oracle. Fixture `add`/`commit` calls assert `git rev-parse --show-toplevel` equals the fixture; initialization creates a new empty fixture first. All fixture roots are under the seat scratch. No lane git mutation occurs.

Actual v2 checker output, exit 0, stderr empty, classes `[]`:

```text
SUMMARY claims=1 findings=0
```

Actual v2 selected audit output, exit 0:

```text
scenario-h8-crlf-prereg=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

Receipt confirms 11 CRLF sequences and zero bare LF in the input. Exact preregistration bytes are retained as `v2-real.prereg.bin`; source bytes, SHA-256s, complete expected/actual text (including CR escapes), runtime versions and all commands are in `receipts.json` and the `tools__*`/`census__*` snapshots. Counter and population snapshot hashes match preregistration.

## Historical r43 contrast

Frozen `census/round-43/c2-hidden-audit.py:120` has the identical h8 row `(crlf=True, 0, [])`. Its isolated h8 run also returned:

```text
scenario-h8-crlf-prereg=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

Checker stdout was the same clean summary. There is no h8 oracle correction between r43 and r44. The r44 docstring identifies corrections to h4 repetition notation and h6 post-freeze editing; those rows were not run, and this report does not turn historical r43 aggregate RED into green.

## Single-defect mutant killed

A scratch-only AST transformation changes only the call in `parse_claims` from `text.splitlines()` to `text.split('\n')`, a CRLF handling regression. The surrounding checker AST is unchanged; `ast.unparse` reformats the candidate. No production candidate or frozen counter was edited. The retained probe regenerates the exact candidate.

Expected remains exit 0, multiset `[]`. Actual candidate exit is 1; actual multiset is:

```text
C1:BASE-UNRESOLVED
C1:CONTROL-MISSING
C1:COUNTER-DIGEST
C1:POPULATION-DIGEST
```

The carriage return contaminates Base, Control and digest values. Complete exact finding details are retained in `receipts.json`. Actual selected audit output, exit 1:

```text
scenario-h8-crlf-prereg=FAIL
#   got rc=1 classes=C1:BASE-UNRESOLVED,C1:CONTROL-MISSING,C1:COUNTER-DIGEST,C1:POPULATION-DIGEST
SUMMARY scenarios=1 pass=0 fail=1
```

This demonstrates real CRLF sensitivity, not rejection of a crashing or always-findings stub.

## Residual risk / verification gaps

- Selected scenario only: no full counter, selftest, unrelated scenarios, resume preflight or runtime rerouting was exercised. No saturation, fleet-wide coverage, numerical axis uplift or admission claim follows.
- Audit `classes()` and main (`c2-hidden-audit.py:101-107,159-162`) compare exit and finding multiset, not the checker summary or stderr. The real run's summary/stderr were independently retained; h8 alone is not a summary-format verifier.
- LSP was unavailable: reading `xd://lsp` returned `No such tool`; therefore no semantic references/definition/diagnostics claim is made. Source/AST review and bounded execution are the evidence.
- Python 3.14.8 and Git 2.56.0 were existing tools. No installs/upgrades, package transactions, service restarts or provider bypasses occurred.
- The probe's finally block removed the complete owned scratch after preserving receipts. Output files are confined to the assigned seat directory, plus the explicitly requested sibling report trailer path.

## Self-evaluation

Accuracy 4/5: exact frozen receipts support results; LSP semantic proof unavailable. Completeness 4/5: all assigned h8 checks performed, intentionally no aggregate validation. Clarity 4/5: short result plus exact evidence; long raw output resides in JSON. Actionability 5/5: retained probe reproduces bounded evidence. Conciseness 4/5: source snapshots add evidence volume. Overall 4.2/5; appropriate next use is L1's scoped integration review, not additional unassigned verification. User should agree given the explicit one-scenario scope.
