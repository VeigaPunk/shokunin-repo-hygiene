# S44reviewer25 — C2 scenario 9 of 10

Axes: calibration / operability / coverage. Assigned axis: operability.
Frozen source: `d314fd6e85d62565344fa6c4b102f52f62297884`.
Result: h9 passes against the frozen tool; one isolated depth-truncation defect is killed. No actionable defect found in this selected scenario's oracle. This is a review recommendation, not admission or a fleet score change.

## Independent expected multiset

Selected `h9-dispatch-depth-three`, not h10. The audit's SCENARIOS row (`census/round-44/c2-hidden-audit.py:123`) supplies `before=["w9/w8/deep-spec.json"]`. The TSV row 10 independently states exit 1 and `C0:DISPATCH-BEFORE-FREEZE`.

Derivation from `tools/souji-freeze-check.py:7-27`, not from the table's answer: Round is valid ASCII 1729; the single complete C1 claim has an ancestral Base, matching counter/population digests, and a red Control. The preregistration and claim files are unchanged after freeze. The fixture adds `.ufo/waves/round-1729/w9/w8/deep-spec.json` in an earlier commit than the commit first adding prereg.txt (`build`, audit lines 65-88). The documented dispatch rule covers **any file under** the round tree with basename `*-spec.json`; it imposes no depth limit. Exactly one matching file exists. Therefore expected multiset is exactly `["C0:DISPATCH-BEFORE-FREEZE"]`, multiplicity one, exit 1; there should be no C1 or other C0 findings.

Canonical implementation corroborates this: `dispatch_findings` lines 138-156 scans the round subtree, matches basenames, and reports each path whose oldest addition is at/before freeze. `evaluate` line 238 adds those findings; `main` lines 402-406 sorts, prints, and returns 1 for nonempty findings.

## Exact bounded execution and observations

All source bytes were extracted read-only using this command shape for each path in `frozen-sha256.json`:

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:<path>
```

The preregistered C2 counter SHA256 and scenario TSV SHA256 match the extracted blobs (see manifest). No counter was run or changed. Copied audit modules retain their original source bytes; `probe.py` selects only h9 by replacing the in-memory SCENARIOS tuple. Its git wrapper guards fixture identity before add/commit. For bootstrap init, it asserts no enclosing repository first, then asserts the new fixture root before any further git mutation. Its run wrapper retains exact tool commands, return codes, stdout/stderr and classes. No other scenario or selftest was executed.

Exact probe command, cwd `/fast/scratch/hyaku/souji-r44/S44reviewer25`:

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer25/probe.py
```

Probe exit: 0. Full exact structured output is retained in `receipts.json`, including all tool arguments and fixture guard results. Frozen tool stdout (both r44 and r43 selected-row probes), tool exit 1, stderr empty:

```
FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-1729/w9/w8/deep-spec.json first added at 752b2d08c4ec, not after freeze 0b3ef20e8c9c
SUMMARY claims=1 findings=1
```

Both audit outputs, audit exit 0:

```
scenario-h9-dispatch-depth-three=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

### Single-defect mutant killed

Only change to the isolated frozen tool copy, line 151:

```diff
-                first[line] = commit
+                if line[len(tree):].count("/") < 2: first[line] = commit
```

This incorrectly drops dispatch files two or more subdirectories below the round tree; it does not manufacture a crash or change the oracle. `mutant.py` is preserved beside the original `tool.py`. Actual mutant classes `[]`, exit 0, stderr empty, stdout:

```
SUMMARY claims=1 findings=0
```

Selected r44 audit exit 1:

```
scenario-h9-dispatch-depth-three=FAIL
#   got rc=0 classes=-
SUMMARY scenarios=1 pass=0 fail=1
```

Thus h9 concretely detects a shallow-recursion regression.

## Historical r43 contrast

The r43 h9 row (`census/round-43/c2-hidden-audit.py:121`) has the same fixture kwargs, expected exit, and expected multiset. Its selected-row probe also passes, so h9 is retained coverage, not a newly repaired oracle. The r44 audit docstring identifies repairs to h4's literal repetition notation and h6's missing FROZEN-EDITED expectation; those rows were inspected but not exercised. This report does not claim the historical full r43 audit passes or erase its registered red (`c2-counter.py:8-12,48-51`).

## Residual risk / verification gaps

- Only h9 was run. No claim of 10/10, full counter success, saturation, runtime rerouting, resume continuity, admission, or numerical improvement is made.
- The audit compares exit and sorted claim/class multiset, not detail text or SUMMARY counts (`classes` lines 101-107; comparison lines 159-162). A wrong detail path/hash can escape this scenario even when class counts match. Exact raw output is retained for manual review; no broader mutation battery was assigned.
- LSP is unavailable: reading `xd://lsp` returned `No such tool`. No server/status/references/definition/diagnostics interface was mounted. Definition/caller observations here are source-text inspection and bounded execution, not semantic LSP proof.
- The supplied trailer names a sibling-level `S44reviewer25.md`, conflicting with the explicit output-only directory restriction. This report stays within the named owned directory at `S44reviewer25/report.md`; no sibling-level file was written.
- Production/domain trees, shared bookkeeping and lane git state were not written. Synthetic repository mutations occurred only under the explicitly owned scratch directory, which was removed after preserving evidence.
- No installation/update, pacman transaction, PATH write, or service restart. Runtime versions: Python 3.14.8, git 2.56.0.

## Reproduction artifacts

`probe.py`, `receipts.json`, `frozen-sha256.json`, `versions.json`, frozen `tool.py`, `audit44.py`, `audit43.py`, `c2-scenarios.tsv`, and isolated `mutant.py` are durable evidence, not production candidates. To reproduce after cleanup, explicitly recreate the named scratch directory and copy the four Python source inputs there before running the command above. Exact original run commands remain in receipts; commit identities can differ on a later run because fixture commit timestamps are not pinned.

Self-evaluation (1–5): accuracy 4 (single-row empirical evidence, no whole-suite claim); completeness 4 (assigned h9 and mutant covered; output-path conflict documented); clarity 4 (exact results separated from inference); actionability 4 (sources/driver/receipts retained, scratch must be recreated); conciseness 4 (detailed evidence retained for audit). Overall 4.0. Highest-impact residual improvement would be explicit detail-text oracle assertions, outside this bounded assignment. The user can independently compare every quoted outcome to the preserved receipts.
