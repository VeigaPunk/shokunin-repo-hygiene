# S44reviewer23 — C2 scenario 7/10

Axes: calibration / operability / coverage. Assigned axis: operability.
Frozen revision: `d314fd6e85d62565344fa6c4b102f52f62297884`.
Result: h7 passes independently derived expectations; a single-defect `.ready` recognition mutant is killed. No actionable defect found in this selected scenario. Recommendation only; no admission, integration, or numerical score change.

## Derivation and source evidence

`census/round-44/c2-hidden-audit.py:121` selects `h7-dispatch-notes-ready`, builder `before=["notes.ready"]`, expected exit 1 and multiset `{C0:DISPATCH-BEFORE-FREEZE: 1}`. `c2-scenarios.tsv:8` agrees.

Independent derivation from `tools/souji-freeze-check.py:11-27`: Round 1729 is valid; `.ufo/waves/round-1729/notes.ready` matches `*.ready*`. Audit build at lines 65-89 commits base, then the early wave file, then the preregistration freeze. Thus its addition is a strict ancestor of freeze, giving exactly one prereg-wide C0 dispatch finding. The one valid C1 block supplies all six required keys, correct counter/population digests, a two-line population, red `EXIT=1` control, and a strict-ancestor Base; preregistration and frozen paths are unchanged. None generates another finding. Implementation evidence: `freeze_rev:123-127`, `dispatch_findings:130-157`, `evaluate:185-239`. Expected tool output shape is therefore one `FINDING C0 DISPATCH-BEFORE-FREEZE ...`, `SUMMARY claims=1 findings=1`, exit 1.

Relevant frozen counter: `census/round-44/c2-counter.py:13-17,132-151` describes ten-row population and hidden-v2 checks. This seat exercised only h7, not that full counter.

Frozen blobs fetched with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:<path>`; every listed worktree file equaled its frozen blob:

| Path | SHA-256 |
|---|---|
| tools/souji-freeze-check.py | f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999 |
| census/round-44/c2-hidden-audit.py | 50872b0da7a36d377ced9cf0e51579ef00f0f0ae402eebad8c579fce6e5e843e |
| census/round-44/c2-scenarios.tsv | 6a68a10161745c7974e93afe9724853f1a61fc192185c128c88840b1977a7054 |
| census/round-44/c2-counter.py | 0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252 |
| census/round-43/c2-hidden-audit.py | 4bb3fac7f3a2f8e6d59f3218a1aaccc45ee8b24717b9f4422bde31a2dabfa541 |

## Exact bounded commands and receipts

From cwd `/fast/scratch/hyaku/souji-r44/S44reviewer23`, executed these three independent commands concurrently:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer23/probe.py r44
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer23/probe.py r43
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer23/probe.py mutant
```

`probe.py` copies frozen audit/tool bytes into seat scratch, narrows the SCENARIOS assignment to its seventh row using AST source locations, and invokes that copied audit's main. Fixture-building and expected classes remain unchanged. Before every fixture add/commit it asserts `git rev-parse --show-toplevel` equals the fixture directory and lies under seat scratch (six guards per run). It captures the checker result without changing its return code or stdout. Retained `*-receipt.json` include the exact underlying checker argv, cwd, frozen source hashes, expected/actual multiset, exit, and mutation guards; `commands.json` records outer commands and outputs. `*-actual.stdout`, `*-actual.stderr`, `*-audit.stdout`, and `*-audit.stderr` preserve exact bytes/text. Selected audit copies and mutant tool are retained alongside this report.

Both r44 and historical r43 h7 audits returned exit 0, empty stderr:

```text
scenario-h7-dispatch-notes-ready=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

Both canonical checker runs returned exit 1, empty stderr, exactly:

```text
FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-1729/notes.ready first added at 8909eaddc616, not after freeze ba67f839d98c
SUMMARY claims=1 findings=1
```

The actual multiset equals independently expected `{C0:DISPATCH-BEFORE-FREEZE: 1}`.

## Single-defect kill

Only mutation in copied checker (`tools/souji-freeze-check.py:150`): replace the `".ready" in base` disjunct by `False`. This removes ready-file recognition without changing dispatch/spec/results recognition, history traversal, or ancestry logic. `mutant-tool.py` preserves the candidate. The checker returned exit 0, empty stderr:

```text
SUMMARY claims=1 findings=0
```

The same selected r44 audit rejected it with exit 1, empty stderr:

```text
scenario-h7-dispatch-notes-ready=FAIL
#   got rc=0 classes=-
SUMMARY scenarios=1 pass=0 fail=1
```

This is a behavioral kill, not a crash: a missing required finding and wrong checker exit.

## Historical contrast, residual risk, verification gaps

The frozen r43 and r44 seventh SCENARIOS rows are identical, independently parsed and compared. Both produce the same h7 result. The r44 audit docstring describes repairs to h4 repetition and h6 post-freeze expectations; h7 is not a repaired historical oracle. This seat does not claim the full historical r43 audit passed or that its retained red is resolved.

Only scenario 7 and the one mutant were run; no whole counter, selftest, other scenarios, full-suite validation, runtime rerouting, resume path, or saturation claim was evaluated. h7 alone does not establish alternate `.ready` placements/suffixes, other artifact names, or post-freeze non-findings. LSP semantic queries were unavailable: `read xd://lsp` returned `No such tool`; source inspection and executed probes are the evidence, not a semantic-reference claim.

No production/counter edits, shared bookkeeping, commits/index mutations in the lane, delegation, or other runtime invocation. No tools installed or upgraded. Existing tools: Python 3.14.8 and git 2.56.0. Scratch is removed before handoff; all receipts remain in this output directory.

Self-evaluation (1–5): accuracy 4 (bounded execution, not full semantic caller proof); completeness 5 (selected scenario, independent derivation, historical contrast, mutant, exact receipts); clarity 4 (long absolute commands retained for reproducibility); actionability 5 (reproducer and mutant preserved); conciseness 4 (receipt inventory repeats some command context). Average 4.4. Most useful expansion would be a separately assigned boundary scenario, not a larger claim from h7. User agreement expected because scope and gaps are explicit.
