# R41w2mutationtester02 — mutation probe of tools/souji-freeze-check.py (parsing, ordering, exit codes, refusal text)

Seat: R41w2mutationtester02 (role mutation-tester, leaf, no subagents). Judged on: operability. Milestone: r41 falsify landed claims.
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin, tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f (read only; no lane file touched, no git mutation).
Tool under test: tools/souji-freeze-check.py, blob sha256 3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b (matches census/round-41/records/c2-after.txt `tool_sha=3c3e80baedd8`).
Frozen instrument: census/round-41/c2-counter.py (run via score-candidate.sh, which clones the tip and commits candidate bytes in the clone only).
Scope: the parsing/ordering/exit-code space. Per-finding-class check deletions belong to R41w2mutationtester01 and were not run.

## Commands run (exact)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && bash census/round-41/score-candidate.sh c2 /fast/scratch/hyaku/souji-r41/R41w2mutationtester02 tools/souji-freeze-check.py=tools/souji-freeze-check.py   # baseline -> baseline-score.txt
cp tools/souji-freeze-check.py .ufo/waves/round-41/w2/R41w2mutationtester02/mut/<ID>.py   # 31 copies, then `edit` applied the line changes listed below
python3 -c "import ast,...; ast.parse(...)"  # parse check of each mutant -> mutant-manifest.txt (all 31 parse; diff line counts recorded)
ls mut | xargs -P 4 ... bash census/round-41/score-candidate.sh c2 /fast/scratch/hyaku/souji-r41/R41w2mutationtester02 tools/souji-freeze-check.py=<seat>/mut/<ID>.py > scores/<ID>.txt   # 32 runs (31 mutants + identity)
python3 -B .ufo/waves/round-41/w2/R41w2mutationtester02/probes.py > .../probes-output.txt   # 21 probe blocks, baseline vs named mutant(s)
python3 -B .ufo/waves/round-41/w2/R41w2mutationtester02/probe_b1.py > .../probe-b1-output.txt
manual checks: X6 stdout placement; X7 short --rev; K3 equivalence (key-lowercase fixture)
```

Scoring rule: score-candidate exit 0 = the counter met its target (21/21, both stubs REJECTED, real ok, retro red) = mutant SURVIVED. Exit 1 = a case or leg failed = mutant KILLED.

## Results

Baseline (`baseline-score.txt`): `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8`, EXIT=0.
Identity control (`scores/m00-identity.txt`): same line, EXIT=0. The harness does not alter a byte-identical tool.

Line numbers refer to the tip tool. Each mutant is one edit (X3 three lines, W4 four lines); `mut/<ID>.py` is the mutant. Score file: `scores/<ID>.txt`.

| ID | Tip line | Mutation | Counter result (scores/<ID>.txt) | Verdict | Behavioural evidence (probes-output.txt) |
|---|---|---|---|---|---|
| K1 | 27 | KEYLINE drops `[ \t]*` before `$` (no trailing-blank strip) | survived, 21/21 | survived, output-divergent | base-trailing-ws: baseline rc=0; K1 rc=1 BASE-UNRESOLVED |
| K2 | 27 | KEYLINE accepts indented keys `^[ \t]*` | survived, 21/21 | survived, output-divergent | key-indented: baseline rc=1 FIELD-MISSING Kill; K2 rc=0 |
| K3 | 27 | KEYLINE `(?i)` case-insensitive | survived, 21/21 | survived, EQUIVALENT | key-lowercase: identical output (`FIELD-MISSING Base`) in both; keys are stored as written and looked up case-sensitively (probe reasoning, not a proof of all inputs) |
| K4 | 76 | duplicate key: last occurrence wins (`if m:`) | survived, 21/21 | survived, output-divergent | key-duplicate-counter: baseline rc=1 COUNTER-DIGEST; K4 rc=0 |
| K5 | 26 | HEADER drops `(?![0-9A-Za-z_])` | survived, 21/21 | survived, output-divergent | header-lookahead: baseline rc=0 claims=1; K5 rc=1 claims=2, six FIELD-MISSING under C2 |
| K6 | 26 | HEADER `C(\d)` single digit | survived, 21/21 | survived, output-divergent | header-two-digit: baseline rc=1 `C10 FIELD-MISSING Kill`; K6 rc=0 claims=1 |
| K7 | 26 | HEADER `[CR](\d+)` (accepts `## R1`) | real FAIL, EXIT=1 | killed (real leg) | scores/K7.txt `real FAIL` |
| P1 | 28 | PATH_SHA drops `$` | survived, 21/21 | survived, output-divergent | sha-trailing-junk: baseline rc=1 COUNTER-DIGEST; P1 rc=0 |
| P2 | 125 | no finding when Counter/Population carries no `sha256=` (`pass`) | survived, 21/21 | survived, output-divergent | sha-missing: baseline rc=1 COUNTER-DIGEST; P2 rc=0 |
| P3 | 28 | PATH_SHA `[0-9a-fA-F]` (uppercase) | survived, 21/21 | survived, detail-only | sha-uppercase-correct: both rc=1 COUNTER-DIGEST on a CORRECT uppercase digest (shared false positive); only the detail text differs |
| P4 | 28 | PATH_SHA `{1,64}` (short digest) | survived, 21/21 | survived, detail-only | sha-short: both rc=1 COUNTER-DIGEST; detail text differs |
| P5 | 28 | PATH_SHA path `(.+?)` (path may contain spaces) | survived, 21/21 | survived, output-divergent | path-with-space: baseline rc=1 COUNTER-MISSING `census/my`; P5 rc=0 |
| R1 | 29 | ROUND without `re.M` | dispatch-before-freeze FAIL, EXIT=1 | killed | scores/R1.txt |
| R2 | 29 | ROUND `(\d)` | dispatch-before-freeze FAIL, EXIT=1 | killed | scores/R2.txt |
| EL1 | 30 | EXIT_LINE `(-?\d+)` | survived, 21/21 | survived, output-divergent | control-exit-negative: baseline rc=1 CONTROL-NOT-RED on `EXIT=-1`; EL1 rc=0 |
| F1 | 82 | freeze_rev drops `--reverse` (newest add, not oldest) | survived, 21/21 | survived, output-divergent | reverse-removed: baseline rc=1 COUNTER-DIGEST + FROZEN-EDITED; F1 rc=0 |
| D1 | 105 | first-add: `setdefault` (newest add, not oldest) | survived, 21/21 | survived, output-divergent | dispatch-first-add: baseline rc=1 DISPATCH-BEFORE-FREEZE; D1 rc=0 |
| D2 | 108 | dispatch in the freeze commit itself exempted (`c != freeze and`) | survived, 21/21 | survived, output-divergent | dispatch-freeze-commit: baseline rc=1 C0 DISPATCH-BEFORE-FREEZE; D2 rc=0 |
| D3 | 108 | dispatch check `if True` | clean-dispatch-after FAIL, EXIT=1 | killed | scores/D3.txt |
| B1 | 153 | Base == FREEZE-REV accepted (`elif not is_ancestor`) | survived, 21/21 | survived, output-divergent | probe-b1-output.txt: baseline rc=1 BASE-NOT-ANCESTOR; B1 rc=0 |
| W1 | 129 | at_rev blob read from the work tree | survived, 21/21 | survived, output-divergent | worktree-rev-blob (--rev = freeze, HEAD edits counter): baseline rc=0; W1 rc=1 FROZEN-EDITED |
| W2 | 197 | prereg read from the work tree | survived, 21/21 | survived, output-divergent | worktree-prereg (uncommitted Kill removed): baseline rc=0; W2 rc=1 FIELD-MISSING Kill |
| W3 | 169 | Control blob read from the work tree | survived, 21/21 | survived, output-divergent | worktree-control (uncommitted EXIT=0): baseline rc=0; W3 rc=1 CONTROL-NOT-RED |
| W4 | 56-58 | Repo.blob reads the work tree for every rev | frozen-edited-counter, frozen-edited-population FAIL, EXIT=1 | killed | scores/W4.txt |
| X1 | 211 | findings exit 2 (`return 2 if lines`) | 17 cases FAIL, EXIT=1 | killed | scores/X1.txt |
| X2 | 206 | refusal exit 1 | unresolved-rev, absent-prereg FAIL, EXIT=1 | killed | scores/X2.txt |
| X3 | 190 | `--root` not a directory: refusal text, exit 1 | survived, 21/21 | survived, output-divergent | root-missing: baseline rc=2; X3 rc=1 (same stderr) |
| X4 | 205 | refusal text loses `: <detail>` | survived, 21/21 | survived, detail-only | refusal-text: baseline stderr `REFUSAL COULD-NOT-EVALUATE: --rev ffff... does not resolve...`; X4 `REFUSAL COULD-NOT-EVALUATE`; rc=2 both |
| X5 | 205 | refusal word `REFUSED` instead of `REFUSAL` | survived, 21/21 | survived, detail-only | refusal-text: X5 stderr `REFUSED COULD-NOT-EVALUATE: ...`; rc=2 both. The counter asserts only the substring `COULD-NOT-EVALUATE` |
| X6 | 205 | refusal written to stdout | unresolved-rev, absent-prereg FAIL, EXIT=1 | killed | scores/X6.txt; manual: `X6 ... 2>/dev/null` prints the REFUSAL line on stdout, rc=2 |
| X7 | 191 | `--rev` full-40 gate removed | survived, 21/21 | survived, output-divergent | rev-short (12-char HEAD): baseline rc=2 `--rev must be a full 40-hex commit id`; X7 rc=0 SUMMARY claims=1 findings=0 |

Tally (31 mutants, all parse, `mutant-manifest.txt`): killed 8 (K7, R1, R2, D3, W4, X1, X2, X6); survived 23 = output-divergent 18 (K1, K2, K4, K5, K6, P1, P2, P5, EL1, F1, D1, D2, B1, W1, W2, W3, X3, X7) + detail-only 4 (P3, P4, X4, X5) + equivalent 1 (K3). Identity control passes as expected.

Not run (named): dropping `--diff-filter=A` in F1's line is argued equivalent (under `--reverse` the oldest commit touching PATH is always its first add), not probed. Dispatch tree prefix, the `Round:`-absent path and the `*.ready` glob are out of this seat's list.

## What the survivors mean

1. The frozen counter scores 21/21 on 18 tool variants whose output differs from the tool at tip. Its 21 cases all run with a clean work tree, rev = HEAD, a single prereg add, no duplicate keys, no `## ` header beyond `C<digits>`, no indentation, no spaces in paths, and no refusal on stdout or on `--root`. Every survivor above sits in one of those untested inputs.
2. Survivors that touch the tip's own grammar text: W1-W3 (grammar line 12-13: "read from the blob at --rev", which reviewer R41reviewer05 F2 also reported), B1 (grammar says "strict ancestor"), D2 (the grammar contradicts itself: "FREEZE-REV or an ancestor" vs "strict-ancestor"; R41reviewer05 U3), and X3 (the grammar's exit 2 for could-not-evaluate).
3. Survivors that are only text: P3, P4, X4, X5. Under the preregistered Kill rule these do not fire.
4. Tool defects surfaced while probing (not counter gaps only):
   - EXIT=-1 is rejected: the tool prints CONTROL-NOT-RED for `EXIT=-1`. The counter's own grammar (census/round-41/c2-counter.py line 36) says `EXIT=<n>` with n "a nonzero integer", and -1 is one. A signal-killed control is recorded as a negative returncode, so the tool would reject it. Severity: low (narrow input), but it contradicts the grammar the tool claims to implement. Not fixed here (read-only seat).
   - A correct uppercase `sha256=` digest is reported as COUNTER-DIGEST with the message "has no sha256=<64 hex>" (probe sha-uppercase-correct, baseline rc=1). That message misleads an operator who has a correct digest. Severity: low.
   - Key-case mistakes (`base:`) report `FIELD-MISSING Base` with no hint of the case mismatch. Cosmetic.
5. The work-tree leak (W1-W3) is not a risk on the committed lane today: the tip tool reads blobs (`git cat-file`), and the probes confirm it. The gap is that the counter cannot detect a regression to work-tree reads.

## Verdict

- Mutation coverage of the C2 instrument over this seat's space: 8/31 killed; 23/31 survived (18 output-divergent). The counter does not pin the parsing/ordering/exit-code behaviour the tool's own grammar text describes.
- C2 as preregistered (Target: `SUMMARY cases=21 pass=21 ... real=ok retro=red`; Kill: tool absent, any case fail, either stub accepted, real not ok, retro not red): no survivor here changes those conditions, so the preregistered measurement is not falsified. The claim's stronger reading ("the counter verifies the tool against its grammar") is falsified for 18 grammar-visible behaviours. Recommended admission wording: C2 holds as measured; name the 18 survivors as counter limits in the r41 lesson; do not describe the counter as grammar-complete.
- One landed-tool defect (EXIT=-1 rejected against the counter's own grammar) is open. Operability axis: harmed narrowly (low). Not an admission blocker by the preregistered rule, but it should be named.

## Receipts (seat-relative paths)

- baseline-score.txt; scores/<ID>.txt (32 files incl. m00-identity); mutant-manifest.txt (parse, sha256, diff line count per mutant)
- mut/<ID>.py (31 mutants, read-only evidence; not tracked files)
- probes.py, probes-output.txt (21 probes), probe_b1.py, probe-b1-output.txt, x6-stderr.txt
- Tools installed: none. Scratch: /fast/scratch/hyaku/souji-r41/R41w2mutationtester02 (deleted after receipts were written into this seat).
