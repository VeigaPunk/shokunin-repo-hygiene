# S44reviewer17 — C2 scenario 1/10

Axes: calibration / operability / coverage. Scoped result: **PASS; single-defect mutant killed.** No production defect established in h1. Recommendation only; no admission, integration, numerical score uplift, or whole-audit saturation claim.

## Findings by severity

No actionable defect in the assigned scenario. The h1 positive fixture rejects a real over-strict parser mutant: removing only Round's trailing horizontal-whitespace allowance changes the tool exit from 0 to 1 and produces `C0:ROUND-MALFORMED`; the selected repaired audit correctly exits 1. Candidate is seat-only `mutant.py`, exact change in `mutant.diff`.

## Independent expected multiset

Selected row: `h1-trailing-space-round`, builder `round_line="Round: 1729 "`. Expected findings multiset **[]**, exit **0**, stdout **`SUMMARY claims=1 findings=0\n`**, stderr **empty**.

Derivation from frozen `tools/souji-freeze-check.py`:
- Lines 11–27 document claim/key grammar and ASCII Round semantics; line 50 explicitly allows trailing `[ \t]*`. Lines 130–138 accept this Round and scan round-1729.
- Audit lines 65–89 construct one valid `## C1` block, all six required nonempty keys, a strict ancestral Base, matching Counter/Population SHA-256 values, two nonblank population rows, regular Control ending `EXIT=1`, and no wave file. This is not a missing-Round or malformed-Round case.
- Evaluate lines 185–239 therefore has no missing/duplicate/empty fields, bad heading, unattached keys, invalid Base, digest/control error, frozen edit, or early dispatch. Revision equals the initial preregistration freeze.
- `c2-scenarios.tsv:2` independently registers exit 0 and `-` (empty findings); audit `SCENARIOS` line 112 agrees. This expectation is derived from grammar and fixture contents, not inferred from PASS alone.

## Frozen source identity and historical contrast

All inspected/executed sources were extracted read-only using `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:<path>`. `frozen-manifest.json` records hashes and byte equality to inspected worktree sources. C2 counter and population hashes match preregistration.

Historical r43 `c2-hidden-audit.py:111` has the identical h1 expectation. Running **only h1** under both r43 and r44 produces identical clean output. The r43 full-audit historical red is intentionally not rerun or erased: the documented differences are h4's literal `FIELD-MISSING*4` and h6's omitted `FROZEN-EDITED` (r44 audit lines 4–8; historical table lines 115–118). This seat supplies no new evidence for those other scenarios or full retention.

## Exact bounded command and observed output

Scratch was explicitly created as `/fast/scratch/hyaku/souji-r44/S44reviewer17`; copies were named `audit44.py`, `audit43.py`, `tool.py`, and `mutant.py`. `probe.py` loads the copied audit and sets `SCENARIOS = (SCENARIOS[0],)` before invoking `main`. It records the exact underlying tool argv, fixture preregistration, exit, stdout, stderr, and classes in each JSON receipt. It creates minimal empty Git metadata through filesystem writes and asserts `git rev-parse --show-toplevel` equals the fixture before **every** Git init/add/commit; guard stdout is retained. Three independent h1 replays run concurrently in threads, not delegated agents.

Executed from that scratch cwd:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer17/probe.py
```

Exact process output (command exit 0):

```text
["r44-real", 0, {"exit": 0, "classes": [], "stdout": "SUMMARY claims=1 findings=0\n", "stderr": ""}, "scenario-h1-trailing-space-round=PASS\nSUMMARY scenarios=1 pass=1 fail=0\n"]
["r43-real", 0, {"exit": 0, "classes": [], "stdout": "SUMMARY claims=1 findings=0\n", "stderr": ""}, "scenario-h1-trailing-space-round=PASS\nSUMMARY scenarios=1 pass=1 fail=0\n"]
["r44-mutant", 1, {"exit": 1, "classes": ["C0:ROUND-MALFORMED"], "stdout": "FINDING C0 ROUND-MALFORMED detail=Round: 1729 \nSUMMARY claims=1 findings=1\n", "stderr": ""}, "scenario-h1-trailing-space-round=FAIL\n#   got rc=1 classes=C0:ROUND-MALFORMED\nSUMMARY scenarios=1 pass=0 fail=1\n"]
```

Replay setup: create the named scratch explicitly, copy preserved `audit44.py`, `audit43.py`, `tool.py`, `mutant.py` there, run the command above with that cwd, then remove only that seat scratch. The driver itself performs only the selected row. Its JSON receipts include the actual generated revision hashes, avoiding invented revision arguments in this report.

## Residual risk and verification gaps

- h1 covers one trailing ASCII space; it does not independently establish acceptance of a trailing tab, multiple spaces, or all Round variants. No claim that this one clean case rejects an always-clean implementation; the counter's other scenarios/controls are outside this bounded seat run.
- `xd://lsp` returned `No such tool`; no language server/status/references/definition/diagnostics device is available. Source inspection is textual fallback, not semantic caller proof. No production diff or runtime-routing/resume change was made or claimed by this seat.
- No full counter, selftest, unrelated suite, retention suite, or other hidden scenario was executed. Canonical C2 counter run logic is `census/round-44/c2-counter.py:125–151`; this focused replay is not its admission result.
- Host rules were read before tooling. No tools installed/upgraded; existing Python 3.14.8 and Git 2.56.0 used. No pacman transaction, service restart, production write, shared bookkeeping, index/jj mutation, or delegation. All Git mutations were guarded seat fixtures only.
- Frozen copies, exact receipts, probe, and mutant remain in this output directory. Seat scratch was recursively removed after preserving receipts.

Self-evaluation: accuracy 4 (textual rather than LSP semantics); completeness 4 (h1 only by assignment, no whole-audit assurance); clarity 4 (raw JSON escaped output is less readable than receipts); actionability 4 (replay needs explicit scratch restoration); conciseness 4 (source derivation plus raw receipts repeats facts). Mean 4.0. Highest-impact future improvement, outside this seat scope: independently exercise tab acceptance rather than extrapolating from a space. User should agree this is bounded evidence, not certification.
