# S44reviewer26 — C2 scenario 10/10

Axes: calibration / operability / coverage. Assigned axis: operability. Frozen revision: `d314fd6e85d62565344fa6c4b102f52f62297884`. Recommendation only; no admission judgment.

## Findings, by severity

### Medium — h10 accepts findings on a refusal path

`census/round-44/c2-hidden-audit.py:138-144` special-cases h10 and tests only exit 2 plus the substring `REFUSAL` anywhere in stderr. It bypasses the exact class-multiset comparison at lines 159-162. The registered row is `h10-missing-prereg-refusal\t2\tREFUSAL` (`c2-scenarios.tsv:11`), while SCENARIOS records an empty finding multiset (audit line 124).

A single added print in the tool's missing-prereg branch (before its existing raise) emits `FINDING C0 NO-CLAIMS spurious-on-refusal`. The copied h10 audit still reports PASS, despite actual finding multiset `[C0:NO-CLAIMS]` versus independently derived `[]`. This is an observed coverage gap, not a production-tool defect. The canonical tool never reaches `evaluate` or its FINDING/SUMMARY printing on this preflight failure (`tools/souji-freeze-check.py:392-405`). Recommendation: have the h10 oracle also reject any finding output; preserve the honest historical r43 instrument unchanged.

Evidence: `receipts.json`, result `round-44 / extra-finding`; `extra-finding.py` preserves the exact candidate. No mutation was applied to production or frozen counters.

## Independent expected result

The synthetic repository has valid base and freeze commits and a valid `prereg.txt`; h10 instead requests `census/absent-prereg.txt` at the valid freeze tip. The documented CLI distinguishes findings (exit 1) from inability to evaluate (exit 2 with `REFUSAL COULD-NOT-EVALUATE`, tool lines 7-9). Canonical main resolves the commit, gets no blob for the requested path, raises Refusal at lines 392-394, and the handler writes stderr and returns 2 at lines 399-401. Claim parsing, missing-field findings, freeze traversal, and all output of FINDING/SUMMARY are unreachable.

Expected: rc 2; finding multiset `[]`; stdout empty; stderr `REFUSAL COULD-NOT-EVALUATE: census/absent-prereg.txt is absent at <fixture-tip>\n`.

Observed baseline, exact:

```text
rc=2
stdout=''
stderr='REFUSAL COULD-NOT-EVALUATE: census/absent-prereg.txt is absent at 1478321c3feacd25ef8a99df6f003d2b4834d8c7\n'
classes=[]
scenario-h10-missing-prereg-refusal=PASS
SUMMARY scenarios=1 pass=1 fail=0
audit_rc=0
```

## Bounded execution and mutation sensitivity

Executed command (cwd was the explicitly created seat scratch):

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer26/probe.py
```

The preserved driver extracts sources with `git -C <lane> show <frozen-revision>:<path>`, saves exact frozen bytes and SHA256 receipts, copies each audit into scratch, replaces only SCENARIOS with its literal h10 row, and calls copied main with `--tool <scratch>/<candidate>.py --work <scratch>/<case>-work`. Each actual tool command, cwd, stdout, stderr, exit code, audit result, and fixture pre-mutation top-level assertion is in `receipts.json`. Copies of the selected audits are retained. Fixture `git add` and `git commit` are guarded by `git rev-parse --show-toplevel == fixture-directory` and containment in seat scratch; only git init precedes those assertions.

Four selected-row executions, no whole suite:

| Audit | Tool | Tool rc / classes | Audit result |
|---|---|---|---|
| r44 | frozen baseline | 2 / `[]` | PASS, exit 0 |
| r43 | frozen baseline | 2 / `[]` | PASS, exit 0 |
| r44 | missing-prereg raise replaced by `return 1` | 1 / `[]`, empty stdout/stderr | FAIL, exit 1 |
| r44 | one spurious FINDING print before existing refusal | 2 / `[C0:NO-CLAIMS]` | PASS, exit 0 |

The killed `wrong-exit.py` mutant shows this scenario detects misclassification of missing preregistration as an ordinary finding result. Exact audit output:

```text
scenario-h10-missing-prereg-refusal=FAIL
SUMMARY scenarios=1 pass=0 fail=1
```

The surviving extra-finding mutant produces exactly:

```text
stdout='FINDING C0 NO-CLAIMS spurious-on-refusal\n'
stderr='REFUSAL COULD-NOT-EVALUATE: census/absent-prereg.txt is absent at 1478321c3feacd25ef8a99df6f003d2b4834d8c7\n'
scenario-h10-missing-prereg-refusal=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

## Historical contrast and affected caller

Read-only frozen blob diff command:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff d314fd6e85d62565344fa6c4b102f52f62297884:census/round-43/c2-hidden-audit.py d314fd6e85d62565344fa6c4b102f52f62297884:census/round-44/c2-hidden-audit.py
```

The h10 row and special branch are unchanged. Observed r43 selected-row output and raw baseline output are identical to r44 above. The actual r44 audit content changes correct h4 multiplicity and h6's FROZEN-EDITED expectation, plus docstring; file mode also changes 100755 to 100644. This selected-row success does not contradict historical whole-audit red. No whole r43 audit was run.

The frozen counter calls the audit with Python explicitly (`c2-counter.py:148-149`), so the executable-mode difference does not affect that caller. Its hidden_v2 gate checks aggregate 10 passing scenarios, and therefore inherits this h10 underassertion (`:146-151`); population checks at `:137-144` do not inspect refusal output. This is source inspection, not a claimed counter execution.

## Residual risk / verification gaps

- LSP device unavailable: `read xd://lsp` returned `No such tool`; references, definitions, and diagnostics could not be obtained. Source reads and frozen diff are literal evidence, not semantic-reference proof.
- Only assigned h10 and two bounded single-defect candidates were exercised. No full counter, selftest, other scenario, lifecycle/resume path, or saturation check was run or claimed. No resume-continuity logic is in this scenario.
- Receipt preserves raw stdout/stderr. No general filesystem no-mutation oracle was run; source inspection shows the canonical requested-path failure precedes evaluate, and its Repo operations are read-only git queries.
- Scratch was removed by the driver: observed `scratch_removed=True`. Retained artifacts are solely in the seat output. No production, sibling, shared bookkeeping, index, or jj edits; no delegation or tool installation/update.

Self-evaluation (1–5): accuracy 4 (exact receipts, no LSP); completeness 4 (bounded assignment complete, no whole-counter claim); clarity 4 (raw receipts separated from inference); actionability 4 (minimal oracle recommendation, no unauthorized fix); conciseness 4 (reproduction detail retained deliberately). Average 4.0. Improvement: integration owner can tighten h10 without changing historical r43. User agreement expected because the defect has a concrete surviving candidate, not an admission assertion.
