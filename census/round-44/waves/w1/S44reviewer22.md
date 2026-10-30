# S44reviewer22 — C2 scenario 6/10

Axes: calibration / **operability** / coverage. Frozen revision: `d314fd6e85d62565344fa6c4b102f52f62297884`. Scope: only `h6-duplicate-three-occurrences`; no full counter, selftest, or unrelated scenario execution.

## Findings by severity

No actionable defect found in the repaired h6 expectation. The historical r43 oracle is demonstrably wrong for this fixture; r44 repairs precisely its missing preregistration-edit finding. This is a scoped review recommendation, not admission or non-author closure.

### Independent expected multiset

`tools/souji-freeze-check.py:11-25` documents claim syntax, first-wins keys, one `KEY-DUPLICATE` per additional occurrence, and preregistration `FROZEN-EDITED`. The fixture (`census/round-44/c2-hidden-audit.py:145-156`) first commits a valid preregistration, then inserts two copies of the existing Base line and commits again. Thus:

* One C1 block; three identical Base occurrences: first retained, two additional occurrences each produce `C1:KEY-DUPLICATE`.
* The queried revision is the second preregistration commit, not its oldest adding commit: one `C0:FROZEN-EDITED`.
* The other required fields remain valid and unchanged; the original Base remains a strict ancestor; there are no dispatch files.

Expected exit **1**, sorted multiset **`[C0:FROZEN-EDITED, C1:KEY-DUPLICATE, C1:KEY-DUPLICATE]`**. This independently agrees with audit SCENARIOS row 6 (`:120`) and TSV row h6 (`:7`). Canonical behavior is implemented by `parse_claims:114-117`, `evaluate:190-197`, and `main:402-406`; no alternative runtime was introduced.

## Bounded observed results

All tool stderr was empty. Original tool output for both repaired and historical audits, exactly:

```text
FINDING C0 FROZEN-EDITED prereg.txt differs between freeze and revision
FINDING C1 KEY-DUPLICATE Base
FINDING C1 KEY-DUPLICATE Base
SUMMARY claims=1 findings=3
```

Tool exit: **1**. Repaired selected-row audit:

```text
scenario-h6-duplicate-three-occurrences=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

Audit exit **0**. Historical r43 expectation is only `[C1:KEY-DUPLICATE, C1:KEY-DUPLICATE]`; same real tool result produces:

```text
scenario-h6-duplicate-three-occurrences=FAIL
#   got rc=1 classes=C0:FROZEN-EDITED,C1:KEY-DUPLICATE,C1:KEY-DUPLICATE
SUMMARY scenarios=1 pass=0 fail=1
```

Historical audit exit **1**. `audit-r43-to-r44.diff` retains the actual frozen audit diff; construction is unchanged and h6 only adds the missing class.

### Single-defect mutant killed

Scratch-only mutation at tool line 197: `sorted(dups)` → `sorted(set(dups))`. This incorrectly collapses repeated occurrences of the same duplicated key to one finding, without changing parsing, freeze comparison, or exit behavior. Mutant output:

```text
FINDING C0 FROZEN-EDITED prereg.txt differs between freeze and revision
FINDING C1 KEY-DUPLICATE Base
SUMMARY claims=1 findings=2
```

Mutant tool exit **1**; repaired selected-row audit exit **1**:

```text
scenario-h6-duplicate-three-occurrences=FAIL
#   got rc=1 classes=C0:FROZEN-EDITED,C1:KEY-DUPLICATE
SUMMARY scenarios=1 pass=0 fail=1
```

The scenario kills a multiset-cardinality defect even though mutant and original tool exits agree.

## Commands and retained evidence

Frozen inputs were obtained with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:<path>` for each path recorded in `commands.json`. No working-tree source was executed. Counter SHA-256 `0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252` and scenario-table SHA-256 `6a68a10161745c7974e93afe9724853f1a61fc192185c128c88840b1977a7054` match preregistration.

Executed command (cwd `/fast/scratch/hyaku/souji-r44/S44reviewer22`):

```text
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer22/probe.py
```

Driver exit **0**. `probe.py` imports scratch copies of each audit, selects only `SCENARIOS[5]` with an identity assertion, and invokes three independent selected-row exercises concurrently. It asserts each fixture's `git rev-parse --show-toplevel` equals that fixture before every add/commit; init targets an explicitly created scratch directory. Captured subprocess commands include full fixture revision IDs in `results.json` and `probe.stdout.txt`. No lane git/index changes occurred.

Retained: `frozen-audit-v2.py`, `frozen-audit-r43.py`, `frozen-tool.py`, `frozen-counter.py`, `frozen-scenarios.tsv`, `mutant.py`, `probe.py`, `commands.json`, `results.json`, `probe.stdout.txt`, `probe.stderr.txt`, and `audit-r43-to-r44.diff`. Python **3.14.8**, stdlib only; no tools installed or upgraded. Scratch removed after receipt preservation.

## Residual risk and verification gaps

* No LSP device is mounted: `read xd://lsp` returned `No such tool`. Semantic references/definition/diagnostics were unavailable. Source line citations are direct frozen-source inspection, not semantic-proof claims.
* This fixture duplicates identical Base values. It proves occurrence cardinality and detects the post-freeze edit, but does not itself distinguish first-wins versus last-wins value selection. No claim of full grammar coverage or saturation.
* Only h6 was run; no 10/10, full C2 target, retention-counter, C1, C3, resume, routing, certification, or admission verdict is inferred.
* Exact output classification checks claim/class multiplicity and exit, not finding detail strings; full raw outputs are nevertheless retained here.

Self-evaluation: accuracy 4/5 (exact receipts; no semantic service), completeness 5/5 (assigned row, independent derivation, historical contrast, killed mutant, cleanup), clarity 4/5 (commands split between report and JSON), actionability 4/5 (replay requires restoring named scratch copies from retained inputs), conciseness 4/5 (raw outputs repeated for standalone review); overall 4.2/5. Improvements: provide a single replay command if broader reproduction is assigned; add differing duplicate values only under an explicitly expanded scenario assignment. Would the user agree: the scoped observed claim is supported without inflating coverage.
