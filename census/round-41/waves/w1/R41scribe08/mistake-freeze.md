# R41scribe08 — candidate row for corpus/lessons/round-41.md `## Mistakes`

Draft for the L1. Row id to be assigned by the L1 (label used here: `R41-MF-PREDATA`). Seat draft only; not landed.

| field | content |
|---|---|
| mistake | The r40 claims named artifacts the frozen preregistration never committed as bytes: the C2 predicate verifies pairs "in the frozen list" that the file does not contain; the C1 item population has no item-table digest; the C3 base is "the r39 base fixture" with no path and no digest. The population, pair set, join grammar and base identity were therefore not frozen before seat data. |
| class | **scope** (the claim's population and boundary were undeclared at freeze). Facet: **stale premise** (the preregistration presupposes a list and a base fixture that are not in its bytes). |
| evidence pointer | `census/round-40/preregistration.txt` (sha256 `7218101a24a48ce8648e9625c992af1aa972d0e4274f17044e185ac0b3b4758c`; first added by `128e412`). Line 8 (C2): "verifies all observed class/trigger pairs in the frozen list". Line 11 (C3): "all mutants survive the r39 base fixture". The file contains no `sha256` or `digest` token (`grep -n -iE 'sha256|digest' census/round-40/preregistration.txt` → no match at `128e412`). Seat evidence: `census/round-40/waves/w1/R40sentinel23.md` F1-F4 (the L4 list "was authored after the wave had scored", per `corpus/lessons/round-40.md` M40-3), `census/round-40/waves/w1/R40sentinel11.md`, `census/round-40/waves/w1/R40executor14.md`, `census/round-40/waves/w1/R40mutationtester08.md`; C3 base identity `census/round-40/waves/w1/R40connector09.md` F1-F3, `R40connector21.md` F1-F2, `R40connector33.md` F1-F3, `R40reviewer54.md`. Lesson: `corpus/lessons/round-40.md` `### M40-3` (line 105), `### M40-4` (line 112), `### M40-5` (line 119). Non-author confirmation: `corpus/lessons/round-40-verifier-spotcheck.md` line 35 ("population, pair set, base-fixture identity are not in `preregistration.txt`"), line 44 (operability: "Frozen pair set/join grammar unfrozen (M40-3)"), line 74 (`R40-D-FREEZE`). |
| captured-by | **none** (runnable). Prose only: `corpus/QUALITY.md` Q93 (line 241), Q94 (line 242), Q95 (line 244) state the rule the r40 freeze broke. Those rows were first committed at `994de3b`, which is a strict descendant of `128e412` (the commit that first added the r40 preregistration), so they post-date the freeze and could not catch it at dispatch. No committed command reads a preregistration and fails on an unfrozen population. The sweep is in the seat report, section 2. |
| fix | C2's runnable freeze check: `tools/souji-freeze-check.py` (counter `census/round-41/c2-counter.py`, 21 cases). It reads a preregistration at a revision and reports `FIELD-MISSING`, `COUNTER-DIGEST`, `POPULATION-DIGEST`, `POPULATION-EMPTY`, `CONTROL-NOT-RED`, `FROZEN-EDITED`, `DISPATCH-BEFORE-FREEZE` and four more classes. A fix counts only once shown able to fail: the always-clean stub (`census/round-41/controls/c2-stub-clean.py`) is REJECTED because it fails 19 of 21 cases (17 finding-class cases and 2 refusal cases; it passes only the 2 clean cases); the always-findings stub is REJECTED (`control_findings=REJECTED`); at the freeze tip the tool is absent and the counter reports `pass=0`. |
| limit on the fix | C2 checks the preregistration's shape, digest equality and freeze order. It does not read the content of a Population file. Whether a pair list or a base-fixture path+digest is enumerated depends on the claim naming that artifact as its Population or Counter file. The Q94 TOTAL-ordering requirement and the Q93 probe-byte requirement stay prose until a counter enforces them. |

## Sweep (captured-by check)

Command (run at `e2a74312af4233963e44e4dbb38838ece07b8bd2`, lane `/home/vgpnk/Projects/shokunin/souji-shokunin`):

```
grep -n -iE 'freez|frozen|pre-?data|before (any|data|dispatch|scor)|population|preregist|pre-dispatch' corpus/QUALITY.md
```

Result: 27 matching lines. The three rows that name the class:

```
241:| Q93 | A documentation-map measurement freezes, BEFORE any seat scores, the complete finite class/trigger input list, the exact probe bytes and filenames, ...
242:| Q94 | A mutation battery pins the exact base fixture PATH and byte digest in its preregistration; “the prior fixture” is not a base identity. ...
244:| Q95 | A calibration claim that revisits a prior round's routed items commits the complete item population (stable ids plus item-file digest) in the preregistration before dispatch. ...
```

Adjacent rows reviewed and judged not to capture the population or pair-list freeze: Q58 (numeric target at base), Q70 and Q76-Q78 (feasibility, stability and clause-scope before a counter freezes), Q80 (one clause per code path), Q59 (axis check, `tools/souji-axis-check.py`).

Commit order (the reason captured-by is "none" at dispatch):

```
$ git log --format='%h %s' -S'| Q94 |' -- corpus/QUALITY.md
994de3b round-40: bind evidence path as well as revision; add path-substitution control
$ git log --format='%h %s' -- census/round-40/preregistration.txt
128e412 2026-10-28 round-40: instruments, sources, knowledge — C1 evidence-bound counter, C2 joined docstring classes, C3 record-branch battery
$ git merge-base --is-ancestor 128e412 994de3b && echo yes
yes
```

Runnable-check sweep: `grep -n -iE 'population|digest|sha256|pair|freez' tools/souji-axis-check.py` → no match (exit 1); `tools/souji-freeze-check.py` absent at `e2a7431` (`ls` → "No such file or directory").

## Receipts

- `.ufo/waves/round-41/w1/R41scribe08/c2-stub-clean-score.txt` — `score-candidate.sh c2` with the always-clean stub: `SUMMARY cases=21 pass=2 fail=19 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL tool_sha=5ccb4fb2705b`, exit 1.
- `.ufo/waves/round-41/w1/R41scribe08/c2-tip-tool-absent.txt` — the counter at `e2a7431` with no candidate: `SUMMARY cases=21 pass=0 fail=21 control_clean=n/a control_findings=n/a real=FAIL retro=FAIL tool_sha=absent`, exit 1.
